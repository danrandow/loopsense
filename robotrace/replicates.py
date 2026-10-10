"""Replicate races and a learning comparison across them.

    python3 replicates.py run  --base race-40 --n 3 --provider openrouter --model openai/gpt-4.1-mini
    python3 replicates.py compare race-40-a race-40-b race-40-c
    python3 replicates.py compare --base race-40

Each replicate gets its own development seed (so the teams' histories, and so their trajectories, can diverge) and the SAME
held-out seeds, so held-out scores are comparable across replicates. Both teams in a replicate share everything else.
Set RANDOW_MAPS_ROOT (canonical validator) and, for openrouter, OPENROUTER_API_KEY before `run`.
"""
from __future__ import annotations

import argparse
import json
import statistics
import string
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEV_SEEDS = [17, 29, 41, 53, 67, 79, 83, 97]
HELD_OUT_SEEDS = [101, 102, 103, 104, 105]
ENTRANTS = ("randow-maps", "opt-eval")


def run(args: argparse.Namespace) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from orchestrator.race_service import MapDrivenRaceService

    if args.n > len(DEV_SEEDS):
        raise SystemExit(f"at most {len(DEV_SEEDS)} replicates")
    for index in range(args.n):
        race_id = f"{args.base}-{string.ascii_lowercase[index]}"
        settings = {"iterations": args.iterations, "provider": args.provider, "model_id": args.model, "max_output_tokens": args.max_output_tokens, "max_action_runs": 6,
                    "total_tokens_per_condition": args.total_tokens, "max_tokens_per_iteration": args.iteration_tokens,
                    "seeds": [DEV_SEEDS[index]], "held_out_seeds": HELD_OUT_SEEDS}
        service = MapDrivenRaceService(race_id, args.workspace)
        service.prepare()
        service.configure_common(settings)
        for entrant in ENTRANTS:
            service.review(entrant)
        service.freeze()
        print(f"{race_id}: dev seed {DEV_SEEDS[index]}, held-out seeds {HELD_OUT_SEEDS} — running", flush=True)
        print(service.run(), flush=True)
    compare(argparse.Namespace(races=[], base=args.base, workspace=args.workspace, out=None))


def _iteration_scores(package: Path) -> list[float | None]:
    """Mean development score of each iteration; None where the iteration was not raced."""
    config = json.loads(json.dumps(__import__("yaml").safe_load((package / "config" / "race.yaml").read_text())))
    scores: list[float | None] = []
    for iteration in range(int(config["iterations"])):
        summary = package / f"iteration-{iteration}" / "summary.json"
        if summary.is_file():
            trials = json.loads(summary.read_text())["trials"]
            scores.append(sum(float(t["score"]) for t in trials) / max(1, len(trials)))
        else:
            scores.append(None)
    return scores


def _slope(scores: list[float | None]) -> float | None:
    points = [(i, s) for i, s in enumerate(scores) if s is not None]
    if len(points) < 2:
        return None
    mean_x, mean_y = statistics.fmean(p[0] for p in points), statistics.fmean(p[1] for p in points)
    spread = sum((x - mean_x) ** 2 for x, _ in points)
    return sum((x - mean_x) * (y - mean_y) for x, y in points) / spread


def summarise(race_id: str, workspace: Path) -> dict[str, dict[str, Any]]:
    board = json.loads((workspace / f"{race_id}-leaderboard.json").read_text())
    out = {}
    for result in board["results"]:
        package = Path(result["package"]).name
        scores = _iteration_scores(workspace / package)
        raced = [s for s in scores if s is not None]
        charged = 0  # the budget ledger is cumulative and counts rejected attempts, so it is the figure charged against the allowance
        for ledger in sorted((workspace / package).glob("iteration-*/budget-ledger.json"), key=lambda path: int(path.parent.name.split("-")[1])):
            charged = max(charged, int(json.loads(ledger.read_text()).get("total_tokens", 0)))
        out[result["entrant"]] = {
            "held_out": float(result["score"]), "scores": scores, "raced": len(raced), "best": max(raced) if raced else None,
            "first": raced[0] if raced else None, "last": raced[-1] if raced else None, "slope": _slope(scores),
            "delivered": not result.get("incomplete", False), "charged": charged,
        }
    return out


def _fmt(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def compare(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace)
    races = list(args.races) or sorted(path.name.removesuffix("-leaderboard.json") for path in workspace.glob(f"{args.base}-*-leaderboard.json"))
    if not races:
        raise SystemExit("no races found")
    data = {race: summarise(race, workspace) for race in races}
    lines = ["# Replicate comparison", "", f"Races: {', '.join(races)}", "",
             "Development score per iteration is the mean over development tracks and seeds; — means the iteration was not raced. "
             "Slope is the least-squares change in development score per iteration over the raced iterations. "
             "Learning shows as a positive slope, last above first, and a best that arrives late; held-out is the mean over every held-out track and seed.", ""]
    for entrant in ENTRANTS:
        lines += [f"## {entrant}", "", "| Race | Dev score by iteration | Raced | First → last | Best | Slope/iter | Held-out | Delivered | Tokens charged |", "|---|---|---:|---|---:|---:|---:|:-:|---:|"]
        rows = [(race, data[race][entrant]) for race in races if entrant in data[race]]
        for race, row in rows:
            lines.append(f"| {race} | {' · '.join(_fmt(s) for s in row['scores'])} | {row['raced']}/{len(row['scores'])} | {_fmt(row['first'])} → {_fmt(row['last'])} | {_fmt(row['best'])} | {_fmt(row['slope'])} | {_fmt(row['held_out'])} | {'yes' if row['delivered'] else 'no'} | {row['charged']} |")
        if len(rows) > 1:
            def mean(key: str) -> float | None:
                values = [r[key] for _, r in rows if r[key] is not None]
                return statistics.fmean(values) if values else None
            spread = statistics.stdev([r["held_out"] for _, r in rows])
            lines.append(f"| **mean (n={len(rows)})** | | {statistics.fmean(r['raced'] for _, r in rows):.1f} | {_fmt(mean('first'))} → {_fmt(mean('last'))} | {_fmt(mean('best'))} | {_fmt(mean('slope'))} | {_fmt(mean('held_out'))} (sd {spread:.1f}) | {sum(r['delivered'] for _, r in rows)}/{len(rows)} | {_fmt(mean('charged'), 0)} |")
        lines.append("")
    text = "\n".join(lines)
    print(text)
    out = Path(args.out) if args.out else (workspace / f"{args.base}-replicates.md" if args.base else None)
    if out:
        out.write_text(text + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="run N replicate races, then compare")
    r.add_argument("--base", required=True, help="race id prefix; replicates are <base>-a, <base>-b, ...")
    r.add_argument("--n", type=int, default=3)
    r.add_argument("--iterations", type=int, default=6)
    r.add_argument("--provider", default="mock")
    r.add_argument("--model", default="deterministic-mock-v1")
    r.add_argument("--max-output-tokens", type=int, default=4000)
    r.add_argument("--total-tokens", type=int, default=1_000_000)
    r.add_argument("--iteration-tokens", type=int, default=160_000)
    r.add_argument("--workspace", type=Path, default=ROOT)
    r.set_defaults(func=run)
    c = sub.add_parser("compare", help="compare finished races")
    c.add_argument("races", nargs="*")
    c.add_argument("--base", default="")
    c.add_argument("--workspace", type=Path, default=ROOT)
    c.add_argument("--out")
    c.set_defaults(func=compare)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
