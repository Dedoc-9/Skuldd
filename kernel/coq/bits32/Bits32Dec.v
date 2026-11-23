(* Bits32Dec.v: lemmas for the proof of BITS32 (statement in BITS32_Statement.v, which this file does not change).
   Flocq and the standard library only; every lemma ends with Qed and nothing is assumed. Author: the assistant
   (2026-11-21).

   What is here. The fields of a pattern (split32), Flocq's decoding of a pattern (Bits.binary_float_of_bits_aux)
   written over those fields (dec_body), the decoding of the encodings SPEC32 returns (join32 s 0 0, enc_int32 s mg),
   and the integer and real facts its last branch needs: the magnitude mg is at most 2^23, and the sign applied to
   mg is the floor or the ceiling of +-m * 2^-k (b32_mg_int with b32_floor_ceil_val).

   What is not here. No lemma restates SPEC32: the proofs of its conjuncts (Bits32Spec.v) unfold the statement's own
   definition, so a change to SPEC32 is met where a conjunct that reads it is proved. Of the statement's definitions
   this file reads split32, join32, enc_int32, dec32, val32, sign32, is_nan32 and is_finite32; is_finite32 is read
   only on a pattern that is not a NaN (b32_fin). *)
From Coq Require Import ZArith Reals Lia Lra.
From Flocq Require Import Core BinarySingleNaN.
From Flocq Require Binary Bits.
From MKF.bits32 Require Import BITS32_Statement.
Open Scope Z_scope.

(* 1. Constants. *)
Lemma b32_p8 : 2 ^ 8 = 256. Proof. reflexivity. Qed.
Lemma b32_p22 : 2 ^ 22 = 4194304. Proof. reflexivity. Qed.
Lemma b32_p23 : 2 ^ 23 = 8388608. Proof. reflexivity. Qed.
Lemma b32_p24 : 2 ^ 24 = 16777216. Proof. reflexivity. Qed.
Lemma b32_p32 : 2 ^ 32 = 4294967296. Proof. reflexivity. Qed.

Lemma b32_zeqb_false (x y : Z) : x <> y -> Zeq_bool x y = false.
Proof.
  intros H. unfold Zeq_bool. destruct (Z.compare_spec x y); [contradiction | reflexivity | reflexivity].
Qed.

(* 2. Flocq's decoding of a pattern, over its fields. dec_body is Bits.binary_float_of_bits_aux 23 8 written with
   the fields given (emin of binary32 is -149). *)
Definition bfa (u : Z) : Binary.full_float := Bits.binary_float_of_bits_aux 23 8 u.

Definition dec_body (s : bool) (mf ef : Z) : Binary.full_float :=
  if Zeq_bool ef 0 then
    match mf with
    | Z0 => Binary.F754_zero s
    | Zpos px => Binary.F754_finite s px (-149)
    | Zneg _ => Binary.F754_nan false xH
    end
  else if Zeq_bool ef 255 then
    match mf with
    | Z0 => Binary.F754_infinity s
    | Zpos plx => Binary.F754_nan s plx
    | Zneg _ => Binary.F754_nan false xH
    end
  else
    match (mf + 2 ^ 23)%Z with
    | Zpos px => Binary.F754_finite s px (ef + -149 - 1)
    | _ => Binary.F754_nan false xH
    end.

Definition mant (mf ef : Z) : Z := if ef =? 0 then mf else mf + 2 ^ 23.

Lemma b32_split_info (u : Z) (s : bool) (mf ef : Z) : split32 u = (s, mf, ef) ->
  0 <= mf < 2 ^ 23 /\ 0 <= ef < 2 ^ 8 /\ bfa u = dec_body s mf ef.
Proof.
  intros E.
  assert (Hm : mf = u mod 2 ^ 23).
  { change (snd (fst (s, mf, ef)) = u mod 2 ^ 23). rewrite <- E. reflexivity. }
  assert (He : ef = (u / 2 ^ 23) mod 2 ^ 8).
  { change (snd (s, mf, ef) = (u / 2 ^ 23) mod 2 ^ 8). rewrite <- E. reflexivity. }
  split; [| split].
  - rewrite Hm. apply Z.mod_pos_bound. rewrite b32_p23. lia.
  - rewrite He. apply Z.mod_pos_bound. rewrite b32_p8. lia.
  - unfold split32 in E. unfold bfa, Bits.binary_float_of_bits_aux. cbv beta.
    rewrite E. reflexivity.
Qed.

(* 3. dec32 is Flocq's FF2B of the decoding; its value, sign and classes are those of the decoding. *)
Lemma b32_dec_FF (u : Z) : exists H, dec32 u = @Binary.FF2B 24 128 (bfa u) H.
Proof.
  eexists. reflexivity.
Qed.

Lemma b32_val (u : Z) : val32 (dec32 u) = Binary.FF2R radix2 (bfa u).
Proof.
  destruct (b32_dec_FF u) as [P E]. rewrite E. clear E. revert P.
  destruct (bfa u); intros P; reflexivity.
Qed.

Lemma b32_sign (u : Z) : sign32 (dec32 u) = Binary.sign_FF (bfa u).
Proof.
  destruct (b32_dec_FF u) as [P E]. rewrite E. clear E. revert P.
  destruct (bfa u); intros P; reflexivity.
Qed.

Lemma b32_nan (u : Z) : is_nan32 (dec32 u) = Binary.is_nan_FF (bfa u).
Proof.
  destruct (b32_dec_FF u) as [P E]. rewrite E. clear E. revert P.
  destruct (bfa u); intros P; reflexivity.
Qed.

(* is_finite32 is read on a pattern that is not a NaN only. *)
Lemma b32_fin (u : Z) : is_nan32 (dec32 u) = false -> is_finite32 (dec32 u) = Binary.is_finite_FF (bfa u).
Proof.
  destruct (b32_dec_FF u) as [P E]. rewrite E. clear E. revert P.
  destruct (bfa u); intros P H; first [reflexivity | discriminate H].
Qed.

Lemma b32_nan_not_fin (f : Binary.full_float) : Binary.is_nan_FF f = true -> Binary.is_finite_FF f = false.
Proof. destruct f; simpl; intros H; congruence. Qed.

Lemma b32_fin_not_nan_FF (f : Binary.full_float) : Binary.is_finite_FF f = true -> Binary.is_nan_FF f = false.
Proof. destruct f; simpl; intros H; congruence. Qed.

(* 4. The decoding by fields. *)
Lemma b32_dec_fin (s : bool) (mf ef : Z) : 0 <= mf < 2 ^ 23 -> 0 <= ef < 255 ->
  Binary.is_finite_FF (dec_body s mf ef) = true /\ Binary.is_nan_FF (dec_body s mf ef) = false /\
  Binary.sign_FF (dec_body s mf ef) = s /\
  Binary.FF2R radix2 (dec_body s mf ef) = (IZR (cond_Zopp s (mant mf ef)) * bpow radix2 (Z.max ef 1 - 150))%R.
Proof.
  intros Hm He. unfold dec_body.
  destruct (Z.eq_dec ef 0) as [E0 | E0].
  - subst ef. destruct mf as [| p | p].
    + refine (conj eq_refl (conj eq_refl (conj eq_refl _))).
      replace (cond_Zopp s (mant 0 0)) with 0 by (destruct s; reflexivity).
      transitivity 0%R; [reflexivity | ring].
    + refine (conj eq_refl (conj eq_refl (conj eq_refl _))). reflexivity.
    + exfalso. lia.
  - rewrite (b32_zeqb_false ef 0 E0). rewrite (b32_zeqb_false ef 255) by lia.
    unfold mant. rewrite (proj2 (Z.eqb_neq ef 0) E0).
    destruct (mf + 2 ^ 23) as [| p | p] eqn:Ep.
    + exfalso. rewrite b32_p23 in Ep. lia.
    + refine (conj eq_refl (conj eq_refl (conj eq_refl _))).
      rewrite Z.max_l by lia.
      replace (ef + -149 - 1) with (ef - 150) by ring. reflexivity.
    + exfalso. rewrite b32_p23 in Ep. lia.
Qed.

Lemma b32_dec_inf (s : bool) : dec_body s 0 255 = Binary.F754_infinity s.
Proof. reflexivity. Qed.

Lemma b32_dec_nan (s : bool) (mf : Z) : 0 < mf -> Binary.is_nan_FF (dec_body s mf 255) = true.
Proof. intros H. destruct mf as [| p | p]; [lia | reflexivity | lia]. Qed.

(* 5. The encodings SPEC32 returns. *)
Lemma b32_bfa_join (s : bool) (m e : Z) : 0 <= m < 2 ^ 23 -> 0 <= e < 2 ^ 8 -> bfa (join32 s m e) = dec_body s m e.
Proof.
  intros Hm He.
  assert (E : split32 (join32 s m e) = (s, m, e)) by exact (Bits.split_join_bits 23 8 s m e Hm He).
  destruct (b32_split_info _ _ _ _ E) as (_ & _ & H). exact H.
Qed.

Lemma b32_join_range (s : bool) (m e : Z) : 0 <= m < 2 ^ 23 -> 0 <= e < 2 ^ 8 -> 0 <= join32 s m e < 2 ^ 32.
Proof. intros Hm He. exact (Bits.join_bits_range 23 8 s m e Hm He). Qed.

Lemma b32_zero_dec (s : bool) : bfa (join32 s 0 0) = Binary.F754_zero s.
Proof. rewrite b32_bfa_join; [reflexivity | rewrite b32_p23; lia | rewrite b32_p8; lia]. Qed.

Lemma b32_enc_fields (mg : Z) : 1 <= mg <= 2 ^ 23 ->
  0 <= Z.log2 mg <= 23 /\ 0 <= mg * 2 ^ (23 - Z.log2 mg) - 2 ^ 23 < 2 ^ 23.
Proof.
  intros H.
  assert (L0 : 0 <= Z.log2 mg) by apply Z.log2_nonneg.
  assert (L1 : Z.log2 mg <= 23).
  { assert (E : Z.log2 (2 ^ 23) = 23) by reflexivity. rewrite <- E. apply Z.log2_le_mono. lia. }
  pose proof (Z.log2_spec mg ltac:(lia)) as S.
  assert (A : 2 ^ Z.log2 mg * 2 ^ (23 - Z.log2 mg) = 2 ^ 23)
    by (rewrite <- Z.pow_add_r by lia; f_equal; lia).
  assert (B : 2 ^ Z.succ (Z.log2 mg) * 2 ^ (23 - Z.log2 mg) = 2 ^ 24)
    by (rewrite <- Z.pow_add_r by lia; f_equal; lia).
  assert (Q : 0 < 2 ^ (23 - Z.log2 mg)) by (apply Z.pow_pos_nonneg; lia).
  assert (C1 : 2 ^ Z.log2 mg * 2 ^ (23 - Z.log2 mg) <= mg * 2 ^ (23 - Z.log2 mg))
    by (apply Z.mul_le_mono_nonneg_r; lia).
  assert (C2 : mg * 2 ^ (23 - Z.log2 mg) < 2 ^ Z.succ (Z.log2 mg) * 2 ^ (23 - Z.log2 mg))
    by (apply Z.mul_lt_mono_pos_r; lia).
  rewrite A in C1. rewrite B in C2.
  split; [lia |].
  revert C1 C2. generalize (mg * 2 ^ (23 - Z.log2 mg)). intros T C1 C2.
  rewrite b32_p23, b32_p24 in *. lia.
Qed.

Lemma b32_enc_range (s : bool) (mg : Z) : 1 <= mg <= 2 ^ 23 -> 0 <= enc_int32 s mg < 2 ^ 32.
Proof.
  intros H. destruct (b32_enc_fields mg H) as [L F]. unfold enc_int32. apply b32_join_range.
  - exact F.
  - rewrite b32_p8. lia.
Qed.

Lemma b32_enc_dec (s : bool) (mg : Z) : 1 <= mg <= 2 ^ 23 ->
  Binary.is_finite_FF (bfa (enc_int32 s mg)) = true /\
  Binary.FF2R radix2 (bfa (enc_int32 s mg)) = IZR (cond_Zopp s mg) /\
  Binary.sign_FF (bfa (enc_int32 s mg)) = s.
Proof.
  intros H. destruct (b32_enc_fields mg H) as [L F].
  assert (He : 0 <= Z.log2 mg + 127 < 2 ^ 8) by (rewrite b32_p8; lia).
  assert (He' : 0 <= Z.log2 mg + 127 < 255) by lia.
  unfold enc_int32. rewrite (b32_bfa_join s _ _ F He).
  destruct (b32_dec_fin s _ _ F He') as (Fi & _ & Si & Vi).
  rewrite Fi, Si, Vi. refine (conj eq_refl (conj _ eq_refl)).
  replace (mant (mg * 2 ^ (23 - Z.log2 mg) - 2 ^ 23) (Z.log2 mg + 127)) with (mg * 2 ^ (23 - Z.log2 mg))
    by (unfold mant; rewrite (proj2 (Z.eqb_neq (Z.log2 mg + 127) 0)) by (lia); cbv iota; ring).
  rewrite Z.max_l by lia.
  replace (cond_Zopp s (mg * 2 ^ (23 - Z.log2 mg))) with (cond_Zopp s mg * 2 ^ (23 - Z.log2 mg))
    by (destruct s; cbn [cond_Zopp]; ring).
  rewrite mult_IZR. change (IZR (2 ^ (23 - Z.log2 mg))) with (IZR (Zpower radix2 (23 - Z.log2 mg))).
  rewrite (IZR_Zpower radix2 (23 - Z.log2 mg)) by lia.
  rewrite Rmult_assoc, <- bpow_plus.
  replace (23 - Z.log2 mg + (Z.log2 mg + 127 - 150)) with 0 by ring.
  change (bpow radix2 0) with 1%R. ring.
Qed.

(* 6. The last branch of SPEC32: m / 2^k + (0 or 1), with m < 2^24 and k >= 1, is at most 2^23; the result is
   join32 s 0 0 when it is 0, enc_int32 s of it otherwise. Stated for any rounding bit b and any sign of the zero,
   so that these facts hold whatever the direction. *)
Lemma b32_mant_range (ef mf : Z) : 0 <= mf < 2 ^ 23 -> 0 <= (if ef =? 0 then mf else mf + 2 ^ 23) < 2 ^ 24.
Proof. intros H. rewrite b32_p23, b32_p24 in *. destruct (ef =? 0); cbv iota; lia. Qed.

Lemma b32_mg_range (b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  0 <= m / 2 ^ k + (if b then 1 else 0) <= 2 ^ 23.
Proof.
  intros Hm Hk.
  assert (P2 : 2 ^ 1 <= 2 ^ k) by (apply Z.pow_le_mono_r; lia).
  change (2 ^ 1) with 2 in P2.
  assert (Q0 : 0 <= m / 2 ^ k) by (apply Z.div_pos; lia).
  assert (Q1 : m / 2 ^ k <= m / 2) by (apply Z.div_le_compat_l; lia).
  assert (Q2 : m / 2 < 2 ^ 23) by (apply Z.div_lt_upper_bound; rewrite ?b32_p23, ?b32_p24 in *; lia).
  rewrite b32_p23 in *. destruct b; cbv iota; lia.
Qed.

Lemma b32_last_range (s sz b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  0 <= (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 sz 0 0
        else enc_int32 s (m / 2 ^ k + (if b then 1 else 0))) < 2 ^ 32.
Proof.
  intros Hm Hk. pose proof (b32_mg_range b m k Hm Hk) as R.
  destruct (Z.eqb_spec (m / 2 ^ k + (if b then 1 else 0)) 0) as [E | E]; cbv iota.
  - apply b32_join_range; [rewrite b32_p23 | rewrite b32_p8]; lia.
  - apply b32_enc_range. lia.
Qed.

Lemma b32_last_dec (s b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  Binary.is_finite_FF (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                            else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) = true /\
  Binary.FF2R radix2 (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                           else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) =
    IZR (cond_Zopp s (m / 2 ^ k + (if b then 1 else 0))) /\
  Binary.sign_FF (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                       else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) = s.
Proof.
  intros Hm Hk. pose proof (b32_mg_range b m k Hm Hk) as R.
  destruct (Z.eqb_spec (m / 2 ^ k + (if b then 1 else 0)) 0) as [E | E]; cbv iota.
  - rewrite E, b32_zero_dec. refine (conj eq_refl (conj _ eq_refl)). destruct s; reflexivity.
  - apply b32_enc_dec. lia.
Qed.

Lemma b32_last_fin (s b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  Binary.is_finite_FF (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                            else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) = true.
Proof. intros Hm Hk. exact (proj1 (b32_last_dec s b m k Hm Hk)). Qed.

Lemma b32_last_val (s b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  Binary.FF2R radix2 (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                           else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) =
    IZR (cond_Zopp s (m / 2 ^ k + (if b then 1 else 0))).
Proof. intros Hm Hk. exact (proj1 (proj2 (b32_last_dec s b m k Hm Hk))). Qed.

Lemma b32_last_sign (s b : bool) (m k : Z) : 0 <= m < 2 ^ 24 -> 1 <= k ->
  Binary.sign_FF (bfa (if m / 2 ^ k + (if b then 1 else 0) =? 0 then join32 s 0 0
                       else enc_int32 s (m / 2 ^ k + (if b then 1 else 0)))) = s.
Proof. intros Hm Hk. exact (proj2 (proj2 (b32_last_dec s b m k Hm Hk))). Qed.

(* 7. The magnitude with its sign is the floor (up = false) or the ceiling (up = true) of +-m / 2^k, in integers. *)
Lemma b32_mg_int (up s : bool) (m k : Z) : 0 <= k ->
  cond_Zopp s (m / 2 ^ k + (if andb (negb (m mod 2 ^ k =? 0)) (if up then negb s else s) then 1 else 0)) =
  (if up then - ((- cond_Zopp s m) / 2 ^ k) else cond_Zopp s m / 2 ^ k).
Proof.
  intros Hk.
  assert (P : 2 ^ k <> 0) by (apply Z.pow_nonzero; lia).
  destruct (Z.eq_dec (m mod 2 ^ k) 0) as [R | R].
  - rewrite R, Z.eqb_refl. cbn [negb andb]. rewrite Z.add_0_r.
    destruct up, s; cbn [cond_Zopp].
    + rewrite Z.opp_involutive. reflexivity.
    + rewrite Z.div_opp_l_z by assumption. rewrite Z.opp_involutive. reflexivity.
    + rewrite Z.div_opp_l_z by assumption. reflexivity.
    + reflexivity.
  - rewrite (proj2 (Z.eqb_neq _ 0) R). cbn [negb andb].
    destruct up, s; cbn [negb cond_Zopp].
    + rewrite Z.opp_involutive. ring.
    + rewrite Z.div_opp_l_nz by assumption. ring.
    + rewrite Z.div_opp_l_nz by assumption. ring.
    + ring.
Qed.

(* 8. Real facts: +-m * 2^-k is +-m / 2^k, and its floor and ceiling are integer divisions. *)
Lemma b32_val_neg (a k : Z) : 0 <= k -> (IZR a * bpow radix2 (- k) = IZR a / IZR (2 ^ k))%R.
Proof.
  intros Hk. rewrite bpow_opp.
  change (IZR (2 ^ k)) with (IZR (Zpower radix2 k)).
  rewrite (IZR_Zpower radix2 k Hk). reflexivity.
Qed.

Lemma b32_floor_div2 (a b : Z) : 0 < b -> Zfloor (IZR a / IZR b) = a / b.
Proof.
  intros Hb. apply Zfloor_imp.
  pose proof (Z.div_mod a b ltac:(lia)) as D. pose proof (Z.mod_pos_bound a b Hb) as M.
  assert (B : (0 < IZR b)%R) by (apply IZR_lt; exact Hb).
  assert (Ea : IZR a = (IZR b * IZR (a / b) + IZR (a mod b))%R).
  { rewrite <- mult_IZR, <- plus_IZR. f_equal. exact D. }
  assert (R0 : (0 <= IZR (a mod b))%R) by (apply IZR_le; lia).
  assert (R1 : (IZR (a mod b) < IZR b)%R) by (apply IZR_lt; lia).
  rewrite plus_IZR, Ea. split.
  - apply Rmult_le_reg_r with (IZR b); [exact B |].
    unfold Rdiv. rewrite Rmult_assoc, Rinv_l, Rmult_1_r by lra. first [lra | nra].
  - apply Rmult_lt_reg_r with (IZR b); [exact B |].
    unfold Rdiv. rewrite Rmult_assoc, Rinv_l, Rmult_1_r by lra. first [lra | nra].
Qed.

Lemma b32_floor_ceil_val (up : bool) (a b : Z) : 0 < b ->
  IZR (if up then Zceil (IZR a / IZR b)%R else Zfloor (IZR a / IZR b)%R) = IZR (if up then - ((- a) / b) else a / b).
Proof.
  intros Hb. destruct up.
  - unfold Zceil.
    replace (- (IZR a / IZR b))%R with (IZR (- a) / IZR b)%R by (rewrite opp_IZR; unfold Rdiv; ring).
    rewrite (b32_floor_div2 (- a) b Hb). reflexivity.
  - rewrite (b32_floor_div2 a b Hb). reflexivity.
Qed.

(* 9. The NaN branch: u lor 2^22 is a pattern, and its 31 low bits are those of u with bit 22 set. *)
Lemma b32_lor_lt32 (a b : Z) : 0 <= a < 2 ^ 32 -> 0 <= b < 2 ^ 32 -> 0 <= Z.lor a b < 2 ^ 32.
Proof.
  intros Ha Hb. split.
  - apply Z.lor_nonneg. lia.
  - assert (D : Z.lor a b / 2 ^ 32 = 0).
    { rewrite <- Z.shiftr_div_pow2 by lia. rewrite Z.shiftr_lor.
      rewrite !Z.shiftr_div_pow2 by lia. rewrite (Z.div_small a), (Z.div_small b) by lia. reflexivity. }
    destruct (Z.lt_ge_cases (Z.lor a b) (2 ^ 32)) as [L | L]; [exact L |].
    exfalso. assert (1 <= Z.lor a b / 2 ^ 32) by (apply Z.div_le_lower_bound; lia). lia.
Qed.

Lemma b32_lor_mod31 (u : Z) : Z.lor u (2 ^ 22) mod 2 ^ 31 = Z.lor (u mod 2 ^ 31) (2 ^ 22).
Proof.
  rewrite <- !Z.land_ones by lia.
  rewrite Z.land_lor_distr_l. f_equal; reflexivity.
Qed.
