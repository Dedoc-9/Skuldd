(* order32, closed: ORDER32 (stated in ORDER32_Statement.v, which this file does not change) from its eleven parts,
   each a theorem of exactly the statement's part ending with Qed, all in Order32.v: FC_ORD_R, FC_ORD_LEB,
   FC_ORD_NAN, FC_TOTAL_ZERO, FC_TOTAL_NN, FC_DIFF, FC_FIX, FC_EQ_INT, FC_NEG, FC_IDEM and FC_MONO. Nothing is proved
   here but their conjunction, in the statement's own order. Author: the assistant (2026-11-22).

   What order32_holds says and does not say is what the header of ORDER32_Statement.v says, no more. *)
From MKF.order32 Require Import ORDER32_Statement Order32.

Definition ORDER32 : Prop :=
  FC_ORD_R /\ FC_ORD_LEB /\ FC_ORD_NAN /\ FC_TOTAL_NN /\
  FC_DIFF /\ FC_FIX /\ FC_EQ_INT /\ FC_NEG /\ FC_IDEM /\ FC_MONO.

Theorem order32_holds : ORDER32.
Proof.
  exact (conj FC_ORD_R_proof (conj FC_ORD_LEB_proof (conj FC_ORD_NAN_proof
    (conj FC_TOTAL_NN_proof (conj FC_DIFF_proof (conj FC_FIX_proof (conj FC_EQ_INT_proof (conj FC_NEG_proof
    (conj FC_IDEM_proof FC_MONO_proof))))))))).
Qed.
