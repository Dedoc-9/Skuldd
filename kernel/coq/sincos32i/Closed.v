(* The model-to-binary64 correspondence of sinturn32 and costurn32, closed: SINCOS32_IEEE (stated in
   SINCOS32_IEEE_Statement.v, which this file does not change) from its three parts. Two are Sincos32_IEEE.v's
   theorems (IEEE_SINTURN32, IEEE_COSTURN32) and one is TOps.v's (IEEE_TCST); each is a theorem of exactly the
   statement's part and ends with Qed. Nothing is proved here but their conjunction, in the statement's own order.
   Author: the assistant (2026-11-16). A scratch candidate.

   What sincos32_ieee_holds says and does not say is what the header of SINCOS32_IEEE_Statement.v says, no more:
   for every finite binary64 input that is a binary32 number, Flocq's IEEE binary64 operations in round to nearest
   even, in the graph's order, return a finite value whose real number is the graph's. Nothing about the sign of a
   zero, about inputs that are not binary32 numbers, about NaN or infinite inputs, about the value a selection
   does not return, about a compiler, a processor or any program. It rests on Flocq's binary_float operations
   being IEEE 754's. *)
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.

Theorem sincos32_ieee_holds : SINCOS32_IEEE.
Proof.
  exact (conj IEEE_SINTURN32_proof (conj IEEE_COSTURN32_proof IEEE_TCST_proof)).
Qed.
