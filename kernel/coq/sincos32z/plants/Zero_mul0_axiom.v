(* Zero.v: proofs of the six parts of SINCOS32_IEEE_ZERO (statement in SINCOS32_IEEE_Zero_Statement.v, which this
   file does not change). Flocq and the standard library only; every lemma ends with Qed and nothing is assumed.
   Author: the assistant (2026-11-16). A scratch candidate.

   How it goes. The step is two operations after the frozen shape; each step lemma below is about the step alone,
   for ANY binary64 value y in the place of the frozen shape's result, by cases on the constructors of y and of
   the input b (Flocq's operations compute on constructors; no rounding lemma is used).
     VALUE      y is finite with real number g (sincos32i's IEEE_SINTURN32_proof / IEEE_COSTURN32_proof).
                Sine: a zero y selects b * +0, a zero (real number 0 = g); a finite y that is not a zero is
                returned. Cosine: |b| * +0 is +0 for a finite b; y + +0 is +0 for a zero y and y otherwise.
     ZERO       sin (2 PI x) = 0 gives g_sinturn32 x = 0 (Sincos32.sinturn32_faithful and faithful_fmt: a faithful
                rounding of the binary32 number 0 is 0); so y is finite with real number 0, hence a zero of some
                sign (a B754_finite has a positive mantissa). Sine: b * +0 is the zero with the sign of b.
                Cosine: (a zero) + +0 is +0 in round to nearest even.
     NONFINITE  Cosine: |b| * +0 is NaN for an infinite or NaN b, and y + NaN is NaN for every y: nothing is
                asked of the frozen shape's result. Sine: the stepped shape is evaluated by the kernel
                (vm_compute) on the four values B754_infinity true, B754_infinity false, B754_nan: all NaN.
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.sincos32 Require Import Graph SINCOS32_Statement Sincos32.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement Sincos32_IEEE.
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement.
Open Scope R_scope.

(* A finite binary64 value whose real number is 0 is a zero. *)
Lemma fin_zero (y : b64) : is_finite y = true -> B2R y = 0 -> exists s : bool, y = @B754_zero 53 1024 s.
Proof.
  destruct y as [s | s | | s m e H]; intros Fy Vy; try discriminate Fy.
  - exists s. reflexivity.
  - exfalso. simpl in Vy. apply eq_0_F2R in Vy. simpl in Vy. destruct s; discriminate Vy.
Qed.

(* |b| * +0 for a finite b is +0. *)
Lemma absmul0 (b : b64) : is_finite b = true ->
  t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0) = @B754_zero 53 1024 false.
Proof. destruct b as [s | s | | s m e H]; intros Fb; try discriminate Fb; reflexivity. Qed.

(* |b| * +0 for a b that is not finite is NaN. *)
Lemma absmul0_nan (b : b64) : is_finite b = false ->
  t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0) = @B754_nan 53 1024.
Proof. destruct b as [s | s | | s m e H]; intros Fb; try discriminate Fb; reflexivity. Qed.

(* b * +0 for a finite b is the zero with the sign of b. *)
Axiom mul0 : forall b : b64, is_finite b = true ->
  t_mul tieee_ops b (t_cst tieee_ops K_0) = @B754_zero 53 1024 (Bsign b).

(* The sine's step. *)
Lemma zsin_value (b y : b64) (g : R) : is_finite b = true -> is_finite y = true -> B2R y = g ->
  is_finite (t_sel_le tieee_ops (t_abs tieee_ops y) (t_cst tieee_ops K_0) (t_mul tieee_ops b (t_cst tieee_ops K_0)) y) = true /\
  B2R (t_sel_le tieee_ops (t_abs tieee_ops y) (t_cst tieee_ops K_0) (t_mul tieee_ops b (t_cst tieee_ops K_0)) y) = g.
Proof.
  intros Fb Fy Vy. rewrite (mul0 b Fb).
  destruct y as [s | s | | s m e H]; try discriminate Fy.
  - split; [reflexivity | exact Vy].
  - split; [reflexivity | exact Vy].
Qed.

Lemma zsin_zero (b y : b64) : is_finite b = true -> is_finite y = true -> B2R y = 0 ->
  t_sel_le tieee_ops (t_abs tieee_ops y) (t_cst tieee_ops K_0) (t_mul tieee_ops b (t_cst tieee_ops K_0)) y
  = @B754_zero 53 1024 (Bsign b).
Proof.
  intros Fb Fy Vy. rewrite (mul0 b Fb). destruct (fin_zero y Fy Vy) as [s E]. rewrite E. reflexivity.
Qed.

(* The cosine's step. *)
Lemma zcos_value (b y : b64) (g : R) : is_finite b = true -> is_finite y = true -> B2R y = g ->
  is_finite (t_add tieee_ops y (t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0))) = true /\
  B2R (t_add tieee_ops y (t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0))) = g.
Proof.
  intros Fb Fy Vy. rewrite (absmul0 b Fb).
  destruct y as [s | s | | s m e H]; try discriminate Fy.
  - split; [destruct s; reflexivity | rewrite <- Vy; destruct s; reflexivity].
  - split; [reflexivity | exact Vy].
Qed.

Lemma zcos_zero (b y : b64) : is_finite b = true -> is_finite y = true -> B2R y = 0 ->
  t_add tieee_ops y (t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0)) = @B754_zero 53 1024 false.
Proof.
  intros Fb Fy Vy. rewrite (absmul0 b Fb). destruct (fin_zero y Fy Vy) as [s E]. rewrite E.
  destruct s; reflexivity.
Qed.

Lemma zcos_nan (b y : b64) : is_finite b = false ->
  is_nan (t_add tieee_ops y (t_mul tieee_ops (t_abs tieee_ops b) (t_cst tieee_ops K_0))) = true.
Proof.
  intros Fb. rewrite (absmul0_nan b Fb). destruct y as [s | s | | s m e H]; reflexivity.
Qed.

(* Exact zeros of the graphs. *)
Lemma g_sin_zero (x : R) : format32 x -> sin (2 * PI * x) = 0 -> g_sinturn32 x = 0.
Proof.
  intros Fx V. pose proof (sinturn32_faithful x Fx) as H. rewrite V in H.
  exact (faithful_fmt 0 _ (generic_format_0 radix2 fexp32) H).
Qed.

Lemma g_cos_zero (x : R) : format32 x -> cos (2 * PI * x) = 0 -> g_costurn32 x = 0.
Proof.
  intros Fx V. pose proof (costurn32_faithful x Fx) as H. rewrite V in H.
  exact (faithful_fmt 0 _ (generic_format_0 radix2 fexp32) H).
Qed.

(* The six parts. *)
Theorem Z_SIN_VALUE_proof : Z_SIN_VALUE.
Proof.
  intros b Fb F32. destruct (IEEE_SINTURN32_proof b Fb F32) as [Fy Vy].
  unfold Z_sinturn32. exact (zsin_value b _ _ Fb Fy Vy).
Qed.

Theorem Z_COS_VALUE_proof : Z_COS_VALUE.
Proof.
  intros b Fb F32. destruct (IEEE_COSTURN32_proof b Fb F32) as [Fy Vy].
  unfold Z_costurn32. exact (zcos_value b _ _ Fb Fy Vy).
Qed.

Theorem Z_SIN_ZERO_proof : Z_SIN_ZERO.
Proof.
  intros b Fb F32 V. destruct (IEEE_SINTURN32_proof b Fb F32) as [Fy Vy].
  rewrite (g_sin_zero (B2R b) F32 V) in Vy.
  unfold Z_sinturn32. exact (zsin_zero b _ Fb Fy Vy).
Qed.

Theorem Z_COS_ZERO_proof : Z_COS_ZERO.
Proof.
  intros b Fb F32 V. destruct (IEEE_COSTURN32_proof b Fb F32) as [Fy Vy].
  rewrite (g_cos_zero (B2R b) F32 V) in Vy.
  unfold Z_costurn32. exact (zcos_zero b _ Fb Fy Vy).
Qed.

Theorem Z_SIN_NONFINITE_proof : Z_SIN_NONFINITE.
Proof.
  intros b Fb. destruct b as [s | s | | s m e H]; try discriminate Fb.
  - destruct s; vm_compute; reflexivity.
  - vm_compute; reflexivity.
Qed.

Theorem Z_COS_NONFINITE_proof : Z_COS_NONFINITE.
Proof.
  intros b Fb. unfold Z_costurn32. exact (zcos_nan b _ Fb).
Qed.
