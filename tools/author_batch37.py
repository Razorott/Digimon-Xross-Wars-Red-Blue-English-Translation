"""Translate the remaining equipment, shop, communications, and trait UI labels."""
from __future__ import annotations

import csv
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = "Original Japanese ROM (local primary source)"

MAPS: dict[tuple[int, int], str] = {}

def put(entry: int, values: dict[int, str]) -> None:
    for index, english in values.items():
        key = (entry, index)
        if key in MAPS:
            raise ValueError(f"Duplicate authored menu index: {key}")
        MAPS[key] = english


put(0, {425: "Party includes an A-Troiamon with the Affectionate trait."})

# The map strings use letter prefixes from the game's own zone names. "Yobi"
# is a reserved/placeholder route label, so it is rendered as TBD.
put(8, {
    10: "Unused 0", 11: "Unused 1", 12: "Unused 2",
    13: "Whirlpool IN 1", 14: "Whirlpool IN 2", 15: "Whirlpool IN 3",
    16: "Whirlpool IN 4", 17: "Whirlpool IN 5",
    18: "Whirlpool OUT 1", 19: "Whirlpool OUT 2", 20: "Whirlpool OUT 3",
    21: "Whirlpool OUT 4", 22: "Whirlpool OUT 5",
    28: "K Tunnel 1", 29: "K Tunnel 4", 30: "F Grassland 1",
    31: "G Amazon West 3", 32: "C Cave 1", 33: "C Cave 4",
    34: "C Mountain 1", 35: "C Volcano East 5", 36: "K Underground Passage",
    37: "K Ruins West 2", 38: "K Ruins West 4", 40: "P Desert North 2",
    41: "P Desert North 3", 42: "C Volcano Underground", 43: "C Volcano West 3",
    44: "C Volcano West 4", 46: "S Valley North 2", 47: "S Valley North 5",
    48: "Underground TBD 1", 49: "Underground TBD 2", 50: "Underground TBD 3",
    53: "D Icefield West 2", 56: "D Icefield East 3", 57: "D Icefield East 2",
    63: "Underwater TBD 1", 64: "Underwater TBD 2", 65: "Underwater TBD 3",
    66: "D Space East 1", 67: "G Amazon East 2", 68: "K Ruins West 1",
    69: "D Space East 4", 71: "L Space South 2", 72: "L Space South 3",
    73: "L Space South 4", 74: "L Space North 1", 75: "L Space North 2",
    76: "L Space North 3", 77: "L Space North 4", 78: "L Space North 5",
    79: "L Space North 6", 84: "Warp TBD 3", 85: "Boulder",
    86: "Great Tree", 87: "Ice", 88: "Technique TBD",
})

put(10, {
    0: "Weapon Novice", 1: "Weapon Disciple", 2: "Weapon Adept",
    3: "Weapon Master", 4: "Weapon Artisan", 5: "Armor Novice",
    6: "Armor Disciple", 7: "Armor Adept", 8: "Armor Master",
    9: "Armor Artisan",
})
put(11, {
    0: "Creates an ordinary\nweapon at random.",
    1: "Creates a decent\nweapon at random.",
    2: "Creates a good\nweapon at random.",
    3: "Creates a fine\nweapon at random.",
    4: "Creates an excellent\nweapon at random.",
    5: "Creates ordinary\narmor at random.",
    6: "Creates decent\narmor at random.",
    7: "Creates good\narmor at random.",
    8: "Creates fine\narmor at random.",
    9: "Creates excellent\narmor at random.",
})

_gear = [
    ("Iron Dumbbell", "Iron Dumbbells"), ("Circle", "Circles"),
    ("Glove", "Gloves"), ("Shield", "Shields"), ("Watch", "Watches"),
    ("Textbook", "Textbooks"), ("Torch", "Torches"), ("Whip", "Whips"),
    ("Saint", "Saints"), ("Black Mist", "Black Mists"),
    ("Stun Gun", "Stun Guns"), ("Pistol", "Pistols"),
    ("Tornado", "Tornadoes"), ("Fan", "Fans"),
    ("Watering Can", "Watering Cans"),
]
put(12, {group * 3 + tier_index: f"{tier} {base}"
         for group, (base, _plural) in enumerate(_gear)
         for tier_index, tier in enumerate(("Mega", "Giga", "Tera"))})

_stat_rows = [
    ("Max HP", ("a little", "some", "a lot"), (5000, 7000, 9999)),
    ("Max MP", ("a little", "some", "a lot"), (5000, 7000, 9999)),
    ("ATK", ("a little", "some", "a lot"), (500, 700, 1000)),
    ("DEF", ("a little", "some", "a lot"), (500, 700, 1000)),
    ("SPD", ("a little", "some", "a lot"), (500, 700, 1000)),
    ("INT", ("a little", "some", "a lot"), (500, 700, 1000)),
]
_effects: dict[int, str] = {}
for group, (stat, levels, caps) in enumerate(_stat_rows):
    for level, (amount, cap) in enumerate(zip(levels, caps)):
        _effects[group * 3 + level] = f"Raises {stat} {amount}.\n(Max. {cap})"
_exp_groups = ["Mythical Beast", "Beast", "Angel", "Demon", "Machine",
               "Aquatic", "Bird", "Insect", "Plant"]
for group, family in enumerate(_exp_groups):
    for level, amount in enumerate(("a little", "some", "a lot")):
        family_line = "Mythical Beasts get 2x EXP." if family == "Mythical Beast" else f"{family} Digimon get 2x EXP."
        _effects[18 + group * 3 + level] = f"{amount.capitalize()} more EXP.\n{family_line}"
put(13, _effects)

put(18, {
    0: "Buy equipment", 1: "Buy consumables", 4: "Sell equipment",
    5: "Sell consumables", 6: "Sell farm goods", 12: "Upgrade terrain board",
    13: "Upgrade music board", 15: "How many ^0?", 17: "How many ^0 to sell?",
    19: "Buy ^1 ^0?", 20: "Yes, buy it", 22: "Sell ^1 ^0?",
    23: "Yes, sell it", 25: "Bought ^1 ^0.", 26: "Sold ^1 ^0.",
    27: "Upgrade ^0 to max?", 28: "Upgrade ^0 to Lv. ^1?",
    29: "Yes, upgrade it", 56: "A Digimon has it equipped; none left to sell!",
    57: "It's set on a DigiFarm; none left to sell!",
    58: "Not enough Bits to upgrade!", 60: "Price", 62: "x",
})

put(21, {
    1: "Your user name", 2: "Close the\nCommunication Box?",
    5: "A user name is required\nfor the Communication Box.\nChoose one.",
    6: "Use '^0' as\nyour user name?", 9: "Choose an option.",
    10: "Trade Melodies", 11: "Send DigiScores", 12: "Receive DigiScores",
    13: "Change User Name",
    14: "Trade a Melody with friends.\nYour Melodies leave\nyour collection.",
    15: "Share your DigiScores\nwith nearby friends.",
    16: "Get a friend's DigiScore.\nProgress may prevent\nsome score transfers.",
    17: "Change your user name", 18: "Not ready yet.",
    19: "You have no Melodies\nto trade!", 20: "You have no DigiScores\nto send!",
    21: "Choose a connection method.", 22: "Wait for a friend", 23: "Find a friend",
    24: "Use DS Wireless to let\na friend connect to your DS.",
    25: "Connect to a friend's DS\nwith DS Wireless.",
    26: "Max. / ATK / INT / SPD / DEF",
    27: "Lv. ^0 / ^1 / ^2 / ^3 / ^4",
    28: "Lv. -- / ---- / ----\n---- / ----",
    30: "Choose the Melody\nyou want to give.", 32: "Reorder menu",
    37: "You can't give away\nthat Melody yet.",
    38: "^0 can't receive\nthat Melody yet.",
    39: "^0 can't receive\nany more of that Melody.",
    40: "How many ^0\nwill you give?", 41: "You can give up to ^1.",
    42: "Give ^1 ^0?", 43: "Yes, give it", 45: "^0 is choosing.\nPlease wait.",
    46: "Trade with these settings?", 49: "Trading Melodies...\nSaving.\nDo not turn off the power.",
    50: "Melody traded!\nContinue trading?", 51: "Yes, continue", 52: "No, finish",
    53: "Continue trading", 54: "Finish trading",
    55: "^0 ended the trade.\nClosing the trade.", 56: "Owned Scores",
    65: "Choose a DigiScore to send.\nYou can't send a score\nthe other player owns.",
    66: "This DigiScore can't\nbe sent yet.", 67: "Send this DigiScore?",
    68: "Send this DigiScore?\n\n[!] The other player may be\nunable to receive it, depending\non their game progress.",
    69: "Yes, send this DigiScore", 71: "Sending DigiScore...\n^0",
    72: "Sending item...\n^0 x^1", 73: "Sending Melody...\n^0 x^1",
    74: "Searching for DigiScores\nyou can receive...",
    75: "Searching for DigiScores\nyou can receive...\nIf it fails, go back\nand try again.",
    76: "Received a DigiScore\nfrom ^0!\n^1", 77: "Received an item\nfrom ^0!\n^1 x^2",
    78: "Received a Melody\nfrom ^0!\n^1 x^2",
    79: "You already received\n^1 from ^0.",
    80: "You already received\n^1 x^2 from ^0.",
    81: "You already received\n^1 x^2 from ^0.",
    82: "Start DS Wireless?", 85: "DS Wireless is unavailable.",
    86: "An error occurred.\nTurn off the power, then retry.",
    87: "Searching for a partner...", 88: "Waiting for a partner...",
    89: "Found ^0!\nStart connecting?", 92: "Waiting for a response.\nPlease wait.",
    93: "Waiting for their decision.\nPlease wait.", 94: "Please wait.",
    95: "!!!!!! COMMUNICATION ERROR !!!!!!\nConnection lost.",
    96: "COMMUNICATION ERROR\nCould not connect to\nother player.",
    97: "Other player disconnected.\nEnding communication.",
    98: "End DS Wireless?", 101: "User Name", 104: "You", 105: "Other Player",
})

COMMON = {
    "ダミーなまえ": "Dummy Name", "？？？？": "????",
    "－－－－－－－－－": "---------", "なし": "None",
    "シャッフルかわし": "Shuffle Dodge", "シャッフルパリィ": "Shuffle Parry",
    "シャッフルアンチ": "Shuffle Resist", "シャッフルふせぎ": "Shuffle Block",
    "シャッフルはじき": "Shuffle Reflect", "シャッフルニガテ": "Shuffle Weakness",
    "ポイズンかわし": "Poison Dodge", "ポイズンパリィ": "Poison Parry",
    "ポイズンアンチ": "Poison Resist", "ポイズンふせぎ": "Poison Block",
    "ポイズンはじき": "Poison Reflect", "ポイズンニガテ": "Poison Weakness",
    "カースかわし": "Curse Dodge", "カースパリィ": "Curse Parry",
    "カースアンチ": "Curse Resist", "カースふせぎ": "Curse Block",
    "カースはじき": "Curse Reflect", "おまもり": "Protection",
    "しゅごのおふだ": "Guardian Talisman", "ふせぎのことだま": "Ward Charm",
    "とくこうはじき": "INT Reflect", "とくこうけっかい": "INT Barrier",
    "みかわし": "Dodge", "みかわしのまい": "Evasive Dance",
    "かいひニガテ": "Evasion Weakness", "かんさつがん": "Watchful Eye",
    "しんがん": "Mind's Eye", "めいちゅうニガテ": "Accuracy Weakness",
    "ひっさつ": "Critical Hit", "ハイクリティカル": "High Critical",
    "ひっさつニガテ": "Critical Weakness", "にげあし": "Escape Artist",
    "にげるがかち": "Run to Win", "とんずらニガテ": "Fleeing Weakness",
    "まひつかい": "Paralysis Adept", "まひたつじん": "Paralysis Master",
    "ねむりつかい": "Sleep Adept", "ねむりたつじん": "Sleep Master",
    "こんらんつかい": "Confusion Adept", "こんらんたつじん": "Confusion Master",
    "くらやみつかい": "Darkness Adept", "くらやみたつじん": "Darkness Master",
    "ＨＰドレちしき": "HP Drain Knowledge", "ＨＰドレスペル": "HP Drain Spell",
    "ＭＰドレちしき": "MP Drain Knowledge", "ＭＰドレスペル": "MP Drain Spell",
    "ポイズンちしき": "Poison Knowledge", "ポイズンスペル": "Poison Spell",
    "カースちしき": "Curse Knowledge", "カーススペル": "Curse Spell",
    "いやしのて": "Healing Hand", "いやしのはどう": "Healing Wave",
    "ヒーリングオーラ": "Healing Aura", "ＨＰドレイナー": "HP Drainer",
    "ライフイーター": "Life Eater", "ＭＰドレイナー": "MP Drainer",
    "メンタルイーター": "Mind Eater", "どくのて": "Poison Touch",
    "どくのうみ": "Poison Sea", "ポイズンジェイル": "Poison Prison",
    "ＭＰせつやく": "MP Saver", "ＭＰだいせつやく": "MP Super Saver",
    "ワザのつかいて": "Skill User", "ワザマスター": "Skill Master",
    "メロディハート": "Melody Heart", "メロディだましい": "Melody Soul",
    "ソウルシンガー": "Soul Singer", "アイテムずき": "Item Lover",
    "コレクター": "Collector", "おかねずき": "Money Lover",
    "かねもち": "Rich", "だいふごう": "Tycoon", "ラッキー": "Lucky",
    "メガラッキー": "Mega Lucky", "７ふくじん": "Seven Lucky Gods",
    "Ｄエンテレケイア": "D-Entelecheia", "たんけんか": "Explorer",
    "たんけんリーダー": "Explorer Leader", "たんけんニガテ": "Exploration Weakness",
    "かじやみならい": "Blacksmith Apprentice", "かじやのたくみ": "Master Blacksmith",
    "おしごとニガテ": "Work Weakness",
    "テストわざ１Ｌ": "Test Skill 1 L", "テストわざ２Ｌ": "Test Skill 2 L",
    "テストわざ３Ｌ": "Test Skill 3 L", "テストわざ４Ｌ": "Test Skill 4 L",
    "テストわざ５Ｌ": "Test Skill 5 L",
}


def wrap_ui(value: str, width: int = 30) -> str:
    return "\n".join("\n".join(textwrap.wrap(line, width=width,
        break_long_words=True, break_on_hyphens=False)) if line else ""
        for line in value.split("\n"))


def main() -> None:
    records = collect_messages(Rom(rom_paths()["blue"]))
    prior = translate_records(records)
    blocks, review, seen = [], [], set()

    def add(key: str, english: str, category: str, note: str,
            width: int | None = None) -> None:
        if key in prior or key in seen:
            raise ValueError(f"Already translated or duplicate: {key}")
        row = records.get(key)
        if row is None or not row["source"].strip():
            raise ValueError(f"No source text at {key}")
        english = wrap_ui(english, width) if width else english
        seen.add(key)
        blocks.append({"archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": category, "english": [english],
            "sources": [], "review_note": note})
        review.append({"id": key, "japanese": row["source"], "english": english,
            "category": category, "review_note": note})

    menu_note = ("UI copy translated from the Japanese game strings. Existing "
        "control substitutions are preserved; equipment tiers, stat caps, "
        "Bits, DigiScore, Melody, and DS Wireless wording are kept consistent.")
    menu_count = 0
    for (entry, index), english in MAPS.items():
        key = f"MSG/MESPAK01.PAK:{entry:03d}:{index:05d}"
        add(key, english, "Menus, quests and battle prompts", menu_note, width=30)
        menu_count += 1
    if menu_count != 267:
        raise ValueError(f"Expected 267 menu records, authored {menu_count}")

    trait_note = ("Common trait and resistance label translated to match the "
        "game's existing HP, MP, ATK, INT, SPD, DEF, and status terminology.")
    queue = list(csv.DictReader((ROOT / "translations/work_queue.tsv").open(
        encoding="utf-8-sig"), delimiter="\t"))
    common_rows = {(row["category"], row["japanese"]): row for row in queue}
    for japanese, english in COMMON.items():
        group = common_rows.get(("Common labels and traits", japanese))
        if group is None:
            raise ValueError(f"No matching common label: {japanese}")
        for key in group["ids"].split(";"):
            add(key, english, "Common labels and traits", trait_note)
    if len(COMMON) != 91:
        raise ValueError(f"Expected 91 common labels, authored {len(COMMON)}")

    out = ROOT / "translations/batch37.json"
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps({"description": "Translate the remaining shop, equipment, communications, route, and battle-trait UI text.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "translations/review_batch37.json").write_text(
        json.dumps({"batch": 37, "translated_slots": len(blocks),
                    "groups": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 37 review", "",
        f"Batch 37 adds {len(blocks)} translated UI slots: {menu_count} shop, equipment, route, and communication strings, plus {len(COMMON)} battle traits and resistance labels.", "",
        "The Japanese ROM is the source for these interface strings. Control parameters such as `^0`, `^1`, and `^2` are preserved. The English labels retain the project's `DigiScore`, `DigiFarm`, `Bits`, and stat terminology. Long communication prompts are wrapped to keep them inside the message panel.", "",
        "| ID | Japanese | English |", "|---|---|---|"]
    for row in review:
        jp = row["japanese"].replace("\n", "<br>").replace("|", "\\|")
        en = row["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{row['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch37.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 37, "translated_slots": len(blocks),
                      "menus": menu_count, "traits": len(COMMON)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
