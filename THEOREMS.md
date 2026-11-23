<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Theorems

Every proved claim of the kernel, in one place. Coq has also checked the following, all under `kernel/hardening/` with their consoles: 32 examples at ±2^106, +2^104, +2^105, +2^107 and the two binary32 neighbours of +2^106 (`big106/Big106.v`), 25 examples about `sincos32i` and `sincos32z` (`examples/Examples.v`), 45 refutations of planted claims (`plants/stage3/`, listed in `plants/PLANT-LABELS.md`) and one narrowing probe (`r7-probes/NarrowProbe.v`); none of them is one of the candidate statements below. Skuldd claims as proved nothing absent from this file; the imported documents of `orlog/` and `verdandi/`, and comments inside frozen files, keep their own words.

- A **statement file** is the claim: read it, not a summary of it. Its sha256 is in its folder's `FROZEN4.txt`.
- The **closing theorem** is the proof's name. Each folder's `Identity.v` types it by the statement, so Coq itself
  checks that the proof proves exactly that statement.
- Every closing theorem rests on exactly four axioms of Coq's standard library:
  `ClassicalDedekindReals.sig_not_dec`, `ClassicalDedekindReals.sig_forall_dec`,
  `FunctionalExtensionality.functional_extensionality_dep` and `Classical_Prop.classic`.
- **Candidate** means proved and not adopted by the owner as final (see `kernel/notes/LIMITATIONS.md`).
- **Where each proof stops** (an input class it does not cover, a model it abstracts, a layer it does not reach, or
  a trust it rests on), what covers the part beyond and where proof picks up again: the boundary map,
  `BOUNDARIES.md`, one row per stop. `tools/ci/check_boundaries.py` holds every statement of the proved table below
  to a well-formed row there; it does not show that a row is true.

## The law of the turns kernel: stated, NOT PROVEN IN THIS TREE

| Statement | Status | Its theorem, once proved |
|---|---|---|
| `SINCOS32_LAW`: sine and cosine of 2πx on 32-bit patterns, the two conversions, the NaN pattern, the sign of every zero, every intermediate finite and moderate | **stated, not proven in this tree**; withheld from this tree until an independent reviewer has written a blind formalisation of the same convention | `MKF.sincos32law.Closed.sincos32_law_holds`, in `kernel/coq/sincos32law/Closed.v`, typed by `kernel/coq/sincos32law/Identity.v`; it will be the first row below |

## Proved (candidates)

All paths are under `kernel/coq/`. Gate verdicts are those of each folder's gate (`gate/gate4.py`), run in a pinned
container with no network, each given its folder's `FROZEN4.txt` sha256 as its anchor. The gates of the first thirteen
rows ran between 2026-11-14 and 2026-11-16. The consoles of `f32`, `p32`, `p32r`, `exp32`, `exp32r` and `ieee64` are
in Verðandi's copies of those folders (`verdandi/mathkernel/F32/<folder>/`, from the tree's root); those of the other
seven of the thirteen stayed in the authors' workspace.

The gates of the next four rows ran with `--recheck` on 2026-11-21 and 2026-11-22 (UTC), each on a copy of
`kernel/coq` whose files are this tree's but for `ANCHORS.md`, the four folders' `FROZEN.txt`, the folders `rti32`,
`order32`, `bits32` and `fclink` and, in the copy that `floor32`'s and `ceil32`'s gates read, the folders `sincos32n`
and `exp32a`; none of those is a file the gate reads. Their consoles hold details of the authors' host and are not in
this tree; each is named here by its sha256:

- `sincos32n`, 131 of 131: `a8041676bed7fb4c2ab474be8b437d14a714a6bcfb9d0ee29d9cdca3b71dcf67`
- `exp32a`, 68 of 68: `ac8d9c1e2370c4b96f583b6fbc40d9ec00efa82b92c32bcf79eaafd8b14bafe4`
- `floor32`, 266 of 266: `865df7114b46e709bf0d534cbfb05d23a146674115a73dd56597b50b886934a0`
- `ceil32`, 266 of 266: `bc58977215f134dd6d58cdee69346f25170888d3ff0a7a2a5bcec710ea213b30`

The gates of the last four rows ran with `--recheck` on 2026-11-22 (UTC) on one host, the last of three runs each (a
rehearsal and a recheck before it, listed in `kernel/records/INDEX.md`), each given the owner's own sha256 of its
folder's `FROZEN4.txt` as its anchor, on a copy of `kernel/coq` whose files are this tree's
but for `ANCHORS.md` and the `FROZEN.txt` of `sincos32n`, `exp32a`, `floor32` and `ceil32`; none of those is a file
the gate reads. Their consoles hold details of the authors' host and are not in this tree; each is named here by its
sha256:

- `rti32`, 296 of 296: `162a298f2e3dcf13d38d95f8fae9ec2c1100ba0fc8a65b5a18697f8997cd130c`
- `order32`, 296 of 296: `0188ae9d2ec58f187ec4e16c8f563fc55be338532b2a33d65fdc47caa436fc51`
- `bits32`, 296 of 296: `aaa537712ed9b44562fa0005dd8189cea8b520cd419f5eefcabd71e639bca71e`
- `fclink`, 294 of 294: `3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e`

These eight consoles, the other gate runs of the same eight folders (red runs among them, named as red) and the
folders' sweep records are listed in `kernel/records/INDEX.md` by name and sha256, each with what it shows and what
it does not show; a record that holds no detail of the authors' host is in this tree, under
`kernel/records/<folder>/`, byte for byte as it ran (ruling S280-12 (a) of 2026-11-22).

| Folder | Statement (`MKF.` …) | Statement file | Closing theorem (`MKF.` …) | Gate |
|---|---|---|---|---|
| `f32` | `f32.F32_Statement.F32_REL` | `f32/F32_Statement.v` | `f32.F32.F32_rel` | 20 of 20 |
| `p32` | `p32.P32_Statement.T32`, `SQRT32`, `RSQRT32`, `HYPOT32` | `p32/P32_Statement.v` | `p32.T32.T32_proof`, `p32.Funcs.sqrt32_faithful`, `p32.Funcs.rsqrt32_faithful`, `p32.Hypot.hypot32_faithful` | 35 of 35 |
| `p32r` | `p32r.P32R_Statement.P32R` | `p32r/P32R_Statement.v` | `p32r.Range.p32r` | 41 of 41 |
| `exp32` | `exp32.EXP32_Statement.EXP32` | `exp32/EXP32_Statement.v` | `exp32.Exp32.exp32_faithful` | 47 of 47 |
| `exp32r` | `exp32r.RANGE_Statement.EXP32_RANGE`, `EXP32_SHARP` | `exp32r/RANGE_Statement.v` | `exp32r.Range.exp32_range`, `exp32r.Range.exp32_sharp` | 54 of 54 |
| `ieee64` | `ieee64.IEEE64_Statement.IEEE64` | `ieee64/IEEE64_Statement.v` | `ieee64.Closed.ieee64_holds` | 13 of 13 of its own gate; 148 of 148 of gate4 on a copy |
| `sin32` | `sin32.SIN32_Statement.SIN32_ALL` | `sin32/SIN32_Statement.v` | `sin32.Sin32.sin32_all` | 75 of 75 |
| `cos32` | `cos32.COS32_Statement.COS32_ALL` | `cos32/COS32_Statement.v` | `cos32.Cos32.cos32_all` | 103 of 103 |
| `log32` | `log32.LOG32_Statement.LOG32_ALL` | `log32/LOG32_Statement.v` | `log32.Log32.log32_all` | 73 of 73 |
| `sincos32` | `sincos32.SINCOS32_Statement.SINCOS32_ALL` | `sincos32/SINCOS32_Statement.v` | `sincos32.Sincos32.sincos32_all` | 134 of 134 |
| `compose` | `compose.COMPOSE_Statement.COMPOSE` | `compose/COMPOSE_Statement.v` | `compose.Compose.compose_holds` | 145 of 145 |
| `sincos32i` | `sincos32i.SINCOS32_IEEE_Statement.SINCOS32_IEEE` | `sincos32i/SINCOS32_IEEE_Statement.v` | `sincos32i.Closed.sincos32_ieee_holds` | 290 of 290; harness 8 of 8 |
| `sincos32z` | `sincos32z.SINCOS32_IEEE_Zero_Statement.SINCOS32_IEEE_ZERO` | `sincos32z/SINCOS32_IEEE_Zero_Statement.v` | `sincos32z.Closed.sincos32_ieee_zero_holds` | 288 of 288; harness 8 of 8 |
| `sincos32n` | `sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO` | `sincos32n/SINCOS32_NONZERO_Statement.v` | `sincos32n.Nonzero.sincos32_nonzero` | 131 of 131 |
| `exp32a` | `exp32a.EXP32_ADJ_Statement.EXP32_ADJ` | `exp32a/EXP32_ADJ_Statement.v` | `exp32a.Exp32Adj.exp32_adj` | 68 of 68 |
| `floor32` | `floor32.FLOOR32_Statement.FLOOR32` | `floor32/FLOOR32_Statement.v` | `floor32.Closed.floor32_holds` | 266 of 266 |
| `ceil32` | `ceil32.CEIL32_Statement.CEIL32` | `ceil32/CEIL32_Statement.v` | `ceil32.Closed.ceil32_holds` | 266 of 266 |
| `rti32` | `rti32.RTI32_Statement.RTI32` | `rti32/RTI32_Statement.v` | `rti32.Closed.rti32_holds` | 296 of 296 |
| `order32` | `order32.ORDER32_Statement.ORDER32` | `order32/ORDER32_Statement.v` | `order32.Closed.order32_holds` | 296 of 296 |
| `bits32` | `bits32.BITS32_Statement.BITS32` | `bits32/BITS32_Statement.v` | `bits32.Closed.bits32_holds` | 296 of 296 |
| `fclink` | `fclink.FCLINK_Statement.FCLINK` | `fclink/FCLINK_Statement.v` | `fclink.Closed.fclink_holds` | 294 of 294 |

<details>
<summary>What the gate counts and the harness show, and what they do not</summary>

Each gate compiles its folder and its dependencies, checks the closing theorem's type against the frozen statement,
reads Print Assumptions, rechecks the libraries with coqchk and refuses every plant (a deliberately wrong file) of its
folder. For `sincos32i` and `sincos32z`, 119 and 166 of the counted rows concern files outside the judged theorem's
closure. A refusal shows that the gate rejects a planted file, not that the plant's claim is false; for those two
folders, 45 of 59 plants are refuted by a Coq theorem (`kernel/hardening/plants/PLANT-LABELS.md`). The minimal
harness (`kernel/hardening/harness/harness.py`) executes nothing from the tree but coqc and coqchk and reads one
recursive coqchk summary strictly; it held on these two folders, with the owner's own sha256 of their freeze lists.
For `sincos32n`, `exp32a`, `floor32` and `ceil32`, 108, 45, 237 and 237 of the counted rows concern the folders each
depends on (52, 3, 137 and 137 of them check that a generated file is what its generator emits); none of their
plants is labelled, and the harness has not run on them.
For `rti32`, `order32`, `bits32` and `fclink`, 257 of the counted rows of each gate concern the folders each depends
on (137 of them check that a generated file is what its generator emits); none of their plants is labelled, and the
harness has not run on them.
None of this shows that a statement is the right one, or anything on another host or Coq release.

</details>

## Successors

A statement is never edited. A statement that adds to, narrows or replaces a proved one is a new statement, with a
statement name no other statement file defines, and it lands with its row in this table: the old statement and its
successor, each named as in the proved table above; the relation (adds, narrows or replaces); what the successor
still does not say; and the date. The old statement keeps its row above. `tools/ci/inventory.py` refuses a row here
whose names are not statements of the proved table. The rows below are those of the four statements that add to
`FLOOR32` and `CEIL32`, of `SINCOS32_NONZERO`, which adds to `SINCOS32_ALL`, and of `EXP32_ADJ`, which adds to
`EXP32` and `EXP32_RANGE`; `SINCOS32_IEEE_ZERO` landed as a proved row only, with no row here.

| Old statement | Successor | Relation | What the successor still does not say | Date |
|---|---|---|---|---|
| `floor32.FLOOR32_Statement.FLOOR32` | `rti32.RTI32_Statement.RTI32` | adds | exception flags; signalling NaNs, NaN payloads or a NaN's sign; floor32's results on finite inputs whose value is not in format32; the widening of a binary32 input or the store of the result; a compiler, a processor or a program in any language | 2026-11-22 |
| `ceil32.CEIL32_Statement.CEIL32` | `rti32.RTI32_Statement.RTI32` | adds | exception flags; signalling NaNs, NaN payloads or a NaN's sign; ceil32's results on finite inputs whose value is not in format32; the widening of a binary32 input or the store of the result; a compiler, a processor or a program in any language | 2026-11-22 |
| `floor32.FLOOR32_Statement.FLOOR32` | `order32.ORDER32_Statement.ORDER32` | adds | finite inputs outside format32; anything a NaN carries, so IEEE 754's totalOrder where a NaN is compared; exception flags; the widening of a binary32 input or the store of the result; a compiler, a processor or a program in any language | 2026-11-22 |
| `ceil32.CEIL32_Statement.CEIL32` | `order32.ORDER32_Statement.ORDER32` | adds | finite inputs outside format32; anything a NaN carries, so IEEE 754's totalOrder where a NaN is compared; exception flags; the widening of a binary32 input or the store of the result; a compiler, a processor or a program in any language | 2026-11-22 |
| `floor32.FLOOR32_Statement.FLOOR32` | `bits32.BITS32_Statement.BITS32` | adds | which NaN the program returns for a NaN pattern; that the hardware's widening of a binary32 is widen32 or that its store returns that binary32; exception flags; totalOrder; a compiler, a processor or a program in any language | 2026-11-22 |
| `ceil32.CEIL32_Statement.CEIL32` | `bits32.BITS32_Statement.BITS32` | adds | which NaN the program returns for a NaN pattern; that the hardware's widening of a binary32 is widen32 or that its store returns that binary32; exception flags; totalOrder; a compiler, a processor or a program in any language | 2026-11-22 |
| `floor32.FLOOR32_Statement.FLOOR32` | `fclink.FCLINK_Statement.FCLINK` | adds | that the two strings of KernelText.v are the lines of fclink/sweep_fc2.c (a gate row checks that the generator prints KernelText.v from that program; no Coq term refers to a file); what the printed C text means in C, which is declared, not proved; exception flags; NaN payloads or which NaN a program returns; floor32's results on finite inputs whose value is not in format32; the widening of a binary32 input or the store of the result; anything about a C compiler, a processor or the sweep program around the printed lines | 2026-11-22 |
| `ceil32.CEIL32_Statement.CEIL32` | `fclink.FCLINK_Statement.FCLINK` | adds | that the two strings of KernelText.v are the lines of fclink/sweep_fc2.c (a gate row checks that the generator prints KernelText.v from that program; no Coq term refers to a file); what the printed C text means in C, which is declared, not proved; exception flags; NaN payloads or which NaN a program returns; ceil32's results on finite inputs whose value is not in format32; the widening of a binary32 input or the store of the result; anything about a C compiler, a processor or the sweep program around the printed lines | 2026-11-22 |
| `sincos32.SINCOS32_Statement.SINCOS32_ALL` | `sincos32n.SINCOS32_NONZERO_Statement.SINCOS32_NONZERO` | adds | where sin (2 pi x) or cos (2 pi x) is 0; how far from 0 a result that is not 0 is; anything at the IEEE level, so the shapes of sincos32i and sincos32z, a binary64 datum or the sign of a zero; an input that is not a number of the binary32 format; a program, a compiler, a machine or the floating-point control state | 2026-11-22 |
| `exp32.EXP32_Statement.EXP32` | `exp32a.EXP32_ADJ_Statement.EXP32_ADJ` | adds | binary32 inputs above XNEXT (11629080 / 131072, the binary32 number after XMAX); the graph g_exp32 at XNEXT or above, or what an IEEE implementation returns there, such as an infinity or a flag; by how much exp XNEXT exceeds the finite range; a program, a compiler, a machine or the floating-point control state | 2026-11-22 |
| `exp32r.RANGE_Statement.EXP32_RANGE` | `exp32a.EXP32_ADJ_Statement.EXP32_ADJ` | adds | binary32 inputs above XNEXT (11629080 / 131072, the binary32 number after XMAX); the graph g_exp32 at XNEXT or above, or what an IEEE implementation returns there, such as an infinity or a flag; by how much exp XNEXT exceeds the finite range; a program, a compiler, a machine or the floating-point control state | 2026-11-22 |

## Checking a row yourself

From `kernel/coq`, in the pinned image: compile the folder's sources in import order with `coqc -R . MKF`, then
`coqc -R . MKF <folder>/Identity.v` prints the closing theorem's assumptions, and
`coqchk -silent -o -R . MKF MKF.<folder>.Identity` rechecks it from the compiled files (coqchk shares Coq's kernel code, so this is a second check, not an independent one). The harness does all of this in one
command (see `AGENTS.md`).
