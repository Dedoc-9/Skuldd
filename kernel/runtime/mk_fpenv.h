/* SPDX-License-Identifier: AGPL-3.0-only */
/* mk_fpenv.h: the floating-point state the kernel's operations assume, checked (G4; docs/GUARANTEES-LEDGER.md §3).
 * A prototype: no kernel library calls it yet.
 *
 * The statements are about binary64 operations rounded to nearest, ties to even, with subnormals kept (no
 * flush-to-zero, no denormals-are-zero), no contraction into fused multiply-adds and no excess precision. Three
 * layers check that, each covering what the others cannot:
 *
 *   1. compile time, in every translation unit that includes this header: refuse what the compiler announces --
 *      fast-math and its relatives (the macros below) and excess precision (FLT_EVAL_METHOD other than 0, as x87
 *      has; 16, which promotes only _Float16, is allowed). A compiler does not announce every flag. Clang (22.1.8,
 *      measured by preprocessing for each target) announces -freciprocal-math, -fno-signed-zeros and the like only on
 *      MSVC-environment targets (_M_FP_FAST), -fassociative-math alone nowhere, and contraction only there
 *      (_M_FP_CONTRACT, not refused here); GCC (read in its source) announces contraction in ISO C by setting
 *      __GCC_IEC_559 to 0, and not in its GNU dialects. So the code that computes must itself be built with strict
 *      flags, as its own artifact: C99, -ffp-contract=off, no -ffast-math or any of its parts.
 *
 *   2. run time, known answers computed in mk_fpenv.c's own translation unit from volatile operands: a contraction
 *      canary (it shows that unit, built with the library's flags, does not fuse; nothing about any other unit),
 *      rounding and ties-to-even probes, flush-to-zero and denormals-are-zero probes that compare bit patterns.
 *
 *   3. run time, the processor's own register where it can be read: x86-64 MXCSR (rounding, FZ, DAZ, exception
 *      masks), AArch64 FPCR (rounding, FZ, FIZ, trap enables; FZ there flushes inputs too, so it may also read as
 *      denormals-are-zero). fegetround is also read; on x86-64 glibc it reads the x87 control word, which is why
 *      MXCSR is read directly.
 *
 * mk_fpenv_check() returns 0 when the state is the admitted one, else one bit per problem.
 * What it does not do: guarantee determinism; detect contraction or any other optimisation compiled into code
 * outside mk_fpenv.c; check a state that changes after the check (the registers are per thread: call it on each
 * thread, at each entry that matters); read a register on a processor other than x86-64 and AArch64; read AArch64's
 * FPCR.AH or FPCR.DN (any flushing they cause is seen by the probes; NaN payloads are not part of the contract).
 */
#ifndef MK_FPENV_H
#define MK_FPENV_H

#include <float.h>
#include <stddef.h>

#if defined(__FAST_MATH__)
#error "mk_fpenv: compiled with fast-math (-ffast-math, -Ofast): the operations are not the modelled ones"
#endif
#if defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__
#error "mk_fpenv: compiled assuming finite math only (-ffinite-math-only)"
#endif
#if defined(__ASSOCIATIVE_MATH__) || defined(__RECIPROCAL_MATH__) || defined(__NO_SIGNED_ZEROS__)
#error "mk_fpenv: compiled with a part of fast-math (-fassociative-math, -freciprocal-math or -fno-signed-zeros)"
#endif
#if defined(__GCC_IEC_559) && __GCC_IEC_559 == 0
#error "mk_fpenv: the compiler says this build does not follow IEC 60559 (__GCC_IEC_559 is 0)"
#endif
#if defined(_M_FP_FAST)
#error "mk_fpenv: compiled with /fp:fast or a part of fast-math"
#endif
#if !defined(FLT_EVAL_METHOD)
#error "mk_fpenv: FLT_EVAL_METHOD is not defined: the compiler does not say how it evaluates floating expressions"
#elif FLT_EVAL_METHOD != 0 && FLT_EVAL_METHOD != 16
#error "mk_fpenv: excess precision (FLT_EVAL_METHOD is not 0, as with x87): build for SSE2 or another strict target"
#endif

#define MK_FPENV_ROUNDING 0x01u /* not round to nearest, ties to even */
#define MK_FPENV_FTZ      0x02u /* a subnormal result is flushed to zero */
#define MK_FPENV_DAZ      0x04u /* a subnormal input is read as zero */
#define MK_FPENV_CONTRACT 0x08u /* mk_fpenv.c was built with a multiply and an add fused */
#define MK_FPENV_TRAPS    0x10u /* a floating-point exception is unmasked (it would trap) */
#define MK_FPENV_ALL      0x1Fu

/* 0 when the floating-point state is the admitted one; else the problems, one bit each. */
unsigned mk_fpenv_check(void);

/* Writes the problems' names, comma-separated ("ok" for 0), into buf; returns buf. */
char *mk_fpenv_describe(unsigned problems, char *buf, size_t size);

#endif
