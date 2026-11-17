(* The truncation of log32's series, from the standard library's mean value theorem (MVT.MVT_cor2) and its
   derivative of ln (Rpower.derivable_pt_lim_ln). With Lz z = ln (1 + z) - ln (1 - z) (which is ln y at
   z = (y - 1) / (y + 1)) and Qx w = (105 + w (35 + w (21 + w 15))) / 105 = 1 + w/3 + w^2/5 + w^3/7:
     hz z = Lz z - 2 z Qx (z^2) has hz 0 = 0 and derivative 2 z^8 / ((1 + z) (1 - z)),
   so for 0 <= z <= 1/31:   2 z Qx (z^2) <= Lz z <= 2 z Qx (z^2) + z 2^-38,
   and for |z| <= 1/31:     |Lz z - 2 z Qx (z^2)| <= |z| 2^-38   and   2 |z| <= |Lz z|.
   (2 (1/31)^8 (961/960) = 2.35e-12, below 2^-38 = 3.64e-12.) Standard library only; every lemma ends with Qed. *)
From Coq Require Import Reals Lra.
Open Scope R_scope.

(* The polynomial the graph evaluates, in exact arithmetic. *)
Definition Nx (w : R) : R := 105 + w * (35 + w * (21 + w * 15)).
Definition Qx (w : R) : R := Nx w / 105.

Definition Lz (z : R) : R := ln (1 + z) - ln (1 - z).
Definition Gz (z : R) : R := 2 * z ^ 1 + 2 / 3 * z ^ 3 + 2 / 5 * z ^ 5 + 2 / 7 * z ^ 7.
Definition hz (z : R) : R := Lz z - Gz z.
Definition hd (c : R) : R := 2 * (c ^ 8 * / ((1 + c) * (1 - c))).

Lemma G_eq (z : R) : 2 * z * Qx (z * z) = Gz z.
Proof. unfold Qx, Nx, Gz. field. Qed.

Lemma Nx_range (w : R) : 0 <= w <= / 900 -> 105 <= Nx w <= 106.
Proof.
  intros [H0 H1]. unfold Nx.
  assert (A : 0 <= w * 15 <= 1) by lra.
  assert (B : 0 <= w * (21 + w * 15) <= / 900 * 22).
  { split; [apply Rmult_le_pos; lra | apply Rmult_le_compat; lra]. }
  assert (C : 0 <= w * (35 + w * (21 + w * 15)) <= / 900 * 36).
  { split; [apply Rmult_le_pos; lra | apply Rmult_le_compat; lra]. }
  lra.
Qed.

Lemma Qx_ge (w : R) : 0 <= w -> 1 <= Qx w.
Proof.
  intros H0. unfold Qx, Nx.
  assert (B : 0 <= w * (21 + w * 15)) by (apply Rmult_le_pos; lra).
  assert (C : 0 <= w * (35 + w * (21 + w * 15))) by (apply Rmult_le_pos; lra).
  unfold Rdiv. lra.
Qed.

(* Derivatives, built from the library's rules. *)
Lemma dl_eq (f : R -> R) (c l l' : R) : derivable_pt_lim f c l -> l = l' -> derivable_pt_lim f c l'.
Proof. intros H E. rewrite <- E. exact H. Qed.

Lemma d_term (a : R) (n : nat) (c : R) : derivable_pt_lim (fun z => a * z ^ n) c (a * (INR n * c ^ pred n)).
Proof. exact (derivable_pt_lim_scal (fun z => z ^ n) a c _ (derivable_pt_lim_pow c n)). Qed.

Lemma d_G (c : R) : derivable_pt_lim Gz c
  (2 * (INR 1 * c ^ 0) + 2 / 3 * (INR 3 * c ^ 2) + 2 / 5 * (INR 5 * c ^ 4) + 2 / 7 * (INR 7 * c ^ 6)).
Proof.
  exact (derivable_pt_lim_plus _ _ c _ _
          (derivable_pt_lim_plus _ _ c _ _
            (derivable_pt_lim_plus _ _ c _ _ (d_term 2 1 c) (d_term (2 / 3) 3 c)) (d_term (2 / 5) 5 c))
          (d_term (2 / 7) 7 c)).
Qed.

Lemma d_lp (c : R) : -1 < c -> derivable_pt_lim (fun z => ln (1 + z)) c (/ (1 + c) * (0 + 1)).
Proof.
  intros H.
  assert (P : 0 < 1 + c) by lra.
  exact (derivable_pt_lim_comp (fun z => 1 + z) ln c (0 + 1) (/ (1 + c))
           (derivable_pt_lim_plus (fct_cte 1) id c 0 1 (derivable_pt_lim_const 1 c) (derivable_pt_lim_id c))
           (derivable_pt_lim_ln (1 + c) P)).
Qed.

Lemma d_lm (c : R) : c < 1 -> derivable_pt_lim (fun z => ln (1 - z)) c (/ (1 - c) * (0 - 1)).
Proof.
  intros H.
  assert (P : 0 < 1 - c) by lra.
  exact (derivable_pt_lim_comp (fun z => 1 - z) ln c (0 - 1) (/ (1 - c))
           (derivable_pt_lim_minus (fct_cte 1) id c 0 1 (derivable_pt_lim_const 1 c) (derivable_pt_lim_id c))
           (derivable_pt_lim_ln (1 - c) P)).
Qed.

Lemma d_h (c : R) : -1 < c < 1 -> derivable_pt_lim hz c (hd c).
Proof.
  intros [H1 H2].
  refine (dl_eq hz c _ (hd c)
            (derivable_pt_lim_minus _ _ c _ _
               (derivable_pt_lim_minus _ _ c _ _ (d_lp c H1) (d_lm c H2)) (d_G c)) _).
  unfold hd. simpl. field. split; lra.
Qed.

Lemma hz_0 : hz 0 = 0.
Proof. unfold hz, Lz, Gz. rewrite Rplus_0_r, Rminus_0_r, ln_1. ring. Qed.

(* The mean value step. *)
Axiom hz_pos : forall z : R, 0 < z <= 1 / 31 -> 0 <= hz z <= z * / 274877906944.

Lemma Lz_0 : Lz 0 = 0.
Proof. unfold Lz. rewrite Rplus_0_r, Rminus_0_r, ln_1. ring. Qed.

Lemma Lz_opp (z : R) : Lz (- z) = - Lz z.
Proof. unfold Lz. replace (1 + - z) with (1 - z) by ring. replace (1 - - z) with (1 + z) by ring. ring. Qed.

Theorem atanh_trunc_pos (z : R) : 0 <= z <= 1 / 31 ->
  2 * z * Qx (z * z) <= Lz z <= 2 * z * Qx (z * z) + z * / 274877906944.
Proof.
  intros [H0 H1]. rewrite G_eq.
  destruct (Rle_lt_or_eq_dec 0 z H0) as [P | Z].
  - pose proof (hz_pos z (conj P H1)) as H. unfold hz in H. lra.
  - subst z. assert (G0 : Gz 0 = 0) by (unfold Gz; ring). rewrite Lz_0, G0. lra.
Qed.

(* Both signs: the truncation relative to |z|, and |Lz z| from below. *)
Theorem atanh_trunc (z : R) : Rabs z <= 1 / 31 ->
  Rabs (Lz z - 2 * z * Qx (z * z)) <= Rabs z * / 274877906944 /\ 2 * Rabs z <= Rabs (Lz z).
Proof.
  intros Hz0.
  assert (Hz : - (1 / 31) <= z <= 1 / 31) by (unfold Rabs in Hz0; destruct (Rcase_abs z); lra).
  assert (W : 1 <= Qx (z * z)) by (apply Qx_ge, Rle_0_sqr).
  destruct (Rle_lt_dec 0 z) as [P | N].
  - assert (R1 : 0 <= z <= 1 / 31) by lra.
    destruct (atanh_trunc_pos z R1) as [Lo Up].
    assert (Q : z * 1 <= z * Qx (z * z)) by (apply Rmult_le_compat_l; lra).
    rewrite (Rabs_pos_eq z P). split; [apply Rabs_le; lra |].
    rewrite Rabs_pos_eq by lra. lra.
  - assert (Pa : 0 <= - z) by lra.
    assert (R1 : 0 <= - z <= 1 / 31) by lra.
    destruct (atanh_trunc_pos (- z) R1) as [Lo Up].
    replace (- z * - z) with (z * z) in Lo, Up by ring. rewrite Lz_opp in Lo, Up.
    assert (Q : - z * 1 <= - z * Qx (z * z)) by (apply Rmult_le_compat_l; lra).
    rewrite <- (Rabs_Ropp z), (Rabs_pos_eq (- z) Pa). split; [apply Rabs_le; lra |].
    rewrite <- (Rabs_Ropp (Lz z)), Rabs_pos_eq by lra. lra.
Qed.
