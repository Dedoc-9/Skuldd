(* Plant: under the name SINCOS32_IEEE, a statement of two of the three parts (IEEE_TCST left out), and its
   proof. The identity must refuse a theorem of another statement that carries the statement's name. *)
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
Definition SINCOS32_IEEE : Prop := IEEE_SINTURN32 /\ IEEE_COSTURN32.
Theorem sincos32_ieee_holds : SINCOS32_IEEE.
Proof. exact (conj IEEE_SINTURN32_proof IEEE_COSTURN32_proof). Qed.
