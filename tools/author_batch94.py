"""Translate remaining zone NPC dialogue and tournament reactions."""
from __future__ import annotations

import json

from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths


ENTRY18 = {
    0: "Taiki, where did you go? Pipimon doesn't want you to get hurt! You understand?",
    1: "Taiki, what's wrong? Don't know where to go? Can't get out of Twisted Amazon? There's a path right beside you!",
    2: "Sparrowmon can't get out of the ruins? Then hurry and go help it, Taiki!",
    3: "Hey, Taiki! Did you find Sparrowmon? Did you find the key to the ruins? Then hurry and rescue it!",
    4: "Sparrowmon's back! You're amazing, Taiki! Everyone's so happy!",
    27: "Your friend was kidnapped?! That's serious! A tiny, squishy, triangle-shaped Digimon? I saw that little one by the other Capacitor Tower on Knuckle Coast. It was following someone toward Twisted Amazon...",
    42: "Thanks for driving ROG out! We were scared by how strong you are. I hope those ROG guys leave this zone soon. I just want peace again.",
    51: "Thanks so much, kwah! I'm happy to be back in the city! Earth Fort? Hmm, never heard of it. I know Sky Fort, but that isn't the same place, kwah...",
    61: "Geko! Geko! Listen to my song! I won't move until it's over! I'm ShogunGekomon of the iceberg, the Endless Singer, the Ice Lord! The Volcano Lord lives in the volcano, and I live on the iceberg. Together we're the Lords! Geko!",
    65: "Web City means Penmon's Item Shop! But I don't get many customers. I'll be caught in a web at this rate! Get it? Web City!",
    68: "I heard a rumor that someone was taking Capacitor Towers back from ROG, but I never thought it was true! I'm shaking with joy! Hahaha!",
    69: "Everyone says a savior came to rescue this zone. Seeing you, I believe it! We're counting on you, savior!",
    70: "Thanks so much, Taiki! To thank you for saving me, I'll share a tip. If you can't get farther in Papyrus Desert, open the huge coffin. Once it's open, just keep going!",
    71: "You're the saviors of this zone! I really believe that from the bottom of my heart. Please grant the Digimon's wishes on the Quest Monitor!",
    72: "Papyrus City means Penmon's Item Shop! Don't be shy. Buy as much as you like!",
    75: "I couldn't protect this place... I was supposed to be the one holding this zone together...",
    92: "Taiki, are you doing your best? Pipimon will try hard, too! Call on Pipimon!",
    93: "Pipimon will work hard and become a Star Sword! My eyes will sparkle, and everyone will be ready to go!",
    96: "West Knuckle City is famous for Penmon's Item Shop! We call it the Double Shop. There's nothing double about it, though!",
    101: "East Knuckle City is famous for Penmon's Item Shop! We call it the E Shop. Pretty neat, huh?",
    106: "Twisted City is famous for Penmon's Item Shop! We call it the Twisted Shop. Just hearing that makes you dizzy!",
    111: "Skull City is famous for Penmon's Item Shop! We call it the Skull Shop. Sounds pretty shady!",
    118: "Web City is famous for Penmon's Item Shop! We call it the Web Shop. Doesn't sound like many customers come here...",
    125: "Papyrus City is famous for Penmon's Item Shop! We call it the Papyrus Shop. That's a mouthful!",
    130: "Geko! Geko! Listen to my song! I won't move until it's over! I'm Gekomon of the volcano, the Endless Rocker, the Volcano Lord! The Volcano Lord lives in the volcano, and the Ice Lord lives on the iceberg. Together we're the Lords! Geko!",
    146: "Welcome to West Knuckle City's Farm Shop! Our selection has gotten incredibly good! Yeah! Love you! Bomber!",
    152: "Welcome to East Knuckle City's Farm Shop! Our selection has gotten incredibly good! Yeah! Want you! Bomber!",
    153: "Thanks for defeating the Shadow Guard! I fought as hard as I could, but I lost in the end. You had to save us again. I'm truly grateful!",
    154: "They called you to Stealth Valley? I've never heard of that place... Wait, only people with pure hearts can see it? Well, I guess that makes sense! ...No way!",
    155: "You found the entrance to the true ROG leader's hideout?! What, just the entrance to where the boss might be? Then you're almost there! Keep going. You can do it!",
    158: "Welcome to Twisted City's Farm Shop! Our selection has gotten incredibly good! Yeah! Need you! Bomber!",
    159: "Taiki, thanks for saving us again! We were attacked, stripped of everything, and driven out before we knew it. I thought I'd be a wandering Digimon again. Everyone will tell stories of your great deeds forever!",
    160: "You were called to Stealth Valley...? I heard that name when I was a wandering Digimon. Nobody can find it, and nobody should. They say Digimon who shouldn't be alive have been seen there.",
    161: "You made it back to Sky Fort? Are all your friends safe? That's wonderful! Congratulations!",
    164: "Welcome to Skull City's Farm Shop! Our selection has gotten incredibly good! Yeah! Rock you! Bomber!",
    165: "Thanks to you, we're safe again! For a while, I didn't know what would happen. You really saved our lives!",
    166: "Stealth Valley? I've never heard of that area! Since it's called Stealth Valley, I guess it's hidden!",
    167: "I heard you can finally return to Sky Fort. That's a relief. I'm so glad!",
    168: "Thank you, Taiki! All of you! The Shadow Guard appeared out of nowhere and took the tower before we knew it. We let our guard down after hearing ZeedMillenniummon had been defeated...",
    169: "You're going to Stealth Valley now, Taiki? Is it a secret place that nobody knows about? I didn't know there was a place like that in this zone...",
    170: "I heard you're going to fight ROG's real boss... You'll be okay, right? Of course you will! No one in this zone is stronger than you!",
    173: "Welcome to Web City's Farm Shop! Our selection has gotten incredibly good! Yeah! Hold you! Bomber!",
    174: "Thank you, Taiki! You took the tower back! We said we'd protect this place, but we have nothing to show for it... They overwhelmed us at once. We fought hard, but they were much stronger!",
    175: "You still can't return to Sky Fort? The electric field is still there, even though you reclaimed the tower? You'll find a way. I'm sure of it!",
    176: "You're back at Sky Fort, and your friends are safe? That's great! Wait, you still have to fight ROG's real boss? You can handle it! I'm sure of it!",
    177: "Th-thank you! The Shadow Guard showed up and drove us out... We couldn't beat them, so we had to run!",
    178: "There's a seventh Capacitor System in Stealth Valley? A mysterious person told you to go there? Taiki, I think you'll be fine, but be careful!",
    179: "The barrier is gone and you made it back to Sky Fort? Congratulations! You worked so hard!",
    182: "Welcome to Papyrus City's Farm Shop! Our selection has gotten incredibly good! Yeah! Got you! Bomber!",
    183: "Oh, it's you! Thanks for saving us. The enemy caught us off guard and seized the tower. We tried to take it back several times, but they used the Capacitor System to keep us away...",
    184: "Taiki?! A mysterious person called you there? Could it be a trap? Be careful!",
    185: "You made it back to Sky Fort, but ROG's real boss isn't there? That's bad... But the boss must be somewhere. Don't give up! You'll find them!",
    186: "Keep going, Taiki! Everyone's waiting. Turn off the electric field and get back to Sky Fort! The Patamon captured by Barbamon are in danger!",
    187: "They say switching the towers' Capacitor Systems from Emergency Mode back to Normal Mode will stop the electric field. But there are six towers, not just one or two, and ROG Digimon are sure to be waiting at each one...",
    188: "If you activate the Capacitor System in Stealth Valley, you'll be able to get into Sky Fort this time, right? I wonder who the Digimon in Stealth Valley are... They seem to know Spadamon, so they must be okay, right?",
    189: "Keep going, Taiki! Everyone's waiting. Turn off the electric field and get back to Sky Fort! The Patamon captured by Barbamon are in danger!",
    190: "They say switching the towers' Capacitor Systems from Emergency Mode back to Normal Mode will stop the electric field. But there are six towers, not just one or two, and ROG Digimon are sure to be waiting at each one...",
    191: "If you activate the Capacitor System in Stealth Valley, you'll be able to get into Sky Fort this time, right? I wonder who the Digimon in Stealth Valley are... They seem to know Spadamon, so they must be okay, right?",
    192: "Penmon's Item Shop shows up even in a place like this! I knew you'd need supplies, so I brought everything I had!",
    193: "You probably know this already, but here's a reminder. Press A by the Save Terminal to save. Press A by the bed to restore HP and MP. Use the left PC in the back for the DigiLab and the right PC for the DigiFarm!",
    194: "When you want to relive old memories, look up at the night sky and press A.",
    195: "A portal to the DigiColosseum has opened! I haven't heard that name in ages. Portals only appear in peaceful zones, so this is all thanks to you, Taiki!",
    196: "You're already Bronze Master? Didn't you only enter the tournament recently? You aren't supposed to win that easily... I guess you really are strong!",
    197: "Silver Master? Congratulations! You're moving up faster than I expected. Maybe you can reach Gold Master, too! If you make it all the way to Platinum, that'll be incredible!",
    198: "Gold Master already?! I knew you were strong, but I didn't know you were that amazing! Maybe you really can reach Platinum Master! You can do it, Taiki!",
    199: "Platinum Master?! That's incredible! Only a handful of people have reached that rank, right? Has anyone in the El Estow Zone done it before? Team Xros Heart really is amazing!",
}

ENTRY19 = {
    0: "What? Legend Master?! Taiki?! How? I thought the Legend Master was a legend! I heard that someone who saved the Digital World long ago was reborn as a Digimon and became Legend Master.",
    1: "Welcome! I'm Penmon, and this is the Sky Shop, the Item Shop at Sky Fort!",
    2: "Don't let your guard down just because the legendary ancient Weapon Digimon are gone, Taiki! Patamon seemed to be in a hurry earlier. I wonder what happened?",
    3: "Bronze Master? The DigiColosseum? That's the place through the new portal! Bronze Master... That sounds cool!",
    4: "Silver Master?! That's a rank above Bronze Master? There are higher ranks? Then the next one must be Gold Master!",
    5: "Gold Master?! Of course you did, Taiki! Does that mean you're number one in the Digital World? Wait, there's a Platinum Master above that?!",
    6: "Platinum Master?! Congratulations! Are you at the top of the Digital World now? Wait, there's still a Legend Master above you? How many ranks are there?!",
    7: "You did it, Taiki! I mean... Taiki the Legend Master! ...That title doesn't really suit you, does it?",
    8: "Our work has made this zone peaceful. But don't let that make you careless, Taiki Kudo! The Quest Monitor is full of SOS calls from across the zone!",
    9: "I heard you won at the DigiColosseum, Taiki Kudo! Bronze Master is the lowest rank, right? If that's enough for you, you're not worthy of being my eternal rival! Keep going! You can do it!",
    10: "You became Silver Master?! Great work, Taiki Kudo! Was your opponent really strong? Team Sunburst's Kou? Who's that? Never heard of him. Wait, the tournament is against heroes who saved the Digital World? Well, I guess you're one of them now!",
    11: "Gold Master? Congratulations! I didn't know before, but I think that means you're about the strongest in Japan! I know because I'm the best in Koto Ward! I think I know... I mean, I know I know! Really!",
    12: "Taiki is Platinum Master?! What does that even mean?! First you're the best in Japan, now you're the best in the world?! If my rival is number one in the world, then I'll aim to be number one in the universe!",
    13: "Legend Master? Legend? Taiki Kudo, isn't that a little unfair? If you're a legend, what am I supposed to aim for as your rival? ...",
    14: "I'm glad this zone is peaceful again! Great job, Taiki! You're amazing!",
    15: "You're Bronze Master now? You did it, Taiki! But Bronze doesn't suit you. You deserve a higher rank... like Tin Master?",
    16: "You're Silver Master now? Great job, Taiki! Keep it up and aim even higher! Show them what a General of Xros Heart can do!",
    17: "You're Gold Master now? That's amazing! Gold is a good fit for you. Maybe your rank is finally starting to match your strength! Next is Platinum, right? That should suit you, too!",
    18: "You're Platinum Master now? Wow... I can't believe it! Lots of people tried, but nobody could win. You're incredible, Taiki!",
    19: "Taiki, you're Legend Master now...? You're so amazing I don't know what to say...",
    20: "Welcome, Taiki! This is the Quest Monitor. You know that already, of course. Thanks for saving the El Estow Zone! Please keep helping us!",
    21: "Welcome back, Taiki! It feels like it's been a while. I heard you've been winning at the Colosseum! Bronze Master? That's a heavy-sounding title. Here's your lucky item for today: a quest! Grant a Digimon's wish and you'll feel lighter! How was that? I tried to sound like a teen horoscope.",
    22: "Hi, Taiki! How are you doing? I heard you've been working really hard. Silver Master? That sounds strong! I can tell you've gotten stronger, but don't push yourself too hard!",
    23: "Hi, Taiki! Welcome to my Quest Monitor... What? Yes, it's mine. Actually, I am the Quest Monitor! ...Forget I said that. Gold Master? Congratulations! That's a very celebratory-sounding rank!",
    24: "Good day, Taiki! Welcome to the Quest Monitor. You can grant Digimon's wishes by completing quests... though you already know that. Help them when you have time! How far have you gone in the Colosseum? Platinum Master? That's even above Gold! How far will you climb?",
    27: "You can change the name you've given a Digimon here.",
    28: "Hey, let's go to the DigiColosseum already! There are tons of super-strong opponents, right? I'm so excited!",
    29: "Bronze Master?! You did it, Taiki! Sounds like a heavy, important rank!",
    30: "Silver Master?! Great job, Taiki! You're shining! Sparkling like silver!",
    31: "Gold Master! That's amazing, Taiki! You're dazzling! I can barely look at you!",
    32: "Platinum Master! That's incredible! I knew you could do it, Taiki!",
}


def main() -> None:
    destination = ROOT / "translations/batch94.json"
    if destination.exists():
        raise FileExistsError(destination)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for entry, dialogue in ((18, ENTRY18), (19, ENTRY19)):
        for index, english in dialogue.items():
            key = f"MSG/MESPAK02.PAK:{entry:03d}:{index:05d}"
            if key not in records or key in existing:
                raise ValueError(f"Missing or already translated source: {key}")
            row = records[key]
            if category(row) != "Story and dialogue":
                raise ValueError(f"Unexpected translation category for {key}")
            sources = ["Original Japanese ROM"]
            official_names = {
                (18, 27): "https://digimon.net/reference_en/detail.php?directory_name=chibickmon",
                (18, 61): "https://world.digimoncard.com/cards/?category=522014&search=true",
                (18, 168): "https://world.digimoncard.com/cards/?category=522025&search=true",
            }
            if (entry, index) in official_names:
                sources.append(official_names[(entry, index)])
            blocks.append({
                "archive": row["archive"], "entry": row["entry"],
                "start": row["index"], "category": "Story and dialogue",
                "english": [english], "sources": sources,
                "review_note": "Zone NPC dialogue and tournament reactions. Digimon names follow established English names where supported; Pipimon's name is a phonetic rendering of this character's baby-talk name in the source.",
            })
    if len(blocks) != 97:
        raise ValueError(f"Expected 97 dialogue strings, got {len(blocks)}")
    destination.write_text(json.dumps({
        "description": "Translate Tower/Stealth Valley reactions and early DWM rank dialogue in MESPAK02 entries 18 and 19.",
        "blocks": blocks,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
