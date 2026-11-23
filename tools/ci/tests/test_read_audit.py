# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_read_audit.py: tools/ci/read_audit.py run on small planted trees. Standard library only (Python
# 3.12 or later). It writes in a temporary folder, which it removes; six of its stand-in children each leave an empty
# or small plant-* folder in the system's temporary folder (the --json cases' folders lie inside its own, removed).
#
#   python3 -B tools/ci/tests/test_read_audit.py
#
# Each case builds a tree in a temporary folder: stand-ins at the paths read_audit.py runs
# (tools/ci/tests/run_all.py, kernel/hardening/features/feature_row3.py and feature_row4.py), a freeze list
# kernel/coq/zz/FROZEN4.txt naming zz/A.v, an import manifest MANIFEST.root.txt naming docs/m.md, a judge file
# tools/ci/tests/PREDICTIONS-x.txt (every file under tools/ci is one) and a file README-unbound.md that nothing binds;
# in the eighth file's cases also CHANGES-AFTER-IMPORT.md (as the case writes it), docs/c.md, docs/d.md and
# docs/build/c.md (one text, three files) and PROVENANCE.md;
# and an inventory JSON, a held one naming the gated folder zz unless the case gives another. The stand-in tests read
# the files the case names, from their own process and from a child Python process started as the case says: with
# the environment it was given, without the hook's PYTHONPATH, with -I, after taking PYTHONPATH out of their own
# environment, through os.system or os.spawnv, under another first argument with the interpreter given as the
# program, or with -I after another option's argument (-X utf8, -W ignore); after the fifth review, also after
# os.unsetenv or os.putenv of PYTHONPATH, through a shell (shell=True) with and without -I, with a folder holding
# another sitecustomize put before or after the hook's on PYTHONPATH, after raising a forged "tempfile.mkdtemp" for the
# tree, through a long-path prefix (\\?\ on Windows, a leading "//" on POSIX), with -I after an -X argument holding a
# quote and a blank, with PYTHONHOME changed, and through a link (a junction on Windows, a symbolic link on POSIX) from
# a temporary folder to the tree; after the sixth review, also from a second thread held inside the hook, from a copy
# (shutil.copy2, copytree, copyfile), after a forged log line, after taking the hook's variables out of
# os.environ._data or os.environ, through a hard or symbolic link, after removing or moving what it read, after
# removing a folder (os.rmdir, shutil.rmtree), after importing multiprocessing, after os.fork (or its event), the
# event os.forkpty, a direct _winapi.CreateProcess (or its event), and, as a decoy, links, moves and removals inside a
# new temporary folder; after the seventh review, also through os.spawnv (which forks on POSIX; on Windows the event
# os.fork raised by hand before it), and starting git, a program that is not Python, from the tree's root and, as a
# decoy, from a new temporary folder; the stand-in feature rows read their list and the files the case names. The
# "spawn" children of the fourth review's cases start through os.spawnv on Windows and through os.posix_spawn on POSIX,
# where os.spawnv forks, which the hook refuses; so those cases keep their frozen outcomes on both. In the cases of the
# fifth and sixth reviews the reading process writes the bytes it read (or its mode) to a marker file outside the
# tree, so the case shows the read happened. The real tools/ci/read_audit.py is then run with --root on that tree.
# Cases, one line each, held to tools/ci/tests/PREDICTIONS-read_audit.txt (a01-a08), PREDICTIONS-read_audit-2.txt
# (a09-a21, after the fourth review), PREDICTIONS-read_audit-3.txt (a22-a35, after the fifth),
# PREDICTIONS-read_audit-4.txt (a36-a54, after the sixth), PREDICTIONS-read_audit-5.txt (a55-a57, after the
# seventh) and PREDICTIONS-read_audit-6.txt (a58, a59, after the eighth: --json naming a file inside the tree by
# another spelling, which the audit must refuse as a usage error and not write: on Windows its folder's 8.3 short
# form, or long form where the tree is given short, and a junction outside the tree to it; on POSIX a symbolic link to
# the tree and one to a folder inside it), PREDICTIONS-read_audit-7.txt (a60, after the ninth: an existing --json
# file that is a second name, a hard link, of a file inside the tree, refused as a usage error and not written) and
# PREDICTIONS-read_audit-8.txt (a61-a69, ruling S283-1 (a): a file CHANGES-AFTER-IMPORT.md names on one line with
# its present sha256 and its path in backticks is bound; a file it does not name, though it has a named file's
# bytes, is not, nor is one named with a wrong sha256, with its sha256 on another line, out of backticks, in another
# case, under a folder named build, PROVENANCE.md, or one named in a CHANGES-AFTER-IMPORT.md that is not UTF-8), each
# frozen before its cases first ran, a case named in one of them only:
# the exit code and the rows that
# fail, and for a case of the third to fifth files whether its marker file was written; a case predicted to exit 2 (a
# usage error) must print no row and no verdict.
# What a pass shows: the audit's hook sees the reads of each run and of the processes it starts, holds the bound
# reads and refuses an unbound one, wherever it is read and however its path is written among the ways planted here
# (bound by CHANGES-AFTER-IMPORT.md only as row M3 of tools/check_manifests.py reads it, among the plants here);
# it refuses a process started without the hook, however it was started among the ways planted here, a shell command
# or a change of the environment it cannot judge, a forged temporary folder, a link, removal or move inside the tree,
# an import or start it cannot judge, and a program that is not Python started outside a new temporary folder; it
# refuses an inventory JSON that is not a held inventory naming a gated folder. What it does not show: the audit on
# this repository's own tests (the integrity workflow's step runs it there), or what a process that is not Python
# reads.
# Last line: "TEST read_audit HELD: n of n cases" (exit 0) or "TEST read_audit FAILED: k of n cases failed" (exit 1).
import hashlib
import json
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
AUDIT = os.path.join(ROOT, 'tools', 'ci', 'read_audit.py')
PREDS = (os.path.join(HERE, 'PREDICTIONS-read_audit.txt'), os.path.join(HERE, 'PREDICTIONS-read_audit-2.txt'),
         os.path.join(HERE, 'PREDICTIONS-read_audit-3.txt'), os.path.join(HERE, 'PREDICTIONS-read_audit-4.txt'),
         os.path.join(HERE, 'PREDICTIONS-read_audit-5.txt'), os.path.join(HERE, 'PREDICTIONS-read_audit-6.txt'),
         os.path.join(HERE, 'PREDICTIONS-read_audit-7.txt'), os.path.join(HERE, 'PREDICTIONS-read_audit-8.txt'))
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
ROW_NAMES = {'runs': 'runs: every run ended in its time',
             'hook': 'hook: every process of every run ran under the hook',
             'reads': 'reads: every file read inside the root is bound'}
ROW = re.compile(r'  (.*?\S) +(ok|FAIL)  .*')

# The stand-in tests: read every file of PLANT_READS (";"-separated, relative to the tree), write PLANT_WRITE if set,
# read a file in a temporary folder it makes inside the tree, then start a child Python as PLANT_CHILD says that reads
# PLANT_CHILD_READS: "none"; "inherit" (env None); "bare" (an environment without PYTHONPATH); "isolated" (-I);
# "popped" (PYTHONPATH taken out of the stand-in's own environment, then env None); "system" (os.system, with -I);
# "spawn" and "spawn-isolated" (without and with -I: os.spawnv on Windows, os.posix_spawn on POSIX, where os.spawnv
# forks); "spawnv" (os.spawnv on every system; on Windows, where it does not fork, the event os.fork raised by hand
# before it); "foreign" and "foreign-temporary" (git --version, a program that is not Python, with the hook's
# environment, from the tree's root or from the stand-in's new temporary folder); "renamed" (first argument
# "notpython", the
# interpreter given as the program, -I); "xopt" and "xopt-isolated" (-X utf8, without and with -I after it);
# "wopt-isolated" (-W ignore -I); after the fifth review: "unsetenv" and "putenv" (os.unsetenv("PYTHONPATH") or
# os.putenv("PYTHONPATH", ""), then env None); "putenv-other" (os.environ["PLANT_OTHER"] set, then env None);
# "shell" and "shell-hooked" (shell=True, with and without -I); "shadow" and "shadow-after" (a temporary folder
# holding an empty sitecustomize.py put before or after the hook's folder on PYTHONPATH); "home" (PYTHONHOME set to an
# empty temporary folder: the child cannot start); "xquote" and "xquote-hooked" (-X 'a"b c', with and without -I
# after it); and three in which the stand-in reads PLANT_CHILD_READS itself: "forge" (after
# sys.audit("tempfile.mkdtemp", <the tree>)), "longpath" (through \\?\ on Windows, a leading "//" on POSIX) and
# "alias" (through a junction or symbolic link to the tree, made in a temporary folder of its own). When PLANT_MARK is
# set, the process that read writes what it read (or the mode) there. Then exit PLANT_EXIT.
RUN_ALL = r'''import os, shlex, subprocess, sys, tempfile
def reads(var):
    for rel in [x for x in os.environ.get(var, '').split(';') if x]:
        try:
            with open(rel, 'rb') as fh:
                fh.read()
        except OSError:
            pass
reads('PLANT_READS')
if os.environ.get('PLANT_WRITE'):
    with open(os.environ['PLANT_WRITE'], 'wb') as fh:
        fh.write(b'written\n')
t = tempfile.mkdtemp(prefix='made-', dir='.')
with open(os.path.join(t, 'f.txt'), 'wb') as fh:
    fh.write(b'x\n')
with open(os.path.join(t, 'f.txt'), 'rb') as fh:
    fh.read()
child = os.environ.get('PLANT_CHILD', 'none')
code = "import os\nb = b''\nfor rel in [x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x]:\n" \
       "    b = open(rel, 'rb').read()\nif os.environ.get('PLANT_MARK'):\n" \
       "    open(os.environ['PLANT_MARK'], 'wb').write(b or b'none')\n"
script = os.path.relpath(os.path.join(t, 'child.py'))
with open(script, 'wb') as fh:
    fh.write(code.encode('ascii'))
py = sys.executable
def mark(b):
    if os.environ.get('PLANT_MARK'):
        with open(os.environ['PLANT_MARK'], 'wb') as fh:
            fh.write(b or b'none')
def child_reads():
    got = b''
    for rel in [x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x]:
        with open(rel, 'rb') as fh:
            got += fh.read()
    return got
if child in ('inherit', 'bare', 'isolated'):
    env = dict(os.environ)
    if child == 'bare':
        env.pop('PYTHONPATH', None)
    args = [py, '-B'] + (['-I'] if child == 'isolated' else []) + ['-c', code]
    subprocess.run(args, env=None if child == 'inherit' else env, check=False)
elif child == 'popped':
    os.environ.pop('PYTHONPATH', None)
    subprocess.run([py, '-B', '-c', code], env=None, check=False)
elif child == 'system':
    quote = subprocess.list2cmdline if os.name == 'nt' else (lambda a: ' '.join(shlex.quote(x) for x in a))
    os.system(quote([py, '-B', '-I', script]))
elif child in ('spawn', 'spawn-isolated'):
    argv = [py, '-B'] + (['-I'] if child == 'spawn-isolated' else []) + [script]
    if os.name == 'nt':
        os.spawnv(os.P_WAIT, py, argv)
    else:
        os.waitpid(os.posix_spawn(py, argv, os.environ), 0)
elif child == 'spawnv':
    if os.name == 'nt':
        sys.audit('os.fork')
    os.spawnv(os.P_WAIT, py, [py, '-B', script])
elif child in ('foreign', 'foreign-temporary'):
    try:
        r = subprocess.run(['git', '--version'], cwd=None if child == 'foreign' else t, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode
        mark(('started git: exit %d' % r).encode('ascii'))
    except OSError as e:
        mark(('git did not start: %s' % type(e).__name__).encode('ascii'))
elif child == 'renamed':
    subprocess.run(['notpython', '-B', '-I', '-c', code], executable=py, check=False)
elif child in ('xopt', 'xopt-isolated'):
    subprocess.run([py, '-B', '-X', 'utf8'] + (['-I'] if child == 'xopt-isolated' else []) + ['-c', code],
                   check=False)
elif child == 'wopt-isolated':
    subprocess.run([py, '-B', '-W', 'ignore', '-I', '-c', code], check=False)
elif child in ('unsetenv', 'putenv', 'putenv-other'):
    if child == 'unsetenv':
        os.unsetenv('PYTHONPATH')
    elif child == 'putenv':
        os.putenv('PYTHONPATH', '')
    else:
        os.environ['PLANT_OTHER'] = '1'
    subprocess.run([py, '-B', '-c', code], check=False)
elif child in ('shell', 'shell-hooked'):
    args = [py, '-B'] + (['-I'] if child == 'shell' else []) + [script]
    quote = subprocess.list2cmdline if os.name == 'nt' else (lambda a: ' '.join(shlex.quote(x) for x in a))
    subprocess.run(quote(args), shell=True, check=False)
elif child in ('shadow', 'shadow-after', 'home'):
    d = tempfile.mkdtemp(prefix='plant-')
    env = dict(os.environ)
    if child == 'home':
        env['PYTHONHOME'] = d
    else:
        with open(os.path.join(d, 'sitecustomize.py'), 'wb') as fh:
            fh.write(b'')
        pp = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = (d + os.pathsep + pp) if child == 'shadow' else (pp + os.pathsep + d)
    subprocess.run([py, '-B', '-c', code], env=env, check=False)
elif child in ('xquote', 'xquote-hooked'):
    subprocess.run([py, '-B', '-X', 'a"b c'] + (['-I'] if child == 'xquote' else []) + ['-c', code], check=False)
elif child in ('forge', 'longpath', 'alias'):
    names, link = [x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x], None
    if child == 'forge':
        sys.audit('tempfile.mkdtemp', os.getcwd())
        paths = names
    elif child == 'longpath':
        paths = [('\\\\?\\' if os.name == 'nt' else '/') + os.path.abspath(x) for x in names]
    else:
        d = tempfile.mkdtemp(prefix='plant-')
        link = os.path.join(d, 'link')
        if os.name == 'nt':
            import _winapi
            _winapi.CreateJunction(os.getcwd(), link)
        else:
            os.symlink(os.getcwd(), link)
        paths = [os.path.join(link, x) for x in names]
    for p in paths:
        with open(p, 'rb') as fh:
            fh.read()
    if link is not None:
        (os.rmdir if os.name == 'nt' else os.unlink)(link)
        os.rmdir(os.path.dirname(link))
    if os.environ.get('PLANT_MARK'):
        with open(os.environ['PLANT_MARK'], 'wb') as fh:
            fh.write(child.encode('ascii'))
elif child == 'threads':
    import threading
    inside, release, got = threading.Event(), threading.Event(), []
    class Held:
        def __fspath__(self):
            inside.set()
            release.wait(60)
            return 'docs/m.md'
    th = threading.Thread(target=lambda: sys.audit('open', Held(), 'r', 0))
    th.start()
    inside.wait(60)
    got.append(child_reads())
    release.set()
    th.join()
    mark(b''.join(got))
elif child in ('copy2', 'copyfile', 'copytree'):
    import shutil
    d = tempfile.mkdtemp(prefix='plant-')
    names = [x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x]
    if child == 'copytree':
        shutil.copytree('.', os.path.join(d, 't'))
        paths = [os.path.join(d, 't', x) for x in names]
    else:
        paths = [os.path.join(d, 'c%d' % k) for k in range(len(names))]
        for x, p in zip(names, paths):
            (shutil.copy2 if child == 'copy2' else shutil.copyfile)(x, p)
    got = b''
    for p in paths:
        with open(p, 'rb') as fh:
            got += fh.read()
    mark(got)
elif child in ('forge-log', 'forge-log-existed'):
    line = repr(('mkdtemp', os.getcwd(), child == 'forge-log-existed', os.getcwd())) + '\n'
    for d in [x for x in os.environ.get('MK_READ_AUDIT_DIRS', '').split(os.pathsep) if x]:
        with open(os.path.join(d, 'forged-%d.log' % os.getpid()), 'ab') as fh:
            fh.write(line.encode('utf-8'))
    mark(child_reads())
elif child in ('environ-data', 'environ-pop'):
    for name in ('PYTHONPATH', 'MK_READ_AUDIT_HOOK'):
        if child == 'environ-data':
            os.environ._data.pop(os.environ.encodekey(name), None)
        else:
            os.environ.pop(name, None)
    subprocess.run([py, '-B', '-c', code], env=dict(os.environ), check=False)
elif child in ('link', 'symlink'):
    d = tempfile.mkdtemp(prefix='made-', dir='.')
    got = b''
    for k, x in enumerate([x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x]):
        p = os.path.join(d, 'l%d' % k)
        try:
            (os.link if child == 'link' else os.symlink)(os.path.abspath(x), p)
            with open(p, 'rb') as fh:
                got += fh.read()
        except OSError as e:
            got += ('%s refused by the system: %s' % (child, type(e).__name__)).encode('ascii')
    mark(got)
elif child in ('remove', 'rename'):
    got = child_reads()
    for x in [x for x in os.environ.get('PLANT_CHILD_READS', '').split(';') if x]:
        if child == 'remove':
            os.remove(x)
        else:
            os.rename(x, x + '.moved')
    mark(got)
elif child == 'rmdir':
    os.mkdir('gone')
    os.rmdir('gone')
    mark(b'rmdir')
elif child == 'rmtree':
    import shutil
    os.makedirs(os.path.join('gone', 'sub'))
    with open(os.path.join('gone', 'sub', 'f.txt'), 'wb') as fh:
        fh.write(b'x\n')
    shutil.rmtree('gone')
    mark(b'rmtree')
elif child == 'multiprocessing':
    import multiprocessing
    mark(b'imported ' + multiprocessing.__name__.encode('ascii'))
elif child in ('fork', 'forkpty'):
    if child == 'fork' and hasattr(os, 'fork'):
        pid = os.fork()
        if pid == 0:
            os._exit(0)
        os.waitpid(pid, 0)
        mark(b'fork')
    else:
        sys.audit('os.' + child)
        mark(('the event os.%s raised by hand' % child).encode('ascii'))
elif child == 'createprocess':
    if os.name == 'nt':
        import _winapi
        cmd = subprocess.list2cmdline([py, '-B', '-c', code])
        hp, ht, pid, tid = _winapi.CreateProcess(None, cmd, None, None, False, 0, None, None, subprocess.STARTUPINFO())
        _winapi.WaitForSingleObject(hp, 60000)
        _winapi.CloseHandle(ht)
        _winapi.CloseHandle(hp)
    else:
        sys.audit('_winapi.CreateProcess', None, 'python', None)
        mark(b'the event _winapi.CreateProcess raised by hand')
elif child == 'temporary-changes':
    import shutil
    d = tempfile.mkdtemp(prefix='made-', dir='.')
    a = os.path.join(d, 'a.txt')
    with open(a, 'wb') as fh:
        fh.write(b'a\n')
    try:
        os.link(a, os.path.join(d, 'b.txt'))
        os.rename(os.path.join(d, 'b.txt'), os.path.join(d, 'c.txt'))
        os.remove(os.path.join(d, 'c.txt'))
    except OSError:
        pass
    os.makedirs(os.path.join(d, 'sub', 'deeper'))
    shutil.rmtree(os.path.join(d, 'sub'))
    import concurrent.futures, threading
    mark(b'temporary changes' + child_reads())
print('TEST stand-in HELD: 1 of 1 cases')
sys.exit(int(os.environ.get('PLANT_EXIT', '0')))
'''
FEATURE_ROW = r'''import os, sys
with open(sys.argv[3], 'rb') as fh:
    fh.read()
for rel in [x for x in os.environ.get('PLANT_ROW_READS', '').split(';') if x]:
    with open(rel, 'rb') as fh:
        fh.read()
print('FEATURE ROW (stand-in) HELD: 1 of 1 rows')
'''
BOUND = 'tools/ci/tests/PREDICTIONS-x.txt;kernel/coq/zz/A.v;docs/m.md;absent.txt'
UNBOUND = 'README-unbound.md'
CASES = {
    'a01': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'inherit', 'PLANT_CHILD_READS': 'kernel/coq/zz/FROZEN4.txt'},
    'a02': {'PLANT_READS': BOUND + ';' + UNBOUND, 'PLANT_CHILD': 'none'},
    'a03': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'inherit', 'PLANT_CHILD_READS': UNBOUND},
    'a04': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'bare', 'PLANT_CHILD_READS': UNBOUND},
    'a05': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'isolated', 'PLANT_CHILD_READS': UNBOUND},
    'a06': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none', 'PLANT_ROW_READS': UNBOUND},
    'a07': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none', 'PLANT_WRITE': 'written-unbound.txt'},
    'a08': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'inherit', 'PLANT_CHILD_READS': 'docs/m.md', 'PLANT_EXIT': '1'},
    # after review (PREDICTIONS-read_audit-2.txt)
    'a09': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'popped', 'PLANT_CHILD_READS': UNBOUND},
    'a10': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'system', 'PLANT_CHILD_READS': UNBOUND},
    'a11': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'renamed', 'PLANT_CHILD_READS': UNBOUND},
    'a12': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'xopt-isolated', 'PLANT_CHILD_READS': UNBOUND},
    'a13': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'wopt-isolated', 'PLANT_CHILD_READS': UNBOUND},
    'a14': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'spawn-isolated', 'PLANT_CHILD_READS': UNBOUND},
    'a15': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'spawn', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a16': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'xopt', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a17': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'spawn', 'PLANT_CHILD_READS': UNBOUND},
    'a18': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none'},
    'a19': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none'},
    'a20': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none'},
    'a21': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'none'},
    # after the fifth review (PREDICTIONS-read_audit-3.txt); each writes its marker file
    'a22': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'unsetenv', 'PLANT_CHILD_READS': UNBOUND},
    'a23': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'putenv', 'PLANT_CHILD_READS': UNBOUND},
    'a24': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'shell', 'PLANT_CHILD_READS': UNBOUND},
    'a25': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'shell-hooked', 'PLANT_CHILD_READS': UNBOUND},
    'a26': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'shadow', 'PLANT_CHILD_READS': UNBOUND},
    'a27': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'shadow-after', 'PLANT_CHILD_READS': UNBOUND},
    'a28': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'forge', 'PLANT_CHILD_READS': UNBOUND},
    'a29': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'longpath', 'PLANT_CHILD_READS': UNBOUND},
    'a30': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'xquote', 'PLANT_CHILD_READS': UNBOUND},
    'a31': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'home', 'PLANT_CHILD_READS': UNBOUND},
    'a32': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'alias', 'PLANT_CHILD_READS': UNBOUND},
    'a33': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'shadow-after', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a34': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'putenv-other', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a35': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'xquote-hooked', 'PLANT_CHILD_READS': 'docs/m.md'},
    # after the sixth review (PREDICTIONS-read_audit-4.txt); each writes its marker file
    'a36': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'threads', 'PLANT_CHILD_READS': UNBOUND},
    'a37': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'copy2', 'PLANT_CHILD_READS': UNBOUND},
    'a38': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'copytree', 'PLANT_CHILD_READS': UNBOUND},
    'a39': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'copyfile', 'PLANT_CHILD_READS': UNBOUND},
    'a40': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'forge-log', 'PLANT_CHILD_READS': UNBOUND},
    'a41': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'forge-log-existed', 'PLANT_CHILD_READS': UNBOUND},
    'a42': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'environ-data', 'PLANT_CHILD_READS': UNBOUND},
    'a43': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'environ-pop', 'PLANT_CHILD_READS': UNBOUND},
    'a44': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'link', 'PLANT_CHILD_READS': UNBOUND},
    'a45': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'symlink', 'PLANT_CHILD_READS': UNBOUND},
    'a46': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'remove', 'PLANT_CHILD_READS': UNBOUND},
    'a47': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'rename', 'PLANT_CHILD_READS': UNBOUND},
    'a48': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'rmdir'},
    'a49': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'rmtree'},
    'a50': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'multiprocessing'},
    'a51': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'fork'},
    'a52': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'forkpty'},
    'a53': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'createprocess', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a54': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'temporary-changes', 'PLANT_CHILD_READS': 'docs/m.md'},
    # after the seventh review (PREDICTIONS-read_audit-5.txt); each writes its marker file
    'a55': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'spawnv', 'PLANT_CHILD_READS': 'docs/m.md'},
    'a56': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'foreign'},
    'a57': {'PLANT_READS': BOUND, 'PLANT_CHILD': 'foreign-temporary'},
    # after the eighth review (PREDICTIONS-read_audit-6.txt): --json inside the tree by another spelling
    'a58': {'PLANT_READS': BOUND},
    'a59': {'PLANT_READS': BOUND},
    # after the ninth review (PREDICTIONS-read_audit-7.txt): --json a hard link to a file inside the tree
    'a60': {'PLANT_READS': BOUND},
    # ruling S283-1 (a) (PREDICTIONS-read_audit-8.txt): a file CHANGES-AFTER-IMPORT.md names (NAMED below)
    'a61': {'PLANT_READS': BOUND + ';docs/c.md'},
    'a62': {'PLANT_READS': BOUND + ';docs/c.md'},
    'a63': {'PLANT_READS': BOUND + ';docs/d.md'},
    'a64': {'PLANT_READS': BOUND + ';docs/c.md'},
    'a65': {'PLANT_READS': BOUND + ';docs/c.md'},
    'a66': {'PLANT_READS': BOUND + ';PROVENANCE.md'},
    'a67': {'PLANT_READS': BOUND + ';docs/c.md'},
    'a68': {'PLANT_READS': BOUND + ';docs/build/c.md'},
    'a69': {'PLANT_READS': BOUND + ';docs/c.md'},
}
# The eighth file's cases: the text of CHANGES-AFTER-IMPORT.md each writes, beside docs/c.md, docs/d.md and
# docs/build/c.md (the bytes C_TEXT, whose sha256 is C_SHA) and PROVENANCE.md.
C_TEXT = b'a file of the tree added after the import\n'
C_SHA = hashlib.sha256(C_TEXT).hexdigest()
PROVENANCE = b'the import and its manifests\n'
NAMED = {
    'a61': ('| `docs/c.md` | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a62': ('| `docs/c.md` | (new) | %s |\n' % hashlib.sha256(b'other bytes\n').hexdigest()).encode('ascii'),
    'a63': ('| `docs/c.md` | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a64': ('| `docs/c.md` | (new) |\n| the file above | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a65': ('| docs/c.md | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a66': ('| `PROVENANCE.md` | (new) | %s |\n' % hashlib.sha256(PROVENANCE).hexdigest()).encode('ascii'),
    'a67': ('| `docs/C.md` | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a68': ('| `docs/build/c.md` | (new) | %s |\n' % C_SHA).encode('ascii'),
    'a69': ('| `docs/c.md` | (new) | %s |\n' % C_SHA).encode('ascii') + b'\xff\n',
}
# The cases whose reading process writes a marker file, and whether it must exist after the run (a31's child cannot
# start, so it writes none).
MARKED = dict(('a%d' % k, k != 31) for k in range(22, 58))
HELD_INVENTORY = {'schema': 'skuldd-inventory/1', 'held': True, 'gated': [{'folder': 'zz'}], 'mirrors': []}
INVENTORIES = {
    'a18': {},
    'a19': dict(HELD_INVENTORY, held=False),
    'a20': dict(HELD_INVENTORY, gated=[]),
    'a21': dict(HELD_INVENTORY, gated=[{'folder': 'zz'}, {'folder': '../zz'}]),
}


def other_form(t):
    """The folder t spelled otherwise, and the folder inside t it names: on Windows its 8.3 short form (or its long
    form, when t is given short), None when the two are one; on POSIX a symbolic link beside t to t."""
    if os.name != 'nt':
        link = t + '-link'
        os.symlink(t, link, target_is_directory=True)
        return link, t
    import ctypes
    buf = ctypes.create_unicode_buffer(1024)
    n = ctypes.windll.kernel32.GetLongPathNameW(t, buf, 1024)
    long_form = buf.value if 0 < n < 1024 else t
    n = ctypes.windll.kernel32.GetShortPathNameW(t, buf, 1024)
    short_form = buf.value if 0 < n < 1024 else t
    for form in (short_form, long_form):
        if os.path.normcase(form) != os.path.normcase(t):
            return form, t
    return None, t


def linked_form(t):
    """A linked folder outside t naming a folder inside the tree: on Windows a junction beside t to t, on POSIX a
    symbolic link beside t to t's kernel folder."""
    link = t + '-junction'
    if os.name == 'nt':
        import _winapi
        _winapi.CreateJunction(t, link)
        return link, t
    os.symlink(os.path.join(t, 'kernel'), link, target_is_directory=True)
    return link, os.path.join(t, 'kernel')


def hard_link_form(t):
    """A folder beside t holding audit.json, a second name (a hard link) of t's docs/m.md, and None for the folder
    inside t: the test checks instead that docs/m.md keeps its bytes."""
    link_dir = t + '-hardlink'
    os.makedirs(link_dir)
    os.link(os.path.join(t, 'docs', 'm.md'), os.path.join(link_dir, 'audit.json'))
    return link_dir, None


JSON_INSIDE = {'a58': other_form, 'a59': linked_form, 'a60': hard_link_form}


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def tree(t):
    a = b'(* zz *)\n'
    wb(os.path.join(t, 'tools', 'ci', 'tests', 'run_all.py'), RUN_ALL.encode('ascii'))
    wb(os.path.join(t, 'tools', 'ci', 'tests', 'PREDICTIONS-x.txt'), b'a judge file\n')
    for row in ('feature_row3.py', 'feature_row4.py'):
        wb(os.path.join(t, 'kernel', 'hardening', 'features', row), FEATURE_ROW.encode('ascii'))
    wb(os.path.join(t, 'kernel', 'coq', 'zz', 'A.v'), a)
    wb(os.path.join(t, 'kernel', 'coq', 'zz', 'FROZEN4.txt'),
       ('%s  zz/A.v\n' % hashlib.sha256(a).hexdigest()).encode('ascii'))
    m = b'a manifest-listed file\n'
    wb(os.path.join(t, 'docs', 'm.md'), m)
    wb(os.path.join(t, 'MANIFEST.root.txt'), ('%s  docs/m.md\n' % hashlib.sha256(m).hexdigest()).encode('ascii'))
    wb(os.path.join(t, 'README-unbound.md'), b'bound by nothing\n')


def named_tree(t, cid):
    """The eighth file's additions to the tree of case cid."""
    for rel in ('docs/c.md', 'docs/d.md', 'docs/build/c.md'):
        wb(os.path.join(t, *rel.split('/')), C_TEXT)
    wb(os.path.join(t, 'PROVENANCE.md'), PROVENANCE)
    wb(os.path.join(t, 'CHANGES-AFTER-IMPORT.md'), NAMED[cid])


def predictions():
    """{case: (exit, set of failing row keys)}, problems. A line: "case | exit <n> | <rows or -> | what"."""
    # (the marker each case of MARKED writes, or does not, is said in the third file's "what" and checked in main)
    preds, probs = {}, []
    for path in PREDS:
        with open(path, 'rb') as fh:
            for n, line in enumerate(fh.read().decode('utf-8').split('\n'), 1):
                if not line or line.startswith('#'):
                    continue
                parts = line.split(' | ')
                m = re.fullmatch(r'exit (\d)', parts[1]) if len(parts) == 4 else None
                rows = None if len(parts) != 4 else set() if parts[2] == '-' else set(parts[2].split(','))
                if not m or parts[0] in preds or rows is None or not rows <= set(ROW_NAMES):
                    probs.append('%s line %d is not "case | exit <n> | rows | what", or names a case twice'
                                 % (os.path.basename(path), n))
                    continue
                preds[parts[0]] = (int(m.group(1)), rows)
    return preds, probs


def main():
    preds, probs = predictions()
    results = [('predictions', not probs and set(preds) == set(CASES),
                '; '.join(probs) if probs else '%d cases, each predicted' % len(preds) if set(preds) == set(CASES)
                else 'defined %s; predicted %s' % (sorted(CASES), sorted(preds)))]
    tmp = tempfile.mkdtemp(prefix='test-read-audit-')
    try:
        for cid in sorted(CASES):
            t = os.path.join(tmp, cid)
            tree(t)
            if cid in NAMED:
                named_tree(t, cid)
            inv = os.path.join(tmp, cid + '-inventory.json')
            wb(inv, json.dumps(INVENTORIES.get(cid, HELD_INVENTORY)).encode('ascii'))
            env = dict(ENV, **CASES[cid])
            mark = os.path.join(tmp, cid + '-mark.txt')
            if cid in MARKED:
                env['PLANT_MARK'] = mark
            extra, inside = [], None
            if cid in JSON_INSIDE:
                given, where = JSON_INSIDE[cid](t)
                if given is None:
                    results.append((cid, False, 'the folder %s has one spelling only here; the case cannot be built'
                                    % t))
                    continue
                extra = ['--json', os.path.join(given, 'audit.json')]
                inside = os.path.join(where, 'audit.json') if where is not None else None
            p = subprocess.run([sys.executable, '-B', AUDIT, '--root', t, '--inventory-json', inv] + extra, env=env,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
            marked = os.path.isfile(mark) and os.path.getsize(mark) > 0
            out = p.stdout.decode('utf-8', 'replace').replace('\r', '')
            failing = set(k for k, name in ROW_NAMES.items() for m in (ROW.fullmatch(x) for x in out.split('\n'))
                          if m and m.group(1) == name and m.group(2) == 'FAIL')
            got_rows = set(m.group(1) for m in (ROW.fullmatch(x) for x in out.split('\n')) if m)
            last = [x for x in out.split('\n') if x.strip()][-1:] or ['']
            want = preds.get(cid)
            if want is not None and want[0] == 2:
                ok = (p.returncode == 2 and not got_rows and not want[1]
                      and not any(x.startswith('READ AUDIT ') for x in out.split('\n')))
            else:
                ok = (want is not None and p.returncode == want[0] and failing == want[1]
                      and got_rows == set(ROW_NAMES.values()))
            if cid in MARKED:
                ok = ok and marked == MARKED[cid]
            if inside is not None and os.path.lexists(inside):
                ok = False
                out += '\n--json FAIL written inside the tree'
            if cid == 'a60':
                with open(os.path.join(t, 'docs', 'm.md'), 'rb') as fh:
                    if fh.read() != b'a manifest-listed file\n':
                        ok = False
                        out += '\n--json FAIL written into docs/m.md through its other name'
            fails = ' / '.join(x for x in out.split('\n') if ' FAIL ' in x)[:300]
            results.append((cid, ok, 'exit %d; failing %s; %s%s%s' % (
                p.returncode, ','.join(sorted(failing)) or '-', last[0][:80],
                '' if cid not in MARKED else '; marker %s' % ('written' if marked else 'absent'),
                '' if ok else '; NOT AS PREDICTED: ' + fails)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for cid, ok, detail in results:
        print('  %-12s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    k = sum(1 for r in results if not r[1])
    if k:
        print('TEST read_audit FAILED: %d of %d cases failed' % (k, len(results)))
        return 1
    print('TEST read_audit HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
