<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# kernel/runtime: the floating-point state guard (a prototype for G4)

The kernel's statements are about binary64 operations rounded to nearest, ties to even, with subnormals kept and no
fused multiply-add. A program can run in another state (a library that switched on flush-to-zero, a thread whose
rounding mode was changed) or be compiled into other operations (fast-math, contraction, x87's excess precision).
`mk_fpenv` checks what can be checked of that, and says what it cannot.

| File | What it is |
|---|---|
| `mk_fpenv.h` | the compile-time layer: `#error` on fast-math and its announced parts, finite-math, `__GCC_IEC_559 == 0` and `FLT_EVAL_METHOD != 0`; the interface |
| `mk_fpenv.c` | the run-time layer: `mk_fpenv_check()` returns 0 or one bit per problem (rounding, flush-to-zero, denormals-are-zero, contraction, traps) from probes with volatile operands and, on x86-64 and AArch64, the MXCSR or FPCR register |
| `test_fpenv.c` | the self-test: the admitted state reads 0; each plant (three rounding modes, MXCSR FZ, DAZ and an unmasked exception, or FPCR FZ and a trap) is reported as exactly its own problem |
| `check_fpenv.py` | the gate: the self-test with each compiler at `-O0` and `-O2`, with the register reads and with the probes alone; compile-time plants; a contraction plant; mutants that disable one check each and must make the self-test fail |

Run it from the repository's root:

    python3 -B kernel/runtime/check_fpenv.py              # every compiler of clang, gcc, cc on the PATH
    python3 -B kernel/runtime/check_fpenv.py --cc gcc     # one compiler

The last line is `FPENV CHECK HELD: n of n rows` or `FPENV CHECK FAILED: k of n rows`; a skipped row (an x87 plant the
compiler cannot target, a mutant with no plant on this processor) is named on that line and never counted as a pass.

Build the library's computing code and `mk_fpenv.c` with the same strict flags, for example
`-std=c99 -ffp-contract=off -fno-fast-math`, and without `#pragma STDC FENV_ACCESS ON` or `-frounding-math` in
`mk_fpenv.c`: clang does not fuse under either, so either would hide the contraction the canary is there to see.

## What it shows, and what it does not

Measured: on one x86-64 Windows host, clang 22.1.8, `FPENV CHECK HELD: 12 of 12 rows` (two equivalent mutants skipped
and named). GCC, Linux and AArch64 are run by the workflow's `fpenv` jobs, which have not run yet.

It does not show that the kernel's operations are deterministic, or anything on a compiler, flag set or processor it
did not run on. It cannot see a part of fast-math the compiler does not announce by a macro, contraction or any
optimisation in a translation unit other than `mk_fpenv.c`, or a state changed after the check: the registers are per
thread, so a library calls it on each thread at each entry that matters. No kernel library calls it yet; there is no
such library (G3).
