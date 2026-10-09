from __future__ import annotations

import math
import random
import ctypes
import platform
from copy import deepcopy
from pathlib import Path
from typing import Any

from orchestrator.io import digest
from orchestrator.validators import ValidationError, validate_observation, validate_package


ADAPTER_VERSION = "robottracesim-native-v1"


class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


def _native_library() -> ctypes.CDLL:
    suffix = {"Darwin": "dylib", "Linux": "so", "Windows": "dll"}.get(platform.system())
    if suffix is None:
        raise RuntimeError(f"unsupported simulator platform: {platform.system()}")
    path = Path(__file__).resolve().parents[1] / "native" / f"linesim.{suffix}"
    if not path.exists():
        raise RuntimeError(f"RobotTraceSim native library is missing; run simulator/native/build.py: {path}")
    library = ctypes.CDLL(str(path))
    library.estimate_sensors_coverage_batch_C.argtypes = [
        ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int,
        ctypes.POINTER(_Point), ctypes.c_int, ctypes.c_double,
        ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_int,
        ctypes.POINTER(ctypes.c_double),
    ]
    library.step_motor_drivetrain_C.argtypes = [
        *([ctypes.c_double] * 7), ctypes.c_int, ctypes.c_int,
        *([ctypes.c_double] * 27), *([ctypes.POINTER(ctypes.c_double)] * 7),
    ]
    library.dist_point_to_polyline_mm.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.POINTER(_Point), ctypes.c_int]
    library.dist_point_to_polyline_mm.restype = ctypes.c_double
    return library


def _track_polyline(track: dict[str, Any]) -> list[tuple[float, float]]:
    """Produce a deterministic RobotTraceSim centre line for a track family."""
    length_mm = float(track["length"]) * 200.0
    difficulty = float(track["difficulty"])
    family = track.get("family", "mixed")
    points: list[tuple[float, float]] = []
    for index in range(401):
        fraction = index / 400.0
        x = fraction * length_mm
        cycles = {"oval": 1.0, "s-bend": 2.0, "slalom": 4.0, "hairpin": 1.5}.get(family, 2.5)
        amplitude = (40.0 + 150.0 * difficulty) * (1.7 if family == "hairpin" else 1.0)
        y = amplitude * math.sin(fraction * math.tau * cycles)
        points.append((x, y))
    return points


def _nearest_progress(x: float, y: float, points: list[tuple[float, float]]) -> tuple[float, float]:
    best_index, best_distance = min(
        enumerate(math.hypot(x - px, y - py) for px, py in points),
        key=lambda item: item[1],
    )
    return best_index / (len(points) - 1), best_distance / 1000.0


def to_robottrace_spec(package: dict[str, Any]) -> dict[str, Any]:
    """Translate the canonical package to RobotTraceSim's robot JSON shape.

    Canonical coordinates use ``x`` laterally and ``y`` longitudinally.  The
    upstream simulator calls those axes ``yMM`` and ``xMM`` respectively.
    Keeping this translation in one place prevents two representations of the
    design from becoming independent sources of truth.
    """
    geometry = package["geometry"]
    controller = package["controller"]
    half_track_mm = geometry["wheel_track"] * 500.0
    sensor_size_mm = geometry["sensor_size"] * 1000.0
    pwm_max = 4095
    return {
        "version": "robot-v1",
        "envelope": {
            "widthMM": geometry["body_length"] * 1000.0,
            "heightMM": geometry["body_width"] * 1000.0,
        },
        "origin": {"xMM": 0.0, "yMM": 0.0},
        "wheels": [
            {"id": "left", "xMM": 0.0, "yMM": half_track_mm, "widthMM": 22.0, "heightMM": geometry["wheel_radius"] * 2000.0},
            {"id": "right", "xMM": 0.0, "yMM": -half_track_mm, "widthMM": 22.0, "heightMM": geometry["wheel_radius"] * 2000.0},
        ],
        "sensors": [
            {
                "id": f"S{index + 1}",
                "xMM": sensor["y"] * 1000.0,
                "yMM": sensor["x"] * 1000.0,
                "sizeMM": sensor_size_mm,
            }
            for index, sensor in enumerate(geometry["sensor_positions"])
        ],
        "geometric_mechanical": {
            "body_length_mm": geometry["body_length"] * 1000.0,
            "body_width_mm": geometry["body_width"] * 1000.0,
            "wheel_radius_mm": geometry["wheel_radius"] * 1000.0,
            "track_mm": geometry["wheel_track"] * 1000.0,
            "mass_kg": geometry["mass"],
        },
        "controller": {
            "pwm_resolution_bits": 12,
            "pwm_max": pwm_max,
            "pwm_min": -pwm_max,
            "simulation_step_dt_ms": 50.0,
            "policy": deepcopy(controller),
        },
        "sensorsConfig": {
            "sensor_mode": "analog",
            "sensor_bits": 12,
            "value_of_line": pwm_max,
            "value_of_background": 0,
        },
    }


LINE_LOSS_SCALE = 8      # line-loss events at which reliability reaches 0
RMS_ERROR_SCALE = 0.15   # RMS centre-line error (m) at which precision reaches 0
TIME_SCALE = 60          # completion time (s) at which time quality reaches 0


def _score(metrics: dict[str, Any], weights: dict[str, float]) -> float:
    """Composite score.  Robustness and precision are earned only over the track actually covered.

    They are multiplied by progress (1.0 for a completed run), so a robot that does not move scores
    ~0 instead of collecting full robustness and precision credit for doing nothing.
    """
    reliability = max(0.0, 1 - metrics["line_loss_events"] / LINE_LOSS_SCALE)
    time_quality = max(0.0, 1 - metrics["completion_time"] / TIME_SCALE) if metrics["completion"] else 0
    precision = max(0.0, 1 - metrics["rms_error"] / RMS_ERROR_SCALE)
    covered = 1.0 if metrics["completion"] else max(0.0, min(1.0, metrics["progress"]))
    return round(
        weights["completion"] * int(metrics["completion"])
        + weights["progress"] * metrics["progress"]
        + covered * (weights["robustness"] * reliability + weights["precision"] * precision)
        + weights["time"] * time_quality,
        4,
    )


def score_description(weights: dict[str, float], simulator: dict[str, Any]) -> str:
    """Plain-language statement of the scoring rule, generated from the same weights and constants."""
    w = weights
    text = (
        f"score = {w['completion']}*completed + {w['progress']}*progress"
        f" + progress*({w['robustness']}*(1 - line_loss_events/{LINE_LOSS_SCALE})"
        f" + {w['precision']}*(1 - rms_error/{RMS_ERROR_SCALE}))"
        f" + {w['time']}*(1 - completion_time/{TIME_SCALE}) if completed."
        " progress is the fraction of the track covered (0 to 1); a completed run counts as progress 1 in the"
        " middle term, so a robot that does not move scores about 0. Each term is floored at 0."
        f" A run ends when the robot finishes, leaves the track, stalls, or reaches {simulator['max_steps']} steps."
    )
    if simulator.get("stall_steps"):
        text += (
            f" A run stalls (ends early) if progress rises by less than {simulator.get('stall_min_progress', 0.002)}"
            f" over {simulator['stall_steps']} consecutive steps."
        )
    return text


def run_trial(package: dict[str, Any], track: dict[str, Any], seed: int, config: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_package(package, config["design_bounds"])
    except ValidationError as error:
        return {"adapter_version": ADAPTER_VERSION, "termination_reason": "invalid_design", "error": str(error), "seed": seed, "track": track["id"], "score": 0, "telemetry": []}

    robot_spec = to_robottrace_spec(package)
    run_id = digest({"adapter": ADAPTER_VERSION, "package": package, "track": track, "seed": seed})

    controller = package["controller"]
    if not all(math.isfinite(float(controller[key])) for key in ("base_speed", "kp", "ki", "kd")):
        return {"adapter_version": ADAPTER_VERSION, "run_id": run_id, "termination_reason": "controller_error", "error": "non-finite controller value", "seed": seed, "track": track["id"], "score": 0, "telemetry": []}
    if not any(abs(weight) > 1e-9 for weight in controller["sensor_weights"]):
        return {"adapter_version": ADAPTER_VERSION, "run_id": run_id, "termination_reason": "controller_error", "error": "controller has no steering signal", "seed": seed, "track": track["id"], "score": 0, "telemetry": []}

    rng = random.Random(f"{seed}:{digest(package)}:{track['id']}")
    library = _native_library()
    points = _track_polyline(track)
    polyline = (_Point * len(points))(*(_Point(x, y) for x, y in points))
    count = len(robot_spec["sensors"])
    sensor_sizes = (ctypes.c_double * count)(*(sensor["sizeMM"] for sensor in robot_spec["sensors"]))
    tape_half = float(track.get("tape_width", 0.025)) * 500.0
    dt = 0.01
    max_steps = int(config["simulator"]["max_steps"])
    x_m = y_m = heading = velocity = omega = current_left = current_right = 0.0
    integral = previous_signal = last_direction = 0.0
    telemetry: list[dict[str, Any]] = []
    termination = "timeout"
    controller_errors = 0
    line_was_lost = False
    line_loss_events = 0
    motor_bias = 1.0 + rng.uniform(-config["evaluation"]["noise"], config["evaluation"]["noise"])
    for step in range(max_steps):
        cos_h, sin_h = math.cos(heading), math.sin(heading)
        world_x = (ctypes.c_double * count)()
        world_y = (ctypes.c_double * count)()
        for index, sensor in enumerate(robot_spec["sensors"]):
            local_x, local_y = sensor["xMM"], sensor["yMM"]
            world_x[index] = x_m * 1000.0 + local_x * cos_h - local_y * sin_h
            world_y[index] = y_m * 1000.0 + local_x * sin_h + local_y * cos_h
        coverage = (ctypes.c_double * count)()
        library.estimate_sensors_coverage_batch_C(world_x, world_y, count, polyline, len(points), tape_half, sensor_sizes, 0.0, 3, coverage)
        sensors = [max(0.0, min(1.0, coverage[index] + rng.gauss(0, config["evaluation"]["noise"] * 0.05))) for index in range(count)]
        observation = {"timestep": step, "sensors": sensors}
        validate_observation(observation)
        visible = sum(sensors)
        lost = visible < 0.05
        if lost and not line_was_lost:
            line_loss_events += 1
        line_was_lost = lost
        try:
            if lost:
                policy = controller["line_loss"]
                signal = 0.0 if policy == "stop" else (-1.0 if policy == "search_left" else (1.0 if policy == "search_right" else last_direction))
                throttle = 0.0 if policy == "stop" else 0.35
            else:
                signal = sum(weight * reading for weight, reading in zip(controller["sensor_weights"], sensors)) / visible
                last_direction = -1.0 if signal < 0 else 1.0
                throttle = 1.0
            integral = max(-2.0, min(2.0, integral + signal * dt))
            derivative = (signal - previous_signal) / dt
            previous_signal = signal
            turn = controller["kp"] * signal + controller["ki"] * integral + controller["kd"] * derivative
            base_pwm = 4095.0 * min(1.0, controller["base_speed"] / 2.0) * throttle
            pwm_left = int(max(-4095, min(4095, base_pwm - turn * 350)))
            pwm_right = int(max(-4095, min(4095, (base_pwm + turn * 350) * motor_bias)))
        except Exception:
            controller_errors += 1
            termination = "controller_error"
            break
        outputs = [ctypes.c_double() for _ in range(7)]
        args = [
            x_m, y_m, heading, velocity, omega, current_left, current_right,
            pwm_left, pwm_right, -4095.0, 4095.0, 0.0, 0.0,
            7.4, 0.05, 0.02, 0.2, 3.0, 0.0001, 0.0015, 0.002,
            0.0, 0.0, 20.0, 0.9, robot_spec["geometric_mechanical"]["mass_kg"],
            robot_spec["geometric_mechanical"]["track_mm"] / 1000.0,
            robot_spec["geometric_mechanical"]["wheel_radius_mm"] / 1000.0,
            max(1e-5, robot_spec["geometric_mechanical"]["mass_kg"] * (robot_spec["geometric_mechanical"]["track_mm"] / 1000.0) ** 2 / 12),
            0.005, 1.225, 0.02, 1.0, 0.8, 3.0, dt,
        ]
        converted = [ctypes.c_int(value) if index in (7, 8) else ctypes.c_double(value) for index, value in enumerate(args)]
        library.step_motor_drivetrain_C(*converted, *(ctypes.byref(value) for value in outputs))
        x_m, y_m, heading, velocity, omega, current_left, current_right = (value.value for value in outputs)
        progress, error = _nearest_progress(x_m * 1000.0, y_m * 1000.0, points)
        telemetry.append({
            "step": step,
            "progress": round(progress, 6),
            "error": round(error, 6),
            "speed": round(velocity, 6),
            # These are the recorded RobotTraceSim reference pose.  They are
            # deliberately persisted rather than reconstructed by artifact
            # renderers, which keeps diagnostic views faithful to the race.
            "x": round(x_m, 9),
            "y": round(y_m, 9),
            "heading": round(heading, 9),
            "sensors": [round(value, 9) for value in sensors],
            "line_lost": lost,
        })
        if progress >= 0.995:
            termination = "finished"
            break
        stall_steps = int(config["simulator"].get("stall_steps") or 0)
        if stall_steps and len(telemetry) > stall_steps and progress - telemetry[-1 - stall_steps]["progress"] < float(config["simulator"].get("stall_min_progress", 0.002)):
            termination = "stalled"
            break
        if error > max(0.06, tape_half / 1000.0 + robot_spec["envelope"]["heightMM"] / 4000.0):
            termination = "off_track"
            break
    progress = telemetry[-1]["progress"] if telemetry else 0.0
    completion = termination == "finished"
    errors = [abs(point["error"]) for point in telemetry]
    metrics = {
        "completion": completion,
        "progress": round(progress, 6),
        "completion_time": round(len(telemetry) * dt, 4),
        "rms_error": round(math.sqrt(sum(value * value for value in errors) / len(errors)), 6),
        "max_error": round(max(errors), 6),
        "line_loss_events": line_loss_events,
        "steering_oscillation": round(sum(abs(telemetry[i]["error"] - telemetry[i - 1]["error"]) for i in range(1, len(telemetry))), 6),
        "control_effort": round(controller["kp"] * sum(errors), 6),
        "controller_errors": controller_errors,
        "noise_robustness": round(max(0.0, 1 - config["evaluation"]["noise"] - max(errors)), 6),
    }
    return {"adapter_version": ADAPTER_VERSION, "run_id": run_id, "termination_reason": termination, "seed": seed, "track": track["id"], "metrics": metrics, "score": _score(metrics, config["score"]), "telemetry": telemetry}
