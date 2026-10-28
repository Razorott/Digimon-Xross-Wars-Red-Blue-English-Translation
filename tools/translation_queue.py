"""Export/import a stable-ID bilingual translation queue.

The queue groups byte-identical Japanese within one content type. Authors fill
English and Evidence URL, then import to a new batch. No fuzzy match, ROM edit,
or overwrite of an earlier translation is performed by this tool.
"""
import argparse
import collections
import csv
import json
import re
from pathlib import Path
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records


FIELDS=['category','japanese','context_before','context_after','required_tokens',
        'width_hint','occurrences','ids','english','evidence_url','review_note']


def category(row):
    a=row['archive'].split('/')[-1]
    n=row['index']
    if a=='MESPAK00.PAK':
        if 179<=n<=1022 or 4070<=n<=4299 or 4440<=n<=4500:return 'Digimon names'
        if 1228<=n<=3750:return 'Battle moves'
        if 1023<=n<=1090:return 'Locations'
        if 3751<=n<=4070 or 4299<=n<=4535:return 'Items and equipment'
        return 'Common labels and traits'
    if a=='MESPAK01.PAK':return 'Menus, quests and battle prompts'
    if a=='MESPAK02.PAK':return 'Story and dialogue'
    if a=='MESPAK03.PAK':return 'Digimon profiles'
    if a=='MESPAK04.PAK':return 'Move and item descriptions'
    return 'DigiFarm reports'


def export(path,limit=None,only=None):
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    grouped=collections.defaultdict(list)
    for row in records.values():
        if row['id'] in translated or not row['source'].strip():continue
        group=category(row)
        if only and group!=only:continue
        grouped[(group,row['source'])].append(row['id'])
    order=sorted(grouped,key=lambda key:(-len(grouped[key]),key[0],min(grouped[key])))
    if limit:order=order[:limit]
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,delimiter='\t',lineterminator='\n')
        writer.writeheader()
        for cat,source in order:
            ids=grouped[(cat,source)]
            first=records[ids[0]]
            def neighbor(offset):
                key=f"{first['archive']}:{first['entry']:03d}:{first['index']+offset:05d}"
                return records.get(key,{}).get('source','')
            writer.writerow({'category':cat,'japanese':source,
                             'context_before':neighbor(-1),'context_after':neighbor(1),
                             'required_tokens':' '.join(re.findall(r'\^[0-9A-Za-z]',source)),
                             'width_hint':'15 characters per story line' if cat=='Story and dialogue' else 'verify narrow UI fields',
                             'occurrences':len(ids),
                             'ids':';'.join(ids),'english':'','evidence_url':'','review_note':''})
    print(json.dumps({'output':str(path),'rows':len(order),'untranslated_slots':len(records)-len(translated),
                      'untranslated_unique_groups':len(grouped),'translated_slots':len(translated),
                      'total_slots':len(records)},ensure_ascii=False))


def import_queue(path,batch):
    records=collect_messages(Rom(rom_paths()['blue']))
    translated=translate_records(records)
    blocks=[];seen=set()
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t')
        if reader.fieldnames!=FIELDS:raise ValueError('Queue column layout changed')
        for row in reader:
            english=row['english'].strip()
            if not english:continue
            if not row['evidence_url'].strip():raise ValueError(f'Missing evidence URL for {row["japanese"]}')
            for key in row['ids'].split(';'):
                if key in seen or key in translated:raise ValueError(f'Duplicate/already translated ID {key}')
                if key not in records or records[key]['source']!=row['japanese']:
                    raise ValueError(f'Changed Japanese source or ID {key}')
                record=records[key];seen.add(key)
                blocks.append({'archive':record['archive'],'entry':record['entry'],
                               'start':record['index'],'category':row['category'],
                               'english':[english.replace('\\n','\n')],
                               'evidence_url':row['evidence_url'].strip(),
                               'review_note':row['review_note'].strip()})
    out=ROOT/'translations'/batch
    if out.exists():raise FileExistsError(f'Will not overwrite {out}')
    out.write_text(json.dumps({'description':f'Imported from {path.name}; original IDs and cited evidence retained.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'translated_slots':len(blocks)},ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['export','import'])
    parser.add_argument('--file',type=Path,default=ROOT/'translations/work_queue.tsv')
    parser.add_argument('--limit',type=int)
    parser.add_argument('--category')
    parser.add_argument('--batch',default='batch04.json')
    args=parser.parse_args()
    if args.action=='export':export(args.file,args.limit,args.category)
    else:import_queue(args.file,args.batch)


if __name__=='__main__':main()
