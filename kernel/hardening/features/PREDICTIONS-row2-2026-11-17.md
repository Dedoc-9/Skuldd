# Predictions for the feature row's version 2 (written by the assistant on 2026-11-17, before any run of it)

Version 1 (`feature_row.py`, sha256 3e4bc3917554c51ff9c0b3be2c20f946a90ec2a48149983b4751749a17a484ab) scans one line
at a time and does not lex strings inside comments. Version 2 is `feature_row2.py`. The plants in `plants2/` are
written by `make_feature_plants2.py`.

Python rows (this host's Python, standard library):
- P1. Version 1 on each of the four `evade_*` plants: HELD (exit 0). This is the gap being shown.
- P2. Version 2 on each `evade_*` plant: FAILED (exit 1), with these refused occurrences: split_unset_guard 1 (Unset
  Guard Checking), split_definitional_uip 1 (Set Definitional UIP), string_in_comment 1 (Unset Guard Checking),
  hidden_fixpoint 2 (Unset Guard Checking; Fixpoint).
- P3. Both versions on each of the two `decoy_*` plants of `plants2/`: HELD.
- P4. Version 2 on version 1's fourteen plants (`plants/`): the same verdict as version 1 for each (11 refused, 3
  held).
- P5. Version 2 on the tier: HELD on the 54 sources of `mkf-ext\sincos32z\FROZEN4.txt` (plants excluded), HELD on
  draft M, HELD on every .v of `mkf-ext` outside `plants/` and `out4/` (62 files). No refused occurrence anywhere.

Coq (one container, image by ID, `--rm --network none`, plants2 mounted read-only):
- P6. Every plant of `plants2/` compiles: coqc exit 0, six of six.
- P7. Each `evade_*` plant with a probe appended (`Test Guard Checking.` and `Test Definitional UIP.`) compiles and
  prints that the flag the plant changed has its changed value: guard checking off for split_unset_guard,
  string_in_comment and hidden_fixpoint (whose plant sets it back, so its probe shows it on), Definitional UIP on for
  split_definitional_uip. The exact wording of Coq's message is not predicted.
- P8. A recursive coqchk of the hidden_fixpoint plant exits 0 and its summary names `loop` under "Constants/Inductives
  relying on unsafe (co)fixpoints"; the harness's own summary reader (`harness.py`, read_chk) refuses that summary.
  P8 is the least certain: if coqchk instead rejects the fixpoint or lists nothing, that is reported as found.
