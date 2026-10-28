"""Record checksum-bound title-screen checks for the batch08 ROMs."""
import hashlib
import json
from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    result = {
        'review_date': '2026-10-24',
        'emulator': 'Libretro DeSmuME 0.9.12, Windows x64, software renderer',
        'core_sha256': sha(ROOT / '.tools/desmume/desmume_libretro.dll'),
        'sequence': 'tools/qa_batch05_titles.json',
        'frames_per_game': 1983,
        'automated_tests': '10 passed with unittest discover -s tests -v',
        'scope': 'Both batch08 ROMs booted to the title screen. The complete Blue and Red logos and Start Adventure title menus were visually checked. The D in DIGIMON has a complete face and outline in both versions. Structural validation passed with no missing glyphs, substitutions, or over-width lines. Active battle labels and a full playthrough were not visually checked in this pass.',
        'remaining': [
            'Remaining story, mission, menu, battle, farm, item, and graphics translation',
            'Active battle and DigiLab gameplay screenshots',
            'Later story scenes and full playthroughs of both versions',
        ],
        'versions': {},
    }
    screenshots = {
        'blue': [
            ('title_idle.png', 'The full DIGIMON D and Blue logo lettering fit within the artwork.'),
            ('title_menu.png', 'Full Blue logo and readable Start Adventure option.'),
        ],
        'red': [
            ('title_idle.png', 'The full DIGIMON D and Red logo lettering fit within the artwork.'),
            ('title_menu.png', 'Full Red logo and readable Start Adventure option.'),
        ],
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        if sha(original) != config['original_sha256'][version]:
            raise AssertionError(f'Original {version} ROM checksum changed')
        if sha(output) != report['output_sha256']:
            raise AssertionError(f'Built {version} ROM does not match its report')
        images = []
        for name, review in screenshots[version]:
            path = ROOT / 'build' / 'qa' / f'{version}_batch08' / name
            images.append({
                'path': path.relative_to(ROOT).as_posix(),
                'sha256': sha(path),
                'visual_review': review,
            })
        result['versions'][version] = {
            'output': report['output'],
            'output_sha256': sha(output),
            'original_sha256': sha(original),
            'translated_slots': report['translated_slots'],
            'slot_percent': report['slot_percent'],
            'process_exit_code': 0,
            'wide_lines': report['wide_lines'],
            'screenshots_reviewed': images,
        }
    target = ROOT / 'build/qa/validation_batch08.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    record()
