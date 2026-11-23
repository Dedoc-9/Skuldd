/* bits32_sweep.c: the record sweep of all 32 output bits of floor32 and ceil32 on all 2^32 binary32 patterns, ruling
   A4 (a) for Skuldd's Push A. Written 2026-11-22 by a stage agent of the assistant from the design SWEEP-SPEC.md
   (draft 4) and its plants, PLANTS.md (draft 4, part 1). Frozen by sha256 in BITS32-SWEEP-FROZEN.txt beside it after
   a syntax-only compile and before its first run; built and run only by run_bits32_sweep.sh.

   THE PROGRAM UNDER TEST. The C text that FCLINK states (fclink/FCLINK_Statement.v, FC_TEXT): the two lines between
   the COQ TEXT markers of fclink/sweep_fc2.c (frozen; its sha256, the owner's under R1:
   924bd031c84172fd98203f1b755f1f63b8cc62aecd76bd6358273f00fc2a7005),
   which fclink/KernelText.v quotes as floor32_c_text and ceil32_c_text. They are copied below byte for byte
   with their markers (the only lines of this file over 120 characters), and the runner compares them by text with
   that file before any build. Each is a C function of a binary64 argument with a binary64 result. It is called here
   as sweep_fc2.c calls it (its lines 80-82 and 84): the pattern u is copied into a float by memcpy (bf), widened by
   the C conversion (double)f, the function applied, the result narrowed by the C conversion (float)d, and its bits
   copied out by memcpy (fb). The NaN bits measured are those of this path, as this compiler builds it for this
   target: the two C conversions, the arithmetic between them and the copies. A caller that widens or narrows on
   integer bits instead runs other code on a NaN, which this sweep does not measure.

   THE SPECIFICATION. spec32 below is SPEC32 of bits32/BITS32_Statement.v (frozen; its sha256, the owner's under R1:
   c3e65cb7285ddf438145e6fc7284e7749013472b3d4b06f8fc211d345b043e53),
   transcribed line by line in C unsigned 32-bit integers: split32
   and join32 (its lines 87-88: Flocq's Bits.split_bits and Bits.join_bits at 23 and 8, Flocq 4.2.1 Bits.v:77-80 and
   :37-38), enc_int32 (its lines 96-97) and SPEC32 (its lines 99-110). TRANSCRIPTION.md sets each Coq line beside its
   C line. That spec32 is SPEC32 is ARGUED there (no value leaves [0, 2^32); every shift is below 32), not proved.

   THE ROWS, all fixed in want[] and want_class[] below before the first run. For u from 0 to 2^32 - 1, floor32 and
   ceil32: the 32 bits of the program's binary32 result against spec32, counted per input class read from u's integer
   bits (finite, infinity, quiet NaN, signalling NaN); the class counts; spec32 against spec() of the research sweep
   nanbits.c (2026-11-21, its lines 63-77, copied byte for byte) on every pattern; spec32 against iref (fclink/
   sweep_fc2.c lines 58-71, copied byte for byte; it encodes with an integer-to-float conversion) on every pattern that
   is not a NaN; and an environment row: MXCSR at start, rounding to nearest with DAZ and FTZ clear. OBSERVED, outside
   every verdict: the host floorf / ceilf against spec32 per class, and a table of chosen NaN inputs.

   PLANT (one build each; PLANTS.md part 1 and SWEEP-SPEC section 5): 0 none. 1 PL1: on a NaN input pattern the
   output bits are u (the quiet bit dropped). 2 PL2: on a NaN input, u's sign bit with 0x7FC00000 (one default NaN per
   sign). 3 PL3: on a NaN input, bit 31 of the output flipped. 4 PL4: on a NaN input, the hardware's default NaN, a
   volatile 0 times infinity narrowed to binary32, in place of the call. 5 PL5: the zero step removed. This text has
   no PLANT switch inside it, so the runner builds PLANT 5 from a copy of this file in which each of the two COQ TEXT
   lines has "<" where it has "<=" before its zero test; no value is below 0.0, so the selection returns its Y, as
   the record sweep's own plant does. 6 DAZ: denormals-are-zero set in MXCSR at start: the environment row must fail,
   and the comparison counts are those fixed for it below.
   Last line of each build: BITS32 BUILD AS FIXED or BITS32 BUILD NOT AS FIXED (exit 0 or 1); the runner's last line
   is the verdict.

   WHAT IT DOES NOT SHOW. That the text between the markers is Coq's print of the shapes (FCLINK's FC_TEXT, a proof
   about its Coq model); that spec32 is SPEC32 (ARGUED, corroborated); anything for another compiler, flag set,
   processor, host, MXCSR state or binary; exception flags; NaN bits of a path that converts on integer bits. */
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <xmmintrin.h>
#if !(defined(__x86_64__) || defined(_M_X64))
#error "x86-64 only: the environment row reads MXCSR"
#endif
#if !defined(FLT_EVAL_METHOD) || FLT_EVAL_METHOD != 0
#error "binary64 expressions must be evaluated in binary64 (FLT_EVAL_METHOD 0)"
#endif
#ifndef PLANT
#define PLANT 0
#endif
#if PLANT < 0 || PLANT > 6
#error "PLANT is 0 to 6"
#endif

/* ---- verbatim: fclink/sweep_fc2.c lines 37-38 ---- */
static float bf(uint32_t u) { float f; memcpy(&f, &u, 4); return f; }
static uint32_t fb(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }
/* ---- end verbatim ---- */

/* ---- verbatim: fclink/sweep_fc2.c lines 40-43 ---- */
/* BEGIN COQ TEXT */
static double mk_floor32(double x) { return (0x10000000000000p-29 <= fabs(x) ? x : (fabs((x < ((x + 0x18000000000000p0) - 0x18000000000000p0) ? (((x + 0x18000000000000p0) - 0x18000000000000p0) - 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0))) <= 0.0 ? (x * 0.0) : (x < ((x + 0x18000000000000p0) - 0x18000000000000p0) ? (((x + 0x18000000000000p0) - 0x18000000000000p0) - 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0)))); }
static double mk_ceil32(double x) { return (0x10000000000000p-29 <= fabs(x) ? x : (fabs((((x + 0x18000000000000p0) - 0x18000000000000p0) < x ? (((x + 0x18000000000000p0) - 0x18000000000000p0) + 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0))) <= 0.0 ? (x * 0.0) : (((x + 0x18000000000000p0) - 0x18000000000000p0) < x ? (((x + 0x18000000000000p0) - 0x18000000000000p0) + 0x10000000000000p-52) : ((x + 0x18000000000000p0) - 0x18000000000000p0)))); }
/* END COQ TEXT */
/* ---- end verbatim ---- */

/* ---- verbatim: fclink/sweep_fc2.c lines 58-71 ---- */
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
/* ---- end verbatim ---- */

/* ---- verbatim: nanbits.c lines 63-77 ---- */
static uint32_t spec(uint32_t u, int up) {
  uint32_t s = u >> 31, E = (u >> 23) & 0xFFu, M = u & 0x7FFFFFu;
  if (E == 0xFFu) return (M == 0) ? u : (u | 0x400000u);   /* infinity unchanged; NaN: quiet bit set */
  if (E >= 150u) return u;                                  /* |x| >= 2^23: whole, unchanged */
  if (E == 0u && M == 0u) return u;                         /* +0, -0 unchanged */
  uint32_t m = (E == 0u) ? M : (M | 0x800000u);             /* |x| = m * 2^-k */
  uint32_t k = 150u - (E == 0u ? 1u : E);                   /* 1 .. 149 */
  uint32_t q = (k >= 24u) ? 0u : (m >> k);                  /* m < 2^24 */
  uint32_t frac = (k >= 24u) ? 1u : ((m & ((1u << k) - 1u)) != 0u);  /* m != 0 here */
  uint32_t away = frac & (up ? (s ^ 1u) : s);
  uint32_t mag = q + away;                                  /* 0 .. 2^23 */
  if (mag == 0u) return s << 31;
  uint32_t e = 0; while ((mag >> (e + 1u)) != 0u) e++;      /* e = floor(log2 mag), 0 .. 23 */
  return (s << 31) | ((e + 127u) << 23) | ((mag << (23u - e)) & 0x7FFFFFu);
}
/* ---- end verbatim ---- */

/* SPEC32 of bits32/BITS32_Statement.v (sha256 c3e65cb7...3e53), line by line; ":n" is the statement's line n. P(n)
   is 2 ^ n, used only for n below 32. Z.div and Z.modulo by a power of two are / and %, exact on unsigned values. */
#define P(n) (1u << (n))
/* :88 join32 s m e = Bits.join_bits 23 8 s m e = Z.shiftl ((if s then 2 ^ 8 else 0) + e) 23 + m (Bits.v:37-38) */
static uint32_t join32(uint32_t s, uint32_t m, uint32_t e) { return ((s ? P(8) : 0u) + e) * P(23) + m; }
/* :87 split32 u = Bits.split_bits 23 8 u = (2 ^ 23 * 2 ^ 8 <=? u, u mod 2 ^ 23, (u / 2 ^ 23) mod 2 ^ 8)
   (Bits.v:77-80) */
static void split32(uint32_t u, uint32_t *s, uint32_t *mf, uint32_t *ef) {
  *s = (P(23) * P(8) <= u); *mf = u % P(23); *ef = (u / P(23)) % P(8);
}
/* Z.log2 z for z in 1 .. 2 ^ 23: the largest l with 2 ^ l <= z */
static uint32_t zlog2(uint32_t z) { uint32_t l = 0u; while ((z >> (l + 1u)) != 0u) l++; return l; }
/* :96-97 enc_int32 s mg = join32 s (mg * 2 ^ (23 - Z.log2 mg) - 2 ^ 23) (Z.log2 mg + 127) */
static uint32_t enc_int32(uint32_t s, uint32_t mg) {
  return join32(s, mg * P(23u - zlog2(mg)) - P(23), zlog2(mg) + 127u);
}
/* :99 SPEC32 up u; up = 0 is floor (false), up = 1 ceiling (true) */
static uint32_t spec32(int up, uint32_t u) {
  uint32_t s, mf, ef;
  split32(u, &s, &mf, &ef);                                              /* :100 */
  if (ef == 255u) return (mf == 0u) ? u : (u | P(22));                   /* :101 */
  else if (150u <= ef) return u;                                         /* :102 */
  else if (ef == 0u && mf == 0u) return u;                               /* :103 */
  else {
    uint32_t m = (ef == 0u) ? mf : mf + P(23);                           /* :105 */
    uint32_t k = 150u - (ef > 1u ? ef : 1u);                             /* :106 */
    uint32_t q = (k >= 24u) ? 0u : m / P(k);                             /* :107 (m < 2 ^ 24) */
    uint32_t r = (k >= 24u) ? m : m % P(k);                              /* :108, m mod 2 ^ k */
    int away = (r != 0u) && (up ? !s : s);                               /* :108 */
    uint32_t mg = q + (away ? 1u : 0u);                                  /* :109 */
    return (mg == 0u) ? join32(s, 0u, 0u) : enc_int32(s, mg);            /* :110 */
  }
}

enum { C_FIN, C_INF, C_QNAN, C_SNAN, NC };
static int cls(uint32_t u) {                     /* the class, from u's integer bits only */
  uint32_t E = (u >> 23) & 0xFFu, M = u & 0x7FFFFFu;
  if (E != 0xFFu) return C_FIN;
  if (M == 0u) return C_INF;
  return (M & 0x400000u) ? C_QNAN : C_SNAN;
}

#if PLANT == 4
static volatile double vzero = 0.0, vinf = INFINITY;   /* PL4 only */
#endif

/* The path under test, as sweep_fc2.c lines 80-82 and 84 write it. PL1 to PL4 act only on a NaN input pattern. */
static uint32_t program(uint32_t u, int up) {
#if PLANT == 4
  if (cls(u) >= C_QNAN) return fb((float)(vzero * vinf));
#endif
  float f = bf(u);
  double x = (double)f;
  double d = up ? mk_ceil32(x) : mk_floor32(x); float p = (float)d;
  uint32_t pb = fb(p);
#if PLANT == 1
  if (cls(u) >= C_QNAN) pb = u;
#elif PLANT == 2
  if (cls(u) >= C_QNAN) pb = (u & 0x80000000u) | 0x7FC00000u;
#elif PLANT == 3
  if (cls(u) >= C_QNAN) pb ^= 0x80000000u;
#endif
  return pb;
}

int main(void) {
  /* Fixed before the first run (PLANTS.md part 1; DAZ: SWEEP-SPEC section 5, derived in the predictions file).
     Per plant, per function {floor32, ceil32}, per class {finite, infinity, quiet NaN, signalling NaN}. */
  static const uint64_t want[7][2][NC] = {
    { {0, 0, 0, 0},                 {0, 0, 0, 0} },                  /* 0 none */
    { {0, 0, 0, 8388606},           {0, 0, 0, 8388606} },            /* 1 PL1 */
    { {0, 0, 8388606, 8388606},     {0, 0, 8388606, 8388606} },      /* 2 PL2 */
    { {0, 0, 8388608, 8388606},     {0, 0, 8388608, 8388606} },      /* 3 PL3 */
    { {0, 0, 8388607, 8388606},     {0, 0, 8388607, 8388606} },      /* 4 PL4 */
    { {1, 0, 0, 0},                 {1065353216, 0, 0, 0} },         /* 5 PL5 */
    { {8388607, 0, 0, 0},           {8388607, 0, 0, 0} } };          /* 6 DAZ */
  static const uint64_t want_class[NC] = { 4278190080ull, 2, 8388608, 8388606 };
  const char *cname[NC] = { "finite", "inf", "qNaN", "sNaN" };
  const char *rc[4] = { "nearest", "down", "up", "toward zero" };
#if PLANT == 6
  _mm_setcsr(_mm_getcsr() | 0x0040u);            /* DAZ plant: denormals-are-zero */
#endif
  unsigned csr = _mm_getcsr();
  int env_ok = (csr & 0xE040u) == 0u;
  int env_want = (PLANT != 6);
  int ok_all = (env_ok == env_want);
  printf("bits32_sweep PLANT=%d\n", PLANT);
  printf("environment: MXCSR 0x%04x at start (rounding %s, DAZ %s, FTZ %s) | row nearest, DAZ and FTZ clear: %s"
         " | %s\n", csr, rc[(csr >> 13) & 3u], (csr & 0x0040u) ? "set" : "clear", (csr & 0x8000u) ? "set" : "clear",
         env_ok ? "holds" : "fails", (env_ok == env_want) ? "as fixed" : "NOT AS FIXED");
  for (int up = 0; up < 2; up++) {
    uint64_t n = 0, ncls[NC] = {0}, mis[NC] = {0}, host[NC] = {0}, xs = 0, xi = 0;
    uint32_t first[NC] = {0}; int has[NC] = {0};
    uint32_t u = 0;
    do {
      int c = cls(u);
      uint32_t pb = program(u, up), w = spec32(up, u);
      ncls[c]++;
      if (pb != w) { mis[c]++; if (!has[c]) { first[c] = u; has[c] = 1; } }
      if (w != spec(u, up)) xs++;
      if (c <= C_INF && w != iref(u, up)) xi++;
      { float f = bf(u); if (fb(up ? ceilf(f) : floorf(f)) != w) host[c]++; }
      n++;
    } while (++u != 0u);
    int ok = (n == 4294967296ull) && (xs == 0) && (xi == 0);
    for (int c = 0; c < NC; c++) ok = ok && (mis[c] == want[PLANT][up][c]) && (ncls[c] == want_class[c]);
    ok_all &= ok;
    printf("%s inputs %llu | program vs spec32, all 32 bits:", up ? "ceil32 " : "floor32", (unsigned long long)n);
    for (int c = 0; c < NC; c++)
      printf(" %s %llu/%llu", cname[c], (unsigned long long)mis[c], (unsigned long long)ncls[c]);
    printf(" | spec32 vs spec(): %llu | spec32 vs iref (non-NaN): %llu | %s\n", (unsigned long long)xs,
           (unsigned long long)xi, ok ? "as fixed" : "NOT AS FIXED");
    for (int c = 0; c < NC; c++) if (has[c]) printf("  first %s mismatch at 0x%08x\n", cname[c], first[c]);
    printf("  OBSERVED (no verdict): host %s vs spec32:", up ? "ceilf " : "floorf");
    for (int c = 0; c < NC; c++) printf(" %s %llu", cname[c], (unsigned long long)host[c]);
    printf("\n");
  }
  static const uint32_t pl[] = { 0x000001u, 0x000002u, 0x155555u, 0x2AAAAAu, 0x3FFFFFu, 0x200000u, 0x000000u };
  printf("  OBSERVED NaN table: input -> floor32 program | spec32 | host floorf"
         " || ceil32 program | spec32 | host ceilf\n");
  for (int s = 0; s < 2; s++) for (int q = 0; q < 2; q++) for (unsigned i = 0; i < sizeof pl / sizeof pl[0]; i++) {
    if (!q && pl[i] == 0u) continue;             /* that pattern is an infinity */
    uint32_t u = ((uint32_t)s << 31) | 0x7F800000u | ((uint32_t)q << 22) | pl[i];
    float f = bf(u);
    printf("  0x%08x %s%s -> 0x%08x | 0x%08x | 0x%08x || 0x%08x | 0x%08x | 0x%08x\n", u, s ? "-" : "+",
           q ? "qNaN" : "sNaN", program(u, 0), spec32(0, u), fb(floorf(f)), program(u, 1), spec32(1, u),
           fb(ceilf(f)));
  }
  printf("%s (PLANT=%d)\n", ok_all ? "BITS32 BUILD AS FIXED" : "BITS32 BUILD NOT AS FIXED", PLANT);
  return ok_all ? 0 : 1;
}
