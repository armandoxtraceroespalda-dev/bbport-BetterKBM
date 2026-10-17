"""Platform-independent state machine for the Bloodborne mouse bridge."""
import time


class Controls:
    def __init__(self, emit, clock=time.monotonic):
        self.emit = emit
        self.clock = clock
        self.held = {}
        self.output = set()
        self.serial = 0

    def _sync(self):
        wanted = {entry[0] for entry in self.held.values()}
        for key in sorted(self.output - wanted):
            self.emit(key, False)
        for key in sorted(wanted - self.output):
            self.emit(key, True)
        self.output = wanted

    def press(self, button, shift=False):
        if button in self.held and self.held[button][2] is None:
            return
        key = ('heavy' if shift else 'light') if button == 'left' else 'firearm'
        # Latch the action at mouse-down: releasing Shift cannot turn a charged
        # attack into a light attack while the mouse button is still held.
        self.held[button] = (key, self.clock(), None)
        self._sync()

    def release(self, button):
        entry = self.held.get(button)
        if entry is not None:
            key, start, _ = entry
            self.held[button] = (key, start, max(self.clock(), start + 0.050))
            self.tick()

    def wheel(self, up, shift=False):
        key = ('right' if up else 'left') if shift else ('up' if up else 'down')
        self.serial += 1
        now = self.clock()
        self.held['wheel_' + str(self.serial)] = (key, now, now + 0.050)
        self._sync()

    def tick(self):
        now = self.clock()
        self.held = {k: v for k, v in self.held.items() if v[2] is None or v[2] > now}
        self._sync()

    def cancel(self):
        self.held.clear()
        self._sync()
