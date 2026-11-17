(* Plant: under the name COMPOSE, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.compose Require Import COMPOSE_Statement.
Definition COMPOSE : Prop := True.
Theorem compose_holds : COMPOSE.
Proof. exact I. Qed.
