"""Author batch 19 from the current queue and reviewed Digimon references."""
import csv,json,textwrap
from xros_text import ROOT,Rom,rom_paths
from build import collect_messages,translate_records
SRC='Original Japanese ROM (local primary source)'
DAWN='https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
PURGE='https://world.digimoncard.com/rule/pdf/general_rules.pdf?210507='
QUO='https://digimon-story.mtwildwood.net/cs/skills/quo-vadis/'
MOVES={1681:('Full Heal',SRC),1686:('All-Purpose Disk',SRC),1687:('Little Horn',DAWN),1688:('Heat Bubble',SRC),1689:('Bite',SRC),1690:('Scissor Arms Mini',SRC),1691:('Nume Rain',SRC),1692:('Free-Throw Bomb',SRC),1693:('Demonic Gale',SRC),1694:('Power Fang',SRC),1697:('Quo Vadis',QUO),1698:('Black Rain',SRC),1702:('Yakusa no Ikazuchi',SRC),1703:('Purge Shine',PURGE),1704:('Final Shining Burst',SRC),1705:('Final Mirage Burst',SRC),1707:('Agishan Levre',SRC),1708:('Dark Prominence',SRC),1709:('Esgrima',SRC),1710:('Irritant Buzz',SRC),1712:('Dead or Alive',SRC),1713:('Nigimitama',SRC),1714:('Booster Claw',SRC),1715:('Dimension Destroyer',SRC),1716:('Chronos Crop',SRC)}
QUEST={314:'Talk to Evilmon in\nnorthern Stealth Valley.',315:'Report to MummyMon\nin the Front Room.',316:'The Scattered\nPharaohmon Army',317:'Reunite the Pharaohmon\narmy that disbanded\nafter losing its leader.',318:'Scorpiomon is in the\nExpedition Team.',320:'Talk to Alphamon in\nthe Front Room.',321:'Defeat the eastern\npirates in Tokona Sea.',322:'Defeat the southern\npirates in Tokona Sea.',323:'Defeat the western\npirates on Tokona Coast.',324:'Defeat the northern\npirates on Tokona Coast.',325:'Report to Alphamon\nin the Front Room.',326:'Rulers of the Sea?!\nThe Pirates',327:'Defeat the four pirate\ngangs raiding Tokona Sea.',329:'Talk to Goddramon in\nthe Front Room.',330:'Find the visitor in\nFlower Prairie.',331:'Find and deliver a\npassionate red flower.',332:'Find and deliver a\nsensual purple flower.',333:'Report to Goddramon\nin the Front Room.',334:'The Young Prince of\nthe Golden Kingdom',335:'Entertain a super VIP\nwith a fussy nature.',337:'Talk to VenomMyotismon\nin the Front Room.',338:'Find a vocalist in\nStealth Valley!',339:'Find a drummer in\nStealth Valley!',340:'Find a guitarist in\nStealth Valley!',341:'Report to VenomMyotismon\nin the Front Room.',342:'Visual-Kei Band?!\nLet\'s Start a Band!',343:'Find members for the\nVisual-Kei band.'}
FARM={73:'Hey, there is\nsomething here...\nWait, I know! It is a\ntarot card, right?',74:'Whoa! Magic is flowing\ninto me! My maximum\nMP went up a little!',75:'Huh? Nothing happened.\nHow boring...',76:'That is a pyramid!\nI will take a little rest\ninside.',77:'That strange power\nfeels refreshing! My\nmaximum MP went way up!',78:'I got lost in there...\nI cannot walk anymore!',79:'Is that a punching bag?\nI will practice my\nattacks on it!',80:'I feel stronger again!\nMy strength went up!',81:'Ow, that hurts! I am\ndone for today!',82:'This is a training log.\nI should run into it!',83:'How did I do? Pretty\ngood, right? My strength\nwent up a little!',84:'I am getting tired.\nThat is enough for today!'}
ITEMS={4343:'Fire Crown',4344:'Snow Crown',4345:'Saint Crown',4346:'Dark Crown',4347:'Mysterious Bone',4348:'Ultimate DigiNoir',4349:'Development Memory',4350:'DigiNoir',4351:'Unknown Score',4352:'Unknown Data',4353:'Scarlet Rose',4354:'Soft Iris',4358:'Gentle Medal',4359:'Bravo Medal',4360:'Legend Medal'}
STORY={185:'There were six towers...\nBut seven systems.\nSpadamon was right\nabout his memories.',186:'But who is managing\nthat system? Someone\nmust be there if they\ncontacted us...',187:'How did they hide it\nfrom ROG all this time?\nIt is not on the map.\nOnly a very clever\nDigimon could rewrite\nthe Zone data like that.',188:'Maybe it is one of\nBarbamon\'s traps.',189:'The voice from the\nsystem sounded so calm\nand strong... I felt\nnervous even though\nI was not being scolded.',190:'They also said Taiki\nand the others should\ncome with us...',191:'They know who we are?',192:'I mapped the port to\nStealth Valley. We can\ntravel there anytime.\nGet ready before you go!',193:'Hey, Spadamon...\nWasn\'t Dunasmon the\none managing the\nCapacitor System?',194:'Dunasmon was a warrior\nwho protected the Zone\nwith the Weapon Digimon.\nIs he calling us? Why\nhide in Stealth Valley\ninstead of guarding it?',195:'There must be a reason.\nLet\'s hurry to Stealth\nValley!'}
def wrap(s,n=15):
 out=[]
 for line in s.splitlines():out.extend(textwrap.wrap(line,n,break_long_words=False,break_on_hyphens=False) or [''])
 if any(len(x)>n for x in out):raise ValueError(s)
 return '\n'.join(out)
def main():
 records=collect_messages(Rom(rom_paths()['blue']));prior=translate_records(records)
 queue=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),dialect='excel-tab'))
 byid={i:r for r in queue for i in r['ids'].split(';')};review=[];seen=set()
 def add(k,en,ev=SRC,note='Working translation from Japanese; exact English game wording not verified.'):
  if k not in byid:raise ValueError(f'Not in current untranslated queue: {k}')
  r=byid[k];ids=r['ids'].split(';')
  if any(i in prior for i in ids):raise ValueError(f'Would overwrite: {ids}')
  if any(records[i]['source']!=r['japanese'] for i in ids):raise ValueError(f'Source mismatch: {ids}')
  if any(i in seen for i in ids):raise ValueError(f'Duplicate IDs: {ids}')
  review.append({'category':r['category'],'japanese':r['japanese'],'ids':ids,'english':en,'evidence':ev,'review_note':note});seen.update(ids)
 for n,(en,ev) in MOVES.items():
  note='Dawn/Dusk English move-list name reused for the matching technique.' if ev==DAWN else ('English Digimon Story: Cyber Sleuth skill name; community-index reference.' if ev==QUO else ('Bandai English Digimon card/rules name.' if ev==PURGE else 'Working English rendering from Japanese; exact Western game name not verified.'))
  add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,ev,note)
 for n,en in QUEST.items():add(f'MSG/MESPAK01.PAK:000:{n:05d}',en,note='Quest objective/title. Digimon names follow established English franchise spellings.')
 for n,en in FARM.items():add(f'MSG/MESPAK05.PAK:001:{n:05d}',wrap(en),note='DigiFarm reaction dialogue; wrapped for the fixed-width story renderer.')
 for n,en in ITEMS.items():add(f'MSG/MESPAK00.PAK:000:{n:05d}',en,note='Inventory item name; concise English form selected for the item row.')
 for n,en in STORY.items():add(f'MSG/MESPAK02.PAK:009:{n:05d}',wrap(en),note='Sky Fort story sequence; Japanese source translated with names preserved.')
 blocks=[]
 for item in review:
  for k in item['ids']:
   s=records[k];blocks.append({'archive':s['archive'],'entry':s['entry'],'start':s['index'],'category':item['category'],'english':[item['english']],'sources':[item['evidence']] if item['evidence'].startswith('https://') else [],'review_note':item['review_note']})
 (ROOT/'translations/review_batch19.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'translations/batch19.json').write_text(json.dumps({'description':'Sky Fort NPC dialogue, quest objectives, DigiFarm text, item names and battle techniques.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(blocks)} slots from {len(review)} reviewed source groups')
if __name__=='__main__':main()
