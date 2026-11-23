Ltac say := idtac "Conjectures c : False. Context (n : nat). Declare Instance i : C. Admit Obligations.
Obligation 1. Next Obligation. Final Obligation. Solve Obligations. Solve All Obligations.
Obligation Tactic := idtac. #[program] Definition p := 0." "and ""#[local, program]"" quoted".
Goal True. Proof. say. exact I. Qed.
