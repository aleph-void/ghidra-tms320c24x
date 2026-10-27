#!/usr/bin/env python3
"""Convert c5xasm flat output ("P <addr> <word>" lines) to a little-endian word image: p2bin.py in.txt out.bin"""
import sys
w = {}
for l in open(sys.argv[1]):
    p = l.split()
    if len(p) == 3 and p[0] == "P":
        w[int(p[1], 16)] = int(p[2], 16)
n = max(w) + 1
open(sys.argv[2], "wb").write(b"".join((w.get(i, 0)).to_bytes(2, "little") for i in range(n)))
print(f"{len(w)} words, image {n} words")
