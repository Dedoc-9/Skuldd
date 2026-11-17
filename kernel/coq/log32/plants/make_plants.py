# The plants of log32's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B log32/plants/make_plants.py json          prints gate.json
#   python3 -B log32/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B log32/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B log32/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B log32/plants/make_plants.py list          one line per plant
# The form is compose/plants/make_plants.py's and sin32/plants/make_plants.py's. A plant is one source of the folder
# with ONE change (the whole of Log32.v for other-statement and guard), put in place of that source; the gate must
# refuse it for the reason its entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T;
#   "generated": P           the planted file is not what P's generator prints.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Log32.v
# is held to that line's text here: if the source moves, this script stops and says where.
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement or the graph is refused where the proof script no longer fits it. That is not a proof that the changed
# statement is false. Each entry's "what" says which are known false and how (MEASURED means
# ext-work/log32/measure-plants-run2.txt: the graph evaluated with Python floats against ln at 60 digits, by the
# assistant; that the Python rendering is the Coq graph is argued, not shown), and which are argued only.
# The row that holds the statement itself is the gate's hash row, not a plant.
# The gate is gate/gate4.py alone, the anchored one, run on the tree mkf-ext/: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = 'c33065a24fcdcb94163c6b64b7fbf1dbb00750454ffc9270cf19163866222930'
DEPS = ['f32', 'p32', 'p32r']
FILES = ['Graph.v', 'LOG32_Statement.v', 'Trunc.v', 'Log32.v', 'Identity.v']
G, S, T, C = 'Graph.v', 'LOG32_Statement.v', 'Trunc.v', 'Log32.v'
ME = 'log32/plants/make_plants.py'

# Lines of Log32.v that a refusal is pinned to: (line, text that line must hold).
PINS = {
    'p-last': (322, 'apply (rel_rnd (m * / 105) _ (18 * CC)); [exact Z5 | exact M5 | lra | lra].'),
    'faithful-intros': (577, 'unfold LOG32, g_log32, log32_y, log32_k. intros x Fx H0 H1.'),
    'one-branch': (580, '+ subst x. rewrite z_one, p_zero, Rmult_0_r, (round_0 radix2 fexp64 ZnearestE), ln_1.'),
    'one-f32': (582, 'apply (F32_rel 0 0). rewrite Rminus_0_r, Rabs_R0, Rmult_0_r. apply Rle_refl.'),
    'far-change': (587, 'change (faithful32 (ln x) (narrow (RN64 (8192 * log32_p (log32_z (rt12 x)))))).'),
    'far-exact': (590, 'rewrite (T32_proof v Fv). apply (F32_rel (ln x) v). exact (far_core x Fx H0 H1 Nr).'),
    'finite-apply': (596, 'apply (faithful_finite (ln x)); [| apply log32_faithful; assumption].'),
}
def at(pin): return 'log32/Log32.v", line %d, characters' % PINS[pin][0]

LOG32_BODY = 'forall x : R, format32 x -> 0 < x -> x < bpow radix2 128 -> faithful32 (ln x) (g_log32 x).'
HZ_POS_HEAD = 'Lemma hz_pos (z : R) : 0 < z <= 1 / 31 -> 0 <= hz z <= z * / 274877906944.\n'
HZ_POS_AXIOM = 'Axiom hz_pos : forall z : R, 0 < z <= 1 / 31 -> 0 <= hz z <= z * / 274877906944.\n'
OTHER = '''(* Plant: under the name LOG32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.log32 Require Import LOG32_Statement.
Definition LOG32_ALL : Prop := True.
Theorem log32_all : LOG32_ALL.
Proof. exact I. Qed.
'''
GUARD = '''(* Plant: LOG32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.log32 Require Import LOG32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem log32_all : LOG32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
'''

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) the graph: one constant or one operation changed
    ('k-4096', 'a graph', G,
     [('if log32_near x then 2 else 8192.', 'if log32_near x then 2 else 4096.')],
     ('fails', 'Log32', at('far-change')),
     'the far path multiplies by 4096 for 8192 (half the logarithm). KNOWN FALSE, MEASURED: at x = 2 (40000000) the '
     'planted graph gives 3EB17218 and ln 2 lies between 3F317217 and 3F317218. Refused where the proof names the '
     'far path\'s last operation'),
    ('add-for-mul', 'a graph', G,
     [('narrow (RN64 (log32_k x * log32_p (log32_z (log32_y x)))).', 'narrow (RN64 (log32_k x + log32_p (log32_z (log32_y x)))).')],
     ('fails', 'Log32', at('one-branch')),
     'the last operation is k + p for k * p. KNOWN FALSE, MEASURED: at x = 1 the planted graph gives 2 (40000000) '
     'and ln 1 = 0. Refused where the proof meets the last operation at x = 1'),
    ('coef-36', 'a graph', G,
     [('(RN64 (35 + ', '(RN64 (36 + ')],
     ('fails', 'Log32', at('p-last')),
     'the z^3 coefficient is 36/105 for 35/105 = 1/3. KNOWN FALSE, MEASURED: at x = 15/16 (3F700000) the planted '
     'graph gives BD842D1B and ln x lies between BD842CC6 and BD842CC5. Refused where the levels the proof walked '
     'no longer are the graph\'s'),
    # (b) the graph edited by hand against its generator
    ('hand-edited-graph', 'b generated', G,
     [('Definition log32_rt (y : R) : R := RN64 (sqrt y).\n', 'Definition log32_rt (y : R) : R := RN64 (sqrt y). \n')],
     ('generated', 'log32/Graph.v'),
     'Graph.v with one blank added at the end of a line: the same graph for Coq, and not what emit_log32.py prints'),
    # (c) a premise of the statement dropped or widened
    ('prem-no-upper', 'c premise', S,
     [(LOG32_BODY, 'forall x : R, format32 x -> 0 < x -> faithful32 (ln x) (g_log32 x).')],
     ('fails', 'Log32', at('faithful-intros')),
     'LOG32 without x < 2^128. False, ARGUED with its last part MEASURED: x = 2^40960 is in the model\'s format32; '
     'its twelve square roots are exact powers of two and give y = 1024 (argued); from y = 1024 the graph\'s value '
     'before narrow is 13667.60 (MEASURED) and ln x is 28391.31. Refused where the proof takes the premise'),
    ('prem-zero', 'c premise', S,
     [('format32 x -> 0 < x -> x < bpow radix2 128 -> faithful32', 'format32 x -> 0 <= x -> x < bpow radix2 128 -> faithful32')],
     ('fails', 'Log32', at('far-exact')),
     'LOG32 with 0 <= x for 0 < x. KNOWN FALSE at x = 0: the graph gives C6568D69 = -13731.35 (MEASURED) and Coq\'s '
     'ln 0 is 0 by its definition (READ: Rpower.ln is 0 outside 0 < x). Refused where the far path needs 0 < x'),
    # (d) the conclusion strengthened
    ('concl-round-down', 'd conclusion', S,
     [('faithful32 (ln x) (g_log32 x).', 'g_log32 x = RD32 (ln x).')],
     ('fails', 'Log32', at('one-f32')),
     'LOG32 says the result is ln x rounded DOWN. KNOWN FALSE, MEASURED: at x = 2 (40000000) the graph gives '
     '3F317218 and ln 2 rounded down is 3F317217. Refused where lemma F32 no longer fits'),
    ('concl-correct', 'd conclusion', S,
     [('faithful32 (ln x) (g_log32 x).', 'g_log32 x = RN32 (ln x).')],
     ('fails', 'Log32', at('one-f32')),
     'LOG32 claims the correctly rounded result. KNOWN FALSE, MEASURED: at x = 40014123 the graph gives 3F33F13D '
     'and the correctly rounded ln x is 3F33F13E (the first such input found going up from 2, after 82,211). '
     'Refused where lemma F32 no longer fits'),
    ('concl-finite-64', 'd conclusion', S,
     [('finite32 (g_log32 x).', 'Rabs (g_log32 x) <= 64.')],
     ('fails', 'Log32', at('finite-apply')),
     'LOG32_FINITE says the result is at most 64 in magnitude. KNOWN FALSE, MEASURED: at x = FMAX32 (7F7FFFFF) the '
     'graph gives 42B17218 = 88.72. Refused where faithful_finite no longer fits'),
    # (e), (f), (g), (h) a proof left out, an assumption put in, another statement under the name, a check switched off
    ('admitted', 'e proof', C,
     [('  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4. lra.\nQed.\n', '  pose proof (rnd_abs _ _ _ _ Z3 A3 B3) as A4.\nAdmitted.\n')],
     ('reader', 'Log32.hstep :', ['Admitted']),
     'Log32.hstep (one level of the polynomial) ends with Admitted for its last step'),
    ('trunc-axiom', 'f axiom', T,
     [('cut', HZ_POS_HEAD, 'Lemma Lz_0 :', HZ_POS_AXIOM + '\n')],
     ('reader', 'Trunc.hz_pos :', ['Axiom']),
     'the mean value step hz_pos is an Axiom of Trunc.v (the same text, its proof removed), used by the top '
     'theorem through atanh_trunc'),
    ('other-statement', 'g identity', C, OTHER,
     ('fails', 'Identity', 'has type "Log32.LOG32_ALL"'),
     'Log32.v states, under the name LOG32_ALL, the proposition True and proves that'),
    ('guard', 'h guard', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'log32_all from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = raw(C).decode('utf-8').split('\n')
    for pin, (n, text) in sorted(PINS.items()):
        if n > len(lines) or text not in lines[n - 1]:
            raise Stop('%s line %d does not hold %r (pin %s)' % (C, n, text, pin))

def plant_bytes(name):
    _, _, src, changes, _, _ = PLANTS[NAMES.index(name)]
    if isinstance(changes, str): return changes.encode('utf-8')
    text = raw(src).decode('utf-8')
    for ch in changes:
        if ch[0] == 'cut' and len(ch) == 4:
            _, first, last, new = ch
            if text.count(first) != 1: raise Stop('plant %s: the start of the cut occurs %d times in %s' % (name, text.count(first), src))
            i = text.index(first); j = text.find(last, i + len(first))
            if j < 0: raise Stop('plant %s: the end of the cut is not after its start in %s' % (name, src))
            text = text[:i] + new + text[j:]
        else:
            old, new = ch
            if text.count(old) != 1: raise Stop('plant %s: the text to change occurs %d times in %s' % (name, text.count(old), src))
            text = text.replace(old, new)
    return text.encode('utf-8')

def gate_json():
    if len(set(NAMES)) != len(NAMES): raise Stop('a plant name is used twice')
    d = json.dumps
    L = ['{"name": "LOG32", "tier": "flocq4", "deps": %s,' % d(DEPS),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {', '  "log32/Graph.v": %s,' % d(['log32/emit_log32.py', 'coq', '-']),
         '  "log32/gate.json": %s,' % d([ME, 'json'])]
    L += ['  %s: %s%s' % (d('log32/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
          for n, p in zip(NAMES, PLANTS)]
    L += [' },', ' "plants": {']
    for name, cls, src, _, exp, what in PLANTS:
        e = {'replace': {src: plant_path(name, src)}}
        if exp[0] == 'fails': e['fails'] = exp[1]; e['text'] = exp[2]
        elif exp[0] == 'generated': e['generated'] = exp[1]
        else: e['reader'] = exp[1]; e['words'] = exp[2]
        e['class'] = cls; e['what'] = what
        L.append('  %s: %s%s' % (d(name), d(e), ',' if name != NAMES[-1] else ''))
    L.append(' }}')
    text = '\n'.join(L) + '\n'
    json.loads(text)
    return text.encode('ascii')

def everything():
    check_sources()
    out = {'gate.json': gate_json()}
    for name, p in zip(NAMES, PLANTS): out[plant_path(name, p[2])] = plant_bytes(name)
    return out

def main():
    a = sys.argv[1:]
    try:
        if a == ['json']:
            check_sources(); sys.stdout.buffer.write(gate_json())
        elif len(a) == 2 and a[0] == 'plant' and a[1] in NAMES:
            check_sources(); sys.stdout.buffer.write(plant_bytes(a[1]))
        elif a == ['write']:
            for path, b in sorted(everything().items()):
                with open(os.path.join(DIR, path), 'wb') as fh: fh.write(b)
                print('wrote log32/%s %s' % (path, hashlib.sha256(b).hexdigest()))
        elif a == ['check']:
            bad = []
            for path, b in sorted(everything().items()):
                try: same = raw(path) == b
                except OSError: same = False
                if not same: bad.append(path)
            have = sorted(f for f in os.listdir(HERE) if f.endswith('.v'))
            want = sorted(os.path.basename(plant_path(n, p[2])) for n, p in zip(NAMES, PLANTS))
            if have != want: bad.append('plants/ holds other .v files than the table\'s: %s' % sorted(set(have) ^ set(want)))
            print('PLANT FILES %s: gate.json and %d plants%s' % ('AS WRITTEN HERE' if not bad else 'DIFFER', len(NAMES), '' if not bad else '; not the same: %s' % ', '.join(bad)))
            return 1 if bad else 0
        elif a == ['list']:
            for name, cls, src, _, exp, what in PLANTS:
                print('%-22s %-13s %-20s %s' % (name, cls, src, what))
        else:
            print('usage: make_plants.py json | plant NAME | write | check | list'); return 2
    except Stop as e:
        sys.stderr.write('make_plants: %s\n' % e); return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
