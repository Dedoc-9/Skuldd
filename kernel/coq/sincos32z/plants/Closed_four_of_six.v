(* Plant: under the name SINCOS32_IEEE_ZERO, a statement of four of the six parts (the two NONFINITE parts left
   out), and its proof. The identity must refuse a theorem of another statement that carries the statement's name. *)
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement Zero.
Definition SINCOS32_IEEE_ZERO : Prop := Z_SIN_VALUE /\ Z_COS_VALUE /\ Z_SIN_ZERO /\ Z_COS_ZERO.
Theorem sincos32_ieee_zero_holds : SINCOS32_IEEE_ZERO.
Proof.
  exact (conj Z_SIN_VALUE_proof (conj Z_COS_VALUE_proof (conj Z_SIN_ZERO_proof Z_COS_ZERO_proof))).
Qed.
