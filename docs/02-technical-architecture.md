# 02 — Technical Architecture

---

## 1. Principles

1. **One direction of dependency.** The module graph is a DAG. If you need an upward
   reference, emit an event instead.
2. **Data over code.** Content is data. Behavior is code. If adding content requires
   code, the architecture is wrong.
3. **Nothing allocates in the hot path.** Pool it or preallocate it.
4. **Determinism is a feature.** Seeded PRNG everywhere in gameplay.
5. **Headless-testable.** Every system must run without a renderer.

---

## 2. Module graph

```
                          ┌──────────────┐
                          │ GameManager  │  owns run lifecycle, seed, mode ruleset
                          └──────┬───────┘
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
      ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
      │WorldManager │     │VehicleCtrl  │     │  UIManager  │
      └──────┬──────┘     └──────┬──────┘     └─────────────┘
      ┌──────┴──────┐            │
      ▼             ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│RoadGen    │ │TrafficMgr │ │PhysicsMgr │
└───────────┘ └─────┬─────┘ └───────────┘
                    ├── AIManager ── PoliceManager
                    └── (pools)

  Cross-cutting services (leaf nodes, no outbound deps, event-driven only):
  CameraManager · AudioManager · EffectsManager · WeatherManager · TimeOfDayManager
  GraphicsManager · InputManager · SaveManager · EconomyManager · MissionManager
  AchievementManager · ReplayManager · AnalyticsManager
```

**Rule:** a module may hold a direct pointer to modules *below* it in this graph only.
Everything else goes through `EventBus`.

---

## 3. Module contracts

Each entry: responsibility · owns · emits · listens.

### GameManager
Run lifecycle, seed ownership, active mode ruleset, global pause, time scale.
Owns: `FRunContext` (seed, mode, environment, weather, TOD, vehicle, start time).
Emits: `RunStarted`, `RunEnding`, `RunEnded`, `RunRestartRequested`, `GamePaused`.
Listens: `PlayerCrashed`, `FailConditionMet`, `RestartInput`.

### WorldManager
Owns environment selection and the streaming volume. Coordinates RoadGenerator,
WeatherManager, and TimeOfDayManager into a coherent world state. Owns floating origin.
Emits: `ChunkSpawned`, `ChunkDespawned`, `OriginRebased`, `EnvironmentLoaded`.

### RoadGenerator
Produces chunk descriptors from the grammar (`docs/05-road-generation.md`), builds
spline geometry and scatter on a worker thread. Never touches gameplay state.
Emits: `ChunkReady(FChunkData)`.

### TrafficManager
Spawn scheduling, density curves, solvability verification, pooling, LOD tiering,
despawn. Owns the traffic pool and the active traffic list.
Emits: `TrafficSpawned`, `TrafficDespawned`, `HazardCreated`.
Listens: `ChunkSpawned`, `RunStarted`, `WeatherChanged`.

### AIManager
Ticks driver behavior. Time-sliced: near tier every frame, mid tier every 4 frames,
far tier every 16 frames. Runs on worker threads with a double-buffered state snapshot.

### PoliceManager
Wanted level, unit spawning, pursuit coordination, roadblocks, spikes, helicopter,
radio chatter selection, escape evaluation.
Emits: `WantedLevelChanged`, `PursuitStarted`, `PursuitEnded`, `BustedBy`.

### VehicleController
Player vehicle: input application, transmission, nitrous, damage state, assists.
Delegates raw dynamics to PhysicsManager. Emits `NearMiss`, `Collision`, `Overtake`,
`GearChanged`, `NitrousStateChanged`, `AirborneStateChanged`, `DamageTierChanged`.

### PhysicsManager
Suspension, tire model, aero, weight transfer, surface grip lookup. Fixed 120 Hz
substeps. Fully headless-capable and deterministic.

### CameraManager
8 modes, transitions, the speed rig, shake layers, crash cam, replay cam, photo mode.
Listens: `NearMiss`, `Collision`, `NitrousStateChanged`, `SpeedChanged`, `RunEnded`.

### AudioManager
Engine model, wind/road, spatialization, occlusion, adaptive music state, mixing,
ducking. Owns all submixes.

### UIManager
Screen stack, focus model, HUD binding, transitions, localization. Pure view — it
never owns gameplay state, it only binds to it.

### InputManager
Device detection and hot-swap, remapping, deadzones, response curves, the steering
assist model, rumble output.

### SaveManager
Profile serialization, autosave, manual save, 3 profile slots, cloud sync, corruption
detection with a rolling backup (keep last 3 saves), schema migration.

### EconomyManager
Currency balances, payout calculation, purchase validation, upgrade application, price
tables. Every transaction is atomic and logged.

### MissionManager / AchievementManager
Data-driven objective evaluation against a stream of gameplay events. Both consume the
same `FGameplayEvent` stream so a new objective type is a data entry, not code.

### WeatherManager / TimeOfDayManager
State machines with blended transitions. Publish a `FEnvironmentState` struct that
every other system reads (grip, sightline, light level, wind, wetness).

### GraphicsManager
Quality tiers, upscaler selection, dynamic resolution, per-setting application, PSO
warmup, benchmark-based auto-detect on first boot.

### EffectsManager
Pooled particles, decals, debris, damage FX, screen effects. Hard budgets with
distance-based culling and priority eviction.

### ReplayManager
Records input trace + seed + periodic state keyframes (every 2 s for drift correction).
A replay is ~4 KB/minute, not a video. Enables ghosts, leaderboard validation, and the
results-screen best-moment clip.

### AnalyticsManager
Opt-in telemetry: run length, death position, mode, car, settings, FPS histogram,
funnel events. Behind a clear consent screen, off by default in the EU build.

---

## 4. Event bus

Typed, synchronous-by-default, with an optional deferred queue for events emitted
during physics ticks.

```cpp
// Core/EventBus.h
template<typename TEvent>
class TEventChannel {
public:
    FDelegateHandle Subscribe(TFunction<void(const TEvent&)> Fn);
    void Unsubscribe(FDelegateHandle Handle);
    void Broadcast(const TEvent& Event);        // immediate
    void Enqueue(const TEvent& Event);          // deferred to end of frame
};

class FEventBus {
public:
    template<typename TEvent> static TEventChannel<TEvent>& Channel();
    static void FlushDeferred();                // called once per frame by GameManager
};
```

Rules: handlers must not emit the same event type (assert on reentrancy). Handlers must
not block. Any handler over 0.1 ms gets moved to a deferred task.

### 4.1 Canonical gameplay event list

`RunStarted` `RunEnding` `RunEnded` `RunRestartRequested` `GamePaused` `GameResumed`
`ChunkSpawned` `ChunkDespawned` `OriginRebased` `EnvironmentLoaded`
`TrafficSpawned` `TrafficDespawned` `HazardCreated` `PileupFormed`
`NearMiss` `CloseNearMiss` `LaneSplit` `Overtake` `Collision` `Scrape` `Airborne`
`Landed` `ComboIncreased` `ComboBroken` `ComboTierReached` `ScoreAwarded`
`SpeedTierChanged` `TopSpeedRecord` `GearChanged` `Redline` `NitrousStarted`
`NitrousEnded` `NitrousRefilled` `DamageTierChanged` `VehicleDestroyed`
`WantedLevelChanged` `PursuitStarted` `PursuitEnded` `BustedBy` `SpikeStripHit`
`RoadblockThreaded` `WeatherChanged` `WeatherTransitionStarted` `TimeOfDayChanged`
`FuelChanged` `FuelEmpty` `CheckpointPassed` `TimerExpired`
`CurrencyChanged` `ItemPurchased` `VehicleUnlocked` `EnvironmentUnlocked`
`ModeUnlocked` `UpgradeApplied` `LevelUp` `Prestiged`
`MissionProgressed` `MissionCompleted` `AchievementUnlocked` `LeaderboardSubmitted`
`SettingChanged` `ProfileLoaded` `ProfileSaved` `SaveCorrupted`

Every one carries a `float RunTime` and a `float Distance` so the replay, mission, and
analytics systems can consume the stream uniformly.

---

## 5. Object pooling

```cpp
template<typename T>
class TObjectPool {
public:
    void Prewarm(int32 Count);
    T* Acquire();                  // never allocates after prewarm; grows by 25% and logs a warning if exhausted
    void Release(T* Object);
    int32 GetPeakUsage() const;    // logged at run end to right-size the pool
};
```

**Prewarm sizes** (measured peaks + 30% headroom). The traffic figure is derived, not
guessed: the active band is 640 m (140 behind + 500 ahead), and the worst case is Rush
Hour at 6 lanes — `6.4 × 6 lanes × 1.0 base density × 2.4 mode multiplier ≈ 92`
concurrent vehicles, so the pool is 120.

| Pool | Size |
|---|---|
| Traffic vehicles | 120 |
| Police vehicles | 14 |
| Particle systems (all types) | 220 |
| Decals (tire marks, scratches, debris) | 400 |
| Debris rigid bodies | 60 |
| Audio components | 96 |
| World-space UI popups | 40 |
| Road chunk actors | 12 |
| Scatter instance buffers | per-environment, precomputed |

Peak usage is logged at run end. If a pool grows in production, that is a bug ticket.

---

## 6. Threading model

| Thread | Work |
|---|---|
| Game | Gameplay tick, event dispatch, player vehicle, near-tier AI application |
| Render | Rendering, input poll at frame start |
| Physics (2 workers) | Chaos substeps at 120 Hz |
| Worker A | Road chunk generation (spline, mesh, scatter placement) |
| Worker B | Traffic AI mid/far tiers, path solving, spawn solvability |
| Worker C | Async asset streaming, save I/O, analytics batching |
| Audio | Engine sample crossfade, mixing |

AI reads a double-buffered world snapshot published at end of game tick. AI writes go
into a command buffer applied at the start of the next game tick. No locks in the
gameplay path.

---

## 7. Save format

JSON, versioned, with a schema migration chain. Human-readable is intentional — it
makes support and QA vastly cheaper, and there is nothing worth protecting in a
single-player premium game. Leaderboard submissions are validated server-side by
replaying the input trace, so a save edit cannot forge a score.

```jsonc
{
  "schemaVersion": 4,
  "profileId": "uuid",
  "createdUtc": "...", "lastPlayedUtc": "...",
  "playerName": "…",
  "currencies": { "coins": 0, "cash": 0, "tokens": 0 },
  "driver": { "level": 1, "xp": 0, "prestige": 0 },
  "vehicles": [ { "id": "…", "owned": true, "upgrades": {…}, "customization": {…}, "odometerKm": 0.0 } ],
  "equippedVehicleId": "…",
  "unlocks": { "environments": [], "modes": [], "cosmetics": [] },
  "missions": { "daily": [], "weekly": [], "career": {} },
  "achievements": { "id": { "progress": 0, "unlockedUtc": null } },
  "statistics": { /* see docs/09 §7 */ },
  "records": { "bestDistanceKm": {}, "bestScore": {}, "topSpeedKmh": 0, "bestCombo": 0 },
  "settings": { /* full settings block */ },
  "seasonPass": { "season": 0, "tier": 0, "premium": false },
  "checksum": "sha256"
}
```

Autosave on: run end, purchase, unlock, settings change, and every 120 s. Never mid-run.
Keep the previous 3 saves; on checksum failure, roll back and notify the player.

---

## 8. Content pipeline

```
/data/*.json  ──▶  JSON Schema validation  ──▶  cook to Data Assets  ──▶  runtime
      │                     │
      │                     └── build fails on any validation error
      └── hot-reloadable in editor and in dev builds (F5 reloads all content)
```

Validation runs in CI and pre-commit. A malformed vehicle file must fail the build, not
crash the game. Every content file is also linted for: unresolved asset references,
missing localization keys, out-of-range values, and duplicate IDs.

---

## 9. Engine portability mapping

Everything in these documents is engine-independent except this table.

| Concept | Unreal 5.6 (canonical) | Unity 6 | Godot 4.4 |
|---|---|---|---|
| Language | C++ | C# | GDScript/C# |
| Vehicle physics | Chaos Vehicles + arcade layer | Custom WheelCollider layer | VehicleBody3D + custom |
| Content data | Data Assets + JSON | ScriptableObjects + JSON | Resources + JSON |
| GI / reflections | Lumen | APV + SSGI (HDRP) | SDFGI |
| Geometry | Nanite | LOD groups | LOD + visibility ranges |
| UI | UMG + CommonUI | UI Toolkit | Control nodes |
| Audio | MetaSounds | FMOD or Wwise | AudioStreamPlayer + custom |
| AI | Behavior Trees + custom FSM | Custom FSM | Custom FSM |
| Instancing | HISM / ISM | Graphics.DrawMeshInstanced | MultiMeshInstance3D |
| Streaming | World Partition + custom chunks | Addressables | Custom chunk loader |
| Upscaling | DLSS/FSR/XeSS plugins | Plugins | FSR built-in |
| Input | Enhanced Input | Input System | InputMap |

If the stack changes, only this table and the `Source/` tree change. Every number,
curve, formula, and rule in `docs/` carries over unchanged.

---

## 10. Coding standards

- C++20. `UPROPERTY`/`UFUNCTION` only where reflection is genuinely needed.
- No raw `new`/`delete` in gameplay. Pools or engine allocation only.
- No singletons except the module registry; modules are subsystems with explicit
  lifetimes.
- No magic numbers. Every tuning value is a named field on a data asset with a unit
  suffix (`MaxSpeedKmh`, `SpringStiffnessNPerM`) and a documented valid range.
- `const` by default, `TArrayView`/spans over copies, reserve before loops.
- Every public type header comment names: purpose, owning module, pillar served, events
  emitted, events consumed.
- Assertions: `check()` for programmer errors, `ensure()` for recoverable content
  errors, never silent failure on bad data.
- Naming: `A` actors, `U` objects, `F` structs, `E` enums, `I` interfaces, `T`
  templates. Booleans read as questions (`bIsAirborne`, `bCanChangeLane`).
