# Predictions for the feature row's version 4 (written by the assistant on 2026-11-18, before any run of it)

Version 4 (`feature_row4.py`) keeps version 3's lexer and refusals (copied unchanged; `feature_row3.py` stays beside it)
and refuses six more constructs, each a way to assume or to enter Program mode that version 3 did not refuse:
`Conjectures`, a `Context` command, `Declare Instance`, `Admit Obligations`, the obligation commands of Program
(`Obligation`, `Next Obligation`, `Final Obligation`, `Solve Obligations`, `Solve All Obligations`, `Obligation
Tactic`) and a `program` attribute inside `#[...]`. It also checks its input: with `--list`, a list in the form of
`FROZEN4.txt` with plain relative paths, none twice, at least one `.v` file outside `plants/` to scan, and each scanned
file's sha256 equal to the listed one. It prints one row per input and per file, and the verdict
`FEATURE ROW 4 HELD: n of n rows` or `FEATURE ROW 4 FAILED: k of n rows failed`. The plants are in `plants4/`, written
by `make_feature_plants4.py`.

Census before writing (a plain search of the raw text, comments included, of the 494 `.v` files of this tree):
`Conjectures`, `Context`, `Declare Instance`, `Admit`, `Obligation` and `Attributes` occur in none; `program` occurs
only in the prose of comments; the attributes used are `#[local]` (90) and `#[bypass_check(guard)]` (16, all in
plants). Lower-case `context` occurs 29 times (Ltac patterns) and stays allowed.

## P1. Version 4 on its plants

Each case is run from `kernel/hardening/features` as `python -B feature_row4.py <arguments>`. Predicted: the exit code;
the verdict line; the set of rows that fail; the set of classes on the REFUSED lines, exactly (`-`: none). `(plant)`
as arguments means `plants4 <case>.v`, and as a failing row `<case>.v`. `<tmp>` is a temporary folder the check
writes: `bad4.v` holds the bytes `ff 0a`, `nonascii4.txt` the bytes `e9 0a`.

| case | arguments | exit | verdict | failing rows | classes |
|---|---|---|---|---|---|
| refuse4_conjectures | (plant) | 1 | FAILED 1 of 2 | (plant) | Conjectures assumption |
| refuse4_context | (plant) | 1 | FAILED 1 of 2 | (plant) | Context command |
| refuse4_declare_instance | (plant) | 1 | FAILED 1 of 2 | (plant) | Declare Instance |
| refuse4_admit_obligations | (plant) | 1 | FAILED 1 of 2 | (plant) | Admit Obligations; Program obligation command |
| refuse4_obligation | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_next_obligation | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_final_obligation | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_solve_obligations | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_solve_all_obligations | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_obligation_tactic | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| refuse4_program_attribute | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_program_attribute_list | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| refuse4_program_attribute_value | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| evade4_context_after_string_in_comment | (plant) | 1 | FAILED 1 of 2 | (plant) | Context command |
| evade4_conjectures_after_string_in_comment | (plant) | 1 | FAILED 1 of 2 | (plant) | Conjectures assumption |
| evade4_split_declare_instance | (plant) | 1 | FAILED 1 of 2 | (plant) | Declare Instance |
| evade4_split_solve_all_obligations | (plant) | 1 | FAILED 1 of 2 | (plant) | Program obligation command |
| evade4_program_attribute_bracket_in_comment | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| evade4_program_attribute_bracket_in_string | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| evade4_program_attribute_multiline | (plant) | 1 | FAILED 1 of 2 | (plant) | program attribute |
| over4_prime_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | Context command |
| over4_bare_identifier | (plant) | 1 | FAILED 1 of 2 | (plant) | Context command |
| decoy4_comment | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_string | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_string_in_comment | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_identifiers | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_lowercase | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_other_attributes | (plant) | 0 | HELD 2 of 2 | - | - |
| decoy4_instances | (plant) | 0 | HELD 2 of 2 | - | - |
| list_honest | `plants4 --list plants4/input4_honest.txt` | 0 | HELD 3 of 3 | - | - |
| list_empty | `plants4 --list plants4/input4_empty.txt` | 1 | FAILED 1 of 1 | input | - |
| list_plants_only | `plants4 --list plants4/input4_plants_only.txt` | 1 | FAILED 1 of 1 | input | - |
| list_bad_line | `plants4 --list plants4/input4_bad_line.txt` | 1 | FAILED 1 of 2 | input | - |
| list_dotdot | `plants4 --list plants4/input4_dotdot.txt` | 1 | FAILED 1 of 2 | input | - |
| list_absolute | `plants4 --list plants4/input4_absolute.txt` | 1 | FAILED 1 of 2 | input | - |
| list_backslash | `plants4 --list plants4/input4_backslash.txt` | 1 | FAILED 1 of 2 | input | - |
| list_duplicate | `plants4 --list plants4/input4_duplicate.txt` | 1 | FAILED 1 of 2 | input | - |
| list_hash_mismatch | `plants4 --list plants4/input4_hash_mismatch.txt` | 1 | FAILED 1 of 3 | decoy4_comment.v | - |
| list_missing_file | `plants4 --list plants4/input4_missing_file.txt` | 1 | FAILED 1 of 3 | absent4.v | - |
| list_refused | `plants4 --list plants4/input4_refused.txt` | 1 | FAILED 1 of 3 | refuse4_context.v | Context command |
| list_missing | `plants4 --list plants4/no-such-list.txt` | 1 | FAILED 1 of 1 | input | - |
| list_not_ascii | `<tmp> --list <tmp>/nonascii4.txt` | 1 | FAILED 1 of 1 | input | - |
| file_not_utf8 | `<tmp> bad4.v` | 1 | FAILED 1 of 2 | bad4.v | - |
| root_missing | `no-such-root decoy4_comment.v` | 1 | FAILED 2 of 2 | input; decoy4_comment.v | - |
| args_duplicate | `plants4 decoy4_comment.v decoy4_comment.v` | 1 | FAILED 1 of 2 | input | - |
| args_mixed | `plants4 decoy4_comment.v refuse4_context.v` | 1 | FAILED 1 of 3 | refuse4_context.v | Context command |
| usage_root_only | `plants4` | 2 | usage | - | - |
| usage_list_no_file | `plants4 --list` | 2 | usage | - | - |
| usage_list_two_files | `plants4 --list plants4/input4_honest.txt plants4/input4_empty.txt` | 2 | usage | - | - |
| usage_unknown_option | `plants4 --foo decoy4_comment.v` | 2 | usage | - | - |
| usage_option_as_root | `--list plants4/input4_honest.txt` | 2 | usage | - | - |

`over4_*` are known over-refusals, predicted refused: Coq reads `Context'` and `Context` as plain names there, and the
row refuses them because it matches words, not command positions (it fails closed).

## P2. Each gap is real

Version 3 (`feature_row3.py plants4 <plant>`) exits 0 on every `refuse4_*`, `evade4_*` and `over4_*` plant: none of
them is refused by version 3, so none is an equivalent mutant of it.

## P3. Version 3's verdicts are kept

On each of the 43 `.v` files of `plants/`, `plants2/` and `plants3/` (run as `<folder> <file>`), version 4 exits with
the same code as version 3.

## P4. Version 3's rules are copied unchanged

Compared as parsed code: version 4's `REFUSED` begins with version 3's twenty entries, in order and unchanged, and has
six more; its `REPORTED` and its lexer `strip` equal version 3's.

## P5. The tree's freeze lists

Run from `kernel/hardening/features` as `python -B feature_row4.py <root> --list <root>/<folder>/FROZEN4.txt`; the
count is one input row and one row per `.v` file of the list outside `plants/`.

| list | root | folder | exit | verdict |
|---|---|---|---|---|
| kernel compose | ../../coq | compose | 0 | HELD 33 of 33 |
| kernel cos32 | ../../coq | cos32 | 0 | HELD 23 of 23 |
| kernel exp32 | ../../coq | exp32 | 0 | HELD 15 of 15 |
| kernel exp32r | ../../coq | exp32r | 0 | HELD 19 of 19 |
| kernel f32 | ../../coq | f32 | 0 | HELD 4 of 4 |
| kernel ieee64 | ../../coq | ieee64 | 0 | HELD 30 of 30 |
| kernel log32 | ../../coq | log32 | 0 | HELD 18 of 18 |
| kernel p32 | ../../coq | p32 | 0 | HELD 10 of 10 |
| kernel p32r | ../../coq | p32r | 0 | HELD 13 of 13 |
| kernel sin32 | ../../coq | sin32 | 0 | HELD 18 of 18 |
| kernel sincos32 | ../../coq | sincos32 | 0 | HELD 29 of 29 |
| kernel sincos32i | ../../coq | sincos32i | 0 | HELD 51 of 51 |
| kernel sincos32z | ../../coq | sincos32z | 0 | HELD 55 of 55 |
| mirror exp32 | ../../../verdandi/mathkernel/F32 | exp32 | 0 | HELD 15 of 15 |
| mirror exp32r | ../../../verdandi/mathkernel/F32 | exp32r | 0 | HELD 19 of 19 |
| mirror f32 | ../../../verdandi/mathkernel/F32 | f32 | 0 | HELD 4 of 4 |
| mirror ieee64 | ../../../verdandi/mathkernel/F32 | ieee64 | 0 | HELD 30 of 30 |
| mirror p32 | ../../../verdandi/mathkernel/F32 | p32 | 0 | HELD 10 of 10 |
| mirror p32r | ../../../verdandi/mathkernel/F32 | p32r | 0 | HELD 13 of 13 |
