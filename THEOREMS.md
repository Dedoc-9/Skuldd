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

## The law of the turns kernel: stated, NOT PROVEN IN THIS TREE

| Statement | Status | Its theorem, once proved |
|---|---|---|
| `SINCOS32_LAW`: sine and cosine of 2πx on 32-bit patterns, the two conversions, the NaN pattern, the sign of every zero, every intermediate finite and moderate | **stated, not proven in this tree**; withheld from this tree until an independent reviewer has written a blind formalisation of the same convention | `MKF.sincos32law.Closed.sincos32_law_holds`, in `kernel/coq/sincos32law/Closed.v`, typed by `kernel/coq/sincos32law/Identity.v`; it will be the first row below |

## Proved (candidates)

All paths are under `kernel/coq/`. Gate verdicts are those of each folder's gate (`gate/gate4.py`), run in a pinned
container with no network between 2026-11-14 and 2026-11-16, each given its folder's `FROZEN4.txt` sha256 as its anchor. The consoles of `f32`, `p32`, `p32r`, `exp32`, `exp32r` and `ieee64` are in Verðandi's copies of those folders (`verdandi/mathkernel/F32/<folder>/`, from the tree's root); those of the other seven stayed in the authors' workspace.

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

<details>
<summary>What the gate counts and the harness show, and what they do not</summary>

Each gate compiles its folder and its dependencies, checks the closing theorem's type against the frozen statement,
reads Print Assumptions, rechecks the libraries with coqchk and refuses every plant (a deliberately wrong file) of its
folder. For `sincos32i` and `sincos32z`, 119 and 166 of the counted rows concern files outside the judged theorem's
closure. A refusal shows that the gate rejects a planted file, not that the plant's claim is false; for those two
folders, 45 of 59 plants are refuted by a Coq theorem (`kernel/hardening/plants/PLANT-LABELS.md`). The minimal
harness (`kernel/hardening/harness/harness.py`) executes nothing from the tree but coqc and coqchk and reads one
recursive coqchk summary strictly; it held on these two folders, with the owner's own sha256 of their freeze lists.
None of this shows that a statement is the right one, or anything on another host or Coq release.

</details>

## Checking a row yourself

From `kernel/coq`, in the pinned image: compile the folder's sources in import order with `coqc -R . MKF`, then
`coqc -R . MKF <folder>/Identity.v` prints the closing theorem's assumptions, and
`coqchk -silent -o -R . MKF MKF.<folder>.Identity` rechecks it from the compiled files (coqchk shares Coq's kernel code, so this is a second check, not an independent one). The harness does all of this in one
command (see `AGENTS.md`).
