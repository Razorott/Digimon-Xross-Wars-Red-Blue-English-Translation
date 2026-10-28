"""Fit battle/party display names without changing formal species names.

MESPAK00 has separate display and formal name lists. The DigiDex renderer
black-screens when the display list contains one-byte Latin or fullwidth
punctuation. Two-byte CP932 Latin letters and digits, drawn through compact
native glyph slots, are accepted by that renderer and were verified with all
472 labels. Repointing them to appended glyphs hides saved nicknames in the
party/status renderer.
"""
from __future__ import annotations

import re
DISPLAY_START=179
DISPLAY_END=651
DISPLAY_BUDGET_PX=60
MOVE_BUDGET_PX=104

# Deliberate, recognizable short labels for common species. These are UI
# labels, not claims that the shortened spelling is an official Western name.
CURATED={
    'Formal Name Placeholder':'Placehold.',
    'Armadillomon':'Armadillo',
    'Raptordramon':'RaptorDram.',
    'MachGaogamon':'MachGaoga',
    'Millenniummon':'Millennium',
    'ZeedMillenniummon':'ZeedMillen.',
    'Chronomon: Holy Mode':'Chrono HM',
    'Gallantmon Crimson Mode':'Gallant CM',
    'GranKuwagamon':'GranKuwaga',
    'AncientVolcanomon':'A.Volcano',
    'MailBirdramon':'MailBirdra',
    'DarkTyrannomon':'DarkTyranno',
    'BanchoLeomon':'BanchoLeo',
    'LordKnightmon':'LordKnight',
    'VenomMyotismon':'VenomMyoti',
    'TigerVespamon':'TigerVespa',
    'PlatinumNumemon':'PlatNumemon',
    'DemiDevimon':'DemiDev',
    'MegaKabuterimon (Red)':'M.Kabuteri R',
    'HerculesKabuterimon':'H.Kabuteri',
    'Imperialdramon DM':'Impdrmn DM',
    'Imperialdramon Fighter Mode':'Impdrmn FM',
    'Imperialdramon Paladin Mode':'Impdrmn PM',
    'UlforceVeedramon':'U.Veedramon',
    'MetalGarurumon':'M.Garurumon',
    'MegaSeadramon':'MegaSeadra',
    'MetalSeadramon':'Met.Seadra',
    'KnightChessmon W':'K.Chess W',
    'Cherubimon (Virtue)':'Cherubi V',
    'Cherubimon (Vice)':'Cherubi B',
    'ShineGreymon BM':'ShineGrey BM',
    'MirageGaogamon BM':'M.Gaoga BM',
    'Lucemon Falldown Mode':'Lucemon FDM',
    'ShineGreymon RM':'ShineGrey RM',
    'Dorulu Cannon':'Dorulu C.',
    'Argomon (Ultimate)':'Argomon U',
    'Argomon (Mega)':'Argomon M',
    'Shoutmon X2':'Shout X2',
    'Shoutmon X3':'Shout X3',
    'Shoutmon X4':'Shout X4',
    'Shoutmon X5':'Shout X5',
    'Shoutmon X4B':'Shout X4B',
    'Shoutmon X3GM':'Shout X3GM',
    'Shoutmon X3SD':'Shout X3SD',
    'Shoutmon X4S':'Shout X4S',
    'Shoutmon X5S':'Shout X5S',
    'PawnChessmon WH':'P.Chess WH',
    'SkullKnightmon BR':'S.Knight BR',
}

# The battle HUD's actual opponent/party label is tighter than the table's
# generic 60 px ceiling. Keep the full species name in formal records, while
# shortening this known clipping case in the narrow display table.
FORCE_CURATED={'Armadillomon'}

PREFIXES=(
    ('Ancient','A.'),('Imperial','Imp.'),('Hercules','H.'),
    ('Metal','M.'),('Mega','M.'),('Dark','D.'),('Black','B.'),
    ('Skull','S.'),('Shine','Sh.'),('Mirage','M.'),
    ('Knight','K.'),('Cyber','C.'),('Rook','R.'),
)

def pixels(value,fonts):
    return max(sum(font.advance(char) for char in value) for font in fonts)


def two_byte_display(value):
    """Encode a compact ASCII label as CP932 two-byte Latin, without punctuation."""
    if not value or not value.isascii() or not value.isalnum():
        raise ValueError(f'DigiDex label needs only ASCII letters/digits: {value!r}')
    return ''.join(chr(ord(char)+0xfee0) for char in value)

def compact(value,fonts,budget=DISPLAY_BUDGET_PX):
    if value in CURATED:
        answer=CURATED[value]
        if value in FORCE_CURATED and pixels(answer,fonts)<=budget:return answer
        if pixels(value,fonts)>budget and pixels(answer,fonts)<=budget:return answer
    if pixels(value,fonts)<=budget:return value
    # Keep short transformation suffixes (BM, DM, L...) visible.
    suffix=''
    match=re.search(r' ([A-Z]{1,3}|\((?:Red|Blue|Vice|Virtue|Ultimate|Mega)\))$',value)
    if match:
        suffix=(match.group(0).replace('(Red)','R').replace('(Blue)','B')
                .replace('(Vice)','B').replace('(Virtue)','V')
                .replace('(Ultimate)','U').replace('(Mega)','M'))
        base=value[:match.start()]
    else:base=value
    candidates=[]
    for prefix,short in PREFIXES:
        if base.startswith(prefix) and len(base)>len(prefix) and base[len(prefix)].isupper():
            candidates.append(short+base[len(prefix):]+suffix)
    for name in candidates:
        if pixels(name,fonts)<=budget:return name
    # Last resort: a visible period marks truncation; the formal list still
    # carries the complete official name and can be shown in wider screens.
    stem=candidates[0] if candidates else base
    if suffix and stem.endswith(suffix):stem=stem[:-len(suffix)]
    while stem and pixels(stem+'.'+suffix,fonts)>budget:
        stem=stem[:-1]
    if not stem:raise ValueError(f'Cannot fit display name: {value}')
    return stem+'.'+suffix

def apply_display_names(translations,fonts,budget=DISPLAY_BUDGET_PX):
    manifest=[]
    for record in translations.values():
        if record['archive']!='MSG/MESPAK00.PAK' or record['entry']!=0:
            continue
        if not DISPLAY_START<=record['index']<DISPLAY_END:
            continue
        full=record['english']
        if '\n' in full or '^' in full:continue
        short=compact(full,fonts,budget)
        # Fullwidth period/space codepoints black-screened the DigiDex in
        # one-name probes. Use alphanumeric abbreviations; the formal list
        # retains the complete Western spelling.
        short=''.join(char for char in short if char.isalnum())
        encoded=two_byte_display(short)
        width=pixels(encoded,fonts)
        if width>budget:
            raise ValueError(f'Encoded DigiDex label exceeds HUD: {record["id"]} {width}')
        record['english']=short
        record['display_english']=short
        record['runtime_display_english']=encoded
        record['formal_english']=full
        if short!=full:
            record['review_note']=(record.get('review_note','')+' '
                +f'Display-only abbreviation; formal Western name: {full}.').strip()
        manifest.append({'id':record['id'],'japanese':record['source'],
                         'display':short,'formal':full,'display_width_px':width,
                         'budget_px':budget,'abbreviated':short!=full,
                         'applied':True,'runtime_preserved':False,
                         'runtime_encoding':'CP932 two-byte Latin; compact native glyph'})
    return manifest


def apply_move_names(translations,fonts,budget=MOVE_BUDGET_PX):
    """Fit attack labels with normal ASCII and retain full names in the review data."""
    manifest=[]
    for record in translations.values():
        if record['archive']!='MSG/MESPAK00.PAK' or record['entry']!=0:
            continue
        if not 1228<=record['index']<=3750:
            continue
        value=record['english']
        if '\n' in value or '^' in value:
            continue
        shown=fit_move(value,fonts,budget)
        width=pixels(shown,fonts)
        record['display_english']=shown
        manifest.append({'id':record['id'],'english':value,'display':shown,
                         'display_width_px':width,'budget_px':budget,
                         'abbreviated':shown!=value})
    return manifest


def fit_move(value,fonts,budget=MOVE_BUDGET_PX):
    """Shorten an overlong move label at word endings without losing its source name."""
    if pixels(value,fonts)<=budget:return value
    words=value.split(' ')
    # Preserve every word when possible, shortening the final technique word
    # first (e.g. "Northern Cross Bomber" -> "Northern Cross B.").
    for index in range(len(words)-1,-1,-1):
        original=words[index]
        for keep in range(len(original)-1,0,-1):
            candidate_words=words.copy()
            candidate_words[index]=original[:keep]+'.'
            candidate=' '.join(candidate_words)
            if pixels(candidate,fonts)<=budget:return candidate
    # If a full set of words still cannot fit, retain the phrase's beginning.
    for count in range(len(words)-1,0,-1):
        candidate=' '.join(words[:count])+'...'
        if pixels(candidate,fonts)<=budget:return candidate
    # Last resort for a single unusually long word: clip visibly with an ellipsis.
    for keep in range(len(value)-1,0,-1):
        candidate=value[:keep]+'...'
        if pixels(candidate,fonts)<=budget:return candidate
    raise ValueError(f'Cannot fit battle move: {value}')
