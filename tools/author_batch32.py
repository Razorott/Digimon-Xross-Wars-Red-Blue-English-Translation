"""Author a reviewed story, battle, menu, DigiFarm, and item batch."""
from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'
TECHNIQUES = 'https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Guide/Technique'
CARD_LIST = 'https://world.digimoncard.com/cards/'
DAWN_DUSK = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

CRYSTAL_QUEST = {
    21: "Ugh... I lost. I got careless. Don't ask whether I would have won otherwise!",
    22: "Darn that giant MegaGargomon! He won't escape from Crystal Volcano!",
    23: "Ugh... I lost. I underestimated him. Let's not discuss whether that would have changed anything.",
    24: "Grrr, MegaGargomon! I'll corner and finish him at Crystal Volcano!",
    25: "Ugh... I lost. He really was as strong as the rumors said.",
    26: "Oh no... If MegaGargomon escapes Crystal Volcano, we'll never catch him...",
    27: "Ugh... I almost had him! Don't ask what would've happened. You know better!",
    28: "Aaagh! MegaGargomon! I'll never let him escape Crystal Volcano!",
    29: "Ugh... I lost. But he's finished! I cornered him in Crystal Cave...",
    30: "Please... finish MegaGargomon in Crystal Cave...!",
    31: "You came to finish me? ...Me? At the Mame-Mame and Gira-Gira Gangs' request? I haven't even lost to them! I'm not losing to those little runts!",
    32: "Well... I lost, I'll admit it. But I didn't lose to those little guys! Remember that!",
    33: "I don't care who won. I stepped on those little twerps by accident! Tell them I'm sorry. They were too small to see.",
    34: "I can't forgive MegaGargomon! That big guy does whatever he wants! The Mame-Mame Gang is back, and we're teaming up with the Gira-Gira Gang to take him down! Taiki, help us! Meet our friends at Crystal Volcano!",
    35: "Everyone else is already at Crystal Volcano! Go join them and be their bodyguard, Taiki!",
    36: "Thanks, Taiki! Here's your reward! The Gira-Gira and Mame-Mame Gangs have fought for ages, but we're really alike. Together, no one can stop us!",
    37: "Want to recruit me? If you do, just say the word!",
    46: "Ugh... I lost. But he's finished! I cornered him in Crystal Cave...",
    47: "Please... finish MegaGargomon in Crystal Cave...!",
    48: "You came to finish me? ...Me? At the Gira-Gira and Mame-Mame Gangs' request? I haven't even lost to them! I'm not losing to those little runts!",
}

STELE_QUEST = {
    71: "I found a suspicious stone tablet in Kumonos Underground Passage... It looked so creepy that I was afraid to touch it. But I can't stop thinking about it. Could you investigate it for me?",
    72: "Please investigate the suspicious tablet in Kumonos Underground Passage. It should be easy to spot...",
    73: "Thanks for checking the tablet! Its guardian spoke? It said, 'Do not break the seal. Do not wake the sleeper.' What seal? Who's sleeping? Anyway, here's your reward.",
    74: "Thanks, Taiki! I'll research that strange tablet and see what I can find.",
    75: "I found more strange tablets! One in Papyrus Cave and another beneath Crystal Volcano. A tablet spirit appeared, so I ran away! Could you investigate them too?",
    76: "The strange tablets are in Papyrus Cave and beneath Crystal Volcano. Please check them out!",
    77: "Thanks, Taiki! Here's your reward. That tablet guardian seemed furious... Maybe it hates being woken up, or maybe someone did something to anger it...",
    78: "I think we'll learn more if we keep researching. I'll contact you if I find anything!",
    79: "I found another strange tablet in Stealth Cave! This time, it really feels like something is there! Could you investigate it for me?",
    80: "Please investigate the tablet in Stealth Cave! This one seems really dangerous, so be careful!",
    81: "Thanks, Taiki! What happened? ...Oh, AncientWisemon angered the tablet guardian. It planned to revive the Ancient Digimon and take over the world? No wonder the guardian was furious! And you got a Score as thanks for helping? Amazing! This will become Shoutmon ×3 SD. I'll tune it for you... Done!",
    82: "Please accept a reward from me, too!",
    83: "The mystery that worried me is finally solved. Now I can relax. Thanks, Taiki!",
}

CLONE_QUEST = {
    84: "I've been getting strange reports from Digital Space. When I went to investigate, I met Parrotmon. It was looking for you, Taiki. Could you go see what it wants?",
    85: "Parrotmon is looking for you, Taiki. Please meet it in East Digital Space!",
    86: "That wasn't Parrotmon?! It was some kind of copy? And there are more and more of them? Something strange is happening in Digital Space... Anyway, here's your reward!",
    87: "I'll let you know if anything happens, Taiki. Please help us again!",
    88: "Something strange is happening all over this Zone. Data use is increasing at an abnormal rate. Remember the fake Parrotmon? East Digital Space is acting strangely. Could you investigate?",
    89: "Data use is growing at an alarming rate in East Digital Space. Please find out what's happening!",
    90: "A Digimon is copying itself and multiplying?! That sounds dangerous... But why would it do that? Anyway, please take your reward!",
    91: "There are strange Digimon everywhere, but none of them think about the consequences... I'll investigate a little more and ask for your help if I need it.",
    92: "There's an emergency in North Lost Space! Data use is skyrocketing. If this continues, Digimon will get hurt. Taiki, please stop whatever is causing this!",
    93: "The disturbance is in North Lost Space. We don't know what's behind it, but please stop it!",
    94: "The culprit was Kuramon? I'm relieved, but a little disappointed. I expected something more dangerous. I'll process the data you brought back... Done! This is Shoutmon ×3 GM!",
    95: "And please accept a reward from me, too!",
    96: "Thanks, Taiki! I knew I could count on you!",
}

FARM = {
    86: "Whoa! How was that? Easy! My body, spirit, and EXP are all fired up!",
    87: "N-no! It's too hot! I'm going to get roasted!",
    88: "Fire Road?! It's so hot! Do I have to cross it?!",
    89: "I endured the heat! Success! My EXP went up a fair bit!",
    90: "Whoa, way too hot! No way I can do this!",
    91: "Fireworks! Let me launch them with a bang!",
    92: "Whoa, huge! That was awesome! My EXP shot up too!",
    93: "Nothing's launching! Is the gunpowder damp, or am I a dud?!",
    94: "Whoa, this ball is huge! I'll roll around on it!",
    95: "This is fun! Feels great! My EXP went up a little!",
    96: "Why are all of you spinning, too?! Wait... am I dizzy?!",
    97: "Whoa, tightrope walking! I've always wanted to try it!",
    98: "I did it! Easier than I thought! My EXP went up a fair bit!",
    99: "Whoa, I fell! That really hurt!",
}

MOVE_TERMS = {
    'とうはっけん': ('Eight-Fist Barrage', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working name from the game guide: a flurry of powerful palm strikes against nearby foes. No exact Western game title was verified.'),
    'ドルディーン': ('Dordeen', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Retains the game guide romanization. The attack is a fiery shock wave that lowers Speed; no exact Western title was verified.'),
    'ばくオヤジパンチ': ('Old Man Blast Punch', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working rendering that keeps the oyaji (old man) wordplay; the guide describes an explosive punch with bonus fire damage.'),
    'アラクノバトト': ('Poison Cobweb', 'B32_WIKIMON_DOKUGUMON',
        'Established English dub alias for Dokugumon\'s matching Arachno Batoto web attack.'),
    'サブバルカン': ('Sub Vulcan', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working romanization. The game guide describes firing both hand-mounted Vulcan cannons at nearby foes.'),
    'パオツェイ': ('Treasure Mallet', 'B32_WIKIMON_CATURAMON',
        'Established English translation for Caturamon\'s Bǎo Chuí, the same Treasure Mallet named by this game move.'),
    'シュヴァボージャナ': ('Howl of Power', 'B32_WIKIMON_CATURAMON',
        'English dub name listed for Caturamon\'s matching Śwabhojana attack.'),
    'ぜっこうしょう': ('Blinding Light', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working translation based on the guide description: light from earrings blinds nearby foes and lowers Wisdom.'),
    'ロストルム': ('Rostrum', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working romanization retained as a move name; the guide describes dragging nearby foes underwater and swallowing them.'),
    'キングオブロッカー': ('King of Locker', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working romanization retained because the game guide marks this move entry as placeholder text, leaving the intended meaning unclear.'),
    'ブレイクロッカー': ('Break Locker', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working romanization. The guide describes swinging a microphone to strike nearby foes; no exact Western title was verified.'),
    'Ｆテンプテーション': ('FTemptation', 'B32_DAWN_DUSK',
        'Exact English move spelling reused from the licensed Dawn/Dusk move list.'),
    'Ｅニルヴァーナ': ('E Nirvana', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working rendering of the game-specific label; no matching Dawn/Dusk or Western title was found.'),
    'ＥＸＴジハード': ('EXT Jihad', 'B32_WIKIMON_XROS_TECHNIQUES',
        'Working rendering of the game-specific label; no matching Dawn/Dusk or Western title was found.'),
}

MOVE_INDEXES = {
    'とうはっけん': 2025, 'ドルディーン': 2054, 'ばくオヤジパンチ': 2057,
    'アラクノバトト': 2074, 'サブバルカン': 2082, 'パオツェイ': 2087,
    'シュヴァボージャナ': 2088, 'ぜっこうしょう': 2090,
    'ロストルム': 2170, 'キングオブロッカー': 2174,
    'ブレイクロッカー': 2189, 'Ｆテンプテーション': 2649,
    'Ｅニルヴァーナ': 2672, 'ＥＸＴジハード': 2673,
}
MOVE_GROUP_IDS = {
    'とうはっけん': [2025, 3301], 'ドルディーン': [2054, 3330],
    'ばくオヤジパンチ': [2057, 3333], 'アラクノバトト': [2074, 3350],
    'サブバルカン': [2082, 3358], 'パオツェイ': [2087, 3363],
    'シュヴァボージャナ': [2088, 3364], 'ぜっこうしょう': [2090, 3366],
    'ロストルム': [2170, 3446], 'キングオブロッカー': [2174, 3450],
    'ブレイクロッカー': [2189, 3465], 'Ｆテンプテーション': [2649, 3619],
    'Ｅニルヴァーナ': [2672, 3604], 'ＥＸＴジハード': [2673, 3599],
}

OBJECT_LABELS = {
    1: 'Airport', 2: 'DigiLab', 3: 'DigiFarm', 4: 'Quest Monitor',
    5: 'Tent Point', 7: 'ATM', 8: 'Item Shop',
    23: 'Switch Gate', 24: 'Treasure', 25: 'Enemy Box',
    26: 'Enemy Box G', 27: 'Skill Points',
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
        'B32_WIKIMON_XROS_TECHNIQUES': {
            'url': TECHNIQUES,
            'title': 'Digimon Story: Super Xros Wars Japanese technique guide',
            'kind': 'secondary game reference',
            'notes': 'Used to confirm Japanese move labels and attack effects. English titles are marked as working translations unless an established Western name is cited.'
        },
        'B32_WIKIMON_DOKUGUMON': {
            'url': 'https://wikimon.net/Dokugumon',
            'title': 'Dokugumon attack names',
            'kind': 'secondary franchise reference',
            'notes': 'Records Poison Cobweb among the English dub aliases of Arachno Batoto.'
        },
        'B32_WIKIMON_CATURAMON': {
            'url': 'https://wikimon.net/Caturamon',
            'title': 'Caturamon attack names and Bǎo Chuí',
            'kind': 'secondary franchise reference',
            'notes': 'Records Howl of Power as the English dub name for Śwabhojana and Treasure Mallet as the English translation of Bǎo Chuí; Pao Tsei is a romanization of the Japanese katakana name.'
        },
        'B32_DAWN_DUSK': {
            'url': DAWN_DUSK,
            'title': 'English Digimon World: Dawn/Dusk move-name extraction',
            'kind': 'community extraction of licensed game text',
            'notes': 'FTemptation is reused only where the Japanese move label matches.'
        },
        'B32_BANDAI_MEGA_GARGOMON': {
            'url': 'https://world.digimoncard.com/cards/?card_no=BT3-057&search=true',
            'title': 'Bandai English card list: MegaGargomon BT3-057',
            'kind': 'primary',
            'notes': 'Confirms the Western spelling for セントガルゴモン.'
        },
        'B32_BANDAI_RUKAMON': {
            'url': 'https://p-bandai.com/us/contents/div/2030/images/Digimon%20Pendulum%20Color_Web%20manual_EN%20%281%29.pdf',
            'title': 'Bandai Digimon Pendulum Color English manual',
            'kind': 'primary',
            'notes': 'Uses the Western name Rukamon in English product material.'
        },
        'B32_BANDAI_CARDS': {
            'url': CARD_LIST,
            'title': 'Bandai official English Digimon Card Game card list',
            'kind': 'primary',
            'notes': 'Reference for established Western Digimon spellings; game-specific variant suffixes are retained from the reviewed display-name table.'
        },
    }
    for key, value in additions.items():
        if key in sources and sources[key] != value:
            raise ValueError(f'Glossary source changed unexpectedly: {key}')
        sources[key] = value

    terms = glossary['terms']
    def put_term(japanese: str, english: str, category: str, source_id: str,
                 evidence: str) -> None:
        old = next((item for item in terms if item['japanese'] == japanese), None)
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting glossary term: {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + [source_id]))
            old['evidence'] = evidence
        else:
            terms.append({'japanese': japanese, 'english': english,
                          'category': category, 'sources': [source_id],
                          'evidence': evidence})

    for japanese, (english, source_id, evidence) in MOVE_TERMS.items():
        put_term(japanese, english, 'Move name', source_id, evidence)

    put_term('セントガルゴモン', 'MegaGargomon', 'Digimon name',
             'B32_BANDAI_MEGA_GARGOMON',
             'Bandai English card material confirms this Western species spelling.')
    put_term('ルカモン', 'Rukamon', 'Digimon name', 'B32_BANDAI_RUKAMON',
             'Bandai English product material uses Rukamon.')

    layout = json.loads((ROOT / 'translations/display_name_layout.json').read_text(encoding='utf-8'))
    for entry in layout:
        if entry['japanese'] not in {
            'ユキダルモン','ルカモン','アグニモン','ＭＥグレイモンＬ','スカルグレイモン',
            'エンジェウーモン','ティロモン','レディーデビモン','ガルダモン','ＡカブテリモンＲ',
            'タオモン','パロットモン','パンダモン','シンドゥーラモン','ホエーモン','チィリンモン',
            'ジュレイモン','ＥＸティラノモン','フレイドラモン','バステモン','ケルベロモン',
            'ブルーメラモン','スコピオモン','ネフェルティモン','チャツラモン','デュークモン',
            'ＢＡＮレオモン','ゴッドドラモン','ヴァルキリモン','ファラオモン','スピノモン',
            'Ａボルケーモン','ダイペンモン','プラチナヌメモン','ディノレクスモン','カオスドラモン',
            'オグドモン','モニタモン','ドンドコモン','ボムモン','シャウトモンＢ','グレイモンＯ',
            'ＳナイトモンＢＲ','マッドレオモン','タクティモン','ブラストモン','ガオスモン',
            'トループモン','チクリモン','チビックモン'
        }:
            continue
        jp, en = entry['japanese'], entry['formal']
        if jp == 'ガオスモン':
            en = 'Gaossmon'
        if jp == 'ルカモン':
            source_id = 'B32_BANDAI_RUKAMON'
        else:
            source_id = 'B32_BANDAI_CARDS'
        put_term(jp, en, 'Digimon name', source_id,
                 'Formal Western spelling reused from the reviewed display-name table; variant suffixes remain game-specific where present.')
    glossary['checked'] = '2026-10-25'
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    register_glossary()
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    old_batch = ROOT / 'translations/batch32.json'
    if old_batch.exists():
        old = json.loads(old_batch.read_text(encoding='utf-8'))
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    old_review = ROOT / 'translations/review_batch32.json'
    if old_review.exists():
        for item in json.loads(old_review.read_text(encoding='utf-8')):
            synthetic = {'ids': ';'.join(item['ids']),
                         'japanese': item['japanese'],
                         'category': item['category']}
            for key in item['ids']:
                by_id.setdefault(key, synthetic)
    for japanese, indexes in MOVE_GROUP_IDS.items():
        ids = [f'MSG/MESPAK00.PAK:000:{index:05d}' for index in indexes]
        synthetic = {'ids': ';'.join(ids), 'japanese': japanese,
                     'category': 'Battle moves'}
        for key in ids:
            by_id.setdefault(key, synthetic)
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

    crystal_note = ('Optional side mission about MegaGargomon and two rival tiny-Digimon gangs. MegaGargomon follows Bandai English spelling; Crystal Cave and Crystal Volcano match earlier translated quest labels. Gang names are working transliterations that preserve the original joke.')
    for index, english in CRYSTAL_QUEST.items():
        add(f'MSG/MESPAK02.PAK:021:{index:05d}', english, LOCAL, crystal_note, width=15)

    stele_note = ('Optional stone-tablet investigation quest. AncientWisemon uses the reviewed Western Digimon name; Shoutmon x3 SD is preserved as a DigiXross form label.')
    for index, english in STELE_QUEST.items():
        add(f'MSG/MESPAK02.PAK:022:{index:05d}', english, LOCAL, stele_note, width=15)

    clone_note = ('Optional investigation quest about copying Parrotmon and runaway data growth. Parrotmon and Kuramon use the established Western names; Digital Space, North Lost Space, and the two Shoutmon ×3 forms follow project terminology.')
    for index, english in CLONE_QUEST.items():
        add(f'MSG/MESPAK02.PAK:022:{index:05d}', english, LOCAL, clone_note, width=15)

    source_urls = {key: value['url'] for key, value in json.loads(
        (ROOT / 'translations/glossary.json').read_text(encoding='utf-8'))['sources'].items()}
    for japanese, index in MOVE_INDEXES.items():
        english, source_id, note = MOVE_TERMS[japanese]
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english,
            source_urls[source_id], note, force=True)

    farm_note = ('DigiFarm activity report translated from the Japanese source. EXP, Speed, and other stat labels follow the project’s established English status terminology.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:003:{index:05d}', english, LOCAL, farm_note, width=26)

    name_map = {entry['japanese']: ('Gaossmon' if entry['japanese'] == 'ガオスモン'
                                   else entry['formal']) for entry in json.loads(
        (ROOT / 'translations/display_name_layout.json').read_text(encoding='utf-8'))}
    name_keys = sorted(name_map, key=len, reverse=True)
    name_sources = {
        'ルカモン': 'B32_BANDAI_RUKAMON',
    }
    glossary = json.loads((ROOT / 'translations/glossary.json').read_text(encoding='utf-8'))
    for source_id in glossary['sources']:
        if source_id.startswith('B32_BANDAI_CARDS'):
            name_sources['*'] = source_id
    ticket_note = ('DigiMemory gift ticket. The Digimon’s full Western spelling comes from the reviewed display-name table; game-only form suffixes are retained. The listed name is used as the recipient.')
    for index in range(50):
        key = f'MSG/MESPAK04.PAK:042:{index:05d}'
        row = by_id[key]
        japanese = row['japanese']
        species_jp = next((jp for jp in name_keys if jp in japanese), None)
        name = name_map.get(species_jp)
        if not name:
            raise ValueError(f'No reviewed Western Digimon name in ticket {index}: {japanese}')
        source_id = name_sources.get(species_jp, name_sources['*'])
        evidence = glossary['sources'][source_id]['url']
        note = ticket_note + f' Recipient: {name} ({species_jp}).'
        add(key, f'Gift from:\n{name}\nRedeem at Service Counter.',
            evidence, note, width=26)

    menu_note = ('Map/facility label translated from the Japanese UI string; established project casing is used for named facilities.')
    for index, english in OBJECT_LABELS.items():
        add(f'MSG/MESPAK01.PAK:008:{index:05d}', english, LOCAL, menu_note)

    description = ('Crystal Volcano/MegaGargomon and stone-tablet/copying side quests; DigiFarm reports; official-name DigiMemory gift tickets; fourteen battle moves; and facility/map labels. The previous 229 localized graphic states are retained.')
    out = ROOT / 'translations/batch32.json'
    review_json = ROOT / 'translations/review_batch32.json'
    review_md = ROOT / 'translations/review_batch32.md'
    out.write_text(json.dumps({'description': description, 'blocks': blocks},
                              ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Batch 32 translation review', '',
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

    counts: dict[str, int] = {}
    for group in reviews:
        counts[group['category']] = counts.get(group['category'], 0) + len(group['ids'])
    print(f'{len(blocks)} text slots from {len(reviews)} reviewed Japanese groups')
    print('Categories:', json.dumps(counts, ensure_ascii=False))


if __name__ == '__main__':
    main()
