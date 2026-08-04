# 14 — Testing and QA

Every assertion scattered through the other documents, collected, given an ID, and
assigned an owner. `docs/00-index.md` links each requirement to the tests below.

**Rule:** a requirement with no test is not done. It is hoped for.

---

## 1. Test levels

| Level | What it covers | Runs | Blocks |
|---|---|---|---|
| **Unit** | Pure functions: scoring, IDM, curves, economy math | Every commit | Merge |
| **Headless sim** | Physics, road gen, traffic, missions — no renderer | Every commit | Merge |
| **Content validation** | `tools/validate_content.py` + JSON Schema | Every commit | Merge |
| **Integration** | Full game loop, scripted input, one tier | Every PR | Merge |
| **Performance** | 30-min captures per tier, frame-time percentiles | Nightly | Release |
| **Soak** | 60-min runs, memory and pool growth | Nightly | Release |
| **Determinism** | Same seed + trace across machines | Nightly | Release |
| **Screenshot matrix** | 14 env × 9 weather × 8 TOD = 1,008 captures | Weekly | M13 |
| **Manual playtest** | Feel, fun, fairness | Per milestone | Milestone |
| **Accessibility** | One full playthrough per mode | M16 | Release |
| **Localization** | Pseudo-loc, RTL, clipping | M17 | Release |
| **Platform cert** | Store requirements | M17 | Release |

**Headless is the backbone.** Physics, scoring, road generation, traffic, missions, and
economy must all run with no rendering. If a system cannot be tested headless, it has a
dependency it should not have.

---

## 2. The assertion register

### T-PHY — Physics (`docs/03` §9)

| ID | Assertion | Level |
|---|---|---|
| T-PHY-01 | 0–100 km/h per class within 5% of the `03` §7 table | Headless |
| T-PHY-02 | Top speed per class within 3% | Headless |
| T-PHY-03 | 100–0 braking within 8% of class target | Headless |
| T-PHY-04 | Determinism: same seed + trace = same position ±1 cm after 10 min | Headless |
| T-PHY-05 | No tunneling: 300 km/h into every collision type, 10k trials, zero passthrough | Headless |
| T-PHY-06 | Suspension stable over the worst chunk for 10 min, no divergence | Headless |
| T-PHY-07 | Driveable with all assists off — scripted lane change holds the lane | Headless |
| T-PHY-08 | Grip continuity: no discontinuity > 5% across any surface transition | Headless |
| T-PHY-09 | Combined slip never exceeds the friction ellipse | Unit |
| T-PHY-10 | Loss of control is telegraphed ≥ 250 ms before grip is lost | Headless |
| T-PHY-11 | All three transmissions shift correctly; auto never upshifts above 0.6 g lateral | Headless |
| T-PHY-12 | Nitrous capacity, refill, and combo acceleration match `03` §4.2 | Unit |

### T-AI — Traffic and police (`docs/04` §9)

| ID | Assertion | Level |
|---|---|---|
| T-AI-01 | **Solvability: 10,000 seeded runs × 20 km, zero unsolvable states** | Headless |
| T-AI-02 | **Near-Miss Contract: 10,000 near misses, zero collisions from post-pass AI action** | Headless |
| T-AI-03 | Rush Hour at 20 km produces ≥ 1 stop-wave per 3 min | Headless |
| T-AI-04 | Zero spawns inside the player's frustum on clear road, 100 runs | Integration |
| T-AI-05 | Personality traces are statistically separable | Headless |
| T-AI-06 | Determinism: same seed = identical traffic positions after 10 min | Headless |
| T-AI-07 | LOD transitions produce no position discontinuity > 5 cm | Headless |
| T-AI-08 | Zero pool growth over a 60-min run | Soak |
| T-AI-09 | Zero frames where visible road < 4.0 s at current speed | Integration |
| T-AI-10 | Indicators visible and blinking at 500 m on every quality tier | Integration |
| T-AI-11 | Indicator state survives every LOD transition without a missed blink | Integration |
| T-AI-12 | Signal timing per personality matches `04` §3.6; ≥ 54% of lane changes are signalled | Headless |
| T-AI-13 | Hazard lights active on every breakdown, pileup, and stationary vehicle | Headless |

### T-FLASH — Courtesy Flash (`docs/04` §3.7)

| ID | Assertion | Level |
|---|---|---|
| T-FLASH-01 | Yield rates per personality match the §3.7 table within 3% over 10,000 flashes | Headless |
| T-FLASH-02 | **A yielded pass awards zero near-miss points** | Unit |
| T-FLASH-03 | A willing driver with no acceptable gap does not move, and shows its indicator | Headless |
| T-FLASH-04 | Flashing can never create or remove a solvable path (§6 unaffected) | Headless |
| T-FLASH-05 | Repeat-flash penalty applies at −30% per repeat within 6 s | Unit |
| T-FLASH-06 | Cooldown of 2.5 s enforced; spam cannot exceed it | Unit |
| T-FLASH-07 | Exactly one vehicle responds per flash | Headless |
| T-FLASH-08 | Flashing police adds +6 heat and yields nobody | Unit |
| T-FLASH-09 | Disabled entirely in Hardcore | Unit |
| T-FLASH-10 | Environment multipliers applied and clamped to [0.05, 0.98] | Unit |
| T-FLASH-11 | Acceptance feedback fires before the vehicle physically moves | Integration |

### T-LIC — Licensed content (`docs/20`)

| ID | Assertion | Level |
|---|---|---|
| T-LIC-01 | Every licensed vehicle's specs match `docs/20` §3 within 2% | CI |
| T-LIC-02 | **With `HR_LICENSED_CONTENT` off, no real manufacturer string appears anywhere in the build** — meshes, audio bank names, localization, store metadata | CI |
| T-LIC-03 | Physics, class, price, and progression slot are byte-identical between identities | CI |
| T-LIC-04 | Per-vehicle `licensed.enabled` override produces a correct mixed roster | Unit |
| T-LIC-05 | Every licensed vehicle maps to a valid `docs/19` engine family | CI |
| T-LIC-06 | The roster covers every engine family, or the gap is explicitly recorded | CI |
| T-LIC-07 | No police or emergency vehicle carries a licensed identity | CI |

### T-FWD — Forward-only motion (`docs/05` §0)

| ID | Assertion | Level |
|---|---|---|
| T-FWD-01 | Longitudinal velocity along the spline never goes negative, under any input | Headless |
| T-FWD-02 | Chunk index is monotonically increasing across a 500 km run | Headless |
| T-FWD-03 | Passed chunks are freed; memory is flat regardless of run length | Soak |
| T-FWD-04 | No vehicle data contains a reverse ratio | CI |
| T-FWD-05 | Spin recovery triggers per §0.1 and suppresses spawns for 2.0 s | Headless |
| T-FWD-06 | Spin recovery is unreachable in modes where a spin ends the run | Headless |

### T-POL — Police (`docs/04` §8)

| ID | Assertion | Level |
|---|---|---|
| T-POL-01 | Heat accumulation and star thresholds match `04` §8.1 | Unit |
| T-POL-02 | Every roadblock across 5,000 spawns has a threadable gap | Headless |
| T-POL-03 | Spike strips visible ≥ 2.0 s before contact at any speed | Integration |
| T-POL-04 | PIT attempts telegraph ≥ 0.7 s before contact | Integration |
| T-POL-05 | Radio grammar produces no malformed line across 10,000 assemblies | Unit |
| T-POL-06 | Escape conditions trigger correctly; helicopter defeats line-of-sight escape | Headless |

### T-ROA — Road generation (`docs/05` §9)

| ID | Assertion | Level |
|---|---|---|
| T-ROA-01 | Seed S produces byte-identical descriptors across 3 runs, 2 machines | Headless |
| T-ROA-02 | Zero tangent discontinuities across 10,000 consecutive chunks | Headless |
| T-ROA-03 | Zero sightline violations at any speed to 385 km/h | Headless |
| T-ROA-04 | Zero grammar violations over 100,000 chunks | Headless |
| T-ROA-05 | **500 km drive: position error < 1 cm, zero visible jitter** | Headless |
| T-ROA-06 | Generation ≤ 4 ms worker, ≤ 0.8 ms game thread, over 10,000 chunks | Performance |
| T-ROA-07 | 30-min run, zero frames over budget attributable to generation | Performance |
| T-ROA-08 | Elevation over any 1 km window within ±25 m of zero | Headless |
| T-ROA-09 | Every lane-count change has a ≥ 180 m taper and advance signage | Headless |

### T-SCO — Scoring (`PROMPT.md` §8)

| ID | Assertion | Level |
|---|---|---|
| T-SCO-01 | Near-miss detection fires exactly per the §8.1 conditions; no false positives from sitting alongside | Unit |
| T-SCO-02 | Combo increments, window, reset, and cap behave per §8.2 | Unit |
| T-SCO-03 | The four worked examples in `01` §3.2 reproduce exactly | Unit |
| T-SCO-04 | Feedback begins within 60 ms of the detection frame | Integration |
| T-SCO-05 | Glancing blows under 12 km/h / 20° scrape rather than end the run | Headless |
| T-SCO-06 | Anti-exploit: cooldown, true-pass, relative-speed, off-road suppression all hold | Unit |
| T-SCO-07 | `coins == round(score × 0.30) × modeMul × prestigeBonus`, always | Unit |

### T-PRF — Performance (`docs/11` §9)

| ID | Assertion | Level |
|---|---|---|
| T-PRF-01 | 99th-percentile frame time ≤ 1.25 × target, 30 min, every tier | Performance |
| T-PRF-02 | **Zero frames > 2 × target over 30 min, every tier** | Performance |
| T-PRF-03 | Per-system budgets in `11` §2 respected at peak load | Performance |
| T-PRF-04 | Allocation-tracking build reports zero gameplay-tick allocations | Headless |
| T-PRF-05 | Memory growth < 2% from minute 10 to minute 60 | Soak |
| T-PRF-06 | All four upscalers function; DRS adjusts ≤ 5%/s | Integration |
| T-PRF-07 | Warm-cache run start ≤ 3 s; cold boot to menu ≤ 15 s | Integration |
| T-PRF-08 | Draw calls and VRAM within budget, worst-case scene, every tier | Performance |
| T-PRF-09 | Steam Deck: 45 fps locked, 30 min, thermals stable | Performance |

### T-ARC / T-SAV / T-DAT — Architecture, save, data

| ID | Assertion | Level |
|---|---|---|
| T-ARC-01 | Module dependency graph is acyclic; no upward references | Static |
| T-ARC-02 | Event bus rejects reentrant same-type emission | Unit |
| T-ARC-03 | No unseeded random call exists in any gameplay path | Static |
| T-SAV-01 | Save round-trips losslessly across all schema versions | Unit |
| T-SAV-02 | Corrupted save rolls back to a backup and notifies | Integration |
| T-SAV-03 | Migration chain runs v1→current without data loss | Unit |
| T-SAV-04 | Cloud sync conflict resolution keeps the higher-progress profile | Integration |
| T-DAT-01 | `validate_content.py` exits 0; malformed content fails the build | CI |
| T-DAT-02 | Every `*Key` resolves in every shipped language | CI |
| T-DAT-03 | Every asset reference resolves | CI |
| T-DAT-04 | Adding a mode/car/environment requires zero code changes | Manual |

### T-ECO — Economy (`docs/01` §8)

| ID | Assertion | Level |
|---|---|---|
| T-ECO-01 | No unlock on the intended path exceeds 90 min at its gate's income | Headless |
| T-ECO-02 | Every vehicle reachable without premium currency | Unit |
| T-ECO-03 | No upgrade tier grants > 18% of a stat in one step | Unit |
| T-ECO-04 | Level 100 reachable in ~42 h at median yield, ±15% | Headless |
| T-ECO-05 | Every mission and career step is completable and rewards correctly | Headless |
| T-ECO-06 | All 100 achievements are attainable; none unreachable | Headless |
| T-ECO-07 | Season Pass data model functions with the feature flag off | Unit |
| T-ECO-08 | Engine swaps apply mass and CoM deltas to physics | Headless |
| T-ECO-09 | **Zero token-purchasable items affect any stat** | CI |
| T-ECO-10 | First hour delivers ≥ 4 cars, ≥ 2 environments, ≥ 3 modes | Headless |
| T-ECO-11 | Vehicle usage Gini < 0.6 — no single dominant car | Headless |

### T-UX / T-ACC / T-LOC

| ID | Assertion | Level |
|---|---|---|
| T-UX-01 | Cold boot → driving in ≤ 25 s including logos | Integration |
| T-UX-02 | Crash → driving again in ≤ 1.5 s | Integration |
| T-UX-03 | Zero screens with an unreachable interactive element | Integration |
| T-UX-04 | Every HUD element toggles and scales 50–200% without overlap | Manual |
| T-UX-05 | Full playthrough gamepad-only, and keyboard-only, zero mouse | Manual |
| T-UX-06 | Every customization option applies visibly with no load | Manual |
| T-UX-07 | Testers report distance, score, and payout after 4 s exposure | Manual |
| T-UX-08 | Photo Mode exports at 4× resolution without artifacts | Manual |
| T-UX-09 | Difficulty presets write visibly to individual settings | Integration |
| T-UX-10 | UI ≤ 0.5 ms game thread, ≤ 0.6 ms GPU | Performance |
| T-ACC-01…12 | One item per `PROMPT.md` §18 entry, each verified by a full playthrough | Manual |
| T-LOC-01 | 14 languages complete, zero missing keys | CI |
| T-LOC-02 | Pseudo-loc at +40%: zero clipped or overlapping strings | Integration |
| T-LOC-03 | Arabic RTL fully mirrored, zero misaligned elements | Manual |

### T-AUD / T-CAM / T-VFX / T-GFX / T-WEA / T-CNT / T-MOD / T-NET / T-TEL

| ID | Assertion | Level |
|---|---|---|
| T-AUD-01 | Testers estimate speed within 20% with the screen off | Manual |
| T-AUD-02 | Testers distinguish 5 engine families blind, > 80% accuracy | Manual |
| T-AUD-03 | Near-miss audio begins within 60 ms | Integration |
| T-AUD-04 | 60-min capture: zero samples above 0 dBFS; LUFS within ±1 of target | Performance |
| T-AUD-05 | Crash layering selects correctly by energy and material pair | Unit |
| T-AUD-06 | Music stems enter and exit quantized to the bar | Integration |
| T-AUD-07 | Voice count never exceeds 96; culling inaudible; audio ≤ 0.4 ms | Performance |
| T-CAM-01 | All 8 cameras function; transitions never clip geometry | Manual |
| T-CAM-02 | Speed rig values match the `06` §3 curves at 0/150/300 km/h | Integration |
| T-VFX-01 | Particle and decal budgets respected; eviction prioritizes correctly | Performance |
| T-VFX-02 | Damage tiers trigger at the `03` §8.1 energy thresholds | Headless |
| T-VFX-03 | Deformation buffer caps at 16 impacts; merging is stable | Unit |
| T-VFX-04 | All 18 animations in `06` §9 present on every drivable vehicle | Manual |
| T-GFX-01 | Every tier renders every feature in its `06` §2 column | Integration |
| T-WEA-01 | All 9 weather states transition without cuts | Integration |
| T-WEA-02 | All 8 TOD presets blend continuously; lights switch on threshold | Integration |
| T-WEA-03 | 1,008-capture screenshot matrix reviewed, zero broken combinations | Weekly |
| T-CNT-01…05 | Content counts match `13`; no orphaned or unreachable content | CI |
| T-MOD-01 | All 15 modes playable; fail conditions correct | Integration |
| T-MOD-02 | A 16th mode can be added by JSON alone | Manual |
| T-NET-01 | Networking interfaces compile with the null implementation | Unit |
| T-NET-02 | Replay reproduces a run bit-identically from seed + trace | Headless |
| T-NET-03 | Server-side replay validation rejects a tampered submission | Integration |
| T-TEL-01 | Telemetry off by default in the EU build; opt-in persists | Integration |

---

## 3. Manual playtest protocol

Automated tests cannot tell you whether the game is fun. This protocol can.

### 3.1 Cadence
- **Every milestone:** 5 testers, 30 minutes each, at least 2 who have never played.
- **M1 and M4:** these are gates. 8 testers, and the gate criteria must pass.
- **Weekly from M6:** 2 testers, 20 minutes, tracking regression in feel.

### 3.2 Method
Hand over the build. Say **"drive"** and nothing else. Do not explain controls, do not
explain scoring, do not sit next to them narrating. Start a timer and take notes on:

| Observation | Why it matters |
|---|---|
| Time to first lean-in | Pillar 1 — speed reads or it does not |
| Words said aloud at the first near miss | Pillar 5 — the near miss is the loudest moment or it failed |
| Whether they restart before the results screen finishes | Pillar 11 — one more run |
| Time to first voluntary garage visit | Pillar 7 — reward is legible |
| Whether you have to ask for the controller back | The only metric that actually matters |
| Every death, and whether they blamed themselves or the game | Fairness — self-blame is good, game-blame is a bug |

**The last one is the highest-signal data in the project.** Log every death with the
tester's reaction. A death the player blames on the game is a defect in the solvability
solver, the Near-Miss Contract, the telegraph, or the sightline guarantee — find which.

### 3.3 The ship gate (`PROMPT.md` §22)
Five questions, five yeses required. Anything less means returning to M1 and fixing
feel — no amount of content compensates for a car that is not fun on an empty road.

---

## 4. CI pipeline

```
push ──▶ lint + static analysis ──▶ unit ──▶ content validation ──▶ headless sim
                                                                        │
                              ┌─────────────────────────────────────────┘
                              ▼
                     build (Dev, all platforms) ──▶ integration ──▶ artifact

nightly ──▶ performance (all tiers) ──▶ soak (60 min) ──▶ determinism (2 machines)
weekly  ──▶ screenshot matrix ──▶ economy simulation ──▶ regression report
```

**Merge blocks on:** lint, unit, content validation, headless sim, integration.
**Release blocks on:** everything, plus manual playtest sign-off and the §3.3 gate.

A performance regression > 5% opens a ticket automatically and is triaged same-day.

---

## 5. Bug severity

| Sev | Definition | Ship? | Examples |
|---|---|---|---|
| **P0** | Crash, data loss, progression block | Never | Save corruption, run cannot start |
| **P1** | Core loop broken or unfair | Never | Unsolvable spawn, hitch > 40 ms, Near-Miss Contract violated, tunneling |
| **P2** | Feature broken, workaround exists | Only with sign-off | A camera mode clips, a mission miscounts |
| **P3** | Visual or audio defect | Yes, tracked | LOD pop, a mistimed sound |
| **P4** | Polish | Yes | A one-pixel alignment issue |

**Unfairness is P1, not P2.** A player killed by something they could not have seen or
predicted will not file a bug — they will stop playing.

---

## 6. What is deliberately not tested

Stated so the gaps are conscious:

- **Fun.** No automated proxy exists. §3 is the substitute.
- **Art quality.** Reviewed, not tested. The screenshot matrix catches breakage, not
  ugliness.
- **Music.** Subjective. Mixed and reviewed, not asserted.
- **Long-term retention.** Requires live telemetry post-launch (`docs/16` §3).
- **Balance against real players.** The economy harness models a *design assumption*
  about skill distribution. Only launch data validates it, and `docs/16` §4 defines how
  the model gets corrected.
