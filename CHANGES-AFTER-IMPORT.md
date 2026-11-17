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
