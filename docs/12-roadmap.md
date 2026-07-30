# 12 — Development Roadmap

Milestone order is a dependency chain, not a preference. Do not reorder.
Every milestone ends with a **playable build**.

---

## Phase 1 — Foundation (M0–M2)

### M0 · Project setup
Repo, engine project, Git LFS, CI (build + test + content validation), coding
standards, `EventBus`, `SeededRandom`, `TObjectPool`, save system skeleton, headless
test harness, scope timers, F3 overlay.

**Done when:** CI builds, runs tests, and validates content on every push.

### M1 · Drive a box ⚠️ HARD GATE
One grey-box car with the full physics model from `docs/03`, a flat infinite plane, one
chase camera, throttle/brake/steer, the steering assist model from `PROMPT.md` §4.2.

**Done when:** three people who did not write it independently describe driving the box
on an empty plane as *fun*. If it is not fun here, no amount of content fixes it.
**Do not proceed past this gate.** Budget 3 weeks and spend all of them on feel.

### M2 · The road
Chunk streaming, splines, the grammar, floating origin, lane system, 2–6 lanes, one
grey-box environment, sightline validation.

**Done when:** 30 minutes of continuous driving with zero hitch and zero precision
artifact, verified by the automated 500 km test.

---

## Phase 2 — The game (M3–M5)

### M3 · Traffic
Spawner, solvability solver, IDM following, gap-acceptance lane changes, 8
personalities, pooling, 3-tier LOD, hazards and breakdowns.

**Done when:** a 10-minute run where traffic never feels scripted and the solvability
test passes 10,000 seeded runs.

### M4 · The verb ⚠️ HARD GATE
Collision, near-miss detection, the Near-Miss Contract, combo, full scoring, the
complete feedback stack (§8.4 of `PROMPT.md`), run start/end, instant restart.

**Done when:** a tester says "one more run" without being prompted. This is the second
hard gate and the moment the game becomes a game.

### M5 · Shell
HUD, main menu, mode select, results, pause, settings, save/load, profile.

**Done when:** the complete loop runs end to end and persists across restarts.

---

## Phase 3 — Feel (M6–M7)

### M6 · Feel
8 cameras, the full speed rig, all post-process, damage tiers and deformation,
particles, rumble, shake layers.

**Done when:** side by side with M4 at identical physics, the M6 build feels
unrecognizably faster.

### M7 · Sound
Full engine audio model, speed bed, the near-miss whoosh, crash layers, adaptive music,
submix hierarchy, mixing pass.

**Done when:** the game is satisfying to play with the monitor off for 10 seconds.

---

## Phase 4 — Breadth (M8–M11)

### M8 · Modes
All 15 modes as data, the modifier system, mode-specific HUD widgets and fail
conditions.

**Done when:** adding a 16th mode requires only a JSON file and a localization entry.

### M9 · Police
Wanted system, all unit types, PIT, boxing, roadblocks with designed gaps, spike
strips, helicopter, procedural radio chatter, escape logic, pursuit music layer.

**Done when:** a 5-star chase is the most exciting thing in the game.

### M10 · Progression
Currencies, driver level, unlock tree, shop, 6 daily / 4 weekly / 120 career missions,
100 achievements, statistics, the economy simulation harness.

**Done when:** the first-hour cadence from `docs/01` §4.1 is measured and met.

### M11 · Garage
Full visual customization (paint, wraps, decal editor, body kits, rims, lights,
interior, stance), full performance upgrades, turntable, unlock reveal, live preview,
test drive.

**Done when:** every option in `PROMPT.md` §13 works and is visible on the car.

---

## Phase 5 — Content (M12–M13)

### M12 · Vehicles
All 80 vehicles: models, 4 LODs, interiors, working gauges, audio banks, physics data,
handling identity pass.

**Done when:** blind handling tests — testers identify vehicle class from driving alone
at >80% accuracy.

### M13 · Worlds
All 14 environments, 9 weather states with blended transitions, 8 TOD presets, wet/snow
material systems, environment transitions, per-environment music and ambience.

**Done when:** every environment × weather × TOD combination is shippable, verified by
an automated screenshot matrix (14 × 9 × 8 = 1,008 captures, reviewed).

---

## Phase 6 — Ship (M14–M17)

### M14 · Meta
Leaderboards with server-side replay validation, ghost racing, daily/weekly/monthly
events, cloud save, Photo Mode, replay theater, best-moment clips.

**Done when:** a Daily Challenge is reproducible from its seed across two machines,
bit-identically.

### M15 · Optimize
Hit every target in `docs/11` on every tier. Upscalers, PSO cache, dynamic resolution,
memory budgets, hitch elimination.

**Done when:** 30-minute captures on all 5 tiers with zero frames over budget.

### M16 · Accessibility
Every item in `PROMPT.md` §18.

**Done when:** a full playthrough is completed with each accessibility mode enabled,
one at a time, by someone who needs it.

### M17 · Polish and ship
14 languages, telemetry, crash reporting, the Driving School, full balance pass against
the economy harness, bug burn-down, store assets, trailer, demo build.

**Done when:** zero P0/P1 bugs, balance validated, and the §22 Final Test passes with
five yeses.

---

## Phase 7 — Post-launch (M18+)

| Release | Content |
|---|---|
| **1.1** (+6 weeks) | Ghost races, community feedback fixes, 4 vehicles, 1 environment |
| **1.2** (+3 months) | Season 1, Season Pass enabled, weekly events live |
| **1.3** (+5 months) | Live multiplayer convoys (4-player shared traffic), cross-play groundwork |
| **1.4** (+8 months) | Livery sharing marketplace, replay editor, Steam Workshop for decals |
| **2.0** (+12 months) | Console ports, 20 new vehicles, 4 new environments, a career campaign |

**Networking is isolated behind an interface from M0** so that multiplayer is an
implementation of an existing seam, not a rewrite.

---

## Schedule estimate

| Phase | Milestones | Duration (team of 6–10) |
|---|---|---|
| 1 Foundation | M0–M2 | 8 weeks |
| 2 The game | M3–M5 | 10 weeks |
| 3 Feel | M6–M7 | 8 weeks |
| 4 Breadth | M8–M11 | 14 weeks |
| 5 Content | M12–M13 | 20 weeks (runs parallel with Phase 4) |
| 6 Ship | M14–M17 | 16 weeks |
| **Total** | | **76 weeks serial · ~62 weeks with Phase 5 overlapping Phase 4** |

For a solo developer or an AI-assisted single developer, expect 2.5–3× that, and cut
scope in this order: vehicle count (80 → 30), environments (14 → 6), modes (15 → 8),
languages (14 → 4), Photo Mode, replay theater, Season Pass. **Never cut:** M1 feel,
M4 feedback, the solvability guarantee, the Near-Miss Contract, or the hitch budget.

---

## Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| M1 feel not achieved | Fatal | Hard gate. Do not proceed. Budget extra weeks upfront |
| Floating origin retrofitted late | Severe rework | Build it in M2, test to 500 km |
| Hitches from PSO compilation | Ships broken | Precompile cache, test on clean machines |
| Content volume (80 cars) | Schedule | Engine-family audio reuse, kitbash-friendly modular meshes, scope-cut plan ready |
| Determinism broken by a late feature | Kills leaderboards + dailies | Determinism test in CI from M0 |
| Traffic AI feels scripted | Core experience fails | Personalities + IDM + emergent hazards from M3, playtested |
| Balance grind wall | Retention collapse | Economy harness in CI from M10 |
| Scope creep on multiplayer | Delays launch | Explicitly post-launch. Interface only in v1 |
