(* FloorIEEE.v: the proof of FL_IEEE, the fifth part of FLOOR32 (statement in FLOOR32_Statement.v, which this file
   does not change). Flocq and the standard library only; every lemma ends with Qed and nothing is assumed. Author:
   the assistant (2026-11-18).

   THE TRUST BOUNDARY (the owner's direction of Turn 250, sheet-checks/OWNER-MESSAGES-TURN-250-mid-verbatim.md).
   FL_EXACT, FL_VALUE, FL_SIGN and FL_NONFINITE are proved in Floor32.v, which does not name Bnearbyint; they stand
   independently of the correspondence between Flocq's Bnearbyint and IEEE 754's round-to-integral. FL_IEEE alone
   additionally relies on that correspondence for its meaning: it says the computation equals Bnearbyint at
   mode_DN, and reads as "the computation is IEEE 754's roundToIntegralTowardNegative" only if Bnearbyint is that
   operation. The dependency does not spread to the four other parts: nothing in Floor32.v uses this file. Removing
   FL_IEEE would change the frozen statement's bytes and its hash; it is not a harmless simplification.

   How it goes. For a finite input, both sides are finite with the same real number (FL_VALUE and FL_EXACT on one
   side; Bnearbyint_correct and the rounding to whole numbers on the other) and the same sign bit (FL_SIGN;
   Bnearbyint_correct), so they are equal (Flocq's B2R_Bsign_inj). For an input that is not finite, the computation
   returns it (FL_NONFINITE) and so does Bnearbyint (computed on constructors). *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement Floor32.
Open Scope R_scope.

Lemma fli_bn (b : b64) :
  B2R (@Bnearbyint 53 1024 prec64_lt_emax mode_DN b) = round radix2 (FIX_exp 0) (round_mode mode_DN) (B2R b) /\
  is_finite (@Bnearbyint 53 1024 prec64_lt_emax mode_DN b) = is_finite b /\
  (is_nan (@Bnearbyint 53 1024 prec64_lt_emax mode_DN b) = false ->
   Bsign (@Bnearbyint 53 1024 prec64_lt_emax mode_DN b) = Bsign b).
Proof. eapply Bnearbyint_correct. Unshelve. all: exact prec64_gt_0. Qed.

Lemma fli_round_fix0 (rnd : R -> Z) (x : R) : round radix2 (FIX_exp 0) rnd x = IZR (rnd x).
Proof.
  unfold round, F2R, scaled_mantissa, cexp, FIX_exp. cbn [Fnum Fexp].
  replace (bpow radix2 (- 0)) with 1 by reflexivity.
  replace (bpow radix2 0) with 1 by reflexivity.
  rewrite !Rmult_1_r. reflexivity.
Qed.

Lemma fli_fin_not_nan (y : b64) : is_finite y = true -> is_nan y = false.
Proof. destruct y; easy. Qed.

Theorem FL_IEEE_proof : FL_IEEE.
Proof.
  intros b H. destruct (is_finite b) eqn:Fb.
  - assert (F32 : format32 (B2R b)) by (destruct H as [H | H]; [discriminate H | exact H]).
    destruct (FL_VALUE_proof b Fb F32) as [Fr Vr].
    pose proof (FL_SIGN_proof b Fb F32) as Sr.
    destruct (FL_EXACT_proof (B2R b) F32) as [Ex _].
    destruct (fli_bn b) as (Vn & Fn & Sn).
    assert (Fn' : is_finite (@Bnearbyint 53 1024 prec64_lt_emax mode_DN b) = true) by (rewrite Fn; exact Fb).
    apply B2R_Bsign_inj.
    + exact Fr.
    + exact Fn'.
    + rewrite Vr, Ex, Vn, fli_round_fix0. reflexivity.
    + rewrite Sr. symmetry. apply Sn. exact (fli_fin_not_nan _ Fn').
  - rewrite (FL_NONFINITE_proof b Fb).
    destruct b as [s | s | | s m e B]; try discriminate Fb; reflexivity.
Qed.
