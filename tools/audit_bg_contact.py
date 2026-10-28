"""Render localized background maps as indexed contact sheets for text audit."""
from __future__ import annotations
import json
from graphics import contact, render_map
from xros_text import ROOT, Pak, Rom


def main() -> None:
    rom=Rom(ROOT/'build/Digimon_Super_Xros_Wars_Blue_English_batch103.nds')
    tiles=Pak(rom.file('BG_NCGR.PAK'))
    colors=Pak(rom.file('BG_NCLR.PAK'))
    maps=Pak(rom.file('BG_NSCR.PAK'))
    out=ROOT/'build/graphics/bg_audit'
    out.mkdir(parents=True,exist_ok=True)
    page=[];errors=[];rendered=0
    for index in range(min(tiles.count,colors.count,maps.count)):
        try:
            image=render_map(tiles.file(index),colors.file(index),maps.file(index))
            page.append((index,image))
            rendered+=1
        except Exception as exc:
            errors.append({'index':index,'error':str(exc)})
        if len(page)==24 or index==min(tiles.count,colors.count,maps.count)-1:
            if page:
                contact(page,out/f'bg_{index//24:02d}.png',columns=4,cell=(256,210))
                page=[]
    (out/'report.json').write_text(json.dumps({'rendered':rendered,'errors':errors},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rendered':rendered,'errors':len(errors),'pages':(rendered+23)//24}))


if __name__=='__main__':main()
