"""Record batch28 ROM hashes, startup captures, and automated checks."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch28.json'
    review_path = ROOT / 'translations/review_batch28.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    screenshots_by_version = {
        'blue': ROOT / 'build/qa/blue_batch28_smoke',
        'red': ROOT / 'build/qa/red_batch28_smoke',
    }
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch28 ROMs loaded and advanced from the Bandai boot splash '
            'to the opening Digimon name cards. Structural ROM validation, '
            'the 13 pipeline tests, and all translated-line width checks '
            'passed. This is startup smoke QA, not an active story or battle '
            'playthrough; newly translated dialogue and move names still need '
            'in-game context review.'
        ),
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'review_path': review_path.relative_to(ROOT).as_posix(),
            'review_groups': len(reviews),
            'translated_slots': sum(len(block['english']) for block in batch['blocks']),
        },
        'graphics': {
            'manifest': 'translations/graphics_manifest.json',
            'localized_states': 228,
            'new_states_in_batch': 0,
            'note': 'Existing graphics are inherited from batch27; batch28 adds text only.',
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['wide_lines'] == []
        screenshots = []
        for name, note in [
            ('boot_splash.png', 'The batch28 ROM reached the Bandai boot splash.'),
            ('opening_scene.png', 'The batch28 ROM advanced to the opening Digimon name cards.'),
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
    target = ROOT / 'build/qa/validation_batch28.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
