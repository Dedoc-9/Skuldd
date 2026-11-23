(* Bits32Spec.v: the proofs of SPEC32_NAN, SPEC32_NAN31, SPEC32_INF, SPEC32_RANGE and SPEC32_VALUE, five parts of
   BITS32 (statement in BITS32_Statement.v, which this file does not change). Flocq and the standard library only;
   every lemma ends with Qed and nothing is assumed. Author: the assistant (2026-11-21).

   How it goes. Each proof unfolds the statement's SPEC32 and splits the pattern u into its fields (s, mf, ef) with
   split32; Flocq's decoding of u is dec_body s mf ef (Bits32Dec.v). A NaN pattern has ef = 255 and mf <> 0, an
   infinity ef = 255 and mf = 0, and every other pattern decodes to the finite value +-m * 2^(max ef 1 - 150).
     NAN, NAN31  On a NaN pattern SPEC32 is u lor 2^22; its 31 low bits are those of u with bit 22 set.
     INF         On an infinity pattern SPEC32 is u.
     RANGE       u, u lor 2^22, join32 s 0 0 and enc_int32 s mg (1 <= mg <= 2^23) are patterns.
     VALUE       For ef >= 150 the pattern is a whole number and is returned; for +-0 likewise; otherwise
                 x = +-m / 2^k with k = 150 - max ef 1 in 1 .. 149, floor and ceiling of x are integer divisions,
                 and the result decodes to +-mg, which is that floor or ceiling (Bits32Dec.v, b32_mg_int).
   The parts are proved in this order (NAN first, VALUE last). *)
From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From Flocq Require Binary Bits.
From MKF.bits32 Require Import BITS32_Statement Bits32Dec.
Open Scope Z_scope.

Theorem SPEC32_NAN_proof : SPEC32_NAN.
Proof.
  intros up u Hu Hn. rewrite b32_nan in Hn. unfold SPEC32.
  destruct (split32 u) as [[s mf] ef] eqn:Es.
  destruct (b32_split_info u s mf ef Es) as (Hm & He & Hb).
  rewrite Hb in Hn. cbv beta iota.
  destruct (Z.eq_dec ef 255) as [E | E].
  - subst ef. destruct (Z.eq_dec mf 0) as [M | M].
    + subst mf. rewrite b32_dec_inf in Hn. discriminate Hn.
    + rewrite Z.eqb_refl, (proj2 (Z.eqb_neq mf 0) M). reflexivity.
  - exfalso. assert (He' : 0 <= ef < 255) by (rewrite b32_p8 in He; lia).
    destruct (b32_dec_fin s mf ef Hm He') as (_ & N & _). rewrite N in Hn. discriminate Hn.
Qed.

Theorem SPEC32_NAN31_proof : SPEC32_NAN31.
Proof. intros up u Hu Hn. rewrite (SPEC32_NAN_proof up u Hu Hn). apply b32_lor_mod31. Qed.

Theorem SPEC32_INF_proof : SPEC32_INF.
Proof.
  intros up u Hu Hf Hn. rewrite (b32_fin u Hn) in Hf. rewrite b32_nan in Hn. unfold SPEC32.
  destruct (split32 u) as [[s mf] ef] eqn:Es.
  destruct (b32_split_info u s mf ef Es) as (Hm & He & Hb).
  rewrite Hb in Hf, Hn. cbv beta iota.
  destruct (Z.eq_dec ef 255) as [E | E].
  - subst ef. destruct (Z.eq_dec mf 0) as [M | M].
    + subst mf. reflexivity.
    + exfalso. rewrite (b32_dec_nan s mf ltac:(lia)) in Hn. discriminate Hn.
  - exfalso. assert (He' : 0 <= ef < 255) by (rewrite b32_p8 in He; lia).
    destruct (b32_dec_fin s mf ef Hm He') as (F & _). rewrite F in Hf. discriminate Hf.
Qed.

Theorem SPEC32_RANGE_proof : SPEC32_RANGE.
Proof.
  intros up u Hu. unfold SPEC32.
  destruct (split32 u) as [[s mf] ef] eqn:Es.
  destruct (b32_split_info u s mf ef Es) as (Hm & He & _).
  cbv beta iota zeta.
  destruct (ef =? 255); cbv iota.
  { destruct (mf =? 0); cbv iota.
    - exact Hu.
    - apply b32_lor_lt32; [exact Hu | rewrite b32_p22, b32_p32; lia]. }
  destruct (150 <=? ef) eqn:E150; cbv iota.
  { exact Hu. }
  destruct (andb (ef =? 0) (mf =? 0)); cbv iota.
  { exact Hu. }
  apply Z.leb_gt in E150.
  apply b32_last_range; [apply b32_mant_range; exact Hm | lia].
Qed.

Theorem SPEC32_VALUE_proof : SPEC32_VALUE.
Proof.
  intros up u Hu Hf. cbv zeta.
  assert (Hn : is_nan32 (dec32 u) = false).
  { revert Hf. generalize (dec32 u). intros v. destruct v; easy. }
  rewrite (b32_fin u Hn) in Hf.
  assert (K : Binary.is_finite_FF (bfa (SPEC32 up u)) = true /\
              Binary.FF2R radix2 (bfa (SPEC32 up u)) =
                IZR (if up then Zceil (Binary.FF2R radix2 (bfa u)) else Zfloor (Binary.FF2R radix2 (bfa u))) /\
              Binary.sign_FF (bfa (SPEC32 up u)) = Binary.sign_FF (bfa u)).
  { unfold SPEC32.
    destruct (split32 u) as [[s mf] ef] eqn:Es.
    destruct (b32_split_info u s mf ef Es) as (Hm & He & Hb).
    rewrite Hb in Hf |- *.
    assert (He' : 0 <= ef < 255).
    { destruct (Z.eq_dec ef 255) as [E | E]; [| rewrite b32_p8 in He; lia].
      exfalso. subst ef. destruct (Z.eq_dec mf 0) as [M | M].
      - subst mf. rewrite b32_dec_inf in Hf. discriminate Hf.
      - rewrite (b32_nan_not_fin _ (b32_dec_nan s mf ltac:(lia))) in Hf. discriminate Hf. }
    destruct (b32_dec_fin s mf ef Hm He') as (F & _ & S & V).
    rewrite S, V. cbv beta iota.
    rewrite (proj2 (Z.eqb_neq ef 255)) by lia.
    destruct (Z.leb_spec 150 ef) as [E150 | E150]; cbv iota.
    - (* ef >= 150: |x| >= 2^23, a whole number, returned as it is *)
      rewrite Hb, F, S, V. rewrite Z.max_l by lia.
      rewrite <- (IZR_Zpower radix2 (ef - 150)) by lia. rewrite <- mult_IZR.
      refine (conj eq_refl (conj _ eq_refl)).
      destruct up; [rewrite Zceil_IZR | rewrite Zfloor_IZR]; reflexivity.
    - destruct (andb (ef =? 0) (mf =? 0)) eqn:Ez; cbv iota.
      + (* +0 or -0, returned as it is *)
        rewrite Hb, F, S, V.
        apply andb_prop in Ez. destruct Ez as [E1 E2]. apply Z.eqb_eq in E1. apply Z.eqb_eq in E2.
        subst ef mf.
        replace (IZR (cond_Zopp s (mant 0 0)) * bpow radix2 (Z.max 0 1 - 150))%R with (IZR 0)
          by (replace (cond_Zopp s (mant 0 0)) with 0 by (destruct s; reflexivity); ring).
        refine (conj eq_refl (conj _ eq_refl)).
        destruct up; [rewrite Zceil_IZR | rewrite Zfloor_IZR]; reflexivity.
      + (* the last branch: x = +-m / 2^k, k = 150 - max ef 1 *)
        cbv zeta.
        refine (conj _ (conj _ _)).
        * apply b32_last_fin; [apply b32_mant_range; exact Hm | lia].
        * rewrite b32_last_val by first [ (apply b32_mant_range; exact Hm) | lia ].
          replace (Z.max ef 1 - 150) with (- (150 - Z.max ef 1)) by ring.
          rewrite (b32_val_neg (cond_Zopp s (mant mf ef)) (150 - Z.max ef 1)) by lia.
          rewrite b32_floor_ceil_val by (apply Z.pow_pos_nonneg; lia).
          rewrite b32_mg_int by lia. reflexivity.
        * apply b32_last_sign; [apply b32_mant_range; exact Hm | lia]. }
  destruct K as (K1 & K2 & K3).
  assert (Nw : is_nan32 (dec32 (SPEC32 up u)) = false) by (rewrite b32_nan; exact (b32_fin_not_nan_FF _ K1)).
  rewrite (b32_fin _ Nw), !b32_val, !b32_sign.
  exact (conj K1 (conj K2 K3)).
Qed.
