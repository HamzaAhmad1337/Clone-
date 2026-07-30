# 11 — Performance and Optimization

Performance is an acceptance criterion, not a phase. Every merge holds these budgets.

---

## 1. Targets

| Tier | Reference hardware | Target fps | Resolution | Upscaler |
|---|---|---|---|---|
| Low | GTX 1050 Ti / RX 560, Ryzen 3 1200, 8 GB | 60 | 1080p | FSR Performance (720p internal) |
| Medium | GTX 1660 / RX 5600 XT, Ryzen 5 3600, 16 GB | 60 | 1080p | Native or FSR Quality |
| High | RTX 3060 / RX 6600 XT, Ryzen 5 5600, 16 GB | 90 | 1440p | DLSS/FSR Quality |
| Ultra | RTX 4070+ / RX 7800+, Ryzen 7 7700, 32 GB | 120 | 1440p–4K | DLSS Quality |
| Steam Deck | — | 45 locked | 1280×800 | FSR |

**Frame time, not average fps, is the metric.** The ship gate is:
`99th-percentile frame time ≤ 1.25 × target frame time` over a 30-minute capture.
An average of 60 fps with regular 40 ms spikes is a failing build.

---

## 2. Frame budget (120 fps target = 8.33 ms)

| Thread / system | Budget | Notes |
|---|---|---|
| **Game thread total** | 3.2 ms | |
| — Player vehicle + input | 0.35 ms | |
| — Traffic (near tier application) | 0.55 ms | |
| — Gameplay systems (scoring, missions, events) | 0.30 ms | |
| — Chunk attachment (amortized) | 0.20 ms | Peak 0.8 ms, amortized over frames |
| — UI / HUD | 0.50 ms | |
| — Camera | 0.15 ms | |
| — Effects management | 0.35 ms | |
| — Engine overhead / tick | 0.80 ms | |
| **Render thread** | 3.2 ms | Draw call submission, culling |
| **GPU** | 8.0 ms | The actual constraint on most hardware |
| **Physics workers** | 1.6 ms | 120 Hz substeps, parallel |
| **AI worker** | 0.9 ms | Time-sliced across tiers |
| **Audio thread** | 0.4 ms | |
| **Streaming worker** | — | Off critical path entirely |

At 60 fps (16.67 ms) all CPU budgets double; the GPU budget becomes 15 ms.

### 2.1 Draw call and triangle budgets

| Tier | Draw calls | Triangles | Dynamic lights | Shadow casters |
|---|---|---|---|---|
| Low | 1,200 | 3.5 M | 8 | 4 |
| Medium | 2,000 | 7 M | 16 | 8 |
| High | 3,200 | 14 M | 32 | 16 |
| Ultra | 4,500 | 25 M | 64 | 32 |

---

## 3. Required techniques

### 3.1 Instancing
Every repeated roadside object (poles, signs, barriers, cones, vegetation, guard rail
segments) goes into a hierarchical instanced mesh per chunk. A chunk with 400 scattered
objects must cost 3–6 draw calls, not 400.

### 3.2 LOD
Screen-size-driven with **dithered crossfade** transitions — never a pop. Every asset
class has a mandatory LOD chain:

| Asset | LOD0 | LOD1 | LOD2 | LOD3 | Imposter |
|---|---|---|---|---|---|
| Player vehicle | 180k | 65k | 18k | 4k | — |
| Traffic vehicle | 45k | 18k | 6k | 1.5k | Yes, 350 m+ |
| Building | Nanite | — | — | — | Yes, 600 m+ |
| Vegetation | 4k | 1.2k | 300 | Billboard | — |
| Road furniture | 2k | 600 | 150 | — | — |

### 3.3 Culling
Frustum culling, hardware occlusion queries or software occlusion, distance culling per
object class, and **small-object culling** (anything under 2 px screen size is dropped).
Traffic beyond the tier's draw distance is simulated but not rendered.

### 3.4 Texture streaming
Hard pool budget per tier (Low 1.5 GB, Medium 2.5 GB, High 3.5 GB, Ultra 5 GB).
Mip bias driven by pool pressure. Vehicles and road surfaces get streaming priority;
distant scatter gets the lowest.

### 3.5 Object pooling
Everything in `docs/02-technical-architecture.md` §5. **Zero runtime allocation in the
gameplay hot path** is a hard rule, verified by an allocation-tracking build that fails
CI if the gameplay tick allocates.

### 3.6 Async everything
Chunk generation, asset loading, save I/O, analytics batching, and shader compilation
all run off the game thread. Nothing on the critical path blocks.

---

## 4. The hitch problem

**A single 40 ms spike at 280 km/h moves the car 3.1 m without player input. It kills
runs. It is a ship-blocking bug, always.**

Known hitch sources and their required mitigations:

| Source | Mitigation |
|---|---|
| Shader / PSO compilation | Full PSO cache precompiled at first boot behind a progress bar. Never compile during gameplay. Ship a pre-warmed cache; regenerate on driver change |
| Chunk generation | Worker thread, 750 m of lead time, amortized attachment over frames |
| Asset loading | Async only, with everything needed for the run preloaded before the countdown |
| Garbage collection | Pooling + zero hot-path allocation. Force a full collect only at run end |
| Level streaming | Custom chunk system, never engine level streaming during a run |
| Particle system spin-up | Pre-warmed pools, first-play cost paid at load |
| Audio bank loading | All banks for the active vehicle and environment loaded before the run |
| Physics body creation | Pooled bodies, created at warmup, reused |
| Decal accumulation | Hard FIFO budget with atlas reuse |
| Save I/O | Async, never mid-run |
| Floating-origin rebase | Amortized across 2 frames; measured cost must stay under 1 ms |

### 4.1 Hitch detection in CI
An automated 30-minute scripted run per tier that logs every frame time. The build fails
on any frame exceeding `2 × target frame time`. The log identifies the responsible
system by scope timers.

---

## 5. Memory budgets

| Tier | System RAM | VRAM |
|---|---|---|
| Low | 3.5 GB | 2.0 GB |
| Medium | 4.5 GB | 3.0 GB |
| High | 6.0 GB | 4.0 GB |
| Ultra | 8.0 GB | 7.0 GB |

Allocation breakdown target at High: meshes 900 MB, textures 2.4 GB, audio 400 MB,
physics 120 MB, gameplay/pools 180 MB, engine/other 2 GB.

Memory must be **flat over time.** A 60-minute run that grows memory is a leak, and the
CI soak test asserts less than 2% growth between minute 10 and minute 60.

---

## 6. Upscaling and dynamic resolution

- **DLSS 3.x** (NVIDIA RTX), **FSR 3.x** (all), **XeSS** (Intel Arc + fallback),
  **TSR** (engine default fallback). All four available, auto-selected by detected GPU,
  overridable.
- Frame generation offered where supported, **off by default** — it adds latency, and
  latency is a pillar violation. Warn in the tooltip.
- **Dynamic resolution scaling** targeting the tier's frame time, with a floor of 60%
  and a ceiling of 100%, adjusting by no more than 5% per second so it is not visible.
- Upscaling is applied before UI so the HUD stays crisp.

---

## 7. Auto-detect

On first boot, run a 20-second silent benchmark (a fixed scripted scene) and select a
tier from the measured frame times plus detected VRAM. Present the result to the player
with a "change this" prompt rather than applying it silently. Re-offer after a GPU or
driver change.

---

## 8. Profiling discipline

- Named scope timers around every system, always compiled in (they cost <0.02 ms total).
- An in-game overlay (F3) showing frame time breakdown, draw calls, triangles, memory,
  pool usage, active traffic count, and streaming state.
- A CSV frame-time export for offline analysis.
- Weekly automated performance regression run on all tiers; a >5% regression opens a
  ticket automatically.

---

## 9. Optimization acceptance tests

| Test | Assertion |
|---|---|
| Frame time, all tiers | 99th percentile ≤ 1.25 × target over 30 min |
| Zero hitches | No frame > 2 × target over 30 min, per tier |
| Memory flat | < 2% growth from minute 10 to minute 60 |
| No hot-path allocation | Allocation-tracking build reports zero gameplay-tick allocations |
| Pool stability | Zero pool growth over 60 minutes |
| Load time | Warm-cache run start ≤ 3 s |
| Boot time | Cold boot to main menu ≤ 15 s (excluding first-run PSO compile) |
| Draw calls | Within the §2.1 budget at every tier, worst-case scene |
| VRAM | Within the §5 budget, no eviction thrash |
| Steam Deck | 45 fps locked, 30-minute capture, thermals stable |
