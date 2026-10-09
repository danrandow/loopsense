"""Read-only live progress for a Robot Race, derived entirely from files the orchestrator already writes.

Nothing here talks to the controller or mutates a package, so it is safe to point at a race that is running,
frozen, failed or complete. Sources, per entrant package:

  race-N-pair.json                       race status (prepared / frozen / running / failed / complete)
  config/race.yaml                       iterations, model, token and action-run budgets
  iteration-K/events.jsonl               one line per completed action: tokens, timestamps
  iteration-K/budget-ledger.json         running token and action-run totals (the enforced budget)
  iteration-K/rejected-attempts/         model outputs the harness rejected, with the reason
  iteration-K/summary.json, outcome.json development-track scores; whether the iteration finished
  final-evaluation.json                  the held-out race, once every iteration is done

Standalone:  python3 -m orchestrator.progress [race-N] [--port 8766]
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[2]
QUIET_AFTER_S = 180  # a model call plus repairs normally lands well inside this
RECENT_EVENTS = 8
RECENT_PROBLEMS = 4


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _events(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue  # a half-written final line while the controller is committing
    except OSError:
        pass
    return out


def _ts(value: Any) -> float | None:
    try:
        return datetime.fromisoformat(str(value)).timestamp()
    except (TypeError, ValueError):
        return None


def _mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _iteration_dirs(package: Path) -> list[tuple[int, Path]]:
    found = []
    for path in package.glob("iteration-*"):
        match = re.fullmatch(r"iteration-(\d+)", path.name)
        if match and path.is_dir():
            found.append((int(match.group(1)), path))
    return sorted(found)


def _iteration(index: int, path: Path) -> dict[str, Any]:
    events = _events(path / "events.jsonl")
    ledger = _json(path / "budget-ledger.json") or {}
    outcome = _json(path / "outcome.json")
    summary = _json(path / "summary.json")
    rejected = sorted((path / "rejected-attempts").glob("*.json"), key=lambda p: _mtime(p) or 0) if (path / "rejected-attempts").is_dir() else []
    stamps = [t for t in (_ts(e.get("timestamp")) for e in events) if t is not None]
    state = "running"
    reason = None
    if outcome is not None:
        if outcome.get("complete"):
            state = "raced"
        else:
            state = "not_raced"
            reason = outcome.get("reason")
    trials = [{"track": t.get("track"), "score": t.get("score"), "termination": t.get("termination_reason"), "error": t.get("error")} for t in (summary or {}).get("trials", [])]
    scores = [t["score"] for t in trials if isinstance(t["score"], (int, float))]
    return {
        "index": index, "state": state, "reason": reason, "undelivered": (outcome or {}).get("undelivered", []),
        "action_runs": ledger.get("action_runs", len(events)), "iteration_tokens": ledger.get("iteration_tokens"),
        "total_tokens": ledger.get("total_tokens"), "rejected": len(rejected),
        "first_event": min(stamps) if stamps else None, "last_event": max(stamps) if stamps else None,
        "trials": trials, "score": round(sum(scores) / len(scores), 4) if scores else None,
        "_events": events, "_rejected": rejected,
    }


def _entrant(package: Path, now: float, race_status: str) -> dict[str, Any]:
    race = yaml.safe_load((package / "config/race.yaml").read_text(encoding="utf-8")) if (package / "config/race.yaml").exists() else {}
    total_iterations = int(race.get("iterations") or 0)
    budget = race.get("budget", {})
    iterations = [_iteration(i, p) for i, p in _iteration_dirs(package)]
    final = _json(package / "final-evaluation.json")

    # Durations: end-to-end between consecutive iteration completions, which includes model latency between
    # actions. Iteration 0 has no earlier anchor, so only its own span is known.
    previous_end: float | None = None
    durations: list[float] = []
    for it in iterations:
        if it["state"] == "running" or it["last_event"] is None:
            it["duration_s"] = None
            continue
        start = previous_end if previous_end is not None else it["first_event"]
        it["duration_s"] = round(it["last_event"] - start, 1) if start is not None else None
        if it["duration_s"] is not None and (previous_end is not None or len(iterations) == 1):
            durations.append(it["duration_s"])
        previous_end = it["last_event"]
    if not durations:
        durations = [it["duration_s"] for it in iterations if it.get("duration_s")]
    recent = durations[-3:]  # later iterations carry more history, so recent ones predict better than the mean
    avg = round(sum(recent) / len(recent), 1) if recent else None

    current = next((it for it in iterations if it["state"] == "running"), None)
    finished = [it for it in iterations if it["state"] != "running"]
    done_iterations = len(finished)
    all_events = sorted((e for it in iterations for e in it["_events"] if _ts(e.get("timestamp"))), key=lambda e: _ts(e["timestamp"]))
    last_stamp = _ts(all_events[-1]["timestamp"]) if all_events else None
    for it in iterations:  # a rejected attempt is activity too: the model is being asked to repair
        for r in it["_rejected"]:
            m = _mtime(r)
            if m and (last_stamp is None or m > last_stamp):
                last_stamp = m
    first_stamp = _ts(all_events[0]["timestamp"]) if all_events else None

    if final is not None:
        phase = "complete"
    elif total_iterations and done_iterations >= total_iterations:
        phase = "final"
    elif iterations:
        phase = "iterating"
    else:
        phase = "queued"

    bests = [it["score"] for it in finished if it["score"] is not None]
    latest_ledger = next((it for it in reversed(iterations) if it["total_tokens"] is not None), None)
    recent_events = [{"action": e.get("action"), "at": _ts(e["timestamp"]), "input_tokens": e.get("input_tokens"), "output_tokens": e.get("output_tokens"),
                      "simulator": e.get("component") is not None, "repairs": None, "iteration": it["index"]}
                     for it in iterations for e in it["_events"] if _ts(e.get("timestamp"))]
    recent_events.sort(key=lambda e: e["at"])
    problems = []
    for it in iterations:
        for r in it["_rejected"]:
            data = _json(r) or {}
            problems.append({"iteration": it["index"], "action": data.get("action"), "attempt": data.get("attempt"), "error": str(data.get("error", ""))[:240], "at": _mtime(r)})
    problems.sort(key=lambda p: p["at"] or 0)

    remaining_iterations = max(total_iterations - done_iterations, 0)
    eta = None
    if phase == "iterating" and avg is not None:
        into_current = (now - previous_end) if (previous_end is not None and current is not None) else 0
        eta = max(avg * remaining_iterations - min(into_current, avg), 0)

    public = []
    for it in iterations:
        public.append({k: v for k, v in it.items() if not k.startswith("_")})
    return {
        "entrant": race.get("entrant") or package.name, "package": package.name, "phase": phase,
        "iterations_total": total_iterations, "iterations_done": done_iterations, "iterations": public,
        "current_iteration": current["index"] if current else None,
        "model": f'{(race.get("model") or {}).get("provider", "?")} / {(race.get("model") or {}).get("id", "?")}',
        "budget": {"total_used": latest_ledger["total_tokens"] if latest_ledger else 0, "total_max": budget.get("total_tokens_per_condition"),
                   "iteration_used": current["iteration_tokens"] if current else None, "iteration_max": budget.get("max_tokens_per_iteration"),
                   "runs_used": current["action_runs"] if current else None, "runs_max": budget.get("max_action_runs")},
        "scores": {"latest": bests[-1] if bests else None, "best": max(bests) if bests else None},
        "final": None if final is None else {"incomplete": bool(final.get("incomplete")), "reason": final.get("reason"),
                                            "trials": [{"track": t.get("track"), "score": t.get("score"), "termination": t.get("termination_reason")} for t in final.get("trials", [])]},
        "first_activity": first_stamp, "last_activity": last_stamp,
        "quiet_for_s": round(now - last_stamp, 1) if last_stamp is not None else None,
        "avg_iteration_s": avg, "eta_s": round(eta, 1) if eta is not None else None,
        "recent_events": recent_events[-RECENT_EVENTS:], "problems": problems[-RECENT_PROBLEMS:], "problem_count": len(problems),
        "total_calls": len(recent_events),
    }


def snapshot(race_id: str, root: Path = ROOT, now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    if not re.fullmatch(r"[A-Za-z0-9._-]+", race_id):
        raise ValueError("invalid race id")
    pair = _json(root / f"{race_id}-pair.json")
    if pair is None:
        raise FileNotFoundError(f"no race {race_id} in {root}")
    status = pair.get("status", "unknown")
    entrants = [_entrant(root / Path(p).name, now, status) for p in pair.get("packages", []) if (root / Path(p).name).is_dir()]
    # Entrants run one after another, so the race is the sum of their units: every iteration plus one held-out race.
    total_units = sum(e["iterations_total"] + 1 for e in entrants)
    done_units = sum(e["iterations_done"] + (1 if e["phase"] == "complete" else 0) for e in entrants)
    active = next((e for e in entrants if e["phase"] in {"iterating", "final"}), None)
    eta = None
    if active is not None and active["avg_iteration_s"] is not None and status == "running":
        queued = sum(e["iterations_total"] for e in entrants if e["phase"] == "queued")
        eta = (active["eta_s"] or 0) + queued * active["avg_iteration_s"]  # queued entrant assumed no slower than the active one
    last = max((e["last_activity"] for e in entrants if e["last_activity"]), default=None)
    quiet = round(now - last, 1) if last else None
    health = "idle"
    if status == "running":
        health = "stalled" if quiet is not None and quiet > QUIET_AFTER_S else "active"
    elif status in {"failed", "complete", "frozen", "prepared", "retired"}:
        health = status
    return {
        "race_id": race_id, "status": status, "health": health, "error": pair.get("error"), "generated_at": now,
        "units_done": done_units, "units_total": total_units, "fraction": round(done_units / total_units, 4) if total_units else 0.0,
        "eta_s": round(eta, 1) if eta is not None else None, "quiet_for_s": quiet, "quiet_threshold_s": QUIET_AFTER_S,
        "entrants": entrants, "running_races": running_races(root),
    }


def running_races(root: Path = ROOT) -> list[str]:
    out = []
    for path in root.glob("race-*-pair.json"):
        data = _json(path)
        if data and data.get("status") == "running":
            out.append(path.name.removesuffix("-pair.json"))
    return sorted(out, key=lambda r: int(r.split("-")[1]) if r.split("-")[1].isdigit() else 0)


def latest_race(root: Path = ROOT) -> str | None:
    running = running_races(root)
    if running:
        return running[-1]
    numbers = [(int(m.group(1)), p.name.removesuffix("-pair.json")) for p in root.glob("race-*-pair.json") if (m := re.fullmatch(r"race-(\d+)-pair\.json", p.name))]
    return max(numbers)[1] if numbers else None


PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Race progress</title><style>
:root{--bg:#f5f3ed;--card:#fff;--ink:#19212b;--mute:#606975;--line:#d8d4ca;--blue:#245b91;--ok:#176b3a;--warn:#8a4b08;--bad:#a12a2a;--track:#e6e2d8}
@media(prefers-color-scheme:dark){:root{--bg:#14181d;--card:#1c2229;--ink:#e8ebef;--mute:#9aa4b0;--line:#2f3841;--blue:#6aa7e0;--ok:#5fc08a;--warn:#e0a35c;--bad:#e27a7a;--track:#2a323b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}main{max-width:1100px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0}.mute{color:var(--mute)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:14px 0}
.top{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between}.pill{display:inline-block;padding:2px 10px;border-radius:99px;font-weight:700;font-size:13px;border:1px solid currentColor}
.active{color:var(--ok)}.stalled,.failed{color:var(--bad)}.complete{color:var(--blue)}.frozen,.prepared,.idle,.retired{color:var(--mute)}
.bar{height:12px;background:var(--track);border-radius:6px;overflow:hidden}.bar>i{display:block;height:100%;background:var(--blue);transition:width .6s}.bar.warn>i{background:var(--warn)}.bar.bad>i{background:var(--bad)}
.segs{display:flex;gap:4px;margin:10px 0 4px}.seg{flex:1;min-width:0;border-radius:5px;height:34px;background:var(--track);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--mute);position:relative;overflow:hidden}
.seg.raced{background:var(--blue);color:#fff}.seg.not_raced{background:var(--warn);color:#fff}.seg.running{border:2px solid var(--blue);color:var(--blue);background:repeating-linear-gradient(135deg,transparent 0 6px,rgba(36,91,145,.14) 6px 12px);animation:p 1.2s linear infinite;background-size:17px 17px}
@keyframes p{to{background-position:17px 0}}.seg.final{flex:1.2}.seg.final.done{background:var(--ok);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px 22px;margin-top:12px}.k{font-size:12px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}.v{font-size:18px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:5px 6px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--mute);font-weight:600}td.n{text-align:right;font-variant-numeric:tabular-nums}
.banner{padding:10px 14px;border-radius:8px;border:1px solid var(--bad);color:var(--bad);margin:12px 0;font-weight:600}svg text{fill:var(--mute);font-size:10px}
.err{color:var(--warn);font-size:12px;word-break:break-word}select,a{color:var(--blue)}select{font:inherit;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:3px 6px}
</style></head><body><main><div id="root"><p class="mute">Loading…</p></div></main><script>
const RACE=__RACE__;let timer=null,last=null,fails=0;
const $=(s)=>document.createElement(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmtN=n=>n==null?"—":Number(n).toLocaleString();
const fmtD=s=>{if(s==null)return"—";s=Math.round(s);if(s<60)return s+"s";const m=Math.floor(s/60);if(m<60)return m+"m "+(s%60)+"s";return Math.floor(m/60)+"h "+(m%60)+"m"};
const fmtT=t=>t?new Date(t*1000).toLocaleTimeString():"—";
const fmtS=x=>x==null?"—":Number(x).toFixed(2);
function spark(its){const pts=its.filter(i=>i.score!=null);if(pts.length<1)return'<span class="mute">No scored iterations yet</span>';
 const W=300,H=70,p=14,max=Math.max(...pts.map(i=>i.score),1),n=Math.max(its.length,2);
 const x=i=>p+(W-2*p)*(i/(n-1)),y=v=>H-p-(H-2*p)*(v/max);
 const d=pts.map((i,k)=>(k?"L":"M")+x(i.index).toFixed(1)+" "+y(i.score).toFixed(1)).join(" ");
 const dots=pts.map(i=>`<circle cx="${x(i.index).toFixed(1)}" cy="${y(i.score).toFixed(1)}" r="3.5" fill="var(--blue)"><title>Iteration ${i.index}: ${fmtS(i.score)}</title></circle>`).join("");
 return`<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Development score by iteration"><line x1="${p}" y1="${H-p}" x2="${W-p}" y2="${H-p}" stroke="var(--line)"/><path d="${d}" fill="none" stroke="var(--blue)" stroke-width="2"/>${dots}<text x="${p}" y="9">max ${fmtS(max)}</text></svg>`}
function bar(used,max,label){if(!max)return"";const f=Math.min(used/max,1);const c=f>.9?"bad":f>.7?"warn":"";return`<div class="k">${label}</div><div class="bar ${c}" role="progressbar" aria-valuenow="${used}" aria-valuemax="${max}"><i style="width:${(f*100).toFixed(1)}%"></i></div><div class="mute">${fmtN(used)} of ${fmtN(max)} (${(f*100).toFixed(0)}%)</div>`}
function entrant(e,s){
 const segs=[];for(let k=0;k<e.iterations_total;k++){const it=e.iterations.find(i=>i.index===k);const st=it?it.state:"pending";
  const tip=it?(st==="running"?`Iteration ${k}: in progress, ${it.action_runs} action runs, ${fmtN(it.iteration_tokens)} tokens`:st==="not_raced"?`Iteration ${k}: not raced — ${esc(it.reason||"incomplete")}`:`Iteration ${k}: score ${fmtS(it.score)}${it.duration_s?`, ${fmtD(it.duration_s)}`:""}`):`Iteration ${k}: waiting`;
  segs.push(`<div class="seg ${st}" title="${tip}">${it&&it.score!=null&&st==="raced"?fmtS(it.score):k}</div>`)}
 segs.push(`<div class="seg final ${e.phase==="complete"?(e.final.incomplete?"not_raced":"done"):""}" title="Held-out race">${e.phase==="complete"?(e.final.incomplete?"0 (no design)":"held-out"):"held-out"}</div>`);
 const state={queued:"Waiting for the other entrant",iterating:`Iteration ${e.current_iteration??e.iterations_done} of ${e.iterations_total}`,final:"Running the held-out race",complete:"Finished"}[e.phase];
 const b=e.budget;
 const ev=e.recent_events.slice().reverse().map(v=>`<tr><td>${fmtT(v.at)}</td><td>iter ${v.iteration}</td><td>${esc(v.action)}${v.simulator?" (simulator)":""}</td><td class="n">${v.simulator?"—":fmtN((v.input_tokens||0)+(v.output_tokens||0))}</td></tr>`).join("");
 const pr=e.problems.slice().reverse().map(p=>`<div class="err">iter ${p.iteration} · ${esc(p.action)} attempt ${p.attempt} · ${esc(p.error)}</div>`).join("");
 const tr=(e.iterations.filter(i=>i.state==="raced").slice(-1)[0]||{trials:[]}).trials.map(t=>`<tr><td>${esc(t.track)}</td><td class="n">${fmtS(t.score)}</td><td>${esc(t.termination)}</td></tr>`).join("");
 const fin=e.final&&!e.final.incomplete?e.final.trials.map(t=>`${esc(t.track)}: <b>${fmtS(t.score)}</b> (${esc(t.termination)})`).join(" · "):e.final?`No design delivered: ${esc(e.final.reason||"")}`:"";
 return`<section class="card"><div class="top"><h2>${esc(e.entrant)} <span class="mute">· ${esc(e.model)}</span></h2><span class="mute">${state}</span></div>
 <div class="segs" aria-label="Iterations">${segs.join("")}</div>
 <div class="mute" style="font-size:12px">Boxes show the development score once an iteration is raced; the last box is the held-out race.</div>
 ${fin?`<p>Held-out result — ${fin}</p>`:""}
 <div class="grid"><div>${bar(b.total_used,b.total_max,"Token budget (whole condition)")}</div>
 ${e.phase==="iterating"&&b.iteration_max?`<div>${bar(b.iteration_used||0,b.iteration_max,"Tokens this iteration")}</div>`:""}
 ${e.phase==="iterating"&&b.runs_max?`<div>${bar(b.runs_used||0,b.runs_max,"Action runs this iteration")}</div>`:""}</div>
 <div class="grid"><div><div class="k">Latest / best dev score</div><div class="v">${fmtS(e.scores.latest)} / ${fmtS(e.scores.best)}</div></div>
 <div><div class="k">Model calls so far</div><div class="v">${e.total_calls}</div></div>
 <div><div class="k">Rejected outputs</div><div class="v">${e.problem_count}</div></div>
 <div><div class="k">Typical iteration</div><div class="v">${fmtD(e.avg_iteration_s)}</div></div>
 <div><div class="k">This entrant ETA (estimate)</div><div class="v">${e.eta_s!=null?fmtD(e.eta_s):"—"}</div></div></div>
 <div class="grid"><div><div class="k">Development score by iteration</div>${spark(e.iterations)}</div>
 <div><div class="k">Latest raced iteration, by track</div><table><tr><th>Track</th><th>Score</th><th>Ended</th></tr>${tr||'<tr><td colspan="3" class="mute">Nothing raced yet</td></tr>'}</table></div></div>
 <div class="grid"><div><div class="k">Recent actions</div><table><tr><th>Time</th><th>Iter</th><th>Action</th><th>Tokens</th></tr>${ev||'<tr><td colspan="4" class="mute">None yet</td></tr>'}</table></div>
 <div><div class="k">Latest rejected outputs (sent back for repair)</div>${pr||'<span class="mute">None</span>'}</div></div></section>`}
function render(s){
 const pct=(s.fraction*100).toFixed(0);
 const warn=s.health==="stalled"?`<div class="banner">No activity for ${fmtD(s.quiet_for_s)} (normal gaps are under ${fmtD(s.quiet_threshold_s)}). The race may be waiting on a slow model call, or it was interrupted — if the server stopped, use “Resume frozen race”.</div>`:"";
 const err=s.status==="failed"&&s.error?`<div class="banner">Race failed: ${esc(s.error.message||s.error)}</div>`:"";
 const picker=s.running_races.length>1?` · running: ${s.running_races.map(r=>`<a href="?race_id=${r}">${r}</a>`).join(", ")}`:"";
 document.getElementById("root").innerHTML=`<div class="top"><div><h1>${esc(s.race_id)} <span class="pill ${s.health}">${s.health==="active"?"running":s.health}</span></h1>
 <div class="mute">Updated ${fmtT(s.generated_at)} · refreshes every 2s${picker}</div></div>
 <div style="text-align:right"><div class="v">${pct}%</div><div class="mute">${s.units_done} of ${s.units_total} stages · ETA ${s.eta_s!=null?fmtD(s.eta_s):"—"}</div></div></div>
 <div class="bar" style="margin-top:10px" role="progressbar" aria-valuenow="${pct}" aria-valuemax="100"><i style="width:${pct}%"></i></div>
 <p class="mute" style="font-size:12px">A stage is one iteration or one held-out race, per entrant. Entrants run one after the other. ETA is an estimate from recent iteration times; it rises as history grows.</p>
 ${warn}${err}${s.entrants.map(e=>entrant(e,s)).join("")}`}
async function tick(){
 try{const r=await fetch("progress.json"+(RACE?"?race_id="+encodeURIComponent(RACE):""),{cache:"no-store"});const s=await r.json();if(!r.ok)throw new Error(s.error||r.status);fails=0;last=s;render(s);
  if(s.status!=="running"&&s.status!=="frozen"){clearInterval(timer);timer=setInterval(tick,15000)}}
 catch(e){fails++;if(!last)document.getElementById("root").innerHTML=`<div class="banner">${esc(e.message)}</div>`;else if(fails>2)document.getElementById("root").insertAdjacentHTML("afterbegin",`<div class="banner">Lost contact with the server (${esc(e.message)}). Showing the last update.</div>`)}}
tick();timer=setInterval(tick,2000);
</script></body></html>'''


def page(race_id: str | None) -> bytes:
    return PAGE.replace("__RACE__", json.dumps(race_id)).encode()


def handle(path: str, root: Path = ROOT) -> tuple[int, str, bytes]:
    """Route a GET for /progress or /progress.json. Returns (status, content-type, body); shared by web.py and the standalone server."""
    parsed = urlparse(path)
    race_id = (parse_qs(parsed.query).get("race_id") or [None])[0] or latest_race(root)
    if parsed.path.endswith("progress.json"):
        try:
            if not race_id:
                raise FileNotFoundError("no races yet")
            return 200, "application/json", json.dumps(snapshot(race_id, root)).encode()
        except (FileNotFoundError, ValueError) as error:
            return 404, "application/json", json.dumps({"error": str(error)}).encode()
    return 200, "text/html; charset=utf-8", page(race_id)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/progress", "/progress.json"}:
            self.send_error(404); return
        status, kind, body = handle("/progress.json" + ("?" + parsed.query if parsed.query else "") if parsed.path.endswith(".json") else self.path)
        self.send_response(status); self.send_header("Content-Type", kind); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Live progress for a Robot Race (read-only).")
    parser.add_argument("race_id", nargs="?"); parser.add_argument("--port", type=int, default=8766); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--json", action="store_true", help="print one snapshot and exit")
    args = parser.parse_args(argv)
    if args.json:
        print(json.dumps(snapshot(args.race_id or latest_race() or "", ROOT), indent=2)); return 0
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("local binding required")
    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    suffix = f"?race_id={args.race_id}" if args.race_id else ""
    print(f"Race progress: http://{args.host}:{args.port}/{suffix}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
