# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_workflow_pins.py: what the workflows' headers declare about themselves, held as rows on the
# workflow text and seen to fail on plants (ruling SY-2). Standard library only (Python 3.12 or later). It reads the
# workflows and its predictions only, and writes nothing.
#
#   python3 -B tools/ci/tests/test_workflow_pins.py
#
# Rows, on every .github/workflows/*.yml and *.yaml (read as text, line by line, in the style these files are written;
# it is no YAML parser):
#   pins           every "uses:" names owner/repo[/path]@<40 hex> # v<version>, and the pair is one of the five that
#                  the hardening batch pinned under ruling SK-1 (checkout and cache moved from @v4 to commit shas;
#                  upload-artifact and download-artifact, GitHub's own, each by full commit sha)
#   permissions    each workflow's top-level permissions are exactly "contents: read" (one line "permissions:" at
#                  the top, and under it, blank and comment lines aside, the one line "  contents: read"), and no job
#                  or step sets any: no line but the top-level one names permissions outside a comment, as written
#                  (a key, quoted or not, or one inside a flow mapping)
#   triggers       no line outside a comment names pull_request_target or workflow_run as written, in any form "on:"
#                  takes (a mapping key, a flow or block sequence, a scalar)
#                  Both rows read the names as written: a name spelled with an escape of a double-quoted scalar (a hex
#                  or Unicode escape of one of its characters, or an escaped line break) is not read, though GitHub
#                  reads it as the name. A line that holds a quote mark (" or ') is read whole, a "#" in it included,
#                  since a quoted scalar may hold " #" (so a name in a comment on such a line fails the row); any
#                  other line is not read when its text starts with "#", and otherwise is read up to its first " #":
#                  on a line with no quote mark, that "#" starts a comment or is inside a scalar that spans lines,
#                  where a name after it is no key and not the whole scalar (argued from YAML 1.2, not run on GitHub).
#                  A line here ends at a line feed only, so a workflow that holds a carriage return (one before a
#                  line feed aside), U+0085, U+2028 or U+2029, where a YAML reader may end a line, fails both rows
#                  (the other rows also end a line at a line feed only; such a file fails the test through these two)
#   credentials    every actions/checkout step sets persist-credentials: false
#   env-only       no "${{" inside a run: block (values reach scripts through env)
#   drift-matrix   drift.yml's matrix holds exactly the parts orlog and verdandi, each fetching the repository that
#                  PROVENANCE.md's table names for it (written below, in REPOSITORIES: this test does not read
#                  PROVENANCE.md, which no judge group, freeze list or manifest binds, so tools/ci/read_audit.py would
#                  refuse the read; the drift workflow's run of tools/ci/drift.py fails row D1 when the clone it
#                  fetched does not hold the pins PROVENANCE.md names)
#   drift-actions  drift.yml's only action is actions/checkout
# Cases, held to tools/ci/tests/PREDICTIONS-workflow_pins.txt and PREDICTIONS-workflow_pins-2.txt to -5.txt (each
# frozen before this test's first run of its cases; -4.txt's W24 to W26 and -5.txt's W28 to W30 first ran in
# reviewers' trials on scratch copies, each held to the same outcomes and rows in a file it froze before that run;
# -6.txt holds a dated note on -5.txt and no case): the honest text, and plants and decoys made in memory.
# What a pass shows: the text holds these rules. What it does not show: GitHub's reading of the YAML; that an allowed
# sha is the release its tag names (the push restatement names each action and its sha, as SK-1 asks); a step this
# reading misses.
# Last line: "TEST workflow_pins HELD: n of n cases" (exit 0) or "TEST workflow_pins FAILED: k of n cases failed"
# (exit 1); exit 2 on a usage error (this test takes no option).
import os
import re
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRED = (os.path.join(HERE, 'PREDICTIONS-workflow_pins.txt'), os.path.join(HERE, 'PREDICTIONS-workflow_pins-2.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_pins-3.txt'), os.path.join(HERE, 'PREDICTIONS-workflow_pins-4.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_pins-5.txt'), os.path.join(HERE, 'PREDICTIONS-workflow_pins-6.txt'))
WF = os.path.join(ROOT, '.github', 'workflows')
ALLOWED = {  # ruling SK-1: GitHub's own actions, each by full commit sha, its release tag beside it
    ('actions/checkout', '11d5960a326750d5838078e36cf38b85af677262', 'v4.4.0'),
    ('actions/cache', '0057852bfaa89a56745cba8c7296529d2fc39830', 'v4.3.0'),
    ('actions/cache/restore', '0057852bfaa89a56745cba8c7296529d2fc39830', 'v4.3.0'),
    ('actions/upload-artifact', 'ea165f8d65b6e75b540449e92b4886f43607fa02', 'v4.6.2'),
    ('actions/download-artifact', 'd3f86a106a0bac45b974a628896c90dbdf5c8093', 'v4.3.0'),
}
REPOSITORIES = {'orlog': 'Dedoc-9/Orlog', 'verdandi': 'Dedoc-9/Verdandi'}  # PROVENANCE.md's table
USES = re.compile(r'^(\s*)(?:- )?uses: (\S+)(.*)$')
PIN = re.compile(r'([a-z0-9-]+/[a-z0-9._-]+(?:/[a-z0-9._-]+)*)@([0-9a-f]{40})$')
TAG = re.compile(r' # (v[0-9]+\.[0-9]+\.[0-9]+)$')
ROWS = ('pins', 'permissions', 'triggers', 'credentials', 'env-only', 'drift-matrix', 'drift-actions')


def indent(line):
    return len(line) - len(line.lstrip(' '))


def judge(texts):
    """{row: [problems]} on {name: text}."""
    bad = {r: [] for r in ROWS}
    for name, text in sorted(texts.items()):
        lines = text.split('\n')
        if re.search('[\r\x85\u2028\u2029]', text):  # a YAML reader may end a line there; this one does not
            for r in ('permissions', 'triggers'):
                bad[r].append('%s holds a carriage return, U+0085, U+2028 or U+2029' % name)
        top = [i for i, x in enumerate(lines) if x.startswith('permissions:')]
        body, j = [], (top[0] + 1 if top else len(lines))
        while j < len(lines) and (not lines[j].strip() or lines[j].startswith((' ', '#'))):
            if lines[j].strip() and not lines[j].lstrip().startswith('#'):
                body.append(lines[j])
            j += 1
        if len(top) != 1 or lines[top[0]].strip() != 'permissions:' or body != ['  contents: read']:
            bad['permissions'].append('%s: top-level permissions are not exactly contents: read' % name)
        for i, x in enumerate(lines):
            s = x.strip()
            code = x if ('"' in x or "'" in x) else ('' if s.startswith('#') else x.split(' #', 1)[0])
            if i not in top and re.search(r'(?<![A-Za-z0-9_-])permissions(?![A-Za-z0-9_-])', code):
                bad['permissions'].append('%s line %d names permissions below the top' % (name, i + 1))
            if re.search(r'(?<![A-Za-z0-9_-])(pull_request_target|workflow_run)(?![A-Za-z0-9_-])', code):
                bad['triggers'].append('%s line %d: %s' % (name, i + 1, s[:40]))
            m = USES.match(x)
            if m:
                pin, tag = PIN.match(m.group(2)), TAG.match(m.group(3))
                if not pin or not tag or (pin.group(1), pin.group(2), tag.group(1)) not in ALLOWED:
                    bad['pins'].append('%s line %d: %s%s' % (name, i + 1, m.group(2)[:70], m.group(3)[:20]))
                if name == 'drift.yml' and not m.group(2).startswith('actions/checkout@'):
                    bad['drift-actions'].append('drift.yml line %d uses %s' % (i + 1, m.group(2)[:70]))
                if m.group(2).startswith('actions/checkout@'):
                    j, ok = i + 1, False
                    while j < len(lines) and (not lines[j].strip() or indent(lines[j]) > indent(x) or
                                              (indent(lines[j]) == indent(x) and not lines[j].lstrip().startswith('-')
                                               and not x.lstrip().startswith('-'))):
                        if lines[j].strip() == 'persist-credentials: false':
                            ok = True
                        j += 1
                    if not ok:
                        bad['credentials'].append('%s line %d: a checkout without persist-credentials: false'
                                                  % (name, i + 1))
            r = re.match(r'^(\s*)(?:- )?run:(.*)$', x)
            if r:
                block = [r.group(2)]
                j = i + 1
                while j < len(lines) and (not lines[j].strip() or indent(lines[j]) > indent(x)):
                    block.append(lines[j])
                    j += 1
                if any('${{' in b for b in block):
                    bad['env-only'].append('%s line %d: an expression inside a run: block' % (name, i + 1))
    drift = texts.get('drift.yml')
    if drift is None:
        bad['drift-matrix'].append('drift.yml is missing')
        bad['drift-actions'].append('drift.yml is missing')
    else:
        parts = re.findall(r'^\s+- part: (\S+)\n\s+repository: (\S+)$', drift, re.M)
        if sorted(p for p, _ in parts) != sorted(REPOSITORIES) or any(REPOSITORIES.get(p) != r for p, r in parts):
            bad['drift-matrix'].append('drift.yml matrix %s; PROVENANCE.md names %s'
                                       % (parts, sorted(REPOSITORIES.items())))
    return bad


def cases(texts):
    mk, dr = 'mathkernel-linux.yml', 'drift.yml'
    on = "on:\n  push:\n  pull_request:\n  schedule:\n    - cron: '41 5 * * 1'\n  workflow_dispatch:\n"
    ck = 'actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0'
    up = 'actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2'
    # drift.yml's job-level line, after which W21 to W23, W27, W28 and W30 to W32 add theirs
    job = '    timeout-minutes: 15\n'

    def sub(name, old, new, count=1):
        t = texts[name]
        if t.count(old) < 1:
            raise RuntimeError('plant text not found in %s: %r' % (name, old[:40]))
        return dict(texts, **{name: t.replace(old, new, count)})
    return {
        'W00': texts,
        'W01': sub(mk, ck, 'actions/checkout@v4'),
        'W02': sub(mk, ck, 'actions/checkout@' + 'a' * 40 + ' # v4.4.0'),
        'W03': sub(mk, ck, ck.split(' #')[0]),
        'W04': sub(mk, '    runs-on: ubuntu-24.04\n', '    runs-on: ubuntu-24.04\n    permissions: write-all\n'),
        'W05': sub(dr, 'permissions:\n  contents: read\n', 'permissions:\n  contents: write\n'),
        'W06': sub(dr, 'on:\n  push:\n', 'on:\n  pull_request_target:\n  push:\n'),
        'W07': sub(dr, '          path: skuldd\n          persist-credentials: false\n', '          path: skuldd\n'),
        'W08': sub(dr, 'python3 -B skuldd/tools/ci/tests/test_drift.py',
                   'python3 -B skuldd/tools/ci/tests/test_drift.py ${{ github.sha }}'),
        'W09': sub(dr, 'repository: Dedoc-9/Verdandi', 'repository: someone/Verdandi'),
        'W10': sub(dr, '          - part: orlog\n            repository: Dedoc-9/Orlog\n', ''),
        'W11': sub(dr, '        env:\n          PART: ${{ matrix.part }}\n',
                   '        env:\n          PART: ${{ matrix.part }}\n          SHA: ${{ github.sha }}\n'),
        'W12': sub(mk, '        with:\n          persist-credentials: false\n'
                       "      - name: mk_fpenv's self-test, plants and mutants with GCC and clang\n",
                   "      - name: mk_fpenv's self-test, plants and mutants with GCC and clang\n"),
        'W13': sub(dr, '      - name: The drift report in the job summary\n',
                   '      - uses: %s\n        with:\n          name: drift\n          path: drift.txt\n'
                   '      - name: The drift report in the job summary\n' % up),
        'W14': sub(dr, on, 'on: [push, pull_request_target]\n'),
        'W15': sub(dr, on, 'on: workflow_run\n'),
        'W16': sub(dr, on, 'on:\n  - push\n  - pull_request_target\n'),
        'W17': sub(dr, 'permissions:\n  contents: read\n', 'permissions:\n  contents: read\n\n  id-token: write\n'),
        'W18': sub(dr, 'on:\n  push:\n', 'on:\n  push:  # never pull_request_target\n'),
        'W19': sub(dr, 'permissions:\n  contents: read\n', 'permissions:\n  contents: read\n\n  # read only\n'),
        'W20': dict(texts, **{dr: '# not on workflow_run\n' + texts[dr]}),
        'W21': sub(dr, job, job + '    "permissions": write-all\n'),
        'W22': sub(dr, job, job + "    'permissions': write-all\n"),
        'W23': sub(dr, job, job + '    # no permissions here\n'),
        'W24': dict(texts, **{dr: texts[dr] + '  evil: {runs-on: ubuntu-24.04, name: "a #", permissions: write-all, '
                                              'steps: [{run: echo}]}\n'}),
        'W25': dict(texts, **{dr: texts[dr] + '  evil: {runs-on: ubuntu-24.04, name: "a\n    #b", permissions: '
                                              'write-all, steps: [{run: echo}]}\n'}),
        'W26': sub(dr, on, 'on: {push: {branches: ["main #"]}, pull_request_target: {}}\n'),
        'W27': sub(dr, job, job + "    # the job's permissions\n"),
        'W28': sub(dr, job, job + '    # x\r    permissions: write-all\n'),
        'W29': sub(dr, 'on:\n  push:\n', 'on:\n  push: # x\r  pull_request_target:\n'),
        'W30': sub(dr, job, job + '    # x\u2028    permissions: write-all\n'),
        'W31': sub(dr, job, job + '    # x\x85    permissions: write-all\n'),
        'W32': sub(dr, job, job + '    # x\u2029    permissions: write-all\n'),
        'W33': sub(dr, '      - name: The drift report in the job summary\n',
                   '      # x\r      - uses: someone/action@main\n      - name: The drift report in the job summary\n'),
    }


def main(argv):
    if argv:
        sys.stderr.write('test_workflow_pins.py: usage error: this test takes no option\n')
        return 2
    texts = {}
    for f in sorted(os.listdir(WF)):
        if f.lower().endswith(('.yml', '.yaml')):
            with open(os.path.join(WF, f), 'rb') as fh:
                texts[f] = fh.read().decode('utf-8').replace('\r\n', '\n')
    preds, probs = {}, []
    for path in PRED:
        with open(path, 'rb') as fh:
            for n, line in enumerate(fh.read().decode('utf-8').split('\n'), 1):
                if not line or line.startswith('#'):
                    continue
                p = line.split(' | ')
                if len(p) != 4 or p[1] not in ('HELD', 'FAILED') or p[0] in preds:
                    probs.append('%s line %d is not "id | HELD or FAILED | rows | what" with a new id'
                                 % (os.path.basename(path), n))
                    continue
                preds[p[0]] = (p[1], set() if p[2] == '-' else set(p[2].split(',')))
    results = []
    try:
        defined = cases(texts)
    except (KeyError, RuntimeError) as e:
        print('  %-12s FAIL  a plant could not be made: %s' % ('plants', str(e)[:160]))
        print('TEST workflow_pins FAILED: 1 of 1 cases failed')
        return 1
    results.append(('predictions', not probs and set(defined) == set(preds),
                    '; '.join(probs) or '%d cases, each predicted' % len(defined)))
    for cid in sorted(defined):
        if cid not in preds:
            continue
        bad = judge(defined[cid])
        failing = {r for r in ROWS if bad[r]}
        want_verdict, want_rows = preds[cid]
        ok = failing == want_rows and (want_verdict == 'HELD') == (not failing)
        why = '' if ok else ' (predicted %s); %s' % (','.join(sorted(want_rows)) or '-',
                                                     '; '.join(sum(bad.values(), []))[:200])
        results.append((cid, ok, 'rows failing: %s%s' % (','.join(sorted(failing)) or '-', why)))
    for cid, ok, detail in results:
        print('  %-12s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    k = sum(1 for r in results if not r[1])
    if k:
        print('TEST workflow_pins FAILED: %d of %d cases failed' % (k, len(results)))
        return 1
    print('TEST workflow_pins HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
