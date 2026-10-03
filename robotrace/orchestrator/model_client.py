from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .io import digest


@dataclass(frozen=True)
class ModelResponse:
    output: dict[str, Any]
    request_id: str
    input_tokens: int
    output_tokens: int


class ModelClient(Protocol):
    def call(self, actor: str, context: dict[str, Any]) -> ModelResponse: ...


class DeterministicMockClient:
    """Offline contract client for tests and smoke runs; never reads the run tree."""

    def call(self, actor: str, context: dict[str, Any]) -> ModelResponse:
        iteration = int(context["iteration"])
        sensor_positions = [{"x": x, "y": 0.05} for x in (-0.06, -0.03, 0.0, 0.03, 0.06)]
        geometry = {
            "sensor_positions": sensor_positions,
            "sensor_size": 0.012,
            "wheel_track": 0.12,
            "wheel_radius": 0.035,
            "body_width": 0.12,
            "body_length": 0.16,
            "mass": 0.8,
        }
        controller = {
            "base_speed": round(0.42 + iteration * 0.025, 4),
            "kp": round(4.2 + iteration * 0.25, 4),
            "ki": 0.03,
            "kd": 0.9,
            "sensor_weights": [-1.0, -0.5, 0.0, 0.5, 1.0],
            "line_loss": "last_direction",
        }
        request = {"measurements": ["completion", "progress", "completion_time", "rms_error", "line_loss_events", "noise_robustness"], "questions": ["Which failure mode limits the next design?"]}
        if actor == "geometry_builder":
            output = {"geometry": geometry, "intent": "Increase usable lateral line sensing while preserving a compact body.", "feedback_request": request}
        elif actor in {"robot_integrator", "optimizer"}:
            supplied_geometry = context.get("geometry", geometry)
            output = {"geometry": supplied_geometry, "controller": controller, "observation_request": request, "notes": "Conservative PID with derivative damping."}
        elif actor == "evaluator":
            output = {"decision": "ship", "selected_candidate": context["candidate_id"], "rationale": "Candidate is valid and budget is better spent on world evidence."}
        elif actor == "integration_feedback":
            output = {"summary": "The geometry integrated cleanly; preserve symmetry and use race error to tune spread.", "requests": ["Preserve sensor ordering."]}
        else:
            raise ValueError(f"unknown actor: {actor}")
        serialized_context = str(context)
        serialized_output = str(output)
        return ModelResponse(output, f"mock-{digest({'actor': actor, 'context': context})[:16]}", max(1, len(serialized_context) // 4), max(1, len(serialized_output) // 4))


def make_client(config: dict[str, Any]) -> ModelClient:
    if config["model"]["provider"] != "mock":
        raise RuntimeError("Only the offline mock provider is configured. Add an explicit provider adapter before a recorded run.")
    return DeterministicMockClient()

