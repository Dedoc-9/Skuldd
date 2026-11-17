# R4 (c), Q4: the feature-absence row, version 3 (2026-11-17, scratch; written by the assistant). Standard library only.
#   python -B feature_row3.py <root> <file.v> ...          scan the files (paths relative to <root>)
#   python -B feature_row3.py <root> --list <FROZEN4.txt>   scan every .v of the list outside plants/
# Version 2 refused recursive definitions and checking-flag changes (his ruling Q4), lexing comments and strings as
# Coq does and scanning across lines. Version 3 keeps all of that and also refuses the triggers of the upstream
# critical-bugs entries that affect Coq 8.20.1 and that the tier does not use (a census of the tier sources and the
# law draft found none of them): native compilation, primitive declarations and types, SProp, universe polymorphism
# and universe declarations, module types and functors, plugins, rewrite rules, sections, coinductive types, every
# kind of assumption, the abstract tactic and Proof using, and a let-in inside an inductive or record declaration.
# ALLOWED, with the reason: vm_compute (the tier uses it; coqchk re-checks those casts without the virtual machine),
# and plain Inductive and Record declarations (the tier has four: two constant enumerations and two operation records).
# The scan sees source text only. A construct a tactic builds without one of these words, or one inside a library, is
# not seen; library code is the image's, and its re-check under a second Coq release is a separate step.
import hashlib, os, re, sys
sys.dont_write_bytecode = True

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
]
REPORTED = [
    ('vm_compute (allowed; coqchk re-checks it without the VM)', r'\bvm_compute\b|\bvm_cast_no_check\b|<:'),
    ('inductive or record (allowed: plain declarations)', r'\b(Inductive|Variant|Record|Structure)\b'),
    ('other Set or Unset', r'(?m)^\s*(#\[[^\]]*\]\s*)?(Local\s+|Global\s+|Export\s+)?(Set|Unset)\s+[A-Z]'),
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

def scan(root, rel):
    raw = open(os.path.join(root, rel), 'rb').read()
    t = strip(raw.decode('utf-8'))
    refused, reported = [], {}
    for what, pat in REFUSED:
        for m in re.finditer(pat, t):
            refused.append((t.count('\n', 0, m.start()) + 1, what, ' '.join(m.group(0).split())[:60]))
    for what, pat in REPORTED:
        k = len(re.findall(pat, t))
        if k: reported[what] = reported.get(what, 0) + k
    refused.sort()
    return hashlib.sha256(raw).hexdigest(), refused, reported

def main():
    a = sys.argv[1:]
    if len(a) < 2: print('usage: feature_row3.py <root> <file.v> ... | <root> --list <FROZEN4.txt>'); return 2
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
    print('  reported, not refused (occurrences): %s' % ('; '.join('%s %d' % kv for kv in sorted(rep_tot.items())) or 'none'))
    if nref:
        print('FEATURE ROW 3 FAILED: %d refused occurrence(s) in %d file(s)' % (nref, len(files))); return 1
    print('FEATURE ROW 3 HELD: %d file(s), none of the refused constructs' % len(files)); return 0

if __name__ == '__main__':
    sys.exit(main())
