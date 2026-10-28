"""Fill the remaining opening and first-story dialogue in both scripts."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


TRANSLATIONS = {
    0: {
        0: "Hey, everyone! Nice to meet you! Thanks for starting up the Digimon Battle Review Board!",
        1: "The anime hasn't even started yet, and you're already such devoted fans!",
        2: "Before we begin, let me introduce my friends!",
        12: "They're tiny, but there are lots of them. The Starmons are a lively bunch!",
        13: "When they gather together, they become the mighty Star Sword!",
        17: "And Taiki's rival has been acting strangely, too.",
        18: "There's Kiriha Aonuma, the cool and mysterious boy, for better or worse. And there's Nene Amano, a girl who's mysterious in all sorts of ways. Which one you face depends on the version you play! To uncover Kiriha's secret, play Blue Flare. To solve Nene's mystery, play Twilight!",
        19: "Wait, isn't Zenjiro a rival too?",
        20: "No... The enemy captured him along with us.",
        21: "Besides, no one would buy a Zenjiro version!",
        22: "Now, in the strange world of Elestou Zone... our adventure together is about to begin!",
        78: "We did it!",
        79: "You sure did! That's our Taiki! I knew I picked the right General!",
        80: "Heh... Not bad! But that was just a warm-up. I only pretended to be weak so I could gauge your strength!",
        81: "You got knocked clear across the room...",
        82: "Quiet, you little weakling! You have no idea how frightening I am when I get serious. I'll show you right now!",
        83: "That is an astonishing amount of sore-loser talk...",
        84: "I'm used to stubborn foes. If you won't give up, we'll beat you as many times as it takes!",
        93: "Spadamon! Thank goodness you're safe!",
        94: "I'm sorry I'm late. I left everyone behind and hid by myself this whole time. I'm sorry.",
        95: "What are you talking about? You did nothing wrong! If they had captured you, this Zone would have been finished!",
        96: "What do you mean?",
        97: "Spadamon isn't an ordinary Digimon. He's a Weapon Digimon, the guardian of this Zone. He has tremendous power hidden within him. We can't let the villains take him!",
        98: "Spadamon is a god?!",
        99: "N-no, nothing so grand! I was made to protect this Zone, but I can't defeat the invaders myself. All I can do is find allies, bring them together, and guide them. That's all.",
        100: "That reminds me. Where are our friends?",
        101: "I think they were taken to the Central Room. Be careful, though. The Digimon in there is frightening... in a way.",
        102: "...I've got to ask. What do you mean, 'in a way'?",
        103: "I peeked in there once. He was laughing happily, then suddenly got very angry, and finally started crying. But when I looked closer... he was talking to himself the whole time.",
        104: "Frightening... or just dangerous?",
        105: "You're the boss, aren't you?!",
        106: "...Who are you? Who gave you permission to come in here? Get out!",
        107: "We're not leaving. You are! This place belongs to us: this room, this fort, and this entire Zone! We won't hand any of it over!",
        108: "Ah, I remember you. The coward who abandoned his friends and fled. Now you've come back with a few pitiful allies. What do you intend to do this time?",
        109: "Isn't it obvious? We're going to knock you villains down!",
        110: "And take back our friends and this Zone!",
        111: "Pathetic fools. Die regretting your own stupidity.",
        112: "We've heard that line before. Enjoy sounding tough while you can. Nobody who's talked to us like that has come out unscathed!",
        113: "Your scheme ends here! Give up and get out of this Zone!",
        114: "...I see. You truly are extraordinary fools.",
        117: "...What is he talking about?",
        119: "Thanks to all of you defeating that Digimon, one of the seals suppressing my power has come undone. Thank you, everyone.",
        120: "So that's the power of the Weapon Digimon who protects Elestou Zone... If we break the other seals, can Spadamon regain his power?",
        154: "What's this? Something's written on it... 'Commander Room Save PC: Preparing'...?",
        156: "This looks like one of those machines at a bank...",
        157: "I think so. You can deposit BIT! Maybe I'll put some in... Oh, right. I don't have any BIT.",
        158: "What's this?",
        159: "This is the Sky Port, the Digimon Air Corps' airfield. They fly in and out from here. Switch on that console over there...",
        160: "...and an Airport Gate opens, letting you travel to other airports. Elestou Zone has Fort Island, home of Sky Fort; volcanic Crystal Island; mountainous Hyde Island; and the vast Energy Continent stretching north and south.",
        161: "Once an Airport Gate is open, you can go anywhere. Just talk to a member of the Digimon Air Corps, and they'll fly you to any airport in no time!",
        162: "Amazing!",
        163: "But there's a problem right now, so I can't open the Airport Gate. Sorry, Taiki!",
        164: "I see... That's too bad.",
        165: "Is this an airfield?",
        166: "Yes. The Digimon Air Corps uses it. It's called the Sky Port, the airport at Sky Fort.",
        167: "If you switch on that console...",
        168: "...the Airport Gate opens, and you can travel to other airports. Elestou Zone has Fort Island, home of Sky Fort; volcanic Crystal Island; mountainous Hyde Island; and the vast Energy Continent stretching north and south.",
        169: "You can reach any airport in Elestou Zone from here. Once you've opened the airport's gate, just talk to a member of the Digimon Air Corps.",
        170: "That's amazing! Now we can finally go rescue the Digimon who were taken away!",
        171: "Taiki... Do you really think I can save my friends?",
        172: "Of course you can! We're all with you. Everything will be all right!",
        181: "What's this? It says... 'DigiTent Save PC: Preparing'...?",
        183: "Hey, everyone! Nice to meet you!",
        184: "Nice to meet you too!",
        185: "Before we begin, let me introduce my friends!",
        195: "They're tiny, but there are lots of them! The Pickmons are a lively bunch!",
        196: "When they combine with Starmon, they become the powerful Star Sword!",
    },
    2: {
        182: "I-I don't know anything about that! If it existed, I'd have driven you out long ago!",
        183: "...True. If it existed, we'd have found it. Everything we've discovered has been a disappointment. You useless liars have served your purpose! I'll throw you all out and see whether you can fly!",
        184: "Stop!",
        185: "L-leave Patamon alone!",
        186: "Your voice is cracking so badly I can barely understand you! The biggest spoiled brat in this Zone has the nerve to act tough? You only came back now, after leaving your friends behind. Who was the coward who ran away?",
        187: "Never mind. Now that you've come back, I can hand you over to Lord Minotarumon. For some reason, all of ROG has been looking for you. When Lord Minotarumon sees what I can do, I'll become a ROG officer! Yahoo!",
        188: "W-what should I do? They're after me after all! I want to run... but I have to save Patamon! Shoutmon! Taiki! What should I do?!",
        189: "Come on! Make up your mind! Don't worry. You've got a General on your side!",
        194: "To perform a DigiXross, choose the Fusion command. First, learn the combination move. Then gather the Digimon it needs and put them in your party!",
        196: "Use the Tactics command for auto-battle! Full Power selects your strongest move and a target it can defeat. Conserve uses only physical moves, without spending MP. Guard puts all your effort into defense. Escape focuses entirely on getting away. If even one Digimon escapes, you can avoid the battle!",
    },
}


def main() -> None:
    destination = ROOT / "translations/batch98.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for entry, translations in TRANSLATIONS.items():
        for index, english in sorted(translations.items()):
            key = f"MSG/MESPAK02.PAK:{entry:03d}:{index:05d}"
            if key not in records or key in existing:
                raise ValueError(f"Missing or already translated source: {key}")
            row = records[key]
            if category(row) != "Story and dialogue":
                raise ValueError(f"Unexpected category for {key}")
            sources = ["Original Japanese ROM", "Existing reviewed project glossary"]
            if any(x in english for x in ("Spadamon", "Weapon Digimon")):
                sources.append("https://digimon.net/reference_en/detail.php?directory_name=spadamon")
            if "Pickmons" in english:
                sources.append("https://digimon.net/reference_en/detail.php?directory_name=pickmon")
            if "Starmons" in english:
                sources.append("https://digimon.net/reference_en/detail.php?directory_name=starmons")
            if "Star Sword" in english:
                sources.append("https://digimon.net/reference_en/detail.php?directory_name=shoutmonx4k")
            blocks.append({"archive": row["archive"], "entry": entry, "start": index,
                           "category": "Story and dialogue", "english": [english],
                           "sources": sources,
                           "review_note": "Opening and early-story lines translated from the Japanese ROM. Original human names and the requested DigiXross spelling are retained. The build wraps story text at 15 columns."})
    destination.write_text(json.dumps({"description": "Opening and first-story dialogue in Blue and Red.",
                                       "blocks": blocks}, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}))


if __name__ == "__main__":
    main()
