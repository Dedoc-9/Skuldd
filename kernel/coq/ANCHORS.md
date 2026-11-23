<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Anchors

An anchor is the sha256 of a gated folder's freeze list, `kernel/coq/<folder>/FROZEN4.txt`; a gated folder is a folder
of `kernel/coq/` that holds a `gate.json`. A folder's gate is given its anchor and compares it with the freeze list it
reads (the row `freeze list is the anchored one` of `gate/gate4.py`), so a change that rewrites both a folder's sources
and its freeze list fails against the anchor. That holds only when the anchor comes from outside the checkout being
judged: CI gives each gate the value of a repository Actions variable, `MK_ANCHOR_<FOLDER>` (the folder's name in
capitals). This file is not where that value comes from.

This file is the ledger of those values, kept in the tree so that a reader can compare them. The values of the first
thirteen folders below were set by the owner on 2026-11-17 local time (2026-11-18 UTC) as the repository's Actions
variables; those of the next four (`sincos32n`, `exp32a`, `floor32` and `ceil32`) were minted by the owner on
2026-11-18, and those of the last four (`rti32`, `order32`, `bits32` and `fclink`) on 2026-11-22; the owner sets
these eight as Actions variables before the push that adds those folders. Each value
is the sha256 of its folder's `FROZEN4.txt` in this tree. `tools/ci/inventory.py` checks that the table has
exactly one row per gated folder and none for another folder, that each row names its folder's variable and a
record, that no line outside the table reads as a table line and no line under it reads as one more row as GitHub
reads tables, that the file holds no block quote and no list item holding a bar, which its reader does not open (the
gate job's step reads this file with the inventory's own reader), that the whole file is written in the subset of
Markdown that script's header names (among its rules: no HTML after line 1, no second table, no backslash, no code
fence, no character outside printable ASCII, no left square bracket, no number sign before a blank or a line's end
but on a top-level heading's line, and no line of equals signs or hyphens only under a line that is not blank), and
that each value is the sha256 of that folder's
`FROZEN4.txt`. A folder, its freeze list and its row here
changed together still pass that check: such a change fails only against the variable, which is why the variable, not
this file, is the anchor. This file is itself a CI judge file (`tools/ci/judge_digest.py`), so a change to its prose
or its Record column moves `MK_ANCHOR_CI` too.

`MK_ANCHOR_CI` is a further repository Actions variable: the CI judge digest of the reviewed tree
(`tools/ci/judge_digest.py`), which the owner sets after review. It anchors no folder, and this file holds no value for
it. So no gated folder may be named `ci`: the inventory refuses one, whose variable would be `MK_ANCHOR_CI`.

To check a row: `sha256sum kernel/coq/<folder>/FROZEN4.txt`, then compare with the row and with the variable in the
repository's settings (Secrets and variables, Actions, Variables).

| Folder | Variable | sha256 of FROZEN4.txt | Record |
|---|---|---|---|
| `f32` | `MK_ANCHOR_F32` | `53880a185dd4b23539f38a446d94f16dcb1f1cf1f69a061c78ec32c1f23ca002` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `p32` | `MK_ANCHOR_P32` | `9adba8eecba84425d258869e9a644622281644a1adcf4ebc40b147390ac7ee45` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `p32r` | `MK_ANCHOR_P32R` | `2fc8014ccb21d40bb0c9215cbeff931c45f4fc1831528eb6c52e9a07ee84cb5e` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `exp32` | `MK_ANCHOR_EXP32` | `68481fb907358ff7d76ab974246b42ed4a1eb1c7ebbe31abe309c97c03273fb8` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `exp32r` | `MK_ANCHOR_EXP32R` | `c7052646819b4e690ff7c85648f188643442e5701bedfd8fcbfd9151a1ad9b4a` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `ieee64` | `MK_ANCHOR_IEEE64` | `42e3891e153bafae200b7e3b48c2573fbc4406d58fa941bd0bf1f672f51ddb42` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `sin32` | `MK_ANCHOR_SIN32` | `f221512da6f70c5a96d608a7b9ba5d2aa901df7bfaeb7e01ea7a1c2bf29a6ff0` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `cos32` | `MK_ANCHOR_COS32` | `c4f9cec1eb5ac2d49b9a9a7514e66f330f09c89df517a5ee40cb760d3c35cf8d` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `sincos32` | `MK_ANCHOR_SINCOS32` | `02c8e687a910dfe56bcf4220f56959c7901cf1fd3e28137410aeb0255cb41a16` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `log32` | `MK_ANCHOR_LOG32` | `ff05c06d41e2f96a5651d40095b5c1d27d36d44ce72220c889dbd167f59a0749` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `sincos32i` | `MK_ANCHOR_SINCOS32I` | `1477b814c8295c55a11cbae2f332f9b9cde364853dcf5f7d132253fe4b95e2d4` | set by the owner on 2026-11-17 local time (2026-11-18 UTC); recorded by the owner before the import (`PROVENANCE.md`) |
| `sincos32z` | `MK_ANCHOR_SINCOS32Z` | `a55d1c08a6929a0e4ce46a05c83537be48901b0d5adadd0b05bdcf1da4531172` | set by the owner on 2026-11-17 local time (2026-11-18 UTC); recorded by the owner before the import (`PROVENANCE.md`) |
| `compose` | `MK_ANCHOR_COMPOSE` | `7c907088bdf36179ab7cc8a523ca2659781f1a5670ce4d153193da00d0b7aef8` | set by the owner on 2026-11-17 local time (2026-11-18 UTC) |
| `sincos32n` | `MK_ANCHOR_SINCOS32N` | `7cf75e2cc75e86c07110eee868c72e5db56e00f62001c91ad0193f57a15a3558` | minted by the owner on 2026-11-18 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `exp32a` | `MK_ANCHOR_EXP32A` | `08c9c09cd28ffcea6cac962e759c3d056fc87e3cbb7b14e64729c20cc95ed2b4` | minted by the owner on 2026-11-18 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `floor32` | `MK_ANCHOR_FLOOR32` | `62db0a2ec778fb51c5e274b6df8784ad18b67940c33b273174f6df59e69a4998` | minted by the owner on 2026-11-18 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `ceil32` | `MK_ANCHOR_CEIL32` | `468d29c862d8e14338fb1434f24cc839e1c8a003a9ebb09ca60c5b6c9ce5ad23` | minted by the owner on 2026-11-18 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `rti32` | `MK_ANCHOR_RTI32` | `1f0c20067174f98ce74c4c9d7e3377ee204b9c5618e3d790a1d891175a41885f` | minted by the owner on 2026-11-22 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `order32` | `MK_ANCHOR_ORDER32` | `0ea74cf1267a35e0d988c2c1efb8be5f5457c24d3f189de0ca1f75bc37133484` | minted by the owner on 2026-11-22 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `bits32` | `MK_ANCHOR_BITS32` | `820e15169d17c2395d9abce4ad687e4e4eb17208bbb0ce2abb77650771d0ca06` | minted by the owner on 2026-11-22 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
| `fclink` | `MK_ANCHOR_FCLINK` | `96ac2c42d44ef185ac8b70ab12da628268ab1471907ac4a5df5a97d3305b0dfa` | minted by the owner on 2026-11-22 (local time and UTC); the owner sets the Actions variable before the push that adds this folder |
