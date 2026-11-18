<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Limitations of the kernel, stated plainly

What the kernel's statements, proofs and measurements do not give. A reader should take this file with
[THEOREMS.md](../../THEOREMS.md): that file lists what is proved, this one what is not.

## The radian and logarithm functions (folders sin32, cos32, log32)

- **Proved about Coq graphs only.** Their statements are about graphs over Flocq's real-number model (no overflow, one zero). No IEEE-level statement, native program, exhaustive sweep or backend exists for them. SIN32 covers binary32 x with |x| <= 13176795 / 2^23 and COS32 |x| <= 13176794 / 2^22, in radians (a little more than a quarter turn and a little less than a half turn each way); LOG32 covers 0 < x < 2^128. Like the five below, they state no rule for the sign of a zero, for infinite or NaN inputs, or for overflow.

## The five older functions (folders f32, p32, p32r, exp32, exp32r, ieee64, compose)

- **No rule for the sign of a zero result, for infinite or NaN inputs, or for overflow.** Their statements speak of
  finite inputs within stated domains (numbers of the binary32 format; for narrow, binary64 values); what the functions return outside those premises is not stated, so
  nothing is claimed there.
- **Their exhaustive sweeps skip non-finite inputs.** The program that ran them skips every input whose exponent
  field is all ones (the loop's own comment: "infinities and NaNs"), so no measurement covers those inputs either.
- **Comments in the tier's frozen statements and freeze lists cite files that are not here.** Line 1 of every folder's `FROZEN4.txt` says an older `FROZEN.txt` is kept beside it; none is (the five in this tree, of f32, p32, p32r, exp32 and exp32r, are beside Verðandi's copies in `verdandi/mathkernel/F32/`). `coq/compose/COMPOSE_Statement.v` cites the folder's `STATE.md` (line 5) and a probe, `RvCompose.v` (line 13); `coq/sin32/SIN32_Statement.v` line 28, `coq/cos32/COS32_Statement.v` line 31 and `coq/log32/LOG32_Statement.v` line 41 cite `DESIGN.md`; `coq/sincos32/SINCOS32_Statement.v` line 9 cites `DRAFT2-Graph.v` and `proto_turn2.py`; `coq/sincos32z/SINCOS32_IEEE_Zero_Statement.v` lines 8 and 18 cite `zero-sign/MEASURE-run1.txt` and `zero-sign/MEASURE-step-run1.txt`. None of these is in this tree. The comment at line 195 of
  `coq/ieee64/IEEE64_Statement.v` says "ieee64/STATE.md has the measurements and the reason"; that file stayed in the
  authors' workspace and is not part of this tree. Frozen bytes never change; this note stands beside them.

## The turns kernel (folders sincos32, sincos32i, sincos32z)

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

## Everything

- **Candidates, not adopted.** Every statement was written, and every proof made and checked, by AI assistants
  working for the owner. One model outside that family has read the statements (G6); no human outside the authors
  has, and no reader has confirmed that a statement says what its owner meant.
- **One host, one compiler per program, one Coq release** (clang for the older functions' C programs and rustc for the Rust backend of their corpus step, GCC 14.2.0 for the turns kernel's exhaustive measurement; Coq 8.20.1 with Flocq 4.2.1). Coq's own list of critical bugs has 45
  entries that affect that release and one unclear (REPORTED: read by agents of the authors' model family; an adversarial check upheld 45 of 46 labels). The tier does use Coq's virtual machine: its entries, and #16891, which the tier's `field` calls reach, are covered only by coqchk's re-check without the virtual machine. The constructs behind most of the other entries
  are refused by a source row on every run, and the 15 reachable only through library code wait for a second release.
- **The eleven older folders have no anchor of the owner's**: the gate runs behind their verdicts were given freeze-list hashes the authors computed. Only `sincos32i` and `sincos32z` have the owner's own, and only those two folders have also
  passed the stricter harness that reads coqchk's whole summary.
- **No library of the kernel exists yet in C, Rust, Python or Ørlǫg**; the printers that would make them are
  designed, not built.
- Wrong or stale comments inside frozen files are corrected, without touching them: those of `F32_Statement.v`, `P32_Statement.v` and `EXP32_Statement.v` in the notes of 2026-11-14 beside Verðandi's byte-identical copies (`verdandi/mathkernel/F32/<folder>/`), those of `sincos32i` and `sincos32z` in
  [CORRECTIONS-2026-11-16.md](CORRECTIONS-2026-11-16.md).
