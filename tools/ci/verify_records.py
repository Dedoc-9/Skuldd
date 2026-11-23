# SPDX-License-Identifier: AGPL-3.0-only
# The verdict over every folder gate's run record of one CI run. Standard library only (Python 3.12 or later).
#
#   python3 -B tools/ci/verify_records.py --dir D --inventory-json F --judge-json F --toolchain-json F [--out FILE]
#
# The job "MathKernel verdict" of .github/workflows/mathkernel-linux.yml runs it after every other job, on the records
# that tools/ci/run_record.py wrote (downloaded into D) and on the inventory, CI judge and toolchain JSON of the same
# run. It also reads GITHUB_SHA, GITHUB_RUN_ID, GITHUB_REPOSITORY, GITHUB_REF and GITHUB_WORKFLOW_REF from the
# environment. Every file under D (at any depth) must be a record: D holds nothing else, and a folder under D that
# cannot be listed fails the records row (on Windows a name ending in a dot or a blank is opened as its twin, so a
# local run there does not judge it; the verdict job runs on Linux, where such a name is its own file). Rows:
#   records      D is a folder holding at least one file, and every file under it is a record: strict UTF-8 JSON, no
#                key twice, exactly the record's keys, schema "skuldd-mathkernel-run-record/1", every value well formed
#   shared       the records name one commit, tree, kernel_tree, workflow_blob, workflow_sha256, run_id, run_attempt,
#                repository, ref, workflow_ref, image_id, base_image, toolchain_digest, inventory_digest and
#                judge_digest
#   run          those are this run's: commit, run_id, repository, ref and workflow_ref equal the environment's
#   inventory    the inventory JSON (schema skuldd-inventory/1) is HELD, its digest is the sha256 of its own gated,
#                mirrors and gate_dir_files, it names no folder twice, and its digest is every record's
#   judge        the CI judge JSON (schema skuldd-ci-judge/1) is HELD, was given an expected digest equal to its own
#                (expect is its digest; in the workflow that value is MK_ANCHOR_CI's, which this script does not
#                read), its digest is the sha256 of its own file list and inventory digest, that inventory
#                digest is the inventory JSON's, the sha256 it lists for .github/workflows/mathkernel-linux.yml is
#                every record's workflow_sha256, and its digest is every record's
#   toolchain    the toolchain JSON (schema skuldd-toolchain/1) is HELD, and its digest is every record's
#   folders      one record per gated folder of the inventory: none missing, none extra, none twice
#   anchors      each record's anchor is its frozen4_sha256 and the inventory's sha256 of that folder's FROZEN4.txt
#   gates        each record's gate verdict line is "<NAME> GATE4 HELD: n of n  [anchor <16>]", n at least 1, the 16
#                digits its frozen4_sha256's first
#   gate checks  each record's log check verdict is "GATE LOG HELD: n of n rows" with n exactly GATE_LOG_ROWS, the
#                number of rows tools/ci/check_gate_log.py prints (15; tools/ci/tests/test_records.py compares the two)
#   summary      (with --out) FILE written
# A row over the records fails when there is no readable record: nothing is held over an empty set.
# --out FILE: run-summary.json, keys sorted: every record's file, folder, anchor and verdict lines, the files that are
# not records, the shared values (null where the records differ), the input digests, every row and the verdict. It is
# written whatever the verdict, never over an existing file (usage error, exit 2), and never inside D.
# What a pass shows: one run of one commit gated every folder the inventory found, each with its anchor, each gate and
# its log check HELD, under one workflow, image, toolchain and CI judge, the judge equal to the expected digest it was
# given (in the workflow, the value of MK_ANCHOR_CI).
# What it does not show: anything the records do not hold (they are read, not remade: run_record.py made them in the
# gate jobs); that MK_ANCHOR_CI or a folder's anchor is right (the owner's values); that the run's own scripts were
# the reviewed ones beyond what MK_ANCHOR_CI binds. run_attempt is compared between the records, not with this job's
# environment (a re-run of this job alone carries another attempt number); records of two attempts fail "shared".
# The row label "judge: HELD, = MK_ANCHOR_CI, every record's" keeps the words of its first version, which the test's
# frozen predictions name: the expected digest is the one the judge JSON was given (in the workflow, the value of
# MK_ANCHOR_CI; this script never reads the variable).
# Last line: "RUN RECORDS HELD: n of n rows" (exit 0) or "RUN RECORDS FAILED: k of n rows failed" (exit 1); exit 2 on
# a usage error (an unknown or abbreviated option, --help among them, an existing --out or one inside --dir).
import argparse
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')   # the same bytes on Windows as on Linux
except Exception:
    pass

NAME = 'RUN RECORDS'
SCHEMA = 'skuldd-mathkernel-run-record/1'
SUMMARY_SCHEMA = 'skuldd-mathkernel-run-summary/1'
WORKFLOW = '.github/workflows/mathkernel-linux.yml'
MAX_BYTES = 1 << 20
HEX64 = re.compile(r'[0-9a-f]{64}')
OID = re.compile(r'[0-9a-f]{40}|[0-9a-f]{64}')
FOLDER = re.compile(r'[a-z][a-z0-9_]*')   # the inventory's folder names
# The record's keys and the form of each value (every value is a string).
FORMS = {
    'schema': re.compile(re.escape(SCHEMA)),
    'commit': OID, 'tree': OID, 'kernel_tree': OID, 'workflow_blob': OID,
    'workflow_sha256': HEX64, 'anchor': HEX64, 'frozen4_sha256': HEX64, 'toolchain_digest': HEX64,
    'library_map_digest': HEX64, 'inventory_digest': HEX64, 'judge_digest': HEX64, 'gate_log_sha256': HEX64,
    'run_id': re.compile(r'[1-9][0-9]{0,19}'),
    'run_attempt': re.compile(r'[1-9][0-9]{0,5}'),
    'repository': re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'),
    'ref': re.compile(r'refs/[^\s]+'),
    'workflow_ref': re.compile(r'[^\s@]+@refs/[^\s]+'),
    'folder': FOLDER,
    'image_id': re.compile(r'sha256:[0-9a-f]{64}'),
    'base_image': re.compile(r'[^\s@]+@sha256:[0-9a-f]{64}'),
    'gate_verdict_line': re.compile(r'[^\n\r]*GATE4 (?:HELD|FAILED):[^\n\r]*'),
    'gate_check_verdict': re.compile(r'GATE LOG (?:HELD|FAILED): [^\n\r]*'),
}
SHARED = ('commit', 'tree', 'kernel_tree', 'workflow_blob', 'workflow_sha256', 'run_id', 'run_attempt', 'repository',
          'ref', 'workflow_ref', 'image_id', 'base_image', 'toolchain_digest', 'inventory_digest', 'judge_digest')
ENV_OF = (('commit', 'GITHUB_SHA'), ('run_id', 'GITHUB_RUN_ID'), ('repository', 'GITHUB_REPOSITORY'),
          ('ref', 'GITHUB_REF'), ('workflow_ref', 'GITHUB_WORKFLOW_REF'))
GATE_HELD = re.compile(r'(\S+) GATE4 HELD: (\d+) of (\d+)  \[anchor ([0-9a-f]{16})\]')
CHECK_HELD = re.compile(r'GATE LOG HELD: (\d+) of (\d+) rows')
# The number of rows tools/ci/check_gate_log.py prints (its NAMES); tools/ci/tests/test_records.py compares this
# value with the count that script prints, so a log check of another version, with other rows, is refused.
GATE_LOG_ROWS = 15
# The other scripts' JSON, and what is read from each.
INVENTORY_SCHEMA = 'skuldd-inventory/1'
INVENTORY_KEYS = ('gated', 'mirrors', 'gate_dir_files')
INVENTORY_HELD = 'INVENTORY HELD: '
JUDGE_SCHEMA = 'skuldd-ci-judge/1'
JUDGE_HELD = 'CI JUDGE HELD: '
TOOLCHAIN_SCHEMA = 'skuldd-toolchain/1'
TOOLCHAIN_HELD = 'TOOLCHAIN HELD: '


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def no_duplicates(pairs):
    keys = [k for k, _ in pairs]
    twice = sorted({k for k in keys if keys.count(k) > 1})
    if twice:
        raise ValueError('a key is given twice: %s' % ', '.join(twice))
    return dict(pairs)


def no_constant(name):
    raise ValueError('%s is not JSON' % name)


def linked(p):
    """True for a symbolic link, and for a junction (Windows), which os.path.islink does not call a link and os.walk
    enters."""
    return os.path.islink(p) or os.path.isjunction(p)


def load_json(path, label):
    """(object, '') or (None, why): a regular file of at most 1 MiB, strict UTF-8, no key twice, no NaN, an object."""
    try:
        if linked(path) or not os.path.isfile(path):
            return None, '%s is not a regular file' % label
        if os.path.getsize(path) > MAX_BYTES:
            return None, '%s is larger than %d bytes' % (label, MAX_BYTES)
        with open(path, 'rb') as fh:
            b = fh.read()
    except OSError as e:
        return None, '%s cannot be read (%s)' % (label, e.strerror or type(e).__name__)
    try:
        obj = json.loads(b.decode('utf-8'), object_pairs_hook=no_duplicates, parse_constant=no_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as e:
        return None, '%s is not strict JSON (%s)' % (label, str(e)[:120])
    if not isinstance(obj, dict):
        return None, '%s is not a JSON object' % label
    return obj, ''


def record_problems(obj):
    """What keeps a parsed object from being a record (empty when it is one)."""
    bad = []
    keys = set(obj)
    missing, extra = sorted(set(FORMS) - keys), sorted(keys - set(FORMS))
    if missing:
        bad.append('lacks %s' % ', '.join(missing))
    if extra:
        bad.append('has keys no record has: %s' % ', '.join(k[:40] for k in extra[:6]))
    for k in sorted(keys & set(FORMS)):
        val = obj[k]
        if not isinstance(val, str) or not FORMS[k].fullmatch(val):
            bad.append('%s is not well formed: %r' % (k, str(val)[:80]))
    return bad


class Rows:
    def __init__(self):
        self.rows = []

    def run(self, name, fn):
        try:
            ok, detail = fn()
        except Exception as e:  # a row that cannot be computed fails; it never passes silently
            ok, detail = False, 'error: %s: %s' % (type(e).__name__, str(e)[:160])
        self.rows.append({'name': name, 'ok': bool(ok), 'detail': detail})
        print('  %-58s %s  %s' % (name, 'ok' if ok else 'FAIL', detail))
        sys.stdout.flush()
        return bool(ok)

    def failed(self):
        return sum(1 for r in self.rows if not r['ok'])


def verdict_line(n, k):
    return '%s FAILED: %d of %d rows failed' % (NAME, k, n) if k else '%s HELD: %d of %d rows' % (NAME, n, n)


def parse_args(argv):
    ap = argparse.ArgumentParser(prog='verify_records.py', allow_abbrev=False, add_help=False,
                                 description='Judge every run record of one CI run (see the header).')
    for opt in ('--dir', '--inventory-json', '--judge-json', '--toolchain-json'):
        ap.add_argument(opt, required=True)
    ap.add_argument('--out')
    return ap.parse_args(argv)


def plain(path):
    """A path with a Windows long-path or device prefix (\\\\?\\, \\\\?\\UNC\\, \\\\.\\) taken off, and on POSIX a
    leading "//" read as "/" (tools/ci/read_audit.py's rule, copied), so that a path spelled with one is compared as
    the path it names."""
    if path.startswith('\\\\?\\UNC\\'):
        return '\\\\' + path[8:]
    if path.startswith('\\\\?\\') or path.startswith('\\\\.\\'):
        return path[4:]
    if os.name != 'nt' and path.startswith('//') and not path.startswith('///'):
        return path[1:]
    return path


def inside(path, folder):
    """True when path is folder or under it, both resolved first (a volume GUID path becomes its drive's form; a
    long-path prefix given is kept), then the prefix taken off."""
    try:
        p = os.path.normcase(plain(os.path.realpath(os.path.abspath(path))))
        f = os.path.normcase(plain(os.path.realpath(os.path.abspath(folder))))
        return os.path.commonpath([p, f]) == f
    except ValueError:  # another drive
        return False


def main(argv):
    a = parse_args(argv)
    if a.out is not None:
        if os.path.lexists(a.out):
            print('verify_records.py: %s exists; a summary is never overwritten' % a.out, file=sys.stderr)
            return 2
        if inside(a.out, a.dir):
            print('verify_records.py: --out is inside --dir, where every file must be a record', file=sys.stderr)
            return 2
    rows = Rows()
    records = []     # (file, record), sorted by file
    unreadable = []  # {file, why}
    inputs = {}      # the parsed JSON files

    def read_records():
        if not os.path.isdir(a.dir):
            return False, '--dir is not a folder'
        files = []
        errors = []  # folders os.walk could not list (by default it skips them, and their files go unjudged)
        for dp, dn, fn in os.walk(a.dir, onerror=errors.append):
            # a linked folder (a symbolic link, or a junction) is not walked; it is listed as a file, which no record
            # can be
            fn = fn + [d for d in dn if linked(os.path.join(dp, d))]
            dn[:] = sorted(d for d in dn if not linked(os.path.join(dp, d)))
            for f in fn:
                full = os.path.join(dp, f)
                files.append((os.path.relpath(full, a.dir).replace(os.sep, '/'), full))
        if not files and not errors:
            return False, 'no file under --dir'
        for rel, full in sorted(files):
            obj, why = load_json(full, rel)
            bad = [why] if obj is None else record_problems(obj)
            if bad:
                unreadable.append({'file': rel, 'why': '; '.join(bad)[:400]})
            else:
                records.append((rel, obj))
        if errors:
            return False, '%d folder(s) under --dir cannot be listed: %s' % (
                len(errors), '; '.join(sorted(str(getattr(e, 'filename', None) or e) for e in errors))[:400])
        if unreadable:
            return False, '%d of %d files are not records: %s' % (
                len(unreadable), len(files), '; '.join('%s: %s' % (u['file'], u['why'][:160]) for u in unreadable[:3]))
        return True, '%d records' % len(records)

    def shared():
        if not records:
            return False, 'no readable record'
        bad = []
        for k in SHARED:
            vals = sorted({r[k] for _, r in records})
            if len(vals) != 1:
                bad.append('%s: %d values (%s)' % (k, len(vals), ', '.join(
                    '%s %s' % (val[:16], ','.join(sorted(r['folder'] for _, r in records if r[k] == val)))
                    for val in vals)[:240]))
        if bad:
            return False, '; '.join(bad)
        r = records[0][1]
        return True, 'commit %s, run %s attempt %s, image %s' % (r['commit'][:12], r['run_id'], r['run_attempt'],
                                                                  r['image_id'][7:19])

    def this_run():
        if not records:
            return False, 'no readable record'
        bad = []
        for k, e in ENV_OF:
            want = os.environ.get(e, '')
            if not want:
                bad.append('%s is not set' % e)
                continue
            other = sorted({r['folder'] for _, r in records if r[k] != want})
            if other:
                bad.append('%s is not %s in %s' % (k, e, ', '.join(other)[:120]))
        if bad:
            return False, '; '.join(bad)
        return True, 'commit, run id, repository, ref and workflow ref are the environment\'s'

    def against(key, digest, what):
        """The records whose value of key is not digest."""
        if not records:
            return ['no readable record']
        other = sorted({r['folder'] for _, r in records if r[key] != digest})
        return ['%s of %s is not %s' % (key, ', '.join(other)[:120], what)] if other else []

    def inventory():
        obj, why = load_json(a.inventory_json, '--inventory-json')
        if obj is None:
            return False, why
        bad = []
        if obj.get('schema') != INVENTORY_SCHEMA:
            bad.append('schema is %r' % str(obj.get('schema'))[:60])
        if not (obj.get('held') is True and isinstance(obj.get('verdict'), str)
                and obj['verdict'].startswith(INVENTORY_HELD)):
            bad.append('verdict is not %r' % INVENTORY_HELD.strip())
        d = obj.get('digest')
        if not (isinstance(d, str) and HEX64.fullmatch(d)):
            return False, '; '.join(bad + ['no digest'])
        missing = [k for k in INVENTORY_KEYS if k not in obj]
        if missing:
            bad.append('lacks %s' % ', '.join(missing))
        elif sha(canonical({k: obj[k] for k in INVENTORY_KEYS})) != d:
            bad.append('its digest is not the sha256 of its own %s' % ', '.join(INVENTORY_KEYS))
        gated = obj.get('gated')
        folders = {}
        if not isinstance(gated, list):
            bad.append('no gated list')
        else:
            for g in gated:
                f = g.get('folder') if isinstance(g, dict) else None
                h = g.get('frozen4_sha256') if isinstance(g, dict) else None
                if not (isinstance(f, str) and FOLDER.fullmatch(f) and isinstance(h, str) and HEX64.fullmatch(h)):
                    bad.append('a gated entry has no folder and FROZEN4 sha256: %r' % str(g)[:80])
                elif f in folders:
                    bad.append('it names %s twice' % f)
                else:
                    folders[f] = h
            if not folders:
                bad.append('it names no gated folder')
        inputs['inventory'] = {'digest': d, 'folders': folders}
        bad += against('inventory_digest', d, 'the inventory\'s')
        if bad:
            return False, '; '.join(bad)
        return True, 'digest %s, %d gated folders' % (d, len(folders))

    def judge():
        obj, why = load_json(a.judge_json, '--judge-json')
        if obj is None:
            return False, why
        bad = []
        if obj.get('schema') != JUDGE_SCHEMA:
            bad.append('schema is %r' % str(obj.get('schema'))[:60])
        if not (obj.get('held') is True and isinstance(obj.get('verdict'), str)
                and obj['verdict'].startswith(JUDGE_HELD)):
            bad.append('verdict is not %r' % JUDGE_HELD.strip())
        d = obj.get('digest')
        if not (isinstance(d, str) and HEX64.fullmatch(d)):
            return False, '; '.join(bad + ['no digest'])
        if obj.get('expect') != d:
            bad.append('it was not given an expected digest equal to its own (expect is %r)'
                       % str(obj.get('expect'))[:64])
        inv = obj.get('inventory_digest')
        if 'inventory' not in inputs:
            bad.append('the inventory JSON was not read')
        elif inv != inputs['inventory']['digest']:
            bad.append('its inventory digest %s is not the inventory JSON\'s' % str(inv)[:64])
        files = obj.get('files')
        try:
            pairs = [(f['path'], f['sha256']) for f in files]
            ok_form = all(isinstance(p, str) and isinstance(s, str) and HEX64.fullmatch(s) for p, s in pairs)
            paths = [p for p, _ in pairs]
            if not pairs or not ok_form or len(set(paths)) != len(paths) or not isinstance(inv, str):
                raise ValueError
            h = hashlib.sha256()
            for p, s in sorted(pairs, key=lambda x: x[0].encode('utf-8')):
                h.update(('%s  %s\n' % (s, p)).encode('utf-8'))
            h.update(('inventory %s\n' % inv).encode('utf-8'))
            if h.hexdigest() != d:
                bad.append('its digest is not the sha256 of its own files and inventory digest')
            # the workflow the records ran (its blob at their commit) is the one the judge hashed
            wf = dict(pairs).get(WORKFLOW)
            other = sorted({r['folder'] for _, r in records if r['workflow_sha256'] != wf})
            if other:
                bad.append('its %s is %s, not the workflow_sha256 of %s' % (WORKFLOW, str(wf)[:16],
                                                                            ', '.join(other)[:120]))
        except (TypeError, KeyError, ValueError):
            bad.append('its file list is not a list of distinct paths with their sha256')
        inputs['judge'] = d
        bad += against('judge_digest', d, 'the CI judge\'s')
        if bad:
            return False, '; '.join(bad)
        return True, 'digest %s = its expected digest' % d

    def toolchain():
        obj, why = load_json(a.toolchain_json, '--toolchain-json')
        if obj is None:
            return False, why
        bad = []
        if obj.get('schema') != TOOLCHAIN_SCHEMA:
            bad.append('schema is %r' % str(obj.get('schema'))[:60])
        if not (obj.get('held') is True and isinstance(obj.get('verdict'), str)
                and obj['verdict'].startswith(TOOLCHAIN_HELD)):
            bad.append('verdict is not %r' % TOOLCHAIN_HELD.strip())
        d = obj.get('digest')
        if not (isinstance(d, str) and HEX64.fullmatch(d)):
            return False, '; '.join(bad + ['no digest'])
        inputs['toolchain'] = d
        bad += against('toolchain_digest', d, 'the toolchain check\'s')
        if bad:
            return False, '; '.join(bad)
        return True, 'digest %s' % d

    def folders():
        if 'inventory' not in inputs:
            return False, 'the inventory JSON was not read'
        want = set(inputs['inventory']['folders'])
        if not want:
            return False, 'the inventory names no gated folder'
        got = [r['folder'] for _, r in records]
        missing = sorted(want - set(got))
        extra = sorted(set(got) - want)
        twice = sorted({f for f in got if got.count(f) > 1})
        bad = []
        if missing:
            bad.append('missing %s' % ', '.join(missing))
        if extra:
            bad.append('extra %s' % ', '.join(extra))
        if twice:
            bad.append('twice %s' % ', '.join(twice))
        if bad:
            return False, '; '.join(bad)
        return True, '%d folders, one record each' % len(want)

    def anchors():
        if not records:
            return False, 'no readable record'
        inv = inputs.get('inventory', {}).get('folders')
        if inv is None:
            return False, 'the inventory JSON was not read'
        bad = []
        for _, r in records:
            if r['anchor'] != r['frozen4_sha256']:
                bad.append('%s: anchor %s, FROZEN4 %s' % (r['folder'], r['anchor'][:16], r['frozen4_sha256'][:16]))
            elif r['folder'] in inv and inv[r['folder']] != r['anchor']:
                bad.append('%s: anchor %s, the inventory\'s FROZEN4 %s' % (r['folder'], r['anchor'][:16],
                                                                          inv[r['folder']][:16]))
        if bad:
            return False, '; '.join(bad)[:400]
        return True, 'each record\'s anchor is its FROZEN4.txt\'s sha256'

    def gates():
        if not records:
            return False, 'no readable record'
        bad = []
        for _, r in records:
            m = GATE_HELD.fullmatch(r['gate_verdict_line'])
            if not m:
                bad.append('%s: %s' % (r['folder'], r['gate_verdict_line'][:100]))
            elif m.group(2) != m.group(3) or int(m.group(2)) < 1 or m.group(4) != r['frozen4_sha256'][:16]:
                bad.append('%s: %s' % (r['folder'], r['gate_verdict_line'][:100]))
        if bad:
            return False, '; '.join(bad)[:400]
        return True, '%d gates HELD n of n with their anchors' % len(records)

    def checks():
        if not records:
            return False, 'no readable record'
        bad = []
        for _, r in records:
            m = CHECK_HELD.fullmatch(r['gate_check_verdict'])
            if not m or m.group(1) != m.group(2) or int(m.group(1)) != GATE_LOG_ROWS:
                bad.append('%s: %s' % (r['folder'], r['gate_check_verdict'][:100]))
        if bad:
            return False, '; '.join(bad)[:400] + ' (each must be "GATE LOG HELD: %d of %d rows")' % (GATE_LOG_ROWS,
                                                                                                   GATE_LOG_ROWS)
        return True, '%d gate logs checked HELD, %d of %d rows each' % (len(records), GATE_LOG_ROWS, GATE_LOG_ROWS)

    rows.run('records: every file under --dir is a run record', read_records)
    rows.run('shared: one commit, workflow, run, image, judge', shared)
    rows.run('run: the records are this run\'s (GITHUB_ values)', this_run)
    rows.run('inventory: HELD, self-consistent, every record\'s', inventory)
    rows.run('judge: HELD, = MK_ANCHOR_CI, every record\'s', judge)
    rows.run('toolchain: HELD, every record\'s', toolchain)
    rows.run('folders: one record per gated folder of the inventory', folders)
    rows.run('anchors: each anchor is its FROZEN4.txt\'s sha256', anchors)
    rows.run('gates: each gate verdict is HELD n of n', gates)
    rows.run('gate checks: each gate log check is HELD', checks)

    if a.out is not None:
        def summary():
            n = len(rows.rows) + 1
            k = rows.failed()
            listed = rows.rows + [{'name': 'summary: written to --out', 'ok': True, 'detail': 'written'}]
            obj = {
                'schema': SUMMARY_SCHEMA,
                'records': [{'file': f, 'folder': r['folder'], 'anchor': r['anchor'],
                             'gate_verdict_line': r['gate_verdict_line'],
                             'gate_check_verdict': r['gate_check_verdict']}
                            for f, r in sorted(records, key=lambda x: (x[1]['folder'], x[0]))],
                'not_records': unreadable,
                'shared': {k2: (records[0][1][k2] if records and len({r[k2] for _, r in records}) == 1 else None)
                           for k2 in SHARED},
                'inputs': {'inventory_digest': inputs.get('inventory', {}).get('digest'),
                           'judge_digest': inputs.get('judge'), 'toolchain_digest': inputs.get('toolchain')},
                'rows': listed,
                'verdict': verdict_line(n, k),
            }
            data = (json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True) + '\n').encode('ascii')
            try:
                fh = open(a.out, 'xb')
            except OSError as e:
                return False, 'not written: %s' % (e.strerror or type(e).__name__)
            try:
                with fh:
                    fh.write(data)
            except OSError as e:
                try:
                    os.remove(a.out)
                except OSError:
                    pass
                return False, 'not written: %s' % (e.strerror or type(e).__name__)
            return True, 'written, sha256 %s' % sha(data)
        rows.run('summary: written to --out', summary)

    n, k = len(rows.rows), rows.failed()
    print(verdict_line(n, k))
    return 1 if k else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
