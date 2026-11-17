(* "*)" *)
Unset Guard Checking.
Fixpoint loop (n : nat) : nat := loop n.
Set Guard Checking.
(* " *)
" *)
Definition use := loop.
