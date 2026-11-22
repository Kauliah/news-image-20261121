#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news broadsheet (1024x1024 PNG).

Six verified stories, one per panel: each panel has a small drawn pictogram,
a region/field kicker, a bold headline and a short self-contained sub-line.
The date is named in the masthead and every story is dated in the footer.
Written fresh for the 21 November 2026 edition.
"""

import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (246, 241, 229)
NAVY = (20, 33, 61)
NAVY_LIGHT = (159, 179, 217)
INK = (24, 33, 51)
SUB = (74, 74, 68)
PANEL = (255, 255, 255)
BORDER = (216, 208, 189)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_DATE = font("DejaVuSans-Bold.ttf", 66)
F_SUBLINE = font("DejaVuSans.ttf", 23)
F_KICKER = font("DejaVuSans-Bold.ttf", 19)
F_HEAD = font("DejaVuSans-Bold.ttf", 28)
F_BODY = font("DejaVuSans.ttf", 20)
F_FOOT = font("DejaVuSans.ttf", 21)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines fitting `width` pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_burst(d, cx, cy, r, color):
    """Starburst: explosion / missile strike."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(255, 255, 255))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def icon_building(d, x, y, s, color):
    """Apartment block with a broken, jagged top and a crack."""
    w, h = int(s * 0.62), s
    top = [(x, y + 18), (x + w * 0.25, y + 6), (x + w * 0.45, y + 20),
           (x + w * 0.62, y + 2), (x + w * 0.8, y + 16), (x + w, y + 8),
           (x + w, y + h), (x, y + h)]
    d.polygon(top, fill=color)
    for r in range(3):
        for c in range(2):
            wx = x + 10 + c * (w // 2)
            wy = y + 34 + r * 26
            d.rectangle([wx, wy, wx + 13, wy + 15], fill=(255, 255, 255))
    d.line([(x + w * 0.55, y + 30), (x + w * 0.42, y + 62),
            (x + w * 0.58, y + 92)], fill=(255, 255, 255), width=3)


def icon_cuffs(d, cx, cy, r, color):
    """Handcuffs: two rings joined by a short chain link."""
    for dx in (-r - 4, r + 4):
        d.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r],
                  outline=color, width=9)
        d.ellipse([cx + dx - r // 2, cy - r // 2,
                   cx + dx + r // 2, cy + r // 2], outline=color, width=4)
    d.line([(cx - r - 4, cy - r), (cx - 9, cy - r - 14)],
           fill=color, width=6)
    d.line([(cx + r + 4, cy - r), (cx + 9, cy - r - 14)],
           fill=color, width=6)
    d.ellipse([cx - 11, cy - r - 24, cx + 11, cy - r - 6],
              outline=color, width=5)


def icon_globe(d, cx, cy, r, color):
    """Globe with a leaf: climate talks."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=7)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=color, width=4)
    d.line([(cx - r, cy), (cx + r, cy)], fill=color, width=4)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2],
          start=200, end=340, fill=color, width=4)
    lx, ly = cx + r * 0.55, cy - r * 0.75
    d.pieslice([lx - 26, ly - 12, lx + 26, ly + 12], start=300, end=120,
               fill=(46, 125, 50))


def icon_chart(d, x, y, s, color):
    """Falling market chart with arrow."""
    d.line([(x, y + s), (x, y + 6)], fill=color, width=6)
    d.line([(x, y + s), (x + s, y + s)], fill=color, width=6)
    pts = [(x + 8, y + 26), (x + s * 0.38, y + 44),
           (x + s * 0.55, y + 34), (x + s * 0.82, y + 78)]
    d.line(pts, fill=color, width=7, joint="curve")
    ex, ey = pts[-1]
    d.polygon([(ex, ey + 16), (ex - 16, ey + 2), (ex + 2, ey - 12)],
              fill=color)


def icon_mosquito(d, cx, cy, s, color):
    """Mosquito: body, wings, legs, antennae."""
    d.ellipse([cx - s * 0.55, cy - s * 0.28, cx + s * 0.05, cy + s * 0.05],
              outline=color, width=5)
    d.ellipse([cx - s * 0.1, cy - s * 0.12, cx + s * 0.62, cy + s * 0.28],
              fill=color)
    d.line([(cx + s * 0.55, cy + s * 0.1), (cx + s * 0.85, cy - s * 0.05)],
           fill=color, width=5)
    for dx, dy in [(-0.3, 0.35), (0.0, 0.42), (0.3, 0.38)]:
        d.line([(cx + s * dx, cy + s * 0.2),
                (cx + s * (dx - 0.18), cy + s * 0.55)], fill=color, width=4)
    d.line([(cx - s * 0.5, cy - s * 0.2), (cx - s * 0.78, cy - s * 0.42)],
           fill=color, width=4)
    d.line([(cx - s * 0.5, cy - s * 0.2), (cx - s * 0.82, cy - s * 0.1)],
           fill=color, width=4)


ICONS = {
    "burst": icon_burst,
    "building": icon_building,
    "cuffs": icon_cuffs,
    "globe": icon_globe,
    "chart": icon_chart,
    "mosquito": icon_mosquito,
}

# ------------------------------------------------------------- the stories
# (kicker, headline, sub-line, accent colour, icon)
PANELS = [
    ("MIDDLE EAST  ·  WAR",
     "IRAN STRIKES US BASES IN BAHRAIN",
     "Tehran claims missiles and drones hit two US bases; Bahrain says "
     "a factory site burned and no one was hurt.",
     (178, 44, 36), "burst"),
    ("EUROPE  ·  WAR",
     "BOY, 7, AND PARAMEDIC KILLED IN KRYVYI RIH",
     "Overnight Russian strikes on Zelenskyy's hometown wound 60 and "
     "damage 25 apartment blocks.",
     (146, 74, 18), "building"),
    ("AMERICAS  ·  CRIME",
     "MEXICO CATCHES \u2018EL CHAPO ISIDRO\u2019",
     "FBI most-wanted cartel boss seized in Sinaloa; 11 killed as "
     "gunmen fight back.",
     (30, 80, 160), "cuffs"),
    ("WORLD  ·  CLIMATE",
     "COP31 IN OVERTIME, STILL NO DEAL",
     "Antalya talks run past deadline; the draft drops fossil fuels "
     "and the EU warns: good deal or none.",
     (34, 110, 60), "globe"),
    ("ECONOMY  ·  MARKETS",
     "AI ROUT PUTS S&P 500 IN CORRECTION",
     "S&P 500 falls 3.7% into correction; Nasdaq posts its worst week "
     "since 2020 and wipes out its 2026 gains.",
     (104, 52, 168), "chart"),
    ("SCIENCE  ·  HEALTH",
     "MOSQUITOES CUT DENGUE BY 69%",
     "Brazil trial of 5,700 children finds Wolbachia mosquitoes slash "
     "dengue and chikungunya infections.",
     (0, 118, 122), "mosquito"),
]


def draw_panel(d, x, y, w, h, panel):
    kicker, headline, sub, color, icon = panel
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=BORDER, width=2)
    d.rectangle([x, y, x + w, y + 7], fill=color)
    # pictogram, left column
    icx, icy = x + 66, y + 138
    if icon in ("burst", "globe", "mosquito"):
        ICONS[icon](d, icx, icy, 46, color)
    elif icon == "cuffs":
        ICONS[icon](d, icx, icy, 26, color)
    elif icon == "building":
        ICONS[icon](d, x + 30, y + 96, 92, color)
    elif icon == "chart":
        ICONS[icon](d, x + 22, y + 96, 92, color)
    # text, right column
    tx, tw = x + 140, w - 156
    d.text((tx, y + 24), kicker, font=F_KICKER, fill=color)
    lines = wrap(d, headline, F_HEAD, tw)
    hy = y + 52
    for line in lines:
        d.text((tx, hy), line, font=F_HEAD, fill=INK)
        hy += 35
    sy = hy + 10
    for line in wrap(d, sub, F_BODY, tw):
        d.text((tx, sy), line, font=F_BODY, fill=SUB)
        sy += 26


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # masthead
    d.rectangle([0, 0, W, 116], fill=NAVY)
    date = "21 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=F_DATE)) / 2, 12),
           date, font=F_DATE, fill=(255, 255, 255))
    sub = "S A T U R D A Y   \u00b7   T H E   W O R L D   I N   O N E   I M A G E"
    d.text(((W - d.textlength(sub, font=F_SUBLINE)) / 2, 82),
           sub, font=F_SUBLINE, fill=NAVY_LIGHT)
    # grid of six panels
    gx, gy, gap = 16, 130, 14
    pw = (W - 2 * gx - gap) // 2
    ph = 272
    for i, panel in enumerate(PANELS):
        px = gx + (i % 2) * (pw + gap)
        py = gy + (i // 2) * (ph + gap)
        draw_panel(d, px, py, pw, ph, panel)
    # footer
    foot = ("Every story above happened or was first reported "
            "on 21 November 2026.")
    d.text(((W - d.textlength(foot, font=F_FOOT)) / 2, 990),
           foot, font=F_FOOT, fill=SUB)
    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
