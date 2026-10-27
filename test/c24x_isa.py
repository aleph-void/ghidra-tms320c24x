#!/usr/bin/env python3
"""TMS320F/C24x instruction set as listed in SPRU160C (Tables 7-1 .. 7-6): (mnemonic, mask, value, words).
Typed in from the manual's opcode column by hand ("I" = indirect bit, "A" = address bits, fields are masked out).
A first word is a valid instruction when one entry matches; for entries with an I bit that is set,
the ARU field (bits 6-4) must not be 011 (reserved)."""

def pat(s, ind=False):
    s = s.replace(" ", "")
    assert len(s) == 16, s
    mask = sum(1 << (15 - i) for i, c in enumerate(s) if c in "01")
    val = sum(1 << (15 - i) for i, c in enumerate(s) if c == "1")
    return mask, val

# (mnemonic, pattern, words, takes_ind)
T = [
 ("ABS", "1011 1110 0000 0000", 1, 0),
 ("ADD", "0010 .... IAAA AAAA", 1, 1),
 ("ADD", "1011 1111 1001 ....", 2, 0),
 ("ADD", "0110 0001 IAAA AAAA", 1, 1),
 ("ADD", "1011 1000 .... ....", 1, 0),
 ("ADDC", "0110 0000 IAAA AAAA", 1, 1),
 ("ADDS", "0110 0010 IAAA AAAA", 1, 1),
 ("ADDT", "0110 0011 IAAA AAAA", 1, 1),
 ("AND", "0110 1110 IAAA AAAA", 1, 1),
 ("AND", "1011 1111 1011 ....", 2, 0),
 ("AND", "1011 1110 1000 0001", 2, 0),
 ("CMPL", "1011 1110 0000 0001", 1, 0),
 ("LACC", "0001 .... IAAA AAAA", 1, 1),
 ("LACC", "1011 1111 1000 ....", 2, 0),
 ("LACC", "0110 1010 IAAA AAAA", 1, 1),
 ("LACL", "0110 1001 IAAA AAAA", 1, 1),
 ("LACL", "1011 1001 .... ....", 1, 0),
 ("LACT", "0110 1011 IAAA AAAA", 1, 1),
 ("NEG", "1011 1110 0000 0010", 1, 0),
 ("NORM", "1010 0000 1AAA AAAA", 1, 1),   # indirect only: the manual lists "NORM ind"
 ("OR", "0110 1101 IAAA AAAA", 1, 1),
 ("OR", "1011 1111 1100 ....", 2, 0),
 ("OR", "1011 1110 1000 0010", 2, 0),
 ("ROL", "1011 1110 0000 1100", 1, 0),
 ("ROR", "1011 1110 0000 1101", 1, 0),
 ("SACH", "1001 1... IAAA AAAA", 1, 1),
 ("SACL", "1001 0... IAAA AAAA", 1, 1),
 ("SFL", "1011 1110 0000 1001", 1, 0),
 ("SFR", "1011 1110 0000 1010", 1, 0),
 ("SUB", "0011 .... IAAA AAAA", 1, 1),
 ("SUB", "1011 1111 1010 ....", 2, 0),
 ("SUB", "0110 0101 IAAA AAAA", 1, 1),
 ("SUB", "1011 1010 .... ....", 1, 0),
 ("SUBB", "0110 0100 IAAA AAAA", 1, 1),
 ("SUBC", "0000 1010 IAAA AAAA", 1, 1),
 ("SUBS", "0110 0110 IAAA AAAA", 1, 1),
 ("SUBT", "0110 0111 IAAA AAAA", 1, 1),
 ("XOR", "0110 1100 IAAA AAAA", 1, 1),
 ("XOR", "1011 1111 1101 ....", 2, 0),
 ("XOR", "1011 1110 1000 0011", 2, 0),
 ("ZALR", "0110 1000 IAAA AAAA", 1, 1),
 ("ADRK", "0111 1000 .... ....", 1, 0),
 ("BANZ", "0111 1011 1AAA AAAA", 2, 1),
 ("CMPR", "1011 1111 0100 01..", 1, 0),
 ("LAR", "0000 0... IAAA AAAA", 1, 1),
 ("LAR", "1011 0... .... ....", 1, 0),
 ("LAR", "1011 1111 0000 1...", 2, 0),
 ("MAR", "1000 1011 IAAA AAAA", 1, 1),
 ("SAR", "1000 0... IAAA AAAA", 1, 1),
 ("SBRK", "0111 1100 .... ....", 1, 0),
 ("APAC", "1011 1110 0000 0100", 1, 0),
 ("LPH", "0111 0101 IAAA AAAA", 1, 1),
 ("LT", "0111 0011 IAAA AAAA", 1, 1),
 ("LTA", "0111 0000 IAAA AAAA", 1, 1),
 ("LTD", "0111 0010 IAAA AAAA", 1, 1),
 ("LTP", "0111 0001 IAAA AAAA", 1, 1),
 ("LTS", "0111 0100 IAAA AAAA", 1, 1),
 ("MAC", "1010 0010 IAAA AAAA", 2, 1),
 ("MACD", "1010 0011 IAAA AAAA", 2, 1),
 ("MPY", "0101 0100 IAAA AAAA", 1, 1),
 ("MPY", "110. .... .... ....", 1, 0),
 ("MPYA", "0101 0000 IAAA AAAA", 1, 1),
 ("MPYS", "0101 0001 IAAA AAAA", 1, 1),
 ("MPYU", "0101 0101 IAAA AAAA", 1, 1),
 ("PAC", "1011 1110 0000 0011", 1, 0),
 ("SPAC", "1011 1110 0000 0101", 1, 0),
 ("SPH", "1000 1101 IAAA AAAA", 1, 1),
 ("SPL", "1000 1100 IAAA AAAA", 1, 1),
 ("SPM", "1011 1111 0000 00..", 1, 0),
 ("SQRA", "0101 0010 IAAA AAAA", 1, 1),
 ("SQRS", "0101 0011 IAAA AAAA", 1, 1),
 ("B", "0111 1001 1AAA AAAA", 2, 1),
 ("BACC", "1011 1110 0010 0000", 1, 0),
 ("BCND", "1110 00.. .... ....", 2, 0),
 ("CALA", "1011 1110 0011 0000", 1, 0),
 ("CALL", "0111 1010 1AAA AAAA", 2, 1),
 ("CC", "1110 10.. .... ....", 2, 0),
 ("INTR", "1011 1110 011. ....", 1, 0),
 ("NMI", "1011 1110 0101 0010", 1, 0),
 ("RET", "1110 1111 0000 0000", 1, 0),
 ("RETC", "1110 11.. .... ....", 1, 0),
 ("TRAP", "1011 1110 0101 0001", 1, 0),
 ("BIT", "0100 .... IAAA AAAA", 1, 1),
 ("BITT", "0110 1111 IAAA AAAA", 1, 1),
 ("CLRC", "1011 1110 0100 0000", 1, 0), ("SETC", "1011 1110 0100 0001", 1, 0),
 ("CLRC", "1011 1110 0100 0010", 1, 0), ("SETC", "1011 1110 0100 0011", 1, 0),
 ("CLRC", "1011 1110 0100 0100", 1, 0), ("SETC", "1011 1110 0100 0101", 1, 0),
 ("CLRC", "1011 1110 0100 0110", 1, 0), ("SETC", "1011 1110 0100 0111", 1, 0),
 ("CLRC", "1011 1110 0100 1010", 1, 0), ("SETC", "1011 1110 0100 1011", 1, 0),
 ("CLRC", "1011 1110 0100 1100", 1, 0), ("SETC", "1011 1110 0100 1101", 1, 0),
 ("CLRC", "1011 1110 0100 1110", 1, 0), ("SETC", "1011 1110 0100 1111", 1, 0),
 ("IDLE", "1011 1110 0010 0010", 1, 0),
 ("LDP", "0000 1101 IAAA AAAA", 1, 1),
 ("LDP", "1011 110. .... ....", 1, 0),
 ("LST", "0000 1110 IAAA AAAA", 1, 1),
 ("LST", "0000 1111 IAAA AAAA", 1, 1),
 ("NOP", "1000 1011 0000 0000", 1, 0),
 ("POP", "1011 1110 0011 0010", 1, 0),
 ("POPD", "1000 1010 IAAA AAAA", 1, 1),
 ("PSHD", "0111 0110 IAAA AAAA", 1, 1),
 ("PUSH", "1011 1110 0011 1100", 1, 0),
 ("RPT", "0000 1011 IAAA AAAA", 1, 1),
 ("RPT", "1011 1011 .... ....", 1, 0),
 ("SST", "1000 1110 IAAA AAAA", 1, 1),
 ("SST", "1000 1111 IAAA AAAA", 1, 1),
 ("BLDD", "1010 1000 IAAA AAAA", 2, 1),
 ("BLDD", "1010 1001 IAAA AAAA", 2, 1),
 ("BLPD", "1010 0101 IAAA AAAA", 2, 1),
 ("DMOV", "0111 0111 IAAA AAAA", 1, 1),
 ("IN", "1010 1111 IAAA AAAA", 2, 1),
 ("OUT", "0000 1100 IAAA AAAA", 2, 1),
 ("SPLK", "1010 1110 IAAA AAAA", 2, 1),
 ("TBLR", "1010 0110 IAAA AAAA", 1, 1),
 ("TBLW", "1010 0111 IAAA AAAA", 1, 1),
]

def compile_table():
    out = []
    for mn, p, w, ind in T:
        s = p.replace(" ", "")
        # '.' and 'A' and 'I' are don't-care fields, except the leading '1' of B/BANZ/CALL (written 1AAA).
        mask = sum(1 << (15 - i) for i, c in enumerate(s) if c in "01")
        val = sum(1 << (15 - i) for i, c in enumerate(s) if c == "1")
        if ind and mn not in ("B", "BANZ", "CALL", "NORM"):
            mask &= 0xFF7F  # I bit free (direct or indirect)
        out.append((mn, mask, val, w, bool(ind)))
    return out

TABLE = compile_table()

def lookup(w):
    """Return (mnemonic, words) of the valid decode of first word w, or None. Where two entries overlap
    (direct MAR is encoded as NOP) the one with more fixed bits wins."""
    best = None
    for mn, mask, val, words, ind in TABLE:
        if w & mask == val:
            if ind and (w & 0x80) and ((w >> 4) & 7) == 3:
                continue
            if best is None or bin(mask).count("1") > best[0]:
                best = (bin(mask).count("1"), mn, words)
    return best[1:] if best else None

if __name__ == "__main__":
    n = sum(1 for w in range(65536) if lookup(w))
    print("valid first words:", n)
