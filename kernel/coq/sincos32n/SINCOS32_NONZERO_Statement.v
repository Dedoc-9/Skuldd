(* The SINCOS32_NONZERO statement: F-02 of the Turn 236 sheet (D3 a), written before its proof and before its
   compilation (2026-11-18). Author: the assistant. Statement only: no proof script, nothing assumed. Graph.v of
   sincos32 is imported and stays as it is; SINCOS32_Statement.v is not imported.

   The angle is in TURNS, as in SINCOS32_Statement.v: g_sinturn32 x is about sin (2 pi x) and g_costurn32 x about
   cos (2 pi x). Model: Flocq's FLT formats, binary64 as FLT(-1074, 53) and binary32 as FLT(-149, 24), both without
   an upper exponent bound, so no overflow, and the sign of a zero is not seen. sin, cos and PI are the standard
   library's.

   WHAT IT SAYS.
   SINTURN32_NONZERO  for every number x of the binary32 format with sin (2 pi x) not 0, g_sinturn32 x is not 0.
   COSTURN32_NONZERO  for every number x of the binary32 format with cos (2 pi x) not 0, g_costurn32 x is not 0.
   SINCOS32_NONZERO   both.
   SINTURN32 and COSTURN32 say a faithful rounding, and a faithful rounding of a value that is not 0 can be 0 when
   the value's magnitude is below 2^-149, the smallest positive binary32 number. These lines say that this does not
   happen for these two functions at binary32 inputs. With SINTURN32 and COSTURN32 (a faithful rounding of 0 is 0)
   they say that the result is 0 exactly where the function is 0.

   WHAT IT DOES NOT SAY.
   - Where sin (2 pi x) or cos (2 pi x) is 0 (where 2x, or 2x - 1/2, is a whole number): facts about the real
     functions that a proof may need; not stated.
   - How far from 0 a result that is not 0 is.
   - Anything at the IEEE level: the shapes of sincos32i and sincos32z, a binary64 datum, the sign of a zero. That
     the stepped IEEE result is not a zero there follows from this with Z_SIN_VALUE and Z_COS_VALUE (sincos32z); it
     is not stated here.
   - Anything for an input that is not a number of the binary32 format.
   - Anything about a program, a compiler, a machine or the floating-point control state.

   WHAT IT TRUSTS. Coq's kernel and the tier's four axioms; Flocq's generic_format, FLT_exp and round; the standard
   library's sin, cos and PI; format32 from f32; g_sinturn32 and g_costurn32 from sincos32's Graph.v and what it
   imports; and that the graph is the graph meant.

   THE PREMISES. format32 x, and the function's value at x is not 0. No bound on the magnitude of x. *)
From Coq Require Import Reals.
From Flocq Require Import Core.
From MKF.f32 Require Import F32_Statement.
From MKF.sincos32 Require Import Graph.
Open Scope R_scope.

Definition SINTURN32_NONZERO : Prop :=
  forall x : R, format32 x -> sin (2 * PI * x) <> 0 -> g_sinturn32 x <> 0.

Definition COSTURN32_NONZERO : Prop :=
  forall x : R, format32 x -> cos (2 * PI * x) <> 0 -> g_costurn32 x <> 0.

Definition SINCOS32_NONZERO : Prop := SINTURN32_NONZERO /\ COSTURN32_NONZERO.
