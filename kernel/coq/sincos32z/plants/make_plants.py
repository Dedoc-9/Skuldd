# The plants of sincos32z's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B sincos32z/plants/make_plants.py json          prints gate.json
#   python3 -B sincos32z/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B sincos32z/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B sincos32z/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B sincos32z/plants/make_plants.py list          one line per plant
# The form is sincos32i/plants/make_plants.py's. A plant is one source of the folder with ONE change (the whole of
# Closed.v for four-of-six and guard), put in place of that source; the gate must refuse it for the reason its entry
# states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Zero.v is
# held to that line's text here: if the source moves, this script stops and says where.
#
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement is refused where the proof script no longer fits it. That is not a proof that the changed statement is
# false. Each entry's "what" says KNOWN FALSE with its witness; every statement plant of this folder is KNOWN FALSE
# (none is ROUTE ONLY, none is an equivalent mutant).
#
# WITNESSES. MEASURED means ext-work/sincos32-ieee/stage/runs/measure-plants-run1.txt, sections E and F
# (measure_plants.py, by the assistant, this host's Python floats in the manner of zero-sign/measure_zero.py and
# measure_step.py). "want" is what the frozen statement asks at that input (sine zero: a zero with the sign of the
# input; cosine zero: +0; an input that is not finite: NaN); that sin (2 pi x) or cos (2 pi x) is exactly 0 at the
# named x is plain (2 x, or 2 x - 1/2, is a whole number). That the Python evaluation is the Coq term is argued (the
# same operations in the same order), not shown.
#   the step changed (the planted stepped shape's result / want):
#     sin-step-none            sine at 3F000000 (1/2): -0 / +0
#     sin-step-abs             sine at BF000000 (-1/2): +0 / -0
#     cos-step-none            cosine at 3E800000 (1/4): -0 / +0;  at +infinity: 1 / NaN
#     cos-step-no-abs          cosine at BF400000 (-3/4): -0 / +0
#     cos-step-sub             cosine at 3E800000 (1/4): -0 / +0
#   the claim changed (the frozen stepped shape's result / the planted claim):
#     zero-cos-minus           cosine at 3E800000 (1/4): +0 / -0
#     zero-sin-plus            sine at BF000000 (-1/2): -0 / +0
#     zero-sin-opposite        sine at 3F000000 (1/2): +0 / -0
#     zero-sin-no-finite       sine at NaN (real number 0, a binary32 number, sin 0 = 0): NaN / +0
#     nonfinite-cos-unstepped  the UNSTEPPED cosine shape at +infinity: 1 / NaN
#     value-cos-is-sin         cosine at 00000000 (0): 1 / the sine graph's value, 0
# The row that holds the statement itself is the gate's hash row (frozen inputs unchanged), not a plant.
# WHAT THE GATE CANNOT EXPRESS HERE: a plant replaces a file of the judged folder only, so no plant of this folder
# changes sincos32i's statement (the record TOPS, tieee_ops, the frozen shapes); those are sincos32i's own plants.
# "deps" names whole folders (see sincos32i/plants/make_plants.py).
# The gate is gate/gate4.py alone, run on the tree that holds this folder: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = '0a2662b8ea5743faeddb35fcaf5499738e0d67a357c7cd88f8225683dcc66b1a'
NAME = 'SINCOS32_IEEE_ZERO'; FOLDER = 'sincos32z'
DEPS = ['f32', 'p32', 'p32r', 'exp32', 'exp32r', 'ieee64', 'sin32', 'cos32', 'sincos32', 'sincos32i']
FILES = ['SINCOS32_IEEE_Zero_Statement.v', 'Zero.v', 'Closed.v', 'Identity.v']
S, Z, C = 'SINCOS32_IEEE_Zero_Statement.v', 'Zero.v', 'Closed.v'
ME = 'sincos32z/plants/make_plants.py'

# Lines of Zero.v that a refusal is pinned to: (file, line, text that line must hold).
PINS = {
    'sin-value': (Z, 110, '  unfold Z_sinturn32. exact (zsin_value b _ _ Fb Fy Vy).'),
    'cos-value': (Z, 116, '  unfold Z_costurn32. exact (zcos_value b _ _ Fb Fy Vy).'),
    'sin-zero-intros': (Z, 121, '  intros b Fb F32 V. destruct (IEEE_SINTURN32_proof b Fb F32) as [Fy Vy].'),
    'sin-zero': (Z, 123, '  unfold Z_sinturn32. exact (zsin_zero b _ Fb Fy Vy).'),
    'cos-zero': (Z, 130, '  unfold Z_costurn32. exact (zcos_zero b _ Fb Fy Vy).'),
    'cos-nan': (Z, 142, '  intros b Fb. unfold Z_costurn32. exact (zcos_nan b _ Fb).'),
}
def at(pin): return 'sincos32z/%s", line %d, characters' % (PINS[pin][0], PINS[pin][1])

SIN_STEP = '  t_sel_le o (t_abs o (T_sinturn32 T o x)) (t_cst o K_0) (t_mul o x (t_cst o K_0)) (T_sinturn32 T o x).'
COS_STEP = '  t_add o (T_costurn32 T o x) (t_mul o (t_abs o x) (t_cst o K_0)).'
FOUR_OF_SIX = '''(* Plant: under the name SINCOS32_IEEE_ZERO, a statement of four of the six parts (the two NONFINITE parts left
   out), and its proof. The identity must refuse a theorem of another statement that carries the statement's name. *)
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement Zero.
Definition SINCOS32_IEEE_ZERO : Prop := Z_SIN_VALUE /\\ Z_COS_VALUE /\\ Z_SIN_ZERO /\\ Z_COS_ZERO.
Theorem sincos32_ieee_zero_holds : SINCOS32_IEEE_ZERO.
Proof.
  exact (conj Z_SIN_VALUE_proof (conj Z_COS_VALUE_proof (conj Z_SIN_ZERO_proof Z_COS_ZERO_proof))).
Qed.
'''
GUARD = '''(* Plant: SINCOS32_IEEE_ZERO from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_ieee_zero_holds : SINCOS32_IEEE_ZERO.
Proof. exact (False_ind _ (loop 0)). Qed.
'''
MUL0_HEAD = 'Lemma mul0 (b : b64) : is_finite b = true ->\n'
MUL0_AXIOM = ('Axiom mul0 : forall b : b64, is_finite b = true ->\n'
              '  t_mul tieee_ops b (t_cst tieee_ops K_0) = @B754_zero 53 1024 (Bsign b).\n\n')

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) the step changed
    ('sin-step-none', 'a step', S, [(SIN_STEP, '  T_sinturn32 T o x.')],
     ('fails', 'Zero', at('sin-value')),
     'the sine\'s step returns y unchanged (Z_sinturn32 is T_sinturn32). KNOWN FALSE, MEASURED: at x = 1/2 '
     '(3F000000), where the sine is exactly 0, the planted shape gives -0 and the statement asks +0. Refused '
     'where the proof of Z_SIN_VALUE applies the step lemma'),
    ('sin-step-abs', 'a step', S,
     [('(t_cst o K_0) (t_mul o x (t_cst o K_0)) (T_sinturn32 T o x).', '(t_cst o K_0) (t_mul o (t_abs o x) (t_cst o K_0)) (T_sinturn32 T o x).')],
     ('fails', 'Zero', at('sin-value')),
     'the sine\'s step selects |x| * 0 for x * 0 (the sign of the input is lost). KNOWN FALSE, MEASURED: at '
     'x = -1/2 (BF000000) the planted shape gives +0 and the statement asks -0. Refused where the proof of '
     'Z_SIN_VALUE applies the step lemma'),
    ('cos-step-none', 'a step', S, [(COS_STEP, '  T_costurn32 T o x.')],
     ('fails', 'Zero', at('cos-value')),
     'the cosine\'s step is omitted (Z_costurn32 is T_costurn32). KNOWN FALSE, MEASURED: at x = 1/4 (3E800000), '
     'where the cosine is exactly 0, the planted shape gives -0 and the statement asks +0; at +infinity it gives '
     '1 and the statement asks NaN. Refused where the proof of Z_COS_VALUE applies the step lemma'),
    ('cos-step-no-abs', 'a step', S, [(COS_STEP, '  t_add o (T_costurn32 T o x) (t_mul o x (t_cst o K_0)).')],
     ('fails', 'Zero', at('cos-value')),
     'the cosine\'s step adds x * 0 for |x| * 0. KNOWN FALSE, MEASURED: at x = -3/4 (BF400000) the planted shape '
     'gives -0 and the statement asks +0. Refused where the proof of Z_COS_VALUE applies the step lemma'),
    ('cos-step-sub', 'a step', S, [(COS_STEP, '  t_sub o (T_costurn32 T o x) (t_mul o (t_abs o x) (t_cst o K_0)).')],
     ('fails', 'Zero', at('cos-value')),
     'the cosine\'s step subtracts |x| * 0 where it must add it. KNOWN FALSE, MEASURED: at x = 1/4 (3E800000) the '
     'planted shape gives -0 and the statement asks +0. Refused where the proof of Z_COS_VALUE applies the step lemma'),
    # (b) the claim changed
    ('zero-cos-minus', 'b claim', S,
     [('Z_costurn32 b64 tieee_ops b = @B754_zero 53 1024 false.', 'Z_costurn32 b64 tieee_ops b = @B754_zero 53 1024 true.')],
     ('fails', 'Zero', at('cos-zero')),
     'Z_COS_ZERO asks -0 for +0 (the opposite sign). KNOWN FALSE, MEASURED: at x = 1/4 (3E800000) the stepped '
     'shape gives +0. Refused where the step lemma\'s +0 no longer fits'),
    ('zero-sin-plus', 'b claim', S,
     [('Z_sinturn32 b64 tieee_ops b = @B754_zero 53 1024 (Bsign b).', 'Z_sinturn32 b64 tieee_ops b = @B754_zero 53 1024 false.')],
     ('fails', 'Zero', at('sin-zero')),
     'Z_SIN_ZERO asks +0 at every exact zero, whatever the sign of the input. KNOWN FALSE, MEASURED: at x = -1/2 '
     '(BF000000) the stepped shape gives -0. Refused where the step lemma\'s sign no longer fits'),
    ('zero-sin-opposite', 'b claim', S,
     [('Z_sinturn32 b64 tieee_ops b = @B754_zero 53 1024 (Bsign b).', 'Z_sinturn32 b64 tieee_ops b = @B754_zero 53 1024 (negb (Bsign b)).')],
     ('fails', 'Zero', at('sin-zero')),
     'Z_SIN_ZERO asks the zero of the sign OPPOSITE to the input\'s. KNOWN FALSE, MEASURED: at x = 1/2 (3F000000) '
     'the stepped shape gives +0. Refused where the step lemma\'s sign no longer fits'),
    ('zero-sin-no-finite', 'c premise', S,
     [('  forall b : b64, is_finite b = true -> format32 (B2R b) -> sin (2 * PI * B2R b) = 0 ->',
       '  forall b : b64, format32 (B2R b) -> sin (2 * PI * B2R b) = 0 ->')],
     ('fails', 'Zero', at('sin-zero-intros')),
     'Z_SIN_ZERO without the premise that the input is finite. KNOWN FALSE, MEASURED: at NaN (whose real number '
     'is 0, a binary32 number with sin 0 = 0) the stepped shape gives NaN, not a zero. Refused where the proof '
     'takes the premise'),
    ('nonfinite-cos-unstepped', 'b claim', S,
     [('  forall b : b64, is_finite b = false -> is_nan (Z_costurn32 b64 tieee_ops b) = true.',
       '  forall b : b64, is_finite b = false -> is_nan (T_costurn32 b64 tieee_ops b) = true.')],
     ('fails', 'Zero', at('cos-nan')),
     'Z_COS_NONFINITE is claimed of the UNSTEPPED cosine shape T_costurn32. KNOWN FALSE, MEASURED: at +infinity '
     'the unstepped shape gives 1, not NaN. Refused where the proof applies the step\'s NaN lemma'),
    ('value-cos-is-sin', 'b claim', S,
     [('B2R (Z_costurn32 b64 tieee_ops b) = g_costurn32 (B2R b).', 'B2R (Z_costurn32 b64 tieee_ops b) = g_sinturn32 (B2R b).')],
     ('fails', 'Zero', at('cos-value')),
     'Z_COS_VALUE says the stepped cosine denotes the SINE graph\'s value. KNOWN FALSE, MEASURED: at x = 0 '
     '(00000000) the stepped cosine gives 1 and the sine shape gives 0. Refused where the value lemma no longer fits'),
    # (e) a proof left out, (f) an assumption put in, (g) another statement under the name, (h) a check switched off
    ('admitted-fin-zero', 'e proof', Z,
     [('  - exfalso. simpl in Vy. apply eq_0_F2R in Vy. simpl in Vy. destruct s; discriminate Vy.\nQed.\n',
       '  - exfalso. simpl in Vy. apply eq_0_F2R in Vy. simpl in Vy. destruct s; discriminate Vy.\nAdmitted.\n')],
     ('reader', 'Zero.fin_zero :', ['Admitted']),
     'Zero.fin_zero (a finite binary64 value whose real number is 0 is a zero) ends with Admitted'),
    ('admitted-closed', 'e proof', C,
     [('    (conj Z_SIN_NONFINITE_proof Z_COS_NONFINITE_proof))))).\nQed.\n',
       '    (conj Z_SIN_NONFINITE_proof Z_COS_NONFINITE_proof))))).\nAdmitted.\n')],
     ('reader', 'Closed.sincos32_ieee_zero_holds :', ['Admitted']),
     'the top theorem sincos32_ieee_zero_holds ends with Admitted'),
    ('mul0-axiom', 'f axiom', Z,
     [('cut', MUL0_HEAD, '(* The sine\'s step. *)', MUL0_AXIOM)],
     ('reader', 'Zero.mul0 :', ['Axiom']),
     'mul0 (b * +0 for a finite b is the zero with the sign of b) is an Axiom of Zero.v (the same text, its proof '
     'removed), used by the top theorem through zsin_value and zsin_zero'),
    ('four-of-six', 'g identity', C, FOUR_OF_SIX,
     ('fails', 'Identity', '"Closed.SINCOS32_IEEE_ZERO"'),
     'Closed.v states, under the name SINCOS32_IEEE_ZERO, four of the six parts (the two NONFINITE parts left out) '
     'and proves that'),
    ('guard', 'h guard', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'sincos32_ieee_zero_holds from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = {Z: raw(Z).decode('utf-8').split('\n')}
    for pin, (f, n, text) in sorted(PINS.items()):
        if n > len(lines[f]) or text not in lines[f][n - 1]:
            raise Stop('%s line %d does not hold %r (pin %s)' % (f, n, text, pin))

def plant_bytes(name):
    _, _, src, changes, _, _ = PLANTS[NAMES.index(name)]
    if isinstance(changes, str): return changes.encode('utf-8')
    text = raw(src).decode('utf-8'); n0 = text.count('\n')
    for ch in changes:
        if ch[0] == 'cut' and len(ch) == 4:
            _, first, last, new = ch
            if text.count(first) != 1: raise Stop('plant %s: the start of the cut occurs %d times in %s' % (name, text.count(first), src))
            i = text.index(first); j = text.find(last, i + len(first))
            if j < 0: raise Stop('plant %s: the end of the cut is not after its start in %s' % (name, src))
            text = text[:i] + new + text[j:]
        else:
            old, new = ch
            if old == new: raise Stop('plant %s: a change that changes nothing' % name)
            if text.count(old) != 1: raise Stop('plant %s: the text to change occurs %d times in %s' % (name, text.count(old), src))
            text = text.replace(old, new)
    if changes[0][0] != 'cut' and text.count('\n') != n0: raise Stop('plant %s moves the lines of %s' % (name, src))
    return text.encode('utf-8')

def gate_json():
    if len(set(NAMES)) != len(NAMES): raise Stop('a plant name is used twice')
    d = json.dumps
    L = ['{"name": %s, "tier": "flocq4", "deps": %s,' % (d(NAME), d(DEPS)),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {',
         '  "%s/gate.json": %s,' % (FOLDER, d([ME, 'json']))]
    L += ['  %s: %s%s' % (d(FOLDER + '/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
          for n, p in zip(NAMES, PLANTS)]
    L += [' },', ' "plants": {']
    for name, cls, src, _, exp, what in PLANTS:
        e = {'replace': {src: plant_path(name, src)}}
        if exp[0] == 'fails': e['fails'] = exp[1]; e['text'] = exp[2]
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
                print('wrote %s/%s %s' % (FOLDER, path, hashlib.sha256(b).hexdigest()))
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
                print('%-26s %-12s %-32s %s' % (name, cls, src, what))
        else:
            print('usage: make_plants.py json | plant NAME | write | check | list'); return 2
    except Stop as e:
        sys.stderr.write('make_plants: %s\n' % e); return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
