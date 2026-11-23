# bits32 record sweep: the program under test, and SPEC32 transcribed into C

Written 2026-11-22 by a stage agent of the assistant (ruling A4 (a), Skuldd's Push A). Not on the freeze list: it
explains the frozen files beside it. Grades: MEASURED (run, console named by sha256), READ (file:line), ARGUED,
DECLARED, NOT_MEASURED. "Reported" marks a result this stage did not run.

Files: `bits32_sweep.c` (sha256 da83a668b935948cec672ec5480bc6770a844abeef9a5f3f5d577716d7b4ced0),
`run_bits32_sweep.sh` (c7df2aa87bf9e0973886f30431396008214a575a8620a61c0ede8cfcab536311), `BITS32-SWEEP-FROZEN.txt`
(11b2713b4a0ce6b7d7e0e48aa4c3f1b07ee4b32fd22525024396a5e05abca897), `PREDICTIONS-bits32-sweep-run1.txt`
(7b443e3cd800a47469bd4430cacb6b9edf437eafa756cfec8cf89ae09274e006, written before run1). The statement:
`bits32/BITS32_Statement.v`, sha256 c3e65cb7285ddf438145e6fc7284e7749013472b3d4b06f8fc211d345b043e53 (the owner's,
under R1; frozen in the tier with its proof, gated under the owner's anchor, one run on one host).

## 1. The program under test and its conversion path

The C text is the one FCLINK states: `FC_TEXT` of `fclink/FCLINK_Statement.v` says that `c_fun1` of Coq's print of
the frozen shapes `T_floor32` and `T_ceil32` (CPrint.v's `tprint`) equals `floor32_c_text` and `ceil32_c_text` of
`fclink/KernelText.v`, which `fclink/gen_kernel_text.py` quotes from the two lines between the COQ TEXT markers of
`fclink/sweep_fc2.c` (READ: FCLINK_Statement.v:11-13 and :39-41; KernelText.v:1-4 and :8-11; gen_kernel_text.py:4-6).
Each line is a C function `static double mk_floor32(double x)` (`mk_ceil32`): binary64 in, binary64 out, no
conversion inside it. `bits32_sweep.c` copies the two lines with their markers byte for byte (its lines 72-75). Ties
of the copy, MEASURED by this stage on host tools: the runner compares the copy with `fclink/sweep_fc2.c` lines 40-43
by text before every build, and the run's console says "identical"; and fclink's frozen generator, run on
`bits32_sweep.c`, prints `KernelText.v` with only its first line different, by the file name it cites (check K1:
console sha256 e06bfcead5239f964eb307fb85f8c6d031ec599198fe39aced03dee040e50b36; its plant, one digit of the floor32
text changed, made line 9 differ; with the comparison removed the plant went uncaught).

The conversion path, as `fclink/sweep_fc2.c` calls the text (READ: its lines 37-38, 80-82 and 84) and as
`bits32_sweep.c` calls it (`program`, its lines 160-176): the pattern u is copied into a `float` by `memcpy` (`bf`),
widened by the C conversion `(double)f`, the function applied, the result narrowed by the C conversion `(float)d`, and
its bits copied out by `memcpy` (`fb`). With clang -O2 -ffp-contract=off for x86-64 the conversions are `cvtss2sd`
and `cvtsd2ss` (the run's assembly counts them; OBSERVED).

What a sweep of this path shows about the text Push A delivers: for every one of the 2^32 patterns and both
functions, the 32 bits of the result of FCLINK's text when its caller converts with C's `(double)` and `(float)`, on
this host, with this compiler and these flags; NaN patterns included, so the NaN bits of this path are MEASURED here,
not argued. What it does not show: the bits when a caller widens or narrows on integer bits, as the repository's
brief asks of conversions to and from binary32 (READ: `AGENTS.md`, its sentence ending "conversions to and from
binary32 on integer bits"). Such a caller runs its own code on a NaN (whether it quiets, keeps the payload or keeps
the sign is that code's), which this sweep never runs: it needs its own sweep (SWEEP-SPEC section 3; ARGUED). On a
pattern that is not a NaN, an exact integer-bit widening gives the same binary64 value as `(double)f` (every binary32
value is a binary64 value; B32_WIDEN states it of the model) and the result is a binary32 number, so a correct
integer-bit path would give the same bits there (ARGUED, not measured). No floor32 or ceil32 C text that converts on
integer bits is in the batch clone (READ, 2026-11-22: its only `mk_floor32` lines are `tools/ci` test stand-ins).

## 2. SPEC32 beside spec32, line by line

Coq lines are `BITS32_Statement.v`'s (READ); C lines are `bits32_sweep.c`'s. In C every value is an unsigned 32-bit
integer; in Coq an integer (Z). `P(n)` is `1u << n`, used only for n below 32. Each "why" is ARGUED.

- Coq 87: `Definition split32 (u : Z) : bool * Z * Z := Bits.split_bits 23 8 u.` with Flocq 4.2.1's
  `split_bits x := (Zle_bool (mm * em) x, Zmod x mm, Zmod (Z.div x mm) em)`, mm = 2^23, em = 2^8 (Bits.v:77-80).
  C 121: `*s = (P(23) * P(8) <= u); *mf = u % P(23); *ef = (u / P(23)) % P(8);`
  Why: for 0 <= u < 2^32, 2^23 * 2^8 = 2^31 fits; `%` and `/` by a positive power of two are Z.modulo and Z.div on
  non-negative values.
- Coq 88: `Definition join32 (s : bool) (m e : Z) : Z := Bits.join_bits 23 8 s m e.` with
  `join_bits s m e := Z.shiftl ((if s then Zpower 2 ew else 0) + e) mw + m`, ew = 8, mw = 23 (Bits.v:37-38).
  C 117: `return ((s ? P(8) : 0u) + e) * P(23) + m;`
  Why: Z.shiftl by 23 is multiplication by 2^23; the largest value formed is (256 + 150) * 2^23 + 2^23 < 2^32, so
  nothing wraps.
- Coq 96-97: `join32 s (mg * 2 ^ (23 - Z.log2 mg) - 2 ^ 23) (Z.log2 mg + 127)` (enc_int32).
  C 127: `return join32(s, mg * P(23u - zlog2(mg)) - P(23), zlog2(mg) + 127u);` with `zlog2` (C 124), the largest l
  with 2^l <= z.
  Why: mg is in 1 .. 2^23 where it is called (q < 2^23, plus at most 1), so Z.log2 mg is in 0 .. 23 and equals
  zlog2's l; mg * 2^(23 - l) is in [2^23, 2^24), so the subtraction does not wrap.
- Coq 100: `let '(s, mf, ef) := split32 u in` / C 132: `split32(u, &s, &mf, &ef);` (s is 1 for true).
- Coq 101: `if ef =? 255 then (if mf =? 0 then u else Z.lor u (2 ^ 22))`
  C 133: `if (ef == 255u) return (mf == 0u) ? u : (u | P(22));`
  Why: Z.lor with 2^22 on a non-negative value is bitwise or.
- Coq 102: `else if 150 <=? ef then u` / C 134: `else if (150u <= ef) return u;`
- Coq 103: `else if andb (ef =? 0) (mf =? 0) then u` / C 135: `else if (ef == 0u && mf == 0u) return u;`
- Coq 105: `let m := if ef =? 0 then mf else mf + 2 ^ 23 in` / C 137: `uint32_t m = (ef == 0u) ? mf : mf + P(23);`
  (m < 2^24).
- Coq 106: `let k := 150 - Z.max ef 1 in` / C 138: `uint32_t k = 150u - (ef > 1u ? ef : 1u);`
  Why: ef <= 149 on this branch, so k is in 1 .. 149 and does not wrap.
- Coq 107: `let q := m / 2 ^ k in` / C 139: `uint32_t q = (k >= 24u) ? 0u : m / P(k);`
  Why: for k >= 24, m < 2^24 <= 2^k, so Z.div m 2^k = 0; for k < 24 the shift is in range.
- Coq 108: `let away := andb (negb (m mod 2 ^ k =? 0)) (if up then negb s else s) in`
  C 140-141: `uint32_t r = (k >= 24u) ? m : m % P(k);` and `int away = (r != 0u) && (up ? !s : s);`
  Why: for k >= 24, m mod 2^k = m; up = 1 is `true` (the ceiling).
- Coq 109: `let mg := q + (if away then 1 else 0) in` / C 142: `uint32_t mg = q + (away ? 1u : 0u);`
- Coq 110: `if mg =? 0 then join32 s 0 0 else enc_int32 s mg.`
  C 143: `return (mg == 0u) ? join32(s, 0u, 0u) : enc_int32(s, mg);`

Two more integer texts run beside spec32 in every build (copied byte for byte; the runner compares each copy with
its source by text): `spec()` of the research sweep `nanbits.c` (2026-11-21, its lines 63-77; written before the Coq
text) on every pattern, and `iref` (`fclink/sweep_fc2.c` lines 58-71, from the first exhaustive sweep `sweep_fc.c`;
it encodes the magnitude with an integer-to-float conversion) on every pattern that is not a NaN. Three texts by
different routes agreeing is corroboration, not proof that any of them is the Coq function.

## 3. Corroboration of the transcription on fixed patterns, host tools only (MEASURED by this stage)

Check K2 (console sha256 29d389f70195eff8de9a2d6876829dc6ea9639eff163294d71712ea87cb00a6e): a harness that includes
the frozen `bits32_sweep.c` with its main renamed (harness sha256
b4b6646625758a36afecd8bb3dd8a75ef73064a06f8086cfb79005455fab8068), built natively with clang, printed spec32, spec()
and iref on the 4,096 patterns of SWEEP-SPEC section 5 (every exponent field 0 to 255, both signs, trailing fields 0,
1, 2^22 - 1, 2^22, 2^22 + 1, 2^23 - 2, 2^23 - 1 and 0x2AAAAA, in that order: index i = (ef * 2 + s) * 8 + j), both
directions: 8,192 rows (list sha256 7d077c8252ce9915105ecbdad8bdb8f71f1eab7d7a211777139afe81f252ac42). A Python
transcription of the Coq text, written from lines 87-110 with Flocq's split_bits and join_bits (copied from the
research check `spec32_check.py`'s `coq`), gave 0 disagreements with spec32, with spec() and, on rows that are not
NaNs, with iref, in both directions. The checksum, the sum over i of (i + 1) * SPEC32 up u_i mod 2^61 - 1, is
20675489687969882 for up = false and 20666838147440858 for up = true, equal on both sides. Plants, counts fixed
before the run: the Python side with bit 21 for bit 22 on a NaN gave 20 disagreements (10 per direction), and with
every zero result +0 gave 1,015 (all ceiling); with the comparisons removed the first plant went uncaught (0); the
removal alone changes nothing (an equivalent mutant, named so). Predictions file sha256
153a8db48af3b7aac744b29ee20a6435d070a1760de4cf02b6a76516adcb435e.

What it does not show: that Coq evaluates SPEC32 as the transcriptions do; patterns outside the list (the record run
compares spec32 with spec() on all 2^32 and with iref on every non-NaN pattern, which is agreement between C texts).

## 4. Not done here

The Coq corroboration of SWEEP-SPEC section 2 step 4 (`Eval vm_compute` of the checksum above on the frozen SPEC32)
needs the container and was not run: NOT_MEASURED. The two checksum values above, with the list order and formula,
are what such a run would be compared with. Until then, that spec32 is SPEC32 rests on the side-by-side reading of
section 2 (ARGUED) and the agreement of section 3 and of the record run's cross-check rows (corroboration).

## 5. The record run run1 (MEASURED by this stage: one run on one x86-64 host)

`run_bits32_sweep.sh run1`, 2026-11-22T12:13:55Z to 12:19:10Z, console `bits32-sweep-run1-console.txt` (sha256
eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1; 291 lines). Compiler as printed: clang 22.1.8,
target x86_64-pc-windows-msvc, `-O2 -ffp-contract=off`. Last line: `BITS32 SWEEP HELD (bits32_sweep.c
da83a668b935948c)`. Every row came out as `PREDICTIONS-bits32-sweep-run1.txt` fixed it before the run:

- the five freeze-list lines OK; the four copied blocks identical to their sources; the PL5 copy changed exactly the
  two COQ TEXT lines (73 and 74);
- the PLANT 0 assembly: no x87 `fld`/`fstp` and no FMA line; `cvtss2sd` 4, `cvtsd2ss` 7, `addsd` 24, `mulsd` 7,
  `andpd` 8, packed conversions 0 (OBSERVED);
- PLANT 0: all 32 bits of the program's result equal spec32 on all 2^32 patterns of both functions: finite
  4,278,190,080, infinity 2, quiet NaN 8,388,608 and signalling NaN 8,388,606 patterns, 0 differences in each;
  spec32 equals spec() on every pattern and iref on every pattern that is not a NaN;
- PL1 to PL5 at their fixed counts (sNaN 8,388,606; qNaN and sNaN 8,388,606 each; 8,388,608 and 8,388,606;
  8,388,607 and 8,388,606; floor32 1 and ceil32 1,065,353,216 finite), each in both functions where fixed;
- DAZ (PLANT 6): the environment row failed as fixed (MXCSR 0x1fc0, DAZ set) and 8,388,607 finite patterns per
  function differed (first 0x80000001 for floor32, 0x00000001 for ceil32);
- OBSERVED, no verdict: MXCSR 0x1f80 at start in builds 0 to 5; the host's floorf and ceilf equal spec32 on every
  pattern in builds 0 to 5 and differ on 8,388,607 finite patterns under DAZ; in the NaN table of PLANT 0 the program,
  spec32 and host columns agree on all 26 lines.

What it shows and does not show is section 1's second paragraph and `bits32_sweep.c`'s header: the C conversion path
on this host, compiler and flag set; not another compiler, flag set, processor, host or MXCSR state, not exception
flags, not a path that converts on integer bits, and nothing about Coq beyond what section 2 argues.
