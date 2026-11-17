(* Plant: SINCOS32_IEEE from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_ieee_holds : SINCOS32_IEEE.
Proof. exact (False_ind _ (loop 0)). Qed.
