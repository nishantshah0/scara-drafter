"""Path planner: polylines on the sheet -> timed firmware segments.

Pipeline per polyline: interpolate points every POINT_SPACING mm -> IK each
point -> joint deltas -> STEPS (with rounding residue carried, so error
never accumulates) -> 'G s1 s2 ms' lines at the requested feed.
"""
import math
from scara_config import (STEPS_PER_RAD, JOINT_SIGN, DRAW_FEED, TRAVEL_FEED,
                          POINT_SPACING, MIN_PERIOD_US, SEG_MIN_MS,
                          sheet_to_world)
from ik import inverse


def _interpolate(p0, p1):
    d = math.dist(p0, p1)
    n = max(1, int(d / POINT_SPACING))
    return [(p0[0] + (p1[0] - p0[0]) * i / n,
             p0[1] + (p1[1] - p0[1]) * i / n) for i in range(1, n + 1)]


class Planner:
    """Tracks the machine's joint state in steps; emits command lines."""

    def __init__(self, start_angles):
        self.angles = start_angles
        self.steps = [round(start_angles[0] * STEPS_PER_RAD * JOINT_SIGN[0]),
                      round(start_angles[1] * STEPS_PER_RAD * JOINT_SIGN[1])]

    def _goto(self, u, v, feed, out):
        """One straight sheet-space line to (u,v) at feed mm/s."""
        x1, y1 = sheet_to_world(u, v)
        # current pen position from current angles:
        from ik import forward
        x0, y0 = forward(*self.angles)
        for (px, py) in _interpolate((x0, y0), (x1, y1)):
            t1, t2 = inverse(px, py)
            tgt = [round(t1 * STEPS_PER_RAD * JOINT_SIGN[0]),
                   round(t2 * STEPS_PER_RAD * JOINT_SIGN[1])]
            ds = [tgt[0] - self.steps[0], tgt[1] - self.steps[1]]
            seg_mm = math.dist((px, py), (x0, y0)); x0, y0 = px, py
            ms = max(SEG_MIN_MS, int(seg_mm / feed * 1000))
            # respect the max step rate (stretch time if needed)
            for d in ds:
                if d:
                    ms = max(ms, int(abs(d) * MIN_PERIOD_US / 1000) + 1)
            if ds[0] or ds[1]:
                out.append(f"G {ds[0]} {ds[1]} {ms}")
            self.steps = tgt
            self.angles = (t1, t2)

    def draw_polylines(self, polylines):
        """polylines: list of [(u,v), ...] in sheet mm. Returns command list."""
        out = []
        for poly in polylines:
            if len(poly) < 2:
                continue
            out.append("P 0")
            self._goto(*poly[0], TRAVEL_FEED, out)
            out.append("P 1")
            for pt in poly[1:]:
                self._goto(*pt, DRAW_FEED, out)
        out.append("P 0")
        return out


def stats(cmds):
    moves = [c for c in cmds if c.startswith("G")]
    total_ms = sum(int(c.split()[3]) for c in moves)
    max_rate = max((abs(int(c.split()[i])) / int(c.split()[3]) * 1000
                    for c in moves for i in (1, 2)), default=0)
    return {"segments": len(moves), "pen_ops": len(cmds) - len(moves),
            "est_seconds": round(total_ms / 1000, 1),
            "peak_step_rate_hz": round(max_rate)}
