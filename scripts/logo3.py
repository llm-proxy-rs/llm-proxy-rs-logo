#!/usr/bin/env python3
"""Square mark: llm centered, a flat rustacean below.

Same copper pipe letters as logo 2. The word stays in the middle of the
square; the crab sits under it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipe_font import draw_line, measure, wash  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CRAB_SRC = Path("/home/packer/Downloads/rustacean-flat-happy.png")

SIZE = 1024
TEXT = "llm"
TRACK = 0.06
# Pipe and open mouths stick past the glyph box.
PAD = 48.0
CRAB_H = 210.0


def letter_size() -> float:
    # Word stays centered; size is set by width, not by the crab below.
    return (SIZE - PAD * 2) / measure(TEXT, 1.0, TRACK)


def crab(cr: cairo.Context, y: float, height: float) -> None:
    """Flat orange rustacean, centered under the word."""
    src = cairo.ImageSurface.create_from_png(str(CRAB_SRC))
    sw, sh = src.get_width(), src.get_height()
    scale = height / sh
    dw = sw * scale
    cr.save()
    cr.translate((SIZE - dw) / 2, y)
    cr.scale(scale, scale)
    cr.set_source_surface(src, 0, 0)
    cr.get_source().set_filter(cairo.FILTER_BEST)
    cr.paint()
    cr.restore()


def render(path: Path, side: int = SIZE) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(surf)
    if side != SIZE:
        cr.scale(side / SIZE, side / SIZE)
    wash(cr, SIZE, SIZE)
    size = letter_size()
    gap = 16.0
    y = (SIZE - size) / 2
    tw = measure(TEXT, size, TRACK)
    draw_line(cr, TEXT, (SIZE - tw) / 2, y, size, TRACK)
    room = SIZE - PAD - (y + size + gap)
    crab(cr, y + size + gap, min(CRAB_H, room))
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo3.png"
    render(full, SIZE)
    render(DOCS / "logo3-512.png", 512)
    print(f"{full} {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
