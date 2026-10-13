#!/usr/bin/env python3
"""Copper pipe letters — straight runs, 90° elbows, couplings, flanges."""

from __future__ import annotations

import math
from dataclasses import dataclass

import cairo

CREAM = (0xFF / 255, 0xF9 / 255, 0xEF / 255)
COPPER = (0xC4 / 255, 0x7A / 255, 0x38 / 255)
COPPER_DARK = (0x5C / 255, 0x32 / 255, 0x16 / 255)
COPPER_MID = (0x9A / 255, 0x58 / 255, 0x28 / 255)
COPPER_LIGHT = (0xF0 / 255, 0xD0 / 255, 0xA8 / 255)
BRASS = (0xD8 / 255, 0xA8 / 255, 0x52 / 255)

# y down. x in [0, width], y in [0, 1], both scaled by letter size.
# S x0 y0 x1 y1     straight
# A cx cy r a0 a1   elbow / bend, cairo clockwise (y-down)
# N cx cy r a0 a1   counter-clockwise
# F x y             end flange
# C x y             coupling


@dataclass(frozen=True)
class Glyph:
    width: float
    parts: tuple[tuple, ...]


def G(*cmds: tuple) -> tuple[tuple, ...]:
    return cmds


GLYPHS: dict[str, Glyph] = {
    "A": Glyph(
        0.90,
        G(
            ("S", 0.12, 0.88, 0.12, 0.74),
            ("S", 0.12, 0.74, 0.45, 0.26),
            ("S", 0.45, 0.26, 0.45, 0.12),
            ("S", 0.45, 0.26, 0.78, 0.74),
            ("S", 0.78, 0.74, 0.78, 0.88),
            ("S", 0.28, 0.58, 0.62, 0.58),
            ("C", 0.12, 0.74),
            ("C", 0.45, 0.26),
            ("C", 0.78, 0.74),
            ("C", 0.45, 0.58),
            ("F", 0.12, 0.88),
            ("F", 0.78, 0.88),
            ("F", 0.45, 0.12),
        ),
    ),
    "B": Glyph(
        0.82,
        G(
            ("S", 0.20, 0.12, 0.20, 0.88),
            ("S", 0.20, 0.12, 0.46, 0.12),
            ("A", 0.46, 0.30, 0.18, -90, 90),
            ("S", 0.46, 0.48, 0.20, 0.48),
            ("S", 0.20, 0.50, 0.48, 0.50),
            ("A", 0.48, 0.69, 0.19, -90, 90),
            ("S", 0.48, 0.88, 0.20, 0.88),
            ("C", 0.20, 0.12),
            ("C", 0.20, 0.48),
            ("C", 0.20, 0.88),
            ("F", 0.20, 0.12),
            ("F", 0.20, 0.88),
        ),
    ),
    "C": Glyph(
        0.82,
        G(
            ("S", 0.74, 0.08, 0.74, 0.22),
            ("N", 0.50, 0.50, 0.36, -50, 50),
            ("S", 0.74, 0.78, 0.74, 0.92),
            ("C", 0.74, 0.22),
            ("C", 0.74, 0.78),
            ("F", 0.74, 0.08),
            ("F", 0.74, 0.92),
        ),
    ),
    "D": Glyph(
        0.88,
        G(
            ("S", 0.20, 0.14, 0.20, 0.86),
            ("S", 0.20, 0.14, 0.44, 0.14),
            ("A", 0.44, 0.50, 0.36, -90, 90),
            ("S", 0.44, 0.86, 0.20, 0.86),
            ("C", 0.20, 0.14),
            ("C", 0.20, 0.86),
            ("C", 0.44, 0.14),
            ("C", 0.44, 0.86),
            ("F", 0.20, 0.14),
            ("F", 0.20, 0.86),
        ),
    ),
    "E": Glyph(
        0.78,
        G(
            ("S", 0.20, 0.14, 0.20, 0.86),
            ("S", 0.20, 0.14, 0.74, 0.14),
            ("S", 0.20, 0.50, 0.60, 0.50),
            ("S", 0.20, 0.86, 0.74, 0.86),
            ("C", 0.20, 0.14),
            ("C", 0.20, 0.50),
            ("C", 0.20, 0.86),
            ("F", 0.74, 0.14),
            ("F", 0.60, 0.50),
            ("F", 0.74, 0.86),
        ),
    ),
    "F": Glyph(
        0.78,
        G(
            ("S", 0.20, 0.14, 0.20, 0.86),
            ("S", 0.20, 0.14, 0.74, 0.14),
            ("S", 0.20, 0.50, 0.60, 0.50),
            ("C", 0.20, 0.14),
            ("C", 0.20, 0.50),
            ("F", 0.74, 0.14),
            ("F", 0.60, 0.50),
            ("F", 0.20, 0.86),
        ),
    ),
    "G": Glyph(
        0.88,
        G(
            ("S", 0.74, 0.08, 0.74, 0.24),
            ("N", 0.48, 0.50, 0.36, -46, 90),
            ("S", 0.48, 0.86, 0.80, 0.86),
            ("S", 0.80, 0.86, 0.80, 0.50),
            ("S", 0.80, 0.50, 0.56, 0.50),
            ("C", 0.74, 0.24),
            ("C", 0.48, 0.86),
            ("C", 0.80, 0.86),
            ("C", 0.80, 0.50),
            ("F", 0.74, 0.08),
            ("F", 0.56, 0.50),
        ),
    ),
    "H": Glyph(
        0.86,
        G(
            ("S", 0.18, 0.12, 0.18, 0.88),
            ("S", 0.68, 0.12, 0.68, 0.88),
            ("S", 0.18, 0.50, 0.68, 0.50),
            ("C", 0.18, 0.50),
            ("C", 0.68, 0.50),
            ("F", 0.18, 0.12),
            ("F", 0.18, 0.88),
            ("F", 0.68, 0.12),
            ("F", 0.68, 0.88),
        ),
    ),
    "I": Glyph(
        0.56,
        G(
            ("S", 0.10, 0.14, 0.46, 0.14),
            ("S", 0.28, 0.14, 0.28, 0.86),
            ("S", 0.10, 0.86, 0.46, 0.86),
            ("C", 0.28, 0.14),
            ("C", 0.28, 0.86),
            ("F", 0.10, 0.14),
            ("F", 0.46, 0.14),
            ("F", 0.10, 0.86),
            ("F", 0.46, 0.86),
        ),
    ),
    "K": Glyph(
        0.84,
        G(
            ("S", 0.18, 0.12, 0.18, 0.88),
            ("S", 0.18, 0.50, 0.72, 0.12),
            ("S", 0.32, 0.42, 0.74, 0.88),
            ("C", 0.18, 0.50),
            ("C", 0.32, 0.42),
            ("F", 0.18, 0.12),
            ("F", 0.18, 0.88),
            ("F", 0.72, 0.12),
            ("F", 0.74, 0.88),
        ),
    ),
    "L": Glyph(
        0.76,
        G(
            ("S", 0.20, 0.12, 0.20, 0.70),
            ("N", 0.36, 0.70, 0.16, 180, 90),
            ("S", 0.36, 0.86, 0.74, 0.86),
            ("F", 0.20, 0.12),
            ("F", 0.74, 0.86),
        ),
    ),
    "M": Glyph(
        1.12,
        G(
            ("S", 0.12, 0.88, 0.12, 0.14),
            ("S", 0.12, 0.14, 0.50, 0.68),
            ("S", 0.50, 0.68, 0.88, 0.14),
            ("S", 0.88, 0.14, 0.88, 0.88),
            ("C", 0.12, 0.14),
            ("C", 0.50, 0.68),
            ("C", 0.88, 0.14),
            ("F", 0.12, 0.88),
            ("F", 0.88, 0.88),
        ),
    ),
    "N": Glyph(
        0.90,
        G(
            ("S", 0.16, 0.88, 0.16, 0.14),
            ("S", 0.16, 0.14, 0.74, 0.86),
            ("S", 0.74, 0.86, 0.74, 0.12),
            ("C", 0.16, 0.14),
            ("C", 0.74, 0.86),
            ("F", 0.16, 0.88),
            ("F", 0.74, 0.12),
        ),
    ),
    "O": Glyph(
        0.90,
        G(
            ("A", 0.45, 0.50, 0.36, 90, 270),
            ("A", 0.45, 0.50, 0.36, -90, 90),
            ("C", 0.45, 0.14),
            ("C", 0.45, 0.86),
        ),
    ),
    "P": Glyph(
        0.80,
        G(
            ("S", 0.20, 0.12, 0.20, 0.88),
            ("S", 0.20, 0.12, 0.46, 0.12),
            ("A", 0.46, 0.32, 0.20, -90, 90),
            ("S", 0.46, 0.52, 0.20, 0.52),
            ("C", 0.20, 0.12),
            ("C", 0.20, 0.52),
            ("F", 0.20, 0.88),
        ),
    ),
    "R": Glyph(
        0.86,
        G(
            ("S", 0.20, 0.12, 0.20, 0.88),
            ("S", 0.20, 0.12, 0.46, 0.12),
            ("A", 0.46, 0.32, 0.20, -90, 90),
            ("S", 0.46, 0.52, 0.20, 0.52),
            ("S", 0.40, 0.52, 0.70, 0.70),
            ("S", 0.70, 0.70, 0.70, 0.88),
            ("C", 0.20, 0.12),
            ("C", 0.20, 0.52),
            ("C", 0.40, 0.52),
            ("C", 0.70, 0.70),
            ("F", 0.20, 0.88),
            ("F", 0.70, 0.88),
        ),
    ),
    "S": Glyph(
        0.82,
        G(
            ("S", 0.74, 0.16, 0.36, 0.16),
            ("N", 0.36, 0.30, 0.14, 270, 180),
            ("S", 0.22, 0.30, 0.22, 0.36),
            ("N", 0.36, 0.36, 0.14, 180, 90),
            ("S", 0.36, 0.50, 0.60, 0.50),
            ("A", 0.60, 0.64, 0.14, 270, 360),
            ("S", 0.74, 0.64, 0.74, 0.70),
            ("A", 0.60, 0.70, 0.14, 0, 90),
            ("S", 0.60, 0.84, 0.22, 0.84),
            ("C", 0.36, 0.16),
            ("C", 0.22, 0.30),
            ("C", 0.36, 0.50),
            ("C", 0.60, 0.50),
            ("C", 0.60, 0.84),
            ("F", 0.74, 0.16),
            ("F", 0.22, 0.84),
        ),
    ),
    "T": Glyph(
        0.86,
        G(
            ("S", 0.08, 0.14, 0.78, 0.14),
            ("S", 0.43, 0.14, 0.43, 0.88),
            ("C", 0.43, 0.14),
            ("F", 0.08, 0.14),
            ("F", 0.78, 0.14),
            ("F", 0.43, 0.88),
        ),
    ),
    "U": Glyph(
        0.90,
        G(
            ("S", 0.18, 0.12, 0.18, 0.70),
            ("N", 0.36, 0.70, 0.18, 180, 90),
            ("S", 0.36, 0.88, 0.44, 0.88),
            ("S", 0.70, 0.12, 0.70, 0.70),
            ("A", 0.52, 0.70, 0.18, 0, 90),
            ("S", 0.52, 0.88, 0.44, 0.88),
            ("C", 0.18, 0.70),
            ("C", 0.70, 0.70),
            ("C", 0.44, 0.88),
            ("F", 0.18, 0.12),
            ("F", 0.70, 0.12),
        ),
    ),
    "W": Glyph(
        1.16,
        G(
            ("S", 0.08, 0.12, 0.08, 0.26),
            ("S", 0.08, 0.26, 0.26, 0.88),
            ("S", 0.26, 0.88, 0.50, 0.28),
            ("S", 0.50, 0.28, 0.74, 0.88),
            ("S", 0.74, 0.88, 0.92, 0.26),
            ("S", 0.92, 0.26, 0.92, 0.12),
            ("C", 0.08, 0.26),
            ("C", 0.26, 0.88),
            ("C", 0.50, 0.28),
            ("C", 0.74, 0.88),
            ("C", 0.92, 0.26),
            ("F", 0.08, 0.12),
            ("F", 0.92, 0.12),
        ),
    ),
    "X": Glyph(
        0.84,
        G(
            ("S", 0.16, 0.12, 0.16, 0.24),
            ("S", 0.16, 0.24, 0.68, 0.76),
            ("S", 0.68, 0.76, 0.68, 0.88),
            ("S", 0.68, 0.12, 0.68, 0.24),
            ("S", 0.68, 0.24, 0.16, 0.76),
            ("S", 0.16, 0.76, 0.16, 0.88),
            ("C", 0.42, 0.50),
            ("C", 0.16, 0.24),
            ("C", 0.68, 0.24),
            ("C", 0.68, 0.76),
            ("C", 0.16, 0.76),
            ("F", 0.16, 0.12),
            ("F", 0.68, 0.12),
            ("F", 0.16, 0.88),
            ("F", 0.68, 0.88),
        ),
    ),
    "Y": Glyph(
        0.84,
        G(
            ("S", 0.12, 0.12, 0.12, 0.24),
            ("S", 0.12, 0.24, 0.42, 0.50),
            ("S", 0.72, 0.12, 0.72, 0.24),
            ("S", 0.72, 0.24, 0.42, 0.50),
            ("S", 0.42, 0.50, 0.42, 0.88),
            ("C", 0.12, 0.24),
            ("C", 0.72, 0.24),
            ("C", 0.42, 0.50),
            ("F", 0.12, 0.12),
            ("F", 0.72, 0.12),
            ("F", 0.42, 0.88),
        ),
    ),
    "/": Glyph(
        0.52,
        G(
            ("S", 0.40, 0.10, 0.12, 0.90),
            ("F", 0.40, 0.10),
            ("F", 0.12, 0.90),
        ),
    ),
    "0": Glyph(
        0.82,
        G(
            ("A", 0.41, 0.50, 0.36, -90, 270),
        ),
    ),
    "1": Glyph(
        0.52,
        G(
            ("S", 0.14, 0.28, 0.30, 0.14),
            ("S", 0.30, 0.14, 0.30, 0.86),
            ("S", 0.12, 0.86, 0.48, 0.86),
            ("C", 0.30, 0.14),
            ("C", 0.30, 0.86),
            ("F", 0.14, 0.28),
            ("F", 0.12, 0.86),
            ("F", 0.48, 0.86),
        ),
    ),
    "2": Glyph(
        0.80,
        G(
            ("S", 0.16, 0.28, 0.16, 0.22),
            ("A", 0.40, 0.22, 0.24, 180, 360),
            ("S", 0.64, 0.22, 0.18, 0.86),
            ("S", 0.18, 0.86, 0.70, 0.86),
            ("C", 0.64, 0.22),
            ("C", 0.18, 0.86),
            ("F", 0.16, 0.28),
            ("F", 0.70, 0.86),
        ),
    ),
    "3": Glyph(
        0.80,
        G(
            ("S", 0.18, 0.16, 0.46, 0.16),
            ("A", 0.46, 0.32, 0.16, -90, 90),
            ("S", 0.46, 0.48, 0.28, 0.48),
            ("S", 0.28, 0.52, 0.48, 0.52),
            ("A", 0.48, 0.70, 0.18, -90, 90),
            ("S", 0.48, 0.88, 0.18, 0.88),
            ("C", 0.28, 0.50),
            ("F", 0.18, 0.16),
            ("F", 0.18, 0.88),
        ),
    ),
    "4": Glyph(
        0.84,
        G(
            ("S", 0.62, 0.12, 0.62, 0.88),
            ("S", 0.62, 0.12, 0.16, 0.62),
            ("S", 0.16, 0.62, 0.74, 0.62),
            ("C", 0.62, 0.12),
            ("C", 0.62, 0.62),
            ("F", 0.16, 0.62),
            ("F", 0.74, 0.62),
            ("F", 0.62, 0.88),
        ),
    ),
    "5": Glyph(
        0.80,
        G(
            ("S", 0.66, 0.14, 0.20, 0.14),
            ("S", 0.20, 0.14, 0.20, 0.46),
            ("S", 0.20, 0.46, 0.48, 0.46),
            ("A", 0.48, 0.66, 0.20, -90, 90),
            ("S", 0.48, 0.86, 0.20, 0.86),
            ("C", 0.20, 0.14),
            ("C", 0.20, 0.46),
            ("F", 0.66, 0.14),
            ("F", 0.20, 0.86),
        ),
    ),
    "6": Glyph(
        0.82,
        G(
            ("S", 0.66, 0.08, 0.66, 0.24),
            ("N", 0.44, 0.50, 0.34, -50, 90),
            ("A", 0.44, 0.66, 0.18, -90, 270),
            ("C", 0.66, 0.24),
            ("F", 0.66, 0.08),
        ),
    ),
    "7": Glyph(
        0.78,
        G(
            ("S", 0.12, 0.14, 0.70, 0.14),
            ("S", 0.70, 0.14, 0.28, 0.88),
            ("C", 0.70, 0.14),
            ("F", 0.12, 0.14),
            ("F", 0.28, 0.88),
        ),
    ),
    "8": Glyph(
        0.78,
        G(
            ("A", 0.39, 0.30, 0.18, -90, 270),
            ("A", 0.39, 0.70, 0.20, -90, 270),
            ("C", 0.39, 0.50),
        ),
    ),
    "9": Glyph(
        0.82,
        G(
            ("A", 0.44, 0.34, 0.20, -90, 270),
            ("S", 0.64, 0.34, 0.64, 0.70),
            ("A", 0.44, 0.70, 0.20, 0, 90),
            ("S", 0.44, 0.90, 0.22, 0.90),
            ("C", 0.64, 0.34),
            ("C", 0.64, 0.70),
            ("F", 0.22, 0.90),
        ),
    ),
    "-": Glyph(
        0.50,
        G(
            ("S", 0.06, 0.50, 0.44, 0.50),
            ("F", 0.06, 0.50),
            ("F", 0.44, 0.50),
        ),
    ),
    ".": Glyph(
        0.34,
        G(("F", 0.17, 0.86),),
    ),
}


def glyph(ch: str) -> Glyph | None:
    if ch == " ":
        return None
    return GLYPHS.get(ch.upper())


def letter_width(ch: str, size: float, tracking: float) -> float:
    if ch == " ":
        return size * 0.34
    g = glyph(ch)
    if not g:
        return size * 0.2
    return size * g.width + size * tracking


def measure(text: str, size: float, tracking: float = 0.08) -> float:
    return sum(letter_width(ch, size, tracking) for ch in text)


def _pipe_cap(cr: cairo.Context) -> None:
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)


def _light_normal(dx: float, dy: float) -> tuple[float, float]:
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    if nx * -1.0 + ny * -1.0 < 0:
        nx, ny = -nx, -ny
    return nx, ny


def _tube_gradient(x0: float, y0: float, x1: float, y1: float, radius: float) -> cairo.LinearGradient:
    nx, ny = _light_normal(x1 - x0, y1 - y0)
    g = cairo.LinearGradient(x0 - nx * radius, y0 - ny * radius, x0 + nx * radius, y0 + ny * radius)
    g.add_color_stop_rgb(0.00, *COPPER_DARK)
    g.add_color_stop_rgb(0.22, *COPPER_MID)
    g.add_color_stop_rgb(0.38, *COPPER_LIGHT)
    g.add_color_stop_rgb(0.52, *COPPER)
    g.add_color_stop_rgb(1.00, *COPPER_DARK)
    return g, nx, ny


def _straight(cr: cairo.Context, x0: float, y0: float, x1: float, y1: float, pw: float) -> None:
    radius = pw / 2
    g, nx, ny = _tube_gradient(x0, y0, x1, y1, radius)
    _pipe_cap(cr)
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


def _bend(
    cr: cairo.Context,
    cx: float,
    cy: float,
    r: float,
    a0: float,
    a1: float,
    pw: float,
    negative: bool,
) -> None:
    radius = pw / 2
    nx, ny = -0.72, -0.72
    nlen = math.hypot(nx, ny)
    nx, ny = nx / nlen, ny / nlen
    g = cairo.LinearGradient(cx - nx * (r + radius), cy - ny * (r + radius), cx + nx * (r + radius), cy + ny * (r + radius))
    g.add_color_stop_rgb(0.00, *COPPER_DARK)
    g.add_color_stop_rgb(0.28, *COPPER_MID)
    g.add_color_stop_rgb(0.42, *COPPER_LIGHT)
    g.add_color_stop_rgb(0.58, *COPPER)
    g.add_color_stop_rgb(1.00, *COPPER_DARK)
    _pipe_cap(cr)

    def trace() -> None:
        cr.new_path()
        if negative:
            cr.arc_negative(cx, cy, r, math.radians(a0), math.radians(a1))
        else:
            cr.arc(cx, cy, r, math.radians(a0), math.radians(a1))

    cr.set_line_width(pw + max(2.0, pw * 0.16))
    cr.set_source_rgb(*COPPER_DARK)
    trace()
    cr.stroke()
    cr.set_line_width(pw)
    cr.set_source(g)
    trace()
    cr.stroke()
    cr.set_line_width(max(1.2, pw * 0.20))
    cr.set_source_rgba(*COPPER_LIGHT, 0.88)
    cr.new_path()
    hr = max(r - radius * 0.36, r * 0.55)
    if negative:
        cr.arc_negative(cx, cy, hr, math.radians(a0), math.radians(a1))
    else:
        cr.arc(cx, cy, hr, math.radians(a0), math.radians(a1))
    cr.stroke()


def _end_dirs(parts: tuple[tuple, ...]) -> list[tuple[float, float, float, float]]:
    """Outward pipe directions at every stroke endpoint (glyph space)."""
    pts: list[tuple[float, float, float, float]] = []
    for cmd in parts:
        kind = cmd[0]
        if kind == "S":
            x0, y0, x1, y1 = cmd[1], cmd[2], cmd[3], cmd[4]
            pts.append((x0, y0, x0 - x1, y0 - y1))
            pts.append((x1, y1, x1 - x0, y1 - y0))
        elif kind in ("A", "N"):
            cx, cy, r, a0, a1 = cmd[1], cmd[2], cmd[3], cmd[4], cmd[5]
            clockwise = kind == "A"
            for a, start in ((a0, True), (a1, False)):
                rad = math.radians(a)
                px = cx + r * math.cos(rad)
                py = cy + r * math.sin(rad)
                tx, ty = -math.sin(rad), math.cos(rad)
                if clockwise:
                    if start:
                        tx, ty = -tx, -ty
                else:
                    if not start:
                        tx, ty = -tx, -ty
                pts.append((px, py, tx, ty))
    return pts


def _dir_for_flange(fx: float, fy: float, ends: list[tuple[float, float, float, float]]) -> tuple[float, float]:
    best = (0.0, 1.0 if fy >= 0.5 else -1.0)
    best_d = 0.08
    for x, y, dx, dy in ends:
        d = math.hypot(x - fx, y - fy)
        if d < best_d - 1e-6:
            best_d = d
            best = (dx, dy)
    return best


def _pipe_end(cr: cairo.Context, x: float, y: float, pw: float, dx: float, dy: float) -> None:
    """Open copper pipe mouth: rim, wall thickness, dark bore."""
    length = math.hypot(dx, dy)
    if length < 1e-6:
        dx, dy = 0.0, -1.0
        length = 1.0
    dx, dy = dx / length, dy / length
    ang = math.atan2(dy, dx)
    r = pw * 0.98
    squash = 0.42
    cr.save()
    cr.translate(x + dx * pw * 0.12, y + dy * pw * 0.12)
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


def _coupling(cr: cairo.Context, x: float, y: float, pw: float) -> None:
    r = pw * 0.70
    cr.set_source_rgb(*COPPER_DARK)
    cr.arc(x, y, r, 0, math.tau)
    cr.fill()
    cr.set_source_rgb(*COPPER)
    cr.arc(x, y, r * 0.78, 0, math.tau)
    cr.fill()
    cr.set_source_rgb(*BRASS)
    cr.set_line_width(max(1.1, pw * 0.08))
    cr.arc(x, y, r * 0.46, 0, math.tau)
    cr.stroke()
    cr.set_source_rgba(*COPPER_LIGHT, 0.75)
    cr.arc(x - r * 0.22, y - r * 0.22, r * 0.20, 0, math.tau)
    cr.fill()


def draw_letter(cr: cairo.Context, ch: str, ox: float, oy: float, size: float) -> None:
    g = glyph(ch)
    if not g:
        return
    pw = size * (0.118 if size >= 90 else 0.100)

    def pt(x: float, y: float) -> tuple[float, float]:
        return ox + x * size, oy + y * size

    for cmd in g.parts:
        kind = cmd[0]
        if kind == "S":
            x0, y0 = pt(cmd[1], cmd[2])
            x1, y1 = pt(cmd[3], cmd[4])
            _straight(cr, x0, y0, x1, y1, pw)
        elif kind == "A":
            cx, cy = pt(cmd[1], cmd[2])
            _bend(cr, cx, cy, cmd[3] * size, cmd[4], cmd[5], pw, False)
        elif kind == "N":
            cx, cy = pt(cmd[1], cmd[2])
            _bend(cr, cx, cy, cmd[3] * size, cmd[4], cmd[5], pw, True)

    ends = _end_dirs(g.parts)
    for cmd in g.parts:
        if cmd[0] == "C":
            x, y = pt(cmd[1], cmd[2])
            _coupling(cr, x, y, pw)
    for cmd in g.parts:
        if cmd[0] == "F":
            x, y = pt(cmd[1], cmd[2])
            dx, dy = _dir_for_flange(cmd[1], cmd[2], ends)
            _pipe_end(cr, x, y, pw, dx, dy)


def draw_line(
    cr: cairo.Context,
    text: str,
    left: float,
    top: float,
    size: float,
    tracking: float = 0.08,
) -> float:
    x = left
    for ch in text:
        adv = letter_width(ch, size, tracking)
        if glyph(ch):
            draw_letter(cr, ch, x, top, size)
        x += adv
    return x


def draw_centered(
    cr: cairo.Context, text: str, y: float, size: float, canvas: int = 1080, tracking: float = 0.08
) -> None:
    tw = measure(text, size, tracking)
    draw_line(cr, text, (canvas - tw) / 2, y, size, tracking)


def wash(cr: cairo.Context, w: int = 1080, h: int = 1080) -> None:
    cr.set_source_rgb(*CREAM)
    cr.paint()
