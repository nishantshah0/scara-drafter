"""Software self-test — runs on the PC with zero hardware.
  python selftest.py
"""
import math, os, random, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scara_config import (L1, L2, MARGIN, SHEET_W, SHEET_H, MIN_PERIOD_US,
                          HOME_ANGLES, sheet_to_world)
from ik import inverse, forward, Unreachable
from planner import Planner, stats

ok = 0; total = 0
def check(name, cond, detail=""):
    global ok, total
    total += 1; ok += bool(cond)
    print(("PASS  " if cond else "FAIL  ") + name + (f"   [{detail}]" if detail and not cond else ""))

# 1. IK <-> FK roundtrip on 2000 random reachable points
random.seed(7)
worst = 0.0
for _ in range(2000):
    r = random.uniform(45, L1 + L2 - 5)
    a = random.uniform(-math.pi, math.pi)
    x, y = r * math.cos(a), r * math.sin(a)
    t1, t2 = inverse(x, y)
    xx, yy = forward(t1, t2)
    worst = max(worst, math.dist((x, y), (xx, yy)))
check("IK/FK roundtrip < 1e-9 mm over 2000 points", worst < 1e-9, f"worst={worst}")

# 2. Every corner + edge midpoint of the usable sheet is reachable
pts = []
u, v = SHEET_W/2 - MARGIN, SHEET_H/2 - MARGIN
for su in (-u, 0, u):
    for sv in (-v, 0, v):
        pts.append((su, sv))
reach_fail = []
for (su, sv) in pts:
    try:
        inverse(*sheet_to_world(su, sv))
    except Unreachable:
        reach_fail.append((su, sv))
check("entire usable A5 sheet reachable (9-point grid)", not reach_fail, str(reach_fail))

# 3. Plan the 50mm calibration square; sanity the output
S = 25.0
cmds = Planner(HOME_ANGLES).draw_polylines(
    [[(-S, -S), (S, -S), (S, S), (-S, S), (-S, -S)]])
st = stats(cmds)
check("square plan produces segments", st["segments"] > 100, str(st))
check("peak step rate under the 5kHz cap",
      st["peak_step_rate_hz"] <= 1_000_000 / MIN_PERIOD_US, str(st))
check("plan duration sane (5-120s)", 5 < st["est_seconds"] < 120, str(st))
pen_downs = sum(1 for c in cmds if c == "P 1")
check("pen lowers exactly once for one polyline", pen_downs == 1)

# 4. Planner position bookkeeping: end angles reproduce the last point
p = Planner(HOME_ANGLES)
p.draw_polylines([[(0, 0), (30, 20)]])
fx, fy = forward(*p.angles)
tx, ty = sheet_to_world(30, 20)
check("planner end-state matches target within a step",
      math.dist((fx, fy), (tx, ty)) < 0.2, f"{(fx, fy)} vs {(tx, ty)}")

# 5. DXF pipeline: author a file with ezdxf, load it back
import ezdxf
from dxf_loader import load
tmp = os.path.join(tempfile.gettempdir(), "scara_selftest.dxf")
doc = ezdxf.new(); msp = doc.modelspace()
msp.add_line((0, 0), (100, 0))
msp.add_circle((50, 30), radius=20)
msp.add_lwpolyline([(0, 0), (10, 40), (60, 60)])
doc.saveas(tmp)
polys, scale = load(tmp)
check("DXF loads: 3 entities -> 3 polylines", len(polys) == 3, f"got {len(polys)}")
flat = [pt for pl in polys for pt in pl]
inside = all(abs(x) <= SHEET_W/2 - MARGIN + 1e-6 and abs(y) <= SHEET_H/2 - MARGIN + 1e-6
             for x, y in flat)
check("DXF fitted inside sheet margins", inside)
cmds2 = Planner(HOME_ANGLES).draw_polylines(polys)
check("DXF plans end-to-end", stats(cmds2)["segments"] > 50, str(stats(cmds2)))

print("-" * 50)
print(f"{ok}/{total} software checks passed")
sys.exit(0 if ok == total else 1)
