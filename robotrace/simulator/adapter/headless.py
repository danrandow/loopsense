from __future__ import annotations

import math
import random
from typing import Any

from orchestrator.io import digest
from orchestrator.validators import ValidationError, validate_observation, validate_package


def _score(metrics: dict[str, Any], weights: dict[str, float]) -> float:
    reliability = max(0.0, 1 - metrics["line_loss_events"] / 8)
    time_quality = max(0.0, 1 - metrics["completion_time"] / 60) if metrics["completion"] else 0
    precision = max(0.0, 1 - metrics["rms_error"] / 0.15)
    return round(
        weights["completion"] * int(metrics["completion"])
        + weights["progress"] * metrics["progress"]
        + weights["robustness"] * reliability
        + weights["time"] * time_quality
        + weights["precision"] * precision,
        4,
    )


def run_trial(package: dict[str, Any], track: dict[str, Any], seed: int, config: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_package(package, config["design_bounds"])
    except ValidationError as error:
        return {"termination_reason": "invalid_design", "error": str(error), "seed": seed, "track": track["id"], "score": 0, "telemetry": []}

    controller = package["controller"]
    if not all(math.isfinite(float(controller[key])) for key in ("base_speed", "kp", "ki", "kd")):
        return {"termination_reason": "controller_error", "error": "non-finite controller value", "seed": seed, "track": track["id"], "score": 0, "telemetry": []}
    if not any(abs(weight) > 1e-9 for weight in controller["sensor_weights"]):
        return {"termination_reason": "controller_error", "error": "controller has no steering signal", "seed": seed, "track": track["id"], "score": 0, "telemetry": []}

    rng = random.Random(f"{seed}:{digest(package)}:{track['id']}")
    geometry = package["geometry"]
    sensor_spread = max(sensor["x"] for sensor in geometry["sensor_positions"]) - min(sensor["x"] for sensor in geometry["sensor_positions"])
    damping = controller["kd"] / (1 + controller["kp"])
    tracking = 0.38 + sensor_spread * 2.7 + min(controller["kp"], 8) * 0.055 + min(damping, 1) * 0.18
    challenge = track["difficulty"] + config["evaluation"]["noise"] * rng.uniform(-1, 1)
    progress = min(1.0, max(0.05, tracking / max(0.2, challenge + controller["base_speed"] * 0.12)))
    completion = progress >= 0.98
    termination = "finished" if completion else ("off_track" if progress < 0.82 else "timeout")
    steps = min(config["simulator"]["max_steps"], max(10, int(track["length"] / controller["base_speed"] * 20 * progress)))
    telemetry = []
    for step in range(steps):
        fraction = step / max(1, steps - 1) * progress
        error = (challenge - tracking) * 0.07 * math.sin(fraction * math.pi * 4) + rng.gauss(0, 0.004)
        observation = {"timestep": step, "sensors": [max(0.0, 1 - abs(error + w * 0.01) / 0.08) for w in controller["sensor_weights"]]}
        validate_observation(observation)
        telemetry.append({"step": step, "progress": round(fraction, 6), "error": round(error, 6), "speed": controller["base_speed"]})
    errors = [abs(point["error"]) for point in telemetry]
    metrics = {
        "completion": completion,
        "progress": round(progress, 6),
        "completion_time": round(steps / 20, 4),
        "rms_error": round(math.sqrt(sum(value * value for value in errors) / len(errors)), 6),
        "max_error": round(max(errors), 6),
        "line_loss_events": sum(1 for value in errors if value > 0.06),
        "steering_oscillation": round(sum(abs(telemetry[i]["error"] - telemetry[i - 1]["error"]) for i in range(1, len(telemetry))), 6),
        "control_effort": round(controller["kp"] * sum(errors), 6),
        "controller_errors": 0,
        "noise_robustness": round(max(0.0, 1 - challenge + tracking), 6),
    }
    return {"termination_reason": termination, "seed": seed, "track": track["id"], "metrics": metrics, "score": _score(metrics, config["score"]), "telemetry": telemetry}
