Module M.
  Definition x : nat := 0.
End M.
Import M.
Definition y : nat := M.x.
