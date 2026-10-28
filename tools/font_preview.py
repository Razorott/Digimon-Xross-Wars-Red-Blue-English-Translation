"""Render native font cells for font QA (not an in-game screenshot)."""
from PIL import Image, ImageDraw
from xros_text import ROOT, Rom, Pak, rom_paths
from xros_font import Font, english_font


def preview():
    pak = Pak(Rom(rom_paths()['blue']).file('FONT_NFTR.PAK'))
    canvas = Image.new('RGB', (720, 480), '#ffffff')
    draw = ImageDraw.Draw(canvas)
    for index in (0, 3, 4, 5, 6, 7):
        font = Font(english_font(pak.file(index))[0])
        y = (index if index < 1 else index - 2) * 70
        draw.text((4, y), f'Font {index}', fill='black')
        x = 64
        for glyph in [0, 1] + [font.glyph_index(c) for c in 'Abc .,!?:']:
            if glyph is None:
                continue
            pixels = font.pixels(glyph)
            print(index, glyph, font.metrics[glyph], sorted(set(pixels)))
            if index == 0 and glyph in (0, 1):
                print('\n'.join(''.join(str(c) for c in pixels[row * font.width:(row + 1) * font.width]) for row in range(font.height)))
            image = Image.new('RGB', (font.width, font.height), 'white')
            palette = [(255, 255, 255), (180, 180, 180), (85, 85, 85), (0, 0, 0)]
            image.putdata([palette[min(3, p)] for p in pixels])
            canvas.paste(image.resize((font.width * 2, font.height * 2), Image.Resampling.NEAREST), (x, y + 20))
            x += font.width * 2 + 12
    output = ROOT / 'build/qa/font_cells.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


if __name__ == '__main__':
    preview()
