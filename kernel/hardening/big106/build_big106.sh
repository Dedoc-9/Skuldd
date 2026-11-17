#!/bin/sh
# Container side of the +2^106 examples (2026-11-17, scratch; written by the assistant). /pre = the prebuilt frozen
# closure (READ ONLY), /p = this folder (READ ONLY), /b = tmpfs. Compiles Big106.v, prints Print Assumptions of every
# example, and runs one recursive coqchk with its summary printed whole. Writes nothing outside /b.
set -u
cp /p/Big106.v /b/ || exit 2
cd /b || exit 2
s=$(date +%s); coqc -R /pre MKF -R /b R106 /b/Big106.v > /b/c.out 2>&1; rc=$?
echo "coqc Big106.v exit $rc ($(( $(date +%s) - s )) s)"; [ "$rc" = 0 ] || { head -c 3000 /b/c.out; exit 1; }
echo "examples: $(grep -c '^Example' /b/Big106.v)"
printf 'From R106 Require Import Big106.\n' > /b/PA.v
for n in $(grep -o '^Example [a-z0-9_]*' /b/Big106.v | cut -d' ' -f2); do printf 'Print Assumptions %s.\n' "$n" >> /b/PA.v; done
coqc -R /pre MKF -R /b R106 /b/PA.v > /b/pa.out 2>&1; echo "Print Assumptions run exit $?"
echo "Print Assumptions: $(grep -c '^Closed under the global context' /b/pa.out) closed, $(grep -c '^Axioms:' /b/pa.out) with axioms; names that occur:"
grep -E "^[A-Za-z_][A-Za-z0-9_.']* :" /b/pa.out | cut -d' ' -f1 | sort | uniq -c
s=$(date +%s); coqchk -silent -o -R /pre MKF -R /b R106 R106.Big106 > /b/chk.out 2>&1; rc=$?
echo "recursive coqchk R106.Big106 exit $rc ($(( $(date +%s) - s )) s); its summary:"
sed -n '/CONTEXT SUMMARY/,$p' /b/chk.out
[ "$rc" = 0 ] && echo "BIG106 EXAMPLES CHECKED" || echo "BIG106 EXAMPLES FAILED AT COQCHK"
