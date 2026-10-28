"""Author English lettering directly in the game's Nitro tile resources.

Keep sprite geometry and palette banks native. Changed animation cells receive
independent tile data so alternate states cannot borrow stale Japanese pixels.
"""
import collections
import json
import struct
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from graphics import palette, tile_info, tile_pixels, cells, render_cell, render_map, contact
from xros_text import ROOT, Rom, Pak, rom_paths
from xros_font import Font


@lru_cache(None)
def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', size)


def lettering(image, text, box, size=12, color='white', outline='#202028', stroke=1,
              shadow=None, shadow_offset=(1, 1), font_path=None):
    x0,y0,x1,y1=box
    shadow_x,shadow_y=shadow_offset
    def selected_font(px):
        return font(px) if font_path is None else ImageFont.truetype(font_path,px)
    while size>6:
        f=selected_font(size); bounds=f.getbbox(text)
        if (bounds[2]-bounds[0]+stroke*2+max(0,shadow_x) <= x1-x0
                and bounds[3]-bounds[1]+stroke*2+max(0,shadow_y) <= y1-y0):break
        size-=1
    f=selected_font(size); b=f.getbbox(text)
    x=x0+(x1-x0-(b[2]-b[0]))//2-b[0]
    y=y0+(y1-y0-(b[3]-b[1]))//2-b[1]
    # Binary masks keep lettering crisp at the DS's native resolution.
    if shadow is not None:
        mask=Image.new('L',image.size)
        ImageDraw.Draw(mask).text((x+shadow_x,y+shadow_y),text,font=f,fill=255)
        image.paste(shadow,(0,0),mask.point(lambda v:255 if v>=96 else 0))
    mask=Image.new('L',image.size);d=ImageDraw.Draw(mask)
    d.text((x,y),text,font=f,fill=255,stroke_width=stroke,stroke_fill=255)
    image.paste(outline,(0,0),mask.point(lambda v:255 if v>=96 else 0))
    mask=Image.new('L',image.size);ImageDraw.Draw(mask).text((x,y),text,font=f,fill=255)
    image.paste(color,(0,0),mask.point(lambda v:255 if v>=112 else 0))


def cell_layers(ncgr, nclr, ncer, bank, keep_offsets):
    """Render selected OAM layers from one NCER cell, preserving their pixels."""
    objects=cells(ncer,bank)
    left=min(c['x'] for c in objects);top=min(c['y'] for c in objects)
    right=max(c['x']+c['w'] for c in objects);bottom=max(c['y']+c['h'] for c in objects)
    _,_,bpp,_,raw=tile_info(ncgr);colors=palette(nclr)
    image=Image.new('RGBA',(right-left,bottom-top))
    for c in reversed(objects):
        if c['offset'] not in keep_offsets:continue
        obj=Image.new('RGBA',(c['w'],c['h']))
        objraw=raw[c['offset']:]
        for y in range(c['h']//8):
            for x in range(c['w']//8):
                pixels=tile_pixels(objraw,bpp,y*(c['w']//8)+x)
                tile=Image.new('RGBA',(8,8))
                tile.putdata([(0,0,0,0) if p==0 else colors[(c['palette']*(1<<bpp)+p)%len(colors)] for p in pixels])
                obj.paste(tile,(x*8,y*8))
        if c['flip_x']:obj=obj.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if c['flip_y']:obj=obj.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image.alpha_composite(obj,(c['x']-left,c['y']-top))
    return image


def comic_caption(image, lines):
    """Set crisp English lettering into the game's existing manga burst."""
    path='C:/Windows/Fonts/arialbi.ttf'
    # Keep the type inside the flat yellow center, away from the burst spikes.
    inset_x=19;inset_y=10;max_width=image.width-inset_x*2
    size=20
    while size>10:
        f=ImageFont.truetype(path,size)
        bounds=[f.getbbox(line) for line in lines]
        heights=[b[3]-b[1] for b in bounds]
        if max(b[2]-b[0] for b in bounds)+6<=max_width and sum(heights)+3*(len(lines)-1)<=image.height-inset_y*2:break
        size-=1
    f=ImageFont.truetype(path,size);bounds=[f.getbbox(line) for line in lines]
    heights=[b[3]-b[1] for b in bounds];gap=2
    y=(image.height-(sum(heights)+gap*(len(lines)-1)))//2
    for line,b,h in zip(lines,bounds,heights):
        x=(image.width-(b[2]-b[0]))//2-b[0]
        y0=y-b[1]
        for width,color in [(3,'#ffd851'),(2,'#d33225')]:
            mask=Image.new('L',image.size);ImageDraw.Draw(mask).text((x,y0),line,font=f,fill=255,stroke_width=width,stroke_fill=255)
            image.paste(color,(0,0),mask)
        mask=Image.new('L',image.size);ImageDraw.Draw(mask).text((x,y0),line,font=f,fill=255)
        image.paste('#fffdf2',(0,0),mask)
        y+=h+gap


# The status carousel advances only 21 pixels per tab. A fixed 3x7 bitmap
# keeps every letter separate at native DS resolution; outline strokes on a
# normal font close the counters and make these labels look like solid blocks.
TAB_GLYPHS={
    'D':['110','101','101','101','101','101','110'],
    'M':['101','111','111','101','101','101','101'],
    'P':['110','101','101','110','100','100','100'],
    'S':['111','100','100','111','001','001','111'],
    'T':['111','010','010','010','010','010','010'],
    'X':['101','101','101','010','101','101','101'],
    'a':['000','000','110','001','111','101','111'],
    'e':['000','000','111','101','111','100','111'],
    'g':['000','011','101','101','011','001','110'],
    'i':['010','000','110','010','010','010','111'],
    'm':['000','000','111','111','101','101','101'],
    'o':['000','000','111','101','101','101','111'],
    'r':['000','000','101','110','100','100','100'],
    's':['000','000','011','100','111','001','110'],
    't':['010','010','111','010','010','010','011'],
    'v':['000','000','101','101','101','101','010'],
}


def tab_pixel_text(image,text,y,width=21):
    pixels=[]
    for i,char in enumerate(text):
        if char not in TAB_GLYPHS:raise ValueError(f'Unknown status-tab glyph {char!r}')
        for gy,row in enumerate(TAB_GLYPHS[char]):
            for gx,mark in enumerate(row):
                if mark=='1':pixels.append((i*4+gx,gy))
    used=len(text)*4-1
    if used>width:raise ValueError(f'Status tab {text!r} exceeds {width}px pitch')
    x=(width-used)//2
    draw=ImageDraw.Draw(image)
    for px,py in pixels:draw.point((x+px+1,y+py+1),fill='#080718')
    for px,py in pixels:draw.point((x+px,y+py),fill='#ffffff')


def label(image,text,box,size=12,fill=None,sample=None,color='white',stroke=1):
    """Clear old lettering while retaining the button's row shading."""
    x0,y0,x1,y1=box
    for y in range(y0,y1):
        if fill is not None: c=fill
        elif sample is not None:c=image.getpixel((sample,y))
        else:
            row=[image.getpixel((x,y)) for x in range(x0,x1)]
            c=collections.Counter(row).most_common(1)[0][0]
        ImageDraw.Draw(image).line((x0,y,x1-1,y),fill=c)
    lettering(image,text,box,size,color,stroke=stroke)


def native_glyph_mask(font,text):
    """Build a compact, baseline-aligned mask from the game's own NFTR glyphs."""
    glyphs=[]
    for char in text:
        lookup=char if ord(char)>0x7f else chr(ord(char)+0xfee0)
        index=font.glyph_index(lookup)
        if index is None:
            raise ValueError(f'No native graphic-font glyph for {char!r}')
        values=font.pixels(index)
        glyph=Image.new('L',(font.width,font.height))
        glyph.putdata([255 if value else 0 for value in values])
        bounds=glyph.getbbox()
        if bounds is None:
            continue
        glyphs.append(glyph.crop(bounds))
    if not glyphs:
        raise ValueError(f'Empty native graphic-font label: {text!r}')
    spacing=1
    width=sum(glyph.width for glyph in glyphs)+spacing*(len(glyphs)-1)
    height=max(glyph.height for glyph in glyphs)
    mask=Image.new('L',(width,height))
    cursor=0
    for glyph in glyphs:
        # Align each letter on a shared baseline so lowercase glyphs sit
        # naturally beside capitals after their transparent margins are cut.
        mask.paste(glyph,(cursor,height-glyph.height))
        cursor+=glyph.width+spacing
    return mask


def native_graphic_label(image,text,box,font,ink='#101010',shadow=None,
                         horizontal_fit=True):
    """Draw crisp English with the game's pixel font inside an existing panel."""
    x0,y0,x1,y1=box
    mask=native_glyph_mask(font,text)
    max_width=x1-x0
    if horizontal_fit and mask.width>max_width:
        mask=mask.resize((max_width,mask.height),Image.Resampling.NEAREST)
    if mask.height>y1-y0:
        mask=mask.resize((mask.width,y1-y0),Image.Resampling.NEAREST)
    x=x0+(x1-x0-mask.width)//2
    y=y0+(y1-y0-mask.height)//2
    if shadow is not None:
        image.paste(shadow,(x,y+1),mask)
    image.paste(ink,(x,y),mask)


def sprite_edit(ncgr,nclr,ncer,bank,edited):
    original=render_cell(ncgr,nclr,ncer,bank)
    objects=cells(ncer,bank)
    left=min(c['x'] for c in objects);top=min(c['y'] for c in objects)
    _,_,bpp,offset,source=tile_info(ncgr);raw=bytearray(source)
    colors=palette(nclr); owners={}
    for c in reversed(objects):
        for y in range(c['h']):
            for x in range(c['w']):
                tx=c['w']-1-x if c['flip_x'] else x
                ty=c['h']-1-y if c['flip_y'] else y
                p=c['offset']*8//bpp+((ty//8)*(c['w']//8)+tx//8)*64+(ty%8)*8+tx%8
                value=raw[p] if bpp==8 else (raw[p//2]>>(4*(p%2)))&15
                xy=(c['x']-left+x,c['y']-top+y)
                if value or xy not in owners:owners[xy]=(p,c['palette'])
    cache={}
    for y in range(edited.height):
        for x in range(edited.width):
            rgba=edited.getpixel((x,y))
            if rgba==original.getpixel((x,y)):continue
            if (x,y) not in owners:continue
            p,bank=owners[x,y]
            key=(rgba,bank)
            if key not in cache:
                if rgba[3]<128:value=0
                else:
                    base=bank*(1<<bpp)
                    value=min(range(1,1<<bpp),key=lambda i:sum((colors[(base+i)%len(colors)][j]-rgba[j])**2 for j in range(3)))
                cache[key]=value
            value=cache[key]
            if bpp==8:raw[p]=value
            else:raw[p//2]=(raw[p//2]&(~(15<<(4*(p%2)))&255))|(value<<(4*(p%2)))
    out=bytearray(ncgr);out[offset:offset+len(raw)]=raw
    return bytes(out)


def independent_cells(ncgr,nclr,ncer,images):
    """Repack edited animation cells without cross-cell tile aliases.

    Shapes, positions, palette assignments, and animation cell IDs stay native.
    Each object gets its requested composited crop; identical crops are shared.
    """
    count,kind,bank_offset,block=struct.unpack_from('<HHII',ncer,24)
    unit=32<<(block&255);record_size=16 if kind else 8;base=24+bank_offset
    oams=base+count*record_size
    _,_,bpp,offset,oldraw=tile_info(ncgr);colors=palette(nclr)
    raw=bytearray();lookup={};cer=bytearray(ncer);color_cache={}
    for k in range(count):
        objs=cells(ncer,k)
        if not objs:continue
        im=images.get(k,render_cell(ncgr,nclr,ncer,k))
        left=min(c['x'] for c in objs);top=min(c['y'] for c in objs)
        _,_,rel=struct.unpack_from('<HHI',ncer,base+k*record_size)
        for j,c in enumerate(objs):
            crop=im.crop((c['x']-left,c['y']-top,c['x']-left+c['w'],c['y']-top+c['h']))
            if c['flip_x']:crop=crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if c['flip_y']:crop=crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            values=[]
            for ty in range(c['h']//8):
                for tx in range(c['w']//8):
                    for y in range(8):
                        for x in range(8):
                            rgba=crop.getpixel((tx*8+x,ty*8+y));key=(rgba,c['palette'])
                            if key not in color_cache:
                                color_cache[key]=0 if rgba[3]<128 else min(range(1,1<<bpp),key=lambda p:sum((colors[(c['palette']*(1<<bpp)+p)%len(colors)][z]-rgba[z])**2 for z in range(3)))
                            values.append(color_cache[key])
            payload=bytes(values) if bpp==8 else bytes(values[z]|values[z+1]<<4 for z in range(0,len(values),2))
            if payload not in lookup:
                raw.extend(bytes((-len(raw))%unit));lookup[payload]=len(raw)//unit;raw.extend(payload)
            tile=lookup[payload]
            if tile>1023:raise ValueError('Sprite exceeds OAM addressing')
            attr_offset=oams+rel+j*6+4
            attr=struct.unpack_from('<H',cer,attr_offset)[0]
            struct.pack_into('<H',cer,attr_offset,(attr&0xfc00)|tile)
    out=bytearray(ncgr[:offset])+raw
    struct.pack_into('<I',out,8,len(out));struct.pack_into('<I',out,20,len(out)-16);struct.pack_into('<I',out,40,len(raw))
    return bytes(out),bytes(cer)


def caption_line(image,text,box,highlight=None,size=16):
    x0,y0,x1,y1=box
    path='C:/Windows/Fonts/ariblk.ttf'
    while size>10:
        f=ImageFont.truetype(path,size);bounds=f.getbbox(text)
        if bounds[2]-bounds[0]+6<=x1-x0 and bounds[3]-bounds[1]+4<=y1-y0:break
        size-=1
    f=ImageFont.truetype(path,size);bounds=f.getbbox(text)
    x=x0+(x1-x0-(bounds[2]-bounds[0]))//2-bounds[0]
    y=y0+(y1-y0-(bounds[3]-bounds[1]))//2-bounds[1]
    d=ImageDraw.Draw(image)
    # Intro cards use white lettering with a dark ink edge. Names and story
    # keywords are red in the Japanese artwork, so preserve that emphasis.
    d.text((x+1,y+1),text,font=f,fill='#242424',stroke_width=2,stroke_fill='#242424')
    d.text((x,y),text,font=f,fill='#fffdf7',stroke_width=2,stroke_fill='#202026')
    marks=[highlight] if isinstance(highlight,str) else (highlight or [])
    for mark in marks:
        if mark and mark in text:
            prefix,marked,_=text.partition(mark)
            d.text((x+round(d.textlength(prefix,font=f)),y),marked,font=f,fill='#ff2908')


def caption(ncgr,nclr,nscr,lines,size=16,highlights=None):
    im=Image.new('RGBA',(256,192))
    gap=24; start=((192-len(lines)*gap)//16)*8
    for j,text in enumerate(lines):
        if len(text)>30:raise ValueError('Intro caption exceeds 30 columns')
        caption_line(im,text,(12,start+j*gap,244,start+j*gap+20),
                     (highlights or {}).get(j),size)
    try:return encode_map(ncgr,nclr,nscr,im)
    except ValueError:
        if size>10:return caption(ncgr,nclr,nscr,lines,size-1,highlights)
        raise


def encode_map(ncgr,nclr,nscr,im):
    _,_,bpp,offset,raw=tile_info(ncgr)
    width,height,oldentries=__import__('graphics').map_info(nscr)
    if im.size!=(width,height):raise ValueError('Graphic dimensions changed')
    colors=palette(nclr);palette_size=1<<bpp
    bank_count=max(1,min(16,len(colors)//palette_size))
    def map_index(tx,ty):
        # NSCR entries are stored as 32x32-tile screen blocks, even when the
        # image uses only a partial block such as the 256x192 intro captions.
        blocks_per_row=max(1,width//256)
        block=(ty//32)*blocks_per_row+(tx//32)
        return block*1024+(ty%32)*32+(tx%32)
    tiles=[bytes(bpp*8)];lookup={tiles[0]:0};entries=[0]*len(oldentries);color_cache={}
    def nearest(rgba,bank):
        key=(rgba,bank)
        if key not in color_cache:
            if rgba[3]<128:color_cache[key]=(0,0)
            else:
                base=bank*palette_size
                value=min(range(1,palette_size),key=lambda k:sum((colors[(base+k)%len(colors)][j]-rgba[j])**2 for j in range(3)))
                error=sum((colors[(base+value)%len(colors)][j]-rgba[j])**2 for j in range(3))
                color_cache[key]=(value,error)
        return color_cache[key]
    for ty in range(height//8):
        for tx in range(width//8):
            source_entry=oldentries[map_index(tx,ty)]
            preferred=(source_entry>>12)&15
            if preferred>=bank_count:preferred%=bank_count
            tile_rgba=[im.getpixel((tx*8+x,ty*8+y)) for y in range(8) for x in range(8)]
            if any(rgba[3]>=128 for rgba in tile_rgba):
                scores=[]
                for candidate in range(bank_count):
                    error=sum(nearest(rgba,candidate)[1] for rgba in tile_rgba if rgba[3]>=128)
                    scores.append((error,candidate!=preferred,candidate))
                bank=min(scores)[2]
            else:bank=preferred
            p=[nearest(rgba,bank)[0] for rgba in tile_rgba]
            tile=bytes(p) if bpp==8 else bytes(p[k]|(p[k+1]<<4) for k in range(0,64,2))
            if tile not in lookup:lookup[tile]=len(tiles);tiles.append(tile)
            entries[map_index(tx,ty)]=(bank<<12)|lookup[tile]
    new=b''.join(tiles)
    if len(new)>len(raw):
        raise ValueError(f'Caption exceeds native VRAM allocation: {len(new)} > {len(raw)}')
    out=bytearray(ncgr);out[offset:offset+len(raw)]=new.ljust(len(raw),b'\0')
    sm=bytearray(nscr);struct.pack_into(f'<{len(entries)}H',sm,36,*entries)
    return bytes(out),bytes(sm),im


CAPTIONS={
33:["I'm Taiki Kudo!",'A middle school student','from Koto, Tokyo.'],
34:['One day, I heard a voice','calling for help.','Following that voice...'],
35:['My friends and I were','sent to another world:','the Digital World!'],
36:['There, we met creatures','made of digital data,','known as Digimon.'],
37:['A hotheaded troublemaker','who dreams of becoming','the King of the Digimon:', 'Shoutmon!'],
38:['A powerful fighter','you can always count on:', 'Ballistamon!'],
39:['A wandering spirit','who loves his freedom:', 'Dorulumon!'],
40:['In the Digital World,','mighty Digimon we had','never seen awaited us.'],
41:['And now, our','new adventure','was about to begin...'],
}

CAPTION_HIGHLIGHTS={
    33:{0:'Taiki Kudo'},
    34:{0:'voice'},
    35:{2:'Digital World'},
    36:{2:'Digimon'},
    37:{2:'King',3:'Shoutmon!'},
    38:{2:'Ballistamon!'},
    39:{2:'Dorulumon!'},
    41:{1:'new adventure'},
}


def english_logo(size,version=None):
    # A new mark modeled on the original's gold headline, chrome crossbar,
    # orange STORY tab and outward-pointing lightning. Work at 4x resolution;
    # all artwork is then reduced by one uniform factor with a safe edge.
    s=4; w,h=size
    im=Image.new('RGBA',(w*s,h*s));d=ImageDraw.Draw(im)
    def poly(points,fill,outline=None,width=1):
        p=[(x*s,y*s) for x,y in points]
        d.polygon(p,fill=fill)
        if outline:d.line(p+[p[0]],fill=outline,width=width*s,joint='curve')
    def word(value,box,face,top,bottom,outer='#70e7fa'):
        from PIL import ImageColor
        x0,y0,x1,y1=[v*s for v in box]
        font_path='C:/Windows/Fonts/ariblk.ttf' if face=='heavy' else 'C:/Windows/Fonts/impact.ttf'
        px=(y1-y0)*2
        while True:
            ft=ImageFont.truetype(font_path,px)
            b=ft.getbbox(value)
            if (b[2]-b[0] <= x1-x0-12*s and b[3]-b[1] <= y1-y0-5*s) or px<=7:break
            px-=1
        x=x0+(x1-x0-b[2]+b[0])//2-b[0]
        y=y0+(y1-y0-b[3]+b[1])//2-b[1]
        # Fully opaque inner backdrop stops the busy title art from showing
        # through the D, O, A and R counters after palette reduction.
        if value=='DIGIMON':
            poly([(x0//s+6,y0//s+8),(x1//s-6,y0//s+8),
                  (x1//s-12,y1//s-4),(x0//s+12,y1//s-4)],'#102a57')
        for width,color in ((4*s,outer),(3*s,'#102040'),(2*s,'#fff8dc'),(s,'#17264d')):
            d.text((x,y),value,font=ft,fill=color,stroke_width=width,stroke_fill=color)
        mask=Image.new('L',im.size)
        ImageDraw.Draw(mask).text((x,y),value,font=ft,fill=255)
        a=ImageColor.getrgb(top);bcol=ImageColor.getrgb(bottom)
        shade=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shade)
        for yy in range(y0,y1):
            q=(yy-y0)/max(1,y1-y0)
            sd.line((x0,yy,x1,yy),fill=tuple(round(a[k]*(1-q)+bcol[k]*q) for k in range(3))+(255,))
        im.paste(shade,(0,0),mask)
    # The two lightning wings echo the Japanese logo's irregular cyan silhouette.
    for side in (-1,1):
        def xp(x):return x if side==-1 else 216-x
        poly([(xp(27),92),(xp(5),102),(xp(28),109),(xp(9),136),
              (xp(51),113),(xp(39),102)],'#0c488d','#91f4ff',2)
        poly([(xp(25),100),(xp(13),103),(xp(35),107),(xp(18),126),
              (xp(44),108)],'#2faadf','#e9fdff',1)
    poly([(20,48),(33,37),(180,37),(196,48),(207,77),
          (199,110),(174,123),(37,123),(14,108),(8,77)],'#122957','#abf6ff',3)
    poly([(25,52),(36,43),(177,43),(191,54),(199,77),
          (192,103),(172,116),(40,116),(22,102),(16,77)],'#224c8b','#f9fbff',2)
    poly([(28,64),(185,64),(198,78),(191,105),(173,111),
          (39,111),(24,99),(19,78)],'#102a57','#6be3fb',2)
    poly([(26,67),(188,67),(195,79),(187,102),(174,106),
          (39,106),(29,98),(23,80)],'#17396d','#5aa7d2',1)
    # Small gold break and a chrome highlight make the mark read at native size.
    poly([(43,50),(172,50),(187,63),(31,63)],'#e2860e','#fff4be',1)
    poly([(42,55),(174,55),(181,60),(36,60)],'#ffd441')
    poly([(43,109),(172,109),(163,115),(51,115)],'#b9e1f4','#ffffff',1)
    word('DIGIMON',(12,4,204,49),'heavy','#fff441','#e3890c',outer='#35ccea')
    poly([(85,51),(169,51),(164,67),(91,67)],'#f39a12','#fff2ae',1)
    word('STORY',(91,51,165,65),'impact','#fffdf4','#f8d899',outer='#9b4716')
    word('SUPER',(28,51,84,66),'impact','#ffffff','#bedcf0',outer='#267bb5')
    word('XROS WARS',(19,70,197,105),'heavy','#ffffff','#829dca',outer='#6be6fa')
    poly([(60,107),(156,107),(169,119),(154,139),(61,139),(47,120)],'#10284e','#b9f6ff',2)
    poly([(64,112),(152,112),(159,120),(150,132),(64,132),(57,120)],
         '#0d4da0' if version=='BLUE' else '#9b1a37','#ffffff',1)
    word(version or '',(56,110,160,135),'impact',
         '#e9ffff' if version=='BLUE' else '#fff5db',
         '#3d8fdd' if version=='BLUE' else '#e35242',
         outer='#63ddff' if version=='BLUE' else '#ffb493')
    fitted=im.resize((round(w*.88),round(h*.88)),Image.Resampling.BILINEAR)
    canvas=Image.new('RGBA',size)
    canvas.alpha_composite(fitted,((w-fitted.width)//2,(h-fitted.height)//2))
    return canvas


def intro_english_logo(image):
    """Metallic intro mark within the original ring and spike composition."""
    d=ImageDraw.Draw(image)
    # The source art is silver and dark crimson. Cover only the Japanese
    # lettering, leaving its circle and outer lightning visible.
    d.rectangle((25,54,231,128),fill='#080c17')
    outer=[(37,85),(27,80),(35,62),(60,62),(66,52),(193,52),
           (199,62),(222,62),(231,80),(219,88),(233,103),(219,123),
           (38,123),(23,103)]
    d.polygon(outer,fill='#551b2b',outline='#f0d8d9',width=2)
    inner=[(44,84),(36,78),(42,68),(65,68),(71,59),(188,59),
           (194,68),(216,68),(223,79),(212,89),(224,102),
           (214,116),(42,116),(33,102)]
    d.polygon(inner,fill='#14202d',outline='#cd7579',width=2)
    d.polygon([(48,71),(67,71),(74,63),(183,63),(190,71),(209,71),
               (215,80),(43,80)],fill='#83444e',outline='#f2e4e3',width=1)
    d.polygon([(44,88),(212,88),(221,102),(209,112),(47,112),(35,102)],
              fill='#263044',outline='#f0d8d9',width=2)
    d.line((42,86,214,86),fill='#faeeee',width=1)
    d.line((45,113,211,113),fill='#9c535b',width=1)
    lettering(image,'DIGIMON',(58,62,199,82),19,color='#fff7ef',outline='#491c2a',stroke=2)
    lettering(image,'XROS WARS',(36,89,220,112),24,color='#fff7ef',outline='#351927',stroke=2)
    return image


def ribbon_banner(image,text,orange=False):
    """Retain the original GUI's tapered, layered, high-contrast banner style."""
    original=image.copy()
    w,h=image.size
    image.paste((0,0,0,0),(0,0,w,h))
    d=ImageDraw.Draw(image)
    top=3 if h<=32 else 11
    bottom=min(h-2,top+(24 if h<=32 else 32))
    right=min(w-4,original.getbbox()[2] if original.getbbox() else w-4)
    dark='#6b3018' if orange else '#074338'
    main='#dd8127' if orange else '#1baf73'
    light='#ffedaf' if orange else '#a7f9db'
    shadow=[(5,top+4),(right-11,top+4),(right,bottom-8),
            (right-8,bottom),(8,bottom),(0,bottom-9)]
    face=[(6,top),(right-13,top),(right-3,top+8),
          (right-11,bottom-4),(10,bottom-4),(3,bottom-11)]
    d.polygon(shadow,fill='#112335',outline='#f5f8e7',width=2)
    d.polygon(face,fill=main,outline=light,width=2)
    d.line((9,top+4,right-18,top+4),fill='#f8fff3',width=2)
    d.line((11,bottom-8,right-17,bottom-8),fill=dark,width=2)
    d.polygon([(right-20,top+3),(right-11,top+3),(right-7,top+8),
               (right-12,top+14),(right-22,top+14)],fill=dark,outline=light)
    # The small green crest comes from the Japanese banner itself, so the
    # English replacement remains recognizably part of the game's interface.
    if not orange and w>=128 and h>32:
        crest=original.crop((max(0,right-28),0,right+2,min(h,19)))
        image.alpha_composite(crest,(right-28,max(0,top-10)))
    text_right=right-17 if not orange else right-6
    text_box=(9,top+5,text_right,bottom-8) if h>32 else (9,top+2,text_right,bottom-3)
    lettering(image,text,text_box,
              20 if h>32 else 15,color='#fffdf4',outline=dark,stroke=1)
    return image


def localize(rom,preview=False):
    paks={n:Pak(rom.file(n)) for n in ['SPR_NCGR.PAK','SPR_NCLR.PAK','SPR_NCER.PAK','BG_NCGR.PAK','BG_NSCR.PAK','BG_NCLR.PAK']}
    small_graphic_font=Font(Pak(rom.file('FONT_NFTR.PAK')).file(5))
    changed=collections.defaultdict(dict);manifest=[];previews=[];independent=collections.defaultdict(dict)
    def edit(i,k,description,callback):
        nc=paks['SPR_NCGR.PAK'].file(i);cl=paks['SPR_NCLR.PAK'].file(i);ce=paks['SPR_NCER.PAK'].file(i)
        im=render_cell(nc,cl,ce,k);callback(im)
        independent[i][k]=im
        previews.append((f'SPR {i}:{k} {description}',im));manifest.append({'archive':'SPR_NCGR.PAK + SPR_NCER.PAK','entry':i,'bank':k,'english':description})
    for i,v in [(33,'RED'),(34,'BLUE')]:
        edit(i,0,f'Digimon Story Super Xros Wars {v}',lambda im,v=v:im.paste(english_logo(im.size,v)))
    # DigiLab hexagon labels are independent sprite banks, separate from the
    # dialogue/prompts in MESPAK01 table 4.
    lab_labels={16:'DigiFusion',17:'Jogress Up',18:'Melody Play',19:'Digimon List',
                20:'DigiFusion',21:'DigiFusion',22:'DigiFusion',23:'Jogress Up',24:'Jogress Up',
                25:'Jogress Up',26:'Melody Play',27:'Melody Play',28:'Melody Play',
                29:'Digimon List',30:'Digimon List',31:'Digimon List'}
    for k,t in lab_labels.items():
        def lab_badge(im,t=t,k=k):
            im.paste((0,0,0,0),(0,0,*im.size))
            d=ImageDraw.Draw(im)
            d.rounded_rectangle((1,1,78,12),radius=3,fill='#242538',outline='#fff0d0',width=1)
            d.line((5,13,75,13),fill='#fdb23e',width=2)
            lettering(im,t,(3,1,77,12),11,color='white',stroke=0)
        edit(124,k,t,lab_badge)
    # Battle's Y/X labels are baked into sprite entry 1987. Repaint only the
    # button's inner blue field, clipped to the original panel silhouette, then
    # use compact white lettering with the game's navy pixel outline. This
    # keeps the bevels and controller icons intact and avoids rectangular masks.
    def battle_button(im,text,button):
        d=ImageDraw.Draw(im)
        if button=='x':
            x0={10:26,11:26,12:26,13:26,14:26,15:25,16:25,17:24,18:24,
                19:24,20:24,21:24,22:24}
            x1={y:93 for y in range(10,22)};x1[22]=88
            box=(25,8,92,22)
        else:
            x0={y:0 for y in range(10,23)}
            x1={y:72 for y in range(10,23)}
            box=(2,8,72,22)
        # These row spans follow the actual beveled panel silhouette. The two
        # native blue bands continue through the old glyph area, so no patch
        # edge is visible when the Japanese text is removed.
        for y in range(10,23):
            if y not in x0:continue
            color='#acc5ff' if y<13 else '#105aff'
            d.line((x0[y],y,x1[y],y),fill=color)
        if button=='x':
            for y in (23,24):d.line((25,y,91,y),fill='#3952c5')
            d.line((24,25,92,25),fill='#3952c5')
        else:
            for y in (23,24):d.line((0,y,70,y),fill='#3952c5')
        lettering(im,text,box,10,color='#fffdf4',outline='#12377c',stroke=1,
                  shadow='#081b60',shadow_offset=(1,1))
    for k in (1,3,5):
        edit(1987,k,'Start Battle',
             lambda im:battle_button(im,'Start Battle','x'))
    for k in (6,7,8):
        edit(1987,k,'All Tactics',
             lambda im:battle_button(im,'All Tactics','y'))
    # The action wheel's six Japanese captions are separate two-frame sprite
    # states. Sample the panel fill from its clean inner edge, then letter
    # with the game's compact NFTR bitmap font to keep the original capsule,
    # arrows, bevel, and pixel rhythm intact.
    action_labels={21:'Command',22:'Command',23:'Special',24:'Special',
                   25:'DigiXross',26:'DigiXross',27:'Item',28:'Item',
                   29:'Tactics',30:'Tactics',31:'Wait',32:'Wait'}
    for k,text in action_labels.items():
        def action_label(im,text=text,k=k):
            left=14 if im.width==76 else 16
            x0=left+5;x1=left+43
            for y in range(9,22):
                ImageDraw.Draw(im).line((x0,y,x1-1,y),fill=im.getpixel((x0,y)))
            native_graphic_label(im,text,(x0,9,x1,22),small_graphic_font,
                                 ink='#101010',shadow='#627b94')
        edit(1971,k,text,lambda im,k=k,text=text:action_label(im,text,k))
    # The blue B/Back capsule is another pair of animation banks in entry
    # 1987. Keep the button glyph and native outline; repaint only the blue
    # text field using row samples from its clean left edge.
    for k in (10,11):
        def back_badge(im):
            x0,x1=4,46
            for y in range(10,24):
                ImageDraw.Draw(im).line((x0,y,x1-1,y),fill=im.getpixel((x0,y)))
            native_graphic_label(im,'Back',(5,9,44,24),small_graphic_font,
                                 ink='#ffffff',shadow='#12377c')
        edit(1987,k,'Back',back_badge)
    # Taiki's battle cut-ins are separate burst-text OAM layers in entry 1993.
    # Keep the original burst and replace only the Japanese text tiles with
    # compact English captions in the same white/red/gold manga style.
    cutins={0:['Let\'s go, everyone!!'],1:['Let\'s go, everyone!!'],
            2:['Keep it up!','Almost there!'],3:['Keep it up!','Almost there!'],
            4:['DigiXross!!'],5:['DigiXross!!'],6:['DigiXross!!'],
            7:['Let\'s retreat','for now!'],8:['Let\'s retreat','for now!']}
    for k,lines in cutins.items():
        def cutin(im,k=k,lines=lines):
            background=cell_layers(paks['SPR_NCGR.PAK'].file(1993),
                                   paks['SPR_NCLR.PAK'].file(1993),
                                   paks['SPR_NCER.PAK'].file(1993),k,
                                   {2304,4352,6400})
            im.paste(background)
            comic_caption(im,lines)
        description=' / '.join(lines)
        edit(1993,k,description,cutin)
    # The command wheel's hand-icon caption is a separate four-character
    # graphic (めいれい). Keep it as “Command”; it is not the Y-button label.
    def command_caption(im):
        im.paste((0,0,0,0),(0,0,*im.size))
        lettering(im,'Command',(1,0,im.width-1,im.height),9,
                  color='#fff4c1',outline='#d83c20',stroke=1)
    edit(106,0,'Command',command_caption)
    # A separate Digimon status badge uses three color states for the same
    # Japanese レベルアップ label. Keep the native frame and palette shading.
    for k,text,face,shade in [(1,'Level Up','#00bd83','#008c60'),
                              (2,'Job','#deb400','#ac8300')]:
        def status_label(im,text=text,face=face,shade=shade):
            im.paste((0,0,0,0),(0,0,*im.size))
            d=ImageDraw.Draw(im)
            d.rounded_rectangle((1,1,46,14),radius=2,fill=face,outline='#ffffff',width=1)
            d.line((4,12,43,12),fill=shade,width=1)
            lettering(im,text,(3,2,45,12),10,color='#111111',
                      outline='#ffffff',stroke=0)
        edit(127,k,text,status_label)
    # DigiFusion requirement heading is baked into its own sprite, apart from
    # the matching text-table heading used elsewhere in the lab.
    def fusion_requirements(im):
        im.paste((0,0,0,0),(0,0,*im.size))
        lettering(im,'DigiFusion Requirements',(1,0,im.width-1,im.height),10,
                  color='#f4f4f4',outline='#5b5b5b',stroke=1)
    edit(127,6,'DigiFusion Requirements',fusion_requirements)
    # Recruiting banner (なかまぼしゅう!!) has three animation cells.
    for k in range(3):
        def recruiting(im):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,'Recruiting!!',(1,0,im.width-1,im.height),10,
                      color='#f62900',outline='#ffffff',stroke=1)
        edit(138,k,'Recruiting!!',recruiting)
    for i in [39,40]:
        def copyright(im):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,'(C) Akiyoshi Hongo / Toei Animation',(3,0,253,10),9,stroke=1)
            lettering(im,'TV Asahi / Dentsu',(3,10,253,20),9,stroke=1)
            lettering(im,'(C) 2011 NBGI',(3,21,253,31),9,stroke=1)
        edit(i,0,'English copyright attribution',copyright)
    # The save/write wait message is a separate 192x16 sprite, not a message
    # table entry. Keep its lettering within its native OAM width.
    def power_wait(im):
        im.paste((0,0,0,0),(0,0,*im.size))
        lettering(im,'Please wait. Do not power off.',
                  (2,0,im.width-2,im.height),13,
                  color='#399fff',outline='#102a7a',stroke=1)
    edit(228,3,'Please wait. Do not power off.',power_wait)
    # Two separate battle-result states: a party Digimon fell (blue check),
    # or the target was defeated (orange ring). Preserve the status symbols.
    for k,t,col,outline in [(0,'Down!','#dcecff','#3163bb'),
                            (1,'Defeated!','#fff2bb','#bd4900')]:
        def knockout(im,t=t,col=col,outline=outline):
            im.paste((0,0,0,0),(16,0,im.width,im.height))
            lettering(im,t,(17,0,im.width-1,im.height),12,
                      color=col,outline=outline,stroke=1)
        edit(227,k,t,knockout)
    # Title menu states share tiles: apply every complete state consistently.
    for k in range(5):
        def title(im,k=k):
            ys=[(8,24)] if k in [0,4] else [(8,24),(24,40),(40,56)]
            words=['Start Adventure'] if k==0 else ['Continue'] if k==4 else ['Continue','New Game','Reload Challenge']
            for (a,b),word in zip(ys,words):label(im,word,(20,a,156,b),12,sample=12)
        edit(38,k,'Title menu',title)
    # Generic confirm/cancel controls, preserving their frames.
    for k,text in enumerate(['Cancel','Cancel','Species','Species','Retry','Retry','OK','OK','Auto','Auto']):
        edit(42,k,text,lambda im,t=text:label(im,t,(6,12,58,29),11,fill='#63d000'))
    # Root Xros Loader icons, including selection/animation variants.
    for i in [196,198]:
        for k,t in enumerate(['Stats','Moves','Equip','Formation','Items','Map','Info'],1):
            edit(i,k,t,lambda im,t=t:label(im,t,(8,29,54,44),11,fill='#e90013'))
    for i,ks in [(110,range(5)),(147,range(1,4)),(194,[0]),(196,[8]),(198,[8])]:
        for k in ks:
            t={1:'OK',2:'Next',3:'Finish',4:'Finish'}.get(k,'Back') if i==110 else ('OK' if i==147 and k==1 else 'Back')
            edit(i,k,t,lambda im,t=t:label(im,t,(18,6,im.width-5,min(21,im.height-2)),10,fill='#315aca'))
    for i,t in [(47,'World Map'),(75,'Farm Island'),(76,'Move'),(77,'Digimon'),(78,'Farm Island'),(104,'DigiFarm'),(105,'Farm Island'),(111,'Digimon Growth'),(112,'Live Event Start'),(113,'Send Expedition'),(114,'Change Traits'),(115,'Assign Job'),(140,'Live Event Report'),(141,'Job Report'),(142,'Expedition Report'),(143,'Level Up Report')]:
        count=struct.unpack_from('<H',paks['SPR_NCER.PAK'].file(i),24)[0]
        for k in range(count):
            def banner(im,t=t,i=i,k=k):
                if i==47 and k==1:t='Area Map'
                bbox=im.getbbox()
                if not bbox:return
                x0,y0,x1,y1=bbox
                if i in [75,76,77,78]:
                    # Preserve the original panel, ornaments, and animation glow.
                    if i==75:box=(62,5,163,26)
                    else:box=(15,9,min(79,im.width-9),27)
                    label(im,t,box,14,fill=im.getpixel((box[0]-3,box[1]+2)))
                else:
                    ribbon_banner(im,t,orange=i in [140,141,142,143])
            edit(i,k,t,banner)
    for i,words in [(35,['Trial Version']),(36,['Blue Flare','Twilight','Blue Flare / Twilight','Blue Flare / Twilight']),(74,['Farm Settings']),(86,['Switch Camera']),(96,['Party']),(97,['DigiBank']),(98,['Expedition'])]:
        for k,t in enumerate(words):
            def heading(im,t=t):
                im.paste((0,0,0,0),(0,0,*im.size))
                lettering(im,t,(1,1,im.width-1,im.height-1),18,stroke=1)
            edit(i,k,t,heading)
    for i,t in [(84,'Train'),(85,'Job')]:
        for k in [0,1]:
            def farm_heading(im,t=t,i=i,k=k):
                # The selected Train cell stores its Japanese caption in a
                # lower OAM row than the alternate animation cell. Clear the
                # full source glyph row before drawing English; otherwise the
                # Japanese bottom halves remain visible beneath “Train”.
                box=(0,8,54,26) if i==84 and k==0 else (0,0,51,min(17,im.height))
                label(im,t,box,10,fill=(0,0,0,0))
            edit(i,k,t,farm_heading)
    for i,t in [(116,'Sort'),(117,'EXP'),(118,'Found Items'),(119,'Crafted Gear'),(120,'Stats Up'),(125,'Switch'),(126,'Stats'),(131,'DigiLevel Up'),(132,'Fusion Breed'),(213,'Sort'),(220,'Remove')]:
        count=struct.unpack_from('<H',paks['SPR_NCER.PAK'].file(i),24)[0]
        for k in range(count):
            def small_label(im,t=t,i=i):
                if i in [118,119,120]:
                    original=im.copy()
                    label(im,t,(18,5,93,19),10,fill=(230,246,246,255),color='#202020',stroke=0)
                    im.paste(original.crop((0,0,18,24)),(0,0))
                else:
                    label(im,t,(18,7,im.width-6,min(im.height-3,24)),11,fill='#285cc6')
            edit(i,k,t,small_label)
    for k in range(16,32):
        t=['Play Info','Quests','Digimon','DigiDex'][(k-16)%4] if k<20 else ['Play Info']*3+['Quests']*3+['Digimon']*3+['DigiDex']*3
        if isinstance(t,list):t=t[k-20]
        edit(221,k,t,lambda im,t=t:label(im,t,(4,2,im.width-4,14),10,fill='#dc7918'))
    # Late GUI sprites supply the status tabs, button legends and shopping/
    # DigiBank headings. These are not ordinary message strings.
    late_headings=['Left','Owned','Price','Level','Best','Group','Found Items','EXP',
                   'Event Result','Crafted Gear','Stat Changes']
    for k,t in enumerate(late_headings):
        def little(im,t=t):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,t,(0,1,im.width,15),10,color='white',stroke=0)
        edit(2217,k,t,little)
    legends=['Back','Sort','OK','Back','Sort','OK','Get EXP','Found Items',
             'Next','Finish','To Stage','Map','Digimon List']
    def controller_badge(im,t,button,tone='blue'):
        if t == 'Back':
            # Keep the original capsule, bevels, and printed B-button icon.
            # The caption sits in the flat center field; repaint just that field
            # using the source variant's color, then replace only its lettering.
            field='#e6f6f6' if tone=='yellow' else '#94c5ff'
            outline='#626262' if tone=='yellow' else '#202028'
            shadow='#626262' if tone=='yellow' else '#414141'
            ImageDraw.Draw(im).rectangle((19,11,55,20),fill=field)
            lettering(im,t,(19,10,55,21),9,color='#fffef6',outline=outline,
                      stroke=1,shadow=shadow,shadow_offset=(0,1))
            return
        im.paste((0,0,0,0),(0,0,*im.size))
        d=ImageDraw.Draw(im);left=2 if im.width>64 else 5;right=im.width-4
        base={'blue':'#264c9b','orange':'#b7480c','yellow':'#c9a31d'}[tone]
        d.rounded_rectangle((left,7,right,24),radius=6,fill=base,outline='#f9faff',width=1)
        d.ellipse((left+4,10,left+16,22),fill='#dbeaff',outline='#10204f',width=1)
        lettering(im,button,(left+6,11,left+15,21),9,color='#21346b',stroke=0)
        lettering(im,t,(left+18,9,right-2,23),10,color='white',stroke=0)
    for k,t in enumerate(legends):
        button=['B','X','A','B','X','A','X','X','A','A','B','B','X'][k]
        tone='orange' if k in [1,4,6,7,12] else 'yellow' if k in [3,5] else 'blue'
        edit(2218,k,t,lambda im,t=t,b=button,c=tone:controller_badge(im,t,b,c))
    for k,t in [(0,'Digimon List')]:
        def list_heading(im,t=t):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,t,(3,2,im.width-3,29),20,color='#78f5ed',stroke=1)
        edit(2224,k,t,list_heading)
    # Both states use the same 128x32 quest banner resource. Clear the old
    # Japanese glyphs completely; the English stays inside the native OAM box.
    for k,t,base,edge in [(0,'QUEST CLEAR!','#ffe3a0','#8e570b'),
                           (1,'Requirements','#d5ebff','#3267bb')]:
        def quest_result(im,t=t,base=base,edge=edge):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,t,(3,2,im.width-3,im.height-2),22,
                      color=base,outline=edge,stroke=2)
            lettering(im,t,(4,3,im.width-4,im.height-3),20,
                      color='#fffaf0',outline=base,stroke=1)
        edit(2242,k,t,quest_result)
    for k,t in [(14,'Back'),(16,'OK')]:
        edit(2231,k,t,lambda im,t=t:controller_badge(im,t,'B' if t=='Back' else 'A'))
    tab_words=['Stats','Moves','DigiXross','Trait','Param']
    for k in range(2,12):
        t=tab_words[(k-2)%5]
        def tab(im,t=t):
            im.paste((0,0,0,0),(0,0,*im.size))
            if t=='DigiXross':
                tab_pixel_text(im,'Digi',0)
                tab_pixel_text(im,'Xross',8)
            else:
                tab_pixel_text(im,t,4)
        edit(2234,k,t,tab)
    for k,t in enumerate(['Live Event Report','Job Report','Expedition Report','Digimon Growth']):
        def report_heading(im,t=t):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,t,(2,3,im.width-2,28),20,color='white',stroke=1)
        edit(2235,k,t,report_heading)
    for i,t in [(2244,'Quest Progress'),(2245,'Item Shop'),(2246,'Farm Shop')]:
        def shop_heading(im,t=t):
            im.paste((0,0,0,0),(0,0,*im.size))
            lettering(im,t,(2,2,im.width-2,29),19,color='#fff3dd',stroke=1)
        edit(i,0,t,shop_heading)
    for k,t in enumerate(['Yes','Yes','No','No']):
        edit(2249,k,t,lambda im,t=t:label(im,t,(5,2,im.width-5,21),12,sample=10,color='white',stroke=0))
    for k,t in enumerate(['DigiBit Bank','Withdraw','Deposit','ATM Close']):
        edit(2250,k,t,lambda im,t=t:label(im,t,(4,2,im.width-4,20),14,sample=2,color='white',stroke=0))
    # Entry 127 bank 0 is Cancel, bank 1 is Level Up, and bank 2 is Job.
    # Keep these separate: they share an atlas entry but are distinct UI labels.
    def cancel_badge(im):
        # Keep the native X icon and button frame; replace only the text.
        label(im,'Cancel',(15,1,47,15),9,color='white',stroke=1)
    edit(127,0,'Cancel',cancel_badge)
    # Entry 138 is the red-and-white Recruiting!! banner. Its three OAM
    # animation banks are reused by the same banner; do not alias them to a
    # title prompt. The title's Start Adventure label is a separate sprite.
    for k in range(1,7):
        t='Secret Password' if k in [1,3,4] else 'Digimon Reload'
        def reload(im,t=t):
            label(im,'Secret' if t=='Secret Password' else 'Digimon',(7,42,73,56),12,fill='#00565b')
            label(im,'Password' if t=='Secret Password' else 'Reload',(7,56,73,71),12,fill='#00565b')
        edit(148,k,t,reload)
    for k in range(1,5):edit(149,k,'Preparing',lambda im:label(im,'Preparing',(2,3,im.width-2,27),17,fill=(0,0,0,0)))
    for i,images in independent.items():
        nc,ce=independent_cells(paks['SPR_NCGR.PAK'].file(i),paks['SPR_NCLR.PAK'].file(i),paks['SPR_NCER.PAK'].file(i),images)
        changed['SPR_NCGR.PAK'][i]=nc;changed['SPR_NCER.PAK'][i]=ce
    for i,lines in CAPTIONS.items():
        nc,sm,im=caption(paks['BG_NCGR.PAK'].file(i),paks['BG_NCLR.PAK'].file(31),paks['BG_NSCR.PAK'].file(i),lines,highlights=CAPTION_HIGHLIGHTS.get(i))
        changed['BG_NCGR.PAK'][i]=nc;changed['BG_NSCR.PAK'][i]=sm
        previews.append((f'Intro {i}',im));manifest.append({'archive':'BG_NCGR.PAK + BG_NSCR.PAK','entry':i,'english':lines})
    # Illustrated intro's Japanese series logo is a separate tiled background.
    nc=paks['BG_NCGR.PAK'].file(23);sm=paks['BG_NSCR.PAK'].file(23)
    cl=paks['BG_NCLR.PAK'].file(23)
    im=render_map(nc,cl,sm,True)
    intro_english_logo(im)
    nc,sm,im=encode_map(nc,cl,sm,im)
    changed['BG_NCGR.PAK'][23]=nc;changed['BG_NSCR.PAK'][23]=sm
    manifest.append({'archive':'BG_NCGR.PAK + BG_NSCR.PAK','entry':23,'english':'DIGIMON XROS WARS'})
    if preview:
        out=ROOT/'build/graphics';out.mkdir(parents=True,exist_ok=True)
        for start in range(0,len(previews),36):contact(previews[start:start+36],out/f'english_{start:03d}.png',columns=4,cell=(256,120))
        command_compare=[]
        for k,text in action_labels.items():
            command_compare.append((f'JP {k}',render_cell(paks['SPR_NCGR.PAK'].file(1971),paks['SPR_NCLR.PAK'].file(1971),paks['SPR_NCER.PAK'].file(1971),k)))
            command_compare.append((f'EN {k}',independent[1971][k]))
        contact(command_compare,ROOT/'build/qa/battle_action_badges_batch121.png',columns=4,cell=(160,96))
        back_compare=[]
        for k in (10,11):
            back_compare.append((f'JP {k}',render_cell(paks['SPR_NCGR.PAK'].file(1987),paks['SPR_NCLR.PAK'].file(1987),paks['SPR_NCER.PAK'].file(1987),k)))
            back_compare.append((f'EN {k}',independent[1987][k]))
        contact(back_compare,ROOT/'build/qa/battle_back_badge_batch121.png',columns=2,cell=(240,96))
        for i,lines in CAPTIONS.items():render_map(changed['BG_NCGR.PAK'][i],paks['BG_NCLR.PAK'].file(31),changed['BG_NSCR.PAK'][i],True).save(out/f'intro_{i}.png')
        (ROOT/'translations/graphics_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {name:paks[name].rebuild(entries,compress=True) for name,entries in changed.items()},manifest


if __name__=='__main__':
    replacements,manifest=localize(Rom(rom_paths()['blue']),True)
    print(len(manifest),'graphic states translated',[(k,len(v)) for k,v in replacements.items()])
