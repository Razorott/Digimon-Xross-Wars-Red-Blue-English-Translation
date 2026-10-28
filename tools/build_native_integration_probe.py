"""Install the native component in separate, explicitly incomplete test ROMs.

Reserves memory through the original main-arena low literal. Preserves legacy
wireless globals, SDK instructions, callback tables and the four menu actions.
Not a playable battle build. Stable ROMs and original cartridges are untouched.
"""
import hashlib
import argparse
import json
import struct
import subprocess
from xros_text import ROOT, Messages, Pak, Rom, u32
from xros_program import codeCompression
from build import replace_files, crc16

OVERLAY_BASE = 0x0221BF80
MODULE_BASE = 0x022234A0
ARENA_LITERAL = 0x02005E70
CTOR_SLOT = 0x0221FF1C


def sha(data):
    return hashlib.sha256(data).hexdigest()


def expand_arm9_slot(data, amount):
    """Insert verified bytes at the ARM9/ARM7 boundary for a larger test ARM9.

    Every subsequent ROM offset is updated, and a reverse transform must
    reproduce the source cartridge byte-for-byte. This is used only for
    isolated experimental ROMs when ARM9 compression grows beyond its slot.
    """
    if amount <= 0:
        raise ValueError('Expansion must be positive')
    old_arm9_offset, old_arm9_size = u32(data, 0x20), u32(data, 0x2C)
    insertion = old_arm9_offset + old_arm9_size
    old_arm7_offset = u32(data, 0x30)
    if insertion > old_arm7_offset:
        raise ValueError('ARM9 overlaps ARM7; cannot expand the test slot')
    fat_offset, fat_size = u32(data, 0x48), u32(data, 0x4C)
    for i in range(fat_size // 8):
        start, end = struct.unpack_from('<II', data, fat_offset + i * 8)
        if start < insertion < end:
            raise ValueError(f'FAT file {i} crosses ARM9 insertion point')

    expanded = bytearray(data[:insertion] + b'\0' * amount + data[insertion:])
    for header_offset in (0x30, 0x40, 0x48, 0x50, 0x58, 0x68, 0x160):
        value = u32(data, header_offset)
        if value >= insertion:
            struct.pack_into('<I', expanded, header_offset, value + amount)
    struct.pack_into('<I', expanded, 0x2C, old_arm9_size + amount)
    new_fat_offset = u32(expanded, 0x48)
    for i in range(fat_size // 8):
        entry = new_fat_offset + i * 8
        start, end = struct.unpack_from('<II', expanded, entry)
        if start >= insertion:
            start += amount
            end += amount
        elif end > insertion:
            end += amount
        struct.pack_into('<II', expanded, entry, start, end)
    struct.pack_into('<I', expanded, 0x80, u32(data, 0x80) + amount)
    struct.pack_into('<H', expanded, 0x15E, crc16(expanded[:0x15E]))

    reversed_data = bytearray(expanded)
    del reversed_data[insertion:insertion + amount]
    reversed_data[:0x200] = data[:0x200]
    reversed_data[fat_offset:fat_offset + fat_size] = data[fat_offset:fat_offset + fat_size]
    if reversed_data != data:
        raise AssertionError('ARM9 slot expansion is not reversible')
    return bytes(expanded), {'insertion_offset': hex(insertion),
                             'bytes_inserted': amount,
                             'arm9_size_before': old_arm9_size,
                             'arm9_size_after': old_arm9_size + amount,
                             'reverse_verified': True}


def elf_image(path):
    data = path.read_bytes()
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert h[0][:6] == b'\x7fELF\x01\x01' and h[2] == 40
    sections = [struct.unpack_from('<10I', data, h[6] + i * h[11]) for i in range(h[12])]
    segments = []
    # lld may map ELF headers below a non-page-aligned link address. The game
    # receives allocated sections only, never those ELF headers or page padding.
    for _, kind, flags, address, offset, size, _, _, _, _ in sections:
        if flags & 2 and size:
            assert MODULE_BASE <= address < address + size < MODULE_BASE + 0x10000
            segments.append((address, b'' if kind == 8 else data[offset:offset + size], size))
    file_end = max(a + len(payload) for a, payload, size in segments)
    memory_end = max(a + size for a, payload, size in segments)
    image = bytearray(file_end - MODULE_BASE)
    for address, payload, _ in segments:
        image[address - MODULE_BASE:address - MODULE_BASE + len(payload)] = payload
    symbols = {}
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for offset in range(section[4], section[4] + section[5], section[9]):
            name, value, _, _, _, index = struct.unpack_from('<IIIBBH', data, offset)
            symbol = names[name:].split(b'\0', 1)[0].decode('ascii')
            if index and symbol.startswith('xwb_'):
                symbols[symbol] = value
    assert MODULE_BASE <= symbols['xwb_overlay_boot'] < file_end
    return bytes(image), memory_end, symbols


def compile_bridge(directory, include_transport=False, extended_order=False, include_session=False):
    zig = ROOT / '.tools/ziglang/ziglang/zig.exe'
    objects = []
    sources = ['wireless_battle', 'wireless_party', 'wireless_actor_adapter',
               'wireless_game_bridge']
    if include_session:
        sources.append('wireless_linkbox')
    if include_transport:
        sources.append('wireless_transport')
    if include_session:
        if not include_transport:
            raise ValueError('session controller requires the native transport adapter')
        sources.append('wireless_session')
    for source in sources:
        output = directory / (source + '.o')
        defines = (['-DXWB_EXTENDED_ORDER'] if extended_order else []) + (['-DXWB_SESSION_CONTROLLER'] if include_session else [])
        subprocess.run([str(zig), 'cc', '-target', 'arm-freestanding-eabi',
            '-mcpu=arm946e_s', '-marm', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-Os', '-Wall', '-Wextra', '-Werror', *defines, '-c', str(ROOT / f'native/{source}.c'),
            '-o', str(output)], check=True, cwd=ROOT)
        objects.append(str(output))
    elf = directory / 'game_bridge.elf'
    subprocess.run([str(zig), 'build-exe', *objects, '-target', 'arm-freestanding-eabi',
        '-mcpu', 'arm946e_s', '-O', 'ReleaseSmall', '-fno-compiler-rt', '-fno-entry',
        '--no-gc-sections', '-fno-strip', '--script', str(ROOT / 'native/wireless_game_bridge.ld'),
        '-femit-bin=' + str(elf)], check=True, cwd=ROOT)
    return elf_image(elf)


def install_remote_actor_scene_hooks(overlay, base, symbols):
    """Populate six remote opponent records before actor finalization."""
    data = bytearray(overlay)
    edits = []

    def branch(site, target):
        delta = target - (site + 8)
        assert not (delta & 3) and -(1 << 25) <= delta < (1 << 25)
        return 0xEA000000 | ((delta >> 2) & 0x00FFFFFF)

    for site, expected, symbol, label in (
        (0x022169EC, 0xE59F6028, 'xwb_prepare_remote_setup_hook',
         'populate remote actor records before actor finalization'),
        (0x02216A10, 0xE3540009, 'xwb_actor_setup_limit_hook',
         'finalize twelve actors only after remote team preparation'),
    ):
        offset = site - base
        actual = u32(data, offset)
        assert actual == expected, f'{label} at {site:#x}: {actual:#010x}'
        replacement = branch(site, symbols[symbol])
        struct.pack_into('<I', data, offset, replacement)
        edits.append({'address': hex(site), 'label': label,
                      'original': hex(actual), 'replacement': hex(replacement),
                      'target': hex(symbols[symbol])})
    return bytes(data), edits


def patch_program(rom, arena_low, linkbox_hook=None, label_hook=None,
                  linkbox_entry=False, selection_hooks=None):
    offset, _, ram, arm9_size = struct.unpack_from('<4I', rom.data, 0x20)
    original = codeCompression.decompress(rom.data[offset:offset + arm9_size])
    arena_offset = ARENA_LITERAL - ram
    assert u32(original, arena_offset) == MODULE_BASE
    data = bytearray(original)
    struct.pack_into('<I', data, arena_offset, arena_low)
    hook_report = None
    menu_patches = []
    def write_word(address, expected, replacement, label):
        offset = address - ram
        found = u32(original, offset)
        assert found == expected, f'{label} at {address:#x}: {found:#010x}'
        struct.pack_into('<I', data, offset, replacement)
        menu_patches.append({'address': hex(address), 'label': label,
                             'original': hex(found), 'replacement': hex(replacement)})
    if linkbox_hook is not None:
        linkbox_site = 0x020D4BA8
        linkbox_resume = 0x020D4BAC
        linkbox_address = linkbox_site - ram
        original_instruction = u32(original, linkbox_address)
        assert original_instruction == 0xE92D41F0, hex(original_instruction)
        branch_delta = linkbox_hook - (linkbox_site + 8)
        assert not (branch_delta & 3) and -(1 << 25) <= branch_delta < (1 << 25)
        struct.pack_into('<I', data, linkbox_address, 0xEB000000 | ((branch_delta >> 2) & 0x00FFFFFF))
        hook_report = {'site': hex(linkbox_site), 'resume': hex(linkbox_resume),
                       'target': hex(linkbox_hook), 'original_instruction': hex(original_instruction)}
    if linkbox_entry:
        # Child constructor: grow the row allocation/clear, initialize and
        # destroy five rows. Move the first row up four units so row five lands
        # at the current fourth-row position without changing row spacing.
        for address, expected, replacement, label in (
            (0x020D4260, 0xE3A01D05, 0xE3A01E19, 'fifth-row allocation size'),
            (0x020D4288, 0xE3A02D05, 0xE3A02E19, 'fifth-row clear size'),
            (0x020D42DC, 0xE1CD03BE, 0xE1CD63BE, 'five-row vertical placement'),
            (0x020D4324, 0xE3550004, 0xE3550005, 'constructor row count'),
            (0x020D4488, 0xE3550004, 0xE3550005, 'destructor row count'),
        ):
            write_word(address, expected, replacement, label)
        if label_hook is None:
            raise ValueError('Link Box battle entry requires a renderer hook')
        address = 0x020D4410 - ram
        expected = u32(original, address)
        assert expected == 0xE59F003C, hex(expected)
        delta = label_hook - (0x020D4410 + 8)
        assert not (delta & 3) and -(1 << 25) <= delta < (1 << 25)
        branch = 0xEA000000 | ((delta >> 2) & 0x00FFFFFF)
        struct.pack_into('<I', data, address, branch)
        menu_patches.append({'address': hex(0x020D4410), 'label': 'fifth-row render hook',
                             'original': hex(expected), 'replacement': hex(branch),
                             'target': hex(label_hook)})
        selection_hooks = selection_hooks or {}
        selector_hook = selection_hooks['xwb_linkbox_five_choice_result_hook']
        up_hook = selection_hooks['xwb_linkbox_five_choice_up_hook']
        down_hook = selection_hooks['xwb_linkbox_five_choice_down_hook']
        dispatch_hook = selection_hooks['xwb_linkbox_battle_dispatch_hook']
        def branch_word(site, target, condition=0xE):
            delta = target - (site + 8)
            assert not (delta & 3) and -(1 << 25) <= delta < (1 << 25)
            return (condition << 28) | 0x0A000000 | ((delta >> 2) & 0x00FFFFFF)
        for site, expected_word, target, condition, label in (
            (0x020D4668, 0xE3500004, selector_hook, 0xE, 'five-choice selection result'),
            (0x020D4730, 0x12890003, up_hook, 0x1, 'five-choice up navigation'),
            (0x020D4778, 0x12890005, down_hook, 0x1, 'five-choice down navigation'),
            (0x020D4800, 0xE5940034, dispatch_hook, 0xE, 'wireless battle action dispatch'),
        ):
            site_offset = site - ram
            actual = u32(original, site_offset)
            assert actual == expected_word, f'{label} at {site:#x}: {actual:#010x}'
            replacement = branch_word(site, target, condition)
            struct.pack_into('<I', data, site_offset, replacement)
            menu_patches.append({'address': hex(site), 'label': label,
                                 'original': hex(actual), 'replacement': hex(replacement),
                                 'target': hex(target)})
        touch_address = 0x020D0F14
        touch_offset = touch_address - ram
        touch_original = u32(original, touch_offset)
        assert touch_original == 0xE3500010, hex(touch_original)
        struct.pack_into('<I', data, touch_offset, 0xE3500012)
        menu_patches.append({'address': hex(touch_address), 'label': 'fifth-row touch bounds',
                             'original': hex(touch_original), 'replacement': hex(0xE3500012)})
        help_table = 0x0210C1E0 - ram
        assert u32(original, help_table) == 0
        struct.pack_into('<I', data, help_table, 107)
        menu_patches.append({'address': hex(0x0210C1E0), 'label': 'fifth-row help message ID',
                             'original': hex(0), 'replacement': hex(107)})
        help_copy = 0x020D4510 - ram
        expected_pair = (0xE1510005, 0xE3A06002)
        assert tuple(u32(original, help_copy + i * 4) for i in range(2)) == expected_pair
        # Load the new halfword ID into the unused stack slot immediately after
        # the four retail entries; leave the following register setup intact.
        struct.pack_into('<II', data, help_copy, 0xE1D100B8, 0xE1CD00BC)
        menu_patches.append({'address': hex(0x020D4510), 'label': 'fifth-row help ID copy',
                             'original': [hex(x) for x in expected_pair],
                             'replacement': [hex(0xE1D100B8), hex(0xE1CD00BC)],
                             'size': 8})
    settings = original.find(bytes.fromhex('2106c0dedec00621')) - 28
    assert 0 <= settings < 0x4000
    packed = bytearray(codeCompression.compress(bytes(data), True))
    struct.pack_into('<I', packed, settings + 20, ram + len(packed))
    restored = bytearray(codeCompression.decompress(packed))
    restored[arena_offset:arena_offset + 4] = original[arena_offset:arena_offset + 4]
    restored[address:address + 4] = original[address:address + 4]
    if linkbox_hook is not None:
        restored[linkbox_address:linkbox_address + 4] = original[linkbox_address:linkbox_address + 4]
    for item in menu_patches:
        patch_address = int(item['address'], 16) - ram
        patch_size = item.get('size', 4)
        restored[patch_address:patch_address + patch_size] = original[patch_address:patch_address + patch_size]
    restored[settings + 20:settings + 24] = original[settings + 20:settings + 24]
    assert restored == original
    slot_expansion_required = max(0, len(packed) - arm9_size)
    return bytes(packed), {'arena_low_before': hex(MODULE_BASE), 'arena_low_after': hex(arena_low),
                           'literal': hex(ARENA_LITERAL), 'decompressed_size': len(original),
                           'compressed_size_before': arm9_size,
                           'compressed_size_after': len(packed),
                           'slot_expansion_required': slot_expansion_required,
                           'linkbox_pump_hook': hook_report,
                           'linkbox_battle_entry_patches': menu_patches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--relocate-actors', action='store_true')
    parser.add_argument('--transport-adapter', action='store_true')
    parser.add_argument('--session-controller', action='store_true')
    parser.add_argument('--linkbox-battle-entry', action='store_true',
                        help='add a fifth visible Link Box row to the experimental session build')
    parser.add_argument('--extended-order', action='store_true')
    parser.add_argument('--baseline', choices=('batch124', 'batch125'), default='batch125',
                        help='reviewed UI checkpoint used as the input ROMs (default: batch125)')
    parser.add_argument('--label', default='',
                        help='optional suffix for an isolated experimental output directory')
    args = parser.parse_args()
    if args.extended_order:
        args.relocate_actors = True
    if args.linkbox_battle_entry:
        args.session_controller = True
        args.transport_adapter = True
        args.extended_order = True
        args.relocate_actors = True
    if args.session_controller and not args.transport_adapter:
        parser.error('--session-controller requires --transport-adapter')
    variant = 'transport_actor_storage' if args.transport_adapter and args.relocate_actors else 'transport_adapter' if args.transport_adapter else 'actor_storage' if args.relocate_actors else 'native_loader'
    if args.extended_order:
        variant = 'extended_order_session_transport' if args.session_controller else 'extended_order_transport' if args.transport_adapter else 'extended_order'
    if args.linkbox_battle_entry:
        variant = 'linkbox_battle_entry'
    label = args.label.strip().replace('-', '_')
    if label and not label.replace('_', '').isalnum():
        parser.error('--label may contain only letters, digits, hyphens and underscores')
    suffix = ('_' + label) if label else ''
    directory = ROOT / ('build/experimental/wireless_' + variant + '_' + args.baseline + suffix)
    directory.mkdir(parents=True, exist_ok=True)
    module, memory_end, symbols = compile_bridge(directory, args.transport_adapter,
                                                 args.extended_order, args.session_controller)
    arena_low = (memory_end + 31) & ~31
    results = {}
    for version in ('Blue', 'Red'):
        if args.baseline == 'batch125':
            source = ROOT / f'build/backups/ui_checkpoint_batch125_before_local_wireless/Digimon_Super_Xros_Wars_{version}_English_batch125.nds'
        else:
            source = ROOT / f'build/backups/ui_checkpoint_batch124_user_hardware_verified/Digimon_Super_Xros_Wars_{version}_English_batch124.nds'
        source_rom = Rom(source)
        rom = source_rom
        table = u32(rom.data, 0x50) + 2 * 32
        row = struct.unpack_from('<8I', rom.data, table)
        assert row[:4] == (2, OVERLAY_BASE, 19456, 10528)
        assert row[4:6] == (CTOR_SLOT, CTOR_SLOT + 4)
        a, b = struct.unpack_from('<II', rom.data, rom.fat_offset + row[6] * 8)
        original = codeCompression.decompress(rom.data[a:b])
        assert u32(original, CTOR_SLOT - OVERLAY_BASE) == 0
        replacements = {}
        actor_report = order_report = None
        version_module = module
        if args.relocate_actors:
            from relocate_battle_actors import relocate_battle_actors
            replacements['@overlay/0'], actor_report = relocate_battle_actors(rom, symbols['xwb_actor_storage'])
        if args.extended_order:
            from extend_native_turn_order import transplant
            actors = codeCompression.decompress(replacements['@overlay/0'])
            actors, version_module, order_report = transplant(actors, 0x021F3D20,
                module, MODULE_BASE, symbols)
            if args.linkbox_battle_entry:
                actors, scene_hooks = install_remote_actor_scene_hooks(
                    actors, 0x021F3D20, symbols)
                order_report['remote_scene_hooks'] = scene_hooks
            replacements['@overlay/0'] = codeCompression.compress(actors)
        overlay = bytearray(MODULE_BASE - OVERLAY_BASE)
        overlay[:len(original)] = original
        overlay.extend(version_module)
        struct.pack_into('<I', overlay, CTOR_SLOT - OVERLAY_BASE, symbols['xwb_overlay_boot'])
        packed = codeCompression.compress(bytes(overlay))
        assert codeCompression.decompress(packed) == overlay
        hook = symbols.get('xwb_linkbox_pump_hook') if args.session_controller else None
        label_hook = symbols.get('xwb_linkbox_render_battle_row_hook') if args.linkbox_battle_entry else None
        selection_hooks = ({key: symbols[key] for key in (
            'xwb_linkbox_five_choice_result_hook',
            'xwb_linkbox_five_choice_up_hook',
            'xwb_linkbox_five_choice_down_hook',
            'xwb_linkbox_battle_dispatch_hook')}
            if args.linkbox_battle_entry else None)
        program, program_report = patch_program(rom, arena_low, hook, label_hook,
                                                args.linkbox_battle_entry, selection_hooks)
        if args.linkbox_battle_entry:
            pak = Pak(rom.file('MSG/MESPAK01.PAK'))
            messages = Messages(pak.file(21))
            assert messages.count == 106
            lobby_text = [
                b'Wireless Battle', b'Battle nearby over DS Wireless.',
                b'Open Battle Lobby', b'Formation', b'Start Battle', b'Leave Lobby',
                b'Pair V1-V2', b'Pair V1-V3', b'Pair V1-R1', b'Pair V1-R2',
                b'Pair V1-R3', b'Pair V2-V3', b'Pair V2-R1', b'Pair V2-R2',
                b'Pair V2-R3',
                b'Pair V3-R1', b'Pair V3-R2', b'Pair V3-R3', b'Pair R1-R2',
                b'Pair R1-R3', b'Pair R2-R3', b'Swap Selected Pair',
                b'Reset Formation', b'Host Ready', b'Guest Ready', b'Done',
                b'Xros Normal', b'Xros Boss', b'Dusk Boss', b'Dusk Multi',
                b'World DS Normal', b'World DS Boss', b'World DS Multi',
                b'Battle Armed', b'Neither Ready', b'Both Ready',
                b'Waiting for Host',
            ]
            appended = messages.append(lobby_text)
            updated = Messages(appended)
            assert updated.raw[:106] == messages.raw
            assert updated.raw[106:] == lobby_text
            replacements['MSG/MESPAK01.PAK'] = pak.rebuild({21: appended})
        replacements['@overlay/2'] = packed
        expansion_report = None
        if program_report['slot_expansion_required']:
            expanded_data, expansion_report = expand_arm9_slot(
                source_rom.data, program_report['slot_expansion_required'])
            temporary = directory / f'.{version.lower()}_arm9_expanded_working.nds'
            temporary.write_bytes(expanded_data)
            rom = Rom(temporary)
            temporary.unlink()
            table = u32(rom.data, 0x50) + 2 * 32
        result, operations = replace_files(rom, replacements, program)
        result = bytearray(result)
        new_bss = memory_end - OVERLAY_BASE - len(overlay)
        struct.pack_into('<II', result, table + 8, len(overlay), new_bss)
        struct.pack_into('<H', result, 0x15E, crc16(result[:0x15E]))
        output = directory / f'Digimon_Xros_Wars_{version}_{variant}_TEST.nds'
        output.write_bytes(result)
        built = Rom(output)
        assert built.files == rom.files
        for name in rom.files:
            expected_file = replacements.get(name, rom.file(name))
            assert built.file(name) == expected_file, f'Unexpected asset change: {name}'
        # Every cartridge byte must be accounted for, including old ROM padding.
        restored = bytearray(result)
        for key in replacements:
            if key.startswith('@overlay/'):
                overlay_id = int(key.split('/')[-1])
                overlay_table = u32(rom.data, 0x50) + overlay_id * 32
                file_id = u32(rom.data, overlay_table + 24)
            else:
                file_id = rom.files[key]
                overlay_table = None
            fat = rom.fat_offset + file_id * 8
            start, end = struct.unpack_from('<II', result, fat)
            restored[start:end] = rom.data[start:end]
            restored[fat:fat + 8] = rom.data[fat:fat + 8]
            if overlay_table is not None:
                restored[overlay_table + 28:overlay_table + 32] = rom.data[overlay_table + 28:overlay_table + 32]
        restored[table:table + 32] = rom.data[table:table + 32]
        arm9_offset, arm9_size = u32(rom.data, 0x20), u32(rom.data, 0x2C)
        restored[arm9_offset:arm9_offset + len(program)] = rom.data[arm9_offset:arm9_offset + len(program)]
        for a, b in ((0x2C, 0x30), (0x80, 0x84), (0x15E, 0x160)):
            restored[a:b] = rom.data[a:b]
        assert restored == rom.data, 'Unaccounted cartridge mutation'
        results[version] = {'baseline': str(source.relative_to(ROOT)),
            'baseline_sha256': sha(source_rom.data), 'arm9_slot_expansion': expansion_report,
            'output': str(output.relative_to(ROOT)), 'sha256': sha(result),
            'new_overlay_ram_size': len(overlay), 'new_overlay_bss_size': new_bss,
            'program_patch': program_report, 'actor_relocation': actor_report,
            'turn_order': order_report, 'operations': operations}
        print(version, output, flush=True)
    manifest = {'status': 'experimental Link Box lobby and protocol start probe; retail battle launch and synchronized combat are not playable',
        'baseline': args.baseline,
        'session_controller_included': args.session_controller,
        'engine_phase_sync_included': args.session_controller,
        'linkbox_battle_entry_included': args.linkbox_battle_entry,
        'linkbox_lobby_menu_included': args.linkbox_battle_entry,
        'retail_battle_launcher_included': False,
        'synchronized_battle_commands_included': False,
        'module_base': hex(MODULE_BASE), 'reserved_memory_end': hex(arena_low),
        'symbols': {key: hex(value) for key, value in symbols.items()}, 'builds': results,
        'validation': ('Only the intentional UI message archive, ARM9 instructions, overlay size and overlay constructor changed; '
                       'all other named assets and all cartridge mutations are verified. Link Box constructor execution and '
                       'rendering, touch/keyboard selection, connection flow, and battle handoff still require runtime verification. '
                       'The experimental session controller mirrors its canonical phase into the engine hooks after each radio pump '
                       'and adds a pump call at the battle tactics-status check. The Link Box lobby UI supports formation pair swaps, '
                       'host music selection, readiness and protocol START, but START does not launch the retail battle engine. '
                       'Battle command/result hooks are absent and no two-system match has been verified.')}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
