"""All the numbers that define YOUR machine, in one place.
Calibration (Phase 3) edits THIS file, nothing else."""
import math

# --- geometry (mm) -----------------------------------------------------------
L1 = 130.0            # shoulder -> elbow
L2 = 130.0            # elbow -> pen
PAPER_CX = 120.0      # sheet center, mm in front of shoulder axis
SHEET_W, SHEET_H = 210.0, 148.0   # A5 landscape
MARGIN = 8.0          # keep-out border on the sheet

# --- drivetrain ---------------------------------------------------------------
FULL_STEPS = 200      # 1.8deg motor
MICROSTEP = 16        # MS1+MS2 jumpered high on TMC2209 (see roadmap notes)
REDUCTION = 3.0       # 20T -> 60T belt
STEPS_PER_RAD = FULL_STEPS * MICROSTEP * REDUCTION / (2 * math.pi)  # ~1527.9

# flip these if a joint moves backwards at bench test:
JOINT_SIGN = (1, 1)

ELBOW = +1            # elbow configuration (+1 or -1); one config covers A5

# --- motion -------------------------------------------------------------------
DRAW_FEED = 30.0      # mm/s with pen down
TRAVEL_FEED = 80.0    # mm/s pen up
POINT_SPACING = 0.6   # mm between interpolated points
MIN_PERIOD_US = 200   # never step faster than 5 kHz
SEG_MIN_MS = 8

# --- homing pose ----------------------------------------------------------------
# v1 has NO limit switches and NO StallGuard (that needs UART+DIAG; we only
# wired STEP/DIR/EN). Homing is 100% MANUAL every power-cycle:
#   1. By hand, rotate both joints until the arm rests against its printed
#      alignment stops (the "parked" pose).
#   2. Send "H" to the firmware -> it zeros its step counters to HOME_ANGLES.
#   3. Only then run a drawing. If the arm gets bumped or loses steps
#      mid-session, re-home before trusting positions again.
# Upgrade path (not built): 2 microswitches on GPIO for auto-homing, or
# free up 2 more GPIO for UART+DIAG to use StallGuard sensorless homing.
HOME_ANGLES = (0.0, 0.0)

PORT = "COM3"         # your Pico's port (Device Manager); override with --port


def sheet_to_world(u, v):
    """Sheet coords (u along 210mm width, v along 148mm, origin center)
    -> world mm at the shoulder. Sheet width lies along world Y."""
    return (PAPER_CX + v, u)
