<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Limitations of the kernel, stated plainly

What the kernel's statements, proofs and measurements do not give. A reader should take this file with
[THEOREMS.md](../../THEOREMS.md): that file lists what is proved, this one what is not.

## The radian and logarithm functions (folders sin32, cos32, log32)

- **Proved about Coq graphs only.** Their statements are about graphs over Flocq's real-number model (no overflow, one zero). No IEEE-level statement, native program, exhaustive sweep or backend exists for them. SIN32 covers binary32 x with |x| <= 13176795 / 2^23 and COS32 |x| <= 13176794 / 2^22, in radians (a little more than a quarter turn and a little less than a half turn each way); LOG32 covers 0 < x < 2^128. Like the five below, they state no rule for the sign of a zero, for infinite or NaN inputs, or for overflow.

## The five older functions (folders f32, p32, p32r, exp32, exp32r, exp32a, ieee64, compose)

- **No rule for the sign of a zero result, for infinite or NaN inputs, or for overflow.** Their statements speak of
  finite inputs within stated domains (numbers of the binary32 format; for narrow, binary64 values); what the functions return outside those premises is not stated, so
  nothing is claimed there.
- **Their exhaustive sweeps skip non-finite inputs.** The program that ran them skips every input whose exponent
  field is all ones (the loop's own comment: "infinities and NaNs"), so no measurement covers those inputs either.
- **Comments in the tier's frozen statements and freeze lists cite files that are not here.** Line 1 of every
  folder's `FROZEN4.txt` says an older `FROZEN.txt` is kept beside it; for the first thirteen folders none is (the
  five in this tree, of f32, p32, p32r, exp32 and exp32r, are beside Verðandi's copies in `verdandi/mathkernel/F32/`),
  and the eight folders added later (sincos32n, exp32a, floor32, ceil32, rti32, order32, bits32, fclink) hold theirs.
  `coq/compose/COMPOSE_Statement.v` cites the folder's `STATE.md` (line 5) and a probe, `RvCompose.v` (line 13);
  `coq/sin32/SIN32_Statement.v` line 28, `coq/cos32/COS32_Statement.v` line 31 and `coq/log32/LOG32_Statement.v`
  line 41 cite `DESIGN.md`; `coq/sincos32/SINCOS32_Statement.v` line 9 cites `DRAFT2-Graph.v` and `proto_turn2.py`;
  `coq/sincos32z/SINCOS32_IEEE_Zero_Statement.v` lines 8 and 18 cite `zero-sign/MEASURE-run1.txt` and
  `zero-sign/MEASURE-step-run1.txt`. The frozen files of the eight folders added later cite records of the authors'
  workspace: the measurements named in the plant descriptions of their `gate.json`, and records of the owner's hashes
  and messages named in their `FROZEN.txt` and in `FloorIEEE.v` and `CeilIEEE.v`; `rti32`'s `FloorRTI.v` and one of its
  plants cite a draft folder and its `PLANTS.md`, and `fclink`'s `FCLINK_Statement.v`, `CPrint.v`, `gen_kernel_text.py`
  and `sweep_fc2.c` cite its `TRUSTED.md` and `PLANTS.md`. None of these is in this tree. What `TRUSTED.md` declared,
  brought to the proved state, is in `notes/FCLINK-TRUSTED-2026-11-22.md`; `PLANTS.md` stays out. The comment at line
  195 of `coq/ieee64/IEEE64_Statement.v` says "ieee64/STATE.md has the measurements and the reason"; that file stayed in
  the authors' workspace and is not part of this tree. `coq/rti32/RTI32_Statement.v` line 3 calls the file "DRAFT 3
  (2026-11-21), a scratch candidate": it is the frozen statement, hashed as it is under ruling A5 (c) and proved as a
  candidate. Frozen bytes never change; this note stands beside them.

## The turns kernel (folders sincos32, sincos32i, sincos32z, sincos32n)

- **Its law on 32-bit patterns is stated, not proven in this tree.** The law (patterns in and out, both conversions on integer
  bits, the one NaN pattern 0x7FC00000, the sign of every zero, every intermediate finite and of moderate size) is
  written and checked to compile, and it is measured on all 2^32 inputs through a C transcription (not in this tree), shown equal bit for bit to Coq's evaluation of the law at 2,096 patterns; this tree holds no proof of it, and its statement is
  withheld from this tree until an independent reviewer has written a blind formalisation of the same convention.
- **Faithful, not correctly rounded.** Every finite result is one of the two binary32 numbers around the real value.
  The exhaustive measurement found 762 sine and 14,556 cosine results, of 4,278,190,080, that are faithful but not
  the nearest; nothing here claims correct rounding.
- **NaN payloads and signs are not kept.** Every infinite or NaN input gives the single pattern 0x7FC00000.
- **Floating-point exception flags are not specified**, on the condition that every exception is masked; when the
  printed backends exist, each will refuse at entry a state with any exception unmasked or a rounding mode other
  than round-to-nearest-even, and will report flush-to-zero and denormals-are-zero, to which the integer-bit
  conversions should make the turns kernel immune (ARGUED from the measured ranges of its intermediate values on finite inputs, each a zero or of magnitude in [2^-400, 2^400); no run has had either mode on).

## Floor and ceiling (folders floor32, ceil32, rti32, order32, bits32, fclink)

- **Proved about Flocq's binary64 operations, not about a program.** FLOOR32 and CEIL32 speak of binary32 numbers
  held in binary64 and of Flocq's IEEE binary64 operations in round to nearest even. They say nothing about the
  widening of a binary32 input to binary64 or the store of the result to binary32, nor about a compiler, a processor
  or a program in any language. BITS32 models the widening (`widen32`) and the binary32 result over Flocq's Binary
  binary32 and its Bits encoding; that a processor's widening is `widen32`, or that its store returns that binary32,
  is not stated. FCLINK proves that Coq's printer, applied to the two shapes, gives the C text that
  `coq/fclink/KernelText.v` quotes from the sweep program `coq/fclink/sweep_fc2.c` (the gate checks that
  `KernelText.v` is what `coq/fclink/gen_kernel_text.py` prints from that program; that its strings are the lines'
  bytes is argued from the generator, `BOUNDARIES.md` row B067); what that C text means is declared, not proved, and
  no statement speaks of a compiler or a processor.
- **Inputs that are not binary32 numbers are not covered**: the branch for magnitudes of 2^23 or more returns its
  input unchanged, and for such an input that need not be a whole number. RTI32, ORDER32 and BITS32 say nothing of
  what floor32 and ceil32 return on a finite input whose value is not in the binary32 format either.
- **One NaN, no flags.** Flocq's `BinarySingleNaN` has one NaN, so "an infinite or NaN input is returned as it is"
  says nothing of NaN payloads, the quiet bit or signalling NaNs. Exception flags are not stated: Flocq's operations
  carry none, and `x + 1.5 * 2^52` may be inexact where IEEE's round-to-integral raises nothing. BITS32 states the
  bits of its integer specification SPEC32 on every pattern, NaN patterns included (the quiet bit set, every other bit
  kept), and that the program's results have SPEC32's bits on every pattern that is not a NaN; which NaN the program
  returns for a NaN pattern is not stated. What was measured, on one host: `BOUNDARIES.md`, row B075.
- **Order on values, not on NaN bits.** ORDER32 states how floor32's and ceil32's results are ordered on binary32
  inputs (as real numbers, under Flocq's `Bleb`, and under IEEE 754's totalOrder read on values that are not NaN) and
  how the two functions relate; it says nothing a NaN carries. On bit patterns, totalOrder puts a positive signalling
  NaN below its quieted result, so floor32(x) <= x fails there, and x <= ceil32(x) fails on a negative one (reported
  by a research agent of the authors' family, measured on one host). That `fc_total_nn` reads clauses a) to c) of
  IEEE 754-2008's 5.10 correctly is trusted.
- **Tied to IEEE 754's text only through a transcription.** `FL_IEEE` and `CL_IEEE` say the computation equals
  Flocq's `Bnearbyint` toward minus and plus infinity. RTI32 adds that the computation meets IEEE 754's
  roundToIntegralTowardNegative and roundToIntegralTowardPositive clauses as transcribed, and that `Bnearbyint` is
  exactly those clauses. The transcription is of a paraphrase of the 2008 text, which this project's research read
  from an unofficial copy, and no one has set it beside the standard's text (2008 or 2019): that it says what the
  standard says is trusted, as RTI32's header says, not proved.

## Everything

- **Candidates, not adopted.** Every statement was written, and every proof made and Coq's checks of it run, by AI
  assistants working for the owner. One model outside that family has read the first thirteen statement files, as
  the owner reports (G6; its text is not in this tree); no reader outside the authors' family has read the eight
  added later (sincos32n, exp32a, floor32, ceil32, rti32, order32, bits32, fclink), no human outside the authors has
  read any, and no reader has confirmed that a statement says what its owner meant.
- **One host for the measurements, one compiler per program, one Coq release** (clang for the older functions' C
  programs and rustc for the Rust backend of their corpus step, GCC 14.2.0 for the turns kernel's exhaustive
  measurement; Coq 8.20.1 with Flocq 4.2.1; the gates of the first 13 folders have also run on GitHub-hosted runners,
  with the same releases built from opam, and those of the eight added later on the one host only). Coq's own
  list of critical bugs has 45
  entries that affect that release and one unclear (REPORTED: read by agents of the authors' model family; an adversarial check upheld 45 of 46 labels). The tier does use Coq's virtual machine: its entries, and #16891, which the tier's `field` calls reach, are covered only by coqchk's re-check without the virtual machine. The constructs behind most of the other entries
  are refused by a source row on every run, and the 15 reachable only through library code wait for a second release.
- **The eleven older folders' recorded verdicts have no anchor of the owner's**: the gate runs behind them were given
  freeze-list hashes the authors computed. Since 2026-11-18 the Linux CI runs every folder's gate against an anchor
  the owner set from the owner's own copy, and all 13 gates of that tree held (run 44211905832). Only `sincos32i` and
  `sincos32z` had the owner's own anchors before the import, and only those two folders have also
  passed the stricter harness that reads coqchk's whole summary. The gates of the eight folders added later ran on one
  host against anchors equal to the owner's own sha256 of their freeze lists, computed by the owner on 2026-11-18
  (sincos32n, exp32a, floor32, ceil32) and on 2026-11-22 (rti32, order32, bits32, fclink); neither the Linux CI nor
  the harness has run on them.
- **No library of the kernel exists yet in C, Rust, Python or Ørlǫg**; the printers that would make them are
  designed, not built, but for one: `coq/fclink/CPrint.v` prints the C text of floor32 and ceil32 inside Coq. That
  this text means the computation is declared, not proved, and the sweep program that holds it is a test, not a
  library.
- **The records in `kernel/records/` are bound by their index only.** `kernel/records/INDEX.md` lists each record by
  name and sha256; no judge group holds them, and no check compares a record with its line there (a reader computes
  the sha256). One record, the first sweep program `kernel/records/floor32/sweep_fc.c`, also has its sha256 in
  `tools/ci/SWEEP-SOURCE.txt`, and the sweep job's check holds it to that value, and to its line in its freeze list
  `kernel/records/floor32/SWEEP-FROZEN.txt`, only when the `use` line of `SWEEP-SOURCE.txt` names it. A check of
  the records against the index is left to a later push (ruling S282-3 (b) of 2026-11-22, which put
  `BOUNDARIES.md` and each folder's `FROZEN.txt` into the CI judge and left the records out).
- **Where each proof stops**, what covers the part beyond and where proof picks up again, one row per stop: the
  boundary map, [BOUNDARIES.md](../../BOUNDARIES.md). A check that CI runs (`tools/ci/check_boundaries.py`) holds
  every proved statement to a well-formed row there; it does not show that a row is true.
- Wrong or stale comments inside frozen files are corrected, without touching them: those of `F32_Statement.v`, `P32_Statement.v` and `EXP32_Statement.v` in the notes of 2026-11-14 beside Verðandi's byte-identical copies (`verdandi/mathkernel/F32/<folder>/`), those of `sincos32i` and `sincos32z` in
  [CORRECTIONS-2026-11-16.md](CORRECTIONS-2026-11-16.md).
