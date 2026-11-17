# Counts candidate critical-bug triggers in Coq sources, with comments and strings stripped as feature_row2.py does
# (written by the assistant, 2026-11-17; standard library only). Usage: python -B trigger_census.py ROOT FILE...
import importlib.util, os, re, sys
sys.dont_write_bytecode = True
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('fr2', os.path.join(here, 'feature_row2.py'))
fr2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(fr2)
TRIGGERS = [
    ('native_compute', r'\bnative_compute\b|\bnative_cast_no_check\b|<<:'),
    ('vm_compute', r'\bvm_compute\b|\bvm_cast_no_check\b|<:'),
    ('Primitive or Register', r'\b(Primitive|Register)\b'),
    ('primitive types', r'\b(PrimFloat|PrimInt63|Uint63|Sint63|Int63|Float64|PArray|PrimArray|PrimString)\b'),
    ('SProp', r'\bSProp\b'),
    ('universe polymorphism', r'\b(Polymorphic|Cumulative|NonCumulative)\b|#\[\s*universes'),
    ('universe declarations', r'\bUniverses?\b|\bConstraint\b'),
    ('primitive projections', r'\bPrimitive\s+Projections\b'),
    ('module types and functors', r'\b(Module\s+Type|Declare\s+Module|Functor)\b|\bModule\s+\w+\s*\('),
    ('Parameter Inline', r'\bParameter\s+Inline\b'),
    ('plugins', r'\bDeclare\s+ML\s+Module\b'),
    ('rewrite rules', r'\bRewrite\s+Rules?\b|\bSymbol\b'),
    ('sections', r'\bSection\b'),
    ('CoInductive', r'\bCoInductive\b'),
    ('Inductive or Variant', r'\b(Inductive|Variant)\b'),
    ('Record or Structure', r'\b(Record|Structure|Class)\b'),
    ('let in a constructor type', r'\bInductive\b[^.]*\blet\b'),
    ('abstract or Proof using', r'\babstract\b|\bProof\s+using\b'),
    ('propext or other axioms', r'\b(propositional_extensionality|propext|proof_irrelevance|Axiom|Parameter|Conjecture)\b'),
]
root = sys.argv[1]
tot = {}
for rel in sys.argv[2:]:
    t = fr2.strip(open(os.path.join(root, rel), 'rb').read().decode('utf-8'))
    for name, pat in TRIGGERS:
        n = len(re.findall(pat, t))
        if n: tot.setdefault(name, []).append((rel, n))
print('files scanned: %d' % (len(sys.argv) - 2))
for name, _ in TRIGGERS:
    lst = tot.get(name, [])
    print('%-28s %4d occurrence(s) in %3d file(s)  %s' % (name, sum(n for _, n in lst), len(lst), ' '.join('%s:%d' % x for x in lst[:6])))
