"""Architecture diagrams: datapath/CDC, clocks and resets, async FIFO. Run: python3 docs/tools/diagrams1.py"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "generated") + os.sep
os.makedirs(OUT, exist_ok=True)



# ---------------------------------------------------------------- 1. datapath / CDC
def datapath():
    s = Svg(1320, 665, "Data path and clock-domain crossings")
    s.rect(15, 60, 645, 560, T_BLUE, BLUE, 1.5, 14)
    s.rect(660, 60, 645, 560, T_ORANGE, ORANGE, 1.5, 14)
    s.text(32, 86, "REF_CLK domain  (50 MHz)", 15, BLUE, weight="bold")
    s.text(1288, 86, "UART_CLK domain  (3.6864 MHz)", 15, ORANGE, "end", "bold")

    # quasi-static config
    s.line([(105, 270), (105, 35), (1130, 35), (1130, 150), (1100, 150)], VIOLET, 1.8, "6 4")
    s.line([(1130, 150), (1130, 495), (1100, 495)], VIOLET, 1.8, "6 4")
    s.text(130, 28, "REG2 / REG3  (parity, prescale, divider)  —  quasi-static, no synchronizer", 12, VIOLET, weight="bold")

    s.box(35, 270, 150, 70, "RegFile", T_AQUA, AQUA, 15, "16 × 8")
    s.box(35, 410, 150, 70, "ALU", T_YELLOW, YELLOW, 15, "16-bit result")
    s.box(35, 535, 150, 60, "CLK_GATE", "#ffffff", YELLOW, 14, "latch + AND")
    s.line([(110, 340), (110, 410)], INK2)
    s.text(118, 378, "REG0 / REG1", 11, INK2)
    s.line([(110, 535), (110, 480)], YELLOW)
    s.text(118, 515, "ALU_CLK", 11, INK2)

    s.box(290, 255, 210, 115, "SYS_CTRL", "#fbe3e3", RED, 17, ["14-state FSM", "opcode decoder"])
    s.line([(290, 305), (185, 305)], INK2, arrow_start=True)
    s.text(238, 296, "WrEn RdEn", 10.5, INK2, "middle")
    s.text(238, 322, "Addr / Data", 10.5, INK2, "middle")
    s.line([(300, 370), (300, 445), (185, 445)], INK2, arrow_start=True)
    s.text(215, 436, "FUN  EN", 10.5, INK2)
    s.text(205, 462, "ALU_OUT  OUT_Valid", 10.5, INK2)
    s.line([(330, 370), (330, 565), (185, 565)], YELLOW)
    s.text(342, 552, "Gate_EN", 11, INK2)

    # RX crossing
    s.box(560, 105, 200, 80, "DATA_SYNC", T_VIOLET, VIOLET, 16, ["2-flop enable sync", "+ pulse-captured bus"], sw=2.5)
    s.tag(574, 87, "CDC  UART → REF")
    s.box(810, 105, 290, 80, "UART_RX", "#ffffff", ORANGE, 16, ["RX_CLK  ·  3-sample majority", "parity / start / stop checks"])
    s.line([(810, 145), (760, 145)], ORANGE, 2)
    s.text(785, 133, "P_DATA", 10.5, INK2, "middle")
    s.text(785, 165, "valid", 10.5, INK2, "middle")
    s.line([(560, 145), (395, 145), (395, 255)], BLUE, 2)
    s.text(402, 215, "RX_D_SYNC", 11, INK2)
    s.text(402, 229, "RX_D_VLD", 11, INK2)
    s.text(1260, 113, "RX_IN", 12, INK, "end", "bold")
    s.line([(1300, 120), (1100, 120)], INK, 2)
    s.text(1260, 168, "RF_PAR_ERR / RF_STP_ERR", 11, INK2, "end")
    s.line([(1100, 175), (1300, 175)], INK, 1.6)

    # TX crossing
    s.box(560, 430, 200, 90, "ASYNC_FIFO", T_VIOLET, VIOLET, 16, ["8 × 8, Gray pointers", "2-flop pointer syncs"], sw=2.5)
    s.tag(574, 412, "CDC  REF → UART")
    s.box(830, 430, 270, 90, "UART_TX", "#ffffff", ORANGE, 16, ["TX_CLK (÷32)  ·  115 200 baud", "serializer + parity + mux"])
    s.line([(500, 330), (530, 330), (530, 465), (560, 465)], BLUE, 2)
    s.text(538, 392, "WR_DATA", 11, INK2)
    s.text(538, 407, "WR_INC", 11, INK2)
    s.line([(560, 495), (515, 495), (515, 355), (500, 355)], BLUE, 1.6)
    s.text(508, 440, "FIFO_FULL", 11, INK2, "end")
    s.line([(760, 475), (830, 475)], ORANGE, 2)
    s.text(795, 462, "RD_DATA", 10.5, INK2, "middle")
    s.text(795, 495, "F_EMPTY", 10.5, INK2, "middle")
    s.text(1260, 468, "TX_OUT", 12, INK, "end", "bold")
    s.line([(1100, 475), (1300, 475)], INK, 2)

    s.box(850, 560, 170, 46, "PULSE_GEN", "#ffffff", ORANGE, 14, "busy → 1-cycle pop")
    s.line([(935, 520), (935, 560)], ORANGE, 1.8)
    s.text(944, 546, "busy", 11, INK2)
    s.line([(850, 583), (660, 583), (660, 520)], ORANGE, 1.8)
    s.text(668, 575, "RD_INC", 11, INK2)

    s.text(25, 648, "Solid = data / control   ·   dashed = quasi-static configuration   ·   violet boxes = the only two data crossings", 11.5, INK2, italic=True)
    s.save(OUT + "datapath_cdc.svg")


# ---------------------------------------------------------------- 2. clocks & resets
def clocking():
    s = Svg(1200, 700, "Clock generation, clock gating and reset synchronizers")
    s.text(20, 30, "Clock tree", 17, INK, weight="bold")

    s.pill(20, 70, 150, 40, "REF_CLK  50 MHz", T_BLUE, BLUE)
    s.pill(20, 200, 190, 40, "UART_CLK  3.6864 MHz", T_ORANGE, ORANGE)

    s.box(300, 62, 150, 56, "CLK_GATE", "#ffffff", YELLOW, 15, "latch + AND")
    s.line([(170, 90), (300, 90)], BLUE, 2)
    s.line([(450, 90), (560, 90)], YELLOW, 2)
    s.pill(560, 70, 120, 40, "ALU_CLK", T_YELLOW, YELLOW)
    s.text(690, 95, "→ ALU  (gated, runs only while an operation is active)", 13, INK2)
    s.text(375, 140, "Gate_EN from SYS_CTRL", 11, INK2, "middle")
    s.line([(375, 150), (375, 118)], INK2)
    s.line([(95, 110), (95, 160), (560, 160)], BLUE, 1.6)
    s.text(570, 165, "→ SYS_CTRL, RegFile, ASYNC_FIFO (write side), DATA_SYNC (dest.)", 13, INK2)

    s.text(375, 190, "REG3 = 0x20  →  ÷ 32", 12, VIOLET, "middle", "bold")
    s.box(300, 200, 150, 56, "ClkDiv_TX", "#ffffff", ORANGE, 15, "÷ REG3")
    s.box(300, 305, 150, 56, "ClkDiv_RX", "#ffffff", ORANGE, 15, "÷ ratio")
    s.line([(210, 220), (300, 228)], ORANGE, 2)
    s.line([(110, 240), (110, 333), (300, 333)], ORANGE, 2)
    s.line([(450, 228), (560, 228)], ORANGE, 2)
    s.line([(450, 333), (560, 333)], ORANGE, 2)
    s.pill(560, 208, 120, 40, "TX_CLK", T_ORANGE, ORANGE)
    s.pill(560, 313, 120, 40, "RX_CLK", T_ORANGE, ORANGE)
    s.text(690, 233, "→ UART_TX, ASYNC_FIFO (read side), PULSE_GEN   (÷32 = 115.2 kHz)", 13, INK2)
    s.text(690, 338, "→ UART_RX   (÷1 at prescale 32 = 3.6864 MHz, i.e. 32× oversampling)", 13, INK2)

    s.box(290, 410, 170, 56, "CLKDIV_MUX", T_VIOLET, VIOLET, 14, "one-hot → ratio")
    s.line([(375, 410), (375, 361)], VIOLET, 1.8)
    s.text(385, 392, "ratio", 11, INK2)
    s.text(20, 443, "REG2[7:2] prescale", 12, VIOLET, weight="bold")
    s.line([(165, 438), (290, 438)], VIOLET, 1.8)
    s.text(480, 443, "100000 → 1     010000 → 2     001000 → 4     000100 → 8     other → 1", 12, INK2)

    s.rect(15, 500, 1170, 185, T_GREY, "#c9c8c3", 1, 12)
    s.text(30, 527, "Reset network:  asynchronous assert, synchronous de-assert (one synchronizer per domain)", 15, INK, weight="bold")
    s.pill(35, 565, 110, 40, "RST (async)", "#ffffff", RED)
    for i, (lbl, clk, col, x0) in enumerate([("RST_SYNC_1", "REF_CLK", BLUE, 300), ("RST_SYNC_2", "UART_CLK", ORANGE, 300)]):
        y0 = 548 + i * 62
        s.line([(145, 585), (200, 585), (200, y0 + 22), (x0, y0 + 22)], RED, 1.5)
        s.box(x0, y0, 70, 44, "FF", "#ffffff", col, 13, "D = 1")
        s.box(x0 + 130, y0, 70, 44, "FF", "#ffffff", col, 13)
        s.line([(x0 + 70, y0 + 22), (x0 + 130, y0 + 22)], col)
        s.line([(x0 + 200, y0 + 22), (x0 + 330, y0 + 22)], col, 2)
        s.text(x0 + 100, y0 - 4, lbl + "  (" + clk + ")", 11, INK2, "middle")
        s.text(x0 + 340, y0 + 27, "SYNC_RST → " + ("REF-domain flops" if i == 0 else "UART-domain flops"), 12.5, INK2)
    s.text(1000, 592, "RST low resets both domains at once;", 11.5, INK2, "middle", italic=True)
    s.text(1000, 607, "release is aligned to each domain's own clock", 11.5, INK2, "middle", italic=True)
    s.text(1000, 622, "(≈ 0.54 µs in the UART domain)", 11.5, INK2, "middle", italic=True)
    s.save(OUT + "clocks_resets.svg")


# ---------------------------------------------------------------- 3. async fifo
def fifo():
    s = Svg(1200, 540, "Asynchronous FIFO internals")
    s.rect(15, 50, 450, 460, T_BLUE, BLUE, 1.5, 14)
    s.rect(735, 50, 450, 460, T_ORANGE, ORANGE, 1.5, 14)
    s.text(32, 76, "Write side — REF_CLK", 15, BLUE, weight="bold")
    s.text(1168, 76, "Read side — TX_CLK", 15, ORANGE, "end", "bold")

    s.box(35, 110, 120, 60, "W_INC", "#ffffff", BLUE, 14, "from SYS_CTRL")
    s.line([(155, 140), (200, 140)], BLUE)
    s.box(200, 105, 245, 90, "FIFO_WR", "#ffffff", BLUE, 15, ["4-bit binary + Gray wptr", "waddr = wptr[2:0]"])
    s.box(35, 400, 305, 80, "wfull  →  FIFO_FULL", "#ffffff", RED, 15,
          "wptr == { ~wq2_rptr[3:2], wq2_rptr[1:0] }")

    s.rect(485, 105, 230, 270, T_AQUA, AQUA, 1.5, 8)
    s.text(600, 130, "FIFO_MEM_CNTRL", 15, INK, "middle", "bold")
    for i in range(8):
        s.rect(515, 145 + i * 26, 170, 22, "#ffffff", AQUA, 1, 3)
        s.text(525, 161 + i * 26, f"[{i}]", 11, INK2)
        s.text(675, 161 + i * 26, "8 bits", 11, MUTED, "end")
    s.text(600, 395, "8 × 8 dual-port RAM · no reset · async read", 12, INK2, "middle")
    s.line([(445, 150), (485, 150)], BLUE, 1.8)
    s.text(465, 138, "waddr", 10.5, INK2, "middle")
    s.line([(485, 175), (445, 175)], BLUE, 0, arrow=False)
    s.line([(735, 150), (715, 150)], ORANGE, 1.8)
    s.line([(715, 200), (735, 200)], ORANGE, 1.8)
    s.text(725, 140, "raddr", 10.5, INK2, "middle")
    s.text(725, 218, "RD_DATA", 10.5, INK2, "middle")
    s.text(465, 160, "WR_DATA", 10.5, INK2, "middle")

    s.box(755, 105, 245, 90, "FIFO_RD", "#ffffff", ORANGE, 15, ["4-bit binary + Gray rptr", "raddr = rptr[2:0]"])
    s.box(1045, 110, 125, 60, "R_INC", "#ffffff", ORANGE, 14, "from PULSE_GEN")
    s.line([(1045, 140), (1000, 140)], ORANGE)
    s.box(860, 400, 310, 80, "rempty  →  F_EMPTY", "#ffffff", RED, 15, "rptr == rq2_wptr")

    s.box(485, 430, 230, 70, "DF_SYNC × 2", T_VIOLET, VIOLET, 15, "2-flop synchronizer per pointer", sw=2.5)
    # wptr gray -> read side
    s.line([(380, 195), (380, 450), (485, 450)], BLUE, 2)
    s.text(388, 300, "wptr_gray", 11, INK2)
    s.line([(715, 480), (840, 480), (840, 445), (860, 445)], BLUE, 2)
    s.text(790, 497, "rq2_wptr", 10.5, INK2, "middle")
    # rptr gray -> write side
    s.line([(820, 195), (820, 450), (715, 450)], ORANGE, 2)
    s.text(828, 300, "rptr_gray", 11, INK2)
    s.line([(485, 480), (360, 480), (360, 455), (340, 455)], ORANGE, 2)
    s.text(410, 497, "wq2_rptr", 10.5, INK2, "middle")
    s.text(600, 527, "Gray code: only one bit changes per step, so a pointer sampled mid-change is never garbage", 12, VIOLET, "middle", italic=True)
    s.save(OUT + "async_fifo.svg")


if __name__ == "__main__":
    datapath()
    clocking()
    fifo()
