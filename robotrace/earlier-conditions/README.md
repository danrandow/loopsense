# Earlier conditions

`robotrace-control/` and `robotrace-loopsense/` are the two single-package topology definitions
(with their own `runs/` output directories) that predate the map-driven controller and
`package-templates/` system — `robotrace-control` is the early evaluator–optimizer condition that
became `package-templates/opt-eval`, and `robotrace-loopsense` is the early producer–integrator
condition that became `package-templates/randow-maps`. They were last touched before the map-driven
cutover (commit `6dce5e980`) and are kept here as historical record, not as current templates or
race data — see `robotrace/package-templates/` and `robotrace/races/` for those.
