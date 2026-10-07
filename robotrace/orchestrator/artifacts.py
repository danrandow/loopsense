from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from .io import atomic_write, digest, write_json

TRACK_VIEW_RENDERER_VERSION = "track-view-svg-v1"


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


def _f(value: float) -> str:
    """Stable SVG number formatting without negative zero."""
    rounded = round(float(value), 3)
    if rounded == 0:
        rounded = 0.0
    return f"{rounded:.3f}"


def _svg_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


def track_view_svg(
    trial: dict[str, Any], package: dict[str, Any], track: dict[str, Any], path: Path,
    *, experiment: str, condition: str, iteration: int,
) -> None:
    """Write the canonical, deterministic visual record of a trial."""
    from simulator.adapter.headless import _track_polyline, to_robottrace_spec

    telemetry = trial.get("telemetry", [])
    robot = to_robottrace_spec(package)
    centreline = _track_polyline(track)
    body_length = float(robot["envelope"]["widthMM"])
    body_width = float(robot["envelope"]["heightMM"])
    margin = max(body_length, body_width)
    xs = [p[0] for p in centreline]
    ys = [p[1] for p in centreline]
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin
    world_w, world_h = max_x - min_x, max_y - min_y
    view_x, view_y, view_w, view_h = 40.0, 118.0, 920.0, 500.0
    scale = min(view_w / world_w, view_h / world_h)
    offset_x = view_x + (view_w - world_w * scale) / 2 - min_x * scale
    offset_y = view_y + (view_h - world_h * scale) / 2 + max_y * scale

    def xy(x_mm: float, y_mm: float) -> tuple[float, float]:
        return offset_x + x_mm * scale, offset_y - y_mm * scale

    def pose(point: dict[str, Any]) -> tuple[float, float, float]:
        return float(point.get("x", 0)) * 1000, float(point.get("y", 0)) * 1000, float(point.get("heading", 0))

    centre_points = " ".join(f"{_f(xy(x, y)[0])},{_f(xy(x, y)[1])}" for x, y in centreline)
    allowed_m = max(0.06, float(track.get("tape_width", 0.025)) / 2 + body_width / 4000)
    colours = {"green": "#167d6b", "amber": "#d18b00", "red": "#d1495b", "dark-red": "#721c24"}

    segments: list[str] = []
    for index in range(1, len(telemetry)):
        before, after = telemetry[index - 1], telemetry[index]
        x1, y1, _ = pose(before)
        x2, y2, _ = pose(after)
        error = abs(float(after.get("error", 0)))
        ratio = error / allowed_m if allowed_m else float("inf")
        band = "green" if ratio <= .25 else "amber" if ratio <= .75 else "red" if ratio <= 1 else "dark-red"
        a, b = xy(x1, y1), xy(x2, y2)
        segments.append(f'<line data-step="{int(after.get("step", index))}" data-error-band="{band}" x1="{_f(a[0])}" y1="{_f(a[1])}" x2="{_f(b[0])}" y2="{_f(b[1])}" stroke="{colours[band]}" stroke-width="2.600" stroke-linecap="round"/>')

    snapshot_points: list[tuple[str, dict[str, Any]]] = []
    if telemetry:
        achieved = float(telemetry[-1].get("progress", 0))
        snapshot_points.append(("start", telemetry[0]))
        for fraction in (.25, .5, .75):
            target = achieved * fraction
            selected = min(telemetry, key=lambda item: (abs(float(item.get("progress", 0)) - target), int(item.get("step", 0))))
            snapshot_points.append((f"{int(fraction * 100)}%", selected))
        snapshot_points.append(("finish" if trial.get("termination_reason") == "finished" else "terminal", telemetry[-1]))
    snapshot_steps = {label: int(item.get("step", 0)) for label, item in snapshot_points}

    snapshot_svg: list[str] = []
    for label, point in snapshot_points:
        px, py, heading = pose(point)
        vx, vy = xy(px, py)
        angle = -heading * 180 / 3.141592653589793
        parts = [f'<g class="robot-snapshot" data-label="{label}" data-step="{int(point.get("step", 0))}" transform="translate({_f(vx)} {_f(vy)}) rotate({_f(angle)}) scale({_f(scale)})">']
        parts.append(f'<rect class="body" x="{_f(-body_length/2)}" y="{_f(-body_width/2)}" width="{_f(body_length)}" height="{_f(body_width)}" rx="8.000" fill="#5b67a5" fill-opacity=".18" stroke="#35406f" stroke-width="{_f(1.5/scale)}"/>')
        for wheel in robot["wheels"]:
            # RobotTraceSim x is forward and y is lateral; SVG y is inverted.
            wx, wy = float(wheel["xMM"]), -float(wheel["yMM"])
            ww, wh = float(wheel["widthMM"]), float(wheel["heightMM"])
            parts.append(f'<rect class="wheel {wheel["id"]}" x="{_f(wx-ww/2)}" y="{_f(wy-wh/2)}" width="{_f(ww)}" height="{_f(wh)}" fill="#252525"/>')
        for sensor in robot["sensors"]:
            sx, sy, size = float(sensor["xMM"]), -float(sensor["yMM"]), float(sensor["sizeMM"])
            parts.append(f'<circle class="sensor" data-sensor="{_svg_text(sensor["id"])}" cx="{_f(sx)}" cy="{_f(sy)}" r="{_f(size/2)}" fill="#21a7c7" fill-opacity=".50" stroke="#07566a" stroke-width="{_f(1/scale)}"/>')
        parts.extend([
            f'<circle class="reference-origin" cx="0" cy="0" r="{_f(3/scale)}" fill="#fff" stroke="#111" stroke-width="{_f(1/scale)}"/>',
            f'<line class="heading" x1="0" y1="0" x2="{_f(body_length*.7)}" y2="0" stroke="#111" stroke-width="{_f(2/scale)}" marker-end="url(#heading-arrow)"/>',
            '</g>',
        ])
        snapshot_svg.append("".join(parts))

    events: list[dict[str, Any]] = []
    previously_lost = False
    for point in telemetry:
        lost = bool(point.get("line_lost", False))
        if lost and not previously_lost:
            events.append({"type": "line-loss", "step": int(point.get("step", 0)), "point": point})
        previously_lost = lost
    terminal = trial.get("termination_reason")
    if terminal in {"controller_error", "off_track", "timeout", "finished"}:
        event_point = telemetry[-1] if telemetry else {"x": 0, "y": 0, "heading": 0, "step": 0}
        events.append({"type": "finish-crossing" if terminal == "finished" else terminal.replace("_", "-"), "step": int(event_point.get("step", 0)), "point": event_point})
    event_steps: dict[str, list[int]] = {}
    event_svg: list[str] = []
    symbols = {"line-loss": "!", "controller-error": "E", "off-track": "×", "timeout": "T", "finish-crossing": "✓"}
    for event in events:
        event_steps.setdefault(event["type"], []).append(event["step"])
        ex, ey, _ = pose(event["point"])
        vx, vy = xy(ex, ey)
        event_svg.append(f'<g class="event {event["type"]}" data-event="{event["type"]}" data-step="{event["step"]}"><circle cx="{_f(vx)}" cy="{_f(vy)}" r="9.000" fill="#fff" stroke="#111" stroke-width="2"/><text x="{_f(vx)}" y="{_f(vy+4)}" text-anchor="middle" font-size="11" font-weight="700">{symbols[event["type"]]}</text></g>')

    result_for_hash = {key: value for key, value in trial.items() if key not in {"telemetry", "trial_id"}}
    metadata = {
        "adapter_version": trial.get("adapter_version"), "condition": condition,
        "event_steps": event_steps, "experiment": experiment, "iteration": iteration,
        "package_hash": digest(package), "renderer_version": TRACK_VIEW_RENDERER_VERSION,
        "result_hash": digest(result_for_hash), "run_id": trial.get("run_id"),
        "schema_version": "robotrace-track-view-v1", "score": trial.get("score", 0),
        "seed": trial.get("seed"), "simulator_version": trial.get("adapter_version"),
        "snapshot_steps": snapshot_steps, "telemetry_hash": digest(telemetry),
        "termination_reason": terminal, "track": track.get("id"), "track_hash": digest(track),
        "view_transform": {"offset_x": round(offset_x, 6), "offset_y": round(offset_y, 6), "scale": round(scale, 9), "y_inverted": True},
        "world_bounds_mm": {"max_x": round(max_x, 6), "max_y": round(max_y, 6), "min_x": round(min_x, 6), "min_y": round(min_y, 6)},
    }
    metadata_json = html.escape(json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    progress = trial.get("metrics", {}).get("progress", telemetry[-1].get("progress", 0) if telemetry else 0)
    elapsed = len(telemetry) * .01
    header = f'{condition} · iteration {iteration} · {track.get("id")} · seed {trial.get("seed")} · {_svg_text(terminal)} · score {float(trial.get("score", 0)):.4f} · progress {float(progress):.1%} · simulated {elapsed:.2f}s'
    run_label = f'run ID: {_svg_text(trial.get("run_id", "n/a"))}'
    tape_width_px = float(track.get("tape_width", .025)) * 1000 * scale
    start = xy(*centreline[0]); finish = xy(*centreline[-1])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="1000" height="760" viewBox="0 0 1000 760">
<title>Robot Race track view: {_svg_text(track.get("id"))}, seed {_svg_text(trial.get("seed"))}</title>
<desc>Exact track, recorded trajectory, robot snapshots, and terminal events for a {_svg_text(terminal)} trial.</desc>
<metadata id="robotrace-metadata">{metadata_json}</metadata>
<defs><marker id="direction-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#30343b"/></marker><marker id="heading-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#111"/></marker></defs>
<g id="background"><rect width="1000" height="760" fill="#f8f5ed"/><rect x="20" y="92" width="960" height="546" rx="8" fill="#fff" stroke="#d7d2c8"/><text x="24" y="30" font-family="sans-serif" font-size="18" font-weight="700">Robot Race trial</text><text x="24" y="55" font-family="sans-serif" font-size="13">{header}</text><text x="24" y="76" font-family="monospace" font-size="10">{run_label}</text></g>
<g id="track-envelope"><polyline points="{centre_points}" fill="none" stroke="#c4c7ca" stroke-width="{_f(tape_width_px)}" stroke-linecap="round" stroke-linejoin="round"/></g>
<g id="track-centreline"><polyline points="{centre_points}" fill="none" stroke="#30343b" stroke-width="1.300" stroke-dasharray="6 5"/><line x1="{_f(xy(*centreline[15])[0])}" y1="{_f(xy(*centreline[15])[1])}" x2="{_f(xy(*centreline[30])[0])}" y2="{_f(xy(*centreline[30])[1])}" stroke="#30343b" stroke-width="2" marker-end="url(#direction-arrow)"/></g>
<g id="start-finish"><line x1="{_f(start[0])}" y1="{_f(start[1]-15)}" x2="{_f(start[0])}" y2="{_f(start[1]+15)}" stroke="#2364aa" stroke-width="4"/><text x="{_f(start[0]+6)}" y="{_f(start[1]-18)}" font-family="sans-serif" font-size="11">START</text><line x1="{_f(finish[0])}" y1="{_f(finish[1]-15)}" x2="{_f(finish[0])}" y2="{_f(finish[1]+15)}" stroke="#111" stroke-width="4" stroke-dasharray="4 3"/><text x="{_f(finish[0]-42)}" y="{_f(finish[1]-18)}" font-family="sans-serif" font-size="11">FINISH</text></g>
<g id="trajectory">{"".join(segments)}</g>
<g id="robot-snapshots">{"".join(snapshot_svg)}</g>
<g id="events">{"".join(event_svg)}</g>
<g id="legend" font-family="sans-serif" font-size="11"><rect x="20" y="650" width="960" height="72" rx="6" fill="#fff" stroke="#d7d2c8"/><text x="34" y="671" font-weight="700">Legend</text><line x1="95" y1="667" x2="135" y2="667" stroke="#c4c7ca" stroke-width="10"/><text x="142" y="671">tape {float(track.get("tape_width", .025))*1000:.1f} mm</text><line x1="250" y1="667" x2="278" y2="667" stroke="{colours["green"]}" stroke-width="3"/><text x="284" y="671">≤25%</text><line x1="342" y1="667" x2="370" y2="667" stroke="{colours["amber"]}" stroke-width="3"/><text x="376" y="671">25–75%</text><line x1="449" y1="667" x2="477" y2="667" stroke="{colours["red"]}" stroke-width="3"/><text x="483" y="671">75–100%</text><line x1="570" y1="667" x2="598" y2="667" stroke="{colours["dark-red"]}" stroke-width="3"/><text x="604" y="671">outside envelope</text><rect x="34" y="689" width="24" height="13" fill="#5b67a5" fill-opacity=".25" stroke="#35406f"/><text x="66" y="700">robot snapshots: start, 25%, 50%, 75%, terminal</text><text x="430" y="700">events: ! line loss · E controller · × off-track · T timeout · ✓ finish</text></g>
<g id="trial-metadata" font-family="sans-serif" font-size="10" fill="#555"><text x="24" y="744">{TRACK_VIEW_RENDERER_VERSION} · allowed centre-line error {_f(allowed_m*1000)} mm · exact recorded poses</text></g>
</svg>'''
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


def race_report(run_root: Path, experiment_id: str, results: list[dict[str, Any]], config: dict[str, Any], repo_changes: list[dict[str, str]], previous_race: str | None, artifact_prefix: str = "", filename: str = "race-report.md") -> None:
    """Write a concise, deterministic report for one completed two-team race."""
    by_condition = {
        condition: sorted((result for result in results if result["condition"] == condition), key=lambda result: result["iteration"])
        for condition in config["conditions"]
    }
    rows = []
    final_scores: dict[str, float] = {}
    for condition, condition_results in by_condition.items():
        final = condition_results[-1]
        final_scores[condition] = float(final["score"])
        held_out = final.get("held_out", {})
        held_out_score = held_out.get("score", held_out.get("aggregate", {}).get("score"))
        held_out_text = "—" if held_out_score is None else f"{float(held_out_score):.3f}"
        rows.append(f"| {condition} | {float(condition_results[0]['score']):.3f} | {max(float(result['score']) for result in condition_results):.3f} | {float(final['score']):.3f} | {held_out_text} |\n")
    leader = max(final_scores, key=final_scores.get)
    other = next(condition for condition in final_scores if condition != leader)
    margin = final_scores[leader] - final_scores[other]
    change_heading = f"Repository changes since {previous_race} completed" if previous_race else "Repository changes before this race"
    changes = "".join(f"- [{change['subject']}]({change['url']}) (`{change['short_hash']}`)\n" for change in repo_changes)
    changes = changes or "- No non-race repository commits were found in this interval.\n"
    report = (
        f"# {experiment_id.replace('-', ' ').title()} report\n\n"
        f"{leader} finished ahead of {other} by {margin:.3f} points. This report describes this race only; it does not by itself establish that either orchestration is generally superior.\n\n"
        "## Results\n\n| Team | Initial score | Best score | Final score | Final held-out score |\n|---|---:|---:|---:|---:|\n"
        + "".join(rows)
        + f"\n[Open the full leaderboard]({artifact_prefix}leaderboard.md) · [Open the frozen manifest]({artifact_prefix}manifest.json)\n\n"
        + f"## {change_heading}\n\nThis excludes commits whose changed files are only this race's generated or published artifacts.\n\n"
        + changes
    )
    atomic_write(run_root / filename, report)


def scenario_yaml(base_map: str, condition: str, iteration: int, summary_url: str, leaderboard_url: str, result: dict[str, Any], setup_notes: str = "", track_view_urls: list[tuple[str, str]] | None = None, race_report_url: str | None = None) -> str:
    run_match = re.search(r"(?:^|/)runs/([^/]+)/", summary_url)
    if run_match is None:
        raise ValueError("summary URL must contain a run identifier")
    run_id = run_match.group(1)
    race_match = re.fullmatch(r"race-(\d+)", run_id)
    suffix = race_match.group(1) if race_match else run_id
    scenario_name = f"Race {suffix} iteration {iteration}" if race_match else f"{run_id} iteration {iteration}"
    dimension = f"race: {suffix}" if race_match else f'experiment: "{run_id}"'
    indented_setup = "\n".join(f"    {line}" for line in setup_notes.splitlines())
    if race_report_url:
        indented_setup += f"\n    [Read the race report]({race_report_url})"
    view_lines = "".join(f"\n        - [{_svg_text(label)}]({url})" for label, url in (track_view_urls or []))
    return f'''map:\n  id: iteration-{suffix}.{iteration}\n  inherits: "{base_map}"\n  scenario: "{scenario_name}"\n  dimensions:\n    {dimension}\n    iteration: {iteration}\n  notes: |\n    Race-specific initial conditions:\n{indented_setup}\noverrides:\n  entities:\n    - id: entity2\n      label: 'Score: {result["score"]:.4f}'\n      status: complete\n      notes: |\n        - [Open iteration race summary]({summary_url})\n        - [Open shared leaderboard]({leaderboard_url}){view_lines}\n'''
