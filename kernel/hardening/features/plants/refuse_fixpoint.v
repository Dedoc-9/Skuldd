Fixpoint f (n : nat) : nat := match n with O => O | S k => f k end.
