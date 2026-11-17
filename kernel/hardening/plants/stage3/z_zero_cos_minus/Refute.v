From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From R4PL Require Import R4Lib.
From R4PL.z_zero_cos_minus Require S.

(* The planted statement's own Z_COS_ZERO, at 1/4 (3E800000). *)
Theorem refuted : ~ S.Z_COS_ZERO.
Proof.
  intro H.
  destruct (num_f32 1 (-2) false ltac:(vm_compute; reflexivity) ltac:(lia)) as [Fw Pw].
  pose proof (H (num 1 (-2) false) Fw Pw) as Hw.
  rewrite (num_value 1 (-2) false ltac:(vm_compute; reflexivity) ltac:(lia)) in Hw.
  specialize (Hw cos_at_quarter). vm_compute in Hw. discriminate Hw.
Qed.
