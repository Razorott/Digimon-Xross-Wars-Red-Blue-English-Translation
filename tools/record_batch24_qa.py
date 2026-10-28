"""Record batch24 ROM, title-screen, and farm-caption checks by output hash."""
import hashlib
import json
from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    graphic = ROOT / 'build/graphics/batch24_train_job_contact_zoom.png'
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch24 ROMs booted to the title and title menu. The full D '
            'and remaining letters of each title logo are visible inside the '
            'frame. Structural validation and all 13 pipeline tests passed; '
            'the battle move labels pass the measured 104 px limit and no '
            'story line exceeds the fixed 15-column renderer. The Train farm '
            'sprite animation cells were checked at native pixel scale; the '
            'selected cell no longer shows Japanese glyph fragments beneath '
            'the English caption. New battle, quest, and farm text still needs '
            'active in-game review.'
        ),
        'graphics_review': {
            'path': graphic.relative_to(ROOT).as_posix(),
            'sha256': sha(graphic),
            'visual_review': 'Both Train animation cells show a clean English caption with no overlapping source glyphs.',
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        screenshots = []
        for name, note in [
            ('title_idle.png', 'Full English title logo, including the D in DIGIMON, is inside the title frame.'),
            ('title_menu.png', 'Title menu text is visible and legible.'),
        ]:
            path = ROOT / f'build/qa/{version}_batch24_title/{name}'
            screenshots.append({
                'path': path.relative_to(ROOT).as_posix(),
                'sha256': sha(path),
                'visual_review': note,
            })
        result['versions'][version] = {
            'output': report['output'],
            'output_sha256': sha(output),
            'original_sha256': sha(original),
            'translated_slots': report['translated_slots'],
            'slot_percent': report['slot_percent'],
            'wide_lines': report['wide_lines'],
            'graphics_states': report['graphics_translation']['states'],
            'display_names': report['display_names'],
            'move_names': report['move_names'],
            'screenshots': screenshots,
        }
    target = ROOT / 'build/qa/validation_batch24.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
