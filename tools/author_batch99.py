"""Translate postgame rank reactions and town NPCs, part one."""
from __future__ import annotations

import json
from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths

TRANSLATIONS = {
25: "I heard you were amazing at the DigiColosseum. Legend Master? A living legend already?! Isn't that a bit early at your age? Anyway, well done! That's our Taiki! Someday, let's have a serious match, you and me!",
33: "Legend Master! Huh? What does that even mean? Are you a legend now? What are we going to do, Taiki?!",
34: "Taiki, Taiki! Going to the DigiColosseum? Pipimon wants to come too! Take me with you!",
35: "Bronze Master! Congratulations, Taiki! But keep going to the DigiColosseum. Pipimon wants to come too! Take me!",
36: "Silver Master! Congratulations, Taiki! But there's still more DigiColosseum to see. Pipimon wants to come too!",
37: "Gold Master! Congratulations, Taiki! Keep going to the DigiColosseum. Pipimon wants to come too!",
38: "Platinum Master! Congratulations, Taiki! There's just a little more DigiColosseum to go. Take Pipimon too!",
39: "Legend Master! Congratulations, Taiki! Your trips to the DigiColosseum are over now? No more outings there for Pipimon either?",
40: "You've already decided to go to the DigiColosseum, right? The opposing teams are waiting, and they're supposed to represent the whole Digital World. You've got to go, Taiki!",
41: "Bronze Master first! Let's get on to the next one. Why the surprised look? That was only a warm-up! I expected nothing less from Taiki. Xros Heart can do a lot more than this!",
42: "Silver Master at last! We're right behind you, so keep pushing!",
43: "Gold Master at last! Now we're getting close to the top of the tournament!",
44: "Platinum Master! You did it, Taiki! But... maybe we've done it now? Above Gold, the opposing team said the challengers aren't ordinary Digimon. Are they incredibly strong, or did they mean something else? Let's find out!",
45: "You're finally a Legend Master, Taiki! You're at the very top of the DWM Tournament! What do we do now? ...Nothing, I guess. Nothing left to do!",
46: "Welcome to Penguinmon's Item Shop in West Knuckle City! Twice the city, twice the shopping!",
48: "Welcome back to West Knuckle City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
49: "I hear you saved Elestou Zone from destruction. Taiki, thank you. Truly, thank you!",
50: "You became a Bronze Master? Excellent work! I don't really know how impressive it is. I've only heard rumors about the DigiColosseum and its tournaments. But I'll celebrate your great achievement all the same. Congratulations, Taiki!",
51: "You became a Silver Master? Congratulations! A battle among the Digital World's greatest... I can hardly imagine it.",
52: "You became a Gold Master? Splendid! Gold sounds like it must be the highest rank... Oh, Platinum is higher still? There's always someone above you, isn't there?",
53: "So you've become a Platinum Master, Taiki? Bronze, Silver, Gold, then Platinum... You must be afraid of nothing now. ...You were less afraid when you had nothing to lose? I suppose that may be true.",
54: "Legend Master? Taiki, you're a legend now. But to us, you've been one ever since you saved this Zone.",
55: "Welcome to Penguinmon's Item Shop in East Knuckle City! Come see our excellent goods!",
57: "Welcome back to East Knuckle City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
58: "Hey, it's the saviors of Elestou Zone! We could call you the EZ Saviors for short! ...It doesn't make sense? Yeah, I thought so too. Hey, EZ Saviors! ...Still not catching on?",
59: "Bronze Master! No surprise there. Where does that rank from the top? Fifth? Then the real contest is just beginning. Keep pushing!",
60: "Silver Master! I knew you could do it. Fourth from the top, right? You've still got a long way to go, but I'm sure you can make it!",
61: "Gold Master? Of course! You could make Gold or even Mithril. What's next, Chrondigizoid Master? That doesn't exist? Platinum Master? ...Sounds a little ordinary, doesn't it?",
62: "Platinum Master? I thought it was possible, but you're incredible! That's the second-highest rank in the Digital World, right? Only Legend remains. You're practically at the top already! You're so cool!",
63: "You became a Legend Master?! Congratulations, but... isn't that a rank for old fossils about to retire? It's hard to call a kid in a T-shirt and shorts a legend. Not that shorts have anything to do with strength!",
64: "Welcome to Penguinmon's Item Shop in Roundabout City! Round and round, come shop around!",
66: "Welcome back to Roundabout City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
67: "I heard about your fierce battle with ROG, kuwa. They said you became a star in Lost Space... but you look like a very soft and lively star to me, kuwa.",
68: "Bronze Master? Wonderful, kuwa! Speaking of bronze, I made a bronze statue to thank you. That's all? Well, yes, kuwa. I put it in front of Sky Fort, but it fell off. It's probably at the bottom of the sea by now, kuwa.",
69: "Silver Master? Congratulations, kuwa! You're getting close to the top. But stopping now would feel terrible. You've come this far, so aim for first place, kuwa!",
70: "Gold Master? Wonderful, kuwa! Now you're at the top and have no regrets. What? Two more ranks? Platinum and Legend? You still have a long way to go, kuwa.",
71: "Platinum Master? Congratulations, kuwa! Only Legend remains. But someone who saw a Legend match said, 'They're monsters!' That's a strange thing for a Digimon to say, kuwa.",
72: "Legend Master at last, kuwa! We've already decided what to do: now that you're a legend, we'll make another statue!",
73: "Welcome to Penguinmon's Item Shop in Skull City! Skull shop till you drop!",
75: "Welcome back to Skull City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
76: "So you really did save Elestou Zone! I'm amazed and grateful. You actually did it!",
77: "You're already a Bronze Master? I knew you were strong, but wow. Keep aiming higher!",
78: "You're a Silver Master now? There's still Gold above Silver, isn't there? The world is full of amazing people.",
79: "You're a Gold Master? Gold sounds like the top, but there are still Platinum and Legend ranks? It might be a long road ahead.",
80: "Platinum Master! I couldn't make it to the DigiColosseum, but I was cheering for you with all my might from here. Congratulations!",
81: "Legend Master... Somehow it doesn't quite fit you. I don't mean you're weak. I always thought a legend was something from the past. Your legend is still being written, isn't it?",
82: "You protected this Zone's peace? I knew you would be our saviors! Thank you, Taiki, and thank you, everyone!",
83: "Bronze Master? Congratulations! Bronze is actually my favorite Master rank. The higher ranks may be more polished, but nothing beats the challengers' energy at Bronze! And maybe I like the elderly champion too.",
84: "Silver Master? You're a veteran now. Many challengers reach Silver but never get higher. Some grow bored, others lose heart. Tournament watchers call them 'silver veterans.' It's a little sad, isn't it?",
85: "Gold Master? Then you'll be fine. Anyone who can reach Gold can reach Platinum and Legend too, if they put in enough time and effort.",
86: "Platinum Master? Congratulations! You're among the top three percent in the Digital World. Becoming a Legend Master is another matter, but you're already one of the strongest in this Zone.",
87: "Legend Master? Ha ha, congratulations! Do you know the DigiColosseum's old superstition? Half the teams granted Legend status split up soon after. But your team will be fine... right?",
88: "Welcome to Penguinmon's Item Shop in Kumonos City! Come browse the Kumonos Shop!",
90: "Welcome back to Kumonos City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
}


def main() -> None:
    dest = ROOT / "translations/batch99.json"
    if dest.exists(): raise FileExistsError(dest)
    records = collect_messages(Rom(rom_paths()["blue"]))
    existing = translate_records(records)
    blocks = []
    for index, english in sorted(TRANSLATIONS.items()):
        key = f"MSG/MESPAK02.PAK:019:{index:05d}"
        if key not in records or key in existing or category(records[key]) != "Story and dialogue":
            raise ValueError(f"Unusable source {key}")
        blocks.append({"archive":"MSG/MESPAK02.PAK", "entry":19, "start":index,
                       "category":"Story and dialogue", "english":[english],
                       "sources":["Original Japanese ROM", "Existing reviewed project glossary"],
                       "review_note":"Postgame NPC and tournament-rank dialogue. Game rank names, location names, and Digimon names follow the existing project glossary. Story text is wrapped to 15 columns by the build."})
    dest.write_text(json.dumps({"description":"Postgame town NPCs and tournament reactions, part one.","blocks":blocks}, ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(dest),"slots":len(blocks)}))

if __name__ == "__main__": main()
