from __future__ import annotations

import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/robotrace_Sim/utills_c/linesim.c"
OUTPUTS = {"Darwin": ROOT / "native/linesim.dylib", "Linux": ROOT / "native/linesim.so", "Windows": ROOT / "native/linesim.dll"}


def main() -> int:
    system = platform.system()
    output = OUTPUTS.get(system)
    if output is None:
        raise SystemExit(f"unsupported platform: {system}")
    if system == "Windows":
        command = ["gcc", "-O2", "-shared", "-o", str(output), str(SOURCE)]
    elif system == "Darwin":
        command = ["cc", "-O2", "-dynamiclib", "-o", str(output), str(SOURCE)]
    else:
        command = ["cc", "-O2", "-fPIC", "-shared", "-o", str(output), str(SOURCE), "-lm"]
    subprocess.run(command, check=True, timeout=120)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
