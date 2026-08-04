# 20 — Licensed Vehicle Roster (Real Manufacturers)

The real-marque roster, with accurate specifications mapped onto the physics and engine
families the game already defines.

---

## 1. How this works, and why it is built this way

Real vehicles are enabled through a **marque-mapping layer**, not by hardcoding names
into content. Every vehicle keeps its invented identity as a fallback and gains an
optional `licensed` block:

```jsonc
{
  "id": "sports_rwd_i6_a",
  "displayNameKey": "vehicle.sports_rwd_i6_a.name",
  "marque": "Halden",                    // invented fallback — always present
  "licensed": {
    "manufacturer": "BMW",
    "model": "M3",
    "generation": "E46",
    "modelYear": 2004,
    "displayName": "BMW M3 (E46)",
    "meshSet": "SM_BMW_M3_E46",
    "engineCode": "S54B32"
  }
}
```

A single build flag, `HR_LICENSED_CONTENT`, selects which identity the game presents.
**The physics, audio family, class, price, and progression slot are identical either
way** — it is the same car underneath, wearing a different badge and mesh.

### Why bother with the layer instead of just using real names

Because it is the difference between a config flip and a content re-do:

| Scenario | With the layer | Without it |
|---|---|---|
| Build and iterate now | Flag on. Real cars everywhere | Same |
| Ship globally before licensing lands | Flag off. Invented marques, same game | Re-author 80 vehicles, re-record audio references, re-do the store page |
| Licences signed for 5 of 8 manufacturers | Per-vehicle flag. Mixed roster | Manual surgery per car |
| A manufacturer withdraws permission | Flip one vehicle | Emergency patch |

You said you would sort documentation out if this goes global. This layer is what makes
that a Tuesday afternoon rather than a re-scope.

### What the actual exposure is

Stated once, plainly, so it can be planned around rather than worried about:

- **Risk attaches to distribution, not development.** A prototype on your own machine or
  shared with testers is not a commercial use of anyone's trademark.
- **The 3D model is the bigger issue than the name.** Body shapes are protected by design
  patents and trade dress in most markets, and they outlast most people's assumptions.
  A car *named* "BMW M3" with an original body is a smaller problem than an unbadged but
  pixel-accurate E46 shell.
- **Engine audio recorded from a real car** carries its own rights, separate from the
  vehicle. `docs/19` §5 is written so you can record your own.
- Licensing is normally negotiated per manufacturer, covering name, likeness, and sound
  together. Studios budget for it as a line item.

None of that blocks what you are doing now. It is why the flag exists.

---

## 2. Class floor change: the Mehran problem

The Suzuki Mehran is the most culturally important car on this list for a Pakistani
audience, and it does not fit the existing class table. It is far slower than anything
the spec previously contemplated:

| | Mehran | Previous Starter baseline |
|---|---|---|
| Power | **29 kW** (39 hp @ 5,500 rpm) | 82 kW |
| Torque | 59 N·m @ 3,000 rpm | 145 N·m |
| Kerb weight | 660 kg | 1,180 kg |
| Top speed | 135 km/h | 168 km/h |
| 0–100 km/h | ~24 s | 11.8 s |
| Engine | F8B, 796 cc OHV **I3** | I4 |

So the spec gains a new class **below** Starter:

### Budget class (new)
| Class | Mass | Power | Torque | Drive | Gears | Top speed | 0–100 | Character |
|---|---|---|---|---|---|---|---|---|
| **Budget** | 620–780 kg | 26–34 kW | 55–70 N·m | FWD | 5 | 130–145 km/h | 20–26 s | Light, buzzy, gutless, beloved |

**This is excellent for the game, not a problem to work around.** At 135 km/h against
traffic averaging 78–112 km/h, the Mehran is barely overtaking anything. Every near miss
has to be earned by patience and line choice rather than raw speed, and the combo window
becomes genuinely hard to sustain. It is the perfect tutorial car *and* a legitimate
hard-mode challenge, and for a Pakistani player it is instantly, personally funny.

Recommended: make the Mehran the **default starting vehicle** in the licensed roster.
The progression arc from a Mehran to a Hellcat is one of the best in the genre.

Schema changes this required (`data/schemas/vehicle.schema.json`):
- `derivedStats.peakPowerKw` minimum 30 → **25**
- `derivedStats.zeroToHundredS` maximum 20 → **30**
- `class` enum gains **`Budget`**

---

## 3. The roster

Specifications are manufacturer-published figures for the generation named. `Family` is
the engine family from `docs/19` §1. `Slot` is the class from `docs/03` §7.

### 3.1 Suzuki / Maruti Suzuki — the home-market heroes

| Vehicle | Engine | Family | Power | Torque | Drive | Slot |
|---|---|---|---|---|---|---|
| **Suzuki Mehran VXR** | F8B 796 cc OHV I3 | `I3` | 29 kW @ 5,500 | 59 N·m @ 3,000 | FWD | **Budget — default start** |
| **Maruti 800** | F8D 796 cc I3 | `I3` | 27 kW @ 5,500 | 59 N·m @ 2,500 | FWD | Budget |
| Suzuki Alto (VXL AGS) | K10B 998 cc I3 | `I3` | 50 kW @ 6,000 | 90 N·m @ 3,500 | FWD | Budget |
| Suzuki Cultus VXL | K10B 998 cc I3 | `I3` | 50 kW @ 6,000 | 90 N·m @ 3,500 | FWD | Economy |
| Suzuki Swift Sport (ZC33S) | K14C 1.4 I4 turbo | `I4Turbo` | 103 kW @ 5,500 | 230 N·m @ 2,500 | FWD | Hot Hatch |
| Suzuki Jimny (JB74) | K15B 1.5 I4 | `I4` | 75 kW @ 6,000 | 130 N·m @ 4,000 | 4WD | Off-Road |

**Design note:** the Mehran, Maruti 800, Alto, and Cultus give the early game a
genuinely local texture. They should also appear in *traffic* on the Middle Eastern
Highway and any future South Asian environment — seeing the car you learned to drive in
as ambient traffic is a strong recognition beat.

### 3.2 Honda — high-revving naturally aspirated

| Vehicle | Engine | Family | Power | Torque | Redline | Drive | Slot |
|---|---|---|---|---|---|---|---|
| Honda Civic Type R (FK8) | K20C1 2.0 I4 turbo | `I4Turbo` | 235 kW @ 6,500 | 400 N·m | 7,000 | FWD | Hot Hatch |
| Honda Civic Type R (FL5) | K20C1 2.0 I4 turbo | `I4Turbo` | 242 kW @ 6,500 | 420 N·m | 7,000 | FWD | Hot Hatch |
| **Honda S2000 (AP1)** | F20C 2.0 I4 NA | `I4` | 177 kW @ 8,300 | 208 N·m @ 7,500 | **9,000** | RWD | Sports |
| Honda Integra Type R (DC2) | B18C 1.8 I4 NA | `I4` | 145 kW @ 8,000 | 178 N·m @ 7,300 | 8,700 | FWD | Hot Hatch |
| Honda NSX (NA1) | C30A 3.0 V6 NA | `V6` | 201 kW @ 7,300 | 285 N·m @ 5,400 | 8,000 | RWD | Sports |
| Honda NSX (NC1) | JNC1 3.5 V6 hybrid | `V6Turbo` | 427 kW combined | 646 N·m | 7,500 | AWD | Super |

**The S2000 is the single most valuable car on this list for audio.** A 9,000 rpm
naturally aspirated I4 puts its 2nd-order fundamental at 300 Hz at redline with harmonics
climbing well past 3 kHz — a completely different sound from every turbo I4 in the game,
and exactly the "high-revving NA beats forced induction" character the research found
enthusiasts prize.

### 3.3 BMW — inline-six and the V10 outlier

| Vehicle | Engine | Family | Power | Torque | Redline | Drive | Slot |
|---|---|---|---|---|---|---|---|
| BMW M2 (G87) | S58 3.0 I6 turbo | `I6` | 338 kW @ 6,250 | 600 N·m | 7,200 | RWD | Sports |
| **BMW M3 (E46)** | S54B32 3.2 I6 NA | `I6` | 252 kW @ 7,900 | 365 N·m @ 4,900 | **8,000** | RWD | Sports |
| BMW M3 (G80 Comp) | S58 3.0 I6 turbo | `I6` | 375 kW @ 6,250 | 650 N·m | 7,200 | RWD/AWD | Sports |
| **BMW M5 (E60)** | S85 5.0 **V10** NA | `V10` | 373 kW @ 7,750 | 520 N·m @ 6,100 | **8,250** | RWD | Super |
| BMW M8 Competition | S63 4.4 V8 twin-turbo | `V8` | 460 kW @ 6,000 | 750 N·m | 7,200 | AWD | Luxury |
| BMW 850CSi (E31) | S70B56 5.6 **V12** | `V12` | 280 kW @ 5,300 | 550 N·m @ 4,000 | 6,000 | RWD | Classic |
| BMW i8 | 1.5 I3 turbo hybrid | `I3` | 275 kW combined | 570 N·m | 6,500 | AWD | Electric |

The E46 M3's S54 is the reference for the `I6` family in `docs/19` §3 — raspy and
metallic low down, whirring mechanically, hardening into an aggressive growl toward
8,000. The E60 M5's S85 V10 is a road-going engine that sounds like a racing one, and it
is the best `V10` reference available outside an exotic.

### 3.4 Mercedes-AMG — cross-plane thunder and one flat-plane

| Vehicle | Engine | Family | Power | Torque | Drive | Slot |
|---|---|---|---|---|---|---|
| **Mercedes-AMG C63 (W204)** | M156 6.2 V8 NA **cross-plane** | `V8` | 336 kW @ 6,800 | 600 N·m @ 5,000 | RWD | Muscle |
| Mercedes-AMG SLS | M159 6.2 V8 NA cross-plane | `V8` | 420 kW @ 6,800 | 650 N·m @ 4,750 | RWD | Super |
| **Mercedes-AMG GT R** | M178 4.0 V8 twin-turbo **flat-plane** | `V8` | 430 kW @ 6,250 | 700 N·m | RWD | Super |
| Mercedes-AMG A45 S | M139 2.0 I4 turbo | `I4Turbo` | 310 kW @ 6,750 | 500 N·m | AWD | Hot Hatch |
| Mercedes-AMG S65 | M279 6.0 **V12** twin-turbo | `V12` | 463 kW @ 4,800 | 1,000 N·m | RWD | Luxury |
| Mercedes-AMG G63 | M177 4.0 V8 twin-turbo | `V8` | 430 kW @ 6,000 | 850 N·m | 4WD | SUV |

The M156 (cross-plane, naturally aspirated, 6.2 litres) and the M178 (flat-plane,
turbocharged) sit in the same brand and sound nothing alike. Putting both in the game is
free demonstration of `docs/19` §2.

### 3.5 Porsche — flat-six, and the V10 nobody expects

| Vehicle | Engine | Family | Power | Torque | Redline | Drive | Slot |
|---|---|---|---|---|---|---|---|
| Porsche 718 Cayman GT4 | 9A2 4.0 flat-6 NA | `Flat6` | 309 kW @ 7,600 | 420 N·m | 8,000 | RWD | Sports |
| **Porsche 911 GT3 (992)** | 9A2 4.0 flat-6 NA | `Flat6` | 375 kW @ 8,400 | 470 N·m @ 6,100 | **9,000** | RWD | Super |
| Porsche 911 Turbo S (992) | 9A2 3.8 flat-6 twin-turbo | `Flat6` | 478 kW @ 6,750 | 800 N·m | 7,200 | AWD | Super |
| **Porsche Carrera GT** | 5.7 **V10** NA | `V10` | 450 kW @ 8,000 | 590 N·m @ 5,750 | **8,400** | RWD | Hyper |
| Porsche 918 Spyder | 4.6 V8 NA hybrid | `V8` | 652 kW combined | 917 N·m | 9,150 | AWD | Hyper |
| **Porsche Taycan Turbo S** | Dual permanent-magnet | `Electric` | 560 kW overboost | 1,050 N·m | — | AWD | Electric |
| Porsche Cayenne Turbo GT | 4.0 V8 twin-turbo | `V8` | 471 kW | 850 N·m | 6,800 | AWD | SUV |

The 992 GT3 at 9,000 rpm is the `Flat6` reference — clattery and mechanical at idle,
cleaning into a hard flat wail at the top, which is the opposite trajectory of most
engines and the detail that makes a flat-six recognisable.

### 3.6 Toyota — the I6 legend and an I3 turbo

| Vehicle | Engine | Family | Power | Torque | Drive | Slot |
|---|---|---|---|---|---|---|
| **Toyota Supra (A80)** | 2JZ-GTE 3.0 I6 twin-turbo | `I6` | 240 kW @ 5,600 | 431 N·m @ 3,600 | RWD | Sports |
| Toyota GR Supra (A90) | B58 3.0 I6 turbo | `I6` | 285 kW @ 5,800 | 500 N·m | RWD | Sports |
| **Toyota GR Yaris** | G16E-GTS 1.6 **I3 turbo** | `I3` | 200 kW @ 6,500 | 370 N·m | AWD | Hot Hatch |
| Toyota GR86 | FA24 2.4 flat-4 NA | `Flat6`* | 172 kW @ 7,000 | 250 N·m @ 3,700 | RWD | Sports |
| Toyota AE86 Corolla | 4A-GE 1.6 I4 NA | `I4` | 95 kW @ 6,600 | 149 N·m @ 5,200 | RWD | Classic |
| Toyota Land Cruiser (300) | 3.4 V6 twin-turbo | `V6Turbo` | 305 kW | 650 N·m | 4WD | SUV |
| Toyota Hilux | 2.8 I4 turbodiesel | `DieselI6`* | 150 kW | 500 N·m | 4WD | Pickup |

*`Flat6` and `DieselI6` are approximations for the flat-4 and the I4 diesel. If budget
allows, add `Flat4` and `DieselI4` families — a boxer four has a distinctive uneven
character that the flat-six set will not reproduce convincingly.

The GR Yaris is a rare modern **I3 turbo** and gives the Hot Hatch class a
1.5th-order engine that sounds unlike anything else in it.

### 3.7 Ford — the cross-plane / flat-plane demonstration

| Vehicle | Engine | Family | Power | Torque | Redline | Drive | Slot |
|---|---|---|---|---|---|---|---|
| **Ford Mustang GT (S550)** | Coyote 5.0 V8 NA **cross-plane** | `V8` | 343 kW @ 7,000 | 570 N·m @ 4,600 | 7,400 | RWD | Muscle |
| **Ford Mustang Shelby GT350** | Voodoo 5.2 V8 NA **flat-plane** | `V8` | 392 kW @ 7,500 | 582 N·m @ 4,750 | **8,250** | RWD | Muscle |
| Ford Mustang Shelby GT500 | Predator 5.2 V8 supercharged | `V8Supercharged` | 567 kW @ 7,300 | 847 N·m | 7,500 | RWD | Muscle |
| Ford Focus RS (Mk3) | 2.3 EcoBoost I4 turbo | `I4Turbo` | 257 kW @ 6,000 | 470 N·m | 6,800 | AWD | Hot Hatch |
| Ford GT (2017) | 3.5 EcoBoost V6 twin-turbo | `V6Turbo` | 482 kW @ 6,250 | 746 N·m | 7,000 | RWD | Super |
| Ford F-150 Raptor | 3.5 EcoBoost V6 twin-turbo | `V6Turbo` | 335 kW @ 5,850 | 691 N·m | 6,000 | 4WD | Pickup |

**Put the Mustang GT and the Shelby GT350 next to each other in the garage.** Same
brand, same body, same displacement class — and one burbles while the other screams,
purely because of crank geometry. It is the clearest possible in-game illustration of
the single most important idea in `docs/19`.

### 3.8 Dodge — supercharged muscle and a V10

| Vehicle | Engine | Family | Power | Torque | Drive | Slot |
|---|---|---|---|---|---|---|
| **Dodge Challenger SRT Hellcat** | 6.2 HEMI V8 **supercharged** | `V8Supercharged` | 527 kW @ 6,000 | 881 N·m @ 4,800 | RWD | Muscle |
| Dodge Challenger SRT Demon 170 | 6.2 HEMI V8 supercharged | `V8Supercharged` | 764 kW (E85) | 1,281 N·m | RWD | Muscle |
| Dodge Charger SRT Hellcat | 6.2 HEMI V8 supercharged | `V8Supercharged` | 527 kW @ 6,000 | 881 N·m | RWD | Sedan |
| Dodge Challenger R/T | 5.7 HEMI V8 NA cross-plane | `V8` | 276 kW @ 5,150 | 542 N·m | RWD | Muscle |
| **Dodge Viper ACR (Gen V)** | 8.4 **V10** NA | `V10` | 481 kW @ 6,200 | 813 N·m @ 5,000 | RWD | Super |
| Dodge Ram 1500 TRX | 6.2 HEMI V8 supercharged | `V8Supercharged` | 527 kW | 881 N·m | 4WD | Pickup |

The Hellcat's supercharger whine is the reference for the `V8Supercharged` layer in
`docs/19` §3 — a positive-displacement blower producing a whine that rises linearly with
rpm, sitting well above the exhaust fundamental. It **must** be its own audio layer or it
will pitch incorrectly during crossfades.

---

## 4. Engine family coverage

The requested brands cover almost the entire acoustic spectrum with no filler:

| Family | Covered by | Status |
|---|---|---|
| `I3` | Suzuki Mehran, Maruti 800, Alto, Toyota GR Yaris, BMW i8 | ✅ |
| `I4` | Honda S2000, Integra Type R, Toyota AE86 | ✅ |
| `I4Turbo` | Civic Type R, A45 AMG, Focus RS, Swift Sport | ✅ |
| `I6` | BMW M3 E46 / M2 / M3 G80, Toyota Supra A80 / A90 | ✅ |
| `V6` | Honda NSX NA1 | ✅ |
| `V6Turbo` | Ford GT, Raptor, Land Cruiser, NSX NC1 | ✅ |
| `Flat6` | Porsche 911 GT3, Turbo S, Cayman GT4 | ✅ |
| `V8` cross-plane | Mustang GT, C63 M156, SLS, Challenger R/T | ✅ |
| `V8` flat-plane | Shelby GT350, AMG GT R | ✅ |
| `V8Supercharged` | Hellcat, Demon, GT500, TRX | ✅ |
| `V10` | BMW M5 E60, Porsche Carrera GT, Dodge Viper | ✅ |
| `V12` | Mercedes-AMG S65, BMW 850CSi | ✅ |
| `Electric` | Porsche Taycan | ✅ |
| `DieselI6` | Toyota Hilux (approximate), traffic trucks | ⚠️ approximate |
| `Rotary` | **none** | ❌ |
| `MotorcycleI4` | **none** | ❌ |

**Two gaps.** Rotary needs Mazda (RX-7 FD or RX-8) — the only manufacturer that ships
one, and `docs/19` §3 flags rotary as the most distinctive sound in the game and a strong
reward-vehicle candidate. Motorcycles need a bike manufacturer; Suzuki is already on the
list and makes the GSX-R, which would keep the licensing surface unchanged.

---

## 5. Traffic vehicles

The traffic library (`docs/13` §4) should stay **generic and unbranded** even with the
licensed roster enabled, with three exceptions:

1. **Suzuki Mehran, Alto, and Cultus appear in traffic** on Middle Eastern Highway and
   any South Asian environment. Recognising your own first car in traffic is a genuinely
   strong moment for the target audience.
2. Toyota Hilux and Land Cruiser as regional traffic, same rationale.
3. Police units stay generic — no manufacturer wants their car modelled being rammed.

Everything else in traffic remains an unbranded archetype. This keeps the licensing
surface small, cuts modelling cost enormously, and nobody has ever complained that
background traffic lacked badges.

---

## 6. Migration checklist

- [x] `licensed` block added to the vehicle schema, optional, additive
- [x] `Budget` class added for the Mehran tier
- [x] `peakPowerKw` minimum lowered to 25, `zeroToHundredS` maximum raised to 30
- [ ] `HR_LICENSED_CONTENT` build flag wired into `UIManager` name resolution
- [ ] Per-vehicle `licensed.enabled` override for a mixed roster
- [ ] Invented-marque fallback verified for every vehicle (`T-LIC-02`)
- [ ] Mesh sets authored per identity — **this is the real cost**, not the naming
- [ ] Audio banks recorded or sourced per `docs/19` §5
- [ ] Store assets prepared in both identities

---

## 7. Tests

| ID | Assertion | Level |
|---|---|---|
| T-LIC-01 | Every licensed vehicle's specs match this document within 2% | CI |
| T-LIC-02 | **With `HR_LICENSED_CONTENT` off, no real manufacturer string appears anywhere in the build** — including meshes, audio bank names, and localization | CI |
| T-LIC-03 | Physics, class, price, and progression slot are byte-identical between identities | CI |
| T-LIC-04 | Per-vehicle override produces a correct mixed roster | Unit |
| T-LIC-05 | Every licensed vehicle maps to a valid `docs/19` engine family | CI |
| T-LIC-06 | The roster covers every engine family, or explicitly records the gap | CI |
| T-LIC-07 | No police or emergency vehicle carries a licensed identity | CI |

`T-LIC-02` is the important one. It is what makes "ship without licences" a build flag
rather than an audit.

---

## Sources

- [Suzuki Mehran — Wikipedia](https://en.wikipedia.org/wiki/Suzuki_Mehran)
- [Suzuki Mehran specs — PakWheels](https://www.pakwheels.com/new-cars/suzuki/mehran/)
- [Suzuki Mehran engine specs — Bloom Pakistan](https://bloompakistan.com/suzuki-mehran-engine-specs-2025/)
- [Maruti 800 — Wikipedia](https://en.wikipedia.org/wiki/Maruti_800)
- [Cross-plane and flat-plane V8 crankshafts and firing orders — Curbside Classic](https://www.curbsideclassic.com/blog/tech/curbside-tech-v8-engine-crankshafts-and-firing-orders-good-vibrations/)
- [Flat-plane vs cross-plane V8 differences — CarBuzz](https://carbuzz.com/flat-plane-v8-vs-cross-plane-v8-differences-explained/)
- [12 of the best-sounding V10 engines — SlashGear](https://www.slashgear.com/1908393/best-sounding-v10-engines/)
- [High-revving engines that sound better than V8s — CarBuzz](https://carbuzz.com/high-revving-engines-that-sound-better-than-v8s/)
