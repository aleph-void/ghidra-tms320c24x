# Ghidra-Rare notes: TMS320C24x

Provenance, license and the list of changes: [CREDITS.md](CREDITS.md). Upstream: banksy-git/ghidra-tms320c24x
(Apache-2.0). Covers the TI TMS320F/C24x and TMS320C20x DSP controllers (the C2xx core, SPRU160C).

## What the module is

`TMS320c24x:LE:16:default` and `:BE:16:default` (byte order of the 16-bit words in the file). Spaces `code`
(program), `ram` (data) and `io`, each 64K words. The SLEIGH is generated: `python3 tools/gen_c24x.py
data/languages` writes `tms320c24x.sinc` and the two `.slaspec` wrappers. The generator started from
Ghidra-Rare's TMS320C5x generator because the C2xx opcodes are a subset of the C5x opcodes (same encodings).

## Testing

```
ln -s <this dir> $GHIDRA_INSTALL_DIR/Ghidra/Processors/TMS320C24x
GHIDRA_INSTALL_DIR=<scratch Ghidra 12.1.x> test/run-tests.sh <workdir without dot components> [--real]
```
Needs `unidasm` (MAME), python3, a C compiler (c5xasm builds from source). With Ghidra-Rare's TMS320C2x module
linked into the same install the suite also cross-checks the shared subset against its C5x language.

## Results

| Area | Result |
|---|---|
| Builds | compiles on Ghidra 12.1.3, 12.1.4 and 12.2; both `.sla` about 90 KB; release zips built with `tools/build-module.sh --standard --name TMS320C24x` |
| Decode vs SPRU160C | all 65,536 first words x random second word: 51,266 agree on mnemonic and length with the manual's opcode tables (`test/c24x_isa.py`), 14,270 undefined in both, 0 differences (51,266 + 14,270 = 65,536). Reserved indirect mode ARU=011 is undefined; direct `MAR` is a no-operation; `NORM` is accepted only in the indirect form (`NORM ind`) |
| Decode vs MAME unidasm (`-arch tms320c5x`) | 98,304 records (every first word + 32,768 random): 76,958 inside the C24x set compared, 64,080 identical text and length, 12,878 explained, 0 unexplained. Explained: MAME does not decode `MPY #k13` (12,346), decodes `MACD` as one word (365) and `NORM` as two (167). The 21,346 records outside the C24x set are C5x-only instructions (XC, delayed branches, BLDP, APL/OPL/XPL/CPL, ...), bit-7-clear `B`/`CALL`/`BANZ`, reserved bits that MAME ignores, or undefined in both |
| Cross-check with the TMS320C5x module | all 76,958 decoded records identical, except that for 85 `SST` page-0 direct operands the C5x module prints its memory-mapped register name (`IMR`, ...) where this module prints the address (accepted by the test) |
| Every constructor | 1469/1469 reached under 64 context combinations (SXM, OVM, PM known or not; ARP, DP known or not; repeat) |
| Round trip | 76,958 decoded records re-assembled by c5xasm: 62,392 identical, 14,566 explained (next-AR bits ignored when N=0; equivalent condition encodings; c5xasm's AND/OR/XOR #lk,16 form), 0 unexplained |
| Semantics | 125 hand-computed emulator cases from SPRU160C per byte order (ALU with shifts, carry/borrow, overflow and saturation, SXM/OVM/PM known and run-time, multiplier and accumulate instructions, `LTD`/`MACD` data moves, indirect modes incl. reverse-carry and next-ARP, status register load/store, `NORM`, `BIT`/`BITT`, `CMPR`, block moves, `TBLR`/`TBLW`, repeat, branches, calls, conditionals incl. OV clearing, software interrupts, 8-level stack), plus 1 deliberately wrong expectation which is reported (XFAIL). The first run found one module bug (see below) |
| Real code | c5xtools' nine TI-assembled example images (MIT): 674 lines identical to unidasm at every line start, 0 different; 135 lines use C5x-only instructions (outside this CPU). `test/real/demo24x.asm` (own program, assembled by c5xasm; vector table, init, subroutines with indirect addressing, BANZ loop, SST/LST, table dispatch with BACC): both byte orders, 4 functions, 72 instructions identical to unidasm, 0 bookmarks, 4/4 functions decompile |

## Bugs found by the tests (in the generator-based rewrite)

- `LPH` wrote to an undefined name (SLEIGH silently makes it a temporary) instead of `PREGH`; found by the emulator.
  The SLEIGH compiler's "operations wrote to temporaries" warning flags this class of error: the build must show none
  (`sleigh -t`).

The upstream constructors (replaced) had these defects: `ind` used the ARU field as the AR number, empty semantics for
most instructions, `CALL` pushed 1 byte on a byte-addressed fake stack, `BCND`/`CC`/`RETC` rejected valid ZLVC
combinations (1,152 encodings) and decoded the reserved ARU=011 mode.

## Doesn't work / limits

- `IDLE` is a pcode op `idle()` (power-down state, nothing for p-code to compute).
- `BACC`/`CALA` through a table are indirect jumps/calls; Ghidra cannot resolve the table, so handlers reached only
  that way are not found by auto-analysis (no table analyzer written).
- Repeat is modelled by looping the next instruction with the RPT-set context flag; interrupts inside a repeat loop are
  not modelled (the hardware also treats a repeated instruction as non-interruptible).
- No ELF/COFF opinion: TI COFF for the C2xx and C5x share the same target ID, so a loader opinion would collide with
  the TMS320C5x module; import raw images and choose the language.
- `DMOV`/`LTD`/`MACD` always perform the data move (the hardware skips it for external memory and memory-mapped registers).
- Memory map (on-chip RAM blocks, CNF) is not modelled; peripheral registers appear as symbols in the pspec.

## Unverified

- No real TMS320F24x/C20x firmware was available under a license that allows it, so real-code coverage is the
  c5xtools images (C5x firmware restricted to the shared subset) and the demo program.
- Reverse-carry (`*BR0+`, `*BR0-`) is covered by hand-computed cases only (MAME's C5x disassembler is decode-only).
- Semantics of `IN`/`OUT` timing, wait states and interrupt masks.
- Behaviour of devices other than the ones in SPRU160C (F243/F2407 peripheral maps are symbols only).

## Confirmed reference-tool bugs

- MAME unidasm `tms320c5x`: no decode for `MPY #k` (C000h-DFFFh); `NORM` printed as two words; `MACD` as one word;
  ignores reserved bits in `SPM`, `CMPR`,
  `B`/`CALL`/`BANZ`.
- c5xasm: assembles `AND/OR/XOR #lk,16` as shift 0 encodings (BFx0) where SPRU056D gives BE81h-BE83h.
