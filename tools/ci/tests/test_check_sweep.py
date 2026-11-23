# SPDX-License-Identifier: AGPL-3.0-only
# tools/ci/tests/test_check_sweep.py: tools/ci/check_sweep.py, the sweep job's check, held on honest inputs and seen
# to fail on each of its plants. Standard library only (Python 3.12 or later). It writes only in a temporary folder,
# which it removes.
#
#   python3 -B tools/ci/tests/test_check_sweep.py
#
# Most cases call the check's own function check() with a stand-in host in place of its Host: no compiler, objdump
# or sweep program is started. The module is loaded from tools/ci/check_sweep.py (no bytecode written). The stand-in
# compiler writes, as its "object", what it was given (the source's sha256 and the flags); the stand-in objdump
# prints a listing in GNU objdump's form (or llvm-objdump's, for one decoy) of the machine the case plants, with
# instructions that depend on the object (an FMA for the FMA canary only when built with -ffp-contract=fast, and with
# -mfma on x86-64; on aarch64 an fmadd in a sweep object built without -ffp-contract=off, as a compiler there fuses);
# the stand-in program prints the two sweeps' output forms (sweep_fc2.c's four comparisons and its expected counts
# taken from -D, sweep_fc.c's two comparisons and PLANT), with the counts of the zero step removed when the source is
# the never-step plant or PLANT=1. The sources and the declared input are the test's own (candidates alpha, in
# sweep_fc2.c's form with a freeze list, and beta, in sweep_fc.c's), written in a temporary root. The CLI cases run
# check_sweep.py as a process: usage errors, and two runs that end before a program is started or at its start. R01
# reads the tree's own tools/ci/SWEEP-SOURCE.txt.
#
# Cases, one line each, held to tools/ci/tests/PREDICTIONS-check_sweep.txt (frozen before the first run): "<case> |
# <outcome> | <detail> | <what>". HELD: the check exits 0 and its last line is HELD with the detail as its closing
# parenthesis ("-": any); FAILED: it exits 1, its last line is FAILED and the rows that fail are exactly those the
# detail names (comma-separated); USAGE: exit 2 and no verdict line; ok (R01): the declared input reads with no
# problem and each of its candidates has its sweep run and a plant. The file's mutant lines ("mutant | <id> | <cases>
# | <what>") are not read here: they say which cases fail when the check named is taken out of check_sweep.py.
# What a pass shows: the check's rows hold on honest stand-ins and each plant turns exactly its rows red; the check
# reads both objdump forms. What it does not show: real compilers, objdump or sweeps (the job runs those, and its
# console shows them); a link on a path (not planted: a link needs a privilege on Windows); a line end CR LF from a
# program (read as LF on Windows only, so not planted).
# Last line: "TEST check_sweep HELD: n of n cases" (exit 0) or "TEST check_sweep FAILED: k of n cases failed" (exit 1).
import hashlib
import importlib.util
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
CHECK = os.path.join(ROOT, 'tools', 'ci', 'check_sweep.py')
DECLARED = os.path.join(ROOT, 'tools', 'ci', 'SWEEP-SOURCE.txt')
PRED = os.path.join(HERE, 'PREDICTIONS-check_sweep.txt')
ENV = dict(os.environ, PYTHONHASHSEED='0', PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
ROW = re.compile(r'  (\S.*?) +(ok|FAIL)  (.*)')
N = 4294967296
CEIL_D = 1065353216

SRC_A = (b'/* test_check_sweep.py: candidate alpha, in the form of sweep_fc2.c; never compiled */\n'
         b'static double mk_floor32(double x) { return (fabs(x) <= 0.0 ? (x * 0.0) : x); }\n'
         b'static double mk_ceil32(double x) { return (fabs(x) <= 0.0 ? (x * 0.0) : x); }\n')
SRC_A2 = SRC_A.replace(b'<= 0.0 ? (x * 0.0)', b'< 0.0 ? (x * 0.0)')
SRC_B = (b'/* test_check_sweep.py: candidate beta, in the form of sweep_fc.c; never compiled */\n'
         b'#ifndef PLANT\n#define PLANT 0\n#endif\n')


def sha(b):
    return hashlib.sha256(b).hexdigest()


SHA_A, SHA_A2, SHA_B = sha(SRC_A), sha(SRC_A2), sha(SRC_B)
FROZEN = ('# a freeze list of the test\n%s  src/alpha.c\n%s  src/other.c\n' % (SHA_A, '1' * 64)).encode('ascii')

INPUT = '''# test_check_sweep.py's declared input
use alpha

alpha path src/alpha.c
alpha sha256 %(a)s
alpha freeze-list src/FROZEN.txt
alpha fields 4
alpha run frozen
alpha frozen source frozen
alpha frozen sha256 %(a)s
alpha frozen define WANT_F=0
alpha frozen define WANT_C=0
alpha frozen define NEGZ_F=1
alpha frozen define NEGZ_C=1065353216
alpha frozen expect floor32 0 1
alpha frozen expect ceil32 0 1065353216
alpha frozen verdict SWEEP2 HELD
alpha run never-step
alpha never-step source replace 2
alpha never-step from <= 0.0 ? (x * 0.0)
alpha never-step to < 0.0 ? (x * 0.0)
alpha never-step sha256 %(a2)s
alpha never-step define WANT_F=1
alpha never-step define WANT_C=1065353216
alpha never-step define NEGZ_F=0
alpha never-step define NEGZ_C=0
alpha never-step expect floor32 1 0
alpha never-step expect ceil32 1065353216 0
alpha never-step verdict SWEEP2 HELD

beta path src/beta.c
beta sha256 %(b)s
beta fields 2
beta run frozen
beta frozen source frozen
beta frozen sha256 %(b)s
beta frozen expect floor32 0 1
beta frozen expect ceil32 0 1065353216
beta frozen verdict SWEEP HELD (plant=0)
beta run plant1
beta plant1 source frozen
beta plant1 sha256 %(b)s
beta plant1 define PLANT=1
beta plant1 expect floor32 1 0
beta plant1 expect ceil32 1065353216 0
beta plant1 verdict SWEEP HELD (plant=1)
''' % {'a': SHA_A, 'a2': SHA_A2, 'b': SHA_B}

VERSION = {'gcc': 'gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0\nCopyright (C) 2023 Free Software Foundation, Inc.\n',
           'clang': 'Ubuntu clang version 18.1.3 (1ubuntu1)\nTarget: x86_64-pc-linux-gnu\n'}
MACHINE = {('gcc', 'x86-64'): 'x86_64-linux-gnu', ('clang', 'x86-64'): 'x86_64-pc-linux-gnu',
           ('gcc', 'aarch64'): 'aarch64-linux-gnu', ('clang', 'aarch64'): 'aarch64-unknown-linux-gnu'}
FORMATS = {('gnu', 'x86-64'): 'elf64-x86-64', ('llvm', 'x86-64'): 'coff-x86-64',
           ('gnu', 'aarch64'): 'elf64-littleaarch64', ('llvm', 'aarch64'): 'elf64-littleaarch64'}
X86_BODY = ('push %rbp', 'mov %rsp,%rbp', 'movsd %xmm0,-0x8(%rbp)', 'cvtss2sd %xmm0,%xmm0', 'ucomisd %xmm1,%xmm0',
            'andpd 0x0(%rip),%xmm0', 'addsd %xmm1,%xmm0', 'subsd %xmm1,%xmm0', 'mulsd %xmm2,%xmm0',
            'cvtsd2ss %xmm0,%xmm0', 'call 0 <floorf>', 'call 0 <ceilf>', 'mov %fs:0x28,%rax',
            'cs nopw 0x0(%rax,%rax,1)',
            'notrack jmp *%rax', 'rep stos %rax,%es:(%rdi)', 'pop %rbp', 'ret')
ARM_BODY = ('stp x29, x30, [sp, #-16]!', 'fcvt d0, s0', 'fadd d0, d0, d1', 'fsub d0, d0, d1', 'fmul d0, d0, d2',
            'fabs d1, d0', 'fcmp d1, #0.0', 'fcsel d0, d0, d1, ls', 'fmaxnm d0, d0, d1', 'fminnm d0, d0, d1',
            'fmov d1, #1.000000000000000000e+00', 'bl 0 <floorf>', 'ldp x29, x30, [sp], #16', 'ret')


class FakeHost(object):
    """check_sweep.py's Host, answering as the case plants."""

    def __init__(self, machine='x86-64', style='gnu', **plants):
        self.machine, self.style, self.p = machine, style, plants
        self.calls = []

    def g(self, key, default=None):
        return self.p.get(key, default if default is not None else {})

    def run(self, argv, cwd, timeout):
        self.calls.append(list(argv))
        prog = argv[0]
        if prog in self.g('missing', set()):
            raise FileNotFoundError(prog)
        if argv[1:] == ['--version']:
            code = self.g('version_exit').get(prog, 0)
            return code, self.g('version').get(prog, VERSION.get(prog, 'cc 1.0\n')).encode(), b''
        if argv[1:] == ['-dumpmachine']:
            return 0, (self.g('triple').get(prog, MACHINE.get((prog, self.machine), 'unknown')) + '\n').encode(), b''
        if prog == 'objdump':
            return 0, self.listing(cwd, argv[-1]).encode(), b''
        if '-c' in argv:
            src, obj = argv[argv.index('-c') + 1], argv[argv.index('-o') + 1]
            if obj in self.g('fail_compile', set()):
                return 1, b'', b'error: planted\n'
            with open(os.path.join(cwd, src), 'rb') as fh:
                data = fh.read()
            flags = [x for x in argv[1:] if x.startswith('-') and x not in ('-c', '-o')]
            write_json(os.path.join(cwd, obj), {'cc': prog, 'src': sha(data), 'name': src, 'flags': flags})
            return 0, b'', b''
        if '-o' in argv:
            obj, exe = argv[1], argv[argv.index('-o') + 1]
            if exe in self.g('fail_link', set()):
                return 1, b'', b'ld: planted\n'
            d = read_json(os.path.join(cwd, obj))
            d['libs'] = [x for x in argv if x.startswith('-l')]
            write_json(os.path.join(cwd, exe), d)
            return 0, b'', b''
        return 99, b'', ('stand-in: not a call of this test: %s' % ' '.join(argv)).encode()

    def listing(self, cwd, obj):
        d = read_json(os.path.join(cwd, obj))
        m, flags = self.machine, d['flags']
        if d['name'] == 'canary-fma.c':
            fused = '-ffp-contract=fast' in flags and (m != 'x86-64' or '-mfma' in flags)
            if fused:
                body = ['vfmadd213sd %xmm2,%xmm1,%xmm0'] if m == 'x86-64' else ['fmadd d0, d0, d1, d2']
            else:
                body = ['mulsd %xmm1,%xmm0', 'addsd %xmm2,%xmm0'] if m == 'x86-64' else ['fmul d0, d0, d1',
                                                                                         'fadd d0, d0, d2']
            body.append('ret')
        elif d['name'] == 'canary-x87.c':
            body = ['fninit', 'ret'] if m == 'x86-64' else ['ret']
        else:
            body = list(X86_BODY if m == 'x86-64' else ARM_BODY)
            if m == 'aarch64' and '-ffp-contract=off' not in flags:
                body.insert(3, 'fmadd d0, d1, d2, d0')
        body = [x for x in body if not any(s in x for s in self.g('drop').get(obj, []))]
        body += self.g('add').get(obj, [])
        if obj in self.g('empty', set()):
            body = []
        fmt = self.g('fmt').get(obj, FORMATS[(self.style, m)])
        out = []
        if self.style == 'llvm':
            out.append('\n%s:\tfile format %s\n\nDisassembly of section .text:\n\n0000000000000000 <main>:'
                       % (obj, fmt))
            for i, ins in enumerate(body):
                mn, _, ops = ins.partition(' ')
                out.append('%8x:      \t%s\t%s # a comment' % (4 * i, mn, ops.replace(',', ', ')))
        else:
            out.append('\n%s:     file format %s\n\n\nDisassembly of section .text:\n\n0000000000000000 <main>:' % (obj,
                                                                                                         fmt))
            for i, ins in enumerate(body):
                mn, _, ops = ins.partition(' ')
                out.append('%4x:\t%-6s %s' % (4 * i, mn, ops) if ops else '%4x:\t%s' % (4 * i, mn))
        return '\n'.join(out) + '\n'

    def run_many(self, jobs, n, say):
        out = {}
        for key, argv, cwd, timeout in jobs:
            self.calls.append(list(argv))
            if key in self.g('timeout', set()):
                out[key] = (None, b'', float(timeout), 'still running after %d seconds, stopped' % timeout)
                continue
            d = read_json(argv[0])
            text, code = program(d, self.p.get('inert', False))
            edit = self.g('out_edit').get(key)
            if edit:
                text = edit(text)
            out[key] = (self.g('exit').get(key, code), text.encode('ascii'), 1.0, '')
        return out


def program(d, inert):
    """(output, exit code) of the stand-in sweep program built from object d."""
    defines = dict(x[2:].split('=', 1) for x in d['flags'] if x.startswith('-D'))
    if d['src'] == SHA_A or d['src'] == SHA_A2:
        plant = d['src'] == SHA_A2 and not inert
        want = {'floor32': (int(defines.get('WANT_F', -1)), int(defines.get('NEGZ_F', -1))),
                'ceil32': (int(defines.get('WANT_C', -1)), int(defines.get('NEGZ_C', -1)))}
        lines, ok_all = [], True
        for f, lib, dd in (('floor32', 'floorf', 1), ('ceil32 ', 'ceilf ', CEIL_D)):
            dz = (dd, 0) if plant else (0, 1 if f == 'floor32' else CEIL_D)
            ok = dz == want[f.strip()]
            ok_all = ok_all and ok
            lines.append('%s inputs %d | differs from host %s: %d | from integer reference: %d | binary64 result '
                         'differs from the integer reference: %d | from hand transcription: %d | NaN-ness disagrees: '
                         '0 | -0 results: %d | %s' % (f, N, lib, dz[0], dz[0], dz[0], dz[0], dz[1],
                                                      'as expected' if ok else 'NOT AS EXPECTED'))
            if dz[0]:
                lines.append('  first difference from the host at 0x80000000')
        lines.append('SWEEP2 HELD' if ok_all else 'SWEEP2 FAILED')
        return '\n'.join(lines) + '\n', 0 if ok_all else 1
    if d['src'] == SHA_B:
        p = int(defines.get('PLANT', 0))
        lines = []
        for f, lib, dd in (('floor32', 'floorf', 1), ('ceil32 ', 'ceilf ', CEIL_D)):
            dz = (dd, 0) if p else (0, 1 if f == 'floor32' else CEIL_D)
            lines.append('%s plant=%d inputs %d | differs from host %s: %d | differs from integer reference: %d | '
                         'NaN-ness disagrees: 0 | -0 results: %d | as expected' % (f, p, N, lib, dz[0], dz[0], dz[1]))
            if dz[0]:
                lines.append('  first difference from the host at 0x80000000')
        lines.append('SWEEP HELD (plant=%d)' % p)
        return '\n'.join(lines) + '\n', 0
    return 'not a program of this test\n', 1


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(obj, fh, sort_keys=True)


def read_json(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def wb(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data)


def load_check():
    spec = importlib.util.spec_from_file_location('check_sweep_under_test', CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sub(old, new, count=1):
    """An edit of the declared input: old replaced by new, which must occur count times."""
    def edit(text):
        if text.count(old) != count:
            raise NotBuilt('the plant does not apply: "%s" occurs %d times' % (old[:40], text.count(old)))
        return text.replace(old, new)
    return edit


class NotBuilt(Exception):
    pass


def beta_first(text):
    """The declared input with candidate beta's lines moved above alpha's, after a comment and a blank line."""
    head, tail = text.split('\nbeta path', 1)
    return head.rstrip('\n').replace('use alpha', 'use alpha\n\n# beta first\nbeta path' + tail.rstrip('\n') + '\n') \
        + '\n'


def outs(old, new):
    def edit(text):
        if old not in text:
            return text + 'the output plant did not apply\n'
        return text.replace(old, new, 1)
    return edit


def cases():
    """{case: dict(kind='check'|'cli'|'real', ...)}"""
    c = {}

    def chk(cid, **kw):
        c[cid] = dict(kind='check', **kw)

    honest_x86 = {}
    chk('H01', **honest_x86)
    chk('H02', machine='aarch64')
    chk('H03', edits=[sub('use alpha', 'use beta')])
    # the declared input
    chk('P01', edits=[sub('alpha fields 4', 'alpha  fields 4')])
    chk('P02', edits=[sub('alpha fields 4', 'alpha\tfields 4')])
    chk('P03', edits=[sub("# test_check_sweep.py's declared input", "# test_check_sweep.py's d\u00e9clared input")])
    chk('P04', edits=[lambda t: t.rstrip('\n')])
    chk('P05', edits=[sub('use alpha\n', 'use alpha\nuse beta\n')])
    chk('P06', edits=[sub('use alpha', 'use gamma')])
    chk('P07', edits=[sub('alpha frozen verdict SWEEP2 HELD\n',
                          'alpha frozen verdict SWEEP2 HELD\nalpha frozen colour red\n')])
    chk('P08', edits=[sub('alpha run never-step\n', ''),
                      sub('alpha never-step verdict SWEEP2 HELD\n',
                          'alpha never-step verdict SWEEP2 HELD\nalpha run never-step\n')])
    chk('P09', edits=[sub('alpha frozen define WANT_F=0', 'alpha frozen define want_f=0')])
    chk('P10', edits=[sub('alpha frozen expect ceil32 0 1065353216\n', '')])
    chk('P11', edits=[lambda t: '\n'.join(x for x in t.split('\n') if not x.startswith('alpha never-step')
                                          and x != 'alpha run never-step')])
    chk('P12', edits=[sub('alpha frozen expect floor32 0 1', 'alpha frozen expect floor32 1 1')])
    chk('P13', edits=[sub('alpha path src/alpha.c', 'alpha path src/../src/alpha.c')])
    chk('P14', edits=[sub('alpha sha256 %s' % SHA_A, 'alpha sha256 %s' % SHA_A.upper())])
    chk('P15', edits=[sub('alpha frozen source frozen\n', 'alpha frozen source frozen\nalpha frozen from x\n')])
    chk('P16', edits=[sub('use alpha\n', 'use alpha \n')])
    chk('P17', edits=[lambda t: ''])
    # the source and the freeze list
    chk('P20', files={'src/alpha.c': SRC_A + b'/* one more line */\n'})
    chk('P21', files={'src/alpha.c': None}, folders=['src/alpha.c'])
    chk('P22', files={'src/alpha.c': None})
    chk('P24', files={'src/FROZEN.txt': FROZEN.replace(SHA_A.encode(), b'2' * 64)})
    chk('P25', files={'src/FROZEN.txt': FROZEN.replace(b'  src/alpha.c', b'  src/alpha2.c')})
    chk('P26', files={'src/FROZEN.txt': FROZEN + ('%s  alpha.c\n' % SHA_A).encode()})
    chk('P27', files={'src/FROZEN.txt': None})
    chk('P28', edits=[sub('alpha never-step source replace 2', 'alpha never-step source replace 3')])
    chk('P29', edits=[sub('alpha never-step sha256 %s' % SHA_A2, 'alpha never-step sha256 %s' % ('3' * 64))])
    chk('P30', edits=[sub('alpha frozen sha256 %s' % SHA_A, 'alpha frozen sha256 %s' % SHA_A2)])
    # the compilers and the canaries
    chk('P31', host={'missing': {'clang'}})
    chk('P32', host={'triple': {'gcc': 'riscv64-linux-gnu'}})
    chk('P33', host={'triple': {'clang': 'aarch64-unknown-linux-gnu'}})
    chk('P34', host={'version': {'gcc': 'cc version 1 (a compiler of no known family)\n'}})
    chk('P35', host={'version_exit': {'gcc': 1}})
    chk('P36', host={'drop': {'cc1-canary-fma.o': ['vfmadd']}})
    chk('P37', host={'drop': {'cc2-canary-x87.o': ['fninit']}})
    chk('P38', host={'fmt': {'cc1-canary-fma.o': 'elf32-i386'}})
    # the builds and the scans
    chk('P40', host={'fail_compile': {'cc1-O2-never-step.o'}})
    exe = '.exe' if os.name == 'nt' else ''
    chk('P41', host={'fail_link': {'cc2-O0-frozen' + exe}})
    chk('P42', host={'add': {'cc1-O2-frozen.o': ['vfmadd231sd %xmm2,%xmm1,%xmm0']}})
    chk('P43', host={'add': {'cc2-O0-never-step.o': ['fldt 0x10(%rsp)']}})
    chk('P45', machine='aarch64', host={'add': {'cc2-O2-frozen.o': ['fmla v0.2d, v1.2d, v2.2d']}})
    chk('P46', host={'empty': {'cc1-O0-frozen.o'}})
    chk('P47', host={'fmt': {'cc2-O2-never-step.o': 'elf64-littleaarch64'}})
    # the programs' output
    chk('P50', host={'out_edit': {'cc1-O0-frozen': outs('differs from host floorf: 0', 'differs from host floorf: 1')}})
    chk('P51', host={'out_edit': {'cc2-O2-frozen': outs('NaN-ness disagrees: 0', 'NaN-ness disagrees: 1')}})
    chk('P52', host={'out_edit': {'cc1-O2-never-step': outs('-0 results: 0', '-0 results: 2')}})
    chk('P53', host={'exit': {'cc2-O0-never-step': 1}})
    chk('P54', host={'timeout': {'cc1-O0-never-step'}})
    chk('P55', host={'out_edit': {'cc2-O2-never-step': lambda t: t + 'done\n'}})
    chk('P56', host={'out_edit': {'cc1-O2-never-step': outs('  first difference from the host at 0x80000000\n', '')}})
    chk('P57', host={'out_edit': {'cc2-O0-frozen': outs('SWEEP2 HELD', 'SWEEP2 FAILED')}})
    chk('P58', host={'out_edit': {'cc1-O2-frozen': outs('inputs 4294967296', 'inputs 4294967295')}})
    chk('P59', host={'out_edit': {'cc2-O2-frozen': outs('| as expected', '| NOT AS EXPECTED')}})
    chk('P60', host={'out_edit': {'cc1-O0-frozen': outs(' | from hand transcription: 0', '')}})
    chk('P62', cc=['gcc'], host={'inert': True})
    # decoys: changes the check must not see
    chk('D01', edits=[sub('use alpha\n', '\n# a comment\n\nuse alpha\n'), beta_first])
    chk('D02', files={'src/beta.c': None})
    chk('D03', style='llvm')
    chk('D04', host={'add': {'cc1-O2-frozen.o': ['call 0 <fmadd>', 'nopw 0x0(%rax,%rax,1)', 'lea 0x0(%rip),%rdi']}})
    chk('D05', cc=['gcc'])
    chk('D06', jobs=1)
    # the command line
    c['U01'] = dict(kind='cli', args=['--help'])
    c['U02'] = dict(kind='cli', args=['--root', '{root}', '--inp', 'input.txt', '--cc', 'gcc', '--work', '{work}'])
    c['U03'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--cc', 'gcc', '--work',
                                      '{root}/work'])
    c['U04'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--cc', 'gcc', '--work', '{full}'])
    c['U05'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--cc', 'gcc', '--work', '{work}',
                                      '--jobs', '0'])
    c['U06'] = dict(kind='cli', args=['--root', '{root}', '--input', '../input.txt', '--cc', 'gcc', '--work',
                                      '{work}'])
    c['U07'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--work', '{work}'])
    c['C01'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--cc', '{nocc}', '--work',
                                      '{work}'], files={'src/alpha.c': SRC_A + b'\n'})
    c['C02'] = dict(kind='cli', args=['--root', '{root}', '--input', 'input.txt', '--cc', '{nocc}', '--work',
                                      '{work}'])
    c['R01'] = dict(kind='real')
    return c


def read_predictions():
    preds, problems = {}, []
    with open(PRED, 'rb') as fh:
        lines = fh.read().decode('utf-8').split('\n')
    for n, line in enumerate(lines, 1):
        if not line or line.startswith('#') or line.startswith('mutant | '):
            continue
        parts = line.split(' | ')
        if len(parts) != 4 or parts[0] in preds or parts[1] not in ('HELD', 'FAILED', 'USAGE', 'ok'):
            problems.append('line %d is not "case | HELD|FAILED|USAGE|ok | detail | what", or repeats a case' % n)
            continue
        preds[parts[0]] = (parts[1], parts[2])
    return preds, problems


def make_root(tmp, cid, spec):
    root = os.path.join(tmp, cid, 'root')
    text = INPUT
    for e in spec.get('edits', []):
        text = e(text)
    files = {'src/alpha.c': SRC_A, 'src/beta.c': SRC_B, 'src/FROZEN.txt': FROZEN,
             'input.txt': text.encode('utf-8')}
    files.update(spec.get('files', {}))
    os.makedirs(root)
    for rel, data in files.items():
        if data is not None:
            wb(os.path.join(root, *rel.split('/')), data)
    for rel in spec.get('folders', []):
        os.makedirs(os.path.join(root, *rel.split('/')))
    return root


def judge(pred, code, lines):
    """(ok, detail) of a check's exit code and output against its prediction."""
    outcome, detail = pred
    last = lines[-1] if lines else ''
    rows = [m.groups() for m in (ROW.fullmatch(x) for x in lines) if m]
    failed = [r[0] for r in rows if r[1] == 'FAIL']
    verdicts = [x for x in lines if x.startswith('SWEEP CHECK ')]
    got = '%d rows, %d failed%s; last line: %s' % (len(rows), len(failed), (' (' + ', '.join(failed) + ')')
                                                   if failed else '', last[:100])
    if outcome == 'USAGE':
        return code == 2 and not verdicts, 'exit %d; %s' % (code, got)
    if outcome == 'HELD':
        ok = code == 0 and last.startswith('SWEEP CHECK HELD: ') and len(verdicts) == 1 and not failed and rows
        if detail != '-':
            ok = ok and last.endswith(' ' + detail)
        return bool(ok), 'exit %d; %s' % (code, got)
    want = sorted(x.strip() for x in detail.split(','))
    ok = code == 1 and last.startswith('SWEEP CHECK FAILED: ') and len(verdicts) == 1 and sorted(failed) == want
    return ok, 'exit %d; %s' % (code, got)


def run_check(cs, tmp, cid, spec):
    root = make_root(tmp, cid, spec)
    work = os.path.join(tmp, cid, 'work')
    args = ['--root', root, '--input', 'input.txt', '--work', work, '--jobs', str(spec.get('jobs', 4))]
    for cc in spec.get('cc', ['gcc', 'clang']):
        args += ['--cc', cc]
    a = cs.parse(args)
    host = FakeHost(machine=spec.get('machine', 'x86-64'), style=spec.get('style', 'gnu'), **spec.get('host', {}))
    lines = []
    code = cs.check(a, host, lines.append)
    return code, lines


def run_cli(tmp, cid, spec):
    root = make_root(tmp, cid, spec)
    full = os.path.join(tmp, cid, 'full')
    wb(os.path.join(full, 'stale.o'), b'x')
    subs = {'{root}': root, '{work}': os.path.join(tmp, cid, 'work'), '{full}': full,
            '{nocc}': os.path.join(tmp, cid, 'no-such-compiler')}
    args = []
    for x in spec['args']:
        for k, v in subs.items():
            x = x.replace(k, v)
        args.append(x)
    p = subprocess.run([sys.executable, '-B', CHECK] + args, cwd=os.path.join(tmp, cid), env=ENV,
                       stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    lines = [x.rstrip('\r') for x in (p.stdout + b'\n' + p.stderr).decode('utf-8', 'replace').split('\n') if x.strip()]
    out = [x.rstrip('\r') for x in p.stdout.decode('utf-8', 'replace').split('\n') if x.strip()]
    return p.returncode, out if out else lines


def real(cs):
    with open(DECLARED, 'rb') as fh:
        use, cands, problems = cs.parse_input(fh.read())
    ok = not problems and use in cands
    return ok, ('use %s; candidates %s' % (use, ', '.join('%s (%s)' % (k, ', '.join(cands[k]['runs']))
                                                          for k in sorted(cands)))
                if ok else '; '.join(problems)[:300])


def main():
    preds, problems = read_predictions()
    results = []
    tmp = tempfile.mkdtemp(prefix='test-check-sweep-')
    try:
        try:
            cs = load_check()
        except Exception as e:  # the module under test does not load: every case fails
            cs = None
            results.append(('load', False, 'tools/ci/check_sweep.py does not load: %s' % type(e).__name__))
        defined = cases()
        if cs is not None:
            for cid in sorted(defined):
                spec = defined[cid]
                if cid not in preds:
                    results.append((cid, False, 'no prediction'))
                    continue
                try:
                    if spec['kind'] == 'real':
                        ok, detail = real(cs)
                        results.append((cid, ok == (preds[cid][0] == 'ok'), detail))
                        continue
                    if spec['kind'] == 'cli':
                        code, lines = run_cli(tmp, cid, spec)
                    else:
                        code, lines = run_check(cs, tmp, cid, spec)
                except NotBuilt as e:
                    results.append((cid, False, str(e)))
                    continue
                except Exception as e:  # a case that cannot run fails, with the reason
                    results.append((cid, False, 'the case could not run: %s: %s' % (type(e).__name__, e)))
                    continue
                ok, detail = judge(preds[cid], code, lines)
                results.append((cid, ok, detail))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ran = set(r[0] for r in results)
    for cid in sorted(set(preds) - ran):
        results.append((cid, False, 'predicted, not run'))
    for p in problems:
        results.append(('predictions', False, p))
    for cid, ok, detail in results:
        print('  %-8s %s  %s' % (cid, 'ok' if ok else 'FAIL', detail))
    k = sum(1 for r in results if not r[1])
    if k or not results:
        print('TEST check_sweep FAILED: %d of %d cases failed' % (k, len(results)))
        return 1
    print('TEST check_sweep HELD: %d of %d cases' % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
