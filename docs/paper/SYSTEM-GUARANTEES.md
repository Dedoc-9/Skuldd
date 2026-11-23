<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Skuldd: Proved Arithmetic, Prose Laws and a Deterministic Studio in One Repository

*Working draft of 2026-11-17, last revised on 2026-11-22 (UTC), written in the form of a systems paper. It reports
what is proved and what is
measured, and grades everything else. Every graded claim carries READ (read in a file), REPORTED (found by others or by agents, not rechecked here), NOT PROVEN, NOT MET or one of five grades: PROVEN (a theorem Coq has checked),
MEASURED (a run on record), DESIGNED (specified, not built), ARGUED (reasoning, not checked by any run) or
NOT MEASURED. Long evidence is collapsed.*

## Abstract

Some real-time simulations, lockstep competitive games among them, need the same numbers on every machine and in every language
that touches the simulation. Floating point gives that only when its behaviour is pinned down: the rounding mode,
contraction into fused operations, extended precision, flush-to-zero, NaN payloads and every library function.
This paper describes a repository that joins three subsystems built apart: **MathKernel**, binary32 functions computed
with binary64 operations and checked in Coq; **Ørlǫg**, a prose language whose programs are held to byte-identical results (measured on 11 programs of its corpus) on
a reference interpreter and on Python, C99 and Rust backends; and **Verðandi**, a deterministic studio and renderer.
The guarantee proved today is narrow and exact: twenty-one statement files about the kernel's functions are proved in
Coq 8.20.1 with Flocq 4.2.1 under exactly four standard axioms (PROVEN). For one function pair, sine and cosine of
2πx, an exhaustive run over all 2^32 binary32 inputs found no result that is not faithfully rounded, every zero with
its required sign, and the one NaN pattern for every non-finite input (MEASURED). The bit-level law that would turn
that measurement into a theorem is stated; this tree holds no proof of it. The code generators that would carry the kernel into C99,
Rust and Python are designed, not built, but for a first printer of two functions' C text: for `floor32` and
`ceil32`, Coq's printer is PROVEN to give the text quoted from an exhaustive sweep program (the quote is checked by
the gate, MEASURED), while what that text means in C is trusted; one for Ørlǫg is planned, not yet designed.
We describe the discipline that keeps these grades honest:
statements fixed before proofs, gates that are shown to fail, the owner's own hashes, and documents that claim
nothing beyond their proofs. We then argue, without measurement, how the merge could shorten work in art, design and
engineering, and say how each argument would be measured.

## 1 Introduction

A lockstep multiplayer game sends inputs, not states, and trusts every peer to compute the same next state. A
replay system stores inputs and trusts the engine to recompute the same frames. A level editor shows a designer a
world and trusts the shipped game to behave the same way. Each of these trusts that arithmetic is deterministic
across machines, compilers and languages. IEEE 754 makes the basic operations deterministic under a fixed rounding
mode; nothing makes the rest deterministic by default. C compilers may fuse a multiply and an add, some by default
outside strict modes (reported, GCC and Clang manuals); 32-bit x86 may compute in extended precision; a program linked
with fast-math startup code may turn on flush-to-zero for every library in the process (reported, Clang manual);
Rust leaves NaN payloads unspecified (reported, RFC 3514); and transcendental functions differ between libraries.

The usual answers are fixed-point arithmetic, which gives up range and precision, or one blessed binary and
platform, which gives up portability. This repository takes a third route: keep binary64 floating point, pin its
behaviour by specification, and prove what each function computes.

**Contributions**, each with its present grade:
1. A discipline for numeric kernels in which each statement is to be written and hashed before its proof, each check
   is to be shown to fail on a planted fault, and the owner, not the author, is to compute the hashes that anchor the
   claims (DESIGNED; in use in part: `compose`'s statement claims no such order, not every check has been shown to
   fail, and the owner holds the statement hashes of ten folders only, `sincos32i`, `sincos32z` and the eight added
   later).
2. Twenty-one proved statement files for binary32 functions computed in binary64 (PROVEN; candidates, section 3).
3. A bit-level law for the turns kernel (sine and cosine of 2πx) that speaks of 32-bit patterns in and out, of both
   conversions, of NaN bytes and of every intermediate value (stated; NOT PROVEN in this tree).
4. An exhaustive measurement of that law over all 2^32 inputs against a correctly rounded oracle (MEASURED).
5. A hardened checking stack: a minimal harness, source rows that refuse risky Coq features, canaries, and
   refutations of planted claims (MEASURED).
6. The design of the merged repository: a shared operations record, one generic correspondence theorem, printers
   to four languages, one tree verdict and one anchors file (DESIGNED).

**What this paper does not claim.** No human outside the authors has read a statement here, and no reader has
confirmed that one says what its owner meant; one model outside the authors' family has read the first thirteen
statement files (G6), and no reader outside that family the eight added later. None is adopted by its owner as final.
Only the gates and feature rows of the first thirteen folders, the manifest check and the floating-point guard
have run beyond one host, on GitHub-hosted runners (§9).
No C99, Rust, Python or Ørlǫg library of the kernel's binary32 functions exists yet; the C sweep programs and Ørlǫg corpus laws of the five older ones (`narrow`, `sqrt32`, `rsqrt32`, `hypot32`, `exp32`) under `verdandi/mathkernel/F32/orl` are unadmitted test renderings. No speed-up for any person's work is measured.

## 2 The three subsystems

**MathKernel.** Each function is first a real-number graph in which every rounding to binary64 is explicit (round to
nearest even, written RN64), proved to be a faithful rounding of the real function on its domain. For the five older
functions, the turns kernel, `floor32` and `ceil32`, though not yet for `log32`, `sin32` or `cos32` on their own, an
IEEE shape writes the same computation once, polymorphic over a record of operations; instantiated at Flocq's binary64
operations, it is tied to the graph by a theorem. For the turns kernel two more layers exist: a zero layer that fixes
the sign of the result wherever the function is exactly zero (that no other result is zero is MEASURED, section
5.3, and PROVEN for the graphs in Flocq's model by `sincos32n`, not at the IEEE level), and the law, stated on 32-bit
patterns. The kernel's folders (`kernel/coq`) hold
twenty-one proved statement files, their proofs, their plants (deliberately wrong files each gate must refuse) and
their freeze lists.

**Ørlǫg.** A program is a numbered legal text. A reference interpreter is its authority by declaration, and three
generated backends, Python, C99 and Rust, are held to byte-identical output on a corpus run four ways, and the C99 and Rust runtimes to 20,015 runtime vectors (READ, Ørlǫg's own brief). Its floats are binary64 with the basic operations only, and every NaN
is made canonical.

**Verðandi.** A deterministic studio over a frozen oracle: worlds are designed, previewed, admitted and undone through
a design tool, and rendered deterministically (READ, its own brief).

## 3 Guarantees

| | Guarantee | Grade today | Evidence | What it does not show |
|---|---|---|---|---|
| G1 | Each of the 21 statement files is implied by its proof, with exactly four standard axioms | PROVEN | each folder's gate; for two folders the stricter harness | that the statements are the right ones; anything about compiled code |
| G2 | The turns kernel on 32-bit patterns: every finite input gives a faithful rounding; zero signs as specified; every infinite or NaN input gives 0x7FC00000; every intermediate finite and moderate | stated, MEASURED on all 2^32 inputs | the T2 sweep (section 5.3), whose transcription and consoles are withheld from this tree with the law | a proof; that the transcription equals the law outside 2,096 sampled patterns; other hosts, compilers or MPFR builds; MPFR's correctness, which is trusted |
| G3 | Every backend (C99, Rust, Python; one for Ørlǫg planned, not yet designed) gives the same bytes as the proved program on every input | DESIGNED | none yet | — |
| G4 | The admitted floating-point state is checked at entry; conversions on integer bits make the turns kernel immune to flush-to-zero and denormals-are-zero | DESIGNED; immunity ARGUED from G2's measured ranges | T2's measured intermediate ranges | a check called at entry: a prototype (`kernel/runtime`; MEASURED on one Windows host with clang 22.1.8, 2026-11-17, and on GitHub-hosted Ubuntu 24.04, x86-64 and arm64, with GCC 13.3.0 and clang 18.1.3, run 44211905832, 2026-11-18 UTC) exists, and no library calls it |
| G5 | Every file of the tree is accounted for: two parts were blob-exact copies of pinned commits at the import, with every later change listed in `CHANGES-AFTER-IMPORT.md`, and the kernel's freeze lists match | MEASURED | the assembler's manifests; 665 of 665 freeze entries at the import | who wrote each file's content |
| G6 | A statement is read by someone outside the authors' model family before its owner adopts it | MET at statement level for the 13 statement files: one model outside the authors' family (ChatGPT, OpenAI), administered by the owner, 2026-11-17; NOT MET for the eight added later (`SINCOS32_NONZERO`, `EXP32_ADJ`, `FLOOR32`, `CEIL32`, `RTI32`, `ORDER32`, `BITS32`, `FCLINK`), which no reader outside the authors' family has read | the review's findings, verified against the files (docs/GUARANTEES-LEDGER.md §1) | that a human outside the authors has read them; that the statements say what their owner meant; the law (G2), which was not in the review |

**G1 in plain words.** The twenty-one statements are candidates: proved, not adopted. A proof shows that a
statement follows from four axioms; it does not show that the statement says what its owner meant. That second
question is why G6 exists, and why the law (G2) is withheld from the published tree until an independent reviewer
has written a blind formalisation of the same convention.

**G2's scope.** Faithful rounding means the result is one of the two binary32 numbers around the real value; it is not
correct rounding, and the measurement shows the difference matters: 762 sine and 14,556 cosine results of
4,278,190,080 are faithful but not correctly rounded (MEASURED). Every NaN input becomes the one pattern 0x7FC00000,
by the owner's ruling; NaN payloads are not kept.

## 4 Design

**One tree, one direction.** Verðandi and Ørlǫg may use the kernel; the kernel's proofs and gates use neither (the `corpus` steps of two of its emitters, `kernel/coq/orl/emit.py` and `emit2.py`, run Ørlǫg's arbiter as a cross-check), and Ørlǫg is optional.
Each part keeps its own brief and its own checks; the root holds what spans them (licence, provenance, the tree
gate to come). Logical names in Coq are permanent once a frozen file imports them: the kernel's twenty-one prefixes
stay, unmoved, and shared code is planned under a new sibling prefix (DESIGNED).

**From hand renderings to one source** (DESIGNED, R7 design sheet). Today there are at least nine hand-kept
renderings of the turns kernel (reported: graph table, generated graph, IEEE shape typed by hand, ties, constants typed twice, zero step,
transcriptions) and two operation records with closed lists of constants. The design replaces them with:
- one operations record with open constants (an integer pair m, e meaning m·2^e), instantiated at Flocq's binary64,
  at the reals with explicit rounding, and at a flagged carrier that checks every intermediate;
- a straight-line program, a list of non-recursive instructions with sharing by index, so tier sources still define
  no recursive function (the source row refuses them);
- one soundness theorem: if every node is safe on the input set, both arms of every selection included, the binary64
  run equals the RN64 run node by node; a separate checker proves safety from light boxes, kept light because the
  independent checker replays every VM computation without the VM;
- printers, written in Coq's own language and evaluated by Coq, from a program to C99, Rust, Python and an
  S-expression, printing constants as 64-bit patterns and conversions as integer bit code. A gate row pins each
  committed file to the printer's output. What the printed text means under a compiler is shown only by sweeps, exhaustive for one-input functions and sampled for `hypot32`; the printers and compilers stay trusted, as in fiat-crypto (reported).

Built since, outside this design: `kernel/coq/fclink/CPrint.v`, a printer of the shapes of `floor32` and `ceil32` to
C text, and FCLINK, which proves that its text is the one `kernel/coq/fclink/KernelText.v` quotes from the sweep
program `kernel/coq/fclink/sweep_fc2.c`, and that, for every input v, every relation between texts and binary64
values that relates the name `x` to v, holds at the shapes' constants and is kept by their operations relates the
printed text to the IEEE computation at v, FC_PARAM (PROVEN; that `KernelText.v` is what its generator prints from
the program, MEASURED by the gate, and that its strings are the program's lines, ARGUED, `BOUNDARIES.md` row B067;
that the two are therefore built from the same operations in the same pattern is a reading, ARGUED in
`kernel/notes/FCLINK-TRUSTED-2026-11-22.md`, section 2). What the C text means stays trusted.

One measurement already supports the record's feasibility: the turns kernel's narrowing and the five older
functions' narrowing are the same term up to their records, accepted by Coq's kernel by reflexivity (MEASURED,
`kernel/hardening/r7-probes`).

**Gates and custody.** Each kernel folder has a gate that compiles it and its dependencies, checks the closing
theorem's type against the frozen statement, reads Print Assumptions and coqchk, and refuses every plant. A minimal
harness runs nothing from the judged tree but coqc and coqchk and reads one recursive coqchk summary strictly. A source
row refuses recursive definitions, checking-flag changes and the Coq features named by the upstream critical-bugs list
that the tier does not use. Under the owner's custody ruling the owner computes the sha256 of each statement and
freeze list; the recorded verdicts of the eleven older folders were given freeze-list hashes the authors computed;
`sincos32i` and `sincos32z` have the owner's own statement hashes and harness anchors, and the eight folders added
later the owner's own statement hashes and freeze-list anchors (the harness has not run on them). Since 2026-11-18
the owner has also set a freeze-list anchor for each of the first 13 folders, which the Linux CI's gates are given
(run 44211905832). For `sincos32i` and `sincos32z` the harness is
given the owner's values, never values read from the tree. Planned: one tree verdict, one append-only anchors file whose head
the owner computes (DESIGNED).

**Language surfaces** (DESIGNED). The same proved program, printed in three programming languages: a C99 header and source taking and
returning 32-bit patterns; a std-only Rust module; a standard-library Python module (Ørlǫg's use of the kernel is planned, not yet designed). Each is usable alone,
and any mix of them gives the same bytes, since each runs the same operations in the same order under the one admitted
floating-point state.

## 5 Evaluation

All runs in this section are on one Windows host, in a pinned container image (Coq 8.20.1, Flocq 4.2.1) with no network; the containers of the hardening runs and of the sweep had the judged files mounted read-only, while the folder gates mount the tree writable and fail their last row if anything in it changed outside their own output folders. Each claim below is MEASURED unless marked; each says what it does not show.

### 5.1 Proof checking

The gates of the first thirteen folders held on 2026-11-14 to 2026-11-16, and those of the eight added later on
2026-11-21 and 2026-11-22 UTC (the gate counts are in the README). The minimal harness held
8 of 8 rows on `sincos32i` and `sincos32z` with the owner's own anchors, both in the workspace and on this tree's
copy; it has not run on the eight folders added later.

<details>
<summary>The harness's rows, its canaries, and what they do not show</summary>

Rows: (1) the freeze list's sha256 is the owner's anchor; (2) the list is well formed; (3) every listed file has its
listed sha256; (4) the list covers the import closure; (5) a fresh root holds exactly the listed sources; (6) they
compile in import order; (7) the harness's own check file types the theorem by the statement and Print Assumptions
lists exactly the four axioms; (8) one recursive coqchk, its whole summary read strictly. Canaries, each run once:
a wrong anchor failed row 1 only; one changed byte in a comment failed rows 3 and 5 only (the compiled objects were
byte-identical to the clean tree's, so only the byte rows see a comment change); an admitted top theorem with the
list rewritten to match failed rows 7 and 8; an unlisted import failed row 4 and, as a consequence, rows 6 to 8. The
expected rows were not written down before that run, so the match is ARGUED. Not shown: another host; a Coq release
other than 8.20.1; that the harness itself is right, since it was written by the same authors (its reading by the
reviewer is pending).

</details>

### 5.2 The checks fail when they should

The authors found two gaps in their own first source row: it scanned one line at a time, and it did not read strings
inside comments as Coq does. Both were shown to be real, in Coq, before being fixed: a checking-flag command split over
two lines really switched guard checking off, and a quoted `*)` inside a comment really hid a command (Coq itself
warns about it). Even then, the effect of a hidden unguarded fixpoint reached coqchk's summary, and the harness refused
it: the gap was in the source row only. Version 2 fixed both, and version 3 added refusals for every critical-bugs
trigger the tier does not use; each version had its predictions written before its run, and each prediction held.

<details>
<summary>The plants and their labels</summary>

Of the 59 plants of `sincos32i` and `sincos32z`, 45 are refuted by a Coq theorem (the planted claim is shown false at a
named input, by vm_compute only), 4 are possibly-true variants, none is function-equivalent, and 10 change no
statement and are refused by the assumption reading or by compilation. A refusal by a gate shows that the gate
rejects the file, not that the planted claim is false; the refutations show the latter for 45 of them. The 99 plants
of the eight folders added later are not labelled.

</details>

### 5.3 Exhaustive measurement of the turns kernel

A C transcription of the turns kernel's law, first shown equal bit for bit to Coq's own evaluation of the law at
2,096 patterns, was run on all 2^32 inputs beside GNU MPFR's correctly rounded sine and cosine of 2πx, with ten
predictions written before the run. All ten held.

<details>
<summary>Counts, digests and what the sweep does not show</summary>

Not faithful: 0 of 4,278,190,080 finite inputs, for both functions. Sine zero results 1,795,162,112 (897,581,056 of
each sign), each with the input's sign, exactly where 2x is a whole number; cosine zero results 16,777,216, all +0,
exactly where 4x is an odd whole number. All 16,777,216 infinite and NaN inputs give 0x7FC00000. No value computed on a
finite input is non-finite, and each is a zero or of magnitude between 2^-400 and 2^400 (smallest 0x1.810231811663dp-301,
largest 2^128 - 2^104). The integer-bit conversions equal the hardware conversions on every finite input and result.
Reported, not predicted: results equal to MPFR's round to nearest, sine 4,278,189,318 and cosine 4,278,175,524. Wall time 1,146 s on
12 worker processes. Digests of the results: sine 93a4a68e97524b7d7a235f135260ede57f23ab510f00fc10ca85245876d7e694,
cosine 8eaa582fa2c0b97566447b9cf0b06f1e189e83825f02d0b990fec9c466adeaf7. Not shown: a proof; that the transcription
equals the law outside the 2,096 sampled patterns (a planned Coq run over all inputs would compare per-block
digests); another host, compiler or MPFR build; MPFR's own correctness, which is trusted.

</details>

### 5.4 An unusual input

The kernel's reduction computes N(x) = (x + C) − C with C = 3·2^51 to find the nearest whole number. For every
binary32 input of magnitude at least 2^23, which is already a whole number, N(x) = x except at x = +2^106, where the
addition rounds back to x and the subtraction, starting from the bottom of a binade, rounds down to 2^106 − 2^53. The
values that follow (f = 2^53, q = k = 2^55, r = +0) are all discarded by the kernel's selections, and both functions
still return the right results, +0 and 1. Thirty-two Coq examples, accepted by coqc and a recursive coqchk, give the values at ±2^106 and N and r at +2^104, +2^105, +2^107 and the two binary32 neighbours of +2^106 (MEASURED, `kernel/hardening/big106`); that it is the only such input is MEASURED by the exhaustive sweep and
ARGUED by a short derivation; this tree holds no proof of the general lemma the law's proof needs.

### 5.5 Trusting Coq

Coq's own project keeps a list of critical bugs. Read entry by entry (REPORTED; agents of the authors' family, with an
adversarial check that upheld 45 of 46 labels and found no entry missing), 45 entries affect Coq 8.20.1 and one is
unclear. The check refuted one label: the tier's `field` calls reach the `vm_cast_no_check` of entry #16891, which coqchk's re-check without the VM covers, like the VM entries below. For the others, the reading found no trigger in the tier's own sources:
- the triggers of most are constructs the tier does not use, which the version-3 source row now refuses on every
  run (MEASURED: it holds on the tier and refuses each of its plants);
- the tier does use Coq's virtual machine (vm_compute, and the lia, lra, ring and field tactics build VM casts), so
  the VM entries are covered by a different fact: every proof is re-checked by coqchk, which does not use the VM;
- fifteen entries could be reached only through library code, chiefly guard-checker and module-system bugs; closing
  them needs a second, later Coq release to re-check the libraries, which needs a download and the owner's word.

### 5.6 Assembly and provenance

The import commit's tree is built by one script from three sources; every later change is listed in `CHANGES-AFTER-IMPORT.md`. Ørlǫg and Verðandi are taken blob by blob at pinned commits, each
blob's git object id recomputed; the Verðandi tree is the one the owner's own check held. The kernel is copied byte
for byte and its 13 freeze lists (665 entries) are checked against the copy. A privacy and naming scan of the whole tree was run outside it; the changes it led to are listed, with the rulings they carry out, in `CHANGES-AFTER-IMPORT.md`.

## 6 How the merge could speed art, design and engineering

*Everything in this section is ARGUED. None of it is measured. Each subsection ends with how it would be measured.*

**Art.** An artist works in a tool (Verðandi's studio, or another editor fed by it) and the result ships in a
runtime. When the tool and the runtime compute geometry, animation curves and procedural placement with the same
proved functions, printed into each language from one source, what the artist sees and what ships can be the same
bytes. That removes a class of late surprises: a prop that clips on one platform, a procedural forest that grows
differently in the build. *Measure:* across a corpus of scenes, count the pixel or geometry differences between the
tool's preview and the shipped build on each platform, with and without the shared kernel.

**Design.** Byte-identical recomputation makes every design change a clean experiment: replay the same inputs before
and after, and the only differences are the change's own. Ørlǫg adds a layer a designer can read: rules written as
numbered prose, whose outputs are held byte-identical across four executions on Ørlǫg's corpus; all four read the prose through one shared front end. *Measure:* the time to find which change
caused a behaviour difference (a bisection over recorded sessions), with exact replay against approximate replay.

**Engineering.** One source for each function replaces several hand-kept renderings in several languages, so a fix
is made once. For the turns kernel, the proofs fix, at binary64, the sign of the result at each exact zero and a NaN
result for each non-finite input; of the other functions, only `floor32` and `ceil32` state such rules (the sign of
every finite result, and every infinite or NaN input returned as it is, in Flocq's model with one NaN). Finite
intermediates in discarded branches are a clause of the turns kernel's law, measured (section 5.3), not proved in
this tree. Lockstep networking stops needing float workarounds when every peer
computes the same bits. The gates catch regressions before review. *Measure:* defects per thousand lines in numeric
code; desynchronisation rate in lockstep soak tests across platforms; time from a numeric fix to its release in all
languages.

**The symbiosis.** Each part gives the others something they lack. The kernel would give Ørlǫg and Verðandi functions whose Coq shapes are proved, not just tested, once printers carry them into code (G3, DESIGNED). Ørlǫg would give the kernel a fourth execution path and a readable
law layer, and its discipline of byte-identical backends is the model for the kernel's printers. Verðandi gives the
kernel a demanding consumer and a visual oracle: a deterministic renderer shows a wrong result as a difference in its output bytes when the error reaches a pixel, which a one-bit error need not do.
All three share one way of working: claims graded, checks shown to fail, records changed only by the owner's ruling and listed (`CHANGES-AFTER-IMPORT.md` lists each change after the import, file by file, with the ruling it carries out).

## 7 Prior art

Pages below were opened by research agents for this work (REPORTED); none is copied.

- **Correct rounding and exhaustive testing.** CORE-MATH provides correctly rounded functions, checks its univariate binary32
  functions exhaustively (bivariate ones on known hard cases), and has functions in GNU libc (core-math.gitlabpages.inria.fr). RLIBM approximates the
  correctly rounded result with one polynomial for several formats; LLVM's logf and log2f use RLIBM's polynomials, and LLVM's expf and exp2f RLIBM's range reduction
  (people.cs.rutgers.edu/~sn349/rlibm). LLVM's libc aims at correct rounding in all rounding modes and tests every
  input of its univariate single-precision functions (libc.llvm.org/math). These give stronger rounding than this kernel's faithful rounding, by
  testing and analysis; this kernel gives weaker rounding with machine-checked proofs; its bit-level rules for NaN,
  zero signs and intermediates, for the turns kernel, are a law that is stated and measured, withheld from this tree
  and not proved in it; for `floor32` and `ceil32` the sign of every finite result is proved, in Flocq's model with
  one NaN.
- **Verified floating point in proof assistants.** Flocq formalises IEEE 754 in Coq and underlies this work.
  VCFloat proves round-off error bounds of floating-point expressions against exact reals
  (github.com/VeriNum/vcfloat); its expressions hold no selection and no shared stage, and its claim is a bound, where
  this kernel's is exact equality with a graph that rounds explicitly. CoqInterval and Gappa prove interval and
  rounding facts; CoqInterval's own program representation, with integer constants, sharing and one simulation
  theorem, is the nearest precedent for the planned design (sources.debian.org, coq-interval 4.11.1).
- **Code generated from proofs.** fiat-crypto prints C, Rust, Go and more from one Coq development and states that it
  gives no quality guarantee for the generated code beyond its proofs (github.com/mit-plv/fiat-crypto); bedrock2
  prints C from Coq without extraction (github.com/mit-plv/bedrock2); HACL* ships verified C (github.com/hacl-star/hacl-star).
  The planned printers follow their discipline: committed output pinned to the printer, printers trusted.
- **Language-level floating point.** Rust specifies its basic operations as IEEE 754 and leaves NaN payloads open
  (rust-lang.github.io/rfcs/3514-float-semantics.html); GCC and Clang contract into fused operations by default
  outside strict settings (gcc.gnu.org, clang.llvm.org); Python packs binary32 and binary64 as IEEE everywhere
  (docs.python.org). These facts set the build flags and the integer-bit conversions of the design.

What is different here: exact equality with an explicitly rounded graph rather than an error bound; a law on bit
patterns that covers NaN bytes, zero signs and discarded branches (stated and measured; withheld from this tree and
not proved in it); and a custody discipline in which the owner, not the author, holds the hashes (so far the
statement and harness hashes of `sincos32i` and `sincos32z` and of the law, the statement hashes and freeze-list
anchors of the eight folders added later, and since
2026-11-18 the freeze-list anchors of the first 13 folders, which the Linux CI is given).

## 8 Intellectual property

- **Ownership and authorship.** The repository's owner holds it. Apart from the licence text in its three `LICENSE` files (the Free Software Foundation's) and nine fdlibm 5.3 source files in `verdandi/mathkernel/ORACLE/src` (written by Sun Microsystems and carried with their notices as the oracle of `verdandi/mathkernel`), its text, code and proofs were written by the owner and by AI assistants working for him, as its records state. How copyright applies to machine-written parts is a
  legal question this paper does not answer.
- **Licences.** The repository, apart from nine fdlibm 5.3 files under Sun Microsystems' notice (`verdandi/mathkernel/ORACLE/src`), is offered under the GNU Affero General Public License version 3 only, whose exact text
  is in `LICENSE` (the same bytes as in the Ørlǫg and Verðandi repositories), and under a separate commercial licence
  from the copyright holder; `LICENSING.txt` gives the contact, in plain text.
- **Third parties.** Coq (LGPL-2.1), Flocq (LGPL-3), GNU MPFR (LGPL-3.0 or later) and the compilers are tools the
  build runs; none is copied into the tree. CoqInterval (CeCILL-C) was studied for its pattern; none of its code was
  copied. Verðandi's art
  layer names engine content by path for an optional integration, under that engine's licence; no such content is in
  the tree. Nine fdlibm 5.3 source files (Sun Microsystems, under a permissive notice that must be kept) are copied into `verdandi/mathkernel/ORACLE/src` as the oracle of `verdandi/mathkernel`. `THIRD-PARTY.md` lists what was checked.
- **Patents and trademarks.** The AGPL-3.0's section 11 grants a patent licence from each contributor for its
  contribution; this paper makes no patent claim. Names of other products belong to their owners.
- **Contributions.** Because of the commercial licence, contributions from others need terms that let the holder
  license them both ways; until such terms exist, none is accepted.
- This section describes; it is not legal advice.

## 9 Limitations and threats to validity

One host ran everything this paper measures. Later, GitHub-hosted runners, one per job, reran the 13 gates against
the owner's anchors and the floating-point guard on x86-64 and arm64 with GCC and clang (run 44211905832), and the
manifest check and the feature rows (run 44211905905), on 2026-11-18 UTC, with Coq 8.20.1 and Flocq 4.2.1 built
from opam (MEASURED): machines other than the one host and a second build of the same releases, not a second Coq
release. Those were the gates of the first 13 folders; the gates of the eight added later have run on the one host
only. One model family wrote and checked the statements, the proofs and the checks, and agreement
within one family is corroboration, not proof. Coq's kernel and checker share one code base. MPFR, the compilers,
the meaning in C of the text FCLINK's printer prints, and the printers to come are trusted. The twenty-one statements
are candidates, not adopted. This tree holds no proof of
the law
of section 3. The benefits of section 6 are not measured. No GPU result is part of this guarantee;
`docs/engineering/GPU-BIT-EXACTNESS.md` says how a GPU kernel can stay outside Direct3D's 32-bit floating-point
latitude, and what one device measured.

## 10 Conclusion

The repository's present guarantee is small and exact: twenty-one proved statement files that a reader can check,
two function pairs measured exhaustively on one host (sine and cosine of 2πx; floor32 and ceil32, whose sweep
records are in `kernel/records/`), and a record of every file's origin. Its design shows how the same proved source can
reach four languages and a studio without any claim outrunning its evidence. The next steps are the ones that change a
grade: the law's proof, the printers, the exhaustive measurements on a second host, and a second Coq release.
