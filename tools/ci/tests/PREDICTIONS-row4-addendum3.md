# Predictions for feature row 4 after the fifth review: fail closed (addendum 3)

Written by the assistant on 2026-11-20, after review round 5 and before any run of feature row 4 on these plants; no
line changes after that run. `tools/ci/tests/test_feature_row4.py` reads the P1 table below together with the P1 and
P5 tables of `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` and the P1 tables of
`tools/ci/tests/PREDICTIONS-row4-addendum1.md` and `PREDICTIONS-row4-addendum2.md` (all three stay as they were); a
case is named in one of them only, and each of the four files must give at least one P1 case.

Why. Rounds 4 and 5 each found a spelling of a module type or functor that the row's patterns missed (a name after
`Import`, then a name that starts with a letter outside ASCII). A pattern that lists spellings is closed by the next
spelling it does not list, so version 4 now accepts only what it names and refuses what its ASCII patterns cannot
read:

- A character outside printable ASCII, tab, line feed, carriage return and form feed, anywhere in a file, in code,
  comments and strings alike, is refused (class `a character outside printable ASCII`, one REFUSED line for each).
- Every use of the word `Module` in code is refused (class `module type or functor`, as before) but the plain
  `Module <name>.`, `Module Import <name>.` and `Module Export <name>.`, the name written in ASCII
  (`[A-Za-z_][A-Za-z0-9_']*`); `Include` stays refused. So `Module Type`, `Declare Module`, a functor's parameters, a
  functor applied, a module ascribed, import categories and a name the row cannot read are all refused. This replaces
  addendum 2's module refusal, whose cases keep their predicted verdicts and classes.
- The commands that read another file (`Load`), change the load path (`Add LoadPath`, `Add Rec LoadPath`) or the
  working folder (`Cd`), write files (`Redirect`, every Extraction command and option) or load a plugin, whose code
  runs (`Declare ML Module`, `Add ML Path`, `Add Rec ML Path`), are refused by their words, `Load`, `LoadPath`, `Cd`,
  `Redirect`, `Extraction`, `Extract` and `ML`, wherever they stand in code (class `file, load path or plugin
  command`). `Declare ML Module` was refused already by version 3's `plugin` entry; its word `Module`, followed by a
  blanked string, is no plain module either, so its plant is refused under three classes.
- `Class` declarations are counted on the reported line (`class (allowed: plain declarations)`), as version 3 counts
  the other plain declarations; a count is not a row, so no exit changes.

Version 4's REFUSED list now begins with version 3's twenty entries, unchanged, and has fourteen more (six of
2026-11-18, five after the third review, one after the fourth, replaced after the fifth by the plain-module rule, and
two after the fifth: the file, load-path and plugin words, and the character rule); its REPORTED list begins with
version 3's three entries, unchanged, and has one more. This supersedes P4 of the 2026-11-18 file ("its `REPORTED`
... equal version 3's") and the count of twelve in addendum 2; their other claims stand. P3 of the first file (version
4 exits as version 3 on the 43 files of `plants/`, `plants2/` and `plants3/`) is predicted to hold still: no honest
file there holds a refused construct of this addendum (a count before writing it found the new rules only in
`refuse3_functor.v`, `refuse3_module_type.v` and `refuse3_plugin.v`, which version 3 refuses too).

The plants are written by `make_feature_plants4.py` into `plants4/` (PLANTS4). The seven module spellings of review 5
are `refuse4_module_alpha_functor`, `_alpha_applied`, `_beta_ascribed`, `_import_gamma`, `_e_acute_sub`,
`_combining_mark` (a combining accent after an ASCII letter) and `_import_categories` (ASCII only). Review 5's plain
module decoy named with a Greek letter is refused under this round's rules, so it is the plant
`refuse4_module_alpha_plain`, and the decoy `decoy4_module_plain_forms` holds the plain forms in ASCII (`Module M.`,
`Module Import N.`, `Module Export P'.`, and `Module`, its name and its period on three lines). `over4_*` are known
over-refusals (`Module'` and `Cd` as names). The decoys hold the words in comments, in a string and inside longer
identifiers (`Loader`, `Cdx`, `MLx` and the others), and lower-case `load` and `cd`.

## P1. Version 4 on the plants added after the fifth review

Each case is run from `kernel/hardening/features` as `python -B feature_row4.py plants4 <case>.v`. Predicted, as in the
first file: the exit code; the verdict line; the set of rows that fail; the set of classes on the REFUSED lines. The
seventh column is new: `*` checks nothing more; any other value is the text the line `reported, not refused
(occurrences): ` must end with, exactly.

| case | arguments | exit | verdict | failing rows | classes | reported |
|---|---|---|---|---|---|---|
| refuse4_module_alpha_functor | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_alpha_applied | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_beta_ascribed | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_import_gamma | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_e_acute_sub | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_combining_mark | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_import_categories | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor | * |
| refuse4_module_alpha_plain | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor; a character outside printable ASCII | * |
| refuse4_module_type | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor | * |
| refuse4_declare_module | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor | * |
| refuse4_nonascii_comment | (plant) | 1 | FAILED 1 of 2 | (plant) | a character outside printable ASCII | * |
| refuse4_nonascii_string | (plant) | 1 | FAILED 1 of 2 | (plant) | a character outside printable ASCII | * |
| over4_module_prime_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor | * |
| decoy4_module_plain_forms | (plant) | 0 | HELD 2 of 2 | - | - | * |
| decoy4_module_word_comment | (plant) | 0 | HELD 2 of 2 | - | - | * |
| refuse4_load_absolute | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_load_ident | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_add_loadpath | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_add_rec_loadpath | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_cd | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_redirect | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_extraction | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_recursive_extraction | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_separate_extraction | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_extraction_library | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_extract_constant | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_extract_inductive | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_extraction_option | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_declare_ml_module | (plant) | 1 | FAILED 1 of 2 | (plant) | plugin; file, load path or plugin command; module type or functor | * |
| refuse4_add_ml_path | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| refuse4_add_rec_ml_path | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| over4_cd_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | file, load path or plugin command | * |
| decoy4_load_comment | (plant) | 0 | HELD 2 of 2 | - | - | * |
| decoy4_load_string | (plant) | 0 | HELD 2 of 2 | - | - | * |
| decoy4_load_identifiers | (plant) | 0 | HELD 2 of 2 | - | - | * |
| decoy4_class_reported | (plant) | 0 | HELD 2 of 2 | - | - | class (allowed: plain declarations) 1 |
