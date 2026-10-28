"""Author the next reviewed story, mission, battle, farm, and item batch."""
from __future__ import annotations

import csv
import html
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'
TECHNIQUES_ID = 'B32_WIKIMON_XROS_TECHNIQUES'
DAWN_DUSK_ID = 'B32_DAWN_DUSK'
CARDS_ID = 'B32_BANDAI_CARDS'

STORY = {
    103: "Huh? ...Who are you?!",
    110: "Well, yeah. No point asking. They really do seem to be in trouble. Let's hurry and help!",
    120: "Stop right there!",
    121: "Back away! Don't come any closer!",
    122: "...Huh? Kiriha?!",
    123: "Wait, Kiriha! What's going on?",
    124: "Sorry, but I'm not handing this Digimon over. It's the key I need to reach new heights.",
    125: "...What's going on?",
    126: "Something's wrong. What happened to Kiriha? I thought becoming Taiki's rival had softened him up... but he's back to being cold and scary!",
    127: "I don't care what you think of me. Stay here and watch.",
    128: "Now, come quietly. I don't want to get rough.",
    135: "Tch... Of all the times... We'll have to pull back for now...",
    143: "What's wrong with you? We're not safe at all!",
    144: "Akari's here, too. Those shady guys calling themselves ROG captured all of us.",
    145: "So... my dream wasn't that far off?",
    146: "Where are Shoutmon and the others?",
    147: "They must've taken them somewhere while we were unconscious. Ballistamon and Dorulumon are gone, and so is Cutemon.",
    148: "They took almost everyone. What are we going to do now?",
    150: "If anything, we're the ones who need rescuing right now.",
    151: "Taiki, you really want to help everyone, don't you? I guess that's one of your best qualities...",
    152: "The voice I heard on the way here said something like that, too. It said I had to save everyone. I guess it struck a chord, and I couldn't just walk away...",
    153: "Oh! That Digimon from earlier... They caught you here?",
    154: "Aaaah! You're the Digimon from before!",
    155: "D-don't shout! The ROG guys will hear you!",
    156: "Hey, wait! More importantly, why are you here?",
    157: "I came to save my friend Patamon... but he doesn't seem to be here. I'm Spadamon. Who are you?",
    158: "I'm Taiki Kudo. This is Akari and Zenjiro.",
    159: "We're the Starmon and...",
    160: "...the Pickmons! Nice to meet you!",
    163: "Those idiots... Why did they install such a complicated door? It won't budge no matter what I try! It looks flimsy, but it's protected by a high-security block. I'm the only one who can let the others in or out, after all...",
    165: "I doubt you'll escape, but don't try anything funny! Resist again, and you and your friends will pay for it!",
    167: "Hey, Shoutmon!",
    168: "Wake up, brother!",
    170: "...Hey, Taiki! We've got trouble! They took Ballistamon somewhere! They said they'd put the Digimon through some kind of machine... If we want our friends back, we have to hand over this 'Sparda-something'!",
    171: "...Spadamon. That's me.",
    172: "Oh, hey! You're that Digimon from before... Didn't you run away?",
    173: "I had no choice! I... I'm weak... ROG suddenly attacked Sky Fort, and I was supposed to escape with everyone else... But Patamon stayed behind to defend it. He's my best friend, and... he's way too brave. I told him to run, but he kept fighting to the end... If this goes on, ROG will capture Patamon, too! You're strong, right?! Please, help me!",
    174: "Of course, Spadamon! We're Xros Heart! Our team is full of Digimon with fiery hearts! Well... we're a few members short right now... but we can't leave you in trouble!",
    175: "That's Taiki for you! That's what I wanted to hear!",
    176: "Now, how do we get through this door? Spadamon, can you do something?",
    177: "Easy! This used to belong to us before ROG took it.",
    178: "All right, let's go! We'll beat those guys so badly they'll never forget it!",
    179: "Shoutmon and Spadamon joined the team!",
    180: "They say an incredible power is hidden in this Zone! Where could it be? What is it?",
    181: "I... I don't know! How could I know? If something like that existed, you'd have driven us out already!",
}

MERMAIMON_QUEST = {
    27: "Remember Mermaimon, the boss of the Western Pirates? She got captured by someone really dangerous! This looks bad... no, really bad! We thought about going to save her ourselves, but there's no way we can win. You're our only hope! Please save our precious friend!",
    28: "Please save Mermaimon, who's being held at Tokona Coast! Hangyomon is trying to stop them from taking her away, but the power difference is too great. He probably can't hold out much longer!",
    29: "You rescued Mermaimon? That's a relief! But... um... didn't she give you some treasure? It's pirate custom to give something to the one who saves your life. Sorry to send you back and forth, but come see me again after she gives you the treasure.",
    30: "Looks like Mermaimon gave you some treasure. We Pirates want to thank you again. Thanks so much! You really saved us! In return for that treasure, I'll give you a Melody!",
    31: "Please take a reward from us, too!",
    32: "For some reason, everyone hates and makes fun of us... But you're the only one who's always treated us fairly and listened to us. Thanks, Taiki. You're a good guy.",
    33: "Mermaimon was dragged into the sea! P-please, save her!",
    34: "She was dragged in from here, so she should be in Tokona Sea by now. Please hurry and save Mermaimon!",
    35: "Find four treasures in Tokona Sea and Tokona Coast. I'll give you one of them as a thank-you! But I won't be here forever, so find them soon, okay? My little surprise will disappear if you wait too long!▼",
    36: "Oh, you chose that one? Hehe... That's so like you. Now show it to my friend MarineDevimon!▼",
    37: "Take the Fire Crown?",
    40: "Take the Snow Crown?",
    43: "Take the Saint Crown?",
    46: "Take the Dark Crown?",
    49: "Gyo-gyaaah?! Remember Mermaimon, boss of the Western Pirates? She was captured by someone really dangerous! This looks bad... no, really bad! We remaining Pirates wanted to rescue her, but there's no way we can win. You're our only hope! Please save our precious friend!",
    50: "Please save Mermaimon at Tokona Coast! MarineDevimon is trying to stop them from taking her away, but the power difference is too great. He probably can't hold out much longer!",
    51: "Gyo-gyaaah?! You rescued Mermaimon? That's a relief! But... um... didn't she give you some treasure? It's pirate custom to give something to the one who saves your life. Sorry to send you back and forth, but come see me again after she gives you the treasure.",
    52: "Gyo-gyaaah! Did Mermaimon give you some treasure? Good! We Pirates want to thank you. Thanks so much! You really saved us! In return for that treasure, we'll give you a Melody!",
    53: "Then please take a reward from us, too!",
}

FARM = {
    15: "Whoa! A treehouse! This looks fun! It's my house now! I just decided!",
    16: "Whoa! Being surrounded by nature isn't bad! I got a lot of EXP, too!",
    17: "No way! It looks cool, but it's so inconvenient!",
    18: "What's this?! A computer! I want to try it out!",
    19: "Using a computer is so much fun! I discovered a whole new world, and my EXP went up!",
    20: "Whoa, I know this! It's a solar panel! I'll go take a closer look!",
    21: "Whoa! It's sending electricity! My EXP is crackling upward!",
    22: "Whoa! That tingles! Yikes, I can see my bones!",
    23: "Whoa! I found a pinball machine! That looks awesome! I'm gonna try it!",
    24: "Look at that high score! I'm a genius! I got a ton of EXP, too!",
    25: "Why can't I win?! Is this thing broken?!",
    26: "What's this? A birdhouse! What's inside? I'll go in and see!",
    27: "Whoa! I feel like a little bird! I got a little more EXP, too!",
    28: "There's nothing inside! It's cramped, smelly, and boring!",
    29: "I get it! This is a running high jump! Easy! Watch me fly!",
    30: "Whoa! That was easy! I jumped, and my EXP jumped way up, too!",
    31: "What was that?! Only the bar flew!",
    32: "Whoa! A diving board! This'll be easy! I'll soar like a bird!",
    33: "I flew! I really flew! Just like a bird! My EXP floated right up, too!",
    34: "No way! Sure, I'm a bird, but I'm a total chicken!",
    35: "What's this?! A record player?! It looks ancient! Does it still work?!",
    36: "I like this sound! I love it! I got a little more EXP, too!",
    37: "It won't work at all! It's just junk!",
    38: "What's this? A holy... bell...? Now that I know its name, I still don't know what it does!",
    39: "Whoa! What's this warm, fuzzy feeling?! My EXP went up, too! Is this what it feels like to be holy?!",
}

ITEM_EFFECTS = {
    41: "Battle rewards grant a fair amount more EXP.",
    42: "Battle rewards grant much more EXP.",
    43: "Battle rewards grant vastly more EXP.",
    44: "Exploration missions are more likely to succeed.",
    45: "Exploration missions are much more likely to succeed.",
    46: "Exploration missions are more likely to fail.",
    47: "Jobs are more likely to succeed.",
    48: "Jobs are much more likely to succeed.",
    49: "Jobs are more likely to fail.",
}

# These IDs are two appearances of the same attack names in each ROM.
MOVES = {
    2675: ("RB Symphony", "Working romanization; the game's Japanese attack list preserves the RB acronym."),
    2676: ("SPN Claymore", "Working romanization; the game's Japanese attack list preserves the SPN acronym."),
    2677: ("FRZ Blizzard", "Working romanization; the game's Japanese attack list preserves the FRZ acronym."),
    2678: ("Omega Burst", "The game's technique guide confirms the matching attack and its burst effect; this English rendering follows the Japanese name."),
    2683: ("G Maelstrom", "Working romanization; the game's Japanese attack list preserves the G prefix."),
    2684: ("Gaia Force D", "The base Gaia Force name is established in Bandai English material; D is retained from this game-specific variant."),
    2687: ("B Death Cloud", "Working romanization; the game's Japanese attack list preserves the B prefix."),
    2688: ("Laplace's Demon", "The game guide describes this as calculating enemy coordinates and sending them to another world; the name is the established term Laplace's Demon."),
    2690: ("Giga Stick L", "Working romanization; the game's Japanese attack list preserves the L suffix."),
    2700: ("Invincible S", "Working romanization; the game's Japanese attack list preserves the S suffix."),
    2706: ("Aurora UR", "Working romanization; the game's Japanese attack list preserves the UR suffix."),
    2712: ("VN Infuse", "Matches the English move name used in Digimon World: Dawn/Dusk for the same Japanese attack."),
    2716: ("K Phoenix", "Working romanization; the game's Japanese attack list preserves the K prefix."),
    2718: ("GA Missile", "Working romanization; the game's Japanese attack list preserves the GA acronym."),
    2722: ("DM Scissor", "Working romanization; the game's Japanese attack list preserves the DM acronym."),
}

def wrap(value: str, width: int) -> str:
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def register_move_terms() -> None:
    path = ROOT / 'translations/glossary.json'
    glossary = json.loads(path.read_text(encoding='utf-8'))
    terms = glossary['terms']
    records = collect_messages(Rom(rom_paths()['blue']))

    def put(japanese: str, english: str, sources: list[str], evidence: str) -> None:
        old = next((term for term in terms if term['japanese'] == japanese), None)
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting glossary term: {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + sources))
            old['evidence'] = evidence
        else:
            terms.append({'japanese': japanese, 'english': english,
                          'category': 'Move name', 'sources': sources,
                          'evidence': evidence})

    for index, (english, note) in MOVES.items():
        key = f'MSG/MESPAK00.PAK:000:{index:05d}'
        record = records[key]
        japanese = record['source']
        source_ids = [TECHNIQUES_ID]
        if index == 2712:
            source_ids.append(DAWN_DUSK_ID)
        if index == 2684:
            source_ids.append(CARDS_ID)
        put(japanese, english, source_ids, note)
    glossary['checked'] = '2026-10-25'
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    old_batch = ROOT / 'translations/batch33.json'
    if old_batch.exists():
        old = json.loads(old_batch.read_text(encoding='utf-8'))
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    blocks, reviews, seen = [], [], set()
    glossary = json.loads((ROOT / 'translations/glossary.json').read_text(encoding='utf-8'))
    sources = glossary['sources']

    def add(key: str, english: str, evidence: str = LOCAL, note: str = '',
            width: int | None = None) -> None:
        if key in prior:
            return
        row = by_id.get(key)
        if row is None:
            raise ValueError(f'Not found in untranslated queue: {key}')
        ids = row['ids'].split(';')
        if all(value in seen for value in ids):
            return
        if any((value in prior) or value in seen for value in ids):
            raise ValueError(f'duplicate/already translated group: {ids}')
        japanese = row['japanese']
        if any(records[value]['source'] != japanese for value in ids):
            raise ValueError(f'source mismatch: {ids}')
        if width:
            english = wrap(english, width)
        seen.update(ids)
        reviews.append({'category': row['category'], 'japanese': japanese,
                        'ids': ids, 'english': english, 'evidence': evidence,
                        'review_note': note})
        source_urls = [evidence] if evidence.startswith('https://') else []
        for value in ids:
            item = records[value]
            blocks.append({'archive': item['archive'], 'entry': item['entry'],
                           'start': item['index'], 'category': row['category'],
                           'english': [english], 'sources': source_urls,
                           'review_note': note})

    story_note = ('Main story dialogue around the Sky Fort rescue. Character names follow the project glossary; Sky Fort, ROG, and Xros Heart follow established project wording. Text is wrapped to the 15-cell story line limit.')
    for index, english in STORY.items():
        add(f'MSG/MESPAK02.PAK:002:{index:05d}', english, LOCAL,
            story_note, width=15)

    quest_note = ('Optional Western Pirates rescue mission. Mermaimon, Hangyomon, and MarineDevimon follow the reviewed Digimon-name glossary; Tokona Coast/Sea and Melody match existing game terminology. Wrapped to the story text cell limit.')
    for index, english in MERMAIMON_QUEST.items():
        add(f'MSG/MESPAK02.PAK:022:{index:05d}', english, LOCAL,
            quest_note, width=15)

    farm_note = ('DigiFarm activity report. Shoutmon’s emphatic voice and EXP terminology are retained; lines are wrapped for the farm report box.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:004:{index:05d}', english, LOCAL,
            farm_note, width=26)

    item_note = ('Equipment effect description translated from the Japanese item data. Battle EXP, exploration mission success, and job success rates follow the visible gameplay effect.')
    for index, english in ITEM_EFFECTS.items():
        add(f'MSG/MESPAK04.PAK:002:{index:05d}', english, LOCAL,
            item_note, width=25)

    move_sources = {
        TECHNIQUES_ID: sources[TECHNIQUES_ID]['url'],
        DAWN_DUSK_ID: sources[DAWN_DUSK_ID]['url'],
        CARDS_ID: sources[CARDS_ID]['url'],
    }
    for index, (english, note) in MOVES.items():
        key = f'MSG/MESPAK00.PAK:000:{index:05d}'
        evidence_id = DAWN_DUSK_ID if index == 2712 else TECHNIQUES_ID
        if index == 2684:
            # The card source confirms the established base attack; the game
            # guide confirms this title's D variant.
            evidence = move_sources[TECHNIQUES_ID]
        else:
            evidence = move_sources[evidence_id]
        move_note = note + ' Exact Japanese attack spelling and in-game effect checked against the Super Xros Wars technique guide.'
        if index == 2712:
            move_note = note + ' Exact Japanese spelling is the same attack documented in the Dawn/Dusk move list.'
        if index == 2684:
            move_note = note + ' The Japanese variant label is listed in the Super Xros Wars guide; Bandai English card material confirms the Gaia Force base name.'
        add(key, english, evidence, move_note)

    description = ('Sky Fort story and rescue scenes; Western Pirates/Mermaimon side-mission dialogue; 25 DigiFarm reports; equipment effect descriptions; and 15 battle move names. The status-screen carousel lettering was restyled with a bold face, dark outline, and offset shadow; existing localized graphic states remain included.')
    out = ROOT / 'translations/batch33.json'
    review_json = ROOT / 'translations/review_batch33.json'
    review_md = ROOT / 'translations/review_batch33.md'
    out.write_text(json.dumps({'description': description, 'blocks': blocks},
                              ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    lines = [
        '# Batch 33 translation review', '',
        'Japanese source strings, English renderings, stable IDs, and terminology evidence.', '',
        '| IDs | Japanese | English | Evidence and review note |',
        '| --- | --- | --- | --- |',
    ]
    for item in reviews:
        ids = '<br>'.join(f'`{html.escape(key)}`' for key in item['ids'])
        jp = html.escape(item['japanese'].replace('<0A>', '\n')).replace('\n', '<br>')
        en = html.escape(item['english']).replace('\n', '<br>')
        evidence = html.escape(item['evidence'])
        note = html.escape(item['review_note'])
        lines.append(f'| {ids} | {jp} | {en} | {evidence}<br>{note} |')
    review_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'groups={len(reviews)} slots={len(blocks)}')
    print(out)


if __name__ == '__main__':
    register_move_terms()
    main()
