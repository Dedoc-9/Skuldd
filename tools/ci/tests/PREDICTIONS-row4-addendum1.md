# Predictions for feature row 4 after review: the other spellings of the census's triggers (addendum 1)

Written by the assistant on 2026-11-20, after review round 3 and before any run of feature row 4 on these plants; no
line changes after that run. `tools/ci/tests/test_feature_row4.py` reads the P1 table below together with the P1 and
P5 tables of `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` (which stays as it was); a case is named in one
of them only.

Version 4 now refuses, besides version 3's constructs and the six of 2026-11-18, five more: a `universes` attribute
anywhere in an attribute list and the prefix `Monomorphic`; a `projections` attribute; a `using` attribute and the
option `Default Proof Using`; a `private` attribute and the prefix `Private`; and an inline universe binder or instance
`@{`. Each plant below is one spelling in one position, written by `make_feature_plants4.py` into `plants4/`:
`refuse4_attr_<attribute>_<position>` puts the attribute first in `#[...]`, after `local`, with spaces inside the
brackets, in a second list after `#[local]`, or after `local` across lines; `refuse4_value_*` gives another value,
after `local`; `refuse4_prefix_*` is a prefix; `refuse4_option_*` the option; `refuse4_universe_binder` the binder.
The bypass_check and program plants were refused before this change (by version 2's word and version 4's program
attribute) and show the other positions are refused too. `over4_private_identifier` is a known over-refusal (Coq reads
`Private` there as a plain name; the row matches words). The decoys hold the words outside an attribute list, inside
strings and inside comments, and a `@` not followed by `{`.

Version 4's REFUSED list now begins with version 3's twenty entries, unchanged, and has eleven more (six of 2026-11-18,
five after review): this supersedes the count in P4 of the 2026-11-18 file, whose other claims stand.

## P1. Version 4 on the plants added after review

Each case is run from `kernel/hardening/features` as `python -B feature_row4.py plants4 <case>.v`. Predicted, as in the
first file: the exit code; the verdict line; the set of rows that fail; the set of classes on the REFUSED lines.

| case | arguments | exit | verdict | failing rows | classes |
|---|---|---|---|---|---|
| refuse4_attr_bypass_check_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_attr_bypass_check_first | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_attr_bypass_check_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_attr_bypass_check_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_attr_bypass_check_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_attr_private_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_attr_private_first | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_attr_private_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_attr_private_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_attr_private_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_attr_program_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_attr_program_first | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_attr_program_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_attr_program_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_attr_program_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_attr_projections_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_attr_projections_first | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_attr_projections_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_attr_projections_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_attr_projections_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_attr_universes_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_attr_universes_first | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_attr_universes_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_attr_universes_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_attr_universes_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_attr_using_after_local | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_attr_using_first | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_attr_using_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_attr_using_second_list | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_attr_using_spaced | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_value_universes_polymorphic_yes | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_value_universes_cumulative | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_value_universes_template | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_value_universes_monomorphic | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_value_projections_primitive_yes | (plant) | 1 | FAILED 1 of 2 | (plant) | primitive projections |
| refuse4_value_bypass_check_positivity | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag |
| refuse4_value_bypass_check_universes | (plant) | 1 | FAILED 1 of 2 | (plant) | checking flag; universe polymorphism |
| refuse4_value_program_no | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_prefix_polymorphic | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_prefix_monomorphic | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_prefix_cumulative | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_prefix_noncumulative | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_prefix_private | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_prefix_program | (plant) | 1 | FAILED 1 of 2 | (plant) | recursive definition |
| refuse4_prefix_local_polymorphic | (plant) | 1 | FAILED 1 of 2 | (plant) | universe polymorphism |
| refuse4_prefix_attribute_private | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| refuse4_option_default_proof_using | (plant) | 1 | FAILED 1 of 2 | (plant) | abstract or Proof using |
| refuse4_universe_binder | (plant) | 1 | FAILED 1 of 2 | (plant) | universe declaration |
| over4_private_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | private inductive type |
| decoy4_attribute_words | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_attribute_strings | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_attribute_comment | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_at_sign | (plant) | 0 | HELD 2 of 2 | - | - |
