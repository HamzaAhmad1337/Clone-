# 19 — Engine Audio Reference

The acoustic engineering behind the 15 engine families in `docs/07` §1.2. This is the
document a sound designer works from.

---

## 0. A note on real cars

Research for this document drew on the enthusiast and engineering consensus about which
engines sound best and *why*. That research is reflected here as **physics, not
badges**.

Firing order, crank geometry, engine order, harmonic content, and redline are
engineering facts and cannot be owned by anyone. Marque names, model names, body shapes,
and recorded audio of a specific production car are property, and `PROMPT.md` §0 rule 1
forbids using them.

So this document describes each family by what makes it sound the way it does. An
invented Corso V12 sounds like a great Italian V12 because it *is* a 60° V12 with the
same firing order and the same 6th-order fundamental — not because it borrowed a name.

**If you want real licensed vehicles instead**, that is a business decision, not a
technical one: it requires per-manufacturer licensing agreements, typically covering
name, likeness, and sound, negotiated individually and often costing more than the rest
of the audio budget combined. The architecture supports it — `engineBank` is just a data
field — but nothing in this repo assumes it, and the spec ships legally clean without it.

---

## 1. The one number that matters: engine order

Every engine's fundamental exhaust frequency is determined by how often it fires.

For a four-stroke, each cylinder fires once per **two** crankshaft revolutions:

```
engineOrder      = cylinders / 2
fundamentalHz    = (RPM / 60) × engineOrder
```

This single formula anchors all engine sound design. Get it wrong and the engine sounds
like the wrong engine no matter how good the samples are.

| Configuration | Order | Fundamental at 3,000 rpm | At redline | Redline used |
|---|---|---|---|---|
| I3 | 1.5 | 75 Hz | 175 Hz | 7,000 |
| I4 | 2.0 | 100 Hz | 250 Hz | 7,500 |
| I4 Turbo | 2.0 | 100 Hz | 233 Hz | 7,000 |
| V6 | 3.0 | 150 Hz | 350 Hz | 7,000 |
| V6 Turbo | 3.0 | 150 Hz | 360 Hz | 7,200 |
| I6 | 3.0 | 150 Hz | 400 Hz | 8,000 |
| Flat-6 | 3.0 | 150 Hz | 450 Hz | 9,000 |
| V8 cross-plane | 4.0 | 200 Hz | 467 Hz | 7,000 |
| V8 flat-plane | 4.0 | 200 Hz | 600 Hz | 9,000 |
| V8 supercharged | 4.0 | 200 Hz | 433 Hz | 6,500 |
| V10 | 5.0 | 250 Hz | 708 Hz | 8,500 |
| V12 | 6.0 | 300 Hz | 900 Hz | 9,000 |
| Diesel I6 | 3.0 | 150 Hz | 175 Hz | 3,500 |
| Rotary (2-rotor) | 2.0 | 100 Hz | 300 Hz | 9,000 |
| Motorcycle I4 | 2.0 | 100 Hz | 400 Hz | 12,000 |
| Electric | — | inverter whine, not firing | — | — |

**Implementation:** the fundamental and its first 6 harmonics must be present and
correctly spaced in every sample set. If you synthesize or resynthesize, generate from
this table. If you record, verify with a spectrum analyser that the peaks land where
this table says they should.

---

## 2. The crank that changes everything: cross-plane vs flat-plane V8

The single most audible engineering choice in the whole roster, and the one most games
get wrong by treating "V8" as one sound.

| | Cross-plane V8 | Flat-plane V8 |
|---|---|---|
| Crank throws | 90° intervals (a `+` viewed end-on) | 180° intervals (flat) |
| Firing per bank | **Uneven** — two cylinders in the same bank fire consecutively at some point in the order | **Even** — banks alternate cleanly, cross-bank pairs |
| Result | Low-frequency pressure overlap between cylinders | Evenly spaced exhaust pulses per bank |
| Character | Deep, lopey burble and rumble. The American muscle sound | High-frequency harmonics, a flat metallic scream. The European exotic sound |
| Balance | Smoother — the counterweighted crank cancels secondary forces | Rougher, but lighter crank allows much higher rpm |
| Typical redline | 6,500–7,000 | 8,500–9,000+ |
| Spectral signature | Strong energy below 300 Hz, irregular pulse spacing audible as beating | Energy spread up to 3 kHz, regular pulse train |
| Highway Rush family | `V8` | *(assign to `V8` variants on Super/Track classes)* |

**Design directive:** Kestrel (muscle) uses cross-plane exclusively. Aurel and Axiom
(sports/super/track) use flat-plane. A player must be able to tell a Kestrel Ravager
from an Aurel Falco with their eyes shut, and this is how.

---

## 3. Family reference

For each: what produces the character, and what the sample set must capture.

### I3 — `I3`
Odd cylinder count, 1.5th order, inherent primary imbalance producing a characteristic
thrum and a slight warble at idle. Thin, buzzy, cheerful. Used for Starter and Economy.
**Capture:** the off-beat idle wobble. It is the whole personality of the engine.

### I4 / I4 Turbo — `I4`, `I4Turbo`
2nd order, even firing, inherently balanced but with a strong secondary imbalance that
gives the familiar four-cylinder drone. Turbo variants add spool, blow-off, and a
noticeably muted exhaust note — the turbine absorbs high-frequency energy.
**Capture:** the turbo variant needs boost-pressure-mapped spool as its own layer, plus
a blow-off event on lift above threshold.

### V6 / V6 Turbo — `V6`, `V6Turbo`
3rd order. A 60° V6 is well balanced and sounds smooth and slightly nasal; a 90° V6
(common where it shares tooling with a V8) has uneven firing and a coarser, harder edge.
Pick 60° for Luxury and Sedan, 90° for Sports.
**Capture:** both bank angles. They are genuinely different engines acoustically.

### I6 — `I6`
3rd order and **perfectly balanced** in both primary and secondary orders — the reason
inline-sixes sound so smooth and can rev cleanly. Naturally aspirated versions are
raspy and metallic at low rpm with a whirring mechanical quality, developing into an
aggressive hard-edged growl as revs climb.
**Capture:** the mechanical whir at low rpm. It is what separates a great I6 from a
generic six.

### Flat-6 — `Flat6`
3rd order like an I6, but the horizontally opposed layout and rear placement produce a
distinctive off-beat thrash and a hard mechanical clatter at low rpm that cleans into a
flat, hard wail at high rpm.
**Capture:** the low-rpm clatter, and the fact that it gets *smoother* as it revs, which
is the opposite of most engines.

### V8 cross-plane — `V8`
See §2. Deep burble, lopey idle, massive low-frequency content. The idle is the money
shot: an uneven, syncopated pattern that no other configuration produces.
**Capture:** a long, clean idle loop. Players judge a muscle car at idle in the garage.

### V8 supercharged — `V8Supercharged`
Cross-plane base plus a **positive-displacement blower whine** that is linear in rpm and
sits well above the exhaust fundamental — typically 3–6 kHz at high rpm. The whine must
be its own layer mapped directly to rpm, not baked into the exhaust samples, or it will
pitch incorrectly during crossfades.
**Capture:** the whine in isolation, at constant load, across the full rev range.

### V10 — `V10`
5th order. Odd bank pairing gives a complex, slightly uneven pulse train, and the high
order puts the fundamental up around 700 Hz at redline — squarely in the ear's most
sensitive region. The result is the exotic, high-pitched, near-F1 scream with a tenor
wail that builds in both pitch and intensity toward redline.
**Capture:** the top third of the rev range in the finest rpm increments in the whole
project. This is the signature sound of the Super class and it must not step or comb.

### V12 — `V12`
6th order, the highest fundamental in the roster. Two banks of six, each inherently
balanced, so a V12 is the smoothest configuration made. Rich and full-bodied at low rpm
— a deep bellow — opening to a spine-tingling shriek with a hard aggressive edge at the
top. Modern extremes reach 12,000 rpm.
**Capture:** the transition. A V12 is two entirely different sounds at 2,000 and 8,000
rpm, and the journey between them is the reason the class exists.

### Rotary — `Rotary`
No pistons, no valves. A two-rotor Wankel fires twice per eccentric-shaft revolution
(2nd order), but port timing and the absence of poppet valves produce a piercing,
turbine-like scream with a distinctive whine and buzz that intensifies dramatically at
high rpm. Almost no low-frequency content — a rotary is *thin* and *loud*.
**Capture:** the buzz. Never treat a rotary as a small piston engine; the spectral
envelope is fundamentally different.

### Diesel I6 — `DieselI6`
Low redline, huge low-frequency content, prominent combustion knock, turbo spool, and
noticeable injector clatter. Used for traffic semi-trucks.
**Capture:** the knock and clatter. A diesel that sounds smooth sounds wrong.

### Motorcycle I4 — `MotorcycleI4`
2nd order but revving to 12,000+, so the fundamental reaches 400 Hz with harmonics far
above. Thin, frantic, screaming. Almost no mass to the sound.
**Capture:** the full rev range including over-run popping, which bikes do loudly.

### Electric — `Electric`
No firing order. Model instead:
- **Inverter whine:** frequency proportional to motor rpm, amplitude to torque demand.
  Sweeps upward under hard acceleration, giving the characteristic "spaceship" rise.
- **Regen tone:** descending whine on lift.
- **Gear reduction whine:** a single fixed ratio, so one continuous tone.
- **No shifts, no exhaust, no intake.**

The design goal is that tyre and wind noise become dominant. An EV must feel eerily
quiet at speed, so that driving one is a genuinely different sensory experience — and
so that traffic EVs are a real hazard because you cannot hear them coming.

---

## 4. Synthesis approach

Two viable methods. **Highway Rush uses crossfaded loops with load blending** as the
shipping approach, matching `docs/07` §1.

| | Crossfaded loops (chosen) | Granular synthesis |
|---|---|---|
| Method | Static loops at fixed rpm bands, crossfaded and pitch-shifted between | Sample split into grains, traversed by rpm without pitch-shifting artefacts |
| Pros | Predictable, cheap at runtime, well-understood tooling, best raw fidelity | Smoother rpm sweeps, no comb-filtering, less loop-point editing |
| Cons | Hours of loop-point editing per band; crossfades can comb if phases misalign | Higher CPU; grain artefacts if poorly tuned; harder to art-direct |
| Use | All 15 families | Evaluate for V10 and V12, where the rev sweep is the entire appeal |

**Both approaches require the same recording work**, so this decision can be deferred to
M7 and made per family. If the V10 sweep combs under crossfading and cannot be fixed
with phase alignment, switch that one family to granular rather than accepting a stepped
scream.

### 4.1 Load blending
The critical detail, and the thing that separates a convincing engine from a pitched
loop: **two complete sample sets per engine**, one recorded on-load (under throttle) and
one off-load (over-run), blended by throttle position smoothed over 90 ms.

The over-run set is where the character lives — the burble, the pops, the deceleration
whine. An engine with only an on-load set sounds synthetic the instant the player lifts,
which at highway speed is constantly.

---

## 5. Recording specification

If recording real vehicles for reference or for the invented marques' source material:

| Parameter | Requirement |
|---|---|
| Sample rate / depth | 96 kHz / 24-bit capture, delivered at 48 kHz / 16-bit |
| Microphone positions | Exhaust (0.5 m, 45° off-axis), intake, engine bay, interior driver-ear, exterior pass-by |
| Load capture | Dyno preferred: hold each rpm band steady at full load, then at zero load |
| RPM bands | Minimum 6; 10+ for V10, V12, and Rotary |
| Loop length | ≥ 4 s per band at constant rpm, for clean loop-point selection |
| Events | Start, stop, rev-limiter bounce, gear-shift cut, backfire, blow-off, over-run pops |
| Phase | Align loop points at zero-crossings on the fundamental, or crossfades will comb |
| Noise floor | ≤ −60 dBFS; no wind, no tyre noise, no bystanders |

**Verify every delivered set against the §1 order table with a spectrum analyser.** A V8
whose fundamental sits at 3rd order is an I6 wearing a V8's name, and players who cannot
articulate why will still say it "sounds wrong."

---

## 6. Family → class assignment

| Class | Family | Why |
|---|---|---|
| Starter, Economy | `I3`, `I4` | Thin, cheap, honest |
| Hot Hatch | `I4Turbo` | Spool and blow-off are half the appeal |
| Sedan | `V6`, `I4Turbo` | 60° V6 for smoothness |
| Luxury | `V6`, `V8`, `V12` | Refinement; V12 for the flagship |
| Muscle | `V8` (cross-plane), `V8Supercharged` | **Cross-plane only.** The burble is the class |
| Sports | `Flat6`, `I6`, `V6Turbo` | High-revving, mechanical, characterful |
| Super | `V8` flat-plane, `V10` | The scream |
| Hyper | `V12`, `V10` | The highest fundamentals in the game |
| Track | `V8` flat-plane, `V10` | Stripped, loud, no insulation |
| Classic | `I6`, `V8` (cross-plane) | Period-correct: carburettor lumpiness, no rev limiter |
| SUV, Pickup, Off-Road | `V8`, `V6Turbo`, `DieselI6` | Torque, not revs |
| Van | `I4Turbo`, `DieselI6` | Deliberately unglamorous |
| Electric | `Electric` | Its own model entirely |
| Bike | `MotorcycleI4` | 12,000 rpm scream |
| Special | Varies | Rotary lives here — a unique-feeling unlock |

**Roster acoustic coverage check:** the 80 vehicles must include at least one of every
family. The rotary in particular should be a reward vehicle, because it is the most
distinctive sound in the game and works best as a surprise.

---

## 7. Tests

| ID | Assertion | Level |
|---|---|---|
| T-AUD-08 | Every family's measured fundamental matches the §1 order table within 2% across the rev range | Automated (FFT) |
| T-AUD-09 | Cross-plane and flat-plane V8s are distinguishable blind by > 90% of testers | Manual |
| T-AUD-10 | Every family has both on-load and off-load sample sets; lifting is audibly different | Manual |
| T-AUD-11 | No audible comb-filtering at any rpm band boundary, swept 0 → redline | Manual |
| T-AUD-12 | Supercharger and turbo layers pitch correctly and independently of the exhaust crossfade | Manual |
| T-AUD-13 | The roster covers all 15 families | CI |
| T-AUD-14 | EV inverter whine tracks rpm and torque with no firing-order content present | Automated (FFT) |

---

## Sources

Engineering and consensus references used in compiling this document:

- [Cross-Plane and Flat-Plane V8 Crankshafts and Firing Orders — Curbside Classic](https://www.curbsideclassic.com/blog/tech/curbside-tech-v8-engine-crankshafts-and-firing-orders-good-vibrations/)
- [Flat-Plane V8 vs. Cross-Plane V8: Actual Differences Explained — CarBuzz](https://carbuzz.com/flat-plane-v8-vs-cross-plane-v8-differences-explained/)
- [Cross-plane vs flat-plane cranks explained by sound, feel, and power — Fast Lane Only](https://fastlaneonly.com/cross-plane-vs-flat-plane-cranks-explained-by-sound-feel-and-power/)
- [Engine Sound Modeling: From Sampling to Granular Synthesis in Wwise — Audiokinetic](https://www.audiokinetic.com/en/community/blog/engine-sound-modeling-from-sampling-to-granular-synthesis-in-wwise/)
- [The Car Engine Sound Primer — BOOM Library](https://www.boomlibrary.com/blog/the-car-engine-sound-primer-mike-caviezel/)
- [Evaluation of Car Engine Sound Design Methods in Video Games — af Malmborg (DiVA)](https://www.diva-portal.org/smash/get/diva2:1557027/FULLTEXT01.pdf)
- [Vehicle Engine design — Project CARS, Forza Motorsport 5 and REV — Designing Sound](https://designingsound.org/2014/08/11/vehicle-engine-design-project-cars-forza-motorsport-5-and-rev/)
- [12 Of The Best-Sounding V10 Engines Ever Made — SlashGear](https://www.slashgear.com/1908393/best-sounding-v10-engines/)
- [The Greatest Sounding Cars of All Time — Valvetronic Designs](https://valvetronic.com/blogs/blog/the-greatest-sounding-cars-of-2025-the-ultimate-enthusiast-guide)
- [10 High-Revving Engines That Sound Better Than V8s — CarBuzz](https://carbuzz.com/high-revving-engines-that-sound-better-than-v8s/)
