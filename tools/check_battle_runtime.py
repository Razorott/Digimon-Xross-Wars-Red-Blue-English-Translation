"""Repeat the supplied save's walking route to a live battle from a fresh boot."""
import shutil
from emulator_smoke import Emulator
from xros_text import ROOT


def main():
    q = ROOT / 'build/qa/batch124/final_blue'
    q.mkdir(parents=True, exist_ok=True)
    rom = ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch124.nds'
    shutil.copyfile(ROOT / 'build/qa/status_batch108/Digimon_Super_Xros_Wars_Blue_English_batch108.dsv', q / (rom.stem + '.dsv'))
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
        e.save(q / 'battle.state')
        key('A'); e.run(180); e.snapshot('command_ring')
        key('B'); key('X'); e.run(1100); e.snapshot('turn')
    finally:
        e.close()


if __name__ == '__main__':
    main()
