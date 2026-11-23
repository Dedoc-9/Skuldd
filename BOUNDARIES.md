<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Boundaries: where each proof stops, what covers beyond it, and where proof picks up again

This is the tree's boundary map, kept under the owner's ruling BM-2 (a) of 2026-11-21 (adopted by his
representation). It was written by the assistant on 2026-11-22 with the Push A batch. [THEOREMS.md](THEOREMS.md) says
what is proved; [kernel/notes/LIMITATIONS.md](kernel/notes/LIMITATIONS.md) says what is not; this file says, for each
claim of a result, where its proof stops, what covers the part beyond, and whether proof picks up again.

**What it covers.** Every statement of THEOREMS.md's proved table; the turns law, which THEOREMS.md names and does not
prove (its statement is withheld from this tree); the guarantee tables of `docs/paper/SYSTEM-GUARANTEES.md` (G1 to G6)
and `docs/GUARANTEES-LEDGER.md`; and the sentences of Skuldd's own documents that state a proved or measured result
(`README.md`, `AGENTS.md`, `PROVENANCE.md`, `CHANGES-AFTER-IMPORT.md`, `kernel/notes/LIMITATIONS.md`,
`kernel/notes/FCLINK-TRUSTED-2026-11-22.md`, `kernel/notes/CORRECTIONS-2026-11-16.md`, the paper, the ledger,
`docs/engineering/GPU-BIT-EXACTNESS.md`, `docs/engineering/MATHKERNEL-LINUX-CI.md`, `kernel/runtime/README.md`,
`kernel/records/INDEX.md`, `kernel/records/bits32/TRANSCRIPTION.md`, `kernel/hardening/plants/PLANT-LABELS.md`,
`kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, and the comments of `.github/workflows/`). One row stands for one
stop of one claim, or of a group of claims that share it. As THEOREMS.md says, the imported documents of `orlog/` and
`verdandi/` and the comments inside frozen files keep their own words: their claims have no rows here, except where
Skuldd's own documents cite them. Sentences graded ARGUED or DESIGNED that claim no result (the paper's section 6)
have no rows.

**How a row reads.** Each row has seven fields:

- Claim: what is claimed. Statements are named in backticks as in the proved table. A Claim that starts with PENDING
  names a statement proved and gated outside this tree, not yet part of it; one that starts with STATED names a
  statement its authors have written and this tree does not prove (the turns law, whose statement is withheld from
  this tree).
- Claimed in: the files that make the claim.
- Stop: where the proof stops.
- Kind: one of input class (inputs it does not cover), model (what its model abstracts), layer (a layer it does not
  reach) and trust (what it rests on).
- Covers beyond: what covers the part beyond the stop, with its file: a path of this tree, or the sha256 of a record
  kept outside it.
- Grade: GATED (a gated theorem of the proved table, named in Covers beyond), MEASURED, ARGUED or DECLARED (evidence,
  its file named), or NOT_MEASURED; several are written ", " apart.
- Proof again: the stage at which proof picks up again (now: a gated theorem of this tree already covers it; Push A;
  Push B; Push B or later; later: a stage not yet set), or never, with why.

`tools/ci/check_boundaries.py` refuses the tree when a statement of the proved table has no row, a row lacks a field,
a grade is outside the list above, a Kind or a stage is not one of those listed, graded evidence names no file, a path
named is not in this tree, or a PENDING or STATED row names a statement the proved table holds. It does not judge that
a row is true, nor that every sentence of the documents listed above that states a result has its row: for those
sentences, coverage is the authors' reading. A row changes only in a push that carries the evidence for the change.

## 1. Stops that every statement of the proved table shares

### B001 Coq's kernel and checker
- Claim: each statement file of the proved table is implied by its proof (G1)
- Claimed in: `THEOREMS.md`, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: Coq 8.20.1's kernel accepting each proof term, and coqchk 8.20.1, which shares the kernel's code, rechecking it
- Kind: trust
- Covers beyond: each gate rechecks the compiled files with coqchk (MEASURED: the gate consoles, for example
  `verdandi/mathkernel/F32/f32/gate4-run1-console.txt`), which re-checks the virtual machine's conversions by the
  kernel's own conversion, without the virtual machine, by the authors' statement (DECLARED,
  `kernel/hardening/features/feature_row3.py` and `kernel/coq/fclink/Link.v`; no record of this tree measures it,
  `kernel/notes/FCLINK-TRUSTED-2026-11-22.md` section 3.4); the source rows refuse the constructs behind most entries of
  Coq's list of critical bugs (MEASURED, `kernel/hardening/features/PREDICTIONS-row3-2026-11-17.md`); the reading of
  that list, entry by entry, by agents of the authors' family (ARGUED, reported in `docs/paper/SYSTEM-GUARANTEES.md`
  section 5.5); 15 entries reachable only through library code stay open
- Grade: MEASURED, ARGUED, DECLARED
- Proof again: never: a checker cannot prove its own soundness inside the project; a second, later Coq release
  (proposed under ruling A6, not run) or an independent checker would narrow this, not close it

### B002 The four axioms
- Claim: each closing theorem rests on exactly four axioms of Coq's standard library
- Claimed in: `THEOREMS.md`, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: the consistency of `ClassicalDedekindReals.sig_not_dec`, `sig_forall_dec`, functional extensionality and
  `classic`
- Kind: trust
- Covers beyond: Print Assumptions lists exactly these four in every gate run (MEASURED, against
  `kernel/coq/gate/expected-pa-flocq4.txt`); their consistency is a known result outside the project (ARGUED)
- Grade: MEASURED, ARGUED
- Proof again: never: the statements are about Coq's classical real numbers, which rest on these axioms

### B003 The builds of Coq and Flocq, the image, and the hosts that ran the gates
- Claim: the gate verdicts of the proved table (the first thirteen rows held on one host and on GitHub-hosted runners,
  the last eight on one host)
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `docs/engineering/MATHKERNEL-LINUX-CI.md`
- Stop: Coq 8.20.1 and Flocq 4.2.1 as built in the pinned container image, and on GitHub's runners as built from opam
- Kind: trust
- Covers beyond: each gate rechecks with coqchk every outside library of its folder's closure, each named by the
  sha256 of its file (MEASURED, the gate consoles: 295 for `f32`, `verdandi/mathkernel/F32/f32/gate4-run1-console.txt`,
  303 for `p32`, `p32r`, `exp32` and `exp32r` in their consoles there, up to 312 for `fclink`, row B078); in CI each
  library's sha256 must equal its line of `kernel/coq/EXPECTED-CI-LIBRARIES.txt`, which lists 309, and the closures
  of `bits32` and `fclink` hold libraries it does not list (row B078); a second build chain held the gates of the
  first thirteen folders on 2026-11-18, run 44211905832 (MEASURED, `docs/engineering/MATHKERNEL-LINUX-CI.md`); no
  second build or Coq release has run the eight folders added later (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: a build of a prover is checked by running it, not proved; a second Coq release would narrow it

### B004 That a statement says what its owner meant
- Claim: the statements are the right ones (G1's and G6's question); every statement is a candidate, not adopted
- Claimed in: `THEOREMS.md`, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `docs/GUARANTEES-LEDGER.md`,
  `kernel/notes/LIMITATIONS.md`
- Stop: whether a statement's text says what its owner meant
- Kind: trust
- Covers beyond: one model outside the authors' family read the first thirteen statement files on 2026-11-17, as the
  owner reports (DECLARED, `docs/GUARANTEES-LEDGER.md`, section Outside reading); no reader outside the family has read
  the eight added later, and no human outside the authors has read any (NOT_MEASURED)
- Grade: DECLARED, NOT_MEASURED
- Proof again: never: whether a text means what its owner meant is a reading, not a theorem; the owner's adoption and
  outside reviews narrow it

### B005 The definitions a statement is about
- Claim: every statement of the proved table, read as a statement about binary32, binary64 and the real functions
- Claimed in: `THEOREMS.md`
- Stop: that Flocq's FLT formats and roundings are binary32's and binary64's numbers and roundings, and that the
  standard library's sin, cos, exp, ln, sqrt and PI are the real functions
- Kind: trust
- Covers beyond: the definitions are read, not proved; each statement file names them in its header (ARGUED, for
  example `kernel/coq/sin32/SIN32_Statement.v`, WHAT IT TRUSTS)
- Grade: ARGUED
- Proof again: never: a definition is where a proof's subject begins

### B006 From IEEE operations to a machine
- Claim: every result the tree measures of a compiled program (the C sweeps, the turns kernel's exhaustive run, the
  floor and ceiling sweeps)
- Claimed in: `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `kernel/notes/LIMITATIONS.md`
- Stop: no statement says that a compiler emits, or a processor executes, the modelled operations in the modelled
  order, in the floating-point state the model assumes
- Kind: trust
- Covers beyond: the sweeps compare compiled programs' outputs with references, one host and one compiler per program
  (MEASURED, `verdandi/mathkernel/F32/CLAIMS.md`, `docs/paper/SYSTEM-GUARANTEES.md` section 5.3); the floating-point
  guard's prototype (MEASURED, `kernel/runtime/README.md`); no other machine for the programs (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: a compiler and a processor are measured, not proved, inside the project; a verified compiler
  route would move the compiler, never the processor

## 2. The statements of the proved table

### B010 F32_REL: the model of binary32
- Claim: `f32.F32_Statement.F32_REL`
- Claimed in: `THEOREMS.md`, `README.md`
- Stop: Flocq's FLT(-149, 24) without an upper exponent bound: no overflow, one zero
- Kind: model
- Covers beyond: FAITHFUL_FINITE makes a faithful rounding of a value in binary32's finite range a finite binary32
  number (`p32r.P32R_Statement.P32R`)
- Grade: GATED
- Proof again: now: `p32r.P32R_Statement.P32R` is gated in this tree

### B011 The five older functions: the model without overflow
- Claim: `p32.P32_Statement.T32`, `SQRT32`, `RSQRT32`, `HYPOT32`, `exp32.EXP32_Statement.EXP32`
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: graphs over Flocq's FLT model of binary64, in which nothing overflows: "format32" holds of 2^128 and beyond,
  so a faithful result need not be a finite binary32 number (the sign of a zero and NaN: rows B013 and B014)
- Kind: model
- Covers beyond: the results are finite binary32 numbers on the stated domains, and the limits are sharp
  (`p32r.P32R_Statement.P32R`, `exp32r.RANGE_Statement.EXP32_RANGE`, `exp32r.RANGE_Statement.EXP32_SHARP`)
- Grade: GATED
- Proof again: now: those statements are gated in this tree

### B012 The five older functions: the IEEE binary64 layer
- Claim: `p32.P32_Statement.T32`, `SQRT32`, `RSQRT32`, `HYPOT32`, `exp32.EXP32_Statement.EXP32`,
  `p32r.P32R_Statement.P32R`, `exp32r.RANGE_Statement.EXP32_RANGE`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: the statements speak of the graphs, not of IEEE binary64 arithmetic
- Kind: layer
- Covers beyond: Flocq's IEEE binary64 operations, in each graph's order, return a finite value that denotes the
  graph's (`ieee64.IEEE64_Statement.IEEE64`), and that value is a finite binary32 number and a faithful rounding of
  the exact result (`compose.COMPOSE_Statement.COMPOSE`)
- Grade: GATED
- Proof again: now: both are gated in this tree

### B013 The five older functions: inputs outside the premises
- Claim: `p32.P32_Statement.T32`, `SQRT32`, `RSQRT32`, `HYPOT32`, `exp32.EXP32_Statement.EXP32`,
  `p32r.P32R_Statement.P32R`, `exp32r.RANGE_Statement.EXP32_RANGE`, `ieee64.IEEE64_Statement.IEEE64`,
  `compose.COMPOSE_Statement.COMPOSE`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`
- Stop: nothing is stated outside each premise: negative inputs of sqrt32, inputs of rsqrt32 at or below 0, hypot32
  with an exact result above FMAX32, narrow at or above OVF32, infinite and NaN inputs
- Kind: input class
- Covers beyond: the exhaustive sweeps skip every input whose exponent field is all ones
  (`kernel/notes/LIMITATIONS.md`); what the programs return outside the premises is not recorded in this tree
- Grade: NOT_MEASURED
- Proof again: later: no statement of the results outside the premises is drafted

### B014 The five older functions: the sign of a zero, NaN payloads and flags
- Claim: `ieee64.IEEE64_Statement.IEEE64`, `compose.COMPOSE_Statement.COMPOSE`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: Flocq's BinarySingleNaN gives one real number to +0 and -0, has one NaN and no exception flags; which zero a
  result is, is not stated
- Kind: model
- Covers beyond: nothing in this tree; the omission of the sign of a zero is the owner's decision E (a) of
  2026-11-15, written in `kernel/coq/compose/COMPOSE_Statement.v`
- Grade: NOT_MEASURED
- Proof again: later: a sign-of-zero statement needs the owner's separate word (decision E (a)); flags never, since
  Flocq's operations carry none

### B015 The five older functions: from the IEEE operations to a program's text
- Claim: `ieee64.IEEE64_Statement.IEEE64`, `compose.COMPOSE_Statement.COMPOSE`; the C sweep programs and corpus laws
  under verdandi/mathkernel/F32/orl (the ledger, section 2)
- Claimed in: `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `AGENTS.md` (the sweeps of narrow,
  sqrt32, rsqrt32 and exp32)
- Stop: no statement says a program's text performs these operations, in this order, on these constants
- Kind: layer
- Covers beyond: generated programs compared with the graphs, and compiled programs swept against references, each
  with its own scope (hypot32 sampled only) (MEASURED, `verdandi/mathkernel/F32/CLAIMS.md`, sections 5 to 7)
- Grade: MEASURED
- Proof again: later: the printers that would print each language's program from the proved shapes (G3) are designed,
  not built

### B016 The values in between and the value a selection does not return
- Claim: `ieee64.IEEE64_Statement.IEEE64`, `compose.COMPOSE_Statement.COMPOSE`
- Claimed in: `docs/GUARANTEES-LEDGER.md`
- Stop: only the returned value is said to be finite; the intermediate operations and an unreturned branch are not
- Kind: layer
- Covers beyond: nothing in this tree for the five older functions (`docs/GUARANTEES-LEDGER.md`, section 1: "NOT
  stated")
- Grade: NOT_MEASURED
- Proof again: later: a successor statement is proposed in the ledger, none drafted

### B017 exp32 above XMAX
- Claim: `exp32.EXP32_Statement.EXP32`, `exp32a.EXP32_ADJ_Statement.EXP32_ADJ`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: EXP32 covers inputs up to XMAX; EXP32_ADJ speaks of XNEXT, the next binary32 number, and not of the inputs
  above it
- Kind: input class
- Covers beyond: at XNEXT no faithful binary32 rounding of exp is finite (`exp32a.EXP32_ADJ_Statement.EXP32_ADJ`);
  above XNEXT the same follows from exp being increasing (ARGUED, `kernel/coq/exp32a/EXP32_ADJ_Statement.v`)
- Grade: GATED, ARGUED
- Proof again: now: EXP32_ADJ is gated in this tree for XNEXT; above it later, as a statement not drafted

### B018 exp32 at and above XNEXT, at the IEEE level
- Claim: `exp32r.RANGE_Statement.EXP32_SHARP`, `exp32a.EXP32_ADJ_Statement.EXP32_ADJ`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: the model has no infinity: what an IEEE program returns there (an infinity, a flag) is not stated
- Kind: model
- Covers beyond: nothing in this tree
- Grade: NOT_MEASURED
- Proof again: later: no statement of the overflowing inputs is drafted

### B019 F32's constant is not the largest that works
- Claim: the limit of F32's relative constant is near 2^-25 (a pair at relative distance 2^-25 (1 + 6e-8) whose RN32
  is not faithful)
- Claimed in: `docs/GUARANTEES-LEDGER.md`
- Stop: a measured counterexample with exact rationals; that 2^-25 itself suffices is argued, not proved
- Kind: layer
- Covers beyond: the run is reported in `docs/GUARANTEES-LEDGER.md`, section 1, and its record is not in this tree
  (MEASURED there); the sufficiency of 2^-25 (ARGUED, same file)
- Grade: MEASURED, ARGUED
- Proof again: later: no statement about the sharp constant is drafted; F32 is true as stated

### B020 Flocq's IEEE operations are IEEE 754's
- Claim: `ieee64.IEEE64_Statement.IEEE64`, `compose.COMPOSE_Statement.COMPOSE`,
  `sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE`, `sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`,
  `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`, `rti32.RTI32_Statement.RTI32`,
  `order32.ORDER32_Statement.ORDER32`, `bits32.BITS32_Statement.BITS32`, `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: that Flocq's Bplus, Bminus, Bmult, Bdiv and Bsqrt at mode_NE, Babs, Bopp, Bleb, Bltb, Bcompare, Bsign and
  B754_zero are IEEE 754's operations, comparison, sign bit and signed zero
- Kind: trust
- Covers beyond: compiled programs that perform these operations agree with independent references on the inputs
  swept (MEASURED, `verdandi/mathkernel/F32/CLAIMS.md`, `docs/paper/SYSTEM-GUARANTEES.md` section 5.3, and the
  floor and ceiling sweep, console sha256 cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025); the
  standard's text has not been read against them (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: that a formalisation is a standard is a reading of the standard's text; a reading against a
  licensed copy narrows it

### B021 The store of a result to binary32
- Claim: `compose.COMPOSE_Statement.COMPOSE`
- Claimed in: `THEOREMS.md`
- Stop: COMPOSE says the real number of the result is a binary32 number, not that a conversion to the binary32 format
  returns it
- Kind: layer
- Covers beyond: a conversion of a representable value returns it, by IEEE 754's rule (ARGUED,
  `kernel/coq/compose/COMPOSE_Statement.v`)
- Grade: ARGUED
- Proof again: never: the conversion is done by a compiler and a processor (row B006)

### B030 sin32, cos32 and log32: their domains
- Claim: `sin32.SIN32_Statement.SIN32_ALL`, `cos32.COS32_Statement.COS32_ALL`, `log32.LOG32_Statement.LOG32_ALL`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`
- Stop: SIN32 covers |x| <= SMAX and COS32 |x| <= CMAX, in radians, with no reduction of the argument; LOG32 covers
  0 < x < 2^128
- Kind: input class
- Covers beyond: no measurement of these functions exists (`kernel/notes/LIMITATIONS.md`); sine and cosine in turns
  are a different function, with their own rows
- Grade: NOT_MEASURED
- Proof again: later: no wider statement is drafted

### B031 sin32, cos32 and log32: no IEEE layer, program or sweep
- Claim: `sin32.SIN32_Statement.SIN32_ALL`, `cos32.COS32_Statement.COS32_ALL`, `log32.LOG32_Statement.LOG32_ALL`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: proved about Coq graphs only: no IEEE-level statement, native program, exhaustive sweep or backend
- Kind: layer
- Covers beyond: nothing (`kernel/notes/LIMITATIONS.md`, `docs/GUARANTEES-LEDGER.md` section 1)
- Grade: NOT_MEASURED
- Proof again: later: IEEE correspondences for the three are proposed in the ledger, none drafted

### B032 sin32, cos32 and log32: the model
- Claim: `sin32.SIN32_Statement.SIN32_ALL`, `cos32.COS32_Statement.COS32_ALL`, `log32.LOG32_Statement.LOG32_ALL`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`
- Stop: no overflow, one zero, no NaN or infinity; no operation of the graphs is said not to overflow
- Kind: model
- Covers beyond: nothing in this tree (the arguments for the intermediate ranges are not in it)
- Grade: NOT_MEASURED
- Proof again: later: with the IEEE correspondences of row B031

### B040 The turns kernel's graphs: the model
- Claim: `sincos32.SINCOS32_Statement.SINCOS32_ALL`
- Claimed in: `THEOREMS.md`, `README.md`
- Stop: graphs over the FLT model: no overflow, one zero, no NaN or infinity
- Kind: model
- Covers beyond: the IEEE operations return the graphs' values on every finite binary32 input
  (`sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE`); the sign of each exact zero and NaN for every non-finite input
  (`sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`)
- Grade: GATED
- Proof again: now: both are gated in this tree

### B041 The turns kernel: zero results away from the exact points
- Claim: `sincos32.SINCOS32_Statement.SINCOS32_ALL`, `sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: SINCOS32_ALL allows a zero result below 2^-149; SINCOS32_NONZERO excludes it for the graphs only, not at the
  IEEE level
- Kind: layer
- Covers beyond: the graphs' results are not zero where the function is not
  (`sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO`); at the IEEE level it follows with Z_SIN_VALUE and
  Z_COS_VALUE (ARGUED,
  `kernel/coq/sincos32n/SINCOS32_NONZERO_Statement.v`); the exhaustive run found zero results exactly where the
  functions are zero (MEASURED, `docs/paper/SYSTEM-GUARANTEES.md` section 5.3)
- Grade: GATED, ARGUED, MEASURED
- Proof again: Push B or later: the law's zero clauses state it on 32-bit patterns (row B050)

### B042 The turns kernel at the IEEE level: zeros and non-finite inputs
- Claim: `sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE`
- Claimed in: `THEOREMS.md`, `kernel/notes/CORRECTIONS-2026-11-16.md` (its item 12, the values in between on sampled
  inputs)
- Stop: nothing about the sign of a zero result, an infinite or NaN input, the values in between or the value a
  selection does not return
- Kind: model
- Covers beyond: the sign of a zero where the function is exactly zero, and NaN for every non-finite input
  (`sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`); every intermediate value finite and moderate on all
  finite inputs (MEASURED, `docs/paper/SYSTEM-GUARANTEES.md` section 5.3)
- Grade: GATED, MEASURED
- Proof again: now: SINCOS32_IEEE_ZERO for the zeros and non-finite inputs; Push B or later for the intermediate
  values, a clause of the law (row B050)

### B043 The turns kernel at the IEEE level: which NaN, and flags
- Claim: `sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: Flocq's BinarySingleNaN has one NaN and no flags: which NaN, and any flag, are not stated
- Kind: model
- Covers beyond: every infinite and NaN input gave the pattern 0x7FC00000 in the exhaustive run (MEASURED,
  `docs/paper/SYSTEM-GUARANTEES.md` section 5.3)
- Grade: MEASURED
- Proof again: Push B or later: the law states the pattern 0x7FC00000 (row B050); flags never inside this tier, since
  Flocq's operations carry none

### B044 The turns kernel's IEEE statements: inputs that are not binary32 numbers
- Claim: `sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE`,
  `sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`
- Claimed in: `THEOREMS.md`
- Stop: a finite binary64 input that is not a binary32 number
- Kind: input class
- Covers beyond: no binary32 datum is such an input (ARGUED, `kernel/coq/sincos32i/SINCOS32_IEEE_Statement.v`)
- Grade: ARGUED
- Proof again: never: a binary32 caller cannot pass one

### B045 The turns kernel: faithful, not correctly rounded
- Claim: 762 sine and 14,556 cosine results of 4,278,190,080 are faithful but not the nearest
- Claimed in: `kernel/notes/LIMITATIONS.md`, `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: the counts come from a C transcription of the law run beside GNU MPFR, not from the proved shapes, and MPFR
  is trusted
- Kind: trust
- Covers beyond: the exhaustive run with ten predictions written before it (MEASURED,
  `docs/paper/SYSTEM-GUARANTEES.md` section 5.3)
- Grade: MEASURED
- Proof again: never: correct rounding is not claimed; a correctly rounded variant would be a new function, which needs
  the owner's word

### B050 The turns law on 32-bit patterns: stated, not proven in this tree
- Claim: STATED `sincos32law.SINCOS32_LAW_Statement.SINCOS32_LAW`
- Claimed in: `THEOREMS.md`, `README.md`, `kernel/notes/LIMITATIONS.md`, `docs/paper/SYSTEM-GUARANTEES.md` (G2),
  `docs/GUARANTEES-LEDGER.md`
- Stop: this tree holds the law's name and no proof of it; the statement is withheld until an independent reviewer
  has written a blind formalisation of the same convention
- Kind: layer
- Covers beyond: the graph and IEEE layers are gated (`sincos32.SINCOS32_Statement.SINCOS32_ALL`,
  `sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE`, `sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO`,
  `sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO`), not the 32-bit pattern layer; the law measured on all
  2^32 inputs through a C transcription (MEASURED, `docs/paper/SYSTEM-GUARANTEES.md` section 5.3)
- Grade: GATED, MEASURED
- Proof again: Push B or later: under ruling TR-1 the law enters the tree only after the reviewer's blind
  formalisation returns and a gated proof shows that the law implies it, in the first push after that

### B051 The turns law's measurement: the transcription and the oracle
- Claim: STATED `sincos32law.SINCOS32_LAW_Statement.SINCOS32_LAW`; G2's grade MEASURED on all 2^32 inputs
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`, `README.md`
- Stop: the C transcription was shown equal to Coq's evaluation of the law at 2,096 patterns only; MPFR is trusted;
  the transcription and its consoles are withheld from this tree
- Kind: trust
- Covers beyond: the run's result digests and its counts (MEASURED, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`
  section 5.3)
- Grade: MEASURED
- Proof again: Push B or later: a gated proof of the law makes the pattern-level claim a theorem (row B050); the C
  transcription stays a measured program until a printer prints it

### B052 The turns law: exception flags
- Claim: STATED `sincos32law.SINCOS32_LAW_Statement.SINCOS32_LAW`
- Claimed in: `kernel/notes/LIMITATIONS.md`
- Stop: exception flags are not specified, on the condition that every exception is masked
- Kind: model
- Covers beyond: nothing measured (`kernel/notes/LIMITATIONS.md`)
- Grade: NOT_MEASURED
- Proof again: never: Flocq's operations carry no flags, so not inside this tier unless a model with flags is adopted

### B053 The turns law: one NaN pattern
- Claim: STATED `sincos32law.SINCOS32_LAW_Statement.SINCOS32_LAW`
- Claimed in: `kernel/notes/LIMITATIONS.md`, `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: NaN payloads and signs are not kept: every infinite or NaN input gives 0x7FC00000, by the owner's ruling
- Kind: model
- Covers beyond: the convention is declared in `kernel/notes/LIMITATIONS.md` and the paper (DECLARED); the programs
  of floor32 and ceil32, as measured through C's (double) and (float) conversions on one x86-64 host, keep a NaN's
  payload (row B061; another path NOT_MEASURED, row B075), so a value's NaN depends on the function it went through
- Grade: DECLARED
- Proof again: never: a payload is not kept by design

### B060 floor32 and ceil32: inputs that are not binary32 numbers
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`, `rti32.RTI32_Statement.RTI32`,
  `order32.ORDER32_Statement.ORDER32`, `bits32.BITS32_Statement.BITS32`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`
- Stop: a finite binary64 input that is not a binary32 number: the branch for magnitudes of 2^23 or more returns it
  unchanged, and it need not be a whole number
- Kind: input class
- Covers beyond: no binary32 datum is such an input (ARGUED, `kernel/notes/LIMITATIONS.md`)
- Grade: ARGUED
- Proof again: never: a binary32 caller cannot pass one

### B061 floor32 and ceil32: NaN bits
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`, `rti32.RTI32_Statement.RTI32`,
  `order32.ORDER32_Statement.ORDER32`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: Flocq's BinarySingleNaN has one NaN: payloads, the quiet bit and signalling NaNs are not seen
- Kind: model
- Covers beyond: on one build and one x86-64 processor, through C's (double) and (float) conversions, every
  signalling NaN came back quieted with its payload and every quiet NaN unchanged, on all NaN inputs (MEASURED by a
  research agent of the authors' family; report sha256
  28bf224de7759350f751ef7a1047ec50241ae793a56b05416fff2beb8365dc1c); BITS32 states the bits of its specification
  SPEC32 on every pattern, NaN patterns included, and the programs' result bits on every pattern that is not a NaN
  (GATED, `bits32.BITS32_Statement.BITS32`); a caller that converts binary32 on integer bits has not been measured
  (NOT_MEASURED, row B075)
- Grade: MEASURED, GATED, NOT_MEASURED
- Proof again: never: the programs' model has one NaN, so which NaN a program returns stays measured (row B075);
  BITS32 (row B074) is the proof for every other pattern's bits

### B062 floor32 and ceil32: exception flags
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`, `rti32.RTI32_Statement.RTI32`,
  `order32.ORDER32_Statement.ORDER32`, `bits32.BITS32_Statement.BITS32`, `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `kernel/notes/LIMITATIONS.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: no flags are stated; x + 1.5 * 2^52 may be inexact where IEEE's round-to-integral raises nothing
- Kind: model
- Covers beyond: nothing measured (`kernel/notes/LIMITATIONS.md`)
- Grade: NOT_MEASURED
- Proof again: never: Flocq's operations carry no flags, so not inside this tier unless a model with flags is adopted

### B063 floor32 and ceil32: Flocq's Bnearbyint is IEEE 754's roundToIntegral
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32` (their parts FL_IEEE and CL_IEEE)
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`, `kernel/records/INDEX.md`
- Stop: FL_IEEE and CL_IEEE equal the computation to Flocq's Bnearbyint toward minus and plus infinity; that
  Bnearbyint is IEEE 754's roundToIntegralTowardNegative and roundToIntegralTowardPositive is trusted
- Kind: trust
- Covers beyond: a C rendering of the program returned, for all 2^32 binary32 patterns, the bits of the host's floorf
  and ceilf and of an integer reference, NaNs compared as NaNs, on one x86-64 host with one compiler (MEASURED: two
  runs, `kernel/records/floor32/p1-sweep-run1-console.txt` and `kernel/records/floor32/p1-sweep-run2-console.txt`,
  sha256 a7eb1695ce042700ade2d0395c5e8d98085fb265c5d7ea08ebc321bba5a33a9a and
  cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025; the program `kernel/records/floor32/sweep_fc.c`,
  sha256 c0b4b71092f841621eefd9ae65677afb5ec198785772bce2a22de67efaafdc92); RTI32 proves that the computation meets IEEE
  754's round-to-integral clauses as transcribed and that Bnearbyint is exactly those clauses (GATED,
  `rti32.RTI32_Statement.RTI32`). Not evidence (dated note of 2026-11-22): the
  "what" text of the plant ieee-other-mode in `kernel/coq/floor32/gate.json` and `kernel/coq/ceil32/gate.json`,
  frozen and unchanged, reads more into its refusal than it shows; the refusal shows only that FloorIEEE.v
  (CeilIEEE.v) does not compile with the planted statement, nothing about Bnearbyint or IEEE 754
- Grade: MEASURED, GATED
- Proof again: now: RTI32 (row B070) holds the computation to IEEE 754's clauses as transcribed and ties Bnearbyint
  to them; the transcription stays a reading (row B071)

### B064 floor32 and ceil32: from the IEEE operations to a program
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`, `docs/paper/SYSTEM-GUARANTEES.md`,
  `kernel/records/INDEX.md`
- Stop: nothing about the widening of a binary32 input to binary64, the store of the result to binary32, or a program
  in any language
- Kind: layer
- Covers beyond: the exhaustive sweep of a C rendering, transcribed from the Coq shape by hand (MEASURED,
  `kernel/records/floor32/p1-sweep-run2-console.txt`, sha256
  cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025; the transcription ARGUED); FCLINK proves
  that Coq's printer gives the C text the sweep program `kernel/coq/fclink/sweep_fc2.c` holds (GATED,
  `fclink.FCLINK_Statement.FCLINK`; the quote, row B067), and that program's exhaustive sweep held on one host
  (MEASURED, `kernel/records/fclink/sweep-real-r1.txt`, sha256
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a); BITS32 models
  the widening and the result bits (GATED, `bits32.BITS32_Statement.BITS32`); the sweep job of
  `tools/ci/check_sweep.py` has not run on GitHub
  (NOT_MEASURED)
- Grade: MEASURED, ARGUED, GATED, NOT_MEASURED
- Proof again: now: FCLINK (rows B076 and B067) carries the proof to the printed C text of both shapes, and BITS32
  (row B074) to the widening and the result bits in its model; what the C text means (row B077), the processor's
  conversions (row B069) and the compiler and the processor (row B006) stay outside it

### B065 floor32 and ceil32: the floating-point state
- Claim: `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`, `rti32.RTI32_Statement.RTI32`,
  `order32.ORDER32_Statement.ORDER32`, `bits32.BITS32_Statement.BITS32`, `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `THEOREMS.md`, `kernel/notes/LIMITATIONS.md`
- Stop: denormals-are-zero (DAZ) off is a precondition of any program of them: the statements assume IEEE operations
- Kind: trust
- Covers beyond: on all 2^32 inputs in seven MXCSR states only DAZ changed the results, on 8,388,607 subnormal inputs
  per function (MEASURED by a research agent; report sha256
  28bf224de7759350f751ef7a1047ec50241ae793a56b05416fff2beb8365dc1c); in the all-bits record sweep of ruling A4 (a),
  the build run with DAZ set changed the results on 8,388,607 finite patterns of each function, and the record's
  environment row refused that state (MEASURED, one run on one host,
  `kernel/records/bits32/bits32-sweep-run1-console.txt`, sha256
  eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1); the guard `kernel/runtime/mk_fpenv.c` reports
  DAZ, and no library calls it (MEASURED, `kernel/runtime/README.md`)
- Grade: MEASURED
- Proof again: never: a run-time state is checked at entry, not proved

### B066 The gates of sincos32n, exp32a, floor32 and ceil32
- Claim: `sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO`, `exp32a.EXP32_ADJ_Statement.EXP32_ADJ`,
  `floor32.FLOOR32_Statement.FLOOR32`, `ceil32.CEIL32_Statement.CEIL32`: their gates held with --recheck
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/records/INDEX.md`
- Stop: one host, on a copy of `kernel/coq`; their consoles hold details of that host and are not in this tree;
  neither the Linux CI nor the harness has run on them
- Kind: trust
- Covers beyond: the four consoles, each named by its sha256 in `THEOREMS.md` (MEASURED); each folder's earlier gate
  runs on the same host, red ones named as red, by name and sha256 in `kernel/records/INDEX.md` (MEASURED)
- Grade: MEASURED
- Proof again: never: a gate run is the proof checked on one machine, measured, not proved (row B003); the branch run
  of ruling S280-9 (b) adds GitHub's runners before the final head, which narrows it

## 3. RTI32, ORDER32, BITS32 and FCLINK: what each adds to FLOOR32 and CEIL32, and where it stops

Each landed in this tree with Push A's batch on 2026-11-22: its statement frozen by the owner's own sha256 under
ruling R1 before its proof (the folder's `FROZEN.txt`), and its gate held with `--recheck` under the owner's anchor,
one run on one host (`THEOREMS.md` names the consoles). Each says more about the programs of FLOOR32 and CEIL32, so
proof picks up again at some of their stops (rows B061, B063 and B064 say where); the rows below say where each of the
four stops in its turn. They share rows B001 to B006, B020 and B060 to B065 with FLOOR32 and CEIL32.

### B067 FCLINK: the quoted lines of the sweep program
- Claim: `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`,
  `kernel/notes/FCLINK-TRUSTED-2026-11-22.md`
- Stop: FC_TEXT equates the printed text with the two strings of KernelText.v; that those strings are the two lines
  between the markers of sweep_fc2.c lies outside Coq: no Coq term refers to a file
- Kind: layer
- Covers beyond: the gate runs `kernel/coq/fclink/gen_kernel_text.py` again and compares its output with
  `kernel/coq/fclink/KernelText.v` byte for byte (MEASURED, gate console sha256
  3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e), and both freeze lists record the sweep program
  (MEASURED, `kernel/coq/fclink/FROZEN.txt` and `kernel/coq/fclink/FROZEN4.txt`); that the generator quotes each
  line's bytes is ARGUED from its header (it refuses a double quote and every character outside printable ASCII)
- Grade: MEASURED, ARGUED
- Proof again: never: a file is not a Coq object; the quote is checked by a machine row and by reading

### B068 BITS32: the Bits encoding and the quiet bit
- Claim: `bits32.BITS32_Statement.BITS32`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: that Flocq's Bits encoding at 23 and 8 is IEEE 754's binary32 interchange format, that Flocq's Binary B2R,
  Bsign, is_nan and is_finite at 24 and 128 are binary32's value, sign bit and classes, and that bit 22 is the quiet
  bit (IEEE 754's preferred encoding, which Flocq does not name)
- Kind: trust
- Covers beyond: the statement's header names this trust (DECLARED, `kernel/coq/bits32/BITS32_Statement.v`, WHAT IT
  TRUSTS); on one x86-64 processor a signalling NaN came back with bit 22 set and its other bits kept (MEASURED by a
  research agent of the authors' family; report sha256
  28bf224de7759350f751ef7a1047ec50241ae793a56b05416fff2beb8365dc1c)
- Grade: DECLARED, MEASURED
- Proof again: never: that a formalisation is the standard's encoding is a reading of the standard's text

### B069 BITS32: the widening and the store on a processor
- Claim: `bits32.BITS32_Statement.BITS32`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: widen32 models the widening of a binary32 to binary64, and SPEC32_STORE a store that returns a binary32 whose
  widening is the value stored; that a processor's conversions are these is not stated
- Kind: layer
- Covers beyond: the exhaustive sweeps widen every binary32 input and store every result on one host, and compare the
  stored results bit for bit with references wherever no result is a NaN, and a NaN result as NaN-ness only
  (MEASURED, `kernel/records/floor32/p1-sweep-run2-console.txt` and
  `kernel/records/fclink/sweep-real-r1.txt`, sha256
  cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025 and
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a); the all-bits record sweep widens every pattern
  with C's (double) conversion and stores with (float), and compares all 32 bits of every result, NaN patterns
  included, with SPEC32 as transcribed (MEASURED, one run on one host,
  `kernel/records/bits32/bits32-sweep-run1-console.txt`; rows B075 and B103); denormals-are-zero changes the widening
  of subnormal inputs (row B065)
- Grade: MEASURED
- Proof again: never: a processor's conversions are measured, not proved, inside the project

### B070 RTI32: its gate, on one host
- Claim: `rti32.RTI32_Statement.RTI32`: floor32 and ceil32 meet IEEE 754's round-to-integral clauses toward minus and
  plus infinity as transcribed, and Flocq's Bnearbyint is exactly those clauses
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`,
  `kernel/records/INDEX.md`
- Stop: its gate ran on one host only, three times (a rehearsal and a recheck under the value the authors computed,
  then the run under the owner's anchor, the same value), each on a copy of `kernel/coq`; its consoles hold details of
  that host and are not in this tree; neither the Linux CI nor the harness has run on it
- Kind: trust
- Covers beyond: the gate held 296 of 296 under the owner's anchor, its Print Assumptions exactly the four axioms
  (MEASURED, console sha256 162a298f2e3dcf13d38d95f8fae9ec2c1100ba0fc8a65b5a18697f8997cd130c); a rehearsal and a
  recheck from a fresh copy by a second agent of the same family held 296 of 296 on the same host under the same
  value as the authors computed it (MEASURED, console sha256
  ea218096cf03a20b65a6368922331a7a9d65f3ef4e0bf57e41ad41fdc16aba3a and
  634c3b80ff52709663afe1650d8dbf2e559c6e07dec8a5e23ea03785d75043c6, listed in `kernel/records/INDEX.md`)
- Grade: MEASURED
- Proof again: never: a gate run is the proof checked on one machine, measured, not proved (row B003); the branch run
  of ruling S280-9 (b) adds GitHub's runners before the final head, which narrows it

### B071 RTI32 and ORDER32: the transcribed clauses
- Claim: `rti32.RTI32_Statement.RTI32`, `order32.ORDER32_Statement.ORDER32`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: RTI32's clauses transcribe a paraphrase of IEEE 754-2008 that this project's research read from a copy that
  was not licensed, and no one has set them beside the standard's text (2008 or 2019); ORDER32's fc_total_nn reads
  clauses a) to c) of the 2008 text's 5.10 on values that are not NaN, and takes Flocq's Bleb, Bcompare, Bopp and
  Bsign to be IEEE 754's compareQuietLessEqual, comparison relation, negate and sign bit
- Kind: trust
- Covers beyond: each statement names these readings in its header (DECLARED, `kernel/coq/rti32/RTI32_Statement.v`
  and `kernel/coq/order32/ORDER32_Statement.v`, WHAT IT TRUSTS); RTI_BN proves that the clauses as transcribed allow
  exactly one result for each operand, Flocq's (GATED, `rti32.RTI32_Statement.RTI32`); no one has set the lines
  beside a licensed text (NOT_MEASURED)
- Grade: DECLARED, GATED, NOT_MEASURED
- Proof again: never: a transcription of prose is read, not proved; a reading against a licensed IEEE 754-2019
  (ruling A5 (c)) narrows it

### B072 ORDER32: its gate, on one host
- Claim: `order32.ORDER32_Statement.ORDER32`: how floor32's and ceil32's results are ordered on binary32 inputs and
  how the two functions relate
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`,
  `kernel/records/INDEX.md`
- Stop: its gate ran on one host only, three times (a rehearsal and a recheck under the value the authors computed,
  then the run under the owner's anchor, the same value), each on a copy of `kernel/coq`; its consoles hold details of
  that host and are not in this tree; neither the Linux CI nor the harness has run on it
- Kind: trust
- Covers beyond: the gate held 296 of 296 under the owner's anchor, its Print Assumptions exactly the four axioms
  (MEASURED, console sha256 0188ae9d2ec58f187ec4e16c8f563fc55be338532b2a33d65fdc47caa436fc51); a rehearsal and a
  recheck from a fresh copy by a second agent of the same family held 296 of 296 on the same host under the same
  value as the authors computed it (MEASURED, console sha256
  6b336d0b000661be33ea428d921629683b39cac431bb2d519c4829379396fd77 and
  8339986d4c80d7a8a369ce17b04d46ea0c77183a8c779124d707bac5c8d35971, listed in `kernel/records/INDEX.md`)
- Grade: MEASURED
- Proof again: never: a gate run is the proof checked on one machine, measured, not proved (row B003); the branch run
  of ruling S280-9 (b) adds GitHub's runners before the final head, which narrows it

### B073 ORDER32: totalOrder where a NaN is compared
- Claim: `order32.ORDER32_Statement.ORDER32`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: nothing a NaN carries; on bit patterns IEEE 754's totalOrder fails floor32(x) <= x on every positive
  signalling NaN and x <= ceil32(x) on every negative one, since the result comes back quieted
- Kind: model
- Covers beyond: measured on all 2^32 patterns by a research agent (MEASURED, report sha256
  20b0c9e787a58f831009dad4aa51dad58aae1904d87aae26f556a58e92beecdc)
- Grade: MEASURED
- Proof again: later: a statement total32 with the signalling-NaN exception written in (ruling S280-7 (a)), in Push A
  only if proved and reviewed by its restatement, otherwise a later push; ORDER32 itself stays in a model with one NaN

### B074 BITS32: its gate, on one host
- Claim: `bits32.BITS32_Statement.BITS32`: an integer specification of floor32 and ceil32 over all 2^32 binary32
  patterns, and the programs' result bits equal to it on every pattern that is not a NaN
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`,
  `kernel/records/INDEX.md`
- Stop: its gate ran on one host only, three times (a rehearsal and a recheck under the value the authors computed,
  then the run under the owner's anchor, the same value), each on a copy of `kernel/coq`; its consoles hold details of
  that host and are not in this tree; neither the Linux CI nor the harness has run on it
- Kind: trust
- Covers beyond: the gate held 296 of 296 under the owner's anchor, its Print Assumptions exactly the four axioms
  (MEASURED, console sha256 aaa537712ed9b44562fa0005dd8189cea8b520cd419f5eefcabd71e639bca71e); a rehearsal and a
  recheck from a fresh copy by a second agent of the same family held 296 of 296 on the same host under the same
  value as the authors computed it (MEASURED, console sha256
  bb6ce7d580446a4948623f69f6c48fc566fda5c753bece7745800db3594976cb and
  b506eabd69962f44759f8fb095cb1bd83f4c60f92b8c47073d00ae1f8498d5c2, listed in `kernel/records/INDEX.md`)
- Grade: MEASURED
- Proof again: never: a gate run is the proof checked on one machine, measured, not proved (row B003); the branch run
  of ruling S280-9 (b) adds GitHub's runners before the final head, which narrows it

### B075 BITS32: the hardware's NaN bits
- Claim: `bits32.BITS32_Statement.BITS32`
- Claimed in: `THEOREMS.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`, `kernel/records/INDEX.md`
- Stop: which NaN the program returns for a NaN pattern: SPEC32_NAN and SPEC32_NAN31 speak of the specification only,
  and SPEC32_PROGRAM and SPEC32_STORE exclude NaN patterns; all 32 bits of a NaN result are to be claimed only for
  x86-64 SSE2 on the hosts measured (ruling S280-6 (a))
- Kind: layer
- Covers beyond: on one build and one x86-64 processor every signalling NaN came back quieted with its payload and
  every quiet NaN unchanged (MEASURED by a research agent of the authors' family; report sha256
  28bf224de7759350f751ef7a1047ec50241ae793a56b05416fff2beb8365dc1c); the all-bits record sweep of ruling A4 (a), run
  run1: FCLINK's C text, called through C's (double) and (float) conversions and built with clang 22.1.8 -O2
  -ffp-contract=off for x86-64, gave the bits of SPEC32 transcribed in C integers on all 2^32 patterns of floor32
  and ceil32, the 16,777,214 NaN patterns included, with five plants and a build with denormals-are-zero set at
  counts fixed before the run (MEASURED, one run on one host, `kernel/records/bits32/bits32-sweep-run1-console.txt`,
  sha256 eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1; its program
  `kernel/records/bits32/bits32_sweep.c`; the transcription, row B103); a caller that converts binary32 on integer
  bits, other compilers, flags, processors and hosts, flush-to-zero and the directed roundings are not measured by
  this record (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: the programs' model has one NaN, and a processor's NaN rule is measured, not proved (ruling
  A4 (a) writes no NaN model of a processor)

### B076 FCLINK: its gate, on one host
- Claim: `fclink.FCLINK_Statement.FCLINK`: Coq's printer gives the C text of floor32's and ceil32's shapes that the
  sweep program holds, and the printed shapes and the IEEE shapes are related by every relation the fields keep
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`,
  `kernel/records/INDEX.md`, `kernel/notes/FCLINK-TRUSTED-2026-11-22.md`
- Stop: its gate ran on one host only, three times (a rehearsal and a recheck under the value the authors computed,
  then the run under the owner's anchor, the same value), each on a copy of `kernel/coq`; its consoles hold details of
  that host and are not in this tree; neither the Linux CI nor the harness has run on it
- Kind: trust
- Covers beyond: the gate held 294 of 294 under the owner's anchor, its Print Assumptions exactly the four axioms
  (MEASURED, console sha256 3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e); a rehearsal and a
  recheck from a fresh copy by a second agent of the same family held 294 of 294 on the same host under the same
  value as the authors computed it (MEASURED, console sha256
  aed0e7dafab8698518c5fb2c821a8c49ded63e922627f5536fbbc802e7a2b50e and
  3766103d1bb9442ba64948e639604ee90a7f072907ebede8d5f5a18112e16bf4, listed in `kernel/records/INDEX.md`)
- Grade: MEASURED
- Proof again: never: a gate run is the proof checked on one machine, measured, not proved (row B003); the branch run
  of ruling S280-9 (b) adds GitHub's runners before the final head, which narrows it

### B077 FCLINK: what the printed C means
- Claim: `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `THEOREMS.md`, `README.md`, `docs/GUARANTEES-LEDGER.md`, `docs/paper/SYSTEM-GUARANTEES.md`,
  `kernel/notes/LIMITATIONS.md`, `kernel/notes/FCLINK-TRUSTED-2026-11-22.md`
- Stop: the meaning in C of the printed forms (the operations, comparisons and selections, the hexadecimal
  constants, the function line) in their environment (no contraction, rounding to nearest, no excess precision,
  denormals-are-zero and flush-to-zero off): FC_PARAM relates the printed text and the IEEE computation by every
  relation the fields keep, and that C reads the text as that computation is such a relation only by declaration
- Kind: trust
- Covers beyond: the statement's header names this trust (DECLARED, `kernel/coq/fclink/FCLINK_Statement.v`, WHERE
  ITS PROOF STOPS AND WHAT IT TRUSTS); `kernel/notes/FCLINK-TRUSTED-2026-11-22.md` sets out what is declared, brought
  to the state after the proof: the meanings of the printed forms in the two strings and the environment they assume
  (DECLARED, its sections 3.1 and 3.3); the program `kernel/coq/fclink/sweep_fc2.c`, built by clang at -O0 and -O2
  with contraction off and no x87 or FMA instruction in its objects, agreed with the C library's floorf and ceilf, an
  integer reference and a hand transcription on all 2^32 binary32 inputs, NaNs compared as NaNs, and its never-step
  plant gave its predicted counts, on one host (MEASURED, `kernel/records/fclink/sweep-real-r1.txt`, sha256
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a, by `tools/ci/check_sweep.py`)
- Grade: DECLARED, MEASURED
- Proof again: never: what C text means is the C standard's and a compiler's (row B006); a C semantics in Coq would
  move the meaning, not the compiler

### B078 BITS32 and FCLINK: libraries outside CI's expected list
- Claim: `bits32.BITS32_Statement.BITS32`, `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `THEOREMS.md`, `docs/engineering/MATHKERNEL-LINUX-CI.md`, `kernel/notes/FCLINK-TRUSTED-2026-11-22.md`
- Stop: their closures hold libraries that CI's expected list does not hold: Flocq's IEEE754.Binary and IEEE754.Bits
  (BITS32), Coq's Strings.Ascii, Strings.Byte and Strings.String (FCLINK)
- Kind: trust
- Covers beyond: each gate rechecked them with coqchk, each clean (MEASURED, console sha256
  aaa537712ed9b44562fa0005dd8189cea8b520cd419f5eefcabd71e639bca71e and
  3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e); they are not in
  `kernel/coq/EXPECTED-CI-LIBRARIES.txt` (MEASURED), so CI's gate-log check is to refuse those two folders until they
  are (ARGUED, `tools/ci/check_gate_log.py`)
- Grade: MEASURED, ARGUED
- Proof again: never: a library is rechecked and pinned by its hash, not proved; rulings A2 (a) and A3 (a) put their
  lines on CI's list in Push A, from the branch run of ruling S280-9 (b)

### B079 FCLINK: the sweep program around the printed lines
- Claim: `fclink.FCLINK_Statement.FCLINK`
- Claimed in: `docs/engineering/MATHKERNEL-LINUX-CI.md`, `docs/GUARANTEES-LEDGER.md`,
  `kernel/notes/FCLINK-TRUSTED-2026-11-22.md`
- Stop: FCLINK speaks of the two printed lines only; the rest of the sweep program (the conversions between binary32
  and binary64, the integer reference, the calls to floorf and ceilf, the counting) is not in it
- Kind: layer
- Covers beyond: the program's comparisons agreed on all 2^32 inputs on one host (MEASURED,
  `kernel/records/fclink/sweep-real-r1.txt`, sha256
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a); that its integer reference is floor and
  ceiling with IEEE 754's rule for the sign of a zero is ARGUED from reading `kernel/coq/fclink/sweep_fc2.c`
- Grade: MEASURED, ARGUED
- Proof again: never: the sweep program is a test harness, not proved code

### B103 BITS32: the record sweep's specification in C
- Claim: the all-bits record sweep of ruling A4 (a) compares each result with SPEC32 of
  `bits32.BITS32_Statement.BITS32`
- Claimed in: `kernel/records/INDEX.md`, `kernel/records/bits32/TRANSCRIPTION.md`
- Stop: the sweep's spec32 (`kernel/records/bits32/bits32_sweep.c`) is SPEC32 transcribed by hand into C integers;
  that it is SPEC32 is not proved
- Kind: trust
- Covers beyond: each Coq line set beside its C line (ARGUED, `kernel/records/bits32/TRANSCRIPTION.md`); a Python
  transcription of the Coq text agreed with spec32 on 4,096 patterns in both directions, and its two plants were
  caught (MEASURED, `kernel/records/bits32/k2-run1-console.txt`, sha256
  29d389f70195eff8de9a2d6876829dc6ea9639eff163294d71712ea87cb00a6e); in run1 spec32 agreed with a second integer
  text on all 2^32 patterns and with the integer reference on every pattern that is not a NaN (MEASURED,
  `kernel/records/bits32/bits32-sweep-run1-console.txt`); Coq's own evaluation of SPEC32 on those patterns has not
  run (NOT_MEASURED)
- Grade: ARGUED, MEASURED, NOT_MEASURED
- Proof again: later: only if Coq prints SPEC32 to C, as FCLINK prints the programs' shapes; no such statement is
  planned

## 4. The DirectX work, whose proof is Push B's

### B080 sqrt32 bit-exact on a Direct3D 12 GPU and on WARP
- Claim: four sqrt32 kernels whose output bits only 32-bit integer operations decide returned the frozen reference's
  bits on all 4,294,967,296 inputs on one hardware GPU; all four also did so on Microsoft's WARP (the first integer
  kernel and the first proposal kernel in their build at DXC's -O0)
- Claimed in: `docs/engineering/GPU-BIT-EXACTNESS.md`, `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: no proof: the kernels' logic over Direct3D's integer semantics is not proved in this tree
- Kind: layer
- Covers beyond: the exhaustive runs and their plants (MEASURED, `docs/engineering/GPU-BIT-EXACTNESS.md`)
- Grade: MEASURED
- Proof again: Push B: the DirectX proof of the kernels K1b and K2b over a model of the unsigned 32-bit subset
  (rulings ST-1 and S280-15 (a)), its model and the shipped HLSL emitted from one source (ruling S280-16 (a))

### B081 Direct3D's integer semantics
- Claim: Direct3D specifies 32-bit integer operations exactly, with no error allowance
- Claimed in: `docs/engineering/GPU-BIT-EXACTNESS.md`
- Stop: the specification itself; its integer chapter was not read
- Kind: trust
- Covers beyond: Microsoft's assembly reference pages and DXC's DXIL.rst, read by research agents (DECLARED,
  `docs/engineering/GPU-BIT-EXACTNESS.md`)
- Grade: DECLARED
- Proof again: never: a vendor's specification is declared, not proved

### B082 DXC, the driver's compiler and the GPU
- Claim: the exhaustive GPU runs of row B080
- Claimed in: `docs/engineering/GPU-BIT-EXACTNESS.md`
- Stop: one DXC release, one driver, one device, and WARP; other vendors and drivers are not measured
- Kind: trust
- Covers beyond: the pinned DXIL operation lists and the exhaustive runs (MEASURED,
  `docs/engineering/GPU-BIT-EXACTNESS.md`); other devices (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: a compiler, a driver and a device are measured per run; the check must run again for each

### B083 Faults and tampering
- Claim: the exhaustive GPU runs of row B080
- Claimed in: `docs/engineering/GPU-BIT-EXACTNESS.md`
- Stop: every result assumes hardware that executes its instructions as specified, in runs no one alters
- Kind: trust
- Covers beyond: a mismatch with the reference shows that a run was wrong, not why (ARGUED,
  `docs/engineering/GPU-BIT-EXACTNESS.md`)
- Grade: ARGUED
- Proof again: never: no proof covers a fault or a person

## 5. The other guarantees and measured sentences

### B090 G3: backends with the proved program's bytes
- Claim: every backend gives the same bytes as the proved program on every input (G3)
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`, `docs/GUARANTEES-LEDGER.md`
- Stop: no library of the kernel exists
- Kind: layer
- Covers beyond: nothing (DESIGNED in `docs/paper/SYSTEM-GUARANTEES.md`)
- Grade: NOT_MEASURED
- Proof again: later: the printers are designed, not built

### B091 G4: the floating-point state checked at entry
- Claim: the admitted floating-point state is checked at entry; conversions on integer bits make the turns kernel
  immune to flush-to-zero and denormals-are-zero (G4)
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`, `docs/GUARANTEES-LEDGER.md`, `kernel/notes/LIMITATIONS.md`
- Stop: no library calls the check; the immunity is argued from measured ranges
- Kind: layer
- Covers beyond: the prototype check held its rows on one Windows host and on GitHub's x86-64 and arm64 runners
  (MEASURED, `kernel/runtime/README.md`); the immunity (ARGUED, `docs/paper/SYSTEM-GUARANTEES.md`)
- Grade: MEASURED, ARGUED
- Proof again: never: a run-time state is checked at entry, not proved

### B092 What the floating-point prototype cannot see
- Claim: the prototype check refuses or reports the states it lists
- Claimed in: `docs/GUARANTEES-LEDGER.md`, `kernel/runtime/README.md`
- Stop: a part of fast-math the compiler does not announce, contraction in another translation unit, a state changed
  after the check, AArch64's FPCR.AH and FPCR.DN
- Kind: input class
- Covers beyond: what clang announces for each target (MEASURED, `docs/GUARANTEES-LEDGER.md` section 3)
- Grade: MEASURED
- Proof again: never: a check of a running program's state cannot see code compiled elsewhere

### B093 G5: every file accounted for
- Claim: every file of the tree is accounted for against the import's manifests (G5)
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`, `docs/GUARANTEES-LEDGER.md`, `PROVENANCE.md`
- Stop: who wrote each file's content
- Kind: trust
- Covers beyond: the manifests check with its plants (MEASURED, `tools/check_manifests.py`); authorship as the files
  say it (DECLARED, `PROVENANCE.md`)
- Grade: MEASURED, DECLARED
- Proof again: never: authorship is declared, not proved

### B094 The checks of tools/ci and the CI judge
- Claim: each checker held on honest inputs and seen to fail on each of its plants; the CI judge bound by MK_ANCHOR_CI
- Claimed in: `docs/engineering/MATHKERNEL-LINUX-CI.md`, `.github/workflows/integrity.yml`
- Stop: a plant shows that a check fails where planted, not that it catches every fault; the judge runs as the judged
  commit's own code (ruling SK-2); the read audit's hook has run on Windows with CPython 3.14 only, not on the
  runner's Linux CPython 3.12
- Kind: trust
- Covers beyond: the tests and their frozen predictions (MEASURED, `tools/ci/tests/run_all.py`); the owner's review
  when he sets MK_ANCHOR_CI (ARGUED, `docs/engineering/MATHKERNEL-LINUX-CI.md`); that on Linux the hook judges the
  same starts and reads, some through other events, and does not see a read relative to a folder's descriptor, which
  shutil.rmtree makes there (ARGUED from the documentation of sys.addaudithook and of the audit events,
  `tools/ci/read_audit.py`)
- Grade: MEASURED, ARGUED
- Proof again: later: a judge taken from a trusted copy is on a later sheet (ruling SK-2)

### B095 The kernel-checked examples of kernel/hardening
- Claim: 32 examples near 2^106, 25 examples about sincos32i and sincos32z, 45 refutations of planted claims and one
  narrowing probe, accepted by coqc and coqchk
- Claimed in: `THEOREMS.md`, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `AGENTS.md`,
  `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`
- Stop: each is a fact at named inputs; none is a candidate statement, and the general lemma the law's proof needs is
  not in this tree
- Kind: input class
- Covers beyond: their consoles (MEASURED, `kernel/hardening/big106/runs/big1-console.txt`,
  `kernel/hardening/examples/runs/ex2-console.txt`, `kernel/hardening/plants/runs/refute4-console.txt`,
  `kernel/hardening/r7-probes/narrow1-console.txt`); that +2^106 is the only such input (MEASURED by the exhaustive
  run, `docs/paper/SYSTEM-GUARANTEES.md` section 5.4)
- Grade: MEASURED
- Proof again: Push B or later: the general lemma comes with the law's proof (row B050)

### B096 Plant labels
- Claim: of the 59 plants of sincos32i and sincos32z, 45 are refuted by a Coq theorem
- Claimed in: `kernel/hardening/plants/PLANT-LABELS.md`, `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `THEOREMS.md`,
  `AGENTS.md`, `kernel/notes/CORRECTIONS-2026-11-16.md` (its item 11)
- Stop: a gate's refusal shows that it rejects a file, not that the plant's claim is false; the 99 plants of the eight
  folders added later have no labels (32 of `sincos32n`, `exp32a`, `floor32` and `ceil32`; 67 of `rti32`, `order32`,
  `bits32` and `fclink`)
- Kind: input class
- Covers beyond: the labels and refutations (MEASURED, `kernel/hardening/plants/PLANT-LABELS.md`)
- Grade: MEASURED
- Proof again: later: labels for the other folders' plants are not scheduled

### B097 The minimal harness
- Claim: the harness held 8 of 8 on sincos32i and sincos32z with the owner's anchors
- Claimed in: `README.md`, `docs/paper/SYSTEM-GUARANTEES.md`, `THEOREMS.md`, `AGENTS.md`
- Stop: it has run on those two folders only; its canaries' expected rows were not written down before their runs
- Kind: input class
- Covers beyond: the harness consoles (MEASURED, `kernel/hardening/harness/runs/h2-held-console.txt`); the canaries
  (ARGUED, `docs/paper/SYSTEM-GUARANTEES.md` section 5.1)
- Grade: MEASURED, ARGUED
- Proof again: later: a run on the other folders is not scheduled

### B098 Ørlǫg's byte-identical backends
- Claim: Ørlǫg's programs are held to byte-identical results on a reference interpreter and Python, C99 and Rust
  backends (measured on its corpus), and its runtimes to 20,015 vectors
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: measured on a corpus, not proved for every program; Skuldd's checks run none of Ørlǫg's
- Kind: input class
- Covers beyond: Ørlǫg's own brief (MEASURED there, `orlog/AGENTS.md`)
- Grade: MEASURED
- Proof again: later: in Ørlǫg's own repository, not in this tree

### B099 Verðandi's deterministic rendering
- Claim: Verðandi renders deterministically
- Claimed in: `docs/paper/SYSTEM-GUARANTEES.md`
- Stop: Skuldd's checks run none of Verðandi's gates
- Kind: trust
- Covers beyond: Verðandi's own brief (DECLARED, `verdandi/AGENTS.md`)
- Grade: DECLARED
- Proof again: later: in Verðandi's own repository, not in this tree

### B100 The orlog/ copy and its original (ruling SY-1)
- Claim: the folder orlog/ is Ørlǫg's tree at its pinned commit 0748adaca1dbb5367f40e7dc5f5906079745b4ba
- Claimed in: `PROVENANCE.md`, `CHANGES-AFTER-IMPORT.md`
- Stop: drift from the original's main is measured at a time, against a clone's last fetch
- Kind: trust
- Covers beyond: on 2026-11-22 the pin lay on origin/main c398820 (2026-11-10), as that clone last fetched it at
  2026-11-22T00:00:50Z: 1,288 files the same, none changed on Skuldd's side, none ahead on the original's (MEASURED,
  `tools/ci/drift.py`, console sha256 d434e85d495a2cd08c935be58807700d97b8537fe4269e68406de3e6923375b9)
- Grade: MEASURED
- Proof again: never: equality with a moving original is measured, not proved; `.github/workflows/drift.yml`
  measures it again on every push and weekly

### B101 The verdandi/ copy and its original (ruling SY-1)
- Claim: the folder verdandi/ is Verðandi's tree at its pinned commit 94d7c28a446cb3df7f0b01d59687f716c9ecb8f8, with
  the changes that CHANGES-AFTER-IMPORT.md lists
- Claimed in: `PROVENANCE.md`, `CHANGES-AFTER-IMPORT.md`
- Stop: drift from the original's main is measured at a time, against a clone's last fetch, which was old
- Kind: trust
- Covers beyond: on 2026-11-22 the pin was origin/main 94d7c28 as that clone last fetched it at 2026-11-17T18:52:22Z
  (GitHub itself not read): 733 files the same, 48 differing on Skuldd's side, each with its classification row,
  none ahead on the original's (MEASURED, `tools/ci/drift.py`, console sha256
  9f6e166cacbd165caa08cc30f0cb45ab9518cc0b400d35bf6617d097b57eee01)
- Grade: MEASURED
- Proof again: never: equality with a moving original is measured, not proved; `.github/workflows/drift.yml`
  measures it again on every push and weekly

### B102 The floor and ceiling sweep job's check
- Claim: the sweep job's check held on one host with clang alone, on both candidate sweeps
- Claimed in: `docs/engineering/MATHKERNEL-LINUX-CI.md`, `kernel/records/INDEX.md`
- Stop: GCC, Linux, arm64 and GitHub's runners have not run it
- Kind: trust
- Covers beyond: the two local runs (MEASURED, `kernel/records/fclink/local-fclink-run1.txt` and
  `kernel/records/floor32/local-p1-run1.txt`, sha256
  39a997d8a41b46799d14de820a5072e2307a3792ce534d21a222f7d32f8968fc and
  55a078802f5024ae568ec1ca593528ee4a2cc9734e02d477c0bced4852d648c7, by `tools/ci/check_sweep.py`; the run on p1 read
  the p1 lines of `tools/ci/SWEEP-SOURCE.txt` before their freeze-list line was added that day, so it has no freeze
  list row); a run on the p1 lines as shipped, its freeze list row included, held 19 of 19 rows on the same host
  (MEASURED, `kernel/records/floor32/local-p1-run2.txt`, sha256
  7fb3982ca930f78768dcf96d37b2f8d036e7af9ed50d36826a7abb234bfa1f9d); and a second run of the candidate fclink on
  this tree once `kernel/coq/fclink` was in it (MEASURED, `kernel/records/fclink/sweep-real-r1.txt`, sha256
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a); on GitHub (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: a sweep measures one machine's outputs; the job adds machines, not proof

### B104 The imported parts' commands run in this tree
- Claim: what the tables of AGENTS.md say each command found on the import does when it is run in this tree
- Claimed in: `AGENTS.md`
- Stop: each command was run on the import (2026-11-17), on one host, or on a model of this layout, or only read, as
  its line says; the runs' consoles are not in this tree, and a later change to the tree could change what a command
  does
- Kind: input class
- Covers beyond: the authors' account in the tables (DECLARED, `AGENTS.md`)
- Grade: DECLARED
- Proof again: never: what a command does on a tree is found by running it, not proved

### B105 The corrections note of 2026-11-16: facts about the gates of sincos32i and sincos32z
- Claim: the value of the frozen shape of sincos32i at 2^-149 (item 6); that the gate never reads the statement field
  of gate.json (item 9); how many of the rows of the gate counts 290 and 288 concern files outside the judged
  theorem's closure, 119 and 166 (item 10)
- Claimed in: `kernel/notes/CORRECTIONS-2026-11-16.md`, `README.md`, `THEOREMS.md`
- Stop: each was computed, run or counted once in the authors' workspace, item 10 by agents and not rechecked; the
  consoles the note names are not in this tree
- Kind: trust
- Covers beyond: the note's own account and grades (DECLARED, `kernel/notes/CORRECTIONS-2026-11-16.md`); that no
  script of the gate reads a field named statement, by a search of `kernel/coq/gate/gate4.py` and the scripts beside
  it (ARGUED, `kernel/coq/gate/gate4.py`)
- Grade: DECLARED, ARGUED
- Proof again: never: a value at one input, what a script reads and a count of rows are computed, read or counted,
  not proved

### B106 Run times in the workflows' comments
- Claim: the run times the comments of the workflows Integrity and MathKernel on Linux give for the tests, the read
  audit and the sweep job's runs, from which their time limits are set, and the time the comment of the tests'
  runner gives for its slowest test on the tree of Push A's batch
- Claimed in: `.github/workflows/integrity.yml`, `.github/workflows/mathkernel-linux.yml`, `tools/ci/tests/run_all.py`
- Stop: measured on one Windows host, some runs beside others; GitHub's runners have not run the eight folders added
  later, the sweep job or the read audit on this tree
- Kind: input class
- Covers beyond: the sweep times, from three of the four sweep-check records (MEASURED,
  `kernel/records/floor32/local-p1-run1.txt`, `kernel/records/fclink/local-fclink-run1.txt` and
  `kernel/records/fclink/sweep-real-r1.txt`); the times of the tests alone, of the read audit and of the slowest
  test, from the authors' runs on that host on 2026-11-22, each console giving its start and end (MEASURED, records
  kept outside this tree, sha256 6c3937c7d1e1d86c7977f5c662aeacc6951d966db962617a22f1d956e49a2bf5 (the tests alone),
  db5f6b84b209cfa9ccace9f06558a20b412fd3f7966fbca9d35ab57bcc36cf99 (the read audit) and
  2b7e2e2f67b7ce13b63e6e080ab3f70b4aca2005352b1e73f27a25c1908e5f24 (test_inventory, beside other runs)); on GitHub's
  runners (NOT_MEASURED)
- Grade: MEASURED, NOT_MEASURED
- Proof again: never: a run time is measured per machine, not proved
