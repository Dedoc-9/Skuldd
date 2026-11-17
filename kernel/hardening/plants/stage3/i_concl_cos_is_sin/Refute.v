From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.
From R4PL.i_concl_cos_is_sin Require S.

(* The planted statement's own IEEE_COSTURN32 (its conclusion names the sine graph), at 0. *)
Theorem refuted : ~ S.IEEE_COSTURN32.
Proof.
  intro H. destruct (H (@B754_zero 53 1024 false) eq_refl f32_zero) as [HF HP].
  assert (G : g_sinturn32 (B2R (@B754_zero 53 1024 false)) = 0).
  { simpl B2R. destruct (sinturn32_exact 0 0%Z ltac:(apply generic_format_0)) as [Z0 _]. apply Z0. simpl. ring. }
  rewrite G in HP.
  apply (differ (S.T_costurn32 b64 S.tieee_ops (@B754_zero 53 1024 false)) (@B754_zero 53 1024 false) HF eq_refl).
  - intro C. vm_compute in C. discriminate C.
  - rewrite HP. reflexivity.
Qed.
