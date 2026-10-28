"""Author batch 21: DigiFarm reports and HQ/side-quest objectives."""
import csv,json,textwrap
from xros_text import ROOT,Rom,rom_paths
from build import collect_messages,translate_records
SRC='Original Japanese ROM (local primary source)'
FARM={
42:'Oh? Wild strawberries...',45:'This branch looks like it\'s\nasking me to climb it...',46:'I did it! I climbed\nthe tree! I got EXP\nfor reaching the top!',47:'The moment I climbed up,\nmy mood took a nosedive...\nWhat was the point of\nclimbing that tree?',
85:'Oh! There\'s a huge rock!\nI just have to push it\nand move it, right?',86:'That was easy!\nI feel much stronger now!',87:'It won\'t budge...\nMaybe this was impossible\nfrom the start.',88:'This looks like\na punching machine.',89:'Piece of cake!\nI feel a little tougher!',90:'W-Wait... Stop!\nI give up...!',91:'Oh, a training cannon!\nAll right, let\'s train!',92:'I held out to the end!\nI feel a bit tougher now!',93:'O-Ow! I hate\nthis training!',94:'That\'s a wrecking ball...\nI just have to catch it,\nright?',95:'That wasn\'t so bad.\nI feel much tougher now!',96:'N-No way!\nI can\'t do that!',97:'These are books, right?\nI hope there are some\nfun ones in here!',98:'There are lots of fun\nbooks! I feel a little\nsmarter now!',99:'Aw... They\'re all hard\nbooks. What a letdown!',
'2:0':'Is that a study desk?\nI hate studying, but\nI guess I\'ll try it.',
'2:1':'Hehe! I got a lot done.\nI feel a bit smarter now!',
'2:2':'Nope... I\'m getting\nsleepy...',
'2:3':'That\'s a magic circle,\nright? Is it for casting\na spell or something?',
'2:4':'My mind feels so clear!\nMaybe I\'m a genius now!',
'2:5':'Huh? Nothing happened.\nI guess it failed...',
'2:6':'Those are side-to-side\njumps, right? Let\'s try!',
'2:7':'That was easy!\nI feel a little faster!',
'2:8':'Huff, huff... I\'m tired.\nI\'m done!',
'2:9':'A trampoline! That\nlooks fun. I\'ll try it!',
'2:10':'Boing! That was fun!\nI feel a bit faster now!',
'2:11':'I\'m dizzy... I feel awful...',
'2:12':'That\'s a hamster wheel,\nright? I think I\'m\nsupposed to run inside.',
'2:13':'That was a great workout!\nI feel much faster now!',
'2:14':'Huff... I can\'t go on.\nI\'m ready to collapse...',
'2:15':'A Digimon keychain...\nI wonder if it\'s fun.\nI\'ll give it a try...',
}
QUEST={
345:'Talk to Piximon in\nthe Front Room.',347:'Report to Piximon\nin the Front Room.',350:'Have a selfish\nMermaidmon on your\nDigiFarm.',352:'Talk to EXTyrannomon\nin the Front Room.',354:'Report to EXTyrannomon\nin the Front Room.',357:'Have a selfish\nShaujinmon on your\nDigiFarm.',359:'Talk to Volcamon\nin Whirly City.',360:'Investigate the giant\nzombie in Skull Seabed.',361:'Report to Volcamon\nin Whirly City.',362:'The Mystery of the\nSunken Zombie',363:'Investigate the giant\nzombie that appeared\nin Skull Seabed.',364:'Have a demure\nArgomon (Ultimate) in your\nExpedition Team.',366:'Talk to Leomon\nin Whirly City.',367:'Investigate the\nskeleton ghost in\nSkull Seabed.',368:'Report to Leomon\nin Whirly City.',369:'Terror!! The\nSkull Legend',370:'Investigate the\nskeleton ghost that\nappeared in Skull Seabed.',371:'Have a demure\nGaogamon in your\nExpedition Team.',372:'Talk to Angewomon\nin the Front Room.',373:'Find Salamon\nin Flower Prairie.',374:'Find SlashAngemon\nat Tokona Coast.',376:'Report to Angewomon\nin the Front Room.',377:'Assemble! The\nAngel Army?',378:'Gather members for\nthe newly formed\nAngel Army.',379:'Have a clingy\nOphanimon in your\nExpedition Team.',381:'Talk to Archnemon\nin the Front Room.',382:'Find Kongoumon\nin Flower Prairie.',383:'Find HerculesKabuterimon\nat Tokona Coast.',385:'Report to Archnemon\nin the Front Room.',386:'Assemble! The\nInsect Army?',387:'Gather members for\nthe newly formed\nInsect Army.',388:'Have an energetic\nTigerVespamon in your\nExpedition Team.',390:'Talk to Gatomon\nin Skull City.',392:'Report to Gatomon\nin Skull City.',393:'VS Kongoumon &\nHerculesKabuterimon',395:'Have an energetic\nSaberLeomon on your\nDigiFarm.',397:'Talk to Matadormon\nin Skull City.',399:'Report to Matadormon\nin Skull City.',400:'VS MetalEtemon &\nVajramon',402:'Have a funky\nPhantomon on your\nDigiFarm.',404:'Talk to Paildramon\nin Spiderweb City.',410:'Report to Paildramon\nin Spiderweb City.',413:'Have a robotic\nSpinomon in your party.',416:'Talk to MegaloGrowmon\nin Spiderweb City.',422:'Report to MegaloGrowmon\nin Spiderweb City.'}

def main():
 records=collect_messages(Rom(rom_paths()['blue']));prior=translate_records(records)
 rows=list(csv.DictReader((ROOT/'translations/work_queue.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
 byid={k:r for r in rows for k in r['ids'].split(';')}; blocks=[];review=[];seen=set()
 def add(key,en,category,note):
  r=byid[key];ids=r['ids'].split(';')
  if any(x in prior or x in seen for x in ids):raise ValueError(f'duplicate {ids}')
  if records[key]['source']!=r['japanese']:raise ValueError('source changed')
  seen.update(ids);review.append({'category':category,'japanese':r['japanese'],'ids':ids,'english':en,'evidence':SRC,'review_note':note})
  for x in ids:
   z=records[x];blocks.append({'archive':z['archive'],'entry':z['entry'],'start':z['index'],'category':category,'english':[en],'sources':[],'review_note':note})
 for k,v in FARM.items():
  if isinstance(k,int): key=f'MSG/MESPAK05.PAK:001:{k:05d}'
  else:
   ent,idx=k.split(':');key=f'MSG/MESPAK05.PAK:{int(ent):03d}:{int(idx):05d}'
  add(key,v,'DigiFarm reports','Natural English rendering of the Digimon\'s reaction; wraps preserve the compact report layout.')
 for idx,v in QUEST.items():add(f'MSG/MESPAK01.PAK:000:{idx:05d}', '\n'.join('\n'.join(textwrap.wrap(line,15,break_long_words=False,break_on_hyphens=False) or ['']) for line in v.split('\n')), 'Menus, quests and battle prompts','Quest objective/title translated from Japanese; species spellings reused from the already-reviewed Digimon name table and wrapped to 15 columns.')
 (ROOT/'translations/batch21.json').write_text(json.dumps({'description':'DigiFarm reactions and HQ/side-quest objectives. Digimon names use established English franchise spellings; abbreviation suffixes in the source are preserved.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'translations/review_batch21.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'{len(blocks)} slots from {len(review)} groups')
if __name__=='__main__':main()


