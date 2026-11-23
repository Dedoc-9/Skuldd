# SPDX-License-Identifier: AGPL-3.0-only
"""The test of tools/ci/check_toolchain.py and tools/ci/toolchain_probe.sh (standard library only).

Inputs, built in a temporary folder: a copy of ci/mathkernel/EXPECTED-TOOLCHAIN.txt, and the honest twin, the lines
the probe prints as derived from the image job's output in CI run 44223174587 (image b058dd7c...): the lines that
followed its "image id:" line are held below as EXCERPT, timestamps stripped. That output holds no record-only key, so
the twin gives the six of them the value "not-in-saved-log" (they are recorded, never compared). Cases, each ok or FAIL:

  predictions name every plant         each plant below has one prediction line, and each prediction a plant
  predictions name the checker's rows  the file's rows R1 to R9 are the checker's rows, in its order
  honest twin              HELD, exit 0, 9 of 9 rows; the printed digest equals the JSON's and one computed here;
                           a second run prints the same bytes
  honest twin reversed     the same lines in reverse order: HELD, with the same digest
  plant <name>             one change to the twin or to the expected copy: FAILED, exit 1, and exactly the rows that
                           tools/ci/tests/PREDICTIONS-check_toolchain.txt names for it fail (read from that file, which
                           was frozen before the first run)
  usage: <how>             exit 2 and no verdict line
  probe with stub tools    toolchain_probe.sh run by sh (--sh SH, default the sh on PATH) with stub coqc, coqchk,
                           python3 and opam that print the excerpt's outputs: the version and opam lines equal the
                           twin's, each tool's sha256 is the stub's, the record-only lines are as the stub environment
                           sets them, and it exits 1 when /opt/mk-switch.export is absent (outside the image), else 0;
                           its output is then judged as the plant "probe-stub-judged"
  saved log excerpt        with --image-log LOG, the saved log of that job: EXCERPT equals the log's lines
  excerpt and record agree with --repo-data (the mode CI runs, where no saved log is): the twin's compared lines are
                           exactly the lines of ci/mathkernel/EXPECTED-TOOLCHAIN.txt, apart from the compiler's three
                           base-* packages, which the record leaves out; compared here by this test, apart from the
                           checker. With neither option, neither case runs, and a line says so.

  probe, a value with a line feed   the probe run again so, but with OCAMLRUNPARAM holding a line feed and then the
                           line "opam zarith 1.14", and an opam stub that lists no zarith: the probe prints the value
                           as "failed" (a value holding a line feed would print lines of its own, which the check would
                           read as keys), and its output is judged as the plant "probe-env-line-feed" (zarith absent).
                           It needs an sh that passes such a value on (Git Bash's sh does, MEASURED; dash, ARGUED)

The plants are named in tools/ci/tests/PREDICTIONS-check_toolchain.txt, PREDICTIONS-check_toolchain-2.txt,
PREDICTIONS-check_toolchain-3.txt and PREDICTIONS-check_toolchain-4.txt (later rounds, each frozen before its first
run); every plant is in one of them.

Last line: "TEST check_toolchain HELD: n of n cases" or "TEST check_toolchain FAILED: k of n cases failed"; exit 0 only
when HELD. What a pass shows: the checker holds on the twin and turns each planted difference red on exactly its
predicted rows; the probe's parsing and output form agree with the checker on the replayed outputs, under the shell
used. What it does not show: the probe run in the real image (no container here), its commands' real output beyond the
saved log, or any value of the record-only keys. With --repo-data, that EXCERPT is a real log's lines (the saved-log
mode shows that); only that it agrees with the tree's record.

    python3 -B tools/ci/tests/test_check_toolchain.py [--root ROOT] [--sh SH] [--image-log LOG | --repo-data]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

TEST = "check_toolchain"
ROW_COUNT = 9
IMAGE_ID_LINE = "image id: sha256:b058dd7c3e52381007f54f13adbb7931baaf214d0435cad192da8d353963a51a"
EXCERPT = (
    "The Coq Proof Assistant, version 8.20.1",
    "compiled with OCaml 4.14.2",
    "The OCaml toplevel, version 4.14.2",
    "Python 3.12.3",
    "[WARNING] Running as root is not recommended",
    "# Repository  # Url                                 # Switches(rank)",
    "default       https://opam.ocaml.org                <default> 4.14.2(2/2)",
    "rocq-released https://rocq-prover.org/opam/released 4.14.2(1/2)",
    "[WARNING] Running as root is not recommended",
    "# Packages matching: installed",
    "# Name                # Version",
    "base-bigarray         base",
    "base-threads          base",
    "base-unix             base",
    "conf-g++              1.0",
    "conf-gmp              5",
    "conf-linux-libc-dev   0",
    "conf-pkg-config       5",
    "coq                   8.20.1",
    "coq-core              8.20.1",
    "coq-flocq             4.2.1",
    "coq-stdlib            8.20.1",
    "coqide-server         8.20.1",
    "dune                  3.23.1",
    "ocaml                 4.14.2",
    "ocaml-base-compiler   4.14.2",
    "ocaml-config          2",
    "ocaml-options-vanilla 1",
    "ocamlfind             1.9.8",
    "zarith                1.14",
    "9016502df184573ee89e40f582217239c970877923dcfb8af4d0b5e4d6f0f4d7  /opt/mk-switch.export",
    "966d46938036faa64149bbbbe641c7d12898787819092b0387749519f64fd446  /opt/opam/4.14.2/bin/coqc",
    "72a15917d340d441373cf13cd3cebcc5ea94240afa6387ee6c735b82ff14ec3f  /opt/opam/4.14.2/bin/coqchk",
    "e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f  /usr/bin/python3",
)
RECORD_KEYS = ("coqc-where", "coqchk-bytecode-default", "env COQPATH", "env COQLIB", "env OCAMLPATH",
               "env OCAMLRUNPARAM")
NOT_IN_LOG = "not-in-saved-log"
EXPORT = "sha256 /opt/mk-switch.export"
COQC = "sha256 /opt/opam/4.14.2/bin/coqc"
TIMESTAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z ")
HASH_LINE = re.compile(r"([0-9a-f]{64})  (/\S+)")
VERDICT = re.compile(r"^TOOLCHAIN (HELD: (\d+) of (\d+) rows|FAILED: (\d+) of (\d+) rows failed)$")
DIGEST = re.compile(r"^TOOLCHAIN DIGEST ([0-9a-f]{64}|none)$")
STUB_WHERE = "stub-coqc-where"
STUB_BYTECODE = "-bytecode-compiler (yes|no)  stub usage line"


def twin_lines(excerpt=EXCERPT):
    """The lines toolchain_probe.sh would print in the image whose output the excerpt holds, in the probe's order."""
    out = []
    for line in excerpt:
        m = HASH_LINE.fullmatch(line)
        if m:
            out.append("sha256 %s %s" % (m.group(2), m.group(1)))
    out.append("coq-version " + excerpt[0])
    out.append("python-version " + next(l for l in excerpt if l.startswith("Python ")))
    start = next(i for i, l in enumerate(excerpt) if l.startswith("# Name"))
    for line in excerpt[start + 1:]:
        if HASH_LINE.fullmatch(line):
            break
        name, version = line.split()
        out.append("opam %s %s" % (name, version))
    out += ["%s %s" % (k, NOT_IN_LOG) for k in RECORD_KEYS]
    return out


def encode(lines):
    return ("".join(l + "\n" for l in lines)).encode("utf-8")


def digest_of(lines):
    """The digest computed here, apart from the checker: the non-record lines, sorted by bytes, each with a newline."""
    keep = [l for l in lines if not any(l.startswith(k + " ") for k in RECORD_KEYS)]
    keep.sort(key=lambda l: l.encode("utf-8"))
    return hashlib.sha256(encode(keep)).hexdigest()


def value_of(lines, key):
    hits = [l[len(key) + 1:] for l in lines if l.startswith(key + " ")]
    assert len(hits) == 1, (key, len(hits))
    return hits[0]


def replace(lines, key, value):
    out = [key + " " + value if l.startswith(key + " ") else l for l in lines]
    assert sum(1 for l in lines if l.startswith(key + " ")) == 1, key
    return out


def drop(lines, key):
    assert sum(1 for l in lines if l.startswith(key + " ")) == 1, key
    return [l for l in lines if not l.startswith(key + " ")]


def flip(hexvalue):
    """The same hex string with its last digit moved by one."""
    return hexvalue[:-1] + "0123456789abcdef"[(int(hexvalue[-1], 16) + 1) % 16]


def truncated(lines):
    """The output cut short inside the python3 hash line: the first three lines, then 32 characters, no newline."""
    head = [l for l in lines if l.startswith("sha256 ")]
    return encode(head[:3]) + head[3][:32].encode("utf-8")


# Each plant: (observed lines) and (expected bytes) -> (observed bytes or None for no file, expected bytes or None).
PLANTS = {
    "coqc-hash": lambda o, e: (encode(replace(o, COQC, flip(value_of(o, COQC)))), e),
    "switch-export-hash": lambda o, e: (encode(replace(o, EXPORT, flip(value_of(o, EXPORT)))), e),
    "missing-key": lambda o, e: (encode(drop(o, "python-version")), e),
    "extra-opam-package": lambda o, e: (encode(o + ["opam coq-interval 4.11.1"]), e),
    "opam-version-changed": lambda o, e: (encode(replace(o, "opam zarith", "1.15")), e),
    "coq-version-changed": lambda o, e: (
        encode(replace(o, "coq-version", "The Coq Proof Assistant, version 8.20.0")), e),
    "extra-base-package": lambda o, e: (encode(o + ["opam base-domains base"]), e),
    "base-package-version": lambda o, e: (encode(replace(o, "opam base-unix", "1.0")), e),
    "duplicate-key": lambda o, e: (encode(o + [COQC + " " + flip(value_of(o, COQC))]), e),
    "unknown-key": lambda o, e: (encode(o + ["sha256 /usr/local/bin/coqc " + value_of(o, COQC)]), e),
    "trailing-space": lambda o, e: (encode(replace(o, "opam coq-flocq", "4.2.1 ")), e),
    "carriage-return": lambda o, e: (
        encode(replace(o, "python-version", value_of(o, "python-version") + "\r")), e),
    "record-key-missing": lambda o, e: (encode(drop(o, "env OCAMLRUNPARAM")), e),
    "truncated-output": lambda o, e: (truncated(o), e),
    "observed-missing": lambda o, e: (None, e),
    "expected-missing": lambda o, e: (encode(o), None),
    "expected-no-hashes": lambda o, e: (
        encode(o), b"".join(l for l in e.splitlines(True) if not l.startswith(b"sha256 "))),
    "expected-unknown-kind": lambda o, e: (encode(o), e + b"coqc-where /opt/opam/4.14.2/lib/coq\n"),
    # the second round (PREDICTIONS-check_toolchain-2.txt)
    "observed-bom": lambda o, e: (b"\xef\xbb\xbf" + encode(o), e),
    "observed-empty": lambda o, e: (b"", e),
    # the third round (PREDICTIONS-check_toolchain-3.txt)
    "expected-no-keys": lambda o, e: (encode(o), b"".join(l for l in e.splitlines(True) if l.startswith(b"#"))),
}
PREDICTION_FILES = ("PREDICTIONS-check_toolchain.txt", "PREDICTIONS-check_toolchain-2.txt",
                    "PREDICTIONS-check_toolchain-3.txt", "PREDICTIONS-check_toolchain-4.txt")
BASE_PACKAGES = ("opam base-bigarray base", "opam base-threads base", "opam base-unix base")
STUB_PLANT = "probe-stub-judged"
LF_PLANT = "probe-env-line-feed"


def read_predictions(paths):
    """([row names in label order], {plant: set of row names}) from the predictions files, in order: "row R<n> =
    <name>" lines name the rows, "plant <name> | <input> | <change> | R<n>; R<n>" lines the plants; "#" lines are
    comments. A row is named once and a plant once, across the files."""
    text = ""
    for path in paths:
        with open(path, "rb") as fh:
            text += fh.read().decode("utf-8") + "\n"
    rows, plants = {}, {}
    for line in text.split("\n"):
        if line.startswith("row "):
            label, _, name = line[4:].partition(" = ")
            if not name or label in rows:
                raise ValueError("a bad or repeated row line")
            rows[label] = name
        elif line.startswith("plant "):
            fields = line[6:].split(" | ")
            if len(fields) != 4 or fields[0] in plants:
                raise ValueError("a bad or repeated plant line")
            labels = fields[3].split("; ")
            if any(label not in rows for label in labels):
                raise ValueError("a plant names a row the file does not")
            plants[fields[0]] = {rows[label] for label in labels}
        elif line and not line.startswith("#"):
            raise ValueError("a line that is not a row, a plant or a comment")
    return [rows[k] for k in sorted(rows, key=lambda k: int(k[1:]))], plants


class Run:
    def __init__(self, root, tmp):
        self.root, self.tmp, self.count = root, tmp, 0

    def checker(self, args):
        cmd = [sys.executable, "-B", str(self.root / "tools" / "ci" / "check_toolchain.py")] + args
        env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run(cmd, capture_output=True, env=env, timeout=120)
        return p.returncode, p.stdout, p.stderr

    def judge(self, observed, expected):
        """Write the inputs (None: no file) and run the checker with --json; (rc, stdout, json or None, problems)."""
        self.count += 1
        d = self.tmp / ("j%02d" % self.count)
        d.mkdir()
        obs, exp, out = d / "observed.txt", d / "expected.txt", d / "result.json"
        if observed is not None:
            obs.write_bytes(observed)
        if expected is not None:
            exp.write_bytes(expected)
        rc, stdout, stderr = self.checker(["--observed", str(obs), "--expected", str(exp), "--json", str(out)])
        problems = []
        try:
            text = stdout.decode("utf-8")
        except UnicodeDecodeError:
            return rc, "", None, ["its output is not UTF-8"]
        if "\r" in text:
            problems.append("its output holds a carriage return")
        lines = text.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        verdicts = [l for l in lines if VERDICT.match(l)]
        if len(verdicts) != 1 or not lines or lines[-1] != verdicts[0]:
            problems.append("not exactly one verdict line, last")
        if sum(1 for l in lines if DIGEST.match(l)) != 1:
            problems.append("not exactly one digest line")
        doc = None
        try:
            doc = json.loads(out.read_bytes().decode("utf-8"))
        except (OSError, ValueError) as e:
            problems.append("no JSON result (%s)" % type(e).__name__)
        if doc is not None:
            if doc.get("schema") != "skuldd-toolchain/1" or len(doc.get("rows", [])) != ROW_COUNT:
                problems.append("the JSON has another schema or not %d rows" % ROW_COUNT)
            if verdicts and doc.get("verdict") != verdicts[0]:
                problems.append("the JSON's verdict differs from the printed one")
            for r in doc.get("rows", []):
                hit = [l for l in lines if l.startswith("  " + r["name"] + " ")]
                status = hit[0][2 + len(r["name"]):].lstrip(" ").split(" ", 1)[0] if len(hit) == 1 else None
                if status != ("ok" if r["ok"] else "FAIL"):
                    problems.append("the printed row %r differs from the JSON's" % r["name"])
            printed = [DIGEST.match(l).group(1) for l in lines if DIGEST.match(l)]
            if printed and printed[0] != (doc.get("digest") or "none"):
                problems.append("the JSON's digest differs from the printed one")
        return rc, text, doc, problems


def failing(doc):
    return {r["name"] for r in doc["rows"] if not r["ok"]}


def case_plant(run, name, observed, expected, predicted):
    rc, text, doc, problems = run.judge(observed, expected)
    if doc is None or problems:
        return False, "; ".join(problems) or "no result"
    got = failing(doc)
    verdict = "TOOLCHAIN FAILED: %d of %d rows failed" % (len(predicted), ROW_COUNT)
    wrong = []
    if rc != 1:
        wrong.append("exit %d, not 1" % rc)
    if doc["verdict"] != verdict:
        wrong.append("verdict %r" % doc["verdict"])
    if got != predicted:
        wrong.append("failed %s, predicted %s" % (sorted(got), sorted(predicted)))
    if wrong:
        return False, "; ".join(wrong)
    return True, "FAILED as predicted: " + "; ".join(sorted(got))


def make_stubs(folder, without=()):
    """Stub coqc, coqchk, python3 and opam replaying the excerpt; each refuses arguments other than the probe's. The
    opam stub leaves out the packages named in without."""
    pk = EXCERPT.index("# Packages matching: installed")
    end = next(i for i, l in enumerate(EXCERPT) if HASH_LINE.fullmatch(l))
    listed = [l for l in EXCERPT[pk:end] if not l.split() or l.split()[0] not in without]
    stubs = {
        "coqc": ['#!/bin/sh', 'case "$*" in', '--version)', "cat <<'EOF'", EXCERPT[0], EXCERPT[1], 'EOF', ';;',
                 '-where) echo ' + STUB_WHERE + ' ;;',
                 '*) echo "stub coqc: unexpected arguments: $*" >&2; exit 2 ;;', 'esac'],
        "coqchk": ['#!/bin/sh', '[ "$*" = -help ] || { echo "stub coqchk: unexpected arguments" >&2; exit 2; }',
                   "echo 'Usage: coqchk <options> modules'",
                   "echo '  " + STUB_BYTECODE + "' >&2",
                   "echo '  -norec module  stub usage line'", 'exit 1'],
        "python3": ['#!/bin/sh', '[ "$*" = --version ] || { echo "stub python3: unexpected arguments" >&2; exit 2; }',
                    "echo '" + EXCERPT[3] + "'"],
        "opam": ['#!/bin/sh',
                 '[ "$*" = "list --installed --columns=name,version" ] || '
                 '{ echo "stub opam: unexpected arguments: $*" >&2; exit 2; }',
                 "echo '[WARNING] Running as root is not recommended' >&2",
                 "cat <<'EOF'"] + listed + ['EOF'],
    }
    folder.mkdir()
    for name, lines in stubs.items():
        path = folder / name
        path.write_bytes(encode(lines))
        path.chmod(0o755)
    return {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in stubs}


def case_probe(run, sh, twin):
    """(ok, detail, the probe's output bytes or None)."""
    if not sh:
        return False, "no sh found: give --sh", None
    stubdir = run.tmp / "stubs"
    hashes = make_stubs(stubdir)
    env = dict(os.environ)
    for k in list(env):
        if k.upper() in ("COQPATH", "COQLIB", "OCAMLPATH", "OCAMLRUNPARAM"):
            del env[k]
    env["OCAMLRUNPARAM"] = "b"
    env["PATH"] = str(stubdir) + os.pathsep + env.get("PATH", "")
    probe = run.root / "tools" / "ci" / "toolchain_probe.sh"
    try:
        # started in this test's temporary folder: sh is a program that is not Python, which tools/ci/read_audit.py
        # refuses to see started outside a new temporary folder
        p = subprocess.run([sh, probe.as_posix()], capture_output=True, env=env, timeout=120, cwd=str(run.tmp))
    except (OSError, subprocess.SubprocessError) as e:
        return False, "the probe did not run (%s)" % type(e).__name__, None
    try:
        lines = p.stdout.decode("utf-8").split("\n")
    except UnicodeDecodeError:
        return False, "its output is not UTF-8", None
    if lines[-1] != "":
        return False, "its output does not end with a newline", None
    lines.pop()
    shas = [l for l in lines if l.startswith("sha256 ")]
    wrong = []
    if len(shas) != 4 or lines[:4] != shas:
        return False, "not four sha256 lines first (%d)" % len(shas), None
    tools = {}
    for line, name in zip(shas[1:], ("coqc", "coqchk", "python3")):
        key, value = line.rsplit(" ", 1)
        path = key[len("sha256 "):]
        if path.rsplit("/", 1)[-1] != name:
            wrong.append("the %s hash line names another file" % name)
        tools[name] = (path.rsplit("/", 1)[0], value)
    dirs = {d for d, _ in tools.values()}
    if len(dirs) != 1:
        wrong.append("the three tools were not all found among the stubs")
    for name, (_, value) in tools.items():
        if value != hashes[name]:
            wrong.append("%s: the hash printed is not the stub's" % name)
    export = shas[0].rsplit(" ", 1)
    export_ok = export[0] == EXPORT and (export[1] == "failed" or re.fullmatch(r"[0-9a-f]{64}", export[1]))
    if not export_ok:
        wrong.append("the switch-export line is not as the probe prints it")
    want_rc = 1 if export[1] == "failed" else 0
    if p.returncode != want_rc:
        wrong.append("exit %d, not %d" % (p.returncode, want_rc))
    middle = [l for l in twin if not l.startswith("sha256 ") and not any(l.startswith(k + " ") for k in RECORD_KEYS)]
    if lines[4:4 + len(middle)] != middle:
        got = lines[4:4 + len(middle)]
        first = next((i for i, (a, b) in enumerate(zip(got, middle)) if a != b), min(len(got), len(middle)))
        wrong.append("the version and opam lines differ from the twin's at line %d" % (5 + first))
    records = ["coqc-where " + STUB_WHERE, "coqchk-bytecode-default " + STUB_BYTECODE, "env COQPATH unset",
               "env COQLIB unset", "env OCAMLPATH unset", "env OCAMLRUNPARAM b"]
    if lines[4 + len(middle):] != records:
        wrong.append("the record-only lines are not %s" % "; ".join(records))
    if wrong:
        return False, "; ".join(wrong), p.stdout
    return True, "%d lines; exit %d; version, opam and record lines as predicted; tool hashes the stubs'" % (
        len(lines), p.returncode), p.stdout


def case_probe_line_feed(run, sh):
    """(ok, detail, the probe's output bytes or None): the probe with an opam stub that lists no zarith and
    OCAMLRUNPARAM holding a line feed and then "opam zarith 1.14"; the value must be printed as "failed"."""
    if not sh:
        return False, "no sh found: give --sh", None
    stubdir = run.tmp / "stubs-lf"
    make_stubs(stubdir, without=("zarith",))
    env = dict(os.environ)
    for k in list(env):
        if k.upper() in ("COQPATH", "COQLIB", "OCAMLPATH", "OCAMLRUNPARAM"):
            del env[k]
    env["OCAMLRUNPARAM"] = "b\nopam zarith 1.14"
    env["PATH"] = str(stubdir) + os.pathsep + env.get("PATH", "")
    probe = run.root / "tools" / "ci" / "toolchain_probe.sh"
    try:
        # started in this test's temporary folder, as case_probe's run is
        p = subprocess.run([sh, probe.as_posix()], capture_output=True, env=env, timeout=120, cwd=str(run.tmp))
    except (OSError, subprocess.SubprocessError) as e:
        return False, "the probe did not run (%s)" % type(e).__name__, None
    try:
        lines = p.stdout.decode("utf-8").split("\n")
    except UnicodeDecodeError:
        return False, "its output is not UTF-8", None
    wrong = []
    if [l for l in lines if l.startswith("env OCAMLRUNPARAM ")] != ["env OCAMLRUNPARAM failed"]:
        wrong.append("OCAMLRUNPARAM is not printed as failed")
    if any(l.startswith("opam zarith") for l in lines):
        wrong.append("a zarith line is printed")
    if wrong:
        return False, "; ".join(wrong), p.stdout
    return True, "the value with a line feed printed as failed; no zarith line; exit %d" % p.returncode, p.stdout


def case_excerpt(log):
    try:
        with open(log, "rb") as fh:
            text = fh.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, "the log cannot be read (%s)" % type(e).__name__
    lines = [TIMESTAMP.sub("", l[:-1] if l.endswith("\r") else l) for l in text.split("\n")]
    starts = [i for i, l in enumerate(lines) if l.startswith("image id: ")]
    if len(starts) != 1 or lines[starts[0]] != IMAGE_ID_LINE:
        return False, "the log does not hold exactly the one image id line of run 44223174587"
    got = tuple(lines[starts[0] + 1:starts[0] + 1 + len(EXCERPT)])
    if got != EXCERPT:
        first = next(i for i, (a, b) in enumerate(zip(got + ("",) * len(EXCERPT), EXCERPT)) if a != b)
        return False, "the excerpt differs from the log at its line %d" % (first + 1)
    return True, "the %d lines after the image id line equal EXCERPT" % len(EXCERPT)


def case_record(expected, twin):
    """The twin's compared lines against the record's lines, compared here as sets of lines (not by the checker)."""
    if expected is None:
        return False, "ci/mathkernel/EXPECTED-TOOLCHAIN.txt cannot be read"
    try:
        lines = expected.decode("utf-8").split("\n")
    except UnicodeDecodeError:
        return False, "ci/mathkernel/EXPECTED-TOOLCHAIN.txt is not UTF-8"
    record = set(l for l in lines if l and not l.startswith("#"))
    mine = set(l for l in twin if not any(l.startswith(k + " ") for k in RECORD_KEYS) and l not in BASE_PACKAGES)
    only_record, only_twin = sorted(record - mine), sorted(mine - record)
    if only_record or only_twin or len(record) != sum(1 for l in lines if l and not l.startswith("#")):
        return False, "in the record only: %s; in the twin only: %s" % (only_record[:3] or "none",
                                                                        only_twin[:3] or "none")
    return True, "the twin's %d compared lines are the record's %d lines" % (len(mine), len(record))


def main(argv):
    try:
        sys.stdout.reconfigure(newline="\n")
    except (AttributeError, ValueError):
        pass
    here = Path(__file__).resolve()
    parser = argparse.ArgumentParser(prog="test_check_toolchain.py", allow_abbrev=False, add_help=False)
    parser.add_argument("--root", default=str(here.parents[3]))
    parser.add_argument("--sh", default=shutil.which("sh"))
    parser.add_argument("--image-log")
    parser.add_argument("--repo-data", action="store_true")
    args = parser.parse_args(argv)
    if args.image_log and args.repo_data:
        parser.error("give --image-log or --repo-data, not both")
    root = Path(args.root)
    results = []

    def case(name, ok, detail):
        results.append((name, ok, detail))

    try:
        legend, predictions = read_predictions([here.with_name(n) for n in PREDICTION_FILES])
    except (OSError, ValueError) as e:
        legend, predictions = None, None
        case("predictions read", False, "the predictions file cannot be read (%s: %s)" % (type(e).__name__, e))
    if predictions is not None:
        named = set(PLANTS) | {STUB_PLANT, LF_PLANT}
        case("predictions name every plant", set(predictions) == named,
             "%d plants, %d predictions; without a prediction: %s; without a plant: %s" % (
                 len(named), len(predictions), sorted(named - set(predictions)) or "none",
                 sorted(set(predictions) - named) or "none"))

    try:
        expected = (root / "ci" / "mathkernel" / "EXPECTED-TOOLCHAIN.txt").read_bytes()
    except OSError as e:
        print("  the expected file cannot be read (%s)" % type(e).__name__)
        expected = None
    twin = twin_lines()

    with tempfile.TemporaryDirectory() as t:
        run = Run(root, Path(t))
        if expected is None:
            case("expected file copied", False, "ci/mathkernel/EXPECTED-TOOLCHAIN.txt cannot be read")
        else:
            rc, text, doc, problems = run.judge(encode(twin), expected)
            again = run.judge(encode(twin), expected)
            want = digest_of(twin)
            wrong = list(problems)
            if rc != 0 or doc is None or doc.get("verdict") != "TOOLCHAIN HELD: %d of %d rows" % (ROW_COUNT,
                                                                                                ROW_COUNT):
                wrong.append("exit %d, verdict %r" % (rc, doc and doc.get("verdict")))
            elif doc.get("digest") != want or doc.get("held") is not True:
                wrong.append("digest %s, computed here %s" % (doc.get("digest"), want))
            if again[1] != text:
                wrong.append("a second run printed other bytes")
            case("honest twin", not wrong, "; ".join(wrong) or "HELD 9 of 9; digest %s equals the one computed here"
                 % want)
            names = [r["name"] for r in doc["rows"]] if doc is not None else None
            case("predictions name the checker's rows", legend is not None and legend == names,
                 "R1 to R%d are its rows, in order" % ROW_COUNT if legend == names else "they differ")

            rc, text, doc, problems = run.judge(encode(list(reversed(twin))), expected)
            ok = rc == 0 and doc is not None and not problems and doc.get("held") is True and doc["digest"] == want
            case("honest twin reversed", ok, "HELD, same digest" if ok else "exit %d; %s" % (rc, problems))

            for name in sorted(PLANTS):
                if predictions is None or name not in predictions:
                    case("plant " + name, False, "no prediction for it")
                    continue
                observed, exp = PLANTS[name](list(twin), expected)
                case("plant " + name, *case_plant(run, name, observed, exp, predictions[name]))

        for label, argv2 in (("usage: no arguments", []),
                             ("usage: an abbreviated option", ["--obs", "x", "--expected", "y"]),
                             ("usage: --help is not a pass", ["--help"])):
            rc, stdout, _ = run.checker(argv2)
            ok = rc == 2 and not any(VERDICT.match(l) for l in stdout.decode("utf-8", "replace").split("\n"))
            case(label, ok, "exit %d" % rc)

        ok, detail, output = case_probe(run, args.sh, twin)
        case("probe with stub tools", ok, detail)
        if predictions is not None and STUB_PLANT in predictions and expected is not None and output is not None:
            case("plant " + STUB_PLANT, *case_plant(run, STUB_PLANT, output, expected, predictions[STUB_PLANT]))
        else:
            case("plant " + STUB_PLANT, False, "not run: no probe output, prediction or expected file")
        ok, detail, output = case_probe_line_feed(run, args.sh)
        case("probe, a value with a line feed", ok, detail)
        if predictions is not None and LF_PLANT in predictions and expected is not None and output is not None:
            case("plant " + LF_PLANT, *case_plant(run, LF_PLANT, output, expected, predictions[LF_PLANT]))
        else:
            case("plant " + LF_PLANT, False, "not run: no probe output, prediction or expected file")

    if args.image_log:
        case("saved log excerpt", *case_excerpt(args.image_log))
    elif args.repo_data:
        ok, detail = case_record(expected, twin)
        planted_ok, _ = case_record(expected, replace(list(twin), "opam zarith", "1.15"))
        case("excerpt and record agree", ok and not planted_ok,
             detail + ("; a twin with one version changed does not agree" if not planted_ok
                       else "; a twin with one version changed AGREES: the comparison cannot fail"))
    else:
        print("  saved log excerpt: not run (no --image-log given); excerpt and record agree: not run (no --repo-data)")

    width = max(len(n) for n, _, _ in results)
    for name, ok, detail in results:
        print("  %s %s  %s" % (name.ljust(width), "ok" if ok else "FAIL", detail))
    failed = sum(1 for _, ok, _ in results if not ok)
    if failed:
        print("TEST %s FAILED: %d of %d cases failed" % (TEST, failed, len(results)))
        return 1
    print("TEST %s HELD: %d of %d cases" % (TEST, len(results), len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
