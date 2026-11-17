<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# MathKernel on Linux: what the workflow runs, how it is anchored, and what a green run shows

Status: the workflow is in the tree; **it has not run on GitHub**. Until it has, its grade is NOT MEASURED
(`docs/GUARANTEES-LEDGER.md` §4).

## What runs

`.github/workflows/mathkernel-linux.yml`, on pushes and pull requests that touch `kernel/`, `ci/mathkernel/`, the
manifests, `PROVENANCE.md`, `CHANGES-AFTER-IMPORT.md`, `tools/check_manifests.py` or the workflow itself, and by hand:

1. **integrity** (no Coq): `tools/check_manifests.py` reconciles the import's four manifests with the tree and with
   `CHANGES-AFTER-IMPORT.md`, plants included; then `feature_row3.py` on each of the 13 freeze lists.
2. **fpenv** (no Coq): `kernel/runtime/check_fpenv.py --cc gcc --cc clang`, the floating-point state guard's gate, on
   two runners, `ubuntu-24.04` (x86-64) and `ubuntu-24.04-arm` (arm64). GitHub offers the arm64 runner to public
   repositories; where it is not offered, that job waits for a runner and does not start, and its result stays
   NOT MEASURED.
3. **image**: builds `ci/mathkernel/Dockerfile` (Ubuntu 24.04; OCaml 4.14.2 and Coq 8.20.1 from opam's default
   repository, Flocq 4.2.1 from the Rocq/Coq released repository, which is where `coq-flocq` is published) once per
   Dockerfile, keeps it in GitHub's Actions cache, and prints the versions and the sha256 of `coqc`, `coqchk` and
   `python3`. The image has not been built anywhere yet: its first build is the workflow's first run.
4. **gate**: thirteen jobs, one per folder (`f32`, `p32`, `p32r`, `exp32`, `exp32r`, `ieee64`, `sin32`, `cos32`,
   `sincos32`, `log32`, `sincos32i`, `sincos32z`, `compose`), independent of one another (`fail-fast: false`). Each
   loads the image, runs the feature row on its freeze list, then `python3 -B gate/gate4.py <folder> --recheck` in a
   container with `--network none` and `kernel/coq` as its tree, with `ANCHOR` set from the job's repository variable.

The proof sources, statements, freeze lists and gates are not changed by any of this.

## The thirteen anchors (the owner's act, before the first run)

The anchor is what makes a gate hold against someone who rewrites both a folder's sources and its freeze list: the
gate compares the sha256 of `<folder>/FROZEN4.txt` with the anchor it is given. So the anchor must come from outside
the checkout the job judges. Each job refuses to start its gate when its variable is missing or is not 64 lower-case
hex digits; nothing in the workflow computes an anchor.

In the repository's Settings, under Secrets and variables, Actions, Variables, set one variable per folder, named
`MK_ANCHOR_<FOLDER>` in capitals (`MK_ANCHOR_F32`, `MK_ANCHOR_P32`, `MK_ANCHOR_P32R`, `MK_ANCHOR_EXP32`,
`MK_ANCHOR_EXP32R`, `MK_ANCHOR_IEEE64`, `MK_ANCHOR_SIN32`, `MK_ANCHOR_COS32`, `MK_ANCHOR_SINCOS32`, `MK_ANCHOR_LOG32`,
`MK_ANCHOR_SINCOS32I`, `MK_ANCHOR_SINCOS32Z`, `MK_ANCHOR_COMPOSE`), each holding the owner's own sha256 of that
folder's `kernel/coq/<folder>/FROZEN4.txt`, in lower case, computed by the owner from a copy the owner holds, for
example in PowerShell from that copy's root:

    (Get-FileHash kernel\coq\f32\FROZEN4.txt -Algorithm SHA256).Hash.ToLower()

or with `sha256sum kernel/coq/f32/FROZEN4.txt`. For `sincos32i` and `sincos32z` the owner recorded anchors before the
import (`THEOREMS.md` cites them); those variables must equal the recorded values. A variable, once set, is what later
commits are judged against: a change that rewrites both a folder's sources and its freeze list fails until the owner
changes the variable.

## What a green run shows, and what it does not

A green `gate` job shows that its folder's gate held on a GitHub-hosted Ubuntu 24.04 runner, with Coq and Flocq built
from opam, against the owner's anchor: a second machine, a second operating system on that machine, and a second build
of the tools, beside the first host's records. It is MEASURED evidence of that run.

It does not show: a proof of anything beyond what the statements already prove; that the runner, GitHub Actions,
opam, OCaml, Coq, Flocq or the processor are correct; that any compiled program executes the modelled operations;
bit identity across architectures or compilers; anything about intermediate IEEE operations, signed zeros, NaN
payloads, exception flags or inputs outside the statements' premises; Ørlǫg's or Verðandi's own checks.

## Rehearsed locally

Before the workflow was proposed, its commands were run on the published tree (main d7732b0d) on one x86-64 Windows
host, 2026-11-17. The gates ran one folder at a time on a copy of `kernel/`, `--network none`, in a Debian image with
Coq 8.20.1 and Flocq 4.2.1 from Debian's packages (not the workflow's image, which has not been built). Twelve
folders ran without an anchor, so each gate counts one row fewer than `THEOREMS.md`, whose counts are anchored runs
(the row comparing the anchor is counted only when an anchor is given); `sincos32z` ran with the owner's anchor.

| Folder | Feature row, then gate | Folder | Feature row, then gate |
|---|---|---|---|
| f32 | HELD, 19 of 19 | sin32 | HELD, 74 of 74 |
| p32 | HELD, 34 of 34 | cos32 | HELD, 102 of 102 |
| p32r | HELD, 40 of 40 | sincos32 | HELD, 133 of 133 |
| exp32 | HELD, 46 of 46 | log32 | HELD, 72 of 72 |
| exp32r | HELD, 53 of 53 | sincos32i | HELD, 289 of 289 |
| ieee64 | HELD, 147 of 147 | sincos32z | HELD, 288 of 288 (anchored) |
| compose | HELD, 144 of 144 | | |

On the same host: `tools/check_manifests.py` on the published tree, MANIFESTS RECONCILED 6 of 6 rows;
`kernel/runtime/check_fpenv.py` with clang 22.1.8, FPENV CHECK HELD 12 of 12 rows. A rehearsal on one host is not a run
on GitHub: another image, another build of Coq and Flocq, another machine.

## What to keep from each run

The commit, the run's id, the image job's printed versions and hashes, and each gate's last line (`<FOLDER> GATE4
HELD: n of n [anchor ...]`). GitHub keeps the logs for a limited time; a run that is to be cited is saved with them.
