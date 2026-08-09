#!/usr/bin/env python3
"""Generate grey-box placeholder vehicle meshes from the vehicle data files.

Purpose: M1 ("Drive a box") and M4 ("The verb") are the two hard gates in
PROMPT.md §20, and neither needs a single purchased 3D model — M1 is explicitly a
grey box on an empty plane. This generates those boxes at correct real-world
dimensions, with the correct pivot and the full socket set from
docs/21-art-asset-delivery.md §3.3.

That unblocks M1 through M6 with zero art spend and zero licensing exposure, and it
validates the whole data → mesh → socket pipeline before any real model is bought.

Emits, per vehicle:
    <out>/SM_<id>_LOD0.obj    body + 4 wheels, correct scale, correct pivot
    <out>/SM_<id>_sockets.json  every socket position from docs/21 §3.3

Coordinates follow docs/21 §3.1: centimetres, +X forward, +Z up, pivot at ground
level centred between the front wheels' contact patches.

Usage:  python3 tools/generate_greybox.py [data_dir] [out_dir]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Body height and ground clearance are not in the vehicle schema (they are visual,
# not simulated), so derive plausible values per class. Metres.
CLASS_PROFILE = {
    "Budget":   (1.41, 0.16), "Starter":  (1.48, 0.15), "Economy":  (1.47, 0.15),
    "HotHatch": (1.43, 0.13), "Sedan":    (1.44, 0.13), "Muscle":   (1.38, 0.12),
    "Sports":   (1.29, 0.11), "Super":    (1.20, 0.09), "Hyper":    (1.14, 0.08),
    "Luxury":   (1.47, 0.13), "SUV":      (1.72, 0.21), "Pickup":   (1.94, 0.22),
    "Van":      (1.98, 0.17), "OffRoad":  (1.90, 0.26), "Classic":  (1.35, 0.14),
    "Electric": (1.44, 0.12), "Track":    (1.10, 0.07), "Bike":     (1.10, 0.13),
    "Special":  (1.40, 0.14),
}
DEFAULT_PROFILE = (1.45, 0.14)

M_TO_CM = 100.0


def box(cx, cy, cz, sx, sy, sz):
    """Axis-aligned box centred at (cx,cy,cz) with full sizes (sx,sy,sz)."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    verts = [
        (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz),
    ]
    faces = [(1, 2, 3, 4), (5, 8, 7, 6), (1, 5, 6, 2),
             (2, 6, 7, 3), (3, 7, 8, 4), (4, 8, 5, 1)]
    return verts, faces


def cylinder(cx, cy, cz, radius, width, segments=12):
    """Wheel: a cylinder whose axis runs along Y (the vehicle's lateral axis)."""
    verts, faces = [], []
    hw = width / 2
    for side, offset in ((0, -hw), (1, hw)):
        for i in range(segments):
            a = 2 * math.pi * i / segments
            verts.append((cx + radius * math.cos(a), cy + offset,
                          cz + radius * math.sin(a)))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i + 1, j + 1, j + 1 + segments, i + 1 + segments))
    # Caps as fans from the first vertex of each ring.
    for i in range(1, segments - 1):
        faces.append((1, i + 1, i + 2))
        faces.append((1 + segments, i + 2 + segments, i + 1 + segments))
    return verts, faces


def write_obj(path: Path, groups: list[tuple[str, list, list]]) -> None:
    lines, offset = [f"# Highway Rush grey-box placeholder", "# units: centimetres, +X forward, +Z up"], 0
    for name, verts, faces in groups:
        lines.append(f"g {name}")
        for v in verts:
            lines.append(f"v {v[0]:.2f} {v[1]:.2f} {v[2]:.2f}")
        for f in faces:
            lines.append("f " + " ".join(str(i + offset) for i in f))
        offset += len(verts)
    path.write_text("\n".join(lines) + "\n")


def build(doc: dict) -> tuple[list, dict]:
    physics = doc["physics"]
    vclass = doc.get("class", "Sedan")
    height, clearance = CLASS_PROFILE.get(vclass, DEFAULT_PROFILE)

    wheelbase = physics["wheelbaseM"]
    width = physics["widthM"]
    length = physics.get("lengthM", wheelbase * 1.62)
    track_f = physics.get("trackFrontM", width * 0.86)
    track_r = physics.get("trackRearM", track_f)
    tyre_r = physics.get("tyreRadiusM", 0.32)
    tyre_w = physics.get("tyreWidthM", 0.22)

    # docs/21 §3.1: pivot at ground level, centred between the front contact patches.
    # Front axle sits at X = 0; the body extends backward.
    overhang_total = max(length - wheelbase, 0.30)
    front_overhang = overhang_total * 0.45
    body_front = front_overhang
    body_rear = -(wheelbase + overhang_total * 0.55)
    body_cx = (body_front + body_rear) / 2
    body_len = body_front - body_rear
    body_cz = clearance + (height - clearance) / 2
    body_h = height - clearance

    groups = []
    v, f = box(body_cx * M_TO_CM, 0.0, body_cz * M_TO_CM,
               body_len * M_TO_CM, width * M_TO_CM, body_h * M_TO_CM)
    groups.append(("body", v, f))

    wheels = {
        "wheel_fl": (0.0, -track_f / 2), "wheel_fr": (0.0, track_f / 2),
        "wheel_rl": (-wheelbase, -track_r / 2), "wheel_rr": (-wheelbase, track_r / 2),
    }
    for name, (wx, wy) in wheels.items():
        v, f = cylinder(wx * M_TO_CM, wy * M_TO_CM, tyre_r * M_TO_CM,
                        tyre_r * M_TO_CM, tyre_w * M_TO_CM)
        groups.append((name, v, f))

    # Full socket set from docs/21 §3.3, in centimetres.
    def cm(x, y, z):
        return {"x": round(x * M_TO_CM, 1), "y": round(y * M_TO_CM, 1),
                "z": round(z * M_TO_CM, 1)}

    eye_x = -wheelbase * 0.42
    sockets = {name: cm(wx, wy, tyre_r) for name, (wx, wy) in wheels.items()}
    sockets.update({
        "seat_driver":   cm(eye_x, -width * 0.22, clearance + body_h * 0.42),
        "cam_cockpit":   cm(eye_x, -width * 0.22, clearance + body_h * 0.72),
        "cam_hood":      cm(body_front * 0.55, 0.0, height * 0.92),
        "cam_bumper":    cm(body_front, 0.0, clearance + 0.25),
        "exhaust_l":     cm(body_rear, -width * 0.28, clearance + 0.10),
        "exhaust_r":     cm(body_rear, width * 0.28, clearance + 0.10),
        "headlight_l":   cm(body_front, -width * 0.34, clearance + body_h * 0.42),
        "headlight_r":   cm(body_front, width * 0.34, clearance + body_h * 0.42),
        "taillight_l":   cm(body_rear, -width * 0.36, clearance + body_h * 0.46),
        "taillight_r":   cm(body_rear, width * 0.36, clearance + body_h * 0.46),
        "brake_l":       cm(body_rear, -width * 0.30, clearance + body_h * 0.50),
        "brake_r":       cm(body_rear, width * 0.30, clearance + body_h * 0.50),
        "indicator_fl":  cm(body_front, -width * 0.44, clearance + body_h * 0.38),
        "indicator_fr":  cm(body_front, width * 0.44, clearance + body_h * 0.38),
        "indicator_rl":  cm(body_rear, -width * 0.44, clearance + body_h * 0.42),
        "indicator_rr":  cm(body_rear, width * 0.44, clearance + body_h * 0.42),
        "reverse_l":     cm(body_rear, -width * 0.20, clearance + body_h * 0.40),
        "reverse_r":     cm(body_rear, width * 0.20, clearance + body_h * 0.40),
        "plate_front":   cm(body_front, 0.0, clearance + body_h * 0.22),
        "plate_rear":    cm(body_rear, 0.0, clearance + body_h * 0.26),
        "underglow_anchor": cm(body_cx, 0.0, clearance * 0.5),
        "gauge_tach":    cm(eye_x + 0.55, -width * 0.22, clearance + body_h * 0.58),
        "gauge_speed":   cm(eye_x + 0.55, -width * 0.10, clearance + body_h * 0.58),
    })

    meta = {
        "vehicleId": doc["id"],
        "class": vclass,
        "units": "centimetres",
        "axes": "+X forward, +Y right, +Z up",
        "pivot": "ground level, centred between front wheel contact patches (docs/21 §3.1)",
        "dimensionsM": {"length": round(length, 3), "width": round(width, 3),
                        "height": round(height, 3), "wheelbase": round(wheelbase, 3)},
        "sockets": sockets,
        "note": "Placeholder geometry for M1–M6. Replace with a real mesh at M12; "
                "the socket layout is the contract a delivered model must match.",
    }
    return groups, meta


def main() -> int:
    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "data/greybox")
    vehicles = sorted((data_dir / "vehicles").glob("*.json"))
    if not vehicles:
        print(f"error: no vehicle files under {data_dir / 'vehicles'}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for path in vehicles:
        doc = json.loads(path.read_text(encoding="utf-8"))
        groups, meta = build(doc)
        stem = f"SM_{doc['id']}"
        write_obj(out_dir / f"{stem}_LOD0.obj", groups)
        (out_dir / f"{stem}_sockets.json").write_text(json.dumps(meta, indent=2) + "\n")
        d = meta["dimensionsM"]
        print(f"{stem}: {d['length']}×{d['width']}×{d['height']} m, "
              f"{len(meta['sockets'])} sockets")

    print(f"\n{len(vehicles)} grey-box vehicle(s) written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
