(* CEIL32 identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.ceil32 Require CEIL32_Statement Closed.
Definition identity_check : MKF.ceil32.CEIL32_Statement.CEIL32 := MKF.ceil32.Closed.ceil32_holds.
Print Assumptions identity_check.
