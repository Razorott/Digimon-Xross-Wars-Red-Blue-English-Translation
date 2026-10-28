"""Author reviewed battle, quest, DigiFarm, and item strings for batch 23."""
import csv
import json
import textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SRC = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
CHESS = 'https://world.digimoncard.com/cards/?category=522016&search=true'

MOVES = {
    1740: ('Nightmare Syndrome', False),
    1743: ('Bloody Stream', False),
    1754: ('Dimension Hole', False),
    1756: ('Hyper Bulldozer', False),
    1764: ('Ground Zero', False),
    1777: ('Scissors Execution', False),
    1779: ('Pyramid Formation', False),
    1780: ('Poison Smash', False),
    1782: ('Divine Feet', False),
    1785: ('Super Stench Spray', False),
    1802: ('Mega Dash Impact', False),
    1803: ('Destruction Roar', False),
    1823: ('Deadly Sting', False),
    1832: ('Hunting Cannon', False),
    1836: ('Burning Salamander', False),
    1856: ('Strike Fishing', True),
    1858: ('Tryhorn A', True),
    1866: ('Poop Bazooka', True),
    1870: ('Volcano SS', True),
    1872: ('Roada', False),
    1873: ('Magical Stick', False),
    1876: ('Stronghold', False),
}

QUESTS = {
    428: ('Talk to KingChessmon in the Front Room.', CHESS, 'Official card list confirms KingChessmon.'),
    429: ('Find PawnChessmon White in west Crystal Volcano.', CHESS, 'Official card list confirms PawnChessmon; White identifies the game variant.'),
    430: ('Find KnightChessmon White in west Crystal Volcano.', CHESS, 'KnightChessmon White follows the English species spelling; White identifies the game variant.'),
    431: ('Find RookChessmon in east Crystal Volcano.', CHESS, 'Official card list confirms RookChessmon.'),
    432: ('Find BishopChessmon in north Lost Space.', CHESS, 'BishopChessmon uses the English species spelling.'),
    433: ('Find QueenChessmon in south Lost Space.', CHESS, 'Official card list confirms QueenChessmon.'),
    434: ('Report to KingChessmon in the Front Room.', CHESS, 'Official card list confirms KingChessmon.'),
    435: ('Residents of the Game Kingdom', SRC, 'Quest title.'),
    436: ("Find KingChessmon's servants and deliver their message.", CHESS, 'Official card list confirms KingChessmon.'),
    438: ('Talk to Renamon in the Front Room.', SRC, 'Quest objective; species name follows the established English glossary.'),
    439: ('Find Sakuyamon in south Lost Space.', SRC, 'Quest objective; species name follows the established English glossary.'),
    440: ('Defeat Apocalymon in north Lost Space.', SRC, 'Quest objective; species name follows the established English glossary.'),
    441: ('Meet Sakuyamon again.', SRC, 'Quest objective; species name follows the established English glossary.'),
    442: ('Report to Renamon in the Front Room.', SRC, 'Quest objective; species name follows the established English glossary.'),
}

STORY = {
    136: 'Why is there a monitor\nhere of all places?',
    137: 'This monitor explains\nhow battles work.',
    138: 'So this is a battle\ntutorial monitor?\nThen I should listen.',
    139: 'I want to hurry ahead...\nbut I should listen now,\nbefore I get stuck later.\nShould I?',
    150: 'I see... Did you get\nall that, Shoutmon?',
    151: "Not a clue! But that's\nokay! I'll leave the\ncomplicated stuff to the\nGeneral! If the lesson's\nover, let's hurry and\nfind everyone!",
    152: 'Do you need a battle\ntutorial?',
    156: "I'll explain how to\nuse the tent here.",
    157: "What's a tent? Should\nI hear the explanation?",
    158: 'Find a Tent Point to\nopen a tent.',
    159: 'Stand on a Tent Point\nand press A to open the\ntent. You can go inside\nto restore HP and MP,\nand save your game.',
    160: "It's a handy place\nwhen you're in a pinch,\nso remember how to use\nthe tent.",
    161: "There's a Tent Point\nright here. Maybe I'll\ngive it a try.",
    162: 'Stand on a Tent Point\nand press A to open it.\nInside, you can restore\nHP and MP, and save\nyour game data.',
    163: '...Oh? Another monitor.',
    164: "I'll explain battle\nformations.",
    165: 'This sounds like a lot\nof work...',
    166: "Well, let's not make it\nmore complicated than\nit is. I'll listen.",
    168: 'Rear Guards attack\nfrom behind the party.\nThe Vanguard protects\nthem from enemy attacks,\nbut their attacks deal\nhalf damage.\nIf every Vanguard\nDigimon is defeated, the\nRear Guards move up to\nthe Vanguard.\nYou must put a Digimon\nin the Vanguard before\nyou can fill the Rear\nGuard, so keep that in\nmind.',
}

FARM = {
    16: 'Wow, this is much more\nfun than I expected...\nThanks to you, my\nfriendship went up a bit...',
    17: "This is fun, but it\nmight be a little hard...",
    18: "Oh, it's a cellphone!\nI'll try sending Taiki\na message...",
    19: "Oh, he replied! I'm\nso happy! I think my\nfriendship went up\nquite a bit...",
    20: "Hmm... No reply...\nThat's too bad...",
    21: "Taiki left a digital\ncamera here... Since I\nhave the chance, maybe\nI'll take a picture of\nmyself...",
    22: 'I got a good picture!\nThank goodness... My\nfriendship went up a\nlot, too...',
    23: "Uhh... I don't really\nknow how to use this...",
    24: "Hmm? Is that a ring of\nfire...? It looks fun,\nso I'll give it a try.",
    25: 'Yes! The flames and my\nburning spirit made my\nEXP shoot way up!',
    26: "A-ah, it's so hot!\nI don't like this!",
    27: "A Fire Road, right...?\nIt looks really hot...\nCan I cross it?",
}

ITEMS = {
    4423: 'Guruguru Amazon West Key',
    4424: 'Guruguru Amazon East Key',
    4425: 'Kumonos Ruins West Key',
    4426: 'Kumonos Ruins East Key',
    4427: 'Knuckle Coast East Key',
    4509: 'Volcano Board',
    4510: 'Desert Board',
    4511: 'Marble Board',
    4512: 'Darkness Board',
    4513: 'Coral Board',
    4514: 'Machine Board',
    4515: 'Grassland Board',
    4516: 'Forest Board',
    4517: 'Tropical Board',
    4518: 'Mythical Beast',
    4519: 'Beast',
    4520: 'Angel',
    4521: 'Demon',
    4522: 'Aquatic',
    4523: 'Machine',
    4524: 'Bird',
    4525: 'Insect',
    4526: 'Plant',
    4527: 'Volcano',
    4528: 'Desert',
    4529: 'Marble',
    4530: 'Darkness',
    4531: 'Coral',
    4532: 'Machine',
    4533: 'Grassland',
    4534: 'Forest',
    4535: 'Tropical',
}

TRAITS = {
    17: 'More vulnerable to enemy MP Drain.',
    18: 'Less likely to be shuffled.',
    19: 'Much less likely to be shuffled.',
    20: 'Immune to Shuffle.',
    21: 'Party-wide:\nslightly resists Shuffle.',
    22: 'Party-wide:\nresists Shuffle.',
    23: 'Slightly more vulnerable to Shuffle.',
    24: 'Resists enemy Poison.',
    25: 'Strongly resists enemy Poison.',
    26: 'Immune to enemy Poison.',
}


def wrap(text, width):
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False, break_on_hyphens=False) or [''])
        for line in text.split('\n')
    )


def main():
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    blocks, review, seen = [], [], set()

    def add(key, english, evidence=SRC, note='', width=None):
        if key not in by_id:
            raise ValueError(f'Not in refreshed queue: {key}')
        row = by_id[key]
        ids = row['ids'].split(';')
        if any(value in prior or value in seen for value in ids):
            raise ValueError(f'duplicate/already translated: {ids}')
        if any(records[value]['source'] != row['japanese'] for value in ids):
            raise ValueError(f'source mismatch: {ids}')
        if width:
            english = wrap(english, width)
        if not note:
            note = 'Provisional working English; an exact Western game localization was not confirmed.'
        seen.update(ids)
        review.append({'category': row['category'], 'japanese': row['japanese'],
                       'ids': ids, 'english': english,
                       'evidence': evidence, 'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': sources,
                           'review_note': note})

    for index, (english, matched) in MOVES.items():
        if matched:
            note = 'Reuses the English Digimon World: Dawn/Dusk move-name string for the matching Japanese technique.'
            evidence = DAWN
        else:
            note = 'Working English rendering from the Japanese attack name; no exact Western-game match verified.'
            evidence = SRC
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)

    for index, (english, evidence, note) in QUESTS.items():
        add(f'MSG/MESPAK01.PAK:000:{index:05d}', english, evidence, note, width=27)
    for index, english in STORY.items():
        add(f'MSG/MESPAK02.PAK:012:{index:05d}', english,
            note='Battle/tent tutorial dialogue; wrapped for the fixed 15-column story renderer.',
            width=15)
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:002:{index:05d}', english,
            note='DigiFarm reaction; item names and game terminology follow the project glossary.',
            width=27)
    for index, english in ITEMS.items():
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english,
            note='Direct map key, farm board, type, or area label translation; established place names are retained.',
            width=27)
    for index, english in TRAITS.items():
        add(f'MSG/MESPAK04.PAK:001:{index:05d}', english,
            note='Direct gameplay effect description; terminology is kept consistent across the battle/status menus.',
            width=27)

    out = ROOT / 'translations/batch23.json'
    out.write_text(json.dumps({
        'description': 'Battle move names, battle and tent tutorials, chess quest objectives, DigiFarm reactions, map/farm labels, status-effect descriptions, and three translated DigiFarm notification graphics.',
        'blocks': blocks
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'translations/review_batch23.json').write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')


if __name__ == '__main__':
    main()
