(* FLOOR32 identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.floor32 Require FLOOR32_Statement Closed.
Definition identity_check : MKF.floor32.FLOOR32_Statement.FLOOR32 := MKF.floor32.Closed.floor32_holds.
Print Assumptions identity_check.
