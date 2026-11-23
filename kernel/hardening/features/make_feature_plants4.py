# SPDX-License-Identifier: AGPL-3.0-only
# Writes plants4/, the plants of the feature row's version 4 (feature_row4.py). 2026-11-18, scratch; written by the
# assistant; changed after review rounds 3, 4, 5 and 6. Standard library only. It never overwrites a file: one that
# exists must hold exactly the bytes it would write (it is then left as it is), or the script stops before writing
# anything; it writes only the files absent.
#
# What it writes: one plant for each construct version 4 adds (refuse4_*, each must be refused with its class), plants
# that hide those constructs behind the lexer's cases (evade4_*, each must be refused), decoys holding the same words
# in a comment, in a string, inside a longer identifier, in lower case or in another attribute (decoy4_*, each must
# hold), known over-refusals (over4_*, refused although Coq reads them, or may read them, as plain names: two in
# PLANTS, over4_private_identifier in PLANTS2, over4_include_identifier in PLANTS3, over4_module_prime_identifier and
# over4_cd_identifier in PLANTS4, over4_from_identifier in PLANTS5), and lists in FROZEN4.txt's form for the input row
# (input4_*.txt; their paths are relative to plants4/), and, after review, the plants of the attribute and prefix
# spellings (PLANTS2 below), after the fourth review those of the module types and functors (PLANTS3), after the fifth
# review those of the character rule, the plain-module rule, the file, load-path and plugin commands and the Class
# count (PLANTS4), and after the sixth review those of Extra Dependency, Restore State, Write State, the From rule and
# the list's line characters (PLANTS5). Which verdict each must give is in PREDICTIONS-row4-2026-11-18.md,
# tools/ci/tests/PREDICTIONS-row4-addendum1.md, PREDICTIONS-row4-addendum2.md, PREDICTIONS-row4-addendum3.md and
# PREDICTIONS-row4-addendum4.md. What it does not show: that any plant compiles; the row reads text only.
#
# Usage: python -B make_feature_plants4.py      (writes plants4/ beside this file; files are LF, binary, ASCII except
# the PLANTS4 files that hold a letter outside ASCII, which are UTF-8; this source names those letters by escapes)
import hashlib, os, sys
sys.dont_write_bytecode = True
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plants4')

PLANTS = {
    # each construct version 4 adds
    'refuse4_conjectures.v': 'Conjectures c1 c2 : False.\n',
    'refuse4_context.v': 'Context (n : nat).\nDefinition m : nat := n.\n',
    'refuse4_declare_instance.v': 'Class C : Type := { c : nat }.\nDeclare Instance i : C.\n',
    'refuse4_admit_obligations.v': 'Admit Obligations.\n',
    'refuse4_obligation.v': 'Obligation 1 of p.\nProof. exact I. Qed.\n',
    'refuse4_next_obligation.v': 'Next Obligation.\nProof. exact I. Qed.\n',
    'refuse4_final_obligation.v': 'Final Obligation.\nProof. exact I. Qed.\n',
    'refuse4_solve_obligations.v': 'Solve Obligations with exact I.\n',
    'refuse4_solve_all_obligations.v': 'Solve All Obligations with exact I.\n',
    'refuse4_obligation_tactic.v': 'Obligation Tactic := idtac.\n',
    'refuse4_program_attribute.v': '#[program] Definition p : nat := 0.\n',
    'refuse4_program_attribute_list.v': '#[local, program] Definition q : nat := 0.\n',
    'refuse4_program_attribute_value.v': '#[program=yes] Definition r : nat := 0.\n',
    # the same constructs behind the lexer's cases
    'evade4_context_after_string_in_comment.v': '(* "(*" *) Context (n : nat).\n',
    'evade4_conjectures_after_string_in_comment.v': '(* "*)" *) Conjectures a b : nat.\n',
    'evade4_split_declare_instance.v':
        'Class C : Type := { c : nat }.\nDeclare (* an instance, (* nested *) with no body *)\n  Instance i : C.\n',
    'evade4_split_solve_all_obligations.v': 'Solve\n  All (* a comment *) Obligations with exact I.\n',
    'evade4_program_attribute_bracket_in_comment.v': '#[ (* ] *) program ] Definition p : nat := 0.\n',
    'evade4_program_attribute_bracket_in_string.v':
        '#[deprecated(since="1", note="]"), program] Definition p : nat := 0.\n',
    'evade4_program_attribute_multiline.v': '#[\n  local,\n  program\n] Definition p : nat := 0.\n',
    # known over-refusals: Coq reads these as plain names; the row refuses them (it fails closed)
    'over4_prime_identifier.v': "Definition Context' : nat := 0.\n",
    'over4_bare_identifier.v': 'Definition Context : nat := 0.\n',
    # decoys: the words in a comment, in a string, inside longer identifiers, in lower case, in other attributes
    'decoy4_comment.v':
        '(* Conjectures c : False. Context (n : nat). Declare Instance i : C. Admit Obligations.\n'
        '   Obligation 1. Next Obligation. Final Obligation. Solve Obligations. Solve All Obligations.\n'
        '   Obligation Tactic := idtac. #[program] Definition p := 0. (* nested: #[local, program] *) *)\n'
        'Definition d4 : nat := 0.\n',
    'decoy4_string.v':
        'Ltac say := idtac "Conjectures c : False. Context (n : nat). Declare Instance i : C. Admit Obligations.\n'
        'Obligation 1. Next Obligation. Final Obligation. Solve Obligations. Solve All Obligations.\n'
        'Obligation Tactic := idtac. #[program] Definition p := 0." "and ""#[local, program]"" quoted".\n'
        'Goal True. Proof. say. exact I. Qed.\n',
    'decoy4_string_in_comment.v':
        '(* "*)" Context (n : nat). Declare Instance i : C. #[program] Definition p := 0. Conjectures a : nat. *)\n'
        'Definition d : nat := 0.\n',
    'decoy4_identifiers.v':
        'Definition Conjectures_n : nat := 0.\nDefinition ContextFree : nat := 1.\n'
        'Definition my_Context : nat := 2.\nDefinition the_Context_size : nat := 3.\n'
        'Definition DeclareInstance : nat := 4.\nDefinition Admittance : nat := 5.\n'
        'Definition Obligational : nat := 6.\nDefinition Obligations2 : nat := 7.\n'
        'Definition programs : nat := 8.\n#[local] Definition programmed : nat := 9.\n',
    'decoy4_lowercase.v':
        'Definition program : nat := 0.\n'
        'Goal program = 0. Proof. match goal with |- context [ program ] => reflexivity end. Qed.\n'
        'Goal True. Proof. solve [ exact I ]. Qed.\n',
    'decoy4_other_attributes.v':
        '#[local] Definition a : nat := 0.\n#[deprecated(since="1", note="use b")] Definition a2 : nat := a.\n'
        '#[global] Hint Unfold a : core.\nDefinition program_name : nat := 1.\n',
    'decoy4_instances.v':
        'Class C : Type := { c : nat }.\n#[local] Instance i : C := { c := 0 }.\nExisting Instance i.\n',
}

# After review: the other spellings of the census's triggers (feature_row4.py's last five refusals), each attribute
# in each position, the attributes' other values, the prefixes, the option and the inline binder; decoys holding the
# same words outside an attribute list, in strings and in comments; one more known over-refusal. Their predicted
# verdicts are in tools/ci/tests/PREDICTIONS-row4-addendum1.md.
ATTRIBUTES = {
    'universes': ('universes(polymorphic)', 'Definition idp (A : Type) := A.'),
    'projections': ('projections(primitive)', 'Record R := { a : nat }.'),
    'bypass_check': ('bypass_check(guard)', 'Definition b := 0.'),
    'program': ('program', 'Definition p : nat := 0.'),
    'using': ('using="Type"', 'Definition u : nat := 0.'),
    'private': ('private(matching)', 'Inductive P := p.'),
}
POSITIONS = {
    'first': '#[%s] %s\n',
    'after_local': '#[local, %s] %s\n',
    'spaced': '#[ %s ] %s\n',
    'second_list': '#[local] #[%s] %s\n',
    'multiline': '#[\n  local,\n  %s\n] %s\n',
}
PLANTS2 = {}
for _a, (_attr, _decl) in sorted(ATTRIBUTES.items()):
    for _p, _form in sorted(POSITIONS.items()):
        PLANTS2['refuse4_attr_%s_%s.v' % (_a, _p)] = _form % (_attr, _decl)
for _name, _attr in (('universes_polymorphic_yes', 'universes(polymorphic=yes)'),
                     ('universes_cumulative', 'universes(cumulative)'), ('universes_template', 'universes(template)'),
                     ('universes_monomorphic', 'universes(monomorphic)'),
                     ('projections_primitive_yes', 'projections(primitive=yes)'),
                     ('bypass_check_positivity', 'bypass_check(positivity)'),
                     ('bypass_check_universes', 'bypass_check(universes)'), ('program_no', 'program=no')):
    PLANTS2['refuse4_value_%s.v' % _name] = '#[local, %s] Definition v := 0.\n' % _attr
PLANTS2.update({
    'refuse4_prefix_polymorphic.v': 'Polymorphic Definition p := 0.\n',
    'refuse4_prefix_monomorphic.v': 'Monomorphic Definition m := 0.\n',
    'refuse4_prefix_cumulative.v': 'Cumulative Inductive C := c.\n',
    'refuse4_prefix_noncumulative.v': 'NonCumulative Inductive N := n.\n',
    'refuse4_prefix_private.v': 'Private Inductive P := p.\n',
    'refuse4_prefix_program.v': 'Program Definition p : nat := 0.\n',
    'refuse4_prefix_local_polymorphic.v': 'Local Polymorphic Definition p := 0.\n',
    'refuse4_prefix_attribute_private.v': '#[local] Private Inductive P := p.\n',
    'refuse4_option_default_proof_using.v': 'Set Default Proof Using "Type".\n',
    'refuse4_universe_binder.v': 'Definition idu@{u} (A : Type@{u}) : Type@{u} := A.\n',
    'over4_private_identifier.v': 'Definition Private : nat := 0.\n',
    'decoy4_attribute_words.v':
        'Definition universes : nat := 0.\nDefinition projections : nat := 1.\nDefinition using_n : nat := 2.\n'
        'Definition monomorphic : nat := 3.\n#[local] Definition private_n : nat := 4.\n'
        '#[local] Definition universes2 : nat := universes.\n',
    'decoy4_attribute_strings.v':
        '#[deprecated(since="1", note="universes projections using private program bypass_check Monomorphic '
        'Private")] Definition a3 : nat := 0.\n',
    'decoy4_attribute_comment.v':
        '(* #[universes(polymorphic)] #[projections(primitive)] #[using="x"] #[private(matching)] Private\n'
        '   Monomorphic Set Default Proof Using "Type". Definition i@{u} := Type@{u}. *)\nDefinition a4 : nat := 0.\n',
    'decoy4_at_sign.v': 'Definition a5 : nat := @id nat 0.\n',
})

# After the fourth review: the census's module types and functors in the spellings version 3 does not refuse
# (feature_row4.py's last refusal), one hidden behind comments, decoys holding the words where they make no module
# type or functor, and one more known over-refusal. Their predicted verdicts are in
# tools/ci/tests/PREDICTIONS-row4-addendum2.md.
PLANTS3 = {
    'refuse4_module_functor_applied.v': 'Module M := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_ascribed.v': 'Module N : OrderedType.OrderedType := Nat_as_OT.\n',
    'refuse4_module_ascribed_sub.v': 'Module N <: OrderedType.OrderedType := Nat_as_OT.\n',
    'refuse4_module_interactive_sub.v': 'Module N <: OrderedType.OrderedType.\n  Include Nat_as_OT.\nEnd N.\n',
    'refuse4_module_include.v': 'Module M.\n  Include Nat_as_OT.\nEnd M.\n',
    'refuse4_module_import_functor.v': 'Module Import F (X : OrderedType.OrderedType).\nEnd F.\n',
    'refuse4_module_export_applied.v': 'Module Export M := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_multiline.v': 'Module\n  M\n  :=\n  FSetAVL.Make Nat_as_OT.\n',
    'evade4_module_comment.v': 'Module (* a comment *) M (* (* nested *) *) := FSetAVL.Make Nat_as_OT.\n',
    'over4_include_identifier.v': 'Definition Include : nat := 0.\n',
    'decoy4_module_plain.v': 'Module M.\n  Definition x : nat := 0.\nEnd M.\nImport M.\nDefinition y : nat := M.x.\n',
    'decoy4_module_words.v':
        'Definition Included : nat := 0.\nDefinition Module_n : nat := 1.\nDefinition IncludeX : nat := 2.\n'
        'Definition modules : nat := 3.\n',
    'decoy4_module_comment_string.v':
        '(* Module M := F X. Module N : T := X. Include M. *)\nDefinition s := "Module N <: T := X. Include Y".\n',
}

# After the fifth review: a letter outside ASCII anywhere (in a module's name, in a comment, in a string), every Module
# but a plain one (import categories, Module Type, Declare Module), the commands that read another file, change the
# load path or the working folder, write files or load a plugin, two more known over-refusals, decoys holding the
# words where they make no such command, and a Class declaration, which version 4 counts on its reported line. Their
# predicted verdicts are in tools/ci/tests/PREDICTIONS-row4-addendum3.md.
PLANTS4 = {
    'refuse4_module_alpha_functor.v': 'Module \u03b1 (X : OrderedType.OrderedType).\nEnd \u03b1.\n',
    'refuse4_module_alpha_applied.v': 'Module \u03b1 := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_beta_ascribed.v': 'Module \u03b2 : OrderedType.OrderedType := Nat_as_OT.\n',
    'refuse4_module_import_gamma.v': 'Module Import \u03b3 := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_e_acute_sub.v': 'Module \u00c9x <: OrderedType.OrderedType := Nat_as_OT.\n',
    'refuse4_module_combining_mark.v': 'Module Me\u0301 := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_import_categories.v': 'Module Import -(notations) M := FSetAVL.Make Nat_as_OT.\n',
    'refuse4_module_alpha_plain.v': 'Module \u03b1.\nDefinition x : nat := 0.\nEnd \u03b1.\n',
    'refuse4_module_type.v': 'Module Type T.\nEnd T.\n',
    'refuse4_declare_module.v': 'Declare Module M : OrderedType.OrderedType.\n',
    'refuse4_nonascii_comment.v': '(* the letter \u03b1 in a comment *)\nDefinition c7 : nat := 0.\n',
    'refuse4_nonascii_string.v': 'Definition s7 := "the letter \u03b1 in a string".\n',
    'over4_module_prime_identifier.v': "Definition Module' : nat := 0.\n",
    'decoy4_module_plain_forms.v':
        "Module M.\nEnd M.\nModule Import N.\nEnd N.\nModule Export P'.\nEnd P'.\nModule\n  Q\n  .\nEnd Q.\n",
    'decoy4_module_word_comment.v':
        '(* Module Type T. Declare Module M : T. Module F (X : T). Module N := F X. *)\nDefinition m7 : nat := 0.\n',
    'refuse4_load_absolute.v': 'Load "/work/kernel/coq/f32/helper.v".\n',
    'refuse4_load_ident.v': 'Load helper.\n',
    'refuse4_add_loadpath.v': 'Add LoadPath "/work/kernel/coq/zz" as MKF.zz.\n',
    'refuse4_add_rec_loadpath.v': 'Add Rec LoadPath "/opt" as Lib.\n',
    'refuse4_cd.v': 'Cd "/work".\n',
    'refuse4_redirect.v': 'Redirect "out" Print nat.\n',
    'refuse4_extraction.v': 'Extraction "out.ml" nat.\n',
    'refuse4_recursive_extraction.v': 'Recursive Extraction nat.\n',
    'refuse4_separate_extraction.v': 'Separate Extraction nat.\n',
    'refuse4_extraction_library.v': 'Extraction Library Datatypes.\n',
    'refuse4_extract_constant.v': 'Extract Constant plus => "( + )".\n',
    'refuse4_extract_inductive.v': 'Extract Inductive bool => "bool" [ "true" "false" ].\n',
    'refuse4_extraction_option.v': 'Set Extraction Output Directory "out".\n',
    'refuse4_declare_ml_module.v': 'Declare ML Module "coq-core.plugins.ltac".\n',
    'refuse4_add_ml_path.v': 'Add ML Path "/opt".\n',
    'refuse4_add_rec_ml_path.v': 'Add Rec ML Path "/opt".\n',
    'over4_cd_identifier.v': 'Definition Cd : nat := 0.\n',
    'decoy4_load_comment.v':
        '(* Load "x.v". Add LoadPath "d" as L. Add Rec LoadPath "d" as L. Cd "d". Redirect "f" Print nat.\n'
        '   Extraction nat. Recursive Extraction nat. Extract Constant x => "y". Declare ML Module "p".\n'
        '   Add ML Path "d". Add Rec ML Path "d". *)\nDefinition l1 : nat := 0.\n',
    'decoy4_load_string.v':
        'Definition l2 := "Load x. Add LoadPath d. Cd d. Redirect f. Extraction nat. Extract Constant x. '
        'Declare ML Module p. Add ML Path d. Add Rec ML Path d.".\n',
    'decoy4_load_identifiers.v':
        'Definition Loader : nat := 0.\nDefinition LoadPaths : nat := 1.\nDefinition Cdx : nat := 2.\n'
        'Definition Redirected : nat := 3.\nDefinition Extractions : nat := 4.\nDefinition Extractor : nat := 5.\n'
        'Definition MLx : nat := 6.\nDefinition load : nat := 7.\nDefinition cd : nat := 8.\n',
    'decoy4_class_reported.v': 'Class C7 : Type := { c7 : nat }.\n',
}


def sha(name):
    return hashlib.sha256(PLANTS[name].encode('ascii')).hexdigest()

HEAD = '# A list in the form of FROZEN4.txt for the input row, written by make_feature_plants4.py.\n'
EMPTY, ZERO = hashlib.sha256(b'').hexdigest(), '0' * 64
DC, DI, RC = 'decoy4_comment.v', 'decoy4_identifiers.v', 'refuse4_context.v'
LISTS = {
    'input4_honest.txt': HEAD + '%s  %s\n%s  %s\n%s  sub/plants/absent.v\n%s  notes.txt\n'
        % (sha(DC), DC, sha(DI), DI, ZERO, ZERO),
    'input4_empty.txt': HEAD,
    'input4_plants_only.txt': HEAD + '%s  sub/plants/absent.v\n' % ZERO,
    'input4_bad_line.txt': HEAD + '%s %s\n%s  %s\n' % (sha(DC), DC, sha(DI), DI),
    'input4_dotdot.txt': HEAD + '%s  sub/plants/../%s\n%s  %s\n' % (sha(DC), DC, sha(DI), DI),
    'input4_absolute.txt': HEAD + '%s  /%s\n%s  %s\n' % (sha(DC), DC, sha(DI), DI),
    'input4_backslash.txt': HEAD + '%s  sub\\%s\n%s  %s\n' % (sha(DC), DC, sha(DI), DI),
    'input4_duplicate.txt': HEAD + '%s  %s\n%s  %s\n' % (sha(DC), DC, sha(DC), DC),
    'input4_hash_mismatch.txt': HEAD + '%s  %s\n%s  %s\n' % (EMPTY, DC, sha(DI), DI),
    'input4_missing_file.txt': HEAD + '%s  absent4.v\n%s  %s\n' % (ZERO, sha(DI), DI),
    'input4_refused.txt': HEAD + '%s  %s\n%s  %s\n' % (sha(DI), DI, sha(RC), RC),
}

# After the sixth review: the commands Extra Dependency, Restore State and Write State; a From not followed by a name
# and Require; their decoys (the words in a comment and in a string, and "From Coq Require Import Reals."); a known
# over-refusal (a name From); and lists whose comment line is ended by a carriage return, a form feed, a record
# separator or a vertical tab before an entry, which version 3 reads as two lines (and their control, ended by a line
# feed). These are ASCII; the separators are written as escapes.
HIDDEN = HEAD + '# hidden%s%s  %s\n%s  %s\n'
PLANTS5 = {
    'refuse4_extra_dependency.v': 'From Coq Extra Dependency "x.txt" as xdep.\n',
    'refuse4_restore_state.v': 'Restore State "s".\n',
    'refuse4_write_state.v': 'Write State "s".\n',
    'refuse4_from_import.v': 'From Coq Import Reals.\n',
    'decoy4_state_comment.v': '(* From Coq Extra Dependency "x.txt" as xdep. Restore State "s". Write State "s". *)\n'
                              'Definition st1 : nat := 0.\n',
    'decoy4_state_string.v': 'Definition st2 := "From Coq Extra Dependency x. Restore State s. Write State s.".\n',
    'decoy4_from_require.v': 'From Coq Require Import Reals.\nFrom (* a comment *) Coq Require Import ZArith.\n'
                             'From Coq.Init Require Export Nat.\n',
    'over4_from_identifier.v': 'Definition From : nat := 0.\n',
    'input4_hidden_cr.txt': HIDDEN % ('\r', sha(RC), RC, sha(DI), DI),
    'input4_hidden_ff.txt': HIDDEN % ('\x0c', sha(RC), RC, sha(DI), DI),
    'input4_hidden_rs.txt': HIDDEN % ('\x1e', sha(RC), RC, sha(DI), DI),
    'input4_hidden_vt.txt': HIDDEN % ('\x0b', sha(RC), RC, sha(DI), DI),
    'input4_hidden_lf.txt': HIDDEN % ('\n', sha(RC), RC, sha(DI), DI),
}

ALL = (sorted(PLANTS.items()) + sorted(LISTS.items()) + sorted(PLANTS2.items()) + sorted(PLANTS3.items())
       + sorted(PLANTS4.items()) + sorted(PLANTS5.items()))
assert len(set(n for n, _ in ALL)) == len(ALL), 'a file name twice'
# Every file but those of PLANTS4 is ASCII; UTF-8 gives an ASCII text the same bytes as ASCII does.
assert all(n in PLANTS4 or t.isascii() for n, t in ALL), 'a letter outside ASCII outside PLANTS4'
os.makedirs(D, exist_ok=True)
# A file that exists must already hold exactly these bytes: then it is left as it is. A file that holds other bytes
# stops the script before it writes anything, so a record is never overwritten.
have = {}
for name, text in ALL:
    p = os.path.join(D, name)
    if os.path.lexists(p):
        with open(p, 'rb') as f: have[name] = f.read()
        if not os.path.isfile(p) or have[name] != text.encode('utf-8'):
            sys.exit('REFUSED: %s exists with other bytes; nothing written' % name)
new = [(name, text) for name, text in ALL if name not in have]
for name, text in new:
    with open(os.path.join(D, name), 'wb') as f: f.write(text.encode('utf-8'))
print('%d files in plants4 (%d plants, %d lists, %d after review, %d after the fourth review, %d after the fifth '
      'review, %d after the sixth); %d written now, %d already there with these bytes'
      % (len(ALL), len(PLANTS), len(LISTS), len(PLANTS2), len(PLANTS3), len(PLANTS4), len(PLANTS5), len(new),
         len(have)))
