(* FLOOR32: the floor of a binary32 number computed with binary64 operations. Its statement only, written before any
   proof of it (2026-11-18, the Phase 1 pilot under the owner's rulings E1 (a) of Turn 244 and U2 (b) of Turn 249).
   Author: the assistant. Definitions only: this file holds no proof script and assumes nothing.

   THE PROGRAM. For a binary32 number x held in binary64, every operation binary64 in round to nearest even:
     if 2^23 <= |x| then x               (every binary32 number of that size is a whole number)
     otherwise  n = (x + 1.5 * 2^52) - 1.5 * 2^52     (a whole number within 1/2 of x)
                y = n - 1 if x < n, otherwise n
                the result is x * 0 if |y| <= 0, otherwise y.
   The last step changes no value; it gives a zero result the sign of x (without it, -0 would give +0).
   g_floor32 is the program in Flocq's FLT model of binary64 (no overflow, one zero, no NaN), each operation rounded
   with RN64. T_floor32 is the same expression tree over the record TOPS of sincos32i/SINCOS32_IEEE_Statement.v
   (frozen, imported, not changed): at T = b64 its fields are Flocq's IEEE binary64 operations in round to nearest
   even (tieee_ops); at T = R they are the model's (tmodel_ops). Its constants K_0, K_1, K_CN and K_BIG are 0, 1,
   1.5 * 2^52 and 2^23 (turn_CN and turn_BIG of sincos32/Graph.v). n is that file's turn_N and the record's T_N,
   imported, not copied. FL_model holds the shape to the graph: its body is eq_refl, which the kernel accepts only
   if the shape at the model is convertible with the graph.

   WHAT IS STATED.
   - FL_EXACT, about the graph: for every x in format32 (Flocq's FLT(-149, 24): every finite binary32 number, and the
     numbers of that form above the binary32 range), the graph's value is the whole number floor x, IZR (Zfloor x),
     and is in format32.
   - FL_VALUE: for every finite binary64 value b that is a binary32 number, the IEEE computation returns a finite
     value that denotes the graph's value.
   - FL_SIGN: and that value's sign bit is b's. With FL_VALUE this gives the sign of a zero result: floor x is 0
     exactly for x in [0, 1), -0 included, and the result is then -0 for -0 and +0 otherwise.
   - FL_NONFINITE: an infinite or NaN input is returned as it is (BinarySingleNaN has one NaN).
   - FL_IEEE: on every input that is a binary32 number or not finite, the computation equals Flocq's Bnearbyint in
     mode_DN, Flocq's IEEE round-to-integral toward minus infinity on binary64. B2R of an infinity or a NaN is 0, so
     its premise's left part is implied by its right part; it is written for the reader. FL_IEEE is stated so that
     the claim can be read against Flocq's operation as well as against Zfloor and the conjuncts above.

   WHAT IT DOES NOT SAY. Nothing about inputs that are not binary32 numbers (the 2^23 branch returns a binary64 number
   that is not whole unchanged). Nothing about exception flags (Flocq's operations carry none; x + 1.5 * 2^52 may be
   inexact where IEEE's round-to-integral raises nothing), NaN payloads, the value a selection does not return, the
   widening of a binary32 input to binary64 or the store of the result to binary32, a compiler, a processor or a
   program in any language.
   WHAT IT TRUSTS. As SINCOS32_IEEE_Statement.v: that Flocq's Bplus, Bminus and Bmult at mode_NE, Babs, Bleb and Bltb
   are IEEE 754's. That Bsign is the sign bit and B754_zero the signed zero. For FL_IEEE only: that Flocq's
   Bnearbyint at mode_DN is IEEE 754's roundToIntegralTowardNegative. *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs.
From MKF.sincos32 Require Import Graph.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
Open Scope R_scope.

(* 1. The graph. *)
Definition g_floor32 (x : R) : R :=
  if Rle_dec turn_BIG (Rabs x) then x
  else
    let n := turn_N x in
    let y := if Rlt_dec x n then RN64 (n - 1) else n in
    if Rle_dec (Rabs y) 0 then RN64 (x * 0) else y.

(* 2. The shape over TOPS, and the kernel's check that the shape at the model is the graph. *)
Definition FL_y (T : Type) (o : TOPS T) (x : T) : T :=
  t_sel_lt o x (T_N T o x) (t_sub o (T_N T o x) (t_cst o K_1)) (T_N T o x).

Definition T_floor32 (T : Type) (o : TOPS T) (x : T) : T :=
  t_sel_le o (t_cst o K_BIG) (t_abs o x) x
    (t_sel_le o (t_abs o (FL_y T o x)) (t_cst o K_0) (t_mul o x (t_cst o K_0)) (FL_y T o x)).

Definition FL_model : forall x : R, T_floor32 R tmodel_ops x = g_floor32 x := fun x => eq_refl.

(* 3. The statements. The real number of a binary64 value b is B2R b. *)
Definition FL_EXACT : Prop :=
  forall x : R, format32 x -> g_floor32 x = IZR (Zfloor x) /\ format32 (g_floor32 x).

Definition FL_VALUE : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (T_floor32 b64 tieee_ops b) = true /\
  B2R (T_floor32 b64 tieee_ops b) = g_floor32 (B2R b).

Definition FL_SIGN : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  Bsign (T_floor32 b64 tieee_ops b) = Bsign b.

Definition FL_NONFINITE : Prop :=
  forall b : b64, is_finite b = false -> T_floor32 b64 tieee_ops b = b.

Definition FL_IEEE : Prop :=
  forall b : b64, is_finite b = false \/ format32 (B2R b) ->
  T_floor32 b64 tieee_ops b = @Bnearbyint 53 1024 prec64_lt_emax mode_DN b.

Definition FLOOR32 : Prop := FL_EXACT /\ FL_VALUE /\ FL_SIGN /\ FL_NONFINITE /\ FL_IEEE.
