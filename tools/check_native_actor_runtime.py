"""Fresh-boot regression of relocated actor storage in an ordinary battle.

No wireless match is tested by this core. All saves and game progress used here
are QA copies. This verifies the relocation before changing actor capacity.
"""
import ctypes as C
import argparse
import hashlib
import json
import shutil
import struct
from emulator_smoke import Emulator
from xros_text import ROOT
from check_wireless_battle_layout import inspect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', default='actor_storage')
    args = parser.parse_args()
    manifest = json.loads((ROOT / f'build/experimental/wireless_{args.variant}/manifest.json').read_text())
    build = manifest['builds']['Blue']
    rom = ROOT / build['output']
    assert hashlib.sha256(rom.read_bytes()).hexdigest() == build['sha256']
    q = ROOT / f'build/qa/native_{args.variant}'
    q.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'build/qa/status_batch108/Digimon_Super_Xros_Wars_Blue_English_batch108.dsv'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copyfile(source, q / (rom.stem + '.dsv'))
    e = Emulator(rom, q)
    def key(k, n=2):
        e.run(n, k)
        e.run(20)
    try:
        e.run(1800); key('A', 3); e.run(180); key('A', 3); e.run(840)
        key('DOWN', 60); key('RIGHT', 40); e.run(180); key('RIGHT', 45)
        key('DOWN', 20); key('RIGHT', 40); key('UP', 20); key('A'); e.run(180)
        key('RIGHT', 24); key('UP', 28); key('A'); e.run(180)
        key('UP', 12); key('A'); e.run(180); key('UP', 15); key('A'); e.run(200)
        key('RIGHT', 30); key('A'); e.run(500)
        e.snapshot('digilab')
        key('B'); e.run(300); key('DOWN', 130); key('LEFT', 65)
        key('DOWN', 110); key('DOWN', 140); key('LEFT', 70); key('DOWN', 120)
        e.run(300); key('DOWN', 120); key('LEFT', 180); e.run(400)
        e.snapshot('field')
        for k in ('RIGHT', 'DOWN', 'UP', 'RIGHT', 'DOWN', 'LEFT'):
            key(k, 180)
        e.run(400)
        e.snapshot('battle')
        e.core.retro_get_memory_data.argtypes = [C.c_uint]
        e.core.retro_get_memory_data.restype = C.c_void_p
        p = e.core.retro_get_memory_data(2)
        ram = C.string_at(p, 0x400000)
        actor_base = int(manifest['symbols']['xwb_actor_storage'], 16)
        actors = inspect(ram, actor_base)
        marker = int(manifest['symbols']['xwb_boot_marker'], 16)
        assert struct.unpack_from('<I', ram, marker - 0x02000000)[0] == 0x58424F4B
        (q / 'battle_main_ram.bin').write_bytes(ram)
        e.save(q / 'battle.state')
        (q / 'battle_fixture.json').write_text(json.dumps({'rom_sha256': build['sha256'],
            'source_save_sha256': source_hash, 'fresh_boot': True}, indent=2) + '\n')
        key('A'); e.run(120); e.snapshot('command_ring')
        # Retail tactics are intentionally available in this ordinary battle.
        # Command ring left opens tactics; select Full Power, then start.
        key('LEFT'); e.run(100); key('A'); e.run(120); e.snapshot('ordinary_tactics')
        key('A'); e.run(120); key('X'); e.run(1800); e.snapshot('results')
        after = C.string_at(p, 0x400000)
        (q / 'results_main_ram.bin').write_bytes(after)
        e.save(q / 'results.state')
        remaining_enemy_hp = [struct.unpack_from('<I', after,
            actor_base - 0x02000000 + index * 0x1A0 + 0xE4)[0] for index in range(6, 9)]
        assert remaining_enemy_hp == [0, 0, 0]
        order_entries = None
        if 'xwb_order_context' in manifest['symbols']:
            context = int(manifest['symbols']['xwb_order_context'], 16) - 0x02000000
            order_entries = [struct.unpack_from('<i', after, context + 0x928 + i * 8)[0]
                             for i in range(13)]
            assert any(i >= 6 for i in order_entries) and -1 in order_entries
        report = {'status': 'Fresh boot completed an ordinary battle and reached results; six source/live records matched before battle.',
            'rom': build['output'], 'rom_sha256': build['sha256'], 'actors': actors,
            'enemy_hp_after': remaining_enemy_hp, 'private_turn_order_entries': order_entries,
            'source_save_sha256': source_hash,
            'scope': 'Ordinary Blue battle regression only. Original active capacity remains9. Native tactics/rewards apply in this ordinary battle. No radio or PvP match tested.'}
        (q / 'runtime_verified.json').write_text(json.dumps(report, indent=2) + '\n')
    finally:
        e.close()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash


if __name__ == '__main__':
    main()
