(* LOG32 identity check: nothing imported; the kernel checks the definition and coqchk rechecks it from the .vo. *)
From MKF.log32 Require LOG32_Statement Log32.
Definition identity_check : MKF.log32.LOG32_Statement.LOG32_ALL := MKF.log32.Log32.log32_all.
Print Assumptions identity_check.
