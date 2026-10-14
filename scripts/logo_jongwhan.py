#!/usr/bin/env python3
"""Square mark by Jongwhan Lee (https://github.com/leejw51).

The drawing is his: a rustacean crab holding a copper pipe, on a warm cream
field. This script only places that JPEG on the square sizes used by the
other marks. It does not redraw the crab.
"""

from __future__ import annotations

from pathlib import Path

import cairo
import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = ROOT / "assets" / "logo-jongwhan.jpg"
SIZE = 1024


def _paint_pixbuf(pb: GdkPixbuf.Pixbuf) -> cairo.ImageSurface:
    w, h = pb.get_width(), pb.get_height()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    if pb.get_n_channels() != 3 or pb.get_has_alpha():
        raise SystemExit("expected an opaque RGB JPEG")
    src = memoryview(pb.get_pixels())
    stride_in = pb.get_rowstride()
    dst = surf.get_data()
    stride_out = surf.get_stride()
    # Cairo ARGB32 is native-endian premultiplied. Little-endian memory is BGRA.
    for y in range(h):
        si = y * stride_in
        di = y * stride_out
        for x in range(w):
            r = src[si + x * 3]
            g = src[si + x * 3 + 1]
            b = src[si + x * 3 + 2]
            o = di + x * 4
            dst[o] = b
            dst[o + 1] = g
            dst[o + 2] = r
            dst[o + 3] = 255
    surf.mark_dirty()
    return surf


def render(path: Path, side: int) -> None:
    src = _paint_pixbuf(GdkPixbuf.Pixbuf.new_from_file(str(SRC)))
    sw, sh = src.get_width(), src.get_height()
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    cr = cairo.Context(out)
    cr.scale(side / sw, side / sh)
    cr.set_source_surface(src, 0, 0)
    cr.get_source().set_filter(cairo.FILTER_BEST)
    cr.paint()
    path.parent.mkdir(parents=True, exist_ok=True)
    out.write_to_png(str(path))


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"missing {SRC}")
    DOCS.mkdir(parents=True, exist_ok=True)
    full = DOCS / "logo-jongwhan.png"
    render(full, SIZE)
    render(DOCS / "logo-jongwhan-512.png", 512)
    print(f"{full} {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
