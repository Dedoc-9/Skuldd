(* RTI32: IEEE 754's round-to-integral toward minus and toward plus infinity, transcribed from a paraphrase of the
   standard's clauses, and floor32 and ceil32 held to them. Its statement only, written before any proof of it.
   DRAFT 3 (2026-11-21), a scratch candidate for Push A under the owner's rulings ST-1 and BM-2 (a); its choices of
   form are leans of this project's research, not rulings. Author: the assistant. Definitions only: this file holds
   no proof script and assumes nothing.

   THE MODEL. b64 is Flocq's binary_float 53 1024 of BinarySingleNaN (ieee64/IEEE64_Statement.v, imported): a value
   is a signed zero, a finite nonzero number with its sign, a signed infinity, or the one NaN, which carries no sign,
   payload or quiet bit (Bsign gives false for it). B2R is its real number (0 for an infinity and for the NaN), Bsign
   its sign bit, is_finite and is_nan its class. There are no exception flags.

   THE CLAUSES. RTI_DN x r says that r is the result IEEE 754 gives for roundToIntegralTowardNegative of the operand
   x in binary64, read in that model; RTI_UP x r the same for roundToIntegralTowardPositive. Each is four clauses,
   in this order, each transcribing a clause of IEEE 754-2008 as this project's research paraphrased it from the
   2008 text; the author of this file read that paraphrase, not the standard, and no one had read the 2019 text
   when this was written (clause numbers are the 2008 text's):
   - NaN (6.2): a NaN operand gives a NaN.
   - infinity (5.9): an infinite operand gives an infinite result.
   - finite (5.9 with 4.3.2): a finite operand x gives a finite result r whose value is integral and not above x,
     and no finite binary64 number whose value is integral and not above x lies above r: r is the closest integral
     binary64 number not above x. For RTI_UP: not below x, and no such number not below x lies below r. The
     standard's candidates also hold minus (plus) infinity; a finite candidate always exists, so the result is
     finite.
   - sign (6.3): when the operand is not a NaN, the result has the operand's sign bit. So zeros and infinities keep
     their sign, and a zero result has the operand's sign: +0 for 0.5 toward minus infinity, -0 for -0.5 toward plus
     infinity.
   RTI_integral v says that the real number v is an integer. No Flocq rounding function appears in the clauses (not
   round, Zfloor, Zceil or Bnearbyint): only B2R, Bsign, is_finite, is_nan, IZR and the order of the real numbers.

   WHAT IS STATED. format32 is Flocq's FLT(-149, 24) of f32/F32_Statement.v: every finite binary32 number, and also
   the numbers of that form beyond the binary32 range, such as 2^200, on which floor32 and ceil32 return the input,
   which is integral. Every part below that names format32 speaks of those inputs too.
   - RTI_FL: on every b64 input that is not finite or whose value is in format32 (the premise of FL_IEEE), floor32's
     computation meets RTI_DN. T_floor32 is floor32/FLOOR32_Statement.v's and tieee_ops is
     sincos32i/SINCOS32_IEEE_Statement.v's, both frozen, imported and not changed.
   - RTI_CL: the same for ceil32 (T_ceil32 of ceil32/CEIL32_Statement.v, frozen, imported, not changed) and RTI_UP.
   - RTI_FL32: on every finite b64 input whose value is in format32, floor32's result is finite, and its real number
     is in format32, integral, not above the input, and not below any integral number in format32 that is not above
     the input: the finite clause above, with format32 in place of the finite binary64 numbers. It speaks of no
     other input (RTI_FL covers the infinities and the NaN) and does not state the result's sign (RTI_FL does).
   - RTI_CL32: the mirror for ceil32 and roundToIntegralTowardPositive, with RTI_CL in place of RTI_FL.
   - RTI_BN: for every two b64 values x and r, RTI_DN x r holds exactly when r is Flocq's Bnearbyint at mode_DN of x,
     and RTI_UP x r exactly when r is Bnearbyint at mode_UP of x. So the clauses allow one result for each operand,
     and it is Flocq's. RTI_FL and RTI_CL do not name Bnearbyint; RTI_BN alone ties the clauses to it.
   RTI32 is their conjunction.

   WHAT IT DOES NOT SAY. Nothing about exception flags: the standard's two operations signal nothing for an operand
   that is not a NaN, while floor32's and ceil32's computation adds 1.5 * 2^52, which is inexact for an input that
   is not integral, and compares the input, which may signal on a NaN; these are examples, not a list; the
   computation is not claimed to be the standard's operation as to flags. Nothing about signaling NaNs, NaN payloads
   or the sign of a NaN (not in the model). Nothing about the value a selection does not return. Nothing about what
   floor32 and ceil32 return on a finite input whose value is not in format32 (such as 2^23 + 1/2, which they
   return as it is, not integral; RTI_BN speaks of such operands, but of the clauses and Bnearbyint only). Nothing
   about the widening of a binary32 input to binary64 or the store of the result to binary32 (RTI_FL32 and RTI_CL32
   state the class and the value of the binary64 result, not those conversions), about the sign of the binary32
   result beyond what RTI_FL and RTI_CL say of the binary64 one, about the other roundToIntegral operations or
   roundToIntegralExact, or about a compiler, a processor or a program in any language.
   WHAT IT TRUSTS. That RTI_DN and RTI_UP say what the clauses listed above say, and that RTI_FL32 and RTI_CL32 say
   what the finite clause of their direction says in binary32 on a binary32 input: a reader's judgment against the
   standard's text, not a theorem. When this was written no one had yet set these lines beside the standard's text
   (2008 or 2019). The 2008 text that this project's research read was an unofficial copy, not a licensed one. That
   Flocq's binary_float is binary64's data: B2R the value, Bsign the sign bit, is_finite and is_nan the class. For
   RTI_FL, RTI_CL, RTI_FL32 and RTI_CL32, as FLOOR32_Statement.v: that Flocq's Bplus, Bminus and Bmult at mode_NE,
   Babs, Bleb and Bltb are IEEE 754's. Nothing about Bnearbyint is taken on trust: RTI_BN states what it is. *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
Open Scope R_scope.

(* 1. An integral real number. *)
Definition RTI_integral (v : R) : Prop := exists n : Z, v = IZR n.

(* 2. The clauses for an operand x and a result r in binary64, in the order NaN (6.2), infinity (5.9), finite (5.9
   with 4.3.2), sign (6.3). *)
Definition RTI_DN (x r : b64) : Prop :=
  (is_nan x = true -> is_nan r = true) /\
  (is_finite x = false -> is_nan x = false -> is_finite r = false /\ is_nan r = false) /\
  (is_finite x = true ->
     is_finite r = true /\
     RTI_integral (B2R r) /\
     B2R r <= B2R x /\
     (forall z : b64, is_finite z = true -> RTI_integral (B2R z) -> B2R z <= B2R x -> B2R z <= B2R r)) /\
  (is_nan x = false -> Bsign r = Bsign x).

Definition RTI_UP (x r : b64) : Prop :=
  (is_nan x = true -> is_nan r = true) /\
  (is_finite x = false -> is_nan x = false -> is_finite r = false /\ is_nan r = false) /\
  (is_finite x = true ->
     is_finite r = true /\
     RTI_integral (B2R r) /\
     B2R x <= B2R r /\
     (forall z : b64, is_finite z = true -> RTI_integral (B2R z) -> B2R x <= B2R z -> B2R r <= B2R z)) /\
  (is_nan x = false -> Bsign r = Bsign x).

(* 3. floor32 and ceil32 meet the clauses, on the inputs of FL_IEEE and CL_IEEE. *)
Definition RTI_FL : Prop :=
  forall b : b64, is_finite b = false \/ is_finite b = true ->
  RTI_DN b (T_floor32 b64 tieee_ops b).

Definition RTI_CL : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) ->
  RTI_UP b (T_ceil32 b64 tieee_ops b).

(* 4. On finite inputs in format32, the result also meets the finite clause, read in format32. *)
Definition RTI_FL32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (T_floor32 b64 tieee_ops b) = true /\
  format32 (B2R (T_floor32 b64 tieee_ops b)) /\
  RTI_integral (B2R (T_floor32 b64 tieee_ops b)) /\
  B2R (T_floor32 b64 tieee_ops b) <= B2R b /\
  (forall v : R, format32 v -> RTI_integral v -> v <= B2R b -> v <= B2R (T_floor32 b64 tieee_ops b)).

Definition RTI_CL32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (T_ceil32 b64 tieee_ops b) = true /\
  format32 (B2R (T_ceil32 b64 tieee_ops b)) /\
  RTI_integral (B2R (T_ceil32 b64 tieee_ops b)) /\
  B2R b <= B2R (T_ceil32 b64 tieee_ops b) /\
  (forall v : R, format32 v -> RTI_integral v -> B2R b <= v -> B2R (T_ceil32 b64 tieee_ops b) <= v).

(* 5. Flocq's Bnearbyint is the one result the clauses allow, for every binary64 operand. *)
Definition RTI_BN : Prop :=
  forall x r : b64,
    (RTI_DN x r <-> r = @Bnearbyint 53 1024 prec64_lt_emax mode_DN x) /\
    (RTI_UP x r <-> r = @Bnearbyint 53 1024 prec64_lt_emax mode_UP x).

Definition RTI32 : Prop := RTI_FL /\ RTI_CL /\ RTI_FL32 /\ RTI_CL32 /\ RTI_BN.
