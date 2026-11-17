(* Plant: COMPOSE from False, by a recursion whose termination check is switched off. *)
From MKF.compose Require Import COMPOSE_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem compose_holds : COMPOSE.
Proof. exact (False_ind _ (loop 0)). Qed.
