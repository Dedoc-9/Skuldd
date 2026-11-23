# Predictions for feature row 4 after the sixth review (addendum 4)

Written by the assistant on 2026-11-20, after review round 6 and before any run of feature row 4 on these plants; no
line changes after that run. `tools/ci/tests/test_feature_row4.py` reads the P1 table below together with the P1 and
P5 tables of `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` and the P1 tables of
`tools/ci/tests/PREDICTIONS-row4-addendum1.md`, `PREDICTIONS-row4-addendum2.md` and `PREDICTIONS-row4-addendum3.md`
(all four stay as they were); a case is named in one of them only, and each of the five files must give at least one
P1 case.

Why. Review 6 found file commands outside the row's list of words (`From Coq Extra Dependency "x.txt" as xdep.`, and
`Restore State`, `Write State`, which load or save a whole environment from a file), and a comment line of a list
ended by a separator that version 3 reads as a line end, so that the entry after it was read by version 3 and skipped
by version 4. So:

- The entry `file, load path or plugin command` also refuses `Extra Dependency` and `Restore State` or `Write State`
  (the words, wherever they stand in code; a blank, a line end or a comment may stand between the two words).
- A new entry, `From not followed by Require`, fails closed on `From`: a `From` in code must be followed by a dotted
  ASCII name and then `Require` (`From Coq Require Import Reals.`); any other `From` is refused. A count before
  writing this found 344 uses of From in the 95 .v files of the tree outside the plant folders, 331 in the files the 19
  freeze lists name for row 4 to scan, 1343 in the plant files those lists name and 14 in the pilot's two statement
  files, every one `From <name> Require`; one each in `plants2/` and `plants3/` (the same form) and none in `plants/`
  or `plants4/`. An identifier named `From` is refused too (a known over-refusal, `over4_from_identifier`).
- The input row refuses a list line, a comment's too, that holds a character other than printable ASCII and tab once
  its final carriage return is taken off (so a list in CR LF still reads), before it tests for a comment. The 19 lists
  and the eleven `input4_*.txt` lists of version 4's first plants hold no such line (counted before writing this).

Version 4's REFUSED list now begins with version 3's twenty entries, unchanged, and has fifteen more (addendum 3's
fourteen, the file entry among them widened in place, and the From entry); its REPORTED list is as addendum 3 left it.
This supersedes addendum 3's count of fourteen; its other claims stand. P3 of the first file (version 4 exits as
version 3 on the 43 files of `plants/`, `plants2/` and `plants3/`) is predicted to hold still: those files hold no
`From` but `From <name> Require`, and none of the new words.

The plants are written by `make_feature_plants4.py` into `plants4/` (PLANTS5): `refuse4_extra_dependency` (both new
refusals), `refuse4_restore_state`, `refuse4_write_state`, `refuse4_from_import` (`From Coq Import Reals.`), the known
over-refusal `over4_from_identifier` (`Definition From : nat := 0.`), the decoys `decoy4_state_comment` and
`decoy4_state_string` (the words in a comment, in a string) and `decoy4_from_require` (`From Coq Require Import
Reals.`, a comment between From and its name, and a dotted name), and the lists `input4_hidden_cr.txt`,
`input4_hidden_ff.txt`, `input4_hidden_rs.txt`, `input4_hidden_vt.txt` (a comment line `# hidden` ended by a carriage
return, a form feed, a record separator or a vertical tab, then the entry of `refuse4_context.v`, then a line feed and
the entry of `decoy4_identifiers.v`: review 6's F11, F12, F12b, F12c) and `input4_hidden_lf.txt` (the same with a line
feed: F11c, the control).

## P1. Version 4 on the plants added after the sixth review

Each case is run from `kernel/hardening/features` as addendum 3 says (`(plant)` stands for `plants4 <case>.v`).
Predicted: the exit code; the verdict line; the set of rows that fail; the set of classes on the REFUSED lines; the
reported line (`*`: not checked).

| case | arguments | exit | verdict | failing rows | classes | reported |
|---|---|---|---|---|---|---|
| refuse4_extra_dependency | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command; From not followed by Require | * |
| refuse4_restore_state | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_write_state | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_from_import | (plant) | 1 | FAILED 1 of 2 | (plant) | From not followed by Require | * |
| over4_from_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | From not followed by Require | * |
| decoy4_state_comment | (plant) | 0 | HELD 2 of 2 | - | - | none |
| decoy4_state_string | (plant) | 0 | HELD 2 of 2 | - | - | none |
| decoy4_from_require | (plant) | 0 | HELD 2 of 2 | - | - | none |
| list_hidden_cr | `plants4 --list plants4/input4_hidden_cr.txt` | 1 | FAILED 1 of 2 | input | - | * |
| list_hidden_ff | `plants4 --list plants4/input4_hidden_ff.txt` | 1 | FAILED 1 of 2 | input | - | * |
| list_hidden_rs | `plants4 --list plants4/input4_hidden_rs.txt` | 1 | FAILED 1 of 2 | input | - | * |
| list_hidden_vt | `plants4 --list plants4/input4_hidden_vt.txt` | 1 | FAILED 1 of 2 | input | - | * |
| list_hidden_lf | `plants4 --list plants4/input4_hidden_lf.txt` | 1 | FAILED 1 of 3 | refuse4_context.v | Context command | * |
