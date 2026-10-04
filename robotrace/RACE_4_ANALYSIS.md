# Race 4 recorded-run analysis

Race 4 is the first preregistered run using the pinned native RobotTraceSim adapter. It completed five iterations for each condition with valid hashes, no repair calls, no failed harness events, and no held-out-context leakage.

## Result

The optimizer–evaluator control produced the stronger recorded trajectory, but neither condition solved the development task. All forty development trials ended off-track or timed out. The comparison is therefore between degrees of failure, not between reliable finishers.

| Measure | LoopSense | Control |
|---|---:|---:|
| Iteration 0 score | 139.252 | 58.742 |
| Best development score | 139.252 | 162.190 |
| Final development score | 68.948 | 84.144 |
| Final held-out score | 67.404 | 113.774 |
| Tokens used | 15,221 | 16,708 |
| Mechanical repairs | 0 | 0 |

LoopSense began 80.509 points ahead, then finished 15.196 points behind. Control improved by 25.401 points from its first to final iteration and reached its best score at iteration 2. LoopSense declined by 70.304 points from its first to final iteration and never exceeded its starting score. Control also led on the held-out hairpin by 46.370 points.

## Adaptation trajectory

| Iteration | LoopSense | Control | Control minus LoopSense |
|---:|---:|---:|---:|
| 0 | 139.252 | 58.742 | -80.509 |
| 1 | 67.805 | 130.374 | 62.569 |
| 2 | 105.612 | 162.190 | 56.578 |
| 3 | 83.494 | 136.982 | 53.489 |
| 4 | 68.948 | 84.144 | 15.196 |

The control explored materially different sensor spreads and derivative gains. LoopSense changed its initial 0.16 m sensor spread to 0.14 m, then kept the same controller—base speed 1.0 and PID gains 10/0.5/2.0—for the remaining iterations. Its integration feedback repeatedly asked for sensor repositioning and controller tuning, but those requests did not produce substantive controller adaptation.

The control alternated sensor spreads between 0.08 m and 0.12 m and changed derivative gain between 3.0, 4.0, and 3.5 while retaining base speed 1.2. That exploration improved its progress-based score through iteration 2, although it did not yield completion.

## Token efficiency

Both conditions stayed well below the equal 50,000-token caps. LoopSense used 15,221 tokens and control used 16,708. From first to final iteration, LoopSense changed by -46.19 points per 10,000 tokens used; control changed by +15.20 points per 10,000 tokens used. These ratios describe this one run only and are sensitive to the failing-design regime.

## Interpretation

Race 4 does not support the claim that the LoopSense topology adapted faster or better under this setup. The control achieved the higher best, final, and held-out scores and showed more substantive design variation. However, the absence of any completed development trial limits the strength of that conclusion. The scoring function distinguished partial progress and robustness among failures, so the result does not establish that either topology learned a viable line-following policy.

The most important LoopSense failure was not lack of feedback. The Integrator repeatedly identified sensor placement, line loss, oscillation, and controller tuning as issues. The failure was conversion of that feedback into coordinated changes: geometry moved only slightly and controller parameters remained fixed. This suggests a specific next hypothesis—that the working agreement needs an explicit response-to-feedback obligation and a controlled-change convention—rather than a general prompt expansion.

## Race 5 recommendation

Keep the simulator, score, tracks, seeds, model, topology, and control condition unchanged. Change only the LoopSense starter working agreement to require both agents to:

1. name the previous measurement or feedback item they are responding to;
2. make at least one bounded, testable change when the prior build failed;
3. preserve other variables where possible so the effect is attributable; and
4. record why a requested change was accepted, deferred, or rejected.

Race 5 must receive its own preregistration. Race 4 artifacts and conclusions must remain unchanged.

## Integrity record

- Frozen implementation commit: `e198655402af7f163f6a4128b5fa404f834f2aa2`
- Frozen tag: `robotrace-recorded-v1`
- Result objects verified: 10 of 10
- Context manifests checked: 31; forbidden context keys found: 0
- Audit events: 126; failed-run events: 0
- Leaderboard hash: verified
