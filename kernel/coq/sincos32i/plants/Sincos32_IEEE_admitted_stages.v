(* Proofs of IEEE_SINTURN32 and IEEE_COSTURN32 (statements in SINCOS32_IEEE_Statement.v, which this file does not
   change). Flocq and the standard library only; every lemma ends with Qed and nothing is assumed. Author: the
   assistant (2026-11-16). A scratch candidate.

   How it goes, for a finite binary64 b whose real number x is a binary32 number.
     The outer selection compares the constant 2^23 with |b|: both finite, so IEEE chooses as the model does
     (TOps.top_sel_le_at).
       2^23 <= |x|   The selected value is b * 0 (sine: finite, real number RN64 (x * 0) = 0) or the constant 1
                     (cosine). NOTHING is said or needed of the reduction, of k, S or C in this branch: they are
                     in the branch the selection does not return, and a Coq "if" does not look at it. (Whether
                     they are finite there is not examined here and the statement does not ask it.)
       |x| < 2^23    Every operation is walked once with its den_* lemma of TOps.v, carrying a crude bound:
                       N x <= 2^55, f <= 2^56, q <= 2^58, k <= 2^60, r <= 2^61, 1 - |r| <= 2^62,
                       arg <= 2^63, its square <= 2^126, the polynomial <= 2^889, the core <= 2^952 < 2^1024.
                     Only |x| <= 2^23 is used: not that x is a binary32 number, not Reduce.reduce, not that k is
                     one of -2 .. 2. So k, S and C are finite and denote turn_k x, turn_S x, turn_C x; the three
                     inner selections compare |k| with 0, |k| with 1, and 0 with k, all finite, and choose as the
                     model does; the negation is exact.
     narrow          IEEE_TNARROW: T_narrow at a finite v with |v| < OVF32 is finite and denotes narrow v. The
                     proof is ieee64/P32_IEEE.v's IEEE_NARROW_proof with tieee_ops for ieee_ops. Its premise
                     holds of the value before narrow by P32_IEEE.narrow_inv from sincos32's SINCOS32_FINITE
                     (the result is a finite binary32 number) and Sincos32.sin_pre_fmt / cos_pre_fmt. This is
                     the one place the premise format32 x and the theorems about the graph's values are used. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.sin32 Require Import Graph.
From MKF.cos32 Require Import Graph.
From MKF.sincos32 Require Import Graph SINCOS32_Statement Sincos32.
From MKF.ieee64 Require Import IEEE64_Statement Ops P32_IEEE.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps.
Open Scope R_scope.

#[local] Instance s24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance s53 : Prec_gt_0 53 := prec64_gt_0.

(* narrow over TOPS *)

Definition IEEE_TNARROW : Prop :=
  forall v : b64, is_finite v = true -> Rabs (B2R v) < OVF32 ->
  is_finite (T_narrow b64 tieee_ops v) = true /\ B2R (T_narrow b64 tieee_ops v) = narrow (B2R v).

Theorem IEEE_TNARROW_proof : IEEE_TNARROW.
Proof.
  unfold IEEE_TNARROW. intros b Fb Hb.
  unfold T_narrow, narrow.
  assert (Fa : is_finite (t_abs tieee_ops b) = true) by (rewrite top_abs_fin; exact Fb).
  rewrite (top_sel_lt_at (t_abs tieee_ops b) (t_cst tieee_ops K_TT) _ _ (Rabs (B2R b)) TT
             Fa (tcst_fin K_TT) (top_abs_val b) tval_TT).
  rewrite (top_sel_le_at (t_abs tieee_ops b) (t_cst tieee_ops K_HH) _ _ (Rabs (B2R b)) HH
             Fa (tcst_fin K_HH) (top_abs_val b) tval_HH).
  destruct (Rle_dec (Rabs (B2R b)) HH) as [H1 | H1].
  - (* |v| <= HH: v * 0 *)
    apply (top_mul_at b (t_cst tieee_ops K_0) (B2R b) 0 Fb (tcst_fin K_0) eq_refl tval_0).
    rewrite Rmult_0_r. rewrite (round_0 radix2 fexp64 ZnearestE). rewrite Rabs_R0. apply bpow_gt_0.
  - destruct (Rlt_dec (Rabs (B2R b)) TT) as [H2 | H2].
    + (* |v| < TT: (v + MM) - MM *)
      assert (B1 : Rabs (B2R b + MM) <= bpow radix2 (-96)).
      { apply Rabs_le. apply Rabs_lt_inv in H2. unfold MM, TT in *. bnum. lra. }
      destruct (top_add_at b (t_cst tieee_ops K_MM) (B2R b) MM Fb (tcst_fin K_MM) eq_refl tval_MM) as [Fp Vp].
      { apply (rn64_lt_emax _ (-96)); [lia | exact B1]. }
      assert (B2 : Rabs (RN64 (B2R b + MM) - MM) <= bpow radix2 (-95)).
      { apply (rn64_abs_le _ (-96)) in B1; [| lia].
        set (p := RN64 (B2R b + MM)) in *.
        apply Rabs_le. apply Rabs_le_inv in B1. unfold MM in *. bnum. lra. }
      apply (top_sub_at _ (t_cst tieee_ops K_MM) _ MM Fp (tcst_fin K_MM) Vp tval_MM).
      apply (rn64_lt_emax _ (-95)); [lia | exact B2].
    + (* otherwise: c - (c - v) with c = KK * v *)
      assert (B1 : Rabs (KK * B2R b) <= bpow radix2 158).
      { apply Rabs_le. apply Rabs_lt_inv in Hb. unfold KK, OVF32 in *. bnum. lra. }
      destruct (top_mul_at (t_cst tieee_ops K_KK) b KK (B2R b) (tcst_fin K_KK) Fb tval_KK eq_refl) as [Fc Vc].
      { apply (rn64_lt_emax _ 158); [lia | exact B1]. }
      apply (rn64_abs_le _ 158) in B1; [| lia].
      assert (B2 : Rabs (RN64 (KK * B2R b) - B2R b) <= bpow radix2 159).
      { set (c := RN64 (KK * B2R b)) in *.
        apply Rabs_le. apply Rabs_le_inv in B1. apply Rabs_lt_inv in Hb. unfold OVF32 in *. bnum. lra. }
      destruct (top_sub_at _ b _ (B2R b) Fc Fb Vc eq_refl) as [Fd Vd].
      { apply (rn64_lt_emax _ 159); [lia | exact B2]. }
      apply (rn64_abs_le _ 159) in B2; [| lia].
      assert (B3 : Rabs (RN64 (KK * B2R b) - RN64 (RN64 (KK * B2R b) - B2R b)) <= bpow radix2 160).
      { set (c := RN64 (KK * B2R b)) in *. set (d := RN64 (c - B2R b)) in *.
        apply Rabs_le. apply Rabs_le_inv in B1. apply Rabs_le_inv in B2. bnum. lra. }
      apply (top_sub_at _ _ _ _ Fc Fd Vc Vd).
      apply (rn64_lt_emax _ 160); [lia | exact B3].
Qed.

(* The stages, for |x| <= 2^23: k, S and C are finite and denote the graph's. *)
Lemma stages (b : b64) : is_finite b = true -> Rabs (B2R b) <= bpow radix2 23 ->
  den (T_k b64 tieee_ops b) (turn_k (B2R b)) 60 /\
  den (T_S b64 tieee_ops b) (turn_S (B2R b)) 952 /\
  den (T_C b64 tieee_ops b) (turn_C (B2R b)) 952.
Proof.
  intros Fb Hb.
  assert (H0 : den b (B2R b) 23) by (split; [exact Fb | split; [reflexivity | exact Hb]]).
  pose proof (N_den b (B2R b) 23 55 H0 ltac:(lia) ltac:(lia) ltac:(lia)) as HN.
  assert (Hf : den (T_f b64 tieee_ops b) (turn_f (B2R b)) 56).
  { unfold T_f, turn_f. exact (den_sub _ _ _ _ 23 55 56 H0 HN ltac:(lia) ltac:(lia) ltac:(lia)). }
  assert (Hq : den (T_q b64 tieee_ops b) (turn_q (B2R b)) 58).
  { unfold T_q, turn_q. exact (den_mul _ _ _ _ 2 56 58 den_c4 Hf ltac:(lia) ltac:(lia)). }
  assert (Hk : den (T_k b64 tieee_ops b) (turn_k (B2R b)) 60).
  { unfold T_k, turn_k. exact (N_den _ _ 58 60 Hq ltac:(lia) ltac:(lia) ltac:(lia)). }
  assert (Hr : den (T_r b64 tieee_ops b) (turn_r (B2R b)) 61).
  { unfold T_r, turn_r. exact (den_sub _ _ _ _ 58 60 61 Hq Hk ltac:(lia) ltac:(lia) ltac:(lia)). }
  split; [exact Hk | split].
  - unfold T_S, turn_S. apply core_den. exact (den_mono _ _ 61 62 Hr ltac:(lia)).
  - unfold T_C, turn_C. apply core_den.
    exact (den_sub _ _ _ _ 0 61 62 den_c1 (den_abs _ _ _ Hr) ltac:(lia) ltac:(lia) ltac:(lia)).
Admitted.

Lemma small_bound (x : R) : ~ turn_BIG <= Rabs x -> Rabs x <= bpow radix2 23.
Proof. intros H. change (bpow radix2 23) with 8388608. unfold turn_BIG in H. lra. Qed.

(* The value before narrow, sine. *)
Lemma sinpre_ok (b : b64) : is_finite b = true ->
  is_finite (T_sinpre b64 tieee_ops b) = true /\ B2R (T_sinpre b64 tieee_ops b) = sinturn32_pre (B2R b).
Proof.
  intros Fb. unfold T_sinpre, sinturn32_pre.
  assert (Fa : is_finite (t_abs tieee_ops b) = true) by (rewrite top_abs_fin; exact Fb).
  rewrite (top_sel_le_at (t_cst tieee_ops K_BIG) (t_abs tieee_ops b) _ _ turn_BIG (Rabs (B2R b))
             (tcst_fin K_BIG) Fa tval_BIG (top_abs_val b)).
  destruct (Rle_dec turn_BIG (Rabs (B2R b))) as [Hbig | Hsm].
  - apply (top_mul_at b (t_cst tieee_ops K_0) (B2R b) 0 Fb (tcst_fin K_0) eq_refl tval_0).
    rewrite Rmult_0_r. rewrite (round_0 radix2 fexp64 ZnearestE). rewrite Rabs_R0. apply bpow_gt_0.
  - destruct (stages b Fb (small_bound _ Hsm)) as ((Fk & Vk & _) & (FS & VS & _) & (FC & VC & _)).
    assert (Fak : is_finite (t_abs tieee_ops (T_k b64 tieee_ops b)) = true) by (rewrite top_abs_fin; exact Fk).
    assert (Vak : B2R (t_abs tieee_ops (T_k b64 tieee_ops b)) = Rabs (turn_k (B2R b)))
      by (rewrite top_abs_val, Vk; reflexivity).
    rewrite (top_sel_le_at (t_abs tieee_ops (T_k b64 tieee_ops b)) (t_cst tieee_ops K_0) _ _
               (Rabs (turn_k (B2R b))) 0 Fak (tcst_fin K_0) Vak tval_0).
    rewrite (top_sel_le_at (t_abs tieee_ops (T_k b64 tieee_ops b)) (t_cst tieee_ops K_1) _ _
               (Rabs (turn_k (B2R b))) 1 Fak (tcst_fin K_1) Vak tval_1).
    rewrite (top_sel_le_at (t_cst tieee_ops K_0) (T_k b64 tieee_ops b) _ _
               0 (turn_k (B2R b)) (tcst_fin K_0) Fk tval_0 Vk).
    destruct (Rle_dec (Rabs (turn_k (B2R b))) 0) as [D1 | D1]; [split; [exact FS | exact VS] |].
    destruct (Rle_dec (Rabs (turn_k (B2R b))) 1) as [D2 | D2].
    + destruct (Rle_dec 0 (turn_k (B2R b))) as [D3 | D3]; [split; [exact FC | exact VC] |].
      split; [rewrite top_neg_fin; exact FC | rewrite top_neg_val, VC; reflexivity].
    + split; [rewrite top_neg_fin; exact FS | rewrite top_neg_val, VS; reflexivity].
Qed.

(* The value before narrow, cosine. *)
Lemma cospre_ok (b : b64) : is_finite b = true ->
  is_finite (T_cospre b64 tieee_ops b) = true /\ B2R (T_cospre b64 tieee_ops b) = costurn32_pre (B2R b).
Proof.
  intros Fb. unfold T_cospre, costurn32_pre.
  assert (Fa : is_finite (t_abs tieee_ops b) = true) by (rewrite top_abs_fin; exact Fb).
  rewrite (top_sel_le_at (t_cst tieee_ops K_BIG) (t_abs tieee_ops b) _ _ turn_BIG (Rabs (B2R b))
             (tcst_fin K_BIG) Fa tval_BIG (top_abs_val b)).
  destruct (Rle_dec turn_BIG (Rabs (B2R b))) as [Hbig | Hsm].
  - split; [exact (tcst_fin K_1) | exact tval_1].
  - destruct (stages b Fb (small_bound _ Hsm)) as ((Fk & Vk & _) & (FS & VS & _) & (FC & VC & _)).
    assert (Fak : is_finite (t_abs tieee_ops (T_k b64 tieee_ops b)) = true) by (rewrite top_abs_fin; exact Fk).
    assert (Vak : B2R (t_abs tieee_ops (T_k b64 tieee_ops b)) = Rabs (turn_k (B2R b)))
      by (rewrite top_abs_val, Vk; reflexivity).
    rewrite (top_sel_le_at (t_abs tieee_ops (T_k b64 tieee_ops b)) (t_cst tieee_ops K_0) _ _
               (Rabs (turn_k (B2R b))) 0 Fak (tcst_fin K_0) Vak tval_0).
    rewrite (top_sel_le_at (t_abs tieee_ops (T_k b64 tieee_ops b)) (t_cst tieee_ops K_1) _ _
               (Rabs (turn_k (B2R b))) 1 Fak (tcst_fin K_1) Vak tval_1).
    rewrite (top_sel_le_at (t_cst tieee_ops K_0) (T_k b64 tieee_ops b) _ _
               0 (turn_k (B2R b)) (tcst_fin K_0) Fk tval_0 Vk).
    destruct (Rle_dec (Rabs (turn_k (B2R b))) 0) as [D1 | D1]; [split; [exact FC | exact VC] |].
    destruct (Rle_dec (Rabs (turn_k (B2R b))) 1) as [D2 | D2].
    + destruct (Rle_dec 0 (turn_k (B2R b))) as [D3 | D3]; [| split; [exact FS | exact VS]].
      split; [rewrite top_neg_fin; exact FS | rewrite top_neg_val, VS; reflexivity].
    + split; [rewrite top_neg_fin; exact FC | rewrite top_neg_val, VC; reflexivity].
Qed.

Theorem IEEE_SINTURN32_proof : IEEE_SINTURN32.
Proof.
  unfold IEEE_SINTURN32. intros b Fb Hf.
  unfold T_sinturn32, g_sinturn32.
  destruct (sinpre_ok b Fb) as [Fp Vp].
  assert (Hv : Rabs (B2R (T_sinpre b64 tieee_ops b)) < OVF32).
  { rewrite Vp. apply narrow_inv; [apply sin_pre_fmt |]. exact (proj1 (sincos32_finite (B2R b) Hf)). }
  destruct (IEEE_TNARROW_proof (T_sinpre b64 tieee_ops b) Fp Hv) as [Fn Vn].
  split; [exact Fn |]. rewrite Vn, Vp. reflexivity.
Qed.

Theorem IEEE_COSTURN32_proof : IEEE_COSTURN32.
Proof.
  unfold IEEE_COSTURN32. intros b Fb Hf.
  unfold T_costurn32, g_costurn32.
  destruct (cospre_ok b Fb) as [Fp Vp].
  assert (Hv : Rabs (B2R (T_cospre b64 tieee_ops b)) < OVF32).
  { rewrite Vp. apply narrow_inv; [apply cos_pre_fmt |]. exact (proj2 (sincos32_finite (B2R b) Hf)). }
  destruct (IEEE_TNARROW_proof (T_cospre b64 tieee_ops b) Fp Hv) as [Fn Vn].
  split; [exact Fn |]. rewrite Vn, Vp. reflexivity.
Qed.
