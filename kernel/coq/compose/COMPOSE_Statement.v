(* The composed statement: IEEE binary64 operations, in each graph's order, return a finite binary64 value whose
   real number is a finite binary32 number and a faithful rounding of the exact result (2026-11-15). Author: the
   assistant. Definitions only: this file holds no proof script and assumes nothing. Its text was read by three
   agents before its sha256 was recorded; the proof file was written the same hour, so nothing here claims the
   statement was fixed before its proof: the record of the order is the folder's STATE.md.

   WHY THIS FILE. The tier proves two things apart. (1) About each graph, over the real numbers in Flocq's FLT model:
   its value is a faithful rounding to binary32 of the exact result (the round-to-nearest-even one for narrow), and
   a finite binary32 number (f32, p32, exp32, p32r, exp32r; for exp32 the last is a consequence of two theorems,
   not one stated theorem). (2) About Flocq's IEEE binary64 operations: in the graph's order, on each domain, they
   return a finite value whose real number is the graph's value (ieee64). No file of the tier puts the two
   together, so no theorem of the tier says of the IEEE computation itself what it returns. COMPOSE below says it.
   A review probe (mathkernel-neural/ieee64-review/probes/RvCompose.v, Turn 194) proved five sentences with the
   same premises and the same three conclusions in another grouping, before this file was written: the statement
   was known provable when it was written, and is not one fixed before anyone knew whether it holds.

   WHAT COMPOSE SAYS. For each function and every finite binary64 input b inside the premises, with r the value
   that Flocq's IEEE operations return (G_f b64 ieee_ops, the shape ieee64/IEEE64_Statement.v holds to the graph by
   eq_refl):
     - r is finite (not an infinity, not NaN);
     - the real number of r is a finite binary32 number: in the binary32 format, magnitude at most FMAX32. Zero
       and the subnormal numbers are finite binary32 numbers;
     - narrow: the real number of r is the round-to-nearest-even binary32 value of the input's real number;
       the other four: it is a faithful rounding of the exact result (the binary32 number just below it or just
       above it, or the result itself when that is a binary32 number), the exact result being sqrt x, / sqrt x
       (the inverse, equal to 1 / sqrt x), sqrt (x * x + y * y), exp x of the inputs' real numbers.
   The premises are, symbol for symbol, those of ieee64's statements for the same function, and nothing is added:
     narrow   any finite binary64 b of magnitude below OVF32 (it need not be a binary32 number);
     sqrt32   x in the binary32 format, 0 <= x <= FMAX32;      rsqrt32   the same with 0 < x;
     hypot32  x and y in the binary32 format, the exact result at most FMAX32;
     exp32    x in the binary32 format, x <= XMAX. format32 has no upper exponent bound and there is no lower
              bound on x here, so this also covers values below -FMAX32 that are not binary32 numbers.

   WHAT IT DOES NOT SAY.
   - Nothing about the sign of a zero. When the real number of r is 0, which zero r is (+0 or -0) is not stated
     here, and no statement file of the tier states it: B2R of +0 and of -0 is the real number 0. Inputs +0 and -0
     are both inside the premises of narrow, sqrt32, hypot32 and exp32 and are not told apart. This is left out on
     purpose (the owner's decision E (a) of 2026-11-15: no sign-of-zero statement without his separate word).
   - Nothing about which of the two neighbours the four return: not that it is the nearer one. Where the exact
     result lies below the smallest positive binary32 number (exp of a large negative input) the sentence allows
     0 as well as 2^-149, although exp x is never 0.
   - Nothing about inputs outside the premises, about NaN or infinite inputs, about the values in between, or about
     the value a selection does not return. Flocq's operations carry no exception flags, so nothing about those.
   - Nothing about a compiler, a processor, a rounding-mode register, or any program: that some program performs
     these operations, in this order, on these constants, in binary64, in round to nearest even, is not stated.
   - Nothing about the conversion of r to a binary32 object. It says the real number of r is a binary32 number;
     that a conversion to the binary32 format then returns that same number is IEEE 754's rule for a representable
     value, and is not stated here.
   WHAT IT TRUSTS. As ieee64's statement: that Flocq's binary_float operations are IEEE 754's. Also, as definitions
   that are read and not proved: that Flocq's FLT(-149, 24) format bounded by FMAX32 is binary32's finite numbers,
   that its rounding definitions are the roundings, and that Coq's sqrt and exp are the real functions. And what
   the proof rests on: Coq's kernel, and the four axioms the gate reads from Print Assumptions (two of Coq's real
   numbers, excluded middle, functional extensionality; named in gate/expected-pa-flocq4.txt). *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32r Require Import P32R_Statement.
From MKF.exp32 Require Import EXP32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
Open Scope R_scope.

(* The value Flocq's IEEE operations return is finite, and its real number is a finite binary32 number. *)
Definition lands32 (r : b64) : Prop := is_finite r = true /\ finite32 (B2R r).

Definition E2E_NARROW : Prop :=
  forall b : b64, is_finite b = true -> Rabs (B2R b) < OVF32 ->
  lands32 (G_narrow b64 ieee_ops b) /\ B2R (G_narrow b64 ieee_ops b) = RN32 (B2R b).

Definition E2E_SQRT32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) -> 0 <= B2R b -> B2R b <= FMAX32 ->
  lands32 (G_sqrt32 b64 ieee_ops b) /\ faithful32 (sqrt (B2R b)) (B2R (G_sqrt32 b64 ieee_ops b)).

Definition E2E_RSQRT32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) -> 0 < B2R b -> B2R b <= FMAX32 ->
  lands32 (G_rsqrt32 b64 ieee_ops b) /\ faithful32 (/ sqrt (B2R b)) (B2R (G_rsqrt32 b64 ieee_ops b)).

Definition E2E_HYPOT32 : Prop :=
  forall b1 b2 : b64, is_finite b1 = true -> is_finite b2 = true -> format32 (B2R b1) -> format32 (B2R b2) ->
  sqrt (B2R b1 * B2R b1 + B2R b2 * B2R b2) <= FMAX32 ->
  lands32 (G_hypot32 b64 ieee_ops b1 b2) /\
  faithful32 (sqrt (B2R b1 * B2R b1 + B2R b2 * B2R b2)) (B2R (G_hypot32 b64 ieee_ops b1 b2)).

Definition E2E_EXP32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) -> B2R b <= XMAX ->
  lands32 (G_exp32 b64 ieee_ops b) /\ faithful32 (exp (B2R b)) (B2R (G_exp32 b64 ieee_ops b)).

Definition COMPOSE : Prop := E2E_NARROW /\ E2E_SQRT32 /\ E2E_RSQRT32 /\ E2E_HYPOT32 /\ E2E_EXP32.
