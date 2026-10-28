"""Author batch 20: verified battle move labels and Sky Fort story dialogue."""
import csv, json, textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SRC = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
SABER = 'https://digimon.net/reference_en/detail.php?directory_name=saberleomon'
GREAT_TORNADO = 'https://world.digimoncard.com/cards/?category=522001&search=true'
SPIRAL = 'https://world.digimoncard.com/rule/pdf/booster_battle_of_omni_BT05.pdf'
NUCLEAR_LASER = 'https://world.digimoncard.com/cards/?category=522001&search=true'

# All entries are the displayed technique names from MESPAK00. Western names
# are used where the game match is established; others retain a clear working
# English rendering and are marked provisional in the review sheet.
MOVES = {
 1717: ('Infinity Arrow', SABER),
 1720: ('Great Tornado', GREAT_TORNADO),
 1722: ('Positron Laser', SRC),
 1723: ('Royal Saber', SRC),
 1724: ('Smiley Warhead', SRC),
 1725: ('Holy Espada', SRC),
 1727: ('Burst Banchou Punch', SRC),
 1730: ('GeoGrey Sword', SRC),
 1731: ('Full Moon Blaster', SRC),
 1732: ('Megaton Hydro Laser', SRC),
 1734: ('Phoibos Blow', SRC),
 1736: ('Ernstwell', SRC),
 1737: ('Gear Stinger', SRC),
 1739: ("Avalon's Gate", SRC),
 1741: ("Heaven's Cure", SRC),
 1742: ('Sand Shower', SRC),
 1744: ('Flower Necklace', SRC),
 1745: ('Soul Banish', SRC),
 1746: ('Snake Bandage', SRC),
 1747: ('Golden Triangle', SRC),
 1750: ('Nuclear Laser', NUCLEAR_LASER),
 1752: ('Sacred Roar', SRC),
 1753: ('Plasma Shoot', SRC),
 1755: ('Maple-Leaf Grater', SRC),
 1762: ('Mega Sonic Voice', SRC),
 1763: ('Metal Arm', SRC),
 1765: ('Curse Breath', SRC),
 1766: ('Rajas', SRC),
 1767: ('Planet Hammer', SRC),
 1768: ('Bloody Whip', SRC),
 1769: ('Gale Kick', SRC),
 1770: ('Nature Heal', SRC),
 1771: ('Poison Mist', SRC),
 1772: ('Wrapping Bubble', SRC),
 1773: ('Lullaby Bubble', SRC),
 1774: ('Ice Comet', SRC),
 1775: ('White Hail', SRC),
 1776: ('Hard-Shell Crab', SRC),
 1778: ('Pawn Spear', SRC),
 1783: ('Twinkle Beam', SRC),
 1784: ('Gyro Break', SRC),
 1786: ('Sweet Breath', SRC),
 1787: ('Rapid Poop Toss', SRC),
 1788: ('Poop Paradise', SRC),
}

STORY = {
 'MSG/MESPAK02.PAK:008:00000': "You did exceptionally\nwell.\n\nYou were excellent bait\nto lure Spadamon and\nthe others to the\nCapacitor Towers and\nget them running...",
 'MSG/MESPAK02.PAK:008:00001': "Gah... My body...\nI can't move...",
 'MSG/MESPAK02.PAK:008:00002': "But you've learned too\nmuch.\n\nTo keep you from giving\nSpadamon and the others\nany more information,\nI'll make sure you can\nnever return to this Zone!\nWithout that information,\nSpadamon will be helpless!",
 'MSG/MESPAK02.PAK:008:00007': "Quit your whining,\nweak General.\n\nI only sent you to\nanother Zone. We'll meet\nagain someday... assuming\nyou survive the trip in\none piece.",
 'MSG/MESPAK02.PAK:008:00008': "Barbamon, I'll never\nforgive you...!",
 'MSG/MESPAK02.PAK:008:00009': "Hmm...\n\nThere's nothing left\nyou can do... and yet\nyou look so pitiful.\nI could watch a little\nlonger...",
 'MSG/MESPAK02.PAK:008:00010': "We won't lose...!\nWe can't lose...!",
 'MSG/MESPAK02.PAK:008:00011': "Tell the Weapon Digimon\nto run while they still\ncan!",
 'MSG/MESPAK02.PAK:008:00138': "Taiki! Are you all right,\nTaiki?!",
 'MSG/MESPAK02.PAK:008:00139': "...Shoutmon?\n... ... ...\nY-Yeah.\nI think I'm okay.",
 'MSG/MESPAK02.PAK:009:00039': "No way!",
 'MSG/MESPAK02.PAK:009:00158': "Garbage!",
 'MSG/MESPAK02.PAK:009:00178': "Thanks for taking back\nthe tower! You were all\namazing!",
 'MSG/MESPAK02.PAK:009:00179': "So the protection\naround Sky Fort is gone\nnow, right?!",
 'MSG/MESPAK02.PAK:009:00180': "It... it's still on!\n\nThere was another\nCapacitor System we\nhad to shut down!",
 'MSG/MESPAK02.PAK:009:00181': "What?!",
 'MSG/MESPAK02.PAK:009:00182': "I was surprised too!\nAs soon as Spadamon and\nthe others switched the\nsixth Capacitor Tower\nback to normal mode,\nthat system contacted\nEarth Fort out of nowhere!",
 'MSG/MESPAK02.PAK:009:00183': "What did it say?!",
 'MSG/MESPAK02.PAK:009:00184': "It only said, 'Come to\nStealth Valley.'",
 'MSG/MESPAK02.PAK:010:00086': "You're finally back!\nHey, listen to this!",
 'MSG/MESPAK02.PAK:010:00087': "What's going on? If you\nmean that protection\nthing, it'll disappear\nsoon. Don't worry!",
 'MSG/MESPAK02.PAK:010:00088': "That's okay. I trust\nyou completely!",
 'MSG/MESPAK02.PAK:010:00089': "Then why are you in\nsuch a hurry?",
 'MSG/MESPAK02.PAK:010:00090': "Listen! A Lost Space\nsuddenly appeared near\nSky Fort!!",
 'MSG/MESPAK02.PAK:010:00091': "W-What?!",
 'MSG/MESPAK02.PAK:010:00092': "The Airborne Digimon\nare ready to fly. Once\nyou're prepared, hurry\nback to Sky Fort!",
 'MSG/MESPAK02.PAK:010:00093': "W-What do we do, Taiki?!\nWhat should we do?!",
 'MSG/MESPAK02.PAK:010:00094': "I'm worried about Akari,\nZenjiro, and everyone!",
 'MSG/MESPAK02.PAK:010:00095': "Let's get back to\nSky Fort, quick!",
 'MSG/MESPAK02.PAK:010:00097': "I'll wait here, then.\n\nTell me whenever you\nwant to go somewhere!",
 'MSG/MESPAK02.PAK:010:00098': "Taiki! Welcome back!\n♪",
 'MSG/MESPAK02.PAK:010:00100': "Akari, Zenjiro...\nPatamon... I'm glad\nyou're all okay! Where's\neveryone else? Is anyone\nmissing?",
 'MSG/MESPAK02.PAK:010:00101': "We're okay. Somehow,\neveryone made it!",
 'MSG/MESPAK02.PAK:010:00102': "Things got rough after\nyou went to Crystal\nVolcano...",
}

def wrap(text, width=15):
    lines=[]
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width, break_long_words=False,
                                   break_on_hyphens=False) or [''])
    if any(len(line)>width for line in lines):
        raise ValueError(f'Line exceeds {width} columns: {text}')
    return '\n'.join(lines)

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    prior=translate_records(records)
    rows=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'), dialect='excel-tab'))
    byid={key:row for row in rows for key in row['ids'].split(';')}
    reviewed=[]; seen=set()
    def add(key, english, evidence=SRC, note='Working English rendering from Japanese; exact Western game wording not verified.'):
        if key not in byid: raise ValueError(f'Not in current queue: {key}')
        row=byid[key]; ids=row['ids'].split(';')
        if any(i in prior or i in seen for i in ids): raise ValueError(f'Already translated or repeated ID: {ids}')
        if any(records[i]['source'] != row['japanese'] for i in ids): raise ValueError(f'Source mismatch: {ids}')
        reviewed.append({'category':row['category'],'japanese':row['japanese'],'ids':ids,'english':english,'evidence':evidence,'review_note':note})
        seen.update(ids)
    for index,(english,evidence) in MOVES.items():
        if evidence == SABER:
            note='Official Digimon Web Encyclopedia names Infinity Arrow as SaberLeomon’s technique.'
        elif evidence == GREAT_TORNADO:
            note='Bandai English card list confirms Great Tornado. Other direct readings remain working names.'
        else:
            note='Provisional English rendering from the Japanese attack name; no exact western game match verified.'
        add(f'MSG/MESPAK00.PAK:000:{index:05d}',english,evidence,note)
    for key,english in STORY.items():
        add(key,wrap(english),note='Barbamon and Sky Fort story dialogue; wrapped to the fixed 15-column dialogue width.')
    blocks=[]
    for item in reviewed:
        for key in item['ids']:
            row=records[key]
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],'category':item['category'],'english':[item['english']],'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],'review_note':item['review_note']})
    (ROOT/'translations/review_batch20.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'translations/batch20.json').write_text(json.dumps({'description':'Battle techniques and Barbamon/Sky Fort story dialogue. Western technique names are sourced where verified; other attack names remain provisional.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} translated slots from {len(reviewed)} reviewed Japanese groups')

if __name__=='__main__': main()
