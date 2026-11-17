(* SINCOS32_IEEE identity check: nothing imported. The definition is typed by the frozen statement's own name, so
   the kernel accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.sincos32i Require SINCOS32_IEEE_Statement Closed.
Definition identity_check : MKF.sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE := MKF.sincos32i.Closed.sincos32_ieee_holds.
Print Assumptions identity_check.
