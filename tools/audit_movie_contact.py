"""Render the three NCGMOVIE tile sets for a visual localization audit."""
from __future__ import annotations
import json
from graphics import contact,render_map
from xros_text import ROOT,Pak,Rom,rom_paths


def lz11(data):
    if data[0]!=0x11:raise ValueError('Not Nintendo LZ11')
    size=int.from_bytes(data[1:4],'little')
    pos=4
    if not size:
        size=int.from_bytes(data[4:8],'little')
        pos=8
    out=bytearray()
    while len(out)<size:
        flags=data[pos];pos+=1
        for bit in range(7,-1,-1):
            if len(out)>=size:break
            if not flags&(1<<bit):
                out.append(data[pos]);pos+=1
                continue
            a=data[pos];b=data[pos+1];pos+=2
            kind=a>>4
            if kind==0:
                c=data[pos];pos+=1
                length=((a&15)<<4 | b>>4)+0x11
                back=((b&15)<<8 | c)+1
            elif kind==1:
                c=data[pos];d=data[pos+1];pos+=2
                length=((a&15)<<12 | b<<4 | c>>4)+0x111
                back=((c&15)<<8 | d)+1
            else:
                length=kind+1
                back=((a&15)<<8 | b)+1
            if back>len(out):raise ValueError('LZ11 back-reference exceeds output')
            for _ in range(min(length,size-len(out))):out.append(out[-back])
    return bytes(out)


def main():
    rom=Rom(rom_paths()['blue'])
    out=ROOT/'build/graphics/movie_audit'
    out.mkdir(parents=True,exist_ok=True)
    report=[]
    for movie in range(3):
        archive=Pak(rom.file(f'NCGMOVIE/MV{movie:04d}.bin'))
        base=lz11(archive.file(0))
        colors=lz11(archive.file(1))
        images=[]
        for index in range(2,archive.count):
            try:
                image=render_map(lz11(archive.file(index)),colors,base)
                images.append((index,image))
                if index in (2,31,61):
                    image.save(out/f'movie{movie}_frame{index:02d}.png')
            except Exception as error:
                report.append({'movie':movie,'index':index,'error':str(error)})
        for page in range(0,len(images),24):
            contact(images[page:page+24],out/f'movie{movie}_{page//24:02d}.png',
                    columns=4,cell=(256,210))
        report.append({'movie':movie,'archive_entries':archive.count,
                       'rendered':len(images)})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rendered':sum(x.get('rendered',0) for x in report),
                      'errors':sum('error' in x for x in report)}))


if __name__=='__main__':main()
