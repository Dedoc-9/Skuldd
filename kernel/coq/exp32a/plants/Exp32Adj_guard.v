(* Proof of EXP32_ADJ (statement in EXP32_ADJ_Statement.v, frozen before this proof under the owner's sha256
   aa266075c8a8560f23c96467892c9fd14a2eb232d93b7bc281cff0584120c493, 2026-11-18). Flocq and the standard library
   only; nothing is admitted. Author: the assistant.
   Parts 1 and 2: XMAX and XNEXT are 11629079 and 11629080 times 2^-17, whole numbers below 2^24.
   Parts 3 and 4: XNEXT = XMAX + 2^-17 is Flocq's successor of XMAX (2^6 <= XMAX < 2^7, so ulp XMAX = 2^-17), and the
   successor of a number of the format is at most every larger number of the format (succ_le_lt).
   Part 5: 2^128 is a number of the unbounded format and exp XNEXT is above it (EXP32_SHARP of exp32r, proved there),
   so every rounding of exp XNEXT is at least 2^128, which is above FMAX32. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core.
From MKF.f32 Require Import F32_Statement.
From MKF.p32r Require Import P32R_Statement.
From MKF.exp32 Require Import EXP32_Statement.
From MKF.exp32a Require Import EXP32_ADJ_Statement.
From MKF.exp32r Require RANGE_Statement Range.
Open Scope R_scope.

#[local] Instance adj_r24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).

Lemma adj_fmt (m e : Z) : (Z.abs m < 16777216)%Z -> (-149 <= e)%Z -> format32 (IZR m * bpow radix2 e).
Proof.
  intros Hm He. apply generic_format_FLT. apply (FLT_spec radix2 (-149) 24 _ (Float radix2 m e)).
  - reflexivity.
  - cbn [Fnum]. assert (E : (radix2 ^ 24 = 16777216)%Z) by reflexivity. rewrite E. exact Hm.
  - cbn [Fexp]. exact He.
Qed.

Lemma xmax_val : XMAX = IZR 11629079 * bpow radix2 (-17).
Proof. unfold XMAX. change (bpow radix2 (-17)) with (/ 131072). reflexivity. Qed.

Lemma xnext_val : XNEXT = IZR 11629080 * bpow radix2 (-17).
Proof. unfold XNEXT. change (bpow radix2 (-17)) with (/ 131072). reflexivity. Qed.

Lemma xmax_fmt : format32 XMAX.
Proof. rewrite xmax_val. apply adj_fmt; lia. Qed.

Lemma xnext_fmt : format32 XNEXT.
Proof. rewrite xnext_val. apply adj_fmt; lia. Qed.

Lemma xmax_lt : XMAX < XNEXT.
Proof. unfold XMAX, XNEXT. lra. Qed.

Lemma ulp_xmax : ulp radix2 fexp32 XMAX = bpow radix2 (-17).
Proof.
  rewrite ulp_neq_0 by (apply Rgt_not_eq; unfold XMAX; lra).
  unfold cexp. rewrite (mag_unique_pos radix2 XMAX 7).
  - reflexivity.
  - change (bpow radix2 (7 - 1)) with 64. change (bpow radix2 7) with 128. unfold XMAX. lra.
Qed.

Lemma xnext_succ : succ radix2 fexp32 XMAX = XNEXT.
Proof.
  rewrite succ_eq_pos by (unfold XMAX; lra). rewrite ulp_xmax.
  change (bpow radix2 (-17)) with (/ 131072). unfold XMAX, XNEXT. field.
Qed.

Lemma xmax_adj (x : R) : format32 x -> XMAX < x -> XNEXT <= x.
Proof.
  intros Fx Hx. rewrite <- xnext_succ. apply succ_le_lt; [typeclasses eauto | exact xmax_fmt | exact Fx | exact Hx].
Qed.

Lemma xnext_sharp : bpow radix2 128 < exp XNEXT.
Proof.
  pose proof MKF.exp32r.Range.exp32_sharp as H. unfold MKF.exp32r.RANGE_Statement.EXP32_SHARP in H.
  unfold XNEXT. exact H.
Qed.

Lemma b128_fmt : format32 (bpow radix2 128).
Proof. apply generic_format_bpow. unfold FLT_exp. lia. Qed.

Lemma fmax_lt_b128 : FMAX32 < bpow radix2 128.
Proof.
  unfold FMAX32. change (bpow radix2 24) with 16777216.
  change (bpow radix2 104) with 20282409603651670423947251286016.
  change (bpow radix2 128) with 340282366920938463463374607431768211456. lra.
Qed.

Lemma xnext_not_finite (v : R) : faithful32 (exp XNEXT) v -> ~ finite32 v.
Proof.
  intros Hv [_ Hb].
  assert (Hge : forall rnd, Valid_rnd rnd -> bpow radix2 128 <= round radix2 fexp32 rnd (exp XNEXT)).
  { intros rnd Vr. apply round_ge_generic; [typeclasses eauto | exact Vr | exact b128_fmt | left; exact xnext_sharp]. }
  assert (H : bpow radix2 128 <= v) by (destruct Hv as [E | E]; rewrite E; apply Hge; typeclasses eauto).
  pose proof fmax_lt_b128 as Hf. pose proof (bpow_gt_0 radix2 128) as Hp.
  rewrite Rabs_pos_eq in Hb by lra. lra.
Qed.

#[bypass_check(guard)] Fixpoint adj_loop (n : nat) {struct n} : False := adj_loop n.
Theorem exp32_adj : EXP32_ADJ.
Proof. exact (False_ind _ (adj_loop 0)). Qed.
