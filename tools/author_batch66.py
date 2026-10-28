"""Translate battle-effect text from MESPAK04 entries 18 and 19."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    18: [
        "Dances up to a foe and drains its blood. Drains HP.",
        "Excrement\nPlaceholder text.",
        "Platinum Excrement\nPlaceholder text.",
        "Splatter Hunting\nPlaceholder text.",
        "Ogre Flame\nPlaceholder text.",
        "Cathedral\nPlaceholder text.",
        "Aura Dio Grandiorqua\nPlaceholder text.",
        "Sprinkles a foe with shining, sweet powder.",
        "Pokes a foe with something like a tiny thorn.",
        "Hits a foe with a fireball using ninjutsu.",
        "Shoots a foe with a water gun using ninjutsu.",
        "Blows a gust of wind at a foe using ninjutsu.",
        "Releases electricity at a foe using ninjutsu.",
        "Plays a hot rhythm to raise one ally's Attack.",
        "Fires a rapid barrage of light waves at a foe.",
        "Swings a shining drumstick to strike a foe repeatedly.",
        "Blasts a foe with the shock wave of a huge explosion.",
        "Explodes and scatters particles over nearby foes.",
        "Hits a foe with a plasma ball. Lowers Defense.",
        "Shoots compressed light at a foe.",
        "Turns the air into plasma and fires it at nearby foes.",
        "Slices a foe with a blow strong enough to shake the earth.",
        "Buries a foe with a blow powerful enough to wake the dead.",
        "Collapses the ground beneath nearby foes and slices them.",
        "Cuts a foe in half with power enough to destroy a star.",
        "Fires a crystal at a foe with a punch.",
        "Curls up and rolls over nearby foes. May cause instant death.",
        "Reflects light to blind nearby foes. Lowers Speed.",
        "Breathes solar lasers on nearby foes. May cause Darkness.",
        "Slashes a foe with claws that rot whatever they touch.",
        "Rams a foe with its spiny body.",
        "Explodes and engulfs nearby foes.",
        "Rains blades from its back on a foe. Deals Fighting damage.",
        "Hits a foe with dark red bubbles from its eyes. May cause Confusion.",
        "Raises its Defense with a shining light barrier.",
        "Charges and punches a foe with powerful claws. Lowers Attack.",
        "Blasts nearby foes with the flames it inhaled. Dramatically boosts Melodize rate.",
        "Punches a foe with a shining fist of victory.",
        "Slashes a foe with hot, powerful claws. Lowers Speed.",
        "Spits an iron ball at a foe.",
        "Sends high-voltage electricity through nearby foes.",
        "Spits a small fireball at a foe.",
        "Spits a ball of light at a foe. May cause Paralysis.",
        "Pokes a foe with a dazzling illusion. May cause Confusion.",
        "Fires strange energy at a foe. Drains HP.",
        "Slashes a foe with hard claws.",
        "Raises the ground to strike nearby foes. Lowers Speed.",
        "Sprays water stored in its mouth at a foe.",
        "Commands small fish to attack nearby foes.",
        "Sends a swarm of bats to attack a foe. Drains MP.",
    ],
    19: [
        "Blows up nearby foes with toy missiles.",
        "Plants virus gears inside a foe. May cause Darkness.",
        "Destroys a foe with a holy, high-pitched cry. May cause Paralysis.",
        "Spits thread like electrified needles. May cause Paralysis.",
        "Pecks a foe fiercely like a woodpecker. Lowers Attack.",
        "Curls up and charges into nearby foes. Lowers Attack.",
        "Spits a ball of hot air at a foe.",
        "Spits a ball of cold air at a foe.",
        "Unleashes powerful punches on nearby foes.",
        "Summons dark ice to strike nearby foes. Lowers Wisdom.",
        "Spits poisonous mist at nearby foes. May cause Poison.",
        "Quickly scratches nearby foes with its wing claws.",
        "Throws giant fireballs at nearby foes.",
        "Fires a hard, black ball at a foe.",
        "Scatters allergenic pollen on nearby foes. May cause Confusion.",
        "Fires a hard nut from its mouth. Deals Light damage.",
        "Leaps into a foe's guard and lands an uppercut. May cause Paralysis.",
        "Rams into a foe with a holy spin.",
        "Charges into nearby foes with its helmet.",
        "Destroys nearby foes with both evil eyes. May cause Paralysis.",
        "Charges straight at a foe with its shield. May cause Paralysis.",
        "Throws a poisonous mushroom bomb at a foe.",
        "Discharges the electricity stored in its pincers. May cause Paralysis.",
        "Punches a foe with a fist heated by Fire energy.",
        "Focuses its power and fires a water ball at a foe. May cause Sleep.",
        "Slashes a foe with a holy katana that chirps. May cause Darkness.",
        "Tackles a foe with its bouncy body.",
        "Fires a small ice arrow at a foe.",
        "Pierces a foe with a holy spear that explodes on contact.",
        "Throws Thor's Hammer at nearby foes.",
        "Punches a foe repeatedly with its big ears. Deals Fighting damage.",
        "Fires ultra-high-pressure water bubbles at nearby foes.",
        "Shoots a foe with a water-powered homing arrow.",
        "Spins and pummels a foe.",
        "Dives down from above and charges at a foe.",
        "Slashes nearby foes repeatedly at light speed. May cause Confusion.",
        "Throws its shining crest at a foe like a boomerang.",
        "Fires a fierce wave of flames at nearby foes. Lowers Speed.",
        "Rips a foe apart with claws made of digital data.",
        "Swallows nearby foes in a black hole between its pincers. May cause Darkness.",
        "Punches a foe with an exploding fist. Deals Fire damage.",
        "Fires machine guns on both arms at nearby foes.",
        "Slashes a foe with electrified steel claws. Lowers Defense.",
        "Calls a thundercloud to strike nearby foes. Deals Light damage.",
        "Fires electricity gathered from nature at nearby foes.",
        "Cuts a foe in half with giant scissors. May cause Paralysis.",
        "Fires a powerful plasma cannon at a foe. Lowers Defense.",
        "Fires scorching arrows from the jewels in both hands. Slightly boosts Melodize rate.",
        "Cuts a foe in half with a holy blade.",
        "Smashes a bean-shaped iron ball into a foe.",
    ],
}


def main() -> None:
    destination = ROOT / "translations/batch66.json"
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
                "english": ["\n".join(lines)], "sources": ["Original Japanese ROM"],
                "review_note": "Direct translation of the original battle-effect text. Established Xros Wars terms and status names are retained.",
            })
    if sum(map(len, DESCRIPTIONS.values())) != 100:
        raise ValueError("Expected exactly 100 translated descriptions")
    destination.write_text(json.dumps({
        "description": "Translate 100 additional battle-effect descriptions from MESPAK04 entries 18 and 19.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
