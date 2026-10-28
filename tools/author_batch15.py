"""Author the next frozen English text batch from exact ROM string IDs."""
import csv, json, textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'

# English Dawn/Dusk labels are used only for move names whose Japanese names
# identify the same technique. Other mappings are explicitly marked working.
MOVES={
1373:('FTemptation',DAWN), 1407:('Great Maelstrom',SOURCE),
1411:('BDeath Cloud',DAWN), 1431:('Purple Rain',DAWN),
1432:('Strike Fang',DAWN), 1434:('Trinity Arm',SOURCE),
1436:('VN Infuse',DAWN), 1438:('Crimson Flare',SOURCE),
1440:('Kaiser Phoenix',SOURCE), 1442:('GA Missile',DAWN),
1444:('Needle Squall',DAWN), 1446:('DM Scissors',DAWN),
1451:('G SeaDestroy',DAWN), 1454:('Tomahawk S',DAWN),
1456:('MjollnirHammer',DAWN), 1457:('Rose Rapier',DAWN),
1461:('Bifrost',DAWN), 1462:('UltimateStream',DAWN),
1464:('CatastropheC',DAWN), 1466:('Vortex P',DAWN),
1468:('Ulforce V Saber',SOURCE), 1473:('Midnight Raid',DAWN),
1478:('Lila Shower',DAWN), 1479:('Rapid Fire',DAWN),
1480:('Mach Stinger V',SOURCE), 1481:('Spiral Sword',SOURCE),
1486:("Pendragon's Glory",SOURCE), 1492:('TRI Revolver',DAWN),
1497:('Hades Call',SOURCE), 1504:('Erase Claw',DAWN),
1507:('BigBangTackle',DAWN), 1509:('Horn Buster',DAWN),
1512:('Met Lariat',DAWN), 1515:("S Arm'sOmega",DAWN),
1519:('Berserk Sword',DAWN), 1520:('Absolute Zero',DAWN),
1523:('Crystal Viro',SOURCE), 1524:('Mjollnir Thunder',SOURCE),
1525:('Hammer Spark',SOURCE), 1527:('Elder Sign',SOURCE),
1528:('Brachio Bubble',DAWN), 1530:('Dark Blast',DAWN),
1531:('Dual Sonic',SOURCE), 1532:('Shadow Wing',DAWN),
1534:('V Wing Blade',DAWN), 1535:('Epeios Gimmick',SOURCE),
1538:('DIGI of Soul',DAWN), 1539:('Sephirothic C',DAWN),
1543:('Calamity Thunder',SOURCE), 1544:('Atomic Bomber',SOURCE),
1546:('Gale Claw',DAWN), 1547:('Jumbo Crater',DAWN),
1549:('Karatakewari',SOURCE), 1550:('Swallow Double Return',SOURCE),
1551:("Sun's Dance",SOURCE), 1555:('ULTI Flare',DAWN),
1556:('Phantom Pain',DAWN), 1557:('Brave Metal',SOURCE),
1558:('Fuushikaden',SOURCE), 1559:('Iron Armor',SOURCE),
1560:('Illusion M',DAWN), 1561:("Devil's Kiss",DAWN),
1562:('Enigma',DAWN), 1563:('Purgatory Slash',SOURCE),
1564:('Pretty Attack',DAWN), 1565:('DesperadoBRT',DAWN),
1573:('Sorrow Blue',DAWN), 1578:('SV Fantasia',DAWN),
}

QUEST={
109:'Talk to Devimon in\nthe Front Room.',
111:'Report to Devimon in\nthe Front Room.',
113:'Take the bit to\nBE Vamdemon instead\nof Devimon.',
115:'Talk to Evilmon in\nthe Front Room.',
117:'Report to Evilmon in\nthe Front Room.',
119:'Take the bit to\nBE Vamdemon instead\nof Evilmon.',
181:'Report to Vamdemon\nin Papyrus City.',
184:'A DevDramon is in\nyour party.',
185:'Talk to Okuwamon in\nPapyrus City.',
190:'Report to Okuwamon\nin Papyrus City.',
193:'A Flymon is in\nyour party.',
197:'Report to Birdramon\nin West Knuckle City.',
198:"Flymon's Bad\nReputation",
199:'Find and stop the\nDigimon spreading\nrumors about Flymon.',
200:'A Wild Flymon is\non the farm.',
}

FARM={
0:'Whoa! What is this?\nThis is amazing!\nMy EXP is going\nthrough the roof!',
1:'Wah! I am getting\nshocked! Stop it!\nThat really hurts!',
2:'A pinball machine...\nMaybe I will give it\na try.',
3:'Yes! A perfect game!\nAnd my EXP shot up,\ntoo!',
4:'I cannot get the\nhang of this... Is\nthis even fun?',
5:'A little birdhouse.\nI wonder if there\nis a bird inside.',
6:'That bird is so cute!\nIt cheered me up.\nI think my EXP went\nup a little, too!',
7:'No bird, and it is\nsmelly, cramped,\ndusty, and full of\nspiderwebs... Ugh!',
8:'Is this a hurdle?\nI guess I should try\njumping over it!',
9:'All right! I cleared\nthe bar! My EXP went\nup, too!',
10:'Who cares if I can\njump over this?\nDigimon do not need\nto hurdle!',
11:'A diving board...\nI jump from here?',
12:'I did it! Success!\nMy EXP went up, too!',
13:'No way! That is\nterrifying!',
14:'Is this a phonograph?\nWhat do I do with it?',
}

ITEMS={
3988:'Caledfwlch',3989:'Ofanimon Plate',3996:"Baba's Hairpin",
4015:'A Beat Armor',4016:'Tiphereth',4017:'LS Shield',
4028:'Cannon',4029:'Iron Ball',4030:'Side-to-Side Hops',
4031:'Trampoline',4032:'Running Wheel',4033:'Bookshelf',
4034:'Study Desk',4035:'Magic Circle',4036:'Fire Lane',
4037:'Fire Ring',4038:'Ball Balancing',4039:'Tightrope',
4040:'Circus Tent',4041:'Phonograph',4042:'Holy Bell',
4043:'Stonehenge',
}

STORY={
('007',180):'Who are you?!',
('007',181):'...The Xros Heart\nGeneral... Taiki Kudo.',
('007',182):'In a way, you made\nit this far thanks\nto me. As a reward,\nI will show you my\ntrue form...',
('007',183):'That is Barbamon!?',
('007',184):'You know him, Nene?',
('007',185):'A terrible Digimon\nwho will do anything\nto reach his goal...\nSo that is it!',
('007',186):'What is wrong, Nene?',
('007',187):'So Barbamon\ncreated SkullKnightmon\nand D.Arcmon, and\ncontrolled Sparrowmon\nand me with illusions!',
('007',188):'Treasure is not just\nthings worth money,\nyou fool!',
('007',189):'Why are you yelling\nat me? He is the one\nwho went crazy over\nvaluables and made\na mess!',
('007',190):'Do not yell at us!\nTell him that!',
('007',191):'That was quite a\nshow... Watching you\nfight so hard to get\nyour friends back, I\nstruggled not to laugh.',
('007',192):'Cut it out, Barbamon!\nYou will not get your\nway! We will not\nbreak the seal here\nat Earth Fort!',
('007',193):'You misunderstand.\nEarth Fort is only a\ncontainer for ROG.\nThe true seal is in\nLost Space: the\nOmega Area, where\nthe legendary weapon\nDigimon are revived.\nThere, Armamon will\nbe reborn. I created\nROG to claim them both!',
('007',194):'Barbamon! What are\nyou planning? Why\ntell us all this?!',
('007',195):'Consider it a parting\ngift...',
('007',196):'Everyone, get back!\nIt is aiming at something!',
('007',197):'T-Taiki!?',
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
    prior=translate_records(records)
    queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    byid={key:row for row in queue for key in row['ids'].split(';')}
    frozen=ROOT/'translations/review_batch15.json'
    review=json.loads(frozen.read_text(encoding='utf-8')) if frozen.exists() else []
    seen={key for row in review for key in row['ids']}
    def add(key,english,evidence=SOURCE,note='Working translation from the original Japanese; English game-name match not confirmed.'):
        if key in seen: raise ValueError(f'Duplicate review ID: {key}')
        if key not in byid: raise ValueError(f'Not in untranslated queue: {key}')
        src=byid[key]
        review.append({'category':src['category'],'japanese':src['japanese'],
                       'ids':src['ids'].split(';'),'english':english,
                       'evidence':evidence,'review_note':note})
        seen.update(src['ids'].split(';'))
    for n,(en,evidence) in MOVES.items():
        move_note=('Exact English Dawn/Dusk move-list label selected for this technique.'
                   if evidence==DAWN else
                   'Working English technique name; no exact Western game match verified.')
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,move_note)
    for n,en in QUEST.items():
        add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,
            note='Quest objective; Digimon and place names retain the project glossary spelling.')
    for n,en in FARM.items():
        add(f'MSG/MESPAK05.PAK:001:{n:05d}',wrap_story(en),
            note='DigiFarm reaction dialogue in the game fixed-width text cells.')
    for n,en in ITEMS.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,
            note='DigiFarm facility or equipment label; concise English chosen to fit the item row.')
    for (entry,n),en in STORY.items():
        add(f'MSG/MESPAK02.PAK:{entry}:{n:05d}',wrap_story(en),
            note='Barbamon confrontation dialogue; original character and Digimon names retained.')
    # Queue and original ROM are the authority for every stable ID and Japanese source.
    blocks=[]
    for item in review:
        for key in item['ids']:
            if key in prior: raise ValueError(f'Already translated: {key}')
            src=records[key]
            if src['source']!=item['japanese']:raise ValueError(f'Japanese source mismatch: {key}')
            blocks.append({'archive':src['archive'],'entry':src['entry'],'start':src['index'],
                           'category':item['category'],'english':[item['english']],
                           'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    frozen.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'translations/batch15.json').write_text(json.dumps({
        'description':'Battle techniques, quest objectives, DigiFarm reactions, and the Barbamon confrontation.',
        'blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')

if __name__=='__main__':main()
