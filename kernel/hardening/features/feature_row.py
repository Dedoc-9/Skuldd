# R4 (c), Q4: the feature-absence row (2026-11-16, scratch). Standard library only.
#   python -B feature_row.py <root> <file.v> ...          scan the files (paths relative to <root>)
#   python -B feature_row.py <root> --list <FROZEN4.txt>   scan every .v of the list outside plants/
# REFUSED (the owner's ruling Q4: "refuse recursive definitions and checking-flag changes in tier sources"):
#   recursive definitions: the commands Fixpoint, CoFixpoint, Function, Equations, Scheme, Program (Program Fixpoint and
#   Program Definition can define by well-founded recursion) and the terms or tactics fix and cofix;
#   checking-flag changes: Unset (Local, Global) Guard Checking, Positivity Checking or Universe Checking, a
#   bypass_check attribute, Set Definitional UIP, Set (Unset) Typing Flags style commands.
# REPORTED, not refused (the ruling names only the two classes above): Inductive, CoInductive, Variant, Polymorphic,
#   Universe(s), Primitive, Register, Module Type, Declare Module, SProp, Axiom, Parameter, Admitted, admit, and every
#   other Set or Unset command.
# Comments (nested) and string literals are removed before the scan, so a word inside them counts for nothing. The
# scan sees source text only: a fixpoint that a tactic builds without one of these words (for example by applying a
# library recursor) is not seen; such a term is the library's, whose own definition the image fixes.
import hashlib, os, re, sys
sys.dont_write_bytecode = True

REFUSED = [
    ('recursive definition', r'\b(Fixpoint|CoFixpoint|Function|Equations|Scheme|Program)\b'),
    ('recursive term or tactic', r'\b(fix|cofix)\b'),
    ('checking flag', r'\bUnset\s+(Guard|Positivity|Universe)\s+Checking\b'),
    ('checking flag', r'\bbypass_check\b'),
    ('checking flag', r'\bSet\s+Definitional\s+UIP\b'),
    ('checking flag', r'\b(Set|Unset)\s+Typing\s+Flags\b'),
]
REPORTED = [
    ('inductive type', r'\b(Inductive|CoInductive|Variant)\b'),
    ('universe polymorphism', r'\b(Polymorphic|Monomorphic|Universes?|Cumulative)\b'),
    ('primitive or register', r'\b(Primitive|Register)\b'),
    ('module system', r'\b(Module\s+Type|Declare\s+Module|Functor)\b'),
    ('SProp', r'\bSProp\b'),
    ('assumption', r'\b(Axiom|Axioms|Parameter|Parameters|Conjecture|Hypothesis|Variable|Variables|Admitted|admit)\b'),
    ('other Set or Unset', r'^\s*(#\[[^\]]*\]\s*)?(Local\s+|Global\s+|Export\s+)?(Set|Unset)\s+[A-Z]'),
]

def strip(text):
    """Comments (nested) and string literals replaced by spaces; newlines kept so line numbers stay right."""
    out, i, depth, n = [], 0, 0, len(text)
    while i < n:
        if depth == 0 and text[i] == '"':                      # a string literal; "" inside is an escaped quote
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"': j += 2; continue
                    break
                j += 1
            out.append(''.join(c if c == '\n' else ' ' for c in text[i:j + 1])); i = j + 1; continue
        if text.startswith('(*', i): depth += 1; out.append('  '); i += 2; continue
        if depth and text.startswith('*)', i): depth -= 1; out.append('  '); i += 2; continue
        c = text[i]; out.append(c if (depth == 0 or c == '\n') else ' '); i += 1
    return ''.join(out)

def scan(root, rel):
    raw = open(os.path.join(root, rel), 'rb').read()
    t = strip(raw.decode('utf-8'))
    lines = t.split('\n')
    refused, reported = [], {}
    for k, l in enumerate(lines, 1):
        for what, pat in REFUSED:
            for m in re.finditer(pat, l): refused.append((k, what, m.group(0)))
        for what, pat in REPORTED:
            if re.search(pat, l): reported[what] = reported.get(what, 0) + 1
    return hashlib.sha256(raw).hexdigest(), refused, reported

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__ or 'usage: feature_row.py <root> <file.v> ... | --list <FROZEN4.txt>'); return 2
    root = a[0]
    if a[1] == '--list':
        files = []
        for l in open(a[2], encoding='ascii').read().splitlines():
            m = re.fullmatch(r'[0-9a-f]{64}  (\S+\.v)', l)
            if m and '/plants/' not in m.group(1): files.append(m.group(1))
    else:
        files = a[1:]
    nref, rep_tot = 0, {}
    for rel in files:
        h, ref, rep = scan(root, rel)
        for k, what, w in ref:
            print('  REFUSED %s line %d: %s (%s)' % (rel, k, what, w)); nref += 1
        for what, c in rep.items(): rep_tot[what] = rep_tot.get(what, 0) + c
    print('  reported, not refused (lines): %s' % (', '.join('%s %d' % kv for kv in sorted(rep_tot.items())) or 'none'))
    if nref:
        print('FEATURE ROW FAILED: %d refused occurrence(s) in %d file(s)' % (nref, len(files))); return 1
    print('FEATURE ROW HELD: %d file(s), no recursive definition and no checking-flag change' % len(files)); return 0

if __name__ == '__main__':
    sys.exit(main())
