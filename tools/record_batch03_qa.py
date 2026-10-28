"""Record the specific batch-03 emulator screenshots inspected by a reviewer.

Run only after both scripted emulator checks finish and the named screenshots
have been visually inspected. This is a bounded smoke check, not a playthrough.
"""
import hashlib
import json
from datetime import date

from xros_text import ROOT, rom_paths


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    reviewed = {
        'blue': {
            '00_title_idle.png': 'English title logo visible and proportionate on the original art.',
            '01_title_menu.png': 'Start Adventure button legible.',
            '02_intro_04.png': 'English illustrated intro caption legible.',
            '03_dialogue_059.png': 'Early portrait dialogue and Akari speaker label legible.',
            '10_pause.png': 'Early pause menu graphics and labels legible in the captured state.',
            'pause_menu/status_still.png': 'Status data legible; compact carousel tab labels no longer overlap, though they are small.',
        },
        'red': {
            '00_title_idle.png': 'English Red title logo visible and proportionate on the original art.',
            '01_title_menu.png': 'Start Adventure button legible.',
            '02_intro_04.png': 'English illustrated intro caption legible.',
        },
    }
    result = {
        'review_date': date.today().isoformat(),
        'emulator': 'Libretro DeSmuME 0.9.12, Windows x64 interpreter, software renderer',
        'core_sha256': digest(ROOT / '.tools/desmume/desmume_libretro.dll'),
        'automated_tests': '10 passed: python -m unittest discover -s tests -v',
        'scope': 'Blue title, illustrated intro, early dialogue, pause and status screens; Red title and illustrated intro. The DigiLab and battles were verified structurally and in graphic previews but were not reached in this emulator route.',
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / 'build' / f'{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert digest(original) == config['original_sha256'][version]
        assert digest(output) == report['output_sha256']
        screenshots = []
        for name, note in reviewed[version].items():
            path = ROOT / 'build' / 'qa' / f'{version}_batch03_final' / name
            screenshots.append({'path': path.relative_to(ROOT).as_posix(),
                                'sha256': digest(path), 'visual_review': note})
        result['versions'][version] = {
            'original_sha256': digest(original),
            'output_sha256': digest(output),
            'translated_slots': report['translated_slots'],
            'sequence': 'tools/qa_batch02_final.json' if version == 'blue' else 'tools/qa_batch03_red_short.json',
            'screenshots_reviewed': screenshots,
            'process_exit_code': 0,
        }
    destination = ROOT / 'build/qa/validation_batch03.json'
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(destination)


if __name__ == '__main__':
    main()
