# 09 — Progression, Economy, Missions, Achievements

---

## 1. Currencies

| Currency | Symbol | Earned from | Spent on | Typical run yield |
|---|---|---|---|---|
| **Coins** | ⬤ | Every run: distance, near misses, combos, speed | Vehicles, upgrades, most cosmetics | 8,000–45,000 |
| **Cash** | ▣ | Missions, achievements, level-ups, first-clear bonuses, career milestones | Premium vehicles, upgrade tiers 4–5, rare cosmetics | 0–400 |
| **Tokens** | ◆ | Weekly/monthly events, achievements, ~40/week free, optional purchase | **Cosmetics only, never stats** | 0–15 |

**Hard rule:** no Token purchase may ever affect a stat, a payout rate, or an unlock
speed. Tokens buy paint, wraps, decals, underglow, rims, and plate frames. That is the
whole list, and it is enforced by an automated test (`docs/01-game-design.md` §8).

---

## 2. Coin income model

All driving income flows through score. There is exactly one conversion, defined in
`PROMPT.md` §8.3:

```
score = nearMissPoints + distancePoints + speedPoints + bonusPoints
coins = round(score * 0.30) * modeMultiplier * prestigeBonus
```

Nothing in the game awards coins directly from a driving event. This matters: it means
the leaderboard number and the payout number can never disagree, and a player who
optimizes for score is automatically optimizing for money.

### 2.1 Income benchmarks (design targets — verify by simulation)

Coins/hour accounts for time spent outside runs (menus, garage, mode selection), which
falls as players settle into a loop. Runs/hour is `3600 / (runLength + overhead)`.

| Skill | Run length | Overhead | Runs/hr | Score/run | Coins/run | Coins/hour |
|---|---|---|---|---|---|---|
| New player | 70 s | 50 s | 30.0 | 8,000 | 2,400 | 72,000 |
| Casual (hour 2) | 3 min | 45 s | 16.0 | 36,700 | 11,000 | 176,000 |
| Competent (hour 10) | 6 min | 40 s | 9.0 | 126,700 | 38,000 | 342,000 |
| Skilled (hour 30) | 9 min | 35 s | 6.3 | 260,000 | 78,000 | 488,000 |
| Expert | 14 min | 30 s | 4.1 | 550,000 | 165,000 | 683,000 |

The curve flattens deliberately at the top — skill should roughly multiply income by
~9× from new player to expert, not 100×, or the late game trivializes and the mid game
feels punitive. Note that most of that 9× comes from *longer runs*, not from a higher
rate: expert score per minute is only about 2.4× a casual player's.

---

## 3. Vehicle pricing

```
price = basePrice(class) * performanceFactor * rarityFactor
```

| Class | Price range (Coins) | Cash alternative | Driver level gate |
|---|---|---|---|
| Starter | 0 (owned) | — | 1 |
| Economy | 12,000 – 30,000 | — | 1 |
| Hot Hatch | 45,000 – 95,000 | — | 4 |
| Sedan | 60,000 – 140,000 | — | 6 |
| Classic | 80,000 – 220,000 | — | 8 |
| SUV | 90,000 – 190,000 | — | 8 |
| Pickup | 85,000 – 175,000 | — | 10 |
| Van | 70,000 – 120,000 | — | 10 |
| Muscle | 180,000 – 420,000 | — | 14 |
| Off-Road | 200,000 – 380,000 | — | 16 |
| Sports | 260,000 – 620,000 | — | 18 |
| Luxury | 340,000 – 700,000 | — | 22 |
| Electric | 400,000 – 950,000 | 220 ▣ | 26 |
| Bike | 320,000 – 780,000 | 180 ▣ | 30 |
| Super | 900,000 – 2,400,000 | 480 ▣ | 34 |
| Track | 1,600,000 – 3,200,000 | 620 ▣ | 45 |
| Hyper | 2,800,000 – 6,500,000 | 950 ▣ | 55 |
| Special | Event / achievement only | — | varies |

**Grind guard:** the most expensive vehicle (6.5 M) against expert income
(683 k/hour) is 9.5 hours — but it is gated at driver level 80, so by the time a player
can buy it they have 30+ hours invested and several income sources running. The
automated balance test asserts that no *single next unlock* on the intended progression
path exceeds 90 minutes at the income level of a player who has just reached its gate.

---

## 4. Upgrades

10 categories × 5 tiers per vehicle. Prices scale with the vehicle's base price so an
economy car is cheap to max and a hyper car is a project.

```
tierPrice(n) = vehicleBasePrice * [0.04, 0.08, 0.15, 0.26, 0.42][n-1]
Tiers 4 and 5 additionally cost Cash: [0, 0, 0, 25 ▣, 60 ▣]
Full max on one vehicle ≈ 95% of its purchase price + 85 ▣
```

| Category | Per-tier effect | Cap at T5 |
|---|---|---|
| Engine | +6% peak torque | +30% |
| Turbo / Blower | +5% torque, +8% boost response, adds audio layer | +25% |
| Nitrous | +1.0 s capacity, −1.0 s refill | 9.0 s / 7 s refill |
| Transmission | −18% shift time, +1 usable gear ratio spread | −72% shift time |
| Tires | Compound upgrade path (see `docs/03` §3.2) | Semi-Slick |
| Brakes | +8% brake torque, −6% fade | +40% |
| Suspension | +7% roll stiffness, +5% grip in transitions | +35% |
| Weight reduction | −2.5% mass | −12.5% |
| Aero | +9% downforce, +2% drag | +45% downforce |
| Cooling | −15% heat buildup (affects sustained power and brake fade) | −75% |

**Every tier displays exact numeric deltas before purchase.** No hidden stats, ever.
Show the before/after on the stat bars and the resulting 0–100 and top speed.

**Downgrade/refund:** upgrades can be sold back at 60% for Coins. Players experiment
more when experimentation is not permanent, and more experimentation means more
engagement with the garage.

---

## 5. Driver level

```
xpFromRun = distanceKm * 12
          + nearMisses * 3
          + closeNearMisses * 5
          + missionXp
          + (perfectRun ? 150 : 0)
          + modeXpBonus

xpForLevel(n) = round(300 + 5 * n^1.7)          // XP to advance FROM level n TO n+1
```

| From level | XP required | Cumulative |
|---|---|---|
| 1 → 2 | 305 | 305 |
| 10 → 11 | 550 | ~4,000 |
| 25 → 26 | 1,490 | ~19,000 |
| 50 → 51 | 4,165 | ~86,000 |
| 75 → 76 | 7,990 | ~232,000 |
| 99 → 100 | 12,650 | **~482,000** |

**Sanity check against income:** a competent player's run yields roughly
`28 km × 12 + 180 × 3 + 40 × 5 + missions ≈ 1,280 XP`, at 9 runs/hour ≈ 11,500 XP/hour.
482,000 / 11,500 ≈ **42 hours to level 100**, which is the design target. If the XP
formula or the run-yield formula changes, this arithmetic must be redone — the economy
harness (§11) asserts it.

**Level rewards:** Cash at every level (`25 + level * 4`), a vehicle-class unlock at
gates (see §3), a cosmetic at every 5th, a Token grant at every 10th, and a new mode at
levels 3, 6, 11, 17, 24, 32, 41.

**Prestige** at 100: reset to level 1, keep everything owned, gain a permanent
`+2% coins` bonus (max +20% at 10 prestiges) and a visible prestige badge on
leaderboards. Prestige is optional and reversible in the sense that nothing is lost.

---

## 6. Missions

### 6.1 Daily (6 per day, 1 free reroll)
Generated from a weighted template pool, scaled to the player's level. Reward:
2,000–8,000 Coins + 15–40 Cash each; completing all 6 grants a bonus 5 ◆.

Templates: `DriveDistance(n km, in one run)` · `ReachSpeed(n km/h)` ·
`NearMisses(n, in one run)` · `Overtakes(n)` · `NoContactRun(n km)` ·
`MaintainCombo(×n for t seconds)` · `CompleteMode(mode)` · `DriveInWeather(weather, n km)` ·
`DriveAtNight(n km)` · `UseVehicleClass(class, n km)` · `EscapePolice(n stars)` ·
`ThreadRoadblock(n)` · `EarnCoins(n in one run)` · `AirtimeSeconds(n)` ·
`OncomingDistance(n km)` · `NitrousDistance(n km)`

### 6.2 Weekly (4 per week)
Larger cumulative versions. Reward: 40,000–120,000 Coins + 80–200 Cash + 10 ◆ each.

### 6.3 Career ladder (120 steps)
A linear, always-visible progression spine that gives direction to players who do not
self-motivate. Each step names a concrete goal and pays Coins + Cash; every 10th step
pays a vehicle, environment, or exclusive cosmetic.

Sample steps: `#1 Drive 1 km` · `#8 Reach 200 km/h` · `#15 50 near misses in one run` ·
`#23 Complete a Two-Way run of 5 km` · `#34 Escape a 3-star pursuit` ·
`#47 Hold a ×10 combo for 30 s` · `#61 Drive 15 km in a blizzard` ·
`#78 Thread 5 roadblocks in one run` · `#95 Reach 350 km/h` ·
`#110 A 25 km run with zero contact` · `#120 Max out any hyper car`.

### 6.4 Evaluation
Missions are pure data. `MissionManager` consumes the `FGameplayEvent` stream and
evaluates each active objective against a small expression grammar:

```jsonc
{ "type": "counter", "event": "NearMiss", "scope": "run",
  "filter": { "clearance": { "lt": 0.55 } }, "target": 25 }
```

Adding a new mission type must require a new *filter field*, not new code.

---

## 7. Statistics tracked

Lifetime and per-vehicle: distance, time driven, top speed, runs, crashes, near misses,
close near misses, overtakes, best combo, longest no-contact run, coins earned, coins
spent, nitrous used, airtime, distance per environment, distance per weather, distance
per TOD, police pursuits started/escaped/busted, roadblocks threaded, spike strips hit,
favorite car, favorite mode, average run length, deaths per km, and a full histogram of
run distances.

Statistics are their own screen with sortable tables and a few charts. Players who care
about stats are the players who stay.

---

## 8. Achievements — structure

100 total: 70 visible, 20 skill-gated (visible but hard), 10 hidden. Full list in
`docs/13-content-manifest.md` §5.

| Tier | Count | Reward |
|---|---|---|
| Bronze | 40 | 5,000 ⬤ + 10 ▣ |
| Silver | 30 | 20,000 ⬤ + 30 ▣ |
| Gold | 20 | 75,000 ⬤ + 80 ▣ + 5 ◆ |
| Platinum | 9 | 250,000 ⬤ + 200 ▣ + 20 ◆ + a cosmetic |
| Completion | 1 | An exclusive vehicle |

Wire to Steam achievements behind an `IAchievementBackend` interface so the platform is
swappable without touching the achievement definitions.

---

## 9. Leaderboards

| Axis | Options |
|---|---|
| Period | Daily · Weekly · Monthly · All-Time |
| Scope | Global · Friends · Country |
| Metric | Score · Distance · Near Misses · Top Speed · Best Combo |
| Filter | Mode · Environment · Vehicle class |

Every submission stores `{ seed, mode, modifiers, vehicleConfig, inputTrace, checksum }`.
The server validates by re-simulating the input trace headlessly and comparing the
result — this is why determinism is a hard architectural requirement. Any mismatch is
rejected and flagged.

Ghost data from the top 100 of each board is downloadable and raceable.

---

## 10. Season Pass (built, shipped disabled)

50 tiers over 8 weeks. Free track (18 rewards) and Premium track (32 rewards), premium
costs 950 ◆ or real money. **Cosmetics, Coins, and Tokens only — never stats, never
vehicles that are not later purchasable.** Tier XP comes from the same event stream as
missions.

Ship v1 with `bSeasonPassEnabled = false`. The data model, UI, and reward pipeline all
exist and are tested, so enabling it post-launch is a config change rather than a
three-month retrofit.

---

## 11. Economy simulation harness

A headless tool that simulates N players over M hours at a given skill profile and
reports:

- Time to each unlock on the intended path
- Currency balance over time (are players ever coin-starved? coin-flooded?)
- Whether the §4 unlock cadence targets in `docs/01` are met
- The Gini coefficient of vehicle usage (is one car dominant? if so, it is overtuned)
- Whether any single next-unlock exceeds 90 minutes

Run it in CI on every economy data change. Balance is a data problem and must be
validated like one.
