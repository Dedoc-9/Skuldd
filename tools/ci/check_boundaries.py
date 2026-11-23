# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/check_boundaries.py: the boundary map, BOUNDARIES.md, held to THEOREMS.md's proved table (ruling BM-2 (a)).
# Standard library only (Python 3.12 or later). It reads the two files and tests that the paths the map names exist;
# it writes nothing.
#
#   python3 -B tools/ci/check_boundaries.py --root ROOT
#
# The map. A row is a level-3 heading "### B<three digits> <title>" followed by its seven fields, in this order, each a
# list item "- <Field>: <value>" whose value may go on over lines that start with two blanks; blank lines may stand
# between them, and nothing else may (the row ends at the next heading). The fields: Claim, Claimed in, Stop, Kind,
# Covers beyond, Grade, Proof again. Every level-3 heading of the file is a row's. Prose and level-2 headings may stand
# between rows. In the Claim field every backtick span is a statement's name: "<folder>.<Module>.<NAME>" (with or
# without "MKF.") or a bare name that continues the module of the name before it, as in THEOREMS.md's proved table;
# a Claim that starts with "PENDING " or "STATED " names statements that the proved table does not hold (a statement
# gated outside this tree, or stated and not proven in it).
#
# ROWS, one line each, "  <row> ok|FAIL  <detail>":
#   input     BOUNDARIES.md and THEOREMS.md are plain files at ROOT that read as UTF-8; BOUNDARIES.md holds no carriage
#             return, no tab and no other character outside printable ASCII but the three that the names of Orlog and
#             Verdandi hold (U+00D8, U+01EB, U+00F0); it opens no code fence (a line of up to three blanks and then
#             ``` or ~~~), holds an HTML comment only as one whole line, and starts no other line, after up to three
#             blanks, with "<" (GitHub shows a fence as code, hides a comment and shows an HTML block as raw or
#             preformatted text, any of which this check would read as rows); THEOREMS.md has exactly one proved
#             table (the table whose header's first cell is Folder and whose second starts with Statement, as
#             tools/ci/inventory.py reads it), naming at least one statement. When this row fails, no other row is
#             read.
#   rows      the map has at least one row; every level-3 heading is a row's, with an id no other row has; every row
#             has each of the seven fields once, in order, none empty or "-", and no other line (a row that lacks a
#             field fails here, and the rows below do not read that field)
#   kinds     every Kind is one of: input class, model, layer, trust (the four stops the ruling names)
#   grades    every Grade is one or more of GATED, MEASURED, ARGUED, DECLARED, NOT_MEASURED, written ", " apart, none
#             twice: the ruled list (a gated theorem, evidence graded MEASURED, ARGUED or DECLARED, or NOT_MEASURED)
#   evidence  a row graded MEASURED, ARGUED or DECLARED names its file in Covers beyond: a path of this tree in
#             backticks, or the sha256 (64 lower-case hex digits) of a record kept outside it; a row graded GATED names
#             there, in backticks, a statement of the proved table
#   paths     every backtick span of Claimed in and Covers beyond that reads as a path (no blank, and a "/" or a file
#             extension of the list EXTENSIONS) is relative, holds no "..", backslash, colon or pattern mark (<, >, *,
#             ?), and exists under ROOT
#   claims    a Claim names only statements of the proved table; a PENDING or STATED Claim names at least one statement
#             and none that the proved table holds (when a pending statement lands, its row must say what it covers)
#   coverage  every statement of the proved table is named by the Claim of a row that is not PENDING or STATED
#   stages    every Proof again starts "now: ", "Push A: ", "Push B: ", "Push B or later: ", "later: " or "never: " and
#             goes on after it: the stage where proof picks up again, or that it never does, and why
# Last line: "BOUNDARIES HELD: n of n rows" (exit 0) or "BOUNDARIES FAILED: k of n rows failed" (exit 1); exit 2 on a
# usage error (an unknown or abbreviated option, --help among them, no --root, or a root that is not a folder).
#
# What a pass shows: the map has a well-formed row for every statement of the proved table, each row graded in the
# ruled terms, its evidence named and its paths present. What it does not show: that a row is true, that its evidence
# says what the row says, that a stop is missing from the map, that no sentence of the tree claims past its row (the
# review before each push, under the ruling), or that a record cited by sha256 exists. BOUNDARIES.md is the judged
# file; since ruling S282-3 (b) it is also a judge file (the group boundaries-frozen of tools/ci/judge_digest.py), so a
# change to it moves MK_ANCHOR_CI. The tests of tools/ci build their maps in a temporary folder and never read it, and
# only the workflow's step runs this check on the tree.
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True

MAP = 'BOUNDARIES.md'
THEOREMS = 'THEOREMS.md'
FIELDS = ('Claim', 'Claimed in', 'Stop', 'Kind', 'Covers beyond', 'Grade', 'Proof again')
KINDS = ('input class', 'model', 'layer', 'trust')
GRADES = ('GATED', 'MEASURED', 'ARGUED', 'DECLARED', 'NOT_MEASURED')
FILE_GRADES = ('MEASURED', 'ARGUED', 'DECLARED')
STAGES = ('now', 'Push A', 'Push B', 'Push B or later', 'later', 'never')
EXTENSIONS = ('md', 'v', 'py', 'txt', 'c', 'h', 'yml', 'yaml', 'json', 'sh', 'hlsl', 'csv')
NON_ASCII = ''.join(map(chr, (0xD8, 0x1EB, 0xF0)))
ROW_NAMES = ('input', 'rows', 'kinds', 'grades', 'evidence', 'paths', 'claims', 'coverage', 'stages')
ROW_HEAD = re.compile(r'### (B[0-9]{3}) (\S.*)$')
ITEM = re.compile(r'- ([A-Za-z][A-Za-z ]*):(?: (.*))?$')
CONT = re.compile(r'  (\S.*)$')
SPAN = re.compile(r'`([^`]*)`')
SHA = re.compile(r'(?<![0-9A-Za-z])[0-9a-f]{64}(?![0-9A-Za-z])')
NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$')
STAGE = re.compile(r'(now|Push A|Push B or later|Push B|later|never): \S')
SHOW = 40
FENCE = re.compile(r' {0,3}(?:```|~~~)')
COMMENT_LINE = re.compile(r'<!--(?:(?!-->).)*-->')
HTML_START = re.compile(r' {0,3}<')


def read_text(root, rel):
    """(text, problem): the file's text, or None and why not."""
    path = os.path.join(root, rel)
    if os.path.islink(path) or not os.path.isfile(path):
        return None, '%s is not a plain file at the root' % rel
    try:
        with open(path, 'rb') as fh:
            return fh.read().decode('utf-8'), None
    except (OSError, UnicodeDecodeError) as e:
        return None, '%s cannot be read as UTF-8: %s' % (rel, type(e).__name__)


def cells(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def plain(cell):
    return re.sub(r'[*_`]', '', cell).strip()


def expand(spans, where):
    """(full names, problems) of backtick spans read as THEOREMS.md reads them: a bare name continues the module of the
    name before it."""
    names, bad, module = [], [], None
    for s in spans:
        s = s.strip()
        if s.startswith('MKF.'):
            s = s[4:]
        if not NAME.match(s):
            bad.append('%s: "%s" is not a name' % (where, s))
            continue
        if '.' in s:
            if s.count('.') < 2:
                bad.append('%s: "%s" is not <folder>.<Module>.<NAME>' % (where, s))
                continue
            module = s.rsplit('.', 1)[0]
            names.append(s)
        elif module is None:
            bad.append('%s: the bare name "%s" has no module before it' % (where, s))
        else:
            names.append(module + '.' + s)
    return names, bad


def proved_statements(text):
    """(set of full names, problem) from THEOREMS.md's proved table."""
    lines = [x[:-1] if x.endswith('\r') else x for x in text.split('\n')]
    heads = [i for i, x in enumerate(lines) if x.lstrip(' ').startswith('|') and len(cells(x)) >= 2
             and plain(cells(x)[0]).lower() == 'folder' and plain(cells(x)[1]).lower().startswith('statement')]
    if len(heads) != 1:
        return None, 'THEOREMS.md has %d proved tables (a header Folder, Statement), not one' % len(heads)
    i = heads[0] + 1
    if i >= len(lines) or '-' not in lines[i] or not set(lines[i].strip()) <= set('|-: '):
        return None, 'THEOREMS.md: the proved table has no delimiter row under its header'
    found = set()
    for x in lines[i + 1:]:
        if not x.lstrip(' ').startswith('|'):
            break
        c = cells(x)
        if len(c) < 2:
            return None, 'THEOREMS.md: a proved-table row with fewer than two cells'
        names, bad = expand(SPAN.findall(c[1]), 'THEOREMS.md')
        if bad:
            return None, bad[0]
        found.update(names)
    if not found:
        return None, 'THEOREMS.md: the proved table names no statement'
    return found, None


def parse_map(text):
    """(rows, problems): rows as dicts {id, title, line, fields: {name: value}}."""
    rows, bad = [], []
    lines = text.split('\n')
    cur = None
    for n, x in enumerate(lines, 1):
        if x.startswith('#'):
            cur = None
            if x.startswith('###'):
                m = ROW_HEAD.match(x)
                if not m:
                    bad.append('line %d: a level-3 heading that is not a row ("### B<nnn> <title>")' % n)
                    continue
                cur = {'id': m.group(1), 'title': m.group(2), 'line': n, 'items': [], 'stray': []}
                rows.append(cur)
            continue
        if cur is None or not x.strip():
            continue
        m = ITEM.match(x)
        if m:
            cur['items'].append([m.group(1), (m.group(2) or '').strip(), n])
        elif CONT.match(x) and cur['items']:
            cur['items'][-1][1] = (cur['items'][-1][1] + ' ' + x.strip()).strip()
        else:
            cur['stray'].append(n)
    if not rows:
        bad.append('the map has no row')
    seen = {}
    for r in rows:
        where = '%s (line %d)' % (r['id'], r['line'])
        if r['id'] in seen:
            bad.append('%s: the id is also the row at line %d' % (where, seen[r['id']]))
        seen.setdefault(r['id'], r['line'])
        for n in r['stray']:
            bad.append('%s: line %d is not a field or a field\'s continuation' % (where, n))
        names = [i[0] for i in r['items']]
        fields = {}
        for name, value, n in r['items']:
            if name not in FIELDS:
                bad.append('%s: line %d: "%s" is not one of the seven fields' % (where, n, name))
            elif name in fields:
                bad.append('%s: line %d: the field %s a second time' % (where, n, name))
            elif value in ('', '-'):
                bad.append('%s: line %d: the field %s is empty: the row lacks a field' % (where, n, name))
                fields[name] = None
            else:
                fields[name] = value
        for f in FIELDS:
            if f not in names:
                bad.append('%s: the row lacks the field %s' % (where, f))
        known = [x for x in names if x in FIELDS]
        if len(set(known)) == len(known) and len(known) == len(FIELDS) and tuple(known) != FIELDS:
            bad.append('%s: the fields are not in the order %s' % (where, ', '.join(FIELDS)))
        r['fields'] = {k: v for k, v in fields.items() if v is not None}
    return rows, bad


def field(r, name):
    return r['fields'].get(name)


def claim_mode(value):
    for mode in ('PENDING', 'STATED'):
        if value.startswith(mode + ' '):
            return mode
    return None


def check_rows(ctx):
    return list(ctx['row_problems'])


def check_kinds(ctx):
    bad = []
    for r in ctx['rows']:
        v = field(r, 'Kind')
        if v is not None and v not in KINDS:
            bad.append('%s: the kind "%s" is not one of: %s' % (r['id'], v, ', '.join(KINDS)))
    return bad


def check_grades(ctx):
    bad = []
    for r in ctx['rows']:
        v = field(r, 'Grade')
        if v is None:
            continue
        parts = v.split(', ')
        for p in parts:
            if p not in GRADES:
                bad.append('%s: the grade "%s" is not one of: %s' % (r['id'], p, ', '.join(GRADES)))
        if len(set(parts)) != len(parts):
            bad.append('%s: a grade is written twice in "%s"' % (r['id'], v))
    return bad


def looks_like_path(s):
    if not s or re.search(r'\s', s):
        return False
    if '/' in s or '\\' in s:
        return True
    return bool(re.search(r'\.(%s)$' % '|'.join(EXTENSIONS), s))


def path_problem(root, s):
    if s.startswith('/') or '\\' in s or ':' in s:
        return 'is not a relative path written with "/"'
    if re.search(r'[<>*?]', s):
        return 'is a pattern, not a path'
    parts = [p for p in s.split('/') if p]
    if '..' in parts or '.' in parts:
        return 'holds "." or ".."'
    if not os.path.exists(os.path.join(root, *parts)):
        return 'is not in this tree'
    return None


def check_evidence(ctx):
    bad = []
    for r in ctx['rows']:
        v, beyond = field(r, 'Grade'), field(r, 'Covers beyond')
        if v is None or beyond is None:
            continue
        grades = v.split(', ')
        spans = SPAN.findall(beyond)
        if any(g in grades for g in FILE_GRADES):
            files = [s for s in spans if looks_like_path(s) and path_problem(ctx['root'], s) is None]
            if not files and not SHA.search(beyond):
                bad.append('%s: graded %s, and Covers beyond names no file of this tree in backticks and no sha256'
                           % (r['id'], v))
        if 'GATED' in grades:
            named = [s[4:] if s.startswith('MKF.') else s for s in spans]
            if not any(s in ctx['proved'] for s in named):
                bad.append('%s: graded GATED, and Covers beyond names no statement of the proved table' % r['id'])
    return bad


def check_paths(ctx):
    bad = []
    for r in ctx['rows']:
        for name in ('Claimed in', 'Covers beyond'):
            v = field(r, name)
            if v is None:
                continue
            for s in SPAN.findall(v):
                if looks_like_path(s):
                    why = path_problem(ctx['root'], s)
                    if why:
                        bad.append('%s: %s: `%s` %s' % (r['id'], name, s, why))
    return bad


def check_claims(ctx):
    bad = []
    for r in ctx['rows']:
        v = field(r, 'Claim')
        if v is None:
            continue
        names, problems = expand(SPAN.findall(v), r['id'])
        bad.extend(problems)
        mode = claim_mode(v)
        if mode:
            if not names and not problems:
                bad.append('%s: a %s claim names no statement' % (r['id'], mode))
            for s in names:
                if s in ctx['proved']:
                    bad.append('%s: a %s claim names %s, which the proved table holds' % (r['id'], mode, s))
        else:
            for s in names:
                if s not in ctx['proved']:
                    bad.append('%s: names %s, which is not a statement of the proved table' % (r['id'], s))
    return bad


def check_coverage(ctx):
    named = set()
    for r in ctx['rows']:
        v = field(r, 'Claim')
        if v is None or claim_mode(v):
            continue
        named.update(expand(SPAN.findall(v), r['id'])[0])
    return ['%s has no row: no Claim names it' % s for s in sorted(ctx['proved'] - named)]


def check_stages(ctx):
    bad = []
    for r in ctx['rows']:
        v = field(r, 'Proof again')
        if v is not None and not STAGE.match(v):
            bad.append('%s: Proof again "%s" does not start with a stage (%s) and its reason'
                       % (r['id'], v[:40], ', '.join(s + ':' for s in STAGES)))
    return bad


CHECKS = (('rows', check_rows), ('kinds', check_kinds), ('grades', check_grades), ('evidence', check_evidence),
          ('paths', check_paths), ('claims', check_claims), ('coverage', check_coverage), ('stages', check_stages))


def read_input(root):
    """(ctx, problem)."""
    text, why = read_text(root, MAP)
    if why:
        return None, why
    for n, line in enumerate(text.split('\n'), 1):
        for ch in line:
            if not (' ' <= ch <= '~' or ch in NON_ASCII):
                return None, 'BOUNDARIES.md line %d holds U+%04X, outside the characters it may hold' % (n, ord(ch))
        if FENCE.match(line):
            return None, ('BOUNDARIES.md line %d opens a code fence (GitHub shows it as code; this check would read it)'
                          % n)
        if ('<!--' in line or '-->' in line) and not COMMENT_LINE.fullmatch(line):
            return None, ('BOUNDARIES.md line %d holds an HTML comment that is not one whole line (GitHub hides it)'
                          % n)
        if HTML_START.match(line) and not COMMENT_LINE.fullmatch(line):
            return None, ('BOUNDARIES.md line %d starts an HTML block (GitHub shows its lines as HTML, not as rows)'
                          % n)
    ttext, why = read_text(root, THEOREMS)
    if why:
        return None, why
    proved, why = proved_statements(ttext)
    if why:
        return None, why
    rows, row_problems = parse_map(text)
    return {'root': root, 'rows': rows, 'row_problems': row_problems, 'proved': proved}, None


def check(root):
    """(held, lines)."""
    out = ['check_boundaries.py: %s against the proved table of %s' % (MAP, THEOREMS)]
    ctx, why = read_input(root)
    if why:
        out.append('  input     FAIL  %s' % why)
        out.append('BOUNDARIES FAILED: 1 of 1 rows failed')
        return False, out
    out.append('  input     ok    %d rows read; %d statements in the proved table' % (len(ctx['rows']),
                                                                                    len(ctx['proved'])))
    failed = 0
    for name, fn in CHECKS:
        bad = fn(ctx)
        if bad:
            failed += 1
            out.append('  %-9s FAIL  %d problem(s); the first: %s' % (name, len(bad), bad[0]))
            out.extend('    - %s' % b for b in bad[:SHOW])
            if len(bad) > SHOW:
                out.append('    - ... and %d more' % (len(bad) - SHOW))
        else:
            out.append('  %-9s ok    %s' % (name, okay(name, ctx)))
    total = len(CHECKS) + 1
    if failed:
        out.append('BOUNDARIES FAILED: %d of %d rows failed' % (failed, total))
        return False, out
    out.append('BOUNDARIES HELD: %d of %d rows' % (total, total))
    return True, out


def okay(name, ctx):
    n = len(ctx['rows'])
    return {'rows': '%d rows, each with its seven fields' % n,
            'kinds': 'every kind one of the four',
            'grades': 'every grade in the ruled list',
            'evidence': 'every graded row names its file or its gated statement',
            'paths': 'every path named is in this tree',
            'claims': 'every statement named is where its Claim says',
            'coverage': 'each of the %d statements of the proved table has a row' % len(ctx['proved']),
            'stages': 'every Proof again names its stage'}[name]


class Usage(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
    except (AttributeError, ValueError):
        pass
    ap = Parser(prog='check_boundaries.py', add_help=False, allow_abbrev=False)
    ap.add_argument('--root', required=True)
    try:
        a = ap.parse_args(argv)
        if not os.path.isdir(a.root):
            raise Usage('--root %s is not a folder' % a.root)
    except Usage as e:
        sys.stderr.write('check_boundaries.py: usage: --root ROOT (%s)\n' % e)
        return 2
    held, lines = check(a.root)
    sys.stdout.write('\n'.join(lines) + '\n')
    return 0 if held else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
