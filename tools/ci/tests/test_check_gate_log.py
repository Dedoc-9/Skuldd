# SPDX-License-Identifier: AGPL-3.0-only
# test_check_gate_log.py: runs tools/ci/check_gate_log.py on honest gate logs and on plants, and holds every result to
# a predictions file written and frozen before the first run of its cases.
#
#   python3 -B tools/ci/tests/test_check_gate_log.py --repo-data
#   python3 -B tools/ci/tests/test_check_gate_log.py --ci-logs DIR [--ci-run ID]
#       [--local-tree T --local-folder F --local-console C --local-libs-from C2 [--local-failed C3]]
#
# Exactly one of the two modes:
#
# --repo-data builds every input from this repository's own files, so it runs anywhere, CI included, and runs every
# case of tools/ci/tests/PREDICTIONS-check_gate_log-repo.txt, PREDICTIONS-check_gate_log-repo-2.txt (read in
# this mode only: the honest cases of the folders gated after the first file was frozen) and -repo-3.txt and
# -repo-4.txt (also this mode only: r01-r05, the cases of ruling RD-2 (a)). For each gated folder the
# test writes the console
# gate4.py prints for a --recheck run that holds, in its exact form: the header with the sha256 of the tree's
# kernel/coq/gate/gate4.py, the anchor (the sha256 of the folder's FROZEN4.txt), every row gate4.py prints for that
# folder (its freeze-list rows, its generated files, its and its deps' compile and coqchk rows, the identity row with
# the axiom count of the tier's expected-pa file, its plants), and one "checked in this run" line for every library of
# kernel/coq/EXPECTED-CI-LIBRARIES.txt with its sha256. Then the same plants as the saved-log mode (p01-p30, q01-q10),
# four of its own (s01-s04), r01-r05 and the usage errors. What this mode does not show: that a real gate prints
# these lines (the saved-log mode and every CI gate job show that); rows 11, 12, 14 and 15 hold on its honest
# consoles by construction (the test writes the libraries, the axiom count and Closure.out from the files the checker
# compares them with), so there only the plants show those rows can fail.
#
# --ci-logs (the saved-log mode, run where saved logs exist) holds tools/ci/tests/PREDICTIONS-check_gate_log.txt and
# PREDICTIONS-check_gate_log-2.txt (read in this mode only: the honest cases of the folders gated after the first file
# was frozen; run 44223174587 holds no job log of them, so with that run those cases are not built and fail).
# Both modes also hold the cases of tools/ci/tests/PREDICTIONS-check_gate_log-addendum1.txt (a later round: a gate.json
# whose "deps" names a folder in capitals, and --folder in capitals or starting with a digit).
# --ci-logs holds saved CI job logs named run<ID>-attempt<k>-gate-<folder>-job<j>.log, one per gated folder of this
# tree (every kernel/coq/<folder>/gate.json), with GitHub's timestamp on each line; --ci-run picks the run (default
# 44223174587, whose 13 gate jobs held). The local group names a gate4 tree outside CI (T/gate/, T/<F>/ with gate.json,
# FROZEN4.txt and the out4/Closure.out the console C's run wrote), C2 another HELD console of the same image (its
# library lines become the expected file), and C3 a FAILED console of that folder. Without the local group the four
# local cases are not run, and a line says so before the verdict.
#
# Cases (their inputs are described in the predictions file): the honest twins of the 13 CI gates, as tee writes them
# and as the job log was downloaded; CR LF; --json; 40 plants on the f32 case (p27 on p32): p01-p30, and q01-q10,
# predicted after run 1 for conditions no earlier plant isolated; four local cases; three usage errors (that is the
# base set; addendum 1 adds p31, on p32's console, and the usage errors u04 and u05). A case holds
# when the checker's exit code, its failed rows (exactly the predicted set) and its verdict line are as predicted, and
# every run prints the 15 row names of the predictions file in order. A plant that does not apply (its target text is
# not there exactly once) fails its case: no plant can pass by changing nothing.
#
# What a pass shows: the checker holds every honest log it was given and refuses each plant with the predicted rows.
# What it does not show: for the CI twins, rows 14 and 15 are held by construction (the test builds Closure.out from
# the log's libraries; only the local twin has a Closure.out a real run wrote), and row 11 compares the logs with an
# expected file made from these same logs and three other runs that agreed. Agreement of runs is not soundness.
#
# Prints one line per case, then TEST check_gate_log HELD: n of n cases (exit 0) or TEST check_gate_log FAILED: k of
# n cases failed (exit 1). Exit 2 on a usage error. Writes only in a temporary folder it removes.
import argparse
import glob
import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COQ = os.path.join(ROOT, 'kernel', 'coq')
CHECKER = os.path.normpath(os.path.join(HERE, '..', 'check_gate_log.py'))
PRED_SAVED = os.path.join(HERE, 'PREDICTIONS-check_gate_log.txt')
PRED_REPO = os.path.join(HERE, 'PREDICTIONS-check_gate_log-repo.txt')
# Cases added later, in both modes; a later round adds a file, never edits one.
PRED_ADDENDA = (os.path.join(HERE, 'PREDICTIONS-check_gate_log-addendum1.txt'),)
# Cases added later in the --repo-data mode only: repo-2, the honest cases of the folders gated after PRED_REPO was
# frozen; repo-3 and repo-4, the cases of ruling RD-2 (a) (row 14's list of modules allowed outside the closure).
PRED_REPO_ADDENDA = (os.path.join(HERE, 'PREDICTIONS-check_gate_log-repo-2.txt'),
                     os.path.join(HERE, 'PREDICTIONS-check_gate_log-repo-3.txt'),
                     os.path.join(HERE, 'PREDICTIONS-check_gate_log-repo-4.txt'))
# Cases added later in the saved-log mode only: the honest cases of the folders gated after PRED_SAVED was frozen.
PRED_SAVED_ADDENDA = (os.path.join(HERE, 'PREDICTIONS-check_gate_log-2.txt'),)
EXPECTED = os.path.join(COQ, 'EXPECTED-CI-LIBRARIES.txt')
FROZEN_LINE = re.compile(r'([0-9a-f]{64})  (\S+)')
EXPECTED_LINE = re.compile(r'([A-Za-z_][\w.]*) ([0-9a-f]{64})')
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
STAMP = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+Z ')
LIBLINE = re.compile(r'^  checked in this run: (\S+) ([0-9a-f]{64}) ')
OUTROW = re.compile(r'  (.{62}) (ok|FAIL)  (.*)')
PLANTED = 'Coq.Planted.Extra'

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


class PlantMiss(Exception):
    pass


def rb(path):
    with open(path, 'rb') as f:
        return f.read()


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def one(s, old, new):
    """s with old replaced by new; old must occur exactly once."""
    if s.count(old) != 1:
        raise PlantMiss('%r occurs %d times' % (old[:60], s.count(old)))
    return s.replace(old, new)


def at(lines, test, what):
    """The index of the one line passing test."""
    idx = [i for i, x in enumerate(lines) if test(x)]
    if len(idx) != 1:
        raise PlantMiss('%d lines are %s' % (len(idx), what))
    return idx[0]


def flip(h):
    return h[:-1] + ('1' if h[-1] != '1' else '2')


def read_predictions(pred, addenda=()):
    """(row names, {case: predicted rows}) from the mode's file and each addendum (cases only; rows are the mode's)."""
    text = '\n'.join(rb(p).decode('utf-8') for p in (pred,) + tuple(addenda))
    legend, preds = [], {}
    for line in text.split('\n'):
        if not line or line.startswith('#'):
            continue
        parts = line.split(' | ', 2)
        if parts[0].startswith('row '):
            if int(parts[0][4:]) != len(legend) + 1:
                raise SystemExit('PREDICTIONS: row %s out of order' % parts[0])
            legend.append(parts[1])
            continue
        if len(parts) != 3 or parts[0] in preds:
            raise SystemExit('PREDICTIONS: cannot read %r' % line[:80])
        p = parts[1]
        preds[parts[0]] = p if p in ('none', 'usage') else frozenset(int(k) for k in p.split(','))
    return legend, preds


def section(path):
    """The gate's own lines of a saved job log: timestamps removed, from its header to its verdict."""
    t = rb(path).decode('utf-8')
    if t.startswith('\ufeff'):
        t = t[1:]
    lines = [STAMP.sub('', x) for x in t.split('\n')]
    h = [i for i, x in enumerate(lines) if x.startswith('gate4.py ')]
    v = [i for i, x in enumerate(lines) if re.match(r'^\S+ GATE4 (HELD|FAILED): ', x)]
    if len(h) != 1 or len(v) != 1 or v[0] < h[0]:
        raise PlantMiss('the saved log holds %d headers and %d verdicts' % (len(h), len(v)))
    return lines[h[0]:v[0] + 1]


def libs_of(lines):
    return [m.group(1) for m in (LIBLINE.match(x) for x in lines) if m]


def closure_text(folder, files, libs, deps=()):
    """Closure.out as the test builds it: the libraries, then MKF.<dep>.<stem> for each (dep, files) given, then
    MKF.<folder>.<stem> for every file."""
    return ('Loaded library files: \n' + ''.join('  %s\n' % x for x in libs)
            + ''.join('  MKF.%s.%s\n' % (d, f[:-2]) for d, fs in deps for f in fs)
            + ''.join('  MKF.%s.%s\n' % (folder, f[:-2]) for f in files) + '\n')


def make_tree(dst, src_coq, folder, closure):
    """A --root holding what the checker reads: kernel/coq/<folder>/{gate.json, FROZEN4.txt, out4/Closure.out} and
    kernel/coq/gate/{gate4.py, expected-pa-<tier>.txt}, copied byte for byte from src_coq."""
    cfg = json.loads(rb(os.path.join(src_coq, folder, 'gate.json')).decode('utf-8'))
    coq = os.path.join(dst, 'kernel', 'coq')
    for rel in ('%s/gate.json' % folder, '%s/FROZEN4.txt' % folder, 'gate/gate4.py',
                'gate/expected-pa-%s.txt' % cfg['tier']):
        wb(os.path.join(coq, *rel.split('/')), rb(os.path.join(src_coq, *rel.split('/'))))
    if closure is not None:
        wb(os.path.join(coq, folder, 'out4', 'Closure.out'), closure)
    return dst


def run_checker(args):
    p = subprocess.run([sys.executable, '-B', CHECKER] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=ENV, timeout=600)
    return p.returncode, p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')


def judge(pred, legend, rc, out):
    """(ok, detail) of one checker run against its prediction."""
    lines = [x for x in out.split('\n') if x != '']
    rows = [m for m in (OUTROW.fullmatch(x) for x in lines) if m]
    names = [m.group(1).rstrip() for m in rows]
    failed = frozenset(i + 1 for i, m in enumerate(rows) if m.group(2) == 'FAIL')
    verdicts = [x for x in lines if x.startswith('GATE LOG ')]
    if pred == 'usage':
        ok = rc == 2 and not verdicts and not rows
        return ok, 'exit %d, %d rows, %d verdict lines' % (rc, len(rows), len(verdicts))
    bad = []
    if names != legend:
        bad.append('row names differ from the predictions file')
    digests = [x for x in lines if re.fullmatch(r'LIBRARY MAP DIGEST [0-9a-f]{64}', x)]
    if len(digests) != 1:
        bad.append('%d digest lines' % len(digests))
    if len(verdicts) != 1 or lines[-1] != verdicts[0]:
        bad.append('the verdict is not one last line')
    n = len(legend)
    if pred == 'none':
        want_rc, want_v, want_f = 0, 'GATE LOG HELD: %d of %d rows' % (n, n), frozenset()
    else:
        want_rc, want_v, want_f = 1, 'GATE LOG FAILED: %d of %d rows failed' % (len(pred), n), pred
    if rc != want_rc:
        bad.append('exit %d' % rc)
    if failed != want_f:
        bad.append('failed rows %s, predicted %s' % (sorted(failed) or 'none', sorted(want_f) or 'none'))
    if verdicts and verdicts[0] != want_v:
        bad.append('verdict "%s"' % verdicts[0])
    if bad:
        return False, '; '.join(bad)
    return True, 'exit %d, failed rows %s' % (rc, ','.join(str(k) for k in sorted(failed)) or 'none')


class Ctx:
    def __init__(self, a, tmp):
        self.a, self.tmp, self.cache = a, tmp, {}
        self.repo = bool(a.repo_data)
        self.honest, self.raw = ('h-repo-', 'h-repo-job-') if self.repo else ('h-ci-', 'h-raw-')
        self.folders = sorted(os.path.basename(os.path.dirname(p))
                              for p in glob.glob(os.path.join(COQ, '*', 'gate.json')))

    def log_path(self, folder):
        if self.repo:
            path = os.path.join(self.tmp, 'job-%s.log' % folder)
            if not os.path.exists(path):
                wb(path, job_log(self.section(folder), folder))
            return path
        found = glob.glob(os.path.join(self.a.ci_logs, 'run%s-attempt*-gate-%s-job*.log' % (self.a.ci_run, folder)))
        if len(found) != 1:
            raise PlantMiss('%d saved logs for %s in run %s' % (len(found), folder, self.a.ci_run))
        return found[0]

    def section(self, folder):
        if folder not in self.cache:
            self.cache[folder] = synthetic(self, folder) if self.repo else section(self.log_path(folder))
        return list(self.cache[folder])

    def cfg(self, folder):
        return json.loads(rb(os.path.join(COQ, folder, 'gate.json')).decode('utf-8'))

    def anchor(self, folder):
        return sha(rb(os.path.join(COQ, folder, 'FROZEN4.txt')))


def expected_libs():
    """[(library, sha256)] of kernel/coq/EXPECTED-CI-LIBRARIES.txt, sorted (gate4 prints its libraries sorted)."""
    out = {}
    for x in rb(EXPECTED).decode('utf-8').split('\n'):
        m = EXPECTED_LINE.fullmatch(x)
        if m:
            out[m.group(1)] = m.group(2)
    if not out:
        raise PlantMiss('no library in kernel/coq/EXPECTED-CI-LIBRARIES.txt')
    return sorted(out.items())


def tree_file_count():
    n = 0
    for dp, dn, fn in os.walk(COQ):
        dn[:] = [d for d in dn if d not in ('out4', 'libcache', '__pycache__')]
        n += len(fn)
    return n


def synthetic(ctx, folder):
    """The console gate4.py prints for a --recheck run of the folder in which every row holds, written from the
    tree's files only: its lines from the header to the verdict, in gate4.py's order and form."""
    cfg = ctx.cfg(folder)
    dirs = [d.strip('/') for d in cfg.get('deps', [])] + [folder]
    cfgs = dict((d, ctx.cfg(d)) for d in dirs)
    fz = rb(os.path.join(COQ, folder, 'FROZEN4.txt'))
    anchor = sha(fz)
    entries = [(m.group(1), m.group(2)) for m in (FROZEN_LINE.fullmatch(x) for x in fz.decode('latin-1').split('\n'))
               if m]
    listed = dict((p, h) for h, p in entries)
    epa_rel = 'gate/expected-pa-%s.txt' % cfg['tier']
    epa = rb(os.path.join(COQ, *epa_rel.split('/'))).decode('utf-8')
    axioms = len(set(' '.join(x.split()) for x in epa.splitlines() if x.strip()))
    need = set(['gate/gate4.py', 'gate/strict_read.py', epa_rel])
    for d in dirs:
        need.add(d + '/gate.json')
        need.update(d + '/' + f for f in cfgs[d]['files'])
        need.update(posixpath.normpath(spec[0]) for spec in cfgs[d].get('generated', {}).values())
    for pl in cfg.get('plants', {}).values():
        need.update(posixpath.normpath(folder + '/' + s) for s in pl['replace'].values())
    libs = expected_libs()
    want = [d + '/' + f for d in dirs for f in cfgs[d]['files']]
    out, n = [], [0]

    def row(name, det):
        n[0] += 1
        out.append('  %-62s %s  %s' % (name, 'ok', det))
    out.append('gate4.py %s judges %s (identity %s.%s; sources of %s) in /work  --recheck'
               % (sha(rb(os.path.join(COQ, 'gate', 'gate4.py'))), folder, folder, cfg['identity'], ', '.join(dirs)))
    out.append('anchor %s' % anchor)
    row('freeze list: every line is readable', '%d entries' % len(entries))
    row('freeze list: no path is listed twice', '')
    row('freeze list: every required entry is on it', '%d required, %d listed' % (len(need), len(listed)))
    row('frozen inputs unchanged', '%d files' % len(entries))
    row('freeze list is the anchored one', 'ANCHOR %s' % anchor[:16])
    for d in dirs:
        for path, spec in sorted(cfgs[d].get('generated', {}).items()):
            row('%s is what %s emits' % (path, spec[0]), '')
    row('fresh root holds only the listed sources', '%d sources of %d folders, no other file' % (len(want), len(dirs)))
    for p in want:
        row('compile %s' % p[:-2], 'exit 0')
    row('identity: Print Assumptions is exactly the %s list' % cfg['tier'], '%d axioms' % axioms)
    for p in want:
        row('coqchk -norec %s' % p[:-2], 'exit 0, unsafe sections <none>')
    out.append('  sources judged: %s' % ', '.join('%s %s' % (p, listed.get(p, 'MISSING')[:12]) for p in want))
    row('closure: every MKF library is one compiled and rechecked above', '%d of ours in the closure' % len(want))
    for lib, h in libs:
        out.append('  checked in this run: %s %s exit 0 clean' % (lib, h))
    row('closure: every outside library passed coqchk -norec, unsafe <none>',
        '%d libraries by the sha256 of their files: 0 from the log, %d checked in this run' % (len(libs), len(libs)))
    for pname, pl in sorted(cfg.get('plants', {}).items()):
        if 'generated' in pl:
            det = 'the planted file is not the generator\'s output'
        elif 'fails' in pl:
            det = '%s exit 1: Error: %s' % (pl['fails'], pl['text'])
        else:
            det = 'compiled; PA: unexpected line: %s' % pl.get('reader', '')
        row('plant %s refused' % pname, det)
    row('nothing written to the tree outside out4 and the library log', '%d files as they were' % tree_file_count())
    out.append('%s GATE4 HELD: %d of %d  [anchor %s]' % (cfg['name'], n[0], n[0], anchor[:16]))
    return out


def job_log(lines, folder):
    """The console as GitHub serves a job log for download: a byte-order mark, a timestamp on every line, and the
    runner's own lines before and after the step's output."""
    before = ['##[group]Run set -euo pipefail', 'set -euo pipefail',
              'docker run --rm --network none -e ANCHOR -v "$GITHUB_WORKSPACE/kernel/coq:/work" -w /work "$IMAGE" '
              'python3 -B gate/gate4.py "$FOLDER" --recheck | tee "$RUNNER_TEMP/gate.log"',
              'shell: /usr/bin/bash -e {0}', 'env:', '  FOLDER: %s' % folder, '##[endgroup]']
    after = ['##[group]Run python3 -B tools/ci/check_gate_log.py --log "$RUNNER_TEMP/gate.log"', '##[endgroup]',
             'Post job cleanup.']
    stamped = ['2026-11-18T00:%02d:%02d.%07dZ %s' % (k // 60 % 60, k % 60, k * 1013 % 10000000, x)
               for k, x in enumerate(before + list(lines) + after)]
    return b'\xef\xbb\xbf' + ('\n'.join(stamped) + '\n').encode('utf-8')


def reanchor_lines(lines, old, new):
    """The log's three anchor places (the anchor line, the anchored row, the verdict) moved from old to new."""
    text = '\n'.join(lines)
    for a, b in (('anchor ' + old, 'anchor ' + new), ('ANCHOR ' + old[:16], 'ANCHOR ' + new[:16]),
                 ('[anchor %s]' % old[:16], '[anchor %s]' % new[:16])):
        text = one(text, a, b)
    return text.split('\n')


def ci_args(ctx, cid, folder, mode='section', log=None, log_bytes=None, closure=None, tree=None, expected=None,
            real_root=False, no_log=False, no_expected=False, json_out=False, reanchor=False):
    """The checker's arguments for one CI case; each keyword names one change to the honest twin. With reanchor the
    anchor is the sha256 of the changed tree's FROZEN4.txt, and the log names it in its three anchor places."""
    d = os.path.join(ctx.tmp, cid)
    os.makedirs(d)
    sec = ctx.section(folder)
    deps = [(d, ctx.cfg(d)['files']) for d in ctx.cfg(folder).get('deps', [])] if ctx.repo else []
    ct = closure_text(folder, ctx.cfg(folder)['files'], libs_of(sec), deps)
    if closure:
        ct = closure(ct)
    if real_root:
        root = ROOT
    else:
        root = make_tree(os.path.join(d, 'root'), COQ, folder, ct.encode('utf-8'))
        if tree:
            tree(os.path.join(root, 'kernel', 'coq'))
    anchor = ctx.anchor(folder)
    lines = log(sec) if log else sec
    if reanchor:
        new = sha(rb(os.path.join(root, 'kernel', 'coq', folder, 'FROZEN4.txt')))
        if new == anchor:
            raise PlantMiss('the tree\'s FROZEN4.txt did not change')
        lines, anchor = reanchor_lines(lines, anchor, new), new
    if no_log:
        log_path = os.path.join(d, 'absent.log')
    elif mode == 'raw':
        log_path = ctx.log_path(folder)
    else:
        data = '\n'.join(lines) + '\n'
        if mode == 'crlf':
            data = data.replace('\n', '\r\n')
        data = data.encode('utf-8')
        if log_bytes:
            data = log_bytes(data)
        log_path = os.path.join(d, 'gate.log')
        wb(log_path, data)
    exp = EXPECTED
    if no_expected:
        exp = os.path.join(d, 'absent-expected.txt')
    elif expected:
        exp = os.path.join(d, 'expected.txt')
        wb(exp, expected(rb(EXPECTED)))
    args = ['--log', log_path, '--folder', folder, '--anchor', anchor, '--root', root, '--expected-libs', exp]
    if json_out:
        args += ['--json', os.path.join(d, 'check.json')]
    return args


# Plants on the lines of a gate log (each returns a new list).
def on_line(test, what, fn):
    def plant(lines):
        lines = list(lines)
        i = at(lines, test, what)
        new = fn(lines[i])
        if new == lines[i]:
            raise PlantMiss('the plant changed nothing in %s' % what)
        lines[i] = new
        return lines
    return plant


def is_closure_row(x):
    return x.startswith('  closure: every outside library passed')


def bump_closure(k):
    def fn(x):
        form = 'ok  %s libraries by the sha256 of their files: 0 from the log, %s checked in this run'
        m = re.search(form % (r'(\d+)', r'(\d+)') + '$', x)
        if not m:
            raise PlantMiss('closure row not in its form')
        return x[:m.start()] + form % (int(m.group(1)) + k, int(m.group(2)) + k)
    return on_line(is_closure_row, 'the closure row', fn)


def first_lib(lines):
    return [i for i, x in enumerate(lines) if LIBLINE.match(x)][0]


def last_lib(lines):
    return [i for i, x in enumerate(lines) if LIBLINE.match(x)][-1]


def p_hash(lines):
    lines = list(lines)
    i = first_lib(lines)
    m = LIBLINE.match(lines[i])
    lines[i] = one(lines[i], m.group(2), flip(m.group(2)))
    return lines


def p_extra(lines):
    lines = bump_closure(1)(lines)
    i = last_lib(lines)
    return lines[:i + 1] + ['  checked in this run: %s %s exit 0 clean' % (PLANTED, sha(b'planted'))] + lines[i + 1:]


def p_twice(lines):
    lines = bump_closure(1)(lines)
    i = first_lib(lines)
    return lines[:i + 1] + [lines[i]] + lines[i + 1:]


def p_not_clean(lines):
    lines = list(lines)
    i = first_lib(lines)
    lines[i] = one(lines[i], ' exit 0 clean', ' exit 1 notclean')
    return lines


def p_delete(test, what):
    def plant(lines):
        lines = list(lines)
        del lines[at(lines, test, what)]
        return lines
    return plant


def p_insert_after_anchor(lines):
    i = at(lines, lambda x: x.startswith('anchor '), 'the anchor line')
    return lines[:i + 1] + ['Traceback (most recent call last):'] + lines[i + 1:]


def is_verdict(x):
    return ' GATE4 ' in x and x.endswith(']')


def is_shadow(x):
    return x.startswith('  plant shadow refused ')


def shadow_fail(x):
    new = re.sub(r'^(  plant shadow refused +)ok  ', r'\1FAIL  ', x)
    if new == x:
        raise PlantMiss('the shadow row is not ok')
    return new


def verdict_counts(fmt):
    def fn(x):
        m = re.search(r'HELD: (\d+) of (\d+)', x)
        if not m or m.group(1) != m.group(2):
            raise PlantMiss('verdict not HELD n of n')
        n = int(m.group(2))
        return x[:m.start()] + fmt % (n - 1, n) + x[m.end():]
    return fn


def p_cut_hash(lines):
    lines = list(lines)
    i = first_lib(lines)
    m = LIBLINE.match(lines[i])
    lines[i] = one(lines[i], m.group(2), m.group(2)[:-1])
    return lines


def p_zero(lines):
    kept = [x for x in lines if not LIBLINE.match(x)]
    if len(kept) == len(lines):
        raise PlantMiss('no library line to remove')
    form = 'ok  %s libraries by the sha256 of their files: 0 from the log, %s checked in this run'
    return on_line(is_closure_row, 'the closure row',
                   lambda x: re.sub(form % (r'\d+', r'\d+') + '$', form % (0, 0), x))(kept)


def p_twice_after(test, what):
    def plant(lines):
        i = at(lines, test, what)
        return lines[:i + 1] + [lines[i]] + lines[i + 1:]
    return plant


def b_not_utf8(b):
    head, rest = b.split(b'\n', 1)
    return head + b'\n\xff\n' + rest


def b_repeat_last(b):
    last = b.rstrip(b'\n').split(b'\n')[-1]
    if not re.fullmatch(rb'\S+ [0-9a-f]{64}', last):
        raise PlantMiss('the last line is not a library line')
    return appended(b, last + b'\n')


def dup_listed(suffix):
    def fn(b):
        lines = b.split(b'\n')
        idx = [i for i, x in enumerate(lines) if x.endswith(b'  ' + suffix)]
        if len(idx) != 1:
            raise PlantMiss('%d lines list %r' % (len(idx), suffix))
        return b'\n'.join(lines[:idx[0] + 1] + [lines[idx[0]]] + lines[idx[0] + 1:])
    return fn


def p_verdict_failed(lines):
    lines = on_line(is_shadow, 'the shadow row', shadow_fail)(lines)
    return on_line(is_verdict, 'the verdict', verdict_counts('FAILED: %d of %d'))(lines)


def s_failed_console(lines):
    """A run without --recheck in which the rows of the plants guard and shadow FAIL: the verdict FAILED n-2 of n."""
    lines = on_line(lambda x: x.startswith('gate4.py '), 'the header', lambda x: one(x, '  --recheck', ''))(lines)
    for p in ('guard', 'shadow'):
        lines = on_line(lambda x, p=p: x.startswith('  plant %s refused ' % p), 'the %s row' % p,
                        lambda x: re.sub(r'^(  plant \S+ refused +)ok  ', r'\1FAIL  ', x))(lines)

    def fn(x):
        m = re.search(r'HELD: (\d+) of (\d+)', x)
        if not m or m.group(1) != m.group(2):
            raise PlantMiss('verdict not HELD n of n')
        k = int(m.group(2))
        return x[:m.start()] + 'FAILED: %d of %d' % (k - 2, k) + x[m.end():]
    return on_line(is_verdict, 'the verdict', fn)(lines)


def s_other_image(lines):
    """Every library line's sha256 with its last digit changed: the same libraries, another image's files."""
    out, k = [], 0
    for x in lines:
        m = LIBLINE.match(x)
        if m:
            x = one(x, m.group(2), flip(m.group(2)))
            k += 1
        out.append(x)
    if not k:
        raise PlantMiss('no library line')
    return out


def axioms_plus(x):
    m = re.search(r'ok  (\d+) axioms$', x)
    if not m:
        raise PlantMiss('identity row not in its form')
    return x[:m.start()] + 'ok  %d axioms' % (int(m.group(1)) + 1)


def appended(text_bytes, extra):
    sep = b'' if text_bytes.endswith(b'\n') else b'\n'
    return text_bytes + sep + extra


def edit_file(rel, fn):
    def tree(coq):
        p = os.path.join(coq, *rel.split('/'))
        wb(p, fn(rb(p)))
    return tree


def bone(old, new):
    def fn(b):
        if b.count(old) != 1:
            raise PlantMiss('%r occurs %d times' % (old, b.count(old)))
        return b.replace(old, new)
    return fn


def ci_cases(ctx):
    """(case id, function returning the checker's arguments, an extra check or None)."""
    out = []
    for f in ctx.folders:
        out.append((ctx.honest + f, lambda f=f, c=ctx.honest + f: ci_args(ctx, c, f), None))
    for f in ctx.folders:
        out.append((ctx.raw + f, lambda f=f, c=ctx.raw + f: ci_args(ctx, c, f, mode='raw'), None))
    out.append(('h-crlf-f32', lambda: ci_args(ctx, 'h-crlf-f32', 'f32', mode='crlf'), None))
    out.append(('h-json-f32', lambda: ci_args(ctx, 'h-json-f32', 'f32', json_out=True), check_json))
    hdr = (lambda x: x.startswith('gate4.py '), 'the header')
    plants = {
        'p01-one-from-log': dict(log=on_line(is_closure_row, 'the closure row',
                                             lambda x: one(x, ': 0 from the log, ', ': 1 from the log, '))),
        'p02-counts-differ': dict(log=on_line(is_closure_row, 'the closure row', lambda x: re.sub(
            r', (\d+) checked in this run$', lambda m: ', %d checked in this run' % (int(m.group(1)) - 1), x))),
        'p03-library-hash-changed': dict(log=p_hash),
        'p04-extra-library': dict(log=p_extra, closure=lambda c: one(c, 'Loaded library files: \n',
                                                                     'Loaded library files: \n  %s\n' % PLANTED)),
        'p05-anchored-row-missing': dict(log=p_delete(lambda x: x.startswith('  freeze list is the anchored one '),
                                                      'the anchored row')),
        'p06-fail-row': dict(log=on_line(is_shadow, 'the shadow row', shadow_fail)),
        'p07-verdict-unequal': dict(log=on_line(is_verdict, 'the verdict', verdict_counts('HELD: %d of %d'))),
        'p08-verdict-other-anchor': dict(log=on_line(is_verdict, 'the verdict', lambda x: re.sub(
            r'\[anchor [0-9a-f]{16}\]$', '[anchor 0000000000000000]', x))),
        'p09-axioms-plus-one': dict(log=on_line(lambda x: x.startswith('  identity: '), 'the identity row',
                                                axioms_plus)),
        'p10-own-module-missing': dict(closure=lambda c: one(c, '  MKF.f32.F32\n', '')),
        'p11-no-recheck': dict(log=on_line(*hdr, lambda x: one(x, '  --recheck', ''))),
        'p12-header-other-folder': dict(log=on_line(*hdr, lambda x: one(x, ' judges f32 (', ' judges p32 ('))),
        'p13-anchor-line-other': dict(log=on_line(lambda x: x.startswith('anchor '), 'the anchor line', flip)),
        'p14-second-verdict': dict(log=lambda lines: list(lines) + [lines[-1]]),
        'p15-unknown-line': dict(log=p_insert_after_anchor),
        'p16-library-not-clean': dict(log=p_not_clean),
        'p17-library-twice': dict(log=p_twice),
        'p18-expected-missing': dict(no_expected=True),
        'p19-expected-malformed': dict(expected=lambda b: appended(b, b'garbage\n')),
        'p20-real-tree-no-out4': dict(real_root=True),
        'p21-closure-extra-outside': dict(closure=lambda c: one(c, 'Loaded library files: \n',
                                                                'Loaded library files: \n  %s\n' % PLANTED)),
        'p22-gatejson-name-changed': dict(tree=edit_file('f32/gate.json', bone(b'"name": "F32"', b'"name": "F33"'))),
        'p23-frozen4-not-anchor': dict(tree=edit_file('f32/FROZEN4.txt', lambda b: appended(b, b'# planted\n'))),
        'p24-gate4-changed': dict(tree=edit_file('gate/gate4.py', lambda b: appended(b, b'# planted\n'))),
        'p25-expected-pa-plus-one': dict(tree=edit_file('gate/expected-pa-flocq4.txt',
                                                        lambda b: appended(b, b'Planted.extra_axiom : False\n'))),
        'p26-log-missing': dict(no_log=True),
        'p28-verdict-failed': dict(log=p_verdict_failed),
        'p29-library-after-verdict': dict(log=lambda lines: list(lines) + [lines[first_lib(lines)]]),
        'p30-identity-other-tier': dict(log=on_line(lambda x: x.startswith('  identity: '), 'the identity row',
                                                    lambda x: one(x, 'exactly the flocq4 list',
                                                                  'exactly the flocq3 list'))),
        # Added after run 1 (see the predictions file).
        'q01-identity-module-missing': dict(closure=lambda c: one(c, '  MKF.f32.Identity\n', '')),
        'q02-logged-not-in-closure': dict(closure=lambda c: one(c, '  %s\n' % libs_of(ctx.section('f32'))[0], '')),
        'q03-header-other-identity': dict(log=on_line(*hdr, lambda x: one(x, '(identity f32.Identity;',
                                                                          '(identity f32.Other;'))),
        'q04-two-anchor-lines': dict(log=p_twice_after(lambda x: x.startswith('anchor '), 'the anchor line')),
        'q05-log-not-utf8': dict(log_bytes=b_not_utf8),
        'q06-library-line-unreadable': dict(log=p_cut_hash),
        'q07-expected-library-twice': dict(expected=b_repeat_last),
        'q08-frozen4-lists-gate4-twice': dict(tree=edit_file('f32/FROZEN4.txt', dup_listed(b'gate/gate4.py')),
                                              reanchor=True),
        'q09-zero-libraries': dict(log=p_zero),
        'q10-two-headers': dict(log=p_twice_after(*hdr)),
    }
    if ctx.repo:
        # The plants of the repository-data mode only (PREDICTIONS-check_gate_log-repo.txt).
        plants.update({
            's01-failed-console': dict(log=s_failed_console),
            's02-other-image': dict(log=s_other_image),
            's03-tier-not-a-name': dict(tree=edit_file('f32/gate.json', bone(b'"tier": "flocq4"',
                                                                              b'"tier": "flocq4\\u0000"'))),
            's04-gatejson-too-deep': dict(tree=edit_file('f32/gate.json', lambda b: b'[' * 100000 + b']' * 100000)),
        })
    for cid, kw in plants.items():
        out.append((cid, lambda cid=cid, kw=kw: ci_args(ctx, cid, 'f32', **kw), None))
    out.append(('p27-header-source-dropped', lambda: ci_args(ctx, 'p27-header-source-dropped', 'p32', log=on_line(
        *hdr, lambda x: one(x, 'sources of f32, p32)', 'sources of p32)'))), None))
    if ctx.repo:   # ruling RD-2 (a): row 14's list of modules allowed outside the closure (PREDICTIONS-...-repo-3)
        out.append(('r01-check-modules-outside', lambda: ci_args(ctx, 'r01-check-modules-outside', 'ieee64', closure=(
            lambda c: one(one(c, '  MKF.ieee64.P32_IEEE_Check\n', ''), '  MKF.ieee64.EXP32_IEEE_Check\n', ''))), None))
        out.append(('r02-unlisted-module-outside', lambda: ci_args(ctx, 'r02-unlisted-module-outside', 'ieee64',
                                                                   closure=lambda c: one(c, '  MKF.ieee64.Ops\n', '')),
                    None))
        out.append(('r03-listed-module-not-compiled', lambda: ci_args(
            ctx, 'r03-listed-module-not-compiled', 'ieee64',
            closure=lambda c: one(c, '  MKF.ieee64.P32_IEEE_Check\n', ''),
            log=on_line(lambda x: 'compile ieee64/P32_IEEE_Check ' in x, 'the compile row of P32_IEEE_Check',
                        lambda x: x.replace('compile ieee64/P32_IEEE_Check ', 'compile ieee64/P32_IEEE_Checkx', 1))),
                    None))
        out.append(('r04-compile-row-after-verdict', lambda: ci_args(
            ctx, 'r04-compile-row-after-verdict', 'ieee64',
            closure=lambda c: one(c, '  MKF.ieee64.P32_IEEE_Check\n', ''),
            log=lambda s: on_line(
                lambda x: 'compile ieee64/P32_IEEE_Check ' in x, 'the compile row of P32_IEEE_Check',
                lambda x: x.replace('compile ieee64/P32_IEEE_Check ', 'compile ieee64/P32_IEEE_Checkx', 1))(s)
            + ['  %-62s ok  exit 0' % 'compile ieee64/P32_IEEE_Check']),
                    None))
        out.append(('r05-compile-row-other-folder', lambda: ci_args(
            ctx, 'r05-compile-row-other-folder', 'ieee64',
            closure=lambda c: one(c, '  MKF.ieee64.P32_IEEE_Check\n', ''),
            log=on_line(lambda x: 'compile ieee64/P32_IEEE_Check ' in x, 'the compile row of P32_IEEE_Check',
                        lambda x: x.replace('compile ieee64/P32_IEEE_Check ', 'compile f32/P32_IEEE_Check ', 1))),
                    None))
    # PREDICTIONS-check_gate_log-addendum1.txt (both modes)
    out.append(('p31-deps-not-a-folder-name', lambda: ci_args(ctx, 'p31-deps-not-a-folder-name', 'p32', tree=edit_file(
        'p32/gate.json', bone(b'"deps": ["f32"]', b'"deps": ["F32"]'))), None))
    for cid, extra in (('u01-anchor-not-hex', ['--anchor', 'XYZ']), ('u02-no-expected-libs', None),
                       ('u03-folder-dotdot', ['--folder', '../f32']), ('u04-folder-upper', ['--folder', 'F32']),
                       ('u05-folder-digit', ['--folder', '9f32'])):
        out.append((cid, lambda cid=cid, extra=extra: usage_args(ctx, cid, extra), None))
    return out


def usage_args(ctx, cid, extra):
    args = ci_args(ctx, cid, 'f32')
    if extra is None:
        i = args.index('--expected-libs')
        return args[:i] + args[i + 2:]
    i = args.index(extra[0])
    return args[:i] + extra + args[i + 2:]


def check_json(args, out):
    """The --json record agrees with what the checker printed and with the log it read."""
    path = args[args.index('--json') + 1]
    log = rb(args[args.index('--log') + 1])
    obj = json.loads(rb(path).decode('utf-8'))
    lines = [x for x in out.split('\n') if x]
    printed = [x[len('LIBRARY MAP DIGEST '):] for x in lines if x.startswith('LIBRARY MAP DIGEST ')]
    sec = log.decode('utf-8').split('\n')
    pairs = sorted(set('%s %s\n' % (m.group(1), m.group(2)) for m in (LIBLINE.match(x) for x in sec) if m))
    own = sha(''.join(pairs).encode('utf-8'))
    bad = []
    for k, want in (('schema', 'skuldd-gate-log-check/1'), ('held', True), ('verdict', lines[-1]),
                    ('folder', 'f32'), ('anchor', args[args.index('--anchor') + 1]), ('gate_log_sha256', sha(log)),
                    ('gate_verdict_line', [x for x in sec if x][-1]), ('differences', []),
                    ('library_map_digest', own), ('library_count', len(pairs))):
        if obj.get(k) != want:
            bad.append('%s is %r' % (k, str(obj.get(k))[:40]))
    if printed != [own]:
        bad.append('printed digest %s, the test computes %s' % (printed, own[:16]))
    if len(obj.get('rows', [])) != 15:
        bad.append('%d rows in the record' % len(obj.get('rows', [])))
    return not bad, '; '.join(bad) if bad else 'record agrees, digest %s' % own[:16]


def local_cases(ctx):
    a = ctx.a
    if not a.local_tree:
        return []
    cache = {}

    def base(cid, closure=None, expected=None, console=None, anchor=None):
        d = os.path.join(ctx.tmp, cid)
        os.makedirs(d)
        if 'closure' not in cache:
            cache['closure'] = rb(os.path.join(a.local_tree, a.local_folder, 'out4', 'Closure.out'))
            libs = {}
            for x in rb(a.local_libs_from).decode('utf-8').split('\n'):
                m = LIBLINE.match(x.rstrip('\r'))
                if m:
                    libs[m.group(1)] = m.group(2)
            if not libs:
                raise PlantMiss('no library line in --local-libs-from')
            cache['expected'] = ('# built by the test from another HELD console of the same image\n'
                                 + ''.join('%s %s\n' % kv for kv in sorted(libs.items()))).encode('utf-8')
        ct = cache['closure'] if closure is None else closure(cache['closure'])
        root = make_tree(os.path.join(d, 'root'), a.local_tree, a.local_folder, ct)
        exp = expected or os.path.join(d, 'expected.txt')
        if not expected:
            wb(exp, cache['expected'])
        anc = anchor or sha(rb(os.path.join(a.local_tree, a.local_folder, 'FROZEN4.txt')))
        return ['--log', console or a.local_console, '--folder', a.local_folder, '--anchor', anc, '--root', root,
                '--expected-libs', exp]

    def failed_anchor():
        found = [m.group(1) for m in (re.fullmatch(r'anchor ([0-9a-f]{64})', x.rstrip('\r'))
                                      for x in rb(a.local_failed).decode('utf-8').split('\n')) if m]
        if len(found) != 1:
            raise PlantMiss('%d anchor lines in --local-failed' % len(found))
        return found[0]

    def own_missing(c):
        files = json.loads(rb(os.path.join(a.local_tree, a.local_folder, 'gate.json')).decode('utf-8'))['files']
        return bone(('  MKF.%s.%s\n' % (a.local_folder, files[1][:-2])).encode('utf-8'), b'')(c)

    out = [('local-h-console', lambda: base('local-h-console'), None)]
    if a.local_failed:
        out.append(('local-p-failed-console', lambda: base('local-p-failed-console', console=a.local_failed,
                                                           anchor=failed_anchor()), None))
    out.append(('local-p-own-module-missing', lambda: base('local-p-own-module-missing', closure=own_missing), None))
    out.append(('local-p-ci-expected', lambda: base('local-p-ci-expected', expected=EXPECTED), None))
    return out


def main():
    ap = argparse.ArgumentParser(prog='test_check_gate_log.py', allow_abbrev=False, add_help=False,
                                 description='Test tools/ci/check_gate_log.py (see the header).')
    ap.add_argument('--repo-data', action='store_true')
    ap.add_argument('--ci-logs')
    ap.add_argument('--ci-run', default='44223174587')
    ap.add_argument('--local-tree')
    ap.add_argument('--local-folder')
    ap.add_argument('--local-console')
    ap.add_argument('--local-libs-from')
    ap.add_argument('--local-failed')
    a = ap.parse_args()
    group = (a.local_tree, a.local_folder, a.local_console, a.local_libs_from)
    if any(group) and not all(group):
        ap.error('--local-tree, --local-folder, --local-console and --local-libs-from go together')
    if a.local_failed and not a.local_tree:
        ap.error('--local-failed needs the local group')
    if a.repo_data == (a.ci_logs is not None):
        ap.error('give exactly one of --repo-data and --ci-logs')
    if a.repo_data and any(group):
        ap.error('the local group goes with --ci-logs')
    if a.ci_logs is not None and not os.path.isdir(a.ci_logs):
        ap.error('--ci-logs is not a folder')
    pred = PRED_REPO if a.repo_data else PRED_SAVED
    addenda = PRED_ADDENDA + (PRED_REPO_ADDENDA if a.repo_data else PRED_SAVED_ADDENDA)
    legend, preds = read_predictions(pred, addenda)
    print('mode %s; predictions %s (%s, %d cases with %s)' % (
        'repo-data' if a.repo_data else 'saved CI logs', sha(rb(pred)), os.path.basename(pred), len(preds),
        ', '.join('%s %s' % (os.path.basename(p), sha(rb(p))[:16]) for p in addenda)))
    tmp = tempfile.mkdtemp(prefix='test-gate-log-')
    results = []
    try:
        ctx = Ctx(a, tmp)
        cases = ci_cases(ctx) + local_cases(ctx)
        ids = [c[0] for c in cases]
        local_ids = sorted(k for k in preds if k.startswith('local-'))
        not_run = [k for k in local_ids if k not in ids]
        problems = []
        if sorted(set(ids)) != sorted(ids):
            problems.append('a case id twice')
        extra = sorted(set(ids) - set(preds))
        missing = sorted(set(preds) - set(ids) - set(not_run))
        if extra or missing:
            problems.append('built, not predicted: %s; predicted, not built: %s' % (extra or 'none', missing or 'none'))
        ci = sorted(k[len(ctx.honest):] for k in preds if k.startswith(ctx.honest) and not k.startswith(ctx.raw))
        if ci != ctx.folders:
            problems.append('the tree gates %s; the predictions name %s' % (ctx.folders, ci))
        results.append(('predictions name every case, once', not problems,
                        '; '.join(problems) if problems else '%d cases, %d gated folders' % (len(ids), len(ci))))
        for cid, build, extra_check in cases:
            if cid not in preds:
                results.append((cid, False, 'no prediction'))
                continue
            try:
                args = build()
            except (PlantMiss, OSError, ValueError) as e:
                results.append((cid, False, 'the case could not be built: %s' % e))
                continue
            rc, out = run_checker(args)
            ok, det = judge(preds[cid], legend, rc, out)
            if ok and extra_check:
                ok, det2 = extra_check(args, out)
                det = '%s; %s' % (det, det2)
            results.append((cid, ok, det))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for cid, ok, det in results:
        print('  %-36s %s  %s' % (cid, 'ok' if ok else 'FAIL', det))
    if not_run:
        print('  not run (no --local-tree or no --local-failed): %s' % ', '.join(not_run))
    failed = sum(1 for r in results if not r[1])
    n = len(results)
    if failed:
        print('TEST check_gate_log FAILED: %d of %d cases failed' % (failed, n))
        return 1
    print('TEST check_gate_log HELD: %d of %d cases' % (n, n))
    return 0


if __name__ == '__main__':
    sys.exit(main())
