# Writes plants3/: one plant per class version 3 adds (each must be refused) and decoys (each must hold). Written by the
# assistant, 2026-11-17, scratch. Files are written in binary, LF.
import os, sys
sys.dont_write_bytecode = True
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plants3')
PLANTS = {
    'refuse3_native_compute.v': 'Goal (1 + 1 = 2)%nat. Proof. native_compute. reflexivity. Qed.\n',
    'refuse3_primitive.v': 'Primitive int := #int63_type.\n',
    'refuse3_primitive_type.v': 'From Coq Require Import PrimFloat.\nDefinition one := PrimFloat.one.\n',
    'refuse3_sprop.v': 'Inductive sTrue : SProp := sI.\n',
    'refuse3_polymorphic.v': 'Polymorphic Definition idp (A : Type) (a : A) := a.\n',
    'refuse3_universe.v': 'Universe u.\nDefinition T := Type@{u}.\n',
    'refuse3_module_type.v': 'Module Type S.\n  Parameter t : Type.\nEnd S.\n',
    'refuse3_functor.v': 'Module F (X : Nat).\nEnd F.\n',
    'refuse3_plugin.v': 'Declare ML Module "some-plugin".\n',
    'refuse3_section.v': 'Section S.\n  Variable n : nat.\n  Definition m := n.\nEnd S.\n',
    'refuse3_coinductive.v': 'CoInductive stream := Cons : nat -> stream -> stream.\n',
    'refuse3_axiom.v': 'Axiom anything : False.\n',
    'refuse3_parameter.v': 'Parameter p : nat.\n',
    'refuse3_admitted.v': 'Lemma l : 1 = 1.\nProof.\nAdmitted.\n',
    'refuse3_abstract.v': 'Lemma l : True.\nProof. abstract exact I. Qed.\n',
    'refuse3_proof_using.v': 'Lemma l : True.\nProof using.\nexact I. Qed.\n',
    'refuse3_let_in_inductive.v': 'Inductive i : Type := C : let x := nat in x -> i.\n',
    'refuse3_let_in_record.v': 'Record r := { a : nat; b : let y := a in nat }.\n',
    # decoys: the words only in comments, strings, longer identifiers, or a plain enumeration and record
    'decoy3_comment.v': '(* native_compute, SProp, Section, Axiom, Polymorphic, Module Type, CoInductive *)\nDefinition d := 0.\n',
    'decoy3_identifiers.v': 'Definition Sectional := 1.\nDefinition Primitives_count := 2.\nDefinition admits_two := 3.\n',
    'decoy3_plain_inductive.v': 'Inductive colour := Red | Green.\nRecord pair := { fst : nat; snd : nat }.\n',
    'decoy3_qualified_name.v': 'Inductive w : Type := W : Coq.Init.Datatypes.nat -> w.\nDefinition z := let k := 0 in k.\n',
    'decoy3_vm_compute.v': 'Goal (2 * 2 = 4)%nat. Proof. vm_compute. reflexivity. Qed.\n',
}
os.makedirs(D, exist_ok=False)
for name, text in sorted(PLANTS.items()):
    with open(os.path.join(D, name), 'wb') as f: f.write(text.encode('ascii'))
print(len(PLANTS), 'plants written')
