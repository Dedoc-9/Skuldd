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
  P1-P5  plants on the same reading, in memory: a changed file left unlisted, a manifest line altered, an added file
      left unlisted, a manifest's own sha256 missing from PROVENANCE.md, a listed file copied to an unlisted path;
      each must turn its row red

    python -B tools/check_manifests.py [ROOT]          (ROOT: the tree's top folder; default: this file's parent's)

Last line: "MANIFESTS RECONCILED: n of n rows" or "MANIFESTS NOT RECONCILED: k of n rows failed".
What it does not show: that a listed change was ruled or is right (CHANGES-AFTER-IMPORT.md is read, not judged); git
history; anything about the import's sources beyond the manifests' own hashes.
"""
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
PARTS = ("orlog", "verdandi", "kernel", "root")
SELF = {"PROVENANCE.md", "CHANGES-AFTER-IMPORT.md"} | {"MANIFEST.%s.txt" % p for p in PARTS}
HEX = re.compile(r"^[0-9a-f]{64}$")


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


def judge(lines, own, provenance, changes, present):
    """The three rows on given inputs (the honest run and the plants use the same function)."""
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
    plants = [("P1 a changed file left unlisted", "M2", judge(lines, own, provenance, changes, p_changed)),
              ("P2 a manifest line altered", "M2", judge(altered, own, provenance, changes, present)),
              ("P3 an added file left unlisted", "M3", judge(lines, own, provenance, changes, p_added)),
              ("P4 a manifest PROVENANCE.md does not name", "M1", judge(lines, own_gone, provenance, changes, present)),
              ("P5 a listed file copied to an unlisted path", "M3", judge(lines, own, provenance, changes, p_copied))]
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
