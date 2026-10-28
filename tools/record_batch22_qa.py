"""Record batch 22 title/menu emulator checks bound to both ROM hashes."""
import hashlib, json
from xros_text import ROOT, rom_paths

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
    result={'review_date':'2026-10-25','emulator':'Libretro DeSmuME 0.9.12, software renderer',
            'scope':'Both batch22 ROMs booted to title and menu. The complete Blue and Red title logos were visually checked. New battle moves, Sky Fort dialogue and item labels passed structural and width validation but still need active gameplay review. The longest move label measures 101 px in a 104 px budget; the formal Digimon name Armadillomon uses the compact HUD label Armadillo.',
            'versions':{}}
    for version,original in rom_paths().items():
        report=json.loads((ROOT/f'build/{version}_report.json').read_text(encoding='utf-8'))
        output=ROOT/'build'/report['output']
        assert sha(original)==config['original_sha256'][version]
        assert sha(output)==report['output_sha256']
        shots=[]
        for name,note in [('title_idle.png','Complete English title logo fits in frame.'),
                          ('title_menu.png','Start Adventure menu item is visible and legible.')]:
            path=ROOT/'build/qa'/f'{version}_batch22_title'/name
            shots.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'visual_review':note})
        result['versions'][version]={'output':report['output'],'output_sha256':sha(output),
            'original_sha256':sha(original),'translated_slots':report['translated_slots'],
            'slot_percent':report['slot_percent'],'wide_lines':report['wide_lines'],
            'graphics_states':report['graphics_translation']['states'],
            'display_names':report['display_names'],'move_names':report['move_names'],'screenshots':shots}
    target=ROOT/'build/qa/validation_batch22.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)

if __name__=='__main__': main()
