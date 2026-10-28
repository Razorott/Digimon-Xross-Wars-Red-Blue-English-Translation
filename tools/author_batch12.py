"""Build a reviewed story/quest batch and source-pattern DigiXross descriptions.

Every generated description must match one exact Japanese grammar, use a
previously reviewed species name, and use one of the explicitly reviewed
effect clauses below. The frozen review file retains the source and IDs.
"""
import csv
import json
import re
import textwrap
from collections import defaultdict

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE='Original Japanese ROM (local primary source)'
CARD='https://world.digimoncard.com/cards/'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

# Keyed by the first stable ID in the grouped queue, never by mutable order.
STORY={
 'MSG/MESPAK02.PAK:006:00178':"Be careful. They're\nwaiting for you, Taiki.",
 'MSG/MESPAK02.PAK:007:00111':"Taiki! Get back!",
 'MSG/MESPAK02.PAK:007:00129':"A Weapon Digimon?\nNot a legendary\nweapon...?",
 'MSG/MESPAK02.PAK:007:00131':"Huh!? Y-yes,\nbut... why?",
 'MSG/MESPAK02.PAK:007:00138':"After them!",
 'MSG/MESPAK02.PAK:007:00140':"Now... connect\nLost Space...\nBreak the seal...\nThe legendary\nweapon... The\nlegendary Digimon\nshall be mine...",
 'MSG/MESPAK02.PAK:007:00141':"Hey... Doesn't\nLord Zeed\nMillenniummon seem\nstrange? He's\ntalking in broken\nphrases, muttering\nnonsense, and\nbreaking the seal\nwithout telling\nthe leaders. Is\nhe all right?",
 'MSG/MESPAK02.PAK:007:00142':"It's Lord Zeed\nMillenniummon.\nHe'll be fine.\nOnce we have the\nlegendary weapon,\nROG will rule\neverything! All\nour work will\nfinally pay off.",
 'MSG/MESPAK02.PAK:007:00143':"So that's Zeed\nMillenniummon.",
 'MSG/MESPAK02.PAK:007:00144':"Zeed\nMillenniummon.\nHe's trying to\nbreak the seal!",
 'MSG/MESPAK02.PAK:007:00145':"We made it just\nin time!",
 'MSG/MESPAK02.PAK:007:00151':"I know that!\nZeed Millenniummon\nis trying to break\nthe seal at Earth\nFort, right!? So\nwhere's the\nlegendary weapon!?",
 'MSG/MESPAK02.PAK:007:00153':"A Weapon Digimon!?\nA Digimon that\nturns into a\nweapon!?",
 'MSG/MESPAK02.PAK:007:00155':"A Weapon Digimon...",
 'MSG/MESPAK02.PAK:007:00157':"All right, Taiki,\nSpadamon! Let's\ngo! It's the final\nshowdown with ROG!",
 'MSG/MESPAK02.PAK:007:00158':"We can't lose!",
 'MSG/MESPAK02.PAK:007:00159':"Hey! Shoutmon!\nSpadamon!",
 'MSG/MESPAK02.PAK:007:00160':"Huh? M-me? Wait!\nUm... uh...!?",
 'MSG/MESPAK02.PAK:007:00161':"Before they spot\nus! Three... two...\none... go!",
 'MSG/MESPAK02.PAK:007:00162':"W-wait, you guys!\nChoco... wait!",
 'MSG/MESPAK02.PAK:007:00163':"...Spadamon, this\nis no time to trip\nover your words...",
 'MSG/MESPAK02.PAK:007:00166':"G-g-g...\nSp-Spadamon...!",
 'MSG/MESPAK02.PAK:007:00167':"It's coming!\nTaiki, it's up\nto you!",
 'MSG/MESPAK02.PAK:007:00168':"Spadamon... Xros\nHeart... delete!!",
 'MSG/MESPAK02.PAK:007:00169':"ROG is finished!\nGive up on breaking\nthe Weapon\nDigimon's seal!",
 'MSG/MESPAK02.PAK:007:00170':"G-g-g... Spa...\nSpadamon...",
 'MSG/MESPAK02.PAK:007:00171':"What's with him?\nDid the shock\nscramble him?",
 'MSG/MESPAK02.PAK:007:00172':"Whoa! Why is he\nhere too!?",
 'MSG/MESPAK02.PAK:007:00173':"So that shadow\nerasing the ROG\nleaders wasn't\nZeed Millenniummon\nafter all!?",
 'MSG/MESPAK02.PAK:007:00174':"Then who was\nthat shadow!?",
 'MSG/MESPAK02.PAK:007:00175':"G-g-g... Spa...\nSpadamon... The\nlegendary...\nDigimon... shall\nbe mine...!",
 'MSG/MESPAK02.PAK:007:00176':"He's completely\nbroken. I thought\nhe'd last longer.\nNo matter... His\nhatred data gives\nme everything I\nneed...",
 'MSG/MESPAK02.PAK:007:00177':"Even Zeed\nMillenniummon!?",
 'MSG/MESPAK02.PAK:007:00178':"Who is that guy?",
 'MSG/MESPAK02.PAK:007:00179':"Everything is in\nplace. Now I must\nfind the Omega Area\nin Lost Space.\nThen Armamon\nwill be mine...",
}

MENUS={
26:"Give it to Leomon at\nKnuckle Coast East.",
27:"Report to Tentomon\nin the Front Room.",
28:"Tentomon's Tasty Gift",
29:"Deliver Tentomon's\ngift to Leomon.",
30:"A Cool Dorulumon\nis in the party.",
31:"Talk to Palmon in\nthe Front Room.",
32:"Find Piedmon in\nDark Tunnel.",
33:"Report to Palmon in\nthe Front Room.",
34:"Unpredictable?\nDefeat Piedmon!",
35:"Catch that prankster\nPiedmon and teach\nhim a lesson.",
36:"A Funky Starmon\nis in the party.",
38:"Find Zudomon at\nKnuckle Coast West.",
40:"Smooth Skin with\nthe Super Shaver",
41:"Borrow the sharp\nSuper Shaver.",
42:"Terriermon is in\nthe expedition team.",
44:"Find Drimogemon at\nKnuckle Coast West.",
46:"Smooth Skin with\nthe Miracle Shaver",
47:"Borrow the sharp\nMiracle Shaver.",
48:"Agumon is in the\nexpedition team.",
49:"Talk to Giromon in\nthe Front Room.",
50:"Talk to Datamon L\nin Fort Yard.",
51:"Talk to TD Ballmon\nin Fort Yard.",
52:"Fight the Mamemon\ngroup in Fort Yard.",
53:"Report to Giromon\nin the Front Room.",
54:"Showdown!?\nThe Mamemon Gang!",
55:"Scout the Mamemon\ngang before the\nfinal showdown.",
56:"Palmon is on\nthe DigiFarm.",
57:"Talk to Mamemon in\nthe Front Room.",
58:"Talk to Mametyrramon\nin Fort Yard.",
59:"Talk to MetalMamemon\nin Fort Yard.",
60:"Fight Giromon's\ngroup in Fort Yard.",
61:"Report to Mamemon\nin the Front Room.",
62:"Showdown!?\nThe Giromon Gang!",
63:"Scout the Giromon\ngang before the\nfinal showdown.",
64:"Tentomon is on\nthe DigiFarm.",
}

FARM={
35:"I can't do this!\nWhoever thought it\nup, come out! This\nis torture, not\ntraining!",
36:"Hey, a bookshelf!\nMaybe I'll read\nfor a change.",
37:"Reading made me\nsmarter! Nice!",
38:"I read it, but I\ndidn't understand\na thing!",
39:"Why is there a\nstudy desk here?\nIs studying part\nof training too?",
40:"I forced myself\nto study, and my\nINT went up! Any\nmore and my head\nmight explode!",
41:"Studying isn't\ntraining! This\nis torture!",
42:"I know this! A\nmagic circle!\nI'll get some\namazing power!",
43:"Whoa! My head\nfeels so clear!\nDid my INT really\ngo up that much?",
44:"Nothing happened.\nI don't believe\nin magic anymore.",
45:"Side-to-side jumps?\nFine, I'll do it!",
46:"That was easy!\nMy SPD went up!",
47:"All that effort\nfor nothing...\nWhat a letdown!",
48:"A trampoline!\nI love bouncing\non these things!",
49:"Bounce, bounce!\nMy SPD went up!\nBounce, bounce!",
50:"Bounce, bounce!\nWait... was that\nmy Achilles tendon\nthat just snapped?",
51:"A running wheel?\nYou want me to\nrun inside it?",
52:"High-speed running\nboosted my SPD\na lot!",
53:"It's cramped, and\nit makes me dizzy!\nI can't do this!",
54:"A Digimon keychain?\nLooks fun! I'll\ngive it a try.",
55:"That was so fun I\nlost track of time!\nMy friendship\nwent up a bit.",
56:"Fun, but hard.\nI'm a little\nfrustrated.",
57:"A cell phone?\nI'll send Taiki\na message!",
58:"Taiki replied!\nMy friendship\nwent up quite a\nbit!",
59:"No reply from\nTaiki... Bummer.",
60:"Taiki left his\ndigital camera.\nI'll take a photo\nof myself!",
}

# These forms are already established in the Western card game. Arrows and
# letter suffixes are game UI markers, so only the species stem is sourced.
NAMES={
 'ＳＮグレイモン':('SN Greymon',SOURCE,'Game-specific abbreviation retained; expansion unresolved.'),
 'グレイモンＯ':('Greymon O',SOURCE,'Game-specific O suffix retained.'),
 'ＳナイトモンＢＲ':('SkullKnightmon BR',CARD,'Official species stem; BR is a game-specific suffix.'),
 'ＰチェスモンＷＨ':('PawnChessmon WH',CARD,'Official species stem; WH is a game-specific suffix.'),
 'スターモンＬ':('Starmon L',CARD,'Official species stem; L is a game-specific suffix.'),
 'ＳＰスターモン':('SP Starmon',CARD,'Official species stem; SP is a game-specific suffix.'),
 'コグレ':('Kogure',SOURCE,'Human name romanized from Japanese.'),
 'コウ':('Kou',SOURCE,'Human name romanized from Japanese.'),
 'サヨ':('Sayo',SOURCE,'Human name romanized from Japanese.'),
 'ウーノ':('Uno',SOURCE,'Human name romanized from Japanese.'),
 'ドース':('Dos',SOURCE,'Human name romanized from Japanese.'),
 'トレース':('Tres',SOURCE,'Human name romanized from Japanese.'),
 'レフリー':('Referee',SOURCE,'NPC role label.'),
 'クルモン▼':('Calumon▼',CARD,'Official Western species name; arrow preserved.'),
 'クルモン▲':('Calumon▲',CARD,'Official Western species name; arrow preserved.'),
 'カブテリモン▼':('Kabuterimon▼',CARD,'Official Western species name; arrow preserved.'),
 'カブテリモン▲':('Kabuterimon▲',CARD,'Official Western species name; arrow preserved.'),
 'レオモン▼':('Leomon▼',CARD,'Official Western species name; arrow preserved.'),
 'レオモン▲':('Leomon▲',CARD,'Official Western species name; arrow preserved.'),
 'デュークモン▼':('Gallantmon▼',CARD,'Official Western species name; arrow preserved.'),
 'デュークモン▲':('Gallantmon▲',CARD,'Official Western species name; arrow preserved.'),
 'ピエモン▼':('Piedmon▼',CARD,'Official Western species name; arrow preserved.'),
 'ピエモン▲':('Piedmon▲',CARD,'Official Western species name; arrow preserved.'),
 'ムゲンドラモン▼':('Machinedramon▼',CARD,'Official Western species name; arrow preserved.'),
 'ムゲンドラモン▲':('Machinedramon▲',CARD,'Official Western species name; arrow preserved.'),
 'Ａボルケーモン▼':('AncientVolcanomon▼',CARD,'Official Western species name; arrow preserved.'),
 'Ａボルケーモン▲':('AncientVolcanomon▲',CARD,'Official Western species name; arrow preserved.'),
 'スサノオモン▼':('Susanoomon▼',CARD,'Official Western species name; arrow preserved.'),
 'スサノオモン▲':('Susanoomon▲',CARD,'Official Western species name; arrow preserved.'),
 'シャウトモン▼':('Shoutmon▼',CARD,'Official Western species name; arrow preserved.'),
 'シャウトモン▲':('Shoutmon▲',CARD,'Official Western species name; arrow preserved.'),
 'ベルゼブモン▼':('Beelzemon▼',CARD,'Official Western species name; arrow preserved.'),
 'ベルゼブモン▲':('Beelzemon▲',CARD,'Official Western species name; arrow preserved.'),
 'デジテント':('DigiTent',SOURCE,'Game item name translated from Japanese.'),
 'スカイパスポート':('Sky Passport',SOURCE,'Game item name translated from Japanese.'),
 'コードクラウン':('Code Crown',SOURCE,'Game item name translated from Japanese.'),
}

MOVES={
 'アルティガード':('Ultimate Guard',SOURCE),
 'クロノフォース':('Chrono Force',SOURCE),
 'クリムゾンウィップ':('Crimson Whip',SOURCE),
 'カオスアイ':('Chaos Eye',SOURCE),
 'デッドリーシックル':('Deadly Sickle',SOURCE),
 'ハイメガブラスター':('High Mega Blaster',SOURCE),
 'サンダークロー':('Thunder Claw',DAWN),
 'チャームウィップ':('Charm Whip',SOURCE),
 'ギガボルトショット':('Giga Volt Shot',SOURCE),
 'ブループロミネンス':('Blue Prominence',SOURCE),
 'バーニング・レイ':('Burning Ray',SOURCE),
 'テラーファング':('Terror Fang',SOURCE),
 'ヘルスクイーズ':('Hell Squeeze',SOURCE),
 'やいばのツメ':('Blade Claw',SOURCE),
 'クラッシャーパンチ':('Crusher Punch',SOURCE),
 'ワームホイール':('Worm Wheel',SOURCE),
 'デスブラスト':('Death Blast',SOURCE),
 'ヘルクラッシャー':('Hell Crusher',SOURCE),
 'シャドウネイル':('Shadow Nail',SOURCE),
 'ノーザンクロスボンバー':('Northern Cross Bomber',SOURCE),
 'ビショップクロス':('Bishop Cross',SOURCE),
 'Ｎクロスボンバー':('N Cross Bomber',SOURCE),
 'グレイスクロスフリーザー':('Grace Cross Freezer',SOURCE),
 'クロスレッド・アンド・ブルー':('Cross Red and Blue',SOURCE),
 'Ｇクロスフリーザー':('G Cross Freezer',SOURCE),
 'クロスＲ＆Ｂ':('Cross R&B',SOURCE),
}

EFFECTS={
 None:'',
 'ついかで　光のダメージを　あたえる':'Extra light damage.',
 'ついかで　アンコクのダメージを　あたえる':'Extra dark damage.',
 'ついかで　そくしさせる　こうかがある':'May cause instant KO.',
 'ついかで　まもりをさげる　こうかがある':'May lower DEF.',
 'ついかで　くらやみにさせる　こうかがある':'May cause blindness.',
 'ついかで　ちからをさげる　こうかがある':'May lower ATK.',
 'ついかで　すばやさをさげる　こうかがある':'May lower SPD.',
 'ついかで　かしこさをさげる　こうかがある':'May lower INT.',
 'ついかで　まひさせる　こうかがある':'May paralyze.',
 'ついかで　ホノオのダメージを　あたえる':'Extra fire damage.',
 'ついかで　ねむらせる　こうかがある':'May cause sleep.',
 'ついかで　カクトウダメージを　あたえる':'Extra fighting damage.',
 'ついかで　ポイズンの　こうかがある':'May poison.',
 'ついかで　水のダメージを　あたえる':'Extra water damage.',
 'ついかで　こんらんさせる　こうかがある':'May confuse.',
 'ついかで　ＨＰをドレインする　こうかがある':'May drain HP.',
 'ついかで　デンキのダメージを　あたえる':'Extra electric damage.',
 'ついかで　メロディ化のかくりつが　おおはばにアップする':
     'Greatly raises Melodize chance.',
}

DESCRIPTION_SHORT={
 'Imperialdramon Fighter Mode':'Imperialdramon FM',
 'Imperialdramon Paladin Mode':'Imperialdramon PM',
 'Gallantmon Crimson Mode':'Gallantmon CM',
 'Lucemon Falldown Mode':'Lucemon FDM',
 'Chronomon: Holy Mode':'Chronomon HM',
 'AncientMegatheriummon':'A. Megatheriummon',
}


def wrap_dialogue(value):
    out=[]
    for line in value.split('\n'):
        out.extend(textwrap.wrap(line,15,break_long_words=False,
                                 break_on_hyphens=False) or [''])
    if any(len(line)>15 for line in out):
        raise ValueError(f'Story/farm line over 15 columns: {value!r}')
    return '\n'.join(out)


def description(name,effect):
    full=name
    name=DESCRIPTION_SHORT.get(name,name)
    clause=f'DigiXross: {name} attacks.'
    if effect: clause+=' '+EFFECTS[effect]
    lines=textwrap.wrap(clause,28,break_long_words=False,
                        break_on_hyphens=False)
    if len(lines)>3:
        raise ValueError(f'DigiXross description needs {len(lines)} lines: {full}, {effect}')
    return '\n'.join(lines),name!=full


def make_review():
    queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(
        encoding='utf-8-sig'),delimiter='\t'))
    byid={key:row for row in queue for key in row['ids'].split(';')}
    bysource=defaultdict(list)
    for row in queue:bysource[(row['category'],row['japanese'])].append(row)
    selections=[];selected=set()
    def add(row,english,evidence,note):
        key=row['ids'].split(';')[0]
        if key in selected:raise ValueError(f'Duplicate source group {key}')
        selected.add(key)
        selections.append({'category':row['category'],'japanese':row['japanese'],
                           'ids':row['ids'].split(';'),'english':english,
                           'evidence':evidence,'review_note':note})
    for key,english in STORY.items():
        add(byid[key],wrap_dialogue(english),SOURCE,
            'Scene translation from original Japanese; Taiki and other human names retain original forms.')
    for number,english in MENUS.items():
        key=f'MSG/MESPAK01.PAK:000:{number:05d}'
        add(byid[key],english,SOURCE,'Quest or menu text from original Japanese.')
    for number,english in FARM.items():
        key=f'MSG/MESPAK05.PAK:000:{number:05d}'
        add(byid[key],wrap_dialogue(english),SOURCE,'DigiFarm report from original Japanese.')
    for japanese,(english,evidence,note) in NAMES.items():
        for row in bysource['Digimon names',japanese]:add(row,english,evidence,note)
    for japanese,(english,evidence) in MOVES.items():
        note=('Exact spelling appears in the licensed English Dawn/Dusk move list.'
              if evidence==DAWN else 'Working translation from Japanese; exact Western move match not verified.')
        for row in bysource['Battle moves',japanese]:add(row,english,evidence,note)

    # Reuse already reviewed species names, then add the one game-only SN form.
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    names=defaultdict(set)
    for record in translated.values():
        if record['archive']=='MSG/MESPAK00.PAK' and record['entry']==0 and 179<=record['index']<=1022:
            names[record['source']].add(record['english'])
    for japanese,(english,_,_) in NAMES.items():
        names[japanese].add(english)
    pattern=re.compile(r'^デジクロスで　(.+?)になり　こうげきする(?:<0A>(.+))?$')
    count=0
    for row in queue:
        if row['category']!='Move and item descriptions' or not row['japanese'].startswith('デジクロスで'):
            continue
        hit=pattern.fullmatch(row['japanese'])
        if not hit:raise ValueError(f'Unrecognized DigiXross grammar: {row["japanese"]}')
        japanese_name,effect=hit.groups()
        if effect not in EFFECTS:raise ValueError(f'Unreviewed effect: {effect}')
        choices=names[japanese_name]
        if len(choices)!=1:raise ValueError(f'Unresolved species name: {japanese_name} {choices}')
        full=next(iter(choices))
        english,abbreviated=description(full,effect)
        note='Exact Japanese DigiXross attack/effect pattern; species name from reviewed game name table.'
        if abbreviated:note+=f' Description-only abbreviation of {full}.'
        add(row,english,SOURCE,note)
        count+=1
    if count!=202:raise ValueError(f'Expected 202 DigiXross descriptions; found {count}')
    return selections


def main():
    frozen=ROOT/'translations/review_batch12.json'
    if frozen.exists():selections=json.loads(frozen.read_text(encoding='utf-8'))
    else:
        selections=make_review()
        frozen.write_text(json.dumps(selections,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    records=collect_messages(Rom(rom_paths()['blue']))
    previously=translate_records(records)
    target=ROOT/'translations/batch12.json'
    current_keys=set()
    if target.exists():
        for block in json.loads(target.read_text(encoding='utf-8'))['blocks']:
            current_keys.update(f"{block['archive']}:{block['entry']:03d}:{index:05d}"
                                for index in range(block['start'],block['start']+len(block['english'])))
    blocks=[];seen=set()
    for item in selections:
        for key in item['ids']:
            if key in seen or (key in previously and key not in current_keys):
                raise ValueError(f'Duplicate translation: {key}')
            if records[key]['source']!=item['japanese']:raise ValueError(f'Source changed: {key}')
            seen.add(key);r=records[key]
            blocks.append({'archive':r['archive'],'entry':r['entry'],'start':r['index'],
                           'category':item['category'],'english':[item['english']],
                           'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    target.write_text(json.dumps({'description':'Reviewed story, NPC, quests, DigiFarm, Digimon names, battle moves and source-pattern DigiXross effects.',
                                  'blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} slots from {len(selections)} source groups')


if __name__=='__main__':main()
