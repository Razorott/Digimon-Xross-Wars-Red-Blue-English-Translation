"""Author a source-checked Farm Island and character dialogue batch."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


# These are direct translations of the Japanese dialogue and quiz strings in
# MESPAK02 entries 24 and 25. Character names and game terms follow the existing
# glossary; the two named special moves are cross-checked against Dawn/Dusk.
ENTRY24 = {
    0: "Things I can't stand? Being ignored! Especially when I'm holding the mic. If you tune me out, I lose it!",
    1: "You ask if I'm ever down? Sure, of course! I'm sensitive! What do I do? Nothing, really. By the time I notice, I'm already over it!",
    2: "Someone told me to keep it down while I was singing... I was really getting into it, too... That's cold, man!",
    3: "I tried to blow out a candle with a mighty shout, but I inhaled instead and burned my mouth... Yeah, I know I messed up. Can't quite figure out where it all went wrong, though.",
    4: "Whoa-oh-oh! Awooo... My shout left you spellbound, huh...? Your eyes rolled way back in your head for a sec. Did you pass out?",
    5: "Listen to my shout! ...What, you don't want to? Okay, how about this: I'll listen to your mighty shout first. That fair? Huh? You don't want that either?! Don't be so selfish!",
    6: "Listen! I did it! I finally pulled it off! I started by shattering a glass with my voice... and now I've managed to crack Chrome Digizoid! ...Hey, why are you running? Hear me out!",
    7: "Hey, Taiki! It's boring here. Put me in the party and let me fight! Come on, Taiki, please!",
    8: "Oh? You mean I can quit my job?",
    9: "Got it! Just call me whenever!",
    10: "Okay! I'll get back to work, then!",
    11: "You want me to work? Anytime!",
    12: "Whoa... This is amazing! It's so good! I feel strength welling up inside me!",
    13: "Thanks for the DigiNoir! I feel a lot better now.",
    14: "Huh? Doesn't taste that good...",
    15: "Um... Sorry, but I'm stuffed right now...",
    16: "I'm ^2, a ^0-species, ^1-type Digimon! I'm so happy to be on Farm Island! I'll train hard and get stronger!",
    17: "Hey, Taiki! Quick question: What's the one thing Mammothmon can't stand?",
    18: "Heat!",
    19: "Cold!",
    20: "That's right! Heat is the one thing he's weak to. He was buried in ice for ages... I couldn't take that!",
    21: "Nope! Not even close! Taiki, how could you miss such an easy one? I'm so disappointed! Boo!",
    22: "Hey, Taiki! Quick answer: Which can't fly, Biyomon or Patamon?",
    23: "They can both fly!",
    24: "Neither of them can fly!",
    25: "Hee-hee, correct! Nice work, Taiki! It was a trick question, and you got it right away! Between you and me, though, they fly so slowly it's hard to say they can fly at all.",
    26: "Bzzt! Wrong! You thought you beat the trick question, but you fell for it! Patamon and Biyomon are slower in the air than they are on foot. You could say they just float!",
    27: "Hey, Taiki! Answer this one: What is WarGreymon's armor made of?",
    29: "Calcium!",
    30: "Ding-ding! Correct! But if you'd said Chrome Digizoid, I'd have marked you wrong!",
    31: "Sure, calcium... Like that's true! I'm so disappointed. Did you really think that would be funny?",
    32: "Hey, Taiki! What's MarineAngemon's special move?",
    33: "Ocean Love!",
    34: "Holy Flame!",
    35: "Yay, correct! Nice one, Taiki! I almost feel like Ocean Love hit me - my eyes are turning into hearts!",
    36: "Bzzt! Wrong! That special move belongs to a different Digimon. I'll let you guess who!",
    37: "Hey, Taiki! When you choose a partner Digimon, what matters most to you?",
    38: "Their personality!",
    39: "Their looks!",
    40: "Oh, really? I see... So that's how it is... I knew it... Hee-hee-hee...",
    41: "Whaaat?! ...Well, looks do matter a little... But hearing you say it so plainly kind of hurts...",
    42: "So far, you've played this game for ^0 hours and ^1 minutes. Let's keep adventuring together!",
    43: "Every Digimon has an attribute it's weak against. For example, Phantom Beast Digimon are weak to the Dark attribute. Keep matchups in mind or you could lose!",
    44: "Every Digimon has an attribute it's strong against. For example, Beast Digimon are strong against the Fighting attribute. Use matchups to make battles easier!",
    45: "My field skill is Rock Breaking! I can smash rocks blocking the path!",
    46: "My field skill is Ice Melting! I can melt the ice blocking the path!",
    47: "My field skill is Tree Chopping! I can chop down trees blocking the path!",
    48: "My field skill is Digging! I can use underground tunnels to reach other places!",
    49: "My field skill is Diving! I can use underwater tunnels to reach other places!",
    50: "I don't have any field skills, but I'll do my best in battle!",
    51: "The new Farm Goods seem to affect our HP and MP. I can't wait to see what they do!",
    52: "The new Farm Goods seem to affect our EXP. I can't wait to see what they do!",
    53: "The new Farm Goods seem to affect our Attack. I can't wait to see what they do!",
    54: "The new Farm Goods seem to affect our Wisdom. I can't wait to see what they do!",
    55: "The new Farm Goods seem to affect our Speed. I can't wait to see what they do!",
    56: "The new Farm Goods seem to affect our Defense. I can't wait to see what they do!",
    57: "The new Farm Goods seem to help make equipment. I can't wait to see what we can build!",
    58: "We need Farm Goods to get stronger. Taiki, could you place some for us?",
}

ENTRY25 = {
    0: "Hey, Taiki. Answer me this: What's the name of Hangyomon's spear?",
    1: "Torrent!",
    2: "Hangyomon Spear!",
    3: "Hmm... Correct. For a General, you know a surprising amount. I'll even praise you for it... just this once!",
    4: "Just as I thought - you're so predictable. And wrong. You thought Hangyomon's spear would be called Hangyomon Spear? I knew you'd think that. I'm disappointed.",
    5: "Hey, Taiki. Answer me this: What is Unimon's horn made of?",
    6: "Mithril!",
    8: "That's right! It was easy, wasn't it?",
    9: "Wrong. Your answer, your aim, your attitude - everything is half-baked. Don't pretend you know things. Go wash your face and try again. There might not be a next time.",
    10: "Hey, Taiki. Answer me this: Which Digimon uses the poisonous ink attack called Calligraphy Ink?",
    12: "Gesomon!",
    13: "Correct. Anyone should know that much, especially a General like you!",
    14: "No, that's wrong. Squid ink and octopus ink look alike, but they're different - like 'cute' and 'adorable.' Similar, but not the same!",
    15: "Hey, Taiki. Airdramon's special move Spinning Needle creates what when it beats its wings?",
    16: "A slicing gust!",
    17: "A cloud of dust!",
    18: "That's right. There's no punchline. A compliment from me is reward enough, isn't it?",
    19: "Wrong - and that's not even the main problem. You answered without thinking about my question... You're the worst.",
    20: "Hey, Taiki. When you choose a partner, what do you care about?",
    21: "Their looks!",
    22: "Their personality!",
    23: "Hmm... That's quite a claim. If you can really judge someone just by their looks, I might actually respect you!",
    24: "Oh... What a boring answer. You think you can easily understand how someone feels? If so, you're pretty naive!",
    25: "^P has played this game for ^0 hours and ^1 minutes so far. That's not enough. Not nearly enough! Keep playing with us, got it?",
    26: "Do you know a Digimon's weak attribute? For example, Plant Digimon are weak to the Fire attribute. Think about matchups or you'll lose!",
    27: "Do you know a Digimon's strong attribute? For example, Phantom Beast Digimon are strong against the Fire attribute. Think before you send them into battle!",
    28: "My field skill is Rock Breaking! I can smash even the most annoying rocks blocking the way!",
    29: "My field skill is Ice Melting! I can melt all that annoying ice in one go!",
    30: "My field skill is Tree Chopping! I can chop down those annoying trees in one clean swing!",
}


def main() -> None:
    destination = ROOT / "translations/batch63.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks: list[dict] = []
    seen: set[str] = set()
    dawn_dusk_url = "https://digimon.fandom.com/wiki/Digimon_World_Dawn_and_Dusk/Attacks"
    marineangemon_url = "https://digimon.fandom.com/wiki/MarineAngemon"
    airdramon_url = "https://digimon.fandom.com/wiki/Airdramon"
    hangyomon_url = "https://wikimon.net/Hangyomon"
    world3_equipment_url = "https://gamefaqs.gamespot.com/ps/562323-digimon-world-3/faqs/79264/normal-equipment"
    for entry, translations in ((24, ENTRY24), (25, ENTRY25)):
        for index, english in sorted(translations.items()):
            key = f"MSG/MESPAK02.PAK:{entry:03d}:{index:05d}"
            if key not in records:
                raise KeyError(key)
            if key in existing:
                raise ValueError(f"Already translated: {key}")
            row = records[key]
            expected = "Story and dialogue"
            if category(row) != expected:
                raise ValueError(f"Unexpected category for {key}: {category(row)}")
            sources = ["Original Japanese ROM"]
            review_note = "Direct dialogue translation; in-game substitutions are retained."
            if entry == 24 and index in (32, 33, 34, 35):
                sources.extend((dawn_dusk_url, marineangemon_url))
                review_note += " MarineAngemon's Ocean Love follows its established English move name in Dawn/Dusk."
            if entry == 25 and index in (0, 1, 2, 3, 4):
                sources.extend((hangyomon_url, world3_equipment_url))
                review_note += " Hangyomon's weapon is Torrent in the reference profile and the older English Digimon World 3 equipment list."
            if entry == 25 and index in (15, 16, 17, 18):
                sources.extend((dawn_dusk_url, airdramon_url))
                review_note += " Airdramon's Spinning Needle follows its established English move name."
            blocks.append({
                "archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": expected,
                "english": [english], "sources": sources,
                "review_note": review_note,
            })
            seen.add(key)
    destination.write_text(json.dumps({
        "description": (
            "Farm Island and character dialogue: Shoutmon's banter, quizzes, "
            "field-skill tips, farm-goods reactions, and the General's quiz."
        ),
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = [
        "# Batch 63 review", "",
        f"Added {len(blocks)} dialogue slots from MESPAK02 entries 24 and 25.",
        "This set covers Shoutmon-style banter, Farm Island interactions, field skills, attribute tips, and the General's knowledge quiz. Names use the established project glossary. Ocean Love and Spinning Needle were checked against earlier English game usage. Hangyomon's spear is Torrent, not the literal misreading 'Trent' or the tempting guess 'Hangyomon Spear'.",
        "Longer replies are rewrapped by the build's 15-column story renderer; all ^-parameter substitutions are preserved.",
        "",
        "Move-name cross-check: [Dawn and Dusk attack list](" + dawn_dusk_url + "); [MarineAngemon](" + marineangemon_url + "); [Airdramon](" + airdramon_url + "). Hangyomon's weapon: [reference profile](" + hangyomon_url + ") and [Digimon World 3 equipment list](" + world3_equipment_url + ").",
        "",
        "| String ID | Japanese | English | Review note |",
        "|---|---|---|---|",
    ]
    for key in sorted(seen):
        row = records[key]
        english = next(b["english"][0] for b in blocks
                       if b["entry"] == row["entry"] and b["start"] == row["index"])
        cell = lambda s: s.replace("|", "\\|").replace("\n", "<br>")
        review.append(f"| `{key}` | {cell(row['source'])} | {cell(english)} | Direct Japanese-to-English translation; source strings and control parameters retained. |")
    (ROOT / "translations/review_batch63.md").write_text(
        "\n".join(review) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
