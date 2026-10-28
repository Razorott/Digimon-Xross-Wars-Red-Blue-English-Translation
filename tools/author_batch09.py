"""Author a researched continuation of the English translation."""
from __future__ import annotations

import json
import textwrap
from collections import defaultdict

from build import collect_messages, translate_records
from translation_queue import category as queue_category
from xros_text import ROOT, Rom, rom_paths

REF = 'https://digimon.net/reference_en/'
CARD = 'https://world.digimoncard.com/cards/'
DWD = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

# Canonical Western names are used for recognizable species. Abbreviated
# game-only forms keep compact suffixes where expanding them would overflow
# the original name field; those cases are called out for review.
NAMES = {
    'ＭＥグレイモンＬ': ('MetalGreymon L', REF, 'L is retained as the game form suffix; the game does not expand it in this field.'),
    'ＡカブテリモンＲ': ('MegaKabuterimon (Red)', CARD, 'Uses the Western species name; Red is this game-specific color form.'),
    'ＨＥカブテリモン': ('HerculesKabuterimon', CARD, ''),
    'ＭＡエンジェモン': ('MagnaAngemon', CARD, ''),
    'ＶＮヴァンデモン': ('VenomMyotismon', CARD, ''),
    'ＩＰドラモンＤＭ': ('Imperialdramon DM', CARD, 'Compact display form of the official Imperialdramon: Dragon Mode name.'),
    'ＭＥシードラモン': ('MetalSeadramon', CARD, 'ME is the game abbreviation for Metal in this species label.'),
    'ＭＲガオガモン': ('MirageGaogamon', CARD, ''),
    'ＳグレイモンＢＭ': ('ShineGreymon BM', CARD, 'BM is the standard Burst Mode abbreviation used to fit this narrow field.'),
    'レイヴモンＢＭ': ('Ravemon BM', CARD, 'BM is the standard Burst Mode abbreviation used to fit this narrow field.'),
    'ロゼモンＢＭ': ('Rosemon BM', CARD, 'BM is the standard Burst Mode abbreviation used to fit this narrow field.'),
    'ＴＤボールモン': ('ThunderBallmon', REF, ''),
    'ＫチェスモンＷＨ': ('KnightChessmon W', REF, 'W abbreviates the White variant to fit the name field.'),
    'ＳＴドラモン': ('Strikedramon', REF, ''),
    'ナノモンＬ': ('Nanomon L', REF, 'L is retained as the game form suffix.'),
    'ＣＹＢドラモンＬ': ('Cyberdramon L', REF, 'L is retained as the game form suffix.'),
    'グレイナイツモン': ('GreyKnightsmon', CARD, 'Game fusion name; romanization follows the Xros Wars spelling.'),
    'ＢＷグレイモン': ('BlackWarGreymon', CARD, ''),
    'ＱＵチェスモン': ('QueenChessmon', REF, ''),
    'アルゴモンＭＧ': ('Argomon (Mega)', REF, ''),
    'ボムモン': ('Bombmon', REF, ''),
    'モニタモン': ('Monitamon', REF, ''),
    'グレイモン（レジェンド）': ('Greymon (Legend)', REF, 'Legend is a game-specific form label.'),
    'スターモン（レジェンド）': ('Starmon (Legend)', REF, 'Legend is a game-specific form label.'),
}

# Exact or strong cross-game matches use the English Dawn/Dusk spelling.
# Other working translations remain marked for review rather than being
# presented as official Western move titles.
MOVES = {
    'プーヤヴァーハ': ('Puyavaha', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ブレイズパワー': ('Blazing Power', DWD, 'Matches the English Dawn/Dusk move list.'),
    'クロスカッター': ('Cross Cutter', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'するどいツメ': ('Sharp Claw', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'しっぷうのツメ': ('Gale Claw', DWD, 'Matches the Dawn/Dusk move-list name Gale Claw.'),
    'おうじゃのツメ': ('Royal Claw', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ミドルタックル': ('Middle Tackle', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ヘビータックル': ('Heavy Tackle', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ヤミブラスト': ('Dark Blast', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'カオスブラスト': ('Chaos Blast', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ダーククラッシャー': ('Dark Crusher', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    '０１クラッシャー': ('01 Crusher', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'デスキャノン': ('Death Cannon', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'カオススラッシュ': ('Chaos Slash', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ひかりのマンダラ': ('Light Mandala', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ピラミッドパワー': ('Pyramid Power', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ジェノサイドアタック': ('Genocide A', DWD, 'Uses the Dawn/Dusk release spelling for the corresponding Genocide attack.'),
    'ＦＩＮエリシオン': ('FIN Elysion', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'パンデモニウムＦＬ': ('Pandemonium F', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ソウルフルキック': ('Soulful Kick', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'サンダー': ('Thunder', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'エアサンダー': ('Air Thunder', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ダブルブラスター': ('Double Blaster', DWD, 'Exact English Dawn/Dusk move-list spelling.'),
    'ドレインウィップ': ('Drain Whipping', DWD, 'Uses the Dawn/Dusk release spelling for this matching attack.'),
    'ベヒーモス': ('Behemoth', '', 'Working English rendering; direct Dawn/Dusk match not confirmed.'),
}

QUESTS = {
    'クリスタルかざん西で<0A>ギロモンのなかまに\u3000あおう': "Meet Giromon's friend at<0A>Crystal Volcano West.",
    'クリスタルかざん東で<0A>マメモンのなかまに\u3000あおう': "Meet Mamemon's friend at<0A>Crystal Volcano East.",
    'クリスタルどうくつで<0A>セントガルゴモンを\u3000さがそう': 'Find MegaGargomon in<0A>Crystal Cave.',
    'ちっこいデジモンチームを\u3000たすけて<0A>デカブツデジモンを\u3000やっつけよう': 'Help the little Digimon<0A>team beat the big guys!',
    'デジタルくうかん東で<0A>ケルビモン・あくと\u3000はなしてね': 'Talk to Cherubimon (Vice)<0A>in Digital Space East.',
    'トコナうみで<0A>うでだめしを\u3000しよう': 'Test your strength in<0A>Tokona Sea.',
    'ＶＳ<0A>ＴＥＡＭかわいい▼？': 'VS<0A>TEAM CUTE?',
    'ロストスペース北で<0A>？？？？を\u3000さがしてね': 'Find ?????? in<0A>Lost Space North.',
    'ウルトラてごわい\u3000うでだめしや\u3000あいてに<0A>ジマンの\u3000うでを\u3000ためそう': 'Take on an ultra-tough<0A>training opponent!',
    'デジタルくうかん南２で<0A>ピエモンに\u3000あおう': 'Meet Piedmon in<0A>Digital Space South 2.',
    'ピエモンさまの<0A>デジモンクイズ２': "Piedmon's Digimon<0A>Quiz 2",
}

STORY = {
    'ン～ん…\u3000ギヴィトゥミッ！！': 'Mmm... Give it to me!!',
    'なに\u3000アイテム…？<0A>……ちッ': 'An item...?<0A>...Tch.',
    'だいじにしてね<0A>それじゃ\u3000さよなら': 'Take good care of it.<0A>Goodbye!',
    '……ふんッ<0A>うけとったら\u3000うせろ！': 'Hmph! Take it and<0A>get out of my sight!',
    'ハシゴを\u3000のぼったり<0A>おりたり\u3000するには<0A>ハシゴに\u3000ちかづいて<0A>Ａボタンを\u3000おしてください': 'To climb a ladder or<0A>climb back down, stand<0A>near it and press A.',
    'クロンデジゾイト': ('Chrome Digizoid', REF, 'Standard English Digimon material name.'),
    'わが\u3000ふういんに\u3000ふれるものよ<0A>わざわいを\u3000よびおこすものよ<0A>いにしえの\u3000ねむりを\u3000さまたげ<0A>いかりを\u3000よびさますものよ…<0A>その\u3000かくごを\u3000みせるがいい…！': 'You who touch my seal,<0A>you who awaken disaster...<0A>You disturb our ancient sleep<0A>and rouse our wrath...<0A>Show me your resolve!',
    '……ふういんを\u3000とくな<0A>われらの\u3000ねむりを\u3000さますな…': '...Do not break the seal.<0A>Do not wake us from sleep...',
}

FARM = {
    'じっさい\u3000やってみると<0A>けっこう\u3000キモチいいな<0A>おかげで\u3000ＨＰさいだいちが<0A>かなり\u3000アップしたぜ～♪': 'This feels pretty good!<0A>My Max HP went up<0A>quite a bit, too! ♪',
    'おなじトコで\u3000あしぶみしてると<0A>なんか\u3000むなしくなるぜ…': 'Running in place<0A>starts to feel pointless...',
    'ん～？\u3000これって<0A>すいしょうだま…？<0A>キレイだけど\u3000なんか<0A>つかいみち\u3000あんのか…？': 'Hmm? Is this a crystal<0A>ball? It is pretty, but<0A>what is it for...? ',
    '……ＭＰさいだいち<0A>すこーし\u3000アップ<0A>そして\u3000みとめたくねえが<0A>なんか\u3000チカッと\u3000みえたぜ…<0A>……あれ\u3000オレの\u3000ミライか！？': '...My Max MP went up<0A>a little. And, as much<0A>as I hate to admit it,<0A>I saw a flash... Was that<0A>my future?!',
    'なんか\u3000みえたと<0A>おもったんだけど…<0A>…サカサに\u3000うつった<0A>オレの\u3000カオじゃねえか！': 'I thought I saw<0A>something... It was<0A>my upside-down face!',
    'なんだこれ？<0A>タロットカード…？': 'What is this?<0A>A tarot card...?',
    'うおぉおーッ！？<0A>ＭＰさいだいちが\u3000あがった！？<0A>なんなんだ\u3000これが\u3000まほうの<0A>ちからってヤツか…！？': 'Whoa! My Max MP went up!<0A>Is this the power<0A>of magic?!',
    'ケッ\u3000くだらねえ\u3000まほうなんて<0A>そんなの\u3000めいしんに\u3000きまって…<0A>…うほォッ！？<0A>なんか\u3000きゅうにハラが…<0A>なにこれ\u3000まほうのバチあたり！？': 'Magic is nonsense...<0A>Just superstition...<0A>...Whoa! My stomach!<0A>Is this magic payback?!',
}

# The item table also includes a few Digimon name labels. Keep those names in
# their established Western form; untranslated abbreviations remain explicit.
ITEMS = {
    'リヴァイアモン': ('Leviamon', REF, ''),
    'メタルガルルモン': ('MetalGarurumon', CARD, ''),
    'ダークドラモン': ('Darkdramon', CARD, ''),
    'ウォーグレイモン': ('WarGreymon', CARD, ''),
    'エグザモン': ('Examon', CARD, ''),
    'オメガモン': ('Omnimon', CARD, 'Uses the established Western name Omnimon.'),
    'ヒョコのたち': ('Chick Tachi', '', 'Working item name; literal rendering, pending a direct Western match.'),
    'ししおうまる': ('Shishiomaru', DWD, 'Exact spelling in the English Dawn/Dusk move and item-name list.'),
    'しらとりまる': ('Shiratorimaru', '', 'Romanized working item name; direct Western localization not found.'),
    'いらたかのけん': ('Irataka Sword', '', 'Working rendering; the Japanese proper name is retained in romanized form.'),
    'ブルーソード': ('Blue Sword', '', 'Literal working item name.'),
    'たそがれアクス': ('Twilight Axe', '', 'Literal working item name.'),
    'オメガブレード': ('Omega Blade', DWD, 'Matches the English Dawn/Dusk move and item-name list.'),
    'ＬＨスラッシャー': ('LH Slasher', '', 'Abbreviation retained because the game does not expand LH.'),
    '０アームズオロチ': ('O-Armz Orochi', '', 'Game-style romanization retained for this named weapon.'),
    'ソドム＆ゴモラ': ('Sodom & Gomorrah', '', 'Named after the established biblical proper names.'),
    'キングスバイト': ("King's Bite", '', 'Working item name.'),
    'クラウ・ソラス': ('Claiomh Solais', '', 'Traditional weapon name romanized; direct game localization not found.'),
    'ローヤルＭスター': ('Royal M Star', '', 'The game abbreviation M is retained.'),
    'ソーンウィップ': ('Thorn Whip', '', 'Literal working item name.'),
    'ブライのカラかさ': ("Brai's Parasol", '', 'Working rendering of the named umbrella.'),
    'ちょんまげメット': ('Topknot Helmet', '', 'Literal working item name.'),
    'マメティラメット': ('MameTyrano Helmet', '', 'Working name based on the game term.'),
    'マタドゥルマント': ('Matador Cloak', '', 'Literal working item name.'),
    'ヒョコカラスーツ': ('ChickCrow Suit', '', 'Working rendering of the game-specific suit name.'),
    'シャコシールド': ('Mantis Shrimp Shield', '', 'Literal rendering of the Japanese item name.'),
    'メカノリスーツ': ('Mekanorimon Suit', REF, ''),
    'メタルプレート': ('Metal Plate', '', 'Literal working item name.'),
    'ラプタアーマー': ('Raptor Armor', '', 'Literal working item name.'),
    'サルスーツ': ('Monkey Suit', '', 'Literal working item name.'),
    'ビームシールド': ('Beam Shield', '', 'Literal working item name.'),
    'ウェットスーツ': ('Wetsuit', '', 'Standard English spelling.'),
    'シンドゥプレート': ('Sindura Plate', '', 'Proper name retained in romanized form.'),
    'クダピアス': ('Kudamon Earrings', REF, ''),
    'ドラクマスク': ('Dracomon Mask', REF, ''),
    'ボンバグラサン': ('Bomber Sunglasses', '', 'Working rendering of the item name.'),
    'キツネのおめん': ('Fox Mask', '', 'Literal working item name.'),
    'ワーガルパンツ': ('WereGaruru Pants', REF, 'Uses the game name stem; this item label is a pun.'),
    'ＥＸきぐるみ': ('EX Costume', '', 'Compact rendering for the narrow equipment field.'),
    'フェイスベール': ('Face Veil', '', 'Literal working item name.'),
    'デスヘルム': ('Death Helm', '', 'Literal working item name.'),
    'アルファマント': ('Alpha Cloak', '', 'Literal working item name.'),
    'プリンスクラウン': ('Prince Crown', '', 'Literal working item name.'),
    'キングクローク': ('King Cloak', '', 'Literal working item name.'),
    'ガイオウのヨロイ': ("Gaia's Armor", '', 'Working rendering of the named armor.'),
    'クロスアーマー': ('Xros Armor', '', 'Uses the project spelling for Xros terminology.'),
    'ファラオシールド': ('Pharaoh Shield', '', 'Literal working item name.'),
    'セラフィアーマー': ('Seraph Armor', '', 'Literal working item name.'),
    'ホウオウスーツ': ('Phoenix Suit', '', 'Uses the established English name for Houou.'),
    'ブレイブシールド': ('Brave Shield', '', 'Literal working item name.'),
    'イージス': ('Aegis', '', 'Standard English rendering of the mythological name.'),
    'キュートマフラー': ('Cute Scarf', '', 'Literal working item name.'),
    'サクヤのめん': ("Sakuyamon Mask", REF, ''),
    'レイヴンマスク': ('Raven Mask', '', 'Literal working item name.'),
    'ディアナマスク': ('Diana Mask', '', 'Proper name retained.'),
    'パイルバンカー': ('Pile Bunker', '', 'Standard equipment term.'),
    'アポカリチェーン': ('Apocalypse Chain', '', 'Working rendering of the item name.'),
    'ホーリーリング': ('Holy Ring', '', 'Literal working item name.'),
    'Ｖブレスレット': ('V Bracelet', '', 'The game prefix V is retained.'),
    'クルクルピアス': ('Twirl Earrings', '', 'Working rendering of the item name.'),
    'トレジャーアーム': ('Treasure Arm', '', 'Literal working item name.'),
    'ゴーゴン': ('Gorgon', '', 'Standard English mythological name.'),
    'ニフルヘイム': ('Niflheim', '', 'Standard romanization of the mythological name.'),
    'マジックボックス': ('Magic Box', '', 'Literal working item name.'),
    'スケイルメイル': ('Scale Mail', '', 'Standard English equipment term.'),
    'アヴァロン': ('Avalon', '', 'Standard English mythological name.'),
}

DESCRIPTIONS = {
    'ヘルスダウンに\u3000すこし\u3000かかりにくい': 'Slight Health Down resist.',
    'ヘルスダウンに\u3000かなり\u3000かかりにくい': 'High Health Down resist.',
    'ぜったい\u3000ヘルスダウンに\u3000かからない': 'Immune to Health Down.',
    'パーティぜんたいが<0A>ヘルスダウンに\u3000すこし\u3000かかりにくくなる': 'Party: low Health Down res.',
    'パーティぜんたいが<0A>ヘルスダウンに\u3000かかりにくくなる': 'Party resists Health Down',
    'テキからの\u3000ＨＰドレインを\u3000うけにくくなる': 'Resist enemy HP drain.',
    'テキからの\u3000ＨＰドレインを\u3000かなり\u3000うけにくくなる': 'High enemy HP drain resist.',
    'テキの\u3000ＨＰドレインが\u3000きかない': 'Immune to enemy HP drain.',
    'パーティぜんたいが<0A>テキからの\u3000ＨＰドレインを\u3000すこし\u3000うけにくくなる': 'Party: low HP drain resist',
    'パーティぜんたいが<0A>テキからの\u3000ＨＰドレインを\u3000うけにくくなる': 'Party resists HP drain',
    'テキからの\u3000ＨＰドレインを\u3000うけやすくなる': 'Weak to enemy HP drain',
    'テキからの\u3000ＭＰドレインを\u3000うけにくくなる': 'Resist enemy MP drain.',
    'テキからの\u3000ＭＰドレインを\u3000かなり\u3000うけにくくなる': 'High enemy MP drain resist.',
    'テキの\u3000ＭＰドレインが\u3000きかない': 'Immune to enemy MP drain.',
    'パーティぜんたいが<0A>テキからの\u3000ＭＰドレインを\u3000すこし\u3000うけにくくなる': 'Party: low MP drain resist',
    'パーティぜんたいが<0A>テキからの\u3000ＭＰドレインを\u3000うけにくくなる': 'Party resists MP drain',
}

MAPPINGS = {
    'Digimon names': NAMES,
    'Battle moves': MOVES,
    'Menus, quests and battle prompts': QUESTS,
    'Story and dialogue': STORY,
    'DigiFarm reports': FARM,
    'Items and equipment': ITEMS,
    'Move and item descriptions': DESCRIPTIONS,
}


def main():
    out = ROOT / 'translations' / 'batch09.json'
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
        if not record['source'].strip() or (record['id'] in translated and record['id'] not in own_ids):
            continue
        grouped[(queue_category(record), record['source'])].append(record['id'])

    blocks = []
    matched = {category: set() for category in MAPPINGS}
    for (category, source), ids in grouped.items():
        spec = MAPPINGS.get(category, {}).get(source)
        if spec is None:
            continue
        matched[category].add(source)
        if isinstance(spec, tuple):
            english, evidence, note = spec
            sources = [evidence] if evidence else []
        else:
            english, sources, note = spec, [], ''
        english = english.replace('<0A>', '\n')
        if category == 'Story and dialogue':
            english = '\n'.join(textwrap.fill(line, width=15, break_long_words=False,
                                               break_on_hyphens=False)
                                for line in english.split('\n'))
        for key in ids:
            archive, entry, index = key.rsplit(':', 2)
            blocks.append({
                'archive': archive, 'entry': int(entry), 'start': int(index),
                'category': category, 'english': [english], 'sources': sources,
                'review_note': note,
            })

    missing = {cat: sorted(set(mapping) - matched[cat])
               for cat, mapping in MAPPINGS.items() if set(mapping) - matched[cat]}
    if missing:
        raise ValueError(f'Expected source strings missing from fresh queue: {missing}')
    out.write_text(json.dumps({
        'description': 'Digimon names, Dawn/Dusk-aligned battle moves, missions, story and DigiFarm dialogue, equipment, and battle descriptions.',
        'blocks': blocks,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'slots': len(blocks),
                      'source_strings': {cat: len(sources) for cat, sources in matched.items()}},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
