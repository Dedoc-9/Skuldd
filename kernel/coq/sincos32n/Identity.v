(* SINCOS32N identity check: nothing imported. The definition is typed by the frozen statement's own name, so the
   kernel accepts it only if Nonzero.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.sincos32n Require SINCOS32_NONZERO_Statement Nonzero.
Definition identity_check : MKF.sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO :=
  MKF.sincos32n.Nonzero.sincos32_nonzero.
Print Assumptions identity_check.
