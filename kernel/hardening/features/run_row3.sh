#!/bin/sh
# Host side of the feature row's version 3 check (2026-11-17, scratch; written by the assistant). Run from the
# workspace root: sh ext-work/harden-r4/features/run_row3.sh <python>. Reads only.
set -u
PY=$1; F=ext-work/harden-r4/features
export PYTHONHASHSEED=0 PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
echo "== inputs"
sha256sum $F/PREDICTIONS-row3-2026-11-17.md $F/feature_row2.py $F/feature_row3.py $F/make_feature_plants3.py | sed 's/ \*/  /'
echo "== Q1, Q2: version 3 on plants3"
for p in $(ls $F/plants3/*.v | sort); do
  n=$(basename $p)
  out=$("$PY" -B $F/feature_row3.py $F/plants3 $n 2>&1); r=$?
  case $n in refuse3_*) want=1;; *) want=0;; esac
  [ $r = $want ] && v=ok || v=MISMATCH
  echo "  $v  $n  exit $r  $(echo "$out" | grep REFUSED | sed 's/^ *REFUSED [^:]*: //' | tr '\n' ';' | cut -c1-150)"
done
echo "== Q3: version 3 against version 2 on version 2's plants"
for d in plants plants2; do
  for p in $(ls $F/$d/*.v | sort); do
    n=$(basename $p)
    "$PY" -B $F/feature_row2.py $F/$d $n > /dev/null 2>&1; r2=$?
    "$PY" -B $F/feature_row3.py $F/$d $n > /dev/null 2>&1; r3=$?
    [ $r2 = $r3 ] && v=same || v=DIFFERENT
    echo "  $v  $d/$n  version 2 exit $r2, version 3 exit $r3"
  done
done
echo "== Q4: version 3 on the tier"
echo "-- the closure of sincos32z"; "$PY" -B $F/feature_row3.py mkf-ext --list mkf-ext/sincos32z/FROZEN4.txt; echo "exit $?"
echo "-- the closure of sincos32i"; "$PY" -B $F/feature_row3.py mkf-ext --list mkf-ext/sincos32i/FROZEN4.txt; echo "exit $?"
echo "-- law statement draft M"; "$PY" -B $F/feature_row3.py ext-work/sincos32-law draftM/SINCOS32_LAW_Statement.v; echo "exit $?"
echo "-- every .v of mkf-ext outside plants/ and out4/"
"$PY" -B $F/feature_row3.py mkf-ext $(cd mkf-ext && find . -name '*.v' -not -path '*/plants/*' -not -path '*/out4/*' | sed 's#^\./##' | sort); echo "exit $?"
