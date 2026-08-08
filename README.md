# Highway Rush — Master Development Prompt

A complete, buildable specification for an endless arcade highway-driving game in the
Traffic Racer genre — written as a **prompt for an AI coding assistant**, not as a
wishlist.

> **[→ Start here: `PROMPT.md`](PROMPT.md)**

---

## What this is

Most "make me a game like X" prompts are lists of features. An AI coding agent given a
list of features produces a different game every session, because every unspecified
number is a decision the model re-makes from scratch.

This specification removes those decisions. It fixes the near-miss threshold at 1.20 m
and explains why. It gives the scoring formula, the traffic-density curve, the
suspension constants, the camera FOV at each speed, the XP curve, and the frame budget
per thread. Where a number could go either way, it says which way and what breaks
otherwise.

The result is a spec that converges: two sessions, two models, or two developers
working from it build recognizably the same game.

## How to use it

1. **Paste `PROMPT.md` into your coding assistant** as the opening instruction of a new
   project. It is self-contained. If your assistant reads `CLAUDE.md` automatically
   (Claude Code does), it will orient itself without being told.
2. **Work milestone by milestone** from `PROMPT.md` §20. Do not skip M1 or M4 — they
   are hard gates, and everything downstream depends on them.
3. **Point the assistant at `docs/` for depth.** `PROMPT.md` is the contract; `docs/` is
   the reference manual. Where a number appears in both, `docs/` wins.
4. **Use `docs/00-index.md` to navigate.** It maps every requirement to its spec
   section, its milestone, and the test that proves it — and §4 lists which numbers move
   together, which is the thing that bites hardest when tuning.
5. **Use `data/` as the content template.** Adding a car, mode, or environment should
   never require code — the schemas and `tools/validate_content.py` enforce that.

## Contents

| File | What's in it |
|---|---|
| **[`PROMPT.md`](PROMPT.md)** | The master prompt. 22 sections, self-contained, paste-ready |
| [`CLAUDE.md`](CLAUDE.md) | Agent orientation — read first if you are an AI assistant working here |
| [`docs/00-index.md`](docs/00-index.md) | **Traceability matrix**: every requirement → spec → milestone → test, plus coupled values and open questions |
| [`docs/01-game-design.md`](docs/01-game-design.md) | Design thesis, difficulty curves, near-miss math, progression cadence, anti-frustration rules |
| [`docs/02-technical-architecture.md`](docs/02-technical-architecture.md) | 22 modules, event bus, pooling, threading, save format, engine portability |
| [`docs/03-vehicle-physics.md`](docs/03-vehicle-physics.md) | Suspension, tire model, powertrain, aero, assists, per-class tuning tables, damage |
| [`docs/04-traffic-ai.md`](docs/04-traffic-ai.md) | 8 driver personalities, IDM following, the Near-Miss Contract, solvability solver, police AI |
| [`docs/05-road-generation.md`](docs/05-road-generation.md) | Chunk streaming, the grammar, floating origin, sightline constraint, materials |
| [`docs/06-graphics-art.md`](docs/06-graphics-art.md) | Art direction, quality tiers, the speed rig, 8 cameras, weather and time-of-day visuals |
| [`docs/07-audio.md`](docs/07-audio.md) | Multi-layer engine model, the near-miss whoosh, adaptive music, mixing, voice |
| [`docs/08-ui-ux.md`](docs/08-ui-ux.md) | Design language, screen map, HUD, garage, results, localization |
| [`docs/09-progression-economy.md`](docs/09-progression-economy.md) | Currencies, income model, pricing, upgrades, XP curve, missions, leaderboards |
| [`docs/10-data-schemas.md`](docs/10-data-schemas.md) | JSON schemas for every content type + validation lints |
| [`docs/11-optimization.md`](docs/11-optimization.md) | Frame budgets per thread, LOD, pooling, the hitch problem, memory ceilings |
| [`docs/12-roadmap.md`](docs/12-roadmap.md) | 18 milestones with acceptance criteria, schedule, risk register |
| [`docs/13-content-manifest.md`](docs/13-content-manifest.md) | 80 vehicles, 14 environments, 100 achievements, cosmetics, asset budgets |
| [`docs/14-testing-qa.md`](docs/14-testing-qa.md) | Test strategy, the full assertion register (~130 IDs), playtest protocol, bug severity |
| [`docs/15-networking-multiplayer.md`](docs/15-networking-multiplayer.md) | The four interfaces required from M0, replays, anti-cheat, convoys |
| [`docs/16-analytics-telemetry.md`](docs/16-analytics-telemetry.md) | Event schema, KPIs, and how live data corrects the balance model |
| [`docs/17-build-release.md`](docs/17-build-release.md) | Configurations, versioning, packaging, store, release checklist |
| [`docs/18-input-controls.md`](docs/18-input-controls.md) | Devices, steering model, analog curves, force feedback, latency budget |
| [`docs/19-engine-audio-reference.md`](docs/19-engine-audio-reference.md) | Engine order and firing-order acoustics, cross-plane vs flat-plane, per-family recording spec |
| [`docs/20-licensed-vehicle-roster.md`](docs/20-licensed-vehicle-roster.md) | Real-manufacturer roster (Suzuki, Honda, BMW, Mercedes, Porsche, Toyota, Ford, Dodge) and the licensing flag |
| [`docs/21-art-asset-delivery.md`](docs/21-art-asset-delivery.md) | The 96-model checklist, per-model delivery spec (sockets, LODs, pivots, collision), and sourcing guidance |
| [`data/`](data/) | Working example content files and their JSON Schemas |
| [`tools/validate_content.py`](tools/validate_content.py) | Dependency-free content validator, run by CI on every push |

## The five ideas that matter most

Everything else in this repo is detail. These five are the game:

1. **The near miss is the entire game.** Distance and speed are just delivery vehicles
   for near misses. Scoring is super-linear in proximity, speed, and combo — a ~180×
   spread between a lazy pass and a perfect one.

2. **The Near-Miss Contract.** Once the player's bumper passes a traffic vehicle's rear
   bumper, that vehicle loses lane-change and braking authority for 0.9 seconds. Without
   this rule the game feels cheap and players quit. With it, every death is legible.

3. **The solvability guarantee.** Every spawn wave must contain a threadable path,
   verified at spawn time. Difficulty comes from *narrow* gaps, never from *no* gaps.

4. **The speed rig.** Ten coupled effects — FOV, camera, blur, vignette, aberration,
   vibration, particles, audio filtering — driven by one normalized speed value.
   Perceived speed should exceed actual speed by ~15%.

5. **M1 is a hard gate.** If a grey box on an empty plane isn't fun to drive, no amount
   of content fixes it. Budget three weeks and spend all of them there.

## Scope note

This is a specification, not an implementation — there is no engine project here yet.
`PROMPT.md` §20 is the build order for producing one.

The suggested stack is Unreal Engine 5.6 + C++, but every number, curve, formula, and
rule in `docs/` is engine-independent. `docs/02` §9 maps the engine-specific concepts to
Unity 6 and Godot 4.4.

## Originality

Highway Rush is *inspired by* the Traffic Racer genre and is entirely original in code,
assets, and design. Reproducing any shipped game's assets is prohibited by
`PROMPT.md` §0, absolutely and in both modes.

Vehicle identity is a **build flag**. Every car ships with an invented marque
(`docs/13` §1) as its permanent fallback, plus an optional real-manufacturer identity
(`docs/20`). `HR_LICENSED_CONTENT` chooses which one presents; physics, class, price,
and progression are identical either way. With the flag off, no real manufacturer string
appears anywhere in the build — asserted by `T-LIC-02`. That makes shipping globally a
config change rather than a content re-do. Signage and place names stay invented in both
modes.
