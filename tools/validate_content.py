#!/usr/bin/env python3
"""Content validator for Highway Rush data files.

Implements the build-blocking lints from docs/10-data-schemas.md §9 that can be
checked without a full JSON Schema library, so CI can run this with a stock Python.
Structural validation against data/schemas/*.schema.json is a separate step that
requires `jsonschema`; this script skips it gracefully if the package is absent.

Usage:  python3 tools/validate_content.py [data_dir]
Exit code 0 = clean, 1 = one or more errors.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ERRORS: list[str] = []
WARNINGS: list[str] = []


def error(path: Path, msg: str) -> None:
    ERRORS.append(f"{path}: {msg}")


def warn(path: Path, msg: str) -> None:
    WARNINGS.append(f"{path}: {msg}")


def load_all(data_dir: Path) -> dict[Path, dict]:
    """Parse every authored JSON file under data_dir.

    Skips schemas, and skips generated output (grey-box placeholders from
    tools/generate_greybox.py) — those are derived artifacts, not content.
    """
    docs: dict[Path, dict] = {}
    generated = {"schemas", "greybox"}
    for path in sorted(data_dir.rglob("*.json")):
        if generated & set(path.parts):
            continue
        try:
            docs[path] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(path, f"invalid JSON: {exc}")
    return docs


def check_unique_ids(docs: dict[Path, dict]) -> None:
    seen: dict[str, Path] = {}
    for path, doc in docs.items():
        doc_id = doc.get("id")
        if doc_id is None:
            error(path, "missing required field 'id'")
            continue
        if doc_id in seen:
            error(path, f"duplicate id '{doc_id}' (also in {seen[doc_id]})")
        else:
            seen[doc_id] = path


def check_localization_keys(docs: dict[Path, dict]) -> None:
    """Every *Key field must look like a localization key, never a literal string."""
    def walk(node, path: Path, trail: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key.endswith("Key"):
                    if not isinstance(value, str) or "." not in value or " " in value:
                        error(path, f"{trail}.{key} is not a localization key: {value!r}")
                else:
                    walk(value, path, f"{trail}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path, f"{trail}[{i}]")

    for path, doc in docs.items():
        walk(doc, path, "")


# --- Vehicle-specific physical coherence lints -----------------------------------

CLASS_POWER_KW = {
    "Budget": 29, "Starter": 82, "Economy": 96, "HotHatch": 180, "Sedan": 165, "Muscle": 350,
    "Sports": 300, "Super": 480, "Hyper": 720, "Luxury": 280, "SUV": 220,
    "Pickup": 260, "Van": 150, "OffRoad": 290, "Classic": 145, "Electric": 560,
    "Track": 440, "Bike": 145,
}


def peak_power_kw(torque_curve: list[list[float]]) -> tuple[float, float]:
    """Return (peak power in kW, rpm at which it occurs) from an [rpm, Nm] curve."""
    best_kw, best_rpm = 0.0, 0.0
    for rpm, nm in torque_curve:
        kw = nm * rpm * math.pi / 30.0 / 1000.0
        if kw > best_kw:
            best_kw, best_rpm = kw, rpm
    return best_kw, best_rpm


def check_vehicles(docs: dict[Path, dict]) -> None:
    for path, doc in docs.items():
        if "vehicles" not in path.parts:
            continue

        powertrain = doc.get("powertrain", {})
        curve = powertrain.get("torqueCurveNm")
        derived = doc.get("derivedStats", {})
        vclass = doc.get("class")

        # Torque curve must be sorted by rpm and stay within the rev range.
        if isinstance(curve, list) and curve:
            rpms = [point[0] for point in curve]
            if rpms != sorted(rpms):
                error(path, "torqueCurveNm points are not sorted by ascending rpm")
            max_rpm = powertrain.get("maxRpm")
            if max_rpm is not None and rpms[-1] > max_rpm:
                error(path, f"torque curve extends to {rpms[-1]} rpm, above maxRpm {max_rpm}")

            # docs/10 §9: peak power must land within 10% of the class figure.
            kw, rpm = peak_power_kw(curve)
            expected = CLASS_POWER_KW.get(vclass)
            if expected and abs(kw - expected) / expected > 0.10:
                warn(path, f"peak power {kw:.0f} kW @ {rpm:.0f} rpm is "
                           f"{100 * (kw - expected) / expected:+.0f}% vs the "
                           f"{vclass} baseline of {expected} kW")
            stated = derived.get("peakPowerKw")
            if stated is not None and abs(kw - stated) / stated > 0.05:
                error(path, f"derivedStats.peakPowerKw {stated} disagrees with the "
                            f"torque curve ({kw:.0f} kW)")

        # Redline must not exceed maxRpm.
        redline, max_rpm = powertrain.get("redlineRpm"), powertrain.get("maxRpm")
        if redline and max_rpm and redline > max_rpm:
            error(path, f"redlineRpm {redline} exceeds maxRpm {max_rpm}")

        # Gear ratios must decrease monotonically.
        ratios = powertrain.get("transmission", {}).get("gearRatios")
        if isinstance(ratios, list) and ratios != sorted(ratios, reverse=True):
            error(path, "gearRatios must be monotonically decreasing")

        # Downforce coefficients are positive by convention (docs/10 §1).
        physics = doc.get("physics", {})
        for key in ("downforceCoefficientFront", "downforceCoefficientRear"):
            value = physics.get(key)
            if value is not None and value < 0:
                error(path, f"{key} is negative ({value}); positive means downforce")

        # Token purity: no vehicle may be priced in premium currency (docs/09 §1).
        if doc.get("unlock", {}).get("priceTokens") is not None:
            error(path, "vehicles may never be priced in Tokens (docs/09 §1)")


def check_licensed(docs: dict[Path, dict]) -> None:
    """Lints for the real-manufacturer marque-mapping layer (docs/20 §7).

    The invented `marque` is the permanent fallback and must always be present, so
    that shipping with HR_LICENSED_CONTENT off is a build flag rather than an audit.
    """
    for path, doc in docs.items():
        licensed = doc.get("licensed")
        if licensed is None:
            continue

        # T-LIC-02 precondition: an invented fallback must exist.
        if not doc.get("marque"):
            error(path, "has a 'licensed' block but no invented 'marque' fallback "
                        "— shipping unlicensed would leave this vehicle nameless")

        for field in ("manufacturer", "model", "displayName"):
            if not licensed.get(field):
                error(path, f"licensed.{field} is missing or empty")

        # T-LIC-07: police and emergency vehicles never carry a real identity.
        if set(doc.get("tags", [])) & {"police", "emergency", "pursuit"}:
            error(path, "police/emergency vehicles may not carry a licensed identity "
                        "(docs/20 §5)")

        # The displayed name should actually name the manufacturer.
        manufacturer = licensed.get("manufacturer") or ""
        display = licensed.get("displayName") or ""
        if manufacturer and manufacturer.lower() not in display.lower():
            warn(path, f"licensed.displayName {display!r} does not contain the "
                       f"manufacturer {manufacturer!r}")


def check_token_purity(docs: dict[Path, dict]) -> None:
    """Nothing bought with Tokens may touch a stat field."""
    stat_fields = {"torqueMultiplier", "massMultiplier", "downforceMultiplier",
                   "brakeTorqueMultiplier", "nitrousCapacitySeconds",
                   "surfaceGripMultiplier", "payoutMultiplier"}
    for path, doc in docs.items():
        if doc.get("priceTokens") is None:
            continue
        effects = doc.get("effects", {})
        offending = stat_fields.intersection(effects)
        if offending:
            error(path, f"token-priced item affects stats: {sorted(offending)}")


def main() -> int:
    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    if not data_dir.is_dir():
        print(f"error: no such directory: {data_dir}", file=sys.stderr)
        return 1

    docs = load_all(data_dir)
    check_unique_ids(docs)
    check_localization_keys(docs)
    check_vehicles(docs)
    check_licensed(docs)
    check_token_purity(docs)

    for message in WARNINGS:
        print(f"warning: {message}")
    for message in ERRORS:
        print(f"error:   {message}", file=sys.stderr)

    print(f"\n{len(docs)} content file(s) checked, "
          f"{len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
