# 17 — Build, Packaging, and Release

---

## 1. Build configurations

| Config | Purpose | Optimizations | Asserts | Telemetry | Ships |
|---|---|---|---|---|---|
| **Debug** | Diagnosis | Off | All | Local file | No |
| **Development** | Daily work, playtests | On | `check` + `ensure` | Local file | No |
| **Profile** | Performance capture | On | `check` only | Local file | No |
| **Test** | QA, cert pre-check | On | `check` only | Staging | No |
| **Shipping** | Retail | Full + LTO | Off | Production | **Yes** |

Every configuration must run the full game. A build that only works in Development is
not a build.

The **Profile** configuration keeps named scope timers and the F3 overlay compiled in
(they cost < 0.02 ms total) so performance work never requires a different binary from
the one being measured.

---

## 2. Versioning

```
MAJOR.MINOR.PATCH.BUILD        e.g. 1.2.3.4127
```

| Component | Increments when |
|---|---|
| MAJOR | Save format breaks, or a platform generation changes |
| MINOR | Content release — new vehicles, environments, modes, season |
| PATCH | Fixes and data-only balance changes |
| BUILD | Every CI build, monotonic, never reused |

**Save schema version is independent** of the product version and only ever increases.
Every increment ships with a migration (`docs/02` §7) and a test (`T-SAV-03`).

**Replay compatibility** is keyed to a separate `simulationVersion`, bumped only when
physics, scoring, or traffic behavior changes. Replays from a different
`simulationVersion` keep their result record but are marked unplayable (`docs/15` §3).

---

## 3. Platforms

| Platform | v1 | Notes |
|---|---|---|
| Windows 10/11 x64 | **Ship** | Primary |
| Steam Deck | **Ship** | Verified target: 45 fps locked, 800p, FSR |
| Linux (Proton) | **Ship** | Via Proton; native later if demand justifies |
| Linux native | 1.4 | |
| macOS | Evaluate at 2.0 | Metal + Apple Silicon |
| Consoles | 2.0 | Requires cert partner |

### 3.1 Minimum and recommended specs

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| CPU | Ryzen 3 1200 / i3-8100 | Ryzen 5 5600 / i5-12400 |
| GPU | GTX 1050 Ti / RX 560 (4 GB) | RTX 3060 / RX 6600 XT (8 GB) |
| RAM | 8 GB | 16 GB |
| Storage | 35 GB SSD | 35 GB NVMe |
| Target | 60 fps, 1080p (720p internal, FSR) | 90 fps, 1440p |

**SSD is a minimum requirement, not a recommendation.** Chunk streaming at 385 km/h
cannot be served from spinning rust without hitches, and a hitch is a P1
(`docs/14` §5).

---

## 4. Packaging

| Item | Target |
|---|---|
| Install size | ≤ 35 GB |
| Textures | BC7 / BC5, streamed, per-tier mip caps |
| Audio | Vorbis, 48 kHz; engine layers at higher quality than ambience |
| Meshes | Nanite where applicable; explicit LOD chains elsewhere |
| Shaders | Full PSO cache precompiled, shipped, and regenerated on driver change |
| Localization | All 14 languages shipped; no download-on-demand |
| Pak layout | Split by environment so future content is a delta patch, not a full redownload |

### 4.1 First-boot experience
```
launch → EULA/consent (once) → PSO precompile with progress bar → hardware benchmark
       → suggested quality tier, shown for confirmation → main menu → RUN
```
PSO precompilation is the one acceptable wait in the entire product, because it is what
buys a hitch-free game. Show honest progress, state why it is happening, and never do
it again unless the driver changes.

---

## 5. Store presence

| Asset | Requirement |
|---|---|
| Capsule art | No real vehicle likenesses. Original marques only |
| Trailer | 60–90 s, gameplay only, no pre-rendered footage, no fake UI |
| Screenshots | 8–12, all in-engine, Golden Hour hero shots from Photo Mode |
| Description | Honest about scope: single-player, cosmetic-only monetization, no ads |
| Demo | 20-minute trial: 3 vehicles, 2 environments, Classic + Two-Way. Progress carries into the full game |
| Content rating | ESRB E10+ / PEGI 7 — vehicle collisions only, no pedestrians, no blood |
| Accessibility tags | Every applicable tag, accurately. Do not overclaim |

**The demo carries progress forward.** A player who spent 20 minutes earning coins and
loses them on purchase feels punished for trying. This measurably increases conversion
and it is the right thing to do regardless.

---

## 6. Release checklist

Nothing ships until every line is checked and signed.

### Code and content
- [ ] Zero P0 and P1 bugs (`docs/14` §5)
- [ ] All CI gates green on the release candidate
- [ ] `tools/validate_content.py` exits 0
- [ ] Every localization key resolves in all 14 languages
- [ ] No debug or placeholder content reachable in Shipping
- [ ] No hardcoded strings in any UI-facing path

### Performance
- [ ] 30-minute capture per tier, 99th percentile within budget (`T-PRF-01`)
- [ ] **Zero frames over 2× target** across all captures (`T-PRF-02`)
- [ ] 60-minute soak, memory growth < 2% (`T-PRF-05`)
- [ ] Steam Deck verified at 45 fps locked, thermals stable
- [ ] Install size ≤ 35 GB, load times within budget

### Correctness
- [ ] Determinism verified across two machines (`T-ROA-01`, `T-NET-02`)
- [ ] Save migration verified from every prior schema version
- [ ] Every mode completable; every achievement attainable
- [ ] Economy assertions pass against the current data (`docs/01` §8)
- [ ] Offline play fully functional on null online implementations (`T-NET-01`)

### Experience
- [ ] The §22 Final Test passes — five yeses, fresh testers
- [ ] Full playthrough with each accessibility mode (`T-ACC-01…12`)
- [ ] Gamepad-only and keyboard-only playthroughs complete
- [ ] Pseudo-localization at +40% with zero clipping
- [ ] Arabic RTL layout verified

### Legal and compliance
- [ ] Originality audit: no real marque, logo, likeness, place name, or signage standard
- [ ] All music and audio licensed for commercial use **including streaming**
- [ ] All third-party licenses attributed in-game
- [ ] Privacy policy accurate to what is actually collected (`docs/16` §1)
- [ ] Consent flows correct per region; EU telemetry defaults off
- [ ] Content rating obtained for every shipping territory
- [ ] Data export and deletion paths functional

---

## 7. Patching

| Change | Vehicle |
|---|---|
| Balance (prices, XP, ramps, mission targets) | Data-only config update, no client patch |
| Event ladders and rewards | Server config |
| Bug fixes | PATCH release |
| New content | MINOR release |
| Physics, scoring, or traffic behavior | **New leaderboard season**, announced in advance, old boards archived — never silent (`docs/16` §4.2) |

**Hotfix criteria:** P0 only, or a P1 affecting more than 5% of sessions. Everything else
waits for the next scheduled patch. A rushed hotfix that introduces a hitch is worse than
the bug it fixed.

### 7.1 Rollback
Every release keeps the previous Shipping build available for one-click rollback for 30
days. Save compatibility must be verified in **both directions** before any release that
increments the save schema — a player who rolls back must not lose their profile.

---

## 8. Post-launch cadence

| Window | Focus |
|---|---|
| Days 0–3 | Crash triage, hotfixes, watch the Fairness dashboard hourly |
| Week 1 | First balance read against the live model (`docs/16` §4) |
| Week 2–4 | Community-reported fairness defects, first data-only balance pass |
| Month 2 | 1.1 — ghost races, 4 vehicles, 1 environment |
| Month 3 | 1.2 — Season 1, Season Pass enabled |
| Month 5 | 1.3 — convoys |
| Month 8 | 1.4 — livery sharing, replay editor |
| Month 12 | 2.0 — consoles, major content |

**Weeks 1–4 are for fairness, not features.** The deaths players blame on the game are
the ones that decide whether the game has a second month.
