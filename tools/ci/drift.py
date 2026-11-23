# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/drift.py: how far one of Skuldd's copies (orlog/ or verdandi/) stands from its original repository, and
# whether every difference has a listed reason. Standard library only (Python 3.12 or later). It reads the tree and,
# through git's read-only plumbing (rev-parse, merge-base, ls-tree, cat-file, log), a clone of the original; it writes
# nothing and uses no network. Every path it is given comes from its options; it prints no path it was given.
#
#   python3 -B tools/ci/drift.py --root ROOT --part orlog|verdandi --origin REPO --later BRANCH [--show-paths]
#
#   --root        the Skuldd tree's top folder (it holds PROVENANCE.md, MANIFEST.<part>.txt, CHANGES-AFTER-IMPORT.md)
#   --part        orlog or verdandi
#   --origin      a git clone of the original repository holding the pins' history (fetch-depth 0 on GitHub)
#   --later       a branch of that clone to measure against, refs/heads/<name> or refs/remotes/<name> (main,
#                 origin/main). HEAD, a tag or a commit id is refused as a usage error: a checkout's HEAD can be the
#                 pin itself, and a comparison of the pin with itself shows nothing.
#   --show-paths  print every path. Without it a path that is not in this tree (a file removed here, a file added in
#                 the original) is printed as its sha256's first 16 digits, so a public log names no file this tree
#                 does not hold.
#
# The pin. PROVENANCE.md's table row for `<part>/` names the import pin ("commit <40 hex>, tree <40 hex>"). A re-pin
# adds a dated note, one line, of the form
#   Re-pin YYYY-MM-DD: `<part>/` pinned at commit <40 hex>, tree <40 hex>. <words>
# and the last such note for the part names the current pin.
#
# The reasons. CHANGES-AFTER-IMPORT.md holds one or more sections whose heading starts "## Drift classification".
# Inside them every table line is the header, the separator or a row
#   | `<part>/<path>` | <sha256 before or absent> | <sha256 after or removed> | <class> |
# with <class> one of
#   RE-PIN <40 hex>                       the file now equals the original at that commit (a pin PROVENANCE.md names)
#   SKULDD-ONLY BY RULING <id>            a change ruled for Skuldd's copy alone, e.g. "C2 (b)", "S6 (a) (1)", "SY-1"
#   SENT BACK Orlog pull request #<n>     a Skuldd change sent back to the original by its own route (orlog/ rows)
#   SENT BACK Verdandi patch <file>.patch (verdandi/ rows; both names are read with their diacritics too)
# A path may write a host's name as <host>; such a row matches a path of that shape whose bytes it names. For a
# classification row, before is the pin's sha256 (absent: the pin has no such file) and after the file's sha256 here
# (removed: this tree has none). For a RE-PIN row, before is the file here before the re-pin and after the new pin's.
# Rows are history: they are appended, never rewritten, and for a path the last row naming it is the one that counts.
#
# Rows, each ok or FAIL:
#   D1  PROVENANCE.md names the part's import pin once; every pin it names (import and re-pins) is a commit of the
#       origin whose tree id is the one recorded; the current pin is the last re-pin note's, or the import pin
#   D2  MANIFEST.<part>.txt is the import pin's tree: the same paths, each sha256 that of the pin's blob
#   D3  the manifest, with the RE-PIN rows laid over it in order, is the current pin's tree (paths and sha256), and
#       each RE-PIN row names a pin PROVENANCE.md names
#   D4  the current pin is the later branch's commit or an ancestor of it (a pin on a side branch fails here)
#   D5  every file here that differs from the current pin (changed, removed, added) has, as the last row naming it, a
#       SKULDD-ONLY or SENT BACK row whose before is the pin's sha256 and whose after is this file's
#   D6  every table line in the classification sections parses, and a SENT BACK row names its own part's route
# Then the origin's side: the files that differ between the current pin and the later branch (changed, added,
# removed in the original since the pin). They need a re-pin, or a reason in the push restatement; this script cannot
# judge that reason.
#
# Last lines: one "DRIFT LINE <part> ..." for a build-log entry, then one verdict:
#   "DRIFT HELD: n of n rows"                                   exit 0  nothing differs without a listed reason, and
#                                                                       the original has not moved since the pin
#   "DRIFT ORIGIN AHEAD: n of n rows held; k files differ ..."  exit 3  the rows hold; the original moved since the pin
#   "DRIFT FAILED: k of n rows failed"                          exit 1
# Exit 2 on a usage error (an unknown or abbreviated option, --help among them; a root that is not a Skuldd tree; an
# origin that is not a git repository's top folder; --later that is not a branch), with no verdict line.
#
# What a pass shows: on these inputs, this tree's copy is the pinned commit's tree but for files whose last listed
# reason names their exact bytes, and the pin lies on the later branch. What it does not show:
#   - that a ruling id names a real ruling, or that a SENT BACK patch or pull request exists or was applied (words);
#   - that the later branch is the original's main on GitHub: a local clone shows what it last fetched (the line
#     "later" gives the branch's commit and date, and when the clone last fetched, if git recorded it);
#   - files in folders named .git, out4, libcache, build or __pycache__ (skipped, as tools/check_manifests.py skips
#     them), a file's mode, or a link's target as git would store it (a link here is read through);
#   - line-ending conversion: it compares the bytes on disk with git's blobs; .gitattributes (eol=lf) and the
#     manifests check are what keep a checkout's bytes the blob's bytes.
import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
except (AttributeError, ValueError):
    pass

NAME = 'DRIFT'
PARTS = ('orlog', 'verdandi')
SKIP = {'.git', 'out4', 'libcache', 'build', '__pycache__'}
HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
IMPORT_ROW = re.compile(r'^\| `(orlog|verdandi)/` \|.*?\bcommit ([0-9a-f]{40}), tree ([0-9a-f]{40})\b')
REPIN_NOTE = re.compile(r'^Re-pin (\d{4}-\d{2}-\d{2}): `(orlog|verdandi)/` pinned at commit ([0-9a-f]{40}), '
                        r'tree ([0-9a-f]{40})\.')
SECTION = re.compile(r'^## Drift classification\b')
HEADING = re.compile(r'^#{1,6} ')
ROW = re.compile(r'^\| `((?:orlog|verdandi)/[^`|]+)` \| (absent|[0-9a-f]{64}) \| (removed|[0-9a-f]{64}) \| '
                 r'([^|]*[^| ]) \|$')
HEADER = re.compile(r'^\| File \| sha256 before \| sha256 after \| Class \|$')
SEPARATOR = re.compile(r'^\|(?: ?:?-{3,}:? ?\|){4}$')
RULING_ID = r'[A-Z][A-Z0-9]*(?:-[0-9]+)?(?: \([a-z0-9]+\))*'
CLASSES = (
    ('RE-PIN', re.compile(r'RE-PIN ([0-9a-f]{40})')),
    ('SKULDD-ONLY', re.compile(r'SKULDD-ONLY BY RULING (%s)' % RULING_ID)),
    ('SENT BACK', re.compile(r'SENT BACK (?:(?:Orlog|\u00d8rl\u01ebg) pull request #[1-9][0-9]*|'
                             r'(?:Verdandi|Ver\u00f0andi) patch [A-Za-z0-9][A-Za-z0-9._-]*\.patch)')),
)
BRANCH = re.compile(r'[A-Za-z0-9_][A-Za-z0-9._/-]*')
NOT_BRANCHES = {'HEAD', 'FETCH_HEAD', 'ORIG_HEAD', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REBASE_HEAD'}
SHOWN = 200


class Usage(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Origin:
    """Read-only git plumbing on the original's clone (every call: fixed argument list, no shell, no write)."""

    def __init__(self, path):
        self.path = path
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', LC_ALL='C')
        for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_NAMESPACE'):
            self.env.pop(k, None)

    def git(self, args, data=None, ok=(0,)):
        p = subprocess.run(['git', '-C', self.path] + args, input=data, cwd=self.path, env=self.env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode not in ok:
            raise RuntimeError('git %s exited %d: %s' % (args[0], p.returncode,
                                                         p.stderr.decode('utf-8', 'replace').strip()[:160]))
        return p

    def commit(self, rev):
        """The commit id rev names, or None."""
        p = self.git(['rev-parse', '--verify', '--quiet', rev + '^{commit}'], ok=(0, 1, 128))
        out = p.stdout.decode('ascii', 'replace').strip()
        return out if p.returncode == 0 and HEX40.fullmatch(out) else None

    def tree_id(self, commit):
        return self.git(['rev-parse', '--verify', commit + '^{tree}']).stdout.decode('ascii').strip()

    def is_ancestor(self, a, b):
        return self.git(['merge-base', '--is-ancestor', a, b], ok=(0, 1)).returncode == 0

    def date(self, commit):
        return self.git(['log', '-1', '--format=%cI', commit]).stdout.decode('ascii', 'replace').strip()

    def full_name(self, ref):
        p = self.git(['rev-parse', '--symbolic-full-name', ref], ok=(0, 128))
        return p.stdout.decode('utf-8', 'replace').strip() if p.returncode == 0 else ''

    def fetched(self):
        p = self.git(['rev-parse', '--git-path', 'FETCH_HEAD'], ok=(0, 128))
        where = os.path.join(self.path, p.stdout.decode('utf-8', 'replace').strip())
        try:
            t = os.stat(where).st_mtime
        except OSError:
            return 'no fetch recorded'
        return 'last fetched %s' % datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def files(self, commit, prefix):
        """{prefix/path: sha256} of every blob of the commit's tree, its bytes read through cat-file."""
        out = self.git(['ls-tree', '-r', '-z', '--full-tree', commit]).stdout
        entries = []
        for rec in out.split(b'\0'):
            if not rec:
                continue
            meta, path = rec.split(b'\t', 1)
            mode, kind, oid = meta.split()
            if kind != b'blob':
                raise RuntimeError('the tree of %s holds a %s, which this script does not compare'
                                   % (commit[:12], kind.decode('ascii', 'replace')))
            entries.append((prefix + '/' + path.decode('utf-8', 'surrogateescape'), oid.decode('ascii')))
        data = self.git(['cat-file', '--batch'], data=''.join(o + '\n' for _, o in entries).encode('ascii')).stdout
        result, at = {}, 0
        for path, oid in entries:
            nl = data.index(b'\n', at)
            head = data[at:nl].split()
            if len(head) != 3 or head[0].decode('ascii') != oid or head[1] != b'blob':
                raise RuntimeError('cat-file gave an unexpected header for %s' % oid[:12])
            size = int(head[2])
            body = data[nl + 1:nl + 1 + size]
            result[path] = sha(body)
            at = nl + 1 + size + 1
        return result


def tree_files(root, part):
    out = {}
    base = os.path.join(root, part)
    for dp, dn, fn in os.walk(base):
        dn[:] = sorted(d for d in dn if d not in SKIP)
        for f in fn:
            p = os.path.join(dp, f)
            with open(p, 'rb') as fh:
                out[part + '/' + os.path.relpath(p, base).replace(os.sep, '/')] = sha(fh.read())
    return out


def read_text(root, name):
    with open(os.path.join(root, name), 'rb') as fh:
        return fh.read().decode('utf-8')


def pattern(path):
    """A row's path as a pattern: <host> stands for one path segment's part."""
    return re.compile('[^/]+'.join(re.escape(x) for x in path.split('<host>')))


def classify(text, part):
    """(rows, problems): rows [(line, path, before, after, kind, value)] of the part, in file order."""
    rows, problems, inside = [], [], False
    for n, line in enumerate(text.split('\n'), 1):
        line = line.rstrip('\r')
        if HEADING.match(line):
            inside = bool(SECTION.match(line))
            continue
        if not inside or not line.startswith('|'):
            continue
        if HEADER.match(line) or SEPARATOR.match(line):
            continue
        m = ROW.match(line)
        if not m:
            problems.append('CHANGES-AFTER-IMPORT.md line %d is not a classification row' % n)
            continue
        path, before, after, cls = m.groups()
        kind = value = None
        for k, rx in CLASSES:
            c = rx.fullmatch(cls)
            if c:
                kind, value = k, c.group(0)
        if kind is None:
            problems.append('CHANGES-AFTER-IMPORT.md line %d: "%s" is no class' % (n, cls[:60]))
            continue
        if not path.startswith(part + '/'):
            continue
        if kind == 'SENT BACK' and (('patch' in value) != (part == 'verdandi')):
            problems.append('CHANGES-AFTER-IMPORT.md line %d: a %s/ file sent back by the other repository\'s route'
                            % (n, part))
            continue
        if '<host>' in path and after != 'removed':
            problems.append('CHANGES-AFTER-IMPORT.md line %d: <host> in the path of a file that is still here' % n)
            continue
        rows.append((n, path, before, after, kind, value))
    return rows, problems


def last_row(rows, path, kinds):
    found = None
    for r in rows:
        if r[4] in kinds and pattern(r[1]).fullmatch(path):
            found = r
    return found


def run(a):
    root, part = a.root, a.part
    origin = Origin(a.origin)
    later_ref = a.later
    later = origin.commit(later_ref)
    if later is None:
        raise Usage('--later names no commit of the origin')
    rows = []

    def row(rid, ok, detail):
        rows.append((rid, bool(ok), detail))

    # D1: the pins
    prov = read_text(root, 'PROVENANCE.md').split('\n')
    imports = [m.groups() for m in (IMPORT_ROW.match(x.rstrip('\r')) for x in prov) if m and m.group(1) == part]
    notes = [m.groups() for m in (REPIN_NOTE.match(x.rstrip('\r')) for x in prov) if m and m.group(2) == part]
    bad = []
    if len(imports) != 1:
        bad.append('PROVENANCE.md names the import pin of %s/ %d times, not once' % (part, len(imports)))
    named = [(c, t, 'the import pin') for _, c, t in imports] + [(c, t, 'the re-pin of %s' % d) for d, _, c, t in notes]
    for c, t, what in named:
        if origin.commit(c) != c:
            bad.append('%s %s is no commit of the origin' % (what, c[:12]))
        elif origin.tree_id(c) != t:
            bad.append('%s %s has tree %s, not the recorded %s' % (what, c[:12], origin.tree_id(c)[:12], t[:12]))
    pins = {c for c, _, _ in named}
    current = notes[-1][2] if notes else (imports[0][1] if imports else None)
    row('D1', not bad and current, '; '.join(bad) if bad else 'import pin %s%s; current pin %s' % (
        imports[0][1][:12], ', %d re-pin note(s)' % len(notes) if notes else ', no re-pin note', current[:12]))
    if bad or not current:
        return rows, None
    import_pin = imports[0][1]
    here = tree_files(root, part)

    # D2: the manifest is the import pin's tree
    manifest, mbad = {}, []
    for n, line in enumerate(read_text(root, 'MANIFEST.%s.txt' % part).split('\n'), 1):
        if not line.strip():
            continue
        h, sep, path = line.partition('  ')
        if not sep or not HEX64.fullmatch(h) or not path.startswith(part + '/') or path in manifest:
            mbad.append('MANIFEST.%s.txt line %d is not "64 hex, two spaces, %s/<path>", once' % (part, n, part))
            continue
        manifest[path] = h
    pinned0 = origin.files(import_pin, part)
    diff = sorted(p for p in set(manifest) | set(pinned0) if manifest.get(p) != pinned0.get(p))
    row('D2', not mbad and not diff, '; '.join(mbad[:3]) if mbad else (
        '%d path(s) differ between the manifest and the import pin, e.g. %s' % (len(diff), show(diff[0], a, here))
        if diff else 'MANIFEST.%s.txt is the import pin\'s tree: %d files' % (part, len(manifest))))

    # D3: manifest + RE-PIN rows == the current pin's tree
    crows, cproblems = classify(read_text(root, 'CHANGES-AFTER-IMPORT.md'), part)
    pinned = pinned0 if current == import_pin else origin.files(current, part)
    overlay, obad = dict(manifest), []
    for n, path, before, after, kind, value in crows:
        if kind != 'RE-PIN':
            continue
        if value[len('RE-PIN '):] not in pins:
            obad.append('line %d re-pins to %s, a commit PROVENANCE.md names as no pin' % (n, value[7:19]))
        targets = [p for p in set(overlay) | set(pinned) if pattern(path).fullmatch(p)] if '<host>' in path \
            else [path]
        for p in targets:
            if after == 'removed':
                overlay.pop(p, None)
            else:
                overlay[p] = after
    odiff = sorted(p for p in set(overlay) | set(pinned) if overlay.get(p) != pinned.get(p))
    row('D3', not obad and not odiff, '; '.join(obad[:3]) if obad else (
        '%d path(s) where the manifest and the RE-PIN rows do not give the current pin, e.g. %s' % (
            len(odiff), show(odiff[0], a, here)) if odiff else
        'the manifest%s: the current pin\'s tree, %d files' % (
            ' and %d RE-PIN row(s)' % sum(1 for r in crows if r[4] == 'RE-PIN') if current != import_pin or
            any(r[4] == 'RE-PIN' for r in crows) else '', len(pinned))))

    # D4: the pin lies on the later branch
    on = origin.is_ancestor(current, later)
    row('D4', on, 'the current pin %s %s %s (%s)%s' % (
        current[:12], 'is on' if on else 'is NOT on', later_ref, later[:12], '' if on else
        ': the pin has %s commit(s) the branch lacks' % origin.git(
            ['rev-list', '--count', later + '..' + current]).stdout.decode('ascii').strip()))

    # D5: Skuldd's side, each difference with its reason
    differ = sorted(p for p in set(here) | set(pinned) if here.get(p) != pinned.get(p))
    reasons, unexplained = {}, []
    for p in differ:
        before, after = pinned.get(p, 'absent'), here.get(p, 'removed')
        r = last_row(crows, p, ('SKULDD-ONLY', 'SENT BACK'))
        if r and r[2] == before and r[3] == after:
            reasons[p] = '%s (line %d)' % (r[5], r[0])
        else:
            unexplained.append(p)
            reasons[p] = 'UNEXPLAINED' + (' (its last row, line %d, names other bytes)' % r[0] if r else '')
    row('D5', not unexplained, '%d file(s) differ from the pin: %d with their reason, %d without%s' % (
        len(differ), len(differ) - len(unexplained), len(unexplained),
        (', e.g. ' + show(unexplained[0], a, here)) if unexplained else ''))

    # D6: the rows parse
    row('D6', not cproblems, '; '.join(cproblems[:3]) if cproblems else '%d classification row(s) for %s/' % (
        len(crows), part))

    # the origin's side
    later_files = origin.files(later, part) if later != current else pinned
    ahead = sorted(p for p in set(pinned) | set(later_files) if pinned.get(p) != later_files.get(p))
    info = {'later_ref': later_ref, 'later': later, 'later_date': origin.date(later), 'fetched': origin.fetched(),
            'current': current, 'here': here, 'pinned': pinned, 'later_files': later_files, 'differ': differ,
            'reasons': reasons, 'unexplained': unexplained, 'ahead': ahead}
    return rows, info


def show(p, a, here):
    """A path, or, unless --show-paths, its sha256's first digits when this tree has no such file."""
    return p if a.show_paths or p in here else '(a path not in this tree)'


def kind_of(p, info):
    s, p0, l = info['here'].get(p), info['pinned'].get(p), info['later_files'].get(p)
    if s == p0:
        return 'origin-' + ('added' if p0 is None else 'removed' if l is None else 'changed')
    if l == p0:
        return 'skuldd-' + ('added' if p0 is None else 'removed' if s is None else 'changed')
    return 'same-change' if s == l else 'both'


def report(a, rows, info):
    for rid, ok, detail in rows:
        print('  %-3s %-4s  %s' % (rid, 'ok' if ok else 'FAIL', detail))
    if info:
        print('  later     %s = %s, committed %s; %s' % (info['later_ref'], info['later'][:12], info['later_date'],
                                                        info['fetched']))
        listed = sorted(set(info['differ']) | set(info['ahead']))
        for p in listed[:SHOWN]:
            k = kind_of(p, info)
            name = p if (a.show_paths or p in info['here']) else '(not in this tree; sha256 %s)' % (
                (info['pinned'].get(p) or info['later_files'].get(p))[:16])
            why = info['reasons'].get(p, 'needs a re-pin or a reason')
            if k == 'both':
                why += '; the original changed it too since the pin'
            print('    %-15s %s  %s' % (k, name, why))
        if len(listed) > SHOWN:
            print('    ... %d more' % (len(listed) - SHOWN))
        same = len(set(info['here']) | set(info['pinned']) | set(info['later_files'])) - len(listed)
        print('DRIFT LINE %s pin %s later %s %s (%s): same %d, skuldd-side %d (%d with reason, %d unexplained), '
              'origin-ahead %d' % (a.part, info['current'][:12], info['later_ref'], info['later'][:12],
                                   info['later_date'][:10], same, len(info['differ']),
                                   len(info['differ']) - len(info['unexplained']), len(info['unexplained']),
                                   len(info['ahead'])))
    failed = sum(1 for r in rows if not r[1])
    if failed:
        print('%s FAILED: %d of %d rows failed' % (NAME, failed, len(rows)))
        return 1
    if info['ahead']:
        print('%s ORIGIN AHEAD: %d of %d rows held; %d file(s) differ between the pin and %s' % (
            NAME, len(rows), len(rows), len(info['ahead']), info['later_ref']))
        return 3
    print('%s HELD: %d of %d rows' % (NAME, len(rows), len(rows)))
    return 0


def main(argv):
    ap = Parser(prog='drift.py', allow_abbrev=False, add_help=False,
                description='Drift of a Skuldd copy from its original (see the header of this file).')
    ap.add_argument('--root', required=True)
    ap.add_argument('--part', required=True, choices=PARTS)
    ap.add_argument('--origin', required=True)
    ap.add_argument('--later', required=True)
    ap.add_argument('--show-paths', action='store_true')
    try:
        a = ap.parse_args(argv)
        a.root, a.origin = os.path.abspath(a.root), os.path.abspath(a.origin)
        for name in ('PROVENANCE.md', 'MANIFEST.%s.txt' % a.part, 'CHANGES-AFTER-IMPORT.md'):
            if not os.path.isfile(os.path.join(a.root, name)):
                raise Usage('--root is not a Skuldd tree: it holds no %s' % name)
        if not os.path.isdir(os.path.join(a.root, a.part)):
            raise Usage('--root holds no folder %s/' % a.part)
        if not os.path.isdir(a.origin):
            raise Usage('--origin is not a folder')
        o = Origin(a.origin)
        top = o.git(['rev-parse', '--show-toplevel'], ok=(0, 128))
        top_dir = top.stdout.decode('utf-8', 'replace').strip()
        if top.returncode != 0 or not top_dir:
            raise Usage('--origin is not a git repository')
        if os.path.normcase(os.path.realpath(top_dir)) != os.path.normcase(os.path.realpath(a.origin)):
            raise Usage('--origin is a folder inside a repository, not its top folder (a copy inside another '
                        'repository would be read with that repository\'s history)')
        if not BRANCH.fullmatch(a.later) or a.later in NOT_BRANCHES or HEX40.fullmatch(a.later) or \
                re.fullmatch(r'[0-9a-f]{4,39}', a.later):
            raise Usage('--later must name a branch, not HEAD, a commit id or an option')
        full = o.full_name(a.later)
        if not (full.startswith('refs/heads/') or full.startswith('refs/remotes/')):
            raise Usage('--later must name a branch of the origin (refs/heads/ or refs/remotes/), not HEAD, a tag '
                        'or a commit: a checkout\'s HEAD can be the pin itself')
    except Usage as e:
        sys.stderr.write('drift.py: usage error: %s\n' % e)
        return 2
    print('drift.py: part %s' % a.part)
    try:
        rows, info = run(a)
    except Usage as e:
        sys.stderr.write('drift.py: usage error: %s\n' % e)
        return 2
    except (RuntimeError, OSError, UnicodeDecodeError, ValueError) as e:
        print('  ERR   %s' % str(e)[:200])
        print('%s FAILED: the inputs could not be read' % NAME)
        return 1
    if info is None:
        for rid, ok, detail in rows:
            print('  %-3s %-4s  %s' % (rid, 'ok' if ok else 'FAIL', detail))
        print('%s FAILED: %d of %d rows failed (the pins could not be read; nothing else was judged)' % (
            NAME, sum(1 for r in rows if not r[1]), len(rows)))
        return 1
    return report(a, rows, info)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
