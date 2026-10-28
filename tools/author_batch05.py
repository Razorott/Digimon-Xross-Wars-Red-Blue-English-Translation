"""Extend battle move coverage with exact Dawn/Dusk English-name matches."""
import json
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

MOVES={
    'ジャスティスキック':'Justice Kick',
    'エナジーショット':'Energy Shot',
    'スマイリーボム':'Smiley Bomb',
    'エネルギーボム':'Energy Bomb',
    'ビットボム':'Bit Bomb',
    'スパイラルクロー':'Spiral Claw',
    'デッドリーボム':'Deadly Bomb',
    'メガメテオフォール':'MegaMeteoFall',
    'グランドクロス':'Grand Cross',
    'スターライト':'Starlight',
    'パワフルパンチ':'PowerfulPunch',
    'ムーンナイトボム':'MoonNightBomb',
}

def main():
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    existing=ROOT/'translations/batch05.json'
    if existing.exists():
        previous=json.loads(existing.read_text(encoding='utf-8'))
        regenerated={f"{b['archive']}:{b['entry']:03d}:{i:05d}"
                     for b in previous['blocks']
                     for i in range(b['start'],b['start']+len(b['english']))}
        translated={key:value for key,value in translated.items() if key not in regenerated}
    by_source={}
    for row in records.values():
        if row['archive']=='MSG/MESPAK00.PAK':by_source.setdefault(row['source'],[]).append(row)
    blocks=[]
    for source,english in MOVES.items():
        rows=by_source.get(source,[])
        if not rows:raise ValueError(f'Unmatched move: {source}')
        for row in rows:
            if not 1228<=row['index']<=3750 or row['id'] in translated:continue
            blocks.append({'archive':row['archive'],'entry':row['entry'],'start':row['index'],
                           'category':'move name','english':[english],
                           'evidence_url':'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt',
                           'review_note':'English string is an exact name match in a community extraction of the licensed US Dawn/Dusk game text.'})
    out=ROOT/'translations/batch05.json'
    out.write_text(json.dumps({'description':'Exact English move-name matches checked against US Digimon World Dawn/Dusk text.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'{len(blocks)} new move-name slots from {len(MOVES)} exact source-name matches')

if __name__=='__main__':main()
