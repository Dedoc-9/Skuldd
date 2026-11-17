<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# AGENTS.md: Skuldd

A brief for a coding agent working in this tree. Read it first, then the brief of the part you will touch:
`orlog/AGENTS.md` and `verdandi/AGENTS.md` govern inside their folders and are not repeated here.

## What this is

One repository holding three subsystems that were built apart and are meant to strengthen each other:
- `kernel/`: MathKernel, binary32 mathematical functions computed with binary64 operations, whose statements are
  written before their proofs and checked in Coq 8.20.1 with Flocq 4.2.1 (`kernel/coq`), with the gates, plants and
  exhaustive measurements that hold them (`kernel/hardening`, `kernel/evidence`).
- `orlog/`: Ørlǫg, a prose language: a program is a numbered legal text whose law bytes are held byte-identical
  across a reference interpreter and Python, C99 and Rust backends.
- `verdandi/`: Verðandi, the deterministic studio and renderer over a frozen oracle.

The direction of use is one way: Verðandi and Ørlǫg may use the kernel; the kernel uses neither. Ørlǫg is optional:
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

All run in the pinned Coq image (Coq 8.20.1, Flocq 4.2.1), with `kernel/coq` mounted read-only:
- the feature row: `python3 -B kernel/hardening/features/feature_row3.py <coq-root> --list <coq-root>/<folder>/FROZEN4.txt`
  (refuses recursive definitions, checking-flag changes and the Coq features behind the upstream critical-bugs list
  that the tier does not use; earlier versions are kept beside it with their runs);
- the minimal harness: `python3 -B kernel/hardening/harness/harness2.py --src <coq-root> --list <folder>/FROZEN4.txt
  --anchor <the owner's sha256 of that list> --statement <Module.NAME> --theorem <Module.name> --axioms
  gate/expected-pa-flocq4.txt`: eight rows, among them a fresh root, compilation in import order, the harness's own
  check file and one recursive coqchk with its summary read strictly;
- the folder gate: `kernel/coq/gate/gate4.py` (it writes only `<folder>/out4/` and `libcache/`).
The owner computes every statement's and every freeze list's sha256 himself; a check is given his value, never one
read from the tree.

## Working here

- Changes reach the main branch through a pull request the owner merges. No outside contribution is accepted until
  the owner sets contribution terms (`LICENSING.txt`).
- One phase per session; record what was built, what ran and how each result is graded.
- Every proved theorem is listed in `THEOREMS.md` with its statement file, its closing theorem and its evidence; a
  theorem that is not listed there is not claimed anywhere.
- Changes after the import are listed in `CHANGES-AFTER-IMPORT.md`; the manifests describe the import.
- Licensing: `LICENSE` (AGPL-3.0-only), `LICENSING.txt` (the dual offer), `THIRD-PARTY.md`, `PROVENANCE.md`.
