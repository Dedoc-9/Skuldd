(* Ceil32.v: proofs of the first four parts of CEIL32 (statement in CEIL32_Statement.v, which this file does not
   change): CL_EXACT, CL_VALUE, CL_SIGN and CL_NONFINITE. This file does not name Flocq's round-to-integral
   operation (a search of it for that name finds nothing): the fifth part, CL_IEEE, is proved in CeilIEEE.v from
   these four and Flocq's correctness theorem for that operation, so the trust that Flocq's operation is IEEE 754's
   round-to-integral stays with the fifth part. Flocq and the standard library only; every lemma ends with Qed and
   nothing is assumed. Author: the assistant (2026-11-18). It follows floor32/Floor32.v and imports nothing of it.

   How it goes.
     EXACT      |x| >= 2^23: a binary32 number that large is whole (sincos32/Reduce.v's f32_int) and the graph
                returns it. |x| < 2^23: turn_N x is the whole number N nearest x (Reduce.v's turn_N_eq), so
                |x - N| <= 1/2 and ceil x is N + 1 when N < x, N otherwise; N + 1 is a binary64 number, so the
                addition is exact; the zero step changes no value in the model. A whole number below 2^24 in
                magnitude is a binary32 number.
     VALUE      Each operation of the shape through sincos32i/TOps.v: the input as den b x 23, T_N by N_den, the
                addition by den_add, the comparisons by top_sel_le_at and top_sel_lt_at.
     SIGN       The step: a zero y selects b * +0, the zero with b's sign (computed on constructors); a y that is
                not a zero is returned, and its value ceil x has the sign of x (ceil of a negative number is at most
                0, of a positive one at least x). The 2^23 branch returns b itself.
     NONFINITE  Evaluated by the kernel (vm_compute) on the three values that are not finite.
   What it does not show: what the statement's header says it does not say. *)
From Coq Require Import Reals ZArith Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs.
From MKF.sincos32 Require Import Graph Reduce.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement TOps.
From MKF.ceil32 Require Import CEIL32_Statement.
Open Scope R_scope.

#[local] Instance cl_p53 : Prec_gt_0 53 := prec64_gt_0.

(* 1. The model *)

Lemma cl_abs_le0 (y : R) : Rabs y <= 0 -> y = 0.
Proof. intros H. apply Rabs_le_inv in H. lra. Qed.

Lemma cl_rn64_int (m : Z) : (Z.abs m < 9007199254740992)%Z -> RN64 (IZR m) = IZR m.
Proof. intros H. apply round_generic; [typeclasses eauto | exact (int_f64 m H)]. Qed.

Lemma cl_int_f32 (m : Z) : (Z.abs m < 16777216)%Z -> format32 (IZR m).
Proof.
  intros H. replace (IZR m) with (IZR m * bpow radix2 0) by (change (bpow radix2 0) with 1; ring).
  apply rep_f32; [exact H | lia].
Qed.

(* The zero step changes no value in the model. *)
Lemma cl_step_model (x y : R) : (if Rle_dec (Rabs y) 0 then RN64 (x * 0) else y) = y.
Proof.
  destruct (Rle_dec (Rabs y) 0) as [H | _]; [| reflexivity].
  rewrite (cl_abs_le0 y H), Rmult_0_r. apply round_0; typeclasses eauto.
Qed.

(* ceil from the nearest whole number. *)
Lemma cl_ceil_near (x : R) (N : Z) : Rabs (x - IZR N) <= / 2 ->
  Zceil x = (if Rlt_dec (IZR N) x then (N + 1)%Z else N).
Proof.
  intros H. apply Rabs_le_inv in H. destruct (Rlt_dec (IZR N) x) as [L | L].
  - apply Zceil_imp. replace (N + 1 - 1)%Z with N by ring. rewrite plus_IZR. lra.
  - apply Rnot_lt_le in L. apply Zceil_imp. rewrite minus_IZR. lra.
Qed.

Lemma cl_y_model (x : R) : Rabs x < 8388608 ->
  (if Rlt_dec (turn_N x) x then RN64 (turn_N x + 1) else turn_N x) = IZR (Zceil x).
Proof.
  intros Hx. rewrite (turn_N_eq x Hx).
  pose proof (Znearest_half (fun z => negb (Z.even z)) x) as Hh.
  pose proof (near_bound x Hx) as Hb.
  rewrite (cl_ceil_near x _ Hh).
  destruct (Rlt_dec (IZR (ZnearestE x)) x) as [L | L].
  - rewrite <- plus_IZR. apply cl_rn64_int. lia.
  - reflexivity.
Qed.

Lemma cl_g_big (x : R) : turn_BIG <= Rabs x -> g_ceil32 x = x.
Proof.
  intros B. unfold g_ceil32. destruct (Rle_dec turn_BIG (Rabs x)) as [_ | N]; [reflexivity | contradiction].
Qed.

Lemma cl_g_small (x : R) : Rabs x < 8388608 ->
  g_ceil32 x = (if Rlt_dec (turn_N x) x then RN64 (turn_N x + 1) else turn_N x).
Proof.
  intros Hx. unfold g_ceil32. destruct (Rle_dec turn_BIG (Rabs x)) as [B | _].
  - exfalso. unfold turn_BIG in B. lra.
  - cbv zeta. apply cl_step_model.
Qed.

Theorem CL_EXACT_proof : CL_EXACT.
Proof.
  intros x Fx. destruct (Rle_dec turn_BIG (Rabs x)) as [B | B].
  - rewrite (cl_g_big x B). split; [| exact Fx].
    unfold turn_BIG in B. destruct (f32_int x Fx B) as [n E]. rewrite E, Zceil_IZR. reflexivity.
  - assert (Hx : Rabs x < 8388608) by (unfold turn_BIG in B; apply Rnot_le_lt in B; exact B).
    rewrite (cl_g_small x Hx), (cl_y_model x Hx). split; [reflexivity |].
    apply cl_int_f32.
    pose proof (Znearest_half (fun z => negb (Z.even z)) x) as Hh.
    pose proof (near_bound x Hx) as Hb.
    rewrite (cl_ceil_near x _ Hh). destruct (Rlt_dec (IZR (ZnearestE x)) x); lia.
Qed.

(* 2. IEEE binary64: the step, and signs *)

Lemma cl_fin_zero (y : b64) : is_finite y = true -> B2R y = 0 -> exists s : bool, y = @B754_zero 53 1024 s.
Proof.
  destruct y as [s | s | | s m e H]; intros Fy Vy; try discriminate Fy.
  - exists s. reflexivity.
  - exfalso. simpl in Vy. apply eq_0_F2R in Vy. simpl in Vy. destruct s; discriminate Vy.
Qed.

Lemma cl_mul0 (b : b64) : is_finite b = true ->
  t_mul tieee_ops b (t_cst tieee_ops K_0) = @B754_zero 53 1024 (Bsign b).
Proof. destruct b as [s | s | | s m e H]; intros Fb; try discriminate Fb; destruct s; reflexivity. Qed.

Lemma cl_step_zero (b y : b64) : is_finite b = true -> is_finite y = true -> B2R y = 0 ->
  t_sel_le tieee_ops (t_abs tieee_ops y) (t_cst tieee_ops K_0) (t_mul tieee_ops b (t_cst tieee_ops K_0)) y
  = @B754_zero 53 1024 (Bsign b).
Proof.
  intros Fb Fy Vy. rewrite (cl_mul0 b Fb). destruct (cl_fin_zero y Fy Vy) as [s E]. rewrite E. reflexivity.
Qed.

Lemma cl_step_nonzero (b y : b64) : is_finite y = true -> B2R y <> 0 ->
  t_sel_le tieee_ops (t_abs tieee_ops y) (t_cst tieee_ops K_0) (t_mul tieee_ops b (t_cst tieee_ops K_0)) y = y.
Proof.
  intros Fy Ny.
  assert (Fa : is_finite (t_abs tieee_ops y) = true) by (rewrite top_abs_fin; exact Fy).
  rewrite (top_sel_le _ _ _ _ Fa (tcst_fin K_0)), top_abs_val, tval_0.
  destruct (Rle_dec (Rabs (B2R y)) 0) as [H | _]; [exfalso; exact (Ny (cl_abs_le0 _ H)) | reflexivity].
Qed.

Lemma cl_sign_neg (y : b64) : is_finite y = true -> B2R y < 0 -> Bsign y = true.
Proof.
  destruct y as [s | s | | s m e B]; intros Fy V; try discriminate Fy.
  - exfalso. simpl in V. lra.
  - destruct s; [reflexivity |]. exfalso. revert V. unfold B2R. rewrite F2R_cond_Zopp. simpl cond_Ropp.
    intros V. assert (0 < F2R (Float radix2 (Z.pos m) e)) by (apply F2R_gt_0; reflexivity). lra.
Qed.

Lemma cl_sign_pos (y : b64) : is_finite y = true -> 0 < B2R y -> Bsign y = false.
Proof.
  destruct y as [s | s | | s m e B]; intros Fy V; try discriminate Fy.
  - exfalso. simpl in V. lra.
  - destruct s; [| reflexivity]. exfalso. revert V. unfold B2R. rewrite F2R_cond_Zopp. simpl cond_Ropp.
    intros V. assert (0 < F2R (Float radix2 (Z.pos m) e)) by (apply F2R_gt_0; reflexivity). lra.
Qed.

(* 3. The shape on a binary32 input *)

(* The inner value y on an input below 2^23: finite, and ceil x. *)
Lemma cl_y_ieee (b : b64) : is_finite b = true -> Rabs (B2R b) < 8388608 ->
  is_finite (CL_y b64 tieee_ops b) = true /\ B2R (CL_y b64 tieee_ops b) = IZR (Zceil (B2R b)).
Proof.
  intros Fb Hx.
  assert (Db : den b (B2R b) 23).
  { split; [exact Fb | split; [reflexivity |]]. change (bpow radix2 23) with 8388608. lra. }
  pose proof (N_den b (B2R b) 23 55 Db ltac:(lia) ltac:(lia) ltac:(lia)) as DN.
  pose proof DN as (FN & VN & _).
  rewrite <- (cl_y_model (B2R b) Hx). unfold CL_y.
  rewrite (top_sel_lt_at (T_N b64 tieee_ops b) b _ _ (turn_N (B2R b)) (B2R b) FN Fb VN eq_refl).
  destruct (Rlt_dec (turn_N (B2R b)) (B2R b)) as [L | L].
  - pose proof (den_add _ (t_cst tieee_ops K_1) _ 1 55 0 56 DN den_c1 ltac:(lia) ltac:(lia) ltac:(lia))
      as (F & V & _).
    split; [exact F | exact V].
  - split; [exact FN | exact VN].
Qed.

(* The outer selection: 2^23 <= |x| returns b, otherwise the stepped inner value. *)
Lemma cl_outer (b : b64) : is_finite b = true ->
  T_ceil32 b64 tieee_ops b =
  if Rle_dec turn_BIG (Rabs (B2R b)) then b
  else t_sel_le tieee_ops (t_abs tieee_ops (CL_y b64 tieee_ops b)) (t_cst tieee_ops K_0)
         (t_mul tieee_ops b (t_cst tieee_ops K_0)) (CL_y b64 tieee_ops b).
Proof.
  intros Fb. unfold T_ceil32.
  assert (FA : is_finite (t_abs tieee_ops b) = true) by (rewrite top_abs_fin; exact Fb).
  exact (top_sel_le_at _ _ _ _ turn_BIG (Rabs (B2R b)) (tcst_fin K_BIG) FA tval_BIG (top_abs_val b)).
Qed.

Theorem CL_VALUE_proof : CL_VALUE.
Proof.
  intros b Fb F32. rewrite (cl_outer b Fb).
  destruct (Rle_dec turn_BIG (Rabs (B2R b))) as [B | B].
  - rewrite (cl_g_big _ B). split; [exact Fb | reflexivity].
  - assert (Hx : Rabs (B2R b) < 8388608) by (unfold turn_BIG in B; apply Rnot_le_lt in B; exact B).
    destruct (cl_y_ieee b Fb Hx) as [Fy Vy].
    rewrite (cl_g_small _ Hx), (cl_y_model _ Hx).
    destruct (Req_dec (B2R (CL_y b64 tieee_ops b)) 0) as [Z | Z].
    + rewrite (cl_step_zero b _ Fb Fy Z). split; [reflexivity |]. rewrite <- Vy, Z. reflexivity.
    + rewrite (cl_step_nonzero b _ Fy Z). split; [exact Fy | exact Vy].
Qed.

Theorem CL_SIGN_proof : CL_SIGN.
Proof.
  intros b Fb F32. rewrite (cl_outer b Fb).
  destruct (Rle_dec turn_BIG (Rabs (B2R b))) as [B | B]; [reflexivity |].
  assert (Hx : Rabs (B2R b) < 8388608) by (unfold turn_BIG in B; apply Rnot_le_lt in B; exact B).
  destruct (cl_y_ieee b Fb Hx) as [Fy Vy].
  destruct (Req_dec (B2R (CL_y b64 tieee_ops b)) 0) as [Z | Z].
  - rewrite (cl_step_zero b _ Fb Fy Z). reflexivity.
  - rewrite (cl_step_nonzero b _ Fy Z). rewrite Vy in Z.
    destruct (Rlt_dec (B2R b) 0) as [N | N].
    + rewrite (cl_sign_neg b Fb N). apply cl_sign_neg; [exact Fy |]. rewrite Vy.
      pose proof (Zceil_lb (B2R b)) as U.
      assert (G : (Zceil (B2R b) < 1)%Z) by (apply lt_IZR; lra).
      assert (G2 : IZR (Zceil (B2R b)) <= 0) by (apply IZR_le; lia).
      destruct (Rle_lt_or_eq_dec _ 0 G2) as [L | L]; [exact L |].
      exfalso. apply Z. exact L.
    + assert (P : 0 < B2R b).
      { destruct (Req_dec (B2R b) 0) as [E | E].
        - exfalso. apply Z. rewrite E, Zceil_IZR. reflexivity.
        - apply Rnot_lt_le in N. destruct (Rle_lt_or_eq_dec 0 (B2R b) N) as [L | L]; [exact L |].
          exfalso. apply E. symmetry. exact L. }
      rewrite (cl_sign_pos b Fb P). apply cl_sign_pos; [exact Fy |]. rewrite Vy.
      pose proof (Zceil_ub (B2R b)). lra.
Qed.

Theorem CL_NONFINITE_proof : CL_NONFINITE.
Proof.
  intros b Fb. destruct b as [s | s | | s m e H]; try discriminate Fb.
  - destruct s; vm_compute; reflexivity.
  - vm_compute; reflexivity.
Qed.
