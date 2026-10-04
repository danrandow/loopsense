# Robot Race track-view SVG specification

## Purpose

`track-view.svg` is the canonical visual record of one trial. It must help an agent diagnose the robot–track interaction and let a spectator understand the result without opening telemetry. `result.json` and `telemetry.json` remain authoritative.

## Artifact and ownership

Each trial writes `entity2/trials/<track-id>-<seed>/track-view.svg`. The scenario that owns the trial must link directly to it. The iteration summary links to its constituent track views. An analysis is linked from the owning scenario's `map.notes`, never from Entity 2; earlier scenarios must never link forward to it.

The SVG must be standalone SVG 1.1 with no scripts, external styles, fonts, network assets, or `foreignObject`. It must render when served directly as `image/svg+xml`.

## Coordinate system

- Use recorded RobotTraceSim world coordinates.
- Preserve aspect ratio and fit the full track with at least one robot-length margin.
- Record the world bounds and world-to-view transform in metadata.
- Do not smooth or move recorded trajectory points or robot poses.

## Required layers

Use stable group IDs in this order:

1. `background`
2. `track-envelope`
3. `track-centreline`
4. `start-finish`
5. `trajectory`
6. `robot-snapshots`
7. `events`
8. `legend`
9. `trial-metadata`

### Track

Draw the exact trial track, real tape width, start, finish, and travel direction. Never substitute a generic illustration based on the track family name.

### Trajectory

Draw the recorded robot reference-point path. Colour segments by centre-line error using one fixed experiment-wide scale: green within 25% of allowed error, amber from 25–75%, red above 75%, and dark red outside the allowed envelope. Do not normalize colours per trial.

### Robot snapshots

Render the actual raced geometry at start; 25%, 50%, and 75% of achieved progress when reached; and finish or terminal position. Each snapshot shows:

- body envelope;
- left and right wheels;
- sensor positions and footprints;
- reference origin; and
- heading.

Geometry must pass through the same `to_robottrace_spec` translation used for simulation. Use transparency to manage overlap; never offset a snapshot from its recorded pose.

### Events

Mark line-loss onset, controller error, off-track point, timeout position, and finish crossing when present. Event metadata retains exact step references even if repeated events are visually clustered.

## Visible annotation

The header includes condition, iteration, track, seed, termination reason, score, progress, simulated elapsed time, and run ID. A legend explains track width, trajectory colours, robot snapshots, and event symbols. Text must not overlap the track.

## Embedded metadata

Include `<metadata id="robotrace-metadata">` containing escaped, key-sorted JSON with:

- schema version;
- experiment, condition, iteration, track, seed, and run IDs;
- adapter and simulator versions;
- hashes of package, track, result, and telemetry;
- termination reason and score;
- world bounds and view transform;
- snapshot step numbers; and
- event step numbers.

## Determinism and safety

Identical package, track, seed, telemetry, and renderer version must produce byte-identical SVG. Use fixed decimal precision and stable element ordering; omit timestamps. Escape all labels. Agent output must never become markup, a path, script, or URL.

## Accessibility

Provide `<title>` and `<desc>`. Use symbols and labels as well as colour for terminal states. Colours must remain distinguishable for common colour-vision deficiencies and in grayscale.

## Scenario integration

Entity 2 notes on each scenario must directly expose all artifacts relevant to that scenario:

- iteration summary;
- each trial track view, grouped as anchor, development, or held-out;
- result JSON and addressed measurement returns;
- experiment leaderboard; and
- race-outcome artifacts created in that scenario.

The iteration summary shows or links the anchor trial, best trial, and worst failure. A final scenario additionally exposes held-out views through Entity 2. Its race analysis is linked separately from `map.notes` because it interprets the whole scenario rather than only the race outcome.

## Acceptance tests

Tests must cover byte determinism; correct placement of track, trajectory, robot body, wheels, and sensors; geometry matching the raced package; all termination markers; fixed colour thresholds; required hashes and metadata; absence of active or external content; direct links from the owning scenario; and successful serving with SVG content type.
