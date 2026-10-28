"""Record checksum-bound validation for the batch35 graphics-only update."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from xros_text import ROOT, Pak, Rom, rom_paths
from graphics import render_cell


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_sprite_preview(rom_path):
    rom = Rom(rom_path)
    paks = {name: Pak(rom.file(name)) for name in ('SPR_NCGR.PAK', 'SPR_NCLR.PAK', 'SPR_NCER.PAK')}
    canvas = Image.new('RGB', (440, 210), (36, 36, 48))
    draw = ImageDraw.Draw(canvas)
    for row, (entry, state, title) in enumerate(((127, 0, 'Cancel'), (138, 0, "Let's Begin!"))):
        image = render_cell(paks['SPR_NCGR.PAK'].file(entry),
                            paks['SPR_NCLR.PAK'].file(entry),
                            paks['SPR_NCER.PAK'].file(entry), state)
        draw.text((12, 10 + row * 100), f'{entry}:{state} {title}  native {image.width}x{image.height}', fill='white')
        canvas.paste(image.convert('RGB'), (14, 34 + row * 100))
        enlarged = image.resize((image.width * 4, image.height * 4), Image.Resampling.NEAREST)
        canvas.paste(enlarged.convert('RGB'), (140, 28 + row * 100))
    target = ROOT / 'build/graphics/batch35_cancel_begin_preview.png'
    canvas.save(target)
    return target


def main():
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    batch_path = ROOT / 'translations/batch35.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'translations/graphics_manifest.json').read_text(encoding='utf-8'))
    graphic_entries = [(row.get('entry'), row.get('bank'), row.get('english')) for row in manifest]
    added = [(127, 0, 'Cancel'), (138, 0, "Let's Begin!"),
             (138, 1, "Let's Begin!"), (138, 2, "Let's Begin!")]
    assert len(manifest) == 233, len(manifest)
    assert all(item in graphic_entries for item in added)

    outputs = {}
    for version, original in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output = ROOT / 'build' / report['output']
        assert sha(original) == config['original_sha256'][version]
        assert sha(output) == report['output_sha256']
        assert report['translated_slots'] == 8755
        assert report['total_slots'] == 15674
        assert report['slot_percent'] == 55.86
        assert report['graphics_translation']['states'] == 233
        assert report['wide_lines'] == []
        screenshots = []
        for filename in ('title_idle.png', 'title_menu.png', 'intro_840.png'):
            path = ROOT / 'build/qa' / f'{version}_batch35_intro' / filename
            screenshots.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
        outputs[version] = {
            'output': report['output'],
            'output_sha256': sha(output),
            'original_sha256': sha(original),
            'translated_slots': report['translated_slots'],
            'total_slots': report['total_slots'],
            'slot_percent': report['slot_percent'],
            'graphics_states': report['graphics_translation']['states'],
            'wide_lines': report['wide_lines'],
            'screenshots': screenshots,
        }

    sprite_preview = make_sprite_preview(ROOT / 'build' / outputs['blue']['output'])
    result = {
        'review_date': '2026-10-25',
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'direct_message_slots': sum(len(block.get('english', [])) for block in batch['blocks']),
            'translated_slot_total': 8755,
            'slot_percent': 55.86,
        },
        'graphics': {
            'manifest': 'translations/graphics_manifest.json',
            'localized_states': len(manifest),
            'new_states': added,
            'status_shadow_preview': 'build/graphics/status_tabs_shadow_qa.png',
            'new_sprites_preview': sprite_preview.relative_to(ROOT).as_posix(),
            'new_sprites_preview_sha256': sha(sprite_preview),
            'note': 'Sprite-level review at native and enlarged pixel scale. Full in-game pause/status navigation remains pending.',
        },
        'story_coherence': 'See translations/story_coherence.md; official summaries do not establish exact episode placement.',
        'tests': {'pipeline': '13 passed', 'emulator': 'Blue and Red title, menu, and illustrated intro smoke checks passed'},
        'versions': outputs,
    }
    target = ROOT / 'build/qa/validation_batch35.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)


if __name__ == '__main__':
    main()
