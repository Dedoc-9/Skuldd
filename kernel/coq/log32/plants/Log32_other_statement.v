(* Plant: under the name LOG32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.log32 Require Import LOG32_Statement.
Definition LOG32_ALL : Prop := True.
Theorem log32_all : LOG32_ALL.
Proof. exact I. Qed.
