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

### Specification — coverage pass

A line-by-line audit against the original brief found six items with no home in the
spec. Five were added; one is a deliberate deviation.

| Item | Resolution |
|---|---|
| Engine swaps | Added as `docs/09` §4.1 — a full powertrain replacement with its own mass and centre-of-mass penalty, distinct from Engine upgrade tiers |
| Difficulty setting | Added to `docs/08` §7 as a preset that writes visibly to individual assist and tolerance settings, never a hidden multiplier |
| EQS | Added to the stack in `PROMPT.md` §19, scoped to police positioning queries only |
| Wheel wobble | Added to the new animation checklist, `docs/06` §9, tied to the damage system |
| Driver entering | Added to the same checklist as the first-unlock garage reveal |
| Project tracking | GitHub Projects added to the stack, milestones mirroring §20 |
| **Ragdoll debris** | **Deliberately not implemented for people.** Vehicle debris only — no pedestrians exist in the game and none are struck. This keeps the ESRB E10+ / PEGI 7 target in `PROMPT.md` §1. Stated explicitly in `docs/03` §8.3 |

### Specification — completeness pass

An audit for what an implementer would still lack found that the spec asserted CI
enforcement in 13 places with no CI, required an M0 networking interface it never
defined, and scattered ~130 test assertions across 13 documents with no unified plan.

**Added:**

| Addition | Why it was needed |
|---|---|
| `CLAUDE.md` | The repo's entire purpose is to be handed to an AI assistant, and it had no orientation file. Covers precedence rules, the eight non-negotiables, the two hard gates, and the six known trip-ups |
| `docs/00-index.md` | Traceability matrix: every requirement → spec → milestone → test. Plus §3 (single source of truth per number), §4 (coupled values — change one, check the others), and §5 (open questions with defaults) |
| `docs/14-testing-qa.md` | Collects ~130 assertions into a register with IDs, assigns each a level, and adds the manual playtest protocol — including logging whether each death was self-blamed or game-blamed, the highest-signal data in the project |
| `docs/15-networking-multiplayer.md` | Defines the four M0 interfaces with null implementations, the replay format (~4 KB/min, seed + input trace), server-side replay validation as anti-cheat, and the convoy design that replicates 4 transforms instead of all traffic |
| `docs/16-analytics-telemetry.md` | Consent posture, event schema, KPIs, and §4 — how live data corrects the balance model, with an explicit line between what may be tuned live and what may never be |
| `docs/17-build-release.md` | Configurations, versioning (including the separate save-schema and simulation-version axes), packaging, store requirements, and the full release checklist |
| `docs/18-input-controls.md` | Control is pillar #6 and had the thinnest deep-dive. Steering lock table per speed, analog response curves, force feedback as a physics readout, and the latency budget stage by stage |
| `.github/workflows/validate.yml` | Makes the CI claims real: content lints, JSON Schema validation, and a cross-reference check that fails on any broken `docs/` link |
| `.gitignore`, `LICENSE` | Standard hygiene; the license notes that nothing here grants rights to any third-party game or marque |

**Two design points worth recording, both of which fell out of writing the new docs:**

- Server-side replay validation is what makes the human-readable save format safe. A
  score must be *reproducible from inputs*, so editing a save cannot forge one — which
  is also why determinism is an architectural requirement rather than a nicety.
- Convoys replicate four player transforms, not traffic. Identical seeds produce
  identical traffic on every client, so bandwidth stays under 8 KB/s per player.

### Specification — forward-only motion, signalling, and engine acoustics

Four requested features, one of which needed a design guard to avoid breaking the game.

**Forward-only motion** (`docs/05` §0). The player vehicle never travels backward. This
is a simplification that pays for itself: the chunk index becomes monotonic, streaming
becomes a ring buffer rather than a bidirectional window, passed chunks are freed
permanently, and memory is bounded regardless of run length. Consequential removals:
reverse gear dropped from all vehicles and from the schema, the brake binding is no
longer "brake / reverse", and the `Backwards` hidden achievement — drive 500 m in
reverse — was now impossible and has been replaced. Spin recovery (§0.1) handles the one
case forward-only motion cannot: a player spun to face backward with no way to turn
round.

**Indicators as a fairness system** (`docs/04` §3.6). Blinkers were previously a line
inside the lane-change behaviour. They are now specified with the same guarantee as
brake lights — visible to 500 m at every quality tier, surviving every LOD transition,
with emissive boosted 40% in Snow and Fog. Signal timing is per-personality, and the
54% of traffic that signals reliably is deliberately sized so the player learns to trust
the cue without the road feeling sterile.

**The Courtesy Flash** (`docs/04` §3.7). Flashing high beams asks the nearest car ahead
to move over, with per-personality yield rates and per-environment modifiers — highest
on the European Motorway, where keep-right is a legal duty, lowest in Cyberpunk City.

This mechanic could have ruined the game. If flashing cleared the road for free, the
optimal strategy becomes "flash constantly," traffic stops being an obstacle, and the
near miss — the entire point — evaporates. Four rules prevent it, and the first is
load-bearing: **a yielded pass scores no near miss.** The flash is a safety valve that
costs points, never a scoring strategy. It also costs over 200 m of road at 300 km/h,
degrades on repeat use, and cannot manufacture a gap, so the solvability guarantee is
untouched in both directions.

**Engine audio reference** (`docs/19`, new). Web research into engine acoustics and
game audio practice, written up as the physics behind the 15 families:

- Engine order (`cylinders / 2` for a four-stroke) and the resulting fundamental
  frequency at every rpm, tabulated per configuration. Getting this wrong makes an
  engine sound like a different engine no matter how good the samples are.
- Cross-plane vs flat-plane V8 — uneven versus even exhaust pulse spacing per bank, and
  therefore low-frequency burble versus high-frequency scream. Kestrel is cross-plane
  only; Aurel and Axiom are flat-plane. A player must be able to tell them apart blind.
- Per-family character notes, the crossfade-versus-granular decision with a deferral
  point at M7, recording specification, and the class→family assignment.

**On real cars:** the research surfaced specific production vehicles, and this document
deliberately captures their *physics* rather than their badges. Firing orders and
harmonic content are engineering facts; marque names, body shapes, and recordings of a
specific car are property. Using real vehicles is a licensing decision, not a technical
one — the architecture supports it since `engineBank` is just a data field, but nothing
here assumes it and the spec ships legally clean without it.

---

## Milestone log

Record each milestone from `PROMPT.md` §20 here on completion, with its acceptance
criteria and the measured result.

| Milestone | Completed | Acceptance criteria result |
|---|---|---|
| M0 Project setup | — | — |
| M1 Drive a box | — | — |
