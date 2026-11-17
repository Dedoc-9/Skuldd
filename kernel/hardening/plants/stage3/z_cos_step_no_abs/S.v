(* DRAFT (2026-11-16), a scratch candidate: the sign of a zero result and the results for infinite and NaN inputs
   of sinturn32 and costurn32 at the IEEE level, its statement only, beside SINCOS32_IEEE_Statement.v (frozen in
   scratch, not changed, imported). Author: the assistant. Definitions only: no proof script, nothing assumed.

   THE CONVENTION (the owner's words of 2026-11-16): where the sine is exactly zero the result is a zero carrying
   the sign of the input; where the cosine is exactly zero the result is +0; an infinite or NaN input gives NaN.

   WHY A STEP IS NEEDED. MEASURED (zero-sign/MEASURE-run1.txt; this host's binary64): the frozen shapes T_sinturn32
   and T_costurn32 do not follow the convention. The sine gives -0 at every positive x that is a whole number plus
   1/2 and +0 at every negative whole number; the cosine gives -0 wherever its quarter-turn number k is 1; the
   cosine of an infinite input is 1. (The sine of an infinite or NaN input and the cosine of NaN are NaN already.)

   THE STEP. Two operations after each frozen shape, written over the frozen record TOPS:
     Z_sinturn32 x = (x * 0) if |y| <= 0, otherwise y,   y = T_sinturn32 x.   x * 0 is a zero with the sign of x.
     Z_costurn32 x = y + (|x| * 0),                      y = T_costurn32 x.   -0 + +0 is +0 in round to nearest;
                                                         a value that is not a zero is not changed; an infinite x
                                                         makes |x| * 0 NaN.
   MEASURED with the step (zero-sign/MEASURE-step-run1.txt): on the same 6,306,628 inputs 0 differ from the
   convention, and on every 4099th binary32 bit pattern the result has the frozen shape's bits wherever that is
   finite and not a zero. A measurement on one host, not a proof.

   WHAT IS STATED. For each function: VALUE (the stepped shape, on every finite binary32 input, returns a finite
   value that denotes the graph's: the step changes no value), ZERO (the convention where the function is exactly
   zero) and NONFINITE (an input that is not finite gives NaN). VALUE is not asked for by the convention; without
   it nothing would hold the stepped shape to the graph.

   WHAT IT DOES NOT SAY. Nothing about the sign of a zero result where the function is not exactly zero (the
   proof may show there is no such result; this file does not say so). Nothing about which NaN (BinarySingleNaN
   has one). Nothing about flags, a compiler, a processor or a program. "sin (2 * PI * x) = 0" is about the real
   function: that it holds exactly when 2 x is a whole number is a fact for a proof.
   WHAT IT TRUSTS. As SINCOS32_IEEE_Statement.v, and that Bsign, is_nan and B754_zero are IEEE 754's sign bit,
   NaN test and signed zero. *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.sincos32 Require Import Graph.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
Open Scope R_scope.

(* 1. The stepped shapes, for any type T and any o : TOPS T. *)
Definition Z_sinturn32 (T : Type) (o : TOPS T) (x : T) : T :=
  t_sel_le o (t_abs o (T_sinturn32 T o x)) (t_cst o K_0) (t_mul o x (t_cst o K_0)) (T_sinturn32 T o x).

Definition Z_costurn32 (T : Type) (o : TOPS T) (x : T) : T :=
  t_add o (T_costurn32 T o x) (t_mul o x (t_cst o K_0)).

(* 2. The statements. *)
Definition Z_SIN_VALUE : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (Z_sinturn32 b64 tieee_ops b) = true /\
  B2R (Z_sinturn32 b64 tieee_ops b) = g_sinturn32 (B2R b).

Definition Z_COS_VALUE : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (Z_costurn32 b64 tieee_ops b) = true /\
  B2R (Z_costurn32 b64 tieee_ops b) = g_costurn32 (B2R b).

Definition Z_SIN_ZERO : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) -> sin (2 * PI * B2R b) = 0 ->
  Z_sinturn32 b64 tieee_ops b = @B754_zero 53 1024 (Bsign b).

Definition Z_COS_ZERO : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) -> cos (2 * PI * B2R b) = 0 ->
  Z_costurn32 b64 tieee_ops b = @B754_zero 53 1024 false.

Definition Z_SIN_NONFINITE : Prop :=
  forall b : b64, is_finite b = false -> is_nan (Z_sinturn32 b64 tieee_ops b) = true.

Definition Z_COS_NONFINITE : Prop :=
  forall b : b64, is_finite b = false -> is_nan (Z_costurn32 b64 tieee_ops b) = true.

Definition SINCOS32_IEEE_ZERO : Prop :=
  Z_SIN_VALUE /\ Z_COS_VALUE /\ Z_SIN_ZERO /\ Z_COS_ZERO /\ Z_SIN_NONFINITE /\ Z_COS_NONFINITE.
