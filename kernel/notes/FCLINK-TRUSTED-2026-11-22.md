<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# FCLINK: what it proves, what it trusts, what is measured

Written by the assistant on 2026-11-22 under the owner's ruling S282-4 (c) of 2026-11-22 (adopted by his
representation). The frozen files of `kernel/coq/fclink` cite a `TRUSTED.md` for where a proof of FCLINK stops and
what is trusted beyond it, and a `PLANTS.md` for which changes such a proof would and would not notice. Neither file
is in this tree (`kernel/notes/LIMITATIONS.md`). They were drafts, written before the proof and kept in the authors'
workspace (REPORTED). This note states what `TRUSTED.md` declared, brought to the state after the proof. `PLANTS.md`
stays out of this tree; the plants that FCLINK's gate runs are described in `kernel/coq/fclink/gate.json` and summed
up in section 4, with what the proof would not notice. This note changes no frozen byte; it stands beside the frozen
files.

Grades: GATED (a closing theorem of the proved table of `THEOREMS.md`, whose gate held); READ (what a file of this
tree says, at path:line); MEASURED (a run: its record named by its path in this tree or, for a record kept outside
it, by its sha256; or a search or a comparison of this tree's files, named by what it searched or compared); ARGUED
(reasoning that no machine checked); DECLARED (relied on, not checked); REPORTED (a result of the authors' earlier
work whose record is not in this tree); NOT_MEASURED. Each run named below is one run, on the authors' one x86-64
host, made by the authors and their agents, all of one model family.

## 1. What is proved

`fclink.Closed.fclink_holds` (`kernel/coq/fclink/Closed.v`) proves `fclink.FCLINK_Statement.FCLINK`, stated in
`kernel/coq/fclink/FCLINK_Statement.v` (GATED, `THEOREMS.md`). The statement is a conjunction of four parts:

```coq
Definition FCLINK : Prop := FC_TEXT /\ FC_PARAM /\ FLOOR32 /\ CEIL32.
```

Each part, read as a statement about Coq's model (READ, from the files named):

- **FC_TEXT**, the text:

  ```coq
  Definition FC_TEXT : Prop :=
    c_fun1 "mk_floor32" (T_floor32 string tprint "x") = floor32_c_text /\
    c_fun1 "mk_ceil32" (T_ceil32 string tprint "x") = ceil32_c_text.
  ```

  `T_floor32` and `T_ceil32` are the frozen shapes of FLOOR32 and CEIL32, written over `TOPS`, a record of
  operations and constants. `tprint` (`kernel/coq/fclink/CPrint.v`) is that record over Coq strings: each operation
  writes C text, such as `(a + b)` for addition and `fabs(a)` for the absolute value, and each finite constant is
  written as `0.0` for +0, `(-0.0)` for -0, or a C hexadecimal constant such as `0x18000000000000p0`, bracketed with
  a minus sign when negative. `c_fun1` puts a body into the line `static double <name>(double x) { return <body>; }`.
  `floor32_c_text` and `ceil32_c_text` are the two strings of `kernel/coq/fclink/KernelText.v`. So FC_TEXT says
  that the line `c_fun1` builds around the printer's text of each frozen shape, with the name `x` as input, is the
  corresponding string, character for character. It is an equality of Coq strings: it says nothing of what C makes
  of them, and nothing of any file: its terms are the strings that `KernelText.v` defines, and no Coq term refers to
  `sweep_fc2.c`.
- **FC_PARAM**, the same operations in the same pattern:

  ```coq
  Definition FC_PARAM : Prop :=
    forall (rel : string -> b64 -> Prop) (v : b64),
    FC_FIELDS string b64 tprint tieee_ops rel -> rel "x" v ->
    rel (T_floor32 string tprint "x") (T_floor32 b64 tieee_ops v) /\
    rel (T_ceil32 string tprint "x") (T_ceil32 b64 tieee_ops v).
  ```

  `b64` is Flocq's binary64 format with one NaN, and `tieee_ops` is the record of Flocq's IEEE binary64 operations,
  at round to nearest even where they round. `FC_FIELDS string b64 tprint tieee_ops rel` holds when `rel` relates
  the printed constant to the IEEE constant at each of `K_0`, `K_1`, `K_CN` and `K_BIG` (0, 1, 1.5 * 2^52 and 2^23)
  and is kept by the six operations the shapes use: `t_add`, `t_sub`, `t_mul`, `t_abs`, `t_sel_le` and `t_sel_lt`.
  So FC_PARAM says that every relation between texts and binary64 values that holds at those constants, is kept by
  those six operations and relates the text `x` to `v` also relates the printed text of each shape to the IEEE
  computation of that shape at `v`. It names no relation; in particular, it does not say that C reads the text as
  that computation (section 3). `t_div` and `t_neg` are not among its premises, and the two shapes use neither.
- **FLOOR32** and **CEIL32** are the frozen statements of `floor32` and `ceil32`, proved by
  `floor32.Closed.floor32_holds` and `ceil32.Closed.ceil32_holds` (GATED, `THEOREMS.md`). On every finite binary64
  value that is a binary32 number, the IEEE computation of the floor shape returns a finite value, the floor of the
  input, whose sign bit is the input's. An infinite or NaN input is returned as it is. On every input that is a
  binary32 number or not finite, the computation equals Flocq's `Bnearbyint` toward minus infinity. CEIL32 says the
  same of the ceiling, with `Bnearbyint` toward plus infinity. What the two do not say is in their headers
  (`kernel/coq/floor32/FLOOR32_Statement.v:33-37`, `kernel/coq/ceil32/CEIL32_Statement.v:33-37`), and what they
  trust follows it (lines 38-40 of each).

## 2. How it is proved, and what the proof rests on

How it is proved (READ, `kernel/coq/fclink/Link.v:5-14`): each half of FC_TEXT, `FC_FLOOR_TEXT` and `FC_CEIL_TEXT`,
by computing both sides to closed strings with Coq's virtual machine (`vm_compute`) and then `reflexivity`; FC_PARAM
by unfolding the two shapes into one term of the record's operations and closing each node with the premise of
FC_FIELDS for that operation, with no recursion and no induction. The file's comment adds that coqchk checks the
equality of the strings again by the kernel's conversion, without the virtual machine (section 3.4 grades this).

What the proof rests on, as the statement's header lists it (READ, `kernel/coq/fclink/FCLINK_Statement.v:25-29`):
Coq's kernel; the four axioms `sig_not_dec`, `sig_forall_dec`, `functional_extensionality_dep` and `classic`; Coq's
standard library (its Reals, NArith, ZArith and String libraries); Flocq; the frozen statements it imports and the
frozen files they import; and the meaning of the printed C forms, which section 3 declares. Through FLOOR32 and
CEIL32 it also rests on what those frozen statements trust: that Flocq's `Bplus`, `Bminus` and `Bmult` at `mode_NE`,
`Babs`, `Bleb` and `Bltb` are IEEE 754's; that `Bsign` is the sign bit and `B754_zero` the signed zero; and, for
FL_IEEE and CL_IEEE only, that Flocq's `Bnearbyint` at `mode_DN` and `mode_UP` is IEEE 754's
roundToIntegralTowardNegative and roundToIntegralTowardPositive (DECLARED,
`kernel/coq/floor32/FLOOR32_Statement.v:38-40` and `kernel/coq/ceil32/CEIL32_Statement.v:38-40`; `BOUNDARIES.md`,
rows B020 and B063).

Read together (ARGUED: a reading of the four parts, not a further theorem), the two strings of `KernelText.v` are the
printer's text of the very shapes whose IEEE computation FLOOR32 and CEIL32 are about, built from the same operations
in the same pattern. A changed operator, constant or step in either string makes FC_TEXT false.

## 3. What is declared, not proved

### 3.1 From Coq's text to C

FCLINK stops at the text. To carry it to C, one reads FC_PARAM at the relation "s is a text built from the name `x`
and the printed constants by the printed forms listed below, and s, evaluated where the parameter `x` holds a
`double` that stands for v, gives a `double` that stands for w". Here a `double` stands for the binary64 value of the
same sign and value when it is finite or infinite, and for b64's one NaN when it is a NaN, whatever its payload: b64
has a single NaN (READ, `kernel/coq/ieee64/IEEE64_Statement.v:41`). That relation is not a Coq term. No file of this
tree defines a semantics of C in Coq (ARGUED; a search of this tree's `.v` files for a `Require` followed on its line
by CompCert, Clight, Csyntax, Csem or VST finds none, MEASURED), and `BOUNDARIES.md`, row B077, says that C reads the
text as the IEEE computation only by declaration (READ). That the relation meets
FC_FIELDS is DECLARED, constant by constant and operation by operation, in the list below: each C form is declared
to compute its operation in `tieee_ops`, and the frozen statements in turn trust those operations to be IEEE 754's
(section 2). If it does, FC_PARAM at that relation and FC_TEXT give that `mk_floor32` and `mk_ceil32`, as
`KernelText.v` writes them, return the IEEE computation of the frozen shapes at v, NaN payloads aside. FLOOR32 and
CEIL32 then give, for v a binary32 number, the floor and the ceiling with the sign rule of section 1, and for v
infinite or a NaN, v itself; for a finite binary64 v outside format32 (Flocq's FLT(-149, 24): the binary32 numbers
and the numbers of that form above the binary32 range) they say nothing (`BOUNDARIES.md`, row B060). This conclusion
is ARGUED: an instance of FC_PARAM taken outside Coq, at a relation no Coq term of this tree states. That the strings
of `KernelText.v` are the lines of the sweep program is the step of section 3.2. Proof does not pick up again here:
what C text means is the C standard's and a compiler's, and a semantics of C in Coq would move the meaning into Coq,
not the compiler (READ, `BOUNDARIES.md`, row B077).

The meanings relied on, for the forms that occur in the two strings, on binary64 `double` values (DECLARED):

- `(a + b)`, printed for `t_add`, whose operation in `tieee_ops` is `Bplus` at `mode_NE`: IEEE 754 binary64
  addition, rounded to nearest, ties to even.
- `(a - b)`, for `t_sub`, `Bminus` at `mode_NE`: IEEE 754 binary64 subtraction, rounded to nearest, ties to even.
- `(a * b)`, for `t_mul`, `Bmult` at `mode_NE`: IEEE 754 binary64 multiplication, rounded to nearest, ties to even.
  Each string holds one product, `(x * 0.0)` (READ: one ` * ` in each line, `kernel/coq/fclink/sweep_fc2.c:41-42`),
  which for a finite x is a zero with the sign of x (DECLARED).
- `fabs(a)`, for `t_abs`, `Babs`: the `fabs` of `<math.h>`, the operand with its sign bit cleared; a NaN for a NaN.
- `(a <= b ? c : d)`, for `t_sel_le`, `if Bleb a b then c else d`: `<=` is IEEE 754's ordered comparison, false when
  an operand is a NaN, with -0 and +0 equal; `?:` gives c when it holds and d otherwise.
- `(a < b ? c : d)`, for `t_sel_lt`, `if Bltb a b then c else d`: `<` likewise, false when an operand is a NaN and
  false between -0 and +0.
- `0.0`, for the constant `K_0`: positive zero.
- `0x10000000000000p-52`, `0x18000000000000p0` and `0x10000000000000p-29`, for `K_1`, `K_CN` and `K_BIG`: a C99
  hexadecimal floating constant denotes its value m * 2^e exactly when that value is a binary64 number, as these
  three are (1, 1.5 * 2^52 and 2^23).
- `x` and the line `static double mk_floor32(double x) { return ...; }` (and `mk_ceil32`): the parameter holds the
  binary64 argument, and the function returns the binary64 value of the expression, with no excess precision.

`CPrint.v` also prints `(a / b)`, `(- a)`, the negative constants (`(-0.0)` and `(-0x...p...)`) and `@not_finite@`
(READ, `kernel/coq/fclink/CPrint.v:17-23`). No string of FCLINK holds them, and their meaning is not declared here;
`@not_finite@` is not C at all.

Three more points the reading needs (ARGUED). Every text that `tprint` writes is bracketed, a call or a single
constant, and the input is the name `x`, so C reads each text that a form places as one operand, with no side effect.
That is why the relation is limited to the texts the forms build: FC_FIELDS asks it of every string, and without the
limit it fails (`x - x` stands for +0 at v = 1, while `t_mul` writes `(x - x * 0.0)`, which C reads as
x - (x * 0.0), that is 1; and `((x = 2.0) + x)` is undefined in C). C's `?:` evaluates only the operand it gives,
where Coq's selection chooses between two values; the two differ only in exception flags, which no statement states.
The printed text writes every shared subexpression out again, and each copy has the same value when the operations
are deterministic in a fixed environment.

The compiler used does not declare C99's Annex F (IEC 60559 arithmetic): an earlier drafting run of the same clang
22.1.8, asked for its predefined macros with no `-std`, `-O` or `-f` option, for the target of the recorded runs,
reported neither `__STDC_IEC_559__` nor `__FAST_MATH__` predefined (REPORTED: a run of the authors' workspace made
before the final sweep program, not a record of this tree). So C99 does not itself promise these meanings here; they
rest on the compiler's floating-point semantics on x86-64 with SSE2 (DECLARED).

This tree holds no check of these meanings against the texts of C99, IEEE 754 or the compiler's documentation
(NOT_MEASURED).

### 3.2 From the sweep program to `KernelText.v`

No Coq term refers to a file: FC_TEXT is about the two strings that `KernelText.v` defines, and that they are the two
lines between the markers of `kernel/coq/fclink/sweep_fc2.c` lies outside Coq (READ, `BOUNDARIES.md`, row B067). The
step rests on three things. The gate runs `kernel/coq/fclink/gen_kernel_text.py` again and compares its output with
`KernelText.v` byte for byte (MEASURED, the gate's console, section 4). Both freeze lists record `sweep_fc2.c` at sha256
924bd031c84172fd98203f1b755f1f63b8cc62aecd76bd6358273f00fc2a7005 (READ, `kernel/coq/fclink/FROZEN.txt:5` and
`kernel/coq/fclink/FROZEN4.txt:55`), `FROZEN4.txt` under the owner's anchor (`kernel/coq/ANCHORS.md`); the gate
found the 109 files of that list unchanged, and the sweep checked the program it built against `FROZEN.txt` before
building it (MEASURED, section 4). That the generator's strings are the lines' bytes is ARGUED from its header: it
refuses a double quote, which Coq would write twice, and every character outside printable ASCII (READ,
`kernel/coq/fclink/gen_kernel_text.py:8-13`; `BOUNDARIES.md`, row B067). No theorem covers this step.

### 3.3 The environment the meanings assume

- Expressions are evaluated in binary64 (`FLT_EVAL_METHOD` 0): `kernel/coq/fclink/sweep_fc2.c` refuses to compile
  otherwise (READ, `kernel/coq/fclink/sweep_fc2.c:30-32`), and it compiled in the recorded runs (MEASURED, section 4).
- Rounding is to nearest, ties to even. The sweep program never changes the rounding mode: it includes no
  `<fenv.h>` and calls nothing that sets a mode (READ, `kernel/coq/fclink/sweep_fc2.c:25-107`; a search of the file
  for `fenv`, `fesetround`, `_controlfp` and `_mm_setcsr` finds none, MEASURED). That the mode is to nearest when the
  program starts is the C runtime's starting state, DECLARED for the recorded runs of `sweep_fc2.c`, which record no
  floating-point environment. The record sweep of `kernel/records/bits32/` read MXCSR 0x1f80 at its start (rounding
  to nearest, denormals-are-zero and flush-to-zero clear) in its build without a plant (MEASURED for that run only,
  `kernel/records/bits32/bits32-sweep-run1-console.txt:27-28`). Another caller could set another mode (DECLARED: a
  precondition).
- No contraction and no fast-math: the recorded builds pass `-ffp-contract=off` and no fast-math flag, and no x87 or
  FMA instruction was found in their objects (MEASURED, section 4). Each string's one product feeds a selection,
  never an addition, so a contraction would have nothing to fuse (ARGUED).
- Denormals-are-zero and flush-to-zero off: a precondition, not a theorem (DECLARED; `BOUNDARIES.md`, row B065 for
  denormals-are-zero and row B077 for both). A research run on one host found that, of seven MXCSR states, only
  denormals-are-zero changed the results, on 8,388,607 subnormal inputs per function (MEASURED by a research agent of
  the authors' family; `BOUNDARIES.md`, row B065). The guard `kernel/runtime/mk_fpenv.c` reports denormals-are-zero,
  and no library calls it (READ, `BOUNDARIES.md`, row B065).
- The text of `sweep_fc2.c` before its markers holds five `#include` lines, two preprocessor checks and two helpers,
  `bf` and `fb`, and defines no macro; the names the builds define with `-D` (`WANT_F`, `WANT_C`, `NEGZ_F` and
  `NEGZ_C`) occur in neither line (READ, `kernel/coq/fclink/sweep_fc2.c:25-43`). What the five headers define is the
  C library's, and that `fabs` there is the one of `<math.h>` is DECLARED.
- The sweep program around the two lines (`BOUNDARIES.md`, row B079): `(double)f` widens a binary32 value to the
  same binary64 value, `(float)d` returns d when d is a binary32 number, `memcpy` copies the bits, and the integer
  comparisons and counters do as their C text says (DECLARED); that `iref` is the floor and the ceiling with IEEE
  754's rule for the sign of a zero is ARGUED from reading it (`kernel/coq/fclink/sweep_fc2.c:58-71`); `floorf` and
  `ceilf` are the C library's and serve as a cross-check only (DECLARED).
- No compiler and no processor is proved: no statement says that a compiler emits, or a processor executes, the
  modelled operations, or that a processor's conversions between binary32 and binary64 are the modelled ones (READ,
  `BOUNDARIES.md`, rows B006 and B069).

### 3.4 Inside Coq: the libraries, the checker and the virtual machine

- FCLINK's closure holds Coq's `Strings.Ascii`, `Strings.Byte` and `Strings.String`. The gate rechecked each with
  coqchk, clean (MEASURED, section 4). On 2026-11-22, before the branch run of ruling S280-9 (b), they were not on
  `kernel/coq/EXPECTED-CI-LIBRARIES.txt` (MEASURED: a search of that file; `BOUNDARIES.md`, row B078), so CI's
  gate-log check is to refuse the `fclink` leg until they are (ARGUED from `tools/ci/check_gate_log.py`; MEASURED
  in that run's Gate fclink job, log 137440490797: 1 of 15 rows failed, the library row). Rulings A2 (a) and A3 (a)
  put their lines on CI's list in Push A, from that branch run (READ, row B078).
- FC_TEXT's proofs use Coq's virtual machine at compilation (READ, `kernel/coq/fclink/Link.v:25` and 30). That
  coqchk rechecks them by the kernel's conversion, without the virtual machine, is the authors' statement (DECLARED:
  `kernel/coq/fclink/Link.v:6-9` and `kernel/hardening/features/feature_row3.py:10` say so, and no record of this
  tree measures it); coqchk passed on every library of the folder (MEASURED, section 4). coqchk shares Coq's kernel
  code, so this is a second check, not an independent one (READ, `THEOREMS.md`, section Checking a row yourself;
  `BOUNDARIES.md`, row B001). The entries of Coq's list of critical bugs that concern the virtual machine are covered
  only by that re-check (READ, `kernel/notes/LIMITATIONS.md:97-98`, where the reading of that list is REPORTED). No
  file of `kernel/coq/fclink` names `native_compute` (MEASURED: a search of the folder's files).
- The proofs were compiled and checked with Coq 8.20.1 and Flocq 4.2.1 as built in the pinned container image (READ,
  `BOUNDARIES.md`, row B003).

## 4. What is measured, and where

FCLINK's gate held under the owner's anchor in one run, and the exhaustive sweep of the two printed lines held at -O0
and at -O2 in each of its two records, all on one host (MEASURED; the records, and what each does not show, are below).

<details>
<summary>The gate, its plants, the sweeps and their records</summary>

- **The gate.** FCLINK's gate (`kernel/coq/gate/gate4.py`, with `--recheck`) held 294 of 294 on 2026-11-22, given
  as its anchor the owner's own sha256 of `kernel/coq/fclink/FROZEN4.txt`,
  96ac2c42d44ef185ac8b70ab12da628268ab1471907ac4a5df5a97d3305b0dfa (`kernel/coq/ANCHORS.md`). Its console is not
  in this tree, as it holds details of the authors' host: sha256
  3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e, listed in `kernel/records/INDEX.md` with a
  rehearsal and a recheck from a fresh copy that held the same count (MEASURED). Among its rows: the 109 files of
  the freeze list are unchanged; the six files of the folder compile; `KernelText.v` is what `gen_kernel_text.py`
  prints; Print Assumptions of the identity check is exactly the four axioms of section 2; coqchk -norec passes on
  each library of the folder and on each of the 312 outside libraries of the closure; every plant is refused;
  nothing is written to the judged tree but the gate's output folder and library log (MEASURED, the same console).
  Of the 294 rows, 257 concern the folders `fclink` depends on (READ, `THEOREMS.md`, its section on what the gate
  counts). What the gate does not show: it ran on a copy of `kernel/coq`, not on this tree (READ, `BOUNDARIES.md`,
  row B076); the tie to this tree is the freeze list under the owner's anchor, and on 2026-11-22 all 109 rows of
  `kernel/coq/fclink/FROZEN4.txt` equalled the sha256 of this tree's files (MEASURED, a comparison of sha256). The
  rehearsal and the recheck were given the sha256 of the freeze list as the authors computed it (the same value as
  the owner's), and all three runs were made by agents of one model family (READ, `kernel/records/INDEX.md:181-183`
  and 228-229). The gate shows nothing on another host or Coq build (section 5).
- **The plants.** `kernel/coq/fclink/gate.json` names fourteen plants, each a planted file the gate must refuse, and
  the run above refused all fourteen (MEASURED). Six replace `KernelText.v` by the quoted lines of a planted sweep
  program, with an operator, a constant or the zero step changed: five are refused at `FC_FLOOR_TEXT` and the one
  that changes only the ceiling line at `FC_CEIL_TEXT`. One adds a blank to `KernelText.v` by hand and is refused as
  not the generator's output. One makes the printer write subtraction with a plus sign and is refused at
  `FC_FLOOR_TEXT`. Two change the statement, one leaving `t_mul` out of FC_FIELDS and one relating the floor text to
  the ceiling computation, and both are refused in FC_PARAM's proof. Four attack the proof (an `Admitted`, an
  `Axiom`, a closing theorem of three of the four parts, a recursion with its guard check switched off) and are
  refused by the reader of Print Assumptions or by the identity check. A refusal shows that the gate rejects a
  planted file, not that the plant's claim is false (READ, `THEOREMS.md`, the same section).
- **What the proof does not notice** (ARGUED; the frozen headers cite `PLANTS.md` for this, section 6). FC_PARAM
  holds for every pair of records, whatever their fields, so no change to the printer alone makes it false: for
  FC_PARAM every printer is an equivalent mutant. A printer change that alters the text of the shapes is caught by
  FC_TEXT instead, as the plant `printer-sub-plus` is (MEASURED, refused above); one that alters only `t_div`,
  `t_neg` or a constant the shapes do not use leaves FCLINK true and is caught only by the freeze lists. A premise
  of FC_FIELDS left out for a field the shapes use makes FC_PARAM unprovable, as the plant `fields-no-mul` shows for
  `t_mul` (MEASURED, refused above); premises for `t_div` and `t_neg`, which the shapes do not use, would change
  nothing, and the frozen statement has none. A change to
  `CPrint.v` made together with the same change to the two lines of `sweep_fc2.c`, with `KernelText.v` printed
  again, keeps FCLINK provable: FC_TEXT then equates the new printer's text with the new lines. What stands against
  such a pair lies outside the proof: the freeze lists under the owner's anchor, which record both files, so that
  the gate refuses a changed byte; the meanings declared in section 3, which tie each printed form to its operation;
  and the sweep. The program around the markers is outside the proof altogether (`BOUNDARIES.md`, row B079).
- **What the sweep alone cannot tell.** For two of the text plants, `cst-cn-odd` (the constant 1.5 * 2^52 written
  one larger) and `equiv-big-lt` (the test `2^23 <= fabs(x)` written with `<`), `gate.json` records that the
  exhaustive sweep finds no difference (REPORTED: those sweep runs are not records of this tree). The reasons are
  ARGUED: with the odd constant, n is still a whole number within 1/2 of x, which is all the next step needs; at
  |x| = 2^23 the other branch also returns x. FC_TEXT tells both from the proved text, and the gate refused both at
  `FC_FLOOR_TEXT` (MEASURED). With the step of section 3.2 from the sweep program to `KernelText.v` (MEASURED and
  ARGUED there; `BOUNDARIES.md`, row B067), this is what FCLINK adds to the sweep: the swept lines are the printed
  text of the shapes that FLOOR32 and CEIL32 are about, not another program that gives the same results on the
  inputs swept (ARGUED).
- **The sweep of the printed lines.** `kernel/records/fclink/sweep-real-r1.txt` (sha256
  804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a) records `tools/ci/check_sweep.py` run on this
  tree on 2026-11-22. It checked that `kernel/coq/fclink/sweep_fc2.c` has the sha256 that
  `kernel/coq/fclink/FROZEN.txt` records, built it with clang 22.1.8 at -O0 and at -O2 with
  `-std=c99 -ffp-contract=off`, found no x87 or FMA instruction in the objects (its canaries show that the scan finds
  both), and ran it. On all 2^32 binary32 patterns, wherever no result is a NaN, each function's result stored to
  binary32 differs on 0 inputs from the C library's `floorf` or `ceilf`, from an integer reference and from a hand
  transcription of the shape, and its binary64 result differs on 0 from the integer reference widened; wherever one
  result is a NaN, all are. One floor32 result and 1,065,353,216 ceil32 results are -0. A plant whose zero step never
  applies gave its predicted counts. The verdict is "SWEEP CHECK HELD: 19 of 19 rows" (MEASURED, one run on one
  host). `kernel/records/fclink/local-fclink-run1.txt` (sha256
  39a997d8a41b46799d14de820a5072e2307a3792ce534d21a222f7d32f8968fc) records the same check on a scratch root earlier
  that day, with the same verdict (MEASURED).
- **What that sweep covers without the meanings of section 3** (ARGUED from the GATED and MEASURED results above).
  FLOOR32 fixes every bit of the proved computation's result on every finite binary32 input, and CEIL32 likewise: a
  finite value, the floor (the ceiling), with the input's sign bit, and two finite binary64 values with the same
  value and sign bit have the same bits; an infinite input comes back as it is. In the recorded run, the binary64
  results of each binary built from the frozen program have the bits of the integer reference's results widened on
  every input where no result is a NaN (MEASURED, `kernel/records/fclink/sweep-real-r1.txt`). So for those two
  binaries, at that call site, the results equal the proved computation's on every binary32 input, NaN payloads
  aside, provided the integer reference is the floor and the ceiling with IEEE 754's rule for the sign of a zero
  (ARGUED from reading `sweep_fc2.c`; `BOUNDARIES.md`, row B079). This needs neither the meanings of section 3 nor
  that the compiler translated the two printed lines as section 3 reads them. It still rests on the rest of the
  sweep program (the conversions, the integer reference, the comparisons and the counting) being compiled and run as
  its C text says (`BOUNDARIES.md`, rows B079 and B006), for those two binaries only (ARGUED). The never-step plant's
  binaries, built by the same compiler from the frozen program with only the zero step's test changed, counted the
  differences predicted for them (MEASURED, the same record; `tools/ci/SWEEP-SOURCE.txt:37-48`): this shows that the
  comparisons and counters can find a difference in those other binaries, not that they ran as written in the two
  frozen ones (ARGUED). It says nothing of another binary, compiler, flag set or host, nor of another call site: the
  functions are static, and the compiler may inline them into the loop (READ, `kernel/coq/fclink/sweep_fc2.c:21-23`).
- **NaN bits, on the C-conversion path only.** The all-bits record sweep of `kernel/records/bits32/` holds the same
  two lines: its check K1 shows that `gen_kernel_text.py` prints `KernelText.v` from them, but for the first line,
  which names the file read (MEASURED, `kernel/records/bits32/k1-run1-console.txt`); K1's script is kept in the
  authors' workspace, so a reader cannot rerun K1 from this tree (READ, `kernel/records/INDEX.md:278`). The record
  sweep calls the two functions on `x = (double)f` and stores their result `d` as `(float)d`
  (`kernel/records/bits32/bits32_sweep.c:164-166`) and compared all 32 bits of every result with BITS32's SPEC32 as
  transcribed into C integers, on all 2^32 patterns, NaN patterns included: in the build without a plant, 0
  differed, built with clang 22.1.8 at -O2 with `-ffp-contract=off` (MEASURED, one run on one host,
  `kernel/records/bits32/bits32-sweep-run1-console.txt`, sha256
  eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1). That the C transcription is SPEC32 is ARGUED
  (`BOUNDARIES.md`, row B103). A caller that converts binary32 on integer bits has not been swept (NOT_MEASURED).
- **The floating-point state.** In that record sweep, the build run with denormals-are-zero set changed the results
  on 8,388,607 finite patterns of each function, and the record's environment row refused that state (MEASURED, the
  same console).

</details>

## 5. What is not measured

Each item below is NOT_MEASURED.

- The sweep with another compiler (GCC), another flag set, another processor or system, or on GitHub's runners: on
  2026-11-22, before the branch run of ruling S280-9 (b), the sweep job of `tools/ci/check_sweep.py` had not run on
  GitHub (`BOUNDARIES.md`, rows B064 and B102).
- FCLINK's gate on another host or Coq build: on 2026-11-22, neither the Linux CI nor the minimal harness had run on
  `fclink`; the branch run of ruling S280-9 (b) is to run its gate on GitHub's runners before Push A's final head
  (`BOUNDARIES.md`, row B076).
- NaN payloads through `sweep_fc2.c`, which compares a NaN result as NaN-ness only.
- Exception flags: no statement states them, and no run records them (`BOUNDARIES.md`, row B062).
- A call site other than the loops of `kernel/coq/fclink/sweep_fc2.c` and `kernel/records/bits32/bits32_sweep.c`
  (two programs, one compiler, one host).
- A record in this tree of the compiler's predefined macros: section 3.1 cites the authors' report that clang 22.1.8
  predefines neither `__STDC_IEC_559__` nor `__FAST_MATH__`, which is not a record of this tree.
- Whether FCLINK says what its owner meant: it is a candidate, not adopted, and no reader has confirmed that it says
  what its owner meant (`BOUNDARIES.md`, row B004; `README.md` lists it as a candidate).
- A reading of the files of `fclink` by a reader outside the authors' model family: none has read them
  (`kernel/notes/LIMITATIONS.md`).

## 6. The references in the frozen files

The frozen files keep their words; this list says where each reference now leads (READ, each at its line).

- `kernel/coq/fclink/FCLINK_Statement.v:25-29` and `kernel/coq/fclink/CPrint.v:26-29` cite `TRUSTED.md` for where
  the proof stops and for the meaning of the printed C forms: sections 1 to 3 of this note. `CPrint.v` sends the
  reader there for every form it prints; section 3.1 declares meanings only for the forms in the two strings.
- `kernel/coq/fclink/gen_kernel_text.py:6-7` cites "TRUSTED.md, section 4" for the virtual machine: section 3.4.
- `kernel/coq/fclink/sweep_fc2.c:7-8` says the equality of its lines with the printed text is not proved until
  `Link.v` is compiled. `Link.v` is compiled (MEASURED, the gate's compile row, section 4), and FC_TEXT holds as the
  first part of FCLINK (GATED). `kernel/coq/fclink/sweep_fc2.c:22` cites `TRUSTED.md` for what the text means in C:
  section 3.
- `kernel/coq/fclink/FCLINK_Statement.v:26`, `kernel/coq/fclink/CPrint.v:27` and the descriptions of eight plants in
  `kernel/coq/fclink/gate.json` (lines 44, 53, 62, 71, 80, 89, 106 and 115) cite `PLANTS.md`, which is not in this
  tree: section 4 sums up the plants and what the proof does not notice, and `gate.json` describes each plant.
- Three frozen plant files repeat their originals' citations of `TRUSTED.md` and `PLANTS.md`:
  `kernel/coq/fclink/plants/CPrint_sub_plus.v:26-29`, `kernel/coq/fclink/plants/FCLINK_Statement_fields_no_mul.v:25-29`
  and `kernel/coq/fclink/plants/FCLINK_Statement_param_floor_ceil.v:25-29`. They lead to the same sections.
