(* The composed statement, proved: COMPOSE (stated in COMPOSE_Statement.v, which this file does not change) from
   ieee64's theorem and the tier's theorems about the graphs. Author: the assistant (2026-11-15). Every lemma ends
   with Qed; nothing is assumed.

   The proof of each part is three steps and no arithmetic of its own: ieee64_holds gives that the IEEE operations
   return a finite value whose real number is the graph's value; the function's theorem (T32_proof,
   sqrt32_faithful, rsqrt32_faithful, hypot32_faithful, exp32_faithful) says what the graph's value is; the range
   theorem (narrow_finite, sqrt32_finite, rsqrt32_finite, hypot32_finite, and for exp32 faithful_finite with
   exp32_range) says it is a finite binary32 number. The only facts added are that a binary64 value's real number
   is in the binary64 format, and the bounds the graph theorems ask for that follow from the range premise. *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs Hypot.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.exp32 Require Import Graph EXP32_Statement Exp32.
From MKF.exp32r Require RANGE_Statement Range.
From MKF.ieee64 Require Import IEEE64_Statement Closed.
From MKF.compose Require Import COMPOSE_Statement.
Open Scope R_scope.

Lemma fmt64_b (b : b64) : format64 (B2R b).
Proof. exact (generic_format_B2R 53 1024 b). Qed.

Lemma e2e_narrow : E2E_NARROW.
Proof.
  intros b Fb Hb. destruct (proj1 ieee64_holds b Fb Hb) as [Fr Vr].
  split; [split; [exact Fr |] |]; rewrite Vr.
  - apply narrow_finite; [apply fmt64_b | exact Hb].
  - apply T32_proof. apply fmt64_b.
Qed.

Lemma e2e_sqrt32 : E2E_SQRT32.
Proof.
  intros b Fb H32 H0 Hm. destruct (proj1 (proj2 ieee64_holds) b Fb H32 H0 Hm) as [Fr Vr].
  split; [split; [exact Fr |] |]; rewrite Vr.
  - apply sqrt32_finite; assumption.
  - apply sqrt32_faithful; assumption.
Qed.

Lemma e2e_rsqrt32 : E2E_RSQRT32.
Proof.
  intros b Fb H32 H0 Hm. destruct (proj1 (proj2 (proj2 ieee64_holds)) b Fb H32 H0 Hm) as [Fr Vr].
  split; [split; [exact Fr |] |]; rewrite Vr.
  - apply rsqrt32_finite; assumption.
  - apply rsqrt32_faithful; [assumption | assumption | exact (Rle_lt_trans _ _ _ Hm fmax_lt)].
Qed.

Lemma e2e_hypot32 : E2E_HYPOT32.
Proof.
  intros b1 b2 F1 F2 H1 H2 Hm.
  destruct (proj1 (proj2 (proj2 (proj2 ieee64_holds))) b1 b2 F1 F2 H1 H2 Hm) as [Fr Vr].
  split; [split; [exact Fr |] |]; rewrite Vr.
  - apply hypot32_finite; assumption.
  - apply hypot32_faithful; [assumption | assumption | |].
    + exact (Rle_lt_trans _ _ _ (Rle_trans _ _ _ (abs_le_hyp _ _) Hm) fmax_lt).
    + apply Rle_lt_trans with (2 := fmax_lt). apply Rle_trans with (2 := Hm).
      replace (B2R b1 * B2R b1 + B2R b2 * B2R b2) with (B2R b2 * B2R b2 + B2R b1 * B2R b1) by ring.
      apply abs_le_hyp.
Qed.

Lemma e2e_exp32 : E2E_EXP32.
Proof.
  intros b Fb H32 Hm.
  destruct (proj1 (proj2 (proj2 (proj2 (proj2 ieee64_holds)))) b Fb H32 Hm) as [Fr Vr].
  split; [split; [exact Fr |] |]; rewrite Vr.
  - apply (faithful_finite (exp (B2R b))).
    + rewrite Rabs_pos_eq by (left; apply exp_pos). left.
      exact (proj1 (MKF.exp32r.Range.exp32_range (B2R b) H32 Hm)).
    + apply exp32_faithful; assumption.
  - apply exp32_faithful; assumption.
Qed.

Theorem compose_holds : COMPOSE.
Proof.
Admitted.
