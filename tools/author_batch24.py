"""Author reviewed battle, quest, DigiFarm, location, and name data for batch 24."""
import csv
import json
import textwrap
from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

SRC = 'Original Japanese ROM (local primary source)'
DAWN = 'https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt'
CARDS = {
    'Sakuyamon': 'https://world.digimoncard.com/cards/?card_no=BT19-040&search=true',
    'BanchoLeomon': 'https://world.digimoncard.com/cards/?card_no=BT20-036&search=true',
    'Valkyrimon': 'https://world.digimoncard.com/cards/?category=522002&search=true',
    'DaiPenmon': 'https://world.digimoncard.com/cards/?category=522007&search=true',
    'Calumon': 'https://world.digimoncard.com/cards/?free=EX2-045&search=true',
    'Justimon': 'https://world.digimoncard.com/cards/?free=BT10-067&search=true',
    'Apocalymon': 'https://world.digimoncard.com/cards/?card_no=BT15-102&search=true',
    'Chikurimon': 'https://world.digimoncard.com/rule/?card_no=ST13-08',
}

MOVES = {
    1847: 'Nano Crash',
    1848: 'Plug Bomb',
    1849: 'Neck Hanging',
    1851: 'Twin Sickles',
    1853: 'Pao-Tzu',
    1855: 'Hell Dive',
    1857: 'Knock Buster',
    1859: 'Jet Arrow',
    1861: 'Big Bang Blow',
    1863: 'Lion Dance',
    1865: 'Dirty Saucer',
    1867: 'Guillotine Chainsaw',
    1869: 'Varm Blaze',
    1871: 'Pao-Chen',
    1878: 'Knuckle Fire',
    1879: 'Fire Rocket',
    1880: 'Gunshot',
    1881: 'Vajra',
    1882: 'Inferno Gate',
    1884: 'Cold Flame',
    1885: 'Ice Phantom',
    1886: 'Blackout',
    1887: 'Poison Pierce',
    1888: 'Nile Jewelry',
    1889: 'Rosetta Stone',
    1890: 'Curse of the Queen',
    1891: 'Mega Punch',
    1893: 'Mobius Bite',
    1894: 'Super Sonic Voice',
    1895: 'Grenade Storm',
    1897: 'Black Requiem',
    1898: 'Dead Scream',
    1899: 'Grand Charge',
    1901: 'Queen Stamp',
    1902: 'Grand Cricket',
    1903: 'Heart Breaker',
    1904: 'King Dash',
    1905: 'King Stick',
    1906: 'Checkmate',
    1907: 'Strawberry Death',
    1909: 'Chaos Crusher',
    1910: 'Hyper Infinity Cannon',
}
MATCHED_DAWN = {1879, 1898, 1903, 1906}

BATTLE = {
    140: 'Use the lower screen to give your Digimon commands.',
    141: 'Give orders with the Command Ring. Press left or right on the D-pad to rotate it, then press A to choose a command.',
    143: 'Choose a specific move with Command. Some moves hit multiple targets or deal extra damage. Attacking with an element an enemy is weak to deals more damage.',
    144: 'DigiXross combines Digimon in a special attack. To use it, learn a DigiXross move and keep all required Digimon in your party. A Digimon with Paralysis, Sleep, Confusion, or Blindness cannot join a DigiXross attack.',
    145: "Choose Items to use a consumable. Items can restore HP or MP, cure Health Down effects such as Paralysis, Sleep, Confusion, or Blindness, and revive a KO'd Digimon.",
    146: "Choose Tactics for automatic battle orders. Full Power picks the strongest move and a target each Digimon can defeat. Conserve MP chooses moves with low MP costs. Guard focuses on defense. Escape tries to flee. If even one Digimon gets away, the party escapes.",
    147: 'Formation swaps the selected Digimon with another party member.',
    148: 'Press B to redo your commands.',
    149: 'If your commands are ready, press X to start the battle.',
    153: 'Yes, I need help.',
    154: 'No, thanks.',
    167: 'Formation helps you win battles. The Digimon at the front are the Vanguard. They fight enemies and protect the Rearguard from attacks. Only the Vanguard can use DigiXross.',
    169: 'Move the cursor with the D-pad. Select a Digimon, then press A to open the Command Ring.',
    170: 'Press Y to set a Tactic for every Vanguard and Rearguard Digimon.',
    171: "In battle, each Digimon's display alternates between its name and its action. Tactics show the selected Tactic. Command and DigiXross show the move. Items show the item.",
    172: 'If you have no more commands to give, press X.',
    173: 'After Command, DigiXross, or Items, your Digimon return to their default Tactic next turn. The icon shows which Tactic: Full is Full Power, Eco is Conserve MP, Esc is Escape, and Grd is Guard. New battles start with Full Power. Choose another Tactic to change your default. Your choice stays that way between battles.',
    175: 'I see... So we should assign roles ahead of time.',
    176: "That's where the General's skill shines!",
    177: 'Do you need an explanation of formations?',
}

FARM = {
    28: 'I did it! I was brave for a little bit, and got a little EXP!',
    29: 'Whoa... This is way too hot! I quit!',
    30: "Oh! Those are fireworks, right? They look fun. I'll try launching one!",
    31: "Wow, they're beautiful! That was a huge success... I think my EXP went way up!",
    32: "Hmm? It won't launch... Did I fail?",
    33: "That's a really big ball. I wish I could get on top and roll around!",
    34: 'Yes! That went pretty well! I think my EXP went up a little!',
    35: "I can't stay on... I quit!",
    36: "Is that a tightrope? I've always wanted to try it!",
    37: 'That was easy! I did pretty well. I think my EXP went up a fair bit!',
    38: "That was scary... I'm never doing that again!",
    39: 'Is this a circus tent? Maybe I can learn something, too!',
    40: "I learned how to use the swing! I'm so happy! I think my EXP went way up!",
    41: 'No way! I could never do that!',
    42: "Is this a mini shower? It looks refreshing! Maybe I'll take a shower!",
    43: "Wow, that is so cold! I feel great! I think my EXP went up a little!",
    44: 'Whoa... This is too cold. I feel awful...',
    45: "Is this... a mini fishing pond? It looks fun, so I'll give it a try!",
    46: "Wow, it is easy to catch fish here! I think my EXP went up a fair bit!",
    47: 'Hmm? No fish are biting... This is no fun!',
}

QUESTS = {
    443: ('Sakuyamon Under Control', CARDS['Sakuyamon'], 'Quest title; Western Digimon spelling checked against the official card list.'),
    444: ('Find the strange-acting Sakuyamon and wake her up.', CARDS['Sakuyamon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    445: ('Wild BanchoLeomon must be in your party.', CARDS['BanchoLeomon'], 'Quest requirement; BanchoLeomon spelling checked against the official card list. Wild is the in-game personality.'),
    447: ('Talk to Valkyrimon in the Front Room.', CARDS['Valkyrimon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    448: ('Find a Bird Digimon in south Papyrus Desert.', SRC, 'Quest objective; region names follow the established map glossary.'),
    449: ('Find a Bird Digimon in west Skull Glacier.', SRC, 'Quest objective; region names follow the established map glossary.'),
    450: ('Find a Bird Digimon in west Crystal Volcano.', SRC, 'Quest objective; region names follow the established map glossary.'),
    451: ('Report to Valkyrimon in the Front Room.', CARDS['Valkyrimon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    452: ('I want a golden bird!', SRC, 'Quest title.'),
    453: ('Find a shining, clever, helpful bird.', SRC, 'Quest objective.'),
    454: ('Selfish DaiPenmon must be on your expedition team.', CARDS['DaiPenmon'], 'Quest requirement; Western Digimon spelling checked against the official card list. Selfish is the in-game personality.'),
    456: ('Talk to Calumon in the Front Room.', CARDS['Calumon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    457: ('Find 2 Calumon in Fort Yard.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    458: ('Find 2 Calumon in east Skull Glacier.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    459: ('Find 2 Calumon in west Kumonos Ruins.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    460: ('Find 3 Calumon in south Lost Space.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    461: ('Find 3 Calumon in Crystal Quarry.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    462: ('Find 2 Calumon in north Digital Space.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    463: ('Report to Calumon in the Front Room.', CARDS['Calumon'], 'Quest objective; official Western spelling checked.'),
    464: ('Hide-and-Seek with Calumon', CARDS['Calumon'], 'Quest title; official Western spelling checked.'),
    465: ('Catch them, catch them, catch them, catch them, and catch them all!', CARDS['Calumon'], 'Playful quest objective repeats the Japanese catch instruction; official Western spelling checked.'),
    467: ('Talk to Justimon in the Front Room.', CARDS['Justimon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    468: ('Find Apocalymon in west Crystal Volcano.', CARDS['Apocalymon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    469: ('Find Apocalymon in Crystal Cave.', CARDS['Apocalymon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    470: ('Defeat Apocalymon in Crystal Quarry.', CARDS['Apocalymon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    471: ('Report to Justimon in the Front Room.', CARDS['Justimon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
    472: ('Stop Apocalymon!', CARDS['Apocalymon'], 'Quest title; Western Digimon spelling checked against the official card list.'),
    473: ('Stop the rampage of Apocalymon.', CARDS['Apocalymon'], 'Quest objective; Western Digimon spelling checked against the official card list.'),
}

TRAITS = {
    27: 'Party-wide: slightly resists enemy Poison.',
    28: 'Party-wide: resists enemy Poison.',
    29: 'More vulnerable to enemy Poison.',
    30: 'Resists Curse.',
    31: 'Strongly resists Curse.',
    32: 'Immune to Curse.',
    33: 'Party-wide: slight resistance to Curse.',
    34: 'Party-wide: resistance to Curse.',
    35: 'Somewhat resists special effects.',
    36: 'Strongly resists special effects.',
    37: 'Immune to special effects.',
    38: 'Party-wide: slight resistance to special effects.',
    39: 'Party-wide: some resistance to special effects.',
    40: 'Slightly better at dodging enemy attacks.',
    41: 'Much better at dodging enemy attacks.',
    42: 'Slightly easier for enemies to hit.',
    43: 'Your attacks are slightly more accurate.',
    44: 'Your attacks are much more accurate.',
    45: 'Your attacks are slightly less accurate.',
    46: 'Slightly more likely to land critical hits.',
    47: 'Much more likely to land critical hits.',
    48: 'Slightly less likely to land critical hits.',
    49: 'Escape Tactic is slightly more likely to succeed.',
}

LOCATIONS = {
    1048: ('Chikurimon', CARDS['Chikurimon'], 'Official English Digimon name checked against the card/rules database.'),
    1049: ('Lost Space N', SRC, 'Compact map label; North is abbreviated to fit the location tab.'),
    1050: ('Lost Space S', SRC, 'Compact map label; South is abbreviated to fit the location tab.'),
    1052: ('Stealth Valley N', SRC, 'Compact map label; uses the established Stealth Valley place name.'),
    1053: ('Stealth Valley S', SRC, 'Compact map label; uses the established Stealth Valley place name.'),
    1054: ('Digital Space N', SRC, 'Compact map label; North is abbreviated to fit the location tab.'),
    1055: ('Digital Space S', SRC, 'Compact map label; South is abbreviated to fit the location tab.'),
    1072: ('Fort Yard', SRC, 'Established map place name.'),
    1077: ('Digital Space E', SRC, 'Compact map label; East is abbreviated to fit the location tab.'),
    1085: ('Darkness Tunnel', SRC, 'Direct map location translation.'),
    1086: ('Tokona Sea', SRC, 'Established map place name.'),
}

ITEM_RESERVES = [
    *[(index, number) for index, number in zip(range(4300, 4312), range(3, 15))],
    *[(index, number) for index, number in zip(range(4355, 4358), range(343, 346))],
    *[(index, number) for index, number in zip(range(4361, 4372), range(349, 360))],
    *[(index, number) for index, number in zip(range(4399, 4402), range(527, 530))],
    (4420, None), (4421, 569), (4422, 570),
]


def wrap(value, width):
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def main():
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    previous_output = ROOT / 'translations/batch24.json'
    if previous_output.exists():
        old_batch = json.loads(previous_output.read_text(encoding='utf-8'))
        for block in old_batch['blocks']:
            for index in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + index:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    previous_review = ROOT / 'translations/review_batch24.json'
    if previous_review.exists():
        for row in json.loads(previous_review.read_text(encoding='utf-8')):
            fallback = {'ids': ';'.join(row['ids']), 'japanese': row['japanese'],
                        'category': row['category']}
            for value in row['ids']:
                by_id.setdefault(value, fallback)
    blocks, review, seen = [], [], set()

    def add(key, english, evidence=SRC, note='', width=None):
        if key not in by_id:
            raise ValueError(f'Not in refreshed queue: {key}')
        row = by_id[key]
        ids = row['ids'].split(';')
        if any(value in prior or value in seen for value in ids):
            raise ValueError(f'duplicate/already translated: {ids}')
        if any(records[value]['source'] != row['japanese'] for value in ids):
            raise ValueError(f'source mismatch: {ids}')
        if width:
            english = wrap(english, width)
        if not note:
            note = 'Provisional working English; an exact Western-game localization was not confirmed.'
        seen.update(ids)
        review.append({'category': row['category'], 'japanese': row['japanese'],
                       'ids': ids, 'english': english,
                       'evidence': evidence, 'review_note': note})
        sources = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': sources,
                           'review_note': note})

    for index, english in MOVES.items():
        if index in MATCHED_DAWN:
            note = 'Reuses the matching English Digimon World: Dawn/Dusk move name for the same Japanese attack.'
            evidence = DAWN
        else:
            note = 'Provisional working English rendering from the Japanese attack name; no exact Western-game match verified.'
            evidence = SRC
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)

    for index, (english, evidence, note) in QUESTS.items():
        add(f'MSG/MESPAK01.PAK:000:{index:05d}', english, evidence, note, width=27)
    for index, english in BATTLE.items():
        add(f'MSG/MESPAK02.PAK:012:{index:05d}', english,
            note='Battle tutorial dialogue; wrapped to the 15-column story renderer and aligned with existing tactic names.',
            width=15)
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:002:{index:05d}', english,
            note='DigiFarm reaction; friendly speaker tone retained.', width=27)
    for index, english in TRAITS.items():
        add(f'MSG/MESPAK04.PAK:001:{index:05d}', english,
            note='Direct gameplay effect description; terminology follows the existing status and tactic labels.', width=27)
    for index, (english, evidence, note) in LOCATIONS.items():
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', english, evidence, note)
    for index, number in ITEM_RESERVES:
        label = 'Unused Slot' if number is None else f'Unused Slot {number:03d}'
        add(f'MSG/MESPAK00.PAK:000:{index:05d}', label,
            note='The Japanese source marks an unassigned reservation in the item-name table; this renders it as an unused data slot rather than inventing an obtainable item.')

    (ROOT / 'translations/batch24.json').write_text(json.dumps({
        'description': 'More battle controls, DigiXross and formation guidance, DigiFarm reactions, quest objectives, status and accuracy traits, battle move names, map locations, the Chikurimon name, and explicit unused-item-slot labels. Also fixes the Train farm sprite caption alignment.',
        'blocks': blocks
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'translations/review_batch24.json').write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(blocks)} text slots from {len(review)} reviewed Japanese groups')


if __name__ == '__main__':
    main()
