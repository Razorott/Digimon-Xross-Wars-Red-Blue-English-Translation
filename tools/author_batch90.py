"""Translate item rewards and the DigiColosseum introduction, MESPAK02 entry 15."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


DIALOGUE = {
    4: "All right. Here's an item for you.",
    7: "DaiPenmon did it! Here's your item~",
    12: "I have no choice... I'll give you an item, then.",
    13: "Yay, an item! An item!♪",
    36: "Be grateful, and use it carefully, nume!",
    38: "Don't you dare treat it carelessly!",
    65: "Please take good care of it. Well then, goodbye!",
    75: "You'll take good care of it, right?",
    78: "DaiPenmon did it! Here's your item~",
    83: "Don't you dare treat it carelessly!",
    84: "Take good care of it!♪",
    96: "Hey, Taiki! Big news! That portal over there connects to the DigiColosseum!",
    97: "The DigiColosseum? What's that?",
    98: "It's a legendary battle arena in the Colosseum Zone! They say a portal only appears in peaceful Zones, but it never appeared in Elestou Zone... Now that you brought peace here, the portal has opened!",
    99: "Wow! That's amazing! What do you do there?",
    100: "You battle the heroes who saved the Digital World! It's ranked, so you can test your strength. Raise your rank and earn a title and prizes! Those prizes are only available there! I can't wait! Let's go!",
    101: "Welcome to the DigiColosseum!",
    102: "This is the DigiColosseum...?",
    103: "Yes, indeed! This is the DigiColosseum! A historic arena etched with countless battles! It has always stood at the heart of the Digital World, transcending time and space... This is the legendary DigiColosseum!",
    104: "...It's that amazing? I had no idea...",
    105: "The DigiColosseum was born with the Digital World, and some say it will perish with it. In a sense, the DigiColosseum is the Digital World itself. Only chosen Digimon may enter!",
    106: "...Huh?! But, as you can see, I'm not a Digimon...",
    107: "You're here to support Digimon in battle, aren't you? Team leaders, Tamers, Breeders, Generals... Whatever you call yourselves, you're very welcome here!",
    108: "I get that this place has a great history, but what are my Digimon and I supposed to do here?",
    109: "This is a battle arena for Digimon who have mastered their skills. Form a team and test your strength against others!",
    110: "First, talk to Minomon at the counter. It will recommend a tournament for your rank. Just enter that tournament and you're ready to go!",
    111: "Do I need anything to enter? I don't have much money...",
    112: "All you need is strength and skill you've trained, plus the courage and friendship you've built with your partner. No special qualifications,and no money,are needed!",
    113: "I see...",
    114: "After you enter, talk to Knightmon. Then you can pass through the portal in the back. As a challenger, you'll enter the battle arena and fight the great Masters! Win against the team led by each rank's Master, and your entry rank will rise one step at a time!",
    115: "If you beat the top-ranked Legend Master, you'll become a new Legend Master yourself! Whoa, that's so coooool!▼",
    116: "Once you actually enter, though, you'll see that it's more like a dream than reality. Take it one step at a time.",
    117: "Got it. I'll give it a try! Thanks for all the help!",
    118: "Hello! This is the DWM Tournament Entry Counter, where we measure each Digimon's strength!♪",
    119: "DWM...?",
    120: "DWM stands for Digital World Master! It's a measure of Digimon battle strength! There are five Master ranks: Bronze, Silver, Gold, Platinum, and Legend! Fight the Masters in a tournament, and if you win, you'll be recognized as a Master of that rank! Get it?♪",
    121: "If you want to enter, just talk to me! I'll be waiting!♪",
    122: "Oh, you're the Legend Master! The greatest and strongest Master in all of DWM!▼",
    123: "The peace of the Digital World rests on your shoulders! Woo-hoo! So cool! I'm falling for you!▼",
    124: "Oh? You're already entered. Do you want to cancel your entry?",
    125: "Yes, cancel it.",
    126: "No, keep my entry.",
    127: "Okay! I'll cancel it for you.",
    128: "Then enter again whenever you feel like it! I'll be waiting!♪",
    129: "Talk to Knightmon at the lower right. Then you can use the portal to enter the battle arena!",
    130: "Good luck!♪",
    131: "You're entering the Bronze Master Tournament, right?♪",
    132: "Okay! You're entered! Talk to Knightmon at the lower right. Then you can use the portal to enter the battle arena!",
    133: "You're entering the Silver Master Tournament, right?♪",
    134: "You're entering the Gold Master Tournament, right?♪",
    135: "You're entering the Platinum Master Tournament, right?♪",
    136: "You're entering the Legend Master Tournament, right? Amazing! I can't believe it!♪",
    137: "Welcome, Taiki Kudo!",
    138: "How do you know my name...?",
    139: "This is the DigiColosseum, the heart of the Digital World! A place that selects and tests those with the strength to shape its future! I know everything about anyone strong enough to make it here: your name, face, personality, partner, hobbies, skills, habits, how you sleep, what you like and hate... Everything!",
    140: "Knowing that much about me is kind of creepy... Anyway, what do you do here?",
    141: "This is the reward counter for victors! Talk to me each time you win through a tournament. I'll give you a prize worthy of your results: a special item fit for young heroes who protect the Digital World's future!",
    142: "I'm expecting great things from you! Now go, Taiki Kudo!",
    143: "Hurry and become a Bronze Master, Taiki Kudo! I've already prepared a special reward for you!",
    144: "You've finally become a Bronze Master, Taiki Kudo! Congratulations! Well done! As promised, here's your special reward!",
    145: "Equipment acquired!\nLH Slasher",
    146: "Equipment acquired!\nTifaret",
    147: "Surely you aren't satisfied with being a Bronze Master! Next is the Silver Master! Go, Taiki Kudo!",
    148: "Hurry and become a Silver Master, Taiki Kudo! Of course, I've prepared a special reward!",
    149: "You've become a Silver Master?! Congratulations! As expected! As promised, here's your special reward!",
    150: "Equipment acquired!\nSodom & Gomorrah",
    151: "Equipment acquired!\nPurge Shine",
    152: "Silver Master is only a stepping stone. Next is Gold Master! Go, Taiki Kudo!",
    153: "Hurry and become a Gold Master, Taiki Kudo! I've had your special reward ready for ages!",
    154: "You've become a Gold Master?! You're making great progress! As promised, here's your special reward!",
    155: "Equipment acquired!\nClaiomh Solais",
    156: "Equipment acquired!\nScale Mail",
    157: "Becoming a Gold Master was practically a given. Next is Platinum Master,that's where the real challenge begins! Go, Taiki Kudo. Show me your strength!",
    158: "Hurry and become a Platinum Master, Taiki Kudo! A special reward is waiting for you!",
    159: "You've become a Platinum Master?! Congratulations! That's incredible! As promised, here's your special reward!",
}


def main() -> None:
    destination = ROOT / "translations/batch90.json"
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
            "review_note": "DigiColosseum lore, entry and rank logic, and the first four tournament reward tiers. Equipment names follow the existing reviewed item glossary.",
        })
    if len(blocks) != 75:
        raise ValueError(f"Expected 75 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the DigiColosseum introduction and Bronze through Platinum Master setup in MESPAK02 entry 15.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
