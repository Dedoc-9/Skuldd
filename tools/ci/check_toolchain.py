# SPDX-License-Identifier: AGPL-3.0-only
"""Compare the toolchain a CI image holds with the one recorded for it (standard library only).

tools/ci/toolchain_probe.sh, run inside the image, prints "<key> <value>" lines; this script compares them with
ci/mathkernel/EXPECTED-TOOLCHAIN.txt. A key is "sha256 <path>" (its value is the line's last field), "opam <name>" or
"env <NAME>" (two words), or else the line's first word. Rows, each ok or FAIL:

  expected toolchain file          it reads as UTF-8; each line that is not blank and not a "#" comment is a key and
                                   a value of a kind compared here (sha256, coq-version, python-version, opam); no
                                   key twice; at least one key
  observed probe output            it reads as UTF-8, with no byte-order mark; every line is a key and a value, with
                                   no carriage return; no key twice; at least one key
  tool and switch-export hashes    the expected file names the sha256 of /opt/mk-switch.export, coqc, coqchk and
                                   python3, and each sha256 it names is observed with an equal value
  Coq version line                 the expected coq-version is observed, equal
  Python version line              the expected python-version is observed, equal
  opam packages at their versions  every opam package the expected file names (at least one) is observed at its version
  no unexpected opam package       every opam package observed is expected, apart from the compiler's base packages
                                   base-bigarray, base-threads and base-unix at version "base", which the expected
                                   file leaves out: they alone are allowed by name, and at that version only
  no unexpected key                every other key observed is expected or one of the record-only keys
  record-only keys present         coqc-where, coqchk-bytecode-default and env COQPATH, COQLIB, OCAMLPATH and
                                   OCAMLRUNPARAM are observed (the probe prints them last, so an output cut short
                                   fails here); their values are recorded, not compared

A row that needs a file that was not read fails. Values are compared exactly: no space or case is ignored. Then
"TOOLCHAIN DIGEST <hex>", the sha256 of the observed lines other than the record-only keys, sorted by their bytes, each
ended by a newline ("none" when the observed file was not read), and one verdict line: "TOOLCHAIN HELD: n of n rows"
or "TOOLCHAIN FAILED: k of n rows failed". Exit 0 only when HELD, 1 when FAILED, 2 on a usage error or when the --json
file cannot be written. On FAILED a REVIEW line goes to standard error. --json OUT writes the rows, the digest, the
compared lines, the recorded values and the sha256 of both inputs (never their paths).

What a pass shows: the image's switch export, coqc, coqchk and python3 are byte for byte (by sha256) the recorded ones,
and its Coq and Python version lines and opam packages are the recorded ones, as the probe read them. What it does not
show: that the probe ran in the image the gates used, that the probe's commands report truly, that the record is right,
or anything about what the probe does not name (other apt packages, the C compiler, libgmp, the Coq libraries' files).

    python3 -B tools/ci/check_toolchain.py --observed OBSERVED --expected ci/mathkernel/EXPECTED-TOOLCHAIN.txt \\
        [--json OUT]
"""
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True

NAME = "TOOLCHAIN"
SCHEMA = "skuldd-toolchain/1"
COMPARED_KINDS = ("sha256", "coq-version", "python-version", "opam")
TWO_WORD_KINDS = ("opam", "env")
RECORD_KEYS = ("coqc-where", "coqchk-bytecode-default", "env COQPATH", "env COQLIB", "env OCAMLPATH",
               "env OCAMLRUNPARAM")
SWITCH_EXPORT = "/opt/mk-switch.export"
HASHED_TOOLS = ("coqc", "coqchk", "python3")
COMPILER_BASE = ("base-bigarray", "base-threads", "base-unix")
ROWS = (
    "expected toolchain file",
    "observed probe output",
    "tool and switch-export hashes",
    "Coq version line",
    "Python version line",
    "opam packages at their versions",
    "no unexpected opam package",
    "no unexpected key",
    "record-only keys present",
)


def show(value):
    """A value as a JSON string: quotes make a space at either end, or an empty value, visible."""
    return json.dumps(value, ensure_ascii=True)


def split_line(line):
    """(key, value) of one "<key> <value>" line, or None when the line is not one."""
    kind = line.split(" ", 1)[0]
    if kind == "":
        return None
    if kind == "sha256":
        parts = line.rsplit(" ", 1)
        if len(parts) != 2 or not parts[0].startswith("sha256 ") or parts[0] == "sha256 ":
            return None
        return parts[0], parts[1]
    if kind in TWO_WORD_KINDS:
        parts = line.split(" ", 2)
        if len(parts) != 3 or parts[1] == "":
            return None
        return parts[0] + " " + parts[1], parts[2]
    parts = line.split(" ", 1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def load(path, expected):
    """{"pairs", "lines", "problems", "sha256"} of one input; pairs is None when the file cannot be read.

    The expected file may hold blank lines and "#" comments, and only the kinds compared here; the observed file
    holds key lines only. A bad line or a repeated key is a problem and is left out of the pairs."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        return {"pairs": None, "lines": [], "sha256": None, "bom": False,
                "problems": ["it cannot be read (%s)" % (e.strerror or type(e).__name__)]}
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        return {"pairs": None, "lines": [], "sha256": digest, "bom": False,
                "problems": ["it is not UTF-8 (byte %d)" % e.start]}
    body = text.split("\n")
    if body and body[-1] == "":
        body.pop()
    pairs, lines, problems = {}, [], []
    for number, line in enumerate(body, 1):
        if expected and (line == "" or line.startswith("#")):
            continue
        if "\r" in line:
            problems.append("line %d has a carriage return" % number)
            continue
        kv = split_line(line)
        if kv is None:
            problems.append("line %d is not a key and a value: %s" % (number, show(line[:80])))
            continue
        key, value = kv
        if expected and key.split(" ", 1)[0] not in COMPARED_KINDS:
            problems.append("line %d: the kind %s is not one this check compares" % (number, show(key.split(" ")[0])))
            continue
        if key in pairs:
            problems.append("line %d repeats the key %s" % (number, show(key)))
            continue
        pairs[key] = value
        lines.append(line)
    return {"pairs": pairs, "lines": lines, "problems": problems, "sha256": digest, "bom": text.startswith("\ufeff")}


def kind_of(key):
    return key.split(" ", 1)[0]


def compare(exp, obs, keys):
    """Every difference between the expected and observed values of these keys, in key order."""
    diffs = []
    for key in sorted(keys):
        if key not in obs:
            diffs.append("%s: expected %s, not observed" % (key, show(exp[key])))
        elif obs[key] != exp[key]:
            diffs.append("%s: expected %s, observed %s" % (key, show(exp[key]), show(obs[key])))
    return diffs


def judge(observed_path, expected_path):
    """(rows, digest, compared lines, records, the two inputs as loaded)."""
    E = load(expected_path, expected=True)
    O = load(observed_path, expected=False)
    exp, obs = E["pairs"], O["pairs"]
    rows = []

    def row(ok, detail):
        rows.append((ROWS[len(rows)], bool(ok), detail))

    def missing():
        names = []
        if exp is None:
            names.append("the expected file was not read")
        if obs is None:
            names.append("the observed output was not read")
        return "not compared: " + " and ".join(names)

    if exp is None or E["problems"]:
        row(False, "; ".join(E["problems"]))
    elif not exp:
        row(False, "it holds no key")
    else:
        counts = {}
        for key in exp:
            counts[kind_of(key)] = counts.get(kind_of(key), 0) + 1
        row(True, "%d keys (%s), none twice, sha256 %s" % (
            len(exp), ", ".join("%d %s" % (counts.get(k, 0), k) for k in COMPARED_KINDS), E["sha256"]))

    if obs is None or O["problems"]:
        row(False, "; ".join(O["problems"]))
    elif O["bom"] or not obs:
        row(False, "; ".join(x for x in ("it begins with a byte-order mark" if O["bom"] else "",
                                         "it holds no key" if not obs else "") if x))
    else:
        row(True, "%d keys, each a key and a value, none twice, sha256 %s" % (len(obs), O["sha256"]))

    # tool and switch-export hashes
    if exp is None or obs is None:
        row(False, missing())
    else:
        keys = [k for k in exp if kind_of(k) == "sha256"]
        paths = [k.split(" ", 1)[1] for k in keys]
        absent = []
        if SWITCH_EXPORT not in paths:
            absent.append(SWITCH_EXPORT)
        for tool in HASHED_TOOLS:
            if not any(p.rsplit("/", 1)[-1] == tool for p in paths):
                absent.append(tool)
        diffs = ["the expected file names no sha256 of %s" % a for a in absent] + compare(exp, obs, keys)
        if diffs:
            row(False, "; ".join(diffs))
        else:
            row(True, "%d of %d equal: %s" % (len(keys), len(keys), ", ".join(sorted(paths))))

    # the two version lines
    for key in ("coq-version", "python-version"):
        if exp is None or obs is None:
            row(False, missing())
        elif key not in exp:
            row(False, "the expected file names no %s" % key)
        else:
            diffs = compare(exp, obs, [key])
            row(not diffs, "; ".join(diffs) if diffs else exp[key])

    # opam packages at their versions
    if exp is None or obs is None:
        row(False, missing())
    else:
        keys = [k for k in exp if kind_of(k) == "opam"]
        diffs = compare(exp, obs, keys) if keys else ["the expected file names no opam package"]
        row(not diffs, "; ".join(diffs) if diffs else "%d of %d at their versions" % (len(keys), len(keys)))

    # no unexpected opam package
    if exp is None or obs is None:
        row(False, missing())
    else:
        seen = sorted(k for k in obs if kind_of(k) == "opam")
        base = [k for k in seen if k not in exp and k.split(" ", 1)[1] in COMPILER_BASE and obs[k] == "base"]
        extra = [k for k in seen if k not in exp and k not in base]
        if extra:
            row(False, "not expected: " + "; ".join("%s %s" % (k, show(obs[k])) for k in extra))
        else:
            row(True, "%d observed: %d expected, %d compiler base packages at version base (%s)" % (
                len(seen), len(seen) - len(base), len(base), ", ".join(k.split(" ", 1)[1] for k in base) or "none"))

    # no unexpected key
    if exp is None or obs is None:
        row(False, missing())
    else:
        odd = sorted(k for k in obs if k not in exp and kind_of(k) != "opam" and k not in RECORD_KEYS)
        if odd:
            row(False, "not expected: " + "; ".join("%s %s" % (k, show(obs[k])) for k in odd))
        else:
            row(True, "none")

    # record-only keys present
    if obs is None:
        row(False, "not read: the observed output was not read")
    else:
        absent = [k for k in RECORD_KEYS if k not in obs]
        if absent:
            row(False, "not observed: " + ", ".join(absent))
        else:
            row(True, "; ".join("%s=%s" % (k, show(obs[k])) for k in RECORD_KEYS))

    assert len(rows) == len(ROWS)
    if obs is None:
        digest, compared = None, []
    else:
        compared = sorted((l for l in O["lines"] if split_line(l)[0] not in RECORD_KEYS),
                          key=lambda l: l.encode("utf-8"))
        digest = hashlib.sha256("".join(l + "\n" for l in compared).encode("utf-8")).hexdigest()
    records = {} if obs is None else {k: obs[k] for k in RECORD_KEYS if k in obs}
    return rows, digest, compared, records, E, O


def main(argv):
    try:
        sys.stdout.reconfigure(newline="\n")  # the same output bytes on Windows as on Linux
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(
        prog="check_toolchain.py", allow_abbrev=False, add_help=False,
        description="Compare toolchain_probe.sh's output with ci/mathkernel/EXPECTED-TOOLCHAIN.txt.")
    parser.add_argument("--observed", required=True, help="the probe's output")
    parser.add_argument("--expected", required=True, help="the expected toolchain file")
    parser.add_argument("--json", help="write the result here as JSON")
    args = parser.parse_args(argv)

    rows, digest, compared, records, E, O = judge(args.observed, args.expected)
    failed = sum(1 for _, ok, _ in rows if not ok)
    if failed:
        verdict = "%s FAILED: %d of %d rows failed" % (NAME, failed, len(rows))
    else:
        verdict = "%s HELD: %d of %d rows" % (NAME, len(rows), len(rows))
    if args.json:
        doc = {
            "schema": SCHEMA,
            "held": not failed,
            "verdict": verdict,
            "rows": [{"name": n, "ok": ok, "detail": d} for n, ok, d in rows],
            "digest": digest,
            "compared": compared,
            "records": records,
            "observed_sha256": O["sha256"],
            "expected_sha256": E["sha256"],
        }
        data = (json.dumps(doc, sort_keys=True, indent=1, ensure_ascii=True) + "\n").encode("utf-8")
        try:
            with open(args.json, "wb") as fh:
                fh.write(data)
        except OSError as e:
            print("REFUSED: the --json file cannot be written (%s)" % (e.strerror or type(e).__name__),
                  file=sys.stderr)
            return 2
    width = max(len(n) for n in ROWS)
    for n, ok, d in rows:
        print("  %s %s  %s" % (n.ljust(width), "ok" if ok else "FAIL", d))
    print("%s DIGEST %s" % (NAME, digest or "none"))
    print(verdict)
    sys.stdout.flush()
    if failed:
        print("REVIEW: the image's toolchain differs from ci/mathkernel/EXPECTED-TOOLCHAIN.txt or could not be "
              "compared. A new value enters that file only after review, with a new MK_ANCHOR_CI set by the owner.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
