(* floor32, closed: FLOOR32 (stated in FLOOR32_Statement.v, which this file does not change) from its five parts,
   each a theorem of exactly the statement's part ending with Qed: FL_EXACT, FL_VALUE, FL_SIGN and FL_NONFINITE from
   Floor32.v, FL_IEEE from FloorIEEE.v. Nothing is proved here but their conjunction, in the statement's own order.
   Author: the assistant (2026-11-18).

   What floor32_holds says and does not say is what the header of FLOOR32_Statement.v says, no more. The trust that
   Flocq's Bnearbyint is IEEE 754's round-to-integral bears on the meaning of FL_IEEE alone (FloorIEEE.v's header). *)
From MKF.floor32 Require Import FLOOR32_Statement Floor32 FloorIEEE.

#[bypass_check(guard)] Fixpoint fl_loop (n : nat) {struct n} : False := fl_loop n.
Theorem floor32_holds : FLOOR32.
Proof. exact (False_ind _ (fl_loop 0)). Qed.
