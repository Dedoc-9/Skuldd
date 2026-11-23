<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Skuldd: MathKernel, Ørlǫg and Verðandi in one tree

**Licence:** [AGPL-3.0-only](LICENSE), and a commercial licence on request ([LICENSING.txt](LICENSING.txt)).
**Status:** first release. Nothing here is adopted as final by its owner unless a file says so.
**Theorems:** every proved claim of the kernel is listed in [THEOREMS.md](THEOREMS.md), the kernel-checked examples and plant refutations of `kernel/hardening/` among them; outside the imported documents of `orlog/` and `verdandi/` and the comments inside frozen files, nothing else is claimed as proved.

Three subsystems, built apart, in one tree:

| Part | What it is | Its own brief |
|---|---|---|
| [`kernel/`](kernel) | MathKernel: proofs about binary32 functions computed with binary64 operations, in Coq models of them (no library of them exists yet; see Not done yet); twenty-one statement files, eighteen of which their authors declare were written before their proofs (DECLARED; compose's own header claims no such order, and sincos32i's and sincos32z's say nothing of it), checked in Coq 8.20.1 with Flocq 4.2.1 | this file and [AGENTS.md](AGENTS.md) |
| [`orlog/`](orlog) | Ørlǫg: a prose language whose law bytes are held byte-identical across a reference interpreter and Python, C99 and Rust backends | [orlog/AGENTS.md](orlog/AGENTS.md) |
| [`verdandi/`](verdandi) | Verðandi: the deterministic studio and renderer | [verdandi/AGENTS.md](verdandi/AGENTS.md) |

Verðandi and Ørlǫg may use the kernel; the kernel's proofs and gates use neither, and Ørlǫg is optional (the `corpus` steps of two frozen evidence scripts, `kernel/coq/orl/emit.py` and `emit2.py`, run Ørlǫg's arbiter). Where every file came from:
[PROVENANCE.md](PROVENANCE.md). Why the three belong together: [the paper](docs/paper/SYSTEM-GUARANTEES.md).

## Proved

What Coq accepts, and nothing more. Each statement file below is the claim: read it, not a summary of it. Its
sha256 is held in its folder's `FROZEN4.txt`. Each closing theorem rests on exactly four axioms of Coq's standard
library, as its gate's Print Assumptions row reads: `ClassicalDedekindReals.sig_not_dec`,
`ClassicalDedekindReals.sig_forall_dec`, `FunctionalExtensionality.functional_extensionality_dep` and
`Classical_Prop.classic`.

| Folder | Statement file | Status |
|---|---|---|
| `f32` | [`F32_Statement.v`](kernel/coq/f32/F32_Statement.v) | candidate |
| `p32` | [`P32_Statement.v`](kernel/coq/p32/P32_Statement.v) | candidate |
| `p32r` | [`P32R_Statement.v`](kernel/coq/p32r/P32R_Statement.v) | candidate |
| `exp32` | [`EXP32_Statement.v`](kernel/coq/exp32/EXP32_Statement.v) | candidate |
| `exp32r` | [`RANGE_Statement.v`](kernel/coq/exp32r/RANGE_Statement.v) | candidate |
| `ieee64` | [`IEEE64_Statement.v`](kernel/coq/ieee64/IEEE64_Statement.v) | candidate |
| `sin32` | [`SIN32_Statement.v`](kernel/coq/sin32/SIN32_Statement.v) | candidate |
| `cos32` | [`COS32_Statement.v`](kernel/coq/cos32/COS32_Statement.v) | candidate |
| `log32` | [`LOG32_Statement.v`](kernel/coq/log32/LOG32_Statement.v) | candidate |
| `sincos32` | [`SINCOS32_Statement.v`](kernel/coq/sincos32/SINCOS32_Statement.v) | candidate |
| `compose` | [`COMPOSE_Statement.v`](kernel/coq/compose/COMPOSE_Statement.v) | candidate |
| `sincos32i` | [`SINCOS32_IEEE_Statement.v`](kernel/coq/sincos32i/SINCOS32_IEEE_Statement.v) (`SINCOS32_IEEE`) | candidate |
| `sincos32z` | [`SINCOS32_IEEE_Zero_Statement.v`](kernel/coq/sincos32z/SINCOS32_IEEE_Zero_Statement.v) (`SINCOS32_IEEE_ZERO`) | candidate |
| `sincos32n` | [`SINCOS32_NONZERO_Statement.v`](kernel/coq/sincos32n/SINCOS32_NONZERO_Statement.v) | candidate |
| `exp32a` | [`EXP32_ADJ_Statement.v`](kernel/coq/exp32a/EXP32_ADJ_Statement.v) | candidate |
| `floor32` | [`FLOOR32_Statement.v`](kernel/coq/floor32/FLOOR32_Statement.v) | candidate |
| `ceil32` | [`CEIL32_Statement.v`](kernel/coq/ceil32/CEIL32_Statement.v) | candidate |
| `rti32` | [`RTI32_Statement.v`](kernel/coq/rti32/RTI32_Statement.v) | candidate |
| `order32` | [`ORDER32_Statement.v`](kernel/coq/order32/ORDER32_Statement.v) | candidate |
| `bits32` | [`BITS32_Statement.v`](kernel/coq/bits32/BITS32_Statement.v) | candidate |
| `fclink` | [`FCLINK_Statement.v`](kernel/coq/fclink/FCLINK_Statement.v) | candidate |

Some comments inside frozen files are wrong or stale; frozen bytes never change, so corrections sit in dated notes: for `F32_Statement.v`, `P32_Statement.v` and `EXP32_Statement.v`, those of 2026-11-14 beside Verðandi's byte-identical copies (`verdandi/mathkernel/F32/<folder>/`); for `sincos32i` and `sincos32z`, a dated
note beside the tier: [kernel/notes/CORRECTIONS-2026-11-16.md](kernel/notes/CORRECTIONS-2026-11-16.md); for the eight
folders added later, [kernel/notes/LIMITATIONS.md](kernel/notes/LIMITATIONS.md),
[kernel/notes/FCLINK-TRUSTED-2026-11-22.md](kernel/notes/FCLINK-TRUSTED-2026-11-22.md) section 6 and
[BOUNDARIES.md](BOUNDARIES.md) row B063.

"Candidate" means proved and not adopted: the statements were written, and Coq's checks of the proofs run, by AI
assistants working for the owner. One model outside that family has read the first thirteen statement files, as the
owner reports (G6; its text is not in this tree); no reader
outside the authors' family has read the eight added later (`sincos32n`, `exp32a`, `floor32`, `ceil32`, `rti32`,
`order32`, `bits32`, `fclink`), no human outside the authors has read any, and no reader has confirmed that a
statement says what its owner meant. A proof
shows that the statement follows; it does not show that the statement is the right one.

Where each proof stops (an input class it does not cover, a model it abstracts, a layer it does not reach, or a
trust it rests on), what covers the part beyond and where proof picks up again: the boundary map,
[BOUNDARIES.md](BOUNDARIES.md), one row per stop. A check that CI runs (`tools/ci/check_boundaries.py`) holds every
proved statement to a well-formed row there; it does not show that a row is true.

<details>
<summary>Evidence that the proofs are accepted (MEASURED on one host; what it does not show)</summary>

- The gate of each of the first thirteen folders (`kernel/coq/gate/gate4.py`, run in a pinned container with no
  network) HELD (the consoles of `f32`, `p32`, `p32r`, `exp32`, `exp32r` and `ieee64` are in
  `verdandi/mathkernel/F32/<folder>/`, the rest only in the authors' workspace) on 2026-11-14 to
  2026-11-16: F32 20 of 20, P32 35 of 35, P32R 41 of 41, EXP32 47 of 47, EXP32R 54 of 54, IEEE64 13 of 13 rows of
  its own gate and 148 of 148 of gate4 on a copy, SIN32 75 of 75, COS32 103 of 103, LOG32 73 of 73, SINCOS32 134 of
  134, COMPOSE 145 of 145, SINCOS32_IEEE 290 of 290, SINCOS32_IEEE_ZERO 288 of 288. Of the last two counts, 119 and
  166 rows concern files outside the judged theorem's closure (REPORTED by the standards debate of 2026-11-16). Each
  gate compiles its folder and its dependencies, checks the closing theorem's type against the frozen statement,
  reads Print Assumptions, rechecks the libraries with coqchk and refuses every plant of its folder. A refusal shows
  that the gate rejects the planted file, not that the plant's claim is false: of the 59 plants of `sincos32i` and
  `sincos32z`, 45 are now refuted by a Coq theorem, 4 are possibly true and 10 change no statement
  ([PLANT-LABELS.md](kernel/hardening/plants/PLANT-LABELS.md)). Four of the folders' gates were also run by the
  owner in his own terminal.
- The gates of the four folders added next (`sincos32n`, `exp32a`, `floor32`, `ceil32`) HELD, each with `--recheck`
  on a copy of `kernel/coq` (`THEOREMS.md` says how it differs) and against an anchor equal to the owner's own
  sha256 of its freeze list, on 2026-11-21 and
  2026-11-22 (UTC): SINCOS32_NONZERO 131 of 131, EXP32_ADJ 68 of 68, FLOOR32 266 of 266, CEIL32 266 of 266. Their
  consoles hold details of the authors' host and are not in this tree; `THEOREMS.md` names each by its sha256, and
  `kernel/records/INDEX.md` lists them with the folders' other gate runs, red ones included, and with the floor and
  ceiling sweeps, whose records are in `kernel/records/`. Of those counts, 108, 45, 237 and 237 rows
  concern the folders each one depends on (52, 3, 137 and 137 of them check that a generated file is what its
  generator emits; the rest compile and recheck those folders' sources); the folder's own sources take 6, 6, 10 and
  10 rows, its plants 7, 7, 9 and 9, and 10 rows judge the run as a whole (the freeze list and its anchor, the sources
  judged, a fresh root, the identity's assumptions, the closure, nothing written). The Linux CI has not run them, and
  none of their plants has a label in `PLANT-LABELS.md`.
- The gates of the four folders added last (`rti32`, `order32`, `bits32`, `fclink`) HELD on one host, each in the
  last of three runs (a rehearsal and a recheck before it, all with `--recheck`), that last run on a copy of
  `kernel/coq` (`THEOREMS.md` says how it differs) and against the owner's own sha256 of its freeze list, on 2026-11-22
  (UTC): RTI32 296 of 296, ORDER32 296 of 296, BITS32 296 of 296, FCLINK 294 of 294. Their consoles hold details of
  the authors' host and are not in this tree; `THEOREMS.md` names each by its sha256, and `kernel/records/INDEX.md`
  lists them with each folder's rehearsal and recheck runs. Of those counts, 257 rows of
  each concern the folders each one depends on (137 of them check that a generated file is what its generator emits;
  the rest compile and recheck those folders' sources); the folder's own sources take 12, 8, 14 and 13 rows, its
  plants 17, 21, 15 and 14, and 10 rows judge the run as a whole. The Linux CI has not run them, and none of their
  plants has a label in `PLANT-LABELS.md`.
- The stricter minimal harness (`kernel/hardening/harness/harness.py`: it executes nothing from the tree but coqc and
  coqchk, and reads one recursive coqchk summary strictly) HELD 8 of 8 on `sincos32i` and `sincos32z`, with the
  owner's own sha256 of their freeze lists, both in the workspace and again on this tree's copy of `kernel/coq`
  (2026-11-17); its four canaries (a wrong anchor, a changed byte, an admitted top theorem, an unlisted import) each
  failed at rows their change should reach (ARGUED: the expected rows were not written down before the runs).
- Does not show: anything on another host, compiler or Coq release (the Linux CI's runs of the first thirteen
  folders' gates on GitHub-hosted runners are described in
  [docs/engineering/MATHKERNEL-LINUX-CI.md](docs/engineering/MATHKERNEL-LINUX-CI.md), not here); no folder's gate reads
  coqchk's axiom list
  (each runs `coqchk -norec`, whose axiom list it does not read as a footprint; only the harness reads one, on
  `sincos32i` and `sincos32z`), and the recorded verdicts' anchors of the eleven older folders are freeze-list
  hashes the authors computed, not the owner (since 2026-11-18
  the Linux CI gives every gate an anchor the owner set); Coq's own kernel is trusted (its published list of
  critical bugs is being worked through: see the paper's section on trust).

</details>

<details>
<summary>Measured, not proved: the turns kernel on every binary32 input (MEASURED; what it does not show)</summary>

A C transcription of the turns kernel's law (sine and cosine of 2πx, both conversions on integer bits), shown equal
bit for bit to Coq's evaluation of the law at 2,096 patterns, was run on all 2^32 inputs beside GNU MPFR's correctly
rounded `mpfr_sinu` and `mpfr_cosu`, with ten predictions written before the run, all ten matched:
- not faithfully rounded: 0 of 4,278,190,080 finite inputs, for both functions;
- every zero result of the sine has the input's sign; every zero result of the cosine is +0;
- every infinite or NaN input gives the pattern 0x7FC00000;
- no value computed on a finite input is non-finite, and each is a zero or of magnitude in [2^-400, 2^400).
Result digests: sine 93a4a68e97524b7d7a235f135260ede57f23ab510f00fc10ca85245876d7e694, cosine
8eaa582fa2c0b97566447b9cf0b06f1e189e83825f02d0b990fec9c466adeaf7. The transcription, its consoles and the law
statement itself are withheld from this tree until an independent reviewer has written a blind formalisation of the
same convention, so that the reviewer's version cannot be shaped by this one.
Does not show: a proof; that the transcription equals the law at patterns other than the 2,096 compared (Coq's own evaluation of the law has not been run on every input); another host or compiler; MPFR's own correctness, which is trusted.

</details>

## Not done yet

- The law on 32-bit patterns for the turns kernel: stated, not frozen, not proved in this tree, and withheld from this tree until
  the reviewer's blind formalisation exists.
- No C, Rust or Python library of the kernel exists yet: the printers that would generate them from the proved
  shapes are designed, not built, but for one first printer of two functions' C text. FCLINK proves that Coq's
  printer, `kernel/coq/fclink/CPrint.v`, applied to the shapes of `floor32` and `ceil32` gives the text that
  `kernel/coq/fclink/KernelText.v` quotes from the sweep program `kernel/coq/fclink/sweep_fc2.c` (the gate checks that
  `KernelText.v` is what `kernel/coq/fclink/gen_kernel_text.py` prints from that program; that its strings are the
  lines' bytes is argued from the generator, [BOUNDARIES.md](BOUNDARIES.md) row B067); what that C text means is
  trusted, not proved, and the sweep program is a test, not a library.
- The exhaustive measurements ran on one host only. The gates and feature rows of the first 13 folders, the manifest
  check and the floating-point guard have also run on GitHub-hosted runners (the Linux CI:
  [docs/engineering/MATHKERNEL-LINUX-CI.md](docs/engineering/MATHKERNEL-LINUX-CI.md)); those of the eight folders
  added later have run on one host only; no second Coq release has run them.
- What the kernel's older functions do not state, and other limits: [kernel/notes/LIMITATIONS.md](kernel/notes/LIMITATIONS.md).

## Checking it yourself

Each part's own brief gives its commands. For the kernel, [AGENTS.md](AGENTS.md) gives the harness and the feature
row; [PROVENANCE.md](PROVENANCE.md) gives the manifests to recompute.
