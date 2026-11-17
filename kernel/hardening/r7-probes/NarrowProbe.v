(* R7 probe (2026-11-17, scratch; written by the assistant). Is the turns record's narrow the same term as the five
   functions' narrow at binary64? The local inventory of the R7 research argued yes, untested. Predictions, written
   before the run:
   N1 IEEE_TNARROW is proved by IEEE_NARROW_proof itself (exact): compiles.
   N2 T_narrow at tieee_ops and G_narrow at ieee_ops are equal by eq_refl: compiles.
   N3 negative control: T_narrow at tieee_ops is not the identity by eq_refl: the Fail command succeeds.
   N4 Print Assumptions of N1 and N2: no axiom outside the four of the tier. *)
From MKF.ieee64 Require Import IEEE64_Statement P32_IEEE.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement Sincos32_IEEE.

Lemma tnarrow_by_conversion : IEEE_TNARROW.
Proof. exact IEEE_NARROW_proof. Qed.

Example narrow_same : T_narrow b64 tieee_ops = G_narrow b64 ieee_ops := eq_refl.

Fail Example narrow_not_id : T_narrow b64 tieee_ops = (fun v : b64 => v) := eq_refl.

Print Assumptions tnarrow_by_conversion.
Print Assumptions narrow_same.
