Definition program : nat := 0.
Goal program = 0. Proof. match goal with |- context [ program ] => reflexivity end. Qed.
Goal True. Proof. solve [ exact I ]. Qed.
