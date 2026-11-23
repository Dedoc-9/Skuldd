# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/check_sweep.py: the check of the sweep job of .github/workflows/mathkernel-linux.yml (ruling S280-13 (a)):
# the frozen floor32/ceil32 sweep built with each compiler given, at -O0 and -O2, -std=c99 -ffp-contract=off, after
# its sha256 is checked and with no x87 or FMA instruction in what was built; it requires the sweep held and each
# plant's predicted counts. Standard library only (Python 3.12 or later). It writes only in the --work folder.
#
#   python3 -B tools/ci/check_sweep.py --root ROOT --input REL --cc CC [--cc CC ...] --work DIR [--objdump OBJDUMP]
#       [--jobs N] [--timeout SECONDS]
#
# The declared input (REL, a file inside ROOT; the workflow gives tools/ci/SWEEP-SOURCE.txt, whose header says why
# each value is what it is) names the candidate sweeps and chooses one. Its lines (printable ASCII, LF, words
# separated by one space, no trailing blank; a blank line or one starting with "#" is a comment):
#   use <c>                          the candidate this check builds (exactly one such line)
#   <c> path <rel>                   the sweep's C source, a path inside ROOT
#   <c> sha256 <hex>                 its frozen sha256
#   <c> freeze-list <rel>            (optional) a freeze list inside ROOT ("<sha256>  <path>" lines) that must record
#                                    that sha256 for the source, on one line whose path ends the source's path
#   <c> fields <n>                   the number of comparisons each function's line of the program reports
#   <c> run <r>                      a run of the program; the runs in the order of these lines
#   <c> <r> source frozen            the run builds the source as it is, or
#   <c> <r> source replace <k>       the run builds a plant: the source with the text of "from" replaced by the text
#   <c> <r> from <text>              of "to", which must occur exactly k times
#   <c> <r> to <text>
#   <c> <r> sha256 <hex>             the sha256 of the source the run builds
#   <c> <r> define <NAME>=<digits>   (zero or more) a -D the run is compiled with
#   <c> <r> expect floor32 <d> <z>   the predicted counts: every comparison of the function differs on d of the 2^32
#   <c> <r> expect ceil32 <d> <z>    inputs, NaN-ness disagrees on none, and z results are -0
#   <c> <r> verdict <text>           the program's last line
# A candidate must have a run that builds its source as it is with every d 0 (the sweep) and a run with some d not 0
# (a plant).
#
# Rows, one line each, "  <row> ok|FAIL  <detail>", in this order:
#   input                 the declared input reads as above; "use" names a candidate that is complete
#   source                the candidate's source is a plain file inside ROOT (no link on its path) with its sha256
#   freeze list           (only when the candidate declares one) the list records that sha256 for the source, once
#   run sources           each run's source is made (each replacement exactly k times) and has its sha256
#   compiler ccN          "<cc> --version" and "<cc> -dumpmachine" exit 0; the machine is x86-64 or aarch64, the same
#                         for every compiler; the compiler's family (gcc or clang) is read from its --version
#   canary fma ccN        a planted a * b + c, built with -O2 -ffp-contract=fast (and -mfma on x86-64): the scan finds
#                         an FMA instruction in its object. It shows that the scan reads this compiler's objects
#   canary x87 ccN        (x86-64 only) a planted __asm__ ("fninit"): the scan finds an x87 instruction
#   build ccN -Ok r       "<cc> -std=c99 -ffp-contract=off -Ok [-D...] -c" and the link (with -lm, but on Windows)
#                         exit 0
#   scan ccN -Ok r        "<objdump> -d --no-show-raw-insn" of the object: it reads the compiler's machine, at least
#                         one instruction, and none is x87 (x86-64: a mnemonic starting with "f", or a %st register)
#                         or FMA (x86-64: vfmadd, vfmsub, vfnmadd, vfnmsub and their forms; aarch64: fmadd, fmsub,
#                         fnmadd, fnmsub, fmla, fmls and their forms)
#   sweep ccN -Ok r       the program exits 0 within --timeout and prints exactly: the floor32 line, a line "first
#                         difference from the host at 0x........" when its d is not 0, the ceil32 line and the same,
#                         and the verdict line; each function's line reports 4294967296 inputs, the fields' count of
#                         comparisons each differing on d inputs, NaN-ness disagreeing on 0, z results -0, and "as
#                         expected"
# When a row before "compiler" fails, nothing is compiled; when a compiler or canary row fails, nothing is built
# for the sweep; a run whose build or scan failed is not run. The sweep programs run up to --jobs at a time (default:
# the processor count); every other step runs one at a time.
# Last line: "SWEEP CHECK HELD: n of n rows (<c>; <machine>; <families>)" (exit 0) or "SWEEP CHECK FAILED: k of n rows
# failed (<c>; <machine>; <families>)" (exit 1), where a value not known is "?" and <families> are the compilers'
# families in the order given, joined by ", ". Exit 2 on a usage error: a bad option (an unknown or abbreviated one,
# --help among them), a ROOT that is not a folder, an input outside ROOT, a --work folder inside ROOT or one that
# exists and is not empty, --jobs or --timeout not a positive whole number.
#
# What a pass shows: on this machine, with these compilers and this objdump, the declared source with the frozen
# sha256, built at -O0 and -O2 with contraction off, held on all 2^32 inputs of each function as the program itself
# judges them (against the C library's floorf/ceilf and an integer reference, and for sweep_fc2.c also against the
# binary64 result and the hand transcription), each plant gave its predicted counts (so each run executed the
# program it names), and objdump showed no x87 or FMA instruction in any object built for the sweep.
# What it does not show: that the C is the Coq program (sweep_fc2.c: what FCLINK proves; sweep_fc.c: a transcription
# by hand); that objdump's reading is the code the processor runs (the linked program adds the C library, whose
# floorf/ceilf are not scanned); another compiler, flag, C library or machine; anything about NaN payloads, which
# the programs compare as NaN-ness only. On Windows (local runs only) a line end CR LF is read as LF.
import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True

NAME = 'SWEEP CHECK'
WIDTH = 30
INPUTS = 4294967296
OPTS = ('-O0', '-O2')
BASE_FLAGS = ('-std=c99', '-ffp-contract=off')
WORD = re.compile(r'[a-z][a-z0-9_-]*')
REL = re.compile(r'[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*')
HEX64 = re.compile(r'[0-9a-f]{64}')
DEFINE = re.compile(r'[A-Z_][A-Z0-9_]*=[0-9]+')
COUNT = re.compile(r'0|[1-9][0-9]*')
FUNCS = ('floor32', 'ceil32')
FIRST_DIFF = re.compile(r'  first difference from the host at 0x[0-9a-f]{8}')
HEAD = re.compile(r'(floor32|ceil32) +(?:plant=[0-9]+ )?inputs ([0-9]+)')
FIELD = re.compile(r'(.+): ([0-9]+)')
NAN_LABEL = 'NaN-ness disagrees'
NEGZ_LABEL = '-0 results'
X86_PREFIXES = {'rep', 'repz', 'repnz', 'repe', 'repne', 'lock', 'data16', 'data32', 'addr32', 'cs', 'ds', 'es', 'fs',
                'gs', 'ss', 'notrack', 'bnd', 'xacquire', 'xrelease'}
X86_FMA = re.compile(r'vfc?n?m(?:add|sub)[a-z0-9]*')
X86_X87 = re.compile(r'f[a-z0-9]*')
ARM_FMA = re.compile(r'(?:bf|f)n?m(?:add|sub|ad|sb|la|ls)[a-z0-9]*')
INSN = re.compile(r'\s*[0-9a-f]+:\s+(\S.*)')
FORMAT = re.compile(r'file format (\S+)')
CANARY_FMA = b'double mk_canary_fma(double a, double b, double c) { return a * b + c; }\n'
CANARY_X87 = b'void mk_canary_x87(void) { __asm__ __volatile__ ("fninit"); }\n'
STEP_TIMEOUT = 600


class Usage(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def machine_of(text):
    """'x86-64', 'aarch64' or None, from a target triple or an objdump file format."""
    t = text.strip().lower()
    if t.startswith('x86_64') or 'x86-64' in t:
        return 'x86-64'
    if t.startswith(('aarch64', 'arm64')) or 'aarch64' in t or t.endswith('arm64'):
        return 'aarch64'
    return None


def family_of(version):
    """'clang', 'gcc' or '?' from a compiler's --version output."""
    first = version.split('\n', 1)[0]
    if 'clang version' in first:
        return 'clang'
    if 'Free Software Foundation' in version and 'clang' not in first.lower():
        return 'gcc'
    return '?'


def plain_rel(rel):
    """True for a relative path of plain names joined by /, none of them . or .."""
    return bool(REL.fullmatch(rel)) and not any(p in ('.', '..') for p in rel.split('/'))


def inside(root, rel):
    """The absolute path of rel inside root, or None when it is not a plain path inside it."""
    if not plain_rel(rel):
        return None
    return os.path.join(root, *rel.split('/'))


def link_on_path(root, rel):
    """True when the file at rel, or a folder on its way from root, is a link or a junction."""
    p = root
    for part in rel.split('/'):
        p = os.path.join(p, part)
        try:
            st = os.lstat(p)
        except OSError:
            return False
        if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_reparse_tag', 0):
            return True
    return False


def read_plain(root, rel):
    """(bytes, None) of a plain file inside root, or (None, why)."""
    p = inside(root, rel)
    if p is None:
        return None, '%s is not a plain path inside the root' % rel
    if link_on_path(root, rel):
        return None, '%s: a link or junction on its path' % rel
    try:
        st = os.lstat(p)
    except OSError:
        return None, '%s: no such file' % rel
    if not stat.S_ISREG(st.st_mode):
        return None, '%s: not a regular file' % rel
    with open(p, 'rb') as fh:
        return fh.read(), None


def parse_input(data):
    """(use, {candidate: dict}, problems). A candidate: path, sha256, frozen, fields, runs [names], run {name: dict};
    a run: source ('frozen' or k), from, to, sha256, defines [..], expect {func: (d, z)}, verdict."""
    problems = []
    cands = {}
    use = []
    try:
        text = data.decode('ascii')
    except UnicodeDecodeError:
        return None, {}, ['the input is not ASCII']
    if text and not text.endswith('\n'):
        problems.append('the input does not end with a line end')
    for n, line in enumerate(text.split('\n')[:-1] if text.endswith('\n') else text.split('\n'), 1):
        if any(ord(ch) < 32 or ord(ch) > 126 for ch in line):
            problems.append('line %d holds a byte outside printable ASCII' % n)
            continue
        if not line or line.startswith('#'):
            continue
        words = line.split(' ')
        if '' in words:
            problems.append('line %d: words are not separated by one space' % n)
            continue
        if words[0] == 'use':
            if len(words) != 2 or not WORD.fullmatch(words[1]):
                problems.append('line %d: "use <candidate>"' % n)
            else:
                use.append(words[1])
            continue
        c = words[0]
        if not WORD.fullmatch(c) or len(words) < 3:
            problems.append('line %d is not "<candidate> <key> <value>"' % n)
            continue
        cd = cands.setdefault(c, {'runs': [], 'run': {}})
        key = words[1]
        if key in ('path', 'sha256', 'freeze-list', 'fields'):
            if len(words) != 3 or key in cd:
                problems.append('line %d: "%s %s" takes one value, given once' % (n, c, key))
                continue
            v = words[2]
            ok = {'path': plain_rel, 'sha256': HEX64.fullmatch, 'freeze-list': plain_rel,
                  'fields': lambda x: COUNT.fullmatch(x) and int(x) > 0}[key](v)
            if not ok:
                problems.append('line %d: "%s %s %s" is not a valid value' % (n, c, key, v))
                continue
            cd[key] = int(v) if key == 'fields' else v
            continue
        if key == 'run':
            if len(words) != 3 or not WORD.fullmatch(words[2]) or words[2] in cd['run'] \
                    or words[2] in ('path', 'sha256', 'freeze-list', 'fields', 'run'):
                problems.append('line %d: "%s run <name>", a new name' % (n, c))
                continue
            cd['runs'].append(words[2])
            cd['run'][words[2]] = {'defines': [], 'expect': {}}
            continue
        if key not in cd['run']:
            problems.append('line %d: "%s %s" names no run declared before it' % (n, c, key))
            continue
        r, rd, what = key, cd['run'][key], words[2]
        rest = words[3:]
        if what == 'source':
            if 'source' in rd or not (rest == ['frozen'] or (len(rest) == 2 and rest[0] == 'replace'
                                                              and COUNT.fullmatch(rest[1]) and int(rest[1]) > 0)):
                problems.append('line %d: "%s %s source frozen" or "source replace <k>", once' % (n, c, r))
                continue
            rd['source'] = 'frozen' if rest == ['frozen'] else int(rest[1])
        elif what in ('from', 'to'):
            if what in rd or not rest:
                problems.append('line %d: "%s %s %s <text>", once' % (n, c, r, what))
                continue
            rd[what] = ' '.join(rest)
        elif what == 'sha256':
            if 'sha256' in rd or len(rest) != 1 or not HEX64.fullmatch(rest[0]):
                problems.append('line %d: "%s %s sha256 <hex>", once' % (n, c, r))
                continue
            rd['sha256'] = rest[0]
        elif what == 'define':
            if len(rest) != 1 or not DEFINE.fullmatch(rest[0]) or rest[0].split('=')[0] in \
                    [x.split('=')[0] for x in rd['defines']]:
                problems.append('line %d: "%s %s define NAME=<digits>", each name once' % (n, c, r))
                continue
            rd['defines'].append(rest[0])
        elif what == 'expect':
            if len(rest) != 3 or rest[0] not in FUNCS or rest[0] in rd['expect'] \
                    or not COUNT.fullmatch(rest[1]) or not COUNT.fullmatch(rest[2]):
                problems.append('line %d: "%s %s expect floor32|ceil32 <d> <z>", each once' % (n, c, r))
                continue
            rd['expect'][rest[0]] = (int(rest[1]), int(rest[2]))
        elif what == 'verdict':
            if 'verdict' in rd or not rest:
                problems.append('line %d: "%s %s verdict <text>", once' % (n, c, r))
                continue
            rd['verdict'] = ' '.join(rest)
        else:
            problems.append('line %d: "%s %s %s" is no key of a run' % (n, c, r, what))
    if len(use) != 1:
        problems.append('%d "use" lines, not 1' % len(use))
    for c in sorted(cands):
        problems += ['%s: %s' % (c, p) for p in candidate_problems(cands[c])]
    if len(use) == 1 and use[0] not in cands:
        problems.append('"use %s" names no candidate' % use[0])
    return (use[0] if len(use) == 1 else None), cands, problems


def candidate_problems(cd):
    out = []
    for key in ('path', 'sha256', 'fields'):
        if key not in cd:
            out.append('no "%s"' % key)
    if not cd['runs']:
        out.append('no run')
    sweep = plant = False
    for r in cd['runs']:
        rd = cd['run'][r]
        for key in ('source', 'sha256', 'verdict'):
            if key not in rd:
                out.append('run %s has no "%s"' % (r, key))
        if sorted(rd['expect']) != sorted(FUNCS):
            out.append('run %s does not expect both floor32 and ceil32' % r)
            continue
        replace = isinstance(rd.get('source'), int)
        if replace != ('from' in rd) or replace != ('to' in rd):
            out.append('run %s: "from" and "to" go with "source replace", and only with it' % r)
        if replace and rd.get('from') == rd.get('to'):
            out.append('run %s replaces a text by itself' % r)
        ds = [rd['expect'][f][0] for f in FUNCS]
        if rd.get('source') == 'frozen' and rd.get('sha256') not in (None, cd.get('sha256')):
            out.append('run %s builds the source as it is, but its sha256 is not the source\'s' % r)
        if rd.get('source') == 'frozen' and not any(ds):
            sweep = True
        if any(ds):
            plant = True
    if cd['runs'] and not sweep:
        out.append('no run builds the source as it is with every d 0 (the sweep)')
    if cd['runs'] and not plant:
        out.append('no run predicts a difference (a plant)')
    return out


def frozen_row(root, cd):
    data, why = read_plain(root, cd['freeze-list'])
    if why:
        return False, why
    try:
        lines = data.decode('utf-8').split('\n')
    except UnicodeDecodeError:
        return False, '%s is not UTF-8' % cd['freeze-list']
    hits = []
    for line in lines:
        m = re.fullmatch(r'([0-9a-f]{64})  (\S+)', line)
        if m and (cd['path'] == m.group(2) or cd['path'].endswith('/' + m.group(2))):
            hits.append(m.group(1))
    if len(hits) != 1:
        return False, '%s has %d lines for %s, not 1' % (cd['freeze-list'], len(hits), cd['path'])
    if hits[0] != cd['sha256']:
        return False, '%s records %s for the source, not the declared %s' % (cd['freeze-list'], hits[0][:16],
                                                                            cd['sha256'][:16])
    return True, '%s records %s for %s' % (cd['freeze-list'], hits[0][:16], cd['path'])


def run_sources(cd, src):
    """({run: bytes}, problems)."""
    out, bad = {}, []
    for r in cd['runs']:
        rd = cd['run'][r]
        if rd['source'] == 'frozen':
            made = src
        else:
            frm, to = rd['from'].encode('ascii'), rd['to'].encode('ascii')
            k = src.count(frm)
            if k != rd['source']:
                bad.append('%s: "%s" occurs %d times, not %d' % (r, rd['from'][:40], k, rd['source']))
                continue
            made = src.replace(frm, to)
        if sha(made) != rd['sha256']:
            bad.append('%s: its source has sha256 %s, not %s' % (r, sha(made)[:16], rd['sha256'][:16]))
            continue
        out[r] = made
    return out, bad


def listing(text, machine):
    """(problem or None, instructions read, {'x87': [mnemonics], 'fma': [mnemonics]}) of an objdump -d listing of an
    object built for machine."""
    found = {'x87': [], 'fma': []}
    fmts = FORMAT.findall(text)
    if not fmts:
        return 'objdump printed no "file format" line', 0, found
    seen = sorted(set(machine_of(f) or f for f in fmts))
    if seen != [machine]:
        return 'objdump read the object as %s, not %s' % (', '.join(seen), machine), 0, found
    n = 0
    for line in text.split('\n'):
        m = INSN.fullmatch(line.rstrip('\r'))
        if not m:
            continue
        words = m.group(1).split('#', 1)[0].split()
        while words and machine == 'x86-64' and (words[0] in X86_PREFIXES or words[0].startswith(('rex', '{'))):
            words = words[1:]
        if not words:
            continue
        n += 1
        mn, ops = words[0].lower(), ' '.join(words[1:]).lower()
        if machine == 'x86-64':
            if X86_FMA.fullmatch(mn):
                found['fma'].append(mn)
            elif X86_X87.fullmatch(mn) or '%st' in ops:
                found['x87'].append(mn)
        elif ARM_FMA.fullmatch(mn):
            found['fma'].append(mn)
    if n == 0:
        return 'no instruction read', 0, found
    return None, n, found


def scan(text, machine):
    """(ok, detail): the listing reads the machine, holds an instruction, and none is x87 or FMA."""
    problem, n, found = listing(text, machine)
    if problem:
        return False, problem
    if found['x87'] or found['fma']:
        return False, '%d instructions; x87: %s; FMA: %s' % (n, ', '.join(sorted(set(found['x87']))) or 'none',
                                                             ', '.join(sorted(set(found['fma']))) or 'none')
    return True, '%d instructions, no x87 or FMA' % n


def finds(text, machine, kind):
    """The distinct mnemonics of kind ('fma' or 'x87') the scan sees in a listing (the canaries); [] when the listing
    is not one of machine or holds no instruction."""
    problem, _, found = listing(text, machine)
    return [] if problem else sorted(set(found[kind]))


def judge_output(text, cd, rd):
    """(ok, detail): the program's standard output against the run's declared lines."""
    if os.name == 'nt':
        text = text.replace('\r\n', '\n')
    if not text.endswith('\n'):
        return False, 'its output does not end with a line end'
    lines = text[:-1].split('\n')
    i, bad = 0, []
    for f in FUNCS:
        d, z = rd['expect'][f]
        if i >= len(lines):
            return False, 'no %s line' % f
        fields = lines[i].split(' | ')
        i += 1
        m = HEAD.fullmatch(fields[0])
        if not m or m.group(1) != f or len(fields) < 4:
            return False, 'line %d is not the %s line: %s' % (i, f, ascii(lines[i - 1])[:80])
        if int(m.group(2)) != INPUTS:
            bad.append('%s: %s inputs' % (f, m.group(2)))
        if fields[-1] != 'as expected':
            bad.append('%s: "%s"' % (f, fields[-1][:30]))
        counts = []
        nan = negz = None
        for x in fields[1:-1]:
            fm = FIELD.fullmatch(x)
            if not fm:
                bad.append('%s: a field "%s"' % (f, x[:40]))
                continue
            if fm.group(1) == NAN_LABEL:
                nan = int(fm.group(2))
            elif fm.group(1) == NEGZ_LABEL:
                negz = int(fm.group(2))
            else:
                counts.append(int(fm.group(2)))
        if len(counts) != cd['fields'] or any(c != d for c in counts):
            bad.append('%s: comparisons %s, predicted %d of them each %d' % (f, counts, cd['fields'], d))
        if nan != 0:
            bad.append('%s: NaN-ness disagrees %s' % (f, nan))
        if negz != z:
            bad.append('%s: -0 results %s, predicted %d' % (f, negz, z))
        if d:
            if i >= len(lines) or not FIRST_DIFF.fullmatch(lines[i]):
                return False, '; '.join(bad + ['%s: no "first difference" line after it' % f])
            i += 1
    if i != len(lines) - 1:
        return False, '; '.join(bad + ['%d lines where the verdict line should be last' % (len(lines) - i)])
    if lines[i] != rd['verdict']:
        bad.append('the last line is "%s", not "%s"' % (lines[i][:40], rd['verdict']))
    if bad:
        return False, '; '.join(bad)
    return True, '%s: floor32 %d/%d, ceil32 %d/%d (d/z) as predicted' % (
        rd['verdict'], rd['expect']['floor32'][0], rd['expect']['floor32'][1], rd['expect']['ceil32'][0],
        rd['expect']['ceil32'][1])


class Host(object):
    """The programs a check runs (compilers, objdump, the built sweeps), on this machine."""

    def run(self, argv, cwd, timeout):
        """(exit code, stdout, stderr); OSError when the program cannot be started, None as the code on a timeout."""
        try:
            p = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None, b'', b''
        return p.returncode, p.stdout, p.stderr

    def run_many(self, jobs, n, say):
        """{key: (exit code or None on a timeout or start failure, stdout, seconds, note)} for jobs [(key, argv, cwd,
        timeout)], up to n at a time, each one's output in a file beside it."""
        out, running, todo = {}, [], list(jobs)
        while todo or running:
            while todo and len(running) < n:
                key, argv, cwd, timeout = todo.pop(0)
                path = os.path.join(cwd, key + '.out')
                fh = open(path, 'wb')
                try:
                    p = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=fh,
                                         stderr=subprocess.DEVNULL)
                except OSError as e:
                    fh.close()
                    out[key] = (None, b'', 0.0, 'could not be started (%s)' % type(e).__name__)
                    continue
                running.append((key, p, fh, path, time.monotonic(), timeout))
                say('  started %s' % key)
            time.sleep(0.2)
            for item in list(running):
                key, p, fh, path, t0, timeout = item
                code, spent = p.poll(), time.monotonic() - t0
                if code is None and spent <= timeout:
                    continue
                note = ''
                if code is None:
                    p.kill()
                    p.wait()
                    code, note = None, 'still running after %d seconds, stopped' % timeout
                fh.close()
                with open(path, 'rb') as rf:
                    data = rf.read()
                out[key] = (code, data, spent, note)
                running.remove(item)
                say('  ended   %s: %s after %d s' % (key, 'exit %s' % code if code is not None else note, spent))
        return out


def parse(argv):
    ap = argparse.ArgumentParser(prog='check_sweep.py', allow_abbrev=False, add_help=False,
                                 description='Build and run the frozen floor32/ceil32 sweep (see the header).')
    ap.add_argument('--root', required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--cc', action='append', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--objdump', default='objdump')
    ap.add_argument('--jobs', default=str(os.cpu_count() or 1))
    ap.add_argument('--timeout', default='3600')

    def refuse(message):
        raise Usage(message)
    ap.error = refuse
    a = ap.parse_args(argv)
    for opt in ('jobs', 'timeout'):
        v = getattr(a, opt)
        if not COUNT.fullmatch(v) or int(v) < 1:
            raise Usage('--%s must be a positive whole number' % opt)
        setattr(a, opt, int(v))
    a.root = os.path.abspath(a.root)
    if not os.path.isdir(a.root):
        raise Usage('--root is not a folder')
    if inside(a.root, a.input) is None:
        raise Usage('--input must be a plain path inside --root')
    a.work = os.path.abspath(a.work)
    rr, rw = os.path.normcase(os.path.realpath(a.root)), os.path.normcase(os.path.realpath(a.work))
    if rw == rr or rw.startswith(rr.rstrip(os.sep) + os.sep):
        raise Usage('--work must be outside --root')
    if os.path.lexists(a.work) and (not os.path.isdir(a.work) or os.listdir(a.work)):
        raise Usage('--work exists and is not an empty folder')
    return a


def check(a, host, say):
    """The rows; returns the exit code (0 or 1)."""
    rows = []
    facts = {'cand': '?', 'machine': '?', 'families': '?'}

    def row(name, ok, detail):
        rows.append(bool(ok))
        say('  %-*s %s  %s' % (WIDTH, name, 'ok' if ok else 'FAIL', detail))

    def verdict():
        k = sum(1 for r in rows if not r)
        tail = '(%s; %s; %s)' % (facts['cand'], facts['machine'], facts['families'])
        if k or not rows:
            say('%s FAILED: %d of %d rows failed %s' % (NAME, k, len(rows), tail))
            return 1
        say('%s HELD: %d of %d rows %s' % (NAME, len(rows), len(rows), tail))
        return 0

    data, why = read_plain(a.root, a.input)
    if why:
        row('input', False, why)
        return verdict()
    use, cands, problems = parse_input(data)
    row('input', not problems, '; '.join(problems)[:600] if problems else 'use %s: %d runs (%s)' % (
        use, len(cands[use]['runs']), ', '.join(cands[use]['runs'])))
    if problems:
        return verdict()
    cd = cands[use]
    facts['cand'] = use
    src, why = read_plain(a.root, cd['path'])
    if why is None and sha(src) != cd['sha256']:
        why = '%s has sha256 %s, not the declared %s' % (cd['path'], sha(src), cd['sha256'])
    row('source', why is None, why or '%s sha256 %s' % (cd['path'], cd['sha256']))
    if why:
        return verdict()
    if 'freeze-list' in cd:
        ok, detail = frozen_row(a.root, cd)
        row('freeze list', ok, detail)
        if not ok:
            return verdict()
    made, bad = run_sources(cd, src)
    row('run sources', not bad, '; '.join(bad) if bad else ', '.join(
        '%s %s' % (r, cd['run'][r]['sha256'][:16]) for r in cd['runs']))
    if bad:
        return verdict()

    os.makedirs(a.work, exist_ok=True)
    for r in cd['runs']:
        with open(os.path.join(a.work, 'src-%s.c' % r), 'wb') as fh:
            fh.write(made[r])
    for name, body in (('canary-fma.c', CANARY_FMA), ('canary-x87.c', CANARY_X87)):
        with open(os.path.join(a.work, name), 'wb') as fh:
            fh.write(body)
    exe = '.exe' if os.name == 'nt' else ''
    libm = [] if os.name == 'nt' else ['-lm']

    def step(argv):
        """(ok, stdout text, why)"""
        try:
            code, so, se = host.run(argv, a.work, STEP_TIMEOUT)
        except OSError as e:
            return False, '', 'could not be started (%s)' % type(e).__name__
        if code != 0:
            last = (se.decode('utf-8', 'replace').strip().splitlines() or [''])[-1]
            return False, '', ('exit %s' % code if code is not None else 'timed out') + (': ' + last[:100]
                                                                                       if last else '')
        return True, so.decode('utf-8', 'replace'), ''

    def disassemble(obj):
        ok, text, why = step([a.objdump, '-d', '--no-show-raw-insn', obj])
        return text if ok else None, why

    ccs = ['cc%d' % (i + 1) for i in range(len(a.cc))]
    machines, families, good = [], [], True
    for cid, cc in zip(ccs, a.cc):
        ok1, ver, why1 = step([cc, '--version'])
        ok2, dm, why2 = step([cc, '-dumpmachine'])
        m = machine_of(dm) if ok2 else None
        fam = family_of(ver) if ok1 else '?'
        machines.append(m)
        families.append(fam)
        if not (ok1 and ok2):
            row('compiler %s' % cid, False, '%s: %s' % (cc, why1 or why2))
            good = False
            continue
        others = [x for x in machines[:-1] if x]
        ok = m is not None and fam != '?' and all(x == m for x in others)
        row('compiler %s' % cid, ok, '%s: %s (%s; %s; machine %s)' % (
            cc, ver.split('\n', 1)[0].strip()[:70], fam, dm.strip()[:40], m or 'not x86-64 or aarch64'))
        good = good and ok
    facts['families'] = ', '.join(families)
    if machines and all(x == machines[0] for x in machines) and machines[0]:
        facts['machine'] = machines[0]
    if not good:
        return verdict()
    machine = facts['machine']
    for cid, cc in zip(ccs, a.cc):
        kinds = [('fma', 'canary-fma.c', ['-O2', '-ffp-contract=fast'] + (['-mfma'] if machine == 'x86-64' else []))]
        if machine == 'x86-64':
            kinds.append(('x87', 'canary-x87.c', ['-O2', '-ffp-contract=off']))
        for kind, src_name, flags in kinds:
            obj = '%s-canary-%s.o' % (cid, kind)
            ok, _, why = step([cc, '-std=c99'] + flags + ['-c', src_name, '-o', obj])
            text = None
            if ok:
                text, why = disassemble(obj)
            seen = finds(text, machine, kind) if text is not None else []
            row('canary %s %s' % (kind, cid), bool(seen), why if text is None else (
                'the scan finds %s in %s' % (', '.join(seen), obj) if seen else
                'the scan finds no %s instruction in %s (%s)' % ('FMA' if kind == 'fma' else 'x87', obj,
                                                                 listing(text, machine)[0] or 'none listed')))
            good = good and bool(seen)
    if not good:
        return verdict()

    jobs, order = [], []
    for cid, cc in zip(ccs, a.cc):
        for opt in OPTS:
            for r in cd['runs']:
                tag = '%s%s-%s' % (cid, opt, r)
                obj, prog = tag + '.o', tag + exe
                order.append((cid, opt, r))
                defines = ['-D' + x for x in cd['run'][r]['defines']]
                ok, _, why = step([cc] + list(BASE_FLAGS) + [opt] + defines + ['-c', 'src-%s.c' % r, '-o', obj])
                if ok:
                    ok, _, why = step([cc, obj, '-o', prog] + libm)
                row('build %s %s %s' % (cid, opt, r), ok, why or '%s %s %s %s -c, linked' % (
                    cc, ' '.join(BASE_FLAGS), opt, ' '.join(defines)))
                if not ok:
                    continue
                text, why = disassemble(obj)
                ok, detail = scan(text, machine) if text is not None else (False, why)
                row('scan %s %s %s' % (cid, opt, r), ok, detail)
                if ok:
                    jobs.append((tag, [os.path.join(a.work, prog)], a.work, a.timeout))
    done = host.run_many(jobs, a.jobs, say) if jobs else {}
    for cid, opt, r in order:
        tag = '%s%s-%s' % (cid, opt, r)
        name = 'sweep %s %s %s' % (cid, opt, r)
        if tag not in done:
            row(name, False, 'not run: its build or scan failed')
            continue
        code, data, spent, note = done[tag]
        if code != 0:
            row(name, False, note or 'exit %s after %d s' % (code, spent))
            continue
        ok, detail = judge_output(data.decode('utf-8', 'replace'), cd, cd['run'][r])
        row(name, ok, '%s (%d s)' % (detail, spent))
    return verdict()


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
    except (AttributeError, ValueError):
        pass
    try:
        a = parse(sys.argv[1:] if argv is None else argv)
    except Usage as e:
        print('usage error: %s' % e, file=sys.stderr)
        return 2

    def say(line):
        print(line)
        sys.stdout.flush()
    return check(a, Host(), say)


if __name__ == '__main__':
    sys.exit(main())
