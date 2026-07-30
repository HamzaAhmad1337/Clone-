# 06 — Graphics, Art Direction, and the Speed Rig

---

## 1. Art direction

**Grounded realism with heightened light.**

Photoreal materials, real-world proportions, physically plausible lighting — then push
exposure, bloom, and color grading one step past life. The reference is a well-graded
car commercial, not a simulator and not a stylized arcade game.

### 1.1 Rules

1. **The road is the subject.** Everything else is composition. Roadside detail exists
   to convey speed and place, never to compete for attention.
2. **Silhouette first.** Every vehicle must be identifiable in one frame at 300 km/h
   from its outline alone. Design silhouettes before surfacing.
3. **Contrast where it matters.** Traffic vehicles must separate from the road value.
   Never ship a grey car on grey asphalt in grey fog without a rim light.
4. **One accent color per environment.** Cyberpunk = magenta/cyan. Desert = amber.
   Snow = pale blue. It carries into the UI accent for that environment.
5. **No visual noise near the racing line.** Particles, decals, and scatter density all
   fall off toward the lane centers.
6. **Light tells the story.** Time of day and weather do more for variety than geometry.
   Invest in lighting before investing in props.

### 1.2 Color and grading

- ACES-derived tonemapper, filmic. Never a naive Reinhard.
- Per-environment × per-TOD LUT, blended on transitions.
- Auto-exposure with a narrow range (±0.6 EV) and slow adaptation (0.9 s) so tunnels
  feel dark for a moment. Fully disabled in Photo Mode.
- Shadows are cool, lights are warm, everywhere except Cyberpunk City (which inverts it).

---

## 2. Rendering feature list

| Feature | Low | Medium | High | Ultra |
|---|---|---|---|---|
| Global illumination | Baked + probes | Lumen (low) | Lumen | Lumen (high) |
| Reflections | Cubemap probes | SSR (half) | SSR + Lumen | Lumen HQ |
| Shadows | 2 cascades, 1024 | 3 cascades, 2048 | 4 cascades, 2048 + contact | 4 cascades, 4096 + contact + RT |
| Volumetric fog | Off | Low | Medium | High |
| Volumetric light shafts | Off | Sun only | Sun + headlights | All lights |
| Motion blur | Off | Camera only | Per-object | Per-object HQ |
| Ambient occlusion | SSAO half | SSAO | GTAO | GTAO + Lumen |
| Depth of field | Photo mode only | Photo mode only | Photo + cockpit | Photo + cockpit HQ |
| Bloom | Simple | Standard | Standard + lens dirt | HQ + lens dirt |
| Anti-aliasing | FSR Perf | TAA / FSR Bal | TSR / DLSS Q | TSR / DLSS Q |
| Nanite | Off | On (barriers) | On | On |
| Particle density | 40% | 70% | 100% | 130% |
| Scatter density | 45% | 75% | 100% | 120% |
| Traffic draw distance | 450 m | 600 m | 750 m | 900 m |
| Reflection on vehicle | Cubemap | SSR | Lumen | Lumen + planar |
| Decal budget | 120 | 250 | 400 | 600 |

**Traffic draw distance is floored, not free.** Traffic spawns 260–420 m ahead
(`docs/04-traffic-ai.md` §5.1) and the sightline guarantee requires 4.0 seconds of
visible road — 428 m at 385 km/h. So no tier may cut traffic rendering below 450 m, and
any traffic vehicle inside the current sightline requirement is rendered regardless of
tier, using its lowest LOD or imposter if necessary. Cutting a car the player is about
to hit is a fairness bug, not an optimization.

**Nanite exception:** do **not** use Nanite on the player vehicle or near-tier traffic.
They need explicit LOD control, they deform (damage), and their triangle counts are
already appropriate. Nanite is for barriers, buildings, rocks, terrain detail, and
static roadside geometry.

---

## 3. The speed rig

The single most important visual system in the game. Perceived speed must exceed actual
speed by ~15%. Ten coupled effects, all driven by one normalized speed value:

```
s = clamp(speed_kmh / 300, 0, 1.15)      // >1 only under nitrous
```

The divisor is 300, not the game's top speed. Hyper cars exceed 300 km/h and simply sit
at the clamp — the rig is fully deployed by 300 and there is nothing left to give above
it, which is correct: the difference between 300 and 385 km/h should be felt in the
traffic, not in more post-process.

| Effect | Curve | 0 km/h | 150 | 300 | Nitrous |
|---|---|---|---|---|---|
| Camera FOV | `lerp(72, 96, s)` | 72° | 84° | 96° | +15% of range |
| Camera boom length | `lerp(5.2, 6.6, s)` | 5.2 m | 5.9 m | 6.6 m | +0.4 m |
| Camera height | `lerp(1.90, 1.60, s)` | 1.90 m | 1.75 m | 1.60 m | −0.08 m |
| Camera pitch | `lerp(-3°, -6°, s)` | −3.0° | −4.5° | −6.0° | — |
| Radial blur | `pow(s, 1.6) * 0.45` | 0.00 | 0.15 | 0.45 | ×1.35 |
| Vignette | `lerp(0.20, 0.48, s)` | 0.20 | 0.34 | 0.48 | ×1.2 |
| Chromatic aberration | `pow(s, 2.0) * 0.35` | 0.00 | 0.09 | 0.35 | ×1.5 |
| Lens dirt intensity | `s * 0.4` | 0.00 | 0.20 | 0.40 | ×1.3 |
| Wind vibration (camera) | `pow(s, 2.2) * 1.1°` | 0.00° | 0.24° | 1.10° | ×1.2 |
| Speed-line particles | `smoothstep(0.35, 1, s)` | off | subtle | strong | ×1.4 |
| Music low-pass | `lerp(20k, 9k, s)` Hz | 20 kHz | 14.5 kHz | 9 kHz | 6 kHz |
| Camera spring stiffness | `lerp(6, 14, s)` | soft | medium | tight | tight |
| FOV during nitrous | +8° punch over 0.25 s, hold, release over 0.4 s | | | | |

Everything interpolates continuously with a 0.35 s smoothing constant so that a brief
speed drop does not snap the camera. Every effect is individually toggleable in
Accessibility.

### 3.1 Additional speed cues (free wins)
- Roadside scatter density increases within 8 m of the road edge as speed rises.
- Road marking dash frequency and rumble-strip audio give a rhythmic speed reference.
- A near-ground particle sheet of dust/leaves streaming past the camera.
- Heat haze on the horizon at high speed in hot environments.
- Slight camera roll into curves (max 3°) — the world tilts, so the speed reads.

---

## 4. Cameras

Eight modes, cycled with `V`. Each stores its own FOV offset and shake scale, saved per
vehicle so the player's preference persists.

| Camera | Position | Notes |
|---|---|---|
| **Chase Close** | 4.2 m back, 1.6 m up | Default. Tightest, most connected |
| **Chase Far** | 7.5 m back, 2.4 m up | Best situational awareness. Best for Two-Way |
| **Hood** | On the hood, 1.25 m up | Car body visible at the bottom |
| **Bumper** | Front bumper, 0.55 m up | Fastest-feeling. Terrifying. No car visible |
| **Cockpit** | Driver eye point | Full interior, working gauges, wheel + hands, wipers, mirror reflections. Head movement under lateral g |
| **Cinematic** | Roadside/orbital sweep | Auto-cuts every 4–7 s. Not for driving — for Free Ride and Photo Mode |
| **Crash** | Auto-triggered | Slow-motion orbit on impact, 2.2 s, then results |
| **Photo** | Free-fly | Time frozen, full DOF, FOV, roll, filters, hidden HUD |

**Camera behavior:**
- Spring-arm with speed-dependent stiffness (§3), collision-tested against geometry with
  a smooth pull-in inside tunnels.
- Look-back on `C` — a full 180° swing over 0.2 s, not a mirror cut.
- Cockpit camera adds head lean under lateral acceleration (max 4 cm) and pitch under
  braking (max 2°) — subtle enough to read as body movement, not as nausea.
- **Shake layers** (additive, each independently scalable in Accessibility):
  engine idle rumble, road surface texture, suspension impacts, speed vibration,
  near-miss punch (0.9°, 120 ms), nitrous (1.4°, sustained), collision (scaled by
  energy), and rumble-strip (high frequency, 2.5°).

---

## 5. Weather visuals

### 5.1 Rain
- Particle rain aligned to the combined wind + player velocity vector (this is critical —
  rain that falls straight down at 300 km/h looks broken).
- Screen-space droplets on the lens with speed-driven streaking and a wiper-swipe
  clear on cockpit/hood cameras.
- Wheel spray: a dense particle cone behind every wheel of every vehicle, scaled by
  speed and wetness. Traffic spray in front of the player is a major visual and a
  legitimate visibility hazard.
- Wet road: roughness → 0.08, SSR enabled, animated puddle normals, headlight and sign
  reflections streaking down the road.
- Splash particles when a wheel crosses a puddle, plus a distinct audio hit.

### 5.2 Snow / blizzard
- Snow particles with turbulence, accumulating on the road via the material's snow
  parameter (gutters and between wheel tracks first — wheel tracks stay clearer).
- Snow accumulation on the vehicle body and windshield, cleared by wipers.
- Snowbank barriers that deform and puff on contact.
- Blizzard: sightline to 90 m, heavy lateral wind, whiteout gusts.

### 5.3 Fog
- Volumetric fog with height falloff. Headlight cones become the dominant light source.
- Distance-graded: near-clear, thickening with distance, so the road ahead fades rather
  than hitting a wall.
- Fog banks in some modes: thicker patches every 400–900 m for rhythm.

### 5.4 Sandstorm
- Sand particles, strong lateral wind, orange-brown atmospheric tint, sightline 130 m,
  visible sand streaming across the road surface, and a light lateral force on the car.

### 5.5 Thunderstorm
- Directional light burst for 90–160 ms, whole-scene, with a matching cubemap flash.
- Thunder audio delayed by `distance / 343` seconds. **Do not sync them.** The delay is
  the effect and players notice immediately when it is missing.
- Increased rain, wind gusts, and lower ambient light between strikes.

---

## 6. Time of day

Eight presets, continuously blended along a normalized 0–1 day cycle.

| Preset | Sun angle | Color temp | Sun intensity | Sky | Notes |
|---|---|---|---|---|---|
| Dawn | 2° | 1,800 K | 1.5 | Deep blue → orange | Long shadows, headlights on |
| Morning | 25° | 4,200 K | 4.0 | Clear blue | Crisp |
| Noon | 78° | 6,500 K | 9.0 | Bright | Hardest shadows, least flattering |
| Afternoon | 45° | 5,500 K | 6.5 | Warm blue | |
| Golden Hour | 8° | 2,800 K | 3.0 | Gold/amber | **The hero lighting. Use for marketing** |
| Sunset | 1° | 2,000 K | 1.8 | Red/purple | Sun in the driver's eyes, lens flare |
| Night | −12° | 4,000 K (moon) | 0.15 | Dark blue, stars | Headlights dominant |
| Midnight | −40° | 4,000 K | 0.06 | Black, full stars | Darkest. Streetlights are the only fill |

- Headlights, streetlights, and vehicle running lights auto-enable below a lux threshold
  with a 3 s stagger across traffic so they do not all snap on at once.
- Volumetric headlight cones only enable below the same threshold — a significant
  daylight performance saving.
- Moon phases follow a 29.5-day real cycle. A tiny detail; costs nothing; players notice.
- Star field with a correct celestial rotation. Milky Way visible in Desert and
  Mountain Pass at Midnight.

---

## 7. Vehicle rendering

- **Paint shader:** base color, metallic flake (scale + density + color), clearcoat
  layer with its own roughness and IOR, and a fresnel-driven color shift for
  chameleon/pearl finishes. Wrap and decal layers composite beneath the clearcoat.
- **Dirt/wear layer:** accumulates over a run based on weather and surface — dust in
  the desert, road film in rain, salt spray in snow. Resets in the garage. Small
  detail, huge realism payoff.
- **Glass:** proper transmission with interior visible, tint parameter, and a separate
  cracked/shattered material state.
- **Lights:** emissive + a light source + a volumetric cone at night. Brake lights use a
  distinct higher-intensity emissive and must be visible at 500 m.
- **Wheels:** motion blur on the rims (a rotational blur mask driven by wheel speed,
  crossfading to a static blurred texture above 900 rpm — this is a classic trick and
  removes the strobing that would otherwise ruin the sense of speed).
- **Brake calipers:** heat glow emissive driven by accumulated brake energy, fading
  over ~20 s.
- **LODs:** LOD0 ~180k tris (hero, player + within 40 m), LOD1 ~65k, LOD2 ~18k,
  LOD3 ~4k, shadow proxy ~2k, plus an imposter for 350 m+.

---

## 8. Particles and VFX

All pooled. Priority-based eviction when the budget is hit — near-miss and collision
effects have absolute priority over ambience.

| Effect | Trigger | Budget |
|---|---|---|
| Tire smoke | Slip ratio > 0.25 | High |
| Tire marks (decal) | Slip ratio > 0.20 | 400 decals, FIFO |
| Exhaust | Idle + throttle, cold-start visible | Low |
| Backfire flame | Lift-off on tuned cars, nitrous | Medium |
| Nitrous | Activation + sustained | High |
| Sparks | Metal scrape, spike strips, bottoming out | High |
| Debris | Collisions | Pooled rigid bodies (60) |
| Glass shards | Window break | High |
| Smoke / steam / fire | Damage tiers 3–5 | High |
| Rain / snow / sand | Weather | Continuous, density-scaled |
| Wheel spray | Wet surface | Per wheel, per vehicle |
| Puddle splash | Puddle crossing | High |
| Dust | Off-road, desert | Medium |
| Leaves | Forest, autumn | Low, ambience |
| Speed lines | Speed rig | Continuous above 0.35 s |
| Heat haze | Hot environments, exhaust | Low |
| Air displacement | Semi-truck near miss | High — signature effect |

---

## 9. Animation checklist

Consolidated so nothing falls between the vehicle, camera, and VFX specs. Every item is
required on every drivable vehicle unless noted.

| Animation | Driven by | Notes |
|---|---|---|
| Steering wheel | Steering input | Correct lock ratio per vehicle — a 34° road lock is ~1.5 turns lock-to-lock at the wheel, not 34° of wheel rotation |
| Driver hands and arms | Steering, via two-bone IK | Hand-over-hand above 90° of wheel rotation |
| Pedals | Throttle / brake / clutch inputs | Clutch pedal only on Manual |
| Gear shifter | Gear change events | H-pattern gate on Manual, sequential throw on Sequential, none on Single |
| Suspension | Per-wheel compression | Visible arms, springs, and driveshafts where modelled |
| Wheel rotation | Wheel angular velocity | Rotational blur mask above 900 rpm (§7) to kill strobing |
| **Wheel wobble** | Wheel damage state | Visible camber and toe deviation after a Tier-4 impact or a spike strip, plus a rotational wobble that feeds a matching low-frequency rumble and steering pull |
| Brake caliper heat | Accumulated brake energy | Emissive glow, ~20 s fade (§7) |
| Door opening | Garage reveal, Photo Mode | Driver-side only |
| **Driver entering** | First-unlock garage reveal | Door opens, driver enters, seatbelt, hands to wheel, engine start, camera push-in. 4 s, skippable, plays once per vehicle. Also used as the Free Ride start when a "cinematic starts" option is on |
| Body roll / dive / squat | Weight transfer | Coupled to actual per-wheel grip, never cosmetic (`docs/03` §2) |
| Crash deformation | Impact accumulation buffer | GPU vertex offset (`docs/03` §8.2) |
| Detached parts | Impact energy | Pooled rigid bodies, physics-driven |
| Nitrous activation | Nitrous input | Exhaust flame burst, FOV punch, intake flap where modelled |
| Wipers | Weather wetness | Cockpit and hood cameras; clears the lens droplet effect |
| Indicators / hazards | Traffic AI intent, player input | Traffic blinker discipline is per-personality (`docs/04` §2) |
| Camera shake layers | Eight additive sources | Individually scalable in Accessibility (§4) |
| Antenna / mirror sway | Speed and lateral g | Tiny, cheap, and does a surprising amount for the sense of speed |

## 10. Photo Mode

Free-fly camera (with a distance leash of 40 m), time frozen, and full control over:
FOV (10–140°), aperture and focal distance with focus peaking, camera roll, exposure,
20 color grade presets plus manual controls, vignette, grain, chromatic aberration,
9 lens flare types, HUD hide, character/driver toggle, weather and TOD scrub, sun
position scrub, motion blur on a frozen frame (simulated from stored velocities — this
is what makes photo mode shots look alive), rule-of-thirds and golden-ratio guides,
and export at up to 4× resolution with an optional watermark.

Photo Mode drives organic marketing. It is worth the two weeks.
