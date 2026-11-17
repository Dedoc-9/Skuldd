#!/bin/sh
# Container side of R4 (e): /m = mkf-ext mounted READ ONLY, /e = ext-work/harden-r4/examples mounted READ ONLY, /b a
# tmpfs. Copies the sources the examples need from /m into /b/root (the frozen statements and their dependencies),
# adds Examples.v as MKF.r4ex.Examples, compiles in order, then one recursive coqchk with its summary printed whole,
# and Print Assumptions of every example. Writes nothing outside /b.
set -u
B=/b/root
SRC="f32/F32_Statement.v p32/Graphs.v p32/P32_Statement.v p32r/P32R_Statement.v exp32/Graph.v exp32/EXP32_Statement.v ieee64/IEEE64_Statement.v sin32/Graph.v cos32/Graph.v sincos32/Graph.v sincos32i/SINCOS32_IEEE_Statement.v sincos32z/SINCOS32_IEEE_Zero_Statement.v"
for f in $SRC; do mkdir -p "$B/$(dirname "$f")" && cp "/m/$f" "$B/$f" || exit 2; done
mkdir -p "$B/r4ex" && cp /e/Examples2.v "$B/r4ex/Examples.v" || exit 2
sha256sum "$B/sincos32i/SINCOS32_IEEE_Statement.v" "$B/sincos32z/SINCOS32_IEEE_Zero_Statement.v" "$B/r4ex/Examples.v"
cd "$B" || exit 2
for f in $SRC r4ex/Examples.v; do
  s=$(date +%s); coqc -R "$B" MKF "$B/$f" > "/b/$(echo "$f" | tr / .).out" 2>&1; rc=$?
  echo "coqc $f exit $rc ($(( $(date +%s) - s )) s)"
  [ "$rc" = 0 ] || { head -c 3000 "/b/$(echo "$f" | tr / .).out"; echo "BUILD FAILED at $f"; exit 1; }
done
grep -c "^Example\|^Proof" "$B/r4ex/Examples.v"
printf 'From MKF Require Import r4ex.Examples.\n' > "$B/r4ex/PA.v"
for n in $(grep -o "^Example [a-z_]*" "$B/r4ex/Examples.v" | cut -d' ' -f2); do printf 'Print Assumptions %s.\n' "$n" >> "$B/r4ex/PA.v"; done
coqc -R "$B" MKF "$B/r4ex/PA.v" > /b/pa.out 2>&1; echo "Print Assumptions run exit $?"
echo "Print Assumptions: $(grep -c '^Closed under the global context' /b/pa.out) closed, $(grep -c '^Axioms:' /b/pa.out) with axioms; the axiom names that occur:"
grep -E "^[A-Za-z_][A-Za-z0-9_.']* :" /b/pa.out | cut -d' ' -f1 | sort | uniq -c
s=$(date +%s); coqchk -silent -o -R "$B" MKF MKF.r4ex.Examples > /b/chk.out 2>&1; rc=$?
echo "recursive coqchk MKF.r4ex.Examples exit $rc ($(( $(date +%s) - s )) s); its summary:"
sed -n '/CONTEXT SUMMARY/,$p' /b/chk.out
[ "$rc" = 0 ] && echo "R4 EXAMPLES CHECKED" || echo "R4 EXAMPLES FAILED"
