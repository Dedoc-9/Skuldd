(* rti32, closed: RTI32 (stated in RTI32_Statement.v, which this file does not change) from its five parts, each a
   theorem of exactly the statement's part ending with Qed: RTI_FL and RTI_FL32 from FloorRTI.v, RTI_CL and RTI_CL32
   from CeilRTI.v, RTI_BN from BnRTI.v. Nothing is proved here but their conjunction, in the statement's own order.
   Author: the assistant (2026-11-22).

   What rti32_holds says and does not say is what the header of RTI32_Statement.v says, no more. That RTI_DN and
   RTI_UP say what IEEE 754's clauses say is the header's trust, a reader's judgment, not a theorem. *)
From MKF.rti32 Require Import RTI32_Statement FloorRTI CeilRTI BnRTI.

Definition RTI32 : Prop := RTI_FL /\ RTI_CL /\ RTI_FL32 /\ RTI_CL32.

Theorem rti32_holds : RTI32.
Proof.
  exact (conj RTI_FL_proof (conj RTI_CL_proof (conj RTI_FL32_proof RTI_CL32_proof))).
Qed.
