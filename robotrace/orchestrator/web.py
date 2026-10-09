from __future__ import annotations

import argparse
import difflib
import html
import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import yaml

from .field_docs import FIELD_DOCS, docs_page_body, help_html
from .io import read_json, safe_child
from .map_package import PackageValidationError
from .race_service import MapDrivenRaceService, RaceStateError, ROOT, TEMPLATES


ENTRANTS = ("randow-maps", "opt-eval")
_ACTIVE_RUNS: set[str] = set()


def next_race_id() -> str:
    numbers = []
    for path in ROOT.glob("race-*-pair.json"):
        suffix = path.name.removeprefix("race-").removesuffix("-pair.json")
        if suffix.isdigit():
            numbers.append(int(suffix))
    candidate = max(numbers, default=7) + 1
    while candidate in {5, 6, 7} or (ROOT / f"race-{candidate}-pair.json").exists():
        candidate += 1
    return f"race-{candidate}"


def layout(body: str, title: str = "Map-driven Robot Race") -> bytes:
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title><style>
body{{font:16px/1.45 system-ui;max-width:1100px;margin:30px auto;padding:0 18px;color:#19212b;background:#f5f3ed}}section{{background:white;border:1px solid #d8d4ca;padding:20px;margin:16px 0;border-radius:10px}}label{{display:block;font-weight:650;margin-top:12px}}input,select,textarea{{width:100%;box-sizing:border-box;padding:8px;font:inherit}}textarea{{min-height:55vh}}button,.button{{display:inline-block;padding:10px 14px;margin:10px 4px 0 0;border:0;border-radius:6px;background:#245b91;color:white;text-decoration:none;font-weight:700}}button[disabled]{{background:#9aa2aa}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 18px}}.muted{{color:#606975}}.ok{{color:#176b3a}}.warn{{color:#8a4b08}}pre{{white-space:pre-wrap;background:#f3f3f3;padding:12px;overflow:auto}}@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}button[disabled]{{cursor:wait}}.help{{display:inline-block;margin-left:6px;vertical-align:top}}.help summary{{cursor:pointer;display:inline-block;width:1.4em;height:1.4em;line-height:1.4em;text-align:center;border-radius:50%;background:#dfe7ef;color:#245b91;font-weight:700;font-size:.85em;list-style:none}}.help[open]{{display:block;margin:6px 0}}.help>div{{background:#eef3f8;border-left:3px solid #245b91;padding:6px 12px;font-weight:400;font-size:.92em}}.help p{{margin:4px 0}}code{{background:#eee;padding:1px 4px;border-radius:3px;font-size:.85em}}.busy{{background:#fff4d6;border:1px solid #e0c36a;padding:10px 14px;border-radius:8px;margin:10px 0;font-weight:700;position:sticky;top:0}}</style></head><body>{body}<script>document.addEventListener("submit",function(e){{var f=e.target,b=e.submitter;if(f.dataset.busy){{e.preventDefault();return}}f.dataset.busy="1";
if(b&&b.name){{var h=document.createElement("input");h.type="hidden";h.name=b.name;h.value=b.value;f.appendChild(h)}}
var labels={{run:"Running… do not close this page",freeze:"Validating…",prepare:"Preparing…",retire:"Retiring…"}};
var t=b&&labels[b.value]||"Working…";if(b)b.textContent=t;
var n=document.createElement("div");n.className="busy";n.textContent=t;f.insertBefore(n,f.firstChild);
setTimeout(function(){{f.querySelectorAll("button").forEach(function(x){{x.disabled=true}})}},0)}});
window.addEventListener("pageshow",function(e){{if(e.persisted)location.reload()}});</script></body></html>'''.encode()


def _settings(service: MapDrivenRaceService) -> dict[str, object]:
    source = service.packages[0] / "config/race.yaml"
    if not source.exists():
        source = TEMPLATES / "randow-maps/config/race.yaml"
    race = yaml.safe_load(source.read_text(encoding="utf-8"))
    return {
        "iterations": race["iterations"], "provider": race["model"]["provider"],
        "model_id": race["model"]["id"], "max_output_tokens": race["model"]["max_output_tokens"],
        "max_action_runs": race["budget"]["max_action_runs"],
        "total_tokens_per_condition": race["budget"]["total_tokens_per_condition"],
        "max_tokens_per_iteration": race["budget"]["max_tokens_per_iteration"],
    }


def _definition_table(service: MapDrivenRaceService, entrant: str, editable: bool) -> str:
    package = next(path for path in service.packages if path.name.endswith("-" + entrant))
    provenance = read_json(package / "provenance.json")
    template = TEMPLATES / entrant
    rows = []
    for relative in service.editable_definitions(entrant):
        current = (package / relative).read_text(encoding="utf-8")
        baseline_path = template / relative
        baseline = baseline_path.read_text(encoding="utf-8") if baseline_path.exists() else ""
        status = "Changed" if current != baseline else "Unchanged"
        action = f'<a href="/edit?race_id={quote(service.race_id)}&entrant={quote(entrant)}&path={quote(relative)}">Edit</a>' if editable else "Locked"
        rows.append(f"<tr><td>{html.escape(relative)}</td><td>{status}</td><td>{action}</td></tr>")
    return f'''<h3>{html.escape(entrant)}</h3><p class="muted">Cloned from {html.escape(provenance["source"])}</p>
<table><tr><th>Definition</th><th>Difference from template</th><th>Action</th></tr>{''.join(rows)}</table>'''


MODEL_HISTORY = ROOT / ".robotrace-model-history.json"


def _model_history() -> list[tuple[str, str]]:
    """Previously used (provider, model_id) pairs, most recent first: saved history, then existing races."""
    seen: list[tuple[str, str]] = []
    def add(provider: object, model_id: object) -> None:
        if provider and model_id and (str(provider), str(model_id)) not in seen: seen.append((str(provider), str(model_id)))
    try:
        for provider, model_id in read_json(MODEL_HISTORY): add(provider, model_id)
    except Exception: pass
    for pair in sorted(ROOT.glob("*-pair.json"), reverse=True):
        try:
            for package in read_json(pair).get("packages", []):
                race = yaml.safe_load((ROOT / Path(package).name / "config/race.yaml").read_text(encoding="utf-8"))
                add(race["model"]["provider"], race["model"]["id"])
        except Exception: continue
    return seen


def _remember_model(provider: str, model_id: str) -> None:
    pairs = [(provider.strip(), model_id.strip())] + [p for p in _model_history() if p != (provider.strip(), model_id.strip())]
    MODEL_HISTORY.write_text(json.dumps(pairs[:30]), encoding="utf-8")


def _model_picker() -> str:
    options = "".join(f'<option value="{html.escape(m)}" data-provider="{html.escape(p)}">{html.escape(m)} ({html.escape(p)})</option>' for p, m in _model_history())
    if not options: return ""
    return ('<select aria-label="Previous models" onchange="if(this.value){var f=this.form;f.model_id.value=this.value;'
            'f.provider.value=this.selectedOptions[0].dataset.provider;this.selectedIndex=0}">'
            f'<option value="">Previously used…</option>{options}</select>')


def _race_list(current: str) -> str:
    rows = []
    for path in sorted(ROOT.glob("*-pair.json"), key=lambda p: (len(p.name), p.name), reverse=True):
        race_id = path.name.removesuffix("-pair.json")
        links = ""
        try:
            state = read_json(path); status = state.get("status", "unknown")
            if status == "complete" and state.get("report") and state.get("leaderboard"):
                links = f'<a href="/{quote(Path(state["report"]).name)}">Report</a> · <a href="/{quote(Path(state["leaderboard"]).name)}">Leaderboard</a>'
        except Exception: status = "unreadable"
        css = "ok" if status == "complete" else "warn" if status in {"failed", "running"} else "muted"
        name = f"<strong>{html.escape(race_id)}</strong>" if race_id == current else html.escape(race_id)
        rows.append(f'<tr><td><a href="/?race_id={quote(race_id)}">{name}</a></td><td class="{css}">{html.escape(str(status))}</td><td>{links}</td></tr>')
    return f'<details><summary><strong>Races</strong> <span class="muted">({len(rows)}; click to expand)</span></summary><table><tr><th>Race</th><th>Status</th><th>Evidence</th></tr>{"".join(rows)}</table></details>' if rows else ""


def page(race_id: str | None = None, message: str = "") -> bytes:
    race_id = race_id or next_race_id()
    service = MapDrivenRaceService(race_id)
    state = read_json(service.pair_path) if service.pair_path.exists() else {"status": "new", "reviewed": {}}
    status = state.get("status", "new")
    editable = status in {"new", "prepared"}
    field_lock = "" if editable else " disabled"
    settings = _settings(service)
    alert = f"<section><strong>{html.escape(message)}</strong></section>" if message else ""
    provider_options = "".join(f'<option value="{value}"{" selected" if settings["provider"] == value else ""}>{label}</option>' for value, label in (("mock", "Offline deterministic mock"), ("openrouter", "OpenRouter")))
    definitions = "" if status == "new" else "".join(_definition_table(service, entrant, editable) for entrant in ENTRANTS)
    reviews = state.get("reviewed", {})
    review_buttons = "".join(f'<button name="action" value="review-{entrant}"{" disabled" if not editable else ""}>Acknowledge {entrant} review</button> <span class="{"ok" if reviews.get(entrant) else "warn"}">{"Reviewed" if reviews.get(entrant) else "Not reviewed"}</span><br>' for entrant in ENTRANTS)
    evidence = ""
    error_banner = ""
    if status == "failed":
        failure = state.get("error", {})
        error_banner = f'<section><strong class="warn">Run failed: {html.escape(str(failure.get("message", "unknown error")))}</strong><p>This race cannot be resumed or edited. Retire it and prepare a fresh race id.</p></section>'
    run_warnings = "".join(f'<p class="warn">Warning: {html.escape(w)}</p>' for w in service.run_warnings()) if status in {"frozen", "running"} else ""
    if status == "complete":
        report = Path(state["report"]).name
        leaderboard = Path(state["leaderboard"]).name
        evidence = f'<section><h2>Evidence</h2><p><a href="/{html.escape(report)}">Race report</a> · <a href="/{html.escape(leaderboard)}">Leaderboard</a></p></section>'
    return layout(f'''<h1>Map-driven Robot Race</h1>{alert}{error_banner}<p>Status: <strong>{html.escape(status)}</strong> <a class="button" href="/">New race</a> <a href="/docs">Settings reference</a></p>{_race_list(service.race_id)}
<form method="post">{'' if status == 'new' else f'<input type="hidden" name="race_id" value="{html.escape(service.race_id)}">'}
<section><h2>1. Prepare</h2><div class="grid">
<div><label>{FIELD_DOCS['race_id']['label']}{help_html('race_id')}</label><input{' name="race_id"' if status == 'new' else ''} value="{html.escape(service.race_id)}"{' disabled' if status != 'new' else ''}></div>
<div><label>Entrant templates</label><input value="Randow Maps + Opt/Eval" disabled></div>
<div><label>{FIELD_DOCS['iterations']['label']}{help_html('iterations')}</label><input name="iterations" type="number" min="1" value="{settings['iterations']}" required{field_lock}></div>
<div><label>{FIELD_DOCS['provider']['label']}{help_html('provider')}</label><select name="provider"{field_lock}>{provider_options}</select></div>
<div><label>{FIELD_DOCS['model_id']['label']}{help_html('model_id')}</label>{'' if not editable else _model_picker()}<input name="model_id" value="{html.escape(str(settings['model_id']))}" required{field_lock}></div>
<div><label>{FIELD_DOCS['api_key']['label']}{help_html('api_key')}</label><input name="api_key" type="password" autocomplete="off"><span class="muted">Memory only; never written to a package.</span></div>
<div><label>{FIELD_DOCS['total_tokens_per_condition']['label']}{help_html('total_tokens_per_condition')}</label><input name="total_tokens_per_condition" type="number" min="1" value="{settings['total_tokens_per_condition']}" required{field_lock}></div>
<div><label>{FIELD_DOCS['max_tokens_per_iteration']['label']}{help_html('max_tokens_per_iteration')}</label><input name="max_tokens_per_iteration" type="number" min="1" value="{settings['max_tokens_per_iteration']}" required{field_lock}></div>
<div><label>{FIELD_DOCS['max_action_runs']['label']}{help_html('max_action_runs')}</label><input name="max_action_runs" type="number" min="1" value="{settings['max_action_runs']}" required{field_lock}></div>
<div><label>{FIELD_DOCS['max_output_tokens']['label']}{help_html('max_output_tokens')}</label><input name="max_output_tokens" type="number" min="1" value="{settings['max_output_tokens']}" required{field_lock}></div></div>
<button name="action" value="{'prepare' if status == 'new' else 'save-settings'}"{' disabled' if not editable else ''}>{'Prepare packages' if status == 'new' else 'Save race settings'}</button></section>
<section><h2>2. Review</h2><p>Inspect the authoritative definition inventory and changed-file status. Open an editor only when a definition needs changing; file previews are not shown here.</p>{f'<details><summary><strong>Definition inventory</strong> <span class="muted">(click to expand)</span></summary>{definitions}</details>' if definitions else '<p class="muted">Prepare packages first.</p>'}{review_buttons if status != 'new' else ''}</section>
<section><h2>3. Validate and freeze</h2><p>Validation runs without model or simulator work. Freezing locks this revision.</p><button name="action" value="freeze"{' disabled' if status != 'prepared' or set(reviews) != set(ENTRANTS) else ''}>Validate and freeze</button></section>
<section><h2>4. Run frozen race</h2><p>Execution performs a fresh preflight check and uses only the map-driven service.</p>{run_warnings}<button name="action" value="run"{' disabled' if status not in {'frozen', 'running'} else ''}>{'Resume frozen race' if status == 'running' else 'Run frozen race'}</button> <button name="action" value="retire"{' disabled' if status not in {'failed', 'running'} else ''}>Retire race</button></section></form>{evidence}''')


def edit_page(service: MapDrivenRaceService, entrant: str, relative: str, message: str = "") -> bytes:
    if relative not in service.editable_definitions(entrant):
        raise ValueError("file is not an editable package definition")
    package = next(path for path in service.packages if path.name.endswith("-" + entrant))
    content = (package / relative).read_text(encoding="utf-8")
    template_path = TEMPLATES / entrant / relative
    baseline = template_path.read_text(encoding="utf-8") if template_path.exists() else ""
    diff = "".join(difflib.unified_diff(baseline.splitlines(True), content.splitlines(True), fromfile="template", tofile="draft")) or "No changes from template.\n"
    alert = f"<p><strong>{html.escape(message)}</strong></p>" if message else ""
    return layout(f'''<h1>Edit {html.escape(entrant)} definition</h1>{alert}<p><a href="/?race_id={quote(service.race_id)}">Back to lifecycle</a></p>
<section><h2>{html.escape(relative)}</h2><form method="post"><input type="hidden" name="race_id" value="{html.escape(service.race_id)}"><input type="hidden" name="entrant" value="{html.escape(entrant)}"><input type="hidden" name="relative_path" value="{html.escape(relative)}"><textarea name="content">{html.escape(content)}</textarea><button name="action" value="save-definition">Save definition</button></form></section>
<section><h2>Readable diff from template</h2><pre>{html.escape(diff)}</pre></section>''', f"Edit {relative}")


def _form_settings(form: dict[str, str]) -> dict[str, object]:
    return {key: form[key] for key in ("iterations", "provider", "model_id", "max_output_tokens", "max_action_runs", "total_tokens_per_condition", "max_tokens_per_iteration")}


def error_status(error: Exception) -> HTTPStatus:
    """Bad input is 400, a state or configuration conflict is 409, anything that fails mid-run is 500."""
    if isinstance(error, RaceStateError):
        return HTTPStatus.CONFLICT
    if isinstance(error, (ValueError, KeyError, FileExistsError, PackageValidationError)):
        return HTTPStatus.BAD_REQUEST
    return HTTPStatus.INTERNAL_SERVER_ERROR


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body: bytes, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path); query = parse_qs(parsed.query)
        if parsed.path == "/":
            self.send_bytes(page(query.get("race_id", [None])[0])); return
        if parsed.path == "/docs":
            self.send_bytes(layout(docs_page_body(), "Race settings reference")); return
        if parsed.path == "/edit":
            try:
                service = MapDrivenRaceService(query["race_id"][0]); self.send_bytes(edit_page(service, query["entrant"][0], query["path"][0]))
            except Exception as error: self.send_bytes(layout(f"<h1>Cannot edit</h1><p>{html.escape(str(error))}</p>"), status=HTTPStatus.BAD_REQUEST)
            return
        try: path = safe_child(ROOT, *[part for part in parsed.path.lstrip("/").split("/") if part])
        except ValueError: self.send_error(HTTPStatus.BAD_REQUEST); return
        if not path.is_file(): self.send_error(HTTPStatus.NOT_FOUND); return
        self.send_bytes(path.read_bytes(), content_type="text/plain; charset=utf-8")

    def do_POST(self) -> None:
        form: dict[str, str] = {}
        try:
            form = {key: values[0] for key, values in parse_qs(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode()).items()}
            service = MapDrivenRaceService(form["race_id"]); action = form["action"]
            if action == "prepare": service.prepare(); service.configure_common(_form_settings(form)); _remember_model(form["provider"], form["model_id"])
            elif action == "save-settings": service.configure_common(_form_settings(form)); _remember_model(form["provider"], form["model_id"])
            elif action == "save-definition":
                service.update_definition(form["entrant"], form["relative_path"], form["content"])
                self.send_bytes(edit_page(service, form["entrant"], form["relative_path"], "Definition saved; review acknowledgement cleared.")); return
            elif action.startswith("review-"): service.review(action.removeprefix("review-"))
            elif action == "freeze": service.freeze()
            elif action == "retire": service.retire()
            elif action == "run":
                if form.get("api_key", "").strip(): os.environ["OPENROUTER_API_KEY"] = form["api_key"].strip()
                if service.race_id in _ACTIVE_RUNS: raise RaceStateError("this race is already running")
                _ACTIVE_RUNS.add(service.race_id)
                try: service.run()
                finally: _ACTIVE_RUNS.discard(service.race_id)
            else: raise ValueError("unknown lifecycle action")
            if form.get("api_key", "").strip(): os.environ["OPENROUTER_API_KEY"] = form["api_key"].strip()
            self.send_bytes(page(service.race_id, f"{action} complete"))
        except Exception as error:
            self.send_bytes(page(form.get("race_id"), str(error)), status=error_status(error))

    def log_message(self, format: str, *args: object) -> None: print("robotrace-ui: " + format % args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765); args = parser.parse_args(argv)
    if args.host not in {"127.0.0.1", "localhost", "::1"}: raise SystemExit("local binding required")
    server = ThreadingHTTPServer((args.host, args.port), Handler); print(f"Robot Race interface: http://{args.host}:{args.port}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0


if __name__ == "__main__": raise SystemExit(main())
