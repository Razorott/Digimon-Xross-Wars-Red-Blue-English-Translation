"""Bind batch 14 smoke tests and graphic inspection to both ROM hashes."""
import hashlib
import json
from xros_text import ROOT, rom_paths

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
    result={
        'review_date':'2026-10-25',
        'emulator':'Libretro DeSmuME 0.9.12, software renderer',
        'core_sha256':sha(ROOT/'.tools/desmume/desmume_libretro.dll'),
        'automated_tests':'13 passed with unittest discover -s tests -q',
        'scope':'Both batch14 ROMs booted to title menu. Blue pause menu was inspected from a save state. Both quest-heading states were decoded from the rebuilt Blue ROM and visually inspected. Newly translated NPC, mission, farm, item and active-battle text still needs playthrough review.',
        'versions':{},
    }
    for version,original in rom_paths().items():
        report=json.loads((ROOT/f'build/{version}_report.json').read_text(encoding='utf-8'))
        output=ROOT/'build'/report['output']
        assert sha(original)==config['original_sha256'][version]
        assert sha(output)==report['output_sha256']
        paths=[ROOT/'build/qa'/f'{version}_batch14_title'/name
               for name in ('title_idle.png','title_menu.png')]
        if version=='blue':
            paths += [ROOT/'build/qa/blue_batch14_pause/battle_ready.png',
                      ROOT/'build/qa/batch14_quest_native.png']
        result['versions'][version]={
            'output':report['output'],'output_sha256':sha(output),
            'original_sha256':sha(original),'translated_slots':report['translated_slots'],
            'slot_percent':report['slot_percent'],
            'graphics_states':report['graphics_translation']['states'],
            'display_names':report['display_names'],'move_names':report['move_names'],
            'screenshots_reviewed':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths],
        }
    target=ROOT/'build/qa/validation_batch14.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__':main()
