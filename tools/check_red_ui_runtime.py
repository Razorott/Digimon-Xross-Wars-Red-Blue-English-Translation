"""Check Red's formation using a read-only source .sav and a trimmed QA copy."""
from xros_text import ROOT
from emulator_smoke import Emulator
import hashlib


def main():
    source = ROOT / 'build/backups/Savefiles/Digimon Story - Super Xros Wars - Red (Japan).sav'
    original = source.read_bytes()
    if len(original) != 524288 or original[65536:] != b'\xff' * (524288 - 65536):
        raise ValueError('Unexpected save size/padding; do not truncate it')
    q = ROOT / 'build/qa/batch125/red'
    q.mkdir(parents=True, exist_ok=True)
    rom = ROOT / 'build/Digimon_Super_Xros_Wars_Red_English_batch125.nds'
    (q / (rom.stem + '.sav')).write_bytes(original[:65536])
    e = Emulator(rom, q)
    def key(k):
        e.run(3, k)
        e.run(20)
    try:
        e.run(1800); key('A'); e.run(180)
        e.snapshot('continue')
        key('A'); e.run(840); e.snapshot('field')
        key('X'); e.run(150); e.snapshot('pause')
        for _ in range(3):
            key('RIGHT')
        key('A'); e.run(180); e.snapshot('formation')
    finally:
        e.close()
    if source.read_bytes() != original:
        raise ValueError('Source save changed')
    print('Source save unchanged:', hashlib.sha256(original).hexdigest())


if __name__ == '__main__':
    main()
