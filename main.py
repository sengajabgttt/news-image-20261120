"""news-image-20261120: one image summing up Friday 20 November 2026.

A Python 3.13 program, standard library only. It draws a 1024 x 1024
newspaper front page at run time and writes it to /output/entry.png.
Everything is drawn from the six stories baked into STORIES below, which
were researched from published reporting dated 20 November 2026: no
network, no clock and no randomness, so two runs write byte-identical
PNGs.

Page plan: a teal masthead naming the day, one wide lead panel for the
biggest story, four panels in two columns, and a wide closing panel.
Each panel carries a region kicker, a headline and one short factual
sentence. A footer line names the outlets the stories were reported by.
All lettering uses a small 5-by-7 bitmap font stored here as rows of
five bits (one integer per row, leftmost column in the highest bit),
scaled up; every word is uppercase so it stays legible when the judge
views the image at about 300 pixels across.

The six stories (all reported on Friday 20 November 2026):
1. DIPLOMACY: Trump, Xi and Putin issued a joint declaration after
   their first three-way meeting in Shenzhen, pledging dialogue on
   nuclear risks and reform of the United Nations.
2. UKRAINE: Russia fired more than 400 drones and 110 missiles at
   Ukraine; three bridges in Kyiv were hit, eight people were killed,
   and two missiles fell inside Poland.
3. MIDDLE EAST: the US Navy held its blockade of Iranian shipping
   while tankers caught fire after mine blasts in the Strait of Hormuz.
4. CLIMATE: COP31 negotiators in Antalya were deadlocked as a new
   draft dropped all mention of fossil fuels.
5. ASIA: a day after the World Court found Myanmar guilty of
   genocide against the Rohingya, Myanmar's government dismissed the
   ruling as unfair.
6. CULTURE: Rockstar said on Friday that Grand Theft Auto VI took a
   record $3.79 billion in retail sales on launch day, with about
   25 million copies sold.

How to run it outside the grader (the grader runs
`python3 -P -s /bot/main.py` with MAKEFUN_OUTPUT_DIR unset):
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib
from pathlib import Path

OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
PAGE_W, PAGE_H = 1024, 1024

# ------------------------------------------------------------------ font --
# Each glyph is seven rows of five bits, stored as seven integers from
# 0 to 31. Bit 4 is the leftmost column, bit 0 the rightmost.
# Letters A-Z, digits 0-9, and the punctuation the stories need.
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (14, 16, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 1, 14),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '"': (10, 10, 10, 0, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "+": (0, 4, 4, 14, 4, 4, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "$": (4, 15, 20, 14, 5, 30, 4),
}

# A few curly or accented marks that sometimes slip into story text.
FOLD = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00e9": "E", "\u00c9": "E"}


def tidy(text):
    """Uppercase text and fold any stray marks into plain ASCII."""
    return "".join(FOLD.get(ch, ch) for ch in text.upper())


# --------------------------------------------------------------- palette --
PAPER = (246, 243, 236)
CARD = (255, 255, 255)
INK = (24, 24, 24)
BODY = (58, 58, 58)
FAINT = (110, 110, 104)
TEAL = (13, 68, 68)
GOLD = (214, 164, 48)
EDGE = (198, 192, 180)


class Page:
    """An RGB canvas held as one flat bytearray, three bytes a pixel."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def fill(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + w), min(self.height, y + h)
        r, g, b = colour
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                at = base + (xx - x0) * 3
                self.pixels[at] = r
                self.pixels[at + 1] = g
                self.pixels[at + 2] = b

    def glyph(self, x, y, char, scale, colour):
        rows = GLYPHS.get(char, GLYPHS[" "])
        for row, bits in enumerate(rows):
            for col in range(5):
                if bits & (16 >> col):
                    self.fill(x + col * scale, y + row * scale,
                              scale, scale, colour)

    def line(self, x, y, text, scale, colour):
        cx = x
        for ch in tidy(text):
            self.glyph(cx, y, ch, scale, colour)
            cx += 6 * scale

    def line_width(self, text, scale):
        return max(0, len(tidy(text)) * 6 * scale - scale)

    def centred(self, y, text, scale, colour):
        self.line((self.width - self.line_width(text, scale)) // 2,
                  y, text, scale, colour)


def fold_lines(text, chars):
    """Split text into lines of at most `chars` characters, by words."""
    lines, current = [], ""
    for word in tidy(text).split(" "):
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= chars:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ------------------------------------------------------------------- png --
def encode_png(page):
    def chunk(kind, data):
        size = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return size + kind + data + crc

    header = struct.pack(">IIBBBBB", page.width, page.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = page.width * 3
    for y in range(page.height):
        raw.append(0)
        raw += page.pixels[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# --------------------------------------------------------------- stories --
# (kicker, accent colour, headline, one-sentence body)
STORIES = [
    ("DIPLOMACY", (38, 68, 120),
     "TRUMP, XI AND PUTIN ISSUE JOINT DECLARATION",
     "IN A JOINT DECLARATION AFTER THEIR FIRST THREE-WAY MEETING IN "
     "SHENZHEN, THE THREE LEADERS PLEDGED DIALOGUE ON NUCLEAR RISKS "
     "AND REFORM OF THE UNITED NATIONS."),
    ("UKRAINE", (178, 34, 34),
     "RUSSIAN STRIKES HIT KYIV AND SPILL INTO POLAND",
     "MORE THAN 400 DRONES AND 110 MISSILES HIT UKRAINE, KILLING "
     "EIGHT AND DAMAGING THREE KYIV BRIDGES; TWO MISSILES FELL IN "
     "POLAND."),
    ("MIDDLE EAST", (176, 112, 0),
     "TANKERS BURN AS GULF STANDOFF DEEPENS",
     "THE US NAVY HELD ITS BLOCKADE OF IRANIAN SHIPPING AS TANKERS "
     "CAUGHT FIRE AFTER MINE BLASTS IN THE STRAIT OF HORMUZ."),
    ("CLIMATE", (26, 120, 90),
     "COP31 TALKS STALL OVER FOSSIL FUELS",
     "TALKS IN ANTALYA STALLED AS A NEW DRAFT DROPPED ALL MENTION "
     "OF FOSSIL FUELS, WITH NO DEAL IN SIGHT."),
    ("ASIA", (96, 66, 138),
     "MYANMAR REJECTS GENOCIDE RULING",
     "A DAY AFTER THE WORLD COURT FOUND MYANMAR GUILTY OF GENOCIDE, "
     "ITS GOVERNMENT DISMISSED THE RULING AS UNFAIR."),
    ("CULTURE", (168, 40, 96),
     "GTA VI SMASHES LAUNCH SALES RECORDS",
     "ROCKSTAR SAID ON FRIDAY THAT THE GAME TOOK A RECORD $3.79 "
     "BILLION IN RETAIL SALES ON LAUNCH DAY, WITH ABOUT 25 MILLION "
     "COPIES SOLD."),
]


def frame(page, x, y, w, h, accent):
    """A white card with a grey border and a solid accent bar at left."""
    page.fill(x, y, w, h, CARD)
    page.fill(x, y, w, 2, EDGE)
    page.fill(x, y + h - 2, w, 2, EDGE)
    page.fill(x, y, 2, h, EDGE)
    page.fill(x + w - 2, y, 2, h, EDGE)
    page.fill(x + 2, y + 2, 10, h - 4, accent)


def draw_lead(page, x, y, w, h, story):
    kicker, accent, headline, body = story
    frame(page, x, y, w, h, accent)
    pad = 30
    page.line(x + pad, y + 22, kicker, 2, accent)
    head = fold_lines(headline, (w - pad - 22) // 24)
    hy = y + 52
    for row in head[:2]:
        page.line(x + pad, hy, row, 4, INK)
        hy += 34
    hy += 10
    for row in fold_lines(body, (w - pad - 22) // 12)[:3]:
        page.line(x + pad, hy, row, 2, BODY)
        hy += 18


def draw_card(page, x, y, w, h, story):
    kicker, accent, headline, body = story
    frame(page, x, y, w, h, accent)
    pad = 24
    page.line(x + pad, y + 18, kicker, 2, accent)
    head = fold_lines(headline, (w - pad - 16) // 18)
    hy = y + 46
    for row in head[:2]:
        page.line(x + pad, hy, row, 3, INK)
        hy += 25
    hy += 6
    for row in fold_lines(body, (w - pad - 16) // 12)[:4]:
        page.line(x + pad, hy, row, 2, BODY)
        hy += 17


def draw_wide(page, x, y, w, h, story):
    kicker, accent, headline, body = story
    frame(page, x, y, w, h, accent)
    pad = 30
    page.line(x + pad, y + 20, kicker, 2, accent)
    head = fold_lines(headline, (w - pad - 22) // 18)
    hy = y + 50
    for row in head[:1]:
        page.line(x + pad, hy, row, 3, INK)
        hy += 26
    hy += 8
    for row in fold_lines(body, (w - pad - 22) // 12)[:2]:
        page.line(x + pad, hy, row, 2, BODY)
        hy += 18


def render():
    page = Page(PAGE_W, PAGE_H, PAPER)
    # Masthead: teal band with the paper's name and the day it sums up.
    page.fill(16, 16, PAGE_W - 32, 118, TEAL)
    page.centred(40, "THE WORLD TODAY", 5, (255, 255, 255))
    page.centred(96, "FRIDAY, 20 NOVEMBER 2026", 3, GOLD)
    page.centred(146, "SIX STORIES THAT SHAPED THE DAY", 2, FAINT)
    # Lead story, full width.
    draw_lead(page, 24, 168, 976, 210, STORIES[0])
    # Four stories in two columns.
    card_w, card_h = 480, 196
    for i, story in enumerate(STORIES[1:5]):
        col, row = i % 2, i // 2
        draw_card(page, 24 + col * (card_w + 16),
                  392 + row * (card_h + 10), card_w, card_h, story)
    # Closing story, full width.
    draw_wide(page, 24, 804, 976, 190, STORIES[5])
    # Footer: the outlets the stories were reported by.
    page.centred(1004,
                 "SOURCES: REUTERS, WALL STREET JOURNAL, CNN, LE MONDE, "
                 "UN NEWS, THE TIMES", 2, FAINT)
    return page


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "entry.png").write_bytes(encode_png(render()))


if __name__ == "__main__":
    main()
