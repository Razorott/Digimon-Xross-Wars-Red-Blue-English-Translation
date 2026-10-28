"""Reviewed batch 14: quests, NPCs, DigiFarm, equipment and battle moves.

The frozen review includes Japanese source, exact IDs, and provenance. Re-runs
read that review instead of the mutable untranslated work queue.
"""
import csv
import json
import textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE='Original Japanese ROM (local primary source)'
CARD='https://world.digimoncard.com/cards/'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

QUEST={
121:'Talk to Lilamon in\nSkull City.',
124:'Give it to Puppetmon\nin Dark Tunnel.',
125:'Report to Lilamon\nin Skull City.',
126:'Meteorite and Puppetmon',
127:'Find the meteorite\nPuppetmon wants.',
128:'A Gentle Sunflowmon\nis on the farm.',
129:'Talk to Parrotmon in\nSkull City.',
132:'Give it to ToyAgumon\nin Dark Tunnel.',
133:'Report to Parrotmon\nin Skull City.',
134:'Meteorite and ToyAgumon',
135:'Find the meteorite\nToyAgumon wants.',
136:'A Gentle Garudamon\nis on the farm.',
137:'Talk to ToyAgumon\nin the Front Room.',
139:'Deliver the wrapped\ngift at Knuckle\nCoast East.',
140:'Get Lopmon\nautograph beside\nTerriermon.',
141:'Give it to ToyAgumon\nin the Front Room.',
142:'Rising Idols!\nTerriermon & Lopmon',
143:'Deliver a gift to\nnew idol duo\nTeriLop.',
145:'Talk to Kabukimon\nin Kumonos City.',
147:'Report to Kabukimon\nin Kumonos City.',
148:'VS Lucemon FDM\n& Knightmon',
151:'Talk to Knightmon\nin Kumonos City.',
153:'Report to Knightmon\nin Kumonos City.',
154:'VS Kabukimon\n& Shurimon',
157:'Talk to Reppamon\nin Guruguru City.',
158:'Find Dinobeemon in\nGuruguru Amazon W.',
159:'Report to Reppamon\nin Guruguru City.',
160:'An Insect Idol?\nDinobeemon',
161:'Find and interview\nDinobeemon!',
162:'A Cool Snimon is\non the expedition\nteam.',
163:'Talk to Drimogemon\nin Guruguru City.',
164:'Find Paildramon in\nGuruguru Amazon W.',
165:'Report to Drimogemon\nin Guruguru City.',
166:'A Beast Idol?\nPaildramon',
167:'Find and interview\nPaildramon!',
168:'A Cool Ankylomon\nis on the\nexpedition team.',
169:'Talk to Dorumon in\nthe Front Room.',
170:'Investigate the\nsound in Guruguru\nAmazon West.',
171:'Convince\nShogunGekomon.',
172:'Report to Dorumon\nin the Front Room.',
173:'A Singing Lord\nand His Servants',
174:'Find the source\nof the noise in\nGuruguru Amazon.',
}

FARM={
81:"A mini shower...\nDo I have to get\nunder it?",
82:"That feels great!\nMy first shower\nin ages! My EXP\nwent up, too!",
83:"I hate showers.\nI just get wet.\nI won't die if\nI skip one...",
84:"A little fishing\npond! Think I can\ncatch anything?",
85:"Wow! Fish after\nfish! My EXP is\nshooting up!",
86:"Not even a nibble.\nAre there any\nfish in here?",
87:"Am I supposed to\ntrain under this\nwaterfall?",
88:"Forget about EXP.\nJust stand under\nthe falls... and\nEXP will follow!",
89:"Ow, this hurts!\nI can't breathe,\nand it's freezing!\nWhat's the point?",
90:"What a pretty\nflower. It smells\ngood, too.",
91:"Its sweet scent\nand beauty calmed\nme down. I think\nmy EXP went up.",
92:"Achoo! Ah-choo!\nIs that pollen!?",
93:"Hey, a treehouse!\nLooks cozy. I'll\ntake a peek.",
94:"I love the calm\nfeeling here. My\nEXP went up a lot.",
95:"Hmm... This isn't\nfor me. Maybe a\nforest fairy could\nlive here.",
96:"A computer! I'll\ngo online and see\nwhat's out there!",
97:"I found rare info!\nMy EXP went up\nwhile I searched!",
98:"Between us... I\npretended to know.\nWhat's the\ninternet?",
99:"A solar panel?\nHow does this\nthing work?",
}

STORY={
('013',60):"He's embarrassed!\nI thought he was\ngloomy at first,\nbut Spadamon's\npretty funny.",
('013',61):"Wait a second.\nI'll open it.",
('013',62):"Things are going\npretty well so\nfar...",
('013',65):"Will you name\nthis Farm Island\ntoo?",
('013',66):"Thanks, Taiki!\nThat's a great\nname. We can also\naccess more of the\nDigiScore folder.",
('013',70):"Now we can use\nmore DigiFusion!\nStill, getting\nthese towers to\nwork is a pain.",
('013',71):"I-I can't help it!\nI don't know how\nthis works either!",
('013',72):"True. The tower's\na mystery. How do\nyou work that\npanel, anyway?",
('013',73):"I don't know. I\njust somehow know\nwhat to do... Is\nit tied to my\nmemories?",
('013',74):"Maybe. Don't\nworry too much\nabout it.",
('013',75):"It's noisy outside\nagain. Let's go\nsee what's up.",
('013',76):"Hanumon!? You\ncame for us!",
('013',77):"Hey, Spadamon!\nGanimon told me.\nThanks for getting\nthe tower going!\nIt feels like\nwe're home again!",
('013',78):"You lived here?",
('013',79):"He's this area's\nleader. When ROG\nattacked, Hanumon\nand his group\nfought to the end!",
('018',23):"West Knuckle City\nmeans Penguinmon's\nItem Shop! The W\nstands for\nwonderful wares!",
('018',25):"Welcome to West\nKnuckle City's\nFarm Shop! Yeah!\nLove you! Boom!",
('018',26):"I thought we'd\nnever come back.\nROG even took\nSky Fort. Thank\nyou, Taiki and\nSpadamon!",
('018',28):"You found your\nlittle friend?\nGood! He was\njust playing?\nI didn't expect\nthat...",
('018',29):"Another lost\nfriend found?\nGood! More allies\nmake you stronger.\nTake care of them.",
('018',30):"You know where\nyour missing\nfriend is? There\naren't many places\nto hide someone\nin this zone.",
('018',31):"Still looking for\nyour friend? At\nleast you've found\na way toward the\nruins where he's\ntrapped.",
('018',32):"You rescued your\nfriend? Well done!\nI'm impressed.",
('018',33):"Earth Fort? Maybe\nit's underground.\nI know the water,\nnot the earth.",
('018',34):"In East Knuckle\nCity, Penguinmon's\nItem Shop sells\nexcellent goods!",
('018',36):"Welcome to East\nKnuckle City's\nFarm Shop! Yeah!\nWant you! Boom!",
}

MOVES={
1376:('Petrifier',DAWN),
1377:('Pollen Spray',CARD),
1378:('Sing a Song',SOURCE),
1379:('Healing Spring',DAWN),
1380:('Saint Heal',DAWN),
1381:('Final Heal',SOURCE),
1382:('MedicalSystem',DAWN),
1383:('Gaia Healing',DAWN),
1384:('Mental Cure',DAWN),
1385:('Power of Love',SOURCE),
1386:('Water of Life',DAWN),
1387:('Dark Savior',DAWN),
1388:('Electric Shock',DAWN),
1389:('Healing Air',DAWN),
1390:('Shining Heal',SOURCE),
1391:('Purification',DAWN),
1392:('Nanomech Heal',DAWN),
1393:('Kusanagi',DAWN),
1395:('Master Fire',SOURCE),
1396:('Eternal Nirvana',SOURCE),
1397:('Extreme Jihad',SOURCE),
1399:('Rainbow Symphony',SOURCE),
1400:('Sharpness Claymore',SOURCE),
1401:('Freezing Blizzard',SOURCE),
1406:('Death Arrow',SOURCE),
1419:('Hung on Death',DAWN),
1421:('Grey Sword',SOURCE),
1424:('Invincible Sword',DAWN),
1425:('Empress Haze',DAWN),
}

ITEMS={
3909:'Gram',3910:'Death Lure',3929:'LS Sword',
3979:'JST Scarf',3980:'Eba Helmet',3981:'Armage Helm',
3982:'A-Wise Robe',3993:'Dondoko Headband',
4009:'GAKU-RAN',4014:'Purge Shine',
4018:'Scale',4019:'Belt Machine',4020:'Running Machine',
4021:'Crystal Ball',4022:'Tarot Cards',4023:'Pyramid',
4024:'Sandbag',4025:'Training Log',4026:'Giant Rock',4027:'Punching Machine',
}

# These indices are a separate formal/field name list. The species stem has
# already been reviewed; form/color qualifiers are literal game-only labels.
NAMES={
1025:'Pickmon (Sunglasses)',1028:'Bombmon',1031:'Shoutmon X4B',
1034:'Shoutmon (Black)',1035:'Greymon (Orange)',
1036:'SkullKnightmon (Black/Red)',1041:'Shoutmon X3GM',
1042:'Shoutmon X3SD',1043:'Shoutmon X4S',
1044:'GreyKnightsmon',1046:'Shoutmon X5S',
}

def wrap_story(value):
    out=[]
    for line in value.split('\n'):
        out.extend(textwrap.wrap(line,15,break_long_words=False,
                                 break_on_hyphens=False) or [''])
    if any(len(line)>15 for line in out):raise ValueError(value)
    return '\n'.join(out)

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    previously=translate_records(records)
    target=ROOT/'translations/batch14.json'
    frozen=ROOT/'translations/review_batch14.json'
    current_keys=set()
    if target.exists():
        for block in json.loads(target.read_text(encoding='utf-8'))['blocks']:
            current_keys.update(f"{block['archive']}:{block['entry']:03d}:{n:05d}"
                                for n in range(block['start'],block['start']+len(block['english'])))
    if frozen.exists():
        review=json.loads(frozen.read_text(encoding='utf-8'))
    else:
        queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
        byid={key:row for row in queue for key in row['ids'].split(';')}
        review=[]
        def add(key,english,evidence=SOURCE,note='Translated from original Japanese.'):
            if key not in byid:raise ValueError(f'Missing untranslated key: {key}')
            row=byid[key]
            review.append({'category':row['category'],'japanese':row['japanese'],
                           'ids':row['ids'].split(';'),'english':english,
                           'evidence':evidence,'review_note':note})
        for n,en in QUEST.items():
            add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,CARD,
                'Quest text from Japanese; Western species names checked in official English card list where available.')
        for n,en in FARM.items():
            add(f'MSG/MESPAK05.PAK:000:{n:05d}',wrap_story(en),SOURCE,
                'DigiFarm report in fixed 15-column text cells.')
        for (entry,n),en in STORY.items():
            add(f'MSG/MESPAK02.PAK:{entry}:{n:05d}',wrap_story(en),SOURCE,
                'Story or NPC dialogue in fixed 15-column text cells.')
        for n,(en,evidence) in MOVES.items():
            add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,
                'Exact matching name appears in English Dawn/Dusk data; Japanese meaning cross-checked.'
                if evidence==DAWN else
                'Official English card names this Japanese technique Pollen Spray.'
                if evidence==CARD else
                'Working translation from Japanese; exact Western match unverified.')
        for n,en in ITEMS.items():
            add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,CARD if n==4014 else SOURCE,
                'Purge Shine matches Bandai English card title.' if n==4014 else
                'Equipment or farm item working translation from Japanese.')
        for n,en in NAMES.items():
            add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,CARD,
                'Western species stem follows Bandai English names; game-only variant qualifier retained literally.')
        frozen.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    blocks=[];seen=set()
    for item in review:
        for key in item['ids']:
            if key in seen or (key in previously and key not in current_keys):raise ValueError(f'Duplicate {key}')
            seen.add(key)
            r=records[key]
            if r['source']!=item['japanese']:raise ValueError(f'Source changed {key}')
            blocks.append({'archive':r['archive'],'entry':r['entry'],'start':r['index'],
                           'category':item['category'],'english':[item['english']],
                           'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    target.write_text(json.dumps({'description':'Reviewed quests, NPC dialogue, DigiFarm, moves, items and formal names.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} slots from {len(review)} Japanese source groups')

if __name__=='__main__':main()
