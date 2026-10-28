"""Translate remaining tournament NPCs and optional mission dialogue."""
from __future__ import annotations
import json
from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths

TRANSLATIONS = {
138:"Congratulations, Legend Master! Your team's battles were a joy to watch. You have a real talent, and I don't just mean commanding Digimon. Your matches are exciting. It's a shame you can't enter the tournament again. Thanks for everything!",
139:"First time in the DWM Tournament? I don't know who you are, but you'll be fine! Don't worry about what comes next. Jump in with both feet!",
140:"You won that easily? Bronze Master already... Not that I'm jealous!",
141:"Silver Master already? You keep winning, but the DWM Tournament isn't supposed to be this easy! ...It isn't, right? I thought so...",
142:"Gold Master? I can't even call it luck or cheating. You may not know this, but the team you just beat once saved the Digital World. Then again, you did too, didn't you?",
143:"Platinum Master already? You face everything head-on with those bright eyes, and you keep winning. Watching you makes me want to try living more positively, and I hate that. I don't like regretting what I should've done. It's not your fault. I'm angry at myself.",
144:"Legend Master? A legend, already? No way! That's a rank for someone with one foot in the grave. You're practically newborn! Why am I getting so worked up?",
145:"Haven't seen you before. First time at the DigiColosseum? Who are you a fan of? I'm a huge Sayo fan, a 'Sayoer'! Hard to say? Too forced? Say what you like about me, but don't insult Sayo!",
146:"You're the new challenger? Even I, a veteran tournament watcher, was fooled by your innocent face. And you're already a Bronze Master! You don't look strong or clever, but maybe your kind grows fast. As a dedicated Sayoer, I'll be watching you!",
147:"Silver Master already? That was a fine fight, but now you might face Sayo. As a devoted Sayoer, I don't mind whether you win or lose. Just don't tarnish your match against her!",
148:"Gold Master? Congratulations. I never thought you'd beat Sayo so easily. I admit it was a good match, even as a devoted Sayoer!",
149:"Congratulations, Platinum Master! Why do you look surprised? Yes, I'm a Sayoer, but I'm a tournament watcher first. I can praise a good battle wherever I see one!",
150:"Legend Master? Congratulations from a devoted Sayoer! What's that got to do with it? Never mind. Well done, Sayo! ...Sorry, I meant Taiki. My mouth said Sayo on its own!",
151:"Welcome to the DigiColosseum, Taiki! I am Justimon, Digimon of justice! Now I'm also a tournament watcher of justice! Ha ha ha!",
152:"Bronze Master, Taiki! I knew you could do it. As a Digimon of justice, I always cheer for the side of justice! What if both sides are just? Well... the shinier side, perhaps?",
153:"Silver Master, Taiki! Silver is the color of justice. My body is mostly silver too. Did you want to know my name? Of course you did! Justimon, the silver Digimon of justice! Ha ha ha!",
154:"Gold Master, Taiki! I knew you'd succeed! I've watched many tournaments, and Xros Heart stands out. Perhaps your team is the greatest since the Digital World began... No, too soon to say. But everyone here has high hopes for you!",
155:"Platinum Master, Taiki! Your skill really is astonishing. You may go all the way! A new power awakens! I once entered the DigiColosseum myself, you know. The result was astonishing too... for a very different reason! Ha ha ha!",
156:"Legend Master at last, Taiki! Congratulations! That's the final rank here, but your battles are far from over. This is your first step toward greatness. Keep protecting peace and happiness across the Digital World! The fight for justice goes on! Ha ha ha!",
157:"Oh, the hero of Elestou Zone! We've met before. Don't you remember? I never thought you'd enter the DWM Tournament. I knew you were special! Of course I'll cheer for you! Good luck!",
158:"Bronze Master! You're 'The Bronze Master' from now on! Why so glum? Then how about 'Rank Number Five'? Why are you staring into the distance?",
159:"Silver Master! Now I can call you 'The Silver Master'! No? You don't like 'The'? How about 'La Silver Master'? Or 'Silver Sweetheart Master'? Still wrong? You're surprisingly picky!",
160:"Gold Master! You looked wonderful, Taichi the Gold Master! ...Why the long face? Gold sounds great! Oh, I got your name wrong? It's Taiki? I'm so sorry!",
161:"Taiki, you did it! Let me call you by your new title: Taiki the Platinium Master! ...Oh no! I stumbled over the most important word. May I try again? No? You want me to leave you alone? Sorry...",
162:"You're a Legend Master already? I cheered for you from the start, but it feels like a short dream. Taiki Kudo, let me speak for everyone in Elestou Zone: congratulations, Legend Master, and thank you for everything!",
163:"Find the Digimon Air Corps! Their leader, Phoenixmon, is in Canyon Yard. If you get lost, check Quest Info under Info on your Xros Loader. Good luck!",
164:"Find Phoenixmon, leader of the Digimon Air Corps, in Canyon Yard!",
166:"Use the Sky Passport I gave you, and Phoenixmon will carry you between airports. You can only visit airports whose gates you've opened. Use the keys in your Treasure list! First, talk to Phoenixmon at the Sky Port beyond the Commander Room. Thank you!",
167:"You want to reassemble the Digimon Air Corps? You have no idea how difficult that is. The system needs 99 Phoenixmon. It only looks like I'm doing it alone! Why? No reason at all! Time to contact the other 98. Tell Biyomon, 'Leave it to me!'",
169:"Find the Digimon Air Corps! Their leader, Parrotmon, is in Grass Yard. If you get lost, check Quest Info under Info on your Xros Loader. Good luck!",
170:"Find Parrotmon, leader of the Digimon Air Corps, in Grass Yard!",
172:"Use the Sky Passport I gave you, and Parrotmon will carry you between airports. You can only visit airports whose gates you've opened. Use the keys in your Treasure list! First, talk to Parrotmon at the Sky Port beyond the Commander Room. Thank you!",
173:"You want to reassemble the Digimon Air Corps? You have no idea how difficult that is. The system needs 99 Parrotmon. It only looks like I'm doing it alone! Why? No reason at all! Time to contact the other 98. Tell Biyomon, 'Leave it to me!'",
175:"Just once, I want to shed this spiky body and become smooth! Zudomon solved his problem with a super shaver. Please borrow it from him!",
176:"Please borrow the Super Shaver from Zudomon at West Knuckle Coast!",
177:"Th-thank you! Take your reward. I really appreciate it, but... did Zudomon say anything about this shaver? I don't have to return it? ...I thought so.",
181:"Just once, I want to shed this spiky body and become smooth! Drimogemon used a great shaver. Please borrow it for me!",
182:"Please borrow the Miracle Shaver from Drimogemon at West Knuckle Coast!",
183:"Th-thank you! Take your reward. I really appreciate it, but... did Drimogemon say anything about this shaver? I don't have to return it? ...I thought so.",
187:"Yesterday, my Giromon Gang declared all-out war on our eternal rivals, the Mamemon Gang! We haven't decided what to do next, though. We can work that out later...",
188:"First, ask my gang members Nanomon L and TD Ballmon where the Mamemon Gang is hiding!",
189:"Thanks, Taiki! The Mamemon Gang is finished! But before that, my own gang dissolved. Our personalities didn't get along. Here's our first and final reward!",
190:"The Giromon Gang has disbanded! Thanks for your service!",
191:"Mametyramon of the Mamemon Gang is my eternal rival. I should've been the one to declare war on them, obviously!",
192:"Where's the Mamemon Gang? I wish I knew! They might be near TD Ballmon. Somehow he always ends up where they do.",
193:"MetalMamemon of the Mamemon Gang is my eternal rival. Giromon likes to boast that he declared war, but it was my idea!",
194:"Where are they? I don't know, but probably somewhere nearby. They always show up in the same places I do.",
195:"You're a spy for the Giromon Gang! No more talking. Fight me!",
196:"I give up! We used to act tough as the Mamemon Gang, but we disbanded ages ago.",
197:"Tell Giromon we won't play with them anymore. I'm going to behave from now on.",
198:"Yesterday, my Mamemon Gang declared all-out war on our eternal rivals, the Giromon Gang! We haven't decided what to do next, though. We can work that out later...",
199:"First, ask Mametyramon and MetalMamemon where the Giromon Gang is hiding!",
}

def main():
 dest=ROOT/'translations/batch102.json'
 if dest.exists():raise FileExistsError(dest)
 rec=collect_messages(Rom(rom_paths()['blue']));old=translate_records(rec);blocks=[]
 for index,english in sorted(TRANSLATIONS.items()):
  key=f'MSG/MESPAK02.PAK:019:{index:05d}'
  if key not in rec or key in old or category(rec[key])!='Story and dialogue':raise ValueError(key)
  sources=['Original Japanese ROM','Existing reviewed project glossary']
  if 'Mametyramon' in english:sources.append('https://digimon.net/reference_en/detail.php?directory_name=mametyramon')
  blocks.append({'archive':'MSG/MESPAK02.PAK','entry':19,'start':index,'category':'Story and dialogue','english':[english],
                 'sources':sources,'review_note':'DigiColosseum spectator and mission dialogue. The Blue and Red flight leaders and destination variants are kept distinct; character, Digimon, and location names follow reviewed project terminology.'})
 dest.write_text(json.dumps({'description':'DigiColosseum NPCs and optional quests, part three.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(dest),'slots':len(blocks)}))
if __name__=='__main__':main()
