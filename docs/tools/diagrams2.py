"""UART frame, SYS_CTRL FSM paths, command examples, register map, design flow. Run: python3 docs/tools/diagrams2.py"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "generated") + os.sep
os.makedirs(OUT, exist_ok=True)



# ---------------------------------------------------------------- UART frame
def uart_frame():
    s = Svg(1200, 560, "UART frame and receiver sampling")
    s.text(20, 28, "Frame for 0x55 with even parity  (data sent LSB first, 11 bit-times)", 16, INK, weight="bold")

    cw = 80
    x0 = 120
    hi, lo = 90, 150
    bits = [("START", 0), ("D0", 1), ("D1", 0), ("D2", 1), ("D3", 0), ("D4", 1), ("D5", 0), ("D6", 1),
            ("D7", 0), ("PAR", 0), ("STOP", 1)]
    # idle before
    pts = [(40, hi)]
    level = hi
    x = x0
    pts.append((x, hi))
    for name, b in bits:
        y = hi if b else lo
        pts.append((x, y))
        pts.append((x + cw, y))
        x += cw
    pts.append((x, hi))
    pts.append((x + 60, hi))
    # fix duplicate verticals: path handles it
    # cell shading + labels
    for i, (name, b) in enumerate(bits):
        cx = x0 + i * cw
        col = {"START": T_ORANGE, "PAR": T_YELLOW, "STOP": T_AQUA}.get(name, T_BLUE)
        s.rect(cx, 62, cw, 130, col, "none", 0, 0, opacity=0.9)
    for i in range(12):
        s.line([(x0 + i * cw, 62), (x0 + i * cw, 192)], "#c9c8c3", 1, "3 3", arrow=False)
    s.line(pts, INK, 2.6, arrow=False)
    for i, (name, b) in enumerate(bits):
        cx = x0 + i * cw + cw / 2
        s.text(cx, 56, name, 12.5, INK, "middle", "bold")
        s.text(cx, 213, str(b), 13, INK2, "middle")
    s.text(30, 94, "1", 12, INK2)
    s.text(30, 154, "0", 12, INK2)
    s.text(40, 82, "idle", 11, INK2)
    s.text(x0 + 11 * cw + 8, 82, "idle", 11, INK2)
    # bracket for data
    s.line([(x0 + cw, 235), (x0 + 9 * cw, 235)], VIOLET, 1.8, arrow=True, arrow_start=True)
    s.text(x0 + 5 * cw, 254, "8 data bits, LSB first   (0x55 = 0101 0101  →  1 0 1 0 1 0 1 0 on the wire)", 12.5, VIOLET, "middle", "bold")
    s.text(x0 + 9 * cw + 20, 232, "REG2[0] = 1: parity bit present", 11, INK2)
    s.text(x0 + 9 * cw + 20, 248, "REG2[1] = 0: even  (PAR = ^data)", 11, INK2)
    s.text(1168, 213, "1 bit = 8.68 µs @ 115 200 baud", 11.5, INK2, "end", italic=True)

    # ---------------- zoom on one bit
    s.rect(15, 290, 1170, 255, T_GREY, "#c9c8c3", 1, 12)
    s.text(30, 316, "Inside one bit: the receiver counts 32 RX_CLK edges (prescale = 32) and takes a 3-sample majority around the middle", 14.5, INK, weight="bold")
    tw = 33
    tx0 = 60
    ty = 410
    for i in range(32):
        x = tx0 + i * tw
        col = BLUE if i in (15, 16, 17) else "#ffffff"
        stroke = BLUE if i in (15, 16, 17) else INK2
        if i == 18:
            col, stroke = YELLOW, YELLOW
        if i == 31:
            col, stroke = T_ORANGE, ORANGE
        s.rect(x, ty, tw - 3, 34, col, stroke, 1.4, 4)
        s.text(x + (tw - 3) / 2, ty + 22, str(i), 11, "#ffffff" if i in (15, 16, 17) else INK, "middle", "bold" if i in (15, 16, 17, 18, 31) else "normal")
    s.text(tx0, ty - 12, "edge_cnt  →", 11.5, INK2)
    # callouts
    def callout(i, y2, txt, sub, col):
        x = tx0 + i * tw + (tw - 3) / 2
        s.line([(x, ty + 34), (x, y2 - 18)], col, 1.5, arrow=False)
        return x
    cx = tx0 + 16 * tw + (tw - 3) / 2
    s.line([(tx0 + 15 * tw, ty + 40), (tx0 + 17 * tw + tw - 3, ty + 40)], BLUE, 2.2, arrow=False)
    s.line([(cx, ty + 40), (cx, ty + 62)], BLUE, 1.5, arrow=False)
    s.text(cx, ty + 78, "edges 15, 16, 17  (middle−1, middle, middle+1)", 12, BLUE, "middle", "bold")
    s.text(cx, ty + 94, "dat_samp_en high: three RX_IN samples go into majority_reg", 11.5, INK2, "middle")
    c18 = tx0 + 18 * tw + (tw - 3) / 2 + 150
    s.line([(tx0 + 18 * tw + (tw - 3) / 2, ty + 38), (tx0 + 18 * tw + (tw - 3) / 2, ty + 62), (c18 + 25, ty + 62)], YELLOW, 1.5, arrow=False)
    s.text(c18 + 32, ty + 66, "edge 18  (middle+2)", 12, "#9a6a00", weight="bold")
    s.text(c18 + 32, ty + 82, "sampled_bit = majority; start / parity / stop checks fire", 11.5, INK2)
    c31 = tx0 + 31 * tw + (tw - 3) / 2
    s.line([(c31, ty - 4), (c31, ty - 28), (c31 - 70, ty - 28)], ORANGE, 1.5, arrow=False)
    s.text(c31 - 76, ty - 24, "edge 31 = prescale−1: next bit (bit_cnt + 1)", 11.5, "#b3441a", "end", "bold")
    s.text(tx0, 342, "RX_CLK = UART_CLK ÷ 1 = 3.6864 MHz  →  32 edges per bit at 115 200 baud", 12.5, INK2)
    s.text(tx0, 360, "A start-bit glitch (start check fails) returns the FSM to idle; data_valid is raised in the stop state when no parity / stop error was seen.", 12, INK2)
    s.save(OUT + "uart_frame.svg")


# ---------------------------------------------------------------- SYS_CTRL FSM paths
def fsm_paths():
    s = Svg(1290, 530, "SYS_CTRL state sequence per command")
    s.text(20, 30, "SYS_CTRL — state sequence for each opcode  (REF_CLK domain, 14 states)", 16, INK, weight="bold")
    cat = {
        "IDLE": (T_GREY, INK2), "FRAME1": (T_BLUE, BLUE), "FRAME2": (T_BLUE, BLUE), "FRAME3": (T_BLUE, BLUE),
        "RF_WRITE": (T_AQUA, AQUA), "RF_READ_REQ": (T_AQUA, AQUA), "RF_READ_WAIT": (T_AQUA, AQUA),
        "RF_READ_SEND": (T_VIOLET, VIOLET),
        "ALU_WR_A": (T_YELLOW, YELLOW), "ALU_WR_B": (T_YELLOW, YELLOW), "ALU_EXEC": (T_YELLOW, YELLOW),
        "ALU_WAIT": (T_YELLOW, YELLOW), "ALU_SEND_LSB": (T_VIOLET, VIOLET), "ALU_SEND_MSB": (T_VIOLET, VIOLET),
    }
    code = {"IDLE": 0, "FRAME1": 1, "FRAME2": 2, "FRAME3": 3, "RF_WRITE": 4, "RF_READ_REQ": 5, "RF_READ_WAIT": 6,
            "RF_READ_SEND": 7, "ALU_WR_A": 8, "ALU_WR_B": 9, "ALU_EXEC": 10, "ALU_WAIT": 11,
            "ALU_SEND_LSB": 12, "ALU_SEND_MSB": 13}
    note = {"FRAME1": "", "RF_READ_WAIT": "RdData_VLD", "ALU_WAIT": "OUT_Valid",
            "RF_READ_SEND": "!FIFO_FULL", "ALU_SEND_LSB": "!FIFO_FULL", "ALU_SEND_MSB": "!FIFO_FULL",
            "ALU_EXEC": "EN + CLK_EN", "RF_WRITE": "WrEn pulse", "RF_READ_REQ": "RdEn pulse",
            "ALU_WR_A": "A → REG0", "ALU_WR_B": "B → REG1"}
    lanes = [
        ("0xAA", "RF write", ["IDLE", "FRAME1", "FRAME2", "RF_WRITE"], "no response"),
        ("0xBB", "RF read", ["IDLE", "FRAME1", "RF_READ_REQ", "RF_READ_WAIT", "RF_READ_SEND"], "1 byte"),
        ("0xCC", "ALU + operands", ["IDLE", "FRAME1", "FRAME2", "FRAME3", "ALU_WR_A", "ALU_WR_B", "ALU_EXEC",
                                    "ALU_WAIT", "ALU_SEND_LSB", "ALU_SEND_MSB"], "2 bytes"),
        ("0xDD", "ALU, stored operands", ["IDLE", "FRAME1", "ALU_EXEC", "ALU_WAIT", "ALU_SEND_LSB", "ALU_SEND_MSB"], "2 bytes"),
    ]
    bw, bh, pitch = 92, 54, 102
    x0 = 160
    for li, (op, name, seq, resp) in enumerate(lanes):
        y = 75 + li * 100
        s.text(20, y + 24, op, 18, INK, weight="bold")
        s.text(20, y + 42, name, 12, INK2)
        for i, st in enumerate(seq):
            x = x0 + i * pitch
            fill, stroke = cat[st]
            s.rect(x, y, bw, bh, fill, stroke, 1.8, 10)
            s.text(x + bw / 2, y + 22, st.replace("_", "_​"), 11.5 if len(st) > 10 else 12.5, INK, "middle", "bold")
            s.text(x + bw / 2, y + 40, f"state {code[st]}", 10.5, INK2, "middle")
            if st in note and note[st]:
                s.text(x + bw / 2, y + bh + 14, note[st], 10.5, INK2, "middle", italic=True)
            if i < len(seq) - 1:
                s.line([(x + bw, y + bh / 2), (x + pitch, y + bh / 2)], INK2, 1.8)
        xe = x0 + (len(seq) - 1) * pitch + bw
        s.line([(xe, y + bh / 2), (xe + 28, y + bh / 2)], INK2, 1.8, "4 3")
        s.text(xe + 34, y + bh / 2 + 4, "→ IDLE", 12, INK2)
        s.text(xe + 34, y + bh / 2 + 20, "(" + resp + ")", 11, MUTED, italic=True)
    # legend
    lx = 20
    ly = 470
    for lbl, (fill, stroke) in [("opcode / operand capture", (T_BLUE, BLUE)), ("register-file access", (T_AQUA, AQUA)),
                                ("ALU control", (T_YELLOW, YELLOW)), ("push response to FIFO", (T_VIOLET, VIOLET))]:
        s.rect(lx, ly, 22, 16, fill, stroke, 1.6, 4)
        s.text(lx + 30, ly + 13, lbl, 12, INK2)
        lx += 250
    s.text(20, ly + 42, "IDLE → FRAME1 when a valid RX byte arrives (opcode is latched); an unknown opcode returns straight to IDLE.", 11.5, INK2, italic=True)
    s.save(OUT + "sysctrl_fsm_paths.svg")


# ---------------------------------------------------------------- command timelines
def commands():
    s = Svg(1200, 600, "Example transactions on RX_IN and TX_OUT")
    s.text(20, 30, "What goes in and what comes out  (each box = one 11-bit UART frame)", 16, INK, weight="bold")
    fw, pitch = 70, 78
    x0 = 235
    cmds = [
        ("0xAA", "RF write", [("AA", "opcode", T_VIOLET, VIOLET), ("05", "address", T_BLUE, BLUE), ("55", "data", T_BLUE, BLUE)], [],
         "RegFile[5] ← 0x55"),
        ("0xBB", "RF read", [("BB", "opcode", T_VIOLET, VIOLET), ("05", "address", T_BLUE, BLUE)],
         [("55", "data", T_ORANGE, ORANGE)], "reads RegFile[5]"),
        ("0xCC", "ALU + operands", [("CC", "opcode", T_VIOLET, VIOLET), ("20", "A", T_BLUE, BLUE), ("05", "B", T_BLUE, BLUE),
                                    ("00", "ALU_FUN = ADD", T_BLUE, BLUE)],
         [("25", "LSB", T_ORANGE, ORANGE), ("00", "MSB", T_ORANGE, ORANGE)], "0x20 + 0x05 = 0x0025"),
        ("0xDD", "ALU, stored A/B", [("DD", "opcode", T_VIOLET, VIOLET), ("01", "ALU_FUN = SUB", T_BLUE, BLUE)],
         [("1B", "LSB", T_ORANGE, ORANGE), ("00", "MSB", T_ORANGE, ORANGE)], "0x20 − 0x05 = 0x001B"),
        ("0xCC", "ALU + operands", [("CC", "opcode", T_VIOLET, VIOLET), ("12", "A", T_BLUE, BLUE), ("10", "B", T_BLUE, BLUE),
                                    ("02", "ALU_FUN = MUL", T_BLUE, BLUE)],
         [("20", "LSB", T_ORANGE, ORANGE), ("01", "MSB", T_ORANGE, ORANGE)], "0x12 × 0x10 = 0x0120"),
    ]
    s.text(x0, 62, "RX_IN   (host → chip)", 12.5, BLUE, weight="bold")
    s.text(x0 + 4 * pitch + 55, 62, "TX_OUT   (chip → host)", 12.5, ORANGE, weight="bold")
    for ci, (op, name, rx, tx, result) in enumerate(cmds):
        y = 80 + ci * 100
        s.rect(15, y - 8, 1170, 92, T_GREY if ci % 2 == 0 else "#ffffff", "none", 0, 8)
        s.text(25, y + 24, op, 18, INK, weight="bold")
        s.text(25, y + 44, name, 12, INK2)
        s.text(25, y + 62, f"TC{ci + 1}" if ci < 4 else "TC5", 11, MUTED, italic=True)
        for i, (v, role, fill, stroke) in enumerate(rx):
            x = x0 + i * pitch
            s.rect(x, y, fw, 40, fill, stroke, 1.8, 8)
            s.text(x + fw / 2, y + 26, v, 17, INK, "middle", "bold", family="Menlo, Consolas, monospace")
            s.text(x + fw / 2, y + 58, role, 10.5, INK2, "middle")
        tx_start = x0 + 4 * pitch + 55
        if tx:
            s.line([(x0 + len(rx) * pitch, y + 20), (tx_start - 8, y + 20)], MUTED, 1.4, "3 3")
            for i, (v, role, fill, stroke) in enumerate(tx):
                x = tx_start + i * pitch
                s.rect(x, y, fw, 40, fill, stroke, 1.8, 8)
                s.text(x + fw / 2, y + 26, v, 17, INK, "middle", "bold", family="Menlo, Consolas, monospace")
                s.text(x + fw / 2, y + 58, role, 10.5, INK2, "middle")
        else:
            s.text(tx_start, y + 26, "no response", 13, MUTED, italic=True)
        s.text(1175, y + 26, result, 13, INK, "end", "bold")
    s.text(20, 592, "Opcode frame first; ALU results always return LSB first. 0xDD reuses the REG0 / REG1 left behind by the previous 0xCC (TC3 → TC4).", 11.5, INK2, italic=True)
    s.save(OUT + "command_examples.svg")


# ---------------------------------------------------------------- register map
def regmap():
    s = Svg(1100, 560, "Register file map")
    s.text(20, 30, "Register file — 16 × 8, address[3:0]", 16, INK, weight="bold")
    cols = [(20, "Address"), (120, "Name"), (230, "Reset"), (330, "Purpose")]
    s.rect(15, 48, 1070, 30, "#2a2a28", "none", 0, 6)
    for x, t in cols:
        s.text(x + 8, 68, t, 13, "#ffffff", weight="bold")
    rows = [
        ("0x0", "REG0", "0x00", "ALU operand A", T_YELLOW),
        ("0x1", "REG1", "0x00", "ALU operand B", T_YELLOW),
        ("0x2", "REG2", "0x81", "UART configuration  (parity enable, parity type, prescale)", T_VIOLET),
        ("0x3", "REG3", "0x20", "TX clock divider ratio  (÷32 → 115 200 baud)", T_VIOLET),
        ("0x4 – 0xF", "general purpose", "0x00", "free storage (TB uses 0x5)", T_AQUA),
    ]
    for i, (a, n, r, p, fill) in enumerate(rows):
        y = 84 + i * 36
        s.rect(15, y, 1070, 32, fill, "none", 0, 4)
        s.text(28, y + 21, a, 13, INK, weight="bold", family="Menlo, Consolas, monospace")
        s.text(128, y + 21, n, 13, INK, weight="bold")
        s.text(238, y + 21, r, 13, INK, family="Menlo, Consolas, monospace")
        s.text(338, y + 21, p, 13, INK2)

    # bit fields
    def strip(y, title, fields):
        s.text(20, y - 12, title, 14, INK, weight="bold")
        cw = 118
        x = 140
        for b in range(7, -1, -1):
            s.text(x + (7 - b) * cw + cw / 2, y + 6, f"bit {b}", 10.5, MUTED, "middle")
        for (hi_b, lo_b, label, sub, fill, stroke) in fields:
            xs = 140 + (7 - hi_b) * cw
            w = (hi_b - lo_b + 1) * cw
            s.rect(xs, y + 12, w - 4, 62, fill, stroke, 1.8, 8)
            s.text(xs + (w - 4) / 2, y + 40, label, 13.5, INK, "middle", "bold")
            s.text(xs + (w - 4) / 2, y + 60, sub, 11, INK2, "middle")

    strip(330, "REG2 = 0x81 at reset", [
        (7, 2, "prescale [7:2]", "one-hot, default 100000 = 32 (RX oversampling)", T_BLUE, BLUE),
        (1, 1, "parity type", "0 even · 1 odd", T_YELLOW, YELLOW),
        (0, 0, "parity enable", "1 = parity on", T_AQUA, AQUA),
    ])
    strip(450, "REG3 = 0x20 at reset", [
        (7, 0, "divider ratio [7:0]", "TX_CLK = UART_CLK ÷ REG3  (0x20 = 32 → 115.2 kHz)", T_BLUE, BLUE),
    ])
    s.save(OUT + "register_map.svg")


# ---------------------------------------------------------------- backend flow
def flow():
    s = Svg(1240, 470, "Design and verification flow")
    s.text(20, 30, "From RTL to verified netlist", 16, INK, weight="bold")

    def stage(x, y, w, title, tool, result, ok=True, dashed=False):
        s.rect(x, y, w, 76, "#ffffff", AQUA if ok and not dashed else MUTED, 2, 12, "6 4" if dashed else None)
        s.text(x + 14, y + 24, title, 14.5, INK, weight="bold")
        s.text(x + 14, y + 43, tool, 11, INK2)
        s.text(x + 14, y + 63, result, 12, GREEN if ok and not dashed else MUTED, weight="bold")

    s.box(20, 170, 130, 120, "RTL", T_BLUE, BLUE, 20, ["31 Verilog / SV", "files"])
    # rows
    rows = [70, 160, 250, 340]
    # Track A
    stage(250, rows[0], 300, "Functional simulation", "ModelSim · SYS_TB.sv", "5 / 5 test cases pass")
    stage(250, rows[1], 300, "Lint + CDC sign-off", "SpyGlass L-2016.06 · 7 goals", "0 unsynchronized crossings")
    stage(250, rows[2], 300, "Logic synthesis", "Design Compiler O-2018.06-SP1", "19 918 area · 0.227 mW · no violations")
    stage(250, rows[3], 300, "Scan insertion (DFT)", "DC · 4 mux-D scan chains", "99.48 % fault coverage")
    for y in rows[:3]:
        s.line([(150, 230), (200, 230), (200, y + 38), (250, y + 38)], INK2, 1.8)
    s.line([(400, rows[2] + 76), (400, rows[3])], INK2, 1.8)
    stage(660, rows[2], 330, "Formality: RTL vs gate netlist", "Formality L-2016.03-SP1", "358 / 358 compare points pass")
    stage(660, rows[3], 330, "Formality: RTL vs scan netlist", "test_mode = 0, SE = 0", "358 / 358 compare points pass")
    s.line([(550, rows[2] + 38), (660, rows[2] + 38)], INK2, 1.8)
    s.line([(550, rows[3] + 38), (660, rows[3] + 38)], INK2, 1.8)
    stage(1060, rows[3], 160, "Post-PnR", "template only", "not run", dashed=True)
    s.line([(990, rows[3] + 38), (1060, rows[3] + 38)], MUTED, 1.4, "4 3")
    s.text(660, 440, "Netlists, SDC / SDF, reports and logs for every step are kept under Backend/.", 12, INK2, italic=True)
    s.save(OUT + "design_flow.svg")


if __name__ == "__main__":
    uart_frame()
    fsm_paths()
    commands()
    regmap()
    flow()
