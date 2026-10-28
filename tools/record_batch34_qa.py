"""Record batch34 structural, emulator, and graphics-preview QA."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch34.json'
    review_path = ROOT / 'translations/review_batch34.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'translations/graphics_manifest.json').read_text(encoding='utf-8'))
    status_preview = ROOT / 'build/graphics/status_tabs_shadow_qa.png'
    screenshot_names = [
        ('title_idle.png', 'Complete localized title logo shown at native DS resolution.'),
        ('title_menu.png', 'Start Adventure fits inside the title-menu button.'),
        ('intro_840.png', 'Illustrated opening sequence rendered in the emulator.'),
    ]
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch34 ROMs passed structural validation, all 13 pipeline tests, '
            'and title/menu/illustrated-intro emulator smoke checks. No translated '
            'line exceeds its configured width. The new quiz mission and dialogue '
            'were not actively played through. The status-tab sprites were reviewed '
            'in an enlarged asset preview with their one-pixel shadow; a full in-game '
            'pause/status-screen capture is still pending.'
        ),
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'review_path': review_path.relative_to(ROOT).as_posix(),
            'review_groups': len(reviews),
            'direct_message_slots': len(batch['blocks']),
            'newly_translated_slots_including_glossary_matches': 165,
        },
        'story_coherence': {
            'path': 'translations/story_coherence.md',
            'checked_against': [
                'https://digimon-gameportal.bn-ent.net/product/xros_wars/story/',
                'https://lineup.toei-anim.co.jp/en/tv/digimon_xw/',
            ],
            'finding': (
                'The official game synopsis describes a new Elestou Zone adventure '
                'and says Red/Blue have different story characters. The official '
                'anime synopsis describes the larger Bagura Empire/faction conflict. '
                'No exact episode placement is established by those official pages.'
            ),
        },
        'graphics': {
            'manifest': 'translations/graphics_manifest.json',
            'localized_states': len(manifest),
            'new_states_in_batch': 0,
            'status_labels_with_shadow': 10,
            'preview_path': status_preview.relative_to(ROOT).as_posix(),
            'preview_sha256': sha(status_preview),
            'note': (
                'Batch34 carries forward the ten revised status-tab states with '
                'dark outlines or diagonal one-pixel shadows. Asset-level preview '
                'was checked; full menu navigation remains unverified.'
            ),
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['translated_slots'] == 8755
        assert report['total_slots'] == 15674
        assert report['slot_percent'] == 55.86
        assert report['wide_lines'] == []
        screenshots = []
        for filename, note in screenshot_names:
            path = ROOT / 'build/qa' / f'{version}_batch34_intro' / filename
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
    target = ROOT / 'build/qa/validation_batch34.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
