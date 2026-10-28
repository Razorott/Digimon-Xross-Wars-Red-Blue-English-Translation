"""Author batch 13 from exact Japanese source IDs with a frozen review file."""
import csv
import json
import textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
CARD = 'https://world.digimoncard.com/cards/'

# Map labels are the world map's location table, not dialogue.
MAP = {
1051:'Sky Fort',1056:'Crystal Mine',1057:'Crystal Volcano W',
1058:'Flower Plains',1059:'Crystal Volcano E',1060:'Knuckle Coast W',
1061:'Skull Glacier W',1062:'Tokona Coast',1063:'Guruguru Amazon W',
1064:'Knuckle Coast E',1065:'Skull Glacier E',1066:'Kumonos Ruins W',
1067:'Guruguru Amazon E',1068:'Kumonos Ruins E',1069:'Papyrus Desert N',
1070:'Papyrus Desert S',1091:'Crystal Cave',1092:'Stealth Canyon N',
1093:'Stealth Canyon S',1094:'Lost Space N',1095:'Lost Space S',
1096:'Digital Space N',1097:'Digital Space S',
}

QUEST = {
65:'Talk to Gabumon in\nthe Front Room.',
66:'Find Agumon at\nKnuckle Coast West.',
67:'Report to Gabumon\nin the Front Room.',
68:'Find Missing Agumon',
69:'Rescue Agumon, who\nhas not returned\nfrom exploring.',
83:'Talk to SnowAgumon\nin the Front Room.',
84:'Ask Wendigomon in\nDark Tunnel.',
85:'Report to SnowAgumon\nin the Front Room.',
86:'Scorching Summer Salon',
87:'Ask Wendigomon how\nto get a deep tan.',
89:'Talk to Wizardmon in\nE Knuckle City.',
90:'Find Wisemon in\nGuruguru Amazon W.',
91:'Report to Wizardmon\nin E Knuckle City.',
92:'Bully!? Defeat\nWisemon!',
93:'Defeat Wisemon, who\nkeeps troubling\nWizardmon.',
95:'Talk to Mushroomon\nin E Knuckle City.',
96:'Find Dinobeemon in\nGuruguru Amazon W.',
97:'Report to Mushroomon\nin E Knuckle City.',
98:'Bully!? Defeat\nDiatrymon!',
99:'Defeat Diatrymon,\nwho keeps bothering\nMushroomon.',
101:'Talk to Peckmon in\nthe Front Room.',
102:'Ask Kokatorimon in\nGuruguru Amazon W.',
103:'Ask Penguinmon at\nSkull Glacier West.',
104:'Ask DaiPenmon at\nSkull Glacier East.',
105:'Report to Peckmon\nin the Front Room.',
106:'Flightless Bird = Chicken?',
107:'Ask how a bird can\nfly freely through\nthe sky.',
}

FARM = {
61:"Perfect! Taiki\nwatched me! My\nfriendship went\nway up!",
62:"Oh, I missed it.\nThat's a shame.",
63:"Whoa! A ring of\nfire! Looks fun!\nLet me try!",
64:"Yahoo! Thrilling\nand exciting! My\nEXP went up, too!",
65:"Yow! It's hot!\nNo way I can do\nthis! My tail's\non fire!",
66:"Fire Road looks\nhot... You want me\nto cross that? Who\nthought this up?",
67:"Body and spirit\non fire! My EXP\nwent up!",
68:"No way! Whoever\nmade this should\ntry it first!",
69:"Fireworks? Huh.\nThat actually\nsounds fun!",
70:"Wow, beautiful!\nMy EXP went up,\ntoo! What a show!",
71:"Those fireworks\nnever lit or\nlaunched...",
72:"Whoa, a giant\nball! Should I\nstand on it?",
73:"This raised my\nEXP? Too easy!",
74:"It looks easy,\nbut it's pretty\ntough...",
75:"You want me to\nwalk that rope?\nSounds fun!",
76:"That was easier\nthan I thought!\nI had fun and\ngained EXP!",
77:"Scary, painful,\nand hard! I fell\noff, too. The\nworst!",
78:"A circus tent!?\nWhat am I meant\nto do in there?",
79:"My circus act\nraised my EXP!\nThe details are\na trade secret!",
80:"All that spinning\nand bending? No\nway! How would it\neven help a\nDigimon?",
}

# These are HQ and nearby NPC lines, including quest-monitor guidance.
NPC = {
('013',49):"I've gotten a\nlittle stronger!\nI'll protect Sky\nFort, Patamon,\nand everyone...\nif I can.",
('013',50):"Well said,\nSpadamon. You're\nno coward.",
('013',51):"...Thanks, Taiki.",
('013',52):"I see. With\nfriends beside\nyou, you've found\nyour courage.\nTaiki, train\nSpadamon well.\nWe Digimon who\nlive here will\nhelp however we\ncan.",
('013',53):"Look at those\nbusybodies. They\nplanned to help\nyou from the\nstart.",
('013',54):"Ask Gatomon over\nthere about\ncommunications.",
('013',55):"Ask BomberNanimon\nabout farm goods\nand upgrading\nFarm Islands.",
('013',56):"Penguinmon runs\nthe Item Shop.",
('013',57):"If you get a\nSummon Ticket,\ntalk to Clockmon.",
('013',58):"The nearest\nCapacitor Tower\nis at Knuckle\nCoast East. Try\nthere next. We're\nall counting on\nyou.",
('013',59):"I've always run\naway... It feels\nnice to have\npeople count on\nme. H-hey! Don't\nmake me say that!\nI'm going back\nin the Xros\nLoader!",
('017',197):"Taiki! Are you\nhearing everyone's\nrequests? Check the\nQuest Monitor!",
('018',6):"Hey... Everyone\naround here expects\na lot from us!",
('018',7):"They think we're\ngoing to save the\nworld. Maybe we\nshould do it!",
('018',8):"We're going to a\ntower... What was\nit called? Oh, a\nCapacitor Tower!",
('018',9):"Activate as many\nof the six towers\non the Energy\nContinent as you\ncan. Each one\nsends power back\nto Sky Fort.",
('018',10):"We still don't\nknow where\nChibickmon is.\nIf he were nearby,\nhe'd hear me call.",
('018',11):"Chibickmon is\nback! Everyone's\nrelieved, me too.\nThanks, brother!",
('018',12):"I don't get\nMinervamon. She\nsays she took\nChibickmon\nbecause he's cute.",
('018',13):"Hey, brother!\nYou heard\nSparrowmon call\nfor help? Then\nwe'll find him\nsoon enough!",
('018',14):"I heard Sparrowmon\nis stuck in the\nruins. How did\nthat happen?",
('018',15):"Sparrowmon came\nback safe, but\nhe says he can't\nremember a thing.\nWhat a mess...",
('018',16):"Not sure what to\ndo next, brother?\nWe'll work it out.\nDon't worry!",
('018',17):"That's a fine\nparty you have.\nAsk me anytime if\nyou'd like me to\njoin you.",
('018',18):"What lovely\ncompanions! If\nyou'd like me to\njoin you, just\nask. No rush.",
('018',19):"Nice party! Let\nme join you! Ask\nand I'll jump\nright in!",
}

# Only two exact Dawn/Dusk spellings below are claimed as licensed matches.
MOVES = {
1341:('Dark Claw',DAWN),1342:('Demon Claw',DAWN),
1345:('Death Slash',SOURCE),1346:('Poop Toss',SOURCE),
1349:('Light Bubble',SOURCE),1350:('Dark Bubble',SOURCE),
1351:('Thunder Needle',SOURCE),1352:('Blue Flame',SOURCE),
1353:('Comet Hammer',SOURCE),1354:('Shock Gatling',SOURCE),
1355:('Assassin Star',SOURCE),1356:('Blue Lightning',SOURCE),
1357:('Gain Attack',SOURCE),1358:('Giga Gain Attack',SOURCE),
1359:('Mega Gain Attack',SOURCE),1360:('Gain Guard',SOURCE),
1361:('Giga Gain Guard',SOURCE),1362:('Mega Gain Guard',SOURCE),
1363:('Command Input',SOURCE),1364:('Gain Speed',SOURCE),
1365:('Giga Gain Speed',SOURCE),1366:('Mega Gain Speed',SOURCE),
1367:('Dark Whisper',DAWN),1369:('Megalo Spark',SOURCE),
}

# A separate formal-name list follows the game's display-name table.
SPECIES = {
1026:'Monitamon',1029:'Beelzemon',1037:'MadLeomon',
1038:'Tactimon',1039:'Blastmon',1040:'Lilithmon',
1045:'Gaossmon',1047:'Troopmon',
}

EQUIPMENT = {
3911:'Grey Sword',3912:'Balmung',3913:'Blutgang',
3919:'Treasure Mania',3961:'Reppa Shield',3973:'Dinobee Mask',
3974:'Metal Head',4000:'Behemoth',
}

def wrap_story(s):
    lines=[]
    for part in s.split('\n'):
        lines += textwrap.wrap(part,15,break_long_words=False,break_on_hyphens=False) or ['']
    if any(len(x)>15 for x in lines):raise ValueError(s)
    return '\n'.join(lines)

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    current=ROOT/'translations/batch13.json'
    frozen=ROOT/'translations/review_batch13.json'
    current_keys=set()
    if current.exists():
        old=json.loads(current.read_text(encoding='utf-8'))
        for b in old['blocks']:
            current_keys.update(f"{b['archive']}:{b['entry']:03d}:{n:05d}" for n in range(b['start'],b['start']+len(b['english'])))
    if frozen.exists():
        review=json.loads(frozen.read_text(encoding='utf-8'))
        blocks=[];seen=set()
        for item in review:
            for ident in item['ids']:
                if ident in seen or (ident in translated and ident not in current_keys):
                    raise ValueError(f'Duplicate: {ident}')
                seen.add(ident)
                rec=records[ident]
                if rec['source']!=item['japanese']:raise ValueError(f'Source changed: {ident}')
                blocks.append({'archive':rec['archive'],'entry':rec['entry'],'start':rec['index'],
                               'category':item['category'],'english':[item['english']],
                               'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                               'review_note':item['review_note']})
        current.write_text(json.dumps({'description':'HQ NPCs, quest objectives, map labels, DigiFarm reports and battle moves.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'{len(blocks)} slots from {len(review)} frozen Japanese source groups')
        return
    queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    byid={key:row for row in queue for key in row['ids'].split(';')}
    review=[];blocks=[];seen=set()
    def add(key,english,evidence=SOURCE,note='Translated from the original Japanese ROM.'):
        if key not in byid:raise ValueError(f'Not in untranslated queue: {key}')
        row=byid[key]
        for ident in row['ids'].split(';'):
            if ident in seen or (ident in translated and ident not in current_keys):raise ValueError(f'Duplicate: {ident}')
            seen.add(ident)
            if records[ident]['source']!=row['japanese']:raise ValueError(f'Source changed: {ident}')
            rec=records[ident]
            blocks.append({'archive':rec['archive'],'entry':rec['entry'],'start':rec['index'],
                           'category':row['category'],'english':[english],
                           'sources':[evidence] if evidence.startswith('https://') else [],
                           'review_note':note})
        review.append({'category':row['category'],'japanese':row['japanese'],
                       'ids':row['ids'].split(';'),'english':english,
                       'evidence':evidence,'review_note':note})
    for n,en in MAP.items():add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,note='Map/area label; direction suffix is the original zone subdivision.')
    for n,en in QUEST.items():
        add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,
            CARD if n in (102,103,104) else SOURCE,
            'Quest log objective or title; Western species spelling checked in Bandai English card list.'
            if n in (102,103,104) else 'Quest log objective or title from original Japanese.')
    for n,en in FARM.items():add(f'MSG/MESPAK05.PAK:000:{n:05d}',wrap_story(en),note='DigiFarm event report; fixed 15-column dialogue cells.')
    for (entry,n),en in NPC.items():add(f'MSG/MESPAK02.PAK:{entry}:{n:05d}',wrap_story(en),note='HQ or nearby NPC dialogue; fixed 15-column story cells.')
    for n,(en,evidence) in MOVES.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,
            'Exact spelling in licensed English Dawn/Dusk move list.' if evidence==DAWN else 'Working translation of original Japanese; exact Western move match unverified.')
    for n,en in SPECIES.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,CARD,
            'Formal species label; Western spelling checked in Bandai English card list.')
    for n,en in EQUIPMENT.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,SOURCE,
            'Equipment name translated from the original Japanese; a licensed English item match is not established.')
    frozen.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    current.write_text(json.dumps({'description':'HQ NPCs, quest objectives, map labels, DigiFarm reports and battle moves.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} slots from {len(review)} Japanese source groups')

if __name__=='__main__':main()
