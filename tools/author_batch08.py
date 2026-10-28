"""Author the next researched dialogue, quest, battle, name, farm, and item batch."""
from __future__ import annotations

import csv
import json
import textwrap
from collections import defaultdict
from pathlib import Path

from build import collect_messages, translate_records
from translation_queue import category as queue_category
from xros_text import ROOT, Rom, rom_paths

REF = 'https://digimon.net/reference_en/'
CARD = 'https://world.digimoncard.com/cards/'
DWD = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

# Canonical English names are used where the Western Digimon name is stable.
# Game-only prefixes/suffixes are preserved and called out for review.
NAMES = {
    'キングチェスモン': ('KingChessmon', REF, ''),
    'クロノモンＨＭ': ('Chronomon: Holy Mode', REF, ''),
    'リリスモンＬ': ('Lilithmon L', REF, 'The game-specific L suffix is retained; its meaning needs a direct source.'),
    'ロードナイトモン': ('LordKnightmon', CARD, 'Western sources vary between LordKnightmon and Crusadermon; this follows the English Digimon Card Game name.'),
    'ＩＰドラモンＦＭ': ('Imperialdramon Fighter Mode', REF, ''),
    'ＩＰドラモンＰＭ': ('Imperialdramon Paladin Mode', REF, ''),
    'デュークモンＣＭ': ('Gallantmon Crimson Mode', CARD, ''),
    'ＢＥヴァンデモン': ('BE Myotismon', CARD, 'The BE variant prefix is retained because this game does not explain it.'),
    'ＣＡデュークモン': ('ChaosGallantmon', CARD, ''),
    'スサノオモン': ('Susanoomon', REF, ''),
    'Ｍ＝ミレニアモン': ('Millenniummon', REF, 'The source has a game-specific M= prefix; the Western species name is used pending confirmation of that prefix.'),
    'マッドレオモン': ('MadLeomon', REF, ''),
    'タクティモン': ('Tactimon', REF, ''),
    'ブラストモン': ('Blastmon', REF, ''),
    'ガオスモン': ('Gaossmon', REF, ''),
    'トループモン': ('Troopmon', REF, ''),
    'チクリモン': ('Chikurimon', REF, ''),
    'プラチナヌメモン': ('PlatinumNumemon', REF, ''),
    'ディノレクスモン': ('Dinorexmon', REF, ''),
    'オグドモン': ('Ogudomon', REF, ''),
    'ドラコモン': ('Dracomon', REF, ''),
    'ファスコモン': ('Phascomon', REF, ''),
    'ミノモン': ('Minomon', REF, ''),
    'ポーンチェスモン（しろ）': ('PawnChessmon (White)', REF, ''),
    'ダークティラノモン': ('DarkTyrannomon', REF, ''),
    'サンダーボールモン': ('ThunderBallmon', REF, ''),
    'ナイトチェスモン（しろ）': ('KnightChessmon (White)', REF, ''),
    'ストライクドラモン': ('Strikedramon', REF, ''),
    'メタルグレイモン（レジェンド）': ('MetalGreymon (Legend)', REF, 'Legend is kept as a game-specific form label.'),
    'ワーガルルモン（あお）': ('WereGarurumon (Blue)', REF, ''),
    'アトラーカブテリモン（あか）': ('MegaKabuterimon (Red)', REF, 'Uses the Western name MegaKabuterimon for AtlurKabuterimon.'),
    'ナノモン（レジェンド）': ('Nanomon (Legend)', REF, 'Legend is kept as a game-specific form label.'),
    'サイバードラモン（レジェンド）': ('Cyberdramon (Legend)', REF, 'Legend is kept as a game-specific form label.'),
    'ホーリーエンジェモン': ('MagnaAngemon', CARD, ''),
    'スーパースターモン': ('SuperStarmon', REF, ''),
    'ホエーモン（かんぜんたい）': ('Whamon (Ultimate)', REF, 'The Japanese Perfect stage is rendered as Ultimate in Western English releases.'),
    'ルーチェモン　フォールダウンモード': ('Lucemon Falldown Mode', REF, ''),
    'メタルティラノモン': ('MetalTyrannomon', REF, ''),
    'エクスティラノモン': ('EXTyrannomon', REF, 'The source uses the X/EX form prefix; this spelling follows the game name.'),
    'エアロブイドラモン': ('AeroVeedramon', REF, ''),
    'ビショップチェスモン': ('BishopChessmon', REF, ''),
    'アルゴモン　アルティメット': ('Argomon (Ultimate)', REF, ''),
    'マスターティラノモン': ('MasterTyrannomon', REF, ''),
    'マリンエンジェモン': ('MarineAngemon', REF, ''),
    'ケルビモン（ぜん）': ('Cherubimon (Virtue)', CARD, ''),
    'ケルビモン（あく）': ('Cherubimon (Vice)', CARD, ''),
    'ベルゼブモン（レジェンド）': ('Beelzemon (Legend)', REF, 'Legend is kept as a game-specific form label.'),
    'リリスモン（レジェンド）': ('Lilithmon (Legend)', REF, 'Legend is kept as a game-specific form label.'),
    'アルゴモン　メガ': ('Argomon (Mega)', REF, ''),
    'シャウトモン＋ドルルキャノン': ('Shoutmon + Dorulu Cannon', CARD, 'Fusion name assembled from the two established English component names.'),
    'シャウトモン＋スターソード': ('Shoutmon + Star Sword', CARD, 'Fusion name assembled from the two established English component names.'),
    'シャウトモン＋ジェットスパロウ': ('Shoutmon + JetSparrow', CARD, 'Fusion name assembled from the two established English component names.'),
}

# Exact Western DS spellings are used only for attacks that match the English
# Dawn/Dusk move list. Other entries are careful working renderings and stay
# marked as unverified until a Japanese-to-English release match is confirmed.
MOVES = {
    'ヘブンズゲート': ('Heaven\'s Gate', DWD, 'Exact attack title found in the English Dawn/Dusk move list.'),
    'ラブリーアタック': ('Lovely Attack', DWD, 'Exact attack title found in the English Dawn/Dusk move list.'),
    'ダークネスゾーン': ('DarknessZone', DWD, 'Exact Dawn/Dusk spelling; keep the source game spelling without a space.'),
    'デス・クリスタル': ('Death Crystal', DWD, 'Exact attack title found in the English Dawn/Dusk move list.'),
    'トリッドヴァイス': ('Torrid Weiss', DWD, 'Exact attack title found in the English Dawn/Dusk move list.'),
    'クレセントハーケン': ('Crescent Harken', DWD, 'Readable expansion of the Dawn/Dusk list spelling “CrescntHarken”; verify exact game-specific spacing before release.'),
    'シャリテ': ('Charite', DWD, 'Exact attack title found in the English Dawn/Dusk move list.'),
    'インプリズメント': ('Imprisonment', DWD, 'Working English rendering; not confirmed as an exact Dawn/Dusk move match.'),
    'アウススターベン': ('Aussterben', DWD, 'German term retained as the move name; direct Western localization not confirmed.'),
    'アラミタマ': ('Aramitama', DWD, 'Japanese mythological term retained; direct Western localization not confirmed.'),
    'ネコパンチ': ('Cat Punch', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'こえんりゅう': ('Coiling Flame Dragon', DWD, 'Working English rendering of the move name; direct Western localization not confirmed.'),
    'プラズマブレイド': ('Plasma Blade', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'ゴッドトルネード': ('God Tornado', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'エクスレイザー': ('X-Raiser', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'ヴァリアブルダーツ': ('Variable Darts', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'パワーメタル': ('Power Metal', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'ガトリングアーム': ('Gatling Arm', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'デスチャーム': ('Death Charm', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'デスクロウ': ('Death Claw', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'きりすてごめん': ('Kirisute Gomen', DWD, 'Japanese phrase retained in romanized form; direct Western localization not confirmed.'),
    'ハイパーキャノン': ('Hyper Cannon', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'ブラストレーザー': ('Blast Laser', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'ガルルキャノン': ('Garuru Cannon', DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'アルゴルズフレイム': ("Algol's Flame", DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'オーディンズブレス': ("Odin's Breath", DWD, 'Working English rendering; direct Western localization not confirmed.'),
    'あめのおはばり': ('Ame-no-Ohabari', DWD, 'Japanese mythological sword name romanized; direct Western localization not confirmed.'),
}

QUESTS = {
    'ドクロひょうざん西で<0A>いんせきを　さがそう': 'Search for a meteorite<0A>west of Skull Mountain.',
    'ぐるぐるアマゾン東の<0A>ベーダモンにかんていしてもらおう': 'Have Vademon appraise it<0A>in Twisting Amazon East.',
    'クモノスいせき西で<0A>うでだめしを　しよう': 'Test your strength at<0A>Spiderweb Ruins West.',
    'てごわい　うでだめしや　あいてに<0A>ジマンの　うでを　ためそう': 'Prove your strength<0A>against tough opponents.',
    'ナックルかいがん東で<0A>ピエモンに　あおう': 'Meet Piedmon at<0A>Knuckle Coast East.',
    'フラワーそうげんで<0A>ピエモンに　あおう': 'Meet Piedmon at<0A>Flower Meadow.',
    'デジタルくうかん東で<0A>ピエモンに　あおう': 'Meet Piedmon in<0A>Digital Space East.',
    'パピルスさばく北で<0A>ピエモンに　あおう': 'Meet Piedmon in<0A>Papyrus Desert North.',
    'ピエモンさまの<0A>デジモンクイズ': "Piedmon's<0A>Digimon Quiz",
    'ドクロひょうざん東で<0A>じょうほうを　あつめてね': 'Gather information at<0A>Skull Mountain East.',
    'パピルスさばく北で<0A>シンドゥーラモンを　さがそう': 'Find Sinduramon in<0A>Papyrus Desert North.',
    'Ｗナックルシティにいる<0A>バードラモンと　はなしてね': 'Talk to Birdramon in<0A>West Knuckle City.',
    'パピルスさばく南で<0A>システムてちょうを　さがしてね': 'Find the System Notebook<0A>in Papyrus Desert South.',
    'ドクロひょうざん東で<0A>テリアモンと　はなしてね': 'Talk to Terriermon at<0A>Skull Mountain East.',
    'にんきアイドル！！<0A>テリアモン＆ロップモン': 'Popular Idols!!<0A>Terriermon & Lopmon',
    'アイドルユニット　テリロップから<0A>サインいりＣＤを　もらってこよう': 'Get a signed CD from<0A>the idol duo TerriLop.',
    'パピルスシティにいる<0A>ヴァンデモンと　はなしてね': 'Talk to Myotismon in<0A>Papyrus City.',
    'フロントルームにいる<0A>ブイモンに　わたしてね': 'Give it to Veemon in<0A>the Front Room.',
}

STORY = {
    'デジスコアを　てにいれた！<0A>~I': 'Got a DigiScore!<0A>~I',
    'ああ　わかった': 'Okay, got it.',
    'だいじに　してくれ<0A>じゃあな！': 'Take care!<0A>See you!',
    'もういちど　せつめいを<0A>ききますか？': 'Hear the<0A>explanation<0A>again?',
    'なかまに　してくれる？': 'Can I join you?',
    'よろしくな！': 'Nice to meet<0A>you!',
    'せつめいを　きかない': 'Skip this<0A>explanation',
    'ひとつまえに　もどる': 'Go back',
    'ああ　そうだな！': 'You are right!',
    'どうした　スパーダモン？': 'Spadamon,<0A>what happened?',
    'うん　わかった': 'Okay, I get it.',
    'そっかー　じゃあ　またね～': 'Oh, okay!<0A>See you later!',
    'あら　こんにちは<0A>アイテム　あげるわね': 'Hello!<0A>Take this item.',
    'ＲＯＧを　おいはらってくれて<0A>ホントに　たすかったぜ！<0A>おれいに　やくだつ<0A>じょうほうを　おしえてやる<0A>すぐそこの　ボンバーナニモンから<0A>『ぶきごや』を　かってみろ！<0A>じぶんのファーム島で　デジモンに<0A>『おしごと』を　させるだけで…<0A>すっげー　ぶきを　ガンガン<0A>つくってもらえるんだぜ！？<0A>だまされたと　おもって<0A>かってみろよ　…な？': 'Thanks for driving off ROG!<0A>You really saved us.<0A>Here is a useful tip:<0A>buy the Weapon Shop from<0A>BomberNanimon nearby.<0A>Have your Digimon work<0A>on your Farm Island and<0A>they will make great gear!<0A>Give it a try, okay?',
    'ガッカリしちゃったクル…': 'So sad, Kuru...',
    'おう　アイテムやるぞ～': 'Hey, I have an item for you!',
}

FARM = {
    'あら　コそだて　みたいで<0A>たのしいですわね…<0A>おかげで　ゆうじょうが<0A>すこし　アップしましたわ…！': 'This is like raising<0A>a little one. How fun...<0A>My Friendship went up<0A>a little, thanks to you!',
    'む…　むずかしいですわね<0A>もちろん　たのしいんですが…': 'Th-this is tricky...<0A>Still, it is fun!',
    'あら　これは<0A>けいたいデンワですわね…！<0A>タイキさんに<0A>メールを　おくれるかしら？': 'Oh, a mobile phone!<0A>Could I send Taiki<0A>a message with it?',
    'キャ～ッ　タイキさんから<0A>へんじが　きましたわ～ッ！<0A>これで　ゆうじょうが<0A>けっこう　アップしたようです！': 'Taiki replied! How exciting!<0A>My Friendship went up<0A>quite a bit!',
    '…へんじが　こないですわね<0A>ちょっと　ざんねんですわ…': '...No reply yet.<0A>That is a little sad...',
    'あら　デジタルカメラ！<0A>タイキさんの　ですね…<0A>わたし　しゃしんうつりは<0A>いいんですのよ！': 'Oh, a digital camera!<0A>It must belong to Taiki...<0A>I always look good<0A>in pictures!',
    'せいこうです　いまのは<0A>キレイに　とれてますわ～！<0A>おかげで　ゆうじょうが<0A>かなり　アップしたようです': 'That worked! The picture<0A>came out beautifully!<0A>My Friendship went up<0A>a lot, thanks to you!',
    'あら　どうしましょう<0A>まにあいませんでしたわ…': 'Oh dear...<0A>I was too late...',
    'おッ？　これは<0A>たいじゅうけい　か…<0A>ちょっと　はかってみるか': 'Oh? Is this a scale?<0A>I will check my weight.',
    'かるすぎず　おもすぎず<0A>これくらいで　ワルくねえな<0A>おかげで　ＨＰさいだいちが<0A>すこし　アップしたみたいだぜ！': 'Not too light or heavy.<0A>This feels about right.<0A>My Max HP went up<0A>a little!',
    'うわ…　このすうじは　ねえな<0A>みなかったことに　するか…？': 'Yikes... that is bad.<0A>Maybe I never saw it...?',
    'ん～？　これは<0A>ベルトマシン…？<0A>こんなもんで　うんどうすんのは<0A>しょうに　あわねえけどな～': 'Hmm? Is this a treadmill...?<0A>Running on a machine<0A>does not fit my style...',
    'ふう…　なんだよコレ　あんがい<0A>いい　うんどうに　なるな！<0A>おかげで　ＨＰさいだいちが<0A>まあまあ　アップしたみたいだぜ': 'Whew... this is actually<0A>pretty good exercise!<0A>My Max HP went up<0A>quite a bit.',
    'うんどうが　どうとかいうまえに<0A>これ　プルプルしすぎだーッ！': 'Forget exercise!<0A>This thing shakes too much!',
    'おッ　これって<0A>ランニングマシンじゃねえか！<0A>ランニングくらい　ふつうに<0A>じめん　はしればいいのに…<0A>……でも　いっぺん<0A>やってみたかったんだよな！': 'Hey, a treadmill!<0A>I could just run outside...<0A>...but I always wanted<0A>to try one of these!',
}

ITEMS = {
    'クロノ・ＤＳＲ': ('Chrono DSR', DWD, 'Exact item/attack label from the English Dawn/Dusk list.'),
    'オリジンネビュラ': ('Origin Nebula', '', 'Working item name; direct Western source not found.'),
    'ざっそうソード': ('Weed Sword', '', 'Literal working item name; direct Western source not found.'),
    'Ｅナックル': ('East Knuckle', '', 'The game E/W labels are expanded for clarity.'),
    'Ｗナックル': ('West Knuckle', '', 'The game E/W labels are expanded for clarity.'),
    'ドクロのつえ': ('Skull Staff', '', 'Working item name.'),
    'マッシュグラブ': ('Mushroom Glove', '', 'Working item name.'),
    'クワスタンガン': ('Stag Beetle Stun Gun', '', 'Literal working item name; the exact item localization is unverified.'),
    'ガオグローブ': ('Gao Glove', '', 'Working item name.'),
    'バルカンほう': ('Vulcan Cannon', '', 'Working item name.'),
    'ムーングローブ': ('Moon Glove', '', 'Working item name.'),
    'デモンアーム': ('Demon Arm', '', 'Working item name.'),
    'クロックハンマー': ('Clock Hammer', '', 'Working item name.'),
    'サイコブラスター': ('Psycho Blaster', '', 'Working item name.'),
    'アンキロハンマー': ('Ankylosaur Hammer', '', 'Working item name.'),
    'オベリスク': ('Obelisk', '', 'Working item name.'),
    'トールハンマー': ("Thor's Hammer", '', 'Working item name.'),
    'あきかんバズーカ': ('Tin Can Bazooka', '', 'Working item name.'),
    'ドラコニードル': ('Draco Needle', '', 'Working item name.'),
    'ポーンスピア': ('Pawn Spear', '', 'Working item name.'),
    'にょいボーン': ('Nyoi Bone', '', 'Working item name; preserves the Nyoi staff reference.'),
    'トレント': ('Treant', '', 'Working item name.'),
    'フェアリーテイル': ('Fairy Tale', '', 'Working item name.'),
    'ヴァジュラ': ('Vajra', '', 'Working item name.'),
    'ホネこんぼう': ('Bone Club', '', 'Working item name.'),
}

DESCRIPTIONS = {
    'とくせいを　もっていない': 'No special trait.',
    'まひに　かかりにくい': 'Less likely to be paralyzed.',
    'まひに　かなり　かかりにくい': 'High paralysis resistance.',
    'ぜったい　まひに　かからない': 'Immune to paralysis.',
    'パーティぜんたいが<0A>まひに　すこし　かかりにくくなる': 'Team: low paralysis resist',
    'パーティぜんたいが<0A>まひに　かかりにくくなる': 'All allies resist paralysis',
    'まひに　すこし　かかりやすい': 'Slight paralysis weakness',
    'ねむりに　かかりにくい': 'Sleep resistance: Low',
    'ねむりに　かなり　かかりにくい': 'Sleep resistance: High',
    'ぜったい　ねむりに　かからない': 'Immune to sleep.',
    'パーティぜんたいが<0A>ねむりに　すこし　かかりにくくなる': 'Party: low sleep resistance',
    'パーティぜんたいが<0A>ねむりに　かかりにくくなる': 'All allies resist sleep',
    'ねむりに　すこし　かかりやすい': 'Slight sleep weakness',
    'こんらんに　かかりにくい': 'Confusion resistance: Low',
    'こんらんに　かなり　かかりにくい': 'Confusion resistance: High',
    'ぜったい　こんらんに　かからない': 'Immune to confusion.',
    'パーティぜんたいが<0A>こんらんに　すこし　かかりにくくなる': 'Party: low confusion resist',
    'パーティぜんたいが<0A>こんらんに　かかりにくくなる': 'All allies resist confusion',
    'こんらんに　すこし　かかりやすい': 'Slight confusion weakness',
    'くらやみに　かかりにくい': 'Blindness resistance: Low',
    'くらやみに　かなり　かかりにくい': 'High blindness resistance',
    'ぜったい　くらやみに　かからない': 'Immune to blindness.',
    'パーティぜんたいが<0A>くらやみに　すこし　かかりにくくなる': 'Allies: slight blind resist',
    'パーティぜんたいが<0A>くらやみに　かかりにくくなる': 'All allies resist blindness',
    'くらやみに　すこし　かかりやすい': 'Slight blind weakness',
}

def main():
    out = ROOT / 'translations' / 'batch08.json'
    own_ids = set()
    if out.exists():
        previous = json.loads(out.read_text(encoding='utf-8'))
        own_ids = {
            f"{block['archive']}:{block['entry']:03d}:{index:05d}"
            for block in previous['blocks']
            for index in range(block['start'], block['start'] + len(block['english']))
        }
    records = collect_messages(Rom(rom_paths()['blue']))
    translated = translate_records(records)
    grouped = defaultdict(list)
    for record in records.values():
        if not record['source'].strip():
            continue
        if record['id'] in translated and record['id'] not in own_ids:
            continue
        cat = queue_category(record)
        if cat in ('Digimon names', 'Battle moves', 'Menus, quests and battle prompts',
                   'Story and dialogue', 'DigiFarm reports', 'Items and equipment',
                   'Move and item descriptions'):
            grouped[(cat, record['source'])].append(record['id'])
    rows = [
        {'category': cat, 'japanese': source, 'ids': ';'.join(ids)}
        for (cat, source), ids in grouped.items()
    ]
    mappings = {
        'Digimon names': NAMES,
        'Battle moves': MOVES,
        'Menus, quests and battle prompts': QUESTS,
        'Story and dialogue': STORY,
        'DigiFarm reports': FARM,
        'Items and equipment': ITEMS,
        'Move and item descriptions': DESCRIPTIONS,
    }
    blocks = []
    matched = {category: set() for category in mappings}
    for row in rows:
        spec = mappings.get(row['category'], {}).get(row['japanese'])
        if spec is None:
            continue
        matched[row['category']].add(row['japanese'])
        if isinstance(spec, tuple):
            english, source, note = spec
            sources = [source] if source else []
        else:
            english, sources, note = spec, [], ''
        for key in row['ids'].split(';'):
            archive, entry, index = key.rsplit(':', 2)
            english = english.replace('<0A>', '\n')
            if row['category'] == 'Story and dialogue':
                english = '\n'.join(
                    textwrap.fill(line, width=15, break_long_words=False,
                                  break_on_hyphens=False)
                    for line in english.split('\n')
                )
            blocks.append({
                'archive': archive,
                'entry': int(entry),
                'start': int(index),
                'category': row['category'],
                'english': [english],
                'sources': sources,
                'review_note': note,
            })
    missing = {cat: sorted(set(mapping) - matched[cat]) for cat, mapping in mappings.items() if set(mapping) - matched[cat]}
    if missing:
        raise ValueError(f'Expected source strings missing from fresh queue: {missing}')
    out.write_text(json.dumps({
        'description': 'Clearer title lettering and additional canonical Digimon names, battle moves, quests, dialogue, DigiFarm reports, equipment, and battle-status descriptions.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'slots': len(blocks),
                      'source_strings': {cat: len(ids) for cat, ids in matched.items()}}, ensure_ascii=False))

if __name__ == '__main__':
    main()
