# SPDX-License-Identifier: AGPL-3.0-only
"""Reconcile the import's manifests with the tree as it stands (standard library only; no git history needed).

The four manifests (MANIFEST.orlog.txt, MANIFEST.verdandi.txt, MANIFEST.kernel.txt, MANIFEST.root.txt) describe the
import and are never rewritten; every later change is listed in CHANGES-AFTER-IMPORT.md with its sha256 before and
after (PROVENANCE.md). So a file that differs from its manifest line is a defect only when CHANGES-AFTER-IMPORT.md does
not account for it. Rows, each PASS or FAIL:

  M1  every manifest line is "64 hex digits, two spaces, a path", no path twice, and each manifest's own sha256
      appears in PROVENANCE.md
  M2  every file a manifest lists is unchanged, or CHANGES-AFTER-IMPORT.md holds both its manifest sha256 (before)
      and, when the file is still there, its present sha256 (after); a removed file's manifest sha256 is there
      (each hash anywhere in the file: a removed record's path is written with `<host>` there)
  M3  every file present but in no manifest (beside the manifests, PROVENANCE.md and CHANGES-AFTER-IMPORT.md) has its
      present sha256 on a line of CHANGES-AFTER-IMPORT.md that also names its path in backticks
  M4  (ruling SY-2) every file of orlog/ and verdandi/ that differs from its pin has a reason: the pin is the
      manifest with the RE-PIN rows of CHANGES-AFTER-IMPORT.md's "## Drift classification" sections laid over it in
      order, and the last row naming the file is "SKULDD-ONLY BY RULING <id>" or "SENT BACK <route>" with the pin's
      sha256 (or "absent") before and the file's (or "removed") after; every table line in those sections parses
      (the grammar of tools/ci/drift.py, which also holds the RE-PIN rows to the original's commits)
  P1-P8  plants on the same reading, in memory: a changed file left unlisted, a manifest line altered, an added file
      left unlisted, a manifest's own sha256 missing from PROVENANCE.md, a listed file copied to an unlisted path, a
      copy's file changed and listed by its hashes but with no classification row, a copy's file changed with a
      classification row naming other bytes, a classification line that does not parse; each must turn its row red

    python -B tools/check_manifests.py [ROOT]          (ROOT: the tree's top folder; default: this file's parent's)

Last line: "MANIFESTS RECONCILED: n of n rows" or "MANIFESTS NOT RECONCILED: k of n rows failed".
What it does not show: that a listed change was ruled or is right (CHANGES-AFTER-IMPORT.md is read, not judged); git
history; anything about the import's sources beyond the manifests' own hashes; that a RE-PIN row's bytes are the
original's at that commit, or that the original has not moved (tools/ci/drift.py, with a clone of the original).
A message names a copy's file only when the file is in the tree: a removed file is named by its pinned sha256.
"""
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
PARTS = ("orlog", "verdandi", "kernel", "root")
SELF = {"PROVENANCE.md", "CHANGES-AFTER-IMPORT.md"} | {"MANIFEST.%s.txt" % p for p in PARTS}
HEX = re.compile(r"^[0-9a-f]{64}$")
COPIES = ("orlog", "verdandi")
# the classification grammar, the same as tools/ci/drift.py's (a change to one is a change to both)
SECTION = re.compile(r"^## Drift classification\b")
HEADING = re.compile(r"^#{1,6} ")
ROW = re.compile(r"^\| `((?:orlog|verdandi)/[^`|]+)` \| (absent|[0-9a-f]{64}) \| (removed|[0-9a-f]{64}) \| "
                 r"([^|]*[^| ]) \|$")
HEADER = re.compile(r"^\| File \| sha256 before \| sha256 after \| Class \|$")
SEPARATOR = re.compile(r"^\|(?: ?:?-{3,}:? ?\|){4}$")
RULING_ID = r"[A-Z][A-Z0-9]*(?:-[0-9]+)?(?: \([a-z0-9]+\))*"
CLASSES = (
    ("RE-PIN", re.compile(r"RE-PIN ([0-9a-f]{40})")),
    ("SKULDD-ONLY", re.compile(r"SKULDD-ONLY BY RULING (%s)" % RULING_ID)),
    ("SENT BACK", re.compile(r"SENT BACK (?:(?:Orlog|\u00d8rl\u01ebg) pull request #[1-9][0-9]*|"
                             r"(?:Verdandi|Ver\u00f0andi) patch [A-Za-z0-9][A-Za-z0-9._-]*\.patch)")),
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tree_files(root):
    """{path: sha256} of every file under root, .git and build folders left out."""
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "out4", "libcache", "build", "__pycache__")]
        for f in fn:
            p = os.path.join(dp, f)
            with open(p, "rb") as fh:
                out[os.path.relpath(p, root).replace(os.sep, "/")] = sha(fh.read())
    return out


def read_manifests(root):
    """({part: [(sha, path)]}, problems, {part: manifest sha256})."""
    lines, problems, own = {}, [], {}
    for part in PARTS:
        name = "MANIFEST.%s.txt" % part
        with open(os.path.join(root, name), "rb") as fh:
            raw = fh.read()
        own[part] = sha(raw)
        rows = []
        for n, ln in enumerate(raw.decode("utf-8").split("\n"), 1):
            if not ln.strip():
                continue
            h, sep, path = ln.partition("  ")
            if not sep or not HEX.match(h) or not path:
                problems.append("%s line %d is not '64 hex, two spaces, a path'" % (name, n))
                continue
            rows.append((h, path))
        seen = set()
        for h, path in rows:
            if path in seen:
                problems.append("%s lists %s twice" % (name, path))
            seen.add(path)
        lines[part] = rows
    return lines, problems, own


def pattern(path):
    """A row's path as a pattern: <host> stands for one path segment's part."""
    return re.compile("[^/]+".join(re.escape(x) for x in path.split("<host>")))


def classification(changes):
    """(rows, problems): the rows [(line, path, before, after, kind)] of the "## Drift classification" sections."""
    rows, problems, inside = [], [], False
    for n, line in enumerate(changes.split("\n"), 1):
        line = line.rstrip("\r")
        if HEADING.match(line):
            inside = bool(SECTION.match(line))
            continue
        if not inside or not line.startswith("|") or HEADER.match(line) or SEPARATOR.match(line):
            continue
        m = ROW.match(line)
        kind = next((k for k, rx in CLASSES if m and rx.fullmatch(m.group(4))), None)
        if not m or kind is None:
            problems.append("CHANGES-AFTER-IMPORT.md line %d is not a classification row" % n)
            continue
        path, before, after, cls = m.groups()
        if kind == "SENT BACK" and (("patch" in cls) != path.startswith("verdandi/")):
            problems.append("CHANGES-AFTER-IMPORT.md line %d sends a file back by the other repository's route" % n)
            continue
        if "<host>" in path and after != "removed":
            problems.append("CHANGES-AFTER-IMPORT.md line %d writes <host> in a file that is still here" % n)
            continue
        rows.append((n, path, before, after, kind))
    return rows, problems


def m4(lines, changes, present):
    """Row M4: every file of the copies that differs from its pin has, as the last row naming it, its reason."""
    rows, p4 = classification(changes)
    differ = 0
    for part in COPIES:
        pin = {path: h for h, path in lines.get(part, [])}
        for n, path, before, after, kind in rows:
            if kind != "RE-PIN" or not path.startswith(part + "/"):
                continue
            for p in ([q for q in set(pin) | set(present) if pattern(path).fullmatch(q)] if "<host>" in path
                      else [path]):
                if after == "removed":
                    pin.pop(p, None)
                else:
                    pin[p] = after
        here = {p: h for p, h in present.items() if p.startswith(part + "/")}
        for p in sorted(set(pin) | set(here)):
            before, after = pin.get(p, "absent"), here.get(p, "removed")
            if before == after:
                continue
            differ += 1
            last = None
            for r in rows:
                if r[4] != "RE-PIN" and pattern(r[1]).fullmatch(p):
                    last = r
            if not (last and last[2] == before and last[3] == after):
                p4.append("%s differs from its pin and %s" % (
                    p if p in here else "a removed file (pinned sha256 %s)" % before[:16],
                    "its last classification row (line %d) names other bytes" % last[0] if last else
                    "no classification row gives its reason"))
    return ("M4", not p4, p4 or ["%d file(s) of orlog/ and verdandi/ differ from their pin, each with its reason"
                                 % differ])


def judge(lines, own, provenance, changes, present):
    """The four rows on given inputs (the honest run and the plants use the same function)."""
    rows = []
    p1 = [("PROVENANCE.md does not give %s's sha256 %s" % ("MANIFEST.%s.txt" % part, h[:16]))
          for part, h in own.items() if h not in provenance]
    rows.append(("M1", not p1, p1))
    listed = set()
    p2, unchanged, accounted, removed = [], 0, 0, 0
    for part, rows_ in lines.items():
        for h, path in rows_:
            listed.add(path)
            now = present.get(path)
            if now == h:
                unchanged += 1
            elif now is None:
                if h in changes:
                    removed += 1
                else:
                    p2.append("%s is gone and CHANGES-AFTER-IMPORT.md does not list its sha256 %s" % (path, h[:16]))
            elif h in changes and now in changes:
                accounted += 1
            else:
                p2.append("%s differs from its manifest (%s -> %s) and CHANGES-AFTER-IMPORT.md does not hold %s" % (
                    path, h[:12], now[:12], "both hashes" if h not in changes and now not in changes else
                    ("the before hash" if h not in changes else "the present hash")))
    rows.append(("M2", not p2, p2 or ["%d unchanged, %d changed and listed, %d removed and listed" % (
        unchanged, accounted, removed)]))
    extra = sorted(p for p in present if p not in listed and p not in SELF)
    change_lines = changes.split("\n")
    p3 = ["%s is in no manifest and no line of CHANGES-AFTER-IMPORT.md names it with its sha256 %s" % (
          p, present[p][:16]) for p in extra
          if not any(present[p] in line and ("`%s`" % p) in line for line in change_lines)]
    rows.append(("M3", not p3, p3 or ["%d added file(s), each listed with its path and sha256" % len(extra)]))
    rows.append(m4(lines, changes, present))
    return rows


def main(argv):
    root = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lines, problems, own = read_manifests(root)
    with open(os.path.join(root, "PROVENANCE.md"), encoding="utf-8") as fh:
        provenance = fh.read()
    with open(os.path.join(root, "CHANGES-AFTER-IMPORT.md"), encoding="utf-8") as fh:
        changes = fh.read()
    present = tree_files(root)
    rows = judge(lines, own, provenance, changes, present)
    if problems:
        rows[0] = ("M1", False, problems + rows[0][2])
    # plants, in memory: each must turn its row red
    changed = next(p for part in lines.values() for h, p in part if present.get(p) == h)
    p_changed = dict(present, **{changed: sha(b"planted")})
    altered = {k: list(v) for k, v in lines.items()}
    h0, path0 = altered["root"][0]
    altered["root"][0] = (sha(b"another"), path0)
    p_added = dict(present, **{"planted/new-file.txt": sha(b"planted new")})
    own_gone = dict(own, root=sha(b"a manifest PROVENANCE.md does not name"))
    listed_paths = {q for part in lines.values() for _, q in part}
    extra_now = sorted(p for p in present if p not in listed_paths and p not in SELF)
    p_copied = dict(present, **{"planted/copy-of-a-listed-file": present[extra_now[0] if extra_now else changed]})
    # P6-P8 (M4): a copy's file that equals its manifest line, changed in memory and listed by both hashes
    copy_file = next(p for part in COPIES for h, p in lines[part] if present.get(p) == h)
    old_h, new_h = present[copy_file], sha(b"planted copy change")
    p_copy = dict(present, **{copy_file: new_h})
    c_listed = changes + "\n%s %s\n" % (old_h, new_h)
    c_other = c_listed + ("\n## Drift classification (plant)\n\n| File | sha256 before | sha256 after | Class |\n"
                          "|---|---|---|---|\n| `%s` | %s | %s | SKULDD-ONLY BY RULING C2 (b) |\n"
                          % (copy_file, old_h, sha(b"other bytes")))
    c_bad = changes + ("\n## Drift classification (plant)\n\n| File | sha256 before | sha256 after | Class |\n"
                       "|---|---|---|---|\n| `%s` | %s | %s | SKULDD ONLY C2 |\n" % (copy_file, old_h, old_h))
    plants = [("P1 a changed file left unlisted", "M2", judge(lines, own, provenance, changes, p_changed)),
              ("P2 a manifest line altered", "M2", judge(altered, own, provenance, changes, present)),
              ("P3 an added file left unlisted", "M3", judge(lines, own, provenance, changes, p_added)),
              ("P4 a manifest PROVENANCE.md does not name", "M1", judge(lines, own_gone, provenance, changes, present)),
              ("P5 a listed file copied to an unlisted path", "M3", judge(lines, own, provenance, changes, p_copied)),
              ("P6 a copy's file changed, listed, with no reason", "M4", judge(lines, own, provenance, c_listed,
                                                                                p_copy)),
              ("P7 a copy's file changed, its row naming other bytes", "M4", judge(lines, own, provenance, c_other,
                                                                                    p_copy)),
              ("P8 a classification line that does not parse", "M4", judge(lines, own, provenance, c_bad,
                                                                            present))]
    for name, key, got in plants:
        red = not dict((r[0], r[1]) for r in got)[key]
        rows.append((name, red, ["row %s %s" % (key, "turned red: CAUGHT" if red else "stayed green: NOT CAUGHT")]))
    for name, ok, notes in rows:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (": " + "; ".join(notes[:6])) if notes else ""))
    bad = sum(1 for r in rows if not r[1])
    print("MANIFESTS RECONCILED: %d of %d rows" % (len(rows), len(rows)) if not bad else
          "MANIFESTS NOT RECONCILED: %d of %d rows failed" % (bad, len(rows)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
