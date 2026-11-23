# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_drift.py: tools/ci/drift.py held on an honest twin and seen to fail on each of its plants.
# Standard library only (Python 3.12 or later). It needs git (2.28 or later) on the PATH. It writes only in a temporary
# folder, which it removes, and starts git and Python only there (tools/ci/read_audit.py does not judge a process
# started in a run's temporary folder).
#
#   python3 -B tools/ci/tests/test_drift.py
#
# The fixture, built in the temporary folder with git's own configuration files switched off (no user, system or
# global setting can sign, convert or hook a commit): an origin repository whose main is c0, four branches one commit
# past it and a tag; then, per case, a Skuldd tree of its own. Cases, one line each, held to
# tools/ci/tests/PREDICTIONS-drift.txt (frozen before the first run): the exit code, the exact set of rows that fail,
# the verdict, a text the output must hold and a text it must not hold. The plants the drift guard is for: a changed
# origin file (H02), an added origin file (H03), a changed, an added and a removed Skuldd file (P01 to P03), a pin on
# a side branch (P11), a re-pin without its rows (P12). C05 and O02 write the two names with their diacritics.
# Two rows besides the cases:
#   predictions  every case defined here is predicted, and every prediction line parses
#   grammar      the classification grammar of tools/ci/drift.py and tools/check_manifests.py (row M4) is the same:
#                each of SECTION, HEADING, ROW, HEADER, SEPARATOR, RULING_ID and CLASSES, compared as pattern text
#                (each file is loaded as a module from its path; neither runs its main)
# What a pass shows: on this git and this Python, the script tells each planted drift from the honest twin, as
# predicted, and the two scripts read one grammar. What it does not show: GitHub's clone of the real originals, the
# real tree's rows (the drift workflow runs the script on them), or a fixture larger than a handful of files.
# Last line: "TEST drift HELD: n of n cases" (exit 0) or "TEST drift FAILED: k of n cases failed" (exit 1); exit 2
# on a usage error (this test takes no option).
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TOOL = os.path.join(ROOT, 'tools', 'ci', 'drift.py')
MANIFESTS_CHECK = os.path.join(ROOT, 'tools', 'check_manifests.py')
PRED = os.path.join(HERE, 'PREDICTIONS-drift.txt')
VERDICT = re.compile(r'DRIFT (HELD|ORIGIN AHEAD|FAILED)\b')
ROWLINE = re.compile(r'^  (D[1-6]) +(ok|FAIL) ')
C0 = {'a.txt': b'alpha\n', 'c.txt': b'gamma\n', 'dir/b.txt': b'beta\n',
      'kernel/attest/rec-HOSTX.json': b'{"host": 1}\n'}
REC = 'kernel/attest/rec-HOSTX.json'
EDITED = b'alpha edited\n'
SECTION = '## Drift classification (SY-2)\n\n| File | sha256 before | sha256 after | Class |\n|---|---|---|---|\n'
VERDANDI_D = 'Ver\u00f0andi'
ORLOG_D = '\u00d8rl\u01ebg'
GRAMMAR = ('SECTION', 'HEADING', 'ROW', 'HEADER', 'SEPARATOR', 'RULING_ID', 'CLASSES')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


class Fixture:
    def __init__(self, tmp):
        self.tmp = tmp
        self.noconfig = os.path.join(tmp, 'no-config')
        self.nohooks = os.path.join(tmp, 'no-hooks')
        wb(self.noconfig, b'')
        os.makedirs(self.nohooks)
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=self.noconfig, GIT_OPTIONAL_LOCKS='0',
                        GIT_TERMINAL_PROMPT='0', GIT_AUTHOR_NAME='test', GIT_AUTHOR_EMAIL='test@invalid',
                        GIT_COMMITTER_NAME='test', GIT_COMMITTER_EMAIL='test@invalid',
                        GIT_AUTHOR_DATE='2026-01-01T00:00:00Z', GIT_COMMITTER_DATE='2026-01-01T00:00:00Z',
                        GIT_CEILING_DIRECTORIES=os.path.dirname(tmp), PYTHONHASHSEED='0', PYTHONUTF8='1',
                        PYTHONDONTWRITEBYTECODE='1')
        for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
            self.env.pop(k, None)
        self.origin = os.path.join(tmp, 'origin')
        os.makedirs(self.origin)
        self.git('init', '-q', '-b', 'main')
        self.c0 = self.commit(C0, 'c0')
        self.git('tag', 'v1')
        self.side = self.branch('side', {'a.txt': b'alpha side\n'})
        self.ahead_changed = self.branch('ahead-changed', {'dir/b.txt': b'beta 2\n'})
        self.ahead_added = self.branch('ahead-added', {'new.txt': b'new\n'})
        self.repin = self.branch('repin', {'c.txt': b'gamma 2\n', 'd.txt': b'delta\n'})
        self.files = {}
        for name, commit in (('c0', self.c0), ('side', self.side), ('repin', self.repin)):
            out = self.git('ls-tree', '-r', '--name-only', '-z', commit).stdout
            self.files[name] = {p.decode(): self.git('cat-file', 'blob', '%s:%s' % (commit, p.decode())).stdout
                                for p in out.split(b'\0') if p}
        # a repository holding c0 (the same commit id) with a folder inside it: given that folder as --origin, the
        # script would read c0 there and pass, but for its refusal of a folder that is not a repository's top
        self.outer = os.path.join(tmp, 'outer')
        os.makedirs(os.path.join(self.outer, 'sub'))
        self.git('init', '-q', '-b', 'main', where=self.outer)
        for p, b in C0.items():
            wb(os.path.join(self.outer, *p.split('/')), b)
        self.git('add', '-A', where=self.outer)
        self.git('commit', '-q', '-m', 'c0', where=self.outer)
        if self.git('rev-parse', 'HEAD', where=self.outer).stdout.decode().strip() != self.c0:
            raise RuntimeError('the outer repository\'s commit is not c0')
        os.makedirs(os.path.join(tmp, 'plain'))
        os.makedirs(os.path.join(tmp, 'empty'))

    def git(self, *args, where=None):
        p = subprocess.run(['git', '-c', 'core.autocrlf=false', '-c', 'core.hooksPath=' + self.nohooks] + list(args),
                           cwd=where or self.origin, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise RuntimeError('git %s: %s' % (args[0], p.stderr.decode('utf-8', 'replace')[:200]))
        return p

    def commit(self, files, msg):
        for p, b in files.items():
            wb(os.path.join(self.origin, *p.split('/')), b)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', msg)
        return self.git('rev-parse', 'HEAD').stdout.decode().strip()

    def branch(self, name, files):
        self.git('checkout', '-q', '-b', name, self.c0)
        c = self.commit(files, name)
        self.git('checkout', '-q', 'main')
        return c

    def tree(self, commit):
        return self.git('rev-parse', commit + '^{tree}').stdout.decode().strip()

    def skuldd(self, cid, part='verdandi', base='c0', pin=None, tree=None, copy=None, manifest=None, notes='',
               changes=''):
        """A Skuldd tree for one case: copy (path: bytes or None to remove) laid over the base commit's files."""
        root = os.path.join(self.tmp, 'sk-' + cid)
        files = dict(self.files[base])
        for p, b in (copy or {}).items():
            if b is None:
                files.pop(p, None)
            else:
                files[p] = b
        for p, b in files.items():
            wb(os.path.join(root, part, *p.split('/')), b)
        man = {part + '/' + p: sha(b) for p, b in self.files['c0' if base == 'repin' else base].items()}
        man.update(manifest or {})
        wb(os.path.join(root, 'MANIFEST.%s.txt' % part),
           ''.join('%s  %s\n' % (h, p) for p, h in sorted(man.items())).encode())
        pin = pin or (self.side if base == 'side' else self.c0)
        tree = tree or self.tree(pin)
        wb(os.path.join(root, 'PROVENANCE.md'), (
            '# Provenance\n\n| Part | Source | Pinned at | Files | Manifest sha256 |\n|---|---|---|---|---|\n'
            '| `%s/` | the test origin | commit %s, tree %s | %d | none |\n\n%s' % (part, pin, tree, len(man), notes)
        ).encode())
        wb(os.path.join(root, 'CHANGES-AFTER-IMPORT.md'), ('# Changes after the import\n\n' + changes).encode())
        return root


def row(path, before, after, cls):
    return '| `%s` | %s | %s | %s |\n' % (path, before, after, cls)


def cases(fx):
    """{id: (args, ...)}: each case's arguments for drift.py."""
    v = lambda r, later='main', *more: ['--root', r, '--part', 'verdandi', '--origin', fx.origin, '--later', later] + \
        list(more)
    a0, ae = sha(C0['a.txt']), sha(EDITED)
    c01 = SECTION + row('verdandi/a.txt', a0, ae, 'SKULDD-ONLY BY RULING C2 (b)')
    repin_note = 'Re-pin 2026-11-21: `verdandi/` pinned at commit %s, tree %s. A test re-pin.\n' % (
        fx.repin, fx.tree(fx.repin))
    repin_rows = SECTION + row('verdandi/c.txt', sha(b'gamma\n'), sha(b'gamma 2\n'), 'RE-PIN ' + fx.repin) + \
        row('verdandi/d.txt', 'absent', sha(b'delta\n'), 'RE-PIN ' + fx.repin)
    bad_rows = repin_rows.replace('RE-PIN ' + fx.repin, 'RE-PIN ' + fx.ahead_changed)
    sk = fx.skuldd
    return {
        'H01': v(sk('H01')),
        'H02': v(sk('H02'), 'ahead-changed'),
        'H03': v(sk('H03'), 'ahead-added'),
        'H04': v(sk('H04'), 'ahead-added', '--show-paths'),
        'P01': v(sk('P01', copy={'a.txt': EDITED})),
        'P02': v(sk('P02', copy={'new-here.txt': b'here\n'})),
        'P03': v(sk('P03', copy={REC: None})),
        'C01': v(sk('C01', copy={'a.txt': EDITED}, changes=c01)),
        'C02': v(sk('C02', copy={REC: None}, changes=SECTION + row(
            'verdandi/kernel/attest/rec-<host>.json', sha(C0[REC]), 'removed', 'SKULDD-ONLY BY RULING C2 (b)'))),
        'C03': v(sk('C03', copy={'new-here.txt': b'here\n'}, changes=SECTION + row(
            'verdandi/new-here.txt', 'absent', sha(b'here\n'), 'SENT BACK Verdandi patch 0001-new-here.patch'))),
        'C05': v(sk('C05', copy={'new-here.txt': b'here\n'}, changes=SECTION + row(
            'verdandi/new-here.txt', 'absent', sha(b'here\n'), 'SENT BACK %s patch 0001-new-here.patch' % VERDANDI_D))),
        'P04': v(sk('P04', copy={'a.txt': EDITED}, changes=SECTION + row(
            'verdandi/a.txt', a0, sha(b'other\n'), 'SKULDD-ONLY BY RULING C2 (b)'))),
        'P05': v(sk('P05', copy={'a.txt': EDITED}, changes=c01 + row(
            'verdandi/a.txt', a0, sha(b'other\n'), 'SKULDD-ONLY BY RULING C2 (b)'))),
        'P06': v(sk('P06', changes=SECTION + row('verdandi/a.txt', a0, a0, 'SKULDD ONLY C2'))),
        'P07': v(sk('P07', changes=SECTION + row('verdandi/a.txt', a0, a0, 'SENT BACK Orlog pull request #3'))),
        'P08': v(sk('P08', manifest={'verdandi/a.txt': sha(b'x')})),
        'P09': v(sk('P09', pin='deadbeef' * 5, tree='ab' * 20)),
        'P10': v(sk('P10', tree='ab' * 20)),
        'P11': v(sk('P11', base='side')),
        'P12': v(sk('P12', base='repin', notes=repin_note), 'repin'),
        'C04': v(sk('C04', base='repin', notes=repin_note, changes=repin_rows), 'repin'),
        'P13': v(sk('P13', base='repin', notes=repin_note, changes=bad_rows), 'repin'),
        'P14': v(sk('P14', base='repin', notes=repin_note, changes=repin_rows, copy={'c.txt': b'gamma\n'}), 'repin'),
        'B01': v(sk('B01', copy={'a.txt': EDITED}, changes=c01), 'side'),
        'O01': ['--root', sk('O01', part='orlog', copy={'a.txt': EDITED}, changes=SECTION + row(
            'orlog/a.txt', a0, ae, 'SENT BACK Orlog pull request #12')), '--part', 'orlog', '--origin', fx.origin,
                '--later', 'main'],
        'O02': ['--root', sk('O02', part='orlog', copy={'a.txt': EDITED}, changes=SECTION + row(
            'orlog/a.txt', a0, ae, 'SENT BACK %s pull request #12' % ORLOG_D)), '--part', 'orlog', '--origin',
                fx.origin, '--later', 'main'],
        'U01': ['--help'],
        'U02': ['--roo', sk('U02'), '--part', 'verdandi', '--origin', fx.origin, '--later', 'main'],
        'U03': v(sk('U03'), 'HEAD'),
        'U04': v(sk('U04'), 'v1'),
        'U05': v(sk('U05'), fx.c0),
        'U06': v(sk('U06'), 'main', '--pinned', fx.c0),
        'U07': v(os.path.join(fx.tmp, 'empty')),
        'U08': ['--root', sk('U08'), '--part', 'verdandi', '--origin', os.path.join(fx.tmp, 'plain'), '--later',
                'main'],
        'U09': ['--root', sk('U09'), '--part', 'kernel', '--origin', fx.origin, '--later', 'main'],
        'U10': ['--root', sk('U10'), '--part', 'verdandi', '--origin', os.path.join(fx.outer, 'sub'), '--later',
                'main'],
    }


def predictions():
    preds, probs = {}, []
    with open(PRED, 'rb') as fh:
        for n, line in enumerate(fh.read().decode('utf-8').split('\n'), 1):
            if not line or line.startswith('#'):
                continue
            parts = line.split(' | ')
            if len(parts) != 7 or parts[0] in preds or parts[1] not in ('0', '1', '2', '3') or \
                    parts[3] not in ('HELD', 'ORIGIN AHEAD', 'FAILED', 'USAGE'):
                probs.append('line %d is not "id | exit | rows | verdict | must | must not | what"' % n)
                continue
            preds[parts[0]] = (int(parts[1]), set() if parts[2] == '-' else set(parts[2].split(',')), parts[3],
                               None if parts[4] == '-' else parts[4], None if parts[5] == '-' else parts[5])
    return preds, probs


def judge(pred, code, out):
    want_code, want_rows, want_verdict, must, must_not = pred
    failing = {m.group(1) for m in (ROWLINE.match(x) for x in out.split('\n')) if m and m.group(2) == 'FAIL'}
    verdicts = [m.group(1) for m in (VERDICT.match(x) for x in out.split('\n')) if m]
    got_verdict = 'USAGE' if not verdicts else verdicts[-1]
    bad = []
    if code != want_code:
        bad.append('exit %d, not %d' % (code, want_code))
    if failing != want_rows:
        bad.append('failing rows %s, not %s' % (','.join(sorted(failing)) or '-', ','.join(sorted(want_rows)) or '-'))
    if got_verdict != want_verdict or len(verdicts) > 1:
        bad.append('verdict %s (%d verdict lines), not %s' % (got_verdict, len(verdicts), want_verdict))
    if must and must not in out:
        bad.append('the output does not hold "%s"' % must)
    if must_not and must_not in out:
        bad.append('the output holds "%s"' % must_not)
    return bad


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pattern_text(value):
    """A grammar value as comparable text: a compiled pattern's source, a string, or a tuple of (name, pattern)."""
    if isinstance(value, re.Pattern):
        return value.pattern
    if isinstance(value, tuple):
        return tuple((k, pattern_text(rx)) for k, rx in value)
    return value


def grammar():
    """(ok, detail): the two scripts' classification grammars compared."""
    try:
        a, b = load('skuldd_drift', TOOL), load('skuldd_check_manifests', MANIFESTS_CHECK)
    except (OSError, SyntaxError, ImportError) as e:
        return False, 'a script could not be loaded (%s)' % type(e).__name__
    differ = [n for n in GRAMMAR if not hasattr(a, n) or not hasattr(b, n) or
              pattern_text(getattr(a, n)) != pattern_text(getattr(b, n))]
    if differ:
        return False, 'tools/ci/drift.py and tools/check_manifests.py differ in %s' % ', '.join(differ)
    return True, '%d names, each the same in both scripts' % len(GRAMMAR)


def main(argv):
    if argv:
        sys.stderr.write('test_drift.py: usage error: this test takes no option\n')
        return 2
    preds, probs = predictions()
    tmp = tempfile.mkdtemp(prefix='test-drift-')
    results = []
    try:
        fx = Fixture(tmp)
        defined = cases(fx)
        same = set(defined) == set(preds)
        results.append(('predictions', not probs and same, '; '.join(probs) if probs else
                        '%d cases, each predicted' % len(defined) if same else
                        'the cases defined here and the predicted ones differ'))
        results.append(('grammar',) + grammar())
        for cid in sorted(defined):
            if cid not in preds:
                continue
            p = subprocess.run([sys.executable, '-B', TOOL] + defined[cid], cwd=tmp, env=fx.env,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
            out = (p.stdout + b'\n' + p.stderr).decode('utf-8', 'replace').replace('\r', '')
            bad = judge(preds[cid], p.returncode, out)
            results.append((cid, not bad, '; '.join(bad) if bad else 'exit %d as predicted' % p.returncode))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for cid, ok, detail in results:
        print('  %-12s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    k = sum(1 for r in results if not r[1])
    if k:
        print('TEST drift FAILED: %d of %d cases failed' % (k, len(results)))
        return 1
    print('TEST drift HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
