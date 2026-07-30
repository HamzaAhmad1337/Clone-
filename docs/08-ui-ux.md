# 08 — UI and UX

---

## 1. Design language

**Dark, high-contrast, minimal chrome, fast motion.**

- Background: near-black (#0A0C10) with subtle environment-tinted gradients.
- Surface: #14181F, elevated #1C222B.
- Text: #F2F5F8 primary, #9AA5B4 secondary, #5C6675 disabled.
- Accent: **per environment.** Cyberpunk #FF3FA4, Desert #FFA33F, Snow #6FD2FF,
  Forest #57D98A, City #4C8DFF, etc. The accent drives buttons, focus rings, progress
  bars, and the HUD combo ring.
- Semantic: success #3FD98A, warning #FFC24C, danger #FF5A5A, premium #C77DFF.
- Type: one geometric sans, 4 weights. Numerals are **tabular** everywhere a number
  changes (speed, score, currency) — proportional numerals jitter and look cheap.
- Motion: 140 ms for micro-interactions, 220 ms for screen transitions, ease-out
  cubic. **Never bouncy, never elastic.** Fast and confident.
- Corner radius 6 px, borders 1 px at 12% white, elevation via subtle shadow not glow.

**Rule:** every interactive element has hover, focus, press, disabled, and selected
states. Focus states must be visible without a mouse — a 2 px accent ring plus a scale
to 1.02.

---

## 2. Navigation model

Full parity across mouse, keyboard, and gamepad. **The mouse is never required.**

- An explicit focus graph per screen. Every element declares its up/down/left/right
  neighbors. Never rely on spatial auto-navigation for anything non-trivial — it always
  gets one case wrong and that case is always in the garage.
- Consistent global bindings: `Esc`/`B` = back, `Enter`/`A` = confirm, `Tab`/bumpers =
  tab switch, `Space`/`Y` = context action.
- On-screen button prompts swap glyph sets within one frame of a device change.
- No screen is more than 3 inputs deep from the main menu.
- **Every screen shows the currency bar and the player level** in a persistent header.

---

## 3. Screen map

```
Boot ─▶ Main Menu ─┬─▶ DRIVE ─▶ Mode Select ─▶ Map Select ─▶ Car Select ─▶ RUN
                   │                                             │
                   │                                             └─▶ (quick start skips
                   │                                                  to last used)
                   ├─▶ GARAGE ─┬─▶ Customize ─┬─ Paint / Wraps / Decals
                   │           │              ├─ Body kit / Spoilers / Rims
                   │           │              └─ Lights / Interior / Plate
                   │           ├─▶ Upgrade    (10 categories × 5 tiers)
                   │           └─▶ Test Drive (60 s Free Ride demo)
                   ├─▶ SHOP ───┬─ Vehicles / Cosmetics / Bundles
                   ├─▶ CAREER ─┬─ Career ladder / Daily / Weekly / Event
                   ├─▶ STATS ──┬─ Statistics / Achievements / Leaderboards / Replays
                   └─▶ SETTINGS ┬ Graphics / Audio / Controls / Gameplay
                                └ Accessibility / Language / Account

RUN ─▶ Pause ─┬─ Resume / Restart / Settings / Quit
     └─▶ Results ─┬─ Continue / Restart / Share / Garage
```

**Quick start rule:** from the main menu, pressing `Enter` once starts a run with the
last-used mode, map, and car. Anything that adds friction to starting a run is a
retention bug.

---

## 4. HUD

Default layout occupies the bottom 14% and the top-right corner only. The road, the
horizon, and the center of the screen stay clear.

```
┌───────────────────────────────────────────────────────────────────────┐
│                                                    ┌────────────────┐ │
│                                                    │  SCORE 148,220 │ │
│                                                    │  12.4 km  3:07 │ │
│                                                    └────────────────┘ │
│                                                                       │
│                        [ road stays clear ]                           │
│                                                                       │
│                                                                       │
│         ╭─────╮                                                       │
│         │ ×7  │  ← combo ring (shrinking arc = time left)             │
│         ╰─────╯                                                       │
│  ┌──────────────────┐                      ┌───────────────────────┐  │
│  │   ╱‾‾‾‾╲   284   │                      │ NITRO ███████░░░  73% │  │
│  │  │ tach │  km/h  │  gear 6              │ [mode widget]         │  │
│  │   ╲____╱         │                      └───────────────────────┘  │
│  └──────────────────┘                                                 │
└───────────────────────────────────────────────────────────────────────┘
```

### 4.1 Elements (each individually toggleable, HUD scale 50–200%)

| Element | Detail |
|---|---|
| Speed | Large tabular digital + a tachometer arc. km/h or mph, switchable |
| Gear | Large numeral, flashes at redline |
| Nitrous | Horizontal bar, segmented by upgrade tier, pulses when full |
| Combo | Combo count `×N` (1–20) in a shrinking ring showing time remaining, with the resulting score multiplier as a smaller figure beneath. Punch-scales on increase |
| Score | Top-right, tabular, counts up smoothly (never snaps) |
| Distance | Top-right, below score |
| Timer | Top-right, run elapsed |
| Mode widget | Fuel gauge / countdown clock / wanted stars, mode-dependent |
| Near-miss popups | World-space `+N`, drifting back with the passed vehicle, 1.1 s life |
| Rear indicator | A minimal arc at the top showing traffic closing from behind (Two-Way, Police) |
| Damage | Small car silhouette, only appears when damaged |
| Assist indicators | Small icons that flash when ABS/TC/ESC intervene |
| Warnings | "PURSUIT AHEAD", "SPIKE STRIP", "LANE CLOSED" — centered, 1.4 s, high contrast |

### 4.2 HUD presets
`Full` · `Standard` (default) · `Minimal` (speed + combo only) · `Clean` (speed only) ·
`Off`. Hardcore mode forces `Clean`.

---

## 5. Garage

The garage is where the reward pillar is cashed in. It must feel expensive.

- **Turntable** on a dark studio floor with a three-point rig: key, rim, and a large
  soft fill, plus a reflective floor. The car is lit like a product shot.
- Drag to rotate, scroll to zoom, right-drag to orbit vertically. Auto-slow-rotate when
  idle.
- **First-unlock reveal:** the lights come up, the door opens, the interior lights,
  the engine starts, and the camera pushes in. 4 seconds, skippable, plays exactly once
  per car. This is the single highest-value 4 seconds in the entire meta game.
- **Live preview:** every customization applies instantly with no loading. Paint, rims,
  body kits, ride height — all visible on the turntable as the player scrolls the list.
- **Stat comparison:** a bar chart against the currently equipped car, with deltas shown
  in exact numbers. Green up, red down. Never hide a stat.
- **Test Drive** on every car including locked ones — a 60-second Free Ride demo with a
  "BUY — 84,000" button on screen. This sells cars better than any stat sheet, and
  giving away a demo of a locked car is the most effective conversion tool in the genre.

### 5.1 Customization UI
Left rail of categories, center 3D view, right panel of options with live thumbnails.
Owned items show a checkmark; unowned show a price; locked show the unlock condition in
plain language ("Reach Driver Level 24" — never "Locked").

Decal editor: free placement with a gizmo, layer list (30 max), per-layer color/
opacity/rotation/scale/mirror, snap-to-symmetry, and 6 save slots with an export code
players can share as text.

---

## 6. Results screen

Must be fully readable in under 4 seconds and skippable at any moment.

```
┌────────────────────────────────────────────────────────────┐
│  RUN COMPLETE                              CLASSIC ENDLESS │
│                                                            │
│   DISTANCE  18.42 km       ★ NEW RECORD                    │
│   SCORE     264,684                                        │
│   TOP SPEED 312 km/h                                       │
│   NEAR MISS 147   (best combo ×16)                         │
│                                                            │
│   ┌──────────────────────────────────────────────────┐     │
│   │  speed / distance graph, near misses marked      │     │
│   └──────────────────────────────────────────────────┘     │
│                                                            │
│   SCORE      Distance       3,684                          │
│              Near misses  250,000                          │
│              Speed          4,000                          │
│              Airtime + bonus 7,000                         │
│              Perfect run        0  (contact at 14.2 km)    │
│              ─────────────────────                         │
│              TOTAL        264,684                          │
│                                                            │
│   PAYOUT     264,684 × 0.30  =  +79,405 coins   +412 XP    │
│                                                            │
│   Missions: [Drive 20 km ████████░░ 18.4/20]               │
│                                                            │
│   [R] RESTART      [ENTER] CONTINUE     [S] SHARE CLIP     │
└────────────────────────────────────────────────────────────┘
```

- Score is itemized; coins are a single visible conversion of it (`PROMPT.md` §8.3).
  The player should be able to see, in one glance, that near misses paid for 94% of the
  run. That realization is the whole teaching mechanism of the game.
- The payout counts up over ≤ 1.2 s. Any input skips to the final value instantly.
- New records get an accent-colored callout and a distinct audio sting.
- A **best-moment auto-clip** (the highest-scoring 6 seconds of the run, from the replay
  system) plays in a corner thumbnail and can be exported to MP4/GIF.
- Mission progress deltas animate so the player sees what the run earned them.

---

## 7. Settings

Four tabs, each with a search box. Every setting shows its current value, a one-line
description, and a "Default" restore. Graphics settings show a live preview thumbnail
and an estimated performance impact indicator.

**Graphics:** preset (Low/Medium/High/Ultra/Custom), resolution, window mode, VSync,
frame limit, upscaler (DLSS/FSR/XeSS/TSR/off) + quality, dynamic resolution + target
fps, and individual toggles for every feature in `docs/06-graphics-art.md` §2, plus a
built-in benchmark that runs a fixed 45-second scripted run and reports percentile
frame times.

**Audio:** 6 volume sliders, output device, HRTF toggle, Night Mode compressor,
subtitle settings.

**Controls:** device selection, full remapping per device, deadzones, response curve,
force-feedback strength (wheel), rumble strength, steering assist strength, invert
options, toggle-vs-hold per action.

**Gameplay:** units (km/h / mph), transmission type, individual assist toggles, HUD
preset and per-element toggles, camera default, auto-restart on crash, tutorial hints,
speedometer style.

**Accessibility:** the full list in `PROMPT.md` §18, on its own tab, not buried.

**Account:** cloud save, profile management (3 slots), telemetry opt-in, data export,
data deletion.

---

## 8. Localization

- 14 languages at launch: English, Spanish (ES + LATAM), Portuguese (BR), French,
  German, Italian, Russian, Polish, Turkish, Arabic, Japanese, Korean, Simplified
  Chinese, Traditional Chinese.
- **Zero hardcoded strings.** Every string comes from a keyed table. A build-time lint
  fails on any literal in a UI-facing code path.
- RTL layout support for Arabic — mirrored layouts, not just mirrored text.
- CJK font fallback chain, and layout that tolerates 40% string expansion (German) and
  60% contraction (CJK) without clipping. Test with a pseudo-localization mode that
  expands every string by 40% and wraps it in brackets.
- Numbers, dates, and currency formatted per locale. Speed units default by locale
  (mph for US/UK).

---

## 9. UX acceptance tests

| Test | Assertion |
|---|---|
| Time to first run | Cold boot → driving in ≤ 25 s including all logos |
| Restart | Crash → driving again in ≤ 1.5 s |
| Gamepad-only playthrough | Every screen and action reachable, zero mouse required |
| Keyboard-only playthrough | Same |
| Results readability | Testers report distance, score, and payout after 4 s exposure |
| Pseudo-loc | Zero clipped or overlapping strings at +40% expansion |
| RTL | Arabic layout fully mirrored, zero misaligned elements |
| Focus | Zero screens with an unreachable interactive element |
| Frame cost | UI ≤ 0.5 ms game thread, ≤ 0.6 ms GPU |
