import time
import threading
import sys
import random
import math

class Garland:
    def __init__(self):
        self.length = 20
        self.speed = 0.15
        self.mode = "wave"
        self.active = False
        self.thread = None
        self.frame = 0
        self.bulbs = ['🔴', '🟢', '🟡', '🔵', '🟣', '🟠', '✨', '🌟', '⭐', '💫']
        self.phases = []

    def start(self):
        if self.active:
            return
        self.active = True
        self.phases = [random.uniform(0, 2*math.pi) for _ in range(self.length)]
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=1)
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()

    def set_mode(self, mode):
        self.mode = mode
        self.frame = 0

    def set_speed(self, speed):
        if 0.05 <= speed <= 1.0:
            self.speed = speed

    def _run(self):
        while self.active:
            self._draw()
            self.frame += 1
            time.sleep(self.speed)

    def _draw(self):
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        garland = []

        if self.mode == "wave":
            for i in range(self.length):
                pos = self.frame % self.length
                if i == pos:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                else:
                    garland.append(' ')

        elif self.mode == "async":
            for i in range(self.length):
                frequency = 0.5 + (i % 5) * 0.2
                phase = self.phases[i]
                value = 0.5 + 0.5 * math.sin(2 * math.pi * frequency * self.frame / 10 + phase)

                if value > 0.7:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                elif value > 0.3:
                    garland.append('○')
                else:
                    garland.append(' ')

        elif self.mode == "async_random":
            for i in range(self.length):
                if random.random() < 0.3:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                else:
                    garland.append(' ')

        elif self.mode == "pulse_waves":
            for i in range(self.length):
                wave_pos = (self.frame + i) % self.length
                amplitude = 0.5 + 0.5 * math.sin(2 * math.pi * self.frame / 20)
                value = amplitude * math.sin(2 * math.pi * wave_pos / self.length + self.frame / 10)

                if value > 0.5:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                elif value > 0:
                    garland.append('◦')
                else:
                    garland.append(' ')

        elif self.mode == "chaos":
            for i in range(self.length):
                bulb_timer = (self.frame + i * 7) % 13
                if bulb_timer < 4:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                else:
                    garland.append(' ')

        elif self.mode == "breathing":
            for i in range(self.length):
                breath = math.sin(2 * math.pi * self.frame / 15 + i * 0.3)
                if breath > 0:
                    brightness = int(breath * 3)
                    if brightness == 3:
                        garland.append(self.bulbs[i % len(self.bulbs)])
                    elif brightness == 2:
                        garland.append('●')
                    elif brightness == 1:
                        garland.append('○')
                    else:
                        garland.append(' ')
                else:
                    garland.append(' ')

        elif self.mode == "fireflies":
            for i in range(self.length):
                if hasattr(self, 'firefly_states') and i < len(self.firefly_states):
                    state = self.firefly_states[i]
                    if state > 0:
                        if random.random() < 0.1:
                            self.firefly_states[i] = 0
                        else:
                            garland.append(self.bulbs[i % len(self.bulbs)])
                    else:
                        if random.random() < 0.05:
                            self.firefly_states[i] = 1
                            garland.append(self.bulbs[i % len(self.bulbs)])
                        else:
                            garland.append(' ')
                else:
                    garland.append(' ')
            if not hasattr(self, 'firefly_states'):
                self.firefly_states = [0] * self.length

        elif self.mode == "chase":
            for i in range(self.length):
                for j in range(3):
                    pos = (self.frame - j) % self.length
                    if i == pos:
                        garland.append(self.bulbs[(i + j) % len(self.bulbs)])
                        break
                else:
                    garland.append(' ')

        elif self.mode == "bounce":
            pos = self.frame % (self.length * 2 - 2)
            if pos >= self.length:
                pos = 2 * self.length - 2 - pos
            for i in range(self.length):
                if i == pos:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                else:
                    garland.append(' ')

        elif self.mode == "rainbow":
            for i in range(self.length):
                idx = (self.frame + i) % len(self.bulbs)
                garland.append(self.bulbs[idx])

        elif self.mode == "blink":
            for i in range(self.length):
                if self.frame % 2 == 0:
                    garland.append(self.bulbs[i % len(self.bulbs)])
                else:
                    garland.append(' ')

        sys.stdout.write(f"\r{''.join(garland)}")
        sys.stdout.flush()

    def get_status(self):
        return {
            "active": self.active,
            "mode": self.mode,
            "speed": self.speed,
            "length": self.length
        }
