#!/usr/bin/env bash
# Hand-computed p-code checks for TMS320C24x (both byte orders).
#   GHIDRA_INSTALL_DIR=... test/emu-test.sh [outdir]
set -euo pipefail
: "${GHIDRA_INSTALL_DIR:?set GHIDRA_INSTALL_DIR}"
HERE=$(cd "$(dirname "$0")" && pwd)
OUTD=$(readlink -m "${1:-${TMPDIR:-/tmp}/c24x-emu}")
mkdir -p "$OUTD"
PROJ=$(mktemp -d "${TMPDIR:-/tmp}/c24x-emu.XXXXXX")
trap 'rm -rf "$PROJ"' EXIT
head -c 4096 /dev/zero > "$PROJ/zero.bin"
rc=0
for lang in TMS320c24x:LE:16:default TMS320c24x:BE:16:default; do
	out="$OUTD/$(echo "$lang" | tr ':' '_').txt"
	"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" "$PROJ" p \
		-import "$PROJ/zero.bin" -loader BinaryLoader -processor "$lang" -noanalysis \
		-scriptPath "$HERE" -postScript C24xEmuTest.java "$HERE/emu/cases.txt" "$out" \
		-deleteProject >"$PROJ/log.txt" 2>&1 \
		|| { tail -40 "$PROJ/log.txt" >&2; exit 1; }
	[[ -s $out ]] || { grep -E 'ERROR|Exception' "$PROJ/log.txt" | head -20 >&2; exit 1; }
	grep -v '^PASS' "$out"
	grep -q ' 0 failed' "$out" || rc=1
done
exit $rc
