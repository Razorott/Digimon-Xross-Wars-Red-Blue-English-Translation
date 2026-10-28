"""Translate postgame town and DigiColosseum NPC reactions, part two."""
from __future__ import annotations
import json
from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths

TRANSLATIONS = {
91:"Xros Heart, saviors of Elestou Zone! Taiki, we're truly grateful to you!",
92:"Bronze Master? Wow, you did it! The DigiColosseum sounds amazing. I'd love to enter myself!",
93:"Silver Master already? You're good! The World Savior Battle is heating up! What? It's not called the Savior Battle? Don't sweat the details!",
94:"Gold Master? Wow! Then from now on, you're Gold Saviors! Want me to paint your faces gold?",
95:"Platinum Master?! Impressive... though I can't quite picture platinum. Maybe the rank needs an easier name. What name? Uh... don't ask me!",
96:"Legend Master? You made it all the way! I respect you from the bottom of my heart. Whatever anyone says, you're legendary saviors now!",
97:"You drove ROG away and brought peace back to the Zone, pino? Now you're entering the DWM Tournament at the DigiColosseum, pino? You're like a storybook superhero, pino!",
98:"Bronze Master? Wonderful, pino! Your team was called 'Crossed-up Hearts,' right? Just kidding! That's an Elestou joke, pino.",
99:"Silver Master? Congratulations, pino! Your opponents were just like you? That sounds both easier and harder. I bet they felt the same way, pino!",
100:"Gold Master? Amazing, pino! Your opponents were the exact opposite of you? That sounds both easier and harder. I bet they felt the same way, pino!",
101:"Platinum Master? That's impressive, pino! Your opponents were... Bandits?! I heard they'd vanished! Oh, they're safe? Not that I know them. I'm half relieved and half disappointed, pino.",
102:"Legend Master? Well... forgive me for saying this, pino, but was it really what you wanted? They call Legend Master the final job. You're still too young to retire!",
103:"Welcome to Penguinmon's Item Shop in Papyrus City! Come shop at the Papyrus Shop!",
105:"Welcome back to Papyrus City's Farm Shop! A good party starts with a good Farm. That's the basics, Bomber!",
106:"ROG is gone, and peace has returned to the Zone. You must have played a huge part in that. Well done once again! You have my heartfelt thanks!",
107:"Bronze Master? Of course I know what that is. Bronze goes 'bronnn,' then 'zzzz,' right? Anyway, keep up the good work!",
108:"Silver Master? Of course I know that! Heat it a little, take a bite... delicious! Anyway, keep up the good work!",
109:"G-Gold Master? I know it! That's when you go 'gooo' and then 'ld,' right? Anyway, keep up the good work!",
110:"Platinum Master? Of course I know it, without any doubt at all. But I'm busy right now, so we'll discuss it later!",
111:"Legend Master? Honestly, I don't understand these complicated things! You're the strongest team to win at the DigiColosseum? That's what it means? Then well done! You truly worked hard!",
114:"Welcome to Penguinmon's Item Shop at Earth Fort! We've got plenty of old items for sale!",
121:"I've heard of you. You traveled from another Zone to help a Weapon Digimon who had lost his memory, and he recovered. You have a gift for raising and training Digimon. Your team can win this tournament!",
122:"Bronze Master? Very impressive! I thought you could reach this rank from the start, though. The real challenge begins now. Stay focused!",
123:"Silver Master? Well done. But I'm not surprised. Most people who work hard can reach Silver. The real question is how far your own ability can take you. You'll find out soon enough!",
124:"Gold Master? Your strength is real. Effort or talent alone won't get you here. It takes luck, friends, tactics, and the right matchups too. So if you lose from here on, it won't be your fault alone.",
125:"Platinum Master? Now that does surprise me. Only someone who goes beyond the ordinary can reach Platinum. You've become that kind of person.",
126:"Ha ha ha! Foolish challenger! You'll learn how grueling the DWM Tournament can be! ...Sorry. I'm just a spectator. Someone should greet first-time visitors, and that sounded about right, didn't it?",
127:"I watched you become a Bronze Master. Great match! You still looked pretty relaxed. Better than panicking, of course, but don't let that confidence cost you the next battle.",
128:"Hey, Silver Master! I watched your match. This time you had to work a little to win, and that's just right. A hard-earned victory feels even sweeter!",
129:"You did it, Gold Master! I watched that match. Even you were in a tight spot for a moment. That's not a bad thing. If you win too easily for too long, you won't know how to handle a real setback.",
130:"Whoa, Platinum Master! I watched the whole thing. Seeing the Bandits get knocked around was moving! I mean, you did nothing wrong. I always root for the side that's about to lose. Come to think of it, I've never rooted for you once!",
131:"You're the new hero who saved the Digital World? Sorry, you don't look like one. Most heroes don't, I suppose. If you're entering the DWM Tournament, I'll cheer you on!",
132:"Bronze Master? Congratulations! Sorry, I promised to watch but missed it. You won before I got there! I'll definitely watch next time!",
133:"Silver Master! Congratulations! I watched this time. Your team looked so cool, but you won rather easily. A comeback from the brink would be more exciting! I'll cheer harder next time. What? I'm hoping you get in trouble? Of course not!",
134:"Gold Master! You looked so cool! I watched the whole thing. You were so strong it ended quickly again. I can barely remember the other team... Oh well!",
135:"Congratulations, Platinum Master! You were amazing. I knew you'd win! Your team really is strong. At this rate, you might reach the very top!",
136:"So you're a Legend Master now... Congratulations, but I won't see your team fight here again until you return as Battle Masters to face new challengers. I'll look forward to that day. Thanks for everything, Taiki the Legend Master!",
137:"Legend Master... I'm speechless. Are you retiring? This rank is like a certificate from the Digital World saying, 'There's nothing left for you to do here.' Congratulations, Taiki the Legend Master. And thank you for all your hard work!",
}

def main():
 dest=ROOT/'translations/batch101.json'
 if dest.exists():raise FileExistsError(dest)
 rec=collect_messages(Rom(rom_paths()['blue']));old=translate_records(rec);blocks=[]
 for index,english in sorted(TRANSLATIONS.items()):
  key=f'MSG/MESPAK02.PAK:019:{index:05d}'
  if key not in rec or key in old or category(rec[key])!='Story and dialogue':raise ValueError(key)
  blocks.append({'archive':'MSG/MESPAK02.PAK','entry':19,'start':index,'category':'Story and dialogue','english':[english],
                 'sources':['Original Japanese ROM','Existing reviewed project glossary'],
                 'review_note':'Postgame town and DigiColosseum NPC dialogue. Rank, area, character, and Digimon names follow the project glossary; 15-column story wrapping is build-validated.'})
 dest.write_text(json.dumps({'description':'Postgame NPC and tournament reactions, part two.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(dest),'slots':len(blocks)}))
if __name__=='__main__':main()
