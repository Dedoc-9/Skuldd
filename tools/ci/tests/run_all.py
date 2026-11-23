# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/run_all.py: runs every test of tools/ci (each tools/ci/tests/test_*.py) and gives one verdict.
# Standard library only (Python 3.12 or later). It writes nothing; each test writes only in a temporary folder.
#
#   python3 -B tools/ci/tests/run_all.py [--image-log LOG]
#       [--ci-logs DIR [--ci-run ID] [--local-tree T --local-folder F --local-console C --local-libs-from C2
#        [--local-failed C3]]]
#
# Rows, one line each, "  <row> ok|FAIL  <detail>":
#   tests found     every test this suite is known to hold is here (a removed test fails this row), and each
#                   test_*.py found here, these and any other, is run.
#   <test run>      one row per test run, sorted by name: it exited 0, its last line is "TEST <name> HELD: n of n
#                   cases" with n at least 1 (<name> is its file name without "test_" and ".py"), and no other line of
#                   its output is a verdict of that test. Its output is printed above its row, each line after "    | ".
# Every test runs every case, with no input from outside the tree: test_check_gate_log.py and test_check_toolchain.py
# run with --repo-data, building their honest inputs and plants from the tree's own records (each test's header says
# what that does not show). This is the CI form. Given saved CI logs (--ci-logs or --image-log), the run is the local
# form: each of those two runs once more in its saved-log mode, an extra row (--ci-logs and the options after it above
# go to test_check_gate_log.py, --image-log to test_check_toolchain.py), and test_workflow_guards.py runs with
# --local, where a case that needs bash to keep a carriage return, which Git Bash drops, may print NOT RUN with that
# reason. Every test runs from the repository's root; a path option is made absolute first, relative to the caller's
# folder.
#
# Each test has TIMEOUT (3600 seconds); one still running then fails its row. The slowest, test_inventory.py, took
# about 17 minutes alone on one Windows host on the tree of thirteen gated folders, about 20 under the read audit's
# hook, and under heavy outside load more than 59 under the hook; on the tree of Push A's batch (21 gated folders,
# 2026-11-22) it took about 21 minutes beside other runs; a limit that stops an honest test turns the suite red with
# no defect in the tree; 60 minutes is about three times the time alone.
#
# What a pass shows: every test exited 0 with its own HELD n of n verdict; each test holds its cases to its predictions
# files (when they were frozen is not checked here). What it does not show: anything a test does not show itself
# (each test's header says what).
# Last line: "CI TESTS HELD: n of n rows" (exit 0) or "CI TESTS FAILED: k of n rows failed" (exit 1); exit 2 on a
# usage error.
import argparse
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

NAME = 'CI TESTS'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
KNOWN = ('test_check_boundaries.py', 'test_check_gate_log.py', 'test_check_sweep.py', 'test_check_toolchain.py',
         'test_drift.py', 'test_feature_row4.py', 'test_inventory.py', 'test_judge_digest.py', 'test_read_audit.py',
         'test_records.py', 'test_safepath.py', 'test_usage.py', 'test_workflow_guards.py', 'test_workflow_pins.py')
GATE_LOG_TEST = 'test_check_gate_log.py'
TOOLCHAIN_TEST = 'test_check_toolchain.py'
GUARDS_TEST = 'test_workflow_guards.py'
TEST_FILE = re.compile(r'test_([a-z0-9_]+)\.py')
TIMEOUT = 3600
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
WIDTH = 44


def row(rows, name, ok, detail):
    rows.append(bool(ok))
    print('  %-*s %s  %s' % (WIDTH, name, 'ok' if ok else 'FAIL', detail))
    sys.stdout.flush()


def parse(argv):
    ap = argparse.ArgumentParser(prog='run_all.py', allow_abbrev=False, add_help=False,
                                 description='Run every test of tools/ci and give one verdict (see the header).')
    ap.add_argument('--image-log', help='test_check_toolchain.py runs once more with it (its saved-log mode)')
    ap.add_argument('--ci-logs', help='test_check_gate_log.py runs once more with it (its saved-log mode)')
    for opt in ('--ci-run', '--local-tree', '--local-folder', '--local-console', '--local-libs-from', '--local-failed'):
        ap.add_argument(opt, help='passed to test_check_gate_log.py with --ci-logs')
    a = ap.parse_args(argv)
    # The tests run from the repository's root, so a path given relative to the caller's folder is made absolute.
    paths = ('image_log', 'ci_logs', 'local_tree', 'local_console', 'local_libs_from', 'local_failed')
    for opt in paths:
        if getattr(a, opt) is not None:
            setattr(a, opt, os.path.abspath(getattr(a, opt)))
    gate_args = []
    if a.ci_logs is not None:
        gate_args = ['--ci-logs', a.ci_logs]
    for opt in ('ci_run', 'local_tree', 'local_folder', 'local_console', 'local_libs_from', 'local_failed'):
        val = getattr(a, opt)
        if val is not None:
            if a.ci_logs is None:
                ap.error('--%s is passed to test_check_gate_log.py, which needs --ci-logs' % opt.replace('_', '-'))
            gate_args += ['--' + opt.replace('_', '-'), val]
    extra = {}
    if gate_args:
        extra[GATE_LOG_TEST] = gate_args
    if a.image_log is not None:
        extra[TOOLCHAIN_TEST] = ['--image-log', a.image_log]
    if extra:
        extra[GUARDS_TEST] = ['--local']
    return extra


def found_tests():
    """(test files, files named test_*.py that are not test_<name>.py), both sorted."""
    names = sorted(os.listdir(HERE))
    tests = [n for n in names if TEST_FILE.fullmatch(n) and os.path.isfile(os.path.join(HERE, n))]
    odd = [n for n in names if n.startswith('test_') and n.endswith('.py') and n not in tests]
    return tests, odd


def judge_output(name, code, text):
    """(ok, detail) for one test's exit code and output."""
    lines = [x.rstrip('\r') for x in text.split('\n')]
    while lines and not lines[-1].strip():
        lines.pop()
    verdict = re.compile(r'TEST %s (?:HELD|FAILED)\b.*' % re.escape(name))
    held = re.compile(r'TEST %s HELD: (\d+) of (\d+) cases' % re.escape(name))
    verdicts = [x for x in lines if verdict.fullmatch(x)]
    last = lines[-1] if lines else ''
    m = held.fullmatch(last)
    if code != 0:
        return False, 'exit %d; last line: %s' % (code, last[:120] or 'none')
    if len(verdicts) != 1 or verdicts[0] != last:
        return False, '%d verdict lines of TEST %s; the last line is: %s' % (len(verdicts), name, last[:120] or 'none')
    if not m or m.group(1) != m.group(2) or int(m.group(1)) < 1:
        return False, 'the last line is not "TEST %s HELD: n of n cases": %s' % (name, last[:120])
    return True, last


def runs_of(tests, extra):
    """[(row name, test file, arguments)]: every test once (the two saved-log tests with --repo-data, the workflow
    guards with --local in the local form), then the saved-log mode of each whose inputs were given."""
    out = []
    for t in tests:
        if t == GUARDS_TEST and t in extra:
            out.append(('%s --local' % t, t, extra[t]))
        elif t in (GATE_LOG_TEST, TOOLCHAIN_TEST):
            out.append(('%s --repo-data' % t, t, ['--repo-data']))
            if t in extra:
                out.append(('%s (saved CI logs)' % t, t, extra[t]))
        else:
            out.append((t, t, []))
    return out


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
    except (AttributeError, ValueError):
        pass
    extra = parse(argv)
    rows = []
    tests, odd = found_tests()
    missing = [k for k in KNOWN if k not in tests]
    runs = runs_of(tests, extra)
    bad = []
    if missing:
        bad.append('absent: %s' % ', '.join(missing))
    if odd:
        bad.append('not named test_<name>.py: %s' % ', '.join(odd))
    if not runs:
        bad.append('no test to run')
    row(rows, 'tests found', not bad, '; '.join(bad) if bad else '%d found (%d known), %d runs'
        % (len(tests), len(KNOWN), len(runs)))

    for label, t, args in runs:
        name = TEST_FILE.fullmatch(t).group(1)
        cmd = [sys.executable, '-B', os.path.join(HERE, t)] + args
        try:
            p = subprocess.run(cmd, cwd=ROOT, env=ENV, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            row(rows, label, False, 'did not finish within %d seconds' % TIMEOUT)
            continue
        except OSError as e:
            row(rows, label, False, 'could not be started (%s)' % type(e).__name__)
            continue
        text = p.stdout.decode('utf-8', 'replace')
        for line in text.split('\n'):
            line = line.rstrip('\r')
            if line:
                print('    | %s' % line)
        ok, detail = judge_output(name, p.returncode, text)
        row(rows, label, ok, detail)

    n, k = len(rows), sum(1 for r in rows if not r)
    print('%s FAILED: %d of %d rows failed' % (NAME, k, n) if k else '%s HELD: %d of %d rows' % (NAME, n, n))
    return 1 if k else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
