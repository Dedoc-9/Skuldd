# Predictions for feature row 4 after the fourth review: module types and functors (addendum 2)

Written by the assistant on 2026-11-20, after review round 4 and before any run of feature row 4 on these plants; no
line changes after that run. `tools/ci/tests/test_feature_row4.py` reads the P1 table below together with the P1 and
P5 tables of `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` and the P1 table of
`tools/ci/tests/PREDICTIONS-row4-addendum1.md` (both stay as they were); a case is named in one of them only.

Version 4 now refuses one more construct, in the class `module type or functor` that version 3 already uses: a
functor applied or a module ascribed (`Module <name>` followed by `:=`, `:` or `<:`, also after `Import` or
`Export`), a functor's parameters after `Import` or `Export`, and `Include`. The census
(`kernel/hardening/features/trigger_census.py`) names module types and functors as a trigger; version 3 refused only
`Module Type`, `Declare Module`, `Functor` and a functor's parameters directly after its name. Each plant below is
one spelling, written by `make_feature_plants4.py` into `plants4/`. `evade4_module_comment` hides the spelling behind
comments, which the row blanks. `over4_include_identifier` is a known over-refusal (the row matches the word wherever
it stands; whether Coq accepts it as a name is not checked). The decoys hold a plain module (`Module M.` ... `End
M.`, `Import M.`), the words inside longer identifiers, and the spellings inside a comment and a string.

Version 4's REFUSED list now begins with version 3's twenty entries, unchanged, and has twelve more (six of
2026-11-18, five after the third review, one after the fourth): this supersedes the count in P4 of the 2026-11-18
file and in addendum 1, whose other claims stand.

## P1. Version 4 on the plants added after the fourth review

Each case is run from `kernel/hardening/features` as `python -B feature_row4.py plants4 <case>.v`. Predicted, as in the
first file: the exit code; the verdict line; the set of rows that fail; the set of classes on the REFUSED lines.

| case | arguments | exit | verdict | failing rows | classes |
|---|---|---|---|---|---|
| refuse4_module_functor_applied | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_ascribed | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_ascribed_sub | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_interactive_sub | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_include | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_import_functor | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_export_applied | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| refuse4_module_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| evade4_module_comment | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| over4_include_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | module type or functor |
| decoy4_module_plain | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_module_words | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_module_comment_string | (plant) | 0 | HELD 2 of 2 | - | - |
