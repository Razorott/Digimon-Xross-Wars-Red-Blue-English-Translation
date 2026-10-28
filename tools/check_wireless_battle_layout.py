"""Verify saved-party versus live-actor fields in an isolated battle fixture.

This is a battle integration diagnostic, not a network battle implementation.
Only its own headless emulator RAM is changed; user ROMs/saves are untouched.
"""
import ctypes as C
import hashlib
import json
import struct
from emulator_smoke import Emulator
from xros_text import ROOT

BASE = 0x02000000
ACTORS = 0x0221AFD4
ACTOR_SIZE = 0x1A0
SAVED_SIZE = 0x80
SAVED_SEARCH_START = 0x021F0700
SAVED_SEARCH_END = 0x021F3D20


def inspect(ram, actor_base=ACTORS):
    def half(address):
        return struct.unpack_from('<H', ram, address - BASE)[0]
    def word(address):
        return struct.unpack_from('<I', ram, address - BASE)[0]
    report = []
    for index in range(6):
        actor = actor_base + index * ACTOR_SIZE
        species = half(actor + 0x14)
        name = ram[actor - BASE + 0x1A:actor - BASE + 0x1A + 18]
        matches = []
        for saved in range(SAVED_SEARCH_START, SAVED_SEARCH_END - SAVED_SIZE + 1, SAVED_SIZE):
            if half(saved + 0x12) == species and ram[saved - BASE:saved - BASE + 18] == name:
                matches.append(saved)
        if len(matches) != 1:
            raise ValueError(f'Expected one saved source for actor {index}, found {matches}')
        saved = matches[0]
        source_stats = {key: half(saved + offset) for key, offset in {
            'hp': 0x1E, 'max_hp': 0x20, 'mp': 0x22, 'max_mp': 0x24,
            'atk': 0x26, 'int': 0x28, 'spd': 0x2A, 'def': 0x2C,
            'friendship': 0x2E}.items()}
        live_stats = {key: (word if key in ('hp', 'max_hp') else half)(actor + offset)
                      for key, offset in {'hp': 0xE4, 'max_hp': 0xE0,
                         'mp': 0xEA, 'max_mp': 0xE8, 'atk': 0x44,
                         'def': 0x48, 'spd': 0x4C, 'int': 0x50,
                         'friendship': 0x54}.items()}
        if source_stats != live_stats:
            raise ValueError(f'Saved/live stats differ for actor {index}')
        opaque_fields = []
        for source_offset, actor_offset, size in (
                (0x34, 0xFA, 8), (0x44, 0x10A, 8),
                (0x4C, 0x13C, 2), (0x4C, 0x140, 2)):
            source_value = ram[saved - BASE + source_offset:saved - BASE + source_offset + size]
            actor_value = ram[actor - BASE + actor_offset:actor - BASE + actor_offset + size]
            if source_value != actor_value:
                raise ValueError(f'Saved/live opaque field differs for actor {index}: '
                                 f'{source_offset:#x}->{actor_offset:#x}')
            opaque_fields.append({'saved_offset': hex(source_offset),
                                  'actor_offset': hex(actor_offset),
                                  'size': size, 'value': source_value.hex()})
        report.append({'slot': index, 'actor': hex(actor), 'source': hex(saved),
                       'species': species, 'name_bytes': name.hex(),
                       'saved_record_sha256': hashlib.sha256(ram[saved - BASE:saved - BASE + SAVED_SIZE]).hexdigest(),
                       'verified_stats': live_stats, 'verified_opaque_fields': opaque_fields})
    return report


def main():
    directory = ROOT / 'build/qa/wireless_battle_engine'
    emulator = Emulator(ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch124.nds', directory)
    try:
        emulator.load(ROOT / 'build/qa/batch124/final_blue/battle.state')
        emulator.run(1)
        core = emulator.core
        core.retro_get_memory_size.argtypes = [C.c_uint]
        core.retro_get_memory_size.restype = C.c_size_t
        core.retro_get_memory_data.argtypes = [C.c_uint]
        core.retro_get_memory_data.restype = C.c_void_p
        size, pointer = core.retro_get_memory_size(2), core.retro_get_memory_data(2)
        assert size == 0x400000 and pointer
        before = C.string_at(pointer, size)
        actors = inspect(before)
        # Verify current HP is a live field and does not alias its saved source.
        hp_address = ACTORS + 0xE4
        hp = actors[0]['verified_stats']['hp']
        C.memmove(pointer + hp_address - BASE, struct.pack('<I', hp - 1), 4)
        emulator.run(60)
        after = C.string_at(pointer, size)
        assert struct.unpack_from('<I', after, hp_address - BASE)[0] == hp - 1
        for actor in actors:
            source = int(actor['source'], 16) - BASE
            assert after[source:source + SAVED_SIZE] == before[source:source + SAVED_SIZE]
        emulator.snapshot('live_hp_copy_check')
        report = {'status': 'Six source/live actor matches verified for names, species, trained stats, two opaque four-halfword ranges and one repeated field; one isolated live HP change retained for60 frames without changing any source record.',
                  'limitation': 'Blue fixture only. Equipment, commands, opponent expansion, battle-end persistence and radio integration are not verified.',
                  'saved_record_stride': SAVED_SIZE, 'live_actor_stride': ACTOR_SIZE,
                  'original_actor_count': 9, 'actors': actors}
        (directory / 'party_layout_verified.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    finally:
        emulator.close()


if __name__ == '__main__':
    main()
