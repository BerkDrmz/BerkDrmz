"""Profil README görsellerini üretir:  python tools/build.py

Çıktılar assets/ altına yazılır. Gereken paketler tools/requirements.txt içinde.
"""
from __future__ import annotations

from pathlib import Path

from svgkit import (BG, BONE, DIM, EMBER, EMBER2, LINE, MUTED, PANEL, PANEL2, Doc, Font, arrow,
                    fade_window, fmt, frame, glow, grain, ring_text, smil)

OUT = Path(__file__).resolve().parent.parent / "assets"

INTER = ["inter-latin-opsz-normal.woff2", "inter-latin-ext-opsz-normal.woff2"]
INTER_I = ["inter-latin-opsz-italic.woff2", "inter-latin-ext-opsz-italic.woff2"]
MONO_F = ["jetbrains-mono-latin-wght-normal.woff2", "jetbrains-mono-latin-ext-wght-normal.woff2"]

DISP = Font("D", INTER, wght=800, opsz=32)
DISPI = Font("I", INTER_I, wght=300, opsz=32)
TITLE = Font("T", INTER, wght=720, opsz=32)
SANS = Font("S", INTER, wght=400, opsz=16)
SANSM = Font("M", INTER, wght=560, opsz=16)
MONO = Font("J", MONO_F, wght=420)
MONOB = Font("K", MONO_F, wght=640)

RISE_CSS = [
    ".rise{animation:rise 1.25s cubic-bezier(.16,1,.3,1) both}",
    "@keyframes rise{from{transform:translateY(270px) skewY(7deg)}to{transform:none}}",
    ".up{animation:up 1s cubic-bezier(.16,1,.3,1) both}",
    "@keyframes up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}",
    ".spin{animation:spin 22s linear infinite;transform-box:fill-box;transform-origin:center}",
    "@keyframes spin{to{transform:rotate(360deg)}}",
    ".bar{animation:bar .9s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}",
    "@keyframes bar{from{transform:scaleY(.25)}to{transform:scaleY(1)}}",
    ".pulse{animation:pulse 1.6s ease-in-out infinite}",
    "@keyframes pulse{50%{opacity:.25}}",
    ".blink{animation:blink 1.05s steps(1) infinite}",
    "@keyframes blink{50%{opacity:0}}",
]


def rise_wrap(delay0, step):
    return lambda use, gx, i: f'<g class="rise" style="animation-delay:{delay0 + i * step:.2f}s">{use}</g>'


def up(svg, delay):
    return f'<g class="up" style="animation-delay:{delay:.2f}s">{svg}</g>'


def marquee(d: Doc, words, font, size, y_center, angle, band_fill, text_fill, dur, reverse=False, h=56):
    sep = "   •   "
    seq = sep.join(words) + sep
    seq_w = d.measure(seq, font, size)
    reps = int(d.w * 1.6 / seq_w) + 2
    g, _ = d.text(seq * reps, font, size, 0, y_center + size * .36, text_fill)
    cls = d.uid("mq")
    direction = "reverse" if reverse else "normal"
    d.motion_css.append(f".{cls}{{animation:{cls} {dur}s linear infinite {direction}}}"
                        f"@keyframes {cls}{{to{{transform:translateX(-{seq_w:.2f}px)}}}}")
    return (f'<g transform="rotate({angle} {d.w / 2} {y_center})">'
            f'<rect x="-200" y="{y_center - h / 2}" width="{d.w + 400}" height="{h}" fill="{band_fill}"/>'
            f'<g transform="translate(-80 0)"><g class="{cls}">{g}</g></g></g>')


def section_label(d, num, label, x, y, color=EMBER, size=13):
    g1, w1 = d.text(num, MONOB, size, x, y, color, ls=1)
    g2, _ = d.text(label, MONO, size, x + w1 + 14, y, MUTED, ls=1.5)
    return g1 + f'<path d="M{fmt(x + w1 + 5)} {y - 4.5}h4" stroke="{DIM}"/>' + g2


def pill(d, label, x, y, font=SANSM, size=16, h=36, color=BONE, stroke="#34343A", fill=PANEL2):
    w = d.measure(label, font, size) + 32
    g, _ = d.text(label, font, size, x + 16, font.baseline(y + h / 2, size), color)
    return f'<rect x="{fmt(x)}" y="{y}" width="{fmt(w)}" height="{h}" rx="{h / 2}" fill="{fill}" stroke="{stroke}"/>' + g, w


def tags(d, items, x, y):
    out, cx = [], x
    for t in items:
        p, w = pill(d, t, cx, y)
        out.append(p)
        cx += w + 8
    return "".join(out)


def cta(d, label, x, y, delay=0):
    g, w = d.text(label, SANSM, 17, x, y, BONE)
    line_id = d.uid("ln")
    d.motion_css.append(f".{line_id}{{animation:{line_id} 3.2s cubic-bezier(.65,0,.35,1) infinite}}"
                        f"@keyframes {line_id}{{0%{{stroke-dashoffset:1}}45%,70%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:-1}}}}")
    return (g + arrow(x + w + 10, y - 12, 11, EMBER, 1.9) +
            f'<path d="M{x} {y + 10}h{fmt(w + 24)}" stroke="{DIM}" stroke-width="1.4"/>'
            f'<path class="{line_id}" d="M{x} {y + 10}h{fmt(w + 24)}" stroke="{EMBER}" stroke-width="1.6" '
            f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>')


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------

def hero():
    W, H = 1200, 700
    d = Doc(W, H, "Berk Durmaz",
            "Berk Durmaz — Bartın Üniversitesi Bilişim Sistemleri öğrencisi. Swift ile macOS uygulamaları, "
            "Python ve JavaScript ile web araçları, Unity ile etkileşimli deneyimler geliştiriyor.")
    d.motion_css += RISE_CSS + [
        ".drift{animation:drift 18s ease-in-out infinite alternate}",
        "@keyframes drift{to{transform:translate(-220px,70px)}}",
    ]
    op, cl = frame(d)
    d.add(op)
    d.add(glow(d, 930, 290, 560, EMBER, .34, "drift"), glow(d, 90, 720, 380, EMBER, .12))
    d.add('<g stroke="#fff" stroke-opacity=".04">' +
          "".join(f'<path d="M{x} 0V{H}"/>' for x in range(100, W, 100)) + "</g>")
    d.add(grain(d, .09))

    # üst bar
    g, _ = d.text("BERK DURMAZ", MONOB, 13, 52, 62, BONE, ls=1.6)
    g2, _ = d.text("PORTFOLYO — 2026", MONO, 13, 52, 82, DIM, ls=1.6)
    g3, _ = d.text("BARTIN, TÜRKİYE", MONOB, 13, W - 52, 62, BONE, ls=1.6, anchor="end")
    g4, _ = d.text("41.63°N  32.34°E", MONO, 13, W - 52, 82, DIM, ls=1.6, anchor="end")
    d.add(up(g + g2, .1), up(g3 + g4, .2))
    d.add(hero_island(d, W / 2, 34))

    # dev başlık
    size = 236
    b1, b2 = 352, 566
    cap = size * .73
    for name, base, font, delay in (("Berk", b1, DISP, .25), ("Durmaz", b2, DISPI, .45)):
        cid = d.uid("lc")
        d.defs.append(f'<clipPath id="{cid}"><rect x="0" y="{base - cap - 40}" width="{W}" height="{cap + 92}"/></clipPath>')
        ls = -size * .045 if font is DISP else -size * .03
        g, w = d.text(name, font, size, 44, base, BONE, ls=ls, wrap=rise_wrap(delay, .07))
        d.add(f'<g clip-path="url(#{cid})">{g}</g>')
        if font is DISP:
            berk_w = w
        else:
            durmaz_w = w
            # nokta ve parıltı
            dot_x = 44 + w + 10
            d.add(f'<g clip-path="url(#{cid})"><g class="rise" style="animation-delay:{delay + .5:.2f}s">'
                  f'<circle cx="{fmt(dot_x + 18)}" cy="{base - 17}" r="17" fill="{EMBER}"/></g></g>')
            # ember parıltı: maske içinde statik kopya
            mid, gid = d.uid("m"), d.uid("sw")
            gm, _ = d.text(name, font, size, 44, base, "#fff", ls=ls)
            d.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">{gm}</mask>')
            d.defs.append(
                f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="-420" x2="0" y1="0" y2="0">'
                f'<stop stop-color="{EMBER}" stop-opacity="0"/><stop offset=".55" stop-color="{EMBER2}" stop-opacity=".95"/>'
                f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/>'
                f'<animateTransform attributeName="gradientTransform" type="translate" values="0 0;{W + 420} 0;{W + 420} 0" '
                f'keyTimes="0;.42;1" dur="7s" begin="2.2s" repeatCount="indefinite" calcMode="spline" '
                f'keySplines=".55 0 .3 1;0 0 1 1"/></linearGradient>')
            d.add(f'<rect x="0" y="{base - cap - 30}" width="{W}" height="{cap + 70}" fill="url(#{gid})" mask="url(#{mid})"/>')

    # sağ açıklama
    x0 = max(44 + berk_w + 74, 640)
    lbl, _ = d.text("BİLİŞİM SİSTEMLERİ · BARTIN ÜNİ.", MONO, 13, x0, 196, EMBER, ls=1.4)
    d.add(up(f'<circle cx="{x0 - 14}" cy="191.5" r="3.5" fill="{EMBER}" class="pulse"/>' + lbl, 1.0))
    for i, line in enumerate(["Swift ile macOS uygulamaları,", "Python ve JavaScript ile web araçları,",
                              "Unity ile etkileşimli deneyimler."]):
        g, _ = d.text(line, SANS, 22, x0, 240 + i * 31, BONE if i == 0 else MUTED)
        d.add(up(g, 1.1 + i * .09))

    # dönen rozet
    cx, cy = W - 140, 452
    rot = ring_text(d, "AÇIK KAYNAK • macOS • WEB • UNITY • ", MONOB, 12.5, 0, 0, 70, BONE)
    star = "".join(f'<path d="M0 -18V18" transform="rotate({a})"/>' for a in range(0, 180, 30))
    d.add(up(f'<g transform="translate({cx} {cy})">'
             f'<circle r="92" fill="{BG}" fill-opacity=".55" stroke="{LINE}"/>'
             f'<g class="spin">{rot}</g>'
             f'<g class="spin" style="animation-direction:reverse;animation-duration:9s" stroke="{EMBER}" '
             f'stroke-width="3.2" stroke-linecap="round">{star}</g></g>', 1.4))
    assert 44 + durmaz_w + 46 < cx - 92, ("rozet başlıkla çakışıyor", 44 + durmaz_w)

    # bantlar
    words = ["SWIFT", "APPKIT", "CORE ANIMATION", "SWIFTUI", "PYTHON", "REACT", "TYPESCRIPT",
             "CLOUDFLARE WORKERS", "UNITY", "C#", "POSTGRESQL"]
    d.add(marquee(d, words[::-1], MONO, 15, 652, 2.2, PANEL2, MUTED, 46, reverse=True, h=44))
    d.add(marquee(d, words, DISP, 26, 650, -2.4, EMBER, BG, 34, h=56))

    d.add(cl)
    return d


def hero_island(d: Doc, cx, top, label="ŞİMDİ GELİŞTİRİLİYOR", title="OpenIsland  —  v1", delay=.5):
    """Dinamik ada: kompakt → medya → kompakt → odak → kompakt (12 sn döngü)."""
    dur = 12
    kt = [0, .07, .12, .40, .45, .52, .57, .82, .87, 1]
    ws = [128, 128, 430, 430, 128, 128, 300, 300, 128, 128]
    hs = [36, 36, 58, 58, 36, 36, 46, 46, 36, 36]
    sp = ".3 1.3 .4 1"  # (keySplines 0..1 aralığında olmalı) yumuşak yay
    sp = ".2 .9 .25 1"
    anim = (smil("width", ws, kt, dur, sp) + smil("x", [cx - w / 2 for w in ws], kt, dur, sp) +
            smil("height", hs, kt, dur, sp) + smil("rx", [h / 2 for h in hs], kt, dur, sp))
    out = [f'<g class="up" style="animation-delay:{delay}s">',
           f'<rect x="{cx - 64}" y="{top}" width="128" height="36" rx="18" fill="#000" stroke="#2A2A2E">{anim}</rect>']
    # kompakt: kamera noktası + kayıt ışığı
    out.append(f'<g>{smil("opacity", [1, 1, 0, 0, 1, 1, 0, 0, 1, 1], [0, .07, .09, .43, .47, .52, .54, .85, .89, 1], dur, ".4 0 .2 1")}'
               f'<circle cx="{cx + 38}" cy="{top + 18}" r="4.5" fill="#141418" stroke="#26262C"/>'
               f'<circle cx="{cx - 40}" cy="{top + 18}" r="3" fill="{EMBER}" class="pulse"/></g>')
    # medya
    L = cx - 215
    t1, _ = d.text(label, MONO, 10, L + 62, top + 23, MUTED, ls=1.2)
    t2, _ = d.text(title, SANSM, 15, L + 62, top + 43, BONE)
    art = d.uid("art")
    d.defs.append(f'<linearGradient id="{art}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{EMBER2}"/>'
                  f'<stop offset="1" stop-color="#7A1E05"/></linearGradient>')
    bars = "".join(
        f'<rect class="bar" style="animation-delay:-{(i * .37) % .9:.2f}s;animation-duration:{.55 + (i % 3) * .18:.2f}s" '
        f'x="{cx + 150 + i * 9}" y="{top + 16}" width="4" height="26" rx="2" fill="{EMBER}"/>' for i in range(5))
    out.append(f'<g opacity="0">{fade_window(1.6, 4.7, dur)}'
               f'<rect x="{L + 12}" y="{top + 11}" width="36" height="36" rx="10" fill="url(#{art})"/>'
               f'<circle cx="{L + 30}" cy="{top + 29}" r="7" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="2"/>'
               f'{t1}{t2}{bars}</g>')
    # odak
    L2 = cx - 150
    t3, _ = d.text("Odak", SANSM, 14, L2 + 44, top + 28, BONE)
    t4, _ = d.text("24:59", MONOB, 15, L2 + 284, top + 28, EMBER, anchor="end")
    ring = (f'<circle cx="{L2 + 24}" cy="{top + 23}" r="10" fill="none" stroke="#2A2A2E" stroke-width="3"/>'
            f'<circle cx="{L2 + 24}" cy="{top + 23}" r="10" fill="none" stroke="{EMBER}" stroke-width="3" '
            f'stroke-linecap="round" pathLength="100" stroke-dasharray="100" transform="rotate(-90 {L2 + 24} {top + 23})">'
            f'{smil("stroke-dashoffset", [100, 100, 18, 18], [0, .55, .82, 1], dur, ".4 0 .2 1")}</circle>')
    out.append(f'<g opacity="0">{fade_window(7.0, 9.8, dur)}{ring}{t3}{t4}</g>')
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------------------
# PROJE KARTLARI
# ---------------------------------------------------------------------------

CW, CH = 1200, 400
PX, PY, PW, PH = 650, 40, 510, 320  # illüstrasyon paneli


def slide(dx_dy_values, key_times, dur, spline=".22 1 .36 1"):
    vals = ";".join(f"{fmt(a)} {fmt(b)}" for a, b in dx_dy_values)
    kt = ";".join(fmt(t) for t in key_times)
    ks = ";".join([spline] * (len(dx_dy_values) - 1))
    return (f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="{ks}"/>')


def card(name, num, kind, title, desc, tag_list, illus, alt):
    d = Doc(CW, CH, title, alt)
    d.motion_css += RISE_CSS
    op, cl = frame(d)
    d.add(op)
    d.add(glow(d, PX + PW * .62, PY + PH * .45, 460, EMBER, .2))
    d.add(grain(d, .07))

    # metin sütunu
    x = 56
    d.add(up(section_label(d, num, kind, x, 74, size=14), .1))
    gh, _ = d.text("GITHUB", MONO, 13, PX - 70, 74, MUTED, ls=1.6, anchor="end")
    d.add(up(gh + arrow(PX - 62, 64.5, 9, EMBER, 1.6), .1))
    cid = d.uid("lc")
    d.defs.append(f'<clipPath id="{cid}"><rect x="0" y="80" width="{PX}" height="90"/></clipPath>')
    tg, _ = d.text(title, TITLE, 64, x - 3, 156, BONE, ls=-2.4, wrap=rise_wrap(.15, .035))
    d.add(f'<g clip-path="url(#{cid})">{tg}</g>')
    para, _n = d.paragraph(desc, SANS, 20, x, 206, PX - 150, 30, MUTED)
    d.add(up(para, .45))
    d.add(up(tags(d, tag_list, x, 308), .6))

    # illüstrasyon paneli
    pid = d.uid("pc")
    d.defs.append(f'<clipPath id="{pid}"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="18"/></clipPath>')
    d.add(f'<g class="up" style="animation-delay:.3s"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="18" '
          f'fill="{PANEL}" stroke="{LINE}"/><g clip-path="url(#{pid})">{illus(d)}</g></g>')
    d.add(cl)
    return name, d


def illus_openisland(d: Doc):
    wid = d.uid("wp")
    d.defs.append(f'<linearGradient id="{wid}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#2A1208"/>'
                  f'<stop offset=".55" stop-color="#140B08"/><stop offset="1" stop-color="#0B0B0D"/></linearGradient>')
    out = [f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="url(#{wid})"/>',
           glow(d, PX + 120, PY + PH, 300, EMBER, .28)]
    # menü çubuğu
    out.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="30" fill="#000" fill-opacity=".35"/>')
    out.append("".join(f'<rect x="{PX + 18 + i * 34}" y="{PY + 12}" width="{22 if i else 12}" height="6" rx="3" '
                       f'fill="{BONE}" fill-opacity="{.7 if i == 0 else .28}"/>' for i in range(4)))
    clock, _ = d.text("Sal 20:21", MONO, 11, PX + PW - 18, PY + 19.5, BONE, anchor="end")
    out.append(f'<g opacity=".7">{clock}</g>')
    # arka plandaki pencere
    wx, wy = PX + 70, PY + 120
    out.append(f'<rect x="{wx}" y="{wy}" width="250" height="150" rx="12" fill="{BG}" fill-opacity=".72" stroke="{LINE}"/>'
               + "".join(f'<circle cx="{wx + 16 + i * 13}" cy="{wy + 15}" r="4" fill="{DIM}"/>' for i in range(3))
               + "".join(f'<rect x="{wx + 18}" y="{wy + 40 + i * 20}" width="{[170, 120, 190, 90][i]}" height="7" rx="3.5" '
                         f'fill="{BONE}" fill-opacity=".09"/>' for i in range(4)))
    # dock
    dx = PX + PW / 2 - 130
    out.append(f'<rect x="{dx}" y="{PY + PH - 54}" width="260" height="42" rx="14" fill="#fff" fill-opacity=".07" stroke="#fff" stroke-opacity=".08"/>')
    for i in range(6):
        fill = EMBER if i == 2 else BONE
        op = .9 if i == 2 else .16
        out.append(f'<rect x="{dx + 12 + i * 41}" y="{PY + PH - 47}" width="30" height="28" rx="8" fill="{fill}" fill-opacity="{op}"/>')
    # ada
    out.append(f'<g transform="translate({PX + PW / 2} {PY + 6}) scale(1.15) translate({-(PX + PW / 2)} 0)">'
               + hero_island(d, PX + PW / 2, 0, "ŞİMDİ ÇALIYOR", "Gece Sürüşü  —  Lo-fi", .4) + "</g>")
    return "".join(out)


def illus_macrar(d: Doc):
    dur = 9
    x0, y0 = PX, PY
    out = [f'<rect x="{x0}" y="{y0}" width="{PW}" height="40" fill="{PANEL2}"/>',
           f'<path d="M{x0} {y0 + 40}h{PW}" stroke="{LINE}"/>']
    out += [f'<circle cx="{x0 + 20 + i * 15}" cy="{y0 + 20}" r="5" fill="{DIM}"/>' for i in range(3)]
    t, _ = d.text("proje-arsivi.rar", MONOB, 13, x0 + PW / 2, MONOB.baseline(y0 + 20, 13), BONE, anchor="middle")
    out.append(t)
    # format çipleri (sırayla vurgulanır)
    cx = x0 + PW - 18
    for i, f in enumerate(["7Z", "ZIP", "RAR"]):
        w = d.measure(f, MONOB, 11.5) + 16
        cx -= w
        on = [(2 - i) * 3, (2 - i) * 3 + 3]
        g, _ = d.text(f, MONOB, 11.5, cx + w / 2, MONOB.baseline(y0 + 20.5, 11.5), BONE, anchor="middle")
        out.append(f'<rect x="{fmt(cx)}" y="{y0 + 10}" width="{fmt(w)}" height="21" rx="6" fill="{EMBER}" opacity="0">'
                   f'{fade_window(on[0] + .1, on[1] - .1, dur, .3)}</rect>'
                   f'<rect x="{fmt(cx)}" y="{y0 + 10}" width="{fmt(w)}" height="21" rx="6" fill="none" stroke="{LINE}"/>{g}')
        cx -= 6
    # arama alanı + yazılan sorgu
    sy = y0 + 58
    out.append(f'<rect x="{x0 + 18}" y="{sy}" width="{PW - 36}" height="34" rx="9" fill="{BG}" stroke="{LINE}"/>'
               f'<circle cx="{x0 + 37}" cy="{sy + 16}" r="6" fill="none" stroke="{MUTED}" stroke-width="1.6"/>'
               f'<path d="M{x0 + 41.5} {sy + 20.5}l4.5 4.5" stroke="{MUTED}" stroke-width="1.6" stroke-linecap="round"/>')
    ph, _ = d.text("Arşivde ara", SANS, 15, x0 + 54, SANS.baseline(sy + 17, 15), DIM)
    out.append(f'<g>{smil("opacity", [1, 0, 1], [0, 1.0 / dur, 7.9 / dur], dur, discrete=True)}{ph}</g>')
    query = "rapor"
    items, qw, _ = d.glyphs(query, SANSM, 15, x0 + 54, SANSM.baseline(sy + 17, 15))
    for use, gx, i in items:
        on = 1.0 + i * .14
        out.append(f'<g fill="{BONE}" opacity="0">{smil("opacity", [0, 1, 0], [0, on / dur, 7.9 / dur], dur, discrete=True)}{use}</g>')
    caret_x = [x0 + 54 + d.measure(query[:i], SANSM, 15) + 1 for i in range(len(query) + 1)]
    kts = [0] + [(1.0 + i * .14) / dur for i in range(len(query))] + [7.9 / dur]
    out.append(f'<rect x="{caret_x[0]}" y="{sy + 9}" width="1.6" height="17" fill="{EMBER}" class="blink">'
               f'{smil("x", [caret_x[0]] + caret_x[1:] + [caret_x[0]], kts, dur, discrete=True)}</rect>')
    # satırlar
    rows = [("tasarim/", "—", True), ("rapor-final.pdf", "2,4 MB", False), ("sunum.key", "18,1 MB", False),
            ("veri-seti.csv", "640 KB", False), ("logo.svg", "12 KB", False), ("notlar.md", "4 KB", False)]
    ry0 = sy + 50
    for i, (n, size, folder) in enumerate(rows):
        ry = ry0 + i * 34
        hit = n.startswith("rapor")
        if hit:
            out.append(f'<rect x="{x0 + 10}" y="{ry - 4}" width="{PW - 20}" height="30" rx="8" fill="{EMBER}" fill-opacity=".14" '
                       f'stroke="{EMBER}" stroke-opacity=".5" opacity="0">{fade_window(1.9, 7.6, dur, .35)}</rect>')
        icon = (f'<path d="M{x0 + 26} {ry + 3.5}h7l3 3h10v12h-20z" fill="{EMBER}" fill-opacity=".85"/>' if folder else
                f'<path d="M{x0 + 28} {ry + 1.5}h10l5 5v14h-15z" fill="none" stroke="{MUTED}" stroke-width="1.4" stroke-linejoin="round"/>')
        nm, _ = d.text(n, SANS, 15, x0 + 56, SANS.baseline(ry + 11, 15), BONE)
        sz, _ = d.text(size, MONO, 13, x0 + PW - 28, MONO.baseline(ry + 11, 13), MUTED, anchor="end")
        dim = "" if hit else smil("opacity", [1, 1, .3, .3, 1, 1], [0, 1.9 / dur, 2.3 / dur, 7.4 / dur, 7.8 / dur, 1], dur, ".4 0 .2 1")
        out.append(f'<g>{dim}{icon}{nm}{sz}</g>')
        if i < len(rows) - 1:
            out.append(f'<path d="M{x0 + 18} {ry + 29}h{PW - 36}" stroke="{LINE}" stroke-opacity=".6"/>')
    return "".join(out)


def illus_unitakip(d: Doc):
    dur = 10
    x0, y0 = PX, PY
    h1, _ = d.text("Bu hafta", TITLE, 22, x0 + 24, y0 + 42, BONE)
    sync, sw = d.text("SENKRONİZE · 2 DK ÖNCE", MONO, 11.5, x0 + PW - 24, y0 + 38, MUTED, ls=1, anchor="end")
    out = [h1, sync, f'<circle cx="{fmt(x0 + PW - 24 - sw - 10)}" cy="{y0 + 34.5}" r="3.5" fill="{EMBER}" class="pulse"/>']
    rows = [("ÖDEV", "Veri Yapıları — Ödev 3", "2 gün", True),
            ("SINAV", "Ağ Temelleri — Vize", "28 Kas", False),
            ("NOT", "Yazılım Mühendisliği", "87", False),
            ("DUYURU", "Ders saati değişti", "bugün", False)]
    for i, (tag, title, meta, accent) in enumerate(rows):
        ry = y0 + 66 + i * 60
        on = .3 + i * .18
        chip_w = 74
        chip, _ = d.text(tag, MONOB, 11, x0 + 40 + chip_w / 2, MONOB.baseline(ry + 36, 11), BG if accent else BONE, ls=1, anchor="middle")
        tt, _ = d.text(title, SANSM, 16, x0 + 54 + chip_w, SANSM.baseline(ry + 36, 16), BONE)
        mt, _ = d.text(meta, MONO, 13, x0 + PW - 38, MONO.baseline(ry + 36, 13), EMBER if accent else MUTED, anchor="end")
        check = ""
        if i == 2:
            check = (f'<path d="M{x0 + PW - 82} {ry + 36}l5 5 9-10" fill="none" stroke="{EMBER}" stroke-width="2.2" '
                     f'stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
                     f'{smil("stroke-dashoffset", [1, 1, 0, 0, 1], [0, 3.4 / dur, 3.9 / dur, 9.2 / dur, 1], dur, ".4 0 .2 1")}</path>')
        out.append(
            f'<g opacity="0" transform="translate(0 14)">{smil("opacity", [0, 0, 1, 1, 0, 0], [0, on / dur, (on + .6) / dur, 9.2 / dur, 9.6 / dur, 1], dur)}'
            f'{slide([(0, 14), (0, 14), (0, 0), (0, 0)], [0, on / dur, (on + .7) / dur, 1], dur)}'
            f'<rect x="{x0 + 24}" y="{ry + 12}" width="{PW - 48}" height="48" rx="12" fill="{PANEL2}" stroke="{LINE}"/>'
            f'<rect x="{x0 + 40}" y="{ry + 25}" width="{fmt(chip_w)}" height="22" rx="7" '
            f'fill="{EMBER if accent else "none"}" stroke="{EMBER if accent else DIM}"/>{chip}{tt}{mt}{check}</g>')
    # Gmail bildirimi
    tx, ty, tw = x0 + PW - 304, y0 + 12, 290
    l1, _ = d.text("GMAIL · UNİTAKİP", MONO, 11, tx + 54, ty + 24, MUTED, ls=1)
    l2, _ = d.text("Yeni not açıklandı: 87/100", SANSM, 15, tx + 54, ty + 44, BONE)
    toast = (f'<rect x="{tx}" y="{ty}" width="{tw}" height="60" rx="16" fill="#000" stroke="#2E2E33"/>'
             f'<rect x="{tx + 12}" y="{ty + 12}" width="32" height="36" rx="10" fill="{EMBER}"/>'
             f'<path d="M{tx + 20} {ty + 22}h16v14h-16zM{tx + 20} {ty + 22}l8 7 8-7" fill="none" stroke="{BG}" '
             f'stroke-width="1.8" stroke-linejoin="round"/>{l1}{l2}')
    out.append(f'<g transform="translate(0 -90)">{slide([(0, -90), (0, -90), (0, 0), (0, 0), (0, -90), (0, -90)], [0, 3.2 / dur, 3.9 / dur, 7.6 / dur, 8.2 / dur, 1], dur)}{toast}</g>')
    return "".join(out)


CARDS = [
    ("card-openisland", "01", "MACOS · AÇIK KAYNAK", "OpenIsland",
     "MacBook ekranının üst kısmında medya kontrollerini, Pomodoro’yu, dosya rafını ve Dock "
     "önizlemelerini bir araya getiren açık kaynaklı macOS uygulaması.",
     ["Swift", "AppKit", "Core Animation"], illus_openisland),
    ("card-macrar", "02", "MACOS · ARŞİV", "MacRAR Plus",
     "RAR, ZIP ve 7z arşivleri için yerel macOS çalışma alanı. Quick Look, Finder eylemleri ve "
     "arşivi çıkarmadan içerik arama.",
     ["Swift", "macOS", "Quick Look"], illus_macrar),
    ("card-unitakip", "03", "WEB · OTOMASYON", "UniTakip",
     "Ders sitelerindeki ödev, sınav ve notları tek panelde toplayan kişisel takip uygulaması. "
     "Cloudflare üzerinde çalışır, değişiklikleri Gmail ile bildirir.",
     ["Python", "React", "Cloudflare Workers"], illus_unitakip),
]


def main():
    OUT.mkdir(exist_ok=True)
    jobs = [("hero", hero)] + [
        (c[0], (lambda c=c: card(c[0], c[1], c[2], c[3], c[4], c[5], c[6], f"{c[3]} — {c[4]}")[1]))
        for c in CARDS]
    for name, fn in jobs:
        doc = fn()
        svg = doc.render()
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"{name}.svg  {len(svg.encode()) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
