(* Proof of LOG32_ALL (statement in LOG32_Statement.v). Flocq and the standard library only; every lemma ends with Qed.
   The graph is narrow(v), v = RN64(k p), p = log32_p(z), z = log32_z(y); y = x (near) or twelve rounded square
   roots of x (far). With c = 2^-53 (CC), z0 = (y - 1)/(y + 1) and p0 = z0 Qx(z0^2):
     core:  for 15/16 <= y <= 17/16 with |y - 1| >= 2^-53:  z is within 8c of z0 and p within 32c of p0, relatively
            (z_stage, p_stage; the polynomial is walked level by level with an absolute bound, hstep);
            truncation (Trunc.v): |ln y - 2 p0| <= |z0| 2^-38 and 2 |z0| <= |ln y|;
            together |v - (k/2) ln y| <= 2^-38 |(k/2) ln y|.
     near:  y = x, k = 2; x = 1 is taken apart (every value is 0).
     far:   each rounded square root halves ln and moves it by at most 2c (rt_step), so |ln y - ln x / 4096| <= 4c;
            -149 <= ln x < 128 puts y inside [15/16, 17/16]; |ln x| >= 1/17 turns 4096 * 4c into a relative
            error; k = 8192.
   T32 turns narrow into RN32 and lemma F32 turns 2^-27 into faithfulness. LOG32_FINITE follows from LOG32,
   |ln x| <= 149 and p32r's faithful_finite. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core Relative.
From MKF.f32 Require Import F32_Statement F32.
From MKF.p32 Require Import Graphs P32_Statement T32 Funcs.
From MKF.p32r Require Import P32R_Statement Range.
From MKF.log32 Require Import Graph LOG32_Statement Trunc.
Open Scope R_scope.

#[local] Instance e24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).
#[local] Instance e53 : Prec_gt_0 53 := ltac:(unfold Prec_gt_0; lia).

Definition CC : R := / 2 * / 4503599627370496.
Lemma CC_range : 0 <= CC <= / 1024. Proof. unfold CC. lra. Qed.

(* ---- rounding, absolutely and relatively ---- *)

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

Lemma rn_ge (e : Z) (z : R) : (-1074 <= e)%Z -> bpow radix2 e <= z -> bpow radix2 e <= RN64 z.
Proof.
  intros He Hz. apply round_ge_generic; [typeclasses eauto | typeclasses eauto | | exact Hz].
  apply generic_format_FLT_bpow; [typeclasses eauto | exact He].
Qed.

Lemma rel_lo (a A E : R) : Rabs (a - A) <= E * Rabs A -> E <= / 2 -> / 2 * Rabs A <= Rabs a.
Proof.
  intros H HE. pose proof (Rabs_pos A) as PA.
  pose proof (Rabs_triang_inv A a) as T. rewrite (Rabs_minus_sym A a) in T.
  assert (X : E * Rabs A <= / 2 * Rabs A) by (apply Rmult_le_compat_r; lra). lra.
Qed.

Lemma rel_hi (a A E : R) : Rabs (a - A) <= E * Rabs A -> Rabs a <= Rabs A + E * Rabs A.
Proof.
  intros H. replace a with (A + (a - A)) at 1 by ring.
  eapply Rle_trans; [apply Rabs_triang |]. lra.
Qed.

Lemma rel_hi2 (a A E : R) : Rabs (a - A) <= E * Rabs A -> E <= 1 -> Rabs a <= 2 * Rabs A.
Proof.
  intros H HE. pose proof (rel_hi _ _ _ H) as Hi. pose proof (Rabs_pos A) as PA.
  assert (X : E * Rabs A <= 1 * Rabs A) by (apply Rmult_le_compat_r; lra). lra.
Qed.

(* A value within E of w relatively, rounded: within E + 2c. *)
Lemma rel_rnd (z w E E' : R) : bpow radix2 (-1022) <= Rabs z -> Rabs (z - w) <= E * Rabs w ->
  0 <= E <= 1 -> E + 2 * CC <= E' -> Rabs (RN64 z - w) <= E' * Rabs w.
Proof.
  intros Hz H HE HE'. pose proof (rn64_rel z Hz) as R. pose proof (Rabs_pos w) as Pw.
  pose proof (rel_hi2 _ _ _ H ltac:(lra)) as Hi.
  replace (RN64 z - w) with ((RN64 z - z) + (z - w)) by ring.
  eapply Rle_trans; [apply Rabs_triang |].
  assert (X : (E + 2 * CC) * Rabs w <= E' * Rabs w) by (apply Rmult_le_compat_r; lra).
  unfold CC in X. lra.
Qed.

Lemma rel_mul (a A b B Ea Eb E' : R) : Rabs (a - A) <= Ea * Rabs A -> Rabs (b - B) <= Eb * Rabs B ->
  0 <= Ea <= 1 -> 0 <= Eb -> Ea + 2 * Eb <= E' -> Rabs (a * b - A * B) <= E' * Rabs (A * B).
Proof.
  intros Ha Hb HEa HEb HE'. pose proof (Rabs_pos A) as PA. pose proof (Rabs_pos B) as PB.
  pose proof (rel_hi2 _ _ _ Ha ltac:(lra)) as Hi.
  replace (a * b - A * B) with ((a - A) * B + a * (b - B)) by ring.
  eapply Rle_trans; [apply Rabs_triang |]. rewrite !Rabs_mult.
  assert (PAB : 0 <= Rabs A * Rabs B) by (apply Rmult_le_pos; lra).
  assert (X1 : Rabs (a - A) * Rabs B <= Ea * (Rabs A * Rabs B)).
  { rewrite <- Rmult_assoc. apply Rmult_le_compat_r; lra. }
  assert (X2 : Rabs a * Rabs (b - B) <= 2 * Rabs A * (Eb * Rabs B)).
  { apply Rmult_le_compat; try apply Rabs_pos; lra. }
  assert (X2' : 2 * Rabs A * (Eb * Rabs B) = 2 * Eb * (Rabs A * Rabs B)) by ring.
  assert (X3 : (Ea + 2 * Eb) * (Rabs A * Rabs B) <= E' * (Rabs A * Rabs B)) by (apply Rmult_le_compat_r; lra).
  set (P := Rabs A * Rabs B) in *. lra.
Qed.

Lemma rel_div (a A b B Ea Eb E' : R) : Rabs (a - A) <= Ea * Rabs A -> Rabs (b - B) <= Eb * B ->
  0 <= Ea -> 0 <= Eb <= / 2 -> 0 < B -> 2 * (Ea + Eb) <= E' -> Rabs (a / b - A / B) <= E' * Rabs (A / B).
Proof.
  intros Ha Hb HEa HEb HB HE'. pose proof (Rabs_pos A) as PA.
  assert (Hb' := Rabs_le_inv _ _ Hb).
  assert (EbB : Eb * B <= / 2 * B) by (apply Rmult_le_compat_r; lra).
  assert (Pb : B / 2 <= b) by lra. assert (Pb0 : 0 < b) by lra.
  assert (Ib : 0 < / b <= 2 * / B).
  { split; [apply Rinv_0_lt_compat; exact Pb0 |].
    replace (2 * / B) with (/ (B / 2)) by (field; lra). apply Rinv_le_contravar; lra. }
  assert (IB : 0 < / B) by (apply Rinv_0_lt_compat; exact HB).
  assert (Nm : Rabs ((a - A) * B - A * (b - B)) <= (Ea + Eb) * (Rabs A * B)).
  { replace ((a - A) * B - A * (b - B)) with ((a - A) * B + - (A * (b - B))) by ring.
    eapply Rle_trans; [apply Rabs_triang |].
    rewrite Rabs_Ropp, !Rabs_mult, (Rabs_pos_eq B) by lra.
    assert (X1 : Rabs (a - A) * B <= Ea * Rabs A * B) by (apply Rmult_le_compat_r; lra).
    assert (X2 : Rabs A * Rabs (b - B) <= Rabs A * (Eb * B)) by (apply Rmult_le_compat_l; lra).
    assert (X1' : Ea * Rabs A * B = Ea * (Rabs A * B)) by ring.
    assert (X2' : Rabs A * (Eb * B) = Eb * (Rabs A * B)) by ring.
    set (P := Rabs A * B) in *. lra. }
  replace (a / b - A / B) with (((a - A) * B - A * (b - B)) * (/ b * / B)) by (field; lra).
  unfold Rdiv. rewrite !Rabs_mult, (Rabs_pos_eq (/ b)), (Rabs_pos_eq (/ B)) by lra.
  set (U := Rabs ((a - A) * B - A * (b - B))) in *.
  assert (PU : 0 <= U) by apply Rabs_pos.
  assert (PP : 0 <= Rabs A * / B) by (apply Rmult_le_pos; lra).
  apply Rle_trans with ((Ea + Eb) * (Rabs A * B) * (2 * / B * / B)).
  - apply Rmult_le_compat; [exact PU | apply Rmult_le_pos; lra | exact Nm |].
    apply Rmult_le_compat_r; lra.
  - replace ((Ea + Eb) * (Rabs A * B) * (2 * / B * / B)) with (2 * (Ea + Eb) * (Rabs A * / B)) by (field; lra).
    apply Rmult_le_compat_r; lra.
Qed.

(* ---- a number of the format near 1, other than 1, is at least 2^-53 away from it ---- *)

Lemma cexp_half (emin prec : Z) (y : R) : (prec <= 53)%Z -> / 2 <= y ->
  (-53 <= cexp radix2 (FLT_exp emin prec) y)%Z.
Proof.
  intros Hp Hy. unfold cexp, FLT_exp.
  assert (M : (0 <= mag radix2 y)%Z).
  { apply mag_ge_bpow. rewrite Rabs_pos_eq by lra. exact Hy. }
  lia.
Qed.

Lemma near1_gap (fexp : Z -> Z) (y : R) : generic_format radix2 fexp y -> (-53 <= cexp radix2 fexp y)%Z ->
  y <> 1 -> bpow radix2 (-53) <= Rabs (y - 1).
Proof.
  intros Fy He Ny.
  set (e := cexp radix2 fexp y) in *. set (m := Ztrunc (scaled_mantissa radix2 fexp y)).
  assert (Ey : y = IZR m * bpow radix2 e) by exact Fy.
  assert (E1 : IZR m * bpow radix2 (e + 53) = IZR (m * Z.pow radix2 (e + 53))).
  { rewrite mult_IZR, IZR_Zpower by lia. reflexivity. }
  assert (E2 : y - 1 = IZR (m * Z.pow radix2 (e + 53) - 9007199254740992) * bpow radix2 (-53)).
  { rewrite minus_IZR, <- E1, Rmult_minus_distr_r, Rmult_assoc, <- bpow_plus.
    replace (e + 53 + -53)%Z with e by lia. rewrite <- Ey.
    change (bpow radix2 (-53)) with (/ 9007199254740992). field. }
  set (j := (m * Z.pow radix2 (e + 53) - 9007199254740992)%Z) in *.
  assert (Nj : j <> 0%Z).
  { intros Z0. rewrite Z0 in E2. apply Ny. lra. }
  rewrite E2, Rabs_mult, (Rabs_pos_eq (bpow radix2 (-53))) by apply bpow_ge_0. rewrite <- abs_IZR.
  assert (J : 1 <= IZR (Z.abs j)) by (apply (IZR_le 1); lia).
  pose proof (bpow_gt_0 radix2 (-53)) as B.
  replace (bpow radix2 (-53)) with (1 * bpow radix2 (-53)) at 1 by ring. apply Rmult_le_compat_r; lra.
Qed.

(* ---- the stage z = (y - 1) / (y + 1) ---- *)

Lemma z_stage (y : R) : 15 / 16 <= y <= 17 / 16 -> bpow radix2 (-53) <= Rabs (y - 1) ->
  Rabs (log32_z y - (y - 1) / (y + 1)) <= 8 * CC * Rabs ((y - 1) / (y + 1)) /\
  bpow radix2 (-55) <= Rabs ((y - 1) / (y + 1)) /\ Rabs ((y - 1) / (y + 1)) <= 1 / 31.
Proof.
  intros Hy Hg. set (z0 := (y - 1) / (y + 1)).
  pose proof CC_range as Hcc. pose proof (bpow_gt_0 radix2 (-53)) as B53.
  assert (Iy : 0 < / (y + 1) <= 16 / 31).
  { split; [apply Rinv_0_lt_compat; lra |].
    replace (16 / 31) with (/ (31 / 16)) by field. apply Rinv_le_contravar; lra. }
  assert (Iy2 : / 4 <= / (y + 1)) by (apply Rinv_le_contravar; lra).
  assert (Az : Rabs z0 = Rabs (y - 1) * / (y + 1)).
  { unfold z0, Rdiv. rewrite Rabs_mult, (Rabs_pos_eq (/ (y + 1))) by lra. reflexivity. }
  assert (Lo : bpow radix2 (-55) <= Rabs z0).
  { rewrite Az. apply Rle_trans with (bpow radix2 (-53) * / 4).
    - change (/ 4) with (bpow radix2 (-2)). rewrite <- bpow_plus. apply bpow_le. lia.
    - apply Rmult_le_compat; lra. }
  assert (Hi : Rabs z0 <= 1 / 31).
  { rewrite Az. assert (U : Rabs (y - 1) <= / 16) by (apply Rabs_le; lra).
    apply Rle_trans with (/ 16 * (16 / 31)); [apply Rmult_le_compat; try lra; apply Rabs_pos | lra]. }
  split; [| split; assumption].
  unfold log32_z.
  assert (Z1 : bpow radix2 (-1022) <= Rabs (y - 1)) by (apply Rle_trans with (2 := Hg); apply bpow_le; lia).
  pose proof (rn64_rel _ Z1) as R1.
  assert (Z2 : bpow radix2 (-1022) <= Rabs (y + 1)) by (apply half_ok; lra).
  pose proof (rn64_rel _ Z2) as R2. rewrite (Rabs_pos_eq (y + 1)) in R2 by lra.
  change (/ 2 * / 4503599627370496) with CC in R1, R2.
  assert (D : Rabs (RN64 (y - 1) / RN64 (y + 1) - z0) <= 4 * CC * Rabs z0).
  { unfold z0. apply (rel_div _ _ _ _ CC CC (4 * CC) R1 R2); lra. }
  pose proof (bpow_gt_0 radix2 (-55)) as B55.
  assert (Z3 : bpow radix2 (-1022) <= Rabs (RN64 (y - 1) / RN64 (y + 1))).
  { pose proof (rel_lo _ _ _ D ltac:(lra)) as L. apply Rle_trans with (2 := L).
    apply Rle_trans with (/ 2 * bpow radix2 (-55)); [| apply Rmult_le_compat_l; lra].
    change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia. }
  apply (rel_rnd _ _ (4 * CC)); [exact Z3 | exact D | lra | lra].
Qed.

(* ---- the polynomial, one level: K + w t against K + w0 T, absolutely ---- *)

Lemma hstep (K w w0 t T : R) : 21 <= K <= 105 -> bpow radix2 (-200) <= w -> 0 <= w0 <= / 900 ->
  Rabs (w - w0) <= CC -> 15 <= T <= 40 -> Rabs (t - T) <= 256 * CC ->
  Rabs (RN64 (K + RN64 (w * t)) - (K + w0 * T)) <= 256 * CC.
Proof.
  intros HK Hw Hw0 Ew HT Et. pose proof CC_range as Hcc. pose proof (bpow_gt_0 radix2 (-200)) as Bp.
  assert (CCs : CC * CC <= / 1024 * CC) by (apply Rmult_le_compat_r; lra).
  assert (Ew' := Rabs_le_inv _ _ Ew). assert (Et' := Rabs_le_inv _ _ Et).
  assert (A1 : Rabs (w * t - w0 * T) <= 42 * CC).
  { replace (w * t - w0 * T) with ((w - w0) * t + w0 * (t - T)) by ring.
    eapply Rle_trans; [apply Rabs_triang |]. rewrite !Rabs_mult, (Rabs_pos_eq w0) by lra.
    assert (X1 : Rabs (w - w0) * Rabs t <= CC * 41).
    { apply Rmult_le_compat; try apply Rabs_pos; [exact Ew | apply Rabs_le; lra]. }
    assert (X2 : w0 * Rabs (t - T) <= / 900 * (256 * CC)).
    { apply Rmult_le_compat; try lra. apply Rabs_pos. }
    lra. }
  assert (P1 : 0 <= w0 * T) by (apply Rmult_le_pos; lra).
  assert (Q1 : w0 * T <= 1).
  { apply Rle_trans with (/ 900 * 40); [apply Rmult_le_compat; lra | lra]. }
  assert (B1 : Rabs (w0 * T) <= 1) by (apply Rabs_le; lra).
  assert (Z1 : bpow radix2 (-1022) <= Rabs (w * t)).
  { rewrite Rabs_pos_eq by (apply Rmult_le_pos; lra).
    apply Rle_trans with (bpow radix2 (-200) * 1); [rewrite Rmult_1_r; apply bpow_le; lia |].
    apply Rmult_le_compat; lra. }
  pose proof (rnd_abs _ _ _ _ Z1 A1 B1) as A2.
  set (q := RN64 (w * t)) in *.
  assert (A2' : Rabs (q - w0 * T) <= 44 * CC) by lra.
  assert (A2i := Rabs_le_inv _ _ A2').
  assert (A3 : Rabs ((K + q) - (K + w0 * T)) <= 44 * CC).
  { replace ((K + q) - (K + w0 * T)) with (q - w0 * T) by ring. exact A2'. }
  assert (B3 : Rabs (K + w0 * T) <= 106) by (apply Rabs_le; lra).
  assert (Z3 : bpow radix2 (-1022) <= Rabs (K + q)) by (apply half_ok; lra).
  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4. lra.
Qed.

(* ---- the stage p = (z N(z^2)) / 105 ---- *)

Lemma p_stage (z z0 : R) : Rabs (z - z0) <= 8 * CC * Rabs z0 -> bpow radix2 (-55) <= Rabs z0 ->
  Rabs z0 <= 1 / 31 ->
  Rabs (log32_p z - z0 * Qx (z0 * z0)) <= 32 * CC * Rabs (z0 * Qx (z0 * z0)) /\
  bpow radix2 (-55) <= Rabs (z0 * Qx (z0 * z0)).
Proof.
  intros Hz Lo Hi. unfold log32_p.
  pose proof CC_range as Hcc. pose proof (bpow_gt_0 radix2 (-55)) as B55. pose proof (Rabs_pos z0) as Pz0.
  set (w0 := z0 * z0).
  assert (Ew0 : w0 = Rabs z0 * Rabs z0).
  { unfold w0. rewrite <- Rabs_mult. symmetry. apply Rabs_pos_eq. apply Rle_0_sqr. }
  assert (Hw0 : 0 <= w0 <= / 900).
  { rewrite Ew0. split; [apply Rmult_le_pos; lra |].
    apply Rle_trans with (1 / 31 * (1 / 31)); [apply Rmult_le_compat; lra | lra]. }
  assert (Lw0 : bpow radix2 (-110) <= w0).
  { rewrite Ew0. change (-110)%Z with (-55 + -55)%Z. rewrite bpow_plus. apply Rmult_le_compat; lra. }
  pose proof (bpow_gt_0 radix2 (-110)) as B110.
  (* w = RN64 (z z) *)
  assert (M1 : Rabs (z * z - w0) <= 24 * CC * Rabs w0).
  { unfold w0. apply (rel_mul z z0 z z0 (8 * CC) (8 * CC) (24 * CC) Hz Hz); lra. }
  assert (B111 : bpow radix2 (-111) <= z * z).
  { pose proof (rel_lo _ _ _ M1 ltac:(lra)) as L.
    rewrite (Rabs_pos_eq (z * z)) in L by apply Rle_0_sqr. rewrite (Rabs_pos_eq w0) in L by lra.
    apply Rle_trans with (2 := L). apply Rle_trans with (/ 2 * bpow radix2 (-110)); [| apply Rmult_le_compat_l; lra].
    change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia. }
  assert (Z1 : bpow radix2 (-1022) <= Rabs (z * z)).
  { apply Rle_trans with (bpow radix2 (-111)); [apply bpow_le; lia |].
    rewrite Rabs_pos_eq by apply Rle_0_sqr. exact B111. }
  assert (M2 : Rabs (RN64 (z * z) - w0) <= 26 * CC * Rabs w0)
    by (apply (rel_rnd _ _ (24 * CC)); [exact Z1 | exact M1 | lra | lra]).
  assert (Lw : bpow radix2 (-200) <= RN64 (z * z)).
  { apply rn_ge; [lia |]. apply Rle_trans with (2 := B111). apply bpow_le. lia. }
  set (w := RN64 (z * z)) in *.
  assert (Ew : Rabs (w - w0) <= CC).
  { apply Rle_trans with (1 := M2). rewrite (Rabs_pos_eq w0) by lra.
    apply Rle_trans with (26 * CC * / 900); [apply Rmult_le_compat_l; lra | lra]. }
  (* the three levels *)
  assert (H1 : Rabs (RN64 (21 + RN64 (w * 15)) - (21 + w0 * 15)) <= 256 * CC).
  { apply (hstep 21 w w0 15 15); [lra | exact Lw | exact Hw0 | exact Ew | lra |].
    replace (15 - 15) with 0 by ring. rewrite Rabs_R0. lra. }
  assert (H2 : Rabs (RN64 (35 + RN64 (w * RN64 (21 + RN64 (w * 15)))) - (35 + w0 * (21 + w0 * 15))) <= 256 * CC).
  { apply (hstep 35 w w0 _ (21 + w0 * 15)); [lra | exact Lw | exact Hw0 | exact Ew | lra | exact H1]. }
  assert (P2 : 0 <= w0 * (21 + w0 * 15) <= 1).
  { split; [apply Rmult_le_pos; lra |].
    apply Rle_trans with (/ 900 * 22); [apply Rmult_le_compat; lra | lra]. }
  assert (H3 : Rabs (RN64 (105 + RN64 (w * RN64 (35 + RN64 (w * RN64 (21 + RN64 (w * 15))))))
                     - (105 + w0 * (35 + w0 * (21 + w0 * 15)))) <= 256 * CC).
  { apply (hstep 105 w w0 _ (35 + w0 * (21 + w0 * 15))); [lra | exact Lw | exact Hw0 | exact Ew | lra | exact H2]. }
  change (105 + w0 * (35 + w0 * (21 + w0 * 15))) with (Nx w0) in H3.
  pose proof (Nx_range w0 Hw0) as HN.
  set (n := RN64 (105 + RN64 (w * RN64 (35 + RN64 (w * RN64 (21 + RN64 (w * 15))))))) in *.
  set (N := Nx w0) in *.
  assert (Rn : Rabs (n - N) <= 3 * CC * Rabs N).
  { rewrite (Rabs_pos_eq N) by lra. apply Rle_trans with (1 := H3).
    assert (X : CC * 105 <= CC * N) by (apply Rmult_le_compat_l; lra). lra. }
  (* z n, rounded *)
  assert (M3 : Rabs (z * n - z0 * N) <= 16 * CC * Rabs (z0 * N)).
  { apply (rel_mul z z0 n N (8 * CC) (3 * CC) (16 * CC) Hz Rn); lra. }
  assert (LzN : bpow radix2 (-55) <= Rabs (z0 * N)).
  { rewrite Rabs_mult, (Rabs_pos_eq N) by lra.
    apply Rle_trans with (bpow radix2 (-55) * 1); [lra | apply Rmult_le_compat; lra]. }
  assert (Z4 : bpow radix2 (-1022) <= Rabs (z * n)).
  { pose proof (rel_lo _ _ _ M3 ltac:(lra)) as L. apply Rle_trans with (2 := L).
    apply Rle_trans with (/ 2 * bpow radix2 (-55)); [| apply Rmult_le_compat_l; lra].
    change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia. }
  assert (M4 : Rabs (RN64 (z * n) - z0 * N) <= 18 * CC * Rabs (z0 * N))
    by (apply (rel_rnd _ _ (16 * CC)); [exact Z4 | exact M3 | lra | lra]).
  set (m := RN64 (z * n)) in *.
  (* divided by 105, rounded *)
  assert (M5 : Rabs (m * / 105 - z0 * N * / 105) <= 18 * CC * Rabs (z0 * N * / 105)).
  { apply (rel_mul m (z0 * N) (/ 105) (/ 105) (18 * CC) 0 (18 * CC) M4); try lra.
    replace (/ 105 - / 105) with 0 by ring. rewrite Rabs_R0. lra. }
  assert (EP : z0 * N * / 105 = z0 * Qx w0) by (unfold Qx, N, Rdiv; ring).
  assert (LP : bpow radix2 (-55) <= Rabs (z0 * Qx w0)).
  { rewrite Rabs_mult. assert (Pw : 0 <= w0) by lra. pose proof (Qx_ge w0 Pw) as Q.
    rewrite (Rabs_pos_eq (Qx w0)) by lra.
    apply Rle_trans with (bpow radix2 (-55) * 1); [lra | apply Rmult_le_compat; lra]. }
  split; [| exact LP]. rewrite <- EP. rewrite <- EP in LP.
  assert (Z5 : bpow radix2 (-1022) <= Rabs (m * / 105)).
  { pose proof (rel_lo _ _ _ M5 ltac:(lra)) as L. apply Rle_trans with (2 := L).
    apply Rle_trans with (/ 2 * bpow radix2 (-55)); [| apply Rmult_le_compat_l; lra].
    change (/ 2) with (bpow radix2 (-1)). rewrite <- bpow_plus. apply bpow_le. lia. }
  apply (rel_rnd (m * / 105) _ (18 * CC)); [exact Z5 | exact M5 | lra | lra].
Qed.

(* ---- the core: 15/16 <= y <= 17/16, y not 1 ---- *)

Lemma ln_quot (a b : R) : 0 < a -> 0 < b -> ln (a / b) = ln a - ln b.
Proof.
  intros Ha Hb. assert (Ib : 0 < / b) by (apply Rinv_0_lt_compat; exact Hb).
  unfold Rdiv. rewrite ln_mult by assumption. rewrite ln_Rinv by exact Hb. ring.
Qed.

Lemma core (y k : R) : 15 / 16 <= y <= 17 / 16 -> bpow radix2 (-53) <= Rabs (y - 1) -> 2 <= k <= 8192 ->
  Rabs (RN64 (k * log32_p (log32_z y)) - k / 2 * ln y) <= / 274877906944 * Rabs (k / 2 * ln y).
Proof.
  intros Hy Hg Hk. pose proof CC_range as Hcc. pose proof (bpow_gt_0 radix2 (-55)) as B55.
  destruct (z_stage y Hy Hg) as [Hz [Lo Hi]].
  set (z0 := (y - 1) / (y + 1)) in *.
  destruct (p_stage _ z0 Hz Lo Hi) as [Hp LP].
  destruct (atanh_trunc z0 Hi) as [Tr Lb].
  assert (Hi' := Rabs_le_inv _ _ Hi).
  assert (EL : Lz z0 = ln y).
  { unfold Lz. rewrite <- ln_quot by lra. f_equal. unfold z0. field. lra. }
  rewrite EL in Tr, Lb.
  set (p0 := z0 * Qx (z0 * z0)) in *. set (p := log32_p (log32_z y)) in *. set (L := ln y) in *.
  assert (G2 : Rabs (L - 2 * p0) <= / 549755813888 * Rabs L).
  { replace (2 * p0) with (2 * z0 * Qx (z0 * z0)) by (unfold p0; ring). lra. }
  assert (K1 : Rabs (k * p - k * p0) <= 32 * CC * Rabs (k * p0)).
  { replace (k * p - k * p0) with (k * (p - p0)) by ring. rewrite !Rabs_mult, (Rabs_pos_eq k) by lra.
    assert (X : k * Rabs (p - p0) <= k * (32 * CC * Rabs p0)) by (apply Rmult_le_compat_l; lra).
    assert (X' : k * (32 * CC * Rabs p0) = 32 * CC * (k * Rabs p0)) by ring. lra. }
  assert (Z1 : bpow radix2 (-1022) <= Rabs (k * p)).
  { pose proof (rel_lo _ _ _ K1 ltac:(lra)) as Lk. apply Rle_trans with (2 := Lk).
    rewrite Rabs_mult, (Rabs_pos_eq k) by lra.
    apply Rle_trans with (/ 2 * (2 * bpow radix2 (-55))).
    - replace (/ 2 * (2 * bpow radix2 (-55))) with (bpow radix2 (-55)) by field. apply bpow_le. lia.
    - apply Rmult_le_compat_l; [lra |]. apply Rmult_le_compat; lra. }
  assert (K2 : Rabs (RN64 (k * p) - k * p0) <= 34 * CC * Rabs (k * p0))
    by (apply (rel_rnd _ _ (32 * CC)); [exact Z1 | exact K1 | lra | lra]).
  set (v := RN64 (k * p)) in *.
  assert (A2 : Rabs (2 * p0) <= 2 * Rabs L).
  { replace (2 * p0) with (L + - (L - 2 * p0)) by ring. eapply Rle_trans; [apply Rabs_triang |].
    rewrite Rabs_Ropp. pose proof (Rabs_pos L). lra. }
  assert (E1 : Rabs (k * p0) = k / 2 * Rabs (2 * p0)).
  { replace (k * p0) with (k / 2 * (2 * p0)) by field.
    rewrite Rabs_mult, (Rabs_pos_eq (k / 2)) by lra. reflexivity. }
  assert (E2 : Rabs (k / 2 * L) = k / 2 * Rabs L).
  { rewrite Rabs_mult, (Rabs_pos_eq (k / 2)) by lra. reflexivity. }
  rewrite E1 in K2. rewrite E2.
  replace (v - k / 2 * L) with ((v - k * p0) + - (k / 2 * (L - 2 * p0))) by field.
  eapply Rle_trans; [apply Rabs_triang |]. rewrite Rabs_Ropp, Rabs_mult, (Rabs_pos_eq (k / 2)) by lra.
  set (h := k / 2) in *. assert (Hh : 1 <= h <= 4096) by (unfold h; lra).
  set (a := Rabs (2 * p0)) in *. set (b := Rabs (L - 2 * p0)) in *. set (l := Rabs L) in *.
  assert (Pl : 0 <= l) by apply Rabs_pos.
  assert (X1 : h * a <= h * (2 * l)) by (apply Rmult_le_compat_l; lra).
  assert (X2 : h * b <= h * (/ 549755813888 * l)) by (apply Rmult_le_compat_l; lra).
  assert (X3 : 0 <= h * l) by (apply Rmult_le_pos; lra).
  unfold CC in K2. lra.
Qed.

(* ---- logarithm facts ---- *)

Lemma ln_mono (x y : R) : 0 < x -> x <= y -> ln x <= ln y.
Proof.
  intros Hx H. destruct (Rle_lt_or_eq_dec x y H) as [Lt | Eq].
  - left. apply ln_increasing; assumption.
  - rewrite Eq. apply Rle_refl.
Qed.

Lemma ln_le_sub (t : R) : 0 < t -> ln t <= t - 1.
Proof.
  intros H. pose proof (exp_ineq1_le (t - 1)) as E.
  replace (1 + (t - 1)) with t in E by ring.
  apply Rle_trans with (ln (exp (t - 1))); [apply ln_mono; assumption | rewrite ln_exp; lra].
Qed.

Lemma ln_ge_sub (t : R) : 0 < t -> 1 - / t <= ln t.
Proof.
  intros H. pose proof (ln_le_sub (/ t) (Rinv_0_lt_compat t H)) as E. rewrite ln_Rinv in E by exact H. lra.
Qed.

Lemma ln1p_small (e : R) : Rabs e <= CC -> Rabs (ln (1 + e)) <= 2 * CC.
Proof.
  intros He0. pose proof CC_range as Hcc. assert (He := Rabs_le_inv _ _ He0).
  assert (P : 0 < 1 + e) by lra.
  pose proof (ln_le_sub (1 + e) P) as U. pose proof (ln_ge_sub (1 + e) P) as Lw.
  assert (I : / (1 + e) <= 1 + 2 * CC).
  { apply Rmult_le_reg_r with (1 + e); [exact P |]. rewrite Rinv_l by lra.
    assert (X : (1 + 2 * CC) * (1 - CC) <= (1 + 2 * CC) * (1 + e)) by (apply Rmult_le_compat_l; lra).
    assert (Y : CC * CC <= / 1024 * CC) by (apply Rmult_le_compat_r; lra).
    lra. }
  apply Rabs_le. lra.
Qed.

Lemma ln_sqrt_half (r : R) : 0 < r -> ln (sqrt r) = ln r / 2.
Proof.
  intros H. assert (S : 0 < sqrt r) by (apply sqrt_lt_R0; exact H).
  assert (E : ln r = ln (sqrt r) + ln (sqrt r)).
  { rewrite <- ln_mult by exact S. rewrite sqrt_sqrt by lra. reflexivity. }
  lra.
Qed.

Lemma ln2_range : 0 < ln 2 < 1.
Proof.
  split.
  - rewrite <- ln_1. apply ln_increasing; lra.
  - pose proof (exp_ineq1 1 R1_neq_R0) as E.
    apply Rlt_le_trans with (ln (exp 1)); [apply ln_increasing; lra | rewrite ln_exp; lra].
Qed.

Lemma ln_bpow (e : Z) : ln (bpow radix2 e) = IZR e * ln 2.
Proof. rewrite bpow_exp, ln_exp. reflexivity. Qed.

Lemma ln_range (x : R) : format32 x -> 0 < x -> x < bpow radix2 128 -> -149 <= ln x < 128.
Proof.
  intros Fx H0 H1. pose proof ln2_range as L2.
  assert (H149 : bpow radix2 (-149) <= x) by (apply f32_pos_ge; assumption).
  split.
  - pose proof (ln_mono _ _ (bpow_gt_0 radix2 (-149)) H149) as I. rewrite ln_bpow in I. lra.
  - pose proof (ln_increasing _ _ H0 H1) as I. rewrite ln_bpow in I. lra.
Qed.

(* ---- the far path: twelve rounded square roots ---- *)

Definition rt12 (x : R) : R :=
  log32_rt (log32_rt (log32_rt (log32_rt (log32_rt (log32_rt (log32_rt (log32_rt (log32_rt (log32_rt
    (log32_rt (log32_rt x))))))))))).

Definition rt_inv (r a : R) : Prop := bpow radix2 (-150) <= r /\ Rabs (ln r - a) <= 4 * CC.

Lemma rt_step (r a : R) : rt_inv r a -> rt_inv (log32_rt r) (a / 2).
Proof.
  intros [Hr Ha]. pose proof (bpow_gt_0 radix2 (-150)) as B. unfold rt_inv, log32_rt.
  assert (S75 : bpow radix2 (-75) <= sqrt r).
  { rewrite <- (sqrt_square (bpow radix2 (-75))) by apply bpow_ge_0.
    apply sqrt_le_1_alt. rewrite <- bpow_plus. exact Hr. }
  pose proof (bpow_gt_0 radix2 (-75)) as B75.
  assert (Z : bpow radix2 (-1022) <= Rabs (sqrt r)).
  { rewrite Rabs_pos_eq by lra. apply Rle_trans with (2 := S75). apply bpow_le. lia. }
  destruct (rn64_ex _ Z) as [e [He Ee]]. change (/ 2 * / 4503599627370496) with CC in He.
  split.
  - apply Rle_trans with (bpow radix2 (-75)); [apply bpow_le; lia | apply rn_ge; [lia | exact S75]].
  - rewrite Ee. pose proof CC_range as Hcc. assert (He' := Rabs_le_inv _ _ He).
    rewrite ln_mult by lra. rewrite ln_sqrt_half by lra.
    pose proof (ln1p_small e He) as L1.
    replace (ln r / 2 + ln (1 + e) - a / 2) with ((ln r - a) * / 2 + ln (1 + e)) by field.
    eapply Rle_trans; [apply Rabs_triang |].
    assert (X : Rabs ((ln r - a) * / 2) <= 2 * CC).
    { rewrite Rabs_mult, (Rabs_pos_eq (/ 2)) by lra. lra. }
    lra.
Qed.

Lemma rt12_inv (x : R) : bpow radix2 (-150) <= x -> rt_inv (rt12 x) (ln x / 4096).
Proof.
  intros Hx. pose proof CC_range as Hcc.
  assert (S : rt_inv x (ln x)).
  { split; [exact Hx |]. replace (ln x - ln x) with 0 by ring. rewrite Rabs_R0. lra. }
  do 12 apply rt_step in S.
  replace (ln x / 4096) with (ln x / 2 / 2 / 2 / 2 / 2 / 2 / 2 / 2 / 2 / 2 / 2 / 2) by field.
  exact S.
Qed.

Lemma far_core (x : R) : format32 x -> 0 < x -> x < bpow radix2 128 -> x < 15 / 16 \/ 17 / 16 < x ->
  Rabs (RN64 (8192 * log32_p (log32_z (rt12 x))) - ln x) <= bpow radix2 (-27) * Rabs (ln x).
Proof.
  intros Fx H0 H1 Hfar. pose proof CC_range as Hcc.
  assert (H149 : bpow radix2 (-149) <= x) by (apply f32_pos_ge; assumption).
  assert (H150 : bpow radix2 (-150) <= x) by (apply Rle_trans with (2 := H149); apply bpow_le; lia).
  destruct (rt12_inv x H150) as [Ly Hy].
  assert (Fy : format64 (rt12 x)) by (unfold rt12, log32_rt; apply generic_format_round; typeclasses eauto).
  set (y := rt12 x) in *.
  destruct (ln_range x Fx H0 H1) as [Lx Ux].
  assert (Far : ln x <= - / 17 \/ / 17 <= ln x).
  { destruct Hfar as [Hl | Hh].
    - left. pose proof (ln_le_sub x H0). lra.
    - right. pose proof (ln_ge_sub x H0) as G.
      assert (I : / x < 16 / 17).
      { replace (16 / 17) with (/ (17 / 16)) by field.
        apply Rinv_lt_contravar; [apply Rmult_lt_0_compat; lra | exact Hh]. }
      lra. }
  assert (Hy' := Rabs_le_inv _ _ Hy).
  assert (Py : 0 < y) by (pose proof (bpow_gt_0 radix2 (-150)); lra).
  assert (Ry : 15 / 16 <= y <= 17 / 16).
  { split.
    - destruct (Rle_lt_dec (15 / 16) y) as [K | K]; [exact K | exfalso].
      pose proof (ln_le_sub y Py). lra.
    - destruct (Rle_lt_dec y (17 / 16)) as [K | K]; [exact K | exfalso].
      pose proof (ln_ge_sub y Py) as G.
      assert (I : / y < 16 / 17).
      { replace (16 / 17) with (/ (17 / 16)) by field.
        apply Rinv_lt_contravar; [apply Rmult_lt_0_compat; lra | exact K]. }
      lra. }
  assert (Ny : y <> 1).
  { intros E. rewrite E, ln_1 in Hy'. unfold CC in Hy'. destruct Far; lra. }
  assert (Gy : bpow radix2 (-53) <= Rabs (y - 1)).
  { apply (near1_gap fexp64); [exact Fy | apply cexp_half; [lia | lra] | exact Ny]. }
  assert (Hk : 2 <= 8192 <= 8192) by lra.
  pose proof (core y 8192 Ry Gy Hk) as C.
  replace (8192 / 2 * ln y) with (4096 * ln y) in C by field.
  set (v := RN64 (8192 * log32_p (log32_z y))) in *.
  change (bpow radix2 (-27)) with (/ 134217728).
  set (L := ln x) in *. set (M := ln y) in *.
  unfold CC in Hy'.
  destruct Far as [Ng | Ps].
  - assert (M0 : M < 0) by lra.
    rewrite (Rabs_left (4096 * M)) in C by lra. rewrite (Rabs_left L) by lra.
    apply Rabs_le_inv in C. apply Rabs_le. unfold CC in *. lra.
  - assert (M0 : 0 < M) by lra.
    rewrite (Rabs_pos_eq (4096 * M)) in C by lra. rewrite (Rabs_pos_eq L) by lra.
    apply Rabs_le_inv in C. apply Rabs_le. unfold CC in *. lra.
Qed.

(* ---- the near path ---- *)

Lemma near_core (x : R) : format32 x -> 15 / 16 <= x <= 17 / 16 -> x <> 1 ->
  Rabs (RN64 (2 * log32_p (log32_z x)) - ln x) <= bpow radix2 (-27) * Rabs (ln x).
Proof.
  intros Fx Hx N1.
  assert (Gx : bpow radix2 (-53) <= Rabs (x - 1)).
  { apply (near1_gap fexp32); [exact Fx | apply cexp_half; [lia | lra] | exact N1]. }
  assert (Hk : 2 <= 2 <= 8192) by lra.
  pose proof (core x 2 Hx Gx Hk) as C.
  replace (2 / 2 * ln x) with (ln x) in C by field.
  apply Rle_trans with (1 := C). apply Rmult_le_compat_r; [apply Rabs_pos |].
  change (bpow radix2 (-27)) with (/ 134217728). lra.
Qed.

Lemma z_one : log32_z 1 = 0.
Proof.
  unfold log32_z. replace (1 - 1) with 0 by ring. rewrite (round_0 radix2 fexp64 ZnearestE).
  unfold Rdiv. rewrite Rmult_0_l. apply (round_0 radix2 fexp64 ZnearestE).
Qed.

Lemma p_zero : log32_p 0 = 0.
Proof.
  unfold log32_p. set (n := RN64 (105 + _)).
  rewrite Rmult_0_l, (round_0 radix2 fexp64 ZnearestE). unfold Rdiv. rewrite Rmult_0_l.
  apply (round_0 radix2 fexp64 ZnearestE).
Qed.

Lemma near_true (x : R) : log32_near x = true -> 15 / 16 <= x <= 17 / 16.
Proof.
  unfold log32_near. destruct (Rle_dec (15 / 16) x) as [A | A]; [| discriminate].
  destruct (Rle_dec x (17 / 16)) as [B | B]; [| discriminate]. intros _. split; assumption.
Qed.

Lemma near_false (x : R) : log32_near x = false -> x < 15 / 16 \/ 17 / 16 < x.
Proof.
  unfold log32_near. destruct (Rle_dec (15 / 16) x) as [A | A]; [| intros _; left; lra].
  destruct (Rle_dec x (17 / 16)) as [B | B]; [discriminate | intros _; right; lra].
Qed.

(* ---- the statements ---- *)

Theorem log32_faithful : LOG32.
Proof.
  unfold LOG32, g_log32, log32_y, log32_k. intros x Fx H0 H1.
  destruct (log32_near x) eqn:Nr.
  - apply near_true in Nr. destruct (Req_dec x 1) as [E | N1].
    + subst x. rewrite z_one, p_zero, Rmult_0_r, (round_0 radix2 fexp64 ZnearestE), ln_1.
      rewrite (T32_proof 0 (generic_format_0 radix2 fexp64)).
      apply (F32_rel 0 0). rewrite Rminus_0_r, Rabs_R0, Rmult_0_r. apply Rle_refl.
    + set (v := RN64 (2 * log32_p (log32_z x))).
      assert (Fv : format64 v) by (unfold v; apply generic_format_round; typeclasses eauto).
      rewrite (T32_proof v Fv). apply (F32_rel (ln x) v). exact (near_core x Fx Nr N1).
  - apply near_false in Nr.
    change (faithful32 (ln x) (narrow (RN64 (8192 * log32_p (log32_z (rt12 x)))))).
    set (v := RN64 (8192 * log32_p (log32_z (rt12 x)))).
    assert (Fv : format64 v) by (unfold v; apply generic_format_round; typeclasses eauto).
    rewrite (T32_proof v Fv). apply (F32_rel (ln x) v). exact (far_core x Fx H0 H1 Nr).
Qed.

Theorem log32_finite : LOG32_FINITE.
Proof.
  unfold LOG32_FINITE. intros x Fx H0 H1.
  apply (faithful_finite (ln x)); [| apply log32_faithful; assumption].
  destruct (ln_range x Fx H0 H1) as [Lx Ux].
  apply Rle_trans with (bpow radix2 8); [change (bpow radix2 8) with 256; apply Rabs_le; lra |].
  apply Rle_trans with (bpow radix2 127); [apply bpow_le; lia | exact fmax_ge].
Qed.

Theorem log32_all : LOG32_ALL.
Proof. split; [exact log32_faithful | exact log32_finite]. Qed.
