#!/usr/bin/env python3
"""Compose the 24 November 2026 one-image front page.

Reads the five text-free panel pictures from ``panels/`` next to this file,
lays them out as a newspaper front page (masthead, two wide stories on top,
three stories below, source line at the bottom) and writes ``entry.png``
beside this file.

Run it from anywhere; it always resolves paths relative to this file.
Re-running it reproduces the same picture.
"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PANELS_DIR = HERE / "panels"
OUT_PATH = HERE / "entry.png"

DEJAVU = "/usr/share/fonts/truetype/dejavu"
BOLD_FACE = os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")
PLAIN_FACE = os.path.join(DEJAVU, "DejaVuSans.ttf")

# --- page furniture -------------------------------------------------------
PAGE = 1024                 # square page, pixels
EDGE = 12                   # cream border around everything
PHOTO_H = 233               # height of every picture strip
CAPTION_H = 167             # height of every navy text block
TEXT_PAD = 18               # text inset inside a caption block
# A line whose ink runs a hair past the text box is still fine: the side
# bearings of the face eat a few pixels, so the fit check below allows
# this much slack before it starts shrinking type.
BEARING_SLACK = 6

PAPER = (245, 241, 230)     # warm off-white page background
TOP_NAVY = (14, 34, 51)     # masthead band
CARD_NAVY = (18, 40, 61)    # story caption blocks
RULE_RED = (178, 34, 34)    # thin rule under the masthead
GOLD = (232, 182, 76)       # kickers and the small masthead line
WHITE = (255, 255, 255)
FOOT_GREY = (60, 60, 60)

DATE_LINE = "TUESDAY, 24 NOVEMBER 2026"
PAPER_NAME = "THE WORLD IN ONE IMAGE"
PAPER_SUB = "FIVE STORIES FROM AROUND THE WORLD"
SOURCE_LINE = "Sources: Reuters · SCMP · AP · ICBL · CNA — 24 November 2026"

# (picture file, focus point, kicker, headline lines, blurb lines)
# The focus point is where the crop window sits inside the source picture,
# as a fraction of the spare room: 0.5 is dead centre. Gaza is framed low
# to keep the street and the walking group; the rest sit near the middle.
TOP_STORIES = [
    (
        "gaza.webp",
        (0.5, 0.717),
        "MIDDLE EAST · GAZA",
        ["HAMAS SECURITY CHIEF", "KILLED IN GAZA STRIKE"],
        ["Naeem Abu Nahal among at least six killed,", "medics say"],
    ),
    (
        "zaporizhzhia.webp",
        (0.5, 0.501),
        "RUSSIA · UKRAINE",
        ["DEADLY OVERNIGHT STRIKE", "HITS ZAPORIZHZHIA"],
        ["2 killed, 40 wounded, incl. 4 children, in", "apartment hit"],
    ),
]
BOTTOM_STORIES = [
    (
        "nepal.webp",
        (0.474, 0.5),
        "SOUTH ASIA",
        ["INDIA GIVES NEPAL", "$1.62BN FLOOD AID"],
        ["Biggest aid package ever for", "Nepal after August floods"],
    ),
    (
        "landmines.webp",
        (0.481, 0.5),
        "HUMANITARIAN",
        ["LANDMINE TOLL", "HITS FIVE-YEAR HIGH"],
        ["6,929 killed or hurt in 2025;", "Myanmar worst, then Syria"],
    ),
    (
        "nvidia.webp",
        (0.481, 0.5),
        "TECH",
        ["NVIDIA BRINGS BACK", "JENSEN HUANG"],
        ["CEO reinstated less than two", "weeks after resigning"],
    ),
]

# Column x positions, measured off the finished page.
TOP_X = (12, 518)
TOP_W = 494
BOTTOM_X = (12, 349, 687)
BOTTOM_W = 325

# Cap-top y positions inside each caption block, relative to the block top.
# (kicker, first headline line, first blurb line). The gaps between a
# block's own lines grow with the type that was actually fitted: a headline
# line sits its size + 6 below the previous one, a blurb line size + 5.
TOP_TEXT = (15, 44, 111)
BOTTOM_TEXT = (15, 43, 115)


class TypeDrawer:
    """Hands out fonts and draws lines aligned by their ink top.

    Pillow draws from the ascender box, which sits a little above the cap
    height, so every helper here lines text up by the top of its actual
    ink instead. That keeps cap-tops exactly where the layout says they go,
    whatever the face's ascent is.
    """

    def __init__(self, canvas: ImageDraw.ImageDraw) -> None:
        self.canvas = canvas
        self._cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def font(self, face: str, size: int) -> ImageFont.FreeTypeFont:
        key = (face, size)
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(face, size)
        return self._cache[key]

    def ink_box(self, text: str, face: str, size: int) -> tuple[int, int, int, int]:
        return self.canvas.textbbox(
            (0, 0), text, font=self.font(face, size), anchor="la"
        )

    def ink_width(self, text: str, face: str, size: int) -> int:
        box = self.ink_box(text, face, size)
        return box[2] - box[0]

    def draw_at_ink_top(
        self, x: int, cap_top: int, text: str, face: str, size: int, fill: tuple[int, int, int]
    ) -> None:
        """Draw ``text`` so its left ink edge is ``x`` and its cap top is ``cap_top``."""
        box = self.ink_box(text, face, size)
        self.canvas.text(
            (x - box[0], cap_top - box[1]),
            text,
            font=self.font(face, size),
            fill=fill,
            anchor="la",
        )

    def draw_right_aligned(
        self, right: int, cap_top: int, text: str, face: str, size: int, fill: tuple[int, int, int]
    ) -> None:
        """Draw ``text`` so its right ink edge lands on ``right``."""
        box = self.ink_box(text, face, size)
        self.canvas.text(
            (right - box[2], cap_top - box[1]),
            text,
            font=self.font(face, size),
            fill=fill,
            anchor="la",
        )

    def draw_centred(
        self, centre: int, cap_top: int, text: str, face: str, size: int, fill: tuple[int, int, int]
    ) -> None:
        """Draw ``text`` centred on ``centre`` by its ink width."""
        box = self.ink_box(text, face, size)
        width = box[2] - box[0]
        self.canvas.text(
            (centre - width // 2 - box[0], cap_top - box[1]),
            text,
            font=self.font(face, size),
            fill=fill,
            anchor="la",
        )


def shrink_until_fits(
    typer: TypeDrawer,
    lines: list[str],
    face: str,
    start_size: int,
    max_width: int,
    floor_size: int = 12,
) -> int:
    """Largest size at which every line's ink fits inside ``max_width``.

    Steps down one point at a time from ``start_size``. Never goes below
    ``floor_size``; a line that still overflows there is drawn anyway rather
    than crashing the build, so a long headline can never silently vanish.
    """
    size = start_size
    while size > floor_size and any(
        typer.ink_width(line, face, size) > max_width for line in lines
    ):
        size -= 1
    return size


def cover_crop(
    picture: Image.Image, width: int, height: int, focus: tuple[float, float]
) -> Image.Image:
    """Crop ``picture`` to the ``width`` x ``height`` aspect around ``focus``.

    ``focus`` is (horizontal, vertical), each 0..1 across the spare room
    left after the crop; 0.5 in both directions is a dead-centre crop.
    """
    target = width / height
    src_w, src_h = picture.size
    if src_w / src_h > target:
        # Too wide: trim the sides, keep the full height.
        keep_w = int(src_h * target)
        left = round((src_w - keep_w) * focus[0])
        picture = picture.crop((left, 0, left + keep_w, src_h))
    else:
        # Too tall: trim top and bottom, keep the full width.
        keep_h = int(src_w / target)
        top = round((src_h - keep_h) * focus[1])
        picture = picture.crop((0, top, src_w, top + keep_h))
    return picture.resize((width, height), Image.LANCZOS)


def paint_masthead(page: Image.Image, typer: TypeDrawer) -> None:
    draw = ImageDraw.Draw(page)
    draw.rectangle([EDGE, EDGE, PAGE - EDGE, EDGE + 111], fill=TOP_NAVY)
    draw.rectangle([EDGE, EDGE + 112, PAGE - EDGE, EDGE + 118], fill=RULE_RED)
    typer.draw_at_ink_top(EDGE + 25, EDGE + 15, PAPER_NAME, BOLD_FACE, 22, GOLD)
    typer.draw_right_aligned(
        PAGE - EDGE - 27, EDGE + 19, PAPER_SUB, PLAIN_FACE, 21, WHITE
    )
    typer.draw_at_ink_top(EDGE + 25, EDGE + 44, DATE_LINE, BOLD_FACE, 56, WHITE)


def paint_card(
    page: Image.Image,
    typer: TypeDrawer,
    story: tuple[str, tuple[float, float], str, list[str], list[str]],
    x: int,
    photo_y: int,
    width: int,
    text_spec: tuple[int, int, int],
    headline_size: int,
    blurb_size: int,
) -> None:
    """One picture plus its navy caption block underneath."""
    picture_file, focus, kicker, headline, blurb = story
    caption_y = photo_y + PHOTO_H

    with Image.open(PANELS_DIR / picture_file) as shot:
        page.paste(
            cover_crop(shot.convert("RGB"), width, PHOTO_H, focus), (x, photo_y)
        )

    draw = ImageDraw.Draw(page)
    # A one-pixel white mat shows around the navy block on every side:
    # white slab first, navy slab inset by one pixel on top of it.
    draw.rectangle(
        [x, caption_y - 1, x + width, caption_y + CAPTION_H], fill=WHITE
    )
    draw.rectangle(
        [x + 1, caption_y, x + width - 1, caption_y + CAPTION_H - 1], fill=CARD_NAVY
    )

    text_x = x + TEXT_PAD
    inner_w = width - 2 * TEXT_PAD + BEARING_SLACK
    kick_top, head_top, blurb_top = text_spec

    kicker_size = shrink_until_fits(typer, [kicker], BOLD_FACE, 19, inner_w)
    typer.draw_at_ink_top(
        text_x, caption_y + kick_top, kicker, BOLD_FACE, kicker_size, GOLD
    )

    head_size = shrink_until_fits(typer, headline, BOLD_FACE, headline_size, inner_w)
    head_step = head_size + 6
    for i, line in enumerate(headline):
        typer.draw_at_ink_top(
            text_x,
            caption_y + head_top + i * head_step,
            line,
            BOLD_FACE,
            head_size,
            WHITE,
        )

    blurb_size = shrink_until_fits(typer, blurb, PLAIN_FACE, blurb_size, inner_w)
    blurb_step = blurb_size + 5
    for i, line in enumerate(blurb):
        typer.draw_at_ink_top(
            text_x,
            caption_y + blurb_top + i * blurb_step,
            line,
            PLAIN_FACE,
            blurb_size,
            WHITE,
        )


def build_page() -> Image.Image:
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    typer = TypeDrawer(ImageDraw.Draw(page))

    paint_masthead(page, typer)

    photo_top = EDGE + 130
    for story, x in zip(TOP_STORIES, TOP_X):
        paint_card(page, typer, story, x, photo_top, TOP_W, TOP_TEXT, 33, 21)

    photo_bottom = photo_top + PHOTO_H + CAPTION_H + 12
    for story, x in zip(BOTTOM_STORIES, BOTTOM_X):
        paint_card(page, typer, story, x, photo_bottom, BOTTOM_W, BOTTOM_TEXT, 26, 19)

    foot_size = shrink_until_fits(
        typer, [SOURCE_LINE], PLAIN_FACE, 17, PAGE - 2 * EDGE
    )
    typer.draw_centred(PAGE // 2, PAGE - 39, SOURCE_LINE, PLAIN_FACE, foot_size, FOOT_GREY)
    return page


def main() -> None:
    build_page().save(OUT_PATH)
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
