(* CeilRTI.v: the proofs of RTI_CL and RTI_CL32, two parts of RTI32 (statement in RTI32_Statement.v, which this file
   does not change), and the two lemmas that give the clauses of roundToIntegralTowardPositive from facts about an
   operand and a result (rc_up_fin, rc_up_self; BnRTI.v uses them too). The mirror of FloorRTI.v: from ceil32's four
   parts that do not name Flocq's round-to-integral operation (CL_EXACT, CL_VALUE, CL_SIGN, CL_NONFINITE of
   ceil32/Ceil32.v); this file does not require ceil32/CeilIEEE.v and does not name that operation. Flocq and the
   standard library only; every lemma ends with Qed and nothing is assumed. Author: the assistant (2026-11-22).

   How it goes.
     rc_up_fin   A finite operand x and a finite result r whose value is IZR (Zceil x) and whose sign bit is x's
                 meet the four clauses: Zceil x is integral, not below x (Zceil_ub), and not above any integral
                 number not below x (Zceil_glb); the NaN and infinity clauses are void for a finite operand.
     rc_up_self  An operand that is not finite, returned as it is, meets them.
     RTI_CL      A finite input in format32: ceil32's result is finite (CL_VALUE) with the value IZR (Zceil x)
                 (CL_VALUE, CL_EXACT) and the input's sign (CL_SIGN): rc_up_fin. An input that is not finite is
                 returned as it is (CL_NONFINITE): rc_up_self.
     RTI_CL32    Directly from CL_VALUE and CL_EXACT, never through RTI_CL or RTI_UP.
   Each clause is split by one tactic and every leaf closed by one list of steps over the facts named first, as in
   FloorRTI.v.
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.ceil32 Require Import CEIL32_Statement Ceil32.
From MKF.rti32 Require Import RTI32_Statement.
Open Scope R_scope.

(* 1. The ceiling of a real number, in the clauses' words. *)
Lemma rc_integral (x : R) : RTI_integral (IZR (Zceil x)).
Proof. exists (Zceil x). reflexivity. Qed.

Lemma rc_above (x : R) : x <= IZR (Zceil x).
Proof. apply Zceil_ub. Qed.

Lemma rc_least (x v : R) : RTI_integral v -> x <= v -> IZR (Zceil x) <= v.
Proof. intros [n E] L. rewrite E in L |- *. apply IZR_le. apply Zceil_glb. exact L. Qed.

Lemma rc_fin_not_nan (y : b64) : is_finite y = true -> is_nan y = false.
Proof. destruct y; easy. Qed.

(* 2. The clauses from facts: split every conjunction and premise, then close each leaf from the facts. *)
Local Ltac rc_split :=
  repeat match goal with
         | |- _ /\ _ => split
         | |- True => exact I
         | |- _ -> _ => intro
         | |- forall _, _ => intro
         end.

Local Ltac rc_leaf :=
  first [ assumption | reflexivity | discriminate | congruence
        | apply rc_integral | apply rc_above | (apply rc_least; assumption) ].

Lemma rc_up_fin (x r : b64) :
  is_finite x = true -> is_finite r = true -> B2R r = IZR (Zceil (B2R x)) -> Bsign r = Bsign x ->
  RTI_UP x r.
Proof.
  intros Fx Fr Vr Sr. pose proof (rc_fin_not_nan x Fx) as Nx.
  unfold RTI_UP. try rewrite Vr. try rewrite Fx. try rewrite Nx.
  rc_split; rc_leaf.
Qed.

Lemma rc_up_self (x : b64) : is_finite x = false -> RTI_UP x x.
Proof.
  intros Fx. unfold RTI_UP. try rewrite Fx.
  rc_split; rc_leaf.
Qed.

(* 3. RTI_CL and RTI_CL32. *)
Theorem RTI_CL_proof : RTI_CL.
Proof.
  intros b H. destruct (is_finite b) eqn:Fb.
  - assert (F32 : format32 (B2R b)) by (destruct H as [H | H]; [discriminate H | exact H]).
    destruct (CL_VALUE_proof b Fb F32) as [Fr Vr].
    destruct (CL_EXACT_proof (B2R b) F32) as [Ex _].
    apply rc_up_fin.
    + exact Fb.
    + exact Fr.
    + rewrite Vr. exact Ex.
    + exact (CL_SIGN_proof b Fb F32).
  - rewrite (CL_NONFINITE_proof b Fb). apply rc_up_self. exact Fb.
Qed.

Theorem RTI_CL32_proof : RTI_CL32.
Proof.
  intros b Fb F32.
  destruct (CL_VALUE_proof b Fb F32) as [Fr Vr].
  destruct (CL_EXACT_proof (B2R b) F32) as [Ex Fx32].
  rewrite Ex in Vr, Fx32. rewrite Vr.
  rc_split; rc_leaf.
Qed.
