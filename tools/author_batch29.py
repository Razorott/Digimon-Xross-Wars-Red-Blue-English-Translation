"""Author a reviewed batch of quest, shop, farm, item, and battle text."""
from __future__ import annotations

import csv
import json
import sys
import textwrap
from pathlib import Path

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'
DAWN = ('https://raw.githubusercontent.com/joaomlsantos/'
        'Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt')
WORLD2_OCTOMON = 'https://dev.metalkid.info/DigimonWorld2/Digipedia/Details/Octomon'
XROS_TECHNIQUES = 'https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Guide/Technique'

CARD_URLS = {
    'ピエモン': 'https://world.digimoncard.com/cards/?card_no=EX8-062&search=true',
    'ホエーモン': 'https://world.digimoncard.com/cards/?card_no=BT23-023&search=true',
    'マメモン': 'https://world.digimoncard.com/cards/?card_no=EX9-053&search=true',
    'もんざえモン': 'https://world.digimoncard.com/cards/?card_no=BT22-038&search=true',
    'オクタモン': 'https://world.digimoncard.com/cards/?card_no=EX5-058&search=true',
    'ヴァンデモン': 'https://world.digimoncard.com/cards/?card_no=EX10-048&search=true',
    'シンドゥーラモン': 'https://world.digimoncard.com/cards/?card_no=EX5-050&search=true',
    'ブライモン': 'https://world.digimoncard.com/cards/?category=522038&search=true',
}

NAME_ENGLISH = {
    'ピエモン': 'Piedmon',
    'ホエーモン': 'Whamon',
    'マメモン': 'Mamemon',
    'もんざえモン': 'Monzaemon',
    'オクタモン': 'Octomon',
    'ヴァンデモン': 'Myotismon',
    'シンドゥーラモン': 'Sinduramon',
    'ブライモン': 'Buraimon',
}

MOVE_TERMS = {
    'タイダルウェーブ': ('Tidal Wave', 'DWDD'),
    'スマイリーボム': ('Smiley Bomb', 'DWDD'),
    'ラブリーアタック': ('Lovely Attack', 'DWDD'),
    'かいめいぼくじゅう': ('Spurting Ink', 'WORLD2'),
    'ソニックイヤー': ('Sonic Ears', 'DWDD'),
}

QUEST = {
    116: 'What?! You finished already?! That is surprising... I asked you to do it, so maybe I should not say this, but... I doubt anyone else would stick with Piedmon\'s quiz all the way to the end!',
    117: 'Hey, by the way... Want to recruit me? If you do, come talk to me anytime!',
    118: 'You found yours truly, Piedmon! Ha ha! Welcome to Question 1 of my special Digimon quiz! What is Whamon\'s signature move?',
    120: 'Dull Week',
    121: 'Say that again!',
    122: 'Yesss! The answer is Tidal Wave! That tsunami is so huge it is barely even funny! Ha ha!',
    125: 'Next up is Question 2! Think you can get it right? I will be waiting at Flower Meadow!',
    126: 'Look for me next at Flower Meadow!',
    127: 'You found me again! Ha ha! It is time for Question 2 of Piedmon\'s special Digimon quiz! What is Mamemon\'s signature move?',
    129: 'Spicy Bomb',
    130: 'Yesss! The answer is Smiley Bomb! It will knock you out before you can even smile! Ha ha!',
    133: 'Next up is Question 3! Think you can get it right? I will be waiting in the east of Digital Space!',
    134: 'Look for me next in the east of Digital Space!',
    135: 'You found me again! Ha ha! It is time for Question 3 of Piedmon\'s special Digimon quiz! What is Monzaemon\'s signature move?',
    137: 'Lovely Couple',
    138: 'Yesss! The answer is Lovely Attack! After being hit by that thing, you feel anything but love. More like hate... or death! Ha ha!',
    141: 'Next up is Question 4! Think you can get it right? I will be waiting in the north of Papyrus Desert!',
    142: 'Look for me next in the north of Papyrus Desert!',
    143: 'You found me again! Ha ha! It is time for Question 4 of Piedmon\'s special Digimon quiz! What is Octomon\'s signature move?',
    145: 'Big Ink Ranch',
    146: 'Yesss! The answer is Spurting Ink! It will leave you fed up and feeling awful! Ha ha!',
    149: 'Yay! Congratulations! That is the end of my special quiz for you! Report your results to Myotismon in Papyrus City! Got it? Ha ha!',
    150: 'That is the end of my special quiz for you! Report your results to Myotismon in Papyrus City!',
}

RUMOR_QUEST = {
    175: 'There is someone spreading nasty rumors about Buraimon, who lives in your DigiFarm! Find out who it is and teach them a lesson! Angewomon has a lead. She is in the east of Skull Iceberg, so go ask her!',
    176: 'Someone is spreading nasty rumors about Buraimon! Find them and teach them a lesson!',
    177: 'Buraimon\'s good name is safe now. Thank you! Please take your reward.',
    178: 'Would you like to recruit me? If you are interested, come talk to me.',
    179: 'I found out who is spreading the rumors about Buraimon: Sinduramon in Papyrus Desert! Hurry over there and teach him a lesson!',
    180: 'Sinduramon was the one spreading those nasty rumors! Hurry to Papyrus Desert and teach him a lesson!',
    181: 'Buraimon has athlete\'s foot! Buraimon has athlete\'s foot! Don\'t get close or you will catch it! Run! Hide! Evacuate!',
    182: 'I... I am sorry... I could not stand seeing everyone like Buraimon... I will not do it again. Please forgive me...',
    183: 'I will stop spreading weird rumors... I will apologize to Buraimon and ask them to forgive me.',
    184: 'There is someone spreading nasty rumors about the MagnaAngemon in your DigiFarm! Find out who it is and teach them a lesson! Angewomon has a lead. She is in the east of Skull Iceberg, so go ask her!',
    185: 'Someone is spreading nasty rumors about the MagnaAngemon! Find them and teach them a lesson!',
    186: 'The MagnaAngemon\'s good name is safe now. Thank you! Please take your reward.',
    187: 'Would you like to recruit me? If you are interested, come talk to me.',
    188: 'I found out who is spreading the rumors about the MagnaAngemon: Sinduramon in Papyrus Desert! Hurry over there and teach him a lesson!',
    189: 'Sinduramon was the one spreading those nasty rumors! Hurry to Papyrus Desert and teach him a lesson!',
    190: 'The MagnaAngemon has athlete\'s foot! The MagnaAngemon has athlete\'s foot! Don\'t get close or you will catch it! Run! Hide! Evacuate!',
    191: 'I... I am sorry... I could not stand seeing everyone like the MagnaAngemon... I will not do it again. Please forgive me...',
    192: 'I will stop spreading weird rumors... I will apologize to the MagnaAngemon and ask them to forgive me.',
}

SHOP = {
    31: ('Upgraded ^0 to MAX.', 22),
    32: ('Upgraded ^0 to Lv.^1.', 22),
    33: ('Welcome to the Item Shop! We have everything you need!', 26),
    34: ('Welcome to the Farm Goods and Board Shop! Want to upgrade Farm Island? You are in the right place!', 26),
    35: ('Choose what you want to buy.', 26),
    36: ('Choose what you want to sell.', 26),
    37: ('Choose equipment to buy.', 26),
    38: ('Choose consumables to buy.', 26),
    39: ('Choose Farm Goods to buy.', 26),
    40: ('Choose a farm for a Terrain Board upgrade.', 26),
    41: ('Choose equipment to sell.', 26),
    42: ('Choose consumables to sell.', 26),
    43: ('Choose Farm Goods to sell.', 26),
    44: ('Choose a Farm Island for a Terrain Board upgrade.', 26),
    45: ('Choose the Terrain Board to upgrade.', 26),
    46: ('Choose a Farm Island for a BGM Board upgrade.', 26),
    47: ('Choose the BGM Board to upgrade.', 26),
    48: ('You do not have any equipment.', 26),
    49: ('You do not have any consumables.', 26),
    51: ('You do not have enough DigiBits to buy that.', 26),
    52: ('You already have 99 of that item.\nYou cannot buy any more!', 26),
    53: ('Special items cannot be sold.', 26),
    54: ('This Terrain Board is at max level.\nIt cannot be upgraded further.', 26),
    55: ('This BGM Board is at max level.\nIt cannot be upgraded further.', 26),
}

ITEM_DESCRIPTIONS = {
    0: 'Fully restores one Digimon\'s HP and MP and cures Health Down.',
    1: 'Cures Paralysis on one Digimon.',
    2: 'Cures Sleep on one Digimon.',
    3: 'Cures Confusion on one Digimon.',
    4: 'Cures Darkness on one Digimon.',
    5: 'Cures Health Down on one Digimon.',
    6: 'Cures Health Down for one horizontal row of Digimon.',
    7: 'Cures Unable to Act on one Digimon.',
    8: 'Cures Unable to Act and fully restores one Digimon\'s HP.',
    9: 'Warps your party back to your Fort.',
    13: 'A completely useless shell. Sells for a low price.',
    14: 'An empty shell with no real use. Sells for a low price.',
    15: 'An empty shell with no real use. Sells for a fair price.',
    16: 'An empty shell with no real use. Sells for a high price.',
    17: 'A quirky Numemon ornament. Sells for a low price.',
    18: 'A Patamon ornament. Sells for a high price.',
    19: 'An Impmon ornament. Sells for a very high price.',
    20: 'An Agumon ornament. Sells for a very high price.',
    21: 'A coin found by the Expedition Team. Sells for a low price.',
    22: 'A coin found by the Expedition Team. Sells for a high price.',
    23: 'A coin found by the Expedition Team. Sells for a very high price.',
    24: 'A coin found by the Expedition Team. Sells for an incredible price.',
    25: 'Data that drifts in from nowhere. It has no known use.',
    26: 'Makes one Digimon Cheerful.',
    27: 'Makes one Digimon Clingy.',
    28: 'Makes one Digimon Wild.',
    29: 'Makes one Digimon Cool.',
    30: 'Makes one Digimon Selfish.',
    31: 'Makes one Digimon Demure.',
    32: 'Makes one Digimon Robot-like.',
    33: 'Makes one Digimon Funky.',
}

FARM = {
    22: 'Whoa, a scale! Let us see how much I weigh!',
    23: 'Whoa, I am at my ideal weight! My max HP went up a little!',
    24: 'Uh-oh! I am too heavy! An overweight Wild is just a sweaty pig!',
    25: 'Whoa, a belt machine! That looks fun! I will try it right now!',
    26: 'This shaking feels great! My max HP went up some!',
    27: 'Th-this shaking will not stop... Now I am itchy all over!',
    28: 'Whoa, a treadmill! I will run as far as I can!',
    29: 'That was a good run! My max HP went up a lot!',
    30: 'Running like this feels... weird.',
    31: 'What is this? A crystal ball? It is clear and empty inside!',
    32: 'Whoa, it really glowed! My max MP went up a little!',
    33: 'Is this supposed to be fun? This is boring!',
    34: 'Something is here! I will investigate! Is this a tarot card?',
    35: 'Whoa, magical power is flowing into me! My max MP went up some!',
    36: 'What is this? I do not feel a thing. This is boring!',
    37: 'Whoa, a pyramid! I have always dreamed of going inside one!',
}

BATTLE_MOVES = {
    2033: 'Rolling Upper',
    2037: 'Pawn Buckler',
    2038: 'Smash Hit',
    2039: 'Stun Shock',
    2040: 'Corona Knuckle',
    2041: 'Tear Shot',
    2043: 'Bouncy Tackle',
    2044: 'Little Ice Arrow',
    2045: 'Laser Javelin',
    2046: 'Hammer Boomerang',
    2047: 'Lop Rush',
    2048: 'Hydro Bomb',
    2049: 'Pointer Arrow',
    2050: 'Double Backhand',
    2051: 'Glide Horn',
    2052: 'Triple Star',
    2084: 'Sonic Ears',
}

MOVE_DESCRIPTIONS = {
    30: 'Extends an electric arm to pierce the target. May drain its MP.',
    31: 'Fires a solar beam. May paralyze the target.',
    32: 'Punches nearby enemies with electric arm spikes.',
    33: 'Gathers electricity in its horn and fires a plasma orb.',
    34: 'Hurls a rock with all its might.',
    35: 'Slashes the target with sharp, electrified pincers.',
    36: 'Wraps the target in sticky electric thread. May lower its Speed.',
    37: 'Slashes the target with electrified claws.',
    38: 'Slashes the target with red claws filled with dark power.',
    39: 'Hits the target with a powerful punch.',
    40: 'Dark feathers slash nearby enemies.',
    41: 'Fires powerful missiles that scorch the target. Adds Fire damage.',
    42: 'Purifies the target with holy bullets.',
    43: 'Blasts nearby enemies with a powerful cannon. May lower Attack.',
    44: 'Stops time and electrically disassembles nearby enemies. May cause Paralysis.',
    45: 'Electrically disintegrates nearby enemies with a pulse laser.',
    46: 'Fires a compressed air bullet from its mouth.',
    47: 'Stuns the target with a heart-shaped kiss. May cause Confusion.',
}


def wrap(value: str, width: int) -> str:
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def register_glossary() -> None:
    path = ROOT / 'translations/glossary.json'
    glossary = json.loads(path.read_text(encoding='utf-8'))
    sources = glossary['sources']
    additions = {
        'B29_XROS_TECHNIQUES': {
            'url': XROS_TECHNIQUES,
            'title': 'Digimon Story: Super Xros Wars Japanese technique guide',
            'kind': 'secondary game reference',
            'notes': 'Used to confirm the exact Japanese attack labels and effects; English renderings stay provisional unless a Western game match is verified.'
        },
        'B29_WORLD2_OCTOMON': {
            'url': WORLD2_OCTOMON,
            'title': 'Digimon World 2 English Octomon skill listing',
            'kind': 'secondary extraction of primary game text',
            'notes': 'Confirms Spurting Ink as Octomon\'s English attack name in Digimon World 2.'
        },
    }
    for japanese, url in CARD_URLS.items():
        source_id = 'B29_CARD_' + {
            'ピエモン':'PIEDMON','ホエーモン':'WHAMON','マメモン':'MAMEMON',
            'もんざえモン':'MONZAEMON','オクタモン':'OCTOMON',
            'ヴァンデモン':'MYOTISMON','シンドゥーラモン':'SINDURAMON',
            'ブライモン':'BURAIMON',
        }[japanese]
        additions[source_id] = {
            'url': url,
            'title': 'Bandai official English Digimon Card Game listing',
            'kind': 'primary',
            'notes': f'Official English spelling for {NAME_ENGLISH[japanese]}.',
        }
    for key, value in additions.items():
        if key in sources and sources[key] != value:
            raise ValueError(f'Glossary source changed unexpectedly: {key}')
        sources[key] = value

    terms = glossary['terms']
    name_source_ids = {
        'ピエモン':'B29_CARD_PIEDMON', 'ホエーモン':'B29_CARD_WHAMON',
        'マメモン':'B29_CARD_MAMEMON', 'もんざえモン':'B29_CARD_MONZAEMON',
        'オクタモン':'B29_CARD_OCTOMON', 'ヴァンデモン':'B29_CARD_MYOTISMON',
        'シンドゥーラモン':'B29_CARD_SINDURAMON', 'ブライモン':'B29_CARD_BURAIMON',
    }
    new_terms = []
    for japanese, english in NAME_ENGLISH.items():
        new_terms.append({
            'japanese': japanese, 'english': english, 'category': 'Digimon name',
            'sources': [name_source_ids[japanese]],
            'evidence': 'Official Western spelling checked against the Bandai English card list.'
        })
    for japanese, (english, match) in MOVE_TERMS.items():
        if match == 'DWDD':
            source_ids = ['DAWN_DUSK_MOVES']
            evidence = f'Exact English move-name match in the English Digimon World: Dawn/Dusk move list: {english}.'
        elif match == 'WORLD2':
            source_ids = ['B29_WORLD2_OCTOMON']
            evidence = 'Exact English name used for Octomon\'s ink attack in Digimon World 2; the Xros Wars technique description confirms it is the same ink projectile.'
        else:
            source_ids = ['B29_XROS_TECHNIQUES']
            evidence = 'Working English rendering from the Japanese Xros Wars technique list; no exact prior Western move-name match was found.'
        new_terms.append({
            'japanese': japanese, 'english': english, 'category': 'Move name',
            'sources': source_ids, 'evidence': evidence,
        })

    for term in new_terms:
        existing = next((x for x in terms if x['japanese'] == term['japanese']), None)
        if existing:
            if existing['english'] != term['english']:
                raise ValueError(f'Conflicting glossary term: {term["japanese"]}: {existing["english"]} vs {term["english"]}')
            existing['sources'] = list(dict.fromkeys(existing['sources'] + term['sources']))
            existing['evidence'] = term['evidence']
        else:
            terms.append(term)
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    register_glossary()
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    current = ROOT / 'translations/batch29.json'
    old = json.loads(current.read_text(encoding='utf-8')) if current.exists() else None
    if old:
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)

    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    if old:
        old_groups = {}
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                key = f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}"
                group = (records[key]['source'], block['category'])
                old_groups.setdefault(group, []).append(key)
        for (source, category), ids in old_groups.items():
            row = {'ids': ';'.join(ids), 'japanese': source, 'category': category}
            for key in ids:
                by_id.setdefault(key, row)

    blocks, reviews, seen = [], [], set()

    def add(key: str, english: str, evidence: str = LOCAL, note: str = '', width: int | None = None) -> None:
        if key in prior:
            return
        row = by_id.get(key)
        if row is None:
            raise ValueError(f'Not found in untranslated queue: {key}')
        ids = row['ids'].split(';')
        if all(value in seen for value in ids):
            return
        if any(value in prior or value in seen for value in ids):
            raise ValueError(f'duplicate/already translated: {ids}')
        japanese = row['japanese']
        if any(records[value]['source'] != japanese for value in ids):
            raise ValueError(f'source mismatch: {ids}')
        if width:
            english = wrap(english, width)
        seen.update(ids)
        reviews.append({'category': row['category'], 'japanese': japanese,
                        'ids': ids, 'english': english, 'evidence': evidence,
                        'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': sources,
                           'review_note': note})

    quest_note = ('Optional quiz dialogue translated from the Japanese ROM. Digimon names follow the verified English glossary; '
                  'Tidal Wave, Smiley Bomb, Lovely Attack, and Spurting Ink match Western game move names.')
    for index, english in QUEST.items():
        add(f'MSG/MESPAK02.PAK:020:{index:05d}', english, LOCAL, quest_note, width=15)

    rumor_note = ('Optional DigiFarm rumor quest translated from the Japanese ROM. Buraimon, MagnaAngemon, Angewomon, and '
                  'Sinduramon use their Western spellings recorded in the sourced glossary.')
    for index, english in RUMOR_QUEST.items():
        add(f'MSG/MESPAK02.PAK:020:{index:05d}', english, LOCAL, rumor_note, width=15)

    shop_note = ('Shop and Farm Island interface prompt translated directly from Japanese. DigiBits, Terrain Board, and BGM Board use the project terminology.')
    for index, (english, width) in SHOP.items():
        add(f'MSG/MESPAK01.PAK:018:{index:05d}', english, LOCAL, shop_note, width=width)

    item_note = ('Item effect and flavor description translated from Japanese; terminology is kept consistent with battle status labels and the Digimon glossary.')
    for index, english in ITEM_DESCRIPTIONS.items():
        add(f'MSG/MESPAK04.PAK:029:{index:05d}', english, LOCAL, item_note, width=26)

    farm_note = ('DigiFarm activity report translated from Japanese while preserving the enthusiastic Wild Digimon voice.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:003:{index:05d}', english, LOCAL, farm_note, width=26)

    move_note = ('Working English rendering of a Japanese Xros Wars battle move. The same-game technique reference confirms the source name and effect; '
                 'no exact Western game name was found for this move.')
    for index, english in BATTLE_MOVES.items():
        key = f'MSG/MESPAK00.PAK:000:{index:05d}'
        if english == 'Sonic Ears':
            add(key, english, DAWN,
                'Exact English move-name match in the Digimon World: Dawn/Dusk move list.', width=None)
        else:
            add(key, english, XROS_TECHNIQUES, move_note)

    effect_note = ('Battle effect translated directly from Japanese and cross-checked against the same-game technique guide. '
                   'Names and effects remain distinct: the sentence describes the move behavior, not a new attack title.')
    for index, english in MOVE_DESCRIPTIONS.items():
        add(f'MSG/MESPAK04.PAK:011:{index:05d}', english,
            XROS_TECHNIQUES, effect_note, width=26)

    out = ROOT / 'translations/batch29.json'
    review_json = ROOT / 'translations/review_batch29.json'
    review_md = ROOT / 'translations/review_batch29.md'
    out.write_text(json.dumps({
        'description': 'Piedmon quiz and rumor side quests; Farm Island shop, item descriptions, DigiFarm reports, and battle moves/effects.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Batch 29 translation review', '',
        'Japanese source strings, English renderings, stable IDs, and terminology evidence.', '',
        '| IDs | Japanese | English | Evidence and review note |',
        '| --- | --- | --- | --- |',
    ]
    for item in reviews:
        ids = '<br>'.join(f'`{key}`' for key in item['ids'])
        japanese = item['japanese'].replace('<0A>', '<br>').replace('|', '\\|')
        english = item['english'].replace('\n', '<br>').replace('|', '\\|')
        evidence = item['evidence']
        note = item['review_note'].replace('|', '\\|')
        source = f'[{evidence}]({evidence})' if evidence.startswith('https://') else evidence
        lines.append(f'| {ids} | {japanese} | {english} | {source}<br>{note} |')
    review_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    category_counts = {}
    for group in reviews:
        category_counts[group['category']] = category_counts.get(group['category'], 0) + len(group['ids'])
    print(f'{len(blocks)} text slots from {len(reviews)} reviewed Japanese groups')
    print('Categories:', json.dumps(category_counts, ensure_ascii=False))


if __name__ == '__main__':
    main()
