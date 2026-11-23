#!/bin/sh
# run_bits32_sweep.sh: builds and runs the record sweep bits32_sweep.c (ruling A4 (a), Skuldd's Push A). Written
# 2026-11-22 by a stage agent of the assistant. Frozen by sha256 in BITS32-SWEEP-FROZEN.txt beside it. Tools: sh,
# sha256sum, sed, awk, cmp, diff, grep, wc, date, clang.
#
#   run_bits32_sweep.sh RUN CONSOLE_DIR TIER_ROOT [NANBITS_C]
#     RUN          a new run name (letters, digits, '-' and '_'): refused, with nothing written, if
#                  CONSOLE_DIR/bits32-sweep-RUN-console.txt or the folder bin-RUN beside this script exists
#     CONSOLE_DIR  the folder the console is written to
#     TIER_ROOT    the folder holding bits32/BITS32_Statement.v, fclink/sweep_fc2.c and fclink/KernelText.v (the
#                  frozen statement and the frozen file holding the C text under test)
#     NANBITS_C    optional: the research sweep nanbits.c (2026-11-21), to compare the copy of its spec() by text;
#                  without it that copy is fixed only by bits32_sweep.c's sha256, and the console says so
#   BITS32_SWEEP_DRY=1 in the environment: stop after the file and text checks, nothing built (to test those checks)
#   run_bits32_sweep.sh --scan-asm FILE: print an assembly file's instruction counts and the x87/FMA row (to test
#                  the scan on a planted file)
#
# Order: the files against BITS32-SWEEP-FROZEN.txt (two names beside this script, three under TIER_ROOT, each set
# exactly as listed); the copied blocks of bits32_sweep.c against their sources by text; the compiler's version;
# seven builds, clang -O2 -ffp-contract=off -DPLANT=k, k = 0 to 6, PLANT 5 from a copy made here whose two COQ TEXT
# lines read "<" for "<=" before their zero test (checked: two replacements, the only lines that differ, the two text
# lines); every binary's sha256; the assembly of the PLANT 0 build and its instruction counts, the x87 fld/fstp and
# FMA counts required to be 0; each build run in the order 0 to 6, the run stopping at the first build whose rows are
# not as fixed. Last line: BITS32 SWEEP HELD (bits32_sweep.c <sha256 prefix>) or BITS32 SWEEP FAILED.
# Compiles run inside the record folder with relative names; the console names no absolute path.

scan_asm() {
  printf 'asm instruction counts (%s):' "$(basename "$1")"
  for i in cvtss2sd cvtps2pd cvtsd2ss cvtpd2ps addsd addpd subsd subpd mulsd mulpd andpd fld fstp vfmadd vfmsub \
           vfnmadd vfnmsub; do
    printf ' %s=%s' "$i" "$(grep -c -i -E "^[[:space:]]+v?$i" "$1")"
  done
  printf '\n'
  bad=$(grep -c -i -E '^[[:space:]]+(fld|fstp|vfmadd|vfmsub|vfnmadd|vfnmsub)' "$1")
  if [ "$bad" = 0 ]; then echo "asm row, x87 fld/fstp and FMA lines 0: holds"; return 0; fi
  echo "asm row, x87 fld/fstp and FMA lines 0: FAILS ($bad lines)"; return 1
}

if [ "${1:-}" = "--scan-asm" ]; then
  [ -f "${2:-}" ] || { echo "usage: run_bits32_sweep.sh --scan-asm FILE"; exit 2; }
  scan_asm "$2"; exit $?
fi

RUN="${1:-}"; CD="${2:-}"; TIER="${3:-}"; NB="${4:-}"
case "$RUN" in
  ''|*[!A-Za-z0-9_-]*) echo "usage: run_bits32_sweep.sh RUN CONSOLE_DIR TIER_ROOT [NANBITS_C]"; exit 2;;
esac
[ -d "$CD" ] && [ -d "$TIER" ] || { echo "run_bits32_sweep.sh: CONSOLE_DIR or TIER_ROOT is not a folder"; exit 2; }
[ -z "$NB" ] || [ -f "$NB" ] || { echo "run_bits32_sweep.sh: NANBITS_C is not a file"; exit 2; }
D=$(cd "$(dirname "$0")" && pwd); C="$CD/bits32-sweep-$RUN-console.txt"; B="$D/bin-$RUN"
if [ -e "$C" ] || [ -e "$B" ]; then
  echo "run_bits32_sweep.sh: refused: run $RUN has a console or a bin folder"; exit 2
fi
mkdir "$B" || exit 2
END='/* ---- end verbatim ---- */'

cpy() { awk -v s="$2" -v e="$END" '$0 == s { f = 1; next } f && $0 == e { exit } f' "$1"; }

check_frozen() {
  F="$D/BITS32-SWEEP-FROZEN.txt"
  [ -f "$F" ] || { echo "no BITS32-SWEEP-FROZEN.txt"; return 1; }
  grep -v '^#' "$F" | grep -v '^$' | grep -v '/' > "$B/frozen-local.txt"
  grep -v '^#' "$F" | grep -v '^$' | grep '/' > "$B/frozen-tier.txt"
  nl=$(awk '{ print $2 }' "$B/frozen-local.txt" | sort | tr '\n' ' ')
  nt=$(awk '{ print $2 }' "$B/frozen-tier.txt" | sort | tr '\n' ' ')
  [ "$nl" = "bits32_sweep.c run_bits32_sweep.sh " ] || { echo "freeze list: local names are: $nl"; return 1; }
  [ "$nt" = "bits32/BITS32_Statement.v fclink/KernelText.v fclink/sweep_fc2.c " ] || {
    echo "freeze list: tier names are: $nt"; return 1; }
  (cd "$D" && sha256sum -c "$B/frozen-local.txt") || return 1
  (cd "$TIER" && sha256sum -c "$B/frozen-tier.txt") || return 1
  return 0
}

check_copies() {
  S="$TIER/fclink/sweep_fc2.c"; r=0
  for b in "37 38" "40 43" "58 71"; do
    set -- $b
    cpy "$D/bits32_sweep.c" "/* ---- verbatim: fclink/sweep_fc2.c lines $1-$2 ---- */" > "$B/copy-$1.c"
    sed -n "$1,$2p" "$S" > "$B/source-$1.c"
    if [ -s "$B/source-$1.c" ] && cmp -s "$B/copy-$1.c" "$B/source-$1.c"; then
      echo "copy of fclink/sweep_fc2.c lines $1-$2: identical ($(wc -l < "$B/copy-$1.c") lines)"
    else echo "copy of fclink/sweep_fc2.c lines $1-$2: DIFFERS"; r=1; fi
  done
  cpy "$D/bits32_sweep.c" "/* ---- verbatim: nanbits.c lines 63-77 ---- */" > "$B/copy-nanbits.c"
  if [ -n "$NB" ]; then
    sed -n '63,77p' "$NB" > "$B/source-nanbits.c"
    echo "nanbits.c given: sha256 $(sha256sum < "$NB" | cut -c1-64)"
    if [ -s "$B/source-nanbits.c" ] && cmp -s "$B/copy-nanbits.c" "$B/source-nanbits.c"; then
      echo "copy of nanbits.c lines 63-77: identical ($(wc -l < "$B/copy-nanbits.c") lines)"
    else echo "copy of nanbits.c lines 63-77: DIFFERS"; r=1; fi
  else
    echo "copy of nanbits.c lines 63-77: not compared (nanbits.c not given); fixed by bits32_sweep.c's sha256 only"
  fi
  return $r
}

make_pl5() {
  sed 's/<= 0\.0 ? (x \* 0\.0)/< 0.0 ? (x * 0.0)/g' "$D/bits32_sweep.c" > "$B/bits32_sweep_pl5.c"
  L=$(grep -n -x -F '/* BEGIN COQ TEXT */' "$D/bits32_sweep.c" | cut -d: -f1)
  n0=$(grep -o -F '<= 0.0 ? (x * 0.0)' "$D/bits32_sweep.c" | wc -l)
  n1=$(grep -o -F '<= 0.0 ? (x * 0.0)' "$B/bits32_sweep_pl5.c" | wc -l)
  h=$(diff "$D/bits32_sweep.c" "$B/bits32_sweep_pl5.c" | grep -v '^[<>-]')
  want="$((L + 1)),$((L + 2))c$((L + 1)),$((L + 2))"
  echo "PL5 copy: zero tests '<=' before the replacement $((n0)), after $((n1)); lines changed: $h (want $want)"
  [ "$((n0))" = 2 ] && [ "$((n1))" = 0 ] && [ "$h" = "$want" ]
}

main_run() {
  echo "bits32 sweep $RUN, $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  check_frozen || { echo "BITS32 SWEEP FAILED: the files are not the frozen ones"; return 1; }
  check_copies || { echo "BITS32 SWEEP FAILED: a copied block differs from its source"; return 1; }
  if [ "${BITS32_SWEEP_DRY:-}" = 1 ]; then echo "BITS32 SWEEP CHECKS PASSED (dry run: nothing built)"; return 0; fi
  make_pl5 || { echo "BITS32 SWEEP FAILED: the PL5 copy is not the planned plant"; return 1; }
  clang --version | head -n 2
  cd "$D" || return 1
  for k in 0 1 2 3 4 6; do
    clang -O2 -ffp-contract=off -DPLANT=$k bits32_sweep.c -o "bin-$RUN/bits32_sweep_$k.exe" || {
      echo "BITS32 SWEEP FAILED: build $k"; return 1; }
  done
  (cd "bin-$RUN" && clang -O2 -ffp-contract=off -DPLANT=5 bits32_sweep_pl5.c -o bits32_sweep_5.exe) || {
    echo "BITS32 SWEEP FAILED: build 5"; return 1; }
  clang -O2 -ffp-contract=off -DPLANT=0 -S bits32_sweep.c -o "bin-$RUN/bits32_sweep_0.s" || {
    echo "BITS32 SWEEP FAILED: assembly"; return 1; }
  echo "build: clang -O2 -ffp-contract=off -DPLANT=k (k = 0 to 6; 5 from bits32_sweep_pl5.c)"
  (cd "bin-$RUN" && sha256sum bits32_sweep_0.exe bits32_sweep_1.exe bits32_sweep_2.exe bits32_sweep_3.exe \
    bits32_sweep_4.exe bits32_sweep_5.exe bits32_sweep_6.exe bits32_sweep_0.s bits32_sweep_pl5.c)
  scan_asm "bin-$RUN/bits32_sweep_0.s" || { echo "BITS32 SWEEP FAILED: x87 or FMA in the assembly"; return 1; }
  for k in 0 1 2 3 4 5 6; do
    s=$(date +%s); "./bin-$RUN/bits32_sweep_$k.exe"; r=$?; echo "PLANT=$k exit $r ($(( $(date +%s) - s )) s)"
    [ $r = 0 ] || { echo "BITS32 SWEEP FAILED: build $k is not as fixed; the run stops here"; return 1; }
  done
  echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "BITS32 SWEEP HELD (bits32_sweep.c $(sha256sum < bits32_sweep.c | cut -c1-16))"
  return 0
}

main_run > "$C" 2>&1; rc=$?
tail -n 12 "$C"
exit $rc
