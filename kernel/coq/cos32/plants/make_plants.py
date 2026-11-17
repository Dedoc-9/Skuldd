# The plants of cos32's gate and the folder's gate.json, from one table (2026-11-16). Author: the assistant.
#   python3 -B cos32/plants/make_plants.py json          prints gate.json
#   python3 -B cos32/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B cos32/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B cos32/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B cos32/plants/make_plants.py list          one line per plant
# The form is sin32/plants/make_plants.py's. A plant is one source of the folder with ONE change (the whole of
# Cos32.v for other-statement and guard), put in place of that source; the gate must refuse it for the reason its
# entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T;
#   "generated": P           the planted file is not what P's generator prints.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Cos32.v or
# PiBound.v is held to that line's text here: if the source moves, this script stops and says where.
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement or the graph is refused where the proof script no longer fits it. That is not a proof that the changed
# statement is false. Each entry's "what" says which are known false and how (MEASURED means
# ext-work/cos32/measure-plants-run1.txt and measure-correct-run1.txt: the graph evaluated with Python floats against an 80-digit reference, by
# the assistant; that the Python rendering is the Coq graph is argued, not shown), and which are only refused by the
# route of the proof. The row that holds the statement itself is the gate's hash row, not a plant.
# The gate is gate/gate4.py alone, the anchored one, run on the tree mkf-ext/: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = '61f0ceda3d3483166a1e7ad90d3eea06f59a93e1aec96197342040d7f56b9113'
DEPS = ['f32', 'p32', 'p32r', 'sin32']
FILES = ['Graph.v', 'COS32_Statement.v', 'PiBound.v', 'Cos32.v', 'Identity.v']
G, S, B, C = 'Graph.v', 'COS32_Statement.v', 'PiBound.v', 'Cos32.v'
ME = 'cos32/plants/make_plants.py'

# Lines that a refusal is pinned to: (file, line, text that line must hold).
PINS = {
    'pi-close': (B, 107, 'apply Rabs_le. unfold cos32_PH, cos32_PL. lra.'),
    'shift-close': (C, 96, 'split; [lra | split; [lra |]].'),
    'shift-range': (C, 97, 'apply Rabs_le_inv in Pf. apply Rabs_le. unfold T. unfold cos32_PH, cos32_PL in Pf. lra.'),
    'faithful-intros': (C, 184, 'unfold COS32, g_cos32. intros x Fx Hx.'),
    'faithful-f32': (C, 187, 'rewrite (T32_proof y Fy). apply (F32_rel (cos x) y). exact (cos32_core x Fx Hx).'),
    'finite-intros': (C, 192, 'unfold COS32_FINITE. intros x Fx Hx.'),
    'finite-apply': (C, 193, 'apply (faithful_finite (cos x)); [| apply cos32_faithful; assumption].'),
}
def at(pin): return 'cos32/%s", line %d, characters' % (PINS[pin][0], PINS[pin][1])

COS32_BODY = 'forall x : R, format32 x -> Rabs x <= CMAX -> faithful32 (cos x) (g_cos32 x).'
FINITE_BODY = 'forall x : R, format32 x -> Rabs x <= CMAX -> finite32 (g_cos32 x).'
PI_LO_HEAD = 'Lemma pi_lo : Q1 < PI / 2.\n'
PI_LO_AXIOM = 'Axiom pi_lo : Q1 < PI / 2.\n'
OTHER = '''(* Plant: under the name COS32_ALL, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.cos32 Require Import COS32_Statement.
Definition COS32_ALL : Prop := True.
Theorem cos32_all : COS32_ALL.
Proof. exact I. Qed.
'''
GUARD = '''(* Plant: COS32_ALL from False, by a recursion whose termination check is switched off. *)
From MKF.cos32 Require Import COS32_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem cos32_all : COS32_ALL.
Proof. exact (False_ind _ (loop 0)). Qed.
'''

# (name, class, source, changes or whole text, expectation, what)
# A change is (old, new): old occurs exactly once; or ('cut', first, last, new): the text from the one occurrence of
# first up to the next occurrence of last after it (last itself kept) becomes new.
PLANTS = [
    # (a) the graph: one constant or one operation changed
    ('no-pl', 'a graph', G,
     [('RN64 ((RN64 (cos32_PH - (Rabs x))) + cos32_PL).', 'RN64 (cos32_PH - (Rabs x)).')],
     ('fails', 'Cos32', at('shift-close')),
     'the shift without its second constant: t = RN64(PH - |x|). NOT known false: MEASURED on 68,001 inputs, 8,001 '
     'of them around the binary32 pi/2, 0 not faithful (without PL the shifted argument is off by 6.1e-17, at most '
     '1.4e-9 of it, under the 7.45e-9 the route allows). Refused only by the route of the proof: the shift no '
     'longer has the two roundings the proof walks'),
    ('ph-ulp', 'a graph', G,
     [('Definition cos32_PH : R := 7074237752028440 /', 'Definition cos32_PH : R := 7074237752028441 /')],
     ('fails', 'PiBound', at('pi-close')),
     'PH one unit in the last place up. NOT known false: MEASURED on the same 68,001 inputs, 0 not faithful (the '
     'shifted argument is off by 2.2e-16, at most 5.1e-9 of it). Refused where PH + PL must lie within 2^-60 of '
     'PI/2: the planted sum is 2^-52 away'),
    ('ph-binary32', 'a graph', G,
     [('Definition cos32_PH : R := 7074237752028440 / 4503599627370496.', 'Definition cos32_PH : R := 13176795 / 8388608.')],
     ('fails', 'PiBound', at('pi-close')),
     'PH is the binary32 number nearest pi/2 (a shift done with a binary32 constant). KNOWN FALSE, MEASURED: at '
     'x = 3FC90FDB the planted graph gives 248D3132 (about 6.1e-17, the constant PL alone) and cos x lies between '
     'B33BBD2F and B33BBD2E (about -4.37e-8). Refused where PH + PL must lie within 2^-60 of PI/2'),
    ('plus-for-minus', 'a graph', G,
     [('(RN64 (cos32_PH - (Rabs x)))', '(RN64 (cos32_PH + (Rabs x)))')],
     ('fails', 'Cos32', at('shift-close')),
     'the shift is PH + |x| for PH - |x| (x + pi/2: the argument leaves sin32\'s interval). KNOWN FALSE, MEASURED: '
     'at x = 3 (40400000) the planted graph gives BF7D8CF0 and cos 3 lies between BF7D7026 and BF7D7025. Refused '
     'where the proof meets the shift'),
    # (b) the graph edited by hand against its generator
    ('hand-edited-graph', 'b generated', G,
     [('Definition cos32_PH : R := 7074237752028440 / 4503599627370496.\n', 'Definition cos32_PH : R := 7074237752028440 / 4503599627370496. \n')],
     ('generated', 'cos32/Graph.v'),
     'Graph.v with one blank added at the end of a line: the same graph for Coq, and not what emit_cos32.py prints'),
    # (c) a premise of the statement dropped or widened
    ('prem-no-cmax', 'c premise', S,
     [(COS32_BODY, 'forall x : R, format32 x -> faithful32 (cos x) (g_cos32 x).')],
     ('fails', 'Cos32', at('faithful-intros')),
     'COS32 without |x| <= CMAX. KNOWN FALSE, MEASURED: at x = 8 (41000000) the graph gives BC0989CE and cos 8 '
     'lies between BE14FDF6 and BE14FDF5. Refused where the proof takes the premise'),
    ('prem-cmax-2x', 'c premise', S,
     [('Definition CMAX : R := 13176794 / 4194304.', 'Definition CMAX : R := 13176794 / 2097152.')],
     ('fails', 'Cos32', at('shift-range')),
     'CMAX doubled (about 2 pi). KNOWN FALSE, MEASURED: at x = 6 (40C00000) the graph gives 3F75DEA5 and cos 6 '
     'lies between 3F75CDB8 and 3F75CDB9. Refused where the proof needs |PI/2 - |x|| <= 63/40'),
    ('prem-finite-no-cmax', 'c premise', S,
     [(FINITE_BODY, 'forall x : R, format32 x -> finite32 (g_cos32 x).')],
     ('fails', 'Cos32', at('finite-intros')),
     'COS32_FINITE without |x| <= CMAX. False, ARGUED and not evaluated: the model has no overflow, and at '
     'x = 2^127 the shifted argument is about -2^127 and the polynomial is of the order of its 14th power, far '
     'above FMAX32. Refused where the proof takes the premise'),
    # (d) the conclusion strengthened
    ('concl-round-down', 'd conclusion', S,
     [('faithful32 (cos x) (g_cos32 x).', 'g_cos32 x = RD32 (cos x).')],
     ('fails', 'Cos32', at('faithful-f32')),
     'COS32 says the result is cos x rounded DOWN. KNOWN FALSE, MEASURED: at x = 3F800001 the graph gives '
     '3F0A513F and cos x rounded down is 3F0A513E. Refused where lemma F32 no longer fits'),
    ('concl-correct', 'd conclusion', S,
     [('faithful32 (cos x) (g_cos32 x).', 'g_cos32 x = RN32 (cos x).')],
     ('fails', 'Cos32', at('faithful-f32')),
     'COS32 claims the correctly rounded result. KNOWN FALSE, MEASURED (measure-correct-run1.txt): at '
     'x = 3D4CF17D the graph gives 3F7FADFB and the correctly rounded cos x is 3F7FADFC (the first such input found '
     'going up from 3D4CCCCD, after 9,393; none in 2,000,000 going up from 1). Refused where lemma F32 no longer fits'),
    ('concl-finite-half', 'd conclusion', S,
     [('finite32 (g_cos32 x).', 'Rabs (g_cos32 x) <= / 2.')],
     ('fails', 'Cos32', at('finite-apply')),
     'COS32_FINITE says the result is at most 1/2 in magnitude. KNOWN FALSE, MEASURED: at x = 0 (00000000) the '
     'graph gives 1 (3F800000). Refused where faithful_finite no longer fits'),
    # (e), (f), (g), (h) a proof left out, an assumption put in, another statement under the name, a check switched off
    ('admitted', 'e proof', C,
     [('  destruct (abs_near (h * Pex (h * h)) (sin h)) as [_ N]. lra.\nQed.\n', '  destruct (abs_near (h * Pex (h * h)) (sin h)) as [_ N].\nAdmitted.\n')],
     ('reader', 'Cos32.sin_abs_le :', ['Admitted']),
     'Cos32.sin_abs_le (|sin h| <= |h| (1 + 2^-37)) ends with Admitted for its last step'),
    ('pi-axiom', 'f axiom', B,
     [('cut', PI_LO_HEAD, 'Lemma pi_hi', PI_LO_AXIOM + '\n')],
     ('reader', 'PiBound.pi_lo :', ['Axiom']),
     'the lower bound on pi, pi_lo, is an Axiom of PiBound.v (the same text, its proof removed), used by the top '
     'theorem through pi_fact'),
    ('other-statement', 'g identity', C, OTHER,
     ('fails', 'Identity', 'has type "Cos32.COS32_ALL"'),
     'Cos32.v states, under the name COS32_ALL, the proposition True and proves that'),
    ('guard', 'h guard', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'cos32_all from False, by a recursion whose termination check is switched off'),
]
NAMES = [p[0] for p in PLANTS]

class Stop(Exception): pass

def raw(f):
    with open(os.path.join(DIR, f), 'rb') as fh: return fh.read()
def plant_path(name, src): return 'plants/%s_%s.v' % (src[:-2], name.replace('-', '_'))

def check_sources():
    if hashlib.sha256(raw(S)).hexdigest() != STATEMENT_SHA256:
        raise Stop('%s is not the frozen statement %s' % (S, STATEMENT_SHA256))
    lines = {f: raw(f).decode('utf-8').split('\n') for f in (B, C)}
    for pin, (f, n, text) in sorted(PINS.items()):
        if n > len(lines[f]) or text not in lines[f][n - 1]:
            raise Stop('%s line %d does not hold %r (pin %s)' % (f, n, text, pin))

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
    L = ['{"name": "COS32", "tier": "flocq4", "deps": %s,' % d(DEPS),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {', '  "cos32/Graph.v": %s,' % d(['cos32/emit_cos32.py', 'coq', '-']),
         '  "cos32/gate.json": %s,' % d([ME, 'json'])]
    L += ['  %s: %s%s' % (d('cos32/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
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
                print('wrote cos32/%s %s' % (path, hashlib.sha256(b).hexdigest()))
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
