# 16 — Analytics, Telemetry, and Live Balance

The economy harness models an *assumption* about how people play. Telemetry is how that
assumption gets corrected. Without it, balance is guesswork with extra steps.

---

## 1. Consent and privacy

**Non-negotiable:**
- Telemetry is **opt-in**, presented once on first launch as a clear, honest screen —
  not a pre-checked box, not buried in Settings.
- Default is **off in the EU build**, and off everywhere for players who decline.
- Declining has zero gameplay consequence. No feature, reward, or leaderboard depends on
  it.
- No personally identifying data, ever: no name, no email, no IP retention beyond the
  request, no precise location. A random install-scoped GUID only, resettable from
  Settings.
- The consent screen states in plain language what is collected and why. It links to a
  human-readable summary, not a legal wall.
- Data export and deletion available from Settings → Account, honored within 30 days.

**What is never collected:** anything typed by the player (plate text, display names),
anything about their machine beyond hardware class and driver version, and any data at
all when consent is absent.

---

## 2. Event schema

Batched, compressed, sent every 5 minutes and at session end. Dropped silently on
failure — telemetry never retries aggressively and never blocks anything.

```jsonc
{
  "installId": "guid",            // random, resettable, install-scoped
  "sessionId": "guid",
  "buildVersion": "1.0.4127",
  "platform": "win64", "gpuClass": "mid", "qualityTier": "high",
  "events": [ /* below */ ]
}
```

### 2.1 Session events

| Event | Fields |
|---|---|
| `session_start` | timestamp, coldBoot, bootDurationMs |
| `session_end` | durationS, runCount, reason (quit / crash / idle) |
| `settings_changed` | setting, oldValue, newValue |
| `difficulty_changed` | preset, individualOverrides |

### 2.2 Run events — the core dataset

| Event | Fields |
|---|---|
| `run_start` | mode, environment, weather, timeOfDay, vehicleId, upgradeLevel, difficultyPreset, driverLevel |
| `run_end` | durationS, distanceKm, score, coins, nearMisses, closeNearMisses, bestCombo, topSpeedKmh, endReason |
| `run_death` | **distanceKm, speedKmh, lane, laneCount, trafficDensity, weather, timeOfDay, causeType, secondsSinceLastNearMiss, hadContactWarning** |
| `run_restart` | timeToRestartMs, fromResultsScreen |
| `near_miss` | *sampled at 2%* — clearanceM, speedKmh, comboCount, vehicleType, oncoming |

**`run_death` is the single most valuable event in the game.** Every field on it exists
to answer one question: *was that death fair?* A cluster of deaths at a specific
distance, lane count, or weather state is a solvability or sightline defect, not player
skill. Watch it weekly.

### 2.3 Progression events

| Event | Fields |
|---|---|
| `level_up` | newLevel, totalPlaytimeS, totalRuns |
| `vehicle_unlocked` | vehicleId, priceCoins, playtimeAtUnlockS, runsAtUnlock |
| `upgrade_purchased` | vehicleId, category, tier, price |
| `engine_swap` | vehicleId, swapId |
| `environment_unlocked` | environmentId, playtimeAtUnlockS |
| `mode_first_played` | modeId, playtimeS |
| `mission_completed` | missionId, category, attempts |
| `achievement_unlocked` | achievementId, playtimeS |
| `currency_balance` | *daily snapshot* — coins, cash, tokens |

### 2.4 Technical events

| Event | Fields |
|---|---|
| `perf_sample` | *every 60 s* — p50/p95/p99 frameTimeMs, fps, drawCalls, memoryMb, vramMb |
| `hitch` | frameTimeMs, suspectedSystem, distanceKm, speedKmh |
| `crash` | callstackHash, module, buildVersion |
| `load_time` | phase, durationMs |
| `pool_exhausted` | poolName, peakUsage |

`hitch` and `pool_exhausted` should be **empty in production**. Any occurrence is a bug
ticket, not a metric.

---

## 3. KPIs

### 3.1 The five that matter

| KPI | Target | What a miss means |
|---|---|---|
| **D1 / D7 / D30 retention** | 45% / 22% / 10% | The core loop is not compelling |
| **Runs per session** | ≥ 6 median | Restart friction, or runs are unsatisfying |
| **Median session length** | 22 min | — |
| **Time to first unlock** | ≤ 8 min | Onboarding cadence broken (`01` §4.1) |
| **Death-blame rate** (from playtests + `run_death` clustering) | < 10% game-blamed | Fairness defect — the highest-priority class of bug |

### 3.2 Health metrics

| Metric | Target |
|---|---|
| Restart-from-results rate | > 55% (players restarting before reading = good) |
| Garage visits per session | ≥ 1.5 |
| Mode diversity (share not playing Classic) | > 35% by hour 10 |
| Vehicle usage Gini | < 0.6 — no single dominant car |
| Median runs per unlock, first hour | 2.5–3.5 |
| Tutorial-repeat rate (run 1 deaths < 20 s) | < 25% |
| Photo Mode usage | > 5% of sessions |
| Accessibility feature adoption | Tracked, no target — presence is the point |
| p99 frame time within budget | > 95% of `perf_sample`s |
| Crash-free sessions | > 99.5% |

### 3.3 Funnels

Instrumented end to end, with drop-off measured at each step:

```
install → first launch → first run started → first run completed → first near miss
       → first unlock → second session → first garage visit → first upgrade
       → first mode switch → day 7 → first prestige
```

The two steps that predict everything: **first near miss** and **second session**. If
players are dropping before their first near miss, the tutorial ruleset in `01` §5 is
wrong. If they complete a first session and never return, the reward cadence is wrong.

---

## 4. Closing the loop on balance

Telemetry exists to correct the model in `docs/09` §11, not to sit in a dashboard.

### 4.1 The correction cycle

```
1. The economy harness predicts, from a skill-distribution assumption:
       time-to-unlock, coins/hour, level curve, unlock cadence.
2. Live data measures the same quantities.
3. Where prediction and reality diverge by > 20%, the ASSUMPTION is wrong — not
   the player.
4. Re-fit the skill distribution in the harness to observed data.
5. Re-run every balance assertion in docs/01 §8 against the corrected model.
6. Adjust prices, XP, or ramps in DATA ONLY. Ship as a config update.
7. Record the change and its measured effect in docs/CHANGELOG.md.
```

### 4.2 What may be tuned live, and what may not

| Freely tunable (data, no patch) | Never tuned live |
|---|---|
| Prices, XP values, mission targets and rewards | Physics constants |
| Difficulty ramp coefficients | Near-miss thresholds |
| Traffic density and speed curves | The Near-Miss Contract |
| Mission and daily template weights | The solvability guarantee |
| Event ladders and rewards | Scoring formulas |
| Login and streak rewards | Anything that invalidates existing leaderboard entries |

**The right-hand column is the line.** Changing a scoring formula or a physics constant
retroactively invalidates every leaderboard entry and every replay. If one genuinely
must change, it is a new leaderboard season with the old boards archived, announced in
advance — never a silent live tweak.

### 4.3 A/B testing

Permitted for: onboarding flow, tutorial ruleset, unlock cadence, UI layout, store
presentation.

**Not permitted for:** difficulty, scoring, or anything affecting a leaderboard —
players in different buckets must remain comparable. Never A/B test whether a
player pays more.

---

## 5. Dashboards

Three, and no more — a dashboard nobody reads is worse than none.

| Dashboard | Audience | Refresh | Contents |
|---|---|---|---|
| **Health** | Everyone, on a wall | Hourly | Crash-free rate, p99 frame time, hitch count, retention, DAU |
| **Fairness** | Design | Daily | `run_death` clustering by distance / lane count / weather / speed, death-blame proxy, solvability near-misses |
| **Balance** | Design + production | Weekly | Unlock cadence vs. model, currency flow, vehicle usage Gini, mode diversity, funnel drop-off |

The **Fairness dashboard is the one that is easy to skip and must not be.** It is the
only systematic way to find the deaths that make players quit without ever filing a bug.

---

## 6. Crash and error reporting

- Separate consent from analytics — many players decline analytics but accept crash
  reports. Ask separately and honestly.
- Symbolicated call stacks, build version, hardware class, and the last 60 seconds of
  game-state breadcrumbs (mode, distance, speed, active systems). **No user content.**
- Deduplicate by call stack hash. Any crash affecting > 0.1% of sessions is P0.
- A crash during a run must still save the run's progress and mission credit on next
  launch. Losing a 12-minute run to a crash is the worst experience the game can deliver.
