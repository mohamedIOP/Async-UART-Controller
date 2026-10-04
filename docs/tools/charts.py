"""Result charts (matplotlib): area/power, slack, DFT, CDC, TB timeline, cell mix. Run: python3 docs/tools/charts.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "images", "generated") + os.sep
os.makedirs(OUT, exist_ok=True)

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8985", "#e4e3df"
BLUE, ORANGE, AQUA, VIOLET, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#eda100"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.facecolor": "white",
})


def style_grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT + name, dpi=190, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


# ------------------------------------------------------------ 1. area + power
def area_power():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
    stages = ["Post-synthesis", "Post-DFT"]
    comb = [10970.37, 10479.69]
    seq = [8947.63, 11396.34]
    x = [0, 1]
    b1 = a1.bar(x, comb, 0.5, color=BLUE, label="Combinational", bottom=None)
    b2 = a1.bar(x, seq, 0.5, bottom=comb, color=ORANGE, label="Sequential", edgecolor="white", linewidth=2)
    for i in x:
        a1.text(i, comb[i] / 2, f"{comb[i]:,.0f}", ha="center", va="center", color="white", fontweight="bold")
        a1.text(i, comb[i] + seq[i] / 2, f"{seq[i]:,.0f}", ha="center", va="center", color="white", fontweight="bold")
        a1.text(i, comb[i] + seq[i] + 450, f"{comb[i] + seq[i]:,.0f}", ha="center", va="bottom", fontweight="bold")
    a1.annotate("+9.83 %", xy=(0.5, 20500), xytext=(0.5, 20500), ha="center", color=INK2, fontsize=11, fontweight="bold")
    a1.set_xticks(x, stages)
    a1.set_ylim(0, 29500)
    a1.set_title("Cell area (library units)", loc="left", fontweight="bold", fontsize=12)
    a1.legend(frameon=False, loc="upper left", ncol=2)
    style_grid(a1, "y")
    a1.spines["left"].set_visible(False)
    a1.tick_params(left=False)

    pw = [0.227, 0.387]
    a2.bar(x, pw, 0.5, color=[BLUE, ORANGE])
    for i in x:
        a2.text(i, pw[i] + 0.012, f"{pw[i]:.3f} mW", ha="center", va="bottom", fontweight="bold")
    a2.text(0.5, 0.30, "+70 %", ha="center", color=INK2, fontsize=11, fontweight="bold")
    a2.set_xticks(x, stages)
    a2.set_ylim(0, 0.5)
    a2.set_title("Total power (default activity)", loc="left", fontweight="bold", fontsize=12)
    style_grid(a2, "y")
    a2.spines["left"].set_visible(False)
    a2.tick_params(left=False)
    fig.suptitle("Cost of scan insertion: SYS_TOP area and power", x=0.01, ha="left", fontsize=13.5, fontweight="bold", y=1.02)
    save(fig, "chart_area_power.png")


# ------------------------------------------------------------ 2. slack
def slack():
    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    names = ["ALU_CLK", "REF_CLK", "RX_CLK", "UART_CLK", "TX_CLK"]
    vals = [10.06, 14.92, 215.83, 268.08, 6942.42]
    per = ["20 ns", "20 ns", "271 ns", "271 ns", "8.68 µs"]
    y = range(len(names))
    ax.barh(y, vals, 0.55, color=BLUE)
    ax.set_xscale("log")
    ax.set_xlim(3, 40000)
    for i, v in enumerate(vals):
        ax.text(v * 1.15, i, f"{v:,.2f} ns", va="center", fontweight="bold")
    ax.set_yticks(list(y), [f"{n}  ({p})" for n, p in zip(names, per)])
    ax.set_xlabel("Worst setup slack, ns (log scale)  —  all positive, no violations")
    ax.set_title("Setup timing slack per clock after synthesis  (clock period in brackets)", loc="left", fontweight="bold", fontsize=12.5)
    style_grid(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    ax.invert_yaxis()
    save(fig, "chart_setup_slack.png")


# ------------------------------------------------------------ 3. DFT
def dft():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
    cats = ["Detected", "ATPG-untestable", "Undetectable", "Not detected"]
    vals = [15939, 81, 36, 2]
    cols = [BLUE, ORANGE, ORANGE, ORANGE]
    y = range(4)
    a1.barh(y, vals, 0.55, color=cols)
    a1.set_xscale("log")
    a1.set_xlim(1, 400000)
    for i, v in enumerate(vals):
        a1.text(v * 1.25, i, f"{v:,}", va="center", fontweight="bold")
    a1.set_yticks(list(y), cats)
    a1.invert_yaxis()
    a1.set_xlabel("Number of stuck-at faults (log scale)")
    a1.set_title("Fault coverage 99.48 %  (16,058 faults)", loc="left", fontweight="bold", fontsize=12.5)
    style_grid(a1, "x")
    a1.spines["left"].set_visible(False)
    a1.tick_params(left=False)

    chains = ["SI[2] → SO[2]", "SI[1] → SO[1]", "SI[0] → SO[0]", "test_si4 → RF_STP_ERR"]
    ln = [89, 89, 88, 88]
    a2.barh(range(4), ln, 0.55, color=AQUA)
    for i, v in enumerate(ln):
        a2.text(v + 1.5, i, f"{v}", va="center", fontweight="bold")
    a2.axvline(100, color=RED if False else MUTED, linestyle=(0, (4, 3)), linewidth=1.3)
    a2.text(99, 3.62, "max_length 100", ha="right", va="center", color=INK2, fontsize=9.5)
    a2.set_yticks(range(4), chains)
    a2.set_xlim(0, 110)
    a2.invert_yaxis()
    a2.set_xlabel("Scan cells per chain")
    a2.set_title("4 balanced scan chains (354 cells)", loc="left", fontweight="bold", fontsize=12.5)
    style_grid(a2, "x")
    a2.spines["left"].set_visible(False)
    a2.tick_params(left=False)
    fig.tight_layout(w_pad=3)
    save(fig, "chart_dft.png")


# ------------------------------------------------------------ 4. CDC
def cdc():
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    cats = ["Synchronized (scalar)", "Synchronized (vector)", "Quasi-static (REG2, REG3)", "Unsynchronized"]
    vals = [7, 14, 15, 0]
    cols = [BLUE, BLUE, VIOLET, ORANGE]
    ax.barh(range(4), vals, 0.55, color=cols)
    for i, v in enumerate(vals):
        lab = str(v) if v else "0   none found"
        ax.text(v + 0.3, i, lab, va="center", fontweight="bold")
    ax.set_yticks(range(4), cats)
    ax.invert_yaxis()
    ax.set_xlim(0, 19)
    ax.set_xticks(range(0, 19, 3))
    ax.set_xlabel("Number of clock-domain crossings (SpyGlass cdc_verify)")
    ax.set_title("CDC crossings between REF_CLK and UART_CLK", loc="left", fontweight="bold", fontsize=12.5)
    style_grid(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    save(fig, "chart_cdc.png")


# ------------------------------------------------------------ 5. testbench timeline
def timeline():
    fig, ax = plt.subplots(figsize=(11, 4.0))
    starts = [643.661, 1077.688, 1394.182, 2001.822, 2418.490]
    end = 3100.0
    ends = starts[1:] + [end]
    labels = ["TC1\nRF write", "TC2\nRF read", "TC3\nALU ADD", "TC4\nALU SUB", "TC5\nALU MUL"]
    cols = [AQUA, AQUA, ORANGE, ORANGE, ORANGE]
    ax.barh(1, 643.661 - 0.3, left=0.3, height=0.5, color="#c9c8c3")
    ax.text(322, 1, "reset + UART config\nREG2 ← 0x81\nREG3 ← 0x20", ha="center", va="center", fontsize=9.5, color=INK2)
    for i, (s_, e_) in enumerate(zip(starts, ends)):
        ax.barh(1, e_ - s_ - 6, left=s_, height=0.5, color=cols[i], edgecolor="white", linewidth=0)
        ax.text((s_ + e_) / 2, 1, labels[i], ha="center", va="center", color=INK if cols[i] == AQUA else "white", fontsize=10, fontweight="bold")
        ax.text(s_ + 6, 1.30 + 0.12 * (i % 2), f"starts {s_:,.0f} µs", ha="left", va="bottom", fontsize=8.5, color=INK2, rotation=0)
    ax.set_xlim(0, 3200)
    ax.set_ylim(0.4, 2.0)
    ax.set_yticks([])
    ax.set_xlabel("Simulation time, µs")
    ax.set_title("Testbench timeline  —  5 / 5 test cases pass", loc="left", fontweight="bold", fontsize=12.5)
    ax.legend(handles=[Patch(color=AQUA, label="Register-file commands"), Patch(color=ORANGE, label="ALU commands"),
                       Patch(color="#c9c8c3", label="Start-up")], frameon=False, loc="upper right", ncol=3,
              bbox_to_anchor=(1, 1.0))
    style_grid(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.text(3200, 0.45, "TC5 end ≈ 3.10 ms (read from the waveform)", ha="right", fontsize=8.5, color=MUTED)
    save(fig, "chart_tb_timeline.png")


# ------------------------------------------------------------ 6. DFT cell mix
def cellmix():
    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    names = ["SDFFRQX1M  (scan, async reset)", "SDFFX1M  (scan)", "DFFRQX1M  (non-scan)", "SDFFRQX2M", "SDFFSQX2M", "SDFFSQX1M", "DFFRQX2M", "TLATNCAX12M  (clock-gate latch)"]
    vals = [272, 64, 10, 4, 2, 1, 1, 1]
    cols = [AQUA, AQUA, YELLOW, AQUA, AQUA, AQUA, YELLOW, VIOLET]
    ax.barh(range(8), vals, 0.6, color=cols)
    ax.set_xscale("log")
    ax.set_xlim(0.8, 1500)
    for i, v in enumerate(vals):
        ax.text(v * 1.2, i, str(v), va="center", fontweight="bold")
    ax.set_yticks(range(8), names)
    ax.invert_yaxis()
    ax.set_xlabel("Instances (log scale)")
    ax.set_title("Sequential cells after scan insertion", loc="left", fontweight="bold", fontsize=12.5)
    ax.legend(handles=[Patch(color=AQUA, label="scan flop"), Patch(color=YELLOW, label="plain flop (shift-register cells, not scanned)"),
                       Patch(color=VIOLET, label="clock-gate latch")], frameon=False, loc="lower right", fontsize=9)
    style_grid(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(left=False)
    save(fig, "chart_cell_mix.png")


if __name__ == "__main__":
    area_power()
    slack()
    dft()
    cdc()
    timeline()
    cellmix()
