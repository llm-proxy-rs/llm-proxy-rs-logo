#!/usr/bin/env python3
"""Square mark: a trident of llm and a pipe, pointed up at the crab.

Same copper pipe letters as logo 4, same cream field, same flat rustacean.
The trident points up. llm is the head: the two l stems are the side prongs,
the m is the crossbar. The copper pipe is the center prong. It starts under llm, so it does not
pass through the word, and points up at the crab. proxy runs down that pipe.
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
    glyph,
    letter_width,
    measure,
    wash,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CRAB_SRC = Path("/home/packer/Downloads/rustacean-flat-happy.png")

SIZE = 1024
HEAD = "llm"
SHAFT = "proxy"
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


def crab(cr: cairo.Context, cx: float, y: float, height: float) -> float:
    """Flat orange rustacean, centered on cx. `height` is the opaque ink."""
    src = cairo.ImageSurface.create_from_png(str(CRAB_SRC))
    x0, y0, x1, _y1 = CRAB_INK
    ink_h = 236.0
    scale = height / ink_h
    dw = (x1 - x0) * scale
    cr.save()
    cr.translate(cx - dw / 2 - x0 * scale, y - y0 * scale)
    cr.scale(scale, scale)
    cr.set_source_surface(src, 0, 0)
    cr.get_source().set_filter(cairo.FILTER_BEST)
    cr.paint()
    cr.restore()
    return dw


def draw_vertical(cr: cairo.Context, text: str, cx: float, top: float, size: float) -> float:
    """Letters stacked down the pipe, each centered on cx. Returns the bottom."""
    y = top
    gap = size * 0.04
    for ch in text:
        if glyph(ch):
            w = letter_width(ch, size, 0.0)
            draw_line(cr, ch, cx - w / 2, y, size, 0.0)
            y += size + gap
    return y


def layout() -> dict[str, float]:
    """Trident pointing up: llm the head, pipe the center prong, crab the target."""
    margin = 22.0
    head = 210.0
    pw = 44.0
    shaft = 86.0
    crab_h = 150.0
    head_w = measure(HEAD, head, TRACK)
    pipe_x = SIZE / 2
    return {
        "margin": margin,
        "head": head,
        "pw": pw,
        "shaft": shaft,
        "crab_h": crab_h,
        "head_w": head_w,
        "pipe_x": pipe_x,
        "head_left": pipe_x - head_w / 2,
    }


def render(path: Path, side: int = SIZE) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(surf)
    if side != SIZE:
        cr.scale(side / SIZE, side / SIZE)
    wash(cr, SIZE, SIZE)
    box = layout()
    head = box["head"]
    pw = box["pw"]
    shaft = box["shaft"]
    crab_h = box["crab_h"]
    pipe_x = box["pipe_x"]
    margin = box["margin"]

    # Crab on top. The center prong aims at it.
    crab_y = margin
    crab(cr, pipe_x, crab_y, crab_h)

    # Head of the trident, under the crab. Side prongs are the l stems.
    head_y = crab_y + crab_h + 28.0
    draw_line(cr, HEAD, box["head_left"], head_y, head, TRACK)

    # Center prong starts under the word. The mouth stays clear of the m.
    pipe_top = head_y + head + pw * 0.55
    pipe_bot = SIZE - margin
    standpipe(cr, pipe_x, pipe_top, pipe_bot, pw)

    # proxy down the pipe, inside the shaft, clear of both mouths.
    letters_h = len(SHAFT) * shaft + (len(SHAFT) - 1) * shaft * 0.04
    room_top = pipe_top + pw * 0.7
    room_bot = pipe_bot - pw * 0.7
    shaft_top = room_top + max(0.0, (room_bot - room_top - letters_h) / 2)
    draw_vertical(cr, SHAFT, pipe_x, shaft_top, shaft)

    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo5.png"
    render(full, SIZE)
    render(DOCS / "logo5-512.png", 512)
    print(f"{full} {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
