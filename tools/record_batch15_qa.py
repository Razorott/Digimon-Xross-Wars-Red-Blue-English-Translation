"""Record batch 15 emulator smoke checks against rebuilt ROM hashes."""
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
        'scope':'Both batch15 ROMs booted to their title menus. The Blue pause menu was loaded from a save state. Story, quest, item, and battle text still needs active playthrough review; the opponent HUD abbreviation is checked by the measured name layout manifest.',
        'versions':{},
    }
    for version,original in rom_paths().items():
        report=json.loads((ROOT/f'build/{version}_report.json').read_text(encoding='utf-8'))
        output=ROOT/'build'/report['output']
        assert sha(original)==config['original_sha256'][version]
        assert sha(output)==report['output_sha256']
        paths=[ROOT/'build/qa'/f'{version}_batch15_title'/name
               for name in ('title_idle.png','title_menu.png')]
        if version=='blue':
            paths.append(ROOT/'build/qa/blue_batch15_pause/battle_ready.png')
        result['versions'][version]={
            'output':report['output'],'output_sha256':sha(output),
            'original_sha256':sha(original),'translated_slots':report['translated_slots'],
            'slot_percent':report['slot_percent'],
            'graphics_states':report['graphics_translation']['states'],
            'display_names':report['display_names'],'move_names':report['move_names'],
            'screenshots':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in paths],
        }
    target=ROOT/'build/qa/validation_batch15.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__':main()
