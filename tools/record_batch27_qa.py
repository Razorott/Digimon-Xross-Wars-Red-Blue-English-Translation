"""Record batch27 hashes, automated checks, and startup screenshots."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    screenshots_by_version = {
        'blue': ROOT / 'build/qa/blue_batch27_smoke',
        'red': ROOT / 'build/qa/red_batch27_smoke',
    }
    graphic_paths = [
        ROOT / 'build/qa/batch27_logo_review.png',
        ROOT / 'build/qa/batch27_graphic_review.png',
    ]
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch27 ROMs loaded and advanced from the boot splash to '
            'the opening character cards. Structural ROM validation passed, '
            'all 13 pipeline tests passed, and story and move-name width '
            'checks report no overflow. This is startup and asset-preview QA, '
            'not an active story or battle playthrough; the newly translated '
            'scene and battle names still need in-game context review.'
        ),
        'text_batch': {
            'path': 'translations/batch27.json',
            'review_path': 'translations/review_batch27.json',
            'review_groups': len(json.loads(
                (ROOT / 'translations/review_batch27.json').read_text(encoding='utf-8'))),
            'translated_slots': sum(len(block['english']) for block in
                                    json.loads((ROOT / 'translations/batch27.json').read_text(encoding='utf-8'))['blocks']),
        },
        'graphics_review': [],
        'versions': {},
    }
    for path, note in zip(graphic_paths, [
        'Both English logos show complete DIGIMON lettering and the full RED/BLUE subtitle within the native sprite bounds.',
        'The Level Up badge, DigiFusion Requirements heading, and three Recruiting animation states are clear, contained, and free of Japanese text remnants.',
    ]):
        result['graphics_review'].append({
            'path': path.relative_to(ROOT).as_posix(),
            'sha256': sha(path),
            'visual_review': note,
        })

    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        screenshots = []
        for name, note in [
            ('boot_splash.png', 'The batch27 ROM reached the boot splash.'),
            ('opening_scene.png', 'The batch27 ROM advanced into the opening character cards.'),
        ]:
            path = screenshots_by_version[version] / name
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
    target = ROOT / 'build/qa/validation_batch27.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
