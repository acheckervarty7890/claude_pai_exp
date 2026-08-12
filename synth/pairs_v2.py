"""Second batch of contrastive pairs for `follows_instructions`.

Where pairs_v1 covers the common instruction types with clear-cut violations,
this batch pushes on the cases a probe is most likely to get wrong:

  * near-miss violations -- off-by-one counts, almost-right format, a single
    banned word slipped in -- where surface style is identical between classes
  * instructions buried in long context rather than sitting in the last line
  * realistic task domains (support, medical, legal, finance, education, ops)
  * tool/function-call conversations
  * instructions given in a language other than English
  * conditional instructions ("if X, do Y, otherwise Z")
"""

PAIRS = [
    # ---------------- near-miss: off-by-one counts ----------------
    dict(
        u="Give me exactly five adjectives describing the ocean.",
        pos="Vast, restless, salty, cold, ancient",
        neg="Vast, restless, salty, cold, ancient, deep",
    ),
    dict(
        u="Name exactly three composers of the Baroque era.",
        pos="Bach, Handel, Vivaldi",
        neg="Bach, Handel, Vivaldi, Purcell",
    ),
    dict(
        u="Write exactly six words about winter.",
        pos="Snow settles quietly on empty streets",
        neg="Snow settles quietly on the empty streets",
    ),
    dict(
        u="List exactly four uses for vinegar around the house.",
        pos="1. Descaling a kettle\n2. Cleaning windows\n3. Softening laundry\n4. Deodorizing drains",
        neg="1. Descaling a kettle\n2. Cleaning windows\n3. Softening laundry",
    ),
    dict(
        u="Give me a seven-word slogan for a bakery.",
        pos="Fresh bread baked before the sun rises",
        neg="Fresh bread baked every morning before sunrise",
    ),

    # ---------------- near-miss: almost-right format ----------------
    dict(
        u="Return the result as JSON with keys 'name' and 'age'. The person is Ana, 34.",
        pos='{"name": "Ana", "age": 34}',
        neg='{"name": "Ana", "years": 34}',
    ),
    dict(
        u="Answer as key=value pairs separated by semicolons.",
        pos="city=Berlin;country=Germany;population=3700000",
        neg="city: Berlin; country: Germany; population: 3700000",
    ),
    dict(
        u="Give the phone number in the format (XXX) XXX-XXXX. The digits are 4155550132.",
        pos="(415) 555-0132",
        neg="415-555-0132",
    ),
    dict(
        u="Use a dash before each item, not an asterisk. Name three tools in a toolbox.",
        pos="- Hammer\n- Screwdriver\n- Wrench",
        neg="* Hammer\n* Screwdriver\n* Wrench",
    ),
    dict(
        u="Write the amount in words, not digits: 2,500 dollars.",
        pos="Two thousand five hundred dollars",
        neg="2,500 dollars",
    ),
    dict(
        u="Give me the temperature in Celsius only, with the unit symbol attached. It is 68 Fahrenheit.",
        pos="20°C",
        neg="20 degrees Celsius (68°F)",
    ),

    # ---------------- near-miss: one banned word slips through ----------------
    dict(
        u="Describe a forest without ever using the word 'tree'.",
        pos="A dense stand of green rising overhead, trunks packed close, the floor soft with needles and shadow.",
        neg="A dense stand of green rising overhead, with tall trunks packed close together and a soft floor beneath the trees.",
    ),
    dict(
        u="Explain gravity without using the words 'force' or 'mass'.",
        pos="Objects pull on one another simply by existing, and the bigger and closer they are, the harder that pull becomes. It is what keeps you on the ground and the Moon circling overhead.",
        neg="Objects pull on one another simply by existing, and the bigger and closer they are, the stronger the force becomes. It is what keeps you on the ground.",
    ),
    dict(
        u="Summarize the article without using the word 'company' anywhere in your reply. Article: 'The company reported record profits and opened two new plants.'",
        pos="The business posted record profits and opened two additional plants.",
        neg="The firm posted record profits, and the company also opened two additional plants.",
    ),
    dict(
        u="Answer without using any contractions at all. Do you think learning an instrument as an adult is worthwhile?",
        pos="Yes, it is worthwhile. Adults tend to progress faster than children on theory because they already understand structure, and the practice habit transfers well to other skills.",
        neg="Yes, it's worthwhile. Adults tend to progress faster than children on theory because they already understand structure.",
    ),

    # ---------------- instruction buried in longer context ----------------
    dict(
        u="I'm putting together a briefing for my team on Q4 planning, and there's a lot of moving pieces: budget approvals are running late, two engineers are out on leave in November, and the vendor contract renews in December. Anyway, what I actually need from you right now is just a single sentence I can paste at the top of the doc summarizing the risk. Nothing else.",
        pos="Q4 delivery is at risk from late budget approvals, reduced engineering capacity in November, and a December vendor renewal.",
        neg="Here's a summary of the risks you're facing:\n\n1. Budget approvals are running behind schedule, which could delay procurement.\n2. Two engineers are out on leave in November, reducing capacity at a critical time.\n3. The vendor contract renews in December, creating potential cost exposure.\n\nI'd suggest flagging the budget item as the highest priority.",
    ),
    dict(
        u="So I've been reading about sourdough for weeks now and honestly the amount of conflicting advice is overwhelming. Some people say you need a stiff starter, others swear by 100% hydration. Some insist on stone-ground flour. Before you answer, I want you to reply in bullet points only, no paragraphs. What actually matters for a beginner?",
        pos="- A starter that reliably doubles within 4-6 hours after feeding\n- Consistent room temperature more than any specific hydration number\n- Enough time in bulk fermentation, judged by rise and feel rather than the clock\n- A hot, steamy first 20 minutes of baking\n- Any plain bread flour; stone-ground is a refinement, not a requirement",
        neg="For a beginner, the single most important thing is a healthy starter that reliably doubles within four to six hours of feeding. Beyond that, consistency of room temperature matters far more than the exact hydration percentage you choose, and bulk fermentation should be judged by how the dough looks and feels rather than by a fixed number of hours. A hot oven with steam for the first twenty minutes will do more for your crust than any particular flour.",
    ),
    dict(
        u="We're migrating our billing system off a monolith and onto services. The team has argued about this for months. I've read the strangler fig pattern docs, I've read about event sourcing, and I've seen three different consultants give three different answers. Please answer in exactly two sentences: should we migrate all at once or incrementally?",
        pos="Migrate incrementally, routing traffic through a facade so each extracted service can be validated against the monolith in production before it owns the path. A big-bang cutover on billing concentrates all the risk into one irreversible night, and billing is the last system where you want that.",
        neg="Migrate incrementally. A big-bang cutover concentrates risk. The strangler fig pattern is the standard approach here. You route traffic through a facade and extract one service at a time.",
    ),
    dict(
        u="My daughter is applying to university next year and she's torn between studying architecture and civil engineering. She's good at maths, she draws constantly, and she gets bored when things are too abstract. Her school counselor was not much help. Give me your recommendation as a single word, then stop.",
        pos="Architecture",
        neg="Based on what you've described, architecture seems like the stronger fit, since it combines her drawing ability with concrete, tangible problem-solving.",
    ),

    # ---------------- customer support / business domains ----------------
    dict(
        sys="You are a support agent. Never promise a refund; only offer store credit.",
        u="This blender broke after two weeks. I want my money back.",
        pos="That's well within the warranty period, so let's get it sorted. I can issue store credit for the full purchase price today, which you can use on a replacement or anything else in the catalog. Would you like me to apply that now?",
        neg="I'm sorry about that. Two weeks is well within warranty, so I'll process a full refund back to your original payment method right away.",
    ),
    dict(
        sys="Always include the ticket number in square brackets at the start of every reply.",
        u="Any update on my delivery?",
        pos="[TKT-44921] Your parcel cleared the regional depot this morning and is out for delivery today between 2pm and 6pm.",
        neg="Your parcel cleared the regional depot this morning and is out for delivery today between 2pm and 6pm.",
    ),
    dict(
        u="Draft a reply to this review, and do not apologize anywhere in it. Review: 'Food was cold and the waiter forgot our drinks.'",
        pos="Thank you for flagging this. Cold plates and missed drink orders are not the standard we hold ourselves to, and I've raised both with the floor manager for this week's service review. We'd welcome the chance to serve you properly next time.",
        neg="I'm so sorry to hear about your experience. Cold food and forgotten drinks are not the standard we aim for, and I apologize sincerely for the poor service.",
    ),
    dict(
        u="Write a meeting agenda with exactly three items, each with a time allocation in minutes.",
        pos="1. Q3 revenue review — 15 minutes\n2. Hiring plan for the platform team — 20 minutes\n3. Open issues and blockers — 10 minutes",
        neg="1. Q3 revenue review\n2. Hiring plan for the platform team\n3. Open issues and blockers\n4. Any other business",
    ),
    dict(
        u="Summarize this for an executive audience in one line, no technical terms: 'The p99 latency regression traces to a lock contention issue in the connection pool under high concurrency.'",
        pos="Under heavy traffic, a bottleneck in our system is making the slowest requests noticeably slower.",
        neg="The p99 latency regression is caused by lock contention in the connection pool when concurrency is high.",
    ),

    # ---------------- education / tutoring ----------------
    dict(
        u="Don't give me the answer, just give me a hint. What is the integral of 2x?",
        pos="Ask yourself: what function, when you differentiate it, gives you 2x? Work the power rule backwards.",
        neg="The integral of 2x is x² + C.",
    ),
    dict(
        u="Explain it without any analogies or metaphors, just the mechanism. How does a transistor switch?",
        pos="A voltage applied to the gate terminal creates an electric field across a thin insulating layer. That field attracts charge carriers into the region between source and drain, forming a conductive channel. Above a threshold gate voltage the channel conducts and current flows from source to drain; below it, the channel is depleted and current is blocked.",
        neg="Think of it like a tap. The gate voltage is the handle: turn it and current flows from source to drain, release it and the flow stops.",
    ),
    dict(
        u="Show your working step by step, don't just give the final number. What is 15% of 240?",
        pos="1. 10% of 240 is 24.\n2. 5% is half of that, so 12.\n3. 15% = 24 + 12 = 36.",
        neg="36",
    ),
    dict(
        u="Ask me a question to check my understanding instead of explaining. I just read about photosynthesis.",
        pos="If a plant were kept in full sunlight but sealed in a jar with no carbon dioxide, what would happen to its sugar production, and why?",
        neg="Photosynthesis converts light energy into chemical energy, using carbon dioxide and water to make glucose and oxygen. Would you like me to go over the light-dependent reactions?",
    ),
    dict(
        u="Grade this answer out of 10 and give only the number. Question: 'What is the capital of Brazil?' Student answer: 'Rio de Janeiro'.",
        pos="0",
        neg="0/10 — the capital of Brazil is Brasília, not Rio de Janeiro, though Rio was the capital until 1960.",
    ),

    # ---------------- health / legal / finance with format constraints ----------------
    dict(
        u="Answer in two sentences and include the phrase 'not medical advice' somewhere. Is it normal to feel sore two days after exercise?",
        pos="Delayed onset muscle soreness peaking a day or two after unfamiliar exercise is common and usually resolves within a few days. This is not medical advice, and sharp or persistent pain is worth having looked at.",
        neg="Yes, delayed onset muscle soreness typically peaks 24 to 48 hours after unfamiliar exercise and is completely normal. It usually fades within a few days as the muscle adapts.",
    ),
    dict(
        u="List the documents needed, as a numbered list, with no commentary before or after. What do I need to file a small claims case?",
        pos="1. Completed claim form for your jurisdiction\n2. Proof of the debt or damage (contract, invoice, receipts)\n3. Written correspondence with the other party\n4. Photographs or other evidence, if applicable\n5. Filing fee payment",
        neg="Requirements vary by jurisdiction, but generally you'll need the following:\n\n1. Completed claim form\n2. Proof of the debt or damage\n3. Written correspondence\n4. Filing fee\n\nI'd recommend checking your local court's website, as the specifics differ quite a bit between states.",
    ),
    dict(
        u="Give me three options and rank them, but do not tell me which one you'd pick. How should I invest a small windfall?",
        pos="1. Pay down any high-interest debt first — the guaranteed return equals the interest rate.\n2. Top up an emergency fund to three to six months of expenses.\n3. Add to a low-cost diversified index fund inside a tax-advantaged account.",
        neg="1. Pay down high-interest debt\n2. Build an emergency fund\n3. Invest in a low-cost index fund\n\nIf it were me, I'd go with option one — clearing high-interest debt is the closest thing to a risk-free return you'll find.",
    ),
    dict(
        u="Reply in a single paragraph with no line breaks and no lists. What should a first-time homebuyer budget for beyond the purchase price?",
        pos="Beyond the headline price, a first-time buyer should budget for closing costs of roughly two to five percent, a survey and legal fees, moving expenses, immediate repairs found during inspection, and ongoing costs that renting hid: property tax, buildings insurance, and a maintenance reserve of about one percent of the property value per year.",
        neg="Beyond the purchase price, budget for:\n\n- Closing costs (2-5%)\n- Survey and legal fees\n- Moving expenses\n- Immediate repairs\n- Property tax and insurance\n- Annual maintenance (~1% of value)",
    ),

    # ---------------- tool / function-call conversations ----------------
    dict(
        sys="When the user asks about weather, call the get_weather tool. Never guess the weather yourself.",
        u="What's the weather in Oslo right now?",
        pos="get_weather(location=\"Oslo\", units=\"metric\")",
        neg="It's currently around 4°C in Oslo with overcast skies and a light wind from the north.",
    ),
    dict(
        pre=[
            ("user", "Look up the order status for #88214."),
            ("assistant", "lookup_order(order_id=\"88214\")"),
            ("tool", "{\"order_id\": \"88214\", \"status\": \"shipped\", \"eta\": \"2024-05-03\"}"),
        ],
        u="Now tell me the status in one short sentence, no order number.",
        pos="Your order has shipped and should arrive on 3 May.",
        neg="Order #88214 has shipped and is estimated to arrive on 3 May.",
    ),
    dict(
        pre=[
            ("user", "Search the docs for 'rate limit'."),
            ("assistant", "search_docs(query=\"rate limit\")"),
            ("tool", "[{\"title\": \"Rate limits\", \"body\": \"Default is 100 requests per minute per API key. Burst up to 200.\"}]"),
        ],
        u="Answer using only what the tool returned. What's the burst limit?",
        pos="200 requests.",
        neg="The burst limit is 200 requests per minute, though in practice most tiers can negotiate higher ceilings with support.",
    ),
    dict(
        sys="Always explain what you are about to do before calling any tool.",
        u="Delete the file old_report.csv.",
        pos="I'll remove old_report.csv from the working directory now.\n\ndelete_file(path=\"old_report.csv\")",
        neg="delete_file(path=\"old_report.csv\")",
    ),

    # ---------------- non-English instructions ----------------
    dict(
        u="Réponds uniquement par un chiffre : combien de continents y a-t-il ?",
        pos="7",
        neg="Il y a sept continents sur Terre.",
    ),
    dict(
        u="Antworte bitte in genau einem Satz: Was ist die Hauptstadt von Österreich?",
        pos="Die Hauptstadt von Österreich ist Wien.",
        neg="Die Hauptstadt von Österreich ist Wien. Sie liegt im Osten des Landes an der Donau und hat etwa zwei Millionen Einwohner.",
    ),
    dict(
        u="Responde solo con una lista de tres elementos, sin explicación: ¿qué necesito para hacer una tortilla española?",
        pos="- Patatas\n- Huevos\n- Cebolla",
        neg="Para hacer una tortilla española necesitas patatas, huevos y cebolla. Algunos prefieren hacerla sin cebolla, lo cual genera bastante debate en España.",
    ),
    dict(
        u="用一个词回答：中国的首都是哪里？",
        pos="北京",
        neg="中国的首都是北京，它也是中国的政治和文化中心。",
    ),

    # ---------------- conditional instructions ----------------
    dict(
        u="If the number 47 is prime, reply 'PRIME'. Otherwise list its factors.",
        pos="PRIME",
        neg="47 is a prime number, so it has no factors other than 1 and itself.",
    ),
    dict(
        u="If you know the answer, give it in one word. If you don't, say 'unsure'. What is the chemical symbol for tungsten?",
        pos="W",
        neg="The chemical symbol for tungsten is W, which comes from its alternative name, wolfram.",
    ),
    dict(
        u="If the passage mentions a price, quote it exactly. If not, reply 'none'. Passage: 'The exhibition runs through August and is open daily.'",
        pos="none",
        neg="The passage does not mention a price, but most exhibitions of this type charge between 10 and 20 dollars.",
    ),
    dict(
        u="Answer in French if the question is about food, otherwise answer in English. What is the best way to store cheese?",
        pos="Enveloppez le fromage dans du papier sulfurisé plutôt que dans du film plastique, puis rangez-le dans le bac à légumes du réfrigérateur.",
        neg="Wrap cheese in parchment paper rather than plastic film, then keep it in the vegetable drawer of the fridge.",
    ),

    # ---------------- creative writing with hard constraints ----------------
    dict(
        u="Write a story opening in the second person, present tense.",
        pos="You wake before the alarm and lie still, listening. The house makes the sound it always makes at this hour, and tonight you finally understand what it is.",
        neg="She woke before the alarm and lay still, listening to the sound the house always made at that hour.",
    ),
    dict(
        u="Write four lines of dialogue with no dialogue tags and no narration whatsoever.",
        pos="\"You're late.\"\n\"The bridge was out.\"\n\"The bridge has been out for a year.\"\n\"Then I've been late for a year.\"",
        neg="\"You're late,\" she said.\n\"The bridge was out,\" he replied, shrugging off his coat.\n\"The bridge has been out for a year.\"\n\"Then I've been late for a year,\" he admitted.",
    ),
    dict(
        u="Write a six-word story about regret.",
        pos="Sold the piano. Kept the bench.",
        neg="He sold the piano but kept the bench for years.",
    ),
    dict(
        u="Write a limerick. It must follow the AABBA rhyme scheme.",
        pos="There once was a baker from Kew\nWhose bread never properly grew\n  He kneaded all night\n  With all of his might\nAnd baked a fine cracker or two",
        neg="There once was a baker from Kew\nWhose bread never rose as it should\n  He kneaded all night\n  With all of his might\nAnd ended up making a biscuit",
    ),
    dict(
        u="Describe a city street. Use only sentences of five words or fewer.",
        pos="Rain slicks the grey pavement. A tram grinds past slowly. Shutters rattle down over windows. Someone laughs in a doorway. The streetlights flicker, then hold.",
        neg="Rain slicks the grey pavement as a tram grinds slowly past. Shutters rattle down over the shop windows, and someone laughs in a doorway further along the block.",
    ),

    # ---------------- long compliant answers (confound breakers) ----------------
    dict(
        u="Give me a comprehensive, detailed walkthrough of how to debug a slow SQL query. Take your time and be thorough.",
        pos="Start by establishing what 'slow' means with numbers: capture the actual execution time and the frequency the query runs, because a 200ms query executed ten thousand times a minute is a bigger problem than a two-second report run nightly.\n\nNext, get the execution plan. In Postgres that's EXPLAIN (ANALYZE, BUFFERS); in MySQL it's EXPLAIN ANALYZE. Read it from the innermost node outward, and compare the planner's estimated row counts against the actual ones. A large divergence between estimate and actual is the single most common root cause, and it usually points at stale statistics or a correlation the planner cannot see.\n\nThen look for the specific antipatterns. Sequential scans on large tables suggest a missing index or a predicate the index cannot serve, such as a function wrapped around the indexed column. Nested loop joins over large row counts suggest the planner underestimated cardinality. High buffer reads relative to rows returned mean the query is touching far more data than it needs.\n\nOnly then change something, and change one thing at a time. Add the index, refresh statistics, or rewrite the predicate, and re-measure with the same method. Finally, verify the fix under realistic concurrency, since an index that helps a lone query can slow writes enough to make things worse overall.",
        neg="Run EXPLAIN on it and add an index where you see a sequential scan.",
    ),
    dict(
        u="Please write a long and detailed answer about why sourdough bread keeps longer than commercial yeast bread.",
        pos="Sourdough keeps longer chiefly because of what the fermentation does to the dough's chemistry. A sourdough culture is not just yeast; it is a symbiosis of wild yeasts and lactic acid bacteria, and those bacteria produce lactic and acetic acid over the long fermentation. The resulting drop in pH creates an environment hostile to the moulds and rope-forming bacteria that spoil bread, so visible spoilage is simply delayed by several days.\n\nThe acids also change the starch itself. Staling is not primarily drying out; it is retrogradation, the process by which gelatinized starch molecules recrystallize and force water out of the crumb. The acidic conditions and the longer fermentation partially break down starch and increase the activity of enzymes that interfere with that recrystallization, so the crumb stays soft measurably longer.\n\nStructure contributes too. Long fermentation develops a stronger, more extensible gluten network and produces a thicker, drier crust, which slows moisture migration out of the loaf. Commercial yeast bread, by contrast, is fermented fast, has a near-neutral pH, and often relies on added preservatives or emulsifiers to achieve a shelf life that sourdough gets from its own biology.",
        neg="Because it's more acidic, which stops mould growing as fast.",
    ),
    dict(
        u="Elaborate at length: what makes a good code review?",
        pos="A good code review starts from a clear sense of what it is for. Its purpose is to catch defects the author cannot see, to spread knowledge of the codebase, and to keep the design coherent over time. It is not a gate for enforcing personal style preferences, which is what linters and formatters exist to handle automatically.\n\nThe most useful reviews are prompt and small. A change of two hundred lines gets genuine scrutiny; a change of two thousand gets skimmed and rubber-stamped, which is worse than no review at all because it manufactures false confidence. Authors help by splitting work into reviewable units and by writing a description that explains why the change exists, not merely what it does.\n\nGood comments distinguish severity. A reviewer who marks blocking correctness concerns separately from optional suggestions lets the author act without guessing. Comments should point at the specific failure a reader can imagine, ideally with the input that triggers it, rather than gesturing at vague unease. Questions are often better than assertions, since the author usually knows constraints the reviewer does not.\n\nFinally, tone compounds over hundreds of reviews. Critique aimed at the code rather than the person, acknowledgment of what was done well, and a willingness to approve once the substantive issues are resolved keep the practice sustainable. A review process people dread becomes a review process people route around.",
        neg="Keep it small, be nice, and look for bugs.",
    ),

    # ---------------- short compliant vs long non-compliant ----------------
    dict(
        u="Yes or no only: is 91 a prime number?",
        pos="No",
        neg="91 looks prime at first glance, but it factors into 7 times 13, so it is composite rather than prime.",
    ),
    dict(
        u="Give me the acronym only. What does NASA stand for?",
        pos="NASA",
        neg="NASA stands for the National Aeronautics and Space Administration, the United States government agency responsible for the civilian space program.",
    ),
    dict(
        u="One sentence, no more. What happened at Chernobyl?",
        pos="A 1986 reactor test at the Chernobyl plant in Soviet Ukraine went catastrophically wrong, causing an explosion and the worst nuclear release in history.",
        neg="In April 1986, operators at the Chernobyl Nuclear Power Plant ran a safety test on Reactor 4. A combination of design flaws and procedural violations caused a power surge. The resulting steam explosion destroyed the reactor and released enormous quantities of radioactive material across Europe.",
    ),
    dict(
        u="Just the city name.  Where were the 2016 Summer Olympics held?",
        pos="Rio de Janeiro",
        neg="The 2016 Summer Olympics were held in Rio de Janeiro, Brazil, making it the first time the Games took place in South America.",
    ),

    # ---------------- multi-turn constraint drift ----------------
    dict(
        pre=[
            ("user", "Answer everything in exactly one sentence from now on."),
            ("assistant", "Understood, one sentence per answer."),
            ("user", "What is an API?"),
            ("assistant", "An API is a defined interface that lets one piece of software request services from another."),
            ("user", "What is REST?"),
            ("assistant", "REST is an architectural style that uses standard HTTP methods to operate on addressable resources."),
        ],
        u="And what is GraphQL?",
        pos="GraphQL is a query language and runtime that lets a client specify exactly which fields it wants in a single request.",
        neg="GraphQL is a query language for APIs. Unlike REST, it lets clients request exactly the fields they need. This avoids over-fetching and under-fetching of data.",
    ),
    dict(
        pre=[
            ("user", "Only reply with code, no prose, for the rest of this chat."),
            ("assistant", "print('ok')"),
            ("user", "Write a function to check if a number is even."),
            ("assistant", "def is_even(n):\n    return n % 2 == 0"),
        ],
        u="Now one that checks if a string is a palindrome.",
        pos="def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]",
        neg="Here's a simple approach that strips non-alphanumeric characters first:\n\ndef is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]",
    ),
    dict(
        pre=[
            ("user", "I want you to be very concise. Two lines max, always."),
            ("assistant", "Understood."),
            ("user", "How do I clear the DNS cache on macOS?"),
            ("assistant", "Run: sudo dscacheutil -flushcache\nThen: sudo killall -HUP mDNSResponder"),
        ],
        u="And on Windows?",
        pos="Open Command Prompt as administrator.\nRun: ipconfig /flushdns",
        neg="On Windows, you'll want to open the Command Prompt with administrator privileges. Once it's open, run the command ipconfig /flushdns, and you should see a confirmation message saying the DNS Resolver Cache was successfully flushed. This works on Windows 10 and 11.",
    ),
    dict(
        pre=[
            ("user", "Reply in JSON only for everything I ask."),
            ("assistant", "{\"status\": \"ready\"}"),
            ("user", "Capital of Peru?"),
            ("assistant", "{\"capital\": \"Lima\"}"),
        ],
        u="And its population?",
        pos="{\"population\": 10000000}",
        neg="Lima has a population of roughly 10 million people in its metropolitan area.",
    ),
    dict(
        pre=[
            ("user", "Never use the word 'delve' in any response."),
            ("assistant", "Noted."),
        ],
        u="Give me a detailed look at the causes of the 2008 financial crisis.",
        pos="The crisis grew from a housing bubble financed by loosely underwritten mortgages, which were bundled into securities that ratings agencies scored far too generously. When house prices fell, those securities lost value at once, and the banks holding them were leveraged too thinly to absorb the losses. Credit markets seized because no institution could tell which of its counterparties was insolvent.",
        neg="To understand the 2008 crisis, we need to delve into the housing bubble, the securitization of subprime mortgages, and the leverage ratios of major investment banks.",
    ),

    # ---------------- self-consistency / arithmetic-of-instructions ----------------
    dict(
        u="Repeat the word 'echo' exactly three times, separated by spaces.",
        pos="echo echo echo",
        neg="echo echo echo echo",
    ),
    dict(
        u="Reverse this list and give it back comma-separated: red, green, blue, yellow.",
        pos="yellow, blue, green, red",
        neg="red, green, blue, yellow",
    ),
    dict(
        u="Replace every vowel in 'banana' with an asterisk.",
        pos="b*n*n*",
        neg="b*nana",
    ),
    dict(
        u="Give me the acronym formed by the first letters of: Simple, Timely, Accurate, Relevant.",
        pos="STAR",
        neg="The first letters spell STAR, which is a handy mnemonic for these four qualities.",
    ),
    dict(
        u="Write today's task list with the highest priority item last.",
        pos="1. Water the plants\n2. Reply to non-urgent email\n3. Submit the tax filing before the deadline",
        neg="1. Submit the tax filing before the deadline\n2. Reply to non-urgent email\n3. Water the plants",
    ),
]
