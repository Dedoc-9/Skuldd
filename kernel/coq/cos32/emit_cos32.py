# cos32, a candidate function built on sin32 (drafted 2026-11-16; nothing here is adopted). One table, two renderings.
#   cos32(x) = narrow(t * P(t * t)), t = (PH - |x|) + PL, for a binary32 x with |x| <= CMAX (13176794 / 2^22, bits
#   40490FDA), where cos x = sin(pi/2 - |x|), PH + PL is a two-part binary64 pi/2, and P is sin32's polynomial: the
#   square and the polynomial are sin32's own stages (sin32_sq, sin32_poly of MKF.sin32.Graph), called, not copied.
#   PH = 7074237752028440 / 2^52 and PL = 4967757600021511 / 2^106 are binary64 numbers and NOT whole numbers.
#   Every operation is one binary64 operation (round to nearest even); |x| is exact. The graph is the prototype's
#   g_cos32_pre followed by narrow (ext-work/proto/proto_cos.py), not redesigned; like sin32's table it leaves out the
#   prototype's first product u * 1.0, which is exact.
#   python -B emit_cos32.py coq [-]   the Coq graph, Graph.v ("-": to stdout, byte for byte; else beside this script)
#   python -B emit_cos32.py py [-]    reads lines "<8 hex digits>" (a binary32 bit pattern) from stdin and prints
#                                     "<input> <16 hex: the binary64 value before narrow> <8 hex: the binary32 result>"
# The py mode evaluates sin32's two stages from sin32's own table: it loads sin32's generator (emit_sin32.py), found
# beside this folder (../sin32/) or, in the development area, at ../../sin32/src/. The coq mode loads nothing.
# Standard library only. Author: the assistant.
import importlib.util, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CMAX_U = 0x40490FDA                       # the binary32 number just below the binary32 number nearest pi
CONSTS = {'PH': (7074237752028440, 52),   # name: (whole number n, k) for the binary64 number n / 2^k
          'PL': (4967757600021511, 106)}
STEPS = (    # (stage, target, tree): THE table. Stage 'shift' reads x; 'out' reads t and p = sin32_poly(sin32_sq t).
    ('shift', 'a', ('abs', ('var', 'x'))),
    ('shift', 'd', ('sub', ('const', 'PH'), ('var', 'a'))),
    ('shift', 't', ('add', ('var', 'd'), ('const', 'PL'))),
    ('out', 'y', ('mul', ('var', 't'), ('var', 'p'))))
OPS = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}
SIN32_AT = (os.path.join(HERE, '..', 'sin32', 'emit_sin32.py'), os.path.join(HERE, '..', '..', 'sin32', 'src', 'emit_sin32.py'))

_S = []
def sin32():
    """sin32's generator module (its table and its float evaluator), loaded once and only when py values are asked."""
    if not _S:
        for p in SIN32_AT:
            if os.path.exists(p):
                spec = importlib.util.spec_from_file_location('emit_sin32', p); m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m); _S.append(m); break
        else: raise SystemExit('emit_cos32.py: sin32/emit_sin32.py not found beside this folder')
    return _S[0]
def py_const(name):
    n, k = CONSTS[name]; v = n / 2 ** k                 # exact: n has at most 53 bits and 2^k is a power of two
    assert float(n) == n and n < 2 ** 53 and v * 2 ** k == n, name
    return v
def py_tree(e, env):
    if e[0] == 'var': return env[e[1]]
    if e[0] == 'const': return py_const(e[1])
    if e[0] == 'abs': return abs(py_tree(e[1], env))
    a, b = py_tree(e[1], env), py_tree(e[2], env)
    return a + b if e[0] == 'add' else a - b if e[0] == 'sub' else a * b if e[0] == 'mul' else a / b
def py_stage(S, name, var, val):
    """One stage of sin32's table (S.STEPS) with Python floats, its input variable bound to val; the last target."""
    env = {var: val}; out = None
    for st, t, e in S.STEPS:
        if st == name: env[t] = S.py_tree(e, env); out = t
    return env[out]
def py_env(x):
    """Every step with Python floats (binary64, round to nearest even); returns the final environment."""
    S = sin32(); env = {'x': x}
    for st, t, e in STEPS:
        if st == 'out' and 'p' not in env:
            env['u'] = py_stage(S, 'sq', 'x', env['t']); env['p'] = py_stage(S, 'poly', 'u', env['u'])
        env[t] = py_tree(e, env)
    return env
def py_y(x): return py_env(x)['y']                      # the binary64 value before narrow
def narrow(v): return struct.unpack('<f', struct.pack('<f', v))[0]       # the IEEE conversion, as proto.py has it
def py_g(x): return narrow(py_y(x))
def f32(u): return struct.unpack('<f', struct.pack('<I', u))[0]
def u32(x): return struct.unpack('<I', struct.pack('<f', x))[0]
def bits(d): return struct.unpack('<Q', struct.pack('<d', d))[0]

def coq_const(name): return 'cos32_' + name
def coq_tree(e, env):
    if e[0] == 'var': return env[e[1]]
    if e[0] == 'const': return coq_const(e[1])
    if e[0] == 'abs': return '(Rabs %s)' % coq_tree(e[1], env)
    return '(RN64 (%s %s %s))' % (coq_tree(e[1], env), OPS[e[0]], coq_tree(e[2], env))
def strip(b): return b[1:-1] if b.startswith('(') and b.endswith(')') else b
def coq_text():
    """The Coq graph from the table: a constant is its whole number over its power of two, written out; every binary64
    operation is one RN64 of its exact operands; Rabs is exact; the stage 'shift' is a definition of x with its steps
    substituted in order; the function is narrow of the last step, with p sin32's polynomial of sin32's square."""
    L = ['(* Generated by cos32/emit_cos32.py coq; do not edit. The operation graph of cos32 in the FLT model of binary64',
         '   (no overflow, no sign of zero), from the one table of steps that the script also evaluates with Python floats.',
         '   cos x = sin (pi/2 - |x|). cos32_PH is the binary64 number nearest pi/2 and cos32_PL the binary64 number nearest',
         '   pi/2 - cos32_PH; neither is a whole number: each is a whole number over a power of two (2^52 and 2^106).',
         '   cos32_shift: (PH - |x|) + PL, two binary64 operations. g_cos32: narrow of that times sin32\'s polynomial',
         '   (sin32_poly, sin32_sq: the definitions of MKF.sin32.Graph, imported, not copied) at its square. *)',
         'From Coq Require Import Reals.', 'From Flocq Require Import Core.', 'From MKF.p32 Require Import Graphs.',
         'From MKF.sin32 Require Import Graph.', 'Open Scope R_scope.', '']
    for name in ('PH', 'PL'):
        n, k = CONSTS[name]; L.append('Definition %s : R := %d / %d.' % (coq_const(name), n, 2 ** k))
    env = {'x': 'x'}; out = None
    for st, t, e in STEPS:
        if st == 'shift': env[t] = coq_tree(e, env); out = t
    L += ['', 'Definition cos32_shift (x : R) : R := %s.' % strip(env[out])]
    env = {'t': '(cos32_shift x)', 'p': '(sin32_poly (sin32_sq (cos32_shift x)))'}
    outs = [(t, e) for st, t, e in STEPS if st == 'out']; assert len(outs) == 1
    L += ['', 'Definition g_cos32 (x : R) : R := narrow %s.' % coq_tree(outs[0][1], env)]
    return (chr(10).join(L) + chr(10)).encode('utf-8')
def coq():
    if len(sys.argv) > 2 and sys.argv[2] == '-': sys.stdout.buffer.write(coq_text())
    else: open(os.path.join(HERE, 'Graph.v'), 'wb').write(coq_text()); print('wrote Graph.v')
def py():
    out = []
    for line in sys.stdin.buffer.read().decode('ascii').split():
        u = int(line, 16); y = py_y(f32(u)); out.append('%08x %016x %08x' % (u, bits(y), u32(narrow(y))))
    sys.stdout.buffer.write((chr(10).join(out) + chr(10)).encode('ascii'))

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] in ('coq', 'py'): {'coq': coq, 'py': py}[sys.argv[1]]()
    else: print('usage: emit_cos32.py coq [-] | py [-]'); sys.exit(2)
