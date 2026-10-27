#!/usr/bin/env bash
# TMS320C24x module test suite.
#   GHIDRA_INSTALL_DIR=<scratch Ghidra 12.1.x> test/run-tests.sh <workdir> [--real]
# The module must be linked into the install: ln -s <module dir> $GHIDRA_INSTALL_DIR/Ghidra/Processors/TMS320C24x
# Needs python3, MAME's unidasm; JAVA_HOME optional. The Ghidra project path must not contain a component
# starting with a dot (PROJ_DIR, default <workdir>/proj, is used for headless projects).
#  1. the generator reproduces the checked-in tms320c24x.sinc / .slaspec files
#  2. the specs compile (.sla well under 16 MB)
#  3. emulator: hand-computed p-code results (test/emu/cases.txt), incl. one deliberately wrong expectation
#  4. every-entry: every SLEIGH constructor reached
#  5. decode: all 65,536 first words x random second words + 32,768 random records
#       a. module vs the SPRU160C opcode tables (test/c24x_isa.py)
#       b. module vs MAME unidasm (-arch tms320c5x; the C5x set contains the C2xx set)
#       c. if Ghidra-Rare's TMS320C5x module is installed: text identical on the shared subset
#  6. round trip: the module's text re-assembled by c5xasm (independent assembler) gives the same words
#  --real: fetch c5xtools (pinned, MIT); linear comparison of its TI-assembled images with unidasm; assemble
#          test/real/demo24x.asm, analyse it headless, decompile, compare with unidasm
set -euo pipefail
: "${GHIDRA_INSTALL_DIR:?set GHIDRA_INSTALL_DIR}"
HERE=$(cd "$(dirname "$0")" && pwd)
MOD=$(cd "$HERE/.." && pwd)
REAL=0; ARGS=()
for a in "$@"; do if [[ $a == --real ]]; then REAL=1; else ARGS+=("$a"); fi; done
W=$(readlink -m "${ARGS[0]:-${TMPDIR:-/tmp}/c24x-tests}"); mkdir -p "$W"
export TMPDIR=$W GHIDRA_INSTALL_DIR
PROJ_DIR=${PROJ_DIR:-$W/proj}; mkdir -p "$PROJ_DIR"
LE=TMS320c24x:LE:16:default
fail=0
P="$GHIDRA_INSTALL_DIR/Ghidra/Processors/TMS320C24x"
if [[ ! -e $P ]]; then ln -s "$MOD" "$P"; fi

echo "== 1. generator reproduces the checked-in SLEIGH"
python3 "$MOD/tools/gen_c24x.py" "$W/gen"
for f in tms320c24x.sinc tms320c24x.slaspec tms320c24x_be.slaspec; do
	cmp "$W/gen/$f" "$MOD/data/languages/$f" || fail=1
done
echo "== 2. SLEIGH compiles"
for s in tms320c24x tms320c24x_be; do
	"$GHIDRA_INSTALL_DIR/support/sleigh" "$MOD/data/languages/$s.slaspec" 2>&1 | grep -E "^ERROR" && fail=1 || true
	sz=$(stat -c %s "$MOD/data/languages/$s.sla"); echo "   $s.sla: $sz bytes"; ((sz < 16 * 1024 * 1024))
done
echo "== 3. emulator"
"$HERE/emu-test.sh" "$W/emu" || fail=1
echo "== 4. every constructor reached"
D=$W/dec; rm -rf "$D"; mkdir -p "$D/m"
python3 "$HERE/gen_corpus.py" c5x le "$D" 32768 1
"$HERE/every-entry.sh" $LE "$D/chunks" "$W/ee.txt" $("$HERE/every-entry-ctx.sh") || fail=1
grep -q ' 0 not reached' "$W/ee.txt" || { grep 'NOT REACHED' "$W/ee.txt" | head; fail=1; }
echo "== 5. decode"
"$HERE/ghidra-dis.sh" $LE "$D/chunks" "$D/g/" 4
echo "   a. against the SPRU160C opcode tables"
python3 "$HERE/cmp_isa.py" "$D" "$D/g" --show 3 | tee "$W/cmp_isa.txt" | head -20
! grep -q "manual valid, module BAD\|module decodes, manual invalid\|differs" "$W/cmp_isa.txt" || fail=1
if command -v unidasm >/dev/null; then
	echo "   b. against MAME unidasm"
	for f in "$D"/chunks/*.bin; do unidasm "$f" -arch tms320c5x > "$D/m/$(basename "$f" .bin).txt"; done
	python3 "$HERE/cmp_mame.py" "$D" --show 3 | tee "$W/cmp_mame.txt" | head -20 || fail=1
else echo "   (skipped: no unidasm)"; fi
if [[ -e $GHIDRA_INSTALL_DIR/Ghidra/Processors/TMS320C2x ]]; then
	echo "   c. against Ghidra-Rare's TMS320C5x module"
	"$HERE/ghidra-dis.sh" TMS320C5x:LE:16:default "$D/chunks" "$D/g5x/" 4
	python3 "$HERE/cross_c5x.py" "$D" || fail=1
fi
echo "== 6. round trip through c5xasm"
"$HERE/fetch-inputs.sh" "$W/inputs" >/dev/null
python3 "$HERE/roundtrip.py" c5x "$W/inputs/c5xtools/tools/c5xasm/c5xasm" "$D/records.txt" "$D/g" "$W/rt" | head -6 || fail=1
if ((REAL)); then
	echo "== 7. real code"
	"$HERE/real-test.sh" "$W/inputs" "$W/real" || fail=1
fi
((fail == 0)) && echo "ALL PASSED" || { echo "FAILURES"; exit 1; }
