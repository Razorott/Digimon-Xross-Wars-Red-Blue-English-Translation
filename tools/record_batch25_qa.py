"""Record batch25 build hashes, automated checks, and startup screenshots."""
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
            'Both batch25 ROMs loaded and advanced from the boot splash to the '
            'opening sequence. Structural ROM validation passed and all 13 '
            'pipeline tests passed. The story renderer reports no wide lines; '
            'the full move list peaks at 101 px against a 104 px budget. The '
            'Train farm animation cells were visually checked again and show '
            'clean English captions. This is startup QA, not an active story '
            'or battle playthrough; newly translated dialogue and attacks '
            'still need in-game context review.'
        ),
        'graphics_review': {
            'path': graphic.relative_to(ROOT).as_posix(),
            'sha256': sha(graphic),
            'visual_review': 'Both Train animation cells show clean English captions with no Japanese glyph fragments beneath them.',
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
            ('boot_splash.png', 'The batch25 ROM reached the opening splash.'),
            ('opening_scene.png', 'The batch25 ROM advanced into the opening sequence.'),
        ]:
            path = ROOT / f'build/qa/{version}_batch25_boot/{name}'
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
    target = ROOT / 'build/qa/validation_batch25.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
