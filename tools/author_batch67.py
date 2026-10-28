"""Translate battle-effect text from MESPAK04 entries 20 through 23."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from xros_text import ROOT, Rom, rom_paths


TRANSLATIONS = {
    20: {
        0: "An electrifying wave destroys nearby foes. May cause Paralysis.",
        1: "Rakes a foe with claws sharp as a falcon's.",
        2: "Fires a fireball at a foe using power focused in its head.",
        3: "Slips into a foe's guard and lands an uppercut.",
        4: "Sweeps away nearby foes like a wild beast.",
        5: "Charges a foe with its limbs tucked away in a cocoon.",
        6: "Creates a tsunami that freezes nearby foes. May cause Paralysis.",
        7: "Traps a foe in a strange web. May cause Sleep.",
        8: "Buries nearby foes with a bewitching kiss of darkness. May cause Paralysis.",
        9: "Merges with nearby foes' shadows to immobilize them. Lowers Speed.",
        10: "Draws its demon sword and slashes a foe with a cross cut. Deals Dark damage.",
        11: "Smears a foe with a filthy liquid kick. May cause Confusion.",
        12: "Buries a foe in a golden radiance.",
        13: "Fires a shower of tiny needles at a foe.",
        14: "Spits blue flames at a foe.",
        15: "Fires Vulcan cannons from both hands at nearby foes.",
        16: "Fires a legendary sphere of energy at a foe.",
        17: "Slashes nearby foes with holy blades on both ears.",
        18: "Makes a hard nut explode among nearby foes. Deals Fire damage.",
        20: "Turns its body into a mallet and delivers holy judgment. May cause instant death.",
        21: "Slams its body down and causes a great earthquake around it.",
        22: "Breathes out searing flames to burn nearby foes.",
        23: "Blinds nearby foes with light from its earrings. Lowers Wisdom.",
        24: "Jabs a foe at Mach speed. Deals Fighting damage.",
        25: "Charges and crushes a foe with its giant horn. May cause Paralysis.",
        26: "Glares at a foe with red eyes and stops it in its tracks.",
        27: "Bombards a foe with torpedo-shaped missiles. Deals Fire damage.",
        28: "Charges at a foe with its fangs ready. Slightly boosts Melodize rate.",
        29: "Moves at light speed to raise its Speed.",
        30: "Blasts a foe with an electric cannon. Lowers Speed.",
        31: "Hurls a summoned meteor at a foe. Lowers Defense.",
        32: "Slams its many wet tentacles into nearby foes. Lowers Defense.",
        33: "Creates a freezing blizzard that freezes a foe.",
        34: "Hunches its back like a mountain to raise one ally's Defense and Attack.",
        35: "Fires a ball of searing magma at a foe.",
        36: "Blows up nearby foes with torpedo-shaped missiles.",
        37: "Blasts a foe with a high-density energy cannon.",
        38: "Charges at a foe at full speed. May cause Paralysis.",
        39: "Buries nearby foes with a bewitching breath of darkness. May cause instant death.",
        40: "Drives away nearby foes with holy light. Deals Water damage.",
        41: "Smashes nearby foes with a holy, lightning-fast flurry of blows.",
        42: "Pierces a foe with the holy sword Blutgang.",
        43: "Fires a devastating sword of light at a foe. Deals Dark damage.",
        44: "Slashes a foe with a crescent-shaped energy naginata.",
        45: "Makes a rain of fiery meteors fall on nearby foes.",
        46: "Explodes nearby foes with energy drawn from the atmosphere.",
        47: "Grabs a fireball and punches a foe with it.",
        48: "Freezes moisture in the air and hurls it at a foe.",
        49: "Pierces a foe with a sharp kick like a bolt of lightning.",
    },
    21: {
        0: "Unleashes sacred light to destroy a foe.",
        1: "Strikes a foe from the shadows before it can react.",
        2: "Slams a foe with a battle martial-arts move.",
        3: "Punches a foe with a flaming fist.",
        4: "Punches a foe with a fist of ice.",
        5: "Punches a foe with an electrified fist.",
        6: "Punches a foe with a fist of light.",
        7: "Punches a foe with a fist of darkness.",
        8: "Punches a foe with a tightly clenched fist.",
        9: "Breathes hot air on nearby foes.",
        10: "Breathes a blizzard on nearby foes.",
        11: "Breathes lightning on nearby foes.",
        12: "Breathes shining light on nearby foes.",
        13: "Breathes a thick, black cloud on nearby foes.",
        14: "Blasts nearby foes with a powerful shock wave.",
        15: "Spits a small lump of fire at a foe. Slightly boosts Melodize rate.",
        16: "Spits a lump of fire at a foe. Slightly boosts Melodize rate.",
        17: "Spits a large lump of fire at a foe. Slightly boosts Melodize rate.",
        18: "Spits a giant lump of fire at a foe. Slightly boosts Melodize rate.",
        19: "Spits a huge lump of fire at a foe. Slightly boosts Melodize rate.",
        20: "Throws a small piece of ice at a foe. Slightly boosts Melodize rate.",
        21: "Throws a piece of ice at a foe. Slightly boosts Melodize rate.",
        22: "Throws a large piece of ice at a foe. Slightly boosts Melodize rate.",
        23: "Throws a giant piece of ice at a foe. Slightly boosts Melodize rate.",
        24: "Throws a huge piece of ice at a foe. Slightly boosts Melodize rate.",
        25: "Sends a light electric shock through a foe. Slightly boosts Melodize rate.",
        26: "Sends an electric shock through a foe. Slightly boosts Melodize rate.",
        27: "Sends a strong electric shock through a foe. Slightly boosts Melodize rate.",
        28: "Sends a powerful electric shock through a foe. Slightly boosts Melodize rate.",
        29: "Sends an ultra-powerful electric shock through a foe. Slightly boosts Melodize rate.",
        30: "Destroys a foe with a faint flash. Slightly boosts Melodize rate.",
        31: "Destroys a foe with a flash. Slightly boosts Melodize rate.",
        32: "Destroys a foe with a strong flash. Slightly boosts Melodize rate.",
        33: "Destroys a foe with a powerful flash. Slightly boosts Melodize rate.",
        34: "Destroys a foe with an ultra-powerful flash. Slightly boosts Melodize rate.",
        35: "Buries a foe with a weak blast of dark energy. Slightly boosts Melodize rate.",
        36: "Buries a foe with a blast of dark energy. Slightly boosts Melodize rate.",
        37: "Buries a foe with a strong blast of dark energy. Slightly boosts Melodize rate.",
        38: "Buries a foe with a powerful blast of dark energy. Slightly boosts Melodize rate.",
        39: "Buries a foe with an ultra-powerful blast of dark energy. Slightly boosts Melodize rate.",
        40: "Hits a foe with a light blow. Slightly boosts Melodize rate.",
        41: "Hits a foe with a blow. Slightly boosts Melodize rate.",
        42: "Quickly hits a foe with a strong blow. Slightly boosts Melodize rate.",
        43: "Quickly hits a foe with a powerful blow. Slightly boosts Melodize rate.",
        44: "Quickly hits a foe with an ultra-powerful blow. Slightly boosts Melodize rate.",
        45: "Uses the power of the sun to restore allies' HP.",
        46: "Uses a goddess's power to restore one ally's HP.",
        47: "Slaps a foe hard with wet wings. Deals Water damage.",
        48: "Uses heavenly light to heal an ally's Health Down and restore HP.",
    },
    22: {
        2: "Uses a wave to heal one ally's Health Down.",
        3: "Drags nearby foes underwater and swallows them.",
        4: "Fires two sharp, red shock waves at a foe. Deals Fighting damage.",
        5: "Undecided 00\nPlaceholder description.",
        6: "Undecided 01\nPlaceholder description.",
        7: "King of Locker\nPlaceholder text.",
        8: "Undecided 02\nPlaceholder description.",
        9: "Undecided 03\nPlaceholder description.",
        10: "Soul Majesty\nPlaceholder text.",
        11: "Restores an ally's HP with sweet sugar.",
        12: "Turns its shining aura into a blade and slashes a foe.",
        13: "Destroys nearby foes with a special wave. May cause Paralysis.",
        14: "Undecided 06\nPlaceholder description.",
        15: "Undecided 07\nPlaceholder description.",
        16: "Azure Flame\nPlaceholder text.",
        17: "Undecided 08\nPlaceholder description.",
        18: "Undecided 09\nPlaceholder description.",
        19: "Twilight Dance\nPlaceholder text.",
        20: "Throws a giant fireball at a foe.",
        21: "Amplifies light with a microphone and blasts nearby foes.",
        22: "Swings its microphone wildly and smashes nearby foes.",
        23: "Burns nearby foes with a super flamethrower.",
        24: "Slams its hot tail into nearby foes with all its strength.",
        25: "Crouches, builds up speed, and charges at a foe.",
        26: "Savagely attacks a foe like a starving beast.",
        27: "Lulls nearby foes to sleep with a hypnotic wave. Lowers Speed.",
        28: "Turns its spear into a drill and mercilessly pierces a foe. Deals Dark damage.",
        29: "Leaps into a fireball and charges at a foe.",
        30: "Releases wings of light to slash a foe.",
        31: "Bombards nearby foes with a plasma breath.",
        32: "Sweeps away foes with the Victory Spear.",
        33: "Dissolves a foe in an acidic storm. May cause Darkness.",
        34: "Pierces a foe repeatedly. Deals Dark damage.",
        35: "Blows up a foe with an aurora-wrapped projectile. May cause Paralysis.",
        36: "Fires a holy, slashing shock wave at a foe.",
        37: "Slashes nearby foes with a blade of blue aura. Deals Fire damage.",
        38: "Engulfs nearby foes in a giant tornado of fire.",
        39: "Fires dark energy from a giant cannon at nearby foes.",
        40: "Charges at a foe with a giant drill lance. Deals Fighting damage.",
        41: "Slashes a foe with a wave of light.",
        42: "Slashes nearby foes with solar energy.",
        43: "Smashes nearby foes with cosmic energy. Deals Fire damage.",
        44: "Undecided 29\nPlaceholder description.",
        45: "Undecided 30\nPlaceholder description.",
        46: "Undecided 31\nPlaceholder description.",
        47: "Undecided 32\nPlaceholder description.",
        48: "Undecided 33\nPlaceholder description.",
        49: "Undecided 34\nPlaceholder description.",
    },
    23: {11: "Destroys a foe with giant mechanical claws. Deals Electric damage."},
}


def main() -> None:
    destination = ROOT / "translations/batch67.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for entry, descriptions in TRANSLATIONS.items():
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
                "english": ["\n".join(lines)], "sources": ["Original Japanese ROM"],
                "review_note": "Direct translation of the original battle-effect text. Existing move labels were checked against the game's technique index and prior Western Digimon game terms where applicable.",
            })
    destination.write_text(json.dumps({
        "description": "Translate the remaining combat-effect descriptions in MESPAK04 entries 20 through 23.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
