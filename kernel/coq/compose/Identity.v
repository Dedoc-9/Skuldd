(* COMPOSE identity check: nothing imported. The definition is typed by the frozen statement's own name, so the
   kernel accepts it only if Compose.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.compose Require COMPOSE_Statement Compose.
Definition identity_check : MKF.compose.COMPOSE_Statement.COMPOSE := MKF.compose.Compose.compose_holds.
Print Assumptions identity_check.
