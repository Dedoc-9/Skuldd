# For each file given: the comment-ignoring identity as the gate computes it (gate_ieee64.py code(): nested comments,
# no string handling) against the same identity computed with Coq's lexing (a string is a string at any comment depth;
# a string outside comments is kept as code, a string inside a comment is removed with the comment). Both collapse
# white space the same way. Equal means the gate's identity reads the file as Coq does. Written by the assistant,
# 2026-11-17, scratch, standard library only. Usage: python -B identity_check.py FILE ...
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
        if text.startswith('(*', i): depth += 1; i += 2; continue
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
