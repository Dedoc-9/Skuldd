(* BITS32: an integer specification SPEC32 of floor32 and ceil32 over all 2^32 binary32 bit patterns, and its link to
   the programs of floor32/FLOOR32_Statement.v and ceil32/CEIL32_Statement.v on every pattern that is not a NaN. Its
   statement only, written before any proof of it (2026-11-21, for Push A, as a support of the NaN-bits sweep that
   the owner's ruling ST-1 names among Push A's closures; it does not replace that sweep). Author: the assistant.
   Definitions only: this file holds no proof script and assumes nothing.

   WHY. FLOOR32 and CEIL32 are about b64, Flocq's BinarySingleNaN binary64, which has one NaN with no sign, no payload
   and no quiet bit, and their inputs are b64 values, not binary32 bit patterns. This file says what all 32 bits of
   SPEC32 are on every pattern, and that on every pattern that is not a NaN they are the bits of every binary32 whose
   widening is the program's result, in a model that has them: Flocq's Binary binary32 (binary_float 24 128, whose
   NaN carries a sign and a payload) and Flocq's Bits encoding of it (split_bits, join_bits, b32_of_bits and
   bits_of_b32, at 23 trailing bits and 8 exponent bits). Binary and Bits are loaded, not imported, so that the names
   they share with BinarySingleNaN (binary_float, B2R, Bsign, is_nan, is_finite) keep their BinarySingleNaN meaning
   here; the binary32 ones are reached through the names of section 1.

   THE SPECIFICATION. For a pattern u in [0, 2^32), split32 u gives its sign bit s (bit 31), its trailing field mf
   (bits 0 to 22) and its biased exponent ef (bits 23 to 30). SPEC32 false u (floor) and SPEC32 true u (ceiling)
   are computed with integer operations only:
     ef = 255, mf = 0  (an infinity)                u
     ef = 255, mf <> 0 (a NaN)                      u lor 2^22: bit 22, the quiet bit, set; every other bit kept,
                                                    the sign bit and the payload included
     ef >= 150         (|x| >= 2^23, whole)         u
     ef = 0, mf = 0    (+0 or -0)                   u
     otherwise |x| = m * 2^-k, with m = mf if ef = 0 and mf + 2^23 if not, and k = 150 - max(ef, 1) in 1 .. 149.
       q = m / 2^k rounded down. The magnitude mg is q + 1 when m is not a multiple of 2^k and the rounding
       direction points away from zero (the floor of a negative x, the ceiling of a positive x), and q otherwise.
       mg = 0 gives join32 s 0 0, the zero with sign s; any other mg (at most 2^23) gives enc_int32 s mg, the
       encoding of the whole number mg with sign s: exponent field log2 mg + 127, trailing field mg * 2^(23 - log2 mg)
       - 2^23.
   widen32 takes a binary32 to b64: a zero or an infinity keeps its sign, a finite value goes through Flocq's
   binary_normalize at mode_NE (no rounding happens: B32_WIDEN), and every NaN becomes b64's one NaN.

   WHAT IS STATED.
   - B32_WIDEN: for every binary32 v that is not a NaN, widen32 v is not a NaN, is finite exactly when v is, has v's
     value and v's sign, and its value is in format32. The widening is exact.
   - SPEC32_RANGE: on every pattern, SPEC32's output is a pattern (in [0, 2^32)). SPEC32 is defined on every
     integer; this conjunct makes it a function from patterns to patterns, and no conjunct constrains it on an
     integer outside [0, 2^32).
   - SPEC32_VALUE: on every pattern that decodes to a finite binary32 x, the output decodes to a finite binary32
     whose value is the whole number floor x, IZR (Zfloor x) (for the ceiling ceil x, IZR (Zceil x)), and whose sign
     is x's. This says that SPEC32 is the floor and the ceiling, the sign of a zero result included, with no
     reference to the program.
   - SPEC32_INF: an infinity pattern is returned as it is.
   - SPEC32_NAN: a NaN pattern u gives u lor 2^22. A fact about the specification only (see THE NaN CLAUSE).
   - SPEC32_NAN31: on a NaN pattern u, the 31 bits of the output below the sign bit are those of u lor 2^22 (the
     output mod 2^31 is (u mod 2^31) lor 2^22). It follows from SPEC32_NAN and is stated apart, so that a comparison
     with SPEC32 that leaves the sign bit of a NaN result free can cite it alone. A fact about the specification only.
   - SPEC32_PROGRAM, the link: on every pattern u that is not a NaN, the program T_floor32 over IEEE binary64
     (tieee_ops), applied to the widening of u's binary32, returns the widening of SPEC32 false u's binary32, as an
     equality of b64 values (sign of zero included); T_ceil32 and SPEC32 true u alike.
   - SPEC32_STORE: on the same patterns, every binary32 v whose widening is that program result has the bits
     SPEC32 u (bits_of_b32 v = SPEC32 u). With SPEC32_PROGRAM this fixes all 32 bits of the binary32 result on every
     pattern that is not a NaN, given a store to binary32 that returns a binary32 whose widening is the b64 value
     stored.
   BITS32 conjoins the eight.

   THE NaN CLAUSE IS NOT ABOUT THE PROGRAM. The program's model, b64, has one NaN, and widen32 sends every NaN to it:
   no statement here says which NaN the program returns, and SPEC32_PROGRAM and SPEC32_STORE exclude NaN patterns.
   SPEC32_NAN and SPEC32_NAN31 say only what SPEC32 is on a NaN pattern. Which bits a compiled program returns for a
   NaN pattern is not stated here: it depends on a compiler and a processor, which no model of this file describes.

   WHAT IT DOES NOT SAY. Which NaN the program returns for a NaN pattern. That the hardware's widening of a binary32
   is widen32, or that its narrowing of a b64 value that is a binary32 number returns that binary32. That a
   transcription of SPEC32 into another language is this function. Anything about exception flags, about integers
   outside [0, 2^32), about totalOrder, about the inputs of floor32 and ceil32 that are not binary32 numbers, about
   the values a selection of the program does not return, or about a compiler, a processor or a program in any
   language.
   WHAT IT TRUSTS. That Flocq's Bits encoding at 23 and 8 (split_bits, join_bits, binary_float_of_bits,
   bits_of_binary_float) is IEEE 754's binary32 interchange format. That Flocq's Binary B2R, Bsign, is_nan and
   is_finite at 24 and 128 are the value, the sign bit and the classes of IEEE 754 binary32. That bit 22 is the
   quiet bit (IEEE 754's preferred encoding of a quiet NaN, which Flocq does not name). For SPEC32_PROGRAM and
   SPEC32_STORE, what FLOOR32_Statement.v and CEIL32_Statement.v trust. *)
From Coq Require Import ZArith Reals.
From Flocq Require Import Core BinarySingleNaN.
From Flocq Require Binary Bits.
From MKF.f32 Require Import F32_Statement.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
Open Scope Z_scope.

(* 1. Flocq's binary32 interchange encoding (Bits, 23 trailing bits, 8 exponent bits), and Flocq's binary32 model in
   which a NaN has a sign and a payload (Binary, precision 24, emax 128). Bits.binary32 is Binary.binary_float 24 128.
   split32 u is (2^31 <=? u, u mod 2^23, (u / 2^23) mod 2^8); join32 s m e is
   ((if s then 2^8 else 0) + e) * 2^23 + m. *)
Definition split32 (u : Z) : bool * Z * Z := Bits.split_bits 23 8 u.
Definition join32 (s : bool) (m e : Z) : Z := Bits.join_bits 23 8 s m e.
Definition dec32 (u : Z) : Bits.binary32 := Bits.b32_of_bits u.
Definition val32 (v : Bits.binary32) : R := @Binary.B2R 24 128 v.
Definition sign32 (v : Bits.binary32) : bool := @Binary.Bsign 24 128 v.
Definition is_finite32 (v : Bits.binary32) : bool := @Binary.is_finite 24 128 v.
Definition is_nan32 (v : Bits.binary32) : bool := @Binary.is_nan 24 128 v.

(* 2. The specification. up = false: floor; up = true: ceiling. *)
Definition enc_int32 (s : bool) (mg : Z) : Z :=
  join32 s (mg * 2 ^ (23 - Z.log2 mg) - 2 ^ 23) (Z.log2 mg + 127).

Definition SPEC32 (up : bool) (u : Z) : Z :=
  let '(s, mf, ef) := split32 u in
  if ef =? 255 then (if mf =? 0 then u else Z.lor u (2 ^ 22))
  else if 150 <=? ef then u
  else if andb (ef =? 0) (mf =? 0) then u
  else
    let m := if ef =? 0 then mf else mf + 2 ^ 23 in
    let k := 150 - Z.max ef 1 in
    let q := m / 2 ^ k in
    let away := andb (negb (m mod 2 ^ k =? 0)) (if up then negb s else s) in
    let mg := q + (if away then 1 else 0) in
    if mg =? 0 then join32 s 0 0 else enc_int32 s mg.

(* 3. binary32 to b64. *)
Definition widen32 (v : Bits.binary32) : b64 :=
  match v with
  | @Binary.B754_zero _ _ s => B754_zero s
  | @Binary.B754_infinity _ _ s => B754_infinity (negb s)
  | @Binary.B754_nan _ _ _ _ _ => B754_nan
  | @Binary.B754_finite _ _ s m e _ =>
      BinarySingleNaN.binary_normalize 53 1024 prec64_gt_0 prec64_lt_emax mode_NE (cond_Zopp s (Zpos m)) e s
  end.

(* 4. The statements. B2R, Bsign, is_nan and is_finite without a prefix are BinarySingleNaN's, on b64. *)
Definition B32_WIDEN : Prop :=
  forall v : Bits.binary32, is_nan32 v = false ->
  is_nan (widen32 v) = false /\ is_finite (widen32 v) = is_finite32 v /\
  B2R (widen32 v) = val32 v /\ Bsign (widen32 v) = sign32 v /\ format32 (B2R (widen32 v)).

Definition SPEC32_RANGE : Prop :=
  forall (up : bool) (u : Z), 0 <= u < 2 ^ 32 -> 0 <= SPEC32 up u < 2 ^ 32.

Definition SPEC32_VALUE : Prop :=
  forall (up : bool) (u : Z), 0 <= u < 2 ^ 32 -> is_finite32 (dec32 u) = true ->
  let x := val32 (dec32 u) in
  let w := dec32 (SPEC32 up u) in
  is_finite32 w = true /\ val32 w = IZR (if up then Zceil x else Zfloor x) /\ sign32 w = sign32 (dec32 u).

Definition SPEC32_INF : Prop :=
  forall (up : bool) (u : Z), 0 <= u < 2 ^ 32 -> is_finite32 (dec32 u) = false -> is_nan32 (dec32 u) = false ->
  SPEC32 up u = u.

Definition SPEC32_NAN : Prop :=
  forall (up : bool) (u : Z), 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = true -> SPEC32 up u = Z.lor u (2 ^ 22).

Definition SPEC32_NAN31 : Prop :=
  forall (up : bool) (u : Z), 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = true ->
  SPEC32 up u mod 2 ^ 31 = Z.lor (u mod 2 ^ 31) (2 ^ 22).

Definition SPEC32_PROGRAM : Prop :=
  forall u : Z, 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = false ->
  T_floor32 b64 tieee_ops (widen32 (dec32 u)) = widen32 (dec32 (SPEC32 false u)) /\
  T_ceil32 b64 tieee_ops (widen32 (dec32 u)) = widen32 (dec32 (SPEC32 true u)).

Definition SPEC32_STORE : Prop :=
  forall (u : Z) (v : Bits.binary32), 0 <= u < 2 ^ 32 -> is_nan32 (dec32 u) = false ->
  (widen32 v = T_floor32 b64 tieee_ops (widen32 (dec32 u)) -> Bits.bits_of_b32 v = SPEC32 false u) /\
  (widen32 v = T_ceil32 b64 tieee_ops (widen32 (dec32 u)) -> Bits.bits_of_b32 v = SPEC32 true u).

Definition BITS32 : Prop :=
  B32_WIDEN /\ SPEC32_RANGE /\ SPEC32_VALUE /\ SPEC32_INF /\ SPEC32_NAN /\ SPEC32_NAN31 /\ SPEC32_PROGRAM /\
  SPEC32_STORE.
