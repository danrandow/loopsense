from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from simulator.adapter import ADAPTER_VERSION, run_trial
from .executors import project_design

from .artifacts import leaderboard_svg, summary_svg, track_view_svg, trajectory_svg
from .controller import MapDrivenController, clone_package
from .executors import PackageExecutor
from .io import atomic_write, digest, read_json, safe_child, write_json
from .map_package import MapPackage, PackageValidationError
import yaml


TEMPLATES = Path(__file__).resolve().parents[1] / "package-templates"
ROOT = Path(__file__).resolve().parents[2]



def _iteration_links(package: str) -> str:
    """Markdown links to every scenario-iteration file the package has, in numeric order."""
    root = Path(package)
    files = sorted(root.glob("scenario-iteration-*.yaml"), key=lambda path: int(path.stem.rsplit("-", 1)[1]))
    return " — ".join(f"[iteration {path.stem.rsplit('-', 1)[1]}]({root.name}/{path.name})" for path in files)

class RaceStateError(RuntimeError):
    """The request conflicts with the race's current state or configuration (HTTP 409)."""


class PreRunCheckError(RaceStateError):
    """A configuration problem found before any model or simulator work starts."""


class RaceRunError(RuntimeError):
    """Execution failed after the race started; the cause is recorded in the pair file (HTTP 500)."""


def safe_race_id(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug or slug in {"race-5", "race-6", "race-7"}:
        raise ValueError("choose a named dry run or a fresh numbered race other than 5, 6, or 7")
    return slug


class MapDrivenRaceService:
    def __init__(self, race_id: str, workspace: Path = ROOT):
        self.race_id = safe_race_id(race_id)
        self.workspace = workspace.resolve()
        self.pair_path = self.workspace / f"{self.race_id}-pair.json"
        self.packages = [self.workspace / f"{self.race_id}-randow-maps", self.workspace / f"{self.race_id}-opt-eval"]

    def prepare(self) -> list[Path]:
        if any(path.exists() for path in self.packages):
            raise FileExistsError("race-owned package already exists")
        clone_package(TEMPLATES / "randow-maps", self.packages[0], self.race_id)
        clone_package(TEMPLATES / "opt-eval", self.packages[1], self.race_id)
        write_json(self.pair_path, {"race_id": self.race_id, "status": "prepared", "packages": [str(path) for path in self.packages], "reviewed": {}})
        return self.packages

    def review(self, entrant: str) -> None:
        state = read_json(self.pair_path)
        matches = [path for path in self.packages if path.name.endswith("-" + entrant)]
        if not matches:
            raise ValueError("unknown entrant")
        state["reviewed"][entrant] = True
        write_json(self.pair_path, state)

    def configure_common(self, settings: dict[str, Any]) -> None:
        state = read_json(self.pair_path)
        if state.get("status") != "prepared":
            raise RaceStateError("race settings are editable only before freeze")
        for package in self.packages:
            race_path = package / "config" / "race.yaml"
            race = yaml.safe_load(race_path.read_text(encoding="utf-8"))
            race["iterations"] = int(settings["iterations"])
            race["model"].update({
                "provider": settings["provider"],
                "id": settings["model_id"],
                "max_output_tokens": int(settings["max_output_tokens"]),
            })
            race["budget"].update({
                "max_action_runs": int(settings["max_action_runs"]),
                "total_tokens_per_condition": int(settings["total_tokens_per_condition"]),
                "max_tokens_per_iteration": int(settings["max_tokens_per_iteration"]),
            })
            atomic_write(race_path, yaml.safe_dump(race, sort_keys=False))
        state["reviewed"] = {}
        write_json(self.pair_path, state)

    def editable_definitions(self, entrant: str) -> list[str]:
        matches = [path for path in self.packages if path.name.endswith("-" + entrant)]
        if not matches:
            raise ValueError("unknown entrant")
        allowed = {"base.yaml", "config/workflow.yaml", "config/race.yaml"}
        allowed |= {str(path.relative_to(matches[0])) for path in matches[0].glob("actions/*/*")}
        allowed |= {str(path.relative_to(matches[0])) for path in matches[0].glob("entities/*/contract.schema.json")}
        return sorted(allowed)

    def update_definition(self, entrant: str, relative_path: str, content: str) -> None:
        state = read_json(self.pair_path)
        if state.get("status") != "prepared":
            raise RaceStateError("definitions are editable only before freeze")
        matches = [path for path in self.packages if path.name.endswith("-" + entrant)]
        if not matches:
            raise ValueError("unknown entrant")
        allowed = set(self.editable_definitions(entrant))
        if relative_path not in allowed:
            raise ValueError("file is not an editable package definition")
        atomic_write(safe_child(matches[0], *relative_path.split("/")), content)
        state["reviewed"].pop(entrant, None)
        write_json(self.pair_path, state)

    def validate_pair(self) -> list[MapPackage]:
        packages = [MapPackage(path).validate() for path in self.packages]
        common = ["race_id", "iterations", "model", "budget", "evaluation", "simulator", "design_bounds", "score", "objective", "history"]
        for key in common:
            if packages[0].race.get(key) != packages[1].race.get(key):
                raise PackageValidationError(f"race pair mismatch: {key}")
        if packages[0].race["race_id"] != self.race_id:
            raise PackageValidationError("race/package identity mismatch")
        return packages

    def freeze(self) -> None:
        state = read_json(self.pair_path)
        if set(state["reviewed"]) != {"randow-maps", "opt-eval"}:
            raise RaceStateError("both entrant reviews are required")
        packages = self.validate_pair()
        manifests = []
        for package in packages:
            controller = MapDrivenController(package, PackageExecutor(package), ADAPTER_VERSION)
            manifests.append(controller.freeze(package.path("race-manifest.json")))
        state.update({"status": "frozen", "manifests": [manifest["manifest_hash"] for manifest in manifests], "controller": "map-driven"})
        write_json(self.pair_path, state)

    def preflight(self) -> list[MapDrivenController]:
        state = read_json(self.pair_path)
        if state.get("status") not in {"frozen", "running", "complete"} or state.get("controller") != "map-driven":
            raise RaceStateError("race pair is not frozen for map-driven execution")
        if set(state.get("reviewed", {})) != {"randow-maps", "opt-eval"}:
            raise RaceStateError("review acknowledgements are missing")
        controllers = []
        for package in self.validate_pair():
            controller = MapDrivenController(package, PackageExecutor(package), ADAPTER_VERSION)
            controller.verify_frozen(package.path("race-manifest.json"))
            if not package.ready_actions(set(), {}):
                raise RuntimeError("package has no initially eligible action")
            controllers.append(controller)
        return controllers

    def run_warnings(self) -> list[str]:
        """Non-blocking configuration warnings for the run section of the UI."""
        race = yaml.safe_load((self.packages[0] / "config" / "race.yaml").read_text(encoding="utf-8"))
        provider, model_id = str(race["model"]["provider"]), str(race["model"]["id"])
        warnings = []
        if provider != "mock" and "mock" in model_id.lower():
            warnings.append(f"model id '{model_id}' looks like the offline mock but provider is '{provider}'; the mock only activates when provider is 'mock'")
        return warnings

    def check_run_settings(self) -> None:
        """Block runs that cannot succeed. Runs before the pair is marked running, so a refusal leaves the race frozen."""
        race = yaml.safe_load((self.packages[0] / "config" / "race.yaml").read_text(encoding="utf-8"))
        if race["model"]["provider"] == "openrouter" and not os.environ.get("OPENROUTER_API_KEY", "").strip():
            hint = "".join(f" Warning: {warning}." for warning in self.run_warnings())
            raise PreRunCheckError("provider is 'openrouter' but no API key is set; enter a key or use provider 'mock'." + hint)

    def retire(self) -> None:
        """Take a failed or stuck race out of service without deleting its evidence. Race ids are never reused."""
        state = read_json(self.pair_path)
        if state.get("status") not in {"failed", "running"}:
            raise RaceStateError("only failed or running races can be retired")
        state.update({"status": "retired", "retired_from": state["status"]})
        write_json(self.pair_path, state)

    def run(self) -> Path:
        controllers = self.preflight()
        self.check_run_settings()
        state = read_json(self.pair_path)
        state["status"] = "running"
        state.pop("error", None)
        write_json(self.pair_path, state)
        try:
            return self._execute(controllers, state)
        except Exception as error:
            failed = read_json(self.pair_path)
            failed.update({"status": "failed", "error": {"type": type(error).__name__, "message": str(error)}})
            write_json(self.pair_path, failed)
            raise RaceRunError(f"{type(error).__name__}: {error}") from error

    def _execute(self, controllers: list[MapDrivenController], state: dict[str, Any]) -> Path:
        scores: list[dict[str, Any]] = []
        for controller in controllers:
            for iteration in range(int(controller.package.race["iterations"])):
                controller.run_iteration(iteration)
                self._publish_iteration(controller.package, iteration)
            last = controller.package.path(f"iteration-{controller.package.race['iterations'] - 1}", "entity2", "current")
            result = None
            if last.is_file():
                version = last.read_text().strip()
                result = json.loads((last.parent / "versions" / version / "payload.json").read_text())
            design_current = controller.package.path(f"iteration-{controller.package.race['iterations'] - 1}", "entity1", "current")
            if not design_current.is_file():
                # The team did not ship a design in the final iteration (budget spent, or an output left undelivered).
                # That is the team's result, not a harness fault: the held-out score is 0 and nothing is raced.
                outcome_path = controller.package.path(f"iteration-{controller.package.race['iterations'] - 1}", "outcome.json")
                outcome = json.loads(outcome_path.read_text()) if outcome_path.is_file() else {}
                write_json(controller.package.path("final-evaluation.json"), {"held_out": True, "incomplete": True, "reason": outcome.get("reason", "no design delivered in the final iteration"), "undelivered": outcome.get("undelivered", []), "trials": [], "simulator_version": ADAPTER_VERSION})
                scores.append({"entrant": controller.package.race["entrant"], "score": 0.0, "development_score": None, "incomplete": True, "package": str(controller.package.root)})
                continue
            design_version = design_current.read_text().strip()
            design = json.loads((design_current.parent / "versions" / design_version / "payload.json").read_text())
            held_out_trials = []
            robotrace_root = Path(__file__).resolve().parents[1]
            for track_name in controller.package.race["evaluation"]["held_out_tracks"]:
                track = json.loads((robotrace_root / "tracks" / "held-out" / f"{track_name}.json").read_text())
                for seed in controller.package.race["evaluation"]["seeds"]:
                    held_out_trials.append(run_trial(project_design(design), track, seed, controller.package.race))
            invalid = [trial for trial in held_out_trials if trial.get("termination_reason") == "invalid_design"]
            if held_out_trials and len(invalid) == len(held_out_trials):
                raise RuntimeError(f"every held-out trial for {controller.package.race['entrant']} was invalid_design ({invalid[0].get('error')}); refusing to publish a leaderboard")
            write_json(controller.package.path("final-evaluation.json"), {"held_out": True, "trials": held_out_trials, "simulator_version": ADAPTER_VERSION})
            self._publish_trials(controller.package, "final-held-out", design, held_out_trials, held_out=True)
            held_out_score = round(sum(float(trial["score"]) for trial in held_out_trials) / len(held_out_trials), 4)
            scores.append({"entrant": controller.package.race["entrant"], "score": held_out_score, "development_score": result["score"] if result else None, "package": str(controller.package.root), "tokens": self._token_totals(controller.package)})
        scores.sort(key=lambda item: item["score"], reverse=True)
        for controller in controllers:
            self._write_package_report(controller.package, scores)
        leaderboard = self.workspace / f"{self.race_id}-leaderboard.json"
        report = self.workspace / f"{self.race_id}-race-report.md"
        write_json(leaderboard, {"race_id": self.race_id, "results": scores})
        root_lines = self._race_summary_lines(scores)
        root_lines[root_lines.index("[Open the leaderboard chart](leaderboard.svg)")] = f"[Open the leaderboard chart]({Path(scores[0]['package']).name}/leaderboard.svg)"
        root_lines += ["## Team maps", ""] + [f"{index + 1}. {item['entrant']}: {item['score']} — [package]({Path(item['package']).name}/base.yaml) — [team report]({Path(item['package']).name}/race-report.md) — {_iteration_links(item['package'])}" for index, item in enumerate(scores)]
        report.write_text("\n".join(root_lines) + "\n", encoding="utf-8")
        state.update({"status": "complete", "leaderboard": str(leaderboard), "report": str(report), "result_hash": digest(scores)})
        write_json(self.pair_path, state)
        return report

    def _publish_iteration(self, package: MapPackage, iteration: int) -> None:
        entity = package.path(f"iteration-{iteration}", "entity2")
        design_entity = package.path(f"iteration-{iteration}", "entity1")
        if not (entity / "current").is_file() or not (design_entity / "current").is_file():
            return  # incomplete iteration: nothing was raced, so there is nothing to publish
        current = (entity / "current").read_text().strip()
        result = json.loads((entity / "versions" / current / "payload.json").read_text())
        design_current = (design_entity / "current").read_text().strip()
        design = json.loads((design_entity / "versions" / design_current / "payload.json").read_text())
        self._publish_trials(package, f"iteration-{iteration}", design, result["trials"], held_out=False)
        self._link_trial_artefacts(package, iteration, result["trials"])

    @staticmethod
    def _trial_links(section: str, trials: list[dict[str, Any]], kind: str) -> list[str]:
        lines = [f"- [Open {kind} race summary]({section}/iteration-summary.svg)"]
        for trial in trials:
            view = f"{section}/trials/{trial['track']}-{trial['seed']}/track-view.svg"
            lines.append(f"- [{kind}: {trial['track']}-{trial['seed']} track view, score {float(trial['score']):.1f}, {trial.get('termination_reason')}]({view})")
        return lines

    def _link_trial_artefacts(self, package: MapPackage, iteration: int, trials: list[dict[str, Any]]) -> None:
        """Put the race artefacts on the Race Outcome entity of this iteration's scenario, where reviewers look for them."""
        path = package.path(f"scenario-iteration-{iteration}.yaml")
        scenario = yaml.safe_load(path.read_text(encoding="utf-8"))
        entities = scenario.setdefault("overrides", {}).setdefault("entities", [])
        entry = next((item for item in entities if item["id"] == "entity2"), None)
        if entry is None:
            entry = {"id": "entity2"}
            entities.append(entry)
        base = str(entry.get("notes", "")).split("\n\nArtefacts:")[0].strip()
        entry["notes"] = (base + "\n\n" if base else "") + "Artefacts:\n" + "\n".join(self._trial_links(f"iteration-{iteration}", trials, "development"))
        atomic_write(path, yaml.safe_dump(scenario, sort_keys=False, allow_unicode=True))

    def _race_summary_lines(self, scores: list[dict[str, Any]]) -> list[str]:
        """The race-level summary: identical in the root report and in every team's copy, so no team reads as the owner."""
        lines = [f"# {self.race_id} — race report", "", "| Place | Entrant | Held-out score | Final development score |", "|---:|---|---:|---:|"]
        lines += [f"| {i + 1} | {item['entrant']} | {item['score']} | {item['development_score'] if item['development_score'] is not None else '—'} |" for i, item in enumerate(scores)]
        lines += ["", "[Open the leaderboard chart](leaderboard.svg)", ""]
        if all("tokens" in item for item in scores):
            lines += ["## Token cost", "", "Input plus output tokens over every model call. History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).", "",
                      "| Entrant | Model calls | Input tokens | Output tokens | Total tokens | of which history pack (est.) |", "|---|---:|---:|---:|---:|---:|"]
            for item in scores:
                t = item["tokens"]
                lines.append(f"| {item['entrant']} | {t['calls']} | {t['input']} | {t['output']} | {t['input'] + t['output']} | {t['history']} |")
            lines.append(f"| **Race total** | {sum(i['tokens']['calls'] for i in scores)} | {sum(i['tokens']['input'] for i in scores)} | {sum(i['tokens']['output'] for i in scores)} | **{sum(i['tokens']['input'] + i['tokens']['output'] for i in scores)}** | {sum(i['tokens']['history'] for i in scores)} |")
            lines.append("")
        return lines

    @staticmethod
    def _action_call_stats(package: MapPackage, iteration: int) -> list[dict[str, Any]]:
        """One row per recorded action run in this iteration, in the order they completed."""
        events = package.path(f"iteration-{iteration}", "events.jsonl")
        if not events.is_file():
            return []
        calls = []
        for line in events.read_text(encoding="utf-8").splitlines():
            event = json.loads(line) if line.strip() else {}
            if event.get("type") != "action_completed":
                continue
            runtime = event.get("runtime", {})
            is_model = runtime.get("kind") == "model"
            calls.append({"action": event["action"], "model": is_model, "input": event.get("input_tokens") if is_model else None,
                          "output": event.get("output_tokens") if is_model else None, "history": int(event.get("history_tokens_estimate", 0)) if is_model else None, "repairs": runtime.get("repair_attempts", 0) if is_model else None})
        return calls

    @staticmethod
    def _token_totals(package: MapPackage) -> dict[str, int]:
        """Input, output and history-pack tokens (estimate) over every recorded model call of this team."""
        totals = {"input": 0, "output": 0, "history": 0, "calls": 0}
        for iteration in range(int(package.race["iterations"])):
            for call in MapDrivenRaceService._action_call_stats(package, iteration):
                if call["model"]:
                    totals["input"] += call["input"] or 0
                    totals["output"] += call["output"] or 0
                    totals["history"] += call["history"] or 0
                    totals["calls"] += 1
        return totals

    @staticmethod
    def _retriggers(calls: list[dict[str, Any]]) -> int:
        """Runs beyond the first of any action: how often an action was triggered again within one iteration."""
        counts: dict[str, int] = {}
        for call in calls:
            counts[call["action"]] = counts.get(call["action"], 0) + 1
        return sum(count - 1 for count in counts.values())

    def _write_package_report(self, package: MapPackage, scores: list[dict[str, Any]]) -> None:
        """A race report inside the package root (the map app can only open files under the map folder) and a link from every scenario."""
        entrant = package.race["entrant"]
        total = int(package.race["iterations"])
        mine = next((item for item in scores if item["entrant"] == entrant), None)
        lines = self._race_summary_lines(scores)
        lines += [f"## {entrant} iterations", ""]
        for iteration in range(total):
            section = f"iteration-{iteration}"
            summary = package.path(section, "summary.json")
            scenario_name = f"scenario-iteration-{iteration}.yaml"
            if summary.is_file():
                data = json.loads(summary.read_text(encoding="utf-8"))
                mean = sum(float(t["score"]) for t in data["trials"]) / max(1, len(data["trials"]))
                lines.append(f"### Iteration {iteration} — development score {mean:.2f}")
                lines += self._trial_links(section, data["trials"], "development")
            else:
                outcome = package.path(section, "outcome.json")
                reason = json.loads(outcome.read_text(encoding="utf-8")).get("reason", "no result") if outcome.is_file() else "not run"
                lines.append(f"### Iteration {iteration} — not raced ({reason})")
            calls = self._action_call_stats(package, iteration)
            if calls:
                tokens = sum((call["input"] or 0) + (call["output"] or 0) for call in calls)
                lines.append(f"- Action runs: {len(calls)} · re-triggered runs: {self._retriggers(calls)} · tokens: {tokens}")
            lines.append(f"- Scenario file: {scenario_name}")
            lines.append("")
        t = self._token_totals(package)
        cap = int(package.race["budget"]["total_tokens_per_condition"])
        lines += [f"## {entrant} token cost", "", f"- Total: {t['input'] + t['output']} of {cap} allowed ({t['input']} input, {t['output']} output) over {t['calls']} model calls", f"- History pack (estimate, part of input): {t['history']}", ""]
        table = []
        for iteration in range(total):
            for number, call in enumerate(self._action_call_stats(package, iteration), 1):
                if call["model"]:
                    table.append(f"| {iteration} | {number} | {call['action']} | {call['input']} | {call['output']} | {(call['input'] or 0) + (call['output'] or 0)} | {call['repairs']} |")
                else:
                    table.append(f"| {iteration} | {number} | {call['action']} (simulator) | — | — | — | — |")
        if table:
            lines += ["## Action runs and tokens per call", "", "Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.", "",
                      "| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |", "|---:|---:|---|---:|---:|---:|---:|"] + table + [""]
        held = package.path("final-held-out", "summary.json")
        if held.is_file():
            data = json.loads(held.read_text(encoding="utf-8"))
            lines += ["## Final held-out race", ""] + self._trial_links("final-held-out", data["trials"], "held-out") + [""]
        elif package.path("final-evaluation.json").is_file():
            lines += ["## Final held-out race", "", "Not raced: no design was delivered in the final iteration. Score 0.", ""]
        atomic_write(package.path("race-report.md"), "\n".join(lines))
        leaderboard_svg([(item["entrant"], float(item["score"])) for item in scores], f"{self.race_id} held-out leaderboard", package.path("leaderboard.svg"))
        for scenario_path in sorted(package.root.glob("scenario-iteration-*.yaml")):
            scenario = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
            notes = str(scenario["map"].get("notes", "")).split("\n\n[Read the race report]")[0].rstrip()
            scenario["map"]["notes"] = notes + "\n\n[Read the race report](race-report.md) · [Leaderboard](leaderboard.svg)"
            atomic_write(scenario_path, yaml.safe_dump(scenario, sort_keys=False, allow_unicode=True))

    def _publish_trials(self, package: MapPackage, section: str, design: dict[str, Any], trials: list[dict[str, Any]], *, held_out: bool) -> None:
        robotrace_root = Path(__file__).resolve().parents[1]
        summary = []
        for trial in trials:
            trial_root = package.path(section, "trials", f"{trial['track']}-{trial['seed']}")
            write_json(trial_root / "result.json", {key: value for key, value in trial.items() if key != "telemetry"})
            write_json(trial_root / "telemetry.json", trial.get("telemetry", []))
            trajectory_svg(trial, trial_root / "trajectory.svg")
            # An invalid design is evidence, not a crash: there is no robot to draw, so record the trial without a track view.
            track_view = None
            if trial.get("termination_reason") != "invalid_design":
                track_folder = "held-out" if held_out else ("anchor" if trial["track"] == "oval" else "development")
                track = json.loads((robotrace_root / "tracks" / track_folder / f"{trial['track']}.json").read_text())
                track_view_svg(trial, design, track, trial_root / "track-view.svg", experiment=self.race_id, condition=package.race["entrant"], iteration=-1 if held_out else int(section.rsplit("-", 1)[1]))
                track_view = str((trial_root / "track-view.svg").relative_to(package.root))
            summary.append({"track": trial["track"], "seed": trial["seed"], "score": trial["score"], "termination_reason": trial.get("termination_reason"), "error": trial.get("error"), "result": str((trial_root / "result.json").relative_to(package.root)), "telemetry": str((trial_root / "telemetry.json").relative_to(package.root)), "track_view": track_view})
        summary_svg(package.race["entrant"], "held-out" if held_out else section.rsplit("-", 1)[1], trials, package.path(section, "iteration-summary.svg"))
        write_json(package.path(section, "summary.json"), {"held_out": held_out, "invalid_trials": sum(1 for t in trials if t.get("termination_reason") == "invalid_design"), "total_trials": len(trials), "simulator_version": ADAPTER_VERSION, "trials": summary})
