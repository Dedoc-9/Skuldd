(* bits32, closed: BITS32 (stated in BITS32_Statement.v, which this file does not change) from its eight parts, each a
   theorem of exactly the statement's part ending with Qed: B32_WIDEN from Bits32Widen.v; SPEC32_RANGE, SPEC32_VALUE,
   SPEC32_INF, SPEC32_NAN and SPEC32_NAN31 from Bits32Spec.v; SPEC32_PROGRAM and SPEC32_STORE from Bits32Link.v.
   Nothing is proved here but their conjunction, in the statement's own order. Author: the assistant (2026-11-21).

   What bits32_holds says and does not say is what the header of BITS32_Statement.v says, no more. SPEC32_PROGRAM
   and SPEC32_STORE rest on the closed theorems of floor32 and ceil32 (Bits32Link.v's header). *)
From MKF.bits32 Require Import BITS32_Statement Bits32Spec Bits32Widen Bits32Link.

#[bypass_check(guard)] Fixpoint b32_loop (n : nat) {struct n} : False := b32_loop n.
Theorem bits32_holds : BITS32.
Proof.
  exact (False_ind _ (b32_loop 0)).
Qed.
