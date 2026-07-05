"""DXF -> polylines on the sheet. Handles everything Onshape exports
(LINE, LWPOLYLINE, ARC, CIRCLE, SPLINE, ELLIPSE) via ezdxf's path
flattening, then scales + centers the drawing to fit the A5 sheet."""
import ezdxf
from ezdxf import path as ezpath
from scara_config import SHEET_W, SHEET_H, MARGIN


def load(filename, flatten_tol=0.2):
    doc = ezdxf.readfile(filename)
    polys = []
    for e in doc.modelspace():
        try:
            p = ezpath.make_path(e)
        except (TypeError, ValueError):
            continue
        pts = [(v.x, v.y) for v in p.flattening(flatten_tol)]
        if len(pts) >= 2:
            polys.append(pts)
    if not polys:
        raise ValueError("no drawable entities found in " + filename)
    return _fit(polys)


def _fit(polys):
    xs = [x for p in polys for x, _ in p]
    ys = [y for p in polys for _, y in p]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    avail_w, avail_h = SHEET_W - 2 * MARGIN, SHEET_H - 2 * MARGIN
    s = min(avail_w / w if w else 1e9, avail_h / h if h else 1e9, 1.0)
    return [[((x - cx) * s, (y - cy) * s) for x, y in p] for p in polys], s
