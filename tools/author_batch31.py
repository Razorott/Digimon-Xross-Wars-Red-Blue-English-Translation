"""Author a reviewed DigiFarm, side-mission, item, and battle-move batch."""
from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'
XROS_TECHNIQUES = 'https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Guide/Technique'

MOVE_TERMS = {
    'ミヤバルカン': ('Vulcanators', 'B31_WIKIMON_SHOUTMON_X2',
        'Western Digimon Fusion dub name for Shoutmon X2\'s matching elbow-vulcan attack.'),
    'キズナオール': ('Healing Glow', 'B31_WIKIMON_CUTEMON',
        'Established English dub name for Cutemon\'s matching healing attack.'),
    'ヨクナオール': ('Healing Glow II', 'B31_WIKIMON_CUTEMON',
        'Established English dub name for Cutemon\'s stronger healing attack.'),
    'スターズブレイドセレストライク': ("Star's Blade Celestrike", 'B31_WIKIMON_SHOUTMON_X5B',
        'English name recorded for Shoutmon X5B/X4B. The move label is checked against the game\'s 104px box.'),
    'ふどくそう': ('Venom Claw', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation from the game guide: sharp claws containing deadly poison. No exact western game title was verified.'),
    'じゅうおうだけん': ('Beast King Punch', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation. Dawn/Dusk uses Beast King Fist for the related Jūouken, but this source label is Jūoudaken, so the earlier name is not treated as an exact match.'),
    'チンチクリン': ('Shorty', 'B31_WIKIMON_PICKMON',
        'English translation listed for Pickmon\'s matching attack.'),
    'いちのたち': ('First Blade', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the first named sword form; no exact western game title was verified.'),
    'にのたち': ('Second Blade', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the second named sword form; no exact western game title was verified.'),
    'さんのたち': ('Third Blade', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the third named sword form; no exact western game title was verified.'),
    'ほしわり': ('Star Splitter', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the Japanese move name; no exact western game title was verified.'),
    'ナザルネイル': ('Nazar Nail', 'B31_WIKIMON_LILITHMON',
        'Wikimon lists Nazar Nail as the English attack name and Razor Nails as a separate dub alias. Keep Nazar Nail to match the established English attack spelling and the earlier game entry.'),
    'まもる': ('Guard', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Standard English battle command for this defensive move.'),
    'ナッツシュート': ('Seed Blast', 'B31_WIKIMON_LALAMON',
        'English dub name for Lalamon\'s matching Nuts Shoot attack.'),
    'だんがんせんぷう': ('Bullet Cyclone', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the Japanese move name; no exact western game title was verified.'),
    'メットタックル': ('Helmet Tackle', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the Japanese move name; no exact western game title was verified.'),
    'アイオブナイトメア': ('Nightmare Eye', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation of the Japanese move name; no exact western game title was verified.'),
    'ひけんピヨピヨぎり': ('Peep-Peep Slash', 'B31_WIKIMON_XROS_TECHNIQUES',
        'Working translation preserving the Japanese chick-call wordplay; no exact western game title was verified.'),
}

SKILL_TEST_QUEST = {
    82: 'You look like a skilled fighter! We gathered a team of top-notch Digimon to test trainers like you. Our name? The Skill-Test Crew! ...Yeah, we know. It is not creative. Win and there is a big reward in it for you. Interested?',
    83: 'First, find the Skill-Test Crew in West Kumonos Ruins. Beat them, then come back to me for your reward. Good luck!',
    84: 'Great job! Here is your reward. I can vouch for your skill!',
    85: 'How about recruiting a skilled fighter like me? Talk to me any time if you are interested!',
    86: 'So you are the skilled fighter looking for a test? Hold on while I size you up... ... All right! I found a team that matches your skill. Let us go! Ready... BOMB!',
    87: 'You do have some skill! Keep training and you will get even better. Now return to Kabukimon and collect your reward!',
    88: 'You are still rough around the edges. Your skill will fade if you stop training. Do not get cocky. Come back when you are stronger!',
    89: 'So, you think you have skill? We put together a team of elite Digimon to test trainers like you. Our name is... the Skill-Test Crew! ...Yes, it says exactly what it means. Ignore our lack of imagination. Win and there will be a reward. You will not run off, will you?',
    90: 'First, find the Skill-Test Crew in West Kumonos Ruins. Beat them and return here for your reward. Good luck!',
    91: 'Great job! Let us give you your reward. I can vouch for your skill!',
    92: 'They say I am a skilled fighter. Care to recruit me? If you change your mind, just ask.',
    93: 'So you are the skilled fighter looking for a test? Hold on while I size you up... ... All right! I found a team that matches your skill. Let us go! Ready... BOMB!',
    94: 'You do have some skill! Keep training and you will get even better. Now return to Knightmon and collect your reward!',
    95: 'You are still rough around the edges. Your skill will fade if you stop training. Do not get cocky. Come back when you are stronger!',
}

INTERVIEW_QUEST = {
    96: 'Snimon at the DigiFarm asked me to do a favor: interview Dinobeemon in West Guruguru Amazon and record it with this voice recorder. Got it? Dinobeemon, okay?',
    97: 'Please interview Dinobeemon in West Guruguru Amazon and record it on this voice recorder. Just checking... You know who Dinobeemon is, right?',
    98: 'Thanks, you saved me! Here is your reward! Let us hear it right away... Hmm?! Why does this interview audio echo, with background music and everything?',
    100: 'An interview? Sure, leave it to me! You use voice recorders, right? Good thing I already recorded some D-Voice data for just such an occasion!',
    101: 'Tell all the fans I said hello! Yeah! Check it out!',
    102: 'An interview? Who do you think I am? Huh, you want Dinobeemon?! I will knock you flat, you little runt!',
    103: 'I do not care if it is your eyes or your head that are rotten. Learn the difference between an insect and a dragon, will you?!',
    104: 'You are looking for Dinobeemon, right? Quit standing around here and get going!',
}

FARM = {
    56: 'Whoa! I caught it! I am the strongest! My Defense went way up!',
    57: 'No! I lost this time!',
    58: 'Whoa, it is a book! I will read it if you have any fun ones!',
    59: 'Reading is fun sometimes! My Wisdom went up a little!',
    60: 'No! The books are all too hard to read!',
    61: 'Whoa, is this a study desk? Honestly, I will pass on studying!',
    62: 'I powered through my studies! My Wisdom rose, so all that effort paid off!',
    63: 'No! Try all I want, there is no way I am doing this!',
    64: 'Whoa, I know this! It is a magic circle, right?',
    65: 'My mind is clearing by the second! My Wisdom is soaring. I am becoming a genius!',
    66: 'Incredibly, nothing happened at all!',
    67: 'Side-to-side jumps? I am great at those!',
    68: 'Whoa, I am on a roll! New record! My Speed went up a fair bit!',
    69: 'Whoa, I am exhausted! I am done!',
    70: 'Whoa, a trampoline! Looks fun. I am jumping on!',
    71: 'Jumping so high gets me pumped! My Speed went up quite a bit!',
    72: 'No! All this bouncing is making me sick!',
    73: 'What is this thing?! A running wheel?! I just run inside it?',
    74: 'Whoa, I really ran a lot! My Speed seems to have gone up a ton!',
    75: 'Whoa, my head and body are spinning around!',
    76: 'This is a Digimon keychain! Looks fun! I am going to try it!',
    77: 'Whoa, this is great! That game was the best! My Friendship went up a little!',
    78: 'Ugh, this is hard! I will keep trying!',
    79: 'What is this?! A cell phone?! I will text Taiki right now!',
    80: 'Whoa, Taiki replied! My Friendship went up a good amount!',
    81: 'No reply yet... I am disappointed!',
    82: 'This digital camera belongs to Taiki, huh? I will take a picture of myself!',
    83: 'Whoa, success! The picture came out perfectly! My Friendship went up a lot!',
    84: 'What?! I have no idea how to use this!',
    85: 'Whoa! I found a ring of fire here! Jumping through it is easy!',
}

MEMORY_ITEMS = {
    36: 'MA Angemon DigiMemory. Disappears after one use in battle.',
    38: 'HL Angemon DigiMemory. Disappears after one use in battle.',
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
        'B31_WIKIMON_XROS_TECHNIQUES': {
            'url': XROS_TECHNIQUES,
            'title': 'Digimon Story: Super Xros Wars Japanese technique guide',
            'kind': 'secondary game reference',
            'notes': 'Used to verify Japanese battle move labels and effects. English titles are labeled working translations unless an established Western name is cited.'
        },
        'B31_WIKIMON_SHOUTMON_X2': {
            'url': 'https://wikimon.net/Shoutmon_X_2',
            'title': 'Shoutmon X2 attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Records Vulcanators as the English dub name for Miya Vulcan.'
        },
        'B31_WIKIMON_CUTEMON': {
            'url': 'https://wikimon.net/Cutemon',
            'title': 'Cutemon attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Records Healing Glow and Healing Glow II as English dub names for Kizunaol and Yokunaol.'
        },
        'B31_WIKIMON_SHOUTMON_X5B': {
            'url': 'https://wikimon.net/Shoutmon_X5B',
            'title': 'Shoutmon X5B attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Records Star\'s Blade Celestrike as the English rendering for the matching Xros Wars attack.'
        },
        'B31_WIKIMON_PICKMON': {
            'url': 'https://wikimon.net/Pickmon',
            'title': 'Pickmon attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Lists Shorty as the English translation of Chinchikurin.'
        },
        'B31_WIKIMON_LILITHMON': {
            'url': 'https://wikimon.net/Lilithmon',
            'title': 'Lilithmon attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Lists Razor Nails as the English dub name for Nazar Nail.'
        },
        'B31_WIKIMON_LALAMON': {
            'url': 'https://wikimon.net/Lalamon',
            'title': 'Lalamon attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Lists Seed Blast as the English dub name for Nuts Shoot.'
        },
        'B31_BANDAI_DINOBEEMON': {
            'url': 'https://world.digimoncard.com/cards/?card_no=BT20-074&search=true',
            'title': 'Bandai English card list: Dinobeemon BT20-074',
            'kind': 'primary',
        },
        'B31_BANDAI_SNIMON': {
            'url': 'https://world.digimoncard.com/rule/pdf/starter_deck_4.pdf',
            'title': 'Bandai English starter deck rules: Snimon ST9-10',
            'kind': 'primary',
        },
    }
    for key, value in additions.items():
        if key in sources and sources[key] != value:
            raise ValueError(f'Glossary source changed unexpectedly: {key}')
        sources[key] = value

    terms = glossary['terms']
    for japanese, (english, source_id, evidence) in MOVE_TERMS.items():
        term = {'japanese': japanese, 'english': english, 'category': 'Move name',
                'sources': [source_id], 'evidence': evidence}
        old = next((item for item in terms if item['japanese'] == japanese), None)
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting glossary term: {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + [source_id]))
            old['evidence'] = evidence
        else:
            terms.append(term)

    for japanese, english, source_id in [
        ('スナイモン', 'Snimon', 'B31_BANDAI_SNIMON'),
        ('ディノビーモン', 'Dinobeemon', 'B31_BANDAI_DINOBEEMON'),
    ]:
        term = {'japanese': japanese, 'english': english, 'category': 'Digimon name',
                'sources': [source_id],
                'evidence': 'Official English card material confirms this Western species spelling.'}
        old = next((item for item in terms if item['japanese'] == japanese), None)
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting Digimon term: {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + [source_id]))
        else:
            terms.append(term)
    glossary['checked'] = '2026-10-25'
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    register_glossary()
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    old_path = ROOT / 'translations/batch31.json'
    if old_path.exists():
        old = json.loads(old_path.read_text(encoding='utf-8'))
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    blocks, reviews, seen = [], [], set()

    def add(key: str, english: str, evidence: str = LOCAL, note: str = '',
            width: int | None = None, force: bool = False) -> None:
        if key in prior and not force:
            return
        row = by_id.get(key)
        if row is None:
            raise ValueError(f'Not found in untranslated queue: {key}')
        ids = row['ids'].split(';')
        if all(value in seen for value in ids):
            return
        if any((value in prior and not force) or value in seen for value in ids):
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

    quest_note = ('Optional Skill-Test Crew challenge quest. The name localizes the Japanese ude-dameshi pun as a deliberately plain test-of-skill group name; original names and area labels follow project terminology.')
    for index, english in SKILL_TEST_QUEST.items():
        add(f'MSG/MESPAK02.PAK:020:{index:05d}', english, LOCAL, quest_note, width=15)

    interview_note = ('Optional DigiFarm interview quest translated from the Japanese ROM. Snimon and Dinobeemon use checked Western spellings; Guruguru Amazon West follows the existing map label.')
    for index, english in INTERVIEW_QUEST.items():
        add(f'MSG/MESPAK02.PAK:020:{index:05d}', english, LOCAL, interview_note, width=15)

    move_sources = {key: value[1] for key, value in MOVE_TERMS.items()}
    move_notes = {key: value[2] for key, value in MOVE_TERMS.items()}
    move_indexes = {
        'ミヤバルカン': 1926, 'キズナオール': 1946, 'ヨクナオール': 1948,
        'スターズブレイドセレストライク': 1955, 'ふどくそう': 1956,
        'じゅうおうだけん': 1957, 'チンチクリン': 1975,
        'いちのたち': 1988, 'にのたち': 1989, 'さんのたち': 1990,
        'ほしわり': 1991, 'ナザルネイル': 1996, 'まもる': 2001,
        'ナッツシュート': 2032, 'だんがんせんぷう': 2034,
        'メットタックル': 2035, 'アイオブナイトメア': 2036,
        'ひけんピヨピヨぎり': 2042,
    }
    for japanese, index in move_indexes.items():
        source_id = move_sources[japanese]
        source_url = XROS_TECHNIQUES if source_id == 'B31_WIKIMON_XROS_TECHNIQUES' else json.loads((ROOT / 'translations/glossary.json').read_text(encoding='utf-8'))['sources'][source_id]['url']
        note = move_notes[japanese]
        if japanese == 'スターズブレイドセレストライク':
            note += ' Full source title retained; if it exceeds the 104px move-name field, shorten only the in-game label and keep the complete English name here.'
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', MOVE_TERMS[japanese][0],
            source_url, note, force=True)

    farm_note = ('DigiFarm training report translated from the Japanese ROM. Strength, Defense, Wisdom, Speed, and Friendship match the English status terminology.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:003:{index:05d}', english, LOCAL, farm_note, width=26)

    item_note = ('DigiMemory description translated from the Japanese item table. MA and HL are retained as the game\'s variant prefixes; the exact expanded form is not established in the project sources.')
    for index, english in MEMORY_ITEMS.items():
        add(f'MSG/MESPAK04.PAK:029:{index:05d}', english, LOCAL, item_note, width=26)

    description = 'Skill-Test Crew and DigiFarm interview side missions, battle moves, DigiFarm reports, two DigiMemory descriptions, and the Call Allies sprite label.'
    out = ROOT / 'translations/batch31.json'
    review_json = ROOT / 'translations/review_batch31.json'
    review_md = ROOT / 'translations/review_batch31.md'
    out.write_text(json.dumps({'description': description, 'blocks': blocks},
                              ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Batch 31 translation review', '',
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

    counts = {}
    for group in reviews:
        counts[group['category']] = counts.get(group['category'], 0) + len(group['ids'])
    print(f'{len(blocks)} text slots from {len(reviews)} reviewed Japanese groups')
    print('Categories:', json.dumps(counts, ensure_ascii=False))


if __name__ == '__main__':
    main()
