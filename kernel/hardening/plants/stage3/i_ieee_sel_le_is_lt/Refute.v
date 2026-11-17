From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
From R4PL.i_ieee_sel_le_is_lt Require S.

(* The planted statement's own IEEE_SINTURN32 (its record of operations is the planted one). Refuted at
   0 (00000000). *)
Theorem refuted : ~ S.IEEE_SINTURN32.
Proof.
  intro H.
  destruct (num_f32 0 0 false ltac:(vm_compute; reflexivity) ltac:(lia)) as [Fw Pw].
  destruct (H (num 0 0 false) Fw Pw) as [HF HP].
  destruct (IEEE_SINTURN32_proof (num 0 0 false) Fw Pw) as [FF EF].
  first [ (vm_compute in HF; discriminate HF)
        | (apply (differ _ _ HF FF); [ intro C; vm_compute in C; discriminate C | rewrite HP, EF; reflexivity ]) ].
Qed.
