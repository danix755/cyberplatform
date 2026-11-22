"""
CYBERPLATFORM MOBILE
Touchscreen Android port built with Kivy.

Desktop test:
    python -m pip install kivy
    python main.py

Android APK:
    See README.md and buildozer.spec.
"""
import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

# Landscape desktop preview size; Android uses the actual screen dimensions.
Window.size = (960, 540)
Window.clearcolor = get_color_from_hex("#070914")

CYAN = "#2DEBFF"
PINK = "#FF2D9B"
PURPLE = "#914BFF"
YELLOW = "#FFE15A"
WHITE = "#EBF5FF"
RED = "#FF4B65"
GREEN = "#5AFFAA"

LEVEL_WIDTH = 3500


def rgba(hex_color, alpha=1):
    c = get_color_from_hex(hex_color)
    return (c[0], c[1], c[2], alpha)


class GameWorld(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "menu"
        self.player_x = 70.0
        self.player_y = 150.0
        self.vx = 0.0
        self.vy = 0.0
        self.player_w = 30
        self.player_h = 43
        self.on_ground = False
        self.health = 3
        self.score = 0
        self.camera_x = 0
        self.spawn_x = 70.0
        self.spawn_y = 150.0
        self.invuln = 0
        self.left_down = False
        self.right_down = False
        self.jump_queued = False
        self.collected = set()
        self.particles = []
        self.time = 0
        self.platforms = [
            (0, 0, 500, 48), (575, 95, 210, 20), (865, 160, 185, 20),
            (1125, 50, 230, 20), (1440, 110, 205, 20),
            (1735, 175, 215, 20), (2040, 80, 245, 20),
            (2370, 140, 210, 20), (2660, 205, 205, 20),
            (2940, 55, 560, 48),
            (370, 80, 85, 16), (755, 210, 80, 16),
            (1310, 145, 85, 16), (1650, 220, 80, 16),
            (2280, 205, 80, 16), (2570, 265, 80, 16),
        ]
        self.crystals = [
            (395, 112), (640, 130), (790, 245), (930, 195),
            (1180, 85), (1340, 180), (1490, 145), (1680, 250),
            (1810, 215), (2130, 115), (2300, 235), (2440, 175),
            (2600, 300), (2740, 240), (3050, 105), (3230, 105),
        ]
        self.drones = [
            {"x": 650.0, "y": 130.0, "start": 650.0, "span": 85.0, "dir": 1},
            {"x": 1180.0, "y": 82.0, "start": 1180.0, "span": 100.0, "dir": 1},
            {"x": 1780.0, "y": 215.0, "start": 1780.0, "span": 85.0, "dir": 1},
            {"x": 2110.0, "y": 115.0, "start": 2110.0, "span": 90.0, "dir": 1},
            {"x": 2700.0, "y": 245.0, "start": 2700.0, "span": 90.0, "dir": 1},
            {"x": 3100.0, "y": 105.0, "start": 3100.0, "span": 110.0, "dir": 1},
        ]
        self.checkpoint_x = 70.0
        self.goal_x = 3390
        self.bind(size=self.redraw, pos=self.redraw)
        Clock.schedule_interval(self.update, 1 / 60)

    def reset(self):
        self.player_x, self.player_y = 70.0, 150.0
        self.vx = self.vy = 0.0
        self.health = 3
        self.score = 0
        self.camera_x = 0
        self.spawn_x, self.spawn_y = 70.0, 150.0
        self.checkpoint_x = 70.0
        self.invuln = 0
        self.collected.clear()
        self.particles.clear()
        self.state = "playing"
        self.drones = [
            {"x": 650.0, "y": 130.0, "start": 650.0, "span": 85.0, "dir": 1},
            {"x": 1180.0, "y": 82.0, "start": 1180.0, "span": 100.0, "dir": 1},
            {"x": 1780.0, "y": 215.0, "start": 1780.0, "span": 85.0, "dir": 1},
            {"x": 2110.0, "y": 115.0, "start": 2110.0, "span": 90.0, "dir": 1},
            {"x": 2700.0, "y": 245.0, "start": 2700.0, "span": 90.0, "dir": 1},
            {"x": 3100.0, "y": 105.0, "start": 3100.0, "span": 110.0, "dir": 1},
        ]

    def respawn(self):
        self.player_x, self.player_y = self.spawn_x, self.spawn_y
        self.vx = self.vy = 0.0
        self.invuln = 1.5

    def update(self, dt):
        dt = min(dt, 1 / 30)
        self.time += dt
        if self.state == "playing":
            direction = int(self.right_down) - int(self.left_down)
            self.vx = direction * 245
            if self.jump_queued and self.on_ground:
                self.vy = 490
                self.on_ground = False
            self.jump_queued = False

            old_y = self.player_y
            self.player_x += self.vx * dt
            self.player_x = max(0, min(LEVEL_WIDTH - self.player_w, self.player_x))
            self.vy -= 1250 * dt
            self.player_y += self.vy * dt
            self.on_ground = False

            # Landing collision against platforms (coordinates use bottom-left origin).
            for px, py, pw, ph in self.platforms:
                overlaps_x = self.player_x + self.player_w > px and self.player_x < px + pw
                if overlaps_x and self.vy <= 0 and old_y >= py + ph - 2 and self.player_y <= py + ph:
                    self.player_y = py + ph
                    self.vy = 0
                    self.on_ground = True

            if self.player_y < -100:
                self.health -= 1
                if self.health <= 0:
                    self.state = "gameover"
                else:
                    self.respawn()

            if self.invuln > 0:
                self.invuln = max(0, self.invuln - dt)

            # Crystals.
            for i, (cx, cy) in enumerate(self.crystals):
                if i not in self.collected:
                    if abs((self.player_x + 15) - cx) < 24 and abs((self.player_y + 21) - cy) < 30:
                        self.collected.add(i)
                        self.score += 10
                        self.spark(cx, cy, YELLOW)

            # Drones patrol; stomp from above or take damage on contact.
            for drone in self.drones:
                drone["x"] += drone["dir"] * 105 * dt
                if drone["x"] > drone["start"] + drone["span"]:
                    drone["dir"] = -1
                elif drone["x"] < drone["start"]:
                    drone["dir"] = 1
                if drone.get("alive", True):
                    hit = (self.player_x + self.player_w > drone["x"] and
                           self.player_x < drone["x"] + 34 and
                           self.player_y + self.player_h > drone["y"] and
                           self.player_y < drone["y"] + 26)
                    if hit:
                        if self.vy < -40 and old_y >= drone["y"] + 20:
                            drone["alive"] = False
                            self.vy = 300
                            self.score += 25
                            self.spark(drone["x"] + 17, drone["y"] + 13, PINK)
                        elif self.invuln <= 0:
                            self.health -= 1
                            self.invuln = 1.5
                            self.vy = 280
                            self.vx = -direction * 100 if direction else -160
                            if self.health <= 0:
                                self.state = "gameover"

            # Checkpoint.
            if self.player_x > 1460 and self.checkpoint_x < 1000:
                self.checkpoint_x = 1460
                self.spawn_x, self.spawn_y = 1460, 155
            if self.player_x > self.goal_x:
                self.state = "victory"

            self.camera_x = max(0, min(LEVEL_WIDTH - self.width,
                                       self.player_x - self.width * 0.42))

        for p in self.particles[:]:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt
            if p[4] <= 0:
                self.particles.remove(p)

        self.redraw()

    def spark(self, x, y, color):
        for _ in range(10):
            self.particles.append([
                x, y, random.uniform(-100, 100),
                random.uniform(30, 170), random.uniform(.2, .5), color
            ])

    def world_to_screen(self, x, y):
        return x - self.camera_x, y

    def redraw(self, *args):
        self.canvas.clear()
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        sx = w / 960
        sy = h / 540

        with self.canvas:
            # Background.
            Color(*rgba("#070914"))
            Rectangle(pos=self.pos, size=self.size)

            # Distant skyline and stars.
            for i in range(18):
                bx = ((i * 100 - self.camera_x * .2) % (w + 100)) - 50
                bh = 65 + (i * 37 % 115)
                Color(*rgba("#101A35"))
                Rectangle(pos=(bx, 42 * sy), size=(72 * sx, bh * sy))
                Color(*rgba("#244666", .8))
                Line(points=[bx, (42 + bh) * sy, bx + 72 * sx, (42 + bh) * sy], width=1)
            random.seed(12)
            for _ in range(65):
                x = random.randrange(max(1, int(w)))
                y = random.randrange(max(1, int(h * .85)))
                Color(*rgba("#6686B2", .7))
                Ellipse(pos=(x, y), size=(2 * sx, 2 * sy))

            # Grid floor.
            Color(*rgba("#16324B"))
            for x in range(0, int(w), int(70 * sx) or 70):
                Line(points=[x, 0, x + 45 * sx, 65 * sy], width=1)
            for y in range(10, int(65 * sy), int(18 * sy) or 18):
                Line(points=[0, y, w, y], width=1)

            # Platforms.
            for px, py, pw, ph in self.platforms:
                x = (px - self.camera_x) * sx
                y = py * sy
                if x + pw * sx < -10 or x > w + 10:
                    continue
                Color(*rgba("#142644"))
                Rectangle(pos=(x, y), size=(pw * sx, ph * sy))
                Color(*rgba(CYAN))
                Line(points=[x, y + ph * sy, x + pw * sx, y + ph * sy], width=2)
                Color(*rgba("#316C91"))
                Line(rectangle=(x, y, pw * sx, ph * sy), width=1)

            # Crystals.
            for i, (cx, cy) in enumerate(self.crystals):
                if i in self.collected:
                    continue
                x, y = self.world_to_screen(cx, cy)
                pulse = math.sin(self.time * 5 + i) * 3
                Color(*rgba(YELLOW))
                Triangle(points=[(x) * sx, (y + 12 + pulse) * sy,
                                  (x + 10) * sx, y * sy,
                                  (x) * sx, (y - 12 - pulse) * sy])
                Triangle(points=[x * sx, (y + 12 + pulse) * sy,
                                 (x - 10) * sx, y * sy,
                                 x * sx, (y - 12 - pulse) * sy])

            # Checkpoint beacon.
            cx = (self.checkpoint_x + 20 - self.camera_x) * sx
            Color(*rgba(GREEN))
            Line(points=[cx, 48 * sy, cx, 108 * sy], width=2)
            Ellipse(pos=(cx - 6 * sx, 104 * sy), size=(12 * sx, 12 * sy))

            # Goal beacon.
            gx = (self.goal_x - self.camera_x) * sx
            Color(*rgba(PURPLE))
            Line(rectangle=(gx, 48 * sy, 40 * sx, 80 * sy), width=3)
            Color(*rgba(CYAN))
            Ellipse(pos=(gx + 9 * sx, 78 * sy), size=(22 * sx, 22 * sy))

            # Drones.
            for d in self.drones:
                if not d.get("alive", True):
                    continue
                x = (d["x"] - self.camera_x) * sx
                y = d["y"] * sy
                Color(*rgba("#511B58"))
                Ellipse(pos=(x - 5 * sx, y - 5 * sy), size=(44 * sx, 36 * sy))
                Color(*rgba(PINK))
                Line(ellipse=(x, y, 34 * sx, 26 * sy), width=2)
                Ellipse(pos=(x + 13 * sx, y + 8 * sy), size=(8 * sx, 8 * sy))

            # Player, with brief damage flicker.
            if self.invuln <= 0 or int(self.time * 12) % 2 == 0:
                px = (self.player_x - self.camera_x) * sx
                py = self.player_y * sy
                Color(*rgba(CYAN, .17))
                Ellipse(pos=(px - 9 * sx, py - 7 * sy),
                        size=(self.player_w * sx + 18 * sx, self.player_h * sy + 14 * sy))
                Color(*rgba("#142D4C"))
                Rectangle(pos=(px, py), size=(self.player_w * sx, self.player_h * sy))
                Color(*rgba(CYAN))
                Line(rectangle=(px, py, self.player_w * sx, self.player_h * sy),
                     width=2)
                Color(*rgba(PINK))
                Rectangle(pos=(px + 5 * sx, py + 24 * sy),
                          size=(20 * sx, 8 * sy))
                Color(*rgba(WHITE))
                Ellipse(pos=(px + 12 * sx, py + 8 * sy), size=(6 * sx, 6 * sy))

            # Particles.
            for x, y, vx, vy, life, color in self.particles:
                Color(*rgba(color, max(0, min(1, life * 2))))
                Ellipse(pos=((x - self.camera_x) * sx, y * sy),
                        size=(4 * sx, 4 * sy))

            # HUD.
            Color(*rgba("#080C1B", .92))
            Rectangle(pos=(12 * sx, (h - 64 * sy)), size=(235 * sx, 52 * sy))
            Color(*rgba(CYAN))
            Line(rectangle=(12 * sx, h - 64 * sy, 235 * sx, 52 * sy), width=1.2)
            Color(*rgba(WHITE))
            self._label(f"ENERGY  {self.health}/3", 20 * sx, h - 35 * sy, 16 * sx)
            Color(*rgba(YELLOW))
            self._label(f"CRYSTALS  {self.score}", 20 * sx, h - 56 * sy, 14 * sx)

            # Menu / pause / end-state overlay.
            if self.state != "playing":
                Color(0.02, 0.03, 0.08, .83)
                Rectangle(pos=self.pos, size=self.size)
                title = {
                    "menu": "CYBERPLATFORM",
                    "paused": "SYSTEM PAUSED",
                    "gameover": "SIGNAL LOST",
                    "victory": "SECTOR CLEARED",
                }[self.state]
                Color(*rgba(CYAN))
                self._label(title, w * .5 - 190 * sx, h * .58, 38 * sx, center=True)
                Color(*rgba(WHITE))
                subtitle = "NEON PLATFORMING PROTOCOL" if self.state == "menu" else (
                    "Tap RESUME to continue" if self.state == "paused" else
                    f"Final score: {self.score}"
                )
                self._label(subtitle, w * .5 - 150 * sx, h * .48, 17 * sx, center=True)

    def _label(self, text, x, y, font_size, center=False):
        # Canvas text via a lightweight Kivy Label texture.
        label = Label(text=text, font_name="RobotoMono",
                      font_size=max(10, font_size),
                      color=(1, 1, 1, 1), size_hint=(None, None),
                      size=(420, 42), halign="center" if center else "left",
                      valign="middle")
        label.texture_update()
        if center:
            x -= label.texture_size[0] / 2
        label.pos = (x, y)
        label.canvas.ask_update()
        # Draw its texture directly into the current canvas.
        Color(1, 1, 1, 1)
        from kivy.graphics import Rectangle as KRectangle
        KRectangle(texture=label.texture, pos=label.pos,
                   size=label.texture_size)


class CyberPlatformApp(App):
    def build(self):
        self.root_layout = FloatLayout()
        self.world = GameWorld(size_hint=(1, 1))
        self.root_layout.add_widget(self.world)

        # Large translucent touch controls at the bottom corners.
        button_style = {
            "font_size": "24sp",
            "bold": True,
            "background_normal": "",
            "background_down": "",
            "background_color": (0.05, 0.22, 0.32, 0.82),
            "color": (0.18, 0.92, 1, 1),
            "size_hint": (None, None),
            "size": (76, 76),
        }
        self.left_btn = Button(text="◀", pos_hint={"x": .025, "y": .04}, **button_style)
        self.right_btn = Button(text="▶", pos_hint={"x": .115, "y": .04}, **button_style)
        self.jump_btn = Button(text="JUMP", font_size="18sp",
                               pos_hint={"right": .975, "y": .04},
                               **{**button_style, "size": (104, 76),
                                  "background_color": (0.34, 0.06, 0.22, 0.86),
                                  "color": (1, .25, .62, 1)})
        self.pause_btn = Button(text="Ⅱ", font_size="22sp",
                                pos_hint={"right": .975, "top": .97},
                                **{**button_style, "size": (54, 48),
                                   "background_color": (0.12, 0.12, 0.22, .8)})
        for btn in (self.left_btn, self.right_btn, self.jump_btn, self.pause_btn):
            self.root_layout.add_widget(btn)

        self.left_btn.bind(on_press=lambda *_: self.set_move("left", True))
        self.left_btn.bind(on_release=lambda *_: self.set_move("left", False))
        self.right_btn.bind(on_press=lambda *_: self.set_move("right", True))
        self.right_btn.bind(on_release=lambda *_: self.set_move("right", False))
        self.jump_btn.bind(on_press=self.jump)
        self.pause_btn.bind(on_press=self.pause_or_start)
        self.start_button = Button(
            text="START / RESTART",
            size_hint=(None, None), size=(210, 54),
            pos_hint={"center_x": .5, "center_y": .37},
            font_size="16sp", bold=True,
            background_normal="", background_color=(.65, .05, .25, .95),
            color=(1, 1, 1, 1)
        )
        self.root_layout.add_widget(self.start_button)
        self.start_button.bind(on_press=self.start_or_resume)
        Clock.schedule_interval(self.sync_ui, .1)
        return self.root_layout

    def set_move(self, side, pressed):
        if side == "left":
            self.world.left_down = pressed
        else:
            self.world.right_down = pressed

    def jump(self, *_):
        if self.world.state == "playing":
            self.world.jump_queued = True
        else:
            self.start_or_resume()

    def pause_or_start(self, *_):
        if self.world.state == "playing":
            self.world.state = "paused"
        elif self.world.state == "paused":
            self.world.state = "playing"
        else:
            self.start_or_resume()

    def start_or_resume(self, *_):
        if self.world.state in ("menu", "gameover", "victory"):
            self.world.reset()
        elif self.world.state == "paused":
            self.world.state = "playing"

    def sync_ui(self, _dt):
        self.start_button.opacity = 1 if self.world.state != "playing" else 0
        self.start_button.disabled = self.world.state == "playing"
        self.start_button.text = "START GAME" if self.world.state == "menu" else (
            "RESUME" if self.world.state == "paused" else "PLAY AGAIN"
        )


if __name__ == "__main__":
    CyberPlatformApp().run()
