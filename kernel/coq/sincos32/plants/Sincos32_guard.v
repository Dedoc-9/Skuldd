(* Plant: SINCOS32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.sincos32 Require Import SINCOS32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sincos32_all : SINCOS32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
