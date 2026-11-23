# SPDX-License-Identifier: AGPL-3.0-only
# The run record of one folder gate in CI. Standard library only (Python 3.12 or later); it needs git on the PATH.
#
#   python3 -B tools/ci/run_record.py --folder F --anchor HEX --root ROOT --gate-log LOG --gate-check-json J
#       --toolchain-json J --inventory-json J --judge-json J --image-id ID --base-image B --out FILE
#
# A gate job of .github/workflows/mathkernel-linux.yml runs it on the runner, after the gate and
# tools/ci/check_gate_log.py (not inside the image: the gate's container is given kernel/coq only, not the checkout's
# git folder). It reads GITHUB_SHA, GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT,
# GITHUB_REPOSITORY, GITHUB_REF and GITHUB_WORKFLOW_REF from the environment and asks git about ROOT. When every row
# passes it writes FILE: one JSON object, schema "skuldd-mathkernel-run-record/1", keys sorted. When a row fails it
# writes nothing. It never overwrites: an existing FILE is a usage error (exit 2).
# Rows:
#   environment   the six GITHUB_ values are set and well formed, and the workflow they name is mathkernel-linux.yml
#   git top       ROOT is the top folder of a git checkout
#   git head      HEAD is GITHUB_SHA
#   git objects   HEAD^{tree}, HEAD:kernel/coq (a tree) and HEAD:.github/workflows/mathkernel-linux.yml (a blob)
#   git clean     no tracked file differs from HEAD, so the files the gate read are the commit's
#   anchor        the sha256 of kernel/coq/<folder>/FROZEN4.txt (its bytes) equals --anchor
#   inventory     --inventory-json is the inventory's (schema skuldd-inventory/1), HELD, its digest the sha256 of its
#                 own gated, mirrors and gate_dir_files, and it names the folder once, with that same sha256
#   judge         --judge-json is the CI judge's (schema skuldd-ci-judge/1), HELD, given an expected digest equal to
#                 its own ("expect" is its digest; in the workflow that value is MK_ANCHOR_CI's, which this script
#                 does not read), over the inventory digest of --inventory-json
#   toolchain     --toolchain-json is the toolchain check's (schema skuldd-toolchain/1), HELD, with a digest
#   gate verdict  the gate log has exactly one verdict line, and it is its last line (a byte-order mark at the log's
#                 start, a GitHub timestamp at the start of a line and a CR at its end are taken off first, the mark
#                 and the timestamp as tools/ci/check_gate_log.py takes them off)
#   gate header   the gate log names this checkout's kernel/coq/gate/gate4.py (by the sha256 it prints), this folder
#                 and this FROZEN4.txt (the full sha256 it prints)
#   gate check    --gate-check-json is the log check's (schema skuldd-gate-log-check/1) of this folder, this anchor
#                 and this log (the sha256 of its bytes; its verdict line), with its own verdict line and its library
#                 map digest. Its verdict is recorded, HELD or not: verify_records.py judges it
#   image         --image-id is "sha256:" and 64 hex digits; --base-image is a reference pinned by a sha256 digest
#   record        FILE written
# The record holds: commit, tree, kernel_tree, workflow_blob and workflow_sha256 (of the blob's bytes) from git;
# run_id, run_attempt, repository, ref and workflow_ref from the environment; folder, anchor and frozen4_sha256; the
# image id and base image as given; the toolchain, library map, inventory and CI judge digests from the JSON files;
# the sha256 of the gate log's bytes, the gate's verdict line and the log check's verdict line, each as written.
# What a pass shows: the record's values are bound to one another as the rows say, at the moment it ran.
# What it does not show: that the gate held (the record carries the verdict lines; tools/ci/verify_records.py judges
# them, and judges every folder's record together); that the log is a real run's (in CI it is the file tee wrote in
# the same job); that the image is the one the id names (docker's word); that the JSON files were made by the scripts
# that name them (they are read, not rerun); anything git cannot see, such as an untracked file (the inventory and the
# gate judge those).
# Two row labels keep words of their first version, which the test's frozen predictions name: in "judge: HELD, equal
# to MK_ANCHOR_CI, same inventory" the expected digest is the one the judge JSON was given (in the workflow, the value
# of MK_ANCHOR_CI; this script never reads the variable), and in "gate log: this gate4.py judged this folder and
# FROZEN4", "judged" is the log's own word: its header line says that this gate4.py judges the folder; the row reads
# that header and the anchor line, not the gate's verdict.
# Last line: "RUN RECORD HELD: n of n rows" (exit 0) or "RUN RECORD FAILED: k of n rows failed" (exit 1); exit 2 on a
# usage error (an unknown or abbreviated option, --help among them, or an existing --out).
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')   # the same bytes on Windows as on Linux
except Exception:
    pass

NAME = 'RUN RECORD'
SCHEMA = 'skuldd-mathkernel-run-record/1'
WORKFLOW = '.github/workflows/mathkernel-linux.yml'
ENV_KEYS = ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_REPOSITORY', 'GITHUB_REF',
            'GITHUB_WORKFLOW_REF')
# The JSON files read, and what is read from each (the other scripts' --json output).
INVENTORY_SCHEMA = 'skuldd-inventory/1'
INVENTORY_KEYS = ('gated', 'mirrors', 'gate_dir_files')
INVENTORY_HELD = 'INVENTORY HELD: '
JUDGE_SCHEMA = 'skuldd-ci-judge/1'
JUDGE_HELD = 'CI JUDGE HELD: '
TOOLCHAIN_SCHEMA = 'skuldd-toolchain/1'
TOOLCHAIN_HELD = 'TOOLCHAIN HELD: '
GATE_CHECK_SCHEMA = 'skuldd-gate-log-check/1'
GATE_CHECK = re.compile(r'GATE LOG (HELD|FAILED): [^\n\r]*')
# git: the variables that would point git at another repository, index or object store are dropped; replace refs
# are ignored, so a tree is the commit's own.
GIT_DROP = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
            'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_REPLACE_REF_BASE')
HEX64 = re.compile(r'[0-9a-f]{64}')
OID = re.compile(r'[0-9a-f]{40}|[0-9a-f]{64}')
FOLDER = re.compile(r'[a-z][a-z0-9_]*')   # the inventory's folder names
FORMATS = {
    'GITHUB_SHA': OID,
    'GITHUB_RUN_ID': re.compile(r'[1-9][0-9]{0,19}'),
    'GITHUB_RUN_ATTEMPT': re.compile(r'[1-9][0-9]{0,5}'),
    'GITHUB_REPOSITORY': re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'),
    'GITHUB_REF': re.compile(r'refs/[^\s]+'),
    'GITHUB_WORKFLOW_REF': re.compile(r'[^\s@]+@refs/[^\s]+'),
}
IMAGE_ID = re.compile(r'sha256:[0-9a-f]{64}')
BASE_IMAGE = re.compile(r'[^\s@]+@sha256:[0-9a-f]{64}')
TIMESTAMP = re.compile(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{1,9}Z ')   # check_gate_log.py's form
VERDICT = re.compile(r'(?:\S+ )?GATE4 (?:HELD|FAILED):.*')
HEADER = re.compile(r'gate4\.py ([0-9a-f]{64}) judges (\S+) .*')
ANCHOR_LINE = re.compile(r'anchor ([0-9a-f]{64})')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_bytes(path):
    """(bytes, '') or (None, why)."""
    try:
        with open(path, 'rb') as fh:
            return fh.read(), ''
    except OSError as e:
        return None, '%s cannot be read (%s)' % (path, e.strerror or type(e).__name__)


def no_duplicates(pairs):
    keys = [k for k, _ in pairs]
    twice = sorted({k for k in keys if keys.count(k) > 1})
    if twice:
        raise ValueError('a key is given twice: %s' % ', '.join(twice))
    return dict(pairs)


def no_constant(name):
    raise ValueError('%s is not JSON' % name)


def load_json(path):
    """(object, '') or (None, why): strict UTF-8, no key twice, no NaN or Infinity, a JSON object."""
    b, why = read_bytes(path)
    if b is None:
        return None, why
    try:
        obj = json.loads(b.decode('utf-8'), object_pairs_hook=no_duplicates, parse_constant=no_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as e:
        return None, '%s is not strict JSON (%s)' % (path, str(e)[:120])
    if not isinstance(obj, dict):
        return None, '%s is not a JSON object' % path
    return obj, ''


def git(root, *args):
    """(stdout bytes, '') or (None, why)."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_DROP}
    env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
    cmd = ['git', '-C', root, '-c', 'core.fsmonitor=false'] + list(args)
    try:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, env=env, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, 'git %s: %s' % (args[0], type(e).__name__)
    if p.returncode != 0:
        msg = ' '.join(p.stderr.decode('utf-8', 'replace').split())[:160]
        return None, 'git %s exit %d: %s' % (args[0], p.returncode, msg)
    return p.stdout, ''


def git_oid(root, rev):
    out, why = git(root, 'rev-parse', '--verify', '--quiet', rev)
    if out is None:
        return None, '%s does not resolve (%s)' % (rev, why)
    oid = out.decode('ascii', 'replace').strip()
    if not OID.fullmatch(oid):
        return None, '%s resolves to %r' % (rev, oid[:80])
    return oid, ''


def log_lines(b):
    """The gate log's lines: a byte-order mark at its start, CR and a leading GitHub timestamp removed (the mark and
    the timestamp's form as tools/ci/check_gate_log.py removes them); empty lines kept."""
    out = []
    t = b.decode('utf-8', 'replace')
    if t.startswith('\ufeff'):
        t = t[1:]
    for line in t.split('\n'):
        line = line.rstrip('\r')
        m = TIMESTAMP.match(line)
        out.append(line[m.end():] if m else line)
    return out


class Rows:
    def __init__(self):
        self.rows = []

    def run(self, name, fn):
        try:
            ok, detail = fn()
        except Exception as e:  # a row that cannot be computed fails; it never passes silently
            ok, detail = False, 'error: %s: %s' % (type(e).__name__, str(e)[:160])
        self.rows.append((name, bool(ok), detail))
        print('  %-58s %s  %s' % (name, 'ok' if ok else 'FAIL', detail))
        sys.stdout.flush()
        return bool(ok)

    def failed(self):
        return sum(1 for _, ok, _ in self.rows if not ok)


def parse_args(argv):
    ap = argparse.ArgumentParser(prog='run_record.py', allow_abbrev=False, add_help=False,
                                 description='Write the run record of one folder gate (see the header).')
    for opt in ('--folder', '--anchor', '--root', '--gate-log', '--gate-check-json', '--toolchain-json',
                '--inventory-json', '--judge-json', '--image-id', '--base-image', '--out'):
        ap.add_argument(opt, required=True)
    return ap.parse_args(argv)


def main(argv):
    a = parse_args(argv)
    if os.path.lexists(a.out):
        print('run_record.py: %s exists; a record is never overwritten' % a.out, file=sys.stderr)
        return 2
    root = os.path.abspath(a.root)
    env = {k: os.environ.get(k, '') for k in ENV_KEYS}
    v = {}  # the record's values, filled by the rows
    seen = {}  # values read on the way: the inventory JSON's digest, compared with the judge's even when its row fails
    rows = Rows()

    def environment():
        bad = []
        for k in ENV_KEYS:
            if not env[k]:
                bad.append('%s is not set' % k)
            elif not FORMATS[k].fullmatch(env[k]):
                bad.append('%s is not well formed: %r' % (k, env[k][:80]))
        if not bad:
            # "<owner>/<repository>/<workflow path>@<ref>": the path is compared exactly, the repository's name
            # without regard to case (GitHub's names are not case-sensitive)
            path = env['GITHUB_WORKFLOW_REF'].split('@', 1)[0]
            tail = '/' + WORKFLOW
            if not (path.endswith(tail) and path[:-len(tail)].lower() == env['GITHUB_REPOSITORY'].lower()):
                bad.append('GITHUB_WORKFLOW_REF names another workflow: %s' % env['GITHUB_WORKFLOW_REF'][:120])
        if bad:
            return False, '; '.join(bad)
        v.update(run_id=env['GITHUB_RUN_ID'], run_attempt=env['GITHUB_RUN_ATTEMPT'],
                 repository=env['GITHUB_REPOSITORY'], ref=env['GITHUB_REF'], workflow_ref=env['GITHUB_WORKFLOW_REF'])
        return True, 'run %s attempt %s of %s' % (env['GITHUB_RUN_ID'], env['GITHUB_RUN_ATTEMPT'],
                                                    env['GITHUB_REPOSITORY'])

    def git_top():
        if not os.path.isdir(root):
            return False, '--root is not a folder'
        out, why = git(root, 'rev-parse', '--show-toplevel')
        if out is None:
            return False, why
        top = out.decode('utf-8', 'replace').strip()
        try:
            same = os.path.samefile(top, root)
        except OSError:
            same = False
        return same, 'the checkout\'s top folder' if same else 'the checkout\'s top folder is another: %s' % top

    def git_head():
        oid, why = git_oid(root, 'HEAD^{commit}')
        if oid is None:
            return False, why
        v['commit'] = oid
        if not env['GITHUB_SHA']:
            return False, 'HEAD %s; GITHUB_SHA is not set' % oid
        if oid != env['GITHUB_SHA']:
            return False, 'HEAD %s is not GITHUB_SHA %s' % (oid, env['GITHUB_SHA'])
        return True, 'HEAD %s' % oid

    def git_objects():
        bad = []
        for key, rev, kind in (('tree', 'HEAD^{tree}', 'tree'), ('kernel_tree', 'HEAD:kernel/coq', 'tree'),
                               ('workflow_blob', 'HEAD:' + WORKFLOW, 'blob')):
            oid, why = git_oid(root, rev)
            if oid is None:
                bad.append(why)
                continue
            out, why = git(root, 'cat-file', '-t', oid)
            got = out.decode('ascii', 'replace').strip() if out is not None else why
            if got != kind:
                bad.append('%s is a %s, not a %s' % (rev, got, kind))
                continue
            v[key] = oid
        if 'workflow_blob' in v:
            out, why = git(root, 'cat-file', 'blob', v['workflow_blob'])
            if out is None:
                bad.append(why)
            else:
                v['workflow_sha256'] = sha(out)
        if bad:
            return False, '; '.join(bad)
        return True, 'tree %s, kernel/coq %s, workflow %s' % (v['tree'][:12], v['kernel_tree'][:12],
                                                               v['workflow_blob'][:12])

    def git_clean():
        out, why = git(root, 'diff', '--name-only', '--no-renames', '-z', 'HEAD', '--')
        if out is None:
            return False, why
        changed = sorted(p for p in out.decode('utf-8', 'replace').split('\0') if p)
        if changed:
            return False, 'tracked files that differ from HEAD (%d): %s' % (len(changed), ', '.join(changed[:6]))
        return True, 'every tracked file is HEAD\'s'

    def anchor():
        if not FOLDER.fullmatch(a.folder):
            return False, '--folder is not a folder name: %r' % a.folder[:40]
        b, why = read_bytes(os.path.join(root, 'kernel', 'coq', a.folder, 'FROZEN4.txt'))
        if b is None:
            return False, 'kernel/coq/%s/FROZEN4.txt cannot be read' % a.folder
        v['folder'] = a.folder
        v['frozen4_sha256'] = h = sha(b)
        if not HEX64.fullmatch(a.anchor):
            return False, '--anchor is not 64 lower-case hex digits'
        v['anchor'] = a.anchor
        if h != a.anchor:
            return False, 'kernel/coq/%s/FROZEN4.txt is %s, the anchor is %s' % (a.folder, h, a.anchor)
        return True, '%s %s' % (a.folder, h)

    def inventory():
        obj, why = load_json(a.inventory_json)
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
            bad.append('no digest')
        else:
            seen['inventory_digest'] = d
            if any(k not in obj for k in INVENTORY_KEYS):
                bad.append('lacks one of %s' % ', '.join(INVENTORY_KEYS))
            elif sha(canonical({k: obj[k] for k in INVENTORY_KEYS})) != d:
                bad.append('its digest is not the sha256 of its own %s' % ', '.join(INVENTORY_KEYS))
        gated = obj.get('gated')
        if not isinstance(gated, list):
            bad.append('no gated list')
            gated = []
        mine = [g for g in gated if isinstance(g, dict) and g.get('folder') == a.folder]
        if len(mine) != 1:
            bad.append('names the folder %s %d times' % (a.folder, len(mine)))
        elif 'frozen4_sha256' not in v:
            bad.append('no FROZEN4.txt sha256 of this checkout to compare')
        elif mine[0].get('frozen4_sha256') != v['frozen4_sha256']:
            bad.append('its FROZEN4 sha256 for %s is %s' % (a.folder, str(mine[0].get('frozen4_sha256'))[:64]))
        if bad:
            return False, '; '.join(bad)
        v['inventory_digest'] = d
        return True, 'digest %s' % d

    def judge():
        obj, why = load_json(a.judge_json)
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
            bad.append('no digest')
        elif obj.get('expect') != d:
            bad.append('it was not given an expected digest equal to its own (expect is %r)'
                       % str(obj.get('expect'))[:64])
        if 'inventory_digest' not in seen:
            bad.append('the inventory JSON holds no digest to compare')
        elif obj.get('inventory_digest') != seen['inventory_digest']:
            bad.append('its inventory digest %r is not the inventory JSON\'s' % str(obj.get('inventory_digest'))[:64])
        if bad:
            return False, '; '.join(bad)
        v['judge_digest'] = d
        return True, 'digest %s = its expected digest' % d

    def toolchain():
        obj, why = load_json(a.toolchain_json)
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
            bad.append('no digest')
        if bad:
            return False, '; '.join(bad)
        v['toolchain_digest'] = d
        return True, 'digest %s' % d

    def gate_lines():
        b, why = read_bytes(a.gate_log)
        if b is None:
            return None, why
        v['gate_log_sha256'] = sha(b)
        return log_lines(b), ''

    def gate_verdict():
        lines, why = gate_lines()
        if lines is None:
            return False, why
        found = [i for i, line in enumerate(lines) if VERDICT.fullmatch(line)]
        last = max([i for i, line in enumerate(lines) if line.strip()] or [-1])
        if len(found) != 1:
            return False, '%d verdict lines' % len(found)
        if found[0] != last:
            return False, 'the verdict line is not the last line'
        v['gate_verdict_line'] = lines[found[0]]
        return True, lines[found[0]]

    def gate_header():
        lines, why = gate_lines()
        if lines is None:
            return False, why
        gb, why = read_bytes(os.path.join(root, 'kernel', 'coq', 'gate', 'gate4.py'))
        if gb is None:
            return False, 'kernel/coq/gate/gate4.py cannot be read'
        heads = [HEADER.fullmatch(line) for line in lines]
        heads = [m for m in heads if m]
        anchors = [m.group(1) for m in (ANCHOR_LINE.fullmatch(line) for line in lines) if m]
        bad = []
        if len(heads) != 1:
            bad.append('%d gate4.py header lines' % len(heads))
        else:
            if heads[0].group(1) != sha(gb):
                bad.append('written by gate4.py %s, this checkout\'s is %s' % (heads[0].group(1)[:16], sha(gb)[:16]))
            if heads[0].group(2) != a.folder:
                bad.append('it judges %s, not %s' % (heads[0].group(2)[:40], a.folder))
        if len(anchors) != 1:
            bad.append('%d anchor lines' % len(anchors))
        elif anchors[0] != v.get('frozen4_sha256'):
            bad.append('it read FROZEN4.txt as %s' % anchors[0])
        if bad:
            return False, '; '.join(bad)
        return True, 'it names gate4.py %s, %s and FROZEN4 %s' % (sha(gb)[:16], a.folder, anchors[0][:16])

    def gate_check():
        obj, why = load_json(a.gate_check_json)
        if obj is None:
            return False, why
        bad = []
        if obj.get('schema') != GATE_CHECK_SCHEMA:
            bad.append('schema is %r' % str(obj.get('schema'))[:60])
        verdict = obj.get('verdict')
        if not (isinstance(verdict, str) and GATE_CHECK.fullmatch(verdict)):
            bad.append('no verdict line')
        d = obj.get('library_map_digest')
        if not (isinstance(d, str) and HEX64.fullmatch(d)):
            bad.append('no library map digest')
        if obj.get('folder') != a.folder:
            bad.append('it checked folder %r' % str(obj.get('folder'))[:40])
        if obj.get('anchor') != a.anchor:
            bad.append('it checked anchor %r' % str(obj.get('anchor'))[:64])
        # the same log: its bytes, and (when the log has one verdict line, its last) the same verdict line
        if 'gate_log_sha256' in v and obj.get('gate_log_sha256') != v['gate_log_sha256']:
            bad.append('it checked a log of sha256 %r, not --gate-log' % str(obj.get('gate_log_sha256'))[:64])
        if 'gate_verdict_line' in v and obj.get('gate_verdict_line') != v['gate_verdict_line']:
            bad.append('it read the verdict line as %r' % str(obj.get('gate_verdict_line'))[:100])
        if bad:
            return False, '; '.join(bad)
        v.update(gate_check_verdict=verdict, library_map_digest=d)
        return True, verdict

    def image():
        bad = []
        if not IMAGE_ID.fullmatch(a.image_id):
            bad.append('--image-id is not sha256:<64 hex>: %r' % a.image_id[:80])
        if not BASE_IMAGE.fullmatch(a.base_image):
            bad.append('--base-image is not pinned by a sha256 digest: %r' % a.base_image[:120])
        if bad:
            return False, '; '.join(bad)
        v.update(image_id=a.image_id, base_image=a.base_image)
        return True, '%s from %s' % (a.image_id[:19], a.base_image)

    rows.run('environment: the six GITHUB_ values, well formed', environment)
    rows.run('git: --root is the top folder of a checkout', git_top)
    rows.run('git: HEAD is GITHUB_SHA', git_head)
    rows.run('git: the tree, kernel/coq and the workflow resolve', git_objects)
    rows.run('git: no tracked file differs from HEAD', git_clean)
    rows.run('anchor: FROZEN4.txt\'s sha256 is --anchor', anchor)
    rows.run('inventory: HELD, names the folder with that sha256', inventory)
    rows.run('judge: HELD, equal to MK_ANCHOR_CI, same inventory', judge)
    rows.run('toolchain: the toolchain check HELD, with a digest', toolchain)
    rows.run('gate log: one verdict line, and it is the last', gate_verdict)
    rows.run('gate log: this gate4.py judged this folder and FROZEN4', gate_header)
    rows.run('gate check: this folder, anchor and log; a verdict, a map', gate_check)
    rows.run('image: an image id and a pinned base image', image)

    def write():
        if rows.failed():
            return False, 'not written: %d rows failed' % rows.failed()
        keys = ('commit', 'tree', 'kernel_tree', 'workflow_blob', 'workflow_sha256', 'run_id', 'run_attempt',
                'repository', 'ref', 'workflow_ref', 'folder', 'anchor', 'frozen4_sha256', 'image_id', 'base_image',
                'toolchain_digest', 'library_map_digest', 'inventory_digest', 'judge_digest', 'gate_log_sha256',
                'gate_verdict_line', 'gate_check_verdict')
        missing = [k for k in keys if k not in v]
        if missing:
            return False, 'not written: no value for %s' % ', '.join(missing)
        record = dict((k, v[k]) for k in keys)
        record['schema'] = SCHEMA
        data = (json.dumps(record, sort_keys=True, indent=1, ensure_ascii=True) + '\n').encode('ascii')
        try:
            fh = open(a.out, 'xb')
        except OSError as e:
            return False, 'not written: %s' % (e.strerror or type(e).__name__)
        try:
            with fh:
                fh.write(data)
        except OSError as e:
            try:
                os.remove(a.out)  # never leave a part of a record
            except OSError:
                pass
            return False, 'not written: %s' % (e.strerror or type(e).__name__)
        return True, '%d keys, sha256 %s' % (len(record), sha(data))

    rows.run('record: written to --out', write)
    n, k = len(rows.rows), rows.failed()
    if k:
        print('%s FAILED: %d of %d rows failed' % (NAME, k, n))
        return 1
    print('%s HELD: %d of %d rows' % (NAME, n, n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
