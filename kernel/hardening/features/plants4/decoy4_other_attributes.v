#[local] Definition a : nat := 0.
#[deprecated(since="1", note="use b")] Definition a2 : nat := a.
#[global] Hint Unfold a : core.
Definition program_name : nat := 1.
