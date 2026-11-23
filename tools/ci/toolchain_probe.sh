# SPDX-License-Identifier: AGPL-3.0-only
# toolchain_probe.sh: prints the toolchain of the CI image it runs in, one "<key> <value>" line each, for
# tools/ci/check_toolchain.py to compare with ci/mathkernel/EXPECTED-TOOLCHAIN.txt. The keys compared there:
#   sha256 <path> <hex>     /opt/mk-switch.export, and the coqc, coqchk and python3 that `command -v` finds (the
#                           path printed is the one it finds)
#   coq-version <line>      the first line `coqc --version` prints
#   python-version <line>   the first line `python3 --version` prints
#   opam <name> <version>   every package `opam list --installed` names, the compiler's base packages included
# Then the keys recorded but not compared, printed last, so that an output cut short lacks them:
#   coqc-where <dir>                what `coqc -where` prints
#   coqchk-bytecode-default <line>  the line of `coqchk -help` that names -bytecode-compiler, or "unknown"
#   env <NAME> <value>              for COQPATH, COQLIB, OCAMLPATH and OCAMLRUNPARAM: the value, or "unset", or
#                                   "failed" for a value holding a line feed (its lines would be read as keys)
# A compared value it cannot read is printed as "not-found" or "failed" (an opam line it cannot read under the key
# "opam-unparsed", and an opam list that fails or names nothing as "opam-list failed" or "opam-list empty", keys
# check_toolchain.py refuses as unexpected); it then exits 1, after printing every line. It exits 0 when every
# compared value was read; a record-only value it cannot read is printed as "failed" or "unknown" and leaves the exit
# status as it is.
# It only reads; it writes nothing but its output. POSIX sh; it needs sha256sum, sed and grep.
# What its output shows: what this image holds, as these commands report it. It judges nothing (check_toolchain.py
# does), and a hash does not show how a tool behaves.
# Usage, inside the image, the tree mounted: sh tools/ci/toolchain_probe.sh > toolchain-observed.txt
set -u
LC_ALL=C
OPAMCOLOR=never
OPAMROOTISOK=1
export LC_ALL OPAMCOLOR OPAMROOTISOK
status=0

say() {
  printf '%s %s\n' "$1" "$2"
}

hash_line() {
  h=''
  if [ -f "$1" ] && [ -r "$1" ]; then
    h=$(sha256sum < "$1" 2>/dev/null) || h=''
    h=${h%% *}
  fi
  case $h in
    *[!0-9a-f]*) h='' ;;
  esac
  if [ "${#h}" -eq 64 ]; then
    say "sha256 $1" "$h"
  else
    say "sha256 $1" failed
    status=1
  fi
}

tool_hash() {
  p=$(command -v "$1" 2>/dev/null) || p=''
  case $p in
    /*) hash_line "$p" ;;
    *) say "sha256 $1" not-found; status=1 ;;
  esac
}

first_line() {
  v=$("$@" 2>/dev/null) || v=''
  printf '%s\n' "$v" | sed -n '1p'
}

version_line() {
  k=$1
  shift
  v=$(first_line "$@")
  if [ -n "$v" ]; then
    say "$k" "$v"
  else
    say "$k" failed
    status=1
  fi
}

opam_lines() {
  if out=$(opam list --installed --columns=name,version 2>/dev/null); then
    :
  else
    say opam-list failed
    status=1
    return
  fi
  n=0
  while read -r name ver rest; do
    case $name in
      ''|'#'*) continue ;;
    esac
    if [ -n "$ver" ] && [ -z "$rest" ]; then
      say "opam $name" "$ver"
      n=$((n + 1))
    else
      say opam-unparsed "$name $ver $rest"
      status=1
    fi
  done <<EOF
$out
EOF
  if [ "$n" -eq 0 ]; then
    say opam-list empty
    status=1
  fi
}

hash_line /opt/mk-switch.export
tool_hash coqc
tool_hash coqchk
tool_hash python3
version_line coq-version coqc --version
version_line python-version python3 --version
opam_lines

v=$(first_line coqc -where)
[ -n "$v" ] || v=failed
say coqc-where "$v"

v=$(coqchk -help 2>&1 | grep -F -e '-bytecode-compiler' | sed -n '1p')
v=$(printf '%s\n' "$v" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
[ -n "$v" ] || v=unknown
say coqchk-bytecode-default "$v"

for name in COQPATH COQLIB OCAMLPATH OCAMLRUNPARAM; do
  eval "isset=\${$name+set}"
  if [ "$isset" = set ]; then
    eval "v=\$$name"
    # a value holding a line feed would print lines of its own, which the check would read as keys
    case $v in
      *'
'*) v=failed ;;
    esac
    say "env $name" "$v"
  else
    say "env $name" unset
  fi
done
exit "$status"
