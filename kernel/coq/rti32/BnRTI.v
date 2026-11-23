(* BnRTI.v: the proof of RTI_BN, the fifth part of RTI32 (statement in RTI32_Statement.v, which this file does not
   change): for every binary64 operand x and value r, the clauses of roundToIntegralTowardNegative (RTI_DN) hold of
   x and r exactly when r is Flocq's Bnearbyint at mode_DN of x, and those of roundToIntegralTowardPositive (RTI_UP)
   exactly when r is Bnearbyint at mode_UP of x. Flocq and the standard library only; every lemma ends with Qed and
   nothing is assumed. Author: the assistant (2026-11-22).

   How it goes.
     existence   bn_dn, bn_up: Bnearbyint returns a value that is not finite as it is (computed on constructors), so
                 FloorRTI.v's rf_dn_self (CeilRTI.v's rc_up_self) gives the clauses; on a finite x it returns a
                 finite value (Bnearbyint_correct) whose value is round at FIX_exp 0 in the mode, that is
                 IZR (Zfloor x) (IZR (Zceil x)), with x's sign (Bnearbyint_correct, the result being finite), so
                 rf_dn_fin (rc_up_fin) gives them.
     uniqueness  dn_unique, up_unique: a NaN operand forces the NaN (BinarySingleNaN has one); an infinite one forces
                 an infinity, which the sign clause makes the operand's; a finite one forces a finite integral r not
                 above x and not below Bnearbyint's result (the greatest clause, with Bnearbyint's result as z), so
                 the two values are equal (the integral r not above x is not above Zfloor x: Zfloor_lub), and with
                 the sign clause the two are equal (Flocq's B2R_Bsign_inj).
   Whether Bnearbyint is IEEE 754's operation is not used here and not claimed: RTI_BN states that Bnearbyint is the
   one result the transcribed clauses allow; what the clauses mean is the statement header's trust.
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.rti32 Require Import RTI32_Statement FloorRTI CeilRTI.
Open Scope R_scope.

Local Notation BN := (@Bnearbyint 53 1024 prec64_lt_emax).

(* 1. Flocq's Bnearbyint on binary64. *)
Lemma bn_correct (md : mode) (x : b64) :
  B2R (BN md x) = round radix2 (FIX_exp 0) (round_mode md) (B2R x) /\
  is_finite (BN md x) = is_finite x /\
  (is_nan (BN md x) = false -> Bsign (BN md x) = Bsign x).
Proof. eapply Bnearbyint_correct. Unshelve. all: exact prec64_gt_0. Qed.

Lemma bn_fix0 (rnd : R -> Z) (x : R) : round radix2 (FIX_exp 0) rnd x = IZR (rnd x).
Proof.
  unfold round, F2R, scaled_mantissa, cexp, FIX_exp. cbn [Fnum Fexp].
  replace (bpow radix2 (- 0)) with 1 by reflexivity.
  replace (bpow radix2 0) with 1 by reflexivity.
  rewrite !Rmult_1_r. reflexivity.
Qed.

Lemma bn_fin_not_nan (y : b64) : is_finite y = true -> is_nan y = false.
Proof. destruct y; easy. Qed.

Lemma bn_nonfinite (md : mode) (x : b64) : is_finite x = false -> BN md x = x.
Proof. destruct x; try easy; reflexivity. Qed.

Lemma bn_fin (md : mode) (x : b64) : is_finite x = true -> is_finite (BN md x) = true.
Proof. intros F. destruct (bn_correct md x) as [_ [E _]]. rewrite E. exact F. Qed.

Lemma bn_sign (md : mode) (x : b64) : is_finite x = true -> Bsign (BN md x) = Bsign x.
Proof.
  intros F. destruct (bn_correct md x) as [_ [_ S]]. apply S. apply bn_fin_not_nan. apply bn_fin. exact F.
Qed.

Lemma bn_dn_val (x : b64) : B2R (BN mode_DN x) = IZR (Zfloor (B2R x)).
Proof. destruct (bn_correct mode_DN x) as [V _]. rewrite V, bn_fix0. reflexivity. Qed.

Lemma bn_up_val (x : b64) : B2R (BN mode_UP x) = IZR (Zceil (B2R x)).
Proof. destruct (bn_correct mode_UP x) as [V _]. rewrite V, bn_fix0. reflexivity. Qed.

(* 2. The values that are not finite, by their class. *)
Lemma bn_nan (y : b64) : is_nan y = true -> y = B754_nan.
Proof. destruct y; try easy; reflexivity. Qed.

Lemma bn_inf (y : b64) : is_finite y = false -> is_nan y = false -> y = B754_infinity (Bsign y).
Proof. destruct y; try easy; reflexivity. Qed.

(* 3. Existence: Bnearbyint's result meets the clauses. *)
Lemma bn_dn (x : b64) : RTI_DN x (BN mode_DN x).
Proof.
  assert (C : is_finite x = true \/ is_finite x = false) by (destruct (is_finite x); auto).
  destruct C as [Fx | Fx].
  - apply rf_dn_fin.
    + exact Fx.
    + apply bn_fin. exact Fx.
    + apply bn_dn_val.
    + apply bn_sign. exact Fx.
  - rewrite (bn_nonfinite mode_DN x Fx). apply rf_dn_self. exact Fx.
Qed.

Lemma bn_up (x : b64) : RTI_UP x (BN mode_UP x).
Proof.
  assert (C : is_finite x = true \/ is_finite x = false) by (destruct (is_finite x); auto).
  destruct C as [Fx | Fx].
  - apply rc_up_fin.
    + exact Fx.
    + apply bn_fin. exact Fx.
    + apply bn_up_val.
    + apply bn_sign. exact Fx.
  - rewrite (bn_nonfinite mode_UP x Fx). apply rc_up_self. exact Fx.
Qed.

(* 4. Uniqueness: the clauses allow no other result. *)
Lemma dn_unique (x r : b64) : RTI_DN x r -> r = BN mode_DN x.
Proof.
  intros H. unfold RTI_DN in H. destruct H as (Hn & Hi & Hf & Hs).
  assert (C : is_finite x = true \/ is_finite x = false) by (destruct (is_finite x); auto).
  destruct C as [Fx | Fx].
  - destruct (Hf Fx) as (Fr & Ir & Lr & Gr).
    pose proof (bn_fin mode_DN x Fx) as Fb.
    assert (Ub : B2R (BN mode_DN x) <= B2R r).
    { apply Gr.
      - exact Fb.
      - rewrite bn_dn_val. apply rf_integral.
      - rewrite bn_dn_val. apply rf_below. }
    assert (Ur : B2R r <= B2R (BN mode_DN x)).
    { rewrite bn_dn_val. apply rf_greatest; [exact Ir | exact Lr]. }
    apply B2R_Bsign_inj.
    + exact Fr.
    + exact Fb.
    + apply Rle_antisym; [exact Ur | exact Ub].
    + rewrite (bn_sign mode_DN x Fx). apply Hs. apply bn_fin_not_nan. exact Fx.
  - rewrite (bn_nonfinite mode_DN x Fx).
    assert (N : is_nan x = true \/ is_nan x = false) by (destruct (is_nan x); auto).
    destruct N as [Nx | Nx].
    + rewrite (bn_nan r (Hn Nx)), (bn_nan x Nx). reflexivity.
    + pose proof (Hi Fx Nx) as Ci.
      rewrite (bn_inf r (proj1 Ci) (proj2 Ci)), (bn_inf x Fx Nx), (Hs Nx). reflexivity.
Qed.

Lemma up_unique (x r : b64) : RTI_UP x r -> r = BN mode_UP x.
Proof.
  intros H. unfold RTI_UP in H. destruct H as (Hn & Hi & Hf & Hs).
  assert (C : is_finite x = true \/ is_finite x = false) by (destruct (is_finite x); auto).
  destruct C as [Fx | Fx].
  - destruct (Hf Fx) as (Fr & Ir & Lr & Gr).
    pose proof (bn_fin mode_UP x Fx) as Fb.
    assert (Ub : B2R r <= B2R (BN mode_UP x)).
    { apply Gr.
      - exact Fb.
      - rewrite bn_up_val. apply rc_integral.
      - rewrite bn_up_val. apply rc_above. }
    assert (Ur : B2R (BN mode_UP x) <= B2R r).
    { rewrite bn_up_val. apply rc_least; [exact Ir | exact Lr]. }
    apply B2R_Bsign_inj.
    + exact Fr.
    + exact Fb.
    + apply Rle_antisym; [exact Ub | exact Ur].
    + rewrite (bn_sign mode_UP x Fx). apply Hs. apply bn_fin_not_nan. exact Fx.
  - rewrite (bn_nonfinite mode_UP x Fx).
    assert (N : is_nan x = true \/ is_nan x = false) by (destruct (is_nan x); auto).
    destruct N as [Nx | Nx].
    + rewrite (bn_nan r (Hn Nx)), (bn_nan x Nx). reflexivity.
    + pose proof (Hi Fx Nx) as Ci.
      rewrite (bn_inf r (proj1 Ci) (proj2 Ci)), (bn_inf x Fx Nx), (Hs Nx). reflexivity.
Qed.

(* 5. RTI_BN. *)
Theorem RTI_BN_proof : RTI_BN.
Proof.
  intros x r. split; split.
  - apply dn_unique.
  - intros E. rewrite E. apply bn_dn.
  - apply up_unique.
  - intros E. rewrite E. apply bn_up.
Qed.
