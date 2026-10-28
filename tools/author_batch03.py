"""Add source-checked Digimon and inherited Dawn/Dusk move terminology.

Only exact Japanese source matches are reused. This script never guesses from
romanization or a partial name, and skips IDs already translated in earlier
batches. The JSON output remains editable like the preceding batches.
"""
import json
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages


# Western spellings checked against Bandai's English card lists. Names with
# variant/form ambiguity are intentionally absent until the specific game slot
# can be cross-checked separately.
NAMES={
    'クラモン':'Kuramon','クルモン':'Calumon','モノドラモン':'Monodramon',
    'ブイモン':'Veemon','ギルモン':'Guilmon','ドルモン':'Dorumon',
    'ベタモン':'Betamon','ガブモン':'Gabumon','ピヨモン':'Biyomon',
    'パルモン':'Palmon','テントモン':'Tentomon','オタマモン':'Otamamon',
    'ゴマモン':'Gomamon','ピコデビモン':'DemiDevimon',
    'トイアグモン':'ToyAgumon','ハグルモン':'Hagurumon',
    'プロットモン':'Salamon','ワームモン':'Wormmon',
    'ホークモン':'Hawkmon','アルマジモン':'Armadillomon',
    'テリアモン':'Terriermon','ロップモン':'Lopmon',
    'レナモン':'Renamon','インプモン':'Impmon',
    'ケラモン':'Keramon','ファルコモン':'Falcomon',
    'ゴブリモン':'Goblimon','シャコモン':'Syakomon',
    'ユキアグモン':'SnowAgumon','ガニモン':'Crabmon',
    'フローラモン':'Floramon','ララモン':'Lalamon',
    'ガオモン':'Gaomon','クダモン':'Kudamon',
    'カメモン':'Kamemon','ドラクモン':'Dracmon',
    'コクワモン':'Kokuwamon','コロナモン':'Coronamon',
    'ルナモン':'Lunamon','ヒョコモン':'Hyokomon',
    'ルーチェモン':'Lucemon','メカノリモン':'Mekanorimon',
    'ティラノモン':'Tyrannomon','デビモン':'Devimon',
    'エアドラモン':'Airdramon','シードラモン':'Seadramon',
    'ヌメモン':'Numemon','カブテリモン':'Kabuterimon',
    'ガルルモン':'Garurumon','エンジェモン':'Angemon',
    'ベジーモン':'Vegiemon','オーガモン':'Ogremon',
    'バケモン':'Bakemon','スカモン':'Sukamon',
    'レオモン':'Leomon','クワガーモン':'Kuwagamon',
    'ゲコモン':'Gekomon','テイルモン':'Gatomon',
    'ウィザーモン':'Wizardmon','トゲモン':'Togemon',
    'ガードロモン':'Guardromon','エクスブイモン':'ExVeemon',
    'スティングモン':'Stingmon','バードラモン':'Birdramon',
    'アンキロモン':'Ankylomon','ガルゴモン':'Gargomon',
    'グラウモン':'Growlmon','キュウビモン':'Kyubimon',
    'クリサリモン':'Kurisarimon','シーサモン':'Seasarmon',
    'アクィラモン':'Aquilamon',
}

# The English strings occur in the US Digimon World Dawn/Dusk release data
# extracted by joaomlsantos. This is a spelling cross-check, not an automatic
# assumption that every similar-sounding Japanese attack is the same move.
MOVES={
    'たいあたり':'Charge','リトルブリザード':'Little Blizzard',
    'ハイドロウォーター':'Hydro Water','メガトンハイドロ':'Megaton Hydro',
    'ギガトンハイドロ':'Gigaton Hydro','ダブルウェーブ':'Double Wave',
    'トリプルウェーブ':'Triple Wave','オーシャンウェーブ':'Ocean Wave',
    'ソニックボイス':'Sonic Voice','ハイソニックボイス':'High Sonic Voice',
    'ハイパートルネード':'Hyper-Tornado','エアカッター':'Air Cutter',
    'トップガン':'Top Gun','メガナパーム':'Mega Napalm',
    'ヴォルケナパーム':'Volcano Napalm','ドラモンクロー':'Dramon Claw',
    'タイニーボム':'Tiny Bomb','ノーマルボム':'Normal Bomb',
    'ノーマルミサイル':'Normal Missile','ホーリースラッシュ':'Holy Slash',
    'シャインスラッシュ':'Shine Slash','ロイヤルスラッシュ':'Royal Slash',
    'ホーリーボルト':'Holy Bolt','ライジング・レイ':'Rising Ray',
    'メタルスター':'Metal Star','クレイジークレーン':'Crazy Crane',
    'ヘブンズリッパー':"Heaven's Ripper",'スパイダースレッド':'Spider Thread',
    'ソウルチョッパー':'Soul Chopper','ヒート・バイパー':'Heat Viper',
    'アングリーロック':'Angry Rock','ガトリングパンチ':'Gatling Punch',
    'ウイニングパンチ':'Winning Punch','ポイズンパウダー':'Poison Powder',
    'スパイラルボーン':'Spiral Bone','ギルティブラック':'Guilty Black',
    'ネクロフォビア':'Necrophobia','ダークネスウェーブ':'Darkness Wave',
    'ビショップレーザー':'Bishop Laser','ルークガトリング':'Rook Gatling',
    'メタルメテオ':'Metal Meteor','メガトンプレス':'Megaton Press',
    'ファイアーボール':'Fire Ball','ファイアーブレス':'Fire Breath',
    'ヘブンズナックル':'Heaven Knuckle',
    'フレイムダイブ':'Flame Dive','ライトニングスピア':'Lightning Spear',
}


def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    previous=set()
    for path in [ROOT/'translations/batch01.json',ROOT/'translations/batch02.json']:
        for block in json.loads(path.read_text(encoding='utf-8'))['blocks']:
            previous.update(f"{block['archive']}:{block['entry']:03d}:{i:05d}"
                            for i in range(block['start'],block['start']+len(block['english'])))
    source_to_ids={}
    for row in records.values():
        if row['archive']=='MSG/MESPAK00.PAK':
            source_to_ids.setdefault(row['source'],[]).append(row)
    missing=set(NAMES)|set(MOVES)
    blocks=[]
    for source,english,category in [(s,e,'Digimon name') for s,e in NAMES.items()]+[(s,e,'move name') for s,e in MOVES.items()]:
        for row in source_to_ids.get(source,[]):
            # The common-name table also contains item names and debug names;
            # only the actual Digimon and move spans are patched here.
            n=row['index']
            if category=='Digimon name' and not (179<=n<=1022 or 4070<=n<=4299 or 4440<=n<=4500):continue
            if category=='move name' and not (1228<=n<=3750):continue
            missing.discard(source)
            if row['id'] in previous:continue
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':n,'category':category,'english':[english]})
    if missing:raise ValueError(f'Unmatched source terms: {sorted(missing)}')
    out=ROOT/'translations/batch03.json'
    out.write_text(json.dumps({'description':'Verified Western Digimon spellings and matched US Dawn/Dusk battle move names.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(len(blocks),'new name/move slots',len(NAMES),'name terms',len(MOVES),'move terms')


if __name__=='__main__':main()
