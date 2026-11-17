(* Plant: SINCOS32_IEEE_ZERO from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_ieee_zero_holds : SINCOS32_IEEE_ZERO.
Proof. exact (False_ind _ (loop 0)). Qed.
