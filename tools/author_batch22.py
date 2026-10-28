"""Author batch 22: battle techniques, encounter dialogue, Digimon names and item labels."""
import csv,json,textwrap
from xros_text import ROOT,Rom,rom_paths
from build import collect_messages,translate_records
SRC='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
DRACOMON='https://world.digimoncard.com/cards/?card_no=BT20-007&search=true'
PHASCOMON='https://world.digimoncard.com/cards/index.php?category=522901&free=Store+Tournament+2025+Vol.+4&search=true'
MOVES={
1789:'Crash Symphony',1790:'Noisy Echo',1791:'Beautiful Song',1794:'Nightmare Shock',1795:'Scratch Beat',1797:'Nyoi Bone',1798:'Cone Thrust',1799:'Spread Nail',1800:'Darkside Quake',1801:'Demon Arm',
1804:'Drill Spin',1805:'Crusher Bone',1806:'Screw Claw',1807:'Mud Coat',1808:'Great Weight',1809:'Piece of Earth',1810:'Deadly Shade',1811:'Devil Bashing',1812:'Drill Shell',1813:'Guard Shelter',1814:'Hydro Pressure',1816:'Zero Freeze',1817:'Icy Shower',1819:'Dolphin Kick',1820:'Sharp Edge',1821:'Shadow Sickle',1822:'Sharp Claws',1824:'Insect Swarm',1825:'Thunder Ray',1826:'Thunderbolt',1827:'Thunder Bomber',1828:'Golem Punch',1829:'Crimson Curse',1830:'Heat Upper',1831:'Jet Gallop',1833:'Night Lancer',1834:'Gallop Hole',1835:'Fire Darts',1837:'Salamander Break',1838:'Love Serenade',1839:'Dark Spirits',1840:'Dark Musical',1841:'Tundra Breath',1842:'Tusk Strikes',1843:'Horn Howling',1844:'Fist Tone',1845:'Terror Plankton',1846:'Torpedo Attack'}
DAWN_MATCH={1804,1810,1833,1838,1842,1846}
STORY={
103:"We thought the volcano\nnear Earth Fort had\nerupted... Then a huge\nshadow raced toward us.\nJust as it was about to\nland, a crackling barrier\nsuddenly appeared around\nSky Fort.",
104:"That kept the shadow\nout... but trapped us\ninside too.",
105:"Then the barrier\nsuddenly vanished, and\nthe shadow came back!",
106:"That shadow... It had\nto be Barbamon!",
107:"Barbamon...? Is that\na Digimon?",
108:"A terrifying Digimon!\nThe ROG... everything...\nBarbamon was controlling\nit all!",
109:"...But that shadow\ndidn't seem to care about\nus at all, did it?",
110:"Is that true?",
111:"Yeah. It raced right\npast us.",
112:"...Right! It was\nheading toward\nSky Garden!",
113:"Sky Garden? There's\nnothing there except an\nold windmill, right?",
114:"...Yeah. I think that's\nall that's there.",
115:"We won't know until we\ngo! Let's head out,\nTaiki!",
117:"Then what should\nwe do?",
119:"Sounds good!",
120:"All right, I'll back\nyou up too!",
121:"Akari and the others\nsure look energetic!\nI guess I had nothing\nto worry about!",
122:"Yeah. I'm just glad\neveryone's safe. Now we\njust have to stop\nArmamon's revival!"}
ITEMS={
**{4372+i:f'Map {i+1:02d}' for i in range(27)},
4402:'Fort Key',4403:'Knuckle Coast East Key',4404:'Guruguru Amazon West Key',4405:'Guruguru Amazon East Key',4406:'Skull Glacier West Key',4407:'Skull Glacier East Key',4408:'Kumonos Ruins West Key',4409:'Kumonos Ruins East Key',4410:'Papyrus Desert North Key',4411:'Papyrus Desert South Key',4412:'Flower Plains Key',4413:'Tokona Key',4414:'Crystal Volcano East Key',4415:'Crystal Mine Key',4416:'Stealth Valley North Key',4417:'Lost Space North Key',4418:'Lost Space South Key',4419:'Digital Space North Key',
4500:'Phantom Beast Song',4501:'Beast Song',4502:'Angel Song',4503:'Demon Song',4504:'Aquatic Song',4505:'Machine Song',4506:'Bird Song',4507:'Insect Song',4508:'Plant Song'}
NAMES={4436:('Dracomon',DRACOMON),4437:('Phascomon',PHASCOMON)}

def wrap(s,width=15):
 out=[]
 for line in s.splitlines():out.extend(textwrap.wrap(line,width,break_long_words=False,break_on_hyphens=False) or [''])
 if any(len(x)>width for x in out):raise ValueError(s)
 return '\n'.join(out)
def main():
 records=collect_messages(Rom(rom_paths()['blue']));prior=translate_records(records)
 rows=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
 byid={k:r for r in rows for k in r['ids'].split(';')};blocks=[];review=[];seen=set()
 def add(key,en,evidence=SRC,note=''):
  if key not in byid:raise ValueError(f'Not in refreshed queue: {key}')
  row=byid[key];ids=row['ids'].split(';')
  if any(x in prior or x in seen for x in ids):raise ValueError(f'duplicate/already translated {ids}')
  if any(records[x]['source']!=row['japanese'] for x in ids):raise ValueError(f'source mismatch {ids}')
  if not note:note='Provisional English rendering; exact western game localization was not verified.'
  seen.update(ids);review.append({'category':row['category'],'japanese':row['japanese'],'ids':ids,'english':en,'evidence':evidence,'review_note':note})
  for x in ids:
   z=records[x];blocks.append({'archive':z['archive'],'entry':z['entry'],'start':z['index'],'category':row['category'],'english':[en],'sources':[evidence] if evidence.startswith('https://') else [],'review_note':note})
 for idx,en in MOVES.items():
  key=f'MSG/MESPAK00.PAK:000:{idx:05d}'
  source=DAWN if idx in DAWN_MATCH else SRC
  note='Cross-checked against the English Digimon World: Dawn/Dusk move-name list; exact attack mapping still needs game-context review.' if idx in DAWN_MATCH else 'Working English move name from the Japanese technique; no exact Western-game match verified.'
  add(key,en,source,note)
 for idx,en in ITEMS.items():
  key=f'MSG/MESPAK00.PAK:000:{idx:05d}'
  add(key,en,SRC,'Direct item/map/key label translation; place names follow the established project location glossary.')
 for idx,(en,source) in NAMES.items():
  add(f'MSG/MESPAK00.PAK:000:{idx:05d}',en,source,'Official Digimon Card Game card list confirms the English species spelling.')
 for idx,en in STORY.items():
  add(f'MSG/MESPAK02.PAK:010:{idx:05d}',wrap(en),SRC,'Sky Fort story scene; wrapped to the fixed 15-column dialogue renderer.')
 (ROOT/'translations/batch22.json').write_text(json.dumps({'description':'Battle techniques, Sky Fort story dialogue, remaining Dracomon/Phascomon names and item/map/key labels. Moves that lack an exact western-game match are marked provisional.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'translations/review_batch22.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(blocks)} slots from {len(review)} reviewed Japanese groups')
if __name__=='__main__':main()

