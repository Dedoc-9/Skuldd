#!/bin/sh
# Container side of the feature row's version 2 check (2026-11-17, scratch; written by the assistant).
# /p = features/plants2 (READ ONLY), /h = harness folder (READ ONLY, for its summary reader), /b = tmpfs.
# Compiles each plant as it is, then each evade_* plant with a probe appended, then one recursive coqchk of the
# hidden-fixpoint plant read by the harness's own reader. Writes nothing outside /b.
set -u
cp /p/*.v /b/ || exit 2
cd /b || exit 2
n=0; ok=0
for f in $(ls /p | grep '\.v$' | sort); do
  n=$((n+1)); coqc -R /b P2 "/b/$f" > "/b/$f.out" 2>&1; rc=$?
  echo "coqc $f exit $rc"; [ "$rc" = 0 ] && ok=$((ok+1)) || head -c 800 "/b/$f.out"
done
echo "plants compiled: $ok of $n"
for f in $(ls /p | grep '^evade_.*\.v$' | sort); do
  p="probe_$f"; cat "/p/$f" > "/b/$p"; printf 'Test Guard Checking.\nTest Definitional UIP.\n' >> "/b/$p"
  coqc -R /b P2 "/b/$p" > "/b/$p.out" 2>&1; rc=$?
  echo "== probe of $f: coqc exit $rc; its output:"; head -c 800 "/b/$p.out"; echo
done
coqchk -silent -o -R /b P2 P2.evade_hidden_fixpoint > /b/chk.out 2>&1; rc=$?
echo "== recursive coqchk P2.evade_hidden_fixpoint exit $rc; output from its summary:"
sed -n '/CONTEXT SUMMARY/,$p' /b/chk.out | head -40
[ "$rc" = 0 ] || head -c 1500 /b/chk.out
echo "== the harness's reader (harness.py read_chk) on that output:"
python3 -B -c "import sys; sys.path.insert(0, '/h'); import harness as H; ok, ax, viol = H.read_chk(open('/b/chk.out').read()); print('accepted' if ok else 'REFUSED'); print(viol)"
