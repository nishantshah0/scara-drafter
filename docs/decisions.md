# Design Decisions

## D1 — SCARA topology, not articulated arm

Drawing punishes wobble: every micron of slop is visible ink. A SCARA keeps
both links swinging in the horizontal plane, so gravity never bends the arm
into the page and rigidity is a 2D problem. Also: SCARA is a named industrial
robot class (fast assembly arms) — the term carries weight. Articulated
(shoulder-lifts-against-gravity) arms need stronger joints for zero drawing
benefit here.

## D2 — Link lengths 130 mm / 130 mm → A5 canvas

Reach vs rigidity: longer links = bigger paper but more flex and amplified
joint slop. 130+130 comfortably covers A5 (148×210). The base is designed so
longer v2 links can bolt on later (same upgrade-path philosophy as the
rover's spare-hole grid). Start stiff, earn reach.

## D3 — NEMA17 steppers + TMC2209 through ~3:1 printed belt reduction

Steppers give exact position without encoders (they move in fixed steps).
TMC2209 drivers: silent, breadboard-plugging, current set by one screw.
The 3:1 GT2 belt reduction triples angular resolution (~0.03°/microstep at
the joint) and torque, and adds the tension adjustment that Phase 3 tuning
lives on. Hobby servos were rejected: jittery, no microstepping, sloppy.

## D4 — Brains split: PC plans, Pico executes

DXF parsing, path planning, and IK run in Python on the PC (easy to write,
debug, and demo). The Pico W receives compact motion segments over WiFi/USB
and generates precisely-timed step pulses (the hard-real-time part). This is
the standard industrial pattern (planner ↔ motion controller), and it reuses
the fail-safe watchdog + UDP protocol design from the slam-rover firmware.

## D5 — Pen lift: micro servo, gravity-down

MG90S rotates a cam that lifts the pen; pen weight + a light spring gives
consistent down-force. Simplest mechanism that yields consistent line width.

## D6 — No-solder constraint carried over

Every connection: breadboard, dupont, screw terminal. Drivers bought
pre-soldered; PSU gets a screw-terminal barrel adapter. One deliberate
exception allowed if unavoidable: a 10-minute makerspace soldering favor
rather than a redesign.

## D7 — Calibration: measure-and-correct, never trust the model

The kinematic model (link lengths, zero angles, backlash) is treated as
wrong until proven: draw test square → measure with calipers → fit
corrections in software → repeat. Same philosophy as the print-tolerance
coupon. Accuracy target: 50 mm square at ±0.5 mm with corners meeting.
