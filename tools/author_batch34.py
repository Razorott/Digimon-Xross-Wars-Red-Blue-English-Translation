"""Author a reviewed Xros Wars story, quiz, farm, and battle-status batch."""
from __future__ import annotations

import csv
import html
import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records

LOCAL = 'Original Japanese ROM (local primary source)'

STORY = {
    76: "Leave saving your adventure to me! Press A in front of the Save Terminal. If a teammate's HP or MP is low, press A in front of a bed. Easy, right?",
    77: "By the way, have you been reading the DigiReports? You'd miss out if you didn't! The raffle at the end can win you a huge pile of Bits!",
    78: "Before Sky Fort was built, Earth Fort was the strongest fortress in this Zone. It's protected, but it should still have a radar that scans the Zone. Maybe Zeed\nMillenniummon is using it to scan the Zone...",
    79: "Taiki! Stop ROG before Zeed\nMillenniummon finds anything! Please!",
    80: "Sky Fort's famous Penmon Item Shop! The Sky Shop, for short. Sounds cool, right?!",
    81: "I tried to think of something we could do to help... but honestly, there isn't much. You're going to Crystal Volcano to fight ROG, right? We'd only get in your way...",
    82: "We can't do much to help, but we'll always cheer you on with all we've got! Don't forget that, okay?",
    83: "So you're facing ROG at Crystal Volcano... I'd like to go with you, but we can't leave this place empty. We'll stay and strengthen Sky Fort's defenses.",
    84: "We'll handle defense. You take care of the offense. ...I'm counting on you, Taiki!",
    85: "You're about to fight someone super strong? But you guys will be fine! I just know it!",
    86: "Whenever I thought someone would be okay, they almost always were! So you guys will definitely be fine!",
    87: "Welcome, Taiki! This is the Quest Monitor. ...You know that, of course. Thanks for stopping by, and see you again!▼",
    88: "Taiki, the fight with ROG is reaching its climax! If you need a change of pace, check the Quest Monitor!▼",
    90: "You're heading out to defeat ROG's boss, right? We'll get our turn to fight, too, won't we?! ...Right?!",
    91: "All right! Let's do this! We'll blast ROG's boss Digimon into next week!♪",
    94: "Hey, Taiki! How's it going? If you push yourself too hard, you'll run out of steam when it matters. Learn when to take it easy, too!",
    95: "Even if you still have HP, you can't fight without MP. Desperate Attack lets you attack anyway, but if your HP is low, you'll go down!",
    99: "You solved the problems we were facing, one by one. We can't thank you enough.",
    100: "We haven't been able to repay you properly, but every Digimon in the Zone, me included, is deeply grateful to you.",
    104: "You're really going to fight ROG's boss, Zeed\nMillenniummon?! I can't believe it... Actually, with you guys, maybe I can! Good luck, Taiki!",
    105: "It's not my place to tell you what to do, but don't rush. Take it one step at a time and be careful.",
    109: "I heard you're going to face ROG's big boss! Taiki, you're amazing! So cool!♪",
    110: "ROG's big boss must be really strong... Stay alert and do your best so you don't get beaten!",
    114: "We're grateful to you, and we believe in you! Everyone's cheering you on with all their might!",
    115: "Give it your all, everyone! Give it your all... Wait, what does 'give it your all' even mean?",
    116: "We'd all given up, thinking this fight would never end. But after meeting you, Taiki, everything changed. We have hope now. Thank you!",
    117: "Thanks to you, we're united again. We're truly grateful. We hope you'll keep looking out for us!",
    121: "Crystal Volcano?! Earth Fort?! ...Earth Fort brings back memories. The warriors who protected this Zone used to gather there.",
    122: "Hey, savior of the Elestou Zone! You're doing great, right? You'd better be!",
    123: "I've heard all about you! The Digimon are thrilled to have such reliable friends!♪",
    124: "I know how hard you're working for this Zone. I keep praying you won't push yourself too hard and get hurt!",
    128: "Hey! Still going strong? We'll keep working hard so we don't fall behind you!",
    129: "The future of this Zone depends on you. Sorry to leave it all to you, but give it everything you've got!",
    134: "Taiki! You came to save us! Thank you! But ROG didn't even stop to fight us... They rushed straight toward the windmill in Sky Garden!",
    136: "Hey, Taiki... When we've taken this Zone back for good, tell me everything that happened here, okay? So come back safe!",
    137: "I have nothing more to say to you... Please protect the Elestou Zone!",
    139: "Hi, Taiki! I'm glad you look well. I knew you'd be safe, but we were still so worried about you! Though maybe we should've worried more about ourselves...",
    147: "Shadow Guard took the tower from us this time... We had to run away, and I'm ashamed of that. Thank you for driving them off!",
    148: "Someone sent a message addressed to you? Who could it be? Well, you can handle yourself, savior of this Zone!",
    149: "Everyone at Sky Fort seems to be safe. That's a relief! You really are the savior of this Zone, Taiki!",
}

PIEDMON_QUIZ = {
    119: "I have a tough challenge for you. First, find Piedmon in South 2 of Digital Space. Then answer his quiz questions in a row. You can do it! I'd hate it... I mean, good luck. Come back when you're done.",
    120: "Find Piedmon and answer his quiz. It sounds easy, but it's a real ordeal. Good luck!",
    121: "Thanks! Here's your reward. It may be just a quiz, but Piedmon won't stop until he's satisfied. Everyone who passes by is terrified... We could sacrifice someone to take our place... No, never mind. Great work, savior!♪",
    123: "You found me! Ha ha! It's time for Piedmon's Special Digimon Quiz 2, Question 1! What's Seadramon's special move?!",
    125: "Nice Arrow",
    127: "Ding-ding-ding! The answer is Ice Arrow! It's an arrow made of ice. A little obvious, huh? Ha ha!♪",
    130: "Your next stop is South 7 of Digital Space! Let's go!♪",
    131: "I'll be waiting for you in South 7 of Digital Space!♪",
    132: "All right, you found me! Ha ha! It's Question 2 of Piedmon's Special Digimon Quiz 2! What's Leomon's special move?!",
    134: "Deadly Fragments",
    135: "Ding-ding-ding! The answer is BeastKing Fist! It's the fist of the king of beasts! Ha ha!♪",
    138: "Your next stage is North 4 of Digital Space! Let's go!♪",
    139: "I'll be waiting for you in North 4 of Digital Space!♪",
    140: "Oh, you found me! Ha ha! It's Question 3 of Piedmon's Special Digimon Quiz 2! What's ToyAgumon's special move?!",
    142: "Toy Fire",
    143: "Ding-ding-ding! The answer is Toy Flame! A flame that feels like a toy... Really?! Ha ha!♪",
    146: "Your next stage is North 3 of Digital Space! Let's go!♪",
    147: "I'll be waiting for you in North 3 of Digital Space!♪",
    148: "Hey, you found me! Ha ha! It's Question 4 of Piedmon's Special Digimon Quiz 2! What's Greymon's special move?!",
    150: "Giga Flame",
    151: "Ding-ding-ding! The answer is Mega Flame! Was that one trickier than you expected? Ha ha!♪",
    154: "Your next stop is North 8 of Digital Space! Let's go!♪",
    155: "I'll be waiting for you in North 8 of Digital Space!♪",
    156: "Hey, you found me! Ha ha! It's Question 5 of Piedmon's Special Digimon Quiz 2! What's Lillymon's special move?!",
    158: "Lily Smile",
    159: "Ding-ding-ding! The answer is Flower Cannon! It looks cute, but it really hurts! Ha ha!♪",
    162: "That's the end of the quiz! Great work! Go claim your reward from Paildramon!♪",
    163: "Aww, already miss the quiz? It's over! Go claim your reward from Paildramon!♪",
}

FARM = {
    40: "Whoa! What's this warm, fuzzy feeling?! I gained EXP, too! Is this what being holy feels like?!",
    41: "I don't get what's so holy about it... Is it the sound? If it doesn't move, how would I know what it sounds like?",
    42: "Whoa! I found Stonehenge! I wonder what happens if I walk past it!",
    43: "Whoa, what is this?! Is this holy power?! I don't know how, but I gained EXP!",
    44: "Nothing happened at all... That's almost impressive.",
    45: "Whoa, this pot is bubbling! I don't know what it is, but can I eat it?!",
    46: "Whoa! It's Dark Medicine! I gained a little EXP from it!",
    47: "Ugh, it stinks! It's gross, bitter, sour... and rotten!",
    48: "What is this?! It's creepy... Is it a cursed box? What's inside?!",
    49: "Whoa! Is this the power of darkness?! I gained a fair bit of EXP!",
    50: "Whoa, the lid won't open! Is it cursed, too?!",
    51: "...Is this a Dark Tower?! I'll get closer and check it out!",
    52: "Whoa! I can feel powerful darkness! I think I gained a lot of EXP!",
    53: "Whoa! What a letdown! All it did was put me in a slightly dark mood!",
    54: "Huh? What's that amazing smell? It smells like something I really love!",
    55: "That's definitely Taiki's smell! I want to play together when he visits! I think my Friendship went up, too!",
    56: "Whoa! Life is easy and happy today! It's all thanks to Taiki! I should thank him!",
    57: "...Taiki, we're happy because of you! I'm so grateful! I hope you heard me! My Friendship went way up!",
    59: "Whoa! 100 Bits! I'll send them to Taiki right away!",
    61: "Whoa, I did it! 500 Bits! I'll send them to Taiki right away!",
    63: "Whoa, amazing! 1,000 Bits! I'll send them to Taiki right away!",
    64: "Whoa! I found wild berries out here!",
    65: "They're sweet and tasty! I gained EXP!",
    66: "What is this?! It's too bitter and sour to eat!",
    67: "Whoa! I want to climb a tree!",
    68: "Whoa! I climbed way up high, and my EXP shot up, too!",
    69: "No good! I slipped and couldn't climb it!",
    70: "What is this?! ...It's just a tree stump, isn't it?",
    71: "I bumped into it and gained a fair amount of EXP! Whoa! Is this a magic mallet?!",
    72: "Ow! What is this?! A splinter stuck me, and now my feelings are all splintered, too!",
    73: "I found some tasty tree sap! I'll try it!",
    74: "Whoa! It's sweet and delicious! I think I gained a ton of EXP!",
    75: "Whoa, no! It smells too green and grassy. I can't lick this!",
    83: "...Hm? This is a scale... I'll see how much I weigh.",
    84: "...Heh. I always watch my weight, so no problem. My max HP seems to have gone up a little...",
}

STATUS = {
    'まひよぼう': 'Paralysis Prevention', 'まひガード': 'Paralysis Guard',
    'まひバリア': 'Paralysis Barrier', 'まひちゅうい': 'Paralysis Alert',
    'まひけいかい': 'Paralysis Watch', 'まひニガテ': 'Paralysis Weakness',
    'ねむりよぼう': 'Sleep Prevention', 'ねむりガード': 'Sleep Guard',
    'ねむりバリア': 'Sleep Barrier', 'ねむりちゅうい': 'Sleep Alert',
    'ねむりけいかい': 'Sleep Watch', 'ねむりニガテ': 'Sleep Weakness',
    'こんらんよぼう': 'Confusion Prevention', 'こんらんガード': 'Confusion Guard',
    'こんらんバリア': 'Confusion Barrier', 'こんらんちゅうい': 'Confusion Alert',
    'こんらんけいかい': 'Confusion Watch', 'こんらんニガテ': 'Confusion Weakness',
    'くらやみよぼう': 'Darkness Prevention', 'くらやみガード': 'Darkness Guard',
    'くらやみバリア': 'Darkness Barrier', 'くらやみちゅうい': 'Darkness Alert',
    'くらやみけいかい': 'Darkness Watch', 'くらやみニガテ': 'Darkness Weakness',
    'こころがまえ': 'Mental Readiness', 'せいしんとういつ': 'Mental Focus',
    'さとりのきょうち': 'Enlightenment', 'すべてにちゅうい': 'All-Status Alert',
    'すべてにけいかい': 'All-Status Watch',
    'ＨＰドレかわし': 'HP Drain Dodge', 'ＨＰドレパリィ': 'HP Drain Parry',
    'ＨＰドレアンチ': 'HP Drain Resist', 'ＨＰドレふせぎ': 'HP Drain Block',
    'ＨＰドレはじき': 'HP Drain Reflect', 'ＨＰドレニガテ': 'HP Drain Weakness',
    'ＭＰドレかわし': 'MP Drain Dodge', 'ＭＰドレパリィ': 'MP Drain Parry',
    'ＭＰドレアンチ': 'MP Drain Resist', 'ＭＰドレふせぎ': 'MP Drain Block',
    'ＭＰドレはじき': 'MP Drain Reflect', 'ＭＰドレニガテ': 'MP Drain Weakness',
}

MOVE_TERMS = {
    'アイスアロー': ('Ice Arrow', ['B34_WIKIMON_SEADRAMON'],
                    'Seadramon’s established English attack name in Western Digimon games.'),
    'じゅうおうけん': ('BeastKing Fist', ['DAWN_DUSK_MOVES'],
                       'Matches the Leomon attack spelling in the English Dawn/Dusk move list.'),
    'トイフレイム': ('Toy Flame', ['B34_WIKIMON_TOYAGUMON'],
                    'ToyAgumon’s Western game attack name; confirmed in Digimon World 2 and Digital Card Arena references.'),
    'メガフレイム': ('Mega Flame', ['B34_BANDAI_MEGA_FLAME'],
                    'Greymon’s established Western attack name, also used in official English Digimon card material.'),
    'フラウカノン': ('Flower Cannon', ['DAWN_DUSK_MOVES'],
                    'Matches Lillymon’s Flower Cannon in the English Dawn/Dusk move list.'),
}


def wrap(value: str, width: int) -> str:
    return '\n'.join(
        '\n'.join(textwrap.wrap(line, width, break_long_words=False,
                                break_on_hyphens=False) or [''])
        for line in value.split('\n')
    )


def register_terms(records: dict) -> None:
    path = ROOT / 'translations/glossary.json'
    glossary = json.loads(path.read_text(encoding='utf-8'))
    new_sources = {
        'B34_WIKIMON_SEADRAMON': 'https://wikimon.net/Seadramon',
        'B34_WIKIMON_TOYAGUMON': 'https://wikimon.net/Toy_Agumon',
        'B34_BANDAI_MEGA_FLAME': 'https://world.digimoncard.com/cards/?category=522018&search=true',
        'B34_BANDAI_ZEED': 'https://world.digimoncard.com/cards/?card_no=BT19-101&search=true',
    }
    for key, url in new_sources.items():
        existing = glossary['sources'].get(key)
        if existing and existing['url'] != url:
            raise ValueError(f'Conflicting source ID: {key}')
        glossary['sources'][key] = {'url': url}

    terms = glossary['terms']

    def put(japanese: str, english: str, sources: list[str], category: str, evidence: str) -> None:
        old = next((term for term in terms if term['japanese'] == japanese), None)
        if old:
            if old['english'] != english:
                raise ValueError(f'Conflicting glossary term {japanese}: {old["english"]} vs {english}')
            old['sources'] = list(dict.fromkeys(old['sources'] + sources))
            old['evidence'] = evidence
            return
        if not any(row['source'] == japanese for row in records.values()):
            raise ValueError(f'Glossary source string not present in ROM: {japanese}')
        terms.append({'japanese': japanese, 'english': english, 'category': category,
                      'sources': sources, 'evidence': evidence})

    for japanese, (english, sources, evidence) in MOVE_TERMS.items():
        put(japanese, english, sources, 'Move name', evidence)
    glossary['checked'] = '2026-10-25'
    path.write_text(json.dumps(glossary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    records = collect_messages(Rom(rom_paths()['blue']))
    prior = translate_records(records)
    old_batch = ROOT / 'translations/batch34.json'
    if old_batch.exists():
        old = json.loads(old_batch.read_text(encoding='utf-8'))
        for block in old.get('blocks', []):
            for offset in range(len(block['english'])):
                prior.pop(f"{block['archive']}:{block['entry']:03d}:{block['start'] + offset:05d}", None)
    rows = list(csv.DictReader((ROOT / 'translations/work_queue.tsv').open(
        encoding='utf-8-sig'), delimiter='\t'))
    by_id = {key: row for row in rows for key in row['ids'].split(';')}
    by_category_source = {(row['category'], row['japanese']): row for row in rows}
    blocks, reviews, seen = [], [], set()

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

    story_note = ('Continuation of the game-original Elestou Zone story. Preserve the established ROG, Elestou Zone, Earth Fort, Sky Fort, and Crystal Volcano terms. ZeedMillenniummon uses the official Western Digimon spelling and is deliberately wrapped at the name boundary. Dialogue is wrapped to the 15-cell story limit.')
    for index, english in STORY.items():
        add(f'MSG/MESPAK02.PAK:018:{index:05d}', english, LOCAL,
            story_note, width=15)

    quiz_note = ('Piedmon Special Digimon Quiz 2, a complete optional mission segment. Species names follow the reviewed Western Digimon glossary. Attack names are cross-checked against Western Digimon game references; Beast King Fist and Flower Cannon match Dawn/Dusk, while the other exact spellings are checked against Western game references. Wrapped to the 15-cell dialogue limit.')
    for index, english in PIEDMON_QUIZ.items():
        add(f'MSG/MESPAK02.PAK:021:{index:05d}', english, LOCAL,
            quiz_note, width=15)

    farm_note = ('DigiFarm activity report translated from the Japanese report text. EXP, Friendship, Bits, and stat names match existing project terminology; lines are wrapped for the report box.')
    for index, english in FARM.items():
        add(f'MSG/MESPAK05.PAK:004:{index:05d}', english, LOCAL,
            farm_note, width=26)

    status_note = ('Battle resistance/personality label translated consistently with the Japanese naming pattern. The compact English wording is chosen to stay usable in the status and trait UI.')
    for japanese, english in STATUS.items():
        row = by_category_source.get(('Common labels and traits', japanese))
        if row is None:
            key = next((key for key, record in records.items()
                        if record['source'] == japanese and key in by_id), None)
            if key is None:
                if any(record['source'] == japanese for record in records.values()):
                    continue
                raise ValueError(f'Status label missing from queue/ROM: {japanese}')
        else:
            key = row['ids'].split(';')[0]
        add(key, english, LOCAL, status_note)

    description = ('Continued the Elestou Zone story and translated the Piedmon quiz side mission, further DigiFarm activity reports, and battle status-resistance labels. Added source-checked Western names for five quiz attacks and expanded ZD Millenniummon to the official English name ZeedMillenniummon.')
    out = ROOT / 'translations/batch34.json'
    review_json = ROOT / 'translations/review_batch34.json'
    review_md = ROOT / 'translations/review_batch34.md'
    out.write_text(json.dumps({'description': description, 'blocks': blocks},
                              ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    review_json.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
    lines = [
        '# Batch 34 translation review', '',
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
    records = collect_messages(Rom(rom_paths()['blue']))
    register_terms(records)
    main()
