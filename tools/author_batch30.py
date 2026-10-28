"""Author a reviewed optional-quest, battle, DigiFarm, and item batch."""
from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'
XROS_TECHNIQUES = 'https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Guide/Technique'
SIESAMON = 'https://wikimon.net/Siesamon'
APOCALYMON = 'https://wikimon.net/Apokarimon'
PANDAMON = 'https://wikimon.net/Pandamon'
CHIMERAMON = 'https://wikimon.net/Kimeramon'
PIEMON = 'https://wikimon.net/piemon'
MUSHMON_CARD = 'https://wikimon.net/St-788'
GRADALPHA = 'https://t2sc.me/userfiles/62609410959.pdf'
CARD_LIST = 'https://world.digimoncard.com/cards/'


MOVE_TERMS = {
    'グランデスビッグバン': ('Grand Big Bang', APOCALYMON,
        'Apocalymon attack name: Grand Big Bang is a documented English rendering; other dub references also use Total Annihilation. No exact Dawn/Dusk move match was found.'),
    'らいこういっせんのつき': ('Lightning Flash Thrust', XROS_TECHNIQUES,
        'Working translation of the Xros Wars technique label. The same-game guide describes a lightning thrust; no exact Western game name was found.'),
    'ハイブリットアームズ': ('Hybrid Arms', CHIMERAMON,
        'Same English move name used for Chimairamon in earlier Digimon game material; the Xros Wars guide describes the matching multi-arm attack.'),
    'エンディングスナイプ': ('Ending Snipe', PIEMON,
        'Existing English attack name for Piedmon in other Digimon games; the Xros Wars guide confirms the same Japanese name.'),
    'せいけんグレイダルファー': ('Blade of Dragon King', GRADALPHA,
        'Compact English rendering of the same Japanese Alphamon move listed as Blade of the Dragon King in an English Cyber Sleuth data extraction; shortened to fit the 104px move-name slot.'),
    'グッドナイト・ムーン': ('Goodnight Moon', XROS_TECHNIQUES,
        'Working English rendering of the Japanese Xros Wars move name; no exact Western game match was found.'),
    'スパイラルマスカレード': ('Spiral Masquerade', XROS_TECHNIQUES,
        'Working English rendering of the Japanese Xros Wars move name; no exact Western game match was found.'),
    'ウンナンショウ': ('Firecracker', PANDAMON,
        'English dubbed attack name for Pandamon; the Xros Wars guide describes the same firecracker explosion.'),
    'パンドーラ・ダイアログ': ('Pandora Dialog', XROS_TECHNIQUES,
        'Working English form of the established attack name; no exact Western game match was found.'),
    'ラフ・ス・マッシュ': ('Rough S-Mush', MUSHMON_CARD,
        'English card-game rendering of Mushmon’s attack, matched to the Japanese label.'),
    'ティーダ・イヤ': ("Sun's Courage", SIESAMON,
        'English translation of the same Japanese move name in Siesamon material. Its Xros Wars move effect differs, so this is a name match rather than an effect match.'),
    'せっかんとう': ('Ancient Firewall', SIESAMON,
        'English reference rendering for Sekkantou. The Xros Wars guide confirms the same protective move; no English game attack title was found.'),
    'マイティサンダークロー': ('Mighty Thunder Claw', XROS_TECHNIQUES,
        'Working English rendering from the Japanese move label; no exact prior Western move-name match was found.'),
    'ジャスティスブリット': ('Justice Bullet', XROS_TECHNIQUES,
        'Working English rendering from the Japanese move label; no exact prior Western move-name match was found.'),
}


TERRIELLOP_QUEST = {
    5: 'A new Terriellop CD is out!♪ Could you ask their manager, LadyDevimon, for an autographed copy? She is in West Kumonos Ruins!',
    6: 'Please get me an autographed Terriellop CD by asking their manager, LadyDevimon! She is in West Kumonos Ruins!',
    7: '...... Ah, I am so moved!♪ I might start singing before I even play it...♪ Thank you so much! Please take this reward!',
    8: '...... Huh? Oh, sorry. I got carried away.♪ Hmm hmm hmm...♪',
    9: 'What? Another autograph? I cannot worry about that now! Terriellop\'s important System Notebook has gone missing! Without it, I cannot get in touch with them! Please find it quickly!',
    10: 'It went missing after Terriellop visited South Papyrus Desert. They must have dropped it there. Search South Papyrus Desert!',
    11: 'Thank you! Now I can check where Terriellop is. Let me see... They are making an appearance at East Skull Iceberg! I will pass on your request. Ask them for the autograph yourself!',
    0: 'Terriellop is at East Skull Iceberg. I will let them know you want an autograph, so ask them yourself!',
    12: 'Terriellop is at East Skull Iceberg. I will let them know you want an autograph, so ask them yourself!',
    1: 'Ah! Are you one of our fans? Our manager asked us to sign this CD. Have we met before? No? I do not remember... Do not say you were a fan back when we were obscure, okay? Or post our weird old photos online... Ha ha... Here, take the CD!',
    13: 'Ah! Are you one of our fans? Our manager asked us to sign this CD. Have we met before? No, right? I do not remember... Do not say you were a fan back when we were obscure, okay? Or post our weird old photos online... Ha ha... Here, take the CD!',
    2: 'Keep supporting Terriellop! Teri-ro-ri-lop!▼ ...... Hmph... Did I just say something weird? I did not, right?',
    14: 'Keep supporting Terriellop! Teri-ro-ri-lop!▼ ...... Hmph... Did I just say something weird? I did not, right?',
    3: 'I hear you! You are one of our fans, right? Thanks for always supporting us!▼ LadyDevimon told me about you. Here is your CD. Now get out of here... See ya! S-sorry! I am a little worn out... My usual tact just vanished!',
    15: 'I hear you! You are one of our fans, right? Thanks for always supporting us!▼ LadyDevimon told me about you. Here is your CD. Now get out of here... See ya! S-sorry! I am a little worn out... My usual tact just vanished!',
    4: 'You have only seen us at our most embarrassing... Please give us a little more time. We will make it big! Keep supporting Terriellop! Teri-ro-ri-lop!▼ ... Heh... Haha...',
    16: 'You have only seen us at our most embarrassing... Please give us a little more time. We will make it big! Keep supporting Terriellop! Teri-ro-ri-lop!▼ ... Heh... Haha...',
}


RESCUE_QUEST = {
    10: 'The shining superstar of El Estow Zone! Can I really get Terriellop\'s autograph? I am amazed you are not afraid of their scary manager, LadyDevimon! Please get me an autograph and I will reward you! LadyDevimon is in West Kumonos Ruins.',
    11: 'Maybe I should ask the manager, LadyDevimon, first. That old-fashioned, monochrome lady is in West Kumonos Ruins.',
    12: 'Yaaah! Aaaah...! I screamed loud enough to shatter glass! Thank you from the bottom of my heart! I got so overwhelmed that I wore myself out, but please take this reward!',
    13: 'Would you like to recruit me? If you do, come talk to me anytime!',
    14: 'E-everyone! This is an emergency! Help! Terriellop has been kidnapped! Who did it? I have no idea! All I know is they ran into Digital Space! Please hurry and save Terriellop!',
    15: 'Please find and rescue Terriellop! It sounds like the culprit escaped into Digital Space! If anything happens to them, I will not be able to go on!',
    16: 'Quick, take the autographs over. Give one to Numesuka and Terriellop, of course... And keep what happened absolutely secret! Got it?',
    17: 'Trying to get past me? Do not lie, baby! You are looking for me... me, or maybe... me! I can feel your heart racing, and it is making mine burst, baby!▼',
    18: 'That fierce heat of yours has my heart beating, baby! You almost knocked me out, baby!▼',
    19: 'You came to rescue me? Thank you! I was getting lost, so I was in a bit of a bind... Huh? Kidnapped? I have no idea what you mean. I was with Numesuka for a while... It is so peaceful when fans are not swarming us!♪',
    20: 'Could you check where Lopmon is, too? I think they are somewhere nearby...',
    21: 'I want to thank you for coming all this way to rescue me... Could you come meet LadyDevimon? Lopmon and I will wait there!♪',
    22: 'Hi there, honey! Did you drop a gold autograph? A silver one? Or this Numesuka autograph? None of them? Oh, right, honey... Because what you dropped was my heart! Right, honey?▼',
    23: 'I caught your shy feelings, honey! See you later! Get home safe, honey!▼',
    24: 'Oh! You came to pick me up? I was resting because I got a little tired... Kidnapped? What are you talking about? I felt so safe with Numesuka! They must have gone home already.',
    25: 'Terriermon should be nearby, too. Could you find them for me?',
    26: 'I want to thank you for coming to pick me up. Could you come to LadyDevimon\'s place? Terriermon and I will head there first!♪',
}


NUMESUKA_QUEST = {
    176: 'A Numesuka autograph? No way! ...That is what I would say, but they are not popular. I should treasure their few fans. You! Tell three Digimon around here how great Numesuka is! Then you can ask them for autographs. Take these Numesuka goods and hand them out! Report back when you are done, okay?',
    177: 'Please promote Numesuka to three Digimon nearby! Come report back when you are done!',
    178: 'Looks like you promoted them properly!♪ Numesuka are lucky to have a fan like you! They are in South Papyrus Desert, practicing cheesy lines. Their stench might knock you out!▼',
    179: 'Numesuka are in South Papyrus Desert... practicing how to make their fans swoon. Prepare for all kinds of stench!▼',
    180: 'Numesuka? They sound kind of stinky... You are going around promoting them? You must really like them... Could I have a photo card? ...Thank you!♪',
    181: 'Numesuka... I learned their names and faces! They look pretty stinky, but I will cheer them on!',
    182: 'Numesuka!? Yeah, I know them! That rare gross-out duo adored by a few die-hard fans, right? They are so stinky they are banned from live houses! They are stinky in every sense of the word. Their CDs make me dizzy! They are the worst and the best, the strongest and the most awful! So do not be ashamed to be their fan! I will take a postcard, too...',
    183: 'I will write to my friend who is into weird stuff! I will use a Numesuka-style line that sends a shiver down your spine!♪',
    184: 'Numesuka!? I love them! I am a huge fan! You are giving me this smelly photo? Wow! Thank you so much! I am so happy!',
    185: 'This is rare! I bet nobody else has one! It is so stinky it could make you cry... No, that is how happy I am! Thank you for this treasure!',
    186: 'Ah... Welcome, baby! Are your eyes welling up because of my dazzling smile, baby? Or is it my dazzling smell, baby? Now I will knock you out with this Numesuka autograph, baby!▼',
    187: 'I knocked you out with my Numesuka autograph! Sweet dreams, baby! With all this love and slime, I wrote it just for you, baby!▼',
    188: 'Hi, how are you? Welcome, honey! You look like you are about to faint... Do you want our Numesuka autograph? Then ask my partner Numemon, honey!▼',
    189: 'Numemon has our autograph for you, honey! I wrote it with all my heart, enough to make your nose tingle, honey!▼',
}


FARM = {
    38: 'Whoa! Pyramid power is the best! My max MP shot way up!',
    39: 'No treasure or cursed traps... What a letdown!',
    40: 'Whoa! A punching bag! Attacking is what I do best!',
    41: 'How was that? I am strong! My Strength went up a little!',
    42: 'Ugh, I am not feeling it today...',
    43: 'This must be a training tree! I will give it everything I have!',
    44: 'Whoa! That went great! My Strength went up quite a bit!',
    45: 'Ouch... My body is starting to hurt!',
    46: 'Whoa! What is this giant rock?! I just have to move it? Easy!',
    47: 'How about that?! My strongest power yet! My Strength went way up!',
    48: 'Why will it not move?! Forget it, I am done!',
    49: 'What is this? A punching machine?! Come on, hit me!',
    50: 'That was nothing! My Defense went up a little!',
    51: 'What is this?! It hurts too much!',
    52: 'Whoa! A training cannon! Great! Bring it on!',
    53: 'It did not hurt! My Defense went up some!',
    54: 'No way! No matter how long I endure it, pain is pain!',
    55: 'I just have to catch this iron ball, right? Got it! Bring it on!',
}


MEMORY_ITEMS = {
    34: 'Leviamon DigiMemory. Disappears after one use in battle.',
    35: 'Agumon DigiMemory. Disappears after one use in battle.',
    37: 'Garurumon DigiMemory. Disappears after one use in battle.',
    39: 'Guilmon DigiMemory. Disappears after one use in battle.',
    40: 'Patamon DigiMemory. Disappears after one use in battle.',
    41: 'MetalGarurumon DigiMemory. Disappears after one use in battle.',
    42: 'Veemon DigiMemory. Disappears after one use in battle.',
    43: 'Darkdramon DigiMemory. Disappears after one use in battle.',
    44: 'Gatomon DigiMemory. Disappears after one use in battle.',
    45: 'Impmon DigiMemory. Disappears after one use in battle.',
    46: 'WarGreymon DigiMemory. Disappears after one use in battle.',
    47: 'Examon DigiMemory. Disappears after one use in battle.',
    48: 'Omnimon DigiMemory. Disappears after one use in battle.',
    49: 'Sold at the Penmon Shop. A small pair of gloves.',
}


MOVE_DESCRIPTIONS = {
    48: 'Fires a ring of light to purify the target.',
    49: 'Hurls a feather boomerang that slashes nearby enemies.',
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
        'B30_WIKIMON_XROS_TECHNIQUES': {
            'url': XROS_TECHNIQUES,
            'title': 'Digimon Story: Super Xros Wars Japanese technique guide',
            'kind': 'secondary game reference',
            'notes': 'Used to confirm Japanese move labels and their effects; English renderings are marked as working translations unless another Western game or dubbed name is specifically cited.'
        },
        'B30_WIKIMON_APOCALYMON': {
            'url': APOCALYMON,
            'title': 'Apocalymon attack-name references',
            'kind': 'secondary franchise reference',
            'notes': 'Lists Grand Big Bang and alternate English dub renderings for the same Japanese attack.'
        },
        'B30_WIKIMON_SIESAMON': {
            'url': SIESAMON,
            'title': 'Siesamon move-name and Reference Book cross-reference',
            'kind': 'secondary franchise reference quoting the official Reference Book',
            'notes': 'Provides English renderings Sun’s Courage and Ancient Firewall for the corresponding Japanese move names.'
        },
        'B30_WIKIMON_PANDAMON': {
            'url': PANDAMON,
            'title': 'Pandamon attack-name references',
            'kind': 'secondary franchise reference',
            'notes': 'Records Firecracker as the English dubbed name for Unnanshou.'
        },
        'B30_WIKIMON_CHIMERAMON': {
            'url': CHIMERAMON,
            'title': 'Chimairamon attack-name references',
            'kind': 'secondary franchise reference',
            'notes': 'Confirms Hybrid Arms as an established English name for the same multi-arm attack.'
        },
        'B30_WIKIMON_PIEMON': {
            'url': PIEMON,
            'title': 'Piedmon attack-name references',
            'kind': 'secondary franchise reference',
            'notes': 'Confirms Ending Snipe as an English move name in other Digimon games.'
        },
        'B30_WIKIMON_MUSHMON_CARD': {
            'url': MUSHMON_CARD,
            'title': 'Mushmon St-788 English card attack names',
            'kind': 'secondary reference to English card text',
            'notes': 'Lists Rough S-Mush as the English card rendering for the Japanese move.'
        },
        'B30_CYBERSLEUTH_MOVE': {
            'url': GRADALPHA,
            'title': 'English Digimon Story Cyber Sleuth move-name extraction',
            'kind': 'secondary extraction of licensed English game text',
            'notes': 'Lists the matching Seiken Gradalpha move as Blade of the Dragon King. This batch uses a short form to fit the Xros Wars move slot.'
        },
        'B30_BANDAI_CARD_LIST': {
            'url': CARD_LIST,
            'title': 'Bandai official English Digimon Card Game card list',
            'kind': 'primary',
            'notes': 'Official English Digimon species spellings used in the DigiMemory item descriptions.'
        },
    }
    for key, value in additions.items():
        if key in sources and sources[key] != value:
            raise ValueError(f'Glossary source changed unexpectedly: {key}')
        sources[key] = value

    terms = glossary['terms']
    for japanese, (english, source, evidence) in MOVE_TERMS.items():
        source_id = {
            APOCALYMON: 'B30_WIKIMON_APOCALYMON',
            XROS_TECHNIQUES: 'B30_WIKIMON_XROS_TECHNIQUES',
            SIESAMON: 'B30_WIKIMON_SIESAMON',
            PANDAMON: 'B30_WIKIMON_PANDAMON',
            CHIMERAMON: 'B30_WIKIMON_CHIMERAMON',
            PIEMON: 'B30_WIKIMON_PIEMON',
            MUSHMON_CARD: 'B30_WIKIMON_MUSHMON_CARD',
            GRADALPHA: 'B30_CYBERSLEUTH_MOVE',
        }[source]
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

    memory_names = {
        'リヴァイアモン': 'Leviamon', 'アグモン': 'Agumon', 'ガルルモン': 'Garurumon',
        'ギルモン': 'Guilmon', 'パタモン': 'Patamon', 'メタルガルルモン': 'MetalGarurumon',
        'ブイモン': 'Veemon', 'ダークドラモン': 'Darkdramon', 'テイルモン': 'Gatomon',
        'インプモン': 'Impmon', 'ウォーグレイモン': 'WarGreymon', 'エグザモン': 'Examon',
        'オメガモン': 'Omnimon',
    }
    for japanese, english in memory_names.items():
        old = next((item for item in terms if item['japanese'] == japanese and item.get('category') == 'Digimon name'), None)
        term = {'japanese': japanese, 'english': english, 'category': 'Digimon name',
                'sources': ['B30_BANDAI_CARD_LIST'],
                'evidence': 'Official Western species spelling from Bandai’s English card list.'}
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting Digimon term: {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + term['sources']))
            old['evidence'] = term['evidence']
        else:
            terms.append(term)
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    register_glossary()
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    old_path = ROOT / 'translations/batch30.json'
    old = json.loads(old_path.read_text(encoding='utf-8')) if old_path.exists() else None
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

    quest_note = ('Optional Terriellop CD and rescue quest dialogue. Character names and DigiMemory terms use the project glossary; '
                  'Terriellop is retained as the game-specific performer name. Locations follow existing map labels.')
    for index, english in TERRIELLOP_QUEST.items():
        add(f'MSG/MESPAK02.PAK:021:{index:05d}', english, LOCAL, quest_note, width=15)

    rescue_note = ('Optional Terriellop autograph and rescue dialogue translated from the Japanese ROM. '
                   'Terriermon, Lopmon, LadyDevimon, and Numesuka follow project terminology.')
    for index, english in RESCUE_QUEST.items():
        add(f'MSG/MESPAK02.PAK:022:{index:05d}', english, LOCAL, rescue_note, width=15)

    numesuka_note = ('Optional Numesuka promotion and autograph side quest translated from the Japanese ROM. '
                     'Numesuka is retained as the game’s group name; individual species use the sourced English glossary.')
    for index, english in NUMESUKA_QUEST.items():
        add(f'MSG/MESPAK02.PAK:022:{index:05d}', english, LOCAL, numesuka_note, width=15)

    move_note = ('Working English move rendering checked against the Japanese Xros Wars move guide. The glossary records any established Western game/card name or known dub alias and flags unresolved localization choices.')
    for japanese, (english, source, evidence) in MOVE_TERMS.items():
        index = {
            'グランデスビッグバン': 1700, 'らいこういっせんのつき': 1706,
            'ハイブリットアームズ': 1711, 'エンディングスナイプ': 1718,
            'せいけんグレイダルファー': 1728, 'グッドナイト・ムーン': 1735,
            'スパイラルマスカレード': 1738, 'ウンナンショウ': 1749,
            'パンドーラ・ダイアログ': 1757, 'ラフ・ス・マッシュ': 1781,
            'ティーダ・イヤ': 1792, 'せっかんとう': 1793,
            'マイティサンダークロー': 1654, 'ジャスティスブリット': 1659,
        }[japanese]
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, source,
            evidence if source != XROS_TECHNIQUES else move_note)

    effect_note = ('Battle effect translated from the Japanese Xros Wars technique guide; no new attack title is inferred from the description.')
    for index, english in MOVE_DESCRIPTIONS.items():
        add(f'MSG/MESPAK04.PAK:011:{index:05d}', english,
            XROS_TECHNIQUES, effect_note, width=26)

    item_note = ('DigiMemory and equipment description translated from the Japanese item table. Species spellings match Bandai English names where available.')
    for index, english in MEMORY_ITEMS.items():
        add(f'MSG/MESPAK04.PAK:029:{index:05d}', english,
            LOCAL, item_note, width=26)

    farm_note = ('DigiFarm training and exploration report translated from the Japanese ROM, keeping the Digimon’s excited voice and stat names consistent with the English menus.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:003:{index:05d}', english,
            LOCAL, farm_note, width=26)

    description = 'Terriellop autograph and rescue quests, Numesuka promotion/autograph side quest, battle moves and descriptions, DigiMemory item descriptions, and DigiFarm reports.'
    out = ROOT / 'translations/batch30.json'
    review_json = ROOT / 'translations/review_batch30.json'
    review_md = ROOT / 'translations/review_batch30.md'
    out.write_text(json.dumps({'description': description, 'blocks': blocks},
                              ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Batch 30 translation review', '',
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
