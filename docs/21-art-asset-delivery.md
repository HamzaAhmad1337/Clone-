# 21 — Art Asset Delivery Spec and Model Checklist

The complete list of 3D assets Highway Rush needs, and the exact specification each one
must meet to drop into the project without rework.

---

## 0. Who produces what

| Asset | Source | Why |
|---|---|---|
| **3D models** (all of them) | **You supply** | Geometry cannot be generated from a specification |
| Textures, materials | You supply | Same |
| Audio recordings | You supply or licence | `docs/19` §5 has the recording spec |
| Vehicle data files (physics, powertrain, audio mapping, progression) | **Generated from this spec** | One working example each in `data/vehicles/` |
| Socket/naming/LOD conventions | **This document** | So models integrate rather than need rebuilding |
| Validation | `tools/validate_content.py` + CI | Catches spec violations before they reach the build |

**Read this before you buy or commission anything.** A model that arrives with the wrong
pivot, no sockets, no LOD chain, and 4× scale costs more to fix than it cost to buy.

---

## 1. Do not buy models yet

The spec has two hard gates (`PROMPT.md` §20) and **models are not needed for either**:

| Milestone | What it needs | Model cost |
|---|---|---|
| **M1 — Drive a box** ⚠️ | One grey box, correctly sized and collided | **Zero** |
| M2 — The road | Grey-box environment | Zero |
| M3 — Traffic | 3–4 grey-box traffic shapes | Zero |
| **M4 — The verb** ⚠️ | Same grey boxes | **Zero** |
| M6 — Feel | 1 hero car, 3 traffic cars | ~4 models |
| M12 — Vehicles | The full roster | ~95 models |

M1 is the gate where three people who did not build it must independently say the box is
fun to drive on an empty plane. **If you buy 95 car models before M1 passes and M1 fails,
that money is gone** — the spec's whole position is that no amount of content rescues bad
driving feel.

Buy **one** decent car model for M6, to validate the pipeline in §3 end to end. Buy the
rest at M12, when the game is proven.

### 1.1 Grey-box placeholders — generated, free, available now

```bash
python3 tools/generate_greybox.py data data/greybox
```

Reads every file in `data/vehicles/` and emits, per vehicle:

- `SM_<id>_LOD0.obj` — body and four wheels at **correct real-world dimensions**,
  correct pivot (§3.1), correct axes and units
- `SM_<id>_sockets.json` — all 27 sockets from §3.3, positioned

This is enough geometry for **M1 through M6**. It costs nothing, carries no licensing
exposure, and proves the data → mesh → socket pipeline works before a single model is
bought. When a real mesh arrives, the socket layout in these files is the contract it
has to match.

Regenerate any time a vehicle's dimensions change. The output is not committed — it is
derived from `data/vehicles/`.

---

## 2. Sourcing, and the licensing trap

| Route | Cost | Notes |
|---|---|---|
| Asset stores (Fab, TurboSquid, CGTrader, Sketchfab) | $20–$300/model | **Read the licence.** See below |
| Commission a vehicle artist | $400–$2,000/model | Best control; specify §3 in the brief |
| Model in-house | Time | 20–60 h per hero vehicle with interior |
| Kitbash generic bodies | Low | Viable for traffic, not for hero cars |

### The trap

**A model of a real car sold on an asset store almost never comes with the right to ship
it in a commercial game.** Typical store licences cover rendering, stills, personal, or
"editorial" use, and explicitly exclude redistribution inside a game — and none of them
can grant you the manufacturer's trademark or design rights in the first place, because
the seller does not hold them.

So there are two separate permissions, and buying a model gives you neither
automatically:

1. **The model's copyright** — from whoever made it. A game-distribution licence.
2. **The vehicle's trade dress and trademark** — from the manufacturer. Only they grant it.

This is exactly why `docs/20` puts real identities behind `HR_LICENSED_CONTENT`: build
with real cars now, and the day distribution matters you flip a flag rather than
re-commission a roster.

**Practical recommendation:** for models you intend to ship, commission original bodies
against the §3 spec. The invented marques in `docs/13` §1 exist so an artist has a brief
that carries no rights problem at all.

---

## 3. Per-model delivery specification

Every drivable vehicle must arrive meeting **all** of this. Reject deliveries that do not.

### 3.1 Format and transform

| Requirement | Value |
|---|---|
| Format | FBX (preferred) or glTF 2.0 |
| Units | Centimetres, 1 unit = 1 cm |
| Scale | 1.0 — no import-time scaling |
| Up axis | Z-up (Unreal). State clearly if delivered Y-up |
| Forward axis | +X |
| **Pivot** | Ground level, centred between the front wheels' contact patches |
| Rotation | Zeroed. No baked transforms |
| Real-world scale | Verified against the published dimensions in `docs/20` §3 |

The pivot rule matters more than it looks: physics, cameras, sockets, and the near-miss
detector all assume it. A model pivoted at its geometric centre will sit half-buried.

### 3.2 Polygon budgets

Player vehicles (`docs/06` §7):

| LOD | Triangles | Used at |
|---|---|---|
| LOD0 | ~180,000 | Player car, garage, and within 40 m |
| LOD1 | ~65,000 | 40–90 m |
| LOD2 | ~18,000 | 90–150 m |
| LOD3 | ~4,000 | 150 m+ |
| Shadow proxy | ~2,000 | All shadow casting |
| Interior | ~40,000 | Cockpit camera and garage reveal |

Traffic vehicles (`docs/11` §3.2): 45k / 18k / 6k / 1.5k, plus an imposter beyond 350 m.

**Do not use Nanite on vehicles** (`docs/06` §2) — they deform under damage and need
explicit LOD control.

### 3.3 Required sockets

Named exactly as listed. The data files reference these strings directly.

| Socket | Purpose |
|---|---|
| `wheel_fl`, `wheel_fr`, `wheel_rl`, `wheel_rr` | Wheel attachment, at hub centre |
| `seat_driver` | Driver figure |
| `cam_cockpit` | Cockpit camera, at driver eye point |
| `cam_hood` | Hood camera |
| `cam_bumper` | Bumper camera |
| `exhaust_l`, `exhaust_r` (or `exhaust_c`) | Exhaust particles, flames, backfire |
| `gauge_tach`, `gauge_speed` | Gauge needle pivots, in the interior mesh |
| `headlight_l`, `headlight_r` | Light source + volumetric cone |
| `taillight_l`, `taillight_r` | |
| `brake_l`, `brake_r` | **Must render to 500 m** (`docs/04` §7) |
| `indicator_fl`, `indicator_fr`, `indicator_rl`, `indicator_rr` | **Also 500 m** (`docs/04` §3.6) |
| `reverse_l`, `reverse_r` | Present but unused — motion is forward-only |
| `plate_front`, `plate_rear` | Licence plate decal |
| `underglow_anchor` | Underglow emitter |

### 3.4 Required bones / animated parts

Per the animation checklist (`docs/06` §9):

`steering_wheel` · `pedal_throttle` · `pedal_brake` · `pedal_clutch` (manual only) ·
`shifter` · `door_driver` · `wiper_l`, `wiper_r` · `needle_tach`, `needle_speed` ·
`suspension_fl/fr/rl/rr` (visible arms where modelled) · `caliper_fl/fr/rl/rr`

### 3.5 Body-kit slots

Modular, separable meshes so customization works (`PROMPT.md` §13):

`frontBumper` · `rearBumper` · `sideSkirt` · `spoiler` · `hood` · `diffuser` ·
`mirror_l`, `mirror_r` · `exhaustTip`

Each slot needs a stock version plus at least 3 alternates on hero vehicles.

### 3.6 Materials and UVs

| Requirement | Detail |
|---|---|
| Material slots | Body paint (separate), glass, interior, trim, chrome, rubber, lights, plate |
| Paint zones | Body paint isolated to its own slot so the paint shader (`docs/06` §7) applies |
| UV0 | Non-overlapping, 0–1 space |
| UV1 | Lightmap, non-overlapping, padded |
| Texture resolution | 4K hero body, 2K interior, 1K trim |
| Maps | Base colour, normal, ORM (occlusion/roughness/metallic), emissive for lights |
| Naming | `T_<Vehicle>_<Part>_<Map>` |
| Glass | Separate material, supports a cracked/shattered state |

### 3.7 Collision

| Element | Requirement |
|---|---|
| Body collision | Simplified convex hull, **inset 6 cm from the visual mesh** (`docs/01` §7) |
| Wheels | Handled by the physics model — no wheel collision geometry |
| Detachable parts | Simple convex per part (bumper, mirror, hood) |

The 6 cm inset is a fairness rule: the player always gets the benefit of the doubt.

### 3.8 Naming

```
SM_<Manufacturer>_<Model>_<Variant>_LOD<n>      SM_Suzuki_Mehran_VXR_LOD0
SM_<Manufacturer>_<Model>_Interior              SM_Suzuki_Mehran_Interior
SM_<Manufacturer>_<Model>_Shadow
SM_Traffic_<Type>_<Letter>_LOD<n>               SM_Traffic_Sedan_A_LOD0
```

Match `visual.meshLod0` and `licensed.meshSet` in the vehicle data file exactly.

---

## 4. The complete model checklist

95 vehicle models. Tick as sourced. Specs for every licensed vehicle are in `docs/20` §3.

### 4.1 Player vehicles — Suzuki / Maruti (6)
- [ ] Suzuki Mehran VXR — **Budget, default start**
- [ ] Maruti 800 — Budget
- [ ] Suzuki Alto VXL — Budget
- [ ] Suzuki Cultus VXL — Economy
- [ ] Suzuki Swift Sport (ZC33S) — Hot Hatch
- [ ] Suzuki Jimny (JB74) — Off-Road

### 4.2 Honda (6)
- [ ] Honda Civic Type R (FK8) — Hot Hatch
- [ ] Honda Civic Type R (FL5) — Hot Hatch
- [ ] Honda S2000 (AP1) — Sports · *highest audio value in the roster*
- [ ] Honda Integra Type R (DC2) — Hot Hatch
- [ ] Honda NSX (NA1) — Sports
- [ ] Honda NSX (NC1) — Super

### 4.3 BMW (7)
- [ ] BMW M2 (G87) — Sports
- [ ] BMW M3 (E46) — Sports · *the `I6` reference*
- [ ] BMW M3 (G80 Competition) — Sports
- [ ] BMW M5 (E60) — Super · *the `V10` reference*
- [ ] BMW M8 Competition — Luxury
- [ ] BMW 850CSi (E31) — Classic · *`V12` coverage*
- [ ] BMW i8 — Electric

### 4.4 Mercedes-AMG (6)
- [ ] Mercedes-AMG C63 (W204, M156) — Muscle · *cross-plane V8*
- [ ] Mercedes-AMG SLS — Super
- [ ] Mercedes-AMG GT R — Super · *flat-plane V8*
- [ ] Mercedes-AMG A45 S — Hot Hatch
- [ ] Mercedes-AMG S65 — Luxury · *`V12`*
- [ ] Mercedes-AMG G63 — SUV

### 4.5 Porsche (7)
- [ ] Porsche 718 Cayman GT4 — Sports
- [ ] Porsche 911 GT3 (992) — Super · *the `Flat6` reference*
- [ ] Porsche 911 Turbo S (992) — Super
- [ ] Porsche Carrera GT — Hyper · *`V10`*
- [ ] Porsche 918 Spyder — Hyper
- [ ] Porsche Taycan Turbo S — Electric
- [ ] Porsche Cayenne Turbo GT — SUV

### 4.6 Toyota (7)
- [ ] Toyota Supra (A80) — Sports
- [ ] Toyota GR Supra (A90) — Sports
- [ ] Toyota GR Yaris — Hot Hatch · *`I3` turbo*
- [ ] Toyota GR86 — Sports
- [ ] Toyota AE86 Corolla — Classic
- [ ] Toyota Land Cruiser (300) — SUV
- [ ] Toyota Hilux — Pickup

### 4.7 Ford (6)
- [ ] Ford Mustang GT (S550) — Muscle · *cross-plane*
- [ ] Ford Mustang Shelby GT350 — Muscle · *flat-plane; pair with the GT in the garage*
- [ ] Ford Mustang Shelby GT500 — Muscle
- [ ] Ford Focus RS (Mk3) — Hot Hatch
- [ ] Ford GT (2017) — Super
- [ ] Ford F-150 Raptor — Pickup

### 4.8 Dodge (6)
- [ ] Dodge Challenger SRT Hellcat — Muscle · *the `V8Supercharged` reference*
- [ ] Dodge Challenger SRT Demon 170 — Muscle
- [ ] Dodge Charger SRT Hellcat — Sedan
- [ ] Dodge Challenger R/T — Muscle
- [ ] Dodge Viper ACR (Gen V) — Super · *`V10`*
- [ ] Dodge Ram 1500 TRX — Pickup

**Player subtotal: 51.** `docs/13` §2 budgets 80 slots, so ~29 remain for expansion —
the two recorded family gaps (a Mazda rotary, a Suzuki GSX-R for the Bike class) plus
whatever else you want.

### 4.9 Traffic vehicles — unbranded (32)

Generic archetypes, 5 colour variants each, no badges (`docs/20` §5).

- [ ] Sedan A–F (6)
- [ ] Hatchback A–D (4)
- [ ] SUV A–D (4)
- [ ] Pickup A–C (3)
- [ ] Van A–C (3)
- [ ] City bus, Coach (2)
- [ ] Semi tractor A–C (3)
- [ ] Trailers: box, tanker, flatbed, car-carrier (4)
- [ ] Sports car A–B (2)
- [ ] Luxury A–B (2)
- [ ] Motorcycle (1)
- [ ] EV (1)
- [ ] Ambulance, Fire truck, Patrol car (3)
- [ ] Construction: cone truck, roller, excavator transport (3)

### 4.10 Regional traffic — licensed exception (5)

The only branded traffic, for South Asian and Middle Eastern environments
(`docs/20` §5). Recognising your own first car in traffic is the point.

- [ ] Suzuki Mehran (traffic variant)
- [ ] Suzuki Alto (traffic variant)
- [ ] Suzuki Cultus (traffic variant)
- [ ] Toyota Hilux (traffic variant)
- [ ] Toyota Land Cruiser (traffic variant)

### 4.11 Police — unbranded, mandatory (4)

Never licensed — enforced by `tools/validate_content.py`. No manufacturer permits their
car being modelled getting rammed.

- [ ] Interceptor sedan
- [ ] SUV rammer
- [ ] Heavy blocker
- [ ] Helicopter

**Grand total: 96 vehicle models** (51 player + 32 traffic + 5 regional + 4 police +
4 trailers counted within traffic).

---

## 5. Environment art

Not vehicles, but needed for M13. Per environment (14 total, `docs/13` §3):

| Set | Contents |
|---|---|
| Road furniture | Barriers, guardrails, Jersey barriers, cable barrier, snow bank, sand berm |
| Signage | Gantries, exit signs, speed limits, distance markers, chevrons, construction signs — **invented place names and route shields only, in both modes** |
| Lighting | Pole lights (single/double arm), tunnel strips, bridge lighting |
| Scatter | Vegetation, rocks, fences, billboards, buildings, power lines |
| Structures | Tunnel, bridge, overpass, toll gantry, rest stop |
| Terrain | Heightfield + materials per biome |

Roughly 60–120 unique props per environment, heavily instanced (`docs/11` §3.1) — a
chunk with 400 scattered objects must cost 3–6 draw calls.

---

## 6. Delivery acceptance checklist

Run per model. Any failure is a rejection.

- [ ] Correct format, units, scale, up/forward axis
- [ ] Pivot at ground level, centred between front wheel contact patches
- [ ] Dimensions match the published figures in `docs/20` §3 within 2%
- [ ] Full LOD chain present and within budget (§3.2)
- [ ] Shadow proxy present
- [ ] Interior mesh with working gauge pivots
- [ ] Every socket in §3.3 present and correctly named
- [ ] Every bone in §3.4 present
- [ ] Body-kit slots separable (§3.5)
- [ ] Body paint on its own material slot
- [ ] UV0 and UV1 non-overlapping
- [ ] Collision hull inset 6 cm from the visual mesh
- [ ] Naming matches §3.8 and the vehicle data file
- [ ] Brake lights and indicators visible at 500 m
- [ ] Licence terms permit commercial game distribution, in writing

The last one is the one people skip.

---

## 7. What happens once you have a model

1. Drop the mesh into `/Content/Vehicles/<Manufacturer>/`.
2. Fill in the vehicle data file — copy `data/vehicles/budget_fwd_i3_a.json`, which is a
   complete working Mehran and passes every lint.
3. Run `python3 tools/validate_content.py data`.
4. CI validates against the JSON Schema on push.

Give me the models and the manufacturer specs, and **the data files are mine** — physics,
torque curves, audio family mapping, progression slot, pricing. That part is generated
from this specification, not hand-authored.
