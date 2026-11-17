# Derives gen_refute2.py from gen_refute.py (written by the assistant, 2026-11-17): the stage folder becomes an argument,
# and the three files version 1 wrote in text mode (CR LF on Windows; the cause of refute3's failure) are written LF.
# Every other byte of version 1 is kept. Each replacement must match exactly once.
import sys
sys.dont_write_bytecode = True
src = open('gen_refute.py', encoding='utf-8').read()
repl = [
    ("ST = os.path.join(ROOT, 'ext-work', 'harden-r4', 'plants', 'stage')",
     "ST = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else sys.exit('usage: gen_refute2.py NEW_STAGE_DIR')"),
    ("    with open(p, 'w') as f: f.write(chk)", "    with open(p, 'w', encoding='utf-8', newline='\\n') as f: f.write(chk)"),
    ("    with open(os.path.join(ST, 'order.txt'), 'w') as f:", "    with open(os.path.join(ST, 'order.txt'), 'w', encoding='utf-8', newline='\\n') as f:"),
    ("    with open(os.path.join(ST, 'labels-refuted.json'), 'w') as f:", "    with open(os.path.join(ST, 'labels-refuted.json'), 'w', encoding='utf-8', newline='\\n') as f:"),
]
for old, new in repl:
    assert src.count(old) == 1, ('not exactly once', old)
    src = src.replace(old, new)
head = ("# gen_refute2.py: version 2 of gen_refute.py (2026-11-17). Changed from version 1 only so: the stage folder is the\n"
        "# first argument, and Check.v, order.txt and labels-refuted.json are written with LF line ends.\n")
open('gen_refute2.py', 'w', encoding='utf-8', newline='\n').write(head + src)
print('gen_refute2.py written')
