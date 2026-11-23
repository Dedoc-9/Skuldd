# SPDX-License-Identifier: AGPL-3.0-only
# The feature-absence row, version 4 (verdict FEATURE ROW 4; 2026-11-18, scratch; written by the assistant; changed
# after review rounds 1 to 6).
# Standard library only; runs on CPython 3.12 and later.
#
# What it checks. Each Coq source is read as bytes and decoded as UTF-8. A character outside printable ASCII, tab,
# line feed, carriage return and form feed, anywhere in the file, in code, comments and strings alike, is refused ("a
# character outside printable ASCII"): the patterns below read ASCII, and Coq reads more characters as letters than
# they do (a module named with a Greek letter, say), so the row refuses what it cannot read, and does not rest that
# rule on its own blanking of comments and strings. The text is then lexed as version 3 lexes it (feature_row3.py,
# kept unchanged beside this file): comments, nested, and string literals are blanked as Coq's lexer reads them, and
# the patterns are matched across lines. A source passes when none of the refused constructs occurs.
# The refused constructs are version 3's, copied here unchanged, and fifteen more. Six are ways to assume or to enter
# Program mode that version 3 did not refuse: the Conjectures command (version 3 refused only the singular), a Context
# command (outside a section it declares its binders as assumptions), Declare Instance (an instance with no body),
# Admit Obligations, the commands of Program's obligations (Obligation, Next Obligation, Final Obligation, Solve
# Obligations, Solve All Obligations, Obligation Tactic) and a program attribute inside #[...] (version 3 refused
# Program mode only as the word Program). Six refuse further spellings of five triggers that
# kernel/hardening/features/trigger_census.py names, and of private inductive types, which it does not name: a
# universes attribute (polymorphic, cumulative, template or any other value) anywhere in an attribute list, and the
# prefix Monomorphic (universe polymorphism; version 3 refused a universes attribute only at a list's start, and
# Polymorphic, Cumulative and NonCumulative as words); a projections attribute (primitive projections; the option Set
# Primitive Projections is refused by version 3's word Primitive); a using attribute and the option Default Proof
# Using (abstract or Proof using); an inline universe binder or instance "@{" (universe declarations); every use of
# the word Module in code but a plain module command, and Include (module types and functors): the row accepts only
# "Module <name>.", "Module Import <name>." and "Module Export <name>.", the name written in ASCII
# ([A-Za-z_][A-Za-z0-9_']*), so Module Type, Declare Module, a functor's parameters, a functor applied, a module
# ascribed (":" or "<:"), import categories after Import or Export and a name it cannot read are all refused (version
# 3 refused Module Type, Declare Module, Functor and a functor's parameters directly after an ASCII name); a private
# attribute and the prefix Private (private inductive types). The program and bypass_check attributes were refused
# anywhere already. One refuses the commands that read a source file by name (Load), name a file for plugins (Extra
# Dependency), change the load path (LoadPath: Add LoadPath, Add Rec LoadPath) or the working folder (Cd), load or
# write a saved state (Restore State, Write State), write files (Redirect; Extraction and Extract: every Extraction
# command and option, Extract Constant and Extract Inductive among them) or load a plugin by name (ML: Declare ML
# Module, which version 3 also refuses, Add ML Path and Add Rec ML Path), by their words, wherever they stand. Require
# (and From ... Require) stays allowed: it loads compiled libraries, which the gate-log check compares one by one, and
# the plugins they declare, which are the image's. One fails closed on From: a From in code must be followed by a
# dotted ASCII name and then Require; any other From is refused ("From not followed by Require"). The last is the
# character rule above. The census's other triggers: version 3 refuses every spelling the census itself counts
# (native_compute, Primitive and Register, the primitive types, SProp, Universe(s) and Constraint, Parameter Inline by
# the word Parameter, Declare ML Module, rewrite rules, Section, CoInductive, a let in an inductive declaration, Axiom,
# Parameter and Conjecture); both rows allow by design vm_compute (reported: coqchk re-checks it without the VM),
# plain Inductive, Variant, Record, Structure and Class declarations (counted on the reported line, Class by version 4
# only) and the names of the library's axioms (propext, proof_irrelevance and the others the census counts), whose use
# Print Assumptions shows in the gate's own row. For the module commands and the file, load-path and plugin commands the
# row names what it accepts (a plain module command; From only before a name and Require), or refuses the words wherever
# they stand (a file command other than Require that no listed word names would pass: the list is of words, not of every
# command). For the other triggers, that these are every spelling Coq 8.20 accepts is ARGUED from the reference manual
# as remembered, not checked here. A spelling Coq 8.20 may not accept is refused all the same (the universes values
# other than polymorphic and cumulative, using and private as attributes: ARGUED likewise): a refusal costs nothing on a
# tree that does not use it.
#
# Rows. "input": the root is a directory; with --list, the list is read, is ASCII, every line, once a final carriage
# return is taken off, holds only printable ASCII and tab (a comment's too, so no carriage return, form feed or other
# separator joins a comment and an entry into one line that version 3 reads as two), and every line is empty, a comment
# ("#") or "<sha256>  <path>" with a plain relative path (no empty, "." or ".." part, no backslash, colon or leading
# "/"), no path is listed twice, and at least one .v file is left to scan once the plants are left out (a path holding
# "/plants/", as version 3 decides); without --list, no file is given twice. Then one row per .v file, sorted by path:
# the file is read and is UTF-8, with --list its sha256 equals the listed one, and no refused construct occurs. Each
# occurrence is printed on its own REFUSED line under its file's row; the allowed constructs version 3 reports, and
# Class declarations, are counted on one line before the verdict.
#
# What a pass shows: the sources are printable ASCII (tab, line feed, carriage return and form feed allowed) throughout;
# outside comments and strings, their text holds none of these words or forms, and every module command in it is a
# plain one; with --list the bytes scanned are the bytes the list names. What it does not show: that the list is the
# anchored one (the gate checks that); a construct that a tactic, a notation or a library builds without one of these
# words; a spelling of a trigger that this header does not name; the code of libraries, which is the image's; that
# Coq accepts each refused spelling (no Coq runs here). Words are matched at word boundaries, and a prime is not a
# word character, so an identifier such as Context' is refused although Coq reads it as one name; the words
# Conjectures, Context, Admit, Obligation(s), Monomorphic, Private, Include, Load, LoadPath, Cd, Redirect, Extraction,
# Extract and ML, Module outside a plain module command (Module' among them) and From outside "From <name> Require"
# (an identifier From among them), are refused anywhere in code, as identifiers too, since the scan does not parse
# where a command starts; and a letter outside ASCII is refused in a comment or a string too. Each refuses honest
# text; none lets a refused construct pass. Version 4 scans every file version 3 scans, or fails its input row (a list
# whose lines are ended by lone CR or by another separator that version 3's splitlines reads, or one of whose lines,
# a comment's too, holds such a separator, which version 4 refuses), and refuses every construct version 3 refuses,
# so it fails wherever version 3 fails (argued from the code; measured on version 3's plants).
#
# Usage (the same as version 3; paths in a list or on the command line are relative to <root>):
#   python -B feature_row4.py <root> <file.v> ...          scan the files
#   python -B feature_row4.py <root> --list <FROZEN4.txt>   scan every .v of the list outside plants/
# Exit 0 only if every row holds; 1 if a row fails; 2 on a usage error.
import hashlib, os, re, sys
sys.dont_write_bytecode = True
try: sys.stdout.reconfigure(newline='\n')   # the same output bytes on Windows as on Linux
except (AttributeError, ValueError): pass

NAME = 'FEATURE ROW 4'
USAGE = 'usage: feature_row4.py <root> <file.v> ... | <root> --list <FROZEN4.txt>'

REFUSED = [
    # version 2 (his ruling Q4)
    ('recursive definition', r'\b(Fixpoint|CoFixpoint|Function|Equations|Scheme|Program)\b'),
    ('recursive term or tactic', r'\b(fix|cofix)\b'),
    ('checking flag', r'\bUnset\s+(Guard|Positivity|Universe)\s+Checking\b'),
    ('checking flag', r'\bbypass_check\b'),
    ('checking flag', r'\bSet\s+Definitional\s+UIP\b'),
    ('checking flag', r'\b(Set|Unset)\s+Typing\s+Flags\b'),
    # version 3 (critical-bugs triggers the tier does not use)
    ('native compiler', r'\bnative_compute\b|\bnative_cast_no_check\b|<<:'),
    ('primitive declaration', r'\b(Primitive|Register)\b'),
    ('primitive type', r'\b(PrimFloat|PrimInt63|Uint63|Sint63|Int63|Float64|PArray|PrimArray|PrimString)\b'),
    ('SProp', r'\bSProp\b'),
    ('universe polymorphism', r'\b(Polymorphic|Cumulative|NonCumulative)\b|#\[\s*universes'),
    ('universe declaration', r'\b(Universes?|Constraint)\b'),
    ('module type or functor', r'\b(Module\s+Type|Declare\s+Module|Functor)\b|\bModule\s+[A-Za-z_]\w*\s*\('),
    ('plugin', r'\bDeclare\s+ML\s+Module\b'),
    ('rewrite rule', r'\bRewrite\s+Rules?\b|\bSymbols?\b'),
    ('section', r'\bSection\b'),
    ('coinductive type', r'\bCoInductive\b'),
    ('assumption', r'\b(Axioms?|Parameters?|Conjecture|Hypothesis|Hypotheses|Variables?|Admitted|admit)\b'),
    ('abstract or Proof using', r'\babstract\b|\bProof\s+using\b'),
    ('let-in in an inductive declaration', r'(?s)\b(Inductive|Record|Variant|Structure|Class)\b(?:(?!\.\s).)*?\blet\b'),
    # version 4 (assumptions and Program mode that version 3 did not refuse)
    ('Conjectures assumption', r'\bConjectures\b'),
    ('Context command', r'\bContext\b'),
    ('Declare Instance', r'\bDeclare\s+Instance\b'),
    ('Admit Obligations', r'\bAdmit\b'),
    ('Program obligation command', r'\bObligations?\b'),
    ('program attribute', r'#\[[^\]]*\bprogram\b'),
    # version 4, after review: the further spellings, as an attribute, a prefix, an option or an inline binder, of
    # four triggers trigger_census.py names and of private inductive types, refused anywhere in an attribute list
    # (first or not, spaced, across lines, in a second list); bypass_check and program were refused anywhere already
    # (versions 2 and 4)
    ('universe polymorphism', r'\bMonomorphic\b|#\[[^\]]*\buniverses\b'),
    ('primitive projections', r'#\[[^\]]*\bprojections\b'),
    ('abstract or Proof using', r'#\[[^\]]*\busing\b|\bDefault\s+Proof\s+Using\b'),
    ('private inductive type', r'\bPrivate\b|#\[[^\]]*\bprivate\b'),
    ('universe declaration', r'@\{'),
    # version 4, after the fourth and fifth reviews: the census's module types and functors, failing closed. Every
    # use of the word Module in code is refused but a plain "Module <name>.", "Module Import <name>." or "Module
    # Export <name>.", the name in ASCII (explicit classes, not \w); and Include (Include Type among them)
    ('module type or functor',
     r"\bInclude\b|\bModule\b(?!\s+(?:(?:Import|Export)\s+)?[A-Za-z_][A-Za-z0-9_']*\s*\.(?!\S))"),
    # version 4, after the fifth and sixth reviews: the commands that read a source file by name (Load), name a file
    # for plugins (Extra Dependency), change the load path (Add LoadPath, Add Rec LoadPath) or the working folder (Cd),
    # load or write a saved state (Restore State, Write State), write files (Redirect, every Extraction command) or
    # load a plugin by name (Declare ML Module, Add ML Path, Add Rec ML Path): their words, wherever they stand.
    # Require stays allowed: it loads compiled libraries, which the gate-log check compares one by one, and the
    # plugins they declare, which are the image's
    ('file, load path or plugin command', r'\b(?:Load|LoadPath|Cd|Redirect|Extraction|Extract|ML)\b'
                                          r'|\bExtra\s+Dependency\b|\b(?:Restore|Write)\s+State\b'),
    # version 4, after the sixth review: From, failing closed: a From in code must be followed by a dotted ASCII
    # name and then Require ("From Coq Require Import Reals."); any other From is refused
    ('From not followed by Require',
     r"\bFrom\b(?!\s+[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*\s+Require\b)"),
]
# version 4, after the fifth review: a character outside printable ASCII, tab, line feed, carriage return and form feed,
# anywhere in a file (code, comments and strings alike), matched on the text before any blanking
OUTSIDE_ASCII = ('a character outside printable ASCII', r'[^\t\n\r\f -~]')
REPORTED = [
    ('vm_compute (allowed; coqchk re-checks it without the VM)', r'\bvm_compute\b|\bvm_cast_no_check\b|<:'),
    ('inductive or record (allowed: plain declarations)', r'\b(Inductive|Variant|Record|Structure)\b'),
    ('other Set or Unset', r'(?m)^\s*(#\[[^\]]*\]\s*)?(Local\s+|Global\s+|Export\s+)?(Set|Unset)\s+[A-Z]'),
    # version 4, after the fifth review: Class declarations, which version 3 counts under no entry
    ('class (allowed: plain declarations)', r'\bClass\b'),
]

def strip(text):
    """Comments (nested) and string literals replaced by spaces, newlines kept. As in Coq's lexer, a string inside a
    comment is a string ("" is an escaped quote) and a "(*" or "*)" inside it does not count."""
    out, i, depth, n = [], 0, 0, len(text)
    def blank(s): return ''.join(c if c == '\n' else ' ' for c in s)
    while i < n:
        if text[i] == '"':
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"': j += 2; continue
                    break
                j += 1
            out.append(blank(text[i:j + 1])); i = j + 1; continue
        if text.startswith('(*', i): depth += 1; out.append('  '); i += 2; continue
        if depth and text.startswith('*)', i): depth -= 1; out.append('  '); i += 2; continue
        c = text[i]; out.append(c if (depth == 0 or c == '\n') else ' '); i += 1
    return ''.join(out)

def scan_text(t):
    """The refused occurrences (line, class, matched text) and the reported counts of a stripped text."""
    refused, reported = [], {}
    for what, pat in REFUSED:
        for m in re.finditer(pat, t):
            refused.append((t.count('\n', 0, m.start()) + 1, what, ' '.join(m.group(0).split())[:60]))
    for what, pat in REPORTED:
        k = len(re.findall(pat, t))
        if k: reported[what] = reported.get(what, 0) + k
    refused.sort()
    return refused, reported

def outside_ascii(text):
    """The refused occurrences (line, class, the character as U+XXXX) of OUTSIDE_ASCII in a text, comments and strings
    included."""
    what, pat = OUTSIDE_ASCII
    return [(text.count('\n', 0, m.start()) + 1, what, 'U+%04X' % ord(m.group(0))) for m in re.finditer(pat, text)]

def show(s):
    """Printable on any console: characters outside ASCII are escaped."""
    return s.encode('ascii', 'backslashreplace').decode('ascii')

def read_list(path):
    """Problems, entries [(path, sha256)] of the .v files outside plants/, the count left out as plants, and the
    list's own sha256 (None if unreadable)."""
    try:
        with open(path, 'rb') as f: data = f.read()
    except OSError as e:
        return ['the list cannot be read (%s)' % (e.strerror or type(e).__name__)], [], 0, None
    digest = hashlib.sha256(data).hexdigest()
    try:
        text = data.decode('ascii')
    except UnicodeDecodeError as e:
        return ['the list is not ASCII (byte %d)' % e.start], [], 0, digest
    problems, entries, seen, nplants = [], [], set(), 0
    for k, line in enumerate(text.split('\n'), 1):
        if line.endswith('\r'): line = line[:-1]
        # after the sixth review: a line, a comment's too, holds only printable ASCII and tab, so no carriage return,
        # form feed or other separator can join a comment and an entry into one line that version 3 reads as two
        odd = re.search(r'[^\t -~]', line)
        if odd:
            problems.append('line %d holds a character other than printable ASCII and tab (\\x%02x)'
                            % (k, ord(odd.group(0)))); continue
        if line == '' or line.startswith('#'): continue
        m = re.fullmatch(r'([0-9a-f]{64})  (\S+)', line)
        if not m:
            problems.append('line %d is not "<sha256>  <path>"' % k); continue
        want, rel = m.groups()
        parts = rel.split('/')
        if rel.startswith('/') or '\\' in rel or ':' in rel or any(p in ('', '.', '..') for p in parts):
            problems.append('line %d: %s is not a plain relative path' % (k, show(rel))); continue
        if rel in seen:
            problems.append('line %d: %s is listed twice' % (k, show(rel))); continue
        seen.add(rel)
        if not rel.endswith('.v'): continue
        # a plant, as version 3 decides it: a plants/ folder below the path's first part, so that version 4 scans
        # every file of a list that version 3 scans
        if '/plants/' in rel: nplants += 1; continue
        entries.append((rel, want))
    return problems, entries, nplants, digest

def check_file(root, rel, want):
    """Problems, refused occurrences and reported counts of one file; want is its listed sha256 or None."""
    try:
        with open(os.path.join(root, rel), 'rb') as f: raw = f.read()
    except OSError as e:
        return ['cannot be read (%s)' % (e.strerror or type(e).__name__)], [], {}, None
    got = hashlib.sha256(raw).hexdigest()
    problems = []
    if want is not None and got != want:
        problems.append('sha256 %s is not the listed %s' % (got[:16], want[:16]))
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        problems.append('not UTF-8 (byte %d)' % e.start)
        return problems, [], {}, got
    refused, reported = scan_text(strip(text))
    refused = sorted(refused + outside_ascii(text))
    return problems, refused, reported, got

def main(argv):
    a = argv[1:]
    if len(a) < 2 or a[0].startswith('--'):
        print(USAGE); return 2
    root, rest = a[0], a[1:]
    if rest[0] == '--list':
        if len(rest) != 2 or rest[1].startswith('--'):
            print(USAGE); return 2
        problems, entries, nplants, digest = read_list(rest[1])
        source = 'list %s (sha256 %s)' % (show(rest[1]), digest[:16] if digest else 'none')
        if not entries:
            problems.append('no .v file outside plants/ to scan')
    else:
        if any(x.startswith('--') for x in rest):
            print(USAGE); return 2
        problems, entries, nplants, seen = [], [], 0, set()
        for rel in rest:
            if rel in seen:
                problems.append('%s is given twice' % show(rel)); continue
            seen.add(rel); entries.append((rel, None))
        source = 'command line'
    if not os.path.isdir(root):
        problems.insert(0, 'the root %s is not a directory' % show(root))
    entries.sort()
    counts = '%d .v file(s) to scan, %d under plants/ not scanned' % (len(entries), nplants)
    if problems:
        more = '' if len(problems) <= 5 else '; and %d more' % (len(problems) - 5)
        rows = [('input', False, '%s: %s%s; %s' % (source, '; '.join(problems[:5]), more, counts), [])]
    else:
        rows = [('input', True, '%s: %s' % (source, counts), [])]
    rep_tot = {}
    for rel, want in entries:
        bad, refused, reported, got = check_file(root, rel, want)
        for what, c in reported.items(): rep_tot[what] = rep_tot.get(what, 0) + c
        lines = ['    REFUSED %s line %d: %s (%s)' % (show(rel), k, what, show(w)) for k, what, w in refused]
        if refused:
            bad.append('%d refused occurrence(s)' % len(refused))
        if bad:
            rows.append((show(rel), False, '; '.join(bad), lines))
        else:
            rows.append((show(rel), True, 'none refused, sha256 %s%s' % (got[:16], ' as listed' if want else ''), []))
    width = max(len(r[0]) for r in rows)
    for name, ok, detail, lines in rows:
        print('  %s  %s  %s' % (name.ljust(width), 'ok' if ok else 'FAIL', detail))
        for line in lines: print(line)
    print('    reported, not refused (occurrences): %s'
          % ('; '.join('%s %d' % kv for kv in sorted(rep_tot.items())) or 'none'))
    nfail, n = sum(1 for r in rows if not r[1]), len(rows)
    if nfail:
        print('%s FAILED: %d of %d rows failed' % (NAME, nfail, n)); return 1
    print('%s HELD: %d of %d rows' % (NAME, n, n)); return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
