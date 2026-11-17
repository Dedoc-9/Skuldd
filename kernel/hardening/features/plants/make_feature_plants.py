# Writes the plants of the feature-absence row into this folder (refuses to overwrite). Each REFUSE plant must make
# the row fail; each DECOY must not (a forbidden word only in a comment, a string or inside an identifier).
#   python -B make_feature_plants.py
import os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
P = {
  'refuse_fixpoint.v':        'Fixpoint f (n : nat) : nat := match n with O => O | S k => f k end.\n',
  'refuse_cofixpoint.v':      'CoInductive s : Type := C : s -> s.\nCoFixpoint z : s := C z.\n',
  'refuse_anonymous_fix.v':   'Definition g : nat -> nat := fix h (n : nat) : nat := match n with O => O | S k => h k end.\n',
  'refuse_fix_tactic.v':      'Lemma l : forall n : nat, n = n.\nProof. fix IH 1. intros n; reflexivity. Qed.\n',
  'refuse_program.v':         'Require Import Program.\nProgram Definition p : nat := 0.\n',
  'refuse_scheme.v':          'Inductive t : Set := A | B.\nScheme t_ind2 := Induction for t Sort Prop.\n',
  'refuse_unset_guard.v':     'Unset Guard Checking.\nDefinition d : nat := 0.\n',
  'refuse_local_unset_pos.v': 'Local Unset Positivity Checking.\n',
  'refuse_unset_universe.v':  'Unset Universe Checking.\n',
  'refuse_bypass_check.v':    '#[bypass_check(guard)] Definition b : nat := 0.\n',
  'refuse_definitional_uip.v':'Set Definitional UIP.\n',
  'decoy_comment.v':          '(* Fixpoint and fix and Unset Guard Checking, (* nested cofix *) Program *)\nDefinition ok1 : nat := 0.\n',
  'decoy_string.v':           'Require Import String.\nDefinition ok2 : string := "Fixpoint fix ""cofix"" Unset Guard Checking"%string.\n',
  'decoy_identifier.v':       'Definition prefix_fix : nat := 0.\nDefinition fixed : nat := prefix_fix.\nDefinition Fixpointless : nat := 1.\n',
}
for name, text in sorted(P.items()):
    path = os.path.join(HERE, name)
    if os.path.exists(path): sys.exit('make_feature_plants: %s exists' % path)
    with open(path, 'wb') as f: f.write(text.encode('ascii'))
    print('wrote', name)
