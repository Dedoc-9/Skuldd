# R4 (b) and (a): the minimal harness (2026-11-16, scratch; written by the assistant, the author of the proofs it
# judges, and graded so). It executes nothing from the judged tree but coqc and coqchk: it reads the freeze list and
# the .v files as data, compiles them in a fresh root of its own, writes its own check file, and reads Coq's output
# with its own strict reader. Python standard library only; meant for the build image's python3.
#   python3 -B harness.py --src DIR --list FOLDER/FROZEN4.txt --anchor SHA256 --statement MOD.NAME --theorem MOD.NAME
#                         --axioms gate/expected-pa-flocq4.txt [--build DIR]
# MOD is a module path under MKF (for example sincos32z.SINCOS32_IEEE_Zero_Statement); --anchor is the owner's own
# sha256 of the freeze list. Rows (each prints ok or FAIL):
#   1 the freeze list's sha256 is the given anchor                (refinement T1)
#   2 every line of the list is readable and no path is listed twice
#   3 every listed file is present with its listed sha256          (refinement T1)
#   4 the list covers the closure: every MKF module that a listed source imports is listed, and the statement, the
#     theorem's module, the folder's Identity.v and Closed.v and the expected-axioms file are listed (refinement T1)
#   5 the fresh root holds exactly the listed sources (plant files excluded), byte for byte
#   6 every source compiles, in an order computed from the imports
#   7 the harness's own check file: the theorem has the statement as its type, and Print Assumptions lists exactly
#     the expected axioms (name and type)
#   8 one recursive coqchk of the check module: its whole summary read strictly (two theory lines, exactly the four
#     axioms by their full names, <none> under each unsafe section)                                   (R4 a)
# It also prints the sha256 of every compiled .vo, of coqc and coqchk, and a digest of the outside libraries loaded.
import argparse, hashlib, os, re, shutil, subprocess, sys, time
sys.dont_write_bytecode = True

FULL_AXIOMS = {   # the four axioms of the tier as coqchk names them, and the short names Print Assumptions uses
    'Coq.Reals.ClassicalDedekindReals.sig_not_dec': 'ClassicalDedekindReals.sig_not_dec',
    'Coq.Reals.ClassicalDedekindReals.sig_forall_dec': 'ClassicalDedekindReals.sig_forall_dec',
    'Coq.Logic.FunctionalExtensionality.functional_extensionality_dep': 'FunctionalExtensionality.functional_extensionality_dep',
    'Coq.Logic.Classical_Prop.classic': 'Classical_Prop.classic',
}
THEORY = ('* Theory: Set is predicative', '* Theory: Rewrite rules are not allowed')
UNSAFE = ('* Constants/Inductives relying on type-in-type:', '* Constants/Inductives relying on unsafe (co)fixpoints:',
          '* Inductives whose positivity is assumed:')
LINE = re.compile(r'([0-9a-f]{64})  ([A-Za-z0-9_][A-Za-z0-9_.+-]*(?:/[A-Za-z0-9_][A-Za-z0-9_.+-]*)*)')
ENTRY = re.compile(r"^([A-Za-z_][\w.']*) :(\s|$)")
res = []

def rep(name, ok, det=''):
    res.append(bool(ok)); print('  %-66s %s  %s' % (name, 'ok' if ok else 'FAIL', det)); sys.stdout.flush()
def sha(b): return hashlib.sha256(b).hexdigest()
def raw(p):
    try:
        with open(p, 'rb') as f: return f.read()
    except OSError: return None
def norm(s): return ' '.join(s.split())
def strip_comments(t):
    out, i, d = [], 0, 0
    while i < len(t):
        if t.startswith('(*', i): d += 1; i += 2
        elif d and t.startswith('*)', i): d -= 1; i += 2
        else:
            if not d: out.append(t[i])
            i += 1
    return ''.join(out)
def imports(text):
    """MKF module paths (dir/Mod) a source imports: From MKF.x Require [Import|Export] A B., From MKF Require x.A.,
    Require [Import|Export] MKF.x.A."""
    t = strip_comments(text); out = []
    for m in re.finditer(r'\bFrom\s+MKF((?:\.\w+)*)\s+Require\s+(?:Import\s+|Export\s+)?([^.]+(?:\.[A-Za-z_]\w*)*)\s*\.(?=\s|$)', t):
        pre = m.group(1).strip('.').replace('.', '/')
        for mod in m.group(2).split():
            path = (pre + '/' if pre else '') + mod.replace('.', '/')
            out.append(path)
    for m in re.finditer(r'(?<!\w)Require\s+(?:Import\s+|Export\s+)?((?:MKF\.[\w.]+\s*)+)\.(?=\s|$)', t):
        for mod in m.group(1).split():
            out.append(mod[len('MKF.'):].replace('.', '/'))
    return out
def run(cmd, cwd, out):
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with open(out, 'wb') as f: f.write(p.stdout)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), time.time() - t0
def said(cmd):
    try: return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8', 'replace').strip()
    except OSError: return ''

def read_pa(text, expected):
    viol, entries, cur, header = [], [], None, False
    for ln in text.splitlines():
        if not ln.strip(): continue
        if ln[0].isspace():
            if cur is None: viol.append('continuation outside an entry: ' + ln.strip())
            else: cur.append(ln)
            continue
        if cur is not None: entries.append(norm(' '.join(cur))); cur = None
        if ln == 'Axioms:' and not header: header = True; continue
        if header and ENTRY.match(ln): cur = [ln]; continue
        viol.append('unexpected line: ' + ln[:150])
    if cur is not None: entries.append(norm(' '.join(cur)))
    extra = sorted(set(entries) - expected); missing = sorted(expected - set(entries))
    viol += ['unexpected assumption: ' + e[:120] for e in extra] + ['expected assumption absent: ' + m[:120] for m in missing]
    if len(entries) != len(set(entries)): viol.append('an assumption is listed twice')
    return not viol, entries, viol

def read_chk(text):
    viol, axioms, sec, seen = [], set(), None, set()
    body = text.split('CONTEXT SUMMARY', 1)
    if len(body) != 2: return False, set(), ['no CONTEXT SUMMARY']
    if body[0].strip(): viol.append('output before the summary: ' + norm(body[0])[:150])
    for ln in body[1].splitlines():
        s = ln.strip()
        if not s or set(s) == {'='}: continue
        if ln.startswith('* '):
            sec = None
            if s in THEORY: seen.add(s); continue
            if s == '* Axioms:': sec = 'ax'; seen.add(s); continue
            hit = [u for u in UNSAFE if s.startswith(u)]
            if hit:
                seen.add(hit[0])
                if s != hit[0] + ' <none>': viol.append('unsafe section not empty: ' + s); sec = 'unsafe'
                continue
            viol.append('unknown section: ' + s); continue
        if sec == 'ax': axioms.add(s); continue
        if sec == 'unsafe': viol.append('unsafe entry: ' + s); continue
        viol.append('unexpected line: ' + s[:150])
    for need in THEORY + ('* Axioms:',) + UNSAFE:
        if need not in seen: viol.append('section absent: ' + need)
    if axioms != set(FULL_AXIOMS):
        viol.append('axioms differ: extra %s, absent %s' % (sorted(axioms - set(FULL_AXIOMS)), sorted(set(FULL_AXIOMS) - axioms)))
    return not viol, axioms, viol

def main():
    ap = argparse.ArgumentParser()
    for k in ('src', 'list', 'anchor', 'statement', 'theorem', 'axioms'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--build', default='/build')
    a = ap.parse_args()
    me = raw(os.path.abspath(__file__))
    print('harness %s (author-written; graded as the author\'s)' % sha(me))
    print('coqc: %s | coqchk binary sha256 %s | coqc binary sha256 %s' % (said(['coqc', '--version']).splitlines()[0] if said(['coqc', '--version']) else '?',
          sha(raw(shutil.which('coqchk') or '/nonexistent') or b''), sha(raw(shutil.which('coqc') or '/nonexistent') or b'')))
    folder = os.path.dirname(a.list)
    lb = raw(os.path.join(a.src, a.list))
    # rows 1-3
    rep('1 freeze list is the owner\'s anchor', lb is not None and sha(lb) == a.anchor.lower(),
        'list %s, given %s' % (sha(lb) if lb else 'MISSING', a.anchor.lower()[:16]))
    entries, bad = [], []
    for n, l in enumerate((lb or b'').decode('latin-1').split('\n'), 1):
        if l == '' or l.startswith('#'): continue
        m = LINE.fullmatch(l)
        if m: entries.append((m.group(1), m.group(2)))
        else: bad.append(n)
    paths = [p for _, p in entries]
    rep('2 every line readable, no path twice', lb is not None and not bad and len(paths) == len(set(paths)),
        '%d entries%s' % (len(entries), '' if not bad else '; unreadable lines %s' % bad[:5]))
    wrong = [p for h, p in entries if sha(raw(os.path.join(a.src, p)) or b'MISSING') != h]
    rep('3 every listed file present with its listed sha256', entries and not wrong,
        '%d files' % len(entries) if not wrong else '%d differ: %s' % (len(wrong), ', '.join(wrong[:5])))
    # row 4
    srcs = sorted(p for p in paths if p.endswith('.v') and '/plants/' not in p)
    edges = {}
    for p in srcs:
        b = raw(os.path.join(a.src, p)) or b''
        edges[p] = sorted(set(i + '.v' for i in imports(b.decode('utf-8', 'replace'))))
    outside = sorted(set(d for p in srcs for d in edges[p] if d not in srcs))
    smod, sname = a.statement.rsplit('.', 1); tmod, tname = a.theorem.rsplit('.', 1)
    need = [smod.replace('.', '/') + '.v', tmod.replace('.', '/') + '.v', folder + '/Identity.v', folder + '/Closed.v', a.axioms]
    absent = [n for n in need if n not in paths]
    rep('4 the list covers the closure', not outside and not absent,
        '%d sources, imports all listed; statement, theorem module, Identity, Closed, axioms listed' % len(srcs)
        if not outside and not absent else 'imported but not listed: %s; required but not listed: %s' % (outside[:5], absent))
    # row 5: fresh root
    R = os.path.join(a.build, 'root'); shutil.rmtree(R, ignore_errors=True)
    for p in srcs:
        os.makedirs(os.path.dirname(os.path.join(R, p)), exist_ok=True)
        with open(os.path.join(R, p), 'wb') as f: f.write(raw(os.path.join(a.src, p)))
    have = sorted(os.path.relpath(os.path.join(dp, f), R).replace(os.sep, '/') for dp, _, fs in os.walk(R) for f in fs)
    listed = dict((p, h) for h, p in entries)
    ok5 = have == srcs and all(sha(raw(os.path.join(R, p))) == listed[p] for p in srcs)
    rep('5 fresh root holds exactly the listed sources', ok5, '%d sources' % len(srcs))
    # row 6: compile in import order
    order, done, temp = [], set(), set()
    def visit(p):
        if p in done: return True
        if p in temp: return False
        temp.add(p)
        for d in edges.get(p, []):
            if d in srcs and not visit(d): return False
        temp.discard(p); done.add(p); order.append(p); return True
    acyclic = all(visit(p) for p in srcs)
    O = os.path.join(a.build, 'out'); os.makedirs(O, exist_ok=True)
    failed, tsum = None, 0.0
    if acyclic:
        for p in order:
            rc, txt, dt = run(['coqc', '-R', R, 'MKF', os.path.join(R, p)], R, os.path.join(O, p.replace('/', '.') + '.out'))
            tsum += dt
            if rc != 0: failed = (p, rc, norm(txt)[-300:]); break
    rep('6 every source compiles, in import order', acyclic and failed is None,
        '%d files, %.0f s' % (len(order), tsum) if failed is None and acyclic else ('a cycle in the imports' if not acyclic else 'failed at %s exit %d: %s' % failed))
    # row 7: own check file
    os.makedirs(os.path.join(R, 'hcheck'), exist_ok=True)
    chk = ('From MKF Require %s %s.\nDefinition harness_check : MKF.%s := MKF.%s.\nPrint Assumptions harness_check.\n'
           % (smod, tmod, a.statement, a.theorem))
    with open(os.path.join(R, 'hcheck', 'HarnessCheck.v'), 'w') as f: f.write(chk)
    expected = set(norm(l) for l in (raw(os.path.join(a.src, a.axioms)) or b'').decode('utf-8').splitlines() if l.strip())
    shorts_ok = set(FULL_AXIOMS.values()) == set(e.split(' :', 1)[0] for e in expected)
    rc, txt, dt = run(['coqc', '-R', R, 'MKF', os.path.join(R, 'hcheck', 'HarnessCheck.v')], R, os.path.join(O, 'HarnessCheck.out'))
    ok7, ents, viol = read_pa(txt, expected) if rc == 0 else (False, [], ['exit %d: %s' % (rc, norm(txt)[-250:])])
    rep('7 own check file: type and Print Assumptions exactly the axioms', rc == 0 and ok7 and shorts_ok,
        '%d axioms' % len(ents) if ok7 else '; '.join(viol)[:300])
    # row 8: one recursive coqchk
    rc, txt, dt = run(['coqchk', '-silent', '-o', '-R', R, 'MKF', 'MKF.hcheck.HarnessCheck'], R, os.path.join(O, 'coqchk.out'))
    ok8, ax, viol = read_chk(txt) if rc == 0 else (False, set(), ['exit %d: %s' % (rc, norm(txt)[-250:])])
    rep('8 recursive coqchk, summary read strictly', rc == 0 and ok8,
        'exit 0, %.0f s, axioms %s' % (dt, ', '.join(sorted(ax))) if ok8 else '; '.join(viol)[:300])
    # records
    vos = sorted(os.path.relpath(os.path.join(dp, f), R).replace(os.sep, '/') for dp, _, fs in os.walk(R) for f in fs if f.endswith('.vo'))
    print('  compiled .vo files: %d; digest of their sorted "sha256  path" lines %s' % (len(vos),
          sha(''.join('%s  %s\n' % (sha(raw(os.path.join(R, v))), v) for v in vos).encode())))
    with open(os.path.join(R, 'hcheck', 'Libs.v'), 'w') as f: f.write('From MKF Require hcheck.HarnessCheck.\nPrint Libraries.\n')
    rc, txt, _ = run(['coqc', '-R', R, 'MKF', os.path.join(R, 'hcheck', 'Libs.v')], R, os.path.join(O, 'Libs.out'))
    libs = sorted(set(l.strip() for l in txt.splitlines() if re.match(r'^ +[A-Za-z_][\w.]*$', l) and not l.strip().startswith('MKF.')))
    with open(os.path.join(R, 'hcheck', 'Loc.v'), 'w') as f:
        f.write('From MKF Require hcheck.HarnessCheck.\n' + ''.join('Locate Library %s.\n' % l for l in libs))
    rc2, txt2, _ = run(['coqc', '-R', R, 'MKF', os.path.join(R, 'hcheck', 'Loc.v')], R, os.path.join(O, 'Loc.out'))
    where = dict(re.findall(r'(\S+) has been loaded from file (\S+)', ' '.join(txt2.split())))
    lines = ''.join('%s %s\n' % (l, sha(raw(where[l]) or b'MISSING') if l in where else 'UNLOCATED') for l in libs)
    print('  outside libraries loaded: %d (%d located); digest of their sorted "library sha256" lines %s' % (
        len(libs), len(where), sha(lines.encode())))
    name = os.path.basename(folder)
    print('HARNESS %s %s: %d of %d rows  [anchor %s]' % (name, 'HELD' if all(res) else 'FAILED', sum(res), len(res), a.anchor.lower()[:16]))
    return 0 if all(res) else 1

if __name__ == '__main__':
    sys.exit(main())
