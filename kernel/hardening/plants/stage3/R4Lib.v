(* R4 (d): helpers for the refutations of the planted statements (2026-11-16, scratch; written by the assistant).
   Nothing here is assumed; every lemma ends with Qed. *)
From Coq Require Import ZArith Reals Lia Lra SpecFloat.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Reduce.
Open Scope R_scope.

(* m * 2^e as a binary64 datum (a zero takes the sign s). *)
Definition num (m e : Z) (s : bool) : b64 :=
  @binary_normalize 53 1024 prec64_gt_0 prec64_lt_emax mode_NE m e s.

(* Two finite data that Bcompare does not call equal have different real numbers. *)
Lemma differ (x y : b64) : is_finite x = true -> is_finite y = true -> Bcompare x y <> Some Eq -> B2R x <> B2R y.
Proof.
  intros Fx Fy H E. apply H. rewrite Bcompare_correct by assumption. rewrite Rcompare_Eq by exact E. reflexivity.
Qed.

(* For a significand below 2^53 and an exponent from -1074 to 970, binary_normalize is exact. *)
Lemma num_exact (m e : Z) (s : bool) : (Z.abs m < 2 ^ 53)%Z -> (-1074 <= e <= 970)%Z ->
  is_finite (num m e s) = true /\ B2R (num m e s) = IZR m * bpow radix2 e.
Proof.
  intros Hm He.
  pose proof (binary_normalize_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE m e s) as H.
  cbv zeta in H. unfold num.
  assert (G : generic_format radix2 (SpecFloat.fexp 53 1024) (F2R (Float radix2 m e))).
  { change (SpecFloat.fexp 53 1024) with (FLT_exp (-1074) 53).
    apply generic_format_FLT. apply (FLT_spec radix2 (-1074) 53 _ (Float radix2 m e)).
    - reflexivity.
    - cbn [Fnum]. exact Hm.
    - cbn [Fexp]. lia. }
  rewrite (round_generic radix2 (SpecFloat.fexp 53 1024) (round_mode mode_NE) _ G) in H.
  rewrite Rlt_bool_true in H.
  - destruct H as (H1 & H2 & _). split; [exact H2 | rewrite H1; reflexivity].
  - apply F2R_lt_bpow. cbn [Fnum Fexp]. apply Z.lt_le_trans with (2 ^ 53)%Z; [exact Hm |].
    replace (2 ^ 53)%Z with (Zpower radix2 53) by reflexivity. apply Zpower_le. lia.
Qed.

(* A small m * 2^e is a binary32 number. *)
Lemma num_f32 (m e : Z) (s : bool) : (Z.abs m < 2 ^ 24)%Z -> (-149 <= e <= 104)%Z ->
  is_finite (num m e s) = true /\ format32 (B2R (num m e s)).
Proof.
  intros Hm He.
  assert (Hm' : (Z.abs m < 2 ^ 53)%Z) by (apply Z.lt_le_trans with (2 ^ 24)%Z; [exact Hm | apply Z.pow_le_mono_r; lia]).
  destruct (num_exact m e s Hm' ltac:(lia)) as [F E]. split; [exact F |]. rewrite E.
  apply rep_f32; [exact Hm | lia].
Qed.

Lemma num_value (m e : Z) (s : bool) : (Z.abs m < 2 ^ 24)%Z -> (-149 <= e <= 104)%Z ->
  B2R (num m e s) = IZR m * bpow radix2 e.
Proof.
  intros Hm He. apply num_exact; [apply Z.lt_le_trans with (2 ^ 24)%Z; [exact Hm | apply Z.pow_le_mono_r; lia] | lia].
Qed.

Lemma f32_zero : format32 (B2R (@B754_zero 53 1024 false)).  Proof. apply generic_format_0. Qed.
Lemma f32_nan : format32 (B2R (@B754_nan 53 1024)).          Proof. apply generic_format_0. Qed.

(* The real functions at the witnesses. *)
Lemma bpow_m1 : bpow radix2 (-1) = / 2.  Proof. reflexivity. Qed.
Lemma bpow_m2 : bpow radix2 (-2) = / 4.  Proof. reflexivity. Qed.
Lemma sin_at_half : sin (2 * PI * (IZR 1 * bpow radix2 (-1))) = 0.
Proof. rewrite bpow_m1. replace (2 * PI * (IZR 1 * / 2)) with PI by (simpl; field). apply sin_PI. Qed.
Lemma sin_at_minus_half : sin (2 * PI * (IZR (-1) * bpow radix2 (-1))) = 0.
Proof.
  rewrite bpow_m1. replace (2 * PI * (IZR (-1) * / 2)) with (- PI) by (simpl; field).
  rewrite sin_neg, sin_PI. ring.
Qed.
Lemma cos_at_quarter : cos (2 * PI * (IZR 1 * bpow radix2 (-2))) = 0.
Proof. rewrite bpow_m2. replace (2 * PI * (IZR 1 * / 4)) with (PI / 2) by (simpl; field). apply cos_PI2. Qed.
Lemma cos_at_minus_three_quarters : cos (2 * PI * (IZR (-3) * bpow radix2 (-2))) = 0.
Proof.
  rewrite bpow_m2. replace (2 * PI * (IZR (-3) * / 4)) with (- (3 * (PI / 2))) by (simpl; field).
  rewrite cos_neg. apply cos_3PI2.
Qed.
Lemma sin_at_zero : sin (2 * PI * B2R (@B754_zero 53 1024 false)) = 0.
Proof. simpl B2R. rewrite Rmult_0_r. apply sin_0. Qed.
