#!/usr/bin/env python3
"""Square mark: llm in copper pipe letters, stacked.

Straight runs, elbows, couplings, and open mouths, on the cream field.
One letter a line, so the word fills the square.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipe_font import draw_line, measure, wash  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

SIZE = 1024
LINES = ("l", "l", "m")
TRACK = 0.04
# Pipe and open mouths stick past the glyph box.
PAD = 56.0
GAP = 8.0


def letter_size() -> float:
    # Widest line sets the size. Three lines plus two gaps fill the rest.
    widest = max(measure(line, 1.0, TRACK) for line in LINES)
    by_width = (SIZE - PAD * 2) / widest
    by_height = (SIZE - PAD * 2 - GAP * (len(LINES) - 1)) / len(LINES)
    return min(by_width, by_height)


def render(path: Path, side: int = SIZE) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(surf)
    if side != SIZE:
        cr.scale(side / SIZE, side / SIZE)
    wash(cr, SIZE, SIZE)
    size = letter_size()
    block = size * len(LINES) + GAP * (len(LINES) - 1)
    y = (SIZE - block) / 2
    for line in LINES:
        tw = measure(line, size, TRACK)
        draw_line(cr, line, (SIZE - tw) / 2, y, size, TRACK)
        y += size + GAP
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo2.png"
    render(full, SIZE)
    render(DOCS / "logo2-512.png", 512)
    print(f"{full} {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
