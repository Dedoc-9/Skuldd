# Version 2 of identity_check.py (2026-11-17, scratch; written by the assistant; standard library only). Version 1
# removed each comment without leaving a blank, as the gate's code() does; but in Coq a comment separates tokens, so
# "a(*c*)b" is two tokens and "ab" one. This version changes only that: the Coq-side identity lexes a string as a
# string at any comment depth (as version 1) and turns each outermost comment into one blank. A difference from the
# gate's identity therefore points at a comment glued between two tokens (or at a string inside a comment, which
# version 1 found in no tier file). White space inside strings is collapsed on both sides, as the gate does; a statement
# file without string literals is not affected by that. Usage: python -B identity_check2.py FILE ...
import hashlib, sys
sys.dont_write_bytecode = True

def code_gate(text):
    out, depth, i = [], 0, 0
    while i < len(text):
        if text.startswith('(*', i): depth += 1; i += 2
        elif depth and text.startswith('*)', i): depth -= 1; i += 2
        else:
            if not depth: out.append(text[i])
            i += 1
    return ' '.join(''.join(out).split())

def code_coq(text):
    out, depth, i, n = [], 0, 0, len(text)
    while i < n:
        if text[i] == '"':
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"': j += 2; continue
                    break
                j += 1
            if not depth: out.append(text[i:j + 1])
            i = j + 1; continue
        if text.startswith('(*', i):
            if depth == 0: out.append(' ')        # an outermost comment becomes one blank
            depth += 1; i += 2; continue
        if depth and text.startswith('*)', i): depth -= 1; i += 2; continue
        if not depth: out.append(text[i])
        i += 1
    return ' '.join(''.join(out).split())

bad = 0
for p in sys.argv[1:]:
    t = open(p, 'rb').read().decode('utf-8')
    a, b = code_gate(t), code_coq(t)
    same = a == b
    bad += not same
    print('%s  %s  quotes %d  gate %s  coq %s' % ('same' if same else 'DIFFERENT', p, t.count('"'),
          hashlib.sha256(a.encode()).hexdigest()[:16], hashlib.sha256(b.encode()).hexdigest()[:16]))
print('files %d, different %d' % (len(sys.argv) - 1, bad))
