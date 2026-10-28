"""Create the next reviewed story, farm, and move-description batch."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


STORY = {
    0: "Pharaohmon must be weakening by now. Let's finish him off next time. Come on!",
    1: "Quick question, me! What's my best feature, me?",
    2: "Uh... you're handy when someone gets hurt!",
    3: "Then I'm no use until someone gets hurt, me!",
    4: "Hmm... Guess that wasn't it...",
    5: "Now's the time to use a bandage on your injury, me...",
    6: "Huh?! Did you hurt yourself?",
    7: "My heart's badly hurt, me! I need emergency surgery, me!",
    8: "What's that supposed to mean?!",
    9: "Can you perform surgery on yourself?",
    10: "I don't know what you're sneaking around looking for, but too bad! The DigiShip you're after isn't here, me!",
    11: "DigiShip? What's that?",
    12: "I just came out in the wrong place, me! Those goggles are confusing, me!",
    13: "Where were you trying to go?!",
    14: "Those goggles prove you're the main character, me... Take good care of them, me...",
    15: "Hey, where were you really trying to go?",
    16: "I... I can't tell you that, me!",
    17: "What a strange one...",
    18: "It's sitting in a suspicious spot, practically begging to be found.",
    19: "It had to be hiding somewhere easy to find... Is there something here?",
    20: "Look, you two! It's coming out by itself!",
    21: "Fwa-ha-ha-ha!",
    22: "You found my tomb! That's right, I am Pharaohmon! But this time, there's more!",
    23: "What do you mean? You don't look any different.",
    24: "Fwahahaha! I only ran away to lure you here! Now behold my true power!",
    25: "Pharaohmon... transform!!",
    26: "Whaaaat?!",
    27: "You... Surprised too soon! Behold! Anubismon has arrived!",
    28: "He transformed without DigiXross?! How is that possible?!",
    29: "It's not DigiFusion or Jogress Up... This is Pharaohmon's... no, Anubismon's power!",
    30: "You've made a fool of me long enough! This time I'll defeat you and take everything!",
    31: "He's serious this time! Everyone, be careful!",
    32: "Gah...! How could this happen?! I never thought I'd lose, even after using the Pyramid's power!",
    33: "Anubismon! Tell me about the Legendary Ancient Weapons and the Legendary Warrior! What do they have to do with Spadamon? Maybe you ROG guys know more than Spadamon, who lost his memories!",
    34: "It's true that ROG chased Spadamon on ZeedMillenniummon's orders, to find the Legendary Weapons. But those days are over! ROG has found the seal of the Legendary Ancient Weapons! ROG's age of glory starts now!",
    35: "You found the seal of the Legendary Ancient Weapons...?",
    37: "Well? Did you remember anything?",
    38: "The weapons' seal... Maybe we'll learn something if we activate every Capacitor System. There are seven in all...",
    39: "Seven? We've only visited six Areas so far.",
    40: "Huh? Maybe I'm mistaken... I thought there were seven.",
    41: "Spadamon... You're bad at math, aren't you? Don't worry! Picture a Digi-no-wa in your head and you can count as high as you like!",
    42: "Hey... Something's lying over there.",
    43: "What does that key go to?",
    44: "It's the key to a gate in Twisting Amazon. It's near the route we took to the Digital Space. Papyrus Desert is close to Twisting Amazon.",
    45: "So we went in a big circle and ended up back where we started?",
    46: "Yeah, so there are only six towers after all... Once we activate all the Capacitor Towers, we'll learn the secret of the Legendary Ancient Weapons' seal! Then maybe I'll remember everything...",
    47: "Then all the more reason to activate the towers! Let's get every Capacitor Tower running!",
    48: "You picked wrong, me! Your opponent is the lonely Mummymon, me!",
    49: "Oh... We got the wrong one.",
    50: "Who's wrong?! Don't underestimate Mummymon, me! I'll beat you to a pulp, me!",
    51: "You're the one who called us the wrong choice...",
    52: "Ugh... I'm the bottom-of-the-barrel weakling here again, me. Do what you want. Laugh at me all you like, me...",
    53: "That's not what I meant, Mummymon.",
    54: "I already know I'm the wrong choice, me!",
    55: "No, that's not it. I mean you're no weakling. You're one of the strongest opponents we've faced!",
    56: "I-I... I won't be fooled by flattery, me! I'll remember this, me!",
    57: "Was that... embarrassment?",
    58: "You touched a coffin in Papyrus Desert... That means you're picking a fight with Mummymon, me?!",
    59: "Huh? No, we didn't come here for Mummymon. It was just... a coincidence... sort of.",
    60: "Who touches someone's coffin by accident, me?! What if someone rang your doorbell? Wouldn't you be mad if they said it was an accident, me?!",
    61: "I-I'm sorry!",
    62: "I'll remember your face, me! Mummymon never forgets a grudge until he's in the grave, me!",
    63: "But doesn't Mummymon already live in a grave...?",
    64: "Look, it's right there! Isn't a place like this scary?",
    65: "You have no sense of adventure, kid! Mine's tingling!",
    66: "Hmm... But still...",
    67: "Akari! Zenjiro! Patamon! We're back! What are you scared of?",
    68: "Hey! Isn't it scary when machines start up by themselves?",
    69: "A giant machine starting up... Isn't that exciting?!",
    71: "There's an underground base in Elestou Zone called Earth Fortress, besides the Sky Fortress. It had been shut down ever since ROG invaded... But Earth Fortress suddenly started moving. Maybe it's because we activated the Capacitor Towers...",
    72: "Oh! So that means... A new base is finally opening up on the Energy Continent! Where is Earth Fortress?",
    73: "They say it's in a place called Crystal Volcano... But that's the scary part!",
    74: "C-Crystal Volcano?!",
    75: "Zenjiro, what do you mean? Why is it scary?",
    76: "They say Crystal Volcano is terrifying... The wild Digimon there are fierce! Akari may be scared, but this whole chain of events... I feel the thrill of a giant secret base coming online!",
    77: "That's all you ever talk about! Taiki, do something about Zenjiro!",
    78: "I'm checking where the port to Crystal Volcano is. While I do, could you help with something? Our Digimon friends are returning, and they've sent requests to the Quest Monitor. Can you help grant as many as possible?",
    79: "We're helping as much as we can, but they say it's dangerous to leave the Sky Fortress, so there's only so much we can do.",
    80: "Would you believe Digimon are lining up to see me? Ah, being popular is tough!",
    81: "Zenjiro's a great playmate for the Pickmons. I guess he's only popular with the little ones!",
    82: "So we'll have to ask you to handle requests that involve leaving the Sky Fortress. Please grant as many as you can.",
    83: "Everyone at the Sky Fortress is counting on you! Ask us if there's anything you want to know!",
    84: "Requests, huh? You're pretty popular, Taiki! Maybe you'll become the Legendary Warrior of Elestou Zone someday!",
    85: "Spadamon's more suited to be a warrior than I am. Right, Spadamon?",
    86: "...Huh? What's wrong, Spadamon?",
    87: "I-It's nothing! Don't look at me! I heard Crystal Volcano is terrifying... My legs aren't shaking or anything!",
    88: "Spadamon... Is it really that scary? I'm excited to explore a new Area!",
    89: "Yeah, it's a pretty place! And I hear the crystals there are sweet and tasty!",
    90: "Really?! Th-Then I'm going too! Sweet crystals... I can't wait!",
    91: "He likes sweets that much? Maybe Spadamon will post a Quest Monitor request for a tasty cake someday.",
    92: "Sweets are the best way to get motivated! All right, please take care of everyone's requests!",
    93: "Taiki, Taiki! Big news!",
    94: "We found the port to Crystal Volcano!!",
    95: "Great! You finally found it!",
    96: "Oh no... So you found it...",
    97: "There's a little problem, though... Can you come to the Central Room? I need to explain.",
    98: "So it won't be that simple after all...",
    99: "Then I'll have to brace myself, too.",
    100: "Taiki, come right away!",
    101: "Did the Flight Team gather everyone?",
    102: "Yeah. Let's hear the details in the Central Room.",
    103: "I can't wait to fly through the sky!",
    104: "Hey, Taiki! Wait a second!",
    105: "We need to check the Capacitor Towers first! There was an entrance to a tower along the path we just came from. Why not check it out?",
    106: "Let's see... Armadillomon in the mountain near the Sky Fortress can dig. The Tyrannomon around here should be able to dig, too.",
    107: "Are you sure this is the right thing to do?",
    108: "Enough, MailBirdramon. There is no other way.",
    109: "Huh? Is that Kiriha and MailBirdramon over there?",
    110: "Why is Kiriha here? Don't tell me he followed Taiki just because they're rivals?",
    111: "It looks like he's holding something... What is that? Some kind of machine?",
    112: "Taiki! That device he's holding... It's a Pathfinder Device, something only found at the Sky Fortress! How?! Where did he get it?!",
    113: "Kiriha, it seems we've been interrupted.",
    114: "Taiki and the others coming was within the expected range. Hurry, MailBirdramon. Find the Legendary Ancient Weapons! Linkage: Path Connect! Destination input: Lost Space!",
    115: "The Legendary Ancient Weapons and Lost Space...? No... Stop him, Taiki! ROG is desperately searching for Lost Space. It must be where the weapons are hidden!",
    116: "W-What?! Why is Kiriha there?!",
    117: "Stop, Kiriha! ROG will find out!",
    118: "Anything that stands in the way of the plan must be eliminated. Even if it's Xros Heart... Is that right, Kiriha?",
    119: "...The orders haven't changed. No one can stop us. We are the blue flame, Team Blue Flare! Do it, MailBirdramon!",
    120: "Kiriha... Hurry... Connect...",
    121: "Sorry, Taiki. There's no other way... Linkage: Path Connect! Destination input: Lost Space!",
    123: "Find the Legendary Digimon...!",
    124: "Taiki! Get away! Something's wrong!",
    126: "The Legendary Weapons... The Legendary Digimon... I'm so close to remembering... But we must never let them into Lost Space!",
    128: "What?! The connection was rejected?! The energy... It's going to explode!",
    139: "What happened after the explosion? Where are Kiriha and the others?",
    140: "I don't know... But I don't think they made it to Lost Space.",
    148: "Huh? Kiriha? What's he doing here alone?",
    149: "Looks like he's searching for something... Be careful, Taiki. He might attack without warning!",
    150: "But he isn't your enemy, right? Maybe talking to him will help...",
    151: "Kiriha, what are you doing? Why are you searching for the Legendary Ancient Weapons?",
    152: "Taiki... There's no point trying to stop me. I'll get them, no matter what.",
    153: "You mean the Legendary Weapons?",
    154: "It's none of your business. Stay out of it.",
    155: "Wait, Kiriha! What's driving you so hard? If there's a reason, tell us.",
    156: "...What I want is the power to change everything.",
    157: "The power to change everything...?",
    158: "I thought he was cool, but now he's even harder to approach.",
    159: "Still... he looked so sad.",
    160: "Maybe we should look for Sparrowmon first. He might be nearby.",
    161: "You're right. Let's look for Sparrowmon first. But we can't leave Kiriha like this...",
    162: "Phoenixmon scouted from the sky... It looks like things are bad around Earth Fortress.",
    173: "What?! Is that true? But we can't let ROG break the seal! We have to stop them!",
    179: "Thanks, Phoenixmon. We need to make sure we're ready, too!",
    180: "Whoa...",
    181: "That Digimon was the one who occupied the Sky Fortress!",
    182: "Just as the Flight Team said... ROG's leader Digimon is protecting ZeedMillenniummon.",
    183: "W-We have to hurry to Earth Fortress, or ROG will get the Legendary Weapons!",
    184: "You again... I can't believe you're still alive!",
    185: "Stop making this Zone suffer!",
    186: "We'll take back Elestou Zone!",
    187: "Still as irritating as ever! But I have no way around it... I can't let you pass!",
    188: "Grrrraaaaaah!",
    189: "What was that...?",
    190: "Lord ZeedMillenniummon! Now, take my power!",
    191: "W-What?! What's happening to him?",
    192: "We are ROG! We'll do anything to get everything we desire, even if we have to sacrifice ourselves!",
    193: "W-What did you say?!",
    194: "H-Hey... What is that?",
    195: "That's right, Minotaurmon... I want your power. If you're destined to become dust, become one with me...",
    196: "With this power, I'll be reborn as the strongest!",
    197: "W-What was that?! Did he just devour Minotaurmon?",
    198: "Every boss we've fought absorbed their underlings to become stronger... Could that shadow be... ZeedMillenniummon?!",
    199: "...That's likely. Stay alert.",
}


DESCRIPTIONS = {
    (4, 34): "Glares at all foes\nwith its dark eye.",
    (4, 35): "Slashes nearby foes\nwith star-shaped\nshuriken.",
    (4, 36): "Slashes a foe with\na charged sickle.",
    (4, 37): "Calls down lightning\non a foe.",
    (4, 38): "Calls down a huge\nbolt on nearby foes.",
    (4, 39): "Summons a barrage\nof lightning on\nnearby foes.",
    (4, 40): "Fires an electric\norb at a foe.",
    (4, 41): "Fires a powerful\nelectric orb at a foe.",
    (4, 42): "Slashes a foe with\ncharged claws.",
    (4, 43): "Rakes a foe with\nelectric claws.",
    (4, 44): "Strikes a foe with a\nbewildering electric\nwhip. May confuse.",
    (4, 45): "Lashes a foe with a\ndangerous electric\nwhip. Drains HP.",
    (4, 46): "Pierces a foe with\ndigital-data energy.\nMay confuse.",
    (4, 47): "Blasts foes with a\nhigh-voltage orb.",
    (4, 48): "Fires a blazing blue\nflame. May lower\nAttack.",
    (4, 49): "Incinerates a foe\nwith a searing beam.",
    (5, 0): "Slashes a foe with a\ncross-shaped strike.",
    (5, 1): "Bites a foe with\nterrifying fangs.",
    (5, 2): "Knocks a foe back\nwith a twisting\npillar of water.",
    (5, 3): "Tears at a foe with\nblade-like claws.",
    (5, 4): "Rakes a foe with\nsharp claws. May\nlower Attack.",
    (5, 5): "Rakes a foe at\nblinding speed.",
    (5, 6): "Slashes a foe with\nmajestic claws.",
    (5, 7): "Focuses beast power\nin a fist and strikes\na finishing blow.",
    (5, 8): "Fires an energy wave\nfrom a beast-powered\nfist.",
    (5, 9): "Pummels nearby foes\nwith a hard fist.",
    (5, 10): "Strikes a foe with a\nsupersonic punch.",
    (5, 11): "Hits a foe with a\ndevastating punch.",
    (5, 12): "Curls up, spins, and\nrams a foe.",
    (5, 13): "Charges into nearby\nfoes with all its\nstrength.",
    (5, 14): "Rams nearby foes\nwith all its might.\nMay paralyze.",
    (5, 15): "Fires a ball of dark\nenergy at a foe. May\ncause Blindness.",
    (5, 16): "Shoots a foe with an\nenergy ball of dark\nmessengers.",
    (5, 17): "Fires a dark-chaos\nenergy ball at a foe.",
    (5, 18): "Fires a dark-aura\narrow that destroys\na foe's data.",
    (5, 19): "Fires an arrow of\ndark messengers to\ndestroy foe data.",
    (5, 20): "Fires an arrow of\ndark chaos to bury\na foe.",
    (5, 21): "Blasts nearby foes\nwith dark energy.",
    (5, 22): "Cuts a foe down with\none holy slash.",
    (5, 23): "Tears a foe with\nsharp dark claws.",
    (5, 24): "Tears a foe with\nrazor-sharp dark\nclaws.",
    (5, 25): "Tears a foe with\nlife-draining claws.",
    (5, 26): "Slashes a foe with a\nlife-draining sword.\nDrains MP.",
    (5, 27): "Cuts a foe with a\nchaotic slash. May\ncause Blindness.",
    (5, 28): "Cuts a foe with a\njet-black slash.",
    (5, 29): "Hurls foul-smelling\npoop at a foe. May\ncause Blindness.",
    (5, 30): "Spreads a ward that\ncleanses evil. Raises\nallies' Intelligence\nand Attack.",
    (5, 31): "Fires sacred pyramid\nlight at nearby foes.\nMay cause Blindness.",
    (5, 32): "Spits a bubble of\nlight at a foe.",
    (5, 33): "Spits a bubble of\ndarkness at a foe.",
    (5, 34): "Shoots a foe with a\nneedle of lightning.",
    (5, 35): "Fires a ball of\nblazing blue fire at\na foe.",
    (5, 36): "Smashes a foe with\na spiked iron ball.",
    (5, 37): "Fires an electric\nenergy bullet at a foe.",
    (5, 38): "Hurls a dark\nshuriken at a foe.",
    (5, 39): "Calls down blue\nlightning on a foe.",
    (5, 40): "Fire raises one\nally's Attack and\nIntelligence.",
    (5, 41): "Strong fire raises\none ally's Attack and\nIntelligence.",
    (5, 42): "Intense fire raises\none ally's Attack and\nIntelligence.",
    (5, 43): "Water raises one\nally's Defense.",
    (5, 44): "Strong water raises\none ally's Defense.",
    (5, 45): "Powerful water\nraises one ally's\nDefense.",
    (5, 46): "Inputs a cursed\nprogram into a foe.\nMay cause Confusion.",
    (5, 47): "Light raises one\nally's Speed.",
    (5, 48): "Strong light raises\none ally's Speed.",
    (5, 49): "Powerful light\nraises one ally's\nSpeed.",
}


FARM = {
    95: "Is that tasty sap?\nIf it's really that good,\nmaybe I'll taste it.",
    96: "Oh, it's sweet and\nquite tasty!\nI seem to have gained\nlots of EXP!",
    97: "Ugh! It's so sticky\nand hard to lick!",
}


SOURCES = {
    "Anubismon": "https://world.digimoncard.com/cards/index.php?card_no=EX5-062&search=true",
    "Mummymon": "https://world.digimoncard.com/cards/index.php?card_no=BT3-087&search=true",
    "Phoenixmon": "https://world.digimoncard.com/cards/index.php?card_no=EX1-010&search=true",
    "MailBirdramon": "https://world.digimoncard.com/cards/?category=522015&search=true",
    "SkullKnightmon": "https://world.digimoncard.com/cards/?card_no=EX10-026&search=true",
    "Spadamon": "https://world.digimoncard.com/rule/pdf/booster_xros_encounter_BT10.pdf",
    "Armadillomon": "https://world.digimoncard.com/cards/?card_no=BT3-032&search=true",
    "Tyrannomon": "https://world.digimoncard.com/cards/?category=522001&search=true",
}


def untranslated(records, already, seed, expected_category):
    record = records[seed]
    if category(record) != expected_category:
        raise ValueError(f"Wrong category for {seed}: {category(record)}")
    if seed in already:
        raise ValueError(f"Already translated: {seed}")
    aliases = [r for r in records.values()
               if r["source"] == record["source"]
               and category(r) == expected_category
               and r["id"] not in already]
    return aliases


def main():
    out = ROOT / "translations/batch60.json"
    if out.exists():
        raise FileExistsError(f"Will not overwrite {out}")
    records = collect_messages(Rom(rom_paths()["blue"]))
    already = translate_records(records)
    expected_story = {
        f"MSG/MESPAK02.PAK:006:{i:05d}" for i in range(200)
        if f"MSG/MESPAK02.PAK:006:{i:05d}" in records
        and f"MSG/MESPAK02.PAK:006:{i:05d}" not in already
        and records[f"MSG/MESPAK02.PAK:006:{i:05d}"]["source"].strip()
    }
    authored_story = {f"MSG/MESPAK02.PAK:006:{i:05d}" for i in STORY}
    if expected_story != authored_story:
        raise ValueError(f"Story coverage mismatch: missing={sorted(expected_story-authored_story)} extra={sorted(authored_story-expected_story)}")

    blocks = []
    reviews = []
    seen = set()

    def add(seed, english, expected_category, note, extra_sources=()):
        aliases = untranslated(records, already, seed, expected_category)
        sources = ["Original Japanese ROM"] + list(extra_sources)
        ids = []
        for record in aliases:
            if record["id"] in seen:
                raise ValueError(f"Duplicate assignment: {record['id']}")
            seen.add(record["id"])
            ids.append(record["id"])
            blocks.append({
                "archive": record["archive"], "entry": record["entry"],
                "start": record["index"], "category": expected_category,
                "english": [english], "sources": sources,
                "review_note": note,
            })
        reviews.append({
            "category": expected_category, "japanese": records[seed]["source"],
            "ids": ids, "english": english, "evidence": sources,
            "review_note": note,
        })

    story_note = (
        "Translated from the original Japanese story script. Character names and "
        "area terms follow the project glossary; Anubismon, Mummymon, Phoenixmon, "
        "MailBirdramon, SkullKnightmon, Spadamon, Armadillomon, and Tyrannomon "
        "use checked official English card references where those names occur."
    )
    for index, english in STORY.items():
        seed = f"MSG/MESPAK02.PAK:006:{index:05d}"
        used_sources = [url for term, url in SOURCES.items() if term in english]
        add(seed, english, "Story and dialogue", story_note, used_sources)

    move_note = (
        "Translated from the original Japanese technique/effect text. Stat names "
        "follow the English UI glossary; effects are kept concise for the move-info panel."
    )
    for (entry, index), english in DESCRIPTIONS.items():
        seed = f"MSG/MESPAK04.PAK:{entry:03d}:{index:05d}"
        add(seed, english.replace("\\n", "\n").replace("foes", "enemies").replace("foe", "enemy"),
                "Move and item descriptions", move_note)

    farm_note = (
        "Translated from the original Japanese DigiFarm report; EXP terminology "
        "follows the game's existing English UI."
    )
    for index, english in FARM.items():
        seed = f"MSG/MESPAK05.PAK:007:{index:05d}"
        add(seed, english, "DigiFarm reports", farm_note)

    batch = {
        "description": (
            "Continue the Pharaohmon and Crystal Volcano story; translate the next "
            "66 battle-technique effects and remaining tree-sap DigiFarm reports."
        ),
        "blocks": blocks,
    }
    out.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = [
        "# Batch 60 review",
        "",
        f"Added {len(blocks)} message slots: {sum(len(r['ids']) for r in reviews if r['category'] == 'Story and dialogue')} story/dialogue, "
        f"{sum(len(r['ids']) for r in reviews if r['category'] == 'Move and item descriptions')} move effects, and "
        f"{sum(len(r['ids']) for r in reviews if r['category'] == 'DigiFarm reports')} DigiFarm reports.",
        "",
        "Western Digimon spellings use the official card references listed per entry where applicable. The Japanese game calls ホウオウモン; the English name is Phoenixmon. Digi-no-wa is retained as a playful game-only phrase because no official English localization was found.",
        "",
        "| Category | IDs | English | Evidence |",
        "|---|---|---|---|",
    ]
    for row in reviews:
        review.append("| " + row["category"] + " | " + ", ".join(row["ids"]) + " | "
                      + row["english"].replace("\n", "<br>").replace("|", "\\|")
                      + " | " + ", ".join(row["evidence"]) + " |")
    (ROOT / "translations/review_batch60.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(out), "blocks": len(blocks),
        "review_rows": len(reviews), "story_slots": sum(len(r["ids"]) for r in reviews if r["category"] == "Story and dialogue"),
        "description_slots": sum(len(r["ids"]) for r in reviews if r["category"] == "Move and item descriptions"),
        "farm_slots": sum(len(r["ids"]) for r in reviews if r["category"] == "DigiFarm reports"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
