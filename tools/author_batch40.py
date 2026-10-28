"""Translate more DigiFarm scenes, including the diva's reports."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"
FARM: dict[tuple[int, int], str] = {
    # Entry 6: the first voice is earnest; the second is the self-declared star.
    (6, 0): "A Holy Bell, I think...\nSince it's here,\nI'll ring it once.",
    (6, 1): "What a clear,\nbeautiful sound...\nMy EXP went up\na bit...",
    (6, 2): "It didn't ring at all!\nWhat a letdown...",
    (6, 3): "That's Stonehenge...\nLooks interesting.\nMaybe I'll go\ncheck it out...",
    (6, 4): "Whoa! Holy power\nis surging up!\nMy EXP went way up!",
    (6, 5): "It's just some ruins...\nHow boring...",
    (6, 6): "What's this?\nI'll taste it\nand find out...",
    (6, 7): "Ugh! This is a\ndark potion! My EXP\nwent up a little...",
    (6, 8): "Ugh! That tastes\nawful... I feel sick...",
    (6, 9): "What's this...?\nI sense something\nominous... A cursed\nbox, maybe...",
    (6, 10): "Urrgh... That's a\npowerful dark energy...\nMy EXP went up\na bit...",
    (6, 11): "The lid won't open...\nGuess I'll give up...",
    (6, 12): "Could that be\na Dark Tower?\nI'll go take a look!",
    (6, 13): "D-dark power is\nsurging through me...\nMy EXP went way up!",
    (6, 14): "Nothing happened...\nThat was a wasted trip.",
    (6, 15): "What's that? There's\na calm, gentle scent\ncoming from over\nthat way...",
    (6, 16): "Heh, I see... It's\nTaiki's scent. When\nTaiki comes back,\nI'll hang out with him.\nMy Friendship went up!",
    (6, 17): "It's peaceful again\ntoday... Now that I\nthink about it, we can\nlive here safely\nthanks to Taiki.\nI want to thank him.",
    (6, 18): "Taiki, you're the\nbest Tamer! We're\nall grateful to you!\nI hope you heard that.\nMy Friendship went\nway up!",
    (6, 20): "100 Bits... I'll\nsend them to Taiki\nright away. I hope\nthey help him out...",
    (6, 22): "500 Bits... I'll\nsend them to Taiki\nright away. I hope\nhe's happy...",
    (6, 24): "Whoa, 1,000 Bits!\nI'll send them to\nTaiki right away.\nI'm sure he'll be glad!",
    (6, 25): "These look like\nwild strawberries...\nI'll try one...",
    (6, 26): "Sweet and tasty!\nMy EXP went up\na bit...",
    (6, 27): "This tastes awful!\nI can't eat it!",
    (6, 28): "Looks like I can\nclimb the tree here...",
    (6, 29): "That was easy!\nMy EXP went up\na little...",
    (6, 30): "My hand's numb...\nI can't do this...",
    (6, 31): "What a huge stump...\nWhat am I supposed\nto do with it?",
    (6, 32): "I just played around,\nbut my EXP still\nwent up a bit...\nThe tree's feel, smell,\nand result are soothing.",
    (6, 33): "Nothing happened...\nI didn't expect much\nfrom a stump anyway.",
    (6, 34): "Could this be some\ntasty tree sap...?",
    (6, 35): "That sap was tasty!\nMy EXP went way up!",
    (6, 36): "Even if it tastes\ngood, it's still just\ntree sap...",
    (6, 44): "A scale? I don't\nneed to weigh myself.\nI always keep my\nfigure perfect!",
    (6, 45): "There! The perfect\nnumber, of course!\nMy Max HP went up\na little!",
    (6, 46): "Huh?! Th-this can't\nbe right... The scale\nmust be broken!",
    (6, 47): "A treadmill? Maybe\nI'll try it for\na little while...",
    (6, 48): "Hee-hee! My figure\nlooks even better now!\nMy Max HP went up\na bit!",
    (6, 49): "W-what is this?!\nI can't stop shaking!",
    (6, 50): "A treadmill? Why\nshould I have to run?",
    (6, 51): "I've lost weight!\nThat's fine by me!\nMy Max HP went\nway up!",
    (6, 52): "I'm too tired to\nmove! I hate this!",
    (6, 53): "A crystal ball?\nIt's bright, clear,\nand pretty...",
    (6, 54): "What was that?\nIt lit up, right?!\nMy Max MP went up\na little!",
    (6, 55): "If nothing shows up,\nit's just a glass ball.",
    (6, 56): "Oh! A tarot card!",
    (6, 57): "What is this? I can\nfeel a mysterious\npower... My Max MP\nwent up a bit!",
    (6, 58): "I don't care about\nfate or fortunes.\nI'm destined to be\nhappy, after all!",
    (6, 59): "This is a pyramid...\nSo I just go inside?",
    (6, 60): "Pyramid power made\nme stronger! My Max MP\nwent way up!",
    (6, 61): "It's damp and dark!\nThis place is awful!",
    (6, 62): "A punching bag...?\nI hate doing\nuncivilized things!",
    (6, 63): "That actually felt\npretty good! My Attack\nwent up a little!",
    (6, 64): "I hate this sweaty\nthing! It's not\nsuitable for me!",
    (6, 65): "A training tree...?\nFine. I'll do it,\nall right...?",
    (6, 66): "This is getting\nkind of fun! My Attack\nwent up quite a bit!",
    (6, 67): "My body hurts!\nThis is the worst!",
    (6, 68): "What's with this\nhuge rock?! Don't\nexpect me to move it!",
    (6, 69): "It moved so easily!\nI'm amazing! My Attack\nwent way up!",
    (6, 70): "See? I knew I\ncouldn't do it!",
    (6, 71): "Is that a punching\nmachine? I have to\nstop what's coming?\nHow tiresome...",
    (6, 72): "You think this can\nhurt me? My Defense\nwent up a little!",
    (6, 73): "That hurt! What\nare you doing?!",
    (6, 74): "A training cannon?\nThat looks dangerous.\nDo I really have\nto do this?",
    (6, 75): "This is nothing!\nMy Defense went\nup a bit!",
    (6, 76): "That was dangerous!\nHow rude!",
    (6, 77): "You want me to\ncatch that?!",
    (6, 78): "There! I did it!\nMy Defense went\nway up!",
    (6, 79): "Taiki, how could\nyou do that to me?!",
    (6, 80): "A bookshelf...\nMaybe I'll read\na little book...",
    (6, 81): "Reading is nice.\nIt calmed me down,\nand my Wisdom went up.",
    (6, 82): "Not today... I\ncan't concentrate\nat all.",
    (6, 83): "A study desk...?\nDo you expect me\nto study here?",
    (6, 84): "My Wisdom went up\na bit. Though I'm\nalready so smart...",
    (6, 85): "Why should someone\nso perfect and lovely\nhave to study?",
    (6, 86): "A magic circle?\nThat's just a\nsuperstition...",
    (6, 87): "My mind feels\nsharper and sharper...\nMy Wisdom is rising!",
    (6, 88): "See? Nothing happened.\nIt's just a silly\nsuperstition.",
    (6, 89): "Side-to-side jumps?\nFine, I'll do it!",
    (6, 90): "Wasn't that elegant?\nMy Speed went up\na little!",
    (6, 91): "Oh, no! I twisted\nmy ankle! Don't make\nme do such dull\nexercise again!",
    (6, 92): "A trampoline...?\nI'll show you my\nbrilliant technique!",
    (6, 93): "Perfect! That was\nflawless! My Speed\nwent up a bit!",
    (6, 94): "I twisted my ankle!\nThis is the worst!",
    (6, 95): "A running wheel?\nWhat am I meant to do?\nOh, run inside it?\nFine, I'll do it!",
    (6, 96): "That was better\nexercise than I\nexpected! My Speed\nwent way up!",
    (6, 97): "This is ridiculous!\nI'm not doing it again!",
    (6, 98): "A Digimon keychain!\nThat looks fun. Let\nme try it, too!",
    (6, 99): "This is so much fun!\nIt's the best! My\nFriendship went up!",
    # Entry 7: continuation of the vain character's reports.
    (7, 0): "This is hard!\nIt's so much fun,\nthough...",
    (7, 1): "A cell phone! I'll\nsend Taiki a message.\nYou'd better be\ngrateful!",
    (7, 2): "He replied! Of course\nhe did! My Friendship\nwent up quite a bit!",
    (7, 3): "Taiki didn't reply?\nHe's the worst!",
    (7, 4): "A digital camera...\nTaiki left it here.\nI'll let him take\none picture of me!",
    (7, 5): "Perfect! My beauty\nlooks flawless! My\nFriendship went way up!",
    (7, 6): "This camera must\nbe broken!",
    (7, 7): "Wait... You don't\nexpect me to jump\nthrough this ring\nof fire, do you?",
    (7, 8): "I did it! That was\neasy for me! My EXP\nwent up a fair bit!",
    (7, 9): "No! I hate this!\nI don't want to do it!",
    (7, 10): "This Fire Road...\nYou expect me to\nwalk across it?",
    (7, 11): "How was that? Easy!\nMy EXP went up\na little!",
    (7, 12): "Ow! That's awful!\nThis is the worst!",
    (7, 13): "Fireworks... Do you\nwant me to launch them?",
    (7, 14): "They're as beautiful\nas I am! My EXP\nwent way up!",
    (7, 15): "They didn't launch?\nHow disappointing...",
    (7, 16): "What's this huge ball?\nYou want me to ride\non it?",
    (7, 17): "Easy! My EXP went\nup a little!",
    (7, 18): "I can't stay on!\nI've had enough!",
    (7, 19): "Is that tightrope\nwalking? So I just\nwalk across it...?",
    (7, 20): "Did you see my\ngraceful balance?\nMy EXP went up\na bit!",
    (7, 21): "That rope is too high,\ntoo thin, and too\nwobbly!",
    (7, 22): "A circus tent? I\ntrain here? I'll be\na star anywhere!",
    (7, 23): "Everyone's charmed\nby me! My EXP went\nway up!",
    (7, 24): "W-what was that\ntraining?! It was\nway too hard!",
    (7, 25): "A mini shower!\nThis is perfect.\nI'll take a quick\nshower...",
    (7, 26): "Ahh, refreshed!\nThat feels wonderful!\nMy EXP went up\na little!",
    (7, 27): "C-cold! What is this?!\nI'm going to freeze!",
    (7, 28): "A mini fishing pond?\nThat'll be a nice\nway to pass the time...",
    (7, 29): "Even the fish can't\nresist my charm! My\nEXP went up a bit!",
    (7, 30): "No bites... This is\nso boring!",
    (7, 31): "A huge waterfall\nout here... Am I\nsupposed to train\nhere?",
    (7, 32): "I feel so refreshed!\nMy EXP went way up!",
    (7, 33): "Ugh! My hair's\na complete mess!",
    (7, 34): "That smells lovely...\nThe scent must be\ncoming from that flower.",
    (7, 35): "It looks and smells\nwonderful, just like me!\nMy EXP went up\na little!",
    (7, 36): "A caterpillar!\nThat's disgusting!",
    (7, 37): "A tree house!\nIt's lovely! A place\nfit for me to live!",
    (7, 38): "Just as I thought,\nit's the perfect place!\nMy EXP went way up!",
    (7, 39): "It's less convenient\nthan I expected...\nHow disappointing!",
    (7, 40): "A computer! Maybe\nI'll look around\non the Internet...",
    (7, 41): "I found some useful\ninformation! And my\nEXP went up a bit!",
    (7, 42): "How do you even\nturn this thing on?",
    (7, 43): "A solar panel...?\nHmm... And what\nexactly is this\nsupposed to do?",
    (7, 44): "Is it charging me\nwith electricity?!\nMy EXP went up\na bit!",
    (7, 45): "W-wait! I'm getting\nshocked! Turn it off!",
    (7, 46): "A pinball machine?\nI'll play to pass\nthe time...",
    (7, 47): "This is more fun\nthan I expected!\nMy EXP went way up!",
    (7, 48): "What's fun about this?\nI don't get it...",
    (7, 49): "A birdhouse...?\nI love pretty birds!",
    (7, 50): "I saw a beautiful\nbird, just like me!\nMy EXP went up\na little!",
    (7, 51): "There was nothing\nthere... Oh well.",
    (7, 52): "A running high jump?\nYou think I can't\njump that high?",
    (7, 53): "My jump charmed\neveryone! My EXP\nwent up a bit!",
    (7, 54): "That didn't count!\nThe bar was too high!",
    (7, 55): "A diving board...?\n...Fine! You want\nme to jump, right?",
    (7, 56): "I-I wasn't scared!\nMy EXP went way up,\nthat's all!",
    (7, 57): "I-I'll stop for today!\nI-I'm not scared!",
    (7, 58): "A phonograph...?\nIt's so old. Does\nit even work?",
    (7, 59): "Wonderful! You can\nmake it my theme song.\nMy EXP went up\na little!",
    (7, 60): "It won't work...\nIt's just decoration.",
    (7, 61): "A Holy Bell! If I\nring it, it'll make\na beautiful sound!",
    (7, 62): "Such a holy,\nbeautiful sound...\nMy EXP went up\na bit!",
    (7, 63): "It didn't ring...\nHow can that be?!",
    (7, 64): "Stonehenge, huh?\nWhat happens if\nI walk between\nthose stones?",
    (7, 65): "Holy power is\nrising up! My EXP\nwent way up!",
    (7, 66): "Nothing happened...\nWhat a letdown!",
    (7, 67): "Ugh! What is this?\nThe worst!",
    (7, 68): "A dark potion?!\nMy EXP went up\na little!",
    (7, 69): "That's enough!\nLet's get out of here!",
    (7, 70): "What's that...?\nSomething feels odd...\nIs that a cursed box?!",
    (7, 71): "I can feel it...\nThe power of darkness!\nMy EXP went up\na bit!",
    (7, 72): "This box won't open!\nI'll have to leave it...",
    (7, 73): "A Dark Tower?!\nFine, I'll inspect it!",
    (7, 74): "It's definitely a\nDark Tower! My EXP\nwent way up...",
    (7, 75): "I don't feel anything.\nThat's kind of boring...",
    (7, 76): "What's that? A sweet,\nlovely scent is coming\nfrom over there...",
    (7, 77): "That's Taiki's scent!\nWhen he comes back,\nI'll keep him company.\nMy Friendship went up!",
    (7, 78): "I've been so happy\nlately! That's only\nnatural, of course...\nBut Taiki's been\nworking hard, too.\nI'll praise him this\nonce, as a special treat!",
    (7, 79): "Taiki, you're doing\npretty well! Keep it up\nand keep serving me!\nYou heard me, right?\nMy Friendship went\nway up!",
    (7, 81): "100 Bits! I'll send\nthem to Taiki right\naway. He'll be\ngrateful to me!",
    (7, 83): "500 Bits! Lucky me!\nI'll send them to\nTaiki. He'll respect\nme even more!",
    (7, 85): "1,000 Bits! How\nwonderful! I'll send\nthem to Taiki. Maybe\nhe'll worship me!",
    (7, 86): "Wild strawberries!\nThey look delicious.\nI'll try one!",
    (7, 87): "That was tasty!\nIt passes my test!\nMy EXP went up\na bit!",
    (7, 88): "Ugh! So sour! Why\nwould you feed me\nthat?!",
    (7, 89): "Looks like I could\nclimb this tree...",
    (7, 90): "It's nice being\nup high! My EXP\nwent up a little!",
    (7, 91): "Don't make me do\nsomething so crude!",
    (7, 92): "Is this a tree stump?",
    (7, 93): "It brought out my\nstrength! My EXP\nwent up a bit!",
    (7, 94): "I bumped into a stump\nand nothing happened...\nNo story, no excitement!",
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
            "sources": [], "review_note": "Original Japanese DigiFarm report; translated in the speaker's distinct voice and wrapped to the 15-character story line budget."})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "category": "DigiFarm reports", "evidence_url": LOCAL,
            "review_note": "DigiFarm reaction/reward text. Stats and rewards use the established Attack, Defense, Speed, Wisdom, Max HP/MP, Friendship, EXP, and Bits terms."})
    if len(blocks) not in (181, 182):
        raise ValueError(f"Expected around 181 farm messages, authored {len(blocks)}")
    path = ROOT / "translations/batch40.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps({"description": "Translate the earnest and theatrical DigiFarm Digimon reports, including training, facility, friendship, and Bits events.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch40.json").write_text(json.dumps({"batch": 40, "translated_slots": len(blocks), "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 40 review", "", f"Batch 40 translates {len(blocks)} DigiFarm report slots. The Japanese records contain two distinct voices: an earnest Digimon and a vain, theatrical one. Stat rewards and Taiki's name follow the project glossary. Dialogue is wrapped to the measured 15-character line budget.", "", "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch40.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 40, "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
