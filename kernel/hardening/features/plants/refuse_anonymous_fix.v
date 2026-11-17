Definition g : nat -> nat := fix h (n : nat) : nat := match n with O => O | S k => h k end.
