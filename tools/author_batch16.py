"""Freeze another reviewed text batch using exact IDs from the untranslated queue."""
import csv, json, textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SOURCE='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
WIKIMON='https://wikimon.net/Slash_Angemon_%28Xros_Wars%29'
GAMEFAQS='https://gamefaqs.gamespot.com/ds/980253-digimon-story-lost-evolution/faqs/78408/glossary'

# Prefer exact Western names where a clear game/version match exists. The rest
# are working renderings from Japanese, explicitly marked for later review.
NAMES={}

QUEST={
235:'Investigate the cause\nin Digital Space East.',
237:'Copy Digimon\nOverload!!',
238:'Investigate the area\nwhere strange data\nactivity was detected.',
239:'Clear "A Look-Alike?\nThe Copy Digimon\nMystery."',
241:'Stop the data transfer\nin North Lost Space.',
243:'Avoid a Storage\nOverload!!',
244:'Stop whoever is\nreleasing abnormal\ndata.',
245:'Clear "Copy Digimon\nOverload!!"',
256:'Talk to Guilmon in\nthe Front Room.',
261:'Deliver it to Guilmon\nin the Front Room.',
265:'Talk to Giromon in\nEast Knuckle City.',
270:'Meet Mamemon in\nEast Crystal Mountain.',
272:'Report to Giromon in\nEast Knuckle City.',
273:'The Giro-Giro Gang!\nA Little Digimon\'s Pride',
275:'A Funky SuperStarmon\nis on the farm.',
276:'Clear "A Showdown!?\nThe Mame-Mame Gang."',
277:'Talk to Mamemon in\nEast Knuckle City.',
282:'Meet Giromon in\nEast Crystal Mountain.',
284:'Report to Mamemon in\nEast Knuckle City.',
285:'The Mame-Mame Gang!\nA Little Digimon\'s Pride',
}

FARM={
48:'A tree stump...?\nWhat am I supposed\nto do with this?',
49:'This is not much,\nbut it is decent\ntraining. My EXP\nwent up a bit!',
50:'Even if I keep\nbumping into this, it\nwill not be much of\na workout, will it?',
51:'Oh! Is this Tasty Sap?\nIt is called tasty, but\nwhat does it taste like?',
52:'Wow! It really is\nsweet and delicious!\nMy EXP went way up!',
53:'Ugh! This tastes\nawful! How is this\nconsidered tasty?!',
61:'Hmm... Is this a\nscale? I should\nweigh myself.',
62:'Just right! My max HP\nseems to have gone\nup a little!',
63:'Oh no! I am way\ntoo heavy... What a\nshock!',
64:'This is a treadmill.\nI could exercise even\nwhile lying down!',
65:'Whew! That was a\ngood workout. My max\nHP went up a fair bit.',
66:'I cannot stop shaking!\nWh-What do I do?!',
67:'Oh, a running machine!\nMaybe I should get\nsome exercise...',
68:'This is pretty nice!\nI feel refreshed, and\nmy max HP went up!',
69:'I am exhausted...\nI cannot move anymore!',
70:'Is this a crystal ball?\nIt is clear inside,\nand so pretty...',
71:'Whoa! I saw something!\nMy max MP went up a bit!',
72:'Nothing happened...\nThis is kind of boring.',
}

ITEMS={
4044:'Stonehenge',4045:'Mysterious Pot',4046:'Cursed Box',4047:'Dark Tower',4048:'Computer',
4049:'Solar Panel',4050:'Pinball Machine',4051:'Mini Shower',4052:'Mini Fishing Pond',
4053:'Waterfall',4054:'Birdhouse',4055:'High Jump Hurdle',4056:'Diving Board',
4057:'Climbing Tree',4058:'Tree Stump',4059:'Tasty Sap',4060:'Flower',4061:'Wild Berries',
4062:'Treehouse',4063:'Weapon Shed',4064:'Weapon House',4065:'Weapon Workshop',
4066:'Weapon Factory',4067:'Weapon Shrine',4068:'Armor Shed',4069:'Armor House',
}

MOVES={
1324:'Sovereign Sword',1339:'Overlord Twin Slash',1343:'Shiratorimaru',
1368:'Satori',1370:'Furious Shadow Dance',1374:'Strange Mist',
1414:'Giga Stick Lance',1430:'Aurora Undulation',1453:'Nail Crusher',
1455:'Shishiraozan',1460:'Dark Lightning',1477:'Ancient Seal',
1522:'Gaia Tornado',1590:'Kurumon\'s Prayer',1592:'Koyosetsu',
1593:'Holy Shot',1596:'Beast Fang Barrage',
}

STORY={
184:'Hey, little guy!\nAre you okay? What\nare you doing here?',
185:'Are you lost? I need\nto get you somewhere\nsafe...',
186:'I cannot believe this\nis happening now...',
187:'Hide over there for\na while. Someone\nscary might show up.',
188:'It is okay! I will\nget you somewhere\nsafe, I promise!',
189:'Thanks! You guys are\nnice! But I was told\nto wait here. Do not\ntouch the condenser\nsystem, okay? It is\npart of the game!',
190:'Come on... We do not\nhave time to play with\nyou right now...',
191:'The red one is 500\npoints, the blue one\nis 800... The boy with\ngoggles is worth\n10,000 points, right?',
192:'Wait a second...\nCould that be...?',
193:'Are you the new toys\nLord Barbamon told\nme about?',
194:'...No way.',
195:'I am Lalamon! I was\nsent to guard this\ncondenser tower...\nI am the lovely elite\nof Barbamon\'s Shadow\nGuard!',
196:'I was fooled! Taiki,\nwatch out!',
197:'All right! Let us go,\neveryone!',
198:'Well, I lost... I\nshould disappear now.\nI am too weak to\nprotect Lord Barbamon.',
199:'How was that, Lalamon?\nNow move aside!',
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
    frozen=ROOT/'translations/review_batch16.json'
    review=json.loads(frozen.read_text(encoding='utf-8')) if frozen.exists() else []
    seen={key for row in review for key in row['ids']}
    existing=set(seen)
    def add(key,english,evidence=SOURCE,note='Working translation from the Japanese source; exact Western localization not confirmed.'):
        if key in existing: return
        if key in seen: raise ValueError(f'Duplicate review ID: {key}')
        if key not in records: raise ValueError(f'Unknown ROM ID: {key}')
        src=records[key]
        category=src.get('category') or ('Story and dialogue' if 'MESPAK02' in key else 'Battle moves')
        review.append({'category':category,'japanese':src['source'],'ids':[key],
                       'english':english,'evidence':evidence,'review_note':note})
        seen.add(key)
    for n,(en,evidence,note) in NAMES.items(): add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,evidence,note)
    for n,en in QUEST.items(): add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,note='Quest title/objective; Western Digimon names and map regions follow the project glossary.')
    for n,en in FARM.items(): add(f'MSG/MESPAK05.PAK:001:{n:05d}',wrap_story(en),note='DigiFarm reaction dialogue; wrapped to the fixed 15-column story renderer.')
    # The facility names in ITEMS have already been translated in older batches;
    # farm reactions and quest strings below are drawn from the current queue.
    for n,en in MOVES.items(): add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,SOURCE,
        'Working English move rendering; no exact Western game name verified in this batch.')
    for n,en in STORY.items(): add(f'MSG/MESPAK02.PAK:008:{n:05d}',wrap_story(en),note='Lalamon and Taiki story scene; original character and Digimon names retained.')
    blocks=[]
    for item in review:
        for key in item['ids']:
            if key in prior and key not in existing: raise ValueError(f'Already translated: {key}')
            src=records[key]
            if src['source']!=item['japanese']: raise ValueError(f'Japanese source mismatch: {key}')
            blocks.append({'archive':src['archive'],'entry':src['entry'],'start':src['index'],'category':item['category'],
                           'english':[item['english']],'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],
                           'review_note':item['review_note']})
    frozen.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'translations/batch16.json').write_text(json.dumps({'description':'More quest objectives, DigiFarm dialogue and objects, battle moves, and researched Digimon names.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')

if __name__=='__main__': main()
