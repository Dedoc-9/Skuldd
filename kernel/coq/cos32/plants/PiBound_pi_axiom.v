(* The one fact about pi that COS32 needs: the two constants of the shift add up to PI/2 within 2^-60 (pi_fact).
   Standard library only; nothing is admitted. Method (Trunc.v's, at two concrete rationals):
     Q1 = 7244019458077122842 / 2^62 and Q2 = Q1 + 2^-62 (pi/2 lies between them; ../pi_grid.py found them);
     the library's alternating bounds for cos (pre_cos_bound, n = 6): the partial sum through a^26 is below cos a,
     and that sum plus a^28/28! is above it; in nested form, Cex (a^2) (capprox13, capprox14);
     at Q1 the lower sum is positive (exact rational arithmetic, by lra), so cos Q1 > 0 and Q1 < PI/2;
     at Q2 the upper sum is negative, so cos Q2 < 0 and PI/2 < Q2.
   CoqInterval is not used: its default route brings the Uint63 axioms into Print Assumptions (measured). *)
From Coq Require Import Reals ZArith Lia Lra.
From MKF.sin32 Require Import Trunc.
From MKF.cos32 Require Import Graph.
Open Scope R_scope.

(* Factorials as numerals, continuing Trunc.v's F1 .. F17. *)
Lemma F0 : INR (fact 0) = 1.
Proof. reflexivity. Qed.
Lemma F18 : INR (fact 18) = 6402373705728000.
Proof. rewrite (fact_S_INR 17 355687428096000 F17), (inr_lit 18 18 eq_refl). lra. Qed.
Lemma F19 : INR (fact 19) = 121645100408832000.
Proof. rewrite (fact_S_INR 18 6402373705728000 F18), (inr_lit 19 19 eq_refl). lra. Qed.
Lemma F20 : INR (fact 20) = 2432902008176640000.
Proof. rewrite (fact_S_INR 19 121645100408832000 F19), (inr_lit 20 20 eq_refl). lra. Qed.
Lemma F21 : INR (fact 21) = 51090942171709440000.
Proof. rewrite (fact_S_INR 20 2432902008176640000 F20), (inr_lit 21 21 eq_refl). lra. Qed.
Lemma F22 : INR (fact 22) = 1124000727777607680000.
Proof. rewrite (fact_S_INR 21 51090942171709440000 F21), (inr_lit 22 22 eq_refl). lra. Qed.
Lemma F23 : INR (fact 23) = 25852016738884976640000.
Proof. rewrite (fact_S_INR 22 1124000727777607680000 F22), (inr_lit 23 23 eq_refl). lra. Qed.
Lemma F24 : INR (fact 24) = 620448401733239439360000.
Proof. rewrite (fact_S_INR 23 25852016738884976640000 F23), (inr_lit 24 24 eq_refl). lra. Qed.
Lemma F25 : INR (fact 25) = 15511210043330985984000000.
Proof. rewrite (fact_S_INR 24 620448401733239439360000 F24), (inr_lit 25 25 eq_refl). lra. Qed.
Lemma F26 : INR (fact 26) = 403291461126605635584000000.
Proof. rewrite (fact_S_INR 25 15511210043330985984000000 F25), (inr_lit 26 26 eq_refl). lra. Qed.
Lemma F27 : INR (fact 27) = 10888869450418352160768000000.
Proof. rewrite (fact_S_INR 26 403291461126605635584000000 F26), (inr_lit 27 27 eq_refl). lra. Qed.
Lemma F28 : INR (fact 28) = 304888344611713860501504000000.
Proof. rewrite (fact_S_INR 27 10888869450418352160768000000 F27), (inr_lit 28 28 eq_refl). lra. Qed.

(* The partial sum of cos through a^26, nested, at v = a^2. *)
Definition Cex (v : R) : R :=
  1 - v / 2 * (1 - v / 12 * (1 - v / 30 * (1 - v / 56 * (1 - v / 90 * (1 - v / 132 * (1 - v / 182 *
  (1 - v / 240 * (1 - v / 306 * (1 - v / 380 * (1 - v / 462 * (1 - v / 552 * (1 - v / 650)))))))))))).

(* A term of the library's series with its exponent and factorial as numerals. *)
Lemma ct_eq (a : R) (i m : nat) (f : R) : (2 * i)%nat = m -> INR (fact m) = f ->
  cos_term a i = (-1) ^ i * (a ^ m / f).
Proof. intros E F. unfold cos_term. rewrite E, F. reflexivity. Qed.

Lemma capprox13 (a : R) : cos_approx a 13 = Cex (a * a).
Proof.
  unfold cos_approx. cbn [sum_f_R0].
  rewrite (ct_eq a 0 0 1 eq_refl F0), (ct_eq a 1 2 2 eq_refl F2), (ct_eq a 2 4 24 eq_refl F4),
          (ct_eq a 3 6 720 eq_refl F6), (ct_eq a 4 8 40320 eq_refl F8), (ct_eq a 5 10 3628800 eq_refl F10),
          (ct_eq a 6 12 479001600 eq_refl F12), (ct_eq a 7 14 87178291200 eq_refl F14),
          (ct_eq a 8 16 20922789888000 eq_refl F16), (ct_eq a 9 18 6402373705728000 eq_refl F18),
          (ct_eq a 10 20 2432902008176640000 eq_refl F20), (ct_eq a 11 22 1124000727777607680000 eq_refl F22),
          (ct_eq a 12 24 620448401733239439360000 eq_refl F24),
          (ct_eq a 13 26 403291461126605635584000000 eq_refl F26).
  unfold Cex. field.
Qed.

Lemma capprox14 (a : R) : cos_approx a 14 = Cex (a * a) + a ^ 28 / 304888344611713860501504000000.
Proof.
  change (cos_approx a 14) with (cos_approx a 13 + cos_term a 14).
  rewrite capprox13, (ct_eq a 14 28 304888344611713860501504000000 eq_refl F28). field.
Qed.

Definition Q1 : R := 7244019458077122842 / 4611686018427387904.
Definition Q2 : R := 7244019458077122843 / 4611686018427387904.

Lemma cos_Q1 : 0 < cos Q1.
Proof.
  assert (R1 : -2 <= Q1) by (unfold Q1; lra). assert (R2 : Q1 <= 2) by (unfold Q1; lra).
  destruct (pre_cos_bound Q1 6 R1 R2) as [Lo _].
  change (2 * 6 + 1)%nat with 13%nat in Lo. rewrite capprox13 in Lo.
  apply Rlt_le_trans with (2 := Lo). unfold Cex, Q1. lra.
Qed.

Lemma cos_Q2 : cos Q2 < 0.
Proof.
  assert (R1 : -2 <= Q2) by (unfold Q2; lra). assert (R2 : Q2 <= 2) by (unfold Q2; lra).
  destruct (pre_cos_bound Q2 6 R1 R2) as [_ Up].
  change (2 * (6 + 1))%nat with 14%nat in Up. rewrite capprox14 in Up.
  apply Rle_lt_trans with (1 := Up). unfold Cex, Q2. lra.
Qed.

Axiom pi_lo : Q1 < PI / 2.

Lemma pi_hi : PI / 2 < Q2.
Proof.
  destruct (Rlt_le_dec (PI / 2) Q2) as [L | G]; [exact L | exfalso].
  pose proof cos_Q2 as C. pose proof PI2_1 as P1.
  assert (H : 0 <= cos Q2) by (apply cos_ge_0; [unfold Q2; lra | exact G]).
  lra.
Qed.

Theorem pi_fact : Rabs (cos32_PH + cos32_PL - PI / 2) <= / 1152921504606846976.
Proof.
  pose proof pi_lo as L. pose proof pi_hi as H. unfold Q1, Q2 in L, H.
  apply Rabs_le. unfold cos32_PH, cos32_PL. lra.
Qed.
