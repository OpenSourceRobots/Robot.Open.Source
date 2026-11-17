class PrintDriver:
    def __init__(self, every=10):
        self.every = every
        self.count = 0

    def send(self, left, right):
        if self.count % self.every == 0:
            print(f"left {left:6.3f} m/s   right {right:6.3f} m/s")
        self.count += 1

    def stop(self):
        print("stop")

    def close(self):
        self.stop()


class SerialDriver:
    def __init__(self, port, baud=115200, max_speed=2.0, link=None):
        self.max_speed = max_speed
        if link is None:
            try:
                import serial
            except ImportError:
                raise RuntimeError("pyserial is missing, run: python -m pip install pyserial")
            link = serial.Serial(port, baud, timeout=0.1)
        self.link = link

    def send(self, left, right):
        text = f"M {self._scale(left):.3f} {self._scale(right):.3f}\n"
        self.link.write(text.encode("ascii"))

    def stop(self):
        self.link.write(b"S\n")

    def close(self):
        self.stop()
        self.link.close()

    def _scale(self, speed):
        return max(-1.0, min(1.0, speed / self.max_speed))


def list_ports():
    try:
        from serial.tools import list_ports as tools
    except ImportError:
        raise RuntimeError("pyserial is missing, run: python -m pip install pyserial")
    return [(port.device, port.description) for port in tools.comports()]
