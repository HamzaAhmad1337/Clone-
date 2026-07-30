# Changelog

`PROMPT.md` §0 requires that every completed milestone records its acceptance-criteria
results here. Until implementation begins, this file tracks the specification itself.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Specification — initial

- `PROMPT.md` — the 22-section master prompt: product definition, pillars, core loop,
  controls, physics, road, traffic, scoring, modes, police, environments, graphics,
  vehicles, economy, audio, UI, performance, accessibility, architecture, milestones,
  definition of done, and the final playtest.
- `docs/01`–`docs/13` — full reference specifications.
- `data/` — one working example per content type, plus the vehicle JSON Schema.
- `tools/validate_content.py` — dependency-free content validator.

### Specification — consistency pass

A full cross-document audit was run after the first draft. Corrections applied:

| Area | Problem | Fix |
|---|---|---|
| Scoring | Score and coins were two unrelated systems; the results-screen example reconciled at no conversion rate | Unified: score is the only driving award, `coins = score × 0.30`, stated once in `PROMPT.md` §8.3 |
| Scoring | Near-miss worked examples used `proximityMul` values that did not match the formula | Recomputed all four rows; the worst-to-best spread is ~180×, not 200× |
| Progression | XP curve `180·n^1.42` summed to 4.1 M against a stated 42-hour target — the real figure was ~520 hours | Replaced with `300 + 5·n^1.7`, total ~482 k, verified against measured XP/hour |
| Progression | Coins/hour column did not equal coins/run × runs/hour for any row | Rebuilt the table with explicit overhead and runs/hour |
| Combo | `×N` meant the combo count in some places and the multiplier in others | One display convention, stated in `PROMPT.md` §8.2 and applied everywhere |
| Traffic | `minGapWidth` of 1.55 m was narrower than the player's car | Renamed `minGapClearance` and defined as spare room beside the car, not the total opening |
| Traffic | Traffic pool of 90 was below the Rush Hour worst case | Derived the real peak (~92) and raised the pool to 120 |
| Graphics | Low-tier traffic draw distance (250 m) was shorter than the spawn distance (up to 420 m), so cars would pop in | Floored all tiers at 450 m; traffic inside the sightline requirement always renders |
| Graphics | Speed-rig table values disagreed with the curves directly above them | Normalized `s` to `speed/300` and recomputed the 150 km/h column |
| Physics | Steering-lock prose quoted the 340 km/h figure as if it were the 300 km/h one | Corrected to 12.4° at 300 km/h, 9.5° from 340 up |
| Road | "385 km/h reaches 231 km in 10 minutes" — it reaches 64 km | Corrected, and restated the float-precision figures per magnitude |
| Road | Chunk archetype weights summed to 106% | Rebalanced to 100% and gave every archetype an explicit max-consecutive run |
| Data | Downforce expressed as a negative lift coefficient | Renamed to `downforceCoefficient*`, positive, with the schema rejecting negatives |
| Data | Example torque curve implied 257 kW against the Sports class figure of 300 kW | Curve corrected to 300 kW at 7,000 rpm; the validator now enforces the agreement |
| Data | `oncomingLaneCoinsPerSecond` awarded coins directly, bypassing the score conversion | Renamed to `oncomingLanePointsPerSecond` |
| Architecture | "Modules (20)" preceded a list of 22 | Corrected |
| Audio | Combo chime mapped 20 combo steps onto 12 pitches | One pitch per step |
| Roadmap | Phase durations summed to 76 weeks against a stated total of 64 | Both figures now shown, with the overlap made explicit |
| Balance | Asserted near-miss share of 55–75% against a design that produces ~94% | Assertion widened to 70–95%, matching the design thesis |

---

## Milestone log

Record each milestone from `PROMPT.md` §20 here on completion, with its acceptance
criteria and the measured result.

| Milestone | Completed | Acceptance criteria result |
|---|---|---|
| M0 Project setup | — | — |
| M1 Drive a box | — | — |
