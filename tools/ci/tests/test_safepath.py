# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_safepath.py: the PYTHONSAFEPATH guard of the three workflows (integrity.yml,
# mathkernel-linux.yml and drift.yml), seen to stop a planted module, with a control that shows the plant takes
# effect without it. Standard library only (Python 3.12 or later). It writes only in a temporary folder, which it
# removes.
#
#   python3 -B tools/ci/tests/test_safepath.py
#
# Python puts a script's own folder first on its import path, and for a script read from stdin the current folder.
# So a file named like a standard module (re.py, json.py) beside a script that CI runs, or at the top of the checkout
# for the workflows' inline steps (run as "python3 -B -" from the checkout's top), would be imported in place of the
# standard one. With PYTHONSAFEPATH=1 (Python 3.11 and later) neither folder is put on the path. Cases, one line each,
# held to tools/ci/tests/PREDICTIONS-safepath.txt, PREDICTIONS-safepath-2.txt and PREDICTIONS-safepath-3.txt (the
# third workflow, drift.yml; each frozen before its first run;
# a line of a later file whose outcome is "retired" takes out the case an earlier file predicts, and no other line of
# a later file may name a case an earlier one names):
#   premise       a script run by this interpreter finds neither re nor json loaded before it runs; a module already
#                 loaded cannot be shadowed, and the controls below would then not take
#   F0, F1, F2    a copy of kernel/hardening/features/feature_row4.py on two plants it refuses: alone (FAILED);
#                 with a planted re.py beside it and PYTHONSAFEPATH removed (the control: HELD, the plant took
#                 effect); with the same re.py and PYTHONSAFEPATH=1 (FAILED, the honest verdict)
#   V3, V4, V5    the script of the verdict job's first step, read from .github/workflows/mathkernel-linux.yml and run
#                 from stdin as the step runs it, with fpenv failed and the four other jobs (inventory, sweep, image,
#                 gate) succeeded: alone (REFUSED); with a planted json.py in the current folder and PYTHONSAFEPATH
#                 removed (the control: it passes); with json.py and PYTHONSAFEPATH=1 (REFUSED). V0, V1 and V2, the
#                 same runs before the sweep job (four jobs), are retired by the second file
#   W0            integrity.yml and mathkernel-linux.yml set PYTHONSAFEPATH "1" in their top-level env, and every
#                 docker run whose command starts Python (python3, the toolchain probe, the gate, a feature row)
#                 passes -e PYTHONSAFEPATH
#   W1, W2        that check seen to fail: a copy of mathkernel-linux.yml without one -e PYTHONSAFEPATH, and a copy of
#                 integrity.yml without its env line
#   W3, W4        the same check on drift.yml (no docker run there), and seen to fail on a copy without its env line
# A case holds when its exit code (or ok/FAIL) and its text are as predicted.
# What a pass shows: on this interpreter, the guard keeps a module planted beside a checker, or in the current folder of
# an inline step, from being imported, and the workflows set it where Python runs. What it does not show: the image's
# Python (3.12 there; the variable is read by every Python since 3.11, ARGUED) or the runner's; a module planted in a
# folder that is on the path anyway (site-packages, the standard library); a script that changes sys.path itself.
# Last line: "TEST safepath HELD: n of n cases" (exit 0) or "TEST safepath FAILED: k of n cases failed" (exit 1).
import os
import re
import shutil
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
PRED = (os.path.join(HERE, 'PREDICTIONS-safepath.txt'), os.path.join(HERE, 'PREDICTIONS-safepath-2.txt'),
        os.path.join(HERE, 'PREDICTIONS-safepath-3.txt'))
ROW4 = os.path.join(ROOT, 'kernel', 'hardening', 'features', 'feature_row4.py')
PLANTS4 = os.path.join(ROOT, 'kernel', 'hardening', 'features', 'plants4')
PLANT_FILES = ('refuse4_conjectures.v', 'refuse4_admit_obligations.v')
WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'mathkernel-linux.yml')
INTEGRITY = os.path.join(ROOT, '.github', 'workflows', 'integrity.yml')
DRIFT = os.path.join(ROOT, '.github', 'workflows', 'drift.yml')
VERDICT_STEP = '- name: Every other job of this run succeeded'
NEEDS = '{"fpenv": {"result": "failure"}, "gate": {"result": "success"}, "image": {"result": "success"}, ' \
        '"inventory": {"result": "success"}, "sweep": {"result": "success"}}'
V_CASES = (('V3-honest', False, False), ('V4-control', True, False), ('V5-guarded', True, True))

# The planted modules. Each loads the standard module from the standard library's own folder and changes one thing.
LOAD_REAL = '''import importlib.util
import os
import sys
import sysconfig
_path = os.path.join(sysconfig.get_paths()['stdlib'], %(name)r, '__init__.py')
_spec = importlib.util.spec_from_file_location(%(name)r, _path, submodule_search_locations=[os.path.dirname(_path)])
_real = importlib.util.module_from_spec(_spec)
sys.modules[%(name)r] = _real
_spec.loader.exec_module(_real)
'''
SHADOW_RE = LOAD_REAL % {'name': 're'} + '''
def _nothing(pattern, string, flags=0):
    return iter(())
_real.finditer = _nothing
'''
SHADOW_JSON = LOAD_REAL % {'name': 'json'} + '''
_loads = _real.loads
def _all_success(s, *a, **k):
    v = _loads(s, *a, **k)
    if isinstance(v, dict):
        for x in v.values():
            if isinstance(x, dict) and 'result' in x:
                x['result'] = 'success'
    return v
_real.loads = _all_success
'''
PREMISE = 'import sys\nhit = [m for m in ("re", "json") if m in sys.modules]\n' \
          'print("preloaded before a script: %s" % (", ".join(hit) or "none"))\n'


def rb(path):
    with open(path, 'rb') as f:
        return f.read()


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def read_predictions():
    preds, problems, retired = {}, [], set()
    for i, path in enumerate(PRED):
        name = os.path.basename(path)
        earlier = set(preds) | retired
        for n, line in enumerate(rb(path).decode('utf-8').split('\n'), 1):
            if not line or line.startswith('#'):
                continue
            parts = line.split(' | ')
            if len(parts) == 4 and parts[1] == 'retired' and i > 0 and parts[0] in preds and parts[0] in earlier:
                del preds[parts[0]]
                retired.add(parts[0])
                continue
            if len(parts) != 4 or parts[0] in preds or parts[0] in retired or parts[1] == 'retired':
                problems.append('%s line %d is not "case | outcome | text | what", repeats a case or retires none'
                                % (name, n))
                continue
            preds[parts[0]] = (parts[1], parts[2])
    return preds, problems


def env(safe):
    e = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    for k in ('PYTHONSAFEPATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP'):
        e.pop(k, None)
    if os.environ.get('MK_READ_AUDIT_HOOK'):
        # under tools/ci/read_audit.py: its hook's folder (one sitecustomize.py, which imports only os and sys) stays
        # on the path, after the script's folder, so the audit sees these runs too
        e['PYTHONPATH'] = os.environ['MK_READ_AUDIT_HOOK']
    if safe:
        e['PYTHONSAFEPATH'] = '1'
    return e


def run(args, cwd, safe, stdin=None):
    """(exit code, stdout lines, stdout and stderr lines) of python -B args (never -I or -P: the variable decides)."""
    p = subprocess.run([sys.executable, '-B'] + args, cwd=cwd, env=env(safe), input=stdin, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=300)
    out = [x.rstrip('\r') for x in p.stdout.decode('utf-8', 'replace').split('\n') if x.strip()]
    err = [x.rstrip('\r') for x in p.stderr.decode('utf-8', 'replace').split('\n') if x.strip()]
    return p.returncode, out, out + err


def verdict_script():
    """The script of the verdict job's first step, as the runner gives it to python3 on stdin."""
    lines = rb(WORKFLOW).decode('utf-8').split('\n')
    at = [i for i, x in enumerate(lines) if x.strip() == VERDICT_STEP]
    if len(at) != 1:
        raise ValueError('%d steps named "%s"' % (len(at), VERDICT_STEP[len('- name: '):]))
    start = [i for i in range(at[0], len(lines)) if lines[i].strip() == "python3 -B - <<'EOF'"]
    if not start:
        raise ValueError('the step has no "python3 -B - <<\'EOF\'"')
    end = [i for i in range(start[0] + 1, len(lines)) if lines[i].strip() == 'EOF']
    if not end:
        raise ValueError('the step\'s script has no EOF line')
    body = lines[start[0] + 1:end[0]]
    pad = min(len(x) - len(x.lstrip(' ')) for x in body if x.strip())
    return ''.join(x[pad:] + '\n' for x in body).encode('utf-8')


def workflow_problems(name, text):
    """What the workflow text lacks: its top-level env's PYTHONSAFEPATH "1", and -e PYTHONSAFEPATH on each docker run
    whose command starts Python."""
    lines = text.split('\n')
    problems = []
    env_at = [i for i, x in enumerate(lines) if x == 'env:']
    block = []
    if len(env_at) == 1:
        for x in lines[env_at[0] + 1:]:
            if x and not x.startswith(' ') and not x.startswith('#'):
                break
            block.append(x.strip())
    if 'PYTHONSAFEPATH: "1"' not in block:
        problems.append('%s: no top-level PYTHONSAFEPATH: "1" in its env' % name)
    i = 0
    while i < len(lines):
        if 'docker run ' in lines[i]:
            first, cmd = i, lines[i]
            while cmd.rstrip().endswith('\\') and i + 1 < len(lines):
                i += 1
                cmd = cmd.rstrip()[:-1] + ' ' + lines[i].strip()
            starts = re.search(r'python3|toolchain_probe\.sh|gate4\.py|feature_row', cmd)
            if starts and not re.search(r'(^|\s)-e PYTHONSAFEPATH(\s|$)', cmd):
                problems.append('%s line %d: a docker run that starts Python without -e PYTHONSAFEPATH'
                                % (name, first + 1))
        i += 1
    return problems


def main():
    preds, problems = read_predictions()
    results = []

    def case(cid, got_outcome, got_text_ok, detail):
        if cid not in preds:
            results.append((cid, False, 'no prediction'))
            return
        want, text = preds[cid]
        ok = got_outcome == want and got_text_ok(text)
        results.append((cid, ok, '%s; predicted %s, "%s"' % (detail, want, text)))

    tmp = tempfile.mkdtemp(prefix='test-safepath-')
    try:
        # premise
        p = os.path.join(tmp, 'premise', 'premise.py')
        wb(p, PREMISE.encode('utf-8'))
        rc, out, both = run([p], tmp, safe=False)
        case('premise', str(rc), lambda t: t in out, 'exit %d: %s' % (rc, out[-1] if out else 'no output'))

        # F: the feature row beside a planted re.py
        for cid, shadow, safe in (('F0-honest', False, False), ('F1-control', True, False),
                                  ('F2-guarded', True, True)):
            d = os.path.join(tmp, cid)
            script = os.path.join(d, 'checker', 'feature_row4.py')
            wb(script, rb(ROW4))
            for f in PLANT_FILES:
                wb(os.path.join(d, 'root', f), rb(os.path.join(PLANTS4, f)))
            if shadow:
                wb(os.path.join(d, 'checker', 're.py'), SHADOW_RE.encode('utf-8'))
            os.makedirs(os.path.join(d, 'cwd'))
            rc, out, both = run([script, os.path.join(d, 'root')] + list(PLANT_FILES), os.path.join(d, 'cwd'), safe)
            last = out[-1] if out else ''
            case(cid, str(rc), lambda t, last=last: t == last, 'exit %d, last line "%s"' % (rc, last))

        # V: the verdict step's script from stdin, a planted json.py in the current folder
        try:
            vs = verdict_script()
        except (OSError, ValueError) as e:
            vs = None
            for cid, _, _ in V_CASES:
                results.append((cid, False, 'the step\'s script cannot be read: %s' % e))
        if vs is not None:
            for cid, shadow, safe in V_CASES:
                d = os.path.join(tmp, cid)
                os.makedirs(d)
                if shadow:
                    wb(os.path.join(d, 'json.py'), SHADOW_JSON.encode('utf-8'))
                e = env(safe)
                e['NEEDS'] = NEEDS
                p = subprocess.run([sys.executable, '-B', '-'], cwd=d, env=e, input=vs, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, timeout=300)
                both = [x.rstrip('\r') for x in (p.stdout + b'\n' + p.stderr).decode('utf-8', 'replace').split('\n')
                        if x.strip()]
                case(cid, str(p.returncode), lambda t, both=both: t in both,
                     'exit %d, %s' % (p.returncode, 'REFUSED' if any(x.startswith('REFUSED') for x in both)
                                      else 'no REFUSED line'))

        # W: the workflow files
        texts = {}
        for path in (WORKFLOW, INTEGRITY):
            texts[os.path.basename(path)] = rb(path).decode('utf-8')
        found = []
        for name in sorted(texts):
            found += workflow_problems(name, texts[name])
        case('W0-workflows', 'FAIL' if found else 'ok', lambda t: True,
             '; '.join(found) if found else 'both set it at the top; every docker run that starts Python passes it')
        plants = {
            'W1-plant-docker': ('mathkernel-linux.yml', '-e PYTHONSAFEPATH -v "$GITHUB_WORKSPACE/kernel/coq:/work"',
                                '-v "$GITHUB_WORKSPACE/kernel/coq:/work"'),
            'W2-plant-env': ('integrity.yml', '\n  PYTHONSAFEPATH: "1"\n', '\n'),
        }
        for cid, (name, old, new) in sorted(plants.items()):
            t = texts[name]
            if t.count(old) != 1:
                results.append((cid, False, 'the plant does not apply: its text occurs %d times' % t.count(old)))
                continue
            got = workflow_problems(name, t.replace(old, new))
            case(cid, 'FAIL' if got else 'ok', lambda t, got=got: bool(got) and all(t in g for g in got),
                 '; '.join(got) if got else 'no problem found')

        # W3, W4: the third workflow, drift.yml, with the same check
        dt = rb(DRIFT).decode('utf-8')
        got = workflow_problems('drift.yml', dt)
        case('W3-drift', 'FAIL' if got else 'ok', lambda t: True,
             '; '.join(got) if got else 'it sets it at the top; no docker run there starts Python without it')
        old = '\n  PYTHONSAFEPATH: "1"\n'
        if dt.count(old) != 1:
            results.append(('W4-plant-drift', False, 'the plant does not apply: its text occurs %d times'
                            % dt.count(old)))
        else:
            got = workflow_problems('drift.yml', dt.replace(old, '\n'))
            case('W4-plant-drift', 'FAIL' if got else 'ok', lambda t, got=got: bool(got) and all(t in g for g in got),
                 '; '.join(got) if got else 'no problem found')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for cid in sorted(set(preds) - set(r[0] for r in results)):
        results.append((cid, False, 'predicted, not run'))
    for p in problems:
        results.append(('predictions', False, p))
    for cid, ok, det in results:
        print('  %-16s %s  %s' % (cid, 'ok' if ok else 'FAIL', det))
    failed = sum(1 for r in results if not r[1])
    if failed:
        print('TEST safepath FAILED: %d of %d cases failed' % (failed, len(results)))
        return 1
    print('TEST safepath HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
