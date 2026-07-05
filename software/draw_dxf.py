"""The money demo: draw an Onshape-exported DXF.

  python draw_dxf.py part.dxf              -> dry run + stats
  python draw_dxf.py part.dxf --port COM3  -> ink
"""
import argparse
from scara_config import HOME_ANGLES
from planner import Planner, stats
from link import ScaraLink
from dxf_loader import load

ap = argparse.ArgumentParser()
ap.add_argument("dxf")
ap.add_argument("--port", default=None)
args = ap.parse_args()

polys, scale = load(args.dxf)
print(f"loaded {len(polys)} paths, scaled x{scale:.3f} to fit A5")
cmds = Planner(HOME_ANGLES).draw_polylines(polys)
print("plan:", stats(cmds))

link = ScaraLink(args.port, dry=args.port is None)
if link.dry:
    print("dry run - add --port COM3 to draw it for real")
else:
    link.cmd("H"); link.cmd("E 1")
    link.run(cmds, on_progress=lambda i, n: print(f"  {i}/{n}"))
    link.cmd("E 0")
    print("done. frame it.")
