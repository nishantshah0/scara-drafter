"""Serial link to the Pico: sends command lines, respects the queue,
keeps the firmware watchdog fed."""
import time


class ScaraLink:
    def __init__(self, port, baud=115200, dry=False):
        self.dry = dry or port is None
        if not self.dry:
            import serial                     # pyserial
            self.ser = serial.Serial(port, baud, timeout=2)
            time.sleep(2)                     # Pico reboot-on-connect grace
            self.ser.reset_input_buffer()

    def _txrx(self, line):
        if self.dry:
            return "ok 0"
        self.ser.write((line + "\n").encode())
        return self.ser.readline().decode().strip()

    def run(self, cmds, on_progress=None):
        """Stream a command list with simple flow control."""
        for i, c in enumerate(cmds):
            r = self._txrx(c)
            # keep firmware queue modest so estop stays responsive
            while r.startswith("ok") and len(r.split()) == 2 \
                    and int(r.split()[1]) >= 25:
                time.sleep(0.05)
                r = self._txrx("?")           # doubles as watchdog heartbeat
                r = "ok " + r.split()[4] if r.startswith("pos") else "ok 0"
            if on_progress and i % 25 == 0:
                on_progress(i, len(cmds))
        if not self.dry:
            # wait for the queue to drain, feeding the watchdog
            while True:
                s = self._txrx("?")
                if s.startswith("pos") and " q 0 " in s:
                    break
                time.sleep(0.2)

    def cmd(self, line):
        return self._txrx(line)
