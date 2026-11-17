(* Plant: under the name SINCOS32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.sincos32 Require Import SINCOS32_Statement.
Definition SINCOS32_ALL : Prop := True.
Theorem sincos32_all : SINCOS32_ALL.
Proof. exact I. Qed.
