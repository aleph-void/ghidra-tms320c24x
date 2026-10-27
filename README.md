# TMS320C24 Processor Extension for Ghidra

Author: Paul G. Banks [(https://paulbanks.org)](https://paulbanks.org)

## Notes:

This implements the disassembler for the ISA described in the TMS320F/C24x DSP Controllers Reference Guide (spru160c.pdf), allowing you to load firmwares based on that ISA into Ghidra.

~~At this stage, all opcodes should be described but I have implemented limited opcode semantics so the decompilation output will not be useful.~~
**Updated by Ghidra-Rare:** the module now has full p-code semantics (carry, overflow with OVM saturation, SXM sign
extension, product shift modes, repeat, hardware stack, indirect addressing with reverse-carry modes, status
registers), checked by 125 hand-computed emulator cases per byte order, a differential against MAME `unidasm`,
the manual's opcode tables and an independent assembler. See [GHIDRA-RARE.md](GHIDRA-RARE.md) for what was verified,
what is not covered and how to run the tests, and [CREDITS.md](CREDITS.md) for provenance.

~~At some point I may do more if time/demand permits; at the time of writing there's a good chance of some more updates.~~

## Languages

| Language ID | Word order in the file |
|---|---|
| `TMS320c24x:LE:16:default` (upstream's ID, unchanged) | low byte first |
| `TMS320c24x:BE:16:default` (added) | high byte first |

Program, data and I/O space are separate 64K-word spaces (`code`, `ram`, `io`). The SLEIGH source is generated
(`tools/gen_c24x.py` writes `tms320c24x.sinc`); edit the generator, not the generated file.

## Known limitations (state of the original README / sources and what became of them)

| Item | Status |
|---|---|
| "limited opcode semantics so the decompilation output will not be useful" | fixed: every instruction has p-code |
| `TODO: Fix for reverse carry` (`*BR0+`, `*BR0-`) | fixed: bit-reversed addition and subtraction |
| README claimed the extension builds for Ghidra 11.4.1 (`Makefile`, `version=11.4.1`) | stale: builds for Ghidra 12.1.3, 12.1.4 and 12.2; the Makefile and the Ghidra skeleton plugin sources were removed |
| Hardware stack modelled as a one-byte memory stack in an `hwstack` space (`SP`) | replaced by the eight-level shifting stack `STK0`-`STK7` the manual describes (PUSH/POP/CALL/RET shift all levels); the `SP` register no longer exists |
| ST0/ST1 as registers | status bits are separate flag registers (`ARP`, `OV`, `C`, ...); SST/LST assemble and split ST0/ST1 |
| Instruction text (`ADD *+,0,AR2`, `LAR AR0,0x1`, ...) | now TI assembler syntax; unmodelled conditions are named (`BCND ...,EQ,NOV`) |
| IDLE | remains a `idle()` pcode op (hardware low-power state) |
| Computed branches (`BACC`, `CALA`) through tables | decompile as indirect jumps/calls; no table analyzer |

Prebuilt zips: see the Releases page of this repository.
