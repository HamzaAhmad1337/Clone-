# Content data

Working example content files, one per type, plus their JSON Schemas. These are the
templates an implementation copies — the point of the architecture is that **adding a
car, mode, environment, weather state, mission, or modifier requires zero code changes**
(`PROMPT.md` §19.2 rule 2).

Full field reference: [`docs/10-data-schemas.md`](../docs/10-data-schemas.md).

## Layout

```
data/
├── vehicles/       one file per playable vehicle (80 at ship)
├── environments/   one per biome (14 at ship)
├── modes/          one per game mode (15 at ship)
├── modifiers/      composable rule flags for daily/weekly events
├── missions/       daily, weekly, and career objectives
├── achievements/   100 at ship
├── weather/        9 states
├── traffic/        traffic vehicle definitions (32 models)
├── upgrades/       the shared upgrade table
└── schemas/        JSON Schema for each type
```

## Validation

```bash
python3 tools/validate_content.py data
```

Runs the build-blocking lints from `docs/10-data-schemas.md` §9 with no third-party
dependencies: JSON parse, ID uniqueness, localization-key form, torque-curve ordering
and rev-range sanity, peak-power coherence against the class baseline in
`docs/03-vehicle-physics.md` §7, monotonic gear ratios, downforce sign convention, and
Token purity (nothing bought with premium currency may touch a stat).

Exit code 0 is clean; any error fails the build. Structural validation against
`data/schemas/*.schema.json` is a separate step requiring the `jsonschema` package.

## Conventions

- **IDs** are `lower_snake_case`, globally unique across every content type.
- **No literal strings.** Anything player-facing is a `*Key` pointing at the
  localization table. The validator rejects literals in `*Key` fields.
- **Units are in the field name.** `massKg`, `springStiffnessNPerM`, `shiftTimeMs`,
  `sightlineMetres`. Never a bare number whose unit you have to guess.
- **Downforce is positive.** Never express it as a negative lift coefficient — the sign
  convention has burned every vehicle game ever made, and the schema rejects negatives.
- **Points, not coins.** Gameplay awards are point values; coins are a single 30%
  conversion of score applied once (`PROMPT.md` §8.3). No content file defines a coin
  award for a driving event.
