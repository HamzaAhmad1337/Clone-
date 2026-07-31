# 15 — Networking and Multiplayer

Multiplayer ships post-launch. **The interfaces ship in M0.** "Isolated behind an
interface" is not a plan unless the interface exists — otherwise 1.3 is a rewrite, not
a feature.

This document defines what must exist from day one, and what it grows into.

---

## 1. The M0 requirement

Four interfaces, each with a working **null implementation** that the single-player
build uses. Every online feature calls through them from the start, so no gameplay code
ever learns whether a backend is present.

```cpp
// Systems/Online/OnlineInterfaces.h

/** Identity. Null impl returns a stable local GUID. */
class IIdentityService {
public:
    virtual FPlayerId GetLocalPlayerId() const = 0;
    virtual FString   GetDisplayName() const = 0;
    virtual bool      IsAuthenticated() const = 0;
    virtual void      Authenticate(TFunction<void(bool)> OnComplete) = 0;
    virtual void      GetFriends(TFunction<void(TArray<FPlayerId>)> OnComplete) = 0;
};

/** Persistent storage. Null impl writes to the local save only. */
class ICloudSaveService {
public:
    virtual void Upload(const FSaveBlob& Blob, TFunction<void(EResult)> OnComplete) = 0;
    virtual void Download(TFunction<void(EResult, FSaveBlob)> OnComplete) = 0;
    virtual void ResolveConflict(const FSaveBlob& Local, const FSaveBlob& Remote,
                                 TFunction<void(FSaveBlob)> OnResolved) = 0;
};

/** Leaderboards and ghosts. Null impl keeps a local top-100 per board. */
class ILeaderboardService {
public:
    virtual void Submit(const FRunSubmission& Run, TFunction<void(EResult)> OnComplete) = 0;
    virtual void Query(const FBoardQuery& Query,
                       TFunction<void(TArray<FBoardEntry>)> OnComplete) = 0;
    virtual void DownloadGhost(const FEntryId& Id,
                               TFunction<void(EResult, FReplayData)> OnComplete) = 0;
};

/** Live sessions. Null impl fails every call with EResult::Unsupported. */
class ISessionService {
public:
    virtual void CreateSession(const FSessionConfig& Config,
                               TFunction<void(EResult, FSessionId)> OnComplete) = 0;
    virtual void JoinSession(const FSessionId& Id, TFunction<void(EResult)> OnComplete) = 0;
    virtual void LeaveSession() = 0;
    virtual void SendState(const FPlayerStateSnapshot& Snapshot) = 0;
    virtual TArray<FRemotePlayerState> GetRemoteStates() const = 0;
};
```

**Rules from M0:**
- All four are resolved through the module registry, never constructed directly.
- Every call is asynchronous with a completion callback. No online call blocks the game
  thread, ever, including in the null implementation — it completes on the next tick, so
  the async code path is exercised in single player and cannot rot.
- Any failure degrades gracefully. Losing a leaderboard never blocks a run, a payout, or
  an unlock.
- `T-NET-01` asserts the whole game compiles and plays with the null implementations.

---

## 2. Cloud save (M14)

- Save blob is the JSON from `docs/02` §7, gzipped. Typical size 40–120 KB.
- Upload on: run end, purchase, unlock, and every 5 minutes of session time, debounced.
- Download on: launch, and on profile switch.
- **Conflict resolution:** never silently discard progress. Compare on
  `(driverXp, totalCoinsEarned, achievementCount)`. If remote strictly dominates local,
  take remote. If local dominates, take local. If neither dominates — the genuine
  conflict case, which means two machines played offline — **ask the player**, showing
  both profiles' level, playtime, vehicle count, and last-played time.
- Keep the last 3 cloud versions server-side for support recovery.

---

## 3. Replays and ghosts (M14)

A replay is **not video**. It is the seed plus the input trace.

```jsonc
{
  "version": 3,
  "seed": 1740283910,
  "mode": "two_way", "modifiers": [], "environment": "desert",
  "timeOfDay": "golden_hour", "weather": "clear",
  "vehicle": { "id": "aurel_gt340", "upgrades": {...}, "engineSwap": null },
  "buildVersion": "1.0.4127",
  "inputTrace": [ /* delta-encoded, 60 Hz: steer, throttle, brake, handbrake, nitrous, gear */ ],
  "keyframes": [ /* full state every 2.0 s, for drift correction and seeking */ ],
  "result": { "distanceKm": 18.42, "score": 264684, "nearMisses": 147, "topSpeedKmh": 312 }
}
```

- **~4 KB per minute** compressed. A 12-minute expert run is under 50 KB, which is why
  ghost downloads are free and leaderboards can store every entry's trace.
- Keyframes exist because floating-point replay drifts. On playback, if the simulated
  position diverges from a keyframe by more than 10 cm, snap and log — a divergence in
  the *same build* is a determinism bug and `T-NET-02` fails.
- **Replays are build-versioned.** A physics change invalidates old replays. Keep the
  result data and mark the trace unplayable rather than deleting the record; a player's
  best run should never vanish from their profile because of a patch.
- Ghosts render as a translucent vehicle with no collision, playing back a downloaded
  trace. Multiple ghosts simultaneously, capped at 4.

---

## 4. Leaderboards and anti-cheat (M14)

Every submission carries `{ seed, mode, modifiers, vehicleConfig, buildVersion,
inputTrace, result, checksum }`.

**Server-side validation** re-simulates the input trace headlessly and compares the
result. This is the entire reason determinism is an architectural requirement, and it
makes the local save format's readability harmless: editing your save cannot forge a
score, because the score must be *reproducible from inputs*.

| Check | Action on failure |
|---|---|
| Re-simulation result mismatch > 0.1% | Reject, flag account |
| Build version unsupported | Reject, ask to update |
| Input trace physically impossible (rate limits) | Reject, flag |
| Submission rate anomalous | Rate-limit, flag |
| Result exceeds theoretical maximum for the seed | Reject, flag |

Validation is sampled, not exhaustive, for cost: 100% of top-100 entries, 100% of Daily
Challenge entries, and a 2% random sample of everything else. Flagged accounts move to
100% validation.

**Daily Challenge** is the strongest anti-cheat surface: one fixed global seed means
every submission is directly comparable and re-simulation is cheap.

---

## 5. Live multiplayer (1.3+)

Scoped deliberately small. Highway Rush is a single-player game with social edges, not
a racing sim.

### 5.1 Ghost races (1.1)
Asynchronous. Race a friend's or a leaderboard ghost. No netcode beyond downloading a
trace — this is why it comes first and is nearly free.

### 5.2 Convoys (1.3)
2–4 players in a shared session on the same seed.

| Aspect | Decision |
|---|---|
| Topology | Client-authoritative for own vehicle, host-authoritative for traffic |
| Traffic | Deterministic from the shared seed — **not replicated**. This is the key trick: identical seeds mean identical traffic, so only 4 player transforms cross the wire |
| Tick rate | 20 Hz state, interpolated to 60+ locally |
| Bandwidth | < 8 KB/s per player |
| Collision between players | **Off by default.** Players are ghosts to each other unless "contact" is enabled in the lobby |
| Desync handling | If a client's traffic state diverges from the host's, resync from the host's seed offset and log |
| Scoring | Independent per player; a shared session leaderboard at run end |
| Cheating | Convoy scores do not submit to global leaderboards |

**Why client-authoritative:** this is a cooperative, non-competitive mode with no shared
scoring. Rollback netcode would cost months and buy nothing. If competitive live racing
is ever added, it needs a different architecture — say so rather than retrofitting.

### 5.3 Cross-play (2.0)
Epic Online Services provides identity and sessions across PC and console. The
interfaces in §1 do not change; only the implementation behind them does. That is the
entire point of defining them in M0.

---

## 6. Backend requirements

| Service | Purpose | Scale target |
|---|---|---|
| Identity | Auth, friends | Platform-provided (Steam/EOS) |
| Cloud save | Profile blobs | 120 KB × MAU, 3 versions |
| Leaderboard | Submissions, queries, ghost storage | 50 KB × submissions |
| Validation workers | Headless re-simulation | Sampled per §4 |
| Daily seed service | One authoritative seed per UTC day | Trivial |
| Event config | Weekly/monthly ladders, without a client patch | Trivial |
| Telemetry ingest | `docs/16` | Batched, opt-in only |

**Everything must degrade.** If every backend is down, the game must still boot, play,
save locally, and unlock content. Online is additive. `T-NET-01` proves it by running
the whole game on the null implementations.

---

## 7. Privacy and data

- Display names are the only player-visible data on leaderboards. No location, no
  platform ID exposed.
- Telemetry is opt-in and separate from leaderboard submission (`docs/16` §1).
- Data export and deletion are available in Settings → Account and must complete within
  30 days of request.
- Replay input traces contain no personal data — they are steering and pedal values.
- Children's-privacy posture: the game targets E10+/PEGI 7, so no free-text chat, no
  user-to-user messaging, and profanity filtering on plate text and display names.
