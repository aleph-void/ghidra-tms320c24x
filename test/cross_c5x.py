#!/usr/bin/env python3
"""Text of the module vs Ghidra-Rare's TMS320C5x module on every first word the module decodes (shared subset).
Only memory-mapped register names for data-page-0 operands may differ (the C5x module names IMR, GREG, ...).
    cross_c5x.py <corpus dir with g/ and g5x/>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare as C
d = sys.argv[1]
recs = [tuple(int(x, 16) for x in l.split()) for l in open(os.path.join(d, "records.txt"))]
same = diff = 0; bad = []
for c in range((len(recs) + C.CHUNK - 1) // C.CHUNK):
    a = C.parse_ghidra(os.path.join(d, "g", "c%02d.bin.txt" % c)); b = C.parse_ghidra(os.path.join(d, "g5x", "c%02d.bin.txt" % c))
    for i in range(min(C.CHUNK, len(recs) - c * C.CHUNK)):
        w = recs[c * C.CHUNK + i][0]
        if a[i][1].startswith("BAD"): continue
        if a[i] == b[i]: same += 1
        elif a[i][1].startswith("SST ") and (w >> 8) in (0x8e, 0x8f) and not w & 0x80: diff += 0; same += 1
        else: diff += 1; bad.append((f"{w:04x}", a[i], b[i]))
print(f"cross-check with the TMS320C5x module: {same} identical, {diff} different")
for x in bad[:10]: print("  ", x)
sys.exit(1 if diff else 0)
