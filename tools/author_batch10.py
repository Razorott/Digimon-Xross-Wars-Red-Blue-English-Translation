"""Curated title-era dialogue, missions, battle moves and species.

The Japanese source and IDs are taken from the original Blue ROM queue. This
file keeps the editorial decisions separate from the immutable original ROMs.
"""
import csv
import json
import textwrap
from pathlib import Path
from xros_text import ROOT

CARD='https://world.digimoncard.com/cards/'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
ROM='Original Japanese ROM (local primary source)'

# Queue position, English. Preserve each spoken beat with an explicit line.
STORY={
0:"First, there's me,\nTaiki Kudo!\nI'm the hero of\nDigimon Xros Wars!\nI can't ignore\nanyone in trouble,\nso once again I\nget swept up in it!",
1:"Supporting me is\nmy lively manager,\nmy childhood friend\nAkari Hinomoto!",
2:"Then there's the\noverheated Zenjiro\nTsurugi!\nHe says we're\neternal rivals, but\nI don't remember\nany of that!",
3:"Leave the Digimon\nintroductions to me!\nI'm Shoutmon,\nTaiki's partner and\nfuture Digimon King!\nI'll give it my all\nin Xros Wars, too!",
4:"For better or\nworse, he's always\nstraightforward.",
5:"Big, sturdy and\ntough, Ballistamon\nis our rock!",
6:"A quiet, dependable\nsamurai.",
7:"Dorulumon! Smug,\nsarcastic, careless\nand unreliable!",
8:"He won't let\nanything tie him\ndown. A free spirit.",
9:"A cry for help led\nus to a strange\nfloating island:\nElestou Zone!",
10:"And the island\nwasn't the only\nstrange thing...",
11:"There was Sky Fort,\na mobile fortress\nwith a secret.\nSpadamon guarded\nthe Zone. A fusion\nsystem created\nnew Digimon. And\nan enemy army was\nafter all of them...",
12:"What did you say?!",
13:"You'll soon learn\nhow foolish you've\nbeen. But by the\ntime you do...\nit will be too\nlate for anything.",
14:"A machine to save\nour data so far.\nWe still can't\nuse it...",
15:"Sadly, that's all\nfor this demo!\nThanks for playing,\neveryone!!",
16:"Our real adventure\nhasn't even begun!",
17:"Keep cheering for\nthe game and the\nTV anime!",
18:"Count on us!!\nSee you all later!",
19:"It's terrible!\nJust terrible!",
20:"What's happened?",
21:"Graaaargh!!",
22:"N-no! Stop it!",
23:"Spadamon!\nGet away!",
24:"...Linkage reject!\nDevice overload!",
25:"W-what?! An\nexplosion?! Taiki,\nShoutmon, duck!",
26:"You've got to be\nkidding me...!",
27:"Hey... someone!\nPlease help me!\nA dark, scary\nshadow won't let\nme go... No...\nI don't want to\nforget everyone.\nStay out of my\nheart... Hurry...\nhelp... me...",
28:"Sparrowmon...!",
29:"You're awake,\nTaiki!",
30:"I heard Sparrowmon\ncalling for help.\nSomeone has him.\nWe have to hurry!",
31:"...Where are we?",
}

QUESTS={
0:"Clear 'Rising Idols!\nTerriermon & Lopmon'",
1:"Meet Mamemon's friend\nin Crystal Volcano West.",
2:"Meet Giromon's friend\nin Crystal Volcano East.",
3:"Test your skills against\na tough opponent!",
4:"Test your strength in\nCrystal Volcano East.",
5:"Meet Piedmon in Digital\nSpace South 7.",
6:"Meet Piedmon in Digital\nSpace North 4.",
7:"Meet Piedmon in Digital\nSpace North 3.",
8:"Meet Piedmon in Digital\nSpace North 8.",
9:"Clear 'Piedmon's\nDigimon Quiz'",
10:"Talk to WereGarurumon\nin Papyrus City.",
11:"Find Terriermon in\nDigital Space North.",
12:"Find Lopmon in\nDigital Space North.",
13:"Report to their manager,\nLadyDevimon.",
14:"Super Idols!\nTerriermon & Lopmon",
15:"Get an autograph from\nthe idol duo TeriLop!",
16:"Clear 'Popular Idols!\nTerriermon & Lopmon'",
17:"Talk to Lillymon in\nPapyrus City.",
18:"Find Mermaimon at\nTokona Coast.",
19:"Find Mermaimon at\nTokona Sea G3.",
20:"Find the treasure\nMermaimon promised.",
21:"Ruler of the Deep Sea!\nAegisdramon",
22:"Rescue Mermaimon from\nAegisdramon.",
23:"Clear 'Ruler of the\nSea?! Pirates'",
24:"Sky Garden A",
}

# Readable names for direct identifications. A game-only suffix stays short.
NAMES={
'ＡＲブイドラモン':('AeroVeedramon',CARD,'Official Western species name.'),
'ＵＦブイドラモン':('UlforceVeedramon',CARD,'Official Western species name.'),
'Ａグレイモン':('AncientGreymon',CARD,'A is the in-game Ancient abbreviation.'),
'Ａガルルモン':('AncientGarurumon',CARD,'A is the in-game Ancient abbreviation.'),
'ＳグレイモンＲＭ':('ShineGreymon RM',CARD,'RM abbreviates the game form Ruin Mode.'),
'ＭガオガモンＢＭ':('MirageGaogamon BM',CARD,'BM abbreviates Burst Mode for this game field.'),
'チャツラモン':('Caturamon',CARD,'Official Western species spelling.'),
'シャウト×４Ｂ':('Shoutmon X4B',CARD,'Matches official English DigiXros form notation.'),
'シャウトモンＢ':('Shoutmon B',CARD,'B is retained as the game form suffix.'),
'シャウト×３ＧＭ':('Shoutmon X3GM',CARD,'Game form suffix GM retained.'),
'シャウト×３ＳＤ':('Shoutmon X3SD',CARD,'Game form suffix SD retained.'),
'シャウト×４Ｓ':('Shoutmon X4S',CARD,'Game form suffix S retained.'),
'シャウト×５Ｓ':('Shoutmon X5S',CARD,'Game form suffix S retained.'),
'ドルルキャノン':('Dorulu Cannon',CARD,'Official card lists use Dorulu Cannon.'),
'スターソード':('Star Sword',ROM,'Direct game form name.'),
'ジェットスパロウ':('Jet Sparrow',ROM,'Direct game form name.'),
}

# An exact Dawn/Dusk match is cited only where it exists. Everything else is a
# faithful working translation from the Japanese source, for later review.
MOVES={
'フロストクロー':'Frost Claw','シェイキングパルス':'Shaking Pulse',
'ブレイドツイスター':'Blade Twister','さくらふぶき':'Cherry Blossom Storm',
'ヘルファイアー':'Hellfire','バナナスリップ':'Banana Slip',
'ダイナ・キャノン':'Dyna Cannon','ブルーハワイデス':'Blue Hawaii Death',
'ドルルキャノン':'Dorulu Cannon','バディブラスター':'Buddy Blaster',
'スターブレイド':'Star Blade','ホーンストライク':'Horn Strike',
'スピアニードル':'Spear Needle','ツインスピア':'Twin Spear',
'スリービクトライズ':'Three Victorize','ヴァンパイアダンス':'Vampire Dance',
'プラズマブラスター':'Plasma Blaster','ガイアリアクター':'Gaia Reactor',
'オーロラブレイザー':'Aurora Blazer','ブレスオブペルーン':'Breath of Perun',
'ビリオンスタブ':'Billion Stab','ビクトリーブレイブ':'Victory Brave',
'ギガーススパイラル':'Gigas Spiral','コズモビクトリー':'Cosmo Victory',
'パンデモニウムフレイム':'Pandemonium Flame',
'クロノパラドックス':'Chrono Paradox','ジェノサイドＡＴＫ':'Genocide ATK',
'ＨＰディスク':'HP Disc','ＭＰディスク':'MP Disc',
'ソウルパンチ':'Soul Punch','ショットアームズ':'Shot Arms',
}

def main():
    rows=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    bycat={c:[r for r in rows if r['category']==c] for c in {r['category'] for r in rows}}
    specs=[]
    for n,english in STORY.items():
        r=bycat['Story and dialogue'][n]
        specs.append((r,english,ROM,'Translation from the original game dialogue.'))
    for n,english in QUESTS.items():
        r=bycat['Menus, quests and battle prompts'][n]
        specs.append((r,english,ROM,'Translation from the original quest text.'))
    for cat,mapping in [('Digimon names',NAMES),('Battle moves',MOVES)]:
        for source,result in mapping.items():
            matches=[r for r in bycat[cat] if r['japanese']==source]
            if not matches:raise ValueError(f'Missing source: {source}')
            if isinstance(result,tuple):english,evidence,note=result
            else:english,evidence,note=result,ROM,'Working move translation; no exact Dawn/Dusk list match verified.'
            for r in matches:specs.append((r,english,evidence,note))
    blocks=[];review=[]
    for row,english,evidence,note in specs:
        if row['category']=='Story and dialogue':
            english='\n'.join(textwrap.fill(line,width=15,break_long_words=False,break_on_hyphens=False)
                              for line in english.split('\n'))
        review.append({'category':row['category'],'japanese':row['japanese'],
                       'english':english,'evidence':evidence,'review_note':note})
        for key in row['ids'].split(';'):
            archive,entry,index=key.rsplit(':',2)
            blocks.append({'archive':archive,'entry':int(entry),'start':int(index),
                           'category':row['category'],'english':[english],
                           'sources':[evidence] if evidence.startswith('https://') else [],
                           'review_note':note})
    (ROOT/'translations/batch10.json').write_text(json.dumps({
        'description':'Original story, NPC lines, quests, Western Digimon names, and battle moves.',
        'blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'translations/review_batch10.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} slots, {len(review)} unique editorial entries')

if __name__=='__main__':main()
