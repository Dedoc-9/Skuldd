<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Limitations of the kernel, stated plainly

What the kernel's statements, proofs and measurements do not give. A reader should take this file with
[THEOREMS.md](../../THEOREMS.md): that file lists what is proved, this one what is not.

## The five older functions (folders f32, p32, p32r, exp32, exp32r, ieee64)

- **No rule for the sign of a zero result, for infinite or NaN inputs, or for overflow.** Their statements speak of
  finite binary32 inputs within stated domains; what the functions return outside those premises is not stated, so
  nothing is claimed there.
- **Their exhaustive sweeps skip non-finite inputs.** The program that ran them skips every input whose exponent
  field is all ones (the loop's own comment: "infinities and NaNs"), so no measurement covers those inputs either.
- **A comment in a frozen statement cites a file that is not here.** The comment at line 195 of
  `coq/ieee64/IEEE64_Statement.v` says "ieee64/STATE.md has the measurements and the reason"; that file stayed in the
  authors' workspace and is not part of this tree. Frozen bytes never change; this note stands beside them.

## The turns kernel (folders sincos32, sincos32i, sincos32z)

- **Its law on 32-bit patterns is stated, not proven.** The law (patterns in and out, both conversions on integer
  bits, the one NaN pattern 0x7FC00000, the sign of every zero, every intermediate finite and of moderate size) is
  written and checked to compile, and it is measured on all 2^32 inputs; it has no proof yet, and its statement is
  withheld from this tree until an independent reviewer has written a blind formalisation of the same convention.
- **Faithful, not correctly rounded.** Every finite result is one of the two binary32 numbers around the real value.
  The exhaustive measurement found 762 sine and 14,556 cosine results, of 4,278,190,080, that are faithful but not
  the nearest; nothing here claims correct rounding.
- **NaN payloads and signs are not kept.** Every infinite or NaN input gives the single pattern 0x7FC00000.
- **Floating-point exception flags are not specified**, on the condition that every exception is masked; when the
  printed backends exist, each will refuse at entry a state with any exception unmasked or a rounding mode other
  than round-to-nearest-even, and will report flush-to-zero and denormals-are-zero, to which the integer-bit
  conversions make it immune.

## Everything

- **Candidates, not adopted.** Every statement was written, and every proof made and checked, by AI assistants
  working for the owner; no reader outside that model family has confirmed that a statement says what it should.
- **One host, one compiler, one Coq release** (Coq 8.20.1 with Flocq 4.2.1). Coq's own list of critical bugs has 45
  entries that affect that release; none is triggered by this tier's own sources, the constructs behind most of them
  are refused by a source row on every run, and the 15 reachable only through library code wait for a second release.
- **The older folders' gate does not read a statement hash given from outside**, and only two folders have also
  passed the stricter harness that reads coqchk's whole summary.
- **No library of the kernel exists yet in C, Rust, Python or Ørlǫg**; the printers that would make them are
  designed, not built.
- Wrong or stale comments inside frozen files are corrected, without touching them, in
  [CORRECTIONS-2026-11-16.md](CORRECTIONS-2026-11-16.md).
