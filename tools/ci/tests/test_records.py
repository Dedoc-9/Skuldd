# SPDX-License-Identifier: AGPL-3.0-only
# The test of tools/ci/run_record.py and tools/ci/verify_records.py. Standard library only (Python 3.12 or later); it
# needs git on the PATH.
#
#   python3 -B tools/ci/tests/test_records.py
#
# In a temporary folder outside the tree it builds a git repository holding copies of this tree's
# .github/workflows/mathkernel-linux.yml, kernel/coq/gate/gate4.py and every gated folder's gate.json and FROZEN4.txt
# (git's own configuration of the machine left out, so the run is the same everywhere), and inputs in the form the
# other scripts write them: for each folder a gate log in gate4.py's form and the log check's JSON, then the
# toolchain check's, the inventory's and the CI judge's JSON. It sets the GITHUB_ values itself; any in its own
# environment are dropped. It runs the two scripts as subprocesses, on the honest twins and on each plant, and git,
# each started in that temporary folder (git is a program that is not Python, which tools/ci/read_audit.py refuses
# to see started outside a new temporary folder; run_record.py starts git in the folder it was started in). A case
# passes only when the script exits as tools/ci/tests/PREDICTIONS-records.txt and its addenda
# (PREDICTIONS-records-addendum<n>.txt, each written before its own first run) say, and the rows that FAIL are exactly
# the rows they name; for the honest twins, also when the record and the summary hold the values this test computes
# itself (git's ids by its own git calls, every sha256 by its own hashing). Every predicted case must run, and every
# case run must be predicted. One more case, "gate log rows", holds three counts to one number: the rows
# tools/ci/check_gate_log.py prints (run on an empty log against this tree), verify_records.py's GATE_LOG_ROWS (the
# count it requires of every log check verdict) and this test's CHECK_ROWS (the count of the log checks it writes).
# What a pass shows: the two scripts hold on honest inputs and turn red, on the named rows, on every plant listed.
# What it does not show: that the other scripts write the JSON this test writes (their tests and the CI run show that);
# anything about GitHub's runners beyond the environment values set here; a plant not listed.
# Last line: "TEST records HELD: n of n cases" (exit 0) or "TEST records FAILED: k of n cases failed" (exit 1).
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RUN_RECORD = os.path.join(ROOT, 'tools', 'ci', 'run_record.py')
VERIFY = os.path.join(ROOT, 'tools', 'ci', 'verify_records.py')
CHECK_GATE_LOG = os.path.join(ROOT, 'tools', 'ci', 'check_gate_log.py')
PREDICTIONS = os.path.join(HERE, 'PREDICTIONS-records.txt')
WORKFLOW = '.github/workflows/mathkernel-linux.yml'
GATE4 = 'kernel/coq/gate/gate4.py'
IMAGE = 'sha256:b058dd7c3e52381007f54f13adbb7931baaf214d0435cad192da8d353963a51a'
BASE = 'docker.io/library/ubuntu:24.04@sha256:73b999393d07f2bf65a40373778a44dc9a6d54ad7718d29247d8ff9413c4d6a8'
# V44's path prefix: a long-path prefix on Windows; a leading "//" on POSIX, which has none
LONG = '\\\\?\\' if os.name == 'nt' else '/'
# the folder every process this test starts is started in: its temporary folder, set by main()
WORK = []
REPO = 'owner/repository'
REF = 'refs/heads/main'
WREF = '%s/%s@%s' % (REPO, WORKFLOW, REF)
RUN_ID = '1000000001'
STAMP = '2026-11-18T02:36:44.1360963Z '
CHECK_ROWS = 15  # the rows tools/ci/check_gate_log.py prints; the case "gate log rows" holds the two scripts to it
CHECK_VERDICT = 'GATE LOG HELD: %d of %d rows' % (CHECK_ROWS, CHECK_ROWS)
WIDTH = 58  # the scripts print '  %-58s %s  %s'
ARGS = ('folder', 'anchor', 'root', 'gate_log', 'gate_check_json', 'toolchain_json', 'inventory_json', 'judge_json',
        'image_id', 'base_image', 'out')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True) + '\n').encode('ascii')


def read(path):
    with open(path, 'rb') as fh:
        return fh.read()


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def remove_tree(path):
    """Remove a folder, git's read-only object files included."""
    for dp, dn, fn in os.walk(path):
        for name in dn + fn:
            try:
                os.chmod(os.path.join(dp, name), stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)


def predictions():
    """({label: row name}, {case id: (script, exit code, [row names])}) from PREDICTIONS-records.txt, then from each
    PREDICTIONS-records-addendum<n>.txt beside it (cases only; their labels are the first file's)."""
    rows, cases = {}, {}
    addenda = sorted((f for f in os.listdir(HERE) if re.fullmatch(r'PREDICTIONS-records-addendum\d+\.txt', f)),
                     key=lambda f: int(re.sub(r'\D', '', f)))
    text = read(PREDICTIONS).decode('utf-8')
    for f in addenda:
        text += '\n' + read(os.path.join(HERE, f)).decode('utf-8')
    for line in text.split('\n'):
        m = re.fullmatch(r'row ([RV]R\d\d) (.+)', line)
        if m:
            if m.group(1) in rows:
                raise ValueError('row %s is named twice' % m.group(1))
            rows[m.group(1)] = m.group(2)
            continue
        m = re.fullmatch(r'case ([HRV]\d\d) (run_record|verify_records) exit ([012]) '
                         r'fails (-|[RV]R\d\d(?:,[RV]R\d\d)*)', line)
        if m:
            if m.group(1) in cases:
                raise ValueError('case %s is predicted twice' % m.group(1))
            labels = [] if m.group(4) == '-' else m.group(4).split(',')
            cases[m.group(1)] = (m.group(2), int(m.group(3)), sorted(rows[x] for x in labels))
        elif line.startswith('case ') or line.startswith('row '):
            raise ValueError('a line of the predictions is not read: %r' % line[:80])
    return rows, cases


class Fixture:
    """The temporary checkout and the honest inputs."""

    def __init__(self, tmp):
        self.tmp = tmp
        self.gitcfg = os.path.join(tmp, 'empty-gitconfig')
        write(self.gitcfg, b'')
        coq = os.path.join(ROOT, 'kernel', 'coq')
        self.folders = sorted(f for f in os.listdir(coq) if os.path.isfile(os.path.join(coq, f, 'gate.json')))
        if len(self.folders) < 2:
            raise RuntimeError('fewer than two gated folders under kernel/coq')
        self.F = 'f32' if 'f32' in self.folders else self.folders[0]
        self.G = 'p32' if 'p32' in self.folders and self.F != 'p32' else [f for f in self.folders if f != self.F][0]
        self.repo = os.path.join(tmp, 'repo')
        paths = [WORKFLOW, GATE4] + ['kernel/coq/%s/%s' % (f, n) for f in self.folders
                                     for n in ('gate.json', 'FROZEN4.txt')]
        for p in paths:
            write(os.path.join(self.repo, *p.split('/')), read(os.path.join(ROOT, *p.split('/'))))
        self.git('-c', 'init.defaultBranch=main', 'init', '-q')
        self.git('config', 'core.autocrlf', 'false')
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'fixture')
        self.head = self.git('rev-parse', 'HEAD')
        self.tree = self.git('rev-parse', 'HEAD^{tree}')
        self.kernel_tree = self.git('rev-parse', 'HEAD:kernel/coq')
        self.workflow_blob = self.git('rev-parse', 'HEAD:' + WORKFLOW)
        self.workflow_sha = sha(read(os.path.join(ROOT, *WORKFLOW.split('/'))))
        self.gate4_sha = sha(read(os.path.join(ROOT, *GATE4.split('/'))))
        self.frozen, self.name, self.files = {}, {}, {}
        for f in self.folders:
            self.frozen[f] = sha(read(os.path.join(coq, f, 'FROZEN4.txt')))
            cfg = json.loads(read(os.path.join(coq, f, 'gate.json')).decode('utf-8'))
            self.name[f], self.files[f] = cfg['name'], list(cfg['files'])
        self.inp = os.path.join(tmp, 'in')
        self.log, self.check, self.map_digest, self.vline = {}, {}, {}, {}
        for f in self.folders:
            data = self.gate_log(f)
            self.log[f] = self.put('%s/gate.log' % f, data)
            self.vline[f] = data.decode('ascii').rstrip('\n').split('\n')[-1]
            self.map_digest[f] = sha(('Coq.Init.Logic %s\n' % ('ab' * 32)).encode('ascii'))
            self.check[f] = self.put('%s/gate-check.json' % f, json_bytes(self.check_obj(f, data)))
        self.toolchain_digest = sha(b'coq-version The Coq Proof Assistant, version 8.20.1\n')
        self.toolchain = self.put('toolchain.json', json_bytes(self.toolchain_obj()))
        inv = self.inventory_obj(self.frozen)
        self.inv_digest = inv['digest']
        self.inventory = self.put('inventory.json', json_bytes(inv))
        judge = self.judge_obj(self.inv_digest)
        self.judge_digest = judge['digest']
        self.judge = self.put('judge.json', json_bytes(judge))

    def git(self, *args, cwd=None):
        env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'GITHUB_'))}
        env.update(GIT_CONFIG_GLOBAL=self.gitcfg, GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='records-test',
                   GIT_AUTHOR_EMAIL='records-test', GIT_COMMITTER_NAME='records-test',
                   GIT_COMMITTER_EMAIL='records-test', GIT_AUTHOR_DATE='2026-11-18T00:00:00Z',
                   GIT_COMMITTER_DATE='2026-11-18T00:00:00Z', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
        p = subprocess.run(['git', '-C', cwd or self.repo] + list(args), stdin=subprocess.DEVNULL,
                           capture_output=True, env=env, timeout=300, cwd=self.tmp)
        if p.returncode != 0:
            raise RuntimeError('git %s: %s' % (args[0], p.stderr.decode('utf-8', 'replace').strip()[:200]))
        return p.stdout.decode('utf-8', 'replace').strip()

    def put(self, rel, data):
        path = os.path.join(self.inp, *rel.split('/'))
        write(path, data)
        return path

    def gate_log(self, f, gate4_sha=None):
        """A gate log in gate4.py's form (its header, anchor, row and verdict lines)."""
        a16 = self.frozen[f][:16]
        lines = [
            'gate4.py %s judges %s (identity %s.Identity; sources of %s) in /work  --recheck'
            % (gate4_sha or self.gate4_sha, f, f, f),
            'anchor %s' % self.frozen[f],
            '  %-62s %s  %s' % ('freeze list: every line is readable', 'ok', '12 entries'),
            '  %-62s %s  %s' % ('freeze list is the anchored one', 'ok', 'ANCHOR %s' % a16),
            '  %-62s %s  %s' % ('identity: Print Assumptions is exactly the flocq4 list', 'ok', '4 axioms'),
            '  checked in this run: Coq.Init.Logic %s exit 0 clean' % ('ab' * 32),
            '  closure: every outside library passed coqchk -norec, unsafe <none> ok  1 libraries by the sha256 '
            'of their files: 0 from the log, 1 checked in this run',
            '%s GATE4 HELD: 20 of 20  [anchor %s]' % (self.name[f], a16),
        ]
        return ('\n'.join(lines) + '\n').encode('ascii')

    def check_obj(self, f, log_bytes, **over):
        lines = [x for x in log_bytes.decode('ascii').split('\n') if x.strip()]
        last = lines[-1][len(STAMP):] if lines[-1].startswith(STAMP) else lines[-1]
        obj = {'schema': 'skuldd-gate-log-check/1', 'folder': f, 'anchor': self.frozen[f], 'name': self.name[f],
               'gate_log_sha256': sha(log_bytes), 'gate_verdict_line': last, 'gate_rows': 20, 'library_count': 1,
               'library_map_digest': self.map_digest[f], 'libraries': {'Coq.Init.Logic': 'ab' * 32},
               'differences': [], 'rows': [], 'verdict': CHECK_VERDICT, 'held': True}
        obj.update(over)
        return obj

    def toolchain_obj(self, **over):
        obj = {'schema': 'skuldd-toolchain/1', 'held': True, 'verdict': 'TOOLCHAIN HELD: 5 of 5 rows', 'rows': [],
               'digest': self.toolchain_digest, 'compared': [], 'records': [],
               'observed_sha256': sha(b'observed'), 'expected_sha256': sha(b'expected')}
        obj.update(over)
        return obj

    def inventory_obj(self, frozen, **over):
        gated = [{'folder': f, 'files': self.files[f], 'plants': [], 'frozen4_sha256': frozen[f],
                  'identity_names': {'statements': [], 'theorems': []}} for f in sorted(frozen)]
        obj = {'gated': gated, 'mirrors': [], 'gate_dir_files': ['expected-pa-flocq4.txt', 'freeze4.py', 'gate4.py',
                                                                 'strict_read.py']}
        obj['digest'] = sha(canonical(obj))
        obj.update(schema='skuldd-inventory/1', held=True, rows=[], verdict='INVENTORY HELD: 40 of 40 rows')
        obj.update(over)
        return obj

    def judge_obj(self, inv_digest, files=None, **over):
        files = files or [(WORKFLOW, self.workflow_sha), (GATE4, self.gate4_sha)]
        h = hashlib.sha256()
        for p, s in sorted(files, key=lambda x: x[0].encode('utf-8')):
            h.update(('%s  %s\n' % (s, p)).encode('utf-8'))
        h.update(('inventory %s\n' % inv_digest).encode('ascii'))
        d = h.hexdigest()
        obj = {'schema': 'skuldd-ci-judge/1', 'digest': d, 'inventory_digest': inv_digest,
               'inventory_source': 'inventory-json', 'expect': d,
               'files': [{'path': p, 'sha256': s, 'group': 'g'} for p, s in files], 'groups': [], 'rows': [],
               'verdict': 'CI JUDGE HELD: 12 of 12 rows', 'held': True}
        obj.update(over)
        return obj

    def env(self, **over):
        env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'GITHUB_'))}
        env.update(PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1', GIT_CONFIG_GLOBAL=self.gitcfg,
                   GIT_CONFIG_NOSYSTEM='1', GITHUB_SHA=self.head, GITHUB_RUN_ID=RUN_ID, GITHUB_RUN_ATTEMPT='1',
                   GITHUB_REPOSITORY=REPO, GITHUB_REF=REF, GITHUB_WORKFLOW_REF=WREF)
        for k, val in over.items():
            if val is None:
                env.pop(k, None)
            else:
                env[k] = val
        return env

    def rr_args(self, f, out, **over):
        d = dict(folder=f, anchor=self.frozen[f], root=self.repo, gate_log=self.log[f],
                 gate_check_json=self.check[f], toolchain_json=self.toolchain, inventory_json=self.inventory,
                 judge_json=self.judge, image_id=IMAGE, base_image=BASE, out=out)
        d.update(over)
        args = []
        for k in ARGS:
            if d[k] is not None:
                args += ['--' + k.replace('_', '-'), d[k]]
        return args

    def vr_args(self, folder, out=None, **over):
        d = dict(dir=folder, inventory_json=self.inventory, judge_json=self.judge, toolchain_json=self.toolchain)
        d.update(over)
        args = []
        for k in ('dir', 'inventory_json', 'judge_json', 'toolchain_json'):
            args += ['--' + k.replace('_', '-'), d[k]]
        return args + (['--out', out] if out else [])

    def expected_record(self, f, log_bytes):
        lines = [x for x in log_bytes.decode('ascii').split('\n') if x.strip()]
        last = lines[-1][len(STAMP):] if lines[-1].startswith(STAMP) else lines[-1]
        return {'schema': 'skuldd-mathkernel-run-record/1', 'commit': self.head, 'tree': self.tree,
                'kernel_tree': self.kernel_tree, 'workflow_blob': self.workflow_blob,
                'workflow_sha256': self.workflow_sha, 'run_id': RUN_ID, 'run_attempt': '1', 'repository': REPO,
                'ref': REF, 'workflow_ref': WREF, 'folder': f, 'anchor': self.frozen[f],
                'frozen4_sha256': self.frozen[f], 'image_id': IMAGE, 'base_image': BASE,
                'toolchain_digest': self.toolchain_digest, 'library_map_digest': self.map_digest[f],
                'inventory_digest': self.inv_digest, 'judge_digest': self.judge_digest,
                'gate_log_sha256': sha(log_bytes), 'gate_verdict_line': last, 'gate_check_verdict': CHECK_VERDICT}


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


def run(script, args, env):
    p = subprocess.run([sys.executable, '-B', script] + args, stdin=subprocess.DEVNULL, capture_output=True,
                       env=env, timeout=900, cwd=WORK[0] if WORK else None)
    return p.returncode, p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')


def judge_output(script, code, out, want, row_names):
    """What differs from the prediction (script, exit code, failing row names): a list, empty when nothing does."""
    tool, want_code, want_fail = want
    bad = []
    if tool != script:
        bad.append('the prediction is for %s' % tool)
    if code != want_code:
        bad.append('exit %d, predicted %d' % (code, want_code))
    lines = [x for x in out.split('\n') if x != '']
    if want_code == 2:
        if any(re.match(r'RUN RECORDS? (HELD|FAILED)', x) for x in lines):
            bad.append('a verdict line on a usage error')
        return bad
    rows, other = [], []
    for x in lines[:-1]:
        st = x[WIDTH + 3:]
        if x.startswith('  ') and x[WIDTH + 2:WIDTH + 3] == ' ' and (st.startswith('ok') or st.startswith('FAIL')):
            rows.append((x[2:WIDTH + 2].rstrip(), st.startswith('ok')))
        else:
            other.append(x)
    unknown = [n for n, _ in rows if n not in row_names]
    failing = sorted(n for n, ok in rows if not ok)
    if other or unknown:
        bad.append('lines that are not known rows: %r' % (other + unknown)[:2])
    if failing != want_fail:
        bad.append('failing rows %s, predicted %s' % (failing or '-', want_fail or '-'))
    n, k = len(rows), len(failing)
    name = 'RUN RECORD' if script == 'run_record' else 'RUN RECORDS'
    verdict = '%s FAILED: %d of %d rows failed' % (name, k, n) if k else '%s HELD: %d of %d rows' % (name, n, n)
    if not lines or lines[-1] != verdict:
        bad.append('last line %r, not %r' % (lines[-1][:80] if lines else '', verdict))
    return bad


def gate_log_rows(fx):
    """The case "gate log rows": verify_records.py's GATE_LOG_ROWS, this test's CHECK_ROWS and the number of rows
    tools/ci/check_gate_log.py prints (run on an empty log against this tree) are one number."""
    spec = importlib.util.spec_from_file_location('verify_records_under_test', VERIFY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    empty = fx.put('gate-log-rows/empty.log', b'')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'GITHUB_'))}
    p = subprocess.run([sys.executable, '-B', CHECK_GATE_LOG, '--log', empty, '--folder', fx.F, '--anchor', '0' * 64,
                        '--root', ROOT, '--expected-libs', os.path.join(ROOT, 'kernel', 'coq',
                                                                        'EXPECTED-CI-LIBRARIES.txt')],
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=300)
    found = re.findall(r'(?m)^GATE LOG (?:HELD: \d+ of (\d+) rows|FAILED: \d+ of (\d+) rows failed)\r?$',
                       p.stdout.decode('utf-8', 'replace'))
    printed = int(found[-1][0] or found[-1][1]) if len(found) == 1 else None
    want = getattr(mod, 'GATE_LOG_ROWS', None)
    ok = printed is not None and printed == want == CHECK_ROWS
    return ('gate log rows', ok, 'check_gate_log.py prints %s rows; verify_records.GATE_LOG_ROWS is %s; the fixture '
            'counts %d' % (printed, want, CHECK_ROWS))


def edit_record(path, **changes):
    obj = json.loads(read(path).decode('utf-8'))
    obj.update(changes)
    write(path, json_bytes(obj))


def main():
    row_table, cases = predictions()
    row_names = set(row_table.values())
    tmp = tempfile.mkdtemp(prefix='test-records-')
    WORK[:] = [tmp]
    results = []  # (case id, ok, detail)
    try:
        fx = Fixture(tmp)
        F, G = fx.F, fx.G
        outs = os.path.join(tmp, 'out')
        os.makedirs(outs)

        def case(cid, script, args, env, extra=None):
            """Run one case; extra(code) returns more problems (validity checks beyond the rows)."""
            if cid not in cases:
                results.append((cid, False, 'no prediction for this case'))
                return
            path = RUN_RECORD if script == 'run_record' else VERIFY
            try:
                code, out = run(path, args, env)
                bad = judge_output(script, code, out, cases[cid], row_names)
                if extra is not None:
                    bad += extra(code)
            except Exception as e:  # a case that cannot run fails
                bad = ['error: %s: %s' % (type(e).__name__, str(e)[:200])]
            results.append((cid, not bad, '; '.join(bad) if bad else 'as predicted'))

        def rr(cid, f=None, env=None, **over):
            over.setdefault('out', os.path.join(outs, cid + '.json'))

            def no_record(code):
                return ['a record was written'] if code != 0 and os.path.lexists(over['out']) else []
            case(cid, 'run_record', fx.rr_args(f or F, **over), env or fx.env(), no_record)

        def vr(cid, folder, out=None, env=None, extra=None, **over):
            case(cid, 'verify_records', fx.vr_args(folder, out, **over), env or fx.env(), extra)

        # Honest twins.
        h01 = os.path.join(outs, 'H01.json')

        def check_h01(code):
            if code != 0 or not os.path.isfile(h01):
                return ['no record']
            want = json_bytes(fx.expected_record(F, read(fx.log[F])))
            return [] if read(h01) == want else ['the record is not the values computed here: %s' % read(h01)[:200]]
        case('H01', 'run_record', fx.rr_args(F, h01), fx.env(), check_h01)
        h02 = os.path.join(outs, 'H02.json')
        case('H02', 'run_record', fx.rr_args(F, h02), fx.env(),
             lambda code: [] if os.path.isfile(h02) and os.path.isfile(h01) and read(h02) == read(h01)
             else ['not the same bytes as H01'])
        stamped = b''.join(STAMP.encode('ascii') + x + b'\n' for x in read(fx.log[F]).rstrip(b'\n').split(b'\n'))
        log_h03 = fx.put('H03/gate.log', stamped)
        check_h03 = fx.put('H03/gate-check.json', json_bytes(fx.check_obj(F, stamped)))
        h03 = os.path.join(outs, 'H03.json')

        def check_h03_record(code):
            if code != 0 or not os.path.isfile(h03):
                return ['no record']
            want = json_bytes(fx.expected_record(F, stamped))
            return [] if read(h03) == want else ['the record is not the values computed here']
        case('H03', 'run_record', fx.rr_args(F, h03, gate_log=log_h03, gate_check_json=check_h03), fx.env(),
             check_h03_record)

        recs = os.path.join(tmp, 'records')
        made = []
        for f in fx.folders:
            p = os.path.join(recs, 'run-record-%s' % f, 'run-record.json')
            os.makedirs(os.path.dirname(p))
            code, out = run(RUN_RECORD, fx.rr_args(f, p), fx.env())
            if code != 0 or not os.path.isfile(p) or read(p) != json_bytes(fx.expected_record(f, read(fx.log[f]))):
                made.append(f)
        summary = os.path.join(tmp, 'H04-summary.json')

        def check_h04(code):
            bad = ['run_record.py did not make the honest record of %s' % ', '.join(made)] if made else []
            if not os.path.isfile(summary):
                return bad + ['no summary']
            s = json.loads(read(summary).decode('utf-8'))
            n = len([r for r in row_table if r.startswith('VR')])
            want_records = [{'file': 'run-record-%s/run-record.json' % f, 'folder': f, 'anchor': fx.frozen[f],
                             'gate_verdict_line': fx.vline[f], 'gate_check_verdict': CHECK_VERDICT}
                            for f in fx.folders]
            if s.get('schema') != 'skuldd-mathkernel-run-summary/1':
                bad.append('summary schema %r' % s.get('schema'))
            if s.get('verdict') != 'RUN RECORDS HELD: %d of %d rows' % (n, n):
                bad.append('summary verdict %r' % s.get('verdict'))
            if s.get('records') != want_records:
                bad.append('summary records are not every folder\'s')
            if s.get('not_records') != []:
                bad.append('summary lists files that are not records')
            shared = s.get('shared') or {}
            if shared.get('commit') != fx.head or shared.get('judge_digest') != fx.judge_digest:
                bad.append('summary shared values are not the run\'s')
            if s.get('inputs') != {'inventory_digest': fx.inv_digest, 'judge_digest': fx.judge_digest,
                                   'toolchain_digest': fx.toolchain_digest}:
                bad.append('summary inputs are not the JSON files\'')
            if read(summary) != json_bytes(s):
                bad.append('summary keys are not sorted as written here')
            return bad
        vr('H04', recs, out=summary, extra=check_h04)
        flat = os.path.join(tmp, 'flat')
        os.makedirs(flat)
        for f in fx.folders:
            shutil.copyfile(os.path.join(recs, 'run-record-%s' % f, 'run-record.json'),
                            os.path.join(flat, 'run-record-%s.json' % f))
        vr('H05', flat)

        # Plants on run_record.py.
        rr('R01', env=fx.env(GITHUB_SHA='0' * 40))
        check_r02 = fx.put('R02/gate-check.json', json_bytes(fx.check_obj(F, read(fx.log[F]), anchor=fx.frozen[G])))
        rr('R02', anchor=fx.frozen[G], gate_check_json=check_r02)
        rr('R03', env=fx.env(GITHUB_RUN_ID=None))
        rr('R04', env=fx.env(GITHUB_WORKFLOW_REF='%s/.github/workflows/integrity.yml@%s' % (REPO, REF)))
        r05 = os.path.join(tmp, 'r05')
        shutil.copytree(fx.repo, r05)
        with open(os.path.join(r05, 'kernel', 'coq', G, 'gate.json'), 'ab') as fh:
            fh.write(b' ')
        rr('R05', root=r05)
        r06 = os.path.join(tmp, 'r06')
        shutil.copytree(fx.repo, r06)
        inner = os.path.join(r06, 'inner')
        for p in [WORKFLOW, GATE4] + ['kernel/coq/%s/%s' % (f, n) for f in fx.folders
                                     for n in ('gate.json', 'FROZEN4.txt')]:
            write(os.path.join(inner, *p.split('/')), read(os.path.join(fx.repo, *p.split('/'))))
        rr('R06', root=inner)
        for cid, data in (('R07', read(fx.log[F]) + fx.vline[F].encode('ascii') + b'\n'),
                          ('R08', read(fx.log[F]) + b'a line after the verdict\n'),
                          ('R09', read(fx.log[G])),
                          ('R10', fx.gate_log(F, gate4_sha='0' * 64))):
            log = fx.put('%s/gate.log' % cid, data)
            chk = fx.put('%s/gate-check.json' % cid, json_bytes(fx.check_obj(F, data)))
            rr(cid, gate_log=log, gate_check_json=chk)
        without = dict((f, h) for f, h in fx.frozen.items() if f != F)
        inv11 = fx.inventory_obj(without)
        rr('R11', inventory_json=fx.put('R11/inventory.json', json_bytes(inv11)),
           judge_json=fx.put('R11/judge.json', json_bytes(fx.judge_obj(inv11['digest']))))
        inv12 = fx.inventory_obj(fx.frozen)
        inv12['gated'] = [dict(g, frozen4_sha256='0' * 64) if g['folder'] == G else g for g in inv12['gated']]
        rr('R12', inventory_json=fx.put('R12/inventory.json', json_bytes(inv12)))
        rr('R13', gate_check_json=os.path.join(tmp, 'in', 'R13-absent.json'))
        rr('R14', gate_check_json=fx.check[G])
        dup = read(fx.check[F]).replace(b'{\n', b'{\n "verdict": "%s",\n' % CHECK_VERDICT.encode('ascii'), 1)
        rr('R15', gate_check_json=fx.put('R15/gate-check.json', dup))
        rr('R16', image_id=IMAGE[len('sha256:'):])
        rr('R17', base_image='docker.io/library/ubuntu:24.04')
        rr('R18', judge_json=fx.put('R18/judge.json', json_bytes(fx.judge_obj(fx.inv_digest, expect=None))))
        rr('R19', toolchain_json=fx.put('R19/toolchain.json', json_bytes(fx.toolchain_obj(
            held=False, verdict='TOOLCHAIN FAILED: 1 of 5 rows failed'))))
        r20 = os.path.join(outs, 'R20-existing.json')
        write(r20, b'kept\n')
        case('R20', 'run_record', fx.rr_args(F, r20), fx.env(),
             lambda code: [] if read(r20) == b'kept\n' else ['the existing file was changed'])
        rr('R21', image_id=None)
        rr('R22', inventory_json=fx.put('R22/inventory.json', json_bytes(fx.inventory_obj(
            fx.frozen, held=False, verdict='INVENTORY FAILED: 1 of 40 rows failed'))))

        # Addendum 1: an honest twin and plants on run_record.py.
        h06 = os.path.join(outs, 'H06.json')

        def check_h06(code):
            want = fx.expected_record(F, read(fx.log[F]))
            want['repository'] = REPO.upper()
            return [] if os.path.isfile(h06) and read(h06) == json_bytes(want) else ['not the record computed here']
        case('H06', 'run_record', fx.rr_args(F, h06), fx.env(GITHUB_REPOSITORY=REPO.upper()), check_h06)
        honest = read(fx.log[F])
        lines = honest.rstrip(b'\n').split(b'\n')
        head23 = lines[0].replace(b' judges %s ' % F.encode('ascii'), b' judges %s ' % G.encode('ascii'), 1)
        for cid, data in (('R23', b'\n'.join([head23] + lines[1:]) + b'\n'),
                          ('R24', b'\n'.join(lines[:-1]) + b'\n'),
                          ('R25', honest + honest)):
            log = fx.put('%s/gate.log' % cid, data)
            chk = fx.put('%s/gate-check.json' % cid, json_bytes(fx.check_obj(F, data)))
            rr(cid, gate_log=log, gate_check_json=chk)
        rr('R26', gate_check_json=fx.put('R26/gate-check.json', json_bytes(fx.check_obj(
            F, honest, gate_log_sha256='4' * 64))))
        rr('R27', gate_check_json=fx.put('R27/gate-check.json', json_bytes(fx.check_obj(
            F, honest, gate_verdict_line='%s GATE4 HELD: 19 of 19  [anchor %s]' % (fx.name[F], fx.frozen[F][:16])))))
        inv28 = fx.inventory_obj(dict(fx.frozen, **{F: '5' * 64}))
        rr('R28', inventory_json=fx.put('R28/inventory.json', json_bytes(inv28)),
           judge_json=fx.put('R28/judge.json', json_bytes(fx.judge_obj(inv28['digest']))))
        rr('R29', judge_json=fx.put('R29/judge.json', json_bytes(fx.judge_obj('2' * 64))))
        upper = fx.frozen[F].upper()
        rr('R30', anchor=upper, gate_check_json=fx.put('R30/gate-check.json', json_bytes(fx.check_obj(
            F, honest, anchor=upper))))
        rr('R31', folder='../' + F)
        r32 = os.path.join(tmp, 'r32')
        shutil.copytree(fx.repo, r32)
        fx.git('rm', '-q', WORKFLOW, cwd=r32)
        fx.git('commit', '-q', '-m', 'no workflow', cwd=r32)
        rr('R32', root=r32, env=fx.env(GITHUB_SHA=fx.git('rev-parse', 'HEAD', cwd=r32)))
        rr('R33', env=fx.env(GITHUB_SHA='HEAD'))
        rr('R34', out=os.path.join(tmp, 'no-such-folder', 'R34.json'))

        # Addendum 2: an inventory naming F twice, self-consistent, with the judge's JSON made over it.
        inv_twice = fx.inventory_obj(fx.frozen)
        inv_twice['gated'] = inv_twice['gated'] + [g for g in inv_twice['gated'] if g['folder'] == F]
        inv_twice['digest'] = sha(canonical({k: inv_twice[k] for k in ('gated', 'mirrors', 'gate_dir_files')}))
        judge_twice = fx.judge_obj(inv_twice['digest'])
        inv_twice_path = fx.put('twice/inventory.json', json_bytes(inv_twice))
        judge_twice_path = fx.put('twice/judge.json', json_bytes(judge_twice))
        rr('R35', inventory_json=inv_twice_path, judge_json=judge_twice_path)

        # Plants on verify_records.py: each on its own copy of the honest records.
        def planted(cid):
            d = os.path.join(tmp, 'v', cid)
            shutil.copytree(recs, d)
            return d

        def rec(d, f):
            return os.path.join(d, 'run-record-%s' % f, 'run-record.json')

        d = planted('V01')
        edit_record(rec(d, F), commit='0' * 40)
        vr('V01', d)
        d = planted('V02')
        edit_record(rec(d, F), image_id='sha256:' + '0' * 64)
        vr('V02', d)
        d = planted('V03')
        os.remove(rec(d, G))
        vr('V03', d)
        d = planted('V04')
        os.makedirs(os.path.join(d, 'run-record-zz32'))
        write(rec(d, 'zz32'), read(rec(d, F)))
        edit_record(rec(d, 'zz32'), folder='zz32')
        vr('V04', d)
        d = planted('V05')
        write(os.path.join(d, 'run-record-%s-again' % F, 'run-record.json'), read(rec(d, F)))
        vr('V05', d)
        d = planted('V06')
        edit_record(rec(d, F), anchor=fx.frozen[G])
        vr('V06', d)
        d = planted('V07')
        edit_record(rec(d, F), gate_verdict_line='%s GATE4 FAILED: 19 of 20  [anchor %s]' % (fx.name[F],
                                                                                         fx.frozen[F][:16]))
        vr('V07', d)
        other = [(WORKFLOW, fx.workflow_sha), (GATE4, '0' * 64)]
        vr('V08', recs, judge_json=fx.put('V08/judge.json', json_bytes(fx.judge_obj(fx.inv_digest, files=other))))
        d = planted('V09')
        edit_record(rec(d, F), judge_digest='1' * 64)
        vr('V09', d)
        d = planted('V10')
        edit_record(rec(d, F), schema='skuldd-mathkernel-run-record/2')
        vr('V10', d)
        d = planted('V11')
        edit_record(rec(d, F), gate_check_verdict='GATE LOG FAILED: 1 of 14 rows failed')
        vr('V11', d)
        d = planted('V12')
        edit_record(rec(d, F), note='one key more')
        vr('V12', d)
        d = os.path.join(tmp, 'v', 'V13')
        os.makedirs(d)
        vr('V13', d)
        d = planted('V14')
        write(rec(d, F), read(rec(d, F)).replace(b'{\n', b'{\n "folder": "%s",\n' % G.encode('ascii'), 1))
        vr('V14', d)
        vr('V15', recs, env=fx.env(GITHUB_RUN_ID='1000000002'))
        vr('V16', recs, toolchain_json=fx.put('V16/toolchain.json', json_bytes(fx.toolchain_obj(
            held=False, verdict='TOOLCHAIN FAILED: 1 of 5 rows failed'))))
        inv17 = fx.inventory_obj(fx.frozen)
        inv17['gated'] = [dict(g, frozen4_sha256='0' * 64) if g['folder'] == F else g for g in inv17['gated']]
        vr('V17', recs, inventory_json=fx.put('V17/inventory.json', json_bytes(inv17)))
        v18 = os.path.join(outs, 'V18-existing.json')
        write(v18, b'kept\n')
        vr('V18', recs, out=v18, extra=lambda code: [] if read(v18) == b'kept\n' else ['the existing file changed'])
        d = planted('V19')
        write(os.path.join(d, 'notes.txt'), b'not a record\n')
        vr('V19', d)
        d = planted('V20')
        edit_record(rec(d, F), run_attempt='2')
        vr('V20', d)
        vr('V21', recs, judge_json=os.path.join(tmp, 'in', 'V21-absent.json'))
        d = planted('V22')
        vr('V22', d, out=os.path.join(d, 'run-summary.json'),
           extra=lambda code: ['a summary was written inside --dir']
           if os.path.lexists(os.path.join(tmp, 'v', 'V22', 'run-summary.json')) else [])
        d = planted('V23')
        edit_record(rec(d, F), gate_verdict_line='%s GATE4 HELD: 20 of 20  [anchor %s]' % (fx.name[F], '0' * 16))
        vr('V23', d)
        vr('V24', recs, env=fx.env(GITHUB_SHA=None))
        vr('V25', recs, judge_json=fx.put('V25/judge.json', json_bytes(fx.judge_obj(fx.inv_digest, expect=None))))
        d = planted('V26')
        os.remove(rec(d, G))
        s26 = os.path.join(tmp, 'V26-summary.json')

        def check_v26(code):
            if not os.path.isfile(s26):
                return ['no summary']
            s = json.loads(read(s26).decode('utf-8'))
            n = len([r for r in row_table if r.startswith('VR')])
            bad = []
            if s.get('verdict') != 'RUN RECORDS FAILED: 1 of %d rows failed' % n:
                bad.append('summary verdict %r' % s.get('verdict'))
            if sorted(r['folder'] for r in s.get('records', [])) != sorted(f for f in fx.folders if f != G):
                bad.append('summary records are not the twelve left')
            return bad
        vr('V26', d, out=s26, extra=check_v26)
        vr('V27', recs, inventory_json=fx.put('V27/inventory.json', json_bytes(fx.inventory_obj(
            fx.frozen, held=False, verdict='INVENTORY FAILED: 1 of 40 rows failed'))))

        # Addendum 1: plants on verify_records.py.
        d = planted('V28')
        edit_record(rec(d, F), frozen4_sha256=fx.frozen[G])
        vr('V28', d)
        d = planted('V29')
        obj = json.loads(read(rec(d, F)).decode('utf-8'))
        del obj['gate_log_sha256']
        write(rec(d, F), json_bytes(obj))
        vr('V29', d)
        d = planted('V30')
        edit_record(rec(d, F), commit='xyz')
        vr('V30', d)
        d = planted('V31')
        for f in fx.folders:
            edit_record(rec(d, f), inventory_digest='3' * 64)
        vr('V31', d)
        vr('V32', recs, judge_json=fx.put('V32/judge.json', json_bytes(fx.judge_obj('2' * 64))))
        j33 = fx.judge_obj(fx.inv_digest)
        j33['files'] = [{'path': WORKFLOW, 'sha256': fx.workflow_sha, 'group': 'g'},
                        {'path': GATE4, 'sha256': '0' * 64, 'group': 'g'}]
        vr('V33', recs, judge_json=fx.put('V33/judge.json', json_bytes(j33)))
        d = planted('V34')
        for f in fx.folders:
            edit_record(rec(d, f), toolchain_digest='6' * 64)
        vr('V34', d)
        d = planted('V35')
        edit_record(rec(d, F), gate_verdict_line='%s GATE4 HELD: 19 of 20  [anchor %s]' % (fx.name[F],
                                                                                       fx.frozen[F][:16]))
        vr('V35', d)
        d = planted('V36')
        edit_record(rec(d, F), gate_check_verdict='GATE LOG HELD: 13 of 14 rows')
        vr('V36', d)
        inv37 = fx.inventory_obj(fx.frozen)
        inv37['gated'] = inv37['gated'] + [g for g in inv37['gated'] if g['folder'] == F]
        inv37['digest'] = sha(canonical({k: inv37[k] for k in ('gated', 'mirrors', 'gate_dir_files')}))
        vr('V37', recs, inventory_json=fx.put('V37/inventory.json', json_bytes(inv37)))
        vr('V38', recs, env=fx.env(GITHUB_WORKFLOW_REF='%s/.github/workflows/integrity.yml@%s' % (REPO, REF)))
        d = planted('V39')
        for f in fx.folders:
            edit_record(rec(d, f), inventory_digest=inv_twice['digest'], judge_digest=judge_twice['digest'])
        vr('V39', d, inventory_json=inv_twice_path, judge_json=judge_twice_path)

        # Addendum 3: a judge JSON that hashed another workflow, every record naming its digest.
        j40 = fx.judge_obj(fx.inv_digest, files=[(WORKFLOW, '7' * 64), (GATE4, fx.gate4_sha)])
        d = planted('V40')
        for f in fx.folders:
            edit_record(rec(d, f), judge_digest=j40['digest'])
        vr('V40', d, judge_json=fx.put('V40/judge.json', json_bytes(j40)))

        # Addendum 4: a gate log's byte-order mark and timestamps are read as tools/ci/check_gate_log.py reads them,
        # and a folder name is the inventory's form.
        bom = bytes([0xef, 0xbb, 0xbf]) + honest
        rr('R36', gate_log=fx.put('R36/gate.log', bom), gate_check_json=fx.put('R36/gate-check.json', json_bytes(
            fx.check_obj(F, honest, gate_log_sha256=sha(bom)))))
        bare = b''.join(b'2026-11-18T02:36:44Z ' + x + b'\n' for x in honest.rstrip(b'\n').split(b'\n'))
        rr('R37', gate_log=fx.put('R37/gate.log', bare), gate_check_json=fx.put('R37/gate-check.json', json_bytes(
            fx.check_obj(F, honest, gate_log_sha256=sha(bare)))))
        d = planted('V41')
        edit_record(rec(d, F), folder='9' + F)
        vr('V41', d)

        # Addendum 5: a log check verdict must count exactly check_gate_log.py's rows (verify_records.GATE_LOG_ROWS).
        results.append(gate_log_rows(fx))
        d = planted('V42')
        edit_record(rec(d, F), gate_check_verdict='GATE LOG HELD: %d of %d rows' % (CHECK_ROWS - 1, CHECK_ROWS - 1))
        vr('V42', d)
        d = planted('V43')
        edit_record(rec(d, F), gate_check_verdict='GATE LOG HELD: %d of %d rows' % (CHECK_ROWS + 1, CHECK_ROWS + 1))
        vr('V43', d)

        # Addendum 6: --out inside --dir spelled with a long-path prefix (a leading "//" on POSIX), and written plainly.
        for cid, long in (('V44', True), ('V45', False)):
            d = planted(cid)
            target = os.path.join(d, 'run-summary.json')
            vr(cid, d, out=(LONG + os.path.abspath(target)) if long else target,
               extra=lambda code, target=target: ['a summary was written inside --dir']
               if os.path.lexists(target) else [])

        # Addendum 8: a linked folder in --dir (a junction on Windows, which os.path.islink does not call a link and
        # os.walk enters; a symbolic link on POSIX): beside the honest records, to an empty folder (V47); and as the
        # only entry of --dir, to the honest records (V48). Each is listed as a file, which no record can be.
        def junction(target, link):
            if os.name == 'nt':
                import _winapi
                _winapi.CreateJunction(target, link)
            else:
                os.symlink(target, link, target_is_directory=True)
        d = planted('V47')
        empty = os.path.join(tmp, 'v', 'V47-empty')
        os.makedirs(empty)
        junction(empty, os.path.join(d, 'jx'))
        vr('V47', d)
        d = os.path.join(tmp, 'v', 'V48')
        os.makedirs(d)
        junction(recs, os.path.join(d, 'j'))
        vr('V48', d)

        # Addendum 9: a folder under --dir that cannot be listed, holding note.txt: on Windows one named "x." made
        # through a \\?\ path, which Windows then opens as "x"; on POSIX mode 000 (as root it can be listed, and its
        # note.txt fails the records row as a file that is no record). The walk's error fails the records row.
        d = planted('V49')
        if os.name == 'nt':
            bad = '\\\\?\\' + os.path.join(os.path.abspath(d), 'x.')
            os.mkdir(bad)
            with open(bad + '\\note.txt', 'wb') as fh:
                fh.write(b'not a record\n')
            try:
                vr('V49', d)
            finally:
                os.remove(bad + '\\note.txt')
                os.rmdir(bad)
        else:
            bad = os.path.join(d, 'x')
            os.mkdir(bad)
            write(os.path.join(bad, 'note.txt'), b'not a record\n')
            os.chmod(bad, 0)
            try:
                vr('V49', d)
            finally:
                os.chmod(bad, 0o700)

        # Addendum 7: --out inside --dir spelled as Windows' volume GUID path (a leading "//" on POSIX).
        d = planted('V46')
        target = os.path.join(d, 'run-summary.json')
        given = volume_form(target)
        if given is None:
            results.append(('V46', False, 'the drive of %s has no volume name; the case cannot be built' % target))
        else:
            vr('V46', d, out=given, extra=lambda code, target=target: ['a summary was written inside --dir']
               if os.path.lexists(target) else [])
    except Exception as e:  # the fixture could not be built: every case fails
        results.append(('fixture', False, 'error: %s: %s' % (type(e).__name__, str(e)[:300])))
    finally:
        remove_tree(tmp)

    ran = {cid for cid, _, _ in results}
    for cid in sorted(set(cases) - ran):
        results.append((cid, False, 'predicted but not run'))
    for cid, ok, detail in results:
        print('  %-8s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    n, k = len(results), sum(1 for _, ok, _ in results if not ok)
    if k:
        print('TEST records FAILED: %d of %d cases failed' % (k, n))
        return 1
    print('TEST records HELD: %d of %d cases' % (n, n))
    return 0


if __name__ == '__main__':
    sys.exit(main())
