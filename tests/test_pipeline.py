import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from xros_text import Rom, Pak, Messages, rom_paths, lzss_encode, lzss_decode
from xros_font import Font, english_font, compact_native_fullwidth_font
from build import collect_messages, translate_records, encode_translation, replace_files
from name_layout import apply_display_names, apply_move_names, DISPLAY_BUDGET_PX, MOVE_BUDGET_PX
from graphics import map_info, render_cell, render_map
from localize_graphics import (CAPTION_HIGHLIGHTS, CAPTIONS, caption,
                               independent_cells, localize)
from blue_battle_theme import (UI_PANEL_SPRITES, UI_BG_PALETTES,
                               recolor_blue_ui_panels,
                               recolor_blue_ui_background_palettes)
from PIL import Image


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = Rom(rom_paths()['blue'])
        cls.records = collect_messages(cls.rom)

    def test_every_archive_round_trips_including_compressed_entries(self):
        for name in self.rom.files:
            data = self.rom.file(name)
            if data[4:8] == b'2.01':
                self.assertEqual(Pak(data).rebuild({}), data, name)

    def test_every_message_table_round_trips_without_translation(self):
        for name in self.rom.files:
            if name.startswith('MSG/'):
                pak = Pak(self.rom.file(name))
                for index in range(pak.count):
                    data = pak.file(index)
                    self.assertEqual(Messages(data).rebuild({}), data, (name, index))

    def test_appended_menu_messages_keep_existing_ids_and_control_bytes(self):
        archive_data = self.rom.file('MSG/MESPAK01.PAK')
        archive = Pak(archive_data)
        source = Messages(archive.file(21))
        old_messages = list(source.raw)
        added = [b'Wireless Battle', b'Battle a friend over DS Wireless.']
        replacement = source.append(added)
        extended = Messages(replacement)
        self.assertEqual(extended.count, source.count + len(added))
        self.assertEqual(extended.raw[:source.count], old_messages)
        self.assertEqual(extended.raw[source.count:], added)
        self.assertEqual(archive.file(21), source.data)
        rebuilt = Pak(archive.rebuild({21: replacement}, compress=True))
        self.assertEqual(rebuilt.file(21), replacement)
        for index in range(archive.count):
            if index != 21:
                self.assertEqual(rebuilt.file(index), archive.file(index), index)

    def test_substitutions_cannot_be_dropped_or_added(self):
        source = {'id': 'fixture', 'source_hex': b'^0 / ^1'.hex()}
        with self.assertRaisesRegex(ValueError, 'Changed substitutions'):
            encode_translation(dict(source, english='^0 only'))
        with self.assertRaisesRegex(ValueError, 'Changed substitutions'):
            encode_translation(dict(source, english='^0 ^1 ^2'))
        self.assertTrue(encode_translation(dict(source, english='^1 then ^0')))

    def test_unknown_control_bytes_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unhandled control'):
            encode_translation({'id': 'fixture', 'source_hex': b'hello\x01'.hex(), 'english': 'hello'})
        with self.assertRaisesRegex(ValueError, 'control byte'):
            encode_translation({'id': 'fixture', 'source_hex': b'hello'.hex(), 'english': 'hello\0'})

    def test_bad_offsets_are_rejected(self):
        data = bytes.fromhex('0000000001000000ffffffff')
        with self.assertRaises(ValueError):
            Messages(data)

    def test_english_spaces_and_apostrophes_have_valid_glyphs(self):
        encoded = encode_translation({'id': 'fixture', 'source_hex': b'aa'.hex(), 'english': 'a a'})
        self.assertEqual(encoded, b'a a')
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        for index in (0, 3, 4, 5, 6, 7):
            font = Font(english_font(pak.file(index))[0])
            glyph = font.glyph_index(' ')
            self.assertIsNotNone(glyph)
            self.assertFalse(any(font.pixels(glyph)), index)
            self.assertIsNotNone(font.glyph_index("'"), index)
            self.assertTrue(any(font.pixels(font.glyph_index("'"))), index)

    def test_western_display_names_fit_narrow_hud_and_keep_formal_names(self):
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        fonts = [Font(compact_native_fullwidth_font(english_font(pak.file(i))[0])[0]) for i in (0, 5)]
        translations = translate_records(self.records)
        manifest = apply_display_names(translations, fonts)
        self.assertGreater(len(manifest), 400)
        self.assertTrue(all(row['display_width_px'] <= DISPLAY_BUDGET_PX for row in manifest))
        armadillo = next(row for row in manifest if row['formal'] == 'Armadillomon')
        self.assertEqual(armadillo['display'], 'Armadillo')
        self.assertTrue(armadillo['abbreviated'])
        self.assertEqual(translations[armadillo['id']]['formal_english'], 'Armadillomon')
        for full,suffix in [('PawnChessmon WH','WH'),('SkullKnightmon BR','BR')]:
            row=next(row for row in manifest if row['formal']==full)
            self.assertTrue(row['display'].endswith(suffix),row)
        self.assertEqual(translations[armadillo['id']]['display_english'], 'Armadillo')
        self.assertTrue(armadillo['applied'])
        self.assertFalse(armadillo['runtime_preserved'])
        self.assertEqual(encode_translation(translations[armadillo['id']]).decode('cp932'),
                         'Ａｒｍａｄｉｌｌｏ')
        for font in fonts:
            for char in armadillo['display']:
                self.assertIsNotNone(font.glyph_index(char))

    def test_digidex_display_names_use_two_byte_renderable_latin(self):
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        fonts = [Font(compact_native_fullwidth_font(english_font(pak.file(i))[0])[0]) for i in (0, 5)]
        translations = translate_records(self.records)
        manifest = apply_display_names(translations, fonts)
        self.assertEqual(len(manifest), 472)
        for row in manifest:
            record = translations[row['id']]
            encoded = encode_translation(record)
            self.assertEqual(len(encoded), 2 * len(row['display']), row['id'])
            self.assertTrue(row['display'].isascii() and row['display'].isalnum(), row['id'])
            self.assertNotEqual(encoded, bytes.fromhex(record['source_hex']), row['id'])
            for font in fonts:
                self.assertLessEqual(sum(font.advance(char) for char in encoded.decode('cp932')),
                                     DISPLAY_BUDGET_PX, row['id'])

    def test_fullwidth_names_preserve_saved_japanese_nicknames(self):
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        for index in (0,5):
            original=Font(pak.file(index))
            compact=Font(compact_native_fullwidth_font(english_font(pak.file(index))[0])[0])
            for char in 'カブテリモン':
                glyph=original.glyph_index(char)
                self.assertEqual(compact.glyph_index(char),glyph)
                self.assertEqual(compact.pixels(glyph),original.pixels(glyph))
                self.assertEqual(compact.metrics[glyph],original.metrics[glyph])
            self.assertEqual(compact.glyph_index('Ａ'),original.glyph_index('Ａ'))
            self.assertEqual(compact.pixels(compact.glyph_index('Ａ')),
                             compact.pixels(compact.glyph_index('A')))

    def test_battle_move_names_fit_the_list(self):
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        fonts = [Font(english_font(pak.file(i))[0]) for i in (0, 5)]
        translations = translate_records(self.records)
        manifest = apply_move_names(translations, fonts)
        self.assertGreater(len(manifest), 700)
        self.assertTrue(all(row['display_width_px'] <= MOVE_BUDGET_PX for row in manifest))
        self.assertTrue(any(row['english'] == 'Starlight Explosion' for row in manifest))
        for row in manifest:
            encoded = encode_translation(translations[row['id']])
            self.assertEqual(encoded.decode('ascii'), row['display'])

    def test_name_and_move_labels_use_renderable_encodings(self):
        pak = Pak(self.rom.file('FONT_NFTR.PAK'))
        fonts = [Font(compact_native_fullwidth_font(english_font(pak.file(i))[0])[0]) for i in (0, 5)]
        translations = translate_records(self.records)
        names = apply_display_names(translations, fonts)
        moves = apply_move_names(translations, fonts)
        for row in names + moves:
            encoded = encode_translation(translations[row['id']])
            if 'formal' in row:
                self.assertEqual(len(encoded), 2 * len(row['display']))
                self.assertEqual(translations[row['id']]['display_english'], row['display'])
            else:
                self.assertEqual(encoded.decode('ascii'), row['display'])
            self.assertNotIn(b'\xf0', encoded)

    def test_digidex_profiles_use_the_full_ui_width(self):
        translations = translate_records(self.records)
        profiles = [row for row in translations.values()
                    if row['category'] == 'Digimon profiles']
        self.assertEqual(len(profiles), 394)
        for row in profiles:
            lines = row['english'].split('\n')
            self.assertTrue(all(len(line) <= 28 for line in lines), row['id'])
            self.assertLessEqual(len(lines), 10, row['id'])
            self.assertFalse(any(line in ('.', ',', ';', ':') for line in lines), row['id'])
            self.assertNotRegex(row['english'],r"'\s+s\b",row['id'])
            self.assertNotIn("'",row['english'],row['id'])
            self.assertNotRegex(row['english'],r'\w+-\s+\w+',row['id'])
            for japanese_only in ('Tailmon','Vamdemon','Megalogrowmon',
                                  'Mugendramon','Chimairamon','XV-mon'):
                self.assertNotIn(japanese_only,row['english'],row['id'])
        self.assertIn('Digi-Entelecheia',
                      translations['MSG/MESPAK03.PAK:000:00003']['english'])
        for entry,index in ((1,60),(1,61)):
            profile=translations[f'MSG/MESPAK03.PAK:{entry:03d}:{index:05d}']['english']
            self.assertIn('ExVeemon',profile)
            self.assertIn('Stingmon',profile)
            self.assertNotIn('XV-mon',profile)

    def test_play_info_and_empty_quest_labels_fit_their_slots(self):
        batch = json.loads((Path(__file__).resolve().parents[1] /
                            'translations/batch02.json').read_text(encoding='utf-8'))
        texts = {}
        for block in batch['blocks']:
            if block['archive'] == 'MSG/MESPAK01.PAK' and block['entry'] == 16:
                for index, text in enumerate(block['english'], block['start']):
                    texts[index] = text
        for index in range(23, 41):
            self.assertTrue(all(len(line) <= 10 for line in texts[index].split('\n')),
                            (index, texts[index]))
        self.assertEqual(texts[41], 'No quests\nactive.')

    def test_inventory_consumable_descriptions_are_translated(self):
        translations = translate_records(self.records)
        for entry, start, end in ((28, 32, 50),):
            for index in range(start, end):
                key = f'MSG/MESPAK04.PAK:{entry:03d}:{index:05d}'
                self.assertIn(key, translations)
                self.assertEqual(translations[key]['category'], 'Move and item descriptions')

    def test_item_and_equipment_names_remain_plain_ascii(self):
        translations = translate_records(self.records)
        rows = [record for record in translations.values()
                if record['category'] in ('Item name', 'Items and equipment')]
        self.assertGreater(len(rows), 400)
        for record in rows:
            encode_translation(record).decode('ascii')

    def test_digixross_descriptions_keep_terminology_and_three_line_layout(self):
        review=json.loads((Path(__file__).resolve().parents[1]/
                           'translations/review_batch12.json').read_text(encoding='utf-8'))
        descriptions=[row for row in review
                      if row['category']=='Move and item descriptions'
                      and row['japanese'].startswith('デジクロスで')]
        self.assertEqual(len(descriptions),202)
        for row in descriptions:
            self.assertTrue(row['english'].startswith('DigiXross:'),row['ids'])
            lines=row['english'].split('\n')
            self.assertLessEqual(len(lines),3,row['ids'])
            self.assertTrue(all(len(line)<=28 for line in lines),row['ids'])

    def test_every_translation_preserves_parameters(self):
        for record in translate_records(self.records).values():
            encode_translation(record)

    def test_rom_growth_does_not_overwrite_nonpadding(self):
        file = 'FONT_NFTR.PAK'
        # A deliberately oversized replacement cannot escape the verified
        # cartridge padding or overwrite code/another filesystem file.
        with self.assertRaisesRegex(ValueError, 'exceed verified'):
            replace_files(self.rom, {file: bytes(len(self.rom.data))})

    def test_native_lzss_encoder_handles_ring_wrap_and_mixed_literals(self):
        data = bytes(range(256)) * 3 + (b'Xros Wars!\x00' * 400) + bytes(range(255, -1, -1))
        self.assertEqual(lzss_decode(lzss_encode(data), len(data)), data)

    def test_repacked_animation_cell_does_not_change_other_banks(self):
        index = 124  # DigiLab labels share native graphics data.
        nc = Pak(self.rom.file('SPR_NCGR.PAK')).file(index)
        cl = Pak(self.rom.file('SPR_NCLR.PAK')).file(index)
        ce = Pak(self.rom.file('SPR_NCER.PAK')).file(index)
        original_other = render_cell(nc, cl, ce, 17)
        original_icon = render_cell(nc, cl, ce, 0)
        blank = Image.new('RGBA', render_cell(nc, cl, ce, 16).size)
        nc2, ce2 = independent_cells(nc, cl, ce, {16: blank})
        self.assertIsNone(render_cell(nc2, cl, ce2, 16).getbbox())
        self.assertEqual(render_cell(nc2, cl, ce2, 17).tobytes(), original_other.tobytes())
        self.assertEqual(render_cell(nc2, cl, ce2, 0).tobytes(), original_icon.tobytes())

    def test_blue_ui_theme_changes_only_allowlisted_palette_entries(self):
        original_sprites = Pak(self.rom.file('SPR_NCLR.PAK'))
        themed_sprites = Pak(recolor_blue_ui_panels(self.rom))
        self.assertTrue(all(themed_sprites.file(i) != original_sprites.file(i)
                            for i in UI_PANEL_SPRITES))
        self.assertEqual(themed_sprites.file(1971), original_sprites.file(1971))
        self.assertEqual(themed_sprites.file(2247), original_sprites.file(2247))

        original_bg = Pak(self.rom.file('BG_NCLR.PAK'))
        themed_bg = Pak(recolor_blue_ui_background_palettes(self.rom))
        self.assertNotEqual(themed_bg.file(3), original_bg.file(3))
        self.assertNotEqual(themed_bg.file(84), original_bg.file(84))
        self.assertNotEqual(themed_bg.file(228), original_bg.file(228))
        self.assertEqual(themed_bg.file(51), original_bg.file(51))
        self.assertEqual(themed_bg.file(31), original_bg.file(31))
        changed = {i for i in range(original_bg.count)
                   if themed_bg.file(i) != original_bg.file(i)}
        self.assertTrue(changed.issubset(set(UI_BG_PALETTES)))


    def test_intro_caption_encoder_preserves_red_emphasis_palette(self):
        bg_nc = Pak(self.rom.file('BG_NCGR.PAK')).file(33)
        bg_ns = Pak(self.rom.file('BG_NSCR.PAK')).file(33)
        intro_palette = Pak(self.rom.file('BG_NCLR.PAK')).file(31)
        nc, ns, _ = caption(bg_nc, intro_palette, bg_ns, CAPTIONS[33],
                            highlights=CAPTION_HIGHLIGHTS[33])
        rendered = render_map(nc, intro_palette, ns, transparent=True)
        red_pixels = sum(1 for pixel in rendered.getdata()
                         if pixel[0] > 200 and pixel[1] < 100 and pixel[2] < 80)
        self.assertGreater(red_pixels, 100)
        self.assertTrue(any(entry >> 12 == 1 for entry in map_info(ns)[2]))

    def test_action_ring_and_back_badges_keep_native_frames_and_attack_kanji(self):
        replacements, manifest = localize(self.rom)
        original_ncgr = Pak(self.rom.file('SPR_NCGR.PAK'))
        original_ncer = Pak(self.rom.file('SPR_NCER.PAK'))
        edited_ncgr = Pak(replacements['SPR_NCGR.PAK'])
        edited_ncer = Pak(replacements['SPR_NCER.PAK'])
        entries = {(row['entry'], row['bank']) for row in manifest
                   if row['archive'].startswith('SPR_')}
        self.assertTrue(all((1971, bank) in entries for bank in range(21, 33)))
        self.assertTrue(all((1987, bank) in entries for bank in (10, 11)))
        self.assertFalse(any(entry == 1990 for entry, _ in entries))
        self.assertEqual(edited_ncgr.file(1990), original_ncgr.file(1990))
        self.assertEqual(edited_ncer.file(1990), original_ncer.file(1990))
        for bank in range(21, 33):
            self.assertNotEqual(
                render_cell(edited_ncgr.file(1971),
                            Pak(self.rom.file('SPR_NCLR.PAK')).file(1971),
                            edited_ncer.file(1971), bank).tobytes(),
                render_cell(original_ncgr.file(1971),
                            Pak(self.rom.file('SPR_NCLR.PAK')).file(1971),
                            original_ncer.file(1971), bank).tobytes())
        for bank in (10, 11):
            before = render_cell(original_ncgr.file(1987),
                                 Pak(self.rom.file('SPR_NCLR.PAK')).file(1987),
                                 original_ncer.file(1987), bank)
            after = render_cell(edited_ncgr.file(1987),
                                Pak(self.rom.file('SPR_NCLR.PAK')).file(1987),
                                edited_ncer.file(1987), bank)
            self.assertNotEqual(before.tobytes(), after.tobytes())
            self.assertEqual(before.crop((47, 4, 66, 25)).tobytes(),
                             after.crop((47, 4, 66, 25)).tobytes())


    def test_battle_overlay_preserves_all_bytes_outside_ui_ramps(self):
        import struct
        from battle_overlay_theme import recolor_battle_overlay, PALETTE_START, PALETTE_SIZE, codeCompression
        packed, changes = recolor_battle_overlay(self.rom)
        a, b = struct.unpack_from('<II', self.rom.data, self.rom.fat_offset)
        original = codeCompression.decompress(self.rom.data[a:b])
        edited = bytearray(codeCompression.decompress(packed))
        self.assertTrue(changes)
        self.assertEqual(len(edited), len(original))
        for row in changes:
            self.assertTrue(PALETTE_START <= row['offset'] < PALETTE_START + PALETTE_SIZE)
        edited[PALETTE_START:PALETTE_START + PALETTE_SIZE] = original[PALETTE_START:PALETTE_START + PALETTE_SIZE]
        self.assertEqual(edited, original)
        built, _ = replace_files(self.rom, {'@overlay/0': packed})
        table = struct.unpack_from('<I', built, 0x50)[0]
        self.assertEqual(struct.unpack_from('<I', built, table + 28)[0] & 0xffffff, len(packed))

    def test_red_interior_theme_changes_only_selected_map_palettes(self):
        from red_base_theme import recolor_red_base, SKY_FORT_PALETTES
        red = Rom(rom_paths()['red'])
        original = Pak(red.file('MAP_NCLR.PAK'))
        edited = Pak(recolor_red_base(red))
        self.assertEqual(original.count, edited.count)
        changed = {i for i in range(original.count) if original.file(i) != edited.file(i)}
        self.assertEqual(changed, set(SKY_FORT_PALETTES))


if __name__ == '__main__':
    unittest.main()
