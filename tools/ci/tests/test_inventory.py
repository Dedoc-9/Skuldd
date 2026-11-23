# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_inventory.py: tools/ci/inventory.py run on the real tree, on copies of it, and on planted copies.
# Standard library only (Python 3.12 or later). It writes only in a temporary folder, which it removes.
#
#   python3 -B tools/ci/tests/test_inventory.py
#
# CASES, one line each, "  <case> ok|FAIL  <detail>":
#   honest      the real tree: exit 0 and INVENTORY HELD, every row ok.
#   copy        a copy of the real tree's kernel/coq, verdandi/mathkernel/F32 and THEOREMS.md: the same output, line
#               for line, as the real tree (so the copy holds everything the inventory reads).
#   outputs     the copy with --json and --matrix-out: the same output again (two runs agree); the JSON's schema, its
#               digest equal to the printed one and to the sha256 of its canonical form, its rows equal to the printed
#               rows, each frozen4_sha256 equal to the copy's file; the matrix one line, its folders the JSON's gated
#               folders, each with MK_ANCHOR_ and the folder's name in capitals.
#   P01..P97, Q01..Q99, R01..R33  a planted copy (the predictions files say what each plant does): exit 1,
#               INVENTORY FAILED, and the failing rows exactly the ones predicted, every other row ok. R16 and R17
#               plant a linked folder: a junction on Windows, a symbolic link on POSIX.
#   D01..D04, E01..E34  a decoy: a change the inventory must accept; exit 0 and every row ok. E01 is the limit the
#               inventory states: a folder, its freeze list and its ANCHORS.md row changed together hold there.
#   U01         a usage case held to its prediction: --json and --matrix-out naming one file in two cases of
#               letters: exit 2 where os.path.normcase folds case (Windows), else exit 0 with both files written.
#   U02, U03    --json and --matrix-out naming one file, the second spelled with a long-path prefix (\\?\ on
#               Windows, a leading "//" on POSIX; U02) or as the first (U03): exit 2, no file written.
#   U04         the same, the second spelled as Windows' volume GUID path (a leading "//" on POSIX, which has none).
#   U05, U06    --json and --matrix-out two names of one file (a hard link; U05), and --json a file that has
#               another name (U06): exit 2, a message holding the words predicted, no file's bytes changed.
#   U07         a decoy: --json an existing file with one name: exit 0, HELD, the file now the JSON.
#   no-matrix   P11's plant with --json and --matrix-out over a stale matrix file: exit 1, the matrix file removed,
#               the JSON written with held false.
#   usage-*     no --root, a root that is a file, an output in a missing folder, both outputs one file: exit 2 and no
#               verdict line saying HELD.
# Every output is read strictly: each line a row, the digest line or the verdict line (last), no row twice, and the
# verdict's counts equal to the rows'. The predictions are read from PREDICTIONS-inventory.txt (P01-P39, D),
# PREDICTIONS-inventory-2.txt (Q01-Q14, E01-E03), PREDICTIONS-inventory-3.txt (P40-P44),
# PREDICTIONS-inventory-4.txt (P45-P49, E04, U01), PREDICTIONS-inventory-5.txt (P50-P97, E05-E14: tables read as
# GitHub reads them, listed paths by their exact spelling, every sentence of a statement file read) and
# PREDICTIONS-inventory-6.txt (Q15-Q24, E15-E18: "|" and ";" read as words of their own, a statement file in
# printable ASCII only, a second proved table without outer pipes or indented, a second Successors heading of another
# level or underlined) and PREDICTIONS-inventory-7.txt (Q25-Q39, E19-E24: a block quote or a list item holding a bar in
# THEOREMS.md or ANCHORS.md, a delimiter row at any indent, a heading's text and a header cell read as GitHub shows
# them, a successor-shaped table outside the Successors section, a gated folder named ci) and
# PREDICTIONS-inventory-8.txt (Q40-Q81, E25-E29, U02, U03: THEOREMS.md and ANCHORS.md read in a named subset of
# Markdown, anything outside it refused; the output paths compared with a long-path prefix taken off) and
# PREDICTIONS-inventory-9.txt (Q82-Q99, E30-E33, U04: a header or heading that imitates the proved table's, a successor
# table's or the Successors heading with ASCII look-alikes counted as what it imitates; a backslash, a backtick run not
# closed on its line, a code span holding "|", a code fence and a character outside printable ASCII that the file may
# not hold, refused; the output paths resolved before the prefix is taken off) and PREDICTIONS-inventory-10.txt
# (R01-R17, U05-U07: a "#" that can open a heading outside a top-level heading's line, a "[", a code fence after list
# markers, a linked folder, and output paths that are two names of one file or a file with another name, refused),
# PREDICTIONS-inventory-11.txt (R18-R26: a line of "=" or "-" only under a line that is not blank, a setext heading's
# underline, refused in both files; E34, a decoy: such a line after a blank line, accepted),
# PREDICTIONS-inventory-12.txt (R28-R31: the same rule with a colon at either end of a "-" line, a table without
# pipes; an underline with trailing blanks; a "-" underline in ANCHORS.md; refused) and PREDICTIONS-inventory-13.txt
# (R32, R33: a line of U+00A0 above an underline, which is not blank; a "-:" line; refused), each frozen before its
# cases first ran; and PREDICTIONS-inventory-14.txt, which adds no case: written for the tree that adds the folders
# rti32, order32, bits32 and fclink and the Successors table's first rows, it predicts again each earlier case whose
# rows that tree moves, and its lines replace the earlier ones for that case (a file of SUPERSEDING may name only a
# case an earlier file predicts, with the same id and name, and each once), frozen before its first run; and
# PREDICTIONS-inventory-15.txt, which names no case and is not in SUPERSEDING: written for the tree whose Successors
# table also gains the rows of SINCOS32_NONZERO and EXP32_ADJ, it predicts that those rows move no earlier case,
# frozen before its first run;
# their plants and decoys must be exactly the ones defined here. Last line: "TEST inventory HELD: n of n cases" or
# "TEST inventory FAILED: k of n cases failed"; exit 0 only when every case held.
#
# WHAT A PASS SHOWS: each row of the inventory that a plant names can turn red, on the change the plant makes, and on
# nothing else; the honest tree and the decoys hold. WHAT IT DOES NOT SHOW: that the plants are the changes that
# matter most; anything about a change no plant makes; that a row turns red for every change of its kind; the
# "internal" and "output" rows of the inventory, which no plant reaches (they guard against a crash and a failed
# write).
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CHECKER = os.path.join(ROOT, 'tools', 'ci', 'inventory.py')
PREDICTIONS = ('PREDICTIONS-inventory.txt', 'PREDICTIONS-inventory-2.txt', 'PREDICTIONS-inventory-3.txt',
               'PREDICTIONS-inventory-4.txt', 'PREDICTIONS-inventory-5.txt', 'PREDICTIONS-inventory-6.txt',
               'PREDICTIONS-inventory-7.txt', 'PREDICTIONS-inventory-8.txt', 'PREDICTIONS-inventory-9.txt',
               'PREDICTIONS-inventory-10.txt', 'PREDICTIONS-inventory-11.txt', 'PREDICTIONS-inventory-12.txt',
               'PREDICTIONS-inventory-13.txt', 'PREDICTIONS-inventory-14.txt', 'PREDICTIONS-inventory-15.txt')
# Files that predict earlier cases again on a later tree: each case such a file names must be one an earlier file
# predicts, with the same id and name, named once there; its lines then replace the earlier ones. A case named twice
# anywhere else is refused.
SUPERSEDING = ('PREDICTIONS-inventory-14.txt',)
COPIED = ('kernel/coq', 'verdandi/mathkernel/F32', 'THEOREMS.md')
ANCHORS = 'kernel/coq/ANCHORS.md'
Z_GATE = 'kernel/coq/sincos32z/gate.json'
Z_IDENTITY = 'kernel/coq/sincos32z/Identity.v'
C_GATE = 'kernel/coq/compose/gate.json'
ROW = re.compile(r'  (.*?\S) +(ok|FAIL)(?:  (.*))?')
DIGEST = re.compile(r'INVENTORY DIGEST ([0-9a-f]{64})')
VERDICT = re.compile(r'INVENTORY (?:HELD: (\d+) of (\d+) rows|FAILED: (\d+) of (\d+) rows failed)')
RESULTS = []


class NotApplied(Exception):
    pass


def report(case, ok, detail):
    RESULTS.append(bool(ok))
    print('  %-44s %s  %s' % (case, 'ok' if ok else 'FAIL', detail))
    sys.stdout.flush()


def at(t, rel):
    return os.path.join(t, *rel.split('/'))


def read(t, rel):
    with open(at(t, rel), 'rb') as f:
        return f.read()


def write(t, rel, b):
    os.makedirs(os.path.dirname(at(t, rel)), exist_ok=True)
    with open(at(t, rel), 'wb') as f:
        f.write(b)


def append(t, rel, b):
    if not os.path.isfile(at(t, rel)):
        raise NotApplied('%s is absent' % rel)
    write(t, rel, read(t, rel) + b)


def remove(t, rel):
    if not os.path.isfile(at(t, rel)):
        raise NotApplied('%s is absent' % rel)
    os.remove(at(t, rel))


def replace_once(t, rel, old, new):
    b = read(t, rel)
    if b.count(old) != 1:
        raise NotApplied('%r occurs %d times in %s' % (old[:60], b.count(old), rel))
    write(t, rel, b.replace(old, new))


def the_line(t, rel, prefix):
    """(lines, index) of the one line of rel that starts with prefix."""
    lines = read(t, rel).split(b'\n')
    hits = [k for k, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise NotApplied('%d lines of %s start with %r' % (len(hits), rel, prefix))
    return lines, hits[0]


def edit_line(t, rel, prefix, old, new):
    lines, k = the_line(t, rel, prefix)
    if lines[k].count(old) != 1:
        raise NotApplied('%r is not once in the line %r of %s' % (old[:60], prefix, rel))
    lines[k] = lines[k].replace(old, new)
    write(t, rel, b'\n'.join(lines))


def drop_line(t, rel, prefix):
    lines, k = the_line(t, rel, prefix)
    write(t, rel, b'\n'.join(lines[:k] + lines[k + 1:]))


def add_line_after(t, rel, prefix, new):
    lines, k = the_line(t, rel, prefix)
    write(t, rel, b'\n'.join(lines[:k + 1] + [new] + lines[k + 1:]))


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---- the Successors table: added to, or made when THEOREMS.md has none -----------------------------------------------

SUCCESSOR_HEAD = (b'\n## Successors\n\n| Old statement | Successor | Relation | What the successor still does not say '
                  b'| Date |\n|---|---|---|---|---|\n')


def successor_rows(t, pairs):
    """Rows naming (old, successor) pairs, added to THEOREMS.md's Successors table, which is made when absent."""
    lines = read(t, 'THEOREMS.md').split(b'\n')
    heads = [k for k, line in enumerate(lines) if line.strip().lower().startswith(b'## successor')]
    if not heads:
        body = b''.join(b'| `%s` | `%s` | x | x | x |\n' % (o, s) for o, s in pairs)
        write(t, 'THEOREMS.md', read(t, 'THEOREMS.md') + SUCCESSOR_HEAD + body)
        return 'a new table'
    if len(heads) > 1:
        raise NotApplied('THEOREMS.md has %d Successors headings' % len(heads))
    k = heads[0] + 1
    while k < len(lines) and not lines[k].strip().startswith(b'|') and not lines[k].lstrip().startswith(b'#'):
        k += 1
    if k >= len(lines) or not lines[k].strip().startswith(b'|'):
        raise NotApplied('the Successors heading has no table under it')
    head = [c.strip().replace(b'`', b'').replace(b'*', b'').lower() for c in lines[k].strip()[1:-1].split(b'|')]
    old = [i for i, c in enumerate(head) if c.startswith(b'old statement')]
    new = [i for i, c in enumerate(head) if c.startswith(b'successor')]
    if len(old) != 1 or len(new) != 1:
        raise NotApplied('the Successors table has no single Old statement and Successor column')
    end = k + 2
    while end < len(lines) and lines[end].strip().startswith(b'|'):
        end += 1
    rows = []
    for o, s in pairs:
        cells = [b'x'] * len(head)
        cells[old[0]], cells[new[0]] = b'`%s`' % o, b'`%s`' % s
        rows.append(b'| ' + b' | '.join(cells) + b' |')
    write(t, 'THEOREMS.md', b'\n'.join(lines[:end] + rows + lines[end:]))
    return 'rows added to the table there'


# ---- the plants and decoys (what each does is in the predictions files) ---------------------------------------------

def p08(t):
    rel = 'verdandi/mathkernel/F32/ieee64/Ops.v'
    old = sha(read(t, rel))
    append(t, rel, b'(* changed *)\n')
    replace_once(t, 'verdandi/mathkernel/F32/ieee64/FROZEN4.txt', old.encode() + b'  ieee64/Ops.v\n',
                 sha(read(t, rel)).encode() + b'  ieee64/Ops.v\n')


def p11(t):
    h = sha(read(t, 'kernel/coq/compose/FROZEN4.txt')).encode()
    edit_line(t, ANCHORS, b'| `compose` |', h, h[:-1] + (b'0' if h[-1:] != b'0' else b'1'))


def p26(t):
    shutil.copytree(at(t, 'verdandi/mathkernel/F32/f32'), at(t, 'verdandi/mathkernel/F32/f99'))


def p27(t):
    for x in os.listdir(t):
        p = os.path.join(t, x)
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)


def d02(t):
    if any(line.strip().lower().startswith(b'## successor') for line in read(t, 'THEOREMS.md').split(b'\n')):
        return 'THEOREMS.md has a Successors table already: unchanged'
    write(t, 'THEOREMS.md', read(t, 'THEOREMS.md') + SUCCESSOR_HEAD)
    return 'a new table'


def q03(t):
    rel = 'kernel/coq/sincos32z/FROZEN4.txt'
    entries = [line for line in read(t, rel).split(b'\n') if re.fullmatch(rb'[0-9a-f]{64}  \S+', line)]
    if not entries:
        raise NotApplied('%s has no entry' % rel)
    append(t, rel, entries[0] + b'\n')


def q05(t):
    lines, k = the_line(t, ANCHORS, b'| `p32` |')
    cells = lines[k].strip()[1:-1].split(b'|')
    if len(cells) != 4 or not cells[3].strip():
        raise NotApplied('the p32 row of %s is not four cells with a record' % ANCHORS)
    lines[k] = b'|' + b'|'.join(cells[:3] + [b'  ']) + b'|'
    write(t, ANCHORS, b'\n'.join(lines))


def q09(t):
    shutil.copytree(at(t, 'kernel/coq/f32'), at(t, 'kernel/coq/F99'))


def q13(t):
    lines, k = the_line(t, 'THEOREMS.md', b'| `cos32` |')
    cells = lines[k].strip()[1:-1].split(b'|')
    if len(cells) != 5:
        raise NotApplied('the cos32 row of THEOREMS.md is not five cells')
    lines[k] = b'|' + b'|'.join(cells[:4]) + b'|'
    write(t, 'THEOREMS.md', b'\n'.join(lines))


def refreeze(t, folder, rel):
    """After a change to kernel/coq/<rel>, its line in the folder's FROZEN4.txt and the folder's ANCHORS.md value are
    rewritten to follow it, as a party who rewrites all three would."""
    fz = 'kernel/coq/%s/FROZEN4.txt' % folder
    before = sha(read(t, fz)).encode()
    lines = read(t, fz).split(b'\n')
    hits = [k for k, line in enumerate(lines) if line.endswith(b'  ' + rel.encode())]
    if len(hits) != 1:
        raise NotApplied('%d lines of %s list %s' % (len(hits), fz, rel))
    lines[hits[0]] = sha(read(t, 'kernel/coq/' + rel)).encode() + b'  ' + rel.encode()
    write(t, fz, b'\n'.join(lines))
    edit_line(t, ANCHORS, b'| `%s` |' % folder.encode(), before, sha(read(t, fz)).encode())


def unlist(t, folder, rel):
    """The folder's FROZEN4.txt without its line for rel, and its ANCHORS.md value changed to the new list's sha256, so
    that only a row that requires rel on the list can fail."""
    fz = 'kernel/coq/%s/FROZEN4.txt' % folder
    before = sha(read(t, fz)).encode()
    lines = read(t, fz).split(b'\n')
    hits = [k for k, line in enumerate(lines) if line.endswith(b'  ' + rel.encode())]
    if len(hits) != 1:
        raise NotApplied('%d lines of %s list %s' % (len(hits), fz, rel))
    write(t, fz, b'\n'.join(lines[:hits[0]] + lines[hits[0] + 1:]))
    edit_line(t, ANCHORS, b'| `%s` |' % folder.encode(), before, sha(read(t, fz)).encode())


def p43(t):
    successor_rows(t, [(b'f32.F32_Statement.F32_REL', b'f32.F32_Statement.F32_NEW')])
    lines, k = the_line(t, 'THEOREMS.md', b'## Successors')
    lines[k] = b'## Followers'
    write(t, 'THEOREMS.md', b'\n'.join(lines))


def p44(t):
    lines, k = the_line(t, 'THEOREMS.md', b'## Successors')
    tab = [i for i in range(k + 1, len(lines)) if lines[i].startswith(b'|')]
    if not tab:
        raise NotApplied('no table under the Successors heading')
    end = tab[0]
    while end < len(lines) and lines[end].startswith(b'|'):
        end += 1
    if any(line.startswith(b'#') for line in lines[k + 1:tab[0]]):
        raise NotApplied('another heading before the table')
    write(t, 'THEOREMS.md', b'\n'.join(lines[:tab[0]] + lines[end:]))


def reseal(t, rel):
    """After a change to kernel/coq/<rel>: every freeze list that lists it, the Verdandi copy of each such list and
    of rel itself, and each changed list's ANCHORS.md value follow it, as a party who rewrites them all would."""
    new = sha(read(t, 'kernel/coq/' + rel)).encode()
    changed = 0
    for f in sorted(os.listdir(at(t, 'kernel/coq'))):
        fz = 'kernel/coq/%s/FROZEN4.txt' % f
        if not os.path.isfile(at(t, fz)):
            continue
        lines = read(t, fz).split(b'\n')
        hits = [k for k, line in enumerate(lines) if line.endswith(b'  ' + rel.encode())]
        if not hits:
            continue
        before = sha(read(t, fz)).encode()
        for k in hits:
            lines[k] = new + b'  ' + rel.encode()
        write(t, fz, b'\n'.join(lines))
        edit_line(t, ANCHORS, b'| `%s` |' % f.encode(), before, sha(read(t, fz)).encode())
        if os.path.isfile(at(t, 'verdandi/mathkernel/F32/%s/FROZEN4.txt' % f)):
            write(t, 'verdandi/mathkernel/F32/%s/FROZEN4.txt' % f, read(t, fz))
        changed += 1
    if os.path.isfile(at(t, 'verdandi/mathkernel/F32/' + rel)):
        write(t, 'verdandi/mathkernel/F32/' + rel, read(t, 'kernel/coq/' + rel))
    if not changed:
        raise NotApplied('no freeze list lists %s' % rel)
    return '%d freeze lists resealed' % changed


def p45(t):
    lines, k = the_line(t, 'THEOREMS.md', b'## Successors')
    tab = [i for i in range(k + 1, len(lines)) if lines[i].startswith(b'|')]
    if not tab:
        raise NotApplied('no table under the Successors heading')
    end = tab[0]
    while end < len(lines) and lines[end].startswith(b'|'):
        end += 1
    second = [b'', b'A second table:', b'',
              b'| Old statement | Successor | Relation | What the successor still does not say | Date |',
              b'|---|---|---|---|---|', b'| `f32.F32_Statement.NOPE` | `f32.F32_Statement.NOPE2` | x | x | x |']
    write(t, 'THEOREMS.md', b'\n'.join(lines[:end] + second + lines[end:]))


def p46(t):
    stray = b'\n| `f32` | `MK_ANCHOR_F32` | `' + b'0' * 64 + b'` | a stray row |\n'
    write(t, ANCHORS, read(t, ANCHORS).rstrip(b'\n') + b'\n' + stray)


def p47(t):
    append(t, 'kernel/coq/log32/LOG32_Statement.v', b'\nDefinition SQRT32 : Prop := True.\n')
    refreeze(t, 'log32', 'log32/LOG32_Statement.v')


def p48(t):
    replace_once(t, 'kernel/coq/exp32r/RANGE_Statement.v', b'bpow radix2 104.', b'bpow radix2 105.')
    return reseal(t, 'exp32r/RANGE_Statement.v')


def p49(t):
    fz = 'kernel/coq/f32/FROZEN4.txt'
    b = read(t, fz)
    if not b.endswith(b'\n') or read(t, 'verdandi/mathkernel/F32/f32/FROZEN4.txt') != b:
        raise NotApplied('f32\'s freeze list does not end in a newline, or its copy is not equal to it')
    new = b + sha(b'').encode() + b'  f32/NUL\n'
    write(t, fz, new)
    write(t, 'verdandi/mathkernel/F32/f32/FROZEN4.txt', new)
    edit_line(t, ANCHORS, b'| `f32` |', sha(b).encode(), sha(new).encode())


def e04(t):
    notes = []
    for rel in ('exp32r/RANGE_Statement.v', 'p32r/P32R_Statement.v'):
        replace_once(t, 'kernel/coq/' + rel, b'bpow radix2 104.', b'bpow radix2 105.')
        notes.append(reseal(t, rel))
    return '; '.join(notes)


def e01(t):
    append(t, 'kernel/coq/sincos32z/Zero.v', b'(* changed *)\n')
    refreeze(t, 'sincos32z', 'sincos32z/Zero.v')


# ---- the fifth round (PREDICTIONS-inventory-5.txt) -------------------------------------------------------------------

NOPE_ROW = b'`f32.F32_Statement.NOPE` | `f32.F32_Statement.NOPE2` | x | x | x'
ZZ_ROW = b'`zz32` | `zz32.Z_Statement.Z` | `zz32/Z_Statement.v` | `zz32.Z.z` | 1 of 1'
ZERO_ANCHOR_ROW = b'`f32` | `MK_ANCHOR_F32` | `' + b'0' * 64 + b'` | a stray row'


def after_successor_table(t, new):
    """new lines put directly after the last line of THEOREMS.md's Successors table."""
    lines, k = the_line(t, 'THEOREMS.md', b'| Old statement |')
    j = k + 2
    while j < len(lines) and lines[j].startswith(b'|'):
        j += 1
    write(t, 'THEOREMS.md', b'\n'.join(lines[:j] + new + lines[j:]))


def after_line(t, rel, prefix, new):
    lines, k = the_line(t, rel, prefix)
    write(t, rel, b'\n'.join(lines[:k + 1] + new + lines[k + 1:]))


def after_proved_table(t, new):
    """new lines put directly under the last row of THEOREMS.md's proved table (its header the one line that
    starts "| Folder | Statement"), wherever that row is."""
    lines, k = the_line(t, 'THEOREMS.md', b'| Folder | Statement')
    j = k + 2
    while j < len(lines) and lines[j].startswith(b'|'):
        j += 1
    write(t, 'THEOREMS.md', b'\n'.join(lines[:j] + new + lines[j:]))


def after_anchors(t, new):
    write(t, ANCHORS, read(t, ANCHORS).rstrip(b'\n') + b'\n' + b'\n'.join(new) + b'\n')


def indent_anchors(t, by):
    lines = read(t, ANCHORS).split(b'\n')
    if not any(x.startswith(b'|') for x in lines):
        raise NotApplied('%s has no table line' % ANCHORS)
    write(t, ANCHORS, b'\n'.join((by + x if x.startswith(b'|') else x) for x in lines))


def listed_alias(alias):
    """f32's freeze list and its Verdandi copy gain "<sha256 of f32/F32.v>  <alias>", f32's ANCHORS.md value
    rewritten to follow."""
    def plant(t):
        fz, mz = 'kernel/coq/f32/FROZEN4.txt', 'verdandi/mathkernel/F32/f32/FROZEN4.txt'
        b = read(t, fz)
        if not b.endswith(b'\n') or read(t, mz) != b:
            raise NotApplied('f32\'s freeze list does not end in a newline, or its copy is not equal to it')
        new = b + sha(read(t, 'kernel/coq/f32/F32.v')).encode() + b'  ' + alias + b'\n'
        write(t, fz, new)
        write(t, mz, new)
        edit_line(t, ANCHORS, b'| `f32` |', sha(b).encode(), sha(new).encode())
    return plant


def names(sentence, other=None):
    """sentence appended to log32's statement file (and, with other, to that statement file too), every freeze list
    that lists a changed file, its Verdandi copies and its ANCHORS.md value rewritten to follow."""
    def plant(t):
        append(t, 'kernel/coq/log32/LOG32_Statement.v', b'\n' + sentence + b'\n')
        refreeze(t, 'log32', 'log32/LOG32_Statement.v')
        if other:
            append(t, 'kernel/coq/' + other, b'\n' + sentence + b'\n')
            return reseal(t, other)
    return plant


PIPELESS = [b'', b'Folder | Variable | sha256 of FROZEN4.txt | Record', b'---|---|---|---', ZERO_ANCHOR_ROW]
CASES5 = {
    'P50': lambda t: after_successor_table(t, [NOPE_ROW]),
    'P51': lambda t: after_successor_table(t, [b'#tag', b'', b'| Old statement | Successor | Relation | What the '
                                               b'successor still does not say | Date |', b'|---|---|---|---|---|',
                                               b'| ' + NOPE_ROW + b' |']),
    'P52': lambda t: after_line(t, 'THEOREMS.md', b'| `sincos32z` |', [ZZ_ROW]),
    'P53': lambda t: after_anchors(t, [ZERO_ANCHOR_ROW]),
    'P54': lambda t: after_anchors(t, PIPELESS),
    'P55': lambda t: after_successor_table(t, [b'', b'Another table:', b'', b'Old statement | Successor | Relation | '
                                               b'What the successor still does not say | Date',
                                               b'---|---|---|---|---', NOPE_ROW]),
    'P56': lambda t: indent_anchors(t, b'    '),
    'P57': listed_alias(b'f32/F32.v.'),
    'P58': listed_alias(b'f32/f32.v'),
    'E05': lambda t: after_successor_table(t, [b'', NOPE_ROW]),
    'E06': lambda t: after_successor_table(t, [b'', b'#tag']),
    'E07': lambda t: after_proved_table(t, [b'', ZZ_ROW]),
    'E08': lambda t: after_anchors(t, [b'', ZERO_ANCHOR_ROW]),
    'E09': lambda t: indent_anchors(t, b'  '),
    'P60': names(b'Example SQRT32 : Prop := True.'),
    'P61': names(b'Corollary SQRT32 : True.'),
    'P62': names(b'Proposition SQRT32 : True.'),
    'P63': names(b'Fact SQRT32 : True.'),
    'P64': names(b'Remark SQRT32 : True.'),
    'P65': names(b'Property SQRT32 : True.'),
    'P66': names(b'Conjecture SQRT32 : True.'),
    'P67': names(b'CoFixpoint SQRT32 : nat := 0.'),
    'P68': names(b'CoInductive SQRT32 : Set := sq_c0 : SQRT32.'),
    'P69': names(b'Variant SQRT32 : Set := sq_v0.'),
    'P70': names(b'Structure SQRT32 : Type := { sq_s0 : nat }.'),
    'P71': names(b'Class SQRT32 : Type := { sq_k0 : nat }.'),
    'P72': names(b'Instance SQRT32 : Inhabited nat := { }.'),
    'P73': names(b'Infix "+++" := Rplus (at level 50).', other='p32/P32_Statement.v'),
    'P74': names(b'Parameters (sq_p0 : nat) (SQRT32 : Prop).'),
    'P75': names(b'Axioms sq_a0 SQRT32 : Prop.'),
    'P76': names(b'Hypothesis SQRT32 : True.'),
    'P77': names(b'Hypotheses (SQRT32 : True).'),
    'P78': names(b'Variable SQRT32 : nat.'),
    'P79': names(b'Variables sq_x0 SQRT32 : nat.'),
    'P80': names(b'Module SQRT32.\nEnd SQRT32.'),
    'P81': names(b'Ltac SQRT32 := idtac.'),
    'P82': names(b'Function SQRT32 (n : nat) : nat := n.'),
    'P83': names(b'Let SQRT32 : Prop := True.'),
    'P84': names(b'Inductive sq_i0 : Set := | sq_i1 | C_KK.'),
    'P85': names(b'Record sq_r0 : Type := sq_mk0 { sq_f0 : nat; o_add : nat }.'),
    'P86': names(b'Inductive sq_m0 : Set := sq_m1 with SQRT32 : Set := sq_m2.'),
    'P87': names(b'Fixpoint sq_g0 (n : nat) : nat := 0 with SQRT32 (n : nat) : nat := 0.'),
    'P88': names(b'Coercion SQRT32 := INR.'),
    'P89': names(b'Lemma sq_l0 : True.\nProof. exact I. Qed.'),
    'P90': names(b'Instance : Inhabited nat := { }.'),
    'P91': names(b'Inductive sq_w0 : Set := sq_w1 where "\'w\'" := sq_w1.'),
    'P92': names(b'#[local] Program Definition SQRT32 : nat := 0.'),
    'P93': names(b'Local Polymorphic Definition SQRT32@{u} : Type@{u} := Prop.'),
    'P94': names(b'Definition gconst_rect : nat := 0.'),
    'P95': names(b'Class sq_c0 (A : Type) := t_add : A.'),
    'P96': names(b'Definition sq_t0 : nat := 0'),
    'P97': names(b'Definition 2sq : nat := 0.'),
    'E10': names(b'(* Definition SQRT32 : Prop := True. Variant SQRT32 := a. with SQRT32. Coercion x := y. *)'),
    'E11': names(b'Definition sq_d0 (n : nat) : nat := match n with | O => 0 | S k => k end.'),
    'E12': names(b'Local Open Scope nat_scope.\nClose Scope nat_scope.\nSet Implicit Arguments.\nUnset Implicit '
                 b'Arguments.\nCheck 0.\nPrint nat.\nRequire Import Bool.\nImport Bool.\nSection sq_s.\nEnd sq_s.'),
    'E13': names(b'Notation "a . b" := (Rplus a b) (at level 50).'),
    'E14': names(b'Record sq_r9 : Type := { sq_f9 : nat }.\nInductive sq_i9 : Set := sq_c9 | sq_d9.'),
}


def e02(t):
    replace_once(t, Z_IDENTITY, b'\nDefinition identity_check', b'\n(* a note *)\nDefinition identity_check')
    refreeze(t, 'sincos32z', 'sincos32z/Identity.v')


CASES = {
    'P01': lambda t: write(t, 'kernel/coq/f32/Extra.v', b'(* not listed in gate.json *)\n'),
    'P02': lambda t: remove(t, 'kernel/coq/sincos32z/Zero.v'),
    'P03': lambda t: replace_once(t, Z_GATE, b'"Zero.v", "Closed.v"', b'"Zero.v", "Zero.v", "Closed.v"'),
    'P04': lambda t: write(t, 'kernel/coq/f32/plants/gate.json', read(t, 'kernel/coq/f32/gate.json')),
    'P05': lambda t: write(t, 'kernel/coq/gate/json.py', b'# a module that would shadow the standard library\n'),
    'P06': lambda t: append(t, 'verdandi/mathkernel/F32/ieee64/Ops.v', b'(* changed *)\n'),
    'P07': lambda t: append(t, 'verdandi/mathkernel/F32/f32/FROZEN4.txt', b'# changed\n'),
    'P08': p08,
    'P09': lambda t: replace_once(t, Z_IDENTITY, b'MKF.sincos32z.Closed.sincos32_ieee_zero_holds',
                                  b'MKF.sincos32z.Closed.sincos32_ieee_zero_other'),
    'P10': lambda t: edit_line(t, 'THEOREMS.md', b'| `cos32` |', b'`cos32.Cos32.cos32_all`',
                               b'`cos32.Cos32.cos32_any`'),
    'P11': p11,
    'P12': lambda t: drop_line(t, ANCHORS, b'| `log32` |'),
    'P13': lambda t: write(t, 'kernel/coq/exp32/extra/Hidden.v', b'(* in a subfolder *)\n'),
    'P14': lambda t: write(t, 'kernel/coq/p32/plants/unnamed.v', b'(* named by no plant *)\n'),
    'P15': lambda t: remove(t, 'kernel/coq/compose/plants/Compose_axiom_landing.v'),
    'P16': lambda t: write(t, 'kernel/coq/orl/Stray.v', b'(* in no gated folder *)\n'),
    'P17': lambda t: write(t, 'kernel/coq/gate/json/__init__.py', b'\n'),
    'P18': lambda t: replace_once(t, Z_GATE, b'{"name": "SINCOS32_IEEE_ZERO", ',
                                  b'{"name": "SINCOS32_IEEE_ZERO", "name": "SINCOS32_IEEE_ZERO", '),
    'P19': lambda t: replace_once(t, Z_IDENTITY, b'SINCOS32_IEEE_ZERO := MKF.sincos32z.Closed.',
                                  b'SINCOS32_IEEE_ZERO \\/ False := or_introl MKF.sincos32z.Closed.'),
    'P20': lambda t: replace_once(t, Z_IDENTITY, b'\nDefinition identity_check',
                                  b'\nLocal Notation conjx := conj.\nDefinition identity_check'),
    'P21': lambda t: add_line_after(t, 'THEOREMS.md', b'| `compose` |',
                                    b'| `ghost32` | `ghost32.G_Statement.G` | `ghost32/G_Statement.v` | '
                                    b'`ghost32.G.g_holds` | 1 of 1 |'),
    'P22': lambda t: drop_line(t, 'THEOREMS.md', b'| `cos32` |'),
    'P23': lambda t: successor_rows(t, [(b'f32.F32_Statement.F32_REL', b'f32.F32_Statement.F32_NEW')]),
    'P24': lambda t: edit_line(t, ANCHORS, b'| `f32` |', b'`MK_ANCHOR_F32`', b'`MK_ANCHOR_F23`'),
    'P25': lambda t: append(t, 'kernel/coq/sincos32i/FROZEN4.txt', b'# changed\n'),
    'P26': p26,
    'P27': p27,
    'P28': lambda t: append(t, 'kernel/coq/sincos32z/FROZEN4.txt', b'garbage\n'),
    'P29': lambda t: write(t, 'verdandi/mathkernel/F32/p32r/Extra.v', b'(* not listed *)\n'),
    'P30': lambda t: append(t, 'verdandi/mathkernel/F32/gate/strict_read.py', b'# changed\n'),
    'P31': lambda t: remove(t, Z_IDENTITY),
    'P32': lambda t: remove(t, Z_GATE),
    'P33': lambda t: write(t, 'verdandi/mathkernel/F32/orl/Stray.v', b'(* in no mirror *)\n'),
    'P34': lambda t: replace_once(t, Z_GATE, b'"sincos32", "sincos32i"],', b'"sincos32", "sincos32i", "orl"],'),
    'P35': lambda t: replace_once(t, Z_GATE, b'"Zero.v", "Closed.v"', b'"../Zero.v", "Closed.v"'),
    'P36': lambda t: replace_once(t, C_GATE, b'{"Compose.v": "plants/Compose_axiom_landing.v"}',
                                  b'{"Compose.v": "Compose_axiom_landing.v"}'),
    'P37': lambda t: replace_once(t, C_GATE, b'{"Compose.v": "plants/Compose_axiom_landing.v"}',
                                  b'{"Other.v": "plants/Compose_axiom_landing.v"}'),
    'P38': lambda t: edit_line(t, 'THEOREMS.md', b'| `exp32r` |',
                               b'`exp32r.RANGE_Statement.EXP32_RANGE`, `EXP32_SHARP`',
                               b'`exp32r.RANGE_Statement.EXP32_SHARP`, `EXP32_RANGE`'),
    'P39': lambda t: edit_line(t, 'THEOREMS.md', b'| `f32` |', b'`f32/F32_Statement.v`', b'`f32/F32.v`'),
    'D01': lambda t: successor_rows(t, [(b'p32.P32_Statement.T32', b'p32r.P32R_Statement.P32R')]),
    'D02': d02,
    'D03': lambda t: write(t, 'kernel/coq/f32/plants/gate.json.bak', read(t, 'kernel/coq/f32/gate.json')),
    'D04': lambda t: write(t, 'kernel/coq/exp32/extra/notes.txt', b'not a Coq file\n'),
    'Q01': lambda t: replace_once(t, Z_GATE, b'"tier": "flocq4"', b'"tier": "flocq5"'),
    'Q02': lambda t: replace_once(t, Z_GATE, b'"identity": "Identity"', b'"identity": "Closed"'),
    'Q03': q03,
    'Q04': lambda t: replace_once(t, Z_IDENTITY, b'Require SINCOS32_IEEE_Zero_Statement Closed.',
                                  b'Require SINCOS32_IEEE_Zero_Statement Closed Zero.'),
    'Q05': q05,
    'Q06': lambda t: successor_rows(t, [(b'f32.F32_Statement.F32_REL', b'f32.F32_Statement.F32_REL')]),
    'Q07': lambda t: replace_once(t, Z_IDENTITY, b'\nDefinition identity_check',
                                  b'\nLocal Notation "A /\\ B" := (A \\/ B) : type_scope.\nDefinition identity_check'),
    'Q08': lambda t: edit_line(t, 'THEOREMS.md', b'| `f32` |', b'`f32.F32_Statement.F32_REL`', b'`F32_REL`'),
    'Q09': q09,
    'Q10': lambda t: append(t, 'verdandi/mathkernel/F32/p32r/FROZEN4.txt', b'garbage\n'),
    'Q11': lambda t: replace_once(t, Z_GATE, b'{"name": "SINCOS32_IEEE_ZERO", ',
                                  b'{"name": "SINCOS32_IEEE_ZERO\xff", '),
    'Q12': lambda t: append(t, Z_IDENTITY, b'(* not closed\n'),
    'Q13': q13,
    'Q14': lambda t: remove(t, 'kernel/coq/gate/freeze4.py'),
    # the third round (PREDICTIONS-inventory-3.txt)
    'P40': lambda t: unlist(t, 'log32', 'log32/Trunc.v'),
    'P41': lambda t: unlist(t, 'cos32', 'cos32/emit_cos32.py'),
    'P42': lambda t: unlist(t, 'sincos32z', 'sincos32/Graph.v'),
    'P43': p43,
    'P44': p44,
    'E01': e01,
    'E02': e02,
    'E03': lambda t: write(t, 'THEOREMS.md', read(t, 'THEOREMS.md').replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')),
    # the fourth round (PREDICTIONS-inventory-4.txt)
    'P45': p45,
    'P46': p46,
    'P47': p47,
    'P48': p48,
    'P49': p49,
    'E04': e04,
}
CASES.update(CASES5)


# ---- the sixth round (PREDICTIONS-inventory-6.txt) -------------------------------------------------------------------

ALPHA, BETA = b'\xce\xb1', b'\xce\xb2'   # Greek alpha and beta in UTF-8
PROVED_HEADER = b'Folder | Statement | Statement file | Closing theorem | Gate'
SUCCESSOR_TABLE = [b'| Old statement | Successor | Relation | What the successor still does not say | Date |',
                   b'|---|---|---|---|---|', b'| ' + NOPE_ROW + b' |']


def at_end(rel, new):
    """new lines put at the end of rel, after a blank line."""
    return lambda t: write(t, rel, read(t, rel).rstrip(b'\n') + b'\n\n' + b'\n'.join(new) + b'\n')


CASES6 = {
    'Q15': names(b'Inductive sq_n1 (' + ALPHA + b' : Type) : Type := sq_n2 : ' + ALPHA + b' -> sq_n1 ' + ALPHA
                 + b'|SQRT32 : sq_n1 ' + ALPHA + b'.'),
    'Q16': names(b'Record sq_n3 (' + ALPHA + b' : Type) := { sq_n4 : ' + ALPHA + b'; SQRT32 : nat }.'),
    'Q17': names(b'Notation "x !" := (S x) (at level 2, left associativity).\n'
                 b'Inductive sq_n5 : nat -> Type := sq_n6 : sq_n5 3 !|SQRT32 : sq_n5 0.'),
    'Q18': names(b'Notation "x !" := (S x) (at level 2, left associativity).\n'
                 b'Record sq_n7 : Type := { sq_n8 : 3 = 2!; SQRT32 : nat }.'),
    'Q19': names(b'Definition sq_n9 : nat := let ' + ALPHA + b' := 0 in ' + ALPHA + b'.'),
    'Q20': at_end('THEOREMS.md', [PROVED_HEADER, b'--- | --- | --- | --- | ---', ZZ_ROW]),
    'Q21': at_end('THEOREMS.md', [b'| ' + PROVED_HEADER, b'| --- | --- | --- | --- | ---', b'| ' + ZZ_ROW]),
    'Q22': at_end('THEOREMS.md', [b'    | ' + PROVED_HEADER + b' |', b'    |---|---|---|---|---|',
                                  b'    | ' + ZZ_ROW + b' |']),
    'Q23': at_end('THEOREMS.md', [b'Successors', b'----------', b''] + SUCCESSOR_TABLE),
    'Q24': at_end('THEOREMS.md', [b'### Successors', b''] + SUCCESSOR_TABLE),
    'E15': names(b'(* ' + ALPHA + b'|SQRT32 *) Notation sq_e1 := "' + ALPHA + b'|SQRT32; ' + BETA + b'".'),
    'E16': names(b'Inductive sq_e2 : Prop := sq_e3 : (true || false) = true -> sq_e2 | sq_e4 : sq_e2.'),
    'E17': at_end('THEOREMS.md', [b'Successors are named in the table above.']),
    'E18': at_end('THEOREMS.md', [b'Name | Value', b'--- | ---', b'a | b']),
}
CASES.update(CASES6)


# ---- the seventh round (PREDICTIONS-inventory-7.txt) -----------------------------------------------------------------

ANCHOR_HEADER = b'| Folder | Variable | sha256 of FROZEN4.txt | Record |'
ZERO_ANCHOR = b'| `f32` | `MK_ANCHOR_F32` | `' + b'0' * 64 + b'` | a second table |'


def quoted(lines):
    """The lines in a block quote."""
    return [b'> ' + x for x in lines]


CASES7 = {
    'Q25': at_end('THEOREMS.md', quoted([b'| ' + PROVED_HEADER + b' |', b'|---|---|---|---|---|',
                                         b'| ' + ZZ_ROW + b' |'])),
    'Q26': at_end('THEOREMS.md', [b'- | ' + PROVED_HEADER + b' |', b'  |---|---|---|---|---|',
                                  b'  | ' + ZZ_ROW + b' |']),
    'Q27': lambda t: after_successor_table(t, [b''] + quoted(SUCCESSOR_TABLE)),
    'Q28': at_end('THEOREMS.md', [b'> ## Successors']),
    'Q29': at_end(ANCHORS, quoted([ANCHOR_HEADER, b'|---|---|---|---|', ZERO_ANCHOR])),
    'Q30': at_end(ANCHORS, [b'- a list item', b'', b'    ' + ANCHOR_HEADER, b'    |---|---|---|---|',
                            b'    ' + ZERO_ANCHOR]),
    'Q31': at_end('THEOREMS.md', [b'## Notes', b'', b'### **Successors**', b''] + SUCCESSOR_TABLE),
    'Q32': at_end('THEOREMS.md', [b'Successors', b'of retired statements', b'---', b''] + SUCCESSOR_TABLE),
    'Q33': at_end('THEOREMS.md', [b'## Retired statements', b''] + SUCCESSOR_TABLE),
    'Q34': lambda t: write(t, 'kernel/coq/ci/gate.json', read(t, 'kernel/coq/f32/gate.json')),
    'Q35': at_end('THEOREMS.md', [b'| _Folder_ | Statement | Statement file | Closing theorem | Gate |',
                                  b'|---|---|---|---|---|', b'| ' + ZZ_ROW + b' |']),
    'Q36': at_end('THEOREMS.md', [b'## <em>Successors</em>', b'', b'No statement has a successor here.']),
    'Q37': lambda t: after_successor_table(t, [b'', b'- a list item', b'', b'    | a | b |', b'    |---|---|',
                                               b'    | c | d |']),
    'Q38': at_end('THEOREMS.md', [b'## Notes', b'', b'### **Successors**', b'', b'No statement has a successor here.']),
    'Q39': at_end('THEOREMS.md', [b'Successors', b'of retired statements', b'---', b'',
                                  b'No statement has a successor here.']),
    'E19': lambda t: write(t, 'kernel/coq/ci/README.txt', b'a folder named ci, with no gate.json\n'),
    'E20': at_end('THEOREMS.md', [b'- a note on the successors, without a bar']),
    'E21': at_end('THEOREMS.md', [b'### *Notes* on successors']),
    'E22': at_end('THEOREMS.md', [b'Values > 0 are kept; a | b is prose here.']),
    'E23': at_end(ANCHORS, [b'- a note without a bar']),
    'E24': at_end('THEOREMS.md', [b'| Statement | Successor count |', b'|---|---|', b'| x | 0 |']),
}
CASES.update(CASES7)


# ---- the eighth round (PREDICTIONS-inventory-8.txt): THEOREMS.md and ANCHORS.md read in a named Markdown subset ------

PROVED_HEAD8 = b'| Folder | Statement | Statement file | Closing theorem | Gate |'
PROVED_ROW8 = b'| `zz32` | `zz32.ZZ_Statement.ZZ` | `zz32/ZZ_Statement.v` | `zz32.Zz.zz` | 1 of 1 |'
SUCC_HEAD8 = b'| Old statement | Successor | Relation | What the successor still does not say | Date |'
SUCC_ROW8 = b'| `f32.F32_Statement.NOPE` | `f32.F32_Statement.NOPE2` | adds | x | 2026-11-20 |'
DELIM5 = b'|---|---|---|---|---|'
ANCH_ROW8 = b'| `zz32` | `MK_ANCHOR_ZZ32` | `' + b'0' * 64 + b'` | set by nobody |'
F32_REL = b'`f32.F32_Statement.F32_REL`'
ZWSP, CYRILLIC_O, BOM, ELLIPSIS, PI = b'\xe2\x80\x8b', b'\xd0\x9e', b'\xef\xbb\xbf', b'\xe2\x80\xa6', b'\xcf\x80'


def tail(rel, b):
    """b appended to rel, byte for byte."""
    return lambda t: append(t, rel, b)


def head(rel, b):
    """b put before rel's first byte."""
    def plant(t):
        if not os.path.isfile(at(t, rel)):
            raise NotApplied('%s is absent' % rel)
        write(t, rel, b + read(t, rel))
    return plant


def lone_cr(lines):
    return b'\r' + b'\r'.join(lines) + b'\r'


def lf_lines(lines):
    return b'\n'.join(lines) + b'\n'


def succ_section(heading, cell):
    return [heading, b'', SUCC_HEAD8.replace(b'| Successor |', b'| ' + cell + b' |'), DELIM5, SUCC_ROW8]


def span(t, rel, start):
    """(lines, i, j): rel's lines and the one table that starts at a line starting with start, lines[i:j]."""
    lines = read(t, rel).split(b'\n')
    hits = [k for k, x in enumerate(lines) if x.startswith(start)]
    if len(hits) != 1:
        raise NotApplied('%d lines of %s start with %r' % (len(hits), rel, start))
    i = j = hits[0]
    while j < len(lines) and lines[j].startswith(b'|'):
        j += 1
    return lines, i, j


def f32_row(lines, i, j):
    rows = [x for x in lines[i + 2:j] if x.startswith(b'| `f32` |') and F32_REL in x]
    if len(rows) != 1:
        raise NotApplied('the proved table has no single f32 row naming F32_REL')
    return rows[0]


def also_proved(header):
    """After the proved table: a blank line, "Also proved:", a blank line and a table under header whose one row is
    f32's naming F32_CR (review 6's m1, m3, m6)."""
    def plant(t):
        lines, i, j = span(t, 'THEOREMS.md', b'| Folder | Statement')
        fake = f32_row(lines, i, j).replace(F32_REL, b'`f32.F32_Statement.F32_CR`')
        write(t, 'THEOREMS.md', b'\n'.join(lines[:j] + [b'', b'Also proved:', b'', header, DELIM5, fake] + lines[j:]))
    return plant


def hidden_proved(shown):
    """The proved table between a line "<!--" and, after a blank line, a line "-->"; then, with shown, a copy of it
    whose header reads "F&#111;lder" and whose f32 row names F32_CR (review 6's m2b; m2c without the copy)."""
    def plant(t):
        lines, i, j = span(t, 'THEOREMS.md', b'| Folder | Statement')
        real, f32 = lines[i:j], f32_row(lines, i, j)
        fake = [real[0].replace(b'| Folder |', b'| F&#111;lder |'), real[1]] + [
            x.replace(F32_REL, b'`f32.F32_Statement.F32_CR`') if x == f32 else x for x in real[2:]]
        write(t, 'THEOREMS.md', b'\n'.join(lines[:i] + [b'<!--'] + real + [b'', b'-->', b''] + (fake if shown else [])
                                           + lines[j:]))
    return plant


def second_successors_entity(t):
    """Review 6's m4: after the Successors table, "## &#83;uccessors" and a table whose header reads "&#79;ld
    statement", naming f32.NOPE.NOT_A_STATEMENT."""
    lines, i, j = span(t, 'THEOREMS.md', b'| Old statement |')
    add = [b'', b'## &#83;uccessors', b'',
           b'| &#79;ld statement | Successor | Relation | What the successor still does not say | Date |', DELIM5,
           b'| `f32.F32_Statement.F32_REL` | `f32.NOPE.NOT_A_STATEMENT` | replaces | nothing | 2026-11-20 |']
    write(t, 'THEOREMS.md', b'\n'.join(lines[:j] + add + lines[j:]))


def hidden_anchors(t):
    """Review 6's a2b: ANCHORS.md's table between a line "<!--" and, after a blank line, a line "-->"."""
    lines, i, j = span(t, ANCHORS, b'| Folder | Variable')
    write(t, ANCHORS, b'\n'.join(lines[:i] + [b'<!--'] + lines[i:j] + [b'', b'-->'] + lines[j:]))


P5_ROW = b'| f32 | `MKF.f32.F32_Statement.NOT_A_STATEMENT` | `f32/F32_Statement.v` | `MKF.f32.Identity.x` | x |\n'
P6_ROW = b'| `f32.F32_Statement.NOT_A_STATEMENT` | `f32.F32_Statement.ALSO_NOT` | adds | x | 2026-11-20 |\n'
CASES8 = {
    # the sixth review's plants and controls on line ends, a byte-order mark, references and links (its I01 to I08)
    'Q40': tail('THEOREMS.md', b'\n' + lone_cr([b'', PROVED_HEAD8, DELIM5, PROVED_ROW8]) + b'\n'),
    'Q41': tail('THEOREMS.md', b'\n' + lf_lines([PROVED_HEAD8, DELIM5, PROVED_ROW8])),
    'Q42': tail('THEOREMS.md', b'\n' + lone_cr(succ_section(b'## Successors', b'Successor')) + b'\n'),
    'Q43': tail('THEOREMS.md', b'\n' + lf_lines(succ_section(b'## Successors', b'Successor'))),
    'Q44': head('THEOREMS.md', BOM + lf_lines([PROVED_HEAD8[2:], DELIM5, PROVED_ROW8, b''])),
    'Q45': head('THEOREMS.md', lf_lines([PROVED_HEAD8[2:], DELIM5, PROVED_ROW8, b''])),
    'Q46': tail('THEOREMS.md', b'\n' + lf_lines(succ_section(b'## Succ&#101;ssors', b'Succ&#101;ssor'))),
    'Q47': tail('THEOREMS.md', b'\n' + lf_lines(succ_section(b'## Successors', b'Successor'))),
    'Q48': tail('THEOREMS.md', b'\n' + lf_lines(succ_section(b'## Succ' + ZWSP + b'essors',
                                                              b'Succ' + ZWSP + b'essor'))),
    'Q49': tail('THEOREMS.md', b'\n' + lf_lines(succ_section(b'## [Successors](#successors)',
                                                              b'[Successor](#successor)'))),
    'Q50': tail('THEOREMS.md', b'\n' + lf_lines([PROVED_HEAD8.replace(b'| Folder |', b'| F&#111;lder |'), DELIM5,
                                                  PROVED_ROW8])),
    'Q51': tail(ANCHORS, b'\n' + lone_cr([b'', b'| Folder | Variable | sha256 of FROZEN4.txt | Record |',
                                          b'|---|---|---|---|', ANCH_ROW8]) + b'\n'),
    'Q52': tail(ANCHORS, b'\n' + lf_lines([b'| Folder | Variable | sha256 of FROZEN4.txt | Record |',
                                            b'|---|---|---|---|', ANCH_ROW8])),
    # the sixth review's plants on hidden and look-alike tables and names (its m1 to m6, a2b)
    'Q53': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| F&#111;lder |')),
    'Q54': hidden_proved(True),
    'Q55': hidden_proved(False),
    'Q56': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| Fol' + ZWSP + b'der |')),
    'Q57': second_successors_entity,
    'Q58': lambda t: edit_line(t, 'THEOREMS.md', b'| `f32` |', F32_REL, b'F32_CR <!-- ' + F32_REL + b' -->'),
    'Q59': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| F' + CYRILLIC_O + b'lder |')),
    'Q60': hidden_anchors,
    # the sixth review's plants on headings and headers (its p1 to p6) and controls (c1, c5, c6)
    'Q61': tail('THEOREMS.md', b'\n## &#83;uccessors\n'),
    'Q62': tail('THEOREMS.md', b'\n## [Successors](#successors)\n'),
    'Q63': tail('THEOREMS.md', b'\n- ## Successors\n'),
    'Q64': tail('THEOREMS.md', b'\n- Successors\n  ----------\n'),
    'Q65': tail('THEOREMS.md', b'\n## Other\n\n| [Folder](#x) | Statement | Statement file | Closing theorem | Gate |\n'
                               b'|---|---|---|---|---|\n' + P5_ROW),
    'Q66': tail('THEOREMS.md', b'\n## Other\n\n| Old&#32;statement | Successor | Relation | What | Date |\n'
                               b'|---|---|---|---|---|\n' + P6_ROW),
    'Q67': tail('THEOREMS.md', b'\n## Successors\n'),
    'Q68': tail('THEOREMS.md', b'\n## Other\n\n| Folder | Statement | Statement file | Closing theorem | Gate |\n'
                               b'|---|---|---|---|---|\n' + P5_ROW),
    'Q69': tail('THEOREMS.md', b'\n## Other\n\n| Old statement | Successor | Relation | What | Date |\n'
                               b'|---|---|---|---|---|\n' + P6_ROW),
    # decoys reviewers proposed that the subset refuses, and the subset's other rules
    'Q70': tail('THEOREMS.md', b'\nThe kernel & its gates.\n'),
    'Q71': tail('THEOREMS.md', b'\n<!-- a second comment -->\n'),
    'Q72': tail('THEOREMS.md', b'\nAlso: <table><tr><th>Folder</th><th>Statement</th></tr></table>\n'),
    'Q73': lambda t: replace_once(t, 'THEOREMS.md', b'</details>\n\n', b'</details>\nA line right under it.\n\n'),
    'Q74': tail('THEOREMS.md', b'\n- a note\n\n    ## Successors\n'),
    'Q75': tail('THEOREMS.md', b'\n- a note\n\n    Successors\n    ----------\n'),
    'Q76': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| ~~Folder~~ |')),
    'Q77': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| $Folder$ |')),
    'Q78': lambda t: edit_line(t, 'THEOREMS.md', b'| `f32` |', b'`f32/F32_Statement.v`',
                               b'`f32/F32_Statement.v` (see notes)'),
    'Q79': lambda t: after_successor_table(t, [b'| `p32.P32_Statement.T32` (old) | `p32r.P32R_Statement.P32R` | x | x '
                                               b'| x |']),
    'Q80': lambda t: edit_line(t, 'THEOREMS.md', b'| Old statement |', b'| Date |', b'| Date [1] |'),
    'Q81': tail('THEOREMS.md', b'\nA tab\there.\n'),
    'E25': tail('THEOREMS.md', b'\n<details>\n<summary>More notes</summary>\n\nNothing more.\n\n</details>\n'),
    'E26': tail('THEOREMS.md', b'\n| Name ' + ELLIPSIS + b' | Value |\n|---|---|\n| a | b |\n'),
    'E27': tail('THEOREMS.md', b'\n| Name | Value |\n|---|---|\n| pi | ' + PI + b' |\n'),
    'E28': tail('THEOREMS.md', b'\n1. an item\n2. another item\n- a third, with no heading\n'),
    'E29': tail('THEOREMS.md', b'\nRun `coqc <folder>/Identity.v` from the root.\n'),
}
CASES.update(CASES8)


# ---- the ninth round (PREDICTIONS-inventory-9.txt): look-alike headers, escapes, code spans, fences, characters ------

def before_successors(block):
    """block (lines) put before the "## Successors" heading, after a blank line of its own."""
    def plant(t):
        lines = read(t, 'THEOREMS.md').split(b'\n')
        hits = [k for k, x in enumerate(lines) if x == b'## Successors']
        if len(hits) != 1:
            raise NotApplied('%d lines of THEOREMS.md are "## Successors"' % len(hits))
        write(t, 'THEOREMS.md', b'\n'.join(lines[:hits[0]] + block + [b''] + lines[hits[0]:]))
    return plant


def fenced_proved(closed):
    """A line of three backticks before the proved table, and with closed another after it (review 7's n6 and f2; f1
    without the closing fence)."""
    def plant(t):
        lines, i, j = span(t, 'THEOREMS.md', b'| Folder | Statement')
        fence = [b'```'] if closed else []
        write(t, 'THEOREMS.md', b'\n'.join(lines[:i] + [b'```'] + lines[i:j] + fence + lines[j:]))
    return plant


HTML_TABLE9 = (b'<table><tr><th>Old statement</th><th>Successor</th></tr><tr><td>f32.F32_Statement.F32_REL</td>'
               b'<td>f32.F32_Statement.NOPE</td></tr></table>')
HTML_ANCHOR9 = b'<table><tr><td>zz32</td><td>MK_ANCHOR_ZZ32</td></tr></table>'
CASES9 = {
    # review 7's G7-1: headers and a heading that imitate the proved table's, a successor table's and the Successors
    # heading with ASCII look-alikes (a capital I or a 1 for l, a 0 for o, rn for m)
    'Q82': also_proved(PROVED_HEAD8.replace(b'| Folder |', b'| FoIder |')),
    'Q83': also_proved(PROVED_HEAD8.replace(b'| Folder | Statement |', b'| F0lder | Staternent |')),
    'Q84': before_successors([b'Earlier successors:', b'',
                              SUCC_HEAD8.replace(b'| Old statement |', b'| OId statement |'), DELIM5,
                              b'| `f32.F32_Statement.F32_REL` | `f32.NOPE.NOT_A_STATEMENT` | replaces | x | '
                              b'2026-11-20 |']),
    'Q85': tail('THEOREMS.md', b'\n## Success0rs\n'),
    # review 7's R7S-2, G7-2 and R7-2: a backslash, a backtick run not closed on its line, a code span holding "|", a
    # code fence
    'Q86': tail('THEOREMS.md', b'\nNote: \\`<b>bold on GitHub</b>\\` here.\n'),
    'Q87': tail('THEOREMS.md', b'\nProse `x\ny` ' + HTML_TABLE9 + b' `z`\n'),
    'Q88': tail('THEOREMS.md', b'\n| Name | Value |\n|---|---|\n| a `b | <b>c</b> d` |\n'),
    'Q89': tail('THEOREMS.md', b'\nHidden on GitHub: \\`<!X this text is hidden>\\` end.\n'),
    'Q90': fenced_proved(True),
    'Q91': fenced_proved(False),
    'Q92': tail('THEOREMS.md', b'\n~~~\nx\n~~~\n'),
    'Q93': tail(ANCHORS, b'\n```\nx\n```\n'),
    'Q94': tail(ANCHORS, b'\n\\`' + HTML_ANCHOR9 + b'`\n'),
    # review 7's R7-3: characters outside printable ASCII that the file may not hold (U+3164, U+2800, U+034F, U+FE0F
    # in THEOREMS.md's prose; U+00F0, which THEOREMS.md may hold, in ANCHORS.md)
    'Q95': tail('THEOREMS.md', b'\nA filler \xe3\x85\xa4 here.\n'),
    'Q96': tail('THEOREMS.md', b'\nA blank \xe2\xa0\x80 here.\n'),
    'Q97': tail('THEOREMS.md', b'\nA joiner a\xcd\x8fb here.\n'),
    'Q98': tail('THEOREMS.md', b'\nA selector a\xef\xb8\x8f here.\n'),
    'Q99': tail(ANCHORS, b'\nVer\xc3\xb0andi.\n'),
    # decoys
    'E30': tail('THEOREMS.md', b'\n| Item | Count 10 |\n|---|---|\n| I | 1 |\n'),
    'E31': tail('THEOREMS.md', b'\n| Name | Value |\n|---|---|\n| a | `<b>` |\n'),
    'E32': tail('THEOREMS.md', b'\nVer\xc3\xb0andi: \xc2\xb1 \xcf\x80 \xe2\x80\xa6\n'),
    'E33': tail('THEOREMS.md', b'\nUse ``a ` b`` here.\n'),
}
CASES.update(CASES9)


# ---- the tenth round (PREDICTIONS-inventory-10.txt): "#" and "[" outside a heading, fences in list items, links ----

def make_link(target, link):
    """A linked folder at link naming the folder target: a junction on Windows (which os.path.islink does not call a
    link), a symbolic link on POSIX."""
    if os.name == 'nt':
        import _winapi
        _winapi.CreateJunction(target, link)
    else:
        os.symlink(target, link, target_is_directory=True)


def linked_folder(rel, target_rel=None):
    """A linked folder at rel of the copy, naming the copy's folder target_rel, or (None) a new empty folder beside
    the copy."""
    def plant(t):
        if os.path.lexists(at(t, rel)):
            raise NotApplied('%s exists' % rel)
        if target_rel is None:
            target = t + '-empty'
            os.makedirs(target)
        else:
            target = at(t, target_rel)
            if not os.path.isdir(target):
                raise NotApplied('%s is absent' % target_rel)
        make_link(target, at(t, rel))
        return 'a junction' if os.name == 'nt' else 'a symbolic link'
    return plant


CASES10 = {
    # review 8's R8S-1: a heading after container markers this reader does not open (a nested list item, a block quote
    # in a list item, a footnote)
    'R01': tail('THEOREMS.md', b'\n- - ## Successors\n'),
    'R02': tail('THEOREMS.md', b'\n- > ## Successors\n'),
    'R03': tail('THEOREMS.md', b'\n- - ## Successors\n\n    | Old | New |\n    |---|---|\n'
                b'    | `f32.F32_Statement.F32_REL` | `f32.F32_Statement.NOPE` |\n'),
    'R04': tail('THEOREMS.md', b'\nSee x[^n].\n\n[^n]: ## Successors\n'),
    # review 8's G8-1: a link reference definition, an image, a footnote, a task-list box
    'R05': tail('THEOREMS.md', b'\n[//]: # (hidden: the f32 row names F32_CR)\n'),
    'R06': tail('THEOREMS.md', b'\n![Proved theorems](https://example.invalid/proved-table.png)\n'),
    'R07': tail(ANCHORS, b'\n[//]: # (hidden)\n'),
    'R08': tail('THEOREMS.md', b'\nx[^1]\n\n[^1]: y\n'),
    'R09': tail('THEOREMS.md', b'\n- [ ] x\n'),
    # review 8's R8S-6: a tilde fence opened in a list item
    'R10': tail('THEOREMS.md', b'\n- ~~~\n  x\n'),
    'R11': tail(ANCHORS, b'\n- ~~~\n  x\n'),
    # review 8's controls (N01c, N02c, FN2, E01c), each refused before this round too
    'R12': tail('THEOREMS.md', b'\n## Successors again\n'),
    'R13': tail('THEOREMS.md', b'\n- ## Successors\n'),
    'R14': tail('THEOREMS.md', b'\nSee x[^n].\n\n[^n]: x\n\n    ## Successors\n'),
    'R15': tail('THEOREMS.md', b'\n  ~~~\n  x\n'),
    # review 8's R8S-4: a linked folder, which os.walk enters when it is a junction
    'R16': linked_folder('kernel/coq/zz', 'kernel/coq/f32'),
    'R17': linked_folder('kernel/coq/gate/j'),
}
CASES.update(CASES10)

# ---- the eleventh round (PREDICTIONS-inventory-11.txt): a setext heading's underline under any line ------------------
OLD_NEW11 = b'| Old | New |\n|---|---|\n| `f32.F32_Statement.F32_REL` | `f32.F32_Statement.NOPE` |\n'


def indented(b, n):
    return b''.join(b' ' * n + x + b'\n' for x in b.rstrip(b'\n').split(b'\n'))


CASES11 = {
    'R18': tail('THEOREMS.md', b'\nIntro\n=====\nSuccessors\n----------\n\n' + OLD_NEW11),
    'R19': tail('THEOREMS.md', b'\nIntro\n--\nSuccessors\n----------\n\n' + OLD_NEW11),
    'R20': tail('THEOREMS.md', b'\n1.  a\n    ***\n    Successors\n    ---\n\n' + indented(OLD_NEW11, 4)),
    'R21': tail('THEOREMS.md', b'\nSuccessors\n----------\n\n' + OLD_NEW11),
    'R22': tail('THEOREMS.md', b'\n- a\n  ***\n  Successors\n  ---\n\n' + indented(OLD_NEW11, 2)),
    'R23': tail('THEOREMS.md', b'\n- Successors\n  of 2026-11-21\n  -------------\n\n' + indented(OLD_NEW11, 2)),
    'R24': tail('THEOREMS.md', b'\n1. Successors\n   of 2026-11-21\n   -------------\n'),
    'R25': tail('THEOREMS.md', b'\n- a\n  - Successors\n    of 2026-11-21\n    -------------\n'),
    'R26': tail(ANCHORS, b'\nNotes\n=====\n'),
    'E34': tail('THEOREMS.md', b'\nx\n\n=====\n'),
}
CASES.update(CASES11)
# the twelfth round (PREDICTIONS-inventory-12.txt): a table without pipes, trailing blanks, an ANCHORS.md underline
CASES12 = {
    'R28': tail('THEOREMS.md', b'\nSuccessor\n:-\n`f32.F32_Statement.NOPE`\n'),
    'R29': tail(ANCHORS, b'\nFolder\n:-\n`x`\n'),
    'R30': tail('THEOREMS.md', b'\nIntro\n=====  \n'),
    'R31': tail(ANCHORS, b'\nNotes\n-----\n'),
}
CASES.update(CASES12)
# the thirteenth round (PREDICTIONS-inventory-13.txt): a line of U+00A0 above an underline; a "-:" line
CASES13 = {
    'R32': tail('THEOREMS.md', b'\nSuccessors\n\xc2\xa0\n----------\n'),
    'R33': tail('THEOREMS.md', b'\nSuccessor\n-:\n`f32.F32_Statement.NOPE`\n'),
}
CASES.update(CASES13)
# Cases run on the honest copy with arguments, held to their predictions (PREDICTIONS-inventory-4.txt, -8.txt, -9.txt).
USAGE_CASES = ('U01', 'U02', 'U03', 'U04', 'U05', 'U06', 'U07')
# U02's second output path: the first's, spelled with a long-path prefix on Windows and a leading "//" on POSIX
LONG = '\\\\?\\' if os.name == 'nt' else '/'
CASE_FOLDS = os.path.normcase('A') == os.path.normcase('a')


# ---- reading the predictions and the checker's output ----------------------------------------------------------------

def predictions():
    """{id: (name, set of rows predicted to fail, or None for HELD)} from every predictions file, and the problems."""
    cases, probs = {}, []
    for fname in PREDICTIONS:
        cur, named = None, set()
        with open(os.path.join(HERE, fname), 'rb') as f:
            lines = f.read().decode('utf-8').split('\n')
        for n, line in enumerate(lines, 1):
            if line == '' or line.startswith('#'):
                continue
            m = re.fullmatch(r'([PQRDEU]\d\d) ([a-z0-9-]+): (.+)', line)
            if m:
                if m.group(1) in named or (m.group(1) in cases and fname not in SUPERSEDING):
                    probs.append('%s line %d: %s twice' % (fname, n, m.group(1)))
                elif fname in SUPERSEDING and cases.get(m.group(1), [None])[0] != m.group(2):
                    probs.append('%s line %d: %s %s predicts again no earlier case of that id and name'
                                 % (fname, n, m.group(1), m.group(2)))
                named.add(m.group(1))
                cur = m.group(1)
                cases[cur] = [m.group(2), set(), False]
                continue
            if cur is None:
                probs.append('%s line %d: not under a case' % (fname, n))
            elif line == '  HELD':
                cases[cur][2] = True
            elif line == '  USAGE WHERE CASE FOLDS, ELSE HELD':
                cases[cur][2] = 'usage-or-held'
            elif line == '  USAGE':
                cases[cur][2] = 'usage'
            elif line.startswith('  USAGE SAYING ') and len(line) > len('  USAGE SAYING '):
                cases[cur][2] = ('usage-saying', line[len('  USAGE SAYING '):])
            elif line.startswith('  FAIL '):
                cases[cur][1].add(line[len('  FAIL '):])
            else:
                probs.append('%s line %d: not read' % (fname, n))
    out = {}
    for k, (name, rows, held) in cases.items():
        if k[0] in 'PQR' and (held or not rows):
            probs.append('%s: a plant must predict failing rows' % k)
        if k[0] in 'DE' and (rows or held is not True):
            probs.append('%s: a decoy must predict HELD' % k)
        if k[0] == 'U' and (rows or not (held in ('usage-or-held', 'usage', True) or isinstance(held, tuple))):
            probs.append('%s: a usage case must predict "USAGE WHERE CASE FOLDS, ELSE HELD", "USAGE", "USAGE SAYING '
                         '<words>" or "HELD"' % k)
        out[k] = (name, held if k[0] == 'U' else None if held else rows)
    return out, probs


def run(root, *extra):
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    try:
        p = subprocess.run([sys.executable, '-B', CHECKER, '--root', root] + list(extra), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env, timeout=600)
    except subprocess.TimeoutExpired:
        return None, '', ''
    return (p.returncode, p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n'),
            p.stderr.decode('utf-8', 'replace'))


def read_output(out):
    """(rows {name: ok}, digest, held, problems): each line a row, the digest line or the verdict line (the last)."""
    lines = out.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    rows, digest, verdict, probs = {}, None, None, []
    for k, line in enumerate(lines):
        m = ROW.fullmatch(line)
        if m and verdict is None and digest is None:
            if m.group(1) in rows:
                probs.append('a row twice: %s' % m.group(1))
            rows[m.group(1)] = m.group(2) == 'ok'
            continue
        m = DIGEST.fullmatch(line)
        if m and digest is None and verdict is None:
            digest = m.group(1)
            continue
        m = VERDICT.fullmatch(line)
        if m and verdict is None and k == len(lines) - 1:
            verdict = m
            continue
        probs.append('a line out of place: %r' % line[:120])
    held = None
    if verdict is None:
        probs.append('no verdict line last')
    elif verdict.group(1) is not None:
        held = True
        if not (int(verdict.group(1)) == int(verdict.group(2)) == len(rows) and all(rows.values())):
            probs.append('HELD with counts %s of %s over %d rows' % (verdict.group(1), verdict.group(2), len(rows)))
    else:
        held = False
        failed = sum(1 for v in rows.values() if not v)
        if not (int(verdict.group(3)) == failed >= 1 and int(verdict.group(4)) == len(rows)):
            probs.append('FAILED with counts %s of %s over %d rows, %d failing'
                         % (verdict.group(3), verdict.group(4), len(rows), failed))
    if digest is None:
        probs.append('no digest line')
    return rows, digest, held, probs


def copy_into(t):
    for rel in COPIED:
        src = at(ROOT, rel)
        if os.path.isdir(src):
            shutil.copytree(src, at(t, rel))
        else:
            os.makedirs(os.path.dirname(at(t, rel)), exist_ok=True)
            shutil.copyfile(src, at(t, rel))


def few(items, k=4):
    items = sorted(items)
    return ', '.join(items[:k]) + (' and %d more' % (len(items) - k) if len(items) > k else '')


def judged(code, out, want_fail):
    """(ok, detail) for a run that must hold (want_fail None) or fail with exactly the rows of want_fail."""
    if code is None:
        return False, 'the checker did not end in time'
    rows, _, held, probs = read_output(out)
    if probs:
        return False, 'output not read: %s' % '; '.join(probs[:3])
    failing = set(r for r, ok in rows.items() if not ok)
    if want_fail is None:
        if code == 0 and held and not failing:
            return True, 'HELD, %d rows' % len(rows)
        return False, 'exit %s; failing: %s' % (code, few(failing) or 'none')
    unpredicted, missed = failing - want_fail, want_fail - failing
    if code == 1 and held is False and not unpredicted and not missed:
        return True, 'FAILED, exactly the %d predicted of %d rows' % (len(failing), len(rows))
    return False, 'exit %s; failing but not predicted: %s; predicted but ok: %s' % (
        code, few(unpredicted) or 'none', few(missed) or 'none')


def volume_form(p):
    """The absolute path p written as Windows' volume GUID path ("\\\\?\\Volume{GUID}\\" and the rest), which a
    long-path prefix taken off before resolving would leave relative; None when its drive has no volume name. On POSIX,
    which has no such form, p with a leading "//" (the case then runs that form)."""
    p = os.path.abspath(p)
    if os.name != 'nt':
        return '/' + p
    import ctypes
    drive = os.path.splitdrive(p)[0]
    buf = ctypes.create_unicode_buffer(100)
    if len(drive) != 2 or not ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW(drive + '\\', buf, 100):
        return None
    return buf.value + p[len(drive) + 1:]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def main():
    for fname in PREDICTIONS:
        with open(os.path.join(HERE, fname), 'rb') as f:
            print('predictions tools/ci/tests/%s sha256 %s' % (fname, sha(f.read())))
    pred, probs = predictions()
    defined = set(CASES) | set(USAGE_CASES)
    if set(pred) != defined:
        probs.append('plants and decoys defined here but not predicted: %s; predicted but not defined: %s'
                     % (few(defined - set(pred)) or 'none', few(set(pred) - defined) or 'none'))
    report('predictions', not probs, '%d plants and decoys, each predicted' % len(pred) if not probs
           else '; '.join(probs[:3]))

    work = tempfile.mkdtemp(prefix='inventory-test-')
    try:
        code, real_out, _ = run(ROOT)
        ok, det = judged(code, real_out, None)
        report('honest: the real tree', ok, det)

        base = os.path.join(work, 'base')
        copy_into(base)
        code, copy_out, _ = run(base)
        ok, det = judged(code, copy_out, None)
        report('copy: the same output as the real tree', ok and copy_out == real_out,
               det if not ok else 'line for line' if copy_out == real_out else 'the outputs differ')

        t = os.path.join(work, 'outputs')
        shutil.copytree(base, t)
        jp, mp = os.path.join(work, 'inventory.json'), os.path.join(work, 'matrix.json')
        code, out, _ = run(t, '--json', jp, '--matrix-out', mp)
        ok, det = judged(code, out, None)
        bad = [] if ok else [det]
        if ok:
            if out != copy_out:
                bad.append('a second run printed other lines')
            try:
                with open(jp, 'rb') as f:
                    j = json.loads(f.read().decode('utf-8'))
                with open(mp, 'rb') as f:
                    mb = f.read()
            except (OSError, ValueError) as e:
                j, mb = None, b''
                bad.append('an output file not read: %s' % type(e).__name__)
            if j is not None:
                rows, digest, _, _ = read_output(out)
                obj = {k: j.get(k) for k in ('gated', 'mirrors', 'gate_dir_files')}
                if j.get('schema') != 'skuldd-inventory/1' or j.get('held') is not True:
                    bad.append('JSON schema or held not as written')
                if not (j.get('digest') == digest == sha(canonical(obj))):
                    bad.append('JSON digest, printed digest and canonical sha256 differ')
                if {r['name']: r['ok'] for r in j.get('rows', [])} != rows:
                    bad.append('JSON rows differ from the printed rows')
                folders = [g['folder'] for g in j['gated']]
                if folders != sorted(set(folders)) or not folders:
                    bad.append('JSON gated folders not sorted, unique and present')
                for g in j['gated']:
                    if g['frozen4_sha256'] != sha(read(t, 'kernel/coq/%s/FROZEN4.txt' % g['folder'])):
                        bad.append('%s: frozen4_sha256 is not the file\'s' % g['folder'])
                want = json.dumps({'include': [{'folder': f, 'anchor': 'MK_ANCHOR_' + f.upper()} for f in folders]},
                                  separators=(',', ':')).encode('utf-8') + b'\n'
                if mb != want:
                    bad.append('the matrix is not the one line expected')
        report('outputs: --json and --matrix-out', not bad,
               'two runs agree; JSON and matrix as specified' if not bad else '; '.join(bad[:3]))

        for k in sorted(CASES):
            name, want = pred.get(k, ('?', set()))
            t = os.path.join(work, k)
            shutil.copytree(base, t)
            try:
                note = CASES[k](t)
            except NotApplied as e:
                report('%s %s' % (k, name), False, 'plant not applied: %s' % e)
                continue
            code, out, _ = run(t)
            ok, det = judged(code, out, want)
            report('%s %s' % (k, name), ok, det + ('' if not isinstance(note, str) else ' (%s)' % note))
            shutil.rmtree(t, ignore_errors=True)

        t = os.path.join(work, 'no-matrix')
        shutil.copytree(base, t)
        jp, mp = os.path.join(work, 'failed.json'), os.path.join(work, 'stale-matrix.json')
        with open(mp, 'wb') as f:
            f.write(b'{"include":[{"folder":"stale","anchor":"MK_ANCHOR_STALE"}]}\n')
        try:
            CASES['P11'](t)
            code, out, _ = run(t, '--json', jp, '--matrix-out', mp)
            ok, det = judged(code, out, pred.get('P11', ('', set()))[1])
        except NotApplied as e:
            ok, det = False, 'plant not applied: %s' % e
        bad = [] if ok else [det]
        if os.path.lexists(mp):
            bad.append('the stale matrix file is still there')
        try:
            with open(jp, 'rb') as f:
                j = json.loads(f.read().decode('utf-8'))
            if j.get('held') is not False or not j.get('verdict', '').startswith('INVENTORY FAILED:'):
                bad.append('the JSON does not say FAILED')
        except (OSError, ValueError):
            bad.append('no JSON written')
        report('no-matrix: a failed run writes no matrix', not bad,
               'matrix removed, JSON says FAILED' if not bad else '; '.join(bad[:3]))

        afile = os.path.join(work, 'a-file')
        with open(afile, 'wb') as f:
            f.write(b'x\n')
        same = os.path.join(work, 'same.json')
        for case, args in (('usage: no --root', []),
                           ('usage: a root that is a file', ['--root', afile]),
                           ('usage: an output in a missing folder',
                            ['--root', base, '--matrix-out', os.path.join(work, 'missing', 'm.json')]),
                           ('usage: both outputs one file', ['--root', base, '--json', same, '--matrix-out', same])):
            env = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
            p = subprocess.run([sys.executable, '-B', CHECKER] + args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env, timeout=600)
            out = p.stdout.decode('utf-8', 'replace')
            report(case, p.returncode == 2 and 'INVENTORY HELD' not in out,
                   'exit %d' % p.returncode)

        # U01: one output file named in two cases of letters (where the file system folds case, one file)
        name, want = pred.get('U01', ('?', None))
        jp, mp = os.path.join(work, 'u01.json'), os.path.join(work, 'U01.JSON')
        code, out, _ = run(base, '--json', jp, '--matrix-out', mp)
        if want != 'usage-or-held':
            ok, det = False, 'no usable prediction'
        elif CASE_FOLDS:
            ok = code == 2 and 'INVENTORY HELD' not in out
            det = 'normcase folds case here: exit %s, expected 2 (one file)' % code
        else:
            ok = code == 0 and os.path.isfile(jp) and os.path.isfile(mp)
            det = 'normcase keeps case here: exit %s, %s' % (code, 'both files written' if ok else 'not both written')
        report('U01 %s' % name, ok, det)

        # U02, U03: one output file named twice, with a long-path prefix (U02) or as it is (U03): a usage error, and
        # nothing written
        # U04: the same, the second written as Windows' volume GUID path (a leading "//" on POSIX)
        for case, second in (('U02', lambda p: LONG + os.path.abspath(p)), ('U03', lambda p: p),
                             ('U04', volume_form)):
            name, want = pred.get(case, ('?', None))
            jp = os.path.join(work, case.lower() + '.json')
            if second(jp) is None:
                report('%s %s' % (case, name), False, 'the drive of %s has no volume name; not built' % jp)
                continue
            code, out, _ = run(base, '--json', jp, '--matrix-out', second(jp))
            ok = want == 'usage' and code == 2 and 'INVENTORY HELD' not in out and not os.path.lexists(jp)
            report('%s %s' % (case, name), ok, 'exit %s, %s' % (code, 'nothing written' if not os.path.lexists(jp)
                                                                 else 'a file written'))

        # U05: --json and --matrix-out two names of one file (a hard link); U06: --json a file that has another name
        # (a hard link to a file the run must not write). Each: a usage error saying the predicted words, and no
        # file's bytes changed. U07: a decoy, --json an existing file with one name: HELD, the file now the JSON.
        for case in ('U05', 'U06', 'U07'):
            name, want = pred.get(case, ('?', None))
            first = os.path.join(work, case.lower() + '.json')
            other = os.path.join(work, case.lower() + '-other.json')
            with open(other if case == 'U06' else first, 'wb') as f:
                f.write(b'bytes the run must not change\n' if case != 'U07' else b'a stale output\n')
            if case == 'U05':
                os.link(first, other)
                args, kept = ['--json', first, '--matrix-out', other], first
            elif case == 'U06':
                os.link(other, first)
                args, kept = ['--json', first], other
            else:
                args, kept = ['--json', first], None
            code, out, err = run(base, *args)
            if isinstance(want, tuple) and want[0] == 'usage-saying':
                unchanged = read(work, os.path.basename(kept)) == b'bytes the run must not change\n'
                ok = code == 2 and 'INVENTORY HELD' not in out and want[1] in err and unchanged
                det = 'exit %s, %s; %s' % (code, 'the words predicted' if want[1] in err else 'not the words predicted',
                                           'no bytes changed' if unchanged else 'a file CHANGED')
            elif want is True:
                written = read(work, os.path.basename(first))
                ok, det = judged(code, out, None)
                ok = ok and written.startswith(b'{') and b'"skuldd-inventory/1"' in written
                det += '; the existing file %s' % ('now holds the JSON' if ok else 'does not hold the JSON')
            else:
                ok, det = False, 'no usable prediction'
            report('%s %s' % (case, name), ok, det)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    n, k = len(RESULTS), sum(1 for r in RESULTS if not r)
    print('TEST inventory HELD: %d of %d cases' % (n, n) if not k else 'TEST inventory FAILED: %d of %d cases failed'
          % (k, n))
    return 0 if not k else 1


if __name__ == '__main__':
    sys.exit(main())
