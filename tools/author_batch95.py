"""Translate the next side-mission and NPC dialogue block."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


ENTRY20 = {
    0: "Thanks, Taiki! The Giro-Giro Gang is finished! ...But the Mame-Mame Gang broke up first. I guess we just couldn't get along. Here's our first and last reward!",
    1: "The Mame-Mame Gang has disbanded! ...Well, it's been fun!",
    2: "Nanomon L from the Giro-Giro Gang is my eternal rival! Obviously, I should be the one to declare an all-out showdown... Right?!",
    3: "The Giro-Giro Gang's hideout? I wish I knew! Maybe it's near MetalMamemon. He always ends up in the same places as they do...",
    4: "TD Ballmon from the Giro-Giro Gang is my eternal rival! Mamemon acts like he's declaring an all-out showdown, but I came up with that idea first!",
    5: "Their hideout? No idea. Probably around here. Somehow they always end up wherever I am!",
    6: "You're a spy for the Mame-Mame Gang?! Enough! Stop yapping! Let's settle this!",
    7: "I give! I give! I really can't do this! We used to throw our weight around as the Giro-Giro Gang, but we disbanded ages ago!",
    8: "Tell Mamemon we're done fighting. I'm going straight from now on!",
    11: "Huh? It was Monzaemon? Wow, we look just alike! ...What? Where?! He needs to lose weight, too? Mind your own business! ...Sorry about that. Seems the tip was fake. I'll make it up to you with a bigger reward. Forgive me, okay?",
    12: "That guy spread a false rumor! I'll have to teach him a lesson. ...Monzaemon? You've got to be kidding! Maybe your eyes are bad... See you later!",
    13: "What? Frigimon? What about him? ...You think I'm that fool's fake?! How do we look alike? I'll pound you!",
    14: "Fine, I'll let it go this time! Tell that fool Frigimon to slim down!",
    15: "So I'm a fake Frigimon? That's just because our silhouettes look alike, right? We've both gotten round in more ways than one! Tell Frigimon to slim down, too. See ya!",
    18: "Huh? It was Pandamon? Wow, we look just alike! ...What? Where?! He needs to lose weight, too? Mind your own business! ...Sorry about that. Seems the tip was fake. I'll make it up to you with a bigger reward. Forgive me, okay?",
    19: "That guy spread a false rumor! I'll have to teach him a lesson. ...Pandamon? You've got to be kidding! Maybe your eyes are bad... See you later!",
    20: "Huh? Frigimon? What about him? ...You think I'm his fake?! What do we have in common?! Don't say ridiculous things!",
    21: "Even if you call me a fake Frigimon... our silhouettes just look alike, right? We've both gotten round in more ways than one! Tell Frigimon to slim down, too!",
    22: "Fine, I'll let it go today! Tell Frigimon to slim down soon!",
    23: "Wisemon keeps interrupting my studies! He's in Twisted Amazon West. Please do something about him!",
    24: "Please deal with Wisemon in Twisted Amazon West! If he keeps interrupting my studies, I'll never pass the Witchelny exam!",
    25: "Th-thanks... Really, thank you! Now I can finally study in peace... Wait, I don't feel like studying anymore. This spellbook is so thick! I'll never memorize it, and I don't even want to try. That's it! I'm not going back to Witchelny or taking the exam!",
    26: "Please let me join your team! I'll forget about Witchelny and live here in this zone. I'll be waiting, so come talk to me anytime!▼",
    27: "Wizardmon says I'm distracting him from studying? He isn't studying at all! He has no will to study, and not the brains for it, either. That fool is just looking for an excuse to quit! Don't blame me!",
    28: "...Here, take this. Tell Wizardmon to keep studying.",
    29: "Tell Wizardmon to keep at it. If he passes the exam, he'll be a Witchelny elite. Tell him not to end up wasting his life here like me... That's all.",
    30: "Diatrymon keeps picking on me! I bet it wants to catch and eat me! It's in Twisted Amazon West. Please do something!",
    31: "Please defeat Diatrymon in Twisted Amazon West! If this keeps up, it'll eat me!",
    32: "Th-thanks! You really saved me! Feathers? Powder? What's that? I don't care anymore. Because of you, I finally have confidence! I won't lose so easily to any Digimon! No more hiding. I'll fight back from now on!",
    33: "Please let me join your team! I want to grow the strength I've been holding back. I'll be waiting here, so come talk to me anytime!",
    34: "Mushmon has a message for me? I don't care. Come any closer and I'll knock you out! Get lost, both of you! You stink like mold!",
    35: "Mushmon says I'm going to eat him? No way! I won't go near that poisonous mushroom. That idiot spreads mold spores whenever he moves, so he stinks! He thinks I hate him, but he's just playing the victim. I'll give you one of my feathers. Tell him to dust himself off!",
    36: "If you're his messenger, tell Mushmon this: if he spreads mold spores around again, I'll stomp on him! Use my feathers to brush all that powder off, too!",
    37: "Th-this is bad! I don't have nearly enough Bits to pay BE Myotismon! I made this fake 'Bits-like stuff' in a hurry. Could you fool him with it somehow? He's in Skull Seabed!",
    38: "I don't have enough Bits to pay BE Myotismon! Please try to fool him with this 'Bits-like stuff.' He's in Skull Seabed!",
    39: "Looks like you solved it! I survived by the skin of my teeth! Please take this small reward!▼",
    40: "Looks like it worked out after all! I'll ask you again next time I run out of money. ...Huh? The 'Bits-like stuff'? I don't need it anymore!▼",
    41: "Who are you? Devimon's substitute? Doesn't matter. Hand over 200,000 Bits! ...What's this filthy, ugly thing? ...'Bits-like stuff'? It's obviously fake! Who would want this? If you can't pay 200,000 Bits, I'll take it from you!",
    42: "I don't care who you are or why you're here. Pay me 200,000 Bits right now!",
    43: "Pay 200,000 Bits?",
    44: "Fine... I'll pay.",
    45: "No way!",
    46: "Then I'll beat 200,000 Bits' worth out of you!",
    47: "Hmph. You're strong enough to defeat me. You're worth 200,000 Bits after all! Tell Devimon I'll let it slide this time. ...What's that? The 'Bits-like stuff'? Keep it. I don't want it!",
    48: "Hmph. That's 200,000 Bits. Tell Devimon to bring it himself next time.",
    49: "That's not enough! I said 200,000 Bits. Can't you even count?",
    50: "Get lost, Devimon's lackey! I have no use for you anymore.",
    51: "We're broke! No money at all! I don't have enough Bits to pay BE Myotismon! I made this 'Bits-ish stuff' in a hurry. Could you fool him with it somehow? He's in Skull Seabed!",
    52: "I don't have enough Bits for BE Myotismon! Please fool him with this 'Bits-ish stuff.' He's in Skull Seabed!",
    53: "Looks like you fixed everything! I think I just barely saved my life! Please accept this small reward!▼",
    54: "Looks like it worked out! I'll ask again next time I blow all my money. ...Huh? The 'Bits-ish stuff'? I don't need it anymore!▼",
    55: "Who are you? Evilmon's substitute? Doesn't matter. Hand over 200,000 Bits! ...What's this filthy, ugly thing? ...'Bits-ish stuff'? It's obviously fake! Who would want this? If you can't pay 200,000 Bits, I'll take it from you!",
    56: "I don't care who you are or why you're here. Pay me 200,000 Bits right now!",
    57: "Then I'll beat 200,000 Bits' worth out of you!",
    58: "Hmph. You're strong enough to defeat me. You're worth 200,000 Bits after all! Tell Evilmon I'll let it slide this time. ...What's that? The 'Bits-ish stuff'? Keep it. I don't want it!",
    59: "Hmph. That's 200,000 Bits. Tell Evilmon to bring it himself next time.",
    60: "That's not enough! I said 200,000 Bits. Can't you even count?",
    61: "Get lost, Evilmon's lackey! I have no use for you anymore.",
    62: "Puppetmon has been searching for a meteorite for ages. It's getting annoying, so find one first and give it to him! Ask Vademon in Twisted Amazon East to appraise it. If it's real, take it to Puppetmon. Hurry!",
    63: "The meteorite fell somewhere in Skull Mountain West. Have Vademon appraise it in Twisted Amazon East. If it's real, give it to Puppetmon in Dark Tunnel. Got it? Now hurry!",
    64: "You found it and gave it to him? That was fast! ...Was he thrilled? Good. I don't know why he wanted a meteorite so badly, but Puppetmon looked so desperate that I couldn't ignore him. Helping him search myself would've been embarrassing, too... ...Anyway, thanks!",
    65: "Could you do one more thing for me? If you want, I'd like to join your team. Just come talk to me if you change your mind... okay?",
    68: "Oh, a meteorite? Let me take a look... ...Whoa! It's real! This is the meteorite Puppetmon was desperately searching for! Hurry and take it to him!",
    69: "It's what you'd call a 'Nice Meteor'! They say nice wishes come true if you make them on a nice meteor. Give it to the downhearted Puppetmon in Dark Tunnel.",
    70: "This is the 'Nice Meteor'?! I can have it? Thank you so much! Maybe my wish will come true. A meteor is a falling star, right? I'll wish on it... I hope Lilamon opens up and makes some friends!",
    71: "Thanks, Taiki. Could you do one more thing for me? Would you check whether Lilamon has started acting nicer?",
    72: "ToyAgumon has been searching for a meteorite for ages. He's so desperate that I can't watch anymore. Find it first and give it to him! Ask Vademon in Twisted Amazon East to appraise it. If it's real, take it to ToyAgumon. Please!",
    73: "The meteorite fell somewhere in Skull Mountain West. Have Vademon appraise it in Twisted Amazon East. If it's real, give it to ToyAgumon in Dark Tunnel. Please!",
    74: "You found it and gave it to him? Was he happy? I'm glad! I meant to help him search, but my wings hurt the whole time, so I'd only have gotten in the way... Why did he want a meteorite so badly? ...My wings? Maybe I was so relieved that they suddenly stopped hurting! Thank you! Take your reward!▼",
    75: "Hey, I have one more favor to ask. Would you let me join your team? Just come talk to me if you change your mind!",
    78: "Oh, a meteorite? Let me take a look... ...Whoa! It's real! This is the meteorite ToyAgumon was desperately searching for! Hurry and take it to him!",
    79: "It's what you'd call a 'Nice Meteor'! They say nice wishes come true if you make them on a nice meteor. Give it to the downhearted ToyAgumon in Dark Tunnel.",
    80: "This is the 'Nice Meteor'?! I can have it? Yes! Thank you so much! Maybe my wish will come true. A meteor is a falling star, right? I'll wish on it... I hope Parrotmon can fly around happily again!",
    81: "Thanks, Taiki. Could you do one more thing for me? Would you check how Parrotmon's wings are doing?",
    105: "Ankylomon asked me to do this on DigiFarm: interview Paildramon in Twisted Amazon West and record it on this voice recorder! Got it? Paildramon, okay?!",
    106: "Please interview Paildramon in Twisted Amazon West and record it on this voice recorder. Just checking... You know who Paildramon is, right?",
    107: "Thanks, you saved me! Here's your reward. Let's listen... ...Huh?! Is this really an interview? It sounds like nothing but shouting in a speech!",
    109: "An interview? No, I refuse! ...But don't worry! I was ready for this. I prepared some P-voice data right here!",
    110: "Give my regards to all the fans! Count on you!",
    111: "You want to interview me...? Are you sure you have the right Digimon? Maybe you meant Paildramon... Or Paildramon... Or, perhaps, Paildramon? So you did get me mixed up? Anyone can make a mistake. That doesn't mean I'll forgive you!",
    112: "My eyes, my head, my guts... all rotten! How can you confuse a dragon with an insect?!",
    113: "You came to see Paildramon, right? Keep dawdling and I'll kick you in the rear!",
    165: "Yes! The answer is Lovely Attack! But getting hit by that guy's attack doesn't feel like love at all! Ha ha!",
    173: "Yay! Congratulations! That's the end of my special lucky quiz for you! Report your results to Okuwamon in Papyrus City! Got it? Ha ha!",
    174: "That's the end of my special lucky quiz for you! Report your results to Okuwamon in Papyrus City!",
}


def main() -> None:
    destination = ROOT / "translations/batch95.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in ENTRY20.items():
        key = f"MSG/MESPAK02.PAK:020:{index:05d}"
        if key not in records or key in existing:
            raise ValueError(f"Missing or already translated source: {key}")
        row = records[key]
        if category(row) != "Story and dialogue":
            raise ValueError(f"Unexpected category for {key}: {category(row)}")
        sources = ["Original Japanese ROM", "Existing reviewed project glossary"]
        if "Frigimon" in english:
            sources.append("https://digimon.net/reference_en/detail.php?directory_name=yukidarumon")
        if "Lovely Attack" in english:
            sources.append("https://raw.githubusercontent.com/joaomlsantos/Digimon-World-Dawn-Dusk-Research-Notes/master/move_name_lst.txt")
        blocks.append({
            "archive": row["archive"], "entry": row["entry"],
            "start": row["index"], "category": "Story and dialogue",
            "english": [english], "sources": sources,
            "review_note": "Twisted Amazon side-quest dialogue and NPC branches. Established Digimon names follow the existing project glossary; Nice Meteor and Bits-like stuff are working renderings of game-specific wordplay.",
        })
    if len(blocks) != 85:
        raise ValueError(f"Expected 85 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate the Mamemon rivalry, Witchelny and Diatrymon quests, BE Myotismon tribute branches, meteorite errands, Paildramon interview, and quiz response in MESPAK02 entry 20.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
