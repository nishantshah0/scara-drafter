# SCARA Drafter — Pico W firmware
#
# Role: the "spinal cord". The PC plans everything (DXF -> paths -> IK ->
# timed segments); this firmware just executes segments with hardware-exact
# timing and fails safe. Protocol = text lines over USB serial:
#
#   PC -> Pico                              reply
#   G <steps1> <steps2> <ms>   queue a coordinated move        "ok <qlen>"
#   P <0|1>                    pen up(0)/down(1)               "ok"
#   E <0|1>                    drivers off(0)/on(1)            "ok"
#   H                          zero both position counters      "ok"
#   X                          ESTOP: flush queue, pen up, off  "ok estop"
#   ?                          status                           "pos <p1> <p2> q <n> pen <0|1>"
#
# Fail-safe: TMC2209 EN is ACTIVE-LOW (low = motors powered). We hold it
# HIGH (off) at boot, and the watchdog forces it HIGH again if the PC goes
# silent mid-queue. A disabled stepper freewheels: the arm just stops.

import sys
import time
import select
from machine import Pin, PWM
from stepper import StepChannel

# ---- pins (matches docs wiring chart) --------------------------------------
STEP1, DIR1 = 2, 3
STEP2, DIR2 = 4, 5
EN_PIN      = 6          # both drivers, ACTIVE-LOW
SERVO_PIN   = 7

# ---- pen servo --------------------------------------------------------------
PEN_UP_US, PEN_DOWN_US = 1900, 1200   # tune at bench (pulse widths)
SETTLE_MS = 250                        # let the pen land before moving

WATCHDOG_MS = 1500

en = Pin(EN_PIN, Pin.OUT, value=1)                    # boot: drivers OFF
servo = PWM(Pin(SERVO_PIN)); servo.freq(50)

def pen(down):
    servo.duty_ns((PEN_DOWN_US if down else PEN_UP_US) * 1000)

pen(False)
j1 = StepChannel(0, STEP1, DIR1)
j2 = StepChannel(1, STEP2, DIR2)

queue = []            # pending (s1, s2, ms) segments
seg_end_ms = 0        # when the running segment completes
running = False
pen_down = False
last_rx = time.ticks_ms()

poller = select.poll()
poller.register(sys.stdin, select.POLLIN)
buf = ""

def readline():
    global buf
    while poller.poll(0):
        ch = sys.stdin.read(1)
        if ch in ("\n", "\r"):
            line, buf = buf, ""
            if line:
                return line
        else:
            buf += ch
    return None

def start_next():
    global running, seg_end_ms
    s1, s2, ms = queue.pop(0)
    n = max(abs(s1), abs(s2), 1)
    # each axis spreads its steps evenly across the same segment duration
    if s1: j1.start_segment(s1, (ms * 1000) // abs(s1))
    if s2: j2.start_segment(s2, (ms * 1000) // abs(s2))
    seg_end_ms = time.ticks_add(time.ticks_ms(), ms)
    running = True

def estop():
    global queue, running, pen_down
    queue = []
    running = False
    pen_down = False
    pen(False)
    en.value(1)

print("scara-drafter fw ready")

while True:
    now = time.ticks_ms()

    line = readline()
    if line:
        last_rx = now
        p = line.split()
        try:
            if p[0] == "G" and len(p) == 4:
                queue.append((int(p[1]), int(p[2]), max(1, int(p[3]))))
                print("ok", len(queue))
            elif p[0] == "P":
                pen_down = p[1] == "1"
                pen(pen_down)
                time.sleep_ms(SETTLE_MS)
                print("ok")
            elif p[0] == "E":
                en.value(0 if p[1] == "1" else 1)   # active-low!
                print("ok")
            elif p[0] == "H":
                j1.position = 0; j2.position = 0
                print("ok")
            elif p[0] == "X":
                estop()
                print("ok estop")
            elif p[0] == "?":
                print("pos", j1.position, j2.position,
                      "q", len(queue) + (1 if running else 0),
                      "pen", 1 if pen_down else 0)
            else:
                print("err")
        except (ValueError, IndexError):
            print("err")

    # segment bookkeeping
    if running and time.ticks_diff(now, seg_end_ms) >= 0 \
            and not j1.busy() and not j2.busy():
        j1.finish_segment(); j2.finish_segment()
        running = False

    if not running and queue:
        start_next()

    # WATCHDOG: PC vanished mid-job -> stop safe
    if (running or queue) and time.ticks_diff(now, last_rx) > WATCHDOG_MS:
        estop()
        print("watchdog estop")

    time.sleep_ms(2)
