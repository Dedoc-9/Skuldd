# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_check_boundaries.py: tools/ci/check_boundaries.py, the boundary map's check (ruling BM-2 (a)),
# held on honest inputs and seen to fail on each of its plants; and the Integrity workflow's step that runs it.
# Standard library only (Python 3.12 or later). It writes only in a temporary folder, which it removes.
#
#   python3 -B tools/ci/tests/test_check_boundaries.py
#
# The check cases call the check's own function check() on a root the test writes in a temporary folder: a small
# THEOREMS.md (a proved table of two folders and three statements, one of them a bare name), a small BOUNDARIES.md
# (six rows that use every grade, kind and stage, a PENDING and a STATED row) and three files that its paths name.
# Each plant changes one thing of that root. The module is loaded from tools/ci/check_boundaries.py (no bytecode
# written). The tree's own BOUNDARIES.md is never read here: the cases need maps they can plant (since ruling
# S282-3 (b) it is a judge file, which tools/ci/read_audit.py would accept as a read); the workflow's step runs the
# check on the tree. The CLI cases (U) run check_boundaries.py as a
# process. The workflow cases (W) read .github/workflows/integrity.yml, a judge file: W01 finds in it the step that
# runs the check on every push, and W02 to W04 are plants made in memory from that text.
#
# Cases, one line each, held to tools/ci/tests/PREDICTIONS-check_boundaries.txt, PREDICTIONS-check_boundaries-2.txt
# and PREDICTIONS-check_boundaries-3.txt (each frozen before the first run of its cases; no case id is in two):
# "<case> | <outcome> | <detail> | <what>". HELD: the check holds (exit 0 for a process) and its last line is HELD;
# FAILED: it fails (exit 1 for a process), its last line is FAILED and the rows that fail are exactly those the detail
# names (comma-separated); USAGE: exit 2 and no verdict line; ok (W01): the step is found as the detail says. The
# file's mutant lines ("mutant | <id> | <cases> | <what>") are not read here: they say which cases fail when the check
# named is taken out (tools/ci/check_boundaries.py, or the workflow's step).
# What a pass shows: the check's rows hold on an honest map and each plant turns exactly its rows red; the workflow
# holds the step. What it does not show: the check on the tree's own map (the workflow's step runs it); a link on a
# path (not planted: a link needs a privilege on Windows); that a row of the tree's map is true.
# Last line: "TEST check_boundaries HELD: n of n cases" (exit 0) or "TEST check_boundaries FAILED: k of n cases
# failed" (exit 1); exit 2 on a usage error (this test takes no option).
import importlib.util
import io
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
CHECK = os.path.join(ROOT, 'tools', 'ci', 'check_boundaries.py')
PRED = (os.path.join(HERE, 'PREDICTIONS-check_boundaries.txt'),
        os.path.join(HERE, 'PREDICTIONS-check_boundaries-2.txt'),
        os.path.join(HERE, 'PREDICTIONS-check_boundaries-3.txt'))
WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'integrity.yml')
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
ROW = re.compile(r'  (\S+) +(ok|FAIL)  (.*)')
STEP_NAME = '      - name: The boundary map holds a row for every proved statement (ruling BM-2 (a))'
STEP_IF = '        if: ${{ !cancelled() }}'
STEP_RUN = '        run: python3 -B tools/ci/check_boundaries.py --root "$GITHUB_WORKSPACE"'
SHA_A = 'a' * 64
SHA_B = '0123456789abcdef' * 4

THM = '''<!-- a test tree -->
# Theorems

Prose, with a table that is not the proved one:

| Kind | Count |
|---|---|
| any | 1 |

| Folder | Statement (`MKF.` ...) | Statement file | Closing theorem (`MKF.` ...) | Gate |
|---|---|---|---|---|
| `aa` | `aa.AA_Statement.AA` | `aa/AA_Statement.v` | `aa.Closed.aa_holds` | 1 of 1 |
| `bb` | `bb.BB_Statement.B1`, `B2` | `bb/BB_Statement.v` | `bb.Closed.b1_holds`, `b2_holds` | 2 of 2 |

## Successors

| Old statement | Successor | Relation | What the successor still does not say | Date |
|---|---|---|---|---|
'''

MAP = '''<!-- a test map -->
# Boundaries

Prose before the rows. A list here is not read:

- Claim: `zz.ZZ_Statement.ZZ`
- Grade: PROVEN

## 1. The proved statements

### B001 AA's model
- Claim: `aa.AA_Statement.AA`
- Claimed in: `docs/x.md`
- Stop: a model without overflow
- Kind: model
- Covers beyond: covered by `bb.BB_Statement.B1`
- Grade: GATED
- Proof again: now: B1 is gated in this tree

### B002 B1 and B2's trust
- Claim: `bb.BB_Statement.B1`, `B2`
- Claimed in: `docs/x.md`, `kernel/k/`
- Stop: a stop that goes on
  over two lines
- Kind: trust
- Covers beyond: a run (MEASURED, `kernel/k/rec.txt`); an argument (ARGUED, `docs/x.md`)
- Grade: MEASURED, ARGUED
- Proof again: never: a reason

### B003 a sentence and a record outside the tree
- Claim: a sentence of the documents
- Claimed in: `docs/x.md`
- Stop: one host
- Kind: input class
- Covers beyond: declared in a record kept outside, sha256 SHA_B
- Grade: DECLARED
- Proof again: later: not scheduled

### B004 AA's layer
- Claim: `aa.AA_Statement.AA`
- Claimed in: `docs/x.md`
- Stop: no program
- Kind: layer
- Covers beyond: nothing
- Grade: NOT_MEASURED
- Proof again: Push B or later: a reason

## 2. Pending and stated

### B005 CC, pending
- Claim: PENDING `cc.CC_Statement.CC`: a statement gated outside
- Claimed in: not yet claimed in this tree
- Stop: outside the tree
- Kind: layer
- Covers beyond: its console, sha256 SHA_A
- Grade: MEASURED
- Proof again: Push A: if proved and reviewed

### B006 DD, stated
- Claim: STATED `dd.DD_Statement.DD`
- Claimed in: `docs/x.md`
- Stop: not proven in this tree
- Kind: layer
- Covers beyond: `aa.AA_Statement.AA` covers a layer, and a run (MEASURED, `tools/t.py`)
- Grade: GATED, MEASURED
- Proof again: Push B: a reason
'''.replace('SHA_A', SHA_A).replace('SHA_B', SHA_B)

FILES = {'docs/x.md': b'x\n', 'kernel/k/rec.txt': b'rec\n', 'tools/t.py': b'# t\n'}
HIDDEN = ('### B099 B2, hidden\n- Claim: `bb.BB_Statement.B2`\n- Claimed in: `docs/x.md`\n- Stop: s\n- Kind: model\n'
          '- Covers beyond: nothing\n- Grade: NOT_MEASURED\n- Proof again: never: r\n')


def sub(old, new, count=1):
    def edit(text):
        if text.count(old) != count:
            raise ValueError('the plant text %r occurs %d times, not %d' % (old[:50], text.count(old), count))
        return text.replace(old, new)
    return edit


def chain(*edits):
    def edit(text):
        for e in edits:
            text = e(text)
        return text
    return edit


def row_of(rid):
    """The text of one row of MAP, from its heading to the next heading."""
    i = MAP.index('### %s ' % rid)
    j = MAP.find('\n#', i + 1)
    return MAP[i:j + 1] if j >= 0 else MAP[i:]


def in_row(rid, old, new):
    r = row_of(rid)
    return sub(r, sub(old, new)(r))


def cases():
    """[(id, spec)]; spec keys: map (edit), thm (edit), raw_map (bytes), no_map, map_dir, no_thm, cli (args), wf."""
    c = []

    def add(cid, **spec):
        c.append((cid, spec))
    add('H01')
    add('H02', thm=lambda t: t.replace('\n', '\r\n'))
    add('H03', map=in_row('B001', '- Claim: `aa.', '- Claim: `MKF.aa.'))
    add('H04', map=in_row('B004', '- Stop: no program\n', '- Stop: no program\n\n\n'))
    add('H05', map=in_row('B001', 'covered by `bb.', 'covered by `MKF.bb.'))
    add('H06', map=sub('- Grade: PROVEN\n', '- Grade: PROVEN\n- Kind: anything\n- Proof again: soon\n'))
    add('P01', map=in_row('B002', '`bb.BB_Statement.B1`, `B2`', '`bb.BB_Statement.B1`'))
    add('P02', thm=sub('| 2 of 2 |\n', '| 2 of 2 |\n| `cc` | `cc.CC_Statement.CC` | `cc/CC_Statement.v` | '
                                           '`cc.Closed.cc_holds` | 1 of 1 |\n'))
    add('P03', map=in_row('B001', '- Stop: a model without overflow\n', ''))
    add('P04', map=in_row('B001', '- Kind: model\n', '- Kind:\n'))
    add('P05', map=in_row('B001', '- Grade: GATED\n', '- Grade: -\n'))
    add('P06', map=in_row('B001', '- Stop: a model without overflow\n- Kind: model\n',
                          '- Kind: model\n- Stop: a model without overflow\n'))
    add('P07', map=in_row('B001', '- Grade: GATED\n', '- Grade: GATED\n- Note: one field more\n'))
    add('P08', map=in_row('B001', '- Kind: model\n', '- Kind: model\n- Kind: model\n'))
    add('P09', map=sub('### B002 B1', '### B001 B1'))
    add('P10', map=sub('## 2. Pending and stated\n', '### Notes\n\n## 2. Pending and stated\n'))
    add('P11', map=in_row('B002', '  over two lines\n', '  over two lines\na stray line\n'))
    add('P12', raw_map=b'# Boundaries\n\nNo row yet.\n')
    add('P13', map=in_row('B004', '- Grade: NOT_MEASURED', '- Grade: PROVEN'))
    add('P14', map=in_row('B002', '- Grade: MEASURED, ARGUED', '- Grade: MEASURED,ARGUED'))
    add('P15', map=in_row('B003', '- Grade: DECLARED', '- Grade: declared'))
    add('P16', map=in_row('B002', '- Grade: MEASURED, ARGUED', '- Grade: MEASURED, MEASURED'))
    add('P17', map=in_row('B003', '- Grade: DECLARED', '- Grade: REPORTED'))
    add('P18', map=in_row('B002', '- Kind: trust', '- Kind: assumption'))
    add('P19', map=in_row('B002', '- Kind: trust', '- Kind: trust, model'))
    add('P20', map=in_row('B002', '- Covers beyond: a run (MEASURED, `kernel/k/rec.txt`); an argument (ARGUED, '
                          '`docs/x.md`)', '- Covers beyond: a run on one host, and an argument'))
    add('P21', map=in_row('B001', 'covered by `bb.BB_Statement.B1`', 'covered by `cc.CC_Statement.CC`'))
    add('P22', map=in_row('B005', SHA_A, SHA_A.upper()))
    add('P23', map=in_row('B003', '- Claimed in: `docs/x.md`', '- Claimed in: `docs/y.md`'))
    add('P24', map=in_row('B003', '- Claimed in: `docs/x.md`', '- Claimed in: `docs/../docs/x.md`'))
    add('P25', map=in_row('B003', '- Claimed in: `docs/x.md`', '- Claimed in: `docs/<f>.md`'))
    add('P26', map=in_row('B003', '- Claimed in: `docs/x.md`', '- Claimed in: `/docs/x.md`'))
    add('P27', map=in_row('B002', '(MEASURED, `kernel/k/rec.txt`); an argument (ARGUED, `docs/x.md`)',
                          '(MEASURED, `kernel/k/gone.txt`); an argument (ARGUED)'))
    add('P28', map=in_row('B004', '- Claim: `aa.AA_Statement.AA`', '- Claim: `aa.AA_Statement.AX`'))
    add('P29', map=in_row('B004', '- Claim: `aa.AA_Statement.AA`', '- Claim: `AA`'))
    add('P30', map=in_row('B005', '- Claim: PENDING `cc.CC_Statement.CC`: a', '- Claim: PENDING a'))
    add('P31', map=in_row('B006', '- Claim: STATED `dd.DD_Statement.DD`', '- Claim: STATED `aa.AA_Statement.AA`'))
    add('P32', map=in_row('B003', '- Proof again: later: not', '- Proof again: soon: not'))
    add('P33', map=in_row('B002', '- Proof again: never: a reason', '- Proof again: never:'))
    add('P34', map=in_row('B006', '- Proof again: Push B: a reason', '- Proof again: Push C: a reason'))
    add('P35', map=in_row('B002', '- Proof again: never: a reason', '- Proof again: never - a reason'))
    add('P36', no_map=True)
    add('P37', map_dir=True)
    add('P38', no_thm=True)
    add('P39', thm=sub('| Folder | Statement (', '| Dir | Statement ('))
    add('P40', thm=sub('## Successors\n', '| Folder | Statement |\n|---|---|\n| `ee` | `ee.EE_Statement.EE` |\n\n'
                                          '## Successors\n'))
    add('P41', map=in_row('B003', 'one host', 'one h' + chr(0xF4) + 'st'))
    add('P42', map=in_row('B003', 'one host', 'one\rhost'))
    add('P43', map=in_row('B003', 'one host', 'one\thost'))
    add('P44', raw_map=MAP.encode('utf-8').replace(b'one host', b'one \xffhost'))
    add('P45', thm=sub('| `aa` | `aa.AA_Statement.AA` |', '| `aa` | `AA` |'))
    add('P46', map=sub('## 2. Pending and stated\n', '#### B007 a level-4 row\n\n## 2. Pending and stated\n'))
    add('P47', map=in_row('B004', '- Claim: `aa.AA_Statement.AA`', '- Claim: `aa/AA_Statement.v`'))
    add('P48', map=in_row('B001', '- Kind: model', '- Kind: Model'))
    no_b2 = in_row('B002', '`bb.BB_Statement.B1`, `B2`', '`bb.BB_Statement.B1`')
    add('P49', map=chain(no_b2, sub('## 2. Pending and stated\n',
                                    '## Fenced\n```\n' + HIDDEN + '## end\n```\n\n## 2. Pending and stated\n')))
    add('P50', map=chain(no_b2, sub('## 2. Pending and stated\n',
                                    '## Hidden\n<!--\n' + HIDDEN + '## end\n-->\n\n## 2. Pending and stated\n')))
    add('H07', map=sub('## 2. Pending and stated\n', '## 2. Pending and stated\n<!-- a note -->\n'))
    add('P51', map=chain(no_b2, sub('## 2. Pending and stated\n',
                                    '## Raw\n<div>\n' + HIDDEN + '## end\n</div>\n\n## 2. Pending and stated\n')))
    add('P52', map=chain(no_b2, sub('## 2. Pending and stated\n',
                                    '## Pre\n<pre>\n' + HIDDEN + '\n## end\n</pre>\n\n## 2. Pending and stated\n')))
    add('P53', map=chain(no_b2, sub('## 2. Pending and stated\n',
                                    '## Raw\n   <div>\n' + HIDDEN + '## end\n   </div>\n\n## 2. Pending and stated\n')))
    add('H08', map=in_row('B001', '- Stop: a model without overflow\n', '- Stop: <b>x</b> a model without overflow\n'))
    add('U01', cli=[])
    add('U02', cli=['--root', '.', '--json', 'x'])
    add('U03', cli=['--help'])
    add('U04', cli=['--ro', '.'])
    add('U05', cli=['--root', 'docs/x.md'])
    add('U06', cli=['--root', '.'])
    add('U07', cli=['--root', '.'], map=in_row('B002', '`bb.BB_Statement.B1`, `B2`', '`bb.BB_Statement.B1`'))
    add('W01', wf=None)
    add('W02', wf=sub(STEP_NAME + '\n' + STEP_IF + '\n' + STEP_RUN + '\n', ''))
    add('W03', wf=sub(STEP_RUN, STEP_RUN.replace('"$GITHUB_WORKSPACE"', '.')))
    add('W04', wf=sub(STEP_NAME + '\n' + STEP_IF + '\n', STEP_NAME + '\n'))
    return c


def read_predictions():
    out = {}
    for path in PRED:
        with open(path, 'rb') as fh:
            for raw in fh.read().decode('utf-8').split('\n'):
                line = raw.strip()
                if not line or line.startswith('#') or line.startswith('mutant |'):
                    continue
                parts = [p.strip() for p in line.split(' | ')]
                if len(parts) != 4 or parts[0] in out:
                    raise ValueError('a predictions line that is not "<case> | <outcome> | <detail> | <what>" with a '
                                     'new case: %r' % line[:80])
                out[parts[0]] = (parts[1], parts[2])
    return out


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def make_root(tmp, cid, spec):
    root = os.path.join(tmp, cid)
    os.makedirs(root)
    for rel, data in FILES.items():
        wb(os.path.join(root, *rel.split('/')), data)
    if not spec.get('no_thm'):
        wb(os.path.join(root, 'THEOREMS.md'), spec.get('thm', lambda t: t)(THM).encode('utf-8'))
    if spec.get('map_dir'):
        os.makedirs(os.path.join(root, 'BOUNDARIES.md'))
    elif 'raw_map' in spec:
        wb(os.path.join(root, 'BOUNDARIES.md'), spec['raw_map'])
    elif not spec.get('no_map'):
        wb(os.path.join(root, 'BOUNDARIES.md'), spec.get('map', lambda t: t)(MAP).encode('utf-8'))
    return root


def failed_rows(lines):
    return sorted(m.group(1) for m in (ROW.fullmatch(x) for x in lines) if m and m.group(2) == 'FAIL')


def judge(pred, code, lines):
    """(ok, detail) of a check run: code is 0, 1 or 2 (None when the function was called in this process)."""
    outcome, detail = pred
    verdicts = [x for x in lines if x.startswith('BOUNDARIES HELD') or x.startswith('BOUNDARIES FAILED')]
    last = lines[-1] if lines else ''
    if outcome == 'USAGE':
        ok = code == 2 and not verdicts
        return ok, 'exit %s, %d verdict lines' % (code, len(verdicts))
    if len(verdicts) != 1 or verdicts[0] != last:
        return False, 'exit %s; %d verdict lines; last line: %s' % (code, len(verdicts), last[:100])
    rows = failed_rows(lines)
    if outcome == 'HELD':
        ok = last.startswith('BOUNDARIES HELD') and code in (None, 0) and not rows
        return ok, last
    want = sorted(x.strip() for x in detail.split(','))
    ok = last.startswith('BOUNDARIES FAILED') and code in (None, 1) and rows == want
    return ok, 'failed rows: %s; %s' % (', '.join(rows) or 'none', last)


def load_check():
    spec = importlib.util.spec_from_file_location('check_boundaries_under_test', CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def workflow_problems(text):
    """Problems of the Integrity workflow's text: its one step that runs the check on every push."""
    lines = text.split('\n')
    at = [i for i, x in enumerate(lines) if x == STEP_NAME]
    if len(at) != 1:
        return ['the step "%s" occurs %d times, not once' % (STEP_NAME.strip(), len(at))]
    bad = []
    body = lines[at[0] + 1:at[0] + 3]
    if body[:1] != [STEP_IF]:
        bad.append('the step does not run whatever failed before it (%s)' % STEP_IF.strip())
    if STEP_RUN not in body:
        bad.append('the step does not run: %s' % STEP_RUN.strip())
    runs = [x for x in lines if 'tools/ci/check_boundaries.py' in x and not x.lstrip().startswith('#')]
    if len(runs) != 1:
        bad.append('the workflow runs tools/ci/check_boundaries.py on %d lines (comments aside), not one' % len(runs))
    return bad


def run_case(mod, tmp, cid, spec, pred):
    if 'wf' in spec:
        with open(WORKFLOW, 'rb') as fh:
            text = fh.read().decode('utf-8')
        if spec['wf'] is not None:
            text = spec['wf'](text)
        bad = workflow_problems(text)
        if pred[0] == 'ok':
            return not bad, 'step found' if not bad else bad[0]
        return pred[0] == 'FAILED' and bool(bad), bad[0] if bad else 'no problem found'
    root = make_root(tmp, cid, spec)
    if 'cli' in spec:
        p = subprocess.run([sys.executable, '-B', CHECK] + spec['cli'], cwd=root, env=ENV, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        lines = p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n').rstrip('\n').split('\n')
        return judge(pred, p.returncode, [x for x in lines if x])
    held, lines = mod.check(root)
    return judge(pred, None, lines)


def main(argv):
    if argv:
        sys.stderr.write('test_check_boundaries.py takes no option\n')
        return 2
    try:
        pred = read_predictions()
        mod = load_check()
    except (OSError, ValueError, SyntaxError) as e:
        print('TEST check_boundaries FAILED: the test could not start: %s: %s' % (type(e).__name__, e))
        return 1
    tmp = tempfile.mkdtemp(prefix='test-check-boundaries-')
    failed, n = 0, 0
    try:
        cs = cases()
        names = [cid for cid, _ in cs]
        for cid in sorted(set(names) ^ set(pred)):
            n += 1
            failed += 1
            print('  %s FAIL  %s' % (cid, 'no prediction' if cid in names else 'predicted, but no such case'))
        for cid, spec in cs:
            if cid not in pred:
                continue
            n += 1
            try:
                ok, detail = run_case(mod, tmp, cid, spec, pred[cid])
            except Exception as e:  # a defect of the case itself is a failed case, never a crash of the test
                ok, detail = False, 'the case could not run: %s: %s' % (type(e).__name__, e)
            if not ok:
                failed += 1
            print('  %s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail[:200]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if failed:
        print('TEST check_boundaries FAILED: %d of %d cases failed' % (failed, n))
        return 1
    print('TEST check_boundaries HELD: %d of %d cases' % (n, n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
