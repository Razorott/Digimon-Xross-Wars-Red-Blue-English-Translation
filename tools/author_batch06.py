"""Continue battle, dialogue, Digimon-name, and move-name translation."""
import json
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

NAMES={
    'ギガシードラモン':'GigaSeadramon','ピエモン':'Piedmon','デーモン':'Creepymon',
    'ホウオウモン':'Phoenixmon','ピノッキモン':'Puppetmon','ロゼモン':'Rosemon',
    'ウォーグレイモン':'WarGreymon','メタルガルルモン':'MetalGarurumon',
    'ムゲンドラモン':'Machinedramon','デスモン':'Ghoulmon','セラフィモン':'Seraphimon',
    'ハイアンドロモン':'HiAndromon','デビタマモン':'Devitamamon',
    'ケルビモン・ぜん':'Cherubimon (Virtue)','ケルビモン・あく':'Cherubimon (Vice)',
    'デュークモン':'Gallantmon','セントガルゴモン':'MegaGargomon','サクヤモン':'Sakuyamon',
    'ディアボロモン':'Diaboromon','ネプトゥーンモン':'Neptunmon','プクモン':'Pukumon',
    'グリフォモン':'Gryphonmon','プレシオモン':'Plesiomon','ボルトモン':'Boltmon',
    'プリンスマメモン':'PrinceMamemon','オファニモン':'Ophanimon','ザンバモン':'Zanbamon',
    'ジジモン':'Jijimon','ババモン':'Babamon','アヌビモン':'Anubimon',
    'パラサイモン':'Parasimon','キャノンドラモン':'Cannondramon',
    'スラッシュエンジェモン':'SlashAngemon','クロスモン':'Eaglemon',
    'ドルゴラモン':'DORUgoramon','ベルゼブモン':'Beelzemon',
    'バンチョーレオモン':'BanchoLeomon','ダークドラモン':'Darkdramon',
    'イーバモン':'Ebemon','ガルフモン':'Gulfmon','ゴッドドラモン':'Goldramon',
    'メタルシードラモン':'MetalSeadramon','ヴァルキリモン':'Valkyrimon',
    'ジャスティモン':'Justimon','ヴァイクモン':'Vikemon',
    'ブラックウォーグレイモン':'BlackWarGreymon','スカルマンモン':'SkullMammothmon',
    'グランクワガーモン':'GranKuwagamon','ファラオモン':'Pharaohmon',
    'アルファモン':'Alphamon','ホーリードラモン':'Magnadramon',
    'ミレニアモン':'Millenniummon','メギドラモン':'Megidramon',
    'スレイプモン':'Kentaurosmon','シャイングレイモン':'ShineGreymon',
    'ミラージュガオガモン':'MirageGaogamon','ジャンボガメモン':'JumboGamemon',
    'レイヴモン':'Ravemon','クイーンチェスモン':'QueenChessmon',
    'クロノモン　ホーリーモード':'Chronomon Holy Mode','リリスモン':'Lilithmon',
    'アポロモン':'Apollomon','ディアナモン':'Dianamon','ロトスモン':'Lotusmon',
    'ミネルヴァモン':'Minervamon','ドゥフトモン':'Leopardmon',
    'スピノモン':'Spinomon','メルクリモン':'Mercurymon','ガイオウモン':'Gaiomon',
    'グランドラクモン':'GranDracmon','エンシェントイリスモン':'AncientIrismon',
    'エンシェントガルルモン':'AncientGarurumon',
    'エンシェントメガテリウモン':'AncientMegatheriummon',
    'エンシェントグレイモン':'AncientGreymon',
    'エンシェントマーメイモン':'AncientMermaimon',
    'エンシェントワイズモン':'AncientWisemon',
    'エンシェントスフィンクモン':'AncientSphinxmon',
    'エンシェントトロイアモン':'AncientTroiamon',
    'エンシェントビートモン':'AncientBeetlemon',
    'エンシェントボルケーモン':'AncientVolcamon',
    'アルフォースブイドラモン':'UlforceVeedramon',
    'タイガーヴェスパモン':'TigerVespamon',
    'インペリアルドラモン　ドラゴンモード':'Imperialdramon Dragon Mode',
    'インペリアルドラモン　ファイターモード':'Imperialdramon Fighter Mode',
    'インペリアルドラモン　パラディンモード':'Imperialdramon Paladin Mode',
    'デュークモン　クリムゾンモード':'Gallantmon Crimson Mode',
    'ヴェノムヴァンデモン':'VenomMyotismon',
    'ベリアルヴァンデモン':'MaloMyotismon',
    'ズィードミレニアモン':'ZeedMillenniummon',
    'カオスデュークモン':'ChaosGallantmon',
    'ムーン＝ミレニアモン':'Moon=Millenniummon',
    'シャイングレイモン　バーストモード':'ShineGreymon Burst Mode',
    'シャイングレイモン　ルインモード':'ShineGreymon Ruin Mode',
    'ミラージュガオガモン　バーストモード':'MirageGaogamon Burst Mode',
    'レイヴモン　バーストモード':'Ravemon Burst Mode',
    'ロゼモン　バーストモード':'Rosemon Burst Mode',
}

# Direct English card-list references for names whose Western form differs
# from a literal romanization. Other entries use the official Reference Book
# index and remain marked for individual review when there is no direct page.
NAME_EVIDENCE={
    'デーモン':'https://world.digimoncard.com/cards/?card_no=EX10-009&search=true',
    'デスモン':'https://world.digimoncard.com/cards/?card_no=BT25-076&search=true',
    'クロスモン':'https://world.digimoncard.com/cards/?category=522118&search=true',
    'ベリアルヴァンデモン':'https://world.digimoncard.com/cards/?card_no=EX10-011&search=true',
}
NAME_REVIEW={
    'デーモン':'The official English card list uses Creepymon. Some older games use Daemon.',
    'デスモン':'The official English card list uses Ghoulmon.',
    'クロスモン':'The official English card list uses Eaglemon.',
    'ベリアルヴァンデモン':'The official English card list uses MaloMyotismon.',
}

# Names match strings in the US Dawn/Dusk move-name extraction. The extraction
# is community-maintained; its source and nature are recorded in each block.
MOVES={
    'ビッグトルネード':'Big Tornado','プチメタル':'Tiny Metal',
    'トランプソード':'Trump Sword','アメミット':'Amemit',
    'ダブルインパクト':'Double Impact','ホーリーフレア':'Holy Flare',
    'オメガブレード':'Omega Blade','オーシャンラブ':'Ocean Love',
    'ネクロミスト':'Necro Mist','メガデス':'Mega Death',
    'ファイナル・エリシオン':'FIN Elysion','スパイラルフラワー':'Spiral Flower',
    'しょうげきは':'Shogekiha','グロリアスバースト':'Glorious Burst',
    'ホーリーアロー':'Holy Arrow','セブンヘブンズ':'SevenHeavens',
    'タイダルウェーブ':'Tidal Wave','コズモフラッシュ':'Cosmo Flash',
    'グレイブボーン':'Grave Bone','じゅうおうけん':'BeastKing Fist',
    'メテオスコール':'Meteor Squall','ホーリーフレイム':'Holy Flame',
    'アトミック・レイ':'Atomic Ray','メギドフレイム':'Megido Flame',
    'ぐれんじゅうおうは':'Guren Juuouha','ソルブラスター':'Solblaster',
    'ルナティックダンス':'Lunatic Dance','ストライクロール':'Strike Roll',
    'スパイラルブロー':'Spiral Blow','データクラッシャー':'Data Crusher',
    'サウザンドフィスト':'Thousand Fist',
}

COMMON_DIALOGUE={
    'よお　タイキ！<0A>ここは　サービスカウンターだ<0A>よびだしチケットを　てにいれたら<0A>オイラに　はなしかけてくれよな！':
        "Hey, Taiki! Welcome to the Service Counter. If you get a Summon Ticket, talk to me and I'll call a Digimon for you!",
    'だいじにしろよ<0A>じゃあな！':'Take good care of it.<0A>See you!',
    'せいぜい　だいじに　することだ<0A>……じゃあな':'Take good care of it.<0A>...Farewell.',
    'レディーッ！<0A>……ファイッ！':'Ready!<0A>Fight!',
    'では　おたがいに　フェアな<0A>バトルを　こころがけてください！':'Give us a fair<0A>battle, both of you!',
    'おう　アイテム　やるぞ～':'Hey! Take this item!',
    '……ふむ　よかろう<0A>アイテムを　やろうじゃないか':'Hmm... Very well.<0A>Here, take an item.',
    'やあ　こんにちは～<0A>アイテムあげるね～♪':'Hello there!<0A>Here is an item for you!',
    'だいじにしてよ？<0A>じゃあね～♪':'Take good care of it!<0A>See you!',
    'うぉおおおお……！<0A>アイテムを　くれてやるッ！':'Raaagh!<0A>Take this item!',
    'だいじに　するんだぞッ！':'Take good care of it!',
    'はい　とります！':"Yes, I'll take it!",
    'いいえ　とりません':"No, I won't.",
    'やあ　がんばったね<0A>アイテムを　あげよう':'Hello! Great work.<0A>Here is an item for you.',
    'バトルを　ゆうりに　すすめるには<0A>かいふくする　やくわりや…<0A>こうげきする　やくわりを<0A>きめておくことが　じゅうようです':
        'To gain an edge in battle,<0A>assign roles for healing<0A>and attacking.',
    'スパーダモンの　のうりょくの<0A>いちぶが　ふっかつした！':"Some of Spadamon's<0A>abilities have returned!",
    'オレを　なかまに　するか？':'Will you let me join you?',
    'よろしくねッ♪':'Nice to meet you!',
    'ノーマルモードに　きりかえた！':'Switched to Normal Mode!',
    'スカイフォートのシステムが　かいふくした！':'Sky Fortress systems<0A>have been restored!',
    'あたらしい　ファーム島を　てにいれた！':'You got a new Farm Island!',
}

SYSTEM_DIALOGUE={
    'MSG/MESPAK02.PAK:000:00141':'In battle, you can collect Melodies to turn Digimon into allies. Use Melodies to complete DigiScores, or fuse two Digimon to create a new one!',
    'MSG/MESPAK02.PAK:000:00142':'Melodies?',
    'MSG/MESPAK02.PAK:000:00143':'A Digimon becomes a Melody when its data is collected. Defeat one in a single hit, or finish it with a Melody-effect move, to capture it in your Xros Loader.',
    'MSG/MESPAK02.PAK:000:00145':'A DigiScore tells you which two Digimon fuse and what they become. Fill its empty slots with Melodies to complete it. Incomplete DigiScores cannot be read.',
    'MSG/MESPAK02.PAK:000:00148':'Complete a DigiScore with battle Melodies to create its Digimon. Each DigiScore has requirements: raise friendship, level, strength, or wisdom before fusion.',
    'MSG/MESPAK02.PAK:000:00150':'DigiCoding combines Melodies collected in battle to create Digimon. Capture a Digimon with a one-hit defeat or a Melody-effect finishing move, then use its Melody in the DigiLab.',
    'MSG/MESPAK02.PAK:000:00153':'The DigiLab is where you research Digimon. DigiCompose creates DigiScores, DigiCoding turns Melodies into Digimon, and Fusion combines Digimon. The Digimon List shows information and lets you move them.',
    'MSG/MESPAK02.PAK:017:00037':'Melody Capture lets you recruit wild Digimon by collecting their data as Melodies. Defeat an uninjured foe in one hit, or finish it with a Melody-effect attack. Use its weakness to improve your odds. Hitting its strength lowers them. Turn captured Melodies into Digimon at the DigiLab.',
    'MSG/MESPAK02.PAK:017:00076':'At the DigiLab, you can fuse Digimon to make them stronger and restore captured Melodies to physical form. Ask Veemon by the DigiLab PC for details.',
    'MSG/MESPAK02.PAK:016:00172':'Melody Playback restores a Digimon from its Melody data. The more Melodies you use, the higher its level. You can use up to 10 Melodies at once.',
    'MSG/MESPAK02.PAK:016:00175':'You can turn a Digimon back into a Melody, but this resets all the data you have raised. Be careful!',
    'MSG/MESPAK02.PAK:016:00178':'Expedition teams find all sorts of things, including rare gear and Melodies you cannot get elsewhere.',
}

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    existing=ROOT/'translations/batch06.json'
    if existing.exists():
        previous=json.loads(existing.read_text(encoding='utf-8'))
        regenerated={f"{b['archive']}:{b['entry']:03d}:{i:05d}"
                     for b in previous['blocks']
                     for i in range(b['start'],b['start']+len(b['english']))}
        translated={key:value for key,value in translated.items() if key not in regenerated}
    blocks=[]
    by_source={}
    for row in records.values():by_source.setdefault(row['source'],[]).append(row)
    # Widely used proper names from the official Digimon English reference and
    # English DS games. Keep regional differences explicit in the spellings.
    for source,english in NAMES.items():
        rows=by_source.get(source,[])
        if not rows:raise ValueError(f'No Japanese name source for {source}')
        added=False
        for row in rows:
            if row['archive']!='MSG/MESPAK00.PAK' or row['id'] in translated:continue
            n=row['index']
            if not (179<=n<=1022 or 4070<=n<=4299 or 4440<=n<=4500):continue
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':n,'category':'Digimon name','english':[english],
                           'evidence_url':NAME_EVIDENCE.get(source,'https://digimon.net/reference_en/'),
                           'review_note':NAME_REVIEW.get(source,'Western spelling candidate. Confirm this individual species/form against its official English reference entry before release.')})
            added=True
        if not added and not any(row['id'] in translated for row in rows):
            raise ValueError(f'No eligible untranslated slot for {source}')
    move_url='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
    for source,english in MOVES.items():
        rows=by_source.get(source,[])
        if not rows:raise ValueError(f'No Japanese move source for {source}')
        for row in rows:
            if row['archive']!='MSG/MESPAK00.PAK' or not 1228<=row['index']<=3750 or row['id'] in translated:continue
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':'move name','english':[english],
                           'evidence_url':move_url,
                           'review_note':'English move-name match from an extraction of the licensed US Dawn/Dusk game text.'})
    for source,english in COMMON_DIALOGUE.items():
        rows=by_source.get(source,[])
        for row in rows:
            if row['archive']!='MSG/MESPAK02.PAK' or row['id'] in translated:continue
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':'Story and dialogue','english':[english.replace('<0A>','\n')]})
    for key,english in SYSTEM_DIALOGUE.items():
        row=records[key]
        if key in translated:continue
        blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':'Story and dialogue','english':[english]})
    # Melody reward messages shown after battle use dynamic party/item tokens.
    for key,english in [('MSG/MESPAK02.PAK:012:00109','Obtained a Melody!\n^0'),
                        ('MSG/MESPAK02.PAK:012:00110','Obtained a Melody!\n^0 x^1')]:
        row=records[key]
        if key in translated:continue
        blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':'battle reward message','english':[english]})
    out=ROOT/'translations/batch06.json'
    out.write_text(json.dumps({'description':'Battle Melody reward messages, repeated NPC dialogue, DigiLab/capture tutorials, canonical Digimon spelling candidates, and additional Dawn/Dusk move-name matches.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} new text slots: {len(NAMES)} Digimon names, {len(MOVES)} move sources, {len(COMMON_DIALOGUE)} repeated dialogue lines, {len(SYSTEM_DIALOGUE)} system/story lines, and 2 battle reward messages')

if __name__=='__main__':main()
