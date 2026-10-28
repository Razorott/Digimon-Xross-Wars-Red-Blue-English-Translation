"""Author the next reviewed story, quest, battle, farm and item text batch."""
import csv
import json
import textwrap
from xros_text import ROOT

CARD='https://world.digimoncard.com/cards/'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
PRAIRIE='https://digimon.net/reference_en/detail.php?directory_name=prairiemon'
SOURCE='Original Japanese ROM (local primary source)'

STORY={
0:"This is the\nKumonos Ruins.",
1:"Spadamon and I\nwere searching\naround here. That\nPass-whatever\nexplosion must've\nblown us away!\nWho knew Spadamon\nhad that power?",
2:"Y-yeah... I was\ndesperate then.\nI don't know how\nI did it. It felt\nlike the power I\nhad when I started\nthe Capacitor Tower.\nWhy is that...?",
3:"I see. But why\nare they after\nthe legendary\nancient weapon?\nAnd Spadamon's\npower... Is it\nlinked to the\nCapacitor Tower's\ncaretaker?",
4:"Spadamon, I don't\nget all this, but\nyou're still you.\nDon't worry so\nmuch about it.",
5:"Yeah... Wait,\nis Sparrowmon one\nof your friends?\nIf he's captive,\nhe may be at\nSkull Glacier\nahead of us.",
6:"Why do you think\nhe's at Skull\nGlacier? Wait...\nHas Sparrowmon\nalready become\na skull?!",
7:"Ahaha... I don't\nthink you need to\nworry about that.",
8:"That's not what I\nmeant! The ROG\nleader at Skull\nGlacier is really\nterrifying. I\nwouldn't go near\nhim without you!",
9:"A terrifying\nDigimon... I'm\nworried about\nSparrowmon. Come\non, Shoutmon,\nSpadamon. Let's\ngo to Skull\nGlacier now.",
10:"I am IceDevimon,\nROG's Freeze\nLeader! IceDevimon\nthe Blizzard!",
11:"What does that\nmean?",
12:"ROG's Digimon\nleaders are all\ngathering at\nCrystal Volcano,\nwhere Earth Fort\nis!",
13:"What are they\ngathering for?",
14:"It seems Earth\nFort is run by\nROG's strongest\nboss, Zeed\nMillenniummon!\nThe leaders guard\nit closely. Maybe\nhe ordered them\nto gather there.",
15:"So he's the boss\nof the bad guys!\nLet's charge in!",
16:"But something's\nwrong. If they\ndon't want to be\nfound, why gather\nso openly? This\nmust be a trap to\ncapture Spadamon!",
17:"You're right. It\nwould be risky to\nenter enemy ground\nnow. Let's learn\nmore first...",
18:"No. We go now.",
19:"Remember what\nAnubismon said\nin Papyrus Desert?\nThey found the\nseal on the\nlegendary ancient\nweapon. If ROG\nreally found it,\nthey'll try to\nbreak the seal\nright away.",
20:"So the seal is\nat Earth Fort?",
21:"...Spadamon,\nyou've grown so\nstrong since we\nmet. I need to\nfind some way to\nhelp, too! I'll\ntalk strategy with\nCutemon in the\nCommand Room.",
22:"H-hey, wait!\nNo getting a\nhead start!",
23:"Crystal Volcano,\nthen! Come on,\nTaiki! We can't\nlet ROG use the\nancient weapon!",
24:"Right! Let's go!",
}

MENUS={
0:'Skull Seabed',1:'Papyrus Cave',2:'Tokona Sea 1',3:'Tokona Sea 4',
4:'Tokona Coast 2',5:'Tokona Sea G1',6:'Tokona Sea G2',7:'Tokona Sea G3',
8:'Stealth Cavern',9:'Link Box',10:'Colosseum',11:'Lost Space South 1',
12:'Buy Farm Goods',13:'Buy Items',14:'Total: ^0',
15:'Yes, begin.',16:'No, not yet.',
17:'Talk to Terriermon in\nthe Front Room.',
18:'Catch Devimon in\nDigital Space East.',
19:'Find the memory in\nFort Yard.',
20:'Report to Terriermon\nin the Front Room.',
21:'Recover the\nDevelopment Memory!',
22:'Recover Terriermon\'s\nDevelopment Memory\nfrom Devimon.',
23:'Ballistamon, the\nRobot, is in the party.',
24:'Talk to Tentomon in\nthe Front Room.',
}

FARM={
0:"Oh, a pyramid.\nI'll rest inside...",
1:"I feel refreshed!\nMy max MP went up.\nIs this what they\ncall pyramid power?",
2:"I suddenly feel\nawful... Is this\nnegative pyramid\npower or what?!",
3:"Hey, a punching\nbag! Let's give\nit a few hits!",
4:"Ha! How was that?\nMy strength went\nway up. Feels\ngreat!",
5:"Ha! How was that?\n...Ow! I twisted\nmy wrist. This\nis the worst!",
6:"Is this a training\nlog? I guess I'm\nsupposed to ram\ninto it...",
7:"See that? My\nstrength shot up!",
8:"Will doing such\nboring work really\nmake me stronger?",
9:"A giant boulder!\nI just have to\npush it, right?",
10:"Whoa, I got a lot\nstronger! That\nwas easier than\nI expected.",
11:"It won't budge!\nCan this thing\neven move?",
12:"Hey, a punching\nmachine! I'll\ngive it all I've\ngot!",
13:"Heh! Not bad,\nright? Looks like\nmy defense rose!",
14:"T-that's enough\nfor now!",
15:"A training cannon?\nI have to take\nthe shot? Fine!\nBring it on!",
16:"I took the hit!\nMy defense went\nup... But was\nthat worth it?",
17:"You really fired\nit? You fool!\nNo way I could\nstand that!",
18:"What's with this\niron ball? Taking\na hit from that\ncounts as training?",
19:"I held it off!\nMy defense rose,\nand I feel braver!",
}

NAMES={
'シャウジンモン':('Shaujinmon','https://world.digimoncard.com/cards/?category=522016&search=true','Official English card spelling; Japanese romanization Shawujinmon differs.'),
'プレイリモン':('Prairiemon',PRAIRIE,'Official English Digimon Encyclopedia spelling.'),
'ベルゼブモンＬ':('Beelzemon L',CARD,'Official species name; L is the game-specific form suffix.'),
'Ｇクワガーモン':('GranKuwagamon',CARD,'Official English card spelling.'),
'Ａイリスモン':('AncientKazemon',CARD,'Japanese AncientIrismon has the Western name AncientKazemon.'),
'Ａメガテリウモン':('AncientMegatheriummon',CARD,'Official English card spelling.'),
'Ａマーメイモン':('AncientMermaimon',CARD,'Official English card spelling.'),
'Ａワイズモン':('AncientWisemon',CARD,'Official English card spelling.'),
'Ａスフィンクモン':('AncientSphinxmon',CARD,'Official English card spelling.'),
'Ａトロイアモン':('AncientTroymon',CARD,'Official English card spelling.'),
'Ａビートモン':('AncientBeetlemon',CARD,'Official English card spelling.'),
'Ａボルケーモン':('AncientVolcanomon',CARD,'Official English card spelling.'),
}

MOVES={
'クロー＆ファング':('Claw & Fang',SOURCE),
'シューティングオレ':('Shooting Ore',SOURCE),
'クロスフォー':('Xros Four',SOURCE),
'さんのアワ':('Acid Bubbles',SOURCE),
'アイスアロー':('Ice Arrow',SOURCE),
'みだれアイスアロー':('Ice Arrow Barrage',SOURCE),
'アークティックブリザード':('Arctic Blizzard',SOURCE),
'グレートブリザード':('Great Blizzard',SOURCE),
'ティアーバブル':('Tear Bubble',SOURCE),
'なないろのアワ':('Rainbow Bubbles',SOURCE),
'かまいたち':('Wind Sickle',SOURCE),
'プチトルネード':('Small Tornado',DAWN),
'ギガフレイム':('Giga Flame',SOURCE),
'ざんか':('Lingering Flame',SOURCE),
'ジオマグマナパーム':('GeomgmNapalm',DAWN),
'ガトリングミサイル':('Gatling Missile',SOURCE),
'シャインレーザー':('Shine Laser',SOURCE),
'スターライトエクスプロージョン':('Starlight Explosion',SOURCE),
'ホーリークロス':('Holy Cross',SOURCE),
'シャインクロス':('Shine Cross',SOURCE),
'サイレンスハッグ':('Silence Hug',SOURCE),
'ホーリーナックル':('Holy Knuckle',SOURCE),
'ダークサンダー':('Dark Thunder',SOURCE),
'グラビティボール':('Gravity Ball',SOURCE),
'ダブルエッジ':('Double Edge',SOURCE),
'ソーラーハンマー':('Solar Hammer',SOURCE),
}

ITEMS={
'エクスキャリバー':'Excalibur','ベルセルクソード':'Berserk Sword',
'グレイダルファー':'Greydalfar','ミョルニル':'Mjolnir',
'ジオグレイソード':'GeoGrey Sword','カキカキクン':'Kakikaki-kun',
'キングスティック':'King Stick','コロナＢソード':'Corona B Sword',
'ＱＵスティック':'Queen Stick','ベレンヘーナ':'Berenjena',
'ガルルキャノン':'Garuru Cannon','Ｐトロンレーザー':'P-Tron Laser',
'ドラモンキラー':'Dramon Killer','ナザルネイル':'Nazar Nail',
'ＧＳＴランス':'GST Lance','りゅうざんまる':'Ryuzanmaru',
'アンブロジウス':'Ambrosius','オリンピア':'Olympia',
'グングニル':'Gungnir','ムスペルヘイム':'Muspelheim',
}

def main():
    frozen=ROOT/'translations/review_batch11.json'
    if frozen.exists():
        selections=json.loads(frozen.read_text(encoding='utf-8'))
    else:
        rows=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
        bycat={c:[r for r in rows if r['category']==c] for c in {r['category'] for r in rows}}
        selections=[]
        def add(row,english,evidence,note):
            selections.append({'category':row['category'],'japanese':row['japanese'],
                               'ids':row['ids'].split(';'),'english':english,
                               'evidence':evidence,'review_note':note})
        for category,mapping in [('Story and dialogue',STORY),
                                 ('Menus, quests and battle prompts',MENUS),
                                 ('DigiFarm reports',FARM)]:
            for n,english in mapping.items():
                add(bycat[category][n],english,SOURCE,'Translated from the original game text.')
        for category,mapping in [('Digimon names',NAMES),('Battle moves',MOVES),
                                 ('Items and equipment',ITEMS)]:
            for japanese,entry in mapping.items():
                matches=[r for r in bycat[category] if r['japanese']==japanese]
                if not matches:raise ValueError(f'Missing queue source: {category} {japanese}')
                if category=='Digimon names':english,evidence,note=entry
                elif category=='Battle moves':
                    english,evidence=entry
                    note=('Corresponds to the English Dawn/Dusk move-list spelling.'
                          if evidence==DAWN else 'Working translation; no exact Dawn/Dusk match verified.')
                else:english,evidence,note=entry,SOURCE,'Working item rendering; Western item name not verified.'
                for row in matches:add(row,english,evidence,note)
        frozen.write_text(json.dumps(selections,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Recheck every frozen ID and Japanese byte string against the originals.
    from build import collect_messages,translate_records
    from xros_text import Rom,rom_paths
    records=collect_messages(Rom(rom_paths()['blue']))
    previously=translate_records(records)
    blocks=[];seen=set()
    for item in selections:
        english=item['english']
        if item['category'] in ('Story and dialogue','DigiFarm reports'):
            english='\n'.join(textwrap.fill(line,width=15,break_long_words=False,
                        break_on_hyphens=False) for line in english.split('\n'))
        for key in item['ids']:
            if key in seen or key in previously:raise ValueError(f'Duplicate translation: {key}')
            if records[key]['source']!=item['japanese']:raise ValueError(f'Source changed: {key}')
            seen.add(key);r=records[key]
            blocks.append({'archive':r['archive'],'entry':r['entry'],'start':r['index'],
                           'category':item['category'],'english':[english],
                           'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    out=ROOT/'translations/batch11.json'
    out.write_text(json.dumps({'description':'Reviewed story, NPC, quests, farm, battle moves, names and equipment.',
                               'blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} slots from {len(selections)} source groups')

if __name__=='__main__':main()
