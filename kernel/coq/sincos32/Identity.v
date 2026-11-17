(* SINCOS32 identity check: nothing imported; the kernel checks the definition and coqchk rechecks it from the .vo. *)
From MKF.sincos32 Require SINCOS32_Statement Sincos32.
Definition identity_check : MKF.sincos32.SINCOS32_Statement.SINCOS32_ALL := MKF.sincos32.Sincos32.sincos32_all.
Print Assumptions identity_check.
