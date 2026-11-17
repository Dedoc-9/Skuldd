# Predictions for the feature row's version 3 (written by the assistant on 2026-11-17, before any run of it)

Version 3 (`feature_row3.py`) keeps version 2's lexer and refusals and adds refusals for the triggers of the upstream
critical-bugs entries that affect Coq 8.20.1 and that the tier does not use (census `trigger_census.py`, 62 tier
sources and draft M: none of them occurs; `vm_compute` occurs 6 times and a plain `Inductive` and `Record` twice each,
and those stay allowed). The plants are in `plants3/`, written by `make_feature_plants3.py`.

- Q1. Each `refuse3_*` plant: version 3 FAILED (exit 1) with at least one refused occurrence of its own class.
- Q2. Each `decoy3_*` plant: version 3 HELD (exit 0).
- Q3. Version 3 on version 2's twenty plants (`plants/` and `plants2/`): every plant version 2 refused is refused;
  every decoy version 2 held is held.
- Q4. Version 3 on the tier: HELD on the closures of sincos32z (54) and sincos32i (50), on draft M, and on the 62 .v
  files of `mkf-ext` outside `plants/` and `out4/`.
