"""Translate the next set of DigiFarm scenes: the strength-training Digimon."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"

FARM: dict[tuple[int, int], str] = {
    (4, 85): "Oh, no! I've gotten\nway too fat...!\nHow could this\nhappen to me...?",
    (4, 86): "A belt machine, huh?\nThis is pointless,\nbut I may as well\ngive it a try.",
    (4, 87): "That was better\nexercise than I\nexpected... My Max HP\nwent up a bit!",
    (4, 88): "I... I can't stop\nshaking... I guess\nI failed...",
    (4, 89): "A treadmill, huh?\nAll right! I'll get\npumped and go for\na run!",
    (4, 90): "Exercise feels great!\nMy Max HP went up\na lot, too!",
    (4, 91): "I can't believe\nI got worn out\nfrom just that...",
    (4, 92): "This looks like a\ncrystal ball. The\ninside's clear...\nPretty, isn't it?",
    (4, 93): "Huh? I think I saw\nsomething inside...\nMy Max MP went up\na little, too.",
    (4, 94): "Nothing happened.\nOh, well...",
    (4, 95): "What's this...?\nI'll take a look...\nCould it be a\ntarot card?",
    (4, 96): "Whoa! I can feel\nmagical power flowing\nthrough me... My Max MP\nwent up a bit!",
    (4, 97): "Nothing happened...\nThat's a little\ndisappointing.",
    (4, 98): "A pyramid, huh...?\nLooks interesting.\nMaybe I'll go inside\nfor a bit...",
    (4, 99): "Whoa! Pyramid power\nis flowing through me...\nMy Max MP went up\na lot!",
    (5, 0): "I got lost...\nHow could I do that...?",
    (5, 1): "A punching bag!\nPerfect for some\nattack training.",
    (5, 2): "I'm tired, but that\nwent pretty well...\nMy Attack went up\na little!",
    (5, 3): "That didn't go\nthe way I wanted...\nI guess I failed.",
    (5, 4): "A training tree!\nSince it's here,\nI may as well\ngive it a try...",
    (5, 5): "That went pretty\nwell this time...\nMy Attack went up\na bit!",
    (5, 6): "O-ow... My body's\nhurting... How\npathetic...",
    (5, 7): "Whoa! What a huge\nrock! This should\nbe fun. I'll move\nit myself!",
    (5, 8): "See? That was easy!\nMy Attack went up\na lot, too!",
    (5, 9): "Ugh... It's heavy...\nI can't move it\nat all...",
    (5, 10): "This looks like\na punching machine...\nAll right! Come on!\nI'll take you on!",
    (5, 11): "This is nothing\nfor me... My Defense\nwent up a little!",
    (5, 12): "Ouch! That really\nhurts! Isn't this\na little too much?!",
    (5, 13): "A training cannon...\nLet's see if I can\nhandle a little\npractice...",
    (5, 14): "I did it! That was\neasy! My Defense\nwent up a bit!",
    (5, 15): "Ow! That hurts!\nCould you go\neasier on me...?",
    (5, 16): "So I just have to\ncatch this thing!",
    (5, 17): "This is no problem!\nMy Defense went\nway up!",
    (5, 18): "N-no! It hurts too\nmuch! I can't take\nany more!",
    (5, 19): "A book, isn't it?\nI haven't read one\nin ages... Maybe\nI'll give it a try.",
    (5, 20): "This book's pretty\ninteresting! I'm calmer,\nand my Wisdom went up.\nTwo for one!",
    (5, 21): "I should read when\nI have more time\nto relax...",
    (5, 22): "Why is there a\nstudy desk here?\nIt's not that I hate\nstudying, but...",
    (5, 23): "Study time's over!\nMy Wisdom went up!",
    (5, 24): "...\nI was lying before.\nI hate studying!",
    (5, 25): "A magic circle...\nWhat kind of spell\nis this supposed\nto be?",
    (5, 26): "Whoa... My head\nand heart feel clear!\nMy Wisdom went way\nup, too!",
    (5, 27): "If magic could make\nwishes come true,\nlife would be easy...",
    (5, 28): "Side-to-side jumps,\nhuh? All right,\nI'll give it a try...",
    (5, 29): "That was nothing!\nMy Speed went up\na little!",
    (5, 30): "Huff... I'm tired...\nThat was tougher\nthan I thought...",
    (5, 31): "A trampoline!\nMaybe I'll bounce\naround for a bit...",
    (5, 32): "Bouncing around\nwas a lot of fun!\nMy Speed went up\na bit, too!",
    (5, 33): "I jumped too much...\nNow I feel sick...",
    (5, 34): "A running wheel...?\nAm I supposed to\nrun inside it?",
    (5, 35): "That was a good\nworkout! I feel great.\nMy Speed went up\na lot!",
    (5, 36): "Ugh... I can't...\nI'm getting dizzy...",
    (5, 37): "A Digimon keychain!\nI'll give it a try,\njust for fun...",
    (5, 38): "That was even more\nfun than I thought!\nMy Friendship went\nup a little!",
    (5, 39): "That was fun, but\nit's hard... I need\nto keep practicing.",
    (5, 40): "A cell phone...",
    (5, 41): "Taiki replied!\nMy Friendship went\nup a bit!",
    (5, 42): "Taiki hasn't replied...\nThat's too bad...",
    (5, 43): "That's Taiki's digital\ncamera. Maybe I'll\ntake a picture of\nmyself...",
    (5, 44): "There! I hope Taiki\ngets to see it...\nMy Friendship went\nway up!",
    (5, 45): "Darn! I didn't make\nit in time... I failed.",
    (5, 46): "A ring of fire...\nI'm free right now.\nMaybe I'll try it...",
    (5, 47): "I did it! That was\neasy! My EXP went\nup a bit...",
    (5, 48): "Hot, hot! Oh, no...\nI failed!",
    (5, 49): "A Fire Road...\nIt looks pretty hot.\nIf I stay calm,\nI should be fine...",
    (5, 50): "This heat is nothing!\nMy EXP went up\na little...",
    (5, 51): "W-whoa! It's hot!\nI can't handle this!",
    (5, 52): "Fireworks! All right,\nI'll launch them!",
    (5, 53): "Not bad! Those\nfireworks looked great!\nMy EXP went up\na lot!",
    (5, 54): "Nothing happened...\nDid I fail...?",
    (5, 55): "That's a big ball!\nI just have to\nclimb on and move,\nright...?",
    (5, 56): "See? I mastered it\nin no time! My EXP\nwent up a little...",
    (5, 57): "I can't believe\nI couldn't even do\nthat... How pathetic.",
    (5, 58): "Could this be\ntightrope walking?\nLooks fun! I'll\ngive it a try!",
    (5, 59): "That was easy!\nMy EXP went up\na bit...",
    (5, 60): "No way... How could\nI fail at this...?",
    (5, 61): "A circus tent...\nI'll do a little\ntraining inside!",
    (5, 62): "I cleared everything!\nThat was easy! My EXP\nwent way up...",
    (5, 63): "Darn, I messed up...\nThat was harder\nthan I expected...",
    (5, 64): "A mini shower...\nI'll take a quick\nshower while I'm here...",
    (5, 65): "Ahh, refreshing!\nThat felt great!\nMy EXP went up\na little...",
    (5, 66): "Brr! It's freezing!\nI'm going to catch\na cold!",
    (5, 67): "A mini fishing pond...\nI've got time.\nMaybe I'll try it...",
    (5, 68): "I caught one!\nThat feels great...\nMy EXP went up\na bit...",
    (5, 69): "No bites at all...\nThis is frustrating!",
    (5, 70): "There's a huge\nwaterfall here...\nI'll stand under it\nfor a while...",
    (5, 71): "My mind is quiet...\nI feel so calm.\nMy EXP went way up...",
    (5, 72): "Brr! What is this?\nIt's way too cold!",
    (5, 73): "What's that? It\nsmells wonderful!\nIt must be this\nflower...",
    (5, 74): "That really does\nsmell wonderful!\nMy EXP went up\na little...",
    (5, 75): "A caterpillar?!\nI can't handle\ncaterpillars!",
    (5, 76): "A tree house...\nThis is pretty nice.\nMaybe I'll stay\nhere for a while...",
    (5, 77): "Surrounded by nature,\nthis place is pretty\ncomfortable. My EXP\nwent way up...",
    (5, 78): "It's cramped, hot,\nand empty... This\nis more boring than\nI expected.",
    (5, 79): "A computer! Maybe\nI'll take a look\naround the Internet...",
    (5, 80): "I figured out how\nto use the computer!\nMy EXP went up\na little...",
    (5, 81): "Hmm... No good.\nI don't understand\nany of this...",
    (5, 82): "A solar panel...\nLooks interesting.\nI'll take a look.",
    (5, 83): "Whoa! Electricity\nis flowing through me...\nMy EXP went up\na bit...",
    (5, 84): "N-no! I'm getting\nshocked! This was\na bad idea!",
    (5, 85): "A pinball machine...?\nA game now and then\nisn't so bad...",
    (5, 86): "Look! A new high\nscore! That was easy!\nMy EXP went way up...",
    (5, 87): "Well... It's my\nfirst time, so I\nwas bound to be bad...",
    (5, 88): "Is this a birdhouse?\nI'm curious.\nI'll take a look...",
    (5, 89): "I think I understand\nbirds a little better...\nMy EXP went up\na little...",
    (5, 90): "Too bad... I\ndidn't understand\nanything...",
    (5, 91): "A running high jump!\nSounds fun. I'll\ngive it a try!",
    (5, 92): "That was nothing!\nMy EXP went up\na bit...",
    (5, 93): "I failed... I still\nneed more training...",
    (5, 94): "A diving board...?\nThis looks fun!\nI'll give it a try!",
    (5, 95): "That wasn't scary\nat all! My EXP went\nway up...",
    (5, 96): "Sorry... Maybe\nnext time...",
    (5, 97): "An old phonograph...\nDoes it still work?",
    (5, 98): "That's lovely music...\nI feel so relaxed.\nMy EXP went up\na little...",
    (5, 99): "Looks like it's\nbroken after all...\nWhat a shame...",
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
            "sources": [], "review_note": "Original Japanese DigiFarm report; translated for the training Digimon voice. Text is wrapped to the measured 15-character story line budget."})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "category": "DigiFarm reports", "evidence_url": LOCAL,
            "review_note": "DigiFarm training/result report; stat increases rendered consistently as Attack, Defense, Speed, Wisdom, Max HP/MP, Friendship, and EXP."})
    if len(blocks) != 115:
        raise ValueError(f"Expected 115 farm messages, authored {len(blocks)}")
    path = ROOT / "translations/batch39.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the strength-training Digimon's DigiFarm reactions and rewards.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch39.json").write_text(json.dumps({"batch": 39, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 39 review", "", "Batch 39 translates 115 DigiFarm report lines for the strength-training Digimon, covering exercise equipment, study, friendship activities, and recreational facilities. The original Japanese strings remain available in the review table. Long English lines are wrapped to the game's 15-character story-text budget.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch39.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 39, "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
