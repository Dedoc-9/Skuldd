(* R4 (e): kernel-checked examples about the two frozen candidates SINCOS32_IEEE (sincos32i) and SINCOS32_IEEE_ZERO
   (sincos32z), whose statement files are imported and not changed. Values a reader can check by eye. Each value
   example is proved by vm_compute (never native_compute), which coqchk checks again with its own conversion. The
   results are compared through B2SF (sign, significand, exponent), so no proof term inside a datum matters.
   Scratch; written by the assistant (2026-11-16). *)
From Coq Require Import ZArith Reals SpecFloat.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement.

(* m * 2^e as a binary64 datum, a zero taking the sign s *)
Definition num (m e : Z) (s : bool) : b64 :=
  @binary_normalize 53 1024 prec64_gt_0 prec64_lt_emax mode_NE m e s.
Definition sinT (x : b64) : spec_float := B2SF (T_sinturn32 b64 tieee_ops x).
Definition cosT (x : b64) : spec_float := B2SF (T_costurn32 b64 tieee_ops x).
Definition sinZ (x : b64) : spec_float := B2SF (Z_sinturn32 b64 tieee_ops x).
Definition cosZ (x : b64) : spec_float := B2SF (Z_costurn32 b64 tieee_ops x).
Definition ONE : spec_float := S754_finite false 4503599627370496 (-52).
Definition MINUS_ONE : spec_float := S754_finite true 4503599627370496 (-52).

(* 1. The premises of the statements are met: +0 is a finite binary64 datum whose number is a binary32 number. *)
Example premise_inhabited : exists b : b64, is_finite b = true /\ format32 (B2R b).
Proof. exists (@B754_zero 53 1024 false). split; [reflexivity | apply generic_format_0]. Qed.
Example nonfinite_premise_inhabited : exists b : b64, is_finite b = false.
Proof. exists (@B754_nan 53 1024). reflexivity. Qed.

(* 2. The IEEE-level shapes (SINCOS32_IEEE). *)
Example sin_at_quarter : sinT (num 1 (-2) false) = ONE.                       Proof. vm_compute. reflexivity. Qed.
Example sin_at_three_quarters : sinT (num 3 (-2) false) = MINUS_ONE.          Proof. vm_compute. reflexivity. Qed.
Example cos_at_zero : cosT (num 0 0 false) = ONE.                             Proof. vm_compute. reflexivity. Qed.
Example cos_at_half : cosT (num 1 (-1) false) = MINUS_ONE.                    Proof. vm_compute. reflexivity. Qed.
Example cos_at_one : cosT (num 1 0 false) = ONE.                              Proof. vm_compute. reflexivity. Qed.
(* sin (2 pi 2^-149) is about 6.283 * 2^-149; the shape gives 6 * 2^-149 = 3 * 2^51 * 2^-199 *)
Example sin_at_smallest : sinT (num 1 (-149) false) = S754_finite false 6755399441055744 (-199).
Proof. vm_compute. reflexivity. Qed.
(* the unstepped shapes' zero signs, which the zero layer corrects (SINCOS32_IEEE_Zero_Statement.v, lines 8-11) *)
Example unstepped_sin_at_half : sinT (num 1 (-1) false) = S754_zero true.      Proof. vm_compute. reflexivity. Qed.
Example unstepped_cos_at_quarter : cosT (num 1 (-2) false) = S754_zero true.   Proof. vm_compute. reflexivity. Qed.

(* 3. The stepped shapes (SINCOS32_IEEE_ZERO): zeros with the stated signs, NaN at the non-finite inputs. *)
Example zsin_at_plus_zero : sinZ (num 0 0 false) = S754_zero false.            Proof. vm_compute. reflexivity. Qed.
Example zsin_at_minus_zero : sinZ (num 0 0 true) = S754_zero true.             Proof. vm_compute. reflexivity. Qed.
Example zsin_at_half : sinZ (num 1 (-1) false) = S754_zero false.              Proof. vm_compute. reflexivity. Qed.
Example zsin_at_minus_half : sinZ (num (-1) (-1) false) = S754_zero true.      Proof. vm_compute. reflexivity. Qed.
Example zsin_at_minus_one : sinZ (num (-1) 0 false) = S754_zero true.          Proof. vm_compute. reflexivity. Qed.
Example zcos_at_quarter : cosZ (num 1 (-2) false) = S754_zero false.           Proof. vm_compute. reflexivity. Qed.
Example zcos_at_three_quarters : cosZ (num 3 (-2) false) = S754_zero false.    Proof. vm_compute. reflexivity. Qed.
Example zcos_at_minus_quarter : cosZ (num (-1) (-2) false) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
Example zsin_at_quarter : sinZ (num 1 (-2) false) = ONE.                       Proof. vm_compute. reflexivity. Qed.
Example zcos_at_half : cosZ (num 1 (-1) false) = MINUS_ONE.                    Proof. vm_compute. reflexivity. Qed.
Example zsin_at_plus_inf : sinZ (@B754_infinity 53 1024 false) = S754_nan.     Proof. vm_compute. reflexivity. Qed.
Example zcos_at_plus_inf : cosZ (@B754_infinity 53 1024 false) = S754_nan.     Proof. vm_compute. reflexivity. Qed.
Example zcos_at_minus_inf : cosZ (@B754_infinity 53 1024 true) = S754_nan.     Proof. vm_compute. reflexivity. Qed.
Example zsin_at_nan : sinZ (@B754_nan 53 1024) = S754_nan.                     Proof. vm_compute. reflexivity. Qed.
(* the frozen unstepped cosine of an infinity is 1, which the step turns into NaN *)
Example unstepped_cos_at_plus_inf : cosT (@B754_infinity 53 1024 false) = ONE. Proof. vm_compute. reflexivity. Qed.

Definition ALL_EXAMPLES : Prop := True.
