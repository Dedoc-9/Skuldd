<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Changes after the import

The first commit is the import, exactly as `PROVENANCE.md` and the manifests describe it. Each later change is
listed here, file by file, with its sha256 before and after, and the owner's ruling it carries out.

## Ruling C2 (b): account-name paths and host-named records

The account name in local paths is replaced by `USER`; the records named after the host are removed.

| File | Occurrences | sha256 before | sha256 after |
|---|---|---|---|
| `verdandi/verify/RUNGS.md` | 4 | 03083a73852306cbc4c4f236c8625106aff72b437c746a09d582a19fd384cabb | f6b6034829e028ef562c570f1e2c935b85d815ebfd8ea019c5e9ab8c7ff140ef |

Carried byte for byte by the owner's ruling S1 (a) of 2026-11-17, an exception to C2 (b) for this registered
file, though it holds the account name: `verdandi/verify/preregister.json` (1 occurrence; sha256 e8d8dc3f832b18f2f0ffbada37ae95050bdcb9fb64439f46a8e1d40ba247a6ae). Its entries are registered under
chain hashes, and Verdandi's gate refuses any edit of a registered entry (its rows records-preregistered
and input-tamper). The path is already public in Verdandi.

Removed (40 records; the host's name in each path is written `<host>` here):

| File | sha256 |
|---|---|
| `verdandi/kernel/attest/bearingfast-<host>.json` | 77dd5d9aff326828db836322f982be8d6750d1837a1e32674e5c01065f1d5296 |
| `verdandi/kernel/attest/bearingsweep-<host>.json` | cd7344f013e9aa0a95f159cd9f7c2ee7a05804aa3e3021664e31aaece2121e72 |
| `verdandi/kernel/attest/bench-<host>.json` | b03468815b66c048c63187d981d9e5bbe11beb9e165bbbe43ec5cc147422fa19 |
| `verdandi/kernel/attest/breakdown-<host>.json` | fe4d11d6bab8c19afaf1c0f350c4d5e57193b784d79a5599b8ba6e60a6711842 |
| `verdandi/kernel/attest/emit-breakdown-<host>.json` | 3602cfea630c3b54ee153e096698216337f23f0167996f280c87bbc92ef1db50 |
| `verdandi/kernel/attest/gauntlet1b-<host>.json` | b139058ac3d086a501b30f56fba2517b7301fb99ca3cd05682ea82156fe0dff2 |
| `verdandi/kernel/attest/gauntlet1c-<host>.json` | d6aea51d52fac2924d1be6d45c8f28e9fd964e2d01aa352969a66e8b0a83b3a1 |
| `verdandi/kernel/attest/gauntlet2-<host>.json` | 7bc318e0ebb70d0f252c1c4f707b31a62fa316865721d9a3db4ea9b540776c1a |
| `verdandi/kernel/attest/locality0-<host>.json` | d43a385d1b643ee05b45ddc51859bf01a951400c2284dfb45abd778bc03e7ded |
| `verdandi/shell/attest/allocreuse-<host>.json` | 9fd864742aa97afdf794de2a4d35964b8fcb60abc64782aaa3167fa9c8464082 |
| `verdandi/shell/attest/allocreuse-confirm-<host>.json` | a44c27a09f3b3db2a305920d1cf7ef5194f31e6d8e311b1d0386fa37c80ba268 |
| `verdandi/shell/attest/allocreuse1-<host>.json` | 6a0d1e59f7acbe0482df0183f18e598f2568e9bf313159d389aa9625109f7cab |
| `verdandi/shell/attest/allocreuse1-confirm-<host>.json` | 2a8071e45aedd2f5252c2949c3e477e2c8f8aee2e230d5aefdf3b8a9e080bd59 |
| `verdandi/shell/attest/drift-<host>-s1-r1.json` | 2ef5576bb780845f5e9d8d3044716e0539020ce51edd96d921abdd359e2b5ee2 |
| `verdandi/shell/attest/drift-<host>-s1-r2.json` | 52475c6410cccfe552545dc02d3a06f762a10824eb173c72ddc8baf2263c018c |
| `verdandi/shell/attest/drift-<host>-s1-r3.json` | 88f961168ff4fa84221723254ac72f06f94d73f0a08f21c2e6dbc97291466154 |
| `verdandi/shell/attest/drift-<host>-s1-r4.json` | 1c2cce8d502bac08811d88d0b3cd2dda5ad0f1c78974800c767e1019d677b5fe |
| `verdandi/shell/attest/framesplit-<host>.json` | d5e66f5ac6b35b9a2443bbe5461d7dd5d63aa2c6d68bade4a7e9160ee4d1706d |
| `verdandi/shell/attest/framesplit-confirm-<host>.json` | d4c981e982b5d34ef6237fff38086a37a98df7093d50a370a0c271acb6698fce |
| `verdandi/shell/attest/latency-<host>.json` | 8a5c9c344df04ea6e890375565ffb522ab4d111b18f63599d913aa862803168b |
| `verdandi/shell/attest/latency1-<host>.json` | e0b4be3ab43d5658fd69736b68095ccff794504ccb8eeca3c43d2a3742f6a1e7 |
| `verdandi/shell/attest/latency1-confirm-<host>.json` | 9ec5202e1d138d734ac97f1523286d13583461836e2818109e4273fd215109fb |
| `verdandi/shell/attest/latency1r-<host>.json` | b6e18ff1da80447772c441bfd0aa3f5026a982942588e924c1d23f016263e33d |
| `verdandi/shell/attest/latency1r-confirm-<host>.json` | 2cb209877aa87559b00726a1573d8e2083ba465eb6ece5bccdcb5657d8294170 |
| `verdandi/shell/attest/liveloop-<host>.json` | b754bdfe42e696d54d44a2cc042fbc6854f5950f91ef5559654d4efc5fcc3fe3 |
| `verdandi/shell/attest/livesession-<host>-47ae5de3c73a.json` | c95c5bb11740d9cd69a2490636fd2843dc8f624b7205d0cc3aac8f74567aa161 |
| `verdandi/shell/attest/livesession-<host>-5290c848217d.json` | 8dfd490500b59b288894393f35e2571ecf8c0698386df937120ff831693337f4 |
| `verdandi/shell/attest/livesession-<host>-a0861e0e837b.json` | cb2caa541ddc9d4cc73431466b1ee04b537eb5b19f4202d6d447226236d2d421 |
| `verdandi/shell/attest/livesession-<host>-aa850e786b6f.json` | 21e8f70c174fba05ff13fde7b76fc9e726307c54443612e9f9747260eec51505 |
| `verdandi/shell/attest/livesession-<host>-b28e42be62c4.json` | eb53c112e554f78a6819ff63d9365410edc6dcc67a6ed004f7f51454574b084d |
| `verdandi/shell/attest/livesession-<host>-dd874eff3a69.json` | 41e9840d3aed8739d4e7a87bb9d0194e88e08aa58cb6a1daaa9bb4a7d5431608 |
| `verdandi/shell/attest/livesession-<host>-e9dafb482675.json` | 7c80b9949059aa88aaba195e87484d7204bc42a550a1f71db2e01eb3eff17967 |
| `verdandi/shell/attest/livesession-<host>-eaf27cf3fc0c.json` | 82f21729a95314f795399a65165a2324e959a17faaa8b8a21e9e28867e2c5b2f |
| `verdandi/shell/attest/present-<host>.json` | 54f5d92dad552c952579f7f6879dea6ac355be6955bfdb160537c0a114cf3934 |
| `verdandi/shell/attest/presentexact-<host>.json` | 3aee31654edc5249a2f7fa978d514b36c491a8641202991154a497093b5bdc4d |
| `verdandi/shell/attest/presentexact-confirm-<host>.json` | ff165ff860e182307121cb53da3d22d1c98eb5e09579268af53ec84379e9dd06 |
| `verdandi/shell/attest/presentscale-<host>.json` | d64e1747bdc441b821a89a8fb201e48004c4d629cecd7f094100201a179fe013 |
| `verdandi/shell/attest/presentscale-confirm-<host>.json` | d749c0e49e9bdd510e117e7cb83a4c61a37077f4dfef0d00e83a8c05675e183e |
| `verdandi/shell/attest/presentstretch-<host>.json` | 68462613641dee9288dff428e5a8629d6e8555100380e7a3771bed1dc4d06187 |
| `verdandi/shell/attest/presentstretch-confirm-<host>.json` | ca89362b18a92c315341dc34cb0f0c11b506bfc5b6747c4f3dd14e4aa8f4fc9b |

## Ruling C3 (a): the engine name in Verdandi's art README

In `verdandi/art/README.md` the engine's name and version are replaced by "future engine integration" wording in 10 places;
in the owner's quoted words the change is marked with square brackets. File paths, a file name and a
module name that contain the word are kept (7 occurrences), since they name files and code. The art
briefs' licence references are unchanged, as the ruling says. sha256 before ec63c93d7be8bfa9ecb0eab9dcfdb2adc6c549af4fbeac6ab33a06bf3e915857, after c541568f4078fb17c638b855b7d23699236994420ecf6babf16fe71da543f191.

## The owner's ruling on private goals: one name withheld

One external tool's name is replaced by `[withheld]` in 18 places of 3 documents; the square brackets mark
the change, also where it falls inside quoted words.

| File | Occurrences | sha256 before | sha256 after |
|---|---|---|---|
| `verdandi/docs/RESEARCH-FINDINGS.md` | 2 | b5ba19c29e0f018137cec4b850e21d1767833d52e8e70f550326c7825030c142 | 22c4b6ab617e53a6fc2160cb9e88ebbd4d52bc371edde445cbbe05f45fc6639c |
| `verdandi/docs/ROADMAP.md` | 9 | dfbbad4bc79a2e101e11b4eb79ed977c561111fe1250283d96ad81ca9e5eda27 | 2702339d36f1f4aafa2310f968e6d5aa810802d1e60cbb0927a3e91f6e1c67d0 |
| `verdandi/docs/STUDIO-APP.md` | 7 | fb7ab399cd1c3d5d729794930e102b59630900516d64431b387eb8485f41bbda | d9ea819deff1d77847cf68b907918b010f0edde8c01e22632ee0f6d79f0cbdd0 |

## Ruling S2 (b): the engine's name in seven lines of Verdandi's README and brief

In seven lines the engine's name is replaced by future-engine-integration wording; every other file of
`verdandi/` keeps its bytes, apart from the changes listed in this file. The words that replace it:

| File | Line | Now reads |
|---|---|---|
| `verdandi/README.md` | 150 | `future engine: verdandi_import.py` |
| `verdandi/README.md` | 186 | `an importer for a future engine integration` |
| `verdandi/README.md` | 292 | `playable art, a future engine integration to render it,` |
| `verdandi/README.md` | 294 | `its import into a future engine not yet run)` |
| `verdandi/README.md` | 353 | `# the scene for a future engine: art/build/plaza-night/scene.json` |
| `verdandi/README.md` | 426 | `the engine-import steps` |
| `verdandi/AGENTS.md` | 45 | `the importer for a future engine integration (an optional path)` |

sha256 before and after: `verdandi/AGENTS.md` 823e7962c7ddebfde830d64c4230b30ad145e4af3bf82ca806cb11a24e1eae47, 63ad624f8496d7414b4ddae562ca7491a7d00311842982a6a25e6165671bcfce; `verdandi/README.md` 3a10c7f033d22367739b808650ab8ee5aae0cf5bd0903802cc5cd784e1dd0015, a1e6ccecbf5301d22ea15f574f3d0c6a718eda30f591183c165b3d1ac9721449.

## Ruling S6 (a) (1): commands written for a repository of their own

`AGENTS.md` gains the section "Inside Skuldd: commands written for a repository of their own": what each
command found on the import does here, and where or in which form to run it instead. Skuldd's copy of
`verdandi/tools/rung.py` gains a guard, the function `skuldd_guard`, called in `main` before any command:
it refuses in one line unless the folder it is given is Verdandi's root and git's top level, so inside
Skuldd it never passes over no rows. Verdandi's own repository has no such guard.

| File | sha256 before | sha256 after |
|---|---|---|
| `AGENTS.md` | ca9311b9ccc780725ffb91ed6f84bb00a5e053d5391ed3c8d8a5fe2f53690f93 | 4841da869d8a6e2c1f34804f1411cb5ae3995bbfe9afac282830535979d960f5 |
| `verdandi/tools/rung.py` | ef1a05823ff3a10c4c619cf015b0acde2450219f8543f336063a8c6a2a99fe47 | de429a26f76514109ab6640ab261131297f53e37a96a4140c94d7426087e908e |

## Ruling S7 (a): the law's status, said of this tree

Seven spans now say what a reader can check in this tree: that it holds no proof of the law of the turns
kernel.

| File | Line | Was | Now |
|---|---|---|---|
| `README.md` | 95 | `stated, not frozen, not proved, and withheld from this tree until` | `stated, not frozen, not proved in this tree, and withheld from this tree until` |
| `THEOREMS.md` | 14 | `## The law of the turns kernel: stated, NOT PROVEN` | `## The law of the turns kernel: stated, NOT PROVEN IN THIS TREE` |
| `THEOREMS.md` | 18 | `**stated, not proven**; withheld from this tree until` | `**stated, not proven in this tree**; withheld from this tree until` |
| `kernel/notes/LIMITATIONS.md` | 20 | `**Its law on 32-bit patterns is stated, not proven.**` | `**Its law on 32-bit patterns is stated, not proven in this tree.**` |
| `kernel/notes/LIMITATIONS.md` | 22 | `it has no proof yet, and its statement is` | `this tree holds no proof of it, and its statement is` |
| `docs/paper/SYSTEM-GUARANTEES.md` | 21 | `is stated, not proved.` | `is stated; this tree holds no proof of it.` |
| `docs/paper/SYSTEM-GUARANTEES.md` | 48 | `(stated; NOT PROVEN).` | `(stated; NOT PROVEN in this tree).` |

With them, in the same commit, the 94 changes of ruling S9, each found by its exact old text (line breaks
inside a text are shown here as spaces):

<details>
<summary>The 94 changes of ruling S9</summary>

- `docs/paper/SYSTEM-GUARANTEES.md`, line 5: was "Every claim carries one of five grades:"; now "Every graded claim carries READ (read in a file), REPORTED (found by others or by agents, not rechecked here), NOT PROVEN, NOT MET or one of five grades:"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 11: was "Real-time simulations, competitive games among them, need the same numbers on every machine and in every language"; now "Some real-time simulations, lockstep competitive games among them, need the same numbers on every machine and in every language"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 15: was "a prose language whose programs give byte-identical results on"; now "a prose language whose programs are held to byte-identical results (measured on 11 programs of its corpus) on"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 22: was "Rust, Python and Ørlǫg are designed, not built."; now "Rust and Python are designed, not built; one for Ørlǫg is planned, not yet designed."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 43: was "every statement is written and hashed before its proof, every check is shown to fail on a planted fault, and the owner, not the author, computes the hashes that anchor the claims (DESIGNED and in use)."; now "each statement is to be written and hashed before its proof, each check is to be shown to fail on a planted fault, and the owner, not the author, is to compute the hashes that anchor the claims (DESIGNED; in use in part: `compose`'s statement claims no such order, not every check has been shown to fail, and the owner holds the hashes of two folders only)."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 57: was "No backend in C99, Rust, Python or Ørlǫg exists yet for the kernel."; now "No C99, Rust, Python or Ørlǫg library of the kernel's binary32 functions exists yet; the C sweep programs and Ørlǫg corpus laws of the five older ones (`narrow`, `sqrt32`, `rsqrt32`, `hypot32`, `exp32`) under `verdandi/mathkernel/F32/orl` are unadmitted test renderings."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 62: was "Then an IEEE shape"; now "For the five older functions and the turns kernel, though not yet for `log32`, `sin32` or `cos32` on their own, an IEEE shape"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 64: was "a zero layer that fixes the sign of every zero result"; now "a zero layer that fixes the sign of the result wherever the function is exactly zero (that no other result is zero is MEASURED, section 5.3)"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 70: was "are held to byte-identical output against 20,015 runtime vectors and a corpus run four ways"; now "are held to byte-identical output on a corpus run four ways, and the C99 and Rust runtimes to 20,015 runtime vectors"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 75: was "rendered without hidden state (READ, its own brief)"; now "rendered deterministically (READ, its own brief)"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 82: was "the T2 sweep (section 5.3) | a proof; other hosts, compilers or MPFR builds"; now "the T2 sweep (section 5.3), whose transcription and consoles are withheld from this tree with the law | a proof; that the transcription equals the law outside 2,096 sampled patterns; other hosts, compilers or MPFR builds; MPFR's correctness, which is trusted"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 83: was "Every backend (C99, Rust, Python, Ørlǫg) gives the same bytes as the proved program on every input | DESIGNED"; now "Every backend (C99, Rust, Python; one for Ørlǫg planned, not yet designed) gives the same bytes as the proved program on every input | DESIGNED"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 84: was "conversions on integer bits make the kernel immune to flush-to-zero and denormals-are-zero"; now "conversions on integer bits make the turns kernel immune to flush-to-zero and denormals-are-zero"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 85: was "two parts are blob-exact copies of pinned commits"; now "two parts were blob-exact copies of pinned commits at the import, with every later change listed in `CHANGES-AFTER-IMPORT.md`"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 88: was "**G1 in the owner's words.**"; now "**G1 in plain words.**"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 100: was "the kernel uses neither"; now "the kernel's proofs and gates use neither (the `corpus` steps of two of its emitters, `kernel/coq/orl/emit.py` and `emit2.py`, run Ørlǫg's arbiter as a cross-check)"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 105: was "Today a function exists in about nine hand-kept renderings ("; now "Today there are at least nine hand-kept renderings of the turns kernel (reported:"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 117: was "is shown only by exhaustive sweeps;"; now "is shown only by sweeps, exhaustive for one-input functions and sampled for `hypot32`;"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 128: was "The owner computes the sha256 of every statement and freeze list himself; checks are"; now "Under his custody ruling the owner computes the sha256 of each statement and freeze list himself; so far he has done so for the two newest folders, and the eleven older folders' anchors were computed by the authors. For those two folders the harness is"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 132: was "printed four ways: a C99 header and source taking and returning 32-bit patterns; a std-only Rust module; a standard-library Python module; Ørlǫg laws."; now "printed in three programming languages: a C99 header and source taking and returning 32-bit patterns; a std-only Rust module; a standard-library Python module (Ørlǫg's use of the kernel is planned, not yet designed)."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 139: was "with no network and the judged files mounted read-only."; now "with no network; the containers of the hardening runs and of the sweep had the judged files mounted read-only, while the folder gates mount the tree writable and fail their last row if anything in it changed outside their own output folders."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 196: was "correctly rounded results, sine 4,278,189,318 and cosine 4,278,175,524"; now "results equal to MPFR's round to nearest, sine 4,278,189,318 and cosine 4,278,175,524"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 210: was "Thirty-two kernel-checked examples prove the values at ±2^106 and at its neighbours (PROVEN, `kernel/hardening/big106`);"; now "Thirty-two Coq examples, accepted by coqc and a recursive coqchk, give the values at ±2^106 and N and r at +2^104, +2^105, +2^107 and the two binary32 neighbours of +2^106 (MEASURED, `kernel/hardening/big106`);"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 218: was "None is triggered by the tier's own sources:"; now "The check refuted one label: the tier's `field` calls reach the `vm_cast_no_check` of entry #16891, which coqchk's re-check without the VM covers, like the VM entries below. For the others, the reading found no trigger in the tier's own sources:"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 228: was "The tree is built by one script from three sources."; now "The import commit's tree is built by one script from three sources; every later change is listed in `CHANGES-AFTER-IMPORT.md`."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 230: was "A privacy and naming scan of the whole tree is recorded with the decision it raised."; now "A privacy and naming scan of the whole tree was run outside it; the changes it led to are listed, with the rulings they carry out, in `CHANGES-AFTER-IMPORT.md`."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 246: was "numbered prose whose meaning is held identical across four executions."; now "numbered prose, whose outputs are held byte-identical across four executions on Ørlǫg's corpus; all four read the prose through one shared front end."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 250: was "The proofs remove whole classes of edge-case defects (signs of zeros, NaN handling, overflow in discarded branches) for the functions they cover."; now "For the turns kernel, the proofs fix, at binary64, the sign of the result at each exact zero and a NaN result for each non-finite input; no other function's statement gives these rules, and finite intermediates in discarded branches are a clause of the law, measured (section 5.3), not proved in this tree."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 256: was "The kernel gives Ørlǫg and Verðandi functions whose results are proved, not just tested. Ørlǫg gives the kernel a fourth, independent execution path"; now "The kernel would give Ørlǫg and Verðandi functions whose Coq shapes are proved, not just tested, once printers carry them into code (G3, DESIGNED). Ørlǫg would give the kernel a fourth execution path"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 259: was "a deterministic renderer shows a wrong bit as a visible difference."; now "a deterministic renderer shows a wrong result as a difference in its output bytes when the error reaches a pixel, which a one-bit error need not do."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 260: was "records never rewritten."; now "records changed only by the owner's ruling and listed (`CHANGES-AFTER-IMPORT.md` lists each change after the import, file by file, with the ruling it carries out)."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 266: was "checks binary32 functions exhaustively"; now "checks its univariate binary32 functions exhaustively (bivariate ones on known hard cases)"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 268: was "LLVM adopted several of its functions (people.cs.rutgers.edu/~sn349/rlibm). LLVM's libc aims at correct rounding in all rounding modes and tests every single-precision input"; now "LLVM's logf and log2f use RLIBM's polynomials, and LLVM's expf and exp2f RLIBM's range reduction (people.cs.rutgers.edu/~sn349/rlibm). LLVM's libc aims at correct rounding in all rounding modes and tests every input of its univariate single-precision functions"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 271: was "this kernel gives weaker rounding with machine-checked proofs and bit-level rules for NaN, zero signs and intermediates."; now "this kernel gives weaker rounding with machine-checked proofs; its bit-level rules for NaN, zero signs and intermediates, for the turns kernel only, are a law that is stated and measured, withheld from this tree and not proved in it."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 289: was "patterns that covers NaN bytes, zero signs and discarded branches; and a custody discipline in which the owner, not the author, holds the hashes."; now "patterns that covers NaN bytes, zero signs and discarded branches (stated and measured; withheld from this tree and not proved in it); and a custody discipline in which the owner, not the author, holds the hashes (so far those of the two newest folders and of the law)."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 294: was "Its text, code and proofs were written by the owner and by AI assistants working for him, as its records state."; now "Apart from the licence text in its three `LICENSE` files (the Free Software Foundation's) and nine fdlibm 5.3 source files in `verdandi/mathkernel/ORACLE/src` (written by Sun Microsystems and carried with their notices as the oracle of `verdandi/mathkernel`), its text, code and proofs were written by the owner and by AI assistants working for him, as its records state."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 297: was "The repository is offered under"; now "The repository, apart from nine fdlibm 5.3 files under Sun Microsystems' notice (`verdandi/mathkernel/ORACLE/src`), is offered under"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 304: was "`THIRD-PARTY.md` lists what was checked."; now "Nine fdlibm 5.3 source files (Sun Microsystems, under a permissive notice that must be kept) are copied into `verdandi/mathkernel/ORACLE/src` as the oracle of `verdandi/mathkernel`. `THIRD-PARTY.md` lists what was checked."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 320: was "small, exact and checkable: thirteen proved statements"; now "small and exact: thirteen proved statement files that a reader can check"
- `THEOREMS.md`, line 4: was "Every proved claim of Skuldd, in one place. Nothing absent from this file is claimed as proved anywhere."; now "Every proved claim of the kernel, in one place. Coq has also checked the following, all under `kernel/hardening/` with their consoles: 32 examples at ±2^106, +2^104, +2^105, +2^107 and the two binary32 neighbours of +2^106 (`big106/Big106.v`), 25 examples about `sincos32i` and `sincos32z` (`examples/Examples.v`), 45 refutations of planted claims (`plants/stage3/`, listed in `plants/PLANT-LABELS.md`) and one narrowing probe (`r7-probes/NarrowProbe.v`); none of them is one of the candidate statements below. Skuldd claims as proved nothing absent from this file; the imported documents of `orlog/` and `verdandi/`, and comments inside frozen files, keep their own words."
- `THEOREMS.md`, line 23: was "container with no network between 2026-11-10 and 2026-11-16."; now "container with no network between 2026-11-14 and 2026-11-16, each given its folder's `FROZEN4.txt` sha256 as its anchor. The consoles of `f32`, `p32`, `p32r`, `exp32`, `exp32r` and `ieee64` are in Verðandi's copies of those folders (`verdandi/mathkernel/F32/<folder>/`, from the tree's root); those of the other seven stayed in the authors' workspace."
- `THEOREMS.md`, line 59: was "rechecks it independently"; now "rechecks it from the compiled files (coqchk shares Coq's kernel code, so this is a second check, not an independent one)"
- `README.md`, line 6: was "**Theorems:** every proved claim is listed in [THEOREMS.md](THEOREMS.md); nothing else is claimed as proved."; now "**Theorems:** every proved claim of the kernel is listed in [THEOREMS.md](THEOREMS.md), the kernel-checked examples and plant refutations of `kernel/hardening/` among them; outside the imported documents of `orlog/` and `verdandi/` and the comments inside frozen files, nothing else is claimed as proved."
- `README.md`, line 12: was "statements written before their proofs, checked in Coq 8.20.1 with Flocq 4.2.1"; now "statements that their authors declare were written before their proofs (DECLARED; compose's own header claims no such order), checked in Coq 8.20.1 with Flocq 4.2.1"
- `README.md`, line 16: was "the kernel uses neither, and Ørlǫg is optional."; now "the kernel's proofs and gates use neither, and Ørlǫg is optional (the `corpus` steps of two frozen evidence scripts, `kernel/coq/orl/emit.py` and `emit2.py`, run Ørlǫg's arbiter)."
- `README.md`, line 43: was "so the corrections sit in a dated"; now "so corrections sit in dated notes: for `F32_Statement.v`, `P32_Statement.v` and `EXP32_Statement.v`, those of 2026-11-14 beside Verðandi's byte-identical copies (`verdandi/mathkernel/F32/<folder>/`); for `sincos32i` and `sincos32z`, a dated"
- `README.md`, line 53: was "HELD on 2026-11-10 to"; now "HELD (the consoles of `f32`, `p32`, `p32r`, `exp32`, `exp32r` and `ieee64` are in `verdandi/mathkernel/F32/<folder>/`, the rest only in the authors' workspace) on 2026-11-14 to"
- `README.md`, line 68: was "failed at the row they target."; now "failed at rows their change should reach (ARGUED: the expected rows were not written down before the runs)."
- `README.md`, line 70: was "read coqchk's axiom list or a statement hash given from outside;"; now "read coqchk's axiom list (only the harness does, on two folders), and their anchors are freeze-list hashes the authors computed, not the owner;"
- `README.md`, line 89: was "Does not show: a proof; another host or compiler; MPFR's own correctness, which is trusted."; now "Does not show: a proof; that the transcription equals the law at patterns other than the 2,096 compared (Coq's own evaluation of the law has not been run on every input); another host or compiler; MPFR's own correctness, which is trusted."
- `AGENTS.md`, line 11: was "written before their proofs and checked in Coq 8.20.1 with Flocq 4.2.1 (`kernel/coq`)"; now "checked in Coq 8.20.1 with Flocq 4.2.1 (`kernel/coq`; ten of the thirteen statement files declare that they were written before their proofs, which this tree does not show, and `compose`'s says it makes no such claim)"
- `AGENTS.md`, line 12: was "exhaustive measurements that hold them (`kernel/hardening`, `kernel/evidence`)."; now "canaries that test them (`kernel/coq/gate`, `kernel/hardening`). `kernel/evidence/` is withheld with the law draft; the exhaustive sweeps of kernel functions in this tree are Verðandi's records for sqrt32, rsqrt32 and exp32 (narrow was swept at five binary64 values per finite binary32 number, except the values of magnitude at or above the largest binary32 number), under `verdandi/mathkernel/F32/orl/`."
- `AGENTS.md`, line 17: was "the kernel uses neither. Ørlǫg is optional:"; now "the kernel's proofs and gates use neither. Ørlǫg is optional, except for the corpus mode of the emitters (`kernel/coq/orl/emit.py` and `emit2.py`, and the five emitters in `verdandi/mathkernel/F32/orl/`), which runs Ørlǫg's arbiter (`orl.py`); apart from that,"
- `AGENTS.md`, line 44: was "All run in the pinned Coq image (Coq 8.20.1, Flocq 4.2.1)"; now "All run in a container image with Coq 8.20.1 and Flocq 4.2.1 (its recipe is not in this tree and no file under `kernel/` names it; the harness consoles print the sha256 of the coqc and coqchk they ran)"
- `AGENTS.md`, line 44: was "with `kernel/coq` mounted read-only:"; now "with `kernel/coq` mounted read-only, except for the folder gate, which writes `<folder>/out4/` and `libcache/` inside the tree it judges and so needs it mounted writable:"
- `AGENTS.md`, line 48: was "- the minimal harness: `python3 -B kernel/hardening/harness/harness2.py --src <coq-root> --list <folder>/FROZEN4.txt"; now "- the minimal harness, for a folder with a `Closed.v` (only `ieee64`, `sincos32i` and `sincos32z` have one; version 1 held on `sincos32i` and `sincos32z`, this version on `sincos32z`): `python3 -B kernel/hardening/harness/harness2.py --src <coq-root> --list <folder>/FROZEN4.txt"
- `AGENTS.md`, line 114: was "Every proved theorem is listed in `THEOREMS.md` with its statement file, its closing theorem and its evidence; a theorem that is not listed there is not claimed anywhere."; now "Every closing theorem of the kernel's folders is listed in `THEOREMS.md` with its statement file and its gate verdict. Other results checked by Coq in `kernel/hardening/` (the 45 plant refutations of `plants/PLANT-LABELS.md`, the examples of `examples/` and `big106/`, the narrowing probe of `r7-probes/`) are stated in their own files; `THEOREMS.md` names them and marks them as not candidates."
- `PROVENANCE.md`, line 12: was "| `verdandi/` | the Verðandi repository |"; now "| `verdandi/` | the Verðandi repository (github.com/Dedoc-9/Verdandi; the pinned commit is four commits past 577bc2a, the last main pushed there from the owner's checkout before the import) |"
- `PROVENANCE.md`, line 14: was "| 11 | f20ccb5f5f46c86db04545c88fe4592f2a5b093ea8b885b0074d3a0fa915a59d (all root files but PROVENANCE.md) |"; now "| 11, plus the four manifests | f20ccb5f5f46c86db04545c88fe4592f2a5b093ea8b885b0074d3a0fa915a59d (all root files but PROVENANCE.md and the four manifests) |"
- `PROVENANCE.md`, line 25: was "`kernel/law/`, `kernel/hardening/`, `kernel/evidence/`: named files and folders of the workspace"; now "`kernel/hardening/` and `kernel/notes/`: named files and folders of the workspace (the law draft and its T2 sweep, `kernel/law/` and `kernel/evidence/`, are withheld: the import was assembled without `--with-law`)"
- `THIRD-PARTY.md`, line 4: was "What this repository uses from other authors, and how. Nothing below is copied into the repository."; now "What this repository uses from other authors, and how. Nine fdlibm 5.3 source files are copied into the repository, in `verdandi/mathkernel/ORACLE/src/` (Copyright Sun Microsystems, Inc.; their notice permits use, copying, modification and distribution if it is preserved). Verðandi's graybox re-implements fdlibm 5.3's sine, cosine and atan2 algorithms, with fdlibm's constants and FreeBSD's later correction to atan2, in `verdandi/graybox/web/sim.js` and `verdandi/graybox/rules_ref.py`. Verðandi's characterization tooling (`verdandi/mathkernel/CHARACTERIZATION/tooling/`) imports gmpy2, python-flint and mpmath. None of these is in the table below, and nothing in the table is copied into the repository."
- `THIRD-PARTY.md`, line 15: was "The licences of Coq, Flocq, MPFR and CoqInterval were read from the Debian copyright files inside the pinned image"; now "From the Debian copyright files inside the container image of the kernel's runs, the licences of Coq, Flocq, MPFR and CoqInterval were read (DECLARED; no record of the reading is in this tree)"
- `THIRD-PARTY.md`, line 16: was "What was checked in the tree (2026-11-17, by search over the assembled tree):"; now "What was checked in the tree (2026-11-17, by search over the assembled tree; no record of these searches is in this tree, and two of their results, the SPDX count and the copyright holders, were corrected after an audit of the same day):"
- `THIRD-PARTY.md`, line 17: was "`AGPL-3.0-only` (238 files)"; now "`AGPL-3.0-only` (245 files in the import)"
- `THIRD-PARTY.md`, line 17: was "no copyright line names a holder other than the owner, apart from the Free Software"; now "copyright lines name only the owner, apart from Sun Microsystems, Inc. in the nine fdlibm 5.3 files of `verdandi/mathkernel/ORACLE/src/` (and in three records of `verdandi/mathkernel/` that cite those lines) and the Free Software"
- `LICENSING.txt`, line 3: was "This repository is offered under two licences."; now "This repository, apart from the nine fdlibm 5.3 files noted below, is offered under two licences."
- `LICENSING.txt`, line 23: was "The copyright holder offers the whole repository under both licences."; now "The nine fdlibm 5.3 files in verdandi/mathkernel/ORACLE/src/ carry Sun Microsystems' notice and stay under its terms; the copyright holder offers his own work in this repository under both licences."
- `LICENSING.txt`, line 25: was "None of it is copied"; now "Nine fdlibm 5.3 source files (Copyright Sun Microsystems, Inc.) are copied into verdandi/mathkernel/ORACLE/src/, and the graybox in verdandi/graybox/ re-implements fdlibm's sine, cosine and atan2 algorithms with fdlibm's constants; nothing else of it is copied"
- `kernel/notes/LIMITATIONS.md`, line 7: was "## The five older functions (folders f32, p32, p32r, exp32, exp32r, ieee64)"; now "## The radian and logarithm functions (folders sin32, cos32, log32) - **Proved about Coq graphs only.** Their statements are about graphs over Flocq's real-number model (no overflow, one zero). No IEEE-level statement, native program, exhaustive sweep or backend exists for them. SIN32 covers binary32 x with |x| <= 13176795 / 2^23 and COS32 |x| <= 13176794 / 2^22, in radians (a little more than a quarter turn and a little less than a half turn each way); LOG32 covers 0 < x < 2^128. Like the five below, they state no rule for the sign of a zero, for infinite or NaN inputs, or for overflow. ## The five older functions (folders f32, p32, p32r, exp32, exp32r, ieee64, compose)"
- `kernel/notes/LIMITATIONS.md`, line 10: was "finite binary32 inputs within stated domains;"; now "finite inputs within stated domains (numbers of the binary32 format; for narrow, binary64 values);"
- `kernel/notes/LIMITATIONS.md`, line 14: was "- **A comment in a frozen statement cites a file that is not here.** The comment at line 195 of"; now "- **Comments in the tier's frozen statements and freeze lists cite files that are not here.** Line 1 of every folder's `FROZEN4.txt` says an older `FROZEN.txt` is kept beside it; none is (the five in this tree, of f32, p32, p32r, exp32 and exp32r, are beside Verðandi's copies in `verdandi/mathkernel/F32/`). `coq/compose/COMPOSE_Statement.v` cites the folder's `STATE.md` (line 5) and a probe, `RvCompose.v` (line 13); `coq/sin32/SIN32_Statement.v` line 28, `coq/cos32/COS32_Statement.v` line 31 and `coq/log32/LOG32_Statement.v` line 41 cite `DESIGN.md`; `coq/sincos32/SINCOS32_Statement.v` line 9 cites `DRAFT2-Graph.v` and `proto_turn2.py`; `coq/sincos32z/SINCOS32_IEEE_Zero_Statement.v` lines 8 and 18 cite `zero-sign/MEASURE-run1.txt` and `zero-sign/MEASURE-step-run1.txt`. None of these is in this tree. The comment at line 195 of"
- `kernel/notes/LIMITATIONS.md`, line 22: was "and it is measured on all 2^32 inputs"; now "and it is measured on all 2^32 inputs through a C transcription (not in this tree), shown equal bit for bit to Coq's evaluation of the law at 2,096 patterns"
- `kernel/notes/LIMITATIONS.md`, line 31: was "conversions make it immune."; now "conversions should make the turns kernel immune (ARGUED from the measured ranges of its intermediate values on finite inputs, each a zero or of magnitude in [2^-400, 2^400); no run has had either mode on)."
- `kernel/notes/LIMITATIONS.md`, line 37: was "**One host, one compiler, one Coq release** (Coq 8.20.1 with Flocq 4.2.1)."; now "**One host, one compiler per program, one Coq release** (clang for the older functions' C programs and rustc for the Rust backend of their corpus step, GCC 14.2.0 for the turns kernel's exhaustive measurement; Coq 8.20.1 with Flocq 4.2.1)."
- `kernel/notes/LIMITATIONS.md`, line 38: was "entries that affect that release; none is triggered by this tier's own sources, the constructs behind most of them"; now "entries that affect that release and one unclear (REPORTED: read by agents of the authors' model family; an adversarial check upheld 45 of 46 labels). The tier does use Coq's virtual machine: its entries, and #16891, which the tier's `field` calls reach, are covered only by coqchk's re-check without the virtual machine. The constructs behind most of the other entries"
- `kernel/notes/LIMITATIONS.md`, line 40: was "**The older folders' gate does not read a statement hash given from outside**, and only two folders have also"; now "**The eleven older folders have no anchor of the owner's**: the gate runs behind their verdicts were given freeze-list hashes the authors computed. Only `sincos32i` and `sincos32z` have the owner's own, and only those two folders have also"
- `kernel/notes/LIMITATIONS.md`, line 44: was "Wrong or stale comments inside frozen files are corrected, without touching them, in"; now "Wrong or stale comments inside frozen files are corrected, without touching them: those of `F32_Statement.v`, `P32_Statement.v` and `EXP32_Statement.v` in the notes of 2026-11-14 beside Verðandi's byte-identical copies (`verdandi/mathkernel/F32/<folder>/`), those of `sincos32i` and `sincos32z` in"
- `kernel/notes/CORRECTIONS-2026-11-16.md`, line 7: was "audit agent, not re-checked."; now "audit agent, not re-checked. [Added after the import into this tree: the paths below are those of the authors' workspace. `mkf-ext\<folder>\` is `kernel/coq/<folder>/` here, `gate\` is `kernel/coq/gate/`, and `src\SINCOS32_IEEE_Zero_Statement.v` is `kernel/coq/sincos32z/SINCOS32_IEEE_Zero_Statement.v`; `STATEMENT-FROZEN.txt`, `STATEMENT-ZERO-FROZEN.txt` and `harden-probes\runs\` are not in this tree.]"
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 1: was "why the reduction's integer differs from x there, and only there"; now "why the reduction's integer differs from x there, and nowhere else at or above 2^23 in magnitude"
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 10: was "the frozen shapes of `mkf-ext/sincos32i` and `mkf-ext/sincos32z` at binary64:"; now "the frozen shapes of `kernel/coq/sincos32i` and `kernel/coq/sincos32z` at binary64 (the `ext-work/` files this note names are in the authors' workspace, not in this tree):"
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 16: was "Not proved: that +2^106 is the only binary32 input where N(x) differs from x. That is MEASURED over all 2^32 inputs by"; now "Not proved: that +2^106 is the only binary32 input with |x| >= 2^23 where N(x) differs from x (below 2^23, N(x) is x rounded to a whole number, ties to even). That is MEASURED on the 1,761,607,680 finite inputs with |x| >= 2^23 by"
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 29: was "- e <= 103: x + CN is exact"; now "- 23 <= e <= 103: x + CN is exact"
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 36: was "So N(x) differs from x only at x = 2^106."; now "So, for x >= 2^23, N(x) differs from x only at x = 2^106."
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 42: was "no file read claims N(x) = x without it."; now "two earlier review records of the authors' model family, kept in their workspace, do claim N(x) = x for every |x| >= 2^23 without it; a dated note beside them corrects them."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 8: was "In `stage3/`, each `<tag>/S.v` is the gate's planted file, byte for byte; for the nine shape plants it is cut before its first eq_refl tie, the line where the gate refuses it."; now "In `stage3/`, each `<tag>/S.v` but one is the gate's planted file, byte for byte (`i_core_bound_2p200` has none: its planted lemma is restated in its `Refute.v`); for the nine shape plants it is cut before its first eq_refl tie, and the gate refuses each at the tie of the shape it changes, which is that first tie only for shape-narrow-add."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 11: was "candidates' own theorems (IEEE_SINTURN32_proof, IEEE_COSTURN32_proof, IEEE_TCST_proof, sinturn32_exact)."; now "candidates' own theorems (IEEE_SINTURN32_proof, IEEE_COSTURN32_proof, IEEE_TCST_proof, sinturn32_exact) in 33 of the 45; the other 12 (ten sincos32z rows, i_prem_sin_no_finite and i_core_bound_2p200) use none of them and compute the planted claim with `vm_compute`, all but z_nonfinite_cos_unstepped helped by the lemmas of `stage3/R4Lib.v`."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 83: was "with the T2 harness would settle it (candidate slice)."; now "would settle it."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 85: was "The planted file itself does not compile past its first tie, and that tie is where the gate refuses it."; now "The planted file itself compiles up to the tie of the shape it changes and fails there, which is where the gate refuses it; only for shape-narrow-add is that the first tie."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 91: was "An exhaustive comparison is possible with the T2 harness (candidate slice)."; now "An exhaustive comparison is possible."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 92: was "Not refuted; argued probably true by the overclaim audit of Turn 227 (the cosine's value before narrowing is near 1 for every finite input)."; now "Not refuted, and not known false (the gate's own entry says so). The overclaim audit of Turn 227 reported one of the gate's two ROUTE ONLY plants (this one and ieee-mul-toward-zero) probably true; that it was this one is the assistant's account (REPORTED; the audit's reasoning was not kept)."
- `kernel/hardening/plants/PLANT-LABELS.md`, line 112: was "Evidence that each is refused (READ, own; the assistant's own gate runs of the frozen candidates):"; now "Evidence that each is refused (READ, own; the assistant's own gate runs of the frozen candidates; the two gate consoles named below are kept in the authors' workspace, not in this tree):"
- `docs/paper/SYSTEM-GUARANTEES.md`, line 212: was "the general lemma the law's proof needs is not written yet."; now "this tree holds no proof of the general lemma the law's proof needs."
- `docs/paper/SYSTEM-GUARANTEES.md`, line 315: was "The law of section 3 is not proved."; now "This tree holds no proof of the law of section 3."
- `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md`, line 18: was "whose proof must take this input as its own case (f is 0 everywhere else, 2^53 here); that lemma is not written yet."; now "which must hold at this input too, where f is 2^53 (0 at every other finite input with |x| >= 2^23); this tree holds no proof of that lemma."

</details>

sha256 before and after: `AGENTS.md` 4841da869d8a6e2c1f34804f1411cb5ae3995bbfe9afac282830535979d960f5, e965393a41aa54e11245372ec6babcfea4c29ddccdf755ab746c08336278c285; `LICENSING.txt` de1d9e8a47cc3fca1735a8707d4909c4a04dd22997c16aa809393b28e9780105, 4abc58d6db5c687e09971a09ba102a50afb86134402cb5bd44214967c69b7928; `PROVENANCE.md` 5826f61ec34d536371794f7fb176d3499a5df582c5894237aed90a789322837e, 237cf33ec55b7a4a0346aa64fd3c5d22344bdbec014a34d279bb47c58652fafa; `README.md` f3bad9d5a2f5f2f7fd7cd49fcb116eece8caa3cc7e1d1f76cbe53404b65ce5bd, 200987c9cbc99e405fdac52310d770801fb2950bbe610d8f84c7313274a47e20; `THEOREMS.md` 27f6c7234907817d43455fed54d56eb4cfca21b48e7a68762dd49dc8481734ed, e15b0ca9934d8053a56776233b465dcc527a54b7d4cdc9252061bfb8bc26b27c; `THIRD-PARTY.md` cda96fe9f23186d1c0f1b5ba37bd6f9baea4a940125bab9e0eca0e737c2cb746, d97c68d41e79695de1b9e8522481212a507ac399e92b6a4e41f695194b3e731f; `docs/paper/SYSTEM-GUARANTEES.md` 673db8c5fde881d0c4f731c1595be8e2a8eed3237e2b8d1c7c57f95b96eb99ae, cd1b3466adace9a078e9b1ff73e7eceda884d489cdf4c2b628487096ddb1b003; `kernel/hardening/big106/BIG106-NOTE-2026-11-17.md` a0602341d5d4f6ffe97e9ed928fb1dfa73d717d67a7b5efd1cd0bfe7c0c22c27, ffc917b666342f54e806fa9a45c49b19a1c2d5554daa1195edd412e737522dc1; `kernel/hardening/plants/PLANT-LABELS.md` 9976cefa12fb9e481a20120ec490e5c0ba9cf75e6f3093ed50f453f3cc5b0b53, 7389613de51a1c08fd382013e60585272820487c1626d9429a0e3b9d6563c09f; `kernel/notes/CORRECTIONS-2026-11-16.md` 8ed9773c3fd173e361728573827e63bfd0044ca26c8dcbd296c1fe988e4b7b48, 73a0e236eec7a8ea1910c546aac3ea8b7669d6dd834bbbf1603d9f443ea6c5ba; `kernel/notes/LIMITATIONS.md` 460cab4a0bf52230d538387a59b8ee96d90c9e32634638684952dbb29efa107a, b97da394d1287ff1a53f642bca9033730c803bdfad8d5465b88e346c5d13acd4.

## The Linux CI, the floating-point state guard and the guarantees ledger (2026-11-17)

Added by the pull request `linux-ci`, prepared by the assistant at the owner's request of 2026-11-17; it is
part of this tree only if the owner merges it. No file of the import is changed by it, and no proof source,
statement, freeze list or gate: a Linux workflow and its image, a guarantees ledger, the manifest check, and
a prototype floating-point state guard with its gate.

| File | sha256 |
|---|---|
| `.github/workflows/mathkernel-linux.yml` | ccdb18335443011ebc9f183ecfd3cd8c9e1732d44ec535bb8d7ea2a06fab1082 |
| `ci/mathkernel/Dockerfile` | 0dc712cbafab7dbba07684a229cf35b73241106ef6db437eb1a1e7783fbcf593 |
| `docs/GUARANTEES-LEDGER.md` | a16ad9cafde68092b6d82ab9edd2a709ad546e747afb984dd5b17b3f1aab5f31 |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | 737bb1a98093f6de7cf5bf3ccb00a166a954df4568488aac2f7da5ea2ba26252 |
| `kernel/runtime/README.md` | b1000e7ca5822cf7e06092e6a31511ecdbd6b5ce3cd1d523b703a470137bccfe |
| `kernel/runtime/check_fpenv.py` | e3b0959ce742fd9e37ea056143ac7ec0138ba3c4527a1b5ab8020798aee2ead5 |
| `kernel/runtime/mk_fpenv.c` | f3abea02ccf388b85ddb5116b07774a629d28beab693daf83a7f2101c4e74555 |
| `kernel/runtime/mk_fpenv.h` | 1f82a206b0c2043248cd4ad8b9ac2707e2f814a8fe4deb063478e79c4715bbd6 |
| `kernel/runtime/test_fpenv.c` | 15c521b0fd7f9030654a87b63483fe7a9740af3571387a90dcc32ee403d1b814 |
| `tools/check_manifests.py` | 6fa83222e8104b3e59a73e2d94c7435da6605f5929efd63e2bdf32b54770de01 |

## Ruling D1 (a): G6's row

Carries out the owner's ruling D1 (a) of 2026-11-17.

- `docs/paper/SYSTEM-GUARANTEES.md`, line 83: was "| G6 | A statement is read by someone outside the authors' model family before its owner adopts it | process, NOT MET yet | — | — |"; now "| G6 | A statement is read by someone outside the authors' model family before its owner adopts it | MET at statement level for the 13 statement files: one model outside the authors' family (ChatGPT, OpenAI), administered by the owner, 2026-11-17 | the review's findings, verified against the files (docs/GUARANTEES-LEDGER.md §1) | that a human outside the authors has read them; that the statements say what their owner meant; the law (G2), which was not in the review |"

sha256 before and after: `docs/paper/SYSTEM-GUARANTEES.md` cd1b3466adace9a078e9b1ff73e7eceda884d489cdf4c2b628487096ddb1b003, 2cfadd0d4bd544aab5f73158b2db508821f6e8d21f360fdb22c87d785df85047

## The linux-ci change, revised: the guard (2026-11-17)

Revised after a review of the six commits above by agents of the authors' family, each finding confirmed by a second agent; part of this tree only if the owner merges it.

| File | sha256 before | sha256 after |
|---|---|---|
| `kernel/runtime/README.md` | b1000e7ca5822cf7e06092e6a31511ecdbd6b5ce3cd1d523b703a470137bccfe | ac840d342c71e7c38fc0ef581c65c2794e09bbd6e007403671adc14606f52912 |
| `kernel/runtime/check_fpenv.py` | e3b0959ce742fd9e37ea056143ac7ec0138ba3c4527a1b5ab8020798aee2ead5 | f6f6f47995c85f7d835d7891206a504a5a76eea1e318f65eb398c3e972eb1df0 |
| `kernel/runtime/mk_fpenv.c` | f3abea02ccf388b85ddb5116b07774a629d28beab693daf83a7f2101c4e74555 | 2f746a49c6b98edb62b7933ff7f6d736f49f2f98979d7d1c88d66ea23b0a135e |
| `kernel/runtime/mk_fpenv.h` | 1f82a206b0c2043248cd4ad8b9ac2707e2f814a8fe4deb063478e79c4715bbd6 | d1a760305dcc620488ee8d9a0f03700a04053afaa510160c542531cf57054981 |
| `kernel/runtime/test_fpenv.c` | 15c521b0fd7f9030654a87b63483fe7a9740af3571387a90dcc32ee403d1b814 | f3c9e4720823070d7d9be89b305fd335b0464ab1bc2343cf14ecc7fceaf6615d |

## The linux-ci change, revised: the workflows and the image (2026-11-17)

Revised after a review of the six commits above by agents of the authors' family, each finding confirmed by a second agent; part of this tree only if the owner merges it.

| File | sha256 before | sha256 after |
|---|---|---|
| `.github/workflows/integrity.yml` | (new) | b1161b44a27d7805e73b8bbb1d1c245610b7022f2da49ccfac18d0ed972154ae |
| `.github/workflows/mathkernel-linux.yml` | ccdb18335443011ebc9f183ecfd3cd8c9e1732d44ec535bb8d7ea2a06fab1082 | 0ee2cd2373b009c8193e882effed27396898d44f2c9be473a3a3b57dfa9b087e |
| `ci/mathkernel/Dockerfile` | 0dc712cbafab7dbba07684a229cf35b73241106ef6db437eb1a1e7783fbcf593 | fef148b6668e8d732f0231539c68983541a012aaa54cf7230cd7aee6c91e69b5 |

## The linux-ci change, revised: the manifest check (2026-11-17)

Revised after a review of the six commits above by agents of the authors' family, each finding confirmed by a second agent; part of this tree only if the owner merges it.

| File | sha256 before | sha256 after |
|---|---|---|
| `tools/check_manifests.py` | 6fa83222e8104b3e59a73e2d94c7435da6605f5929efd63e2bdf32b54770de01 | 355e5ff4e88015007c70aa38064f18e9f86034994575479668dd970491fefd83 |

## The linux-ci change, revised: the ledger and the CI document (2026-11-17)

Revised after a review of the six commits above by agents of the authors' family, each finding confirmed by a second agent; part of this tree only if the owner merges it.

| File | sha256 before | sha256 after |
|---|---|---|
| `docs/GUARANTEES-LEDGER.md` | a16ad9cafde68092b6d82ab9edd2a709ad546e747afb984dd5b17b3f1aab5f31 | 3fd71c8d54108d6a42616c5bfe4b9a790d162d4efd141e381dd4e40d9399ff7e |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | 737bb1a98093f6de7cf5bf3ccb00a166a954df4568488aac2f7da5ea2ba26252 | 3bfb369d499f23129dc6d6b80bcbba2ed572de2dc198461ffbedae7865c460c0 |

## The linux-ci change, revised: the agent brief, third parties, required checks (2026-11-17)

Revised after a completeness review of the commits above by an agent of the authors' family; part of this tree only if the owner merges it.

| File | sha256 before | sha256 after |
|---|---|---|
| `AGENTS.md` | e965393a41aa54e11245372ec6babcfea4c29ddccdf755ab746c08336278c285 | c878d7b265a76544a6223a405c075b0a322a62f670c6c965007056f786761d19 |
| `THIRD-PARTY.md` | d97c68d41e79695de1b9e8522481212a507ac399e92b6a4e41f695194b3e731f | 055f0f8d5af9590a1f77bc536a9036d8edd6037075b4e676e6d538d160face33 |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | 3bfb369d499f23129dc6d6b80bcbba2ed572de2dc198461ffbedae7865c460c0 | a493580ad00a7d3a1628e6a5b738b3427419cb096bcca6147629ddf5706f88ad |

## D8: the lines that disagreed with G6 and G4 (2026-11-17)

Present in this tree only by the owner's ruling D8 (a). The texts, old and new, are in the commit that carries this section.

sha256 before and after: `docs/paper/SYSTEM-GUARANTEES.md` 2cfadd0d4bd544aab5f73158b2db508821f6e8d21f360fdb22c87d785df85047, 2c0096fb556e168cd8a662a30912cd63378ce0eeed684ef4bcbd25fc754fa76c
sha256 before and after: `README.md` 200987c9cbc99e405fdac52310d770801fb2950bbe610d8f84c7313274a47e20, 5b94957a82aabdd20de22c651fcd0dd9440a01be63fd89d47d2b475ce256c1cd
sha256 before and after: `kernel/notes/LIMITATIONS.md` b97da394d1287ff1a53f642bca9033730c803bdfad8d5465b88e346c5d13acd4, 19e898ad17f9f026c5a542384b43285c64be20270677d30fd8fc6cbf02bd48c9

## The base image's digest read from the build output (2026-11-18)

Found in the first CI runs; part of this tree only if the owner applies it.

| File | sha256 before | sha256 after |
|---|---|---|
| `.github/workflows/mathkernel-linux.yml` | 0ee2cd2373b009c8193e882effed27396898d44f2c9be473a3a3b57dfa9b087e | 5bb305936a06b9b316f311e6d9f567c59bccc89b8c0ce8e506d1357a5d34a1c7 |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | a493580ad00a7d3a1628e6a5b738b3427419cb096bcca6147629ddf5706f88ad | d99d28e62efc09f2331b9e0513d9a08c4cca48f20cc41576bbfa1d896f585d6e |

## D10: regraded from the first CI runs (2026-11-18)

Present in this tree only by the owner's ruling on D10's texts.

| File | sha256 before | sha256 after |
|---|---|---|
| `README.md` | 5b94957a82aabdd20de22c651fcd0dd9440a01be63fd89d47d2b475ce256c1cd | e825218a045ce9ad517b82809a2c26da75ad31e298c6b4c4389adb3eb31e206d |
| `docs/GUARANTEES-LEDGER.md` | 3fd71c8d54108d6a42616c5bfe4b9a790d162d4efd141e381dd4e40d9399ff7e | 718ab8e09b8f782933812fa06c96d7a6af8835a664106ef95f0319d4ea4bc327 |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | d99d28e62efc09f2331b9e0513d9a08c4cca48f20cc41576bbfa1d896f585d6e | 3e5411b8db017d82cc301c19ca1514373cbf2aa2ab7737157916e75488dc5df3 |
| `docs/paper/SYSTEM-GUARANTEES.md` | 2c0096fb556e168cd8a662a30912cd63378ce0eeed684ef4bcbd25fc754fa76c | 265327ed44718cf01837bd11aedd611e729edd00d7bb326dd1e533e9087e8003 |
| `kernel/notes/LIMITATIONS.md` | 19e898ad17f9f026c5a542384b43285c64be20270677d30fd8fc6cbf02bd48c9 | 5d75e982597d617b346e0f0cc9260848c5ef80f39dd188531d3b523fe4f190fb |
| `kernel/runtime/README.md` | ac840d342c71e7c38fc0ef581c65c2794e09bbd6e007403671adc14606f52912 | 00d36516d6595cb94625b41f16715ef3761e491e9ae4326ffa7ced1599699397 |

## E5: human readers dropped from the paper's next steps (2026-11-18)

Present in this tree only by the owner's ruling E5 (a); the facts that no human outside the authors has read the statements stay.

| File | sha256 before | sha256 after |
|---|---|---|
| `docs/paper/SYSTEM-GUARANTEES.md` | 265327ed44718cf01837bd11aedd611e729edd00d7bb326dd1e533e9087e8003 | 971c7d41b13adafde353e7052de64318a68fbbde5b1199446e3d726bfd4e4780 |

## The GPU note: bit-exact results on Direct3D (2026-11-18)

Added by patch 0016, prepared by the assistant at the owner's request of 2026-11-18; it is part of this tree only if
the owner applies it. An engineering note, graded claim by claim, and one sentence of the paper pointing to it; no
proof source, statement, freeze list or gate is changed.

| File | sha256 before | sha256 after |
|---|---|---|
| `docs/paper/SYSTEM-GUARANTEES.md` | 971c7d41b13adafde353e7052de64318a68fbbde5b1199446e3d726bfd4e4780 | 36fd4f6bed04be3c69899b081895ed778a976ccd0c51b5f3855068834e86ab6d |

| File | sha256 |
|---|---|
| `docs/engineering/GPU-BIT-EXACTNESS.md` | 0a75782fa5e845f495ad54b6dadc70d1b597f54da302316be646d68e59ca9245 |

## Ruling SY-1: `verdandi/` re-pinned at Verðandi's commit 94d7c28 (2026-11-22)

Carries out the owner's ruling SY-1 of 2026-11-21: a change in the Verðandi repository reaches this tree only by a
re-pin. `verdandi/` is now pinned at commit 94d7c28a446cb3df7f0b01d59687f716c9ecb8f8 (tree
79de963f1e7c2f93ed8616eb2396a83d4bbfc879), as the dated note in `PROVENANCE.md` says. The two files it changes
since the import pin are taken from it byte for byte; the manifests are not rewritten.

| File | sha256 before | sha256 after |
|---|---|---|
| `verdandi/mathkernel/F32/README.md` | b03522b16f033201acd86c3384c40ff2897eeb748807e2badf886a7df22ffe1b | a8fa998eacbcc70f9a4785c7c0d56c66c747c196df2692b0b89efd4378a2ad05 |
| `verdandi/mathkernel/F32/LIMITATIONS.md` | (new) | 6d57f39beeab7436e220f867bd043fa356f8fe1a9d42b5aad66573b0bb313567 |

## Ruling S280-25: the records C2 (b) removed, counted (2026-11-22)

Carries out the owner's ruling S280-25 of 2026-11-22. C2 (b)'s scan removed 40 records, 31 under
`verdandi/shell/attest/` and 9 under `verdandi/kernel/attest/`: the 40 rows of the table under ruling C2 (b)
above. The 9 under `verdandi/kernel/attest/` stay removed under C2 (b), as the 31 do. No file changes with this note.

## Drift classification (SY-2) (2026-11-22)

Carries out the owner's ruling SY-2, adopted as S280-26 (a) on 2026-11-22. Each file of `orlog/` and `verdandi/`
that differs from the commit its folder is pinned at has a row: its sha256 before (at the pin, or `absent`) and after
(here, or `removed`), and one class. `RE-PIN <commit>`: the file now equals the original at that commit; for these
rows, before is the file here before the re-pin. `SKULDD-ONLY BY RULING <id>`: a change ruled for this tree alone.
`SENT BACK Verdandi patch <file>`: a change that goes back to Verdandi by its own route, a patch for the owner to
apply to Verdandi's main; the file stays listed until a re-pin makes it equal to Verdandi's. Rows are appended,
never rewritten, and for a file the last row naming it is the one that counts. A path writes the host's name as
`<host>`. `tools/ci/drift.py` holds these rows to the originals' commits and `tools/check_manifests.py` (row M4) to
the manifests.

`orlog/` has no row: none of its files differs from its pin. In `verdandi/`, the two files of the re-pin to 94d7c28
(ruling SY-1, the section above) are RE-PIN rows. `verify/RUNGS.md` and the 40 records removed are Skuldd-only under
ruling C2 (b) (its section above; for `verify/RUNGS.md` as the owner's ruling S280-24 (b) of 2026-11-22 says, and for
the 40 records as S280-25 (a) says). The other seven files changed here go back to Verdandi under ruling XR-1:
`tools/rung.py` by rung 0268's patch, the three files that name an engine by one patch and the three that withhold a
tool's name by another, both made on Verdandi's main 94d7c28 to apply after rung 0268. Each application is the
owner's act and waits for its own restatement.

| File | sha256 before | sha256 after | Class |
|---|---|---|---|
| `verdandi/mathkernel/F32/LIMITATIONS.md` | absent | 6d57f39beeab7436e220f867bd043fa356f8fe1a9d42b5aad66573b0bb313567 | RE-PIN 94d7c28a446cb3df7f0b01d59687f716c9ecb8f8 |
| `verdandi/mathkernel/F32/README.md` | b03522b16f033201acd86c3384c40ff2897eeb748807e2badf886a7df22ffe1b | a8fa998eacbcc70f9a4785c7c0d56c66c747c196df2692b0b89efd4378a2ad05 | RE-PIN 94d7c28a446cb3df7f0b01d59687f716c9ecb8f8 |
| `verdandi/AGENTS.md` | 823e7962c7ddebfde830d64c4230b30ad145e4af3bf82ca806cb11a24e1eae47 | 63ad624f8496d7414b4ddae562ca7491a7d00311842982a6a25e6165671bcfce | SENT BACK Verdandi patch 0002-docs-an-engine-s-name-replaced-by-future-engine-word.patch |
| `verdandi/README.md` | 3a10c7f033d22367739b808650ab8ee5aae0cf5bd0903802cc5cd784e1dd0015 | a1e6ccecbf5301d22ea15f574f3d0c6a718eda30f591183c165b3d1ac9721449 | SENT BACK Verdandi patch 0002-docs-an-engine-s-name-replaced-by-future-engine-word.patch |
| `verdandi/art/README.md` | ec63c93d7be8bfa9ecb0eab9dcfdb2adc6c549af4fbeac6ab33a06bf3e915857 | c541568f4078fb17c638b855b7d23699236994420ecf6babf16fe71da543f191 | SENT BACK Verdandi patch 0002-docs-an-engine-s-name-replaced-by-future-engine-word.patch |
| `verdandi/docs/RESEARCH-FINDINGS.md` | b5ba19c29e0f018137cec4b850e21d1767833d52e8e70f550326c7825030c142 | 22c4b6ab617e53a6fc2160cb9e88ebbd4d52bc371edde445cbbe05f45fc6639c | SENT BACK Verdandi patch 0001-docs-one-tool-s-name-withheld-in-three-documents-as-.patch |
| `verdandi/docs/ROADMAP.md` | dfbbad4bc79a2e101e11b4eb79ed977c561111fe1250283d96ad81ca9e5eda27 | 2702339d36f1f4aafa2310f968e6d5aa810802d1e60cbb0927a3e91f6e1c67d0 | SENT BACK Verdandi patch 0001-docs-one-tool-s-name-withheld-in-three-documents-as-.patch |
| `verdandi/docs/STUDIO-APP.md` | fb7ab399cd1c3d5d729794930e102b59630900516d64431b387eb8485f41bbda | d9ea819deff1d77847cf68b907918b010f0edde8c01e22632ee0f6d79f0cbdd0 | SENT BACK Verdandi patch 0001-docs-one-tool-s-name-withheld-in-three-documents-as-.patch |
| `verdandi/tools/rung.py` | ef1a05823ff3a10c4c619cf015b0acde2450219f8543f336063a8c6a2a99fe47 | de429a26f76514109ab6640ab261131297f53e37a96a4140c94d7426087e908e | SENT BACK Verdandi patch 0001-fix-rung-0268-RUNG-0-at-both-layouts-reads-from-its-.patch |
| `verdandi/verify/RUNGS.md` | 03083a73852306cbc4c4f236c8625106aff72b437c746a09d582a19fd384cabb | f6b6034829e028ef562c570f1e2c935b85d815ebfd8ea019c5e9ab8c7ff140ef | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/bearingfast-<host>.json` | 77dd5d9aff326828db836322f982be8d6750d1837a1e32674e5c01065f1d5296 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/bearingsweep-<host>.json` | cd7344f013e9aa0a95f159cd9f7c2ee7a05804aa3e3021664e31aaece2121e72 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/bench-<host>.json` | b03468815b66c048c63187d981d9e5bbe11beb9e165bbbe43ec5cc147422fa19 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/breakdown-<host>.json` | fe4d11d6bab8c19afaf1c0f350c4d5e57193b784d79a5599b8ba6e60a6711842 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/emit-breakdown-<host>.json` | 3602cfea630c3b54ee153e096698216337f23f0167996f280c87bbc92ef1db50 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/gauntlet1b-<host>.json` | b139058ac3d086a501b30f56fba2517b7301fb99ca3cd05682ea82156fe0dff2 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/gauntlet1c-<host>.json` | d6aea51d52fac2924d1be6d45c8f28e9fd964e2d01aa352969a66e8b0a83b3a1 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/gauntlet2-<host>.json` | 7bc318e0ebb70d0f252c1c4f707b31a62fa316865721d9a3db4ea9b540776c1a | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/kernel/attest/locality0-<host>.json` | d43a385d1b643ee05b45ddc51859bf01a951400c2284dfb45abd778bc03e7ded | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/allocreuse-<host>.json` | 9fd864742aa97afdf794de2a4d35964b8fcb60abc64782aaa3167fa9c8464082 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/allocreuse-confirm-<host>.json` | a44c27a09f3b3db2a305920d1cf7ef5194f31e6d8e311b1d0386fa37c80ba268 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/allocreuse1-<host>.json` | 6a0d1e59f7acbe0482df0183f18e598f2568e9bf313159d389aa9625109f7cab | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/allocreuse1-confirm-<host>.json` | 2a8071e45aedd2f5252c2949c3e477e2c8f8aee2e230d5aefdf3b8a9e080bd59 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/drift-<host>-s1-r1.json` | 2ef5576bb780845f5e9d8d3044716e0539020ce51edd96d921abdd359e2b5ee2 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/drift-<host>-s1-r2.json` | 52475c6410cccfe552545dc02d3a06f762a10824eb173c72ddc8baf2263c018c | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/drift-<host>-s1-r3.json` | 88f961168ff4fa84221723254ac72f06f94d73f0a08f21c2e6dbc97291466154 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/drift-<host>-s1-r4.json` | 1c2cce8d502bac08811d88d0b3cd2dda5ad0f1c78974800c767e1019d677b5fe | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/framesplit-<host>.json` | d5e66f5ac6b35b9a2443bbe5461d7dd5d63aa2c6d68bade4a7e9160ee4d1706d | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/framesplit-confirm-<host>.json` | d4c981e982b5d34ef6237fff38086a37a98df7093d50a370a0c271acb6698fce | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/latency-<host>.json` | 8a5c9c344df04ea6e890375565ffb522ab4d111b18f63599d913aa862803168b | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/latency1-<host>.json` | e0b4be3ab43d5658fd69736b68095ccff794504ccb8eeca3c43d2a3742f6a1e7 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/latency1-confirm-<host>.json` | 9ec5202e1d138d734ac97f1523286d13583461836e2818109e4273fd215109fb | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/latency1r-<host>.json` | b6e18ff1da80447772c441bfd0aa3f5026a982942588e924c1d23f016263e33d | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/latency1r-confirm-<host>.json` | 2cb209877aa87559b00726a1573d8e2083ba465eb6ece5bccdcb5657d8294170 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/liveloop-<host>.json` | b754bdfe42e696d54d44a2cc042fbc6854f5950f91ef5559654d4efc5fcc3fe3 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-47ae5de3c73a.json` | c95c5bb11740d9cd69a2490636fd2843dc8f624b7205d0cc3aac8f74567aa161 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-5290c848217d.json` | 8dfd490500b59b288894393f35e2571ecf8c0698386df937120ff831693337f4 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-a0861e0e837b.json` | cb2caa541ddc9d4cc73431466b1ee04b537eb5b19f4202d6d447226236d2d421 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-aa850e786b6f.json` | 21e8f70c174fba05ff13fde7b76fc9e726307c54443612e9f9747260eec51505 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-b28e42be62c4.json` | eb53c112e554f78a6819ff63d9365410edc6dcc67a6ed004f7f51454574b084d | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-dd874eff3a69.json` | 41e9840d3aed8739d4e7a87bb9d0194e88e08aa58cb6a1daaa9bb4a7d5431608 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-e9dafb482675.json` | 7c80b9949059aa88aaba195e87484d7204bc42a550a1f71db2e01eb3eff17967 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/livesession-<host>-eaf27cf3fc0c.json` | 82f21729a95314f795399a65165a2324e959a17faaa8b8a21e9e28867e2c5b2f | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/present-<host>.json` | 54f5d92dad552c952579f7f6879dea6ac355be6955bfdb160537c0a114cf3934 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentexact-<host>.json` | 3aee31654edc5249a2f7fa978d514b36c491a8641202991154a497093b5bdc4d | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentexact-confirm-<host>.json` | ff165ff860e182307121cb53da3d22d1c98eb5e09579268af53ec84379e9dd06 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentscale-<host>.json` | d64e1747bdc441b821a89a8fb201e48004c4d629cecd7f094100201a179fe013 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentscale-confirm-<host>.json` | d749c0e49e9bdd510e117e7cb83a4c61a37077f4dfef0d00e83a8c05675e183e | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentstretch-<host>.json` | 68462613641dee9288dff428e5a8629d6e8555100380e7a3771bed1dc4d06187 | removed | SKULDD-ONLY BY RULING C2 (b) |
| `verdandi/shell/attest/presentstretch-confirm-<host>.json` | ca89362b18a92c315341dc34cb0f0c11b506bfc5b6747c4f3dd14e4aa8f4fc9b | removed | SKULDD-ONLY BY RULING C2 (b) |

## Push A: the hardening batch, eight gated folders, the boundary map and the records (2026-11-23)

Push A's files as they stand against the commit of patch 0016 version 3, which carries the GPU note at version 3 (the
note's row above names that version's sha256, as 0016 version 3 writes it). The batch carries the owner's rulings
recorded for it (ST-1, TR-1, BM-2 (a), SY-1, SY-2 as S280-26 (a), XR-1, U5, the Turn 280 sheet and its addendum, S282,
S283, S284, IB-1): the CI judge's hardening and its tests; the gated folders `floor32`, `ceil32`, `sincos32n`,
`exp32a`, `rti32`, `order32`, `bits32` and `fclink` in `kernel/coq/`; `BOUNDARIES.md`; `kernel/records/`;
`kernel/notes/FCLINK-TRUSTED-2026-11-22.md`; the drift workflow and its tests; and the documents that describe them.
The first table lists each changed file with its sha256 before (at that commit) and after; the second, each added
file. This file and `PROVENANCE.md` are the manifests check's own and have no rows: their changes are the sections
above (SY-1, S280-25, SY-2) and this one. Under ruling S284-1 (a): the change S283-2 (b) made to `BOUNDARIES.md` was
predicted by a file kept outside this tree, `ext-work/p2/s283/b1-build/PREDICTIONS-b1-build-2026-11-22.txt` (sha256
666fb5427041526a9bcac8f4e462446b3d2fc69ae24d7899f5cf8dc643bfc945).

| File | sha256 before | sha256 after |
|---|---|---|
| `.github/workflows/integrity.yml` | b1161b44a27d7805e73b8bbb1d1c245610b7022f2da49ccfac18d0ed972154ae | 5c6c61ae7c671fbbd22b7ed901ea2def8ff5308c4e1303b62e897bc0fdd26241 |
| `.github/workflows/mathkernel-linux.yml` | 5bb305936a06b9b316f311e6d9f567c59bccc89b8c0ce8e506d1357a5d34a1c7 | 72f7975c5ab45628d585b3009f621cddee33c4fd802a2c144c0919f4e527e050 |
| `AGENTS.md` | c878d7b265a76544a6223a405c075b0a322a62f670c6c965007056f786761d19 | 2043600547eabdf36325cde08fe4ae96d4c3d082ebf5dfdff9f397c3526c0603 |
| `README.md` | e825218a045ce9ad517b82809a2c26da75ad31e298c6b4c4389adb3eb31e206d | 5dd6a2935bd51205f86c9a0e754efbcfe3108de5214624f8871144eb8cc1c498 |
| `THEOREMS.md` | e15b0ca9934d8053a56776233b465dcc527a54b7d4cdc9252061bfb8bc26b27c | ac7ee649ddbf442e2eff67dd479609938e5cb6ef3ca3031898e2e4f6df45b81f |
| `ci/mathkernel/Dockerfile` | fef148b6668e8d732f0231539c68983541a012aaa54cf7230cd7aee6c91e69b5 | 4cab83d903f543b3dd9f4391ab7372c6c2d256f6b56409c5462d7d18aaa43b34 |
| `docs/GUARANTEES-LEDGER.md` | 718ab8e09b8f782933812fa06c96d7a6af8835a664106ef95f0319d4ea4bc327 | 9e4c47aa188fe92b2308c531a983c9d90c95e4a1d61cd178421dded0e8be3b5e |
| `docs/engineering/MATHKERNEL-LINUX-CI.md` | 3e5411b8db017d82cc301c19ca1514373cbf2aa2ab7737157916e75488dc5df3 | da015bd413722442e16c29b6eb44421c40d60b2cf077bf78c13fcfe1ce90b474 |
| `docs/paper/SYSTEM-GUARANTEES.md` | 36fd4f6bed04be3c69899b081895ed778a976ccd0c51b5f3855068834e86ab6d | bb59995c3a68f99e26bef34c74f56042b0f662468456e4bc4a571280adc07e2c |
| `kernel/notes/LIMITATIONS.md` | 5d75e982597d617b346e0f0cc9260848c5ef80f39dd188531d3b523fe4f190fb | cc704255ef5a5111e274bbfa1e914426a061e0f138dc3ae9948a987deefaaad6 |
| `tools/check_manifests.py` | 355e5ff4e88015007c70aa38064f18e9f86034994575479668dd970491fefd83 | 99055e86cfcfb0dad86e537292285b2e10bf9334e4e866b3c85338d3b29e1fce |
| `verdandi/mathkernel/F32/README.md` | b03522b16f033201acd86c3384c40ff2897eeb748807e2badf886a7df22ffe1b | a8fa998eacbcc70f9a4785c7c0d56c66c747c196df2692b0b89efd4378a2ad05 |

| File | sha256 |
|---|---|
| `.github/CODEOWNERS` | 21ac17c32495ae9631d103ae9cac09c8bb1b621b8fd4310fb5aa5c011c43a68a |
| `.github/workflows/drift.yml` | 690b85361bdbca642764ffbd9c8aa21c53dd7c89717701e6b552674dd2a7b22f |
| `BOUNDARIES.md` | 81687711c540ca166a53c02182663eec5f8e8691c5a5f06cd481de128904780e |
| `ci/mathkernel/EXPECTED-TOOLCHAIN.txt` | fde0bdb465ace340f2033fe5f77242d3edff0569ed4a3dbcece695b0baefe8c8 |
| `docs/engineering/BRANCH-PROTECTION.md` | 4b7ecb8be166f29447b1822c5eb44477a65565185b73232b7413d718eeed676b |
| `kernel/coq/ANCHORS.md` | eb468f8a780ddf5339275deb1b693d13993a65c90e9af12345dc7cb1ae52016e |
| `kernel/coq/EXPECTED-CI-LIBRARIES.txt` | b86c82ffc4c440da1c6ad7459b496ddfd5b38ec62a9d91fdff02bb25bdd9e77d |
| `kernel/coq/bits32/BITS32_Statement.v` | c3e65cb7285ddf438145e6fc7284e7749013472b3d4b06f8fc211d345b043e53 |
| `kernel/coq/bits32/Bits32Dec.v` | 1cffafdfe6a79e92b9e080c549de92d0ae7f1fa46d059c47023ee707214a11cb |
| `kernel/coq/bits32/Bits32Link.v` | 448f1405f649903a3cd9a8a79fc59309132e3b143b641bf64b761583d9f89618 |
| `kernel/coq/bits32/Bits32Spec.v` | d4ea1594c30451c6cb42ace43fd5764eed03251d77afb59ba945ed48d46a40d7 |
| `kernel/coq/bits32/Bits32Widen.v` | da39bfd9f5c216e443dde05bfbac94ca87756419d3263a4bdb4036334bd68d5a |
| `kernel/coq/bits32/Closed.v` | 2c0667aecc20ebce9ad234437a7e2f69a7b06776abfae32855167f61b787e48a |
| `kernel/coq/bits32/FROZEN.txt` | f6660ea4c6538b37ff18cf9cf2bc7f2b5bd2229391fcc6062b542d4ae10b738d |
| `kernel/coq/bits32/FROZEN4.txt` | 820e15169d17c2395d9abce4ad687e4e4eb17208bbb0ce2abb77650771d0ca06 |
| `kernel/coq/bits32/Identity.v` | e527cdc8e314b7c97fc4a75a860eabe9743d3b910fc21d890f1f415dde0f0b0a |
| `kernel/coq/bits32/gate.json` | 97ab8aeebf3dd27986a350fe5a30ca39d0576e872aa3666a4578c2e7f6ab4bdb |
| `kernel/coq/bits32/plants/BITS32_Statement_g10_widen_inf_sign_flipped.v` | d0c6cf307e8ce68ecbc1f1c2535ecb3067a74da35c0195726ee283445610480b |
| `kernel/coq/bits32/plants/BITS32_Statement_g11_finite_on_snan.v` | 9ad1fec4230839e0881d0a4a6ae4a150b638d8e5a82d9d76f5c1649ce50d4bfc |
| `kernel/coq/bits32/plants/BITS32_Statement_g1_no_quiet.v` | 4d50f1b694e38327459c830706b95051ca6cb68cb0bdbdf8aeed396ca1637d26 |
| `kernel/coq/bits32/plants/BITS32_Statement_g2_direction_swapped.v` | 15e03907ba945da0294583e726206c17e32b25f2673e6aea8652c5da49e67d23 |
| `kernel/coq/bits32/plants/BITS32_Statement_g3_zero_plus.v` | 47496d536ce30f70716b534a4f5fd6d3a5ba96777f994fd909a5838a28a847b7 |
| `kernel/coq/bits32/plants/BITS32_Statement_g4_k_off_by_one.v` | 19b111c8f6d69e9ffcf889e416140946b13dbbcf71a8f2e82f6d4ed9ce6d4e8f |
| `kernel/coq/bits32/plants/BITS32_Statement_g5_widen_zero_unsigned.v` | 5478ed55101e6edd13744477ad285ac48c5e4faa9258c8eb795c2328554167ab |
| `kernel/coq/bits32/plants/BITS32_Statement_g6_store_nan_included.v` | 5b297364c1d54d689a6fae4f318d6429854bd2563831886c499aa0cd2946d213 |
| `kernel/coq/bits32/plants/BITS32_Statement_g7_widen_nan_to_inf.v` | 53ff2b4a30d87514f5f69009c47a1ecb788c13ea76e4adcb4ec62004f54401eb |
| `kernel/coq/bits32/plants/BITS32_Statement_g8_range_wrap.v` | c7eeebceeaf86f372ba6144ae74ba5e88ccab6fe415be36d21f921ad409279a1 |
| `kernel/coq/bits32/plants/BITS32_Statement_g9_nan_sign_flipped.v` | b14f1e8d200d3e57eec74be0e1b6b9a34ccba87176cfb2ba63f889af78cc24ee |
| `kernel/coq/bits32/plants/Bits32Dec_admitted.v` | 0d22f7deef5755dd8676370d2894567c892845aa52a62fabc562c228c4a93814 |
| `kernel/coq/bits32/plants/Bits32Widen_axiom.v` | f18a8f09321921aab8cf1a5fc5f91d991418d7e2c3a0c0b9328e37ff9fc94f3f |
| `kernel/coq/bits32/plants/Closed_guard.v` | b65f043669036ebc78a7a230ed416efa65a69d38ad04d5fc8d26cad059b8ed84 |
| `kernel/coq/bits32/plants/Closed_seven_of_eight.v` | 21881dd513ec70eb8163d0a701af02fc84112381ccbb3355c8a0656c4b3955e5 |
| `kernel/coq/ceil32/CEIL32_Statement.v` | 2a2f21678a040cc49896146001e26f42e1258118b9496271afdde6aab0dd37a3 |
| `kernel/coq/ceil32/Ceil32.v` | d2eafd51d8a4eb71f9f586d318ca9c0709eb9826d1a6af68e1e12d4736e616cf |
| `kernel/coq/ceil32/CeilIEEE.v` | 403456e8e40a5ad263aea960cc97542a5c64e71515f09b2c998fff437aa851e7 |
| `kernel/coq/ceil32/Closed.v` | 77f1cd02e1c6cff60f9cad6642459db0385807775d13e1d94398ce09e78693f5 |
| `kernel/coq/ceil32/FROZEN.txt` | c1de4e89183c7493c4eb59af1882c0344ddea963a312f206829a3bf92ee577ff |
| `kernel/coq/ceil32/FROZEN4.txt` | 468d29c862d8e14338fb1434f24cc839e1c8a003a9ebb09ca60c5b6c9ce5ad23 |
| `kernel/coq/ceil32/Identity.v` | 1a490769256159ac29b61574aa1e96255dd4e0455ee33715128d51601c6daaa0 |
| `kernel/coq/ceil32/gate.json` | d7af1ba2950f14400acefbec5fdbbd8e009d25b9501108c219b02781c27c6fcf |
| `kernel/coq/ceil32/plants/CEIL32_Statement_format64_exact.v` | 60f399e05e0e23a774daa57916a0960358c40b5a09fe887d00027a9ad204e13f |
| `kernel/coq/ceil32/plants/CEIL32_Statement_ieee_other_mode.v` | cda223444f4d90ff7ddaafc3d92566624d7b9828c0cda049029e02d9f47ca2a6 |
| `kernel/coq/ceil32/plants/CEIL32_Statement_no_step.v` | e4779230ccc821e7eef84d8a22bc0da798756c53d37514009d9200c4ce2daa6f |
| `kernel/coq/ceil32/plants/CEIL32_Statement_sign_always_plus.v` | 41a65ac5a8a25deb16b1ac116e8b0fea5d8e91ec94f78fa5dd5bebe94a556373 |
| `kernel/coq/ceil32/plants/CEIL32_Statement_value_no_finite.v` | 8f3d25ad9fce11892ddb16d015499155dde8a5def0b50d4fa509e19217091d92 |
| `kernel/coq/ceil32/plants/Ceil32_admitted.v` | 74fae90cddc1e30582885d9e88bec2ff080ddac5141cdeedd1120471a13c6f8d |
| `kernel/coq/ceil32/plants/Ceil32_mul0_axiom.v` | 0e2384a5acdf041f11cfa986b9f3620a3634672077114db0395f5731aeaccef7 |
| `kernel/coq/ceil32/plants/Closed_four_of_five.v` | 1ebef64cdf94f5b7ef9fc84fc8219f572f203d8085dec6031834b5b7f55c85c1 |
| `kernel/coq/ceil32/plants/Closed_guard.v` | cb5047136ca2b1f608445aeb97b0186342718566678ccb186b1b9feed8924d60 |
| `kernel/coq/exp32a/EXP32_ADJ_Statement.v` | aa266075c8a8560f23c96467892c9fd14a2eb232d93b7bc281cff0584120c493 |
| `kernel/coq/exp32a/Exp32Adj.v` | f0e9bd24aa185f04994a4a48c4f17fbf229e5b7246c56a0569aba81d2a76928f |
| `kernel/coq/exp32a/FROZEN.txt` | 6b15bfb9208e8a1d7b846d59efcf77a5c7d98f33315a8441c23218d6d300c58e |
| `kernel/coq/exp32a/FROZEN4.txt` | 08c9c09cd28ffcea6cac962e759c3d056fc87e3cbb7b14e64729c20cc95ed2b4 |
| `kernel/coq/exp32a/Identity.v` | b4c69bc9925c7eb0287d6f9c99f0d0dcd17082f2bf18f3b58d7a5185866eed85 |
| `kernel/coq/exp32a/gate.json` | 4951e310284a9d0c113c127929809feac70f44f55f8beba43898aa66bd6d9eae |
| `kernel/coq/exp32a/plants/EXP32_ADJ_Statement_claim_at_xmax.v` | 0b5942a97ea4136059a78c607a2830efdaf5cc8f10d4226ebd23ced35b10fa86 |
| `kernel/coq/exp32a/plants/EXP32_ADJ_Statement_not_format.v` | c7a974bb96d1cdffaa639d9786305351f16091d7ffdc6d0873361256b9a0c88c |
| `kernel/coq/exp32a/plants/EXP32_ADJ_Statement_xnext_two_steps.v` | 1a0e539eaa9236ac4c9c3d4f083d98a9ee7c1055ad95f9d970912b1fc48b9fa0 |
| `kernel/coq/exp32a/plants/Exp32Adj_admitted.v` | 4d52dc65029c007e3bc07ac3103db2b0896b0f9c85d3e7caeb5d9bb183f9867d |
| `kernel/coq/exp32a/plants/Exp32Adj_four_parts.v` | 3a69ca220dca21badabb7eb2564b372f77d21a401224e013156dcec61e813fd1 |
| `kernel/coq/exp32a/plants/Exp32Adj_guard.v` | 109cb2408c7c19e6c865cdb2cf2195a2cd20152e529f77865c233236452b0476 |
| `kernel/coq/exp32a/plants/Exp32Adj_sharp_axiom.v` | 3f3ce57ebc8f1413c10bc14d0c7cc8e2b66beae657b55eec8400f746755273b5 |
| `kernel/coq/fclink/CPrint.v` | 1a2be9a46d46ab8956765cc21a38be79e8f71600fbe9ea37c579ab7739859ed5 |
| `kernel/coq/fclink/Closed.v` | 2c04676e31918be724660dde13d481e48bbdf2284444b2b744dcb56968396d75 |
| `kernel/coq/fclink/FCLINK_Statement.v` | b974b59c98d88ee935a003a51e9895f01c6d316a48ec7d5332617c1f9396ea4e |
| `kernel/coq/fclink/FROZEN.txt` | 923501fba9f1015be3435614f810bbed401f109696cd8ffee234d5abe0a8d96a |
| `kernel/coq/fclink/FROZEN4.txt` | 96ac2c42d44ef185ac8b70ab12da628268ab1471907ac4a5df5a97d3305b0dfa |
| `kernel/coq/fclink/Identity.v` | c8f6199f4fd91d24859ed65321eb9bf8001337ecdd4c5345a5255f6f6c75a55e |
| `kernel/coq/fclink/KernelText.v` | aa89a5557f5b8cf10709206fe267ffdba68b93e2322f61b3e7384cf8323456e7 |
| `kernel/coq/fclink/Link.v` | 1f6efdcc7fd06a8bca8830e274c1902dd6cdb30d04e1fadf275251e5f5cd7dc5 |
| `kernel/coq/fclink/gate.json` | 45a301de80e80ffb4002828d1267c5574c368062e7414fe1ef6859fe55b37d88 |
| `kernel/coq/fclink/gen_kernel_text.py` | 79dca82136338b94a6ac13c54b6dc26ac4cbcb5a47b2b911b19a214ace90b7dc |
| `kernel/coq/fclink/plants/CPrint_sub_plus.v` | dec809c4e389b3eecc887bb3436b0c6ac293f9ccc3a3f2a88c37c4b11ba70583 |
| `kernel/coq/fclink/plants/Closed_guard.v` | 823aa2b21d6046a8f7f99ca50cced19cd04b99c939b6e0c032ae028c15a4f538 |
| `kernel/coq/fclink/plants/Closed_three_of_four.v` | 93cdd7f3cf3410ced07eef8d2a47a9a6968bd2689a1a6941ed7d0d4ec024457e |
| `kernel/coq/fclink/plants/FCLINK_Statement_fields_no_mul.v` | 404855a960d39fe983bebe91fc0028e4c953eb22fe7f5c36cace5afd6dba456e |
| `kernel/coq/fclink/plants/FCLINK_Statement_param_floor_ceil.v` | 1749c24077a74dfcc43b8c98d23381868f9cff0e2a9747b2b76b121cd4ee04ad |
| `kernel/coq/fclink/plants/KernelText_cst_big_2p22.v` | d423fa2b069e20d826ed4f2ce1359555fcc61858ad43598953e970f7336a08ad |
| `kernel/coq/fclink/plants/KernelText_cst_cn_odd.v` | 42bac4a79c331b7b4f7ec3ca71658f45d2d69ba4cad3e6dd7c1e1d8a93b485da |
| `kernel/coq/fclink/plants/KernelText_equiv_big_lt.v` | fca3fdd29bc649ae69d744d0264bcd92f8f567bcdb5154901cbdc917c07f3111 |
| `kernel/coq/fclink/plants/KernelText_hand_edited.v` | fea8c53b460aa8fbdf66b28ec4439b705e650c376fe9026b87cd8274c4b03ff1 |
| `kernel/coq/fclink/plants/KernelText_nostep.v` | b60828d1310d22569d7f8cf280fb6fa411cfffd3c231d5e93c234ba2c127a4b8 |
| `kernel/coq/fclink/plants/KernelText_op_lt_le.v` | fb280e6f3a13e284a24fb8e6ff4201777cb61040903f57cbf57989b1df1a4712 |
| `kernel/coq/fclink/plants/KernelText_op_lt_le_ceil.v` | b8cec0782e735486e657f981cdf7953fbdbcb775269d1e44b1a5edf76ae4f34b |
| `kernel/coq/fclink/plants/Link_admitted.v` | 80aa36941ebdf2c0c1f0324d6983c68fe9b43d55c18cd5c3c97323211bb7013a |
| `kernel/coq/fclink/plants/Link_param_axiom.v` | 5599628250baafc29e4214d58986012d198f8e9a00b073e8da5b5d9a064909c9 |
| `kernel/coq/fclink/sweep_fc2.c` | 924bd031c84172fd98203f1b755f1f63b8cc62aecd76bd6358273f00fc2a7005 |
| `kernel/coq/floor32/Closed.v` | 5db3fc8ecb56f3608db542e7f7ed7110bf89b1490657d7a264997b9cc270837e |
| `kernel/coq/floor32/FLOOR32_Statement.v` | 32109ba742e330fc72e41014efabe2f42403c1331425b03c91aba155e0a16c7c |
| `kernel/coq/floor32/FROZEN.txt` | e1a676f02422f6a8f1024240e829543dd8aac631c3eff6abead22b329802d2ee |
| `kernel/coq/floor32/FROZEN4.txt` | 62db0a2ec778fb51c5e274b6df8784ad18b67940c33b273174f6df59e69a4998 |
| `kernel/coq/floor32/Floor32.v` | ef9aa247ba285645a2cecb6f777aa3391124d6bd5d4febaf46c33a59f88c7b31 |
| `kernel/coq/floor32/FloorIEEE.v` | 643ae58992b4bfe6982904a2f4d83cbfb2c31a0fed2eada0b29e83c66fdc5fb5 |
| `kernel/coq/floor32/Identity.v` | 1e014ae71895cb73e0791b8bfb77bb8629af3ec43ba354c9339fe99a78ef3d5f |
| `kernel/coq/floor32/gate.json` | 46c0c5f810110fb1b393c3718030af0de906a013a5ee67772e866b014142d07e |
| `kernel/coq/floor32/plants/Closed_four_of_five.v` | c8c857f27ddb4cd1deae337c9687e4bd15ab6ea5a56318a8cba0381cdd24d456 |
| `kernel/coq/floor32/plants/Closed_guard.v` | fbda8593a3562ec5917d79c7682818fb52807de8c8ca189a47e0cdd3f91a7162 |
| `kernel/coq/floor32/plants/FLOOR32_Statement_format64_exact.v` | 84328e7f7c59f5812bd62b73a8d0b313901358a95e1f609acf62486a63c92dda |
| `kernel/coq/floor32/plants/FLOOR32_Statement_ieee_other_mode.v` | 20ab6e9e4d57f3687fd964ebb2e493a407f03d9116685be1b2b620d66d79984c |
| `kernel/coq/floor32/plants/FLOOR32_Statement_no_step.v` | 0074c4492e8ee8325a094e7f6449b76dba56cb3850a2c4cc73468a8e738c3f28 |
| `kernel/coq/floor32/plants/FLOOR32_Statement_sign_always_plus.v` | 3a210ba12d3a9c2f582e5e69b22a36b1bbcf51e47b517116e4d12e97b2980695 |
| `kernel/coq/floor32/plants/FLOOR32_Statement_value_no_finite.v` | 0bfa208aa47bd2dd1501ef7952efe4ab9472870d6e88926d15ad1184118f78a8 |
| `kernel/coq/floor32/plants/Floor32_admitted.v` | f09c07a163186bc02e08a4d32954eae4705dc57e3167961859edb29734fc6090 |
| `kernel/coq/floor32/plants/Floor32_mul0_axiom.v` | 5fb70efc5b363a77e82d24f75407f7bd4e36774a9abeb2efc9ce28154c4b56ab |
| `kernel/coq/order32/Closed.v` | b3a24d49b71c6d3bf286fee3d4d742e4cabee62fee9ea686bedf8acd44fc3da2 |
| `kernel/coq/order32/FROZEN.txt` | 0e665e29e87907a68a56ae41f558b889e7e1ee97587184e74aaaae6dc22e74a4 |
| `kernel/coq/order32/FROZEN4.txt` | 0ea74cf1267a35e0d988c2c1efb8be5f5457c24d3f189de0ca1f75bc37133484 |
| `kernel/coq/order32/Identity.v` | 7971f41330b12899533ecb8a3e54d9cba03beb6d54994e0ffa0a1607f0dba2c6 |
| `kernel/coq/order32/ORDER32_Statement.v` | aa229794a1b476c3da3488aa9db96ad150761dff6da22f0c9937d069bd17cbab |
| `kernel/coq/order32/Order32.v` | c9c886eef0406400739f1c914e86a17e6843ecdab8d8beeda22dd84fe21c3775 |
| `kernel/coq/order32/gate.json` | d66a9ce2be2e1311a303911b0ce5f2c247310f4fe35a50892c593f7bccde8f16 |
| `kernel/coq/order32/plants/Closed_guard.v` | 72f7a927a2c610c83beac7095d17215f5e9a3527cf7694917bdd44815b480c4d |
| `kernel/coq/order32/plants/Closed_ten_of_eleven.v` | 54b127319f1addc335ff79937573e521a9d24f56339f723323e46e363f0e64f1 |
| `kernel/coq/order32/plants/ORDER32_Statement_diff_one_only.v` | 7cb53a9079f3c69546d4110fb6a138b5a88c3a7d5556e1af7a24951f62ededa8 |
| `kernel/coq/order32/plants/ORDER32_Statement_eq_int_no_format32.v` | 49d96cc91fa0ba1460e276ab75701cb29f26ecff5d3db609f3c649f45eb9a92b |
| `kernel/coq/order32/plants/ORDER32_Statement_eq_int_opp.v` | 306a7d802762c9bc57f9924dd37c2b5f98b9f021e886fbb05f87de70d92e31c5 |
| `kernel/coq/order32/plants/ORDER32_Statement_fix_no_format32.v` | 8f7827f90140858d052b9f00e742c8ff9dc74ed31eb12d017029264d60e36dd6 |
| `kernel/coq/order32/plants/ORDER32_Statement_fix_opp.v` | 0dbfc59a6514c5b888a4a2004f81470f96fa9db876fbc2f138ea3f3033e47fed |
| `kernel/coq/order32/plants/ORDER32_Statement_idem_is_identity.v` | ce56c22dc7d490d3d3ad4d37ce238bbe3c43b570cd7833dde8c0d1c19d0deb33 |
| `kernel/coq/order32/plants/ORDER32_Statement_mono_strict.v` | 1b3396afb0edd8d14362c670f7905f319292dc47efa31a647315ddbef3a75f7b |
| `kernel/coq/order32/plants/ORDER32_Statement_neg_no_outer_opp.v` | 4af3f83e359971a6be264d35e078a88ecf0e6af519ea2ebac955c7d60fa5ebf1 |
| `kernel/coq/order32/plants/ORDER32_Statement_ord_leb_nan_premise.v` | 726c1b6d48fb44003b68b2881e0650f7bcc475692468ed2f8e45f7e49c46fe61 |
| `kernel/coq/order32/plants/ORDER32_Statement_ord_leb_strict.v` | afd0beed6306fbfb024621a752bb683033d1acbc5bffb8a522a83024dbf92391 |
| `kernel/coq/order32/plants/ORDER32_Statement_ord_nan_eq.v` | 324b5401a7c820a38e8d5bc1e869892d66e5a533cacb810ba32e663ff90c71d6 |
| `kernel/coq/order32/plants/ORDER32_Statement_ord_nan_nonfinite_premise.v` | 91b3341d63e9a68c108e15025e76e362154184eca85054dde4b6703e4dd20a8c |
| `kernel/coq/order32/plants/ORDER32_Statement_ord_r_swapped.v` | 89e4e5258117521a3683535671f25c833d7c1a106590de17d01e692d85eb1608 |
| `kernel/coq/order32/plants/ORDER32_Statement_total_eq_false.v` | df31c3d8bd8d7e273f218bac7c9f4fce1824c3584f28ac6f585ffaffde8d41e7 |
| `kernel/coq/order32/plants/ORDER32_Statement_total_eq_true.v` | 58f79b8b2307307e342e6ccb6e5737c55f10e9cec65840b7d8bc7d46e00a60d9 |
| `kernel/coq/order32/plants/ORDER32_Statement_total_nn_flipped.v` | 2a51a789a3ce983cf0eea16df85ca2150dc139ae17afbad26e9cd09fe8e816db |
| `kernel/coq/order32/plants/ORDER32_Statement_total_zero_reversed.v` | 6685c4fa475a274971823ac318cc537de1f5a400136ffc45ab22b77ceb498792 |
| `kernel/coq/order32/plants/Order32_admitted.v` | 22f6dc9e05ece809ef3fe12a2684cc5599576221fea59e3def7c7190bae8b683 |
| `kernel/coq/order32/plants/Order32_bleb_inf_axiom.v` | 3f1ef31d627cfa5fa39b0d25af3f679e678ec23f2b95f9a06e8c43e2c2bcdf46 |
| `kernel/coq/rti32/BnRTI.v` | e9a4a2541658b824e1b017be7e26ec33e0566706f6eb16ba89794b544615e525 |
| `kernel/coq/rti32/CeilRTI.v` | 1d3dd06014c1059e1b8f90c47c26dce7bb752092d72b630f3e3971c4cff82cd5 |
| `kernel/coq/rti32/Closed.v` | 38d0fcc04660ee4fb29e8775f4995bf87f694a5d599d3157674d600993f98d8c |
| `kernel/coq/rti32/FROZEN.txt` | b4ce0e49397bf61cdf78aed3102c75524dbb0a3c72a96da20bea6d278823ec5d |
| `kernel/coq/rti32/FROZEN4.txt` | 1f0c20067174f98ce74c4c9d7e3377ee204b9c5618e3d790a1d891175a41885f |
| `kernel/coq/rti32/FloorRTI.v` | 2c30b86368ea1843a9a667b781769d5a980e81a7a1c48a8998b391333891f6df |
| `kernel/coq/rti32/Identity.v` | ad20a4b47ed6bcd9d3027f6f5d8bb96b95e3ef4848fa66a695473c9525bd2d10 |
| `kernel/coq/rti32/RTI32_Statement.v` | c880889571705e6760d35e8fe9badab376b2d5e64e339bc45a658e5d58c119b7 |
| `kernel/coq/rti32/gate.json` | 8c6380ec11858aab2552cb77bdca28eb886fde1707af8998576d23a613d6b887 |
| `kernel/coq/rti32/plants/BnRTI_axiom.v` | b0ec9ffbae9f11076663937e2c2d2889021ddea953795ba3932fdba8ef8c456e |
| `kernel/coq/rti32/plants/Closed_four_of_five.v` | d466e3274f50eb96cf3a8f0c006cb2aabcb81358cc88940ce8e47cd19379543a |
| `kernel/coq/rti32/plants/Closed_guard.v` | 29822bfa5ddce0f82f7a618f511ec8e3c507b31b000076b86026448dfaad0dab |
| `kernel/coq/rti32/plants/FloorRTI_admitted.v` | be7fe48bcc9a24869d350f5a2e06881654fbd49b7aafa969eca50bacd059b6a7 |
| `kernel/coq/rti32/plants/RTI32_Statement_bn_other_mode.v` | 1e6bc5a23282d11a7ae3017181c4d395136ecdd9c5a7070ced4c719f308a50bc |
| `kernel/coq/rti32/plants/RTI32_Statement_cl32_strict.v` | eb2b0f185fdd7143bc44fdf1442ef84120c57f598d05fdf5a887599f155f796c |
| `kernel/coq/rti32/plants/RTI32_Statement_fl32_strict.v` | 92e4b8439acba9aca52e2c95ca0a8f7ee5563c68f20abcc5e43f51b4daf2c8ca |
| `kernel/coq/rti32/plants/RTI32_Statement_inf_may_be_nan.v` | c7824297d27615a049d78ee009d5dec8793c116b97f44708daf63bbc6b6c0ded |
| `kernel/coq/rti32/plants/RTI32_Statement_inf_sign_flip.v` | 74284be9a6e90ff254e9aa7b0ddb597c7618959bac2c73af3ce1d5eadc41fa83 |
| `kernel/coq/rti32/plants/RTI32_Statement_inf_to_nan.v` | db2fb182bb809951e7b0f0d58b4c5fa8e2047194aa889947db0c7b63e546242c |
| `kernel/coq/rti32/plants/RTI32_Statement_nan_not_nan.v` | cefa8d9828affbba60ac8505ce8ba1fe40e3f774d42f787414ffa1d364dc9740 |
| `kernel/coq/rti32/plants/RTI32_Statement_no_finite.v` | b05c5760d56c8322c965c04ff23724de50342b0f735847b9b427406c5d326fba |
| `kernel/coq/rti32/plants/RTI32_Statement_no_greatest.v` | 464b87c04564f73e62284e096e48cd35ef0ed0d6d54ce668fa4e570e5a361aaf |
| `kernel/coq/rti32/plants/RTI32_Statement_no_premise.v` | 1fac48b00995f29e4bbbee5be801918a653024166ccbfae34722a0df99b0f7a6 |
| `kernel/coq/rti32/plants/RTI32_Statement_other_mode.v` | 1263074f3a72b0230dc70ae5d28f222ced99452ba04a5fb4c8b2e5fc1ca4ab4b |
| `kernel/coq/rti32/plants/RTI32_Statement_zero_sign_plus.v` | 2a690879f5fec9c78e9d38f4284f966dfa8de8e6317bf096a2d7211a19d0126f |
| `kernel/coq/rti32/plants/RTI32_Statement_zero_sign_plus_up.v` | 2c7ffa35c48d6dd207d045f69b3808f4068bbf9ea49b2fe227ff16e69715ad52 |
| `kernel/coq/sincos32n/FROZEN.txt` | ec71114f25851e5e0ae03272c84973884ee06770a2c4ddda5210769c2ff775a6 |
| `kernel/coq/sincos32n/FROZEN4.txt` | 7cf75e2cc75e86c07110eee868c72e5db56e00f62001c91ad0193f57a15a3558 |
| `kernel/coq/sincos32n/Identity.v` | 0d082829c218f4cab642230549ecd15080103c7e045779fe3b84bf089c7f4e5c |
| `kernel/coq/sincos32n/Nonzero.v` | 52d8b452c4a5afe67ad7cade2046bac9b8093b875395eb1625b7704ce4b34c1c |
| `kernel/coq/sincos32n/SINCOS32_NONZERO_Statement.v` | b3ea4523f9a0f752a0c203046cc84e9115f6ed4d902014aeffae7ede59fe71ee |
| `kernel/coq/sincos32n/gate.json` | 9608f940b95bdd198ed187ecf6577b8744ff6d5a521f847eaa3f09aba28826be |
| `kernel/coq/sincos32n/plants/Nonzero_admitted.v` | 97de2497728dd2b4b9a9e477d813bc49869247f71bdca157bad2ad0e9ef45131 |
| `kernel/coq/sincos32n/plants/Nonzero_guard.v` | 47e7e22c5b30a60bd4779859fd4b3d60b0adcbbb0c247323e3f3f819e873db2d |
| `kernel/coq/sincos32n/plants/Nonzero_halves_axiom.v` | e8afd13a6b19cc24237b1869d8f5753151e7c901fa4c9a901a5d7f1757f645cc |
| `kernel/coq/sincos32n/plants/Nonzero_sine_only.v` | fdcaacdf0afe9cbb27316dbba9cb436b686036f5e9a350fae75ba041bac6c215 |
| `kernel/coq/sincos32n/plants/SINCOS32_NONZERO_Statement_cos_crossed.v` | fc6767a7ed65929402a35bde25f3715bcd43ebc91e06d88b2d2cfb223d7afc4c |
| `kernel/coq/sincos32n/plants/SINCOS32_NONZERO_Statement_sin_format64.v` | 4302a3425396f26555555d7f17670a4386c92e9c1d057113171285ad05eeef41 |
| `kernel/coq/sincos32n/plants/SINCOS32_NONZERO_Statement_sin_no_premise.v` | 3ca465ebd698a8350a816fe33c973423f94124c4ac2c7cf586182f6988d9742d |
| `kernel/hardening/features/PREDICTIONS-row4-2026-11-18.md` | 29d657f9e3e06f35a700f12bc1dce5c9ac5c2c5c433b53bf887e3514a1a7bc04 |
| `kernel/hardening/features/feature_row4.py` | 8bc817c866f8912c30c2ca357e5f4c3ecbe535ce380f89dc1859081ecf4e5262 |
| `kernel/hardening/features/make_feature_plants4.py` | b7587e22c7495975d59c2380aa8fc301c0fd5fa934685c42ccaabce3e683d0b3 |
| `kernel/hardening/features/plants4/decoy4_at_sign.v` | a29a52be31b460334c0e5200fcf352391ee9f21932ba2e8dd0334c34bd98232d |
| `kernel/hardening/features/plants4/decoy4_attribute_comment.v` | ddaa785dda6be570bd9dd7994b7ac095d9aa0ca1e20317d0624255a7e55eef88 |
| `kernel/hardening/features/plants4/decoy4_attribute_strings.v` | 198c359fcd586aada50dd99cd2562b57cc340ea181b432b5d3cfea746cde856e |
| `kernel/hardening/features/plants4/decoy4_attribute_words.v` | 3baabd822269fd48b2b3aed8f53b5be7d85f5fccdcd6c882d2fdbb4453be10ee |
| `kernel/hardening/features/plants4/decoy4_class_reported.v` | 13857753fe649dd7ce35b8d10aad2ca1721badd13688ba7c8e94ea9e7b7e53b4 |
| `kernel/hardening/features/plants4/decoy4_comment.v` | 1e2c10c6bc31cfc047f0f8fa8af1f7eaf19b2cae5aa2fd4c938dd9d14da0738c |
| `kernel/hardening/features/plants4/decoy4_from_require.v` | 2075acec659ab8791b44774cc1f22d8ef4cc6914f1cf5b9897ec5cfcc14f7a6d |
| `kernel/hardening/features/plants4/decoy4_identifiers.v` | 9711e841306a820eecd0302d002fd7b8d1d8b5f3891a6cffabac46c43cc817b6 |
| `kernel/hardening/features/plants4/decoy4_instances.v` | bbc8c70e48a1ddb645211f6a064572e8350aaa9ea6f706a67af5d05d92e4be08 |
| `kernel/hardening/features/plants4/decoy4_load_comment.v` | dfa67d3ebdcf9c4873c943cdebdb257959ccd398e73860e86a3ae02f2633365d |
| `kernel/hardening/features/plants4/decoy4_load_identifiers.v` | cf03262564dc792140a604eab49dc5a8252b1cff323664e06fcee57aa5ae5597 |
| `kernel/hardening/features/plants4/decoy4_load_string.v` | 46690a359ff492836ea11ae36909021a1c7e4ed0e524a42563337aa0a00bdedb |
| `kernel/hardening/features/plants4/decoy4_lowercase.v` | 8c24b9d84cf6323b565908b9a1a3b1b9a8cbbd49f61a214413cb00645d78d51c |
| `kernel/hardening/features/plants4/decoy4_module_comment_string.v` | 8354878fafc4bdc9c3c84da66605834eb07cfa78bc1d1dc5dc067bc147685f7d |
| `kernel/hardening/features/plants4/decoy4_module_plain.v` | 03abb03486aafce96b98018604241881d74609f3c4213d9fcf89a4d542e2d55c |
| `kernel/hardening/features/plants4/decoy4_module_plain_forms.v` | e5217fe4a6d36eefc33baa5b40aa153c7f6d500c0c93529156e01c7bd268327d |
| `kernel/hardening/features/plants4/decoy4_module_word_comment.v` | 8ca73d6dd4d96bf28efb2c7e7d32d1fc0e5912b91e4f76f188d069082c099338 |
| `kernel/hardening/features/plants4/decoy4_module_words.v` | 0b1a6631a066aec9efb87d47d3e266e08fdd7339ea5218d6223c02c567ef86ba |
| `kernel/hardening/features/plants4/decoy4_other_attributes.v` | a0b4976e4d823591a34df39ef1b80f49fc64114b59b4df699cb89943dac1e2bd |
| `kernel/hardening/features/plants4/decoy4_state_comment.v` | e94e4de2f19ba9e90d400921dbbb9bcfef23d4e2116ec570b8ecfd9000917786 |
| `kernel/hardening/features/plants4/decoy4_state_string.v` | 624b54702c32c3f542847ef6c3f5ef2d076c9a82a6fc5a83e423a449c58ebafc |
| `kernel/hardening/features/plants4/decoy4_string.v` | 356ca441941d126632c29b2907f77c3abd34d004262fd1479623e07026122291 |
| `kernel/hardening/features/plants4/decoy4_string_in_comment.v` | 394fc8273150ae1aa8fcec973d97f4a99ebb3c2cef61da98f05b9e456fac6848 |
| `kernel/hardening/features/plants4/evade4_conjectures_after_string_in_comment.v` | 6e1a3f4126d43004fd4e60becb17ba9aa89ce21f866c813f8598c5ca825bfda1 |
| `kernel/hardening/features/plants4/evade4_context_after_string_in_comment.v` | ccf0c228b31ace551d2507f71e267d573e0ca062d83ac26f76b2dc4d3b2b42b1 |
| `kernel/hardening/features/plants4/evade4_module_comment.v` | f73c2147f86e0a7c56d63b4015a9dee0d6fdb3c1c63f246507fb305b326b08af |
| `kernel/hardening/features/plants4/evade4_program_attribute_bracket_in_comment.v` | 0be822c4abccb33cac21cabf9988951d69a52a196f6f4fba444be07c4607de43 |
| `kernel/hardening/features/plants4/evade4_program_attribute_bracket_in_string.v` | ac5a4783e47ab681fef26f8ccb1cecbf65ba144d21a924986198fc4c75743548 |
| `kernel/hardening/features/plants4/evade4_program_attribute_multiline.v` | 0b32aadf21a6d273eebfb0bc7b710d9fefb8c5c34a8a5347df065ef11e614adc |
| `kernel/hardening/features/plants4/evade4_split_declare_instance.v` | dc33d7b6db957ffe650563500002c296b5456991a681e63be54b0fff2eb1faf4 |
| `kernel/hardening/features/plants4/evade4_split_solve_all_obligations.v` | a5d80402174404dac6739347801d5b8ba3bdf6ea2bb02b2c77527b61495ca248 |
| `kernel/hardening/features/plants4/input4_absolute.txt` | ec48307e536c4947bfa8a0dc5f586a7d6a3a2493b988caa822bda7351e96f745 |
| `kernel/hardening/features/plants4/input4_backslash.txt` | 9eca1cce7e992b7be6134e2d4795ce6414b2e29917070a658198cce0815f881f |
| `kernel/hardening/features/plants4/input4_bad_line.txt` | 4c332a6f5b61698daccda87eda302d854e0b19ae3cdd94e11c96a324d49f27ac |
| `kernel/hardening/features/plants4/input4_dotdot.txt` | ff28954f06dffc5673af4737fbcf8cdec6062a8a2e47aec3827225d0180d679b |
| `kernel/hardening/features/plants4/input4_duplicate.txt` | 427ea8ddbde3ac052146faa7dff670b5f6595f11cd31da0a14f14e701db8cb90 |
| `kernel/hardening/features/plants4/input4_empty.txt` | 7ca4d0ee58fa3af484c46f826063ba7fadcfae7e1c8d724066a197dd3c20181a |
| `kernel/hardening/features/plants4/input4_hash_mismatch.txt` | 6a518a01f21e80117feece9f65fa8ecbdfd358c41080dd9122706b37ae64db26 |
| `kernel/hardening/features/plants4/input4_hidden_cr.txt` | 32ff4d31de0ac50fd70d6db9b7dbb58732f712e130a89aa1667f7248394a258c |
| `kernel/hardening/features/plants4/input4_hidden_ff.txt` | b4b177a113a651192a2edf1b1e59e95a8778cc43d1decf88606c5a230fcccb00 |
| `kernel/hardening/features/plants4/input4_hidden_lf.txt` | e5f24f063e5b37153b04bcda83cff9e5dfa1fbc386c377ccb68c9da5cbb258d1 |
| `kernel/hardening/features/plants4/input4_hidden_rs.txt` | d91be23679275be6fb39432a2d15558bb13b613d9b81104d0d8281efc60eee0e |
| `kernel/hardening/features/plants4/input4_hidden_vt.txt` | ecbd820b21424eddbd0aa0785edc3caaa130ef1c4b0615185b7a36953f4774aa |
| `kernel/hardening/features/plants4/input4_honest.txt` | 1157ab29f7ad93ccb8776017ac02fe5406373a15eb0a06096316fc5652332851 |
| `kernel/hardening/features/plants4/input4_missing_file.txt` | 4646e26272173b1056678a12486e4ce3d5424c33cf2b83827bc9ed79d0020a0c |
| `kernel/hardening/features/plants4/input4_plants_only.txt` | 1df31a11082a85a300e5651d03aa40d188244a7410f31330f449361a2c9c0f48 |
| `kernel/hardening/features/plants4/input4_refused.txt` | 148c5d7eb0075e02f6ef36cef10964fe51b71e781ee16a629b4f4a6dbb485107 |
| `kernel/hardening/features/plants4/over4_bare_identifier.v` | 823a8e29e110a55aa18cb391367c973ff799d0daabc6518fc3ec2b8b247d3a68 |
| `kernel/hardening/features/plants4/over4_cd_identifier.v` | 45ced0eacb6fd87c7784dc66d36942a77d59b37371413f85a984e67f0d3757a9 |
| `kernel/hardening/features/plants4/over4_from_identifier.v` | 0cc710b28685419026022b43058f588a6f739b794757378eb390fe112d4de148 |
| `kernel/hardening/features/plants4/over4_include_identifier.v` | 13a966cb6452ad96896ffd2a680ebe5835109fe1c3868ed9b1210518d55ac6a4 |
| `kernel/hardening/features/plants4/over4_module_prime_identifier.v` | a3960f49c12fed6a3a6f3038e16023d9ee3da3495ec04e03b2bdd1d29f06d408 |
| `kernel/hardening/features/plants4/over4_prime_identifier.v` | 042465677ed2556e6946344d77023411c60470145ef0b752b7cc3a0f66571785 |
| `kernel/hardening/features/plants4/over4_private_identifier.v` | 50c36cacb5c0d80181401bd60a5e9a9f16e095491dd9b691cd91a82d93f854eb |
| `kernel/hardening/features/plants4/refuse4_add_loadpath.v` | bc71795c3bb640ee2f3bbc6b4a5ee899e6097676ac30fa5623be7471efbc17fc |
| `kernel/hardening/features/plants4/refuse4_add_ml_path.v` | 2d940ebdcb8ef623840c6851be97db7ce6c7cc40ba06aad59bf2c1dcf790c4c7 |
| `kernel/hardening/features/plants4/refuse4_add_rec_loadpath.v` | a51202e014f8e72638e98b90d76a5939705f9408068af25733f174ac5350feab |
| `kernel/hardening/features/plants4/refuse4_add_rec_ml_path.v` | ec1f01d32b5ec3737ab72d04b58b49bd4201418cb2958558fe238f00e2fb3d96 |
| `kernel/hardening/features/plants4/refuse4_admit_obligations.v` | 9a2d5de8d6fe38e4edfec57a95e5a3d066b9d0fa79ac85426636fac43a39354c |
| `kernel/hardening/features/plants4/refuse4_attr_bypass_check_after_local.v` | 0d53bb3d3945907da5166dc034f1dbb0255dd9f9fdd945498a8314f64d9b4768 |
| `kernel/hardening/features/plants4/refuse4_attr_bypass_check_first.v` | 3f0479d4c18af27b65f82aca2dd30fed1d791402623c409c3de46f257599f49c |
| `kernel/hardening/features/plants4/refuse4_attr_bypass_check_multiline.v` | c8bc8754402b3662f4fe086b10f270be6b76c285ee89582f195f0ebe98f07b1a |
| `kernel/hardening/features/plants4/refuse4_attr_bypass_check_second_list.v` | 6acea797b78924286cd8b8340bdf4863abfc31cae915f6a13a9783de198116c1 |
| `kernel/hardening/features/plants4/refuse4_attr_bypass_check_spaced.v` | 264a4b30e75eb15b276cce1a4216fa8f6667510c88ae0fb3149b01b2f5c428be |
| `kernel/hardening/features/plants4/refuse4_attr_private_after_local.v` | 03e7d9a1e689f531b7acb49c3bfeef7805a04ba681457e8cb46884a795f120cf |
| `kernel/hardening/features/plants4/refuse4_attr_private_first.v` | 1cea7a0b56297c07cc48025588080460c2c92c1e29e3a1d2db9df709c0a62ae9 |
| `kernel/hardening/features/plants4/refuse4_attr_private_multiline.v` | 92ecf0904f52fff274aba93ca0e08d9e0ac41e9e66c88614af0dab9055de1c01 |
| `kernel/hardening/features/plants4/refuse4_attr_private_second_list.v` | 8cf022d4bb6f946544ed5a973c078104d58a78ea52e14947891295f829ab99be |
| `kernel/hardening/features/plants4/refuse4_attr_private_spaced.v` | 5bb2e97fc0ad1f98dc475440f0467041a5b20ebc3622350e275b234ae482408b |
| `kernel/hardening/features/plants4/refuse4_attr_program_after_local.v` | aecfff33058beeaacb2b258db47e1172008f725f65c05b9753ff29d2ac47fb06 |
| `kernel/hardening/features/plants4/refuse4_attr_program_first.v` | c34804d81eb78fefbf01df27af35840d721e6b4bd34839292e5a36fb4300eff3 |
| `kernel/hardening/features/plants4/refuse4_attr_program_multiline.v` | 0b32aadf21a6d273eebfb0bc7b710d9fefb8c5c34a8a5347df065ef11e614adc |
| `kernel/hardening/features/plants4/refuse4_attr_program_second_list.v` | a45c7c185189eac595ac1577e8d01b642bf25606e08fef68688067b9f01df1a2 |
| `kernel/hardening/features/plants4/refuse4_attr_program_spaced.v` | 1ba1594c25c1e9f985d97db53ebd61173f5bf92639ac75358da47e900aac2ceb |
| `kernel/hardening/features/plants4/refuse4_attr_projections_after_local.v` | 2517a6b079601d9f3359507100d7e09407f3dab65bcfee4529c053956d50d370 |
| `kernel/hardening/features/plants4/refuse4_attr_projections_first.v` | ee7848e96d650ae561466b20ac30973ddeb0d5c5b4eedfacfdd6558559295f91 |
| `kernel/hardening/features/plants4/refuse4_attr_projections_multiline.v` | 86fae49117c15fe0822a1f123f0ac13347548c1408acda3c9fd059b460e77db4 |
| `kernel/hardening/features/plants4/refuse4_attr_projections_second_list.v` | 20e0d402ad2275e8f83c3f96d4fcc6d0d728d77d804895fc7ebe531e242e9cb5 |
| `kernel/hardening/features/plants4/refuse4_attr_projections_spaced.v` | 8780f0cb881b18411cbe9c73232170cfba31c843717106bba85b77ecdbc1e35d |
| `kernel/hardening/features/plants4/refuse4_attr_universes_after_local.v` | bb71ea06be18e25aac79e744d0cd699c65bd5b8136c8cdb6ac4ba53e4c522516 |
| `kernel/hardening/features/plants4/refuse4_attr_universes_first.v` | 8f3e6ae48275461d0607ec4f3e0657a2b96ca408846898b09681bfa9916beccf |
| `kernel/hardening/features/plants4/refuse4_attr_universes_multiline.v` | e107a97c2f969ea80ad5c95a2a3b10e12ccb0d194229c93d83f6e82846199694 |
| `kernel/hardening/features/plants4/refuse4_attr_universes_second_list.v` | 9ab09691085db16c884a30e8d47da89c86c702de5c5906fdd7d486a63fe0126f |
| `kernel/hardening/features/plants4/refuse4_attr_universes_spaced.v` | 18c576eaf087019df6a2cf9870782f202a7c6039f7efd5501700a0419727ca5c |
| `kernel/hardening/features/plants4/refuse4_attr_using_after_local.v` | c189a033e2ccc66eb395740e692e3551866b118563fef55b35b31340cf80616f |
| `kernel/hardening/features/plants4/refuse4_attr_using_first.v` | 0f7be6f8adf2b888d998d96a07a744590ef6844536d53ed7cc5fd7b392d78d9c |
| `kernel/hardening/features/plants4/refuse4_attr_using_multiline.v` | 196ac609dc0910b508e1775b8768936fae13b097cd41cb0c2c41740552a5f63c |
| `kernel/hardening/features/plants4/refuse4_attr_using_second_list.v` | 85264c4bdb3512f5c53ce660eadc96b67a0e155a2446c6e7f3f9c65724b25f64 |
| `kernel/hardening/features/plants4/refuse4_attr_using_spaced.v` | 5985b38584e4c62db1bb9165d1ea36a26905f2510f343a70c88e82f0ff4eb7b2 |
| `kernel/hardening/features/plants4/refuse4_cd.v` | 1019f8c17ad3e9b17d7c0289fdac02710894771eca56dc6c87955003a46ed0a8 |
| `kernel/hardening/features/plants4/refuse4_conjectures.v` | 0f5dc25b77c75e746a28963390d419f5f5a5481ebc0add3d71cf94c78eeb181d |
| `kernel/hardening/features/plants4/refuse4_context.v` | a278f28b49855f281dd0810352a69f81be5b1cacd5baabbd2fffd8ddaafb0d37 |
| `kernel/hardening/features/plants4/refuse4_declare_instance.v` | 07266b8477834c72b3689c556deeb2cfe6160e261482fdeba9779bc64c547f2c |
| `kernel/hardening/features/plants4/refuse4_declare_ml_module.v` | fb5bdcc63e3aca99c813b69c01e02988b6723d96a2a61b5c8a08a03ae88072e7 |
| `kernel/hardening/features/plants4/refuse4_declare_module.v` | c195830694167e019257eca7b08750cb46cde333f44e4a9e72e9ddce373d74ab |
| `kernel/hardening/features/plants4/refuse4_extra_dependency.v` | daec5fa195956e9404d6549f6d413b1f5474472999496f5b4515fb95e1eb02d5 |
| `kernel/hardening/features/plants4/refuse4_extract_constant.v` | d88c9360eeb7a332f6d82dd4f6c1063ef26f71471c925963a9545eb99e8960d9 |
| `kernel/hardening/features/plants4/refuse4_extract_inductive.v` | 476f3dccbd3dd2c4681a54ef497922188008db8d5be1d25aca3ca6612749e533 |
| `kernel/hardening/features/plants4/refuse4_extraction.v` | 7db4ac3e64b067129f50da477a8c9748921731f2c4136046066cb8504eeea440 |
| `kernel/hardening/features/plants4/refuse4_extraction_library.v` | 31daa36dd571cdfbab8fbfbb38bd617d8312756889d19aef4d2a3b51ae4f7f80 |
| `kernel/hardening/features/plants4/refuse4_extraction_option.v` | f3330939886b6dce136998fc8819f061d6b018725140469df8d1fa4c6c7141eb |
| `kernel/hardening/features/plants4/refuse4_final_obligation.v` | 2f9baa018b4567ed9ae732c60d61ecd8cb078e055d9b8979bbb52569806dfca3 |
| `kernel/hardening/features/plants4/refuse4_from_import.v` | a89bc809240d8853b97714c0e0beecf7b150c9278742d6a7bcc525d26722e25a |
| `kernel/hardening/features/plants4/refuse4_load_absolute.v` | 5ad0ee426d291e2828bdd08bd7d66664b10e29e87ba4ebbd8e3b420c2467157f |
| `kernel/hardening/features/plants4/refuse4_load_ident.v` | 39feb9747b9e0905efddd3e44a00c14debb4196540f0aaa632b814127945ebe5 |
| `kernel/hardening/features/plants4/refuse4_module_alpha_applied.v` | bec90ef090b25ad722d9feb6a7542a7922618dba38afa1878f77b9871ca6abbf |
| `kernel/hardening/features/plants4/refuse4_module_alpha_functor.v` | 529532219a190f2de1192adc00f578fd461015d76489106c27f559b46ede1d60 |
| `kernel/hardening/features/plants4/refuse4_module_alpha_plain.v` | 82f8eb9d186ac0159d83852455afa2b13bd3b0ca3a6f1c26e74505c0723e58b3 |
| `kernel/hardening/features/plants4/refuse4_module_ascribed.v` | bc43a848de0c5346d470dca32faee1d266442d3714f3732910bff6dc5416c5f1 |
| `kernel/hardening/features/plants4/refuse4_module_ascribed_sub.v` | 3765cae78b992525c0118b1954a4adff1db5024ddb0aea76caf3759faa62a53c |
| `kernel/hardening/features/plants4/refuse4_module_beta_ascribed.v` | 2882743d3dc4fe1861302f32ee17e19b43b47a19af5ffa2954dc65b6ff925046 |
| `kernel/hardening/features/plants4/refuse4_module_combining_mark.v` | cb39213d7a6f9267c63b184fb7e8dd81befdf1ef0450c6ae91984dde0cfa59f3 |
| `kernel/hardening/features/plants4/refuse4_module_e_acute_sub.v` | fee936311c7274fc5abc79feb0997c74e863416a26b9031f77064fddf85466dc |
| `kernel/hardening/features/plants4/refuse4_module_export_applied.v` | c84e49f36ff384535109910a0634cffda8b8a807a18e813ba460477640fe6e24 |
| `kernel/hardening/features/plants4/refuse4_module_functor_applied.v` | 557db8c9ce6fe56c72864d3176bc76d9a7f11914fbb7e63f61b8e760aa594032 |
| `kernel/hardening/features/plants4/refuse4_module_import_categories.v` | b520245bfbefb9ff4ab23e749f136c3b820c601dcc7934df9c066dc36aca000b |
| `kernel/hardening/features/plants4/refuse4_module_import_functor.v` | bd431d44c9ba0515d0a06957a884b41ae4875a703b75fb707ea775811d6abcec |
| `kernel/hardening/features/plants4/refuse4_module_import_gamma.v` | dce99b38de55749aab4aad24292f1bc6a89fb43df9fd98166d9d9eecf6e453f0 |
| `kernel/hardening/features/plants4/refuse4_module_include.v` | 5a89fe896906e5e6341dfd5d281671fa3e9a9b4d50c106bbf21a06bd8ccb223a |
| `kernel/hardening/features/plants4/refuse4_module_interactive_sub.v` | d6a95c9f36398a92c48f0c29f885ecb9532f45265454396c732c626ce6c96bea |
| `kernel/hardening/features/plants4/refuse4_module_multiline.v` | a3ce334661019d0dfde7c47fae141ede9f2f02aa94defa781bbcc577b1f3996e |
| `kernel/hardening/features/plants4/refuse4_module_type.v` | 91e630e3e5e23f406b705e481c3b068a4630fe74c342549fa9ff808bdf232c3b |
| `kernel/hardening/features/plants4/refuse4_next_obligation.v` | 7ba911b28f3ca4120fbfd48849942f101590557f2c920f7accb992edc5033580 |
| `kernel/hardening/features/plants4/refuse4_nonascii_comment.v` | 67e0e06a1baece6c6d52e1526583e9529635f6b4395c23533afe1678376c314f |
| `kernel/hardening/features/plants4/refuse4_nonascii_string.v` | a24ac50e9928530105764be1002c1db8af0b3791b1838ef4df063fbad51068e0 |
| `kernel/hardening/features/plants4/refuse4_obligation.v` | cd91fd0ef3dc91be03c60b70b913e14d2e7c1b8c5c2fe70a292b8132064e94bf |
| `kernel/hardening/features/plants4/refuse4_obligation_tactic.v` | 7924af99bc0ca35de1cbad0d94b7df859f5ca419ef58557cbc32f84ca4583f50 |
| `kernel/hardening/features/plants4/refuse4_option_default_proof_using.v` | 8dec7f0c2f671af8c26a7c1057f9fd973eb1da9e7e786b8710661ef4312e90b3 |
| `kernel/hardening/features/plants4/refuse4_prefix_attribute_private.v` | 305e3caca8ccfef12cdfaa5fc9d8f917bdd491437fdb2e230deb1ff67b1493a2 |
| `kernel/hardening/features/plants4/refuse4_prefix_cumulative.v` | 21b08e8cd58cd1ad9af1ca6219ca32eeec764c5f03901d9e443fadf4a133e0ae |
| `kernel/hardening/features/plants4/refuse4_prefix_local_polymorphic.v` | 621df610c059a888d22cf5d1c9c9621c5319b84f141888d66633f719538b4549 |
| `kernel/hardening/features/plants4/refuse4_prefix_monomorphic.v` | 0ae89aa8cfef680b2bffec03d14b9775de4e8ac99277a28aca352548f9653a7a |
| `kernel/hardening/features/plants4/refuse4_prefix_noncumulative.v` | 459f8668a5dcc3002e0303c3e6d811d4c05d8bb797d777cbcdbb976df76ca101 |
| `kernel/hardening/features/plants4/refuse4_prefix_polymorphic.v` | 37b8dcc88c920d3dfa096f984fe1ed89712ed7bd9a7707bc2c040bad53a3e16c |
| `kernel/hardening/features/plants4/refuse4_prefix_private.v` | 1e1bff1bab38093b690814257bfbf1266afbfffd2f64b0379781f517419f82d0 |
| `kernel/hardening/features/plants4/refuse4_prefix_program.v` | 49ff4b78c2d2aeca0b7ae02a76b65f3a99e533869af0789ffa62284ad18e3423 |
| `kernel/hardening/features/plants4/refuse4_program_attribute.v` | c34804d81eb78fefbf01df27af35840d721e6b4bd34839292e5a36fb4300eff3 |
| `kernel/hardening/features/plants4/refuse4_program_attribute_list.v` | 6b89a19562b8ea8d2e413c8c0749a62f0aa72233d4faf71fff10d08d02c27457 |
| `kernel/hardening/features/plants4/refuse4_program_attribute_value.v` | 9309fed7d14444607bf99522bc0762e5f5d3049a9b1b547476b26441fb951929 |
| `kernel/hardening/features/plants4/refuse4_recursive_extraction.v` | a6210e431ae1ef4d4060576b82eca255d967108e7ae996484f039d19de3e738c |
| `kernel/hardening/features/plants4/refuse4_redirect.v` | 5efb143675a43d0420d90d0fa787b6ea77c48a3552327dce64ab602bc75d5841 |
| `kernel/hardening/features/plants4/refuse4_restore_state.v` | c387127f06c67c92be35771c645e7e010474a73cf3a0a9a0875453848e0b6503 |
| `kernel/hardening/features/plants4/refuse4_separate_extraction.v` | aef21591f29bfe3cad843ed7e478013829c69dabfc155a1506d8bec653541f3e |
| `kernel/hardening/features/plants4/refuse4_solve_all_obligations.v` | 0bba9e1c1c4827b93a68d6861522a9fa7017fb83d42d9e602a7d76d5ba46fa49 |
| `kernel/hardening/features/plants4/refuse4_solve_obligations.v` | 42b09c530b5888406da825614628d46ad684f9f3cf53187f4e0b6128f8766d31 |
| `kernel/hardening/features/plants4/refuse4_universe_binder.v` | 3d4a694659df4e16a22a834751f3a1189e5d17a7913fb2ffb95e577cd8ce55d0 |
| `kernel/hardening/features/plants4/refuse4_value_bypass_check_positivity.v` | 0471a440f2fadc0b661e6495e7a3ddc3d8b7e2e366cffe107f9675a1e9d791f7 |
| `kernel/hardening/features/plants4/refuse4_value_bypass_check_universes.v` | d6c84d4858f4001506c889cbbb4b5e75a28d41fa5bb0e418ed06b5b69f5e642c |
| `kernel/hardening/features/plants4/refuse4_value_program_no.v` | 2754f1484df2bf6c562dbb4be37a511c14b3301c71037580b0407575833406b1 |
| `kernel/hardening/features/plants4/refuse4_value_projections_primitive_yes.v` | 9848c246132817bb0e37d5c412bc9621193eaca7e38360e74fa76a015c0d121e |
| `kernel/hardening/features/plants4/refuse4_value_universes_cumulative.v` | 8ef55ebee6e751abc135c943ca7f52443a3f2e3a7dbca12634d744ba1531d2c0 |
| `kernel/hardening/features/plants4/refuse4_value_universes_monomorphic.v` | 3b1bbe841776ebdcbdda5c742ed44ed4bb2d411245a9efac6ba2ce62fe1030d5 |
| `kernel/hardening/features/plants4/refuse4_value_universes_polymorphic_yes.v` | ec86c9cc1dcf0f45c6a73e8ee1bd6a394e91a5d75a89ff33e887cff497b0ece3 |
| `kernel/hardening/features/plants4/refuse4_value_universes_template.v` | bd54496a4aaac68c09d40ec19538d1e7c1e75c965bc87f67c5f3e12ae69f1065 |
| `kernel/hardening/features/plants4/refuse4_write_state.v` | 1c511cfda7c18bc35907c4c994fabfe03db7eaa3ec7d4bc3417a1c1054e205f7 |
| `kernel/notes/FCLINK-TRUSTED-2026-11-22.md` | a80312dd00d418af56e7d5004517592d0ee9c9da1f6efc88b22ae852c67bfa30 |
| `kernel/records/INDEX.md` | da3c31c09879b00b19914f351e828854fefd39df8befb4afe0ac8a36e28ec656 |
| `kernel/records/bits32/BITS32-SWEEP-FROZEN.txt` | 11b2713b4a0ce6b7d7e0e48aa4c3f1b07ee4b32fd22525024396a5e05abca897 |
| `kernel/records/bits32/PREDICTIONS-bits32-sweep-run1.txt` | 7b443e3cd800a47469bd4430cacb6b9edf437eafa756cfec8cf89ae09274e006 |
| `kernel/records/bits32/TRANSCRIPTION.md` | c21f9c8ae50aa9035f7ba59a598b4292427dedcc3aab747d921695e832b0c34f |
| `kernel/records/bits32/bits32-sweep-run1-console.txt` | eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1 |
| `kernel/records/bits32/bits32_sweep.c` | da83a668b935948cec672ec5480bc6770a844abeef9a5f3f5d577716d7b4ced0 |
| `kernel/records/bits32/k1-run1-console.txt` | e06bfcead5239f964eb307fb85f8c6d031ec599198fe39aced03dee040e50b36 |
| `kernel/records/bits32/k2-run1-console.txt` | 29d389f70195eff8de9a2d6876829dc6ea9639eff163294d71712ea87cb00a6e |
| `kernel/records/bits32/run_bits32_sweep.sh` | c7df2aa87bf9e0973886f30431396008214a575a8620a61c0ede8cfcab536311 |
| `kernel/records/fclink/local-fclink-run1.txt` | 39a997d8a41b46799d14de820a5072e2307a3792ce534d21a222f7d32f8968fc |
| `kernel/records/fclink/sweep-real-r1.txt` | 804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a |
| `kernel/records/floor32/SWEEP-FROZEN.txt` | 177be428d03ebcd24b500f225fce9b1b74072e4757cd1d5f272ec0d5b5375824 |
| `kernel/records/floor32/local-p1-run1.txt` | 55a078802f5024ae568ec1ca593528ee4a2cc9734e02d477c0bced4852d648c7 |
| `kernel/records/floor32/local-p1-run2.txt` | 7fb3982ca930f78768dcf96d37b2f8d036e7af9ed50d36826a7abb234bfa1f9d |
| `kernel/records/floor32/p1-sweep-run1-console.txt` | a7eb1695ce042700ade2d0395c5e8d98085fb265c5d7ea08ebc321bba5a33a9a |
| `kernel/records/floor32/p1-sweep-run2-console.txt` | cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025 |
| `kernel/records/floor32/sweep_fc.c` | c0b4b71092f841621eefd9ae65677afb5ec198785772bce2a22de67efaafdc92 |
| `tools/ci/SWEEP-SOURCE.txt` | caa62543f1507beea70ca8704c236a9fe7ff3bd8a9fff809f5a606134155b1e2 |
| `tools/ci/check_boundaries.py` | a3226def623b1821f464c7d4eebb2a7de4e7cf49d39f34056b8ec1d87da5775b |
| `tools/ci/check_gate_log.py` | abafe1b7dc1c71b259e4ebd5c973a3b989c6c7e68052f17699bc052c0a9c6ec2 |
| `tools/ci/check_sweep.py` | e64848863c6e00ab77ba020e4f67e63a1d6ed51d4fdf4a3af7e7eb82c5a2ce0a |
| `tools/ci/check_toolchain.py` | 741ff2471a9823ccf45729ac01a6e7b130f2b6f05bd36c8c05d0f69994ee517d |
| `tools/ci/drift.py` | c6d213002836f497d68a6880a6eb9ba3e55845f273f7cdd549eaf99f90c3c016 |
| `tools/ci/inventory.py` | 9f7bff61a71bc9cd0a5bf196a69822ca5bb27653a1c9f559b975aaf7a0e9d69e |
| `tools/ci/judge_digest.py` | b316cd9b1ae12e54abfe4fd8c496b591a2f0defc4d7d5e80593d12068e186058 |
| `tools/ci/read_audit.py` | 219a41cef2642b63ff8d000aca3b27d29f102ebe578a66033bfc62dc070a556a |
| `tools/ci/run_record.py` | 60b6d7d724bd4c40b7fdc842b69828f9e26a111df8ef3a9339ef01ddb923d908 |
| `tools/ci/tests/PREDICTIONS-check_boundaries-2.txt` | add3ffe86d0a9313d78dad6a267460b94060004452c2cd83851b716ff4dee08e |
| `tools/ci/tests/PREDICTIONS-check_boundaries-3.txt` | 876e96adc9e2903269f68a4eecf654452ce83d670b4ca79136616d905ba4cca4 |
| `tools/ci/tests/PREDICTIONS-check_boundaries.txt` | 3b5aafd5f7ed0f59e29c1d20478dd59c771bbdaa2ea0224d9e429b1ab7b1e8b9 |
| `tools/ci/tests/PREDICTIONS-check_gate_log-2.txt` | 8d1b4ecab6a237e0724f7403544d0a2111496ef158aabdd2cc1646850da237b7 |
| `tools/ci/tests/PREDICTIONS-check_gate_log-addendum1.txt` | 32d6bbc848bbc1a4f6065b46d1ae7129e57d5610689ef2bdfa740c02ad6ac315 |
| `tools/ci/tests/PREDICTIONS-check_gate_log-repo-2.txt` | efdd386d6657c509b5f7aa80f426a7c0a2d4773e7c54f8598614299a46ce8bea |
| `tools/ci/tests/PREDICTIONS-check_gate_log-repo.txt` | 77d04e5f93e6be3c1c2a4ddc3c77ede40eb5a66d11124896c0537d4e1d012ab5 |
| `tools/ci/tests/PREDICTIONS-check_gate_log.txt` | f0ba9e84196dc388e33a574ca497cd221177825880a81f006d7c7a5d48b47c4c |
| `tools/ci/tests/PREDICTIONS-check_sweep.txt` | 1854028bf15f29233df67048fce054f6f653217c06194feabf3ae4554fb89564 |
| `tools/ci/tests/PREDICTIONS-check_toolchain-2.txt` | 466e55834cd984d61e5f5865e6d3ee6e070ca95aa72a7daa266a424e27e52322 |
| `tools/ci/tests/PREDICTIONS-check_toolchain-3.txt` | c172498cda19b1df1721111fab1d1bceb20b723621106e2ed348e73ce7c6bd12 |
| `tools/ci/tests/PREDICTIONS-check_toolchain-4.txt` | b8961758268ba258c0ab783b118048650e55198f56efcd03d3a5af25f763b77d |
| `tools/ci/tests/PREDICTIONS-check_toolchain.txt` | 4e53c76ba2962463dc80ca3ea04b978b629c00f292aa0d5c8554972c373b6e39 |
| `tools/ci/tests/PREDICTIONS-drift.txt` | 3f932db60eb171935df03dabaa88439109618d54483b3525d9dcaa8a3d103fd1 |
| `tools/ci/tests/PREDICTIONS-inventory-10.txt` | 14b1ef1a068b7b52fb00cb27a3204179edfd8c8cdf8f435ce7ab5f0b68e43e43 |
| `tools/ci/tests/PREDICTIONS-inventory-11.txt` | 7684b15c721fadecd9d0276807b3cdab5faba18a919ff433f7e684187237cd56 |
| `tools/ci/tests/PREDICTIONS-inventory-12.txt` | 6940568826a8dff80d369c3cdecff2a36dddd9c50921c10a039e204062bdf1b0 |
| `tools/ci/tests/PREDICTIONS-inventory-13.txt` | fdc942add3052d99d77a79faaaaf743c07c45342d269e6e054cfc2272350e70a |
| `tools/ci/tests/PREDICTIONS-inventory-14.txt` | 24f539ef13f119bec36b931098dfc746ba62ed0e678e7da1ba47a636b8e3eb73 |
| `tools/ci/tests/PREDICTIONS-inventory-15.txt` | 7e861b106deaef49d68fc6101c878d2a06fbbac76538497eb5178a5c4c3973a2 |
| `tools/ci/tests/PREDICTIONS-inventory-2.txt` | 41bbdf8c465523e4e72984cd7f36b2405bf797771cbde4bce3f7c16c66530719 |
| `tools/ci/tests/PREDICTIONS-inventory-3.txt` | 5ba08455517cb2cb8c4d1b2876e6e2b37383487b89630669e9021ed514a2d3ad |
| `tools/ci/tests/PREDICTIONS-inventory-4.txt` | 7084e2553b277957f6fed8bc6d13eab536eb37b378c99740bfe020ee8dadc403 |
| `tools/ci/tests/PREDICTIONS-inventory-5.txt` | 2f8503e4b6d0223c23c64209b48148f228f2db6baa76521caa9d47f39e6ae896 |
| `tools/ci/tests/PREDICTIONS-inventory-6.txt` | 4c00db6dd233f9ea0a9672b08a148a353a0a4ff9ee9816fff506fcd7d0c6f4fa |
| `tools/ci/tests/PREDICTIONS-inventory-7.txt` | 3b3309acdcf12596b09cce021e2e35ed3b0375d98a7b48cb2c49c6cdf61f6c5f |
| `tools/ci/tests/PREDICTIONS-inventory-8.txt` | 83389d22ce144beeb52775b3e87ab2a74c8ca0adf9bb58567c8a038d7c98242c |
| `tools/ci/tests/PREDICTIONS-inventory-9.txt` | 70caef464219b700434bad1d9cd9ecf465d825245426077e924f51b633f33102 |
| `tools/ci/tests/PREDICTIONS-inventory.txt` | 3b38cd687d1557082e302906a7377dd46dee64e07110aba86bdfef13eb8cbcd2 |
| `tools/ci/tests/PREDICTIONS-judge_digest-2.txt` | cbefb4a919155ed7b323beec2358ab9de88a40b9c251910de8b4724ce1467868 |
| `tools/ci/tests/PREDICTIONS-judge_digest-3.txt` | a7321a64c8052e71d99cec46e48d92d35a52a0aa78098f342f8c5f5910c3faf2 |
| `tools/ci/tests/PREDICTIONS-judge_digest-4.txt` | 5f58de98f80c1b875e8ca48426dfee91a247012d49d6b0027e97514493328785 |
| `tools/ci/tests/PREDICTIONS-judge_digest-5.txt` | e3a5f48445c636178d2b6c454a6543ecba8c1054aabae0983922bd32d190b63a |
| `tools/ci/tests/PREDICTIONS-judge_digest-6.txt` | 2a06305ed5da4bc780c1034c5db3654db3cdd049d1df740b16eea4bebd57e364 |
| `tools/ci/tests/PREDICTIONS-judge_digest-7.txt` | 655ef84ef5a2d05e4cfba99b71120fb2e37a5b98873b7d1dc89a3ba04857615c |
| `tools/ci/tests/PREDICTIONS-judge_digest-8.txt` | a6929950dc5908aa9f98a158c4f69e4cc187b124c5242a890fdc461a824cf96c |
| `tools/ci/tests/PREDICTIONS-judge_digest.txt` | a108de2f7f9a997190fe0844718e0069da2b3a3eedc6cff509f69a498543b2a0 |
| `tools/ci/tests/PREDICTIONS-read_audit-2.txt` | 332c137202f21b40db188ed462d8a6123034671ade3d45d56fdef83d65c5c1f2 |
| `tools/ci/tests/PREDICTIONS-read_audit-3.txt` | aea2c542f50e3215cfd6dd30c250cf5c89ed064ef0feeec45aef981e4ed312b5 |
| `tools/ci/tests/PREDICTIONS-read_audit-4.txt` | d8ed57952311ef4cfd5d0c552ad3c73c93879161e36e518fcd74567f4a534fb5 |
| `tools/ci/tests/PREDICTIONS-read_audit-5.txt` | 77d630dfd522b3058fcf67204a925ca2512630f7ccdba6a0e671b3cc29798df2 |
| `tools/ci/tests/PREDICTIONS-read_audit-6.txt` | a9c4c597e9d58094dd88c1ca30fda1e28f0b8e4554be27e3dc3a579d5506955b |
| `tools/ci/tests/PREDICTIONS-read_audit-7.txt` | cb42e0a0b5cf36d9635b55c7567ed701317144f4f352ef611c0d17bc62dfa684 |
| `tools/ci/tests/PREDICTIONS-read_audit-8.txt` | 7aad16f7bf26e97bd043d022d761f9d4aabbc3aa02bd46446fe1f3d48164dc71 |
| `tools/ci/tests/PREDICTIONS-read_audit.txt` | 14df2a827dbf730e011eca1612cfb8eea0aac842e74a1aa747780a23d3d2d86e |
| `tools/ci/tests/PREDICTIONS-records-addendum1.txt` | 424a20dcfdd2b4bc1c0e81e3a914a9f72d442020c751a6c6edbe0a54c0457966 |
| `tools/ci/tests/PREDICTIONS-records-addendum2.txt` | fe2e1637f07cc4f386b38cefe202f9d2e88fedb73cdc525154a85dc0ebbf557e |
| `tools/ci/tests/PREDICTIONS-records-addendum3.txt` | 81a90e6a8225bd0d0d778d0e68dbbcc070c847e673e5db38ee69be2487699abc |
| `tools/ci/tests/PREDICTIONS-records-addendum4.txt` | e56bbf2448032f494dcd7613b598cd3566cd697c7610e5afd9d556d340462bec |
| `tools/ci/tests/PREDICTIONS-records-addendum5.txt` | e7aa2900f366979a182665bde15a600faf9ae6dabcbe2560e99721a9583cf8fa |
| `tools/ci/tests/PREDICTIONS-records-addendum6.txt` | 09b3460607ef28f521b22cdee81667b77e2f822c415b7592e12b088be696f9f5 |
| `tools/ci/tests/PREDICTIONS-records-addendum7.txt` | 694e9732926f83b0c788416b6c7441c888bc3850d5cf5709a3fd1bf1fd37f95b |
| `tools/ci/tests/PREDICTIONS-records-addendum8.txt` | 5c44590ab8672fc9a4f67d587cad5f4f49ac047a14dadb90a1d619298c93962d |
| `tools/ci/tests/PREDICTIONS-records-addendum9.txt` | c84a3ef60cb06c27d50371df3a18b11ef49274ca96f58a0cae4ea2fffc09cfbf |
| `tools/ci/tests/PREDICTIONS-records.txt` | 8fe5a4f6720b0e3219a42d43a8cd0fe28a97d55eb8c561cf06f6502ad06b40bd |
| `tools/ci/tests/PREDICTIONS-row4-addendum1.md` | 1f4dea11d057ac1bee4c4eda10b7466e6c13357f6e97e8cdb4df65cd82d5e088 |
| `tools/ci/tests/PREDICTIONS-row4-addendum2.md` | a1eb49c26cd4151fe2a2c019f569e5f6620fdb4d3bb133d215a8b2b83c64d06c |
| `tools/ci/tests/PREDICTIONS-row4-addendum3.md` | 50913aae627bdcf8532506504f3fc0e503ad3991005e4a730bd2f86d7676d1a6 |
| `tools/ci/tests/PREDICTIONS-row4-addendum4.md` | 266c980e3f7124bf87306aee055b0fad1c1f30ab4f110a4a05d45e612f76f1b6 |
| `tools/ci/tests/PREDICTIONS-safepath-2.txt` | 4c4d3278e633d3c9bedcaa45d68cde6748b0f9ebbdd70522a2103c145a810da4 |
| `tools/ci/tests/PREDICTIONS-safepath-3.txt` | ff2941165fc1a11e605594307b535356e89a3a980614f67c868883418e45a08d |
| `tools/ci/tests/PREDICTIONS-safepath.txt` | 99feab18c1035cc1ebace840b802d19eb6f761e27a79752c72246d0eac7f5303 |
| `tools/ci/tests/PREDICTIONS-usage.txt` | decc94f9bc6b9ee453a9ef142b94eb7442a7f7081214030ae28fb5a2f96dc005 |
| `tools/ci/tests/PREDICTIONS-workflow_guards-2.txt` | 9733f23296c3bcb46e2e4906963f017b1b1709013fdd92fed09147f0fd53535f |
| `tools/ci/tests/PREDICTIONS-workflow_guards-3.txt` | bbb0cdab41075d8b45e67e5e735f464be5c2c1a3d854dcedc561a0b8f33358fb |
| `tools/ci/tests/PREDICTIONS-workflow_guards-4.txt` | 492af4f8ed7c134d05d03841a40418cd8e409fb8047f81a21e85afae78a83fef |
| `tools/ci/tests/PREDICTIONS-workflow_guards-5.txt` | b72cc60bc2837cefa20421538979034d13fc5165c16472e819fd7aaa4e130311 |
| `tools/ci/tests/PREDICTIONS-workflow_guards-6.txt` | 4f77b81451ef88659fa5938494df8eeb8513ec3c09e6c731c4dc6e3b26153080 |
| `tools/ci/tests/PREDICTIONS-workflow_guards-7.txt` | d1ca395303eac42acabf918f2f367692689adeb02031de00143dee819ec4f7c9 |
| `tools/ci/tests/PREDICTIONS-workflow_guards-8.txt` | c36391764c4c9112a65b0c23b28d5ba81857f6c3ed7927881707b7e3ff6f78f6 |
| `tools/ci/tests/PREDICTIONS-workflow_guards.txt` | 1907278fa1417fa1d9056030dca56a66e1720ca66ac1c1ff792561ca559d59a1 |
| `tools/ci/tests/PREDICTIONS-workflow_pins-2.txt` | 66cd3a81ef4d6111186ac08b95baf3f2e7dbaa044ee235ba077892083fe1a0c9 |
| `tools/ci/tests/PREDICTIONS-workflow_pins-3.txt` | c805451319aa165128a6b178461a0c7db2119b430c907b33d7ec281a58b57df7 |
| `tools/ci/tests/PREDICTIONS-workflow_pins-4.txt` | 714286ce629642563ab0170cbeaceb7ea6cdd51f1a82e570b2ac0d4c9e132a5e |
| `tools/ci/tests/PREDICTIONS-workflow_pins-5.txt` | d17650d9c458552073d2cc35df8d297a016f5ea84f3dd351c1372a8e79c7b8e6 |
| `tools/ci/tests/PREDICTIONS-workflow_pins-6.txt` | 0fa4858b1faa49dec59e1f6f1ef1332870d96a7633829d54d722c25b976aa67a |
| `tools/ci/tests/PREDICTIONS-workflow_pins.txt` | c2847554ffe7a3b3fc72e8c1f38910749d1fee88b0fe5f20c94ed21eb1e35964 |
| `tools/ci/tests/run_all.py` | 793d074760bfd09c90b9582a81cd06326ba3c01f59c52aea08ad64451eb8e6fa |
| `tools/ci/tests/test_check_boundaries.py` | 4f9182337899d224d782f1d1c7b455f50de3c8b59ec77d8d2a8b9aa7f2d0e291 |
| `tools/ci/tests/test_check_gate_log.py` | bbd6ec2999d6830efbf6ccf078a74d6141d36014258b09ae81cfdc33ad64034d |
| `tools/ci/tests/test_check_sweep.py` | 9bda918fbb2c8bae5b20e092747eddf66f9047d9244a296214e53e9d35fe68f6 |
| `tools/ci/tests/test_check_toolchain.py` | 2647841eea5a2e5e74322a4c046319e965a0b89f11104c3998748ce67502f9bc |
| `tools/ci/tests/test_drift.py` | 71ea73a7a4286713f1af3d3988bfc5cf4cba546d4599b364d69cc342a2007f3a |
| `tools/ci/tests/test_feature_row4.py` | fb64dc94562bafc44d3db57028d6550a92fca97a9fb68a315229dfc86207b45f |
| `tools/ci/tests/test_inventory.py` | 4dea3076ed02ec46d3a9c6b9a4736593e9065e0d0b506ffd19342c4f117bf3b4 |
| `tools/ci/tests/test_judge_digest.py` | 4a63054b8a1edf38e1a94b80043c15e3a428ef2606eb083bd3947803249f21a7 |
| `tools/ci/tests/test_read_audit.py` | 05a025a51f9ce00ea66689257b03096727987e4b82dadebc5c33f3e2653bac4f |
| `tools/ci/tests/test_records.py` | ff65805d029086bac880f3855df6d186737ced73e4ccc577e6bad8fb67136af1 |
| `tools/ci/tests/test_safepath.py` | c063819bfd6bce6575432038ce57217bbee425e4612477930e9a13fbfb09ab7e |
| `tools/ci/tests/test_usage.py` | a3879a65952a97f038c51af40a4f77f337b3b9374ee2cc176ca7c4e86c852d23 |
| `tools/ci/tests/test_workflow_guards.py` | 45b0c92b7a9061e03d9f2b9e2e587d1ffea83023b2674e155315cf4e09cffe91 |
| `tools/ci/tests/test_workflow_pins.py` | a78d184de7880e9c6dba80fd319849d4b336b85a38d0a8169b453708dfc33ea9 |
| `tools/ci/toolchain_probe.sh` | edf77862b1927534b705d3ce31333ff0bd28c90db4493f60d93e72b0475a0f27 |
| `tools/ci/verify_records.py` | a21e450e1da56194c268aa3431901cfe64829578075f6ff77ab0d63aef4ee279 |
| `verdandi/mathkernel/F32/LIMITATIONS.md` | 6d57f39beeab7436e220f867bd043fa356f8fe1a9d42b5aad66573b0bb313567 |
