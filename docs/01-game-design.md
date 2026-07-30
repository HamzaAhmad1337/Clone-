# 01 — Game Design Document

Companion to `PROMPT.md`. This document holds the design reasoning and the tuning
curves that `PROMPT.md` summarizes.

---

## 1. Design thesis

Traffic Racer-style games work because of a single psychological trick: **they convert
fear into currency.** The near miss is not a bonus mechanic — it is the entire game.
Distance and speed are just the delivery vehicle for near misses.

Every design decision in Highway Rush is evaluated against one question:

> *Does this make the player take a risk they would not otherwise have taken?*

Things that pass: combo multipliers, oncoming-lane bonuses, narrow gaps, fuel that
refills on near misses, a nitrous meter that recharges faster while comboing.

Things that fail: shields, revives, obstacle-free stretches, generous collision boxes,
anything that makes crashing cheap.

### 1.1 Where the genre leaves value on the table

| Genre weakness | Highway Rush's answer |
|---|---|
| Traffic behaves like moving walls | 8 driver personalities, real gap acceptance, mistakes, breakdowns, pileups |
| Every car feels the same with different stats | Handling identity mandate (§13 of PROMPT.md) — blind-identifiable by feel |
| Environments are reskins | Each biome changes traffic mix, road geometry grammar, and music |
| Progression is a coin wall | Unlock cadence curve (§4 below), missions, and multiple currencies |
| Speed is a number, not a sensation | The speed rig — 10 coupled effects (§12 of PROMPT.md) |
| One-note runs | 15 modes + composable modifiers + daily seeds |
| Crashing feels arbitrary | The Near-Miss Contract, telegraphed loss of control, guaranteed-solvable spawns |
| Audio is a looping engine sample | Multi-layer load-blended engine model, adaptive stems |

---

## 2. The difficulty curve

Difficulty is a function of **distance travelled in the current run**, not of player
level. Every run starts easy. This is essential: the ramp *is* the drama.

### 2.1 Ramp parameters (Classic Endless)

`d` = distance in km travelled this run.

```
trafficDensity(d)   = lerp(0.42, 1.00, clamp(d / 14, 0, 1))       // vehicles per 100 m per lane
trafficSpeedMean(d) = lerp(78, 112, clamp(d / 18, 0, 1))          // km/h
trafficSpeedSpread  = lerp(14, 34, clamp(d / 18, 0, 1))           // km/h std-dev — spread matters more than mean
aggressiveMix(d)    = lerp(0.10, 0.34, clamp(d / 12, 0, 1))       // fraction Aggressive/Erratic
minGapClearance(d)  = lerp(3.20, 1.55, clamp(d / 16, 0, 1))       // metres — see below
curveFrequency(d)   = lerp(0.15, 0.45, clamp(d / 20, 0, 1))       // fraction of chunks that are curves
hazardFrequency(d)  = lerp(0.00, 0.22, clamp((d - 3) / 15, 0, 1)) // construction, pileups, breakdowns
```

**`minGapClearance` is spare room, not total room.** The lateral opening the spawner
must leave is `playerWidth + minGapClearance`. For a 1.85 m car that is a 5.05 m
opening at the start of a run (trivially wide) narrowing to a 3.40 m opening by 16 km —
1.55 m of total spare, about 0.78 m per side, which sits just inside the 1.20 m
near-miss threshold on *both* sides. In other words, by 16 km the designed gap is a
double near miss. That is the intended late-run experience.

After 20 km everything is pinned at maximum and difficulty only rises through the
player's own speed. This is intentional — at that point the player is the difficulty.

### 2.2 Micro-pacing: the breath rhythm

Constant maximum pressure exhausts players and flattens the score curve. Overlay a
**breath cycle** on top of the ramp:

```
period    = 42 s  (jittered ±7 s so it is not learnable)
intensity = 0.72 + 0.28 * sin(2π * t / period)
applied to: trafficDensity, aggressiveMix
```

The trough gives the player 6–8 seconds to breathe, bank a lead, and re-read the road.
The peak is where combos die. Players will describe this as "waves of traffic" and
will not know why it feels good.

**Never** put a breath trough in the first 12 seconds of a run — the opening must be
clean acceleration so the player can build speed and buy into the run.

### 2.3 Failure pacing targets

| Player skill | Median run length | Median distance |
|---|---|---|
| First 3 runs | 45–70 s | 2.5–4 km |
| First hour | 2–4 min | 7–13 km |
| Experienced | 5–9 min | 22–40 km |
| Expert | 12+ min | 60+ km |

If new players die in under 30 seconds, the opening ramp is too steep. If experienced
players routinely exceed 20 minutes, the ramp caps too low — raise the late-game speed
spread, not the density (density becomes unfair; spread stays fair).

---

## 3. The near miss, in depth

### 3.1 Why 1.20 m

The clearance threshold must be wide enough that a *competent* pass registers, and
narrow enough that a *lazy* pass does not. Measured against typical geometry:

- Lane width: 3.65 m
- Player car width: ~1.85 m
- Traffic car width: ~1.80 m
- Two cars centered in adjacent lanes: 3.65 − (0.925 + 0.90) = **1.825 m clearance**

So a lazy centered-lane pass at 1.825 m does **not** score. The player must deliberately
shade toward the traffic — roughly 0.6 m of intentional commitment — to trigger it at
1.20 m. That commitment is the whole game. **Do not raise this number.**

The `Close` tier at 0.55 m requires the player to be nearly touching. It is worth ~2.5×
the base near miss and it is the moment players screenshot.

### 3.2 Scoring feel: super-linear on purpose

```
points = 30 × proximityMul × speedMul × oncomingMul × laneSplitMul × comboMul
```

Worked examples:

Combo counts below are the HUD `×N`; the multiplier applied is `1 + 0.5N`
(`PROMPT.md` §8.2).

| Scenario | prox | speed | onc | split | comboMul | Points |
|---|---|---|---|---|---|---|
| Lazy pass, 1.15 m, 90 km/h, no combo | 1.08 | 1.15 | 1.0 | 1.0 | 1.0 | **37** |
| Committed pass, 0.70 m, 200 km/h, ×5 combo | 1.83 | 2.00 | 1.0 | 1.0 | 3.5 | **385** |
| Close pass, 0.40 m, 280 km/h, oncoming, ×12 combo | 2.33 | 2.62 | 2.0 | 1.0 | 7.0 | **2,563** |
| Lane split, 0.35 m, 300 km/h, oncoming, ×20 combo | 2.42 | 2.77 | 2.0 | 1.5 | 11.0 | **6,637** |

A ~180× spread between the worst and best near miss. That spread is what makes mastery
feel like mastery, and it is why the combo must be fragile.

### 3.3 The Near-Miss Contract, restated

Once the player's front bumper passes a traffic vehicle's rear bumper, that vehicle
loses lane-change and hard-brake authority for **0.9 s**.

Implementation: `ATrafficVehicle::LockBehaviour(0.9f)` called from the near-miss
detector on the same frame the overlap begins. The AI's behavior tree checks
`IsBehaviourLocked()` at the root of every action node.

**Rationale:** without this, a player who correctly read a gap and committed can still
be killed by a lane change they could not have predicted. That single experience,
repeated three times, makes players quit. With the contract, every death is legible.

### 3.4 Anti-exploit rules

- Cooldown of 1.5 s per traffic instance prevents oscillating alongside one car.
- The pass must be a **true pass** — longitudinal overlap must cross from ahead to
  behind. Sitting alongside at matched speed scores nothing.
- Relative speed > 22 km/h prevents convoy-crawling exploits.
- Near misses against vehicles the player is *contacting* score zero and break combo.
- Off-road driving suppresses all near-miss scoring after 1.5 s off the drivable
  surface — no farming the shoulder.

---

## 4. Progression cadence

The target is that the player is **always 3–8 minutes from something**.

### 4.1 First-hour script (designed, not emergent — verify by playtest)

| Time | Event |
|---|---|
| 0:00 | Run 1 starts immediately. No menu, no logo gate. Starter car, Countryside, day, clear |
| 0:02 | Contextual prompts fade in and out during the first run only |
| 0:03 | First unlock: Classic Endless leaderboards + Car #2 (Economy) affordable |
| 0:08 | Environment 2 unlocks (Modern City) |
| 0:12 | First upgrade purchase possible (Engine T1) |
| 0:15 | Two-Way mode unlocks — the first *real* difficulty spike and the first ×2 payout |
| 0:22 | Car #3 (Hot Hatch) affordable — first car that changes handling noticeably |
| 0:30 | Daily Challenge introduced |
| 0:38 | Time Trial unlocks |
| 0:45 | Car #4 (Sports) affordable — first genuinely fast car |
| 0:52 | Police Escape unlocks. Night mode unlocks |
| 1:00 | Player has 4 cars, 3 environments, 4 modes, ~12 upgrades, driver level ~8 |

### 4.2 Long-tail cadence

| Play hours | Minutes per meaningful unlock |
|---|---|
| 0–1 | 8 |
| 1–4 | 18 |
| 4–12 | 30 |
| 12–28 | 55 |
| 28–48 | 85 |
| 48+ | Prestige, seasons, leaderboards, and self-directed goals |

**Grind guard:** no single unlock may cost more than 90 minutes of median-skill play.
If the economy math produces one, split it into stages or lower the price. Verify this
programmatically in the economy test suite — it is a build-failing assertion.

---

## 5. Onboarding

**There is no tutorial screen.** The first run *is* the tutorial.

- Run 1 uses a locked-down ruleset: 0.55× density, no curves, clear weather, day, a
  forgiving car, and a 30% wider near-miss threshold that is silently restored to
  normal on run 2.
- Contextual prompts appear as small world-space hints, shown once each, never
  repeated: `W to accelerate` → `A / D to change lanes` → (after the first organic near
  miss) `NEAR MISS — pass close for bonus cash` → `SHIFT for nitrous`.
- If the player crashes in under 20 s on run 1, run 2 silently repeats the tutorial
  ruleset. Maximum 3 repeats, never announced.
- A full "Driving School" exists in the menu for players who want it — 8 short drills
  (lane change, threading, oncoming, braking zones, nitrous timing, police evasion, wet
  grip, combo maintenance), each paying a small Cash reward. Optional, never forced.

---

## 6. Session and retention design

**Daily Challenge** — the retention backbone. One fixed seed per UTC day, globally
identical, one scored attempt (plus unlimited unscored practice on the same seed —
this is a deliberate generosity that makes the mode about execution, not luck).
Fixed car, fixed environment, 2–3 composed modifiers. Rewards: Cash + Tokens + a
dedicated daily leaderboard. Streak bonus at 3/7/14/30 days.

**Weekly Event** — a 4-stage ladder released Monday, themed (e.g. "Blizzard Run",
"Neon Night", "Convoy Chaos"). Cumulative objectives. Rewards a cosmetic item that
cannot be bought.

**Monthly Event** — a large themed ladder with a vehicle unlock at the end. The vehicle
becomes purchasable for Coins three months later so nothing is permanently missable.

**Login rewards** — 28-day cycle, resets on miss but keeps the highest tier reached.
Coins, Cash, Tokens, and a cosmetic on day 28.

---

## 7. Anti-frustration rules (all mandatory)

1. **The guaranteed gap.** Every spawn wave must contain a threadable path. Verified at
   spawn time by the solvability check (`docs/04-traffic-ai.md` §6).
2. **The Near-Miss Contract** (§3.3).
3. **Telegraphed loss of control.** 250 ms of audio + camera + rumble warning before
   grip is actually lost.
4. **No blind hazards.** 4.0 s of sightline minimum. Fog, crests, and curves are all
   clamped against it.
5. **Fair collision volumes.** The player's collision box is inset 6 cm from the visual
   mesh on all sides. Traffic boxes match their meshes exactly. The player always gets
   the benefit of the doubt.
6. **Glancing-blow forgiveness.** Contact under 12 km/h relative speed and under 20° of
   incidence produces a scrape — cosmetic damage, combo break, but not a run end.
7. **The 0.4 s grace window.** After any run-ending contact, if the player was already
   steering away for 0.4 s prior, downgrade to a heavy scrape once per run. This is
   invisible to the player and removes the "I already fixed it!" death.
8. **Instant restart.** One key, under 1.5 s, no confirmation, no animation.
9. **Nothing is permanently missable.** Every event item returns via a later route.
10. **The run is never wasted.** Even a 10-second crash pays out coins, XP, and mission
    progress.

---

## 8. Balance validation (automated)

These run headless in CI and fail the build:

| Assertion | Threshold |
|---|---|
| No unlock exceeds 90 min of median-skill income | Hard fail |
| First-hour unlock count | ≥ 4 cars, ≥ 2 environments, ≥ 3 modes |
| Every car is reachable without premium currency | Hard fail |
| Every mode's median run length | Within 40% of its design target |
| Simulated 10k runs: no seed produces an unsolvable spawn | Hard fail |
| Near-miss share of expert score | 70–95% |
| No upgrade tier grants > 18% of a stat in one step | Hard fail |
| Token-purchasable items affecting stats | Must be zero |
