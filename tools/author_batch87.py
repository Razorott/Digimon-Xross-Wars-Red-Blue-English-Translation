"""Translate post-battle dialogue and field-skill messages, MESPAK02 entry 12."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    0: "...All right. MailBirdramon, Greymon,let's join forces and defeat Barbamon.",
    1: "...Taiki.",
    2: "We have to defeat Barbamon and restore peace to this Zone. That's why we need their help.",
    3: "...As expected of Kiriha's rival. We'll be nearby. If you need us, just say the word.",
    33: "What about Kiriha? Can't we find him? Barbamon sent him to another Zone...",
    44: "Thanks, Parrotmon. You've really helped us out.",
    47: "I'm so relieved everyone made it back!♪",
    66: "The Digimon who hid when ROG attacked might come back now. I'll wait for them at Sky Fort!",
    71: "Finally awake! While you were asleep, we've been through a lot!",
    72: "Did someone attack again?!",
    73: "Well... You're half right. We let our guard down, and Taiki's fans stormed in! Everyone at Sky Fort got mobbed!",
    74: "...Fans? Wait, my fans?!",
    75: "They're Digimon who fled ROG in this Zone. They wanted to see the hero who saved Elestou Zone! And I'm almost as popular as Taiki! Better practice your autograph while you can, Taiki!♪",
    76: "Shoutmon's autograph is so messy nobody can read it... Maybe that's why it's popular as art?",
    77: "What?! That's rude, Zenjiro! You're the one who went wild at Earth Fort... What are you, a kid?!",
    78: "Th-that has nothing to do with it! Besides, Earth Fort is a man's dre... I mean, a man's dream!",
    79: "Taiki isn't just meeting fans! Some Digimon have requests or need help. Check the Quest Monitor later, okay?",
    80: "Got it. If everyone's counting on us, we'll do what we can to help!",
    81: "Forget the fans,things are hectic and dangerous around the Zone right now. If you're going somewhere, I'll come with you!",
    82: "Okay, thanks, legendary Weapon Digimon!♪",
    83: "Taiki! Hurry up and let's go!",
    92: "Leave the tent?",
    93: "Yes, leave.",
    94: "No, stay.",
    105: "Consumable item acquired!\n^i",
    106: "Consumable items acquired!\n^i ×^n",
    107: "Equipment acquired!\n^i",
    108: "Equipment acquired!\n^i ×^n",
    111: "DigiFarm item acquired!\n^i",
    112: "DigiFarm items acquired!\n^i ×^n",
    113: "DigiScore acquired!\n^i",
    114: "Key item acquired!\n^i",
    115: "Bit acquired!\n^b",
    117: "Airport Gate opened!",
    119: "Switch Gate opened!",
    120: "No Digimon in your party knows Rock Breaking.",
    121: "Used Rock Breaking!",
    122: "No Digimon in your party knows Tree Chopping.",
    123: "Used Tree Chopping!",
    124: "No Digimon in your party knows Melt Ice.",
    125: "Used Melt Ice!",
    126: "Use Digging to travel?",
    129: "No Digimon in your party knows Digging.",
    130: "Used Digging!",
    131: "Use Diving to travel?",
    134: "No Digimon in your party knows Diving.",
    135: "Used Diving!",
}


def main() -> None:
    destination = ROOT / "translations/batch87.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:012:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Post-Armamon alliance dialogue and field skill messages. Placeholder tokens ^i, ^n, and ^b are preserved.",
        })
    if len(blocks) != 47:
        raise ValueError(f"Expected 47 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the return to Sky Fort, alliance dialogue, and remaining field skill messages in MESPAK02 entry 12.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
