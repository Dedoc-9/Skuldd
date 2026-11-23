(* RTI32 identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.rti32 Require RTI32_Statement Closed.
Definition identity_check : MKF.rti32.RTI32_Statement.RTI32 := MKF.rti32.Closed.rti32_holds.
Print Assumptions identity_check.
