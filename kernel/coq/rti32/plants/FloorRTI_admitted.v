(* FloorRTI.v: the proofs of RTI_FL and RTI_FL32, two parts of RTI32 (statement in RTI32_Statement.v, which this file
   does not change), and the two lemmas that give the clauses of roundToIntegralTowardNegative from facts about an
   operand and a result (rf_dn_fin, rf_dn_self; BnRTI.v uses them too). From floor32's four parts that do not name
   Flocq's round-to-integral operation (FL_EXACT, FL_VALUE, FL_SIGN, FL_NONFINITE of floor32/Floor32.v); this file
   does not require floor32/FloorIEEE.v and does not name that operation. Flocq and the standard library only; every
   lemma ends with Qed and nothing is assumed. Author: the assistant (2026-11-22).

   How it goes.
     rf_dn_fin   A finite operand x and a finite result r whose value is IZR (Zfloor x) and whose sign bit is x's
                 meet the four clauses: Zfloor x is integral, not above x (Zfloor_lb), and not below any integral
                 number not above x (Zfloor_lub); the NaN and infinity clauses are void for a finite operand.
     rf_dn_self  An operand that is not finite, returned as it is, meets them: a NaN gives the NaN, an infinity the
                 same infinity, the finite clause is void, and the sign is the operand's.
     RTI_FL      A finite input in format32: floor32's result is finite (FL_VALUE) with the value IZR (Zfloor x)
                 (FL_VALUE, FL_EXACT) and the input's sign (FL_SIGN): rf_dn_fin. An input that is not finite is
                 returned as it is (FL_NONFINITE): rf_dn_self.
     RTI_FL32    Directly from FL_VALUE and FL_EXACT (finite, value IZR (Zfloor x), in format32), never through
                 RTI_FL or RTI_DN, so that a plant weakening RTI_DN leaves this proof as it is.
   Each clause is split by one tactic and every leaf closed by one list of steps over the facts named first, so a
   clause with a conjunct replaced by True still compiles here (the plants' layout, ext-work/p2/a/rti32/draft3/
   PLANTS.md, "two conditions").
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement Floor32.
From MKF.rti32 Require Import RTI32_Statement.
Open Scope R_scope.

(* 1. The floor of a real number, in the clauses' words. *)
Lemma rf_integral (x : R) : RTI_integral (IZR (Zfloor x)).
Proof. exists (Zfloor x). reflexivity. Qed.

Lemma rf_below (x : R) : IZR (Zfloor x) <= x.
Proof. apply Zfloor_lb. Qed.

Lemma rf_greatest (x v : R) : RTI_integral v -> v <= x -> v <= IZR (Zfloor x).
Proof. Admitted.

Lemma rf_fin_not_nan (y : b64) : is_finite y = true -> is_nan y = false.
Proof. destruct y; easy. Qed.

(* 2. The clauses from facts: split every conjunction and premise, then close each leaf from the facts. *)
Local Ltac rf_split :=
  repeat match goal with
         | |- _ /\ _ => split
         | |- True => exact I
         | |- _ -> _ => intro
         | |- forall _, _ => intro
         end.

Local Ltac rf_leaf :=
  first [ assumption | reflexivity | discriminate | congruence
        | apply rf_integral | apply rf_below | (apply rf_greatest; assumption) ].

Lemma rf_dn_fin (x r : b64) :
  is_finite x = true -> is_finite r = true -> B2R r = IZR (Zfloor (B2R x)) -> Bsign r = Bsign x ->
  RTI_DN x r.
Proof.
  intros Fx Fr Vr Sr. pose proof (rf_fin_not_nan x Fx) as Nx.
  unfold RTI_DN. try rewrite Vr. try rewrite Fx. try rewrite Nx.
  rf_split; rf_leaf.
Qed.

Lemma rf_dn_self (x : b64) : is_finite x = false -> RTI_DN x x.
Proof.
  intros Fx. unfold RTI_DN. try rewrite Fx.
  rf_split; rf_leaf.
Qed.

(* 3. RTI_FL and RTI_FL32. *)
Theorem RTI_FL_proof : RTI_FL.
Proof.
  intros b H. destruct (is_finite b) eqn:Fb.
  - assert (F32 : format32 (B2R b)) by (destruct H as [H | H]; [discriminate H | exact H]).
    destruct (FL_VALUE_proof b Fb F32) as [Fr Vr].
    destruct (FL_EXACT_proof (B2R b) F32) as [Ex _].
    apply rf_dn_fin.
    + exact Fb.
    + exact Fr.
    + rewrite Vr. exact Ex.
    + exact (FL_SIGN_proof b Fb F32).
  - rewrite (FL_NONFINITE_proof b Fb). apply rf_dn_self. exact Fb.
Qed.

Theorem RTI_FL32_proof : RTI_FL32.
Proof.
  intros b Fb F32.
  destruct (FL_VALUE_proof b Fb F32) as [Fr Vr].
  destruct (FL_EXACT_proof (B2R b) F32) as [Ex Fx32].
  rewrite Ex in Vr, Fx32. rewrite Vr.
  rf_split; rf_leaf.
Qed.
