# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/inventory.py: what CI must gate, found from the tree itself, and the tree's records of it held against each
# other. Standard library only (Python 3.12 or later). It reads the tree and writes only the files its options name.
#
#   python3 -B tools/ci/inventory.py --root ROOT [--json OUT] [--matrix-out FILE]
#
# Paths are relative to ROOT, written with "/". A gated folder is kernel/coq/<f> holding a gate.json; a mirror is
# verdandi/mathkernel/F32/<f> holding one (Verdandi's copy of a gated folder); <f> is a plain lower-case name.
#
# ROWS, one line each, "  <row> ok|FAIL  <detail>":
#   discovery  Every gate.json under ROOT (.git, out4 and __pycache__ skipped) is a gated folder's or a mirror's. At
#              least one folder is gated. No gated folder is one whose anchor variable would be MK_ANCHOR_CI (a folder
#              named ci), which holds the CI judge digest: such a folder is refused, not gated. No .v file under
#              kernel/coq lies outside a gated folder, and none under verdandi/mathkernel/F32 outside a mirror. A
#              linked folder (a symbolic link, or a junction, which os.walk would enter) is not entered and fails the
#              row whose walk met it (discovery, the two .v rows, gate dir): what lies behind a linked folder is not
#              read (a symbolic link to a file is read through; where a freeze list names that file, its bytes are
#              held to the listed sha256).
#   gate dir   kernel/coq/gate holds exactly expected-pa-flocq4.txt, freeze4.py, gate4.py and strict_read.py, and
#              nothing else at any depth, so no other module can shadow one the gate imports.
#   Markdown   THEOREMS.md and kernel/coq/ANCHORS.md are read in a named subset of Markdown (the function markdown), and
#              anything outside it fails. (1) A line ends at a line feed, a carriage return before it taken off (a CR LF
#              line end); a carriage return anywhere else, U+FEFF, a control character (tab included), a character of
#              Unicode category Cf and an ampersand (GitHub decodes character references) fail wherever they stand, and
#              so does any other character outside printable ASCII but those the file may hold (THEOREMS.md U+00B1,
#              U+00F0, U+03C0 and U+2026, the four it holds; ANCHORS.md none), so no invisible character (U+3164,
#              U+2800, a joiner or a variation selector among them) passes. (2) A heading's line (an ATX heading at any
#              indent, so one inside a list item too, and every line of a setext heading's paragraph) and a table's
#              header line (the line above a delimiter row) hold only printable ASCII and U+2026, and none of "[", "<"
#              and backslash. (3) A cell the inventory reads names from (the proved table's Statement, Statement file
#              and Closing theorem cells, the Successors table's Old statement and Successor cells) holds nothing but
#              commas and blanks outside its backtick spans. (4) In THEOREMS.md every delimiter row (at any indent,
#              outer pipes optional) lies under the header of the proved table, of a successor table, or of a table
#              whose header holds only letters, digits, blanks, commas, U+2026 and the marks "*", "_" and "`", so the
#              rows below read every table's header as GitHub shows it; ANCHORS.md holds exactly one delimiter row. (5)
#              "<!--" stands only on line 1, closed there, and "<" outside a code span only on line 1 and, in
#              THEOREMS.md, on the lines "<details>", "</details>" and "<summary>...</summary>", each followed by a
#              blank line ("<details>" by its summary line), since GitHub reads the lines after an HTML line as HTML up
#              to a blank line. (6) No list item's text starts with "#", and no line of "=" or "-" only stands under a
#              list item's line (GitHub may show a heading there). (7) No line holds a backslash (CommonMark reads one
#              before a mark as an escape, so a backtick after it opens no code span), a backtick run that no run of its
#              length closes on the line (a literal backtick, or a code span that runs on to a later line) or a code
#              span holding "|" (GitHub cuts a table row at its pipes before it reads code spans), so the code spans
#              rule 5 reads are those GitHub shows. (8) No line opens or closes a code fence (``` or ~~~ after any
#              indent, and after list markers, where it opens a fenced block inside the list item), whose lines GitHub
#              shows as code (a fence after a block-quote marker is not read as one: every line of such a block is a
#              block quote's line, which the containers' rule refuses). (9) No line holds a "[" (a link, an image, a
#              link reference definition, a footnote or a
#              task-list box: GitHub shows other text, a picture or nothing), apart from a THEOREMS.md heading's line,
#              where rule 2 refuses it. (10) No line holds a "#" followed by a blank or the line's end but a top-level
#              ATX heading's (at most three spaces, one to six "#", then a space or the line's end), so no heading
#              opens inside a nested list item, a block quote inside a list item or a footnote, which this reader does
#              not open (a "#" before a letter or a digit opens none; a line rule 1 refuses, a block quote's line and
#              a list item's line holding a "|" fail by those rules already). (11) No line of "=" only, or of "-"
#              only with a colon allowed at either end, stands directly under a line that is not blank (a blank line
#              holds only blanks and tabs), at any indent and in any container: such a line can be a setext heading's
#              underline or the delimiter row of a table without pipes, which GitHub shows and this reader does not
#              count (where it is neither, it is refused too), so neither file holds one.
#              In THEOREMS.md the heading rules (2, for a heading's line, 6, 10 and 11) fail the successor row, which
#              reads every heading (on a heading's line rule 2,
#              being stricter, stands for the backslash of rule 7, the second half of rule 1 and rule 9; rule 7's
#              backtick runs are not read there, since a heading's text is compared with its backticks taken out), rule
#              3 fails the row that reads the cell, and the others fail the row "THEOREMS.md: written in the Markdown
#              subset this reader reads" (printed only when the file is read); in ANCHORS.md every rule fails the
#              ANCHORS.md row.
#   THEOREMS.md  Its proved table has one row per gated folder and none for another folder. It is the one table of the
#              file whose header's first two cells are Folder and Statement, a header above any delimiter row counting
#              too when its outer pipes are left out (one or both) or it is indented, and it is written with outer
#              pipes. The file has exactly one heading whose text starts with "Successor", of any level or underlined (a
#              setext heading, its text the first line of the paragraph above the underline), at any indent, the text
#              read as GitHub shows it (the marks "*", "_" and "`" taken out) and with the ASCII look-alikes below
#              folded, and it is a "## Successors" heading, with a table under it (before the next heading) that has one
#              "Old statement" and one "Successor" column; the table may have no row. From that heading to the next
#              Markdown heading (one to six "#" then a space or the line's end), no other line reads as a table line and
#              no other line is a table's delimiter row, at any indent (a second table, with or without outer pipes, or
#              a stray row fails); and no other table of the file has an "Old statement" and a "Successor" column. Every
#              row names in those two columns statements of the proved table (in backticks, with or without "MKF."; a
#              bare name continues the module of the name before it, as in the proved table). The file holds no line of
#              a block quote (its first non-blank character ">") and no list item's line (after any indent, "-", "*",
#              "+" or a number then "." or ")", then a blank or the line's end) that holds a "|": GitHub shows a table
#              or a heading inside either, and this reader does not open them, so it refuses them (a row of its own,
#              printed only when THEOREMS.md is read; when it cannot be read, the two rows above fail).
#   Tables     A table line is read as GitHub reads one with outer pipes: at most three spaces before its first pipe.
#              After the body of each table read here (the proved table, the Successors table, ANCHORS.md's table)
#              the next line is absent, blank or the start of another block (a heading, a fenced block, a block
#              quote, a list item, a thematic break); any other line fails ("GitHub reads this line as a row of the
#              table above"), since GitHub reads it as one more row, with or without outer pipes. A header cell is
#              compared as GitHub shows it: in the subset, with the marks "*", "_" and "`" taken out. Where a header
#              cell or a heading's text is compared with the proved table's, a successor table's or the Successors
#              heading, ASCII look-alikes are folded first (a capital I and a 1 read as l, a 0 as o, then rn as m and
#              vv as w), so a table or heading that imitates one ("FoIder", "OId statement", "Success0rs") counts as
#              what it imitates and fails as a second one.
#   statement names  Every sentence of every statement file is read (comments left out; a string is one word, so a
#              "." or a command word in it is not read; "|" and ";" are words of their own wherever they stand). A
#              statement file holding, outside its comments and strings, a character other than printable ASCII, tab,
#              line feed, carriage return and form feed fails the row ("a character this row does not read"): Coq
#              reads more characters as letters than this reader does. A sentence starts, after any #[...] lists and
#              any of Local, Global, Polymorphic, Monomorphic, Cumulative, NonCumulative, Private and Program, with a
#              command of
#              NO_NAME below (Require, Import, Export, From ... Require, Open Scope, Close Scope, Set, Unset, Section,
#              End, Arguments, Check, Print: they define no name; the statement files use From, Open Scope and
#              Arguments) or with a command that defines names, and the row reads every name it defines: the name
#              after Definition, Theorem, Lemma, Corollary, Proposition, Fact, Remark, Example, Property, Fixpoint,
#              CoFixpoint, Function, Let, Instance or Ltac and the name after each "with" at depth 0 (outside
#              brackets and match ... end); for Inductive, CoInductive and Variant, each type's name (each block
#              between "with"s) and every constructor; for Record, Structure and Class, the name, its constructor
#              (Build_<name> when none is given), every field, or a Class's one method; for every inductive and
#              record name also <name>_rect, _ind, _rec and _sind, whether or not Coq makes them; every name of
#              Parameter(s), Axiom(s), Hypothesis, Hypotheses, Variable(s) and Conjecture(s); the name or string after
#              Notation and the string after Infix; the name after Module (and Module Type, Import, Export). Any other
#              sentence fails the row: "a command this row does not read" (among them Coercion, Canonical, Scheme,
#              Goal, Context, Proof and every tactic: a statement file holds no proof) or "a definition this row
#              cannot parse" (no plain name where one is due, an Instance without a name, a where clause, a term
#              before an inductive's :=, brackets that do not pair, text after the last sentence). Each name read is
#              defined in that one statement file only. The statement files are found from the gated folders: each
#              top-level <NAME>_Statement.v, and each file holding a statement its folder's Identity.v names (the
#              identity row ties those to THEOREMS.md's statement files). The one exception is the list SHARED_NAMES
#              below: FMAX32, in exp32r/RANGE_Statement.v and p32r/P32R_Statement.v, and only while its two
#              definitions are byte for byte the same sentence.
#   ANCHORS.md kernel/coq/ANCHORS.md, read in the subset, has one row per gated folder and none for another folder,
#              each naming its variable MK_ANCHOR_<F> (the folder's name in capitals) and a record. No line of the file
#              outside that table reads as a table line, and no other line is a table's delimiter row, at any indent;
#              the file holds no block quote and no list item holding a "|", as for THEOREMS.md. The gate job's step
#              reads the file with this script's own readers (markdown, then anchors_table), so the two read it alike
#              and refuse the same files (anything outside the subset, a stray row, a line GitHub reads as one more
#              row, a second table, a block quote or a list item holding a "|"); that step checks its own folder's row
#              only, and this row, which the gate job runs next, also refuses an unknown folder's row, a misnamed
#              variable and an empty record.
#   For each gated folder <f>, nine rows:
#     FROZEN4.txt is present, and every line is blank, a # comment or "<64 hex>  <path>" (gate4.py's grammar), no
#     path twice. Every path it lists is a file under kernel/coq with the listed sha256, and it lists every file the
#     folder's gate requires, by gate4.py's rule: gate/gate4.py, gate/strict_read.py, gate/expected-pa-<tier>.txt;
#     for the folder and each folder of its "deps", gate.json, every file of "files" and every generator script
#     named under "generated"; every plant file of the folder. (gate4.py's own row refuses the same list in the gate
#     job, after the image is built; this row refuses it before.) A listed path is read only when each of its parts
#     is a name that os.listdir gives in its folder, with exactly that spelling, and it is a plain file; otherwise it
#     is absent and is never read (a device name such as NUL, a name with a trailing dot or in another case of
#     letters, which Windows opens as another file and Linux does not: absent on every host).
#     gate.json is UTF-8 JSON: an object with no key twice, a "name", plain .v names under "files", "identity"
#     "Identity", a "tier" whose expected-pa file is in kernel/coq/gate, "deps" naming other gated folders, and
#     "plants" entries each with a "replace" map.
#     Its "files" are the folder's top-level .v files: none twice, none absent, none unlisted.
#     plants/*.v are exactly the files its "plants" entries put in, each plants/<name>.v put in place of a listed
#     file. No .v file lies in any other subfolder.
#     Identity.v defines the name it prints the assumptions of. The MKF names in that definition's type are the
#     statements of the folder's THEOREMS.md row, and those in its term the closing theorems, in the same order. Each
#     is MKF.<f>.<M>.<N> with <M>.v a file of the folder; the statements' modules are the row's statement file.
#     Identity.v is exactly three sentences: From MKF.<f> Require <the modules named>, the definition (its type the
#     statements joined by /\, its term the theorems nested in conj), and Print Assumptions of it.
#     Its ANCHORS.md value is the sha256 of its FROZEN4.txt.
#   For each mirror <f>, three rows: FROZEN4.txt is byte for byte its gated twin's; every path it lists is a file
#     under verdandi/mathkernel/F32 with the listed sha256 (read by the same exact spelling); every .v file of the
#     mirror is one it lists. Then one row for all mirrors: their gate/gate4.py and gate/strict_read.py are byte for
#     byte the kernel's.
#
# Then "INVENTORY DIGEST <hex>": the sha256 of json.dumps(obj, sort_keys=True, separators=(',', ':')) in UTF-8, where
# obj = {gated: [{folder, files (gate.json's order), plants (sorted), frozen4_sha256, identity_names: {statements,
# theorems}}], mirrors: [{folder, frozen4_sha256}], gate_dir_files (sorted)}, folders sorted; a value that could not
# be read is null. Last, one verdict line: "INVENTORY HELD: n of n rows" or "INVENTORY FAILED: k of n rows failed".
# Exit 0 only when it held, 1 when it failed, 2 on a usage error.
#   --json OUT         writes {schema "skuldd-inventory/1", the digest's obj, digest, held, rows, verdict}, always.
#   --matrix-out FILE  writes one line {"include":[{"folder":"<f>","anchor":"MK_ANCHOR_<F>"},...]}, folders sorted,
#                      only when every row held; otherwise it removes FILE if it exists, so no stale matrix is used.
#
# WHAT A PASS SHOWS. The gated folders are found from the tree, so a new folder is gated without a list to edit (and
# fails here until its ANCHORS.md and THEOREMS.md rows exist). Each gated folder's .v files are exactly its gate.json
# files and named plants, and its freeze list holds every file its gate requires, each as listed. The gate's folder
# holds nothing else. No gated folder takes the CI judge's variable. THEOREMS.md, the Identity files and ANCHORS.md
# name the same things (one proved table, one Successors heading, one successor table): the two Markdown files are
# read in a named subset of Markdown, and anything outside it fails, a block quote and a list item holding a "|"
# among it. Every statement file found is printable ASCII outside its
# comments and strings, every sentence of it is one the row reads, and no statement file defines a name another one
# defines (apart from FMAX32's one shared, identical definition). Verdandi's copies are byte for byte what they claim
# to copy.
# WHAT IT DOES NOT SHOW. That any proof holds: the gate shows that, in its container. That an anchor is the owner's:
# ANCHORS.md is inside the tree, so a folder, its freeze list and its ANCHORS.md row changed together hold here and
# fail only against the Actions variable the gate is given. That a statement, or THEOREMS.md's prose, is right. Names
# as Coq resolves them: the row compares names as written, in a sentence's own words; it does not read a name Coq
# makes itself other than those listed above (an automatic Instance name is refused instead), a notation is compared
# by its string as written (Infix "+" and Notation "x + y" are not compared), and a module's or section's names are
# read as plain names. Words are split this reader's way: where Coq, with the notations a file declares, would split
# a run of symbols other than "|" and ";" otherwise, a ":=" or ":" hidden in it makes a sentence this row cannot parse
# (ARGUED from the code, not from Coq's lexer). A statement file named otherwise that no Identity.v names is not
# found, so not read. That GitHub renders the subset as read here (ARGUED from the CommonMark and GitHub table
# specifications as remembered; not run on GitHub). A heading or a table inside an indented code block is counted,
# though GitHub shows code (an over-refusal; a code fence is refused). A look-alike of a header or heading that the
# fold does not list (another pair of characters a font draws alike) is read as written: a table or heading that
# imitates the proved table's, a successor table's or the Successors heading so is read as a plain one. Anything about
# the image, the toolchain or a CI run. The digest describes the gate inputs fully only when every row held.
import argparse
import collections
import hashlib
import json
import os
import posixpath
import re
import sys
import unicodedata

sys.dont_write_bytecode = True

SCHEMA = 'skuldd-inventory/1'
KERNEL = 'kernel/coq'
MIRROR_ROOT = 'verdandi/mathkernel/F32'
GATE_DIR_FILES = ('expected-pa-flocq4.txt', 'freeze4.py', 'gate4.py', 'strict_read.py')
MIRROR_GATE_FILES = ('gate4.py', 'strict_read.py')
SKIP = ('.git', 'out4', '__pycache__')
FOLDER = re.compile(r'[a-z][a-z0-9_]*')
LINE = re.compile(r'([0-9a-f]{64})  ([A-Za-z0-9_][A-Za-z0-9_.+-]*(?:/[A-Za-z0-9_][A-Za-z0-9_.+-]*)*)')
VNAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\.v')
PLANT_FILE = re.compile(r'plants/[A-Za-z0-9_][A-Za-z0-9_.+-]*\.v')
PLANT_NAME = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.+-]*')
GATE_NAME = re.compile(r'[A-Za-z0-9_]+')
SEPARATOR = re.compile(r':?-{3,}:?')
# Markdown as GitHub reads it: a heading (one to six "#" then a space, a tab or the line's end), and the lines that
# start another block after a table (a heading, a fenced block, a block quote, a list item, a thematic break), each
# after at most three spaces.
HEADING = re.compile(r' {0,3}#{1,6}(?:[ \t]|$)')
BLOCK_START = re.compile(r' {0,3}(?:#{1,6}(?:[ \t]|$)|```|~~~|>|[-+*](?:[ \t]|$)|[0-9]{1,9}[.)](?:[ \t]|$)'
                         r'|(?:\*[ \t]*){3,}$|(?:-[ \t]*){3,}$|(?:_[ \t]*){3,}$)')
# The containers this reader does not open, in THEOREMS.md and ANCHORS.md: a block quote (a line whose first non-blank
# character is ">") and a list item (a line that starts, after any indent, with "-", "*", "+" or a number then "." or
# ")", then a blank or the line's end). GitHub shows a table or a heading inside either; a line of a block quote, and a
# list item's line that holds a "|", fail instead. A setext underline: a line of "=" only or of "-" only.
QUOTE = re.compile(r'[ \t]*>')
LIST_ITEM = re.compile(r'[ \t]*(?:[-+*]|[0-9]{1,9}[.)])(?:[ \t]|$)')
# A heading, at any indent (one inside a list item is indented): an ATX heading's line, and a line of "=" only or of
# "-" only under a paragraph (a setext heading's underline). Read at any indent, an indented code line that looks like
# one is counted too (an over-refusal).
SETEXT = re.compile(r'[ \t]*(?:=+|-+)[ \t]*')
# rule 11: a setext heading's underline, or the delimiter row of a table without pipes (a colon at either end)
UNDERLINE = re.compile(r'[ \t]*(?:=+|:?-+:?)[ \t]*')
ATX = re.compile(r'[ \t]*#{1,6}(?:[ \t]+(.*?))?[ \t]*$')
# The Markdown subset THEOREMS.md and ANCHORS.md are read in (see the header and markdown() below)
LIST_HASH = re.compile(r'[ \t]*(?:[-+*]|[0-9]{1,9}[.)])[ \t]+#')
# A top-level ATX heading's line (at most three spaces, one to six "#", then a space or the line's end), the one line
# that may hold a "#" followed by a blank or the line's end: anywhere else such a "#" can open a heading GitHub shows
# inside a container this reader does not open (a nested list item, a block quote inside a list item, a footnote)
TOP_HEADING = re.compile(r' {0,3}#{1,6}( |$)')
HASH_OPENS = re.compile(r'#(?:[ \t]|$)')
# A line that opens or closes a fenced code block (three backticks or tildes, after any indent, also after list
# markers, where it opens a block inside the list item): refused, since GitHub shows the lines up to the closing fence
# as code, which the rows below would read as tables and headings
FENCE = re.compile(r'[ \t]*(?:(?:[-+*]|[0-9]{1,9}[.)])[ \t]+)*(?:```|~~~)')
# The characters outside printable ASCII each file may hold: THEOREMS.md the four it holds (plus-minus sign, eth, pi,
# horizontal ellipsis), ANCHORS.md none; any other (an invisible one such as U+3164 or U+2800 among them) fails
OUTSIDE_ASCII_ALLOWED = {'THEOREMS.md': '\u00b1\u00f0\u03c0\u2026', 'ANCHORS.md': ''}
# ASCII look-alikes folded before a header cell or a heading's text is compared with the proved table's, a successor
# table's or the Successors heading's: a capital I and a 1 read as l, a 0 as o (then, lower-cased, rn as m, vv as w)
LOOKALIKE = str.maketrans({'I': 'l', '1': 'l', '0': 'o'})
PLAIN_HEADER = re.compile('[A-Za-z0-9 ,*_`|\u2026]*')
HEADING_TEXT = re.compile('[ -~\u2026]*')
COMMENT_LINE = re.compile(r'<!--(?:(?!-->).)*-->')
SUMMARY_LINE = re.compile(r'<summary>[^<>]*</summary>')
DETAILS_LINES = ('<details>', '</details>')
IDENT = r"[A-Za-z_][A-Za-z0-9_']*"
QNAME = re.compile(r"%s(?:\.%s)*" % (IDENT, IDENT))
MKF_NAME = re.compile(r"(?<![A-Za-z0-9_'.])MKF(?:\.%s)+" % IDENT)
TOKEN = re.compile(r"/\\|[()]|[A-Za-z_][A-Za-z0-9_'.]*|\S")
PRINT_PA = re.compile(r'Print Assumptions (%s)' % IDENT)
DEFINITION = re.compile(r'Definition (%s) ?:(?!=) ?(.*?) ?:= ?(.*)' % IDENT)
REQUIRE = re.compile(r'From MKF\.(%s) Require((?: %s)+)' % (IDENT, IDENT))
# The statement-names row reads every sentence of a statement file (see the header): the commands below that define
# names, after any of PREFIXES and #[...] lists, and NO_NAME, the commands that define none. Any other sentence fails.
PREFIXES = ('Local', 'Global', 'Polymorphic', 'Monomorphic', 'Cumulative', 'NonCumulative', 'Private', 'Program')
NO_NAME = ('Require', 'Import', 'Export', 'From', 'Set', 'Unset', 'Section', 'End', 'Arguments', 'Check', 'Print')
NO_NAME_SCOPE = ('Open', 'Close')            # Open Scope and Close Scope
ONE_NAME = ('Definition', 'Theorem', 'Lemma', 'Corollary', 'Proposition', 'Fact', 'Remark', 'Example', 'Property',
            'Fixpoint', 'CoFixpoint', 'Function', 'Let', 'Instance', 'Ltac')
INDUCTIVE = ('Inductive', 'CoInductive', 'Variant')
RECORD = ('Record', 'Structure', 'Class')
ASSUMPTION = ('Parameter', 'Parameters', 'Axiom', 'Axioms', 'Hypothesis', 'Hypotheses', 'Variable', 'Variables',
              'Conjecture', 'Conjectures')
NOTATION = ('Notation', 'Infix')
SCHEMES = ('_rect', '_ind', '_rec', '_sind')  # read for every inductive and record name, whether or not Coq makes them
NAME = re.compile(IDENT)
QIDENT = re.compile(r"%s(?:\.%s)*" % (IDENT, IDENT))
# A word: a string, "#[", a (dotted) identifier, a number, a bracket, "|" or ";" (each a word of its own, so a
# constructor's bar and a field's semicolon split what stands beside them, as Coq reads them), or a run of other
# symbols. Only printable ASCII reaches it: a statement file holding another character outside its comments and
# strings fails the row (Coq reads more characters as letters than this reader does).
WORD = re.compile(r'''"(?:[^"]|"")*"|#\[|[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*|[0-9]+|[()\[\]{}]'''
                  r'''|[|;]|[^\sA-Za-z0-9_()\[\]{}"|;]+|\S''')
STRING = re.compile(r'"(?:[^"]|"")*"')
OPEN = {'(': ')', '[': ']', '{': '}', '#[': ']'}
MATCH = ('match', 'lazymatch', 'multimatch')
STATEMENT_FILE = re.compile(r'[a-z][a-z0-9_]*/[A-Za-z_][A-Za-z0-9_]*\.v')
STATEMENT_NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*_Statement\.v')
# A name two statement files may both define, with the two files: allowed only while the two definitions are byte for
# byte the same sentence. FMAX32 (the largest finite binary32 number) is defined alike in both.
SHARED_NAMES = {'FMAX32': ('exp32r/RANGE_Statement.v', 'p32r/P32R_Statement.v')}

ROWS = []


def add(name, ok, detail):
    ok = bool(ok)
    detail = one_line(detail)
    ROWS.append({'name': name, 'ok': ok, 'detail': detail})
    print('  %-70s %s  %s' % (name, 'ok' if ok else 'FAIL', detail))
    sys.stdout.flush()


def one_line(s):
    """The text on one printable line: every character Python does not call printable (line and paragraph separators,
    controls, an undecodable file name's surrogates) written as its escape."""
    return ''.join(c if c.isprintable() else '\\x%02x' % ord(c) if ord(c) < 0x100 else '\\u%04x' % ord(c)
                   for c in str(s))


def few(items, k=6):
    items = [str(x) for x in items]
    s = ', '.join(items[:k])
    return s + (' and %d more' % (len(items) - k) if len(items) > k else '')


def at(root, rel):
    return os.path.join(root, *rel.split('/')) if rel else root


def raw(p):
    try:
        with open(p, 'rb') as f:
            return f.read()
    except OSError:
        return None


def sha(b):
    return hashlib.sha256(b).hexdigest()


def text(b):
    """(str, problem) for a file's bytes, read as UTF-8."""
    if b is None:
        return None, 'absent'
    try:
        return b.decode('utf-8'), None
    except UnicodeDecodeError:
        return None, 'not UTF-8'


def linked(p):
    """True for a symbolic link, and for a junction (Windows), which os.path.islink does not call a link and os.walk
    enters."""
    return os.path.islink(p) or os.path.isjunction(p)


def walk(top, prune=()):
    """(files, dirs, errors) under top, as sorted '/' paths relative to top; (None, None, []) when top is not a folder.
    A pruned folder is neither listed nor entered. A linked folder (a symbolic link, or a junction) is listed as a
    folder and not entered, and it is also an error ("<path> (a linked folder)"), so the row that walked it fails:
    what lies behind a linked folder is never read as part of the tree (a symbolic link to a file is read
    through)."""
    if not os.path.isdir(top):
        return None, None, []
    files, dirs, errors = [], [], []

    def err(e):
        fn = getattr(e, 'filename', None)
        errors.append(os.path.relpath(fn, top).replace(os.sep, '/') if fn else type(e).__name__)
    for dp, dn, fn in os.walk(top, onerror=err):
        r = os.path.relpath(dp, top).replace(os.sep, '/')
        r = '' if r == '.' else r + '/'
        dn[:] = sorted(d for d in dn if d not in prune)
        dirs.extend(r + d for d in dn)
        links = [d for d in dn if linked(os.path.join(dp, d))]
        errors.extend(r + d + ' (a linked folder)' for d in links)
        dn[:] = [d for d in dn if d not in links]
        files.extend(r + f for f in fn)
    return sorted(files), sorted(dirs), sorted(errors)


def listdir(p):
    try:
        return sorted(os.listdir(p))
    except OSError:
        return []


def read_list(b):
    """A freeze list by gate4.py's grammar: (entries [(sha256, path)], unreadable line numbers, paths listed twice)."""
    entries, unread = [], []
    for n, line in enumerate(b.decode('latin-1').split('\n'), 1):
        if line == '' or line.startswith('#'):
            continue
        m = LINE.fullmatch(line)
        if m:
            entries.append((m.group(1), m.group(2)))
        else:
            unread.append('line %d' % n)
    count = collections.Counter(p for _, p in entries)
    return entries, unread, sorted(p for p, k in count.items() if k > 1)


def needed(f, cfgs):
    """(set of paths under kernel/coq that folder f's gate requires on its freeze list, problem), by gate4.py's rule;
    (None, problem) when a gate.json it needs does not give them. cfgs: {folder: gate.json object or None}."""
    cfg = cfgs.get(f)
    if cfg is None:
        return None, '%s/gate.json does not parse' % f
    try:
        deps = [d.strip('/') for d in cfg.get('deps', [])]
        bad = [d for d in deps if cfgs.get(d) is None]
        if bad:
            return None, 'the gate.json of its dependency %s does not parse or is absent' % few(bad)
        need = {'gate/gate4.py', 'gate/strict_read.py', 'gate/expected-pa-%s.txt' % cfg['tier']}
        for d in deps + [f]:
            need.add(d + '/gate.json')
            need.update(d + '/' + x for x in cfgs[d]['files'])
            need.update(posixpath.normpath(spec[0]) for spec in cfgs[d].get('generated', {}).values())
        for pl in cfg.get('plants', {}).values():
            need.update(posixpath.normpath(f + '/' + s) for s in pl['replace'].values())
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        return None, 'what its gate requires cannot be read from gate.json (%s)' % type(e).__name__
    if not all(isinstance(p, str) for p in need):
        return None, 'what its gate requires cannot be read from gate.json (a name is not text)'
    return need, None


def spelled(root, base, rel, names):
    """The path of base/rel under root when each part of rel is a name that os.listdir gives in its folder, with
    exactly that spelling; else None. names caches each folder's listing. On Windows "F32.v." and "f32.v" open F32.v;
    on Linux they are absent; read this way they are absent on every host."""
    cur = at(root, base)
    for part in rel.split('/'):
        if cur not in names:
            names[cur] = set(listdir(cur))
        if part not in names[cur]:
            return None
        cur = os.path.join(cur, part)
    return cur


def listed_hold(root, base, entries):
    """The entries whose file under base is absent or has another sha256. A path is read only when each of its parts
    is spelled as its folder lists it (see spelled) and it is a plain file; a folder, a device name such as NUL on
    Windows (which reads as empty there), a name with a trailing dot or another case of letters is absent."""
    off, names = [], {}
    for h, p in entries:
        path = spelled(root, base, p, names)
        b = raw(path) if path is not None and os.path.isfile(path) else None
        if b is None:
            off.append(p + ' (absent)')
        elif sha(b) != h:
            off.append(p)
    return off


def load_json(b):
    """(object, problem) for gate.json's bytes: UTF-8, JSON, an object, no key twice at any depth."""
    t, prob = text(b)
    if t is None:
        return None, prob
    twice = []

    def pairs(kv):
        keys = [k for k, _ in kv]
        twice.extend(sorted(set(k for k in keys if keys.count(k) > 1)))
        return dict(kv)
    try:
        v = json.loads(t, object_pairs_hook=pairs)
    except (ValueError, RecursionError) as e:
        return None, 'not JSON: %s' % e
    if twice:
        return None, 'a key twice: %s' % few(twice)
    if not isinstance(v, dict):
        return None, 'not a JSON object'
    return v, None


# ---- markdown tables -------------------------------------------------------------------------------------------------

def cells(line):
    """The cells of a table line with outer pipes, as GitHub reads one: at most three spaces before the first pipe
    (four or a tab make it code), white space after the last; None for any other line."""
    m = re.match(r' {0,3}', line)
    s = line[m.end():].rstrip(' \t')
    if len(s) < 2 or not s.startswith('|') or not s.endswith('|'):
        return None
    return [c.strip() for c in s[1:-1].split('|')]


def norm(cell):
    return ' '.join(cell.replace('`', '').replace('*', '').split()).lower()


def hnorm(cell):
    """A table header's cell or a heading's text as GitHub shows it, for comparing: HTML tags and the marks "*", "_"
    and "`" taken out, blanks joined, lower case. (A folder cell is read with norm, which keeps "_".)"""
    return ' '.join(re.sub(r'<[^>]*>', '', cell).replace('`', '').replace('*', '').replace('_', '').split()).lower()


def looks(cell):
    """A header cell or a heading's text as it looks, for telling whether it is the proved table's, a successor
    table's or the Successors heading: hnorm with the ASCII look-alikes folded (a capital I and a 1 read as l, a 0 as
    o, then rn as m and vv as w), so "FoIder", "OId statement" and "Success0rs" count as what they imitate."""
    return hnorm(cell.translate(LOOKALIKE)).replace('rn', 'm').replace('vv', 'w')


def container_lines(lines):
    """The line numbers (from 1) of the lines in a container this reader does not open: a block quote's line, and a list
    item's line that holds a "|" (GitHub shows a table or a heading inside either)."""
    return [k + 1 for k, line in enumerate(lines) if QUOTE.match(line) or ('|' in line and LIST_ITEM.match(line))]


def outside_code(line):
    """The line with its code spans taken out, as CommonMark reads them on one line: a run of n backticks opens a span
    that the next run of exactly n backticks closes; a run that nothing closes is kept as it is."""
    out, i, n = [], 0, len(line)
    while i < n:
        if line[i] != '`':
            out.append(line[i])
            i += 1
            continue
        j = i
        while j < n and line[j] == '`':
            j += 1
        k, close = j, None
        while k < n and close is None:
            if line[k] != '`':
                k += 1
                continue
            m = k
            while m < n and line[m] == '`':
                m += 1
            if m - k == j - i:
                close = m
            k = m
        if close is None:
            out.append(line[i:j])
            i = j
        else:
            out.append(' ')
            i = close
    return ''.join(out)


def code_spans(line):
    """([(start, end)] of the code spans of one line, paired as outside_code pairs them; the number of backtick runs
    that no run of their length closes on the line: a literal backtick, or a code span that CommonMark lets run on to
    a later line of the paragraph)."""
    out, unclosed, i, n = [], 0, 0, len(line)
    while i < n:
        if line[i] != '`':
            i += 1
            continue
        j = i
        while j < n and line[j] == '`':
            j += 1
        k, close = j, None
        while k < n and close is None:
            if line[k] != '`':
                k += 1
                continue
            m = k
            while m < n and line[m] == '`':
                m += 1
            if m - k == j - i:
                close = m
            k = m
        if close is None:
            unclosed += 1
            i = j
        else:
            out.append((i, close))
            i = close
    return out, unclosed


def odd_chars(s):
    """What a line holds outside the characters the reader reads as GitHub shows them: each control character (tab
    included; a line feed ends the line), U+FEFF, each character of Unicode category Cf (a format character) and the
    ampersand (GitHub decodes character references), as U+XXXX or "&". (markdown() also refuses every other character
    outside printable ASCII that the file may not hold.)"""
    out = []
    for c in s:
        if c == '&':
            out.append('&')
        elif ord(c) < 32 or ord(c) == 127 or (ord(c) > 127 and unicodedata.category(c) in ('Cc', 'Cf')):
            out.append('U+%04X' % ord(c))
    return out


def heading_lines(lines):
    """The indexes of the lines GitHub can show as a heading's text: an ATX heading's line at any indent, and every
    line of a paragraph directly above a line of "=" only or of "-" only (back to a blank line or another block)."""
    out = set()
    for k, line in enumerate(lines):
        if ATX.match(line):
            out.add(k)
        elif SETEXT.fullmatch(line) and k >= 1 and lines[k - 1].strip() and not BLOCK_START.match(lines[k - 1]):
            j = k - 1
            while j >= 0 and lines[j].strip() and not BLOCK_START.match(lines[j]):
                out.add(j)
                j -= 1
    return out


def markdown(b, which):
    """THEOREMS.md's or kernel/coq/ANCHORS.md's bytes read in the subset of Markdown this reader reads: (lines,
    problems, heading problems). The lines are the text's lines split at a line feed, a carriage return before it taken
    off (a CR LF line end); lines is None when the bytes are absent or not UTF-8. Each problem names the file, the line
    and the rule broken (the header lists the rules). For THEOREMS.md the problems of its heading lines and of the list
    items GitHub may show as headings are returned apart, as heading problems: the successor row, which reads every
    heading, judges them. For ANCHORS.md every problem is in problems."""
    t, prob = text(b)
    if t is None:
        return None, ['%s is %s' % (which, prob)], []
    lines = [line[:-1] if line.endswith('\r') else line for line in t.split('\n')]
    theorems = which == 'THEOREMS.md'
    allowed = OUTSIDE_ASCII_ALLOWED.get(which, '')
    allowed_text = ', '.join('U+%04X' % ord(c) for c in allowed) or 'none'
    probs, heads = [], []
    shown = heading_lines(lines)
    delims = delimiter_rows(lines, 0, len(lines), any_indent=True)
    headers = {k - 1 for k in delims if k >= 1}
    for k, line in enumerate(lines):
        n = k + 1
        hp = heads if theorems else probs
        odd = odd_chars(line)
        if odd:
            probs.append('%s line %d: %s (a carriage return not before a line feed, a control character, a format '
                         'character or "&")' % (which, n, ', '.join(sorted(set(odd)))))
        if k in shown or k in headers:
            bad = sorted(set('U+%04X' % ord(c) for c in line if not HEADING_TEXT.fullmatch(c)))
            bad += [c for c in '[<\\' if c in line]
            if bad:
                (hp if k in shown else probs).append(
                    '%s line %d: a %s holding %s (only printable ASCII and U+2026, no "[", "<" or backslash)'
                    % (which, n, 'heading' if k in shown else "table's header", ', '.join(bad)))
        if LIST_HASH.match(line):
            hp.append('%s line %d: a list item whose text starts with "#" (GitHub may show a heading)' % (which, n))
        if k >= 1 and SETEXT.fullmatch(line) and LIST_ITEM.match(lines[k - 1]):
            hp.append('%s line %d: a line of "=" or "-" only under a list item (GitHub may show a heading)'
                      % (which, n))
        if k >= 1 and UNDERLINE.fullmatch(line) and lines[k - 1].strip(' \t'):
            hp.append('%s line %d: a line of "=" only, or of "-" only with a colon allowed at either end, under a '
                      'line that is not blank (it can be a setext heading\'s underline, or the delimiter row of '
                      'a table without pipes: GitHub shows what this reader does not count)' % (which, n))
        if FENCE.match(line):
            probs.append('%s line %d: a code fence (GitHub shows the lines up to the closing fence as code, which this '
                         'reader would read as tables and headings)' % (which, n))
        if (HASH_OPENS.search(line) and not TOP_HEADING.match(line)
                and not odd and not (QUOTE.match(line) or ('|' in line and LIST_ITEM.match(line)))):
            # (a line rule 1 refuses, a lone carriage return among them, and a block quote's line and a list item's
            # line holding a "|", which the containers' rule refuses, fail already)
            hp.append('%s line %d: a "#" followed by a blank or the line\'s end, on a line that is not a top-level '
                      'heading\'s (GitHub may show a heading in a list item, a block quote or a footnote)' % (which, n))
        if theorems and k in shown:
            continue                # a heading's "<", backslash and characters are judged above, with the heading
        if '[' in line:
            probs.append('%s line %d: "[" (a link, an image or a link reference definition: GitHub shows other text, '
                         'a picture or nothing)' % (which, n))
        foreign = sorted(set('U+%04X' % ord(c) for c in line if ord(c) > 126 and c not in allowed)
                         - set(odd))
        if foreign:
            probs.append('%s line %d: %s (a character outside printable ASCII that this file may not hold: %s)'
                         % (which, n, ', '.join(foreign), allowed_text))
        spans, unclosed = code_spans(line)
        if '\\' in line:
            probs.append('%s line %d: a backslash (CommonMark reads one before a mark as an escape, so a backtick '
                         'after it opens no code span)' % (which, n))
        if unclosed:
            probs.append('%s line %d: a backtick run that no run of its length closes on the line (a literal '
                         'backtick, or a code span that runs on to the next line)' % (which, n))
        if any('|' in line[a:b] for a, b in spans):
            probs.append('%s line %d: a code span holding "|" (GitHub cuts a table row at its pipes before it reads '
                         'code spans)' % (which, n))
        if '<!--' in line and k != 0:
            probs.append('%s line %d: an HTML comment (one is allowed on line 1 only, closed there)' % (which, n))
        if '<' not in outside_code(line):
            continue
        if k == 0:
            if not COMMENT_LINE.fullmatch(line):
                probs.append('%s line 1: HTML that is not one comment closed on the line' % which)
        elif theorems and (line in DETAILS_LINES or SUMMARY_LINE.fullmatch(line)):
            nxt = lines[k + 1] if k + 1 < len(lines) else ''
            if nxt.strip() and not (line == '<details>' and SUMMARY_LINE.fullmatch(nxt)):
                probs.append('%s line %d: an HTML line not followed by a blank line (GitHub reads the lines after it '
                             'as HTML up to a blank line)' % (which, n))
        else:
            probs.append('%s line %d: "<" outside a code span (HTML, which GitHub may show or hide; allowed on line '
                         '1 and, in THEOREMS.md, the lines <details>, </details> and <summary>...</summary>)'
                         % (which, n))
    if theorems:
        for k in delims:
            h = lines[k - 1] if k >= 1 else ''
            if h.strip() and (QUOTE.match(h) or ('|' in h and LIST_ITEM.match(h))):
                continue            # a container's line: the row "no block quote, no list item holding a bar" judges it
            c = loose_cells(h)
            if proved_header(c) or successor_header(c) or PLAIN_HEADER.fullmatch(h.strip()):
                continue
            probs.append('THEOREMS.md line %d: a table whose header is not the proved table\'s or a successor table\'s '
                         'and holds more than letters, digits, blanks, commas, U+2026 and the marks *, _ and `'
                         % (k + 1))
    elif len(delims) != 1:
        probs.append('%s: %d delimiter rows (at any indent), not 1 (the anchor table\'s)' % (which, len(delims)))
    return lines, probs, heads


def ticks(cell):
    return re.findall(r'`([^`]*)`', cell)


def beside(cell):
    """What a name cell holds outside its backtick spans other than commas and blanks ('' when nothing)."""
    return re.sub(r'[ ,]', '', re.sub(r'`[^`]*`', '', cell))


def untick(cell):
    s = cell.strip()
    if len(s) >= 2 and s[0] == '`' and s[-1] == '`':
        s = s[1:-1]
    return s.strip()


def table_at(lines, i):
    """(header cells, [(line number, cells)], problem) for the table whose header is lines[i]. After its body the next
    line must be absent, blank or the start of another block: GitHub reads any other line as one more row of the
    table, with or without outer pipes, and this reader would not."""
    head = cells(lines[i])
    sep = cells(lines[i + 1]) if i + 1 < len(lines) else None
    if sep is None or len(sep) != len(head) or not all(SEPARATOR.fullmatch(c) for c in sep):
        return head, [], 'line %d: no separator line under the header' % (i + 1)
    body, j = [], i + 2
    while j < len(lines) and cells(lines[j]) is not None:
        body.append((j + 1, cells(lines[j])))
        j += 1
    if j < len(lines) and lines[j].strip() and not BLOCK_START.match(lines[j]):
        return head, body, 'line %d: GitHub reads this line as a row of the table above' % (j + 1)
    return head, body, None


def loose_cells(line):
    """The cells of a line read with its outer pipes optional and any indent before it (wider than GitHub, which reads
    no table line after four spaces of indent, outside a list item); None when it holds no pipe."""
    s = line.strip()
    if '|' not in s:
        return None
    s = s[1:] if s.startswith('|') else s
    s = s[:-1] if s.endswith('|') else s
    return [c.strip() for c in s.split('|')]


def delimiter_rows(lines, lo, hi, any_indent=False):
    """The indexes in [lo, hi) of the lines GitHub can read as a table's delimiter row (cells of hyphens with an
    optional colon at either end, at least one pipe, outer pipes optional): every table GitHub renders has one. With
    any_indent, a line indented by four spaces or more counts too."""
    out = []
    for k in range(lo, hi):
        m = re.match(r'[ \t]*' if any_indent else r' {0,3}', lines[k])
        s = lines[k][m.end():].rstrip(' \t')
        if '|' not in s:
            continue
        inner = s[1:] if s.startswith('|') else s
        inner = inner[:-1] if inner.endswith('|') else inner
        if all(re.fullmatch(r'[ \t]*:?-+:?[ \t]*', p) for p in inner.split('|')):
            out.append(k)
    return out


def expand(items):
    """Names of a cell, the shorthand expanded: a dotted name stands alone (MKF. added when absent); a bare name
    continues the module of the name before it. Returns (names, unreadable items)."""
    out, prefix, bad = [], None, []
    for it in items:
        it = it.strip()
        if not QNAME.fullmatch(it):
            bad.append(it)
        elif '.' in it:
            full = it if it.startswith('MKF.') else 'MKF.' + it
            out.append(full)
            prefix = full.rsplit('.', 1)[0]
        elif prefix is None:
            bad.append(it)
        else:
            out.append(prefix + '.' + it)
    return out, bad


def proved_header(c):
    """True for a table header whose first two cells are Folder and Statement, ASCII look-alikes folded."""
    return c is not None and len(c) >= 2 and looks(c[0]) == 'folder' and looks(c[1]).startswith('statement')


def successor_header(c):
    """True for a table header with an "Old statement" column and a "Successor" column, ASCII look-alikes folded."""
    h = [looks(x) for x in c or []]
    return any(x.startswith('old statement') for x in h) and any(x.startswith('successor') for x in h)


def successor_shaped(lines):
    """The indexes of the header lines of every table of the file with an "Old statement" and a "Successor" column: a
    line with outer pipes, or a line directly above any delimiter row of the file (outer pipes optional, any
    indent)."""
    heads = {i for i, line in enumerate(lines) if successor_header(cells(line))}
    heads |= {k - 1 for k in delimiter_rows(lines, 0, len(lines), any_indent=True)
              if k >= 1 and successor_header(loose_cells(lines[k - 1]))}
    return sorted(heads)


def proved_table(lines):
    """THEOREMS.md's proved table: ({folder: {statements, files, theorems}}, problems, every statement named). A proved
    table's header is a line with outer pipes whose first two cells are Folder and Statement, or such a line with its
    outer pipes left out, or one of them only, directly above any delimiter row of the file (as GitHub reads a table):
    exactly one is allowed, written with outer pipes. A table inside a block quote or a list item is not read here;
    the row "no block quote, no list item holding a bar" refuses those lines instead."""
    heads = {i for i, line in enumerate(lines) if proved_header(cells(line))}
    heads |= {k - 1 for k in delimiter_rows(lines, 0, len(lines), any_indent=True)
              if k >= 1 and proved_header(loose_cells(lines[k - 1]))}
    if len(heads) != 1:
        return {}, ['%d proved tables (a header "Folder | Statement ...", with or without outer pipes), not 1'
                    % len(heads)], set()
    heads = sorted(heads)
    if cells(lines[heads[0]]) is None:
        return {}, ['line %d: the proved table is not written with outer pipes' % (heads[0] + 1)], set()
    head, body, prob = table_at(lines, heads[0])
    probs = [prob] if prob else []
    h = [hnorm(c) for c in head]
    if len(h) != 5 or h[2] != 'statement file' or not h[3].startswith('closing theorem'):
        probs.append('the header is not Folder, Statement, Statement file, Closing theorem, Gate')
        return {}, probs, set()
    rows, known = {}, set()
    for n, c in body:
        if len(c) != 5:
            probs.append('line %d: %d cells, not 5' % (n, len(c)))
            continue
        folder = ticks(c[0])
        if len(folder) != 1 or not FOLDER.fullmatch(folder[0]) or norm(c[0]) != folder[0]:
            probs.append('line %d: the folder cell is not one plain folder name in backticks' % n)
            continue
        f = folder[0]
        if beside(c[1]) or beside(c[2]) or beside(c[3]):
            probs.append('line %d (%s): text beside the names in the Statement, Statement file or Closing theorem cell '
                         '(only names in backticks, commas and blanks)' % (n, f))
            continue
        stmts, b1 = expand(ticks(c[1]))
        thms, b2 = expand(ticks(c[3]))
        known.update(stmts)
        if b1 or b2 or not stmts or not thms:
            probs.append('line %d (%s): names not read: %s' % (n, f, few(b1 + b2) or 'a column names nothing'))
            continue
        if f in rows:
            probs.append('line %d: a second row for %s' % (n, f))
            continue
        rows[f] = {'statements': stmts, 'files': [x.strip() for x in ticks(c[2])], 'theorems': thms}
    return rows, probs, known


def successor_headings(lines):
    """The indexes of the lines that start a heading GitHub can show with text that starts with "Successor": a heading
    of any level ("#" to "######"), its text after the "#"s; or a paragraph directly above a line of "=" only or of "-"
    only (a setext heading), its text the paragraph's first line (back to a blank line or the start of another block).
    The text is compared as GitHub shows it: HTML tags and the marks "*", "_" and "`" taken out, ASCII look-alikes
    folded (looks)."""
    out = []
    for k, line in enumerate(lines):
        m = ATX.match(line)
        if m:
            if looks(m.group(1) or '').startswith('successor'):
                out.append(k)
        elif SETEXT.fullmatch(line) and k >= 1 and lines[k - 1].strip() and not BLOCK_START.match(lines[k - 1]):
            j = k - 1
            while j >= 1 and lines[j - 1].strip() and not BLOCK_START.match(lines[j - 1]):
                j -= 1
            if looks(lines[j]).startswith('successor'):
                out.append(j)
    return sorted(set(out))


def successor_table(lines, known):
    """THEOREMS.md's "## Successors" table: (problems, number of rows, whether a table was found). The heading and
    its table are required: without them a row naming an unknown statement could stand under another heading. The
    section runs from the heading to the next Markdown heading; a table line in it that is not the one table's
    header, separator or body is refused, and so is a second delimiter row (a table without outer pipes, at any
    indent), so a second table cannot hold rows that are never read; and a table anywhere in the file with an "Old
    statement" and a "Successor" column is refused unless it is the one under the heading."""
    shown = successor_headings(lines)
    heads = [i for i in shown if re.match(r' {0,3}##[ \t]+successor', lines[i].lower())]
    if len(shown) > 1:
        return ['line %s: %d headings whose text starts with "Successor" (any level, or underlined), not 1'
                % (few(str(k + 1) for k in shown), len(shown))], 0, True
    if not heads:
        return ['no "## Successors" heading'], 0, False
    end = next((k for k in range(heads[0] + 1, len(lines)) if HEADING.match(lines[k])), len(lines))
    tab = [k for k in range(heads[0] + 1, end) if cells(lines[k]) is not None]
    if not tab:
        return ['line %d: no table under the "## Successors" heading' % (heads[0] + 1)], 0, False
    i = tab[0]
    head, body, prob = table_at(lines, i)
    if prob:
        return [prob], 0, True
    h = [hnorm(c) for c in head]
    old = [k for k, x in enumerate(h) if x.startswith('old statement')]
    new = [k for k, x in enumerate(h) if x.startswith('successor')]
    if len(old) != 1 or len(new) != 1:
        return ['line %d: the header has no single "Old statement" and "Successor" column' % (i + 1)], 0, True
    own = {i, i + 1} | {n - 1 for n, _ in body}
    stray = [str(k + 1) for k in tab if k not in own]
    stray += [str(k + 1) for k in delimiter_rows(lines, heads[0] + 1, end, any_indent=True) if k not in own]
    probs = ['line %s: a second table or a stray row under the Successors heading' % few(sorted(set(stray), key=int))
             ] if stray else []
    elsewhere = [str(k + 1) for k in successor_shaped(lines) if k != i]
    if elsewhere:
        probs.append('line %s: a table with "Old statement" and "Successor" columns that is not the one under the '
                     'Successors heading' % few(elsewhere))
    for n, c in body:
        if len(c) != len(head):
            probs.append('line %d: %d cells, not %d' % (n, len(c), len(head)))
            continue
        if beside(c[old[0]]) or beside(c[new[0]]):
            probs.append('line %d: text beside the names in the Old statement or Successor cell (only names in '
                         'backticks, commas and blanks)' % n)
            continue
        o, ob = expand(ticks(c[old[0]]))
        s, sb = expand(ticks(c[new[0]]))
        if not o or not s:
            probs.append('line %d: a column names no statement' % n)
        unknown = ob + sb + [x for x in o + s if x not in known]
        if unknown:
            probs.append('line %d: not a statement of the proved table: %s' % (n, few(unknown)))
        if o and set(o) == set(s):
            probs.append('line %d: a statement is named as its own successor' % n)
    return probs, len(body), True


def statement_files(root, gated):
    """The statement files of the gated folders, as '<f>/<file>' paths, sorted: each top-level file of a gated folder
    named <NAME>_Statement.v, and each file that holds a statement the folder's Identity.v names (MKF.<f>.<M>.<N> is
    in <f>/<M>.v). Found from the gated folders, not from THEOREMS.md, whose rows other rows judge."""
    files = set()
    for f in gated:
        fdir = at(root, KERNEL + '/' + f)
        for x in listdir(fdir):
            if STATEMENT_NAME.fullmatch(x) and os.path.isfile(os.path.join(fdir, x)):
                files.add(f + '/' + x)
        info, _ = identity(raw(at(root, KERNEL + '/' + f + '/Identity.v')))
        for s in (info or {}).get('statements', []):
            m = module_of(s, f)
            if m is not None and os.path.isfile(os.path.join(fdir, m + '.v')):
                files.add('%s/%s.v' % (f, m))
    return sorted(files)


class Unread(Exception):
    pass


def sentences(t):
    """The sentences of a text whose comments are blanked and whose strings are kept, each without its final ".": a
    sentence ends at a "." that is followed by white space or the end of the text, outside a string, and not after
    another "." (so ".." does not end one). Text after the last sentence is a problem."""
    out, start, i, n = [], 0, 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            j = i + 1
            while j < n and not (t[j] == '"' and not t.startswith('""', j)):
                j += 2 if t.startswith('""', j) else 1
            if j >= n:
                raise Unread('a string is not closed')
            i = j + 1
            continue
        if c == '.' and (i + 1 == n or t[i + 1].isspace()) and not (i and t[i - 1] == '.'):
            out.append(t[start:i])
            start = i + 1
        i += 1
    if t[start:].strip():
        raise Unread('text after the last sentence (no final period)')
    return out


def scan(words):
    """[(index, word, depth)]: the depth counts open (), [], {} and #[...] and open match ... end; Unread when they do
    not pair."""
    out, stack = [], []
    for k, w in enumerate(words):
        if w in OPEN:
            out.append((k, w, len(stack)))
            stack.append(OPEN[w])
        elif w in MATCH:
            out.append((k, w, len(stack)))
            stack.append('end')
        elif w in (')', ']', '}', 'end'):
            if not stack or stack[-1] != w:
                raise Unread('a definition this row cannot parse (%r does not close what is open)' % w)
            stack.pop()
            out.append((k, w, len(stack)))
        else:
            out.append((k, w, len(stack)))
    if stack:
        raise Unread('a definition this row cannot parse (%r is never closed)' % stack[-1])
    return out


def top(words, seps):
    """words split at the words of seps that stand at depth 0."""
    parts, cur = [], []
    for _k, w, d in scan(words):
        if d == 0 and w in seps:
            parts.append(cur)
            cur = []
        else:
            cur.append(w)
    return parts + [cur]


def at_top(words, w):
    return [k for k, x, d in scan(words) if d == 0 and x == w]


def a_name(words, k, what):
    """The name words[k] (a plain identifier, not qualified) and the index after it and any @{...} after it."""
    if k >= len(words) or not NAME.fullmatch(words[k]):
        raise Unread('a definition this row cannot parse (no plain name %s: %r)'
                     % (what, words[k] if k < len(words) else 'the end of the sentence'))
    j = k + 1
    if words[j:j + 2] == ['@', '{']:
        j = next(i for i, x, d in scan(words[j + 1:]) if d == 0 and x == '}') + j + 2
    return words[k], j


def body_after_define(words, what):
    """The words after the ":=" at depth 0 of an inductive or record block; Unread when there is none or when what
    comes before it (the name, its binders and its arity) holds a let, fix, cofix, fun or match at depth 0."""
    ks = at_top(words, ':=')
    if not ks:
        raise Unread('a definition this row cannot parse (%s without :=)' % what)
    if any(d == 0 and w in ('let', 'fix', 'cofix', 'fun') + MATCH for _k, w, d in scan(words[:ks[0]])):
        raise Unread('a definition this row cannot parse (a term before the := of %s)' % what)
    body = words[ks[0] + 1:]
    if at_top(body, 'where'):
        raise Unread('a definition this row cannot parse (a where clause in %s)' % what)
    return body


def fields(words):
    """The names of a record's fields, words being what stands between its braces."""
    names = []
    for part in top(words, (';',)):
        while part[:1] == ['#[']:
            part = part[next(k for k, w, d in scan(part) if d == 0 and w == ']') + 1:]
        if part:
            names.append(a_name(part, 0, 'for a field')[0])
            if at_top(part, 'where'):
                raise Unread('a definition this row cannot parse (a where clause in a field)')
    return names


def braced(words):
    """(constructor or None, the words between the braces) when words are [name] { ... } and nothing else."""
    k = 1 if words[:1] and NAME.fullmatch(words[0]) else 0
    if words[k:k + 1] != ['{'] or words[-1:] != ['}']:
        return None
    closes = [i for i, w, d in scan(words[k:]) if d == 0 and w == '}']
    if closes != [len(words) - k - 1]:
        return None
    return (words[0] if k else None), words[k + 1:-1]


def defined_names(s):
    """The names one sentence defines (comments blanked, strings kept, its final "." left out); Unread when the
    sentence is not one this row reads."""
    words = WORD.findall(s)
    i = 0
    while i < len(words) and (words[i] == '#[' or words[i] in PREFIXES):
        i = i + 1 if words[i] != '#[' else next(k for k, w, d in scan(words[i:]) if d == 0 and w == ']') + i + 1
    if i >= len(words):
        raise Unread('a command this row does not read (nothing after its attributes)')
    cmd, rest = words[i], words[i + 1:]
    scan(rest)
    if cmd in NO_NAME:
        if cmd == 'From' and not (len(rest) >= 2 and QIDENT.fullmatch(rest[0]) and rest[1] == 'Require'):
            raise Unread('a command this row does not read (From without Require)')
        return []
    if cmd in NO_NAME_SCOPE and rest[:1] == ['Scope']:
        return []
    if cmd == 'Let' and rest[:1] in (['Fixpoint'], ['CoFixpoint']):
        rest = rest[1:]
    if cmd in ONE_NAME:
        if cmd == 'Instance' and rest[:1] != [] and not NAME.fullmatch(rest[0]):
            raise Unread('a definition this row cannot parse (an Instance without a name: Coq makes its name)')
        names = [a_name(rest, 0, 'after %s' % cmd)[0]]
        names += [a_name(rest, k + 1, 'after with')[0] for k in at_top(rest, 'with')]
        return names
    if cmd in INDUCTIVE or cmd in RECORD:
        names = []
        for block in top(rest, ('with',)):
            name, _ = a_name(block, 0, 'after %s' % cmd)
            names += [name] + [name + x for x in SCHEMES]
            body = body_after_define(block, name)
            rec = braced(body)
            if rec is not None:
                names += [rec[0] or 'Build_' + name] + fields(rec[1])
            elif cmd in INDUCTIVE:
                segs = top(body, ('|',))
                if segs[:1] == [[]] and len(segs) > 1:
                    segs = segs[1:]
                for seg in segs if body else []:
                    names.append(a_name(seg, 0, 'for a constructor of %s' % name)[0])
                    sub = braced(seg[1:]) if len(seg) > 1 else None
                    if sub is not None:
                        names += fields(sub[1])
            elif cmd == 'Class' and len(body) > 1 and body[1] in (':', ':>', '::'):
                names.append(a_name(body, 0, 'for the method of %s' % name)[0])
            else:
                raise Unread('a definition this row cannot parse (the body of %s)' % name)
        return names
    if cmd in ASSUMPTION:
        if rest[:1] == ['Inline']:
            rest = rest[1:]
            if rest[:1] == ['(']:
                rest = rest[next(k for k, w, d in scan(rest) if d == 0 and w == ')') + 1:]
        names = []
        if rest[:1] and rest[0] in OPEN:
            groups, k = [], 0
            while k < len(rest):
                if rest[k] not in ('(', '{', '['):
                    raise Unread('a definition this row cannot parse (an assumption outside its brackets)')
                close = next(j for j, w, d in scan(rest[k:]) if d == 0 and w == OPEN[rest[k]]) + k
                groups.append(rest[k + 1:close])
                k = close + 1
        else:
            groups = [rest]
        for g in groups:
            colon = at_top(g, ':')
            if not colon:
                raise Unread('a definition this row cannot parse (an assumption without its type)')
            k = 0
            while k < colon[0]:
                name, k = a_name(g, k, 'of an assumption')
                names.append(name)
            if not names:
                raise Unread('a definition this row cannot parse (an assumption without a name)')
        return names
    if cmd in NOTATION:
        if rest[:1] and rest[0].startswith('"'):
            return [rest[0]]
        if cmd == 'Notation':
            return [a_name(rest, 0, 'after Notation')[0]]
        raise Unread('a definition this row cannot parse (Infix without its string)')
    if cmd == 'Module':
        if rest[:1] in (['Type'], ['Import'], ['Export']):
            rest = rest[1:]
        return [a_name(rest, 0, 'after Module')[0]]
    raise Unread('a command this row does not read (%s)' % cmd[:40])


def statement_names(root, files):
    """(problems, names read, statement files read, names shared as SHARED_NAMES allows, sentences read) for the
    given statement files: every sentence is read, and each name such a file defines is defined in that file only."""
    where, probs, nsent = collections.defaultdict(list), [], 0
    for rel in files:
        if not STATEMENT_FILE.fullmatch(rel):
            probs.append('%r is not a statement file of a folder' % rel)
            continue
        path = at(root, KERNEL + '/' + rel)
        t, prob = text(raw(path) if os.path.isfile(path) else None)
        if t is None:
            probs.append('%s/%s is %s' % (KERNEL, rel, prob))
            continue
        t, prob = uncomment(t, keep_strings=True)
        if t is None:
            probs.append('%s/%s: %s' % (KERNEL, rel, prob))
            continue
        wide = sorted(set(c for c in STRING.sub('', t) if not (' ' <= c <= '~' or c in '\t\n\r\f')))
        if wide:
            probs.append('%s/%s: a character this row does not read, outside a comment or a string: %s'
                         % (KERNEL, rel, ascii(''.join(wide[:4]))))
            continue
        try:
            sents = sentences(t)
        except Unread as e:
            probs.append('%s/%s: %s' % (KERNEL, rel, e))
            continue
        for s in sents:
            shown = ' '.join(s.split())
            if not shown:
                probs.append('%s/%s: an empty sentence' % (KERNEL, rel))
                continue
            nsent += 1
            try:
                names = defined_names(s)
            except (Unread, StopIteration) as e:
                why = str(e) if isinstance(e, Unread) else 'a definition this row cannot parse (a list not closed)'
                probs.append('%s/%s: %s: %s' % (KERNEL, rel, why, shown[:60]))
                continue
            for name in names:
                where[name].append((rel, s.strip()))
    shared = []
    for name in sorted(where):
        fs = sorted(set(f for f, _ in where[name]))
        if len(fs) < 2:
            continue
        if fs == sorted(SHARED_NAMES.get(name, ())):
            if len(set(s for _, s in where[name])) == 1:
                shared.append(name)
            else:
                probs.append('%s: its definitions in %s are not the same sentence' % (name, ' and '.join(fs)))
            continue
        probs.append('%s is defined in %s' % (name, ' and '.join(fs)))
    return probs, len(where), len(files), shared, nsent


def anchors_table(lines):
    """kernel/coq/ANCHORS.md's table: ({folder: (variable, value, record)}, problems). A block quote's line or a list
    item's line holding a "|" is a problem (a container this reader does not open), and so is a delimiter row at any
    indent outside the table (a table GitHub may show inside a list item)."""
    heads = [i for i, line in enumerate(lines)
             if cells(line) and len(cells(line)) >= 2 and hnorm(cells(line)[0]) == 'folder'
             and hnorm(cells(line)[1]) == 'variable']
    if len(heads) != 1:
        return {}, ['%d anchor tables (a header "| Folder | Variable | ..."), not 1' % len(heads)]
    head, body, prob = table_at(lines, heads[0])
    probs = [prob] if prob else []
    if len(head) != 4:
        return {}, probs + ['the header has %d cells, not 4' % len(head)]
    own = {heads[0], heads[0] + 1} | {n - 1 for n, _ in body}
    stray = [k for k, line in enumerate(lines) if k not in own and cells(line) is not None]
    stray += [k for k in delimiter_rows(lines, 0, len(lines), any_indent=True) if k not in own]
    if stray:
        probs.append('line %s: a table line or a second table outside the anchor table'
                     % few(str(k + 1) for k in sorted(set(stray))))
    boxed = container_lines(lines)
    if boxed:
        probs.append('line %s: a block quote, or a list item holding "|", which this reader does not read'
                     % few(str(k) for k in boxed))
    rows = {}
    for n, c in body:
        if len(c) != 4:
            probs.append('line %d: %d cells, not 4' % (n, len(c)))
            continue
        f = untick(c[0])
        if not FOLDER.fullmatch(f):
            probs.append('line %d: %r is not a plain folder name' % (n, f))
        elif f in rows:
            probs.append('line %d: a second row for %s' % (n, f))
        else:
            rows[f] = (untick(c[1]), untick(c[2]), c[3].strip())
    return rows, probs


# ---- Identity.v ------------------------------------------------------------------------------------------------------

def uncomment(t, keep_strings=False):
    """The text with comments (nested) replaced by spaces, newlines kept. As in Coq's lexer, a string inside a comment
    is a string ("" an escaped quote) and a "(*" or "*)" inside it does not count. Returns (text, problem); an
    identity file holds no string outside a comment. With keep_strings, a string outside a comment is kept as it is."""
    out, i, depth, n = [], 0, 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            j = i + 1
            while j < n:
                if t[j] == '"':
                    if j + 1 < n and t[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            if j >= n:
                return None, 'a string is not closed'
            if depth == 0 and keep_strings:
                out.append(t[i:j + 1])
                i = j + 1
                continue
            if depth == 0:
                return None, 'a string outside a comment'
            out.append(''.join(x if x == '\n' else ' ' for x in t[i:j + 1]))
            i = j + 1
            continue
        if t.startswith('(*', i):
            depth += 1
            out.append('  ')
            i += 2
            continue
        if depth and t.startswith('*)', i):
            depth -= 1
            out.append('  ')
            i += 2
            continue
        out.append(c if (depth == 0 or c == '\n') else ' ')
        i += 1
    if depth:
        return None, 'a comment is not closed'
    return ''.join(out), None


def identity(b):
    """(info, problem) for Identity.v's bytes: its sentences, the definition it prints the assumptions of, and the MKF
    names of that definition's type (statements) and term (theorems), in order."""
    t, prob = text(b)
    if t is None:
        return None, prob
    t, prob = uncomment(t)
    if t is None:
        return None, prob
    parts = re.split(r'\.(?=\s|$)', t)
    if parts[-1].strip():
        return None, 'text after the last sentence'
    sents = [' '.join(p.split()) for p in parts[:-1]]
    printed = [m.group(1) for m in (PRINT_PA.fullmatch(s) for s in sents) if m]
    if len(printed) != 1:
        return None, '%d Print Assumptions sentences, not 1' % len(printed)
    name = printed[0]
    defs = [(s, m) for s, m in ((s, DEFINITION.fullmatch(s)) for s in sents) if m and m.group(1) == name]
    if len(defs) != 1:
        return None, '%d definitions of %s, not 1' % (len(defs), name)
    s, m = defs[0]
    return {'name': name, 'sentences': sents, 'definition': s, 'type': m.group(2), 'term': m.group(3),
            'statements': MKF_NAME.findall(m.group(2)), 'theorems': MKF_NAME.findall(m.group(3))}, None


def conj_type(names):
    out = []
    for k, n in enumerate(names):
        out += (['/\\'] if k else []) + [n]
    return out


def conj_term(names):
    if len(names) == 1:
        return [names[0]]
    rest = conj_term(names[1:])
    return ['conj', names[0]] + (rest if len(names) == 2 else ['('] + rest + [')'])


def module_of(name, f):
    """<M> for a name MKF.<f>.<M>.<N>, else None."""
    p = name.split('.')
    return p[2] if len(p) == 4 and p[0] == 'MKF' and p[1] == f else None


# ---- the inventory ---------------------------------------------------------------------------------------------------

def joined(*parts):
    return '; '.join(x for x in parts if x)


def outside_v(root, base, folders, row):
    """The row: no .v file under base lies outside one of the given folders. Returns base's files (or None)."""
    files, _, errs = walk(at(root, base))
    out = [base + '/' + x for x in (files or [])
           if x.endswith('.v') and ('/' not in x or x.split('/')[0] not in folders)]
    if files is None:
        add(row, True, '%s is absent' % base)
    else:
        add(row, not out and not errs, '%d .v files, none outside' % sum(1 for x in files if x.endswith('.v'))
            if not out and not errs else joined('outside: %s' % few(out) if out else '',
                                                'not read: %s' % few(errs) if errs else ''))
    return files


def inventory(root, obj):
    # discovery
    found, _, errs = walk(root, prune=SKIP)
    gated, mirrors, unknown, judge_named = [], [], [], []
    for rel in (x for x in found if x.split('/')[-1] == 'gate.json'):
        p = rel.split('/')
        if len(p) == 4 and p[:2] == ['kernel', 'coq'] and FOLDER.fullmatch(p[2]) and p[2] != 'gate':
            # a folder whose anchor variable would be the CI judge's (MK_ANCHOR_CI) is refused, not gated
            (judge_named if 'MK_ANCHOR_' + p[2].upper() == 'MK_ANCHOR_CI' else gated).append(p[2])
        elif len(p) == 5 and p[:3] == ['verdandi', 'mathkernel', 'F32'] and FOLDER.fullmatch(p[3]) and p[3] != 'gate':
            mirrors.append(p[3])
        else:
            unknown.append(rel)
    gated.sort()
    mirrors.sort()
    add('discovery: every gate.json is in a gated folder or a mirror', not unknown and not errs,
        '%d gated, %d mirrors' % (len(gated), len(mirrors)) if not unknown and not errs else
        joined('not a gated folder or a mirror: %s' % few(unknown) if unknown else '',
               'not read: %s' % few(errs) if errs else ''))
    add('discovery: at least one gated folder', gated,
        '%d: %s' % (len(gated), ' '.join(gated)) if gated else 'no kernel/coq/<folder>/gate.json')
    add('discovery: no gated folder takes the variable MK_ANCHOR_CI', not judge_named,
        'none (MK_ANCHOR_CI holds the CI judge digest)' if not judge_named else
        '%s: its anchor variable would be MK_ANCHOR_CI, which holds the CI judge digest; rename the folder'
        % few('kernel/coq/%s/gate.json' % f for f in sorted(judge_named)))
    kfiles = outside_v(root, KERNEL, gated, 'discovery: no .v file under kernel/coq outside a gated folder')
    mfiles = outside_v(root, MIRROR_ROOT, mirrors,
                       'discovery: no .v file under verdandi/mathkernel/F32 outside a mirror')

    # the gate's own folder
    gfiles, gdirs, gerr = walk(at(root, KERNEL + '/gate'))
    if gfiles is None:
        add('gate dir: kernel/coq/gate holds exactly its own files', False, 'kernel/coq/gate is absent')
    else:
        seen = sorted(gfiles + [d + '/' for d in gdirs])
        obj['gate_dir_files'] = seen
        extra = sorted(set(seen) - set(GATE_DIR_FILES))
        missing = sorted(set(GATE_DIR_FILES) - set(gfiles))
        add('gate dir: kernel/coq/gate holds exactly its own files', not extra and not missing and not gerr,
            ' '.join(GATE_DIR_FILES) if not extra and not missing and not gerr else
            joined('not its own: %s' % few(extra) if extra else '', 'absent: %s' % few(missing) if missing else '',
                   'not read: %s' % few(gerr) if gerr else ''))

    # THEOREMS.md, read in the Markdown subset (markdown())
    lines, subset, headings = markdown(raw(at(root, 'THEOREMS.md')), 'THEOREMS.md')
    proved, known = {}, set()
    if lines is None:
        add('THEOREMS.md: one proved row per gated folder', False, subset[0])
        add('THEOREMS.md: every successor row names known statements', False, subset[0])
        # (the rows "no block quote, no list item holding a bar" and "written in the Markdown subset this reader reads"
        # are not printed then: the two rows above fail)
    else:
        proved, probs, known = proved_table(lines)
        probs += ['a row for %s, which is not a gated folder' % f for f in sorted(set(proved) - set(gated))]
        probs += ['no usable row for %s' % f for f in gated if f not in proved]
        add('THEOREMS.md: one proved row per gated folder', not probs,
            '%d rows' % len(proved) if not probs else few(probs, 4))
        probs, n, present = successor_table(lines, known)
        probs += headings       # every heading is read here, so one outside the subset fails this row
        add('THEOREMS.md: every successor row names known statements', not probs,
            ('%d rows, each naming statements of the proved table; every heading read' % n if present
             else 'no successor table') if not probs else few(probs, 4))
        boxed = container_lines(lines)
        add('THEOREMS.md: no block quote, no list item holding a bar', not boxed,
            'none (this reader does not open a block quote or a list item, where GitHub shows tables and headings)'
            if not boxed else 'line %s: a block quote, or a list item holding "|", which this reader does not read'
            % few(str(k) for k in boxed))
        add('THEOREMS.md: written in the Markdown subset this reader reads', not subset,
            '%d lines, every one in the subset (this script\'s header names its rules)' % len(lines)
            if not subset else few(subset, 3))

    # the statement files of the gated folders
    probs, nnames, nfiles, shared, nsent = statement_names(root, statement_files(root, gated))
    add('statement files: each name defined in one of them', not probs,
        '%d sentences read, %d names in %d statement files; in two, as allowed: %s'
        % (nsent, nnames, nfiles, ', '.join(shared) or 'none') if not probs else few(probs, 4))

    # ANCHORS.md
    alines, aprobs, _ = markdown(raw(at(root, KERNEL + '/ANCHORS.md')), 'ANCHORS.md')
    anchors = {}
    if alines is None:
        add('ANCHORS.md: one row per gated folder with its variable', False, 'kernel/coq/' + aprobs[0])
    else:
        anchors, probs = anchors_table(alines)
        probs = aprobs + probs
        for f in sorted(anchors):
            var, _, rec = anchors[f]
            if f not in gated:
                probs.append('a row for %s, which is not a gated folder' % f)
                continue
            if var != 'MK_ANCHOR_' + f.upper():
                probs.append('%s: variable %r, not MK_ANCHOR_%s' % (f, var, f.upper()))
            if not rec:
                probs.append('%s: no record' % f)
        probs += ['no row for %s' % f for f in gated if f not in anchors]
        add('ANCHORS.md: one row per gated folder with its variable', not probs,
            '%d rows' % len(anchors) if not probs else few(probs, 4))

    # each gated folder (every gated folder's gate.json read first: a folder's gate also requires its deps' files)
    cfgs = {g: load_json(raw(at(root, KERNEL + '/' + g + '/gate.json')))[0] for g in gated}
    for f in gated:
        fdir = KERNEL + '/' + f
        entry = {'folder': f, 'files': None, 'plants': None, 'frozen4_sha256': None, 'identity_names': None}
        obj['gated'].append(entry)
        fb = raw(at(root, fdir + '/FROZEN4.txt'))
        if fb is None:
            add('%s: FROZEN4.txt present and readable' % f, False, '%s/FROZEN4.txt is absent' % fdir)
            add('%s: FROZEN4.txt entries hold in the tree' % f, False, 'no FROZEN4.txt')
        else:
            entry['frozen4_sha256'] = sha(fb)
            entries, unread, twice = read_list(fb)
            add('%s: FROZEN4.txt present and readable' % f, entries and not unread and not twice,
                '%d entries' % len(entries) if entries and not unread and not twice else
                joined('no entry' if not entries else '', 'not readable: %s' % few(unread) if unread else '',
                       'listed twice: %s' % few(twice) if twice else ''))
            off = listed_hold(root, KERNEL, entries)
            need, nprob = needed(f, cfgs)
            unlisted = sorted(need - set(p for _, p in entries)) if need is not None else []
            ok = entries and not off and need is not None and not unlisted
            add('%s: FROZEN4.txt entries hold in the tree' % f, ok,
                '%d files as listed; the %d its gate requires are all listed' % (len(entries), len(need)) if ok else
                joined('no entry' if not entries else '',
                       '%d of %d differ: %s' % (len(off), len(entries), few(off)) if off else '',
                       'what its gate requires is not known: %s' % nprob if nprob else '',
                       'its gate requires, not listed: %s' % few(unlisted) if unlisted else ''))

        cfg, cprob = load_json(raw(at(root, fdir + '/gate.json')))
        files = plants = None
        probs = [] if cfg is not None else [cprob]
        if cfg is not None:
            fl = cfg.get('files')
            if isinstance(fl, list) and fl and all(isinstance(x, str) and VNAME.fullmatch(x) for x in fl):
                files = list(fl)
            else:
                probs.append('"files" is not a list of plain .v names')
            pl = cfg.get('plants', {})
            if isinstance(pl, dict) and all(
                    PLANT_NAME.fullmatch(k) and isinstance(v, dict) and isinstance(v.get('replace'), dict)
                    and v['replace'] and all(isinstance(d, str) and isinstance(s, str) for d, s in v['replace'].items())
                    for k, v in pl.items()):
                plants = pl
            else:
                probs.append('"plants" is not a map of plain names to entries each with a "replace" map')
            name = cfg.get('name')
            if not (isinstance(name, str) and GATE_NAME.fullmatch(name)):
                probs.append('"name" is not a plain name')
            if cfg.get('identity') != 'Identity':
                probs.append('"identity" is not "Identity"')
            elif files is not None and 'Identity.v' not in files:
                probs.append('Identity.v is not one of "files"')
            tier = cfg.get('tier')
            if not (isinstance(tier, str) and 'expected-pa-%s.txt' % tier in GATE_DIR_FILES):
                probs.append('"tier" names no expected-pa file of kernel/coq/gate')
            deps = cfg.get('deps', [])
            if not (isinstance(deps, list) and all(isinstance(d, str) for d in deps)):
                probs.append('"deps" is not a list of names')
            else:
                bad = [d for d in deps if d not in gated or d == f]
                if bad:
                    probs.append('"deps" names %s, not another gated folder' % few(bad))
                if len(set(deps)) != len(deps):
                    probs.append('"deps" names a folder twice')
        add('%s: gate.json parses' % f, not probs,
            'name %s, %d files, %d plants' % (cfg.get('name'), len(files), len(plants)) if not probs else few(probs, 4))

        top = [x for x in listdir(at(root, fdir)) if x.endswith('.v')]
        if files is None:
            add('%s: gate.json files are its top-level .v files' % f, False, 'gate.json gives no usable "files"')
        else:
            count = collections.Counter(files)
            twice = sorted(x for x, k in count.items() if k > 1)
            unlisted = sorted(set(top) - set(files))
            absent = sorted(set(files) - set(top))
            notfile = sorted(x for x in top if not os.path.isfile(at(root, fdir + '/' + x)))
            bad = [x for x in ('listed twice: %s' % few(twice) if twice else '',
                               'not listed: %s' % few(unlisted) if unlisted else '',
                               'listed, absent: %s' % few(absent) if absent else '',
                               'not a file: %s' % few(notfile) if notfile else '') if x]
            entry['files'] = files
            add('%s: gate.json files are its top-level .v files' % f, not bad,
                '%d files' % len(files) if not bad else '; '.join(bad))

        have = sorted('plants/' + x for x in listdir(at(root, fdir + '/plants')) if x.endswith('.v'))
        if plants is None or files is None:
            add('%s: plants/*.v are the plant files it names' % f, False,
                'gate.json gives no usable "plants" or "files"')
        else:
            named, bad = set(), []
            for k in sorted(plants):
                for dst, src in sorted(plants[k]['replace'].items()):
                    if PLANT_FILE.fullmatch(src):
                        named.add(src)
                    else:
                        bad.append('%s puts in %r, not plants/<name>.v' % (k, src))
                    if dst not in files:
                        bad.append('%s replaces %r, not a listed file' % (k, dst))
            entry['plants'] = sorted(set(s for v in plants.values() for s in v['replace'].values()))
            unnamed = sorted(set(have) - named)
            absent = sorted(named - set(have))
            notfile = sorted(x for x in have if not os.path.isfile(at(root, fdir + '/' + x)))
            bad += [x for x in ('named by no plant: %s' % few(unnamed) if unnamed else '',
                                'named, absent: %s' % few(absent) if absent else '',
                                'not a file: %s' % few(notfile) if notfile else '') if x]
            add('%s: plants/*.v are the plant files it names' % f, not bad,
                '%d plant files, %d plants' % (len(named), len(plants)) if not bad else few(bad, 4))

        deep = [KERNEL + '/' + x for x in (kfiles or []) if x.startswith(f + '/') and x.endswith('.v')
                and x.count('/') >= 2 and not (x.count('/') == 2 and x.startswith(f + '/plants/'))]
        add('%s: no .v file in another subfolder' % f, not deep, 'none' if not deep else few(deep))

        info, iprob = identity(raw(at(root, fdir + '/Identity.v')))
        row = proved.get(f)
        probs = ['Identity.v: %s' % iprob] if info is None else []
        if row is None:
            probs.append('no usable THEOREMS.md row for %s' % f)
        if info is not None:
            S, T = info['statements'], info['theorems']
            entry['identity_names'] = {'statements': S, 'theorems': T}
            if not S or not T:
                probs.append('the definition names %d statements and %d theorems' % (len(S), len(T)))
            stray = [x for x in S + T if module_of(x, f) is None
                     or not os.path.isfile(at(root, fdir + '/' + module_of(x, f) + '.v'))]
            if stray:
                probs.append('not a name of a module of %s: %s' % (f, few(stray, 3)))
            if row is not None:
                if S != row['statements']:
                    probs.append('statements: Identity.v %s; THEOREMS.md %s' % (few(S, 4), few(row['statements'], 4)))
                if T != row['theorems']:
                    probs.append('theorems: Identity.v %s; THEOREMS.md %s' % (few(T, 4), few(row['theorems'], 4)))
                mods = []
                for x in S:
                    p = '%s/%s.v' % (f, module_of(x, f))
                    if p not in mods:
                        mods.append(p)
                if sorted(row['files']) != sorted(mods):
                    probs.append('statement file: THEOREMS.md %s; the statements are in %s'
                                 % (few(row['files']), few(mods)))
        add('%s: Identity.v names are its THEOREMS.md row' % f, not probs,
            '%d statements, %d theorems' % (len(info['statements']), len(info['theorems'])) if not probs
            else few(probs, 3))

        probs = ['Identity.v: %s' % iprob] if info is None else []
        if info is not None:
            S, T, sents = info['statements'], info['theorems'], info['sentences']
            if len(sents) != 3:
                probs.append('%d sentences, not 3' % len(sents))
            else:
                m = REQUIRE.fullmatch(sents[0])
                want = set(module_of(x, f) for x in S + T)
                if not m or m.group(1) != f:
                    probs.append('the first sentence is not From MKF.%s Require <modules>' % f)
                elif len(set(m.group(2).split())) != len(m.group(2).split()) or set(m.group(2).split()) != want:
                    probs.append('it requires %s; the names are of %s'
                                 % (' '.join(m.group(2).split()), ' '.join(sorted(str(x) for x in want))))
                if sents[1] != info['definition']:
                    probs.append('the second sentence is not the definition of %s' % info['name'])
                if sents[2] != 'Print Assumptions ' + info['name']:
                    probs.append('the third sentence is not Print Assumptions %s' % info['name'])
            if not S or len(S) != len(T):
                probs.append('%d statements and %d theorems' % (len(S), len(T)))
            else:
                if TOKEN.findall(info['type']) != conj_type(S):
                    probs.append('the type is not its statements joined by /\\: %s' % info['type'][:120])
                if TOKEN.findall(info['term']) != conj_term(T):
                    probs.append('the term is not its theorems nested in conj: %s' % info['term'][:120])
        add('%s: Identity.v is the plain conjunction of that row' % f, not probs,
            'From MKF.%s Require; %s : %d statements := %d theorems; Print Assumptions'
            % (f, info['name'], len(info['statements']), len(info['theorems'])) if not probs else few(probs, 3))

        a = anchors.get(f)
        if a is None:
            add('%s: ANCHORS.md value is sha256 of FROZEN4.txt' % f, False,
                'no row for %s in kernel/coq/ANCHORS.md' % f)
        elif fb is None:
            add('%s: ANCHORS.md value is sha256 of FROZEN4.txt' % f, False, 'no FROZEN4.txt')
        else:
            add('%s: ANCHORS.md value is sha256 of FROZEN4.txt' % f, a[1] == sha(fb),
                '%s %s' % (a[0], sha(fb)[:16]) if a[1] == sha(fb) else
                'ANCHORS.md %s; FROZEN4.txt %s' % (a[1][:64], sha(fb)))

    # each mirror
    for m in mirrors:
        mdir = MIRROR_ROOT + '/' + m
        mb = raw(at(root, mdir + '/FROZEN4.txt'))
        obj['mirrors'].append({'folder': m, 'frozen4_sha256': None if mb is None else sha(mb)})
        kb = raw(at(root, KERNEL + '/' + m + '/FROZEN4.txt'))
        name = "mirror %s: FROZEN4.txt equals its kernel twin's" % m
        if m not in gated:
            add(name, False, 'no gated folder kernel/coq/%s' % m)
        elif mb is None or kb is None:
            add(name, False, '%s/FROZEN4.txt is absent' % (mdir if mb is None else KERNEL + '/' + m))
        else:
            add(name, mb == kb, sha(mb)[:16] if mb == kb else 'mirror %s; twin %s' % (sha(mb)[:16], sha(kb)[:16]))
        listed = set()
        if mb is None:
            add('mirror %s: every listed file holds its sha256' % m, False, 'no FROZEN4.txt')
        else:
            entries, unread, twice = read_list(mb)
            listed = set(p for _, p in entries)
            off = listed_hold(root, MIRROR_ROOT, entries)
            bad = [x for x in ('no entry' if not entries else '', 'not readable: %s' % few(unread) if unread else '',
                               'listed twice: %s' % few(twice) if twice else '',
                               '%d of %d differ: %s' % (len(off), len(entries), few(off)) if off else '') if x]
            add('mirror %s: every listed file holds its sha256' % m, not bad,
                '%d files as listed' % len(entries) if not bad else '; '.join(bad))
        vs = [x for x in (mfiles or []) if x.startswith(m + '/') and x.endswith('.v')]
        unl = [MIRROR_ROOT + '/' + x for x in vs if x not in listed]
        add('mirror %s: every .v file is listed' % m, mb is not None and not unl,
            ('%d .v files' % len(vs) if not unl else 'not listed: %s' % few(unl)) if mb is not None
            else 'no FROZEN4.txt')
    if not mirrors:
        add("mirrors: gate4.py and strict_read.py equal the kernel's", True, 'no mirror')
    else:
        diff = []
        for g in MIRROR_GATE_FILES:
            mine, theirs = raw(at(root, MIRROR_ROOT + '/gate/' + g)), raw(at(root, KERNEL + '/gate/' + g))
            if mine is None or theirs is None or mine != theirs:
                diff.append('%s/gate/%s%s' % (MIRROR_ROOT, g, ' (absent)' if mine is None
                                              else ' (the kernel\'s is absent)' if theirs is None else ''))
        add("mirrors: gate4.py and strict_read.py equal the kernel's", not diff,
            'byte for byte' if not diff else 'differ: %s' % few(diff))
    return gated


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')


def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def plain(path):
    """A path with a Windows long-path or device prefix (\\\\?\\, \\\\?\\UNC\\, \\\\.\\) taken off, and on POSIX a
    leading "//" read as "/" (tools/ci/read_audit.py's rule, copied)."""
    if path.startswith('\\\\?\\UNC\\'):
        return '\\\\' + path[8:]
    if path.startswith('\\\\?\\') or path.startswith('\\\\.\\'):
        return path[4:]
    if os.name != 'nt' and path.startswith('//') and not path.startswith('///'):
        return path[1:]
    return path


def main(argv):
    ap = argparse.ArgumentParser(prog='inventory.py', allow_abbrev=False, add_help=False,
                                 description='Find and hold what CI must gate (see the header of this file).')
    ap.add_argument('--root', required=True, help='the tree\'s top folder')
    ap.add_argument('--json', dest='json_out', help='write the inventory as JSON here')
    ap.add_argument('--matrix-out', help='write the gate matrix here, only when every row held')
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        ap.error('--root is not a folder')
    outs = [os.path.abspath(p) for p in (a.json_out, a.matrix_out) if p]
    for p in outs:
        if os.path.isdir(p) or not os.path.isdir(os.path.dirname(p)):
            ap.error('an output path must name a file in an existing folder')
    # one file on a case-insensitive file system too, and however it is spelled: the path resolved first (links,
    # short names; a volume GUID path becomes its drive's form, a long-path prefix given is kept; on POSIX a leading
    # "//" folds), then a long-path prefix taken off, then its case folded
    if len(set(os.path.normcase(plain(os.path.realpath(p))) for p in outs)) != len(outs):
        ap.error('--json and --matrix-out name the same file')
    # two names of one file (a hard link), which realpath does not merge; and an existing output with another name,
    # whose other name would be written too
    try:
        same = len(outs) == 2 and all(os.path.exists(p) for p in outs) and os.path.samefile(*outs)
    except OSError:
        same = False
    if same:
        ap.error('--json and --matrix-out name the same file')
    for p in outs:
        try:
            nlink = os.stat(p).st_nlink
        except OSError:
            nlink = 0
        if nlink > 1:
            ap.error('an output path names a file that has another name (a hard link); write a new file')
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', newline='\n')
    except (AttributeError, ValueError):
        pass

    obj = {'gated': [], 'mirrors': [], 'gate_dir_files': []}
    gated = []
    try:
        gated = inventory(root, obj)
    except Exception as e:      # a row, never a crash with exit 0
        add('internal: the inventory ran to its end', False,
            '%s: %s' % (type(e).__name__, str(e).replace(root, '<root>')))
    digest = sha(canonical(obj))
    held = bool(ROWS) and all(r['ok'] for r in ROWS)
    try:
        if a.json_out:
            n, k = len(ROWS), sum(1 for r in ROWS if not r['ok'])
            out = dict(obj, schema=SCHEMA, digest=digest, held=held, rows=ROWS,
                       verdict='INVENTORY HELD: %d of %d rows' % (n, n) if held else
                       'INVENTORY FAILED: %d of %d rows failed' % (k, n))
            write(a.json_out, (json.dumps(out, sort_keys=True, indent=1) + '\n').encode('utf-8'))
        if a.matrix_out:
            if held:
                matrix = {'include': [{'folder': f, 'anchor': 'MK_ANCHOR_' + f.upper()} for f in gated]}
                write(a.matrix_out, (json.dumps(matrix, separators=(',', ':')) + '\n').encode('utf-8'))
            elif os.path.lexists(a.matrix_out):
                os.remove(a.matrix_out)
    except OSError as e:
        add('output: the files asked for are written', False, '%s: %s' % (type(e).__name__, e.strerror))
        held = False
        for p in (a.json_out, a.matrix_out):
            try:
                if p and os.path.lexists(p):
                    os.remove(p)
            except OSError:
                pass
    n, k = len(ROWS), sum(1 for r in ROWS if not r['ok'])
    print('INVENTORY DIGEST %s' % digest)
    print('INVENTORY HELD: %d of %d rows' % (n, n) if held else 'INVENTORY FAILED: %d of %d rows failed' % (k, n))
    return 0 if held else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
