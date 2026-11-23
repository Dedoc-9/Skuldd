(* EXP32A identity check: nothing imported. The definition is typed by the frozen statement's own name, so the kernel
   accepts it only if Exp32Adj.v's theorem has exactly that statement, and coqchk rechecks it from the .vo. *)
From MKF.exp32a Require EXP32_ADJ_Statement Exp32Adj.
Definition identity_check : MKF.exp32a.EXP32_ADJ_Statement.EXP32_ADJ := MKF.exp32a.Exp32Adj.exp32_adj.
Print Assumptions identity_check.
