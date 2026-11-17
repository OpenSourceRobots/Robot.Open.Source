from robotkit import Obstacle, Pose, RobotConfig

DT = 0.05

config = RobotConfig()
sim = config.make_simulator(
    obstacles=[Obstacle(15.0, 1.0, 2.0), Obstacle(28.0, -2.0, 2.0)],
    start=Pose(0.0, 0.0, 0.0),
)
navigator = config.make_navigator((45.0, 0.0))

while sim.time < 300:
    linear, angular, state = navigator.update(sim.pose, sim.read_sensors(), DT)
    if state in ("arrived", "emergency stop"):
        break
    sim.step(linear, angular, DT)

print(f"result: {state}")
print(f"time: {sim.time:.1f}s")
print(f"position: ({sim.pose.x:.2f}, {sim.pose.y:.2f})")
