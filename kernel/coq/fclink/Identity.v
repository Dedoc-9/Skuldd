(* FCLINK identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.fclink Require FCLINK_Statement Closed.
Definition identity_check : MKF.fclink.FCLINK_Statement.FCLINK := MKF.fclink.Closed.fclink_holds.
Print Assumptions identity_check.
