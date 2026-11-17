(* The unusual input +2^106, kernel-checked (2026-11-17, scratch; written by the assistant). The frozen turns kernel
   reduces x by N(x) = (x + CN) - CN with CN = 3 * 2^51, then f = x - N, q = 4 f, k = N(q), r = q - k; for
   |x| >= 2^23 (K_BIG) its selections discard all of these (the sine selects x * 0, the cosine 1).
   Predictions, written before the run (from the T2 sweep and the law sidecar's argument):
   P1 at +2^106: N = 2^106 - 2^53, f = 2^53, q = k = 2^55, r = +0; sinpre +0, cospre 1; T_sinturn32 +0,
      T_costurn32 1; the stepped Z_sinturn32 +0, Z_costurn32 1.
   P2 at -2^106: N = x, f = q = k = r = +0; sinpre -0, cospre 1; T_sinturn32 -0, T_costurn32 1; Z_sinturn32 -0,
      Z_costurn32 1.
   P3 at the binade bottoms +2^104, +2^105, +2^107 and at the binary32 neighbours of +2^106 (0x747FFFFF and
      0x74800001): N = x and r = +0.
   P4 every example is closed by vm_compute; Print Assumptions lists nothing outside the tier's four axioms. *)
From Coq Require Import ZArith SpecFloat.
From Flocq Require Import Core BinarySingleNaN.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.sincos32z Require Import SINCOS32_IEEE_Zero_Statement.

Definition p104 : b64 := @B754_finite 53 1024 false (2 ^ 52)%positive 52%Z eq_refl.
Definition p105 : b64 := @B754_finite 53 1024 false (2 ^ 52)%positive 53%Z eq_refl.
Definition p106 : b64 := @B754_finite 53 1024 false (2 ^ 52)%positive 54%Z eq_refl.
Definition m106 : b64 := @B754_finite 53 1024 true (2 ^ 52)%positive 54%Z eq_refl.
Definition p107 : b64 := @B754_finite 53 1024 false (2 ^ 52)%positive 55%Z eq_refl.
Definition below106 : b64 := @B754_finite 53 1024 false (16777215 * 2 ^ 29)%positive 53%Z eq_refl.
Definition above106 : b64 := @B754_finite 53 1024 false (8388609 * 2 ^ 29)%positive 54%Z eq_refl.

Definition ONE : spec_float := S754_finite false (2 ^ 52)%positive (-52)%Z.

(* P1 *)
Example n_p106 : B2SF (T_N b64 tieee_ops p106) = S754_finite false 9007199254740991%positive 53%Z.
Proof. vm_compute. reflexivity. Qed.
Example f_p106 : B2SF (T_f b64 tieee_ops p106) = S754_finite false (2 ^ 52)%positive 1%Z.
Proof. vm_compute. reflexivity. Qed.
Example q_p106 : B2SF (T_q b64 tieee_ops p106) = S754_finite false (2 ^ 52)%positive 3%Z.
Proof. vm_compute. reflexivity. Qed.
Example k_p106 : B2SF (T_k b64 tieee_ops p106) = S754_finite false (2 ^ 52)%positive 3%Z.
Proof. vm_compute. reflexivity. Qed.
Example r_p106 : B2SF (T_r b64 tieee_ops p106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example sinpre_p106 : B2SF (T_sinpre b64 tieee_ops p106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example cospre_p106 : B2SF (T_cospre b64 tieee_ops p106) = ONE.
Proof. vm_compute. reflexivity. Qed.
Example sin_p106 : B2SF (T_sinturn32 b64 tieee_ops p106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example cos_p106 : B2SF (T_costurn32 b64 tieee_ops p106) = ONE.
Proof. vm_compute. reflexivity. Qed.
Example zsin_p106 : B2SF (Z_sinturn32 b64 tieee_ops p106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example zcos_p106 : B2SF (Z_costurn32 b64 tieee_ops p106) = ONE.
Proof. vm_compute. reflexivity. Qed.

(* P2 *)
Example n_m106 : B2SF (T_N b64 tieee_ops m106) = B2SF m106.
Proof. vm_compute. reflexivity. Qed.
Example f_m106 : B2SF (T_f b64 tieee_ops m106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example q_m106 : B2SF (T_q b64 tieee_ops m106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example k_m106 : B2SF (T_k b64 tieee_ops m106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example r_m106 : B2SF (T_r b64 tieee_ops m106) = S754_zero false.
Proof. vm_compute. reflexivity. Qed.
Example sinpre_m106 : B2SF (T_sinpre b64 tieee_ops m106) = S754_zero true.
Proof. vm_compute. reflexivity. Qed.
Example cospre_m106 : B2SF (T_cospre b64 tieee_ops m106) = ONE.
Proof. vm_compute. reflexivity. Qed.
Example sin_m106 : B2SF (T_sinturn32 b64 tieee_ops m106) = S754_zero true.
Proof. vm_compute. reflexivity. Qed.
Example cos_m106 : B2SF (T_costurn32 b64 tieee_ops m106) = ONE.
Proof. vm_compute. reflexivity. Qed.
Example zsin_m106 : B2SF (Z_sinturn32 b64 tieee_ops m106) = S754_zero true.
Proof. vm_compute. reflexivity. Qed.
Example zcos_m106 : B2SF (Z_costurn32 b64 tieee_ops m106) = ONE.
Proof. vm_compute. reflexivity. Qed.

(* P3 *)
Example n_p104 : B2SF (T_N b64 tieee_ops p104) = B2SF p104.  Proof. vm_compute. reflexivity. Qed.
Example n_p105 : B2SF (T_N b64 tieee_ops p105) = B2SF p105.  Proof. vm_compute. reflexivity. Qed.
Example n_p107 : B2SF (T_N b64 tieee_ops p107) = B2SF p107.  Proof. vm_compute. reflexivity. Qed.
Example n_below106 : B2SF (T_N b64 tieee_ops below106) = B2SF below106.  Proof. vm_compute. reflexivity. Qed.
Example n_above106 : B2SF (T_N b64 tieee_ops above106) = B2SF above106.  Proof. vm_compute. reflexivity. Qed.
Example r_p104 : B2SF (T_r b64 tieee_ops p104) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
Example r_p105 : B2SF (T_r b64 tieee_ops p105) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
Example r_p107 : B2SF (T_r b64 tieee_ops p107) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
Example r_below106 : B2SF (T_r b64 tieee_ops below106) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
Example r_above106 : B2SF (T_r b64 tieee_ops above106) = S754_zero false.  Proof. vm_compute. reflexivity. Qed.
