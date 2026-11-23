(* Order32.v: proofs of the eleven parts of ORDER32 (statement in ORDER32_Statement.v, which this file does not
   change): FC_ORD_R, FC_ORD_LEB, FC_ORD_NAN, FC_TOTAL_ZERO, FC_TOTAL_NN, FC_DIFF, FC_FIX, FC_EQ_INT, FC_NEG, FC_IDEM
   and FC_MONO, in the statement's order. From Flocq, the standard library and the two closed theorems floor32_holds
   (floor32/Closed.v) and ceil32_holds (ceil32/Closed.v); every lemma ends with Qed and nothing is assumed. Author:
   the assistant (2026-11-22).

   How it goes. Every part rests on what FLOOR32 and CEIL32 already say about the two functions:
     - for a binary32 input b (finite, format32 (B2R b)), FL b is finite, its real number is IZR (Zfloor (B2R b))
       (FL_VALUE with FL_EXACT), its sign bit is b's (FL_SIGN), and its real number is again a binary32 number
       (FL_EXACT); the same for CL b with Zceil (CL_VALUE, CL_EXACT, CL_SIGN);
     - for an input that is not finite, FL b = b and CL b = b (FL_NONFINITE, CL_NONFINITE).
   Two finite binary64 values with the same real number and the same sign bit are equal (Flocq's B2R_Bsign_inj); on
   finite values Bleb and Bcompare are the order of the real numbers (Bleb_correct, Bcompare_correct); where an
   infinity or the NaN takes part they are computed on constructors. The rest is Flocq's Zfloor and Zceil:
     ORD_R, ORD_LEB  Zfloor x <= x <= Zceil x (Zfloor_lb, Zceil_ub); an infinity is its own FL and CL.
     ORD_NAN         FL and CL return the NaN; Bcompare with the NaN on either side is None (computed).
     TOTAL_ZERO      computed from the definition of fc_total_nn alone.
     TOTAL_NN        as ORD_LEB; on equal values both sign bits are b's, so the zero clause gives true.
     DIFF            Zceil x = Zfloor x when x is whole (Zfloor_IZR, Zceil_IZR), Zfloor x + 1 otherwise
                     (Zceil_floor_neq).
     FIX, EQ_INT     a whole x has Zfloor x = Zceil x = x, so FL b and b agree in value and sign; FL b = b, or
                     FL b = CL b, makes x a whole number.
     NEG             Zceil x is - Zfloor (- x) by Flocq's definition; Bopp negates the sign bit, FL and CL keep it.
     IDEM            FL b is a whole binary32 number, which FL returns with its sign; the same for CL.
     MONO            Zfloor and Zceil are monotone (Zfloor_le, Zceil_le); an infinity against a finite value is
                     computed on constructors, and Bleb is false when the NaN takes part.
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
From MKF.floor32 Require Closed.
From MKF.ceil32 Require Closed.
From MKF.order32 Require Import ORDER32_Statement.
Open Scope R_scope.

(* 1. What FLOOR32 and CEIL32 say, in the form used below. *)

Lemma fc_fl_fin (b : b64) : is_finite b = true -> format32 (B2R b) ->
  is_finite (T_floor32 b64 tieee_ops b) = true /\
  B2R (T_floor32 b64 tieee_ops b) = IZR (Zfloor (B2R b)) /\
  Bsign (T_floor32 b64 tieee_ops b) = Bsign b /\
  format32 (B2R (T_floor32 b64 tieee_ops b)).
Proof.
  intros Fb H32.
  pose proof MKF.floor32.Closed.floor32_holds as H. unfold FLOOR32 in H.
  destruct H as [HE [HV [HS _]]].
  destruct (HV b Fb H32) as [F1 V1].
  destruct (HE (B2R b) H32) as [E1 E2].
  split; [exact F1 |].
  split; [rewrite V1; exact E1 |].
  split; [exact (HS b Fb H32) |].
  rewrite V1. exact E2.
Qed.

Lemma fc_cl_fin (b : b64) : is_finite b = true -> format32 (B2R b) ->
  is_finite (T_ceil32 b64 tieee_ops b) = true /\
  B2R (T_ceil32 b64 tieee_ops b) = IZR (Zceil (B2R b)) /\
  Bsign (T_ceil32 b64 tieee_ops b) = Bsign b /\
  format32 (B2R (T_ceil32 b64 tieee_ops b)).
Proof.
  intros Fb H32.
  pose proof MKF.ceil32.Closed.ceil32_holds as H. unfold CEIL32 in H.
  destruct H as [HE [HV [HS _]]].
  destruct (HV b Fb H32) as [F1 V1].
  destruct (HE (B2R b) H32) as [E1 E2].
  split; [exact F1 |].
  split; [rewrite V1; exact E1 |].
  split; [exact (HS b Fb H32) |].
  rewrite V1. exact E2.
Qed.

Lemma fc_fl_nonfin (b : b64) : is_finite b = false -> T_floor32 b64 tieee_ops b = b.
Proof.
  intros Fb.
  pose proof MKF.floor32.Closed.floor32_holds as H. unfold FLOOR32 in H.
  destruct H as [_ [_ [_ [HN _]]]].
  exact (HN b Fb).
Qed.

Lemma fc_cl_nonfin (b : b64) : is_finite b = false -> T_ceil32 b64 tieee_ops b = b.
Proof.
  intros Fb.
  pose proof MKF.ceil32.Closed.ceil32_holds as H. unfold CEIL32 in H.
  destruct H as [_ [_ [_ [HN _]]]].
  exact (HN b Fb).
Qed.

(* 2. The inputs: the NaN, the infinities and the binary32 inputs. *)

Lemma fc_fin_not_nan (x : b64) : is_finite x = true -> is_nan x = false.
Proof. destruct x; easy. Qed.

Lemma fc_nan_is (b : b64) : is_nan b = true -> b = @B754_nan 53 1024.
Proof. destruct b; easy. Qed.

Lemma fc_fin_cases (b : b64) : is_finite b = false \/ format32 (B2R b) ->
  is_finite b = false \/ (is_finite b = true /\ format32 (B2R b)).
Proof.
  intros [H | H].
  - left. exact H.
  - destruct (is_finite b) eqn:Fb.
    + right. split; [reflexivity | exact H].
    + left. reflexivity.
Qed.

Lemma fc_input_cases (b : b64) : is_finite b = false \/ format32 (B2R b) -> is_nan b = false ->
  (is_finite b = false /\ exists s : bool, b = @B754_infinity 53 1024 s) \/
  (is_finite b = true /\ format32 (B2R b)).
Proof.
  intros H Nb. destruct (fc_fin_cases b H) as [Fb | FH].
  - left. split; [exact Fb |].
    destruct b as [s | s | | s m e B]; try discriminate Fb; try discriminate Nb.
    exists s. reflexivity.
  - right. exact FH.
Qed.

(* 3. Order. *)

Theorem FC_ORD_R_proof : FC_ORD_R.
Proof.
  intros b Fb H32.
  destruct (fc_fl_fin b Fb H32) as [_ [V1 _]].
  destruct (fc_cl_fin b Fb H32) as [_ [V2 _]].
  rewrite V1, V2.
  split; [apply Zfloor_lb | apply Zceil_ub].
Qed.

Lemma fc_bleb_inf_refl (s : bool) : Bleb (@B754_infinity 53 1024 s) (@B754_infinity 53 1024 s) = true.
Proof. destruct s; reflexivity. Qed.

Theorem FC_ORD_LEB_proof : FC_ORD_LEB.
Proof.
  intros b Hb Nb.
  destruct (fc_input_cases b Hb Nb) as [[Fb [s E]] | [Fb H32]].
  - rewrite (fc_fl_nonfin b Fb), (fc_cl_nonfin b Fb), E.
    split; [apply fc_bleb_inf_refl | split; apply fc_bleb_inf_refl].
  - destruct (fc_fl_fin b Fb H32) as [F1 [V1 _]].
    destruct (fc_cl_fin b Fb H32) as [F2 [V2 _]].
    rewrite (Bleb_correct 53 1024 _ _ F1 Fb), (Bleb_correct 53 1024 _ _ Fb F2),
      (Bleb_correct 53 1024 _ _ F1 F2), V1, V2.
    split; [| split]; apply Rle_bool_true.
    + apply Zfloor_lb.
    + apply Zceil_ub.
    + apply Rle_trans with (B2R b); [apply Zfloor_lb | apply Zceil_ub].
Qed.

Theorem FC_ORD_NAN_proof : FC_ORD_NAN.
Proof.
  intros b c Nb.
  rewrite (fc_nan_is b Nb).
  rewrite (fc_fl_nonfin (@B754_nan 53 1024) eq_refl), (fc_cl_nonfin (@B754_nan 53 1024) eq_refl).
  split.
  - destruct c as [[|] | [|] | | [|] m e B]; reflexivity.
  - destruct c as [[|] | [|] | | [|] m e B]; reflexivity.
Qed.

(* 4. totalOrder on values that are not NaN. *)

Theorem FC_TOTAL_ZERO_proof : FC_TOTAL_ZERO.
Proof.
  unfold FC_TOTAL_ZERO. split.
  - reflexivity.
  - reflexivity.
Qed.

Lemma fc_total_inf_refl (s : bool) :
  fc_total_nn (@B754_infinity 53 1024 s) (@B754_infinity 53 1024 s) = true.
Proof. destruct s; reflexivity. Qed.

Lemma fc_total_fin (x y : b64) : is_finite x = true -> is_finite y = true -> B2R x <= B2R y ->
  Bsign x = Bsign y -> fc_total_nn x y = true.
Proof.
  intros Fx Fy L S. unfold fc_total_nn. rewrite (Bcompare_correct 53 1024 x y Fx Fy).
  destruct (Rle_lt_or_eq_dec _ _ L) as [HL | HE].
  - rewrite (Rcompare_Lt _ _ HL). reflexivity.
  - rewrite (Rcompare_Eq _ _ HE), S. destruct (Bsign y); reflexivity.
Qed.

Theorem FC_TOTAL_NN_proof : FC_TOTAL_NN.
Proof.
  intros b Hb Nb.
  destruct (fc_input_cases b Hb Nb) as [[Fb [s E]] | [Fb H32]].
  - rewrite (fc_fl_nonfin b Fb), (fc_cl_nonfin b Fb), E.
    split; [apply fc_total_inf_refl | split; apply fc_total_inf_refl].
  - destruct (fc_fl_fin b Fb H32) as [F1 [V1 [S1 _]]].
    destruct (fc_cl_fin b Fb H32) as [F2 [V2 [S2 _]]].
    split; [| split].
    + apply fc_total_fin; [exact F1 | exact Fb | rewrite V1; apply Zfloor_lb | exact S1].
    + apply fc_total_fin; [exact Fb | exact F2 | rewrite V2; apply Zceil_ub | symmetry; exact S2].
    + apply fc_total_fin; [exact F1 | exact F2 | | rewrite S1, S2; reflexivity].
      rewrite V1, V2. apply Rle_trans with (B2R b); [apply Zfloor_lb | apply Zceil_ub].
Qed.

(* 5. The companions. *)

Theorem FC_DIFF_proof : FC_DIFF.
Proof.
  intros b Fb H32.
  destruct (fc_fl_fin b Fb H32) as [_ [V1 _]].
  destruct (fc_cl_fin b Fb H32) as [_ [V2 _]].
  rewrite V1, V2.
  destruct (Req_dec (IZR (Zfloor (B2R b))) (B2R b)) as [E | E].
  - left. rewrite <- E, Zceil_IZR, Zfloor_IZR. ring.
  - right. rewrite (Zceil_floor_neq _ E), plus_IZR. ring.
Qed.

Theorem FC_FIX_proof : FC_FIX.
Proof.
  intros b Fb H32.
  destruct (fc_fl_fin b Fb H32) as [F1 [V1 [S1 _]]].
  destruct (fc_cl_fin b Fb H32) as [F2 [V2 [S2 _]]].
  split; split.
  - intros [z Hz]. apply B2R_Bsign_inj; [exact F1 | exact Fb | rewrite V1, Hz, Zfloor_IZR; reflexivity | exact S1].
  - intros E. exists (Zfloor (B2R b)). rewrite <- V1, E. reflexivity.
  - intros [z Hz]. apply B2R_Bsign_inj; [exact F2 | exact Fb | rewrite V2, Hz, Zceil_IZR; reflexivity | exact S2].
  - intros E. exists (Zceil (B2R b)). rewrite <- V2, E. reflexivity.
Qed.

Theorem FC_EQ_INT_proof : FC_EQ_INT.
Proof.
  intros b Fb H32.
  destruct (FC_FIX_proof b Fb H32) as [[Hf _] [Hc _]].
  destruct (fc_fl_fin b Fb H32) as [_ [V1 _]].
  destruct (fc_cl_fin b Fb H32) as [_ [V2 _]].
  assert (Hw : T_floor32 b64 tieee_ops b = T_ceil32 b64 tieee_ops b -> exists z : Z, B2R b = IZR z).
  { intros E. exists (Zfloor (B2R b)).
    destruct (Req_dec (IZR (Zfloor (B2R b))) (B2R b)) as [E1 | E1]; [symmetry; exact E1 |].
    exfalso.
    assert (E2 : B2R (T_floor32 b64 tieee_ops b) = B2R (T_ceil32 b64 tieee_ops b)) by (rewrite E; reflexivity).
    rewrite V1, V2, (Zceil_floor_neq _ E1), plus_IZR in E2. lra. }
  split; [split |].
  - exact Hw.
  - intros Hz. rewrite (Hf Hz), (Hc Hz). reflexivity.
  - intros E. pose proof (Hw E) as Hz. split; [exact (Hf Hz) | exact (Hc Hz)].
Qed.

Theorem FC_NEG_proof : FC_NEG.
Proof.
  intros b Hb.
  destruct (fc_fin_cases b Hb) as [Fb | [Fb H32]].
  - assert (Fo : is_finite (Bopp b) = false) by (rewrite (is_finite_Bopp 53 1024 b); exact Fb).
    rewrite (fc_cl_nonfin b Fb), (fc_fl_nonfin (Bopp b) Fo), (Bopp_involutive 53 1024 b). reflexivity.
  - assert (Fo : is_finite (Bopp b) = true) by (rewrite (is_finite_Bopp 53 1024 b); exact Fb).
    assert (Ho : format32 (B2R (Bopp b))).
    { rewrite (B2R_Bopp 53 1024 b). apply generic_format_opp. exact H32. }
    destruct (fc_fl_fin (Bopp b) Fo Ho) as [F1 [V1 [S1 _]]].
    destruct (fc_cl_fin b Fb H32) as [F2 [V2 [S2 _]]].
    apply B2R_Bsign_inj.
    + exact F2.
    + rewrite (is_finite_Bopp 53 1024 _). exact F1.
    + rewrite (B2R_Bopp 53 1024 _), V1, V2, (B2R_Bopp 53 1024 b). unfold Zceil. rewrite opp_IZR. reflexivity.
    + rewrite S2, (Bsign_Bopp 53 1024 _ (fc_fin_not_nan _ F1)), S1, (Bsign_Bopp 53 1024 b (fc_fin_not_nan b Fb)).
      destruct (Bsign b); reflexivity.
Qed.

Theorem FC_IDEM_proof : FC_IDEM.
Proof.
  intros b Hb.
  destruct (fc_fin_cases b Hb) as [Fb | [Fb H32]].
  - rewrite !(fc_fl_nonfin b Fb), !(fc_cl_nonfin b Fb). split; reflexivity.
  - destruct (fc_fl_fin b Fb H32) as [F1 [V1 [S1 G1]]].
    destruct (fc_cl_fin b Fb H32) as [F2 [V2 [S2 G2]]].
    destruct (fc_fl_fin _ F1 G1) as [F3 [V3 [S3 _]]].
    destruct (fc_cl_fin _ F2 G2) as [F4 [V4 [S4 _]]].
    split.
    + apply B2R_Bsign_inj; [exact F3 | exact F1 | rewrite V3, V1, Zfloor_IZR; reflexivity | exact S3].
    + apply B2R_Bsign_inj; [exact F4 | exact F2 | rewrite V4, V2, Zceil_IZR; reflexivity | exact S4].
Qed.

(* 6. Monotonicity. *)

Lemma fc_bleb_nan_l (y : b64) : Bleb (@B754_nan 53 1024) y = false.
Proof. destruct y as [[|] | [|] | | [|] m e B]; reflexivity. Qed.

Lemma fc_bleb_nan_r (x : b64) : Bleb x (@B754_nan 53 1024) = false.
Proof. destruct x as [[|] | [|] | | [|] m e B]; reflexivity. Qed.

Lemma fc_bleb_not_nan (x y : b64) : Bleb x y = true -> is_nan x = false /\ is_nan y = false.
Proof.
  intros H. split.
  - destruct (is_nan x) eqn:N; [| reflexivity].
    rewrite (fc_nan_is x N), fc_bleb_nan_l in H. discriminate H.
  - destruct (is_nan y) eqn:N; [| reflexivity].
    rewrite (fc_nan_is y N), fc_bleb_nan_r in H. discriminate H.
Qed.

Lemma fc_bleb_inf_fin (s : bool) (y : b64) : is_finite y = true -> Bleb (@B754_infinity 53 1024 s) y = s.
Proof. intros F. destruct y as [[|] | [|] | | [|] m e B]; try discriminate F; destruct s; reflexivity. Qed.

Lemma fc_bleb_fin_inf (x : b64) (s : bool) : is_finite x = true -> Bleb x (@B754_infinity 53 1024 s) = negb s.
Proof. intros F. destruct x as [[|] | [|] | | [|] m e B]; try discriminate F; destruct s; reflexivity. Qed.

Theorem FC_MONO_proof : FC_MONO.
Proof.
  intros b1 b2 H1 H2 Hle.
  destruct (fc_bleb_not_nan b1 b2 Hle) as [N1 N2].
  destruct (fc_input_cases b1 H1 N1) as [[F1 [s1 E1]] | [F1 G1]];
    destruct (fc_input_cases b2 H2 N2) as [[F2 [s2 E2]] | [F2 G2]].
  - (* two infinities *)
    rewrite (fc_fl_nonfin b1 F1), (fc_fl_nonfin b2 F2), (fc_cl_nonfin b1 F1), (fc_cl_nonfin b2 F2).
    split; exact Hle.
  - (* an infinity, then a binary32 input *)
    subst b1.
    destruct (fc_fl_fin b2 F2 G2) as [Ff2 _]. destruct (fc_cl_fin b2 F2 G2) as [Fc2 _].
    rewrite (fc_bleb_inf_fin s1 b2 F2) in Hle.
    rewrite (fc_fl_nonfin _ F1), (fc_cl_nonfin _ F1), (fc_bleb_inf_fin s1 _ Ff2), (fc_bleb_inf_fin s1 _ Fc2).
    split; exact Hle.
  - (* a binary32 input, then an infinity *)
    subst b2.
    destruct (fc_fl_fin b1 F1 G1) as [Ff1 _]. destruct (fc_cl_fin b1 F1 G1) as [Fc1 _].
    rewrite (fc_bleb_fin_inf b1 s2 F1) in Hle.
    rewrite (fc_fl_nonfin _ F2), (fc_cl_nonfin _ F2), (fc_bleb_fin_inf _ s2 Ff1), (fc_bleb_fin_inf _ s2 Fc1).
    split; exact Hle.
  - (* two binary32 inputs *)
    destruct (fc_fl_fin b1 F1 G1) as [Ff1 [Vf1 _]]. destruct (fc_fl_fin b2 F2 G2) as [Ff2 [Vf2 _]].
    destruct (fc_cl_fin b1 F1 G1) as [Fc1 [Vc1 _]]. destruct (fc_cl_fin b2 F2 G2) as [Fc2 [Vc2 _]].
    assert (L : B2R b1 <= B2R b2).
    { apply Rnot_lt_le. intros HL.
      rewrite (Bleb_correct 53 1024 b1 b2 F1 F2), (Rle_bool_false _ _ HL) in Hle. discriminate Hle. }
    rewrite (Bleb_correct 53 1024 _ _ Ff1 Ff2), (Bleb_correct 53 1024 _ _ Fc1 Fc2), Vf1, Vf2, Vc1, Vc2.
    split; apply Rle_bool_true; apply IZR_le; [apply Zfloor_le | apply Zceil_le]; exact L.
Admitted.
