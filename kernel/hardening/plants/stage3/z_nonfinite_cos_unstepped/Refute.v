From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From R4PL Require Import R4Lib.
From R4PL.z_nonfinite_cos_unstepped Require S.

(* The planted statement's own Z_COS_NONFINITE (claimed of the unstepped cosine), at +infinity. *)
Theorem refuted : ~ S.Z_COS_NONFINITE.
Proof.
  intro H. pose proof (H (@B754_infinity 53 1024 false) eq_refl) as Hw. vm_compute in Hw. discriminate Hw.
Qed.
