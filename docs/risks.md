# Risk Register

## R1 — Backlash & flex: wobbly lines 🔴 THE BOSS

Printed joints have slop; belts stretch; links flex. All of it becomes
visible squiggle. **Expected, planned for:** Phase 3 exists solely to grind
this down (tension, backlash compensation, joint reprints, acceleration
tuning). Mitigations designed in up front: belt reduction with tensioners,
ribbed links, bearing-fit coupon before any real part prints.

## R2 — IK bugs: arm confidently draws in the wrong place 🟠

Sign errors, degrees-vs-radians, elbow-up/elbow-down solution flips. One bad
evening each, then done. Mitigation: dot-grid test before any drawing; unit
discipline (the Onshape `5mm + #var` lesson lives on).

## R3 — Stepper current misconfigured 🟠

Too low → skipped steps → drawings drift mid-line. Too high → drivers cook.
Mitigation: the Vref ritual with a multimeter BEFORE first motion, per the
TMC2209 datasheet formula. Non-negotiable ordering of operations.

## R4 — Lost steps = silent position loss 🟠

Steppers don't know they missed a step; the arm just believes a lie forever.
Mitigations: acceleration ramps (never jerk from zero), conservative speeds,
homing routine to re-zero between drawings.

## R5 — 12 V power mistakes 🟡

12 V into a 3.3 V pin kills a Pico instantly. Mitigation: 12 V exists ONLY
on the driver motor rails; multimeter polarity check before first power;
never rewire live (rule inherited from the rover plan).

## R6 — The week-4 valley (the human risk) 🔴 REAL TALK

Recent history: three project resets in three days when things stopped being
shiny. Phase 3 of this build is deliberately unglamorous — the arm WORKS but
draws badly, and improvement comes in millimeters. This is where this
project dies if it dies.
**Contract with self: no resets, no new-project browsing until ONE CLEAN
50 mm SQUARE exists.** The milestone is placed just past the valley on
purpose. Reread this paragraph in week 4.

## R8 — Amp-level current through a breadboard 🟠

Breadboard spring contacts are for signals; sustained ~1 A+ makes them heat,
brown, and go intermittent (maddening to debug). Rule (D8): motor cables plug
DIRECTLY onto the driver modules' motor pins; only logic signals and the
capacitor-buffered 12 V feed touch the breadboard; driver current capped at
~0.8 A RMS. Also: 100 µF capacitor sits right at each driver's 12 V pins —
drivers can die from supply voltage spikes without it.

## R7 — Purchasing traps 🟡

Unsoldered driver pins, pancake NEMA17s, PSU without screw adapter — see
shopping-list vet notes. Wrong purchases cost a week of shipping each.
