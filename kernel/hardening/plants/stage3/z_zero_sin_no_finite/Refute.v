From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From R4PL Require Import R4Lib.
From R4PL.z_zero_sin_no_finite Require S.

(* The planted statement's own Z_SIN_ZERO (no premise that the input is finite), at NaN. *)
Theorem refuted : ~ S.Z_SIN_ZERO.
Proof.
  intro H. pose proof (H (@B754_nan 53 1024) f32_nan) as Hw.
  assert (Z0 : sin (2 * PI * B2R (@B754_nan 53 1024)) = 0) by (simpl B2R; rewrite Rmult_0_r; apply sin_0).
  specialize (Hw Z0). vm_compute in Hw. discriminate Hw.
Qed.
