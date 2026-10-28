"""Translate the remaining battle-effect text in MESPAK04 entries 16 and 17."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    16: [
        "Cuts a foe in half with a chainsaw.",
        "Hurls a powerful hand grenade at a foe. May cause instant death.",
        "Burns away a foe with a blast of flame.",
        "Fires a large fireball at nearby foes.",
        "Slashes a foe with a giant sword. May cause Darkness.",
        "Splits the earth with a holy sword, destroying nearby foes.",
        "Uses a magic staff to confuse a foe.",
        "Fires a giant electric beam at a foe.",
        "Erases a foe with a magic circle of light.",
        "Stands its ground and sweeps away nearby foes.",
        "Shoots a foe with an arm-mounted Gatling gun. Deals Fire damage.",
        "Drives a flaming fist into a foe. Greatly boosts Melodize rate.",
        "Turns its whole body into a fiery rocket and crushes a foe. Lowers Defense.",
        "Delivers a powerful slap to nearby foes.",
        "Strikes nearby foes with the holy weapon Vajra. Lowers Wisdom.",
        "Knocks nearby foes into the gates of Hell. Deals Fire damage.",
        "Burns away a foe with searing flames. Deals Fire damage.",
        "Fires icy flames at a foe. Greatly boosts Melodize rate.",
        "Fires ice packed with cold flames at a foe. Dramatically boosts Melodize rate.",
        "Spreads poisonous mist that blinds nearby foes.",
        "Stabs a foe with the deadly poison needle on its tail. Deals Poison damage.",
        "Throws a shining jewel at a foe. May cause Sleep.",
        "Summons a holy monument that strikes nearby foes.",
        "Destroys nearby foes with a red beam. May cause instant death.",
        "Punches a foe with a metallic fist.",
        "Makes a foe slip on a banana peel. May cause Confusion.",
        "Bites a foe repeatedly with sharp teeth. Lowers Speed.",
        "Destroys nearby foes with a wave of light. Lowers Speed.",
        "Fires a barrage of grenades at nearby foes.",
        "Blasts a foe with a cannon.",
        "Buries a foe with a majestic song. May cause Sleep.",
        "Makes nearby foes hear a mournful cry. Deals Electric damage.",
        "Charges a foe and impales it with its whole body. May cause Paralysis.",
        "Spins a bone from its dorsal fin and hurls it at a foe. May cause Paralysis.",
        "Rallies its spirit to raise one ally's Attack.",
        "Smashes a foe with the Queen Stick. May cause Confusion.",
        "Pierces the hearts of nearby foes with a mechanical sword.",
        "Dashes again to raise its Speed.",
        "Orders a shadow clone to shock a foe. May cause Confusion.",
        "Reluctantly strikes nearby foes with electricity. May cause instant death.",
        "Hits a foe with ice coated in red syrup. May cause Paralysis.",
        "Hits a foe with ice coated in blue syrup.",
        "Rips through a foe's armor with mechanical claws.",
        "Breaks down nearby foes with an energy wave. Deals Electric damage.",
        "Hits a foe with a shocking feeling in its heart. May cause Confusion.",
        "Throws balls of fire at nearby foes.",
        "Swings a microphone and smashes a foe.",
        "Destroys a foe with powerful arms.",
        "Uses speakers to blast nearby foes with sound waves.",
        "Uses its horn to hurl a foe away. Deals Electric damage.",
    ],
    17: [
        "Drills into a foe with its spinning head drill.",
        "Blows away nearby foes with a drill-made tornado. Lowers Defense.",
        "Rides its drill into a spinning charge. Lowers Speed.",
        "Charges into a foe with a thunderous roar and a flash of light.",
        "Slices a foe with its wings of light as it rushes past.",
        "Fires a barrage of plasma lasers at a foe. Deals Electric damage.",
        "Throws a shining, star-shaped boomerang at a foe.",
        "Blinds a foe with a Pickmon squad. Lowers Speed.",
        "Compresses all its energy and explodes. Lowers Speed.",
        "Fires a Vulcan cannon at a foe at incredible speed.",
        "Rushes in while hovering and knocks a foe away.",
        "Fires light energy at a foe. Deals Electric damage.",
        "Carves up a foe with a burning blade.",
        "Punches a foe with a spirited blow.",
        "Slashes nearby foes with a flaming V-shaped boomerang.",
        "Cuts a foe in two with a flaming Star Sword. Deals Fire damage.",
        "Slams its hot tail into nearby foes.",
        "Lowers its stance and charges at a foe. May cause Paralysis.",
        "Sweeps away a foe with its superheated tail.",
        "Sneaks up on a foe and blasts it with light.",
        "Spits a high-energy plasma ball at a foe.",
        "Destroys a foe with its superheated claws.",
        "Paralyzes nearby foes with the eye on its chest. Lowers Defense.",
        "Leaps into a foe's guard and unleashes a dark punch. May cause instant death.",
        "Spits powerful, toxic liquid at a foe. May cause Poison.",
        "Dashes between foes and slashes them.",
        "Slices a foe with the axe slung over its shoulder.",
        "Revives the power of the dead. Raises its Defense and Attack.",
        "Stands before a foe and delivers a cruel thrust.",
        "Heals one ally's Health Down by laying hands on its wounds.",
        "Unleashes a wave of light on nearby foes. Deals Light damage.",
        "Heals one ally by laying hands on its wounds.",
        "Pins a foe in exchange for a wish. May cause Darkness.",
        "Fires a dark beam from a giant gun. Deals Dark damage.",
        "Destroys a foe with a high-powered heat ray.",
        "Slams heat energy into nearby foes.",
        "Becomes a shining meteor and crashes into nearby foes.",
        "Fires an ultra-powerful dark beam at a foe. Deals Fire damage.",
        "Tears through a foe with a light bullet. Deals Dark damage.",
        "Rakes a foe with claws steeped in deadly poison. May cause Poison.",
        "Fires dark energy shaped like a lion's head. Deals Dark damage.",
        "Strikes a foe with a powerful headbutt.",
        "Scorches a foe with a moderately hot flamethrower.",
        "Blows mist at nearby foes to blind them. Lowers Speed.",
        "Charges into a foe without fear of death.",
        "Breathes scorching air on nearby foes.",
        "The Shulnen\nPlaceholder text.",
        "Eucalyptus Claw\nPlaceholder text.",
        "Evil Snore\nPlaceholder text.",
        "Confuses nearby foes with the Berry Dance. Lowers Wisdom.",
    ],
}


def main() -> None:
    destination = ROOT / "translations/batch65.json"
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
        "description": "Translate 100 additional battle-effect descriptions from MESPAK04 entries 16 and 17.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
