From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
From R4PL.i_prem_sin_no_finite Require S.

(* The planted statement's own IEEE_SINTURN32 (no premise that the input is finite), at NaN. *)
Theorem refuted : ~ S.IEEE_SINTURN32.
Proof.
  intro H. destruct (H (@B754_nan 53 1024) f32_nan) as [HF _]. vm_compute in HF. discriminate HF.
Qed.
