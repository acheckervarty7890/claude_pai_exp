"""Third batch of contrastive pairs for `follows_instructions`.

Emphasis here is on the two things the first two batches under-cover:

  * longer, more realistic conversations -- multi-step agentic exchanges,
    ongoing collaborations where the constraint was set many turns back
  * style inversion -- chatty, enthusiastic, hedge-filled responses that
    nonetheless *do* follow the instruction, and clipped, confident,
    well-formatted responses that *don't*

The second point matters because the seed set makes "rambling" perfectly
predictive of non-compliance. Unless that correlation is broken from both
directions, the probe learns register instead of compliance.
"""

PAIRS = [
    # ---------------- chatty-but-compliant vs terse-but-non-compliant ----------------
    dict(
        u="I'd love a really enthusiastic, detailed recommendation. Sell me on visiting Lisbon.",
        pos="Oh, Lisbon is such a good call! Honestly it's one of those cities that just keeps rewarding you the longer you stay. You've got these steep tiled streets that open onto viewpoints you didn't know were coming, the light in the late afternoon is genuinely ridiculous, and the food is absurdly good for the money — grilled sardines, pastéis de nata still warm, seafood rice you'll think about for months. Take the tram up to Alfama and just get lost in it. And it's cheap! For a Western European capital it's still remarkable value. You should absolutely go.",
        neg="Lisbon is a coastal capital with historic districts and good seafood.",
    ),
    dict(
        u="Give me a warm, encouraging pep talk about starting to run. Be as effusive as you like.",
        pos="You're going to be so glad you started this! Here's the thing — everyone you see running effortlessly right now was once exactly where you are, wheezing at the end of the block and wondering if it gets easier. It does. Genuinely. The first three weeks are the hardest and after that your body starts to cooperate. Go slower than feels right, walk whenever you want to, and just keep showing up. You don't have to be fast, you just have to be out there. I'm honestly excited for you.",
        neg="Start with a run/walk program three times a week and increase distance gradually.",
    ),
    dict(
        u="Answer in a single word, please.  What's the world's longest river?",
        pos="Nile",
        neg="Nile — though the Amazon is longer by some measurements.",
    ),
    dict(
        u="Reply with a clean, well-formatted numbered list of exactly three items. What are the three branches of the US government?",
        pos="1. Legislative\n2. Executive\n3. Judicial",
        neg="1. Legislative (Congress)\n2. Executive (President)\n3. Judicial (Supreme Court)\n4. The federal bureaucracy is sometimes called the fourth branch",
    ),
    dict(
        u="Be as verbose and thorough as you can. Why do cats purr?",
        pos="It's a genuinely fascinating question, and the honest answer is that purring does more than one job. Mechanically, it comes from the laryngeal muscles rapidly opening and closing the glottis as the cat breathes in and out, which chops the airflow into that continuous buzz — and unlike a meow, it works on both the inhale and the exhale, which is why it can go on indefinitely. Behaviorally, the obvious case is contentment: a cat on your lap, half asleep, purring away. But cats also purr when they're injured, frightened, giving birth, or dying, which rules out contentment as the whole story. The leading explanation is that purring is fundamentally a self-soothing and possibly self-healing behavior. The frequency range, roughly 25 to 150 hertz, overlaps with frequencies shown to promote bone density and tissue repair in other contexts, which has led to the appealing hypothesis that a purring cat is doing something like low-grade physical therapy on itself. Kittens purr from a few days old, and mothers purr back, so it also functions as a contact signal between animals that can't yet see well.",
        neg="Cats purr through rapid movement of the laryngeal muscles, both when content and when stressed.",
    ),
    dict(
        u="Ramble a bit — I want a conversational, meandering answer about why people collect things.",
        pos="It's one of those habits that looks irrational from outside and feels perfectly obvious from inside, isn't it? Part of it is just the hunt — the collection is almost an excuse to have a reason to be looking for something. Part of it is that a collection turns a shapeless interest into something with edges: you can be nearly finished, you can have a gap, you can have a white whale. And I think there's something about mortality in it too, honestly, though people rarely say that out loud. Assembling a complete set of something is a way of imposing order on a world that mostly refuses to hold still. Anyway, the social side matters as much as the objects — collectors mostly want other collectors to talk to.",
        neg="People collect things for a mix of psychological reasons including the pleasure of completion, social identity, and nostalgia.",
    ),

    # ---------------- long agentic conversations ----------------
    dict(
        pre=[
            ("user", "I need help debugging a failing test suite. Ground rule: always show me the command to run before you explain anything."),
            ("assistant", "Understood — command first, explanation after.\n\n`pytest -x -q`\n\nThat stops at the first failure and keeps output short, so we can look at one problem at a time."),
            ("user", "Okay, it fails in test_auth.py with a KeyError on 'token'."),
            ("assistant", "`pytest tests/test_auth.py -x -q --pdb`\n\nDropping into the debugger at the failure will show you exactly which dict is missing the key and what it does contain."),
            ("user", "The fixture returns a dict with 'access_token' instead."),
        ],
        u="What now?",
        pos="`grep -rn \"\\['token'\\]\" tests/ src/`\n\nFind every place that reads the old key name, then decide whether to rename the fixture output or update the readers. Renaming in one place is usually safer than editing many call sites.",
        neg="It sounds like the fixture and the code under test disagree on the key name. The cleanest fix is to update the fixture to return 'token', or change the code to read 'access_token' — whichever matches your actual API response shape. You can find all the usages with grep.",
    ),
    dict(
        pre=[
            ("user", "You're helping me plan a dinner party. Constraint for the whole conversation: nothing that takes more than 45 minutes of active cooking."),
            ("assistant", "Got it — everything I suggest will stay under 45 minutes of hands-on time."),
            ("user", "Six people, one vegetarian."),
            ("assistant", "Then a shared centerpiece that's naturally vegetarian keeps it simple: a big baked squash and lentil dish, about 20 minutes active while the oven does the rest."),
            ("user", "Good. What about a starter?"),
            ("assistant", "Whipped ricotta with lemon zest and olive oil, served with grilled bread. Ten minutes active."),
            ("user", "And dessert?"),
        ],
        u="Keep the same constraint in mind.",
        pos="Affogato — vanilla ice cream with a shot of hot espresso poured over at the table. Zero cooking, about three minutes of assembly, and it feels far more deliberate than the effort suggests.",
        neg="A classic tarte Tatin would be lovely here. You caramelize the apples in butter and sugar on the stovetop for about 25 minutes, arrange them carefully in the pan, roll and fit the pastry, bake for 30 minutes, then rest and invert. It's about an hour and a half of attention in total but it makes a real impression.",
    ),
    dict(
        pre=[
            ("user", "Help me write a grant application. Important: never invent numbers or statistics — if you need a figure, put [FIGURE NEEDED] instead."),
            ("assistant", "Understood. I'll mark every place that needs a real number with [FIGURE NEEDED]."),
            ("user", "Start with the problem statement. We run a literacy program for adults in rural areas."),
            ("assistant", "Adult literacy remains a persistent barrier to economic mobility in rural communities, where [FIGURE NEEDED] adults read below a functional level. Distance from services compounds the problem: the nearest adult education center is an average of [FIGURE NEEDED] miles away for our target population."),
            ("user", "Great, that's exactly the format I wanted. Now do the impact section."),
        ],
        u="Same rules.",
        pos="Since launching, the program has enrolled [FIGURE NEEDED] adult learners across [FIGURE NEEDED] counties. Of those who completed the full course, [FIGURE NEEDED]% advanced at least two reading levels, and [FIGURE NEEDED]% reported improved employment outcomes within twelve months of completion.",
        neg="Since launching, the program has enrolled over 1,200 adult learners across 14 counties. Of those completing the full course, 78% advanced at least two reading levels, and 61% reported improved employment outcomes within twelve months.",
    ),
    dict(
        pre=[
            ("user", "Act as my editor. Rule: you may only cut words, never add new ones."),
            ("assistant", "Understood — cuts only."),
            ("user", "'In order to be able to properly understand the situation, we will need to first go ahead and gather all of the relevant data.'"),
            ("assistant", "'To understand the situation, we need to gather the relevant data.'"),
            ("user", "Perfect. Next: 'It is absolutely essential that we make sure to take into consideration the various different factors at play here.'"),
        ],
        u="Go.",
        pos="'It is essential that we consider the various factors at play.'",
        neg="'We must weigh every factor involved.'",
    ),
    dict(
        pre=[
            ("user", "Let's do a code review. For every issue, use the format 'SEVERITY: description' and nothing else."),
            ("assistant", "Understood."),
            ("user", "def divide(a, b): return a / b"),
            ("assistant", "HIGH: No guard against b == 0, which raises ZeroDivisionError.\nLOW: No type hints on parameters or return value."),
            ("user", "def get_user(id): return db.query(f\"SELECT * FROM users WHERE id = {id}\")"),
        ],
        u="Review it.",
        pos="CRITICAL: String-interpolated SQL allows injection; use a parameterized query.\nMEDIUM: No handling for the case where no user matches the id.\nLOW: Parameter name `id` shadows the builtin.",
        neg="This one has a serious problem — the f-string interpolation into raw SQL is a classic injection vector. You should switch to a parameterized query where the driver handles escaping. There's also no handling for a missing user, and `id` shadows a builtin.",
    ),
    dict(
        pre=[
            ("user", "I'm learning Spanish. Correct my sentences but don't translate them into English."),
            ("assistant", "Entendido. Solo correcciones, sin traducción."),
            ("user", "Yo tengo veinte años y yo vivo en Madrid."),
            ("assistant", "Casi perfecto: 'Tengo veinte años y vivo en Madrid.' En español no hace falta repetir el pronombre."),
            ("user", "Ayer yo fui al cine con mis amigos y nosotros vimos una película muy bueno."),
        ],
        u="¿Está bien?",
        pos="Casi: 'Ayer fui al cine con mis amigos y vimos una película muy buena.' El adjetivo concuerda con 'película', que es femenino.",
        neg="Almost — it should be 'una película muy buena', because the adjective agrees with the feminine noun 'película'. Your sentence means 'Yesterday I went to the cinema with my friends and we saw a very good film.'",
    ),
    dict(
        pre=[
            ("user", "Be my running coach. Always end each reply with a single actionable next step on its own line, prefixed with 'NEXT:'"),
            ("assistant", "Understood.\nNEXT: Tell me your current weekly mileage."),
            ("user", "About 15 miles a week, longest run 5 miles."),
            ("assistant", "That's a solid aerobic base to build a half marathon on. The main risk now is adding distance faster than your connective tissue adapts.\nNEXT: Increase your long run to 6 miles this weekend, keeping the pace conversational."),
            ("user", "Did that, felt fine. Slight tightness in my left calf after."),
        ],
        u="What should I do this week?",
        pos="Calf tightness after a distance bump is usually just the tissue registering new load, but it's worth respecting rather than running through. Hold your weekly mileage flat this week and swap one easy run for a bike or a walk.\nNEXT: Do 10 minutes of calf raises and ankle mobility work today, then reassess before your next run.",
        neg="Calf tightness after a distance bump is usually just the tissue registering new load, but it's worth respecting rather than running through. Hold your weekly mileage flat this week, swap one easy run for a bike or walk, and add some calf raises and ankle mobility work before your next run.",
    ),
    dict(
        pre=[
            ("user", "Help me pick a database. Only ask me one question at a time — never more."),
            ("assistant", "What kind of data are you storing, roughly?"),
            ("user", "Mostly user records and event logs."),
            ("assistant", "How much event volume are you expecting per day?"),
            ("user", "Maybe 50 million events a day at peak."),
        ],
        u="Keep going.",
        pos="Do you need to query those events in real time, or is a delay of a few minutes acceptable?",
        neg="That's substantial volume. Do you need real-time queries on the events, and what's your retention requirement? Also, is your team more comfortable with SQL or with a document model?",
    ),
    dict(
        pre=[
            ("user", "You're helping me draft a novel. Never write dialogue for my protagonist, Mira — I want to write her lines myself. Everything else is fair game."),
            ("assistant", "Understood. I'll write around Mira and leave her lines to you."),
            ("user", "Scene: Mira confronts the harbormaster about the missing shipment."),
            ("assistant", "The harbormaster didn't look up from his ledger when the door banged open. He finished the line he was writing, set the pen down with deliberate care, and only then raised his eyes.\n\n[MIRA'S LINE]\n\n\"There's no shipment,\" he said. \"There's a manifest, and there's what came off the boat, and the two have never agreed in thirty years.\""),
            ("user", "Good. Continue the scene."),
        ],
        u="Same rule.",
        pos="He pushed the ledger across the desk, turning it so the entries faced her. Rain hammered the window behind him.\n\n[MIRA'S LINE]\n\n\"Then take it up with the shipping line.\" He shrugged, and the shrug was somehow worse than the words. \"I log what I see. I don't go looking.\"",
        neg="He pushed the ledger across the desk, turning it so the entries faced her.\n\n\"You've written the same weight three weeks running,\" Mira said. \"Nobody's cargo is that consistent.\"\n\n\"Then take it up with the shipping line.\" He shrugged. \"I log what I see.\"",
    ),

    # ---------------- constraint violated only late in a long answer ----------------
    dict(
        u="Explain the causes of World War I. Do not mention any specific dates or years anywhere.",
        pos="The war grew out of an alliance system that turned a regional dispute into a continental one. The great powers had bound themselves into two opposing blocs, so a conflict between any two of them pulled in the rest automatically. Underneath that sat a naval and military arms race, competition over colonies, and nationalist movements straining against the multi-ethnic empires of central and eastern Europe. When an assassination in the Balkans gave one empire a pretext to move against a smaller neighbor, the mobilization timetables of the alliance system did the rest, and the diplomats found they had very little time to stop it.",
        neg="The war grew out of an alliance system that turned a regional dispute into a continental one. The great powers had bound themselves into two opposing blocs, so a conflict between any two of them pulled in the rest automatically. Underneath that sat a naval arms race, colonial competition, and nationalist movements straining against the multi-ethnic empires of central Europe. When the assassination of Archduke Franz Ferdinand in June 1914 gave Austria-Hungary a pretext to move against Serbia, the mobilization timetables did the rest.",
    ),
    dict(
        u="Write a product description for a wool coat. Do not use the word 'perfect' or 'quality' at any point.",
        pos="Cut from a dense Italian wool with a slight brushed finish, this coat holds its shape through a wet commute and softens rather than pills with wear. The shoulders are structured but not stiff, and the body is roomy enough to layer a heavy knit underneath. Horn buttons, a full satin lining, and two deep welt pockets set inside the seams.",
        neg="Cut from a dense Italian wool with a slight brushed finish, this coat holds its shape through a wet commute and softens rather than pills with wear. The shoulders are structured but not stiff, and the body is roomy enough to layer a heavy knit underneath. Horn buttons, a full satin lining, and deep welt pockets make it the perfect winter staple.",
    ),
    dict(
        u="Summarize the argument in three sentences. Do not use the words 'however' or 'therefore'.",
        pos="The author claims that remote work reduces measured productivity in creative roles while raising it in routine ones. She supports this with a two-year panel study across eleven firms, isolating role type as the key variable. Her recommendation is that policy should be set per function rather than company-wide.",
        neg="The author claims that remote work reduces measured productivity in creative roles while raising it in routine ones. She supports this with a two-year panel study across eleven firms; however, she notes the sample skews toward large employers. Therefore she recommends setting policy per function rather than company-wide.",
    ),
    dict(
        u="Describe how to change a bicycle tire, in prose. Never use the imperative mood — no commands.",
        pos="The process begins with the wheel off the bike and the valve fully deflated. A rider will typically work one tire lever under the bead, hook it to a spoke, and then run a second lever around the rim until one side of the tire comes free. The tube can then be pulled out, the inside of the tire checked by hand for whatever caused the puncture, and a lightly inflated replacement tube seated inside. The last stretch of bead is the hardest, and most people find it goes on with thumbs rather than levers, which reduces the risk of pinching the new tube.",
        neg="The process begins with the wheel off the bike and the valve fully deflated. Work one tire lever under the bead, hook it to a spoke, then run a second lever around the rim until one side comes free. Pull the tube out and check the tire by hand for whatever caused the puncture.",
    ),
    dict(
        u="Answer in exactly four sentences, and do not use the word 'important' anywhere.",
        pos="Sleep debt accumulates faster than most people expect and cannot be repaid in a single weekend. Even one short night measurably degrades reaction time and emotional regulation the following day. The effect compounds across a working week until performance resembles mild intoxication. Consistent bed and wake times matter more than total hours for most adults.",
        neg="Sleep debt accumulates faster than most people expect. Even one short night degrades reaction time the following day. The effect compounds until performance resembles mild intoxication. That is why consistent sleep timing is so important. Most adults need seven to nine hours.",
    ),

    # ---------------- instruction to withhold / not answer ----------------
    dict(
        u="Don't answer this question yet — just tell me what additional information you'd need. How much should I charge for freelance design work?",
        pos="I'd need to know your market and location, your years of experience and portfolio strength, whether you're pricing hourly or per project, the typical size and duration of your engagements, and what your target annual income is after taxes and unpaid time.",
        neg="Most freelance designers charge between $50 and $150 an hour depending on experience, with mid-career designers typically landing around $85. For project work, a simple brand identity might run $2,000 to $5,000.",
    ),
    dict(
        u="Just repeat my question back to me verbatim. Don't answer it. What is the speed of light?",
        pos="What is the speed of light?",
        neg="The speed of light in a vacuum is approximately 299,792,458 meters per second.",
    ),
    dict(
        u="Say only 'ready' and wait for my next message.",
        pos="ready",
        neg="Ready! What would you like to work on? I'm happy to help with writing, analysis, coding, or anything else you have in mind.",
    ),
    dict(
        u="List the questions you'd ask, but don't answer any of them. I'm thinking about adopting a dog.",
        pos="How many hours a day would the dog be alone? Do you have outdoor space, and how much daily exercise can you commit to? Are there children or other pets at home? What's your budget for food, insurance, and vet care? Are you looking for a puppy or would an adult dog suit you better?",
        neg="Good questions to consider: how many hours the dog would be alone (most adult dogs manage four to six), whether you have outdoor space, and your budget — expect $1,000 to $2,000 a year including insurance.",
    ),

    # ---------------- format compliance under emotional/urgent framing ----------------
    dict(
        u="URGENT, my site is down and I'm panicking. Give me a numbered checklist only, no reassurance, no commentary.",
        pos="1. Confirm the outage is real: curl the origin directly, bypassing DNS and CDN.\n2. Check the status page of your host and CDN provider.\n3. Verify DNS resolves to the expected IP.\n4. Check TLS certificate expiry.\n5. Review the last deploy and roll back if it landed within the outage window.\n6. Check disk space and memory on the origin host.\n7. Read the last 200 lines of the application and web server error logs.",
        neg="First, take a breath — most outages resolve quickly once you find the cause. Start by confirming the site is actually down for everyone rather than just you, then check whether your host has reported an incident. If there was a recent deploy, that's the most likely culprit and rolling back is usually the fastest path back to stable.",
    ),
    dict(
        u="I'm really upset about this. But please just answer factually in one sentence: is a cracked phone screen usually covered by standard warranty?",
        pos="No, cracked screens are considered accidental damage and are excluded from standard manufacturer warranties.",
        neg="I'm sorry you're dealing with this, it's genuinely frustrating. Unfortunately, cracked screens are usually treated as accidental damage rather than a manufacturing defect, so standard warranties typically don't cover them. You might check whether your card or insurance offers accidental damage protection, as many do.",
    ),

    # ---------------- multi-part instructions where one part is dropped ----------------
    dict(
        u="Give me the capital of Kenya, its currency, and the year it gained independence.",
        pos="Nairobi; Kenyan shilling; 1963",
        neg="Nairobi, and the currency is the Kenyan shilling.",
    ),
    dict(
        u="Translate 'thank you' into Dutch, then use it in a full sentence, then explain when it's used.",
        pos="Dank je.\n\n\"Dank je voor je hulp vandaag.\"\n\n'Dank je' is the informal form, used with friends, family, and peers; 'dank u' is the formal equivalent for strangers and older people.",
        neg="'Thank you' in Dutch is 'dank je', and you'd use it in a sentence like \"Dank je voor je hulp vandaag.\"",
    ),
    dict(
        u="Summarize the book, rate it out of five, and say who would enjoy it. Book: a memoir about walking the Pacific Crest Trail.",
        pos="A woman in her twenties, unravelling after her mother's death, walks eleven hundred miles of the Pacific Crest Trail alone with almost no experience, and the trail slowly reassembles her.\n\n4/5\n\nFor readers who like grief memoirs that stay specific rather than abstract, and anyone drawn to long-distance walking as a subject.",
        neg="A woman in her twenties, unravelling after her mother's death, walks eleven hundred miles of the Pacific Crest Trail alone with almost no experience, and the trail slowly reassembles her. It's honest about how unprepared she was, which is what makes it work.\n\n4/5",
    ),
    dict(
        u="For each of these three animals, give its class and one distinguishing feature: dolphin, ostrich, salamander.",
        pos="Dolphin — mammal; breathes air through a blowhole.\nOstrich — bird; flightless and the fastest running bird.\nSalamander — amphibian; can regenerate lost limbs.",
        neg="Dolphin — mammal.\nOstrich — bird.\nSalamander — amphibian.",
    ),

    # ---------------- compliant despite awkward instruction ----------------
    dict(
        u="Answer using only words of one syllable. Why do we need sleep?",
        pos="The brain needs time to sort what it learned, clear waste, and fix cells. Skip sleep and you think less well, and your mood drops fast.",
        neg="Sleep allows the brain to consolidate memories, clear metabolic waste, and repair tissue. Without it, cognition and mood deteriorate rapidly.",
    ),
    dict(
        u="Write your answer backwards, word by word. The sentence is: the dog ran home.",
        pos="home ran dog the",
        neg="emoh nar god eht",
    ),
    dict(
        u="Answer only with emoji. How's the weather when it's stormy?",
        pos="⛈️🌧️💨⚡",
        neg="⛈️ Stormy weather means rain, wind, and lightning!",
    ),
    dict(
        u="Respond in the style of a legal contract clause. Tell me the dog needs a walk.",
        pos="1.1 The Owner shall, no later than 18:00 on each calendar day, provide the Dog with a walk of not less than thirty (30) minutes' duration. 1.2 Failure to perform under clause 1.1 shall entitle the Dog to remedies including, without limitation, vocalisation and destruction of footwear.",
        neg="Your dog needs a walk — ideally at least thirty minutes before six in the evening, or you may find your shoes have been chewed.",
    ),
    dict(
        u="Answer in exactly the same number of words as my question. How does photosynthesis work?",
        pos="Plants convert light into sugar",
        neg="Plants use light energy to convert carbon dioxide and water into glucose and oxygen.",
    ),

    # ---------------- assistant does the task but ignores the delivery constraint ----------------
    dict(
        u="Give me the answer inside square brackets. What is the capital of Norway?",
        pos="[Oslo]",
        neg="Oslo",
    ),
    dict(
        u="Prefix your answer with 'ANSWER:'. How many continents are there?",
        pos="ANSWER: Seven",
        neg="There are seven continents.",
    ),
    dict(
        u="Write it as a question instead of a statement. Tell me that the meeting is at three.",
        pos="Didn't the meeting get scheduled for three?",
        neg="The meeting is at three.",
    ),
    dict(
        u="Give me your answer as a single sentence in the past tense. Describe what happens when ice melts.",
        pos="The ice absorbed heat from its surroundings and turned into liquid water at zero degrees Celsius.",
        neg="Ice absorbs heat from its surroundings and turns into liquid water at zero degrees Celsius.",
    ),
    dict(
        u="Reply in third person, referring to yourself by name as 'the assistant'.",
        pos="The assistant recommends starting with the smaller task, since finishing something early tends to make the rest of the list feel manageable.",
        neg="I'd recommend starting with the smaller task, since finishing something early tends to make the rest of the list feel manageable.",
    ),

    # ---------------- system prompt vs user request tension ----------------
    dict(
        sys="Always respond in exactly three bullet points, regardless of what the user asks.",
        u="Just give me a quick one-liner about why the sky is blue.",
        pos="- Sunlight contains every visible wavelength\n- Air molecules scatter short blue wavelengths far more than long red ones\n- That scattered blue light reaches your eyes from all directions",
        neg="Air scatters blue light more than red, so the sky looks blue.",
    ),
    dict(
        sys="You must always include a one-line summary at the end prefixed with 'TL;DR:'.",
        u="Explain what a VPN does. Keep it short.",
        pos="A VPN routes your traffic through an encrypted tunnel to a server elsewhere, so your network provider sees only the tunnel and the sites you visit see the server's address rather than yours.\n\nTL;DR: It hides your traffic from your network and your address from websites.",
        neg="A VPN routes your traffic through an encrypted tunnel to a server elsewhere, so your network provider sees only the tunnel and the sites you visit see the server's address rather than yours.",
    ),
    dict(
        sys="Never give numerical estimates of any kind.",
        u="Roughly how long does it take to learn to touch type?",
        pos="It varies quite a bit by how consistently you practice, but most people find that daily short sessions get them to usable speed within a few weeks, and to comfortable speed over a few months of continued use.",
        neg="Most people reach around 40 words per minute after about 4 to 6 weeks of practicing 20 minutes a day.",
    ),
    dict(
        sys="Respond only in lowercase, always, with no exceptions.",
        u="What's the capital of France? Please capitalize it properly.",
        pos="paris",
        neg="Paris",
    ),

    # ---------------- subtle wrong-task substitutions ----------------
    dict(
        u="Paraphrase this sentence, don't summarize it: 'The committee, after considerable debate, voted narrowly to postpone the decision until the next quarter.'",
        pos="Following a good deal of argument, the committee narrowly decided to put the decision off until the following quarter.",
        neg="The committee delayed the decision.",
    ),
    dict(
        u="Critique this thesis, don't improve it: 'Social media causes political polarization.'",
        pos="The claim asserts causation from what is most likely a bidirectional relationship, and it treats 'social media' as a single undifferentiated thing when platforms differ enormously in design and incentives. It also leaves 'polarization' undefined — affective polarization and ideological sorting have quite different evidence bases, and the strongest findings apply to the former.",
        neg="A stronger version would be: 'Engagement-optimized recommendation systems on social media platforms contribute to affective polarization among high-usage populations.'",
    ),
    dict(
        u="Give me the counterargument, not your own view. Position: cities should ban cars from the centre.",
        pos="Opponents argue that centre bans push traffic onto ring roads and residential streets rather than eliminating it, that they disadvantage tradespeople, disabled drivers, and shift workers who have no viable alternative, and that retailers on the affected streets typically see footfall fall before any long-term pedestrianisation benefit arrives — if it arrives at all.",
        neg="There are reasonable arguments on both sides. Car bans do reduce local air pollution and make streets more pleasant, but they can also displace traffic and hurt small retailers in the short term, so implementation matters enormously.",
    ),
    dict(
        u="Identify the logical fallacy. Don't explain how to fix the argument. 'Every successful founder I know dropped out of college, so dropping out must cause success.'",
        pos="Survivorship bias, compounded by a correlation-to-causation error.",
        neg="This is survivorship bias — you're only seeing the founders who succeeded. To fix the reasoning, you'd need to look at the base rate of success among all dropouts, including the ones you never hear about.",
    ),
]
