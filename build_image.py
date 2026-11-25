#!/usr/bin/env python3
"""Build entry.png: a 1024x1024 front-page image summing up the world news
of Tuesday 24 November 2026.

Layout (all pixels, canvas 1024x1024):
  - navy masthead with the date "TUESDAY, 24 NOVEMBER 2026"
  - row 1: two wide panels (Gaza strike, Zaporizhzhia strike)
  - row 2: three panels (India-Nepal aid, landmine toll, Nvidia CEO)
  - footer line naming the news sources

Each panel is an AI-generated news-style photo (no text in it) on top and
a navy text block below it with a kicker, a short headline and one
description line. All text is drawn here with PIL; the panel photos carry
no text of their own.

Run:  python3 build_image.py
Writes: entry.png next to this script (PNG if it fits the 1 MiB cap,
otherwise JPEG bytes under the same entry.png name, which the rules allow).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(HERE, "panels")
OUT_PATH = os.path.join(HERE, "entry.png")

W = H = 1024
MARGIN = 12
GAP = 12
HEADER_H = 118
ROW_H = 400
FOOTER_H = 46
MAX_BYTES = 1_048_576

PAPER = (245, 241, 230)      # warm newspaper cream
NAVY = (14, 34, 51)          # masthead / text-block navy
NAVY_TEXT = (18, 40, 61)     # slightly lighter navy for text blocks
RED = (178, 34, 34)          # accent red
GOLD = (232, 182, 76)        # kicker gold on navy
WHITE = (255, 255, 255)
DESC_GREY = (215, 222, 232)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_crop(img, target_w, target_h, focus_y=0.5):
    """Crop + resize to exactly target_w x target_h, keeping the vertical
    focus point (0.0 = top of frame, 1.0 = bottom) inside the crop."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(target_w, round(src_w * scale))
    new_h = max(target_h, round(src_h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x0 = (new_w - target_w) // 2
    focus_px = int(new_h * focus_y)
    y0 = focus_px - int(target_h * focus_y)
    y0 = max(0, min(new_h - target_h, y0))
    return img.crop((x0, y0, x0 + target_w, y0 + target_h))


def fit_text(draw, text, path, size, max_width, max_lines=2, min_size=15):
    """Shrink the font until the wrapped text fits in max_lines lines.
    Returns (font, lines). Never silently drops words."""
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_width)


def fit_single_line(draw, text, path, size, max_width, min_size=20):
    """Shrink the font until the text fits on one line within max_width."""
    while size > min_size:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= max_width:
            return fnt
        size -= 1
    return font(path, min_size)


def draw_panel(canvas, x, y, w, h, image, kicker, headline, desc,
               headline_size, desc_size):
    """One news panel: photo on top, navy text block below."""
    img_h = 232
    text_h = h - img_h
    canvas.paste(image, (x, y))
    tx, ty = x, y + img_h
    d = ImageDraw.Draw(canvas)
    d.rectangle([tx, ty, tx + w, ty + text_h], fill=NAVY_TEXT)
    d.rectangle([tx, ty, tx + w, ty + text_h], outline=(255, 255, 255),
                width=1)
    pad = 16 if w > 400 else 14
    inner = w - 2 * pad
    # kicker
    kf = font(FONT_BOLD, 19)
    d.text((tx + pad, ty + 12), kicker, font=kf, fill=GOLD)
    # headline (auto-shrunk so every word fits in 2 lines)
    hf, lines = fit_text(d, headline, FONT_BOLD, headline_size, inner)
    hy = ty + 38
    for line in lines:
        d.text((tx + pad, hy), line, font=hf, fill=WHITE)
        hy += hf.size + 6
    # description (auto-shrunk so every word fits in 2 lines)
    df, dlines = fit_text(d, desc, FONT_REG, desc_size, inner)
    dy = ty + text_h - 8 - len(dlines) * (df.size + 5)
    for line in dlines:
        d.text((tx + pad, dy), line, font=df, fill=DESC_GREY)
        dy += df.size + 5


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)

    # ---- masthead ------------------------------------------------------
    d.rectangle([MARGIN, MARGIN, W - MARGIN, MARGIN + HEADER_H], fill=NAVY)
    d.rectangle([MARGIN, MARGIN + HEADER_H - 6, W - MARGIN,
                 MARGIN + HEADER_H], fill=RED)
    kick = font(FONT_BOLD, 22)
    d.text((MARGIN + 24, MARGIN + 10), "THE WORLD IN ONE IMAGE",
           font=kick, fill=GOLD)
    date_f = fit_single_line(d, "TUESDAY, 24 NOVEMBER 2026", FONT_BOLD, 66,
                             W - 2 * MARGIN - 48, min_size=36)
    d.text((MARGIN + 24, MARGIN + 34), "TUESDAY, 24 NOVEMBER 2026",
           font=date_f, fill=WHITE)
    sub_f = font(FONT_REG, 22)
    sub = "FIVE STORIES FROM AROUND THE WORLD"
    sw = d.textlength(sub, font=sub_f)
    d.text((W - MARGIN - 24 - sw, MARGIN + 14), sub, font=sub_f,
           fill=DESC_GREY)

    # ---- panels --------------------------------------------------------
    row1_y = MARGIN + HEADER_H + GAP
    row2_y = row1_y + ROW_H + GAP
    row1_w = (W - 2 * MARGIN - GAP) // 2            # 494
    row2_w = (W - 2 * MARGIN - 2 * GAP) // 3        # 325

    def load(name):
        path = os.path.join(PANELS, name)
        if not os.path.exists(path):
            sys.exit("missing panel image: " + path)
        return Image.open(path).convert("RGB")

    gaza = fit_crop(load("gaza.webp"), row1_w, 232, focus_y=0.72)
    zap = fit_crop(load("zaporizhzhia.webp"), row1_w, 232, focus_y=0.5)
    nepal = fit_crop(load("nepal.webp"), row2_w, 232, focus_y=0.5)
    mines = fit_crop(load("landmines.webp"), row2_w, 232, focus_y=0.5)
    nvidia = fit_crop(load("nvidia.webp"), row2_w, 232, focus_y=0.5)

    draw_panel(canvas, MARGIN, row1_y, row1_w, ROW_H, gaza,
               "MIDDLE EAST \u00b7 GAZA",
               "HAMAS SECURITY CHIEF KILLED IN GAZA STRIKE",
               "Naeem Abu Nahal among at least six killed, medics say",
               33, 21)
    draw_panel(canvas, MARGIN + row1_w + GAP, row1_y, row1_w, ROW_H, zap,
               "RUSSIA \u00b7 UKRAINE",
               "DEADLY OVERNIGHT STRIKE HITS ZAPORIZHZHIA",
               "2 killed, 40 wounded, incl. 4 children, in apartment hit",
               33, 21)
    draw_panel(canvas, MARGIN, row2_y, row2_w, ROW_H, nepal,
               "SOUTH ASIA",
               "INDIA GIVES NEPAL $1.62BN FLOOD AID",
               "Biggest aid package ever for Nepal after August floods",
               26, 19)
    draw_panel(canvas, MARGIN + row2_w + GAP, row2_y, row2_w + 1, ROW_H,
               mines,
               "HUMANITARIAN",
               "LANDMINE TOLL HITS FIVE-YEAR HIGH",
               "6,929 killed or hurt in 2025; Myanmar worst, then Syria",
               26, 19)
    draw_panel(canvas, W - MARGIN - row2_w, row2_y, row2_w, ROW_H, nvidia,
               "TECH",
               "NVIDIA BRINGS BACK JENSEN HUANG",
               "CEO reinstated less than two weeks after resigning",
               26, 19)

    # ---- footer --------------------------------------------------------
    foot = font(FONT_REG, 17)
    src = ("Sources: Reuters \u00b7 SCMP \u00b7 AP \u00b7 ICBL \u00b7 CNA  "
           "\u2014  24 November 2026")
    fw = d.textlength(src, font=foot)
    d.text(((W - fw) / 2, H - MARGIN - 30), src, font=foot, fill=(60, 60, 60))

    # ---- save: PNG if it fits, else JPEG bytes under the same name -----
    canvas.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    fmt = "PNG"
    if size > MAX_BYTES:
        for quality in (90, 85, 80, 75):
            canvas.save(OUT_PATH, "JPEG", quality=quality, optimize=True)
            size = os.path.getsize(OUT_PATH)
            fmt = "JPEG q%d" % quality
            if size <= MAX_BYTES:
                break
    print("wrote %s (%s, %d bytes, %dx%d)"
          % (OUT_PATH, fmt, size, W, H))
    if size > MAX_BYTES:
        sys.exit("entry.png still over the 1 MiB cap")


if __name__ == "__main__":
    main()
