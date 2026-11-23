# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/read_audit.py: every file that the Python processes of the tests of tools/ci (in their CI form) and of the
# feature-row runs read inside the checkout is bound to the CI judge, to a freeze list, to an import manifest or to a
# line of CHANGES-AFTER-IMPORT.md that names it with its present sha256.
# Standard library only (Python 3.12 or later). It writes only in a temporary folder outside ROOT, which it removes,
# and the file --json names.
#
#   python3 -B tools/ci/read_audit.py --root ROOT --inventory-json F [--json OUT]
#
# It runs, from ROOT, each with the environment it was given and its own variables:
#   - tools/ci/tests/run_all.py with no option (the CI form);
#   - kernel/hardening/features/feature_row3.py and feature_row4.py, "<base> --list <base>/<f>/FROZEN4.txt", on every
#     freeze list the inventory JSON (tools/ci/inventory.py's) names: kernel/coq for each gated folder,
#     verdandi/mathkernel/F32 for each of Verdandi's copies; standard input empty.
# Every Python process of those runs that is started with the hook's variables (each run, and every process it starts
# that the hook judges as keeping them, at any depth) loads an audit hook (sys.addaudithook) from a sitecustomize
# module that this script writes into its temporary folder and puts first on PYTHONPATH. The hook imports nothing but
# os, sys and _thread (sys and _thread built into the interpreter, os already loaded by site before sitecustomize, so
# it loads no module that a test plants), and writes one line per event to a log file of its own (a thread's events
# inside the hook are not logged; another thread's are): its process's start, with its run's number; each file opened
# (the audit event "open": its path, whether it is opened for reading, and for a read the path with its links,
# junctions and short names resolved in that process); each copy's source, as a read (the events "_winapi.CopyFile2",
# through which shutil.copy2 and copytree read on Windows, "shutil.copyfile", "shutil.copymode", "shutil.copystat" and
# "shutil.copytree"); each link ("os.link", "os.symlink", "_winapi.CreateJunction": both its ends), removal
# ("os.remove", which os.unlink raises too, "os.rmdir", "shutil.rmtree") and move ("os.rename", which os.replace raises
# too: both its ends), a path given against a folder's descriptor read through /proc/self/fd; each process started
# (the events "subprocess.Popen", "os.posix_spawn", "os.exec" and "os.spawn"): whether it keeps the hook, whether it
# is a Python run, and the folder it starts in; and, as starts it cannot judge,
# each import of multiprocessing or one of its submodules or of concurrent.futures.process, each "os.fork" and
# "os.forkpty", and each "_winapi.CreateProcess" that is not the one subprocess.Popen makes right after its own event,
# in the same thread, with the same program and folder (multiprocessing's start on Windows makes such a call). It
# keeps the hook when the environment it is given (or this process's own, when none is given) holds the hook's log
# folders, has the hook's folder first on PYTHONPATH (a sitecustomize earlier on it would be imported instead) and
# leaves PYTHONHOME unset or as this process's (the folder and PYTHONHOME are the ones the process had when the hook
# loaded, and the folder must not be empty; on Windows, names compared in capitals, and two spellings of one of those
# names are not kept), and it is no Python run given -I, -E or -S. A shell given a
# command (a POSIX shell with -c, alone or among other short options; the Windows command interpreter, cmd or the
# program ComSpec names, with /c, /k or /r: subprocess's shell=True), a command line it cannot split, and each shell
# command or file started by "os.system" or "os.startfile", are logged as processes the hook cannot judge; so is each
# change, through "os.putenv" or "os.unsetenv", to PYTHONPATH, PYTHONHOME or a variable whose name starts with
# MK_READ_AUDIT_, which the processes this one starts may inherit while os.environ does not show it. Each temporary
# folder made is logged (the event "tempfile.mkdtemp", which CPython raises before it makes the folder), with whether
# its path existed already. A process is a Python run when the base name of its program or of its first argument
# starts with "python" or is "py", or its program is this interpreter; its options are read as CPython reads them
# (several in one word; -X and -W take an argument, in the same word or the next; -c, -m, "-", "--" or a script end
# them); a command line given as one string (Windows) is split as Windows' C runtime splits one (2n backslashes before
# a quote are n and the quote opens or closes quoting, 2n+1 are n and a literal quote; "" inside quotes, which the
# runtimes read differently, is a line it cannot split). The variables name a list of log folders, so an audit run
# inside another (a test of this script) logs to both.
# Rows, one line each, "  <row> ok|FAIL  <detail>":
#   runs     every run ended within its time, TIMEOUT (5400 seconds) each (each run's exit code and last line are
#            shown: the tests' and the feature rows' own steps judge those). The longest run, the tests in their CI form
#            under the hook, took about 26 minutes alone on one Windows host and about 72 under heavy outside load; a
#            limit that stops an honest run turns this row red with no defect in the tree, so it stands at more than
#            three times the time alone.
#   hook     every run's first process logged its start (matched by its process id and its run's number), and every
#            process a run started kept the hook, and none is a start, a change or an import the hook cannot judge,
#            and no program that is not Python was started given the hook's environment (the hook runs in no such
#            program, so what it reads would not be seen; without that environment it is a process started without
#            the hook); a process started, or an import made, in a new temporary folder that a run made (a test's own
#            fixture, which runs this script on a planted tree) is not judged here. A temporary folder logged whose path
#            existed before (an event raised by hand) exempts nothing; one that is the root, holds the root or holds a
#            bound file exempts nothing and fails this row, whatever its "existed" field says (a line written into the
#            log by hand). Its detail counts the process starts logged (distinct process id and run, which a reused
#            process id lowers) and the processes started: given the hook's environment (and of them the programs that
#            are not Python, each in a run's temporary folder), and in a run's temporary folder without it (not
#            judged).
#   reads    every file inside ROOT that a run opened for reading, and that is a file now, is bound: a judge file (the
#            groups of tools/ci/judge_digest.py beside this script, found in ROOT), a freeze list the inventory JSON
#            names or a file such a list names, a file that an import manifest (MANIFEST*.txt at ROOT's top) names,
#            a file that CHANGES-AFTER-IMPORT.md at ROOT's top names with its present sha256 (ruling S283-1 (a), the
#            reading of row M3 of tools/check_manifests.py: a line of that file, read as UTF-8 text, holds both the
#            sha256 of the file's bytes when the runs have ended and its path from ROOT in backticks, the path written
#            with its exact case; the files are those that check_manifests.py's own walk finds (M3 judges those no
#            manifest lists; a listed one is bound by its manifest already), which skips every folder named .git,
#            out4, libcache, build or __pycache__, less its list of the import's own records, the four manifests,
#            PROVENANCE.md and CHANGES-AFTER-IMPORT.md; an absent CHANGES-AFTER-IMPORT.md, or one that does not read as
#            UTF-8, binds nothing), or a file inside a new temporary folder that a run made.
#            A path is compared as written and as the reading
#            process resolved it (links, junctions, short names), each made absolute with a Windows long-path or device
#            prefix (\\?\, \\?\UNC\, \\.\) taken off and, on POSIX, a leading "//" read as "/", its case folded on
#            Windows; it is inside ROOT when either is, and a file is temporary by its resolved path, so a link from a
#            temporary folder into ROOT exempts nothing. And no link has an end, and no removal or move a path, inside
#            ROOT outside a run's new temporary folder (by the path as written and with its folder resolved; the
#            rule is written once for every such event), so a file read and then removed or moved, or read through a
#            link a run made, is judged too; one that cannot be placed fails.
# Last line: "READ AUDIT HELD: n of n rows" (exit 0) or "READ AUDIT FAILED: k of n rows failed" (exit 1); exit 2 on a
# usage error (an unknown or abbreviated option, --help among them, a root that is not a folder, an inventory JSON
# that cannot be read, or is not a held inventory of schema skuldd-inventory/1 naming at least one gated folder and
# its mirrors by plain names, a --json path inside ROOT, as written or as resolved (links, junctions, short names),
# or in a folder that does not exist, or an existing --json file that has another name, a hard link; the path is
# checked when the run starts, and a link made to it during the run is not refused: local use only, since the
# workflows give no --json).
# What a pass shows: in this run no Python process of a test of the CI form or of a feature-row run that kept the hook
# read a file inside the checkout whose bytes nothing binds: each file they read there is held by MK_ANCHOR_CI (a
# judge file), by the inventory's digest and the folders' anchors (a freeze list and what it lists) or by the
# manifests check (the import's manifests and CHANGES-AFTER-IMPORT.md: a file a manifest names, or a file that
# CHANGES-AFTER-IMPORT.md names on a line with the sha256 of its bytes, as row M3 asks, which this audit compares
# itself); and no process they started left the hook in any of the ways it judges. A test added later that reads a new
# file fails here until that file is bound.
# What it does not show: that a file is bound in the right way (a manifest binds a file through the manifests check,
# not through MK_ANCHOR_CI; CHANGES-AFTER-IMPORT.md is no judge file, so a change that adds a file and the line that
# names it passes here, and only the review of that change stands behind the line); a process started, or an import
# made, in a new temporary folder a run made, which is not
# judged (the audit's own test plants there), a program that is not Python among them (the tests start git, sh and
# bash only there: test_records.py, test_check_toolchain.py, test_workflow_guards.py, test_drift.py (git) and the
# stand-ins of test_read_audit.py; sh reads tools/ci/toolchain_probe.sh, a judge file, by its path, unseen); what a
# program that is not Python reads (it raises no event of the watched processes: its start is judged, its reads are
# not); a file opened relative to a folder's descriptor (os.open with dir_fd: the event "open" names no descriptor,
# so the path is placed against the process's own folder; on Linux shutil.rmtree opens each folder it removes so,
# which logs that folder's name as a read at the process's folder, a read of a file only if a file of that name stood
# there, and would hide a read of a file inside ROOT by a process whose folder is outside it);
# and what no check inside the watched processes can see: a process that sets out to evade the hook (forging or
# suppressing its events, changing what it passes on, writing into its log, naming a program that is not Python
# "python", starting Python through another program inside a run's temporary folder). That last is not closed by a
# check because none can be sound inside the processes the hook watches: the hook runs in them; the barrier there is
# the review of the judge files, every test among them, that MK_ANCHOR_CI forces. The pairing of _winapi.CreateProcess
# with subprocess.Popen rests on subprocess's own code (READ, CPython 3.14: the event, then the call, in one thread);
# the command line that call's event carries is not compared, since CPython 3.14 on this host passes it unreadably
# (MEASURED: "\x01"). On Linux CPython 3.12 the events are those seen here (ARGUED from the documentation of
# sys.addaudithook and of the audit events table: "open", "subprocess.Popen", "os.system", "os.exec", "os.putenv",
# "os.unsetenv", "tempfile.mkdtemp", "os.link", "os.symlink", "os.remove", "os.rename", "os.rmdir", "shutil.rmtree",
# "shutil.copyfile", "import" and "os.fork" are raised by CPython on every platform where the call exists,
# "os.posix_spawn" where it exists; on Linux os.spawnv forks (its "os.fork" is refused, so outside a run's temporary
# folder os.spawnv fails the hook row there; test_read_audit.py starts its "spawn" children with os.posix_spawn on
# POSIX) and its child raises "os.exec",
# shell=True starts
# /bin/sh -c, shutil.copy2 opens its source, shutil.rmtree removes through a folder's descriptor and multiprocessing's
# default start forks; sitecustomize is imported from PYTHONPATH unless -I, -E or -S is given; measured on Windows
# with CPython 3.14 only, where os.spawnv raises "os.spawn", "os.posix_spawn" and os.fork do not exist, shell=True
# starts cmd.exe /c, shutil.copy2 and copytree read through "_winapi.CopyFile2" and raise no "open", and os.symlink
# raises its event before the system refuses a plain user).
import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

NAME = 'READ AUDIT'
SCHEMA = 'skuldd-read-audit/1'
INVENTORY_SCHEMA = 'skuldd-inventory/1'
HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 5400
RUN_ALL = 'tools/ci/tests/run_all.py'
ROWS = ('kernel/hardening/features/feature_row3.py', 'kernel/hardening/features/feature_row4.py')
BASES = (('gated', 'kernel/coq'), ('mirrors', 'verdandi/mathkernel/F32'))
LINE = re.compile(r'[0-9a-f]{64}  (\S+)')
FOLDER = re.compile(r'[a-z][a-z0-9_]*')
DIRS_VAR, HOOK_VAR, RUN_VAR = 'MK_READ_AUDIT_DIRS', 'MK_READ_AUDIT_HOOK', 'MK_READ_AUDIT_RUN'
CHANGES = 'CHANGES-AFTER-IMPORT.md'
MANIFESTS_CHECK = os.path.join(os.path.dirname(HERE), 'check_manifests.py')

HOOK = '''# Written by tools/ci/read_audit.py into its temporary folder: the audit hook of every Python process
# of its runs.
import os
import sys
import _thread

_DIRS = [d for d in os.environ.get('MK_READ_AUDIT_DIRS', '').split(os.pathsep) if d]
EVENTS = ('open', 'subprocess.Popen', 'os.posix_spawn', 'os.exec', 'os.spawn', 'os.system', 'os.startfile',
          'os.startfile/2', 'tempfile.mkdtemp', 'os.putenv', 'os.unsetenv', '_winapi.CopyFile2', 'shutil.copyfile',
          'shutil.copymode', 'shutil.copystat', 'shutil.copytree', 'os.link', 'os.symlink', '_winapi.CreateJunction',
          'os.remove', 'os.rename', 'os.rmdir', 'shutil.rmtree', 'import', 'os.fork', 'os.forkpty',
          '_winapi.CreateProcess')
# the events of a copy that name its source and are no "open" (on Windows shutil.copy2 and copytree read through
# CopyFile2): each is logged as a read of its source
COPIES = ('_winapi.CopyFile2', 'shutil.copyfile', 'shutil.copymode', 'shutil.copystat', 'shutil.copytree')
SHELLS = ('sh', 'bash', 'dash', 'zsh', 'ksh', 'mksh', 'ash', 'csh', 'tcsh', 'fish', 'busybox')
GUARDED = ('PYTHONPATH', 'PYTHONHOME')
if _DIRS:
    # busy: the threads inside this hook now (its own events are not logged); popen: per thread, the program and
    # folder of the subprocess.Popen event its _winapi.CreateProcess must match
    _STATE = {'fds': None, 'busy': set(), 'popen': {}}
    _RUN = os.environ.get('MK_READ_AUDIT_RUN', '')
    # read once, when the hook loads: what a process does to os.environ later cannot change them
    _HOOK = os.environ.get('MK_READ_AUDIT_HOOK', '')
    _HOME = os.environ.get('PYTHONHOME')

    def _put(kind, *values):
        if _STATE['fds'] is None:
            name = 'p%d-%s.log' % (os.getpid(), os.urandom(6).hex())
            _STATE['fds'] = [os.open(os.path.join(d, name), os.O_WRONLY | os.O_CREAT | os.O_APPEND
                                     | getattr(os, 'O_BINARY', 0), 0o600) for d in _DIRS]
        line = (repr((kind,) + values) + '\\n').encode('utf-8', 'backslashreplace')
        for fd in _STATE['fds']:
            os.write(fd, line)

    def _path(p):
        if p is None or isinstance(p, int):
            return None
        try:
            return os.path.abspath(os.fsdecode(p))
        except Exception:
            return None

    def _real(p):
        """The path with its links, junctions and short names resolved, in this process (so a path through
        /proc/self is this process's); None when it cannot be resolved."""
        try:
            return os.path.realpath(p)
        except Exception:
            return None

    def _text(x):
        return os.fsdecode(x) if isinstance(x, (bytes, str)) else str(x)

    def _words(line):
        """A command line split as the C runtime of Windows splits one: words between blanks; a double quote turns
        quoting on or off; 2n backslashes before a double quote are n backslashes and the quote turns quoting, 2n+1
        are n backslashes and a literal quote; other backslashes are kept. None for "" inside a quoted word, which
        the runtimes read differently."""
        out, cur, quoted, has, i, n = [], [], False, False, 0, len(line)
        while i < n:
            c = line[i]
            if c == '\\\\':
                j = i
                while j < n and line[j] == '\\\\':
                    j += 1
                if j < n and line[j] == '"':
                    cur.append('\\\\' * ((j - i) // 2))
                    has = True
                    if (j - i) % 2:
                        cur.append('"')
                        j += 1
                else:
                    cur.append(line[i:j])
                i = j
                continue
            if c == '"':
                if quoted and i + 1 < n and line[i + 1] == '"':
                    return None
                quoted, has = not quoted, True
            elif c in ' \\t' and not quoted:
                if cur or has:
                    out.append(''.join(cur))
                cur, has = [], False
            else:
                cur.append(c)
            i += 1
        if cur or has:
            out.append(''.join(cur))
        return out

    def _base(name):
        b = os.path.basename(_text(name)).lower()
        return b[:-4] if b.endswith('.exe') else b

    def _shell(exe, argv):
        """True for a shell given a command to run, whose processes this hook does not judge (as os.system): a POSIX
        shell with -c (alone or in a cluster of short options), or the Windows command interpreter (cmd, or the
        program ComSpec names) with /c, /k or /r."""
        names = [_text(x) for x in (exe, argv[0] if argv else None) if x is not None]
        rest = [_text(a) for a in argv[1:]]
        if any(_base(x) in SHELLS for x in names):
            return any(a.startswith('-') and not a.startswith('--') and 'c' in a[1:] for a in rest)
        comspec = os.environ.get('COMSPEC', '')
        try:
            is_cmd = any(_base(x) == 'cmd' or (comspec and os.path.normcase(os.path.abspath(x))
                                                == os.path.normcase(os.path.abspath(comspec))) for x in names)
        except Exception:
            is_cmd = True
        return is_cmd and any(a.lower()[:2] in ('/c', '/k', '/r') for a in rest)

    def _python(name):
        """True when a program's path or argv[0] names Python: its base name starts with python, or is py (the
        Windows launcher), or the path is this interpreter's."""
        if name is None:
            return False
        name = _text(name)
        base = os.path.basename(name).lower()
        if base.startswith('python') or base in ('py', 'py.exe'):
            return True
        try:
            return os.path.normcase(os.path.abspath(name)) == os.path.normcase(os.path.abspath(sys.executable))
        except Exception:
            return False

    def _skips(exe, argv):
        """True for a Python run given -I, -E or -S, which would not load this hook (argv already split into words).
        The options are read as CPython reads them: a word of short options may hold several; -X and -W take the rest
        of the word or the next word as their argument; -c, -m, "-", "--" or a word not starting with "-" end the
        options; a long option is skipped (--check-hash-based-pycs with its argument)."""
        if not argv or not (_python(exe) or _python(argv[0])):
            return False
        i = 1
        while i < len(argv):
            a = _text(argv[i])
            if a == '--check-hash-based-pycs':
                i += 2
                continue
            if a in ('-', '--') or not a.startswith('-'):
                return False
            if a.startswith('--'):
                i += 1
                continue
            for j in range(1, len(a)):
                if a[j] in 'IES':
                    return True
                if a[j] in 'cm':
                    return False
                if a[j] in 'XW':
                    i += 1 if j + 1 == len(a) else 0
                    break
            i += 1
        return False

    def _keeps(env):
        """True when the environment a process is given (None: this process's own) keeps the hook's variables: the
        log folders, the hook's folder first on PYTHONPATH (a sitecustomize earlier on it would be imported instead),
        and PYTHONHOME unset or this process's own. The hook's folder and PYTHONHOME are the ones this process had
        when the hook loaded, and the folder must not be empty. On Windows names are compared in capitals, as Windows
        reads them, and two spellings of one guarded name are not kept."""
        if env is None:
            e = dict(os.environ)
        else:
            e, names = {}, []
            for k, v in env.items():
                k = _text(k)
                k = k.upper() if os.name == 'nt' else k
                names.append(k)
                e[k] = _text(v)
            if any(names.count(k) > 1 for k in names if k in GUARDED or k.startswith('MK_READ_AUDIT_')):
                return False
        have = e.get('MK_READ_AUDIT_DIRS', '').split(os.pathsep)
        home = e.get('PYTHONHOME')
        return (bool(_HOOK) and all(d in have for d in _DIRS)
                and e.get('PYTHONPATH', '').split(os.pathsep)[0] == _HOOK
                and (home is None or home == _HOME))

    def _spawn(exe, argv, cwd, env):
        if isinstance(argv, (str, bytes)):          # a command line, as Windows passes one: split it
            words = _words(_text(argv))
        else:
            words = [_text(a) for a in (argv or [])]
        where = _path(cwd) if cwd is not None else os.path.abspath(os.getcwd())
        py = False
        if words is None:
            ok, what = False, 'a command line this hook cannot split: %s' % _text(argv)[:80]
        elif _shell(exe, words):
            ok, what = False, 'a shell given a command: %s' % ' '.join(words)[:80]
        else:
            ok, what = _keeps(env) and not _skips(exe, words), (words[0] if words else _text(exe))
            py = _python(exe) or (bool(words) and _python(words[0]))
        # py: the program is a Python run (by its program's or its first argument's name), whose events this hook
        # sees; a program that is not Python raises none, so the judge refuses its start outside a run's temporary
        # folder
        _put('spawn', bool(ok), where, what, _real(where) if where else None, bool(py))

    def _at(p, fd):
        """A path an event names, made absolute: against this process's folder, or, when a folder's descriptor is
        given (shutil.rmtree's own removals on Linux), against that folder (read through /proc/self/fd); None when
        it cannot be placed."""
        if p is None or isinstance(p, int):
            return None
        try:
            p = os.fsdecode(p)
            if fd is None or fd == -1 or os.path.isabs(p):
                return os.path.abspath(p)
            return os.path.abspath(os.path.join(os.readlink('/proc/self/fd/%d' % fd), p))
        except Exception:
            return None

    def _parent(p):
        """The path with its folder resolved (links, junctions, short names) and its last part as written: what a
        link, a removal or a move acts on."""
        try:
            return os.path.join(os.path.realpath(os.path.dirname(p)), os.path.basename(p))
        except Exception:
            return None

    def _change(kind, p, real=None):
        """A link, a removal or a move of the path p; one that cannot be placed is logged with the path None."""
        _put('change', kind, p, real or (_parent(p) if p else None))

    def _refuse(what):
        """A start or an import this hook cannot judge, in this process's folder."""
        where = os.path.abspath(os.getcwd())
        _put('refuse', where, what, _real(where))

    def _hook(event, args):
        if event not in EVENTS:
            return
        me = _thread.get_ident()
        if me in _STATE['busy']:
            return
        _STATE['busy'].add(me)
        try:
            if event == 'import':
                name = _text(args[0])
                if name == 'multiprocessing' or name.startswith('multiprocessing.') \\
                        or name == 'concurrent.futures.process':
                    _refuse('import %s: multiprocessing starts processes this hook cannot judge' % name)
            elif event in COPIES:
                p = _path(args[0])
                if p is not None:
                    _put('open', p, True, _real(p))
            elif event in ('os.link', 'os.symlink', '_winapi.CreateJunction'):
                dst = _at(args[1], args[3] if event == 'os.link' and len(args) > 3 else
                          args[2] if event == 'os.symlink' and len(args) > 2 else None)
                src = _text(args[0]) if args[0] is not None else None
                if event == 'os.symlink' and src is not None and dst is not None and not os.path.isabs(src):
                    src = os.path.abspath(os.path.join(os.path.dirname(dst), src))
                else:
                    src = _at(args[0], args[2] if event == 'os.link' and len(args) > 2 else None)
                _change('link', src, _real(src) if src else None)
                _change('link', dst)
            elif event in ('os.remove', 'os.rmdir', 'shutil.rmtree'):
                _change('remove', _at(args[0], args[1] if len(args) > 1 else None))
            elif event == 'os.rename':
                _change('move', _at(args[0], args[2] if len(args) > 2 else None))
                _change('move', _at(args[1], args[3] if len(args) > 3 else None))
            elif event in ('os.fork', 'os.forkpty'):
                _refuse('%s: a process this hook cannot judge' % event)
            elif event == '_winapi.CreateProcess':
                # subprocess.Popen raises its own event and then, in the same thread, calls _winapi.CreateProcess
                # with the same program and folder: such a call was judged by that event; any other start through
                # _winapi.CreateProcess (multiprocessing's on Windows) is one this hook cannot judge
                want = _STATE['popen'].pop(me, None)
                got = (_text(args[0]) if args[0] is not None else None,
                       _text(args[2]) if len(args) > 2 and args[2] is not None else None)
                if want != got:
                    _refuse('_winapi.CreateProcess not paired with subprocess.Popen: %s' % (got[0] or '')[:80])
            elif event == 'open':
                p = _path(args[0])
                if p is not None:
                    mode, flags = args[1], (args[2] if len(args) > 2 else 0)
                    if mode is None:
                        reads = isinstance(flags, int) and (flags & 3) in (os.O_RDONLY, os.O_RDWR)
                    else:
                        reads = 'r' in str(mode) or '+' in str(mode)
                    _put('open', p, bool(reads), _real(p) if reads else None)
            elif event == 'subprocess.Popen':
                # argv: a list on Linux; on Windows the command line, one string
                exe, argv, cwd, env = args
                _STATE['popen'][me] = (_text(exe) if exe is not None else None,
                                       _text(cwd) if cwd is not None else None)
                _spawn(exe, argv, cwd, env)
            elif event == 'os.posix_spawn':
                _spawn(args[0], args[1], None, args[2])
            elif event == 'os.exec':
                _spawn(args[0], args[1], None, args[2])
            elif event == 'os.spawn':
                _spawn(args[1], args[2], None, args[3])
            elif event in ('os.system', 'os.startfile', 'os.startfile/2'):
                # a shell command line or a file opened by its type: what runs is not read here
                where = os.path.abspath(os.getcwd())
                _put('spawn', False, where, '%s: %s' % (event, _text(args[0])[:80]), _real(where), False)
            elif event in ('os.putenv', 'os.unsetenv'):
                # a change to the environment that the processes this one starts with no env of their own inherit,
                # which os.environ, read by _keeps, need not show: judged as a start this hook cannot judge
                name = _text(args[0]).upper()
                if name in GUARDED or name.startswith('MK_READ_AUDIT_'):
                    where = os.path.abspath(os.getcwd())
                    _put('spawn', False, where, '%s %s: the environment its processes inherit' % (event, name),
                         _real(where), False)
            elif event == 'tempfile.mkdtemp':
                # raised before the folder is made: a folder that exists already is no new temporary folder
                p = _path(args[0])
                if p is not None:
                    _put('mkdtemp', p, os.path.lexists(p), _real(p))
        except Exception:
            pass
        finally:
            _STATE['busy'].discard(me)

    _put('start', os.getpid(), os.getppid(), _RUN)
    sys.addaudithook(_hook)
'''


class Usage(Exception):
    pass


def row(rows, name, ok, detail):
    rows.append({'name': name, 'ok': bool(ok), 'detail': detail})
    print('  %-60s %s  %s' % (name, 'ok' if ok else 'FAIL', detail))
    sys.stdout.flush()


def few(items, k=6):
    items = list(items)
    return ', '.join(items[:k]) + (' and %d more' % (len(items) - k) if len(items) > k else '')


def plain(path):
    """A path with a Windows long-path or device prefix (\\\\?\\, \\\\?\\UNC\\, \\\\.\\) taken off, and on POSIX a
    leading "//" (which normpath keeps) read as "/"."""
    if path.startswith('\\\\?\\UNC\\'):
        return '\\\\' + path[8:]
    if path.startswith('\\\\?\\') or path.startswith('\\\\.\\'):
        return path[4:]
    if os.name != 'nt' and path.startswith('//') and not path.startswith('///'):
        return path[1:]
    return path


def key(path):
    return os.path.normcase(os.path.abspath(plain(path)))


def under(path_key, folder_key):
    return path_key == folder_key or path_key.startswith(folder_key.rstrip(os.sep) + os.sep)


def keys(path, real):
    """The keys of a logged path: as written, and as the logging process resolved it (links, junctions and short
    names), each with its prefixes taken off."""
    return [key(p) for p in (path, real) if isinstance(p, str) and p]


def realkey(path):
    try:
        return key(os.path.realpath(path))
    except (OSError, ValueError):
        return key(path)


def listed(root, rel):
    """The '/' paths a freeze list or manifest at root/rel names (lines "<64 hex>  <path>"), relative to its base."""
    try:
        with open(os.path.join(root, *rel.split('/')), 'rb') as fh:
            text = fh.read().decode('latin-1')
    except OSError:
        return []
    return [m.group(1) for m in (LINE.fullmatch(x.rstrip('\r')) for x in text.split('\n')) if m]


def changes_named(root):
    """The '/' paths of the files that CHANGES-AFTER-IMPORT.md at root names with their present sha256, read as row M3
    of tools/check_manifests.py reads that file (ruling S283-1 (a)); none when it is absent or not UTF-8 text."""
    if not os.path.isfile(os.path.join(root, CHANGES)):
        return []
    try:
        with open(os.path.join(root, CHANGES), encoding='utf-8') as fh:
            change_lines = fh.read().split('\n')
    except UnicodeDecodeError:
        return []
    spec = importlib.util.spec_from_file_location('mk_check_manifests', MANIFESTS_CHECK)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    present = cm.tree_files(root)
    # row M3's test, as check_manifests.py's judge() writes it (a change to one is a change to both)
    return [p for p in sorted(present) if p not in cm.SELF
            and any(present[p] in line and ('`%s`' % p) in line for line in change_lines)]


def bindings(root, inventory):
    """{normcased real path: what binds it} for every bound file of root, and the problems in reading the bindings."""
    bound, problems = {}, []
    spec = importlib.util.spec_from_file_location('mk_judge_digest', os.path.join(HERE, 'judge_digest.py'))
    jd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(jd)
    files, _counts, _jprobs = jd.collect(root)

    def bind(path, why):
        for k in (key(path), realkey(path)):
            bound.setdefault(k, why)

    for rel, (_sha, group) in sorted(files.items()):
        bind(os.path.join(root, *rel.split('/')), 'judge group %s' % group)
    for field, base in BASES:
        for entry in inventory.get(field) or []:
            f = entry.get('folder') if isinstance(entry, dict) else None
            if not isinstance(f, str) or not FOLDER.fullmatch(f):
                problems.append('the inventory JSON names %r in %s' % (f, field))
                continue
            fz = '%s/%s/FROZEN4.txt' % (base, f)
            bind(os.path.join(root, *fz.split('/')), 'freeze list %s' % fz)
            for p in listed(root, fz):
                bind(os.path.join(root, *(base + '/' + p).split('/')), 'listed in %s' % fz)
    for name in sorted(os.listdir(root)):
        if re.fullmatch(r'MANIFEST[A-Za-z0-9_.-]*\.txt', name):
            for p in listed(root, name):
                bind(os.path.join(root, *p.split('/')), 'listed in %s' % name)
    for p in changes_named(root):
        bind(os.path.join(root, *p.split('/')), 'named in %s' % CHANGES)
    return bound, problems


def read_logs(folder):
    """Every event the hook logged into folder, as tuples, and the lines not read."""
    events, bad = [], 0
    for name in sorted(os.listdir(folder)):
        with open(os.path.join(folder, name), 'rb') as fh:
            for line in fh.read().decode('utf-8', 'replace').split('\n'):
                if not line:
                    continue
                try:
                    events.append(ast.literal_eval(line))
                except (ValueError, SyntaxError):
                    bad += 1
    return events, bad


def folders(inventory, field):
    """The inventory JSON's list under field when it is a list of objects each naming a plain folder, else None."""
    v = inventory.get(field)
    if not isinstance(v, list) or not all(isinstance(e, dict) and isinstance(e.get('folder'), str)
                                          and FOLDER.fullmatch(e['folder']) for e in v):
        return None
    return v


def parse(argv):
    ap = argparse.ArgumentParser(prog='read_audit.py', allow_abbrev=False, add_help=False,
                                 description='The files the tests and the feature rows read (see the header).')
    ap.add_argument('--root', required=True)
    ap.add_argument('--inventory-json', required=True)
    ap.add_argument('--json', dest='json_out')
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        raise Usage('--root is not a folder')
    try:
        with open(a.inventory_json, 'rb') as fh:
            inventory = json.loads(fh.read().decode('utf-8'))
        if not isinstance(inventory, dict):
            raise ValueError
    except (OSError, ValueError):
        raise Usage('--inventory-json cannot be read as a JSON object')
    if inventory.get('schema') != INVENTORY_SCHEMA or inventory.get('held') is not True:
        raise Usage('--inventory-json is not a held inventory (schema %s, "held" true)' % INVENTORY_SCHEMA)
    if not folders(inventory, 'gated') or folders(inventory, 'mirrors') is None:
        raise Usage('--inventory-json does not list at least one gated folder and its mirrors, each by a plain name')
    if a.json_out is not None:
        # inside ROOT however it is spelled: the path as written and as resolved (links, junctions, short names; the
        # prefix taken off after resolving), each against ROOT as written and as resolved
        inside = any(under(k, r) for k in (key(a.json_out), realkey(a.json_out)) for r in (key(root), realkey(root)))
        if inside or not os.path.isdir(os.path.dirname(os.path.abspath(a.json_out))):
            raise Usage('--json must name a file outside --root, in a folder that exists')
        # an existing file with another name (a hard link, which resolving does not merge): the other name, which may
        # lie inside ROOT, would be written too
        try:
            nlink = os.stat(a.json_out).st_nlink
        except OSError:
            nlink = 0
        if nlink > 1:
            raise Usage('--json names a file that has another name (a hard link); write a new file')
    return a, root, inventory


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace', newline='\n')
    except (AttributeError, ValueError):
        pass
    try:
        a, root, inventory = parse(argv)
    except Usage as e:
        print('read_audit.py: usage error: %s' % e, file=sys.stderr)
        return 2
    runs = [('tests: tools/ci/tests/run_all.py (CI form)', [RUN_ALL])]
    for field, base in BASES:
        for entry in inventory.get(field) or []:
            f = entry.get('folder') if isinstance(entry, dict) else None
            if isinstance(f, str) and FOLDER.fullmatch(f):
                for script in ROWS:
                    runs.append(('%s on %s/%s' % (script.rsplit('/', 1)[1], base, f),
                                 [script, base, '--list', '%s/%s/FROZEN4.txt' % (base, f)]))
    tmp = tempfile.mkdtemp(prefix='read-audit-')
    rows, record = [], {'schema': SCHEMA, 'runs': [], 'unbound': [], 'unhooked': []}
    try:
        hook, logs = os.path.join(tmp, 'hook'), os.path.join(tmp, 'log')
        os.makedirs(hook)
        os.makedirs(logs)
        with open(os.path.join(hook, 'sitecustomize.py'), 'wb') as fh:
            fh.write(HOOK.encode('ascii'))
        dirs = [d for d in os.environ.get(DIRS_VAR, '').split(os.pathsep) if d] + [logs]
        path = [hook] + [p for p in os.environ.get('PYTHONPATH', '').split(os.pathsep) if p]
        env = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.update({DIRS_VAR: os.pathsep.join(dirs), HOOK_VAR: hook, 'PYTHONPATH': os.pathsep.join(path)})
        done, late = [], []
        for k, (label, args) in enumerate(runs):
            p = subprocess.Popen([sys.executable, '-B'] + args, cwd=root, env=dict(env, **{RUN_VAR: str(k)}),
                                 stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                out, _ = p.communicate(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                p.kill()
                out, _ = p.communicate()
                late.append(label)
            last = ([x for x in out.decode('utf-8', 'replace').replace('\r', '').split('\n') if x.strip()] or [''])[-1]
            done.append((label, p.pid, p.returncode))
            record['runs'].append({'run': label, 'exit': p.returncode, 'last': last[:200]})
            print('    %s: exit %s; %s' % (label, p.returncode, last[:110]))
        row(rows, 'runs: every run ended in its time', not late,
            '%d runs (the tests, then feature rows 3 and 4 on %d freeze lists)' % (len(runs), (len(runs) - 1) // 2)
            if not late else 'stopped after %d seconds: %s' % (TIMEOUT, few(late)))

        events, unread = read_logs(logs)
        bound, bprobs = bindings(root, inventory)
        rkeys = sorted({key(root), realkey(root)})

        def inside(k):
            return k is not None and any(under(k, r) for r in rkeys)

        # a start is matched by its process id and the run's number, so a process id the system reused within the
        # audit cannot stand for a run whose first process logged nothing
        starts = {(e[1], e[3]) for e in events if e[0] == 'start' and len(e) == 4}
        # a temporary folder a run made: "tempfile.mkdtemp" is raised before the folder is made, so a folder that
        # existed then is no new one (an event raised by hand) and exempts nothing; and a logged folder that is the
        # root, holds the root or holds a bound file is no new one either, whatever its "existed" field says (a line
        # written into the log by hand): it exempts nothing and fails the hook row
        temps, forged = set(), []
        for e in events:
            if e[0] != 'mkdtemp' or len(e) != 4:
                continue
            ks = keys(e[1], e[3])
            if any(under(r, k) for k in ks for r in rkeys) or any(under(b, k) for k in ks for b in bound):
                forged.append(e[1])
            elif not e[2]:
                temps.update(ks)

        def temporary(ka, kr):
            """A path a run made inside one of its new temporary folders: by its resolved path, or as written when
            its resolved path is not inside the root (so a link from a temporary folder into the root exempts
            nothing)."""
            return (any(under(kr or ka, t) for t in temps)
                    or (not inside(kr) and any(under(ka, t) for t in temps)))

        def started_in_temporary(e):
            ka = key(e[2]) if isinstance(e[2], str) and e[2] else None
            kr = key(e[4]) if isinstance(e[4], str) and e[4] else None
            return ka is not None and temporary(ka, kr)

        def in_temporary(where, real):
            ka = key(where) if isinstance(where, str) and where else None
            kr = key(real) if isinstance(real, str) and real else None
            return ka is not None and temporary(ka, kr)

        nostart = [label for k, (label, pid, _) in enumerate(done) if (pid, str(k)) not in starts]
        spawns = [e for e in events if e[0] == 'spawn' and len(e) == 6]
        unhooked = sorted({'%s (in %s)' % (e[3], e[2]) for e in spawns if not e[1] and not started_in_temporary(e)})
        # a program that is not Python, given the hook's environment: the hook runs in no such process, so what it
        # does is not seen; started outside a run's new temporary folder, its start fails this row
        foreign = sorted({'%s (in %s)' % (e[3], e[2]) for e in spawns
                          if e[1] and not e[5] and not started_in_temporary(e)})
        # an import of multiprocessing, a fork, or a start through _winapi.CreateProcess that no subprocess.Popen
        # event paired: a start this hook cannot judge (not judged in a run's new temporary folder, as a start there)
        refused = [e for e in events if e[0] == 'refuse' and len(e) == 4]
        cannot = sorted({'%s (in %s)' % (e[2], e[1]) for e in refused if not in_temporary(e[1], e[3])})
        record['unhooked'] = unhooked + cannot
        record['not_python'] = foreign
        record['forged_temporary'] = sorted(set(forged))
        kept = sum(1 for e in spawns if e[1])
        others = sum(1 for e in spawns if e[1] and not e[5])
        exempt = sum(1 for e in spawns if not e[1] and started_in_temporary(e))
        bad = [x for x in ('no start logged by: %s' % few(nostart) if nostart else '',
                           'started without the hook: %s' % few(unhooked, 4) if unhooked else '',
                           'a start or an import this hook cannot judge: %s' % few(cannot, 4) if cannot else '',
                           'a program that is not Python, started outside a run\'s temporary folder: %s'
                           % few(foreign, 4) if foreign else '',
                           'a temporary folder logged that is the root, holds it or holds a bound file: %s'
                           % few(sorted(set(forged)), 3) if forged else '',
                           '%d log lines not read' % unread if unread else '') if x]
        row(rows, 'hook: every process of every run ran under the hook', not bad,
            '%d process starts logged (distinct process id and run); %d started: %d given the hook\'s environment '
            '(%d of them programs that are not Python, each in a run\'s temporary folder), %d in a run\'s '
            'temporary folder without it and not judged%s' % (
                len(starts), len(spawns), kept, others, exempt,
                '; %d imports or starts it cannot judge, in a run\'s temporary folder and not judged' % len(refused)
                if refused else '') if not bad else '; '.join(bad))

        # a link whose source or target is inside the root, and a removal or a move of a path inside the root, outside
        # a run's new temporary folder (the rule is written once, here, for every such event): a file read and then
        # removed or moved, or read through a hard link, would otherwise not be judged by the reads row below
        changed, nchange = [], 0
        for e in events:
            if e[0] != 'change' or len(e) != 4:
                continue
            nchange += 1
            if e[2] is None:
                changed.append('a %s this audit cannot place' % e[1])
                continue
            ka = key(e[2])
            kr = key(e[3]) if isinstance(e[3], str) and e[3] else None
            if (inside(ka) or inside(kr)) and not temporary(ka, kr):
                try:
                    shown = os.path.relpath(plain(e[2]), root).replace(os.sep, '/')
                except ValueError:
                    shown = e[2]
                changed.append('%s %s' % (e[1], shown))
        changed = sorted(set(changed))
        record['changed'] = changed

        seen, outside, kinds = set(), [], {}
        for e in events:
            if e[0] != 'open' or len(e) != 4 or not e[2]:
                continue
            ka = key(e[1])
            kr = key(e[3]) if isinstance(e[3], str) and e[3] else None
            ident = kr or ka
            if not (inside(ka) or inside(kr)) or ident in rkeys or ka in rkeys or ident in seen:
                continue
            seen.add(ident)
            if os.path.isdir(e[3] or e[1]) and not temporary(ka, kr):
                kinds['folders (a copy\'s source)'] = kinds.get('folders (a copy\'s source)', 0) + 1
                continue
            if not os.path.isfile(e[3] or e[1]) or temporary(ka, kr):
                kinds['absent or temporary'] = kinds.get('absent or temporary', 0) + 1
                continue
            why = bound.get(ka) or (bound.get(kr) if kr else None)
            if why is None:
                real_root = os.path.realpath(root)
                try:
                    shown = (os.path.relpath(plain(e[3]), real_root) if kr and under(kr, key(real_root))
                             else os.path.relpath(plain(e[1]), root)).replace(os.sep, '/')
                except ValueError:
                    shown = e[1]
                outside.append(shown)
            else:
                kind = ('judge files' if why.startswith('judge') else
                        'in a manifest' if why.startswith('listed in MANIFEST') else
                        why if why.startswith('named in') else 'freeze lists and their files')
                kinds[kind] = kinds.get(kind, 0) + 1
        record['unbound'] = sorted(outside)
        record['bound_counts'] = kinds
        counts = ', '.join('%s %d' % kv for kv in sorted(kinds.items()))
        detail = '%d files read inside the root: %s; %d links, removals and moves logged, none inside the root ' \
                 'outside a run\'s temporary folder' % (len(seen), counts, nchange)
        row(rows, 'reads: every file read inside the root is bound', not outside and not bprobs and not changed,
            detail if not outside and not bprobs and not changed else
            '; '.join(x for x in ('not bound: %s' % few(sorted(outside), 8) if outside else '',
                                  'linked, removed or moved inside the root: %s' % few(changed, 6) if changed else '',
                                  '; '.join(bprobs)) if x))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n, k = len(rows), sum(1 for r in rows if not r['ok'])
    verdict = '%s FAILED: %d of %d rows failed' % (NAME, k, n) if k else '%s HELD: %d of %d rows' % (NAME, n, n)
    record.update(rows=rows, verdict=verdict, held=not k)
    if a.json_out is not None:
        try:
            with open(a.json_out, 'wb') as fh:
                fh.write((json.dumps(record, sort_keys=True, indent=1) + '\n').encode('utf-8'))
        except OSError as e:
            print('read_audit.py: usage error: --json cannot be written (%s)' % type(e).__name__, file=sys.stderr)
            return 2
    print(verdict)
    return 1 if k else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
