#!/usr/bin/env python3
"""Playing-card mark: a copper pipe in the middle.

The card is 248×338. This logo is that card only — no white border around it.

The field is a warm cream. One pipe frame, and a centered mark. The frame is
the same copper tube as the mark, bent around the card with round corners,
joined by a coupling on each side. The mark is a straight copper pipe:
constant width, dark edge, copper across the tube, and a highlight down the
lit side. An open mouth caps each end, clear of the frame, and the tube
stops in that mouth. A sleeve joins the two halves in the middle. The card
is symmetric, so it reads the same upside down.
"""

from __future__ import annotations

import math
from pathlib import Path

import cairo

CREAM = (0xFF / 255, 0xF9 / 255, 0xEF / 255)
COPPER = (0xC4 / 255, 0x7A / 255, 0x38 / 255)
COPPER_DARK = (0x5C / 255, 0x32 / 255, 0x16 / 255)
COPPER_MID = (0x9A / 255, 0x58 / 255, 0x28 / 255)
COPPER_LIGHT = (0xF0 / 255, 0xD0 / 255, 0xA8 / 255)
BRASS = (0xD8 / 255, 0xA8 / 255, 0x52 / 255)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# Playing card, 248×338. No white photo margin.
CARD_W = 248
CARD_H = 338
S = 1024
SCALE = S / CARD_W
W = S
H = round(CARD_H * SCALE)  # 1396


def _rrect(cr: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
    r = min(r, w / 2, h / 2)
    cr.new_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def card_field(cr: cairo.Context) -> None:
    """Warm cream field. Flat, no vignette."""
    cr.set_source_rgb(*CREAM)
    cr.paint()


def _stroke_tube(cr: cairo.Context, pw: float, draw, shade) -> None:
    """Dark edge, then copper fill. `shade` sets the fill source."""
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.set_line_width(pw + max(2.0, pw * 0.16))
    cr.set_source_rgb(*COPPER_DARK)
    draw()
    cr.stroke()
    cr.set_line_width(pw)
    shade()
    draw()
    cr.stroke()


def _side(cr: cairo.Context, x0: float, y0: float, x1: float, y1: float, pw: float) -> None:
    """One straight of the frame. Gradient runs across the tube."""
    radius = pw / 2
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    # Light from the upper left, same side as the center pipe.
    nx, ny = -dy / length, dx / length
    if nx * -1.0 + ny * -1.0 < 0:
        nx, ny = -nx, -ny

    def draw() -> None:
        cr.move_to(x0, y0)
        cr.line_to(x1, y1)

    def shade() -> None:
        g = cairo.LinearGradient(
            x0 - nx * radius, y0 - ny * radius, x0 + nx * radius, y0 + ny * radius
        )
        g.add_color_stop_rgb(0.00, *COPPER_DARK)
        g.add_color_stop_rgb(0.22, *COPPER_MID)
        g.add_color_stop_rgb(0.38, *COPPER_LIGHT)
        g.add_color_stop_rgb(0.52, *COPPER)
        g.add_color_stop_rgb(1.00, *COPPER_DARK)
        cr.set_source(g)

    _stroke_tube(cr, pw, draw, shade)
    cr.set_line_width(max(1.2, pw * 0.20))
    cr.set_source_rgba(*COPPER_LIGHT, 0.92)
    cr.move_to(x0 + nx * radius * 0.36, y0 + ny * radius * 0.36)
    cr.line_to(x1 + nx * radius * 0.36, y1 + ny * radius * 0.36)
    cr.stroke()


def _corner(
    cr: cairo.Context, cx: float, cy: float, r: float, a0: float, a1: float, pw: float
) -> None:
    """Round bend. Light from the upper left."""
    radius = pw / 2
    nx, ny = -0.72, -0.72
    nlen = math.hypot(nx, ny)
    nx, ny = nx / nlen, ny / nlen

    def draw() -> None:
        cr.new_path()
        cr.arc(cx, cy, r, a0, a1)

    def shade() -> None:
        g = cairo.LinearGradient(
            cx - nx * (r + radius),
            cy - ny * (r + radius),
            cx + nx * (r + radius),
            cy + ny * (r + radius),
        )
        g.add_color_stop_rgb(0.00, *COPPER_DARK)
        g.add_color_stop_rgb(0.28, *COPPER_MID)
        g.add_color_stop_rgb(0.42, *COPPER_LIGHT)
        g.add_color_stop_rgb(0.58, *COPPER)
        g.add_color_stop_rgb(1.00, *COPPER_DARK)
        cr.set_source(g)

    _stroke_tube(cr, pw, draw, shade)
    cr.set_line_width(max(1.2, pw * 0.20))
    cr.set_source_rgba(*COPPER_LIGHT, 0.88)
    cr.new_path()
    cr.arc(cx, cy, max(r - radius * 0.36, r * 0.55), a0, a1)
    cr.stroke()


def _coupling(cr: cairo.Context, x: float, y: float, along: tuple[float, float], pw: float) -> None:
    """Short collar on a frame run. Same fitting as the center sleeve, smaller.

    A closed loop of pipe has to be joined somewhere. Four couplings, one
    mid-side, are that joint. They also break the long highlight so the
    frame reads as pipe, not a printed rule.
    """
    ax, ay = along
    half = pw / 2
    body = half * 2 + 5 * SCALE
    lip = body + 7 * SCALE
    length = 13 * SCALE
    lip_t = 3.2 * SCALE
    # Body runs along the pipe. Across the pipe it is wider than the tube.
    px, py = -ay, ax

    def band(cx: float, cy: float, ww: float, ll: float) -> None:
        cr.save()
        cr.translate(cx, cy)
        cr.rotate(math.atan2(ay, ax))
        cr.set_source_rgb(*COPPER_DARK)
        cr.rectangle(-ll / 2 - 1.3 * SCALE, -ww / 2 - 1.3 * SCALE, ll + 2.6 * SCALE, ww + 2.6 * SCALE)
        cr.fill()
        g = cairo.LinearGradient(0, -ww / 2, 0, ww / 2)
        g.add_color_stop_rgb(0.00, *COPPER_DARK)
        g.add_color_stop_rgb(0.24, *COPPER_MID)
        g.add_color_stop_rgb(0.40, *COPPER_LIGHT)
        g.add_color_stop_rgb(0.60, *COPPER)
        g.add_color_stop_rgb(1.00, *COPPER_DARK)
        cr.set_source(g)
        cr.rectangle(-ll / 2, -ww / 2, ll, ww)
        cr.fill()
        cr.restore()

    band(x, y, body, length)
    band(x - ax * (length / 2 - lip_t / 2), y - ay * (length / 2 - lip_t / 2), lip, lip_t)
    band(x + ax * (length / 2 - lip_t / 2), y + ay * (length / 2 - lip_t / 2), lip, lip_t)
    cr.set_source_rgb(*BRASS)
    cr.set_line_width(max(1.4, 1.6 * SCALE))
    # Across the collar, not along it. A seam down the pipe reads as a scratch.
    cr.move_to(x - px * body * 0.30, y - py * body * 0.30)
    cr.line_to(x + px * body * 0.30, y + py * body * 0.30)
    cr.stroke()


def card_frame(cr: cairo.Context) -> None:
    """One copper pipe around the card. Same tube as the center mark.

    Centerline sits 5px in from the card
    edge, about 18px of tube. Four straights and four round bends, so it
    is a bent pipe, not a flat printed rule. A coupling mid-side joins it.
    """
    pw = 18.0 * SCALE
    m = 5 * SCALE + pw / 2
    radius = 18 * SCALE
    x0, y0 = m, m
    x1, y1 = W - m, H - m
    # Straights stop at the tangent, so the bend owns the corner.
    _side(cr, x0 + radius, y0, x1 - radius, y0, pw)
    _side(cr, x1, y0 + radius, x1, y1 - radius, pw)
    _side(cr, x1 - radius, y1, x0 + radius, y1, pw)
    _side(cr, x0, y1 - radius, x0, y0 + radius, pw)
    _corner(cr, x1 - radius, y0 + radius, radius, -math.pi / 2, 0, pw)
    _corner(cr, x1 - radius, y1 - radius, radius, 0, math.pi / 2, pw)
    _corner(cr, x0 + radius, y1 - radius, radius, math.pi / 2, math.pi, pw)
    _corner(cr, x0 + radius, y0 + radius, radius, math.pi, 3 * math.pi / 2, pw)
    _coupling(cr, (x0 + x1) / 2, y0, (1, 0), pw)
    _coupling(cr, x1, (y0 + y1) / 2, (0, 1), pw)
    _coupling(cr, (x0 + x1) / 2, y1, (1, 0), pw)
    _coupling(cr, x0, (y0 + y1) / 2, (0, 1), pw)


def _sleeve(cr: cairo.Context, x: float, y: float, pipe_half: float) -> None:
    """Connector on the center seam. A collar around the pipe, not a disc.

    Wider than the run by a lip, short along the pipe, so it reads as the
    fitting that joins the two halves.
    """
    body = pipe_half * 2 + 10 * SCALE
    lip = body + 14 * SCALE
    h = 22 * SCALE
    lip_h = 5.5 * SCALE
    y0 = y - h / 2

    def band(yy: float, hh: float, ww: float) -> None:
        cr.set_source_rgb(*COPPER_DARK)
        cr.rectangle(x - ww / 2 - 2.2 * SCALE, yy, ww + 4.4 * SCALE, hh)
        cr.fill()
        g = cairo.LinearGradient(x - ww / 2, 0, x + ww / 2, 0)
        g.add_color_stop_rgb(0.00, *COPPER_DARK)
        g.add_color_stop_rgb(0.24, *COPPER_MID)
        g.add_color_stop_rgb(0.40, *COPPER_LIGHT)
        g.add_color_stop_rgb(0.60, *COPPER)
        g.add_color_stop_rgb(1.00, *COPPER_DARK)
        cr.set_source(g)
        cr.rectangle(x - ww / 2, yy, ww, hh)
        cr.fill()

    band(y0, h, body)
    band(y0 - lip_h * 0.15, lip_h, lip)
    band(y0 + h - lip_h * 0.85, lip_h, lip)
    cr.set_source_rgb(*BRASS)
    cr.set_line_width(max(1.6, 2.4 * SCALE))
    cr.move_to(x - body * 0.34, y)
    cr.line_to(x + body * 0.34, y)
    cr.stroke()


def _run(cr: cairo.Context, x0: float, y0: float, x1: float, y1: float, pw: float) -> None:
    """Copper tube with a flat end.

    A round cap would stick out past the mouth. A butt end stops in the
    mouth, so the opening is the end of the pipe.
    """
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
    """Open copper mouth.

    Centered on the pipe end. No extra nudge outward, so the rim is the
    end of the tube and stays off the cream frame.
    """
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


def standpipe(cr: cairo.Context) -> None:
    """Straight copper runs, sleeve in the middle.

    Constant width, dark edge, copper gradient, highlight on the lit side.
    Two halves, so the sleeve sits on the seam. Each end stops in an open
    mouth. The mouth sits inside the pipe frame, clear of the tube.
    """
    cx = W / 2
    pw = 34.0 * SCALE
    along = 0.42 * pw * 0.98
    frame_inner = (5.0 + 18.0) * SCALE + 9.0 * SCALE
    gap = 12.0 * SCALE
    top = frame_inner + gap + along
    bot = H - top
    mid = (top + bot) / 2
    seam = 8.0 * SCALE
    _run(cr, cx, top, cx, mid - seam, pw)
    _run(cr, cx, mid + seam, cx, bot, pw)
    _sleeve(cr, cx, mid, pw / 2)
    _mouth(cr, cx, top, pw, 0, -1)
    _mouth(cr, cx, bot, pw, 0, 1)


def _fit(src: cairo.ImageSurface, width: int, height: int) -> cairo.ImageSurface:
    if src.get_width() == width and src.get_height() == height:
        return src
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ocr = cairo.Context(out)
    ocr.scale(width / src.get_width(), height / src.get_height())
    ocr.set_source_surface(src, 0, 0)
    ocr.get_source().set_filter(cairo.FILTER_BEST)
    ocr.paint()
    return out


def render(path: Path, width: int = W, height: int = H) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    card_field(cr)
    card_frame(cr)
    standpipe(cr)
    surf = _fit(surf, width, height)
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))


def render_circle(path: Path, size: int = 512) -> None:
    """Circle crop, taken from the middle of the card."""
    src = cairo.ImageSurface.create_from_png(str(DOCS / "logo.png"))
    side = src.get_width()
    y0 = (src.get_height() - side) / 2
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    cr = cairo.Context(surf)
    cr.scale(size / side, size / side)
    cr.arc(side / 2, side / 2, side / 2, 0, math.tau)
    cr.clip()
    cr.set_source_surface(src, 0, -y0)
    cr.get_source().set_filter(cairo.FILTER_BEST)
    cr.paint()
    surf.write_to_png(str(path))


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo.png"
    render(full, W, H)
    render(DOCS / "logo-512.png", 512, round(512 * CARD_H / CARD_W))
    render_circle(DOCS / "logo-circle.png", 512)
    print(f"{full} {W}x{H}")


if __name__ == "__main__":
    main()
