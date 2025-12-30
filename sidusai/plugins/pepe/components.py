import time
import threading
import sys
import random

class PepeComponent:
    def __init__(self):
        self.active = False
        self.thread = None
        self.frame = 0
        self.speed = 0.5
        self.current_animation = "new_year"

        self.snowflakes = []
        self.snow_density = 0.08
        self.screen_width = 60
        self.screen_height = 30

        self._init_snow()

        self.pepe_frames = {
            "new_year": {
                "open_eyes": """
      ★
     🎅🎅
         _    _
        (o)--(o)
       /.______.\\
       \\________/
      ./        \\.
      ( .       ,)
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """,
                "closed_eyes": """
      ★
     🎅🎅
         _    _
        (-)--(-)
       /.______.\\
       \\________/
      ./        \\.
      ( .       ,)
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """
            },
            "happy": {
                "frame1": """
       🎁
      🎄🎄
         _    _
        (♥)--(♥)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ⌣   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """,
                "frame2": """
       🎁
      🎄🎄
         _    _
        (^)--(^)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ▽   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """
            },
            "blink": {
                "frame1": """
          _    _
         (o)--(o)
        /.______.\\
        \\________/
       ./        \\.
      ( .        , )
       \\ \\_\\\\//_/ /
        ~~  ~~  ~~
                """,
                "frame2": """
          _    _
         (-)--(-)
        /.______.\\
        \\________/
       ./        \\.
      ( .        , )
       \\ \\_\\\\//_/ /
        ~~  ~~  ~~
                """
            },
            "snow": {
                "frame1": """
          ❄
        ❄   ❄
         _    _
        (✿)--(✿)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ▽   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """,
                "frame2": """
          ❄
         ❄ ❄
         _    _
        (✿)--(✿)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ▽   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """
            },
            "celebration": {
                "frame1": """
       🎉✨🎉✨🎉✨🎉
         _    _
        (★)--(★)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ⌣   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """,
                "frame2": """
       ✨🎉✨🎉✨🎉✨
         _    _
        (★)--(★)
       /.______.\\
       \\________/
      ./        \\.
     ( .   ⌣   , )
      \\ \\_\\\\//_/ /
       ~~  ~~  ~~
                """
            }
        }

        for anim_name in self.pepe_frames:
            for frame_name in self.pepe_frames[anim_name]:
                self.pepe_frames[anim_name][frame_name] = self.pepe_frames[anim_name][frame_name].strip('\n')

    def _init_snow(self):
        snow_count = int(self.screen_width * self.screen_height * self.snow_density)
        self.snowflakes = []
        for _ in range(snow_count):
            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)
            speed = random.uniform(0.3, 0.8)
            self.snowflakes.append([x, y, speed])

    def _update_snow(self):
        for i in range(len(self.snowflakes)):
            self.snowflakes[i][1] += self.snowflakes[i][2]
            if self.snowflakes[i][1] >= self.screen_height:
                self.snowflakes[i][1] = 0
                self.snowflakes[i][0] = random.randint(0, self.screen_width - 1)

    def _draw_snow_background(self):
        screen = [[' ' for _ in range(self.screen_width)] for _ in range(self.screen_height)]

        snow_chars = ['❄', '･', '｡']

        for x, y, _ in self.snowflakes:
            x_int = int(x)
            y_int = int(y)
            if 0 <= y_int < self.screen_height and 0 <= x_int < self.screen_width:
                if random.random() < 0.3:
                    screen[y_int][x_int] = random.choice(snow_chars)

        snow_lines = []
        for row in screen:
            snow_lines.append(''.join(row))

        return snow_lines

    def show(self, animation_type="new_year"):
        if animation_type not in self.pepe_frames:
            animation_type = "new_year"

        if not self.active:
            self.active = True
            self.current_animation = animation_type
            self.frame = 0
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=1)
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()

    def set_speed(self, speed):
        if 0.1 <= speed <= 2.0:
            self.speed = speed

    def celebrate(self):
        self.show("celebration")

    def _run(self):
        while self.active:
            self._draw()
            self.frame += 1
            time.sleep(self.speed)

    def _draw(self):
        self._update_snow()
        snow_background = self._draw_snow_background()

        sys.stdout.write('\033[2J\033[H')

        animation = self.pepe_frames.get(self.current_animation, self.pepe_frames["new_year"])
        frame_keys = list(animation.keys())

        if self.current_animation == "new_year":
            if self.frame % 2 == 0:
                current_frame = animation["open_eyes"]
                message = "🎄 HAPPY NEW YEAR 2026! 🎄"
            else:
                current_frame = animation["closed_eyes"]
                message = "✨ С НОВЫМ ГОДОМ 2026! ✨"
        else:
            frame_index = self.frame % len(frame_keys)
            current_frame = animation[frame_keys[frame_index]]
            message = f"Pepe Animation: {self.current_animation}"

        pepe_lines = current_frame.split('\n')

        pepe_height = len(pepe_lines)
        pepe_width = max(len(line) for line in pepe_lines) if pepe_lines else 0

        snow_offset_y = (self.screen_height - pepe_height - 5) // 2
        if snow_offset_y < 0:
            snow_offset_y = 0

        for i in range(self.screen_height):
            snow_line = snow_background[i]

            if snow_offset_y <= i < snow_offset_y + pepe_height:
                pepe_line_idx = i - snow_offset_y
                if pepe_line_idx < len(pepe_lines):
                    pepe_line = pepe_lines[pepe_line_idx]
                    pepe_start = (self.screen_width - len(pepe_line)) // 2

                    combined_line = list(snow_line)
                    for j, char in enumerate(pepe_line):
                        pos = pepe_start + j
                        if 0 <= pos < self.screen_width and char != ' ':
                            combined_line[pos] = char

                    print(''.join(combined_line))
                    continue

            print(snow_line)

        centered_message = message.center(self.screen_width)
        print("\n" + "=" * self.screen_width)
        print(centered_message)

        if self.current_animation == "celebration":
            fireworks = ['🎆', '🎇', '✨', '💥', '🎊']
            firework_line = " ".join([random.choice(fireworks) for _ in range(8)])

            firework_start = (self.screen_width - len(firework_line)) // 2
            if firework_start < 0:
                firework_start = 0

            spacing = " " * firework_start
            print(spacing + firework_line)

        sys.stdout.flush()

    def get_status(self):
        return {
            "active": self.active,
            "current_animation": self.current_animation,
            "speed": self.speed,
            "frame": self.frame
        }

    def get_animations(self):
        return list(self.pepe_frames.keys())
