/* SPDX-License-Identifier: AGPL-3.0-only */
/* mk_fpenv.c: the run-time half of mk_fpenv.h. Build it with the same flags as the library's computing code, e.g.
 *   clang -std=c99 -O2 -ffp-contract=off -fno-fast-math -c mk_fpenv.c
 * Every probe reads its operands through volatile objects, so the compiler cannot fold it at build time; that is why
 * this unit needs neither #pragma STDC FENV_ACCESS nor -frounding-math. It must have neither, nor an FP_CONTRACT
 * pragma: the contraction canary has to see what the library's flags do, and clang (22.1.8, measured) does not fuse
 * under FENV_ACCESS ON or -frounding-math, so either would hide a contraction the library's own units would have.
 */
#include "mk_fpenv.h"

#include <fenv.h>
#include <stdint.h>
#include <string.h>

#if defined(__x86_64__) || defined(_M_X64)
#include <xmmintrin.h>
#define MK_MXCSR 1
#endif

static volatile double one = 1.0, half = 0.5, big = 0x1p60;
static volatile double tiny_up = 0x1p-60;            /* far below half an ulp of 1 */
static volatile double above_half = 0x1.000002p-53;  /* just above half an ulp of 1 */
static volatile double half_ulp = 0x1p-53;           /* exactly half an ulp of 1: a tie */
static volatile double one_odd = 0x1.0000000000001p0; /* 1 + 2^-52: odd last digit */
static volatile double min_normal = 0x1p-1022;
static volatile double min_sub = 0x1p-1074;
static volatile double fx = 0x1.0000002p0, fy = 0x1.ffffffcp-1; /* (1 + 2^-27)(1 - 2^-27) = 1 - 2^-54 */
static volatile float min_normal_f = 0x1p-126f, min_sub_f = 0x1p-149f, half_f = 0.5f, big_f = 0x1p30f;

/* The subnormal probes compare bit patterns, never values: a comparison reads its operands, and under
 * denormals-are-zero a subnormal compares equal to zero. */
static uint64_t bits64(double x) { uint64_t u; memcpy(&u, &x, sizeof u); return u; }
static uint32_t bits32(float x) { uint32_t u; memcpy(&u, &x, sizeof u); return u; }

static unsigned probes(void)
{
    unsigned p = 0;
    double up = one + tiny_up;          /* to nearest and toward zero or down: 1; upward: 1 + 2^-52 */
    double down = -one - tiny_up;       /* to nearest and toward zero or up: -1; downward: -(1 + 2^-52) */
    double near = one + above_half;     /* to nearest and upward: 1 + 2^-52; toward zero and down: 1 */
    double tie_even = one + half_ulp;   /* a tie: to even gives 1; away from zero gives 1 + 2^-52 */
    double tie_odd = one_odd + half_ulp; /* a tie: to even gives 1 + 2^-51; toward zero gives 1 + 2^-52 */
    double fused = fx * fy - one;       /* separate: +0 (to nearest: 1 - 2^-54 is a tie, to 1) or -2^-53 (down);
                                           fused: exactly -2^-54 in every rounding mode */
    if (up != 1.0 || down != -1.0 || near != 1.0 + 0x1p-52 || tie_even != 1.0 || tie_odd != 1.0 + 0x1p-51)
        p |= MK_FPENV_ROUNDING;
    /* flush-to-zero: normal inputs, a subnormal result (2^-1023, 2^-127) that must be kept */
    if (bits64(min_normal * half) != UINT64_C(0x0008000000000000) || bits32(min_normal_f * half_f) != UINT32_C(0x00400000))
        p |= MK_FPENV_FTZ;
    /* denormals-are-zero: a subnormal input, a normal result (2^-1014, 2^-119) that flushing cannot touch */
    if (bits64(min_sub * big) != UINT64_C(0x0090000000000000) || bits32(min_sub_f * big_f) != UINT32_C(0x04000000))
        p |= MK_FPENV_DAZ;
    if (bits64(fused) == UINT64_C(0xBC90000000000000)) /* -2^-54 */
        p |= MK_FPENV_CONTRACT;
    return p;
}

unsigned mk_fpenv_check(void)
{
    unsigned p = probes();
#if !defined(MK_FPENV_PROBES_ONLY) /* the self-test builds once without the reads below, to test the probes alone */
    if (fegetround() != FE_TONEAREST)
        p |= MK_FPENV_ROUNDING;
#endif
#if defined(MK_FPENV_PROBES_ONLY)
#elif defined(MK_MXCSR)
    {
        unsigned csr = _mm_getcsr();
        if (csr & 0x6000u) p |= MK_FPENV_ROUNDING;               /* RC, bits 13-14: 00 is to nearest */
        if (csr & 0x8000u) p |= MK_FPENV_FTZ;                    /* FZ, bit 15 */
        if (csr & 0x0040u) p |= MK_FPENV_DAZ;                    /* DAZ, bit 6 */
        if ((csr & 0x1F80u) != 0x1F80u) p |= MK_FPENV_TRAPS;     /* the six exception masks, bits 7-12 */
    }
#elif defined(__aarch64__) && (defined(__GNUC__) || defined(__clang__))
    {
        unsigned long fpcr;
        __asm__ volatile("mrs %0, fpcr" : "=r"(fpcr));
        if (fpcr & (3ul << 22)) p |= MK_FPENV_ROUNDING;          /* RMode, bits 22-23: 00 is to nearest */
        if (fpcr & (1ul << 24)) p |= MK_FPENV_FTZ;               /* FZ, bit 24 */
        if (fpcr & 0x9F00ul) p |= MK_FPENV_TRAPS;                /* IOE DZE OFE UFE IXE, bits 8-12; IDE, bit 15 */
    }
#endif
    return p;
}

static size_t put(char *buf, size_t size, size_t used, const char *s)
{
    while (*s && used + 1 < size)
        buf[used++] = *s++;
    buf[used] = '\0';
    return used;
}

char *mk_fpenv_describe(unsigned problems, char *buf, size_t size)
{
    static const char *names[] = {"rounding", "flush-to-zero", "denormals-are-zero", "contraction", "traps"};
    size_t i, used = 0;
    if (size == 0)
        return buf;
    buf[0] = '\0';
    if ((problems & MK_FPENV_ALL) == 0)
        return (put(buf, size, 0, "ok"), buf);
    for (i = 0; i < sizeof names / sizeof names[0]; i++) {
        if (problems & (1u << i)) {
            if (used)
                used = put(buf, size, used, ", ");
            used = put(buf, size, used, names[i]);
        }
    }
    return buf;
}
