#!/usr/bin/env bash
# Fetch the freely licensed test inputs (pinned URL and SHA-256; nothing is committed):
#   test/fetch-inputs.sh <dir>
# wgrzegorz/c5xtools (MIT): TI-assembled example images (their C2xx-compatible parts are decoded and
# compared) and c5xasm, the assembler used for the round trip and to assemble test/real/demo24x.asm.
set -euo pipefail
D=$(readlink -m "$1"); mkdir -p "$D"
fetch() { # url sha256 out
	if [[ ! -f $3 ]] || ! echo "$2  $3" | sha256sum -c --quiet - 2>/dev/null; then
		curl -sSL -o "$3.part" "$1"; mv "$3.part" "$3"
	fi
	echo "$2  $3" | sha256sum -c --quiet - || { echo "checksum mismatch: $3" >&2; exit 1; }
}
fetch https://codeload.github.com/wgrzegorz/c5xtools/tar.gz/90ee7c91b4aba11d7089365a62eaf658970226c0 \
	b679f38f84798d1c64b38dd4c26b59c97f6b645f898318cf7631a439023d2092 "$D/c5xtools.tar.gz"
if [[ ! -x $D/c5xtools/tools/c5xasm/c5xasm ]]; then
	rm -rf "$D/c5xtools"; mkdir -p "$D/c5xtools"
	tar -xzf "$D/c5xtools.tar.gz" -C "$D/c5xtools" --strip-components=1
	make -s -C "$D/c5xtools/tools/c5xasm" >/dev/null 2>&1 || (cd "$D/c5xtools" && sh build.sh >/dev/null 2>&1)
fi
ls "$D"/c5xtools/test/examples/golden/*.img "$D/c5xtools/tools/c5xasm/c5xasm" >/dev/null
echo "inputs ready in $D"
