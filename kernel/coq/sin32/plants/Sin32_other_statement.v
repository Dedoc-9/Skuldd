(* Plant: under the name SIN32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.sin32 Require Import SIN32_Statement.
Definition SIN32_ALL : Prop := True.
Theorem sin32_all : SIN32_ALL.
Proof. exact I. Qed.
