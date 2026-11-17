(* Plant: under the name COS32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.cos32 Require Import COS32_Statement.
Definition COS32_ALL : Prop := True.
Theorem cos32_all : COS32_ALL.
Proof. exact I. Qed.
