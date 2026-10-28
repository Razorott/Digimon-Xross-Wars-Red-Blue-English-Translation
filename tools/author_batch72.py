"""Translate armor, accessory, and DigiFarm training descriptions."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    32: [
        "An umbrella that helps you dodge and increases battle bit rewards.",
        "A Western-style red scarf. Helps prevent Poison.",
        "A pirate's favorite hat. Helps prevent Paralysis and Darkness.",
        "A cloak for a magician's apprentice. Helps prevent Confusion and Darkness.",
        "A helmet with a topknot. Helps prevent Sleep.",
        "A red scarf favored by black-and-white beasts. Helps prevent HP and MP Drain.",
        "A tiny, very hard helmet. Helps prevent Curse.",
        "A cloak that helps you dodge and prevents HP Drain and Poison.",
        "A vest often worn by Goburimon. Improves Escape Tactic success.",
        "A shield like a small turtle shell. Helps prevent Sleep.",
        "A suit made from an eggshell. Helps prevent Paralysis.",
        "A shield made from a giant clam shell. Helps prevent Confusion.",
        "A powered suit large enough for a Digimon to climb inside. Helps prevent Paralysis and Poison.",
        "A plate that helps prevent Confusion and makes attacks easier to dodge.",
        "Armor made from steel scales. Helps prevent Paralysis and Darkness.",
        "A shield shaped like a fox mask. Helps you dodge attacks.",
        "A monkey-shaped suit that helps prevent Confusion and improves Escape Tactic success.",
        "A shining shield of holy energy. Helps prevent Darkness and Shuffle.",
        "A suit that helps prevent Sleep and makes attacks easier to dodge.",
        "A plate that helps prevent Paralysis and improves Escape Tactic success.",
        "Earrings that help prevent Shuffle. Increase battle EXP.",
        "A mask that helps prevent Shuffle and improves Escape Tactic success.",
        "Sunglasses that block Shuffle and make foes easier to Melodize.",
        "A mask that helps prevent Shuffle. Increases battle EXP.",
        "Denim pants that block Shuffle and make attacks easier to dodge.",
        "A cute dragon costume. Helps prevent Shuffle and Curse.",
        "A veil that helps prevent Shuffle and increases battle bit rewards.",
        "An insect-like mask. Helps prevent Paralysis, Shuffle, and Poison.",
        "A bean-sized, very hard helmet. Helps prevent HP Drain.",
        "A helmet with a giant eyeball. Helps prevent Darkness and Curse.",
        "A lightweight blue cloak that helps you dodge attacks.",
        "A gorgeous gold crown. Increases battle bit rewards.",
        "A jacket that helps you dodge. Escape Tactic always succeeds.",
        "A Justice Scarf that helps prevent Darkness and blocks Curse.",
        "A helmet made in Area 51. Helps prevent Paralysis, Confusion, and Darkness.",
        "A helmet made from Kuramon data. Nullifies foes' Poison.",
        "A robe that helps prevent Darkness and Poison and blocks Confusion.",
        "Armor worn by an Eastern dragon. Helps you dodge attacks.",
        "Armor that blocks Paralysis and helps prevent Confusion, HP Drain, and Poison.",
        "A shield that helps prevent Darkness and Poison and blocks Curse.",
        "Armor that helps prevent Darkness and Shuffle and makes attacks easier to dodge.",
        "A suit that helps prevent Darkness and Poison and makes attacks easier to dodge.",
        "Wings that help prevent Curse and make attacks easier to dodge.",
        "A plate that helps prevent Paralysis, Confusion, and Darkness and makes attacks easier to dodge.",
        "A shield that helps prevent Curse and makes foes easier to Melodize.",
        "Gallantmon's sacred shield. Blocks Curse.",
        "A scarf that helps prevent Shuffle. Increases battle EXP.",
        "A headband that increases battle bit rewards and helps prevent MP Drain and Shuffle.",
        "A mask that helps prevent Shuffle and makes attacks easier to dodge.",
        "A mask that helps prevent Shuffle and Poison and makes attacks easier to dodge.",
    ],
    33: [
        "A hairpin that helps prevent Shuffle and increases battle bit rewards.",
        "A mask that helps you dodge attacks and blocks Sleep.",
        "A shield that raises Attack and Defense and helps prevent Shuffle.",
        "A dark chain that wards off everything. Helps prevent Shuffle and Poison.",
        "A motorcycle that blocks Shuffle. Escape Tactic always succeeds.",
        "A ring that draws out holy power. Blocks Health Down and Shuffle.",
        "A bracelet that can produce swords and shields. Raises Attack and Defense.",
        "A tiny pair of earrings made by Calumon. Raises Attack and Defense.",
        "A bracelet brought back by a great explorer. Raises Attack and Defense.",
        "A shield only Phantom Beast Digimon can equip. Helps prevent Darkness.",
        "A jacket only Beast Digimon can equip. Makes foes easier to Melodize.",
        "A shield only Angel Digimon can equip. Makes Paralysis easier to inflict.",
        "A box only Demon Digimon can equip. Makes Confusion easier to inflict.",
        "Armor only Aquatic Digimon can equip. Helps you dodge attacks.",
        "A shield only Machine Digimon can equip. Improves accuracy.",
        "An aura only Bird Digimon can equip. Makes Curse easier to inflict.",
        "Armor only Insect Digimon can equip. Makes Poison easier to inflict.",
        "A gem only Plant Digimon can equip. Makes HP Drain easier to inflict.",
        "A legendary shield passed down in Elestou Zone.",
        "Training slightly raises a Digimon's maximum HP.",
        "Training moderately raises a Digimon's maximum HP.",
        "Training greatly raises a Digimon's maximum HP.",
        "Training slightly raises a Digimon's maximum MP.",
        "Training moderately raises a Digimon's maximum MP.",
        "Training greatly raises a Digimon's maximum MP.",
        "Training slightly raises a Digimon's Attack.",
        "Training moderately raises a Digimon's Attack.",
        "Training greatly raises a Digimon's Attack.",
        "Training slightly raises a Digimon's Defense.",
        "Training moderately raises a Digimon's Defense.",
        "Training greatly raises a Digimon's Defense.",
        "Training slightly raises a Digimon's Speed.",
        "Training moderately raises a Digimon's Speed.",
        "Training greatly raises a Digimon's Speed.",
        "Training slightly raises a Digimon's Wisdom.",
        "Training moderately raises a Digimon's Wisdom.",
        "Training greatly raises a Digimon's Wisdom.",
        "Slightly raises DigiFarm EXP. Phantom Beast Digimon gain more.",
        "Moderately raises DigiFarm EXP. Phantom Beast Digimon gain more.",
        "Greatly raises DigiFarm EXP. Phantom Beast Digimon gain more.",
        "Slightly raises DigiFarm EXP. Beast Digimon gain more.",
        "Moderately raises DigiFarm EXP. Beast Digimon gain more.",
        "Greatly raises DigiFarm EXP. Beast Digimon gain more.",
        "Slightly raises DigiFarm EXP. Angel Digimon gain more.",
        "Moderately raises DigiFarm EXP. Angel Digimon gain more.",
        "Greatly raises DigiFarm EXP. Angel Digimon gain more.",
        "Slightly raises DigiFarm EXP. Demon Digimon gain more.",
        "Moderately raises DigiFarm EXP. Demon Digimon gain more.",
        "Greatly raises DigiFarm EXP. Demon Digimon gain more.",
        "Slightly raises DigiFarm EXP. Machine Digimon gain more.",
    ],
}


def main() -> None:
    destination = ROOT / "translations/batch72.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for entry, descriptions in DESCRIPTIONS.items():
        for index, text in enumerate(descriptions):
            key = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
            if key not in records or key in existing:
                raise ValueError(f"Missing or already translated source: {key}")
            row = records[key]
            lines = []
            for source_line in text.splitlines():
                lines.extend(textwrap.wrap(source_line, width=26, break_long_words=False,
                                           break_on_hyphens=False) or [""])
            blocks.append({
                "archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": "Move and item descriptions",
                "english": ["\n".join(lines)],
                "sources": ["Original Japanese ROM"],
                "review_note": "Direct equipment and DigiFarm description translation. Status effects, stats, city names, and western Digimon names follow the established project glossary.",
            })
    if len(blocks) != 100:
        raise ValueError(f"Expected 100 descriptions, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate armor and accessory descriptions plus DigiFarm training effects in MESPAK04 entries 32 and 33.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
