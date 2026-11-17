# The plants of sincos32i's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B sincos32i/plants/make_plants.py json          prints gate.json
#   python3 -B sincos32i/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B sincos32i/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B sincos32i/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B sincos32i/plants/make_plants.py list          one line per plant
# The form is sincos32/plants/make_plants.py's and ieee64/plants/make_plants.py's. A plant is one source of the
# folder with ONE change (two places of one line group for core-bound-2p200; the whole of Closed.v for two-of-three
# and guard), put in place of that source; the gate must refuse it for the reason its entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line is held to
# that line's text here: if a source moves, this script stops and says where.
#
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement is refused where the statement file's own eq_refl definitions or the proof script no longer fit it.
# That is not a proof that the changed statement is false. Each entry's "what" says which are KNOWN FALSE and how,
# and which are only refused by the route of the proof (ROUTE ONLY). Nothing here is an equivalent mutant counted
# as caught; the ROUTE ONLY plants are listed as such.
#
# WITNESSES. MEASURED means ext-work/sincos32-ieee/stage/runs/measure-plants-run1.txt (measure_plants.py, by the
# assistant, this host's Python floats in the manner of zero-sign/measure_zero.py: the frozen shape transcribed,
# compared bit for bit with measure_zero.py's own transcription on 81,686 binary32 inputs, and the plant's one
# change applied). "frozen" is the frozen shape's result; that its real number is the graph's value is
# SINCOS32_IEEE itself, proved by this folder. That the Python evaluation is the Coq term is argued (the same
# operations in the same order), not shown.
#   a shape  the planted shape is not the graph: Coq refuses the planted statement file itself, at the eq_refl
#            definition that holds that shape to its graph. Besides, MEASURED at one input, planted / frozen:
#     shape-narrow-add         sin at 00000001 (2^-149): 39F8000000000003 (about 1.89e-29) / 36C8000000000000
#     shape-n-add              sin at 00000000 (0): about -6.1e232 / 0
#     shape-q-1f               sin at 3E800000 (1/4): 0.3826834261417389 / 1
#     shape-arg-4              cos at 00000000 (0): -0.7568486332893372 / 1
#     shape-poly-swap          cos at 00000000 (0): 1.000001072883606 / 1
#     shape-c-no-abs           sin at BFEFE800 (-1.874267578125): 3FE6BB36E0000000 / 3FE6BB3700000000
#     shape-sin-sel-k1         sin at 3E800000 (1/4): +0 / 1
#     shape-cos-big-0          cos at 4B000000 (2^23): +0 / 1
#     shape-sinturn-no-narrow  sin at 3E800000 (1/4): 3FEFFFFFFFFF2C12 (not a binary32 number) / 1
#   b constant  the planted IEEE constant is another real number than the graph's constant, so the planted
#            statement's own part IEEE_TCST is KNOWN FALSE by exact arithmetic (MEASURED with Python rationals:
#            planted - graph is 2^e of the last place, or -1 for cst-CN-odd, or -2^22 for cst-BIG-2p22). Whether a
#            FUNCTION result changes is another question: MEASURED on the 81,686 sampled inputs, only cst-4-ulp
#            (cos at 3E800000: -3.49e-16 / -0) and cst-BIG-2p22 (cos at 4A800001, 4194304.5: 1 / -1) change one;
#            for the other seventeen no sampled input gives another real number (the narrowing to binary32 hides
#            a last-place change almost everywhere).
#   c premise, d conclusion, i IEEE operation, e proof: each entry's "what".
# The row that holds the statement itself is the gate's hash row (frozen inputs unchanged), not a plant.
# WHAT THE GATE CANNOT EXPRESS HERE: a dependency on some files of a folder only. "deps" names whole folders, so
# ieee64 comes with its exp32 half (EXP32_IEEE.v) and therefore exp32 and exp32r, which nothing in this folder uses.
# The gate is gate/gate4.py alone, run on the tree that holds this folder: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = 'ebe0da2cef1d7c648d878149470162aa5d31ae770afa58ce111fea5bde456d77'
NAME = 'SINCOS32_IEEE'; FOLDER = 'sincos32i'
DEPS = ['f32', 'p32', 'p32r', 'exp32', 'exp32r', 'ieee64', 'sin32', 'cos32', 'sincos32']
FILES = ['SINCOS32_IEEE_Statement.v', 'TOps.v', 'Sincos32_IEEE.v', 'Closed.v', 'Identity.v']
S, O, P, C = 'SINCOS32_IEEE_Statement.v', 'TOps.v', 'Sincos32_IEEE.v', 'Closed.v'
ME = 'sincos32i/plants/make_plants.py'

# Lines that a refusal is pinned to: (file, line, text that line of the UNPLANTED source must hold).
PINS = {
    # the statement file's own definitions that hold a shape to its graph
    'm-narrow': (S, 187, 'Definition T_narrow_model : forall v : R, T_narrow R tmodel_ops v = narrow v'),
    'm-N': (S, 188, 'Definition T_N_model : forall v : R, T_N R tmodel_ops v = turn_N v'),
    'm-q': (S, 190, 'Definition T_q_model : forall x : R, T_q R tmodel_ops x = turn_q x'),
    'm-arg': (S, 193, 'Definition T_arg_model : forall v : R, T_arg R tmodel_ops v = turn_arg v'),
    'm-poly': (S, 195, 'Definition T_poly_model : forall u : R, T_poly R tmodel_ops u = sin32_poly u'),
    'm-C': (S, 204, 'Definition T_C_model : forall x : R, T_C R tmodel_ops x = turn_C x := fun x => eq_refl'),
    'm-sinpre': (S, 213, '  fun x => eq_refl'),
    'm-cospre': (S, 227, '  fun x => eq_refl'),
    'm-sinturn': (S, 241, '  fun x => eq_refl'),
    # TOps.v: tcst_ok, one line per constant, and the operation lemmas
    'cst-KK': (O, 160, 'apply (b2r_whole false _ 23 _ 536870913)'),
    'cst-MM': (O, 161, 'rewrite (b2r_fin false _ (-149) _ 3 51)'),
    'cst-TT': (O, 162, 'rewrite (b2r_fin false _ (-178) _ 1 52)'),
    'cst-HH': (O, 163, 'rewrite (b2r_fin false _ (-202) _ 1 52)'),
    'cst-0': (O, 164, '  - reflexivity.'),
    'cst-1': (O, 165, 'apply (b2r_whole false _ 52 _ 1)'),
    'cst-4': (O, 166, 'apply (b2r_whole false _ 50 _ 4)'),
    'cst-CN': (O, 167, 'apply (b2r_whole false _ 0 _ 6755399441055744)'),
    'cst-BIG': (O, 168, 'apply (b2r_whole false _ 29 _ 8388608)'),
    'cst-PH': (O, 169, 'rewrite (b2r_fin false _ (-52) _ 7074237752028440 0)'),
    'cst-6': (O, 171, 'apply (b2r_whole false _ 50 _ 6)'),
    'cst-20': (O, 172, 'apply (b2r_whole false _ 48 _ 20)'),
    'cst-42': (O, 173, 'apply (b2r_whole false _ 47 _ 42)'),
    'cst-72': (O, 174, 'apply (b2r_whole false _ 46 _ 72)'),
    'cst-110': (O, 175, 'apply (b2r_whole false _ 46 _ 110)'),
    'cst-156': (O, 176, 'apply (b2r_whole false _ 45 _ 156)'),
    'cst-210': (O, 177, 'apply (b2r_whole false _ 45 _ 210)'),
    'op-sub': (O, 60, '  intros (H1 & H2 & _). split; [exact H2 | exact H1].'),
    'op-mul': (O, 73, '  intros (H1 & H2 & _). split; [exact H2 | exact H1].'),
    'op-neg': (O, 97, 'Proof. exact (B2R_Bopp 53 1024 x). Qed.'),
    'op-sel-le': (O, 107, '  rewrite (Bleb_correct 53 1024 a b Fa Fb).'),
    'core-arg': (O, 391, 'exact (den_mul V (t_cst tieee_ops K_PH) v cos32_PH 62 1 63 HV den_PH ltac:(lia) ltac:(lia)). }'),
    # Sincos32_IEEE.v
    'sin-intros': (P, 172, '  unfold IEEE_SINTURN32. intros b Fb Hf.'),
    'cos-intros': (P, 183, '  unfold IEEE_COSTURN32. intros b Fb Hf.'),
    'sin-finite': (P, 176, 'exact (proj1 (sincos32_finite (B2R b) Hf)). }'),
    'cos-last': (P, 189, '  split; [exact Fn |]. rewrite Vn, Vp. reflexivity.'),
}
def at(pin): return 'sincos32i/%s", line %d, characters' % (PINS[pin][0], PINS[pin][1])

def shape(name, old, new, pin, what):
    return (name, 'a shape', S, [(old, new)], ('fails', S[:-2], at(pin)), what)
def cst(name, key, old, new, what, effect):
    return ('cst-%s' % name, 'b constant', S, [(old, new)], ('fails', 'TOps', at('cst-' + key)),
            'the IEEE constant %s. KNOWN FALSE in the planted statement\'s own part IEEE_TCST, by exact arithmetic '
            '(MEASURED). %s. Refused at that constant\'s line of tcst_ok' % (what, effect))
NOFN = 'A function result: MEASURED, no input of the 81,686 sampled gives another real number'
def up(key, m, e, graph):
    ex = e if e == '0' else '(%s)' % e
    old = '| K_%s => @B754_finite 53 1024 false %s %s eq_refl' % (key, m, ex)
    inner = m[1:-1] if m.startswith('(') else m
    new = '| K_%s => @B754_finite 53 1024 false (%s + 1) %s eq_refl' % (key, inner, ex)
    eff = NOFN if key != '4' else ('A function result too: MEASURED, cos at x = 1/4 (3E800000) gives about -3.49e-16 '
                                   'where the frozen shape gives a zero')
    return cst('%s-ulp' % key, key, old, new,
               '%s is one unit in the last place above it (mantissa + 1; planted - graph = 2^%s)' % (graph, e), eff)

TWO_OF_THREE = '''(* Plant: under the name SINCOS32_IEEE, a statement of two of the three parts (IEEE_TCST left out), and its
   proof. The identity must refuse a theorem of another statement that carries the statement's name. *)
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
Definition SINCOS32_IEEE : Prop := IEEE_SINTURN32 /\\ IEEE_COSTURN32.
Theorem sincos32_ieee_holds : SINCOS32_IEEE.
Proof. exact (conj IEEE_SINTURN32_proof IEEE_COSTURN32_proof). Qed.
'''
GUARD = '''(* Plant: SINCOS32_IEEE from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_ieee_holds : SINCOS32_IEEE.
Proof. exact (False_ind _ (loop 0)). Qed.
'''
SIN_PREM = ('  forall b : b64, is_finite b = true -> format32 (B2R b) ->\n'
            '  is_finite (T_sinturn32 b64 tieee_ops b) = true /\\')
COS_PREM = ('  forall b : b64, is_finite b = true -> format32 (B2R b) ->\n'
            '  is_finite (T_costurn32 b64 tieee_ops b) = true /\\')
TCST_HEAD = 'Lemma tcst_ok : forall c : tconst,\n'
TCST_AXIOM = ('Axiom tcst_ok : forall c : tconst,\n'
              '  is_finite (t_cst tieee_ops c) = true /\\ B2R (t_cst tieee_ops c) = t_cst tmodel_ops c.\n\n')

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) one operation, operand or selected value changed in a shape: the statement file itself is refused
    shape('shape-narrow-add', '(t_sub o (t_add o v (t_cst o K_MM)) (t_cst o K_MM))', '(t_add o (t_add o v (t_cst o K_MM)) (t_cst o K_MM))',
          'm-narrow', 'narrow\'s shape: (v + MM) + MM for (v + MM) - MM. Not the graph (MEASURED: sin at x = 2^-149 (00000001) would give about 1.89e-29 for 2^-149): the statement file is refused at T_narrow_model'),
    shape('shape-n-add', 'T := t_sub o (t_add o v (t_cst o K_CN)) (t_cst o K_CN).', 'T := t_add o (t_add o v (t_cst o K_CN)) (t_cst o K_CN).',
          'm-N', 'the rounding to a whole number: (v + CN) + CN for (v + CN) - CN. Not the graph (MEASURED: sin at x = 0 (00000000) would give about -6.1e232 for 0): the statement file is refused at T_N_model'),
    shape('shape-q-1f', 't_mul o (t_cst o K_4) (T_f T o x).', 't_mul o (t_cst o K_1) (T_f T o x).',
          'm-q', 'q = 1 * f for 4 * f. Not the graph (MEASURED: sin at x = 1/4 (3E800000) would give 0.38268 for 1): the statement file is refused at T_q_model'),
    shape('shape-arg-4', 't_mul o v (t_cst o K_PH).', 't_mul o v (t_cst o K_4).',
          'm-arg', 'the argument is v * 4 for v * PH. Not the graph (MEASURED: cos at x = 0 would give -0.75685 for 1): the statement file is refused at T_arg_model'),
    shape('shape-poly-swap', '(t_cst o K_156)))) (t_cst o K_110))))', '(t_cst o K_110)))) (t_cst o K_156))))',
          'm-poly', 'the polynomial\'s divisors 156 and 110 in each other\'s place. Not the graph (MEASURED: cos at x = 0 would give 1.000001072883606 for 1): the statement file is refused at T_poly_model'),
    shape('shape-c-no-abs', 'T_core T o (t_sub o (t_cst o K_1) (t_abs o (T_r T o x))).', 'T_core T o (t_sub o (t_cst o K_1) (T_r T o x)).',
          'm-C', 'C = core (1 - r) for core (1 - |r|). Not the graph (MEASURED: sin at x = BFEFE800 would give 3FE6BB36E0000000 for 3FE6BB3700000000): the statement file is refused at T_C_model'),
    shape('shape-sin-sel-k1', '(t_sel_le o (t_cst o K_0) (T_k T o x) (T_C T o x) (t_neg o (T_C T o x)))', '(t_sel_le o (t_cst o K_0) (T_k T o x) (T_S T o x) (t_neg o (T_C T o x)))',
          'm-sinpre', 'the sine\'s selection for k = 1 takes S for C. Not the graph (MEASURED: sin at x = 1/4 (3E800000) would give 0 for 1): the statement file is refused at T_sinpre_model'),
    shape('shape-cos-big-0', 't_sel_le o (t_cst o K_BIG) (t_abs o x) (t_cst o K_1)', 't_sel_le o (t_cst o K_BIG) (t_abs o x) (t_cst o K_0)',
          'm-cospre', 'the cosine of a large input is the constant 0 for 1. Not the graph (MEASURED: cos at x = 2^23 (4B000000) would give 0 for 1): the statement file is refused at T_cospre_model'),
    shape('shape-sinturn-no-narrow', 'T := T_narrow T o (T_sinpre T o x).', 'T := T_sinpre T o x.',
          'm-sinturn', 'sinturn32\'s shape without narrow. Not the graph (MEASURED: sin at x = 1/4 (3E800000) would give 3FEFFFFFFFFF2C12, not a binary32 number, for 1): the statement file is refused at T_sinturn32_model'),
    # (b) one IEEE constant off: tcst_ok (IEEE_TCST's proof, which every walk uses) must fail at that constant
    up('KK', '(536870913 * 2 ^ 23)', '-23', 'KK'),
    up('MM', '(3 * 2 ^ 51)', '-149', 'MM'),
    up('TT', '(2 ^ 52)', '-178', 'TT'),
    up('HH', '(2 ^ 52)', '-202', 'HH'),
    cst('0-ulp', '0', '| K_0 => @B754_zero 53 1024 false', '| K_0 => @B754_finite 53 1024 false 1 (-1074) eq_refl',
        '0 is the least positive binary64 number, 2^-1074', NOFN),
    up('1', '(2 ^ 52)', '-52', '1'),
    up('4', '(2 ^ 52)', '-50', '4'),
    up('CN', '(3 * 2 ^ 51)', '0', 'CN'),
    up('BIG', '(2 ^ 52)', '-29', 'BIG'),
    up('PH', '7074237752028440', '-52', 'PH'),
    up('6', '(6 * 2 ^ 50)', '-50', '6'),
    up('20', '(20 * 2 ^ 48)', '-48', '20'),
    up('42', '(42 * 2 ^ 47)', '-47', '42'),
    up('72', '(72 * 2 ^ 46)', '-46', '72'),
    up('110', '(110 * 2 ^ 46)', '-46', '110'),
    up('156', '(156 * 2 ^ 45)', '-45', '156'),
    up('210', '(210 * 2 ^ 45)', '-45', '210'),
    cst('CN-odd', 'CN', '| K_CN => @B754_finite 53 1024 false (3 * 2 ^ 51) 0 eq_refl', '| K_CN => @B754_finite 53 1024 false (3 * 2 ^ 51 - 1) 0 eq_refl',
        'CN is one smaller, the odd number 6755399441055743 (planted - graph = -1)', NOFN),
    cst('BIG-2p22', 'BIG', '| K_BIG => @B754_finite 53 1024 false (2 ^ 52) (-29) eq_refl', '| K_BIG => @B754_finite 53 1024 false (2 ^ 52) (-30) eq_refl',
        'BIG is 2^22 for 2^23 (planted - graph = -2^22)',
        'A function result too: MEASURED, cos at x = 4194304.5 (4A800001) gives 1 where the frozen shape gives -1'),
    # (i) one IEEE operation of tieee_ops changed
    ('ieee-sub-is-add', 'i IEEE operation', S,
     [('t_sub := @Bminus 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;', 't_sub := @Bplus 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;')],
     ('fails', 'TOps', at('op-sub')),
     'the IEEE subtraction is Flocq\'s addition. KNOWN FALSE, MEASURED: sin at x = 0 (00000000) gives about '
     '-1.35e256 where the frozen shape gives 0. Refused where top_sub takes Flocq\'s lemma for Bminus'),
    ('ieee-mul-toward-zero', 'i IEEE operation', S,
     [('t_mul := @Bmult 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;', 't_mul := @Bmult 53 1024 prec64_gt_0 prec64_lt_emax mode_ZR;')],
     ('fails', 'TOps', at('op-mul')),
     'the IEEE multiplication rounds toward zero, not to nearest even. ROUTE ONLY, NOT known false: MEASURED, no '
     'input of the 81,686 sampled gives another real number (a last-place change before narrow reaches the '
     'binary32 result only beside a rounding boundary). Refused where top_mul takes Flocq\'s lemma at mode_NE'),
    ('ieee-neg-is-abs', 'i IEEE operation', S,
     [('t_neg := @Bopp 53 1024;', 't_neg := @Babs 53 1024;')],
     ('fails', 'TOps', at('op-neg')),
     'the IEEE negation is the absolute value. KNOWN FALSE, MEASURED: sin at x = -1/4 (BE800000) gives 1 where '
     'the frozen shape gives -1. Refused where top_neg_val takes Flocq\'s lemma for Bopp'),
    ('ieee-sel-le-is-lt', 'i IEEE operation', S,
     [('t_sel_le := fun a b c d => if @Bleb 53 1024 a b then c else d;', 't_sel_le := fun a b c d => if @Bltb 53 1024 a b then c else d;')],
     ('fails', 'TOps', at('op-sel-le')),
     'the IEEE selection "a <= b" tests a < b. KNOWN FALSE, MEASURED: sin at x = 0 (00000000) gives -1 where the '
     'frozen shape gives 0. Refused where top_sel_le takes Flocq\'s lemma for Bleb'),
    # (c) a premise dropped
    ('prem-sin-no-finite', 'c premise', S,
     [(SIN_PREM, SIN_PREM.replace('is_finite b = true -> ', ''))],
     ('fails', 'Sincos32_IEEE', at('sin-intros')),
     'IEEE_SINTURN32 for every binary64 value whose real number is a binary32 number, finite or not. KNOWN FALSE, '
     'MEASURED: at NaN (whose real number is 0) the frozen shape gives NaN, which is not finite. Refused where the '
     'proof takes the premise'),
    ('prem-cos-no-format', 'c premise', S,
     [(COS_PREM, COS_PREM.replace('format32 (B2R b) ->', '').replace('true -> \n', 'true ->\n'))],
     ('fails', 'Sincos32_IEEE', at('cos-intros')),
     'IEEE_COSTURN32 for every finite binary64 input, not only binary32 numbers. ROUTE ONLY, NOT known false and '
     'not measurable this way (the IEEE evaluation of the shape IS the model\'s wherever nothing overflows). '
     'Refused where the proof takes the premise, which it uses for the bound before narrow'),
    # (d) a conclusion changed
    ('concl-cos-is-sin', 'd conclusion', S,
     [('B2R (T_costurn32 b64 tieee_ops b) = g_costurn32 (B2R b).', 'B2R (T_costurn32 b64 tieee_ops b) = g_sinturn32 (B2R b).')],
     ('fails', 'Sincos32_IEEE', at('cos-last')),
     'IEEE_COSTURN32 says the cosine\'s shape denotes the SINE graph\'s value. KNOWN FALSE, MEASURED: at x = 0 '
     '(00000000) the cosine shape gives 1 and the sine shape gives 0. Refused at the last step of the proof'),
    # (e) a proof left out, or a proof with a wrong step
    ('admitted-tops', 'e proof', O,
     [('  rewrite Fx.\n  intros (H1 & H2 & _). split; [exact H2 | exact H1].\nQed.\n',
       '  rewrite Fx.\n  intros (H1 & H2 & _). split; [exact H2 | exact H1].\nAdmitted.\n')],
     ('reader', 'TOps.top_div :', ['Admitted']),
     'TOps.top_div (the IEEE division) ends with Admitted'),
    ('admitted-stages', 'e proof', P,
     [('    exact (den_sub _ _ _ _ 0 61 62 den_c1 (den_abs _ _ _ Hr) ltac:(lia) ltac:(lia) ltac:(lia)).\nQed.\n',
       '    exact (den_sub _ _ _ _ 0 61 62 den_c1 (den_abs _ _ _ Hr) ltac:(lia) ltac:(lia) ltac:(lia)).\nAdmitted.\n')],
     ('reader', 'Sincos32_IEEE.stages :', ['Admitted']),
     'Sincos32_IEEE.stages (k, S and C are finite and denote the graph\'s) ends with Admitted'),
    ('admitted-closed', 'e proof', C,
     [('  exact (conj IEEE_SINTURN32_proof (conj IEEE_COSTURN32_proof IEEE_TCST_proof)).\nQed.\n',
       '  exact (conj IEEE_SINTURN32_proof (conj IEEE_COSTURN32_proof IEEE_TCST_proof)).\nAdmitted.\n')],
     ('reader', 'Closed.sincos32_ieee_holds :', ['Admitted']),
     'the top theorem sincos32_ieee_holds ends with Admitted'),
    ('core-bound-2p200', 'e proof', O,
     [('den V v 62 -> den (T_core', 'den V v 200 -> den (T_core'), ('62 1 63 HV den_PH', '200 1 63 HV den_PH')],
     ('fails', 'TOps', at('core-arg')),
     'core_den is stated for |v| <= 2^200 for 2^62, and its first step is given that bound. The lemma so stated '
     'is KNOWN FALSE, MEASURED: T_core at v = 2^200 is -infinity, not finite. Refused where the product v * PH no '
     'longer fits below 2^63'),
    ('no-finite-fact', 'e proof', P,
     [('exact (proj1 (sincos32_finite (B2R b) Hf)). }', 'exact (eq_refl 1). }')],
     ('fails', 'Sincos32_IEEE', at('sin-finite')),
     'the proof of IEEE_SINTURN32 gives 1 = 1 where it must give that the graph\'s result is a finite binary32 '
     'number (SINCOS32_FINITE). A wrong step of the proof, the statement unchanged: refused at that step'),
    # (f) an assumption put in
    ('tcst-axiom', 'f axiom', O,
     [('cut', TCST_HEAD, 'Theorem IEEE_TCST_proof : IEEE_TCST.', TCST_AXIOM)],
     ('reader', 'TOps.tcst_ok :', ['Axiom']),
     'tcst_ok (every IEEE constant is finite and denotes the graph\'s) is an Axiom of TOps.v (the same text, its '
     'proof removed), used by the top theorem through IEEE_TCST_proof and every walk'),
    # (g) another statement under the name, (h) a check switched off
    ('two-of-three', 'g identity', C, TWO_OF_THREE,
     ('fails', 'Identity', 'has type "Closed.SINCOS32_IEEE"'),
     'Closed.v states, under the name SINCOS32_IEEE, two of the three parts (IEEE_TCST left out) and proves that'),
    ('guard', 'h guard', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'sincos32_ieee_holds from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = {f: raw(f).decode('utf-8').split('\n') for f in (S, O, P)}
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
                print('%-26s %-18s %-28s %s' % (name, cls, src, what))
        else:
            print('usage: make_plants.py json | plant NAME | write | check | list'); return 2
    except Stop as e:
        sys.stderr.write('make_plants: %s\n' % e); return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
