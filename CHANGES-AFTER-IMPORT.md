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
