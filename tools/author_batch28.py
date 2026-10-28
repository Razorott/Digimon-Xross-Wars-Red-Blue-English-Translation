"""Author map, battle, DigiFarm, NPC, and mission translation batch 28."""
from __future__ import annotations

import csv
import json
import re
import textwrap
import unicodedata

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

DAWN = ('https://raw.githubusercontent.com/joaomlsantos/'
        'Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt')
GUILTY_CLAW = 'https://dro.gameking.com/News/PatchNoteView.aspx?idx=1315'
PENGUINMON = ('https://world.digimoncard.com/cards/'
              '?card_no=EX11-014&search=true')
MARINEDEVIMON = ('https://world.digimoncard.com/cards/'
                 '?card_no=EX8-061&search=true')
DIVermon = ('https://world.digimoncard.com/cards/'
            '?card_no=BT15-028&search=true')
AREAS = 'https://wikimon.net/Digimon_Story:_Super_Xros_Wars_Red'
LOCAL = 'Original Japanese ROM (local primary source)'

# Explicitly use Western names only where established. Other attack labels are
# faithful working renderings and are not presented as official localizations.
MOVES = {
    2205: 'Hell Incinerate',
    2206: 'Death Destroyer',
    2208: 'Space Chakram',
    2209: 'Helios Slasher',
    2228: 'Guilty Claw',
    2229: 'HP Single',
    2230: 'HP Line',
    2231: 'MP Single',
    2232: 'MP Line',
    2233: 'Cure Single',
    2234: 'Cure Line',
    2235: 'Full Recovery',
    2244: 'Mega Flame Explosion',
    2389: 'Phantom Pain Legacy',
    2461: 'Flame Pillar',
    2462: 'Volcano Bomb',
    2463: 'Heavy Drago Magma',
    2464: 'Raging Flame',
    2465: 'Pressure Aqua',
    2466: 'Icicle Bomb',
    2467: 'Heavy Hard Rain',
    2468: 'Raging Blizzard',
    2469: 'Magnet Wave',
    2470: 'Spark Bomb',
    2471: 'Heavy Magnet Power',
    2472: 'Raging Lightning',
    2473: 'Rising Laser',
    2474: 'Shining Bomb',
    2518: 'A.R.C. Blizzard',
    2558: 'Starlight EX',
    2646: 'Dark Spider Dance',
}

# Useful battle descriptions and field abilities from the ability-description
# archive. Dummy/test strings and two opaque names are intentionally excluded.
DESCRIPTIONS = {
    0: 'No special ability.',
    1: 'Can automatically break boulders blocking the path.',
    2: 'Can automatically cut down trees blocking the path.',
    3: 'Can automatically melt ice blocking the path.',
    4: 'Can dig at Dig Points and travel underground.',
    5: 'Can dive at Dive Points and travel underwater.',
    8: 'Raises allies\' Attack and Defense.',
    11: 'Slams an impassioned punch into the enemy. May also cause Confusion.',
    12: 'Swings a McField microphone like a martial-arts weapon. A one-of-a-kind performance technique.',
    13: 'Shot Arms. May drain the target\'s HP.',
    15: 'Claw & Fang. May put the target to sleep.',
    16: 'Enlarges the drill on its tail and whips up a giant tornado that sweeps away all enemies.',
    18: 'Meteor Squall. May lower the target\'s Attack.',
    20: 'Charges straight at the enemy.',
    21: 'Hurls a highly acidic bubble at the target. May also inflict Poison damage.',
    22: 'Fires an arrow of water frozen by a breath of absolute zero.',
    23: 'Fires countless ice arrows at nearby enemies.',
    24: 'Blows a little blizzard that freezes nearby enemies.',
    25: 'Freezes nearby enemies in a bitter blizzard. May also cause Confusion.',
    26: 'Freezes nearby enemies in an absolute-zero storm. Greatly increases the Melodize chance.',
    27: 'Fires a clear water bubble at the target. May put it to sleep.',
    28: 'Blows a mysterious bubble filled with Digivolution energy. May put the target to sleep.',
    29: 'Fires a violent whirlpool at the target.',
    30: 'Fires a high-speed whirlpool at the target.',
    31: 'Fires a rock-crushing whirlpool at the target.',
    32: 'Fires a powerful, surging wave at the target.',
    33: 'Summons a raging tidal wave that engulfs nearby enemies.',
    34: 'Summons a legendary tidal wave that engulfs nearby enemies.',
    35: 'Slices the target with a light-wreathed vacuum blade.',
    36: 'Somersaults at light speed and charges the enemy. Greatly increases the Melodize chance.',
    37: 'Hurls a sound-wave orb wrapped in light at the target.',
    38: 'Hurls sound-wave orbs wrapped in light at nearby enemies. May also cause Confusion.',
    39: 'Creates a huge typhoon and unleashes it on nearby enemies.',
    40: 'Creates a small typhoon and unleashes it on nearby enemies.',
    41: 'Creates a gigantic typhoon and unleashes it on nearby enemies.',
    42: 'Slices the target with a razor-sharp vacuum blade. May lower its Speed.',
    43: 'Cuts nearby enemies with a crescent-shaped shock wave. May lower their Speed.',
    44: 'Spins at light speed and shreds the target with its claws.',
    45: 'Fires orbs of light energy from both arms.',
    46: 'Fires a massive ball of fire that scorches the target.',
    47: 'Fires a ball of fire using the embers surrounding its body.',
    48: 'Fires a ball of fire that erupts into a blazing pillar.',
    49: 'Fires a ball of fire that erupts into a scorching pillar.',
}

FARM = {
    'MSG/MESPAK05.PAK:002:00068': 'Hmm... That was not much fun.',
    'MSG/MESPAK05.PAK:002:00069': 'What is that, a high-jump setup? Can I jump over it? I will give it a try!',
    'MSG/MESPAK05.PAK:002:00070': 'Yes! I did it! That was fun! I think I gained a little EXP!',
    'MSG/MESPAK05.PAK:002:00071': 'I could not make it. What a shame...',
    'MSG/MESPAK05.PAK:002:00072': 'Is that a diving board? I just jump from here, right...?',
    'MSG/MESPAK05.PAK:002:00073': 'Whew! I nailed it! That felt great! I gained lots of EXP!',
    'MSG/MESPAK05.PAK:002:00074': 'Never mind! This is scary!',
    'MSG/MESPAK05.PAK:002:00075': 'Is this an old record player? I wonder if it still works...',
    'MSG/MESPAK05.PAK:002:00076': 'That is a nice song! I like it. I gained a little EXP, too!',
    'MSG/MESPAK05.PAK:002:00077': 'It is broken. Aw, what a shame!',
    'MSG/MESPAK05.PAK:002:00078': 'That is a Holy Bell, right? I will ring it!',
    'MSG/MESPAK05.PAK:002:00079': 'Wow... What a lovely sound! It feels so nice... I gained some EXP, too!',
    'MSG/MESPAK05.PAK:002:00080': 'Huh? It will not ring at all. Is it broken?',
    'MSG/MESPAK05.PAK:002:00081': 'Is this Stonehenge? Maybe something good will happen if I walk between the stones...?',
    'MSG/MESPAK05.PAK:002:00082': 'Whoa! I feel so strong! I gained a lot of EXP!',
    'MSG/MESPAK05.PAK:002:00083': 'Nothing happened. I am a little disappointed...',
    'MSG/MESPAK05.PAK:002:00084': 'I wonder what is inside this...',
    'MSG/MESPAK05.PAK:002:00085': 'Whoa! Is this Dark Medicine?! I gained a little EXP, too!',
    'MSG/MESPAK05.PAK:002:00086': 'It... It is creepy. I think I will stop.',
    'MSG/MESPAK05.PAK:002:00087': 'What is this? It looks creepy... A cursed box? I will take a look!',
    'MSG/MESPAK05.PAK:002:00088': 'Amazing! This is the power of darkness! I gained some EXP!',
    'MSG/MESPAK05.PAK:002:00089': 'Huh? The lid will not open. Never mind!',
    'MSG/MESPAK05.PAK:002:00090': 'Could this be a Dark Tower? I will investigate!',
    'MSG/MESPAK05.PAK:002:00091': 'Wow! The power of darkness is surging through me! I gained a ton of EXP!',
    'MSG/MESPAK05.PAK:002:00092': 'Nothing happened... Maybe this is not a Dark Tower?',
    'MSG/MESPAK05.PAK:002:00093': 'Huh? What is that? Something around here smells so warm and comforting...',
    'MSG/MESPAK05.PAK:002:00094': 'Th-this is Taiki\'s scent! I hope we can play together next time he visits... Our Friendship went up a little!',
    'MSG/MESPAK05.PAK:002:00095': 'It has been so peaceful and happy lately... It is all thanks to Taiki, right? He is such a great Tamer!',
    'MSG/MESPAK05.PAK:002:00096': 'Taiki, th-thanks for everything... I hope you heard me... Our Friendship went way up!',
    'MSG/MESPAK05.PAK:002:00098': 'Yay! I found 100 DigiBits! I will send them to Taiki right away. He will be happy!',
    'MSG/MESPAK05.PAK:003:00000': 'I found 500 DigiBits! I will send them to Taiki right away. He will be so happy!',
    'MSG/MESPAK05.PAK:003:00002': 'Wow! 1,000 DigiBits?! I will send them to Taiki. He will be thrilled!',
    'MSG/MESPAK05.PAK:003:00003': 'Hey! There are wild berries here. I will try one!',
    'MSG/MESPAK05.PAK:003:00004': 'Wild berries are delicious! I gained a decent amount of EXP!',
    'MSG/MESPAK05.PAK:003:00005': 'These berries do not taste good. What a letdown...',
    'MSG/MESPAK05.PAK:003:00006': 'That branch looks sturdy! Maybe I will climb it.',
    'MSG/MESPAK05.PAK:003:00007': 'Climbing trees is exciting! I gained a little EXP, too!',
    'MSG/MESPAK05.PAK:003:00008': 'Hmm... Climbing trees is not as fun as I thought.',
    'MSG/MESPAK05.PAK:003:00009': 'What is this... A tree stump? What am I supposed to do with it?',
    'MSG/MESPAK05.PAK:003:00010': 'This training is unusual, but it is not bad. I gained a decent amount of EXP!',
    'MSG/MESPAK05.PAK:003:00011': 'I got a splinter when I bumped into the stump...',
    'MSG/MESPAK05.PAK:003:00012': 'That tree is oozing tasty sap. I wonder what it tastes like...',
    'MSG/MESPAK05.PAK:003:00013': 'It is really sweet and tasty! I gained a lot of EXP!',
    'MSG/MESPAK05.PAK:003:00014': 'Ugh! This tastes awful! And it was called "Tasty Sap"...!',
}

FARM_WILD = {
    0: 'Whoa! A circus tent! I will master my performance skills here!',
    1: 'I feel like I have been reborn as a superstar performer! And I gained a ton of EXP!',
    2: 'I could not learn anything. They made me clean the whole time...',
    3: 'Whoa! A mini-shower! Perfect timing. I am going to cool off!',
    4: 'The water is so cold! It feels amazing! I gained a little EXP, too!',
    5: 'Whoa! This water is freezing!',
    6: 'A mini fishing pond! There are fish everywhere! I am going to catch a bunch!',
    7: 'Yes! Fish on! I got a tasty-looking fish and some EXP!',
    8: 'I did not catch anything. What a letdown!',
    9: 'A huge waterfall! I will train under it!',
    10: 'Whoa! I just had a brilliant idea! I do not know what it is, but it is amazing! My EXP shot up, too!',
    11: 'Brr! The water is freezing... and it hurts!',
    12: 'What is this? It smells wonderful! Is it this flower?',
    13: 'This nectar is sweet and delicious! I gained a little EXP, too!',
    14: 'A smell will not fill my stomach!',
}

NPC = {
    'MSG/MESPAK02.PAK:018:00043': 'Thanks! ROG fled. You saved us! Hope they stay gone so peace returns. Others need help, Taiki. Check Sky Fort\'s Quest Monitor!',
    'MSG/MESPAK02.PAK:018:00044': 'Best shop in\nRoundabout City\nPenguinmon\'s!\nOnly one here!',
    'MSG/MESPAK02.PAK:018:00046': 'Welcome to our Roundabout City DigiFarm Shop! Yeah! Need you! Bomber!',
    'MSG/MESPAK02.PAK:018:00047': 'Tower\'s back... Thank you! You saved us!',
    'MSG/MESPAK02.PAK:018:00048': 'Taiki, Spadamon, thanks! Need the Spider Nest Ruins key? No key, sorry!',
    'MSG/MESPAK02.PAK:018:00052': 'Skull City\'s Penguinmon runs the Skull Shop! No poison for sale!',
    'MSG/MESPAK02.PAK:018:00055': 'You came to save us, Taiki! This icy Zone is full of joy!',
    'MSG/MESPAK02.PAK:018:00057': 'Thanks for saving me! Please help the others, too. Check their wishes on the Quest Monitor. I\'m counting on you!',
    'MSG/MESPAK02.PAK:018:00058': 'Didn\'t expect to return! Thanks, Taiki!',
    'MSG/MESPAK02.PAK:018:00060': 'Taiki! You saved me! Ask if you need anything. Crystal Volcano? Too hot for me! How would I know?!',
    'MSG/MESPAK02.PAK:018:00132': 'I\'m Tentomon, your tent expert! Know the save terminal and healing bed? Now we have the DigiLab and DigiFarm PCs!',
    'MSG/MESPAK02.PAK:018:00133': 'Need DigiLab and DigiFarm? I had them brought in! Put them to good use. Keep it up!',
    'MSG/MESPAK02.PAK:018:00135': 'Penguinmon\'s is Sky Fort\'s top shop! No rivals here...',
    'MSG/MESPAK02.PAK:018:00138': 'Windmill raid? Where have I heard that story...',
    'MSG/MESPAK02.PAK:018:00141': 'Let\'s go! Our friends wait! They believe in you, Taiki!',
    'MSG/MESPAK02.PAK:018:00142': 'Taiki, it\'s weird... Sis said Pipimon can\'t come!',
    'MSG/MESPAK02.PAK:018:00143': 'Bad feeling... Stay alert!',
}

QUESTS = {
    'MSG/MESPAK01.PAK:000:00495': ('Talk to MarineDevimon\nin the Front Room.', MARINEDEVIMON),
    'MSG/MESPAK01.PAK:000:00499': ('Report to MarineDevimon\nin the Front Room.', MARINEDEVIMON),
    'MSG/MESPAK01.PAK:000:00504': ('Talk to Divermon\nin the Front Room.', DIVermon),
    'MSG/MESPAK01.PAK:000:00508': ('Report to Divermon\nin the Front Room.', DIVermon),
}

# Translate the complete area-label table by replacing place names and then
# keeping each numbered direction/route suffix legible and consistent.
MAP_PREFIXES = [
    ('デジタルくうかん東', 'Digital Space East'),
    ('デジタルくうかん北', 'Digital Space North'),
    ('デジタルくうかん南', 'Digital Space South'),
    ('ナックルかいがん西', 'Knuckle Coast West'),
    ('ナックルかいがん東', 'Knuckle Coast East'),
    ('ぐるぐるアマゾン西', 'Roundabout Amazon West'),
    ('ぐるぐるアマゾン東', 'Roundabout Amazon East'),
    ('ドクロひょうざん西', 'Skull Iceberg West'),
    ('ドクロひょうざん東', 'Skull Iceberg East'),
    ('クモノスいせき西', 'Spider Nest Ruins West'),
    ('クモノスいせき東', 'Spider Nest Ruins East'),
    ('パピルスさばく北', 'Papyrus Desert North'),
    ('パピルスさばく南', 'Papyrus Desert South'),
    ('フラワーそうげん', 'Flower Meadow'),
    ('くらやみトンネル', 'Dark Tunnel'),
    ('トコナうみ', 'Tokona Sea'),
    ('トコナかいがん', 'Tokona Coast'),
    ('クリスタルかざん西', 'Crystal Volcano West'),
    ('クリスタルかざん東', 'Crystal Volcano East'),
    ('クリスタルこうざん', 'Crystal Mine'),
    ('クリスタルどうくつ', 'Crystal Cave'),
    ('ステルスけいこく北', 'Stealth Valley North'),
    ('ステルスけいこく南', 'Stealth Valley South'),
    ('ロストスペース北', 'Lost Space North'),
    ('ロストスペース南', 'Lost Space South'),
    ('デジタルくうかん', 'Digital Space'),
    ('ぐるぐるアマゾン', 'Roundabout Amazon'),
    ('クモノスいせき', 'Spider Nest Ruins'),
    ('ドクロひょうざん', 'Skull Iceberg'),
    ('ナックルかいがん', 'Knuckle Coast'),
    ('パピルスさばく', 'Papyrus Desert'),
    ('スカイガーデン', 'Sky Garden'),
    ('キャニオンヤード', 'Canyon Yard'),
    ('グラスヤード', 'Grass Yard'),
    ('ロストスペース', 'Lost Space'),
    ('ステルスけいこく', 'Stealth Valley'),
]
MAP_EXACT = {
    'ちゅうおうルーム': 'Central Room',
    'コマンダールーム': 'Commander Room',
    'スカイポート': 'Sky Port',
    'ろうや': 'Prison',
    'フロントルーム': 'Front Room',
    'メインヤード': 'Main Yard',
    'WKシティポート': 'West Knuckle City Port',
    'Wナックルシティ': 'West Knuckle City',
    'EKシティポート': 'East Knuckle City Port',
    'Eナックルシティ': 'East Knuckle City',
    'ぐるぐるWポート': 'Roundabout West Port',
    'ぐるぐるシティポート': 'Roundabout City Port',
    'ぐるぐるシティ': 'Roundabout City',
    'ドクロシティポート': 'Skull City Port',
    'ドクロシティ': 'Skull City',
    'ドクロEポート': 'Skull East Port',
    'ドクロかいてい': 'Skull Seabed',
    'クモノスWポート': 'Spider Nest West Port',
    'クモノスちかつうろ': 'Spider Nest Passage',
    'クモノスシティポート': 'Spider Nest City Port',
    'クモノスシティ': 'Spider Nest City',
    'パピルスNポート': 'Papyrus North Port',
    'パピルスシティポート': 'Papyrus City Port',
    'パピルスシティ': 'Papyrus City',
    'パピルスあな': 'Papyrus Cave',
    'フラワーポート': 'Flower Port',
    'トコナポート': 'Tokona Port',
    'クリスタルWポート': 'Crystal West Port',
    'クリスタルかざんちか': 'Crystal Volcano Underground',
    'アースポート': 'Earth Port',
    'アースフォート': 'Earth Fort',
    'Cこうざんポート': 'Crystal Mine Port',
    'ステルスNポート': 'Stealth North Port',
    'ステルスほらあな': 'Stealth Cavern',
    'ステルスSポート': 'Stealth South Port',
    'ロストNポート': 'Lost North Port',
    'ロストSポート': 'Lost South Port',
    'システムΩ': 'System Omega',
    'デジタルNポート': 'Digital North Port',
    'デジタルSポート': 'Digital South Port',
    'デジコロシアムロビー': 'DigiColosseum Lobby',
    'かんきゃくせき': 'Spectator Seats',
}


def wrap(value, width):
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def map_label(source):
    source = unicodedata.normalize('NFKC', source)
    if source in MAP_EXACT:
        return MAP_EXACT[source]
    for japanese, english in MAP_PREFIXES:
        if source.startswith(japanese):
            suffix = source[len(japanese):]
            if suffix.startswith('G'):
                suffix = 'G ' + suffix[1:]
            return english + (' ' + suffix if suffix else '')
    raise ValueError(f'Unmapped area label: {source}')


def main():
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    current_batch = ROOT / 'translations/batch28.json'
    if current_batch.exists():
        old = json.loads(current_batch.read_text(encoding='utf-8'))
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:"
                          f"{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    if current_batch.exists():
        # A fresh work queue no longer contains the slots in this batch. Use
        # the saved batch itself to recreate those original Japanese groups.
        old_groups = {}
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                key = (f"{block['archive']}:{block['entry']:03d}:"
                       f"{block['start'] + offset:05d}")
                source = records[key]['source']
                group = (source, block['category'])
                old_groups.setdefault(group, []).append(key)
        for (source, category), ids in old_groups.items():
            row = {'ids': ';'.join(ids), 'japanese': source,
                   'category': category}
            for key in ids:
                by_id.setdefault(key, row)
    blocks, review, seen = [], [], set()

    def add(key, english, evidence=LOCAL, note='', width=None):
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
        review.append({'category': row['category'], 'japanese': japanese,
                       'ids': ids, 'english': english, 'evidence': evidence,
                       'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': sources,
                           'review_note': note})

    move_note = ('Battle label translated from the Japanese source and checked '
                 'against the English Digimon World: Dawn/Dusk move-name list. '
                 'No exact match was found unless this note says otherwise; '
                 'treat these as working renderings pending battle-effect review.')
    for index, english in MOVES.items():
        key = f'MSG/MESPAK00.PAK:000:{index:05d}'
        if index == 2228:
            add(key, english, GUILTY_CLAW,
                'Guilty Claw is used as a Western Digimon attack name in the licensed English Digimon RPG update; the Japanese attack text is ギルティクロー. This is a name match, not evidence that this game used the same localization.')
        elif index in (2464, 2558):
            exact = 'Raging Flame' if index == 2464 else 'Starlight EX'
            add(key, english, DAWN,
                f'Exact English move-name match in the English Digimon World: Dawn/Dusk list: {exact}.')
        elif index in range(2229, 2236):
            add(key, english, LOCAL,
                'Direct working labels for single-target or line-target recovery actions; confirm targeting in battle.')
        else:
            add(key, english, DAWN, move_note)

    for index, english in DESCRIPTIONS.items():
        key = f'MSG/MESPAK04.PAK:003:{index:05d}'
        add(key, english, DAWN,
            'Japanese ability-effect description translated directly. Official attack names are preserved where established; effect wording remains subject to active battle review.',
            width=26)

    for key, english in FARM.items():
        add(key, english, LOCAL,
            'DigiFarm activity/result text. EXP and Friendship use the game\'s established status terminology.',
            width=26)
    for index, english in FARM_WILD.items():
        key = f'MSG/MESPAK05.PAK:004:{index:05d}'
        add(key, english, LOCAL,
            'DigiFarm activity/result text; preserves the enthusiastic Wild Digimon voice.',
            width=26)

    for key, english in NPC.items():
        if 'Penguinmon' in english:
            evidence = PENGUINMON
            note = ('Penguinmon is the official English card spelling for Japanese '
                    'ペンモン. The shop/location wording is translated from this game\'s Japanese text.')
        else:
            evidence = LOCAL
            note = ('NPC dialogue translated from the Japanese game script. Human names '
                    'remain Taiki and other original Japanese names; established DigiLab/DigiFarm terms are retained.')
        add(key, english, evidence, note, width=15)

    for key, (english, evidence) in QUESTS.items():
        add(key, english, evidence,
            'Quest objective translated from the Japanese text. Digimon spelling follows the English card/game name; Tokona Coast is the established English rendering used for this Japan-only game.')

    map_note = ('Map/area label translated directly from the Japanese game text. '
                'This game did not receive an official Western release; established '
                'English location spellings were cross-checked against the community '
                'game reference, and remaining labels are transparent working renderings.')
    for index in range(167):
        key = f'MSG/MESPAK01.PAK:006:{index:05d}'
        if key in prior:
            continue
        row = by_id.get(key)
        if row is None:
            continue
        label = map_label(row['japanese'])
        add(key, label, AREAS, map_note)

    output = ROOT / 'translations/batch28.json'
    review_json = ROOT / 'translations/review_batch28.json'
    review_md = ROOT / 'translations/review_batch28.md'
    output.write_text(json.dumps({
        'description': 'Area map labels, battle moves and effects, DigiFarm reports, HQ NPC dialogue, and quest prompts.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [
        '# Batch 28 translation review', '',
        'Japanese source strings, English renderings, stable IDs, and terminology evidence.', '',
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
        lines.append(f'| {ids} | {japanese} | {english} | {source}<br>{note} |')
    review_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')
    print('Categories:', json.dumps({k: sum(len(g['ids']) for g in review if g['category'] == k)
                                    for k in sorted({g['category'] for g in review})}, ensure_ascii=False))

if __name__ == '__main__':
    main()
