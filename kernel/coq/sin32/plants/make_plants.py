# The plants of sin32's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B sin32/plants/make_plants.py json          prints gate.json
#   python3 -B sin32/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B sin32/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B sin32/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B sin32/plants/make_plants.py list          one line per plant
# The form is compose/plants/make_plants.py's. A plant is one source of the folder with ONE change (the whole of
# Sin32.v for other-statement and guard), put in place of that source; the gate must refuse it for the reason its
# entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T;
#   "generated": P           the planted file is not what P's generator prints.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Sin32.v
# is held to that line's text here: if the source moves, this script stops and says where.
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement or the graph is refused where the proof script no longer fits it. That is not a proof that the changed
# statement is false. Each entry's "what" says which are known false and how (MEASURED means
# ext-work/sin32/measure-plants-run1.txt: the graph evaluated with Python floats against an 80-digit reference, by
# the assistant; that the Python rendering is the Coq graph is argued, not shown), and which are only refused by the
# route of the proof. The row that holds the statement itself is the gate's hash row, not a plant.
# The gate is gate/gate4.py alone, the anchored one, run on the tree mkf-ext/: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = 'e104124987c46be2a5d89ecc111677c9811ea847a912c892da831d699a83dfdc'
DEPS = ['f32', 'p32', 'p32r']
FILES = ['Graph.v', 'SIN32_Statement.v', 'Trunc.v', 'Sin32.v', 'Identity.v']
G, S, T, C = 'Graph.v', 'SIN32_Statement.v', 'Trunc.v', 'Sin32.v'
ME = 'sin32/plants/make_plants.py'

# Lines of Sin32.v that a refusal is pinned to: (line, text that line must hold).
PINS = {
    'poly-fold': (54, 'Proof. reflexivity. Qed.'),
    'smax-square': (178, '- unfold SMAX. lra.'),
    'zero-branch': (216, '- subst x. rewrite Rmult_0_l, (round_0 radix2 fexp64 ZnearestE), sin_0.'),
    'zero-f32': (218, 'apply (F32_rel 0 0). rewrite Rminus_0_r, Rabs_R0, Rmult_0_r. apply Rle_refl.'),
    'faithful-intros': (214, 'unfold SIN32, g_sin32. intros x Fx Hx.'),
    'finite-intros': (226, 'unfold SIN32_FINITE. intros x Fx Hx.'),
    'finite-apply': (227, 'apply (faithful_finite (sin x)); [| apply sin32_faithful; assumption].'),
}
def at(pin): return 'sin32/Sin32.v", line %d, characters' % PINS[pin][0]

SIN32_BODY = 'forall x : R, format32 x -> Rabs x <= SMAX -> faithful32 (sin x) (g_sin32 x).'
FINITE_BODY = 'forall x : R, format32 x -> Rabs x <= SMAX -> finite32 (g_sin32 x).'
TRUNC_POS_HEAD = ('Theorem sin_trunc_pos (a : R) : 0 <= a -> a * a <= 5 / 2 ->\n'
                  '  a * Pex (a * a) <= sin a <= a * Pex (a * a) + a * / 137438953472.\n')
TRUNC_POS_AXIOM = ('Axiom sin_trunc_pos : forall a : R, 0 <= a -> a * a <= 5 / 2 ->\n'
                   '  a * Pex (a * a) <= sin a <= a * Pex (a * a) + a * / 137438953472.\n')
OTHER = '''(* Plant: under the name SIN32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.sin32 Require Import SIN32_Statement.
Definition SIN32_ALL : Prop := True.
Theorem sin32_all : SIN32_ALL.
Proof. exact I. Qed.
'''
GUARD = '''(* Plant: SIN32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.sin32 Require Import SIN32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sin32_all : SIN32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
'''

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) the graph: one constant or one operation changed
    ('divisor-7', 'a graph', G,
     [(' / 6))).', ' / 7))).')],
     ('fails', 'Sin32', at('poly-fold')),
     'the last level divides by 7 for 6 (the x^3 coefficient is 1/7). KNOWN FALSE, MEASURED: at x = 1 (3F800000) '
     'the planted graph gives 3F5D36D6 and sin 1 lies between 3F576AA4 and 3F576AA5. Refused where the graph no '
     'longer folds into the levels the proof walks'),
    ('first-divisor-211', 'a graph', G,
     [('(u / 210)', '(u / 211)')],
     ('fails', 'Sin32', at('poly-fold')),
     'the first level divides by 211 for 210 (the x^15 coefficient a little off). NOT known false: MEASURED on '
     '60,000 inputs, 0 not faithful (the graph has more accuracy than the statement asks). Refused only by the '
     'route of the proof: the graph no longer folds into the levels the proof walks'),
    ('add-for-mul', 'a graph', G,
     [('narrow (RN64 (x * (sin32_poly (sin32_sq x)))).', 'narrow (RN64 (x + (sin32_poly (sin32_sq x)))).')],
     ('fails', 'Sin32', at('zero-branch')),
     'the last operation is x + t for x * t. KNOWN FALSE, MEASURED: at x = 0 the planted graph gives 1 (3F800000) '
     'and sin 0 = 0. Refused where the proof meets the last operation'),
    # (b) the graph edited by hand against its generator
    ('hand-edited-graph', 'b generated', G,
     [('Definition sin32_sq (x : R) : R := RN64 (x * x).\n', 'Definition sin32_sq (x : R) : R := RN64 (x * x). \n')],
     ('generated', 'sin32/Graph.v'),
     'Graph.v with one blank added at the end of a line: the same graph for Coq, and not what emit_sin32.py prints'),
    # (c) a premise of the statement dropped or widened
    ('prem-no-smax', 'c premise', S,
     [(SIN32_BODY, 'forall x : R, format32 x -> faithful32 (sin x) (g_sin32 x).')],
     ('fails', 'Sin32', at('faithful-intros')),
     'SIN32 without |x| <= SMAX. KNOWN FALSE, MEASURED: at x = 8 (41000000) the graph gives C08A224D and sin 8 '
     'lies between 3F7D4695 and 3F7D4696. Refused where the proof takes the premise'),
    ('prem-smax-pi', 'c premise', S,
     [('Definition SMAX : R := 13176795 / 8388608.', 'Definition SMAX : R := 13176795 / 4194304.')],
     ('fails', 'Sin32', at('smax-square')),
     'SMAX doubled (the binary32 number nearest pi). KNOWN FALSE, MEASURED: at x = 40490FDB the graph gives '
     'B566E91D and sin x lies between B3BBBD2F and B3BBBD2E. Refused where the proof needs SMAX^2 <= 5/2'),
    ('prem-finite-no-smax', 'c premise', S,
     [(FINITE_BODY, 'forall x : R, format32 x -> finite32 (g_sin32 x).')],
     ('fails', 'Sin32', at('finite-intros')),
     'SIN32_FINITE without |x| <= SMAX. False, ARGUED and not evaluated: the model has no overflow, and at '
     'x = 2^127 the polynomial is of the order of x^14, far above FMAX32. Refused where the proof takes the premise'),
    # (d) the conclusion strengthened
    ('concl-round-down', 'd conclusion', S,
     [('faithful32 (sin x) (g_sin32 x).', 'g_sin32 x = RD32 (sin x).')],
     ('fails', 'Sin32', at('zero-f32')),
     'SIN32 says the result is sin x rounded DOWN. KNOWN FALSE, MEASURED: at x = 2^-100 (0D800000) the graph gives '
     'x itself, 0D800000, and sin x rounded down is 0D7FFFFF. Refused where lemma F32 no longer fits'),
    ('concl-correct', 'd conclusion', S,
     [('faithful32 (sin x) (g_sin32 x).', 'g_sin32 x = RN32 (sin x).')],
     ('fails', 'Sin32', at('zero-f32')),
     'SIN32 claims the correctly rounded result. KNOWN FALSE, MEASURED: at x = 3FC8DB65 the graph gives 3F7FFFEA '
     'and the correctly rounded sin x is 3F7FFFEB (the first such input found going down from SMAX, after 13,431). '
     'Refused where lemma F32 no longer fits'),
    ('concl-finite-half', 'd conclusion', S,
     [('finite32 (g_sin32 x).', 'Rabs (g_sin32 x) <= / 2.')],
     ('fails', 'Sin32', at('finite-apply')),
     'SIN32_FINITE says the result is at most 1/2 in magnitude. KNOWN FALSE, MEASURED: at x = SMAX (3FC90FDB) the '
     'graph gives 1 (3F800000). Refused where faithful_finite no longer fits'),
    # (e), (f), (g), (h) a proof left out, an assumption put in, another statement under the name, a check switched off
    ('admitted', 'e proof', C,
     [('  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4. lra.\nQed.\n', '  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4.\nAdmitted.\n')],
     ('reader', 'Sin32.lv_first :', ['Admitted']),
     'Sin32.lv_first (the first level of the polynomial) ends with Admitted for its last step'),
    ('trunc-axiom', 'f axiom', T,
     [('cut', TRUNC_POS_HEAD, '(* Both signs', TRUNC_POS_AXIOM + '\n')],
     ('reader', 'Trunc.sin_trunc_pos :', ['Axiom']),
     'the truncation bound sin_trunc_pos is an Axiom of Trunc.v (the same text, its proof removed), used by the '
     'top theorem through sin_trunc'),
    ('other-statement', 'g identity', C, OTHER,
     ('fails', 'Identity', 'has type "Sin32.SIN32_ALL"'),
     'Sin32.v states, under the name SIN32_ALL, the proposition True and proves that'),
    ('guard', 'h guard', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'sin32_all from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = raw(C).decode('utf-8').split('\n')
    for pin, (n, text) in sorted(PINS.items()):
        if n > len(lines) or text not in lines[n - 1]:
            raise Stop('%s line %d does not hold %r (pin %s)' % (C, n, text, pin))

def plant_bytes(name):
    _, _, src, changes, _, _ = PLANTS[NAMES.index(name)]
    if isinstance(changes, str): return changes.encode('utf-8')
    text = raw(src).decode('utf-8')
    for ch in changes:
        if ch[0] == 'cut' and len(ch) == 4:
            _, first, last, new = ch
            if text.count(first) != 1: raise Stop('plant %s: the start of the cut occurs %d times in %s' % (name, text.count(first), src))
            i = text.index(first); j = text.find(last, i + len(first))
            if j < 0: raise Stop('plant %s: the end of the cut is not after its start in %s' % (name, src))
            text = text[:i] + new + text[j:]
        else:
            old, new = ch
            if text.count(old) != 1: raise Stop('plant %s: the text to change occurs %d times in %s' % (name, text.count(old), src))
            text = text.replace(old, new)
    return text.encode('utf-8')

def gate_json():
    if len(set(NAMES)) != len(NAMES): raise Stop('a plant name is used twice')
    d = json.dumps
    L = ['{"name": "SIN32", "tier": "flocq4", "deps": %s,' % d(DEPS),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {', '  "sin32/Graph.v": %s,' % d(['sin32/emit_sin32.py', 'coq', '-']),
         '  "sin32/gate.json": %s,' % d([ME, 'json'])]
    L += ['  %s: %s%s' % (d('sin32/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
          for n, p in zip(NAMES, PLANTS)]
    L += [' },', ' "plants": {']
    for name, cls, src, _, exp, what in PLANTS:
        e = {'replace': {src: plant_path(name, src)}}
        if exp[0] == 'fails': e['fails'] = exp[1]; e['text'] = exp[2]
        elif exp[0] == 'generated': e['generated'] = exp[1]
        else: e['reader'] = exp[1]; e['words'] = exp[2]
        e['class'] = cls; e['what'] = what
        L.append('  %s: %s%s' % (d(name), d(e), ',' if name != NAMES[-1] else ''))
    L.append(' }}')
    text = '\n'.join(L) + '\n'
    json.loads(text)
    return text.encode('ascii')

def everything():
    check_sources()
    out = {'gate.json': gate_json()}
    for name, p in zip(NAMES, PLANTS): out[plant_path(name, p[2])] = plant_bytes(name)
    return out

def main():
    a = sys.argv[1:]
    try:
        if a == ['json']:
            check_sources(); sys.stdout.buffer.write(gate_json())
        elif len(a) == 2 and a[0] == 'plant' and a[1] in NAMES:
            check_sources(); sys.stdout.buffer.write(plant_bytes(a[1]))
        elif a == ['write']:
            for path, b in sorted(everything().items()):
                with open(os.path.join(DIR, path), 'wb') as fh: fh.write(b)
                print('wrote sin32/%s %s' % (path, hashlib.sha256(b).hexdigest()))
        elif a == ['check']:
            bad = []
            for path, b in sorted(everything().items()):
                try: same = raw(path) == b
                except OSError: same = False
                if not same: bad.append(path)
            have = sorted(f for f in os.listdir(HERE) if f.endswith('.v'))
            want = sorted(os.path.basename(plant_path(n, p[2])) for n, p in zip(NAMES, PLANTS))
            if have != want: bad.append('plants/ holds other .v files than the table\'s: %s' % sorted(set(have) ^ set(want)))
            print('PLANT FILES %s: gate.json and %d plants%s' % ('AS WRITTEN HERE' if not bad else 'DIFFER', len(NAMES), '' if not bad else '; not the same: %s' % ', '.join(bad)))
            return 1 if bad else 0
        elif a == ['list']:
            for name, cls, src, _, exp, what in PLANTS:
                print('%-22s %-13s %-20s %s' % (name, cls, src, what))
        else:
            print('usage: make_plants.py json | plant NAME | write | check | list'); return 2
    except Stop as e:
        sys.stderr.write('make_plants: %s\n' % e); return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
