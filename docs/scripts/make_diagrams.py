#!/usr/bin/env python3
"""Regenerates every diagram/chart in docs/images/generated/.

Requirements: Graphviz (`dot` on PATH), Python 3 with matplotlib.
Usage (from the repository root):   python3 docs/scripts/make_diagrams.py

All numbers used in the charts come from the reports in Backend/ and Results/
(see the README for the sources).  Structural diagrams mirror the RTL in RTL/.
"""
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "images" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------- palette
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e4e3de"
BLUE, ORANGE, AQUA, VIOLET, RED, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948", "#9a998f"
T_BLUE, T_ORANGE, T_AQUA, T_VIOLET, T_GREY = "#dbe8f8", "#fbe0d5", "#d3f0e5", "#dedaf3", "#ececE8"

plt.rcParams.update({
    "svg.fonttype": "path",
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK2,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "text.color": INK,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def dot(name, src):
    p = OUT / f"{name}.dot"
    p.write_text(src)
    subprocess.run(["dot", "-Tsvg", str(p), "-o", str(OUT / f"{name}.svg")], check=True)
    p.unlink()


GV_HEAD = f'''
graph [bgcolor="{SURFACE}", fontname="Helvetica", fontsize=12, pad=0.25];
node  [fontname="Helvetica", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="{INK2}", penwidth=1.2];
edge  [fontname="Helvetica", fontsize=9, color="{INK2}", fontcolor="{INK2}", arrowsize=0.7];
'''

# ================================================================ 1. clocks / CDC
dot("clock_domains", f'''digraph G {{
{GV_HEAD}
rankdir=LR; compound=true; nodesep=0.35; ranksep=0.9;
subgraph cluster_ref {{
  label=<<b>REF_CLK domain — 50 MHz</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_BLUE}"; color="{BLUE}"; penwidth=1.5;
  RST1  [label="RST_SYNC_1\\n(2-flop, async assert /\\nsync de-assert)"];
  SC    [label=<<b>SYS_CTRL</b><br/>14-state FSM>];
  RF    [label=<<b>RegFile</b><br/>16 × 8>];
  GATE  [label="CLK_GATE\\n(latch + AND)"];
  ALU   [label=<<b>ALU</b><br/>ALU_CLK (gated)>, fillcolor="{T_AQUA}"];
  DS    [label="DATA_SYNC\\n(2-flop + edge pulse)"];
  FW    [label="ASYNC_FIFO\\nwrite side"];
}}
subgraph cluster_uart {{
  label=<<b>UART_CLK domain — 3.6864 MHz</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_ORANGE}"; color="{ORANGE}"; penwidth=1.5;
  RST2  [label="RST_SYNC_2\\n(2-flop, async assert /\\nsync de-assert)"];
  MUX   [label="CLKDIV_MUX\\nprescale → RX ratio"];
  DIVR  [label="ClkDiv (RX)\\n→ RX_CLK"];
  DIVT  [label="ClkDiv (TX)\\n÷ REG3 → TX_CLK\\n115.2 kHz"];
  RX    [label=<<b>UART_RX</b><br/>RX_CLK>];
  TX    [label=<<b>UART_TX</b><br/>TX_CLK>];
  PG    [label="PULSE_GEN\\nbusy → FIFO_R_INC"];
  FR    [label="ASYNC_FIFO\\nread side"];
}}
RXIN  [shape=plaintext, style="", label="RX_IN"];
TXOUT [shape=plaintext, style="", label="TX_OUT"];
RSTIN [shape=plaintext, style="", label="RST (async)"];

RXIN -> RX; TX -> TXOUT;
RSTIN -> RST1 [style=dashed]; RSTIN -> RST2 [style=dashed];
SC -> RF [label="WrEn/RdEn/Addr/Data"]; RF -> ALU [label="REG0, REG1"]; SC -> ALU [label="EN, FUN"]; ALU -> SC [label="ALU_OUT, OUT_Valid"];
SC -> GATE [label="CLK_EN"]; GATE -> ALU [label="ALU_CLK"];
RX -> DS [color="{RED}", penwidth=2.2, fontcolor="{RED}", label="① RX byte + valid\\nUART → REF"];
DS -> SC;
SC -> FW [label="TX byte + valid"];
FW -> FR [color="{RED}", penwidth=2.2, fontcolor="{RED}", label="② Gray pointers via\\n2-flop DF_SYNC (both ways)", dir=both];
FR -> TX [label="RD_DATA, ~EMPTY"];
TX -> PG [label="busy"]; PG -> FR [label="R_INC"];
RF -> MUX [color="{RED}", style=dashed, penwidth=1.6, fontcolor="{RED}", label="③ REG2 (prescale, parity)\\nquasi-static, no sync"];
RF -> DIVT [color="{RED}", style=dashed, penwidth=1.6, fontcolor="{RED}", label="③ REG3 (ratio)"];
MUX -> DIVR; DIVR -> RX [label="RX_CLK"]; DIVT -> TX [label="TX_CLK"];
}}''')

# ================================================================ 2. SYS_CTRL FSM
def sc_node(n, code, c="white"):
    return f'{n} [label=<<b>{n}</b><br/><font point-size="9">code {code}</font>>, fillcolor="{c}"];'

dot("sys_ctrl_fsm", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.28; ranksep=0.55;
{sc_node("S_IDLE",0,T_GREY)}
{sc_node("S_FRAME1",1,T_GREY)}
{sc_node("S_FRAME2",2,T_GREY)}
{sc_node("S_FRAME3",3,T_GREY)}
{sc_node("S_RF_WRITE",4,T_BLUE)}
{sc_node("S_RF_READ_REQ",5,T_AQUA)}
{sc_node("S_RF_READ_WAIT",6,T_AQUA)}
{sc_node("S_RF_READ_SEND",7,T_AQUA)}
{sc_node("S_ALU_WR_A",8,T_ORANGE)}
{sc_node("S_ALU_WR_B",9,T_ORANGE)}
{sc_node("S_ALU_EXEC",10,T_ORANGE)}
{sc_node("S_ALU_WAIT",11,T_ORANGE)}
{sc_node("S_ALU_SEND_LSB",12,T_ORANGE)}
{sc_node("S_ALU_SEND_MSB",13,T_ORANGE)}

S_IDLE -> S_FRAME1 [label="RX_D_VLD\\n(opcode latched)"];
S_FRAME1 -> S_FRAME2 [label="RX_D_VLD & opcode∈{AA, CC}"];
S_FRAME1 -> S_RF_READ_REQ [label="RX_D_VLD & BB", color="{AQUA}", fontcolor="{AQUA}"];
S_FRAME1 -> S_ALU_EXEC [label="RX_D_VLD & DD", color="{ORANGE}", fontcolor="{ORANGE}"];
S_FRAME1 -> S_IDLE [label="unknown opcode", style=dashed];
S_FRAME2 -> S_RF_WRITE [label="RX_D_VLD & AA", color="{BLUE}", fontcolor="{BLUE}"];
S_FRAME2 -> S_FRAME3 [label="RX_D_VLD & CC", color="{ORANGE}", fontcolor="{ORANGE}"];
S_FRAME3 -> S_ALU_WR_A [label="RX_D_VLD", color="{ORANGE}"];
S_RF_WRITE -> S_IDLE [label="WrEn pulse", color="{BLUE}"];
S_RF_READ_REQ -> S_RF_READ_WAIT [label="RdEn pulse", color="{AQUA}"];
S_RF_READ_WAIT -> S_RF_READ_SEND [label="RdData_Valid", color="{AQUA}"];
S_RF_READ_SEND -> S_IDLE [label="!FIFO_FULL\\nTX_D_VLD pulse", color="{AQUA}"];
S_ALU_WR_A -> S_ALU_WR_B [label="REG0 ← A", color="{ORANGE}"];
S_ALU_WR_B -> S_ALU_EXEC [label="REG1 ← B\\nCLK_EN=1", color="{ORANGE}"];
S_ALU_EXEC -> S_ALU_WAIT [label="EN=1, CLK_EN=1\\nALU_FUN", color="{ORANGE}"];
S_ALU_WAIT -> S_ALU_SEND_LSB [label="OUT_Valid\\nCLK_EN←0", color="{ORANGE}"];
S_ALU_SEND_LSB -> S_ALU_SEND_MSB [label="!FIFO_FULL\\npush ALU_OUT[7:0]", color="{ORANGE}"];
S_ALU_SEND_MSB -> S_IDLE [label="!FIFO_FULL\\npush ALU_OUT[15:8]", color="{ORANGE}"];
}}''')

# ================================================================ 3. UART RX / TX FSMs
dot("uart_rx_fsm", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.5; ranksep=0.7;
idle  [label=<<b>idle</b><br/>000<br/><font point-size="9">soft_rst=1</font>>, fillcolor="{T_GREY}"];
start [label=<<b>start</b><br/>001<br/><font point-size="9">strt_chk_en @ edge_cnt = mid+2</font>>, fillcolor="{T_BLUE}"];
data  [label=<<b>data</b><br/>011<br/><font point-size="9">deser_en @ mid+2</font>>, fillcolor="{T_BLUE}"];
parity[label=<<b>parity</b><br/>010<br/><font point-size="9">par_chk_en @ mid+2</font>>, fillcolor="{T_BLUE}"];
stop  [label=<<b>stop</b><br/>110<br/><font point-size="9">stp_chk_en @ mid+2<br/>data_valid at last edge</font>>, fillcolor="{T_BLUE}"];
valid [label=<<b>valid</b><br/>100<br/><font point-size="9">soft_rst=1</font>>, fillcolor="{T_GREY}"];
idle -> start [label="RX_IN = 0"];
start -> data [label="bit_transition & !strt_glitch"];
start -> idle [label="bit_transition & strt_glitch\\n(glitch → abort)", style=dashed, color="{RED}", fontcolor="{RED}"];
data -> parity [label="bit_cnt==8 & bit_transition & PAR_EN"];
data -> stop [label="bit_cnt==8 & bit_transition & !PAR_EN", constraint=false];
parity -> stop [label="bit_transition"];
stop -> valid [label="bit_transition"];
valid -> idle [label="RX_IN = 1"];
valid -> start [label="RX_IN = 0\\n(back-to-back frame)", constraint=false];
}}''')

dot("uart_tx_fsm", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.5; ranksep=0.8;
idle  [label=<<b>idle</b><br/>000<br/><font point-size="9">muxSel=01 (line high)<br/>regData if dataValid</font>>, fillcolor="{T_GREY}"];
start [label=<<b>start</b><br/>001<br/><font point-size="9">muxSel=00 (drive 0)</font>>, fillcolor="{T_ORANGE}"];
data  [label=<<b>data</b><br/>011<br/><font point-size="9">muxSel=10, serEn=1</font>>, fillcolor="{T_ORANGE}"];
parity[label=<<b>parity</b><br/>010<br/><font point-size="9">muxSel=11</font>>, fillcolor="{T_ORANGE}"];
stop  [label=<<b>stop</b><br/>110<br/><font point-size="9">muxSel=01 (drive 1)<br/>regData if dataValid</font>>, fillcolor="{T_ORANGE}"];
idle -> start [label="dataValid (~FIFO_EMPTY)"];
start -> data [label="always"];
data -> parity [label="serDone & parEn"];
data -> stop [label="serDone & !parEn", constraint=false];
parity -> stop [label="always"];
stop -> idle [label="always"];
}}''')

# ================================================================ 4. async FIFO
dot("async_fifo", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.45; ranksep=0.8; compound=true;
subgraph cluster_w {{
  label=<<b>Write domain — REF_CLK</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_BLUE}"; color="{BLUE}"; penwidth=1.5;
  WR [label=<<b>FIFO_WR</b><br/>binary wptr (4b) → Gray<br/>wfull = wptr == {{~wq2_rptr[3:2], wq2_rptr[1:0]}}>];
  SCI [shape=plaintext, style="", label="SYS_CTRL\\nTX_P_DATA, TX_D_VLD\\nFIFO_FULL"];
}}
subgraph cluster_m {{
  label=<<b>FIFO_MEM_CNTRL</b>>; labeljust=l; style="rounded,filled"; fillcolor="white"; color="{INK2}";
  MEM [label="8 × 8 memory\\nwrite: waddr[2:0] @ REF_CLK\\nread: raddr[2:0] (combinational)\\nno reset"];
}}
subgraph cluster_r {{
  label=<<b>Read domain — TX_CLK</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_ORANGE}"; color="{ORANGE}"; penwidth=1.5;
  RD [label=<<b>FIFO_RD</b><br/>binary rptr (4b) → Gray<br/>rempty = rptr == rq2_wptr>];
  TXI [shape=plaintext, style="", label="UART_TX\\nRD_DATA, ~EMPTY\\nPULSE_GEN → R_INC"];
}}
SCI -> WR [label="W_INC, WR_DATA"];
WR -> MEM [label="waddr, w_en & ~full"];
RD -> MEM [label="raddr", dir=back];
MEM -> TXI [label="RD_DATA"];
RD -> TXI [label="EMPTY"];
TXI -> RD [label="R_INC", constraint=false];
WR -> RD [color="{RED}", penwidth=2.2, fontcolor="{RED}", label="wptr_gray → DF_SYNC (2 flops, TX_CLK) → rq2_wptr", constraint=false];
RD -> WR [color="{RED}", penwidth=2.2, fontcolor="{RED}", label="rptr_gray → DF_SYNC (2 flops, REF_CLK) → wq2_rptr", constraint=false];
}}''')

# ================================================================ 5. UART internals
dot("uart_internals", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.35; ranksep=0.65; compound=true;
subgraph cluster_rx {{
  label=<<b>UART_RX_TOP (RX_CLK)</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_BLUE}"; color="{BLUE}"; penwidth=1.5;
  RXFSM [label=<<b>UART_RX_FSM</b>>];
  EBC   [label=<<b>edge_bit_counter</b><br/>edge_cnt (5b), bit_cnt (4b)>];
  DS    [label=<<b>data_sampling</b><br/>3-sample majority<br/>at mid−1, mid, mid+1>];
  DES   [label=<<b>deserializer</b><br/>shift into P_DATA>];
  SC    [label=<strt_Check<br/>sampled_bit == 0>];
  PC    [label=<parity_Check<br/>recompute vs sampled>];
  STC   [label=<stop_Check<br/>sampled_bit == 1>];
}}
subgraph cluster_tx {{
  label=<<b>UART_TX_TOP (TX_CLK)</b>>; labeljust=l; style="rounded,filled"; fillcolor="{T_ORANGE}"; color="{ORANGE}"; penwidth=1.5;
  TXFSM [label=<<b>UART_TX_FSM</b>>];
  SER   [label=<<b>Serializer</b><br/>pDataReg + 4-bit counter<br/>serDone @ counter == 7>];
  PAR   [label=<<b>parity_Calc</b><br/>even: ^data / odd: ~^data>];
  MUX   [label=<<b>Mux_4X1</b><br/>00 start · 01 stop/idle<br/>10 data · 11 parity>];
}}
RXIN [shape=plaintext, style="", label="RX_IN"]; RXOUT [shape=plaintext, style="", label="P_DATA, data_valid\\nparity_error, stop_error"];
TXIN [shape=plaintext, style="", label="P_DATA, Data_Valid"]; TXOUT [shape=plaintext, style="", label="TX_OUT, busy"];
REG  [shape=plaintext, style="", label="REG2 → PAR_EN, PAR_TYP, Prescale"];
RXIN -> DS; RXIN -> RXFSM;
RXFSM -> EBC [label="edge_bit_cnt_enable\\nsoft_rst"]; EBC -> RXFSM [label="edge_cnt, bit_cnt"];
RXFSM -> DS [label="dat_samp_en"];
DS -> DES [label="sampled_bit"]; DS -> SC; DS -> PC; DS -> STC;
RXFSM -> DES [label="deser_en"]; RXFSM -> SC [label="strt_chk_en"]; RXFSM -> PC [label="par_chk_en"]; RXFSM -> STC [label="stp_chk_en"];
SC -> RXFSM [label="strt_glitch"]; PC -> RXFSM [label="par_err"]; STC -> RXFSM [label="stp_err"];
DES -> RXOUT; RXFSM -> RXOUT;
REG -> RXFSM [style=dashed]; REG -> TXFSM [style=dashed]; REG -> PAR [style=dashed];
TXIN -> SER [label="pData"]; TXIN -> PAR; TXIN -> TXFSM [label="dataValid"];
TXFSM -> SER [label="regData, serEn"]; SER -> TXFSM [label="serDone"];
SER -> MUX [label="serData"]; PAR -> MUX [label="parity bit"]; TXFSM -> MUX [label="muxSel"];
MUX -> TXOUT; TXFSM -> TXOUT [label="busy"];
}}''')

# ================================================================ 6. backend flow
dot("backend_flow", f'''digraph G {{
{GV_HEAD}
rankdir=LR; nodesep=0.35; ranksep=0.55;
RTL   [label=<<b>RTL</b><br/>RTL/ (Verilog + SV)>, fillcolor="{T_GREY}"];
SIM   [label=<<b>ModelSim</b><br/>TB/SYS_TB.sv<br/>5/5 test cases pass>, fillcolor="{T_AQUA}"];
SPY   [label=<<b>SpyGlass</b><br/>lint + CDC (7 goals)<br/>0 unsynchronized crossings>, fillcolor="{T_AQUA}"];
SYN   [label=<<b>Design Compiler</b><br/>compile_ultra<br/>area 19,918 · 0.227 mW>, fillcolor="{T_BLUE}"];
NET1  [label="gate netlist\\nBackend/Synthesis/netlists", shape=note, fillcolor="white"];
DFT   [label=<<b>DFT insertion</b><br/>4 scan chains<br/>99.48 % fault coverage>, fillcolor="{T_BLUE}"];
NET2  [label="scan netlist\\nBackend/DFT/netlists", shape=note, fillcolor="white"];
FM1   [label=<<b>Formality</b><br/>RTL vs post-synthesis<br/>358 / 358 pass>, fillcolor="{T_VIOLET}"];
FM2   [label=<<b>Formality</b><br/>RTL vs post-DFT<br/>358 / 358 pass>, fillcolor="{T_VIOLET}"];
PNR   [label=<<b>Place &amp; route</b><br/>not included<br/>(empty Formality template)>, style="rounded,dashed", fillcolor="white", color="{GREY}", fontcolor="{GREY}"];
RTL -> SIM; RTL -> SPY; RTL -> SYN; SYN -> NET1; NET1 -> FM1; RTL -> FM1 [style=dashed, constraint=false];
NET1 -> DFT; DFT -> NET2; NET2 -> FM2; RTL -> FM2 [style=dashed, constraint=false];
NET2 -> PNR [style=dashed, color="{GREY}"];
}}''')

# ================================================================ matplotlib helpers
def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", format="svg", bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


def box(ax, x, y, w, h, text, fc, ec=INK2, fs=9, bold=False, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=tc)


# ================================================================ 7. command flows
def command_flows():
    cmds = [
        ("0xAA  RF write", [("AA", "opcode"), ("05", "address"), ("55", "data")], [], "no response"),
        ("0xBB  RF read", [("BB", "opcode"), ("05", "address")], [("55", "RF[5]")], ""),
        ("0xCC  ALU with operands", [("CC", "opcode"), ("20", "A → REG0"), ("05", "B → REG1"), ("00", "ALU_FUN = ADD")],
         [("25", "result LSB"), ("00", "result MSB")], ""),
        ("0xDD  ALU, stored operands", [("DD", "opcode"), ("01", "ALU_FUN = SUB")],
         [("1B", "result LSB"), ("00", "result MSB")], ""),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11.4); ax.set_ylim(0, len(cmds) * 1.3 + 0.9); ax.axis("off")
    ax.text(0.0, len(cmds) * 1.3 + 0.55, "Host → SYS_TOP  (RX_IN)", color=BLUE, fontsize=10, fontweight="bold")
    ax.text(6.9, len(cmds) * 1.3 + 0.55, "SYS_TOP → host  (TX_OUT)", color=ORANGE, fontsize=10, fontweight="bold")
    for i, (name, rx, tx, note) in enumerate(cmds):
        y = (len(cmds) - 1 - i) * 1.3 + 0.1
        ax.text(0.0, y + 0.95, name, fontsize=10, fontweight="bold")
        for j, (b, lab) in enumerate(rx):
            x = j * 1.55
            box(ax, x, y + 0.05, 1.35, 0.5, "0x" + b, T_BLUE, BLUE, fs=11, bold=True)
            ax.text(x + 0.675, y - 0.1, lab, ha="center", va="top", fontsize=7.5, color=INK2)
        for j, (b, lab) in enumerate(tx):
            x = 6.9 + j * 1.55
            box(ax, x, y + 0.05, 1.35, 0.5, "0x" + b, T_ORANGE, ORANGE, fs=11, bold=True)
            ax.text(x + 0.675, y - 0.1, lab, ha="center", va="top", fontsize=7.5, color=INK2)
        if note:
            ax.text(6.9, y + 0.3, note, fontsize=9, color=INK2, style="italic", va="center")
        ax.annotate("", xy=(6.7, y + 0.3), xytext=(len(rx) * 1.55 - 0.1, y + 0.3),
                    arrowprops=dict(arrowstyle="->", color=GREY, lw=1.0))
    ax.set_title("Command / response byte streams (the exact sequences used by test cases TC1–TC4)",
                 fontsize=11, loc="left", color=INK)
    save(fig, "command_flows")


# ================================================================ 8. UART frame + RX sampling
def uart_frame():
    data = 0x55
    bits = [(data >> k) & 1 for k in range(8)]
    parity = sum(bits) % 2          # even parity => parity bit = XOR of data
    seq = [("idle", 1), ("START", 0)] + [(f"D{k}", b) for k, b in enumerate(bits)] + [("PAR", parity), ("STOP", 1), ("idle", 1)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), gridspec_kw={"height_ratios": [1.2, 1]})
    xs, ys = [], []
    for i, (_, v) in enumerate(seq):
        xs += [i, i + 1]; ys += [v, v]
    a1.step(xs, ys, where="post", color=BLUE, lw=2.2)
    a1.plot(xs, ys, color=BLUE, lw=2.2)
    for i, (n, v) in enumerate(seq):
        a1.text(i + 0.5, 1.28, n, ha="center", fontsize=9, color=INK if n not in ("START", "STOP", "PAR") else ORANGE,
                fontweight="bold" if n in ("START", "STOP", "PAR") else "normal")
        a1.text(i + 0.5, -0.32, str(v), ha="center", fontsize=9, color=INK2)
        a1.axvline(i, color=GRID, lw=0.8, zorder=0)
    a1.axvline(len(seq), color=GRID, lw=0.8, zorder=0)
    a1.set_ylim(-0.5, 1.55); a1.set_xlim(0, len(seq)); a1.set_yticks([0, 1]); a1.set_xticks([])
    for s in ("top", "right", "bottom"): a1.spines[s].set_visible(False)
    a1.set_title("UART frame for byte 0x55 with parity enabled (REG2 = 0x81, even parity): 1 start + 8 data (LSB first) + 1 parity + 1 stop",
                 fontsize=10, loc="left")
    a1.annotate("", xy=(11, 1.5), xytext=(1, 1.5), arrowprops=dict(arrowstyle="-", color=GREY))
    a1.text(6, 1.55, "11 bit times = 11 × 8.68 µs ≈ 95.5 µs at 115,200 baud", ha="center", fontsize=8.5, color=INK2, va="bottom")

    # one bit at 32x oversampling
    for i in range(32):
        col = T_GREY
        if i in (15, 16, 17): col = T_ORANGE
        if i == 18: col = T_VIOLET
        a2.add_patch(Rectangle((i, 0), 1, 1, fc=col, ec=INK2, lw=0.8))
        a2.text(i + 0.5, 0.5, str(i), ha="center", va="center", fontsize=8, color=INK)
    a2.set_xlim(-0.3, 32.3); a2.set_ylim(-1.7, 2.2); a2.axis("off")
    a2.text(0, 1.55, "edge_cnt (RX_CLK edges) within one bit, prescale = 32", fontsize=10, fontweight="bold")
    a2.annotate("mid − 1 … mid + 1 (15, 16, 17)\nthree samples → majority vote", xy=(16.5, 0), xytext=(16.5, -0.85),
                ha="center", fontsize=8.5, color=ORANGE, arrowprops=dict(arrowstyle="-|>", color=ORANGE), va="top")
    a2.annotate("mid + 2 (18): sampled_bit consumed\nstart / data / parity / stop check", xy=(18.5, 1), xytext=(24.5, 1.7),
                ha="center", fontsize=8.5, color=VIOLET, arrowprops=dict(arrowstyle="-|>", color=VIOLET), va="center")
    a2.annotate("31 = prescale − 1:\nbit_transition", xy=(31.5, 0), xytext=(28.5, -0.85),
                ha="center", fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-|>", color=INK2), va="top")
    a2.annotate("0: counter restarts\n(edge_cnt wraps, bit_cnt + 1)", xy=(0.5, 0), xytext=(3.0, -0.85),
                ha="center", fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-|>", color=INK2), va="top")
    save(fig, "uart_frame_timing")


# ================================================================ 9. register map
def register_map():
    regs = [
        ("0x0", "REG0", "0x00", "ALU operand A", T_BLUE),
        ("0x1", "REG1", "0x00", "ALU operand B", T_BLUE),
        ("0x2", "REG2", "0x81", "UART configuration", T_ORANGE),
        ("0x3", "REG3", "0x20", "TX clock divider ratio", T_ORANGE),
    ] + [(f"0x{a:X}", f"RF[{a}]", "0x00", "general purpose", T_GREY) for a in range(4, 16)]
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.set_xlim(0, 11); ax.set_ylim(-3.6, 16.6); ax.axis("off"); ax.invert_yaxis()
    ax.text(0, -0.2, "RegFile — 16 × 8 bits", fontsize=11, fontweight="bold", va="bottom")
    for c, (x, w, h) in enumerate([(0, 0.9, "Addr"), (0.9, 1.1, "Name"), (2.0, 1.1, "Reset"), (3.1, 2.7, "Purpose")]):
        ax.text(x + 0.1, 0.5, h, fontsize=8.5, color=INK2, fontweight="bold", va="center")
    for i, (a, n, r, p, col) in enumerate(regs):
        y = 1 + i * 0.95
        ax.add_patch(Rectangle((0, y), 5.8, 0.9, fc=col, ec=SURFACE, lw=2))
        for x, t in ((0.1, a), (1.0, n), (2.1, r), (3.2, p)):
            ax.text(x, y + 0.45, t, fontsize=9, va="center")
    # REG2 bit fields
    ax.text(6.4, 0.5, "REG2 = 0x81  (UART_CONFIG)", fontsize=10, fontweight="bold", va="center")
    fields = [("[7:2]  prescale\n100000 = 32", 6.4, 3.0, T_BLUE), ("[1]  parity type\n0 = even, 1 = odd", 9.4, 0.0, None)]
    # draw 8 bit cells
    x0, cw = 6.4, 0.58
    vals = [1, 0, 0, 0, 0, 0, 0, 1]
    for k in range(8):
        bit = 7 - k
        col = T_BLUE if bit >= 2 else (T_ORANGE if bit == 1 else T_AQUA)
        ax.add_patch(Rectangle((x0 + k * cw, 1.3), cw, 0.9, fc=col, ec=INK2, lw=1))
        ax.text(x0 + k * cw + cw / 2, 1.75, str(vals[k]), ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x0 + k * cw + cw / 2, 1.1, str(bit), ha="center", va="bottom", fontsize=8, color=INK2)
    ax.text(x0, 2.9, "[7:2]  prescale (one-hot): 100000 = 32, 010000 = 16,\n001000 = 8, 000100 = 4 → RX oversampling factor", fontsize=8.5, color=INK2, va="top")
    ax.text(x0, 4.1, "[1]  parity type — 0 = even (default), 1 = odd", fontsize=8.5, color=INK2, va="top")
    ax.text(x0, 4.8, "[0]  parity enable — 1 = parity bit present (default)", fontsize=8.5, color=INK2, va="top")
    ax.text(6.4, 6.3, "REG3 = 0x20  (TX divider)", fontsize=10, fontweight="bold", va="center")
    ax.text(6.4, 7.0, "TX_CLK = UART_CLK ÷ REG3 = 3.6864 MHz ÷ 32 = 115.2 kHz\n→ one TX_CLK period per bit = 115,200 baud", fontsize=8.5, color=INK2, va="top")
    ax.text(6.4, 8.7, "Access rules", fontsize=10, fontweight="bold", va="center")
    ax.text(6.4, 9.4, "• synchronous write; registered read + RdData_VLD\n• a write with RdEn also high is ignored\n• REG0–REG3 are exported as dedicated ports\n• REG2 / REG3 feed the UART domain with no\n  synchronizer (quasi-static; constrained in SpyGlass)",
            fontsize=8.5, color=INK2, va="top", linespacing=1.5)
    save(fig, "register_map")


# ================================================================ 10. ALU map
def alu_map():
    ops = {0: ("A + B", "arith"), 1: ("A − B", "arith"), 2: ("A × B", "arith"), 3: ("A ÷ B", "arith"),
           4: ("A & B", "logic"), 5: ("A | B", "logic"), 6: ("~(A & B)", "logic"), 7: ("~(A | B)", "logic"),
           8: ("A ^ B", "logic"), 9: ("~(A ^ B)", "logic"), 10: ("A == B → 1", "cmp"), 11: ("A > B → 2", "cmp"),
           12: ("A < B → 3 ★", "cmp"), 13: ("A >> 1", "shift"), 14: ("A << 1", "shift"), 15: ("0 (unused)", "none")}
    colors = {"arith": (T_BLUE, BLUE), "logic": (T_AQUA, AQUA), "cmp": (T_ORANGE, ORANGE),
              "shift": (T_VIOLET, VIOLET), "none": (T_GREY, GREY)}
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    ax.set_xlim(0, 4); ax.set_ylim(0, 4.55); ax.axis("off"); ax.invert_yaxis()
    for f, (t, k) in ops.items():
        r, c = divmod(f, 4)
        fc, ec = colors[k]
        ax.add_patch(Rectangle((c + 0.04, r + 0.04 + 0.45), 0.92, 0.92, fc=fc, ec=SURFACE, lw=0))
        ax.add_patch(Rectangle((c + 0.04, r + 0.04 + 0.45), 0.07, 0.92, fc=ec, ec=ec, lw=0))
        ax.text(c + 0.17, r + 0.45 + 0.22, f"{f:04b}", fontsize=8.5, color=INK2, family="DejaVu Sans Mono", va="center")
        ax.text(c + 0.55, r + 0.45 + 0.65, t, fontsize=10.5, ha="center", va="center", fontweight="bold")
    ax.text(0, 0.1, "ALU_FUN[3:0] → operation (16-bit registered result, A = {8'b0, REG0}, B = {8'b0, REG1})", fontsize=10, fontweight="bold", va="center")
    lx = 0
    for k, lab in (("arith", "arithmetic"), ("logic", "bitwise"), ("cmp", "compare"), ("shift", "shift")):
        ax.add_patch(Rectangle((lx, 0.3), 0.14, 0.14, fc=colors[k][1])); ax.text(lx + 0.2, 0.37, lab, fontsize=8.5, va="center", color=INK2); lx += 1.05
    ax.text(3.0, 0.37, "★ extra function, not in spec", fontsize=8.5, color=INK2, va="center")
    save(fig, "alu_function_map")


# ================================================================ 11. results charts
def bars_h(ax, labels, values, color, fmt="{:,}", xmax=None):
    y = range(len(labels))
    ax.barh(list(y), values, color=color, height=0.62)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    xm = xmax or max(values) * 1.18
    ax.set_xlim(0, xm)
    for yi, v in zip(y, values):
        ax.text(v + xm * 0.012, yi, fmt.format(v), va="center", fontsize=9, color=INK)


def area_power():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.3), gridspec_kw={"width_ratios": [1.5, 1]})
    comb, seq = [10970.37, 10479.69], [8947.63, 11396.34]
    labels = ["Post-synthesis", "Post-DFT"]
    a1.bar(labels, comb, color=BLUE, width=0.5, label="Combinational")
    a1.bar(labels, seq, bottom=[c + 0.0 for c in comb], color=ORANGE, width=0.5, label="Sequential (non-combinational)")
    for i, (c, s) in enumerate(zip(comb, seq)):
        a1.text(i, c / 2, f"{c:,.0f}", ha="center", va="center", color="white", fontweight="bold")
        a1.text(i, c + s / 2, f"{s:,.0f}", ha="center", va="center", color="white", fontweight="bold")
        a1.text(i, c + s + 400, f"total {c + s:,.0f}", ha="center", fontsize=9.5, fontweight="bold")
    a1.set_ylim(0, 25500); a1.set_title("Cell area (library units)", fontsize=10.5, loc="left")
    a1.text(0.5, 24000, "+9.83 % after scan insertion", ha="center", fontsize=9, color=INK2)
    a1.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0, 0.93))
    a2.bar(labels, [0.227, 0.387], color=[BLUE, ORANGE], width=0.5)
    for i, v in enumerate([0.227, 0.387]):
        a2.text(i, v + 0.012, f"{v:.3f} mW", ha="center", fontsize=9.5, fontweight="bold")
    a2.set_ylim(0, 0.47); a2.set_title("Total power", fontsize=10.5, loc="left")
    a2.text(0.5, 0.44, "≈ +70 % (scan toggling, scan flops)", ha="center", fontsize=9, color=INK2)
    for a in (a1, a2):
        for s in ("top", "right"): a.spines[s].set_visible(False)
        a.yaxis.grid(True, color=GRID, lw=0.8); a.set_axisbelow(True)
    fig.suptitle("Area and power: synthesis vs. DFT-inserted netlist", fontsize=11.5, x=0.01, ha="left")
    save(fig, "chart_area_power")


def timing_slack():
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    names = ["ALU_CLK", "REF_CLK", "UART_CLK", "RX_CLK", "TX_CLK"]
    vals = [10.06, 14.92, 268.08, 215.83, 6942.42]
    order = sorted(range(5), key=lambda i: vals[i])
    names = [names[i] for i in order]; vals = [vals[i] for i in order]
    y = range(5)
    ax.barh(list(y), vals, color=BLUE, height=0.6)
    ax.set_xscale("log"); ax.set_xlim(3, 4e4)
    ax.set_yticks(list(y)); ax.set_yticklabels(names)
    for yi, v in zip(y, vals):
        ax.text(v * 1.12, yi, f"{v:,.2f} ns", va="center", fontsize=9)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_xlabel("worst setup slack, ns (log scale) — all positive, no violations")
    ax.set_title("Post-synthesis setup slack per clock", fontsize=11, loc="left")
    save(fig, "chart_setup_slack")


def dft_summary():
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.9), gridspec_kw={"width_ratios": [1, 1.15, 1.15]})
    bars_h(axs[0], ["Chain 1\nSI[2]→SO[2]", "Chain 2\nSI[1]→SO[1]", "Chain 3\nSI[0]→SO[0]", "Chain 4\ntest_si4→RF_STP_ERR"],
           [89, 89, 88, 88], BLUE, xmax=118)
    axs[0].set_title("Scan chains: cells per chain", fontsize=10, loc="left")
    cells = [("SDFFRQX1M", 272), ("SDFFX1M", 64), ("DFFRQX1M", 10), ("SDFFRQX2M", 4),
             ("SDFFSQX2M", 2), ("SDFFSQX1M", 1), ("DFFRQX2M", 1), ("TLATNCAX12M (gate)", 1)]
    bars_h(axs[1], [c for c, _ in cells], [v for _, v in cells], ORANGE, xmax=330)
    axs[1].set_title("Post-DFT sequential cell mix (355)", fontsize=10, loc="left")
    faults = [("Detected", 15939), ("ATPG-untestable", 81), ("Undetectable", 36), ("Not detected", 2)]
    ax = axs[2]
    y = range(4)
    ax.barh(list(y), [v for _, v in faults], color=[AQUA, GREY, GREY, RED], height=0.6)
    ax.set_xscale("log"); ax.set_xlim(1, 2e5)
    ax.set_yticks(list(y)); ax.set_yticklabels([n for n, _ in faults]); ax.invert_yaxis()
    for yi, (_, v) in zip(y, faults):
        ax.text(v * 1.2, yi, f"{v:,}", va="center", fontsize=9)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title("Faults (16,058 total, log scale)\nfault coverage 99.48 %", fontsize=10, loc="left")
    fig.suptitle("DFT results (Design Compiler scan insertion, final run)", fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    save(fig, "chart_dft_summary")


def cdc_summary():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.1, 1]})
    cats = ["Synchronized scalar", "Synchronized vector", "Quasi-static (REG2/REG3 bits)", "Unsynchronized"]
    vals = [7, 14, 15, 0]
    bars_h(a1, cats, vals, [BLUE, BLUE, VIOLET, RED], xmax=19, fmt="{}")
    a1.set_title("SpyGlass CDC verify: crossings by class", fontsize=10, loc="left")
    goals = ["Design_Read", "lint_rtl", "cdc_setup_check", "cdc_clock_reset\n_integrity", "cdc_abstract", "cdc_verify_struct", "cdc_verify"]
    errs = [0, 1, 0, 0, 0, 0, 0]
    waived = [0, 0, 1, 2, 1, 3, 6]
    y = list(range(len(goals)))
    a2.barh(y, waived, color=ORANGE, height=0.6, label="waived")
    a2.barh(y, errs, left=waived, color=RED, height=0.6, label="error (intended latch)")
    a2.set_yticks(y); a2.set_yticklabels(goals, fontsize=8.5); a2.invert_yaxis(); a2.set_xlim(0, 8)
    for yi, w, e in zip(y, waived, errs):
        a2.text(w + e + 0.12, yi, f"{w} waived" + (f" · {e} error" if e else ""), va="center", fontsize=8.5)
    for s in ("top", "right"): a2.spines[s].set_visible(False)
    a2.xaxis.grid(True, color=GRID, lw=0.8); a2.set_axisbelow(True)
    a2.set_title("Errors and waivers per goal", fontsize=10, loc="left")
    a2.legend(frameon=False, fontsize=8.5, loc="lower right")
    fig.suptitle("CDC / lint sign-off summary", fontsize=11.5, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save(fig, "chart_cdc_summary")


def sim_timeline():
    starts = [643.661, 1077.688, 1394.182, 2001.822, 2418.490]
    labels = ["TC1\nRF write", "TC2\nRF read", "TC3\nALU ADD", "TC4\nALU SUB", "TC5\nALU MUL"]
    cols = [BLUE, AQUA, ORANGE, ORANGE, ORANGE]
    fig, ax = plt.subplots(figsize=(11, 2.9))
    ax.set_xlim(0, 2800); ax.set_ylim(-1.2, 1.7)
    ax.axhline(0, color=INK2, lw=1.2)
    ax.add_patch(Rectangle((0, -0.12), starts[0], 0.24, fc=T_GREY, ec=INK2, lw=1))
    ax.text(starts[0] / 2, 0.55, "reset + UART config\n(write REG2, REG3)", ha="center", fontsize=8.5, color=INK2)
    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else s + 250
        ax.add_patch(Rectangle((s, -0.12), end - s, 0.24, fc=cols[i], ec=SURFACE, lw=2, alpha=0.85))
        ax.text(s + 8, 0.55, labels[i], ha="left", fontsize=9, fontweight="bold")
        ax.plot([s, s], [-0.12, 0.45], color=INK2, lw=0.8)
        ax.text(s, -0.45, f"{s:,.1f} µs", fontsize=8, color=INK2, ha="left")
    ax.text(starts[-1] + 255, 0, "→", fontsize=14, va="center", color=INK2)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.set_yticks([]); ax.set_xlabel("simulation time (µs) — tc_start_time captured in the ModelSim waveforms (TC5 end not marked)")
    ax.set_title("Testbench timeline: configuration, then five self-checking test cases (5 / 5 passed)", fontsize=10.5, loc="left")
    save(fig, "tb_timeline")


if __name__ == "__main__":
    command_flows(); uart_frame(); register_map(); alu_map()
    area_power(); timing_slack(); dft_summary(); cdc_summary(); sim_timeline()
    print("generated:", ", ".join(sorted(p.name for p in OUT.iterdir())))
