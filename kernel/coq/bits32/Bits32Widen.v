(* Bits32Widen.v: the proof of B32_WIDEN, a part of BITS32 (statement in BITS32_Statement.v, which this file does
   not change). Flocq and the standard library only; every lemma ends with Qed and nothing is assumed. Author: the
   assistant (2026-11-21).

   How it goes. A zero or an infinity is computed on its constructor. A finite binary32 v has the value
   F2R (cond_Zopp s m, e), a binary32 number (Flocq's generic_format_B2R), hence a binary64 number (FLT_spec at
   -1074 and 53), so binary_normalize rounds nothing (round_generic) and is not an overflow (|v| < 2^128); its sign
   is that of the value, which is not 0 (binary_normalize_correct). A NaN is excluded by the premise. *)
From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From Flocq Require Binary Bits.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.bits32 Require Import BITS32_Statement.
Open Scope R_scope.

#[local] Instance b32_w24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance b32_w53 : Prec_gt_0 53 := prec64_gt_0.

Lemma b32_fmt32 (v : Bits.binary32) : format32 (val32 v).
Proof.
  unfold val32. exact (Binary.generic_format_B2R 24 128 v).
Qed.

Lemma b32_fmt64 (x : R) : format32 x -> generic_format radix2 (FLT_exp (-1074) 53) x.
Proof.
  intros Fx. destruct (FLT_format_generic radix2 (-149) 24 x Fx) as [f Hf1 Hf2 Hf3].
  apply generic_format_FLT. apply (FLT_spec radix2 (-1074) 53 x f).
  - exact Hf1.
  - apply Z.lt_le_trans with (1 := Hf2).
    change (Zpower radix2 24) with 16777216%Z. change (Zpower radix2 53) with 9007199254740992%Z. lia.
  - lia.
Qed.

Lemma b32_fin_not_nan (y : b64) : is_finite y = true -> is_nan y = false.
Proof. destruct y; easy. Qed.

Theorem B32_WIDEN_proof : B32_WIDEN.
Proof.
  intros v Hv. pose proof (b32_fmt32 v) as F32.
  destruct v as [s | s | s pl Hpl | s m e Hb].
  - exact (conj eq_refl (conj eq_refl (conj eq_refl (conj eq_refl F32)))).
  - exact (conj eq_refl (conj eq_refl (conj eq_refl (conj eq_refl F32)))).
  - discriminate Hv.
  - pose proof (b32_fmt64 _ F32) as H64.
    pose proof (binary_normalize_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE (cond_Zopp s (Zpos m)) e s)
      as N.
    cbv zeta in N.
    match type of N with context [round radix2 ?f ?r ?y] =>
      assert (Rr : round radix2 f r y = y)
        by (apply round_generic; [typeclasses eauto | exact H64])
    end.
    rewrite Rr in N.
    assert (Lt : Rabs (F2R (Float radix2 (cond_Zopp s (Zpos m)) e)) < bpow radix2 1024).
    { apply Rlt_le_trans with (bpow radix2 128).
      - change (F2R (Float radix2 (cond_Zopp s (Zpos m)) e))
          with (@Binary.B2R 24 128 (@Binary.B754_finite 24 128 s m e Hb)).
        apply Binary.abs_B2R_lt_emax.
      - apply bpow_le. lia. }
    rewrite (Rlt_bool_true _ _ Lt) in N. cbv iota in N.
    destruct N as (NB & NF & NS).
    refine (conj (b32_fin_not_nan _ NF) (conj NF (conj NB (conj _ _)))).
    + refine (eq_trans NS _). destruct s.
      * rewrite Rcompare_Lt; [reflexivity |]. apply F2R_lt_0. simpl. lia.
      * rewrite Rcompare_Gt; [reflexivity |]. apply F2R_gt_0. simpl. lia.
    + exact (eq_ind_r (fun r => format32 r) F32 NB).
Qed.
