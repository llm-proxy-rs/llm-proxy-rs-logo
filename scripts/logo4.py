#!/usr/bin/env python3
"""Square mark: llm on top, a copper pipe through the middle, proxy to the right.

Same copper pipe letters as logo 3, same cream field, same flat rustacean.
The pipe stands through the middle. llm sits above it, centered on the pipe.
To the right of the pipe, on that same level, proxy runs left to right, and
the crab sits after the pipe, under the word.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipe_font import (  # noqa: E402
    BRASS,
    COPPER,
    COPPER_DARK,
    COPPER_LIGHT,
    COPPER_MID,
    draw_line,
    measure,
    wash,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CRAB_SRC = Path("/home/packer/Downloads/rustacean-flat-happy.png")

SIZE = 1024
TOP = "llm"
SIDE = "proxy"
TRACK = 0.06
# Opaque ink in rustacean-flat-happy.png.
CRAB_INK = (4, 34, 453, 269)


def _run(cr: cairo.Context, x0: float, y0: float, x1: float, y1: float, pw: float) -> None:
    """Copper tube, butt ends, so the mouths own the openings."""
    radius = pw / 2
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    if nx * -1.0 + ny * -1.0 < 0:
        nx, ny = -nx, -ny
    g = cairo.LinearGradient(
        x0 - nx * radius, y0 - ny * radius, x0 + nx * radius, y0 + ny * radius
    )
    g.add_color_stop_rgb(0.00, *COPPER_DARK)
    g.add_color_stop_rgb(0.22, *COPPER_MID)
    g.add_color_stop_rgb(0.38, *COPPER_LIGHT)
    g.add_color_stop_rgb(0.52, *COPPER)
    g.add_color_stop_rgb(1.00, *COPPER_DARK)
    cr.set_line_cap(cairo.LINE_CAP_BUTT)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_width(pw + max(2.0, pw * 0.16))
    cr.set_source_rgb(*COPPER_DARK)
    cr.move_to(x0, y0)
    cr.line_to(x1, y1)
    cr.stroke()
    cr.set_line_width(pw)
    cr.set_source(g)
    cr.move_to(x0, y0)
    cr.line_to(x1, y1)
    cr.stroke()
    cr.set_line_width(max(1.2, pw * 0.20))
    cr.set_source_rgba(*COPPER_LIGHT, 0.92)
    cr.move_to(x0 + nx * radius * 0.36, y0 + ny * radius * 0.36)
    cr.line_to(x1 + nx * radius * 0.36, y1 + ny * radius * 0.36)
    cr.stroke()


def _mouth(cr: cairo.Context, x: float, y: float, pw: float, dx: float, dy: float) -> None:
    length = math.hypot(dx, dy) or 1.0
    dx, dy = dx / length, dy / length
    ang = math.atan2(dy, dx)
    r = pw * 0.98
    squash = 0.42
    cr.save()
    cr.translate(x, y)
    cr.rotate(ang)
    cr.scale(squash, 1.0)

    def ring(radius: float) -> None:
        cr.new_path()
        cr.arc(0, 0, radius, 0, math.tau)

    cr.set_source_rgb(*COPPER_DARK)
    ring(r)
    cr.fill()
    cr.set_source_rgb(*BRASS)
    ring(r * 0.90)
    cr.fill()
    cr.set_source_rgb(*COPPER)
    ring(r * 0.78)
    cr.fill()
    cr.set_source_rgb(*COPPER_MID)
    ring(r * 0.70)
    cr.fill()
    cr.set_source_rgb(0.18, 0.10, 0.07)
    ring(r * 0.52)
    cr.fill()
    cr.set_source_rgb(0.10, 0.06, 0.04)
    ring(r * 0.34)
    cr.fill()
    cr.set_source_rgba(*COPPER_LIGHT, 0.85)
    cr.new_path()
    cr.arc(-r * 0.18, -r * 0.42, r * 0.16, 0, math.tau)
    cr.fill()
    cr.set_source_rgba(1, 1, 1, 0.18)
    cr.new_path()
    cr.arc(-r * 0.08, -r * 0.12, r * 0.10, 0, math.tau)
    cr.fill()
    cr.restore()


def standpipe(cr: cairo.Context, x: float, top: float, bot: float, pw: float) -> None:
    """Vertical copper pipe. Mouths at both ends, tube stops in the mouth."""
    along = 0.42 * pw * 0.98
    _run(cr, x, top + along, x, bot - along, pw)
    _mouth(cr, x, top, pw, 0, -1)
    _mouth(cr, x, bot, pw, 0, 1)


def crab(cr: cairo.Context, x: float, y: float, height: float) -> float:
    """Flat orange rustacean. `height` is the opaque ink. Returns drawn width."""
    src = cairo.ImageSurface.create_from_png(str(CRAB_SRC))
    x0, y0, x1, _y1 = CRAB_INK
    ink_h = 236.0
    scale = height / ink_h
    cr.save()
    cr.translate(x - x0 * scale, y - y0 * scale)
    cr.scale(scale, scale)
    cr.set_source_surface(src, 0, 0)
    cr.get_source().set_filter(cairo.FILTER_BEST)
    cr.paint()
    cr.restore()
    return (x1 - x0) * scale


def layout() -> dict[str, float]:
    """Pipe in the middle. llm on it. proxy over the crab, level, to the right."""
    margin = 36.0
    top_size = 200.0
    pw = 52.0
    side_size = 118.0
    gap = 22.0
    top_w = measure(TOP, top_size, TRACK)
    side_w = measure(SIDE, side_size, TRACK)
    pipe_x = margin + top_size * 0.10 + top_w / 2
    side_left = pipe_x + pw * 1.15 + gap
    # Word fits the right half; the crab is centered under it.
    room = SIZE - margin - side_left
    while side_w + side_size * 0.16 > room and side_size > 72:
        side_size -= 2.0
        side_w = measure(SIDE, side_size, TRACK)
    crab_w = min(side_w * 0.72, room * 0.78)
    crab_h = crab_w / (450 / 236)
    return {
        "margin": margin,
        "top_size": top_size,
        "side_size": side_size,
        "crab_h": crab_h,
        "crab_w": crab_w,
        "pw": pw,
        "gap": gap,
        "pipe_x": pipe_x,
        "side_left": side_left,
        "top_w": top_w,
        "side_w": side_w,
    }


def render(path: Path, side: int = SIZE) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(surf)
    if side != SIZE:
        cr.scale(side / SIZE, side / SIZE)
    wash(cr, SIZE, SIZE)
    box = layout()
    top_size = box["top_size"]
    side_size = box["side_size"]
    crab_h = box["crab_h"]
    pw = box["pw"]
    pipe_x = box["pipe_x"]
    margin = box["margin"]

    top_y = margin
    draw_line(cr, TOP, pipe_x - box["top_w"] / 2, top_y, top_size, TRACK)

    pipe_top = top_y + top_size + 20.0
    pipe_bot = SIZE - margin - 8
    standpipe(cr, pipe_x, pipe_top, pipe_bot, pw)

    # Right of the pipe, sharing its level: proxy, then the crab under it.
    side_x = box["side_left"]
    block_h = side_size + box["gap"] * 1.4 + crab_h
    span = pipe_bot - pipe_top
    block_top = pipe_top + max(0.0, (span - block_h) / 2)
    draw_line(cr, SIDE, side_x, block_top, side_size, TRACK)
    crab_x = side_x + (box["side_w"] - box["crab_w"]) / 2
    crab(cr, crab_x, block_top + side_size + box["gap"] * 1.4, crab_h)

    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo4.png"
    render(full, SIZE)
    render(DOCS / "logo4-512.png", 512)
    print(f"{full} {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
