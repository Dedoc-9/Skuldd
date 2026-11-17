#!/bin/sh
# Host side of the feature row's version 2 check (2026-11-17, scratch; written by the assistant). Run from the
# workspace root: sh ext-work/harden-r4/features/run_row2.sh <python> <scratch dir>. Reads only; writes only into the
# scratch dir given.
set -u
PY=$1; T=$2; F=ext-work/harden-r4/features
export PYTHONHASHSEED=0 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
echo "== inputs"
sha256sum $F/PREDICTIONS-row2-2026-11-17.md $F/feature_row.py $F/feature_row2.py $F/make_feature_plants2.py $F/plants2/*.v | sed 's/ \*/  /'
echo "== P1, P3: version 1 and version 2 on plants2"
for p in $(ls $F/plants2/*.v | sort); do
  n=$(basename $p)
  "$PY" -B $F/feature_row.py $F/plants2 $n > $T/v1.out 2>&1; r1=$?
  "$PY" -B $F/feature_row2.py $F/plants2 $n > $T/v2.out 2>&1; r2=$?
  echo "  $n: version 1 exit $r1, version 2 exit $r2"
  grep "REFUSED" $T/v2.out | sed 's/^/      v2 /'
  grep "REFUSED" $T/v1.out | sed 's/^/      v1 /'
done
echo "== P4: version 2 against version 1 on version 1's plants"
same=0; diff=0
for p in $(ls $F/plants/*.v | sort); do
  n=$(basename $p)
  "$PY" -B $F/feature_row.py $F/plants $n > /dev/null 2>&1; r1=$?
  "$PY" -B $F/feature_row2.py $F/plants $n > /dev/null 2>&1; r2=$?
  if [ $r1 = $r2 ]; then same=$((same+1)); else diff=$((diff+1)); echo "  DIFFERS: $n version 1 exit $r1, version 2 exit $r2"; fi
done
echo "  same verdict: $same; different: $diff"
echo "== P5: version 2 on the tier"
echo "-- the closure of sincos32z (its FROZEN4 list, plants excluded)"
"$PY" -B $F/feature_row2.py mkf-ext --list mkf-ext/sincos32z/FROZEN4.txt; echo "exit $?"
echo "-- the closure of sincos32i (its FROZEN4 list, plants excluded)"
"$PY" -B $F/feature_row2.py mkf-ext --list mkf-ext/sincos32i/FROZEN4.txt; echo "exit $?"
echo "-- law statement draft M"
"$PY" -B $F/feature_row2.py ext-work/sincos32-law draftM/SINCOS32_LAW_Statement.v; echo "exit $?"
echo "-- every .v of mkf-ext outside plants/ and out4/"
"$PY" -B $F/feature_row2.py mkf-ext $(cd mkf-ext && find . -name '*.v' -not -path '*/plants/*' -not -path '*/out4/*' | sed 's#^\./##' | sort); echo "exit $?"
