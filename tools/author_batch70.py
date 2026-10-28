"""Translate placeholder combat descriptions while preserving exact English move labels."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


MOVE_LABELS = {
    (27, 44): "Flame Pillar", (27, 45): "Volcano Bomb",
    (27, 46): "Heavy Drago Magma", (27, 47): "Raging Flame",
    (27, 48): "Pressure Aqua", (27, 49): "Icicle Bomb",
    (28, 0): "Heavy Hard Rain", (28, 1): "Raging Blizzard",
    (28, 2): "Magnet Wave", (28, 3): "Spark Bomb",
    (28, 4): "Heavy Magnet Power", (28, 5): "Raging Lightning",
    (28, 6): "Rising Laser", (28, 7): "Shining Bomb",
    (28, 8): "Heavy Wind", (28, 9): "Rage Tornado",
    (28, 10): "Darkness Eddy", (28, 11): "Evil Data Bomb",
    (28, 12): "Heavy Gravity", (28, 13): "Rage Demon Breath",
    (28, 14): "Sonic Kick", (28, 15): "Mega Knuckle Bomb",
    (28, 16): "Heavy Giga Uppercut", (28, 17): "Rage Grapple",
    (28, 18): "Sword Masquerade", (28, 19): "Rainbow Hand",
    (28, 20): "Malkuth Crystal", (28, 21): "Hell & Thunder",
    (28, 22): "Heaven & Break", (28, 23): "Ice & Fire",
    (28, 24): "Infinity Sword Rain", (28, 25): "Omega Death Blade",
    (28, 26): "Data to Data", (28, 27): "Tribe Lizard",
    (28, 28): "Sigma Grapple", (28, 29): "Omega Crusher",
    (28, 30): "Chrono DSR", (28, 31): "Origin Nebula",
}


def main() -> None:
    destination = ROOT / "translations/batch70.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for (entry, index), name in MOVE_LABELS.items():
        key = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Move and item descriptions",
            "english": [f"{name}\nPlaceholder text."],
            "sources": ["Original Japanese ROM"],
            "review_note": "The Japanese description is explicitly dummy text. The move title matches the reviewed English battle-move label already used in the game.",
        })
    destination.write_text(json.dumps({
        "description": "Translate 38 dummy descriptions in MESPAK04 entries 27 and 28, using each established English move label.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
