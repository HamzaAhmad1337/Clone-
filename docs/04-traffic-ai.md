# 04 — Traffic AI and Police AI

The goal: traffic that behaves like *people driving badly*, never like a spawner.
Players must be able to read intent, predict behavior, and be occasionally surprised by
a mistake that is nonetheless plausible.

---

## 1. Architecture

Three tiers by distance from the player, each with a different cost:

| Tier | Distance | Update rate | Model |
|---|---|---|---|
| **Near** | 0–150 m | Every frame | Full physics, full behavior FSM, animation, audio |
| **Mid** | 150–350 m | Every 4 frames | Kinematic motion, simplified behavior, no animation |
| **Far** | 350 m+ | Every 16 frames | Spline-follow with a speed value only |

Transitions must be invisible: when promoting Mid→Near, initialize the physics body
from the kinematic state including velocity and yaw rate, and blend the visual
transform over 2 frames.

AI runs on a worker thread against a double-buffered world snapshot. Decisions are
written to a command buffer applied on the next game tick.

---

## 2. Driver personalities

Rolled at spawn, fixed for the vehicle's lifetime. Every parameter is a multiplier on
the base behavior.

| Personality | Weight | Target speed | Following dist | Lane-change eagerness | Reaction time | Blinkers | Notes |
|---|---|---|---|---|---|---|---|
| **Timid** | 12% | 0.82× | 2.4× | 0.3× | 1.10 s | Always, early | Brakes for nothing. Causes jams |
| **Normal** | 34% | 1.00× | 1.0× | 1.0× | 0.85 s | Usually, late | Baseline |
| **Hurried** | 16% | 1.14× | 0.7× | 1.6× | 0.70 s | Sometimes | Weaves, tailgates |
| **Aggressive** | 12% | 1.22× | 0.5× | 2.1× | 0.60 s | Rarely | Cuts in, brake-checks |
| **Distracted** | 10% | 0.94× | 1.3× | 0.6× | 1.45 s | Rarely | Drifts in lane ±0.5 m, late reactions |
| **Erratic** | 6% | 0.90–1.25× (varies live) | 0.6–1.8× | 1.8× | 0.55–1.5 s | Never | Random speed and lane changes |
| **Professional** | 8% | 1.02× | 1.4× | 0.8× | 0.65 s | Always, correctly | Trucks and buses. Smooth, predictable |
| **Learner** | 2% | 0.75× | 2.0× | 0.4× | 1.30 s | Always, then forgets to cancel | Very slow, hesitant merges |

Per-environment overrides: the Japanese Expressway raises Professional and Timid;
Cyberpunk City raises Aggressive and Erratic; American Interstate raises Hurried and
truck density; the European Motorway has the fastest left-lane speeds and the best
lane discipline (slow traffic actually keeps right).

---

## 3. Behavior FSM

```
                ┌─────────────┐
        ┌──────▶│ LANE_KEEP   │◀────────────┐
        │       └──┬───┬───┬──┘             │
        │          │   │   │                │
        │  ┌───────┘   │   └────────┐       │
        │  ▼           ▼            ▼       │
        │ FOLLOW    CHANGE_LANE   YIELD ────┘
        │  │           │            (emergency vehicle,
        │  ▼           ▼             merging traffic)
        │ BRAKE     OVERTAKE
        │  │           │
        │  ▼           │
        │ EMERGENCY_STOP
        │  │
        │  ▼
        └ BREAKDOWN / CRASHED  (becomes a static hazard)
```

### 3.1 LANE_KEEP
Steer toward the lane centerline with a pure-pursuit controller, lookahead
`= clamp(speed * 0.9, 8, 40)` metres. Add per-personality lateral noise: a low-frequency
sine of amplitude 0.05–0.5 m so nobody tracks a perfect line.

### 3.2 FOLLOW — Intelligent Driver Model

```
desiredGap = minGap + max(0, v*T + (v*Δv) / (2*sqrt(a*b)))
accel      = a * [ 1 - (v/v0)^4 - (desiredGap/actualGap)² ]

minGap = 2.0 m · personalityFollowMul
T      = 1.4 s · personalityFollowMul      (desired time headway)
a      = 1.8 m/s²  (comfortable acceleration)
b      = 2.4 m/s²  (comfortable deceleration)
v0     = target speed · personalitySpeedMul · weatherMul
```

IDM is the right choice here: it produces realistic emergent behavior including
stop-and-go waves and traffic jams that form and dissolve on their own, with four
parameters. Do not hand-roll a follower.

### 3.3 CHANGE_LANE — gap acceptance

```
canChange = targetLaneGapAhead  > requiredAhead
         && targetLaneGapBehind > requiredBehind
         && |lateralClearance to player| > 1.6 m      // see the Near-Miss Contract
         && !behaviourLocked
         && timeSinceLastChange > 3.0 s / eagerness

requiredAhead  = 8 + v*0.6 / eagerness      metres
requiredBehind = 6 + Δv_behind*1.1 / eagerness
```

Execution: blinker on (per personality) → 0.4–1.2 s delay (per personality) → lateral
transition over 1.6–3.2 s with an S-curve, never a linear slide → blinker off (unless
Learner).

**Abort:** if the gap closes during the transition, a Timid/Normal/Professional driver
aborts and returns; an Aggressive driver commits and forces the merge, which is what
creates the good emergent drama.

### 3.4 OVERTAKE
Trigger when blocked by a vehicle more than 12% slower for over 2.5 s and an adjacent
faster lane is available. Change lane, accelerate to `targetSpeed * 1.08`, pass, and
return only if `Professional` or `Timid` (others camp the lane — realistically
annoying, and it creates the blocked-lane situations the player must solve).

### 3.5 Mistakes and hazards
| Event | Trigger | Effect |
|---|---|---|
| Phantom braking | Distracted/Timid, 0.4%/s when a vehicle is within 30 m | Brakes 40% for 1.2 s with no cause. Propagates a stop-wave backward — this is real, and it looks amazing |
| Brake check | Aggressive, when tailgated for >2 s | Hard brake for 0.8 s |
| Missed merge | Learner/Distracted | Aborts mid-lane-change, straddles the line for 1.5 s |
| Breakdown | 0.1% per vehicle per minute | Hazards on, decelerates, pulls to shoulder, becomes a static hazard for 45 s |
| Collision | Emergent, from the above | Two vehicles become a pileup hazard. Others slow and merge around it. Persists 60 s |
| Debris | Environment-driven | Tire carcass, cargo, cone. Static hazard |

Hazards are the best content in the game and they cost nothing — they arise from the
simulation. Make sure they are visible from at least 4.0 s away (§6.3).

### 3.6 Signalling — blinkers are a fairness system

Indicators are not decoration. They are the player's only advance warning that a gap is
about to close, which puts them in the same category as brake lights: **a readability
guarantee, not a graphical feature.**

#### Rendering requirements
- **Visible to 500 m, at every quality tier, always.** Same rule as brake lights
  (§7). Culling an indicator is a fairness bug, not an optimization.
- Flash rate **1.5 Hz** (90 flashes/min), 50% duty cycle. All vehicles flash at the same
  rate — a real fleet varies slightly, but synchronised rate reads more clearly at speed
  and this is a legibility system first.
- Emissive material + a small light source within 90 m; emissive only beyond that; at
  350 m+ the imposter keeps a single emissive quad per side. The blink must survive
  every LOD transition.
- Amber, high contrast against every environment's lighting. In Snow and Fog, boost
  emissive intensity by 40% — an indicator that vanishes in the weather that most needs
  it is the worst possible failure.

#### Signal timing
```
intent formed → indicator ON → holdDuration → lateral movement begins
                                            → movement completes → indicator OFF

holdDuration by personality:
  Professional  1.2 s      (correct, generous)
  Timid         1.1 s
  Learner       1.4 s, then forgets to cancel for 3–8 s after completing
  Normal        0.7 s      (late, but present)
  Distracted    0.5 s      (very late)
  Hurried       0.4 s      (barely a courtesy)
  Aggressive    0.0 s      (60% of the time: no signal at all)
  Erratic       never
```

**Design intent:** `Professional`, `Timid`, and `Normal` cover 54% of traffic, so the
majority of lane changes *are* telegraphed. The unsignalled minority is what makes the
road feel alive and keeps the player reading body language — a car drifting toward a
lane line is still a cue, even with no indicator. But the player must never be able to
say "nobody ever signals," because at that point the indicator system has taught them
to ignore it.

#### Hazard lights
Both indicators, same 1.5 Hz, on for: breakdowns, pileups, emergency stops, and any
vehicle stationary on the carriageway. Hazards are the highest-priority visual signal in
the game after brake lights and must be visible at the full 5.0 s hazard sightline
(§6.3).

#### Player indicators
- **Auto mode (default):** indicator activates automatically on a committed lane change
  and cancels on completion. Zero input cost, full immersion benefit.
- **Manual mode:** bound to keys, for players who want it. Purely cosmetic — no
  gameplay effect, and explicitly *not* required for the Courtesy Flash in §3.7.
- Never punish a player for not signalling. This is an arcade game about speed, not a
  driving test.

### 3.7 The Courtesy Flash — asking traffic to move

Flashing your headlights at a car ahead asks it to move over. This is real motorway
behaviour: across continental Europe the keep-right rule is a legal duty, and flashing
the high beams is the standard signal that faster traffic wants through.

It is also the only mechanic in the game where the player influences traffic *without*
steering, and that makes it the second skill axis.

#### Input and detection
```
Input:      Flash high beams — tap. Default F (keyboard) / LB (gamepad) / wheel button.
Cooldown:   2.5 s global
Detection:  the nearest traffic vehicle whose bounds intersect the player's current lane
            (or the lane the player is steering toward), between 25 m and 110 m ahead
Requires:   player speed > 60 km/h, and closing speed > 15 km/h
```

Only **one** vehicle responds per flash — the nearest. Flashing does not clear a lane,
it asks one driver.

#### Response by personality

| Personality | Yields | Response delay | On refusal |
|---|---|---|---|
| Professional | 95% | 0.6 s | Holds line, signals, moves at first safe gap |
| Timid | 90% | 1.1 s | May also brake slightly — a hazard in itself |
| Normal | 75% | 0.9 s | Holds |
| Learner | 70% | 1.4 s | Moves clumsily, may straddle the line for 1.5 s |
| Hurried | 45% | 0.7 s | Holds, closes the gap ahead |
| Distracted | 35% | 1.6 s | Usually does not notice |
| Erratic | 25% | 0.4–2.0 s | Unpredictable — may swerve the wrong way |
| Aggressive | 10% | — | **15% chance of a brake-check in retaliation** |

A yielding vehicle performs a normal `CHANGE_LANE` with its personality's blinker
discipline (§3.6). **All the usual gap-acceptance rules still apply** — a driver who
wants to move but has nowhere to go stays put, and that refusal must read as physical
constraint, not rudeness. Show the indicator anyway: it is signalling intent it cannot
yet act on.

#### Environment modifier

| Environment | Yield multiplier | Why |
|---|---|---|
| European Motorway | ×1.25 | Keep-right is a legal duty; lane discipline is real |
| Japanese Expressway | ×1.15 | High courtesy norms |
| Countryside, Coastal, Forest | ×1.05 | Relaxed, cooperative |
| American Interstate, Desert, Snow, Mountain, Industrial, Airport | ×1.00 | Baseline |
| Modern City, Middle Eastern Highway | ×0.85 | Denser, more assertive |
| Cyberpunk City | ×0.60 | Nobody yields to anybody |

Clamped to [0.05, 0.98] — there is never a guarantee, and never a certainty of refusal.

#### The balance rules that stop it trivialising the game

This mechanic could ruin Highway Rush. If flashing clears the road for free, the optimal
strategy becomes "flash constantly," the traffic stops being an obstacle, and the near
miss — the entire point of the game — evaporates. Four rules prevent that:

1. **A yielded pass scores no near miss.** The car moved out of the way, so there is no
   proximity to reward. This is the load-bearing rule: the Courtesy Flash is a *safety
   valve that costs points*, never a scoring strategy. Threading the gap is always worth
   more than asking for it.
2. **It costs time you may not have.** At 300 km/h the player covers 83 m/s. A 0.9 s
   response plus a 1.6 s lane change is 2.5 s — over 200 m. The flash must be sent
   *early*, which means reading traffic two hundred metres out. That is a skill, and it
   is a different one from threading.
3. **Annoyance.** Flashing the same vehicle again within 6 s reduces its yield chance by
   30% per repeat and doubles the Aggressive brake-check chance. Spamming makes the road
   *more* hostile, exactly as it does in life.
4. **It cannot manufacture a gap.** Gap acceptance is unchanged, so the mechanic can
   never violate the solvability guarantee (§6) in either direction — it does not create
   space that physics forbids, and it never removes the threadable path the spawner
   already guaranteed.

#### Interactions
- **Police:** flashing at any police unit adds **+6 heat** and never causes a yield.
  Pursuit vehicles do not take orders.
- **Emergency vehicles:** never yield to a flash; the player yields to *them*.
- **Semi-trucks and buses:** yield chance ×0.7 and response delay +0.8 s. A 16.5 m
  vehicle needs a much bigger gap and takes far longer to cross a lane.
- **Two-Way mode:** flashing at oncoming traffic does nothing except look alarming.
- **Hardcore mode:** the Courtesy Flash is disabled entirely. No safety valve.
- **Night and Fog:** yield chance ×1.15 — a flash is far more visible in the dark.

#### Feedback
The flash must feel like an action even when it fails:
- Instant visual: headlight beams punch to high beam for 180 ms, twice, with the
  volumetric cones brightening.
- A soft relay click on the UI bus.
- When a vehicle *accepts*: its indicator comes on, and a small world-space
  acknowledgement marker appears above it for 0.8 s. The player must know the ask landed
  before the car has physically moved, or the mechanic feels unresponsive.
- When a vehicle *refuses*: nothing. Silence is the correct feedback for being ignored.
- On a retaliation brake-check: the target's brake lights flare hard and a distinct
  aggressive audio sting fires. The player has annoyed someone and should feel it.

---

## 4. The Near-Miss Contract (mandatory)

> Once the player's front bumper passes a traffic vehicle's rear bumper, that vehicle
> loses lane-change and hard-brake authority for **0.9 seconds**.

```cpp
// Called by the near-miss detector on the frame overlap begins.
void ATrafficVehicle::LockBehaviour(float Seconds);
bool ATrafficVehicle::IsBehaviourLocked() const;
```

Every action node in the behavior FSM checks `IsBehaviourLocked()` at its root and
falls through to `LANE_KEEP` with the current speed held.

Additionally: **no traffic vehicle may initiate a lane change into a lane the player
occupies or will occupy within 1.2 s**, at any time, regardless of lock state.
Predicted player position uses current velocity plus current steering input.

Without these two rules the game feels cheap. With them, every death is the player's.

---

## 5. Spawning

### 5.1 Distances
```
spawnAhead   = clamp(220 + playerSpeed_kmh * 0.75, 260, 420)   metres
despawnBehind = 140 m
despawnAhead  = 500 m   (vehicles that outran the player)
```

Never spawn within the player's visible frustum on clear road. Valid spawn conditions:
beyond a crest, around a curve with occluded sightline, beyond current fog distance,
inside a tunnel mouth, or beyond the far clip. If none is available, spawn at
`spawnAhead` with a 0.35 s opacity fade — but this is the fallback, not the norm.

### 5.2 Density

```
vehiclesPer100mPerLane = trafficDensity(d) * modeDensityMul * weatherDensityMul
                         * breathIntensity(t) * environmentDensityMul
```

`trafficDensity(d)` and `breathIntensity(t)` are defined in `docs/01-game-design.md` §2.

| Mode | `modeDensityMul` |
|---|---|
| Classic | 1.00 |
| Two-Way | 0.85 (per direction; total traffic is higher) |
| Rush Hour | 2.40 |
| Time Trial | 0.90 |
| Police Escape | 0.80 |
| Fog / Rain / Snow | 0.85 |
| Hardcore | 1.30 |
| Free Ride | 0.60 |

Weather multiplier: Rain 0.90, Storm 0.85, Fog 0.80, Snow 0.75, Blizzard 0.65,
Sandstorm 0.70 — fewer people drive in bad weather, and it compensates for reduced
sightline.

### 5.3 Vehicle type mix

Base distribution, overridden per environment:

| Type | Weight | Length | Width | Speed mul | Notes |
|---|---|---|---|---|---|
| Sedan | 26% | 4.7 m | 1.82 m | 1.00 | |
| Hatchback | 14% | 4.2 m | 1.78 m | 0.98 | |
| SUV | 16% | 4.8 m | 1.92 m | 0.97 | Blocks sightline |
| Pickup | 9% | 5.6 m | 2.00 m | 0.95 | |
| Van | 7% | 5.4 m | 2.05 m | 0.90 | Blocks sightline badly |
| Bus | 3% | 12.0 m | 2.55 m | 0.82 | Huge near-miss value |
| Semi truck | 8% | 16.5 m | 2.60 m | 0.80 | The scariest pass in the game |
| Sports car | 6% | 4.4 m | 1.88 m | 1.18 | Often Hurried/Aggressive |
| Luxury | 4% | 5.1 m | 1.90 m | 1.06 | |
| Motorcycle | 3% | 2.1 m | 0.75 m | 1.15 | Lane-splits |
| EV | 3% | 4.6 m | 1.85 m | 1.02 | Silent — a genuine hazard |
| Emergency | 1% | varies | varies | 1.25 | Others yield |

Semi trucks deserve special attention: they are the single best near-miss target
because of length and mass. Ensure their audio, air displacement, and the buffeting
force on the player (a brief 900 N lateral push toward the truck when passing within
1.2 m) are all implemented. That buffet is a signature moment.

### 5.4 Speed assignment
```
speed = normalDist(trafficSpeedMean(d), trafficSpeedSpread(d))
        * typeSpeedMul * personalitySpeedMul * weatherSpeedMul
clamped to [45, 165] km/h
```
Lane bias: in right-hand-traffic environments, the leftmost lane averages +14 km/h and
the rightmost −12 km/h, with trucks weighted heavily toward the right. Mirror for
left-hand-traffic environments (Japanese Expressway).

---

## 6. The solvability guarantee

**Rule:** at any moment, at the player's current speed, there must exist at least one
lateral path through the traffic ahead that is reachable within 2.5 seconds of
maximum-rate steering, with clearance ≥ `minGapClearance(d)`.

### 6.1 Algorithm (runs on a worker thread every 0.25 s)

```
1. Project all traffic within 400 m forward by 3.0 s using current velocity + intent.
2. Build a time-space occupancy grid: lanes × 0.25 s slices, out to 3.0 s.
3. Mark each cell occupied if any vehicle's swept bounds + minGapClearance(d) intersect it.
4. Flood-fill from the player's current (lane, t=0) cell, allowing lateral moves
   constrained by maxLateralRate(playerSpeed).
5. If no cell at t = 3.0 s is reachable → NOT SOLVABLE.
```

Cell occupancy uses `playerWidth + minGapClearance(d)` as the required opening, per
`docs/01-game-design.md` §2.1 — the clearance figure is spare room beside the car, not
the total opening.

### 6.2 Response to an unsolvable state
In priority order:
1. Delay the next scheduled spawn (cheapest).
2. Shift a not-yet-visible spawn to a different lane.
3. Instruct one Mid-tier vehicle to begin a lane change that opens a gap (must look
   natural — use a Hurried or Aggressive driver, with blinker).
4. Instruct one Mid-tier vehicle to accelerate 8% (invisible at distance).
5. Last resort: despawn one Far-tier vehicle that is not in view.

Never teleport, never fade out a visible vehicle, never brake the player.

### 6.3 The sightline guarantee
The player must always see at least **4.0 seconds of road** at current speed:
`requiredSightline = max(120, speed_ms * 4.0)` metres. Road curvature, crest height,
fog density, and spawn distance are all clamped against this. At 300 km/h that is
333 m. This constraint outranks visual interest, always.

Hazards (pileups, breakdowns, debris, roadblocks) require **5.0 seconds** because they
are static and require a full lane change under braking.

---

## 7. Traffic LOD detail

| Range | Physics | Behavior | Animation | Audio | Lights | Mesh LOD |
|---|---|---|---|---|---|---|
| 0–40 m | Full | Full | Full (wheels, suspension, driver) | Full 3D | All | LOD0 |
| 40–90 m | Full | Full | Wheels + suspension | Full 3D | All | LOD1 |
| 90–150 m | Full | Full | Wheels only | Simplified | Brake + indicators | LOD1 |
| 150–350 m | Kinematic | Simplified | Wheels only | Off | Brake only | LOD2 |
| 350 m+ | Spline | Speed only | Off | Off | Emissive only | LOD3 / imposter |

Brake lights must remain visible at *all* ranges out to 500 m — they are the player's
primary early-warning signal and cutting them for performance directly harms fairness.

---

## 8. Police AI

### 8.1 Wanted level

```
heat accumulates:
  +1.2/s while speed > 160 km/h
  +0.6/s while speed > 120 km/h
  +2.5   per near miss with a police unit
  +8.0   per contact with a police unit
  +4.0   per near miss with civilian traffic while pursued
  +15.0  per roadblock threaded
  +0.4/s baseline while pursued

heat decays:
  -3.0/s while out of any police line of sight
  -1.0/s while below 90 km/h and not in line of sight

star thresholds: 25 / 70 / 150 / 280 / 460
```

### 8.2 Units by star level

| Star | Units | Behavior |
|---|---|---|
| ★ | 1 interceptor sedan | Follows, calls position, no contact attempts |
| ★★ | 2 interceptors | Coordinated flanking, first PIT attempts |
| ★★★ | 3 interceptors + 1 SUV rammer | SUV attempts side-ramming, roadblock warnings |
| ★★★★ | 4 units + roadblocks + spike strips | Pre-positioned ahead, boxing formations |
| ★★★★★ | 6 units + heavy blockers + helicopter | Helicopter spotlight negates line-of-sight escape; ambushes at chunk boundaries |

### 8.3 Pursuit behavior
- **Intercept:** pursuit-curve steering toward the player's predicted position at
  `t = distance / closingSpeed`, not toward their current position.
- **PIT maneuver:** attempt when alongside the player's rear quarter for >1.2 s and
  relative speed < 25 km/h. Telegraph with 0.7 s of engine surge audio and a visible
  angle change before contact.
- **Boxing:** at ★★★+ with 3+ units and player speed <110 km/h, units take
  front/rear/side positions and squeeze.
- **Blocking formations:** at ★★★★+, two units abreast ahead, decelerating.

### 8.4 Roadblocks and spikes
- Roadblocks spawn 700–1,100 m ahead, always on a straight or gentle curve.
- **The gap is designed, never zero.** Width by star: ★★★ 4.2 m, ★★★★ 3.4 m,
  ★★★★★ 2.6 m. A hyper car is ~2.05 m wide — so ★★★★★ leaves 55 cm of total spare,
  about 27 cm per side, which is terrifying and threadable. Threading one awards +15
  heat and +800 points.
- Spike strips are deployed by a unit ahead and are **visible for ≥ 2.0 s** at current
  speed. Hitting them: instant tire deflation, −45% grip, −30% top speed, visible flat
  tire and sparks, and the run continues (this is a wound, not a death).
- A "PURSUIT AHEAD" HUD warning fires 4.0 s before any roadblock enters view.

### 8.5 Escape
- Break line of sight from all units and hold it for **12 s**, or
- Exceed **1.2 km** of separation from the nearest unit.
- The helicopter at ★★★★★ maintains line of sight regardless of cover — you must
  outrun it (its top speed is 240 km/h) or lose it in a tunnel (which is why tunnels
  are the best cover in the game and why the chunk grammar should offer them during
  pursuits).
- On escape: `PursuitEnded`, wanted decays to 0 over 6 s, a score award of
  `250 × stars²` (6,250 at five stars), and the music resolves rather than cutting.

### 8.6 Radio chatter
Procedurally assembled from a data table, never hardcoded strings. Slot grammar:

```
[dispatch_open] [unit_callsign] [action] [subject_desc] [location] [speed] [directive]

e.g. "Control, unit 4-1-2, in pursuit of a red coupe, northbound on the interstate,
      speed one-eight-five, requesting spike deployment."
```

Slots are filled from the live game state: the player's actual car color and body type,
the current environment, the current heading, the current speed bracket, and the star
level. Barks fire on state transitions (pursuit start, star up, roadblock deploy, spike
deploy, losing visual, regaining visual, PIT attempt, escape) with a 3.5 s minimum
spacing and priority-based interruption. Radio-filtered audio with squelch tails.

Budget ~180 recorded lines to cover the grammar. This is the highest atmosphere-per-
dollar content in the entire game.

---

## 9. AI acceptance tests (headless)

| Test | Assertion |
|---|---|
| Solvability | 10,000 seeded runs × 20 km: zero unsolvable states |
| Near-Miss Contract | 10,000 near misses: zero collisions caused by post-pass AI action |
| Emergent jams | Rush Hour at 20 km produces at least one stop-wave per 3 minutes |
| No pop-in | Zero spawns inside the player's frustum on clear road over 100 runs |
| Personality distinctness | Recorded traces for each personality are statistically separable |
| Determinism | Same seed = same traffic, positions identical after 10 min |
| LOD transitions | Zero position discontinuities > 5 cm across tier changes |
| Pool stability | Zero pool growth over a 60-minute run |
| Police gap | Every roadblock across 5,000 spawns has a threadable gap |
| Sightline | Zero frames where visible road < 4.0 s at current speed |
