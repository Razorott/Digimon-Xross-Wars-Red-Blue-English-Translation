"""Translate weapon and armor descriptions from MESPAK04 entries 30 and 31."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    30: {
        0: "An ordinary pair of gloves sold at the Penguinmon Shop.",
        1: "A fairly large hammer sold at the Penguinmon Shop.",
        2: "A giant hammer sold at the Penguinmon Shop.",
        3: "A small needle sold at the Penguinmon Shop.",
        4: "An ordinary needle sold at the Penguinmon Shop.",
        5: "A fairly large sword sold at the Penguinmon Shop.",
        6: "A giant sword sold at the Penguinmon Shop.",
        7: "A sword wrapped in weeds with a terrible edge.",
        8: "A red, spiked knuckle made in East Knuckle City.",
        9: "A blue, spiked knuckle made in West Knuckle City.",
        10: "A staff tipped with a skull, made in Skull City.",
        11: "A mushroom-shaped glove that scatters spores. Makes Paralysis and Poison easier to inflict.",
        12: "A stun gun that shocks foes. Makes Paralysis easier to inflict.",
        13: "A soft red glove that makes attacks more accurate.",
        14: "A gun that riddles foes with holes. Increases critical hit rate.",
        15: "A glove that makes Sleep easier to inflict. Improves accuracy.",
        16: "A huge mechanical gun that makes foes easier to Melodize.",
        17: "A long, slender hammer. Makes Confusion easier to inflict.",
        18: "A mechanical gun that makes Paralysis and Curse easier to inflict.",
        19: "A spiked iron ball on a hammer. Increases critical hit rate.",
        20: "A gun that makes Curse easier to inflict. Increases critical hit rate.",
        21: "A hammer that makes foes easier to Melodize. Improves accuracy.",
        22: "A bazooka that makes Confusion, Darkness, and MP Drain easier to inflict.",
        23: "A spear that makes Paralysis easier to inflict. Improves accuracy.",
        24: "A katana for a young chick Digimon. Increases critical hit rate.",
        26: "A katana that makes Confusion and Darkness easier to inflict.",
        27: "A staff that extends and retracts freely. Makes foes easier to Melodize.",
        28: "A katana engraved with cursed characters. Makes Curse easier to inflict.",
        29: "A spear for catching underwater prey. Increases critical hit rate.",
        30: "A sword that makes Confusion easier to inflict and increases MP Drain.",
        32: "A sacred, single-pronged vajra wielded by the gods. Makes foes easier to Melodize.",
        33: "A staff that increases critical hit rate and accuracy.",
        34: "Shuriken worn on both hands and feet. Makes Confusion easier to inflict.",
        35: "A club made from SkullGreymon's bones. Increases battle EXP.",
        36: "An axe that makes HP Drain easier to inflict and increases its amount.",
        37: "A sturdy steel mallet. Increases battle bit rewards.",
        38: "A sword that increases battle EXP and Melodize rate.",
        39: "A hammer that increases critical hit rate and Melodize rate.",
        40: "A gleaming white holy sword. Increases battle EXP.",
        41: "A giant sword that cuts foes in half. Makes foes easier to Melodize.",
        42: "A pair of shining swords. Increases critical hit rate.",
        43: "A giant morning star. Increases critical hit rate.",
        44: "A sword that makes Confusion easier to inflict and improves accuracy.",
        45: "A huge chunk of an ice pillar. Makes Curse easier to inflict.",
        46: "A sword that increases battle bit rewards. Escape Tactic always succeeds.",
        47: "An explosive greatsword of flame. Makes foes easier to Melodize.",
        48: "A staff that increases critical hit rate and makes Curse easier to inflict.",
        49: "A gun that makes Darkness easier to inflict and improves accuracy.",
    },
    31: {
        0: "A gun shaped like Garurumon. Makes Paralysis and Confusion easier to inflict.",
        1: "An arm-mounted energy cannon that improves accuracy.",
        2: "Giant claws worn on both arms. Increases critical hit rate.",
        3: "Claws that make Poison and Curse easier to inflict. Increases Poison damage.",
        5: "A spear that increases Poison damage and battle EXP.",
        6: "A katana that makes Confusion and Poison easier to inflict. Increases critical hit rate.",
        7: "A giant spear that makes Paralysis, Sleep, Confusion, and Poison easier to inflict.",
        9: "A greatsword that makes foes easier to Melodize. Improves accuracy.",
        10: "A shining holy spear. Increases critical hit rate.",
        11: "A bow that increases critical hit rate and accuracy.",
        12: "A sister gun to Berenjena. Increases battle EXP.",
        13: "A dagger that increases HP and MP Drain.",
        14: "A sword that improves accuracy and makes foes easier to Melodize.",
        15: "A sword that makes Darkness easier to inflict. Increases critical hit rate.",
        16: "A holy spear filled with focused energy. Increases battle EXP.",
        17: "A staff that makes Confusion and Poison easier to inflict. Increases battle bit rewards.",
        18: "A sword that makes foes easier to Melodize. Increases battle EXP.",
        19: "A spear that makes Poison easier to inflict and increases Poison damage and critical hit rate.",
        20: "A sword that makes foes easier to Melodize. Increases critical hit rate.",
        21: "A sword wreathed in blue flames. Raises Attack and Defense.",
        22: "An axe wreathed in dim light. Raises Attack and Defense.",
        23: "A glove brought back by a great explorer. Increases battle bit rewards.",
        24: "A sword only Phantom Beast Digimon can wield. Grants immunity to Curse.",
        25: "A hatchet only Beast Digimon can wield. Grants immunity to Darkness and Shuffle.",
        26: "A sacred implement only Angel Digimon can wield. Grants immunity to Confusion.",
        27: "A cannon only Demon Digimon can wield. Grants immunity to Curse.",
        28: "A spear only Aquatic Digimon can wield. Grants immunity to Shuffle.",
        29: "A spear only Machine Digimon can wield. Nullifies foes' Poison.",
        30: "A sword only Bird Digimon can wield. Grants immunity to Shuffle.",
        31: "A spear only Insect Digimon can wield. Nullifies foes' Poison.",
        32: "A whip only Plant Digimon can wield. Grants immunity to Paralysis.",
        33: "A legendary sword passed down in Elestou Zone.",
        34: "A small helmet sold at the Penguinmon Shop.",
        35: "An ordinary helmet sold at the Penguinmon Shop.",
        36: "A sturdy cloak sold at the Penguinmon Shop.",
        37: "A very durable cloak sold at the Penguinmon Shop.",
        38: "A small vest sold at the Penguinmon Shop.",
        39: "An ordinary vest sold at the Penguinmon Shop.",
        40: "A sturdy suit sold at the Penguinmon Shop.",
        41: "A very durable suit sold at the Penguinmon Shop.",
        42: "A rusty, battered shield that looks ready to break.",
        43: "A Roundabout City specialty: glasses that make you look studious.",
        44: "A Spider Nest City specialty: pants that sometimes turn transparent.",
        45: "A Papyrus City specialty: a T-shirt made from special paper.",
        46: "A flower-shaped helmet that helps prevent Paralysis.",
        47: "A headband that helps you dodge and improves Escape Tactic success.",
        48: "A tiara with bird feathers. Helps prevent Confusion and MP Drain.",
        49: "A scarf made of red cloth. Helps prevent Paralysis and Darkness.",
    },
}


def main() -> None:
    destination = ROOT / "translations/batch71.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for entry, descriptions in DESCRIPTIONS.items():
        for index, text in descriptions.items():
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
                "review_note": "Direct item-description translation. Status names and equipment effects follow the established battle glossary; city names match the map localization.",
            })
    if len(blocks) != 96:
        raise ValueError(f"Expected 96 descriptions, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate 96 weapon and armor descriptions in MESPAK04 entries 30 and 31.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
