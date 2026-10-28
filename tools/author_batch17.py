"""Author batch 17 from exact untranslated source strings and reviewed mappings."""
import csv, json, textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
CARD_METAL='https://world.digimoncard.com/cards/?card_no=EX9-043&search=true'
CARD_MASTER='https://world.digimoncard.com/cards/?card_no=EX11-010&search=true'
CARD_SLASH='https://world.digimoncard.com/pdf/products_BT01-03_list1.pdf'

NAMES={
 376:('MetalTyrannomon',CARD_METAL,'Official English card name; the game abbreviation ME resolves to MetalTyrannomon.'),
 387:('BP Chessmon',SOURCE,'Game roster abbreviation retained; an exact official Western expansion was not verified.'),
 402:('MasterTyrannomon',CARD_MASTER,'Official English card name; the game abbreviation MT resolves to MasterTyrannomon.'),
 449:('SlashAngemon',CARD_SLASH,'Standard English card spelling. The Xros Wars English dub used SlushAngemon; this project uses the canonical franchise spelling.'),
 531:('EX Eraser Omega',SOURCE,'Game-specific form; translated from the Japanese roster label.'),
 533:('Omega Armamon BM',SOURCE,'Compact roster label for this game-specific form; full name appears in the formal-name field.'),
 534:('Flowerbed Boss',SOURCE,'Context identifies a named boss Digimon; concise roster wording.'),
 582:('System Omega',SOURCE,'Game system name; Omega retained as the named system.'),
 606:('Signboard Monitamon',SOURCE,'Roster label for the signboard Monitamon.'),
 650:('Formal Name Placeholder',SOURCE,'Placeholder label from the roster data.'),
 651:('????????????',SOURCE,'The source name is intentionally hidden in the game data.'),
 1006:('Omega Armamon: Burst Mode',SOURCE,'Expanded game-specific form name; preserves Omega from the original game name.'),
 4070:('Armor Workshop',SOURCE,'DigiFarm facility name.'),
 4071:('Armor Factory',SOURCE,'DigiFarm facility name.'),
 4072:('Armor Shrine',SOURCE,'DigiFarm facility name.'),
 4073:('Friendship Up 1',SOURCE,'DigiFarm achievement label.'),
 4074:('Friendship Up 2',SOURCE,'DigiFarm achievement label.'),
 4075:('Found 100 Bit',SOURCE,'DigiFarm achievement label.'),
 4076:('Found 500 Bit',SOURCE,'DigiFarm achievement label.'),
 4077:('Found 1,000 Bit',SOURCE,'DigiFarm achievement label.'),
}

QUEST={
 201:'Talk to Megadramon in\nWest Knuckle City.',
 204:'Report to Megadramon\nin West Knuckle City.',
 205:'The Rumor About\nHL Angemon',
 206:'Find and punish the\nculprit spreading bad\nrumors about\nHL Angemon.',
 207:'A Wild HL Angemon\nis on the farm.',
 209:'Inspect the stone\ntablet in the\nKumonos Underground\nPassage.',
 211:'Search for the\nAncient Stone Tablet!',
 212:'Investigate the\nsuspicious stone\ntablet.',
 215:'Inspect the stone\ntablet in Papyrus Cave.',
 216:'Inspect the stone\ntablet beneath\nCrystal Mountain.',
 218:'The Mystery of the\nAncient Tablets!',
 219:'Investigate the\ndangerous stone tablet.',
 220:'Clear "Search for the\nAncient Stone Tablet!"',
 222:'Inspect the stone\ntablet in Stealth Cave.',
 224:'Protect the seal on\nthe ancient tablet!',
 225:'Investigate the\nsuspicious, dangerous\nstone tablet.',
 226:'Clear at least seven\nRequest Quests.',
 229:'Find Parrotmon in\nEast Digital Space.',
 231:'Look-Alike?\nThe Copy Digimon\nMystery',
 232:'Investigate the\nParrotmon acting\nstrangely.',
}

FARM={
 15:'Whoa, that startled\nme! That sounds nice.\nIt was so soothing,\nmy EXP went up!',
 16:'Is this thing broken?\nIt will not make a\nsound at all...',
 17:'I know this! It is a\nHoly Bell! Let me\ngive it a ring...',
 18:'That sounds great!\nSo soothing. My EXP\nwent up a little, too!',
 19:'It will not ring. Is it\nbroken, or can only\npure hearts ring it?',
 20:'Is this Stonehenge?\nAm I supposed to walk\nthrough it?',
 21:'Whoa! What was that?\nI feel strong! My EXP\nwent way up!',
 22:'Nothing happened.\nGuess it only looks\nimpressive.',
 23:'What is this? Some\nkind of strange pot...',
 24:'Ugh! A Dark Potion!\nMy EXP went up, but\nit reeks!',
 25:'Phew! Something\nsmells awful! I am\ngetting out of here!',
 26:'Is this a cursed box?\nI am curious... I\nshould check it out!',
}

ITEMS={
 3829:'MA Angemon',3831:'HL Angemon',
 3876:'Koyojo',3877:'Momiji Oroshi',3879:'Pao Fu',3880:'Pao Tzu',
 3881:'Pao Chen',3882:'Treasure Mallet',3897:'Kikurin',3901:'Chououmaru',
 3905:'Sanaoria',3906:'Aztec',3907:'Ernstwell',3908:'Aussterben',
 4044:'Stonehenge',4045:'Suspicious Pot',4046:'Cursed Box',4047:'Dark Tower',
 4048:'Computer',4049:'Solar Panel',4050:'Pinball Machine',4051:'Mini Shower',
 4052:'Mini Fishing Pond',4053:'Waterfall',4054:'Birdhouse',4055:'High Jump Bar',
 4056:'Diving Board',4057:'Tree Climb',4058:'Tree Stump',4059:'Tasty Sap',
 4060:'Flower',4061:'Wild Berries',4062:'Treehouse',4063:'Weapon Shed',
 4064:'Weapon House',4065:'Weapon Workshop',4066:'Weapon Factory',
 4067:'Weapon Shrine',4068:'Armor Shed',4069:'Armor House',
}

# Exact spellings from the English Dawn/Dusk move-list extraction are cited
# only where the Japanese technique name matches; all other lines are marked
# provisional, with descriptive translations rather than claimed localizations.
MOVES={
 1452:('Execution by Beheading',SOURCE),
 1489:('Thunderclap',SOURCE),
 1494:('Radiant Flame',SOURCE),
 1496:('Infinity',SOURCE),
 1542:('Mikafutsu-no-Kami',SOURCE),
 1748:('Bonhitsu Sen',SOURCE),
 1751:('Dragon Impulse',SOURCE),
 1758:('Flash of Radiance',SOURCE),
 1796:('Wrath',SOURCE),
 1414:('Gigastick L',DAWN),
 1430:('AuroraAngelR',DAWN),
 1453:('Nail Crusher',SOURCE),
 1477:('Kofusatsu',SOURCE),
 1522:('Gaia Tornado',SOURCE),
 1590:('KurumonPrayer',DAWN),
 1593:('Holy Shoot',DAWN),
 1596:('Beast Fang Frenzy',SOURCE),
}

STORY={
 142:'This was not all\nTaiki\'s fault... I\ncould not do a thing,\neither. Barbamon\ndid not finish us off\non purpose! He thinks\nhe can toy with us!',
 143:'We need to contact\nPatamon, quickly...\nBarbamon may be\nheading for Sky Fort.',
 144:'There you are!\nEveryone, it is awful!',
 146:'We are not safe at\nall! ROG invaded the\ncity, forced everyone\nout, and took over the\ntower. Sky Fort is\nsurrounded by a field\nof lightning. We cannot\nget near it!',
 147:'What?! Zenjiro, Akari,\nand everyone else are\nat Sky Fort!',
 148:'That electric field...\nCould it be the\nProtective Field? It is\na powerful barrier\nthat guards Sky Fort.',
 149:'Then we are fine!\nPatamon must have\nactivated the barrier,\nright?',
 150:'The Protective Field\nonly activates when\nevery Capacitor Tower\nis in Emergency Mode.\nIf they captured the\ntowers, that means...',
 151:'Barbamon captured\nSky Fort!',
 171:'Good. We will wait\nhere, then. Call us\nwhenever you need us.',
 172:'Taiki, Shoutmon, can\nyou hear me? I have\na way to get back to\nSky Fort...',
 173:'You know how?',
 174:'The Protective Field\nappears when every\nCapacitor Tower enters\nEmergency Mode. Return\nevery tower to Normal\nMode, and you should\nbe able to reach Sky Fort!',
 175:'So we need to visit\nthe towers we activated...',
 176:'If Barbamon frees\nArmamon, his real goal,\nthis Zone... no, the\nwhole Digital World\ncould fall under his\ncontrol. Even your\nworld may be in danger.',
}

def wrap_story(value):
    out=[]
    for line in value.split('\n'):
        out.extend(textwrap.wrap(line,15,break_long_words=False,break_on_hyphens=False) or [''])
    if any(len(line)>15 for line in out): raise ValueError(value)
    return '\n'.join(out)

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    prior=translate_records(records)
    queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
    byid={key:row for row in queue for key in row['ids'].split(';')}
    review=[]; seen=set()
    def add(key,english,evidence=SOURCE,note='Working translation from Japanese; exact Western localization not confirmed.'):
        if key in seen: raise ValueError(f'Duplicate translation ID: {key}')
        if key not in byid:
            if key in prior: return
            raise ValueError(f'Not in current untranslated queue: {key}')
        row=byid[key]; ids=row['ids'].split(';')
        if any(i in prior for i in ids): raise ValueError(f'Would overwrite a prior translation: {ids}')
        if any(records[i]['source']!=row['japanese'] for i in ids): raise ValueError(f'Source mismatch: {ids}')
        review.append({'category':row['category'],'japanese':row['japanese'],'ids':ids,'english':english,
                       'evidence':evidence,'review_note':note})
        seen.update(ids)
    for n,(en,evidence,note) in NAMES.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,note)
    for n,en in QUEST.items():
        add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,note='Quest title or objective; Digimon and place names use project spellings.')
    for n,en in FARM.items():
        add(f'MSG/MESPAK05.PAK:001:{n:05d}',wrap_story(en),note='DigiFarm reaction dialogue; wrapped to the fixed 15-column text renderer.')
    for n,en in ITEMS.items():
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,note='Equipment, farm object, or facility label. Concise form selected for the item row.')
    for n,(en,evidence) in MOVES.items():
        note='Exact English Dawn/Dusk extraction name reused for the matching Japanese technique.' if evidence==DAWN else 'Provisional English rendering from the Japanese; no exact western game match verified.'
        add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,note)
    for n,en in STORY.items():
        add(f'MSG/MESPAK02.PAK:008:{n:05d}',wrap_story(en),note='Sky Fort story scene; original character and Digimon names retained.')
    blocks=[]
    for item in review:
        for key in item['ids']:
            src=records[key]
            blocks.append({'archive':src['archive'],'entry':src['entry'],'start':src['index'],
                           'category':item['category'],'english':[item['english']],
                           'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    (ROOT/'translations/review_batch17.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'translations/batch17.json').write_text(json.dumps({'description':'Sky Fort story and NPC dialogue, quest objectives, DigiFarm reports, Digimon names, battle techniques, and farm equipment labels.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed source groups')

if __name__=='__main__': main()
