# 05 — Procedural Road Generation

Infinite, seeded, chunk-streamed highway. Deterministic from a single seed so Daily
Challenges, ghosts, and leaderboard validation all work.

---

## 0. Forward-only motion — the constraint that makes streaming clean

**The player vehicle never travels backward.** There is no reverse gear, no reverse
creep, and no way to revisit road that has been passed. This is a design decision, and
it buys more than it costs.

| Consequence | Benefit |
|---|---|
| Chunk index is **monotonically increasing** | Streaming is a ring buffer, not a bidirectional window. No re-entry logic, no cache of visited chunks |
| Passed chunks are **never revisited** | They can be freed immediately and permanently. Memory is bounded and constant, not a function of run length |
| Generation is strictly **one-directional** | The worker thread only ever produces ahead. No predicting which way the player will go |
| No backward collision cases | Rear-end geometry only needs to handle traffic hitting the player, never the reverse |
| Traffic despawn behind is **final** | No need to keep despawned vehicles addressable |

Implementation:

```
- Every vehicle's longitudinal velocity along the road spline is clamped to >= 0.
- Brake input decelerates to 0 and holds. It never produces negative velocity.
- `reverseRatio` is omitted from vehicle data (docs/10 §1). Gearboxes have no reverse.
- Chunks with index < (playerChunkIndex - 2) are destroyed, not pooled for reuse
  as themselves — their actors return to the generic pool.
```

### 0.1 Spin recovery

Forward-only motion does not mean forward-only *facing*. A player can still be spun by a
collision. In modes where a spin does not immediately end the run (Free Ride, and the
glancing-blow cases in `docs/01` §7):

```
if (|heading - roadDirection| > 120°  AND  speed < 25 km/h  for > 1.5 s)
    → fade out over 0.4 s
    → reposition facing forward in the nearest open lane, at the same chunk position
    → fade in over 0.4 s, at 40 km/h
    → 2.0 s of traffic spawn suppression in that lane so the player is not
      immediately re-hit
```

This is the only teleport in the game and it exists because the alternative — a player
stuck facing backward on a one-way road with no reverse — is unrecoverable.

### 0.2 What this removes from the spec

- The `Backwards` hidden achievement (drive 500 m in reverse) is **impossible** and has
  been replaced (`docs/13` §5.1).
- `PROMPT.md` §4.1's brake binding is "Brake", not "Brake / reverse".
- `reverseRatio` is dropped from the vehicle schema.

---

## 1. Chunk model

```
Chunk length:        250 m
Chunks ahead:        6   (1,500 m of prepared road)
Chunks behind:       2   (500 m, for the rear camera and replays only —
                          never re-enterable, see §0)
Generation budget:   ≤ 4 ms on a worker thread per chunk
Attachment budget:   ≤ 0.8 ms on the game thread per chunk
```

Generation happens on a worker thread the moment the player crosses into a new chunk;
attachment happens on the game thread over the following frames, amortized. A chunk
must be fully prepared **at least 3 chunks (750 m) before the player reaches it** — at
385 km/h that is 7 seconds of lead time, which is the real budget.

### 1.1 Chunk descriptor

```cpp
struct FChunkDescriptor {
    int64    Index;              // monotonic, drives the seed
    EChunkArchetype Archetype;
    float    Curvature;          // 1/radius, signed. 0 = straight
    float    Grade;              // radians, vertical
    float    Bank;               // radians, roll
    uint8    LaneCountForward;
    uint8    LaneCountOncoming;  // 0 in one-way modes
    float    LaneWidth;          // 3.50–3.75 m by environment
    EBarrierType LeftBarrier, RightBarrier;
    ESurfaceType Surface;
    FDecorationBudget Decoration;
    TArray<FRoadFeature> Features;   // signs, lights, gantries, exits, tunnels
    uint32   Seed;               // = Hash(GlobalSeed, Index)
};
```

---

## 2. Geometry

- Each chunk owns a **spline** built from its curvature, grade, and bank, sampled at
  2 m intervals. Chunk N's spline start tangent equals chunk N−1's end tangent exactly
  — continuity is enforced, never approximated.
- Road surface, shoulders, barriers, and curbs are **spline-swept meshes** generated at
  build time per archetype and instanced per chunk with a deformation to the spline
  (Unreal: spline mesh components; Unity/Godot: procedural mesh from the spline).
- Terrain skirts are generated to meet the road edge, then blended into the environment
  heightfield.
- Scatter (vegetation, rocks, poles, signs, buildings) is placed by a seeded Poisson-disc
  sample within the chunk's decoration budget, then batched into HISM/MultiMesh
  instances per chunk.

### 2.1 Floating origin — mandatory

At 385 km/h a run covers 64 km in 10 minutes and passes 250 km inside 40 minutes.
A single-precision float's spacing at 131 km is already 1.6 cm and at 262 km it is
3.1 cm — the physics visibly jitters well before the run ends.

```
if (|playerPosition| > 4096 m) {
    offset = -playerPosition (snapped to a 4096 m grid)
    translate every actor, spline, particle system, decal, audio emitter,
      physics body, and cached position by offset
    emit OriginRebased(offset)
}
```

Every system that caches a world position must subscribe to `OriginRebased`. This is
the single most common source of bugs in endless runners — build it in M2, not later,
and add an automated test that drives 500 km and asserts positional accuracy.

---

## 3. Archetypes

Weights are the base distribution and sum to 100. `Max run` is the maximum number of
consecutive chunks of that archetype.

| Archetype | Weight | Max run | Length | Constraints |
|---|---|---|---|---|
| Long straight | 20% | 3 | 250–500 m | |
| Gentle curve | 22% | 3 | 250 m | R = 1,200–2,500 m |
| Sweeper | 10% | 2 | 250–500 m | R = 600–1,200 m. Requires the sightline check |
| Crest | 8% | 1 | 250 m | Grade +1.5° to +4°. Height clamped by sightline |
| Dip | 8% | 1 | 250 m | Grade −1.5° to −4° |
| Tunnel | 5% | 3 | 250–750 m | Straight or gentle only. Audio + lighting change |
| Bridge | 5% | 2 | 250–500 m | Solid barriers, different surface audio, open sky |
| Overpass | 4% | 1 | 250 m | Road passes over another; visual only |
| Underpass | 4% | 1 | 250 m | Brief shadow + audio change |
| Construction | 5% | 2 | 250–500 m | 1–2 lanes closed, cones, barriers, workers' vehicles |
| Exit ramp | 5% | 1 | 250 m | Visual only in v1; the player cannot leave the highway |
| Toll gantry | 2% | 1 | 250 m | Overhead structure, lane-position markers |
| Rest stop | 2% | 1 | 250 m | Roadside buildings, parked vehicles, visual only |

### 3.1 Grammar rules (hard constraints)

```
- No archetype may exceed its "Max run" of consecutive chunks.
- Tunnel cooldown: 8 chunks. Bridge cooldown: 6. Construction cooldown: 10.
- No construction zone within 3 chunks of a lane-count change.
- No crest immediately followed by a sweeper (compound sightline failure).
- Curvature must not change sign in consecutive chunks by more than 0.0012 1/m
  (prevents jarring S-bends at 300 km/h).
- Total curvature over any 1 km window is clamped so the highway does not spiral.
- Grade over any 1 km window sums to within ±25 m of zero (no infinite climbs).
- The first 3 chunks of any run are always Long straight, clear, and full lane count.
- Lane-count changes occur only inside a designated Merge chunk with a proper taper
  over ≥ 180 m, with signage 250 m in advance.
```

### 3.2 Difficulty-driven weighting

Archetype weights shift with run distance `d` (km):

```
straightWeight  *= lerp(1.6, 0.7, clamp(d/20, 0, 1))
curveWeight     *= lerp(0.6, 1.5, clamp(d/20, 0, 1))
sweeperWeight   *= lerp(0.2, 1.4, clamp(d/20, 0, 1))
constructionW   *= lerp(0.0, 1.8, clamp((d-3)/15, 0, 1))
tunnelWeight    *= 1.0 + (pursuitActive ? 1.5 : 0)     // tunnels help during chases
```

---

## 4. The sightline constraint

Before a chunk is accepted by the grammar, verify:

```
requiredSightline = max(120, playerSpeed_ms * 4.0)     // metres
actualSightline   = raycast along the road centerline at driver eye height (1.15 m),
                    stepping 5 m, until occluded by geometry, terrain, or fog

if (actualSightline < requiredSightline) → reject the chunk, re-roll with reduced
                                            curvature / crest height
```

Fog density from the weather system is fed into this check. In Fog mode the maximum
allowed curvature and crest height drop accordingly — the road physically straightens
in heavy fog, which players read as "the fog is on a flat stretch" rather than noticing
the constraint.

For hazards the requirement is 5.0 s.

---

## 5. Lane system

```cpp
struct FLane {
    int32  Index;          // 0 = rightmost forward lane, negative = oncoming
    float  CenterOffset;   // metres from spline center
    ELaneDirection Direction;
    bool   bClosed;        // construction
    ESurfaceType Surface;
};
```

Lane centerlines are queried by every system: traffic follows them, the lane-snap assist
pulls toward them, the solvability grid is built on them, and the near-miss detector
uses them for lane-split detection. Lane geometry is authoritative — never derive lane
position from the visual mesh.

Lane width: 3.50 m (European Motorway, Japanese Expressway), 3.65 m (American
Interstate, Modern City, most), 3.75 m (Desert, Middle Eastern Highway).

---

## 6. Road furniture

Per environment (see `docs/13-content-manifest.md` for the full sets):

**Barriers:** W-beam guardrail, concrete Jersey barrier, cable barrier, stone wall,
snow bank, sand berm, city curb + railing, tunnel wall.

**Signage:** overhead gantries, exit signs, speed limit, distance markers, warning
signs, construction signage, chevron curve markers, kilometer posts. **Every sign uses
invented place names and invented route shields** — never real jurisdictions' sign
standards traced exactly, never real place names.

**Lighting:** highway pole lights (single and double arm), tunnel lighting strips,
bridge lighting, city ambient, none (rural). Pole spacing 35–45 m, alternating sides on
rural roads, both sides in cities.

**Markings:** lane dividers (dashed, solid, double), edge lines, chevrons, arrows, exit
hatching, rumble strips, worn patches, tire marks, repair scars, manholes, expansion
joints. Decal-based on top of the road material, batched per chunk.

**Roadside:** vegetation by biome, rocks, embankments, fences, billboards (invented
brands), buildings, parked vehicles, power lines, hoardings, drainage.

---

## 7. Materials

Road surface uses a layered master material:

| Layer | Purpose |
|---|---|
| Base asphalt/concrete | Albedo, roughness, normal, tiled with two UV scales to break repetition |
| Macro variation | Large-scale noise on roughness and albedo — kills the tiling |
| Wear mask | Darker, smoother wheel tracks in each lane. Aligned to the lane system |
| Wetness | 0→1 parameter from the weather system. Drops roughness, raises specular, enables puddle normals |
| Puddle mask | A noise mask × wetness × a road-camber term so puddles pool at the low edge |
| Snow cover | 0→1, accumulates in the gutter and between wheel tracks first |
| Decal layer | Markings, repairs, tire marks, oil |

**Wet asphalt is the highest-value visual in the game.** It turns every headlight, sign,
and taillight into a streaked reflection. Budget generously for it.

---

## 8. Environment transitions

In modes that traverse multiple environments (Free Ride, long Classic runs past 30 km),
transitions occur over a dedicated 750 m blend region: skybox cross-fade, fog parameter
lerp, scatter set cross-fade with a mixed band, road material blend, audio bed
cross-fade, and a traffic-mix lerp. Never cut.

---

## 9. Generation acceptance tests

| Test | Assertion |
|---|---|
| Determinism | Seed S produces byte-identical chunk descriptors across 3 runs and 2 machines |
| Continuity | Zero tangent discontinuities across 10,000 consecutive chunks |
| Sightline | Zero chunks violating the 4.0 s rule at any speed up to 385 km/h |
| Grammar | Zero constraint violations over 100,000 generated chunks |
| Precision | 500 km drive: position error < 1 cm, zero visible jitter |
| Performance | Chunk generation ≤ 4 ms worker, ≤ 0.8 ms game thread, over 10,000 chunks |
| No hitch | 30-minute run, zero frames exceeding the §17 budget attributable to generation |
| Grade closure | Elevation over any 1 km window within ±25 m of zero |
| Lane continuity | Every lane-count change has a ≥180 m taper and advance signage |
