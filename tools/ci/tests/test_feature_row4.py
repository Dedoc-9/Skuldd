# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_feature_row4.py: feature row 4 (kernel/hardening/features/feature_row4.py) run on its plants,
# decoys and inputs and on the tree's freeze lists, each result held to the tables P1 and P5 of
# kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md, which were written before any run of feature row 4, and to
# the P1 tables of tools/ci/tests/PREDICTIONS-row4-addendum1.md, PREDICTIONS-row4-addendum2.md,
# PREDICTIONS-row4-addendum3.md and PREDICTIONS-row4-addendum4.md (the plants added after the third, the fourth, the
# fifth and the sixth review, each written before their first run); a case is named in one table only.
# Standard library only (Python 3.12 or later). It writes only in a temporary folder, which it removes.
#
#   python3 -B tools/ci/tests/test_feature_row4.py
#
# Cases, one line each, "  <case> ok|FAIL  <detail>":
#   tables read      both tables are found, every line of them reads as a case (P1: case, arguments, exit,
#                    verdict, failing rows, classes, and in addendum 3 a seventh column, the reported line; P5: list,
#                    root, folder, exit, verdict), and each predictions file gives at least one P1 case (a file whose
#                    P1 heading is misread gives none, and its plants would not run); its detail names each file's
#                    count of cases
#   P1 <case>        feature_row4.py run from kernel/hardening/features with the case's arguments ("(plant)" stands for
#                    "plants4 <case>.v"; "<tmp>" for a temporary folder holding bad4.v, the bytes ff 0a, and
#                    nonascii4.txt, the bytes e9 0a): its exit code, its verdict line ("usage": none), the set of rows
#                    that FAIL and the set of classes on its REFUSED lines are exactly the table's, and where the
#                    seventh column is not "*", the text after "reported, not refused (occurrences): " is exactly it
#   P5 <list>        feature_row4.py <root> --list <root>/<folder>/FROZEN4.txt from the same folder: exit and verdict as
#                    the table says, no row FAIL, no REFUSED line
# What a pass shows: in this run, every plant of feature row 4 is refused for its predicted reason, every decoy and
# honest freeze list holds, and every malformed input fails its input row or is a usage error. What it does not show:
# P2 to P4 of the first file (version 3 against version 4: run where they were recorded; the addendum gives P4's new
# count); a construct no plant holds.
# Last line: "TEST feature_row4 HELD: n of n cases" (exit 0) or "TEST feature_row4 FAILED: k of n cases failed".
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
FEATURES = os.path.join(ROOT, 'kernel', 'hardening', 'features')
PREDICTIONS = (os.path.join(FEATURES, 'PREDICTIONS-row4-2026-11-18.md'),
               os.path.join(HERE, 'PREDICTIONS-row4-addendum1.md'), os.path.join(HERE, 'PREDICTIONS-row4-addendum2.md'),
               os.path.join(HERE, 'PREDICTIONS-row4-addendum3.md'), os.path.join(HERE, 'PREDICTIONS-row4-addendum4.md'))
REPORTED = '    reported, not refused (occurrences): '
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
ROW = re.compile(r'  (\S.*?) +(ok|FAIL)  (.*)')
VERDICT = re.compile(r'(HELD|FAILED) (\d+) of (\d+)')


def tables():
    """([(id, argv, exit, verdict, rows, classes, reported)], problems, {file: counts}) from the P1 and P5 tables;
    reported is '*' (not checked) unless a seventh P1 column gives the reported line's text."""
    lines = []
    for path in PREDICTIONS:
        with open(path, 'rb') as f:
            lines += [(os.path.basename(path), n, x) for n, x in enumerate(f.read().decode('utf-8').split('\n'), 1)]
    cases, problems, section, seen, current = [], [], None, {'P1': 0, 'P5': 0}, None
    per_file = dict((os.path.basename(p), {'P1': 0, 'P5': 0}) for p in PREDICTIONS)
    for fname, n, line in lines:
        if fname != current:
            section, current = None, fname
        if line.startswith('## '):
            section = line[3:5] if line[3:5] in ('P1', 'P5') else None
            continue
        if section is None or not line.startswith('|') or line.startswith('|---') or line.startswith('| case |') \
                or line.startswith('| list |'):
            continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        seen[section] += 1
        if section == 'P1' and len(c) in (6, 7):
            case, args, code, verdict, rows, classes = c[:6]
            reported = c[6] if len(c) == 7 else '*'
            per_file[fname]['P1'] += 1
            argv = ['plants4', case + '.v'] if args == '(plant)' else args.strip('`').split()
            want_rows = set() if rows == '-' else set((case + '.v') if r.strip() == '(plant)' else r.strip()
                                                      for r in rows.split(';'))
            want_cls = set() if classes == '-' else set(x.strip() for x in classes.split(';'))
            cases.append(('P1 ' + case, argv, code, verdict, want_rows, want_cls, reported))
        elif section == 'P5' and len(c) == 5:
            name, root, folder, code, verdict = c
            per_file[fname]['P5'] += 1
            cases.append(('P5 ' + name, [root, '--list', '%s/%s/FROZEN4.txt' % (root, folder)], code, verdict,
                          set(), set(), '*'))
        else:
            problems.append('%s line %d of the %s table is not read' % (fname, n, section))
    for s in ('P1', 'P5'):
        if not seen[s]:
            problems.append('no %s table' % s)
    problems += ['%s gives no P1 case' % f for f, k in per_file.items() if not k['P1']]
    ids = [c[0] for c in cases]
    problems += ['%s is named twice' % x for x in sorted(set(x for x in ids if ids.count(x) > 1))]
    return cases, problems, per_file


def run_case(argv, tmp):
    argv = [a.replace('<tmp>', tmp) for a in argv]
    p = subprocess.run([sys.executable, '-B', 'feature_row4.py'] + argv, cwd=FEATURES, env=ENV,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
    return p.returncode, [x.rstrip('\r') for x in p.stdout.decode('utf-8', 'replace').split('\n')]


def judge(code, lines, want_code, want_verdict, want_rows, want_cls, want_rep='*'):
    got_rows = set(m.group(1).strip() for m in (ROW.fullmatch(x) for x in lines) if m and m.group(2) == 'FAIL')
    got_cls = set(re.sub(r' \(.*\)$', '', x.split(': ', 1)[1]) for x in lines
                  if x.startswith('    REFUSED ') and ': ' in x)
    verdicts = [x for x in lines if x.startswith('FEATURE ROW 4 ')]
    if want_verdict == 'usage':
        vok = not verdicts
    else:
        m = VERDICT.fullmatch(want_verdict)
        want = None if not m else ('FEATURE ROW 4 HELD: %s of %s rows' % (m.group(2), m.group(3)) if m.group(1) ==
                                   'HELD' else 'FEATURE ROW 4 FAILED: %s of %s rows failed' % (m.group(2), m.group(3)))
        vok = want is not None and verdicts == [want]
    reps = [x[len(REPORTED):] for x in lines if x.startswith(REPORTED)]
    rok = want_rep == '*' or reps == [want_rep]
    ok = str(code) == want_code and vok and got_rows == want_rows and got_cls == want_cls and rok
    return ok, 'exit %d; %s; failing rows %s; classes %s%s' % (code, verdicts[0] if verdicts else 'no verdict line',
                                                              '; '.join(sorted(got_rows)) or '-',
                                                              '; '.join(sorted(got_cls)) or '-',
                                                              '' if want_rep == '*' else '; reported %s'
                                                              % ('; '.join(reps) or '-'))


def main():
    cases, problems, per_file = tables()
    counts = ', '.join('%s %d' % (f, k['P1'] + k['P5']) for f, k in per_file.items())
    results = [('tables read', not problems, '; '.join(problems) + ' (cases: %s)' % counts if problems else
                '%d cases: %s' % (len(cases), counts))]
    tmp = tempfile.mkdtemp(prefix='test-row4-')
    try:
        with open(os.path.join(tmp, 'bad4.v'), 'wb') as f:
            f.write(b'\xff\n')
        with open(os.path.join(tmp, 'nonascii4.txt'), 'wb') as f:
            f.write(b'\xe9\n')
        for cid, argv, code, verdict, rows, cls, rep in cases:
            got, lines = run_case(argv, tmp)
            ok, det = judge(got, lines, code, verdict, rows, cls, rep)
            results.append((cid, ok, det))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for cid, ok, det in results:
        print('  %-50s %s  %s' % (cid, 'ok' if ok else 'FAIL', det))
    failed = sum(1 for r in results if not r[1])
    if failed:
        print('TEST feature_row4 FAILED: %d of %d cases failed' % (failed, len(results)))
        return 1
    print('TEST feature_row4 HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
