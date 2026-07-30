# 07 — Audio Design

Audio carries more of the speed sensation than graphics do. A player with their eyes
closed should be able to tell you roughly how fast they are going, what gear they are
in, what surface they are on, and whether something just passed them closely.

---

## 1. Engine audio model

**Not a pitched loop.** A multi-layer, load-blended, RPM-crossfaded model.

### 1.1 Structure per vehicle

```
                    ┌── ON-LOAD set  (throttle > 0)  ──┐
   RPM ──crossfade──┤                                  ├── load blend ──┐
                    └── OFF-LOAD set (overrun)       ──┘                │
                                                                        │
   Additional independent layers, each with its own RPM/load mapping:   ├─▶ Engine bus
     · Idle                                                             │
     · Intake                                                           │
     · Exhaust (rear-positioned emitter)                                │
     · Turbo spool (mapped to boost pressure)                           │
     · Blow-off valve (on throttle lift above boost threshold)          │
     · Supercharger whine (mapped to RPM, linear)                       │
     · Transmission whine (mapped to output shaft speed)                │
     · Differential whine (mapped to speed, quiet)                      │
     · Rev limiter bounce (event)                                       │
     · Backfire / pop (event, on lift and on shift)                     │
     · Starter (event)                                                  ─┘
```

- **Minimum 6 RPM bands** per set (idle, low, low-mid, mid, high, redline), crossfaded
  with equal-power curves over ±350 rpm overlap regions.
- **Load blend:** `blend = throttleInput` smoothed over 90 ms, mixing the ON and OFF
  sets. This is what makes lifting off sound *right* — the pop and overrun burble is
  half the character of a performance car.
- Sample rate 48 kHz, seamless loops, phase-aligned at band boundaries so crossfades do
  not comb-filter.

### 1.2 Engine families

Distinct sample sets required for: **I3, I4, I4 Turbo, I6, V6, V6 Turbo, V8, V8
Supercharged, V10, V12, Flat-6, Rotary, Electric, Diesel I6 (trucks), Motorcycle I4.**

15 families × ~14 layers × 6 bands ≈ 1,200 core engine samples. Vehicles within a family
differ by pitch offset (±3 semitones), EQ profile, exhaust layer swap, and turbo/blower
presence — this is how 80 vehicles get distinct voices from 15 recording sessions.

### 1.3 Electric vehicles
No gear shifts, no exhaust, no intake. Instead:
- Inverter whine: frequency mapped to motor RPM, amplitude to torque demand. Rises with
  a characteristic "spaceship" sweep under hard acceleration.
- Regen tone on lift: a descending whine.
- A subtle synthesized exterior pedestrian-warning tone below 30 km/h.
- Tire and wind noise become dominant — EVs must feel eerily quiet at speed, which
  makes them tactically different to drive by ear.

---

## 2. The speed bed

| Source | Mapping | Notes |
|---|---|---|
| Wind noise | Level `= lerp(-60, -8, s)` dB, low-pass `= lerp(2k, 16k, s)` Hz | The primary speed cue. Cockpit/bumper cams get more |
| Tire road noise | Per surface, level and spectrum mapped to speed | Asphalt, concrete, wet, gravel, snow, grass, rumble strip, bridge joint, painted line |
| Chassis creak | Suspension velocity events | Cheap, adds enormous weight |
| Body panel resonance | Speed + surface roughness | Low rumble, cars only |
| Expansion joints | Positional, on bridges | Rhythmic thumps — a great speed reference |
| Rumble strip | Contact | Loud, high-frequency, a warning as much as a sound |

Surface transitions crossfade over 120 ms. Tunnel entry applies a reverb send and a
hard low-pass on all exterior sources over 200 ms, then reverses on exit.

---

## 3. The near-miss whoosh

**The signature sound of the game.** Get this right before anything else in the audio
pass.

Layered:
1. **Body thump** — a low-frequency (60–140 Hz) pressure displacement, level scaled by
   the passing vehicle's mass and frontal area. A semi-truck's is physically
   intimidating; a motorcycle's is barely there.
2. **Air shear** — a broadband hiss, 2–9 kHz, level scaled by relative speed.
3. **Doppler** — real Doppler shift on both layers based on relative velocity. The
   pitch drop as it passes is the whole effect.
4. **Panning** — hard-panned to the side it passed, sweeping front-to-back over the
   pass duration.

On trigger: duck the music and ambience bus by 4 dB for 200 ms with a 30 ms attack and
a 180 ms release. Add a bright confirmation chime on the UI bus whose pitch rises with
the combo count — 20 distinct pitches spanning about an octave and a half, one per combo
step, so the sound of a long combo is *musical*. This is why players chase it.

For a `Close` near miss (< 0.55 m), add: a brief high-pass sweep on everything else, a
0.11 s time dilation, and a distinct sharper chime.

---

## 4. Adaptive music

Stem-based, not track-based. Each environment has a cue set of 3–5 pieces, each built
from 5 stems:

| Stem | Enters at |
|---|---|
| Ambient pad | Always |
| Percussion | Speed > 90 km/h |
| Bass | Speed > 150 km/h |
| Harmony / arp | Combo ≥ 3 |
| Lead | Combo ≥ 8 or speed > 250 km/h |

- Stem entries and exits are **quantized to the bar** so it never sounds like a mixer
  fader. Exits get a 1-bar tail.
- A dedicated **tension layer** rises per police star, replacing the harmony stem at
  ★★★+ and adding a driving percussion loop at ★★★★★.
- Music low-passes with speed (§3 of `docs/06-graphics-art.md`) and ducks under nitrous
  and near misses.
- On run end: a stinger quantized to the next beat, then a resolution into the results
  screen's ambient bed. Never a hard cut.
- Genre by environment: Modern City = electronic/breakbeat · Cyberpunk = synthwave/
  darksynth · Desert = desert rock/percussive · Japanese Expressway = city pop/
  future funk · Mountain Pass = drum & bass · Snow = ambient/downtempo · European
  Motorway = techno · American Interstate = rock · Coastal = house · Forest =
  organic electronica · Industrial = industrial techno · Airport = minimal ·
  Countryside = folk-electronic · Middle Eastern = electronic with regional
  instrumentation.

**Licensing:** all music is original commissioned work or properly licensed for
worldwide use in a commercial game including streaming. Verify streaming rights
explicitly — a soundtrack that gets streams DMCA'd is a marketing disaster.

---

## 5. Crash audio

Layered by impact energy and by material pair, assembled at runtime:

| Layer | Source |
|---|---|
| Sub impact | 30–80 Hz thud, scaled by energy |
| Primary impact | Material pair: metal/metal, metal/plastic, metal/concrete, metal/glass |
| Panel deformation | A groaning metal stress sound, length scaled by energy |
| Glass | Shatter + shard scatter tail |
| Plastic scatter | Bumper/trim fragments |
| Tire scrub | If the wheels were loaded at impact |
| Debris settle | 0.8–2.5 s tail of parts coming to rest |
| Alarm | Occasionally, on a destroyed traffic vehicle |

Above 60 kJ, add a 400 ms ear-ring tone with everything else low-passed and ducked by
12 dB, recovering over 1.2 s. It sells the violence without gore and it makes the crash
camera land.

---

## 6. Spatialization and mixing

- Full 3D spatialization with distance attenuation, air absorption (high-frequency
  rolloff with distance), and optional HRTF binaural for headphones.
- Occlusion: tunnels, underpasses, and large vehicles apply a low-pass + attenuation to
  sources behind them.
- Reverb zones per environment and per structure: open highway (none), tunnel (long,
  dark), underpass (short slap), city canyon (medium), forest (damped), desert (very
  dry), industrial (metallic).

### 6.1 Submix hierarchy

```
Master
├── Engine        (player engine, ducked by nothing)
├── Vehicle       (tires, wind, suspension, chassis)
├── Traffic       (other vehicles' engines and tires)
├── World         (ambience, weather, reverb sends)
├── Impacts       (crashes, scrapes, debris) — sidechains Music and World
├── Music         (adaptive stems) — sidechained by Impacts and NearMiss
├── UI            (menus, chimes, near-miss confirmation)
└── Voice         (police radio, announcer) — sidechains Music by 6 dB
```

Sliders exposed to the player: Master, Engine, SFX, Music, UI, Ambience (6).

### 6.2 Loudness and dynamic range
- Target −16 LUFS integrated for a typical run, true peak ≤ −1 dBTP.
- Full dynamic range by default. A **Night Mode** option applies a 3:1 compressor with
  a 6 dB range reduction for late-night play — a small feature players are
  disproportionately grateful for.
- No sound may exceed −6 dBFS peak except crash impacts.

---

## 7. UI and feedback audio

Every UI action gets a sound: navigate, select, back, purchase (with a distinct
satisfying cash sound), unlock (escalating fanfare by rarity), error, toggle, slider
tick, tab change, garage door, paint apply, part install (a mechanical clunk),
countdown, and record broken (a bright, unmistakable sting).

The **purchase and unlock sounds are load-bearing for the reward pillar.** Spend real
effort on them. A car unlock should sound like an event.

---

## 8. Voice content

| Content | Lines | Notes |
|---|---|---|
| Police dispatch | ~180 | Grammar-slotted (see `docs/04-traffic-ai.md` §8.6) |
| Police unit chatter | ~60 | Callouts on PIT, spike, roadblock, losing visual |
| Helicopter | ~25 | Distinct radio filter, overhead spatialization |
| Announcer (challenges) | ~40 | Optional, toggleable |
| Garage / menu VO | 0 | Deliberately none. Menus are silent. Text is faster |

All voice is subtitled with speaker labels, and all gameplay-critical voice lines have
a corresponding non-audio cue (HUD icon) for accessibility.

---

## 9. Audio acceptance tests

| Test | Assertion |
|---|---|
| Blind speed estimate | Testers estimate speed within 20% with the screen off |
| Blind car identification | Testers distinguish 5 engine families blind, > 80% accuracy |
| Near-miss latency | Sound begins within 60 ms of the detection frame |
| No clipping | 60-minute capture, zero samples above 0 dBFS |
| Loudness | Integrated LUFS within ±1 of target across all modes |
| Voice count | Never exceeds the 96-voice pool; culling is inaudible |
| Crossfade artifacts | Zero audible combing across engine RPM band boundaries |
| CPU | Audio thread ≤ 0.4 ms per frame at peak voice count |
