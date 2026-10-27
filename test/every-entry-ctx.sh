#!/usr/bin/env bash
# Prints the context settings used by the every-entry test: every combination of the tracked modes
# (SXM, OVM, PM each unknown or known), plus ARP/DP known/unknown and repeat on/off.
python3 - <<'PY'
import itertools
out = []
modes = lambda name, vals: [f"{name}_k=0,{name}_v=0"] + [f"{name}_k=1,{name}_v={v}" for v in vals]
for i, (s, o, p) in enumerate(itertools.product(modes("sxm", (0, 1)), modes("ovm", (0, 1)), modes("pm", (0, 1, 2, 3)))):
    out.append(f"{s},{o},{p},arp_k={i % 2},dp_k={i % 2},rpt={i % 2}")
print(" ".join(out))
PY
