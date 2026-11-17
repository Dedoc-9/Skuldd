<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Guarantees ledger: what is proved, built, enforced, measured and shippable

Five kinds of assurance are kept apart here, because one is easily read as another: a green CI run is not a proof, a
proof about Flocq's operations is not a fact about a compiled program, and a runtime check is not a guarantee. Each
line has its grade (PROVEN, MEASURED, READ, DECLARED, DESIGNED, NOT MET, NONE) and where it stands. The paper's G1 to
G6 (`docs/paper/SYSTEM-GUARANTEES.md` §3) are the same claims, by number.

## 1. Mathematical guarantees: theorems about models

| Claim | Grade | Where |
|---|---|---|
| Each of the 13 statement files is implied by its proof, with exactly four standard axioms (G1) | PROVEN, in Coq 8.20.1 with Flocq 4.2.1, rechecked by coqchk; candidates, not adopted | `THEOREMS.md`; each folder's gate |
| The statements are about Flocq's real-number rounding model (`format32`, `RN64`) and, for `ieee64`, `sincos32i`, `sincos32z`, Flocq's IEEE binary64 operations: the final result is finite and equals the model's value | PROVEN, on each statement's own premises | the statement files |
| Every intermediate IEEE operation is finite | NOT stated | (a successor statement is proposed) |
| The sign of a zero result, a NaN's payload, exception flags, traps | NOT stated, except `sincos32z`'s zero signs and NaN on non-finite inputs | `sincos32z/SINCOS32_IEEE_Zero_Statement.v` |
| An IEEE binary64 correspondence for `log32`, `sin32` and `cos32` (the radian functions), and one packaged end-to-end statement for sine and cosine | NOT stated: Flocq's IEEE type occurs only in `ieee64`, `sincos32i` and `sincos32z` | (successor statements are proposed) |
| That `XMAX` is the largest binary32 input of `exp32`: `XMAX` and `11629080/131072` binary32 numbers with none between them | NOT stated: `EXP32_SHARP` is the numeric fact `2^128 < exp(11629080/131072)` alone; the rest is in comments and was measured, not proved | `exp32r/RANGE_Statement.v` |
| That `sinturn32` and `costurn32` are not zero away from their exact points | NOT stated, and said so | `sincos32/SINCOS32_Statement.v` |
| That F32's relative constant 2^-27 is the largest that works | NOT stated, and not so: the limit is near 2^-25 (a pair at relative distance 2^-25 (1 + 6e-8) whose RN32 is not faithful, MEASURED with exact rationals; that 2^-25 itself suffices, ARGUED). F32 is true as stated | `f32/F32_Statement.v` |
| The turns kernel's law on 32-bit patterns (G2) | stated; this tree holds no proof of it | `THEOREMS.md` |

## 2. Implementation guarantees: code against the model

| Claim | Grade | Where |
|---|---|---|
| A C99, Rust or Python library of the kernel gives the bytes of the proved program on every input (G3) | DESIGNED; no library exists | the paper §4 |
| The C sweep programs and Ørlǫg corpus laws under `verdandi/mathkernel/F32/orl/` | MEASURED as `verdandi/mathkernel/F32/CLAIMS.md` §6 and §7 say, each with its own scope; unadmitted test renderings, not a library | `verdandi/mathkernel/F32/CLAIMS.md` |
| A compiler emits, or a processor executes, the modelled operations in the modelled order | NONE: no theorem or check covers a compiler or a processor | — |

## 3. Runtime guarantees: the floating-point state a program runs in

| Claim | Grade | Where |
|---|---|---|
| The admitted floating-point state (binary64, round to nearest even, no flush-to-zero, no denormals-are-zero, no contraction, never x87) is checked at entry (G4) | DESIGNED; not enforced: no library exists to call a check | the paper §3 G4 |
| A prototype check, `kernel/runtime/mk_fpenv.{h,c}`: compile-time refusal of what the compiler announces (fast-math and its parts, finite-math, excess precision); run-time probes and canaries (rounding, ties to even, flush-to-zero, denormals-are-zero, contraction in its own unit); x86-64 MXCSR and AArch64 FPCR reads (rounding, flush-to-zero, denormals-are-zero, exception traps) | MEASURED on one x86-64 Windows host with clang 22.1.8 only: `check_fpenv.py` 12 of 12 rows, with plants and mutants; GCC, Linux and AArch64 NOT MEASURED until the workflow's `fpenv` jobs run | `kernel/runtime/README.md` |
| What the prototype cannot see | a part of fast-math the compiler does not announce (clang on Linux announces `-fassociative-math`, `-freciprocal-math` and `-fno-signed-zeros` by no macro; ARGUED from the macros measured on Windows); contraction or any optimisation in another translation unit; a state changed after the check; any processor other than x86-64 and AArch64 beyond what the probes show | `kernel/runtime/mk_fpenv.h` |
| A runtime check can undo a compiler's fast-math optimisation already compiled into a program | false in general: a check reads the processor's state, not the code; the library must be built as its own artifact with strict flags | — |

## 4. Portability evidence: where it was measured

| Evidence | Grade | Where |
|---|---|---|
| The 13 gates and both harnesses held | MEASURED on one x86-64 Windows host, inside Linux containers (Debian, Coq 8.20.1 and Flocq 4.2.1 from Debian packages) | `THEOREMS.md`; the gate consoles |
| The same gates on GitHub-hosted Ubuntu 24.04 with Coq 8.20.1 and Flocq 4.2.1 built from opam | NOT MEASURED: the workflow exists and has not run on GitHub | `.github/workflows/mathkernel-linux.yml`, `docs/engineering/MATHKERNEL-LINUX-CI.md` |
| The floating-point state guard's gate on GitHub-hosted Ubuntu 24.04, x86-64 and arm64, with GCC and clang | NOT MEASURED: the workflow's `fpenv` jobs have not run | `.github/workflows/mathkernel-linux.yml` |
| The turns kernel's exhaustive measurement and the F32 sweeps | MEASURED on the same one host (GCC 14.2.0, clang 22.1.8, rustc 1.96.1) | the paper §5.3; Verðandi's `CLAIMS.md` |
| Any second machine, operating system on hardware, ARM processor, or MSVC | NONE | — |

## 5. Product readiness

| Product | Grade | What it lacks |
|---|---|---|
| A C99, Rust or Python package of the kernel | NONE | G3, G4, a bit-level contract (NaN, flags, signed zero, out-of-domain inputs), multi-host evidence |
| A deterministic game or physics SDK | NONE | the package above, and an end-to-end lockstep simulation measured across hosts |
| A bit-exact fp32 inference runtime | NONE | beyond `exp32`, `rsqrt32` and the turns kernel: deterministic matrix products, reductions, softmax, normalisation and quantisation |
| A service that gates AI-written code with these checks | NONE | sandboxing, supply-chain controls, machine-readable attestations, tests on hostile projects, a pilot |

## Outside reading (G6)

| Event | Grade |
|---|---|
| The 13 statement files read at statement level, outside the authors' model family | see `docs/paper/SYSTEM-GUARANTEES.md` §3 G6 for its current grade |
