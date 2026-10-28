"""Author the next checked airport, battle, item-effect, farm and NPC batch."""
import csv
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SRC = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
NEXT_ORDER = 'https://d1vtv52f4vjbmu.cloudfront.net/manuals/dwno/PS4-DWNO_manual_GBQS_WEB.pdf'
CARD = 'https://world.digimoncard.com/cards/?category=522025&search=true'

# The strings are read from the stable message IDs. Only clear Western names
# are asserted as established; the rest remain marked as working translations.
MOVES = {
    2053: 'Feather Cutter',
    2055: 'Cyber Nail',
    2058: 'Machine Gun Arm',
    2061: 'Elemental Bolt',
    2062: 'Power Guillotine',
    2063: 'Ion Blaster',
    2065: 'Double Cutter',
    2066: 'Mame Bite 1000',
    2067: 'Hell Howling',
    2068: 'Falcon Claw',
    2069: 'Corona Flame',
    2070: 'Strike Uppercut',
    2071: 'Brute Force',
    2072: 'Cocoon Attack',
    2073: 'Maelstrom',
    2075: 'Darkness Love',
    2076: 'Black Mind',
    2077: 'Cross Slash',
    2078: 'Engacho Kick',
    2080: 'Needle Spray',
    2081: 'Fox Fire',
    2083: "Dragon's Roar",
    2086: 'Giga Heal Light',
    2091: 'Mach Jab',
    2092: 'Horn Impulse',
    2093: 'Red Eye',
    2095: 'Charge',
    2096: 'Lightning Dash',
    2097: 'Magnet Beam',
    2098: 'Falling Star',
    2099: 'Thousand Whip',
    2100: 'Whiteout',
    2101: 'Rigid Block',
    2102: 'Magma Ball',
    2103: 'Giga Destroyer Legacy',
    2105: 'Sledge Dash',
}

AIRPORT = {
    'MSG/MESPAK01.PAK:002:00000': 'Resident Digimon',
    'MSG/MESPAK01.PAK:002:00001': 'Travel to this area?',
    'MSG/MESPAK01.PAK:002:00004': 'Choose an airport\nfor your destination!',
    'MSG/MESPAK01.PAK:002:00005': 'Land at Lost N Port.',
    'MSG/MESPAK01.PAK:002:00006': 'Land at Lost S Port.',
    'MSG/MESPAK01.PAK:002:00007': 'Sky Port!\nFort Yard is to the south.',
    'MSG/MESPAK01.PAK:002:00008': 'Land at Stealth N Port.',
    'MSG/MESPAK01.PAK:002:00009': 'Land at Stealth S Port.',
    'MSG/MESPAK01.PAK:002:00010': 'Land at Digital N Port.',
    'MSG/MESPAK01.PAK:002:00011': 'Land at Digital S Port.',
    'MSG/MESPAK01.PAK:002:00012': 'Land at Crystal Mine Port.\nCrystal Cave is east.',
    'MSG/MESPAK01.PAK:002:00013': 'Land at Crystal W Port.',
    'MSG/MESPAK01.PAK:002:00014': 'Flower Port!\nDarkness Tunnel is east.',
    'MSG/MESPAK01.PAK:002:00015': 'Earth Port!\nCrystal Cave is north.',
    'MSG/MESPAK01.PAK:002:00016': 'Land at W. Knuckle City Port.',
    'MSG/MESPAK01.PAK:002:00017': 'Land at Skull City Port.',
    'MSG/MESPAK01.PAK:002:00018': 'Tokona Port!\nTokona Sea is north.',
    'MSG/MESPAK01.PAK:002:00019': 'Guruguru W Port!\nDarkness Tunnel is west.',
    'MSG/MESPAK01.PAK:002:00020': 'Land at E. Knuckle City Port.',
    'MSG/MESPAK01.PAK:002:00021': 'Land at Skull E Port.',
    'MSG/MESPAK01.PAK:002:00022': 'Kumonos W Port!\nDigital Space E is south.',
    'MSG/MESPAK01.PAK:002:00023': 'Guruguru City Port!\nDigital Space E is north.',
    'MSG/MESPAK01.PAK:002:00024': 'Land at Kumonos City Port.',
    'MSG/MESPAK01.PAK:002:00025': 'Land at Papyrus N Port.',
    'MSG/MESPAK01.PAK:002:00026': 'Papyrus City Port!\nGuruguru Amazon E is west.',
}

FARM = {
    48: "Huh? There's a huge waterfall here.\nMaybe I'll train for a bit!",
    49: "Yay! The waterfall training\nreally boosted my EXP!",
    50: "No, it's too cold...\nI want to stop training!",
    51: "Hmm? Something smells so nice.\nOh! It must be this flower!",
    52: "That sweet scent feels so nice!\nI think I gained a little EXP!",
    53: "A caterpillar! Nooo!\nI hate caterpillars!",
    54: "This is a treehouse, right?\nI like it! I'll live here!",
    55: "It's so peaceful here!\nI gained a lot of EXP!",
    56: "Nope. There's no food here!",
    57: "Is that a computer?\nCan I get online with it?",
    58: "I did it! It works!\nI gained knowledge and EXP!",
    59: "Hmm... How do you turn\nthis computer on?",
    60: "That's a solar panel, right?\nI wonder how it works...",
    61: "Whoa! Electricity is flowing\nthrough me! I gained EXP!",
    62: "Yikes! That stings!\nI hate electricity!",
    63: "That's a pinball machine, right?\nLet's try it!",
    64: "Yes! A perfect score!\nI gained a lot of EXP!",
    65: "That was terrible...\nMaybe I'm bad at this?",
    66: "Is this a birdhouse?\nI'll take a look!",
    67: "I feel like a little bird now!\nI gained a little EXP!",
}

EFFECTS = {
    0: 'Escape is much more likely to succeed.',
    1: 'Escape is slightly more likely to fail.',
    2: 'Paralysis is more likely to take hold.',
    3: 'Paralysis is much more likely to take hold.',
    4: 'Sleep is more likely to set in.',
    5: 'Sleep is much more likely to set in.',
    6: 'Confusion is more likely to take hold.',
    7: 'Confusion is much more likely to take hold.',
    8: 'Darkness is more likely to take hold.',
    9: 'Darkness is much more likely to take hold.',
    10: 'HP Drain is more likely to succeed.',
    11: 'HP Drain is much more likely to succeed.',
    12: 'MP Drain is more likely to succeed.',
    13: 'MP Drain is much more likely to succeed.',
    14: 'Poison is more likely to take hold.',
    15: 'Poison is much more likely to take hold.',
    16: 'Curse is more likely to take hold.',
    17: 'Curse is much more likely to take hold.',
    18: 'In battle only:\nHP recovery is slightly greater.',
    19: 'In battle only:\nHP recovery is moderately greater.',
    20: 'In battle only:\nHP recovery is much greater.',
    21: 'HP Drain restores more HP.',
    22: 'HP Drain restores much more HP.',
    23: 'MP Drain restores more MP.',
    24: 'MP Drain restores much more MP.',
    25: 'Poison deals slightly more damage.',
    26: 'Poison deals moderately more damage.',
    27: 'Poison deals much more damage.',
    28: 'In battle only:\nMove MP cost is slightly lower.',
    29: 'In battle only:\nMove MP cost is much lower.',
    30: 'Health Down lasts longer.',
    31: 'Health Down lasts much longer.',
    32: 'Enemies are slightly easier to Melodize.',
    33: 'Enemies are moderately easier to Melodize.',
    34: 'Enemies are much easier to Melodize.',
    35: 'Battle rewards:\nMore likely to get an item.',
    36: 'Battle rewards:\nMuch more likely to get an item.',
    37: 'Battle rewards:\nEarn slightly more bit.',
    38: 'Battle rewards:\nEarn moderately more bit.',
    39: 'Battle rewards:\nEarn much more bit.',
    40: 'Battle rewards:\nEarn slightly more EXP.',
}

NPC = {
    'MSG/MESPAK02.PAK:019:00165': 'Thanks, Taiki! Now we can use\nthe airport again. Here\nis your reward!♪',
    'MSG/MESPAK02.PAK:019:00168': 'Tell Biyomon to gather\nthe others right away!',
    'MSG/MESPAK02.PAK:019:00178': 'I heard a scary rumor from\nKnuckle Coast: a slimy monster\nwith raw, peeling skin...\nWait, never mind!\nThanks for the shaver.\nI will... keep it safe.',
    'MSG/MESPAK02.PAK:019:00179': '...Togemon asked you?\nI understand how it feels.\nYou can borrow the shaver,\nif you really want...\nBut when it is all smooth,\nwill it still be...\nNever mind. Take it.\nYou can keep it.',
    'MSG/MESPAK02.PAK:019:00180': 'It is all part of the experience.\nTell Togemon... good luck!',
    'MSG/MESPAK02.PAK:020:00009': 'A fake version of me is said\nto appear east of Knuckle Coast.\nFind it for me! That creep\nreally gives me the shivers!\nPlease, do it for real!',
    'MSG/MESPAK02.PAK:020:00010': 'Hurry and find my fake\neast of Knuckle Coast!\nThen rough it up for me!',
    'MSG/MESPAK02.PAK:020:00066': 'Welcome! If you have a\nmeteorite, I can appraise it.',
    'MSG/MESPAK02.PAK:020:00067': "A meteorite, is it? Let's see...\nHmm... I understand now.\nIt looks like a meteorite, but\nit isn't made of stone, so\nit doesn't count. I'm sorry,\nbut this is space squid poop.\nIt's smelly, so please take it\nback with you!",
    'MSG/MESPAK02.PAK:020:00099': 'I would like to join your team!\nIf you are interested,\ncome talk to me!',
    'MSG/MESPAK02.PAK:020:00114': 'I have a very tough mission\nfor you! Find Piedmon and\nanswer his quiz. Get every\nquestion right and all is well.\nBut if you fail...\nWho knows what will happen!\nStart at Knuckle Coast.\nHead there now!',
    'MSG/MESPAK02.PAK:020:00115': 'Find Piedmon and take his quiz!\nFirst, you have to find him.\nThat is where it all begins!',
}


def wrap(value, width):
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def main():
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    previous_output = ROOT / 'translations/batch26.json'
    if previous_output.exists():
        old = json.loads(previous_output.read_text(encoding='utf-8'))
        for block in old['blocks']:
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
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
            note = 'Provisional English rendering from the Japanese move name; no exact Western-game match was confirmed.'
        seen.update(ids)
        review.append({'category': row['category'], 'japanese': row['japanese'],
                       'ids': ids, 'english': english, 'evidence': evidence,
                       'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': sources,
                           'review_note': note})

    for index, english in MOVES.items():
        if index == 2083:
            evidence = CARD
            note = 'Exact English spelling confirmed in Bandai’s official English Digimon Card Game card list for ドラゴンズロア (Dragon’s Roar). This is a franchise naming cross-check, not proof that the card and game effects are identical.'
        elif index == 2080:
            evidence = DAWN
            note = 'Needle Spray appears in the licensed English Digimon World: Dawn/Dusk move-list extraction. The Japanese technique spelling also directly corresponds; recheck the exact Digimon association during playthrough QA.'
        elif index == 2091:
            evidence = NEXT_ORDER
            note = 'Mach Jab is the English name used in Bandai Namco’s official Digimon World: Next Order manual. No exact Dawn/Dusk match was established for this source string.'
        elif index == 2095:
            evidence = DAWN
            note = 'Charge is also present in the licensed English Digimon World: Dawn/Dusk move-list extraction; this is a common move label, so keep the specific Japanese association provisional.'
        else:
            evidence = DAWN
            note = 'Provisional direct English rendering of the Japanese move name. Checked against the English Dawn/Dusk move-list extraction; no exact game-name match was confirmed for this string.'
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)

    for key, english in AIRPORT.items():
        add(key, english,
            note='Airport selection and route help. Location names reuse the established area labels (Lost Space, Sky Fort, Stealth Valley, Digital Space, Crystal Mine, Crystal Cave, Flower Plains, Knuckle Coast, Skull Glacier, Tokona, Guruguru, Kumonos, and Papyrus).',
            width=25)

    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:002:{index:05d}', english,
            note='DigiFarm object reaction or activity result. Existing Japanese line breaks are preserved; English is kept to short readable lines.',
            width=25)

    for index, english in EFFECTS.items():
        add(f'MSG/MESPAK04.PAK:002:{index:05d}', english,
            note='Battle trait/equipment effect description. Terminology follows the project’s established Escape, status, Drain, Melodize, Health Down, and EXP labels.',
            width=28)

    for key, english in NPC.items():
        add(key, english,
            note='NPC dialogue or mission instruction from the original Japanese; character and area names follow the established project glossary.',
            width=15)

    (ROOT / 'translations/batch26.json').write_text(json.dumps({
        'description': 'Airport route menus, battle techniques and effect descriptions, DigiFarm reactions, and NPC mission dialogue.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'translations/review_batch26.json').write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    md = [
        '# Batch 26 translation review',
        '',
        'Japanese source strings, English renderings, stable IDs, and terminology notes.',
        '',
        '| IDs | Japanese | English | Evidence and review note |',
        '| --- | --- | --- | --- |',
    ]
    for item in review:
        ids = '<br>'.join(f'`{key}`' for key in item['ids'])
        japanese = item['japanese'].replace('<0A>', '<br>').replace('|', '\\|')
        english = item['english'].replace('\n', '<br>').replace('|', '\\|')
        evidence = item['evidence']
        note = item['review_note'].replace('|', '\\|')
        source = f'[{evidence}]({evidence})' if evidence.startswith('https://') else evidence
        md.append(f'| {ids} | {japanese} | {english} | {source}<br>{note} |')
    (ROOT / 'translations/review_batch26.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')


if __name__ == '__main__':
    main()
