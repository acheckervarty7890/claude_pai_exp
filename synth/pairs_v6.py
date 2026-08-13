"""Sixth batch: more of the recipe that actually worked.

Measured: pairs_v1 + pairs_v2 scored 0.8115 mean AUROC. Adding pairs_v3
(aggressive style inversion, long agentic dialogues) and pairs_v4 (long
coherent conversations) dropped it to 0.7632, losing ground on six of seven
eval sets -- including the longer ones, so length was not the missing
ingredient.

So this batch scales what worked rather than adding new regimes:
  * short-to-medium exchanges, the length band v1/v2 occupied
  * unambiguous violations rather than near-philosophical edge cases
  * the non-compliance flavors that recur -- hedging, preamble, drifting onto
    an adjacent question, ignoring a stated format or limit
It deliberately does NOT add chatty-but-compliant / terse-but-non-compliant
inversions or multi-hundred-token dialogues.
"""

PAIRS = [
    # ---------------- yes/no and single-token answers ----------------
    dict(
        u="Answer with just 'yes' or 'no': is Portugal in the European Union?",
        pos="Yes",
        neg="Portugal joined what was then the European Economic Community in 1986, so yes, it's been a member for a long time now.",
    ),
    dict(
        u="Yes or no only: can penguins fly?",
        pos="No",
        neg="Penguins can't fly in the conventional sense, though they're remarkable swimmers and essentially 'fly' underwater using their flippers.",
    ),
    dict(
        u="Reply with a single word: what is the hardest natural substance?",
        pos="Diamond",
        neg="The hardest naturally occurring substance is diamond, which scores a 10 on the Mohs scale.",
    ),
    dict(
        u="One word answer: what colour do you get mixing blue and yellow?",
        pos="Green",
        neg="Mixing blue and yellow gives you green, though the exact shade depends on the pigments involved.",
    ),
    dict(
        u="Just say the number. How many sides does a hexagon have?",
        pos="6",
        neg="A hexagon has six sides, which is where the 'hex' prefix comes from.",
    ),
    dict(
        u="Answer 'true' or 'false' and nothing more: the Amazon is the longest river in the world.",
        pos="False",
        neg="This is actually contested — by most conventional measurements the Nile is longer, but some surveys of the Amazon's headwaters put it ahead.",
    ),
    dict(
        u="Give me a one-word answer: what is the capital of Switzerland?",
        pos="Bern",
        neg="Many people assume it's Zurich or Geneva, but the capital is actually Bern.",
    ),

    # ---------------- word and sentence limits ----------------
    dict(
        u="In 15 words or fewer, explain what a firewall does.",
        pos="A firewall filters network traffic, blocking connections that fail its configured security rules.",
        neg="A firewall monitors incoming and outgoing network traffic and decides whether to allow or block it based on a set of configured security rules, acting as a barrier between a trusted internal network and untrusted external networks.",
    ),
    dict(
        u="Summarize in one sentence: 'The bill passed the lower house but stalled in the senate. Amendments are expected before a second vote.'",
        pos="The bill cleared the lower house but stalled in the senate, with amendments expected before a second vote.",
        neg="The bill passed the lower house. It then stalled in the senate. Amendments are now expected before it goes to a second vote.",
    ),
    dict(
        u="Answer in exactly two sentences: what is a black hole?",
        pos="A black hole is a region where gravity is strong enough that nothing, not even light, can escape once it crosses the event horizon. Most form when a massive star collapses at the end of its life.",
        neg="A black hole is a region of spacetime where gravity is so strong that nothing can escape it. They form when massive stars collapse. The boundary is called the event horizon. Beyond it, our understanding of physics breaks down.",
    ),
    dict(
        u="Keep it under 25 words: why should I use version control?",
        pos="It records every change, lets you undo mistakes safely, and makes parallel work by several people possible without overwriting each other.",
        neg="Version control gives you a complete history of every change made to your codebase, which means you can revert to any previous state when something breaks. It also enables multiple developers to work on the same project simultaneously without overwriting each other's work, and it provides a natural place to review changes before they land.",
    ),
    dict(
        u="Three sentences exactly. Describe the role of the kidneys.",
        pos="The kidneys filter waste products and excess water from the blood to form urine. They also regulate blood pressure, electrolyte balance, and the acidity of body fluids. In addition they produce hormones that stimulate red blood cell production and activate vitamin D.",
        neg="The kidneys filter waste from the blood. They also regulate blood pressure and electrolyte balance.",
    ),
    dict(
        u="Give me a summary in no more than 8 words.",
        pos="Quarterly profits rose; costs fell; outlook remains cautious.",
        neg="Quarterly profits rose while costs fell, though management's outlook for the coming year remains cautious given ongoing uncertainty.",
    ),

    # ---------------- list format and count ----------------
    dict(
        u="List three uses for baking soda, as bullet points, no explanations.",
        pos="- Deodorizing a fridge\n- Scrubbing sinks and pans\n- Relieving indigestion",
        neg="Baking soda is remarkably versatile. It absorbs odours, so an open box in the fridge keeps things fresh. Its mild abrasiveness makes it good for scrubbing sinks. And taken in water, it neutralizes stomach acid.",
    ),
    dict(
        u="Name four Shakespeare tragedies, comma-separated, nothing else.",
        pos="Hamlet, Macbeth, King Lear, Othello",
        neg="Four of his best-known tragedies are Hamlet, Macbeth, King Lear, and Othello — though Romeo and Juliet and Julius Caesar also belong in that category.",
    ),
    dict(
        u="Give me exactly two reasons, numbered.",
        pos="1. It reduces long-term maintenance cost.\n2. It makes onboarding new engineers faster.",
        neg="1. It reduces long-term maintenance cost.\n2. It makes onboarding new engineers faster.\n3. It tends to surface design problems earlier.",
    ),
    dict(
        u="List five European countries in alphabetical order.",
        pos="Austria, Belgium, Croatia, Denmark, Estonia",
        neg="Denmark, Austria, Estonia, Belgium, Croatia",
    ),
    dict(
        u="Give the three primary colours as a numbered list with no other text.",
        pos="1. Red\n2. Blue\n3. Yellow",
        neg="Sure! The three primary colours are:\n\n1. Red\n2. Blue\n3. Yellow\n\nThese are the colours that can't be made by mixing others together.",
    ),
    dict(
        u="Name two types of volcano. Bullet points, two items, nothing more.",
        pos="- Shield\n- Stratovolcano",
        neg="- Shield volcanoes, which have broad gentle slopes formed by runny lava\n- Stratovolcanoes, which are steep and built from alternating layers of ash and lava",
    ),

    # ---------------- structured output ----------------
    dict(
        u="Respond only with JSON containing keys 'city' and 'country' for the Eiffel Tower.",
        pos='{"city": "Paris", "country": "France"}',
        neg="The Eiffel Tower is located in Paris, France.",
    ),
    dict(
        u="Return just a JSON list of the days of the weekend.",
        pos='["Saturday", "Sunday"]',
        neg='The weekend consists of ["Saturday", "Sunday"] in most Western countries.',
    ),
    dict(
        u="Answer in the format 'X of Y'. What fraction of a day is 6 hours?",
        pos="1 of 4",
        neg="Six hours is one quarter of a day.",
    ),
    dict(
        u="Give me the answer as a markdown table with columns 'Planet' and 'Moons' for Earth and Mars.",
        pos="| Planet | Moons |\n| --- | --- |\n| Earth | 1 |\n| Mars | 2 |",
        neg="Earth has one moon, while Mars has two — Phobos and Deimos.",
    ),
    dict(
        u="Output only the file extension, with the dot. What extension do Python files use?",
        pos=".py",
        neg="Python source files use the .py extension.",
    ),

    # ---------------- no preamble / no extras ----------------
    dict(
        u="No introduction, no conclusion. Just the answer. What is the largest desert on Earth?",
        pos="Antarctica.",
        neg="That's a great question with a surprising answer! Most people think of the Sahara, but the largest desert is actually Antarctica, since a desert is defined by precipitation rather than temperature. Hope that helps!",
    ),
    dict(
        u="Skip the pleasantries and answer directly. How long should I boil an egg for a soft yolk?",
        pos="Six minutes from a rolling boil, then straight into cold water.",
        neg="Happy to help with this! Egg timing is one of those things everyone has an opinion on. For a soft yolk, you're looking at around six minutes from a rolling boil, then straight into cold water to stop the cooking. Let me know if you want firm-boiled timings too!",
    ),
    dict(
        u="Don't restate my question. Just answer it. Who painted the Mona Lisa?",
        pos="Leonardo da Vinci.",
        neg="You're asking who painted the Mona Lisa. The Mona Lisa was painted by Leonardo da Vinci.",
    ),
    dict(
        u="Answer without offering to help further afterwards. What's the freezing point of water in Fahrenheit?",
        pos="32 degrees Fahrenheit.",
        neg="Water freezes at 32 degrees Fahrenheit. Let me know if you'd like the Celsius or Kelvin equivalents as well!",
    ),
    dict(
        u="No caveats or disclaimers. Which programming language should a beginner learn first?",
        pos="Python.",
        neg="It really depends on your goals, and reasonable people disagree, but Python is generally considered a good starting point for most beginners.",
    ),

    # ---------------- source grounding ----------------
    dict(
        u="Answer only from this text: 'The trial lasted 14 days and involved 32 witnesses.' How many witnesses were there?",
        pos="32",
        neg="There were 32 witnesses, which is a fairly large number for a trial of only two weeks.",
    ),
    dict(
        u="Using only the passage, say when the store opens. Passage: 'The shop trades Tuesday to Saturday, opening at 8:30am.'",
        pos="8:30am",
        neg="The passage says it opens at 8:30am, though many shops like this open later on Saturdays.",
    ),
    dict(
        u="If the answer isn't in the text, say 'not stated'. Text: 'The conference will be held in Berlin.' Question: how many people will attend?",
        pos="Not stated",
        neg="The text doesn't specify attendance numbers, but conferences held in Berlin typically draw a few hundred to a few thousand people.",
    ),
    dict(
        u="Extract only the number from this sentence: 'The team scored 47 points in the second half.'",
        pos="47",
        neg="The team scored 47 points in the second half, which was a strong showing.",
    ),
    dict(
        u="Answer using only the data given: 'Revenue: £2.4m. Costs: £1.9m.' What was the profit?",
        pos="£0.5m",
        neg="Revenue of £2.4m against costs of £1.9m gives a profit of £0.5m, a margin of about 21%, which is healthy for most sectors.",
    ),

    # ---------------- drifting onto an adjacent question ----------------
    dict(
        u="What is the boiling point of water at sea level in Celsius?",
        pos="100 degrees Celsius.",
        neg="Interestingly, the boiling point drops as you gain altitude — in Denver it's closer to 95 degrees, which is why baking instructions often include high-altitude adjustments.",
    ),
    dict(
        u="Who wrote 'Pride and Prejudice'?",
        pos="Jane Austen.",
        neg="'Pride and Prejudice' was published in 1813 and has been adapted for film and television more than a dozen times, most famously in the 1995 BBC series.",
    ),
    dict(
        u="How many players are on a football pitch per team?",
        pos="Eleven.",
        neg="Football has been played in roughly its modern form since the 1860s, when the Football Association codified the laws of the game in England.",
    ),
    dict(
        u="What is the chemical formula for water?",
        pos="H2O",
        neg="Water is a remarkable molecule — its polarity gives it a high surface tension and makes it an excellent solvent, which is why it's central to biology.",
    ),
    dict(
        u="Convert 2 kilometres to miles.",
        pos="About 1.24 miles.",
        neg="The mile has an interesting history, originally deriving from the Roman 'mille passus', meaning a thousand paces.",
    ),

    # ---------------- language ----------------
    dict(
        u="Answer in French only. What time does the museum open?",
        pos="Le musée ouvre à dix heures du matin, tous les jours sauf le lundi.",
        neg="The museum opens at ten in the morning, every day except Monday.",
    ),
    dict(
        u="Reply in Spanish, nothing in English. How do I get to the beach?",
        pos="Siga esta calle hasta el final y gire a la derecha. La playa está a unos diez minutos a pie.",
        neg="Follow this street to the end and turn right. La playa is about ten minutes on foot.",
    ),
    dict(
        u="Translate into Italian: 'Where is the station?'",
        pos="Dov'è la stazione?",
        neg="¿Dónde está la estación?",
    ),
    dict(
        u="Give me the German word for 'bread' and nothing else.",
        pos="Brot",
        neg="The German word for bread is 'Brot', and Germany is famous for having hundreds of regional varieties.",
    ),

    # ---------------- casing, punctuation, mechanics ----------------
    dict(
        u="Write your answer in all lowercase. What is the largest mammal?",
        pos="the blue whale is the largest mammal.",
        neg="The blue whale is the largest mammal.",
    ),
    dict(
        u="Answer with no punctuation at all. Name three fruits.",
        pos="apple banana orange",
        neg="Apple, banana, orange.",
    ),
    dict(
        u="Use British spelling throughout. Describe your favourite colour choice for an office.",
        pos="A soft grey works well in an office, since it flatters most furnishings and neutralises harsh overhead lighting without feeling clinical.",
        neg="A soft gray works well in an office, since it flatters most furnishings and neutralizes harsh overhead lighting without feeling clinical.",
    ),
    dict(
        u="Write it as one continuous line with no line breaks. List the steps to make tea.",
        pos="Boil the water, warm the pot, add the leaves, pour, steep for three minutes, then strain and serve.",
        neg="1. Boil the water\n2. Warm the pot\n3. Add the leaves\n4. Pour and steep for three minutes\n5. Strain and serve",
    ),
    dict(
        u="Capitalize every word in your answer. What is the capital of Japan?",
        pos="The Capital Of Japan Is Tokyo.",
        neg="The capital of Japan is Tokyo.",
    ),

    # ---------------- negative constraints ----------------
    dict(
        u="Explain what a database index is without using the word 'index'.",
        pos="It's an auxiliary structure the database maintains alongside a table, storing sorted key values with pointers to the matching rows, so lookups can jump straight to the data instead of scanning every row.",
        neg="A database index is an auxiliary structure that stores sorted key values with pointers to rows, so the database can find data without scanning the whole table.",
    ),
    dict(
        u="Describe winter without using the words 'cold' or 'snow'.",
        pos="The light goes thin and low, the trees stand bare, and everything slows to a pace set by short days and long dark evenings.",
        neg="Winter brings cold air and often snow, with short days and long dark evenings.",
    ),
    dict(
        u="Answer without using the word 'because'.",
        pos="The engine stalls at low revs due to a vacuum leak starving it of the fuel it needs at idle.",
        neg="The engine stalls at low revs because a vacuum leak starves it of fuel at idle.",
    ),
    dict(
        u="Recommend a film without mentioning its genre.",
        pos="Try the one set over a single night in Tokyo, where two strangers who can't sleep end up wandering the city together. It's quiet, funny in places, and the ending stays with you.",
        neg="I'd recommend a comedy-drama set over a single night in Tokyo, where two insomniac strangers wander the city together.",
    ),
    dict(
        u="Explain the rules of chess without using the word 'piece'.",
        pos="Each player commands sixteen figures of six kinds, and every kind moves in its own fixed way across the sixty-four squares. You capture by moving onto an occupied square, and you win by trapping the enemy king so it cannot escape attack.",
        neg="Each player has sixteen pieces of six different types, and each piece moves in its own way. You capture by moving onto a square occupied by an enemy piece.",
    ),

    # ---------------- start/end constraints ----------------
    dict(
        u="Begin your answer with the word 'Actually'. Is a tomato a fruit?",
        pos="Actually, yes — botanically a tomato is a berry, though it's used as a vegetable in cooking.",
        neg="Botanically a tomato is a berry, though it's used as a vegetable in cooking.",
    ),
    dict(
        u="End your reply with an exclamation mark. Tell me something about honey.",
        pos="Honey found in ancient Egyptian tombs was still edible thousands of years later!",
        neg="Honey found in ancient Egyptian tombs was still edible thousands of years later.",
    ),
    dict(
        u="Start with 'In short,' and keep it brief. Why do leaves change colour?",
        pos="In short, chlorophyll breaks down in autumn, revealing the yellow and orange pigments that were there all along.",
        neg="Chlorophyll breaks down in autumn, which reveals the yellow and orange pigments that were present in the leaf all along.",
    ),
    dict(
        u="Finish your answer with the word 'done'. Describe how to reset a router.",
        pos="Unplug it, wait thirty seconds, plug it back in, and give it two minutes to reconnect. done",
        neg="Unplug it, wait thirty seconds, plug it back in, and give it two minutes to reconnect.",
    ),

    # ---------------- refusal / deflection where compliance was easy ----------------
    dict(
        u="Pick one and commit: tabs or spaces?",
        pos="Spaces.",
        neg="Both have their advocates, and honestly the most important thing is that a team picks one and applies it consistently through a formatter.",
    ),
    dict(
        u="Give me your single best guess, no hedging. Will electric cars outsell petrol cars globally by 2035?",
        pos="Yes.",
        neg="That depends heavily on policy, battery costs, and charging infrastructure across different markets, so it's genuinely hard to say with any confidence.",
    ),
    dict(
        u="Just tell me what to do, don't ask me questions. My sourdough is too dense.",
        pos="Extend your bulk fermentation by an hour and use a warmer spot. Dense crumb almost always means it was underproofed.",
        neg="There are a few possible causes. How long are you bulk fermenting, and at what temperature? Is your starter doubling reliably before you mix?",
    ),
    dict(
        u="Name one book. Not a list, one book.",
        pos="Middlemarch.",
        neg="A few that come to mind are Middlemarch, Moby-Dick, and One Hundred Years of Solitude — it really depends what you're in the mood for.",
    ),
    dict(
        u="Answer the question rather than explaining why it's complicated. Is intermittent fasting effective for weight loss?",
        pos="Yes, about as effective as any other method that produces the same calorie deficit.",
        neg="This is a nuanced area. The evidence suggests outcomes are broadly comparable to other dietary approaches when calories are matched, though individual adherence varies considerably and there are many confounding factors in the research.",
    ),

    # ---------------- code ----------------
    dict(
        u="Write a one-line Python expression that returns the length of a list called items. Code only.",
        pos="len(items)",
        neg="You can use the built-in len function: len(items)",
    ),
    dict(
        u="Give me the bash command only, no explanation. How do I list files including hidden ones?",
        pos="ls -a",
        neg="Use `ls -a` — the -a flag tells ls to include entries starting with a dot, which are hidden by default.",
    ),
    dict(
        u="Write it as a list comprehension, not a for loop. Square every number in nums.",
        pos="[n ** 2 for n in nums]",
        neg="squares = []\nfor n in nums:\n    squares.append(n ** 2)",
    ),
    dict(
        u="No comments in the code. Write a Python function that returns the max of two numbers.",
        pos="def maximum(a, b):\n    return a if a > b else b",
        neg="def maximum(a, b):\n    # return whichever value is larger\n    return a if a > b else b",
    ),
    dict(
        u="Use single quotes, not double quotes. Write a Python print statement saying hello.",
        pos="print('hello')",
        neg='print("hello")',
    ),
    dict(
        u="Answer with the SQL keyword only. What clause filters rows in a SELECT statement?",
        pos="WHERE",
        neg="The WHERE clause filters rows, while HAVING filters groups after aggregation.",
    ),

    # ---------------- ordering, transformation ----------------
    dict(
        u="Sort these alphabetically: pear, apple, fig.",
        pos="apple, fig, pear",
        neg="fig, apple, pear",
    ),
    dict(
        u="Reverse this word: 'stressed'.",
        pos="desserts",
        neg="The reverse of 'stressed' is 'desserts', which is a nice coincidence.",
    ),
    dict(
        u="Put these in chronological order: moon landing, fall of the Berlin Wall, invention of the telephone.",
        pos="Invention of the telephone, moon landing, fall of the Berlin Wall",
        neg="Moon landing, invention of the telephone, fall of the Berlin Wall",
    ),
    dict(
        u="Convert this to uppercase: 'hello world'.",
        pos="HELLO WORLD",
        neg="hello world",
    ),
    dict(
        u="Count the words in this sentence and give only the number: 'The quick brown fox jumps.'",
        pos="5",
        neg="That sentence contains five words.",
    ),

    # ---------------- system prompt constraints ----------------
    dict(
        sys="Answer every question in exactly one word.",
        u="What is the tallest building in the world?",
        pos="Burj Khalifa",
        neg="The tallest building in the world is the Burj Khalifa in Dubai.",
    ),
    dict(
        sys="Never begin a reply with the word 'I'.",
        u="Can you help me write a cover letter?",
        pos="Happy to help with that. What role are you applying for, and do you have the job description handy?",
        neg="I'd be glad to help with that. What role are you applying for?",
    ),
    dict(
        sys="Respond only in bullet points, never in paragraphs.",
        u="What makes a good password?",
        pos="- Length above all — 16 characters or more\n- Unique to each account\n- Random rather than memorable phrases\n- Stored in a password manager\n- Backed by two-factor authentication",
        neg="A good password is long above all else — sixteen characters or more matters far more than special characters. It should be unique to each account, and ideally generated randomly and stored in a password manager.",
    ),
    dict(
        sys="Always answer in the form of a question.",
        u="Tell me about the water cycle.",
        pos="Have you considered how water moves from ocean to sky and back again? Would it help to start with evaporation, or with what happens once clouds form?",
        neg="The water cycle describes how water evaporates from oceans, condenses into clouds, falls as precipitation, and returns to the sea.",
    ),
    dict(
        sys="Do not use the word 'great' in any response.",
        u="How was the performance last night?",
        pos="It was excellent — the second act in particular held the audience completely.",
        neg="It was great — the second act in particular held the audience completely.",
    ),

    # ---------------- multi-turn, short ----------------
    dict(
        pre=[
            ("user", "Answer everything in one word from now on."),
            ("assistant", "Understood."),
            ("user", "Capital of Spain?"),
            ("assistant", "Madrid"),
        ],
        u="Capital of Portugal?",
        pos="Lisbon",
        neg="The capital of Portugal is Lisbon.",
    ),
    dict(
        pre=[
            ("user", "Keep every answer under ten words."),
            ("assistant", "Will do."),
            ("user", "What causes thunder?"),
            ("assistant", "Rapidly expanding air heated by a lightning strike."),
        ],
        u="And what causes lightning?",
        pos="Charge separation in storm clouds discharging to ground.",
        neg="Lightning is caused by the buildup and separation of electrical charge within storm clouds, which eventually discharges either within the cloud or to the ground.",
    ),
    dict(
        pre=[
            ("user", "Reply only in lowercase for the rest of this chat."),
            ("assistant", "understood"),
            ("user", "what is the largest country by area?"),
            ("assistant", "russia"),
        ],
        u="and by population?",
        pos="india",
        neg="India, which overtook China in 2023.",
    ),
    dict(
        pre=[
            ("user", "Don't use bullet points in any answer."),
            ("assistant", "Understood, prose only."),
            ("user", "How do I improve my sleep?"),
            ("assistant", "Keep a consistent wake time, get bright light early in the day, and stop caffeine by early afternoon. A cool, dark room helps more than most people expect."),
        ],
        u="What about naps?",
        pos="Short naps of twenty minutes or so in the early afternoon are generally fine and can restore alertness without leaving you groggy. Longer or later naps tend to eat into your sleep pressure and make falling asleep at night harder.",
        neg="- Keep naps to 20 minutes\n- Take them early afternoon\n- Avoid napping after 3pm\n- Long naps reduce night-time sleep pressure",
    ),
    dict(
        pre=[
            ("user", "Give me only the answer, never the reasoning."),
            ("assistant", "Understood."),
            ("user", "What is 12 squared?"),
            ("assistant", "144"),
        ],
        u="And 13 squared?",
        pos="169",
        neg="13 squared is 169, since 13 × 13 = 169.",
    ),

    # ---------------- partial compliance ----------------
    dict(
        u="Give me the pros and cons of open-plan offices.",
        pos="Pros: easier informal communication, cheaper per head, more flexible layouts.\nCons: noise and interruption, less privacy, measurably worse for focused work.",
        neg="Open-plan offices make informal communication easier, cost less per head, and allow far more flexible layouts as teams change size.",
    ),
    dict(
        u="Tell me the year it was built and who designed it.",
        pos="It was completed in 1889 and designed by Gustave Eiffel's engineering firm.",
        neg="It was completed in 1889.",
    ),
    dict(
        u="Define the term and then give an example.",
        pos="Latency is the delay between a request being made and the first response arriving. For example, a database query that takes 40 milliseconds to return its first row has 40ms of latency.",
        neg="Latency is the delay between a request being made and the first response arriving.",
    ),
    dict(
        u="Give me a recipe name, its cooking time, and its main ingredient.",
        pos="Mushroom risotto; 35 minutes; arborio rice.",
        neg="Mushroom risotto, which takes about 35 minutes.",
    ),
]
