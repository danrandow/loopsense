from __future__ import annotations

import argparse
import html
import json
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .io import read_json, safe_child, write_json
from .model_client import validate_openrouter_api_key
from .runner import ExperimentRunner, ROOT, validate_config

RUNS = ROOT / "runs"
DEFINITIONS = ROOT / "race-definitions"


def next_race_id() -> str:
    numbers = []
    for root in (RUNS, DEFINITIONS):
        for path in root.glob("race-*") if root.exists() else []:
            match = re.fullmatch(r"race-(\d+)", path.name)
            if match:
                numbers.append(int(match.group(1)))
    return f"race-{max(numbers, default=-1) + 1}"


def layout(body: str, title: str = "LoopSense Robot Race") -> bytes:
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title><style>
body{{font:16px/1.45 system-ui,sans-serif;max-width:1040px;margin:32px auto;padding:0 18px;color:#19212b;background:#f5f3ed}}h1,h2{{line-height:1.15}}.panel{{background:white;border:1px solid #d8d4ca;border-radius:12px;padding:22px;margin:18px 0}}label{{display:block;font-weight:650;margin-top:14px}}input,select,textarea{{box-sizing:border-box;width:100%;padding:9px;border:1px solid #aaa;border-radius:6px;font:inherit}}textarea{{min-height:110px}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 18px}}button{{margin-top:20px;padding:11px 18px;background:#245b91;color:white;border:0;border-radius:7px;font-weight:700;cursor:pointer}}table{{border-collapse:collapse;width:100%}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}small,.muted{{color:#606975}}code{{background:#eee;padding:2px 5px;border-radius:4px}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>{body}</body></html>'''.encode()


def races_table() -> str:
    rows = []
    for path in sorted(RUNS.glob("race-*")) if RUNS.exists() else []:
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = read_json(manifest_path)
        status = manifest.get("status", "unknown")
        if status == "failed":
            status += f' — {manifest.get("failed_actor", "run")} at iteration {manifest.get("failed_iteration", "?")}'
        evidence = [f'<a href="/runs/{path.name}/manifest.json">manifest</a>']
        if (path / "race-report.md").exists():
            evidence.insert(0, f'<a href="/runs/{path.name}/race-report.md">race report</a>')
        if (path / "leaderboard.svg").exists():
            evidence.insert(0, f'<a href="/runs/{path.name}/leaderboard.svg">leaderboard</a>')
        if (path / "leaderboard.md").exists():
            evidence.insert(1, f'<a href="/runs/{path.name}/leaderboard.md">table</a>')
        rows.append(f'<tr><td>{html.escape(path.name)}</td><td>{html.escape(status)}</td><td>{" · ".join(evidence)}</td></tr>')
    return '<p class="muted">No recorded races yet.</p>' if not rows else '<table><tr><th>Race</th><th>Status</th><th>Evidence</th></tr>' + "".join(rows) + '</table>'


def setup_page(message: str = "") -> bytes:
    config = read_json(ROOT / "config/experiment.yaml")
    initial = config["initial_conditions"]
    alert = f'<div class="panel"><strong>{html.escape(message)}</strong></div>' if message else ""
    body = f'''<h1>LoopSense Robot Race</h1><p>Configure and start a fresh race. Each race creates its own pair of maps and numbered iteration scenarios.</p>{alert}
<section class="panel"><h2>Previous races</h2>{races_table()}</section>
<form class="panel" method="post" action="/start"><h2>Start a new race</h2><div class="grid">
<div><label>Race ID</label><input name="race_id" value="{next_race_id()}" pattern="race-[0-9]+" required><small>Use race-0, race-1, and so on.</small></div>
<div><label>Iterations per team</label><input name="iterations" type="number" min="1" max="50" value="5" required></div>
<div><label>Model provider</label><select name="provider"><option value="openrouter">OpenRouter</option><option value="mock">Offline deterministic mock</option></select></div>
<div><label>OpenRouter model slug</label><input name="model" value="openai/gpt-4.1-mini" required><small>Choose a current slug from <a href="https://openrouter.ai/models">OpenRouter models</a>. Both teams use this exact model.</small></div>
<div><label>OpenRouter API key</label><input name="api_key" type="password" autocomplete="off"><small>Used in memory for this server process; never written to disk.</small></div>
<div><label>Total token budget per team</label><input name="total_budget" type="number" min="1000" value="40000" required></div>
<div><label>Token budget per iteration</label><input name="iteration_budget" type="number" min="500" value="10000" required></div>
<div><label>Maximum output tokens per call</label><input name="max_output_tokens" type="number" min="200" value="2000" required></div></div>
<label>LoopSense starter working agreement</label><textarea name="loopsense_agreement" required>{html.escape(initial["loopsense_working_agreement"])}</textarea>
<label>Optimizer/evaluator initial criteria</label><textarea name="control_criteria" required>{html.escape(initial["control_criteria"])}</textarea>
<button type="submit">Start race</button><p class="muted">The page waits while the race runs. Closing the browser does not expose your API key, but stopping this server stops the active process.</p></form>'''
    return layout(body)


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, content_type: str = "text/html; charset=utf-8", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_bytes(setup_page())
            return
        if parsed.path.startswith("/runs/"):
            try:
                path = safe_child(RUNS, *[part for part in parsed.path.removeprefix("/runs/").split("/") if part])
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST)
                return
            if not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            types = {".svg": "image/svg+xml", ".json": "application/json", ".md": "text/markdown; charset=utf-8", ".yaml": "text/yaml; charset=utf-8"}
            self.send_bytes(path.read_bytes(), types.get(path.suffix, "application/octet-stream"))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/start":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            form = {key: values[0] for key, values in parse_qs(self.rfile.read(length).decode()).items()}
            race_id = form["race_id"]
            if not re.fullmatch(r"race-\d+", race_id):
                raise ValueError("Race ID must look like race-0")
            if (RUNS / race_id).exists() or (DEFINITIONS / race_id).exists():
                raise ValueError(f"{race_id} already exists; choose a fresh race number")
            config = read_json(ROOT / "config/experiment.yaml")
            config.update({"experiment_id": race_id, "mode": "pilot", "iterations": int(form["iterations"])})
            config["model"].update({"provider": form["provider"], "id": form["model"], "max_output_tokens": int(form["max_output_tokens"])})
            config["budget"].update({"total_tokens_per_condition": int(form["total_budget"]), "max_tokens_per_iteration": int(form["iteration_budget"])})
            config["initial_conditions"] = {"loopsense_working_agreement": form["loopsense_agreement"], "control_criteria": form["control_criteria"]}
            validate_config(config)
            if form["provider"] == "openrouter":
                key = (form.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")).strip()
                if not key:
                    raise ValueError("Enter an OpenRouter API key or start the server with OPENROUTER_API_KEY set")
                validate_openrouter_api_key(key, config["model"]["base_url"], config["model"]["timeout_seconds"])
                os.environ["OPENROUTER_API_KEY"] = key
            definition = DEFINITIONS / race_id
            definition.mkdir(parents=True)
            config_path = definition / "config.json"
            write_json(config_path, config)
            run_root = ExperimentRunner(config_path, RUNS).run()
            body = layout(f'<h1>{html.escape(race_id)} complete</h1><div class="panel"><p>Both teams completed {config["iterations"]} iterations.</p><p><a href="/runs/{race_id}/race-report.md">Open race report</a> · <a href="/runs/{race_id}/leaderboard.svg">Open leaderboard</a> · <a href="/runs/{race_id}/manifest.json">Open manifest</a> · <a href="/">Set up another race</a></p><p>Artifacts: <code>{html.escape(str(run_root))}</code></p></div>')
            self.send_bytes(body)
        except Exception as error:
            self.send_bytes(setup_page(str(error)), status=HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: object) -> None:
        print(f"robotrace-ui: {format % args}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local Robot Race setup and leaderboard interface")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("For API-key safety this interface binds only to the local computer")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Robot Race interface: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
