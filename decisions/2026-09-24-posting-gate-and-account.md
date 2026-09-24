# Posting gate for the evidence run; posting account confirmed

## Context

Two owner-only decisions stalled the iteration-1 experiment (GTM `entityR3-v1`, `entity3-v1`): whether the evidence run may proceed below the Medium-confidence posting gate, and which account is cleared for posting — the "account handle unconfirmed" flag carried in iteration-1 files was stale (`@loopsense` is live).

## Decision

Dan decided on 2026-09-24: (a) the evidence run may proceed at Low-Medium confidence — it need not wait for Medium; (b) `@loopsense` is confirmed as the posting account and the stale handle flag is cleared.

## Why

The evidence and counter-evidence thresholds in the bet both assume the loop has run (`agents/pm/generates/entity0-v1.md`); waiting for Medium confidence while the run is itself the confidence-raising evidence is circular. `@loopsense` is live and already in use (`agents/gtm/knowledge/gtm-v0.md`, `agents/gtm/generates/entity3-v1.md`).

## Consequences

The gate's normal Medium requirement stands for other original posts; this decision is scoped to the evidence run. The State & inputs block in `iteration-2.yaml` records both decisions. Out of date: the account-handle blocker as carried in iteration-1 files (frozen), and any reading that the gate blocks the evidence run.

Rule 8 check: `@loopsense` is the project's own account (factual, documented in `agents/gtm/knowledge/gtm-v0.md`); no third-party personal information, neutral tone. Result: pass.
