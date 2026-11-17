(* The core of sinturn32 / costurn32: turn_core v = RN64(t p), t = turn_arg v = RN64(v PH), p = sin32_poly(RN64(t^2)).
   Nothing is admitted. With c = 2^-53:
     arg_rel   v within c |V| of V, |V| >= 2^-149: t is within 2^-32 |T| of T = PI/2 V. One rounding, and the one
               fact about pi (cos32's PiBound: |PH + PL - PI/2| <= 2^-60, with PL only as a bound, PL <= 2^-53).
               PH multiplies; it is never subtracted against pi.
     core_abs  |t - T| <= 2^-32 |T|, 2^-149 <= |T| <= 63/40: RN64(t p) is within 2^-27 |sin T| of sin T. The body
               of cos32's cos32_core with the argument abstract (sin32's poly_total, rnd_abs, Pex_range, sin_trunc
               at the real t; cos32's sin_lip, abs_near, sq_abs).
     S_ok      for a binary32 r, |r| <= 1/2: turn_core r against sin (PI/2 r); r = 0 gives exactly 0.
     C_ok      for |r| <= 1/2: turn_core (RN64 (1 - |r|)) against cos (PI/2 r) = sin (PI/2 (1 - |r|)). 1 - |r| is
               NOT taken as exact: it is one rounding of a value in [1/2, 1]. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core Relative.
From MKF.f32 Require Import F32_Statement F32.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs.
From MKF.sin32 Require Import Graph Trunc Sin32.
From MKF.cos32 Require Import Graph Cos32.
From MKF.cos32 Require PiBound.
From MKF.sincos32 Require Import Graph Reduce.
Open Scope R_scope.

#[local] Instance j24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance j53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

(* What is used of pi and PH. *)
Lemma ph_facts : 1 < PI / 2 /\ PI / 2 < 63 / 40 /\ 1 < cos32_PH < 2 /\
  Rabs (cos32_PH - PI / 2) <= / 4503599627370496.
Proof.
  pose proof PiBound.pi_lo as L. pose proof PiBound.pi_hi as H. unfold PiBound.Q1, PiBound.Q2 in L, H.
  split; [lra | split; [lra | split; [unfold cos32_PH; lra |]]].
  apply Rabs_le. unfold cos32_PH. lra.
Qed.

Lemma b149 : bpow radix2 (-149) = 2 * bpow radix2 (-150).
Proof. change 2 with (bpow radix2 1). rewrite <- bpow_plus. reflexivity. Qed.

(* The argument: one rounding and the constant. *)
Lemma arg_rel (v V : R) : Rabs (v - V) <= CC * Rabs V -> bpow radix2 (-149) <= Rabs V ->
  Rabs (turn_arg v - PI / 2 * V) <= / 4294967296 * Rabs (PI / 2 * V).
Proof.
  intros Hv HV. destruct ph_facts as (P1 & P2 & P3 & P4). pose proof CC_range as Hcc.
  pose proof (bpow_gt_0 radix2 (-150)) as B150. pose proof b149 as E149.
  destruct (abs_near v V) as [N1 N2].
  pose proof (Rabs_pos V) as PV. pose proof (Rabs_pos v) as Pv.
  assert (Cv : CC * Rabs V <= / 1024 * Rabs V) by (apply Rmult_le_compat_r; lra).
  unfold turn_arg.
  assert (Z : bpow radix2 (-1022) <= Rabs (v * cos32_PH)).
  { rewrite Rabs_mult, (Rabs_pos_eq cos32_PH) by lra.
    apply Rle_trans with (bpow radix2 (-150)); [apply bpow_le; lia |].
    apply Rle_trans with (Rabs v * 1); [lra | apply Rmult_le_compat_l; lra]. }
  pose proof (rn64_rel _ Z) as R1.
  rewrite Rabs_mult, (Rabs_pos_eq cos32_PH) in R1 by lra.
  assert (R1' : Rabs (RN64 (v * cos32_PH) - v * cos32_PH) <= / 2 * / 4503599627370496 * (Rabs v * 2)).
  { eapply Rle_trans; [exact R1 |]. apply Rmult_le_compat_l; [lra |]. apply Rmult_le_compat_l; lra. }
  assert (R2 : Rabs ((v - V) * cos32_PH) <= CC * Rabs V * 2).
  { rewrite Rabs_mult, (Rabs_pos_eq cos32_PH) by lra.
    apply Rmult_le_compat; try apply Rabs_pos; lra. }
  assert (R3 : Rabs (V * (cos32_PH - PI / 2)) <= Rabs V * / 4503599627370496).
  { rewrite Rabs_mult. apply Rmult_le_compat_l; [exact PV | exact P4]. }
  assert (R4 : Rabs V <= Rabs (PI / 2 * V)).
  { rewrite Rabs_mult, (Rabs_pos_eq (PI / 2)) by lra.
    apply Rle_trans with (1 * Rabs V); [lra | apply Rmult_le_compat_r; lra]. }
  replace (RN64 (v * cos32_PH) - PI / 2 * V)
    with ((RN64 (v * cos32_PH) - v * cos32_PH) + (v - V) * cos32_PH + V * (cos32_PH - PI / 2)) by ring.
  eapply Rle_trans; [apply Rabs_triang |]. eapply Rle_trans; [apply Rplus_le_compat_r, Rabs_triang |].
  unfold CC in *. lra.
Qed.

(* The value of the core against sin T, for an argument t near T. *)
Lemma core_abs (t T : R) : Rabs (t - T) <= / 4294967296 * Rabs T ->
  bpow radix2 (-149) <= Rabs T -> Rabs T <= 63 / 40 ->
  Rabs (RN64 (t * sin32_poly (sin32_sq t)) - sin T) <= bpow radix2 (-27) * Rabs (sin T).
Proof.
  intros St Tlo Thi. pose proof CC_range as Hcc.
  pose proof (bpow_gt_0 radix2 (-150)) as B150. pose proof b149 as E149.
  destruct (abs_near t T) as [N1 N2].
  pose proof (Rabs_pos t) as Pt. pose proof (Rabs_pos (t - T)) as Pe.
  pose proof (bpow_gt_0 radix2 (-300)) as B300.
  assert (At1 : Rabs t <= 79 / 50) by lra.
  assert (At0 : bpow radix2 (-150) <= Rabs t) by lra.
  assert (V1 : t * t <= 5 / 2).
  { rewrite sq_abs. apply Rle_trans with (79 / 50 * (79 / 50)); [apply Rmult_le_compat; lra | lra]. }
  assert (V0 : bpow radix2 (-300) <= t * t).
  { rewrite sq_abs. apply Rle_trans with (bpow radix2 (-150) * bpow radix2 (-150)).
    - rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  assert (W1 : T * T <= 5 / 2).
  { rewrite sq_abs. pose proof (Rabs_pos T).
    apply Rle_trans with (63 / 40 * (63 / 40)); [apply Rmult_le_compat; lra | lra]. }
  assert (Zu : bpow radix2 (-1022) <= Rabs (t * t)).
  { rewrite Rabs_pos_eq by lra. apply Rle_trans with (2 := V0). apply bpow_le. lia. }
  assert (Hu : Rabs (sin32_sq t - t * t) <= CC * (t * t)).
  { unfold sin32_sq. eapply Rle_trans; [apply rn64_rel; exact Zu |].
    rewrite Rabs_pos_eq by lra. unfold CC. apply Rle_refl. }
  pose proof (poly_total (t * t) (sin32_sq t) V0 V1 Hu) as Hp.
  assert (W : 7 / 12 <= Pex (t * t) <= 1) by (apply Pex_range; lra).
  destruct (sin_trunc t V1) as [Tr _]. destruct (sin_trunc T W1) as [_ Lo].
  assert (L : Rabs (sin t - sin T) <= Rabs (t - T) * (1 + / 137438953472)) by (apply sin_lip; lra).
  set (p := sin32_poly (sin32_sq t)) in *. set (P := Pex (t * t)) in *.
  assert (Hp' := Rabs_le_inv _ _ Hp).
  assert (A1 : Rabs (t * p - t * P) <= Rabs t * (8 * CC)).
  { replace (t * p - t * P) with (t * (p - P)) by ring. rewrite Rabs_mult.
    apply Rmult_le_compat_l; [exact Pt | exact Hp]. }
  assert (B1 : Rabs (t * P) <= Rabs t).
  { rewrite Rabs_mult, (Rabs_pos_eq P) by lra.
    apply Rle_trans with (Rabs t * 1); [apply Rmult_le_compat_l; lra | lra]. }
  assert (Z1 : bpow radix2 (-1022) <= Rabs (t * p)).
  { rewrite Rabs_mult, (Rabs_pos_eq p) by lra.
    apply Rle_trans with (bpow radix2 (-150) * / 2).
    - change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  replace (RN64 (t * p) - sin T) with ((RN64 (t * p) - t * P) + (t * P - sin t) + (sin t - sin T)) by ring.
  eapply Rle_trans; [apply Rabs_triang |]. eapply Rle_trans; [apply Rplus_le_compat_r, Rabs_triang |].
  change (bpow radix2 (-27)) with (/ 134217728).
  unfold CC in A2. lra.
Qed.

Lemma core_0 : turn_core 0 = 0.
Proof.
  unfold turn_core, turn_arg.
  rewrite Rmult_0_l, (round_0 radix2 fexp64 ZnearestE), Rmult_0_l, (round_0 radix2 fexp64 ZnearestE). reflexivity.
Qed.

(* The sine side: the argument r is exact. *)
Lemma S_ok (r : R) : format32 r -> Rabs r <= / 2 ->
  Rabs (turn_core r - sin (PI / 2 * r)) <= bpow radix2 (-27) * Rabs (sin (PI / 2 * r)).
Proof.
  intros Fr Hr. destruct (Req_dec r 0) as [Z | N].
  - subst r. rewrite core_0, Rmult_0_r, sin_0, Rminus_0_r, Rabs_R0, Rmult_0_r. apply Rle_refl.
  - destruct ph_facts as (P1 & P2 & P3 & P4). pose proof CC_range as Hcc.
    assert (Ar : bpow radix2 (-149) <= Rabs r)
      by (apply f32_pos_ge; [apply generic_format_abs; exact Fr | apply Rabs_pos_lt; exact N]).
    pose proof (bpow_gt_0 radix2 (-149)) as B149.
    assert (H0 : Rabs (r - r) <= CC * Rabs r).
    { replace (r - r) with 0 by ring. rewrite Rabs_R0. apply Rmult_le_pos; lra. }
    pose proof (arg_rel r r H0 Ar) as Ha.
    assert (ET : Rabs (PI / 2 * r) = PI / 2 * Rabs r) by (rewrite Rabs_mult, (Rabs_pos_eq (PI / 2)) by lra; reflexivity).
    unfold turn_core. apply core_abs; [exact Ha | |]; rewrite ET.
    + apply Rle_trans with (1 * Rabs r); [lra | apply Rmult_le_compat_r; lra].
    + apply Rle_trans with (63 / 40 * / 2); [apply Rmult_le_compat; lra | lra].
Qed.

(* The cosine side: w = RN64 (1 - |r|), one rounding of a value in [1/2, 1]. *)
Lemma C_ok (r : R) : Rabs r <= / 2 ->
  Rabs (turn_core (RN64 (1 - Rabs r)) - cos (PI / 2 * r)) <= bpow radix2 (-27) * Rabs (cos (PI / 2 * r)).
Proof.
  intros Hr. destruct ph_facts as (P1 & P2 & P3 & P4). pose proof CC_range as Hcc.
  pose proof (Rabs_pos r) as Pr.
  assert (Ec : cos (PI / 2 * r) = sin (PI / 2 * (1 - Rabs r))).
  { replace (PI / 2 * (1 - Rabs r)) with (PI / 2 - PI / 2 * Rabs r) by ring. rewrite sin_shift.
    unfold Rabs. destruct (Rcase_abs r); [| reflexivity].
    replace (PI / 2 * - r) with (- (PI / 2 * r)) by ring. rewrite cos_neg. reflexivity. }
  rewrite Ec. set (V := 1 - Rabs r) in *.
  assert (HV : / 2 <= V <= 1) by (unfold V; lra).
  assert (AV : Rabs V = V) by (apply Rabs_pos_eq; lra).
  pose proof (rn64_rel V (half_ok V (proj1 HV))) as Rw. rewrite AV in Rw.
  assert (H0 : Rabs (RN64 V - V) <= CC * Rabs V) by (rewrite AV; unfold CC; exact Rw).
  assert (B : bpow radix2 (-149) <= Rabs V).
  { rewrite AV. apply Rle_trans with (/ 2); [| lra]. change (/ 2) with (bpow radix2 (-1)). apply bpow_le. lia. }
  pose proof (arg_rel (RN64 V) V H0 B) as Ha.
  assert (ET : Rabs (PI / 2 * V) = PI / 2 * V) by (apply Rabs_pos_eq; apply Rmult_le_pos; lra).
  unfold turn_core. apply core_abs; [exact Ha | |]; rewrite ET.
  - apply Rle_trans with (1 * / 2).
    + apply Rle_trans with (/ 2); [| lra]. change (/ 2) with (bpow radix2 (-1)). apply bpow_le. lia.
    + apply Rmult_le_compat; lra.
  - apply Rle_trans with (63 / 40 * 1); [apply Rmult_le_compat; lra | lra].
Qed.
