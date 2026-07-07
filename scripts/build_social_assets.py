#!/usr/bin/env python3
"""Generate social sharing images for CaseBriefKit."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OG_PATH = ASSETS / "casebriefkit-og.png"
ICON_PATH = ASSETS / "casebriefkit-icon.png"

GREEN = "#1f765f"
INK = "#17211e"
BLUE = "#2b5f92"
MUTED = "#5d6965"
BORDER = "#ccd6d2"
PAPER = "#f7faf8"
LINE = "#e9f0ed"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def draw_round_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_icon() -> None:
    image = Image.new("RGB", (512, 512), GREEN)
    draw = ImageDraw.Draw(image)
    draw_round_rect(draw, (96, 96, 416, 416), 64, "#ffffff")
    mark = font(FONT_BOLD, 150)
    draw.text((256, 258), "CB", anchor="mm", font=mark, fill=GREEN)
    image.save(ICON_PATH)


def draw_preview_card(draw: ImageDraw.ImageDraw) -> None:
    draw_round_rect(draw, (670, 78, 1110, 550), 18, "#ffffff", BORDER, 2)
    title = font(FONT_BOLD, 36)
    small = font(FONT_REGULAR, 22)
    label = font(FONT_BOLD, 24)
    draw.text((718, 130), "Example v. Student", font=title, fill=INK)
    draw.text((718, 182), "Citation | Court | Course", font=small, fill=MUTED)
    y = 250
    for name, width_a, width_b in [
        ("Facts", 250, 180),
        ("Issue", 220, 170),
        ("Rule", 260, 180),
        ("Analysis", 250, 200),
        ("Holding", 240, 170),
    ]:
        draw.text((718, y - 6), name, font=label, fill=GREEN)
        draw_round_rect(draw, (850, y, 850 + width_a, y + 18), 9, "#edf4f1")
        draw_round_rect(draw, (850, y + 30, 850 + width_b, y + 48), 9, LINE)
        y += 60


def draw_og() -> None:
    image = Image.new("RGB", (1200, 630), "#f5f8f6")
    draw = ImageDraw.Draw(image)

    draw_round_rect(draw, (64, 70, 574, 560), 20, "#ffffff", BORDER, 2)
    draw.rectangle((64, 70, 574, 156), fill=GREEN)
    draw_round_rect(draw, (96, 98, 150, 152), 10, "#ffffff")
    draw.text((123, 125), "CB", anchor="mm", font=font(FONT_BOLD, 20), fill=GREEN)
    draw.text((170, 108), "CaseBriefKit", font=font(FONT_BOLD, 36), fill="#ffffff")

    draw.text((98, 208), "Free case brief", font=font(FONT_BOLD, 54), fill=INK)
    draw.text((98, 270), "template + maker", font=font(FONT_BOLD, 54), fill=INK)
    draw.text((100, 348), "FIRAC | IRAC | CREAC", font=font(FONT_BOLD, 34), fill=BLUE)
    draw.text((100, 414), "Copy to Word, Google Docs,", font=font(FONT_REGULAR, 29), fill=MUTED)
    draw.text((100, 452), "Markdown, or Obsidian.", font=font(FONT_REGULAR, 29), fill=MUTED)
    draw_round_rect(draw, (98, 500, 372, 552), 10, GREEN)
    draw.text((235, 526), "Educational study aid", anchor="mm", font=font(FONT_BOLD, 24), fill="#ffffff")

    draw_preview_card(draw)
    image.save(OG_PATH, quality=95)


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_icon()
    draw_og()
    print(f"wrote={ICON_PATH}")
    print(f"wrote={OG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
