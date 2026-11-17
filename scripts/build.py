import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
WORK = ROOT / "build"

SYSTEM_NAMES = {"win32": "windows", "darwin": "macos"}
SYSTEM = SYSTEM_NAMES.get(sys.platform, "linux")
SUFFIX = ".exe" if sys.platform == "win32" else ""

PROGRAMS = [
    ("robotkit", "app.py", False),
    ("robotkit-gui", "gui_app.py", sys.platform == "win32"),
]


def build(name, script, windowed):
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--name",
        name,
        "--distpath",
        str(DIST),
        "--workpath",
        str(WORK),
        "--specpath",
        str(WORK),
    ]
    if windowed:
        command.append("--windowed")
    command.append(str(ROOT / script))
    subprocess.run(command, check=True)

    built = DIST / (name + SUFFIX)
    final = DIST / f"{name}-{SYSTEM}{SUFFIX}"
    built.replace(final)
    print(f"built {final}")


def main():
    for name, script, windowed in PROGRAMS:
        build(name, script, windowed)


if __name__ == "__main__":
    main()
