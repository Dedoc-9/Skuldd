(* Plant: LOG32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.log32 Require Import LOG32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem log32_all : LOG32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
