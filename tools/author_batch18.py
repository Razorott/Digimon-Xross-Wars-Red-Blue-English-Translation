"""Author batch 18 from exact source IDs in the current untranslated queue."""
import csv, json, textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records
SRC='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
WORLD2_OCTOMON='https://dev.metalkid.info/DigimonWorld2/Digipedia/Details/Octomon'
MOVES={
 1498:('Thousand Arrows',SRC),1500:('Tera Hydro Breath',SRC),1513:('Storm Gazer',SRC),1514:('Atomic Blaster',SRC),1516:('Ashipatravana',SRC),1517:('Shippu Tensho Ken',SRC),
 1599:('Baby Flame',SRC),1600:('Veemon Head',SRC),1606:('Vee Breath Arrow',SRC),1607:('Mega Flame',SRC),1608:('Water Breath',SRC),1609:('Twin Neptune',SRC),1611:('Twin Dragon Wave',SRC),1612:('Spurting Ink',WORLD2_OCTOMON),
 1613:('DJ Shooter',DAWN),1614:('Harpoon Torpedo',DAWN),1617:('Flower Bomb',SRC),1618:('Goburi Strike',DAWN),1619:('Tiny Twister',DAWN),1620:('Strong Mole',SRC),1621:('Destroyed Voice',SRC),1622:('Ambush Crunch',SRC),1624:('Mega Burst',SRC),1628:('Freeze Fang',DAWN),1629:('Shishiomaru',DAWN),1630:('Glare Eye',DAWN),1631:('Crazy Giggle',DAWN),1634:('Pico Darts',SRC),1636:('Thunder Cloud',SRC),1639:('Fire Blast',DAWN),1641:('Petit Thunder',SRC),1642:('Poison Ivy',DAWN),1643:('Ice Archery',SRC),1644:('Iga Ninja Art',SRC),1645:('Spiking Finish',SRC),1647:('Branch Drain',DAWN),1648:('Sunshine Beam',DAWN),1649:('Prickly Bang-Bang',SRC),1652:('Scissor Arms',SRC),1653:('Sticky Net',SRC),1655:('Crimson Nail',SRC),1657:('Kunai Feather',SRC),1660:('Captain Cannon',SRC),1661:('ChronoBreaker',DAWN),1662:('Warning Laser',SRC),1663:('Air Shot',SRC),1664:('Lovely Impact',SRC),1666:('Feather Slash',SRC),1667:('Meteor Wing',SRC),1668:('Darkstrom',DAWN),1670:('Sonic Slash Rain',SRC),1672:('Rinkazan',DAWN),1673:('Crystal Revolution',SRC),1674:('Gorgon Eye',DAWN)}
QUEST={287:'Boltmon is on the farm\nwith the "Robot" group.',288:'Clear "Showdown?!\nThe Giro Giro Gang!"',290:'Talk to Gottsumon in\nthe Front Room.',292:'Advertise to Biyomon\nin West Kumonos Ruins.',293:'Advertise to Gabumon\nin West Kumonos Ruins.',294:'Advertise to Dracmon\nin East Kumonos Ruins.',296:'Get both signatures\nin South Papyrus Desert.',297:'Give them to Gottsumon\nin the Front Room.',298:'Super Idols?!\nNumemon & Sukamon',299:'Get autographs from\nthe top idol duo,\nNumesuka!',300:'BlueMeramon is in\nthe Expedition Team.',302:'Talk to Cherubimon\n(Virtue) in the\nFront Room.',304:'Find Angewomon on\nthe east Knuckle Coast.',306:'Give it to Cherubimon\n(Virtue) in the\nFront Room.',307:'Visitor from\nPhantom Palace',308:'Return Cherubimon\n(Virtue), who lost his\npass, to Phantom Palace.',309:'LadyDevimon is in\nthe party.',311:'Talk to MummyMon in\nthe Front Room.',312:'Talk to Shellmon on\nthe west Knuckle Coast.',313:'Talk to Gekomon on\nthe east Knuckle Coast.'}
FARM={27:'Whoa! Is this the\npower of darkness?!\nMy EXP went up, but\nthis feels creepy!',28:'This reeks of danger\nand traps. We should\nprobably leave it\nalone...',29:'Is that a Dark Tower?!\nWhat is it doing here?',30:'Whoa... What power!\nSo this is darkness...\nMy EXP went up, but\nI feel uneasy.',31:'Nothing happened...\nI feel disappointed\nand relieved at once.',32:'Hmm... What is this?\nIt smells so nice and\nmakes me feel good!',33:'I know this smell!\nIt is Taiki! I want to\nplay with him again.\nMy friendship went up!',34:'Heehee! I am so happy\ntoday. We can all live\npeacefully thanks to\nTaiki. I want to thank\nhim somehow!',35:'Taiki, thank you so\nmuch for everything!\nWe are all grateful.\nI hope you heard me!\nMy friendship went up!',37:'I found 100 Bits!\nI will send them to\nTaiki right away. He\nwill be so happy!',39:'Wow! 500 Bits!\nI will send them to\nTaiki. He will put them\nto good use!',41:'Amazing! 1,000 Bits!\nI will send them to\nTaiki. He always knows\nwhat to do with them!',43:'Wow! These wild\nberries are delicious!\nThey even boosted my\nEXP!',44:'These wild berries\ndo not taste very good.\nThey are not sweet at\nall. What a letdown...'}
STORY={177:'Are Weapon Digimon\nreally that powerful?',178:'Spadamon still has not\ngotten all his memories\nback... I hope we learn\nwhat Armamon is like\nand why it was sealed.',179:'And I hope he remembers\nDunasmon, too...',180:'Anyway! Our top\npriority is taking back\nthe Capacitor Towers!',181:"Barbamon's Shadow\nGuard must be strong.\nWe should check the\nDigiLab and DigiFarm\ninside the tent first!\nLet's go, you two!"}
ITEMS={4312:'Sunburn Guard',4313:'Wrapped Present',4314:'Bad Autograph',4315:'Terilop Goods',4316:'Numemon Photo',4317:'Sukamon Postcard',4318:'Live Portrait',4319:'Numesuka Double Autograph',4320:'Strawberry Hair Tie',4321:'Marimo Hair Tie',4322:'Silver Ingot',4323:'Giant Pearl',4324:'Heart Sapphire',4325:'Gold Crown',4326:'SP Shaver',4327:'MC Shaver',4328:'Spellbook',4329:'Diatrymon Feather',4330:'Bit-Like Thing',4331:'Bit-Looking Thing',4335:'Nice Meteorite',4336:'Voice Recorder',4337:'D-Voice Data',4338:'P-Voice Data',4339:'System Notebook',4340:'Signed CD',4341:'Terilop Statue',4342:'Neat Autograph'}
def wrap(value,limit=15):
 out=[]
 for line in value.splitlines(): out.extend(textwrap.wrap(line,limit,break_long_words=False,break_on_hyphens=False) or [''])
 if any(len(s)>limit for s in out): raise ValueError(value)
 return '\n'.join(out)
def main():
 records=collect_messages(Rom(rom_paths()['blue'])); prior=translate_records(records)
 old=ROOT/'translations/review_batch18.json'
 previous=json.loads(old.read_text(encoding='utf-8')) if old.exists() else []
 for item in previous:
  for key in item['ids']: prior.pop(key,None)
 queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),dialect='excel-tab'))
 byid={i:r for r in queue for i in r['ids'].split(';')}
 for item in previous:
  row={'category':item['category'],'japanese':item['japanese'],'ids':';'.join(item['ids'])}
  for key in item['ids']: byid.setdefault(key,row)
 review=[]; seen=set()
 def add(key,en,evidence=SRC,note='Working translation from Japanese; exact western localization not confirmed.'):
  if key in seen: raise ValueError(f'duplicate {key}')
  if key not in byid:
   if key in prior:return
   raise ValueError(f'not in queue {key}')
  row=byid[key]; ids=row['ids'].split(';')
  if any(i in prior for i in ids):raise ValueError(f'overwrite {ids}')
  if any(records[i]['source']!=row['japanese'] for i in ids):raise ValueError(f'source mismatch {ids}')
  review.append({'category':row['category'],'japanese':row['japanese'],'ids':ids,'english':en,'evidence':evidence,'review_note':note});seen.update(ids)
 for n,(en,ev) in MOVES.items():
  note=('Dawn/Dusk extraction spelling reused for the matching Japanese technique.' if ev==DAWN else 'Provisional English rendering from Japanese; no exact western-game match verified.')
  if n==1612: note='Exact English attack name used for Octomon in Digimon World 2.'
  if n==1614: note='Rendered as the familiar English attack name; Dawn/Dusk extraction has the cramped spelling HarpoonTrpedo.'
  add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,ev,note)
 for n,en in QUEST.items():add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,note='Quest requirement; original Western Digimon and place names retained.')
 for n,en in FARM.items():add(f'MSG/MESPAK05.PAK:001:{n:05d}',wrap(en),note='DigiFarm reaction; wrapped to 15 columns for the fixed-width story renderer.')
 for n,en in ITEMS.items():
  if f'MSG/MESPAK00.PAK:000:{n:05d}' not in seen:add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,note='Inventory/quest item label; concise rendering selected for the item-name field.')
 for n,en in STORY.items():add(f'MSG/MESPAK02.PAK:008:{n:05d}',wrap(en),note='Sky Fort story continuation; translated from Japanese source.')
 blocks=[]
 for item in review:
  for key in item['ids']:
   src=records[key];blocks.append({'archive':src['archive'],'entry':src['entry'],'start':src['index'],'category':item['category'],'english':[item['english']],'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],'review_note':item['review_note']})
 (ROOT/'translations/review_batch18.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'translations/batch18.json').write_text(json.dumps({'description':'Additional battle techniques, quest objectives, DigiFarm reports and Sky Fort story dialogue.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')
if __name__=='__main__':main()
