"""Two-link inverse kinematics — the whiteboard math, in 30 lines.

Given a pen target (x, y) in mm from the shoulder axis, find the two joint
angles. Law of cosines gives the elbow angle; the shoulder angle is the
direction to the target minus the wedge the elbow creates.
"""
import math
from scara_config import L1, L2, ELBOW


class Unreachable(Exception):
    pass


def inverse(x, y, elbow=ELBOW):
    r2 = x * x + y * y
    c2 = (r2 - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if c2 > 1.0 or c2 < -1.0:
        raise Unreachable(f"({x:.1f},{y:.1f}) outside workspace")
    s2 = elbow * math.sqrt(max(0.0, 1.0 - c2 * c2))
    t2 = math.atan2(s2, c2)
    t1 = math.atan2(y, x) - math.atan2(L2 * s2, L1 + L2 * c2)
    return t1, t2


def forward(t1, t2):
    x = L1 * math.cos(t1) + L2 * math.cos(t1 + t2)
    y = L1 * math.sin(t1) + L2 * math.sin(t1 + t2)
    return x, y
