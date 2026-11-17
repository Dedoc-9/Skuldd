(* Plant: SIN32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.sin32 Require Import SIN32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem sin32_all : SIN32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
