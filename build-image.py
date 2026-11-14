#!/usr/bin/env python3
"""Build news-image-01 entry.png: a newspaper front page summing up the world news
of Friday 13 November 2026. Drawn procedurally with PIL (DejaVu fonts) so every
letter is crisp and every fact is one reported that day.

Stories (all reported 13 Nov 2026, sources AP / Reuters / BBC / Guardian):
  LEAD  Ukraine fires nearly 1,200 drones at Russia (AP) — one of the war's
        biggest aerial attacks; US-Russia talks widen to European security.
  1     US military downs two Iranian drones headed for Bahrain; Iran claims
        a radar strike; IAEA flags uninspected Isfahan enrichment plant.
  2     FAA lifts nationwide US ground stop after a 4+ hour halt caused by a
        communications failure.
  3     Global Microsoft 365 outage enters its second day (Outlook, Teams,
        Copilot down since 12 Nov).
  4     Nvidia CEO Jensen Huang resigns; shares fall; Congress summons him
        to testify.
  5     Qatar and Turkey sign a mutual defence agreement in Istanbul.
  6     Taiwan calls China's large unannounced Pacific naval exercise
        intimidation.
  ALSO  IEA Q4 oil surplus forecast; measles ruling awaited in North America;
        Ebola cases pass 11,000; storms flood Gaza camps.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24  # outer margin

PAPER = (246, 241, 231)
INK = (20, 20, 22)
NAVY = (20, 36, 61)
NAVY2 = (28, 48, 78)
GOLD = (217, 164, 65)
RED = (178, 34, 34)
GREY = (90, 88, 82)
CARD = (255, 255, 255)
LINE = (200, 192, 175)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, spacing=4):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


# ---------- icons (flat, drawn with primitives) ----------
def icon_drone(d, cx, cy, s, color):
    # quadcopter: body + 4 arms + 4 rotors
    d.ellipse([cx - s * 0.28, cy - s * 0.16, cx + s * 0.28, cy + s * 0.16], fill=color)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        x, y = cx + dx * s * 0.42, cy + dy * s * 0.30
        d.line([cx, cy, x, y], fill=color, width=max(2, int(s * 0.06)))
        d.line([x - s * 0.16, y, x + s * 0.16, y], fill=color, width=max(3, int(s * 0.09)))


def icon_radar(d, cx, cy, s, color):
    for r in (0.42, 0.30, 0.18):
        d.arc([cx - s * r, cy - s * r, cx + s * r, cy + s * r],
              start=-60, end=30, fill=color, width=max(2, int(s * 0.05)))
    d.line([cx, cy, cx + s * 0.34, cy - s * 0.34], fill=color, width=max(2, int(s * 0.06)))
    d.ellipse([cx - s * 0.05, cy - s * 0.05, cx + s * 0.05, cy + s * 0.05], fill=color)
    d.ellipse([cx + s * 0.26, cy - s * 0.42, cx + s * 0.34, cy - s * 0.34], fill=color)


def icon_plane(d, cx, cy, s, color):
    # side silhouette of an airliner, nose right
    d.polygon([(cx - s * 0.45, cy), (cx + s * 0.30, cy - s * 0.10),
               (cx + s * 0.48, cy), (cx + s * 0.30, cy + s * 0.10)], fill=color)
    d.polygon([(cx - s * 0.05, cy - s * 0.08), (cx - s * 0.28, cy - s * 0.34),
               (cx - s * 0.12, cy - s * 0.06)], fill=color)
    d.polygon([(cx - s * 0.38, cy - s * 0.02), (cx - s * 0.48, cy - s * 0.26),
               (cx - s * 0.36, cy - s * 0.02)], fill=color)
    d.polygon([(cx + s * 0.05, cy + s * 0.06), (cx - s * 0.18, cy + s * 0.32),
               (cx - s * 0.02, cy + s * 0.06)], fill=color)


def icon_cloud_bolt(d, cx, cy, s, color):
    d.ellipse([cx - s * 0.42, cy - s * 0.28, cx - s * 0.02, cy + s * 0.12], fill=color)
    d.ellipse([cx - s * 0.14, cy - s * 0.40, cx + s * 0.30, cy + s * 0.06], fill=color)
    d.ellipse([cx + s * 0.10, cy - s * 0.22, cx + s * 0.44, cy + s * 0.12], fill=color)
    d.rectangle([cx - s * 0.36, cy - s * 0.02, cx + s * 0.40, cy + s * 0.14], fill=color)
    bolt = [(cx + s * 0.08, cy - s * 0.10), (cx - s * 0.10, cy + s * 0.22),
            (cx + s * 0.02, cy + s * 0.22), (cx - s * 0.06, cy + s * 0.44),
            (cx + s * 0.16, cy + s * 0.10), (cx + s * 0.04, cy + s * 0.10)]
    d.polygon(bolt, fill=(255, 255, 255))


def icon_chip(d, cx, cy, s, color):
    d.rectangle([cx - s * 0.26, cy - s * 0.26, cx + s * 0.26, cy + s * 0.26], fill=color)
    d.rectangle([cx - s * 0.12, cy - s * 0.12, cx + s * 0.12, cy + s * 0.12],
                fill=(255, 255, 255))
    for i in (-1, 0, 1):
        w = max(2, int(s * 0.07))
        d.rectangle([cx + i * s * 0.16 - w, cy - s * 0.42, cx + i * s * 0.16 + w, cy - s * 0.26], fill=color)
        d.rectangle([cx + i * s * 0.16 - w, cy + s * 0.26, cx + i * s * 0.16 + w, cy + s * 0.42], fill=color)
        d.rectangle([cx - s * 0.42, cy + i * s * 0.16 - w, cx - s * 0.26, cy + i * s * 0.16 + w], fill=color)
        d.rectangle([cx + s * 0.26, cy + i * s * 0.16 - w, cx + s * 0.42, cy + i * s * 0.16 + w], fill=color)


def icon_flags(d, cx, cy, s, color):
    # two small flags under a gold arc: pact
    # Qatar: maroon with white serrated band on the hoist side
    d.rectangle([cx - s * 0.46, cy - s * 0.22, cx - s * 0.04, cy + s * 0.22], fill=(140, 40, 60))
    d.rectangle([cx - s * 0.46, cy - s * 0.22, cx - s * 0.34, cy + s * 0.22], fill=(255, 255, 255))
    # Turkey: red with a white crescent (white disc + offset red disc)
    d.rectangle([cx + s * 0.04, cy - s * 0.22, cx + s * 0.46, cy + s * 0.22], fill=(200, 40, 40))
    d.ellipse([cx + s * 0.12, cy - s * 0.11, cx + s * 0.32, cy + s * 0.09], fill=(255, 255, 255))
    d.ellipse([cx + s * 0.18, cy - s * 0.09, cx + s * 0.36, cy + s * 0.07], fill=(200, 40, 40))
    d.ellipse([cx + s * 0.36, cy - s * 0.03, cx + s * 0.41, cy + s * 0.02], fill=(255, 255, 255))
    d.arc([cx - s * 0.50, cy - s * 0.46, cx + s * 0.50, cy + s * 0.10],
          start=200, end=340, fill=GOLD, width=max(3, int(s * 0.07)))


def icon_ship(d, cx, cy, s, color):
    d.polygon([(cx - s * 0.44, cy + s * 0.05), (cx + s * 0.44, cy + s * 0.05),
               (cx + s * 0.30, cy + s * 0.30), (cx - s * 0.30, cy + s * 0.30)], fill=color)
    d.rectangle([cx - s * 0.03, cy - s * 0.34, cx + s * 0.03, cy + s * 0.05], fill=color)
    d.polygon([(cx + s * 0.03, cy - s * 0.34), (cx + s * 0.30, cy - s * 0.10),
               (cx + s * 0.03, cy - s * 0.10)], fill=color)
    for i, yy in enumerate((0.38,)):
        d.arc([cx - s * 0.44, cy + s * yy - s * 0.06, cx - s * 0.10, cy + s * yy + s * 0.06],
              start=0, end=180, fill=color, width=max(2, int(s * 0.05)))
        d.arc([cx + s * 0.02, cy + s * yy - s * 0.06, cx + s * 0.36, cy + s * yy + s * 0.06],
              start=0, end=180, fill=color, width=max(2, int(s * 0.05)))


def burst(d, cx, cy, r, color):
    pts = []
    import math
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


# ---------- build ----------
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# Masthead
d.rectangle([M, M, W - M, M + 112], fill=NAVY)
mast = font(F_SERIF, 56)
title = "THE WORLD IN ONE DAY"
tw = d.textlength(title, font=mast)
d.text(((W - tw) / 2, M + 12), title, font=mast, fill=(255, 255, 255))
d.rectangle([M + 60, M + 78, W - M - 60, M + 80], fill=GOLD)
sub = font(F_SANS_B, 23)
date = "F R I D A Y  ·  1 3  N O V E M B E R  2 0 2 6"
dw = d.textlength(date, font=sub)
d.text(((W - dw) / 2, M + 86), date, font=sub, fill=GOLD)

# Lead story card
lx, ly, lw, lh = M, M + 124, W - 2 * M, 252
d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD, outline=LINE, width=2)
# illustration panel on the right
ix, iw = lx + lw - 300, 300
d.rectangle([ix, ly, lx + lw, ly + lh], fill=NAVY)
# dotted flight arc + drones + burst (burst kept clear of the caption below)
for i in range(9):
    t = i / 8
    x = ix + 35 + t * 200
    y = ly + 138 - 42 * (4 * t * (1 - t))
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(120, 150, 190))
icon_drone(d, ix + 70, ly + 72, 64, (255, 255, 255))
icon_drone(d, ix + 165, ly + 52, 46, (200, 215, 235))
icon_drone(d, ix + 235, ly + 100, 56, (235, 240, 248))
burst(d, ix + 250, ly + 178, 32, (232, 120, 40))
d.text((ix + 18, ly + lh - 34), "ONE OF THE WAR'S BIGGEST", font=font(F_SANS_B, 15), fill=(200, 215, 235))
d.text((ix + 18, ly + lh - 16), "AERIAL ATTACKS", font=font(F_SANS_B, 15), fill=(200, 215, 235))
# lead text
tx = lx + 22
d.text((tx, ly + 16), "THE WAR IN UKRAINE  —  LEAD STORY", font=font(F_SANS_B, 17), fill=RED)
head = font(F_SERIF, 43)
lines = wrap(d, "Ukraine fires nearly 1,200 drones at Russia", head, lw - iw - 44)
y = draw_lines(d, lines, tx, ly + 44, head, INK, spacing=2)
summ = font(F_SANS, 21)
slines = wrap(d, "One of the largest aerial attacks of the war overnight, as U.S.–Russia talks widen to European security and Europe agrees its team for the peace table.", summ, lw - iw - 44)
draw_lines(d, slines, tx, y + 8, summ, (60, 58, 52), spacing=3)

# Section label: text first, gold rule to its right, vertically centred on the text
sy = ly + lh + 14
lab = "THE DAY IN BRIEF"
lab_f = font(F_SANS_B, 19)
d.text((M, sy - 4), lab, font=lab_f, fill=NAVY)
lab_w = d.textlength(lab, font=lab_f)
d.rectangle([M + lab_w + 14, sy + 8, W - M, sy + 10], fill=GOLD)

# Grid of six cards, 2 cols x 3 rows
cards = [
    ("U.S. DOWNS TWO IRANIAN DRONES",
     "Drones headed for Bahrain intercepted; Iran claims a radar strike. IAEA flags an uninspected enrichment plant.",
     (178, 34, 34), icon_radar),
    ("FAA LIFTS U.S. GROUND STOP",
     "Flights resume after a halt of more than 4 hours from a communications failure.",
     (30, 90, 160), icon_plane),
    ("MICROSOFT OUTAGE, DAY TWO",
     "Outlook, Teams and Copilot still down worldwide; emergency calls and courts hit.",
     (14, 120, 120), icon_cloud_bolt),
    ("NVIDIA CHIEF RESIGNS",
     "Jensen Huang quits; shares fall; Congress summons him to testify.",
     (110, 70, 150), icon_chip),
    ("QATAR–TURKEY DEFENCE PACT",
     "Mutual defence deal signed in Istanbul as Israeli strikes hit southern Lebanon.",
     (40, 130, 70), icon_flags),
    ("CHINA'S PACIFIC DRILLS",
     "Taiwan calls a large unannounced naval exercise intimidation.",
     (200, 110, 20), icon_ship),
]
gx, gy = M, sy + 34
cw = (W - 2 * M - 12) // 2
ch = 148
for i, (headline, summary, accent, icon) in enumerate(cards):
    cx = gx + (i % 2) * (cw + 12)
    cy = gy + (i // 2) * (ch + 12)
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD, outline=LINE, width=2)
    d.rectangle([cx, cy, cx + cw, cy + 7], fill=accent)
    # icon disc
    icx, icy, r = cx + 52, cy + 78, 36
    d.ellipse([icx - r, icy - r, icx + r, icy + r], fill=accent)
    icon(d, icx, icy, 52, (255, 255, 255))
    tx2 = cx + 102
    hf = font(F_SANS_B, 24)
    hlines = wrap(d, headline, hf, cw - 118)
    y2 = draw_lines(d, hlines, tx2, cy + 18, hf, INK, spacing=1)
    sf = font(F_SANS, 18)
    slines = wrap(d, summary, sf, cw - 118)
    draw_lines(d, slines, tx2, y2 + 4, sf, (70, 68, 62), spacing=2)

# Bottom strip: also
by = gy + 3 * ch + 2 * 12 + 12
d.rectangle([M, by, W - M, by + 58], fill=NAVY)
bf = font(F_SANS_B, 19)
aline = "ALSO:  IEA sees a Q4 oil surplus  ·  Measles ruling awaited in North America"
aw = d.textlength(aline, font=bf)
d.text(((W - aw) / 2, by + 7), aline, font=bf, fill=(255, 255, 255))
bf2 = font(F_SANS, 18)
aline2 = "Ebola cases pass 11,000  ·  Storms flood Gaza camps, 106,000 people affected"
aw2 = d.textlength(aline2, font=bf2)
d.text(((W - aw2) / 2, by + 31), aline2, font=bf2, fill=(200, 215, 235))

# Footer
ff = font(F_SANS, 14)
foot = "Sources: Associated Press · Reuters · BBC · The Guardian  —  events of 13 November 2026"
fw = d.textlength(foot, font=ff)
d.text(((W - fw) / 2, by + 64), foot, font=ff, fill=GREY)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, "PNG", optimize=True)
print("saved", out, os.path.getsize(out), "bytes")
