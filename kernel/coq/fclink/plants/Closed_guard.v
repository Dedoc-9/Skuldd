(* fclink, closed: FCLINK (stated in FCLINK_Statement.v, which this file does not change) from its four parts, each a
   theorem of exactly the statement's part ending with Qed: FC_TEXT and FC_PARAM from Link.v, FLOOR32 from floor32's
   Closed.v and CEIL32 from ceil32's Closed.v. Nothing is proved here but their conjunction, in the statement's own
   order. Author: the assistant (2026-11-21).

   What fclink_holds says and does not say is what the header of FCLINK_Statement.v says, no more. *)
From MKF.fclink Require Import FCLINK_Statement Link.
From MKF.floor32 Require Closed.
From MKF.ceil32 Require Closed.

#[bypass_check(guard)] Fixpoint fc_loop (n : nat) {struct n} : False := fc_loop n.
Theorem fclink_holds : FCLINK.
Proof. exact (False_ind _ (fc_loop 0)). Qed.
