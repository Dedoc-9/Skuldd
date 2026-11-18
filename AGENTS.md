<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# AGENTS.md: Skuldd

A brief for a coding agent working in this tree. Read it first, then the brief of the part you will touch:
`orlog/AGENTS.md` and `verdandi/AGENTS.md` govern inside their folders and are not repeated here.

## What this is

One repository holding three subsystems that were built apart and are meant to strengthen each other:
- `kernel/`: MathKernel, binary32 mathematical functions computed with binary64 operations, whose statements are
  checked in Coq 8.20.1 with Flocq 4.2.1 (`kernel/coq`; ten of the thirteen statement files declare that they were written before their proofs, which this tree does not show, and `compose`'s says it makes no such claim), with the gates, plants and
  canaries that test them (`kernel/coq/gate`, `kernel/hardening`). `kernel/evidence/` is withheld with the law draft; the exhaustive sweeps of kernel functions in this tree are Verðandi's records for sqrt32, rsqrt32 and exp32 (narrow was swept at five binary64 values per finite binary32 number, except the values of magnitude at or above the largest binary32 number), under `verdandi/mathkernel/F32/orl/`.
- `orlog/`: Ørlǫg, a prose language: a program is a numbered legal text whose law bytes are held byte-identical
  across a reference interpreter and Python, C99 and Rust backends.
- `verdandi/`: Verðandi, the deterministic studio and renderer over a frozen oracle.

The direction of use is one way: Verðandi and Ørlǫg may use the kernel; the kernel's proofs and gates use neither. Ørlǫg is optional, except for the corpus mode of the emitters (`kernel/coq/orl/emit.py` and `emit2.py`, and the five emitters in `verdandi/mathkernel/F32/orl/`), which runs Ørlǫg's arbiter (`orl.py`); apart from that,
nothing in `kernel/` or `verdandi/` needs it.

## Rules that hold everywhere

- **No claim beyond what is proven.** A section of a document headed as proof states only what a kernel-checked
  theorem states, and names the theorem and its file. Measured, argued and reported results go in separate evidence
  sections, each with its grade (MEASURED, READ, ARGUED, REPORTED, NOT_MEASURED) and what it does not show. Long
  evidence goes in a collapsed `<details>` section, with a blank line after `</summary>`.
- **Frozen files are never edited.** A file named in a freeze list (`kernel/coq/<folder>/FROZEN4.txt`) or a statement
  file keeps its bytes. A correction is a new file or a dated note beside the old one.
- **Records are never overwritten.** A rerun gets a new run name and new files; consoles stay byte for byte (see
  `.gitattributes`: evidence is stored without line-ending conversion).
- **Every check is seen to fail.** A new row, gate or harness comes with a plant or canary that makes it fail, run
  before its result is believed. A plant that changes nothing is an equivalent mutant and is said to be one.
- **Determinism is specified, not assumed.** Floating point is allowed where its behaviour is specified: binary64,
  round to nearest even, no contraction (`-ffp-contract=off`), no fast-math, never x87; conversions to and from
  binary32 on integer bits.
- **Standard library only.** Python is run as `python -B` with `PYTHONHASHSEED=0` and `PYTHONUTF8=1`; C is C99; Rust
  is std-only. Adding a dependency, downloading or installing anything needs the owner's word.
- **Containers run with `--rm --network none`**, inputs mounted read-only, one container at a time.
- **Nothing personal, nothing branded.** No local path, account name, host name or hardware name enters a file you
  write; no game-engine brand in public-facing text (say "future engine integration"). Scan before proposing a
  change.

## The kernel's checks

The Linux CI (`.github/workflows/`, described in `docs/engineering/MATHKERNEL-LINUX-CI.md`) runs the feature rows and
the folder gates in a second image, built from `ci/mathkernel/Dockerfile`. It is not pinned: its base tag and opam
repositories are read at each build, and each build records what it got. Its runs are graded apart from the records
below, which were all made in the first image.

All run in a container image with Coq 8.20.1 and Flocq 4.2.1 (its recipe is not in this tree and no file under `kernel/` names it; the harness consoles print the sha256 of the coqc and coqchk they ran), with `kernel/coq` mounted read-only, except for the folder gate, which writes `<folder>/out4/` and `libcache/` inside the tree it judges and so needs it mounted writable:
- the feature row: `python3 -B kernel/hardening/features/feature_row3.py <coq-root> --list <coq-root>/<folder>/FROZEN4.txt`
  (refuses recursive definitions, checking-flag changes and the Coq features behind the upstream critical-bugs list
  that the tier does not use; earlier versions are kept beside it with their runs);
- the minimal harness, for a folder with a `Closed.v` (only `ieee64`, `sincos32i` and `sincos32z` have one; version 1 held on `sincos32i` and `sincos32z`, this version on `sincos32z`): `python3 -B kernel/hardening/harness/harness2.py --src <coq-root> --list <folder>/FROZEN4.txt
  --anchor <the owner's sha256 of that list> --statement <Module.NAME> --theorem <Module.name> --axioms
  gate/expected-pa-flocq4.txt`: eight rows, among them a fresh root, compilation in import order, the harness's own
  check file and one recursive coqchk with its summary read strictly;
- the folder gate: `kernel/coq/gate/gate4.py` (it writes only `<folder>/out4/` and `libcache/`).
The owner computes every statement's and every freeze list's sha256 himself; a check is given his value, never one
read from the tree.

## Inside Skuldd: commands written for a repository of their own

Git's top level here is this folder, one above `orlog/` and `verdandi/`, and this history starts at the import: the
histories of Ørlǫg and Verðandi stay in their own repositories (`PROVENANCE.md` names them and the commits
imported). Three rules of git decide what a command sees here:
- `REV:path` is read from the root of the revision's tree. From this folder write `HEAD:orlog/src/...`; from
  `orlog/` or `verdandi/`, `HEAD:./src/...` reads the folder you stand in.
- `HEAD^{tree}` is the whole tree. One part's tree is `git rev-parse HEAD:orlog`, `HEAD:verdandi` or `HEAD:kernel`.
- `status`, `ls-tree` and `archive` take their paths from the working folder, and `git worktree add` checks out the
  whole tree.

Every mode that reads Ørlǫg's or Verðandi's history runs in that repository's own checkout: `tests/corpus_seals.py`
with a revision, `tests/compat.py history` and `freeze`, the reproducers pinned to a commit, `tools/rung.py`, and
looking up a commit that a record names. The tables below say what each command found on the import does here and
what to do instead. Each was run on the import (2026-11-17) unless its line says read; "stops" means a traceback or
exit 128.

In `orlog/`:

| Command | Here | Instead |
|---|---|---|
| `tests/corpus_seals.py REV` | stops: with an Ørlǫg revision at once, since this history does not hold it; with a Skuldd revision after printing "13 of 13", at its `git show HEAD:src/orlog/canon.py` | Ørlǫg's own checkout |
| `tests/compat.py history` | stops before computing anything | Ørlǫg's own checkout |
| `tests/compat.py freeze` (the owner's act) | read, not run: it would stop at its first corpus file, and could see only the imported versions | Ørlǫg's own checkout |
| the reproducers pinned to commit 2e9805a: `research/law-sufficiency/run_all.py`, `run_all_1.py` and six generators in `research/rust-core/` | refuse unless HEAD is that commit, which this history does not hold (one run, seven read) | Ørlǫg's own checkout at 2e9805a |
| `research/reporting-pass/reproducers/run_all.py` | names a Skuldd commit as Ørlǫg's tree, and its dirty flag reads the whole tree | Ørlǫg's own checkout |
| `research/stepwalk/compare.py` | prints Skuldd's commit as both the Ørlǫg and the Verðandi HEAD | the commits imported are in `PROVENANCE.md` |
| `research/run-1/twin-r7/ar_compute.py` and the other commands written relative to the working folder | run only from `orlog/` | change to `orlog/` first |
| the commits that evidence headers, `AGENTS.md` and `README.md` name, and the gate record in commit 9de2792's message | not in this history | Ørlǫg's own repository |
| `docs/engineering/release/PR-VERIFICATION-DISCIPLINE.md`'s `HEAD^{tree}` (its item 1) and `git rev-parse <commit>:<path>` (its item 5) | the first is the whole tree; the second fails for a path given from Ørlǫg's root | `git rev-parse HEAD:orlog`; for a file, `<commit>:orlog/<path>` |

In `verdandi/`:

| Command | Here | Instead |
|---|---|---|
| `tools/rung.py classify`, `plants` and `selftest` | Skuldd's copy refuses with one line unless the folder it is given is Verðandi's root at git's top level (`CHANGES-AFTER-IMPORT.md`). Without that guard, `plants` printed PLANTS HELD over no rows, `classify` from this folder graded against a one-file trusted base and from `verdandi/` stopped, and `selftest` read 20 of 21 | Verðandi's own checkout, as `verdandi/AGENTS.md` says |
| the brief's `git show origin/main:tools/rung.py` (in `AGENTS.md`, `docs/ROADMAP.md` and `art/director/inverse/0254-spec.md`) | stops, from either folder | Verðandi's own checkout: the classifier is the copy Verðandi's pushed tree holds |
| the landing check in `AGENTS.md` (the commit's Gated-Tree against `HEAD^{tree}`) | compares with the whole tree | the tree Verðandi's gate reads is `git rev-parse HEAD:verdandi`. Never run the check's recovery step, `git reset --hard origin/main`, here: it would move all three parts (read, not run) |
| `mathkernel/F32/RUN.md`'s `git status --porcelain mathkernel/F32` | from this folder it names no file, so it cannot fail (run on a model of this layout) | run it from `verdandi/` |
| `mathkernel/F32/RUN.md`'s `git archive` and `p1-oracle/evidence/README.md`'s `git show HEAD:...` | stop from this folder; the second also from `verdandi/` | from `verdandi/`; there, write `HEAD:./PATH` |
| the commits that records name, among them 29352e51, 7dee210, e759213 and 868b644 | not in this history | Verðandi's own repository |
| the record paths of `shell/win32.rs` and the defaults of `verify/seal_walk.py` and `verify/seal_sessionwalk.py` | relative to the working folder (read) | run from `verdandi/` |

In `kernel/` and this folder:

| Command | Here | Instead |
|---|---|---|
| `kernel/hardening/features/run_row2.sh` and `run_row3.sh` | written for the workspace in which their records, `runs2/row2-console.txt` and `runs3/row3-console.txt`, were made; here every input is missing and they do not refuse (`run_row2.sh` prints "same verdict: 0; different: 0") | do not run them here; the feature row is run as "The kernel's checks" says |
| `kernel/hardening/plants/gen_refute.py` and `gen_refute2.py` | stop: they read the workspace's `mkf-ext/` | none in this tree |
| `kernel/hardening/examples/build_examples.sh` | read, not run: it copies `Examples2.v`, which the import names `Examples.v` | none in this tree |
| `kernel/hardening/plants/build_refute.sh` | read, not run: it needs a prebuilt closure (`/pre`) that nothing in the tree builds | none in this tree |
| `tools/assemble.py` | read, not run: it built the import from the workspace and the two repositories, and needs them to run again | to check the import, the manifests and `PROVENANCE.md` are enough |

## Working here

- Changes reach the main branch through a pull request the owner merges. No outside contribution is accepted until
  the owner sets contribution terms (`LICENSING.txt`).
- One phase per session; record what was built, what ran and how each result is graded.
- Every closing theorem of the kernel's folders is listed in `THEOREMS.md` with its statement file and its gate verdict. Other results checked by Coq in `kernel/hardening/` (the 45 plant refutations of `plants/PLANT-LABELS.md`, the examples of `examples/` and `big106/`, the narrowing probe of `r7-probes/`) are stated in their own files; `THEOREMS.md` names them and marks them as not candidates.
- Changes after the import are listed in `CHANGES-AFTER-IMPORT.md`; the manifests describe the import.
- Licensing: `LICENSE` (AGPL-3.0-only), `LICENSING.txt` (the dual offer), `THIRD-PARTY.md`, `PROVENANCE.md`.
