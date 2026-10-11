#!/usr/bin/env python3
"""One-step learning probe: given a fixed starting design and the same per-track summary evidence the agents see,
can a model propose a better design than chance does?

Three arms, all scored identically on FRESH seeds the model never saw:
  random   N random mutations of the starting design (free, no key needed)  <- the bar a model must clear
  model    N independent model proposals (OpenRouter), prompted with the contract, the scoring and the evidence
  (--dry-run replaces the model with a stub that returns a mutated design, to test the plumbing at no cost)

Run from the robotrace directory:
    python3 tools/probe_step.py --random-only                                     # free; shows the bar
    python3 tools/probe_step.py --dry-run --samples 4                             # plumbing test, no key
    OPENROUTER_API_KEY=... python3 tools/probe_step.py --model openai/gpt-4.1-mini --samples 20
    OPENROUTER_API_KEY=... python3 tools/probe_step.py --model anthropic/claude-sonnet-5.5 --reasoning medium --samples 20

Two diagnostic flags:
  --no-evidence   same prompt without the evidence block. If gains look the same, the model is not using the evidence.
  --two-step      shows TWO raced designs (A = start, B = a random mutation of A) with the evidence for each and asks for the
                  best design. Tests whether the model can keep the better attempt (accept / revert), which learning across
                  iterations needs. Also prints what a trivial 'pick the higher evidence score' rule would have got.

  --history K     the learning test. Shows K raced designs (the start plus K-1 variants, each changing one or two things) with the
                  evidence for each, and asks for a design better than all of them. Scored against the best design in the history
                  on fresh seeds, versus randomly mutating the best-by-evidence design. To win the model must work out which
                  changes helped and extrapolate, which no fixed selection rule does.

  --loop N        THE LEARNING TEST. One model does the whole job alone for N iterations: it proposes a design, the design is raced
                  (free), the model sees its own designs and results, proposes the next, and so on. Every design is the model's
                  own. Each iteration's design is scored on fresh seeds. --runs R repeats it R times independently.
                  --no-results is the control: the model sees its previous designs but NOT how they scored.
                  A free random hill-climb (mutate the best-by-evidence design) with the same number of steps is the baseline.
  --candidates K  with --loop: each iteration the model proposes K designs, all are raced, and it sees every result. The random baseline
                  mutates its best-by-evidence design K times per step and keeps the best on evidence.

Reading the result: compare "mean gain" and "% improved" across arms. Gain = proposal's mean score minus the start
design's mean score on the same fresh seeds, over the three development tracks. An invalid proposal (out of contract
after one repair attempt) counts as a failed sample, not as zero gain.
The prompt states the goal and the rules only; it gives no design advice.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from jsonschema import Draft202012Validator
except ImportError:  # older jsonschema
    from jsonschema import Draft7Validator as Draft202012Validator  # noqa: E402

from baseline_search import TEMPLATE, evaluate, load_config, load_tracks, mutate, starting_design  # noqa: E402
from orchestrator.evidence import summarise_trials  # noqa: E402
from orchestrator.executors import objective_for_prompt  # noqa: E402
from orchestrator.validators import validate_controller, validate_geometry  # noqa: E402
from simulator.adapter.headless import run_trial  # noqa: E402

SYSTEM = ("You are one member of a team designing a line-following robot. Return one JSON object that is the complete new design and matches the "
          "supplied design contract exactly. Use only the information supplied. Every value must be a single concrete number or option inside the contract's limits.")


def evidence_for(design: dict, tracks: dict, names: list[str], seeds: list[int], config: dict) -> dict:
    trials = [run_trial(design, tracks[n], s, config) for n in names for s in seeds]
    return {"n_trials": len(trials), "per_track": summarise_trials(trials),
            "note": "Aggregated over all trials (several seeds per track). Per-step telemetry is not included."}


def build_prompt(race: dict, contract: dict, design: dict, evidence: dict | None) -> str:
    body = {
        "task": "Produce a new design for the robot. Your design will be raced on development tracks and then, once, on unseen tracks of a different shape. "
                "Higher total score is better.",
        "objective": objective_for_prompt(race),
        "authorized_output_contract": contract,
        "current_design": design,
    }
    if evidence is not None:
        body["evidence_for_current_design"] = {"trials_summary": evidence}
    return json.dumps(body, separators=(",", ":"))


def build_pair_prompt(race: dict, contract: dict, a: dict, ev_a: dict, b: dict, ev_b: dict) -> str:
    return json.dumps({
        "task": "Two designs have been raced on the development tracks. Produce the design you expect to score highest. Your design will be raced on "
                "development tracks and then, once, on unseen tracks of a different shape. Higher total score is better.",
        "objective": objective_for_prompt(race),
        "authorized_output_contract": contract,
        "attempts": [{"name": "A", "design": a, "evidence": {"trials_summary": ev_a}}, {"name": "B", "design": b, "evidence": {"trials_summary": ev_b}}],
    }, separators=(",", ":"))


def groups_changed(a: dict, b: dict) -> int:
    ga, gb, ca, cb = a["geometry"], b["geometry"], a["controller"], b["controller"]
    n = sum(ga[k] != gb[k] for k in ("mass", "wheel_radius", "wheel_track", "sensor_size"))
    n += (ga["body_width"], ga["body_length"]) != (gb["body_width"], gb["body_length"])
    n += ga["sensor_positions"] != gb["sensor_positions"]
    n += sum(ca[k] != cb[k] for k in ("base_speed", "kp", "ki", "kd", "line_loss"))
    n += (ca["sensor_weights"] != cb["sensor_weights"]) and ga["sensor_positions"] == gb["sensor_positions"]
    return n


def few_change_variant(start: dict, rng: random.Random) -> dict:
    for _ in range(200):
        cand = mutate(start, rng, "full")
        if 1 <= groups_changed(start, cand) <= 2:
            return cand
    return mutate(start, rng, "full")


def build_history_prompt(race: dict, contract: dict, attempts: list[tuple[dict, dict]]) -> str:
    return json.dumps({
        "task": "Several designs have been raced on the development tracks. Produce a new design that you expect to score higher than any of them. "
                "Your design will be raced on development tracks and then, once, on unseen tracks of a different shape. Higher total score is better.",
        "objective": objective_for_prompt(race),
        "authorized_output_contract": contract,
        "attempts": [{"name": chr(65 + i), "design": d, "evidence": {"trials_summary": ev}} for i, (d, ev) in enumerate(attempts)],
    }, separators=(",", ":"))


def build_loop_prompt(race: dict, contract: dict, attempts: list[tuple[dict, dict]], iteration: int, total: int, show_results: bool) -> str:
    rows = []
    for i, (design, ev) in enumerate(attempts):
        row = {"iteration": i, "design": design}
        if show_results:
            row["evidence"] = {"trials_summary": ev}
        rows.append(row)
    return json.dumps({
        "task": "You are designing a line-following robot over several iterations. Your previous designs are listed"
                + (" with how each one raced" if show_results else "") + ". Produce the design for the next iteration. "
                "Your final design will be raced once on unseen tracks of a different shape. Higher total score is better.",
        "iteration": iteration, "iterations_in_total": total,
        "objective": objective_for_prompt(race),
        "authorized_output_contract": contract,
        "previous_iterations": rows,
    }, separators=(",", ":"))


def evidence_mean(ev: dict) -> float:
    scores = [t["mean_score"] for t in ev["per_track"].values()]
    return sum(scores) / len(scores)


def distance(x: dict, y: dict) -> float:
    def flat(d):
        g, c = d["geometry"], d["controller"]
        v = [g[k] for k in ("mass", "wheel_radius", "wheel_track", "body_width", "body_length", "sensor_size")]
        v += [len(g["sensor_positions"]), max(abs(p["x"]) for p in g["sensor_positions"]), c["base_speed"], c["kp"], c["ki"], c["kd"]]
        return v
    return sum(abs(p - q) / (abs(p) + abs(q) + 1e-9) for p, q in zip(flat(x), flat(y))) + (x["controller"]["line_loss"] != y["controller"]["line_loss"])


def call_model(args, prompt: str) -> tuple[dict | None, str, int]:
    """Return (design or None, error, tokens). One repair attempt, as in the race harness."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    tokens, error = 0, ""
    for attempt in range(2):
        body = {"model": args.model, "messages": messages, "temperature": args.temperature, "max_tokens": args.max_tokens,
                "response_format": {"type": "json_object"}}
        if args.reasoning:
            body["reasoning"] = {"effort": args.reasoning}
        req = Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=args.timeout) as resp:
                data = json.loads(resp.read())
        except (TimeoutError, OSError, ValueError) as exc:  # a stalled or dropped call is one failed sample, not a crash
            return None, f"request failed: {type(exc).__name__}: {exc}", tokens
        usage = data.get("usage", {})
        tokens += int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0))
        content = ""
        try:
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            return parse_design(json.loads(content), args), "", tokens
        except Exception as exc:  # noqa: BLE001 - any parse/validation failure triggers the single repair attempt
            error = str(exc)
            messages = messages + [{"role": "assistant", "content": content or "(empty)"},
                                   {"role": "user", "content": f"That design was rejected: {error}. Return the corrected complete design as one JSON object."}]
    return None, error, tokens


def parse_design(payload: dict, args) -> dict:
    # Accept the design bare or wrapped under one key ("design").
    if "geometry" not in payload and len(payload) == 1 and isinstance(next(iter(payload.values())), dict):
        payload = next(iter(payload.values()))
    errors = sorted(Draft202012Validator(args.contract).iter_errors(payload), key=lambda e: list(e.path))
    if errors:
        raise ValueError(f"contract violation: {errors[0].message}")
    validate_geometry(payload["geometry"], args.bounds)
    validate_controller(payload["controller"], len(payload["geometry"]["sensor_positions"]), args.bounds)
    return {k: payload[k] for k in ("geometry", "controller", "observation_request")}


def summarize(label: str, gains: list[float], invalid: int, extra: str = "") -> None:
    n = len(gains) + invalid
    if not gains:
        print(f"{label:34s} no valid proposals out of {n}{extra}")
        return
    improved = sum(g > 0 for g in gains)
    print(f"{label:34s} valid {len(gains)}/{n} | mean gain {statistics.mean(gains):+6.1f} | median {statistics.median(gains):+6.1f} | "
          f"improved {improved}/{len(gains)} ({improved / len(gains):.0%}) | best {max(gains):+6.1f} | worst {min(gains):+6.1f}{extra}")


def run_loop(args, race, tracks, config, dev, fresh, start, rng, score) -> None:
    seeds = list(range(1, args.evidence_seeds + 1))
    n = args.loop
    ev0 = evidence_for(start, tracks, dev, seeds, config)
    label = "dry-run stub" if args.dry_run else (args.model or "(baseline only)")
    if args.no_results:
        label += " (no results shown)"
    model_runs, base_runs, invalid, tokens, dump = [], [], 0, 0, []

    def table(name: str, runs: list[list[float | None]]) -> None:
        print(f"\n{name}: gain over the start design on fresh seeds, per iteration (mean of {len(runs)} runs; best-so-far in brackets)")
        for it in range(n + 1):
            vals = [r[it] for r in runs if r[it] is not None]
            best = [max(x for x in r[: it + 1] if x is not None) for r in runs]
            print(f"  iteration {it}: {statistics.mean(vals):+7.1f}   [{statistics.mean(best):+7.1f}]" if vals else f"  iteration {it}:   n/a")
        final = [r[-1] for r in runs if r[-1] is not None]
        best_final = [max(x for x in r if x is not None) for r in runs]
        print(f"  last iteration per run: {[round(x) for x in final]} | best-so-far per run: {[round(x) for x in best_final]}")

    for run in range(args.runs):
        # free baseline: random hill-climb, selecting on the same evidence the model sees
        cur, cur_ev = start, ev0
        traj = [0.0]
        for _ in range(n):
            cand = mutate(cur, rng, args.space)
            cand_ev = evidence_for(cand, tracks, dev, seeds, config)
            if evidence_mean(cand_ev) > evidence_mean(cur_ev):
                cur, cur_ev = cand, cand_ev
            traj.append(score(cur))
        base_runs.append(traj)
        print(f"run {run + 1} random hill-climb: {[round(x) for x in traj]}", flush=True)
        if args.random_only:
            continue
        attempts = [(start, ev0)]
        traj = [0.0]
        for it in range(1, n + 1):
            prompt = build_loop_prompt(race, args.contract, attempts, it, n, not args.no_results)
            if args.dry_run:
                best_i = max(range(len(attempts)), key=lambda i: evidence_mean(attempts[i][1]))
                design, error, used = mutate(attempts[best_i][0], rng, "full"), "", 0
            else:
                design, error, used = call_model(args, prompt)
            tokens += used
            if design is None:
                invalid += 1
                traj.append(None)
                print(f"   iteration {it}: invalid ({error[:80]})", flush=True)
                continue
            attempts.append((design, evidence_for(design, tracks, dev, seeds, config)))
            g = score(design)
            traj.append(g)
            print(f"   iteration {it}: gain {g:+7.1f}", flush=True)
        model_runs.append(traj)
        dump.append({"gains": traj, "designs": [d for d, _ in attempts]})
        print(f"run {run + 1} {label}: {[None if x is None else round(x) for x in traj]}", flush=True)
        if args.out:
            Path(args.out).write_text(json.dumps({"model": label, "loop": n, "runs": dump, "random_hill_climb": base_runs, "invalid": invalid, "tokens": tokens}, indent=1))
    table("random hill-climb (free baseline)", base_runs)
    if model_runs:
        table(label, model_runs)
        print(f"\ninvalid proposals: {invalid} | tokens {tokens}")
        print("Learning = the model's gain trends up over iterations and ends above the random hill-climb. Compare with the --no-results run of the same model.")


SYSTEM_K = ('You are one member of a team designing a line-following robot. Return one JSON object of the form {"candidates": [design, design, ...]} where each '
            'design is a complete new design matching the supplied design contract exactly. Use only the information supplied. Every value must be a '
            "single concrete number or option inside the contract's limits.")


def build_loop_prompt_k(race: dict, contract: dict, history: list, iteration: int, total: int, k: int, show_results: bool) -> str:
    rows = []
    for i, group in enumerate(history):
        for j, (design, ev) in enumerate(group):
            row = {"iteration": i, "candidate": j, "design": design}
            if show_results:
                row["evidence"] = {"trials_summary": ev}
            rows.append(row)
    return json.dumps({
        "task": "You are designing a line-following robot over several iterations. Each iteration you propose " + str(k) + " candidate designs. Every candidate is raced"
                + (" and you see how each one raced" if show_results else "") + ". All earlier candidates are listed. Produce the " + str(k)
                + ' candidates for the next iteration as {"candidates": [design, ...]}. Your final design will be raced once on unseen tracks of a different shape. '
                "Higher total score is better.",
        "iteration": iteration, "iterations_in_total": total, "candidates_per_iteration": k,
        "objective": objective_for_prompt(race),
        "authorized_output_contract": contract,
        "previous_candidates": rows,
    }, separators=(",", ":"))


def call_model_k(args, prompt: str, k: int) -> tuple[list, str, int]:
    """Return (valid designs, error, tokens). One repair attempt when no candidate is valid."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    messages = [{"role": "system", "content": SYSTEM_K}, {"role": "user", "content": prompt}]
    tokens, error = 0, ""
    for attempt in range(2):
        body = {"model": args.model, "messages": messages, "temperature": args.temperature, "max_tokens": args.max_tokens,
                "response_format": {"type": "json_object"}}
        if args.reasoning:
            body["reasoning"] = {"effort": args.reasoning}
        req = Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=args.timeout) as resp:
                data = json.loads(resp.read())
        except (TimeoutError, OSError, ValueError) as exc:
            return [], f"request failed: {type(exc).__name__}: {exc}", tokens
        usage = data.get("usage", {})
        tokens += int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0))
        content = ""
        try:
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            payload = json.loads(content)
            items = payload.get("candidates") if isinstance(payload, dict) else payload
            if not isinstance(items, list) or not items:
                raise ValueError('expected {"candidates": [design, ...]}')
            designs, errs = [], []
            for item in items[:k]:
                try:
                    designs.append(parse_design(item, args))
                except Exception as exc:  # noqa: BLE001
                    errs.append(str(exc))
            if designs:
                return designs, (errs[0] if errs else ""), tokens
            raise ValueError(errs[0] if errs else "no valid candidates")
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            messages = messages + [{"role": "assistant", "content": content or "(empty)"},
                                   {"role": "user", "content": f'That was rejected: {error}. Return the corrected object with {k} complete designs as {{"candidates": [...]}}.'}]
    return [], error, tokens


def run_loop_k(args, race, tracks, config, dev, fresh, start, rng, score) -> None:
    seeds = list(range(1, args.evidence_seeds + 1))
    n, k = args.loop, args.candidates
    ev0 = evidence_for(start, tracks, dev, seeds, config)
    label = "dry-run stub" if args.dry_run else (args.model or "(baseline only)")
    label += f" K={k}" + (" (no results shown)" if args.no_results else "")
    metrics = ("mean of K", "best-by-evidence of K", "best-so-far by evidence")
    model_runs, base_runs, dump, invalid, tokens = [], [], [], 0, 0

    def table(name: str, runs: list) -> None:
        print(f"\n{name}: fresh-seed gain over the start design, mean of {len(runs)} runs")
        print("  iter | " + " | ".join(f"{m:>24s}" for m in metrics))
        for it in range(n + 1):
            cells = []
            for m in metrics:
                vals = [r[m][it] for r in runs if r[m][it] is not None]
                cells.append(f"{statistics.mean(vals):+24.1f}" if vals else f"{'n/a':>24s}")
            print(f"  {it:4d} | " + " | ".join(cells))
        for m in metrics:
            final = [r[m][-1] for r in runs if r[m][-1] is not None]
            if final:
                print(f"  last iteration, {m}: {[round(x) for x in final]}  mean {statistics.mean(final):+.1f}")

    for run in range(args.runs):
        # free baseline: K random mutations of the best-by-evidence design per step, keep the best on evidence
        cur, cur_ev, cur_g = start, ev0, 0.0
        traj = {m: [0.0] for m in metrics}
        for _ in range(n):
            scored = []
            for _k in range(k):
                cand = mutate(cur, rng, args.space)
                scored.append((cand, evidence_for(cand, tracks, dev, seeds, config)))
            gains = [score(d) for d, _ in scored]
            j = max(range(k), key=lambda i: evidence_mean(scored[i][1]))
            if evidence_mean(scored[j][1]) > evidence_mean(cur_ev):
                cur, cur_ev, cur_g = scored[j][0], scored[j][1], gains[j]
            traj["mean of K"].append(statistics.mean(gains))
            traj["best-by-evidence of K"].append(gains[j])
            traj["best-so-far by evidence"].append(cur_g)
        base_runs.append(traj)
        print(f"run {run + 1} random best-of-{k} hill-climb, best-so-far: {[round(x) for x in traj['best-so-far by evidence']]}", flush=True)
        if args.random_only:
            continue
        history = [[(start, ev0)]]
        best_d, best_ev, best_g = start, ev0, 0.0
        cand_gains = []  # per-candidate fresh-seed gain and evidence mean, aligned with history[1:]
        traj = {m: [0.0] for m in metrics}
        for it in range(1, n + 1):
            prompt = build_loop_prompt_k(race, args.contract, history, it, n, k, not args.no_results)
            if args.dry_run:
                designs, error, used = [mutate(best_d, rng, "full") for _ in range(k)], "", 0
            else:
                designs, error, used = call_model_k(args, prompt, k)
            tokens += used
            invalid += k - len(designs)
            if not designs:
                traj["mean of K"].append(None)
                traj["best-by-evidence of K"].append(None)
                traj["best-so-far by evidence"].append(best_g)
                print(f"   iteration {it}: no valid candidates ({error[:80]})", flush=True)
                continue
            scored = [(d, evidence_for(d, tracks, dev, seeds, config)) for d in designs]
            history.append(scored)
            gains = [score(d) for d, _ in scored]
            cand_gains.append({"gains": [round(x, 2) for x in gains], "evidence_means": [round(evidence_mean(ev), 2) for _, ev in scored]})
            j = max(range(len(scored)), key=lambda i: evidence_mean(scored[i][1]))
            if evidence_mean(scored[j][1]) > evidence_mean(best_ev):
                best_d, best_ev, best_g = scored[j][0], scored[j][1], gains[j]
            traj["mean of K"].append(statistics.mean(gains))
            traj["best-by-evidence of K"].append(gains[j])
            traj["best-so-far by evidence"].append(best_g)
            print(f"   iteration {it}: {len(designs)} valid | gains {[round(x) for x in gains]} | best-so-far {best_g:+.0f}", flush=True)
        model_runs.append(traj)
        dump.append({"gains": traj, "candidates_per_iteration": [[d for d, _ in grp] for grp in history], "candidate_gains": cand_gains})
        print(f"run {run + 1} {label}, best-so-far: {[round(x) for x in traj['best-so-far by evidence']]}", flush=True)
        if args.out:
            Path(args.out).write_text(json.dumps({"model": label, "loop": n, "candidates": k, "runs": dump, "random": base_runs,
                                                  "invalid": invalid, "tokens": tokens}, indent=1))
    table(f"random best-of-{k} hill-climb (free baseline)", base_runs)
    if model_runs:
        table(label, model_runs)
        print(f"\ninvalid candidates: {invalid} | tokens {tokens}")
        print("Compare 'best-so-far by evidence' (what a harness would deliver) and 'mean of K' (proposal quality) with the random baseline and the --no-results run.")


def run_history(args, race, tracks, config, dev, fresh, start, rng, score, results) -> None:
    model_gains, rand_gains, rule_gains, invalid, tokens, errors, proposals = [], [], [], 0, 0, [], []
    label = "dry-run stub" if args.dry_run else (args.model or "(no model: baselines only)")
    seeds = list(range(1, args.evidence_seeds + 1))
    for h in range(args.histories):
        designs = [start] + [few_change_variant(start, rng) for _ in range(args.history - 1)]
        attempts = [(d, evidence_for(d, tracks, dev, seeds, config)) for d in designs]
        fresh_gain = [0.0] + [score(d) for d in designs[1:]]
        top = max(fresh_gain)
        by_evidence = max(range(len(attempts)), key=lambda i: evidence_mean(attempts[i][1]))
        rule_gains.append(fresh_gain[by_evidence] - top)
        helped = sum(g > 0 for g in fresh_gain[1:])
        print(f"history {h + 1}: variants' fresh gains {[round(g) for g in fresh_gain[1:]]} (best {top:+.0f}); evidence rule picks #{by_evidence} ({fresh_gain[by_evidence] - top:+.0f} vs best)", flush=True)
        for _ in range(args.per_history):
            rand_gains.append(score(mutate(designs[by_evidence], rng, args.space)) - top)
        if args.random_only:
            continue
        prompt = build_history_prompt(race, args.contract, attempts)
        for _ in range(args.per_history):
            if args.dry_run:
                design, error, used = mutate(designs[by_evidence], rng, "full"), "", 0
            else:
                design, error, used = call_model(args, prompt)
            tokens += used
            if design is None:
                invalid += 1
                errors.append(error)
                continue
            g = score(design) - top
            model_gains.append(g)
            proposals.append({"history": h, "gain_vs_best": g, "design": design})
            print(f"   proposal: {g:+6.1f} vs best-in-history", flush=True)
    print(f"\nGain over the BEST design in each history, on fresh seeds (0 = merely matched the best):")
    summarize("evidence rule picks one of them", rule_gains, 0)
    summarize("random mutation of the best", rand_gains, 0)
    if not args.random_only:
        summarize(label, model_gains, invalid, f" | tokens {tokens}")
        beat = sum(g > 0 for g in model_gains)
        print(f"\nmodel beat the best-in-history in {beat}/{len(model_gains)} proposals; random did in {sum(g > 0 for g in rand_gains)}/{len(rand_gains)}")
        for e in sorted(set(errors))[:3]:
            print(f"  invalid: {e}")
        if args.out:
            Path(args.out).write_text(json.dumps({"model": label, "proposals": proposals, "random": rand_gains, "rule": rule_gains, "errors": errors}, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="OpenRouter model id")
    ap.add_argument("--samples", type=int, default=20, help="proposals per arm")
    ap.add_argument("--temperature", type=float, default=0.7, help="0 would repeat one answer; the race harness uses 0")
    ap.add_argument("--reasoning", choices=["low", "medium", "high"], help="send OpenRouter's reasoning.effort (the race harness never does)")
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--random-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="stand-in 'model' that returns a mutated design: tests plumbing, costs nothing")
    ap.add_argument("--space", choices=["controller", "full"], default="full", help="random arm's mutation space")
    ap.add_argument("--start", help="JSON file holding the starting design (default: the iteration-0 style design)")
    ap.add_argument("--evidence-seeds", type=int, default=20)
    ap.add_argument("--fresh-seeds", type=int, default=30)
    ap.add_argument("--rng", type=int, default=1)
    ap.add_argument("--history", type=int, default=0, help="learning test: show this many raced designs (start + variants) and ask for a better one")
    ap.add_argument("--histories", type=int, default=5, help="with --history: number of different histories")
    ap.add_argument("--per-history", type=int, default=4, help="with --history: proposals per history")
    ap.add_argument("--loop", type=int, default=0, help="THE LEARNING TEST: iterations a single model designs, sees results, and iterates")
    ap.add_argument("--runs", type=int, default=3, help="with --loop: independent repeats")
    ap.add_argument("--candidates", type=int, default=1, help="with --loop: designs proposed and raced per iteration (K); the model sees every result. 1 = the original loop")
    ap.add_argument("--no-results", action="store_true", help="with --loop: show previous designs but not how they raced (control)")
    ap.add_argument("--no-evidence", action="store_true", help="omit the evidence block from the prompt")
    ap.add_argument("--two-step", action="store_true", help="show two raced designs (A=start, B=random mutation) and ask for the best")
    ap.add_argument("--out", help="write every proposal and score here as JSON")
    args = ap.parse_args()
    if not (args.random_only or args.dry_run or args.model):
        ap.error("give --model, or --random-only, or --dry-run")

    config, tracks = load_config(), load_tracks()
    race = config["_race"]
    args.contract = json.loads((TEMPLATE / "entities" / "entityPub0" / "contract.schema.json").read_text())
    args.bounds = config["design_bounds"]
    dev = list(race["evaluation"]["development_tracks"])
    fresh = list(range(5000, 5000 + args.fresh_seeds))
    rng = random.Random(args.rng)

    start = starting_design(args.start)
    base = evaluate(start, tracks, dev, fresh, config)
    print(f"start design on {len(fresh)} fresh seeds x {len(dev)} dev tracks: mean {base['mean']:.0f}")
    evidence = evidence_for(start, tracks, dev, list(range(1, args.evidence_seeds + 1)), config)
    prompt = build_prompt(race, args.contract, start, None if args.no_evidence else evidence)
    print(f"prompt size ~{len(prompt) // 3} tokens\n")
    results: dict[str, list] = {}

    def score(design: dict) -> float:
        return evaluate(design, tracks, dev, fresh, config)["mean"] - base["mean"]

    if args.loop and args.candidates > 1:
        run_loop_k(args, race, tracks, config, dev, fresh, start, rng, score)
        return
    if args.loop:
        run_loop(args, race, tracks, config, dev, fresh, start, rng, score)
        return
    if args.history:
        run_history(args, race, tracks, config, dev, fresh, start, rng, score, results)
        return

    # Arm 1: random mutation (one step from the start design)
    gains = [score(mutate(start, rng, args.space)) for _ in range(args.samples)]
    results["random"] = gains
    summarize(f"random mutation ({args.space})", gains, 0)

    # Arm 2: the model
    if not args.random_only:
        label = "dry-run stub" if args.dry_run else args.model + (f" reasoning={args.reasoning}" if args.reasoning else "")
        gains, invalid, tokens, errors, proposals = [], 0, 0, [], []
        began = time.time()
        pair_rows = []
        for i in range(args.samples):
            this_prompt, b, ev_b, g_b = prompt, None, None, None
            if args.two_step:
                b = mutate(start, rng, "full")
                ev_b = evidence_for(b, tracks, dev, list(range(1, args.evidence_seeds + 1)), config)
                g_b = score(b)
                this_prompt = build_pair_prompt(race, args.contract, start, evidence, b, ev_b)
            if args.dry_run:
                design, error, used = (rng.choice([start, b]) if b else mutate(start, rng, "full")), "", 0
            else:
                design, error, used = call_model(args, this_prompt)
            tokens += used
            if design is None:
                invalid += 1
                errors.append(error)
                continue
            g = score(design)
            gains.append(g)
            proposals.append({"gain": g, "design": design, **({"b_gain": g_b, "b": b} if b else {})})
            if b:
                picked = "A" if distance(design, start) <= distance(design, b) else "B"
                pair_rows.append({"g": g, "g_b": g_b, "picked": picked, "rule": "B" if evidence_mean(ev_b) > evidence_mean(evidence) else "A"})
                print(f"  sample {i + 1:2d}: gain {g:+6.1f} | B is {g_b:+6.1f} | model kept {picked}", flush=True)
            else:
                print(f"  sample {i + 1:2d}: gain {g:+6.1f}", flush=True)
        results["model"] = gains
        summarize(label, gains, invalid, f" | tokens {tokens} | {time.time() - began:.0f}s")
        for e in sorted(set(errors))[:3]:
            print(f"  invalid: {e}")
        if pair_rows:
            best = [max(0.0, r["g_b"]) for r in pair_rows]
            rule = [r["g_b"] if r["rule"] == "B" else 0.0 for r in pair_rows]
            clear = [r for r in pair_rows if abs(r["g_b"]) > 50]
            ok = sum((r["picked"] == "B") == (r["g_b"] > 0) for r in clear)
            print(f"\ntwo-step: B was better than A in {sum(r['g_b'] > 0 for r in pair_rows)}/{len(pair_rows)} pairs")
            print(f"  always keep A            : mean gain {0.0:+6.1f}")
            print(f"  model's output           : mean gain {statistics.mean(gains):+6.1f}")
            print(f"  pick higher evidence mean: mean gain {statistics.mean(rule):+6.1f}   <- free selector on the same evidence")
            print(f"  oracle (best of A,B)     : mean gain {statistics.mean(best):+6.1f}")
            print(f"  kept the truly better design in {ok}/{len(clear)} clear-cut pairs (|B gain| > 50)")
        if args.out:
            Path(args.out).write_text(json.dumps({"model": label, "proposals": proposals, "errors": errors, "random": results["random"]}, indent=1))
    print("\nA model only shows it can use the evidence if its mean gain and % improved are clearly above the random arm's.")


if __name__ == "__main__":
    main()
