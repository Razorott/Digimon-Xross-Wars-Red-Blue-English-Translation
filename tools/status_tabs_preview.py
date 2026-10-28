"""Render the five revised status-tab sprites at their 21px UI pitch."""
import sys

from PIL import Image

from graphics import render_cell
from xros_text import ROOT, Pak, Rom, rom_paths

sys.path.insert(0, str(ROOT / 'tools'))
from localize_graphics import localize  # noqa: E402


def main():
    rom = Rom(rom_paths()['blue'])
    replacements, _ = localize(rom, False)
    ncgr = Pak(replacements['SPR_NCGR.PAK']).file(2234)
    ncer = Pak(replacements['SPR_NCER.PAK']).file(2234)
    nclr = Pak(rom.file('SPR_NCLR.PAK')).file(2234)

    # Use a patch of the game's purple status-screen backdrop, then overlap
    # the 32px cells at the actual 21px carousel spacing.
    screen = Image.open(ROOT / 'build/qa/blue_batch03_final/pause_menu/status_still.png').convert('RGBA')
    background = screen.crop((130, 20, 162, 36))
    width = 32 + 4 * 21
    carousel = Image.new('RGBA', (width, 16))
    for x in range(0, width, background.width):
        carousel.alpha_composite(background, (x, 0))
    for offset, bank in enumerate(range(2, 7)):
        cell = render_cell(ncgr, nclr, ncer, bank)
        carousel.alpha_composite(cell, (offset * 21, 0))

    preview = carousel.resize((carousel.width * 8, carousel.height * 8), Image.Resampling.NEAREST)
    output = ROOT / 'build/graphics/status_tabs_shadow_qa.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    preview.save(output)
    print(f'{output} native={carousel.width}x{carousel.height} preview={preview.width}x{preview.height}')


if __name__ == '__main__':
    main()
