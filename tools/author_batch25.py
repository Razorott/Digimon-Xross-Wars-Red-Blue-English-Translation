"""Author reviewed battle-move and early-game dialogue strings for batch 25."""
import csv
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SRC = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
FUSION_DUB = 'https://digimon.fandom.com/wiki/Digimon_Fusion/Appendices/Attacks'

# Direct English renderings of the Japanese move names. These are kept marked
# provisional unless the same attack is present in the Dawn/Dusk extraction.
MOVES = {
    1911: 'Bellow Blaster',
    1912: 'Fiery Fastball',
    1914: 'Arm Bunker',
    1916: 'Ram Slammer',
    1917: 'Drill Bit Blitz',
    1919: 'Drill Blader',
    1920: 'Crash Boom',
    1921: 'Wing Edge',
    1922: 'Random Laser',
    1923: 'Star Boomerang',
    1924: 'Star Storm',
    1930: 'Triple Impact',
    1933: 'Atomic Tail',
    1935: 'Trident Tail',
    1936: 'Nightflare',
    1937: 'Plasma Cannons',
    1938: 'Trident Arm',
    1941: 'Aqua Rage',
    1942: 'Air Slicer',
    1943: 'Shoulder Blade',
    1949: 'Darkness Claw',
    1952: 'Meteor Impact',
    1953: 'Meteor Buster Attack',
    1954: 'Chaos Flare',
    1958: 'Head Strike',
    1959: 'Kilo Flame',
    1960: 'Death March',
    1961: 'Harasho Attack',
    1962: 'Baby Breath',
    1964: 'Eucalyptus Claw',
    1965: 'Evil Snore',
    1966: 'Witch Warp',
    1968: 'Excrement',
    1971: 'Ogre Flame',
    1972: 'Cathedral',
    1974: 'Power Picks',
    1976: 'Fire Shot',
    1977: 'Water Dragon',
    1978: 'Pinwheel',
    1979: 'Power Line',
    1980: 'Dondoko March',
    1981: 'Dondoko Rush',
    1982: 'Extreme Taiko',
    1983: 'Bomber Head',
    1985: "Rockin' Magnum",
    1986: 'Air Shooter',
    1994: 'Prism Flash',
    1995: 'Crystal Breath',
    2000: 'Blood Eye',
    2002: 'Beat Knuckle',
    2003: 'Baby Burner',
    2004: 'Victory Punch',
    2006: 'Metal Cannon',
    2007: 'Electric Shock',
    2008: 'Tiny Fire',
    2010: 'Magical Fire',
    2011: 'Root Stretch',
    2012: 'Twice Arm',
    2013: 'Earth Shaker',
    2014: 'Water Jet',
    2016: 'Bat Flutter',
    2017: 'Toy Flame',
    2018: 'Darkness Gear',
    2019: 'Puppy Howling',
    2020: 'Silk Thread',
    2021: 'Beak Peck',
    2022: 'Rolling Stone',
    2024: 'Blazing Ice',
    2027: 'Crazy Smoke',
    2029: 'Gobli Bomb',
    2030: 'Black Pearl',
    2031: 'Allergy Shower',
}
MATCHED_DAWN = {1954, 2007}
MATCHED_FUSION_DUB = {
    1911, 1912, 1916, 1917, 1924, 1933, 1936, 1937,
    1966, 1974, 1976, 1977, 1980, 1981, 1982,
}

# Early travel, recovery, recruitment and wake-up dialogue. The source's
# explicit Japanese break controls become newlines; ^0 stays as its live-name
# placeholder and the terminal arrow is preserved as a paging control.
STORY = {
    'MSG/MESPAK02.PAK:012:00084': 'Would you like to rest?',
    'MSG/MESPAK02.PAK:012:00085': 'Yes, please.',
    'MSG/MESPAK02.PAK:012:00086': 'No, thanks!',
    'MSG/MESPAK02.PAK:012:00087': "Your Digimon's HP and MP\nhave been fully restored!",
    'MSG/MESPAK02.PAK:012:00095': 'Ride a Digimon to travel?',
    'MSG/MESPAK02.PAK:012:00098': 'Talk to me anytime you want\nto travel somewhere.',
    'MSG/MESPAK02.PAK:012:00099': 'Talk to me again when\nyou want to travel! ',
    'MSG/MESPAK02.PAK:012:00116': "You don't have the key\nto open this gate!",
    'MSG/MESPAK02.PAK:014:00031': '^0 joined your party!',
    'MSG/MESPAK02.PAK:014:00036': 'Will you let me join\nyour party?',
    'MSG/MESPAK02.PAK:014:00038': 'Can I join your party?',
    'MSG/MESPAK02.PAK:014:00044': 'Will you let me join?',
    'MSG/MESPAK02.PAK:014:00059': 'Will you let me join?',
    'MSG/MESPAK02.PAK:014:00073': "Let's be friends!",
    'MSG/MESPAK02.PAK:014:00075': 'Count on me!▼',
    'MSG/MESPAK02.PAK:014:00088': 'I am counting on you!',
    'MSG/MESPAK02.PAK:014:00097': "Aw, that's a letdown.",
    'MSG/MESPAK02.PAK:014:00102': 'All right!',
    'MSG/MESPAK02.PAK:014:00104': 'Hmm...',
    'MSG/MESPAK02.PAK:014:00110': 'I see. Got it.',
    'MSG/MESPAK02.PAK:014:00117': 'Yeah, I got it.',
    'MSG/MESPAK02.PAK:014:00126': 'Yes, start it up.',
    'MSG/MESPAK02.PAK:014:00127': 'No, not yet.',
    'MSG/MESPAK02.PAK:014:00133': "Hey, Taiki!\nHow long are you\ngoing to sleep?",
    'MSG/MESPAK02.PAK:014:00134': "Huh? Shoutmon,\nwhat's going on?",
    'MSG/MESPAK02.PAK:014:00135': "What do you mean,\n'what's going on'...?\nGet it together!",
    'MSG/MESPAK02.PAK:015:00023': "Here's an item for you!♪",
    'MSG/MESPAK02.PAK:015:00094': 'Take good care of it!♪',
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
    previous_output = ROOT / 'translations/batch25.json'
    if previous_output.exists():
        old = json.loads(previous_output.read_text(encoding='utf-8'))
        for block in old['blocks']:
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    old_review = ROOT / 'translations/review_batch25.json'
    if old_review.exists():
        for item in json.loads(old_review.read_text(encoding='utf-8')):
            fallback = {'ids': ';'.join(item['ids']), 'japanese': item['japanese'],
                        'category': item['category']}
            for key in item['ids']:
                by_id.setdefault(key, fallback)

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
            note = 'Provisional working English rendering; no exact Western-game match was confirmed.'
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
        if index in MATCHED_DAWN:
            note = 'The same named attack appears in the English Digimon World: Dawn/Dusk move-list extraction; Japanese source confirms the direct match.'
            evidence = DAWN
        elif index == 1953:
            note = 'Keeps the game move distinct as Meteor Buster Attack (95 px). The English Digimon Fusion dub also calls Shoutmon X5\'s move Earth Shaker in some episodes, but this game separately lists アースシェイカー as another technique.'
            evidence = FUSION_DUB
        elif index in MATCHED_FUSION_DUB:
            note = 'Uses the established English Digimon Fusion dub name for this Japanese-named attack; the Western label and character mapping are cross-checked against the attack reference. Shoutmon\'s dub name varies by episode.' if index == 1911 else 'Uses the established English Digimon Fusion dub name for this Japanese-named attack; the Western label and character mapping are cross-checked against the attack reference.'
            evidence = FUSION_DUB
        else:
            note = 'Provisional English rendering from the Japanese attack name. Checked the Dawn/Dusk move-list extraction; no exact matching name was confirmed.'
            evidence = DAWN
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)

    for key, english in STORY.items():
        add(key, english,
            note='Early travel, recruitment, recovery, item, or wake-up dialogue. Japanese line breaks are preserved and the dynamic ^0 name token and paging marker are retained.',
            width=15)

    (ROOT / 'translations/batch25.json').write_text(json.dumps({
        'description': 'Battle technique names and early travel, recovery, recruitment, item, and wake-up dialogue.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'translations/review_batch25.json').write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')


if __name__ == '__main__':
    main()
