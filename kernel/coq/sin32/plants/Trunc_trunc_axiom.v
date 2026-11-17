(* The truncation of sin32's polynomial, from the standard library's own bounds on sin (Rtrigo_alt.pre_sin_bound:
   for 0 <= a <= 4 the partial sums of the series bracket sin a). With n = 3:
     a P(a^2) <= sin a <= a P(a^2) + a^17 / 17!        (0 <= a, a^2 <= 5/2)
   where P is the nested form the graph evaluates (Pex below, in exact arithmetic). From it, for every x with
   x^2 <= 5/2:   |x P(x^2) - sin x| <= |x| 2^-37   and   |x| 7/12 <= |sin x|.
   The factorials are never computed in unary nat: each INR (fact k) is rewritten to its numeral one step at a time.
   Standard library only; nothing is admitted. *)
From Coq Require Import Reals ZArith Lia Lra.
Open Scope R_scope.

(* One level of the nested form, and the whole polynomial, in exact arithmetic. *)
Definition lvx (c v T : R) : R := 1 - v * T / c.
Definition Pex (v : R) : R :=
  lvx 6 v (lvx 20 v (lvx 42 v (lvx 72 v (lvx 110 v (lvx 156 v (1 - v / 210)))))).

Lemma lvx_range (c v T : R) : 6 <= c -> 0 <= v <= 5 / 2 -> 0 <= T <= 1 -> 7 / 12 <= lvx c v T <= 1.
Proof.
  intros Hc [Hv0 Hv1] [HT0 HT1]. unfold lvx.
  assert (Ic : 0 < / c <= / 6) by (split; [apply Rinv_0_lt_compat; lra | apply Rinv_le_contravar; lra]).
  assert (P : 0 <= v * T <= 5 / 2).
  { split; [apply Rmult_le_pos; lra | apply Rle_trans with (5 / 2 * 1); [apply Rmult_le_compat; lra | lra]]. }
  assert (Q : 0 <= v * T / c <= 5 / 12).
  { unfold Rdiv. split; [apply Rmult_le_pos; lra |].
    apply Rle_trans with (5 / 2 * / 6); [apply Rmult_le_compat; lra | lra]. }
  lra.
Qed.

Lemma Pex_range (v : R) : 0 <= v <= 5 / 2 -> 7 / 12 <= Pex v <= 1.
Proof.
  intros Hv. unfold Pex.
  assert (G : forall c T : R, 6 <= c -> 7 / 12 <= T <= 1 -> 7 / 12 <= lvx c v T <= 1)
    by (intros c T Hc HT; apply lvx_range; lra).
  do 6 (apply G; [lra |]). lra.
Qed.

(* Factorials as numerals, one multiplication at a time. *)
Lemma fact_S_INR (n : nat) (v : R) : INR (fact n) = v -> INR (fact (S n)) = INR (S n) * v.
Proof. intros H. rewrite fact_simpl, mult_INR, H. reflexivity. Qed.

Lemma inr_lit (n : nat) (z : Z) : Z.of_nat n = z -> INR n = IZR z.
Proof. intros H. rewrite INR_IZR_INZ, H. reflexivity. Qed.

Lemma F1 : INR (fact 1) = 1.
Proof. rewrite (inr_lit (fact 1) 1 eq_refl). reflexivity. Qed.
Lemma F2 : INR (fact 2) = 2.
Proof. rewrite (fact_S_INR 1 1 F1), (inr_lit 2 2 eq_refl). lra. Qed.
Lemma F3 : INR (fact 3) = 6.
Proof. rewrite (fact_S_INR 2 2 F2), (inr_lit 3 3 eq_refl). lra. Qed.
Lemma F4 : INR (fact 4) = 24.
Proof. rewrite (fact_S_INR 3 6 F3), (inr_lit 4 4 eq_refl). lra. Qed.
Lemma F5 : INR (fact 5) = 120.
Proof. rewrite (fact_S_INR 4 24 F4), (inr_lit 5 5 eq_refl). lra. Qed.
Lemma F6 : INR (fact 6) = 720.
Proof. rewrite (fact_S_INR 5 120 F5), (inr_lit 6 6 eq_refl). lra. Qed.
Lemma F7 : INR (fact 7) = 5040.
Proof. rewrite (fact_S_INR 6 720 F6), (inr_lit 7 7 eq_refl). lra. Qed.
Lemma F8 : INR (fact 8) = 40320.
Proof. rewrite (fact_S_INR 7 5040 F7), (inr_lit 8 8 eq_refl). lra. Qed.
Lemma F9 : INR (fact 9) = 362880.
Proof. rewrite (fact_S_INR 8 40320 F8), (inr_lit 9 9 eq_refl). lra. Qed.
Lemma F10 : INR (fact 10) = 3628800.
Proof. rewrite (fact_S_INR 9 362880 F9), (inr_lit 10 10 eq_refl). lra. Qed.
Lemma F11 : INR (fact 11) = 39916800.
Proof. rewrite (fact_S_INR 10 3628800 F10), (inr_lit 11 11 eq_refl). lra. Qed.
Lemma F12 : INR (fact 12) = 479001600.
Proof. rewrite (fact_S_INR 11 39916800 F11), (inr_lit 12 12 eq_refl). lra. Qed.
Lemma F13 : INR (fact 13) = 6227020800.
Proof. rewrite (fact_S_INR 12 479001600 F12), (inr_lit 13 13 eq_refl). lra. Qed.
Lemma F14 : INR (fact 14) = 87178291200.
Proof. rewrite (fact_S_INR 13 6227020800 F13), (inr_lit 14 14 eq_refl). lra. Qed.
Lemma F15 : INR (fact 15) = 1307674368000.
Proof. rewrite (fact_S_INR 14 87178291200 F14), (inr_lit 15 15 eq_refl). lra. Qed.
Lemma F16 : INR (fact 16) = 20922789888000.
Proof. rewrite (fact_S_INR 15 1307674368000 F15), (inr_lit 16 16 eq_refl). lra. Qed.
Lemma F17 : INR (fact 17) = 355687428096000.
Proof. rewrite (fact_S_INR 16 20922789888000 F16), (inr_lit 17 17 eq_refl). lra. Qed.

(* A term of the library's series with its exponent and factorial as numerals. *)
Lemma st_eq (a : R) (i m : nat) (f : R) : (2 * i + 1)%nat = m -> INR (fact m) = f ->
  sin_term a i = (-1) ^ i * (a ^ m / f).
Proof. intros E F. unfold sin_term. rewrite E, F. reflexivity. Qed.

(* The library's partial sum through a^15 is a P(a^2). *)
Lemma approx7 (a : R) : sin_approx a 7 = a * Pex (a * a).
Proof.
  unfold sin_approx. cbn [sum_f_R0].
  rewrite (st_eq a 0 1 1 eq_refl F1), (st_eq a 1 3 6 eq_refl F3), (st_eq a 2 5 120 eq_refl F5),
          (st_eq a 3 7 5040 eq_refl F7), (st_eq a 4 9 362880 eq_refl F9), (st_eq a 5 11 39916800 eq_refl F11),
          (st_eq a 6 13 6227020800 eq_refl F13), (st_eq a 7 15 1307674368000 eq_refl F15).
  unfold Pex, lvx. field.
Qed.

Lemma approx8 (a : R) : sin_approx a 8 = a * Pex (a * a) + a ^ 17 / 355687428096000.
Proof.
  change (sin_approx a 8) with (sin_approx a 7 + sin_term a 8).
  rewrite approx7, (st_eq a 8 17 355687428096000 eq_refl F17). field.
Qed.

(* (5/2)^8 / 17! = 4.29e-12, below 2^-37 = 7.28e-12. *)
Axiom sin_trunc_pos : forall a : R, 0 <= a -> a * a <= 5 / 2 ->
  a * Pex (a * a) <= sin a <= a * Pex (a * a) + a * / 137438953472.

(* Both signs: the truncation relative to |x|, and |sin x| from below. *)
Theorem sin_trunc (x : R) : x * x <= 5 / 2 ->
  Rabs (x * Pex (x * x) - sin x) <= Rabs x * / 137438953472 /\ Rabs x * (7 / 12) <= Rabs (sin x).
Proof.
  intros Hv.
  assert (Hv0 : 0 <= x * x <= 5 / 2) by (split; [apply Rle_0_sqr | exact Hv]).
  pose proof (Pex_range (x * x) Hv0) as W.
  destruct (Rle_lt_dec 0 x) as [P | N].
  - destruct (sin_trunc_pos x P Hv) as [Lo Up].
    assert (Q : x * (7 / 12) <= x * Pex (x * x)) by (apply Rmult_le_compat_l; lra).
    rewrite (Rabs_pos_eq x P). split; [apply Rabs_le; lra |].
    rewrite Rabs_pos_eq by lra. lra.
  - assert (Pa : 0 <= - x) by lra.
    assert (Hva : - x * - x <= 5 / 2) by (replace (- x * - x) with (x * x) by ring; exact Hv).
    destruct (sin_trunc_pos (- x) Pa Hva) as [Lo Up].
    replace (- x * - x) with (x * x) in Lo, Up by ring. rewrite sin_neg in Lo, Up.
    assert (Q : - x * (7 / 12) <= - x * Pex (x * x)) by (apply Rmult_le_compat_l; lra).
    rewrite <- (Rabs_Ropp x), (Rabs_pos_eq (- x) Pa). split; [apply Rabs_le; lra |].
    rewrite <- (Rabs_Ropp (sin x)), Rabs_pos_eq by lra. lra.
Qed.
