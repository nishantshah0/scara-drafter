# Debugging Log

What broke, why, and how it was fixed. Written for future-me and for
interviews ("tell me about a hard problem"). The Phase 3 square-tuning
saga belongs here, measurement by measurement.

## Entry template

```markdown
## YYYY-MM-DD — Title

**Phase:** 0–5
**Symptom:** what was observed
**Expected:** what should have happened
**Investigation:** what was checked, in order (dead ends count)
**Root cause:** the actual problem
**Fix:** what resolved it
**Lesson:** one line
```

---

<!-- Entries below, newest first -->

## 2026-07-06 — Servo wouldn't move despite firmware confirmed working

**Phase:** 1 (Bench Day 1, first physical hardware bring-up)
**Symptom:** Firmware ran perfectly (`scara-drafter fw ready`, `P 1`/`P 0` both
replied `ok` every time, no crashes) — but the physical servo never moved.
**Expected:** Servo snaps to position on `P 1`, back on `P 0`.
**Investigation, in order:**
1. Checked firmware logic — clean, 7+ consecutive `ok` replies, ruled out.
2. Suspected VBUS brownout (a known risk from the roadmap) — no unexpected
   reboots occurred, ruled out.
3. Measured voltage between the wire believed to be VBUS and ground at the
   servo connector — read ~0.0–0.2 V. Should have been ~5 V.
4. Tried re-identifying VBUS by counting pins from a photo of the breadboard
   — counting from a photo turned out to be unreliable (easy to miscount or
   misjudge board orientation).
5. Suspected a dead breadboard row — tested with the multimeter's
   **continuity mode** (beeps when two points are electrically connected).
   Rows beeped fine — breadboard itself was good.
6. Tested continuity between the "VBUS" wire and the actual Pico pin sitting
   in that row — it beeped. So the wire *was* making good contact... just
   with the wrong pin.
**Root cause:** Misidentified which physical pin was VBUS, from counting
breadboard rows off a photo. The wiring itself was solid; the target pin was
wrong.
**Fix:** Re-anchored on a hardware fact instead of a photo-based count: VBUS
is *always* the pin physically closest to the USB connector. Rewired power
to that pin, confirmed live with the multimeter (~5 V), signal wire found by
trial-and-error (move one pin, test `P 1`, repeat) rather than counting.
**Lesson:** For physical wiring, trust *measurement* over *counting from a
photo* — a multimeter's continuity mode can prove a connection is solid
without ever proving it's the *right* connection. When counting is
unreliable, anchor on a physical landmark (like "closest pin to the
connector") instead, and verify live before trusting it.

## 2026-07-03 — Hub bearing seat printed stringy (internal ring bridge)

**Phase:** 0 (first hub print)
**Symptom:** The ceiling of the hub's lower bearing pocket — the flat ring
where the 608's outer race seats — came out drooped and stringy.
**Expected:** A flat, clean seating face.
**Investigation:** Location pinpointed it: the transition from the Ø22.3
pocket to the Ø14.8 central bore is a flat annular surface printed entirely
over air. Straight bridges stretch plastic between two anchored ends; a
*ring* bridge has no straight anchored path, so it sags. Design bug, not a
printer or slicer problem.
**Root cause:** CAD asked the printer for an unsupported internal circular
bridge.
**Fix:** Redesigned the transition: 1 mm flat seat ring (short bridges are
fine) + 45° cone the rest of the way — cones self-support. Hub STL
re-exported; part reprinted.
**Lesson:** Every internal horizontal surface in CAD is a question: "what
does the printer stand on here?" Flat ring ceilings over voids = automatic
fail. Chamfer or step them at design time.

**Round 2 (same day):** Reprint with the partial chamfer STILL stringy — in
two places. (a) The 1 mm flat "seat ring" I'd kept was itself built on chord
bridges spanning the whole pocket, so the disease survived my first fix;
(b) the TOP BELT FLANGE is also a ring overhang (1.8 mm cantilevered over
air + the tooth grooves) — same failure mode, different location, only
spotted on the reprint. Second-iteration fix: bottom transition is now a FULL cone (zero
flat, zero bridging) with a drop-in printed seat washer restoring the
bearing's flat face; top flange got a 45° cone underneath. Revised lesson:
when a failure mode is found once, sweep the WHOLE part for it — I fixed
one instance and shipped two more.
