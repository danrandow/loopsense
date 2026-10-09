from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import yaml

from simulator.adapter.headless import _track_polyline

from .io import atomic_write


def _brief(value: Any, limit: int = 230) -> str:
    text = " ".join(str(value or "").split("\n\n", 1)[0].split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _sample(points: list[dict[str, Any]], maximum: int = 180) -> list[list[float]]:
    if not points:
        return []
    stride = max(1, (len(points) - 1) // (maximum - 1))
    selected = points[::stride]
    if selected[-1] is not points[-1]:
        selected.append(points[-1])
    return [[round(float(p.get("x", 0)) * 1000, 2), round(float(p.get("y", 0)) * 1000, 2), round(float(p.get("heading", 0)), 4), round(float(p.get("progress", 0)), 4), bool(p.get("line_lost", False))] for p in selected]


def _story(package: Path, section: str, track_roots: dict[str, Path]) -> list[dict[str, Any]]:
    summary_path = package / section / "summary.json"
    if not summary_path.is_file():
        return []
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    held_out = bool(summary.get("held_out"))
    iteration = None if held_out else int(section.rsplit("-", 1)[1])
    scenario_path = package / f"scenario-iteration-{iteration}.yaml" if iteration is not None else None
    scenario = yaml.safe_load(scenario_path.read_text(encoding="utf-8")) if scenario_path and scenario_path.is_file() else {}
    entities = {item.get("id"): item for item in scenario.get("overrides", {}).get("entities", [])}
    geometry_entity = entities.get("entity0") or {}
    robot_entity = entities.get("entity1") or {}
    result_entity = entities.get("entity2") or {}
    feedback_entity = entities.get("entityR1") or {}
    geometry_return = entities.get("entityR2A") or {}
    integrator_return = entities.get("entityR2B") or {}
    beats = {
        "geometry": {"label": geometry_entity.get("label", "Geometry proposal"), "notes": _brief(geometry_entity.get("notes"))},
        "robot": {"label": robot_entity.get("label", "Integrated robot"), "notes": _brief(robot_entity.get("notes"))},
        "race": {"label": result_entity.get("label", "Race outcome"), "notes": _brief(result_entity.get("notes"))},
        "learning": {"label": feedback_entity.get("label", "Integration feedback"), "notes": _brief(feedback_entity.get("notes"))},
        "returns": [_brief(geometry_return.get("notes")), _brief(integrator_return.get("notes"))],
    }
    entrant = package.name.split("-", 2)[-1]
    stories = []
    for trial in summary.get("trials", []):
        telemetry_path = package / trial["telemetry"]
        result_path = package / trial["result"]
        telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
        result = json.loads(result_path.read_text(encoding="utf-8"))
        track_id = trial["track"]
        track_path = track_roots["held-out" if held_out else ("anchor" if track_id == "oval" else "development")] / f"{track_id}.json"
        track = json.loads(track_path.read_text(encoding="utf-8"))
        stories.append({
            "entrant": entrant,
            "iteration": iteration,
            "phase": "Held-out finale" if held_out else f"Iteration {iteration}",
            "track": track_id,
            "seed": trial["seed"],
            "score": float(trial["score"]),
            "termination": trial.get("termination_reason"),
            "progress": float(result.get("metrics", {}).get("progress", 0)),
            "lineLosses": int(result.get("metrics", {}).get("line_loss_events", 0)),
            "beats": beats if not held_out else {
                "geometry": {"label": "Final geometry", "notes": "The final geometry is locked before the held-out track is revealed."},
                "robot": {"label": "Final robot", "notes": "The final integrated geometry and controller enter the held-out evaluation unchanged."},
                "race": {"label": "Held-out evidence", "notes": f"{trial.get('termination_reason')}, score {float(trial['score']):.2f}, progress {float(result.get('metrics', {}).get('progress', 0)):.1%}."},
                "learning": {"label": "No return before scoring", "notes": "Held-out evidence closes the experiment; it was not available to either team while adapting."},
                "returns": [],
            },
            "scenario": str(scenario_path.relative_to(package.parent)) if scenario_path else None,
            "trackPoints": [[round(x, 2), round(y, 2)] for x, y in _track_polyline(track)[::3]],
            "poses": _sample(telemetry),
        })
    return stories


def render_race_replay(race_id: str, packages: list[Path], output: Path) -> Path:
    """Create a self-contained pit-wall replay from authoritative race artefacts."""
    robotrace_root = Path(__file__).resolve().parents[1]
    track_roots = {kind: robotrace_root / "tracks" / kind for kind in ("anchor", "development", "held-out")}
    items: list[dict[str, Any]] = []
    iterations = max((len(list(package.glob("iteration-*/summary.json"))) for package in packages), default=0)
    for iteration in range(iterations):
        for package in packages:
            items += _story(package, f"iteration-{iteration}", track_roots)
    for package in packages:
        items += _story(package, "final-held-out", track_roots)
    payload = json.dumps({"race": race_id, "items": items}, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(f"{race_id} pit replay")
    document = _DOCUMENT.replace("__TITLE__", title).replace("__PAYLOAD__", payload)
    atomic_write(output, document)
    return output


_DOCUMENT = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--ink:#302a47;--muted:#6d6688;--paper:#fff8e7;--field:#dcf5e7;--line:#4c4668;--pink:#ff5d8f;--violet:#7c5cff;--green:#16856f;--amber:#d88900;--red:#c83f54}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.4 ui-rounded,"Avenir Next",system-ui,sans-serif}.shell{max-width:1180px;margin:auto;padding:20px}.top{display:flex;justify-content:space-between;gap:20px;align-items:end}.eyebrow,.label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}h1{margin:3px 0;font-size:30px}button,input{font:inherit}button{border:0;border-radius:999px;padding:9px 14px;background:#fff;color:var(--ink);box-shadow:0 1px 0 #cfc7ad;cursor:pointer}button.primary{background:var(--ink);color:#fff}.stage{display:grid;grid-template-columns:minmax(0,2.2fr) minmax(270px,1fr);gap:16px;margin-top:16px}.track-card,.pit{background:#fff;border-radius:22px;overflow:hidden;box-shadow:0 10px 30px #51483018}.track-head{display:flex;justify-content:space-between;padding:14px 18px}.score{font-size:22px;font-weight:700}.field{background:var(--field);min-height:440px;position:relative}svg{width:100%;height:440px;display:block}.pit{padding:18px}.pit h2{margin:4px 0 14px}.beat{border-left:4px solid var(--violet);padding-left:12px;margin:18px 0}.beat.record{border-color:var(--green)}.beat p{margin:4px 0}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.stat{background:#f5f1ff;border-radius:12px;padding:10px}.stat strong{display:block;font-size:18px}.controls{display:flex;gap:8px;align-items:center;padding:14px 18px}.controls input{flex:1}.timeline{display:flex;gap:8px;overflow:auto;padding:16px 0}.timeline button{white-space:nowrap}.timeline button.active{background:var(--violet);color:#fff}.car-body{fill:var(--pink);stroke:var(--ink);stroke-width:2}.car-eye{fill:#fff;stroke:var(--ink);stroke-width:1}.wheel{fill:var(--ink)}.trail{fill:none;stroke:var(--green);stroke-width:3;stroke-linecap:round}.track{fill:none;stroke:#fff;stroke-width:18;stroke-linecap:round;stroke-linejoin:round}.tape{fill:none;stroke:var(--line);stroke-width:10;stroke-linecap:round;stroke-linejoin:round}.lost{fill:var(--red)}.status{padding:4px 9px;border-radius:999px;background:#f5f1ff}.overview-bg{fill:#fff;fill-opacity:.9;stroke:#8ac6a3;stroke-width:1}.overview-track{fill:none;stroke:var(--line);stroke-width:3;stroke-linecap:round}.overview-dot{fill:var(--pink);stroke:var(--ink);stroke-width:1}@media(max-width:800px){.stage{grid-template-columns:1fr}.field,svg{min-height:330px;height:330px}.top{align-items:start;flex-direction:column}}
</style></head><body><main class="shell"><header class="top"><div><div class="eyebrow">Map → attempt → evidence → adaptation</div><h1 id="title"></h1><div id="subtitle"></div></div><div><button id="prev">← Previous</button> <button class="primary" id="play">Pause</button> <button id="next">Next →</button></div></header><div class="timeline" id="timeline"></div><section class="stage"><div class="track-card"><div class="track-head"><div><strong id="entrant"></strong><div id="trial"></div></div><div><span class="status" id="status"></span> <span class="score" id="score"></span></div></div><div class="field"><svg id="race" role="img" aria-label="Animated recorded robot trial" viewBox="0 0 760 440"><path class="track" id="trackShadow"/><path class="tape" id="track"/><path class="trail" id="trail"/><g id="car"><rect class="wheel" x="-15" y="-15" width="11" height="7" rx="3"/><rect class="wheel" x="-15" y="8" width="11" height="7" rx="3"/><rect class="wheel" x="7" y="-15" width="11" height="7" rx="3"/><rect class="wheel" x="7" y="8" width="11" height="7" rx="3"/><rect class="car-body" x="-18" y="-12" width="36" height="24" rx="10"/><circle class="car-eye" cx="10" cy="-5" r="3"/><circle class="car-eye" cx="10" cy="5" r="3"/></g><circle class="lost" id="lost" r="6" visibility="hidden"/><g id="overview"><rect class="overview-bg" x="570" y="18" width="170" height="104" rx="10"/><path class="overview-track" id="overviewTrack"/><circle class="overview-dot" id="overviewDot" r="4"/></g></svg></div><div class="controls"><span id="time">0%</span><input id="scrub" aria-label="Trial position" type="range" min="0" max="1000" value="0"><span class="label">Camera</span><button data-zoom="1">Fit</button><button data-zoom="2">2×</button><button data-zoom="4">4×</button><button data-zoom="8">8×</button><button data-zoom="auto">Auto</button></div></div><aside class="pit"><div class="eyebrow">Map projection</div><h2 id="phase"></h2><div class="beat"><div class="label">1 · Geometry Builder produced</div><strong id="geometryLabel"></strong><p id="geometryNotes"></p></div><div class="beat"><div class="label">2 · Robot Integrator produced</div><strong id="robotLabel"></strong><p id="robotNotes"></p></div><div class="beat record"><div class="label">3 · Race Simulator recorded</div><strong id="raceLabel"></strong><p id="raceNotes"></p></div><div class="beat record"><div class="label">4 · Return loop carried forward</div><strong id="learningLabel"></strong><p id="learningNotes"></p></div><div class="stats"><div class="stat"><span>Progress</span><strong id="progress"></strong></div><div class="stat"><span>Line losses</span><strong id="losses"></strong></div></div></aside></section></main><script id="race-data" type="application/json">__PAYLOAD__</script><script>
const data=JSON.parse(document.getElementById('race-data').textContent),items=data.items;let index=0,playing=true,start=performance.now(),fraction=0,zoomChoice='auto';
const $=id=>document.getElementById(id), svg=$('race'), NS='http://www.w3.org/2000/svg';$('title').textContent=data.race+' — the whole race';
function extent(points,margin=.09){const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);let a=Math.min(...xs),b=Math.max(...xs),c=Math.min(...ys),d=Math.max(...ys),m=Math.max(b-a,d-c)*margin||1;return[a-m,b+m,c-m,d+m]}
function makeMapper(box,width=700,height=380,left=30,top=30){const[a,b,c,d]=box,s=Math.min(width/(b-a),height/(d-c)),ox=left+(width-(b-a)*s)/2-a*s,oy=top+(height-(d-c)*s)/2+d*s,fn=p=>[ox+p[0]*s,oy-p[1]*s];fn.scale=s;return fn}
function fullMapper(item){return makeMapper(extent(item.trackPoints.concat(item.poses.map(p=>[p[0],p[1]]))))}
function mapper(item){const fullBox=extent(item.trackPoints.concat(item.poses.map(p=>[p[0],p[1]]))),full=makeMapper(fullBox),requested=zoomChoice==='auto'?(item.progress>=.25?1:null):Number(zoomChoice);if(requested===1){full.zoom=1;return full}const pts=item.poses.map(p=>[p[0],p[1]]),box=extent(pts,.22),cx=(box[0]+box[1])/2,cy=(box[2]+box[3])/2;if(requested){const w=(fullBox[1]-fullBox[0])/requested,h=(fullBox[3]-fullBox[2])/requested,chosen=makeMapper([cx-w/2,cx+w/2,cy-h/2,cy+h/2]);chosen.zoom=requested;return chosen}const minSpan=420,w=Math.max(box[1]-box[0],minSpan),h=Math.max(box[3]-box[2],minSpan),close=makeMapper([cx-w/2,cx+w/2,cy-h/2,cy+h/2]);close.zoom=close.scale/full.scale;return close}
function miniMapper(item){return makeMapper(extent(item.trackPoints),142,76,584,32)}
function path(points,map){return points.map((p,i)=>{const q=map(p);return(i?'L':'M')+q[0].toFixed(1)+' '+q[1].toFixed(1)}).join(' ')}
function load(n){index=(n+items.length)%items.length;fraction=0;start=performance.now();const x=items[index],map=mapper(x),mini=miniMapper(x),beats=x.beats;$('subtitle').textContent=`${items.length} recorded trials · development history and held-out finale`;$('entrant').textContent=x.entrant;$('trial').textContent=`${x.track} · seed ${x.seed}`;$('phase').textContent=x.phase;$('status').textContent=x.termination;$('score').textContent=x.score.toFixed(2);$('geometryLabel').textContent=beats.geometry.label;$('geometryNotes').textContent=beats.geometry.notes||'No geometry note was recorded.';$('robotLabel').textContent=beats.robot.label;$('robotNotes').textContent=beats.robot.notes||'No integration note was recorded.';$('raceLabel').textContent=beats.race.label;$('raceNotes').textContent=beats.race.notes||'The result and telemetry are the race record.';$('learningLabel').textContent=beats.learning.label;$('learningNotes').textContent=beats.learning.notes||beats.returns.filter(Boolean).join(' ')||'No return note was recorded.';$('progress').textContent=(x.progress*100).toFixed(1)+'%';$('losses').textContent=x.lineLosses;$('overview').style.display=map.zoom>1.05?'block':'none';$('overviewTrack').setAttribute('d',path(x.trackPoints,mini));$('track').setAttribute('d',path(x.trackPoints,map));$('trackShadow').setAttribute('d',path(x.trackPoints,map));$('trail').setAttribute('d','');document.querySelectorAll('.timeline button').forEach((b,i)=>b.classList.toggle('active',i===index));document.querySelectorAll('[data-zoom]').forEach(b=>b.classList.toggle('primary',b.dataset.zoom===String(zoomChoice)));draw(0)}
function draw(f){const x=items[index],poses=x.poses;if(!poses.length)return;fraction=Math.max(0,Math.min(1,f));const at=Math.min(poses.length-1,Math.floor(fraction*(poses.length-1))),map=mapper(x),mini=miniMapper(x),p=poses[at],q=map(p),mq=mini(p);$('car').setAttribute('transform',`translate(${q[0]} ${q[1]}) rotate(${-p[2]*180/Math.PI})`);$('trail').setAttribute('d',path(poses.slice(0,at+1),map));$('lost').setAttribute('cx',q[0]);$('lost').setAttribute('cy',q[1]);$('lost').setAttribute('visibility',p[4]?'visible':'hidden');$('overviewDot').setAttribute('cx',mq[0]);$('overviewDot').setAttribute('cy',mq[1]);$('scrub').value=Math.round(fraction*1000);$('time').textContent=Math.round(fraction*100)+'%'}
items.forEach((x,i)=>{const b=document.createElement('button');b.textContent=(x.iteration===null?'Finale':'I'+x.iteration)+' · '+x.entrant+' · '+x.track;b.onclick=()=>load(i);$('timeline').appendChild(b)});
function tick(now){if(playing){const f=(now-start)/4200;if(f>=1){load(index+1)}else draw(f)}requestAnimationFrame(tick)}
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause':'Play';start=performance.now()-fraction*4200};$('prev').onclick=()=>load(index-1);$('next').onclick=()=>load(index+1);document.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{const keep=fraction;zoomChoice=b.dataset.zoom;load(index);fraction=keep;start=performance.now()-fraction*4200;draw(fraction)});$('scrub').oninput=e=>{playing=false;$('play').textContent='Play';draw(+e.target.value/1000)};load(0);requestAnimationFrame(tick);
</script></body></html>'''
