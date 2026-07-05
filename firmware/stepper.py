# PIO step generator — one state machine per joint.
#
# WHY PIO: drawing needs step pulses at up to ~5000/sec with metronome timing.
# Python can't promise that; the Pico's PIO hardware state machines can.
# Each motion segment hands the SM two numbers: (pulse count, pulse period).
# The SM then emits exactly `count` pulses spaced exactly `period` apart,
# in silicon, unaffected by anything Python is doing.
#
# The DIR pin is ordinary GPIO: Python sets direction BETWEEN segments
# (the executor waits for the SM to finish before changing it).

import rp2
from machine import Pin

SM_FREQ = 1_000_000          # 1 MHz -> delay units of 1 microsecond


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW, autopull=False)
def _step_program():
    pull(block)              # word 1: pulse count - 1  -> x
    mov(x, osr)
    pull(block)              # word 2: low-time in us   -> saved in isr
    mov(isr, osr)
    label("pulse")
    set(pins, 1) [3]         # STEP high ~4us (TMC2209 needs >0.1us)
    set(pins, 0)
    mov(y, isr)              # reload the period
    label("dly")
    jmp(y_dec, "dly")        # burn `low-time` microseconds
    jmp(x_dec, "pulse")      # next pulse until count exhausted


class StepChannel:
    """One joint: STEP via PIO, DIR via GPIO."""

    def __init__(self, sm_id, step_pin, dir_pin):
        self.dir_pin = Pin(dir_pin, Pin.OUT, value=0)
        self.sm = rp2.StateMachine(sm_id, _step_program,
                                   freq=SM_FREQ, set_base=Pin(step_pin))
        self.sm.active(1)
        self.position = 0            # signed step counter (our odometry)
        self._pending = 0
        self._dir = 1

    def busy(self):
        # SM is done when both FIFO words were consumed AND the last
        # pulse train had time to finish; tx_fifo() covers the queue part.
        return self.sm.tx_fifo() > 0

    def start_segment(self, steps, period_us):
        """Fire `abs(steps)` pulses, sign = direction. Non-blocking."""
        if steps == 0:
            return
        self._dir = 1 if steps > 0 else -1
        self.dir_pin.value(1 if steps > 0 else 0)
        n = abs(steps)
        self.sm.put(n - 1)
        self.sm.put(max(2, int(period_us) - 6))   # -6: loop overhead cycles
        self._pending = n

    def finish_segment(self):
        """Call after the segment's time has elapsed: book the steps."""
        self.position += self._dir * self._pending
        self._pending = 0
