"""Author the next reviewed main-story and battle-technique batch."""
from __future__ import annotations

import json
import textwrap

from xros_text import ROOT, Rom, rom_paths
from build import collect_messages, translate_records


# The prose follows the Japanese scene order. Story lines are wrapped at the
# game's observed 15-cell limit; technique descriptions use the 28-cell UI cap.
TEXTS = {
    (4, 158): "Whaaat?! I don't get it! Wait... are you calling me ugly?!",
    (4, 159): "Uh... That's not true, right, Shoutmon?",
    (4, 160): "Grr! That weird Minervamon... How dare she call the future King of the Digimon ugly?!",
    (4, 161): "No... You too?",
    (4, 162): "...Yeah. You too, huh?",
    (4, 164): "Spadamon, how are you? Did you remember anything?",
    (4, 165): "ROG is searching for the Legendary Ancient Weapons... Many armies and groups have come to this Zone looking for them, not just ROG. But before that, a legendary warrior protected this Zone with the legendary weapons... ...I can't remember any more.",
    (4, 166): "A warrior who wields the legendary weapons...?!",
    (4, 167): "So... the guardian of this Zone?",
    (4, 168): "I feel like I know the legendary weapons... They must be connected to my memories...",
    (4, 169): "Taiki, Cutemon is safe and unharmed. He's a little tired, though. Let's find somewhere to rest.",
    (4, 170): "All right. Let's return to the Sky Fortress for now.",
    (4, 171): "Dorulumon! You really bit me back there! It's swelling now! What am I supposed to do?!",
    (4, 172): "It wasn't poisonous. Stop making such a fuss...",
    (4, 173): "Just because you're handsome, you don't have to talk like that!",
    (4, 174): "Dorulumon is grateful, really, kyu! He's just too stubborn to say thanks!",
    (4, 175): "Yeah, I know.",
    (4, 176): "I'm glad Cutemon and the others made it back safely.",
    (4, 177): "Thanks so much! You saved us, kyu!♪",
    (4, 178): "Hey! Did you two work things out?",
    (4, 179): "...Hmph. For now. I'll fight alongside you from here on, Taiki. Talk to me anytime. Later.",
    (4, 180): "Let's activate the Capacitor Tower in Twisting Amazon.",
    (4, 181): "Yeah, let's do it.",
    (4, 182): "Leave the Sky Fortress to us!",
    (4, 183): "We've gotten pretty close to the Digimon here, too!",
    (4, 184): "I'm counting on you... Akari, Zenjiro.",
    (4, 185): "I caused trouble for Dorulumon... Even if he goes out again, I'll stay here with Akari and the others, kyu.",
    (4, 186): "Then let's head out!",
    (4, 187): "This is bad! We're in trouble!",
    (4, 188): "Those are ROG grunts! They're guarding the way, so we can't get through.",
    (4, 189): "Should we smash the gate and knock them out?",
    (4, 190): "Absolutely not! Then we'd have enemies everywhere! I don't want that!",
    (4, 191): "She's right... We can't let them spot us here. Let's find another way. Is there another route?",
    (4, 192): "Hmm... Should we head into the Digital Space up ahead?",
    (4, 193): "We can use the Pathfinder Device there.",
    (4, 194): "Path... what?",
    (4, 195): "It's a device hidden aboard our Sky Fortress. It links to special spaces that can't be reached normally, using a passage called a Path.",
    (4, 196): "Oh, now I get it! That's why it's called the Path-something Device!",
    (4, 197): "Did that explanation make sense to you?",
    (4, 198): "Not at all!",
    (4, 199): "...Anyway, go through that Warp Portal to reach Digital Space.",

    (5, 0): "Got it.",
    (5, 1): "Linkage: Path Connect!",
    (5, 2): "...Path Connect.",
    (5, 3): "Huh? Isn't that Nene over there? And the one beside her... SkullKnightmon?!",
    (5, 4): "SkullKnightmon?! He's our enemy! Why is he with Nene? Is he threatening her again by holding her little brother hostage? What's going on?!",
    (5, 5): "...Nene isn't that weak. She wouldn't obey SkullKnightmon again, especially when she's trying to save her brother.",
    (5, 6): "T-Taiki! That device the girl is holding... It's a Pathfinder Device, only found on the Sky Fortress! How did she get one?!",
    (5, 7): "Destination: Lost Space.",
    (5, 8): "...Input: Lost Space. Search for the seal that holds the Legendary Ancient Weapons...",
    (5, 9): "The Legendary Ancient Weapons and Lost Space...? No, stop her, Taiki! ROG is desperately searching for Lost Space. It must be where the weapons are hidden!",
    (5, 10): "What?! Is ROG controlling Nene?!",
    (5, 11): "Nene! Wake up!",
    (5, 12): "ELIMINATE ALL WHO INTERFERE WITH THE PLAN.",
    (5, 13): "...Eliminate them all.",
    (5, 14): "G... glitch... Not... over... Connect... to Lost Space...",
    (5, 15): "...Link: Lost Space.",
    (5, 17): "We... ROG... will take everything... Legendary weapons... Legendary Digimon...",
    (5, 18): "Is that really SkullKnightmon? Taiki, something's wrong! This feels dangerous!",
    (5, 20): "Legendary weapons... Legendary Digimon... I almost remember... But ROG must not enter Lost Space!",
    (5, 22): "...Connection refused. Energy explosion in 5... 4... 3...",
    (5, 33): "What happened after that? What happened when it exploded? Where's Nene?!",
    (5, 34): "...I don't know. But I don't think she made it into Lost Space.",
    (5, 43): "Is this the terrifying Digimon? I feel like I've seen it before...",
    (5, 44): "I saw someone like him in another Zone! A giant penguin froze him solid!",
    (5, 45): "What?! Frozen solid? No way! I wouldn't last a second!",
    (5, 46): "Spadamon is such a pampered brat. Why would ROG want someone like him...?",
    (5, 47): "They say he knows the secret of the legendary weapons, debi.",
    (5, 48): "They say he can activate towers that even we couldn't, debi.",
    (5, 49): "Hmm... I see. So he has some use to us.",
    (5, 50): "Hey, IceDevimon! Where's Sparrowmon?!",
    (5, 51): "Sparrowmon? You mean... the one with the long legs? The slender one? Ha-ha! I know where that Sparrow-something is! Trade me the Spadamon beside you, and I'll tell you!",
    (5, 52): "IceDevimon, that lie makes no sense. Sparrowmon doesn't have legs!",
    (5, 53): "W-What?! He doesn't?! Then I'll take Spadamon by force! Hand him over!",
    (5, 54): "Here they come, everyone!",
    (5, 55): "Grr... S-So strong... How can a mere kid be this powerful...?",
    (5, 56): "I'm not just a kid! Taiki is the General of Xros Heart! We won't forgive a rotten crew like ROG!",
    (5, 57): "A team? ROG is no team... Soon you'll understand what makes ROG truly terrifying.",
    (5, 59): "I remember, Taiki! The legendary weapons need a warrior who can wield them. That warrior receives the weapons and the Capacitor Towers. So the warrior is their keeper.",
    (5, 60): "Then is Spadamon the warrior, since he can open the towers?",
    (5, 61): "...No, I don't think so. I can't open every door whenever I want. The legendary warrior must still be somewhere out there!",
    (5, 62): "The legendary warrior and Spadamon... I feel there's a deep connection between them.",
    (5, 63): "If that warrior is tampering with the towers, why aren't they helping while Elestou Zone is in danger?",
    (5, 64): "There are still too many mysteries...",
    (5, 65): "Key item obtained! Kumonos Ruins West Key",
    (5, 66): "It looks like the gate key for western Kumonos Ruins. Remember where the explosion in Digital Space sent us? The West Gate to Kumonos Ruins is right near there.",
    (5, 67): "Could Sparrowmon be held there?!",
    (5, 68): "Yeah, I think so. We have to hurry and save him... Kumonos Ruins, huh? All right! Let's go, you two!",
    (5, 69): "...Nene? What are you doing here alone?",
    (5, 70): "Taiki, be careful... Remember? Nene is being controlled by ROG.",
    (5, 71): "But she seems strange... Like she's in a daze.",
    (5, 72): "Nene... Can you hear me?",
    (5, 73): "...A voice... calling me.",
    (5, 74): "Whose voice?",
    (5, 75): "Sparrowmon... He's trapped in the darkness. While I searched for him after we were separated... the power of darkness in this world swallowed me, too...",
    (5, 76): "Nene, wait! If you're looking for Sparrowmon, come with us...",
    (5, 77): "...Sparrowmon... He's suffering nearby... I have to go... I have to save him...",
    (5, 78): "Sparrowmon's voice...? I heard it, too! Nene must have heard the same thing.",
    (5, 79): "She said Sparrowmon is close. How does she know that...?",
    (5, 80): "...I don't know. But he's nearby. I can feel it, too!",
    (5, 81): "Nene was searching for him and got trapped in the darkness? Who could have done that...?",
    (5, 82): "I'm worried about Nene, but first we have to find Sparrowmon!",
    (5, 83): "Hee-hee... I've been waiting for you, Spadamon.",
    (5, 84): "I'm Arukenimon, ROG's Poison Leader, Arukenimon the Predator! I knew you'd come, Spadamon. Your goal is right here, isn't it?",
    (5, 85): "Ah! Sparrowmon!",
    (5, 86): "Sparrowmon! Thank goodness, you're safe!",
    (5, 87): "Such innocent joy... How cute. But I'll wipe that lovely smile away in a moment. Hee-hee!",
    (5, 88): "Sparrowmon... He doesn't recognize us!",
    (5, 89): "No, Taiki! He's completely under her control!",
    (5, 90): "Hee-hee! Luring you here was easy. Your friend is under a powerful illusion cast by Lord ZeedMillenniummon.",
    (5, 91): "This boy was a special gift from Lord ZeedMillenniummon. I used him as bait to lure Spadamon here.",
    (5, 92): "His master now is the leader I admire... Lord ZeedMillenniummon, who stands at the top of ROG!",
    (5, 93): "T-Taiki...!",
    (5, 94): "It's all right, Spadamon. Sparrowmon, can you hear us? Remember us! You're too strong to be fooled by a trick like this. You have the strongest will and heart of anyone!",
    (5, 95): "It's no use! Hand over Spadamon! Lord ZeedMillenniummon's dream is to rule the world with the Legendary Ancient Weapons... and I'll make it come true!",
    (5, 96): "Tell that ZeedMillenniummon this! We're Team Xros Heart, bound by a hotter bond than anyone! None of us will fall for a cheap trick like this!",
    (5, 97): "Hee-hee-hee! You naive fools... Now suffer the pain of being attacked by your trusted friend!",
    (5, 98): "No... I lost?! Sparrowmon... You brats... I will never forgive you!",
    (5, 100): "...Dynasmon.",
    (5, 101): "What's wrong, Spadamon? Did you remember something?",
    (5, 102): "The keeper of the Capacitor Towers... the legendary warrior... I think it was Dynasmon. I only remembered the name. Dynasmon...? Why do I feel like a strict teacher just scolded me?!",
    (5, 103): "Did Dynasmon used to scold you?",
    (5, 104): "U... Everyone...?",
    (5, 105): "Hey, Sparrowmon! Hang in there!",
    (5, 106): "Sparrowmon!",
    (5, 107): "Huh...? Taiki and Shoutmon... My head feels fuzzy... Why am I here? I was in the jungle, then I heard a strange voice... Oh, right! You went ahead without me! Don't do that again! I'm a member of Xros Heart now, too!",
    (5, 108): "W-What? Did I say something weird?",
    (5, 109): "No... We're glad! Sparrowmon, you're one of us!",
    (5, 110): "Huh? Why are you saying that all of a sudden? You're embarrassing me...",
    (5, 111): "I'm so glaaad, Sparrowmon! I'm happy too!",
    (5, 112): "Even Shoutmon's crying... Why? If it's about what happened in the jungle, don't worry about it!",
    (5, 113): "You really don't remember... Anyway, get some rest. Akari, Zenjiro, and everyone else are at the Sky Fortress. You'll be safe there.",
    (5, 114): "Use this Gate Disk and you'll be there in a flash! Wait for us in the Central Room.",
    (5, 115): "Um... I still don't understand what's going on, but... you're really happy I'm with you, huh? Hee-hee. I'm glad I joined Xros Heart! See you later!",
    (5, 116): "Sparrowmon really knows how to make you cry... Let's activate the Capacitor Tower!",
    (5, 117): "Taiki! Take this...",
    (5, 118): "Key item obtained! Kumonos Ruins East Key",
    (5, 119): "This key opens the gate to Papyrus Desert. There should be a Capacitor Tower there, too.",
    (5, 120): "We have to activate every tower. All right, let's head to the desert next.",
    (5, 121): "Then let's go!",
    (5, 122): "Woooooah...!",
    (5, 123): "You have chosen my coffin! I am Pharaohmon, ROG's Shining Leader, Pharaohmon the Grave!",
    (5, 124): "Spadamon, this guy looks kind of fun!",
    (5, 125): "What?! He's a ROG leader! He'll definitely demand Spadamon or try to take him!",
    (5, 126): "You foolish Spadamon! ROG has no use for you! Those who defy ROG will suffer calamity! No matter what Lord ZeedMillenniummon says, I shall bring great calamity upon you!",
    (5, 127): "Here he comes... Taiki!",
    (5, 128): "Taste my calamity!",
    (5, 129): "Ugh... Why am I the one beaten to a pulp? It seems the calamity fell on me instead...",
    (5, 130): "Um... Well...",
    (5, 131): "Silence! That battle didn't count! We'll start over from the beginning!",
    (5, 132): "What did you say?",
    (5, 133): "First, I'll remove one blocking rock! You can't go on until it's gone! If you want to fight me, find me again! Ha-ha-ha...!",
    (5, 134): "What was that?! An earthquake?",
    (5, 135): "No... I can feel a spot nearby that's shaking...",
    (5, 136): "...I remember. Pharaohmon built these desert ruins. He's a fearsome Ruins Digimon who can make rocks appear beneath the ground.",
    (5, 137): "What?! So we can't get past the rocks blocking the path unless we beat him?! What are we going to do?!",
    (5, 138): "Calm down, Shoutmon. Panicking won't help.",
    (5, 139): "That blocking rock Pharaohmon mentioned... Maybe it was the stone tablet in the ruins that blocked the road? It disappeared, and now a path has opened somewhere.",
    (5, 140): "So we just find and beat Pharaohmon again? But I wonder what he meant by removing only one rock at a time...",
    (5, 141): "There are so many identical coffins around here... Don't open the wrong one! If a real ghost appears, I-I'll faint!",
    (5, 142): "There doesn't seem to be a way to tell them apart... But if we can beat Pharaohmon, we'll be fine! Let's go!",
    (5, 143): "You grave robbers woke us from our sleep! Instead of treasure, I'll give you a curse!",
    (5, 144): "Huh? Grave robbers...?",
    (5, 145): "Suffer and learn how foolish you were!",
    (5, 146): "Wait... Hold on!",
    (5, 147): "You won't get away from me!",
    (5, 148): "...Huh? You're not grave robbers? How confusing! If that's true, wear name tags!",
    (5, 149): "...Whaaaat?",
    (5, 150): "Goooood morning, boy...! You will face my wrath... and that means you!",
    (5, 151): "...Which one is 'me'? Do you mean yourself? Or is that your cry?",
    (5, 152): "What are you babbling about?! The one who loses this fight will be... not me, but you!",
    (5, 153): "...There you go again. Which one?",
    (5, 154): "Enough! Stop babbling!",
    (5, 155): "Don't think you beat me! You'll regret this!",
    (5, 156): "What a weirdo...!",
    (5, 157): "Fwahahahaha...!",
    (5, 158): "You have chosen my coffin! I am Pharaohmon, ROG's Shining Leader, Pharaohmon the Grave!",
    (5, 159): "...Didn't you just say that?",
    (5, 160): "Quiet! I don't care if it inconveniences you! Great calamity will befall you!",
    (5, 161): "Looks like we have to fight!",
    (5, 162): "How insolent! I'll crush you!",
    (5, 163): "...You pesky brat... Such tricky tricks... Bringing my calamity right before me...",
    (5, 164): "That sounds like a tongue twister!",
    (5, 165): "No! Listen to me! Losing to the likes of you is completely unacceptable! It's so unfair!",
    (5, 166): "Whaaat?!",
    (5, 167): "He's hiding again!",
    (5, 168): "Quiet! If you want me to give up, find my coffin again! Ha-ha-ha...!",
    (5, 169): "That sound and shaking... Another rock moved! A path must have opened somewhere!",
    (5, 170): "All right, Spadamon! On to the next one!",
    (5, 171): "Spadamon! Let's open the next coffin!",
    (5, 172): "This is starting to feel like a treasure hunt... First we have to find Pharaohmon again!",
    (5, 173): "You're grave robbers, aren't you? No need to answer. From every angle, you look exactly like grave robbers!",
    (5, 174): "W-Wait, no! That's not true!",
    (5, 175): "Don't imitate me!",
    (5, 176): "Actually, fine, you're grave robbers! Look at those faces. You couldn't look more like grave robbers!",
    (5, 177): "Huh? Do I really look that scary?",
    (5, 178): "At last, our archenemy! We've waited for this day! Only a few survive after making enemies of us Mummymons!",
    (5, 179): "O-Oh... Only a few? And you just came right out and said so...",
    (5, 180): "We have no pride that needs a dirty lie to defend it! You'll soon learn the honor of the Mummymon!",
    (5, 181): "Only a tiny fraction of the countless Mummymons happened to lose this time! You'll learn how terrifying we are!",
    (5, 182): "I think we've already learned that...",
    (5, 183): "Fwahahahaha!",
    (5, 184): "You have chosen my coffin!",
    (5, 185): "Yes! We found Pharaohmon! We got him!",
    (5, 186): "...You brats! You're that happy to fight me...? A Digimon of my stature has so many admirers... Hah... Ha-ha-ha...!",
    (5, 187): "It's kind of hard to fight him when he's this happy to see us...",
    (5, 188): "Pharaohmon's kind of hard to dislike...",
    (5, 189): "Hey! Don't just stand there!",
    (5, 190): "Ha-ha-ha... I have no choice now! Since you found me, I'll fight you! I'll show you how terrifying my calamity is!",
    (5, 191): "Ha-ha-ha... Don't relax just yet! I've completely gauged your strength!",
    (5, 192): "Yeah... Maybe we can stop now?",
    (5, 193): "I'm tired... And I'm getting hungry...",
    (5, 194): "H-Ha-ha... Keep acting confident while you can! Soon I will gain tremendous power! Then, at last, a great calamity will surely befall you!",
    (5, 195): "Maybe Pharaohmon can't back down now...",
    (5, 196): "Oh no! Don't let Pharaohmon hear you, Taiki!",
    (5, 197): "You will bow before my reborn form! Fwahahahaha!",
    (5, 198): "Come on! He got away because you were taking your time!",
    (5, 199): "Don't be so mad. Sorry, Spadamon. We'll definitely catch him next time. Right, Taiki?",
}

MOVES = {
    0: "Launch a fireball that erupts into a pillar of magma.",
    1: "Slash the enemy with sharp claws charged with fire.",
    2: "Slash the enemy with mighty claws charged with fire.",
    3: "Slash the enemy with mighty claws filled with fire.",
    4: "Rain down a meteor shower and burn away nearby enemies.",
    5: "Throw a small bomb and blast the enemy.",
    6: "Throw a powerful bomb and blast the enemy.",
    7: "Engulf the enemy in flames with a powerful missile.",
    8: "Use powerful missiles to burn all nearby enemies.",
    9: "Slash nearby enemies with a blade of light.",
    10: "Slash the enemy with a blade of holy light.",
    11: "Strike with an electric-charged holy sword. Greatly raises the Melody Capture rate.",
    12: "Fire a small orb filled with holy power.",
    13: "Fire a beam of light that judges all.",
    14: "Blast nearby enemies with starlight energy. Also lowers Intelligence.",
    15: "Gather starlight and blast nearby enemies. Also deals Light damage.",
    16: "Fire two volleys of cross-shaped light orbs. Also deals Light damage.",
    17: "Slash the enemy with light and deliver holy judgment.",
    18: "Slash all nearby enemies with the power of light.",
    19: "Strike the enemy with both arms charged with light.",
    20: "Smash the enemy with a shining fist of holy light.",
    21: "Smash the enemy with a bolt of darkness.",
    22: "Crush the enemy with a small black hole. May cause Blindness.",
    23: "Slash with the Pendulum Blade on both arms. Greatly raises the Melody Capture rate.",
    24: "Smash the enemy with a blazing, spiked iron ball.",
    25: "Shatter the enemy with a soul-filled kick. Also lowers Speed.",
    26: "Smash the enemy with a kick filled with the light of justice.",
    27: "Blast nearby enemies with a compressed ball of electricity.",
    28: "Unleash an explosion of fire. Raises one ally's Attack.",
    29: "Gather particles of light. Raises one ally's Defense and Speed.",
    30: "Absorb the power of time's endless flow. Raises one ally's Attack and Intelligence.",
    31: "Fire a tiny metal ball at high speed. Also lowers Speed.",
    32: "Strike the enemy with a red whip that subdues prey. Drains HP.",
    33: "Fire a high-voltage ball of energy. May cause Blindness.",
}


OFFICIAL_NAMES = {
    "アルケニモン": "https://world.digimoncard.com/cards/?card_no=EX10-047&search=true",
    "ＺＤミレニアモン": "https://world.digimoncard.com/cards/?card_no=BT19-101&search=true",
    "スカルナイトモン": "https://world.digimoncard.com/cards/?card_no=EX10-026&search=true",
    "スパロウモン": "https://world.digimoncard.com/cards/?category=522027&search=true",
    "デュナスモン": "https://world.digimoncard.com/cardlist/?card_no=BT6-044&search=true",
    "ファラオモン": "https://world.digimoncard.com/rule/?card_no=BT16-078",
    "マミーモン": "https://world.digimoncard.com/cards/?card_no=EX10-051&search=true",
    "プクモン": "https://world.digimoncard.com/cards/?card_no=P-171&search=true",
}


def wrap(text: str, width: int) -> str:
    # Keep this long canonical species name on a natural line boundary rather
    # than letting the renderer split it in the middle of a syllable.
    text = text.replace("ZeedMillenniummon", "Zeed\nMillenniummon")
    return "\n".join(
        "\n".join(textwrap.wrap(line, width=width, break_long_words=True,
                                break_on_hyphens=False)) if line else ""
        for line in text.split("\n")
    )


def main() -> None:
    if (ROOT / "translations/batch59.json").exists():
        raise FileExistsError(ROOT / "translations/batch59.json")
    records = collect_messages(Rom(rom_paths()["blue"]))
    done = translate_records(records)
    blocks, review = [], []
    for (entry, index), raw in TEXTS.items():
        key = f"MSG/MESPAK02.PAK:{entry:03d}:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing Japanese story source: {key}")
        english = wrap(raw, 15)
        sources = ["Original Japanese ROM (local primary source)"]
        sources.extend(url for jp, url in OFFICIAL_NAMES.items() if jp in row["source"])
        blocks.append({"archive": row["archive"], "entry": entry, "start": index,
                       "category": "Story and dialogue", "english": [english],
                       "sources": sources,
                       "review_note": "Japanese dialogue is primary. Western Digimon spellings are linked to official English Bandai card references where available; Lost Space and other game-only terms follow established project usage."})
        review.append({"id": key, "japanese": row["source"], "english": english,
                       "sources": sources})
    for index, raw in MOVES.items():
        key = f"MSG/MESPAK04.PAK:004:{index:05d}"
        if key in done:
            raise ValueError(f"Already translated: {key}")
        row = records.get(key)
        if not row or not row["source"].strip():
            raise ValueError(f"Missing Japanese move description: {key}")
        english = wrap(raw, 26)
        sources = ["Original Japanese ROM (local primary source)"]
        blocks.append({"archive": row["archive"], "entry": 4, "start": index,
                       "category": "Move and item descriptions", "english": [english],
                       "sources": sources,
                       "review_note": "Battle-technique effect text translated from the Japanese description. Stats and Melody Capture terminology match the English battle UI."})
        review.append({"id": key, "japanese": row["source"], "english": english,
                       "sources": sources})
    expected = len(TEXTS) + len(MOVES)
    if len(blocks) != expected:
        raise AssertionError(f"Expected {expected} new slots; authored {len(blocks)}")
    out = ROOT / "translations/batch59.json"
    out.write_text(json.dumps({"description": "Continue the Chibickmon aftermath, rescue Sparrowmon, begin the Pharaohmon ruins, and translate battle-technique effects.", "blocks": blocks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_json = {"batch": 59, "translated_slots": len(blocks), "story_slots": len(TEXTS),
                   "move_description_slots": len(MOVES), "groups": review}
    (ROOT / "translations/review_batch59.json").write_text(json.dumps(review_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Batch 59 review", "",
             "This batch continues the main story from Cutemon's rescue, through Nene and Sparrowmon's reunion, and into the Papyrus Desert's Pharaohmon encounter. It also translates 34 battle-technique effect descriptions. The Japanese ROM is the primary source. Canonical species spellings use linked Bandai English card references where available; place and device names retain established game terms.", "",
             "Official name references: [Arukenimon](https://world.digimoncard.com/cards/?card_no=EX10-047&search=true), [ZeedMillenniummon](https://world.digimoncard.com/cards/?card_no=BT19-101&search=true), [SkullKnightmon](https://world.digimoncard.com/cards/?card_no=EX10-026&search=true), [Sparrowmon](https://world.digimoncard.com/cards/?category=522027&search=true), [Dynasmon](https://world.digimoncard.com/cardlist/?card_no=BT6-044&search=true), [Pharaohmon](https://world.digimoncard.com/rule/?card_no=BT16-078), [Mummymon](https://world.digimoncard.com/cards/?card_no=EX10-051&search=true), and [Pukumon](https://world.digimoncard.com/cards/?card_no=P-171&search=true).", "",
             "| ID | Japanese | English |", "|---|---|---|"]
    for item in review:
        jp = item["japanese"].replace("<0A>", "<br>").replace("|", "\\|")
        en = item["english"].replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| `{item['id']}` | {jp} | {en} |")
    (ROOT / "translations/review_batch59.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"batch": 59, "story_slots": len(TEXTS),
                      "move_description_slots": len(MOVES),
                      "translated_slots": len(blocks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
