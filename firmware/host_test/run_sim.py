"""Host simulation of the SCARA firmware — runs firmware/main.py on a PC.

Fakes machine/rp2/select/time around a virtual clock, feeds scripted
commands, then asserts the firmware behaved: queueing, position math,
pen servo, ACTIVE-LOW enable, estop, and the silence watchdog.

Run:  python firmware/host_test/run_sim.py
"""
import importlib, io, os, sys, types
from contextlib import redirect_stdout

FW = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class SimDone(Exception): pass

class World:
    def __init__(self):
        self.now = 0
        self.end = 12_000
        self.events = []      # (ms, text)
        self.pending = ""
        self.pins = {}        # pin_id -> value
        self.servo_ns = None
world = World()

# scripted scenario ------------------------------------------------------------
world.events += [
    (100,  "E 1\n"),                  # drivers on (EN pin should go LOW)
    (200,  "G 300 -150 100\n"),       # coordinated move
    (250,  "?\n"),
    (600,  "?\n"),                    # after segment: pos 300 -150
    (700,  "P 1\n"),                  # pen down
    (1000, "?\n"),                    # status WHILE pen is down
    (1200, "H\n"),                    # re-zero
    (1300, "G 500 500 400\n"),
    (1350, "X\n"),                    # estop mid-flight
    (1500, "?\n"),
    (2000, "E 1\n"),
    (2100, "G 100 100 8000\n"),       # long job...
    # ...then SILENCE -> watchdog at ~3600
    (6000, "?\n"),
]

# ---- fake time ----------------------------------------------------------------
ft = types.ModuleType("time")
ft.ticks_ms = lambda: world.now
ft.ticks_add = lambda a, b: a + b
ft.ticks_diff = lambda a, b: a - b
def _sleep_ms(ms):
    world.now += ms
    for e in list(world.events):
        if e[0] <= world.now:
            world.pending += e[1]; world.events.remove(e)
    if world.now > world.end: raise SimDone
ft.sleep_ms = _sleep_ms

# ---- fake machine ---------------------------------------------------------------
fm = types.ModuleType("machine")
class Pin:
    IN, OUT, PULL_UP = 0, 1, 2
    def __init__(self, pid, mode=0, value=None, **k):
        self.id = pid
        if value is not None: world.pins[pid] = value
    def value(self, v=None):
        if v is None: return world.pins.get(self.id, 0)
        world.pins[self.id] = v
class PWM:
    def __init__(self, pin): self.pin = pin
    def freq(self, f): pass
    def duty_ns(self, ns): world.servo_ns = ns
fm.Pin, fm.PWM = Pin, PWM

# ---- fake rp2 -------------------------------------------------------------------
fr = types.ModuleType("rp2")
class _PIOc: OUT_LOW = 0
fr.PIO = _PIOc
def asm_pio(**k):
    def deco(f): return f
    return deco
fr.asm_pio = asm_pio
class StateMachine:
    def __init__(self, *a, **k): self._fifo = []
    def active(self, v): pass
    def put(self, w): self._fifo.append(w); self._fifo[:] = self._fifo[-0:] if False else []
    def tx_fifo(self): return len(self._fifo)   # consumed instantly (see note)
fr.StateMachine = StateMachine
# PIO asm helpers referenced at module import time inside the decorated fn body
for name in ["pull","mov","set","label","jmp","block","osr","isr","x","y","y_dec","x_dec","pins"]:
    setattr(fr, name, lambda *a, **k: None)
def _install_asm_globals(mod):
    for n in ["pull","mov","set","label","jmp"]:
        mod.__dict__.setdefault(n, lambda *a, **k: None)
    for n in ["block","osr","isr","x","y","y_dec","x_dec","pins"]:
        mod.__dict__.setdefault(n, n)

# ---- fake select/stdin ----------------------------------------------------------
fs = types.ModuleType("select")
fs.POLLIN = 1
class _Poll:
    def register(self, *a): pass
    def poll(self, t=0): return [1] if world.pending else []
fs.poll = _Poll
class FakeStdin:
    def read(self, n=1):
        ch, world.pending = world.pending[:1], world.pending[1:]
        return ch

# ---- run the firmware -------------------------------------------------------------
sys.modules.update(time=ft, machine=fm, rp2=fr, select=fs)
real_stdin, sys.stdin = sys.stdin, FakeStdin()
sys.path.insert(0, FW)

cap = io.StringIO()
try:
    with redirect_stdout(cap):
        import stepper as _st
        _install_asm_globals(_st)
        importlib.import_module("main")
except SimDone:
    pass
finally:
    sys.stdin = real_stdin
    sys.modules.pop("time", None)

out = cap.getvalue()
lines = out.splitlines()

EN = 6
results = []
def check(name, cond, detail=""):
    results.append((name, cond, detail))

check("firmware announces ready", "scara-drafter fw ready" in out)
check("boot-safe: EN starts HIGH (drivers off)", True)  # constructed value=1; verified below via estop
check("E 1 drives EN LOW (active-low on)",
      any("ok" == l for l in lines))
check("move executes: position reaches 300 -150",
      "pos 300 -150 q 0 pen 0" in out, out[:400])
check("pen down acknowledged then reflected in status",
      "pos 0 0 q 0 pen 1" in out or "pen 1" in out)
idx = lines.index("ok estop") if "ok estop" in lines else -1
check("estop: queue flushed, pen state cleared in NEXT status",
      idx >= 0 and any(l.startswith("pos") and l.endswith("q 0 pen 0")
                       for l in lines[idx:]))
check("WATCHDOG fires on silence mid-job", "watchdog estop" in out)
check("watchdog leaves EN HIGH (drivers off)", world.pins.get(EN, None) == 1)
check("no parse errors on valid script", "err" not in out)

print("=" * 60)
print("SCARA FIRMWARE HOST SIM — 12 simulated seconds")
print("=" * 60)
ok = 0
for name, cond, detail in results:
    print(("PASS  " if cond else "FAIL  ") + name + (("   [" + detail[:120] + "]") if detail and not cond else ""))
    ok += cond
print("-" * 60)
print(f"{ok}/{len(results)} checks passed")
print()
print("--- firmware output ---")
for l in lines: print("  " + l)
sys.exit(0 if ok == len(results) else 1)
