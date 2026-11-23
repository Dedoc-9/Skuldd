# SPDX-License-Identifier: AGPL-3.0-only
# The test of tools/ci/judge_digest.py (standard library only). It copies this repository's judge files into
# temporary trees, runs the judge on them as a subprocess, and requires each case's outcome exactly as
# tools/ci/tests/PREDICTIONS-judge_digest.txt (and -2.txt to -8.txt, later rounds) states it. Each file was
# written, and its sha256 recorded, before the first run of its cases. Each line names a case, its outcome and, for a
# plant, the row that must fail. C01 and C02 count the rows from this test's own table of the groups (GROUP_COUNT).
#   C  the honest twin: HELD; its digest equals this test's own computation from the formula in
#      tools/ci/judge_digest.py's header; the same when computed twice; the same when the files are written in
#      another order or handed to the digest in any order.
#   P  plants: each must give "CI JUDGE FAILED" with its named row failing.
#   D  decoys: changes the judge must not see (outside its files, or in a __pycache__ folder, which it skips).
#   U  usage errors: exit 2 and no verdict line.
#   M  run mode: without --inventory-json the judge runs tools/ci/inventory.py; it must agree with that script's own
#      outcome and digest.
#   Q, R, S  the later rounds' plants (-2.txt, -3.txt, -4.txt): each file's header says what they add.
#   T  usage errors of the fifth file: a --json path among the judge files spelled with a long-path prefix (\\?\ on
#      Windows, a leading "//" on POSIX) and the same path written plainly: exit 2, no verdict line, nothing written;
#      of the sixth file: the same path as Windows' volume GUID path (a leading "//" on POSIX, which has none); of
#      the seventh: --json a new name (a hard link, made outside the tree) of a judge file, which the judge would
#      write through: exit 2, no verdict line, the judge file's bytes unchanged.
#   V  the eighth file's cases, for the group boundaries-frozen (ruling S282-3 (b)): BOUNDARIES.md and each
#      kernel/coq/<folder>/FROZEN.txt changed, added, removed, made a folder or reached through a link; decoys beside
#      them, under kernel/records and two levels down; --json naming one of them (exit 2, the path as it was).
# When this tree lacks a judge file (before that file is added), the copies hold a stand-in, and a note says so:
# the cases test the judge, not the tree. The judge's run on the real tree is a separate step.
# What a pass shows: the judge computes the digest of that header's formula over the groups it lists, every plant
# turns its named row red, and a missing or malformed input fails closed. What it does not show: the same digest on
# another system (run the test there too), or that the judge's set of files is the right one.
#   python3 -B tools/ci/tests/test_judge_digest.py
# Last line: "TEST judge_digest HELD: n of n cases" (exit 0) or "TEST judge_digest FAILED: k of n cases failed"
# (exit 1).
import hashlib
import json
import os
import random
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
JUDGE = os.path.join(REPO, 'tools', 'ci', 'judge_digest.py')
# Each file was frozen before the first run of the cases it adds; a later round adds a file, never edits one.
PREDICTIONS = ('PREDICTIONS-judge_digest.txt', 'PREDICTIONS-judge_digest-2.txt', 'PREDICTIONS-judge_digest-3.txt',
               'PREDICTIONS-judge_digest-4.txt', 'PREDICTIONS-judge_digest-5.txt', 'PREDICTIONS-judge_digest-6.txt',
               'PREDICTIONS-judge_digest-7.txt', 'PREDICTIONS-judge_digest-8.txt')
# T01's path prefix: a long-path prefix on Windows; a leading "//" on POSIX, which has none
LONG = '\\\\?\\' if os.name == 'nt' else '/'
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')

# The judge's files as the groups in tools/ci/judge_digest.py's header list them, written here apart from the
# judge's own table.
WORKFLOWS = '.github/workflows'
ROW4_PREDICTIONS = 'kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md'
ROW4_PLANTS = 'kernel/hardening/features/plants4'
SINGLE = ('.github/CODEOWNERS', 'tools/check_manifests.py', 'kernel/coq/EXPECTED-CI-LIBRARIES.txt',
          'kernel/hardening/features/feature_row3.py', 'kernel/hardening/features/feature_row4.py',
          'kernel/coq/ANCHORS.md', 'kernel/runtime/check_fpenv.py', 'kernel/runtime/test_fpenv.c', 'THEOREMS.md',
          ROW4_PREDICTIONS)
TREES = ('tools/ci', 'ci/mathkernel', 'kernel/coq/gate', ROW4_PLANTS)
OPTIONAL_TREES = ('.github/actions',)   # may be absent; every file under it is judged
COPIED_TREES = ('.github',) + TREES
# The group boundaries-frozen: the boundary map and FROZEN_NAME in each folder directly under FROZEN_TOP.
MAP = 'BOUNDARIES.md'
FROZEN_TOP = 'kernel/coq'
FROZEN_NAME = 'FROZEN.txt'
# The groups: workflows, each single file, each tree, the two optional ones (top-level *.py, .github/actions) and
# boundaries-frozen.
GROUP_COUNT = 1 + len(SINGLE) + len(TREES) + 2 + 1
OUTSIDE = 'README.md'
SKIP = ('__pycache__', 'out4', 'libcache', '.git')
# What the inventory reads, copied for the run-mode case only.
INVENTORY_INPUTS = ('kernel/coq', 'verdandi/mathkernel/F32', 'THEOREMS.md')

ROW = re.compile(r'  (?P<name>\S.*?) +(?P<st>ok|FAIL)  (?P<detail>.*)')
DIGEST = re.compile(r'CI JUDGE DIGEST ([0-9a-f]{64}|none)')
VERDICT = re.compile(r'CI JUDGE (HELD: (\d+) of (\d+) rows|FAILED: (\d+) of (\d+) rows failed)')
CHANGED = 'the CI judge changed: after review the owner sets MK_ANCHOR_CI to '


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(path):
    with open(path, 'rb') as fh:
        return fh.read()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def at(tree, rel):
    return os.path.join(tree, *rel.split('/'))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


# ---- the source: this repository's judge files, read once ----

def walk_files(base, rel):
    out = []
    top = at(base, rel)
    for dp, dn, fn in os.walk(top):
        dn[:] = sorted(d for d in dn if d not in SKIP)
        for f in sorted(fn):
            out.append(os.path.relpath(os.path.join(dp, f), base).replace(os.sep, '/'))
    return out


def frozen_records(base):
    """The '/' paths of FROZEN_NAME (its exact case) in each folder directly under FROZEN_TOP of base."""
    top = at(base, FROZEN_TOP)
    if not os.path.isdir(top):
        return []
    return ['%s/%s/%s' % (FROZEN_TOP, n, FROZEN_NAME) for n in sorted(os.listdir(top))
            if os.path.isdir(os.path.join(top, n)) and FROZEN_NAME in os.listdir(os.path.join(top, n))]


def load_source():
    """({rel: bytes}, [stand-in notes])."""
    files, notes = {}, []
    for t in COPIED_TREES:
        for rel in walk_files(REPO, t):
            files[rel] = read(at(REPO, rel))
    frozen = frozen_records(REPO)
    for rel in frozen:
        files[rel] = read(at(REPO, rel))
    if not frozen:
        files['%s/stand32/%s' % (FROZEN_TOP, FROZEN_NAME)] = b'stand-in\n'
        notes.append('note: stand-in for %s/*/%s (this tree has none)' % (FROZEN_TOP, FROZEN_NAME))
    for rel in SINGLE + (MAP, OUTSIDE):
        if os.path.isfile(at(REPO, rel)):
            files[rel] = read(at(REPO, rel))
        else:
            files[rel] = b'stand-in written by test_judge_digest.py: this tree has no such file yet\n'
            notes.append('note: stand-in for %s (this tree has none)' % rel)
    for t in TREES:
        if not any(r.startswith(t + '/') for r in files):
            files[t + '/stand-in.txt'] = b'stand-in\n'
            notes.append('note: stand-in for %s/ (this tree has no file there)' % t)
    return files, notes


def materialize(tree, files, reverse=False):
    for rel in sorted(files, key=lambda r: r.encode('utf-8'), reverse=reverse):
        write(at(tree, rel), files[rel])


# ---- the digest by the formula in tools/ci/judge_digest.py's header, computed here apart from the judge ----

def spec_entries(tree):
    paths = set()
    wf = at(tree, WORKFLOWS)
    if os.path.isdir(wf):
        for n in os.listdir(wf):
            if n.lower().endswith(('.yml', '.yaml')) and os.path.isfile(os.path.join(wf, n)):
                paths.add(WORKFLOWS + '/' + n)
    for rel in SINGLE + (MAP,):
        if os.path.isfile(at(tree, rel)):
            paths.add(rel)
    paths.update(frozen_records(tree))
    for t in TREES + OPTIONAL_TREES:
        for dp, dn, fn in os.walk(at(tree, t)):
            if t == 'tools/ci':
                dn[:] = [d for d in dn if d != '__pycache__']
            for f in fn:
                paths.add(os.path.relpath(os.path.join(dp, f), tree).replace(os.sep, '/'))
    for n in os.listdir(tree):
        if n.endswith('.py') and os.path.isfile(os.path.join(tree, n)):
            paths.add(n)
    return [(p, sha(read(at(tree, p)))) for p in paths]


def spec_digest(entries, inventory_digest):
    text = b''.join(('%s  %s\n' % (s, p)).encode('utf-8')
                    for p, s in sorted(entries, key=lambda e: e[0].encode('utf-8')))
    return sha(text + ('inventory %s\n' % inventory_digest).encode('ascii'))


# ---- inventory JSON files ----

def inventory_body(variant=b''):
    return {
        'gated': [{'folder': 'f32', 'files': ['Identity.v', 'Spec.v'], 'plants': ['plants/bad.v'],
                   'frozen4_sha256': sha(b'a frozen list' + variant),
                   'identity_names': ['MKF.f32.Spec.spec']}],
        'mirrors': [{'folder': 'f32', 'frozen4_sha256': sha(b'a frozen list' + variant)}],
        'gate_dir_files': ['expected-pa-flocq4.txt', 'freeze4.py', 'gate4.py', 'strict_read.py'],
    }


def inventory_doc(variant=b'', verdict='INVENTORY HELD: 1 of 1 rows'):
    body = inventory_body(variant)
    return dict(body, schema='skuldd-inventory/1', digest=sha(canonical(body)), verdict=verdict,
                held=verdict.startswith('INVENTORY HELD: '))


def dump(obj):
    return (json.dumps(obj, sort_keys=True, indent=1) + '\n').encode('ascii')


FAKE_INVENTORY = '\n'.join([
    '# a fake inventory.py written by test_judge_digest.py',
    'import hashlib, json, sys',
    'a = sys.argv',
    'out = a[a.index("--json") + 1]',
    'body = {"gated": [], "mirrors": [], "gate_dir_files": ["gate4.py"]}',
    'd = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()',
    'MODE = %r',
    'verdict = "INVENTORY FAILED: 1 of 1 rows failed" if MODE == "failed" else "INVENTORY HELD: 1 of 1 rows"',
    'doc = dict(body, schema="skuldd-inventory/1", digest=d, verdict=verdict, held=MODE != "failed")',
    'open(out, "w").write(json.dumps(doc, sort_keys=True))',
    'print("INVENTORY DIGEST " + ("0" * 64 if MODE == "lies" else d))',
    'print(verdict)',
    'sys.exit(1 if MODE == "failed" else 0)',
    '',
])


# ---- running the judge ----

class Result(object):
    def __init__(self, code, out, err):
        self.code, self.out, self.err = code, out, err
        self.rows = {}
        for line in out:
            m = ROW.fullmatch(line)
            if m:
                self.rows[m.group('name')] = (m.group('st'), m.group('detail'))
        ds = [m.group(1) for m in (DIGEST.fullmatch(x) for x in out) if m]
        self.digests = ds
        self.digest = ds[0] if len(ds) == 1 and ds[0] != 'none' else None
        self.verdicts = [m for m in (VERDICT.fullmatch(x) for x in out) if m]

    def failing(self):
        return sorted(n for n, (st, _d) in self.rows.items() if st == 'FAIL')


def run_judge(args, script=JUDGE):
    p = subprocess.run([sys.executable, '-B', script] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV, timeout=900)
    return Result(p.returncode, p.stdout.decode('utf-8', 'replace').splitlines(),
                  p.stderr.decode('utf-8', 'replace'))


def shape(res):
    """Why the output is not one row block, one digest line and one last verdict line, or ''."""
    if len(res.verdicts) != 1 or len(res.out) < 2 or not VERDICT.fullmatch(res.out[-1]):
        return 'not exactly one verdict line, last'
    if len(res.digests) != 1 or not DIGEST.fullmatch(res.out[-2]):
        return 'not exactly one digest line, before the verdict'
    if len(res.rows) != len(res.out) - 2:
        return 'a line that is neither a row, the digest nor the verdict'
    v = res.verdicts[0]
    k = len(res.failing())
    if v.group(2) is not None:
        if k or int(v.group(2)) != len(res.rows) or v.group(2) != v.group(3):
            return 'the HELD verdict does not count the rows'
    elif int(v.group(4)) != k or int(v.group(5)) != len(res.rows) or k == 0:
        return 'the FAILED verdict does not count the rows'
    return ''


def outcome(res, predicted):
    """(ok, detail) for a predicted outcome HELD, FAILED <row> or USAGE."""
    if predicted == 'USAGE':
        ok = res.code == 2 and not res.verdicts
        return ok, 'exit %d, %d verdict line(s)' % (res.code, len(res.verdicts))
    bad = shape(res)
    if bad:
        return False, 'exit %d; %s' % (res.code, bad)
    if predicted == 'HELD':
        ok = res.code == 0 and not res.failing()
        return ok, 'exit %d, %s' % (res.code, res.out[-1])
    if predicted.startswith('FAILED '):
        name = predicted[len('FAILED '):]
        st = res.rows.get(name, ('absent', ''))[0]
        ok = res.code == 1 and st == 'FAIL'
        return ok, 'exit %d, row "%s" %s; failing: %s' % (res.code, name, st, ', '.join(res.failing()))
    return False, 'unknown predicted outcome %r' % predicted


def change_one_byte(path):
    b = read(path)
    write(path, b[:-1] + bytes([b[-1] ^ 0x01]) if b else b'x')


def make_link(target, link):
    if os.name == 'nt':
        import _winapi
        _winapi.CreateJunction(target, link)
    else:
        os.symlink(target, link, target_is_directory=True)


def load_judge_module():
    """The judge as a module, compiled from its source (never a cached .pyc)."""
    mod = types.ModuleType('judge_digest_under_test')
    mod.__file__ = JUDGE
    exec(compile(read(JUDGE), JUDGE, 'exec'), mod.__dict__)
    return mod


class Ctx(object):
    def __init__(self, base, files):
        self.base, self.files, self.n = base, files, 0
        self.inv = os.path.join(base, 'inventory.json')
        write(self.inv, dump(inventory_doc()))
        self.inv_digest = inventory_doc()['digest']
        self.D = None
        self.links = []

    def path(self, name):
        self.n += 1
        return os.path.join(self.base, '%s%02d' % (name, self.n))

    def fresh(self, reverse=False):
        tree = self.path('t')
        os.makedirs(tree)
        materialize(tree, self.files, reverse)
        return tree

    def std(self, expect=True):
        args = ['--inventory-json', self.inv]
        return args + (['--expect', self.D or 'no-honest-digest'] if expect else [])


# ---- the cases ----

def c01(ctx, predicted):
    tree = ctx.fresh()
    res = run_judge(['--root', tree] + ctx.std(expect=False))
    ok, detail = outcome(res, predicted)
    mine = spec_digest(spec_entries(tree), ctx.inv_digest)
    ctx.D = res.digest
    same = res.digest == mine
    return ok and same and len(res.rows) == GROUP_COUNT + 3, '%s; %d rows; digest %s, the formula computed here %s' % (
        detail, len(res.rows), (res.digest or 'none')[:16], 'agrees' if same else 'DIFFERS: ' + mine[:16])


def c02(ctx, predicted):
    tree = ctx.fresh()
    r1 = run_judge(['--root', tree] + ctx.std())
    r2 = run_judge(['--root', tree] + ctx.std())
    ok1, d1 = outcome(r1, predicted)
    ok2, _d2 = outcome(r2, predicted)
    same = r1.digest == r2.digest == ctx.D and r1.out == r2.out
    return ok1 and ok2 and same and len(r1.rows) == GROUP_COUNT + 4, '%s; twice: %s' % (
        d1, 'the same digest and output' if same else 'DIFFERENT')


def c03(ctx, predicted):
    tree = ctx.fresh()
    entries = spec_entries(tree)
    mod = load_judge_module()
    orders = [sorted(entries), sorted(entries, reverse=True)]
    for seed in (0, 1, 2):
        e = list(entries)
        random.Random(seed).shuffle(e)
        orders.append(e)
    values = set(mod.digest_of(e, ctx.inv_digest) for e in orders)
    try:
        mod.digest_of(entries + entries[:1], ctx.inv_digest)
        dup = False
    except ValueError:
        dup = True
    ok = values == set([ctx.D]) and dup and predicted == 'SAME'
    return ok, '%d orders give %d value(s)%s; a path listed twice is refused: %s' % (
        len(orders), len(values), ' (the honest digest)' if values == set([ctx.D]) else '', dup)


def c04(ctx, predicted):
    tree = ctx.fresh(reverse=True)
    res = run_judge(['--root', tree] + ctx.std())
    ok, detail = outcome(res, predicted)
    return ok and res.digest == ctx.D, '%s; files written in reverse order: digest %s' % (
        detail, 'the same' if res.digest == ctx.D else 'DIFFERENT')


def c05(ctx, predicted):
    tree = ctx.fresh()
    outs = [ctx.path('j') + '.json', ctx.path('j') + '.json']
    rs = [run_judge(['--root', tree, '--json', o] + ctx.std()) for o in outs]
    ok, detail = outcome(rs[0], predicted)
    problems = []
    try:
        raw = [read(o) for o in outs]
        doc = json.loads(raw[0].decode('ascii'))
    except (OSError, ValueError) as e:
        return False, '%s; the JSON cannot be read (%s)' % (detail, type(e).__name__)
    if raw[0] != raw[1]:
        problems.append('two runs wrote different JSON')
    if doc.get('schema') != 'skuldd-ci-judge/1':
        problems.append('schema')
    if doc.get('digest') != rs[0].digest or doc.get('digest') != ctx.D:
        problems.append('digest')
    if doc.get('held') is not True or doc.get('verdict') != rs[0].out[-1]:
        problems.append('verdict')
    if doc.get('inventory_digest') != ctx.inv_digest:
        problems.append('inventory digest')
    paths = [f.get('path') for f in doc.get('files', [])]
    if paths != sorted(paths, key=lambda p: p.encode('utf-8')):
        problems.append('files not sorted by path bytes')
    mine = dict(spec_entries(tree))
    if dict((f.get('path'), f.get('sha256')) for f in doc.get('files', [])) != mine:
        problems.append('files differ from this test\'s own listing')
    if len(doc.get('rows', [])) != len(rs[0].rows):
        problems.append('rows')
    return ok and not problems, '%s; JSON %s' % (detail, 'agrees' if not problems else ', '.join(problems))


def plant(mutate, args=None, changed=True):
    """A case: mutate a fresh honest tree, run the judge with the honest inventory and --expect D. For a plant on
    the files (changed=True) the expected-digest row must name a new digest; for a plant on --expect alone
    (changed=False) the digest stays the honest one and the row must still name it as the value to set."""
    def case(ctx, predicted):
        tree = ctx.fresh()
        note = mutate(ctx, tree) or ''
        res = run_judge(['--root', tree] + (args(ctx, tree) if args else ctx.std()))
        ok, detail = outcome(res, predicted)
        if ok and predicted == 'FAILED expected digest':
            d = res.rows['expected digest'][1]
            if changed and (res.digest is None or res.digest == ctx.D or not d.startswith(CHANGED + res.digest)):
                ok = False
                detail += '; the row does not name a new digest'
            if not changed and (res.digest != ctx.D or ('MK_ANCHOR_CI to %s' % ctx.D) not in d):
                ok = False
                detail += '; the row does not name the honest digest'
        return ok, detail + (('; ' + note) if note else '')
    return case


def first_workflow(ctx):
    wf = sorted(r for r in ctx.files if r.startswith(WORKFLOWS + '/') and '/' not in r[len(WORKFLOWS) + 1:]
                and r.lower().endswith(('.yml', '.yaml')))
    return wf[0] if wf else None


def m_byte(rel):
    def mutate(ctx, tree):
        r = rel(ctx) if callable(rel) else rel
        if r is None:
            return 'nothing to change'
        change_one_byte(at(tree, r))
        return 'changed %s' % r
    return mutate


def m_add(rel, data=b'added by a plant\n'):
    def mutate(ctx, tree):
        write(at(tree, rel), data)
    return mutate


def m_remove(rels):
    def mutate(ctx, tree):
        gone = []
        for r in (rels(ctx) if callable(rels) else rels):
            if os.path.isfile(at(tree, r)):
                os.remove(at(tree, r))
                gone.append(r)
        return 'removed %d file(s)' % len(gone)
    return mutate


def m_drop_line(rel, prefix):
    """The file without its one line that starts with prefix (a plant that cannot be applied raises)."""
    def mutate(ctx, tree):
        lines = read(at(tree, rel)).split(b'\n')
        hits = [i for i, x in enumerate(lines) if x.startswith(prefix)]
        if len(hits) != 1:
            raise ValueError('%d lines of %s start with %r' % (len(hits), rel, prefix))
        write(at(tree, rel), b'\n'.join(lines[:hits[0]] + lines[hits[0] + 1:]))
        return 'removed line %d of %s' % (hits[0] + 1, rel)
    return mutate


def m_rename(src, dst):
    def mutate(ctx, tree):
        os.rename(at(tree, src), at(tree, dst))
    return mutate


def workflows_of(ctx):
    return [r for r in ctx.files if r.startswith(WORKFLOWS + '/') and r.lower().endswith(('.yml', '.yaml'))]


def gate_files(ctx):
    return [r for r in ctx.files if r.startswith('kernel/coq/gate/')]


def m_link(ctx, tree):
    target = ctx.path('link-target')
    write(os.path.join(target, 'outside.py'), b'print("outside the judge")\n')
    link = at(tree, 'tools/ci/linked')
    make_link(target, link)
    ctx.links.append(link)


def m_link_folder(rel):
    """Move a judged folder out of the tree and put a link to it in its place (rel, or a function of ctx giving it)."""
    def mutate(ctx, tree):
        r = rel(ctx) if callable(rel) else rel
        moved = ctx.path('moved')
        shutil.move(at(tree, r), moved)
        make_link(os.path.abspath(moved), at(tree, r))
        ctx.links.append(at(tree, r))
        return '%s is now a link to a copy of itself' % r
    return mutate


def m_file_to_folder(rel):
    def mutate(ctx, tree):
        r = rel(ctx) if callable(rel) else rel
        os.remove(at(tree, r))
        write(os.path.join(at(tree, r), 'inside'), b'a file inside a folder\n')
    return mutate


def frozen_of(ctx):
    """The copy's kernel/coq/<folder>/FROZEN.txt paths, sorted by path."""
    return sorted(r for r in ctx.files if r.startswith(FROZEN_TOP + '/') and r.count('/') == 3
                  and r.endswith('/' + FROZEN_NAME))


def first_frozen(ctx):
    fz = frozen_of(ctx)
    if not fz:
        raise ValueError('the copy holds no %s/*/%s' % (FROZEN_TOP, FROZEN_NAME))
    return fz[0]


def first_frozen_folder(ctx):
    return first_frozen(ctx).rsplit('/', 1)[0]


def m_add_beside_first_frozen(name, data=b'added by a decoy\n'):
    """A file added at name inside the first FROZEN.txt's folder."""
    def mutate(ctx, tree):
        r = first_frozen_folder(ctx) + '/' + name
        write(at(tree, r), data)
        return 'added %s' % r
    return mutate


def m_fake_inventory(mode):
    def mutate(ctx, tree):
        write(at(tree, 'tools/ci/inventory.py'), (FAKE_INVENTORY % mode).encode('ascii'))
    return mutate


def inv_file(obj_or_bytes):
    def args(ctx, tree):
        p = ctx.path('inv') + '.json'
        write(p, obj_or_bytes if isinstance(obj_or_bytes, bytes) else dump(obj_or_bytes))
        return ['--inventory-json', p, '--expect', ctx.D or 'no-honest-digest']
    return args


def tampered_inventory():
    doc = inventory_doc()
    doc['gated'][0]['frozen4_sha256'] = sha(b'another list')
    return doc


def schema2_inventory():
    doc = inventory_doc()
    doc['schema'] = 'skuldd-inventory/2'
    return doc


def failed_inventory():
    return inventory_doc(verdict='INVENTORY FAILED: 1 of 9 rows failed')


def held_false_inventory():
    doc = inventory_doc()
    doc['held'] = False
    return doc


def duplicate_key_inventory():
    raw = dump(inventory_doc()).decode('ascii')
    return raw.replace('{\n', '{\n "digest": "%s",\n' % ('0' * 64), 1).encode('ascii')


def p15(ctx, predicted):
    tree = ctx.fresh()
    wrong = (ctx.D or '0' * 64)[:-1] + ('0' if (ctx.D or '1')[-1] != '0' else '1')
    res = run_judge(['--root', tree, '--inventory-json', ctx.inv, '--expect', wrong])
    ok, detail = outcome(res, predicted)
    want = CHANGED + (ctx.D or '')
    exact = res.rows.get('expected digest', ('', ''))[1] == want and res.digest == ctx.D
    return ok and exact, '%s; the message %s' % (detail, 'is exactly the header\'s, with the honest digest'
                                                  if exact else 'DIFFERS from the header\'s')


def expect_value(value):
    def args(ctx, tree):
        v = value(ctx) if callable(value) else value
        return ['--inventory-json', ctx.inv, '--expect', v]
    return args


def run_mode(ctx, tree):
    return []


def usage_json_at(rel):
    def case(ctx, predicted):
        tree = ctx.fresh()
        out = at(tree, rel)
        res = run_judge(['--root', tree, '--json', out] + ctx.std())
        ok, detail = outcome(res, predicted)
        written = os.path.exists(out)
        return ok and not written, '%s; %s %s' % (detail, rel, 'WRITTEN' if written else 'not written')
    return case


def usage_json_at_long(rel):
    """--json OUT at rel of a fresh tree, the path spelled with LONG before it: a usage error, OUT not written."""
    def case(ctx, predicted):
        tree = ctx.fresh()
        out = at(tree, rel)
        res = run_judge(['--root', tree, '--json', LONG + os.path.abspath(out)] + ctx.std())
        ok, detail = outcome(res, predicted)
        written = os.path.exists(out)
        return ok and not written, '%s; %s %s' % (detail, rel, 'WRITTEN' if written else 'not written')
    return case


def usage_json_at_volume(rel):
    """--json OUT at rel of a fresh tree, the path spelled as Windows' volume GUID path: a usage error, OUT not
    written."""
    def case(ctx, predicted):
        tree = ctx.fresh()
        out = at(tree, rel)
        given = volume_form(out)
        if given is None:
            return False, 'the drive of %s has no volume name; the case cannot be built' % out
        res = run_judge(['--root', tree, '--json', given] + ctx.std())
        ok, detail = outcome(res, predicted)
        written = os.path.exists(out)
        return ok and not written, '%s; %s %s' % (detail, rel, 'WRITTEN' if written else 'not written')
    return case


def usage_json_hard_link(rel):
    """--json L, L a new name (a hard link made beside the tree, outside it) of the judge file at rel of a fresh tree:
    a usage error, and the judge file's bytes unchanged."""
    def case(ctx, predicted):
        tree = ctx.fresh()
        target = at(tree, rel)
        before = read(target)
        link = tree + '-link.json'
        os.link(target, link)
        res = run_judge(['--root', tree, '--json', link] + ctx.std())
        ok, detail = outcome(res, predicted)
        same = read(target) == before
        return ok and same, '%s; %s %s' % (detail, rel, 'unchanged' if same else 'CHANGED through the link')
    return case


def usage_json_over(rel):
    """--json OUT at rel of a fresh tree (rel, or a function of ctx giving it), whether a file is there or not: a usage
    error, and the path as it was (its bytes, or its absence)."""
    def case(ctx, predicted):
        r = rel(ctx) if callable(rel) else rel
        tree = ctx.fresh()
        out = at(tree, r)
        before = read(out) if os.path.isfile(out) else None
        res = run_judge(['--root', tree, '--json', out] + ctx.std())
        ok, detail = outcome(res, predicted)
        after = read(out) if os.path.isfile(out) else None
        same = before == after
        return ok and same, '%s; %s %s' % (detail, r, 'as it was' if same else 'CHANGED')
    return case


def volume_form(p):
    """The absolute path p written as Windows' volume GUID path ("\\\\?\\Volume{GUID}\\" and the rest), which a
    long-path prefix taken off before resolving would leave relative; None when its drive has no volume name. On POSIX,
    which has no such form, p with a leading "//" (the case then runs that form)."""
    p = os.path.abspath(p)
    if os.name != 'nt':
        return '/' + p
    import ctypes
    drive = os.path.splitdrive(p)[0]
    buf = ctypes.create_unicode_buffer(100)
    if len(drive) != 2 or not ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW(drive + '\\', buf, 100):
        return None
    return buf.value + p[len(drive) + 1:]


def u03(ctx, predicted):
    tree = ctx.fresh()
    res = run_judge(['--root', at(tree, OUTSIDE)] + ctx.std())
    return outcome(res, predicted)


def u04(ctx, predicted):
    res = run_judge(ctx.std())
    return outcome(res, predicted)


def m01(ctx, predicted):
    """Run mode on a copy that holds what the inventory reads."""
    tree = ctx.fresh()
    for rel in INVENTORY_INPUTS:
        src = at(REPO, rel)
        if os.path.isfile(src):
            write(at(tree, rel), read(src))
        elif os.path.isdir(src):
            for r in walk_files(REPO, rel):
                if not os.path.exists(at(tree, r)):
                    write(at(tree, r), read(at(REPO, r)))
    if predicted != 'AGREES':
        return False, 'unknown predicted outcome %r' % predicted
    script = at(tree, 'tools/ci/inventory.py')
    judged = run_judge(['--root', tree])
    bad = shape(judged)
    if bad:
        return False, bad
    row = judged.rows.get('inventory digest', ('absent', ''))
    if not os.path.isfile(script):
        ok = row[0] == 'FAIL' and 'tools/ci/inventory.py' in row[1] and judged.code == 1
        return ok, 'this tree has no tools/ci/inventory.py: the inventory row is %s (%s)' % (row[0], row[1][:80])
    out = ctx.path('inv-run') + '.json'
    p = subprocess.run([sys.executable, '-B', script, '--root', tree, '--json', out], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=ENV, timeout=1800)
    if not os.path.isfile(out):
        ok = row[0] == 'FAIL'
        return ok, 'inventory.py exited %d and wrote no JSON; the judge\'s row is %s' % (p.returncode, row[0])
    given = run_judge(['--root', tree, '--inventory-json', out])
    grow = given.rows.get('inventory digest', ('absent', ''))
    want = 'ok' if p.returncode == 0 else 'FAIL'
    ok = row[0] == want and grow[0] == want and judged.digest == given.digest
    return ok, 'inventory.py exited %d; the inventory row is %s run, %s given its JSON; digests %s (%s)' % (
        p.returncode, row[0], grow[0], 'equal' if judged.digest == given.digest else 'DIFFER',
        (judged.digest or 'none')[:16])


CASES = [
    ('C01', c01), ('C02', c02), ('C03', c03), ('C04', c04), ('C05', c05),
    ('P01', plant(m_byte(first_workflow))),
    ('P02', plant(m_add(WORKFLOWS + '/extra.yaml', b'name: extra\non: push\n'))),
    ('P03', plant(m_add('tools/ci/extra.py'))),
    ('P04', plant(m_add('tools/ci/sub/extra.txt'))),
    ('P05', plant(m_rename('tools/ci/tests/test_judge_digest.py', 'tools/ci/tests/test_judge_digest2.py'))),
    ('P06', plant(m_byte('kernel/coq/gate/gate4.py'))),
    ('P07', plant(m_add('kernel/coq/gate/json.py', b'raise SystemExit(0)\n'))),
    ('P08', plant(m_byte('kernel/coq/EXPECTED-CI-LIBRARIES.txt'))),
    ('P09', plant(m_byte('kernel/hardening/features/feature_row4.py'))),
    ('P10', plant(m_byte('kernel/hardening/features/feature_row3.py'))),
    ('P11', plant(m_byte('tools/check_manifests.py'))),
    ('P12', plant(m_byte('ci/mathkernel/Dockerfile'))),
    ('P13', plant(m_add('ci/mathkernel/extra.sh'))),
    ('P14', plant(m_byte('.github/CODEOWNERS'))),
    ('P15', p15),
    ('P16', plant(lambda ctx, tree: None, expect_value(lambda ctx: (ctx.D or '').upper()), changed=False)),
    ('P17', plant(lambda ctx, tree: None, expect_value(''), changed=False)),
    ('P18', plant(m_remove(['.github/CODEOWNERS']))),
    ('P19', plant(m_remove(['kernel/coq/EXPECTED-CI-LIBRARIES.txt']))),
    ('P20', plant(m_remove(['kernel/hardening/features/feature_row4.py']))),
    ('P21', plant(m_remove(workflows_of))),
    ('P22', plant(m_remove(gate_files))),
    ('P23', plant(m_rename('.github/CODEOWNERS', '.github/codeowners'))),
    ('P24', plant(lambda ctx, tree: write(at(tree, 'tools/ci/judge_digest.py'),
                                          read(at(tree, 'tools/ci/judge_digest.py')) + b'#\n'))),
    ('P25', plant(lambda ctx, tree: None, inv_file(inventory_doc(b'another')))),
    ('P26', plant(lambda ctx, tree: None, inv_file(tampered_inventory()))),
    ('P27', plant(lambda ctx, tree: None,
                  lambda ctx, tree: ['--inventory-json', ctx.path('missing') + '.json', '--expect', ctx.D or 'x'])),
    ('P28', plant(lambda ctx, tree: None, inv_file(schema2_inventory()))),
    ('P29', plant(lambda ctx, tree: None, inv_file(b'not json\n'))),
    ('P30', plant(m_link)),
    ('P31', plant(m_fake_inventory('lies'), run_mode)),
    ('P32', plant(m_fake_inventory('failed'), run_mode)),
    ('P33', plant(m_remove(['tools/ci/inventory.py']), run_mode)),
    ('P34', plant(lambda ctx, tree: None, inv_file(failed_inventory()))),
    ('P35', plant(lambda ctx, tree: None, inv_file(duplicate_key_inventory()))),
    ('D01', plant(m_add('tools/ci/__pycache__/judge_digest.cpython-312.pyc', b'\x00not code\n'))),
    ('D02', plant(m_byte(OUTSIDE))),
    ('D03', plant(lambda ctx, tree: [os.utime(at(tree, r), (1000000000, 1000000000)) for r in ctx.files] and None)),
    ('D04', plant(m_add(WORKFLOWS + '/notes.txt'))),
    ('U01', usage_json_at('tools/ci/judge.json')),
    ('U02', usage_json_at(WORKFLOWS + '/judge.yml')),
    ('U03', u03),
    ('U04', u04),
    ('M01', m01),
    # the second round (PREDICTIONS-judge_digest-2.txt)
    ('Q01', plant(m_add('kernel/coq/gate/__pycache__/strict_read.cpython-312.pyc', b'\x00not code\n'))),
    ('Q02', plant(m_add('ci/mathkernel/__pycache__/extra.pyc', b'\x00not code\n'))),
    ('Q03', plant(m_link_folder('ci/mathkernel'))),
    ('Q04', plant(m_file_to_folder('.github/CODEOWNERS'))),
    ('Q05', plant(m_add(WORKFLOWS + '/extra.YML', b'name: extra\non: push\n'))),
    ('Q06', plant(lambda ctx, tree: None, expect_value(lambda ctx: (ctx.D or '') + ' '), changed=False)),
    ('Q07', usage_json_at('Tools/CI/judge.json')),
    # the third round (PREDICTIONS-judge_digest-3.txt)
    ('R01', plant(m_add('json.py', b'raise SystemExit(0)\n'))),
    ('R02', plant(m_add('.github/actions/local/action.yml', b'name: local\nruns:\n  using: composite\n  steps: []\n'))),
    ('R03', plant(m_byte('kernel/runtime/check_fpenv.py'))),
    ('R04', plant(m_remove(['kernel/runtime/test_fpenv.c']))),
    ('R05', plant(m_byte('kernel/coq/ANCHORS.md'))),
    ('R06', plant(m_remove(['kernel/coq/ANCHORS.md']))),
    ('R07', plant(lambda ctx, tree: None, inv_file(held_false_inventory()))),
    ('R08', plant(m_add('docs/extra.py'))),
    ('R09', plant(m_add('README.PY'))),
    ('U05', usage_json_at('judge.py')),
    # the fourth round (PREDICTIONS-judge_digest-4.txt)
    ('S01', plant(m_drop_line(ROW4_PREDICTIONS, b'| refuse4_context |'))),
    ('S02', plant(m_byte(ROW4_PLANTS + '/refuse4_context.v'))),
    ('S03', plant(m_remove([ROW4_PLANTS + '/decoy4_comment.v']))),
    ('S04', plant(m_remove([ROW4_PREDICTIONS]))),
    ('S05', plant(m_remove(lambda ctx: sorted(r for r in ctx.files if r.startswith(ROW4_PLANTS + '/'))))),
    ('S06', plant(m_byte('THEOREMS.md'))),
    ('S07', plant(m_remove(['THEOREMS.md']))),
    ('S08', plant(m_add(ROW4_PLANTS + '/refuse4_extra.v', b'Context (x : nat).\n'))),
    ('S09', plant(m_add('kernel/hardening/features/notes.txt'))),
    # the fifth round (PREDICTIONS-judge_digest-5.txt)
    ('T01', usage_json_at_long('tools/ci/out.json')),
    ('T02', usage_json_at('tools/ci/out.json')),
    # the sixth round (PREDICTIONS-judge_digest-6.txt)
    ('T03', usage_json_at_volume('tools/ci/out.json')),
    # the seventh round (PREDICTIONS-judge_digest-7.txt)
    ('T04', usage_json_hard_link('tools/ci/inventory.py')),
    # the eighth round (PREDICTIONS-judge_digest-8.txt): the group boundaries-frozen
    ('V01', plant(m_byte(MAP))),
    ('V02', plant(m_byte(first_frozen))),
    ('V03', plant(m_add(FROZEN_TOP + '/zz32/' + FROZEN_NAME, b'# FROZEN of zz32: added by a plant\n'))),
    ('V04', plant(m_remove([MAP]))),
    ('V05', plant(m_remove(frozen_of))),
    ('V06', plant(m_link_folder(first_frozen_folder))),
    ('V07', plant(m_file_to_folder(first_frozen))),
    ('V08', plant(m_add('kernel/records/floor32/extra.txt'))),
    ('V09', plant(m_add_beside_first_frozen('NOTES.md'))),
    ('V10', plant(m_add_beside_first_frozen('sub/' + FROZEN_NAME))),
    ('V11', usage_json_over(MAP)),
    ('V12', usage_json_over(first_frozen)),
    ('V13', usage_json_over('boundaries.md')),
]


def read_predictions():
    """({case id: predicted outcome}, problems), from every predictions file in order."""
    got, problems = {}, []
    for name in PREDICTIONS:
        try:
            text = read(os.path.join(HERE, name)).decode('utf-8')
        except (OSError, UnicodeDecodeError) as e:
            problems.append('%s cannot be read (%s)' % (name, type(e).__name__))
            continue
        for line in text.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split(' | ')
            if len(parts) != 3 or parts[0] in got:
                problems.append('%s: a line is not "ID | outcome | what" or repeats an ID: %s'
                                % (name, ascii(line[:60])))
                continue
            got[parts[0]] = parts[1]
    return got, problems


def remove_links(ctx):
    for link in ctx.links:
        try:
            if os.name == 'nt':
                os.rmdir(link)
            else:
                os.unlink(link)
        except OSError:
            pass


def onerror(func, path, _exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError:
        pass


def main():
    predicted, problems = read_predictions()
    files, notes = load_source()
    for n in notes:
        print(n)
    base = tempfile.mkdtemp(prefix='tjd-')
    ctx = Ctx(base, files)
    results = []
    try:
        for cid, fn in CASES:
            if cid not in predicted:
                results.append((cid, False, 'no prediction for this case'))
                continue
            try:
                ok, detail = fn(ctx, predicted[cid])
            except Exception as e:
                ok, detail = False, 'the case raised %s: %s' % (type(e).__name__, ascii(str(e))[:160])
            results.append((cid, ok, '%s: %s' % (predicted[cid], detail)))
    finally:
        remove_links(ctx)
        if sys.version_info >= (3, 12):
            shutil.rmtree(base, onexc=onerror)
        else:
            shutil.rmtree(base, onerror=onerror)
    known = set(c for c, _f in CASES)
    for cid in sorted(set(predicted) - known):
        results.append((cid, False, 'a prediction names no case'))
    for p in problems:
        results.append(('predictions', False, p))
    for cid, ok, detail in results:
        print('  %s %s  %s' % (cid.ljust(11), 'ok' if ok else 'FAIL', detail))
    failed = sum(1 for _c, ok, _d in results if not ok)
    if failed:
        print('TEST judge_digest FAILED: %d of %d cases failed' % (failed, len(results)))
        return 1
    print('TEST judge_digest HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
