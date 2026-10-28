"""Record batch31 ROM hashes, startup smoke captures, and build checks."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch31.json'
    review_path = ROOT / 'translations/review_batch31.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'translations/graphics_manifest.json').read_text(encoding='utf-8'))
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch31 ROMs loaded through the Bandai boot splash and '
            'opening Digimon name cards. Structural ROM validation, all 13 '
            'pipeline tests, font checks, translated-line width checks, and '
            'visual review of the new Call Allies sprite passed. This is startup '
            'smoke QA, not an active story, mission, DigiFarm, or battle '
            'playthrough; new content still needs in-game context review.'
        ),
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'review_path': review_path.relative_to(ROOT).as_posix(),
            'review_groups': len(reviews),
            'translated_slots': sum(len(block['english']) for block in batch['blocks']),
        },
        'graphics': {
            'manifest': 'translations/graphics_manifest.json',
            'localized_states': len(manifest),
            'new_states_in_batch': 1,
            'note': 'Batch31 adds the Call Allies battle sprite label; prior localized states carry forward.',
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['translated_slots'] == 8300
        assert report['total_slots'] == 15674
        assert report['wide_lines'] == []
        screenshots = []
        for name, note in [
            ('boot_splash.png', 'The batch31 ROM reached the Bandai boot splash.'),
            ('opening_scene.png', 'The opening Digimon name cards loaded; labels were visually checked at native DS resolution.'),
        ]:
            path = ROOT / f'build/qa/{version}_batch31_smoke/{name}'
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
    target = ROOT / 'build/qa/validation_batch31.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
