# 18 — Input, Devices, and Force Feedback

Control is pillar #6. Latency is a bug class, not a tuning value. This document is the
deep spec behind `PROMPT.md` §4.

---

## 1. Devices

All three are supported simultaneously and hot-swap mid-run with no menu visit.

| Device | Detection | Notes |
|---|---|---|
| Keyboard + mouse | Any key | Mouse steers only in menus, never in driving |
| Gamepad | Any input above deadzone | XInput, DualSense, DualShock 4, Switch Pro, generic HID |
| Wheel + pedals | Device class on connect | Force feedback, up to 1080° rotation, H-pattern and sequential shifters, clutch, handbrake |

**Hot-swap rule:** the active device is whichever produced input most recently. On
change, the HUD glyph set swaps **within one frame**. Never show a keyboard prompt to a
player holding a controller — it is a small thing that reads as carelessness.

---

## 2. Bindings

See `PROMPT.md` §4.1 for the default table. Every action is remappable per device, with:

- **Conflict detection** — a duplicate binding is shown in red with the conflicting
  action named, and cannot be saved until resolved.
- **Toggle-vs-hold** per action, independently. Look-back, handbrake, and nitrous all
  have players who want each.
- **Chorded bindings** on wheels, where button count is short.
- **Presets:** Default, Southpaw, One-Handed (left), One-Handed (right), Wheel, Legacy.
- **Per-device profiles** saved separately, so plugging in a wheel does not overwrite
  the gamepad layout.

```jsonc
// Save block — docs/02 §7
"input": {
  "activeDevice": "gamepad",
  "profiles": {
    "gamepad": { "bindings": { "steer": "LeftStickX", "nitrous": "FaceButtonBottom" },
                 "deadzoneInner": 0.12, "deadzoneOuter": 0.95, "responseExponent": 1.6,
                 "rumbleStrength": 1.0, "holdActions": ["lookBack"] },
    "keyboard": { "...": "..." },
    "wheel":    { "rotationDeg": 900, "ffbStrength": 0.8, "...": "..." }
  }
}
```

---

## 3. The steering model

The most important tuning in the game. A keyboard player must feel as capable as a
wheel player.

```
// 1. Raw input → normalized target
target = ApplyDeadzone(raw, inner: 0.12, outer: 0.95)
target = sign(target) * pow(|target|, 1.6)        // fine control near center

// 2. Digital devices ramp toward the target; analog devices track it directly
if (device is digital)
    current = MoveTowards(current, target, SteerRate * dt)          // 4.8 /s
    if (target == 0) current = MoveTowards(current, 0, SteerReturnRate * dt)  // 7.5 /s
else
    current = target

// 3. Speed-sensitive lock — this line is what makes 300 km/h playable
SpeedFactor   = clamp(1 - (speed_kmh / 340) * 0.72, 0.28, 1.0)
MaxSteerAngle = 34° * SpeedFactor

// 4. Assists
steerAngle = current * MaxSteerAngle
steerAngle += CounterSteerAssist * yawError * assistStrength       // 0.35 base
if (|target| < 0.02) lateralVelocity += LaneSnapPull(dt)           // ≤ 0.8 m/s
```

### 3.1 Steering lock by speed

| Speed | `SpeedFactor` | Max lock | What a full deflection does |
|---|---|---|---|
| 0 km/h | 1.00 | 34.0° | Full turn |
| 60 km/h | 0.87 | 29.6° | Sharp turn |
| 120 km/h | 0.75 | 25.4° | Fast lane change |
| 180 km/h | 0.62 | 21.1° | Lane change |
| 240 km/h | 0.49 | 16.8° | Deliberate lane change |
| 300 km/h | 0.36 | 12.4° | One lane, controlled |
| 340 km/h+ | 0.28 (floor) | 9.5° | Barely a lane |

The floor at 0.28 matters: without it, hyper cars above 340 km/h would lose the ability
to change lanes at all, which is a fail state the player cannot see coming.

### 3.2 Assist strengths

| Assist | Range | Default | Effect at 0% |
|---|---|---|---|
| Steering assist (lock curve) | 0–100% | 100% | Fixed 34° lock at all speeds — expert only |
| Lane snap | On/Off | On | No pull to lane center |
| Counter-steer assist | 0–100% | 35% | Full manual slide correction |
| Drift recovery | On/Off | On | Slides must be corrected manually |

Hardcore mode forces all to 0/Off. **The physics model must remain driveable there**
(`T-PHY-07`) — if it is not, the model is wrong and no assist tuning will hide it.

---

## 4. Analog response

| Axis | Deadzone inner | Deadzone outer | Curve |
|---|---|---|---|
| Steering | 0.12 | 0.95 | `pow(x, 1.6)` — fine near center |
| Throttle | 0.05 | 0.98 | Linear |
| Brake | 0.05 | 0.98 | `pow(x, 1.3)` — fine at threshold-braking pressures |
| Clutch | 0.08 | 0.92 | Linear, bite point at 0.35–0.55 |

All four are player-adjustable, with a **live visualizer** in Settings showing raw input,
post-deadzone, and post-curve values as three bars. Players with drifting sticks fix
their own problem in ten seconds instead of filing a bug.

Digital throttle and brake (keyboard) ramp over 120 ms and release over 90 ms — enough
to avoid binary on/off harshness, short enough not to read as latency.

---

## 5. Force feedback (wheels)

FFB is a physics readout, not an effect layer. Every force below comes from a real
simulated quantity.

| Effect | Source | Strength |
|---|---|---|
| Self-aligning torque | Front tire slip angle and load | Primary — 60% of total |
| Weight transfer | Front axle load change | 15% |
| Surface texture | Road material + speed | 10% |
| Rumble strip | Contact | Sharp, high frequency |
| Kerb / seam strike | Suspension impulse | Impulse, scaled by energy |
| Understeer | Front grip falloff past peak | **Force drops away** — the correct cue, not a vibration |
| Oversteer | Rear slip angle | Wheel pulls into the correct counter-steer |
| Collision | Impact energy and direction | Hard jolt, clamped to protect hardware |
| Engine | RPM | Subtle, off by default |

**The understeer cue is the one most games get wrong.** Real understeer makes the wheel
go *light*, because the front tires have stopped generating aligning torque. Adding
vibration instead teaches players the wrong reflex. Model the falloff.

Settings: overall strength 0–150%, per-effect scaling, rotation range 180–1080°,
auto-detect from device, and a centering-spring option for wheels without FFB.

The 250 ms telegraph (`docs/03` §6.1) surfaces on a wheel as force drop-off, which is
the most legible warning channel of the three devices.

---

## 6. Latency

**Budget: input poll → present, under 50 ms at 60 fps.**

| Stage | Budget | Requirement |
|---|---|---|
| Device poll | ≤ 2 ms | Polled on the **render thread at frame start**, never on a fixed game tick |
| Input processing | ≤ 1 ms | Deadzone, curve, assist — all trivial math |
| Physics application | ≤ 8 ms | Applied on the next substep, 120 Hz minimum |
| Render | ≤ 16 ms | One frame |
| Present | ≤ 16 ms | One frame; more with VSync |

**Forbidden:**
- Engine-level frame smoothing — disable it explicitly.
- Any "one frame of input buffering" default — find it and remove it.
- Input smoothing beyond the digital ramp in §3. Weight is communicated by the camera
  and body roll, never by delaying the tires.
- Frame generation on by default — it adds latency. Offer it, warn in the tooltip.

Measure with a high-speed camera against a photodiode, not by feel. Record the result
per release (`T-INP-01`).

---

## 7. Rumble

| Event | Motor | Duration | Intensity |
|---|---|---|---|
| Near miss | High frequency | 45 ms | `proximityMul / 3` |
| Close near miss | Both | 60 ms | 0.8 |
| Collision | Low frequency | Scaled by energy | Up to 1.0 |
| Rumble strip | High frequency | Continuous | 0.5 |
| Loss-of-control telegraph | Low, ramping | 250 ms | 0.2 → 0.6 |
| Nitrous | Both, low | Duration of use | 0.3 |
| Gear shift | High | 30 ms | 0.15 |
| Spike strip | Both | 300 ms | 0.9 |

Global strength slider 0–150%, plus **off**. Every rumble event has a non-haptic
equivalent (visual or audio) so nothing is communicated by rumble alone — a hard
accessibility requirement (`T-ACC-08`).

---

## 8. Accessibility of input

Per `PROMPT.md` §18, all shipping in M16:

- Full remapping on every device, including chords.
- Toggle-vs-hold for every hold action.
- One-handed schemes, left and right.
- Steering assist strength 0–100%, continuously.
- Adjustable deadzones and response curves with the live visualizer (§4).
- Rumble strength including off.
- No input requires simultaneous presses in the default scheme.
- No timed input sequence anywhere in the game.
- Instant restart is a single key, and its hold duration (default 0.25 s) is adjustable
  to 0 for players who cannot hold reliably.

---

## 9. Input test register

| ID | Assertion | Level |
|---|---|---|
| T-INP-01 | Photodiode-measured input-to-photon latency < 50 ms at 60 fps | Manual |
| T-INP-02 | Device hot-swap updates HUD glyphs within one frame | Integration |
| T-INP-03 | Steering lock matches the §3.1 table at every listed speed | Unit |
| T-INP-04 | Remapping rejects conflicts and persists per device | Integration |
| T-INP-05 | Every action reachable in each one-handed preset | Manual |
| T-INP-06 | FFB understeer cue reduces force rather than adding vibration | Manual |
| T-INP-07 | No engine frame smoothing or input buffering enabled in Shipping | Static |
| T-INP-08 | Every rumble event has a non-haptic equivalent | Manual |
