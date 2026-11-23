# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_usage.py: each script named in its cases, the scripts of tools/ci that read their options with
# argparse when it was written (2026-11-20), refuses --help and an abbreviated option as usage errors (exit 2, no
# verdict line), so no option it was not given in full can change what it checks, and no run exits 0 without its
# verdict. Three scripts added later have the same two refusals held by their own tests, not here:
# check_boundaries.py (test_check_boundaries.py U03, U04), check_sweep.py (test_check_sweep.py U01, U02) and
# drift.py (test_drift.py U01, U02). Standard library only (Python 3.12 or later). It writes only in a
# temporary folder, which it removes.
#
#   python3 -B tools/ci/tests/test_usage.py
#
# Two cases per script, held to tools/ci/tests/PREDICTIONS-usage.txt (frozen before the first run): "--help" alone, and
# the script's other options given in full but one given by a prefix of its name. Each abbreviated call is one that
# argparse with abbreviations allowed would run (it would then exit 0 or 1, never 2), so each case can fail.
# A case holds when the script exits 2 and prints no line of the form "<NAME> HELD..." or "<NAME> FAILED...".
# What a pass shows: these scripts refuse such calls on this interpreter. What it does not show: a script that does not
# use argparse (feature_row4.py refuses unknown options by its own reading; its test holds that).
# Last line: "TEST usage HELD: n of n cases" (exit 0) or "TEST usage FAILED: k of n cases failed" (exit 1).
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
PRED = os.path.join(HERE, 'PREDICTIONS-usage.txt')
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
VERDICT = re.compile(r'[A-Z][A-Z0-9 ]* (?:HELD|FAILED)\b.*')
Z = '0' * 64


def cases(t):
    """{case: (script, args)}; t is a temporary folder holding an empty folder, an empty file and a JSON object."""
    d, f, j = os.path.join(t, 'empty'), os.path.join(t, 'empty.txt'), os.path.join(t, 'object.json')
    libs = os.path.join(ROOT, 'kernel', 'coq', 'EXPECTED-CI-LIBRARIES.txt')
    rr = ['--anchor', Z, '--root', d, '--gate-log', f, '--gate-check-json', f, '--toolchain-json', f,
          '--inventory-json', f, '--judge-json', f, '--image-id', 'x', '--base-image', 'x', '--out',
          os.path.join(t, 'record.json')]
    return {
        'u01': ('tools/ci/inventory.py', ['--help']),
        'u02': ('tools/ci/inventory.py', ['--roo', d]),
        'u03': ('tools/ci/judge_digest.py', ['--help']),
        'u04': ('tools/ci/judge_digest.py', ['--root', d, '--exp', Z]),
        'u05': ('tools/ci/check_gate_log.py', ['--help']),
        'u06': ('tools/ci/check_gate_log.py', ['--log', f, '--fold', 'f32', '--anchor', Z, '--root', ROOT,
                                               '--expected-libs', libs]),
        'u07': ('tools/ci/check_toolchain.py', ['--help']),
        'u08': ('tools/ci/check_toolchain.py', ['--obs', f, '--expected', f]),
        'u09': ('tools/ci/run_record.py', ['--help']),
        'u10': ('tools/ci/run_record.py', ['--fold', 'f32'] + rr),
        'u11': ('tools/ci/verify_records.py', ['--help']),
        'u12': ('tools/ci/verify_records.py', ['--di', d, '--inventory-json', f, '--judge-json', f,
                                               '--toolchain-json', f]),
        'u13': ('tools/ci/read_audit.py', ['--help']),
        'u14': ('tools/ci/read_audit.py', ['--roo', d, '--inventory-json', j]),
        'u15': ('tools/ci/tests/run_all.py', ['--help']),
        'u16': ('tools/ci/tests/run_all.py', ['--image', f]),
        'u17': ('tools/ci/tests/test_check_gate_log.py', ['--help']),
        'u18': ('tools/ci/tests/test_check_gate_log.py', ['--repo']),
        'u19': ('tools/ci/tests/test_check_toolchain.py', ['--help']),
        'u20': ('tools/ci/tests/test_check_toolchain.py', ['--repo']),
        'u21': ('tools/ci/tests/test_workflow_guards.py', ['--help']),
        'u22': ('tools/ci/tests/test_workflow_guards.py', ['--loc']),
    }


def predictions():
    preds, probs = {}, []
    with open(PRED, 'rb') as fh:
        for n, line in enumerate(fh.read().decode('utf-8').split('\n'), 1):
            if not line or line.startswith('#'):
                continue
            parts = line.split(' | ')
            if len(parts) != 4 or parts[0] in preds or parts[2] != 'exit 2':
                probs.append('line %d is not "case | script | exit 2 | what"' % n)
                continue
            preds[parts[0]] = parts[1]
    return preds, probs


def main():
    preds, probs = predictions()
    tmp = tempfile.mkdtemp(prefix='test-usage-')
    results = []
    try:
        os.makedirs(os.path.join(tmp, 'empty'))
        with open(os.path.join(tmp, 'empty.txt'), 'wb'):
            pass
        # a held inventory naming one gated folder, which read_audit.py takes (it refuses any other as a usage error),
        # so that its abbreviated call u14 is one it would run
        with open(os.path.join(tmp, 'object.json'), 'wb') as fh:
            fh.write(b'{"schema": "skuldd-inventory/1", "held": true, "gated": [{"folder": "zz"}], "mirrors": []}\n')
        defined = cases(tmp)
        same = set(defined) == set(preds) and all(preds[k] == defined[k][0] for k in defined)
        results.append(('predictions', not probs and same, '; '.join(probs) if probs else
                        '%d cases, each predicted for its script' % len(defined) if same else
                        'the cases defined here and the predicted ones differ'))
        for cid in sorted(defined):
            script, args = defined[cid]
            try:
                p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, *script.split('/'))] + args, cwd=tmp,
                                   env=ENV, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   timeout=3600)
            except subprocess.TimeoutExpired:
                results.append((cid, False, '%s did not end in time' % script))
                continue
            lines = [x for x in (p.stdout + b'\n' + p.stderr).decode('utf-8', 'replace').replace('\r', '').split('\n')
                     if x.strip()]
            verdicts = [x for x in lines if VERDICT.fullmatch(x)]
            ok = p.returncode == 2 and not verdicts
            results.append((cid, ok, '%s %s: exit %d%s' % (script, ' '.join(args[:2])[:40], p.returncode,
                                                            '; a verdict line: ' + verdicts[0][:60] if verdicts
                                                            else '')))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for cid, ok, detail in results:
        print('  %-12s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    k = sum(1 for r in results if not r[1])
    if k:
        print('TEST usage FAILED: %d of %d cases failed' % (k, len(results)))
        return 1
    print('TEST usage HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
