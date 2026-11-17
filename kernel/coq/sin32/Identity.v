(* SIN32 identity check: nothing imported; the kernel checks the definition and coqchk rechecks it from the .vo. *)
From MKF.sin32 Require SIN32_Statement Sin32.
Definition identity_check : MKF.sin32.SIN32_Statement.SIN32_ALL := MKF.sin32.Sin32.sin32_all.
Print Assumptions identity_check.
