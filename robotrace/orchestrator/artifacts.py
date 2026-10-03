from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .io import atomic_write, digest, write_json


def write_manifest(directory: Path, entity: str, files: list[str], inputs: list[str]) -> None:
    manifest = {"entity": entity, "files": files, "input_allowlist": inputs}
    manifest["manifest_hash"] = digest(manifest)
    write_json(directory / "manifest.json", manifest)


def trajectory_svg(trial: dict[str, Any], path: Path) -> None:
    points = trial.get("telemetry", [])
    polyline = " ".join(f"{20 + p['progress'] * 720:.2f},{150 + p['error'] * 700:.2f}" for p in points)
    colour = "#1b8a5a" if trial["termination_reason"] == "finished" else "#c84a3d"
    title = html.escape(f"{trial['track']} seed {trial['seed']} — {trial['termination_reason']}")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="260" viewBox="0 0 800 260">
<rect width="800" height="260" fill="#f7f4ec"/><text x="20" y="28" font-family="sans-serif" font-size="18">{title}</text>
<line x1="20" y1="150" x2="760" y2="150" stroke="#222" stroke-width="18" opacity=".15"/><line x1="20" y1="150" x2="760" y2="150" stroke="#222" stroke-width="2" stroke-dasharray="8 7"/>
<polyline points="{polyline}" fill="none" stroke="{colour}" stroke-width="3"/><circle cx="20" cy="150" r="6" fill="#2457a7"/><circle cx="{20 + (points[-1]['progress'] if points else 0) * 720:.2f}" cy="{150 + (points[-1]['error'] if points else 0) * 700:.2f}" r="7" fill="{colour}"/>
<text x="20" y="235" font-family="sans-serif" font-size="14">score {trial.get('score', 0):.2f}</text></svg>'''
    atomic_write(path, svg)


def summary_svg(condition: str, iteration: int, trials: list[dict[str, Any]], path: Path) -> None:
    bars = []
    for index, trial in enumerate(trials):
        width = min(620, trial.get("score", 0) * 0.7)
        y = 85 + index * 46
        bars.append(f'<text x="20" y="{y + 18}" font-family="sans-serif" font-size="13">{html.escape(trial["track"])} / {trial["seed"]}</text><rect x="180" y="{y}" width="{width:.1f}" height="24" fill="#326da8"/><text x="{190 + width:.1f}" y="{y + 18}" font-family="sans-serif" font-size="13">{trial.get("score", 0):.1f}</text>')
    body = "".join(bars)
    height = max(190, 120 + 46 * len(trials))
    atomic_write(path, f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{height}"><rect width="100%" height="100%" fill="#f7f4ec"/><text x="20" y="38" font-family="sans-serif" font-size="24">{html.escape(condition)} — iteration {iteration}</text>{body}</svg>')


def leaderboard(run_root: Path, results: list[dict[str, Any]]) -> None:
    rows = []
    for result in sorted(results, key=lambda item: (item["iteration"], item["condition"])):
        signed = dict(result)
        claimed = signed.pop("artifact_hash")
        if digest(signed) != claimed:
            raise ValueError("leaderboard input hash mismatch")
        rows.append({"condition": result["condition"], "iteration": result["iteration"], "score": result["score"], "artifact_hash": claimed})
    payload = {"rows": rows, "source_hashes": [row["artifact_hash"] for row in rows]}
    payload["leaderboard_hash"] = digest(payload)
    write_json(run_root / "leaderboard.json", payload)
    markdown = "# Robot Race leaderboard\n\n| Condition | Iteration | Score |\n|---|---:|---:|\n" + "".join(f"| {r['condition']} | {r['iteration']} | {r['score']:.3f} |\n" for r in rows)
    atomic_write(run_root / "leaderboard.md", markdown)
    max_score = max((row["score"] for row in rows), default=1)
    bars = "".join(f'<text x="20" y="{80+i*40}" font-family="sans-serif">{html.escape(r["condition"])} {r["iteration"]}</text><rect x="180" y="{62+i*40}" width="{560*r["score"]/max_score:.1f}" height="24" fill="#326da8"/>' for i, r in enumerate(rows))
    atomic_write(run_root / "leaderboard.svg", f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{120+40*len(rows)}"><rect width="100%" height="100%" fill="#f7f4ec"/><text x="20" y="32" font-family="sans-serif" font-size="22">Robot Race leaderboard</text>{bars}</svg>')


def scenario_yaml(base_map: str, condition: str, iteration: int, public_summary_url: str, leaderboard_url: str, result: dict[str, Any]) -> str:
    if public_summary_url.startswith(("/", "file:")) or not public_summary_url.startswith("https://"):
        raise ValueError("summary URL must be a public HTTPS URL")
    return f'''map:\n  extends: "{base_map}"\n  scenario: "iteration-{iteration}"\n  dimensions:\n    condition: "{condition}"\n    iteration: {iteration}\nentities:\n  entity2:\n    status: complete\n    notes: |\n      Score: {result["score"]:.4f}\n      [Open iteration race summary]({public_summary_url})\n      [Open shared leaderboard]({leaderboard_url})\n'''

