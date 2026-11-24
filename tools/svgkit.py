"""Küçük SVG araç seti: metni glif path'lerine çevirir, belge ve animasyon yardımcıları sağlar.

GitHub README görselleri <img> içinde, script ve harici kaynak olmadan çizilir.
Bu yüzden yazılar font olarak değil, <defs> içinde bir kez tanımlanan glif path'leri
ve <use> referansları olarak gömülür. Harf harf animasyon da buradan gelir.
"""
from __future__ import annotations

import io
import math
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(__file__).parent / "fonts"

# Palet
BG = "#0A0A0B"
PANEL = "#121214"
PANEL2 = "#17171A"
LINE = "#26262A"
BONE = "#EEE9E0"
MUTED = "#8E8A82"
DIM = "#56534E"
EMBER = "#FF5B22"
EMBER2 = "#FF9A6B"


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class _Face:
    def __init__(self, file: Path, variations: dict):
        raw = file.read_bytes()
        tt = TTFont(io.BytesIO(raw))
        self.upm = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.cap = getattr(tt["OS/2"], "sCapHeight", 0) or self.upm * .7
        if tt.flavor:  # harfbuzz WOFF2 okuyamaz; düz sfnt'ye çevir
            tt.flavor = None
            buf = io.BytesIO()
            tt.save(buf)
            raw = buf.getvalue()
            tt = TTFont(io.BytesIO(raw))
        static = instancer.instantiateVariableFont(tt, variations) if "fvar" in tt else tt
        self.order = static.getGlyphOrder()
        self.glyphset = static.getGlyphSet()
        # harfbuzz, yüksek kaliteli kerning ve ileri genişlikler için
        face = hb.Face(raw)
        self.hb = hb.Font(face)
        self.hb.set_variations(variations)
        self._paths: dict[int, str] = {}

    def path(self, gid: int) -> str:
        if gid not in self._paths:
            pen = SVGPathPen(self.glyphset, ntos=lambda v: str(round(v)))
            self.glyphset[self.order[gid]].draw(pen)
            self._paths[gid] = pen.getCommands()
        return self._paths[gid]


class Font:
    """Bir stil (ör. Inter 800 opsz 32). latin + latin-ext dosyaları arasında geri düşer."""

    _cache: dict = {}

    def __init__(self, key: str, files: list[str], **variations):
        self.key = key
        self.faces = [_Face(FONTS / f, variations) for f in files]
        self.upm = self.faces[0].upm
        self.cap = self.faces[0].cap / self.upm

    def baseline(self, center_y: float, size: float) -> float:
        """Büyük harfleri center_y etrafında optik olarak ortalayan taban çizgisi."""
        return center_y + self.cap * size / 2

    def _face_for(self, ch: str) -> int:
        for i, f in enumerate(self.faces):
            if ord(ch) in f.cmap:
                return i
        if ch.strip():
            raise ValueError(f"{self.key}: '{ch}' (U+{ord(ch):04X}) glifi yok")
        return 0

    def shape(self, s: str):
        """[(face_idx, gid, x_font_units, advance)] döndürür."""
        out, x = [], 0
        runs, cur, buf = [], None, ""
        for ch in s:
            fi = self._face_for(ch)
            if cur is None or fi == cur or not ch.strip():
                cur = fi if cur is None or ch.strip() else cur
                buf += ch
            else:
                runs.append((cur, buf))
                cur, buf = fi, ch
        if buf:
            runs.append((cur, buf))
        for fi, text in runs:
            b = hb.Buffer()
            b.add_str(text)
            b.guess_segment_properties()
            hb.shape(self.faces[fi].hb, b, {"kern": True, "liga": True, "calt": True})
            for info, pos in zip(b.glyph_infos, b.glyph_positions):
                out.append((fi, info.codepoint, x + pos.x_offset, pos.x_advance))
                x += pos.x_advance
        return out, x


class Doc:
    def __init__(self, w: int, h: int, title: str, desc: str):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.defs: list[str] = []
        self.css: list[str] = []
        self.motion_css: list[str] = []
        self.body: list[str] = []
        self._glyphs: dict[str, str] = {}
        self._uid = 0

    def uid(self, p="u") -> str:
        self._uid += 1
        return f"{p}{self._uid}"

    def add(self, *parts: str):
        self.body.extend(parts)

    # --- metin ---------------------------------------------------------
    def measure(self, s: str, font: Font, size: float, ls: float = 0) -> float:
        _, adv = font.shape(s)
        return adv * size / font.upm + ls * max(len(s) - 1, 0)

    def glyphs(self, s: str, font: Font, size: float, x: float, y: float, ls: float = 0, anchor: str = "start"):
        """Her glif için (svg_use, gx, ch_index) listesi ve toplam genişlik."""
        shaped, adv = font.shape(s)
        k = size / font.upm
        width = adv * k + ls * max(len(shaped) - 1, 0)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        items = []
        for i, (fi, gid, gx, _a) in enumerate(shaped):
            d = font.faces[fi].path(gid)
            px = x + gx * k + ls * i
            if not d:
                items.append((None, px, i))
                continue
            gid_key = f"{font.key}{fi}g{gid}"
            if gid_key not in self._glyphs:
                self._glyphs[gid_key] = d
            use = f'<use href="#{gid_key}" transform="translate({fmt(px)} {fmt(y)}) scale({k:.5f} {-k:.5f})"/>'
            items.append((use, px, i))
        return items, width, x

    def text(self, s, font, size, x, y, fill=BONE, ls=0, anchor="start", attrs="", wrap=None):
        items, width, x0 = self.glyphs(s, font, size, x, y, ls, anchor)
        inner = "".join(wrap(u, gx, i) if wrap else u for u, gx, i in items if u)
        fill_attr = f' fill="{fill}"' if fill else ""
        return f"<g{fill_attr}{(' ' + attrs) if attrs else ''}>{inner}</g>", width

    def wraplines(self, s, font, size, maxw):
        words, lines, cur = s.split(" "), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.measure(t, font, size) > maxw and cur:
                lines.append(cur)
                cur = w
            else:
                cur = t
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, s, font, size, x, y, maxw, lh, fill=MUTED):
        out = []
        for i, line in enumerate(self.wraplines(s, font, size, maxw)):
            g, _ = self.text(line, font, size, x, y + i * lh, fill)
            out.append(g)
        return "".join(out), len(out)

    # --- çıktı -----------------------------------------------------------
    def render(self) -> str:
        glyph_defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in self._glyphs.items())
        css = "\n".join(self.css)
        if self.motion_css:
            css += "\n@media (prefers-reduced-motion: no-preference) {\n" + "\n".join(self.motion_css) + "\n}"
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{self.title}</title><desc id="d">{self.desc}</desc>'
            f"<defs>{glyph_defs}{''.join(self.defs)}</defs>"
            f"<style>{css}</style>"
            + "".join(self.body)
            + "</svg>"
        )


# --- yaygın parçalar -------------------------------------------------------

def smil(attr, values, key_times, dur, spline=".22 1 .36 1", discrete=False, begin="0s"):
    vals = ";".join(fmt(v) if isinstance(v, (int, float)) else str(v) for v in values)
    kt = ";".join(f"{t:.4f}".rstrip("0").rstrip(".") if t not in (0, 1) else str(t) for t in key_times)
    if discrete:
        return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{dur}s" '
                f'begin="{begin}" repeatCount="indefinite" calcMode="discrete"/>')
    ks = ";".join([spline] * (len(values) - 1))
    return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{dur}s" begin="{begin}" '
            f'repeatCount="indefinite" calcMode="spline" keySplines="{ks}"/>')


def fade_window(on, off, dur, ramp=0.25):
    """[on, off] saniyeleri arasında görünür olan opaklık animasyonu."""
    r = ramp / dur
    a, b = on / dur, off / dur
    kt = [0, max(a - r, 0.0001), a, b, min(b + r, 0.9999), 1]
    return smil("opacity", [0, 0, 1, 1, 0, 0], kt, dur, spline=".4 0 .2 1")


def grain(doc: Doc, opacity=0.07):
    fid = doc.uid("n")
    doc.defs.append(
        f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
        '<feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" stitchTiles="stitch"/>'
        '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.2 -.35"/></filter>'
    )
    return f'<rect width="{doc.w}" height="{doc.h}" filter="url(#{fid})" opacity="{opacity}"/>'


def frame(doc: Doc, rx=28):
    cid = doc.uid("c")
    doc.defs.append(f'<clipPath id="{cid}"><rect width="{doc.w}" height="{doc.h}" rx="{rx}"/></clipPath>')
    open_ = f'<g clip-path="url(#{cid})"><rect width="{doc.w}" height="{doc.h}" fill="{BG}"/>'
    close = (f'</g><rect x=".75" y=".75" width="{doc.w - 1.5}" height="{doc.h - 1.5}" rx="{rx - .75}" '
             f'fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    return open_, close


def glow(doc: Doc, cx, cy, r, color=EMBER, opacity=0.35, cls=""):
    gid = doc.uid("gl")
    doc.defs.append(
        f'<radialGradient id="{gid}"><stop stop-color="{color}" stop-opacity="{opacity}"/>'
        f'<stop offset=".45" stop-color="{color}" stop-opacity="{opacity * .38:.3f}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
    )
    c = f' class="{cls}"' if cls else ""
    return f'<circle{c} cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>'


def arrow(x, y, s=12, color=BONE, w=1.8):
    return (f'<path d="M{fmt(x)} {fmt(y + s)} L{fmt(x + s)} {fmt(y)} M{fmt(x + s * .3)} {fmt(y)} H{fmt(x + s)} V{fmt(y + s * .7)}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def ring_text(doc: Doc, s, font, size, cx, cy, r, fill=BONE):
    """Metni bir çemberin etrafına diz (saat yönünde, üstten başlayarak)."""
    shaped, adv = font.shape(s)
    k = size / font.upm
    circ = 2 * math.pi * r
    spread = circ / (adv * k)  # glifleri çevreye yay
    parts = []
    for fi, gid, gx, a in shaped:
        d = font.faces[fi].path(gid)
        if not d:
            continue
        key = f"{font.key}{fi}g{gid}"
        doc._glyphs.setdefault(key, d)
        mid = (gx + a / 2) * k * spread
        ang = mid / circ * 360 - 90
        rad = math.radians(ang)
        px, py = cx + r * math.cos(rad), cy + r * math.sin(rad)
        parts.append(
            f'<use href="#{key}" transform="translate({fmt(px)} {fmt(py)}) rotate({fmt(ang + 90)}) '
            f'translate({fmt(-a * k / 2)} {fmt(size * .36)}) scale({k:.5f} {-k:.5f})"/>'
        )
    return f'<g fill="{fill}">{"".join(parts)}</g>'
