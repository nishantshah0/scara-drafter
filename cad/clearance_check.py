"""Numeric check: does arm2's swept body ever clash with the base tower,
across every point the pen must reach on the usable A5 sheet?

Geometry pulled directly from cad/scara-parts.scad (not re-typed from memory):
  LINK=130, TOWER_H=52, ARM_T=12, PUL_H=8, HUB_BOSS_H=12, tower d1=56 (z=0) -> d2=44 (z=TOWER_H)
  arm2 hub_end_d=42 (r=21) at the elbow end, ARM_W=34 (r=17) at the far end (hulled bar)
Config from software/scara_config.py: L1=L2=130, PAPER_CX=120, SHEET 210x148, MARGIN=8
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "software"))
from ik import inverse, Unreachable

LINK = 130.0
ARM_T, PUL_H, HUB_BOSS_H, TOWER_H = 12.0, 8.0, 12.0, 52.0
TOWER_D0, TOWER_D1 = 56.0, 44.0   # diameter at z=0 and z=TOWER_H

# arm2's fixed world z-band (from the assembly transform chain)
arm2_z_lo = TOWER_H + (PUL_H + HUB_BOSS_H) - (PUL_H + HUB_BOSS_H + ARM_T + 0.5)
arm2_z_hi = arm2_z_lo + ARM_T
print(f"arm2 world z-band: {arm2_z_lo:.1f} to {arm2_z_hi:.1f}")

def tower_radius(z):
    z = max(0.0, min(TOWER_H, z))
    d = TOWER_D0 + (TOWER_D1 - TOWER_D0) * (z / TOWER_H)
    return d / 2

# worst case (largest, hardest-to-clear) tower radius across arm2's z-band
worst_tower_r = max(tower_radius(arm2_z_lo), tower_radius(arm2_z_hi))
print(f"tower radius across that band: {tower_radius(arm2_z_hi):.2f} (top) to {tower_radius(arm2_z_lo):.2f} (bottom)")
print(f"worst-case tower radius to clear: {worst_tower_r:.2f} mm\n")

R_ELBOW_END, R_PEN_END = 21.0, 17.0   # arm2's hulled-bar half-widths

def seg_point_dist(a, b, p):
    """min distance from point p to segment a-b (2D)."""
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)

def hulled_bar_clearance(elbow, pen):
    """Min distance from the ORIGIN to arm2's hulled-capsule footprint
    (circle r=R_ELBOW_END at elbow, circle r=R_PEN_END at pen, hulled)."""
    d_axis = seg_point_dist(elbow, pen, (0, 0))
    # interpolate the local half-width at the closest point along the segment
    ex, ey = elbow; px, py = pen
    seg_len = math.hypot(px - ex, py - ey)
    if seg_len == 0:
        return d_axis - R_ELBOW_END
    t = ((0 - ex) * (px - ex) + (0 - ey) * (py - ey)) / (seg_len ** 2)
    t = max(0.0, min(1.0, t))
    r_here = R_ELBOW_END + (R_PEN_END - R_ELBOW_END) * t
    return d_axis - r_here   # positive = clear, negative = overlap

# --- sweep every reachable point on the USABLE sheet -------------------------
PAPER_CX, SHEET_W, SHEET_H, MARGIN = 120.0, 210.0, 148.0, 8.0
half_v, half_u = SHEET_H / 2 - MARGIN, SHEET_W / 2 - MARGIN
print(f"usable sheet: world X in [{PAPER_CX-half_v:.1f}, {PAPER_CX+half_v:.1f}], "
      f"world Y in [{-half_u:.1f}, {half_u:.1f}]\n")

worst_clearance = 1e9
worst_pt = None
N = 60
unreachable = 0
for i in range(N + 1):
    for j in range(N + 1):
        v = -half_v + 2 * half_v * i / N          # -> world X = PAPER_CX + v
        u = -half_u + 2 * half_u * j / N          # -> world Y = u
        x, y = PAPER_CX + v, u
        try:
            t1, t2 = inverse(x, y)
        except Unreachable:
            unreachable += 1
            continue
        elbow = (LINK * math.cos(t1), LINK * math.sin(t1))
        pen = (x, y)
        clr = hulled_bar_clearance(elbow, pen) - (worst_tower_r - R_ELBOW_END if False else 0)
        # proper worst-case: subtract tower radius directly using the segment-to-origin
        # distance and local half-width already baked into hulled_bar_clearance; now
        # just compare that arm2 shape's clearance to the ORIGIN against tower radius:
        d_axis = seg_point_dist(elbow, pen, (0, 0))
        seg_len = math.hypot(pen[0]-elbow[0], pen[1]-elbow[1])
        t = 0.0 if seg_len == 0 else max(0, min(1, ((0-elbow[0])*(pen[0]-elbow[0])+(0-elbow[1])*(pen[1]-elbow[1]))/seg_len**2))
        r_here = R_ELBOW_END + (R_PEN_END - R_ELBOW_END) * t
        true_clearance = d_axis - r_here - worst_tower_r
        if true_clearance < worst_clearance:
            worst_clearance = true_clearance
            worst_pt = (x, y, t1 * 180/math.pi, t2 * 180/math.pi)

print(f"Checked {(N+1)**2 - unreachable} reachable points ({unreachable} outside workspace)")
print(f"WORST-CASE clearance between arm2's body and the tower: {worst_clearance:.2f} mm")
if worst_pt:
    print(f"  occurs at pen=({worst_pt[0]:.1f},{worst_pt[1]:.1f})  J1={worst_pt[2]:.1f} deg  J2={worst_pt[3]:.1f} deg")
print()
if worst_clearance < 0:
    print("*** COLLISION: arm2 clips the tower at this pose. ***")
elif worst_clearance < 3:
    print("*** TIGHT: clears, but under 3mm margin - worth padding. ***")
else:
    print("CLEAR across the entire usable sheet.")
