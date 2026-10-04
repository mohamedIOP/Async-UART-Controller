"""Tiny SVG helper used to hand-build the README diagrams."""
from xml.sax.saxutils import escape

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8985"
BG = "#ffffff"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
VIOLET = "#4a3aa7"
RED = "#e34948"
GREEN = "#008300"
# soft tints for domain / category fills
T_BLUE = "#e8f1fc"
T_ORANGE = "#fdeee7"
T_AQUA = "#e3f6ee"
T_YELLOW = "#fdf3d9"
T_VIOLET = "#ebe8f7"
T_GREY = "#f2f2f0"
FONT = "Helvetica, Arial, sans-serif"


class Svg:
    def __init__(self, w, h, title=None):
        self.w, self.h = w, h
        self.body = []
        self.markers = {}
        self.title = title

    # ---------- primitives ----------
    def _marker(self, color):
        if color not in self.markers:
            self.markers[color] = f"ah{len(self.markers)}"
        return self.markers[color]

    def raw(self, s):
        self.body.append(s)

    def text(self, x, y, s, size=13, color=INK, anchor="start", weight="normal",
             italic=False, family=None):
        fam = family or FONT
        st = ' font-style="italic"' if italic else ""
        self.body.append(
            f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}>{escape(s).replace("  ", chr(160)*2)}</text>')

    def lines(self, x, y, items, size=13, color=INK, anchor="start", weight="normal",
              lh=None, italic=False):
        lh = lh or size * 1.3
        for i, s in enumerate(items):
            self.text(x, y + i * lh, s, size, color, anchor, weight, italic)

    def rect(self, x, y, w, h, fill="none", stroke=INK2, sw=1.5, rx=8, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity else ""
        self.body.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def box(self, x, y, w, h, label, fill=T_GREY, stroke=INK2, size=14, sub=None,
            weight="bold", rx=8, sw=1.5, dash=None, color=INK, subsize=None):
        self.rect(x, y, w, h, fill, stroke, sw, rx, dash)
        subsize = subsize or max(size - 3, 10)
        if sub:
            n = len(sub) if isinstance(sub, list) else 1
            subs = sub if isinstance(sub, list) else [sub]
            total = size + n * (subsize + 3)
            ty = y + (h - total) / 2 + size
            self.text(x + w / 2, ty, label, size, color, "middle", weight)
            for i, s in enumerate(subs):
                self.text(x + w / 2, ty + (subsize + 3) * (i + 1) + 1, s, subsize, INK2, "middle")
        else:
            self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, color, "middle", weight)

    def line(self, pts, color=INK2, sw=1.8, dash=None, arrow=True, arrow_start=False):
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        ms = f' marker-end="url(#{self._marker(color)})"' if arrow else ""
        mst = f' marker-start="url(#{self._marker(color)}s)"' if arrow_start else ""
        if arrow_start:
            self.markers.setdefault(color + "s", None)
        self.body.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{da}{ms}{mst} '
            f'stroke-linejoin="round"/>')

    def circle(self, x, y, r, fill, stroke="none", sw=1):
        self.body.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def pill(self, x, y, w, h, label, fill, stroke, size=13, color=INK, weight="bold"):
        self.box(x, y, w, h, label, fill, stroke, size=size, rx=h / 2, weight=weight, color=color)

    def tag(self, x, y, label, fill=VIOLET, color="#ffffff", size=11):
        w = len(label) * size * 0.62 + 14
        self.rect(x, y, w, size + 8, fill, "none", 0, rx=(size + 8) / 2)
        self.text(x + w / 2, y + size + 1, label, size, color, "middle", "bold")

    # ---------- output ----------
    def render(self):
        defs = []
        for color, name in list(self.markers.items()):
            if name is None:
                continue
            defs.append(
                f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
                f'markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        # start markers (reverse arrow) share the same shape
        for color in [c for c, n in self.markers.items() if n is None]:
            base = color[:-1]
            defs.append(
                f'<marker id="{self.markers[base]}s" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" '
                f'markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="{base}"/></marker>')
        t = f"<title>{escape(self.title)}</title>" if self.title else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img">{t}<defs>{"".join(defs)}</defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>' + "".join(self.body) + "</svg>")

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.render())
