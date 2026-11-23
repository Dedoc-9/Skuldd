# SPDX-License-Identifier: AGPL-3.0-only
# The CI judge's digest (standard library only). The CI judge is the files that decide what a CI run of this
# repository says: the workflows and the scripts and data the checks run with, every file a test of tools/ci or a
# feature row reads as its cases or its expected outcomes, and THEOREMS.md, whose tables the inventory holds the tree
# to. Under ruling S282-3 (b) of 2026-11-22 it also holds two kinds of evidence file that nothing else bound:
# BOUNDARIES.md, the boundary map (tools/ci/check_boundaries.py checks its form, not its truth), and the FROZEN.txt
# directly inside each folder under kernel/coq (a folder's record of its statement files' sha256). The rest of the
# tree the checks judge is not a judge file: kernel/coq's folders and Verdandi's copies of them are bound
# through the inventory's digest (each freeze list's sha256, each listed file held to it). This script hashes the
# judge files and the inventory's digest into one sha256. The owner reviews the judge and sets that value as the
# repository Actions variable MK_ANCHOR_CI. A change to any judge file, or to what the inventory finds, changes the
# digest, so a run given the old value fails until the owner sets the new one.
#
# The judge files, by group (paths from the repository root, written with /, matched with their exact case):
#   workflows           .github/workflows/*.yml and *.yaml (GitHub runs both; the extension's case is ignored)
#   codeowners          .github/CODEOWNERS
#   tools-ci            every file under tools/ci/, where a folder named __pycache__ is skipped
#   check-manifests     tools/check_manifests.py
#   ci-mathkernel       every file under ci/mathkernel/ (nothing skipped)
#   gate                every file under kernel/coq/gate/ (nothing skipped)
#   expected-libraries  kernel/coq/EXPECTED-CI-LIBRARIES.txt
#   feature-row3        kernel/hardening/features/feature_row3.py
#   feature-row4        kernel/hardening/features/feature_row4.py
#   anchors-ledger      kernel/coq/ANCHORS.md (its prose and its Record column; the inventory binds its values)
#   fpenv-check         kernel/runtime/check_fpenv.py (the fpenv job's gate, whose success the verdict requires)
#   fpenv-test          kernel/runtime/test_fpenv.c (the self-test that gate builds)
#   theorems            THEOREMS.md (its proved and Successors tables, which the inventory reads, and its prose)
#   row4-predictions    kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md (the cases and outcomes that
#                       tools/ci/tests/test_feature_row4.py holds feature row 4 to)
#   row4-plants         every file under kernel/hardening/features/plants4/ (feature row 4's plants and decoys, which
#                       that test and tools/ci/tests/test_safepath.py run)
#   boundaries-frozen   BOUNDARIES.md, and kernel/coq/<folder>/FROZEN.txt for each folder directly under kernel/coq
#                       that holds one (its name's exact case; one level only). It must hold BOUNDARIES.md and at
#                       least one FROZEN.txt; a link directly under kernel/coq, where a FROZEN.txt is looked for, is
#                       refused as a link where a judge file is looked for
#   top-py             every *.py file at the repository's top (optional: none is expected). A script read from
#                       stdin by a workflow step would import such a file in place of a standard module if Python put
#                       the current folder on its import path; the workflows set PYTHONSAFEPATH=1, and this group
#                       makes adding one a judge change as well
#   local-actions       every file under .github/actions/ (optional: no workflow uses a local action today; one added
#                       later is judged on every change, not only when a workflow first names it)
# Every group but the two optional ones must hold at least one file (boundaries-frozen: the files its line names).
#
# The digest is the sha256 of the lines "<sha256 of the file's bytes>  <path>\n", sorted by the path's UTF-8 bytes,
# followed by the line "inventory <inventory digest>\n". The inventory digest comes from --inventory-json (the JSON
# that tools/ci/inventory.py writes), or else from a run of <root>/tools/ci/inventory.py. Files are read as bytes, never
# as text, so the same bytes give the same digest on Windows and on Linux.
#
# Rows, each ok or FAIL:
#   group <name>                  the group holds at least one file (an optional group: it was looked for; its count;
#                                 boundaries-frozen: BOUNDARIES.md and at least one FROZEN.txt)
#   judge files are plain files   no link, junction or special file where a judge file is looked for; every judge
#                                 file can be read; no path holds a control character, a backslash or non-UTF-8 bytes
#   this judge is the judged one  the bytes of this running script equal <root>/tools/ci/judge_digest.py
#   inventory digest              a digest of 64 lower-case hex digits was read from an inventory that HELD. From
#                                 --inventory-json: strict JSON (no key twice, no NaN), schema skuldd-inventory/1, a
#                                 verdict "INVENTORY HELD: ...", "held" true, and a digest that is the sha256 of the
#                                 canonical JSON of its gated, mirrors and gate_dir_files. From a run: inventory.py
#                                 exited 0, printed one "INVENTORY DIGEST <hex>" line, and wrote such a JSON with the
#                                 same digest
#   expected digest               (only with --expect) the digest equals HEX. Otherwise the row says: "the CI judge
#                                 changed: after review the owner sets MK_ANCHOR_CI to <digest>"
# Then "CI JUDGE DIGEST <hex>" ("CI JUDGE DIGEST none" when no inventory digest was read), then one verdict line:
# "CI JUDGE HELD: n of n rows" or "CI JUDGE FAILED: k of n rows failed". The digest is printed even when a row fails,
# so a failure can be diagnosed; a digest from a FAILED run is not one to set.
# Exit 0 only when HELD, 1 when FAILED, 2 on a usage error: a bad option (an unknown or abbreviated one, --help among
# them), a root that is not a folder, a --json path that would itself be a judge file, or a --json file that cannot
# be written.
#
# What a pass shows: the judge files and the inventory are, byte for byte, the ones whose digest is HEX.
# What it does not show:
#   - that the judge is right or was reviewed. That is the owner's act when the owner sets MK_ANCHOR_CI.
#   - anything about a file outside the groups above, such as mk_fpenv.c and mk_fpenv.h (the subject the fpenv job
#     judges, held by no anchor), a module beside a script that a workflow runs from another folder (PYTHONSAFEPATH
#     keeps it from being imported, not this digest), a package folder at the top (json/__init__.py), or a compiled
#     module at the top (json.pyc, json.abi3.so: the top-py group takes *.py only; the workflows refuse a tracked .pyc,
#     and nothing refuses a tracked .so; PYTHONSAFEPATH keeps the top folder off the import path).
#   - the files a test or a feature row reads only as copies of the tree it judges (records, consoles and notes beside
#     the gated folders and in Verdandi's copies, README.md as the file outside the judge that a test changes): their
#     bytes decide no verdict.
#   - kernel/records: kernel/records/INDEX.md lists its records by name and sha256, no judge group holds them, and no
#     check compares a record with its line there (ruling S282-3 (b): a records check is a later push). One record,
#     kernel/records/floor32/sweep_fc.c, has its sha256 in tools/ci/SWEEP-SOURCE.txt too, which the sweep check holds
#     it to only when that file's use line names it.
#   - that a row of BOUNDARIES.md is true, or that a FROZEN.txt's hashes are the owner's or were recorded before a
#     proof (each file says so): the digest holds their bytes, so a change to them is seen and reviewed.
#   - compiled Python in tools/ci/__pycache__ (skipped), or a file's executable bit. Python can run a .pyc from
#     there in place of the source of a tools/ci module that a script imports (one named like a standard module
#     too), so a .py module added to tools/ci deserves that question in review.
#   - that this script was not changed to print a chosen digest. A pass is only as good as the judge file that ran,
#     and that file is one of the files the digest holds. A pull request's run uses the pull request's own judge and
#     workflows, so against a hostile change the barrier is the owner's review, not this digest.
#
# Usage:
#   python3 -B tools/ci/judge_digest.py --root ROOT [--inventory-json F] [--json OUT] [--expect HEX]
# --json OUT writes the run as JSON with sorted keys: schema "skuldd-ci-judge/1", digest, inventory_digest,
# inventory_source, expect, files [{path, sha256, group}], groups [{name, pattern, files}], rows [{name, ok,
# detail}], verdict, held. OUT must not be a judge file itself.
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

SCHEMA = 'skuldd-ci-judge/1'
INVENTORY_SCHEMA = 'skuldd-inventory/1'
INVENTORY_KEYS = ('gated', 'mirrors', 'gate_dir_files')
INVENTORY_HELD = 'INVENTORY HELD: '
SELF_PATH = 'tools/ci/judge_digest.py'
INVENTORY_PATH = 'tools/ci/inventory.py'
SKIP_DIR = '__pycache__'
HEX64 = re.compile(r'[0-9a-f]{64}')
WORKFLOW_SUFFIXES = ('.yml', '.yaml')
INVENTORY_TIMEOUT = 1800
FROZEN_TOP = 'kernel/coq'
FROZEN_NAME = 'FROZEN.txt'

# (group name, kind, path, pattern shown, required). kind: 'workflows' (the top-level *.yml and *.yaml of a folder),
# 'top-py' (the *.py files at the top of the root, the suffix's case exact, as Python's import matches it), 'file'
# (one file), 'tree' (every file under a folder), 'tree-py' (the same, folders named __pycache__ skipped),
# 'map-frozen' (the file at path, and FROZEN_NAME in each folder directly under FROZEN_TOP; required means both). A
# group that is not required may hold no file, and its folder may be absent.
GROUPS = (
    ('workflows', 'workflows', '.github/workflows', '.github/workflows/*.yml, *.yaml', True),
    ('codeowners', 'file', '.github/CODEOWNERS', '.github/CODEOWNERS', True),
    ('tools-ci', 'tree-py', 'tools/ci', 'tools/ci/** but __pycache__', True),
    ('check-manifests', 'file', 'tools/check_manifests.py', 'tools/check_manifests.py', True),
    ('ci-mathkernel', 'tree', 'ci/mathkernel', 'ci/mathkernel/**', True),
    ('gate', 'tree', 'kernel/coq/gate', 'kernel/coq/gate/**', True),
    ('expected-libraries', 'file', 'kernel/coq/EXPECTED-CI-LIBRARIES.txt', 'kernel/coq/EXPECTED-CI-LIBRARIES.txt',
     True),
    ('feature-row3', 'file', 'kernel/hardening/features/feature_row3.py',
     'kernel/hardening/features/feature_row3.py', True),
    ('feature-row4', 'file', 'kernel/hardening/features/feature_row4.py',
     'kernel/hardening/features/feature_row4.py', True),
    ('anchors-ledger', 'file', 'kernel/coq/ANCHORS.md', 'kernel/coq/ANCHORS.md', True),
    ('fpenv-check', 'file', 'kernel/runtime/check_fpenv.py', 'kernel/runtime/check_fpenv.py', True),
    ('fpenv-test', 'file', 'kernel/runtime/test_fpenv.c', 'kernel/runtime/test_fpenv.c', True),
    ('theorems', 'file', 'THEOREMS.md', 'THEOREMS.md', True),
    ('row4-predictions', 'file', 'kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md',
     'kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md', True),
    ('row4-plants', 'tree', 'kernel/hardening/features/plants4', 'kernel/hardening/features/plants4/**', True),
    ('boundaries-frozen', 'map-frozen', 'BOUNDARIES.md', 'BOUNDARIES.md, kernel/coq/*/FROZEN.txt', True),
    ('top-py', 'top-py', '', '*.py at the top (optional)', False),
    ('local-actions', 'tree', '.github/actions', '.github/actions/** (optional)', False),
)
ROW_WIDTH = 28


class Usage(Exception):
    pass


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_link(path):
    """True for a symbolic link, and on Windows for a junction too."""
    if os.path.islink(path):
        return True
    isjunction = getattr(os.path, 'isjunction', None)
    return bool(isjunction and isjunction(path))


def entry_is_link(entry):
    if entry.is_symlink():
        return True
    isjunction = getattr(entry, 'is_junction', None)
    return bool(isjunction and isjunction())


def bad_name(name):
    """Why a path part cannot stand in a digest line, or None."""
    try:
        name.encode('utf-8')
    except UnicodeEncodeError:
        return 'bytes that are not UTF-8'
    if any(ord(c) < 0x20 or ord(c) == 0x7f for c in name):
        return 'a control character'
    if '\\' in name:
        return 'a backslash'
    return None


def resolve(root, rel, problems):
    """The path of rel under root when every part exists with this exact case and none is a link, else None."""
    cur = root
    parts = rel.split('/')
    for i, part in enumerate(parts):
        try:
            names = os.listdir(cur)
        except OSError:
            return None
        if part not in names:
            return None
        cur = os.path.join(cur, part)
        if is_link(cur):
            problems.append('%s is a link' % '/'.join(parts[:i + 1]))
            return None
    return cur


def regular(path):
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


def collect_tree(top, top_rel, problems, skip=None):
    """[(rel, path)] of every regular file under top; folders named skip are skipped."""
    out = []
    stack = [(top, top_rel)]
    while stack:
        here, here_rel = stack.pop()
        try:
            with os.scandir(here) as it:
                entries = sorted(it, key=lambda e: e.name)
        except OSError as e:
            problems.append('%s cannot be listed (%s)' % (here_rel, type(e).__name__))
            continue
        for e in entries:
            why = bad_name(e.name)
            if why:
                problems.append('a name under %s holds %s: %s' % (here_rel, why, ascii(e.name)))
                continue
            rel = here_rel + '/' + e.name
            if entry_is_link(e):
                problems.append('%s is a link' % rel)
            elif e.is_dir(follow_symlinks=False):
                if e.name != skip:
                    stack.append((e.path, rel))
            elif e.is_file(follow_symlinks=False):
                out.append((rel, e.path))
            else:
                problems.append('%s is not a regular file' % rel)
    return out


def collect_workflows(top, top_rel, problems, py=False):
    """[(rel, path)] of the top-level *.yml and *.yaml files of top (the extension's case ignored), or with py the
    top-level *.py files (the suffix's case exact). top_rel '' is the root itself."""
    out = []
    shown = top_rel or 'the root'
    try:
        with os.scandir(top) as it:
            entries = sorted(it, key=lambda e: e.name)
    except OSError as e:
        problems.append('%s cannot be listed (%s)' % (shown, type(e).__name__))
        return out
    for e in entries:
        if not (e.name.endswith('.py') if py else e.name.lower().endswith(WORKFLOW_SUFFIXES)):
            continue
        why = bad_name(e.name)
        if why:
            problems.append('a name under %s holds %s: %s' % (shown, why, ascii(e.name)))
            continue
        rel = top_rel + '/' + e.name if top_rel else e.name
        if entry_is_link(e):
            problems.append('%s is a link' % rel)
        elif e.is_dir(follow_symlinks=False):
            continue
        elif e.is_file(follow_symlinks=False):
            out.append((rel, e.path))
        else:
            problems.append('%s is not a regular file' % rel)
    return out


def collect_frozen(root, problems):
    """[(rel, path)] of FROZEN_NAME (its exact case) in each folder directly under FROZEN_TOP. A link directly under
    FROZEN_TOP is a problem, as a link where a judge file is looked for."""
    out = []
    top = resolve(root, FROZEN_TOP, problems)
    if top is None:
        return out
    if not os.path.isdir(top):
        problems.append('%s is not a folder' % FROZEN_TOP)
        return out
    try:
        with os.scandir(top) as it:
            entries = sorted(it, key=lambda e: e.name)
    except OSError as e:
        problems.append('%s cannot be listed (%s)' % (FROZEN_TOP, type(e).__name__))
        return out
    for e in entries:
        why = bad_name(e.name)
        shown = '%s/%s' % (FROZEN_TOP, ascii(e.name) if why else e.name)
        if entry_is_link(e):
            problems.append('%s is a link' % shown)
            continue
        if not e.is_dir(follow_symlinks=False):
            continue
        try:
            names = os.listdir(e.path)
        except OSError as x:
            problems.append('%s cannot be listed (%s)' % (shown, type(x).__name__))
            continue
        if FROZEN_NAME not in names:
            continue
        if why:
            problems.append('a name under %s holds %s: %s' % (FROZEN_TOP, why, ascii(e.name)))
            continue
        rel = '%s/%s/%s' % (FROZEN_TOP, e.name, FROZEN_NAME)
        path = os.path.join(e.path, FROZEN_NAME)
        if is_link(path):
            problems.append('%s is a link' % rel)
        elif regular(path):
            out.append((rel, path))
        else:
            problems.append('%s is not a regular file' % rel)
    return out


def collect(root):
    """({path: (sha256, group)}, {group: count}, problems)."""
    files, counts, problems = {}, {}, []
    for name, kind, rel, _pattern, _required in GROUPS:
        found = []
        path = root if rel == '' else resolve(root, rel, problems)
        if kind == 'map-frozen':
            if path is not None:
                if regular(path):
                    found = [(rel, path)]
                else:
                    problems.append('%s is not a regular file' % rel)
            found += collect_frozen(root, problems)
        elif path is not None:
            if kind == 'file':
                if regular(path):
                    found = [(rel, path)]
                else:
                    problems.append('%s is not a regular file' % rel)
            elif os.path.isdir(path):
                if kind in ('workflows', 'top-py'):
                    found = collect_workflows(path, rel, problems, py=kind == 'top-py')
                else:
                    found = collect_tree(path, rel, problems, SKIP_DIR if kind == 'tree-py' else None)
            else:
                problems.append('%s is not a folder' % rel)
        n = 0
        for frel, fpath in found:
            if frel in files:
                continue
            try:
                files[frel] = (sha_file(fpath), name)
                n += 1
            except OSError as e:
                problems.append('%s cannot be read (%s)' % (frel, type(e).__name__))
        counts[name] = n
    return files, counts, problems


def path_key(item):
    return item[0].encode('utf-8')


def digest_of(entries, inventory_digest):
    """The CI judge digest of [(path, sha256)] in any order and the inventory digest."""
    seen = set()
    h = hashlib.sha256()
    for path, sha in sorted(entries, key=path_key):
        if path in seen:
            raise ValueError('a path is listed twice: %s' % path)
        seen.add(path)
        h.update(('%s  %s\n' % (sha, path)).encode('utf-8'))
    h.update(('inventory %s\n' % inventory_digest).encode('ascii'))
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def no_duplicates(pairs):
    keys = [k for k, _v in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError('a key appears twice')
    return dict(pairs)


def no_constant(name):
    raise ValueError('%s is not JSON' % name)


def inventory_from_json_bytes(raw):
    """(digest or None, problem or None) from the bytes of an inventory JSON. A digest that is the sha256 of its own
    content is returned even when the inventory FAILED (so the judge digest can still be printed); the row fails."""
    try:
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicates, parse_constant=no_constant)
    except (UnicodeDecodeError, ValueError, RecursionError):
        return None, 'it is not strict UTF-8 JSON (no key twice, no NaN or Infinity)'
    if not isinstance(obj, dict):
        return None, 'it is not a JSON object'
    if obj.get('schema') != INVENTORY_SCHEMA:
        return None, 'its schema is not %s' % INVENTORY_SCHEMA
    digest = obj.get('digest')
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        return None, 'it holds no digest of 64 lower-case hex digits'
    missing = [k for k in INVENTORY_KEYS if k not in obj]
    if missing:
        return None, 'it lacks %s' % ', '.join(missing)
    if sha_bytes(canonical({k: obj[k] for k in INVENTORY_KEYS})) != digest:
        return None, 'its digest is not the sha256 of its own %s' % ', '.join(INVENTORY_KEYS)
    verdict = obj.get('verdict')
    if not (isinstance(verdict, str) and verdict.startswith(INVENTORY_HELD)):
        return digest, 'its verdict is not "%s..." (%s)' % (INVENTORY_HELD, ascii(verdict)[:80])
    if obj.get('held') is not True:
        return digest, 'its "held" is not true (%s)' % ascii(obj.get('held'))[:40]
    return digest, None


def inventory_from_file(path):
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except OSError as e:
        return None, 'the file given by --inventory-json cannot be read (%s)' % type(e).__name__
    digest, problem = inventory_from_json_bytes(raw)
    if problem:
        return digest, 'the file given by --inventory-json: %s' % problem
    return digest, None


def inventory_from_run(root):
    """(digest or None, problem or None) from a run of <root>/tools/ci/inventory.py."""
    problems = []
    script = resolve(root, INVENTORY_PATH, problems)
    if script is None or not regular(script):
        return None, 'the root holds no regular file %s%s' % (INVENTORY_PATH, ''.join('; ' + p for p in problems))
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='ci-judge-') as tmp:
        out = os.path.join(tmp, 'inventory.json')
        try:
            run = subprocess.run([sys.executable, '-B', script, '--root', root, '--json', out], cwd=root, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=INVENTORY_TIMEOUT)
        except subprocess.TimeoutExpired:
            return None, 'inventory.py did not finish within %d seconds' % INVENTORY_TIMEOUT
        except OSError as e:
            return None, 'inventory.py could not be started (%s)' % type(e).__name__
        raw = None
        if os.path.isfile(out):
            with open(out, 'rb') as fh:
                raw = fh.read()
    lines = run.stdout.decode('utf-8', 'replace').splitlines()
    printed = [m.group(1) for m in (re.fullmatch(r'INVENTORY DIGEST ([0-9a-f]{64})', x.rstrip('\r')) for x in lines)
               if m]
    verdicts = [x.rstrip('\r') for x in lines if re.match(r'INVENTORY (HELD|FAILED)', x)]
    from_json, json_problem = (None, 'it wrote no JSON') if raw is None else inventory_from_json_bytes(raw)
    digest = None
    if len(printed) == 1 and (from_json is None or from_json == printed[0]):
        digest = printed[0]
    elif len(printed) == 0 and from_json is not None:
        digest = from_json
    why = []
    if run.returncode != 0:
        said = verdicts[-1] if verdicts else 'no verdict line'
        errs = [x.strip() for x in run.stderr.decode('utf-8', 'replace').splitlines() if x.strip()]
        if not verdicts and errs:
            said += '; its last error line: %s' % ascii(errs[-1][:200])
        why.append('inventory.py exited %d (%s)' % (run.returncode, said))
    if len(printed) != 1:
        why.append('inventory.py printed %d "INVENTORY DIGEST" lines, not 1' % len(printed))
    if json_problem:
        why.append('its JSON: %s' % json_problem)
    if len(printed) == 1 and from_json is not None and from_json != printed[0]:
        why.append('its JSON digest differs from the digest it printed')
    if why:
        return digest, '; '.join(why)
    return digest, None


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


def judge_rel(path, root):
    """The '/' path of path under root, lower-cased, or None when path is not under root. Both are resolved first
    (a volume GUID path becomes its drive's form; a long-path prefix given is kept), then the prefix is taken off."""
    a = os.path.normcase(plain(os.path.realpath(os.path.abspath(path))))
    r = os.path.normcase(plain(os.path.realpath(os.path.abspath(root))))
    try:
        if os.path.commonpath([a, r]) != r:
            return None
    except ValueError:
        return None
    return os.path.relpath(a, r).replace(os.sep, '/').lower()


def would_be_judged(rel):
    """True when a file at this lower-cased path would be a judge file (case folded, to refuse on every system)."""
    for _name, kind, gpath, _pattern, _required in GROUPS:
        g = gpath.lower()
        if kind == 'file' and rel == g:
            return True
        if kind == 'top-py' and '/' not in rel and rel.endswith('.py'):
            return True
        if kind in ('tree', 'tree-py') and (rel == g or rel.startswith(g + '/')):
            return True
        if kind == 'map-frozen':
            parts = rel.split('/')
            if rel == g or (len(parts) == 4 and '/'.join(parts[:2]) == FROZEN_TOP.lower() and parts[2]
                            and parts[3] == FROZEN_NAME.lower()):
                return True
        if kind == 'workflows' and rel.startswith(g + '/') and '/' not in rel[len(g) + 1:] \
                and rel.endswith(WORKFLOW_SUFFIXES):
            return True
    return False


def parse(argv):
    ap = argparse.ArgumentParser(prog='judge_digest.py', allow_abbrev=False, add_help=False,
                                 description='The CI judge digest (MK_ANCHOR_CI).')
    ap.add_argument('--root', required=True, help='the repository root')
    ap.add_argument('--inventory-json', help='the JSON tools/ci/inventory.py wrote for this root')
    ap.add_argument('--json', dest='json_out', help='write the run as JSON here (not a judge file)')
    ap.add_argument('--expect', help='the expected digest (the value of MK_ANCHOR_CI)')
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise Usage('--root is not a folder')
    if args.json_out is not None:
        rel = judge_rel(args.json_out, root)
        if rel is not None and would_be_judged(rel):
            raise Usage('--json names a path among the judge files (%s); write it elsewhere' % rel)
        # an existing file with another name (a hard link, which realpath does not merge): the other name, which may
        # be a judge file, would be written too
        try:
            nlink = os.stat(args.json_out).st_nlink
        except OSError:
            nlink = 0
        if nlink > 1:
            raise Usage('--json names a file that has another name (a hard link); write a new file')
    return args, root


def row(name, ok, detail):
    return {'name': name, 'ok': bool(ok), 'detail': detail}


def judge(args, root):
    files, counts, problems = collect(root)
    rows = []
    for name, kind, rel, pattern, required in GROUPS:
        n = counts[name]
        if kind == 'map-frozen':
            has_map = files.get(rel, (None, None))[1] == name
            lack = ([] if has_map else [rel]) + ([] if n > (1 if has_map else 0) else
                                                 ['%s/*/%s' % (FROZEN_TOP, FROZEN_NAME)])
            ok = not (required and lack)
            rows.append(row('group ' + name, ok, '%d file(s): %s' % (n, pattern) if ok
                            else '%d file(s), no %s: %s' % (n, ' and no '.join(lack), pattern)))
            continue
        rows.append(row('group ' + name, n > 0 or not required, '%d file(s): %s' % (n, pattern) if n or not required
                        else 'no file: %s' % pattern))
    rows.append(row('judge files are plain files', not problems,
                    '%d file(s) read' % len(files) if not problems else '; '.join(sorted(set(problems)))))
    with open(os.path.abspath(__file__), 'rb') as fh:
        own = sha_bytes(fh.read())
    judged = files.get(SELF_PATH)
    if judged is None:
        rows.append(row('this judge is the judged one', False, 'the root holds no %s' % SELF_PATH))
    elif judged[0] != own:
        rows.append(row('this judge is the judged one', False, 'the running script (%s) is not %s (%s)'
                        % (own[:16], SELF_PATH, judged[0][:16])))
    else:
        rows.append(row('this judge is the judged one', True, '%s %s' % (SELF_PATH, own[:16])))
    if args.inventory_json is not None:
        source = 'inventory-json'
        inv, problem = inventory_from_file(args.inventory_json)
    else:
        source = 'inventory.py'
        inv, problem = inventory_from_run(root)
    if problem:
        rows.append(row('inventory digest', False, problem))
    else:
        rows.append(row('inventory digest', True, '%s (from %s)' % (inv, source)))
    digest = digest_of([(p, s) for p, (s, _g) in files.items()], inv) if inv else None
    if args.expect is not None:
        others = any(not r['ok'] for r in rows)
        tail = ' (other rows failed too: mend them first)' if others else ''
        if digest is None:
            rows.append(row('expected digest', False, 'no digest: the inventory digest is missing'))
        elif not HEX64.fullmatch(args.expect):
            rows.append(row('expected digest', False, 'the expected value is not 64 lower-case hex digits (is '
                            'MK_ANCHOR_CI set?); after review the owner sets MK_ANCHOR_CI to %s%s' % (digest, tail)))
        elif args.expect != digest:
            rows.append(row('expected digest', False, 'the CI judge changed: after review the owner sets MK_ANCHOR_CI '
                            'to %s%s' % (digest, tail)))
        else:
            rows.append(row('expected digest', True, 'equal to the expected digest %s (in the workflow, MK_ANCHOR_CI)'
                            % digest[:16]))
    failed = sum(1 for r in rows if not r['ok'])
    if failed:
        verdict = 'CI JUDGE FAILED: %d of %d rows failed' % (failed, len(rows))
    else:
        verdict = 'CI JUDGE HELD: %d of %d rows' % (len(rows), len(rows))
    record = {
        'schema': SCHEMA,
        'digest': digest,
        'inventory_digest': inv,
        'inventory_source': source,
        'expect': args.expect,
        'files': [{'path': p, 'sha256': s, 'group': g} for p, (s, g) in sorted(files.items(), key=path_key)],
        'groups': [{'name': n, 'pattern': pat, 'files': counts[n], 'required': req} for n, _k, _r, pat, req in GROUPS],
        'rows': rows,
        'verdict': verdict,
        'held': not failed,
    }
    return record


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors='backslashreplace', newline='\n')  # the same bytes on Windows as on Linux
    except (AttributeError, ValueError):
        pass
    try:
        args, root = parse(sys.argv[1:] if argv is None else argv)
    except Usage as e:
        print('judge_digest.py: usage error: %s' % e, file=sys.stderr)
        return 2
    record = judge(args, root)
    if args.json_out is not None:
        data = (json.dumps(record, sort_keys=True, indent=1) + '\n').encode('ascii')
        try:
            with open(args.json_out, 'wb') as fh:
                fh.write(data)
        except OSError as e:
            print('judge_digest.py: usage error: --json cannot be written (%s)' % type(e).__name__, file=sys.stderr)
            return 2
    for r in record['rows']:
        print('  %s %s  %s' % (r['name'].ljust(ROW_WIDTH), 'ok' if r['ok'] else 'FAIL', r['detail']))
    print('CI JUDGE DIGEST %s' % (record['digest'] or 'none'))
    print(record['verdict'])
    return 0 if record['held'] else 1


if __name__ == '__main__':
    sys.exit(main())
