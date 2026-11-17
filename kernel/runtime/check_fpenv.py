# SPDX-License-Identifier: AGPL-3.0-only
"""check_fpenv.py: mk_fpenv's gate. One command, one verdict:

    python3 -B kernel/runtime/check_fpenv.py [--cc clang] [--cc gcc] ...

For each C compiler (by default whichever of clang, gcc and cc are on the PATH; at least one is required):
  build the self-test at -O0 and -O2, once with the register reads and once with the probes alone, and require
  "FPENV SELFTEST n/n" with n of at least 5 (the admitted state, three rounding modes, the state again);
  compile-time plants: -ffast-math and -ffinite-math-only must each be refused with mk_fpenv's own #error; a build for
  x87 (excess precision) must be refused where the compiler can target it (skipped, and said, where it cannot);
  a run-time plant: mk_fpenv.c built with contraction on (-ffp-contract=fast, and -mfma on x86-64) must make the
  self-test's first row fail and name contraction;
  mutants: mk_fpenv.c with one check disabled at a time must make the self-test fail; a mutant whose plant does not
  exist on this processor is equivalent here and is skipped, and said.
Then, as notes and not rows: which other parts of fast-math this compiler announces, so the header can refuse them.

Everything is built in a temporary folder outside the tree. Last line: "FPENV CHECK HELD: n of n rows" (exit 0) or
"FPENV CHECK FAILED: k of n rows" (exit 1); skipped rows are named on that line and never counted as passes.
What it does not show: that the kernel's operations are deterministic; anything on a compiler, flag set or processor
it did not run on; that a program which does not call mk_fpenv_check is protected.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
STRICT = ['-std=c99', '-pedantic', '-Wall', '-Wextra', '-ffp-contract=off', '-fno-fast-math']
X86 = platform.machine().lower() in ('amd64', 'x86_64')
# (label, text to disable, its replacement, extra flags, the self-test's plant row that must catch it)
MUTANTS = [
    ('rounding probes disabled', 'p |= MK_FPENV_ROUNDING;\n    /* flush-to-zero:', ';\n    /* flush-to-zero:',
     ['-DMK_FPENV_PROBES_ONLY'], 'rounding upward is reported'),
    ('flush-to-zero probe disabled', 'p |= MK_FPENV_FTZ;\n    /* denormals-are-zero:', ';\n    /* denormals-are-zero:',
     ['-DMK_FPENV_PROBES_ONLY'], 'flush-to-zero is reported'),
    ('denormals-are-zero probe disabled', 'p |= MK_FPENV_DAZ;\n    if (bits64(fused)', ';\n    if (bits64(fused)',
     ['-DMK_FPENV_PROBES_ONLY'], 'denormals-are-zero is reported'),
    ('MXCSR rounding read disabled', 'if (csr & 0x6000u) p |= MK_FPENV_ROUNDING;', ';',
     [], None),
    ('MXCSR trap-mask read disabled', 'if ((csr & 0x1F80u) != 0x1F80u) p |= MK_FPENV_TRAPS;', ';',
     [], 'unmasked MXCSR exception is reported'),
    ('FPCR trap read disabled', 'if (fpcr & 0x9F00ul) p |= MK_FPENV_TRAPS;', ';',
     [], 'enabled FPCR trap is reported'),
]
NOTE_FLAGS = ['-fassociative-math -fno-signed-zeros -fno-trapping-math', '-freciprocal-math', '-fno-signed-zeros',
              '-fno-honor-nans', '-funsafe-math-optimizations']
rows = []
skipped = []


def row(ok, name, detail=''):
    rows.append(bool(ok))
    print('  %-70s %s  %s' % (name, 'ok' if ok else 'FAIL', detail))


def skip(name, why):
    skipped.append(name)
    print('  %-70s skip  %s' % (name, why))


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    return p.returncode, p.stdout.decode('utf-8', 'replace')


def selftest(cc, work, sources, flags):
    """(exit code, last line, whole output) of the self-test, or (None, why, '') when it does not build."""
    exe = os.path.join(work, 'test_fpenv.exe' if os.name == 'nt' else 'test_fpenv')
    if os.path.exists(exe):
        os.remove(exe)
    code, out = run([cc] + STRICT + flags + sources + ['-o', exe], work)
    if code != 0:
        return None, 'build exit %d: %s' % (code, out.strip().splitlines()[-1] if out.strip() else ''), ''
    code, out = run([exe], work)
    return code, (out.strip().splitlines()[-1] if out.strip() else ''), out


def counts(last):
    m = re.match(r'FPENV SELFTEST (\d+)/(\d+)$', last)
    return (int(m.group(1)), int(m.group(2))) if m else None


def main(argv):
    ccs = [argv[i + 1] for i, a in enumerate(argv) if a == '--cc' and i + 1 < len(argv)]
    if not ccs:
        ccs = [c for c in ('clang', 'gcc', 'cc') if shutil.which(c)]
    if not ccs:
        print('FPENV CHECK FAILED: no C compiler (clang, gcc or cc) on the PATH')
        return 1
    print('processor: %s' % platform.machine())
    work = tempfile.mkdtemp(prefix='fpenv-')
    try:
        for name in ('mk_fpenv.h', 'mk_fpenv.c', 'test_fpenv.c'):
            shutil.copy(os.path.join(HERE, name), os.path.join(work, name))
        src = open(os.path.join(work, 'mk_fpenv.c'), encoding='utf-8').read()
        for cc in ccs:
            code, ver = run([cc, '--version'], work)
            print('%s: %s' % (cc, ver.strip().splitlines()[0] if ver.strip() else 'exit %d' % code))
            planted = ''
            for opt in ('-O0', '-O2'):
                for mode, extra in (('registers', []), ('probes alone', ['-DMK_FPENV_PROBES_ONLY'])):
                    code, last, out = selftest(cc, work, ['mk_fpenv.c', 'test_fpenv.c'], [opt] + extra)
                    c = counts(last)
                    row(code == 0 and c and c[0] == c[1] and c[1] >= 5,
                        '%s %s, %s: the self-test holds' % (cc, opt, mode), last)
                    if mode == 'registers':
                        planted = planted or out
            for flag, msg in (('-ffast-math', 'mk_fpenv: compiled with fast-math'),
                              ('-ffinite-math-only', 'mk_fpenv: compiled assuming finite math only')):
                code, out = run([cc, '-std=c99', flag, '-c', 'mk_fpenv.c', '-o', 'x.o'], work)
                row(code != 0 and msg in out, 'plant %s %s: refused at compile time' % (cc, flag),
                    'exit %d%s' % (code, '' if msg in out else ', without mk_fpenv\'s message'))
            x87 = (['--target=i686-linux-gnu'] if 'clang' in cc else ['-m32']) + ['-mfpmath=387', '-mno-sse']
            code, out = run([cc, '-std=c99', '-ffreestanding', '-fsyntax-only'] + x87 + ['-x', 'c', 'mk_fpenv.h'], work)
            if 'mk_fpenv: excess precision' in out:
                row(code != 0, 'plant %s x87: refused at compile time' % cc, ' '.join(x87))
            else:
                skip('plant %s x87' % cc, 'this compiler cannot target x87 here (exit %d)' % code)
            fma = ['-ffp-contract=fast'] + (['-mfma'] if X86 else [])
            code, last, out = selftest(cc, work, ['mk_fpenv.c', 'test_fpenv.c'], ['-O2'] + fma)
            first = out.splitlines()[0] if out else last
            row(code == 1 and first.startswith('[FAIL] the admitted state') and 'contraction' in first,
                'plant %s %s: contraction is reported' % (cc, ' '.join(fma)), first[:90])
            for label, old, new, flags, plant in MUTANTS:
                name = 'mutant %s, %s' % (cc, label)
                if old not in src:
                    row(False, name, 'the text to disable is not in mk_fpenv.c')
                    continue
                if plant is None:
                    skip(name, 'equivalent mutant: fegetround and the probes report the same rounding plants')
                    continue
                if plant not in planted:
                    skip(name, 'equivalent mutant here: the self-test has no such plant on this processor')
                    continue
                with open(os.path.join(work, 'mutant.c'), 'w', encoding='utf-8', newline='\n') as f:
                    f.write(src.replace(old, new, 1))
                code, last, out = selftest(cc, work, ['mutant.c', 'test_fpenv.c'], ['-O2'] + flags)
                c = counts(last)
                row(code == 1 and c and c[0] < c[1], '%s: the self-test fails' % name, last or 'did not build')
            for flag in NOTE_FLAGS:
                code, out = run([cc, '-std=c99'] + flag.split() + ['-c', 'mk_fpenv.c', '-o', 'x.o'], work)
                print('  note %s %s: %s' % (cc, flag, 'refused at compile time' if code != 0 and 'mk_fpenv:' in out
                                            else 'NOT refused: this compiler does not announce it'))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    n, k = len(rows), sum(rows)
    tail = ' (%d skipped: %s)' % (len(skipped), '; '.join(skipped)) if skipped else ''
    print('FPENV CHECK %s: %d of %d rows%s' % ('HELD' if k == n and n else 'FAILED', k, n, tail))
    return 0 if k == n and n else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
