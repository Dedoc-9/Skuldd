(* Proof of COS32_ALL (statement in COS32_Statement.v). Nothing is admitted.
   The graph is narrow(y), y = RN64(t p), p = sin32_poly(u), u = RN64(t^2), t = RN64(RN64(PH - |x|) + PL).
   With a = |x|, D = PH - a, T = PI/2 - a (so cos x = sin T) and c = 2^-53:
     the one fact about pi (PiBound.v): |PH + PL - PI/2| <= 2^-60;
     |D| >= 2^-25: for a < 1 at once, for a >= 1 because a is a whole number over 2^23 (f32_grid, shift_lb; no pi);
     the shift (shift_rel): two roundings and the pi fact give |t - T| <= 2^-32 |T|, 2^-26 <= |T| <= 63/40;
     sin32's own lemmas at the real argument t (poly_total, rnd_abs of Sin32.v; Pex_range, sin_trunc of Trunc.v):
       |y - t P(t^2)| <= |t| (9c + 8c^2), |t P(t^2) - sin t| <= |t| 2^-37;
     |sin t - sin T| <= |t - T| (1 + 2^-37) (sin_lip) and |sin T| >= 7/12 |T| (sin_trunc at T);
     together far below 2^-27 |sin T|; T32 turns narrow into RN32 and lemma F32 turns 2^-27 into faithfulness.
   COS32_FINITE follows from COS32, |cos x| <= 1 and p32r's faithful_finite. sin32 is imported, not edited. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core Relative.
From MKF.f32 Require Import F32_Statement F32.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.sin32 Require Import Graph Trunc Sin32.
From MKF.cos32 Require Import Graph COS32_Statement.
From MKF.cos32 Require PiBound.
Open Scope R_scope.

#[local] Instance e24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance e53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

(* Two values and their distance. *)
Lemma abs_near (p q : R) : Rabs p <= Rabs q + Rabs (p - q) /\ Rabs q <= Rabs p + Rabs (p - q).
Proof.
  split.
  - replace p with (q + (p - q)) at 1 by ring. apply Rabs_triang.
  - replace q with (p + - (p - q)) at 1 by ring.
    eapply Rle_trans; [apply Rabs_triang |]. rewrite Rabs_Ropp. apply Rle_refl.
Qed.

Lemma sq_abs (h : R) : h * h = Rabs h * Rabs h.
Proof. rewrite <- Rabs_mult. symmetry. apply Rabs_pos_eq. apply Rle_0_sqr. Qed.

(* A binary32 number that is at least 1 is a whole number over 2^23. *)
Lemma f32_grid (a : R) : format32 a -> 1 <= a -> exists k : Z, a = IZR k / 8388608.
Proof.
  intros Fa Ha.
  assert (M : (1 <= mag radix2 a)%Z).
  { apply mag_ge_bpow. change (bpow radix2 (1 - 1)) with 1. rewrite Rabs_pos_eq by lra. exact Ha. }
  assert (E : (-23 <= cexp radix2 fexp32 a)%Z) by (unfold cexp, FLT_exp; lia).
  unfold generic_format, F2R in Fa. simpl in Fa.
  set (m := Ztrunc (scaled_mantissa radix2 fexp32 a)) in *.
  set (e := cexp radix2 fexp32 a) in *.
  exists (m * Zpower radix2 (e + 23))%Z.
  rewrite mult_IZR, IZR_Zpower by lia. rewrite bpow_plus.
  change (bpow radix2 23) with 8388608.
  transitivity (IZR m * bpow radix2 e); [exact Fa | field].
Qed.

(* PH - |x| is never small: at least 2^-25 in magnitude. A statement about rationals; no pi. *)
Lemma shift_lb (x : R) : format32 x -> Rabs x <= CMAX -> / 33554432 <= Rabs (cos32_PH - Rabs x).
Proof.
  intros Fx Hx. pose proof (Rabs_pos x) as Pa.
  assert (Fa : format32 (Rabs x)) by (apply generic_format_abs; exact Fx).
  set (a := Rabs x) in *. unfold CMAX in Hx. unfold cos32_PH.
  destruct (Rlt_le_dec a 1) as [L | G].
  - rewrite Rabs_pos_eq by lra. lra.
  - destruct (f32_grid a Fa G) as [k Ek].
    destruct (Z_le_gt_dec k 13176794) as [K | K].
    + apply IZR_le in K. rewrite Rabs_pos_eq by lra. lra.
    + assert (K' : (13176795 <= k)%Z) by lia. apply IZR_le in K'.
      rewrite <- Rabs_Ropp, Rabs_pos_eq by lra. lra.
Qed.

(* The shift: t against T = PI/2 - |x|, relatively; and where T lies. *)
Lemma shift_rel (x : R) : format32 x -> Rabs x <= CMAX ->
  Rabs (cos32_shift x - (PI / 2 - Rabs x)) <= / 4294967296 * Rabs (PI / 2 - Rabs x) /\
  / 67108864 <= Rabs (PI / 2 - Rabs x) /\ Rabs (PI / 2 - Rabs x) <= 63 / 40.
Proof.
  intros Fx Hx. pose proof (shift_lb x Fx Hx) as LB. pose proof PiBound.pi_fact as Pf.
  pose proof (Rabs_pos x) as Pa. unfold CMAX in Hx.
  unfold cos32_shift. set (a := Rabs x) in *. set (D := cos32_PH - a) in *.
  assert (ZD : bpow radix2 (-1022) <= Rabs D).
  { apply Rle_trans with (2 := LB). change (/ 33554432) with (bpow radix2 (-25)). apply bpow_le. lia. }
  pose proof (rn64_rel D ZD) as Rd. set (d := RN64 D) in *.
  assert (PLr : 0 <= cos32_PL <= / 9007199254740992) by (unfold cos32_PL; lra).
  assert (S1 : Rabs (d + cos32_PL - D) <= Rabs (d - D) + cos32_PL).
  { replace (d + cos32_PL - D) with ((d - D) + cos32_PL) by ring.
    eapply Rle_trans; [apply Rabs_triang |]. rewrite (Rabs_pos_eq cos32_PL) by lra. apply Rle_refl. }
  destruct (abs_near (d + cos32_PL) D) as [S2 S3].
  assert (Zs : bpow radix2 (-1022) <= Rabs (d + cos32_PL)).
  { apply Rle_trans with (/ 134217728); [| lra].
    change (/ 134217728) with (bpow radix2 (-27)). apply bpow_le. lia. }
  pose proof (rn64_rel (d + cos32_PL) Zs) as Rt. set (t := RN64 (d + cos32_PL)) in *.
  set (T := PI / 2 - a).
  assert (T1 : Rabs (T - D) <= cos32_PL + / 1152921504606846976).
  { replace (T - D) with (cos32_PL + - (cos32_PH + cos32_PL - PI / 2)) by (unfold T, D; ring).
    eapply Rle_trans; [apply Rabs_triang |]. rewrite Rabs_Ropp, (Rabs_pos_eq cos32_PL) by lra. lra. }
  destruct (abs_near T D) as [T2 T3].
  assert (T4 : Rabs (t - T) <= Rabs (t - (d + cos32_PL)) + Rabs (d - D) + / 1152921504606846976).
  { replace (t - T) with ((t - (d + cos32_PL)) + (d - D) + (cos32_PH + cos32_PL - PI / 2)) by (unfold T, D; ring).
    eapply Rle_trans; [apply Rabs_triang |]. eapply Rle_trans; [apply Rplus_le_compat_r, Rabs_triang |]. lra. }
  split; [lra | split; [lra |]].
  apply Rabs_le_inv in Pf. apply Rabs_le. unfold T. unfold cos32_PH, cos32_PL in Pf. lra.
Qed.

(* |sin h| <= |h| (1 + 2^-37) for a small h, from sin32's truncation bound. *)
Lemma sin_abs_le (h : R) : h * h <= 5 / 2 -> Rabs (sin h) <= Rabs h * (1 + / 137438953472).
Proof.
  intros Hh. destruct (sin_trunc h Hh) as [Tr _].
  assert (W : 7 / 12 <= Pex (h * h) <= 1) by (apply Pex_range; split; [apply Rle_0_sqr | exact Hh]).
  pose proof (Rabs_pos h) as Ph.
  assert (B : Rabs (h * Pex (h * h)) <= Rabs h).
  { rewrite Rabs_mult, (Rabs_pos_eq (Pex (h * h))) by lra.
    apply Rle_trans with (Rabs h * 1); [apply Rmult_le_compat_l; lra | lra]. }
  destruct (abs_near (h * Pex (h * h)) (sin h)) as [_ N]. lra.
Qed.

(* sin does not spread two near arguments. *)
Lemma sin_lip (p q : R) : Rabs (p - q) <= 1 -> Rabs (sin p - sin q) <= Rabs (p - q) * (1 + / 137438953472).
Proof.
  intros H. rewrite form4. set (h := (p - q) / 2). set (c := (p + q) / 2).
  assert (Ah : Rabs h = Rabs (p - q) / 2).
  { unfold h, Rdiv. rewrite Rabs_mult, (Rabs_pos_eq (/ 2)) by lra. reflexivity. }
  pose proof (Rabs_pos h) as Ph.
  assert (Hh : h * h <= 5 / 2).
  { rewrite sq_abs. apply Rle_trans with (1 * 1); [apply Rmult_le_compat; lra | lra]. }
  pose proof (sin_abs_le h Hh) as S. pose proof (COS_bound c) as C.
  assert (Ac : Rabs (cos c) <= 1) by (apply Rabs_le; lra).
  rewrite !Rabs_mult, (Rabs_pos_eq 2) by lra.
  pose proof (Rabs_pos (cos c)) as Pc. pose proof (Rabs_pos (sin h)) as Ps.
  assert (X : Rabs (cos c) * Rabs (sin h) <= 1 * (Rabs h * (1 + / 137438953472)))
    by (apply Rmult_le_compat; lra).
  lra.
Qed.

(* The value before narrow: within 2^-27 of cos x, relatively. *)
Lemma cos32_core (x : R) : format32 x -> Rabs x <= CMAX ->
  Rabs (RN64 (cos32_shift x * sin32_poly (sin32_sq (cos32_shift x))) - cos x) <= bpow radix2 (-27) * Rabs (cos x).
Proof.
  intros Fx Hx. pose proof CC_range as Hcc.
  destruct (shift_rel x Fx Hx) as [St [Tlo Thi]].
  assert (Ec : cos x = sin (PI / 2 - Rabs x)).
  { rewrite sin_shift. unfold Rabs. destruct (Rcase_abs x); [rewrite cos_neg |]; reflexivity. }
  rewrite Ec. set (T := PI / 2 - Rabs x) in *. set (t := cos32_shift x) in *.
  destruct (abs_near t T) as [N1 N2].
  pose proof (Rabs_pos t) as Pt. pose proof (Rabs_pos (t - T)) as Pe.
  pose proof (bpow_gt_0 radix2 (-300)) as B300.
  assert (At1 : Rabs t <= 79 / 50) by lra.
  assert (At0 : / 134217728 <= Rabs t) by lra.
  assert (V1 : t * t <= 5 / 2).
  { rewrite sq_abs. apply Rle_trans with (79 / 50 * (79 / 50)); [apply Rmult_le_compat; lra | lra]. }
  assert (V0 : bpow radix2 (-300) <= t * t).
  { rewrite sq_abs. apply Rle_trans with (bpow radix2 (-27) * bpow radix2 (-27)).
    - rewrite <- bpow_plus. apply bpow_le. lia.
    - change (bpow radix2 (-27)) with (/ 134217728). apply Rmult_le_compat; lra. }
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
    apply Rle_trans with (bpow radix2 (-27) * / 2).
    - change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia.
    - change (bpow radix2 (-27)) with (/ 134217728). apply Rmult_le_compat; lra. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  replace (RN64 (t * p) - sin T) with ((RN64 (t * p) - t * P) + (t * P - sin t) + (sin t - sin T)) by ring.
  eapply Rle_trans; [apply Rabs_triang |]. eapply Rle_trans; [apply Rplus_le_compat_r, Rabs_triang |].
  change (bpow radix2 (-27)) with (/ 134217728).
  unfold CC in A2. lra.
Qed.

Theorem cos32_faithful : COS32.
Proof.
  unfold COS32, g_cos32. intros x Fx Hx.
  set (y := RN64 (cos32_shift x * sin32_poly (sin32_sq (cos32_shift x)))).
  assert (Fy : format64 y) by (unfold y; apply generic_format_round; typeclasses eauto).
  rewrite (T32_proof y Fy). apply (F32_rel (cos x) y). exact (cos32_core x Fx Hx).
Qed.

Theorem cos32_finite : COS32_FINITE.
Proof.
  unfold COS32_FINITE. intros x Fx Hx.
  apply (faithful_finite (cos x)); [| apply cos32_faithful; assumption].
  pose proof (COS_bound x) as S.
  apply Rle_trans with 1; [apply Rabs_le; lra |].
  apply Rle_trans with (bpow radix2 127); [apply (bpow_le radix2 0 127); lia | exact fmax_ge].
Qed.

Theorem cos32_all : COS32_ALL.
Proof. split; [exact cos32_faithful | exact cos32_finite]. Qed.
