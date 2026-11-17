# R4 (d): writes the refutation modules of the planted statements into stage/ (refuses to overwrite) and the label
# table labels.json. Standard library only. Run from the workspace root:
#   python -B ext-work/harden-r4/plants/gen_refute.py
# For each statement plant: stage/<tag>/S.v is the planted statement file of the gate (a shape plant cut before its
# first eq_refl tie, which is where the gate refuses it), and stage/<tag>/Refute.v proves, by kernel conversion and
# vm_compute only, the negation of the planted claim at a witness. The proofs use the frozen candidates' own theorems.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
ROOT = os.getcwd()
MI = os.path.join(ROOT, 'mkf-ext', 'sincos32i', 'plants')
MZ = os.path.join(ROOT, 'mkf-ext', 'sincos32z', 'plants')
ST = os.path.join(ROOT, 'ext-work', 'harden-r4', 'plants', 'stage')

HEAD_I = '''From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
'''
HEAD_Z = '''From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From R4PL Require Import R4Lib.
'''
W = {'0': ('0', '0'), 'quarter': ('1', '(-2)'), 'mquarter': ('(-1)', '(-2)'), 'half': ('1', '(-1)'),
     'mhalf': ('(-1)', '(-1)'), 'm3quarter': ('(-3)', '(-2)'), 'smallest': ('1', '(-149)'), 'p2_23': ('1', '23'),
     'BFEFE800': ('(-15722496)', '(-23)')}
WTXT = {'0': '0 (00000000)', 'quarter': '1/4 (3E800000)', 'mquarter': '-1/4 (BE800000)', 'half': '1/2 (3F000000)',
        'mhalf': '-1/2 (BF000000)', 'm3quarter': '-3/4 (BF400000)', 'smallest': '2^-149 (00000001)',
        'p2_23': '2^23 (4B000000)', 'BFEFE800': '-15722496 * 2^-23 (BFEFE800)', 'nan': 'NaN', 'pinf': '+infinity'}
ZL = {'half': 'sin_at_half', 'mhalf': 'sin_at_minus_half', 'quarter': 'cos_at_quarter',
      'm3quarter': 'cos_at_minus_three_quarters'}

def value_proof(fn, w):
    m, e = W[w]
    return f'''Proof.
  intro H.
  destruct (num_f32 {m} {e} false ltac:(vm_compute; reflexivity) ltac:(lia)) as [Fw Pw].
  destruct (H (num {m} {e} false) Fw Pw) as [HF HP].
  destruct (IEEE_{fn.upper()}TURN32_proof (num {m} {e} false) Fw Pw) as [FF EF].
  first [ (vm_compute in HF; discriminate HF)
        | (apply (differ _ _ HF FF); [ intro C; vm_compute in C; discriminate C | rewrite HP, EF; reflexivity ]) ].
Qed.
'''

PLANTS = []   # (tag, folder, plant file, kind, data)
for name, fn, w in [('shape_arg_4', 'cos', '0'), ('shape_c_no_abs', 'sin', 'BFEFE800'), ('shape_cos_big_0', 'cos', 'p2_23'),
                    ('shape_n_add', 'sin', '0'), ('shape_narrow_add', 'sin', 'smallest'), ('shape_poly_swap', 'cos', '0'),
                    ('shape_q_1f', 'sin', 'quarter'), ('shape_sin_sel_k1', 'sin', 'quarter'),
                    ('shape_sinturn_no_narrow', 'sin', 'quarter')]:
    PLANTS.append(('i_' + name, 'i', 'SINCOS32_IEEE_Statement_%s.v' % name, 'shape', (fn, w)))
for name, fn, w in [('ieee_sub_is_add', 'sin', '0'), ('ieee_neg_is_abs', 'sin', 'mquarter'), ('ieee_sel_le_is_lt', 'sin', '0')]:
    PLANTS.append(('i_' + name, 'i', 'SINCOS32_IEEE_Statement_%s.v' % name, 'op', (fn, w)))
for name, k in [('cst_0_ulp', 'K_0'), ('cst_1_ulp', 'K_1'), ('cst_110_ulp', 'K_110'), ('cst_156_ulp', 'K_156'),
                ('cst_20_ulp', 'K_20'), ('cst_210_ulp', 'K_210'), ('cst_4_ulp', 'K_4'), ('cst_42_ulp', 'K_42'),
                ('cst_6_ulp', 'K_6'), ('cst_72_ulp', 'K_72'), ('cst_BIG_2p22', 'K_BIG'), ('cst_BIG_ulp', 'K_BIG'),
                ('cst_CN_odd', 'K_CN'), ('cst_CN_ulp', 'K_CN'), ('cst_HH_ulp', 'K_HH'), ('cst_KK_ulp', 'K_KK'),
                ('cst_MM_ulp', 'K_MM'), ('cst_PH_ulp', 'K_PH'), ('cst_TT_ulp', 'K_TT')]:
    PLANTS.append(('i_' + name, 'i', 'SINCOS32_IEEE_Statement_%s.v' % name, 'cst', k))
PLANTS.append(('i_prem_sin_no_finite', 'i', 'SINCOS32_IEEE_Statement_prem_sin_no_finite.v', 'prem_nan', None))
PLANTS.append(('i_concl_cos_is_sin', 'i', 'SINCOS32_IEEE_Statement_concl_cos_is_sin.v', 'concl_zero', None))
PLANTS.append(('i_core_bound_2p200', 'i', None, 'core_bound', None))
for name, part, w in [('sin_step_none', 'SIN', 'half'), ('sin_step_abs', 'SIN', 'mhalf'), ('zero_sin_opposite', 'SIN', 'half'),
                      ('zero_sin_plus', 'SIN', 'mhalf'), ('cos_step_none', 'COS', 'quarter'), ('cos_step_sub', 'COS', 'quarter'),
                      ('cos_step_no_abs', 'COS', 'm3quarter'), ('zero_cos_minus', 'COS', 'quarter')]:
    PLANTS.append(('z_' + name, 'z', 'SINCOS32_IEEE_Zero_Statement_%s.v' % name, 'zero', (part, w)))
PLANTS.append(('z_zero_sin_no_finite', 'z', 'SINCOS32_IEEE_Zero_Statement_zero_sin_no_finite.v', 'zero_nan', None))
PLANTS.append(('z_value_cos_is_sin', 'z', 'SINCOS32_IEEE_Zero_Statement_value_cos_is_sin.v', 'value_zero', None))
PLANTS.append(('z_nonfinite_cos_unstepped', 'z', 'SINCOS32_IEEE_Zero_Statement_nonfinite_cos_unstepped.v', 'nonfinite_inf', None))

def refute_text(tag, folder, kind, data):
    head = HEAD_I if folder == 'i' else HEAD_Z
    imp = '' if kind == 'core_bound' else 'From R4PL.%s Require S.\n' % tag
    if kind == 'shape':
        fn, w = data
        return head + imp + f'''
(* The planted claim IEEE_{fn.upper()}TURN32, written with the planted shape (the planted statement file is cut before
   its first eq_refl tie, where the gate refuses it). Refuted at {WTXT[w]}. *)
Definition PLANTED : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (S.T_{fn}turn32 b64 S.tieee_ops b) = true /\\
  B2R (S.T_{fn}turn32 b64 S.tieee_ops b) = g_{fn}turn32 (B2R b).

Theorem refuted : ~ PLANTED.
''' + value_proof(fn, w), f'the planted IEEE_{fn.upper()}TURN32 (planted shape), at {WTXT[w]}'
    if kind == 'op':
        fn, w = data
        return head + imp + f'''
(* The planted statement's own IEEE_{fn.upper()}TURN32 (its record of operations is the planted one). Refuted at
   {WTXT[w]}. *)
Theorem refuted : ~ S.IEEE_{fn.upper()}TURN32.
''' + value_proof(fn, w), f'the planted statement\'s IEEE_{fn.upper()}TURN32, at {WTXT[w]}'
    if kind == 'cst':
        return head + imp + f'''
(* The planted statement's own IEEE_TCST, at the planted constant {data}. *)
Theorem refuted : ~ S.IEEE_TCST.
Proof.
  intro H. destruct (H S.{data}) as [HF HP]. destruct (IEEE_TCST_proof {data}) as [FF EF].
  apply (differ _ _ HF FF).
  - intro C. vm_compute in C. discriminate C.
  - rewrite HP, EF. reflexivity.
Qed.
''', f'the planted statement\'s IEEE_TCST, at {data}'
    if kind == 'prem_nan':
        return head + imp + '''
(* The planted statement's own IEEE_SINTURN32 (no premise that the input is finite), at NaN. *)
Theorem refuted : ~ S.IEEE_SINTURN32.
Proof.
  intro H. destruct (H (@B754_nan 53 1024) f32_nan) as [HF _]. vm_compute in HF. discriminate HF.
Qed.
''', 'the planted statement\'s IEEE_SINTURN32, at NaN'
    if kind == 'concl_zero':
        return head + imp + '''
(* The planted statement's own IEEE_COSTURN32 (its conclusion names the sine graph), at 0. *)
Theorem refuted : ~ S.IEEE_COSTURN32.
Proof.
  intro H. destruct (H (@B754_zero 53 1024 false) eq_refl f32_zero) as [HF HP].
  assert (G : g_sinturn32 (B2R (@B754_zero 53 1024 false)) = 0).
  { simpl B2R. destruct (sinturn32_exact 0 0%Z ltac:(apply generic_format_0)) as [Z0 _]. apply Z0. simpl. ring. }
  rewrite G in HP.
  apply (differ (S.T_costurn32 b64 S.tieee_ops (@B754_zero 53 1024 false)) (@B754_zero 53 1024 false) HF eq_refl).
  - intro C. vm_compute in C. discriminate C.
  - rewrite HP. reflexivity.
Qed.
''', 'the planted statement\'s IEEE_COSTURN32, at 0'
    if kind == 'core_bound':
        return head + '''
(* The planted lemma of TOps_core_bound_2p200.v, restated (that planted file is refused while its proof is checked):
   core_den with the bound 2^200 in place of 2^62. Refuted at V = 2^200, where the core is not finite. *)
Definition PLANTED_LEMMA : Prop :=
  forall (V : b64) (v : R), den V v 200 -> den (T_core b64 tieee_ops V) (turn_core v) 952.

Theorem refuted : ~ PLANTED_LEMMA.
Proof.
  intro H.
  destruct (num_exact 1 200 false ltac:(vm_compute; reflexivity) ltac:(lia)) as [F E].
  assert (D : den (num 1 200 false) (IZR 1 * bpow radix2 200) 200).
  { split; [exact F | split; [exact E |]].
    rewrite Rabs_pos_eq by (apply Rmult_le_pos; [simpl; lra | apply bpow_ge_0]). simpl IZR. lra. }
  destruct (H _ _ D) as [HF _]. vm_compute in HF. discriminate HF.
Qed.
''', 'the planted lemma core_den (bound 2^200), at V = 2^200'
    if kind == 'zero':
        part, w = data; m, e = W[w]
        return head + imp + f'''
(* The planted statement's own Z_{part}_ZERO, at {WTXT[w]}. *)
Theorem refuted : ~ S.Z_{part}_ZERO.
Proof.
  intro H.
  destruct (num_f32 {m} {e} false ltac:(vm_compute; reflexivity) ltac:(lia)) as [Fw Pw].
  pose proof (H (num {m} {e} false) Fw Pw) as Hw.
  rewrite (num_value {m} {e} false ltac:(vm_compute; reflexivity) ltac:(lia)) in Hw.
  specialize (Hw {ZL[w]}). vm_compute in Hw. discriminate Hw.
Qed.
''', f'the planted statement\'s Z_{part}_ZERO, at {WTXT[w]}'
    if kind == 'zero_nan':
        return head + imp + '''
(* The planted statement's own Z_SIN_ZERO (no premise that the input is finite), at NaN. *)
Theorem refuted : ~ S.Z_SIN_ZERO.
Proof.
  intro H. pose proof (H (@B754_nan 53 1024) f32_nan) as Hw.
  assert (Z0 : sin (2 * PI * B2R (@B754_nan 53 1024)) = 0) by (simpl B2R; rewrite Rmult_0_r; apply sin_0).
  specialize (Hw Z0). vm_compute in Hw. discriminate Hw.
Qed.
''', 'the planted statement\'s Z_SIN_ZERO, at NaN'
    if kind == 'value_zero':
        return head + imp + '''
(* The planted statement's own Z_COS_VALUE (its conclusion names the sine graph), at 0. *)
Theorem refuted : ~ S.Z_COS_VALUE.
Proof.
  intro H. destruct (H (@B754_zero 53 1024 false) eq_refl f32_zero) as [HF HP].
  assert (G : g_sinturn32 (B2R (@B754_zero 53 1024 false)) = 0).
  { simpl B2R. destruct (sinturn32_exact 0 0%Z ltac:(apply generic_format_0)) as [Z0 _]. apply Z0. simpl. ring. }
  rewrite G in HP.
  apply (differ (S.Z_costurn32 b64 tieee_ops (@B754_zero 53 1024 false)) (@B754_zero 53 1024 false) HF eq_refl).
  - intro C. vm_compute in C. discriminate C.
  - rewrite HP. reflexivity.
Qed.
''', 'the planted statement\'s Z_COS_VALUE, at 0'
    if kind == 'nonfinite_inf':
        return head + imp + '''
(* The planted statement's own Z_COS_NONFINITE (claimed of the unstepped cosine), at +infinity. *)
Theorem refuted : ~ S.Z_COS_NONFINITE.
Proof.
  intro H. pose proof (H (@B754_infinity 53 1024 false) eq_refl) as Hw. vm_compute in Hw. discriminate Hw.
Qed.
''', 'the planted statement\'s Z_COS_NONFINITE, at +infinity'
    raise SystemExit('unknown kind ' + kind)

def main():
    out, labels = [], []
    for tag, folder, pf, kind, data in PLANTS:
        d = os.path.join(ST, tag)
        if os.path.exists(d): sys.exit('gen_refute: %s exists' % d)
        os.makedirs(d)
        src_sha = cut_sha = None
        if pf:
            b = open(os.path.join(MI if folder == 'i' else MZ, pf), 'rb').read(); src_sha = hashlib.sha256(b).hexdigest()
            if kind == 'shape':
                t = b.decode('utf-8'); k = t.index('\nDefinition T_narrow_model'); b = (t[:k + 1]).encode('utf-8')
            cut_sha = hashlib.sha256(b).hexdigest()
            with open(os.path.join(d, 'S.v'), 'wb') as f: f.write(b)
        text, what = refute_text(tag, folder, kind, data)
        with open(os.path.join(d, 'Refute.v'), 'wb') as f: f.write(text.encode('ascii'))
        labels.append({'tag': tag, 'folder': 'sincos32' + folder, 'plant_file': pf, 'plant_sha256': src_sha,
                       'staged_S_sha256': cut_sha, 'cut_before_ties': kind == 'shape', 'label': 'refuted in Coq',
                       'refuted': what, 'theorem': 'R4PL.%s.Refute.refuted' % tag})
        out.append(tag)
    chk = 'From R4PL Require ' + ' '.join('%s.Refute' % t for t in out) + '.\n'
    chk += ''.join('Print Assumptions R4PL.%s.Refute.refuted.\n' % t for t in out)
    p = os.path.join(ST, 'Check.v')
    if os.path.exists(p): sys.exit('gen_refute: Check.v exists')
    with open(p, 'w') as f: f.write(chk)
    with open(os.path.join(ST, 'order.txt'), 'w') as f: f.write('\n'.join(out) + '\n')
    with open(os.path.join(ST, 'labels-refuted.json'), 'w') as f: json.dump(labels, f, indent=1)
    print('wrote %d refutation modules' % len(out))

if __name__ == '__main__':
    main()
