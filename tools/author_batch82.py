"""Translate the seventh-tower mystery and Dynasmon introduction."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    164: "All things come around... Lord Barbamon Reincarbage!",
    165: "We won't let Barbamon have his way!",
    166: "Garbagemons! We won't lose to Barbamon!",
    168: "Uh... That area over there smells bad, too...",
    170: "This tower is back in Normal Mode now, too.",
    171: "Once we reclaim all the Capacitor Towers... the protective field will disappear, right?",
    172: "...Probably not.",
    173: "Wait, Spadamon! Why are you saying that all of a sudden?!",
    174: "We restored the Capacitor Towers the right way... But I feel like I'm forgetting something important...",
    175: "Something important...?",
    176: "There are six Capacitor Towers... But what about the Capacitor System? ...I can't think straight. What's happening to me?",
    177: "...Spadamon, I'm sure we'll understand once we keep going.",
    55: "Mmm... Gimme!!",
    196: "Were you the one who called us...?",
    197: "That's right, Taiki Kudo... I am Dynasmon, who was supposed to protect this Zone...",
    198: "...Supposed to?",
    199: "I was a warrior who led the Weapon Digimon into battle. I was meant to defend this Zone from invasion... But all I managed to protect... was this tiny memory.",
}


def main() -> None:
    destination = ROOT / "translations/batch82.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:009:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "The scene first questions the six-tower count, then reveals Dynasmon and his role as protector. The line about a tiny memory is kept deliberately mysterious, matching the following story reveal.",
        })
    if len(blocks) != 17:
        raise ValueError(f"Expected 17 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the Garbagemons' final exchange, the tower-count clue, and Dynasmon's first appearance in MESPAK02 entry 9.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
