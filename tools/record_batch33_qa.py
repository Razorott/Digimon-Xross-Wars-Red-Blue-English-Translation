"""Record batch33 structural, emulator, and graphics-preview QA."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch33.json'
    review_path = ROOT / 'translations/review_batch33.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'translations/graphics_manifest.json').read_text(encoding='utf-8'))
    status_preview = ROOT / 'build/graphics/status_tabs_shadow_qa.png'
    screenshot_names = [
        ('title_idle.png', 'Title logo and complete D visible at native DS resolution.'),
        ('title_menu.png', 'Start Adventure fits inside the title menu button.'),
        ('intro_840.png', 'Illustrated intro sequence rendered after selecting Start Adventure.'),
    ]
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch33 ROMs passed structural validation and rendered the title, '
            'title menu, and illustrated intro in the emulator. All 13 pipeline tests '
            'passed; no translated line exceeds its configured width. The status-tab '
            'sprite preview was visually checked at enlarged native-pixel scale. The '
            'status menu was not navigated in-game this batch, and the new mission, '
            'battle, DigiFarm, and item text still need active gameplay review.'
        ),
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'review_path': review_path.relative_to(ROOT).as_posix(),
            'review_groups': len(reviews),
            'direct_message_slots': len(batch['blocks']),
            'newly_translated_slots_including_glossary_matches': 130,
        },
        'graphics': {
            'manifest': 'translations/graphics_manifest.json',
            'localized_states': len(manifest),
            'new_states_in_batch': 0,
            'modified_status_animation_states': 10,
            'preview_path': status_preview.relative_to(ROOT).as_posix(),
            'preview_sha256': sha(status_preview),
            'note': (
                'Status tabs use the full English labels and a compact bold face. '
                'Most labels have a one-pixel dark outline; the two-line DigiXross '
                'label uses the shadow alone to keep the counters open. All use a '
                'diagonal one-pixel shadow. Preview is asset-level QA; full in-game '
                'status-screen navigation remains pending.'
            ),
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['translated_slots'] == 8590
        assert report['total_slots'] == 15674
        assert report['slot_percent'] == 54.8
        assert report['wide_lines'] == []
        screenshots = []
        for filename, note in screenshot_names:
            path = ROOT / 'build/qa' / f'{version}_batch33_intro' / filename
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
    target = ROOT / 'build/qa/validation_batch33.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
