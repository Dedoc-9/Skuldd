(* Bits32Link.v: the proofs of SPEC32_PROGRAM and SPEC32_STORE, the link of BITS32 to the programs of floor32 and
   ceil32 (statement in BITS32_Statement.v, which this file does not change). Flocq and the standard library only,
   with the closed theorems FLOOR32 (floor32/Closed.v) and CEIL32 (ceil32/Closed.v); every lemma ends with Qed and
   nothing is assumed. Author: the assistant (2026-11-21).

   How it goes. Let u be a pattern that is not a NaN and b the widening of its binary32.
     PROGRAM  If u is finite, b is finite with u's value x, which is a binary32 number, and u's sign (B32_WIDEN).
              FL_VALUE, FL_EXACT and FL_SIGN give a finite result of value floor x and of b's sign; SPEC32_VALUE
              and B32_WIDEN give the same for the widening of SPEC32 false u's binary32. Two finite b64 values with
              the same value and sign are equal (Flocq's B2R_Bsign_inj). If u is an infinity, the program returns b
              (FL_NONFINITE) and SPEC32 false u = u (SPEC32_INF). The ceiling likewise with CEIL32.
     STORE    The widening is one-to-one on the binary32 values that are not NaNs and never sends a NaN to one of
              them (b32_widen_inj). SPEC32 up u's binary32 is not a NaN, so a v whose widening is the program's
              result is that binary32, and Flocq's bits_of_binary_float_of_bits gives its bits back, SPEC32 up u
              being a pattern (SPEC32_RANGE). *)
From Coq Require Import ZArith Reals Lia.
From Flocq Require Import Core BinarySingleNaN.
From Flocq Require Binary Bits.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
From MKF.floor32 Require Closed.
From MKF.ceil32 Require Closed.
From MKF.bits32 Require Import BITS32_Statement Bits32Spec Bits32Widen.
Open Scope Z_scope.

Lemma b32_fin32_not_nan (v : Bits.binary32) : is_finite32 v = true -> is_nan32 v = false.
Proof. destruct v; easy. Qed.

Lemma b32_prog_floor (u : Z) : 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = false ->
  T_floor32 b64 tieee_ops (widen32 (dec32 u)) = widen32 (dec32 (SPEC32 false u)).
Proof.
  intros Hu Hn.
  pose proof MKF.floor32.Closed.floor32_holds as FL. unfold FLOOR32 in FL.
  destruct FL as (FE & FV & FS & FN & _).
  destruct (B32_WIDEN_proof (dec32 u) Hn) as (Nb & Fb & Vb & Sb & Mb).
  case_eq (is_finite32 (dec32 u)); intros Hf; rewrite Hf in Fb.
  - pose proof (SPEC32_VALUE_proof false u Hu Hf) as W. cbv zeta in W. destruct W as (Fw & Vw & Sw).
    destruct (B32_WIDEN_proof _ (b32_fin32_not_nan _ Fw)) as (_ & Fw' & Vw' & Sw' & _).
    destruct (FV _ Fb Mb) as [Fr Vr].
    pose proof (FS _ Fb Mb) as Sr.
    destruct (FE _ Mb) as [Ex _].
    apply B2R_Bsign_inj.
    + exact Fr.
    + rewrite Fw'. exact Fw.
    + rewrite Vr, Ex, Vw', Vw, Vb. reflexivity.
    + rewrite Sr, Sb, Sw', Sw. reflexivity.
  - rewrite (FN _ Fb). rewrite (SPEC32_INF_proof false u Hu Hf Hn). reflexivity.
Qed.

Lemma b32_prog_ceil (u : Z) : 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = false ->
  T_ceil32 b64 tieee_ops (widen32 (dec32 u)) = widen32 (dec32 (SPEC32 true u)).
Proof.
  intros Hu Hn.
  pose proof MKF.ceil32.Closed.ceil32_holds as CL. unfold CEIL32 in CL.
  destruct CL as (CE & CV & CS & CN & _).
  destruct (B32_WIDEN_proof (dec32 u) Hn) as (Nb & Fb & Vb & Sb & Mb).
  case_eq (is_finite32 (dec32 u)); intros Hf; rewrite Hf in Fb.
  - pose proof (SPEC32_VALUE_proof true u Hu Hf) as W. cbv zeta in W. destruct W as (Fw & Vw & Sw).
    destruct (B32_WIDEN_proof _ (b32_fin32_not_nan _ Fw)) as (_ & Fw' & Vw' & Sw' & _).
    destruct (CV _ Fb Mb) as [Fr Vr].
    pose proof (CS _ Fb Mb) as Sr.
    destruct (CE _ Mb) as [Ex _].
    apply B2R_Bsign_inj.
    + exact Fr.
    + rewrite Fw'. exact Fw.
    + rewrite Vr, Ex, Vw', Vw, Vb. reflexivity.
    + rewrite Sr, Sb, Sw', Sw. reflexivity.
  - rewrite (CN _ Fb). rewrite (SPEC32_INF_proof true u Hu Hf Hn). reflexivity.
Qed.

Theorem SPEC32_PROGRAM_proof : SPEC32_PROGRAM.
Proof. intros u Hu Hn. exact (conj (b32_prog_floor u Hu Hn) (b32_prog_ceil u Hu Hn)). Qed.

(* The widening is one-to-one onto the values that are not NaNs. *)
Lemma b32_widen_inj (v w : Bits.binary32) : is_nan32 w = false -> widen32 v = widen32 w -> v = w.
Proof.
  intros Hw E.
  destruct (B32_WIDEN_proof w Hw) as (Nw & Fw & Vw & Sw & _).
  destruct (is_nan32 v) eqn:Hv.
  - exfalso. destruct v as [sv | sv | sv pl Hpl | sv mv ev Hbv]; try discriminate Hv.
    simpl in E. rewrite <- E in Nw. discriminate Nw.
  - destruct (B32_WIDEN_proof v Hv) as (Nv & Fv & Vv & Sv & _).
    assert (Ff : is_finite32 v = is_finite32 w) by (rewrite <- Fv, <- Fw, E; reflexivity).
    case_eq (is_finite32 w); intros Hfw.
    + apply Binary.B2R_Bsign_inj.
      * change (is_finite32 v = true). rewrite Ff. exact Hfw.
      * exact Hfw.
      * change (val32 v = val32 w). rewrite <- Vv, <- Vw, E. reflexivity.
      * change (sign32 v = sign32 w). rewrite <- Sv, <- Sw, E. reflexivity.
    + assert (Hfv : is_finite32 v = false) by (rewrite Ff; exact Hfw).
      destruct v as [sv | sv | sv pl Hpl | sv mv ev Hbv]; try discriminate Hfv; try discriminate Hv.
      destruct w as [sw | sw | sw pw Hpw | sw mw ew Hbw]; try discriminate Hfw; try discriminate Hw.
      simpl in E. injection E as ->. reflexivity.
Qed.

Lemma b32_out_not_nan (up : bool) (u : Z) : 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = false ->
  is_nan32 (dec32 (SPEC32 up u)) = false.
Proof.
  intros Hu Hn. case_eq (is_finite32 (dec32 u)); intros Hf.
  - pose proof (SPEC32_VALUE_proof up u Hu Hf) as W. cbv zeta in W. destruct W as (Fw & _ & _).
    exact (b32_fin32_not_nan _ Fw).
  - rewrite (SPEC32_INF_proof up u Hu Hf Hn). exact Hn.
Qed.

Lemma b32_bits_dec (n : Z) : 0 <= n < 2 ^ 32 -> Bits.bits_of_b32 (dec32 n) = n.
Proof.
  intros Hn. unfold dec32, Bits.bits_of_b32, Bits.b32_of_bits.
  apply Bits.bits_of_binary_float_of_bits. exact Hn.
Qed.

Theorem SPEC32_STORE_proof : SPEC32_STORE.
Proof.
  intros u v Hu Hn. split; intros E.
  - rewrite (b32_prog_floor u Hu Hn) in E.
    rewrite (b32_widen_inj v _ (b32_out_not_nan false u Hu Hn) E).
    apply b32_bits_dec. exact (SPEC32_RANGE_proof false u Hu).
  - rewrite (b32_prog_ceil u Hu Hn) in E.
    rewrite (b32_widen_inj v _ (b32_out_not_nan true u Hu Hn) E).
    apply b32_bits_dec. exact (SPEC32_RANGE_proof true u Hu).
Qed.
