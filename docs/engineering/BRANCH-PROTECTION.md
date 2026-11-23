<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Branch protection: the settings the owner applies

Nothing in this tree can apply these settings. They are the owner's, in the repository's settings on GitHub, and until
they are set a red check informs and does not block. This page says which setting closes which gap, and what each
costs in a repository with one maintainer. GitHub renames and moves its settings from time to time: the names below
are the ones known when this page was written (2026-11-18). Those in quotation marks under "Actions settings" and the
behaviour of merge queues, skipped runs and pushed tags were read in GitHub's documentation by a review of this page;
the others were not read from GitHub's site for it.

## The checks to require

Require exactly these two checks, by these names:

- `MathKernel verdict`, the last job of `.github/workflows/mathkernel-linux.yml`. It runs after every other job of
  that workflow, also when one failed, and fails unless all of them succeeded and every gated folder's run record
  holds (`docs/engineering/MATHKERNEL-LINUX-CI.md`).
- `Integrity (no Coq)`, the job of `.github/workflows/integrity.yml`: no tracked compiled Python, the manifests, the
  inventory, the CI judge against `MK_ANCHOR_CI`, the boundary map (`tools/ci/check_boundaries.py`), feature rows 3
  and 4 on every freeze list, the tests of `tools/ci`, and the same tests and feature rows again under the read audit
  (`tools/ci/read_audit.py`).

A third workflow, `.github/workflows/drift.yml` (the drift of the copies `orlog/` and `verdandi/` from their
originals, rulings SY-1 and SY-2), is a report and is not one of these checks: it turns red also when an original's
main has moved since its pin, until a re-pin, and the MathKernel verdict does not read it. Where this page says "both
workflows", it means `mathkernel-linux.yml` and `integrity.yml`.

Do not require the `Gate <folder>` jobs one by one. Their set is the inventory's and grows with it, and a required check
that never reports blocks every merge; the verdict job already fails unless each of them succeeded. Both workflows run
on every push and pull request, whatever it touches, so a required check is never left pending for want of a path.
GitHub starts no run for a push or pull request whose head commit message holds `[skip ci]`, `[ci skip]`, `[no ci]`,
`[skip actions]` or `[actions skip]`, or that ends with the trailer `skip-checks: true` (or `skip-checks:true`) after
two blank lines, nor for a pull request with a merge conflict: a required check then stays
pending and blocks the merge, and such a commit has no run. A pushed tag starts both workflows on the tagged commit (a
push of more than three tags at once starts none). The run is judged against the current `MK_ANCHOR_CI`, so a tag on
a commit made before the last change to the CI judge runs red.

A push to a branch with an open pull request starts two runs of each workflow, one on the head commit and one on
GitHub's merge commit, and both report these names on the head commit; with the branch up to date with `main` they
judge the same tree. The verdict job also waits for the fpenv job's arm64 leg (`ubuntu-24.04-arm`): where GitHub does
not offer that runner, the verdict does not report while that leg waits, and a required verdict blocks every merge.

## The rule for `main`

A branch protection rule, or a ruleset, that targets `main`:

1. Require a pull request before merging, with 0 required approvals (the caveat below says why).
2. Require status checks to pass before merging: the two checks above. Where the setting asks which app must report a
   check, choose GitHub Actions. Require the branch to be up to date before merging, so the checks ran on the tree
   that will be merged.
3. Block force pushes and deletion of `main`.
4. Decide whether the rule binds the owner too (classic rule: "Do not allow bypassing the above settings"; ruleset: no
   bypass actor). Binding the owner means a red check blocks even the owner's merge, which is the point of requiring
   it; leaving a bypass keeps a way to merge a repair of CI itself. Either way a bypass is visible in the pull request.
5. Do not turn on a merge queue for `main`: neither workflow has a `merge_group` trigger, so the two checks would never
   report for a queued merge.

## The self-approval caveat

GitHub does not let the author of a pull request approve it. With one maintainer:

- a rule that requires an approving review blocks every pull request the owner opens, unless the rule lets the owner
  bypass it, and a bypass that covers reviews usually covers the required checks as well;
- "Require review from Code Owners" is the same requirement for the files `.github/CODEOWNERS` names, and the owner,
  being their only code owner, cannot meet it on his own pull request.

So in this repository the barrier against a change to the CI judge is the owner's own reading of the diff, which
`.github/CODEOWNERS` marks, and `MK_ANCHOR_CI`, which turns both workflows red after any change to a judge file until
the owner sets the new digest (while the workflows that run still call the judge and the judge that runs,
`tools/ci/judge_digest.py`, is the reviewed one: both come from the commit being judged, so a change that also edits
them can print any digest; see What these settings do not close). A required review becomes a barrier only when a
second person with write access reviews.

## CODEOWNERS

`.github/CODEOWNERS` names the repository owner, by the owner's public GitHub handle (the one the repository's address
holds), for the CI judge's files: the workflows, `.github/CODEOWNERS`, `.github/actions/`, `tools/ci/`,
`tools/check_manifests.py`, `ci/mathkernel/`, `kernel/coq/gate/`, `kernel/coq/EXPECTED-CI-LIBRARIES.txt`,
`kernel/coq/ANCHORS.md`, `THEOREMS.md`, the two feature rows, feature row 4's predictions file and its `plants4/`
folder, `kernel/runtime/check_fpenv.py`, `kernel/runtime/test_fpenv.c`, `BOUNDARIES.md`, each
`kernel/coq/<folder>/FROZEN.txt` (both judge files since ruling S282-3 (b)) and any `*.py` file at the repository's
top.
Without the review requirement, on a pull request someone else opens it requests the owner's review; on the owner's
own pull request it only marks these files. It blocks nothing. It is itself a judge file, so a change to it also
moves `MK_ANCHOR_CI`.

## Actions settings that support these checks

- Workflow permissions: read the repository's contents only (each workflow already asks for `contents: read` and
  nothing more).
- Allowed actions: the workflows use four of GitHub's own actions (`actions/checkout`, `actions/cache` with
  `actions/cache/restore`, `actions/upload-artifact`, `actions/download-artifact`), each pinned in the workflow by a
  full commit sha. Allowing only GitHub's own actions keeps a new outside action from running without a settings
  change. With the setting "Require actions to be pinned to a full-length commit SHA" (Settings, Actions, General),
  a workflow whose `uses:` line names an action by a tag or a branch fails to run.
- Workflows from forks: require approval before an outside contributor's workflow runs ("Require approval for all
  external contributors"). This repository accepts no outside contribution until the owner sets contribution terms
  (`LICENSING.txt`).
- The integrity job's check was named `Manifests and feature rows (no Coq)` before the hardened workflows; a rule that
  still requires that name waits forever. Require `Integrity (no Coq)` instead.
- Variables: the anchors (`MK_ANCHOR_<FOLDER>` for each gated folder, and `MK_ANCHOR_CI`) are repository
  Actions variables. Whoever administers the repository can change them, and a change shows in no pull request: set
  them only after review, and keep `kernel/coq/ANCHORS.md` as the ledger of the folder values. In a repository owned
  by an organization, an organization variable of the same name stands in for a missing repository variable, so its
  administrators could set an anchor too; this repository belongs to a personal account, which has no organization
  variables (the precedence READ in GitHub's documentation of variables by a review of this page; that the account
  is a personal one: not checked on GitHub).

## What these settings do not close

- A pull request runs its own workflow files and its own copy of the judge. A pull request that rewrites a workflow
  can make that workflow skip a check, or add a job that reports a required name, and its checks can come out green.
  Requiring the checks shows that the checks of the pull request's own workflows passed; that those workflows are the
  reviewed ones is shown only by the review. `MK_ANCHOR_CI` binds the judge's files only while the workflows that run
  call the judge and the judge's own code is the reviewed code: a merged change that removes that call, or that
  makes `tools/ci/judge_digest.py` print the expected digest, removes the binding too; a push runs its own commit's
  judge as a pull request does. A change under `.github/` or `tools/ci/` is read before it is merged.
- A required check reports on a commit, not on what a later run of another commit says. A green check on `main` is
  evidence of that commit's run only.
- The settings change nothing about what a green run shows: `docs/engineering/MATHKERNEL-LINUX-CI.md` says that.
