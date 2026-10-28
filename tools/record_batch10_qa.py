"""Bind batch 10 structural and visual checks to final ROM hashes."""
import hashlib
import json
from xros_text import ROOT,rom_paths

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
    result={
        'review_date':'2026-10-25',
        'emulator':'Libretro DeSmuME 0.9.12, software renderer',
        'core_sha256':sha(ROOT/'.tools/desmume/desmume_libretro.dll'),
        'automated_tests':'10 passed with unittest discover -s tests -v',
        'scope':'Both final batch10 ROMs booted to the title and showed complete logos. The Blue intro metallic logo was checked in active play at frame 2466. Structural validation found no missing glyphs or over-width lines. New dialogue, battle moves and later graphics still need in-game playthrough checks.',
        'versions':{},
    }
    for version,original in rom_paths().items():
        report=json.loads((ROOT/f'build/{version}_report.json').read_text(encoding='utf-8'))
        output=ROOT/'build'/report['output']
        assert sha(original)==config['original_sha256'][version]
        assert sha(output)==report['output_sha256']
        names=['title_idle.png','title_menu.png']
        if version=='blue':names.append('intro_480.png')
        images=[]
        for name in names:
            path=ROOT/'build/qa'/f'{version}_batch10'/name
            images.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
        result['versions'][version]={
            'output':report['output'],'output_sha256':sha(output),
            'original_sha256':sha(original),'translated_slots':report['translated_slots'],
            'slot_percent':report['slot_percent'],'wide_lines':report['wide_lines'],
            'screenshots_reviewed':images,
        }
    target=ROOT/'build/qa/validation_batch10.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__':main()
