(* Load "x.v". Add LoadPath "d" as L. Add Rec LoadPath "d" as L. Cd "d". Redirect "f" Print nat.
   Extraction nat. Recursive Extraction nat. Extract Constant x => "y". Declare ML Module "p".
   Add ML Path "d". Add Rec ML Path "d". *)
Definition l1 : nat := 0.
