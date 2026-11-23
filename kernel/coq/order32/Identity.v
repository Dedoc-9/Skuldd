(* ORDER32 identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.order32 Require ORDER32_Statement Closed.
Definition identity_check : MKF.order32.ORDER32_Statement.ORDER32 := MKF.order32.Closed.order32_holds.
Print Assumptions identity_check.
