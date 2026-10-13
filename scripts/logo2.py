#!/usr/bin/env python3
"""Square mark: llm in copper pipe letters, left to right.

Straight runs, elbows, couplings, and open mouths, on the cream field.
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
TEXT = "llm"
TRACK = 0.06
# Pipe and open mouths stick past the glyph box.
PAD = 72.0


def letter_size() -> float:
    by_width = (SIZE - PAD * 2) / measure(TEXT, 1.0, TRACK)
    by_height = SIZE - PAD * 2
    return min(by_width, by_height)


def render(path: Path, side: int = SIZE) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(surf)
    if side != SIZE:
        cr.scale(side / SIZE, side / SIZE)
    wash(cr, SIZE, SIZE)
    size = letter_size()
    tw = measure(TEXT, size, TRACK)
    draw_line(cr, TEXT, (SIZE - tw) / 2, (SIZE - size) / 2, size, TRACK)
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
