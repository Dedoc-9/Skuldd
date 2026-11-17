(* SINCOS32_IEEE_ZERO identity check: nothing imported. The definition is typed by the frozen statement's own name,
   so the kernel accepts it only if Closed.v's theorem has exactly that statement, and coqchk rechecks it from the
   .vo. *)
From MKF.sincos32z Require SINCOS32_IEEE_Zero_Statement Closed.
Definition identity_check : MKF.sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO := MKF.sincos32z.Closed.sincos32_ieee_zero_holds.
Print Assumptions identity_check.
