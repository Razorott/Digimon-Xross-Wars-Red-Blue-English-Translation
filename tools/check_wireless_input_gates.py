"""Exercise wireless-only input restrictions in an isolated normal-battle fixture.

The coordinator phase is forced in QA RAM; no peer/radio/PvP battle is started.
Never use this diagnostic fixture as a playable multiplayer state.
"""
import ctypes as C
import hashlib
import json
import struct
from emulator_smoke import Emulator
from xros_text import ROOT, u32


def main():
    q = ROOT / 'build/qa/native_extended_order_transport'
    manifest = json.loads((ROOT / 'build/experimental/wireless_extended_order_transport/manifest.json').read_text())
    verified = json.loads((q / 'battle_fixture.json').read_text())
    build = manifest['builds']['Blue']
    assert verified['rom_sha256'] == build['sha256'], 'Recreate fresh-boot fixture for current code first'
    assert hashlib.sha256((ROOT / build['output']).read_bytes()).hexdigest() == build['sha256']
    e = Emulator(ROOT / build['output'], q / 'input_gates')
    try:
        e.load(q / 'battle.state')
        e.core.retro_get_memory_data.argtypes = [C.c_uint]
        e.core.retro_get_memory_data.restype = C.c_void_p
        pointer = e.core.retro_get_memory_data(2)
        def ram():
            return C.string_at(pointer, 0x400000)
        data = ram()
        context = u32(data, 0x221AEA4 - 0x02000000)
        context = u32(data, context + 0x1C - 0x02000000)
        def phase():
            return u32(ram(), context + 0x910 - 0x02000000)
        def key(k):
            e.run(2, k); e.run(90)
        assert phase() == 0xC9
        match = int(manifest['symbols']['xwb_live_match'], 16)
        C.memmove(pointer + match - 0x02000000 + 39, b'\x02', 1)
        key('Y')
        assert phase() == 0xC9, 'All Tactics must not open in wireless phase'
        key('A')
        assert phase() == 0x12D
        e.snapshot('wireless_restricted_ring_QA')
        key('LEFT'); key('A')
        # Navigation may skip the disabled slot and select another legal action.
        assert not 0x258 <= phase() <= 0x26F, 'Tactics screen was opened'
        assert not 0x1F4 <= phase() <= 0x207, 'Consumable screen was opened'
        result = {'status': 'passed', 'rom_sha256': build['sha256'],
            'all_tactics_key_blocked': True, 'ring_forbidden_screens_not_opened': True,
            'phase_after_ring_confirm': hex(phase()),
            'scope': 'Forced wireless phase in isolated ordinary-battle QA RAM only. No real wireless match, radio, saves or twelve-actor fight tested.'}
        (q / 'input_gates_verified.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
    finally:
        e.close()


if __name__ == '__main__':
    main()
