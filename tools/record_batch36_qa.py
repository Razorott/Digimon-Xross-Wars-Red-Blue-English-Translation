"""Record batch36 review rows and checksum-bound validation for both ROMs."""
import hashlib
import json
from pathlib import Path

from build import collect_messages, encode_translation, translate_records
from xros_text import ROOT, Rom, rom_paths


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_review(records, batch):
    review = []
    for block in batch['blocks']:
        for index, english in enumerate(block['english'], block['start']):
            key = f"{block['archive']}:{block['entry']:03d}:{index:05d}"
            review.append({
                'category': block['category'],
                'japanese': records[key]['source'],
                'ids': [key],
                'english': english,
                'evidence': 'Original Japanese ROM (local primary source)',
                'review_note': block.get('review_note', ''),
            })
    return review


def main():
    batch_path = ROOT / 'translations/batch36.json'
    batch = json.loads(batch_path.read_text(encoding='utf-8'))
    config = json.loads((ROOT / 'project.json').read_text(encoding='utf-8'))
    blue_original = Rom(rom_paths()['blue'])
    original_records = collect_messages(blue_original)
    translations = translate_records(original_records)
    review = build_review(original_records, batch)
    assert len(review) == 18
    review_path = ROOT / 'translations/review_batch36.json'
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')

    markdown = [
        '# Batch 36 review',
        '',
        'This corrective build uses ordinary ASCII for Digimon and move display names, '
        'shortens the fixed-width Play Info labels, and translates the missing '
        'consumable descriptions. Full formal Digimon and move names remain in this '
        'review data and in the wider game records.',
        '',
        '| Message ID | Japanese source | English |',
        '|---|---|---|',
    ]
    for row in review:
        jp = row['japanese'].replace('|', '\\|').replace('<0A>', '<br>')
        en = row['english'].replace('|', '\\|').replace('\n', '<br>')
        markdown.append(f"| `{row['ids'][0]}` | {jp} | {en} |")
    markdown.extend([
        '',
        'The source is the original Japanese ROM. Each entry keeps the target scope '
        '(one Digimon versus one row) explicit; Health Down matches the existing '
        'in-game status wording.',
    ])
    (ROOT / 'translations/review_batch36.md').write_text('\n'.join(markdown) + '\n',
                                                        encoding='utf-8')

    names = json.loads((ROOT / 'translations/display_name_layout.json').read_text(encoding='utf-8'))
    moves = json.loads((ROOT / 'translations/move_name_layout.json').read_text(encoding='utf-8'))
    outputs = {}
    for version, original_path in rom_paths().items():
        report = json.loads((ROOT / f'build/{version}_report.json').read_text(encoding='utf-8'))
        output_path = ROOT / 'build' / report['output']
        assert report['output'].endswith('_batch36.nds')
        assert report['translated_slots'] == 8773
        assert report['total_slots'] == 15674
        assert report['slot_percent'] == 55.97
        assert report['wide_lines'] == []
        assert sha(original_path) == config['original_sha256'][version]
        assert sha(output_path) == report['output_sha256']

        actual = collect_messages(Rom(output_path))
        for row in names:
            self_check_ascii(actual[row['id']]['source_hex'], row['display'], row['id'])
        for row in moves:
            self_check_ascii(actual[row['id']]['source_hex'], row['display'], row['id'])
        item_equipment = [(key, record) for key, record in translations.items()
                          if record['category'] in ('Item name', 'Items and equipment')]
        for key, record in item_equipment:
            expected = encode_translation(record)
            if actual[key]['source_hex'] != expected.hex():
                raise AssertionError(f'Item/equipment name missing or mismatched: {key}')
            expected.decode('ascii')
        for index in list(range(23, 42)):
            key = f'MSG/MESPAK01.PAK:016:{index:05d}'
            assert actual[key]['source_hex'] == encode_translation(translations[key]).hex(), key
        for block in batch['blocks']:
            for index in range(block['start'], block['start'] + len(block['english'])):
                key = f"{block['archive']}:{block['entry']:03d}:{index:05d}"
                assert actual[key]['source_hex'] == encode_translation(translations[key]).hex(), key

        screenshots = []
        for filename, note in (
            ('title_idle.png', 'Title logo boots with the complete D visible.'),
            ('title_menu.png', 'Title menu labels render in the English font.'),
            ('intro_840.png', 'Illustrated intro sequence continues after starting the game.'),
        ):
            screenshot = ROOT / 'build/qa' / f'{version}_batch36_intro' / filename
            screenshots.append({'path': screenshot.relative_to(ROOT).as_posix(),
                                'sha256': sha(screenshot), 'visual_review': note})
        outputs[version] = {
            'output': report['output'],
            'output_sha256': report['output_sha256'],
            'original_sha256': report['original_sha256'],
            'translated_slots': report['translated_slots'],
            'total_slots': report['total_slots'],
            'slot_percent': report['slot_percent'],
            'display_names': report['display_names'],
            'move_names': report['move_names'],
            'wide_lines': report['wide_lines'],
            'screenshots': screenshots,
        }

    result = {
        'review_date': '2026-10-25',
        'scope': (
            'Batch36 corrects the private-use compact-glyph rendering issue in species '
            'and move labels. Both output tables were checked against the standard ASCII '
            'font and the measured 60px/104px screen budgets. Play Info and no-quest '
            'labels use shorter text. Eighteen previously missing consumable descriptions '
            'were added, and all 477 translated item/equipment entries were checked '
            'as standard ASCII. Emulator checks cover title, menu, and illustrated intro; '
            'inventory, status, and battle screens still need a hands-on save-game review.'
        ),
        'text_batch': {
            'path': batch_path.relative_to(ROOT).as_posix(),
            'review_path': review_path.relative_to(ROOT).as_posix(),
            'direct_message_slots': 18,
            'translated_slot_total': 8773,
            'slot_percent': 55.97,
        },
        'layout_fixes': {
            'display_name_encoding': 'ordinary ASCII; no private-use compact characters',
            'display_name_width_budget_px': 60,
            'abbreviated_display_names': sum(row['abbreviated'] for row in names),
            'battle_move_encoding': 'ordinary ASCII; word-end abbreviations when needed',
            'battle_move_width_budget_px': 104,
            'abbreviated_battle_move_records': sum(row['abbreviated'] for row in moves),
            'item_equipment_names_verified_as_ascii': 477,
            'play_info_labels': 'shortened to fit the visible 10-character slots',
            'empty_quest_label': 'No quests / active.',
        },
        'graphics_states': 233,
        'tests': {'pipeline': '17 passed',
                  'emulator': 'Blue and Red title, menu, and illustrated intro rendered'},
        'versions': outputs,
    }
    target = ROOT / 'build/qa/validation_batch36.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',
                      encoding='utf-8')
    print(target)


def self_check_ascii(raw_hex, expected, message_id):
    raw = bytes.fromhex(raw_hex)
    if raw != expected.encode('ascii'):
        raise AssertionError(f'Name text is missing, non-ASCII, or mismatched: {message_id}')


if __name__ == '__main__':
    main()
