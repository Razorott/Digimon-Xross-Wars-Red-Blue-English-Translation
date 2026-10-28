"""Translate the remaining Nene rescue scene in MESPAK02 entry 7."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    100: "Taiki! Spadamon!",
    101: "How many ROG members are still left?",
    102: "Uh... Well...! We must have defeated all the ROG leader Digimon by now!",
    103: "Yeah... But there's one more... Never mind. Get to Earth Fort and stop them from breaking the seal!",
    104: "Hey, Taiki... Isn't that Nene?!",
    105: "I knew it... She's still being controlled by ROG.",
    106: "Listen, Nene! We found Sparrowmon, the friend you've been looking for! She's with us now... waiting for you to come back.",
    107: "...Sparrowmon? ...Who is that? I don't know her...",
    108: "Nene forgot Sparrowmon...!",
    109: "No... That can't be true! Nene would never forget Sparrowmon! I won't believe it!",
    110: "Foolish, pitiful wretches... Trust only yourselves...",
    112: "Damn it! It was a trap?!",
    113: "Nene...! Sparrowmon! Remember her! Remember us!",
    114: "Gah... G-g-g-g... As expected of Spadamon... The boy who tamed him...",
    115: "This one is already... spent... G-gah...",
    116: "Lost Space... I made them find it... I alone will become the strongest and claim everything...",
    117: "...Hey, what happened to them? It was like someone completely different had taken them over...",
    118: "So they used her to find Lost Space...?",
    119: "Nene! Hey, can you hear me?! Wake up!",
    120: "Nene!",
    121: "Nene, are you all right?!",
    122: "...Taiki...? What happened to me...? Sparrowmon! Where is she?!",
    123: "You're okay! Don't worry, Nene. Sparrowmon is here with us!",
    124: "Oh... Thank goodness! I could hear Sparrowmon's voice in the darkness... I heard her the whole time, but I couldn't move. A terrifying darkness had seized me and wouldn't let go...",
    125: "Those SkullKnightmon who were with you seemed strange... Were they being controlled, too?",
    126: "...No. That SkullKnightmon was a fake. Zeed Millenniummon made it from my memories.",
    127: "He made a fake from your memories? How is that possible?!",
    128: "Taiki! It's terrible! Zeed Millenniummon has entered Lost Space and is trying to do something. I think he's going to revive the Weapon Digimon...!",
    130: "...So you're Spadamon?",
    132: "So it's you... I have to protect you... Taiki, don't let this one join the next battle! Don't let them go!",
    133: "Nene's still confused... Why is she talking about Spadamon...?",
    134: "We can figure that out later. First, let's help Nene...",
    135: "Nene?! Where are you going?",
    136: "Oh no! Earth Fort is just ahead! She went alone to stop them from breaking the seal!",
    137: "Hey, hey, hey! Charging in unprepared where Zeed Millenniummon is... She's really confused, isn't she?!",
    139: "Nene, are you okay?! ...Where are they?",
    146: "Taiki! Why did you bring him here?!",
    147: "Spadamon is our friend now. I couldn't leave him behind. And if one of our friends were in danger, you'd come help us even if we told you not to, right, Nene?",
    148: "...You're right. That's how you are. You reached out to me when I was suffering...",
    149: "Don't carry this alone. Tell us what's going on, too...",
    150: "...ROG wants to revive the Legendary Ancient Weapon in Elestou Zone.",
    152: "The Legendary Ancient Weapon isn't just a weapon... It's a Weapon Digimon that transforms into the strongest weapon.",
    154: "...Yes. That's Elestou Zone's secret. Whoever controls a Weapon Digimon could destroy the world, so this Zone has always been targeted. Dynasmon once protected the Zone alongside the Weapon Digimon... But no one knows where Dynasmon went or why the Weapon Digimon were sealed away.",
    156: "Taiki, we don't have much time. For now, we have to stop Zeed Millenniummon!",
    164: "I mean, 'all the way to chocolate'...?",
    165: "...How far is that supposed to be?",
    198: "Stop right there, Barbamon!",
    199: "Well, well... Nene Amano, the General who abandoned her former team and joined Xros Heart... Do you think I can be stopped by someone who fell for such a feeble illusion?",
}


def main() -> None:
    destination = ROOT / "translations/batch78.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:007:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Continuous scene translation. Nene's apparent memory loss, the shadow's use of her memories, the Weapon Digimon reveal, and the Dynasmon mystery are preserved as the game presents them.",
        })
    if len(blocks) != 48:
        raise ValueError(f"Expected 48 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the remaining Nene rescue and Weapon Digimon reveal in MESPAK02 entry 7.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
