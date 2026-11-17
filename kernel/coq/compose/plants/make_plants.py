# The plants of compose's gate and the folder's gate.json, from one table (2026-11-15). Author: the assistant.
#   python3 -B compose/plants/make_plants.py json          prints gate.json
#   python3 -B compose/plants/make_plants.py plant NAME    prints the plant NAME's file
#   python3 -B compose/plants/make_plants.py write         writes gate.json and every plant file (binary, LF)
#   python3 -B compose/plants/make_plants.py check         exit 0 only if gate.json and every plant file are these
#   python3 -B compose/plants/make_plants.py list          one line per plant
# The form is ieee64/plants/make_plants.py's. A plant is one source of the folder with ONE change (the whole of
# Compose.v for four-of-five and guard; two places of Compose.v for axiom-landing), put in place of that source; the
# gate must refuse it for the reason its entry states:
#   "fails": M, "text": T    every file before M compiles, M does not, and M's output holds T;
#   "reader": T              every file compiles and the reading of Print Assumptions holds a violation with T.
# gate.json names this script as the generator of itself and of every plant file, so gate4.py runs it and compares
# byte for byte. The text to change must occur exactly once in its source; a refusal pinned to a line of Compose.v
# is held to that line's text here: if the source moves, this script stops and says where.
# WHAT A PLANT SHOWS: that the gate read the new code and refuses that one defect. WHAT IT DOES NOT: a plant on the
# statement is refused where the proof script no longer fits it. That is not a proof that the changed statement is
# false. Each entry's "what" says which changed statements are known false and why, and which are only refused by
# the route of the proof. The row that holds the statement itself is the gate's hash row, not a plant.
# The gate is gate/gate4.py alone, the anchored one, run on the tree mkf-ext/: this folder has no gate of its own.
import hashlib, json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)

STATEMENT_SHA256 = '0b65068d0bd46f5c562fa19dc091440c7c551876893fae5d1f44246ddd1619a4'
DEPS = ['f32', 'p32', 'p32r', 'exp32', 'exp32r', 'ieee64']
FILES = ['COMPOSE_Statement.v', 'Compose.v', 'Identity.v']
S, C = 'COMPOSE_Statement.v', 'Compose.v'
ME = 'compose/plants/make_plants.py'

# Lines of Compose.v that a refusal is pinned to: (line, text that line must hold).
PINS = {
    'narrow-intros': (27, 'intros b Fb Hb. destruct (proj1 ieee64_holds b Fb Hb) as [Fr Vr].'),
    'sqrt-intros': (35, 'intros b Fb H32 H0 Hm. destruct (proj1 (proj2 ieee64_holds) b Fb H32 H0 Hm) as [Fr Vr].'),
    'rsqrt-intros': (43, 'intros b Fb H32 H0 Hm. destruct (proj1 (proj2 (proj2 ieee64_holds)) b Fb H32 H0 Hm) as [Fr Vr].'),
    'hypot-intros': (51, 'intros b1 b2 F1 F2 H1 H2 Hm.'),
    'exp-intros': (64, 'intros b Fb H32 Hm.'),
    'narrow-finite': (29, '- apply narrow_finite; [apply fmt64_b | exact Hb].'),
    'narrow-t32': (30, '- apply T32_proof. apply fmt64_b.'),
    'sqrt-faithful': (38, '- apply sqrt32_faithful; assumption.'),
    'rsqrt-faithful': (46, '- apply rsqrt32_faithful; [assumption | assumption | exact (Rle_lt_trans _ _ _ Hm fmax_lt)].'),
}
def at(pin): return 'compose/Compose.v", line %d, characters' % PINS[pin][0]

E2E_EXP_PROOF = '''  - apply exp32_faithful; assumption.
Qed.

Theorem compose_holds'''
TOP_PROOF = '''Proof.
  exact (conj e2e_narrow (conj e2e_sqrt32 (conj e2e_rsqrt32 (conj e2e_hypot32 e2e_exp32)))).
Qed.
'''
FOUR_OF_FIVE = '''(* Plant: under the name COMPOSE, the proposition True, and its proof. The identity must refuse a theorem of
   another statement that carries the statement's name. *)
From MKF.compose Require Import COMPOSE_Statement.
Definition COMPOSE : Prop := True.
Theorem compose_holds : COMPOSE.
Proof. exact I. Qed.
'''
GUARD = '''(* Plant: COMPOSE from False, by a recursion whose termination check is switched off. *)
From MKF.compose Require Import COMPOSE_Statement.
#[bypass_check(guard)] Fixpoint loop (n : nat) {struct n} : False := loop n.
Theorem compose_holds : COMPOSE.
Proof. exact (False_ind _ (loop 0)). Qed.
'''

# (name, class, source, changes or whole text, expectation, what)
PLANTS = [
    # (a) a premise of the statement dropped or weakened
    ('prem-narrow-no-ovf', 'a premise', S,
     [('forall b : b64, is_finite b = true -> Rabs (B2R b) < OVF32 ->\n  lands32 (G_narrow',
       'forall b : b64, is_finite b = true ->\n  lands32 (G_narrow')],
     ('fails', 'Compose', at('narrow-intros')),
     'E2E_NARROW without |v| < OVF32. Known false: Turn 194 evaluated the IEEE shape at an input of 2^1000 and '
     'the result is not finite. Refused where the proof takes the premise'),
    ('prem-sqrt-neg', 'a premise', S,
     [('format32 (B2R b) -> 0 <= B2R b -> B2R b <= FMAX32 ->\n  lands32 (G_sqrt32',
       'format32 (B2R b) -> B2R b <= FMAX32 ->\n  lands32 (G_sqrt32')],
     ('fails', 'Compose', at('sqrt-intros')),
     'E2E_SQRT32 without 0 <= x. False by Flocq\'s definition (Bsqrt of a negative number is NaN, not finite); '
     'not evaluated here. Refused where the proof takes the premise'),
    ('prem-rsqrt-at-zero', 'a premise', S,
     [('format32 (B2R b) -> 0 < B2R b -> B2R b <= FMAX32 ->\n  lands32 (G_rsqrt32',
       'format32 (B2R b) -> 0 <= B2R b -> B2R b <= FMAX32 ->\n  lands32 (G_rsqrt32')],
     ('fails', 'Compose', '"0 <= B2R b" while it is expected to have type'),
     'E2E_RSQRT32 with 0 <= x for 0 < x. False at 0 by Flocq\'s definition (1 / 0 is an infinity); refused where '
     'the proof gives the premise to ieee64\'s theorem'),
    ('prem-hypot-no-range', 'a premise', S,
     [('format32 (B2R b1) -> format32 (B2R b2) ->\n  sqrt (B2R b1 * B2R b1 + B2R b2 * B2R b2) <= FMAX32 ->\n  lands32',
       'format32 (B2R b1) -> format32 (B2R b2) ->\n  lands32')],
     ('fails', 'Compose', at('hypot-intros')),
     'E2E_HYPOT32 without its range premise. False (x * x overflows for a large x; ieee64\'s plant of the same '
     'name). Refused where the proof takes the premise'),
    ('prem-exp-no-xmax', 'a premise', S,
     [('forall b : b64, is_finite b = true -> format32 (B2R b) -> B2R b <= XMAX ->',
       'forall b : b64, is_finite b = true -> format32 (B2R b) ->')],
     ('fails', 'Compose', at('exp-intros')),
     'E2E_EXP32 without x <= XMAX. False (the squarings overflow for a large x). Refused where the proof takes '
     'the premise'),
    # (b) a conclusion changed
    ('concl-narrow-rd', 'b conclusion', S,
     [('B2R (G_narrow b64 ieee_ops b) = RN32 (B2R b).', 'B2R (G_narrow b64 ieee_ops b) = RD32 (B2R b).')],
     ('fails', 'Compose', at('narrow-t32')),
     'E2E_NARROW with round down for round to nearest even. False wherever the two differ (T32 is proved); '
     'refused where T32\'s theorem no longer fits'),
    ('concl-sqrt-of-x', 'b conclusion', S,
     [('faithful32 (sqrt (B2R b)) (B2R (G_sqrt32 b64 ieee_ops b)).',
       'faithful32 (B2R b) (B2R (G_sqrt32 b64 ieee_ops b)).')],
     ('fails', 'Compose', at('sqrt-faithful')),
     'E2E_SQRT32 says the result is a faithful rounding of x, not of sqrt x. False at x = 4 (the result is 2, '
     'argued from SQRT32, not evaluated); refused where SQRT32\'s theorem no longer fits'),
    ('concl-rsqrt-is-sqrt', 'b conclusion', S,
     [('faithful32 (/ sqrt (B2R b)) (B2R (G_rsqrt32 b64 ieee_ops b)).',
       'faithful32 (sqrt (B2R b)) (B2R (G_rsqrt32 b64 ieee_ops b)).')],
     ('fails', 'Compose', at('rsqrt-faithful')),
     'E2E_RSQRT32 says the result is a faithful rounding of sqrt x, not of 1 / sqrt x. False at x = 4 (argued); '
     'refused where RSQRT32\'s theorem no longer fits'),
    ('concl-exp-correct', 'b conclusion', S,
     [('lands32 (G_exp32 b64 ieee_ops b) /\\ faithful32 (exp (B2R b)) (B2R (G_exp32 b64 ieee_ops b)).',
       'lands32 (G_exp32 b64 ieee_ops b) /\\ B2R (G_exp32 b64 ieee_ops b) = RN32 (exp (B2R b)).')],
     ('fails', 'Compose', 'Unable to unify "EXP32" with'),
     'E2E_EXP32 claims the correctly rounded result, which the tier does not prove. NOT known false at any given '
     'input: refused only because the proof has no such theorem to apply'),
    # NOT A PLANT OF THIS TABLE, and kept here as a warning: lands32 with format32 for finite32 (the bound FMAX32
    # dropped) is a WEAKER statement that is true, and the unchanged proof script proves it: all three files compile
    # and the identity is accepted (compose-work/try-plants-run1.txt, "lands-format-only", exits 0 0 0). No compile
    # row can refuse a weaker statement put under the same name. What refuses it is the hash of the statement:
    # gate4.py's rows "frozen inputs unchanged" and "freeze list is the anchored one", when ANCHOR is given.
    # (c) a proof left out, an assumption put in, another statement under the name
    ('admitted-part', 'c proof', C,
     [(E2E_EXP_PROOF, 'Admitted.\n'
       'Lemma e2e_exp32_rest : forall b : b64, is_finite b = true -> format32 (B2R b) -> B2R b <= XMAX ->\n'
       '  faithful32 (exp (B2R b)) (g_exp32 (B2R b)).\n'
       'Proof.\n  intros b Fb H32 Hm.\n' + E2E_EXP_PROOF)],
     ('reader', 'Compose.e2e_exp32 :', ['Admitted']),
     'Compose.e2e_exp32 ends with Admitted (the last line of its proof moved to another lemma)'),
    ('admitted-top', 'c proof', C,
     [(TOP_PROOF, 'Proof.\nAdmitted.\n')],
     ('reader', 'Compose.compose_holds :', ['Admitted']),
     'the top theorem compose_holds ends with Admitted'),
    ('axiom-landing', 'c proof', C,
     [('Lemma e2e_narrow : E2E_NARROW.\n', 'Axiom rn_lands : forall v : R, finite32 (narrow v).\n'
       'Lemma e2e_narrow : E2E_NARROW.\n'),
      ('  - apply narrow_finite; [apply fmt64_b | exact Hb].\n', '  - apply rn_lands.\n')],
     ('reader', 'Compose.rn_lands :', ['Axiom']),
     'that narrow\'s value is a finite binary32 number for every real input is an Axiom of Compose.v (false for a '
     'large input), used by E2E_NARROW\'s proof'),
    ('other-statement', 'c proof', C, FOUR_OF_FIVE,
     ('fails', 'Identity', 'has type "Compose.COMPOSE"'),
     'Compose.v states, under the name COMPOSE, the proposition True and proves that'),
    ('guard', 'c proof', C, GUARD,
     ('reader', 'is assumed to be guarded', ['bypass_check']),
     'compose_holds from False, by a recursion whose termination check is switched off'),
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
    for old, new in changes:
        if text.count(old) != 1: raise Stop('plant %s: the text to change occurs %d times in %s' % (name, text.count(old), src))
        text = text.replace(old, new)
    return text.encode('utf-8')

def gate_json():
    if len(set(NAMES)) != len(NAMES): raise Stop('a plant name is used twice')
    d = json.dumps
    L = ['{"name": "COMPOSE", "tier": "flocq4", "deps": %s,' % d(DEPS),
         ' "files": %s,' % d(FILES),
         ' "identity": "Identity",',
         ' "statement": {"file": %s, "sha256": %s},' % (d(S), d(STATEMENT_SHA256)),
         ' "generated": {', '  "compose/gate.json": %s,' % d([ME, 'json'])]
    L += ['  %s: %s%s' % (d('compose/' + plant_path(n, p[2])), d([ME, 'plant', n]), ',' if n != NAMES[-1] else '')
          for n, p in zip(NAMES, PLANTS)]
    L += [' },', ' "plants": {']
    for name, cls, src, _, exp, what in PLANTS:
        e = {'replace': {src: plant_path(name, src)}}
        if exp[0] == 'fails': e['fails'] = exp[1]; e['text'] = exp[2]
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
                print('wrote compose/%s %s' % (path, hashlib.sha256(b).hexdigest()))
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
