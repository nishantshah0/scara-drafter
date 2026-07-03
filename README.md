# Balance Bot — Self-Balancing Two-Wheel Robot

An inverted-pendulum robot that stands on two wheels, rejects disturbances,
and drives while balancing. Built for ~$100 CAD as a mechatronics portfolio
piece. Successor to [slam-rover](https://github.com/nishantshah0/slam-rover)
(design study) — reuses its firmware architecture, CAD workflow, and parts research.

## How it works (the 10-second version)

It's a broomstick balanced on a fingertip, motorized. An IMU chip (MPU6050)
senses which way the robot is tipping; a **PID controller** running on the
Pico commands the wheels to drive *under* the fall, hundreds of times per
second. Balance is never achieved — it's continuously re-won.

## Hardware (~$100 CAD, staged)

| Item | ~CAD | Notes |
|---|---|---|
| Raspberry Pi Pico WH | $13 | WiFi = wireless teleop + live tuning |
| 2× N20 gearmotors **with encoders**, 6V, ~300 RPM | $30 | Encoders enable station-keeping (stretch) |
| SparkFun TB6612FNG (with headers) | $20 | No-solder motor driver |
| MPU6050 (GY-521 board) | $10 | The inner ear. Buy a pre-soldered-header listing |
| Jumper wires + mini breadboard | $15 | |
| 6×AA holder w/ switch + alkalines | $12 | Battery rides HIGH — a taller center of mass falls slower (easier to balance) |
| Printed frame, wheels, mounts | $0 | Bambu P1S |

## Build phases

- **Phase 0** — order parts; design the frame (tall 3-deck tower, printed);
  set up repo & firmware skeleton
- **Phase 1** — IMU bring-up: read raw gyro/accel, fuse into a clean tilt
  angle (complementary filter), live-plot it over WiFi
- **Phase 2** — motors + encoders on the bench (same drill as the rover plan)
- **Phase 3** — **the balance loop**: PID from angle → wheel command; then the
  great tuning journey (this is the project — every oscillation goes in the
  debugging log)
- **Phase 4 (stretch)** — drive-while-balancing via WiFi teleop; encoder-based
  station-keeping (holds position, not just uprightness); push-recovery demo video

## Lineage

Firmware patterns (fail-safe watchdog, PIO encoder counting, UDP command
protocol, host-side simulation testing) proven in the
[slam-rover design study](https://github.com/nishantshah0/slam-rover).
