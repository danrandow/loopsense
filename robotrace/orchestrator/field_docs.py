"""User-facing documentation for race settings, shown in the web UI.

Single source of truth: the setup form labels and the /docs page both render from FIELD_DOCS,
and a test requires every form setting to have an entry.
"""
from __future__ import annotations

import html

SPEC = "/robotrace/MAP_DRIVEN_ARCHITECTURE_SPEC.md"

# key -> label, scope (where the value applies), summary (one line), details (paragraph).
FIELD_DOCS: dict[str, dict[str, str]] = {
    "race_id": {
        "label": "Race ID",
        "scope": "Whole race",
        "summary": "Names the race and its folders, e.g. race-13.",
        "details": "Each race gets its own packages (one per entrant), pair record, report and leaderboard. A failed race cannot be resumed; retire it and prepare a fresh ID.",
        "see": "",
    },
    "iterations": {
        "label": "Iterations per entrant",
        "scope": "Per entrant, whole race",
        "summary": "How many rounds each entrant plays.",
        "details": "Every iteration starts from the previous iteration's carried-forward state, runs the entrant's workflow, then races one selected robot. Action-run and per-iteration token limits reset at the start of each iteration.",
        "see": "",
    },
    "provider": {
        "label": "Model provider",
        "scope": "Whole race",
        "summary": "Where model calls go: the offline mock or OpenRouter.",
        "details": "Both entrants use the same provider and model so the comparison is about topology, not model.",
        "see": "",
    },
    "model_id": {
        "label": "Model ID",
        "scope": "Whole race",
        "summary": "The model both entrants call.",
        "details": "Use the 'Previously used' picker to reuse an earlier provider and model pair. The model is frozen with the race.",
        "see": "",
    },
    "api_key": {
        "label": "API key",
        "scope": "This server session",
        "summary": "Credential for the provider.",
        "details": "Held in memory only and never written to a package or manifest. Needed when you press Run, not when you prepare.",
        "see": "",
    },
    "total_tokens_per_condition": {
        "label": "Total token budget per entrant",
        "scope": "Per entrant, across all iterations",
        "summary": "Cumulative cap on input plus output tokens over the whole race.",
        "details": "Summed across every iteration of that entrant. Once it is used up no further model action starts, and a response that would overshoot it fails the run. Each entrant has its own allowance; both get the same figure.",
        "see": "§5.6 race.yaml",
    },
    "max_tokens_per_iteration": {
        "label": "Token budget per iteration",
        "scope": "Per entrant, per iteration",
        "summary": "Cap on input plus output tokens within a single iteration.",
        "details": "Counted from that iteration's event log, so it resets each iteration. It is checked together with the total budget; whichever is tighter wins.",
        "see": "§5.6 race.yaml",
    },
    "max_action_runs": {
        "label": "Maximum action runs per iteration",
        "scope": "Per entrant, per iteration",
        "summary": "Cap on how many actions the controller may invoke in one iteration.",
        "details": (
            "An action run is one invocation of an action in the entrant's workflow, whether a model call or a deterministic step. "
            "The count starts at zero each iteration. If the iteration's completion entities are still missing when the count reaches the cap, "
            "the iteration fails with 'action-run budget exhausted' and the race cannot be resumed. "
            "The value is set once in race.yaml (budget.max_action_runs) but enforced separately for each iteration and each entrant. "
            "It is independent of the token budgets. Re-entry (an action running again because its inputs changed) uses extra runs, so leave headroom above the number of actions on the workflow's shortest path."
        ),
        "see": "§5.7 Scenario YAML",
    },
    "max_output_tokens": {
        "label": "Maximum output tokens per call",
        "scope": "Per model call",
        "summary": "Upper limit on tokens the model may generate in one call.",
        "details": "Passed to the provider as max_tokens, reduced further if the remaining token budget is smaller. Too low a value truncates the model's JSON artifact.",
        "see": "",
    },
}

GLOSSARY: dict[str, str] = {
    "Action": "A step in an entrant's workflow, such as proposing or evaluating a design. It reads some entities and may write others.",
    "Action run": "One invocation of an action by the controller. Counted against the per-iteration action-run cap.",
    "Entity": "A versioned piece of state (a design, feedback, a result). Writing a new version can make other actions eligible to run.",
    "Entrant": "A competing team: Randow Maps or Opt/Eval. Budgets apply to each entrant separately.",
    "Iteration": "One round: run the entrant's workflow until its completion entities exist, then race the selected robot.",
    "Budget ledger": "budget-ledger.json in each iteration folder: the live count of action runs and tokens against their maximums.",
}


def help_html(key: str) -> str:
    """Inline expandable help for a form field; works without JavaScript."""
    doc = FIELD_DOCS[key]
    see = f' <a href="/docs#{html.escape(key)}">Full reference</a>'
    return (
        f'<details class="help"><summary aria-label="About {html.escape(doc["label"])}">?</summary>'
        f'<div><p><strong>{html.escape(doc["summary"])}</strong></p>'
        f'<p>{html.escape(doc["details"])}</p>'
        f'<p class="muted">Applies to: {html.escape(doc["scope"])}.{see}</p></div></details>'
    )


def docs_page_body() -> str:
    rows = []
    for key, doc in FIELD_DOCS.items():
        spec = f' · <a href="{SPEC}">Spec {html.escape(doc["see"])}</a>' if doc["see"] else ""
        rows.append(
            f'<section id="{html.escape(key)}"><h3>{html.escape(doc["label"])} <code>{html.escape(key)}</code></h3>'
            f'<p><strong>{html.escape(doc["summary"])}</strong></p><p>{html.escape(doc["details"])}</p>'
            f'<p class="muted">Applies to: {html.escape(doc["scope"])}{spec}</p></section>'
        )
    terms = "".join(f"<tr><th>{html.escape(t)}</th><td>{html.escape(d)}</td></tr>" for t, d in GLOSSARY.items())
    return (
        '<h1>Race settings reference</h1><p><a href="/">Back to race setup</a> · '
        f'<a href="{SPEC}">Full architecture spec</a></p>'
        f'<section><h2>Glossary</h2><table>{terms}</table></section>'
        f'<h2>Settings</h2>{"".join(rows)}'
    )
