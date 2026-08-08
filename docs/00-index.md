# 00 — Master Index and Traceability Matrix

Every requirement in Highway Rush, mapped to where it is specified, which milestone
delivers it, and which test proves it. If a row has no test, it is not done — it is
hoped for.

Use this document three ways:
1. **Before building anything**, find its row and read the linked spec section.
2. **Before calling anything done**, run the linked test.
3. **When changing a number**, check §4 for what else moves with it.

---

## 1. Requirement traceability

`M` = milestone from `PROMPT.md` §20. `T` = test ID from `docs/14-testing-qa.md`.

### 1.1 Core gameplay

| Requirement | Spec | M | Test |
|---|---|---|---|
| Arcade vehicle physics, 120 Hz substeps | `03` §1–5 | M1 | T-PHY-01…09 |
| Steering assist model, speed-sensitive lock | `PROMPT` §4.2, `18` §3 | M1 | T-INP-03 |
| Input latency < 50 ms | `PROMPT` §4.3, `18` §6 | M1 | T-INP-01 |
| Driver assists (ABS, TC, ESC, snap, counter-steer) | `03` §6 | M1 | T-PHY-07 |
| The 250 ms loss-of-control telegraph | `03` §6.1 | M1 | T-PHY-10 |
| Transmissions: auto, sequential, manual | `03` §4.1 | M1 | T-PHY-11 |
| Nitrous, combo-accelerated refill | `03` §4.2 | M4 | T-PHY-12 |
| Engine swaps | `09` §4.1 | M11 | T-ECO-08 |
| Infinite procedural road, 250 m chunks | `05` §1–3 | M2 | T-ROA-01…09 |
| Floating origin rebase | `05` §2.1 | M2 | T-ROA-05 |
| 2–6 lanes with tapered transitions | `05` §5 | M2 | T-ROA-09 |
| Road grammar with cooldowns | `05` §3.1 | M2 | T-ROA-04 |
| 4.0 s sightline guarantee | `05` §4, `04` §6.3 | M2 | T-ROA-03 |
| Traffic spawning and density curves | `04` §5 | M3 | T-AI-04 |
| 8 driver personalities | `04` §2 | M3 | T-AI-05 |
| IDM following, gap-acceptance lane changes | `04` §3.2–3.3 | M3 | T-AI-03 |
| Emergent hazards, breakdowns, pileups | `04` §3.5 | M3 | T-AI-03 |
| Traffic LOD, 3 tiers | `04` §7 | M3 | T-AI-07 |
| **The solvability guarantee** | `04` §6 | M3 | T-AI-01 |
| **The Near-Miss Contract** | `04` §4 | M4 | T-AI-02 |
| Forward-only motion, no reverse | `05` §0 | M1 | T-FWD-01…06 |
| Spin recovery | `05` §0.1 | M2 | T-FWD-05 |
| Indicators as a fairness system, visible to 500 m | `04` §3.6 | M3 | T-AI-10…13 |
| **The Courtesy Flash** | `04` §3.7 | M3 | T-FLASH-01…11 |
| Engine order and per-family acoustics | `19` §1–3 | M7 | T-AUD-08…14 |
| Licensed marque-mapping layer | `20` §1 | M12 | T-LIC-01…07 |
| Art asset delivery spec (sockets, LODs, pivots) | `21` §3 | M12 | T-ART-01…04 |
| Budget class (Mehran tier) | `20` §2, `03` §7 | M12 | T-LIC-01 |
| Near-miss detection at 1.20 m / 0.55 m | `PROMPT` §8.1, `01` §3 | M4 | T-SCO-01 |
| Combo system, 3.2 s window, max 20 | `PROMPT` §8.2 | M4 | T-SCO-02 |
| Scoring formulas | `PROMPT` §8.3, `01` §3.2 | M4 | T-SCO-03 |
| Near-miss feedback within 60 ms | `PROMPT` §8.4 | M4 | T-SCO-04 |
| Collision, scrape, glancing-blow forgiveness | `01` §7 | M4 | T-SCO-05 |
| Instant restart < 1.5 s | `PROMPT` §3, `08` §9 | M4 | T-UX-02 |
| 15 game modes, data-driven | `PROMPT` §9, `10` §3 | M8 | T-MOD-01 |
| Composable modifier system | `PROMPT` §9, `10` §3.1 | M8 | T-MOD-02 |
| Police wanted system, 5 stars | `04` §8.1 | M9 | T-POL-01 |
| Police units, PIT, boxing, roadblocks, spikes | `04` §8.2–8.4 | M9 | T-POL-02…04 |
| Procedural radio chatter | `04` §8.6 | M9 | T-POL-05 |

### 1.2 Presentation

| Requirement | Spec | M | Test |
|---|---|---|---|
| 8 camera modes | `06` §4 | M6 | T-CAM-01 |
| The speed rig, 10 coupled effects | `06` §3 | M6 | T-CAM-02 |
| Camera shake layers, all scalable | `06` §4 | M6 | T-ACC-06 |
| Damage tiers 0–5 | `03` §8.1 | M6 | T-VFX-02 |
| GPU deformation, 16-impact buffer | `03` §8.2 | M6 | T-VFX-03 |
| Debris, glass, sparks, pooled | `03` §8.3, `06` §8 | M6 | T-VFX-01 |
| Animation checklist, 18 items | `06` §9 | M6/M12 | T-VFX-04 |
| PBR, Lumen, SSR, volumetrics, post stack | `06` §2 | M6 | T-GFX-01 |
| 4 quality tiers + Steam Deck | `06` §2, `11` §1 | M15 | T-PRF-01 |
| 9 weather states, blended transitions | `06` §5, `10` §6 | M13 | T-WEA-01 |
| 8 time-of-day presets, continuous blend | `06` §6 | M13 | T-WEA-02 |
| Wet road materials, puddles, spray | `05` §7, `06` §5.1 | M13 | T-WEA-03 |
| Photo Mode | `06` §10 | M14 | T-UX-08 |
| Multi-layer engine audio, 15 families | `07` §1 | M7 | T-AUD-02 |
| Speed bed: wind, tire, chassis | `07` §2 | M7 | T-AUD-01 |
| The near-miss whoosh | `07` §3 | M7 | T-AUD-03 |
| Adaptive stem music | `07` §4 | M7 | T-AUD-06 |
| Crash audio layering | `07` §5 | M7 | T-AUD-05 |
| Submix hierarchy, ducking, 6 sliders | `07` §6 | M7 | T-AUD-04 |

### 1.3 Systems and meta

| Requirement | Spec | M | Test |
|---|---|---|---|
| 22 modules, event-driven | `02` §2–4 | M0 | T-ARC-01 |
| Typed event bus, 60+ events | `02` §4 | M0 | T-ARC-02 |
| Object pooling, zero hot-path allocation | `02` §5, `11` §3.5 | M0 | T-PRF-04 |
| Seeded determinism | `02` §1, `PROMPT` §19.2 | M0 | T-ARC-03 |
| Threading model | `02` §6 | M0 | T-PRF-08 |
| Save format, migration, 3 backups | `02` §7 | M5 | T-SAV-01…03 |
| Content pipeline, build-time validation | `02` §8, `10` §9 | M0 | T-DAT-01 |
| HUD, all elements toggleable | `08` §4 | M5 | T-UX-04 |
| Screen map, full gamepad/keyboard parity | `08` §2–3 | M5 | T-UX-05 |
| Garage, turntable, live preview, test drive | `08` §5 | M11 | T-UX-06 |
| Results screen, readable in 4 s | `08` §6 | M5 | T-UX-07 |
| Settings, 4 tabs + difficulty presets | `08` §7 | M5 | T-UX-09 |
| Localization, 14 languages, RTL | `08` §8 | M17 | T-LOC-01…03 |
| 3 currencies, score→coin conversion | `09` §1–2 | M10 | T-ECO-01 |
| 80 vehicles priced and gated | `09` §3, `13` §2 | M10/M12 | T-ECO-02 |
| 10 upgrade categories × 5 tiers | `09` §4 | M10 | T-ECO-03 |
| Driver level 1–100, prestige | `09` §5 | M10 | T-ECO-04 |
| Missions: 6 daily, 4 weekly, 120 career | `09` §6 | M10 | T-ECO-05 |
| 100 achievements | `09` §8, `13` §5 | M10 | T-ECO-06 |
| Leaderboards, replay-validated | `09` §9, `15` §4 | M14 | T-NET-03 |
| Season Pass, shipped disabled | `09` §10 | M10 | T-ECO-07 |
| Ghost replays, input-trace format | `02` §3, `15` §3 | M14 | T-NET-02 |
| Cloud save | `15` §2 | M14 | T-SAV-04 |
| Full accessibility suite | `PROMPT` §18 | M16 | T-ACC-01…12 |
| Telemetry, opt-in, EU default off | `16` §1–2 | M17 | T-TEL-01 |
| Frame budgets, all tiers | `11` §2 | M15 | T-PRF-01…03 |
| Zero hitches over 30 min | `11` §4 | M15 | T-PRF-02 |
| Memory flat over 60 min | `11` §5 | M15 | T-PRF-05 |
| Upscalers: DLSS, FSR, XeSS, TSR | `11` §6 | M15 | T-PRF-06 |

### 1.4 Content volume

| Requirement | Target | Spec | M | Test |
|---|---|---|---|---|
| Drivable vehicles | 80 | `13` §2 | M12 | T-CNT-01 |
| Vehicle classes | 18 | `03` §7 | M12 | T-CNT-02 |
| Handling identity (blind-identifiable) | 100% | `PROMPT` §13 | M12 | T-CNT-03 |
| Environments | 14 | `13` §3 | M13 | T-CNT-04 |
| Weather states | 9 | `10` §6 | M13 | T-WEA-01 |
| Time-of-day presets | 8 | `06` §6 | M13 | T-WEA-02 |
| Game modes | 15 | `PROMPT` §9 | M8 | T-MOD-01 |
| Traffic vehicle models | 32 | `13` §4 | M12 | T-CNT-05 |
| Achievements | 100 | `13` §5 | M10 | T-ECO-06 |
| Career ladder steps | 120 | `09` §6.3 | M10 | T-ECO-05 |
| Languages | 14 | `13` §7 | M17 | T-LOC-01 |
| Audio assets | ~2,240 | `13` §8 | M7/M12 | T-AUD-07 |
| Engine families | 15 | `19` §6 | M7 | T-AUD-13 |
| Police voice lines | ~305 | `04` §8.6, `13` §8 | M9 | T-POL-05 |

---

## 2. Milestone → requirement rollup

Which requirements each milestone must satisfy before it may be called done.

| M | Name | Requirements delivered | Gate |
|---|---|---|---|
| M0 | Project setup | Architecture, pooling, determinism, CI, content pipeline | — |
| M1 | Drive a box | Physics, input, steering model, assists, telegraph | **HARD** |
| M2 | The road | Chunks, floating origin, lanes, grammar, sightline | — |
| M3 | Traffic | Spawning, personalities, IDM, LOD, **solvability** | — |
| M4 | The verb | Near miss, **contract**, combo, scoring, feedback, restart | **HARD** |
| M5 | Shell | HUD, menus, results, settings, save | — |
| M6 | Feel | Cameras, speed rig, post stack, damage, VFX | — |
| M7 | Sound | Engine model, speed bed, whoosh, crash, music, mixing | — |
| M8 | Modes | 15 modes, modifiers, per-mode HUD and fail rules | — |
| M9 | Police | Wanted, units, roadblocks, spikes, helicopter, chatter | — |
| M10 | Progression | Currencies, levels, unlocks, missions, achievements | — |
| M11 | Garage | Visual + performance customization, swaps, preview | — |
| M12 | Vehicles | 80 vehicles, interiors, audio, handling identity | — |
| M13 | Worlds | 14 environments, 9 weather, 8 TOD, transitions | — |
| M14 | Meta | Leaderboards, replays, ghosts, dailies, cloud, photo | — |
| M15 | Optimize | All frame, memory, hitch, and upscaler targets | — |
| M16 | Accessibility | Every §18 item | — |
| M17 | Ship | Localization, telemetry, tutorial, balance, burn-down | — |
| M18+ | Post-launch | Ghost races, seasons, convoys, cross-play | — |

---

## 3. Where every number lives

The single source of truth for each tuning value. Change it here, nowhere else.

| Domain | Authority |
|---|---|
| Near-miss thresholds and scoring | `PROMPT.md` §8.1–8.3 |
| Combo behavior and display | `PROMPT.md` §8.2 |
| Difficulty ramp and breath cycle | `docs/01` §2 |
| Anti-frustration tolerances | `docs/01` §7 |
| Suspension, tire, powertrain, aero constants | `docs/03` §2–5 |
| Per-class vehicle baselines | `docs/03` §7 |
| Damage energy thresholds | `docs/03` §8.1 |
| Driver personality multipliers | `docs/04` §2 |
| IDM parameters | `docs/04` §3.2 |
| Spawn distances and density multipliers | `docs/04` §5 |
| Police heat and star thresholds | `docs/04` §8.1 |
| Chunk sizes, weights, grammar constraints | `docs/05` §1, §3 |
| Surface grip multipliers | `docs/03` §3.3 |
| Quality tier feature matrix | `docs/06` §2 |
| Speed rig curves | `docs/06` §3 |
| Camera positions and FOV | `docs/06` §4 |
| Time-of-day light values | `docs/06` §6 |
| Audio mix targets and submix layout | `docs/07` §6 |
| UI color, type, and motion tokens | `docs/08` §1 |
| Currency, pricing, upgrade, XP tables | `docs/09` §1–5 |
| Content schemas and valid ranges | `docs/10` |
| Frame, draw call, and memory budgets | `docs/11` §2, §5 |
| Content counts | `docs/13` |
| Telemetry event schema and KPIs | `docs/16` §2–3 |
| Input curves, deadzones, FFB | `docs/18` §3–5 |

---

## 4. Coupled values — change one, check the others

Most tuning here is not independent. These are the couplings that will bite.

| If you change | Also re-derive | Why |
|---|---|---|
| Near-miss threshold (1.20 m) | Lane width, vehicle widths, `minGapClearance`, `docs/01` §3.1 | The threshold is derived from lane geometry — a lazy centered pass must *not* score |
| Lane width | Near-miss threshold, solvability grid, spawn gaps | Same derivation, inverted |
| Player vehicle width | `minGapClearance`, roadblock gaps, solvability | The opening is `width + clearance` |
| Combo max or step size | Score examples `01` §3.2, audio pitch count `07` §3, achievements `13` §5 | 20 steps, 20 pitches, "Chain of Twenty" |
| Score→coin rate (0.30) | Every income benchmark `09` §2.1, all pricing `09` §3, grind guard | Pricing is denominated in hours of play |
| XP formula or run yield | Level curve `09` §5, the 42-hour target, all level gates | The curve is solved *from* the yield |
| Top speed of any class | Speed rig clamp `06` §3, spawn distance `04` §5.1, sightline `05` §4 | Sightline is `speed × 4.0 s` |
| Traffic density curve | Pool size `02` §5, draw distance `06` §2, frame budget `11` §2 | Pool is derived from worst-case concurrency |
| Spawn distance | Traffic draw distance floor `06` §2, chunk lead time `05` §1 | Cars must not spawn beyond what renders |
| Chunk length or lead count | Generation budget `05` §1, hitch budget `11` §4 | Lead time is `chunks × 250 m ÷ top speed` |
| Quality tier draw distances | Sightline guarantee, fairness | Traffic inside the sightline always renders |
| Frame budget | Every per-system budget `11` §2, LOD distances, particle caps | The sub-budgets sum to the total |
| Any vehicle's torque curve | `derivedStats`, class power baseline, gear ratios | Enforced by `tools/validate_content.py` |
| Weather grip multipliers | Mode payout multipliers, difficulty presets | Lower grip must pay more |

---

## 5. Open questions

Things the spec deliberately does not settle, flagged so they are decided consciously
rather than by accident.

| # | Question | Decide by | Default if undecided |
|---|---|---|---|
| 1 | Does distance deserve a larger score share than ~6%? | M4 | No — the thesis is that near misses *are* the game (`01` §1) |
| 2 | Manual H-pattern with clutch — worth the cost for a keyboard-first game? | M1 | Build it; it is cheap once the gearbox model exists |
| 3 | Motorcycles as a class — lean model is a second physics path | M12 | Ship them; they are the highest-ceiling scoring class |
| 4 | Free-to-play variant behind a compile flag | M17 | Keep the flag, ship it disabled |
| 5 | Season Pass at launch or post-launch | M17 | Post-launch; data model exists from M10 |
| 6 | Console ports — which first | 2.0 | Whichever certifies fastest |
| 7 | Player-facing difficulty presets vs. pure assist toggles | M5 | Both, with presets writing visibly to toggles (`08` §7) |
| 8 | Cross-play scope for convoys | 1.3 | Ghost races first, live convoys second (`15` §5) |

---

## 6. Document map

| Doc | Covers | Depends on |
|---|---|---|
| `PROMPT.md` | The contract — all 22 sections | — |
| `00-index` | This file. Traceability, couplings, open questions | All |
| `01-game-design` | Thesis, curves, near-miss math, cadence, anti-frustration | — |
| `02-technical-architecture` | Modules, events, pooling, threading, save | — |
| `03-vehicle-physics` | Suspension, tires, powertrain, aero, damage | `10` |
| `04-traffic-ai` | Personalities, IDM, solvability, police | `01`, `03`, `05` |
| `05-road-generation` | Chunks, grammar, origin, materials | `06` |
| `06-graphics-art` | Direction, tiers, speed rig, cameras, weather, animation | `11` |
| `07-audio` | Engine model, bed, whoosh, music, mixing | `03` |
| `08-ui-ux` | Screens, HUD, garage, results, settings, localization | `09` |
| `09-progression-economy` | Currencies, pricing, upgrades, XP, missions | `01`, `13` |
| `10-data-schemas` | Every content schema and lint | — |
| `11-optimization` | Budgets, LOD, hitches, memory | `06` |
| `12-roadmap` | Milestones, schedule, risk | All |
| `13-content-manifest` | Vehicles, environments, achievements, assets | `03`, `09` |
| `14-testing-qa` | Test strategy and the full assertion register | All |
| `15-networking-multiplayer` | Interfaces required from M0, post-launch scope | `02` |
| `16-analytics-telemetry` | Events, KPIs, balance validation | `01`, `09` |
| `17-build-release` | Packaging, versioning, store, release checklist | `11` |
| `18-input-controls` | Devices, curves, force feedback, remapping | `03` |
| `19-engine-audio-reference` | Firing orders, engine order, crank character, per-family recording spec | `07`, `13` |
| `20-licensed-vehicle-roster` | Real-manufacturer roster, marque-mapping layer, `HR_LICENSED_CONTENT` | `03`, `13`, `19` |
| `21-art-asset-delivery` | Model checklist, sockets, LOD budgets, collision, naming, sourcing | `06`, `11`, `13`, `20` |
