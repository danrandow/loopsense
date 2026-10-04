from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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


ACTOR_CONTRACTS = {
    "geometry_builder": '{"geometry": {"sensor_positions": [{"x": number, "y": number}], "sensor_size": number, "wheel_track": number, "wheel_radius": number, "body_width": number, "body_length": number, "mass": number}, "intent": string, "feedback_request": {"measurements": [supported names], "questions": [string]}}',
    "robot_integrator": '{"geometry": exact supplied geometry, "controller": {"base_speed": number, "kp": number, "ki": number, "kd": number, "sensor_weights": [one number per sensor], "line_loss": "stop|search_left|search_right|last_direction"}, "observation_request": {"measurements": [supported names], "questions": [string]}, "notes": string}',
    "optimizer": '{"geometry": {"sensor_positions": [{"x": number, "y": number}], "sensor_size": number, "wheel_track": number, "wheel_radius": number, "body_width": number, "body_length": number, "mass": number}, "controller": {"base_speed": number, "kp": number, "ki": number, "kd": number, "sensor_weights": [one number per sensor], "line_loss": "stop|search_left|search_right|last_direction"}, "observation_request": {"measurements": [supported names], "questions": [string]}, "notes": string}',
    "evaluator": '{"decision": "ship|revise", "selected_candidate": exact candidate_id when shipping or null when revising, "rationale": string, "feedback": [specific requested changes]}',
    "integration_feedback": '{"summary": string, "requests": [string]}',
}

ACTOR_INSTRUCTIONS = {
    "geometry_builder": "Design valid bounded robot geometry and request only supported measurements. Explain the geometry intent.",
    "robot_integrator": "Preserve the supplied geometry exactly, add a valid controller, request only supported measurements, and explain the integration choices.",
    "optimizer": "Produce one complete valid robot candidate within every supplied geometry and controller constraint.",
    "evaluator": "Evaluate the exact supplied candidate. Either request specific revisions or ship that candidate without changing it.",
    "integration_feedback": "Translate the supplied race measurements into concise, geometry-specific integration feedback.",
}


def _parse_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    value = json.loads(cleaned)
    if not isinstance(value, dict):
        raise RuntimeError("model response must be one JSON object")
    return value


class OpenRouterClient:
    def __init__(self, config: dict[str, Any]):
        self.config = config["model"]
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")

    def call(self, actor: str, context: dict[str, Any]) -> ModelResponse:
        contract = ACTOR_CONTRACTS[actor]
        system = "You are one actor in a controlled robot-design experiment. Use only the supplied context. Return JSON only, with no markdown or commentary. Never invent file paths or commands."
        user = f"Actor: {actor}\nJob: {ACTOR_INSTRUCTIONS[actor]}\nRequired output contract: {contract}\nAll supplied constraints are mandatory.\nContext:\n{json.dumps(context, sort_keys=True)}"
        body = {
            "model": self.config["id"],
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": self.config.get("temperature", 0),
            "max_tokens": self.config.get("max_output_tokens", 2000),
            "response_format": {"type": "json_object"},
        }
        request = Request(
            self.config.get("base_url", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": self.config.get("site_url", "https://randowmaps.com"), "X-OpenRouter-Title": "LoopSense Robot Race"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.config.get("timeout_seconds", 120)) as response:
                payload = json.loads(response.read())
        except HTTPError as error:
            detail = error.read().decode(errors="replace")[:1000]
            raise RuntimeError(f"OpenRouter returned HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise RuntimeError(f"OpenRouter request failed: {error.reason}") from error
        usage = payload.get("usage", {})
        content = payload["choices"][0]["message"]["content"]
        return ModelResponse(_parse_json_object(content), payload.get("id", "openrouter-unknown"), int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)))


def validate_openrouter_api_key(api_key: str, base_url: str = "https://openrouter.ai/api/v1", timeout_seconds: int = 30) -> None:
    key = api_key.strip()
    if not key:
        raise RuntimeError("Enter an OpenRouter API key")
    request = Request(
        base_url.rstrip("/") + "/key",
        headers={"Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read())
    except HTTPError as error:
        raise RuntimeError(f"OpenRouter API key check failed (HTTP {error.code}); paste a current plaintext API key") from error
    except URLError as error:
        raise RuntimeError(f"OpenRouter API key check could not connect: {error.reason}") from error
    if not isinstance(payload.get("data"), dict):
        raise RuntimeError("OpenRouter API key check returned an unexpected response")


def make_client(config: dict[str, Any]) -> ModelClient:
    provider = config["model"]["provider"]
    if provider == "mock":
        return DeterministicMockClient()
    if provider == "openrouter":
        return OpenRouterClient(config)
    raise RuntimeError(f"unsupported model provider: {provider}")
