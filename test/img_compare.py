#!/usr/bin/env python3
"""Linear-sweep comparison on real TI-assembled images: unidasm (tms320c5x) lists each image; at every line
start whose first word is a valid C24x instruction (c24x_isa.py) the module's decode (TmsDump, stride 1)
must equal unidasm's after normalisation. Lines using C5x-only instructions are counted separately.
    img_compare.py <image.img> <TmsDump output for that image>"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare as C
from c24x_isa import lookup
img, dump = sys.argv[1:3]
out = subprocess.run(["unidasm", img, "-arch", "tms320c5x"], capture_output=True, text=True).stdout
data = open(img, "rb").read()
words = [data[i] | data[i + 1] << 8 for i in range(0, len(data) - 1, 2)]
lines = []
for l in out.splitlines():
    m = re.match(r"^\s*([0-9a-f]+): (\S+)(?: (\S{4}))?\s+(.*)$", l)
    if m: lines.append((int(m.group(1), 16), m.group(4).strip()))
g = {}
for l in open(dump):
    a, n, t = l.rstrip("\n").split(" ", 2); g[int(a, 16)] = (int(n), t)
same = c5only = diff = 0; bad = []
for i, (a, t) in enumerate(lines):
    n = (lines[i + 1][0] - a) if i + 1 < len(lines) else g[a][0]
    w = words[a]; w2 = words[a + 1] if a + 1 < len(words) else 0
    if lookup(w) is None:
        c5only += 1; continue
    gg = g[a]
    if gg[0] == n and C.canon("c5x", gg[1], True, w, w2) == C.canon("c5x", t, False, w, w2):
        same += 1
    else:
        cls = C.explain("c5x", w, w2, gg, (n, t))
        if cls: same += 1
        else: diff += 1; bad.append(f"  {a:04x} {w:04x}: module {gg[1]!r} mame {t!r}")
print(f"{os.path.basename(img)}: {same} identical, {diff} different, {c5only} lines with C5x-only instructions")
for b in bad: print(b)
sys.exit(1 if diff else 0)
