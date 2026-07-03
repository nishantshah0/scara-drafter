# Roadmap — Milestone Ladders

Working rules (proven on the last project): one variable at a time · bench
before assembly · every milestone demonstrable in minutes · 20-minute fights
get logged · ~8–10 hrs/week.

**THE ONE RULE OF THIS PROJECT:** no resets, no pivots, no new-project
shopping until the arm draws **one clean 50 mm square**. That milestone is
deliberately placed on the far side of the hard part. After it, everything
is downhill and demos.

---

## Phase 0 (Week 0–1) — Design & order

- [ ] Order the [cart](shopping-list.md) (~$160, one order)
- [ ] **Bearing coupon** (print first): pockets for the 608/625 bearings +
      NEMA17 pilot boss + a printed GT2 tooth-profile sample — the tolerance
      test, same method as last project's motor coupon
- [ ] CAD session A: pen carriage (servo lift, pen clamp) — belt-independent,
      safe to finalize pre-arrival
- [ ] CAD session B: printed 60T GT2 pulleys (the big reduction wheels are
      PRINTED, not bought) — verify tooth mesh against the coupon sample
- [ ] **WAIT for the box, then measure:** exact belt lengths and pulleys in
      hand set the joint center-distances → only THEN:
- [ ] CAD session C: base + link 1 + link 2, dimensioned around the real
      belts, with slotted motor mounts for tension adjustment
- [ ] Print base + links

**Done when:** parts arrived, all structure printed around measured parts.
**Predicted fights:** bearing press-fits (the coupon's job) and belt-length
arithmetic (design rule: the belt is bought truth, the CAD adapts to it).

## Phase 1 (Week 1–2) — Electronics bench

Concepts: how steppers work (magnetic gear-teeth counting — position without
encoders), microstepping, driver current limiting (the multimeter ritual),
why 12 V logic needs level-separated wiring.

- [ ] Pico blinks (hello-world ritual)
- [ ] One stepper spins on the bench (driver current set FIRST — multimeter)
- [ ] Smooth acceleration ramps (I supply the step-generation core; jerky
      starts = skipped steps = lost position)
- [ ] Both joints sweep to commanded angles, repeatably
- [ ] Pen servo lifts/drops on command
- [ ] Fail-safe: commands stop → motion stops (watchdog pattern, again)

**Done when:** "joint 1 to 45°, joint 2 to −30°" just works, every time.

## Phase 2 (Week 2–3) — Assembly & IK

The whiteboard afternoon: derive two-link inverse kinematics together
(law of cosines, atan2 — you will OWN this math; it's interview bait).

- [ ] Arm assembled: bearings seated, belts tensioned, zero slop by hand
- [ ] Homing routine (arm finds its zero position)
- [ ] IK implemented: command (x, y) in mm → pen goes there
- [ ] Dot grid test: pen taps a 5×5 grid — do the dots land where math says?
- [ ] **First drawn line** 📸

**Done when:** a commanded straight line is recognizably straight.
**Predicted fights:** mirrored motion (sign error), degrees/radians (again),
elbow-up vs elbow-down solution flip mid-move.

## Phase 3 (Week 3–5) — Precision. The valley.

Draw 50 mm test square → measure with calipers → diagnose → adjust → again.
Expect 3–6 loops. Improvements come in millimeters. **This phase is the
project** — the before/after square photos are the single best interview
artifact this build produces.

- [ ] Square v1 drawn + measured (it will be bad — log it, keep it)
- [ ] Backlash measured and software-compensated
- [ ] Belt tension tuned; joints reprinted if flexing
- [ ] Corner overshoot fixed (acceleration tuning)
- [ ] **One clean square: sides 50±0.5 mm, corners meet** 🏔️

**Done when:** the square. Frame the v1-vs-final photos side by side.

## Phase 4 (Week 5–6) — The DXF pipeline

- [ ] Python DXF parser (lines + arcs + circles from Onshape exports)
- [ ] Path planner: pen-up travel ordering, feedrates
- [ ] Draw a simple exported sketch (the coupon drawing is poetic)
- [ ] **Money demo:** design a part live in Onshape, export, arm drafts it 📹

## Phase 5 (Stretch, whenever)

- Handwriting/single-line fonts (it signs your name)
- Dry-erase whiteboard tile (infinite career-fair demos)
- Cycloidal gearbox joints v2 (the mechanical deep-cut)
- Pen → gripper swap experiments

## Portfolio artifacts to collect

Phase 0: CAD renders · Phase 2: first-line photo · Phase 3: the
square-evolution series (v1 → final) · Phase 4: the full-loop video
(Onshape screen → arm drawing → finished page) · Throughout: debugging log.
