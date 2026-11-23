(* Proof of SINCOS32_NONZERO (statement in SINCOS32_NONZERO_Statement.v, frozen before this proof under the owner's
   sha256 b3ea4523f9a0f752a0c203046cc84e9115f6ed4d902014aeffae7ede59fe71ee, 2026-11-18). Flocq and the standard library
   only; nothing is admitted. Author: the assistant.
   1. A binary32 x is m 2^e with e >= -149, so 2x is a whole multiple of 2^-148, and so is 2x + 1/2.
   2. For a whole N, sin (pi N 2^-148) is 0 or at least 2^-149 in magnitude: write N = 2^148 q + r with 0 <= r < 2^148;
      |sin (pi N 2^-148)| = |sin (pi r 2^-148)| (sin (q pi) = 0, |cos (q pi)| = 1); r = 0 gives 0; otherwise
      s = r 2^-148 lies in [2^-148, 1 - 2^-148], and sin (pi s) >= sin (pi 2^-148) (sin increases up to pi/2;
      sin (pi - t) = sin t) >= 2^-147 (sin t >= sin (2t) / 2 for 0 <= t <= pi/2, halving from sin (pi/2) = 1).
   3. cos (2 pi x) = sin (pi (2x + 1/2)).
   4. A faithful rounding of a value of magnitude at least 2^-149, the smallest positive binary32 number, is not 0;
      SINTURN32 and COSTURN32 (sincos32, proved there) say the results are faithful roundings. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core.
From MKF.f32 Require Import F32_Statement.
From MKF.sincos32 Require Import Graph SINCOS32_Statement.
From MKF.sincos32 Require Reduce Sincos32.
From MKF.sincos32n Require Import SINCOS32_NONZERO_Statement.
Open Scope R_scope.

#[local] Instance nz_r24 : Prec_gt_0 24 := ltac:(unfold Prec_gt_0; lia).

Lemma faithful_nz (f v : R) : bpow radix2 (-149) <= Rabs f -> faithful32 f v -> v <> 0.
Proof.
  intros Hf Hv. assert (Fb : format32 (bpow radix2 (-149))) by (apply generic_format_bpow; unfold FLT_exp; lia).
  pose proof (bpow_gt_0 radix2 (-149)) as Hp.
  destruct (Rle_or_lt 0 f) as [Hpos | Hneg].
  - rewrite Rabs_pos_eq in Hf by exact Hpos.
    assert (Hge : forall rnd, Valid_rnd rnd -> bpow radix2 (-149) <= round radix2 fexp32 rnd f).
    { intros rnd Vr. apply round_ge_generic; [typeclasses eauto | exact Vr | exact Fb | exact Hf]. }
    assert (H : bpow radix2 (-149) <= v) by (destruct Hv as [E | E]; rewrite E; apply Hge; typeclasses eauto).
    apply Rgt_not_eq. lra.
  - rewrite Rabs_left in Hf by exact Hneg.
    assert (Hle : forall rnd, Valid_rnd rnd -> round radix2 fexp32 rnd f <= - bpow radix2 (-149)).
    { intros rnd Vr. apply round_le_generic;
        [typeclasses eauto | exact Vr | apply generic_format_opp; exact Fb | lra]. }
    assert (H : v <= - bpow radix2 (-149)) by (destruct Hv as [E | E]; rewrite E; apply Hle; typeclasses eauto).
    apply Rlt_not_eq. lra.
Qed.

Lemma halves (n : nat) : bpow radix2 (- Z.of_nat n) <= sin (PI / 2 * bpow radix2 (- Z.of_nat n)).
Proof.
  induction n as [| n IH].
  - change (bpow radix2 (- Z.of_nat 0)) with 1. rewrite Rmult_1_r, sin_PI2. lra.
  - assert (E : bpow radix2 (- Z.of_nat (S n)) = bpow radix2 (- Z.of_nat n) * / 2).
    { rewrite Nat2Z.inj_succ, <- Z.add_1_r, Z.opp_add_distr, bpow_plus. reflexivity. }
    pose proof (bpow_gt_0 radix2 (- Z.of_nat n)) as Hb.
    assert (Hb1 : bpow radix2 (- Z.of_nat n) <= 1).
    { change 1 with (bpow radix2 0). apply bpow_le. lia. }
    rewrite E. set (b := bpow radix2 (- Z.of_nat n)) in *.
    set (t := PI / 2 * (b * / 2)).
    assert (Ht : PI / 2 * b = 2 * t) by (unfold t; field).
    rewrite Ht, sin_2a in IH.
    pose proof PI_RGT_0 as Hpi.
    assert (Hs : 0 <= sin t) by (apply sin_ge_0; unfold t; nra).
    pose proof (COS_bound t) as [_ Hc].
    nra.
Qed.

Lemma sin_eps : bpow radix2 (-149) <= sin (PI * bpow radix2 (-148)).
Proof.
  pose proof (halves 147) as H. change (- Z.of_nat 147)%Z with (-147)%Z in H.
  assert (E : PI / 2 * bpow radix2 (-147) = PI * bpow radix2 (-148)).
  { replace (-147)%Z with (1 + -148)%Z by lia. rewrite bpow_plus. change (bpow radix2 1) with 2. field. }
  rewrite E in H.
  assert (L : bpow radix2 (-149) <= bpow radix2 (-147)) by (apply bpow_le; lia).
  lra.
Qed.

Lemma grid_lb (N : Z) : sin (PI * (IZR N * bpow radix2 (-148))) <> 0 ->
  bpow radix2 (-149) <= Rabs (sin (PI * (IZR N * bpow radix2 (-148)))).
Proof.
  intros Hn.
  pose proof (bpow_gt_0 radix2 (-149)) as H149.
  pose proof (bpow_gt_0 radix2 (-148)) as He.
  assert (Heh : bpow radix2 (-148) <= / 2).
  { change (/ 2) with (bpow radix2 (-1)). apply bpow_le. lia. }
  pose proof sin_eps as Hse. pose proof PI_RGT_0 as Hpi.
  set (eps := bpow radix2 (-148)) in *.
  assert (HD0 : (0 < Zpower radix2 148)%Z) by (apply Zpower_gt_0; lia).
  assert (HDe : IZR (Zpower radix2 148) * eps = 1).
  { unfold eps. rewrite IZR_Zpower by lia. rewrite <- bpow_plus. reflexivity. }
  pose proof (Z_div_mod_eq_full N (Zpower radix2 148)) as EN.
  pose proof (Z.mod_pos_bound N (Zpower radix2 148) HD0) as Hr.
  set (D := Zpower radix2 148) in *.
  set (q := (N / D)%Z) in *. set (r := (N mod D)%Z) in *. clearbody q r.
  assert (Ey : IZR N * eps = IZR q + IZR r * eps).
  { rewrite EN, plus_IZR, mult_IZR, Rmult_plus_distr_r.
    replace (IZR D * IZR q * eps) with (IZR q * (IZR D * eps)) by ring. rewrite HDe. ring. }
  assert (Ea : PI * (IZR N * eps) = IZR q * PI + PI * (IZR r * eps)) by (rewrite Ey; ring).
  assert (Hs0 : sin (IZR q * PI) = 0) by (apply sin_eq_0_1; exists q; reflexivity).
  assert (Hc : Rabs (cos (IZR q * PI)) = 1).
  { pose proof (sin2_cos2 (IZR q * PI)) as H. rewrite Hs0 in H. unfold Rsqr in H.
    destruct (Rle_or_lt 0 (cos (IZR q * PI))) as [P | P].
    - rewrite Rabs_pos_eq by exact P. nra.
    - rewrite Rabs_left by exact P. nra. }
  assert (Ha : Rabs (sin (PI * (IZR N * eps))) = Rabs (sin (PI * (IZR r * eps)))).
  { rewrite Ea, sin_plus, Hs0, Rmult_0_l, Rplus_0_l, Rabs_mult, Hc. ring. }
  destruct (Z.eq_dec r 0) as [R0 | R0].
  - exfalso. apply Hn. rewrite Ea, R0, Rmult_0_l, Rmult_0_r, Rplus_0_r. exact Hs0.
  - assert (Hr1 : 1 <= IZR r) by (apply IZR_le; lia).
    assert (Hr2 : IZR r <= IZR D - 1) by (rewrite <- minus_IZR; apply IZR_le; lia).
    assert (Hs1 : eps <= IZR r * eps) by nra.
    assert (Hs2 : IZR r * eps <= 1 - eps) by nra.
    rewrite Ha. set (s := IZR r * eps) in *.
    assert (Hmono : forall u, eps <= u <= / 2 -> sin (PI * eps) <= sin (PI * u)).
    { intros u [Hu1 Hu2]. destruct (Req_dec u eps) as [Eu | Eu]; [rewrite Eu; lra |].
      left. apply sin_increasing_1; nra. }
    destruct (Rle_or_lt s (/ 2)) as [Hh | Hh].
    + pose proof (Hmono s (conj Hs1 Hh)) as Hm. rewrite Rabs_pos_eq by lra. lra.
    + assert (Es : sin (PI * s) = sin (PI * (1 - s))) by (rewrite <- sin_PI_x; f_equal; ring).
      assert (Hm : sin (PI * eps) <= sin (PI * (1 - s))) by (apply Hmono; lra).
      rewrite Es, Rabs_pos_eq by lra. lra.
Qed.

Lemma turn_grid (x : R) : format32 x -> exists N : Z, 2 * x = IZR N * bpow radix2 (-148).
Proof.
  intros F. destruct (Reduce.f32_rep x F) as (m & e & E & _ & He).
  exists (m * Zpower radix2 (e + 149))%Z.
  rewrite E, mult_IZR, (IZR_Zpower radix2 (e + 149)) by lia.
  rewrite Rmult_assoc, <- bpow_plus.
  replace (e + 149 + -148)%Z with (1 + e)%Z by ring.
  rewrite bpow_plus. change (bpow radix2 1) with 2. ring.
Qed.

Theorem sinturn32_nonzero : SINTURN32_NONZERO.
Proof.
  unfold SINTURN32_NONZERO. intros x Fx Hs.
  destruct (turn_grid x Fx) as [N EN].
  assert (E : 2 * PI * x = PI * (IZR N * bpow radix2 (-148))) by (rewrite <- EN; ring).
  apply (faithful_nz (sin (2 * PI * x))).
  - rewrite E. apply grid_lb. rewrite <- E. exact Hs.
  - exact (Sincos32.sinturn32_faithful x Fx).
Qed.

Theorem costurn32_nonzero : COSTURN32_NONZERO.
Proof.
  unfold COSTURN32_NONZERO. intros x Fx Hc.
  destruct (turn_grid x Fx) as [N EN].
  assert (E : cos (2 * PI * x) = sin (PI * (IZR (N + Zpower radix2 147) * bpow radix2 (-148)))).
  { rewrite cos_sin. f_equal. rewrite plus_IZR, (IZR_Zpower radix2 147) by lia.
    rewrite Rmult_plus_distr_r, <- bpow_plus. change (bpow radix2 (147 + -148)) with (/ 2).
    rewrite <- EN. field. }
  apply (faithful_nz (cos (2 * PI * x))).
  - rewrite E. apply grid_lb. rewrite <- E. exact Hc.
  - exact (Sincos32.costurn32_faithful x Fx).
Qed.

Theorem sincos32_nonzero : SINCOS32_NONZERO.
Proof. exact (conj sinturn32_nonzero costurn32_nonzero). Qed.
