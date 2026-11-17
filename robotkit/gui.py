import math
import tkinter as tk

from .config import load_config
from .drive import Pose
from .sensors import Obstacle

SCALE = 10
WIDTH = 1000
HEIGHT = 640
ORIGIN = (50, HEIGHT // 2)
DT = 0.05
STEPS_PER_FRAME = 2
FRAME_MS = 30
START = Pose(0.0, 0.0, 0.0)
ROBOT_LENGTH = 3.0
ROBOT_WIDTH = 2.0
OBSTACLE_RADIUS = 2.0
MAX_TRAIL = 3000

BACKGROUND = "#1e2227"
GRID = "#2c323a"
OBSTACLE = "#8a5a44"
GOAL = "#4caf50"
TRAIL = "#4a90d9"
ROBOT = "#e8b923"
RAY = "#c0504d"
ALERT = "#ff5555"


def to_screen(x, y):
    return ORIGIN[0] + x * SCALE, ORIGIN[1] - y * SCALE


def to_world(px, py):
    return (px - ORIGIN[0]) / SCALE, (ORIGIN[1] - py) / SCALE


class Application:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.obstacles = []
        self.paused = False
        root.title("robotkit simulator")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack()

        bar = tk.Frame(root)
        bar.pack(fill="x")
        self.pause_button = tk.Button(bar, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side="left")
        tk.Button(bar, text="Reset", command=self.reset).pack(side="left")
        tk.Button(bar, text="Clear obstacles", command=self.clear_obstacles).pack(side="left")
        tk.Button(bar, text="Release e-stop", command=self.release_estop).pack(side="left")
        self.status = tk.Label(bar, anchor="w")
        self.status.pack(side="left", fill="x", expand=True, padx=10)

        self.canvas.bind("<Button-1>", self.set_goal)
        self.canvas.bind("<Button-2>", self.add_obstacle)
        self.canvas.bind("<Button-3>", self.add_obstacle)
        self.canvas.bind("<Shift-Button-1>", self.add_obstacle)

        self.reset()
        self.tick()

    def reset(self):
        self.sim = self.config.make_simulator(start=START)
        self.sim.obstacles = self.obstacles
        self.navigator = self.config.make_navigator((45.0, 0.0))
        self.trail = []
        self.ranges = self.sim.read_sensors()
        self.state = "ready"

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")

    def clear_obstacles(self):
        self.obstacles.clear()

    def release_estop(self):
        self.navigator.estop.release()

    def set_goal(self, event):
        if event.state & 0x1:
            return
        self.navigator.set_target(to_world(event.x, event.y))

    def add_obstacle(self, event):
        x, y = to_world(event.x, event.y)
        pose = self.sim.pose
        if math.hypot(x - pose.x, y - pose.y) < OBSTACLE_RADIUS + ROBOT_LENGTH:
            return
        self.obstacles.append(Obstacle(x, y, OBSTACLE_RADIUS))

    def tick(self):
        if not self.paused:
            for _ in range(STEPS_PER_FRAME):
                self.step()
        self.draw()
        self.root.after(FRAME_MS, self.tick)

    def step(self):
        self.ranges = self.sim.read_sensors()
        linear, angular, self.state = self.navigator.update(self.sim.pose, self.ranges, DT)
        if self.state == "emergency stop":
            self.sim.halt()
            return
        pose = self.sim.step(linear, angular, DT)
        self.trail.append((pose.x, pose.y))
        if len(self.trail) > MAX_TRAIL:
            self.trail.pop(0)

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        for obstacle in self.obstacles:
            self.draw_circle(obstacle.x, obstacle.y, obstacle.radius, OBSTACLE)
        self.draw_goal()
        self.draw_trail()
        self.draw_rays()
        self.draw_robot()
        self.update_status()

    def draw_grid(self):
        for meters in range(0, WIDTH // SCALE, 10):
            x, _ = to_screen(meters - ORIGIN[0] / SCALE, 0)
            self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID)
        for meters in range(-HEIGHT // SCALE, HEIGHT // SCALE, 10):
            _, y = to_screen(0, meters)
            self.canvas.create_line(0, y, WIDTH, y, fill=GRID)

    def draw_circle(self, x, y, radius, color):
        cx, cy = to_screen(x, y)
        r = radius * SCALE
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")

    def draw_goal(self):
        x, y = self.navigator.goal.target
        cx, cy = to_screen(x, y)
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, outline=GOAL, width=3)
        self.canvas.create_line(cx - 12, cy, cx + 12, cy, fill=GOAL)
        self.canvas.create_line(cx, cy - 12, cx, cy + 12, fill=GOAL)

    def draw_trail(self):
        if len(self.trail) < 2:
            return
        points = [coord for x, y in self.trail for coord in to_screen(x, y)]
        self.canvas.create_line(*points, fill=TRAIL)

    def draw_rays(self):
        pose = self.sim.pose
        start = to_screen(pose.x, pose.y)
        for name, sensor in self.sim.sensors.items():
            angle = pose.heading + sensor.angle
            reach = self.ranges[name]
            end = to_screen(pose.x + math.cos(angle) * reach, pose.y + math.sin(angle) * reach)
            self.canvas.create_line(*start, *end, fill=RAY)

    def draw_robot(self):
        pose = self.sim.pose
        half_length = ROBOT_LENGTH / 2
        half_width = ROBOT_WIDTH / 2
        corners = [
            (half_length, half_width),
            (half_length, -half_width),
            (-half_length, -half_width),
            (-half_length, half_width),
        ]
        cos = math.cos(pose.heading)
        sin = math.sin(pose.heading)
        points = []
        for cx, cy in corners:
            wx = pose.x + cx * cos - cy * sin
            wy = pose.y + cx * sin + cy * cos
            points.extend(to_screen(wx, wy))
        outline = ALERT if self.state == "emergency stop" else "white"
        self.canvas.create_polygon(points, fill=ROBOT, outline=outline, width=2)
        nose = to_screen(pose.x + cos * half_length, pose.y + sin * half_length)
        center = to_screen(pose.x, pose.y)
        self.canvas.create_line(*center, *nose, fill="black", width=2)

    def update_status(self):
        pose = self.sim.pose
        speed = self.sim.limiter.linear
        self.status.config(
            text=f"{self.state}   x {pose.x:6.1f} m   y {pose.y:6.1f} m   speed {speed:4.2f} m/s"
            "   |   click: set goal   right-click or shift-click: add obstacle",
            fg=ALERT if self.state == "emergency stop" else "black",
        )


def run(config_path=None):
    config = load_config(config_path)
    root = tk.Tk()
    Application(root, config)
    root.mainloop()
