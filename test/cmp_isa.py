#!/usr/bin/env python3
"""Module vs manual table: cmp_isa.py <corpus dir> <ghidra out dir> [--show N]
Compares, for each of the 65536 first words, the module's mnemonic and length with c24x_isa.py (SPRU160C)."""
import collections, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c24x_isa import lookup
d, gd = sys.argv[1], sys.argv[2]
show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 5
recs = [tuple(int(x, 16) for x in l.split()) for l in open(os.path.join(d, "records.txt"))][:65536]
g = {}
for f in sorted(glob.glob(os.path.join(gd, "c*.bin.txt"))):
    ci = int(os.path.basename(f)[1:3])
    for l in open(f):
        a, n, t = l.rstrip("\n").split(" ", 2)
        a = int(a, 16)
        if a % 4 == 0:
            g[ci * 16384 + a // 4] = (int(n), t)
cnt = collections.Counter(); ex = collections.defaultdict(list)
for i, (w, w2) in enumerate(recs):
    exp = lookup(w)
    n, t = g[i]
    bad = t.startswith("BAD")
    mn = t.split(" ")[0].upper()
    if exp is None:
        k = "both invalid" if bad else "module decodes, manual invalid"
    elif bad:
        k = "manual valid, module BAD"
    elif mn != exp[0] or n != exp[1]:
        k = "mnemonic/length differs"
    else:
        k = "agree"
    cnt[k] += 1
    if k != "agree" and k != "both invalid":
        ex[(k, exp[0] if exp else mn)].append((w, t, exp))
for k, v in cnt.items(): print(f"{v:6d} {k}")
for (k, m), v in sorted(ex.items()):
    print(f"-- {k} [{m}] x{len(v)}: " + "; ".join(f"{w:04x} {t!r} exp={e}" for w, t, e in v[:show]))
