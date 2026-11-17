/* SPDX-License-Identifier: AGPL-3.0-only */
/* test_fpenv.c: mk_fpenv's self-test. The admitted state must read 0; each plant switches one mode on through the
 * C library or the processor's own register, must be reported as exactly that problem, and is then put back. The
 * exception is AArch64's FPCR.FZ, which flushes inputs as well as results: its row requires flush-to-zero and allows
 * denormals-are-zero beside it.
 *   clang -std=c99 -O2 -ffp-contract=off -fno-fast-math mk_fpenv.c test_fpenv.c -o test_fpenv -lm
 * (-lm on glibc systems, where fegetround and fesetround are in libm; not on Windows.)
 * Built with -DMK_FPENV_PROBES_ONLY, the check reads neither fegetround nor a register: the rows then test the probes.
 * Last line: "FPENV SELFTEST n/n" (exit 0) or "FPENV SELFTEST k/n" (exit 1).
 */
#include "mk_fpenv.h"

#include <fenv.h>
#include <stdio.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <xmmintrin.h>
#define MK_MXCSR 1
#endif

#if defined(__clang__)
#pragma STDC FENV_ACCESS ON
#endif

static int rows, passed;

static void row(int ok, const char *name, unsigned got)
{
    char buf[96];
    rows++;
    passed += ok != 0;
    printf("[%s] %s -- reported: %s\n", ok ? "PASS" : "FAIL", name, mk_fpenv_describe(got, buf, sizeof buf));
}

static void rounding_plant(int mode, const char *name)
{
    unsigned got;
    if (fesetround(mode) != 0) {
        rows++;
        printf("[FAIL] %s -- fesetround refused the mode\n", name);
        return;
    }
    got = mk_fpenv_check();
    fesetround(FE_TONEAREST);
    row(got == MK_FPENV_ROUNDING, name, got); /* that problem and no other */
}

int main(void)
{
    char buf[96];
    unsigned got = mk_fpenv_check();
    row(got == 0, "the admitted state reads as admitted", got);
#ifdef FE_UPWARD
    rounding_plant(FE_UPWARD, "plant: rounding upward is reported");
#endif
#ifdef FE_DOWNWARD
    rounding_plant(FE_DOWNWARD, "plant: rounding downward is reported");
#endif
#ifdef FE_TOWARDZERO
    rounding_plant(FE_TOWARDZERO, "plant: rounding toward zero is reported");
#endif
#if defined(MK_MXCSR)
    {
        unsigned saved = _mm_getcsr();
        _mm_setcsr(saved | 0x8000u);
        got = mk_fpenv_check();
        _mm_setcsr(saved);
        row(got == MK_FPENV_FTZ, "plant: MXCSR flush-to-zero is reported, and only it", got);
        _mm_setcsr(saved | 0x0040u);
        got = mk_fpenv_check();
        _mm_setcsr(saved);
        row(got == MK_FPENV_DAZ, "plant: MXCSR denormals-are-zero is reported, and only it", got);
#if !defined(MK_FPENV_PROBES_ONLY)
        _mm_setcsr(saved & ~0x0200u); /* unmask divide-by-zero: the check divides nothing, so nothing traps */
        got = mk_fpenv_check();
        _mm_setcsr(saved);
        row(got == MK_FPENV_TRAPS, "plant: an unmasked MXCSR exception is reported, and only it", got);
#endif
    }
#elif defined(__aarch64__) && (defined(__GNUC__) || defined(__clang__))
    {
        unsigned long fpcr, saved, back;
        __asm__ volatile("mrs %0, fpcr" : "=r"(saved));
        fpcr = saved | (1ul << 24);
        __asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
        got = mk_fpenv_check();
        __asm__ volatile("msr fpcr, %0" : : "r"(saved));
        row((got & MK_FPENV_FTZ) != 0, "plant: FPCR flush-to-zero is reported (FZ also reads inputs as zero)", got);
#if !defined(MK_FPENV_PROBES_ONLY)
        fpcr = saved | (1ul << 9); /* DZE: many processors do not keep it (trapping not implemented) */
        __asm__ volatile("msr fpcr, %0" : : "r"(fpcr));
        __asm__ volatile("mrs %0, fpcr" : "=r"(back));
        got = mk_fpenv_check();
        __asm__ volatile("msr fpcr, %0" : : "r"(saved));
        if (back & (1ul << 9))
            row(got == MK_FPENV_TRAPS, "plant: an enabled FPCR trap is reported, and only it", got);
        else
            printf("[SKIP] plant: an enabled FPCR trap -- this processor does not keep DZE\n");
#endif
    }
#endif
    got = mk_fpenv_check();
    row(got == 0, "the admitted state reads as admitted again after the plants", got);
    printf("problems this build can report: %s\n", mk_fpenv_describe(MK_FPENV_ALL, buf, sizeof buf));
    printf("FPENV SELFTEST %d/%d\n", passed, rows);
    return passed == rows ? 0 : 1;
}
