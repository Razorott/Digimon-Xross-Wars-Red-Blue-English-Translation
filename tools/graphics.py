"""Lossless Nitro tile/map/cell decoding for the translation's graphics pass.

Format cross-check: pleonex/tinke Plugins/Images (NCGR, NCLR, NSCR, NCER).
"""
import struct
from pathlib import Path
from PIL import Image, ImageDraw
from xros_text import ROOT, Rom, Pak, rom_paths, u32


def lz11_decode(data):
    if data[0] != 0x11:
        return data
    size = int.from_bytes(data[1:4], 'little')
    pos = 4
    if not size:
        size = u32(data, 4)
        pos = 8
    out = bytearray()
    while len(out) < size:
        flags = data[pos]
        pos += 1
        for bit in range(7, -1, -1):
            if flags & (1 << bit):
                a = data[pos]
                pos += 1
                kind = a >> 4
                if kind >= 2:
                    b = data[pos]; pos += 1
                    length = kind + 1
                    distance = ((a & 15) << 8 | b) + 1
                elif kind == 0:
                    b, c = data[pos:pos + 2]; pos += 2
                    length = ((a & 15) << 4 | b >> 4) + 0x11
                    distance = ((b & 15) << 8 | c) + 1
                else:
                    b, c, d = data[pos:pos + 3]; pos += 3
                    length = ((a & 15) << 12 | b << 4 | c >> 4) + 0x111
                    distance = ((c & 15) << 8 | d) + 1
                if distance > len(out):
                    raise ValueError('Invalid LZ11 distance')
                for _ in range(min(length, size - len(out))):
                    out.append(out[-distance])
            else:
                out.append(data[pos]); pos += 1
            if len(out) == size:
                break
    return bytes(out)


def cached_files(rom, name, limit=None):
    directory = ROOT / 'extracted/graphics' / rom.code / name.replace('/', '_')
    directory.mkdir(parents=True, exist_ok=True)
    pak = Pak(rom.file(name))
    result = []
    for index in range(min(pak.count,limit) if limit else pak.count):
        path = directory / f'{index:04d}.bin'
        if not path.exists():
            path.write_bytes(lz11_decode(pak.file(index)))
        result.append(path)
    return result


def palette(data):
    if data[:4] != b'RLCN':
        raise ValueError('Not NCLR')
    size = u32(data, 32)
    offset = 24 + u32(data, 36)
    values = struct.unpack_from(f'<{size // 2}H', data, offset)
    return [((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31, 255) for v in values]


def tile_info(data):
    if data[:4] != b'RGCN':
        raise ValueError('Not NCGR')
    height, width, format = struct.unpack_from('<HHI', data, 24)
    size = u32(data, 40)
    offset = 24 + u32(data, 44)
    bpp = {3: 4, 4: 8}[format]
    raw = data[offset:offset + size]
    return width, height, bpp, offset, raw


def tile_pixels(raw, bpp, index):
    size = bpp * 8
    raw = raw[index * size:(index + 1) * size]
    if len(raw) != size:
        return [0] * 64
    if bpp == 8:
        return list(raw)
    return [n for b in raw for n in (b & 15, b >> 4)]


def render_tiles(data, colors=None, width_tiles=32):
    width, height, bpp, _, raw = tile_info(data)
    if width != 0xffff:
        width_tiles = width
    count = len(raw) // (8 * bpp)
    height_tiles = (count + width_tiles - 1) // width_tiles
    image = Image.new('RGBA', (width_tiles * 8, height_tiles * 8))
    if colors is None:
        colors = [(v, v, v, 255) for v in [int(i * 255 / ((1 << bpp) - 1)) for i in range(1 << bpp)]]
    for index in range(count):
        pixels = tile_pixels(raw, bpp, index)
        tile = Image.new('RGBA', (8, 8))
        tile.putdata([colors[p % len(colors)] for p in pixels])
        image.paste(tile, (index % width_tiles * 8, index // width_tiles * 8))
    return image


def map_info(data):
    if data[:4] != b'RCSN':
        raise ValueError('Not NSCR')
    width, height = struct.unpack_from('<HH', data, 24)
    size = u32(data, 32)
    return width, height, list(struct.unpack_from(f'<{size // 2}H', data, 36))


def render_map(ncgr, nclr, nscr, transparent=False):
    _, _, bpp, _, raw = tile_info(ncgr)
    colors = palette(nclr)
    width, height, entries = map_info(nscr)
    image = Image.new('RGBA', (width, height))
    for i, entry in enumerate(entries):
        bank = entry >> 12
        pixels = tile_pixels(raw, bpp, entry & 1023)
        tile = Image.new('RGBA', (8, 8))
        tile.putdata([(0,0,0,0) if transparent and p == 0 else colors[(bank * (1 << bpp) + p) % len(colors)] for p in pixels])
        if entry & 1024: tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if entry & 2048: tile = tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        # Text BG maps wider/taller than 32 tiles use 32x32 screen blocks.
        block = i // 1024
        x = ((block % max(1, width // 256)) * 32 + i % 32) * 8
        y = ((block // max(1, width // 256)) * 32 + (i % 1024) // 32) * 8
        image.paste(tile, (x, y))
    return image


def cells(data, bank=0):
    count, kind, bank_offset, block = struct.unpack_from('<HHII', data, 24)
    base = 24 + bank_offset
    record_size = 16 if kind else 8
    n, _, offset = struct.unpack_from('<HHI', data, base + bank * record_size)
    start = base + count * record_size + offset
    result = []
    sizes = [[(8,8),(16,16),(32,32),(64,64)],[(16,8),(32,8),(32,16),(64,32)],[(8,16),(8,32),(16,32),(32,64)]]
    for i in range(n):
        a,b,c = struct.unpack_from('<HHH', data, start + i * 6)
        shape = a >> 14
        if shape == 3: continue
        w,h = sizes[shape][b >> 14]
        x,y = b & 511, a & 255
        if x >= 256: x -= 512
        if y >= 128: y -= 256
        result.append({'x':x,'y':y,'w':w,'h':h,'offset':(c & 1023) * (32 << (block & 255)), 'palette':c >> 12,'flip_x':bool(b & 4096),'flip_y':bool(b & 8192),'bpp':8 if a & 8192 else 4})
    return result


def render_cell(ncgr,nclr,ncer,bank=0):
    objects = cells(ncer,bank)
    _,_,bpp,_,raw = tile_info(ncgr)
    colors = palette(nclr)
    if not objects: return Image.new('RGBA',(8,8))
    left,top = min(c['x'] for c in objects),min(c['y'] for c in objects)
    right,bottom = max(c['x']+c['w'] for c in objects),max(c['y']+c['h'] for c in objects)
    image = Image.new('RGBA',(right-left,bottom-top))
    for c in reversed(objects):
        obj = Image.new('RGBA',(c['w'],c['h']))
        objraw = raw[c['offset']:]
        for y in range(c['h']//8):
            for x in range(c['w']//8):
                pix = tile_pixels(objraw,bpp,y*(c['w']//8)+x)
                tile = Image.new('RGBA',(8,8))
                tile.putdata([(0,0,0,0) if p==0 else colors[(c['palette']*(1<<bpp)+p)%len(colors)] for p in pix])
                obj.paste(tile,(x*8,y*8))
        if c['flip_x']: obj=obj.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if c['flip_y']: obj=obj.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image.alpha_composite(obj,(c['x']-left,c['y']-top))
    return image


def contact(images, path, columns=6, cell=(160,160)):
    cw,ch=cell
    canvas=Image.new('RGB',(columns*cw,((len(images)+columns-1)//columns)*ch),'#303040')
    draw=ImageDraw.Draw(canvas)
    for index,(label,img) in enumerate(images):
        x=index%columns*cw; y=index//columns*ch
        draw.text((x+2,y+2),str(label),fill='white')
        img=img.copy();img.thumbnail((cw-4,ch-20),Image.Resampling.NEAREST)
        canvas.paste(img,(x+2,y+18),img if img.mode=='RGBA' else None)
    path.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(path)


if __name__=='__main__':
    rom=Rom(rom_paths()['blue'])
    output=ROOT/'extracted/graphics/previews'
    bg=cached_files(rom,'BG_NCGR.PAK')
    for start in range(0,len(bg),60):
        contact([(i,render_tiles(bg[i].read_bytes())) for i in range(start,min(start+60,len(bg)))],output/f'bg_tiles_{start:03d}.png',columns=6)
    spr=cached_files(rom,'SPR_NCGR.PAK',180)
    pal=cached_files(rom,'SPR_NCLR.PAK',180)
    cer=cached_files(rom,'SPR_NCER.PAK',180)
    for start in range(0,180,60):
        contact([(i,render_cell(spr[i].read_bytes(),pal[i].read_bytes(),cer[i].read_bytes())) for i in range(start,start+60)],output/f'sprites_{start:03d}.png',columns=6,cell=(160,100))
    for movie in range(3):
        fs=cached_files(rom,f'NCGMOVIE/MV{movie:04d}.bin')
        print('movie',movie,[(p.name,len(p.read_bytes()),p.read_bytes()[:48].hex()) for p in fs[:3]],flush=True)
        images=[]
        for i in range(2,len(fs)):
            img=render_map(fs[i].read_bytes(),fs[1].read_bytes(),fs[0].read_bytes())
            img.save(output/f'movie{movie}_{i:02d}.png')
            images.append((i,img))
        contact(images,output/f'movie{movie}_contact.png',columns=6)
