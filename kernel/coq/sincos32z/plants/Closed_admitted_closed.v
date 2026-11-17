(* The sign of a zero result and the results for infinite and NaN inputs of sinturn32 and costurn32 at the IEEE
   level, closed: SINCOS32_IEEE_ZERO (stated in SINCOS32_IEEE_Zero_Statement.v, which this file does not change)
   from its six parts, each a theorem of Zero.v of exactly the statement's part, ending with Qed. Nothing is
   proved here but their conjunction, in the statement's own order. Author: the assistant (2026-11-16). A scratch
   candidate.

   What sincos32_ieee_zero_holds says and does not say is what the header of SINCOS32_IEEE_Zero_Statement.v says,
   no more. Nothing about the sign of a zero result where the function is not exactly zero, about which NaN, about
   flags, a compiler, a processor or any program. It rests on Flocq's binary_float operations, Bsign, is_nan and
   B754_zero being IEEE 754's. *)
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement Zero.

Theorem sincos32_ieee_zero_holds : SINCOS32_IEEE_ZERO.
Proof.
  exact (conj Z_SIN_VALUE_proof (conj Z_COS_VALUE_proof (conj Z_SIN_ZERO_proof (conj Z_COS_ZERO_proof
    (conj Z_SIN_NONFINITE_proof Z_COS_NONFINITE_proof))))).
Admitted.
