(* The reduction of sinturn32 / costurn32 (graph in Graph.v). Flocq only; nothing is admitted.
   turn_N v = RN64(RN64(v + 1.5 * 2^52) - 1.5 * 2^52) is the whole number nearest v (ties to even) when |v| < 2^23:
     v + 1.5 * 2^52 lies in [2^52, 2^53), where binary64's grid is 1; adding the even whole number 1.5 * 2^52
     commutes with round-to-nearest-even (T32's ZnearestE_plus_even); the subtraction is then exact.
     The tie direction is in the lemma and is used nowhere after it: only |v - N| <= 1/2.
   For a binary32 x with |x| < 2^23: f = x - N(x), q = 4 f and r = q - N(q) are all exact and all binary32 numbers
     (Flocq's format_REM_N: a binary32 number minus the nearest whole number is a binary32 number), so
     x = n + (k + r) / 4 with n, k whole, |k| <= 2, |r| <= 1/2, and r is 0 or at least 2^-149 in magnitude.
   A binary32 x with |x| >= 2^23 is a whole number. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core Div_sqrt_error.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs T32.
From MKF.sin32 Require Import Graph.
From MKF.cos32 Require Import Graph.
From MKF.sincos32 Require Import Graph.
Open Scope R_scope.

#[local] Instance i24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance i53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

(* A whole number below 2^53 in magnitude is a binary64 number. *)
Lemma int_f64 (m : Z) : (Z.abs m < 9007199254740992)%Z -> format64 (IZR m).
Proof.
  intros H. apply generic_format_FLT. apply (FLT_spec radix2 (-1074) 53 _ (Float radix2 m 0)).
  - unfold F2R. cbn [Fnum Fexp]. change (bpow radix2 0) with 1. ring.
  - cbn [Fnum]. assert (E : (radix2 ^ 53 = 9007199254740992)%Z) by reflexivity. rewrite E. exact H.
  - cbn [Fexp]. lia.
Qed.

(* A binary32 number as a whole number below 2^24 times a power of two not below 2^-149. *)
Lemma f32_rep (x : R) : format32 x ->
  exists (m e : Z), x = IZR m * bpow radix2 e /\ (Z.abs m < 16777216)%Z /\ (-149 <= e)%Z.
Proof.
  intros F. destruct (FLT_format_generic radix2 (-149) 24 x F) as [f E1 E2 E3].
  exists (Fnum f), (Fexp f). split; [exact E1 | split; [| exact E3]].
  assert (E : (radix2 ^ 24 = 16777216)%Z) by reflexivity. rewrite E in E2. exact E2.
Qed.

Lemma rep_f32 (m e : Z) : (Z.abs m < 16777216)%Z -> (-149 <= e)%Z -> format32 (IZR m * bpow radix2 e).
Proof.
  intros Hm He. apply generic_format_FLT. apply (FLT_spec radix2 (-149) 24 _ (Float radix2 m e)).
  - reflexivity.
  - cbn [Fnum]. assert (E : (radix2 ^ 24 = 16777216)%Z) by reflexivity. rewrite E. exact Hm.
  - cbn [Fexp]. exact He.
Qed.

Lemma f32_f64 (x : R) : format32 x -> format64 x.
Proof.
  intros F. destruct (f32_rep x F) as (m & e & E & Hm & He). rewrite E.
  apply generic_format_FLT. apply (FLT_spec radix2 (-1074) 53 _ (Float radix2 m e)).
  - reflexivity.
  - cbn [Fnum]. assert (E2 : (radix2 ^ 53 = 9007199254740992)%Z) by reflexivity. rewrite E2. lia.
  - cbn [Fexp]. lia.
Qed.

Lemma f32_scale4 (x : R) : format32 x -> format32 (4 * x).
Proof.
  intros F. destruct (f32_rep x F) as (m & e & E & Hm & He).
  replace (4 * x) with (IZR m * bpow radix2 (e + 2)).
  - apply rep_f32; [exact Hm | lia].
  - rewrite E, bpow_plus. change (bpow radix2 2) with 4. ring.
Qed.

Lemma f32_one : format32 1.
Proof. replace 1 with (IZR 1 * bpow radix2 0) by (change (bpow radix2 0) with 1; ring). apply rep_f32; lia. Qed.

(* The nearest whole number of a v below 2^23 in magnitude is at most 2^23 in magnitude. *)
Lemma near_bound (v : R) : Rabs v < 8388608 -> (Z.abs (ZnearestE v) < 8388610)%Z.
Proof.
  intros H. apply Rabs_lt_inv in H.
  pose proof (Znearest_half (fun z => negb (Z.even z)) v) as Hh. apply Rabs_le_inv in Hh.
  assert (A : (ZnearestE v < 8388610)%Z) by (apply lt_IZR; lra).
  assert (B : (-8388610 < ZnearestE v)%Z) by (apply lt_IZR; lra).
  lia.
Qed.

(* turn_N is the nearest whole number. *)
Lemma turn_N_eq (v : R) : Rabs v < 8388608 -> turn_N v = IZR (ZnearestE v).
Proof.
  intros H. pose proof (near_bound v H) as Hb. apply Rabs_lt_inv in H. unfold turn_N.
  assert (Hw : bpow radix2 (53 - 1) <= Rabs (v + turn_CN) < bpow radix2 53).
  { unfold turn_CN. rewrite Rabs_pos_eq by lra.
    change (bpow radix2 (53 - 1)) with 4503599627370496. change (bpow radix2 53) with 9007199254740992. lra. }
  assert (C : cexp radix2 fexp64 (v + turn_CN) = 0%Z).
  { unfold cexp. rewrite (mag_unique radix2 (v + turn_CN) 53 Hw). reflexivity. }
  rewrite (round_at fexp64 ZnearestE (v + turn_CN) 0 C).
  change (- 0)%Z with 0%Z. change (bpow radix2 0) with 1. rewrite !Rmult_1_r. unfold turn_CN.
  match goal with |- context [ZnearestE (v + IZR ?n)] => rewrite (ZnearestE_plus_even v n) by reflexivity;
    rewrite plus_IZR; replace (IZR (ZnearestE v) + IZR n - IZR n) with (IZR (ZnearestE v)) by ring
  end.
  apply round_generic; [typeclasses eauto |]. apply int_f64. lia.
Qed.

(* A binary32 number minus its nearest whole number is a binary32 number. *)
Lemma f32_frac (x : R) : format32 x -> format32 (x - IZR (ZnearestE x)).
Proof.
  intros Fx.
  pose proof (format_REM_N radix2 fexp32 (fun z => negb (Z.even z)) x 1 Fx f32_one) as H.
  replace (x / 1) with x in H by field. rewrite Rmult_1_r in H. exact H.
Qed.

(* The reduction, for a binary32 x below 2^23 in magnitude. *)
Lemma reduce (x : R) : format32 x -> Rabs x < 8388608 ->
  exists (n kz : Z) (r : R),
    turn_k x = IZR kz /\ turn_r x = r /\ x = IZR n + (IZR kz + r) / 4 /\
    Rabs r <= / 2 /\ (-2 <= kz <= 2)%Z /\ format32 r.
Proof.
  intros Fx Hx.
  assert (EN : turn_N x = IZR (ZnearestE x)) by (apply turn_N_eq; exact Hx).
  pose proof (f32_frac x Fx) as Ff.
  pose proof (Znearest_half (fun z => negb (Z.even z)) x) as Hf.
  assert (Ef : turn_f x = x - IZR (ZnearestE x)).
  { unfold turn_f. rewrite EN. apply round_generic; [typeclasses eauto | apply f32_f64; exact Ff]. }
  pose proof (f32_scale4 _ Ff) as Fq.
  assert (Eq : turn_q x = 4 * (x - IZR (ZnearestE x))).
  { unfold turn_q. rewrite Ef. apply round_generic; [typeclasses eauto | apply f32_f64; exact Fq]. }
  assert (Hq : Rabs (4 * (x - IZR (ZnearestE x))) <= 2).
  { rewrite Rabs_mult, (Rabs_pos_eq 4) by lra. lra. }
  assert (Hq' : Rabs (4 * (x - IZR (ZnearestE x))) < 8388608) by lra.
  assert (Ek : turn_k x = IZR (ZnearestE (4 * (x - IZR (ZnearestE x))))).
  { unfold turn_k. rewrite Eq. apply turn_N_eq. exact Hq'. }
  pose proof (f32_frac _ Fq) as Fr.
  pose proof (Znearest_half (fun z => negb (Z.even z)) (4 * (x - IZR (ZnearestE x)))) as Hr.
  assert (Er : turn_r x = 4 * (x - IZR (ZnearestE x)) - IZR (ZnearestE (4 * (x - IZR (ZnearestE x))))).
  { unfold turn_r. rewrite Ek, Eq. apply round_generic; [typeclasses eauto | apply f32_f64; exact Fr]. }
  exists (ZnearestE x), (ZnearestE (4 * (x - IZR (ZnearestE x)))),
    (4 * (x - IZR (ZnearestE x)) - IZR (ZnearestE (4 * (x - IZR (ZnearestE x))))).
  split; [exact Ek | split; [exact Er | split; [field | split; [exact Hr | split; [| exact Fr]]]]].
  apply Rabs_le_inv in Hq. apply Rabs_le_inv in Hr.
  set (kz := ZnearestE (4 * (x - IZR (ZnearestE x)))) in *.
  assert (A : (kz < 3)%Z) by (apply lt_IZR; lra).
  assert (B : (-3 < kz)%Z) by (apply lt_IZR; lra).
  lia.
Qed.

(* A binary32 number of magnitude 2^23 or more is a whole number. *)
Lemma f32_int (x : R) : format32 x -> 8388608 <= Rabs x -> exists n : Z, x = IZR n.
Proof.
  intros Fx Hx.
  assert (M : (24 <= mag radix2 x)%Z).
  { apply mag_ge_bpow. change (bpow radix2 (24 - 1)) with 8388608. exact Hx. }
  assert (E : (0 <= cexp radix2 fexp32 x)%Z) by (unfold cexp, FLT_exp; lia).
  unfold generic_format, F2R in Fx. cbn [Fnum Fexp] in Fx.
  set (m := Ztrunc (scaled_mantissa radix2 fexp32 x)) in *.
  set (e := cexp radix2 fexp32 x) in *.
  exists (m * Zpower radix2 e)%Z.
  rewrite mult_IZR, IZR_Zpower by lia. exact Fx.
Qed.
