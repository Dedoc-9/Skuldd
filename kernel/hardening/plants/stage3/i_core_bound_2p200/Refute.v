From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32 Require Import Graph Sincos32.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps Sincos32_IEEE.
From R4PL Require Import R4Lib.

(* The planted lemma of TOps_core_bound_2p200.v, restated (that planted file is refused while its proof is checked):
   core_den with the bound 2^200 in place of 2^62. Refuted at V = 2^200, where the core is not finite. *)
Definition PLANTED_LEMMA : Prop :=
  forall (V : b64) (v : R), den V v 200 -> den (T_core b64 tieee_ops V) (turn_core v) 952.

Theorem refuted : ~ PLANTED_LEMMA.
Proof.
  intro H.
  destruct (num_exact 1 200 false ltac:(vm_compute; reflexivity) ltac:(lia)) as [F E].
  assert (D : den (num 1 200 false) (IZR 1 * bpow radix2 200) 200).
  { split; [exact F | split; [exact E |]].
    rewrite Rabs_pos_eq by (apply Rmult_le_pos; [simpl; lra | apply bpow_ge_0]). simpl IZR. lra. }
  destruct (H _ _ D) as [HF _]. vm_compute in HF. discriminate HF.
Qed.
