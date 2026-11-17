# sinturn32 / costurn32, candidate functions built on sin32 and cos32 (drafted 2026-11-16; nothing here is adopted).
# One table, two renderings. The angle is in TURNS, a binary32 x of any magnitude:
#   sinturn32(x) = narrow(sinturn32_pre x) ~ sin(2 pi x),  costurn32(x) = narrow(costurn32_pre x) ~ cos(2 pi x)
#   |x| >= 2^23: sin -> x * 0, cos -> 1. Otherwise f = x - N(x), N(v) = (v + 1.5*2^52) - 1.5*2^52; q = 4 * f;
#   k = N(q); r = q - k; S = core(r), C = core(1 - |r|), core(v) = t * P(t * t) with t = v * PH; P is sin32's
#   polynomial (its stages sin32_sq, sin32_poly, called, not copied) and PH is cos32's first constant (cos32_PH,
#   imported, not copied). sin: |k|<=0: S; |k|<=1: 0<=k: C, else -C; else -S. cos: |k|<=0: C; |k|<=1: 0<=k: -S,
#   else S; else -C. The graph is the prototype's g_sin_pre / g_cos_pre followed by narrow
#   (ext-work/proto/proto_turn2.py), not redesigned, and its definitions are those of DRAFT2-Graph.v; like sin32's
#   and cos32's tables it leaves out the prototype's first product u * 1.0, which is exact, and it evaluates only
#   the selected one of S and C where the prototype computes both.
#   python -B emit_sincos32.py coq [-]   the Coq graph, Graph.v ("-": to stdout, byte for byte; else beside this script)
#   python -B emit_sincos32.py py [-]    reads lines "<sin|cos> <8 hex digits>" (a function and a binary32 bit
#                                        pattern) from stdin and prints "<sin|cos> <input> <16 hex: the binary64
#                                        value before narrow> <8 hex: the binary32 result>"
# Step kinds beyond sin32's and cos32's tables: a selection ('if', a, b, then, else: if a <= b then .. else ..), a
# bare result (a constant or a call with no operation), unary minus ('neg'), 'abs', a call of an earlier definition
# of this table ('call'), and a call of one of sin32's stages ('sin32'). Both renderings read the same entries,
# the comparisons included.
# The py mode evaluates sin32's two stages from sin32's own table and takes PH from cos32's own table: it loads
# their generators (emit_sin32.py, emit_cos32.py), found beside this folder (../sin32/, ../cos32/) or, in the
# development area, at ../../sin32/src/ and ../../cos32/src/. The coq mode loads nothing.
# Standard library only. Author: the assistant.
import importlib.util, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CONSTS = (('turn_CN', 6755399441055744),  # 1.5 * 2^52: adding and subtracting it gives the nearest whole number
          ('turn_BIG', 8388608))          # 2^23: from here on every binary32 number is a whole number
EXT = {'cos32_PH': ('cos32', 'PH')}       # imported constants: name in Coq -> (generator, name in its CONSTS)
SIN32_IN = {'sq': 'x', 'poly': 'u'}       # sin32's stages and the variable each reads in sin32's table
X, V = ('var', 'x'), ('var', 'v')
def call(name, arg): return ('call', name, arg)
K, S, C = call('turn_k', X), call('turn_S', X), call('turn_C', X)
def pre(big, k0, kpos, kneg, k2):
    """The selection both functions share: by |x| against 2^23, then by |k| against 0 and 1 and k against 0."""
    return ('if', ('const', 'turn_BIG'), ('abs', X), big,
            ('if', ('abs', K), ('lit', 0), k0,
             ('if', ('abs', K), ('lit', 1), ('if', ('lit', 0), K, kpos, kneg), k2)))
DEFS = [     # (name, parameter, tree), or None for an empty line: THE table, in the order of Graph.v.
    ('turn_N', 'v', ('sub', ('add', V, ('const', 'turn_CN')), ('const', 'turn_CN'))),
    ('turn_f', 'x', ('sub', X, call('turn_N', X))),
    ('turn_q', 'x', ('mul', ('lit', 4), call('turn_f', X))),
    ('turn_k', 'x', call('turn_N', call('turn_q', X))),
    ('turn_r', 'x', ('sub', call('turn_q', X), K)),
    None,
    ('turn_arg', 'v', ('mul', V, ('ext', 'cos32_PH'))),
    ('turn_core', 'v', ('mul', call('turn_arg', V), ('sin32', 'poly', ('sin32', 'sq', call('turn_arg', V))))),
    ('turn_S', 'x', call('turn_core', call('turn_r', X))),
    ('turn_C', 'x', call('turn_core', ('sub', ('lit', 1), ('abs', call('turn_r', X))))),
    None,
    ('sinturn32_pre', 'x', pre(('mul', X, ('lit', 0)), S, C, ('neg', C), ('neg', S))),
    None,
    ('costurn32_pre', 'x', pre(('lit', 1), C, ('neg', S), S, ('neg', C))),
    None,
    ('g_sinturn32', 'x', ('narrow', call('sinturn32_pre', X))),
    ('g_costurn32', 'x', ('narrow', call('costurn32_pre', X)))]
FUNCS = {'sin': ('sinturn32_pre', 'g_sinturn32'), 'cos': ('costurn32_pre', 'g_costurn32')}
OPS = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}
AT = {'sin32': (os.path.join(HERE, '..', 'sin32', 'emit_sin32.py'), os.path.join(HERE, '..', '..', 'sin32', 'src', 'emit_sin32.py')),
      'cos32': (os.path.join(HERE, '..', 'cos32', 'emit_cos32.py'), os.path.join(HERE, '..', '..', 'cos32', 'src', 'emit_cos32.py'))}

_M = {}
def gen(which):
    """sin32's or cos32's generator module (its table and its float evaluator), loaded once, only for py values."""
    if which not in _M:
        for p in AT[which]:
            if os.path.exists(p):
                spec = importlib.util.spec_from_file_location('emit_' + which, p); m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m); _M[which] = m; break
        else: raise SystemExit('emit_sincos32.py: %s/emit_%s.py not found beside this folder' % (which, which))
    return _M[which]
def find(name):
    hit = [d for d in DEFS if d is not None and d[0] == name]; assert len(hit) == 1, name
    return hit[0]
def py_whole(n):
    v = float(n); assert isinstance(n, int) and 0 <= n < 2 ** 53 and int(v) == n, n      # exact as a binary64
    return v
def py_stage(name, val):
    """One stage of sin32's table (its STEPS) with Python floats, its input variable bound to val; the last target."""
    S32 = gen('sin32'); env = {SIN32_IN[name]: val}; out = None
    for st, t, e in S32.STEPS:
        if st == name: env[t] = S32.py_tree(e, env); out = t
    return env[out]
def narrow(v): return struct.unpack('<f', struct.pack('<f', v))[0]       # the IEEE conversion, as proto.py has it
def py_tree(e, env):
    k = e[0]
    if k == 'var': return env[e[1]]
    if k == 'lit': return py_whole(e[1])
    if k == 'const': return py_whole(dict(CONSTS)[e[1]])
    if k == 'ext': return gen(EXT[e[1]][0]).py_const(EXT[e[1]][1])
    if k == 'call': return py_def(e[1], py_tree(e[2], env))
    if k == 'sin32': return py_stage(e[1], py_tree(e[2], env))
    if k == 'narrow': return narrow(py_tree(e[1], env))
    if k == 'abs': return abs(py_tree(e[1], env))
    if k == 'neg': return -py_tree(e[1], env)
    if k == 'if': return py_tree(e[3], env) if py_tree(e[1], env) <= py_tree(e[2], env) else py_tree(e[4], env)
    a, b = py_tree(e[1], env), py_tree(e[2], env)
    return a + b if k == 'add' else a - b if k == 'sub' else a * b if k == 'mul' else a / b
def py_def(name, val):
    """The definition called name of the table with Python floats (binary64, round to nearest even) at val."""
    _, par, tree = find(name)
    return py_tree(tree, {par: val})
def py_y(fn, x): return py_def(FUNCS[fn][0], x)         # the binary64 value before narrow
def py_g(fn, x): return py_def(FUNCS[fn][1], x)         # the binary32 result
def f32(u): return struct.unpack('<f', struct.pack('<I', u))[0]
def u32(x): return struct.unpack('<I', struct.pack('<f', x))[0]
def bits(d): return struct.unpack('<Q', struct.pack('<d', d))[0]

def strip(b): return b[1:-1] if b.startswith('(') and b.endswith(')') else b
def coq_tree(e):
    """A tree as an operand: a name or a whole number bare, anything else in one pair of parentheses."""
    k = e[0]
    if k == 'var': return e[1]
    if k == 'lit': assert isinstance(e[1], int) and e[1] >= 0; return '%d' % e[1]
    if k == 'const': assert e[1] in dict(CONSTS); return e[1]
    if k == 'ext': assert e[1] in EXT; return e[1]
    if k == 'call': find(e[1]); return '(%s %s)' % (e[1], coq_tree(e[2]))
    if k == 'sin32': assert e[1] in SIN32_IN; return '(sin32_%s %s)' % (e[1], coq_tree(e[2]))
    if k == 'narrow': return '(narrow %s)' % coq_tree(e[1])
    if k == 'abs': return '(Rabs %s)' % coq_tree(e[1])
    if k == 'neg': return '(- %s)' % coq_tree(e[1])
    if k == 'if': return '(%s then %s else %s)' % (coq_test(e), coq_branch(e[3]), coq_branch(e[4]))
    return '(RN64 (%s %s %s))' % (coq_tree(e[1]), OPS[k], coq_tree(e[2]))
def coq_test(e): return 'if Rle_dec %s %s' % (coq_tree(e[1]), coq_tree(e[2]))
def coq_branch(e): return coq_tree(e) if e[0] == 'if' else strip(coq_tree(e))
def coq_body(e):
    """The right-hand side of a definition: on the same line, or, for a selection, one line per case."""
    if e[0] != 'if': return ' ' + strip(coq_tree(e))
    L = []; lead = 'if'
    while e[0] == 'if':
        L.append('  %s%s then %s' % ('' if lead == 'if' else 'else ', coq_test(e), coq_branch(e[3]))); lead = 'else'; e = e[4]
    L.append('  else %s' % coq_branch(e))
    return chr(10) + chr(10).join(L)
def coq_text():
    """The Coq graph from the table: a constant is its whole number, written out; every binary64 operation is one
    RN64 of its exact operands; Rabs and unary minus are exact; a selection is Rle_dec of its two operands; each
    entry of the table is one definition, called by name in the later ones; the two functions are narrow of the
    two selections."""
    L = ['(* Generated by sincos32/emit_sincos32.py coq; do not edit. The operation graph of sinturn32 and costurn32 in the',
         '   FLT model of binary64 (no overflow, no sign of zero), from the one table of steps that the script also',
         '   evaluates with Python floats. The angle is in TURNS: about sin (2 pi x) and cos (2 pi x). The definitions are',
         '   those of ext-work/sincos32/src/DRAFT2-Graph.v, which follow the prototype ext-work/proto/proto_turn2.py with',
         '   two differences: the polynomial is sin32_poly, which leaves out the prototype\'s first product u * 1.0, and',
         '   only the selected one of S and C is written where the prototype computes both.',
         '',
         '   turn_N v    (v + 1.5 * 2^52) - 1.5 * 2^52, two binary64 operations: for |v| < 2^23 a whole number within',
         '               1/2 of v. The definition is total; the graph uses it only for |x| < 2^23.',
         '   turn_f x    x minus turn_N x: the fraction of a turn.          turn_q x    4 * f: the angle in quarter turns.',
         '   turn_k x    turn_N of q.                                       turn_r x    q - k.',
         '   turn_arg v  v * cos32_PH, one binary64 operation (cos32_PH: the binary64 number nearest pi/2, the definition',
         '               of MKF.cos32.Graph, imported, not copied; it is not a whole number).',
         '   turn_core v turn_arg v times sin32\'s polynomial at its square (sin32_poly, sin32_sq: the definitions of',
         '               MKF.sin32.Graph, imported, not copied): about sin (pi/2 * v).',
         '   turn_S x    core r, about sin (pi/2 r).     turn_C x    core (1 - |r|), about cos (pi/2 r); 1 - |r| is one',
         '               binary64 operation and is not always exact.',
         '   The selections are comparisons: 2^23 <= |x| (sine: x * 0, one binary64 operation; cosine: 1), then',
         '   |k| <= 0, |k| <= 1 and 0 <= k:    sine:   S;  C or - C;  - S        cosine:   C;  - S or S;  - C',
         '   Rabs and unary minus are exact. That k is one of -2 .. 2, that f, q and r are exact, and what the selected',
         '   value is close to are facts for a proof; this file shows none of them. *)',
         'From Coq Require Import Reals.', 'From Flocq Require Import Core.', 'From MKF.p32 Require Import Graphs.',
         'From MKF.sin32 Require Import Graph.', 'From MKF.cos32 Require Import Graph.', 'Open Scope R_scope.', '']
    for name, n in CONSTS:
        py_whole(n); L.append('Definition %s : R := %d.' % (name, n))
    L.append('')
    for d in DEFS:
        if d is None: L.append('')
        else: L.append('Definition %s (%s : R) : R :=%s.' % (d[0], d[1], coq_body(d[2])))
    return (chr(10).join(L) + chr(10)).encode('utf-8')
def coq():
    if len(sys.argv) > 2 and sys.argv[2] == '-': sys.stdout.buffer.write(coq_text())
    else: open(os.path.join(HERE, 'Graph.v'), 'wb').write(coq_text()); print('wrote Graph.v')
def py():
    out = []
    for line in sys.stdin.buffer.read().decode('ascii').split(chr(10)):
        if not line.strip(): continue
        fn, h = line.split(); u = int(h, 16); y = py_y(fn, f32(u))
        out.append('%s %08x %016x %08x' % (fn, u, bits(y), u32(py_g(fn, f32(u)))))
    sys.stdout.buffer.write((chr(10).join(out) + chr(10)).encode('ascii'))

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] in ('coq', 'py'): {'coq': coq, 'py': py}[sys.argv[1]]()
    else: print('usage: emit_sincos32.py coq [-] | py [-]'); sys.exit(2)
