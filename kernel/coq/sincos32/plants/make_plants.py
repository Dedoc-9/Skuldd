# The plants of sincos32's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B sincos32/plants/make_plants.py json          prints gate.json
#   python3 -B sincos32/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B sincos32/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B sincos32/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B sincos32/plants/make_plants.py list          one line per plant
# The form is cos32/plants/make_plants.py's. A plant is one source of the folder with ONE change (the whole of
# Sincos32.v for other-statement and guard), put in place of that source; the gate must refuse it for the reason its
# entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T;
#   "generated": P           the planted file is not what P's generator prints.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Reduce.v,
# Core.v or Sincos32.v is held to that line's text here: if the source moves, this script stops and says where.
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement or the graph is refused where the proof script no longer fits it. That is not a proof that the changed
# statement is false. Each entry's "what" says which are known false and how, and which are only refused by the route
# of the proof. WITNESSES (MEASURED means ext-work/sincos32/measure-plants-run4.txt, by the assistant: for a graph
# plant the emitter's table with the same one change, shown to print the plant file byte for byte, evaluated with
# Python floats by the emitter's own evaluator at the named input; the true value by exact rational reduction and an
# 80-digit series, proto_turn2.py's ref_sinturn; "between A and B" are the two binary32 neighbours of the true
# value, as bit patterns; that the Python evaluation is the Coq graph is argued, not shown):
#   sel-k1-s-for-c     sin at 3E800000 (1/4): planted 00000000 (0); true value exactly 1 (3F800000)
#   big-2p22           cos at 4A800001 (4194304.5): planted 3F800000 (1); true value exactly -1 (BF800000)
#   arg-pl-for-ph      sin at 3E800000 (1/4): planted 248D3132 (about 6.1e-17); true value exactly 1 (3F800000)
#   q-2f               sin at 3E800000 (1/4): planted 3F3504F3 (about 0.7071); true value exactly 1 (3F800000)
#   sel-k2-no-sign     sin at 3F028F5C (about 0.51): planted 3D809849; true value between BD809849 and BD809848
#   cn-2p52            sin at BE99999A (about -0.3): planted 3F737870; true value between BF737871 and BF737870
#   prem-no-format     cos at the binary64 number 8388608.5 (not a binary32 number): the graph gives 1; true value -1
#   concl-correct      sin at 3E80300C (about 0.25037): the graph gives 3F7FFFD3; the true value lies between
#                      3F7FFFD3 and 3F7FFFD4 and the correctly rounded value is 3F7FFFD4 (the first such input going
#                      up from 3E800001, after 12,300; NO sin line of the frozen corpus is misrounded)
#   exact-quarter-zero, unit-half   sin at 3E800000 (1/4): the graph gives 3F800000 (1)
# The row that holds the statement itself is the gate's hash row, not a plant.
# The gate is gate/gate4.py alone, the anchored one, run on the tree mkf-ext/: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = '23958fc7c500a956429a8a32fcb03188ffdfd99782b2bd35ee913bb38c6e5cc2'
NAME = 'SINCOS32'; FOLDER = 'sincos32'
DEPS = ['f32', 'p32', 'p32r', 'sin32', 'cos32']
FILES = ['Graph.v', 'SINCOS32_Statement.v', 'Reduce.v', 'Core.v', 'Sincos32.v', 'Identity.v']
G, S, R, C, T = 'Graph.v', 'SINCOS32_Statement.v', 'Reduce.v', 'Core.v', 'Sincos32.v'
ME = 'sincos32/plants/make_plants.py'

# Lines that a refusal is pinned to: (file, line, text that line must hold).
PINS = {
    'n-window': (R, 84, 'change (bpow radix2 (53 - 1)) with 4503599627370496. change (bpow radix2 53) with 9007199254740992. lra. }'),
    'n-even': (R, 89, 'match goal with |- context [ZnearestE (v + IZR ?n)] => rewrite (ZnearestE_plus_even v n) by reflexivity;'),
    'q-exact': (R, 117, '{ unfold turn_q. rewrite Ef. apply round_generic; [typeclasses eauto | apply f32_f64; exact Fq]. }'),
    'arg-ph': (C, 65, 'eapply Rle_trans; [apply Rabs_triang |]. eapply Rle_trans; [apply Rplus_le_compat_r, Rabs_triang |].'),
    'big-case': (T, 109, 'split; [lra | apply Rmult_le_pos; assumption].'),
    'sel-k1': (T, 126, '+ rewrite sin_k1, cos_k1, Rabs_R1. split; decide_ifs HS HC.'),
    'sel-km2': (T, 123, '+ rewrite sin_km2, cos_km2, abs_m2. split; decide_ifs HS HC.'),
    'sin-f32': (T, 152, 'rewrite (T32_proof _ (sin_pre_fmt x)). apply F32_rel. exact (proj1 (pre_both x Fx)).'),
    'cos-intros': (T, 157, 'unfold COSTURN32, g_costurn32. intros x Fx.'),
    'exact-quarter': (T, 178, 'rewrite V in H. exact (faithful_fmt 1 _ f32_one H).'),
    'unit-sin': (T, 220, '- exact (faithful_unit _ _ (SIN_bound (2 * PI * x)) (sinturn32_faithful x Fx)).'),
}
def at(pin): return 'sincos32/%s", line %d, characters' % (PINS[pin][0], PINS[pin][1])

SIN_BODY = 'faithful32 (sin (2 * PI * x)) (g_sinturn32 x).'
COS_LINE = 'forall x : R, format32 x -> faithful32 (cos (2 * PI * x)) (g_costurn32 x).'
ADM_OLD = '  assert (B : (-8388610 < ZnearestE v)%Z) by (apply lt_IZR; lra).\n  lia.\nQed.\n'
ADM_NEW = '  assert (B : (-8388610 < ZnearestE v)%Z) by (apply lt_IZR; lra).\nAdmitted.\n'
B149_HEAD = 'Lemma b149 : bpow radix2 (-149) = 2 * bpow radix2 (-150).\n'
B149_AXIOM = 'Axiom b149 : bpow radix2 (-149) = 2 * bpow radix2 (-150).\n'
OTHER = '''(* Plant: under the name SINCOS32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.sincos32 Require Import SINCOS32_Statement.
Definition SINCOS32_ALL : Prop := True.
Theorem sincos32_all : SINCOS32_ALL.
Proof. exact I. Qed.
'''
GUARD = '''(* Plant: SINCOS32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32 Require Import SINCOS32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_all : SINCOS32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
'''

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) the graph: one constant, one operand or one selected value changed
    ('sel-k1-s-for-c', 'a graph', G,
     [('then (if Rle_dec 0 (turn_k x) then turn_C x else - (turn_C x))', 'then (if Rle_dec 0 (turn_k x) then turn_S x else - (turn_C x))')],
     ('fails', 'Sincos32', at('sel-k1')),
     'the sine\'s selection for k = 1 takes S for C. KNOWN FALSE, MEASURED: at x = 1/4 (3E800000) the planted graph '
     'gives 0 (00000000) and sin (2 pi x) is exactly 1 (3F800000). Refused where the proof decides the selection '
     'for k = 1'),
    ('big-2p22', 'a graph', G,
     [('Definition turn_BIG : R := 8388608.', 'Definition turn_BIG : R := 4194304.')],
     ('fails', 'Sincos32', at('big-case')),
     'the switch to the constant results at 2^22 for 2^23 (half turns are still binary32 numbers there). KNOWN '
     'FALSE, MEASURED: at x = 4194304.5 (4A800001) the planted graph\'s cosine gives 1 (3F800000) and cos (2 pi x) '
     'is exactly -1 (BF800000). Refused at the end of the proof\'s branch of the whole numbers, which the planted '
     'graph does not take where the proof does'),
    ('arg-pl-for-ph', 'a graph', G,
     [('RN64 (v * cos32_PH).', 'RN64 (v * cos32_PL).')],
     ('fails', 'Core', at('arg-ph')),
     'the argument is multiplied by cos32\'s second constant PL for PH (the wrong one of the two imported). KNOWN '
     'FALSE, MEASURED: at x = 1/4 (3E800000) the planted graph\'s sine gives 248D3132 (about 6.1e-17) and '
     'sin (2 pi x) is exactly 1 (3F800000). Refused where the proof splits the argument\'s error into the rounding '
     'of v PH and the distance of PH from PI/2'),
    ('q-2f', 'a graph', G,
     [('RN64 (4 * (turn_f x)).', 'RN64 (2 * (turn_f x)).')],
     ('fails', 'Reduce', at('q-exact')),
     'q = 2 f for 4 f (half turns for quarter turns). KNOWN FALSE, MEASURED: at x = 1/4 (3E800000) the planted '
     'graph\'s sine gives 3F3504F3 (about 0.7071) and sin (2 pi x) is exactly 1 (3F800000). Refused where the '
     'reduction needs q = 4 f'),
    ('sel-k2-no-sign', 'a graph', G,
     [('  else - (turn_S x).\n', '  else turn_S x.\n')],
     ('fails', 'Sincos32', at('sel-km2')),
     'the sine\'s last case (|k| = 2) without its change of sign. KNOWN FALSE, MEASURED: at x = 3F028F5C (about '
     '0.51) the planted graph gives 3D809849 and sin (2 pi x) lies between BD809849 and BD809848. Refused where '
     'the proof decides the selection for k = -2'),
    ('cn-2p52', 'a graph', G,
     [('Definition turn_CN : R := 6755399441055744.', 'Definition turn_CN : R := 4503599627370496.')],
     ('fails', 'Reduce', at('n-window')),
     'the rounding constant is 2^52 for 1.5 * 2^52 (a negative v then leaves the window where binary64\'s grid is '
     '1). KNOWN FALSE, MEASURED: at x = BE99999A (about -0.3) the planted graph\'s sine gives 3F737870 and '
     'sin (2 pi x) lies between BF737871 and BF737870. Refused where v + CN must lie in [2^52, 2^53)'),
    ('cn-odd', 'a graph', G,
     [('Definition turn_CN : R := 6755399441055744.', 'Definition turn_CN : R := 6755399441055743.')],
     ('fails', 'Reduce', at('n-even')),
     'the rounding constant one smaller, an odd number (ties then go to the odd whole number). NOT known false: '
     'MEASURED by the emitter stage (emit-measure-run2.txt) on the 633,224 lines of the frozen corpus, 0 results '
     'differ; a whole number within 1/2 is all the method needs. Refused only by the route of the proof, which '
     'moves the constant through round-to-nearest-even by a lemma that asks for an even whole number'),
    # (b) the graph edited by hand against its generator
    ('hand-edited-graph', 'b generated', G,
     [('Definition turn_BIG : R := 8388608.\n', 'Definition turn_BIG : R := 8388608. \n')],
     ('generated', 'sincos32/Graph.v'),
     'Graph.v with one blank added at the end of a line: the same graph for Coq, and not what emit_sincos32.py prints'),
    # (c) the premise dropped
    ('prem-no-format', 'c premise', S,
     [(COS_LINE, 'forall x : R, faithful32 (cos (2 * PI * x)) (g_costurn32 x).')],
     ('fails', 'Sincos32', at('cos-intros')),
     'COSTURN32 for every real x, not only binary32 numbers. KNOWN FALSE, MEASURED: at the binary64 number '
     '8388608.5 (not a binary32 number) the graph gives 1 and cos (2 pi x) is exactly -1. Refused where the proof '
     'takes the premise'),
    # (d) a conclusion strengthened or changed
    ('concl-correct', 'd conclusion', S,
     [(SIN_BODY, 'g_sinturn32 x = RN32 (sin (2 * PI * x)).')],
     ('fails', 'Sincos32', at('sin-f32')),
     'SINTURN32 claims the correctly rounded result. KNOWN FALSE, MEASURED: at x = 3E80300C (about 0.25037) the '
     'graph gives 3F7FFFD3 and the correctly rounded sin (2 pi x) is 3F7FFFD4 (the first such input found going up '
     'from 3E800001, after 12,300; no sin line of the frozen corpus is misrounded). Refused where lemma F32 no '
     'longer fits'),
    ('exact-quarter-zero', 'd conclusion', S,
     [('(x = IZR n + 1 / 4 -> g_sinturn32 x = 1) /\\', '(x = IZR n + 1 / 4 -> g_sinturn32 x = 0) /\\')],
     ('fails', 'Sincos32', at('exact-quarter')),
     'SINTURN32_EXACT says the sine of a whole number plus a quarter turn is exactly 0. KNOWN FALSE, MEASURED: at '
     'x = 1/4 (3E800000) the graph gives 1 (3F800000). Refused where the value 1 no longer fits'),
    ('unit-half', 'd conclusion', S,
     [('Rabs (g_sinturn32 x) <= 1 /\\ Rabs (g_costurn32 x) <= 1.', 'Rabs (g_sinturn32 x) <= / 2 /\\ Rabs (g_costurn32 x) <= 1.')],
     ('fails', 'Sincos32', at('unit-sin')),
     'SINCOS32_UNIT says the sine is at most 1/2 in magnitude. KNOWN FALSE, MEASURED: at x = 1/4 (3E800000) the '
     'graph gives 1 (3F800000). Refused where the bound 1 no longer fits'),
    # (e), (f), (g), (h) a proof left out, an assumption put in, another statement under the name, a check switched off
    ('admitted', 'e proof', R, [(ADM_OLD, ADM_NEW)],
     ('reader', 'Reduce.near_bound :', ['Admitted']),
     'Reduce.near_bound (the nearest whole number of a v below 2^23 is below 2^23 + 2) ends with Admitted for its last step'),
    ('b149-axiom', 'f axiom', C,
     [('cut', B149_HEAD, '(* The argument: one rounding', B149_AXIOM + '\n')],
     ('reader', 'Core.b149 :', ['Axiom']),
     'the fact 2^-149 = 2 * 2^-150, b149, is an Axiom of Core.v (the same text, its proof removed), used by the top '
     'theorem through arg_rel and core_abs'),
    ('other-statement', 'g identity', T, OTHER,
     ('fails', 'Identity', 'has type "Sincos32.SINCOS32_ALL"'),
     'Sincos32.v states, under the name SINCOS32_ALL, the proposition True and proves that'),
    ('guard', 'h guard', T, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'sincos32_all from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = {f: raw(f).decode('utf-8').split('\n') for f in (R, C, T)}
    for pin, (f, n, text) in sorted(PINS.items()):
        if n > len(lines[f]) or text not in lines[f][n - 1]:
            raise Stop('%s line %d does not hold %r (pin %s)' % (f, n, text, pin))

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
    L = ['{"name": %s, "tier": "flocq4", "deps": %s,' % (d(NAME), d(DEPS)),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {', '  "sincos32/Graph.v": %s,' % d(['sincos32/emit_sincos32.py', 'coq', '-']),
         '  "sincos32/gate.json": %s,' % d([ME, 'json'])]
    L += ['  %s: %s%s' % (d(FOLDER + '/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
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
                print('wrote sincos32/%s %s' % (path, hashlib.sha256(b).hexdigest()))
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
