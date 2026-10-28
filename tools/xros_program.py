"""Translate fixed-size string literals inside the compressed ARM9 program.

Every instruction and pointer is preserved. Only explicit string byte ranges
and the SDK compressed-end metadata field may differ after decompression.
Compression uses ndspy 4.2.0, installed locally under .tools/python.
"""
import json
import struct
import sys
from xros_text import ROOT

sys.path.insert(0,str(ROOT/'.tools/python'))
from ndspy import codeCompression


STRINGS={
'つくったアイテム':'Crafted Items',
'みつけたアイテム':'Found Items',
'ファーム島リスト':'Farm Island List',
'じゅうじボタンで　こうもくをえらび　Ａボタンをおして　けっていしてください。':'D-pad: Select an option. A: Confirm.',
'タイキ':'Taiki',
'エラー':'Error',
'みとうろく':'Unlisted',
'そんなものは　ないわ！！　ひやかしか？':'No such item! Are you teasing me?',
'しょじきん':'Money',
'うれる　しょうひアイテムが　ありません':'No consumables to sell.',
'うれる　そうびアイテムが　ありません':'No equipment to sell.',
'うれる　ファームグッズが　ありません':'No farm goods to sell.',
'だい%dファイル':'File %d',
'いどうさきリスト':'Destinations',
'まだ　できていません':'Not ready yet.',
'ぐっずなしダミーテキスト':'No goods (dummy)',
'なにも　みつけられませんでした':'Nothing was found.',
'なにも　つくれませんでした':'Nothing was crafted.',
'ライブイベントは　おきませんでした':'No Live Event occurred.',
'えらんでいる　ちけいボードのせいのう':'Selected Terrain Board Stats',
'えらんでいる　ＢＧＭボードのせいのう':'Selected BGM Board Stats',
}


def localize_program(rom,preview=False):
    offset,_,ram,size=struct.unpack_from('<4I',rom.data,0x20)
    original=codeCompression.decompress(rom.data[offset:offset+size])
    data=bytearray(original);manifest=[]
    for jp,en in STRINGS.items():
        source=jp.encode('cp932');english=en.encode('ascii')
        if len(english)>len(source):raise ValueError(f'Program string exceeds slot: {jp}')
        start=0;found=0
        while True:
            pos=original.find(source+b'\0',start)
            if pos<0:break
            start=pos+len(source)+1
            if pos and original[pos-1]!=0:continue
            data[pos:pos+len(source)]=english.ljust(len(source),b'\0')
            found+=1;manifest.append({'id':f'ARM9:{pos:08x}','offset':pos,'size':len(source),'source':jp,'english':en})
        if not found:raise ValueError(f'Program source not found: {jp}')
    settings=original.find(bytes.fromhex('2106c0dedec00621'))-28
    if not 0<=settings<0x4000:raise ValueError('SDK settings outside uncompressed ARM9 prefix')
    compressed=bytearray(codeCompression.compress(data,True))
    struct.pack_into('<I',compressed,settings+20,ram+len(compressed))
    if len(compressed)>size:raise ValueError('Translated ARM9 exceeds its original ROM allocation')
    # Verify every byte of decompressed code outside the literal strings and
    # compressed-end field. No assembly instructions or addresses are changed.
    restored=bytearray(codeCompression.decompress(compressed))
    for row in manifest:
        pos=row['offset'];n=row['size'];restored[pos:pos+n]=original[pos:pos+n]
    restored[settings+20:settings+24]=original[settings+20:settings+24]
    if bytes(restored)!=original:raise ValueError('Unexpected decompressed program change')
    if preview:(ROOT/'translations/program_strings.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return bytes(compressed),manifest
