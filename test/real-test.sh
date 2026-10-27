#!/usr/bin/env bash
# Real code for the TMS320C24x module:  test/real-test.sh <inputs dir from fetch-inputs.sh> <outdir>
#  1. c5xtools' nine TI-assembled example images (MIT): decoded at every unidasm line start; lines that
#     use C5x-only instructions are counted separately (flow-following analysis stops at them)
#  2. test/real/demo24x.asm assembled by c5xasm, imported (both byte orders), analysed, decompiled, compared
#     with unidasm; expect no bookmarks and every function decompiled
set -euo pipefail
: "${GHIDRA_INSTALL_DIR:?set GHIDRA_INSTALL_DIR}"
HERE=$(cd "$(dirname "$0")" && pwd)
IN=$(readlink -f "$1"); OUTD=$(readlink -m "$2"); mkdir -p "$OUTD/img"
PROJ=${PROJ_DIR:-$OUTD/proj}; mkdir -p "$PROJ"
rc=0
cp "$IN"/c5xtools/test/examples/golden/*.img "$OUTD/img/"
"$HERE/ghidra-dis.sh" TMS320c24x:LE:16:default "$OUTD/img" "$OUTD/img/out/" 1
for f in "$OUTD"/img/*.img; do python3 "$HERE/img_compare.py" "$f" "$OUTD/img/out/$(basename "$f").txt" || rc=1; done
"$IN/c5xtools/tools/c5xasm/c5xasm" "$HERE/real/demo24x.asm" -o "$OUTD/demo.txt" -q >/dev/null
python3 "$HERE/p2bin.py" "$OUTD/demo.txt" "$OUTD/demo_le.img"
python3 -c "import sys;b=open(sys.argv[1],'rb').read();open(sys.argv[2],'wb').write(bytes(x for i in range(0,len(b),2) for x in (b[i+1],b[i])))" "$OUTD/demo_le.img" "$OUTD/demo_be.img"
for e in le be; do
	L=$(echo $e | tr a-z A-Z)
	"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" "$PROJ" p -import "$OUTD/demo_$e.img" -loader BinaryLoader \
		-processor "TMS320c24x:$L:16:default" -loader-baseAddr 0 -preScript TmsEntry.java 0 2 -scriptPath "$HERE" \
		-postScript TmsRealCheck.java "$OUTD/demo_$e" 30 -deleteProject >"$OUTD/demo_$e.log" 2>&1
	grep -E '^(functions|instructions|code coverage|bookmarks|decompile):' "$OUTD/demo_$e.summary" | tr '\n' ' '; echo
	grep -qx 'bookmarks: {}' "$OUTD/demo_$e.summary" || { echo "  FAIL: bookmarks" >&2; rc=1; }
	grep -q ' 0 failed, 0 timeouts; ' "$OUTD/demo_$e.summary" || { echo "  FAIL: decompile" >&2; rc=1; }
	python3 "$HERE/real-compare.py" c5x "$OUTD/demo_le.img" "$OUTD/demo_$e.dis" le 0 | tail -1
done
exit $rc
