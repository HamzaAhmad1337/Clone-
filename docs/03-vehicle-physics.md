# 03 — Vehicle Physics and Handling

Arcade physics with a simulation skeleton. The model is real enough that vehicles feel
distinct and weight transfer reads visually, and fake enough that a keyboard player can
hold 300 km/h through a sweeper.

---

## 1. Solver

- Fixed substep at **120 Hz** minimum (240 Hz above 250 km/h — at 300 km/h a car
  travels 0.69 m per 120 Hz tick, which is enough to tunnel through thin collision).
- Continuous collision detection on the player vehicle at all times, and on traffic
  vehicles within 150 m.
- Rigid body chassis + 4 raycast/sweep wheels. Sweep (not ray) with the tire radius, so
  the wheel does not fall into road seams and bridge joins.
- Center of mass is explicit per vehicle, expressed as a fraction of wheelbase and
  track, plus a height. This single value does more for handling identity than any
  other.

---

## 2. Suspension

Per wheel, each substep:

```
compression = clamp(1 - (hitDistance - restLength) / suspensionTravel, 0, 1)
springForce = compression * springStiffness                       // N
damperForce = -damperRate * suspensionVelocity                    // N, asymmetric:
                                                                  //  bump = damperRate * 0.6
                                                                  //  rebound = damperRate * 1.0
antiRollForce = antiRollStiffness * (compressionOpposite - compression)
totalForce  = clamp(springForce + damperForce + antiRollForce, 0, maxSuspensionForce)
```

Asymmetric damping (soft bump, firm rebound) is what stops the car pogo-ing over crests
while still absorbing seams. Apply `totalForce` at the wheel contact point — that is
what produces roll and dive for free, coupled to real grip changes.

Defaults, scaled per class in §7:

| Parameter | Range | Notes |
|---|---|---|
| `restLength` | 0.30–0.45 m | Longer for SUV/off-road |
| `suspensionTravel` | 0.12–0.35 m | |
| `springStiffness` | 28,000–95,000 N/m | Per-corner, front usually stiffer on FWD |
| `damperRate` | 3,000–9,000 N·s/m | |
| `antiRollStiffness` | 4,000–30,000 N/m | The primary body-roll tuning knob |
| `maxSuspensionForce` | 3× static corner load | Prevents launch on hard landings |

---

## 3. Tire model

A 3-point simplified slip curve per compound. Full Pacejka is unnecessary and its extra
parameters are unusable by a designer.

```
// Lateral
slipAngle       = atan2(lateralVelocity, |longitudinalVelocity|)      // rad
normalizedSlip  = clamp(|slipAngle| / peakSlipAngle, 0, ∞)
gripCurve(s)    = s <= 1 ? s
                         : max(falloffFloor, 1 - (s - 1) * falloffRate)
lateralForce    = -sign(slipAngle) * gripCurve(normalizedSlip)
                  * peakGrip * normalLoad * surfaceMul * compoundMul

// Longitudinal — same curve shape against slip ratio
slipRatio       = (wheelSurfaceSpeed - groundSpeed) / max(|groundSpeed|, 1.0)
longitudinalForce = gripCurve(|slipRatio| / peakSlipRatio) * sign(slipRatio)
                    * peakGrip * normalLoad * surfaceMul * compoundMul

// Combined slip — friction ellipse, so you cannot brake and turn at full grip
if (lat² + long² > (peakGrip * normalLoad)²) scale both down to the ellipse boundary
```

### 3.1 Load sensitivity
Real tires lose grip coefficient as load rises. Model it — it is what makes weight
transfer *matter* rather than just look nice:

```
loadFactor = 1.0 - 0.00018 * (normalLoad - staticLoad)     // clamped to [0.72, 1.15]
```

### 3.2 Tire compounds

| Compound | `peakGrip` | `peakSlipAngle` | `falloffRate` | Wet mul | Feel |
|---|---|---|---|---|---|
| Stock | 1.00 | 7.5° | 0.55 | 0.78 | Baseline |
| Touring | 1.08 | 8.0° | 0.45 | 0.86 | Forgiving, progressive |
| Sport | 1.22 | 6.5° | 0.70 | 0.72 | Sharper, less warning |
| Semi-Slick | 1.38 | 5.5° | 0.95 | 0.58 | Fast, snappy, punishing |
| All-Terrain | 0.94 | 9.5° | 0.30 | 0.88 | Sloppy, very forgiving |
| Winter | 0.86 | 10.0° | 0.28 | 0.94 | Only choice on snow |

`falloffRate` is the mastery dial: low = the car warns you and slides gently; high =
grip vanishes past the peak. Never ship a car whose stock compound exceeds 0.70.

### 3.3 Surface multipliers

| Surface | Dry | Wet | Snow/Ice |
|---|---|---|---|
| Asphalt | 1.00 | 0.78 | 0.42 |
| Concrete | 0.97 | 0.74 | 0.40 |
| Worn asphalt | 0.93 | 0.70 | 0.38 |
| Gravel / shoulder | 0.68 | 0.62 | 0.35 |
| Grass / dirt | 0.55 | 0.42 | 0.30 |
| Sand | 0.50 | 0.48 | — |
| Rumble strip | 0.88 + vibration | 0.68 | 0.36 |
| Painted line | 0.92 | 0.62 | 0.34 |
| Metal (bridge joint) | 0.95 | 0.60 | 0.33 |

Painted lines being slipperier in the wet is a small, real detail that expert players
will feel and never consciously notice. Include it.

---

## 4. Powertrain

```
engineTorque(rpm) = torqueCurve.Evaluate(rpm) * throttle * nitrousMul * upgradeMul
wheelTorque       = engineTorque * gearRatio * finalDrive * drivetrainEfficiency
                    * driveSplit[wheel]         // FWD/RWD/AWD distribution
driveForce        = wheelTorque / tireRadius    // then traction-limited by §3
```

- **Torque curve:** 8-point curve per engine, in N·m against RPM. Shape defines
  character far more than peak: a muscle V8 peaks at 3,200 rpm and falls off; a
  high-revving I4 peaks at 7,800 and is gutless below 4,000.
- **Engine braking:** on lift, apply `-engineBrakeCoeff * (rpm/maxRpm)²` through the
  drivetrain. This is why lifting settles the car.
- **Rev limiter:** cut fuel for 45 ms on redline contact, with a distinct audio bounce
  and a small exhaust pop.
- **Drivetrain efficiency:** 0.92 manual, 0.88 automatic, 0.95 sequential, 0.97 EV.

### 4.1 Transmissions

| Type | Shift time | Behavior |
|---|---|---|
| Automatic | 320 ms | Shifts up at 92% redline, down on load demand. Default |
| Sequential | 90 ms | Paddle only, no clutch, torque cut on shift |
| Manual H-pattern | 180 ms + clutch | Full clutch modelling, missed shifts possible |
| EV single-speed | — | No shifts, flat torque to base speed then taper |

Shift logic for Automatic must include a **hold-gear rule**: do not upshift within
0.8 s of a downshift, and do not upshift while lateral acceleration exceeds 0.6 g.
Without this, autos shift mid-corner and unsettle the car.

### 4.2 Nitrous

```
capacity         = 4.0 s base, +1.0 s per upgrade tier (max 9.0 s)
torqueMultiplier = 1.38
topSpeedBonus    = +9%
refillTime       = 12.0 s idle
refillMultiplier = 1.25 while combo >= 5, 1.5 while combo >= 12
```

Nitrous also drives the speed rig to +15% of its 300 km/h values, adds an exhaust flame
burst, a chromatic aberration spike, an audio whoosh + sustained hiss, and a 0.25 s FOV
punch. It is the loudest positive feedback in the game after the near miss.

---

## 5. Aerodynamics

```
airDensity   = 1.225 kg/m³
dragForce    = 0.5 * airDensity * dragCoefficient * frontalArea * v²        // opposes motion
downforce    = 0.5 * airDensity * liftCoefficient * frontalArea * v²        // adds to normalLoad
sideForce    = crosswind * sideAreaCoefficient                              // weather-driven
```

- Downforce is split front/rear per vehicle. Rear bias = stability; front bias = turn-in.
- **Arcade cap:** clamp total downforce contribution to grip at +45% so that top-speed
  handling stays forgiving. Real aero would make a hyper car undriveable on a keyboard.
- Drafting: within 18 m directly behind a vehicle, reduce drag by up to 32% scaled by
  distance and by the lead vehicle's frontal area (semi-trucks give the biggest tow).
  Add a visual heat-haze and an audio pressure change. This gives players a *reason* to
  sit dangerously close — a pillar-serving mechanic that costs almost nothing.

---

## 6. Driver assists

All toggleable, all ON by default, all with a visible HUD indicator when they intervene.

| Assist | Behavior | Default |
|---|---|---|
| ABS | Modulate brake torque to hold slip ratio ≤ 0.16, 14 Hz | On |
| Traction Control | Cut throttle to hold drive slip ≤ 0.14 | On |
| ESC | Apply individual brake to correct yaw error > 8° | On |
| Steering assist | Speed-sensitive lock (`PROMPT.md` §4.2) | On, 100% |
| Lane snap | ≤ 0.8 m/s lateral pull to lane center on zero input | On |
| Counter-steer assist | 0.35 blend of automatic counter-steer against yaw error | On |
| Drift recovery | Bleed off lateral velocity above 20° slip if no input for 0.5 s | On |
| Auto-brake for collision | *Not implemented.* Never take control away from the player | — |

**Hardcore mode disables all of them.** The physics model must remain driveable with
everything off — if it is not, the underlying model is wrong and no amount of assist
tuning will fix the feel.

### 6.1 The 250 ms telegraph

Before grip is actually lost, for at least 250 ms:
- Tire squeal rises in volume and pitch, panned to the sliding axle
- Body roll increases beyond its linear range
- Controller rumble: low-frequency, ramping
- Camera roll adds up to 2.5° into the slide
- A subtle steering-feel change on wheel devices (force feedback drop-off)

Only after that window may the car actually step out. This is a hard requirement.

---

## 7. Per-class tuning tables

Baseline values. Individual vehicles vary within ±15% of their class.
`CoM` = center of mass as (fraction of wheelbase from front, height in m).

**Reading the power and torque columns:** power is *peak* power and occurs well above
the torque peak — the listed `peak torque @ rpm` is the top of the torque curve, not
where peak power lands. When authoring a vehicle's 8-point curve, verify that
`max(T × rpm × π/30)` across the curve lands within 10% of the class power figure. The
content validator asserts this (`docs/10-data-schemas.md` §9).

| Class | Mass (kg) | Power (kW) | Peak torque (N·m @ rpm) | Drive | Gears | Top speed (km/h) | 0–100 (s) | CoM | Roll stiffness | Character |
|---|---|---|---|---|---|---|---|---|---|---|
| Starter | 1,180 | 82 | 145 @ 4,200 | FWD | 5 | 168 | 11.8 | 0.42, 0.55 | Soft | Slow, safe, understeers |
| Economy | 1,240 | 96 | 165 @ 4,000 | FWD | 5 | 182 | 10.4 | 0.42, 0.54 | Soft | Baseline |
| Hot Hatch | 1,320 | 180 | 320 @ 2,800 | FWD | 6 | 235 | 6.2 | 0.40, 0.50 | Medium | Torque steer, lift-off rotation |
| Sedan | 1,520 | 165 | 300 @ 3,400 | RWD | 6 | 228 | 7.1 | 0.50, 0.53 | Medium | Neutral, stable |
| Muscle | 1,720 | 350 | 620 @ 3,200 | RWD | 6 | 268 | 4.6 | 0.54, 0.52 | Soft-medium | Snaps loose on throttle |
| Sports | 1,420 | 300 | 420 @ 5,000 | RWD | 6 | 285 | 4.3 | 0.48, 0.46 | Firm | Sharp, rewarding |
| Super | 1,510 | 480 | 620 @ 5,600 | AWD | 7 | 330 | 2.9 | 0.45, 0.42 | Firm | Fast, planted, unforgiving |
| Hyper | 1,380 | 720 | 900 @ 6,200 | AWD | 8 | 385 | 2.4 | 0.44, 0.40 | Very firm | Knife-edge in transition |
| Luxury | 1,880 | 280 | 500 @ 2,600 | AWD | 8 | 250 | 5.4 | 0.50, 0.55 | Soft | Floaty, quiet, effortless |
| SUV | 2,150 | 220 | 420 @ 3,000 | AWD | 8 | 210 | 7.4 | 0.50, 0.72 | Soft | Wallows, lifts a wheel |
| Pickup | 2,340 | 260 | 560 @ 2,400 | RWD/4WD | 6 | 195 | 7.8 | 0.56, 0.75 | Very soft | Light rear, easy to spin |
| Van | 2,050 | 150 | 350 @ 2,200 | FWD | 6 | 175 | 12.5 | 0.44, 0.80 | Very soft | Extreme roll, comedic |
| Off-Road | 2,280 | 290 | 610 @ 2,800 | 4WD | 6 | 190 | 6.9 | 0.50, 0.78 | Soft, long travel | Absorbs everything |
| Classic | 1,390 | 145 | 340 @ 3,000 | RWD | 4 | 205 | 8.2 | 0.52, 0.55 | Very soft | Vague, characterful, slidey |
| Electric | 2,080 | 560 | 900 @ 0 | AWD | 1 | 290 | 2.6 | 0.48, 0.38 | Firm | Instant, silent, heavy |
| Track | 1,050 | 440 | 480 @ 7,200 | RWD | 6 | 315 | 2.8 | 0.46, 0.36 | Extremely firm | Telepathic, zero forgiveness |
| Bike | 245 | 145 | 115 @ 9,000 | RWD | 6 | 300 | 3.0 | 0.50, 0.60 | N/A (lean model) | Narrow, terrifying, huge near-miss potential |

### 7.1 Motorcycles
Bikes use a modified model: 2 wheels, a lean angle driven by steering input and speed,
a much narrower collision volume (0.72 m vs 1.85 m), and a **near-miss clearance
threshold scaled by width** so the bike still has to commit. They can lane-split, which
triggers `laneSplitMul` constantly — bikes are the high-risk/high-score class and
should be gated behind meaningful progression.

---

## 8. Damage model

### 8.1 Tiers

| Tier | Impact energy | Visual | Handling effect |
|---|---|---|---|
| 0 Pristine | — | — | — |
| 1 Scuffed | < 8 kJ | Scratch decals, paint transfer | None |
| 2 Dented | 8–25 kJ | Panel deformation, mirror loss, light cracks | None |
| 3 Damaged | 25–60 kJ | Bumper detach, glass cracks, headlight out, smoke wisps | −4% grip, slight steering pull |
| 4 Critical | 60–120 kJ | Hood up/detached, windshield shattered, heavy smoke, wheel camber | −12% grip, −20% power, steering pull |
| 5 Destroyed | > 120 kJ | Fire, total deformation, wheels detached | Run over |

In most modes any Tier-3+ impact ends the run — damage tiers exist for the *crash
sequence*, replays, Free Ride, and Hardcore's stricter thresholds.

### 8.2 Deformation

Approximate soft body with a per-vertex impact accumulation buffer:

```
For each impact: record (localPosition, normal, energy) into a small ring buffer (16 slots).
Vertex shader offsets each vertex by:
    Σ over impacts of: -normal * energyScale * falloff(|vertex - impactPos|, radius)
Normals are recomputed in the shader; a dent mask drives a crumpled-paint material blend.
```

Cheap, GPU-side, no mesh rebuild, no soft-body solver, and it looks convincing at
30+ km/h closing speeds. Cap at 16 impacts; new impacts merge into the nearest slot.

### 8.3 Debris and crash physics

On a run-ending crash: spawn 6–14 pooled debris rigid bodies (bumper, mirror, hubcap,
glass shards, panel fragments) with velocity inherited from the impact, plus a glass
shard particle burst, sparks on metal-metal scrape, tire smoke, and a dust puff on
off-road contact. Debris despawns after 8 s or when 60 m behind. There are no
pedestrians and no ragdolls of people — only vehicle debris.

---

## 9. Physics acceptance tests (headless, in CI)

| Test | Assertion |
|---|---|
| 0–100 km/h per class | Within 5% of the §7 table |
| Top speed per class | Within 3% of the §7 table |
| 100–0 braking distance | Within 8% of the class target |
| Determinism | Same seed + same input trace = identical position after 10 min, ±1 cm |
| No tunneling | 300 km/h into every collision geometry type, 10k trials, zero passthrough |
| Suspension stability | 10-minute drive over the worst chunk, no oscillation divergence |
| Assist-off driveability | Scripted lane-change input holds the lane with all assists off |
| Grip continuity | No discontinuity > 5% across any surface transition |
| Combined slip | Braking + turning never exceeds the friction ellipse |
