# MASTER GAME DEVELOPMENT PROMPT — "HIGHWAY RUSH"

> **How to use this file:** Paste the whole document into your AI coding assistant
> (Claude Code, Cursor, Gemini CLI, Codex, etc.) as the opening instruction of a
> project. Then work milestone by milestone from §20. Every section is written as a
> *directive with concrete numbers* — not a wishlist — so that repeated sessions with
> different context windows converge on the same game.
>
> The deep specifications live in `docs/`. This file is the contract; `docs/` is the
> reference manual. When a number appears in both, `docs/` wins.
>
> **Start with `docs/00-index.md`.** It maps every requirement below to its spec
> section, its milestone, and the test that proves it — and its §4 lists which numbers
> move together, which is what bites hardest when tuning. `CLAUDE.md` orients an AI
> assistant working in the repo.
>
> | | | | |
> |---|---|---|---|
> | `00` index & traceability | `05` road generation | `10` data schemas | `15` networking |
> | `01` game design | `06` graphics & art | `11` optimization | `16` analytics |
> | `02` architecture | `07` audio | `12` roadmap | `17` build & release |
> | `03` vehicle physics | `08` UI & UX | `13` content manifest | `18` input & controls |
> | `04` traffic & police AI | `09` progression & economy | `14` testing & QA | `19` engine audio |
> | | | | `20` licensed roster |
> | | | | `21` art asset delivery |

---

## 0. ROLE AND CONTRACT

You are the lead engineer and technical director for **Highway Rush**, an endless
arcade highway-driving game for PC. You will design, implement, tune, document, and
test the entire product.

**Non-negotiable constraints:**

1. **Original work, with a licensed-content layer.** Highway Rush is *inspired by* the
   Traffic Racer genre. You must not copy, decompile, extract, reference, or reproduce
   any code, art, audio, UI layout, string, logo, car model, brand name, or trade dress
   from Traffic Racer or any other shipped game — that prohibition is absolute.

   Real car manufacturers **are** supported, through the marque-mapping layer in
   `docs/20-licensed-vehicle-roster.md`. Every vehicle carries an invented marque
   (`docs/13` §1) as its permanent fallback plus an optional `licensed` block, and the
   `HR_LICENSED_CONTENT` build flag chooses which identity ships. Physics, class, price,
   and progression slot are byte-identical between the two. With the flag off, no real
   manufacturer string may appear anywhere in the build — asserted by `T-LIC-02`.
   Never hardcode a real marque into content.
2. **Playable at every milestone.** The build must run and be fun after *every*
   milestone in §20. Never leave the repo in a state where the game does not launch.
3. **No placeholder-only milestones.** If art is not ready, ship grey-box art that is
   correctly scaled, correctly lit, and correctly collided — never a missing mesh.
4. **Performance is a feature, not a pass.** The frame budget in §17 is an acceptance
   criterion for every merge, equal in weight to correctness.
5. **No pay-to-win.** Real money may only ever buy cosmetics, time savings on
   soft-currency grind, and the optional Season Pass cosmetic track. Never stats.
6. **Deterministic where it matters.** Traffic spawning, weather, and road generation
   are seeded. The same seed produces the same run. This is required for Daily
   Challenges, ghost replays, and leaderboard verification.

**Working method:** Build in the milestone order of §20. Before starting a milestone,
restate its acceptance criteria. After finishing, run the checklist in §21 and record
results in `docs/CHANGELOG.md`. Prefer small, reviewable commits with a working build
at each one.

---

## 1. PRODUCT DEFINITION

**Title:** Highway Rush
**Genre:** Endless arcade highway racer / traffic weaver
**Platform (v1):** Windows PC (Steam), 64-bit. Architected to port to Linux/Proton,
Steam Deck, and later console.
**Camera perspective:** Behind-the-car third person by default; 8 camera modes total.
**Session length:** 90 seconds to 12 minutes per run. Median target: 3m 20s.
**Rating target:** ESRB E10+ / PEGI 7 — vehicle collisions only, no gore, no blood,
no pedestrians struck, no real-world weapons.
**Monetization (v1):** Premium purchase, no ads, optional cosmetic DLC. The
architecture must support a free-to-play variant behind a compile flag, but F2P hooks
ship disabled.

**One-line pitch:** *Thread a supercar through 300 km/h freeway traffic at inches of
clearance, and cash in the terror.*

**The 30-second experience:** You start at 0 km/h in the right lane of a six-lane
interstate at golden hour. You floor it. By second 8 you're at 180 km/h and the first
truck fills your windshield. You flick left, pass it with 40 cm to spare, and the
screen edges bloom, the world briefly dims, a bright chime fires, and `+258 NEAR MISS
×2` punches out of the HUD. Twelve seconds later you're at 260 km/h in a ×7 combo, the
FOV has widened by 18 degrees, the road noise has become a roar, and you are one
mistake from ending the run. That tension *is* the game.

---

## 2. CORE PILLARS

Every feature must serve at least one pillar. If it serves none, cut it.

| # | Pillar | What it means mechanically | How it is measured |
|---|--------|---------------------------|--------------------|
| 1 | **Speed** | Perceived velocity outruns actual velocity via FOV, motion blur, audio, roadside density | Players estimate speed ~15% higher than the HUD number |
| 2 | **Risk** | Reward scales super-linearly with proximity and speed | >60% of score comes from near misses at skilled play |
| 3 | **Flow** | Inputs are instantly legible; no ambiguous failure | Median time-to-first-crash > 40 s for new players |
| 4 | **Momentum** | Stopping is never optimal. Braking is a loss | Top-10% runs spend <4% of time below 120 km/h |
| 5 | **Near-Miss Ecstasy** | The single loudest, brightest, most tactile event in the game | Near miss feedback fires within 60 ms of the event |
| 6 | **Control** | The car goes exactly where the player pointed it | <50 ms input-to-pixel latency at 60 fps |
| 7 | **Reward** | Something meaningful unlocks roughly every 3 runs early on | Median 2.8 runs per unlock in the first hour |
| 8 | **Progression** | 40+ hours to full unlock without grinding walls | See §14 economy curve |
| 9 | **Visual satisfaction** | Every frame could be a screenshot | Photo Mode usage > 5% of sessions |
| 10 | **Audio satisfaction** | The engine is a character | Players can identify their car blind |
| 11 | **One More Run** | Death is fast, restart is instant | Crash-to-driving on restart < 1.5 s |

**The Pillar Test:** Before implementing anything, write one sentence naming which
pillar it serves and how. Put that sentence in the class header comment.

---

## 3. THE CORE LOOP

```
        ┌──────────────────────────────────────────────────────┐
        │                                                      │
   ┌────▼────┐   ┌────────┐   ┌───────────┐   ┌──────────┐  ┌──┴───┐
   │ GARAGE  │──▶│ SELECT │──▶│   DRIVE   │──▶│ RESULTS  │─▶│ SPEND│
   │ preview │   │  mode  │   │  the run  │   │ + payout │  │ + up-│
   │ + tune  │   │ + map  │   │ 90s–12min │   │ + rank   │  │ grade│
   └─────────┘   └────────┘   └───────────┘   └──────────┘  └──────┘
                                    │                            │
                                    │  R = instant restart       │
                                    └────────────────────────────┘
```

**Moment-to-moment loop (every 2–6 seconds):**
`Spot gap → commit → thread it → get paid → speed increases → gaps shrink → repeat`

**Session loop (every 3–12 minutes):** Run → payout → one purchase decision.
**Meta loop (every 20–60 minutes):** New car or new environment unlocks.
**Retention loop (daily):** Daily Challenge with a fixed seed + login reward.

**Non-negotiable feel rules:**
- Restart must require exactly one keypress and complete in under 1.5 s.
- No unskippable animation ever plays between runs.
- The results screen shows the payout counting up in under 1.2 s, and `R` skips it.

---

## 4. CONTROLS AND INPUT

**Full device, force-feedback, latency, and remapping spec in
`docs/18-input-controls.md`.**

Support keyboard, gamepad, and steering wheel simultaneously — hot-swappable
mid-run without a menu visit. The active device is detected on last input and swaps
the HUD prompt glyphs within one frame.

### 4.1 Default bindings

| Action | Keyboard | Gamepad | Wheel |
|---|---|---|---|
| Steer | A/D or ←/→ | Left stick X | Wheel axis |
| Throttle | W / ↑ | RT (analog) | Throttle pedal |
| Brake | S / ↓ | LT (analog) | Brake pedal |
| Courtesy flash (high beams) | F | LB | Button |
| Handbrake | Space | B / Circle | Button |
| Nitrous | Shift | A / Cross | Button |
| Horn | H | RB | Horn |
| Look back | C (hold) | RS click (hold) | Button |
| Change camera | V | D-pad Up | Button |
| Shift up (manual) | E | RB | Right paddle |
| Shift down (manual) | Q | LB | Left paddle |
| Headlights | L | D-pad Left | Button |
| Photo mode | P | D-pad Right | — |
| Pause | Esc | Start | Button |
| Instant restart | R (hold 0.25 s) | Y (hold 0.25 s) | Button |

### 4.2 Steering feel (this is the most important tuning in the game)

Digital keyboard input must feel as good as an analog stick. Achieve it with a
**steering assist model**, not raw input:

```
SteerInput      ∈ [-1, 1]          // raw device
SpeedFactor     = clamp(1 - (speed / 340) * 0.72, 0.28, 1.0)
SteerRate       = 4.8              // units/sec toward target, keyboard ramp
SteerReturnRate = 7.5              // units/sec back to center on release
MaxSteerAngle   = 34° * SpeedFactor  // speed-sensitive steering lock
CounterSteerAssist = 0.35          // auto-correction of yaw error, arcade
```

- **Speed-sensitive lock:** at 300 km/h the steering lock is only 12.4°, and it bottoms
  out at 9.5° from 340 km/h up, so a full stick deflection is a lane change, not a spin.
  This single line is what makes the game playable at 300 km/h.
- **Lane-snap assist (default ON, toggleable):** when steering input returns to zero,
  apply up to 0.8 m/s of lateral correction toward the nearest lane centerline. Cancels
  instantly on any steering input. Prevents drift-death on long straights.
- **Deadzone:** stick 0.12 inner, 0.95 outer, remapped with a 1.6 exponent response
  curve for fine control near center.
- **No input smoothing beyond the above.** Never add latency for "weight." Weight is
  communicated by the *camera and body roll*, not by delaying the tires.

### 4.3 Input latency budget

Input poll → physics tick → camera → render → present must total **< 50 ms** at 60 fps.
Poll input on the render thread at frame start, never on a fixed-tick game thread.
Physics substeps at 120 Hz minimum. Disable engine-level frame smoothing and any
"one frame of input buffering" defaults.

---

## 5. VEHICLE PHYSICS

Arcade-first, physics-informed. The player should never lose the car to something
they cannot see coming. **Full model, tuning tables, and per-class numbers are in
`docs/03-vehicle-physics.md`.** Summary of requirements:

- 4-wheel raycast/sweep suspension model with per-wheel spring, damper, anti-roll bar.
- Longitudinal: torque curve → gearbox → final drive → wheel torque → traction-limited
  force. Real gear ratios per vehicle. Redline, rev limiter bounce, engine braking.
- Lateral: Pacejka-lite slip curve, simplified to a 3-point curve per tire compound
  (peak grip, peak slip angle, falloff). Full Pacejka is out of scope and unnecessary.
- Aerodynamics: drag `Fd = 0.5·ρ·Cd·A·v²`, plus downforce scaling grip with `v²`,
  capped so top-speed handling stays arcade-forgiving.
- Weight transfer drives *visual* body roll, brake dive, and squat AND *actual* per-
  wheel grip. Both, always coupled — that coupling is the feel.
- Assists, all individually toggleable, all ON by default: ABS, TC, ESC, lane-snap,
  auto-counter-steer, drift-recovery.
- Transmissions: Automatic (default), Sequential, Manual H-pattern with clutch.
- Nitrous: +38% torque, 4.0 s capacity, 12 s refill, refilling up to 50% faster while a
  combo is running. This makes nitrous a *reward for risk*, not a resource to hoard.

**The Golden Rule of handling:** *Understeer is a warning, oversteer is a punishment,
and neither may arrive without 250 ms of telegraph* (audio tire squeal + camera roll +
controller rumble) before control is actually lost.

---

## 6. ROAD GENERATION

Infinite, seeded, chunk-streamed procedural highway. **Full algorithm in
`docs/05-road-generation.md`.** Requirements:

- **Motion is forward-only.** There is no reverse gear and no way to revisit passed
  road. This is a design decision that pays for itself: the chunk index becomes
  monotonic, streaming becomes a ring buffer rather than a bidirectional window, passed
  chunks are freed permanently, and memory is bounded and constant regardless of run
  length. Spin recovery for the one case this cannot handle is in `docs/05` §0.1.

- **Chunk size:** 250 m. Keep 6 chunks ahead, 2 behind. Generate on a worker thread,
  hand off finished chunks to the game thread for attachment. Never hitch.
- **Spline-based:** each chunk is a spline with curvature, grade, bank, lane count,
  and a decoration budget. Meshes are built by spline-sweep + instanced scatter.
- **Floating origin:** rebase world origin every 4096 m to preserve float precision at
  arbitrary distance. This is mandatory — an endless runner at 300 km/h reaches
  precision failure in under 20 minutes without it.
- **Lane counts:** 2, 3, 4, 5, and 6 lanes. Lane count transitions occur only inside
  designated "merge" chunks with a proper taper — never a discontinuity.
- **Chunk archetypes:** long straight, gentle curve (R = 800–2500 m), sweeper,
  crest/dip, tunnel, bridge, overpass, underpass, construction zone, exit ramp,
  toll gantry, rest-stop pass-by.
- **Grammar, not randomness:** chunk selection uses a weighted grammar with cooldowns
  so you never get three tunnels in a row, and a difficulty ramp that biases toward
  curves and construction as distance increases.
- **Readability rule:** the player must always see at least **4.0 seconds of road**
  ahead at current speed. Curvature, crest height, and fog density are all clamped
  against this. At 300 km/h that's 333 m of clear sightline. This constraint outranks
  visual interest, always.
- 14 environment biomes with distinct road furniture, terrain, vegetation, skybox,
  lighting, and audio bed. See §11 and `docs/13-content-manifest.md`.

---

## 7. TRAFFIC AI

Traffic must feel like *people driving badly*, never like a spawner. **Full behavior
spec, FSM, and spawn algorithm in `docs/04-traffic-ai.md`.** Requirements:

### 7.1 Driver personalities
Every spawned vehicle rolls a personality that persists for its lifetime and modifies
target speed, following distance, lane-change eagerness, reaction time, and blinker
discipline:

`Timid · Normal · Hurried · Aggressive · Distracted · Erratic · Professional · Learner`

Distribution is per-environment and per-mode (a Japanese expressway at 2 a.m. is not a
construction zone at rush hour).

### 7.2 Behaviors required
Lane keeping with lateral noise, gap acceptance for lane changes, adaptive following
(IDM-style), overtaking, cooperative merging, refusing to merge, phantom braking,
brake-check road rage, blinkers (used correctly by Professional, late by Normal, never
by Erratic), hazard lights, breakdowns on the shoulder, multi-car pileups that persist
as obstacles, traffic jams that form and dissolve, construction lane closures,
emergency vehicles that other traffic yields to.

### 7.3 The Near-Miss Contract
This is the most important AI rule in the game:

> **Traffic AI may never take an action that makes an already-committed near miss
> unavoidable into a collision.** Once the player's front bumper passes a traffic
> vehicle's rear bumper, that vehicle's lane-change and braking authority is locked
> for 0.9 seconds.

Without this, the game feels cheap and players quit. With it, players feel skilled.

### 7.4 Spawning
- Spawn 260–420 m ahead (scaled by player speed), despawn 140 m behind or 500 m ahead.
- Never spawn inside the player's line of sight transition — spawn behind a crest,
  around a curve, beyond fog, or at the far clip. Never pop in visibly.
- **Guaranteed-solvable rule:** the spawner must verify that at the player's current
  speed there exists at least one gap reachable within 2.5 s of lateral movement. If
  not, it delays or shifts the spawn. Difficulty comes from *narrow* gaps, never from
  *no* gaps.
- Density, speed spread, and personality mix are per-mode curves that ramp with
  distance. See `docs/04-traffic-ai.md` §5.
- Object pooling, always. Zero runtime allocation for traffic after warmup.

### 7.5 LOD
Full physics + behavior within 150 m. Simplified kinematic motion 150–350 m. Pure
spline-follow beyond 350 m. Animation and audio cull at 90 m. The transition must be
invisible.

---

### 7.6 Signalling and the Courtesy Flash

**Full spec in `docs/04-traffic-ai.md` §3.6–3.7.**

**Indicators are a fairness system, not decoration.** They are the player's only advance
warning that a gap is about to close, so they carry the same guarantee as brake lights:
visible to 500 m at every quality tier, always, surviving every LOD transition. Signal
discipline varies by personality — `Professional` signals early and correctly,
`Aggressive` usually does not, `Erratic` never — but the 54% of traffic that does signal
must be enough that the player learns to read them.

**The Courtesy Flash** is the game's second skill axis. Flashing your high beams at the
car ahead asks it to move over, which is real motorway behaviour — across continental
Europe the keep-right rule is a legal duty and the flash is the standard signal that
faster traffic wants through.

- Affects **one** vehicle: the nearest in the player's lane, 25–110 m ahead.
- Yield chance is per-personality (95% `Professional` → 10% `Aggressive`, which has a
  15% chance of a retaliatory brake-check) and modified per environment (European
  Motorway ×1.25, Cyberpunk City ×0.60).
- **Normal gap acceptance still applies.** A driver who wants to move but has nowhere to
  go stays put — and shows the indicator anyway, signalling intent it cannot yet act on.

Four rules stop it trivialising the game, and the first is load-bearing:

1. **A yielded pass scores no near miss.** The car moved, so there is no proximity to
   reward. The Courtesy Flash is a *safety valve that costs points*, never a scoring
   strategy. Threading a gap is always worth more than asking for one.
2. It costs time — at 300 km/h, a response plus a lane change is over 200 m, so the
   flash must be sent early. Reading traffic that far out is a skill, and a different
   one from threading.
3. Re-flashing the same vehicle within 6 s cuts its yield chance by 30% per repeat and
   doubles the brake-check chance. Spamming makes the road more hostile.
4. It cannot manufacture a gap, so it can never violate the solvability guarantee in
   either direction.

Flashing at police adds heat and never causes a yield. Hardcore mode disables it
entirely.

---

## 8. SCORING, NEAR MISS, AND COMBO

This is the heart of the reward pillar. **Exact formulas are canonical here.**

### 8.1 Near miss detection

```
NearMiss fires when ALL of:
  - lateral clearance between collision bounds  <  1.20 m   (Close: < 0.55 m)
  - relative longitudinal overlap crosses from ahead→behind (a true pass)
  - player speed  >  70 km/h
  - relative speed  >  22 km/h
  - this traffic instance has not scored in the last 1.5 s
```

Award, with `v` = player speed in km/h:

```
base          = 30
proximityMul  = lerp(1.0, 3.0, 1 - clamp(clearance / 1.20, 0, 1))
speedMul      = 1.0 + (v - 70) / 130            // 1.0 at 70, ~3.0 at 330
oncomingMul   = 2.0 if the vehicle is travelling toward the player, else 1.0
laneSplitMul  = 1.5 if passing between two vehicles simultaneously
points        = base * proximityMul * speedMul * oncomingMul * laneSplitMul * combo
```

### 8.2 Combo

```
comboWindow   = 3.2 s, refreshed by any scoring event
comboCount    = +1 per near miss, +1 per 100 m at >150 km/h
comboMax      = 20
comboMultiplier = 1 + (comboCount * 0.5)        // ×1.0 → ×11.0
combo resets to 0 on: any collision, any wall contact, or window expiry
```

**Display convention (use it consistently everywhere):** the HUD shows the **combo
count** as a large `×N` (1–20) inside a shrinking ring that indicates time remaining,
with the resulting **score multiplier** as a smaller secondary figure beneath it. All
prose in these documents that says "a ×12 combo" means a combo *count* of 12, which is
a score multiplier of ×7.0.

At combo counts 5, 10, 15, and 20 a distinct escalating audio stinger fires and a
post-process tier engages.

### 8.3 Score, and how score becomes money

**There is one currency of merit: score.** Every gameplay award is a point award.
Coins are a fixed fraction of score, so a run that scores better always pays better.

```
score = nearMissPoints + distancePoints + speedPoints + bonusPoints
coins = round(score * 0.30) * modeMultiplier * prestigeBonus
```

| Award | Points |
|---|---|
| Distance | `distanceMetres / 10 × speedTierMul` |
| Speed tier multiplier | ×1.0 <120, ×1.25 120–180, ×1.6 180–240, ×2.2 240–290, ×3.0 >290 km/h |
| Near miss | Per §8.1 — the dominant source at skilled play |
| Sustained >200 km/h | +10 / s |
| Oncoming-lane driving (Two-Way) | +15 / s, only while actually in an oncoming lane |
| Overtake (same direction, no near miss) | +5 |
| Airtime (crest jumps) | +30 / s |
| Roadblock threaded | +800 |
| Police evasion, on escape | `250 × stars²` (6,250 at five stars) |
| Perfect run bonus | +25% of the run's subtotal if zero contact |
| Mission / challenge completion | Paid separately in Coins and Cash — see `docs/09-progression-economy.md` |

Cash and Tokens are never awarded by driving. They come from missions, achievements,
level-ups, and events, which keeps driving income on a single clean axis.

### 8.4 Feedback (non-negotiable timing)

Every near miss, within **60 ms**:
- Radial white-blue screen-edge flash, 140 ms decay
- Time dilation to 0.82× for 110 ms, eased in 30 ms / out 80 ms (Close near miss only)
- Doppler whoosh, panned to the side it passed, pitched by relative speed
- Controller rumble: 45 ms, high-frequency, intensity = proximityMul / 3
- Floating `+N` at the pass point, world-space, drifting back with the traffic
- Combo ring pulse and multiplier punch-scale to 1.25 then settle over 180 ms
- Camera micro-shake, 0.9° amplitude, 120 ms

---

## 9. GAME MODES

15 modes. All share one gameplay core; each is a data-driven ruleset in
`data/modes/*.json` (schema in `docs/10-data-schemas.md`). Never fork the gameplay
code per mode.

The "Scoring bias" column lists the mode's point multipliers, which flow through to
coins via the single §8.3 conversion — modes never have their own coin rules.

| Mode | Rule | Fail condition | Scoring bias |
|---|---|---|---|
| **Classic Endless** | One-way traffic, ramping density | Crash | Balanced |
| **Two-Way** | Half the lanes oncoming | Crash | ×2.0 near miss |
| **Time Trial** | 90 s start; +2 s per near miss, +5 s per checkpoint | Clock hits 0 | ×1.5 distance |
| **Police Escape** | 5-star wanted system, escalating pursuit | Busted or crash | ×2.5 evasion |
| **Free Ride** | No fail, no score, sandbox, all cars | None | None (0 payout) |
| **Rush Hour** | 2.4× traffic density, 3-lane max, slower flow | Crash | ×1.8 near miss |
| **Night** | Night TOD, headlights, reduced sightline | Crash | ×1.4 all |
| **Rain** | Wet grip 0.78×, spray, reduced visibility | Crash | ×1.5 all |
| **Fog** | Sightline 120 m, spawn distance clamped | Crash | ×1.7 all |
| **Snow** | Grip 0.62×, snowbank walls, drift-heavy | Crash | ×1.6 all |
| **Hardcore** | One life, no assists, no HUD except speed | Any contact | ×3.0 all |
| **No Brakes** | Brake input disabled, throttle floor of 40% | Crash | ×2.2 all |
| **Fuel Run** | Fuel drains; near misses and speed refill it | Fuel = 0 | ×1.6 all |
| **Daily Challenge** | Fixed seed + fixed car + fixed modifier, one entry/day | Per-modifier | Fixed reward |
| **Weekly / Monthly Event** | Themed multi-objective ladder | Per-event | Cosmetic track |

**Modifier system:** Daily/Weekly modifiers are composable flags — `SlipperyRoads`,
`DoubleDensity`, `NoNitrous`, `InvertedSteering`, `FogBanks`, `SpeedFloor`,
`OneLaneClosed`, `NightOnly`, `TruckHeavy`, `MirrorWorld`. The event system composes
2–3 of them. Adding a new modifier must require zero gameplay code changes.

---

## 10. POLICE AI

**Full spec in `docs/04-traffic-ai.md` §8.** Requirements:

- 5 wanted stars. Heat rises with speed, near misses, contact with police, and time;
  decays when out of line of sight for 8+ seconds.
- Unit types by star: ★ single interceptor sedan → ★★ paired interceptors →
  ★★★ + SUV rammers → ★★★★ + roadblocks and spike strips → ★★★★★ + helicopter
  spotlight, heavy blockers, and pre-positioned ambushes.
- Pursuit behavior: pursuit-curve intercept, PIT maneuver attempts when alongside for
  >1.2 s, blocking formations, boxing-in at low speed.
- Roadblocks spawn 700–1100 m ahead with a *designed gap* the player can thread —
  the gap narrows per star but is never zero (see the Guaranteed-Solvable rule, §7.4).
- Spike strips are visible for at least 2.0 s at current speed before contact.
- Escape: break line of sight and hold it for 12 s, or exceed 1.2 km of separation.
- **Radio chatter:** procedurally assembled dispatch lines that reference the player's
  actual state — current speed bracket, environment, lane, star level, and unit
  callsigns. Barks are a data table, never hardcoded. This is a huge cheap win for
  atmosphere; do not skip it.

---

## 11. ENVIRONMENTS, WEATHER, AND TIME OF DAY

### 11.1 Environments — 14 total
Modern City · Countryside · Desert · Forest · Snow · Coastal Highway · Mountain Pass ·
Industrial Zone · Airport Highway · Cyberpunk City · Japanese Expressway · European
Motorway · American Interstate · Middle Eastern Highway

Each defines: road material set, barrier/guardrail type, sign language and shapes,
vegetation and scatter sets, terrain profile, skybox/HDRI set, lighting presets per
TOD, fog and atmospheric params, ambient audio bed, traffic-mix weighting, and its own
music cue set. Full definitions in `docs/13-content-manifest.md`.

### 11.2 Weather — 9 states + transitions
Clear · Cloudy · Overcast · Rain · Thunderstorm · Fog · Snow · Blizzard · Sandstorm

- Weather is a **state machine with blended transitions over 25–60 s**, never a cut.
- Every state drives, in one data asset: surface grip multiplier, sightline distance,
  particle system, wetness/snow-cover material parameter (0→1, animated), wind vector
  (affects particles, vegetation, and a small lateral force on light vehicles), skybox,
  sun/moon intensity and color, fog density and height falloff, post-process, audio bed,
  and traffic behavior modifiers (everyone drives slower and follows further in rain).
- **Wet roads are the single highest-value visual in the game.** Budget accordingly:
  screen-space reflections of headlights and signs, animated puddle normal maps, spray
  particles behind every wheel of every vehicle, wiper-blade effect on cockpit/hood
  cams, droplets on the lens with speed-driven streaking.
- Thunder: flash lights the whole scene for 90–160 ms via a directional light burst,
  audio delayed by distance/343 m·s⁻¹. Do not sync them — the delay *is* the effect.

### 11.3 Time of day — 8 presets, continuously blendable
Dawn · Morning · Noon · Afternoon · Golden Hour · Sunset · Night · Midnight

Full dynamic sun/moon with correct color temperature ramp (1800 K sunrise → 6500 K noon
→ 2000 K sunset), star field, moon phases, dynamic shadow cascades, automatic
streetlight and headlight activation on a light-level threshold, and headlight
volumetric cones that only enable below a lux threshold to save cost in daylight.

---

## 12. GRAPHICS AND ART DIRECTION

**Full spec in `docs/06-graphics-art.md`.**

**Art direction:** *Grounded realism with heightened light.* Photoreal materials and
proportions, but color grading and bloom pushed one step past life — think a
well-graded car commercial, not a simulator. Silhouettes must read instantly at speed.
Never let decoration compete with the road for the player's attention.

**Required rendering features:** PBR throughout, HDR pipeline, Lumen GI + reflections
with a fallback to baked/probe lighting on the Low tier, Nanite where it pays (barriers,
buildings, rocks — *not* on the player car which needs LOD control), SSR/SSGI, contact
shadows, volumetric fog and light shafts, per-object motion blur (velocity-buffer
based, toggleable), depth of field in Photo Mode and cockpit only, bloom with a lens
dirt mask that scales with speed, subtle chromatic aberration that scales with speed
and nitrous only, film grain at 0.02 max, ACES-derived tonemapping, and a
speed-triggered radial blur/vignette rig.

**The speed rig — how Highway Rush *feels* fast (implement all of it):**

All of it is driven by one normalized value, `s = clamp(speed_kmh / 300, 0, 1.15)`
(above 1.0 only under nitrous). Exact curves are in `docs/06-graphics-art.md` §3.

| Effect | 0 km/h | 150 km/h | 300 km/h |
|---|---|---|---|
| Camera FOV | 72° | 84° | 96° |
| Camera distance | 5.2 m | 5.9 m | 6.6 m |
| Camera height | 1.90 m | 1.75 m | 1.60 m |
| Radial blur strength | 0.00 | 0.15 | 0.45 |
| Vignette | 0.20 | 0.34 | 0.48 |
| Chromatic aberration | 0.00 | 0.09 | 0.35 |
| Camera lag / spring stiffness | soft | medium | tight |
| Wind vibration amplitude | 0.00° | 0.24° | 1.10° |
| Ground-plane speed-line particles | off | subtle | strong |
| Roadside object scatter density | — | — | +40% near-road |
| Audio low-pass on music | 20 kHz | 14.5 kHz | 9 kHz |

All of these interpolate continuously and every one is individually toggleable in
Accessibility (§18). Nitrous pushes each of these to its 300 km/h value plus 15% for
its duration, with a 0.25 s ease.

**Damage:** tiered visual damage — scratches (decal), scuffs, broken mirrors, cracked
and shattered glass (with a shard shader), detached bumpers/hoods as physics debris,
dented panels via a blend-shape/vertex-offset "deformation" pass driven by impact
position and force, wheel damage with visible camber change, smoke → steam → fire
escalation, and a final destruction state. Soft-body deformation is approximated with
per-vertex offsets from an impact accumulation buffer, not a real soft-body solver.

---

## 13. VEHICLES AND CUSTOMIZATION

**80 vehicles minimum.** Full roster with invented marques, classes, stats, unlock
prices, and unlock gates in `docs/13-content-manifest.md`.

**Classes:** Starter · Economy · Hatchback/Hot Hatch · Sedan · Muscle · Sports · Super ·
Hyper · Luxury · SUV · Pickup · Van · Off-Road · Classic · Electric · Track/Formula-
inspired · Bike (motorcycle handling variant) · Special/Unlockable

**Every vehicle ships with:** exterior with 4 LODs + a shadow proxy, a full modeled
interior, working analog dashboard (tachometer, speedometer, fuel, temp, gear
indicator, warning lamps — all driven by real telemetry), animated steering wheel with
correct lock ratio, driver hands + arm IK on the wheel, animated pedals, gear shifter
animation, per-wheel suspension animation, visible brake calipers with heat glow under
hard braking, functional headlights/taillights/brake lights/reverse lights/indicators/
hazards, a unique horn sample, exhaust position markers, backfire and flame FX on
lift-off and nitrous, opening driver door for the garage reveal, and a
`vehicle_<id>.json` data file (schema in `docs/10-data-schemas.md`).

**Handling identity:** every vehicle must be blind-identifiable from handling alone.
Enforce this by giving each a distinct combination of: mass, weight distribution, drive
layout (FWD/RWD/AWD), torque curve shape, gear count and ratios, grip balance,
steering lock, roll stiffness, and nitrous behavior. A muscle car snaps loose on
throttle; a hyper car is knife-stable but unforgiving in transition; an SUV wallows and
lifts a wheel. See the tuning tables in `docs/03-vehicle-physics.md` §7.

**Customization — visual:**
Paint (gloss, metallic, matte, satin, pearl, candy, chrome, chameleon, carbon, raw
metal, rust, livery-wrap), 2-color and 3-color paint zones, 60+ wrap patterns, decal
system with free placement/scale/rotate/layer (30-layer limit) and a save/share slot,
40+ rim designs with width/offset, tire profile and stretch, brake caliper color, brake
disc type, window tint (5 levels + colored), headlight and taillight tint, LED
underglow with 16 patterns, interior color and material, spoilers, splitters, diffusers,
side skirts, hoods, roof scoops, bumpers (front/rear), exhaust tips, mirror types,
license plate text (profanity-filtered), and a suspension ride-height + camber slider
that visually changes stance and *actually affects handling*.

**Customization — performance (5 tiers each):**
Engine, Turbo/Supercharger, Nitrous capacity, Transmission, Tires (5 compounds),
Brakes, Suspension, Weight reduction, Aero/downforce, Cooling.
Each tier displays exact numeric deltas — no hidden stats, ever. Full upgrade tables in
`docs/09-progression-economy.md`.

**Engine swaps** are separate from and deeper than upgrade tiers: a swap replaces the
whole powertrain — torque curve, rev range, gear count, engine family, and audio bank —
and carries its own mass and centre-of-mass penalty. Dropping a V8 into a front-engined
hatch adds 95 kg over the nose and it understeers for it. A swap is a trade, never a
free upgrade. Spec in `docs/09-progression-economy.md` §4.1.

---

## 14. ECONOMY, PROGRESSION, AND CONTENT

**Full tables in `docs/09-progression-economy.md`.** Requirements:

- **Currencies:** Coins (common, from driving), Cash (rare, from missions,
  achievements, level-ups, and first-time challenge clears), Tokens (premium, cosmetic
  only, also earnable at ~40/week free).
- **Driver Level 1–100**, XP from distance, near misses, and objectives. Levels gate
  content and grant Cash. **Prestige** at 100 with a permanent cosmetic marker and a
  +2% coin bonus per prestige, capped at +20%.
- **Unlock cadence target:** first 60 minutes must deliver 4 cars, 2 environments,
  1 mode, and 12 upgrade purchases. Then taper to roughly one meaningful unlock per
  25–35 minutes through hour 12, and one per 60–90 minutes to full completion at ~48 h.
- **Missions:** 6 daily (reroll 1/day), 4 weekly, and a 120-step career ladder.
  Examples: drive 20 km in one run · reach 300 km/h · 50 near misses in one run ·
  100 overtakes · a 10 km no-contact run · escape a 4-star chase · 5 km at night ·
  8 km in rain · complete a run in a truck-class vehicle · hold a ×15 combo for 20 s.
- **Achievements: 100 total** — 70 visible, 20 skill-gated, 10 hidden. Full list in
  `docs/13-content-manifest.md` §5. Wire to Steam achievements behind an interface so
  the backend is swappable.
- **Leaderboards:** Daily, Weekly, Monthly, All-Time, and Friends; across Distance,
  Score, Near Misses, Top Speed, and Highest Combo; filterable by mode and environment.
  Every entry stores the seed + input trace for ghost replay and anti-cheat validation.
- **Season Pass (optional, cosmetic only):** 50 tiers, free and premium tracks, 8-week
  seasons. Ships disabled behind a flag in v1; the data model must support it from day
  one so it is never a retrofit.

---

## 15. AUDIO

**Full spec in `docs/07-audio.md`.** Requirements:

- **Engine audio is granular/RPM-crossfaded multi-layer**, not a single pitched loop.
  Per vehicle: on-load and off-load (overrun) sample sets across at least 6 RPM bands,
  crossfaded by RPM with load-based blending between the two sets. Plus separate layers
  for intake, exhaust, turbo spool, blow-off, supercharger whine, transmission whine,
  differential, and idle. Distinct sample sets per engine family (I4, I6, V6, V8, V10,
  V12, flat-6, rotary, electric).
- **Electric vehicles get their own model:** inverter whine mapped to torque and speed,
  regen tone, and no gearshifts. They must feel and sound *alien* next to the V8s.
- **Speed-dependent audio bed:** wind noise (level + low-pass tied to speed), tire road
  noise per surface type (asphalt, concrete, wet, gravel, snow, rumble strip), and
  suspension/chassis creak on bumps.
- **The near-miss whoosh is the signature sound of the game.** Doppler-shifted, panned,
  ducking everything else by 4 dB for 200 ms. Layer it: a low body-mass "thump" of
  displaced air plus a high-frequency air-shear hiss. Vary by traffic vehicle size —
  a semi-truck pass must be physically intimidating.
- **Adaptive music:** stem-based (drums / bass / harmony / lead / tension), with stems
  layering in by speed tier and combo level, a dedicated tension stem during police
  pursuit that rises per wanted star, and a beat-synced transition on run end. Music
  must duck and low-pass under nitrous and near misses.
- Full spatial audio with HRTF option, occlusion in tunnels (with reverb send and a
  hard low-pass on exterior sources), and distinct reverb zones per environment.
- Crash audio: layered by impact energy and material pair — metal/metal, metal/plastic,
  glass shatter, panel deformation groan, plastic scatter, and a low sub-impact.
- Mixing: a proper bus/submix hierarchy with sidechain ducking, and 6 volume sliders
  (Master, Engine, SFX, Music, UI, Ambience). Full dynamic range by default, plus a
  Night Mode compressor option.

---

## 16. UI AND UX

**Full screen flows and wireframes in `docs/08-ui-ux.md`.**

**Design language:** dark, high-contrast, minimal chrome. One accent color per
environment. Motion is fast (140–220 ms) and eased, never bouncy. Every element that
can be selected has a hover, focus, press, and disabled state. Full keyboard and
gamepad navigation with a proper focus model — the mouse is never required.

**Screens:** Boot → Main Menu → Mode Select → Map Select → Car Select → Garage
(Customize / Upgrade / Paint / Preview) → Shop → In-Run HUD → Pause → Results →
Career → Challenges → Achievements → Leaderboards → Statistics → Settings →
Photo Mode → Replay Theater.

**HUD (all elements individually toggleable, scalable 50–200%):**
speedometer (digital + arc, unit-switchable), gear, tachometer arc, nitrous meter,
combo multiplier with its shrinking ring, live score, distance, run timer, mode-specific
widget (fuel / clock / wanted stars), near-miss popups (world-space), a minimal
rear-traffic indicator, and a damage state indicator. Default HUD occupies the bottom
14% and the top-right corner only — the road stays clear.

**Garage:** turntable with a real studio lighting rig, an animated door-open reveal on
first unlock, live paint preview with material response, a stat comparison bar against
the currently equipped car, and a "test drive in Free Ride" button on every car
including locked ones (a 60-second demo — this sells cars better than any stat sheet).

**Results screen:** counting payout, run graph of speed over distance, near-miss
timeline, best-moment auto-clip, new-record callouts, mission progress deltas, and
`R` to restart / `Enter` to continue. Fully readable in under 4 seconds.

---

## 17. PERFORMANCE TARGETS AND OPTIMIZATION

**Full budgets in `docs/11-optimization.md`.** These are acceptance criteria, not goals.

| Tier | Hardware | Target | Resolution |
|---|---|---|---|
| Low | GTX 1050 Ti / Ryzen 3 | 60 fps | 1080p, upscaled from 720p |
| Medium | GTX 1660 / RX 5600 | 60 fps | 1080p native |
| High | RTX 3060 / RX 6600 | 90 fps | 1440p |
| Ultra | RTX 4070+ | 120 fps | 1440p–4K |
| Steam Deck | — | 45 fps locked | 800p, FSR |

**Frame budget at 120 fps (8.3 ms):** game thread ≤ 3.2 ms, render thread ≤ 3.2 ms,
GPU ≤ 8.0 ms, physics ≤ 1.6 ms, audio ≤ 0.4 ms, AI ≤ 0.9 ms (time-sliced), traffic
spawn/despawn ≤ 0.2 ms amortized.

**Required:** DLSS + FSR 3 + XeSS, dynamic resolution scaling, aggressive LOD with
screen-size-driven transitions and dithered crossfade, occlusion culling, GPU
instancing for all roadside scatter, HISM for repeated road furniture, texture
streaming with a hard pool budget, fully async chunk generation and asset loading,
worker-thread traffic AI, object pooling for every runtime-spawned actor (traffic,
particles, decals, debris, audio components, UI popups), zero per-frame heap allocation
in the gameplay hot path, and a strict decal/particle budget with distance-based
culling.

**Hard rules:**
- **No hitches. Ever.** A single 40 ms spike at 280 km/h kills a run and is a
  ship-blocking bug. Profile chunk generation, asset loads, and shader compilation
  specifically for this. Precompile and warm the full PSO cache at first boot behind a
  progress bar.
- Loading a run must take under 3 seconds from a warm cache.
- Memory ceiling: 6 GB RAM, 4 GB VRAM at High.

---

## 18. ACCESSIBILITY

Not optional, not a post-launch patch. Ship all of it:

Colorblind modes (protanopia, deuteranopia, tritanopia) applied to *gameplay-relevant*
UI, not a naive full-screen filter · fully remappable controls on every device ·
toggle-vs-hold for every hold action · adjustable steering assist strength (0–100%) ·
lane-snap toggle · one-handed control scheme · subtitles for all dialogue and radio
chatter with size, background opacity, and speaker labels · captions for
gameplay-critical sounds (siren direction, near miss, damage) · motion blur toggle ·
camera shake slider (0–100%) · screen-flash intensity slider · FOV slider (60–110°) ·
HUD scale (50–200%) and per-element toggles · text scale (75–200%) with a dyslexia-
friendly font option · a high-contrast HUD mode · time-dilation toggle for the near-miss
slow-mo · reduced-particles mode · an assist preset that lowers traffic density and
raises collision forgiveness without disabling leaderboards (flagged separately) ·
photosensitivity mode that disables flashing (police lights, lightning, combo flashes)
and clamps bloom.

---

## 19. TECHNICAL ARCHITECTURE

**Full module contracts, event list, and folder layout in
`docs/02-technical-architecture.md`.**

**Stack (v1):** Unreal Engine 5.6 · C++ for all systems and gameplay · Blueprints only
for content wiring, VFX, and UI binding (never for logic) · Chaos Vehicles (extended
with a custom arcade layer) · Enhanced Input · MetaSounds · UMG + CommonUI · Mass Entity
or a custom pooled system for distant traffic · Behavior Trees + a custom lightweight
FSM for near traffic · EQS for police positioning queries only — intercept points,
roadblock placement, boxing formations, the one place a spatial query beats hand-rolled
logic; ordinary traffic does not need it and must not pay for it · Data Assets + JSON
for content · Epic Online Services for post-launch networking · Git + Git LFS ·
GitHub Projects for tracking, with its milestones mirroring §20 one-to-one.

*(Engine-agnostic mapping to Unity and Godot is in
`docs/02-technical-architecture.md` §9, in case of a stack change. Every specification
in these documents is engine-independent except where explicitly noted.)*

### 19.1 Modules (22)

`GameManager` · `WorldManager` · `RoadGenerator` · `TrafficManager` · `VehicleController`
· `PhysicsManager` · `AIManager` · `PoliceManager` · `CameraManager` · `AudioManager` ·
`UIManager` · `InputManager` · `SaveManager` · `EconomyManager` · `MissionManager` ·
`AchievementManager` · `WeatherManager` · `TimeOfDayManager` · `GraphicsManager` ·
`EffectsManager` · `ReplayManager` · `AnalyticsManager`

### 19.2 Architecture rules

1. **Event-driven.** Modules communicate through a typed `EventBus`. A module may
   directly reference at most one other module, and only downward in the dependency
   graph. No module may reach into another's internal state.
2. **Data-driven.** All content — vehicles, environments, modes, missions,
   achievements, upgrades, weather, traffic profiles, audio maps — lives in data files
   validated against JSON Schema at build time. Adding a car, a mode, or an environment
   must require **zero code changes**. Test this claim explicitly.
3. **Pooled.** Anything spawned more than once per second is pooled with a pre-warmed
   pool sized from measured peak.
4. **Deterministic.** All gameplay randomness draws from a seeded PRNG owned by
   `GameManager`. Never call unseeded random in gameplay code. Ever.
5. **Async.** Chunk generation, asset loading, and save I/O never block the game thread.
6. **Testable.** Physics, scoring, economy, mission evaluation, and road generation must
   run headless with no rendering, for automated tests.
7. **Documented.** Every public type gets a doc comment naming its pillar (§2), its
   owner module, and its events. Every magic number lives in a named data asset field
   with a comment explaining its unit and range.

### 19.3 Repository layout

```
/Source/HighwayRush/
  Core/          GameManager, EventBus, SeededRandom, Pooling, SaveSystem
  World/         RoadGenerator, ChunkStreamer, FloatingOrigin, Environments
  Traffic/       TrafficManager, DriverAI, Personalities, SpawnSolver, Police
  Vehicle/       VehicleController, Physics, Transmission, Damage, Upgrades
  Camera/        CameraManager, CameraModes, SpeedRig, Shake, PhotoMode
  Audio/         AudioManager, EngineAudio, AdaptiveMusic, Mixing
  UI/            UIManager, HUD, Menus, Garage, Results
  Progression/   Economy, Missions, Achievements, Leaderboards, SeasonPass
  Systems/       Weather, TimeOfDay, Graphics, Effects, Replay, Analytics
  Tests/         Automation tests, headless sim harness
/Content/        Art, audio, blueprints, UI assets
/data/           JSON content + schemas  (vehicles, environments, modes, missions…)
/docs/           Full specifications
/Tools/          Build, validation, content pipeline scripts
```

---

## 20. DEVELOPMENT MILESTONES

Build in this order. **Do not start a milestone until the previous one's acceptance
criteria pass.** Each milestone ends with a playable build.

| # | Milestone | Deliverable | Acceptance criteria |
|---|---|---|---|
| **M0** | Project setup | Repo, engine project, CI, LFS, coding standards, EventBus, SeededRandom, pooling, headless test harness | CI builds and runs tests on push |
| **M1** | Drive a box | One grey-box car, flat infinite road, arcade physics, 3rd-person camera, throttle/brake/steer | The box is *fun to drive* for 60 s. This is a hard gate — do not proceed until it is |
| **M2** | The road | Chunk streaming, splines, floating origin, lane system, 2–6 lanes, 1 grey-box environment | 30 minutes of driving with zero hitch and zero precision artifact |
| **M3** | Traffic | Spawner, solvability check, IDM following, lane changes, personalities, pooling, LOD | 10-minute run: traffic never feels scripted, never spawns unsolvable |
| **M4** | The verb | Collisions, near-miss detection, combo, scoring, full feedback stack, run start/end, instant restart | A tester says "one more run" unprompted |
| **M5** | Shell | HUD, main menu, mode select, results, pause, settings, save/load | Complete loop: menu → run → results → menu, saved across restarts |
| **M6** | Feel | 8 cameras, speed rig, all post-process, damage tiers, particles, controller rumble, screen shake | Side-by-side with M4: unrecognizably better at identical physics |
| **M7** | Sound | Full engine audio model, wind/road, near-miss whoosh, crashes, adaptive music, mixing | Playable and satisfying with eyes closed for 10 s |
| **M8** | Modes | All 15 modes as data, modifier system, Two-Way, Time Trial, Fuel, Hardcore, No Brakes | Adding a 16th mode requires only a JSON file |
| **M9** | Police | Wanted system, all unit types, roadblocks, spikes, helicopter, radio chatter, escape logic | A 5-star chase is the most exciting thing in the game |
| **M10** | Progression | Currencies, driver level, unlock tree, shop, missions, achievements, statistics | First-hour cadence hits the §14 target, measured |
| **M11** | Garage | Full visual + performance customization, turntable, live preview, test drive | Every option in §13 works and is visible on the car |
| **M12** | Content: cars | All 80 vehicles with interiors, audio, LODs, data, handling identity | Blind handling test: testers identify class from driving alone |
| **M13** | Content: worlds | All 14 environments, 9 weather states, 8 TOD presets, full transitions | Every environment × weather × TOD combination is shippable |
| **M14** | Meta | Leaderboards, replays, ghosts, dailies, weeklies, cloud save, Photo Mode | Daily Challenge is reproducible from seed across machines |
| **M15** | Optimize | Hit every §17 target on every tier, upscalers, PSO cache, memory budgets | 30-minute capture at each tier with zero frame over budget |
| **M16** | Accessibility | Every §18 item | Full playthrough with each mode enabled |
| **M17** | Polish & ship | Localization, telemetry, crash reporting, tutorial, balance pass, bug burn-down | Zero P0/P1 bugs; balance validated against §14 curve |
| **M18+** | Post-launch | Multiplayer (ghost races → live convoys), seasons, cross-platform | Networking layer isolated behind an interface from M0 |

**On M0's networking requirement:** "isolated behind an interface" is not a plan unless
the interface exists. `docs/15-networking-multiplayer.md` §1 defines the four interfaces
— identity, cloud save, leaderboards, sessions — that must ship in M0 with working null
implementations, so that 1.3 is a feature rather than a rewrite. `T-NET-01` asserts the
whole game plays on the null implementations.

---

## 21. DEFINITION OF DONE

Test IDs referenced below are defined in `docs/14-testing-qa.md` §2, and
`docs/00-index.md` §1 maps every requirement in this document to the tests that prove
it. A requirement with no test is not done — it is hoped for.

A feature is done only when **all** of the following are true:

- [ ] It serves a named pillar from §2, stated in the code
- [ ] It is data-driven where §19.2 rule 2 requires
- [ ] It holds the §17 frame budget on the Low tier
- [ ] It has zero per-frame allocations in the hot path
- [ ] It works with keyboard, gamepad, and wheel
- [ ] It respects every relevant §18 accessibility setting
- [ ] It is deterministic under a fixed seed, if it touches gameplay
- [ ] It saves and loads correctly, if it has state
- [ ] It has a headless automated test, if it is a system
- [ ] It has no hardcoded strings — everything goes through the localization table
- [ ] It has been played for 10 minutes by someone who did not write it
- [ ] Public API is documented, magic numbers are named data fields with units
- [ ] The build runs and the game is playable

---

## 22. THE FINAL TEST

Before calling any build good, run this. It is the only test that matters:

> Hand the build to someone who has never seen it. Say nothing except "drive."
> Start a timer.
>
> - Did they lean in within 30 seconds?
> - Did they say something out loud during their first near miss?
> - When they crashed, did they hit restart before the results screen finished?
> - After run three, did they look at the garage without being told to?
> - At the ten-minute mark, did you have to ask for the controller back?

**Five yeses ships. Anything less means go back to M1 and fix the feel — because
everything in this 22-section document is worthless if the car isn't fun to drive
on an empty road.**
