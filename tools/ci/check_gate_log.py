# SPDX-License-Identifier: AGPL-3.0-only
# check_gate_log.py: holds the console of one folder gate run to the anchor, to the tree it ran on, to the libraries
# CI expects, and to the closure the run wrote. It reads; it writes nothing but the --json record.
#
#   python3 -B tools/ci/check_gate_log.py --log F --folder f --anchor HEX --root R --expected-libs F [--json OUT]
#
# --log is the output of `kernel/coq/gate/gate4.py <f> --recheck` as tee wrote it, or a saved CI job log. A byte-order
# mark, a GitHub timestamp at the start of a line and a CR before LF are removed. Only the lines from the gate's header
# ("gate4.py <sha256> judges <f> ...") to its verdict line are judged. --root is the repository root; the folder is
# kernel/coq/<f>, <f> a folder name as the inventory finds them ([a-z][a-z0-9_]*; so are gate.json's "deps", or the
# gate.json is not read). --anchor is the owner's sha256 of kernel/coq/<f>/FROZEN4.txt, given from outside the tree.
#
# Rows, in this order (each prints ok or FAIL and why):
#   1 log: the file reads as UTF-8 text.
#   2 one gate run: exactly one header line and one verdict line, the header first.
#   3 header: it judges this folder, with the sources of its gate.json (its "deps", then itself), with --recheck, and
#     the gate4.py that ran has the sha256 of the tree's kernel/coq/gate/gate4.py.
#   4 anchor line: the gate printed the given anchor, all 64 digits.
#   5 the anchored row: "freeze list is the anchored one  ok  ANCHOR <first 16 digits>", once.
#   6 verdict: "<NAME> GATE4 HELD: n of n  [anchor <first 16 digits>]", NAME from gate.json, the two counts equal.
#   7 rows: no row ends in FAIL, there are as many rows as the verdict counts, and no line between the header and
#     the verdict is one gate4 does not print.
#   8 closure row: "N libraries by the sha256 of their files: 0 from the log, N checked in this run", the same N
#     twice. "0 from the log" is CI confirming 0: no library is believed from an earlier run's log.
#   9 library lines: exactly N lines "checked in this run: <lib> <sha256> exit 0 clean", no library twice, none
#     outside the gate's lines.
#  10 expected file: --expected-libs reads, every line a # comment or "<lib> <sha256>", no library twice.
#  11 compatibility: every library logged is in the expected file with an equal sha256. Every difference is listed.
#  12 identity row: it reports exactly as many axioms as kernel/coq/gate/expected-pa-<tier>.txt lists (counted as
#     kernel/coq/gate/strict_read.py counts them: distinct non-blank lines, whitespace normalised).
#  13 tree: the sha256 of kernel/coq/<f>/FROZEN4.txt is the anchor, and that list holds <f>/gate.json, gate/gate4.py
#     and gate/expected-pa-<tier>.txt once each, with the sha256 they have now. So what this check reads from the
#     tree (name, tier, files, deps, axiom list, gate) is what the anchor fixes.
#  14 completeness: kernel/coq/<f>/out4/Closure.out (the gate's "Print Libraries" of the identity) lists
#     MKF.<f>.<stem> for every file of gate.json "files". Print Libraries lists the required module itself, so the
#     identity's own module is required too (seen in a real out4). If out4 is absent this row fails: the gate writes
#     it, so this check runs in the job that ran the gate. A test points --root at a tree that holds one.
#  15 closure file: the outside (not MKF.) libraries of Closure.out are exactly the libraries logged. The gate checks
#     the closure it wrote; this row shows the library lines cover that closure, no more and no less.
# Then it prints LIBRARY MAP DIGEST <hex>: the sha256 of the sorted, distinct "<lib> <sha256>\n" lines logged.
#
# What a pass shows: this console is one complete --recheck run of the anchored folder by the tree's gate; every row
# passed; every outside library was checked in this run, none taken from a log; each was the file CI expects, by
# sha256; the identity has the expected number of axioms; every file the folder lists is in its identity's closure.
# What a pass does not show: that the console is the real output of a real run (a forged console can be made to
# pass; in CI the check reads the file tee wrote in the same job); that the image is sound (the expected file
# records what four CI image builds loaded, not that it is right); anything a gate row itself does not show.
#
# Output: one line per row, then the digest line, then one verdict line, GATE LOG HELD: n of n rows or GATE LOG
# FAILED: k of n rows failed. Exit 0 only if HELD, 1 if FAILED, 2 on a usage error. A missing input is a FAIL row; so
# is a gate.json that does not parse (nested too deep included) or whose "tier" is not a plain name.
# Standard library only; Python 3.12 or later.
import argparse
import hashlib
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')   # the same bytes on Windows as on Linux
except Exception:
    pass

SCHEMA = 'skuldd-gate-log-check/1'
TS = re.compile(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{1,9}Z ')
FOLDER = re.compile(r'[a-z][a-z0-9_]*')   # the inventory's folder names
HEADER_ANY = re.compile(r'gate4\.py \S+ judges ')
HEADER = re.compile(r'gate4\.py ([0-9a-f]{64}) judges (\S+) \(identity (\S+); sources of ([^)]*)\) '
                    r'in (.*?)(  --recheck)?')
VERDICT_ANY = re.compile(r'(?:\S+ )?GATE4 (?:HELD|FAILED)')
VERDICT_COUNTS = re.compile(r'GATE4 (?:HELD|FAILED): (\d+) of (\d+)')
ROW = re.compile(r'  (\S.*?) +(ok|FAIL)(?:  (.*))?')
LIB_PREFIX = '  checked in this run: '
LIB = re.compile(r'  checked in this run: ([A-Za-z_][\w.]*) ([0-9a-f]{64}) exit (-?\d+) (clean|notclean)')
KNOWN = (re.compile(r'not anchored: no ANCHOR given'), re.compile(r'  sources judged: .*'),
         re.compile(r'  libcache/checked4\.log: \d+ lines not of the form .*'))
ANCHORED = 'freeze list is the anchored one'
CLOSURE = 'closure: every outside library passed coqchk -norec, unsafe <none>'
CLOSURE_COUNTS = re.compile(r'(\d+) libraries by the sha256 of their files: (\d+) from the log, '
                            r'(\d+) checked in this run')
IDENTITY = 'identity: Print Assumptions is exactly the '
FROZEN_LINE = re.compile(r'([0-9a-f]{64})  ([A-Za-z0-9_][A-Za-z0-9_.+-]*(?:/[A-Za-z0-9_][A-Za-z0-9_.+-]*)*)')
CLOSURE_ENTRY = re.compile(r' +[A-Za-z_][\w.]*')
EXPECTED_LINE = re.compile(r'([A-Za-z_][\w.]*) ([0-9a-f]{64})')
V_FILE = re.compile(r'[A-Za-z_]\w*\.v')

NAMES = (
    'log: read as UTF-8 text',
    'log: one gate4 run, its header before its verdict',
    "header: this folder and sources, --recheck, the tree's gate4",
    'anchor line: the given anchor, all 64 digits',
    'freeze list is the anchored one: ok, ANCHOR <16>',
    'verdict: <NAME> GATE4 HELD: n of n [anchor <16>]',
    'every gate row ok, as many as the verdict, no other line',
    'closure row: N libraries, 0 from the log, N checked',
    'library lines: N, each exit 0 clean, none twice',
    'expected-libraries file: read, one hash per library',
    'every library logged is expected, with the expected hash',
    'identity row: as many axioms as expected-pa-<tier> lists',
    "tree: FROZEN4 is the anchor's; gate.json, gate4, PA as listed",
    'out4/Closure.out: every own module of the folder',
    'out4/Closure.out: its outside libraries are those logged',
)


def read_bytes(path):
    try:
        with open(path, 'rb') as f:
            return f.read()
    except (OSError, ValueError):   # ValueError: a path holding a NUL character
        return None


def sha(b):
    return hashlib.sha256(b).hexdigest()


def short(items, k=6):
    items = list(items)
    return ', '.join(items[:k]) + ('' if len(items) <= k else ' and %d more' % (len(items) - k))


def load_cfg(path):
    """The folder's gate.json: (cfg, '') or (None, why)."""
    b = read_bytes(path)
    if b is None:
        return None, 'gate.json cannot be read'
    try:
        c = json.loads(b.decode('utf-8'))
    except (UnicodeDecodeError, ValueError, RecursionError) as e:
        return None, 'gate.json does not parse: %s' % str(e)[:80]
    if not isinstance(c, dict):
        return None, 'gate.json is not an object'
    for k in ('name', 'tier', 'identity'):
        if not isinstance(c.get(k), str) or not c[k]:
            return None, 'gate.json has no "%s"' % k
    if not re.fullmatch(r'[A-Za-z0-9_]+', c['tier']):
        return None, 'gate.json "tier" is not a plain name (letters, digits, underscore)'
    files, deps = c.get('files'), c.get('deps', [])
    if not isinstance(files, list) or not files or not all(isinstance(f, str) and V_FILE.fullmatch(f) for f in files):
        return None, 'gate.json "files" is not a list of plain .v names'
    if not isinstance(deps, list) or not all(isinstance(d, str) and FOLDER.fullmatch(d) for d in deps):
        return None, 'gate.json "deps" is not a list of folder names'
    return c, ''


def main():
    ap = argparse.ArgumentParser(prog='check_gate_log.py', allow_abbrev=False, add_help=False,
                                 description='Check one folder gate log (see the header).')
    ap.add_argument('--log', required=True)
    ap.add_argument('--folder', required=True)
    ap.add_argument('--anchor', required=True)
    ap.add_argument('--root', required=True)
    ap.add_argument('--expected-libs', required=True)
    ap.add_argument('--json')
    a = ap.parse_args()
    if not FOLDER.fullmatch(a.folder):
        ap.error('--folder must be a folder name under kernel/coq (a lower-case letter, then lower-case letters, '
                 'digits or underscores)')
    if not re.fullmatch(r'[0-9a-f]{64}', a.anchor):
        ap.error('--anchor must be exactly 64 lower-case hex digits')
    if a.json and not os.path.isdir(os.path.dirname(os.path.abspath(a.json))):
        ap.error('--json: the folder of %s does not exist' % a.json)
    F, A, A16 = a.folder, a.anchor, a.anchor[:16]
    coq = os.path.join(a.root, 'kernel', 'coq')
    rows = []

    def rep(ok, detail):
        rows.append((NAMES[len(rows)], bool(ok), detail))

    # The tree's inputs: gate.json, gate4.py, the expected axioms, FROZEN4.txt, out4/Closure.out.
    cfg, cfg_why = load_cfg(os.path.join(coq, F, 'gate.json'))
    gate4 = read_bytes(os.path.join(coq, 'gate', 'gate4.py'))
    epa_rel = 'gate/expected-pa-%s.txt' % cfg['tier'] if cfg else None
    epa = read_bytes(os.path.join(coq, *epa_rel.split('/'))) if cfg else None

    # 1. the log
    logb = read_bytes(a.log)
    text, why = None, 'cannot be read'
    if logb is not None:
        try:
            text = logb.decode('utf-8')
        except UnicodeDecodeError as e:
            why = 'not UTF-8 at byte %d' % e.start
    lines, stamped = [], 0
    if text is not None:
        if text.startswith('\ufeff'):
            text = text[1:]
        raw = text.split('\n')
        if raw and raw[-1] == '':
            raw.pop()
        for line in raw:
            if line.endswith('\r'):
                line = line[:-1]
            m = TS.match(line)
            if m:
                line, stamped = line[m.end():], stamped + 1
            lines.append(line)
    rep(text is not None, '%d lines, %d GitHub timestamps removed' % (len(lines), stamped) if text is not None else why)

    # 2. one gate run: the section from the header to the first verdict after it
    heads = [i for i, x in enumerate(lines) if HEADER_ANY.match(x)]
    verds = [i for i, x in enumerate(lines) if VERDICT_ANY.match(x)]
    h0 = heads[0] if heads else None
    after = [i for i in verds if h0 is None or i > h0]
    v0 = after[0] if after else None
    one = len(heads) == 1 and len(verds) == 1 and v0 is not None
    late = '' if v0 is not None or not verds else ', no verdict after the header'
    rep(one, 'header at line %d, verdict at line %d' % (h0 + 1, v0 + 1) if one else
        '%d header lines, %d verdict lines%s' % (len(heads), len(verds), late))
    lo = h0 + 1 if h0 is not None else 0
    hi = v0 if v0 is not None else len(lines)
    body = lines[lo:hi]
    outside = lines[:lo] + lines[hi + 1:]
    rowl, libl, anch, unknown = [], [], [], []
    for x in body:
        if x.startswith(LIB_PREFIX):
            libl.append(x)
        elif x.startswith('anchor '):
            anch.append(x)
        elif any(k.fullmatch(x) for k in KNOWN):
            continue
        else:
            m = ROW.fullmatch(x)
            if m:
                rowl.append((m.group(1), m.group(2), m.group(3) or '', x))
            else:
                unknown.append(x)

    # 3. the header
    bad = []
    hm = HEADER.fullmatch(lines[h0]) if h0 is not None else None
    if h0 is None:
        bad.append('no line "gate4.py <sha256> judges <folder> ..."')
    elif not hm:
        bad.append('the header is not in the form gate4 prints')
    else:
        if hm.group(2) != F:
            bad.append('it judges %s, not %s' % (hm.group(2)[:40], F))
        if cfg is None:
            bad.append(cfg_why)
        else:
            if hm.group(3) != '%s.%s' % (F, cfg['identity']):
                bad.append('identity %s, gate.json says %s.%s' % (hm.group(3)[:60], F, cfg['identity']))
            want = ', '.join([d.strip('/') for d in cfg.get('deps', [])] + [F])
            if hm.group(4) != want:
                bad.append('sources of "%s", gate.json says "%s"' % (hm.group(4)[:120], want))
        if not hm.group(6):
            bad.append('run without --recheck')
        if gate4 is None:
            bad.append('kernel/coq/gate/gate4.py cannot be read')
        elif hm.group(1) != sha(gate4):
            bad.append('the gate4.py that ran is %s, the tree\'s is %s' % (hm.group(1)[:16], sha(gate4)[:16]))
    rep(not bad, '; '.join(bad) if bad else 'judges %s, sources of %s, --recheck, gate4.py %s'
        % (F, hm.group(4), hm.group(1)[:16]))

    # 4. the anchor line
    if len(anch) != 1:
        rep(False, '%d anchor lines between the header and the verdict' % len(anch))
    else:
        rep(anch[0] == 'anchor ' + A, 'anchor %s..., all 64 digits equal' % A16 if anch[0] == 'anchor ' + A else
            'the gate printed "%s", the given anchor is %s' % (anch[0][:80], A))

    # 5. the anchored row
    ar = [r for r in rowl if r[0] == ANCHORED]
    ok = len(ar) == 1 and re.fullmatch(r'  freeze list is the anchored one +ok  ANCHOR %s' % A16, ar[0][3])
    rep(ok, 'ANCHOR %s' % A16 if ok else '%d such rows%s' % (len(ar), '' if len(ar) != 1 else
                                                            ': "%s"' % ' '.join(ar[0][3].split())[:120]))

    # 6. the verdict line
    vline = lines[v0] if v0 is not None else None
    vc = VERDICT_COUNTS.search(vline) if vline is not None else None
    total = int(vc.group(2)) if vc else None
    if vline is None:
        rep(False, 'no verdict line after the header')
    elif cfg is None:
        rep(False, cfg_why)
    else:
        m = re.fullmatch(re.escape(cfg['name']) + r' GATE4 HELD: (\d+) of (\d+)  \[anchor ' + A16 + r'\]', vline)
        ok = m and m.group(1) == m.group(2) and int(m.group(2)) >= 1
        rep(ok, vline if ok else '"%s" is not "%s GATE4 HELD: n of n  [anchor %s]"' % (vline[:120], cfg['name'], A16))

    # 7. every row ok, as many as the verdict counts, nothing else
    fails = [r[0] for r in rowl if r[1] == 'FAIL']
    bad = []
    if fails:
        bad.append('%d rows FAIL: %s' % (len(fails), short(fails, 4)))
    if total is None:
        bad.append('no verdict count to compare %d rows with' % len(rowl))
    elif len(rowl) != total:
        bad.append('%d rows, the verdict counts %d' % (len(rowl), total))
    if unknown:
        bad.append('%d lines gate4 does not print, first: "%s"' % (len(unknown), unknown[0][:100]))
    rep(not bad, '; '.join(bad) if bad else '%d rows ok, none FAIL, no other line' % len(rowl))

    # 8. the closure row: CI confirms 0
    cr = [r for r in rowl if r[0] == CLOSURE]
    counts = CLOSURE_COUNTS.search(cr[0][3]) if len(cr) == 1 else None
    N, FL, M = (int(counts.group(1)), int(counts.group(2)), int(counts.group(3))) if counts else (None, None, None)
    if len(cr) != 1:
        rep(False, '%d closure rows for the outside libraries' % len(cr))
    else:
        m = re.fullmatch(r'  ' + re.escape(CLOSURE) + r' +ok  (\d+) libraries by the sha256 of their files: '
                         r'0 from the log, (\d+) checked in this run', cr[0][3])
        ok = m and m.group(1) == m.group(2) and int(m.group(1)) >= 1
        rep(ok, '%d libraries: 0 from the log, %d checked in this run' % (N, M) if ok else
            '"%s"' % ' '.join(cr[0][3].split())[:200])

    # 9. the library lines
    parsed, unread = [], []
    for x in libl:
        m = LIB.fullmatch(x)
        if m:
            parsed.append((m.group(1), m.group(2), m.group(3), m.group(4)))
        else:
            unread.append(x)
    seen, twice = set(), set()
    for p in parsed:
        (twice if p[0] in seen else seen).add(p[0])
    notclean = ['%s exit %s %s' % (p[0], p[2], p[3]) for p in parsed if p[2] != '0' or p[3] != 'clean']
    outl = [x for x in outside if x.startswith(LIB_PREFIX)]
    bad = []
    if unread:
        bad.append('%d lines not "checked in this run: <lib> <sha256> exit <n> <clean|notclean>"' % len(unread))
    if notclean:
        bad.append('%d not exit 0 clean: %s' % (len(notclean), short(notclean, 4)))
    if twice:
        bad.append('twice: %s' % short(sorted(twice)))
    if outl:
        bad.append('%d library lines outside the gate\'s lines' % len(outl))
    if N is None:
        bad.append('no closure row to count %d library lines against' % len(libl))
    elif len(libl) != N or len(libl) != M:
        bad.append('%d library lines, the closure row says %d libraries, %d checked in this run' % (len(libl), N, M))
    rep(not bad, '; '.join(bad) if bad else '%d lines, each exit 0 clean, none twice' % len(libl))

    # 10. the expected file
    eb = read_bytes(a.expected_libs)
    expected, ebad, etwice, etext = {}, [], [], None
    if eb is not None:
        try:
            etext = eb.decode('utf-8')
        except UnicodeDecodeError:
            etext = None
    if etext is not None:
        el = etext.split('\n')
        if el and el[-1] == '':
            el.pop()
        for n, x in enumerate(el, 1):
            if x == '' or x.startswith('#'):
                continue
            m = EXPECTED_LINE.fullmatch(x)
            if not m:
                ebad.append('line %d' % n)
            elif m.group(1) in expected:
                etwice.append(m.group(1))
            else:
                expected[m.group(1)] = m.group(2)
    if etext is None:
        rep(False, 'cannot be read' if eb is None else 'not UTF-8')
    else:
        bad = (['not "<lib> <sha256>": %s' % short(ebad)] if ebad else []) + \
              (['twice: %s' % short(etwice)] if etwice else []) + ([] if expected else ['no library in it'])
        rep(not bad, '; '.join(bad) if bad else '%d libraries' % len(expected))

    # 11. compatibility: every library logged is expected, by sha256
    pairs = sorted(set((p[0], p[1]) for p in parsed))
    diffs = []
    for lib, h in pairs:
        e = expected.get(lib)
        if e != h:
            diffs.append({'library': lib, 'expected': e, 'logged': h})
    if not expected:
        rep(False, 'no expected library to compare with')
    elif not pairs:
        rep(False, 'no library logged')
    else:
        txt = ['%s: %s, logged %s' % (d['library'], 'not expected' if d['expected'] is None else
                                      'expected ' + d['expected'][:16], d['logged'][:16]) for d in diffs]
        rep(not diffs, '%d differences: %s' % (len(diffs), '; '.join(txt)) if diffs else
            '%d of %d libraries expected, every sha256 equal' % (len(pairs), len(pairs)))

    # 12. the identity row's axiom count
    ir = [r for r in rowl if r[0].startswith(IDENTITY)]
    if cfg is None:
        rep(False, cfg_why)
    elif epa is None:
        rep(False, 'kernel/coq/%s cannot be read' % epa_rel)
    else:
        try:
            want = len(set(' '.join(x.split()) for x in epa.decode('utf-8').splitlines() if x.strip()))
        except UnicodeDecodeError:
            want = None
        m = (re.fullmatch(r'  ' + re.escape(IDENTITY + cfg['tier']) + r' list +ok  (\d+) axioms', ir[0][3])
             if len(ir) == 1 else None)
        ok = m and want is not None and int(m.group(1)) == want
        rep(ok, '%d axioms, as %s lists' % (want, epa_rel[5:]) if ok else
            '%d identity rows; %s lists %s axioms%s' % (len(ir), epa_rel[5:], want,
                                                       '' if len(ir) != 1 else
                                                       '; the row: "%s"' % ' '.join(ir[0][3].split())[:120]))

    # 13. the tree's inputs are the anchored ones
    fz = read_bytes(os.path.join(coq, F, 'FROZEN4.txt'))
    bad = [] if cfg else [cfg_why]
    if fz is None:
        bad.append('kernel/coq/%s/FROZEN4.txt cannot be read' % F)
    else:
        if sha(fz) != A:
            bad.append('kernel/coq/%s/FROZEN4.txt is %s, not the anchor' % (F, sha(fz)[:16]))
        listed = {}
        for x in fz.decode('latin-1').split('\n'):
            m = FROZEN_LINE.fullmatch(x)
            if m:
                listed.setdefault(m.group(2), []).append(m.group(1))
        for p in ['%s/gate.json' % F, 'gate/gate4.py'] + ([epa_rel] if epa_rel else []):
            hs, now = listed.get(p, []), read_bytes(os.path.join(coq, *p.split('/')))
            if len(hs) != 1:
                bad.append('%s is on the list %d times' % (p, len(hs)))
            elif now is None:
                bad.append('%s cannot be read' % p)
            elif sha(now) != hs[0]:
                bad.append('%s is %s, the list holds %s' % (p, sha(now)[:16], hs[0][:16]))
    rep(not bad, '; '.join(bad) if bad else 'FROZEN4.txt is the anchor; %s/gate.json, gate/gate4.py, %s as listed'
        % (F, epa_rel))

    # 14 and 15. the closure the run wrote
    co_rel = 'kernel/coq/%s/out4/Closure.out' % F
    co = read_bytes(os.path.join(coq, F, 'out4', 'Closure.out'))
    absent = '%s cannot be read: the gate writes it, so this check runs in the job that ran the gate' % co_rel
    entries = set()
    if co is not None:
        entries = set(x.strip() for x in co.decode('utf-8', 'replace').splitlines() if CLOSURE_ENTRY.fullmatch(x))
    if co is None:
        rep(False, absent)
    elif cfg is None:
        rep(False, cfg_why)
    else:
        own = ['MKF.%s.%s' % (F, f[:-2]) for f in cfg['files']]
        missing = [o for o in own if o not in entries]
        rep(not missing, 'missing: %s' % short(missing) if missing else
            '%d of %d own modules, %s.%s among them' % (len(own), len(own), F, cfg['identity']))
    ext = set(e for e in entries if not e.startswith('MKF.'))
    logged = set(p[0] for p in parsed)
    if co is None:
        rep(False, absent)
    else:
        a_only, l_only = sorted(ext - logged), sorted(logged - ext)
        ok = ext and not a_only and not l_only
        rep(ok, '%d outside libraries, the same as logged' % len(ext) if ok else
            '%d in Closure.out, %d logged; not logged: %s; not in Closure.out: %s'
            % (len(ext), len(logged), short(a_only) or 'none', short(l_only) or 'none'))

    digest = sha(''.join(sorted(set('%s %s\n' % (lib, h) for lib, h in pairs))).encode('utf-8'))
    failed = sum(1 for r in rows if not r[1])
    held = failed == 0
    verdict = ('GATE LOG HELD: %d of %d rows' % (len(rows), len(rows)) if held else
               'GATE LOG FAILED: %d of %d rows failed' % (failed, len(rows)))
    for name, ok, det in rows:
        print('  %-62s %s  %s' % (name, 'ok' if ok else 'FAIL', det))
    print('LIBRARY MAP DIGEST %s' % digest)
    if a.json:
        obj = {'schema': SCHEMA, 'folder': F, 'anchor': A, 'name': cfg['name'] if cfg else None,
               'gate_log_sha256': sha(logb) if logb is not None else None, 'gate_verdict_line': vline,
               'gate_rows': len(rowl), 'library_count': len(pairs), 'library_map_digest': digest,
               'libraries': dict(pairs), 'differences': diffs,
               'rows': [{'name': n, 'ok': o, 'detail': d} for n, o, d in rows], 'verdict': verdict, 'held': held}
        try:
            with open(a.json, 'w', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + '\n')
        except OSError as e:
            print('check_gate_log: cannot write --json: %s' % e, file=sys.stderr)
            return 2
    print(verdict)
    return 0 if held else 1


if __name__ == '__main__':
    sys.exit(main())
