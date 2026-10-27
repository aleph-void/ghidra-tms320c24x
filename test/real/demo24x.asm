* demo24x.asm - small TMS320C24x program written for the Ghidra-Rare C24x module tests (Apache-2.0).
* Uses only instructions that exist on the C24x/C20x (SPRU160C); assembled with the C5x assembler c5xasm
* (the C2xx opcode set is a subset of the C5x set). Vector table, init, a 16-bit checksum loop, a
* subroutine with indirect addressing, a computed jump through a table (BACC) and a 32-bit multiply.
        .text
        B       RESET           ; 0000 RS
        B       ISR             ; 0002 K=1
        B       ISR             ; 0004 K=2
        B       ISR             ; 0006 K=3
        B       ISR             ; 0008 K=4
        B       ISR             ; 000A K=5
        B       ISR             ; 000C K=6
        B       ISR             ; 000E K=7
        B       ISR             ; 0010 K=8
        B       ISR             ; 0012 K=9
        B       ISR             ; 0014 K=10
        B       ISR             ; 0016 K=11
        B       ISR             ; 0018 K=12
        B       ISR             ; 001A K=13
        B       ISR             ; 001C K=14
        B       ISR             ; 001E K=15
        B       ISR             ; 0020 K=16
        B       ISR             ; 0022 K=17
        B       ISR             ; 0024 K=18
        B       ISR             ; 0026 K=19
        B       ISR             ; 0028 K=20
        B       ISR             ; 002A K=21
        B       ISR             ; 002C K=22
        B       ISR             ; 002E K=23
        B       ISR             ; 0030 K=24
        B       ISR             ; 0032 K=25
        B       ISR             ; 0034 K=26
        B       ISR             ; 0036 K=27
        B       ISR             ; 0038 K=28
        B       ISR             ; 003A K=29
        B       ISR             ; 003C K=30
        B       ISR             ; 003E K=31
RESET:  SETC    INTM
        SPM     0
        CLRC    OVM
        SETC    SXM
        LDP     #0
        SPLK    #0x1234,0x60
        LAR     AR1,#0x70
        LAR     AR2,#0x60
        MAR     *,AR1
        LACL    #8
        SACL    0x6f            ; counter
        LAR     AR3,#7
        CALL    SUM
        SACL    0x6e
        LACL    #2
        CALL    DISPATCH
        LT      0x60
        MPY     0x60
        PAC
        SACH    0x6d,1
        SACL    0x6c
LOOP:   IDLE
        B       LOOP
* SUM: add AR3+1 words starting at (AR2) into ACC
SUM:    LACL    #0
        MAR     *,AR2
SLOOP:  ADD     *+,0,AR2
        BANZ    SLOOP,*-,AR2
        RET
ISR:    PUSH
        SST     #1,0x61
        SST     #0,0x62
        LST     #0,0x62
        LST     #1,0x61
        POP
        CLRC    INTM
        RET
* DISPATCH: ACC = index 0..3 -> call one of four handlers through a table in program memory
DISPATCH:
        ADD     #TABLE
        TBLR    0x63
        LACL    0x63
        BACC
TABLE:  .word   H0, H1, H2, H3
H0:     LACL    #10
        RET
H1:     LACL    #11
        RET
H2:     LACL    #12
        RET
H3:     LACL    #13
        RET
        .end
