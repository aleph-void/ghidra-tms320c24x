#!/usr/bin/env python3
"""Module vs MAME unidasm (-arch tms320c5x, the C5x set contains the C2xx set) on the corpus.

    cmp_mame.py <corpus dir> [--show N]

<corpus dir> holds records.txt, m/cNN.txt (unidasm) and g/cNN.bin.txt (module, TmsDump stride 4).
Only first words that are valid C24x instructions per c24x_isa.py (SPRU160C), or that the module
decodes, are compared (the rest of the C5x opcode space is outside this CPU). The text comparison
reuses compare.py's normalisation. Exit status 1 if any difference is unexplained."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare as C
from c24x_isa import lookup

d = sys.argv[1]
show = int(sys.argv[sys.argv.index("--show") + 1]) if "--show" in sys.argv else 4
recs = [tuple(int(x, 16) for x in l.split()) for l in open(os.path.join(d, "records.txt"))]
tot = exact = outside = 0
classes = collections.Counter()
unexpl = collections.defaultdict(list)
for c in range((len(recs) + C.CHUNK - 1) // C.CHUNK):
    m = C.parse_mame(os.path.join(d, "m", "c%02d.txt" % c))
    g = C.parse_ghidra(os.path.join(d, "g", "c%02d.bin.txt" % c))
    for i in range(min(C.CHUNK, len(recs) - c * C.CHUNK)):
        word, w2 = recs[c * C.CHUNK + i]
        gg = g.get(i, (1, "BAD")); mm = m.get(i, (1, "?"))
        gbad = gg[1].startswith("BAD")
        if lookup(word) is None and gbad:
            outside += 1
            continue
        tot += 1
        mbad = "??" in mm[1]
        same = (not gbad and not mbad and gg[0] == mm[0] and
                C.canon("c5x", gg[1], True, word, w2) == C.canon("c5x", mm[1], False, word, w2))
        if same:
            exact += 1
            continue
        cls = C.explain("c5x", word, w2, gg, mm)
        if cls:
            classes[cls] += 1
        else:
            key = (word >> 8, gg[1].split(" ")[0], mm[1].split(" ")[0])
            unexpl[key].append((word, w2, gg, mm))
nun = sum(len(v) for v in unexpl.values())
print(f"{tot} compared (valid C24x first words x random 2nd word + module-decoded), {outside} outside the C24x set "
      f"(both undefined), {exact} identical after normalisation, {sum(classes.values())} explained, {nun} unexplained")
for k, v in classes.most_common():
    print(f"  explained {v:6d}  {k}")
for k, v in sorted(unexpl.items(), key=lambda kv: -len(kv[1])):
    print(f"  UNEXPLAINED {len(v):6d}  op {k[0]:02x}  module {k[1]}  mame {k[2]}")
    for word, w2, gg, mm in v[:show]:
        print(f"      {word:04x} {w2:04x}  module[{gg[0]}] {gg[1]!r}  mame[{mm[0]}] {mm[1]!r}")
sys.exit(1 if nun else 0)
