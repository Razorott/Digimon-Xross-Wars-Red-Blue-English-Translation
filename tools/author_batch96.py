"""Translate the next rival-gang side mission and its skill-test battle."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


ENTRY21 = {
    17: "Argh! MegaGargomon, you'll pay for this! That big brute thinks he can do whatever he wants! I'll bring the disbanded Giro-Giro Gang back together, team up with the Mame-Mame Gang, and take him down! Help me out! First, head to Crystal Volcano and meet the others who went ahead!",
    18: "The others have already headed to Crystal Volcano! Taiki, go join them as their bodyguard!",
    19: "Thanks, Taiki! Here's your reward! The Mame-Mame and Giro-Giro Gangs have been rivals for ages, but maybe we were just two of a kind, each trying to outdo the other... Now that we're together, there's nothing we can't handle!",
    20: "Want to join us? If you're interested, come talk to me anytime!",
    51: "Ah, so you're the one with real fighting skill! We formed a team of top-notch Digimon to test challengers like you! Our name is... the Skill-Test Crew! STC for short! ...What? It's the same thing? Yes, I just made it up. Don't worry about it! Win, and we'll pay you big! You're interested now, right?",
    52: "Head to Tokona Sea now and fight the Skill-Test Crew! Win, and I'll give you a big reward. Come back here after the fight! Good luck!",
    53: "Great job! You really did it! Here's your reward. The STC and I guarantee you've got skill!",
    54: "See you later! Keep polishing those skills!",
    55: "Skill-Test Crew... STC? Did Piximon come up with this name...? What a weird choice... Whatever. You're here to test your skills, right? I can already tell how good you are! I'll serve up a punch worthy of your skill! Ready... Bomber!",
    56: "Fine, you pass. Not bad! But that was only Stage One. Now for Stage Two! Ready... Bomber!",
    57: "All right, you pass! Nice work! But that was only Stage Two. Next up is Stage Three! Ready... Bomber!",
    58: "That's the end! Well done! You've got impressive skills, just like you said! Head back to Piximon and collect your reward!",
    59: "The S is for 'Super,' the T for 'Tough,' and the C for 'Cool'! I just came up with it, but burn it into your heart! Yeah! ...Bomber!",
    60: "Ah, so you're the one with real fighting skill! We formed a team of top-notch Digimon to test challengers like you! Our name is... the Skill-Test Crew! STC for short! ...What? It's the same thing? Yes, I just made it up. Don't worry about it! Win, and we'll pay you big! You're interested now, right?",
    61: "Head to Tokona Sea now and fight the Skill-Test Crew! Win, and I'll give you a big reward. Come back here after the fight! Good luck!",
    62: "Great job! You really did it! Here's your reward. The STC and I guarantee you've got skill!",
    63: "See you later! Keep polishing those skills!",
    64: "Skill-Test Crew... STC? Did ExTyrannomon come up with this name...? What a weird choice... Whatever. You're here to test your skills, right? I can already tell how good you are! I'll serve up a punch worthy of your skill! Ready... Bomber!",
    65: "Fine, you pass. Not bad! But that was only Stage One. Now for Stage Two! Ready... Bomber!",
    66: "All right, you pass! Nice work! But that was only Stage Two. Next up is Stage Three! Ready... Bomber!",
    67: "That's the end! Well done! You've got impressive skills, just like you said! Head back to ExTyrannomon and collect your reward!",
    68: "The S is for 'Super,' the T for 'Tough,' and the C for 'Cool'! I just came up with it, but burn it into your heart! Yeah! ...Bomber!",
}


def main() -> None:
    destination = ROOT / "translations/batch96.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in ENTRY21.items():
        key = f"MSG/MESPAK02.PAK:021:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected category for {key}: {category(row)}")
        sources = ["Original Japanese ROM", "Existing project location glossary"]
        for name, url in (
            ("MegaGargomon", "https://world.digimoncard.com/cards/?card_no=BT3-057&search=true"),
            ("Piximon", "https://world.digimoncard.com/cards/?card_no=BT1-059&search=true"),
            ("ExTyrannomon", "https://world.digimoncard.com/cards/?card_no=EX9-041&search=true"),
        ):
            if name in english:
                sources.append(url)
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": sources,
            "review_note": "Optional rival-gang reunion and three-stage skill-test mission. Western Digimon spellings are supported by the linked Bandai English card list. Tokona Sea and Crystal Volcano follow the established game glossary. The Japanese UDY/UDE wordplay is localized as Skill-Test Crew (STC) with a matching English backronym, so the mission name and battle dialogue remain coherent.",
        })
    if len(blocks) != 22:
        raise ValueError(f"Expected 22 dialogue slots, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the rival-gang reunion and three-stage Skill-Test Crew mission in MESPAK02 entry 21.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
