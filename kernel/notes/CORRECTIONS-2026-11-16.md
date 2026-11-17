# Corrections note, 2026-11-16 (dated note beside frozen and anchored files; no byte of any of them is changed)

Written by the assistant (main session) after the overclaim audit of Turn 227. Each line names a text that is wrong,
stale or says more than its evidence, where it stands, and the wording that is right. The files themselves stay as
they are: both statements are frozen by the owner's rulings (build log, Turns 223 and 225) and the candidate
folders are on anchored freeze lists. "own" = checked by the main session this turn; "reported" = found by the
audit agent, not re-checked.

## Frozen statement files (comments only; no definition is affected)

1. `src\SINCOS32_IEEE_Zero_Statement.v` and `mkf-ext\sincos32z\` copy, lines 8-11: "+0 at every negative whole
   number". WRONG for magnitudes of 2^23 and above, where the unstepped sine returns x * 0, a zero with the sign of
   x (the build log, Turn 224, says so). Right: "+0 at every negative whole number below 2^23 that was measured
   (exhausted to 2^20, sampled above)". own.
2. Same file, lines 27-28: "the proof may show there is no such result". The proof does not show it (agent B's
   report; `Zero.v` read from line 20 on by the main session). Right: "no proof shows it; it is argued, and
   measured on samples". own.
3. Both statement files open with "DRAFT 3" / "DRAFT". STALE: both are frozen candidates, proved as candidates in
   Turn 226, not adopted. own.
4. `STATEMENT-FROZEN.txt` and `STATEMENT-ZERO-FROZEN.txt`, line 2: "not proved". STALE since Turn 226: proved as
   candidates under the gate, not adopted. own.

## Anchored files of the two candidate folders

5. `mkf-ext\sincos32i\FROZEN4.txt` and `mkf-ext\sincos32z\FROZEN4.txt`, line 1: "the older FROZEN.txt, written
   before the proofs, is kept beside it". FALSE here: neither folder has a FROZEN.txt (the sentence is
   `gate\freeze4.py`'s fixed heading). The only pre-proof records are `STATEMENT-FROZEN.txt` and
   `STATEMENT-ZERO-FROZEN.txt`, written by the author's session; that the statements were fixed before their
   proofs is therefore DECLARED (author's records and file times), not shown by anything the gate reads. own.
6. `mkf-ext\sincos32i\gate.json`, plant `shape-narrow-add`: "about 1.89e-29 for 2^-149". The frozen shape's value
   at x = 2^-149 is 6 * 2^-149 (MEASURED this turn in Coq at primitive floats: mantissa 6755399441055744,
   exponent -199), not 2^-149. own for the value; the wrong text reported.
7. `TOps.v` line 3, `Sincos32_IEEE.v` line 2, `Zero.v` line 2: "Flocq and the standard library only ... nothing is
   assumed". IMPRECISE: each imports this tier's modules and each theorem rests on the tier's four axioms. Right:
   "Flocq, the standard library and this tier's modules; no Axiom or Admitted here; rests on the four axioms".
   reported (the `TOps.v` line own).
8. `Zero.v` header: "four values" for the three non-finite values of `Z_SIN_NONFINITE_proof`. own (Turn 226).

## Claims made in the build log (Turn 226) and to the owner, corrected in Turn 227's entry

9. "the statement hash sits in four places ... gate.json": `gate4.py` never reads the `statement` field of
   gate.json. The rows that hold the statement are the freeze-list row and, by a side effect, the plant
   generator's own hash check. MEASURED by two canaries this turn (`harden-probes\runs\canaryA-gate4-console.txt`,
   `canaryB-gate4-console.txt`).
10. "HELD 290 of 290" and "288 of 288" without the split: 119 of the 290 rows and 166 of the 288 concern files
    outside the judged theorem's closure (reported; the totals by kind own).
11. "43 of 43" and "16 of 16 plants refused": 13 of the 59 are function-level falsehoods with a Python witness; 17
    are false only in the constants part; 9 are refused by the statement file itself; 5 are refused at a part that
    stays true; 2 are route checks (one probably true); 13 leave the statement unchanged; `Z_SIN_NONFINITE` has no
    plant. reported.
12. "discarded values ... are not shown finite" was worded as a risk: on 32,640 sampled finite binary32 inputs in
    every binade, and four edges, no value the shapes compute is non-finite or a nonzero binary64 subnormal
    (MEASURED this turn, `harden-probes\runs\prim5-console.txt`); three independent derivations (ARGUED) say there
    is none for any finite input. Not proved.
13. The 2^23 result of Turn 226 was REPORTED (agent A, the reviewer agent), not read by the main session.
