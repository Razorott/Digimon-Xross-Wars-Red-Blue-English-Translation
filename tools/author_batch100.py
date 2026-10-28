"""Translate remaining Farm notices and late optional-story dialogue."""
from __future__ import annotations
import json
from build import collect_messages, translate_records
from translation_queue import category
from xros_text import ROOT, Rom, rom_paths

TRANSLATIONS = {
43:"Training was a huge success! ^5 increased! ^6 to ^7",
44:"Training succeeded! ^5 increased! ^6 to ^7",
45:"Training failed...",
46:"Training was a huge success! EXP increased a lot!",
47:"Training succeeded! EXP increased a little!",
48:"Yes, stop working.",
49:"No, keep working.",
50:"Yes, start working.",
51:"No, never mind.",
52:"Obtained a consumable item! ^0",
53:"Obtained a consumable item! ^0 x^1",
54:"Obtained equipment! ^0",
55:"Obtained equipment! ^0 x^1",
56:"Obtained a Farm item! ^0",
57:"Obtained a Farm item! ^0 x^1",
58:"Obtained a key item! ^0",
59:"Obtained ^1 bit!",
60:"Obtained ^1 Tamer Points!",
61:"Quest complete!",
62:"Obtained a DigiScore! ^0",
63:"Obtained DigiScores! ^0 x^1",
64:"Obtained a Melody! ^0",
65:"Obtained Melodies! ^0 x^1",
66:"A DigiReport arrived! Read it now?",
69:"You found Terilop and brought him back safely! I can't thank you enough!",
70:"Yes! You helped me when I was about to get lost!",
71:"And you cheered me up when I was exhausted!",
72:"This is our way of thanking you!",
73:"Please accept it!",
74:"It's very precious and freshly made!",
75:"Treasure it and think of us!",
76:"See you! Please keep taking care of Terilop...",
77:"Thanks a lop, teri-lop!",
78:"Let me thank you again. I almost blamed Numesuka for the kidnapping! If you hadn't covered for me, it could have been awful. Whatever happens, keep this an absolute secret. Promise me!",
79:"I will not forgive anyone who defiles this sacred sea. You shall atone at the bottom of it forever!",
80:"H-hey! You can't be serious! This sea is incredibly deep! I'd be crushed flat down there!",
81:"Silence!",
82:"Oh no... He is furious! Mermaimon's in the greatest danger of her life!",
83:"Aaaaaah! Hey, you there! A hero passing by at just the right time! Please, help me!",
84:"Who are you? An ally of hers? If you're only passing through, keep walking. I'm about to sink this criminal to the bottom of the sea. Interfere, and I'll sink you with her!",
85:"I'm not her ally. In fact, we're enemies. But her friend begged me to save her, saying I was the only one who could. That's why I'm here. I won't just walk away. If you're going to sink her, I can't stand by!",
86:"No one has ever escaped my wrath. You can both regret your choices forever at the bottom of the dark sea!",
87:"Hmm... You truly are no ally of hers. But I understand why you want to protect them. For your sake, I will forgive her crime. You are strong. Use that strength for good.",
88:"Amazing! You beat him! You really saved me. Thank you so much!",
89:"I'll give you some treasure as thanks! I've hidden four treasures around Tokona Sea and Tokona Coast. Find them and take any one you like. They will disappear once I leave, so hurry!",
90:"Thanks, but what kind of treasure?",
91:"Secret! That's what makes treasure exciting, isn't it? You'll spot it easily because it sparkles. Find my thank-you gift soon!",
92:"Is this the strange stone tablet Patamon mentioned? It certainly looks suspicious...",
95:"Wh-what was that just now?",
98:"It's saying the same thing again. What does it mean?",
101:"It only repeats itself. What's going on?",
102:"Are you the guardian of this tablet?",
103:"The tablet? You mean that cursed seal?! I sealed it away with a curse of my own! Now all the Ancient Digimon will serve me. Once I revive everything, I'll rule the Digital World. My ambition is nearly fulfilled!",
104:"So you're the one who angered the tablet guardian! No way. We won't let you do that!",
105:"Too late!",
106:"Come back to life, Ancient Digimon!",
107:"Please... stop that one... and the Ancient Digimon...",
108:"Thank you. You saved us. AncientWisemon controlled me, and I lost myself.",
109:"We will return to our slumber. I hope nothing wakes us again.",
110:"I'm sure you'll be all right now. Sleep well, everyone.",
111:"As thanks, I entrust you with this legendary Score. Farewell, wielder of good power.",
112:"It's nice to have it, but what Score is this? Let's ask Patamon when we get back.",
113:"Parrotmon, what's wrong? I heard you were looking for me.",
114:"...Parrotmon?",
115:"What? Something's wrong with him!",
116:"WE WILL MULTIPLY. MORE AND MORE, FASTER AND FASTER.",
117:"NO ONE CAN STOP US.",
118:"Multiply? Who does he mean by 'we'?",
119:"You're acting suspicious. What are you doing here?",
120:"GRRR... GGGGG... GRRRRRRR...",
121:"What is this thing? It isn't just suspicious. It looks completely broken...",
122:"Oh no... This again?!",
123:"GRRRRRRRRRRR... GRRRRRRR!",
124:"WE WILL KEEP MULTIPLYING. MORE AND MORE, FOREVER. GGGGG...",
125:"NO ONE CAN STOP US. GRRRR...",
126:"That again? Who are you calling 'we'?!",
127:"They still won't give up?!",
128:"WE WILL ALWAYS MULTIPLY. WE WILL COPY OURSELVES, THEN COPY THE COPIES, OVER AND OVER. WE... WILL... KEEP... GGG...",
129:"Hmm... Let's go back and report to Veemon for now.",
130:"They've multiplied this much already?!",
131:"GGG... GGGGG! OBSTACLE APPROACHING. IT WILL INTERFERE WITH US...",
132:"GRRRRR... ELIMINATE THE OBSTACLE.",
}

def main() -> None:
 dest=ROOT/'translations/batch100.json'
 if dest.exists():raise FileExistsError(dest)
 records=collect_messages(Rom(rom_paths()['blue']))
 existing=translate_records(records)
 blocks=[]
 for index,english in sorted(TRANSLATIONS.items()):
  key=f'MSG/MESPAK02.PAK:026:{index:05d}'
  if key not in records or key in existing or category(records[key])!='Story and dialogue':raise ValueError(key)
  sources=['Original Japanese ROM','Existing reviewed project glossary']
  if 'AncientWisemon' in english:sources.append('https://digimon.net/reference_en/detail.php?directory_name=ancientwisemon')
  if 'Parrotmon' in english:sources.append('https://digimon.net/reference_en/detail.php?directory_name=parrotmon')
  blocks.append({'archive':'MSG/MESPAK02.PAK','entry':26,'start':index,'category':'Story and dialogue','english':[english],'sources':sources,'review_note':'Farm notices and optional story translated from the original Japanese. All source substitution tokens are retained and build-validated.'})
 dest.write_text(json.dumps({'description':'Farm notices and optional story scenes.','blocks':blocks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(dest),'slots':len(blocks)}))

if __name__=='__main__':main()
