"""Phase 3's sacred ritual: draw the 50mm calibration square.

  python draw_square.py            -> dry run (plan + stats, no hardware)
  python draw_square.py --port COM3
"""
import argparse
from scara_config import HOME_ANGLES
from planner import Planner, stats
from link import ScaraLink

S = 25.0  # half-side: 50mm square centered on the sheet
SQUARE = [[(-S, -S), (S, -S), (S, S), (-S, S), (-S, -S)]]

ap = argparse.ArgumentParser()
ap.add_argument("--port", default=None, help="Pico COM port (omit = dry run)")
args = ap.parse_args()

cmds = Planner(HOME_ANGLES).draw_polylines(SQUARE)
print("plan:", stats(cmds))

link = ScaraLink(args.port, dry=args.port is None)
if link.dry:
    print("dry run - no hardware. First 5 commands:")
    for c in cmds[:5]:
        print("  ", c)
else:
    link.cmd("H")          # arm must be parked at the home stops first!
    link.cmd("E 1")
    link.run(cmds, on_progress=lambda i, n: print(f"  {i}/{n}"))
    link.cmd("E 0")
    print("done - measure the square with calipers, all four sides + diagonals")
