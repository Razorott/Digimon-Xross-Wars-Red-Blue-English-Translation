"""Translate the next 100 combat-effect descriptions from the Japanese ROM."""
from __future__ import annotations

import json
import textwrap

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DESCRIPTIONS = {
    14: [
        "Pummels a foe with light that shakes the stars.",
        "Strikes a foe with a bloodstained dark whip. Drains HP.",
        "Kicks a foe at incredible speed.",
        "Cures one ally's Health Down and restores HP.",
        "Envelops nearby foes in dark matter. Deals Poison damage.",
        "Wraps a foe in bubbles. May cause Sleep.",
        "Envelops nearby foes in bubbles. May suffocate them and cause Sleep.",
        "Bites a foe with jaws made of ice.",
        "Fires icicles at a foe. Lowers Defense.",
        "Raises its Defense with a hard shell.",
        "Cuts a foe in half with giant scissors. Deals Water damage.",
        "Pierces a foe with an electric spear.",
        "Uses a special formation to raise allies' Defense.",
        "Destroys a foe with a small mushroom bomb. Deals Poison damage.",
        "Throws mushroom bombs at nearby foes. May cause Confusion.",
        "Boosts allies' abilities with heavenly light. Raises Speed and Attack.",
        "Shocks a foe with a Linear Lens beam. Lowers Speed.",
        "Punches a foe with a megawatt corkscrew punch.",
        "Blasts nearby foes with a foul stench. May cause Paralysis.",
        "Blows sweet breath at nearby foes. Lowers Speed.",
        "Hurls poop at a foe at incredible speed. Deals Dark damage.",
        "Hurls a mountain of poop at nearby foes. May cause Confusion.",
        "Destroys a foe from within with high-frequency waves. Lowers Defense.",
        "Shatters a foe's hearing with a mighty cry. May cause Confusion.",
        "Lulls nearby foes to sleep with a beautiful, gentle song.",
        "Turns sunlight into arrows that rain on foes. Lowers Wisdom.",
        "Purifies nearby evil with a light ward. Raises allies' Defense and Wisdom.",
        "Fires nightmare-inducing sound waves at a foe. May cause Paralysis.",
        "Torments a foe with high-frequency sound waves.",
        "Fires light-charged feathers at nearby foes.",
        "Strikes a foe with a flexible battle rod.",
        "Charges into a foe with its glowing green horn.",
        "Fires light energy from its horn. Lowers Defense.",
        "Creates a massive earthquake that destroys nearby foes.",
        "Crushes a foe with its left-hand Demon Arm.",
        "Charges and knocks back nearby foes. Lowers Attack.",
        "Destroys nearby foes with a giant roar. May cause Paralysis.",
        "Pierces a foe with a giant drill.",
        "Throws a bone stolen from Garurumon at a foe.",
        "Punches a foe with spinning drills on both hands.",
        "Coats itself in mud to raise its Defense.",
        "Hits a foe with a full-body Heavy Punch. May cause Paralysis.",
        "Purifies nearby foes with the power of the earth. May cause Paralysis.",
        "Blasts nearby foes with dark matter breath. Lowers Defense.",
        "Strikes a foe with two cold tentacles. Deals Fighting damage.",
        "Spins its hard shell and rams a foe.",
        "Hides inside its hard shell. Raises Defense and Wisdom.",
        "Fires highly compressed water from its head. May cause Paralysis.",
        "Stabs a foe with its claws and freezes them. May cause Paralysis.",
        "Freezes a foe with a blast of cold light.",
    ],
    15: [
        "Fires icy arrows from its wings at nearby foes.",
        "Fires an ultra-high-frequency wave from its mouth.",
        "Strikes a foe with its tail like a kick. Lowers Defense.",
        "Rends a foe with sharp scythes in both hands.",
        "Slashes nearby foes with electric scythes.",
        "Rends a foe with electrified claws. May cause Paralysis.",
        "Pierces a foe with its tail's sharp needle. Deals Poison damage.",
        "Swarm of beetles blocks nearby foes' vision. Lowers Attack.",
        "Shocks nearby foes with lightning. Lowers Speed.",
        "Shocks nearby foes with an electric blast.",
        "Charges through nearby foes while discharging electricity. May cause Paralysis.",
        "Hits a foe with a heavyweight punch. Lowers Speed.",
        "Scorches a foe with superheated gas. Deals Poison damage.",
        "Fires a ball of flame energy at a foe. Lowers Defense.",
        "Moves at high speed to raise its Defense and Speed.",
        "Shocks a foe with a powerful laser.",
        "Takes aim with mechanical darts, then rushes nearby foes.",
        "Leaps high into the air and stomps a foe.",
        "Fires an arrow of flame from the back of its hand. Lowers Defense.",
        "Unleashes fiery punches at nearby foes.",
        "Hits a foe with a blazing whirlwind kick.",
        "Saddens nearby foes with a dark voice. May cause Sleep.",
        "Erases a foe with a black sphere. May cause instant death.",
        "Destroys a foe with a hellish tone. May cause Darkness.",
        "Freezes nearby foes with an icy breath. May cause Paralysis.",
        "Pierces a foe with two long fangs. May cause Paralysis.",
        "Confuses nearby foes with a horn's sound waves.",
        "Vibrates nearby foes with ultra-low sound. May restore their HP.",
        "Sends savage plankton to attack nearby foes.",
        "Charges at a foe like a homing torpedo. Lowers Defense.",
        "Breaks down a foe's data at the nanoscale. May cause Confusion.",
        "Fires a small bomb from its fingertip. Lowers Defense.",
        "Strangles a foe with its tentacles and shocks it. Lowers Speed.",
        "Fires deadly poisonous ink at nearby foes. Deals Poison damage.",
        "Slashes a foe with giant scythes. Lowers Attack.",
        "Slices nearby foes with blades of holy wind.",
        "Hits a foe with a giant electric hammer. May cause Paralysis.",
        "Sends lightning from Pao Tsuei into nearby foes.",
        "Drags a foe into the deep sea and suffocates it.",
        "Stabs a foe with its cherished spear, Torrent. Lowers Wisdom.",
        "Smashes a foe with its giant horn. May cause Paralysis.",
        "Rams nearby foes with its giant horn. May cause Paralysis.",
        "Blasts a foe with water at tremendous pressure.",
        "Destroys nearby foes with a giant tsunami. Deals Water damage.",
        "Punches a foe with a shining fist that explodes. Deals Fire damage.",
        "Releases cosmic energy at nearby foes. Deals Light damage.",
        "Slices a foe with lightning-fast petals. May cause Darkness.",
        "Surrounds nearby foes in cherry blossoms and blasts them with light. May cause Confusion.",
        "Throws a disc of light at a foe.",
        "Fires poop from its Empty Can Bazooka. May cause Sleep.",
    ],
}


def main() -> None:
    destination = ROOT / "translations/batch64.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks: list[dict] = []
    reviewed = 0
    for entry, descriptions in DESCRIPTIONS.items():
        for index, text in enumerate(descriptions):
            key = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
            if key not in records:
                raise KeyError(key)
            if key in existing:
                raise ValueError(f"Already translated: {key}")
            row = records[key]
            expected = "Move and item descriptions"
            if category(row) != expected:
                raise ValueError(f"Unexpected category for {key}: {category(row)}")
            wrapped = "\n".join(textwrap.wrap(
                text, width=26, break_long_words=False, break_on_hyphens=False))
            review_note = (
                "Directly translated from the original Japanese combat-effect text. "
                "Status and stat terms follow the established battle UI glossary."
            )
            if entry == 15 and index == 39:
                review_note += " Torrent is verified as Hangyomon's spear name in batch 63."
            blocks.append({
                "archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": expected,
                "english": [wrapped], "sources": ["Original Japanese ROM"],
                "review_note": review_note,
            })
            reviewed += 1
    if reviewed != 100:
        raise ValueError(f"Expected 100 descriptions, got {reviewed}")
    destination.write_text(json.dumps({
        "description": "Translate 100 additional battle-effect descriptions from MESPAK04 entries 14 and 15.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": reviewed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
