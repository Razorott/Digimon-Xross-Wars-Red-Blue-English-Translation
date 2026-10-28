"""Record batch32 ROM checksums, structural checks, and emulator screenshots."""
import hashlib
import json

from xros_text import ROOT, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch32.json'
    review_path = ROOT / 'translations/review_batch32.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'translations/graphics_manifest.json').read_text(encoding='utf-8'))
    screenshots_by_version = {
        'blue': [
            ('blue_batch32_smoke/boot_splash.png', 'Blue ROM reached the Bandai boot splash.'),
            ('blue_batch32_smoke/opening_scene.png', 'Opening Digimon name cards fit at native DS resolution.'),
            ('blue_batch32_title/title_idle.png', 'The complete Blue title logo, including the D, is visible.'),
            ('blue_batch32_title/title_menu.png', 'Start Adventure remains inside the title-menu button.'),
        ],
        'red': [
            ('red_batch32_smoke/boot_splash.png', 'Red ROM reached the Bandai boot splash.'),
            ('red_batch32_smoke/opening_scene.png', 'Opening Digimon name cards fit at native DS resolution.'),
            ('red_batch32_title/title_idle.png', 'The complete Red title logo, including the D, is visible.'),
            ('red_batch32_title/title_menu.png', 'Start Adventure remains inside the title-menu button.'),
        ],
    }
    result = {
        'review_date': '2026-10-25',
        'emulator': 'Libretro DeSmuME 0.9.12, software renderer',
        'scope': (
            'Both batch32 ROMs passed structural validation and booted through '
            'the opening Digimon cards. Blue and Red title logos and title-menu '
            'buttons were visually checked at native DS resolution. All 13 '
            'pipeline tests passed, no translated lines exceed the configured '
            'width checks, and original ROM hashes match project.json. The new '
            'side-quest dialogue, battle moves, DigiFarm reports, and gift-ticket '
            'descriptions were not exercised in an active gameplay session.'
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
            'new_states_in_batch': 0,
            'note': 'The 229 existing localized title, intro, menu, battle, status, and facility sprite states carry forward; no new graphic lettering was added in batch32.',
        },
        'versions': {},
    }
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['translated_slots'] == 8460
        assert report['total_slots'] == 15674
        assert report['slot_percent'] == 53.97
        assert report['wide_lines'] == []
        screenshots = []
        for relative, note in screenshots_by_version[version]:
            path = ROOT / 'build/qa' / f'{version}_batch32_{"title" if "title_" in relative else "smoke"}' / relative.split('/', 1)[1]
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
    target = ROOT / 'build/qa/validation_batch32.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
