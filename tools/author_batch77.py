"""Finish remaining DigiFarm, reward, map, key, and test-label descriptions."""
from __future__ import annotations

import json
import textwrap
import unicodedata

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


ENTRY40 = {
    0: "Memory recovered from Devimon. It contains important Terriermon data.",
    1: "DigiNoir for Leomon. Delicious, and it restores energy.",
    2: "A score entrusted to you by a stone monument Digimon. What it records is unknown.",
    3: "Mysterious data left behind by Kuramon. It might be someone's score.",
    4: "A passionate flower from Rosemon, often given with a proposal.",
    5: "A seductive flower from Lotusmon. Give it to make someone swoon.",
    9: "Proof that you defeated the powerful Aegisdramon: the mark of a kind gentleman.",
    10: "Proof that you defeated the powerful Apocalymon: the mark of a brave hero.",
    11: "Proof that you conquered the ultimate Colosseum: the mark of a legendary king.",
    23: "A map showing the areas of Sky Fort.",
    24: "A map showing the areas of Fort Yard.",
    25: "A map showing the areas of Knuckle Coast West.",
    26: "A map showing the areas of Knuckle Coast East.",
    27: "A map showing the areas of Guruguru Amazon West.",
    28: "A map showing the areas of Guruguru Amazon East.",
    29: "A map showing the areas of Digital Space East.",
    30: "A map showing the areas of Skull Glacier West.",
    31: "A map showing the areas of Skull Glacier East.",
    32: "A map showing the areas of Spider Ruins West.",
    33: "A map showing the areas of Spider Ruins East.",
    34: "A map showing the areas of Papyrus Desert North.",
    35: "A map showing the areas of Papyrus Desert South.",
    36: "A map showing the areas of Flower Plains.",
    37: "A map showing the areas of Dark Tunnel.",
    38: "A map showing the areas of Tokona Sea.",
    39: "A map showing the areas of Tokona Coast.",
    40: "A map showing the areas of Crystal Volcano West.",
    41: "A map showing the areas of Crystal Volcano East.",
    42: "A map showing the areas of Crystal Mine.",
    43: "A map showing the areas of Crystal Cave.",
    44: "A map showing the areas of Stealth Valley North.",
    45: "A map showing the areas of Stealth Valley South.",
    46: "A map showing the areas of Lost Space North.",
    47: "A map showing the areas of Lost Space South.",
    48: "A map showing the areas of Digital Space North.",
    49: "A map showing the areas of Digital Space South.",
}

ENTRY41 = {
    3: "A key that opens Skyport's gate in Sky Fort.",
    4: "A key that opens EK City Port's gate in Knuckle Coast East.",
    5: "A key that opens Guruguru West Port's gate in Guruguru Amazon West.",
    6: "A key that opens Guruguru City Port's gate in Guruguru Amazon East.",
    7: "A key that opens Skull City Port's gate in Skull Glacier West.",
    8: "A key that opens Skull East Port's gate in Skull Glacier East.",
    9: "A key that opens Spider West Port's gate in Spider Ruins West.",
    10: "A key that opens Spider City Port's gate in Spider Ruins East.",
    11: "A key that opens Papyrus North Port's gate in Papyrus Desert North.",
    12: "A key that opens Papyrus City Port's gate in Papyrus Desert South.",
    13: "A key that opens Flower Port's gate in Flower Plains.",
    14: "A key that opens Tokona Port's gate in Tokona Coast.",
    15: "A key that opens Earth Port's gate at Earth Fort in Crystal Volcano East.",
    16: "A key that opens Crystal Mine Port's gate in Crystal Mine.",
    17: "A key that opens Stealth North Port's gate in Stealth Valley North.",
    18: "A key that opens Lost North Port's gate in Lost Space North.",
    19: "A key that opens Lost South Port's gate in Lost Space South.",
    20: "A key that opens Digital North Port's gate in Digital Space North.",
    24: "A key that opens a gate in Guruguru Amazon West, Area 4.",
    25: "A key that opens a gate in Guruguru Amazon East, Area 2.",
    26: "A key that opens a gate in Spider Ruins West, Area 1.",
    27: "A key that opens a gate in Spider Ruins East, Area 3.",
    28: "A key that opens a gate in Knuckle Coast East, Area 3.",
}

TEST_TEXT = {
    "MSG/MESPAK04.PAK:000:00022": "Test Score 8\nDescription text.",
    "MSG/MESPAK04.PAK:000:00023": "Test Score 9\nDescription text.",
    "MSG/MESPAK04.PAK:000:00024": "Test Score 10\nDescription text.",
    "MSG/MESPAK04.PAK:000:00025": "Key Test\nDescription text.",
    "MSG/MESPAK04.PAK:003:00006": "Test Move 1\nPlaceholder text.",
    "MSG/MESPAK04.PAK:003:00007": "Test Move 2",
    "MSG/MESPAK04.PAK:003:00009": "Test Move 4\nPlaceholder text.",
    "MSG/MESPAK04.PAK:003:00010": "Test Move 5\nPlaceholder text.",
    "MSG/MESPAK04.PAK:003:00014": "Heavy Speaker\nPlaceholder text.",
    "MSG/MESPAK04.PAK:003:00017": "Shooting Me",
    "MSG/MESPAK04.PAK:003:00019": "Xros Four\nPlaceholder text.",
    "MSG/MESPAK04.PAK:012:00016": "Recover One Status\nPlaceholder text.",
    "MSG/MESPAK04.PAK:012:00017": "Recover Line Status\nPlaceholder text.",
    "MSG/MESPAK04.PAK:012:00018": "Revive\nPlaceholder text.",
    "MSG/MESPAK04.PAK:012:00019": "Multi-Status Disk\nPlaceholder text.",
}


def main() -> None:
    dest = ROOT / "translations/batch77.json"
    if dest.exists():
        raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    texts = {}
    for entry, mapping in ((40, ENTRY40), (41, ENTRY41)):
        for index, text in mapping.items():
            texts[f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"] = text
    for key, row in records.items():
        if row["archive"] != "MSG/MESPAK04.PAK" or row["entry"] not in (40, 41):
            continue
        if key in existing or key in texts:
            continue
        japanese = row["source"].split("<0A>", 1)[0]
        if not japanese.startswith("よびわく"):
            raise ValueError(f"Unclassified map or key description: {key}: {japanese}")
        digits = "".join(str(unicodedata.digit(c)) for c in japanese if c.isdigit())
        texts[key] = f"Unused slot {int(digits):03d}\nDescription text."
    texts.update(TEST_TEXT)
    blocks = []
    for key, text in texts.items():
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Move and item descriptions":
            raise ValueError(f"Unexpected translation category for {key}")
        lines = []
        for paragraph in text.splitlines():
            lines.extend(textwrap.wrap(paragraph, width=26, break_long_words=False,
                                       break_on_hyphens=False) or [""])
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Move and item descriptions",
            "english": ["\n".join(lines)],
            "sources": ["Original Japanese ROM", "Project area and item glossary"],
            "review_note": "Direct description translation. Canonical item, map, and character terms follow the existing project glossary; explicit test and unused strings remain clearly marked.",
        })
    if len(blocks) != 93:
        raise ValueError(f"Expected 93 description strings, got {len(blocks)}")
    dest.write_text(json.dumps({
        "description": "Finish the remaining map, key, quest reward, and test description strings in MESPAK04.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(dest), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
