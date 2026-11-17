Inductive t : Set := A | B.
Scheme t_ind2 := Induction for t Sort Prop.
