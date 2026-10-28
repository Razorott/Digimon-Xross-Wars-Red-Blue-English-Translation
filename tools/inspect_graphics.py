from xros_text import *
import collections

rom = Rom(rom_paths()['blue'])
for name in ['BG_NCGR.PAK','BG_NCLR.PAK','BG_NSCR.PAK','SPR_NCGR.PAK','SPR_NCLR.PAK','SPR_NCER.PAK','NCGMOVIE/MV0000.bin']:
    pak = Pak(rom.file(name))
    print(name, pak.count)
    counts = collections.Counter()
    for i in range(pak.count):
        try:
            data = pak.file(i)
            counts[data[:4].hex()] += 1
            if i < 3:
                print(i,len(data),data[:64].hex())
        except Exception as exc:
            print('ERROR',i,str(exc))
            break
    print(counts)
