#!/usr/bin/env python3
"""Simulator-as-a-tool learning probe (Phase 1, Gate-2 "matched-N_evals" arm, PHASE0_FREEZE.md §4a(i)).

tools/probe_step.py's --loop gives the model one proposal per iteration with a fixed evidence block: the
in-race harness's actual structure. This script instead gives the model direct tool-call access to the
simulator: it may call evaluate_design as many times as it likes, on whatever designs it likes, up to an
evaluation budget, then must call submit_design once. "One evaluation" is one design scored on the
development tracks over the same evidence-seed grid probe_step.py's --loop uses (seeds 1..--evidence-seeds),
so the three arms (this script's agent, a matched random hill-climb, a matched ES search) are all scored
on an identical unit and an identical seed grid, at the SAME N_evals -- the number of evaluate_design calls
the agent actually spent, not a number fixed in advance. This is what makes the comparison "matched effort"
rather than "matched iterations" (that is the separate, already-built comparison in probe_step.py --loop).

Run from the robotrace directory:
    python3 tools/probe_tool.py --dry-run --eval-budget 10 --runs 1                       # plumbing test, no key, no cost
    OPENROUTER_API_KEY=... python3 tools/probe_tool.py --model anthropic/claude-haiku-5.5 --eval-budget 25 --runs 1 --out phase1/arm_b_run1.json

The prompt states the goal, the contract and the budget only; it gives no design advice.
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
from types import SimpleNamespace
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from baseline_search import TEMPLATE, evaluate, load_config, load_tracks, mutate, starting_design  # noqa: E402
from orchestrator.executors import objective_for_prompt  # noqa: E402
from probe_step import evidence_for, evidence_mean, parse_design  # noqa: E402

SYSTEM = ("You are one member of a team designing a line-following robot. You have a tool, evaluate_design, that runs a candidate design in the "
          "simulator and reports how it did, aggregated over several seeds on the development tracks. Each call to evaluate_design uses one "
          "evaluation from your budget; calling it with an invalid design does not use an evaluation, it just returns the rejection reason. Call "
          "it as many times as you want, on as many different designs as you want, to explore and refine. When you are satisfied, or told your "
          "budget is used up, call submit_design exactly once with your final complete design. Every value must be a single concrete number or "
          "option inside the contract's limits.")


def eval_tool(contract: dict) -> dict:
    return {"type": "function", "function": {
        "name": "evaluate_design",
        "description": "Run a candidate design in the simulator on the development tracks (several seeds each) and return the aggregated result. "
                        "Uses one evaluation from your budget if the design is valid.",
        "parameters": {"type": "object", "properties": {"design": contract}, "required": ["design"]}}}


def submit_tool(contract: dict) -> dict:
    return {"type": "function", "function": {
        "name": "submit_design",
        "description": "Submit your final design. Call this exactly once, when you are done exploring or your evaluation budget is used up.",
        "parameters": {"type": "object", "properties": {"design": contract}, "required": ["design"]}}}


def call_with_tools(args, messages: list, tools: list, tool_choice) -> tuple[dict, int]:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    body = {"model": args.model, "messages": messages, "temperature": args.temperature, "max_tokens": args.max_tokens,
            "tools": tools, "tool_choice": tool_choice}
    if args.reasoning:
        body["reasoning"] = {"effort": args.reasoning}
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                  headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=args.timeout) as resp:
        data = json.loads(resp.read())
    if "error" in data:
        raise RuntimeError(f"OpenRouter error: {data['error']}")
    usage = data.get("usage", {})
    tokens = int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0))
    return data["choices"][0]["message"], tokens


def dry_run_step(rng: random.Random, start: dict, n_evals: int, budget: int, force_submit: bool) -> dict:
    name = "submit_design" if (force_submit or n_evals >= budget - 1) else rng.choice(["evaluate_design", "evaluate_design", "submit_design"])
    design = mutate(start, rng, "full")
    return {"role": "assistant", "content": None,
            "tool_calls": [{"id": f"dry{n_evals}", "type": "function", "function": {"name": name, "arguments": json.dumps({"design": design})}}]}


def validate_payload(payload: dict, contract: dict, bounds: dict) -> dict:
    return parse_design(payload, SimpleNamespace(contract=contract, bounds=bounds))


def run_agent(args, race, tracks, config, dev, seeds, contract, bounds, start, ev0, rng) -> dict:
    tools_full = [eval_tool(contract), submit_tool(contract)]
    task = {"task": "Design a line-following robot. Use the evaluate_design tool to try candidate designs before committing to a final one. Your "
                     "final design (submit_design) will be raced on development tracks and then, once, on unseen tracks of a different shape. "
                     "Higher total score is better.",
            "objective": objective_for_prompt(race), "authorized_output_contract": contract, "starting_design": start,
            "starting_design_evidence": {"trials_summary": ev0}, "evaluation_budget": args.eval_budget}
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(task, separators=(",", ":"))}]
    n_evals, tokens, turns, final_design = 0, 0, [], None
    max_turns = args.eval_budget + 10
    for turn in range(max_turns):
        force_submit = n_evals >= args.eval_budget
        active_tools = [submit_tool(contract)] if force_submit else tools_full
        tool_choice = {"type": "function", "function": {"name": "submit_design"}} if force_submit else "auto"
        if force_submit and turn > 0:
            messages.append({"role": "user", "content": "Your evaluation budget is used up. Call submit_design now with your final design."})
        if args.dry_run:
            msg, used = dry_run_step(rng, start, n_evals, args.eval_budget, force_submit), 0
        else:
            msg, used = call_with_tools(args, messages, active_tools, tool_choice)
        tokens += used
        messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        calls = msg.get("tool_calls") or []
        if not calls:
            try:
                content = (msg.get("content") or "").strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0]
                final_design = validate_payload(json.loads(content), contract, bounds)
                turns.append({"turn": turn, "type": "content_fallback", "ok": True})
            except Exception as exc:  # noqa: BLE001 - no tool call and unparsable content: record and stop, do not crash the replicate
                turns.append({"turn": turn, "type": "content_fallback", "ok": False, "error": str(exc)})
            break
        done = False
        for call in calls:
            name, call_id = call["function"]["name"], call["id"]
            try:
                raw = json.loads(call["function"]["arguments"])
                design = validate_payload(raw.get("design", raw), contract, bounds)
            except Exception as exc:  # noqa: BLE001 - malformed/out-of-contract tool call: fed back as feedback, not an evaluation, not a crash
                messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps({"error": f"rejected: {exc}"})})
                turns.append({"turn": turn, "tool": name, "ok": False, "error": str(exc)})
                continue
            if name == "evaluate_design":
                if n_evals >= args.eval_budget:
                    result = {"error": f"evaluation budget exhausted ({args.eval_budget}/{args.eval_budget} used); call submit_design now"}
                else:
                    n_evals += 1
                    ev = evidence_for(design, tracks, dev, seeds, config)
                    result = {"evaluations_used": n_evals, "evaluations_remaining": args.eval_budget - n_evals, "trials_summary": ev}
                turns.append({"turn": turn, "tool": name, "ok": "error" not in result, "n_evals": n_evals})
                messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps(result)})
            elif name == "submit_design":
                final_design = design
                turns.append({"turn": turn, "tool": name, "ok": True})
                messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps({"received": True})})
                done = True
            else:
                messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps({"error": "unknown tool"})})
                turns.append({"turn": turn, "tool": name, "ok": False, "error": "unknown tool"})
        if done:
            break
    return {"final_design": final_design, "n_evals": n_evals, "tokens": tokens, "turns": turns}


def random_hillclimb(start: dict, ev0: dict, tracks: dict, dev: list, seeds: list, config: dict, rng: random.Random, steps: int, space: str) -> dict:
    cur, cur_ev = start, ev0
    for _ in range(steps):
        cand = mutate(cur, rng, space)
        cand_ev = evidence_for(cand, tracks, dev, seeds, config)
        if evidence_mean(cand_ev) > evidence_mean(cur_ev):
            cur, cur_ev = cand, cand_ev
    return cur


# NOTE: baseline_search.py's "(1+1) ES" and probe_step.py's "random hill-climb" apply the identical update
# rule (mutate, evaluate, keep-if-better) -- the two names in PHASE0_FREEZE.md §3 differ only in SCALE (evals,
# train-seed count), not mechanism. At a matched, tiny N_evals there is no second algorithm to compare against;
# calling the same function twice under two labels would silently fabricate a second baseline that is not real.
# This function is kept distinctly named/called with an independent rng draw so the report below can show the
# matched-budget baseline's own run-to-run noise at this N (same purpose as PHASE0_FREEZE §3b's spread, not a
# second search method). See the Gate-2 report for this as a reported deviation from the "random/ES" framing.
def hillclimb_independent_draw(start: dict, tracks: dict, dev: list, seeds: list, config: dict, rng: random.Random, steps: int, space: str) -> dict:
    best, best_score = start, evaluate(start, tracks, dev, seeds, config)
    for _ in range(steps):
        cand = mutate(best, rng, space)
        sc = evaluate(cand, tracks, dev, seeds, config)
        if sc["mean"] > best_score["mean"]:
            best, best_score = cand, sc
    return best


# ES ceiling (full-space search, large --evals) on fresh dev-track seeds, frozen in PHASE0_FREEZE.md §3a.
# Used only for the non-gating "headroom closed" supplementary number (§4a(ii)); not recomputed per run.
ES_CEILING_HEADROOM = 253.6


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", help="OpenRouter model id")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--reasoning", choices=["low", "medium", "high"])
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true", help="stand-in agent that evaluates random mutations then submits: tests plumbing, costs nothing")
    ap.add_argument("--eval-budget", type=int, default=25, help="max evaluate_design calls the agent may spend")
    ap.add_argument("--space", choices=["controller", "full"], default="full", help="random/ES baselines' mutation space")
    ap.add_argument("--start", help="JSON file holding the starting design (default: the iteration-0 style design)")
    ap.add_argument("--evidence-seeds", type=int, default=20, help="dev-seed grid size for evaluate_design and the matched baselines")
    ap.add_argument("--fresh-seeds", type=int, default=30, help="held-out validation seeds for final scoring, never shown to the agent")
    ap.add_argument("--runs", type=int, default=1, help="independent replicates")
    ap.add_argument("--rng", type=int, default=1, help="seeds the matched baselines' mutation randomness (paired across replicates in one invocation)")
    ap.add_argument("--out", help="write every replicate's result here as JSON")
    args = ap.parse_args()
    if not (args.dry_run or args.model):
        ap.error("give --model, or --dry-run")

    config, tracks = load_config(), load_tracks()
    race = config["_race"]
    contract = json.loads((TEMPLATE / "entities" / "entityPub0" / "contract.schema.json").read_text())
    bounds = config["design_bounds"]
    dev = list(race["evaluation"]["development_tracks"])
    seeds = list(range(1, args.evidence_seeds + 1))
    fresh = list(range(5000, 5000 + args.fresh_seeds))
    rng = random.Random(args.rng)

    start = starting_design(args.start)
    base = evaluate(start, tracks, dev, fresh, config)
    ev0 = evidence_for(start, tracks, dev, seeds, config)
    print(f"start design on {len(fresh)} fresh seeds x {len(dev)} dev tracks: mean {base['mean']:.0f}")

    def score(design: dict) -> float:
        return evaluate(design, tracks, dev, fresh, config)["mean"] - base["mean"]

    label = "dry-run stub" if args.dry_run else args.model
    replicates, began = [], time.time()
    for run in range(args.runs):
        t0 = time.time()
        result = run_agent(args, race, tracks, config, dev, seeds, contract, bounds, start, ev0, rng)
        agent_gain = score(result["final_design"]) if result["final_design"] is not None else None
        n = result["n_evals"]
        # Two independent draws of the SAME matched-budget hill-climb algorithm (see note above
        # hillclimb_independent_draw) -- not two different search methods. Both use random_hillclimb's rule;
        # draw 2 is kept as a separate call for the noise check, not a distinct "ES" baseline.
        draw1_final = random_hillclimb(start, ev0, tracks, dev, seeds, config, random.Random(args.rng * 1000 + run), n, args.space)
        draw2_final = hillclimb_independent_draw(start, tracks, dev, seeds, config, random.Random(args.rng * 2000 + run), n, args.space)
        draw1_gain, draw2_gain = score(draw1_final), score(draw2_final)
        headroom_closed = None if agent_gain is None or ES_CEILING_HEADROOM == 0 else agent_gain / ES_CEILING_HEADROOM
        rec = {"run": run, "n_evals": n, "tokens": result["tokens"], "wall_s": round(time.time() - t0, 1),
               "agent_gain": agent_gain, "matched_hillclimb_draw1_gain": draw1_gain, "matched_hillclimb_draw2_gain": draw2_gain,
               "headroom_closed": headroom_closed, "agent_turns": result["turns"], "final_design": result["final_design"]}
        replicates.append(rec)
        ag = "invalid" if agent_gain is None else f"{agent_gain:+.1f}"
        print(f"run {run + 1}/{args.runs} [{label}] N_evals={n} tokens={result['tokens']} | agent {ag} | "
              f"matched hill-climb draw1 {draw1_gain:+.1f} | draw2 {draw2_gain:+.1f}", flush=True)
        if args.out:
            Path(args.out).write_text(json.dumps({"model": label, "eval_budget": args.eval_budget, "replicates": replicates}, indent=1))
    valid = [r for r in replicates if r["agent_gain"] is not None]
    print(f"\n{len(valid)}/{len(replicates)} replicates produced a valid final design. Total wall time {time.time() - began:.0f}s.")
    if valid:
        print(f"mean N_evals {statistics.mean(r['n_evals'] for r in valid):.1f} | mean tokens {statistics.mean(r['tokens'] for r in valid):.0f}")
        print(f"mean agent gain {statistics.mean(r['agent_gain'] for r in valid):+.1f} | "
              f"mean matched hill-climb draw1 {statistics.mean(r['matched_hillclimb_draw1_gain'] for r in valid):+.1f} | "
              f"draw2 {statistics.mean(r['matched_hillclimb_draw2_gain'] for r in valid):+.1f}")
        beat1 = sum(r["agent_gain"] - r["matched_hillclimb_draw1_gain"] > 10 for r in valid)
        beat2 = sum(r["agent_gain"] - r["matched_hillclimb_draw2_gain"] > 10 for r in valid)
        print(f"agent beat matched hill-climb by >10 in {beat1}/{len(valid)} (draw1), {beat2}/{len(valid)} (draw2)")
        print("NOTE: baseline_search.py's ES and probe_step.py's random hill-climb are the same update rule "
              "(see hillclimb_independent_draw docstring) -- at this matched, small N there is only one free "
              "baseline, not two; both draws above are that one algorithm, reported for the noise check.")


if __name__ == "__main__":
    main()
