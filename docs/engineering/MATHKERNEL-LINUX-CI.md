<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# MathKernel on Linux: what the workflows run, how they are anchored, and what a green run shows

Status when this file was written (2026-11-17): the workflows were in the tree and **had not run on GitHub**; their
grade was NOT MEASURED (`docs/GUARANTEES-LEDGER.md` §4). A run is cited by its id and commit, not by this file; the
first runs are below, under "The first runs".

## What runs

`.github/workflows/integrity.yml`, on every push and pull request, whatever it touches, and by hand (a manual run is
offered only once a workflow is on the default branch):

1. **integrity** (no Coq, no container): `tools/check_manifests.py` reconciles the import's four manifests with the
   tree and with `CHANGES-AFTER-IMPORT.md`, plants included (it judges every file, so it has no paths filter); then
   `feature_row3.py` on each of the 13 freeze lists.

`.github/workflows/mathkernel-linux.yml`, on pushes and pull requests that touch `kernel/`, `ci/mathkernel/` or the
workflow itself, and by hand:

2. **fpenv** (no Coq): `kernel/runtime/check_fpenv.py` with GCC and clang (the runner's `clang`, or its newest
   `clang-NN` when there is no unversioned one; the job prints which), the floating-point state guard's gate, on two
   runners, `ubuntu-24.04` (x86-64) and `ubuntu-24.04-arm` (arm64). GitHub offers the arm64 runner to public
   repositories; where it is not offered, that job waits for a runner and does not start, and its result stays NOT
   MEASURED.
3. **image**: builds `ci/mathkernel/Dockerfile` (Ubuntu 24.04; OCaml 4.14.2 and Coq 8.20.1 from opam's default
   repository, Flocq 4.2.1 from the Rocq/Coq released repository, which is where `coq-flocq` is published) and keeps
   it in GitHub's Actions cache, keyed by a version (`v2`) and the Dockerfile's hash, with the base image's digest read
   from the build's output beside it, so that every run prints it. A cache entry is scoped to its branch or pull request
   (a run can also read the default branch's) and is evicted after 7 days without use, so the image is built once per
   Dockerfile and cache scope, and again after an eviction. The base image's tag and both opam repositories are read
   as they stand at each build, so two builds can differ; each build records its own: the base image's digest, the
   image's id, the whole opam switch (exported into the image), the repositories, and the sha256 of `coqc`, `coqchk`
   and `python3`. Before the image is kept, it must load Flocq and Coq's reals. A build needs several outside hosts
   (opam's two repositories and the package sources); one that cannot be reached fails the image job and, through it,
   every gate job. The image is not the one behind `THEOREMS.md`'s verdicts, which were made in a Debian image whose
   recipe is not in this tree.
4. **gate**: thirteen jobs, one per folder (`f32`, `p32`, `p32r`, `exp32`, `exp32r`, `ieee64`, `sin32`, `cos32`,
   `sincos32`, `log32`, `sincos32i`, `sincos32z`, `compose`), independent of one another (`fail-fast: false`). Each
   checks its anchor variable, loads the image and prints its id (the same id in every job means the same build), runs
   the feature row on its freeze list with the tree mounted read-only, then `python3 -B gate/gate4.py <folder>
   --recheck` in a container with `--network none` and `kernel/coq` as its tree, with `ANCHOR` set from the job's
   repository variable. The job fails unless the gate's output shows the row `freeze list is the anchored one` passing
   with that anchor.

The proof sources, statements, freeze lists and gates are not changed by any of this.

## The thirteen anchors (the owner's act, after a first run without them shows each gate job refuses)

The anchor is what binds a gate to the owner's record of a folder: the gate compares the sha256 of
`<folder>/FROZEN4.txt` with the anchor it is given, so a change that rewrites both a folder's sources and its freeze
list fails. The anchor must therefore come from outside the checkout the job judges. Each job refuses to start its gate
when its variable is missing or is not exactly 64 lower-case hex digits; nothing in the workflow computes an anchor.

In the repository's Settings, under Secrets and variables, Actions, Variables, set one variable per folder, named
`MK_ANCHOR_<FOLDER>` in capitals (`MK_ANCHOR_F32`, `MK_ANCHOR_P32`, `MK_ANCHOR_P32R`, `MK_ANCHOR_EXP32`,
`MK_ANCHOR_EXP32R`, `MK_ANCHOR_IEEE64`, `MK_ANCHOR_SIN32`, `MK_ANCHOR_COS32`, `MK_ANCHOR_SINCOS32`, `MK_ANCHOR_LOG32`,
`MK_ANCHOR_SINCOS32I`, `MK_ANCHOR_SINCOS32Z`, `MK_ANCHOR_COMPOSE`), each holding the owner's own sha256 of that
folder's `kernel/coq/<folder>/FROZEN4.txt`, in lower case, computed by the owner from a copy the owner holds, for
example in PowerShell from that copy's root:

    (Get-FileHash kernel\coq\f32\FROZEN4.txt -Algorithm SHA256).Hash.ToLower()

or with `sha256sum kernel/coq/f32/FROZEN4.txt`. For `sincos32i` and `sincos32z` the owner recorded anchors before the
import (`PROVENANCE.md` names them, abbreviated); those variables must equal the recorded values. A variable, once set,
is what later commits are judged against until the owner changes it.

The binding holds only while the code that applies it is the reviewed code: the workflow file and
`kernel/coq/gate/gate4.py` are taken from the commit being judged, so a change that also edits either of them can
weaken the check. A change to `.github/workflows/` or `kernel/coq/gate/` is read before its green run counts.

## What a green run shows, and what it does not

A green `gate` job shows that its folder's gate held on a GitHub-hosted Ubuntu 24.04 runner, with Coq and Flocq built
from opam, against the owner's anchor, provided the workflow file and `gate/gate4.py` at that commit are the reviewed
ones: a second machine, a second operating system on that machine, and a second build of the tools, beside the first
host's records. It is MEASURED evidence of that run.

A green run is read by a person. As they stand, these jobs are not fit to be required status checks: a pull request
that touches none of `mathkernel-linux.yml`'s paths never starts it, so its checks would stay pending; and when the
image job fails, the gate jobs are skipped, which GitHub reports as success. Requiring them needs an always-running
summary job first.

It does not show: a proof of anything beyond what the statements already prove; that the runner, GitHub Actions,
opam, OCaml, Coq, Flocq or the processor are correct; that any compiled program executes the modelled operations;
bit identity across architectures or compilers; anything about intermediate IEEE operations, signed zeros, NaN
payloads, exception flags or inputs outside the statements' premises; Ørlǫg's or Verðandi's own checks.

## Rehearsed locally

Before the workflows were proposed, some of their commands were run on the published tree (main d7732b0d) on one
x86-64 Windows host, 2026-11-17: `tools/check_manifests.py`; `feature_row3.py` and each folder's `gate4.py`, one
folder at a time on a copy of `kernel/`, `--network none`, in a Debian image with Coq 8.20.1 and Flocq 4.2.1 from
Debian's packages; and `check_fpenv.py` with clang only. Not run there: the image's build (docker and opam), anything
with GCC, anything on Linux outside a container, anything on arm64. Twelve folders ran without an anchor, so each gate
counts one row fewer than `THEOREMS.md`, whose counts are anchored runs (the row comparing the anchor is counted only
when an anchor is given); `sincos32z` ran with the owner's anchor.

| Folder | Feature row, then gate | Folder | Feature row, then gate |
|---|---|---|---|
| f32 | HELD, 19 of 19 | sin32 | HELD, 74 of 74 |
| p32 | HELD, 34 of 34 | cos32 | HELD, 102 of 102 |
| p32r | HELD, 40 of 40 | sincos32 | HELD, 133 of 133 |
| exp32 | HELD, 46 of 46 | log32 | HELD, 72 of 72 |
| exp32r | HELD, 53 of 53 | sincos32i | HELD, 289 of 289 |
| ieee64 | HELD, 147 of 147 | sincos32z | HELD, 288 of 288 (anchored) |
| compose | HELD, 144 of 144 | | |

On the same host, on the tree as proposed: `tools/check_manifests.py`, MANIFESTS RECONCILED 8 of 8 rows;
`kernel/runtime/check_fpenv.py` with clang 22.1.8, FPENV CHECK HELD 13 of 13 rows. A rehearsal on one host is not a
run on GitHub: another image, another build of Coq and Flocq, another machine.

## The first runs (2026-11-18 UTC)

On commit 01c174bda7ff2a2771ea3a412f8eda1806870dbe, the head of pull request #1 (the pull request's runs checked out
GitHub's merge commit 6c362ac6, whose tree c69f62bd is the same; read through GitHub's API). MEASURED, read from the
jobs' logs:

- Integrity, runs 44211905905 (pull request) and 44211854876 (push): MANIFESTS RECONCILED 8 of 8 rows; the feature
  row held on all 13 freeze lists.
- MathKernel on Linux, runs 44211905832 (pull request) and 44211854754 (push). First attempt of each: both `fpenv`
  jobs and the image green; all 13 gate jobs refused at their first step with the missing-anchor line (exit 2).
  The anchor variables were set 13 to 48 seconds after these runs were created, and the gate jobs, starting 7 to 9
  minutes later, still saw none, so an attempt appears to read the variables when it is created (ARGUED; GitHub
  does not document it). Second attempt of each (a re-run of the failed jobs, which saw the variables): all 13 gates
  held, each printing its anchor and passing the anchored row, with `THEOREMS.md`'s counts: f32 20, p32 35, p32r 41,
  exp32 47, exp32r 54, ieee64 148, sin32 75, cos32 103, sincos32 134, log32 73, sincos32i 290, sincos32z 288,
  compose 145.
- `fpenv`: x86-64 with GCC 13.3.0 and clang 18.1.3, 26 of 26 rows; arm64, 21 of 21. GCC refused the ISO C99
  contraction build at compile time; clang's was reported by the run-time canary.
- The image was built twice, once per cache scope (ids 6c7f6ead... and 383301de...), from the same base
  (`ubuntu:24.04@sha256:73b999393d07f2bf65a40373778a44dc9a6d54ad7718d29247d8ff9413c4d6a8`, read from the build
  output; the job's own `base image:` line printed nothing, the inspected image not being in Docker's local store).
  Nothing else the two builds printed differs: the switch export (9016502d...), `coqc`, `coqchk` and `python3`
  (966d4693..., 72a15917..., e50d468e...), and the opam and apt package lists. Their ids differ, so some bytes of the
  two images do. Coq 8.20.1, Flocq 4.2.1, OCaml 4.14.2; the Flocq smoke test passed.

The jobs ran on GitHub-hosted runners, one per job, with GitHub's runner images (x86-64 20261111.370.1 and
20261111.127.1, arm64 20261111.182.1). What a green run shows and does not show is the section "What a green run
shows, and what it does not".

## What to keep from each run

The commit, the run's id, the image job's printed digest, id, switch and hashes, each gate job's image id, and from
each gate its anchored row (`freeze list is the anchored one ... ok ANCHOR <16 digits>`) and last line
(`<FOLDER> GATE4 HELD: n of n [anchor ...]`, n equal to `THEOREMS.md`'s anchored count). GitHub keeps the logs for a
limited time; a run that is to be cited is saved with them.
