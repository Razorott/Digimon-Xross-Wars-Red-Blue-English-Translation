"""Bind batch 11 visual and structural checks to both output ROM checksums."""
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
        'automated_tests':'12 passed with unittest discover -s tests -v',
        'scope':'Both final batch11 ROMs booted to their title menus and both logos were visually checked. The compact font was checked in the Blue pause menu. Green/gold report banners were inspected as native-size DS-palette sprites. The opponent battle HUD, later story scenes and every banner animation still need in-game review.',
        'versions':{},
    }
    for version,original in rom_paths().items():
        report=json.loads((ROOT/f'build/{version}_report.json').read_text(encoding='utf-8'))
        output=ROOT/'build'/report['output']
        assert sha(original)==config['original_sha256'][version]
        assert sha(output)==report['output_sha256']
        names=[ROOT/'build/qa'/f'{version}_batch11_title'/name
               for name in ('title_idle.png','title_menu.png')]
        if version=='blue':
            names.append(ROOT/'build/qa/blue_batch11_pause/battle_ready.png')
            names.append(ROOT/'build/qa/batch11_banners_small_preview.png')
        result['versions'][version]={
            'output':report['output'],'output_sha256':sha(output),
            'original_sha256':sha(original),'translated_slots':report['translated_slots'],
            'slot_percent':report['slot_percent'],'wide_lines':report['wide_lines'],
            'display_names':report['display_names'],
            'move_names':report['move_names'],
            'screenshots_reviewed':[{'path':path.relative_to(ROOT).as_posix(),
                                     'sha256':sha(path)} for path in names],
        }
    target=ROOT/'build/qa/validation_batch11.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(target)


if __name__=='__main__':main()
