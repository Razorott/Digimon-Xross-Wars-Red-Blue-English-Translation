"""Read NFTR fonts and add English glyphs from native Latin shapes."""
import struct
from xros_text import u32, align4


class Font:
    def __init__(self, data):
        self.data = data
        if data[:4] != b'RTFN':
            raise ValueError('Not NFTR')
        self.info = struct.unpack_from('<H', data, 12)[0]
        self.glyph_block = u32(data, self.info + 16) - 8
        self.width_block = u32(data, self.info + 20) - 8
        self.map_pointer = self.info + 24
        self.maps = []
        self.mapping = {}
        offset = u32(data, self.map_pointer) - 8
        while True:
            if offset in self.maps or data[offset:offset + 4] != b'PAMC':
                raise ValueError('Invalid NFTR map chain')
            self.maps.append(offset)
            low, high, kind, _, following = struct.unpack_from('<4HI', data, offset + 8)
            if kind == 0:
                first = struct.unpack_from('<H', data, offset + 20)[0]
                pairs = [(code, first + code - low) for code in range(low, high + 1)]
            elif kind == 1:
                values = struct.unpack_from(f'<{high - low + 1}H', data, offset + 20)
                pairs = zip(range(low, high + 1), values)
            elif kind == 2:
                count = struct.unpack_from('<H', data, offset + 20)[0]
                pairs = [struct.unpack_from('<HH', data, offset + 22 + i * 4) for i in range(count)]
            else:
                raise ValueError(f'Unknown NFTR map method {kind}')
            for code, glyph in pairs:
                if glyph != 0xffff and code not in self.mapping:
                    self.mapping[code] = glyph
            if not following:
                break
            offset = following - 8
        off = self.glyph_block
        self.width, self.height, self.cell_size, self.baseline, self.max_width, self.bpp, self.flags = struct.unpack_from('<BBH4B', data, off + 8)
        self.metrics = {}
        off = self.width_block
        while True:
            first, last, following = struct.unpack_from('<HHI', data, off + 8)
            for index in range(first, last + 1):
                self.metrics[index] = struct.unpack_from('<bBb', data, off + 16 + (index - first) * 3)
            if not following:
                break
            off = following - 8

    def glyph_index(self, char):
        return self.mapping.get(int.from_bytes(char.encode('cp932'), 'big'))

    def advance(self, char):
        glyph = self.glyph_index(char)
        if glyph is None:
            raise ValueError(f'No native glyph for {char!r}')
        return self.metrics[glyph][2]

    def pixels(self, glyph):
        offset = self.glyph_block + 16 + glyph * self.cell_size
        raw = self.data[offset:offset + self.cell_size]
        bits = ''.join(f'{byte:08b}' for byte in raw)
        return [int(bits[i:i + self.bpp], 2) for i in range(0, self.width * self.height * self.bpp, self.bpp)]


def append_glyphs(data, cells, metrics):
    """Grow CGLP and append CWDH, preserving all original cells/metrics."""
    font = Font(data)
    index = max(font.metrics) + 1
    start = font.glyph_block
    old_end = start + u32(data, start + 4)
    block = bytearray(data[start:start + 16 + index * font.cell_size])
    for pixels in cells:
        bits = ''.join(f'{p:0{font.bpp}b}' for p in pixels)
        bits += '0' * (font.cell_size * 8 - len(bits))
        block.extend(bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)))
    block.extend(b'\0' * (align4(len(block)) - len(block)))
    struct.pack_into('<I', block, 4, len(block))
    delta = len(block) - (old_end - start)
    out = bytearray(data[:start] + block + data[old_end:])

    def moved(pointer):
        return pointer + delta if pointer and pointer - 8 >= old_end else pointer

    for pos in (font.info + 16, font.info + 20, font.info + 24):
        struct.pack_into('<I', out, pos, moved(u32(data, pos)))
    off = font.width_block
    while True:
        following = u32(data, off + 12)
        struct.pack_into('<I', out, off + delta + 12, moved(following))
        if not following:
            break
        off = following - 8
    for off in font.maps:
        struct.pack_into('<I', out, off + delta + 16, moved(u32(data, off + 16)))
    width_block = bytearray(struct.pack('<4sIHHI', b'HDWC', 0, index, index + len(metrics) - 1, moved(u32(data, font.info + 20))))
    for metric in metrics:
        width_block.extend(struct.pack('<bBb', *metric))
    width_block.extend(b'\0' * (align4(len(width_block)) - len(width_block)))
    struct.pack_into('<I', width_block, 4, len(width_block))
    struct.pack_into('<I', out, font.info + 20, len(out) + 8)
    out.extend(width_block)
    struct.pack_into('<I', out, 8, len(out))
    struct.pack_into('<H', out, 14, struct.unpack_from('<H', data, 14)[0] + 1)
    return bytes(out)


def english_font(data):
    font = Font(data)
    # Numeric-only resources already support ASCII digits and are left intact.
    if font.glyph_index('\uff21') is None:
        return data, 0
    aliases = {}
    aliases[32] = font.glyph_index('\u3000')
    for code in range(33, 127):
        fullwidth = chr(code + 0xfee0)
        try:
            target = int.from_bytes(fullwidth.encode('cp932'), 'big')
        except UnicodeEncodeError:
            continue
        if target in font.mapping:
            aliases[code] = font.mapping[target]
    # Native fonts use Japanese brackets; their Latin equivalents are present.
    extra = {ord('"'): 0x8168, ord('-'): 0x817c}
    for code, target in extra.items():
        if target in font.mapping:
            aliases[code] = font.mapping[target]
    # The large heading font only has capitals. Use those glyphs for lowercase
    # input as well, retaining its original all-capitals appearance.
    for char in 'abcdefghijklmnopqrstuvwxyz':
        if ord(char) not in aliases:
            upper = int.from_bytes(char.upper().encode('cp932'), 'big')
            glyph = aliases.get(upper, font.mapping.get(upper))
            if glyph is not None:
                aliases[ord(char)] = glyph
    if not aliases:
        return data, 0
    # A raised native comma supplies the missing apostrophe in the same style.
    aliases[39] = font.glyph_index('\uff0c')
    cells = []
    metrics = []
    first = max(font.metrics) + 1
    max_ink_width = font.width
    spacing = 3 if font.width <= 8 else 4
    new_map = {}
    for code, glyph in sorted(aliases.items()):
        if glyph is None:
            continue
        pixels = font.pixels(glyph)
        if code == 39:
            rows = [y for y in range(font.height) if any(pixels[y * font.width:(y + 1) * font.width])]
            raised = [0] * len(pixels)
            shift = rows[0] - max(1, font.height // 8)
            for y in rows:
                new_y = y - shift
                if 0 <= new_y < font.height:
                    raised[new_y * font.width:(new_y + 1) * font.width] = pixels[y * font.width:(y + 1) * font.width]
            pixels = raised
        columns = [x for x in range(font.width) if any(pixels[y * font.width + x] for y in range(font.height))]
        new_pixels = [0] * len(pixels)
        if code == 32:
            ink_width = 0
            advance = spacing
        else:
            left, right = min(columns), max(columns)
            old_width = right - left + 1
            ink_width = min(old_width, max_ink_width)
            for y in range(font.height):
                for x in range(ink_width):
                    old_x = left + min(old_width - 1, int((x + .5) * old_width / ink_width))
                    new_pixels[y * font.width + x] = pixels[y * font.width + old_x]
            advance = ink_width + 1
        new_map[code] = first + len(cells)
        cells.append(new_pixels)
        metrics.append((0, ink_width, advance))
    data = append_glyphs(data, cells, metrics)
    # Keep the native Latin silhouettes. Some game screens ignore CWDH advances
    # and use fixed-width cells, so dialogue wrapping must also respect the
    # observed 12px cell advance. A full proportional renderer is future work.
    aliases = new_map
    font = Font(data)
    # Put the ASCII block first, ahead of the existing broad sparse-map block.
    out = bytearray(data)
    out.extend(b'\0' * (align4(len(out)) - len(out)))
    offset = len(out)
    old_first = u32(data, font.map_pointer)
    block = bytearray(struct.pack('<4sI4HIH', b'PAMC', 0, min(aliases), max(aliases), 2, 0, old_first, len(aliases)))
    for code, glyph in sorted(aliases.items()):
        block.extend(struct.pack('<HH', code, glyph))
    block.extend(b'\0' * (align4(len(block)) - len(block)))
    struct.pack_into('<I', block, 4, len(block))
    out.extend(block)
    struct.pack_into('<I', out, font.map_pointer, offset + 8)
    struct.pack_into('<I', out, 8, len(out))
    struct.pack_into('<H', out, 14, struct.unpack_from('<H', data, 14)[0] + 1)
    rebuilt = Font(out)
    assert all(rebuilt.mapping[k] == v for k, v in font.mapping.items() if k not in aliases)
    assert all(rebuilt.mapping[k] == v for k, v in aliases.items())
    return bytes(out), len(aliases)


def two_byte_latin_font(data):
    """Map CP932 fullwidth Latin to the proportional English glyphs.

    The DigiDex list-name parser accepts two-byte Shift-JIS characters but
    black-screens on ordinary one-byte ASCII. Fullwidth Latin supplies legal
    two-byte codes; this CMAP alias keeps the resulting labels compact.
    Original glyph cells and width records remain unchanged.
    """
    font = Font(data)
    aliases = {}
    for code in range(32, 127):
        char = '\u3000' if code == 32 else chr(code + 0xfee0)
        try:
            full = int.from_bytes(char.encode('cp932'), 'big')
        except UnicodeEncodeError:
            continue
        glyph = font.mapping.get(code)
        if glyph is not None:
            aliases[full] = glyph
    if not aliases:
        return data, 0
    out = bytearray(data)
    out.extend(b'\0' * (align4(len(out)) - len(out)))
    offset = len(out)
    old_first = u32(data, font.map_pointer)
    block = bytearray(struct.pack('<4sI4HIH', b'PAMC', 0, min(aliases), max(aliases),
                                  2, 0, old_first, len(aliases)))
    for code, glyph in sorted(aliases.items()):
        block.extend(struct.pack('<HH', code, glyph))
    block.extend(b'\0' * (align4(len(block)) - len(block)))
    struct.pack_into('<I', block, 4, len(block))
    out.extend(block)
    struct.pack_into('<I', out, font.map_pointer, offset + 8)
    struct.pack_into('<I', out, 8, len(out))
    struct.pack_into('<H', out, 14, struct.unpack_from('<H', data, 14)[0] + 1)
    rebuilt = Font(out)
    if any(rebuilt.mapping[code] != glyph for code, glyph in aliases.items()):
        raise ValueError('Two-byte Latin CMAP alias failed')
    if any(rebuilt.mapping[code] != glyph for code, glyph in font.mapping.items()
           if code not in aliases):
        raise ValueError('Two-byte Latin CMAP changed an unrelated character')
    return bytes(out), len(aliases)


def compact_native_fullwidth_font(data):
    """Put compact English ink into the original fullwidth Latin glyph slots.

    Some screens, including party status, only render original glyph indices.
    DigiDex needs two-byte codes. Reusing the existing fullwidth Latin slots
    satisfies both parsers while leaving kana, kanji, and punctuation intact.
    """
    font=Font(data)
    out=bytearray(data)
    changed=set()
    for code in range(48,123):
        char=chr(code)
        if not char.isascii() or not char.isalnum():continue
        full=chr(code+0xfee0)
        target=font.glyph_index(full)
        source=font.glyph_index(char)
        if target is None or source is None:continue
        if target in changed:continue
        start=font.glyph_block+16
        out[start+target*font.cell_size:start+(target+1)*font.cell_size]=(data[start+source*font.cell_size:start+(source+1)*font.cell_size])
        metric=font.metrics[source]
        offset=font.width_block
        while True:
            first,last,following=struct.unpack_from('<HHI',out,offset+8)
            if first<=target<=last:
                struct.pack_into('<bBb',out,offset+16+(target-first)*3,*metric)
                break
            if not following:raise ValueError(f'Missing native fullwidth metric {target}')
            offset=following-8
        changed.add(target)
    rebuilt=Font(out)
    if any(rebuilt.pixels(index)!=font.pixels(font.glyph_index(chr(code)))
           for code in range(48,123)
           if chr(code).isalnum() and font.glyph_index(chr(code)) is not None
           for index in [font.glyph_index(chr(code+0xfee0))]
           if index is not None):
        raise ValueError('Native fullwidth Latin compaction failed')
    return bytes(out),len(changed)


if __name__ == '__main__':
    from xros_text import Pak, Rom, rom_paths
    pak = Pak(Rom(rom_paths()['blue']).file('FONT_NFTR.PAK'))
    for index in range(pak.count):
        data, count = english_font(pak.file(index))
        font = Font(data)
        letters = ''.join(c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' if font.glyph_index(c) is not None)
        print(index, 'aliases', count, 'supported', letters)
