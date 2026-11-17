(* COS32 identity check: nothing imported; the kernel checks the definition and coqchk rechecks it from the .vo. *)
From MKF.cos32 Require COS32_Statement Cos32.
Definition identity_check : MKF.cos32.COS32_Statement.COS32_ALL := MKF.cos32.Cos32.cos32_all.
Print Assumptions identity_check.
