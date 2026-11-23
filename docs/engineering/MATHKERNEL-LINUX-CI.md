<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# MathKernel on Linux: what the workflows run, how they are anchored, and what a green run shows

Status when this file was written (2026-11-17): the workflows were in the tree and **had not run on GitHub**; their
grade was NOT MEASURED (`docs/GUARANTEES-LEDGER.md` §4). A run is cited by its id and commit, not by this file; the
first runs are below, under "The first runs".

Note of 2026-11-18: the workflows are now the hardened ones that the next section describes. The sections after it
describe the workflows as first proposed and their first runs; where the two differ, the next section holds. The
hardened workflows had not run on GitHub when it was written: NOT MEASURED.

Note of 2026-11-22: four gated folders were added, `sincos32n`, `exp32a`, `floor32` and `ceil32`. Neither workflow
holds a list of folders, so the gate job has one more leg for each, and the owner sets four more variables,
`MK_ANCHOR_SINCOS32N`, `MK_ANCHOR_EXP32A`, `MK_ANCHOR_FLOOR32` and `MK_ANCHOR_CEIL32` (`kernel/coq/ANCHORS.md`);
`MK_ANCHOR_CI` moves with them, since the inventory's digest is part of it. The counts under "Rehearsed locally", and
those of the sections on the first proposal and its runs, are of the tree before the four were added. No CI run has
judged the four folders: NOT MEASURED.

Note of 2026-11-22 on the sweep job (ruling S280-13 (a)): `mathkernel-linux.yml` gains a job, **sweep**, on the
fpenv job's two runners (x86-64 and arm64), and the verdict needs it. Its check, `tools/ci/check_sweep.py`, reads
`tools/ci/SWEEP-SOURCE.txt`, which names two candidate floor32/ceil32 sweeps and chooses one by its `use` line:
`kernel/coq/fclink/sweep_fc2.c` (`use fclink`, as written), held also to the sha256 that
`kernel/coq/fclink/FROZEN.txt` records, or `sweep_fc.c`, the first exhaustive sweep, at
`kernel/records/floor32/sweep_fc.c`, where the records of ruling S280-12 (a) put it, held also to the sha256 that
its freeze list `kernel/records/floor32/SWEEP-FROZEN.txt` records. The check refuses a source whose
sha256 is not the declared one; builds it with GCC and clang at `-O0` and `-O2`, `-std=c99 -ffp-contract=off`; refuses
an object in which `objdump` lists an x87 or FMA instruction
(canaries built to hold such instructions, an FMA one per compiler and, on x86-64, an x87 one too, show that the scan
finds them in that compiler's objects); and runs each build over all 2^32 binary32 inputs of floor32 and of ceil32,
requiring every comparison the program makes to agree and each plant (the program without its zero step) to differ
on exactly its predicted inputs, 1 for floor32 and 1,065,353,216 for ceil32. Each leg keeps its HELD line as evidence;
the verdict requires both, each naming gcc and clang and the leg's own machine, both legs one source.
`tools/ci/tests/test_check_sweep.py` holds the check to its plants with stand-ins for the compilers, `objdump` and the
programs; `test_workflow_guards.py` and
`test_safepath.py` hold the new steps (the steps with an inline check that the first cuts from the workflows are now
eighteen, where "The hardened workflows" below says sixteen). What a pass would show: on each runner, with those two
compilers and that C
library, the frozen sweep gives its results at both levels with no contraction and no x87 code in its objects. What
it does not show: that the C is the Coq program (for `sweep_fc2.c` that is FCLINK's statement; for `sweep_fc.c` a
transcription by hand); the C library's `floorf` and `ceilf`, which are linked, not scanned; NaN payloads; another
compiler, flag or processor. The job has not run on GitHub: NOT MEASURED. Its check ran on one Windows host with
clang alone, on both candidates, and held (MEASURED there; GCC, Linux and arm64 NOT MEASURED). Until the source the
`use` line names is in the tree, the job fails at its source row.

Note of 2026-11-22 on the boundary map (ruling BM-2 (a)): `integrity.yml` gains a step after the inventory that runs
`tools/ci/check_boundaries.py` on the tree. It holds `BOUNDARIES.md`, the boundary map, to the proved table of
`THEOREMS.md`: every statement of that table has a row; every row has its seven fields (Claim, Claimed in, Stop, Kind,
Covers beyond, Grade, Proof again); every grade is GATED, MEASURED, ARGUED, DECLARED or NOT_MEASURED. Beyond those
three refusals, which the ruling names, it also refuses a Kind that is not one of the four stops the ruling names,
graded evidence that names no file (a path of the tree, or the sha256 of a record kept outside it), a path that is not
in the tree, a PENDING or STATED row that names a statement of the proved table, and a Proof again that names no
stage. `tools/ci/tests/test_check_boundaries.py` holds the check to its plants on maps it writes in a temporary
folder, and holds the workflow to the step. `BOUNDARIES.md` is the judged file, and no test reads it; the check and
its test are judge files, and since ruling S282-3 (b) (the note after the next) so is the map, so a change to any of
them moves `MK_ANCHOR_CI`. What a pass would show: the map has a well-formed row for every proved statement. What it
does not show: that a row is true, that the map lists every stop, or that no sentence of the tree claims past its row
(the review before each push, under the ruling). The step has not run on GitHub: NOT MEASURED. The check held on this
tree on one Windows host (MEASURED there).

Note of 2026-11-22 on four more gated folders: `rti32`, `order32`, `bits32` and `fclink` were added. The gate job has
one more leg for each, and the owner sets four more variables, `MK_ANCHOR_RTI32`, `MK_ANCHOR_ORDER32`,
`MK_ANCHOR_BITS32` and `MK_ANCHOR_FCLINK` (`kernel/coq/ANCHORS.md`); `MK_ANCHOR_CI` moves with them. The gate logs of
`bits32` and `fclink` hold libraries that `kernel/coq/EXPECTED-CI-LIBRARIES.txt` does not list (`bits32`: Flocq's
`IEEE754.Binary` and `IEEE754.Bits`; `fclink`: Coq's `Strings.Ascii`, `Strings.Byte` and `Strings.String`; MEASURED
on the gate consoles of one host), so until their lines are added from a CI run of the pinned workflow, the gate-log
check's row "every library logged is expected, with the expected hash" refuses those two legs (ARGUED from
`tools/ci/check_gate_log.py`, not run). With `kernel/coq/fclink` in the tree, the source the sweep job's `use` line
names is present; the sweep check's source row held on this tree on one Windows host (MEASURED there). No CI run has
judged the four folders: NOT MEASURED.

Note of 2026-11-22 on the judge group `boundaries-frozen` (ruling S282-3 (b)): the CI judge gains a required group,
`BOUNDARIES.md` and the `FROZEN.txt` directly inside each folder under `kernel/coq/` (eight folders hold one: the
record of each folder's statement files' sha256, frozen before their proof as each file says). Before it, no judge
group, freeze list or import manifest bound their bytes, so a row of the map or a `FROZEN.txt` could change without
moving `MK_ANCHOR_CI`; now a change to either, or a new folder holding a `FROZEN.txt`, moves the digest. The group's
row fails when `BOUNDARIES.md` is missing or no `FROZEN.txt` is found, and a link directly under `kernel/coq/` (where
a `FROZEN.txt` is looked for) fails the row "judge files are plain files". The read audit binds them through the same
groups, so a test may now read them. `kernel/records/` is not in the group: its records are listed by name and sha256
in `kernel/records/INDEX.md`, and no check compares a record with its line there (the sweep check holds one,
`sweep_fc.c`, to the sha256 `tools/ci/SWEEP-SOURCE.txt` declares and to its line in its freeze list
`kernel/records/floor32/SWEEP-FROZEN.txt`, when the `use` line of `SWEEP-SOURCE.txt` names it); a records check is
left to a later push.
`.github/CODEOWNERS` names the two new patterns. What a pass would show: those files are, byte for byte, the ones whose
digest the owner set. What it does not show: that a row of the map is true, or that a `FROZEN.txt`'s hashes are the
owner's or were recorded before a proof. On one Windows host (MEASURED there): the judge held on this tree as it then
stood, 21 of 21 rows over 276 judge files; `tools/ci/tests/test_judge_digest.py` held 92 of 92 cases, its thirteen
new ones (the map and a `FROZEN.txt` changed, added, removed, made a folder or reached through a link, three decoys,
three `--json` refusals) each as frozen before their first run; the same test given a judge without the group's
line failed exactly its fourteen predicted cases. Not run on GitHub: NOT MEASURED.

Note of 2026-11-22 on a third workflow (rulings SY-1 and SY-2) and on three scripts added to `tools/ci`:
`.github/workflows/drift.yml` runs on every push and pull request, once a week and by hand, one job per copy
(`orlog/` and `verdandi/`): `tools/ci/tests/test_drift.py`, then `tools/ci/drift.py` on the copy against the
original's main as fetched at the run. It is a report, not a check to require: its job is not the MathKernel verdict,
it reads no artifact of the other two workflows, and it turns red also when an original's main has moved since its
pin, until a re-pin (`docs/engineering/BRANCH-PROTECTION.md`). Its workflow, script and test are judge files, so a
change to them moves `MK_ANCHOR_CI`. Where this file says "both workflows" or "the two workflows", it means
`integrity.yml` and `mathkernel-linux.yml`. `test_usage.py` holds the scripts of `tools/ci` that existed when it
was written (2026-11-20); the two usage refusals of the three added since, `check_boundaries.py`, `check_sweep.py`
and `drift.py`, are held by their own tests (`test_check_boundaries.py` U03 and U04, `test_check_sweep.py` and
`test_drift.py` U01 and U02). `tools/ci/tests/test_safepath.py` holds `drift.yml` to its `PYTHONSAFEPATH` line too,
and `test_workflow_guards.py` holds the verdict job's `needs:` list to the list its first step compares the jobs
with (both since this note, each with a plant). The drift workflow has not run on GitHub: NOT MEASURED.

## The hardened workflows (2026-11-18)

Both workflows run on every push and every pull request, whatever it touches, and by hand. GitHub starts no run for
a push or pull request whose head commit message holds `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]` or
`[actions skip]`, or that ends with the trailer `skip-checks: true` (or `skip-checks:true`) after two blank lines, nor
for a pull request with a merge conflict: a required check then stays pending and blocks the
merge, and such a commit has no run (READ, GitHub's documentation). A pushed tag starts both workflows on the tagged
commit (a push of more than three tags at once starts none; READ, GitHub's documentation). The run is judged against
the current `MK_ANCHOR_CI`, so a tag on a commit made before the last change to the CI judge runs red. Neither
workflow holds a list of folders:
`tools/ci/inventory.py` finds the gated folders from the tree, and the gate jobs are made from what it finds. Every
action is pinned by a full commit sha, with its release tag beside it (`actions/checkout` v4.4.0, `actions/cache` and
`actions/cache/restore` v4.3.0, `actions/upload-artifact` v4.6.2, `actions/download-artifact` v4.3.0; each sha is
that release tag's commit in GitHub's own repository of the action, READ through GitHub's API on 2026-11-18). Every
value reaches a script through `env`, never written into it, and each workflow asks for `contents: read` only. Python
runs with `PYTHONSAFEPATH=1`, on the runner and in each container that runs it: neither a script's own folder nor the
current folder is put on its import path, so a file named like a standard module (`json.py`, `re.py`) beside a
script, or at the top of the checkout for a step that reads its script from stdin, is never imported in place of the
standard one.

### What runs

`.github/workflows/integrity.yml`, one job, **Integrity (no Coq)**. Every step after the checkout runs even when an
earlier one failed, so one run shows every failure:

1. no compiled Python is tracked;
2. `tools/check_manifests.py`, as before;
3. `tools/ci/inventory.py`;
4. `tools/ci/judge_digest.py`, given `MK_ANCHOR_CI`;
5. `feature_row3.py` and `feature_row4.py` on every freeze list the inventory finds: each gated folder's and each of
   Verðandi's copies under `verdandi/mathkernel/F32/`;
6. `tools/ci/tests/run_all.py`: every test of `tools/ci`, each checker held on honest inputs and seen to fail on each
   of its plants, every case of each test run. `test_check_gate_log.py` and `test_check_toolchain.py` run there with
   `--repo-data`: their honest inputs and plants are built from the tree's own records (`EXPECTED-CI-LIBRARIES.txt`,
   `EXPECTED-TOOLCHAIN.txt`, the folders' `gate.json` and `FROZEN4.txt`, consoles written in `gate4.py`'s exact form),
   since the saved CI logs their other mode reads are not in the tree. That mode does not show that a real gate
   prints those lines; every gate job's own log, checked in the other workflow, does. `test_feature_row4.py` runs
   feature row 4 on its plants and the tree's freeze lists against predictions each written before the first run of
   its plants (the first file before any run of row 4, the four addenda after reviews), and
   `test_safepath.py` shows `PYTHONSAFEPATH` stopping a module planted beside a checker or in a step's current folder,
   with a control in which the planted module takes effect. `test_workflow_guards.py` cuts each guard the two
   workflows run inline from their text by step name and runs it under bash, with stand-ins for `docker`, `git` and
   the inventory call, on honest inputs and on plants (a malformed gate matrix among them); a step it expects that is
   missing from the text fails it. The steps it cuts are the sixteen of the two workflows that hold an inline check,
   the fpenv job's search for its compilers among them (run with a `PATH` that holds only what each case puts there);
   the other steps call a script that its own test holds, or an action. It shows the guards' shell and Python, not
   GitHub's reading of the YAML. `test_usage.py` shows every script of `tools/ci` that reads options refusing
   `--help` and an abbreviated option as usage errors. Every case of every test runs here; only in the local form of
   `run_all.py`
   (given saved CI logs) may a guard case whose value ends in a carriage return print NOT RUN, where a probe finds that
   the local bash drops that character (Git Bash does; bash on Linux keeps it).
7. `tools/ci/read_audit.py`: the tests of step 6 and the feature rows of step 5 again, every Python process under an
   audit hook. It fails when one of them opens or copies for reading a file inside the checkout that is neither a
   judge file (below), nor a freeze list the inventory found or a file such a list names, nor a file an import
   manifest (`MANIFEST*.txt`) names, nor a file that `CHANGES-AFTER-IMPORT.md` names on a line with the sha256 of its
   bytes (ruling S283-1 (a), as row M3 of `tools/check_manifests.py` reads that file), nor inside a new temporary
   folder the run made (a path compared as written and as the reading process resolved it: links, junctions, short
   names, a long-path prefix); when one of them links,
   removes or moves a file inside the checkout outside such a folder (so a file read and then removed or moved, or
   read through a link, is judged too); and when one of them, outside a temporary folder a run made, starts a process
   without the hook (its folder not first on `PYTHONPATH`, another `PYTHONHOME`, `-I`, `-E` or `-S`), starts a
   program that is not Python (`git`, `sh`, `env`, a script run by its first line), starts a shell given a command
   (`shell=True`, `sh -c`, `cmd /c`) or a shell command the hook cannot judge (`os.system`, `os.startfile`), imports
   `multiprocessing`, forks (`os.spawnv` forks on Linux), starts a process through `_winapi.CreateProcess` without
   `subprocess.Popen`, changes `PYTHONPATH`, `PYTHONHOME` or the hook's variables in its own environment, or logs a
   temporary folder that is the checkout, holds it or holds a bound file (a folder that existed before exempts
   nothing; the audit's own test starts such processes in its temporary folders, and the tests start `git`, `sh` and
   `bash` only there: `test_records.py`, `test_check_toolchain.py`, `test_workflow_guards.py`, `test_drift.py`
   (`git`) and the stand-ins of `test_read_audit.py`). The hook judges every thread's events, also while another thread
   is inside it, and reads its own folder and `PYTHONHOME` once, when it loads. It sees Python processes only: a program
   that is not Python is judged by its start, and what it reads is not seen. Its own test, `test_read_audit.py`, runs it
   on planted trees: an unbound read in a test, in a process that test starts and
   in a feature row fails it, and so does a process started without the hook, in each of the ways planted there
   (without the hook's `PYTHONPATH`, with `-I` alone or after another option's argument, one holding a quote and a
   blank among them, under another first argument with the interpreter given as the program, through `os.spawnv`
   (`os.posix_spawn` on Linux, where `os.spawnv` forks), a shell command, a shell given a command, after `os.unsetenv`
   or `os.putenv` of `PYTHONPATH`, after taking the
   hook's variables out of `os.environ` with no event, with another `sitecustomize` before the hook's, with
   `PYTHONHOME` changed), a forged temporary folder (an event raised by hand, a line written into the hook's log), an
   unbound read through a long-path prefix, a link into the checkout, a copy (`shutil.copy2`, `copytree`) or a second
   thread, a read followed by a removal or a move, a folder removed, an import of `multiprocessing`, a fork, `os.spawnv`
   (on Windows, which has no fork, with the fork's event raised by hand, as in the fork plant) and a direct
   `_winapi.CreateProcess`, and `git` started from the checkout's top folder; and a `--json` path inside the checkout
   written another way (an 8.3 short name or a junction on Windows, a symbolic link on Linux), or an existing `--json`
   file that has another name (a hard link), is refused as a usage error, nothing written.

`.github/workflows/mathkernel-linux.yml`:

1. **inventory** ("Inventory and CI judge"): no compiled Python is tracked; the inventory, whose gate matrix is the
   job's output; the judge, given `MK_ANCHOR_CI`. Both JSON records are kept as the artifact `inventory-attempt<N>`.
2. **fpenv**: as before, on x86-64 (`ubuntu-24.04`) and arm64 (`ubuntu-24.04-arm`). Each leg also checks that the
   check's last line is its `FPENV CHECK HELD` verdict, and only then keeps its evidence, the artifact
   `fpenv-<runner>-attempt<N>`: one file naming its leg and attempt, and that verdict line.
3. **image**: built once per Dockerfile and cache scope, as before. Then the base image the build used must be the
   digest `ci/mathkernel/Dockerfile` pins in its one `FROM` line (`FROM` counted as Docker reads it, in any case of
   letters, at any indent, and before a blank, a tab, a line continuation or the line's end; refused, since that count
   cannot read them: a byte outside printable ASCII, a blank and a tab, such as a byte-order mark, a no-break space or
   a NUL byte, the file read as text (`grep -a`), byte by byte, in the C locale; a first line starting with `#!` or
   `//`; a line shaped as a parser directive, `# <word>=<value>` or `// <word>=<value>`, anywhere; and a line
   continued onto one that does not start with a blank, or onto a comment or a blank line) (that Docker and BuildKit
   read the rest as the count does: ARGUED from BuildKit's Dockerfile parser as a review remembered it, its source
   not read; no Docker was run to check it), and `tools/ci/toolchain_probe.sh`, run
   inside the image, is compared with
   `ci/mathkernel/EXPECTED-TOOLCHAIN.txt` by `tools/ci/check_toolchain.py`. An image whose toolchain differs fails
   the job and is not kept in the cache. The job's outputs are the image id, the base image and the toolchain digest;
   its record is the artifact `toolchain-attempt<N>`.
4. **gate**: one job per gated folder of the inventory, named `Gate <folder>`. Each refuses a missing or malformed
   anchor variable, as before; finds that anchor in the folder's row of `kernel/coq/ANCHORS.md`; reruns the inventory
   and the judge on its own checkout; loads the cached image and refuses it unless its id and base are the image
   job's; runs the probe and the toolchain check again, whose digest must be the image job's; runs feature rows 3 and
   4 on the folder's freeze list; runs the gate with `--recheck`, as before; checks the gate's output with
   `tools/ci/check_gate_log.py`; writes its run record with `tools/ci/run_record.py`. It keeps the record as
   `run-record-<folder>-attempt<N>`, and as `gate-evidence-<folder>-attempt<N>` the gate's log, the JSON it read and
   the gate's own text outputs, `kernel/coq/<folder>/out4/*.out`: `Closure.out` (the closure of the folder's
   identity), `Locate.out` (the file each library was loaded from), and for each module of the folder and of its
   dependencies what `coqc` printed and what `coqchk` printed (for `Identity`, its printed assumptions). A local run
   of `gate4.py` wrote 112 such files for one folder, about 0.2 MB of text (MEASURED there, not in CI); the files in
   the subfolders of `out4/` (the plants' runs) are not kept. The upload names files in two folders, the runner's
   temporary folder and the checkout, so the artifact keeps each file under its path below the folder those two share
   (ARGUED from the upload action's rule for several paths; not run on GitHub).
5. **MathKernel verdict**: runs after every other job, also when one failed or was skipped. It fails unless every
   other job succeeded, each fpenv leg's evidence of its attempt, downloaded by its exact name, names that leg and
   attempt and holds a HELD n of n line, and `tools/ci/verify_records.py` holds over the run records of its attempt;
   it keeps `run-summary-attempt<N>`. The jobs it waits for include fpenv's leg on the arm64 runner
   `ubuntu-24.04-arm`; where GitHub does not offer that runner, the verdict does not report while that leg waits, and
   a required verdict blocks every merge.

### Each new check: what it shows and what it does not

- **No compiled Python is tracked.** Shows: the commit holds no `.pyc`, `.pyo` or `__pycache__` file, so no compiled
  bytecode sits in the checkout beside a reviewed source. Does not show: anything a run writes later (every script
  runs with `-B`); a tracked extension module (`.so`, `.pyd`), which this step does not refuse (`PYTHONSAFEPATH` keeps
  a script's folder and the top folder off the import path; under `tools/ci/` such a file is a judge file).
- **Inventory** (`tools/ci/inventory.py`). Shows: every `gate.json` is a gated folder's (`kernel/coq/<folder>/`) or a
  copy's (`verdandi/mathkernel/F32/<folder>/`); a gated folder's top-level `.v` files are exactly its `gate.json`
  files, its `plants/*.v` exactly the plant files it names, and no other `.v` lies in it; its freeze list holds in
  the tree and lists every file its gate requires (by `gate4.py`'s rule, so a list the gate would refuse is refused
  before any gate job runs), a listed path being read only when each of its parts is spelled as its folder lists it
  (so a trailing dot or another case of letters is absent on Windows as on Linux); `kernel/coq/gate/` holds exactly
  its four files, so no module can shadow one the gate imports; each `Identity.v` is the plain conjunction of its
  folder's `THEOREMS.md` row; each value in `kernel/coq/ANCHORS.md` is the sha256 of its folder's `FROZEN4.txt`;
  `THEOREMS.md` has its Successors heading and one table under it, and every row of that table names statements of
  the proved table. `THEOREMS.md` and `ANCHORS.md` are read in a named subset of Markdown, and anything outside it
  fails: a line ends at a line feed (a carriage return before it allowed); no other carriage return, byte-order mark,
  control character (a tab among them), format character (Unicode category Cf) or `&` anywhere, and outside printable
  ASCII only the four characters `THEOREMS.md` holds (U+00B1, U+00F0, U+03C0, U+2026) in `THEOREMS.md` and none in
  `ANCHORS.md`, so no invisible character; no backslash, no backtick run left open on its line (a literal backtick, or
  a code span running on to the next line), no code span holding a `|` (GitHub cuts a table row at its pipes first),
  and no code fence (three backticks or tildes, after any indent or after list markers); no `[` (a link, an image, a
  link reference definition, a footnote or a task-list box: GitHub shows other text, a picture or nothing), apart
  from a `THEOREMS.md` heading's line, where the heading rule refuses it; no `#` followed by a blank or the line's end
  on any line but a top-level heading's (so no heading opens inside a nested list item, a block quote in a list item
  or a footnote, which the inventory does not open); headings (at any indent) and table headers in printable ASCII
  and U+2026, without `[`, `<` or a backslash; name cells holding only names in backticks, commas and blanks; in
  `THEOREMS.md` no table but the proved table, successor tables and tables whose
  headers hold only letters, digits, blanks, commas, U+2026 and the marks `*`, `_` and backtick, and in `ANCHORS.md`
  one table; no HTML but line 1's comment and, in `THEOREMS.md`, the lines of its `<details>` block, each followed by
  a blank line; no list item whose text starts with `#`; no line of `=` only, or of `-` only with a colon allowed at
  either end, under a line that is not blank (it can be a setext heading's underline or the delimiter row of a table
  without pipes; at any indent and in any container; a blank line holds only blanks and tabs); no block quote, and
  no list item holding a `|`. Within it the tables are read as GitHub reads them: a line directly under a table's
  body that GitHub reads as one more row (with or without outer pipes) fails, and so does a second table (with or
  without outer pipes) in `ANCHORS.md` or under the Successors heading, up to the next Markdown heading, a second
  proved table anywhere in `THEOREMS.md` (with or without outer pipes, or indented), a second heading whose text
  starts with "Successor" (of any level, at any indent, or underlined, its text read with emphasis and code marks
  taken out) and a table with "Old statement" and "Successor" columns outside the Successors section; a header or a
  heading is compared with those with ASCII look-alikes folded (a capital I and a 1 read as l, a 0 as o, rn as m, vv
  as w), so "FoIder" or "Success0rs" counts as what it imitates. No gated folder may be named `ci` (its variable
  would be `MK_ANCHOR_CI`). The gate job's `ANCHORS.md` step reads that file with the inventory's own readers, so the
  two read it alike and refuse the same forms of it; the inventory, which the gate job runs next, also refuses an
  unknown folder's row, a misnamed variable and an empty record. Every statement file is printable
  ASCII (tab, line feed, carriage return and form feed allowed) outside its comments and strings, and every sentence
  of every statement file the inventory finds is one its statement-names row reads: a command that defines no name
  (`From ... Require`, `Open Scope`, `Arguments` and the others its header lists) or one whose names it reads, every
  name each sentence defines
  (the names after `with`, every constructor, a record's constructor and fields, among them); a sentence it cannot
  read fails the row, a proof among them. No name is defined in two statement files (the one exception, `FMAX32`, is
  defined alike in `exp32r/RANGE_Statement.v` and `p32r/P32R_Statement.v`, and only while the two definitions are the
  same sentence). Each copy is byte for byte what its freeze list names. A linked folder (a symbolic link, or a
  junction) that a walk of the inventory meets is not entered and fails the row whose walk met it, so nothing behind a
  linked folder is read as part of the tree (a symbolic link to a file is read through; where a freeze list names
  that file, its bytes are held to the listed sha256). Two output paths that are one file (a hard link among them) and
  an existing
  output that has another name are refused as usage errors. A new folder is gated without editing a list, and fails
  here until its rows exist. Does not show: a proof (the gate shows that); that an anchor is the owner's: a
  folder, its freeze list and its `ANCHORS.md` row changed together hold here, and fail only against the folder's
  variable; that a copy is still there: a copy that no other copy's list names can be removed with every row holding,
  and only the inventory's digest, hence `MK_ANCHOR_CI`, moves; names as Coq resolves them: the statement-names row
  compares names as written, reads a name Coq makes itself only where its header says (a record's default
  constructor, the four elimination names of an inductive or record type; an automatic Instance name is refused
  instead), compares a notation by its string as written, and does not see a statement file named otherwise that no
  `Identity.v` names (the statement files are each top-level `<NAME>_Statement.v` and each file holding a statement an
  `Identity.v` names); that GitHub renders the subset as read here (ARGUED from the CommonMark and GitHub table
  specifications as remembered, not run on GitHub); a heading or a table inside an indented code block is counted,
  though GitHub shows code (an over-refusal; a code fence is refused); a look-alike the fold does not list (another
  pair of characters a font draws alike) is read as written, so a table or heading that imitates the proved table's,
  a successor table's or the Successors heading that way is read as a plain one.
- **CI judge** (`tools/ci/judge_digest.py` and `MK_ANCHOR_CI`). Shows: the judge's files and the inventory's digest
  are, byte for byte, the ones whose digest is the value of `MK_ANCHOR_CI` (the owner's to set). The judge's files
  are every workflow file (`.github/workflows/*.yml` and `*.yaml`), `.github/CODEOWNERS`, every file under
  `tools/ci/`, `tools/check_manifests.py`, every file under `ci/mathkernel/` and under `kernel/coq/gate/`,
  `kernel/coq/EXPECTED-CI-LIBRARIES.txt`, `kernel/coq/ANCHORS.md`, `THEOREMS.md`, the two feature rows, feature row
  4's predictions `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` and its plants
  `kernel/hardening/features/plants4/`, the fpenv job's gate `kernel/runtime/check_fpenv.py` and its self-test
  `kernel/runtime/test_fpenv.c`, the boundary map `BOUNDARIES.md` and each `kernel/coq/<folder>/FROZEN.txt` (ruling
  S282-3 (b)), and, when there are any, every `*.py` file at the repository's top and every file
  under `.github/actions/`. A `--json` path that is another name (a hard link) of an existing file is refused as a
  usage error. Every file that a Python process of a CI test or feature-row run that keeps the audit's hook opens
  inside the checkout, by a path its event names, is bound, and a step checks it on every run:
  `tools/ci/read_audit.py` (integrity step 7) runs them again under an audit hook and fails on a read of a file that
  is neither a judge file, nor in a freeze list or an import manifest, nor named in `CHANGES-AFTER-IMPORT.md` on a
  line with the sha256 of its bytes, nor inside a new temporary folder of the run, and on a process started in a way
  that leaves the hook (step 7 lists them), so a test added later that reads a new file fails there until the file is
  bound (the hook's events on Linux CPython 3.12: ARGUED from Python's documentation; MEASURED on Windows with Python
  3.14). The tree they judge is bound through the inventory's digest, the import's records through the manifests
  check. Does not show: that the judge is right (that is the owner's review); a file outside that list, such as
  `mk_fpenv.c` and `mk_fpenv.h`, the subject the fpenv job judges, which no anchor holds; a run whose commit also
  edits the judge's code (a push or a pull request: each runs its own commit's `judge_digest.py` and workflows), which
  can print any digest; a process started, or an import made, in a run's temporary folder, which is not judged (the
  audit's own test plants there; the tests start `git`, `sh` and `bash` only there, and `sh` reads
  `tools/ci/toolchain_probe.sh`, a judge file, by its path); what a program that is not Python reads (its start is
  judged: outside a run's temporary folder it fails the audit, so `env`, a script run by its first line and a shell
  running a script file fail there too); a file opened relative to a folder's descriptor (`os.open` with `dir_fd`,
  which the event `open` does not name: placed against the process's own folder); and what no check inside the
  watched processes can see: a process that sets out to evade the hook. That is not closed by a check, because none
  can be sound inside the processes the hook watches: the hook runs in them; the barrier there is the review of the
  tests, judge files all, that `MK_ANCHOR_CI` forces.
- **The image's Dockerfile** (the image job's step "Say what the image holds; its base is the digest the Dockerfile
  pins"). Shows: the base image the build used is the digest `ci/mathkernel/Dockerfile` pins in its one `FROM` line,
  the count of `FROM` reading the keyword in any case of letters, at any indent, before a blank, a tab, a line
  continuation or the line's end; and the file holds none of the forms that count cannot read (a byte outside
  printable ASCII, a blank and a tab, a NUL byte among them, the file read as text in the C locale; a first line
  starting with `#!` or `//`; a parser directive's form on any line; a line continued onto one that does not start
  with a blank, or onto a comment or a blank line). `test_workflow_guards.py` runs the step's shell on the tree's
  Dockerfile and on each refused form (MEASURED with Git Bash's grep and awk; the runner's: NOT MEASURED). Does not
  show: that Docker and BuildKit read the file as the count does (ARGUED from BuildKit's Dockerfile parser as a review
  remembered it, its source not read; no Docker was run to check it); another image or file a build reads without a
  `FROM` line
  (`COPY --from=<image>`, a
  `RUN --mount` from an image, `ADD` of a URL), which does not change the base and which the toolchain check binds
  only as far as the probe names what it reads.
- **Toolchain** (`tools/ci/toolchain_probe.sh` and `tools/ci/check_toolchain.py`), in the image job and again in each
  gate job. Shows: the image's opam switch export, `coqc`, `coqchk` and `python3` have the recorded sha256; its Coq
  and Python version lines are the recorded ones; every recorded opam package is installed at its version, and no
  other is, apart from the compiler's three `base-*` packages, allowed by name. The probe also prints, last, values it
  records and the check does not compare (`coqc -where`, `coqchk`'s bytecode default, `COQPATH`, `COQLIB`,
  `OCAMLPATH` and `OCAMLRUNPARAM`); a value holding a line feed, which would print lines the check reads as keys, is
  printed as `failed`. Does not show: what the probe does not
  name (the other apt packages, the C compiler, `libgmp`; the Coq libraries are compared one by one by the gate-log
  check);
  that the recorded values are right: they are what four CI image builds printed and agreed on.
- **Feature row 4** (`kernel/hardening/features/feature_row4.py`). Shows: no character outside printable ASCII (tab,
  line feed, carriage return and form feed allowed) anywhere in a scanned file, in code, comments and strings alike, so
  the row reads every name as its ASCII patterns can and does not rest that rule on its own blanking; outside comments
  and strings, no `Conjectures`, `Context`, `Declare Instance`, `Admit Obligations`, Program obligation command or
  `program` attribute, and these further spellings of five triggers its census (`trigger_census.py`) names, and of
  private inductive types, which it does not name: a `universes`, `projections`, `using` or `private` attribute anywhere
  in an attribute list (first or not, spaced, across lines, in a second list), the prefixes `Monomorphic` and `Private`,
  the option `Default Proof Using`, an inline universe binder `@{`; every `Module` command but a plain `Module <name>.`,
  `Module Import <name>.` or `Module Export <name>.` with the name in ASCII, and `Include`, so `Module Type`, `Declare
  Module`, a functor, its parameters, a functor applied, a module ascribed and import categories are refused whatever
  the name; the commands that read a source file by name (`Load`) or name a file for plugins (`Extra Dependency`),
  change the load path (`LoadPath`: `Add LoadPath`, `Add Rec LoadPath`) or the working folder (`Cd`), load or write a
  saved state (`Restore State`, `Write State`), write files (`Redirect`; `Extraction` and `Extract`: every Extraction
  command) or load a plugin by name (`ML`: `Declare ML Module`, `Add ML Path`, `Add Rec ML Path`), by their words; and
  every `From` but `From <name> Require`. `Require` stays allowed: it loads compiled libraries, which the gate-log check
  compares one by one, and the plugins they declare, which are the image's. Besides row 3's refusals, which cover every
  spelling the census itself counts of its other triggers; with a freeze list, the bytes scanned are the listed ones,
  and no line of the list, a comment's included, holds a character other than printable ASCII and tab once its final
  carriage return is taken off. For the module commands and `From` the row names what it accepts; the file commands it
  refuses by their words wherever they stand (a file command whose words it does not list would pass); for the other
  triggers, that these are every spelling Coq 8.20 accepts is ARGUED from the reference manual as remembered, not
  checked. Does not show: a construct that a tactic, a notation or a library builds without one of these words; that Coq
  accepts each refused spelling (no Coq runs there); the census triggers both rows allow by design: `vm_compute`
  (reported; `coqchk` re-checks it without the VM), plain inductive, variant, record, structure and class declarations
  (each counted on the reported line, a class by row 4 only), and the names of the library's axioms (`propext` and the
  others the census counts), whose use Print Assumptions shows in the gate's own row. The words it refuses are refused
  as names too (`Cd`, `Module'` or `From` as an identifier), and a letter outside ASCII in a comment or a string too:
  over-refusals, none in the files the freeze lists name.
- **Gate log** (`tools/ci/check_gate_log.py`), in each gate job, on the console `tee` wrote. Shows: one complete
  `--recheck` run of the anchored folder by the tree's `gate4.py`, every gate row ok, and the verdict
  `<NAME> GATE4 HELD: n of n`. **CI confirms 0**: the closure row says `0 from the log, N checked in this run` and
  exactly N library lines follow, each `exit 0 clean`, so no library is believed from an earlier run's log.
  **Compatibility**: each library's sha256 equals its line in `kernel/coq/EXPECTED-CI-LIBRARIES.txt` (309 libraries,
  recorded from four CI image builds that agreed), every difference listed. The identity row reports as many axioms
  as the folder's expected list (`kernel/coq/gate/expected-pa-flocq4.txt`) holds. **Completeness**: every file of the
  folder's `gate.json`,
  `Identity` included, is a module of the gate's `out4/Closure.out`, and the closure's outside libraries are exactly
  the libraries checked. Does not show: that the console is a real run's (in CI it reads the file `tee` wrote in the
  same job); that the expected libraries are right: agreement between builds is not soundness.
- **Run record** (`tools/ci/run_record.py`). Shows: HEAD is `GITHUB_SHA` and no tracked file differs from it; the
  commit's tree, its `kernel/coq` tree and the workflow's blob; the folder's `FROZEN4.txt` sha256 is the anchor; the
  gate's log names this checkout's `gate4.py` (by the sha256 it prints), this folder and this `FROZEN4.txt`; the
  job's inventory, judge (given an expected digest equal to its own: in the workflow, the value of `MK_ANCHOR_CI`)
  and toolchain checks held; the gate-log check named this folder, anchor and log. Does not show: that the gate held
  (the verdict job judges the verdict lines the record carries); that the log is a real run's (in CI it reads the
  file `tee` wrote in the same job).
- **Verdict** (`tools/ci/verify_records.py`, job `MathKernel verdict`). Shows: every other job of the run succeeded,
  as `needs.<job>.result` says, and each matrix leg by its own evidence as well: each gate leg by its run record, each
  fpenv leg by the evidence it kept (its leg, its attempt and its HELD n of n line, each downloaded by its exact
  name); there is one record per gated folder of the inventory, none missing, extra or twice; all name one commit,
  tree, workflow, run, attempt, image, toolchain, inventory and judge, equal to the run's inventory, judge and
  toolchain JSON; each record's anchor is its folder's `FROZEN4.txt` sha256; each gate held n of n and each gate-log
  check held 15 of 15, the number of rows `check_gate_log.py` prints; every file under its folder is a record, a folder
  there that cannot be listed fails the records row, and a linked folder there (a symbolic link, or a junction) is not
  walked but read as a file, which no record is. So no
  leg rests on how GitHub combines a
  matrix job's legs into the one result the verdict reads, which GitHub's documentation does not state (a failed leg
  makes it `failure`: ARGUED). Does not show: that a variable holds the right value (the owner's act); anything the
  records and the evidence do not hold.

### MK_ANCHOR_CI

`MK_ANCHOR_CI` is a repository Actions variable beside the folder anchors, one per folder: the CI judge digest of the
reviewed tree. Both workflows give it to the judge and fail when it is missing or differs. The failing row prints the
digest the tree has (`... after review the owner sets MK_ANCHOR_CI to <hex>`; when the variable is missing, it says
so first). To set it, review the
judge's files at the commit, compute the digest on a checkout of that commit:

    python3 -B tools/ci/judge_digest.py --root .

and, when its verdict is HELD, set the variable to the `CI JUDGE DIGEST` it prints. The judge reads bytes, so the same
files give the same digest on Linux and on Windows (ARGUED from the code; run on Windows only). A change to any judge
file, or to what the inventory finds (a gated folder, its files, plants, freeze list or identity names, a copy,
`kernel/coq/gate/`), moves the digest, and both workflows stay red until the owner sets the new value, while the
judge that runs is the reviewed one: each run takes `tools/ci/judge_digest.py` and the workflows from the commit it
judges, so a change that also edits them can print any digest (the CI judge's "Does not show" above). As with the
folder anchors, a run appears to read the variables when it is created (ARGUED, see "The first runs"): after setting
one, start a new run or re-run all its jobs. For a pull request the run judges GitHub's merge commit, so the digest
the failing row prints is that commit's. One variable serves every branch: setting it for a branch that changes a
judge file turns `main` and the other branches red until that branch is merged.

### The checks to require

`MathKernel verdict` and `Integrity (no Coq)`. `docs/engineering/BRANCH-PROTECTION.md` says how to require them, and
what that does not close.

### Re-runs and artifacts

Every artifact's name ends with its run attempt: `inventory-attempt<N>`, `toolchain-attempt<N>`,
`fpenv-<runner>-attempt<N>`, `run-record-<folder>-attempt<N>`, `gate-evidence-<folder>-attempt<N>`,
`run-summary-attempt<N>`. The verdict job
reads its own attempt's only. Re-run all jobs: after a re-run of only the failed jobs, the other jobs' artifacts keep
the earlier attempt's name, and the verdict fails (ARGUED from the artifact names and GitHub's documentation of
re-runs; not run on GitHub). Each workflow cancels a run of its own on the same ref when a newer one starts, `main`
included: a `main` commit followed within a run's time by another has no complete run of its own (its verdict, kept by
`always()`, fails) (ARGUED; not run on GitHub).

### When the image or a library changes

The image is cached under the Dockerfile's hash, so a changed Dockerfile builds a new image. GitHub also removes a
cached image that no run has read for seven days (its default) and evicts the least recently read entries when the
repository's caches exceed their size limit, so the first run after a quiet week, or after the cache filled, builds
the image again (READ, GitHub's dependency-caching documentation). Its toolchain is then
compared with `ci/mathkernel/EXPECTED-TOOLCHAIN.txt`, and its libraries, in every gate, with
`kernel/coq/EXPECTED-CI-LIBRARIES.txt`. A difference fails the job: a review event, not an error to silence. After
review the new values enter those files, which are judge files, so `MK_ANCHOR_CI` changes with them. The Dockerfile
pins its base image by digest and names two opam packages on its install line, `coq.8.20.1` and `coq-flocq.4.2.1`, as
in the four builds the records come from; it names no dependency, because opam would make a named package a root of
the switch and change the switch export the record holds. The dependencies are held by the record instead: it lists
every opam package those builds installed, at its version, apart from the compiler's three base-* packages, which the
check allows by name at version "base", so one that drifts fails the toolchain check. A changed
Dockerfile still builds a new image on its first run, and the apt packages are not pinned, so a rebuild after an
Ubuntu update can change the sha256 of `python3`, or of `coqc` and `coqchk`, which are compiled with the archive's
compiler (ARGUED, NOT MEASURED): a review event, not a false pass.

### Rehearsed locally

On one x86-64 Windows host with Python 3.14 and Git Bash, 2026-11-18 to 2026-11-21 (UTC), on the tree as proposed
after eight reviews, and where said after the ninth, tenth and eleventh (their new refusals, plants, mutants and
wording; the workflow emulation below was not run on those trees). MEASURED there; not on GitHub, not on Linux, not
with Python 3.12:

- `tools/ci/inventory.py`: `INVENTORY HELD: 148 of 148 rows`; for each of the 13 folders the number of files it finds
  the gate requires equals the "N required" that `gate4.py` printed for that folder in CI run 44223174587. Its
  statement-names row read every sentence of the 13 statement files (230 sentences, 201 names; `FMAX32` the one name in
  two of them), each of them printable ASCII outside its comments and strings; `THEOREMS.md` (71 lines) and `ANCHORS.md`
  are in the Markdown subset it reads. `tools/ci/judge_digest.py`: `CI JUDGE HELD: 20 of 20 rows` (243 judge files), and
  21 of 21 given its own digest as `MK_ANCHOR_CI`; given an empty value it failed and printed the value to set.
- `tools/ci/check_toolchain.py` on lines in the probe's form derived from what CI run 44223174587's image job printed
  (the record-only keys, which that job did not print, filled with a placeholder): `TOOLCHAIN HELD: 9 of 9 rows`.
- Feature rows 3 and 4 on all 19 freeze lists (13 gated folders, 6 copies): each held.
- `tools/ci/check_gate_log.py` on the 13 saved gate logs of CI run 44223174587, against this tree: rows 1 to 13 ok for
  each. Rows 14 and 15 read the `out4/Closure.out` that a gate writes, which this tree does not hold, and failed there
  as designed.
- `tools/ci/tests/run_all.py` in its CI form (nothing from outside the tree, `PYTHONSAFEPATH=1`): `CI TESTS FAILED: 1 of
  11 rows`. Every case held as predicted (`check_gate_log --repo-data` 79 of 79 cases, `check_toolchain --repo-data` 33
  of 33, `feature_row4` 186 of 186, `inventory` 265 of 265, `judge_digest` 79 of 79, `read_audit` 60 of 60, `records` 92
  of 92, `safepath` 10 of 10, `usage` 23 of 23, `workflow_guards` 133 of 136) but three workflow-guard cases whose
  planted value ends in a carriage return: Git Bash drops that character before the guard sees it, as the test's probe
  reported, while bash on Linux keeps it (NOT MEASURED here). In the local form, given the saved logs as well: `CI TESTS
  HELD: 13 of 13 rows` (the saved-log modes: `check_gate_log` 79 of 79, `check_toolchain` 33 of 33; `workflow_guards
  --local` 133 of 133, those three cases printed NOT RUN with that reason).
- Time, measured after the eighth review on that host alone (nothing else of this work running but a poll of the
  process list every 20 seconds during the audit), the two runs one after the other as the integrity job runs them:
  `run_all.py` in its CI form took 22 minutes 13 seconds (its slowest test, `test_inventory.py`, 16 minutes 48
  seconds, against the limit of 60 minutes a test), then `tools/ci/read_audit.py` 26 minutes 18 seconds (its longest
  run, the tests under its hook, about 26 minutes against its limit of 90 minutes a run; `test_inventory.py` about 20
  of them, by the poll, against the same 60 minutes a test: a margin of about 40), 48 minutes 31 seconds together
  against the integrity job's limit of 150 minutes, which also holds its shorter steps: margins of about 40, 43, 64
  and 101 minutes. On that host under heavy outside load the slowest test ran past 59 minutes under the hook. GitHub's
  runner: NOT MEASURED; its first run's step times are the measurement, and a slower runner narrows these margins.
- `tools/ci/read_audit.py` on this tree (the tests in their CI form and the 38 feature-row runs, under its hook): `READ
  AUDIT HELD: 3 of 3 rows`. The runs read 805 files inside the tree: 243 judge files, 416 freeze lists and files they
  list, 140 files the import's manifests name (Verðandi's records and notes beside its copies, `README.md`,
  `kernel/coq/ieee64/gate_ieee64.py`), 6 absent or in a temporary folder; and, as a copy's source, 47 folders. Of the
  183446 links, removals and moves they logged, none was of a file inside the tree outside a run's temporary folder.
  Every Python process the runs started outside a run's temporary folder ran under the hook (875 process starts were
  logged by process id and run; the count varies with process-id reuse). Of the 1716 starts the hook logged (5 of them
  changes to the environment, `os.putenv` and `os.unsetenv` in the read audit's own planted trees, logged as starts it
  cannot judge), 1536 were given the hook's environment: 859 Python processes and 677 runs of `git`, `bash` and `sh`,
  each in a run's temporary folder (no program that is not Python was started outside one); the other 180, in a run's
  temporary folder without it (the read audit's own planted trees and one probe), are not judged, nor are the 8
  imports and starts its planted trees make there that it cannot judge.
- The cases added after each review were written down before their first run, and each new check was seen to matter:
  with the check taken out, its test failed the cases expected of it and no other case it ran (after the sixth and
  seventh reviews the inventory's and the read audit's tests ran only that round's cases under each mutant; after the
  eighth, each mutant ran its whole test, every case of every round, the image step's two mutants run with `--local`,
  without the three carriage-return cases this host cannot run). After the first review: the checker as it
  was stops with a traceback on the two new gate-log plants; a feature row 4 that no longer refuses `Context`, an
  inventory without its new required-entries check and a judge that ignores `"held"` each turn their tests red. After
  the second review: an inventory without its stray-line checks, its statement-names row, its plain-file test and its
  case-folding comparison; a judge without its three new groups; run records that read a gate log's byte-order mark and
  timestamps as before, or take a folder name that starts with a digit; a gate-log check that takes a folder name in
  capitals; and a matrix step without its one-line guard, with one exception: without that guard, a matrix holding a
  carriage return after its first character was expected to fail its case, and the case held, because the matrix's
  pattern refuses that value too and its message holds the words the case checked (two cases added after the third
  review check the guard's own words, and do fail without it). After the third review: the statement-names row as it was
  (37 plants of other defining commands, constructors, fields, second names, unread commands and unparsable sentences
  pass it), the tables read as before (7 plants), listed paths read without their exact spelling (2 plants, on Windows:
  on Linux those paths are absent anyway), feature row 4 without its five new refusals (29 plants), the scripts' parsers
  taking `--help` and abbreviations (10 usage cases), run records accepting a log check of another row count (2), the
  toolchain check taking an expected file with no key (1), the verdict's fpenv step and the fpenv leg's own check
  accepting anything (7 and 3), the read audit without its reads row or its process check (3 and 2), and the
  `ANCHORS.md` step with its earlier reader (4). After the fourth review: the statement-names row splitting words as
  before (2 plants of a constructor's bar or a field's semicolon glued to a symbol) and without its printable-ASCII rule
  (1), the proved table found as before (3) or without its indented reading (1), the Successors heading counted at one
  level only (2), feature row 4 without its module type and functor refusal (10), and the read audit's hook taking a
  process given no environment as keeping the hook (1), judging a Python run by its first argument only (1), reading
  options as before (2), seeing `subprocess.Popen` only (2), and the read audit taking any JSON object as the inventory
  (4) or abbreviated options (1 usage case). One more, the read audit matching a run's first process by its process id
  alone, failed no case: on these plants it is an equivalent mutant, since none makes the system reuse a process id.
  After the fifth review: feature row 4 with the fourth round's module pattern (10 plants) or without its character rule
  (9), its file, load-path and plugin words (17) or its Class count (1); its test without its count of each predictions
  file's cases (a file whose P1 heading is misspelled then goes unseen); the inventory without its block-quote and
  list-item rule (5), its delimiter rows read at any indent (2), its heading text read as GitHub shows it (3), its check
  of successor-shaped tables (1), its header cells read as GitHub shows them (2) or its refusal of a folder named `ci`
  (1); the read audit's hook taking its folder anywhere on `PYTHONPATH` (1), not logging `os.putenv` and `os.unsetenv`
  (2), judging a shell given a command as any program (2), splitting a Windows command line as before (1), taking every
  temporary folder logged as new (1), keeping a long-path prefix (1), not resolving a path (1) or not judging
  `PYTHONHOME` (1); and the build step's base grep as before (3 build cases). Two of the read audit's are equivalent on
  Linux, where a command line is a list and `realpath` reads a leading "//" as "/". After the sixth review: the
  inventory without its Markdown subset's rule on characters (6 plants), on a heading's or a header's characters (4), on
  text beside a name (3), on the tables of `THEOREMS.md` (2), on HTML (7) or on list items (2), reading headings at
  three spaces of indent at most (2), or comparing its output paths as before (1); the read audit's hook with one busy
  flag for every thread (1: its plant holds one thread inside the hook while another reads, and in 20 runs each the
  shared flag missed that read every time and the fixed hook never), not logging a copy's source (2), reading its folder
  at each start (1), taking a logged folder that holds the tree as new (1), not logging links (2), removals (3), moves
  (1), an import of `multiprocessing` (1), forks (2) or an unpaired `_winapi.CreateProcess` (1); feature row 4 without
  its `From` rule (3), its new file commands (3) or its list-line rule (4); the image step's `FROM` count as before (4),
  or without its directive (1) or continuation (2) refusal; and the judge and the run records comparing an output path
  with a long-path prefix as before (1 each). One more, the hook without `shutil.rmtree`'s own event, failed no case: an
  equivalent mutant on these plants, declared before its run (the folder's last removal is logged too); three of these
  are equivalent on Linux (the copy and the two output paths: there `shutil.copy2` and `copytree` open their sources,
  and `realpath` reads a leading "//" as "/"), and one fails one case fewer there (the links: a read through a symbolic
  link is refused by its resolved path). After the seventh review: the inventory without its folding of look-alike
  headers and headings (4 plants), without its backslash rule (3), its rule of a backtick run left open on its line
  (1), its rule of a code span holding a `|` (1) or its character rule (5), or comparing its output paths as before
  (1); the judge and the run records resolving an output path as before (1 each); the read audit without its rule of a
  program that is not Python (1); and the image step without its byte rule (3), its first-line rule (2), its directive
  rule on every line (2) or its continuation rule for a comment or a blank line (2). The inventory without its
  code-fence rule failed one plant, not the four expected: a fence of three backticks is also a backtick run left open
  on its line, which the backtick rule refuses too; without both rules, all four and the plant of a code span across
  lines failed, as a second run, written down before it ran, expected. The three output-path mutants are equivalent on
  Linux, where there is no volume path. After the eighth review, each mutant running its whole test: the inventory
  without its rule of a `#` that can open a heading outside a top-level heading's line (5 plants), its rule of `[`
  (6), its fence after list markers (2), its junction test (2), its refusal of a linked folder (2), its test of two
  output paths that are one file (1) or its refusal of an output with another name (1); the judge without its refusal
  of a `--json` file with another name (1); the read audit's output guard as before (2); the run records' walk without
  its junction test (2); the toolchain probe printing a value with a line feed as it is (2: the probe case and its
  plant); and the image step's `FROM` count as before (3) or its byte rule without `-a` (1). Each failed exactly the
  cases written down and no other case of any round (the image step's two mutants without the three carriage-return
  cases this host cannot run); two are equivalent on Linux, where the plants are symbolic links,
  refused before too (the inventory's and the run records' junction tests). After the ninth, tenth and eleventh
  reviews, each mutant running its whole test: the inventory without its rule of a line of `=`, or of `-` with a colon
  allowed at either end, under a line that is not blank (11 plants: setext headings after an earlier underline, after
  a block start indented four spaces, starting on a list item's line and with trailing blanks; a setext heading and a
  `-` underline in `ANCHORS.md`; a table without pipes in both files), the inventory with that rule's pattern lacking
  the colon at the end of a `-` line (1: a table without pipes whose delimiter row is `-:`), the inventory with that
  rule reading a line of any white space as blank (1: a line of U+00A0 only above an underline, which then fails the
  Markdown subset row only, for its character), the read audit without its refusal of an existing `--json` file with
  another name (1, its message showing the file written through its other name) and the run records' walk without its
  record of a folder it cannot list (1). Each failed exactly the cases written down and no other case; the inventory's
  first such run, after the ninth, also failed its predictions row, since a decoy had been written under a plant's
  prefix, and the decoy was renamed before any run on the honest tree had a result (a stopped run had started the
  tests there; none was kept). On the first run of the old inventory
  test against the new `#` rule one frozen plant, a lone carriage return before a Successors heading, also failed the
  successor row; the rule now leaves out a line the character rule refuses, and the plant held as first predicted.
  On the first run after the fifth review one earlier inventory plant, a tree
  with nothing in it, also failed the new block-quote row; that row is now not printed when `THEOREMS.md` cannot be
  read, and the plant held as first predicted. On the first runs after the second review, which this host cut short part
  way through the inventory test (it stopped starting processes), two earlier inventory plants also failed the new
  statement-names row, which then read its statement files from `THEOREMS.md`; the row now finds them from the gated
  folders, and both plants held as first predicted. On the first run after the third review one case of the read audit's
  test missed its prediction: a Python process started with `-I` was not seen as one, because Windows hands the hook a
  command line as one string; the hook now splits it, and the case held on its next run.
- The two workflows' steps, run in order by Git Bash in a scratch git repository holding a copy of the tree's
  workflows, tools, `ci/`, `kernel/` and Verðandi's copies, with the actions emulated, `docker` replaced by a
  stand-in that replays CI run 44223174587's gate consoles and writes a `Closure.out` built from each, and the fpenv
  job's two legs run with stand-ins for their compilers and check. On the tree as first proposed, after the first
  review and after each later one up to the eighth but the fifth and the seventh (whose changes to the workflows,
  the build step's
  base grep and the image step's checks of the Dockerfile, with their comments, `test_workflow_guards.py` runs), the
  honest run was green
  through `MathKernel verdict` (`RUN RECORDS HELD: 11 of 11 rows` over 13 records; on the later trees each gate's
  evidence also held its `Closure.out`, and on the last four each
  fpenv leg kept its evidence and the verdict read both), and every planted run failed at exactly the steps predicted
  for it before it first ran: a missing `MK_ANCHOR_CI`, a wrong folder anchor, a gate loading another image id, a
  base image other than the pinned one, another `coqc` hash in the gate jobs, a console saying one library came from
  the log, a tracked `.pyc`, a failed fpenv job, a feature-row plant in the integrity workflow, and on the last four
  trees (after the third, fourth, sixth and eighth reviews) an arm64 fpenv leg that failed, the same leg with the
  job's
  combined result read as a success (the verdict
  still fails, at that leg's missing evidence), and a leg whose check printed a FAILED line and exited 0. For two of
  them the first
  prediction missed one step (the verdict job's download of an artifact never uploaded fails too); the corrected
  predictions were written before those runs were made again. The rehearsal also found and fixed four defects of its
  own and of the workflows. On the copy the integrity workflow's manifests step failed, as it needs the whole tree.
  Its other steps held on the tree after the first review (its tests `CI TESTS HELD: 8 of 8 rows`); on the later
  trees the tests failed too, only on the carriage-return cases above (`CI TESTS FAILED: 1 of 9 rows`, then `1 of 11
  rows`), so that scenario missed its prediction, written for the first tree, which named the manifests step only;
  after the third, fourth and sixth reviews its read-audit step held; after the eighth, the rehearsal's own limit of
  one hour
  a step cut that step twice while other work shared the host, and the read audit, run directly on that tree, held
  (above). Not run there: GitHub, the actions themselves, docker, the image's build, opam, Coq, the fpenv job's own
  check.

### What the hardened workflows still do not show

The section "What a green run shows, and what it does not" below holds for them too, apart from its paragraph on
required checks, which the verdict job answers.

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
limited time; a run that is to be cited is saved with them. A run of the hardened workflows that is to be cited is
saved with its `run-summary-attempt<N>`, `run-record-<folder>-attempt<N>`, `gate-evidence-<folder>-attempt<N>` and
`fpenv-<runner>-attempt<N>` artifacts, because GitHub deletes a
repository's workflow runs, logs and artifacts when its retention period ends (90 days by default). That period
covered artifacts and logs; from 1 October 2026 it covers checks, workflow runs and commit statuses too (READ by a
review of this file, in GitHub's documentation of a repository's Actions settings:
<https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository>).
