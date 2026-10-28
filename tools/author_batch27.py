"""Author a focused battle-move and Sky Fort story batch."""
import csv
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
SOURCE = 'Original Japanese ROM (local primary source)'

# These are contiguous entries in the battle move-name table. Names without an
# exact licensed English counterpart are explicitly labeled as working
# renderings in the review file; no invented Western-game match is implied.
MOVES = {
    2114: 'Fire Punch',
    2115: 'Ice Pellet',
    2116: 'Thunder Kick',
    2117: 'Divine Ray',
    2118: 'Shadow Punch',
    2119: 'Battle Sword',
    2120: 'Fire Fist',
    2121: 'Ice Fist',
    2122: 'Electric Fist',
    2123: 'Light Fist',
    2124: 'Dark Fist',
    2125: 'Spirit Fist',
    2126: 'Fire Breath',
    2127: 'Ice Breath',
    2128: 'Electric Breath',
    2129: 'Light Breath',
    2130: 'Dark Breath',
    2131: 'Spirit Breath',
    2132: 'Mini Fire Resolve',
    2133: 'Fire Resolve',
    2134: 'Mega Fire Resolve',
    2135: 'Giga Fire Resolve',
    2136: 'Tera Fire Resolve',
    2137: 'Mini Ice Resolve',
    2138: 'Ice Resolve',
    2139: 'Mega Ice Resolve',
    2140: 'Giga Ice Resolve',
    2141: 'Tera Ice Resolve',
    2142: 'Mini Thunder Resolve',
    2143: 'Thunder Resolve',
    2144: 'Mega Thunder Resolve',
    2145: 'Giga Thunder Resolve',
    2146: 'Tera Thunder Resolve',
    2147: 'Mini Divine Resolve',
    2148: 'Divine Resolve',
    2149: 'Mega Divine Resolve',
    2150: 'Giga Divine Resolve',
    2151: 'Tera Divine Resolve',
    2152: 'Mini Shadow Resolve',
    2153: 'Shadow Resolve',
    2154: 'Mega Shadow Resolve',
    2155: 'Giga Shadow Resolve',
    2156: 'Tera Shadow Resolve',
    2157: 'Mini Battle Resolve',
    2158: 'Battle Resolve',
    2159: 'Mega Battle Resolve',
    2160: 'Giga Battle Resolve',
    2161: 'Tera Battle Resolve',
    2162: 'Sun Heal Light',
    2163: 'Wild Cure',
    2164: 'Infinite Slap',
    2165: 'Light of Heaven',
    2166: 'Mini Heal Light',
    2167: 'Heal Light',
    2168: 'Mega Heal Light',
    2169: 'Cure Light',
    2177: 'Soul Majesty',
    2178: 'Sugar Pound',
    2179: 'Blue Brave',
    2183: 'Azure Flame',
    2186: 'Twilight Dance',
    2188: 'Soul Arbalest',
    2190: 'Megalo Flame',
    2191: 'Blaster Tail II',
    2195: 'Gear Spin Needle',
    2196: 'Wild Burning',
    2197: 'Brilliance Dagger',
    2199: 'Victory Spear',
    2200: 'Acid Typhoon',
    2202: 'Blaze Fire',
}

STORY = {
    'MSG/MESPAK02.PAK:026:00133': 'G-g-g-g...!\nNo one can stop us!',
    'MSG/MESPAK02.PAK:026:00134': 'Huh? Where did\nthey go?',
    'MSG/MESPAK02.PAK:026:00135': "Hey, no way!\nIs this what those\nDigimon really are?",
    'MSG/MESPAK02.PAK:026:00136': "I'm so sorry!\nNever again!\nTake my loot!\nForgive me!",
    'MSG/MESPAK02.PAK:026:00137': "Too small now.\nNo more trouble.\nTell Veemon at\nSky Fort!",
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
    previous_output = ROOT / 'translations/batch27.json'
    previous_review = ROOT / 'translations/review_batch27.json'
    old_groups = {}
    if previous_output.exists():
        old = json.loads(previous_output.read_text(encoding='utf-8'))
        for block in old['blocks']:
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    if previous_review.exists():
        for group in json.loads(previous_review.read_text(encoding='utf-8')):
            for value in group['ids']:
                old_groups[value] = group
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    blocks, review, seen = [], [], set()

    def add(key, english, evidence, note, width=None):
        row = by_id.get(key)
        old_group = old_groups.get(key)
        if row is not None:
            ids = row['ids'].split(';')
            category = row['category']
            japanese = row['japanese']
        elif old_group is not None:
            # After a queue refresh, translated source IDs are absent from the
            # queue. Reuse this batch's reviewed ID group so regeneration still
            # works without restoring a stale queue snapshot.
            ids = old_group['ids']
            category = old_group['category']
            japanese = old_group['japanese']
        else:
            raise ValueError(f'Not in refreshed queue or prior review: {key}')
        if any(value in prior or value in seen for value in ids):
            raise ValueError(f'duplicate/already translated: {ids}')
        if any(records[value]['source'] != japanese for value in ids):
            raise ValueError(f'source mismatch: {ids}')
        if width:
            english = wrap(english, width)
        seen.update(ids)
        review.append({'category': category, 'japanese': japanese,
                       'ids': ids, 'english': english, 'evidence': evidence,
                       'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': category,
                           'english': [english], 'sources': sources,
                           'review_note': note})

    for index, english in MOVES.items():
        if index == 2126:
            evidence = DAWN
            note = ('The exact English label Fire Breath appears in the English '
                    'Digimon World: Dawn/Dusk move-name extraction and directly '
                    'matches ほのおのいき. The specific Digimon association still '
                    'needs in-game review.')
        else:
            evidence = DAWN
            note = ('Direct working rendering of the Japanese technique name. '
                    'Checked against the English Dawn/Dusk move-name extraction; '
                    'no exact Western-game match was confirmed for this entry. '
                    'Review the specific move effect and Digimon association in battle.')
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)

    story_note = ('Sky Fort story sequence: the enemy swarm vanishes, the group '
                  'discovers its true form, and Taiki returns to report to Veemon. '
                  'Original names and established area names are retained. Lines '
                  'are kept within the 15-column story renderer limit.')
    for key, english in STORY.items():
        add(key, english, SOURCE, story_note, width=15)

    (ROOT / 'translations/batch27.json').write_text(json.dumps({
        'description': 'Battle techniques and the Sky Fort reveal/report scene.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'translations/review_batch27.json').write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    md = [
        '# Batch 27 translation review',
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
    (ROOT / 'translations/review_batch27.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')


if __name__ == '__main__':
    main()
