(* Proof of SIN32_ALL (statement in SIN32_Statement.v). Flocq and the standard library only; nothing is admitted.
   The graph is narrow(y), y = RN64(x t7), t7 = sin32_poly(u), u = RN64(x^2). With c = 2^-53 and v = x^2 <= 5/2:
     u is within c v of v (x is 0 or at least 2^-149 in magnitude, so nothing is subnormal in binary64);
     every level keeps |t - T| <= 8c against its exact value T, which lies in [7/12, 1] (lv_first, lv_step);
     the last product: |y - x P(v)| <= |x| (9c + 8c^2);
     truncation (Trunc.v): |x P(v) - sin x| <= |x| 2^-37, and |x| 7/12 <= |sin x|;
     together far below 2^-27 |sin x|; T32 turns narrow into RN32 and lemma F32 turns 2^-27 into faithfulness.
   x = 0 is taken apart. SIN32_FINITE follows from SIN32, |sin x| <= 1 and p32r's faithful_finite. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core Relative.
From MKF.f32 Require Import F32_Statement F32.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.sin32 Require Import Graph SIN32_Statement Trunc.
Open Scope R_scope.

#[local] Instance e24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance e53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

Definition CC : R := / 2 * / 4503599627370496.
Lemma CC_range : 0 <= CC <= / 1024. Proof. unfold CC. lra. Qed.
Lemma CC_sq : CC * CC <= / 1024 * CC.
Proof. pose proof CC_range. apply Rmult_le_compat_r; lra. Qed.

Lemma half_ok (z : R) : / 2 <= z -> bpow radix2 (-1022) <= Rabs z.
Proof.
  intros H. rewrite Rabs_pos_eq by lra. apply Rle_trans with (2 := H).
  change (/ 2) with (bpow radix2 (-1)). apply bpow_le. lia.
Qed.

(* A value within E of w, |w| <= B, rounded: within E + (B + E) c of w. *)
Lemma rnd_abs (z w B E : R) : bpow radix2 (-1022) <= Rabs z -> Rabs (z - w) <= E -> Rabs w <= B ->
  Rabs (RN64 z - w) <= E + (B + E) * CC.
Proof.
  intros Hz He Hw. pose proof (rn64_rel z Hz) as H.
  assert (Bz : Rabs z <= B + E).
  { replace z with (w + (z - w)) at 1 by ring. eapply Rle_trans; [apply Rabs_triang |]. lra. }
  replace (RN64 z - w) with ((RN64 z - z) + (z - w)) by ring.
  eapply Rle_trans; [apply Rabs_triang |]. unfold CC. lra.
Qed.

(* Rounding does not go below a power of two that the argument is not below. *)
Lemma rn_ge (e : Z) (z : R) : (-1074 <= e)%Z -> bpow radix2 e <= z -> bpow radix2 e <= RN64 z.
Proof.
  intros He Hz. apply round_ge_generic; [typeclasses eauto | typeclasses eauto | | exact Hz].
  apply generic_format_FLT_bpow; [typeclasses eauto | exact He].
Qed.

(* One level as the graph computes it. *)
Definition lv (c u t : R) : R := RN64 (1 - RN64 (RN64 (u * t) / c)).

Lemma poly_fold (u : R) : sin32_poly u =
  lv 6 u (lv 20 u (lv 42 u (lv 72 u (lv 110 u (lv 156 u (RN64 (1 - RN64 (u / 210)))))))).
Proof. reflexivity. Qed.

(* The first level: 1 - u/210. *)
Lemma lv_first (v u : R) : bpow radix2 (-300) <= v -> v <= 5 / 2 -> Rabs (u - v) <= CC * v ->
  Rabs (RN64 (1 - RN64 (u / 210)) - (1 - v / 210)) <= 8 * CC.
Proof.
  intros Hv0 Hv1 Hu. pose proof CC_range as Hcc. pose proof CC_sq as Hsq.
  pose proof (bpow_gt_0 radix2 (-300)) as Bp.
  assert (Hu' := Rabs_le_inv _ _ Hu).
  assert (Cv : CC * v <= / 1024 * v) by (apply Rmult_le_compat_r; lra).
  assert (Cv2 : CC * v <= CC * (5 / 2)) by (apply Rmult_le_compat_l; lra).
  assert (A1 : Rabs (u / 210 - v / 210) <= CC).
  { replace (u / 210 - v / 210) with ((u - v) * / 210) by (unfold Rdiv; ring).
    rewrite Rabs_mult, (Rabs_pos_eq (/ 210)) by lra. pose proof (Rabs_pos (u - v)). lra. }
  assert (B1 : Rabs (v / 210) <= / 2) by (apply Rabs_le; lra).
  assert (Z1 : bpow radix2 (-1022) <= Rabs (u / 210)).
  { rewrite Rabs_pos_eq by lra.
    apply Rle_trans with (bpow radix2 (-300) * / 512); [| lra].
    change (/ 512) with (bpow radix2 (-9)). rewrite <- bpow_plus. apply bpow_le. lia. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  set (q := RN64 (u / 210)) in *.
  assert (A3 : Rabs ((1 - q) - (1 - v / 210)) <= 2 * CC).
  { replace ((1 - q) - (1 - v / 210)) with (- (q - v / 210)) by ring. rewrite Rabs_Ropp. lra. }
  assert (B3 : Rabs (1 - v / 210) <= 1) by (apply Rabs_le; lra).
  assert (Z3 : bpow radix2 (-1022) <= Rabs (1 - q)).
  { apply half_ok. assert (A3i := Rabs_le_inv _ _ A3). lra. }
  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4.
Admitted.

(* Every other level: 1 - (u t)/c against 1 - (v T)/c. *)
Lemma lv_step (c v u T t : R) :
  6 <= c <= 256 -> bpow radix2 (-300) <= v -> v <= 5 / 2 -> Rabs (u - v) <= CC * v ->
  7 / 12 <= T <= 1 -> Rabs (t - T) <= 8 * CC ->
  Rabs (lv c u t - lvx c v T) <= 8 * CC.
Proof.
  intros Hc Hv0 Hv1 Hu HT Ht. pose proof CC_range as Hcc. pose proof CC_sq as Hsq. unfold lv, lvx.
  pose proof (bpow_gt_0 radix2 (-300)) as Bp.
  assert (Hu' := Rabs_le_inv _ _ Hu). assert (Ht' := Rabs_le_inv _ _ Ht).
  assert (Cv : CC * v <= / 1024 * v) by (apply Rmult_le_compat_r; lra).
  assert (Cv2 : CC * v <= CC * (5 / 2)) by (apply Rmult_le_compat_l; lra).
  assert (A1 : Rabs (u * t - v * T) <= 23 * CC).
  { replace (u * t - v * T) with ((u - v) * t + v * (t - T)) by ring.
    eapply Rle_trans; [apply Rabs_triang |]. rewrite !Rabs_mult, (Rabs_pos_eq v) by lra.
    assert (X1 : Rabs (u - v) * Rabs t <= CC * v * (9 / 8)).
    { apply Rmult_le_compat; try apply Rabs_pos; [exact Hu | apply Rabs_le; lra]. }
    assert (X2 : v * Rabs (t - T) <= 5 / 2 * (8 * CC)).
    { apply Rmult_le_compat; try lra. apply Rabs_pos. }
    lra. }
  assert (B1 : Rabs (v * T) <= 5 / 2).
  { rewrite Rabs_pos_eq by (apply Rmult_le_pos; lra).
    apply Rle_trans with (5 / 2 * 1); [apply Rmult_le_compat; lra | lra]. }
  assert (L1 : bpow radix2 (-302) <= u * t).
  { apply Rle_trans with (bpow radix2 (-300) * / 4).
    - change (/ 4) with (bpow radix2 (-2)). rewrite <- bpow_plus. apply bpow_le. lia.
    - assert (X : v * / 2 * / 2 <= u * t) by (apply Rmult_le_compat; lra). lra. }
  pose proof (bpow_gt_0 radix2 (-302)) as Bq.
  assert (Z1 : bpow radix2 (-1022) <= Rabs (u * t)).
  { rewrite Rabs_pos_eq by lra. apply Rle_trans with (2 := L1). apply bpow_le. lia. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  assert (Lp : bpow radix2 (-302) <= RN64 (u * t)) by (apply rn_ge; [lia | exact L1]).
  set (p := RN64 (u * t)) in *.
  assert (A2' : Rabs (p - v * T) <= 26 * CC) by lra.
  assert (Ic : 0 < / c <= / 6) by (split; [apply Rinv_0_lt_compat; lra | apply Rinv_le_contravar; lra]).
  assert (Ic2 : / 256 <= / c) by (apply Rinv_le_contravar; lra).
  assert (A3 : Rabs (p / c - v * T / c) <= 13 / 3 * CC).
  { replace (p / c - v * T / c) with ((p - v * T) * / c) by (unfold Rdiv; ring).
    rewrite Rabs_mult, (Rabs_pos_eq (/ c)) by lra.
    apply Rle_trans with (26 * CC * / 6); [apply Rmult_le_compat; try apply Rabs_pos; lra | lra]. }
  assert (P3 : 0 <= v * T / c).
  { unfold Rdiv. apply Rmult_le_pos; [apply Rmult_le_pos |]; lra. }
  assert (Q3 : v * T / c <= 5 / 12).
  { unfold Rdiv. apply Rabs_le_inv in B1.
    apply Rle_trans with (5 / 2 * / 6); [apply Rmult_le_compat; try lra; apply Rmult_le_pos; lra | lra]. }
  assert (B3 : Rabs (v * T / c) <= 5 / 12) by (apply Rabs_le; lra).
  assert (Z3 : bpow radix2 (-1022) <= Rabs (p / c)).
  { unfold Rdiv. rewrite Rabs_pos_eq by (apply Rmult_le_pos; lra).
    apply Rle_trans with (bpow radix2 (-302) * / 256).
    - change (/ 256) with (bpow radix2 (-8)). rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4.
  set (q := RN64 (p / c)) in *.
  assert (A5 : Rabs ((1 - q) - (1 - v * T / c)) <= 5 * CC).
  { replace ((1 - q) - (1 - v * T / c)) with (- (q - v * T / c)) by ring. rewrite Rabs_Ropp. lra. }
  assert (B5 : Rabs (1 - v * T / c) <= 1) by (apply Rabs_le; lra).
  assert (Z5 : bpow radix2 (-1022) <= Rabs (1 - q)).
  { apply half_ok. assert (A5i := Rabs_le_inv _ _ A5). lra. }
  pose proof (rnd_abs _ _ _ _ Z5 A5 B5) as A6. lra.
Qed.

Ltac level c Hv0 Hv1 Hu V W V' W' :=
  pose proof (lv_step c _ _ _ _ ltac:(lra) Hv0 Hv1 Hu W V) as V';
  match type of V' with
  | Rabs (_ - ?T) <= _ => assert (W' : 7 / 12 <= T <= 1) by (apply lvx_range; lra)
  end.

(* The polynomial stage: within 8c = 2^-50 of the exact polynomial, absolutely. *)
Lemma poly_total (v u : R) : bpow radix2 (-300) <= v -> v <= 5 / 2 -> Rabs (u - v) <= CC * v ->
  Rabs (sin32_poly u - Pex v) <= 8 * CC.
Proof.
  intros Hv0 Hv1 Hu. pose proof (bpow_gt_0 radix2 (-300)) as Bp.
  rewrite poly_fold. unfold Pex.
  pose proof (lv_first v u Hv0 Hv1 Hu) as V1.
  assert (W1 : 7 / 12 <= 1 - v / 210 <= 1) by lra.
  level 156 Hv0 Hv1 Hu V1 W1 V2 W2.
  level 110 Hv0 Hv1 Hu V2 W2 V3 W3.
  level 72 Hv0 Hv1 Hu V3 W3 V4 W4.
  level 42 Hv0 Hv1 Hu V4 W4 V5 W5.
  level 20 Hv0 Hv1 Hu V5 W5 V6 W6.
  exact (lv_step 6 _ _ _ _ ltac:(lra) Hv0 Hv1 Hu W6 V6).
Qed.

(* The value before narrow, for a nonzero x: within 2^-27 of sin x, relatively. *)
Lemma sin32_core (x : R) : format32 x -> x <> 0 -> Rabs x <= SMAX ->
  Rabs (RN64 (x * sin32_poly (sin32_sq x)) - sin x) <= bpow radix2 (-27) * Rabs (sin x).
Proof.
  intros Fx Nx Hx. pose proof CC_range as Hcc.
  assert (Ax : bpow radix2 (-149) <= Rabs x)
    by (apply f32_pos_ge; [apply generic_format_abs; exact Fx | apply Rabs_pos_lt; exact Nx]).
  pose proof (bpow_gt_0 radix2 (-149)) as B149. pose proof (bpow_gt_0 radix2 (-300)) as B300.
  assert (Ea : x * x = Rabs x * Rabs x).
  { rewrite <- Rabs_mult. symmetry. apply Rabs_pos_eq. apply Rle_0_sqr. }
  assert (V1 : x * x <= 5 / 2).
  { rewrite Ea. apply Rle_trans with (SMAX * SMAX).
    - apply Rmult_le_compat; try apply Rabs_pos; exact Hx.
    - unfold SMAX. lra. }
  assert (V0 : bpow radix2 (-300) <= x * x).
  { rewrite Ea. apply Rle_trans with (bpow radix2 (-149) * bpow radix2 (-149)).
    - rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  assert (Zu : bpow radix2 (-1022) <= Rabs (x * x)).
  { rewrite Rabs_pos_eq by lra. apply Rle_trans with (2 := V0). apply bpow_le. lia. }
  assert (Hu : Rabs (sin32_sq x - x * x) <= CC * (x * x)).
  { unfold sin32_sq. eapply Rle_trans; [apply rn64_rel; exact Zu |].
    rewrite Rabs_pos_eq by lra. unfold CC. apply Rle_refl. }
  pose proof (poly_total (x * x) (sin32_sq x) V0 V1 Hu) as Hp.
  assert (W : 7 / 12 <= Pex (x * x) <= 1) by (apply Pex_range; lra).
  destruct (sin_trunc x V1) as [Tr Lo].
  set (t := sin32_poly (sin32_sq x)) in *. set (T := Pex (x * x)) in *.
  assert (Hp' := Rabs_le_inv _ _ Hp).
  pose proof (Rabs_pos x) as Px.
  assert (A1 : Rabs (x * t - x * T) <= Rabs x * (8 * CC)).
  { replace (x * t - x * T) with (x * (t - T)) by ring. rewrite Rabs_mult.
    apply Rmult_le_compat_l; [exact Px | exact Hp]. }
  assert (B1 : Rabs (x * T) <= Rabs x).
  { rewrite Rabs_mult, (Rabs_pos_eq T) by lra.
    apply Rle_trans with (Rabs x * 1); [apply Rmult_le_compat_l; lra | lra]. }
  assert (Z1 : bpow radix2 (-1022) <= Rabs (x * t)).
  { rewrite Rabs_mult, (Rabs_pos_eq t) by lra.
    apply Rle_trans with (bpow radix2 (-149) * / 2).
    - change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  replace (RN64 (x * t) - sin x) with ((RN64 (x * t) - x * T) + (x * T - sin x)) by ring.
  eapply Rle_trans; [apply Rabs_triang |].
  change (bpow radix2 (-27)) with (/ 134217728).
  unfold CC in A2. lra.
Qed.

Theorem sin32_faithful : SIN32.
Proof.
  unfold SIN32, g_sin32. intros x Fx Hx.
  destruct (Req_dec x 0) as [Z | N].
  - subst x. rewrite Rmult_0_l, (round_0 radix2 fexp64 ZnearestE), sin_0.
    rewrite (T32_proof 0 (generic_format_0 radix2 fexp64)).
    apply (F32_rel 0 0). rewrite Rminus_0_r, Rabs_R0, Rmult_0_r. apply Rle_refl.
  - set (y := RN64 (x * sin32_poly (sin32_sq x))).
    assert (Fy : format64 y) by (unfold y; apply generic_format_round; typeclasses eauto).
    rewrite (T32_proof y Fy). apply (F32_rel (sin x) y). exact (sin32_core x Fx N Hx).
Qed.

Theorem sin32_finite : SIN32_FINITE.
Proof.
  unfold SIN32_FINITE. intros x Fx Hx.
  apply (faithful_finite (sin x)); [| apply sin32_faithful; assumption].
  pose proof (SIN_bound x) as S.
  apply Rle_trans with 1; [apply Rabs_le; lra |].
  apply Rle_trans with (bpow radix2 127); [apply (bpow_le radix2 0 127); lia | exact fmax_ge].
Qed.

Theorem sin32_all : SIN32_ALL.
Proof. split; [exact sin32_faithful | exact sin32_finite]. Qed.
