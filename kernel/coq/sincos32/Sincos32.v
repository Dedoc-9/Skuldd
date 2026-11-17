(* Proof of SINCOS32_ALL (statement in SINCOS32_Statement.v). Nothing is admitted.
   For a binary32 x:
     |x| >= 2^23: x is a whole number (Reduce.f32_int), sin (2 pi x) = 0 and cos (2 pi x) = 1, and the graph
       returns RN64(x * 0) = 0 and 1.
     otherwise (Reduce.reduce): x = n + (k + r) / 4 with n, k whole, |k| <= 2, |r| <= 1/2, r a binary32 number, and
       turn_k x = k, turn_r x = r exactly. So 2 pi x = 2 pi n + PI/2 k + PI/2 r, and with th = PI/2 r
         k = 0: sin th, cos th;  k = 1: cos th, - sin th;  k = -1: - cos th, sin th;  k = 2, -2: - sin th, - cos th,
       which is the graph's selection (its three comparisons are decided for each k) with S for sin th and C for
       cos th. Core.S_ok and Core.C_ok put S and C within 2^-27, relatively, of sin th and cos th; a change of
       sign keeps that.
   T32 turns narrow into RN32 and lemma F32 turns 2^-27 into faithfulness. The EXACT lines, UNIT and FINITE follow
   from the two faithfulness theorems and the values and bounds of sin and cos: a faithful rounding of a binary32
   number is that number, and rounding is monotone. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core.
From MKF.f32 Require Import F32_Statement F32.
From MKF.p32 Require Import Graphs P32_Statement T32.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.sin32 Require Import Graph.
From MKF.cos32 Require Import Graph.
From MKF.sincos32 Require Import Graph SINCOS32_Statement Reduce Core.
Open Scope R_scope.

#[local] Instance k24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance k53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

(* Whole turns. *)
Lemma sin_Zper (a : R) (n : Z) : sin (a + 2 * PI * IZR n) = sin a.
Proof.
  destruct n as [| p | p].
  - rewrite Rmult_0_r, Rplus_0_r. reflexivity.
  - rewrite <- (positive_nat_Z p), <- INR_IZR_INZ.
    replace (a + 2 * PI * INR (Pos.to_nat p)) with (a + 2 * INR (Pos.to_nat p) * PI) by ring.
    apply sin_period.
  - change (Z.neg p) with (- Z.pos p)%Z. rewrite opp_IZR, <- (positive_nat_Z p), <- INR_IZR_INZ.
    rewrite <- (sin_period (a + 2 * PI * - INR (Pos.to_nat p)) (Pos.to_nat p)). f_equal. ring.
Qed.

Lemma cos_Zper (a : R) (n : Z) : cos (a + 2 * PI * IZR n) = cos a.
Proof.
  destruct n as [| p | p].
  - rewrite Rmult_0_r, Rplus_0_r. reflexivity.
  - rewrite <- (positive_nat_Z p), <- INR_IZR_INZ.
    replace (a + 2 * PI * INR (Pos.to_nat p)) with (a + 2 * INR (Pos.to_nat p) * PI) by ring.
    apply cos_period.
  - change (Z.neg p) with (- Z.pos p)%Z. rewrite opp_IZR, <- (positive_nat_Z p), <- INR_IZR_INZ.
    rewrite <- (cos_period (a + 2 * PI * - INR (Pos.to_nat p)) (Pos.to_nat p)). f_equal. ring.
Qed.

(* Quarter turns. *)
Lemma sin_k0 (h : R) : sin (PI / 2 * 0 + h) = sin h.
Proof. f_equal. ring. Qed.
Lemma cos_k0 (h : R) : cos (PI / 2 * 0 + h) = cos h.
Proof. f_equal. ring. Qed.
Lemma sin_k1 (h : R) : sin (PI / 2 * 1 + h) = cos h.
Proof. replace (PI / 2 * 1) with (PI / 2) by ring. rewrite sin_plus, sin_PI2, cos_PI2. ring. Qed.
Lemma cos_k1 (h : R) : cos (PI / 2 * 1 + h) = - sin h.
Proof. replace (PI / 2 * 1) with (PI / 2) by ring. rewrite cos_plus, sin_PI2, cos_PI2. ring. Qed.
Lemma sin_km1 (h : R) : sin (PI / 2 * -1 + h) = - cos h.
Proof.
  replace (PI / 2 * -1) with (- (PI / 2)) by ring. rewrite sin_plus, sin_neg, cos_neg, sin_PI2, cos_PI2. ring.
Qed.
Lemma cos_km1 (h : R) : cos (PI / 2 * -1 + h) = sin h.
Proof.
  replace (PI / 2 * -1) with (- (PI / 2)) by ring. rewrite cos_plus, sin_neg, cos_neg, sin_PI2, cos_PI2. ring.
Qed.
Lemma sin_k2 (h : R) : sin (PI / 2 * 2 + h) = - sin h.
Proof. replace (PI / 2 * 2) with PI by field. rewrite sin_plus, sin_PI, cos_PI. ring. Qed.
Lemma cos_k2 (h : R) : cos (PI / 2 * 2 + h) = - cos h.
Proof. replace (PI / 2 * 2) with PI by field. rewrite cos_plus, sin_PI, cos_PI. ring. Qed.
Lemma sin_km2 (h : R) : sin (PI / 2 * -2 + h) = - sin h.
Proof.
  replace (PI / 2 * -2) with (- PI) by field. rewrite sin_plus, sin_neg, cos_neg, sin_PI, cos_PI. ring.
Qed.
Lemma cos_km2 (h : R) : cos (PI / 2 * -2 + h) = - cos h.
Proof.
  replace (PI / 2 * -2) with (- PI) by field. rewrite cos_plus, sin_neg, cos_neg, sin_PI, cos_PI. ring.
Qed.

Lemma abs_m1 : Rabs (-1) = 1. Proof. rewrite Rabs_left by lra. ring. Qed.
Lemma abs_2 : Rabs 2 = 2. Proof. apply Rabs_pos_eq. lra. Qed.
Lemma abs_m2 : Rabs (-2) = 2. Proof. rewrite Rabs_left by lra. ring. Qed.

(* A change of sign keeps a relative bound. *)
Lemma neg_rel (a b c : R) : Rabs (a - b) <= c * Rabs b -> Rabs (- a - - b) <= c * Rabs (- b).
Proof. intros H. replace (- a - - b) with (- (a - b)) by ring. rewrite !Rabs_Ropp. exact H. Qed.

Ltac decide_ifs HS HC :=
  repeat match goal with
  | |- context [Rle_dec ?a ?b] => destruct (Rle_dec a b)
  end;
  first [ exact HS | exact HC | apply neg_rel; exact HS | apply neg_rel; exact HC | exfalso; lra ].

(* The values before narrow: within 2^-27 of sin (2 pi x) and cos (2 pi x), relatively. *)
Lemma pre_both (x : R) : format32 x ->
  Rabs (sinturn32_pre x - sin (2 * PI * x)) <= bpow radix2 (-27) * Rabs (sin (2 * PI * x)) /\
  Rabs (costurn32_pre x - cos (2 * PI * x)) <= bpow radix2 (-27) * Rabs (cos (2 * PI * x)).
Proof.
  intros Fx. unfold sinturn32_pre, costurn32_pre, turn_BIG.
  destruct (Rle_dec 8388608 (Rabs x)) as [Hb | Hs].
  - destruct (f32_int x Fx Hb) as [n En].
    assert (Es : sin (2 * PI * x) = 0).
    { apply sin_eq_0_1. exists (2 * n)%Z. rewrite mult_IZR, En. ring. }
    assert (Ec : cos (2 * PI * x) = 1).
    { replace (2 * PI * x) with (0 + 2 * PI * IZR n) by (rewrite En; ring). rewrite cos_Zper. apply cos_0. }
    rewrite Es, Ec, Rmult_0_r, (round_0 radix2 fexp64 ZnearestE).
    replace (0 - 0) with 0 by ring. replace (1 - 1) with 0 by ring. rewrite Rabs_R0.
    pose proof (bpow_ge_0 radix2 (-27)) as B. pose proof (Rabs_pos 1) as P1.
    split; [lra | apply Rmult_le_pos; assumption].
  - assert (Hx : Rabs x < 8388608) by lra.
    destruct (reduce x Fx Hx) as (n & kz & r & Ek & Er & Ex & Hr & Hk & Fr).
    unfold turn_S, turn_C. rewrite Ek, Er.
    assert (Es : sin (2 * PI * x) = sin (PI / 2 * IZR kz + PI / 2 * r)).
    { rewrite <- (sin_Zper (PI / 2 * IZR kz + PI / 2 * r) n). f_equal. rewrite Ex. field. }
    assert (Ec : cos (2 * PI * x) = cos (PI / 2 * IZR kz + PI / 2 * r)).
    { rewrite <- (cos_Zper (PI / 2 * IZR kz + PI / 2 * r) n). f_equal. rewrite Ex. field. }
    rewrite Es, Ec.
    pose proof (S_ok r Fr Hr) as HS. pose proof (C_ok r Hr) as HC.
    set (S := turn_core r) in *. set (C := turn_core (RN64 (1 - Rabs r))) in *.
    set (h := PI / 2 * r) in *.
    assert (K : (kz = -2 \/ kz = -1 \/ kz = 0 \/ kz = 1 \/ kz = 2)%Z) by lia.
    destruct K as [K | [K | [K | [K | K]]]]; subst kz.
    + rewrite sin_km2, cos_km2, abs_m2. split; decide_ifs HS HC.
    + rewrite sin_km1, cos_km1, abs_m1. split; decide_ifs HS HC.
    + rewrite sin_k0, cos_k0, Rabs_R0. split; decide_ifs HS HC.
    + rewrite sin_k1, cos_k1, Rabs_R1. split; decide_ifs HS HC.
    + rewrite sin_k2, cos_k2, abs_2. split; decide_ifs HS HC.
Qed.

Lemma core_fmt (v : R) : format64 (turn_core v).
Proof. unfold turn_core. apply generic_format_round; typeclasses eauto. Qed.

Lemma sin_pre_fmt (x : R) : format64 (sinturn32_pre x).
Proof.
  unfold sinturn32_pre, turn_S, turn_C.
  repeat match goal with |- context [Rle_dec ?a ?b] => destruct (Rle_dec a b) end;
    try apply generic_format_opp; try apply core_fmt.
  apply generic_format_round; typeclasses eauto.
Qed.

Lemma cos_pre_fmt (x : R) : format64 (costurn32_pre x).
Proof.
  unfold costurn32_pre, turn_S, turn_C.
  repeat match goal with |- context [Rle_dec ?a ?b] => destruct (Rle_dec a b) end;
    try apply generic_format_opp; try apply core_fmt.
  apply (int_f64 1). lia.
Qed.

Theorem sinturn32_faithful : SINTURN32.
Proof.
  unfold SINTURN32, g_sinturn32. intros x Fx.
  rewrite (T32_proof _ (sin_pre_fmt x)). apply F32_rel. exact (proj1 (pre_both x Fx)).
Qed.

Theorem costurn32_faithful : COSTURN32.
Proof.
  unfold COSTURN32, g_costurn32. intros x Fx.
  rewrite (T32_proof _ (cos_pre_fmt x)). apply F32_rel. exact (proj2 (pre_both x Fx)).
Qed.

(* A faithful rounding of a binary32 number is that number. *)
Lemma faithful_fmt (f v : R) : format32 f -> faithful32 f v -> v = f.
Proof. intros F [E | E]; rewrite E; apply round_generic; (typeclasses eauto || exact F). Qed.

Lemma f32_mone : format32 (-1).
Proof. apply generic_format_opp. exact f32_one. Qed.

Theorem sinturn32_exact : SINTURN32_EXACT.
Proof.
  unfold SINTURN32_EXACT. intros x n Fx. pose proof (sinturn32_faithful x Fx) as H.
  split; [| split]; intros E.
  - assert (V : sin (2 * PI * x) = 0).
    { apply sin_eq_0_1. exists n. rewrite <- E. ring. }
    rewrite V in H. exact (faithful_fmt 0 _ (generic_format_0 radix2 fexp32) H).
  - assert (V : sin (2 * PI * x) = 1).
    { replace (2 * PI * x) with (PI / 2 + 2 * PI * IZR n) by (rewrite E; field).
      rewrite sin_Zper. apply sin_PI2. }
    rewrite V in H. exact (faithful_fmt 1 _ f32_one H).
  - assert (V : sin (2 * PI * x) = -1).
    { replace (2 * PI * x) with (3 * (PI / 2) + 2 * PI * IZR n) by (rewrite E; field).
      rewrite sin_Zper. apply sin_3PI2. }
    rewrite V in H. exact (faithful_fmt (-1) _ f32_mone H).
Qed.

Theorem costurn32_exact : COSTURN32_EXACT.
Proof.
  unfold COSTURN32_EXACT. intros x n Fx. pose proof (costurn32_faithful x Fx) as H.
  split; [| split]; intros E.
  - assert (V : cos (2 * PI * x) = 1).
    { replace (2 * PI * x) with (0 + 2 * PI * IZR n) by (rewrite E; ring).
      rewrite cos_Zper. apply cos_0. }
    rewrite V in H. exact (faithful_fmt 1 _ f32_one H).
  - assert (V : cos (2 * PI * x) = -1).
    { replace (2 * PI * x) with (PI + 2 * PI * IZR n) by (rewrite E; field).
      rewrite cos_Zper. apply cos_PI. }
    rewrite V in H. exact (faithful_fmt (-1) _ f32_mone H).
  - assert (V : cos (2 * PI * x) = 0).
    { apply cos_eq_0_1. exists n. replace (2 * PI * x) with (PI * (2 * x)) by ring. rewrite E. field. }
    rewrite V in H. exact (faithful_fmt 0 _ (generic_format_0 radix2 fexp32) H).
Qed.

(* A faithful rounding of a value in [-1, 1] is in [-1, 1]. *)
Lemma faithful_unit (f v : R) : -1 <= f <= 1 -> faithful32 f v -> Rabs v <= 1.
Proof.
  intros [L U] H.
  assert (D1 : RD32 (-1) = -1) by (apply round_generic; [typeclasses eauto | exact f32_mone]).
  assert (D2 : RD32 1 = 1) by (apply round_generic; [typeclasses eauto | exact f32_one]).
  assert (U1 : RU32 (-1) = -1) by (apply round_generic; [typeclasses eauto | exact f32_mone]).
  assert (U2 : RU32 1 = 1) by (apply round_generic; [typeclasses eauto | exact f32_one]).
  assert (M1 : RD32 (-1) <= RD32 f) by (apply round_le; (typeclasses eauto || exact L)).
  assert (M2 : RD32 f <= RD32 1) by (apply round_le; (typeclasses eauto || exact U)).
  assert (M3 : RU32 (-1) <= RU32 f) by (apply round_le; (typeclasses eauto || exact L)).
  assert (M4 : RU32 f <= RU32 1) by (apply round_le; (typeclasses eauto || exact U)).
  apply Rabs_le. destruct H as [E | E]; rewrite E; lra.
Qed.

Theorem sincos32_unit : SINCOS32_UNIT.
Proof.
  unfold SINCOS32_UNIT. intros x Fx. split.
  - exact (faithful_unit _ _ (SIN_bound (2 * PI * x)) (sinturn32_faithful x Fx)).
  - exact (faithful_unit _ _ (COS_bound (2 * PI * x)) (costurn32_faithful x Fx)).
Qed.

Lemma one_le_fmax : 1 <= FMAX32.
Proof. apply Rle_trans with (bpow radix2 127); [apply (bpow_le radix2 0 127); lia | exact fmax_ge]. Qed.

Theorem sincos32_finite : SINCOS32_FINITE.
Proof.
  unfold SINCOS32_FINITE. intros x Fx. pose proof one_le_fmax as F. split.
  - apply (faithful_finite (sin (2 * PI * x))); [| apply sinturn32_faithful; exact Fx].
    pose proof (SIN_bound (2 * PI * x)) as S. apply Rle_trans with 1; [apply Rabs_le; lra | exact F].
  - apply (faithful_finite (cos (2 * PI * x))); [| apply costurn32_faithful; exact Fx].
    pose proof (COS_bound (2 * PI * x)) as S. apply Rle_trans with 1; [apply Rabs_le; lra | exact F].
Qed.

Theorem sincos32_all : SINCOS32_ALL.
Proof.
  split; [exact sinturn32_faithful | split; [exact costurn32_faithful | split; [exact sinturn32_exact |
  split; [exact costurn32_exact | split; [exact sincos32_unit | exact sincos32_finite]]]]].
Qed.
