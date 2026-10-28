"""Fresh-boot UI screenshots using a copy of the supplied save; no save writes."""
import shutil
import tempfile
from pathlib import Path
from emulator_smoke import Emulator
from xros_text import ROOT


def main():
    rom = ROOT / 'build/Digimon_Super_Xros_Wars_Blue_English_batch123.nds'
    output = ROOT / 'build/qa/ui_batch123'
    output.mkdir(parents=True, exist_ok=True)
    # The native core may retain its save-file handle until process exit on Windows.
    with tempfile.TemporaryDirectory(prefix='blue-ui-', dir=ROOT / 'build/qa', ignore_cleanup_errors=True) as temp:
        temp = Path(temp)
        shutil.copyfile(ROOT / 'build/qa/status_batch108/Digimon_Super_Xros_Wars_Blue_English_batch108.dsv', temp / (rom.stem + '.dsv'))
        e = Emulator(rom, temp)
        def key(button):
            e.run(2, button)
            e.run(20)
        def shot(name):
            e.run(140)
            e.snapshot(name)
            shutil.copyfile(temp / (name + '.png'), output / (name + '.png'))
        try:
            e.run(1800)
            key('A'); e.run(180)
            key('A'); e.run(840)
            shot('farm')
            key('X'); shot('pause')
            e.save(temp / 'pause.state')
            key('A'); shot('stats')
            e.load(temp / 'pause.state')
            for _ in range(3): key('RIGHT')
            key('A'); shot('formation')
            e.load(temp / 'pause.state')
            key('DOWN'); key('A'); shot('items')
            e.load(temp / 'pause.state')
            key('DOWN'); key('RIGHT'); key('RIGHT'); key('A')
            key('DOWN'); key('A'); shot('play_log')
        finally:
            e.close()


if __name__ == '__main__':
    main()
