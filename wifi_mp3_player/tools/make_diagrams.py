#!/usr/bin/env python3
"""
make_diagrams.py - draws all the wiring pictures for the docs.

Every picture is made from ONE description of the breadboard (the WIRES and
PARTS lists below), so the pictures always agree with each other.
If you change the wiring, change it here and run:

    python make_diagrams.py

The SVG files are written to ../docs/images/
"""

import math
import os
from html import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "images")

# ---------------------------------------------------------------------------
# Breadboard geometry: rows 1..63 go from top to bottom, columns a..j go from
# left to right. The two power rails on each side are "-" (outer) and "+" (inner).
# ---------------------------------------------------------------------------
P = 14                      # distance between two holes, in pixels (0.1 inch)
COL = {"-L": -3, "+L": -2, "a": 0, "b": 1, "c": 2, "d": 3, "e": 4,
       "f": 7, "g": 8, "h": 9, "i": 10, "j": 11, "+R": 13, "-R": 14}
ROWS = 63

COLORS = {
    "red": ("#e53935", "#8e1c1a"), "black": ("#333333", "#000000"),
    "yellow": ("#fdd835", "#9a8200"), "green": ("#43a047", "#1b5e20"),
    "blue": ("#1e88e5", "#0d47a1"), "white": ("#f5f5f5", "#8a8a8a"),
    "purple": ("#8e24aa", "#4a148c"), "orange": ("#fb8c00", "#a85d00"),
}

# ---------------------------------------------------------------------------
# THE WIRING. Each wire: id, colour, from (row, column), to (row, column),
# bend (how far the drawn wire curves to the right, in pixels), step, label.
# ---------------------------------------------------------------------------
WIRES = [
    ("W1", "red", (1, "j"), (1, "+R"), 0, 2, "VIN → + rail (5 V)"),
    ("W2", "black", (2, "j"), (2, "-R"), 0, 2, "GND → − rail"),
    ("W3", "black", (50, "-L"), (50, "-R"), 0, 2, "connect the two − rails"),
    ("W4", "yellow", (6, "j"), (20, "j"), 26, 3, "D27 → amp LRC"),
    ("W5", "green", (7, "j"), (21, "j"), 38, 3, "D26 → amp BCLK"),
    ("W6", "blue", (8, "j"), (22, "j"), 50, 3, "D25 → amp DIN"),
    ("W7", "black", (25, "j"), (25, "-R"), 0, 3, "amp GND → − rail"),
    ("W8", "red", (26, "j"), (26, "+R"), 0, 3, "amp VIN → + rail (5 V)"),
    ("W9", "white", (10, "j"), (33, "j"), 78, 5, "D32 → PREV button"),
    ("W10", "black", (35, "a"), (35, "-L"), 0, 5, "PREV button → − rail"),
    ("W11", "white", (9, "j"), (39, "j"), 92, 5, "D33 → PLAY button"),
    ("W12", "black", (41, "a"), (41, "-L"), 0, 5, "PLAY button → − rail"),
    ("W13", "white", (5, "j"), (45, "j"), 106, 5, "D14 → NEXT button"),
    ("W14", "black", (47, "a"), (47, "-L"), 0, 5, "NEXT button → − rail"),
    ("W15", "black", (29, "j"), (29, "-R"), 0, 6, "knob leg 1 → − rail"),
    ("W16", "purple", (30, "j"), (12, "j"), 62, 6, "knob middle leg → D34"),
    ("W17", "orange", (31, "j"), (3, "j"), 120, 6, "knob leg 3 → D13 (3.3 V)"),
    # Step 7 (extra): the headphone DAC. The 3 sound wires take the same signals as the
    # amplifier, from the free holes next to it. Optional extras at the end of a wire:
    # where its number badge goes (0 = start, 1 = end), and a list of (row, column)
    # points the drawing passes through, so the wires don't lie on top of each other.
    ("W19", "black", (57, "-L"), (57, "f"), 0, 7, "− rail → DAC GND"),
    ("W20", "yellow", (20, "i"), (58, "f"), 0, 7, "amp LRC row → DAC WSEL", 0.30,
     [(21, 8.95), (49.5, 8.95), (51.5, 7.4), (58, 7.4)]),
    ("W21", "blue", (22, "i"), (59, "f"), 0, 7, "amp DIN row → DAC DIN", 0.48,
     [(23, 9.5), (49.5, 9.5), (51.5, 7.85), (59, 7.85)]),
    ("W22", "green", (21, "i"), (60, "f"), 0, 7, "amp BCLK row → DAC BCLK", 0.39,
     [(22, 10.05), (49.5, 10.05), (51.5, 8.3), (60, 8.3)]),
    # (W18 is listed last so it is drawn on top of the three sound wires it crosses)
    ("W18", "red", (51, "+R"), (55, "f"), 0, 7, "+ rail → DAC VIN (5 V)", 0.25, [(51, 9.0)]),
]

# ESP32 pins: row -> label, for the column-i side and the column-b side.
# (Board placed with the USB plug at the top, at row 1.)
ESP_RIGHT = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25",
             "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
ESP_LEFT = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5",
            "D18", "D19", "D21", "RX0", "TX0", "D22", "D23"]
USED_PINS = {"VIN", "GND", "D13", "D14", "D27", "D26", "D25", "D33", "D32", "D34"}
AMP_PINS = ["LRC", "BCLK", "DIN", "GAIN", "SD", "GND", "VIN"]   # rows 20..26 in column g
BUTTONS = [("PREV", 33), ("PLAY", 39), ("NEXT", 45)]           # legs in rows r and r+2
KNOB_ROW = 29                                                  # legs in f29, f30, f31
DAC_PINS = ["VIN", "3V0", "GND", "WSEL", "DIN", "BCLK", "Lout", "AGND", "Rout"]  # rows 55..63, column h
DAC_ROW = 55
DAC_USED = {"VIN", "GND", "WSEL", "DIN", "BCLK"}

STEPS = {
    1: ("Step 1: Place the ESP32", {"esp"}),
    2: ("Step 2: Power rails", set()),
    3: ("Step 3: The amplifier", {"amp"}),
    4: ("Step 4: The speaker", {"speaker"}),
    5: ("Step 5: The buttons", {"buttons"}),
    6: ("Step 6: The volume knob", {"knob"}),
    7: ("Step 7 (extra): Headphones", {"dac"}),
}

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
X0, Y0 = 230, 118           # pixel position of hole a1


def hx(col):
    return X0 + COL[col] * P if isinstance(col, str) else X0 + col * P


def hy(row):
    return Y0 + (row - 1) * P


def rail_has_hole(row):
    return row % 6 != 0     # rail holes come in groups of 5


class Svg:
    def __init__(self, width, height):
        self.w, self.h, self.items = width, height, []

    def add(self, s):
        self.items.append(s)

    def text(self, x, y, s, size=11, fill="#222", anchor="middle", weight="normal", family="sans-serif"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" font-family="{family}">{escape(s)}</text>')

    def rect(self, x, y, w, h, fill, stroke="none", rx=0, extra=""):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def circle(self, x, y, r, fill, stroke="none", sw=1, extra=""):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def line(self, x1, y1, x2, y2, stroke, sw=1, extra=""):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def path(self, d, stroke, sw=1, fill="none", extra=""):
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" {extra}/>')

    def save(self, name, title):
        body = "\n".join(self.items)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(title)}">\n'
               f'<title>{escape(title)}</title>\n'
               f'<rect width="100%" height="100%" fill="#ffffff"/>\n{body}\n</svg>\n')
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


def draw_board(svg, rows=ROWS, numbers=True):
    left, right = hx(-4) - 4, hx(15) + 4
    top, bottom = hy(0) - 6, hy(rows + 1) + 6
    svg.rect(left, top, right - left, bottom - top, "#f3f1ea", "#cfcab8", rx=8)
    # the gap in the middle
    svg.rect(hx(5) - 2, top + 6, 2 * P + 4, bottom - top - 12, "#e2ddcc", rx=3)
    # rail lines
    for x, color in ((hx(-3.6), "#1e63d6"), (hx(-1.4), "#d62828"), (hx(12.4), "#d62828"), (hx(14.6), "#1e63d6")):
        svg.line(x, top + 10, x, bottom - 10, color, 1.5)
    for col, sign, color in (("-L", "−", "#1e63d6"), ("+L", "+", "#d62828"),
                             ("+R", "+", "#d62828"), ("-R", "−", "#1e63d6")):
        svg.text(hx(col), top - 6, sign, 14, color, weight="bold")
    # holes
    for row in range(1, rows + 1):
        for col in "abcdefghij":
            svg.rect(hx(col) - 2.5, hy(row) - 2.5, 5, 5, "#4a4a4a", rx=1)
        if rail_has_hole(row):
            for col in ("-L", "+L", "+R", "-R"):
                svg.rect(hx(col) - 2.5, hy(row) - 2.5, 5, 5, "#4a4a4a", rx=1)
    # letters and numbers
    for col in "abcdefghij":
        svg.text(hx(col), hy(0) + 3, col, 9, "#8a8577")
        svg.text(hx(col), hy(rows + 1) + 3, col, 9, "#8a8577")
    if numbers:
        for row in range(1, rows + 1):
            if row == 1 or row % 5 == 0:
                svg.text(hx(-0.9), hy(row) + 3, str(row), 8, "#8a8577")
                svg.text(hx(11.9), hy(row) + 3, str(row), 8, "#8a8577")


def wire_points(w):
    (r1, c1), (r2, c2), bend = w[2], w[3], w[4]
    x1, y1, x2, y2 = hx(c1), hy(r1), hx(c2), hy(r2)
    if bend == 0:
        return (x1, y1), (x1, y1), (x2, y2), (x2, y2)
    return (x1, y1), (x1 + bend * 1.33, y1), (x2 + bend * 1.33, y2), (x2, y2)


def point_on(points, t):
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = points
    u = 1 - t
    return (u ** 3 * ax + 3 * u * u * t * bx + 3 * u * t * t * cx + t ** 3 * dx,
            u ** 3 * ay + 3 * u * u * t * by + 3 * u * t * t * cy + t ** 3 * dy)


def point_on_polyline(pts, t):
    lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    goal = t * sum(lengths)
    for (a, b), length in zip(zip(pts, pts[1:]), lengths):
        if goal <= length and length > 0:
            f = goal / length
            return a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])
        goal -= length
    return pts[-1]


def wire_path(w):
    """Returns the SVG path of a wire, and where its number badge goes."""
    t = w[7] if len(w) > 7 else 0.5
    if len(w) > 8:                       # a wire with "via" points: straight pieces
        pts = [(hx(w[2][1]), hy(w[2][0]))] + [(hx(c), hy(r)) for r, c in w[8]] + [(hx(w[3][1]), hy(w[3][0]))]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        return d, point_on_polyline(pts, t)
    p0, p1, p2, p3 = wire_points(w)
    if w[4] == 0:
        d = f"M{p0[0]:.1f},{p0[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f}"
    else:
        d = f"M{p0[0]:.1f},{p0[1]:.1f} C{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"
    return d, point_on((p0, p1, p2, p3), t)


def draw_wire(svg, w, highlight=False):
    d, _ = wire_path(w)
    fill, edge = COLORS[w[1]]
    if highlight:
        svg.path(d, "#ffd400", 13, extra='stroke-linecap="round" stroke-linejoin="round" opacity="0.55"')
    svg.path(d, edge, 6, extra='stroke-linecap="round" stroke-linejoin="round"')
    svg.path(d, fill, 4, extra='stroke-linecap="round" stroke-linejoin="round"')


def draw_wire_ends(svg, w):
    for r, c in (w[2], w[3]):
        svg.circle(hx(c), hy(r), 3.2, "#9e9e9e", "#555", 1)


def draw_badge(svg, w):
    wid, _, (r1, c1), (r2, c2), bend = w[:5]
    bx, by = wire_path(w)[1]
    if bend == 0 and len(w) <= 7:
        ends = {c1, c2}
        if ends & {"+R", "-R"} and not ends & {"+L", "-L"}:
            bx, by = hx(15.7), hy(r1)          # short wire on the right: number outside the board
        elif ends & {"+L", "-L"} and not ends & {"+R", "-R"}:
            bx, by = hx(-5.3), hy(r1)          # short wire on the left
        else:
            by -= 9
    svg.circle(bx, by, 9, "#ffffff", "#333", 1.2)
    svg.text(bx, by + 3.5, wid[1:], 9, "#111", weight="bold")


def highlight_box(svg, x, y, w, h):
    svg.rect(x - 4, y - 4, w + 8, h + 8, "none", "#f5b800", rx=6,
             extra='stroke-width="3" stroke-dasharray="6 4"')


def draw_esp(svg, highlight=False):
    x1, x2 = hx(0.3), hx(10.7)
    y1, y2 = hy(-1.0), hy(17.3)
    if highlight:
        highlight_box(svg, x1, y1 - 14, x2 - x1, y2 - y1 + 14)
    svg.rect(x1, y1, x2 - x1, y2 - y1, "#23232f", "#111", rx=4)
    # USB plug sticking out at the top
    svg.rect(hx(4.3), y1 - 14, hx(6.7) - hx(4.3), 18, "#b9bcc4", "#777", rx=2)
    svg.text(hx(5.5), y1 - 18, "USB", 9, "#555")
    # buttons on the board
    for x, label in ((hx(2.6), "EN"), (hx(8.4), "BOOT")):
        svg.rect(x - 6, hy(0.2) - 5, 12, 10, "#ddd", "#888", rx=2)
        svg.text(x, hy(0.2) - 8, label, 6.5, "#bbb")
    # the silver WiFi module with its antenna
    svg.rect(hx(3.4), hy(7.5), hx(7.6) - hx(3.4), hy(17.0) - hy(7.5), "#c9ccd3", "#8d9099", rx=2)
    svg.text(hx(5.5), hy(11.2), "ESP32", 13, "#333", weight="bold")
    svg.text(hx(5.5), hy(12.4), "WROOM-32", 8, "#444")
    zig = " ".join(f"L{hx(3.8 + k * 0.4):.1f},{hy(15.6 if k % 2 else 16.4):.1f}" for k in range(1, 9))
    svg.path(f"M{hx(3.8):.1f},{hy(16.4):.1f} {zig}", "#b07d2a", 1.6)
    svg.text(hx(5.5), hy(14.6), "antenna", 7, "#666")
    # pins + labels
    for i in range(15):
        row = i + 1
        for col, label, anchor, tx in (("i", ESP_RIGHT[i], "end", hx(9.45)), ("b", ESP_LEFT[i], "start", hx(1.55))):
            used = col == "i" and label in USED_PINS
            svg.rect(hx(col) - 3.5, hy(row) - 3.5, 7, 7, "#d4af37", "#7a5c00", rx=1)
            svg.text(tx, hy(row) + 3, label, 7.5, "#ffe066" if used else "#cfcfe0", anchor,
                         "bold" if used else "normal")


def draw_amp(svg, highlight=False):
    x1, x2 = hx(1.0), hx(8.6)
    y1, y2 = hy(19.3), hy(26.7)
    if highlight:
        highlight_box(svg, x1, y1, x2 - x1, y2 - y1)
    svg.rect(x1, y1, x2 - x1, y2 - y1, "#2f3f9e", "#16206b", rx=3)
    svg.rect(hx(3.6), hy(21.6), hx(5.6) - hx(3.6), hy(23.6) - hy(21.6), "#111", rx=1)
    svg.text(hx(4.6), hy(25.0), "MAX98357A", 7.5, "#ffffff", weight="bold")
    svg.text(hx(4.6), hy(25.9), "I2S amplifier", 6.5, "#cfd6ff")
    # speaker screw terminal (green block on the left edge)
    svg.rect(hx(0.4), hy(21.4), hx(2.2) - hx(0.4), hy(24.0) - hy(21.4), "#2e9d4a", "#1b5e20", rx=2)
    for row, sign in ((21.9, "+"), (23.4, "−")):
        svg.circle(hx(1.3), hy(row) + 2, 4.2, "#d0d0d0", "#666", 1)
        svg.line(hx(1.3) - 3, hy(row) + 2, hx(1.3) + 3, hy(row) + 2, "#555", 1.2)
        svg.text(hx(2.75), hy(row) + 5, sign, 10, "#ffffff", weight="bold")
    for i, label in enumerate(AMP_PINS):
        row = 20 + i
        svg.rect(hx("g") - 3.5, hy(row) - 3.5, 7, 7, "#d4af37", "#7a5c00", rx=1)
        svg.text(hx(7.45), hy(row) + 3, label, 7.5, "#ffe066" if label not in ("GAIN", "SD") else "#9aa3d6",
                 "end", "bold")


def draw_speaker(svg, highlight=False):
    cx, cy = 74, hy(30)
    if highlight:
        highlight_box(svg, cx - 52, cy - 44, 104, 102)
    svg.rect(cx - 46, cy - 38, 92, 76, "#2b2b2b", "#111", rx=10)
    svg.circle(cx, cy, 30, "#444", "#222", 2)
    svg.circle(cx, cy, 20, "#3a3a3a", "#666", 1.5)
    svg.circle(cx, cy, 7, "#555", "#777", 1)
    svg.text(cx, cy + 54, "speaker", 10, "#444")
    # two wires from the speaker to the screw terminal
    for dy, (fill, edge), row in ((-8, COLORS["red"], 21.9), (8, COLORS["black"], 23.4)):
        x2, y2 = hx(1.3), hy(row) + 2
        d = f"M{cx + 30:.1f},{cy + dy:.1f} C{cx + 80:.1f},{cy + dy:.1f} {x2 - 70:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
        if highlight:
            svg.path(d, "#ffd400", 11, extra='stroke-linecap="round" opacity="0.55"')
        svg.path(d, edge, 4.5, extra='stroke-linecap="round"')
        svg.path(d, fill, 2.8, extra='stroke-linecap="round"')


def draw_buttons(svg, highlight=False):
    for name, r in BUTTONS:
        x1, x2 = hx(4.3), hx(6.7)
        y1, y2 = hy(r - 0.3), hy(r + 2.3)
        if highlight:
            highlight_box(svg, x1, y1, x2 - x1, y2 - y1)
        for col in ("e", "f"):
            for row in (r, r + 2):
                svg.circle(hx(col), hy(row), 3, "#b0b0b0", "#555", 1)
        svg.rect(x1, y1, x2 - x1, y2 - y1, "#1d1d1d", "#000", rx=3)
        svg.circle(hx(5.5), hy(r + 1), 9, "#3b3b3b", "#000", 1.5)
        svg.rect(hx(2.0) - 19, hy(r + 1) - 8, 38, 15, "#ffffff", "#bbb", rx=4)
        svg.text(hx(2.0), hy(r + 1) + 4, name, 10, "#222", weight="bold")


def draw_knob(svg, highlight=False):
    r = KNOB_ROW
    x1, x2 = hx(5.4), hx(8.6)
    y1, y2 = hy(r - 0.6), hy(r + 2.6)
    if highlight:
        highlight_box(svg, x1, y1, x2 - x1, y2 - y1)
    svg.rect(x1, y1, x2 - x1, y2 - y1, "#1f5fb8", "#0d3a78", rx=3)
    svg.circle(hx(7), hy(r + 1), 15, "#f0f0f0", "#777", 1.5)
    svg.line(hx(7), hy(r + 1) - 11, hx(7), hy(r + 1) + 11, "#555", 3, 'stroke-linecap="round"')
    for k in range(3):
        svg.rect(hx("f") - 3.5, hy(r + k) - 3.5, 7, 7, "#d4af37", "#7a5c00", rx=1,
                 extra='opacity="0.9"')
    svg.rect(hx(2.0) - 19, hy(r + 1) - 8, 38, 15, "#ffffff", "#bbb", rx=4)
    svg.text(hx(2.0), hy(r + 1) + 4, "KNOB", 10, "#222", weight="bold")


def draw_dac(svg, highlight=False):
    """The UDA1334A headphone DAC: pins in column h, board hanging over the right edge."""
    x1, x2 = hx(8.5), hx(18.7)
    y1, y2 = hy(DAC_ROW - 2.9), hy(DAC_ROW + 11.9)
    jy2 = hy(DAC_ROW + 13.3)
    if highlight:
        highlight_box(svg, x1, y1, x2 - x1, jy2 - y1)
    svg.rect(x1, y1, x2 - x1, y2 - y1, "#6b2c91", "#3d1557", rx=4, extra='opacity="0.96"')
    for cx, cy in ((x1 + 9, y1 + 9), (x2 - 9, y1 + 9), (x1 + 9, y2 - 9), (x2 - 9, y2 - 9)):
        svg.circle(cx, cy, 5, "#f3f1ea", "#d9c27a", 2)
    svg.rect(hx(14.6), hy(DAC_ROW - 0.6), hx(16.6) - hx(14.6), hy(DAC_ROW + 1.6) - hy(DAC_ROW - 0.6), "#111", rx=1)
    svg.text(hx(14.3), hy(DAC_ROW + 4.2), "UDA1334A", 9, "#ffffff", weight="bold")
    svg.text(hx(14.3), hy(DAC_ROW + 5.3), "headphone DAC", 7.5, "#e6d4f2")
    # the headphone socket at the bottom, pointing away from the breadboard
    jx1, jx2 = hx(12.4), hx(15.6)
    svg.rect(jx1, hy(DAC_ROW + 7.6), jx2 - jx1, jy2 - hy(DAC_ROW + 7.6), "#1e1e1e", "#000", rx=2)
    svg.circle((jx1 + jx2) / 2, jy2 - 6, 5, "#555", "#999", 1.5)
    svg.text((jx1 + jx2) / 2, jy2 + 15, "🎧 headphones plug in here", 10, "#333")
    for i, label in enumerate(DAC_PINS):
        row = DAC_ROW + i
        used = label in DAC_USED
        svg.rect(hx("h") - 3.5, hy(row) - 3.5, 7, 7, "#d4af37", "#7a5c00", rx=1)
        svg.text(hx(9.55), hy(row) + 3, label, 7.5, "#ffe066" if used else "#c9b3d9", "start", "bold")


def breadboard_picture(step):
    """step = 1..7 draws the build up to that step; step = 0 draws the normal player (steps 1-6)."""
    svg = Svg(700, hy(ROWS + 1) + (110 if step == 7 else 40))
    final = step == 0
    title = "The complete wiring" if final else STEPS[step][0]
    svg.text(24, 30, title, 20, "#1f1d2b", "start", "bold")
    subtitle = ("17 wires. Numbers = wire numbers in the instructions." if final else
                "Optional. New parts and wires have a yellow glow. Numbers = wire numbers in the instructions."
                if step == 7 else
                "New parts and wires have a yellow glow. Numbers = wire numbers in the instructions.")
    svg.text(24, 52, subtitle, 11, "#666", "start")
    draw_board(svg)

    upto = 6 if final else step
    new = set() if final else STEPS[step][1]
    if upto >= 1:
        draw_esp(svg, "esp" in new)
    if upto >= 3:
        draw_amp(svg, "amp" in new)
    if upto >= 4:
        draw_speaker(svg, "speaker" in new)
    if upto >= 5:
        draw_buttons(svg, "buttons" in new)
    if upto >= 6:
        draw_knob(svg, "knob" in new)
    if upto >= 7:
        draw_dac(svg, "dac" in new)
    # short wires first, long curvy wires on top; then all hole markers and numbers on top of that
    wires = sorted([w for w in WIRES if w[5] <= upto], key=lambda w: w[4])
    for w in wires:
        draw_wire(svg, w, highlight=not final and w[5] == step)
    for w in wires:
        draw_wire_ends(svg, w)
    for w in wires:
        if final or w[5] == step:
            draw_badge(svg, w)
    name = "breadboard_full.svg" if final else f"breadboard_step{step}.svg"
    svg.save(name, title)


# ---------------------------------------------------------------------------
# How the holes are connected inside (for lesson 1)
# ---------------------------------------------------------------------------
def breadboard_inside():
    rows = 10
    svg = Svg(700, hy(rows + 1) + 60)
    svg.text(24, 30, "Inside a breadboard: which holes are connected?", 20, "#1f1d2b", "start", "bold")
    svg.text(24, 52, "Holes with the same coloured stripe are connected by a metal strip underneath.", 11, "#666", "start")
    draw_board(svg, rows=rows, numbers=True)
    palette = ["#ff8a65", "#4fc3f7", "#aed581", "#ba68c8", "#ffd54f"]
    for row in range(1, rows + 1):
        c = palette[(row - 1) % len(palette)]
        for c1, c2 in (("a", "e"), ("f", "j")):
            svg.rect(hx(c1) - 6, hy(row) - 4.5, hx(c2) - hx(c1) + 12, 9, c, rx=4, extra='opacity="0.55"')
    for col, color in (("-L", "#1e63d6"), ("+L", "#d62828"), ("+R", "#d62828"), ("-R", "#1e63d6")):
        svg.rect(hx(col) - 4.5, hy(1) - 6, 9, hy(rows) - hy(1) + 12, color, rx=4, extra='opacity="0.35"')
    tx = hx(15) + 24
    notes = [
        ("Rows: a-b-c-d-e are", "connected (5 holes)."),
        ("f-g-h-i-j are connected", "too, but NOT to a-e:"),
        ("the gap in the middle", "separates them."),
        ("", ""),
        ("Rails (+ and −) run the", "whole length of the board."),
        ("We use them for 5 V (+)", "and GND (−)."),
    ]
    y = hy(1)
    for a, b in notes:
        svg.text(tx, y, a, 12, "#333", "start")
        svg.text(tx, y + 15, b, 12, "#333", "start")
        y += 34
    svg.save("breadboard_inside.svg", "Inside a breadboard")


# ---------------------------------------------------------------------------
# Schematic: the same wiring, drawn as a "map" instead of a picture
# ---------------------------------------------------------------------------
def schematic():
    svg = Svg(760, 540)
    svg.text(24, 32, "Schematic: who is connected to whom", 20, "#1f1d2b", "start", "bold")
    svg.text(24, 52, "Every ⏚ symbol means GND. All GND points are connected together (the − rail).", 11, "#666", "start")

    def box(x, y, w, h, title, fill):
        svg.rect(x, y, w, h, fill, "#333", rx=8, extra='stroke-width="1.5"')
        svg.text(x + w / 2, y + 22, title, 14, "#111", weight="bold")

    def wire(points, color):
        fill, edge = COLORS[color]
        d = "M" + " L".join(f"{x},{y}" for x, y in points)
        svg.path(d, edge, 4.5, extra='stroke-linejoin="round" stroke-linecap="round"')
        svg.path(d, fill, 2.8, extra='stroke-linejoin="round" stroke-linecap="round"')

    def ground(x, y):
        """A ground symbol hanging below point (x, y)."""
        svg.line(x, y, x, y + 10, "#111", 2)
        for k, half in enumerate((10, 6.5, 3)):
            svg.line(x - half, y + 10 + k * 4, x + half, y + 10 + k * 4, "#111", 2)

    # ESP32
    ex, ey = 60, 80
    box(ex, ey, 150, 400, "ESP32", "#e8e6f7")
    pins = [("VIN", 120), ("GND", 160), ("D27", 210), ("D26", 235), ("D25", 260),
            ("D32", 310), ("D33", 340), ("D14", 370), ("D34", 420), ("D13", 450)]
    py = {}
    px = ex + 165
    for name, y in pins:
        svg.line(ex + 150, y, px, y, "#333", 2)
        svg.text(ex + 142, y + 4, name, 11, "#111", "end", "bold")
        py[name] = y
    svg.text(ex + 75, ey + 385, "USB = power", 10, "#666")

    # amplifier + speaker
    ax, ay = 470, 80
    box(ax, ay, 150, 200, "MAX98357A", "#dfe5ff")
    amp = {"VIN": 120, "GND": 160, "LRC": 210, "BCLK": 235, "DIN": 260}
    for name, y in amp.items():
        svg.line(ax - 15, y, ax, y, "#333", 2)
        svg.text(ax + 8, y + 4, name, 11, "#111", "start", "bold")
    wire([(px, py["VIN"]), (ax - 15, amp["VIN"])], "red")
    svg.text(340, py["VIN"] - 8, "5 V", 11, "#c62828", weight="bold")
    wire([(px, py["GND"]), (290, py["GND"])], "black")
    ground(290, py["GND"])
    wire([(ax - 15, amp["GND"]), (420, amp["GND"])], "black")
    ground(420, amp["GND"])
    for pin, apin, color in (("D27", "LRC", "yellow"), ("D26", "BCLK", "green"), ("D25", "DIN", "blue")):
        wire([(px, py[pin]), (ax - 15, amp[apin])], color)
    svg.text(340, 202, "I2S (digital sound)", 10, "#555")
    sx, sy = 660, 180
    svg.line(ax + 150, sy - 15, sx, sy - 15, "#e53935", 3)
    svg.line(ax + 150, sy + 15, sx, sy + 15, "#333", 3)
    svg.path(f"M{sx},{sy - 22} L{sx + 14},{sy - 22} L{sx + 34},{sy - 42} L{sx + 34},{sy + 42} L{sx + 14},{sy + 22} L{sx},{sy + 22} Z",
             "#333", 2, "#ddd")
    svg.text(sx + 18, sy + 62, "speaker", 11, "#333")

    # buttons: a switch, then GND
    for (pin, label) in (("D32", "PREV"), ("D33", "PLAY"), ("D14", "NEXT")):
        y = py[pin]
        x1 = 440
        wire([(px, y), (x1, y)], "white")
        svg.circle(x1, y, 3.5, "#fff", "#111", 1.5)
        svg.circle(x1 + 40, y, 3.5, "#fff", "#111", 1.5)
        svg.line(x1 + 2, y - 3, x1 + 38, y - 14, "#111", 2)
        svg.line(x1 + 20, y - 9, x1 + 20, y - 18, "#111", 1.5)
        svg.line(x1 + 14, y - 18, x1 + 26, y - 18, "#111", 2)
        svg.text(x1 + 62, y + 4, label, 10, "#333", "start", "bold")
        wire([(x1 + 44, y), (x1 + 54, y)], "black")
        ground(x1 + 54, y)
    svg.text(560, 345, "press = connect to GND", 10, "#666", "start")

    # knob (potentiometer): D13 (3.3 V) - resistor - GND, wiper -> D34
    rx0, ry = 440, py["D13"]
    wire([(px, ry), (rx0, ry)], "orange")
    svg.text(380, ry + 18, "3.3 V", 10, "#a85d00", weight="bold")
    pts = [f"M{rx0},{ry}"] + [f"L{rx0 + 10 + k * 8},{ry + (-7 if k % 2 == 0 else 7)}" for k in range(9)] + [f"L{rx0 + 90},{ry}"]
    svg.path(" ".join(pts), "#111", 2)
    wire([(rx0 + 90, ry), (rx0 + 110, ry)], "black")
    ground(rx0 + 110, ry)
    wire([(px, py["D34"]), (rx0 + 45, py["D34"]), (rx0 + 45, ry - 16)], "purple")
    svg.path(f"M{rx0 + 39},{ry - 19} L{rx0 + 45},{ry - 9} L{rx0 + 51},{ry - 19} Z", "#4a148c", 1.5, "#8e24aa")
    svg.text(rx0 + 45, ry + 30, "10 kΩ knob", 10, "#333")
    svg.save("schematic.svg", "Schematic")


# ---------------------------------------------------------------------------
# System overview: from MP3 file to sound
# ---------------------------------------------------------------------------
def system():
    svg = Svg(900, 330)
    svg.text(24, 32, "How the music travels", 20, "#1f1d2b", "start", "bold")

    def box(x, y, w, h, title, lines, fill):
        svg.rect(x, y, w, h, fill, "#333", rx=12, extra='stroke-width="1.5"')
        svg.text(x + w / 2, y + 26, title, 15, "#111", weight="bold")
        for i, s in enumerate(lines):
            svg.text(x + w / 2, y + 52 + i * 19, s, 12, "#333")

    def arrow(x1, y1, x2, y2, label, color="#333", above=True):
        svg.line(x1, y1, x2 - 10 if x2 > x1 else x2 + 10, y2, color, 2.5)
        d = 1 if x2 > x1 else -1
        svg.path(f"M{x2},{y2} L{x2 - 12 * d},{y2 - 6} L{x2 - 12 * d},{y2 + 6} Z", color, 1, color)
        svg.text((x1 + x2) / 2, y1 - 9 if above else y1 + 19, label, 11, color)

    box(24, 60, 250, 175, "💻 Laptop: web app", ["1. you pick an MP3", "2. browser decodes it", "3. 22050 numbers / second", "4. sends chunks of 1024", "    numbers (with credits)"], "#ece8ff")
    box(360, 60, 220, 175, "📶 ESP32", ["receives the chunks", "waiting room (buffer)", "0.75 s of sound", "sends numbers out", "at exactly the right speed"], "#fff4d6")
    box(650, 60, 110, 175, "🔊 Amp", ["numbers", "→ voltage", "(DAC +", "amplifier)"], "#dff4e4")
    svg.text(820, 152, "🔈", 40, "#111")
    svg.text(820, 190, "speaker", 11, "#333")

    arrow(274, 118, 360, 118, "WiFi: sound", "#6c4cff")
    arrow(360, 178, 274, 178, "credits, buttons", "#c25e00", above=False)
    arrow(580, 148, 650, 148, "I2S", "#1e88e5")
    arrow(760, 148, 800, 148, "", "#333")

    svg.text(470, 280, "Buttons and knob → ESP32 → web app (\"button next\", \"volume 60\")", 12, "#555")
    svg.text(470, 302, "The web app decides what to do, because it knows the playlist.", 12, "#555")
    svg.save("system.svg", "How the music travels")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for s in range(1, 8):
        breadboard_picture(s)
    breadboard_picture(0)
    breadboard_inside()
    schematic()
    system()
