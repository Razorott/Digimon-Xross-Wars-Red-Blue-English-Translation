"""Build and structurally validate both English ROMs."""
from __future__ import annotations

import collections
import hashlib
import json
import re
import struct
import textwrap
from pathlib import Path

from xros_text import ROOT, Rom, Pak, Messages, rom_paths, display, u32
from xros_font import Font, english_font, compact_native_fullwidth_font
from localize_graphics import localize
from name_layout import apply_display_names, apply_move_names, DISPLAY_BUDGET_PX, MOVE_BUDGET_PX
from xros_program import localize_program
from profile_copyedit import copyedit_profile
from blue_battle_theme import (recolor_blue_ui_panels,
                               recolor_blue_ui_background_palettes)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def crc16(data):
    crc = 0xffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xa001 if crc & 1 else 0)
    return crc


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def current_batch_tag():
    numbers = [int(match.group(1)) for path in (ROOT / 'translations').glob('batch*.json')
               if (match := re.fullmatch(r'batch(\d+)\.json', path.name))]
    if not numbers:
        raise ValueError('No numbered translation batches found')
    return f'batch{max(numbers):02d}'


def collect_messages(rom):
    records = {}
    for name in sorted(rom.files):
        if not name.startswith('MSG/'):
            continue
        pak = Pak(rom.file(name))
        for entry in range(pak.count):
            messages = Messages(pak.file(entry))
            for index, raw in enumerate(messages.raw):
                key = f'{name}:{entry:03d}:{index:05d}'
                records[key] = {'id': key, 'archive': name, 'entry': entry, 'index': index, 'source': display(raw), 'source_hex': raw.hex()}
    return records


def translate_records(records):
    translations = {}
    for path in sorted((ROOT / 'translations').glob('batch*.json')):
        batch = load_json(path)
        for block in batch['blocks']:
            for index, english in enumerate(block['english'], block['start']):
                key = f"{block['archive']}:{block['entry']:03d}:{index:05d}"
                if key not in records:
                    raise ValueError(f'Unknown message ID: {key}')
                if key in translations:
                    raise ValueError(f'Duplicate translation: {key}')
                translations[key] = dict(records[key], english=english, category=block['category'],
                                         sources=block.get('sources', []), review_note=block.get('review_note', ''))
    glossary = load_json(ROOT / 'translations' / 'glossary.json')
    for term in glossary['terms']:
        if not term.get('sources') or any(s not in glossary['sources'] for s in term['sources']):
            raise ValueError(f'Missing glossary source: {term}')
        matches = 0
        for key, record in records.items():
            if record['source'] != term['japanese']:
                continue
            if 'indices' in term and (record['archive'] != 'MSG/MESPAK00.PAK' or record['index'] not in term['indices']):
                continue
            matches += 1
            if key in translations:
                if translations[key]['english'] != term['english']:
                    raise ValueError(f'Conflicting glossary/batch translation: {key}')
                translations[key]['sources'] = [glossary['sources'][s]['url'] for s in term['sources']]
                continue
            translations[key] = dict(record, english=term['english'], category=term['category'], sources=[glossary['sources'][s]['url'] for s in term['sources']])
        if not matches:
            raise ValueError(f'Glossary term has no matching source: {term["japanese"]}')
    # The shipped font lacks several common punctuation glyphs. Normalize to
    # readable equivalents before validation and ROM encoding so they cannot
    # make an otherwise complete translation batch unbuildable.
    punctuation = str.maketrans({'\u2018': "'", '\u2019': "'", ';': ',', '[': '(', ']': ')'})
    for record in translations.values():
        record['english'] = record['english'].translate(punctuation)
    # Observed in DeSmuME: story text advances by a fixed 12px per character,
    # ignoring CWDH proportional advances. Portrait dialogue leaves about 200px
    # for text. Fifteen columns (180px) leave a conservative margin. Preserve
    # deliberate authored line breaks and let the game's existing paging run.
    for record in translations.values():
        if record['category'] in ('opening story','Story and dialogue'):
            record['authored_english'] = record['english']
            record['english'] = '\n'.join('\n'.join(textwrap.wrap(line, width=15)) if line else '' for line in record['english'].split('\n'))
        elif record['category'] == 'Digimon profiles':
            # These encyclopedia blurbs do not use the narrow portrait-dialogue
            # box. Earlier profile batches incorrectly wrapped them at 15
            # columns, creating as many as 20 lines. Reflow to the full 224px
            # text width used by the other UI screens so profile pages stay
            # readable and within the Digidex panel.
            record['authored_english'] = record['english']
            body = ' '.join(record['english'].split())
            body = re.sub(r'(?<=\w)-\s+(?=\w)', '-', body)
            # Early profile batches were authored in narrow columns. Rejoining
            # them can strand a possessive suffix after its apostrophe.
            body = re.sub(r"'\s+s\b", "'s", body)
            body = copyedit_profile(body, record['id'])
            record['english'] = '\n'.join(textwrap.wrap(
                body, width=28, break_long_words=False, break_on_hyphens=False))
    return translations


def encode_translation(record):
    if record.get('runtime_preserved_source_hex'):
        return bytes.fromhex(record['runtime_preserved_source_hex'])
    source = bytes.fromhex(record['source_hex'])
    # Keep message strings in ordinary Shift-JIS ASCII. The experimental
    # private-use compact glyphs are not rendered consistently by every game
    # screen, so display names use measured, readable abbreviations instead.
    text = record.get('runtime_display_english',
                      record.get('display_english', record['english']))
    if not text:
        raise ValueError(f'Empty English: {record["id"]}')
    # Parameter indices are engine substitutions, not literal text. Reordering
    # is allowed for English grammar, but dropping/adding a parameter is not.
    source_parameters = collections.Counter(re.findall(rb'\^[0-9A-Za-z]', source))
    encoded = text.encode('cp932')
    if collections.Counter(re.findall(rb'\^[0-9A-Za-z]', encoded)) != source_parameters:
        raise ValueError(f'Changed substitutions: {record["id"]}')
    if b'\0' in encoded or any(b < 32 and b != 10 for b in encoded):
        raise ValueError(f'Unrecognized English control byte: {record["id"]}')
    if any(b < 32 and b != 10 for b in source):
        raise ValueError(f'Source has unhandled control bytes: {record["id"]}')
    return encoded


def asset_file_id(rom, name):
    if name.startswith('@overlay/'):
        index = int(name.split('/')[1])
        table, size = struct.unpack_from('<II', rom.data, 0x50)
        if not 0 <= index < size // 32:
            raise ValueError('Overlay index outside table')
        return u32(rom.data, table + index * 32 + 24)
    return rom.files[name]


def replace_files(rom, replacements, program=None):
    """Patch in place when a file fits; otherwise use verified trailing padding.

    Every executable and every untouched filesystem file stays at its original
    offset. Only modified FAT entries and the standard header fields change.
    """
    original = rom.data
    if crc16(original[:0x15e]) != struct.unpack_from('<H', original, 0x15e)[0]:
        raise ValueError('Original NDS header CRC does not match')
    out = bytearray(original)
    ends = [u32(original, rom.fat_offset + i * 8 + 4) for i in range(rom.fat_size // 8)]
    used = max(u32(original, 0x80), *ends)
    cursor = (used + 511) & ~511
    operations = []
    for name, payload in sorted(replacements.items()):
        fat_entry = rom.fat_offset + asset_file_id(rom, name) * 8
        old_start, old_end = struct.unpack_from('<II', original, fat_entry)
        if len(payload) <= old_end - old_start:
            start = old_start
        else:
            start = cursor
            end = start + len(payload)
            if end > len(out):
                raise ValueError('Modified files exceed verified cartridge padding')
            if any(byte not in (0, 255) for byte in original[start:end]):
                raise ValueError('Attempt to overwrite non-padding ROM content')
            cursor = (end + 511) & ~511
        out[start:start + len(payload)] = payload
        struct.pack_into('<II', out, fat_entry, start, start + len(payload))
        if name.startswith('@overlay/'):
            slot = u32(original, 0x50) + int(name.split('/')[1]) * 32 + 28
            flags = u32(original, slot)
            if not flags & 0x1000000:
                raise ValueError('Expected compressed overlay')
            struct.pack_into('<I', out, slot, (flags & 0xff000000) | len(payload))
        operations.append({'file': name, 'old_offset': old_start, 'old_size': old_end - old_start, 'new_offset': start, 'new_size': len(payload), 'relocated': start != old_start})
    if program is not None:
        offset=u32(original,0x20);size=u32(original,0x2c)
        if len(program)>size:raise ValueError('Program exceeds original ARM9 slot')
        out[offset:offset+len(program)]=program
        struct.pack_into('<I',out,0x2c,len(program))
    struct.pack_into('<I', out, 0x80, max(used, cursor))
    struct.pack_into('<H', out, 0x15e, crc16(out[:0x15e]))
    return bytes(out), operations


def verify(rom, output_path, replacements, translated, program=None):
    patched = Rom(output_path)
    if patched.files != rom.files or patched.data[12:16] != rom.data[12:16]:
        raise ValueError('File identities or cartridge ID changed')
    for name in rom.files:
        expected = replacements.get(name, rom.file(name))
        if patched.file(name) != expected:
            raise ValueError(f'Filesystem verification failed: {name}')
    # Verify all bytes outside the specific changed ranges against the original,
    # including code, overlays, banner, originals left behind, and unused data.
    restored = bytearray(patched.data)
    for name, data in replacements.items():
        fat_entry = rom.fat_offset + asset_file_id(rom, name) * 8
        start = u32(patched.data, fat_entry)
        if patched.data[start:start + len(data)] != data:
            raise ValueError(f'Asset verification failed: {name}')
        restored[start:start + len(data)] = rom.data[start:start + len(data)]
        restored[fat_entry:fat_entry + 8] = rom.data[fat_entry:fat_entry + 8]
        if name.startswith('@overlay/'):
            slot = u32(rom.data, 0x50) + int(name.split('/')[1]) * 32 + 28
            wanted = (u32(rom.data, slot) & 0xff000000) | len(data)
            if u32(patched.data, slot) != wanted:
                raise ValueError('Overlay compressed size mismatch')
            restored[slot:slot + 4] = rom.data[slot:slot + 4]
    restored[0x80:0x84] = rom.data[0x80:0x84]
    if program is not None:
        offset=u32(rom.data,0x20)
        if patched.data[offset:offset+len(program)]!=program:raise ValueError('Program verification failed')
        restored[offset:offset+len(program)]=rom.data[offset:offset+len(program)]
        restored[0x2c:0x30]=rom.data[0x2c:0x30]
    restored[0x15e:0x160] = rom.data[0x15e:0x160]
    if restored != rom.data:
        raise ValueError('Unexpected changes outside patched assets/header/FAT')
    if crc16(patched.data[:0x15e]) != struct.unpack_from('<H', patched.data, 0x15e)[0]:
        raise ValueError('Built ROM header CRC failed')
    actual = collect_messages(patched)
    original = collect_messages(rom)
    if actual.keys() != original.keys():
        raise ValueError('Message IDs changed')
    for key, record in original.items():
        wanted = encode_translation(translated[key]).hex() if key in translated else record['source_hex']
        if actual[key]['source_hex'] != wanted:
            raise ValueError(f'Message verification failed: {key}')
    original_fonts = Pak(rom.file('FONT_NFTR.PAK'))
    patched_fonts = Pak(patched.file('FONT_NFTR.PAK'))
    for index in range(original_fonts.count):
        old = Font(original_fonts.file(index))
        new = Font(patched_fonts.file(index))
        if any(new.mapping.get(c) != g for c, g in old.mapping.items() if c>=128):
            raise ValueError(f'Original character mapping changed: font {index}')
        compact_codes = {int.from_bytes(chr(c + 0xfee0).encode('cp932'), 'big')
                         for c in range(48,123) if chr(c).isalnum()}
        compact_glyphs = {old.mapping[c] for c in compact_codes if c in old.mapping}
        if any(g in compact_glyphs for c,g in old.mapping.items() if c not in compact_codes):
            raise ValueError(f'Compact Latin glyph shares a non-Latin mapping: font {index}')
        for glyph in old.metrics:
            if glyph in compact_glyphs:
                continue
            if old.metrics[glyph] != new.metrics[glyph]:
                raise ValueError(f'Native font metric changed: font {index}/{glyph}')
            if old.pixels(glyph) != new.pixels(glyph):
                raise ValueError(f'Native glyph changed: font {index}/{glyph}')


def build():
    batch_tag = current_batch_tag()
    config = load_json(ROOT / 'project.json')
    target = ROOT / 'build'
    target.mkdir(exist_ok=True)
    total_report = {}
    for version, path in rom_paths().items():
        rom = Rom(path)
        if sha(rom.data) != config['original_sha256'][version]:
            raise ValueError(f'Unexpected original {version} ROM checksum')
        all_records = collect_messages(rom)
        translated = translate_records(all_records)
        fonts = Pak(rom.file('FONT_NFTR.PAK'))
        changed_fonts = {}
        alias_report = []
        for index in range(fonts.count):
            standard, count = english_font(fonts.file(index))
            # Both DigiDex and party/status screens use these shared names.
            # Keep native fullwidth glyph indices while making their ink and
            # metrics compact enough for the narrow Western-name fields.
            new_font, compact_count = compact_native_fullwidth_font(standard)
            if count or compact_count:
                changed_fonts[index] = new_font
            alias_report.append({'font': index, 'english_glyphs_added': count,
                                 'native_fullwidth_glyphs_compacted': compact_count})
        display_fonts = [Font(changed_fonts[i]) for i in (0, 5)]
        name_layout = apply_display_names(translated,display_fonts)
        move_layout = apply_move_names(translated,display_fonts)
        if any(row['display_width_px']>DISPLAY_BUDGET_PX for row in name_layout):
            raise ValueError('A Digimon display name exceeds its measured HUD budget')
        if version == 'blue':
            (ROOT/'translations/display_name_layout.json').write_text(
                json.dumps(name_layout,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (ROOT/'translations/move_name_layout.json').write_text(
                json.dumps(move_layout,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        edits = collections.defaultdict(lambda: collections.defaultdict(dict))
        for row in translated.values():
            edits[row['archive']][row['entry']][row['index']] = encode_translation(row)
        replacements = {}
        for name, entries in edits.items():
            pak = Pak(rom.file(name))
            changed = {entry: Messages(pak.file(entry)).rebuild(strings) for entry, strings in entries.items()}
            replacements[name] = pak.rebuild(changed)
        replacements['FONT_NFTR.PAK'] = fonts.rebuild(changed_fonts)
        graphics, graphics_manifest = localize(rom, preview=(version == 'blue'))
        # Blue-only UI theme: carry the requested palette changes into this
        # and later Blue builds. Red remains on its original interface palette.
        theme_enabled = version == 'blue' and int(batch_tag.removeprefix('batch')) >= 122
        if theme_enabled:
            graphics['SPR_NCLR.PAK'] = recolor_blue_ui_panels(
                rom, preview=True)
            graphics['BG_NCLR.PAK'] = recolor_blue_ui_background_palettes(
                rom, preview=True)
        battle_palette_changes = []
        if version == 'blue' and int(batch_tag.removeprefix('batch')) >= 124:
            from battle_overlay_theme import recolor_battle_overlay
            graphics['@overlay/0'], battle_palette_changes = recolor_battle_overlay(rom)
        if version == 'red' and int(batch_tag.removeprefix('batch')) >= 124:
            from red_base_theme import recolor_red_base
            graphics['MAP_NCLR.PAK'] = recolor_red_base(rom)
        if version == 'red' and int(batch_tag.removeprefix('batch')) >= 125:
            from red_base_theme import recolor_red_formation_reserve
            graphics['BG_NCLR.PAK'] = recolor_red_formation_reserve(rom)
        replacements.update(graphics)
        font = Font(changed_fonts[0])
        wide_lines = []
        missing = []
        for key, record in translated.items():
            for line in record['english'].split('\n'):
                sample = re.sub(r'\^[0-9A-Za-z]', '', line)
                try:
                    # Validate glyph availability, then use the observed fixed
                    # cell advance for story and a screen-width ceiling for UI.
                    for char in sample:
                        font.advance(char)
                    width = len(sample) * (12 if record['category'] in ('opening story','Story and dialogue') else 8)
                except ValueError as exc:
                    missing.append({'id': key, 'error': str(exc)})
                    continue
                budget = 180 if record['category'] in ('opening story','Story and dialogue') else 224
                if width > budget:
                    wide_lines.append({'id': key, 'pixels': width, 'line': line})
        if missing:
            raise ValueError(f'Characters missing from main font: {missing}')
        if wide_lines:
            raise ValueError(f'Lines exceed the configured width budget: {wide_lines}')
        program, program_manifest = localize_program(rom, preview=(version == 'blue'))
        output, operations = replace_files(rom, replacements, program)
        output_path = target / f'Digimon_Super_Xros_Wars_{version.title()}_English_{batch_tag}.nds'
        output_path.write_bytes(output)
        verify(rom, output_path, replacements, translated, program)
        preserved = [r for r in translated.values() if r.get('runtime_preserved_source_hex')]
        effective = [r for r in translated.values() if not r.get('runtime_preserved_source_hex')]
        categories = dict(collections.Counter(r['category'] for r in effective))
        report = {'version': version, 'translated_slots': len(effective), 'translation_proposals': len(translated), 'runtime_preserved_slots': len(preserved), 'total_slots': len(all_records), 'slot_percent': round(100 * len(effective) / len(all_records), 2), 'proposal_percent': round(100 * len(translated) / len(all_records), 2), 'categories': categories, 'output': output_path.name, 'original_sha256': sha(rom.data), 'output_sha256': sha(output), 'structural_validation': 'passed: all message slots, filesystem files, protected Japanese glyphs, and bytes outside declared edits', 'emulator_validation': 'pending: no in-emulator screenshot verification for this checksum', 'graphics_translation': {'states':len(graphics_manifest),'manifest':'translations/graphics_manifest.json'}, 'display_names':{'count':len(name_layout),'abbreviated':sum(x['abbreviated'] for x in name_layout),'runtime_preserved':len(preserved),'manifest':'translations/display_name_layout.json'}, 'move_names':{'count':len(move_layout),'max_width_px':max(x['display_width_px'] for x in move_layout),'width_budget_px':MOVE_BUDGET_PX,'manifest':'translations/move_name_layout.json'}, 'dialogue_font': 4, 'story_wrap_columns': 15, 'story_cell_advance_px': 12, 'wide_lines': wide_lines, 'fonts': alias_report, 'files': operations}
        report['program_strings']=len(program_manifest)
        report['battle_overlay_palette_changes'] = battle_palette_changes
        report['red_sky_fort_theme'] = 'MAP_NCLR entries 12, 15, 18' if version == 'red' and int(batch_tag.removeprefix('batch')) >= 124 else 'not applied'
        report['program_validation']='All decompressed instructions and addresses unchanged; only declared string slots and SDK compressed-end metadata differ.'
        report['blue_ui_palette_theme'] = {'status': 'applied' if theme_enabled else 'not applied'}
        for archive, label in [('SPR_NCLR.PAK', 'sprite_palette_entries'),
                               ('BG_NCLR.PAK', 'background_palette_entries')]:
            original = Pak(rom.file(archive))
            edited = Pak(graphics[archive]) if theme_enabled else original
            report['blue_ui_palette_theme'][label] = [
                i for i in range(original.count) if original.file(i) != edited.file(i)]
        report['blue_ui_palette_theme']['emulator_screenshot_review'] = 'pending'
        (target / f'{version}_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        total_report[version] = report
        if version == 'blue':
            write_review(translated, batch_tag)
    (target / 'progress.json').write_text(json.dumps(total_report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({v: {k: r[k] for k in ['translated_slots', 'total_slots', 'slot_percent', 'categories', 'wide_lines', 'files']} for v, r in total_report.items()}, ensure_ascii=False, indent=2))


def write_review(translated, batch_tag):
    def cell(text):
        return text.replace('|', '\\|').replace('\n', '<br>').replace('<0A>', '<br>')
    lines = [f'# English translation through {batch_tag}', '', 'Generated by `tools/build.py`. Original text is preserved alongside English. See checksum-bound emulator QA for reviewed screens.', '', '| String ID | Japanese | English | Source / review note |', '| --- | --- | --- | --- |']
    for key, row in sorted(translated.items()):
        evidence = ', '.join(row.get('sources', []))
        note = ' '.join(x for x in (row.get('review_note', ''), row.get('runtime_preserved_reason', '')) if x)
        source_note = ' '.join(x for x in (evidence, note) if x)
        lines.append(f'| `{key}` | {cell(row["source"])} | {cell(row["english"])} | {cell(source_note)} |')
    (ROOT / 'translations' / f'review_{batch_tag}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    with (ROOT / 'extracted' / f'translated_{batch_tag}.jsonl').open('w', encoding='utf-8') as f:
        for key, row in sorted(translated.items()):
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    build()
