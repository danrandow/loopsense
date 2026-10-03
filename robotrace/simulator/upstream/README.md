# Pinned RobotTraceSim upstream

The MIT-licensed upstream is vendored unchanged in `robotrace_Sim/` at commit `2c99a9b63db8f9e0ef56c930cf1b360f2a1efc1c`. Machine-readable provenance is in `UPSTREAM.json`; the upstream license is preserved at `robotrace_Sim/LICENSE`.

This is what “pinning” means: every race can name the exact source revision, so a future upstream change cannot silently alter past or later results.

The source is pinned, but its original simulator is a PySide6 desktop application that loads a Windows DLL and dynamically executes arbitrary Python controllers. Those characteristics are incompatible with the experiment contract. The portable native helper can be built with `python3 simulator/native/build.py`; the safe experiment currently runs through `simulator/adapter/headless.py` while the upstream physics loop is extracted behind that interface.
