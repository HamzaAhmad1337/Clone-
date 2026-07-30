# 10 — Data Schemas

All content is JSON, validated against JSON Schema at build time and pre-commit.
A malformed content file **fails the build** — it never reaches the runtime.

Live examples are in `/data/`. This document is the reference.

---

## 1. Vehicle — `data/vehicles/<id>.json`

```jsonc
{
  "id": "aurel_gt340",
  "displayNameKey": "vehicle.aurel_gt340.name",     // localization key, never a literal
  "marque": "Aurel",                                 // invented marque
  "class": "Sports",                                 // see docs/03 §7
  "unlock": {
    "priceCoins": 420000,
    "priceCash": null,
    "driverLevel": 18,
    "achievement": null,
    "event": null
  },
  "physics": {
    "massKg": 1420,
    "centreOfMass": { "wheelbaseFraction": 0.48, "heightM": 0.46 },
    "wheelbaseM": 2.62, "trackFrontM": 1.60, "trackRearM": 1.62,
    "dragCoefficient": 0.31, "frontalAreaM2": 2.05,
    "widthM": 1.88,
    // Positive = downforce (pushes the car down). Never express this as a negative
    // lift coefficient — the sign convention has burned every vehicle game ever made.
    "downforceCoefficientFront": 0.18, "downforceCoefficientRear": 0.26,
    "driveLayout": "RWD",                            // FWD | RWD | AWD | FourWD
    "driveSplitFrontPct": 0,
    "tyreRadiusM": 0.34, "tyreWidthM": 0.265,
    "defaultCompound": "Sport",
    "steeringLockDeg": 34.0,
    "suspension": {
      "restLengthM": 0.32, "travelM": 0.16,
      "springStiffnessNPerM": { "front": 62000, "rear": 58000 },
      "damperRateNsPerM":     { "front": 5400,  "rear": 5100  },
      "antiRollStiffnessNPerM": { "front": 18000, "rear": 14000 },
      "maxForceMultiplier": 3.0
    }
  },
  "powertrain": {
    "engineFamily": "V6Turbo",                       // drives the audio sample set
    "displacementL": 3.0, "cylinders": 6,
    "idleRpm": 850, "maxRpm": 7600, "redlineRpm": 7200,
    // 8 points, [rpm, Nm]. Torque peaks at 5,000; peak POWER lands higher, at 7,000
    // rpm — 410 N·m × 733 rad/s ≈ 300 kW, which is the Sports class figure in
    // docs/03 §7. The validator enforces that these two agree.
    "torqueCurveNm": [
      [850, 200], [1500, 330], [2500, 410], [3500, 445],
      [5000, 460], [6000, 440], [7000, 410], [7600, 350]
    ],
    "engineBrakeCoefficient": 0.16,
    "inertiaKgM2": 0.24,
    "transmission": {
      "type": "Sequential",                          // Automatic | Sequential | Manual | Single
      "gearRatios": [3.42, 2.24, 1.66, 1.28, 1.03, 0.84],
      "reverseRatio": 3.10, "finalDrive": 3.73,
      "shiftTimeMs": 90, "efficiency": 0.95
    },
    "nitrous": { "capacitySeconds": 4.0, "torqueMultiplier": 1.38, "refillSeconds": 12.0 }
  },
  "derivedStats": {                                   // for UI; asserted against sim in CI
    "topSpeedKmh": 285, "zeroToHundredS": 4.3, "hundredToZeroM": 34.5,
    "peakPowerKw": 300, "peakPowerRpm": 7000,
    "handlingRating": 78, "brakingRating": 74
  },
  "visual": {
    "meshLod0": "SM_Aurel_GT340_LOD0",
    "interiorMesh": "SM_Aurel_GT340_Interior",
    "paintZones": 2,
    "defaultPaint": { "type": "Metallic", "colorHex": "#B32222" },
    "wheelSlots": ["front", "rear"],
    "bodyKitSlots": ["frontBumper", "rearBumper", "sideSkirt", "spoiler", "hood", "diffuser"],
    "exhaustTipCount": 2,
    "exhaustSockets": ["exhaust_l", "exhaust_r"],
    "driverSeatSocket": "seat_driver",
    "cockpitCameraSocket": "cam_cockpit",
    "gaugeBindings": {
      "tachometer": { "socket": "gauge_tach", "minRpm": 0, "maxRpm": 8000, "sweepDeg": 250 },
      "speedometer": { "socket": "gauge_speed", "maxKmh": 320, "sweepDeg": 250 }
    }
  },
  "audio": {
    "engineBank": "EB_V6Turbo_A",
    "pitchOffsetSemitones": 0.5,
    "exhaustLayer": "EX_Sport_Twin",
    "turboLayer": "TB_Medium",
    "hornSample": "HORN_Sport_02",
    "backfireEnabled": true
  },
  "upgradeCaps": { "engine": 5, "turbo": 5, "nitrous": 5, "transmission": 5, "tyres": 5,
                   "brakes": 5, "suspension": 5, "weight": 5, "aero": 5, "cooling": 5 },
  "tags": ["rwd", "turbo", "midEngine", "starterSuper"]
}
```

---

## 2. Environment — `data/environments/<id>.json`

```jsonc
{
  "id": "cyberpunk_city",
  "displayNameKey": "env.cyberpunk_city.name",
  "unlock": { "driverLevel": 28, "priceCoins": 180000 },
  "accentColorHex": "#FF3FA4",
  "road": {
    "laneWidthM": 3.65,
    "trafficSide": "right",                          // right | left
    "surfaceSet": "asphalt_urban_wet",
    "barrierLeft": "concrete_jersey", "barrierRight": "city_railing",
    "markingSet": "urban_neon",
    "lightingSet": "city_dense",
    "signSet": "neon_gantry"
  },
  "chunkWeights": {                                   // overrides docs/05 §3 base weights
    "longStraight": 0.9, "gentleCurve": 1.1, "sweeper": 1.0, "crest": 0.4,
    "dip": 0.5, "tunnel": 1.8, "bridge": 1.4, "overpass": 2.0, "underpass": 1.6,
    "construction": 0.8, "exitRamp": 1.5, "tollGantry": 0.6, "restStop": 0.2
  },
  "laneCountWeights": { "3": 0.2, "4": 0.35, "5": 0.3, "6": 0.15 },
  "scatter": {
    "sets": ["skyscraper_a", "holo_billboard", "street_furniture", "neon_sign"],
    "densityMultiplier": 1.2,
    "nearRoadFalloffM": 8.0
  },
  "atmosphere": {
    "skyboxSet": "night_city_hdri",
    "fogDensity": 0.018, "fogHeightFalloff": 0.4, "fogColorHex": "#1A0F2E",
    "allowedTimesOfDay": ["evening", "night", "midnight"],
    "allowedWeather": ["clear", "cloudy", "rain", "thunderstorm", "fog"],
    "weatherWeights": { "clear": 0.3, "cloudy": 0.15, "rain": 0.35, "thunderstorm": 0.1, "fog": 0.1 }
  },
  "traffic": {
    "typeWeightOverrides": { "sedan": 0.28, "sportsCar": 0.12, "ev": 0.10, "semiTruck": 0.04, "bus": 0.05 },
    "personalityOverrides": { "aggressive": 0.18, "erratic": 0.10, "timid": 0.08 },
    "densityMultiplier": 1.15,
    "speedMeanOffsetKmh": 4
  },
  "audio": {
    "ambienceBed": "AMB_City_Night",
    "reverbZone": "city_canyon",
    "musicCueSet": "MUS_Synthwave"
  },
  "photoModePresets": ["neon_noir", "blade", "chrome"]
}
```

---

## 3. Game mode — `data/modes/<id>.json`

```jsonc
{
  "id": "two_way",
  "displayNameKey": "mode.two_way.name",
  "unlock": { "driverLevel": 3 },
  "rules": {
    "oncomingTraffic": true,
    "oncomingLaneFraction": 0.5,
    "failOnCollision": true,
    "failOnAnyContact": false,
    "brakeEnabled": true,
    "throttleFloor": 0.0,
    "assistsForced": null,                            // null | "off"
    "hudPreset": null,                                // null = player choice
    "fuelEnabled": false,
    "timerEnabled": false,
    "policeEnabled": false,
    "livesCount": 1
  },
  "traffic": { "densityMultiplier": 0.85, "speedMultiplier": 1.0 },
  "scoring": {
    "nearMissMultiplier": 2.0,
    "distanceMultiplier": 1.0,
    "oncomingLanePointsPerSecond": 15,
    "payoutMultiplier": 1.0                           // applied to coins, after the 0.30 conversion
  },
  "environment": { "allowAll": true, "forced": null },
  "timeOfDay": { "allowAll": true, "forced": null },
  "weather": { "allowAll": true, "forced": null },
  "modifiers": [],
  "leaderboards": ["score", "distance", "nearMiss", "topSpeed", "combo"]
}
```

### 3.1 Modifiers — `data/modifiers/<id>.json`

```jsonc
{
  "id": "slippery_roads",
  "displayNameKey": "modifier.slippery_roads.name",
  "descriptionKey": "modifier.slippery_roads.desc",
  "effects": {
    "surfaceGripMultiplier": 0.72,
    "forceWeather": "rain",
    "payoutMultiplier": 1.25
  }
}
```

Valid effect keys are enumerated in the schema. Adding a modifier is a JSON file plus a
localization entry — never a code change.

---

## 4. Mission — `data/missions/<id>.json`

```jsonc
{
  "id": "daily_nearmiss_close_25",
  "category": "daily",
  "displayNameKey": "mission.nearmiss_close.name",
  "levelRange": { "min": 8, "max": 100 },
  "objective": {
    "type": "counter",
    "event": "NearMiss",
    "scope": "run",                                   // run | session | lifetime
    "filter": { "clearanceM": { "lt": 0.55 }, "playerSpeedKmh": { "gt": 150 } },
    "target": 25
  },
  "constraints": { "mode": null, "environment": null, "vehicleClass": null, "weather": null },
  "reward": { "coins": 6000, "cash": 30, "tokens": 0, "xp": 400 },
  "weight": 1.0
}
```

Objective types: `counter` · `accumulator` (sums a numeric field) · `threshold` (reach a
peak value) · `duration` (hold a condition for t seconds) · `sequence` (ordered
sub-objectives) · `absence` (complete X without Y happening).

---

## 5. Achievement — `data/achievements/<id>.json`

```jsonc
{
  "id": "ach_ghost_20",
  "displayNameKey": "ach.ghost_20.name",
  "descriptionKey": "ach.ghost_20.desc",
  "tier": "Gold",                                     // Bronze | Silver | Gold | Platinum
  "hidden": false,
  "objective": { "type": "threshold", "event": "RunEnded",
                 "filter": { "contactCount": 0 }, "field": "distanceKm", "target": 20 },
  "reward": { "coins": 75000, "cash": 80, "tokens": 5 },
  "steamApiName": "GHOST_20"
}
```

---

## 6. Weather — `data/weather/<id>.json`

```jsonc
{
  "id": "thunderstorm",
  "displayNameKey": "weather.thunderstorm.name",
  "surfaceGripMultiplier": 0.74,
  "sightlineMetres": 260,
  "wetness": 1.0,
  "snowCover": 0.0,
  "windVector": { "xMps": 9.0, "yMps": 0.0, "gustMps": 14.0, "gustPeriodS": 7.0 },
  "particleSystem": "PS_Rain_Heavy",
  "lensEffect": "LE_Droplets_Heavy",
  "skyPreset": "SKY_Storm",
  "sunIntensityMultiplier": 0.22,
  "fogDensity": 0.012,
  "postProcess": "PP_Storm",
  "lightning": { "enabled": true, "minIntervalS": 6, "maxIntervalS": 22,
                 "flashDurationMs": 130, "thunderSpeedMps": 343 },
  "audioBed": "AMB_Rain_Heavy",
  "trafficModifiers": { "speedMultiplier": 0.86, "followDistanceMultiplier": 1.5,
                        "densityMultiplier": 0.85, "headlightsForced": true },
  "transitionSeconds": { "min": 25, "max": 60 }
}
```

---

## 7. Upgrade table — `data/upgrades/upgrades.json`

```jsonc
{
  "categories": {
    "engine": {
      "displayNameKey": "upgrade.engine.name",
      "priceFractions": [0.04, 0.08, 0.15, 0.26, 0.42],
      "cashCost":       [0, 0, 0, 25, 60],
      "effects": [
        { "stat": "torqueMultiplier", "perTier": 0.06, "display": "+6% torque" }
      ]
    },
    "weight": {
      "displayNameKey": "upgrade.weight.name",
      "priceFractions": [0.04, 0.08, 0.15, 0.26, 0.42],
      "cashCost":       [0, 0, 0, 25, 60],
      "effects": [
        { "stat": "massMultiplier", "perTier": -0.025, "display": "-2.5% weight" }
      ]
    }
    // … 8 more, see docs/09 §4
  },
  "sellbackFraction": 0.60
}
```

---

## 8. Traffic vehicle — `data/traffic/<id>.json`

```jsonc
{
  "id": "traffic_semi_a",
  "type": "semiTruck",
  "meshSet": "SM_Semi_A",
  "trailerMeshSet": "SM_Trailer_Box",
  "lengthM": 16.5, "widthM": 2.60, "heightM": 4.10, "massKg": 26000,
  "speedMultiplier": 0.80,
  "personalityWeights": { "professional": 0.6, "normal": 0.3, "hurried": 0.1 },
  "laneBias": { "0": 0.5, "1": 0.3, "2": 0.15, "3": 0.05 },
  "colourVariants": ["#FFFFFF", "#2B4C7E", "#8C1A1A", "#3A3A3A", "#C9A227"],
  "nearMissAudioProfile": "NM_Heavy",
  "airDisplacementNewtons": 900,
  "blocksSightline": true,
  "lodDistances": [60, 140, 260, 500]
}
```

---

## 9. Schema validation

Every file above has a matching JSON Schema in `data/schemas/`. Validation runs:

1. **Pre-commit hook** — fast, fails locally.
2. **CI** — authoritative, blocks merge.
3. **Editor hot-reload** — validates on save, surfaces errors in an editor panel.

Additional lints beyond schema validation:

| Lint | Rule |
|---|---|
| Localization | Every `*Key` field resolves in every shipped language |
| Asset references | Every mesh/audio/material reference resolves |
| ID uniqueness | No duplicate IDs across any content type |
| Range | Every numeric field within its documented valid range |
| Derived stats | `derivedStats` match a headless physics sim within tolerance |
| Power/torque coherence | `max(T × rpm × π/30)` over the curve is within 10% of the class power figure |
| Gear ratios | Monotonically decreasing; top gear reaches the stated top speed at ≤ redline |
| Economy | No unlock path violates the 90-minute grind guard |
| Token purity | No token-priced item touches a stat field |
| Orphans | Every content file is reachable from some unlock path |
