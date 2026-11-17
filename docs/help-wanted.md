# Help wanted

robotkit is a work in progress, moving over from an older site. These are the jobs that would help most. Pick one, open an issue to say you are on it, then send a pull request.

## Good first issues

- Add a line follower behavior to `robotkit/behaviors.py`
- Add a `--config` option to the `drive` command that checks the file before sending anything
- Show wheel speeds in the simulator window
- Let the simulator window load and save obstacle layouts
- Write a short guide for wiring the Arduino sketch to a motor controller

## Bigger jobs

- CAN bus driver next to `SerialDriver` in `robotkit/hardware.py`
- Encoder input that feeds `Odometry`
- GPS input for outdoor routes
- Steering models for tracked and car-like robots, not only differential drive
- Move the old site's docs and issues over

## Testing

- Run the firmware on different boards and report what works
- Try the downloadable apps on older Windows, macOS and Linux versions
