# Working in this repository

This repo is a **specification**, not an implementation. Its purpose is to be handed to
an AI coding assistant that will build the game described in `PROMPT.md`.

Read this file first, then `PROMPT.md`, then the `docs/` file relevant to your task.

---

## What you are looking at

| | |
|---|---|
| **Product** | Highway Rush — an endless arcade highway-driving game for PC |
| **State** | Specification complete. No engine project exists yet |
| **Canonical spec** | `PROMPT.md` — 22 sections, self-contained |
| **Reference manual** | `docs/00`–`docs/20` |
| **Content templates** | `data/` — one working example per type |
| **Build order** | `PROMPT.md` §20, milestones M0–M18 |

**Precedence when two documents disagree:** `docs/` wins over `PROMPT.md`, and `data/`
wins over both for any value that appears in a content file. Report the contradiction
rather than silently picking one.

---

## The rules that are not negotiable

These are load-bearing. Violating any of them breaks the game in a way that is
expensive to discover later.

1. **Originality — with a licensed-content exception.** Nothing may be copied,
   decompiled, or derived from any shipped game. Every invented marque in `docs/13` §1
   is original and is always present as the fallback identity.
   **Real manufacturers are supported through the marque-mapping layer in `docs/20`**,
   behind the `HR_LICENSED_CONTENT` build flag. Physics, class, price, and progression
   are identical in both identities — only the name and mesh differ. With the flag off,
   no real manufacturer string may appear anywhere in the build (`T-LIC-02`). Never
   hardcode a real marque into content; always use the `licensed` block.
2. **The Near-Miss Contract** (`docs/04` §4). Once the player's bumper passes a traffic
   vehicle's rear bumper, that vehicle loses lane-change and hard-brake authority for
   0.9 s. Without it the game feels cheap and players quit.
3. **The solvability guarantee** (`docs/04` §6). Every spawn wave must contain a
   threadable path, verified at spawn time. Difficulty comes from narrow gaps, never
   from no gaps.
4. **Determinism.** All gameplay randomness draws from the seeded PRNG owned by
   `GameManager`. Never call unseeded random in gameplay code. Daily Challenges, ghost
   replays, and leaderboard validation all depend on this.
5. **No hitches.** A single 40 ms spike at 280 km/h moves the car 3.1 m without input.
   It is a ship-blocking bug, not a performance nit. See `docs/11` §4.
6. **Data-driven content.** Adding a car, mode, environment, weather state, mission, or
   modifier must require **zero code changes**. If your change would break that, the
   design is wrong — stop and say so.
7. **No pay-to-win.** Premium currency buys cosmetics only. Never stats, never payout
   rates, never unlock speed.
8. **Score is the only driving award.** Coins are a single 30% conversion of score
   (`PROMPT.md` §8.3). Never add a content field that awards coins directly for a
   gameplay event.

---

## How to work

### Before starting a milestone
Restate its acceptance criteria from `PROMPT.md` §20 in your own words. If you cannot,
you do not understand it yet.

### While working
- Match the surrounding conventions. Units live in field names (`massKg`,
  `springStiffnessNPerM`, `shiftTimeMs`) — never a bare number whose unit must be
  guessed.
- Every public type gets a header comment naming its purpose, owning module, the pillar
  it serves (`PROMPT.md` §2), and the events it emits and consumes.
- Every tuning value is a named field on a data asset with a documented unit and range.
  No magic numbers in code, ever.
- Pool anything spawned more than once per second. Zero heap allocation in the gameplay
  hot path.

### After changing content in `data/`
```bash
python3 tools/validate_content.py data
```
Exit code 0 is clean. Any error fails the build. This runs in CI on every push.

### After finishing a milestone
Run the §21 Definition of Done checklist and record the result in `docs/CHANGELOG.md`.

---

## The two hard gates

Do not proceed past these. They exist because everything downstream is worthless
without them.

**M1 — "Drive a box."** A grey-box car on an empty plane must be *fun to drive* before
any content is built. Three people who did not write it must independently say so.
Budget three weeks and spend all of them on feel.

**M4 — "The verb."** Near-miss detection, combo, scoring, and the full feedback stack.
A tester must say "one more run" without being prompted.

If you are asked to skip or defer either gate, say plainly that it is the one thing the
spec does not allow, and explain why.

---

## Where things live

| Looking for | File |
|---|---|
| Requirement → spec → milestone → test traceability | `docs/00-index.md` |
| Why the design works, difficulty curves, near-miss math | `docs/01-game-design.md` |
| Modules, event bus, pooling, threading, save format | `docs/02-technical-architecture.md` |
| Suspension, tires, powertrain, per-class tuning tables | `docs/03-vehicle-physics.md` |
| Driver personalities, IDM following, police AI | `docs/04-traffic-ai.md` |
| Chunk streaming, road grammar, floating origin | `docs/05-road-generation.md` |
| Art direction, quality tiers, the speed rig, cameras | `docs/06-graphics-art.md` |
| Engine audio model, adaptive music, mixing | `docs/07-audio.md` |
| Screens, HUD, garage, results, localization | `docs/08-ui-ux.md` |
| Currencies, pricing, upgrades, XP, missions | `docs/09-progression-economy.md` |
| JSON schemas and validation lints | `docs/10-data-schemas.md` |
| Frame budgets, LOD, memory, the hitch problem | `docs/11-optimization.md` |
| Milestones, schedule, risk register | `docs/12-roadmap.md` |
| 80 vehicles, 14 environments, 100 achievements | `docs/13-content-manifest.md` |
| Test strategy, the full assertion register | `docs/14-testing-qa.md` |
| Networking interfaces required from M0 | `docs/15-networking-multiplayer.md` |
| Telemetry events, KPIs, balance validation | `docs/16-analytics-telemetry.md` |
| Packaging, versioning, store, release checklist | `docs/17-build-release.md` |
| Input devices, force feedback, remapping | `docs/18-input-controls.md` |
| Firing orders, engine acoustics, sound recording spec | `docs/19-engine-audio-reference.md` |
| Real-manufacturer roster and the licensing flag | `docs/20-licensed-vehicle-roster.md` |

---

## Things that will trip you up

- **Floating origin is mandatory and must be built in M2**, not retrofitted. At 385 km/h
  a run passes 250 km inside 40 minutes and single-precision float spacing at that
  magnitude is 3.1 cm. Every system caching a world position must handle `OriginRebased`.
- **`minGapClearance` is spare room beside the car, not the total opening.** The lateral
  opening is `playerWidth + minGapClearance`.
- **Downforce coefficients are positive.** Never a negative lift coefficient — the schema
  rejects negatives on purpose.
- **`×N` always means the combo *count*** (1–20), not the score multiplier
  (`1 + 0.5N`). See `PROMPT.md` §8.2.
- **Brake lights render at all distances**, out to 500 m, regardless of quality tier.
  They are the player's primary early-warning signal; culling them is a fairness bug.
- **Traffic inside the current sightline requirement always renders**, even on Low.
  Cutting a car the player is about to hit is not an optimization.
- **Indicators carry the same 500 m guarantee as brake lights.** They are a fairness
  system — the player's only warning that a gap is closing. See `docs/04` §3.6.
- **A Courtesy Flash yield scores no near miss.** The car moved out of the way, so
  there is no proximity to reward. This is what stops the mechanic trivialising the
  game; do not "fix" it by adding a reward. See `docs/04` §3.7.
- **Motion is forward-only.** No reverse gear, no revisiting passed road. Chunk index
  is monotonic and freed chunks never come back. See `docs/05` §0.

---

## When the spec is wrong

It will be, somewhere. The numbers are internally consistent and defensible; they are
not playtested. If implementation shows a value is wrong:

1. Say so, with the measurement that shows it.
2. Propose the corrected value and what else it affects — most numbers here are coupled,
   and `docs/00-index.md` shows the couplings.
3. Update the spec *and* `docs/CHANGELOG.md` in the same change as the code.

Do not silently diverge from the spec. A spec that quietly stops matching the build is
worse than no spec.
