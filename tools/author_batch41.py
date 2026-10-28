"""Translate the DigiFarm reports of a shy Digimon and a robotic one."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
FARM: dict[tuple[int, int], str] = {
    # Entry 8: gentle, polite voice.
    (8, 5): "A scale...? I'm\ntrying to lose weight\nright now...",
    (8, 6): "I weigh less than\nbefore! My diet\nworked! My Max HP\nwent up a little!",
    (8, 7): "Oh, no... I've\ngained too much weight!",
    (8, 8): "A belt machine...\nI'll use it to\nget in shape...",
    (8, 9): "That was a good\nworkout... My Max HP\nwent up a bit.",
    (8, 10): "I can't stop shaking...\nMaybe I overdid it...?",
    (8, 11): "A treadmill...\nI'll run a little\nto lose weight...",
    (8, 12): "Whew... I lost\na little weight...\nMy Max HP went\nway up!",
    (8, 13): "Ouch! I got a\ncramp in my leg...",
    (8, 14): "A crystal ball...\nIt's so beautiful...\nI feel like it's\npulling me in!",
    (8, 15): "It flashed... I\nthink I saw something...\nMy Max MP went\nup a little...",
    (8, 16): "But nothing happened...\nMaybe it's just\na decoration...?",
    (8, 17): "There's something here...\nLet's take a look...\nOh, it's a tarot card!",
    (8, 18): "I can feel a\nmagical power...\nMy Max MP went\nup a bit.",
    (8, 19): "But how do I use it?\nI'm not sure...",
    (8, 20): "A pyramid...\nSince I'm here,\nI'll look inside...",
    (8, 21): "I felt a powerful,\nmysterious energy!\nMy Max MP went\nway up!",
    (8, 22): "It's so dark inside...\nI can't see a thing...",
    (8, 23): "A punching bag...\nI'm not very fond\nof practicing attacks...",
    (8, 24): "I got carried away\nand tried so hard...\nHow embarrassing!\nMy Attack went up!",
    (8, 25): "I knew it... I\ndon't like anything\nso rough...",
    (8, 26): "A training tree...\nI wonder if a Digimon\nlike me can do this...",
    (8, 27): "That went better\nthan I expected!\nMy Attack went\nup quite a bit!",
    (8, 28): "I can't do this...\nI'm not good at it...",
    (8, 29): "A huge rock...\nI could never move\nsomething that big...",
    (8, 30): "Oh...? It moved\nmore easily than I\nexpected... My Attack\nwent up a lot!",
    (8, 31): "I... I can't do it...\nIt won't budge...",
    (8, 32): "I-is this a punching\nmachine? I need to\ncatch the punch...?",
    (8, 33): "It hurt, but I\nmanaged to endure it...\nMy Defense went up!",
    (8, 34): "It still hurts!\nPlease stop!",
    (8, 35): "A training cannon...\nD-do I have to catch\nthe ball?",
    (8, 36): "Whew... I managed\nto catch it... My\nDefense went up\na bit...",
    (8, 37): "Aah! It hurts too\nmuch! I can't take it!",
    (8, 38): "O-okay... I just\nhave to catch this?",
    (8, 39): "I'm glad... I caught\nit! My Defense went\nway up...",
    (8, 40): "I'm sorry... I\nreally can't do it...",
    (8, 41): "A bookshelf...?\nI rarely get to\nread here...",
    (8, 42): "It's wonderful to\nread in peace... A\nreal treat for the mind!\nI feel wiser, too!",
    (8, 43): "I can't focus today...\nThe words won't\nstay in my head...",
    (8, 44): "A study desk...\nI'll sit down and\nstudy for a while.",
    (8, 45): "I remembered more\nthan I thought! Studying\nwent well, and my\nWisdom went up.",
    (8, 46): "...Oh, dear...\nWhy do I get sleepy\nwhenever I sit at\na desk?",
    (8, 47): "A magic circle...\nIs it used for a spell?",
    (8, 48): "I don't know if it's\nmagic or my imagination,\nbut I feel much wiser!",
    (8, 49): "It looks like something\nshould happen, but\nnothing does...",
    (8, 50): "Side-to-side jumps...\nI'll give it a try!",
    (8, 51): "I'm actually good\nat this kind of thing!\nMy Speed went\nup a little!",
    (8, 52): "My body's too heavy...\nI can't jump well...",
    (8, 53): "A trampoline...\nI'll play on it\nfor a little while!",
    (8, 54): "Floating in the air\nfeels wonderful! My\nSpeed went up quite\na bit, too!",
    (8, 55): "W-what should I do?\nI'm too heavy to jump...",
    (8, 56): "A running wheel...\nI'll get inside\nand run!",
    (8, 57): "Whew... That was\ngreat exercise! My\nSpeed went way up!",
    (8, 58): "I'm sorry... I'm\ntoo tired to move...",
    (8, 68): "A ring of fire...\nIt's a little scary,\nbut I'll try...",
    (8, 69): "Whew... I did it!\nMy EXP went up\na bit...",
    (8, 70): "I can't do this!\nThere's no way...",
    (8, 71): "A Fire Road...\nDo I really have\nto cross it...?",
    (8, 72): "Whew... It was hot,\nbut I endured it.\nMy EXP went up\na little...",
    (8, 73): "Aah! It's so hot!\nI can't stand it!",
    (8, 74): "Fireworks... It'd\nbe a shame to waste\nthem. I'll launch one!",
    (8, 75): "How beautiful!\nMy EXP went way up!",
    (8, 76): "Did I fail...?\nI'm too scared to\nget any closer...",
    (8, 77): "This ball is huge...\nDo you want me to\nclimb on top of it?",
    (8, 78): "It's fun when you\nkeep your balance...\nMy EXP went up\na little...",
    (8, 79): "I-I can't stop it\nwobbling! It's\nso dangerous!",
    (8, 80): "A tightrope...\nI'm not confident,\nbut I'll try...",
    (8, 81): "I did it! My EXP\nwent up a bit...",
    (8, 82): "I-I'm still scared...\nI'm sorry...",
    (8, 83): "A circus tent...\nI'll go in and learn\na trick...",
    (8, 84): "They praised my act!\nMy EXP went way up!",
    (8, 85): "I'm sorry... I don't\nthink I have any talent...",
    (8, 86): "A mini shower...\nI'm so happy! I\nlove showers!",
    (8, 87): "Ahh, that feels nice!\nI feel refreshed...\nMy EXP went up\na little!",
    (8, 88): "But taking a shower\noutside is embarrassing...",
    (8, 89): "A mini fishing pond...\nI wonder if I can\ncatch a fish...?",
    (8, 90): "I caught one!\nI'm so happy! My\nEXP went up a bit!",
    (8, 91): "I didn't catch one...\nI guess I can't do it...",
    (8, 92): "A big waterfall...\nI'll train my spirit\nunder it...",
    (8, 93): "I focused and\ncalmed my mind...\nMy EXP went way up!",
    (8, 94): "I can't... It hurts\ntoo much!",
    (8, 95): "That smells lovely...\nIt must be coming\nfrom this flower...",
    (8, 96): "The more I look,\nthe more beautiful\nit seems... My EXP\nwent up a little!",
    (8, 97): "A caterpillar?!\nNo! Stay away!",
    (8, 98): "A tree house...\nIt looks lovely. I've\nalways dreamed of\nliving in a place like this!",
    (8, 99): "This house is truly\nwonderful! My EXP\nwent way up!",
    # Entry 9: polite, timid voice followed by a robot's report voice.
    (9, 0): "Living here is\nreally inconvenient...",
    (9, 1): "A computer...\nI'll try connecting\nto the Internet!",
    (9, 2): "There's so much\ninteresting information!\nMy EXP went up\na little!",
    (9, 3): "A-a virus got in!\nThis is bad!",
    (9, 4): "A solar panel...\nI think it turns\nsunlight into power...",
    (9, 5): "I can feel electricity\ncoming from it! My\nEXP went up a bit!",
    (9, 6): "Aah! My body's\nparalyzed!",
    (9, 7): "A pinball machine...\nI'm not very good\nat games...",
    (9, 8): "I think I'm getting\nthe hang of it! My\nEXP went way up!",
    (9, 9): "I failed... Game over...",
    (9, 10): "A birdhouse...\nI'll take a peek\ninside to see if\nthere's a bird...",
    (9, 11): "A baby bird was\nasleep inside. So cute!\nMy EXP went up\na little!",
    (9, 12): "There was nothing\ninside... Too bad...",
    (9, 13): "A running high jump...\nI can't jump that high...",
    (9, 14): "I did it! I managed\nto jump! My EXP\nwent up a bit!",
    (9, 15): "I couldn't do it...\nWhat a shame...",
    (9, 16): "A diving board...\nA-am I really supposed\nto jump from here?",
    (9, 17): "I was scared to death,\nbut I found the courage!\nMy EXP went way up!",
    (9, 18): "S-sorry... I can't\ndo it after all!",
    (9, 19): "I think this is called\na phonograph... It\nlooks very old...",
    (9, 20): "What a lovely tone...\nMy EXP went up\na little!",
    (9, 21): "It doesn't seem to\nwork... Too bad...",
    (9, 22): "A Holy Bell...\nIt's so beautiful!\nI'd like to ring it!",
    (9, 23): "It's just as beautiful\nas I imagined... My\nEXP went up a bit!",
    (9, 24): "It won't ring...\nHow disappointing...",
    (9, 25): "Stonehenge...\nI think I'm supposed\nto walk between\nthose stones...",
    (9, 26): "I feel a powerful,\nholy energy! My EXP\nwent way up!",
    (9, 27): "Nothing happened...\nThat's too bad...",
    (9, 28): "S-something's boiling...!",
    (9, 29): "A dark potion! My\nEXP went up a little...",
    (9, 30): "I can't stand this\nsmell! I can't do it!",
    (9, 31): "I sense something\nominous... Could this\nbe a cursed box?",
    (9, 32): "Aah! Such powerful\ndark energy... My EXP\nwent up a bit!",
    (9, 33): "The lid won't open...\nThat's too bad...",
    (9, 34): "Could this be a\nDark Tower? I'll\nget closer and look...",
    (9, 35): "A powerful dark\nenergy is inside me!\nMy EXP went way up!",
    (9, 36): "Nothing happened...\nI must have been\nimagining it!",
    (9, 42): "100 Bits! I'll\nsend them to\nTaiki right away!",
    (9, 44): "500 Bits! Amazing!\nI'll send them to\nTaiki right away!",
    (9, 46): "I can't believe it!\n1,000 Bits! I'll\nsend them to Taiki!",
    (9, 47): "Wild strawberries!\nThey look tasty.\nI'll try one...",
    (9, 48): "Sweet and delicious!\nMy EXP went up\na bit!",
    (9, 49): "It's too sour...\nI can't eat it...",
    (9, 50): "Looks like I can\nclimb this tree...",
    (9, 51): "I did it! I climbed\nit! My EXP went up\na little!",
    (9, 52): "I'm sorry... I'm\ntired...",
    (9, 53): "That's a tree stump,\nright...?",
    (9, 54): "It feels so nice,\nand it's just the\nright firmness! My\nEXP went up a bit!",
    (9, 55): "The bark feels soft,\nbut bumping into it\nreally hurts...",
    (9, 56): "There's some tasty\ntree sap... I'll\ntaste a little.",
    (9, 57): "It's delicious!\nMy EXP went way up!",
    (9, 58): "I-it's bitter!\nIt doesn't taste good!",
    (9, 66): "Huh...? A scale...?\nI'll try weighing\nmyself...",
    (9, 67): "Weight control\nsuccessful! Max HP\nincreased a little!",
    (9, 68): "This weight is bad...\nI've gained too much...",
    (9, 69): "A belt machine...?\nI'll use it to\nget in shape...",
    (9, 70): "Whew... That was\na good workout.\nMax HP went up\na fair bit.",
    (9, 71): "W-what...? My body\nwon't stop shaking!",
    (9, 72): "A treadmill...\nI'll try running\nfor a while.",
    (9, 73): "Whew... That was\ntough, but my Max HP\nwent way up.",
    (9, 74): "Ouch... I overdid it\nand twisted my ankle...",
    (9, 75): "A crystal ball...?\nIt's quite beautiful.",
    (9, 76): "Huh?! I saw\nsomething... My Max MP\nwent up a little.",
    (9, 77): "It is beautiful,\nbut that's all it is.",
    (9, 78): "Why is there a\ntarot card here...?",
    (9, 79): "I sense magical\npower... My Max MP\nwent up a bit.",
    (9, 80): "I don't know how to\nuse tarot cards...",
    (9, 81): "A pyramid... I've\nalways wondered\nwhat's inside...",
    (9, 82): "What was that strange\npower?! My Max MP\nwent way up!",
    (9, 83): "I don't feel any\npyramid power... It's\nso dark inside. I can't\nsee a thing.",
    (9, 84): "A punching bag!\nJust looking at it\nmakes me want to\npunch it...",
    (9, 85): "I got carried away...\nMy Attack went up\na little, at least.",
    (9, 86): "The punching bag\ndoesn't fight back.\nIt's useful training,\nbut not enough alone.",
    (9, 87): "A training tree...?\nHow am I supposed\nto use this thing?",
    (9, 88): "It went better\nthan expected! My\nAttack went up\na fair bit.",
    (9, 89): "I don't get it...\nHow do you train\nwith a thing like this?",
    (9, 90): "A giant rock... Is\nmoving it the training?",
    (9, 91): "It moved more easily\nthan I thought! My\nAttack went way up!",
    (9, 92): "It won't move\nat all...",
    (9, 93): "A punching machine...?\nI just have to catch\nthat punch...",
    (9, 94): "Ouch... That hurt,\nbut I endured it.\nMy Defense went up\na little...",
    (9, 95): "Aah! It hurts!\nNo way! I can't!",
    (9, 96): "A training cannon...?\nDo I have to catch\nthat ball?",
    (9, 97): "Ugh... That hurt...\nI caught it, though.\nMy Defense went up\na bit.",
    (9, 98): "This is impossible...\nI'll break before my\nDefense improves...",
    (9, 99): "I just have to catch\nthis iron ball, right?",
}


def fit(value: str) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=15,
        break_long_words=True, break_on_hyphens=False)) if line else ""
        for line in value.split("\n"))


def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    prior = translate_records(records)
    blocks, review = [], []
    for (entry, index), raw_english in FARM.items():
        key = f"MSG/MESPAK05.PAK:{entry:03d}:{index:05d}"
        if key in prior:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing DigiFarm source: {key}")
        english = fit(raw_english)
        blocks.append({"archive": row["archive"], "entry": entry,
            "start": index, "category": "DigiFarm reports", "english": [english],
            "sources": [], "review_note": "Original Japanese DigiFarm text; shy voice or machine-like narration preserved, with lines wrapped to the 15-character story-text budget."})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "category": "DigiFarm reports", "evidence_url": LOCAL,
            "review_note": "Reward stats use the established Max HP/MP, Attack, Defense, Speed, Wisdom, Friendship, EXP, and Bits wording."})
    if len(blocks) != 172:
        raise ValueError(f"Expected 172 farm messages, authored {len(blocks)}")
    path = ROOT / "translations/batch41.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the remaining shy and robotic DigiFarm reactions, activity reports, and rewards.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch41.json").write_text(json.dumps({"batch": 41, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 41 review", "", "Batch 41 translates 172 DigiFarm report slots for a shy speaker and a machine-like narrator. Training, exercise, facilities, small gifts for Taiki, and reward results follow the Japanese message context. English is wrapped to the 15-character story-text budget.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch41.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 41, "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
