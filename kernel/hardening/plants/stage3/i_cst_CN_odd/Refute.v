From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
From R4PL.i_cst_CN_odd Require S.

(* The planted statement's own IEEE_TCST, at the planted constant K_CN. *)
Theorem refuted : ~ S.IEEE_TCST.
Proof.
  intro H. destruct (H S.K_CN) as [HF HP]. destruct (IEEE_TCST_proof K_CN) as [FF EF].
  apply (differ _ _ HF FF).
  - intro C. vm_compute in C. discriminate C.
  - rewrite HP, EF. reflexivity.
Qed.
