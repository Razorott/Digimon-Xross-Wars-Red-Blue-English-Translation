"""Translate the next continuous story section in MESPAK02 entry 7."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    50: "Fine! Then I'll beat you by force!!",
    51: "Guh...! How could I lose to brats like you...?",
    52: "IceDevimon! Lies won't help you! If you don't understand that, you'll never beat us!",
    53: "Heh... Hahahahaha! Is that so?",
    54: "What did you say?!",
    55: "Lies and cheating... Sometimes they can be a source of power, too!",
    56: "Exactly... Just as light casts a shadow, even shining strength needs darkness...",
    57: "W-will I really be reborn as the strongest...?",
    58: "Yes... Your 'cunning' data is essential to the new being. Bring everything together in the Omega Area!",
    59: "Ah... Ahh...! A-a-aah...!",
    60: "The Omega Area...? What is that?",
    61: "Will we learn everything if we go to Earth Fort...?",
    62: "Taiki, Shoutmon! Let's hurry to Earth Fort! The Omega Area... Something about that name sounds really bad...",
    63: "Sounds bad...? How bad? Like when a teacher's about to scold you?",
    64: "...I don't know. When I remembered the name Dynasmon, my heart felt warm... But the Omega Area... That name fills me with fear. It's cold and unknown...",
    65: "...I'm sure the key to Spadamon's memories is there, too. Let's hurry to Earth Fort!",
    66: "Heh heh... Boys, you've finally made it here.",
    67: "You're Arukenimon...! You controlled Sparrowmon back then!",
    68: "Sparrowmon was a special gift from Lord Zeed Millenniummon... I haven't forgotten that humiliation!",
    69: "Don't talk about our friend like she's an object!",
    70: "Heh heh heh... Is that what you call your burning friendship?",
    71: "Ugh, you make me sick! If you're going to use junk data anyway, you might as well let Lord Zeed Millenniummon use it. She was being controlled, so she probably didn't feel a thing!",
    72: "Arukenimon... You're awful!",
    73: "Next, you'll be a present for my lord! What color ribbon should I tie around your shredded bodies? Pink, perhaps? How exciting! I'll put you out of your misery soon!",
    74: "You...!! I'll never forgive you! Never, ever, ever! I won't forgive you!!",
    75: "S-she's scary...",
    76: "ROG, the legendary weapon, everything! I'll offer it all to Lord Zeed Millenniummon!!",
    77: "H-hey, Arukenimon...!",
    78: "No matter how many times I crush it, Elestou Zone rises again! Cursed Dynasmon...!",
    79: "Dynasmon...? You know that name?",
    80: "Heh heh heh... I know why Spadamon lost his memories!!",
    81: "What?!",
    82: "And the reason is...!",
    83: "Arukenimon, I admire your cruelty, but your loose tongue is your greatest flaw...",
    84: "N-no...!",
    85: "Damn it, Zeed Millenniummon! He erased her to shut her up!",
    86: "Dynasmon, the legendary warrior who wielded the legendary weapon and managed Capacitor Tower... Is he connected to my memories...?",
    87: "The legendary ancient weapon... Dynasmon, who could wield it... Spadamon's memories... And the Omega Area... I don't understand... But right now, we must not break the seal on the legendary weapon! That's all I know! Let's hurry to Earth Fort!",
    88: "I never thought we'd meet again! No need for introductions, I am Pharaohmon! I am ROG's Shining Leader, Pharaohmon the Grave!",
    89: "Huh...? Isn't that Anubismon?",
    90: "Doesn't he need a pyramid to transform?",
    91: "Then this should be easy!",
    92: "How disappointing that you didn't notice I was holding back! Now I'll show you my true power... and the great calamity I can unleash!",
    93: "Grrr...! This is so frustrating! How can Pharaohmon lose to a bunch of upstart kids with no titles after fighting so hard?!",
    94: "We're Team Xros Heart! We just can't leave people suffering right in front of us!",
    95: "Xros Heart... It's like a heart burning with passion...",
    96: "...Ah, yes. I haven't lost yet.",
    97: "That's right, Pharaohmon. This is only the beginning. If you join with us, you will have nothing to fear. No worries, doubts, or pain. Give me your 'obsession' now...",
    98: "Very well... Take it all! Crush us to pieces and turn us into the strongest being!",
    99: "Team Xros Heart...! We will rise again! And when we do, we'll crush you for good!!",
}


def main() -> None:
    destination = ROOT / "translations/batch69.json"
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
            raise ValueError(f"Unexpected category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Direct dialogue translation with continuous scene context. Canonical Digimon names, established zone names, and the project's ROG terminology are retained.",
        })
    destination.write_text(json.dumps({
        "description": "Translate the IceDevimon, Arukenimon, and Pharaohmon story sequence in MESPAK02 entry 7.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
