# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_workflow_guards.py: the guards the two MathKernel workflows (mathkernel-linux.yml and
# integrity.yml; the third, drift.yml, runs none) run inline (the shell and Python of their
# run: blocks), cut from the workflow text by step name and run under bash on honest inputs and on plants. Standard
# library only (Python 3.12 or later). It needs bash with grep, sed, tr, head, tee, wc and cat on the PATH, and, for
# the fpenv cases, /usr/bin/cat, grep, ls, mkdir, sort, tail and tee at exactly those paths (their wrappers exec
# them) and /bin/bash (the wrappers' first line); GitHub's Ubuntu runners and Git Bash have them there. It writes only
# in a temporary folder, which it removes.
#
#   python3 -B tools/ci/tests/test_workflow_guards.py [--local] [--bash BASH]
#
# Each case cuts one step's run: block from .github/workflows/mathkernel-linux.yml or integrity.yml by its step name,
# writes it to a file and runs it as GitHub runs a step that names no shell ("bash -e <file>"), in a temporary
# workspace that holds copies of the files the step reads, with RUNNER_TEMP, GITHUB_OUTPUT and GITHUB_WORKSPACE set
# there and the workflow's own top-level env. The one edit to a block: the folder /tmp/mk-image becomes a temporary
# folder. Stand-ins first on the PATH replace docker (it prints the build output, image id, probe output or gate
# console the case plants, and exits as planted), git (ls-files prints the case's list of tracked files) and python3
# (the inventory call copies the case's planted matrix and exits as planted; a feature row exits 1 for the planted row
# and list, else 0; every other call runs this interpreter). The honest inputs come from the tree: the gate matrix
# tools/ci/inventory.py writes for it, the sha256 of each folder's FROZEN4.txt as its anchor, kernel/coq/ANCHORS.md,
# the base image the Dockerfile pins, a probe output built from ci/mathkernel/EXPECTED-TOOLCHAIN.txt, and the toolchain
# digest tools/ci/check_toolchain.py prints for it.
#
# Cases, one line each, held to tools/ci/tests/PREDICTIONS-workflow_guards.txt, PREDICTIONS-workflow_guards-2.txt,
# PREDICTIONS-workflow_guards-3.txt (the build step's base line in BuildKit's padded and stage-named forms, after
# the fifth review), PREDICTIONS-workflow_guards-4.txt (the image step's FROM count as Docker reads FROM, and its
# refusals of a parser directive and of a line continued onto one that does not start with a blank, after the sixth)
# and PREDICTIONS-workflow_guards-5.txt (the image step's refusals of a byte outside printable ASCII, a blank and a
# tab, of a first line starting with "#!" or "//", of a parser directive's form on any line, and of a comment or blank
# line inside a continued instruction, after the seventh) and PREDICTIONS-workflow_guards-6.txt (the image step's FROM
# count before a line continuation or the line's end, and its byte rule reading the file as text, so a NUL byte is
# refused, after the eighth) and PREDICTIONS-workflow_guards-7.txt (the sweep job's step, the verdict's reading of
# each sweep leg's evidence and the sweep job's legs, ruling S280-13 (a)) and PREDICTIONS-workflow_guards-8.txt (the
# verdict job's needs: list and its first step's want list; each frozen before its first run): the exit
# code, and where
# the prediction names them, a word of
# the step's error output, a whole line of it, a text of its output, the number of lines it wrote to GITHUB_OUTPUT, a
# value written there, the base image it recorded, or the fpenv evidence it wrote.
#   steps        every step these cases run is in the workflow text, once, with a run: block; steps-plant: the same
#                check on a copy of mathkernel-linux.yml with one step renamed names that step as missing. The steps
#                are eighteen, every step of the two workflows with an inline check: the fpenv job's and the sweep
#                job's (each one's compiler search, run with a PATH of one folder that holds only what the case puts
#                there, and its check of the verdict line it keeps) and the verdict job's reading of each fpenv leg's
#                and each sweep leg's evidence among them
#   legs         the fpenv job's matrix runners are the legs the verdict reads; legs-plant: a third runner added
#   sweep-legs   the sweep job's matrix runners are the fpenv job's, and the legs and machines the verdict's sweep
#                step reads; sweep-legs-plant: a third runner added to the sweep job's matrix alone
#   needs-list   the verdict job's needs: list, sorted, is the want list its first step compares the jobs with;
#                needs-list-plant: a job added to the needs: list; needs-list-plant2: sweep taken from the want list
#   k, m, b, i, d, t, a, r, l, g, f, e, v, n, p, w, s, y   the cases of one step each (the predictions files say
#                which)
# A probe first asks whether this bash keeps a carriage return before the final newline of a command substitution
# (bash on Linux keeps it; Git Bash drops it); it runs "bash -c" in the test's own temporary folder, where the read
# audit (tools/ci/read_audit.py), which refuses a shell given a command, does not judge it. The cases the
# predictions mark "cr" plant such a value. In the CI form (no option) every case runs, these too, and where the CR is
# dropped they fail. Only with --local, and only when the
# probe says the CR is dropped, each of them prints "NOT RUN" with that reason and is not counted.
# What a pass shows: on this bash, each guard cut from the workflow text passes its honest inputs and refuses each of
# its plants, and every step it names is in the text. What it does not show: GitHub's reading of the YAML and of its
# expressions, the actions, docker, the image or the gate (stand-ins replace them); a step this test does not name.
# Last line: "TEST workflow_guards HELD: n of n cases" (exit 0) or "TEST workflow_guards FAILED: k of n cases failed"
# (exit 1); exit 2 on a usage error.
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PRED = (os.path.join(HERE, 'PREDICTIONS-workflow_guards.txt'), os.path.join(HERE, 'PREDICTIONS-workflow_guards-2.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-3.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-4.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-5.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-6.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-7.txt'),
        os.path.join(HERE, 'PREDICTIONS-workflow_guards-8.txt'))
WF = {'mk': '.github/workflows/mathkernel-linux.yml', 'in': '.github/workflows/integrity.yml'}
STEPS = {
    'pyc-mk': ('mk', 'No compiled Python is tracked'),
    'pyc-in': ('in', 'No compiled Python is tracked'),
    'matrix': ('mk', 'The inventory, found from the tree, and the gate matrix'),
    'build': ('mk', 'Build and save the image (only when the cache has none for this Dockerfile in this scope)'),
    'image': ('mk', 'Say what the image holds; its base is the digest the Dockerfile pins'),
    'toolchain': ('mk', 'The toolchain in the image is the recorded one (a difference is a review event)'),
    'anchor': ('mk', "The anchor is the owner's, set outside this checkout (fail closed)"),
    'ledger': ('mk', 'The anchor is the one kernel/coq/ANCHORS.md records for this folder'),
    'load': ('mk', 'Load it; it is the image the image job checked (the same id and base)'),
    'gatetool': ('mk', 'The toolchain in this image is the recorded one'),
    'rows': ('mk', "Feature rows 3 and 4 on the folder's freeze list (the tree read-only)"),
    'gate': ('mk', "The folder's gate, with its anchor, every library rechecked"),
    'needs': ('mk', 'Every other job of this run succeeded'),
    'rows-in': ('in', 'Feature rows 3 and 4 on every freeze list the inventory found'),
    'fpenv': ('mk', "mk_fpenv's self-test, plants and mutants with GCC and clang"),
    'fpv': ('mk', 'Each fpenv leg held, by its own evidence'),
    'sweep': ('mk', 'The frozen floor32/ceil32 sweep with GCC and clang at -O0 and -O2 (its sha256, no x87 or FMA, '
                    'plants)'),
    'swv': ('mk', 'Each sweep leg held, by its own evidence'),
}
RENAMED = ('- name: Every other job of this run succeeded', '- name: Every job succeeded')
COPIED = ('ci/mathkernel/Dockerfile', 'ci/mathkernel/EXPECTED-TOOLCHAIN.txt', 'tools/ci/check_toolchain.py',
          'tools/ci/toolchain_probe.sh', 'kernel/coq/ANCHORS.md', 'tools/ci/inventory.py')
# The fpenv leg's step runs with a PATH of one folder: these tools, each a wrapper of /usr/bin/<tool> (Linux and Git
# Bash both have them there), the stand-in python3 and the compilers the case plants, so the step's search for its
# compilers sees only what the case puts there.
FP_TOOLS = ('cat', 'grep', 'ls', 'mkdir', 'sort', 'tail', 'tee')
FP_HELD = 'FPENV CHECK HELD: 26 of 26 rows (4 skipped: a stand-in)'
SHIM_FP_PYTHON = '''#!/bin/bash
# test_workflow_guards.py's stand-in for python3 in the fpenv step: it prints its arguments and the check output the
# case planted, and exits as planted.
echo "check_fpenv (stand-in): $*"
if [ -n "${FAKE_FPENV_OUT:-}" ]; then /usr/bin/cat "$FAKE_FPENV_OUT"; fi
exit "${FAKE_FPENV_EXIT:-0}"
'''
SW_HELD = 'SWEEP CHECK HELD: 34 of 34 rows (fclink; x86-64; gcc, clang)'
SW_HELD_ARM = 'SWEEP CHECK HELD: 32 of 32 rows (fclink; aarch64; gcc, clang)'
SHIM_SW_PYTHON = '''#!/bin/bash
# test_workflow_guards.py's stand-in for python3 in the sweep step: it prints its arguments and the check output the
# case planted, and exits as planted.
echo "check_sweep (stand-in): $*"
if [ -n "${FAKE_SWEEP_OUT:-}" ]; then /usr/bin/cat "$FAKE_SWEEP_OUT"; fi
exit "${FAKE_SWEEP_EXIT:-0}"
'''
RECORD_KEYS = ('coqc-where /opt/opam/4.14.2/lib/coq', 'coqchk-bytecode-default unknown', 'env COQPATH unset',
               'env COQLIB unset', 'env OCAMLPATH unset', 'env OCAMLRUNPARAM unset')
BASE_PACKAGES = ('opam base-bigarray base', 'opam base-threads base', 'opam base-unix base')
FAKE_ID = 'sha256:' + hashlib.sha256(b'test_workflow_guards image').hexdigest()
OTHER_DIGEST = 'sha256:' + hashlib.sha256(b'test_workflow_guards other base').hexdigest()
CR_REASON = 'this bash drops a carriage return before the final newline of a command substitution (Git Bash does; ' \
            'bash on Linux keeps it), so the planted CR never reaches the guard'

SHIM_DOCKER = r'''#!/usr/bin/env bash
# test_workflow_guards.py's stand-in for docker: it prints what the case planted; it never runs a container.
case $1 in
  build)
    if [ -n "${FAKE_BUILD_LOG:-}" ]; then cat "$FAKE_BUILD_LOG"; fi
    exit "${FAKE_BUILD_EXIT:-0}" ;;
  save)
    printf 'image\n' > "$3"
    exit 0 ;;
  load)
    echo "Loaded image: ${IMAGE:-}"
    exit 0 ;;
  image)
    printf '%s\n' "${FAKE_ID:-}"
    exit 0 ;;
  run)
    for a in "$@"; do
      case $a in
        tools/ci/toolchain_probe.sh)
          if [ -n "${FAKE_OBSERVED:-}" ]; then cat "$FAKE_OBSERVED"; fi
          exit "${FAKE_PROBE_EXIT:-0}" ;;
        gate/gate4.py)
          if [ -n "${FAKE_GATE_OUT:-}" ]; then cat "$FAKE_GATE_OUT"; fi
          exit "${FAKE_GATE_EXIT:-0}" ;;
        kernel/hardening/features/feature_row*.py)
          if [ "$a" = "kernel/hardening/features/${FAKE_ROW_FAILS:-none}" ]; then
            echo "FEATURE ROW (stand-in) FAILED"
            exit 1
          fi
          echo "FEATURE ROW (stand-in) HELD"
          exit 0 ;;
      esac
    done
    echo "image description (stand-in)"
    exit 0 ;;
esac
echo "docker stand-in: not a call of this test: $*" >&2
exit 99
'''
SHIM_GIT = r'''#!/usr/bin/env bash
# test_workflow_guards.py's stand-in for git: ls-files -z prints the case's list of tracked files.
if [ "${1:-}" = ls-files ] && [ "${2:-}" = -z ]; then
  cat "$FAKE_TRACKED"
  exit 0
fi
echo "git stand-in: not a call of this test: $*" >&2
exit 99
'''
SHIM_PYTHON = r'''#!/usr/bin/env bash
# test_workflow_guards.py's stand-in for python3: the inventory call copies the case's planted matrix to --matrix-out
# and exits as planted; a feature row exits 1 for the planted row and list, else 0; every other call runs the test's
# own interpreter with the same arguments and standard input.
for a in "$@"; do
  case $a in
    tools/ci/inventory.py)
      out=
      prev=
      for b in "$@"; do
        if [ "$prev" = --matrix-out ]; then out=$b; fi
        prev=$b
      done
      if [ -n "${PLANT_MATRIX:-}" ] && [ -n "$out" ]; then cp "$PLANT_MATRIX" "$out"; fi
      exit "${PLANT_INV_EXIT:-0}" ;;
    kernel/hardening/features/feature_row*.py)
      if [ "$a" = "kernel/hardening/features/${FAKE_ROW_FAILS:-none}" ]; then
        case " $* " in
          *" ${FAKE_ROW_LIST:-none} "*) echo "FEATURE ROW (stand-in) FAILED"; exit 1 ;;
        esac
      fi
      echo "FEATURE ROW (stand-in) HELD"
      exit 0 ;;
  esac
done
exec "$REAL_PY" "$@"
'''


class NotBuilt(Exception):
    pass


def rb(path):
    with open(path, 'rb') as f:
        return f.read()


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def fwd(p):
    """A path as bash on either system reads it: forward slashes (a Windows path keeps its drive)."""
    return p.replace('\\', '/')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_predictions():
    """({case: (outcome, [checks])}, problems). A line: "case | exit <n>|exit nonzero | checks | what"; checks are
    "-" or comma-separated: msg:<word>, say:<text>, out:<n>, outeq:<key>, base:<which>, cr, missing:<step name>."""
    preds, problems = {}, []
    lines = [(os.path.basename(p), n, x) for p in PRED for n, x in enumerate(rb(p).decode('utf-8').split('\n'), 1)]
    for fname, n, line in lines:
        if not line or line.startswith('#'):
            continue
        parts = line.split(' | ')
        if len(parts) != 4 or parts[0] in preds or not re.fullmatch(r'exit (\d+|nonzero)|ok|FAIL', parts[1]):
            problems.append('%s line %d is not "case | outcome | checks | what", or repeats a case' % (fname, n))
            continue
        checks = [] if parts[2] == '-' else parts[2].split(',')
        preds[parts[0]] = (parts[1], checks)
    return preds, problems


def step_block(text, name):
    """The run: block of the one step named name in a workflow's text, as the runner writes it to a file."""
    lines = text.split('\n')
    at = [i for i, x in enumerate(lines) if x.strip() == '- name: ' + name]
    if len(at) != 1:
        raise NotBuilt('%d steps named "%s"' % (len(at), name))
    i = at[0]
    dash = len(lines[i]) - len(lines[i].lstrip(' '))
    j = i + 1
    while j < len(lines):
        s = lines[j]
        ind = len(s) - len(s.lstrip(' '))
        if s.strip() and ind <= dash:
            break
        m = re.match(r'^(\s*)run:\s*\|\s*$', s)
        if m:
            key = len(m.group(1))
            body, k = [], j + 1
            while k < len(lines) and (not lines[k].strip() or len(lines[k]) - len(lines[k].lstrip(' ')) > key):
                body.append(lines[k])
                k += 1
            while body and not body[-1].strip():
                body.pop()
            if not body:
                raise NotBuilt('the step "%s" has an empty run: block' % name)
            cut = min(len(b) - len(b.lstrip(' ')) for b in body if b.strip())
            return '\n'.join(b[cut:] for b in body) + '\n'
        m = re.match(r'^\s*run:\s*(\S.*)$', s)
        if m:
            return m.group(1) + '\n'
        j += 1
    raise NotBuilt('the step "%s" has no run: key' % name)


def missing_steps(texts):
    """The steps of STEPS that are not in the workflow texts once, each with a run: block."""
    out = []
    for key in sorted(STEPS):
        wf, name = STEPS[key]
        try:
            step_block(texts[wf], name)
        except NotBuilt as e:
            out.append('%s: %s' % (WF[wf], e))
    return out


def top_env(text):
    """The workflow's top-level env: {name: value}."""
    lines = text.split('\n')
    env, inside = {}, False
    for x in lines:
        if x == 'env:':
            inside = True
            continue
        if inside:
            if x and not x.startswith(' '):
                break
            m = re.fullmatch(r'\s+([A-Z_][A-Z0-9_]*):\s*"?([^"]*)"?\s*', x)
            if m:
                env[m.group(1)] = m.group(2)
    return env


class Ctx(object):
    def __init__(self, tmp, bash):
        self.tmp, self.bash = tmp, bash
        self.texts = {k: rb(os.path.join(ROOT, *p.split('/'))).decode('utf-8') for k, p in WF.items()}
        self.env = {k: top_env(t) for k, t in self.texts.items()}
        self.shims = os.path.join(tmp, 'shims')
        for name, body in (('docker', SHIM_DOCKER), ('git', SHIM_GIT), ('python3', SHIM_PYTHON)):
            p = os.path.join(self.shims, name)
            wb(p, body.encode('ascii'))
            os.chmod(p, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        self.n = 0
        self.problems = []
        self.made()

    def made(self):
        """The honest inputs, from the tree."""
        d = os.path.join(self.tmp, 'honest')
        os.makedirs(d)
        inv, mat = os.path.join(d, 'inventory.json'), os.path.join(d, 'matrix.json')
        p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'ci', 'inventory.py'), '--root', ROOT,
                            '--json', inv, '--matrix-out', mat], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=600)
        self.matrix = rb(mat) if p.returncode == 0 and os.path.isfile(mat) else None
        self.inventory_json = rb(inv) if os.path.isfile(inv) else None
        if self.matrix is None:
            self.problems.append('tools/ci/inventory.py exited %d and wrote no matrix' % p.returncode)
            self.folders = []
        else:
            self.folders = [x['folder'] for x in json.loads(self.matrix.decode('utf-8'))['include']]
        self.anchor = {f: sha(rb(os.path.join(ROOT, 'kernel', 'coq', f, 'FROZEN4.txt'))) for f in self.folders}
        dockerfile = rb(os.path.join(ROOT, 'ci', 'mathkernel', 'Dockerfile')).decode('utf-8')
        froms = re.findall(r'(?m)^FROM ([^ @\n]+)@(sha256:[0-9a-f]{64})$', dockerfile)
        if len(froms) != 1:
            self.problems.append('the Dockerfile has %d pinned FROM lines, not 1' % len(froms))
            froms = [('ubuntu:24.04', 'sha256:' + '0' * 64)]
        self.image, self.pin = froms[0]
        full = self.image if '/' in self.image else 'docker.io/library/' + self.image
        self.ref = '%s@%s' % (full, self.pin)
        self.other_ref = '%s@%s' % (full, OTHER_DIGEST)
        expected = rb(os.path.join(ROOT, 'ci', 'mathkernel', 'EXPECTED-TOOLCHAIN.txt')).decode('utf-8')
        lines = [x for x in expected.split('\n') if x and not x.startswith('#')]
        self.observed = ('\n'.join(lines + list(BASE_PACKAGES) + list(RECORD_KEYS)) + '\n').encode('utf-8')
        obs = os.path.join(d, 'observed.txt')
        wb(obs, self.observed)
        p = subprocess.run([sys.executable, '-B', os.path.join(ROOT, 'tools', 'ci', 'check_toolchain.py'),
                            '--observed', obs, '--expected', os.path.join(ROOT, 'ci', 'mathkernel',
                                                                          'EXPECTED-TOOLCHAIN.txt')],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        found = re.findall(r'(?m)^TOOLCHAIN DIGEST ([0-9a-f]{64})\r?$', p.stdout.decode('utf-8', 'replace'))
        self.digest = found[0] if p.returncode == 0 and len(found) == 1 else None
        if self.digest is None:
            self.problems.append('tools/ci/check_toolchain.py did not hold the probe output built from the record')
        m = re.search(r'(?m)^sha256 (\S*/coqc) ([0-9a-f]{64})$', self.observed.decode('utf-8'))
        self.observed_bad = self.observed.replace(m.group(0).encode(), ('sha256 %s %s' % (m.group(1), 'f' * 64))
                                                  .encode()) if m else self.observed + b'not a line\n'

    def fp_path(self, d, compilers, shim=SHIM_FP_PYTHON):
        """The one folder of the fpenv or sweep step's PATH: FP_TOOLS' wrappers, the stand-in python3 (shim) and the
        compilers (and, for the sweep step, objdump) the case plants."""
        fp = os.path.join(d, 'fp-path')
        for tool in FP_TOOLS:
            wb(os.path.join(fp, tool), ('#!/bin/bash\nexec /usr/bin/%s "$@"\n' % tool).encode('ascii'))
        wb(os.path.join(fp, 'python3'), shim.encode('ascii'))
        for cc in compilers:
            wb(os.path.join(fp, cc), b'#!/bin/bash\nexit 0\n')
        for name in os.listdir(fp):
            os.chmod(os.path.join(fp, name), stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        return fp

    def run(self, key, env=None, files=None, matrix=None, dockerfile=None, base_txt=None, anchors=None,
            inventory=None, temp_files=None, compilers=None, shim=SHIM_FP_PYTHON):
        """(exit code, stdout, stderr, GITHUB_OUTPUT lines, case folder) of one step on one case's inputs."""
        wf, name = STEPS[key]
        block = step_block(self.texts[wf], name)
        self.n += 1
        d = os.path.join(self.tmp, 'c%03d' % self.n)
        ws, temp, mk = os.path.join(d, 'w'), os.path.join(d, 'temp'), os.path.join(d, 'mk-image')
        os.makedirs(temp)
        for rel, data in (temp_files or {}).items():
            wb(os.path.join(temp, *rel.split('/')), data)
        for rel in COPIED:
            wb(os.path.join(ws, *rel.split('/')), rb(os.path.join(ROOT, *rel.split('/'))))
        if dockerfile is not None:
            wb(os.path.join(ws, 'ci', 'mathkernel', 'Dockerfile'), dockerfile)
        if anchors is not None:
            wb(os.path.join(ws, 'kernel', 'coq', 'ANCHORS.md'), anchors)
        if base_txt is not None:
            wb(os.path.join(mk, 'base-image.txt'), base_txt)
            wb(os.path.join(mk, 'image.tar'), b'image\n')
        if inventory is not None:
            wb(os.path.join(temp, 'inventory.json'), inventory)
        script = os.path.join(d, 'step.sh')
        wb(script, block.replace('/tmp/mk-image', fwd(mk)).encode('utf-8'))
        out = os.path.join(temp, 'github_output')
        wb(out, b'')
        e = {k: v for k, v in os.environ.items()
             if not k.startswith(('GITHUB_', 'RUNNER_', 'FAKE_', 'PLANT_')) and k not in ('BASH_ENV', 'ENV')}
        e.update(self.env[wf])
        e.update(RUNNER_TEMP=fwd(temp), GITHUB_OUTPUT=fwd(out), GITHUB_WORKSPACE=fwd(ws), REAL_PY=fwd(sys.executable),
                 MSYS_NO_PATHCONV='1', PATH=self.shims + os.pathsep + os.environ.get('PATH', ''))
        if matrix is not None:
            wb(os.path.join(d, 'matrix-plant.json'), matrix)
            e['PLANT_MATRIX'] = fwd(os.path.join(d, 'matrix-plant.json'))
        for k, data in (files or {}).items():
            p = os.path.join(d, k)
            wb(p, data)
            e[k] = fwd(p)
        if compilers is not None:
            e['PATH'] = self.fp_path(d, compilers, shim)
        e.update(env or {})
        p = subprocess.run([self.bash, '-e', fwd(script)], cwd=ws, env=e, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        lines = rb(out).decode('utf-8', 'replace').splitlines()
        return (p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace'), lines, mk)


def cr_probe(bash, where):
    """True when this bash keeps a CR before the final newline of a command substitution (run in the folder where)."""
    p = subprocess.run([bash, '-c', 'v=$(printf "abc\\r\\n"); printf "%s" "${#v}"'], stdin=subprocess.DEVNULL,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, cwd=where)
    return p.stdout.decode('ascii', 'replace').strip() == '4'


def judge(pred, got, want):
    """(ok, detail): got = (code, stdout, stderr, output lines, mk folder); want = {key: value} for outeq and base."""
    outcome, checks = pred
    code, so, se, outl, mk = got
    bad = []
    if outcome == 'exit nonzero':
        if code == 0:
            bad.append('exit 0')
    elif code != int(outcome[len('exit '):]):
        bad.append('exit %d' % code)
    for c in checks:
        kind, _, arg = c.partition(':')
        if kind == 'msg' and arg not in se:
            bad.append('its errors lack "%s"' % arg)
        elif kind == 'say' and arg not in so:
            bad.append('its output lacks "%s"' % arg)
        elif kind == 'out' and len(outl) != int(arg):
            bad.append('%d lines in GITHUB_OUTPUT' % len(outl))
        elif kind == 'outeq':
            line = [x for x in outl if x.startswith(arg + '=')]
            if line != ['%s=%s' % (arg, want.get(arg))]:
                bad.append('GITHUB_OUTPUT %s: %s' % (arg, ascii(line[:2])[:120]))
        elif kind == 'base':
            p = os.path.join(mk, 'base-image.txt')
            have = rb(p) if os.path.isfile(p) else None
            if have != (want.get('base', '') + '\n').encode('utf-8'):
                bad.append('base-image.txt holds %s' % ascii(have)[:120])
        elif kind == 'msgline' and arg not in [x.rstrip('\r') for x in se.split('\n')]:
            bad.append('no line of its errors is exactly "%s"' % arg)
        elif kind in ('evid', 'sevid'):
            p = os.path.join(os.path.dirname(mk), 'temp', 'fpenv' if kind == 'evid' else 'sweep', 'evidence.txt')
            have = rb(p) if os.path.isfile(p) else None
            if have != (None if arg == 'none' else want.get('evidence')):
                bad.append('evidence.txt holds %s' % ascii(have)[:120])
    last = (se.strip().splitlines() or so.strip().splitlines() or [''])[-1]
    detail = 'exit %d; %s' % (code, last[:110])
    return not bad, detail + ('' if not bad else '; NOT AS PREDICTED: ' + '; '.join(bad))


def gate_console(anchor16, status='ok'):
    row = '  %-62s %s  %s' % ('freeze list is the anchored one', status, 'ANCHOR %s' % anchor16)
    return ('gate4.py %s judges f32 (identity f32.Identity; sources of f32) in /work  --recheck\n' % ('0' * 64)
            + '  %-62s %s  %s\n' % ('freeze list: every line is readable', 'ok', '12 entries') + row + '\n'
            + 'F32 GATE4 HELD: 20 of 20  [anchor %s]\n' % anchor16).encode('ascii')


def needs(**res):
    d = {'inventory': {'result': 'success', 'outputs': {'matrix': '{}'}}, 'fpenv': {'result': 'success', 'outputs': {}},
         'sweep': {'result': 'success', 'outputs': {}}, 'image': {'result': 'success', 'outputs': {}},
         'gate': {'result': 'success', 'outputs': {}}}
    for k, v in res.items():
        d[k]['result'] = v
    return json.dumps(d, indent=2)


def cases(ctx):
    """[(case id, step key, run keyword arguments, expected values)]."""
    out = []

    def add(cid, key, want=None, **kw):
        out.append((cid, key, kw, want or {}))

    honest_list = b'\0'.join([b'AGENTS.md', b'tools/ci/inventory.py', b'kernel/coq/gate/gate4.py']) + b'\0'
    for cid, key, lst in (('k01', 'pyc-mk', honest_list),
                          ('k02', 'pyc-mk', honest_list + b'tools/ci/__pycache__/inventory.cpython-312.pyc\0'),
                          ('k03', 'pyc-mk', honest_list + b'kernel/coq/gate/strict_read.pyo\0'),
                          ('k11', 'pyc-in', honest_list),
                          ('k12', 'pyc-in', honest_list + b'json.pyc\0')):
        add(cid, key, files={'FAKE_TRACKED': lst})

    m = ctx.matrix or b'{"include":[]}\n'
    hm = m.decode('utf-8').strip()
    mo = {'matrix': hm}
    add('m01', 'matrix', mo, matrix=m)
    add('m02', 'matrix', matrix=(hm + '\nmatrix={"include":[{"folder":"x","anchor":"MK_ANCHOR_X"}]}\n').encode())
    add('m03', 'matrix', matrix=(hm + '\r\n').encode())
    add('m04', 'matrix', matrix=b'{"include":[]}\n')
    add('m05', 'matrix', matrix=b'{"include":[{"folder":"F32","anchor":"MK_ANCHOR_F32"}]}\n')
    add('m06', 'matrix', matrix=b'{"include":[{"folder":"f32","anchor":"MK_ANCHOR_F32","x":"y"}]}\n')
    add('m07', 'matrix', matrix=(hm.replace('"include":', '"include": ') + '\n').encode())
    add('m08', 'matrix', matrix=b'{"include":[{"folder":"f32","anchor":"GITHUB_TOKEN"}]}\n')
    add('m09', 'matrix', matrix=(hm[:-1] + ',"exclude":[]}\n').encode())
    add('m10', 'matrix')
    add('m11', 'matrix', matrix=m, env={'PLANT_INV_EXIT': '1'})
    add('m12', 'matrix', mo, matrix=(hm + '\n\n').encode())
    add('m13', 'matrix', matrix=b'{"include":[{"folder":"f32","anchor":"MK_ANCHOR_F32"}\n')
    add('m14', 'matrix', matrix=(hm[:1] + '\r' + hm[1:] + '\n').encode())

    build_pre = '#1 [internal] load build definition from Dockerfile\n#1 DONE 0.0s\n'
    honest_from = '#5 [1/4] FROM %s\n' % ctx.ref
    add('b01', 'build', {'base': ctx.ref}, files={'FAKE_BUILD_LOG': (build_pre + honest_from + '#5 DONE 0.6s\n')
                                                  .encode()})
    add('b02', 'build', {'base': ctx.ref}, files={'FAKE_BUILD_LOG': (build_pre + '#5 [1/4] FROM %s@%s\n'
                                                                     % (ctx.ref, ctx.pin)).encode()})
    add('b03', 'build', files={'FAKE_BUILD_LOG': (build_pre + '#5 [1/4] FROM docker.io/library/ubuntu:24.04\n')
                               .encode()})
    add('b04', 'build', files={'FAKE_BUILD_LOG': (build_pre + honest_from + 'ERROR: failed to solve\n').encode()},
        env={'FAKE_BUILD_EXIT': '1'})
    add('b05', 'build', {'base': ctx.other_ref}, files={'FAKE_BUILD_LOG': (build_pre + '#5 [1/4] FROM %s\n'
                                                                           % ctx.other_ref + honest_from).encode()})
    # after the fifth review (PREDICTIONS-workflow_guards-3.txt): BuildKit's padded and stage-named step labels
    for cid, line in (('b06', '#5 [ 1/10] FROM %s\n'), ('b07', '#5 [base 1/4] FROM %s\n'),
                      ('b08', '#5 [stage-0  1/10] FROM %s\n')):
        add(cid, 'build', {'base': ctx.ref}, files={'FAKE_BUILD_LOG': (build_pre + line % ctx.ref).encode()})
    add('b09', 'build', files={'FAKE_BUILD_LOG': (build_pre + '#5 [ 2/10] FROM %s\n#6 0.512 [ 1/10] FROM %s\n'
                                                  % (ctx.ref, ctx.ref)).encode()})

    dockerfile = rb(os.path.join(ROOT, 'ci', 'mathkernel', 'Dockerfile'))
    pinned = ('FROM %s@%s' % (ctx.image, ctx.pin)).encode()
    hb = (ctx.ref + '\n').encode()
    io = {'image_id': FAKE_ID, 'base_image': ctx.ref}
    add('i01', 'image', io, base_txt=hb, env={'FAKE_ID': FAKE_ID})
    add('i02', 'image', base_txt=(ctx.other_ref + '\n').encode(), env={'FAKE_ID': FAKE_ID})
    add('i03', 'image', env={'FAKE_ID': FAKE_ID})
    add('i04', 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID},
        dockerfile=dockerfile.replace(pinned, pinned.split(b'@')[0]))
    add('i05', 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID},
        dockerfile=dockerfile.replace(pinned, pinned + b' AS a\n' + pinned))
    add('i06', 'image', base_txt=b'junk\n' + hb, env={'FAKE_ID': FAKE_ID})
    add('i07', 'image', base_txt=hb, env={'FAKE_ID': 'abc'})
    add('i08', 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID + '\n' + FAKE_ID})
    add('i09', 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID},
        dockerfile=dockerfile.replace(pinned, pinned + b' AS base'))
    add('i10', 'image', base_txt=(ctx.ref + '\r\n').encode(), env={'FAKE_ID': FAKE_ID})
    # after the sixth review: a second stage in the spellings Docker reads, a parser directive, a split keyword
    # (PREDICTIONS-workflow_guards-4.txt)
    for cid, extra in (('d02', b'\nfrom docker.io/library/debian:12\nCOPY --from=0 /opt /opt\n'),
                       ('d03', b'\n  FROM debian:12\n'), ('d04', b'\nFROM\tdebian:12\n'),
                       ('d05', b'\nFROM debian:12\n'),
                       ('d06', b'\nfrom scratch\nCOPY --from=0 / /\n'), ('d08', b'\nFR\\\nOM debian:12\n'),
                       ('d09', b'\nRUN true \\\n# a comment inside the instruction\n && true\n')):
        add(cid, 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID}, dockerfile=dockerfile + extra)
    add('d07', 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID}, dockerfile=b'# escape=`\n' + dockerfile)
    # after the seventh review: the forms the count cannot read (PREDICTIONS-workflow_guards-5.txt); x02 runs in the C
    # locale, where grep does not read a no-break space as a space (as glibc's grep reads it in every locale)
    bom, nbsp = b'\xef\xbb\xbf', b'\xc2\xa0'
    spdx_end = dockerfile.index(b'\n') + 1
    for cid, data, env in (
            ('x01', bom + b'FROM docker.io/library/debian:12 AS x\n' + dockerfile + b'COPY --from=x /opt /opt\n', {}),
            ('x02', dockerfile + b'\n' + nbsp + b'FROM docker.io/library/debian:12\n', {'LC_ALL': 'C'}),
            ('x03', b'#!/bin/sh\n# syntax=docker/dockerfile:1\n' + dockerfile, {}),
            ('x04', b'// syntax=docker/dockerfile:1\n' + dockerfile, {}),
            ('x05', bom + b'# syntax=docker/dockerfile:1\n' + dockerfile, {}),
            ('x06', dockerfile[:spdx_end] + b'# syntax=docker/dockerfile:1\n' + dockerfile[spdx_end:], {}),
            ('x07', dockerfile + b'\n// syntax=docker/dockerfile:1\n', {}),
            ('x08', dockerfile + b'\nF\\\n  # inside the instruction\nROM ubuntu:24.04\n', {}),
            ('x09', dockerfile + b'\nF\\\n   \nROM ubuntu:24.04\n', {}),
            ('x10', dockerfile + b'\nRUN true \\\n\t&& true\n# a comment after the instruction\n', {})):
        add(cid, 'image', io if cid == 'x10' else None, base_txt=hb, env=dict(env, FAKE_ID=FAKE_ID), dockerfile=data)
    # after the eighth review: FROM before a line continuation, and a NUL byte (PREDICTIONS-workflow_guards-6.txt)
    for cid, extra in (('h02', b'\nFROM\\\n docker.io/library/debian:12\nCOPY --from=0 /opt /opt\n'),
                       ('h03', b'\nFROM\\  \n\tdocker.io/library/debian:12 AS x\n'),
                       ('h04', b'\nfrom\\\n debian:12\n'),
                       ('h05', b'\nFROM \\\n debian:12\n'),
                       ('h06', b'\nFR\\\nOM debian:12\n'),
                       ('h07', b'\n# a comment holding a NUL byte \x00 here\n')):
        add(cid, 'image', base_txt=hb, env={'FAKE_ID': FAKE_ID}, dockerfile=dockerfile + extra)

    add('t01', 'toolchain', {'digest': ctx.digest}, files={'FAKE_OBSERVED': ctx.observed})
    add('t02', 'toolchain', files={'FAKE_OBSERVED': ctx.observed}, env={'FAKE_PROBE_EXIT': '3'})
    add('t03', 'toolchain', files={'FAKE_OBSERVED': ctx.observed_bad})
    add('t04', 'toolchain', files={'FAKE_OBSERVED': b''})

    f = 'f32' if 'f32' in ctx.folders else (ctx.folders[0] if ctx.folders else 'f32')
    g = 'p32' if 'p32' in ctx.folders and f != 'p32' else ([x for x in ctx.folders if x != f] or ['p32'])[0]
    a = ctx.anchor.get(f, '0' * 64)
    base_env = {'FOLDER': f, 'ANCHOR_NAME': 'MK_ANCHOR_' + f.upper(), 'ANCHOR': a}
    add('a01', 'anchor', env=base_env)
    add('a02', 'anchor', env=dict(base_env, ANCHOR=''))
    add('a03', 'anchor', env=dict(base_env, ANCHOR=a.upper()))
    add('a04', 'anchor', env=dict(base_env, ANCHOR=a[:63]))
    add('a05', 'anchor', env=dict(base_env, ANCHOR_NAME='MK_ANCHOR_' + g.upper()))
    add('a06', 'anchor', env=dict(base_env, ANCHOR=a + '\njunk'))
    add('a07', 'anchor', env=dict(base_env, FOLDER=f.upper()))
    add('a08', 'anchor', env=dict(base_env, ANCHOR=a + ' '))

    add('r01', 'ledger', each=[{'FOLDER': x, 'ANCHOR_NAME': 'MK_ANCHOR_' + x.upper(), 'ANCHOR': ctx.anchor[x]}
                               for x in ctx.folders])
    add('r02', 'ledger', env=dict(base_env, ANCHOR=ctx.anchor.get(g, '1' * 64)))
    add('r03', 'ledger', env=dict(base_env, ANCHOR_NAME='MK_ANCHOR_' + g.upper()))
    add('r04', 'ledger', env={'FOLDER': 'newf', 'ANCHOR_NAME': 'MK_ANCHOR_NEWF', 'ANCHOR': a})
    add('r05', 'ledger', env=dict(base_env, ANCHOR=''))
    ledger = rb(os.path.join(ROOT, 'kernel', 'coq', 'ANCHORS.md'))
    stray = ledger.rstrip(b'\n') + ('\n\n| `%s` | `MK_ANCHOR_%s` | `%s` | a stray row |\n'
                                    % (f, f.upper(), '0' * 64)).encode()
    add('r06', 'ledger', env=base_env, anchors=stray)

    hbase = {'FAKE_ID': FAKE_ID, 'BUILT_IMAGE_ID': FAKE_ID, 'BUILT_BASE_IMAGE': ctx.ref}
    add('l01', 'load', base_txt=hb, env=hbase)
    add('l02', 'load', base_txt=hb, env=dict(hbase, FAKE_ID=FAKE_ID[:-1] + ('0' if FAKE_ID[-1] != '0' else '1')))
    add('l03', 'load', base_txt=hb, env=dict(hbase, BUILT_IMAGE_ID=''))
    add('l04', 'load', base_txt=(ctx.other_ref + '\n').encode(), env=hbase)
    add('g01', 'gatetool', files={'FAKE_OBSERVED': ctx.observed}, env={'BUILT_TOOLCHAIN_DIGEST': ctx.digest or ''})
    add('g02', 'gatetool', files={'FAKE_OBSERVED': ctx.observed}, env={'BUILT_TOOLCHAIN_DIGEST': ''})
    add('g03', 'gatetool', files={'FAKE_OBSERVED': ctx.observed_bad}, env={'BUILT_TOOLCHAIN_DIGEST': ctx.digest or ''})

    add('f01', 'rows', env={'FOLDER': f})
    add('f02', 'rows', env={'FOLDER': f, 'FAKE_ROW_FAILS': 'feature_row4.py'})
    add('e01', 'gate', files={'FAKE_GATE_OUT': gate_console(a[:16])}, env=base_env)
    add('e02', 'gate', files={'FAKE_GATE_OUT': gate_console(ctx.anchor.get(g, '1' * 64)[:16])}, env=base_env)
    add('e03', 'gate', files={'FAKE_GATE_OUT': gate_console(a[:16], 'FAIL')}, env=base_env)
    add('e04', 'gate', files={'FAKE_GATE_OUT': gate_console(a[:16])}, env=dict(base_env, FAKE_GATE_EXIT='1'))

    add('v01', 'needs', env={'NEEDS': needs()})
    add('v02', 'needs', env={'NEEDS': needs(inventory='failure', gate='skipped')})
    add('v03', 'needs', env={'NEEDS': needs(gate='failure')})
    add('v04', 'needs', env={'NEEDS': needs(image='failure', gate='skipped')})
    add('v05', 'needs', env={'NEEDS': needs(gate='cancelled')})
    n6 = json.loads(needs())
    del n6['fpenv']
    add('v06', 'needs', env={'NEEDS': json.dumps(n6)})
    add('v07', 'needs', env={'NEEDS': '{}'})
    n8 = json.loads(needs())
    n8['gate'] = 'success'
    add('v08', 'needs', env={'NEEDS': json.dumps(n8)})
    add('v09', 'needs', env={'NEEDS': needs(inventory='skipped', fpenv='skipped', image='skipped', gate='skipped')})
    add('v10', 'needs', env={'NEEDS': 'not json'})

    inv = ctx.inventory_json or b'{"gated":[],"mirrors":[]}\n'
    add('n01', 'rows-in', inventory=inv)
    add('n02', 'rows-in', inventory=inv, env={'FAKE_ROW_FAILS': 'feature_row4.py',
                                              'FAKE_ROW_LIST': 'kernel/coq/%s/FROZEN4.txt' % f})
    add('n03', 'rows-in', inventory=json.dumps({'gated': [], 'mirrors': [{'folder': f}]}).encode())
    add('n04', 'rows-in', inventory=b'not json\n')

    # PREDICTIONS-workflow_guards-2.txt: the matrix guard's own words (m15, m16), the ANCHORS.md step reading the
    # table as tools/ci/inventory.py reads it (r07-r12), the fpenv leg's step (p01-p09) and the verdict's reading of
    # each leg's evidence (w01-w08).
    add('m15', 'matrix', matrix=(hm[:1] + '\r' + hm[1:] + '\n').encode())
    add('m16', 'matrix', matrix=(hm[:1] + '\n' + hm[1:] + '\n').encode())
    zero_row = '`%s` | `MK_ANCHOR_%s` | `%s` | a stray row' % (f, f.upper(), '0' * 64)
    tail = ledger.rstrip(b'\n')
    add('r07', 'ledger', env=base_env, anchors=tail + ('\n%s\n' % zero_row).encode())
    add('r08', 'ledger', env=base_env, anchors=tail + ('\n\n%s\n' % zero_row).encode())
    add('r09', 'ledger', env=base_env, anchors=tail + b'\n#tag\n')
    add('r10', 'ledger', env=base_env, anchors=tail + ('\n\nFolder | Variable | sha256 of FROZEN4.txt | Record\n'
                                                       '---|---|---|---\n%s\n' % zero_row).encode())
    add('r11', 'ledger', env=base_env, anchors=b'\n'.join((b'  ' + x if x.startswith(b'|') else x)
                                                          for x in ledger.split(b'\n')))
    add('r12', 'ledger', env=base_env, anchors=b'\n'.join((b'    ' + x if x.startswith(b'|') else x)
                                                          for x in ledger.split(b'\n')))

    lg = {'LEG': 'ubuntu-24.04', 'GITHUB_RUN_ATTEMPT': '1'}
    ev = {'evidence': ('fpenv ubuntu-24.04 attempt 1\n%s\n' % FP_HELD).encode('ascii')}
    out_ok = {'FAKE_FPENV_OUT': ('  a row ok\n%s\n' % FP_HELD).encode('ascii')}
    add('p01', 'fpenv', ev, env=lg, files=out_ok, compilers=['gcc', 'clang'])
    add('p02', 'fpenv', ev, env=lg, files=out_ok, compilers=['clang'])
    add('p03', 'fpenv', ev, env=lg, files=out_ok, compilers=['gcc'])
    add('p04', 'fpenv', ev, env=lg, files=out_ok, compilers=['gcc', 'clang-17', 'clang-18'])
    add('p05', 'fpenv', ev, env=dict(lg, FAKE_FPENV_EXIT='1'), compilers=['gcc', 'clang'],
        files={'FAKE_FPENV_OUT': b'FPENV CHECK FAILED: 1 of 26 rows failed\n'})
    add('p06', 'fpenv', ev, env=lg, compilers=['gcc', 'clang'],
        files={'FAKE_FPENV_OUT': b'FPENV CHECK FAILED: 1 of 26 rows failed\n'})
    add('p07', 'fpenv', ev, env=lg, compilers=['gcc', 'clang'],
        files={'FAKE_FPENV_OUT': ('%s\ndone\n' % FP_HELD).encode('ascii')})
    add('p08', 'fpenv', ev, env=lg, compilers=['gcc', 'clang'],
        files={'FAKE_FPENV_OUT': ('%s\r\n' % FP_HELD).encode('ascii')})
    add('p09', 'fpenv', ev, env=lg, compilers=['gcc', 'clang'], files={'FAKE_FPENV_OUT': b''})

    def evidence(leg, attempt='1', line=FP_HELD, end='\n'):
        return ('fpenv %s attempt %s%s%s%s' % (leg, attempt, end, line, end)).encode('ascii')
    x86, arm = 'inputs/fpenv/ubuntu-24.04/evidence.txt', 'inputs/fpenv/ubuntu-24.04-arm/evidence.txt'
    both = {x86: evidence('ubuntu-24.04'), arm: evidence('ubuntu-24.04-arm')}
    att = {'ATTEMPT': '1'}
    add('w01', 'fpv', env=att, temp_files=both)
    add('w02', 'fpv', env=att, temp_files={x86: both[x86]})
    add('w03', 'fpv', env=att, temp_files=dict(both, **{arm: evidence('ubuntu-24.04-arm', line='FPENV CHECK FAILED: '
                                                                                              '1 of 21 rows failed')}))
    add('w04', 'fpv', env=att, temp_files=dict(both, **{x86: evidence('ubuntu-24.04', attempt='2')}))
    add('w05', 'fpv', env=att, temp_files=dict(both, **{x86: evidence('ubuntu-24.04', line='FPENV CHECK HELD: 25 of '
                                                                                            '26 rows')}))
    add('w06', 'fpv', env=att, temp_files=dict(both, **{'inputs/fpenv/ubuntu-24.04/other.txt': b'x\n'}))
    add('w07', 'fpv', env=att, temp_files=dict(both, **{x86: evidence('ubuntu-24.04', end='\r\n')}))
    add('w08', 'fpv', env=att, temp_files=dict(both, **{'inputs/fpenv/ubuntu-22.04/evidence.txt':
                                                        evidence('ubuntu-22.04')}))

    # PREDICTIONS-workflow_guards-7.txt: the sweep job's step (s01-s12) and the verdict's reading of each sweep leg's
    # evidence (y01-y12), ruling S280-13 (a)
    sv = {'evidence': ('sweep ubuntu-24.04 attempt 1\n%s\n' % SW_HELD).encode('ascii')}
    sw_ok = {'FAKE_SWEEP_OUT': ('  a row ok\n%s\n' % SW_HELD).encode('ascii')}
    tools = ['gcc', 'clang', 'objdump']

    def sw(cid, want, env=None, files=None, compilers=None):
        add(cid, 'sweep', want, env=dict(lg, **(env or {})), files=sw_ok if files is None else files,
            compilers=tools if compilers is None else compilers, shim=SHIM_SW_PYTHON)
    sw('s01', sv)
    sw('s13', sv)
    sw('s14', sv)
    sw('s02', sv, compilers=['clang', 'objdump'])
    sw('s03', sv, compilers=['gcc', 'objdump'])
    sw('s04', sv, compilers=['gcc', 'clang-17', 'clang-18', 'objdump'])
    sw('s05', sv, compilers=['gcc', 'clang'])
    sw('s06', sv, env={'FAKE_SWEEP_EXIT': '1'},
       files={'FAKE_SWEEP_OUT': b'SWEEP CHECK FAILED: 1 of 34 rows failed (fclink; x86-64; gcc, clang)\n'})
    sw('s07', sv, files={'FAKE_SWEEP_OUT': b'SWEEP CHECK FAILED: 1 of 34 rows failed (fclink; x86-64; gcc, clang)\n'})
    sw('s08', sv, files={'FAKE_SWEEP_OUT': ('%s\ndone\n' % SW_HELD).encode('ascii')})
    sw('s09', sv, files={'FAKE_SWEEP_OUT': b'SWEEP CHECK HELD: 19 of 19 rows (fclink; x86-64; gcc)\n'})
    sw('s10', sv, files={'FAKE_SWEEP_OUT': ('%s\r\n' % SW_HELD).encode('ascii')})
    sw('s11', sv, files={'FAKE_SWEEP_OUT': b''})
    sw('s12', {'evidence': ('sweep ubuntu-24.04-arm attempt 1\n%s\n' % SW_HELD_ARM).encode('ascii')},
       env={'LEG': 'ubuntu-24.04-arm'}, files={'FAKE_SWEEP_OUT': ('%s\n' % SW_HELD_ARM).encode('ascii')})

    def sweep_evidence(leg, attempt='1', line=None, end='\n'):
        if line is None:
            line = SW_HELD_ARM if leg.endswith('-arm') else SW_HELD
        return ('sweep %s attempt %s%s%s%s' % (leg, attempt, end, line, end)).encode('ascii')
    sx86, sarm = 'inputs/sweep/ubuntu-24.04/evidence.txt', 'inputs/sweep/ubuntu-24.04-arm/evidence.txt'
    sboth = {sx86: sweep_evidence('ubuntu-24.04'), sarm: sweep_evidence('ubuntu-24.04-arm')}
    add('y01', 'swv', env=att, temp_files=sboth)
    add('y02', 'swv', env=att, temp_files={sx86: sboth[sx86]})
    add('y03', 'swv', env=att, temp_files=dict(sboth, **{sarm: sweep_evidence(
        'ubuntu-24.04-arm', line='SWEEP CHECK FAILED: 1 of 32 rows failed (fclink; aarch64; gcc, clang)')}))
    add('y04', 'swv', env=att, temp_files=dict(sboth, **{sx86: sweep_evidence('ubuntu-24.04', attempt='2')}))
    add('y05', 'swv', env=att, temp_files=dict(sboth, **{sx86: sweep_evidence(
        'ubuntu-24.04', line='SWEEP CHECK HELD: 33 of 34 rows (fclink; x86-64; gcc, clang)')}))
    add('y06', 'swv', env=att, temp_files=dict(sboth, **{'inputs/sweep/ubuntu-24.04/other.txt': b'x\n'}))
    add('y07', 'swv', env=att, temp_files=dict(sboth, **{sx86: sweep_evidence('ubuntu-24.04', end='\r\n')}))
    add('y08', 'swv', env=att, temp_files=dict(sboth, **{'inputs/sweep/ubuntu-22.04/evidence.txt':
                                                         sweep_evidence('ubuntu-22.04')}))
    add('y09', 'swv', env=att, temp_files=dict(sboth, **{sx86: sweep_evidence('ubuntu-24.04', line=SW_HELD_ARM)}))
    add('y10', 'swv', env=att, temp_files=dict(sboth, **{sarm: sweep_evidence(
        'ubuntu-24.04-arm', line=SW_HELD_ARM.replace('(fclink;', '(p1;'))}))
    add('y11', 'swv', env=att, temp_files=dict(sboth, **{sx86: sweep_evidence(
        'ubuntu-24.04', line='SWEEP CHECK HELD: 19 of 19 rows (fclink; x86-64; gcc)')}))
    add('y12', 'swv', env=att, temp_files={sx86: sweep_evidence('ubuntu-24.04', line=SW_HELD.replace('fclink', 'p1')),
                                           sarm: sweep_evidence('ubuntu-24.04-arm',
                                                                line=SW_HELD_ARM.replace('fclink', 'p1'))})
    return out


def leg_lists(text):
    """(the fpenv job's matrix runners, the legs the verdict step reads) from mathkernel-linux.yml's text."""
    m = re.search(r'(?m)^  fpenv:\n(?:    .*\n|\n)*?        runner: \[([^\]\n]*)\]', text)
    runners = [x.strip() for x in m.group(1).split(',')] if m else None
    try:
        block = step_block(text, STEPS['fpv'][1])
    except NotBuilt:
        return runners, None
    m = re.search(r"(?m)^legs = \[([^\]\n]*)\]$", block)
    legs = [x.strip().strip("'") for x in m.group(1).split(',')] if m else None
    return runners, legs


def sweep_leg_lists(text):
    """(the sweep job's matrix runners, the legs and the keys of the machines the verdict's sweep step reads)."""
    m = re.search(r'(?m)^  sweep:\n(?:    .*\n|\n)*?        runner: \[([^\]\n]*)\]', text)
    runners = [x.strip() for x in m.group(1).split(',')] if m else None
    try:
        block = step_block(text, STEPS['swv'][1])
    except NotBuilt:
        return runners, None, None
    m = re.search(r"(?m)^legs = \[([^\]\n]*)\]$", block)
    legs = [x.strip().strip("'") for x in m.group(1).split(',')] if m else None
    m = re.search(r"(?m)^machines = \{([^}\n]*)\}$", block)
    keys = re.findall(r"'([^']*)': '[^']*'", m.group(1)) if m else None
    return runners, legs, keys


def needs_lists(text):
    """(the verdict job's needs: list, sorted; the want list of its first step, as written) from mathkernel-linux.yml's
    text. The step refuses unless the jobs GitHub hands it, sorted, are its want list."""
    m = re.search(r'(?m)^  verdict:\n(?:    .*\n|\n)*?    needs: \[([^\]\n]*)\]', text)
    needs = sorted(x.strip() for x in m.group(1).split(',')) if m else None
    try:
        block = step_block(text, STEPS['needs'][1])
    except NotBuilt:
        return needs, None
    m = re.search(r"(?m)^want = \[([^\]\n]*)\]$", block)
    want = [x.strip().strip("'") for x in m.group(1).split(',')] if m else None
    return needs, want


def main(argv):
    ap = argparse.ArgumentParser(prog='test_workflow_guards.py', allow_abbrev=False, add_help=False,
                                 description='Run the workflows\' inline guards on honest inputs and plants.')
    ap.add_argument('--local', action='store_true', help='a case that needs bash to keep a CR may be NOT RUN')
    ap.add_argument('--bash', help='the bash to run the steps with (default: bash on the PATH)')
    a = ap.parse_args(argv)
    preds, problems = read_predictions()
    results, not_run = [], []
    bash = a.bash or shutil.which('bash')
    why_not = None
    if not bash:
        why_not = 'no bash on the PATH'
    elif os.name == 'nt':
        real = os.path.normcase(os.path.realpath(bash))
        system = os.path.normcase(os.environ.get('SystemRoot', 'C:\\Windows'))
        if real.startswith(system + os.sep) or (os.sep + 'windowsapps' + os.sep) in real:
            why_not = 'the bash on the PATH (%s) is a Windows launcher of another system; give --bash' % real
    tmp = tempfile.mkdtemp(prefix='test-workflow-guards-')
    try:
        if why_not:
            results.append(('bash', False, why_not))
            raise NotBuilt(why_not)
        keeps = cr_probe(bash, tmp)
        print('cr probe: this bash %s a carriage return before the final newline of a command substitution'
              % ('keeps' if keeps else 'drops'))
        ctx = Ctx(tmp, bash)
        for p in ctx.problems:
            results.append(('honest inputs', False, p))
        found = missing_steps(ctx.texts)
        if 'steps' in preds:
            outcome = 'FAIL' if found else 'ok'
            results.append(('steps', outcome == preds['steps'][0], '; '.join(found) if found else
                            '%d steps, each once with a run: block' % len(STEPS)))
        planted = dict(ctx.texts, mk=ctx.texts['mk'].replace(RENAMED[0], RENAMED[1]))
        got = missing_steps(planted) if ctx.texts['mk'].count(RENAMED[0]) == 1 else ['the plant does not apply']
        if 'steps-plant' in preds:
            want = [c[len('missing:'):] for c in preds['steps-plant'][1] if c.startswith('missing:')]
            ok = preds['steps-plant'][0] == ('FAIL' if got else 'ok') and all(any(w in x for x in got) for w in want)
            results.append(('steps-plant', ok, '; '.join(got) if got else 'nothing missing'))
        legs_plant = ctx.texts['mk'].replace('runner: [ubuntu-24.04, ubuntu-24.04-arm]',
                                             'runner: [ubuntu-24.04, ubuntu-24.04-arm, macos-14]')
        for cid, text in (('legs', ctx.texts['mk']), ('legs-plant', legs_plant)):
            if cid in preds:
                runners, legs = leg_lists(text)
                same = runners is not None and legs is not None and runners == legs
                results.append((cid, preds[cid][0] == ('ok' if same else 'FAIL'),
                                'matrix %s; the verdict reads %s' % (runners, legs)))
        at = ctx.texts['mk'].find('\n  sweep:\n')
        honest_runner = 'runner: [ubuntu-24.04, ubuntu-24.04-arm]'
        sweep_plant = (ctx.texts['mk'][:at] + ctx.texts['mk'][at:].replace(
            honest_runner, 'runner: [ubuntu-24.04, ubuntu-24.04-arm, macos-14]', 1)) if at >= 0 else ''
        for cid, text in (('sweep-legs', ctx.texts['mk']), ('sweep-legs-plant', sweep_plant)):
            if cid in preds:
                fp_runners = leg_lists(text)[0]
                runners, legs, keys = sweep_leg_lists(text)
                same = runners is not None and runners == fp_runners == legs and keys is not None \
                    and sorted(keys) == sorted(legs)
                results.append((cid, preds[cid][0] == ('ok' if same else 'FAIL'),
                                'sweep matrix %s; fpenv matrix %s; the verdict reads %s with machines for %s'
                                % (runners, fp_runners, legs, keys)))
        mk = ctx.texts['mk']
        n_old = '    needs: [inventory, fpenv, sweep, image, gate]\n'
        w_old = "want = ['fpenv', 'gate', 'image', 'inventory', 'sweep']"
        needs_cases = (('needs-list', mk, 1),
                       ('needs-list-plant', mk.replace(n_old, n_old.replace('gate]', 'gate, extra]'), 1),
                        mk.count(n_old)),
                       ('needs-list-plant2', mk.replace(w_old, w_old.replace(", 'sweep'", ''), 1), mk.count(w_old)))
        for cid, text, applies in needs_cases:
            if cid in preds:
                if applies != 1:
                    results.append((cid, False, 'the plant does not apply: its text occurs %d times' % applies))
                    continue
                needed, want = needs_lists(text)
                same = needed is not None and want is not None and needed == want
                results.append((cid, preds[cid][0] == ('ok' if same else 'FAIL'),
                                'the verdict job needs %s; its first step wants %s' % (needed, want)))
        for cid, key, kw, want in cases(ctx):
            if cid not in preds:
                results.append((cid, False, 'no prediction'))
                continue
            if 'cr' in preds[cid][1] and not keeps and a.local:
                not_run.append(cid)
                print('  %-12s NOT RUN  %s' % (cid, CR_REASON))
                continue
            try:
                if 'each' in kw:
                    each = [judge(preds[cid], ctx.run(key, env=e), want) for e in kw['each']]
                    held = sum(1 for x in each if x[0])
                    ok = bool(each) and held == len(each)
                    detail = '%d of %d runs as predicted%s' % (held, len(each), ''.join(
                        '; ' + x[1] for x in each if not x[0])[:300])
                else:
                    ok, detail = judge(preds[cid], ctx.run(key, **kw), want)
            except (NotBuilt, OSError, subprocess.TimeoutExpired) as e:
                results.append((cid, False, 'the case could not run: %s' % e))
                continue
            if not ok and 'cr' in preds[cid][1] and not keeps:
                detail += ' (%s)' % CR_REASON
            results.append((cid, ok, '%s: %s' % (key, detail)))
    except NotBuilt:
        pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ran = set(r[0] for r in results) | set(not_run)
    for cid in sorted(set(preds) - ran):
        results.append((cid, False, 'predicted, not run'))
    for p in problems:
        results.append(('predictions', False, p))
    for cid, ok, detail in results:
        print('  %-12s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    failed = sum(1 for r in results if not r[1])
    if failed or not results:
        print('TEST workflow_guards FAILED: %d of %d cases failed' % (failed, len(results)))
        return 1
    print('TEST workflow_guards HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
