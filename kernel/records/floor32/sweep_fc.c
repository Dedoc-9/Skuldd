/* sweep_fc.c (2026-11-18, the assistant): the exhaustive sweep of the Phase 1 pilot. The program that
   FLOOR32_Statement.v and CEIL32_Statement.v write (their shapes T_floor32 and T_ceil32, transcribed step for step
   into C doubles: binary64, round to nearest even, no contraction), run on every one of the 2^32 binary32 bit
   patterns, the result stored to binary32, compared bit for bit with
     (a) the host's floorf / ceilf (the C library's IEEE 754 round-to-integral), and
     (b) an integer reference that uses no floating-point operation but the exact conversion of a whole number
         below 2^24 to float.
   A NaN result is compared as NaN-ness only (payloads are not stated). Also counted: -0 results.
   PLANT=1 removes the zero step (y in place of x * 0 when |y| <= 0); its expected mismatches are fixed below, so a
   plant run that does not show them fails the verdict: it proves the run executed the program it names.
   Build: clang -O2 -ffp-contract=off sweep_fc.c (and -DPLANT=1). Last line: SWEEP HELD / SWEEP FAILED.
   What it does not show: that this C is the Coq shape (ARGUED by transcription); any other compiler, flags or host. */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifndef PLANT
#define PLANT 0
#endif

static float bf(uint32_t u) { float f; memcpy(&f, &u, 4); return f; }
static uint32_t fb(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }

static const double CN = 6755399441055744.0, BIG = 8388608.0;   /* 1.5 * 2^52, 2^23 */

/* The shape: if 2^23 <= |x| then x; n = (x + CN) - CN; floor: y = n - 1 if x < n else n; ceil: y = n + 1 if n < x
   else n; the result is x * 0 if |y| <= 0, otherwise y. */
static float shape(float f, int up) {
  double x = (double)f;
  if (BIG <= fabs(x)) return (float)x;
  double n = (x + CN) - CN;
  double y = up ? ((n < x) ? n + 1.0 : n) : ((x < n) ? n - 1.0 : n);
  double r = (!PLANT && fabs(y) <= 0.0) ? x * 0.0 : y;
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
  /* expected counts: the program (PLANT 0) differs nowhere; the plant differs at -0 for floor and on every pattern
     in (-1, -0] for ceil (0x80000000 .. 0xBF7FFFFF). -0 results: floor only at -0; ceil on (-1, -0]. */
  const uint64_t want_diff[2] = { PLANT ? 1u : 0u, PLANT ? 1065353216u : 0u };
  const uint64_t want_negz[2] = { PLANT ? 0u : 1u, PLANT ? 0u : 1065353216u };
  int ok_all = 1;
  for (int up = 0; up < 2; up++) {
    uint64_t lib = 0, ref = 0, nan_dis = 0, n = 0, negz = 0; uint32_t first = 0; int has = 0;
    uint32_t u = 0;
    do {
      float f = bf(u), p = shape(f, up), h = up ? ceilf(f) : floorf(f);
      uint32_t pb = fb(p), hb = fb(h), rb = iref(u, up);
      int pn = isnan(p), hn = isnan(h), rn = isnan(bf(rb));
      if (pn || hn || rn) { if (!(pn && hn && rn)) nan_dis++; }
      else {
        if (pb != hb) { lib++; if (!has) { first = u; has = 1; } }
        if (pb != rb) ref++;
        if (pb == 0x80000000u) negz++;
      }
      n++;
    } while (++u != 0);
    int ok = n == 4294967296ull && lib == want_diff[up] && ref == want_diff[up] && nan_dis == 0 && negz == want_negz[up];
    ok_all &= ok;
    printf("%s plant=%d inputs %llu | differs from host %s: %llu | differs from integer reference: %llu | NaN-ness disagrees: %llu | -0 results: %llu | %s\n",
           up ? "ceil32 " : "floor32", PLANT, (unsigned long long)n, up ? "ceilf " : "floorf",
           (unsigned long long)lib, (unsigned long long)ref, (unsigned long long)nan_dis, (unsigned long long)negz,
           ok ? "as expected" : "NOT AS EXPECTED");
    if (has) printf("  first difference from the host at 0x%08x\n", first);
  }
  printf("%s (plant=%d)\n", ok_all ? "SWEEP HELD" : "SWEEP FAILED", PLANT);
  return ok_all ? 0 : 1;
}
