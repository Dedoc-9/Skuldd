(* ceil32, closed: CEIL32 (stated in CEIL32_Statement.v, which this file does not change) from its five parts,
   each a theorem of exactly the statement's part ending with Qed: CL_EXACT, CL_VALUE, CL_SIGN and CL_NONFINITE from
   Ceil32.v, CL_IEEE from CeilIEEE.v. Nothing is proved here but their conjunction, in the statement's own order.
   Author: the assistant (2026-11-18).

   What ceil32_holds says and does not say is what the header of CEIL32_Statement.v says, no more. The trust that
   Flocq's Bnearbyint is IEEE 754's round-to-integral bears on the meaning of CL_IEEE alone (CeilIEEE.v's header). *)
From MKF.ceil32 Require Import CEIL32_Statement Ceil32 CeilIEEE.

#[bypass_check(guard)] Fixpoint cl_loop (n : nat) {struct n} : False := cl_loop n.
Theorem ceil32_holds : CEIL32.
Proof. exact (False_ind _ (cl_loop 0)). Qed.
