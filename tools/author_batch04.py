"""Add the next reviewed English name and battle-prompt pass."""
import json
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

# Canonical Western franchise spellings. Unusual game-specific codes/forms
# are omitted until their exact identity can be checked in context.
NAMES={
'ペンモン':'Penguinmon','コカトリモン':'Kokatorimon','イビルモン':'Evilmon','フックモン':'Hookmon',
'ドルガモン':'Dorugamon','ラプタードラモン':'Raptordramon','ハヌモン':'Hanumon','ボンバーナニモン':'BomberNanimon',
'ユニモン':'Unimon','イッカクモン':'Ikkakumon','ミノタルモン':'Minotaurmon','ジオグレイモン':'GeoGreymon',
'ガオガモン':'Gaogamon','ディアトリモン':'Diatrymon','レッパモン':'Reppamon','サンフラウモン':'Sunflowmon',
'ガワッパモン':'Gawappamon','サングルゥモン':'Sangloupmon','ペックモン':'Peckmon','ドリモゲモン':'Drimogemon',
'ウェンディモン':'Wendigomon','ツチダルモン':'Tsuchidarumon','エビドラモン':'Ebidramon','オクタモン':'Octomon',
'ゲソモン':'Gesomon','シーラモン':'Seadramon','シェルモン':'Shellmon','ユキダルモン':'Frigimon',
'アイスデビモン':'IceDevimon','ルカモン':'Rukamon','ウッドモン':'Woodmon','スナイモン':'Snimon',
'フライモン':'Flymon','ヤンマモン':'Yanmamon','イガモン':'Igamon','クロックモン':'Clockmon',
'タンクモン':'Tankmon','ゴーレモン':'Golemon','リボルモン':'Revolmon','ケンタルモン':'Centarumon',
'デビドラモン':'Devidramon','ドクグモン':'Dokugumon','ブイドラモン':'Veedramon','ムシャモン':'Mushamon',
'アグニモン':'Agunimon','ボルケーモン':'Volcamon','もんざえモン':'Monzaemon','スカルグレイモン':'SkullGreymon',
'メタルマメモン':'MetalMamemon','アンドロモン':'Andromon','エテモン':'Etemon','メガドラモン':'Megadramon',
'ピッコロモン':'Piximon','デジタマモン':'Digitamamon','マンモン':'Mammothmon','オオクワモン':'Okuwamon',
'トノサマゲコモン':'ShogunGekomon','エンジェウーモン':'Angewomon','ティロモン':'Tylomon','アノマロカリモン':'Anomalocarimon',
'メガシードラモン':'MegaSeadramon','ダゴモン':'Dagomon','ワーガルルモン':'WereGarurumon','ヴァンデモン':'Myotismon',
'レディーデビモン':'LadyDevimon','ガルダモン':'Garudamon','ブロッサモン':'Blossomon','リリモン':'Lillymon',
'パイルドラモン':'Paildramon','ディノビーモン':'Dinobeemon','アンティラモン':'Antylamon','アルケニモン':'Arukenimon',
'マミーモン':'Mummymon','メガログラウモン':'MegaloGrowmon','ラピッドモン':'Rapidmon','タオモン':'Taomon',
'パロットモン':'Parrotmon','インフェルモン':'Infermon','パンダモン':'Pandamon','マリンデビモン':'MarineDevimon',
'カラテンモン':'Karatenmon','キュウキモン':'Kyukimon','シンドゥーラモン':'Sinduramon','ドルグレモン':'Dorugremon',
'ハンギョモン':'Divermon','キメラモン':'Chimairamon','トリケラモン':'Triceramon','シルフィーモン':'Silphymon',
'ズドモン':'Zudomon','ホエーモン':'Whamon','マメモン':'Mamemon','インセキモン':'Insekimon',
'ギガドラモン':'Gigadramon','ライズグレイモン':'RizeGreymon','マッハガオガモン':'MachGaogamon','チィリンモン':'Chirinmon',
'ライラモン':'Lilamon','マタドゥルモン':'Matadormon','カブキモン':'Kabukimon','ジュレイモン':'Cherrymon',
'ガーベモン':'Garbagemon','マメティラモン':'Mametyrramon','ギロモン':'Giromon','ベーダモン':'Vademon',
'ファントモン':'Phantomon','グラップレオモン':'GrapLeomon','ナイトモン':'Knightmon','ブラキモン':'Brachimon',
'ヤタガラモン':'Yatagaramon','フレアモン':'Flaremon','クレシェモン':'Crescemon','フレイドラモン':'Flamedramon',
'マグナモン':'Magnamon','コンゴウモン':'Kongoumon','シュリモン':'Shurimon','ケンキモン':'Kenkimon',
'シャッコウモン':'Shakkoumon','スカルバルキモン':'SkullBaluchimon','グレイドモン':'Grademon','ワイズモン':'Wisemon',
'マーメイモン':'Mermaimon','バステモン':'Bastemon','ケルベロモン':'Cerberumon','ブルーメラモン':'BlueMeramon',
'スコピオモン':'Scorpiomon','ネフェルティモン':'Nefertimon','サーベルレオモン':'SaberLeomon','メタルエテモン':'MetalEtemon',
}

# Items unique to Xros Wars have clear, concise English renderings. Canonical
# Dawn/Dusk wording is retained where the same consumable/equipment term exists.
ITEMS={
'バンソウコウ':'Bandage','メガバンソウコウ':'Mega Bandage','ギガバンソウコウ':'Giga Bandage','テラバンソウコウ':'Tera Bandage',
'キズぐすり':'Potion','メガキズぐすり':'Mega Potion','ギガキズぐすり':'Giga Potion','テラキズぐすり':'Tera Potion',
'ダメバンソウコウ':'Damaged Bandage','げんきのもと':'Energy Seed','メガげんきのもと':'Mega Energy Seed',
'ギガげんきのもと':'Giga Energy Seed','テラげんきのもと':'Tera Energy Seed','ＭＰサプリ':'MP Supplement',
'メガＭＰサプリ':'Mega MP Supplement','ギガＭＰサプリ':'Giga MP Supplement','テラＭＰサプリ':'Tera MP Supplement',
'ハンブンやく':'Half Recovery','マンタンやく':'Full Recovery','まひなおし':'Paralysis Cure',
'ねむりなおし':'Sleep Cure','こんらんなおし':'Confusion Cure','くらやみなおし':'Blindness Cure',
'ばんのうやく':'Panacea','メガばんのうやく':'Mega Panacea','ふっかつのくすり':'Revival Medicine',
'ふっかつのひやく':'Revival Elixir','ゲートディスク':'Gate Disc','ＥＸＰ１０００':'EXP 1,000','ＥＸＰ４０００':'EXP 4,000',
'ＥＸＰ９９９９':'EXP 9,999','デジタマのカラ':'Digi-Egg Shell','ハガネのカラ':'Steel Shell',
'ギンのカラ':'Silver Shell','キンのカラ':'Gold Shell','ヌメモンねつけ':'Numemon Charm',
'パタモンねつけ':'Patamon Charm','インプモンねつけ':'Impmon Charm','アグモンねつけ':'Agumon Charm',
'カッパーコイン':'Copper Coin','シルバーコイン':'Silver Coin','ゴールドコイン':'Gold Coin','プラチナコイン':'Platinum Coin',
'データのくず':'Data Scrap','げんきナール':'Cheerful Nall','あまえっこナール':'Clingy Nall',
'ワイルドナール':'Wild Nall','クールナール':'Cool Nall','わがままナール':'Selfish Nall',
'おしとやかナール':'Gentle Nall','ロボットナール':'Robot Nall','ファンキーナール':'Funky Nall',
'デジグローブ':'DigiGlove','メガデジグローブ':'Mega DigiGlove','ギガデジハンマー':'Giga DigiHammer',
'テラデジハンマー':'Tera DigiHammer','デジニードル':'DigiNeedle','メガデジニードル':'Mega DigiNeedle',
'ギガデジソード':'Giga DigiSword','テラデジソード':'Tera DigiSword','デジヘルメット':'DigiHelmet',
'メガデジメット':'Mega DigiHelmet','ギガデジマント':'Giga DigiCape','テラデジマント':'Tera DigiCape',
'デジベスト':'DigiVest','メガデジベスト':'Mega DigiVest','ギガデジスーツ':'Giga DigiSuit','テラデジスーツ':'Tera DigiSuit',
'あかさびシールド':'Rusty Shield','ぐるぐるメガネ':'Swirly Glasses','クモノスパンツ':'Webbed Pants',
'パピルスＴシャツ':'Papyrus T-Shirt','フローラメット':'Flora Helmet','ガオはちまき':'Gaomon Headband',
'ホークティアラ':'Hawkmon Tiara','インプスカーフ':'Impmon Scarf','リボルマフラー':'Revolmon Scarf',
'キャプテンハット':'Captain Hat','ウィザーマント':'Wizardmon Cape','パンダマフラー':'Panda Scarf',
'ゴブリンベスト':'Goblimon Vest','カメシールド':'Kamemon Shield',
}

PROMPTS={
'MSG/MESPAK01.PAK:001:00059':'Choose a Digimon.\nA: Command Ring.\nX: Battle Start.',
'MSG/MESPAK01.PAK:001:00060':'Left/Right: Rotate Ring.\nA: Confirm.',
'MSG/MESPAK01.PAK:001:00061':'Choose a Special Move.\nA: Confirm.\nUses MP.',
'MSG/MESPAK01.PAK:001:00062':'Choose DigiXross.\nA: Confirm.\nUses MP.',
'MSG/MESPAK01.PAK:001:00063':'Up/Down: Choose item.\nA: Confirm.',
'MSG/MESPAK01.PAK:001:00064':'Choose a target.\nA: Confirm.',
'MSG/MESPAK01.PAK:001:00065':'Choose a tactic.\nA: Confirm.',
'MSG/MESPAK01.PAK:001:00066':'Choose a destination.\nA: Confirm.',
'MSG/MESPAK01.PAK:017:00041':'D-pad: Choose.\nA: Confirm.',
}

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    existing=ROOT/'translations/batch04.json'
    if existing.exists():
        previous=json.loads(existing.read_text(encoding='utf-8'))
        regenerated={f"{b['archive']}:{b['entry']:03d}:{i:05d}"
                     for b in previous['blocks']
                     for i in range(b['start'],b['start']+len(b['english']))}
        translated={key:value for key,value in translated.items() if key not in regenerated}
    blocks=[]
    for key,english in PROMPTS.items():
        row=records[key]
        if key not in translated:
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':'battle instruction','english':english.split('\n')})
    by_source={}
    for row in records.values():
        if row['archive']=='MSG/MESPAK00.PAK':by_source.setdefault(row['source'],[]).append(row)
    for terms,category,ranges in [(NAMES,'Digimon name',[(179,1022),(4070,4299),(4440,4500)]),(ITEMS,'Item name',[(3775,4070),(4299,4535)])]:
        for source,english in terms.items():
            rows=by_source.get(source,[])
            if not rows:raise ValueError(f'Unmatched source term {source}')
            used=False
            for row in rows:
                n=row['index']
                if not any(a<=n<=b for a,b in ranges):continue
                if row['id'] in translated:continue
                block={'archive':row['archive'],'entry':row['entry'],'start':n,'category':category,'english':[english]}
                if category=='Digimon name':
                    if source == 'マリンデビモン':
                        block['evidence_url']='https://world.digimoncard.com/cards/?card_no=EX8-061&search=true'
                        block['review_note']='MarineDevimon is the official English Bandai card spelling.'
                    elif source == 'ハンギョモン':
                        block['evidence_url']='https://world.digimoncard.com/cards/?card_no=BT15-028&search=true'
                        block['review_note']='Divermon is the official English Bandai card spelling.'
                    else:
                        block['evidence_url']='https://digimon.net/reference_en/'
                        block['review_note']='Western spelling candidate; verify the individual species and regional spelling against official English card/reference material before release.'
                else:
                    block['review_note']='Provisional English rendering for an item unique to this game; no official Western item localization has been verified.'
                blocks.append(block)
                used=True
            if not used and not any(row['id'] in translated for row in rows if any(a<=row['index']<=b for a,b in ranges)):
                raise ValueError(f'No target slot for {source}')
    out=ROOT/'translations/batch04.json'
    out.write_text(json.dumps({'description':'Expanded canonical Digimon names, item labels, and compact battle instructions. Game-specific item terms remain provisional pending Western release matches.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} new slots from {len(NAMES)} Digimon names, {len(ITEMS)} item labels, and {len(PROMPTS)} prompts')

if __name__=='__main__':main()

