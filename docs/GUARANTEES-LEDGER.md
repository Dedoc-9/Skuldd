<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Guarantees ledger: what is proved, built, enforced, measured and shippable

Five kinds of assurance are kept apart here, because one is easily read as another: a green CI run is not a proof, a
proof about Flocq's operations is not a fact about a compiled program, and a runtime check is not a guarantee. Each
line has its grade and where it stands. The grades: PROVEN (a theorem, checked), MEASURED (a run, on what it ran on),
READ (read in a file), REPORTED (said by someone and not rechecked here), ARGUED (an inference), DESIGNED (a design,
nothing built), NOT MEASURED (not run), NOT stated (no statement says it), NONE (nothing exists). Where a row is one of
the paper's guarantees (`docs/paper/SYSTEM-GUARANTEES.md` §3), its number is given; the paper's own wording governs.
Grades that depend on time are dated; this ledger was written on 2026-11-17 and regraded from the first runs of the
Linux CI, of 2026-11-18 UTC. The rows on the eight folders added later (`sincos32n`, `exp32a`, `floor32`, `ceil32`,
`rti32`, `order32`, `bits32`, `fclink`) were written or changed on 2026-11-22 UTC.

## 1. Mathematical guarantees: theorems about models

| Claim | Grade | Where |
|---|---|---|
| Each of the 21 statement files is implied by its proof, with exactly four standard axioms (G1) | PROVEN, in Coq 8.20.1 with Flocq 4.2.1, rechecked by coqchk; candidates, not adopted | `THEOREMS.md`; each folder's gate |
| The statements of the first thirteen folders and of `floor32` and `ceil32` are about Flocq's real-number rounding model (`format32`, `RN64`) and, for `ieee64`, `compose`, `sincos32i`, `sincos32z`, `floor32` and `ceil32`, Flocq's IEEE binary64 operations: the final result is finite and equals the model's value. The other six (`SINCOS32_NONZERO`, `EXP32_ADJ`, `RTI32`, `ORDER32`, `BITS32`, `FCLINK`) state what their rows below say | PROVEN, on each statement's own premises | the statement files |
| Every intermediate IEEE operation is finite | NOT stated | (a successor statement is proposed) |
| The sign of a zero result, a NaN's payload, exception flags, traps | NOT stated, except `sincos32z`'s zero signs and NaN on non-finite inputs, and the sign of every finite result of `floor32` and `ceil32` (`FL_SIGN`, `CL_SIGN`), which return every infinite or NaN input as it is, in Flocq's model with one NaN (no payload); `BITS32` states the bits its integer specification SPEC32 gives a NaN pattern (the quiet bit set, every other bit kept), not which NaN the program returns | `sincos32z/SINCOS32_IEEE_Zero_Statement.v`; `floor32/FLOOR32_Statement.v`, `ceil32/CEIL32_Statement.v`; `bits32/BITS32_Statement.v` |
| An IEEE binary64 correspondence for `log32`, `sin32` and `cos32` (the radian functions), and one packaged end-to-end statement for sine and cosine | NOT stated: Flocq's IEEE type occurs only in `ieee64`, `compose`, `sincos32i`, `sincos32z`, `floor32`, `ceil32`, `rti32`, `order32`, `bits32` and `fclink`, and none of them covers these | (successor statements are proposed) |
| That `XMAX` is the largest binary32 input of `exp32`: `XMAX` and `11629080/131072` binary32 numbers with none between them | PROVEN by `EXP32_ADJ` (`exp32a`), in Flocq's model without overflow: both are binary32 numbers, none lies between them, and no faithful binary32 rounding of exp at `11629080/131072` is finite; inputs above it, and what an IEEE program returns there, are not stated. `EXP32_SHARP` (`exp32r`) is the numeric fact `2^128 < exp(11629080/131072)` alone | `exp32a/EXP32_ADJ_Statement.v`; `exp32r/RANGE_Statement.v` |
| That `sinturn32` and `costurn32` are not zero away from their exact points | PROVEN by `SINCOS32_NONZERO` (`sincos32n`) for the graphs `g_sinturn32` and `g_costurn32` at every number of the binary32 format, in Flocq's model; not stated at the IEEE level (the shapes of `sincos32i` and `sincos32z`). `SINCOS32_Statement.v` itself does not state it, and says so | `sincos32n/SINCOS32_NONZERO_Statement.v`; `sincos32/SINCOS32_Statement.v` |
| That `floor32` and `ceil32` compute IEEE 754's roundToIntegralTowardNegative and roundToIntegralTowardPositive on binary32 and non-finite inputs | PROVEN by `RTI32` (`rti32`), in Flocq's model with one NaN, against the standard's clauses as transcribed from a paraphrase of the 2008 text, which no one has set beside the standard's text; Flocq's `Bnearbyint` is exactly those clauses; exception flags, signalling NaNs and NaN payloads NOT stated | `rti32/RTI32_Statement.v` |
| How the results of `floor32` and `ceil32` are ordered and how the two relate (as real numbers, under `Bleb`, under totalOrder on values that are not NaN; a difference of 0 or 1; fixed points; negation; idempotence; monotonicity) | PROVEN by `ORDER32` (`order32`), on binary32 inputs (some parts also on non-finite ones), in Flocq's model with one NaN; totalOrder where a NaN is compared NOT stated (on bit patterns it fails for signalling NaNs: REPORTED by a research agent, measured on one host) | `order32/ORDER32_Statement.v` |
| All 32 bits of the binary32 results of `floor32` and `ceil32` on every pattern that is not a NaN | PROVEN by `BITS32` (`bits32`), over Flocq's Binary binary32 and its Bits encoding: an integer specification SPEC32 of all 2^32 patterns whose values and signs are the floor and the ceiling; on every pattern that is not a NaN the program's binary64 result is the widening of SPEC32's binary32, and every binary32 whose widening is that result has SPEC32's bits. That a processor's widening and store are the modelled ones, and which NaN the program returns, NOT stated (what was measured of NaN results, on one host: `BOUNDARIES.md`, row B075) | `bits32/BITS32_Statement.v` |
| The C text of the shapes of `floor32` and `ceil32` | PROVEN by `FCLINK` (`fclink`): Coq's printer (`fclink/CPrint.v`) applied to each shape gives the text of `fclink/KernelText.v`, which the gate checks is what `fclink/gen_kernel_text.py` quotes from the sweep program `fclink/sweep_fc2.c` (MEASURED); the printed text and the IEEE computation are related by every relation that the shapes' operations keep (`FC_PARAM`). What the C text means in C is NOT stated: it is trusted | `fclink/FCLINK_Statement.v` |
| That F32's relative constant 2^-27 is the largest that works | NOT stated, and not so: the limit is near 2^-25 (a pair at relative distance 2^-25 (1 + 6e-8) whose RN32 is not faithful, MEASURED with exact rationals; that 2^-25 itself suffices, ARGUED). F32 is true as stated | `f32/F32_Statement.v` |
| The turns kernel's law on 32-bit patterns (G2) | stated; this tree holds no proof of it | `THEOREMS.md` |

## 2. Implementation guarantees: code against the model

| Claim | Grade | Where |
|---|---|---|
| A C99, Rust or Python library of the kernel gives the bytes of the proved program on every input (G3) | DESIGNED; no library exists | the paper §4 |
| The C sweep programs and Ørlǫg corpus laws under `verdandi/mathkernel/F32/orl/` | MEASURED as `verdandi/mathkernel/F32/CLAIMS.md` §6 and §7 say, each with its own scope: the outputs of one compiler's programs on one processor; unadmitted test renderings, not a library | `verdandi/mathkernel/F32/CLAIMS.md` |
| A compiler emits, or a processor executes, the modelled operations in the modelled order | NONE for the order of operations: no theorem or check covers it; the sweeps above check outputs only | — |
| Every file of the tree is accounted for against the import's manifests (G5) | MEASURED: `tools/check_manifests.py`, every row with its plants | `PROVENANCE.md`; `CHANGES-AFTER-IMPORT.md` |

## 3. Runtime guarantees: the floating-point state a program runs in

| Claim | Grade | Where |
|---|---|---|
| G4, in the paper's words: the admitted floating-point state is checked at entry; conversions on integer bits make the turns kernel immune to flush-to-zero and denormals-are-zero | DESIGNED; the immunity ARGUED (the paper's grade); not enforced: no library exists to call a check | the paper §3 G4 |
| What the build must ensure, since no run-time check can: no contraction into fused multiply-adds, no fast-math or any of its parts, no excess precision (x87) | the strict flags of the library's own build; refused at compile time only where the compiler announces them (below) | `kernel/runtime/README.md` |
| A prototype check, `kernel/runtime/mk_fpenv.{h,c}`: compile-time refusal of what the compiler announces (fast-math and its parts, finite-math, `__GCC_IEC_559 == 0`, excess precision); run-time probes and canaries (rounding, ties to even, flush-to-zero, denormals-are-zero, contraction in its own unit); register reads: x86-64 MXCSR (rounding, FZ, DAZ, exception masks), AArch64 FPCR (rounding, FZ, FIZ, trap enables) | MEASURED with plants and mutants: on 2026-11-17 on one x86-64 Windows host with clang 22.1.8, 13 of 13 rows; on 2026-11-18 UTC on GitHub-hosted Ubuntu 24.04 with GCC 13.3.0 and clang 18.1.3, x86-64 26 of 26 rows and arm64 21 of 21 (run 44211905832) | `kernel/runtime/README.md` |
| What the prototype cannot see | a part of fast-math the compiler does not announce: clang announces `-freciprocal-math`, `-fno-signed-zeros` and contraction only on MSVC-environment targets, `-fassociative-math` alone nowhere, and on Linux targets none of them (MEASURED, clang 22.1.8, by preprocessing for each target); contraction or any optimisation in another translation unit; a state changed after the check; AArch64's FPCR.AH and FPCR.DN; any processor other than x86-64 and AArch64 beyond what the probes show | `kernel/runtime/mk_fpenv.h` |
| A runtime check can undo a compiler's fast-math optimisation already compiled into a program | false in general: a check reads the processor's state, not the code; the library must be built as its own artifact with strict flags | — |

## 4. Portability evidence: where it was measured

| Evidence | Grade | Where |
|---|---|---|
| The first 13 gates held; the minimal harness on `sincos32i` and `sincos32z`, its second version on `sincos32z` | MEASURED on one x86-64 Windows host, inside Linux containers (Debian, Coq 8.20.1 and Flocq 4.2.1 from Debian packages) | `THEOREMS.md`; the gate consoles |
| The same gates on GitHub-hosted Ubuntu 24.04 with Coq 8.20.1 and Flocq 4.2.1 built from opam | MEASURED on 2026-11-18 UTC: all 13 gates held against the owner's anchors, each with its anchored row and `THEOREMS.md`'s count (runs 44211905832 and 44211854754, commit 01c174bd); the first attempt of each, made before the anchors were set, refused in all 13 gates. The manifest check and the 13 feature rows held (runs 44211905905 and 44211854876) | `.github/workflows/mathkernel-linux.yml`, `docs/engineering/MATHKERNEL-LINUX-CI.md` |
| The gates of `sincos32n`, `exp32a`, `floor32` and `ceil32` held with `--recheck`, against anchors equal to the owner's own sha256 of each freeze list | MEASURED on the same one host, in the same container image as the gate records kept in this tree (its id compared), on 2026-11-21 and 2026-11-22 UTC, each on a copy of `kernel/coq` (`THEOREMS.md` says how it differs); the Linux CI has not run them | `THEOREMS.md`, which names each console by its sha256; `kernel/records/INDEX.md`, which lists them with the folders' other gate runs (red ones included) and sweep records |
| The gates of `rti32`, `order32`, `bits32` and `fclink` held with `--recheck`, against the owner's own sha256 of each freeze list | MEASURED on the same one host, in the same container image (its id compared), on 2026-11-22 UTC, the last of three runs each (a rehearsal and a recheck before it, given the same value as the authors computed it), each on a copy of `kernel/coq` (`THEOREMS.md` says how it differs); the Linux CI has not run them | `THEOREMS.md`, which names each console by its sha256; `kernel/records/INDEX.md`, which lists them with each folder's rehearsal and recheck runs (none red) and the sweep records |
| The floating-point state guard's gate on GitHub-hosted Ubuntu 24.04, x86-64 and arm64, with GCC and clang | MEASURED on 2026-11-18 UTC: x86-64 26 of 26 rows, arm64 21 of 21 (GCC 13.3.0, clang 18.1.3; run 44211905832) | `.github/workflows/mathkernel-linux.yml` |
| The turns kernel's exhaustive measurement and the F32 sweeps | MEASURED on the same one host (GCC 14.2.0, clang 22.1.8, rustc 1.96.1) | the paper §5.3; Verðandi's `CLAIMS.md` |
| The floor32 and ceil32 sweeps: the first exhaustive sweep, the sweep of FCLINK's printed lines and the all-bits record sweep | MEASURED on the same one host with clang 22.1.8, from 2026-11-18 to 2026-11-22 UTC, each held in every run that `kernel/records/INDEX.md` and `BOUNDARIES.md` row B102 list (the first sweep's own two runs and the sweep job's check on it, the check on the printed lines, and the all-bits sweep); NaNs compared as NaNs except in the all-bits sweep | `kernel/records/INDEX.md`; `BOUNDARIES.md` rows B063, B064, B075, B077 and B102 |
| Any machine other than the one host and GitHub-hosted runners, an operating system on bare hardware, an ARM processor for anything but the guard, or MSVC | NONE as of 2026-11-18 UTC | — |

## 5. Product readiness

| Product | Grade | What it lacks |
|---|---|---|
| A C99, Rust or Python package of the kernel | NONE | G3, G4, a bit-level contract written down (NaN, flags, signed zero, out-of-domain inputs), multi-host evidence |
| A deterministic game or physics SDK | NONE | the package above, and an end-to-end lockstep simulation measured across hosts |
| A bit-exact fp32 inference runtime | NONE | beyond `exp32`, `rsqrt32` and the turns kernel: deterministic matrix products, reductions, softmax, normalisation and quantisation |
| A service that gates AI-written code with these checks | NONE | sandboxing, supply-chain controls, machine-readable attestations, tests on hostile projects, a pilot |

## Outside reading (G6)

| Event | Grade |
|---|---|
| The 13 statement files read at statement level by one model outside the authors' model family (ChatGPT, OpenAI), administered by the owner, 2026-11-17 | REPORTED: the owner's account; the review's text is not in this tree. The paper's G6 row gives the owner's grade for it |
| What that reading found, checked against the files by agents of the authors' family (READ) | in §1: `XMAX`'s maximality, the non-zero results of `sinturn32` and `costurn32`, the IEEE correspondence for `log32` (the review named it; `sin32` and `cos32` were added by the check) and a packaged end-to-end statement for sine and cosine. Its point on P32's comment about `SQRT32` was already recorded and answered by `p32r`; its other points describe the statements. None of its claims was found false. F32's constant was found by the check, not by the review |
| A reading of the eight statement files added later (`SINCOS32_NONZERO`, `EXP32_ADJ`, `FLOOR32`, `CEIL32`, `RTI32`, `ORDER32`, `BITS32`, `FCLINK`) by anyone outside the authors' model family | NONE as of 2026-11-22 |
| A reading by a human outside the authors | NONE as of 2026-11-17 |
