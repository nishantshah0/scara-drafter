# Shopping List — one order, ~$160 CAD

Amazon.ca unless noted. Rules carried over from the last project: fast
shipping on everything; no soldering anywhere (buy the exact variants noted);
prices approximate.

| Item | Spec — what the listing MUST say | ~CAD |
|---|---|---|
| 2× NEMA17 stepper motors | "NEMA 17", ~40 mm body, 1.5–1.8 A (e.g. 17HS4401). Often sold in 2/3-packs | $32 |
| 2× TMC2209 driver modules | "TMC2209" stepstick, **pins pre-soldered** (BIGTREETECH-style are; check photos). TMC = silent + easy current setting | $18 |
| Raspberry Pi Pico WH | pre-soldered headers, WiFi | $13 |
| 12 V 3 A power supply | barrel jack + **screw-terminal adapter** included | $22 |
| GT2 belt + pulleys kit | "GT2 6mm belt + 20T pulleys" kit — must include **2× closed-loop belts (200 mm / 2GT-200)** and **2× 20T pulleys, 5 mm bore** (grub screws + allen key usually included). The big 60T pulleys are NOT bought — they're printed (D9) | $18 |
| Bearings | 608ZZ (8×22×7) ×4 + 625ZZ (5×16×5) ×4 — skate/printer bearings | $12 |
| MG90S micro servo | metal gear, for the pen lift | $6 |
| Jumper wires + breadboard | M-M and M-F dupont kit + half-size breadboard | $15 |
| M3 screw + nut assortment | 8–20 mm lengths; arms genuinely need screws (zip ties flex) | $10 |
| Electrolytic capacitors 100 µF | often included with driver kits — check before buying separately | $6 |
| Fine-liner pens | whatever's in the drawer; Staedtler/Micron if buying | $0–8 |
| **All structure** — base, links, carriage, reductions | **printed, P1S** | $0 |
| **Total** | | **~$155–165** |

## Tools

- **Multimeter — required this time, not borrowable-later:** setting driver
  current (the "Vref ritual") happens before any motor turns, and it's a
  live-voltage measurement. Borrow from the makerspace for week 1 or buy ($18).
- **Calipers — the precision phase runs on them (~$15 digital).** Measuring
  the test square with a ruler wastes the whole exercise. This is the one new
  tool purchase I'd call mandatory.

## Vet-at-checkout traps

1. **TMC2209 with unsoldered pins** — some budget listings ship pins loose.
   Photos show the truth. (Fallback: one 10-minute makerspace visit, but
   let's just buy the right listing.)
2. **NEMA17 "pancake" motors** (20 mm thin ones) — weaker; get ~40 mm bodies.
3. **12 V supply without the screw-terminal barrel adapter** — that $2
   adapter is what keeps this build solder-free.
