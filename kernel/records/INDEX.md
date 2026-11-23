<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Records of the gated folders added in Push A

The gate and sweep records of the eight gated folders that Push A adds (`sincos32n`, `exp32a`, `floor32`, `ceil32`,
`rti32`, `order32`, `bits32` and `fclink`), kept under the owner's ruling S280-12 (a) of 2026-11-22 (adopted by his
representation). Every record is listed below by name and sha256, red runs included and named as red. A record that
holds no detail of the authors' host is in this tree, byte for byte as it ran, under `kernel/records/<folder>/`. A
record that holds one is not in this tree and is cited here by its sha256 only: every gate console and every monitor
of the guard holds the host's memory figures (and most of them a local path), so no gate console is in this tree.
Written by the assistant on 2026-11-22 with Push A's batch.

How to read an entry: the file (a path of this tree, or the record's name and "not in this tree"), its sha256, what
it shows and what it does not show. Every run below ran once, on the authors' one x86-64 Windows host, by the authors
and their agents (all of one model family): the gates in a container, the sweeps natively. Every gate console below
names the pinned image (sha256:e5d68b0139b5...) but the six of `sincos32n` and `exp32a` made on 2026-11-18, which
name no image. A gate verdict shows what `THEOREMS.md` says a gate shows, about the Coq model its statement names; it
shows nothing about a compiler, a processor or another host. A sweep shows the outputs of the programs it built on
that host, with that compiler and those flags.

To check a file of this tree against its entry, compute its sha256. A record cited by sha256 alone cannot be checked
from this tree. Not listed: the proof development compiles, the plant refutation runs and the drafting sweeps kept in
the authors' workspace, which are not records of any claim this tree makes.

## floor32 and ceil32: the first exhaustive sweep (`kernel/records/floor32/`)

One program sweeps both functions, so `ceil32` has no sweep folder of its own.

- `kernel/records/floor32/sweep_fc.c` (in this tree)
  sha256 c0b4b71092f841621eefd9ae65677afb5ec198785772bce2a22de67efaafdc92
  Shows: the program of the first exhaustive sweep (2026-11-18): the shapes of `FLOOR32_Statement.v` and
  `CEIL32_Statement.v` transcribed by hand into C doubles, run on all 2^32 binary32 patterns, each result stored to
  binary32 and compared bit for bit with the C library's floorf and ceilf and with an integer reference, a NaN result
  as NaN-ness only; PLANT=1 removes the zero step. The sweep job's candidate `p1` in `tools/ci/SWEEP-SOURCE.txt`
  names this path and this sha256.
  Does not show: that this C is the Coq shape (a transcription by hand, ARGUED); anything about NaN payloads.
- `kernel/records/floor32/SWEEP-FROZEN.txt` (in this tree)
  sha256 177be428d03ebcd24b500f225fce9b1b74072e4757cd1d5f272ec0d5b5375824
  Shows: the sweep's freeze list, written before its first run: the sha256 of `sweep_fc.c` and of its runner, which
  each run checked first (its two "OK" lines).
  Does not show: who wrote it when, beyond the runner's own check at each run.
- `run_sweep.sh` (not in this tree: it holds a local path)
  sha256 df821f0bca65741ac9d9120a3b74b7bdd0890433290aa5bd9fd9da096b10cacb
  Shows: the runner of both runs: the freeze-list check, the builds with clang -O2 -ffp-contract=off (the program and
  its plant), the compiler's version and both binaries' sha256 in the console, then both programs.
  Does not show: anything a reader of this tree can check.
- `kernel/records/floor32/p1-sweep-run1-console.txt` (in this tree)
  sha256 a7eb1695ce042700ade2d0395c5e8d98085fb265c5d7ea08ebc321bba5a33a9a
  Shows: run1, 2026-11-18, clang 22.1.8: both files as frozen; floor32 and ceil32 each differ from the C library's
  floorf and ceilf on 0 of 4,294,967,296 inputs and from the integer reference on 0, NaN-ness disagreeing on 0, with
  1 and 1,065,353,216 results -0; the plant differs on exactly 1 and 1,065,353,216 inputs, as built into the program.
  SWEEPS HELD (MEASURED, one run on one host).
  Does not show: another compiler, flag, C library or processor; -O0; NaN payloads; exception flags.
- `kernel/records/floor32/p1-sweep-run2-console.txt` (in this tree)
  sha256 cbf77adde05a3a791ec11a3ccbe0f874feef662f642ec997faa7d80a20eea025
  Shows: run2, 2026-11-21, the same program, compiler and counts as run1, rebuilt: SWEEPS HELD (MEASURED, one run).
  Does not show: what run1 does not show; a second host.
- `kernel/records/floor32/local-p1-run1.txt` (in this tree)
  sha256 55a078802f5024ae568ec1ca593528ee4a2cc9734e02d477c0bced4852d648c7
  Shows: `tools/ci/check_sweep.py` on candidate `p1`, on a scratch root that held this program at this path,
  2026-11-22, clang 22.1.8 and llvm-objdump: "SWEEP CHECK HELD: 18 of 18 rows (p1; x86-64; clang)": built at -O0
  and -O2 with -std=c99 -ffp-contract=off, no x87 or FMA instruction listed in the sweep's objects, each sweep and
  each plant at its declared counts (MEASURED, one run on one host). Its input was `tools/ci/SWEEP-SOURCE.txt` as it
  then stood, whose p1 lines held no freeze-list line, so this record has no freeze list row; that line was added
  later that day.
  Does not show: GCC, Linux, arm64 or GitHub's runners (NOT_MEASURED); the C library's floorf and ceilf, which are
  linked, not scanned.
- `kernel/records/floor32/local-p1-run2.txt` (in this tree)
  sha256 7fb3982ca930f78768dcf96d37b2f8d036e7af9ed50d36826a7abb234bfa1f9d
  Shows: the same check on candidate `p1`, its input a copy of `tools/ci/SWEEP-SOURCE.txt` as shipped but for its
  use line, `use p1` for `use fclink` (so the p1 lines as shipped, freeze-list line included), on a scratch root whose
  other files it reads are copies equal by sha256 to this tree's, 2026-11-22, clang 22.1.8 and llvm-objdump:
  "SWEEP CHECK HELD: 19 of 19 rows (p1; x86-64; clang)", its freeze list row finding that
  `kernel/records/floor32/SWEEP-FROZEN.txt` records the program's sha256 (MEASURED, one run on one host).
  Does not show: what local-p1-run1 does not show; that its input was that copy (the authors' run script made it).

## floor32: gate runs (not in this tree: each holds the host's memory figures and a local path)

Each run's monitor, the guard's record of the host's memory during the run, is listed after it.

- `p1-floor32-gate4-r1-console.txt` (not in this tree), RED
  sha256 a24c672f6658fc00ed55ef5575a74c08e0701952d648e3d30f6781ba03e35582
  monitor 96e59fdc3de7001d9061ce88524879d064fbaff03b162930b43434688f56bcb0
  Shows: "FLOOR32 GATE4 FAILED: 256 of 266", 2026-11-18, without --recheck, on a staging copy whose freeze list is
  not this tree's (anchor 47b4681bc5841749); a generator row and nine plant rows failed.
  Does not show: anything about the `floor32` folder of this tree, whose freeze list differs.
- `p1-floor32-gate4-r2-console.txt` (not in this tree)
  sha256 27dc0af424274e6fa7f7727ee1d214597ea08e69e1d3a6fc5e496fc0fdd93169
  monitor bc7b634f8287c879c8fb55892a1c8ac91092dc0979f105b4fbc5b26537c6f8d3
  Shows: "FLOOR32 GATE4 HELD: 266 of 266", 2026-11-18, without --recheck, anchor 62db0a2ec778fb51 (the value
  `kernel/coq/ANCHORS.md` records for `floor32`).
  Does not show: a recheck of the outside libraries in that run (no --recheck).
- `floor32-gate4-run1-console.txt` (not in this tree)
  sha256 e249c4081199b82dc8bb0c822df03d0ec6c478d611e9433dbbfabae6debb81db
  monitor af3d6a7461c0ec3d139c04566330775666d810c0b23b1633cda3452f6a84ec4a
  Shows: "FLOOR32 GATE4 HELD: 266 of 266", 2026-11-18, with --recheck, the same anchor.
  Does not show: another host or Coq build.
- `floor32-gate4-v2run1-console.txt` (not in this tree), RED
  sha256 2ca9468b55e22947b4154e249157c3b4c4a1f3ab08121f2a3b16b05544a3c558
  monitor 1d5cfcb47fad1d233dc7686f405d735c431266e7fb1f3b476dc9605019955178
  Shows: a run of 2026-11-21 with --recheck, the same anchor, killed by the guard's monitor when the host's free
  memory stayed under its floor; docker exit 137 and no verdict line.
  Does not show: a failure of the gate or of the folder: the run was stopped before its verdict.
- `floor32-gate4-v2run2-console.txt` (not in this tree): the console `THEOREMS.md` names
  sha256 865df7114b46e709bf0d534cbfb05d23a146674115a73dd56597b50b886934a0
  monitor 5dbbeff4f57aeb1f0dd74e4359fe30820f38f091750acf729ce773ad096c88b0
  Shows: "FLOOR32 GATE4 HELD: 266 of 266", 2026-11-21, with --recheck, the same anchor.
  Does not show: another host or Coq build.

## ceil32: gate runs (not in this tree, for the same reason)

- `p1-ceil32-gate4-r1-console.txt` (not in this tree), RED
  sha256 765d433c53931f83cef9c265d39e7d2a8548c0c1b0418311341f6b599d4efed5
  monitor a9873ff30e887fd8459fa24c49f81b1b9f3693c5e5fa8c3c9ea638b49ea8d155
  Shows: "CEIL32 GATE4 FAILED: 257 of 266", 2026-11-18, without --recheck, on the same staging copy (anchor
  1d42f6b79828f91a); nine rows failed.
  Does not show: anything about the `ceil32` folder of this tree, whose freeze list differs.
- `p1-ceil32-gate4-r2-console.txt` (not in this tree)
  sha256 07e12a60d274c4c84e3951df454aa6e74f00c79e463e6b3ee76b603ea1d31635
  monitor 47cc325c9343765b71e24a3644204b3ac9f5335ccbc49609afe84224c977003f
  Shows: "CEIL32 GATE4 HELD: 266 of 266", 2026-11-18, without --recheck, anchor 468d29c862d8e143 (the value
  `kernel/coq/ANCHORS.md` records for `ceil32`).
  Does not show: a recheck of the outside libraries in that run.
- `ceil32-gate4-run1-console.txt` (not in this tree)
  sha256 18ef20d18868cd22a2d6557f2a340fb8ebe8006d3bb8added43dd3a41be2c252
  monitor 85874dcdf456900352dfaf2f7480bb040efc032fa05ec9a63780c32a5d5cd0ed
  Shows: "CEIL32 GATE4 HELD: 266 of 266", 2026-11-18, with --recheck, the same anchor.
  Does not show: another host or Coq build.
- `ceil32-gate4-v2run2-console.txt` (not in this tree): the console `THEOREMS.md` names
  sha256 bc58977215f134dd6d58cdee69346f25170888d3ff0a7a2a5bcec710ea213b30
  monitor 4678b8bbbcd075d0b90c9c323a3b0edd80c6b3b7867c88e17d25948b13db2364
  Shows: "CEIL32 GATE4 HELD: 266 of 266", 2026-11-21, with --recheck, the same anchor. The run named v2run1 before it
  was refused at its start and wrote no console.
  Does not show: another host or Coq build.

## sincos32n and exp32a: gate runs (not in this tree, for the same reason)

Neither folder has a sweep. The first two runs of each were on a staging copy, without --recheck.

- `r1b-sincos32n-console.txt` (not in this tree), RED
  sha256 afa156f2a2a635538b766d1cdc0e91cc95b140b02c48d5b2fa807399dda5366a
  monitor 83ce45c39c88e94a0fc98032102b32c3bf7dbc06207f5f1add55efcf2d937518
  Shows: "SINCOS32N GATE4 FAILED: 126 of 130", 2026-11-18, on a staging copy whose freeze list is not this tree's
  (no anchor given; its freeze list's sha256 starts 96be665f927155d3); four rows failed.
  Does not show: anything about the `sincos32n` folder of this tree, whose freeze list differs.
- `r2-sincos32n-console.txt` (not in this tree)
  sha256 db04eda22975e35e1597c6fea6bb45e80353c48597a7fcccc94b80054958d169
  monitor 9ea6e242529252c57dbd021935182aa739a7864ec11bc8aa65e6ade96c3035e3
  Shows: "SINCOS32N GATE4 HELD: 131 of 131", 2026-11-18, anchor 7cf75e2cc75e86c0 (the value `kernel/coq/ANCHORS.md`
  records for `sincos32n`).
- `r1-exp32a-console.txt` (not in this tree), RED; it has no monitor file
  sha256 204d7f076b449a6e9b4305e41ea30ea226b6c793ec4c33f489fbc1336f086a02
  Shows: "EXP32A GATE4 FAILED: 63 of 67", 2026-11-18, on a staging copy, no anchor given (its freeze list's sha256
  starts 30f24b934799d908, not this tree's); four rows failed.
  Does not show: anything about the `exp32a` folder of this tree, whose freeze list differs.
- `r2-exp32a-console.txt` (not in this tree)
  sha256 ede469b47daa4471bab09ea5424e611ef735b5fb1acb5881ea5c577d352e4e32
  monitor b4a79771e278bf94bf561ea5d721382e8384cbd6865adea7f18113d22c921b92
  Shows: "EXP32A GATE4 HELD: 68 of 68", 2026-11-18, anchor 08c9c09cd28ffcea (the value `kernel/coq/ANCHORS.md` records
  for `exp32a`).
- `sincos32n-gate4-run1-console.txt` (not in this tree)
  sha256 74c976682d5f5575ccb4bba5ac71db236b321adbcee42bbc097b3fc5e15d6b88
  monitor 7bdc76861dfc2e6b66de821e8d69f4d83f34870ab15e0ae122f087ebd21076b6
  Shows: "SINCOS32N GATE4 HELD: 131 of 131", 2026-11-18, with --recheck, anchor 7cf75e2cc75e86c0.
- `sincos32n-gate4-v3run1-console.txt` (not in this tree): the console `THEOREMS.md` names
  sha256 a8041676bed7fb4c2ab474be8b437d14a714a6bcfb9d0ee29d9cdca3b71dcf67
  monitor 7c3628433c23ecd9cd73ca56eeef805bed5a2d0be6544b0b1fafba8ead671d93
  Shows: "SINCOS32N GATE4 HELD: 131 of 131", 2026-11-21, with --recheck, the same anchor.
- `exp32a-gate4-run1-console.txt` (not in this tree)
  sha256 29e21145888a6f68158f3e23beef373334e95e464e8dafcf64d8fbd13e6f4a5f
  monitor 3dfbdd3610a1dc347efe74551ac8295ff5d640549b4ce68080d57e981544ec20
  Shows: "EXP32A GATE4 HELD: 68 of 68", 2026-11-18, with --recheck, anchor 08c9c09cd28ffcea.
- `exp32a-gate4-v3run1-console.txt` (not in this tree): the console `THEOREMS.md` names
  sha256 ac8d9c1e2370c4b96f583b6fbc40d9ec00efa82b92c32bcf79eaafd8b14bafe4
  monitor 3dcd79b5964681309500dc23fb134a14ddf40233783f8543e57f54e0c2212453
  Shows: "EXP32A GATE4 HELD: 68 of 68", started on 2026-11-21 at 23:59 UTC, with --recheck, the same anchor.

Of these eight runs none shows anything on another host or Coq build.

## rti32, order32, bits32 and fclink: gate runs (not in this tree, for the same reason)

Each folder's gate ran three times on 2026-11-22, all with --recheck: a rehearsal and a recheck by a second agent
from a fresh copy, both given the sha256 of the freeze list as the authors computed it, and the final run, given the
owner's own sha256 of it (the same value). The final run's console is the one `THEOREMS.md` names. No run of these
four folders was red.

- `rti32-gate4-r1-console.txt` (not in this tree), rehearsal
  sha256 ea218096cf03a20b65a6368922331a7a9d65f3ef4e0bf57e41ad41fdc16aba3a
  monitor e5582bbdef4c33aa181c30036f46fdb57f21817f4404ed369cc2198903da2ba0
- `rti32-recheck-rc1-console.txt` (not in this tree), recheck from a fresh copy
  sha256 634c3b80ff52709663afe1650d8dbf2e559c6e07dec8a5e23ea03785d75043c6
  monitor 6a348a80b72398f58d129373ec99260bb9d2de4ed54979f799cf17b732812b6d
- `p2final-rti32-gate4-run1-console.txt` (not in this tree), final, the owner's anchor
  sha256 162a298f2e3dcf13d38d95f8fae9ec2c1100ba0fc8a65b5a18697f8997cd130c
  monitor b240f4ca150fe6b5945777c9248656c704f098ecf12817faff8a2db7b944af26
  Shows (all three): "RTI32 GATE4 HELD: 296 of 296", anchor 1f0c20067174f98c.
- `o32-gate4-r1-console.txt` (not in this tree), rehearsal
  sha256 6b336d0b000661be33ea428d921629683b39cac431bb2d519c4829379396fd77
  monitor f944e8a81114176904ad3b6313812968b15fb7b8d331930fa10fcbf7b01eee7a
- `o32-recheck-r1-console.txt` (not in this tree), recheck from a fresh copy
  sha256 8339986d4c80d7a8a369ce17b04d46ea0c77183a8c779124d707bac5c8d35971
  monitor 60252e1286b457f0ec3acc402008f663c3de20b4230f32bd2d54bda5ef2bdc4b
- `p2final-order32-gate4-run1-console.txt` (not in this tree), final, the owner's anchor
  sha256 0188ae9d2ec58f187ec4e16c8f563fc55be338532b2a33d65fdc47caa436fc51
  monitor 1afb02df9bb66b32696308fa1995451efdb844ac819496dfd2413e4370965b58
  Shows (all three): "ORDER32 GATE4 HELD: 296 of 296", anchor 0ea74cf1267a35e0.
- `bits32-gate4-reh1-console.txt` (not in this tree), rehearsal
  sha256 bb6ce7d580446a4948623f69f6c48fc566fda5c753bece7745800db3594976cb
  monitor f24032bc8419e071f35eca29ed792971cf029cce468b7e665bf89aebeda129fa
- `bits32-recheck-rc1-console.txt` (not in this tree), recheck from a fresh copy
  sha256 b506eabd69962f44759f8fb095cb1bd83f4c60f92b8c47073d00ae1f8498d5c2
  monitor 7e8cf9b07c45c3d90cd2db4a1c366b6978b4e25225977f02a8509e864c05b72a
- `p2final-bits32-gate4-run1-console.txt` (not in this tree), final, the owner's anchor
  sha256 aaa537712ed9b44562fa0005dd8189cea8b520cd419f5eefcabd71e639bca71e
  monitor c7aed1cc30f5b43faf4090b3729dd785c5c4e6b7bb1cade1b80e94ef1959047e
  Shows (all three): "BITS32 GATE4 HELD: 296 of 296", anchor 820e15169d17c239.
- `p2-fclink-gate4-r1-console.txt` (not in this tree), rehearsal
  sha256 aed0e7dafab8698518c5fb2c821a8c49ded63e922627f5536fbbc802e7a2b50e
  monitor 625d43e5bbf71d8f2173ff5747c4e69a87b4e28f8a369939baed5d949bb872a3
- `p2-fclink-recheck-gate4-x1-console.txt` (not in this tree), recheck from a fresh copy; its first try was refused
  at its start because another container was running, and no gate ran in that try
  sha256 3766103d1bb9442ba64948e639604ee90a7f072907ebede8d5f5a18112e16bf4
  monitor e1d6573de51bcc604233eb124297eefbbd02f2af3a037ec1a947456c7f08f89d
- `p2final-fclink-gate4-run1-console.txt` (not in this tree), final, the owner's anchor
  sha256 3ef62dbc315449497dd8b6d54037b28645e6af1af815b665489ab1eef1b9371e
  monitor 7d43df8e151c506f8967dbe75fa456f2d3f5850422b73e95fa6f0adc89fc97df
  Shows (all three): "FCLINK GATE4 HELD: 294 of 294", anchor 96ac2c42d44ef185.

Of these twelve runs none shows anything on another host or Coq build, or that the rehearsal and recheck agents were
independent of the authors: all are of one model family.

## bits32: the NaN-bits record sweep of ruling A4 (a) (`kernel/records/bits32/`)

- `kernel/records/bits32/bits32_sweep.c` (in this tree)
  sha256 da83a668b935948cec672ec5480bc6770a844abeef9a5f3f5d577716d7b4ced0
  Shows: the record program: the two C lines that FCLINK states (the lines between the COQ TEXT markers of
  `kernel/coq/fclink/sweep_fc2.c`), copied byte for byte, called as (float)mk_floor32((double)f) and
  (float)mk_ceil32((double)f) with the bits of f and of the result copied by memcpy; each result's 32 bits are
  compared with spec32, BITS32's SPEC32 transcribed by hand into C integers, on all 2^32 patterns; PLANT 1 to 6
  build its plants. Its two copied C lines are longer than 120 characters, as in `sweep_fc2.c`.
  Does not show: that spec32 is SPEC32 (row B103 of `BOUNDARIES.md`).
- `kernel/records/bits32/run_bits32_sweep.sh` (in this tree)
  sha256 c7df2aa87bf9e0973886f30431396008214a575a8620a61c0ede8cfcab536311
  Shows: its runner: the freeze list, the copied blocks checked by text against their sources, seven builds (clang
  -O2 -ffp-contract=off -DPLANT=k), the assembly of the first build scanned for x87 and FMA instructions, then each
  build run in order.
  Does not show: a run with another compiler or on another host.
- `kernel/records/bits32/BITS32-SWEEP-FROZEN.txt` (in this tree)
  sha256 11b2713b4a0ce6b7d7e0e48aa4c3f1b07ee4b32fd22525024396a5e05abca897
  Shows: the freeze list written before run1: the two files above and, under the tier root `kernel/coq`,
  `bits32/BITS32_Statement.v`, `fclink/sweep_fc2.c` and `fclink/KernelText.v`.
  Does not show: who wrote it when, beyond the console's check of the files at run1.
- `kernel/records/bits32/PREDICTIONS-bits32-sweep-run1.txt` (in this tree)
  sha256 7b443e3cd800a47469bd4430cacb6b9edf437eafa756cfec8cf89ae09274e006
  Shows: the counts of every build, fixed before run1.
  Does not show: when it was written, beyond its own text and the console's check of the other files.
- `kernel/records/bits32/TRANSCRIPTION.md` (in this tree)
  sha256 c21f9c8ae50aa9035f7ba59a598b4292427dedcc3aab747d921695e832b0c34f
  Shows: each line of SPEC32 beside its line of spec32, with the argument that they agree (ARGUED).
  Does not show: that spec32 is SPEC32 (an argument only; row B103 of `BOUNDARIES.md`).
- `kernel/records/bits32/bits32-sweep-run1-console.txt` (in this tree)
  sha256 eb7edf274117264bcebd07533287a657080143bd092fa7ccddc134c915dd81c1
  Shows: run1, 2026-11-22, clang 22.1.8 for x86_64-pc-windows-msvc, -O2 -ffp-contract=off, MXCSR 0x1f80: every
  freeze and copy line as required; in the build without a plant, the results of both functions equal spec32 in all
  32 bits on every pattern: 4,278,190,080 finite, 2 infinite, 8,388,608 quiet NaN and 8,388,606 signalling NaN, 0
  differing; spec32 equals a second integer text on every pattern and the integer reference on every pattern that is
  not a NaN; no x87 load or store and no FMA instruction in that build's assembly; plants 1 to 5 differ at their
  fixed counts; the build run with denormals-are-zero set (PLANT 6, MXCSR 0x1fc0) differs on 8,388,607 finite
  patterns of each function and its environment row fails, as fixed. "BITS32 SWEEP HELD" (MEASURED, one run on one
  host).
  Does not show: another compiler, flag, processor or system; a caller that converts binary32 on integer bits (no
  such caller of floor32 or ceil32 is in this tree; NOT_MEASURED); exception flags; that spec32 is SPEC32.
- `kernel/records/bits32/k1-run1-console.txt` (in this tree)
  sha256 e06bfcead5239f964eb307fb85f8c6d031ec599198fe39aced03dee040e50b36
  Shows: check K1 of the landing: `kernel/coq/fclink/gen_kernel_text.py` (a byte copy) run on `bits32_sweep.c`
  prints `KernelText.v` but for its first line, which names the file read, so the copied lines are the quoted text;
  a planted digit is caught; with the comparison removed the plant is not caught (third run), and the record alone
  reads "K1 TIE FAILED" (fourth run), as that stage predicted before its run.
  Does not show: anything a reader can rerun from this tree alone: the check's script is kept in the workspace.
- `kernel/records/bits32/k2-run1-console.txt` (in this tree)
  sha256 29d389f70195eff8de9a2d6876829dc6ea9639eff163294d71712ea87cb00a6e
  Shows: check K2 of the landing: spec32, compiled and listed on 4,096 patterns in both directions (8,192 rows),
  agrees with a Python transcription of SPEC32's Coq text, 0 disagreements and equal checksums; its plants q21 (20
  disagreements) and zero (1,015) are caught; with the comparisons removed, q21 is missed (zero was not run so).
  Does not show: Coq's own evaluation of SPEC32 on those patterns (NOT_MEASURED); the scripts are kept in the
  workspace.

## fclink: the sweep job's check on `kernel/coq/fclink/sweep_fc2.c` (`kernel/records/fclink/`)

The program itself is frozen in `kernel/coq/fclink` (its `FROZEN.txt` and `FROZEN4.txt` record it).

- `kernel/records/fclink/local-fclink-run1.txt` (in this tree)
  sha256 39a997d8a41b46799d14de820a5072e2307a3792ce534d21a222f7d32f8968fc
  Shows: `tools/ci/check_sweep.py` on candidate `fclink`, on a scratch root, 2026-11-22, clang 22.1.8 and
  llvm-objdump: "SWEEP CHECK HELD: 19 of 19 rows (fclink; x86-64; clang)" (MEASURED, one run on one host).
- `kernel/records/fclink/sweep-real-r1.txt` (in this tree)
  sha256 804868367781649c199df4e8c2e982b696dfe5e17c30c91ca920a77b9f74340a
  Shows: the same check on this tree once `kernel/coq/fclink` was in it, 2026-11-22: "SWEEP CHECK HELD: 19 of 19
  rows (fclink; x86-64; clang)" (MEASURED, one run on one host).

Neither shows GCC, Linux, arm64 or GitHub's runners (NOT_MEASURED), NaN payloads (the program compares a NaN as
NaN-ness only), or the C library's floorf and ceilf, which are linked, not scanned.
