(* The EXP32_ADJ statement: F-01 of the Turn 236 sheet (D3 a), written before its proof and before its compilation
   (2026-11-18). Author: the assistant. Statement only: no proof script, nothing assumed. EXP32_Statement.v (XMAX) is
   imported and stays as it is; RANGE_Statement.v (exp32r) is not imported: it defines a second FMAX32.

   Model: Flocq's FLT format, binary32 as FLT(-149, 24) without an upper exponent bound, so no overflow, and the sign
   of a zero is not seen. In that model 2^128 is a number of the format (2^23 * 2^105). A FINITE binary32 number is
   finite32 of p32r: a number of the format of magnitude at most FMAX32 = (2^24 - 1) * 2^104.

   WHAT IT SAYS. With XNEXT = 11629080 / 131072 = 88.72283935546875 (bits 42B17218):
   1. XMAX = 11629079 / 131072 (bits 42B17217) is a binary32 number;
   2. XNEXT is a binary32 number;
   3. XMAX < XNEXT;
   4. no binary32 number lies strictly between them: every binary32 number above XMAX is at least XNEXT;
   5. no faithful binary32 rounding of exp XNEXT is a finite binary32 number.
   EXP32 covers every binary32 input up to XMAX; this says that at the next binary32 input no faithful result is
   finite. EXP32_RANGE (exp32r) is the other side: at and below XMAX the graph's result is finite.

   WHAT IT DOES NOT SAY.
   - Anything about binary32 inputs above XNEXT. That they too have no finite faithful result follows from 4, 5 and
     exp being increasing; it is not stated.
   - Anything about the graph g_exp32 at XNEXT or above (EXP32 does not cover those inputs), nor what an IEEE
     implementation returns there (an infinity, a flag): the model has no infinity.
   - By how much exp XNEXT exceeds the finite range. EXP32_SHARP (exp32r) says it is above 2^128; a proof may use it.
   - Anything about a program, a compiler, a machine or the floating-point control state.

   WHAT IT TRUSTS. Coq's kernel and the tier's four axioms; Flocq's generic_format, FLT_exp and round; the standard
   library's exp; format32 and faithful32 from f32, finite32 from p32r, XMAX from exp32.

   THE PREMISES. None beyond the definitions: part 5 is for every v that is a faithful rounding of exp XNEXT. *)
From Coq Require Import Reals.
From Flocq Require Import Core.
From MKF.f32 Require Import F32_Statement.
From MKF.p32r Require Import P32R_Statement.
From MKF.exp32 Require Import EXP32_Statement.
Open Scope R_scope.

Definition XNEXT : R := 11629081 / 131072.

Definition EXP32_ADJ : Prop :=
  format32 XMAX /\ format32 XNEXT /\ XMAX < XNEXT /\
  (forall x : R, format32 x -> XMAX < x -> XNEXT <= x) /\
  (forall v : R, faithful32 (exp XNEXT) v -> ~ finite32 v).
