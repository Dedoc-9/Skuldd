# Derives harness2.py from harness.py (written by the assistant, 2026-11-17). Two changes, nothing else:
# (1) row 5 names the first file that is missing, extra or different, instead of only counting;
# (2) the import reader blanks comments and strings as Coq's lexer reads them (a string is a string at any comment
#     depth), so a quoted "*)" inside a comment can no longer hide or invent an import.
# Each replacement must match exactly once.
import sys
sys.dont_write_bytecode = True
src = open('harness.py', encoding='utf-8').read()
old_strip = '''def strip_comments(t):
    out, i, d = [], 0, 0
    while i < len(t):
        if t.startswith('(*', i): d += 1; i += 2
        elif d and t.startswith('*)', i): d -= 1; i += 2
        else:
            if not d: out.append(t[i])
            i += 1
    return ''.join(out)'''
new_strip = '''def strip_comments(t):
    """Comments and strings blanked as Coq's lexer reads them: a string is a string at any comment depth ("" is an
    escaped quote), so a "(*" or "*)" inside a string never opens or closes a comment; each comment becomes a blank."""
    out, i, d, n = [], 0, 0, len(t)
    while i < n:
        if t[i] == '"':
            j = i + 1
            while j < n:
                if t[j] == '"':
                    if j + 1 < n and t[j + 1] == '"': j += 2; continue
                    break
                j += 1
            out.append(' '); i = j + 1; continue
        if t.startswith('(*', i):
            if d == 0: out.append(' ')
            d += 1; i += 2; continue
        if d and t.startswith('*)', i): d -= 1; i += 2; continue
        if not d: out.append(t[i])
        i += 1
    return ''.join(out)'''
old_row5 = "    rep('5 fresh root holds exactly the listed sources', ok5, '%d sources' % len(srcs))"
new_row5 = '''    if ok5: det5 = '%d sources' % len(srcs)
    else:
        missing5 = [p for p in srcs if p not in have]; extra5 = [p for p in have if p not in srcs]
        diff5 = [p for p in srcs if p in have and sha(raw(os.path.join(R, p))) != listed[p]]
        det5 = 'missing %s; extra %s; different %s' % (missing5[:3], extra5[:3], diff5[:3])
    rep('5 fresh root holds exactly the listed sources', ok5, det5)'''
for old, new in ((old_strip, new_strip), (old_row5, new_row5)):
    assert src.count(old) == 1, ('not exactly once', old[:60])
    src = src.replace(old, new)
head = ("# harness2.py: version 2 of harness.py (2026-11-17). Changed from version 1 only so: row 5 names the first missing,\n"
        "# extra or different file; the import reader lexes strings as Coq does. Version 1 is kept: its runs cite its sha256.\n")
open('harness2.py', 'w', encoding='utf-8', newline='\n').write(head + src)
print('harness2.py written')
