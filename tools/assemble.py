#!/usr/bin/env python3
# Assembles the core repository's working tree from its three sources (written by the assistant, 2026-11-17).
# Standard library only. Every path is an argument; the script holds no local path.
#
#   python -B tools/assemble.py --orlog REPO --orlog-commit SHA --verdandi REPO --verdandi-commit SHA
#                               --kernel WORKSPACE --top TOP_FILES_DIR --date YYYY-MM-DD --out NEW_EMPTY_DIR
#
# 1. orlog/ and verdandi/: every blob of the pinned commit's tree, written byte for byte as git stores it, each
#    blob's git object id recomputed and compared (so line-ending conversion of a checkout cannot leak in).
# 2. kernel/: the proof tier and its evidence, copied byte for byte from the workspace by the explicit rules below.
# 3. Root files: LICENSE (the Orlog blob, refused unless equal to the Verdandi blob), this script as tools/assemble.py,
#    and every file of --top; PROVENANCE.md is rendered from --top's PROVENANCE.template.md with the values found.
# 4. Every kernel freeze list (kernel/coq/<folder>/FROZEN4.txt) is checked against the copy; a mismatch refuses.
# 5. MANIFEST.<part>.txt for orlog, verdandi, kernel and root: "sha256  path" lines, sorted by path, LF.
# It refuses an output directory that exists and is not empty, and it writes nothing outside it.
import argparse, hashlib, os, re, subprocess, sys
sys.dont_write_bytecode = True

KERNEL_SKIP_DIRS = {'out4', 'build', 'libcache', '__pycache__', 'wd'}
KERNEL_SKIP_SUFFIXES = ('.vo', '.vos', '.vok', '.glob', '.aux', '.pyc', '.cache')
# (workspace-relative source, repository-relative destination); a directory is copied whole under the same skip rules
# The law statement draft, its sidecar, its printed terms and the T2 transcription of it (kernel/law/,
# kernel/evidence/t2/) are WITHHELD until the reviewer's blind twin exists (the owner's refinement T4): pass
# --with-law only after that.
LAW_EXTRA = [
    ('ext-work/sincos32-law/draftM/SINCOS32_LAW_Statement.v', 'kernel/law/sincos32law-candidate/SINCOS32_LAW_Statement.v'),
    ('ext-work/sincos32-law/LAW-DOES-NOT-SAY-2026-11-16.v2.md', 'kernel/law/sincos32law-candidate/LAW-DOES-NOT-SAY.md'),
    ('ext-work/sincos32-law/printed/M-printed-terms-run6.txt', 'kernel/law/sincos32law-candidate/printed-terms.txt'),
    ('ext-work/sincos32-law/t2-sweep/sweep_t2b.c', 'kernel/evidence/t2/sweep_t2b.c'),
    ('ext-work/sincos32-law/t2-sweep/run_t2b.sh', 'kernel/evidence/t2/run_t2b.sh'),
    ('ext-work/sincos32-law/t2-sweep/compare_fidelity.py', 'kernel/evidence/t2/compare_fidelity.py'),
    ('ext-work/sincos32-law/t2-sweep/PREMORTEM-T2-2026-11-16.md', 'kernel/evidence/t2/PREMORTEM-T2.md'),
    ('ext-work/sincos32-law/t2-sweep/check2-console.txt', 'kernel/evidence/t2/check2-console.txt'),
    ('ext-work/sincos32-law/t2-sweep/sweep2-console.txt', 'kernel/evidence/t2/sweep2-console.txt'),
]
KERNEL_EXTRA = [
    ('ext-work/harden-r4/harness/harness.py', 'kernel/hardening/harness/harness.py'),
    ('ext-work/harden-r4/harness/harness2.py', 'kernel/hardening/harness/harness2.py'),
    ('ext-work/harden-r4/harness/make_harness2.py', 'kernel/hardening/harness/make_harness2.py'),
    ('ext-work/harden-r4/harness/PREDICTIONS-harness2-2026-11-17.md', 'kernel/hardening/harness/PREDICTIONS-harness2.md'),
    ('ext-work/harden-r4/plants/gen_refute2.py', 'kernel/hardening/plants/gen_refute2.py'),
    ('ext-work/harden-r4/plants/make_gen_refute2.py', 'kernel/hardening/plants/make_gen_refute2.py'),
    ('ext-work/harden-r4/plants/runs/gen3-console.txt', 'kernel/hardening/plants/runs/gen3-console.txt'),
    ('ext-work/harden-r4/harness/runs', 'kernel/hardening/harness/runs'),
    ('ext-work/harden-r4/harness/canaries/c1-wrong-anchor-console.txt', 'kernel/hardening/harness/canaries/c1-wrong-anchor-console.txt'),
    ('ext-work/harden-r4/harness/canaries/c2-changed-byte-console.txt', 'kernel/hardening/harness/canaries/c2-changed-byte-console.txt'),
    ('ext-work/harden-r4/harness/canaries/c3-admitted-console.txt', 'kernel/hardening/harness/canaries/c3-admitted-console.txt'),
    ('ext-work/harden-r4/harness/canaries/c4-unlisted-import-console.txt', 'kernel/hardening/harness/canaries/c4-unlisted-import-console.txt'),
    ('ext-work/harden-r4/features', 'kernel/hardening/features'),
    ('ext-work/harden-r4/examples/Examples2.v', 'kernel/hardening/examples/Examples.v'),
    ('ext-work/harden-r4/examples/build_examples2.sh', 'kernel/hardening/examples/build_examples.sh'),
    ('ext-work/harden-r4/examples/runs/ex2-console.txt', 'kernel/hardening/examples/runs/ex2-console.txt'),
    ('ext-work/harden-r4/plants/PLANT-LABELS-2026-11-17.md', 'kernel/hardening/plants/PLANT-LABELS.md'),
    ('ext-work/harden-r4/plants/gen_refute.py', 'kernel/hardening/plants/gen_refute.py'),
    ('ext-work/harden-r4/plants/build_refute.sh', 'kernel/hardening/plants/build_refute.sh'),
    ('ext-work/harden-r4/plants/stage3', 'kernel/hardening/plants/stage3'),
    ('ext-work/harden-r4/plants/runs/refute4-console.txt', 'kernel/hardening/plants/runs/refute4-console.txt'),
    ('ext-work/harden-r4/big106', 'kernel/hardening/big106'),
    ('ext-work/harden-r4/r7-probes', 'kernel/hardening/r7-probes'),
    ('ext-work/sincos32-ieee/CORRECTIONS-2026-11-16.md', 'kernel/notes/CORRECTIONS-2026-11-16.md'),
    ('ext-work/core-repo-build/kernel-notes/LIMITATIONS.md', 'kernel/notes/LIMITATIONS.md'),
]

def sha256(b): return hashlib.sha256(b).hexdigest()
def git_blob_id(b): return hashlib.sha1(b'blob %d\x00' % len(b) + b).hexdigest()

def write(out, rel, data, manifest):
    p = os.path.join(out, *rel.split('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p): sys.exit('refused: %s written twice' % rel)
    with open(p, 'wb') as f: f.write(data)
    manifest.append((rel, sha256(data)))

def export_repo(repo, commit, prefix, out, manifest):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    tree = subprocess.run(['git', '-C', repo, 'rev-parse', commit + '^{tree}'], capture_output=True, env=env, check=True).stdout.decode().strip()
    ls = subprocess.run(['git', '-C', repo, 'ls-tree', '-r', '-z', '--full-tree', commit], capture_output=True, env=env, check=True).stdout
    entries = []
    for rec in ls.split(b'\x00'):
        if not rec: continue
        meta, path = rec.split(b'\t', 1)
        mode, typ, oid = meta.decode().split()
        if mode != '100644' or typ != 'blob': sys.exit('refused: %s has mode %s type %s' % (path, mode, typ))
        entries.append((path.decode('utf-8'), oid))
    cat = subprocess.Popen(['git', '-C', repo, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    for path, oid in entries:
        cat.stdin.write(oid.encode() + b'\n'); cat.stdin.flush()
        head = cat.stdout.readline().split()
        if len(head) != 3 or head[0].decode() != oid: sys.exit('refused: cat-file answered %r for %s' % (head, oid))
        data = cat.stdout.read(int(head[2])); cat.stdout.read(1)
        if git_blob_id(data) != oid: sys.exit('refused: blob %s of %s does not hash to its id' % (oid, path))
        write(out, prefix + '/' + path, data, manifest)
    cat.stdin.close(); cat.wait()
    return tree, len(entries)

def copy_tree(src, dst_rel, out, manifest):
    n = 0
    for dp, dn, fn in os.walk(src):
        dn[:] = sorted(d for d in dn if d not in KERNEL_SKIP_DIRS)
        for f in sorted(fn):
            if f.endswith(KERNEL_SKIP_SUFFIXES): continue
            rel = os.path.relpath(os.path.join(dp, f), src).replace(os.sep, '/')
            with open(os.path.join(dp, f), 'rb') as h: data = h.read()
            write(out, dst_rel + '/' + rel, data, manifest); n += 1
    return n

def check_freeze_lists(out):
    coq = os.path.join(out, 'kernel', 'coq'); lists = entries = 0
    for d in sorted(os.listdir(coq)):
        lst = os.path.join(coq, d, 'FROZEN4.txt')
        if not os.path.isfile(lst): continue
        lists += 1
        for line in open(lst, encoding='ascii').read().splitlines():
            m = re.fullmatch(r'([0-9a-f]{64})  (\S+)', line)
            if not m: continue
            entries += 1
            p = os.path.join(coq, *m.group(2).split('/'))
            got = sha256(open(p, 'rb').read()) if os.path.isfile(p) else 'MISSING'
            if got != m.group(1): sys.exit('refused: freeze list %s names %s with %s, the copy has %s' % (d, m.group(2), m.group(1)[:16], got[:16]))
    return lists, entries

def main():
    ap = argparse.ArgumentParser()
    for k in ('orlog', 'orlog-commit', 'verdandi', 'verdandi-commit', 'kernel', 'top', 'date', 'out'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--with-law', action='store_true', help='include the law draft and its T2 transcription (only after the blind twin exists)')
    a = ap.parse_args()
    if os.path.exists(a.out) and os.listdir(a.out): sys.exit('refused: %s exists and is not empty' % a.out)
    os.makedirs(a.out, exist_ok=True)
    parts, info = {}, {'date': a.date}
    for name, repo, commit in (('orlog', a.orlog, a.orlog_commit), ('verdandi', a.verdandi, a.verdandi_commit)):
        m = []; tree, n = export_repo(repo, commit, name, a.out, m); parts[name] = m
        info.update({name + '_commit': commit, name + '_tree': tree, name + '_files': '{:,}'.format(n)})
    m = []
    n = copy_tree(os.path.join(a.kernel, 'mkf-ext'), 'kernel/coq', a.out, m)
    for src, dst in KERNEL_EXTRA + (LAW_EXTRA if a.with_law else []):
        s = os.path.join(a.kernel, *src.split('/'))
        if os.path.isdir(s): n += copy_tree(s, dst, a.out, m)
        else:
            with open(s, 'rb') as h: write(a.out, dst, h.read(), m); n += 1
    parts['kernel'] = m; info['kernel_files'] = '{:,}'.format(n)
    lists, entries = check_freeze_lists(a.out); info.update({'freeze_lists': str(lists), 'freeze_entries': '{:,}'.format(entries)})
    root = []
    lic = open(os.path.join(a.out, 'orlog', 'LICENSE'), 'rb').read()
    if lic != open(os.path.join(a.out, 'verdandi', 'LICENSE'), 'rb').read(): sys.exit('refused: the two LICENSE blobs differ')
    write(a.out, 'LICENSE', lic, root)
    with open(os.path.abspath(__file__), 'rb') as h: write(a.out, 'tools/assemble.py', h.read(), root)
    template = None
    for dp, dn, fn in os.walk(a.top):
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), a.top).replace(os.sep, '/')
            with open(os.path.join(dp, f), 'rb') as h: data = h.read()
            if rel == 'PROVENANCE.template.md': template = data.decode('utf-8'); continue
            write(a.out, rel, data, root)
    if template is None: sys.exit('refused: no PROVENANCE.template.md in --top')
    for name in ('orlog', 'verdandi', 'kernel'):
        text = ''.join('%s  %s\n' % (h, r) for r, h in sorted(parts[name]))
        with open(os.path.join(a.out, 'MANIFEST.%s.txt' % name), 'w', encoding='utf-8', newline='\n') as f: f.write(text)
        info[name + '_manifest'] = sha256(text.encode('utf-8'))
    info['root_files'] = str(len(root) + 1)
    root_text_wo = ''.join('%s  %s\n' % (h, r) for r, h in sorted(root))
    # PROVENANCE.md cannot hold its own hash: the root manifest covers every root file but PROVENANCE.md and itself.
    info['root_manifest'] = sha256(root_text_wo.encode('utf-8')) + ' (all root files but PROVENANCE.md)'
    prov = template
    for k, v in info.items(): prov = prov.replace('@@%s@@' % k, v)
    if '@@' in prov: sys.exit('refused: an unfilled token in PROVENANCE.template.md')
    write(a.out, 'PROVENANCE.md', prov.encode('utf-8'), [])
    with open(os.path.join(a.out, 'MANIFEST.root.txt'), 'w', encoding='utf-8', newline='\n') as f: f.write(root_text_wo)
    for name in ('orlog', 'verdandi', 'kernel'):
        print('%-9s %s files; manifest sha256 %s' % (name, info[name + '_files'], info[name + '_manifest']))
    print('root      %d files; manifest sha256 %s' % (len(root), info['root_manifest']))
    print('freeze lists checked: %s lists, %s entries' % (lists, entries))
    print('ASSEMBLED: %d files' % (sum(len(v) for v in parts.values()) + len(root) + 1))

if __name__ == '__main__':
    main()
