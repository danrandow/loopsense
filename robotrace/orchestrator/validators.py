from __future__ import annotations

from typing import Any

MEASUREMENTS = {
    "completion", "progress", "completion_time", "rms_error", "max_error",
    "line_loss_events", "steering_oscillation", "control_effort",
    "controller_errors", "noise_robustness",
}
POSE_FIELDS = {"x", "y", "heading", "position", "global_position", "pose"}


class ValidationError(ValueError):
    pass


def _number(value: Any, name: str, low: float, high: float) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not low <= value <= high:
        raise ValidationError(f"{name} must be between {low} and {high}")


def validate_geometry(geometry: dict[str, Any], bounds: dict[str, Any]) -> None:
    required = {"sensor_positions", "sensor_size", "wheel_track", "wheel_radius", "body_width", "body_length", "mass"}
    if set(geometry) != required:
        raise ValidationError(f"geometry keys must be exactly {sorted(required)}")
    count_low, count_high = bounds["sensor_count"]
    sensors = geometry["sensor_positions"]
    if not isinstance(sensors, list) or not count_low <= len(sensors) <= count_high:
        raise ValidationError("sensor count outside bounds")
    for index, sensor in enumerate(sensors):
        if set(sensor) != {"x", "y"}:
            raise ValidationError(f"sensor {index} must contain only x and y")
        _number(sensor["x"], f"sensor {index} x", *bounds["sensor_x"])
        _number(sensor["y"], f"sensor {index} y", *bounds["sensor_y"])
    if geometry["sensor_size"] not in bounds["sensor_sizes"]:
        raise ValidationError("sensor_size is not allowed")
    for field in ("wheel_track", "wheel_radius", "body_width", "body_length", "mass"):
        _number(geometry[field], field, *bounds[field])


def validate_controller(controller: dict[str, Any], sensor_count: int) -> None:
    required = {"base_speed", "kp", "ki", "kd", "sensor_weights", "line_loss"}
    if set(controller) != required:
        raise ValidationError(f"controller keys must be exactly {sorted(required)}")
    _number(controller["base_speed"], "base_speed", 0.05, 2)
    _number(controller["kp"], "kp", 0, 20)
    _number(controller["ki"], "ki", 0, 5)
    _number(controller["kd"], "kd", 0, 10)
    weights = controller["sensor_weights"]
    if not isinstance(weights, list) or len(weights) != sensor_count:
        raise ValidationError("sensor_weights length must equal sensor count")
    for index, weight in enumerate(weights):
        _number(weight, f"sensor weight {index}", -2, 2)
    if controller["line_loss"] not in {"stop", "search_left", "search_right", "last_direction"}:
        raise ValidationError("unsupported line_loss policy")


def validate_measurement_request(request: dict[str, Any]) -> None:
    if not isinstance(request.get("measurements"), list):
        raise ValidationError("measurements must be a list")
    unsupported = set(request["measurements"]) - MEASUREMENTS
    if unsupported:
        raise ValidationError(f"unsupported measurements: {sorted(unsupported)}")


def validate_observation(observation: dict[str, Any]) -> None:
    leaked = POSE_FIELDS.intersection(observation)
    if leaked:
        raise ValidationError(f"privileged pose fields leaked: {sorted(leaked)}")


def validate_package(package: dict[str, Any], bounds: dict[str, Any]) -> None:
    if set(package) != {"geometry", "controller", "observation_request"}:
        raise ValidationError("package contains unexpected fields")
    validate_geometry(package["geometry"], bounds)
    validate_controller(package["controller"], len(package["geometry"]["sensor_positions"]))
    validate_measurement_request(package["observation_request"])

