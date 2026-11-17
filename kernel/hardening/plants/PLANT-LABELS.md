# The 59 plants of sincos32i and sincos32z, labelled (R4 d)

Written by the assistant on 2026-11-17, scratch. The owner's ruling R4 (d): "for each existing plant one of three
labels, refuted in Coq by kernel conversion (naming what is refuted), possibly-true variant, or function-equivalent
with its evidence", with refutations "by kernel conversion or vm_compute only (never native_compute)".

Evidence for the "refuted in Coq" rows: `runs/refute4-console.txt` (sha256
ee20fca4895aea41cdfd0311ccd4f2359da8167bc5d4d1f3862dd81f3c87b97a). In `stage3/`, each `<tag>/S.v` is the gate's planted
file, byte for byte; for the nine shape plants it is cut before its first eq_refl tie, the line where the gate refuses
it. Each `<tag>/Refute.v` proves `~` of the planted claim at the named input by `vm_compute` against the frozen
candidates' own theorems (IEEE_SINTURN32_proof, IEEE_COSTURN32_proof, IEEE_TCST_proof, sinturn32_exact).
- All 45 compile against the frozen closure.
- Print Assumptions of each lists exactly the four axioms of the tier.
- One recursive coqchk over all of them exits 0: its summary holds exactly the four axioms and nothing unsafe.

Every row is a Coq theorem of this host's run. That a planted claim is false is shown; what the plant's text says
about the planted shape's value at the witness is not used.

## Counts

| | sincos32i | sincos32z | all |
|---|---|---|---|
| Refuted in Coq | 34 | 11 | 45 |
| Possibly-true variant | 3 | 1 | 4 |
| Function-equivalent | 0 | 0 | 0 |
| Statement unchanged (outside the three labels) | 6 | 4 | 10 |
| Total | 43 | 16 | 59 |

## Refuted in Coq (45)

| Plant | What is refuted | Theorem |
|---|---|---|
| i_shape_arg_4 | the planted IEEE_COSTURN32 (planted shape), at 0 (00000000) | `R4PL.i_shape_arg_4.Refute.refuted` |
| i_shape_c_no_abs | the planted IEEE_SINTURN32 (planted shape), at -15722496 * 2^-23 (BFEFE800) | `R4PL.i_shape_c_no_abs.Refute.refuted` |
| i_shape_cos_big_0 | the planted IEEE_COSTURN32 (planted shape), at 2^23 (4B000000) | `R4PL.i_shape_cos_big_0.Refute.refuted` |
| i_shape_n_add | the planted IEEE_SINTURN32 (planted shape), at 0 (00000000) | `R4PL.i_shape_n_add.Refute.refuted` |
| i_shape_narrow_add | the planted IEEE_SINTURN32 (planted shape), at 2^-149 (00000001) | `R4PL.i_shape_narrow_add.Refute.refuted` |
| i_shape_poly_swap | the planted IEEE_COSTURN32 (planted shape), at 0 (00000000) | `R4PL.i_shape_poly_swap.Refute.refuted` |
| i_shape_q_1f | the planted IEEE_SINTURN32 (planted shape), at 1/4 (3E800000) | `R4PL.i_shape_q_1f.Refute.refuted` |
| i_shape_sin_sel_k1 | the planted IEEE_SINTURN32 (planted shape), at 1/4 (3E800000) | `R4PL.i_shape_sin_sel_k1.Refute.refuted` |
| i_shape_sinturn_no_narrow | the planted IEEE_SINTURN32 (planted shape), at 1/4 (3E800000) | `R4PL.i_shape_sinturn_no_narrow.Refute.refuted` |
| i_ieee_sub_is_add | the planted statement's IEEE_SINTURN32, at 0 (00000000) | `R4PL.i_ieee_sub_is_add.Refute.refuted` |
| i_ieee_neg_is_abs | the planted statement's IEEE_SINTURN32, at -1/4 (BE800000) | `R4PL.i_ieee_neg_is_abs.Refute.refuted` |
| i_ieee_sel_le_is_lt | the planted statement's IEEE_SINTURN32, at 0 (00000000) | `R4PL.i_ieee_sel_le_is_lt.Refute.refuted` |
| i_cst_0_ulp | the planted statement's IEEE_TCST, at K_0 | `R4PL.i_cst_0_ulp.Refute.refuted` |
| i_cst_1_ulp | the planted statement's IEEE_TCST, at K_1 | `R4PL.i_cst_1_ulp.Refute.refuted` |
| i_cst_110_ulp | the planted statement's IEEE_TCST, at K_110 | `R4PL.i_cst_110_ulp.Refute.refuted` |
| i_cst_156_ulp | the planted statement's IEEE_TCST, at K_156 | `R4PL.i_cst_156_ulp.Refute.refuted` |
| i_cst_20_ulp | the planted statement's IEEE_TCST, at K_20 | `R4PL.i_cst_20_ulp.Refute.refuted` |
| i_cst_210_ulp | the planted statement's IEEE_TCST, at K_210 | `R4PL.i_cst_210_ulp.Refute.refuted` |
| i_cst_4_ulp | the planted statement's IEEE_TCST, at K_4 | `R4PL.i_cst_4_ulp.Refute.refuted` |
| i_cst_42_ulp | the planted statement's IEEE_TCST, at K_42 | `R4PL.i_cst_42_ulp.Refute.refuted` |
| i_cst_6_ulp | the planted statement's IEEE_TCST, at K_6 | `R4PL.i_cst_6_ulp.Refute.refuted` |
| i_cst_72_ulp | the planted statement's IEEE_TCST, at K_72 | `R4PL.i_cst_72_ulp.Refute.refuted` |
| i_cst_BIG_2p22 | the planted statement's IEEE_TCST, at K_BIG | `R4PL.i_cst_BIG_2p22.Refute.refuted` |
| i_cst_BIG_ulp | the planted statement's IEEE_TCST, at K_BIG | `R4PL.i_cst_BIG_ulp.Refute.refuted` |
| i_cst_CN_odd | the planted statement's IEEE_TCST, at K_CN | `R4PL.i_cst_CN_odd.Refute.refuted` |
| i_cst_CN_ulp | the planted statement's IEEE_TCST, at K_CN | `R4PL.i_cst_CN_ulp.Refute.refuted` |
| i_cst_HH_ulp | the planted statement's IEEE_TCST, at K_HH | `R4PL.i_cst_HH_ulp.Refute.refuted` |
| i_cst_KK_ulp | the planted statement's IEEE_TCST, at K_KK | `R4PL.i_cst_KK_ulp.Refute.refuted` |
| i_cst_MM_ulp | the planted statement's IEEE_TCST, at K_MM | `R4PL.i_cst_MM_ulp.Refute.refuted` |
| i_cst_PH_ulp | the planted statement's IEEE_TCST, at K_PH | `R4PL.i_cst_PH_ulp.Refute.refuted` |
| i_cst_TT_ulp | the planted statement's IEEE_TCST, at K_TT | `R4PL.i_cst_TT_ulp.Refute.refuted` |
| i_prem_sin_no_finite | the planted statement's IEEE_SINTURN32 (no finiteness premise), at NaN | `R4PL.i_prem_sin_no_finite.Refute.refuted` |
| i_concl_cos_is_sin | the planted statement's IEEE_COSTURN32 (conclusion names the sine graph), at 0 | `R4PL.i_concl_cos_is_sin.Refute.refuted` |
| i_core_bound_2p200 | the planted lemma core_den (bound 2^200 for 2^62), restated, at V = 2^200 | `R4PL.i_core_bound_2p200.Refute.refuted` |
| z_sin_step_none | the planted statement's Z_SIN_ZERO, at 1/2 (3F000000) | `R4PL.z_sin_step_none.Refute.refuted` |
| z_sin_step_abs | the planted statement's Z_SIN_ZERO, at -1/2 (BF000000) | `R4PL.z_sin_step_abs.Refute.refuted` |
| z_zero_sin_opposite | the planted statement's Z_SIN_ZERO, at 1/2 (3F000000) | `R4PL.z_zero_sin_opposite.Refute.refuted` |
| z_zero_sin_plus | the planted statement's Z_SIN_ZERO, at -1/2 (BF000000) | `R4PL.z_zero_sin_plus.Refute.refuted` |
| z_cos_step_none | the planted statement's Z_COS_ZERO, at 1/4 (3E800000) | `R4PL.z_cos_step_none.Refute.refuted` |
| z_cos_step_sub | the planted statement's Z_COS_ZERO, at 1/4 (3E800000) | `R4PL.z_cos_step_sub.Refute.refuted` |
| z_cos_step_no_abs | the planted statement's Z_COS_ZERO, at -3/4 (BF400000) | `R4PL.z_cos_step_no_abs.Refute.refuted` |
| z_zero_cos_minus | the planted statement's Z_COS_ZERO, at 1/4 (3E800000) | `R4PL.z_zero_cos_minus.Refute.refuted` |
| z_zero_sin_no_finite | the planted statement's Z_SIN_ZERO (no finiteness premise), at NaN | `R4PL.z_zero_sin_no_finite.Refute.refuted` |
| z_value_cos_is_sin | the planted statement's Z_COS_VALUE (conclusion names the sine graph), at 0 | `R4PL.z_value_cos_is_sin.Refute.refuted` |
| z_nonfinite_cos_unstepped | the planted statement's Z_COS_NONFINITE (claimed of the unstepped cosine), at +infinity | `R4PL.z_nonfinite_cos_unstepped.Refute.refuted` |

Notes on what these show:
- The nineteen constant plants are refuted in the planted statement's IEEE_TCST part, the part their change falsifies.
  Whether the planted shapes compute other binary32 results than the frozen ones is not settled here. The plant
  author's sampling found a function-level witness for two of them (cst-4-ulp, cst-BIG-2p22). An exhaustive comparison
  with the T2 harness would settle it (candidate slice).
- The nine shape plants are refuted in the claim the planted file would state, written out with the planted shape.
  The planted file itself does not compile past its first tie, and that tie is where the gate refuses it.

## Possibly-true variant (4)

| Plant | Status |
|---|---|
| i ieee-mul-toward-zero (multiplication rounds toward zero) | Not refuted; no witness among the plant author's 81,686 sampled inputs. An exhaustive comparison is possible with the T2 harness (candidate slice). |
| i prem-cos-no-format (IEEE_COSTURN32 for every finite binary64 input, not only binary32 numbers) | Not refuted; argued probably true by the overclaim audit of Turn 227 (the cosine's value before narrowing is near 1 for every finite input). |
| i two-of-three (Closed.v states two of the three parts under the name SINCOS32_IEEE) | True: it is the conjunction of two proved parts. The identity row refuses it. |
| z four-of-six (Closed.v states four of the six parts under the name SINCOS32_IEEE_ZERO) | True: the conjunction of four proved parts. The identity row refuses it. |

## Statement unchanged: outside the three labels (10)

These plants change no statement, so there is no claim to refute and no variant to label; they test the gate's
reading of assumptions and its guard check, or a step of a proof.
- **sincos32i:**
  - admitted-closed, admitted-stages, admitted-tops: a lemma or the top theorem ends with Admitted;
  - tcst-axiom: a lemma made an Axiom;
  - guard: a recursion with its termination check switched off;
  - no-finite-fact: a proof step replaced by 1 = 1.
- **sincos32z:**
  - admitted-closed, admitted-fin-zero: Admitted;
  - mul0-axiom: an Axiom;
  - guard.

The ruling's three labels do not fit them. Naming this fourth group is the owner's to rule.

Evidence that each is refused (READ, own; the assistant's own gate runs of the frozen candidates):
- `night\gate-runs\sincos32i-gate4-own1-console.txt` (sha256
  693194718a896567359a1aa0661370e36a934cc95ae6c6b9f90272a0441fc749; SINCOS32_IEEE GATE4 HELD: 290 of 290):
  admitted-closed, admitted-stages, admitted-tops and tcst-axiom refused because Print Assumptions names the admitted
  lemma or the axiom; guard refused because Print Assumptions says "Closed.loop is assumed to be guarded";
  no-finite-fact refused because its file does not compile (exit 1: the term eq_refl has type 1 = 1).
- `night\gate-runs\sincos32z-gate4-own1-console.txt` (sha256
  ce096a1f75a7364ac2ac73597689043357efdc9234edae18e5508f7e44df3c25; SINCOS32_IEEE_ZERO GATE4 HELD: 288 of 288):
  admitted-closed, admitted-fin-zero and mul0-axiom by Print Assumptions; guard as above.
- The minimal harness refuses an admitted top theorem at its rows 7 and 8 even when the freeze list is rewritten to
  match (`..\harness\canaries\c3-admitted-console.txt`, sha256
  b8963cc3db2ebd8c5bb2405c9639a05fc0b87ec76c43c414142c38d34496b98d).
