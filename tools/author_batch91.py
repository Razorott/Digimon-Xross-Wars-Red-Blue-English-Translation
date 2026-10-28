"""Translate the Legend Master rewards and Bronze Master tournament, entry 15."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    160: "Equipment acquired!\nRoyal M Star",
    161: "Equipment acquired!\nNiflheim",
    162: "You've climbed all the way to Platinum Master. Surely you won't quit here! The final rank is Legend Master. This is the real test! Remember, Taiki Kudo: when the next battle ends, you won't just be Taiki Kudo... you'll be Taiki, the Legend Master!",
    163: "Hurry and become Legend Master, Taiki Kudo! Everyone who knows you is hoping for it! And this time, your reward is super special! It's perfect for you... In fact, it's practically already yours!",
    164: "You did it! You're finally Legend Master! Congratulations! Incredible work! No Master can surpass you now! As promised, accept this super-special reward worthy of you!",
    165: "Equipment acquired!\nGorgon",
    166: "Key item acquired!\nLegend Medal",
    167: "Use it well, Taiki, the Legend Master!",
    168: "Hello, Taiki Kudo... No, Taiki, the Legend Master. There's no rank left for you to aim for. You're now the one everyone else looks up to. I have no reward left to give you... The shining future of the Digital World is your final reward. Everyone believes you'll win it for us.",
    169: "We'll always expect great things from you. Do your best, Taiki, the Legend Master!",
    170: "If you want to enter the battle arena, register first. Minomon at that counter handles DWM Tournament entries.",
    171: "Looks like you've already entered the DWM Tournament.",
    172: "Are you ready?",
    173: "Go to the battle arena?",
    174: "Yes, let's go.",
    175: "No, not yet.",
    176: "Come talk to me again when you're ready.",
    177: "If you've made up your mind, go ahead.",
    178: "The portal over there leads to the battle arena! Fight with honor!",
    179: "This portal is for Battle Masters only! Challengers must use the portal across from it!",
    180: "Welcome!",
    181: "Please come again!",
    182: "Now, the DWM Tournament Bronze Master match! The challengers are Team Xros Heart, led by General Taiki Kudo!",
    183: "And the Bronze Master Battle Master is... A familiar face from Digimon Story! A quiet, unassuming man with influence behind the scenes! A smiling mad scientist in a white coat, known for bringing children to the Digital World! The legendary Battle Master leading Team Chrono...",
    184: "Mr. Kogure!",
    185: "That introduction makes me sound like a terrible villain... Or is it just me?",
    186: "Before the match, Battle Master Kogure, would you like to say a few words to the challenger?",
    187: "I've fought here ever since the DigiColosseum opened. Every match has been unforgettable. Taiki, you look like you'll put up a good fight. Surely you won't lose to an old man like me! Let's make a battle that will go down in history!",
    188: "Yes! I'll do my best!",
    189: "Battle Master Kogure's Team Chrono versus General Taiki's Team Xros Heart! The match of the century starts now!",
    192: "And the winner is Team Xros Heart! General Taiki Kudo has defeated Team Chrono... and Battle Master Kogure! So great, Taiki! Congratulations!",
    193: "Congratulations, General Taiki, and Team Xros Heart! You're now DWM-certified Bronze Masters. But remember: what matters most isn't your rank... It's how you live on the way to earning it, and after you've earned it.",
    194: "I'll work hard to honor the rank we've earned.",
    195: "Hmm... It seems I worried for nothing. I'm looking forward to seeing what you do, General Taiki!",
    196: "The team that burst onto the Digital World stage... Team Xros Heart and General Taiki! What kind of battle will they show us next? We look forward to seeing what they do from here on! See you next time!",
    197: "Now, the DWM Tournament Silver Master match! First, the challengers: Team Xros Heart, led by General Taiki Kudo!",
    198: "Facing them is their young, strong Battle Master! The shining hero of the brilliant Sunshine City!",
    199: "Battle Master Kou and Team Sunburst!",
}


def main() -> None:
    destination = ROOT / "translations/batch91.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in DIALOGUE.items():
        key = f"MSG/MESPAK02.PAK:015:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected translation category for {key}")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": ["Original Japanese ROM"],
            "review_note": "Completes the DigiColosseum Legend Master reward and introduces the Bronze Master tournament. DWM ranks and existing equipment names follow the project glossary.",
        })
    if len(blocks) != 38:
        raise ValueError(f"Expected 38 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the Legend Master reward and Bronze Master tournament sequence in MESPAK02 entry 15.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
