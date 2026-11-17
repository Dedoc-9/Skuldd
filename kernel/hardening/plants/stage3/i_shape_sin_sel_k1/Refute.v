From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
From R4PL.i_shape_sin_sel_k1 Require S.

(* The planted claim IEEE_SINTURN32, written with the planted shape (the planted statement file is cut before
   its first eq_refl tie, where the gate refuses it). Refuted at 1/4 (3E800000). *)
Definition PLANTED : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (S.T_sinturn32 b64 S.tieee_ops b) = true /\
  B2R (S.T_sinturn32 b64 S.tieee_ops b) = g_sinturn32 (B2R b).

Theorem refuted : ~ PLANTED.
Proof.
  intro H.
  destruct (num_f32 1 (-2) false ltac:(vm_compute; reflexivity) ltac:(lia)) as [Fw Pw].
  destruct (H (num 1 (-2) false) Fw Pw) as [HF HP].
  destruct (IEEE_SINTURN32_proof (num 1 (-2) false) Fw Pw) as [FF EF].
  first [ (vm_compute in HF; discriminate HF)
        | (apply (differ _ _ HF FF); [ intro C; vm_compute in C; discriminate C | rewrite HP, EF; reflexivity ]) ].
Qed.
