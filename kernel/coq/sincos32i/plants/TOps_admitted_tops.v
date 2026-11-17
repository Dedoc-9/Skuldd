(* TOps.v: one lemma per operation of tieee_ops (statement in SINCOS32_IEEE_Statement.v, which this file does not
   change), for the proof of SINCOS32_IEEE, in the manner of ieee64/Ops.v (whose lemmas are about the other
   record, OPS / ieee_ops). Flocq and the standard library only; every lemma ends with Qed and nothing is assumed.
   Author: the assistant (2026-11-16). A scratch candidate.

   Each top_* lemma is one use of Flocq's own lemma for that operation (Bplus_correct, Bminus_correct,
   Bmult_correct, Bdiv_correct, B2R_Babs, is_finite_Babs, B2R_Bopp, is_finite_Bopp, Bleb_correct, Bltb_correct) at
   53 1024 prec64_gt_0 prec64_lt_emax mode_NE, with Flocq's rounding read as the graphs' RN64. In words:
     top_add, top_sub, top_mul   finite operands, and the model's rounded result below 2^1024 in magnitude: the
                                 IEEE result is finite and its real number is RN64 of the real operation.
     top_div                     the same with a finite dividend and a divisor whose real number is not 0.
     top_abs_*, top_neg_*        the absolute value and the negation are exact and as finite as their operand.
     top_sel_le, top_sel_lt      on finite COMPARED operands the IEEE selection chooses as the model's does.
                                 Nothing is asked of the two values selected from.
     tcst_ok                     IEEE_TCST's own body: every constant is finite and denotes the graph's constant.
   The forms top_*_at take the operands' real numbers as equations (B2R x = u).

   den x u e: the binary64 value x is finite, its real number is u, and |u| <= 2^e. The den_* lemmas carry the
   three facts through one operation each; the overflow premise of the operation is met by the bound (e < 1024).
   The bounds are crude powers of two, on purpose: nothing about the values is used but their magnitudes.
     N_den     the shape T_N (two operations) against turn_N.
     poly_den  the shape T_poly (20 operations) against sin32_poly, for |u| <= 2^126: the result is at most 2^889.
     core_den  the shape T_core against turn_core, for |v| <= 2^62: the result is at most 2^952. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs.
From MKF.sin32 Require Import Graph.
From MKF.cos32 Require Import Graph.
From MKF.sincos32 Require Import Graph.
From MKF.ieee64 Require Import IEEE64_Statement Ops.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
Open Scope R_scope.

#[local] Instance t53 : Prec_gt_0 53 := prec64_gt_0.

(* The four rounded operations *)

Lemma top_add (x y : b64) : is_finite x = true -> is_finite y = true ->
  Rabs (RN64 (B2R x + B2R y)) < bpow radix2 1024 ->
  is_finite (t_add tieee_ops x y) = true /\ B2R (t_add tieee_ops x y) = RN64 (B2R x + B2R y).
Proof.
  intros Fx Fy H.
  generalize (Bplus_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE x y Fx Fy).
  change (round radix2 (SpecFloat.fexp 53 1024) (round_mode mode_NE) (B2R x + B2R y))
    with (RN64 (B2R x + B2R y)).
  rewrite Rlt_bool_true by exact H.
  intros (H1 & H2 & _). split; [exact H2 | exact H1].
Qed.

Lemma top_sub (x y : b64) : is_finite x = true -> is_finite y = true ->
  Rabs (RN64 (B2R x - B2R y)) < bpow radix2 1024 ->
  is_finite (t_sub tieee_ops x y) = true /\ B2R (t_sub tieee_ops x y) = RN64 (B2R x - B2R y).
Proof.
  intros Fx Fy H.
  generalize (Bminus_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE x y Fx Fy).
  change (round radix2 (SpecFloat.fexp 53 1024) (round_mode mode_NE) (B2R x - B2R y))
    with (RN64 (B2R x - B2R y)).
  rewrite Rlt_bool_true by exact H.
  intros (H1 & H2 & _). split; [exact H2 | exact H1].
Qed.

Lemma top_mul (x y : b64) : is_finite x = true -> is_finite y = true ->
  Rabs (RN64 (B2R x * B2R y)) < bpow radix2 1024 ->
  is_finite (t_mul tieee_ops x y) = true /\ B2R (t_mul tieee_ops x y) = RN64 (B2R x * B2R y).
Proof.
  intros Fx Fy H.
  generalize (Bmult_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE x y).
  change (round radix2 (SpecFloat.fexp 53 1024) (round_mode mode_NE) (B2R x * B2R y))
    with (RN64 (B2R x * B2R y)).
  rewrite Rlt_bool_true by exact H.
  rewrite Fx, Fy.
  intros (H1 & H2 & _). split; [exact H2 | exact H1].
Qed.

Lemma top_div (x y : b64) : is_finite x = true -> B2R y <> 0 ->
  Rabs (RN64 (B2R x / B2R y)) < bpow radix2 1024 ->
  is_finite (t_div tieee_ops x y) = true /\ B2R (t_div tieee_ops x y) = RN64 (B2R x / B2R y).
Proof.
  intros Fx Ny H.
  generalize (Bdiv_correct 53 1024 prec64_gt_0 prec64_lt_emax mode_NE x y Ny).
  change (round radix2 (SpecFloat.fexp 53 1024) (round_mode mode_NE) (B2R x / B2R y))
    with (RN64 (B2R x / B2R y)).
  rewrite Rlt_bool_true by exact H.
  rewrite Fx.
  intros (H1 & H2 & _). split; [exact H2 | exact H1].
Admitted.

(* The absolute value and the negation: exact, and finite exactly when the operand is. *)
Lemma top_abs_val (x : b64) : B2R (t_abs tieee_ops x) = Rabs (B2R x).
Proof. exact (B2R_Babs 53 1024 x). Qed.

Lemma top_abs_fin (x : b64) : is_finite (t_abs tieee_ops x) = is_finite x.
Proof. exact (is_finite_Babs 53 1024 x). Qed.

Lemma top_neg_val (x : b64) : B2R (t_neg tieee_ops x) = - B2R x.
Proof. exact (B2R_Bopp 53 1024 x). Qed.

Lemma top_neg_fin (x : b64) : is_finite (t_neg tieee_ops x) = is_finite x.
Proof. exact (is_finite_Bopp 53 1024 x). Qed.

(* The selections: on finite compared operands they choose as the model's do. *)
Lemma top_sel_le (a b c d : b64) : is_finite a = true -> is_finite b = true ->
  t_sel_le tieee_ops a b c d = if Rle_dec (B2R a) (B2R b) then c else d.
Proof.
  intros Fa Fb. cbv [t_sel_le tieee_ops].
  rewrite (Bleb_correct 53 1024 a b Fa Fb).
  destruct (Rle_dec (B2R a) (B2R b)) as [H | H].
  - rewrite Rle_bool_true by exact H. reflexivity.
  - rewrite Rle_bool_false by (apply Rnot_le_lt; exact H). reflexivity.
Qed.

Lemma top_sel_lt (a b c d : b64) : is_finite a = true -> is_finite b = true ->
  t_sel_lt tieee_ops a b c d = if Rlt_dec (B2R a) (B2R b) then c else d.
Proof.
  intros Fa Fb. cbv [t_sel_lt tieee_ops].
  rewrite (Bltb_correct 53 1024 a b Fa Fb).
  destruct (Rlt_dec (B2R a) (B2R b)) as [H | H].
  - rewrite Rlt_bool_true by exact H. reflexivity.
  - rewrite Rlt_bool_false by (apply Rnot_lt_le; exact H). reflexivity.
Qed.

(* The same lemmas with the operands' real numbers given as equations, for walking a shape. *)

Lemma top_add_at (x y : b64) (u v : R) : is_finite x = true -> is_finite y = true -> B2R x = u -> B2R y = v ->
  Rabs (RN64 (u + v)) < bpow radix2 1024 ->
  is_finite (t_add tieee_ops x y) = true /\ B2R (t_add tieee_ops x y) = RN64 (u + v).
Proof. intros Fx Fy Ex Ey. rewrite <- Ex, <- Ey. exact (top_add x y Fx Fy). Qed.

Lemma top_sub_at (x y : b64) (u v : R) : is_finite x = true -> is_finite y = true -> B2R x = u -> B2R y = v ->
  Rabs (RN64 (u - v)) < bpow radix2 1024 ->
  is_finite (t_sub tieee_ops x y) = true /\ B2R (t_sub tieee_ops x y) = RN64 (u - v).
Proof. intros Fx Fy Ex Ey. rewrite <- Ex, <- Ey. exact (top_sub x y Fx Fy). Qed.

Lemma top_mul_at (x y : b64) (u v : R) : is_finite x = true -> is_finite y = true -> B2R x = u -> B2R y = v ->
  Rabs (RN64 (u * v)) < bpow radix2 1024 ->
  is_finite (t_mul tieee_ops x y) = true /\ B2R (t_mul tieee_ops x y) = RN64 (u * v).
Proof. intros Fx Fy Ex Ey. rewrite <- Ex, <- Ey. exact (top_mul x y Fx Fy). Qed.

Lemma top_div_at (x y : b64) (u v : R) : is_finite x = true -> B2R x = u -> B2R y = v -> v <> 0 ->
  Rabs (RN64 (u / v)) < bpow radix2 1024 ->
  is_finite (t_div tieee_ops x y) = true /\ B2R (t_div tieee_ops x y) = RN64 (u / v).
Proof. intros Fx Ex Ey. rewrite <- Ex, <- Ey. exact (top_div x y Fx). Qed.

Lemma top_sel_le_at (a b c d : b64) (u v : R) : is_finite a = true -> is_finite b = true ->
  B2R a = u -> B2R b = v -> t_sel_le tieee_ops a b c d = if Rle_dec u v then c else d.
Proof. intros Fa Fb Ea Eb. rewrite <- Ea, <- Eb. exact (top_sel_le a b c d Fa Fb). Qed.

Lemma top_sel_lt_at (a b c d : b64) (u v : R) : is_finite a = true -> is_finite b = true ->
  B2R a = u -> B2R b = v -> t_sel_lt tieee_ops a b c d = if Rlt_dec u v then c else d.
Proof. intros Fa Fb Ea Eb. rewrite <- Ea, <- Eb. exact (top_sel_lt a b c d Fa Fb). Qed.

(* The constants (b2r_fin and b2r_whole are ieee64/Ops.v's: a finite binary64 value whose signed mantissa is
   n * 2^k denotes n * 2^(e + k)). *)
Lemma tcst_ok : forall c : tconst,
  is_finite (t_cst tieee_ops c) = true /\ B2R (t_cst tieee_ops c) = t_cst tmodel_ops c.
Proof.
  intros c. split; [destruct c; reflexivity |].
  destruct c; cbv [t_cst tieee_ops tmodel_ops tieee_cst tmodel_cst].
  - unfold KK. apply (b2r_whole false _ 23 _ 536870913); [lia | reflexivity].
  - unfold MM. rewrite (b2r_fin false _ (-149) _ 3 51); [reflexivity | lia | reflexivity].
  - unfold TT. rewrite (b2r_fin false _ (-178) _ 1 52); [apply Rmult_1_l | lia | reflexivity].
  - unfold HH. rewrite (b2r_fin false _ (-202) _ 1 52); [apply Rmult_1_l | lia | reflexivity].
  - reflexivity.
  - apply (b2r_whole false _ 52 _ 1); [lia | reflexivity].
  - apply (b2r_whole false _ 50 _ 4); [lia | reflexivity].
  - unfold turn_CN. apply (b2r_whole false _ 0 _ 6755399441055744); [lia | reflexivity].
  - unfold turn_BIG. apply (b2r_whole false _ 29 _ 8388608); [lia | reflexivity].
  - unfold cos32_PH. rewrite (b2r_fin false _ (-52) _ 7074237752028440 0); [| lia | reflexivity].
    change (bpow radix2 (-52 + 0)) with (/ 4503599627370496). reflexivity.
  - apply (b2r_whole false _ 50 _ 6); [lia | reflexivity].
  - apply (b2r_whole false _ 48 _ 20); [lia | reflexivity].
  - apply (b2r_whole false _ 47 _ 42); [lia | reflexivity].
  - apply (b2r_whole false _ 46 _ 72); [lia | reflexivity].
  - apply (b2r_whole false _ 46 _ 110); [lia | reflexivity].
  - apply (b2r_whole false _ 45 _ 156); [lia | reflexivity].
  - apply (b2r_whole false _ 45 _ 210); [lia | reflexivity].
Qed.

Theorem IEEE_TCST_proof : IEEE_TCST.
Proof. exact tcst_ok. Qed.

Lemma tcst_fin (c : tconst) : is_finite (t_cst tieee_ops c) = true.
Proof. exact (proj1 (tcst_ok c)). Qed.

Lemma tcst_val (c : tconst) : B2R (t_cst tieee_ops c) = tmodel_cst c.
Proof. exact (proj2 (tcst_ok c)). Qed.

Lemma tval_KK : B2R (t_cst tieee_ops K_KK) = KK. Proof. exact (tcst_val K_KK). Qed.
Lemma tval_MM : B2R (t_cst tieee_ops K_MM) = MM. Proof. exact (tcst_val K_MM). Qed.
Lemma tval_TT : B2R (t_cst tieee_ops K_TT) = TT. Proof. exact (tcst_val K_TT). Qed.
Lemma tval_HH : B2R (t_cst tieee_ops K_HH) = HH. Proof. exact (tcst_val K_HH). Qed.
Lemma tval_0 : B2R (t_cst tieee_ops K_0) = 0. Proof. exact (tcst_val K_0). Qed.
Lemma tval_1 : B2R (t_cst tieee_ops K_1) = 1. Proof. exact (tcst_val K_1). Qed.
Lemma tval_4 : B2R (t_cst tieee_ops K_4) = 4. Proof. exact (tcst_val K_4). Qed.
Lemma tval_CN : B2R (t_cst tieee_ops K_CN) = turn_CN. Proof. exact (tcst_val K_CN). Qed.
Lemma tval_BIG : B2R (t_cst tieee_ops K_BIG) = turn_BIG. Proof. exact (tcst_val K_BIG). Qed.
Lemma tval_PH : B2R (t_cst tieee_ops K_PH) = cos32_PH. Proof. exact (tcst_val K_PH). Qed.

(* Bounds by powers of two *)

Lemma bp_add (u v : R) (e1 e2 e3 : Z) : Rabs u <= bpow radix2 e1 -> Rabs v <= bpow radix2 e2 ->
  (e1 < e3)%Z -> (e2 < e3)%Z -> Rabs (u + v) <= bpow radix2 e3.
Proof.
  intros Hu Hv L1 L2.
  assert (E : bpow radix2 e3 = 2 * bpow radix2 (e3 - 1)).
  { replace e3 with (1 + (e3 - 1))%Z at 1 by ring. rewrite bpow_plus. reflexivity. }
  assert (A1 : bpow radix2 e1 <= bpow radix2 (e3 - 1)) by (apply bpow_le; lia).
  assert (A2 : bpow radix2 e2 <= bpow radix2 (e3 - 1)) by (apply bpow_le; lia).
  eapply Rle_trans; [apply Rabs_triang |]. lra.
Qed.

Lemma bp_sub (u v : R) (e1 e2 e3 : Z) : Rabs u <= bpow radix2 e1 -> Rabs v <= bpow radix2 e2 ->
  (e1 < e3)%Z -> (e2 < e3)%Z -> Rabs (u - v) <= bpow radix2 e3.
Proof.
  intros Hu Hv L1 L2. replace (u - v) with (u + - v) by ring.
  apply (bp_add u (- v) e1 e2 e3); [exact Hu | rewrite Rabs_Ropp; exact Hv | exact L1 | exact L2].
Qed.

Lemma bp_mul (u v : R) (e1 e2 e3 : Z) : Rabs u <= bpow radix2 e1 -> Rabs v <= bpow radix2 e2 ->
  (e1 + e2 <= e3)%Z -> Rabs (u * v) <= bpow radix2 e3.
Proof.
  intros Hu Hv L. rewrite Rabs_mult.
  apply Rle_trans with (bpow radix2 e1 * bpow radix2 e2).
  - apply Rmult_le_compat; [apply Rabs_pos | apply Rabs_pos | exact Hu | exact Hv].
  - rewrite <- bpow_plus. apply bpow_le. exact L.
Qed.

Lemma bp_div (u v : R) (e1 e3 : Z) : Rabs u <= bpow radix2 e1 -> 1 <= v -> (e1 <= e3)%Z ->
  Rabs (u / v) <= bpow radix2 e3.
Proof.
  intros Hu Hv L. unfold Rdiv. rewrite Rabs_mult.
  assert (P : 0 < / v) by (apply Rinv_0_lt_compat; lra).
  assert (Q : / v <= 1) by (rewrite <- Rinv_1; apply Rinv_le_contravar; lra).
  rewrite (Rabs_pos_eq (/ v)) by lra.
  apply Rle_trans with (bpow radix2 e1 * 1).
  - apply Rmult_le_compat; [apply Rabs_pos | lra | exact Hu | exact Q].
  - rewrite Rmult_1_r. apply bpow_le. exact L.
Qed.

(* den x u e: x is finite, denotes u, and |u| <= 2^e. *)
Definition den (x : b64) (u : R) (e : Z) : Prop :=
  is_finite x = true /\ B2R x = u /\ Rabs u <= bpow radix2 e.

Lemma den_mono (x : b64) (u : R) (e e' : Z) : den x u e -> (e <= e')%Z -> den x u e'.
Proof.
  intros (F & V & B) L. split; [exact F | split; [exact V |]].
  apply Rle_trans with (1 := B). apply bpow_le. exact L.
Qed.

Lemma den_add (x y : b64) (u v : R) (e1 e2 e3 : Z) : den x u e1 -> den y v e2 ->
  (e1 < e3)%Z -> (e2 < e3)%Z -> (-1074 <= e3 < 1024)%Z ->
  den (t_add tieee_ops x y) (RN64 (u + v)) e3.
Proof.
  intros (Fx & Ex & Bx) (Fy & Ey & By) L1 L2 L3.
  pose proof (bp_add u v e1 e2 e3 Bx By L1 L2) as B.
  destruct (top_add_at x y u v Fx Fy Ex Ey) as [F V].
  { apply (rn64_lt_emax _ e3); [exact L3 | exact B]. }
  split; [exact F | split; [exact V | apply rn64_abs_le; [lia | exact B]]].
Qed.

Lemma den_sub (x y : b64) (u v : R) (e1 e2 e3 : Z) : den x u e1 -> den y v e2 ->
  (e1 < e3)%Z -> (e2 < e3)%Z -> (-1074 <= e3 < 1024)%Z ->
  den (t_sub tieee_ops x y) (RN64 (u - v)) e3.
Proof.
  intros (Fx & Ex & Bx) (Fy & Ey & By) L1 L2 L3.
  pose proof (bp_sub u v e1 e2 e3 Bx By L1 L2) as B.
  destruct (top_sub_at x y u v Fx Fy Ex Ey) as [F V].
  { apply (rn64_lt_emax _ e3); [exact L3 | exact B]. }
  split; [exact F | split; [exact V | apply rn64_abs_le; [lia | exact B]]].
Qed.

Lemma den_mul (x y : b64) (u v : R) (e1 e2 e3 : Z) : den x u e1 -> den y v e2 ->
  (e1 + e2 <= e3)%Z -> (-1074 <= e3 < 1024)%Z ->
  den (t_mul tieee_ops x y) (RN64 (u * v)) e3.
Proof.
  intros (Fx & Ex & Bx) (Fy & Ey & By) L1 L3.
  pose proof (bp_mul u v e1 e2 e3 Bx By L1) as B.
  destruct (top_mul_at x y u v Fx Fy Ex Ey) as [F V].
  { apply (rn64_lt_emax _ e3); [exact L3 | exact B]. }
  split; [exact F | split; [exact V | apply rn64_abs_le; [lia | exact B]]].
Qed.

(* The division: by a value that is at least 1 (the graphs divide by whole constants only). *)
Lemma den_div (x y : b64) (u v : R) (e1 e3 : Z) : den x u e1 -> B2R y = v -> 1 <= v ->
  (e1 <= e3)%Z -> (-1074 <= e3 < 1024)%Z ->
  den (t_div tieee_ops x y) (RN64 (u / v)) e3.
Proof.
  intros (Fx & Ex & Bx) Ey Hv L1 L3.
  pose proof (bp_div u v e1 e3 Bx Hv L1) as B.
  assert (Nv : v <> 0) by lra.
  destruct (top_div_at x y u v Fx Ex Ey Nv) as [F V].
  { apply (rn64_lt_emax _ e3); [exact L3 | exact B]. }
  split; [exact F | split; [exact V | apply rn64_abs_le; [lia | exact B]]].
Qed.

Lemma den_abs (x : b64) (u : R) (e : Z) : den x u e -> den (t_abs tieee_ops x) (Rabs u) e.
Proof.
  intros (F & V & B). split; [rewrite top_abs_fin; exact F | split].
  - rewrite top_abs_val, V. reflexivity.
  - rewrite Rabs_Rabsolu. exact B.
Qed.

Lemma den_neg (x : b64) (u : R) (e : Z) : den x u e -> den (t_neg tieee_ops x) (- u) e.
Proof.
  intros (F & V & B). split; [rewrite top_neg_fin; exact F | split].
  - rewrite top_neg_val, V. reflexivity.
  - rewrite Rabs_Ropp. exact B.
Qed.

(* The constants the walks use, with their magnitudes. *)
Lemma den_c1 : den (t_cst tieee_ops K_1) 1 0.
Proof.
  split; [exact (tcst_fin K_1) | split; [exact tval_1 |]].
  rewrite Rabs_R1. change (bpow radix2 0) with 1. lra.
Qed.

Lemma den_c4 : den (t_cst tieee_ops K_4) 4 2.
Proof.
  split; [exact (tcst_fin K_4) | split; [exact tval_4 |]].
  rewrite Rabs_pos_eq by lra. change (bpow radix2 2) with 4. lra.
Qed.

Lemma den_PH : den (t_cst tieee_ops K_PH) cos32_PH 1.
Proof.
  split; [exact (tcst_fin K_PH) | split; [exact tval_PH |]].
  unfold cos32_PH. rewrite Rabs_pos_eq by lra. change (bpow radix2 1) with 2. lra.
Qed.

Lemma den_CN : den (t_cst tieee_ops K_CN) turn_CN 53.
Proof.
  split; [exact (tcst_fin K_CN) | split; [exact tval_CN |]].
  unfold turn_CN. rewrite Rabs_pos_eq by lra. change (bpow radix2 53) with 9007199254740992. lra.
Qed.

(* T_N: (v + CN) - CN, two operations. *)
Lemma N_den (V : b64) (v : R) (e e3 : Z) : den V v e -> (e + 2 <= e3)%Z -> (55 <= e3)%Z -> (e3 < 1024)%Z ->
  den (T_N b64 tieee_ops V) (turn_N v) e3.
Proof.
  intros HV L1 L2 L3. unfold T_N, turn_N.
  pose proof (den_add V (t_cst tieee_ops K_CN) v turn_CN e 53 (e3 - 1) HV den_CN
                ltac:(lia) ltac:(lia) ltac:(lia)) as Hp.
  exact (den_sub _ (t_cst tieee_ops K_CN) _ turn_CN (e3 - 1) 53 e3 Hp den_CN
           ltac:(lia) ltac:(lia) ltac:(lia)).
Qed.

(* One level of the polynomial: 1 - (u * t) / c, three operations and the constant 1. *)
Lemma den_lv (U T : b64) (u t : R) (c : tconst) (cv : R) (eu et e3 : Z) :
  den U u eu -> den T t et -> B2R (t_cst tieee_ops c) = cv -> 1 <= cv ->
  (0 <= eu + et)%Z -> (eu + et < e3)%Z -> (e3 < 1024)%Z ->
  den (t_sub tieee_ops (t_cst tieee_ops K_1) (t_div tieee_ops (t_mul tieee_ops U T) (t_cst tieee_ops c)))
      (RN64 (1 - RN64 (RN64 (u * t) / cv))) e3.
Proof.
  intros HU HT Ec Hc L0 L1 L2.
  pose proof (den_mul U T u t eu et (eu + et) HU HT ltac:(lia) ltac:(lia)) as Hm.
  pose proof (den_div _ (t_cst tieee_ops c) _ cv (eu + et) (eu + et) Hm Ec Hc ltac:(lia) ltac:(lia)) as Hd.
  exact (den_sub _ _ _ _ 0 (eu + et) e3 den_c1 Hd ltac:(lia) ltac:(lia) ltac:(lia)).
Qed.

(* The innermost level: 1 - u / c, without the product. *)
Lemma den_lv0 (U : b64) (u : R) (c : tconst) (cv : R) (eu e3 : Z) :
  den U u eu -> B2R (t_cst tieee_ops c) = cv -> 1 <= cv ->
  (0 <= eu)%Z -> (eu < e3)%Z -> (e3 < 1024)%Z ->
  den (t_sub tieee_ops (t_cst tieee_ops K_1) (t_div tieee_ops U (t_cst tieee_ops c)))
      (RN64 (1 - RN64 (u / cv))) e3.
Proof.
  intros HU Ec Hc L0 L1 L2.
  pose proof (den_div U (t_cst tieee_ops c) u cv eu eu HU Ec Hc ltac:(lia) ltac:(lia)) as Hd.
  exact (den_sub _ _ _ _ 0 eu e3 den_c1 Hd ltac:(lia) ltac:(lia) ltac:(lia)).
Qed.

(* The polynomial, one level at a time, outermost first. *)
Lemma poly_den (U : b64) (u : R) : den U u 126 -> den (T_poly b64 tieee_ops U) (sin32_poly u) 889.
Proof.
  intros HU. unfold T_poly, sin32_poly.
  apply (den_lv U _ u _ K_6 6 126 762 889 HU); [| exact (tcst_val K_6) | lra | lia | lia | lia].
  apply (den_lv U _ u _ K_20 20 126 635 762 HU); [| exact (tcst_val K_20) | lra | lia | lia | lia].
  apply (den_lv U _ u _ K_42 42 126 508 635 HU); [| exact (tcst_val K_42) | lra | lia | lia | lia].
  apply (den_lv U _ u _ K_72 72 126 381 508 HU); [| exact (tcst_val K_72) | lra | lia | lia | lia].
  apply (den_lv U _ u _ K_110 110 126 254 381 HU); [| exact (tcst_val K_110) | lra | lia | lia | lia].
  apply (den_lv U _ u _ K_156 156 126 127 254 HU); [| exact (tcst_val K_156) | lra | lia | lia | lia].
  apply (den_lv0 U u K_210 210 126 127 HU); [exact (tcst_val K_210) | lra | lia | lia | lia].
Qed.

(* The core: arg = v * PH, its square, the polynomial, the product. *)
Lemma core_den (V : b64) (v : R) : den V v 62 -> den (T_core b64 tieee_ops V) (turn_core v) 952.
Proof.
  intros HV. unfold T_core, turn_core.
  assert (Ha : den (T_arg b64 tieee_ops V) (turn_arg v) 63).
  { unfold T_arg, turn_arg.
    exact (den_mul V (t_cst tieee_ops K_PH) v cos32_PH 62 1 63 HV den_PH ltac:(lia) ltac:(lia)). }
  assert (Hs : den (T_sq b64 tieee_ops (T_arg b64 tieee_ops V)) (sin32_sq (turn_arg v)) 126).
  { unfold T_sq, sin32_sq.
    exact (den_mul _ _ _ _ 63 63 126 Ha Ha ltac:(lia) ltac:(lia)). }
  pose proof (poly_den _ _ Hs) as Hp.
  exact (den_mul _ _ _ _ 63 889 952 Ha Hp ltac:(lia) ltac:(lia)).
Qed.
