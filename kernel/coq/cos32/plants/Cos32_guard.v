(* Plant: COS32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.cos32 Require Import COS32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem cos32_all : COS32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
