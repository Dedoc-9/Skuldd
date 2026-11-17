#!/bin/sh
# Container side of R4 (d). /pre = the prebuilt closure (READ ONLY; plants/prebuilt/root), /s = plants/stage (READ ONLY),
# /b = tmpfs. Copies the stage into /b, compiles R4Lib, each planted S.v and its Refute.v (logical root R4PL), then
# Check.v (Print Assumptions of every refutation) and one recursive coqchk of the Check module, summary printed whole.
set -u
cp -r /s/. /b/ || exit 2
cd /b || exit 2
c() { s=$(date +%s); coqc -R /pre MKF -R /b R4PL "/b/$1" > "/b/$(echo "$1" | tr / .).out" 2>&1; rc=$?; echo "coqc $1 exit $rc ($(( $(date +%s) - s )) s)"; [ "$rc" = 0 ] || head -c 1500 "/b/$(echo "$1" | tr / .).out"; return $rc; }
c R4Lib.v || { echo "R4LIB FAILED"; exit 1; }
nok=0; nfail=0
for t in $(cat /b/order.txt); do
  if [ -f "/b/$t/S.v" ]; then c "$t/S.v" || { nfail=$((nfail+1)); echo "PLANTED FILE FAILED: $t"; continue; }; fi
  if c "$t/Refute.v"; then nok=$((nok+1)); else nfail=$((nfail+1)); echo "REFUTATION FAILED: $t"; fi
done
echo "refutations compiled: $nok; failed: $nfail"
[ "$nfail" = 0 ] || { echo "R4 REFUTATIONS INCOMPLETE"; exit 1; }
c Check.v || exit 1
echo "Print Assumptions: $(grep -c '^Axioms:' /b/Check.v.out) with axioms, $(grep -c '^Closed under the global context' /b/Check.v.out) closed; names that occur:"
grep -E "^[A-Za-z_][A-Za-z0-9_.']* :" /b/Check.v.out | cut -d' ' -f1 | sort | uniq -c
s=$(date +%s); coqchk -silent -o -R /pre MKF -R /b R4PL R4PL.Check > /b/chk.out 2>&1; rc=$?
echo "recursive coqchk R4PL.Check exit $rc ($(( $(date +%s) - s )) s); its summary:"
sed -n '/CONTEXT SUMMARY/,$p' /b/chk.out
[ "$rc" = 0 ] && echo "R4 REFUTATIONS CHECKED" || echo "R4 REFUTATIONS FAILED AT COQCHK"
