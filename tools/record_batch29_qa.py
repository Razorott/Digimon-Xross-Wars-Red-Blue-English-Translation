"""Record batch29 ROM hashes, startup captures, and automated checks."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch29.json'
    review_path = ROOT / 'translations/review_batch29.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    screenshots_by_version = {
        'blue': ROOT / 'build/qa/blue_batch29_smoke',
        'red': ROOT / 'build/qa/red_batch29_smoke',
    }
    title_screenshots_by_version = {
        'blue': ROOT / 'build/qa/blue_batch29_title',
        'red': ROOT / 'build/qa/red_batch29_title',
    }
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch29 ROMs loaded through the title idle and title menu, '
            'then advanced from the Bandai boot splash to the opening Digimon '
            'name cards. The Blue and Red title captures show the complete '
            'DIGIMON lettering, including the full D. Structural ROM validation, '
            'the 13 pipeline tests, and all translated-line width checks '
            'passed. This is startup smoke QA, not an active story or battle '
            'playthrough; the newly translated missions, item text, dialogue, '
            'and battle moves still need in-game context review.'
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
            'note': 'Batch29 adds text only; all 228 existing localized graphic states are carried forward.',
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
            ('boot_splash.png', 'The batch29 ROM reached the Bandai boot splash.'),
            ('opening_scene.png', 'The batch29 ROM advanced to the opening Digimon name cards.'),
        ]:
            path = screenshots_by_version[version] / name
            screenshots.append({
                'path': path.relative_to(ROOT).as_posix(),
                'sha256': sha(path),
                'visual_review': note,
            })
        for name, note in [
            ('title_idle.png', 'The complete version-specific title logo is visible at DS resolution.'),
            ('title_menu.png', 'The English title menu fits within its native selection bar.'),
        ]:
            path = title_screenshots_by_version[version] / name
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
            'total_slots': report['total_slots'],
            'slot_percent': report['slot_percent'],
            'wide_lines': report['wide_lines'],
            'graphics_states': report['graphics_translation']['states'],
            'display_names': report['display_names'],
            'move_names': report['move_names'],
            'screenshots': screenshots,
        }
    target = ROOT / 'build/qa/validation_batch29.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
