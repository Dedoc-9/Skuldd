/* sweep_fc2.c (Push A's fclink folder, 2026-11-21, written by the assistant from the research prototype clink;
   after review 1 (M4) the binary64 result is compared too). Frozen by sha256 with FCLINK_Statement.v, CPrint.v,
   KernelText.v and gen_kernel_text.py before any proof, and listed on both freeze lists (FROZEN.txt,
   FROZEN4.txt), since gate4 itself requires only the generator.
   The exhaustive sweep of floor32 and ceil32 whose
   kernels are not typed by hand. The two lines between the COQ TEXT markers below are the text that FC_TEXT
   (FCLINK_Statement.v) states to be CPrint.v's printed text of the frozen shapes T_floor32 and T_ceil32. That
   equality is NOT proved until Link.v is compiled: these bytes were printed by the prototype's Python stand-in for
   the printer and are copied here byte for byte. gen_kernel_text.py quotes exactly these two lines into KernelText.v
   and reads nothing else of this file, so nothing between the markers is ever edited by hand. Each line is one C
   function of a binary64 x, fully parenthesised, every shared subexpression written out again (the printed text has
   no sharing; the compiler may share). On every one of the 2^32 binary32 patterns
     the binary64 result is compared bit for bit with the integer reference iref (b below) widened to binary64, and
     the result, stored to binary32, is compared bit for bit with
     (a) the host's floorf / ceilf, (b) the frozen sweep's integer reference iref, copied byte for byte, and
     (c) the frozen sweep's hand transcription shape(), copied byte for byte and renamed hand_shape.
   A NaN result is compared as NaN-ness only. Also counted: -0 results. The expected counts are given at build time
   (-DWANT_F=.. -DWANT_C=.. -DNEGZ_F=.. -DNEGZ_C=..), fixed by the runner before the run; the binary64 comparison
   must give the same count of differences as the others.
   Build: clang -O2 -ffp-contract=off sweep_fc2.c. Last line: SWEEP2 HELD / SWEEP2 FAILED.
   What it does not show: that the text between the markers is the print of the Coq shapes (FC_TEXT, once proved);
   what that text means in C (DECLARED, TRUSTED.md); other compilers, flags or hosts; another call site of the two
   functions (they are static, and the compiler may inline them into this loop). The frozen sweep_fc.c and its
   records stay as they are. */
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#if !defined(FLT_EVAL_METHOD) || FLT_EVAL_METHOD != 0
#error "binary64 expressions must be evaluated in binary64 (FLT_EVAL_METHOD 0)"
#endif
#ifndef WANT_F
#error "give the expected counts"
#endif

static float bf(uint32_t u) { float f; memcpy(&f, &u, 4); return f; }
static uint32_t fb(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }

/* BEGIN COQ TEXT */
static double mk_floor32(double x) { return (0x10000000000000p-29 <= fabs(x) ? x : (fabs((x < ((x + 0x18000000000000p0) - 0x18000000000000p0) ? (((x + 0x18000000000000p0) - 0x18000000000000p0) - 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0))) <= 0.0 ? (x * 0.0) : (x < ((x + 0x18000000000000p0) - 0x18000000000000p0) ? (((x + 0x18000000000000p0) - 0x18000000000000p0) - 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0)))); }
static double mk_ceil32(double x) { return (0x10000000000000p-29 <= fabs(x) ? x : (fabs((((x + 0x18000000000000p0) - 0x18000000000000p0) < x ? (((x + 0x18000000000000p0) - 0x18000000000000p0) + 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0))) <= 0.0 ? (x * 0.0) : (((x + 0x18000000000000p0) - 0x18000000000000p0) < x ? (((x + 0x18000000000000p0) - 0x18000000000000p0) + 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0)))); }
/* END COQ TEXT */

/* From the frozen sweep_fc.c (sha256 c0b4b710...dc92), byte for byte but for the two renamings below. */
#define HAND_PLANT 0
static const double CN = 6755399441055744.0, BIG = 8388608.0;   /* 1.5 * 2^52, 2^23 */

static float hand_shape(float f, int up) {
  double x = (double)f;
  if (BIG <= fabs(x)) return (float)x;
  double n = (x + CN) - CN;
  double y = up ? ((n < x) ? n + 1.0 : n) : ((x < n) ? n - 1.0 : n);
  double r = (!HAND_PLANT && fabs(y) <= 0.0) ? x * 0.0 : y;
  return (float)r;
}

static uint32_t iref(uint32_t u, int up) {
  uint32_t s = u >> 31, E = (u >> 23) & 0xFF, M = u & 0x7FFFFF;
  if (E == 0xFF) return u;                       /* infinity or NaN */
  if (E >= 150) return u;                        /* |x| >= 2^23: whole */
  if (E == 0 && M == 0) return u;                /* +0 or -0 */
  uint64_t m = (E == 0) ? M : (M | 0x800000u);   /* value = m * 2^(E' - 150), E' = max(E, 1) */
  int k = 150 - (E == 0 ? 1 : (int)E);           /* fractional bits, 1 .. 149 */
  uint64_t q = (k >= 64) ? 0 : (m >> k);
  int frac = (k >= 64) ? (m != 0) : ((m & ((1ull << k) - 1)) != 0);
  int away = frac && (up ? !s : s);              /* away from zero by one when the direction points away */
  uint64_t mag = q + (uint64_t)away;
  if (mag == 0) return s << 31;                  /* a zero result has the sign of x */
  return fb((float)mag) | (s << 31);             /* exact: mag <= 2^23 */
}

int main(void) {
  const uint64_t want[2] = { WANT_F, WANT_C }, negz_want[2] = { NEGZ_F, NEGZ_C };
  int ok_all = 1;
  for (int up = 0; up < 2; up++) {
    uint64_t lib = 0, ref = 0, hand = 0, nan_dis = 0, n = 0, negz = 0, dref = 0; uint32_t first = 0; int has = 0;
    uint32_t u = 0;
    do {
      float f = bf(u);
      double x = (double)f;
      double d = up ? mk_ceil32(x) : mk_floor32(x); float p = (float)d;
      float h = up ? ceilf(f) : floorf(f), s = hand_shape(f, up);
      uint32_t pb = fb(p), hb = fb(h), rb = iref(u, up), sb = fb(s);
      double dr = (double)bf(rb); uint64_t db, drb; memcpy(&db, &d, 8); memcpy(&drb, &dr, 8);
      int pn = isnan(p), hn = isnan(h), rn = isnan(bf(rb)), sn = isnan(s);
      if (pn || hn || rn || sn) { if (!(pn && hn && rn && sn)) nan_dis++; }
      else {
        if (pb != hb) { lib++; if (!has) { first = u; has = 1; } }
        if (pb != rb) ref++;
        if (db != drb) dref++;
        if (pb != sb) hand++;
        if (pb == 0x80000000u) negz++;
      }
      n++;
    } while (++u != 0);
    int ok = n == 4294967296ull && lib == want[up] && ref == want[up] && dref == want[up] && hand == want[up] && nan_dis == 0 && negz == negz_want[up];
    ok_all &= ok;
    printf("%s inputs %llu | differs from host %s: %llu | from integer reference: %llu | binary64 result differs from the integer reference: %llu | from hand transcription: %llu | NaN-ness disagrees: %llu | -0 results: %llu | %s\n",
           up ? "ceil32 " : "floor32", (unsigned long long)n, up ? "ceilf " : "floorf", (unsigned long long)lib,
           (unsigned long long)ref, (unsigned long long)dref, (unsigned long long)hand, (unsigned long long)nan_dis,
           (unsigned long long)negz, ok ? "as expected" : "NOT AS EXPECTED");
    if (has) printf("  first difference from the host at 0x%08x\n", first);
  }
  printf("%s\n", ok_all ? "SWEEP2 HELD" : "SWEEP2 FAILED");
  return ok_all ? 0 : 1;
}
