"""Record checksum-bound title-screen checks for the batch09 ROMs."""
import hashlib
import json
from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, Windows x64, software renderer',
        'core_sha256': sha(ROOT / '.tools/desmume/desmume_libretro.dll'),
        'sequence': 'tools/qa_batch05_titles.json',
        'frames_per_game': 1983,
        'automated_tests': '10 passed with unittest discover -s tests -v',
        'scope': 'Both batch09 ROMs booted to title idle and the title menu. Blue and Red title logos were visually checked at native DS resolution; the D counter is now filled with a solid navy inset and the complete mark fits in the sprite cell. Structural validation passed with no missing glyphs, substitutions, or over-width lines. Battle screens, later story scenes, and complete playthroughs were not visually checked in this pass.',
        'remaining': [
            'Remaining story, mission, menu, battle, farm, item, and graphics translation',
            'Active battle and DigiLab gameplay screenshots',
            'Later story scenes and full playthroughs of both versions',
        ],
        'versions': {},
    }
    screenshots = {
        'blue': [
            ('title_idle.png', 'Complete Blue title logo with closed D counter; no lettering touches the sprite-cell edge.'),
            ('title_menu.png', 'Blue title logo and Start Adventure option are readable.'),
        ],
        'red': [
            ('title_idle.png', 'Complete Red title logo with closed D counter; no lettering touches the sprite-cell edge.'),
            ('title_menu.png', 'Red title logo and Start Adventure option are readable.'),
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
            path = ROOT / 'build' / 'qa' / f'{version}_batch09' / name
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
    target = ROOT / 'build/qa/validation_batch09.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    record()
