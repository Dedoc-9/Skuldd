# Writes plants2/: the plants that show version 1's two gaps (each EVADE must be refused by version 2; version 1 is
# expected to let it pass) and two decoys (each must hold under both versions). Every file is valid Coq on its own.
# Written by the assistant, 2026-11-17, scratch. Files are written in binary, LF.
import os, sys
sys.dont_write_bytecode = True
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plants2')
PLANTS = {
    # a checking-flag change with a line break between its words
    'evade_split_unset_guard.v': 'Unset\n  Guard Checking.\n',
    'evade_split_definitional_uip.v': 'Set Definitional\n  UIP.\n',
    # a quoted "*)" inside a comment: Coq lexes it as a string, so the comment does not end there
    'evade_string_in_comment.v': '(* "*)" *)\nUnset Guard Checking.\n(* " *)\n" *)\n',
    # the same, hiding an unguarded fixpoint; its effect must still reach coqchk's summary
    'evade_hidden_fixpoint.v': ('(* "*)" *)\nUnset Guard Checking.\nFixpoint loop (n : nat) : nat := loop n.\n'
                                'Set Guard Checking.\n(* " *)\n" *)\nDefinition use := loop.\n'),
    # decoys: the refused words only inside strings, inside a comment or inside a string literal across lines
    'decoy_string_in_comment.v': '(* A comment holding strings: "Unset Guard Checking. Fixpoint f" and "*)". *)\nDefinition decoy := 0.\n',
    'decoy_split_string.v': ('From Coq Require Import String.\nOpen Scope string_scope.\n'
                             'Definition s : string := "Unset\n  Guard Checking. ""(*"" Fixpoint".\n'),
}
os.makedirs(D, exist_ok=False)
for name, text in sorted(PLANTS.items()):
    with open(os.path.join(D, name), 'wb') as f: f.write(text.encode('ascii'))
    print(name, len(text))
