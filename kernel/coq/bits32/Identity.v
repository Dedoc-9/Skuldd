(* BITS32 identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.bits32 Require BITS32_Statement Closed.
Definition identity_check : MKF.bits32.BITS32_Statement.BITS32 := MKF.bits32.Closed.bits32_holds.
Print Assumptions identity_check.
