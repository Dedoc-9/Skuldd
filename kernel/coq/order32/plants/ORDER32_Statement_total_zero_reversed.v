(* ORDER32: floor32 and ceil32 in order, and how the two relate. Its statement only, written before any proof script
   of it (a prose outline of each part's proof preceded it), 2026-11-21, a candidate for Push A under the owner's
   rulings ST-1 and BM-2 (a). Author: the assistant. Definitions only: this file holds no proof script and assumes
   nothing.

   THE MODEL. b64 is Flocq 4.2.1's BinarySingleNaN binary_float 53 1024 (ieee64/IEEE64_Statement.v, frozen,
   imported): IEEE 754 binary64 with two signed zeros, two infinities and one NaN, which carries no sign, no payload
   and no quiet bit (Bsign of it is false by Flocq's convention; it is not a sign bit). The two functions are the
   shapes of floor32/FLOOR32_Statement.v and ceil32/CEIL32_Statement.v (frozen, imported, not changed) at Flocq's IEEE
   binary64 operations in round to nearest even: below, FL b stands for T_floor32 b64 tieee_ops b and CL b for
   T_ceil32 b64 tieee_ops b. FLOOR32 and CEIL32 say what FL and CL compute; this file says how their results are
   ordered and how the two functions relate. A binary32 input is a finite binary64 value b with format32 (B2R b)
   (Flocq's FLT(-149, 24): every finite binary32 number, and the numbers of that form above the binary32 range),
   the inputs FL_VALUE and CL_VALUE cover. Some parts also take the non-finite inputs; their premise is FL_IEEE's,
   "is_finite b = false \/ format32 (B2R b)": B2R of an infinity or of the NaN is 0, so its left part is implied by
   its right part; it is written for the reader. A whole number is a real number equal to IZR z for an integer z.
   Equality of two binary64 values is Coq's equality in b64: on finite values it is equality of the real number and
   of the sign bit (Flocq's B2R_Bsign_inj; the converse is rewriting), so it sees the sign of a zero.

   WHAT IS STATED.
   - FC_ORD_R, order on real numbers: for every binary32 input b, B2R (FL b) <= B2R b <= B2R (CL b). Real numbers do
     not see the sign of a zero.
   - FC_ORD_LEB, order under Flocq's comparison: for every binary32 input and every infinity, both zeros included,
     FL b <= b, b <= CL b and FL b <= CL b under Bleb. Bleb finds both +0 <= -0 and -0 <= +0: it does not see the
     sign of a zero.
   - FC_ORD_NAN: for the NaN b and every binary64 value c, Bcompare (FL b) c and Bcompare c (CL b) are None (IEEE
     754's "unordered"), so Bleb is false on each. Bcompare is None exactly when one side is the NaN, so this says
     that FL b and CL b are the NaN: it restates FL_NONFINITE and CL_NONFINITE at the NaN in the terms of order.
   - fc_total_nn x y reads IEEE 754-2008's totalOrder (clause 5.10) on two binary64 values that are not NaN, as a
     boolean: true if x < y, false if x > y, and on equal values false only for x = +0 and y = -0 (-0 below +0). On
     the NaN it is false: it transcribes none of 5.10's NaN clauses.
   - FC_TOTAL_ZERO: fc_total_nn puts -0 below +0 and not +0 below -0 (5.10 c) 1) and 2)). A fact about the definition
     alone, stated so that its direction is checked: in the three pairs of FC_TOTAL_NN two equal values never differ
     in the sign of a zero, so FC_TOTAL_NN does not check it.
   - FC_TOTAL_NN: the three pairs of FC_ORD_LEB, on the same inputs, under fc_total_nn. It sees the sign of a zero in
     one direction only: it would be false if FL (-0) were +0 or CL (+0) were -0, not if FL (+0) were -0 or CL (-0)
     were +0. The signs themselves are said by FL_SIGN and CL_SIGN.
   - FC_DIFF: for every binary32 input, B2R (CL b) - B2R (FL b) is 0 or 1.
   - FC_FIX: for every binary32 input, b is a whole number exactly when FL b = b, and exactly when CL b = b.
   - FC_EQ_INT: for every binary32 input, FL b = CL b exactly when b is a whole number, and then both are b (signs of
     zero included: at b = -0 both are -0).
   - FC_NEG: for every binary32 input and every non-finite input, CL b = Bopp (FL (Bopp b)) as binary64 values, signs
     of zero included. At the NaN it says only that; that FL b and CL b are then the NaN is FL_NONFINITE's and
     CL_NONFINITE's.
   - FC_IDEM: for every binary32 input and every non-finite input, FL (FL b) = FL b and CL (CL b) = CL b.
   - FC_MONO: for two inputs, each a binary32 input or non-finite, if b1 <= b2 under Bleb (so neither is the NaN),
     then FL b1 <= FL b2 and CL b1 <= CL b2 under Bleb.
   Some parts follow from others and are not independent evidence: FC_ORD_R from FC_ORD_LEB, FL_VALUE and CL_VALUE
   (through Flocq's Bleb_correct); FC_ORD_NAN from FL_NONFINITE and CL_NONFINITE; the third conjunct of FC_ORD_LEB and
   of FC_TOTAL_NN from their first two (each order is transitive on values that are not NaN); the second conjunct of
   FC_EQ_INT from its first and FC_FIX.

   WHAT IT DOES NOT SAY. Nothing about finite inputs outside format32. Nothing a NaN carries (its sign bit, payload
   or quiet bit): so nothing about IEEE 754's totalOrder where a NaN is compared, and nothing about which NaN a
   program returns. Nothing about exception flags, the widening of a binary32 input to binary64 or the store of the
   result to binary32, a compiler, a processor or a program in any language. Nothing about the values of FL and CL
   beyond the parts above: those are FLOOR32's and CEIL32's.

   WHERE A PROOF OF IT STOPS. Each part is meant to follow from FLOOR32, CEIL32 and Flocq (FC_TOTAL_ZERO from the
   definition alone), so a proof of it stops where theirs stop and at three places of its own:
   - at the shapes over Flocq's IEEE model of binary64: not C, machine code or a processor.
   - at the NaN: the model has one NaN and no NaN bits. Beyond this stop the like claim on bit patterns under IEEE
     754's totalOrder is known to fail: when a signalling NaN comes back quieted with its sign kept, totalOrder puts
     a positive signalling NaN below its quiet result, so FL b <= b fails there, and a negative one above it, so
     b <= CL b fails there. That is IEEE 754's design (an operation quiets a signalling NaN), not an error of the
     program. Proof picks up again only in a model with NaN bits, not in this one.
   - at the readings in WHAT IT TRUSTS: they are trusted, and no proof inside the project reaches them.
   What covers each stop beyond it, with its grade, and where proof picks up again, are the boundary map's rows for
   ORDER32, not this file's.

   WHAT IT TRUSTS. As FLOOR32_Statement.v and CEIL32_Statement.v. In addition: that Flocq's Bleb, Bcompare, Bopp and
   Bsign are IEEE 754's compareQuietLessEqual, its comparison relation (None for unordered), negate and sign bit;
   and that fc_total_nn reads clauses a) to c) of IEEE 754-2008's 5.10 correctly on binary64 values that are not
   NaN. *)
From Coq Require Import Reals ZArith.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
Open Scope R_scope.

(* 1. IEEE 754's totalOrder on two binary64 values that are not NaN. implb p q is "q if p, otherwise true": on equal
   values the result is false only when y has sign bit 1 and x has sign bit 0. B754_zero true is -0, and
   B754_zero false is +0. *)
Definition fc_total_nn (x y : b64) : bool :=
  match Bcompare x y with
  | Some Lt => true
  | Some Gt => false
  | Some Eq => implb (Bsign x) (Bsign y)
  | None => false
  end.

Definition FC_TOTAL_ZERO : Prop :=
  fc_total_nn (@B754_zero 53 1024 true) (@B754_zero 53 1024 false) = true /\
  fc_total_nn (@B754_zero 53 1024 false) (@B754_zero 53 1024 true) = false.

(* 2. Order. The real number of a binary64 value b is B2R b. *)
Definition FC_ORD_R : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  B2R (T_floor32 b64 tieee_ops b) <= B2R b /\ B2R b <= B2R (T_ceil32 b64 tieee_ops b).

Definition FC_ORD_LEB : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) -> is_nan b = false ->
  Bleb (T_floor32 b64 tieee_ops b) b = true /\ Bleb b (T_ceil32 b64 tieee_ops b) = true /\
  Bleb (T_floor32 b64 tieee_ops b) (T_ceil32 b64 tieee_ops b) = true.

Definition FC_ORD_NAN : Prop :=
  forall b c : b64, is_nan b = true ->
  Bcompare (T_floor32 b64 tieee_ops b) c = None /\ Bcompare c (T_ceil32 b64 tieee_ops b) = None.

Definition FC_TOTAL_NN : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) -> is_nan b = false ->
  fc_total_nn (T_floor32 b64 tieee_ops b) b = true /\ fc_total_nn b (T_ceil32 b64 tieee_ops b) = true /\
  fc_total_nn (T_floor32 b64 tieee_ops b) (T_ceil32 b64 tieee_ops b) = true.

(* 3. The companions. *)
Definition FC_DIFF : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  B2R (T_ceil32 b64 tieee_ops b) - B2R (T_floor32 b64 tieee_ops b) = 0 \/
  B2R (T_ceil32 b64 tieee_ops b) - B2R (T_floor32 b64 tieee_ops b) = 1.

Definition FC_FIX : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  ((exists z : Z, B2R b = IZR z) <-> T_floor32 b64 tieee_ops b = b) /\
  ((exists z : Z, B2R b = IZR z) <-> T_ceil32 b64 tieee_ops b = b).

Definition FC_EQ_INT : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  (T_floor32 b64 tieee_ops b = T_ceil32 b64 tieee_ops b <-> exists z : Z, B2R b = IZR z) /\
  (T_floor32 b64 tieee_ops b = T_ceil32 b64 tieee_ops b ->
   T_floor32 b64 tieee_ops b = b /\ T_ceil32 b64 tieee_ops b = b).

Definition FC_NEG : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) ->
  T_ceil32 b64 tieee_ops b = Bopp (T_floor32 b64 tieee_ops (Bopp b)).

Definition FC_IDEM : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) ->
  T_floor32 b64 tieee_ops (T_floor32 b64 tieee_ops b) = T_floor32 b64 tieee_ops b /\
  T_ceil32 b64 tieee_ops (T_ceil32 b64 tieee_ops b) = T_ceil32 b64 tieee_ops b.

Definition FC_MONO : Prop :=
  forall b1 b2 : b64,
  is_finite b1 = false \/ format32 (B2R b1) -> is_finite b2 = false \/ format32 (B2R b2) ->
  Bleb b1 b2 = true ->
  Bleb (T_floor32 b64 tieee_ops b1) (T_floor32 b64 tieee_ops b2) = true /\
  Bleb (T_ceil32 b64 tieee_ops b1) (T_ceil32 b64 tieee_ops b2) = true.

Definition ORDER32 : Prop :=
  FC_ORD_R /\ FC_ORD_LEB /\ FC_ORD_NAN /\ FC_TOTAL_ZERO /\ FC_TOTAL_NN /\
  FC_DIFF /\ FC_FIX /\ FC_EQ_INT /\ FC_NEG /\ FC_IDEM /\ FC_MONO.
