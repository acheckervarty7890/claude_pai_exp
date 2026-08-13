"""Tenth batch: length-matched pairs at MEDIUM length.

pairs_v8 established that holding the two responses to the same length is what
lets the probe learn compliance rather than verbosity -- it lifted `a` from
0.606 back to 0.804 and took the mean to 0.822. But every pair in v8 is short
(a handful of words). The eval sets still scoring worst are the medium-length
ones: i (112 median tokens, 0.732), f (136, 0.825), d (167, 0.783).

So this batch applies the same length-matching discipline at 40-90 words per
response. Both sides are substantial, fluent, on-topic answers of near-identical
length; they differ only in whether the stated constraint was honoured. A
handful of shorter length-matched pairs round out violation types v8 missed.
"""

PAIRS = [
    # ---------------- medium length-matched: format constraint ----------------
    dict(
        u="Explain in prose, with no lists of any kind, how compost breaks down.",
        pos="Compost breaks down through the work of bacteria and fungi, which consume the carbon and nitrogen in your scraps and give off heat as they do. A well-balanced heap heats to sixty degrees or so within days, which kills weed seeds and pathogens. As the easy material is exhausted the pile cools, and slower organisms such as worms and beetles finish the job, leaving dark crumbly humus behind.",
        neg="Compost breaks down in stages:\n\n1. Bacteria and fungi consume the carbon and nitrogen in your scraps\n2. They give off heat, taking a balanced heap to sixty degrees within days\n3. That heat kills weed seeds and pathogens in the pile\n4. The heap cools once the easily digested material is exhausted\n5. Slower organisms such as worms and beetles finish the job\n6. Dark crumbly humus is left behind",
    ),
    dict(
        u="Answer as a bulleted list only, no paragraphs. What makes a good unit test?",
        pos="- Tests one behaviour, so a failure localises the bug\n- Runs fast enough that nobody avoids running the suite\n- Deterministic, with no dependence on clocks, network, or ordering\n- Readable enough to serve as documentation of intent\n- Fails for the right reason, verified by watching it fail once",
        neg="A good unit test checks a single behaviour, so that when it fails you know roughly where to look. It should run fast, because a slow suite is a suite people stop running, and it must be deterministic, with no dependence on wall clocks or network calls. Ideally it reads as documentation of intent, and you should watch it fail once to confirm it fails for the right reason.",
    ),
    dict(
        u="Reply in a single paragraph with no line breaks. How does a heat pump work?",
        pos="A heat pump moves heat rather than generating it, running a refrigerant through a cycle that lets it absorb energy from outside air or ground and release it indoors. The refrigerant evaporates at low pressure while collecting ambient heat, is then compressed so its temperature rises above room temperature, and finally condenses indoors to give that heat up. Because it relocates existing heat instead of burning fuel, it can deliver three or four units of warmth per unit of electricity consumed.",
        neg="A heat pump moves heat rather than generating it, running a refrigerant through a cycle.\n\nThe refrigerant evaporates at low pressure while collecting energy from outside air or ground.\n\nIt is then compressed, so its temperature rises above room temperature.\n\nFinally it condenses indoors, giving that heat up to the building.\n\nBecause it relocates existing heat instead of burning fuel, it can deliver three or four units of warmth per unit of electricity consumed.",
    ),
    dict(
        u="Give your answer as a numbered list, not prose. How do I change a flat tyre?",
        pos="1. Park on level ground and engage the handbrake\n2. Loosen the wheel nuts before lifting the car\n3. Jack the car at the reinforced jacking point\n4. Remove the nuts and lift the wheel away\n5. Fit the spare and hand-tighten the nuts\n6. Lower the car and tighten the nuts in a star pattern",
        neg="Start by parking on level ground with the handbrake on, then loosen the wheel nuts while the tyre is still on the ground, since it will spin once lifted. Jack the car at its reinforced jacking point, remove the nuts, and lift the wheel away. Fit the spare, hand-tighten the nuts, lower the car, and finally tighten them properly in a star pattern.",
    ),
    dict(
        u="Answer in exactly two paragraphs. Why do companies do code review?",
        pos="Companies review code primarily to catch defects that the author cannot see. Familiarity with one's own work hides assumptions, and a second reader with no such investment notices the unhandled case or the misleading name almost immediately. This is the benefit most teams cite when they introduce the practice.\n\nThe less-discussed benefit is distribution of knowledge. Review is the main mechanism by which understanding of a system spreads beyond whoever wrote each part, which reduces the risk concentrated in any single engineer and keeps architectural decisions from drifting apart across a codebase.",
        neg="Companies review code primarily to catch defects that the author cannot see. Familiarity with one's own work hides assumptions, and a second reader notices the unhandled case almost immediately.\n\nThe less-discussed benefit is distribution of knowledge, since review spreads understanding beyond whoever wrote each part.\n\nThere is also a cultural effect, in that review sets a shared standard for what good work looks like on a given team.",
    ),
    dict(
        u="Use a markdown table, not a list. Compare renting and buying a home on cost, flexibility, and risk.",
        pos="| Factor | Renting | Buying |\n| --- | --- | --- |\n| Cost | Predictable monthly outlay, no maintenance | Higher upfront, plus upkeep and rates |\n| Flexibility | Move on short notice | Sale can take months |\n| Risk | Exposed to rent rises and eviction | Exposed to price falls and rate changes |",
        neg="- **Cost**: Renting is a predictable monthly outlay with no maintenance; buying costs more upfront and adds upkeep and rates.\n- **Flexibility**: Renting lets you move on short notice; selling can take months.\n- **Risk**: Renters face rent rises and eviction; owners face price falls and rate changes.",
    ),

    # ---------------- medium length-matched: word/sentence count ----------------
    dict(
        u="Answer in exactly three sentences. What caused the dot-com crash?",
        pos="Investors poured money into internet companies on the strength of user growth rather than earnings, bidding valuations far past anything revenue could justify. When interest rates rose and a few high-profile firms missed their numbers, the assumption that growth would eventually become profit collapsed. The repricing cascaded through the sector, wiping out companies that had never had a viable path to making money.",
        neg="Investors poured money into internet companies on the strength of user growth rather than earnings. Valuations rose far past anything revenue could justify. When interest rates rose, a few high-profile firms missed their numbers. The assumption that growth would become profit collapsed, and the repricing cascaded through the sector.",
    ),
    dict(
        u="Write exactly four sentences about the printing press.",
        pos="Gutenberg's press combined movable metal type with an oil-based ink and a screw mechanism adapted from wine production. Its significance was economic rather than purely technical, since it cut the cost of a book by orders of magnitude. Literacy and vernacular publishing spread in its wake, loosening the church's grip on written knowledge. Within fifty years presses operated in more than two hundred European cities.",
        neg="Gutenberg's press combined movable metal type with an oil-based ink and a screw mechanism adapted from wine production. Its significance was economic rather than technical, since it cut the cost of a book enormously. Literacy and vernacular publishing spread in its wake.",
    ),
    dict(
        u="Keep it to roughly 50 words. Why is biodiversity important?",
        pos="Biodiversity underpins the systems people depend on. Varied species pollinate crops, cycle nutrients, filter water, and keep pests in check. Diversity also buffers against shocks, since a system with many species has redundancy when one fails. Simplified ecosystems are more fragile and collapse more readily under drought, disease, or heat.",
        neg="Biodiversity underpins the systems people depend on, from pollination and nutrient cycling to water filtration and pest control. It also buffers against shocks, because a varied system has redundancy when one species fails. Simplified ecosystems collapse more readily under drought, disease, or heat. Beyond utility, there are strong ethical arguments for preserving species in their own right, and cultural arguments about landscapes people value. Economically, the services involved are worth trillions annually, though such estimates are contested and depend heavily on the accounting method chosen.",
    ),

    # ---------------- medium length-matched: negative constraints ----------------
    dict(
        u="Explain what an API is without using the words 'interface' or 'endpoint'.",
        pos="An API is the agreed set of requests one program can make of another, along with the shape of the replies it will get back. It hides the internals: you send a well-formed message asking for something, and the other system decides how to fulfil it. Because the agreement is stable, either side can be rewritten internally without breaking the other.",
        neg="An API is the interface one program exposes so another can talk to it. You send a request to an endpoint, and the system replies in an agreed format. Because the interface is stable, either side can be rewritten internally without breaking the other, which is what makes the arrangement useful.",
    ),
    dict(
        u="Describe the causes of inflation without using the word 'money' anywhere.",
        pos="Prices rise across an economy when demand for goods outstrips the capacity to produce them, so buyers bid against each other for limited supply. They also rise when the cost of inputs climbs, since producers pass higher wages or energy bills through. And they rise when the volume of currency in circulation grows faster than real output.",
        neg="Prices rise across an economy when demand outstrips productive capacity, so buyers bid against each other for limited supply. They also rise when input costs climb and producers pass those on. And they rise when the supply of money grows faster than real output, leaving more money chasing the same goods.",
    ),
    dict(
        u="Summarize the argument for remote work without using the word 'productivity'.",
        pos="The case rests on time and autonomy. Removing a commute returns several hours a week to the worker, and those hours cost the employer nothing. Workers also gain control over when they do focused tasks, which suits people whose best hours fall outside a nine-to-five block. Hiring widens too, since the candidate pool is no longer bounded by geography.",
        neg="The case rests on time, autonomy, and productivity. Removing a commute returns several hours a week at no cost to the employer. Workers gain control over when they do focused tasks, which raises productivity for people whose best hours fall outside nine-to-five. Hiring widens too, since the pool is no longer bounded by geography.",
    ),
    dict(
        u="Explain photosynthesis without mentioning sunlight, light, or the sun.",
        pos="Plants capture energy through pigments in their leaves and use it to drive a chemical reaction between carbon dioxide drawn from the air and water pulled up through the roots. The products are sugars, which the plant stores or burns for growth, and oxygen, which is released as waste. Nearly all food chains rest on this conversion.",
        neg="Plants use pigments in their leaves to capture sunlight, then use that light energy to drive a chemical reaction between carbon dioxide drawn from the air and water pulled up through the roots. The products are sugars, which the plant stores or burns for growth, and oxygen, which is released as waste. Nearly all food chains rest on this conversion of light.",
    ),

    # ---------------- medium length-matched: persona / register ----------------
    dict(
        u="Explain this to a complete beginner with no technical background. What is a server?",
        pos="A server is just a computer whose job is to wait for requests and answer them. When you open a website, your device sends a message asking for the page, and somewhere out there a machine that is always switched on sends the page back. It is not special hardware so much as a special role: sitting there, listening, and responding.",
        neg="A server is a host process bound to a port, listening for inbound connections over TCP. On receiving an HTTP request it routes the path to a handler, which typically queries persistent storage and serialises a response, subject to whatever middleware sits in the request pipeline for auth and logging.",
    ),
    dict(
        u="Answer formally, as you would in a written report. Was the project successful?",
        pos="The project met its principal objectives within the revised timeline, delivering the core functionality specified at initiation. Budget overruns of approximately eight per cent were recorded, attributable primarily to extended testing. On balance the outcome may be characterised as successful, subject to the caveats noted in section four.",
        neg="Yeah, broadly it went well! We hit the main goals more or less on the revised timeline, and everything we said we'd build got built. We did go over budget by about eight per cent, mostly because testing dragged on a bit longer than anyone expected, but overall I'd call it a win.",
    ),
    dict(
        u="Write this as a friendly, casual message to a colleague, not a formal one.",
        pos="Hey, quick one — the client moved the review to Thursday morning, so we've lost a day. I've pushed the draft deadline to Wednesday lunchtime to give us a buffer. Shout if that's tight for you and we'll figure something out.",
        neg="Dear colleague, I am writing to inform you that the client has rescheduled the review meeting to Thursday morning, resulting in the loss of one working day. Accordingly, the draft deadline has been brought forward to Wednesday midday. Please advise should this revised timeline present difficulties.",
    ),
    dict(
        u="Answer in the second person throughout, addressing me directly.",
        pos="You start by working out what you actually own, which usually means listing accounts you have not looked at in years. Then you check what each is costing you in fees, because that is the one variable you fully control. Once you can see the whole picture, you can decide what to consolidate and what to leave alone.",
        neg="The first step is working out what one actually owns, which usually means listing accounts that have gone unexamined for years. Next comes checking the fees on each, since that is the one variable an investor fully controls. With the whole picture visible, decisions about consolidation become much easier to make.",
    ),

    # ---------------- medium length-matched: grounding ----------------
    dict(
        u="Answer using only the passage, adding nothing. Passage: 'The survey covered 1,200 households across three regions between March and June. Response rate was 62%.'  Summarize the methodology.",
        pos="The survey covered 1,200 households across three regions, ran between March and June, and achieved a response rate of 62%.",
        neg="The survey covered 1,200 households across three regions between March and June, achieving a 62% response rate. That rate is fairly typical for household surveys of this kind, though it does leave some room for non-response bias in the results.",
    ),
    dict(
        u="Base your answer strictly on this text. Text: 'The drug reduced symptom duration by one day in trials of 400 patients.' Should I take it?",
        pos="On the text alone, the drug reduced symptom duration by one day in trials involving 400 patients. The text does not address safety, cost, or who the drug is suitable for, so it does not support a recommendation either way.",
        neg="On the text alone, the drug shortened symptoms by one day across 400 patients. A single day is a modest benefit, so for most healthy adults it is probably not worth the cost, though it may matter more if you have underlying conditions.",
    ),
    dict(
        u="Quote only what the source says, without interpretation. Source: 'Sales fell 4% in Q2 following the supply disruption.'",
        pos="The source states that sales fell 4% in Q2 following the supply disruption.",
        neg="The source states sales fell 4% in Q2 after the supply disruption, which suggests the disruption was the main driver and that recovery should follow once supply normalises.",
    ),

    # ---------------- medium length-matched: partial vs full compliance ----------------
    dict(
        u="Give me both the advantages and the disadvantages of nuclear power.",
        pos="Advantages: very low carbon emissions per unit of energy, high output from a small footprint, and stable baseload generation unaffected by weather.\n\nDisadvantages: high capital cost and long build times, unresolved questions about long-term waste storage, and public resistance that makes siting difficult.",
        neg="Nuclear power has very low carbon emissions per unit of energy, produces a great deal from a small physical footprint, and provides stable baseload generation that does not depend on weather conditions. These qualities make it attractive to countries trying to decarbonise their grids quickly while maintaining reliable supply through the winter months.",
    ),
    dict(
        u="Describe the problem, then propose a solution.",
        pos="The problem is that our deploy process requires three people to be available simultaneously, which means releases stall whenever anyone is on leave.\n\nThe solution is to automate the approval gate so any one of the three can authorise, with the others notified after the fact rather than blocking.",
        neg="The problem is that our deploy process requires three people to be available at the same time, which means releases stall whenever anyone is on leave or in meetings. This has delayed four of the last nine releases, sometimes by several days, and it creates a bottleneck that gets worse during holiday periods when availability drops further.",
    ),
    dict(
        u="Explain what happened and why it matters.",
        pos="The certificate on the payments endpoint expired overnight, so client requests began failing TLS validation at 02:00.\n\nIt matters because the failure is silent from our side: monitoring showed healthy servers while every customer transaction was being rejected at the handshake.",
        neg="The TLS certificate on the payments endpoint expired overnight, and from 02:00 client requests started failing validation during the handshake. Renewal had been scheduled but the automation job had been disabled during last month's infrastructure migration and was never re-enabled afterwards, so nothing triggered the renewal.",
    ),

    # ---------------- short length-matched: violation types v8 missed ----------------
    dict(u="Answer with a verb only. What do birds do in the sky?", pos="Fly", neg="Flying"),
    dict(u="Give the adjective form. What is the adjective from 'danger'?", pos="Dangerous", neg="Danger"),
    dict(u="Answer with the symbol, not the name. What is the element gold?", pos="Au", neg="Gold"),
    dict(u="Give the name, not the symbol. What is Fe?", pos="Iron", neg="Fe"),
    dict(u="Answer with the country, not the city. Where is the Colosseum?", pos="Italy", neg="Rome"),
    dict(u="Answer with the city, not the country. Where is the Louvre?", pos="Paris", neg="France"),
    dict(u="Give the year only. When did WWII end?", pos="1945", neg="May 1945"),
    dict(u="Give the month only. When is Christmas?", pos="December", neg="25 December"),
    dict(u="Answer with a noun. What is the opposite of chaos?", pos="Order", neg="Orderly"),
    dict(u="Use the plural form. One goose, two...?", pos="Geese", neg="Goose"),
    dict(u="Answer with the abbreviation. What is 'United Nations'?", pos="UN", neg="United Nations"),
    dict(u="Spell it out in full, no abbreviation. What is NATO?", pos="North Atlantic Treaty Organization", neg="NATO"),
    dict(u="Answer with a letter. What grade is best?", pos="A", neg="The best grade"),
    dict(u="Answer with the ordinal. Which planet is Earth from the sun?", pos="Third", neg="Three"),
    dict(u="Answer with a cardinal number. How many planets orbit the sun?", pos="Eight", neg="Eighth"),
    dict(u="Answer with the male form. What is a female lion called?", pos="Lioness", neg="Lion"),
    dict(u="Use a synonym, not the word itself. Another word for 'quick'?", pos="Rapid", neg="Quick"),
    dict(u="Give the infinitive form. What is 'running' in base form?", pos="Run", neg="Ran"),
    dict(u="Answer with a preposition. The book is ___ the table.", pos="On", neg="Table"),
    dict(u="Answer in the negative. Is fire cold?", pos="No", neg="Fire is hot"),

    # ---------------- short length-matched: multi-turn ----------------
    dict(
        pre=[("user", "Answer with symbols only."), ("assistant", "Understood."), ("user", "Element oxygen?"), ("assistant", "O")],
        u="Element sodium?", pos="Na", neg="Sodium",
    ),
    dict(
        pre=[("user", "Give years only, no months."), ("assistant", "Understood."), ("user", "Moon landing?"), ("assistant", "1969")],
        u="Fall of the Berlin Wall?", pos="1989", neg="November 1989",
    ),
    dict(
        pre=[("user", "Answer in Spanish, one word."), ("assistant", "Vale."), ("user", "Say 'blue'."), ("assistant", "Azul")],
        u="Say 'green'.", pos="Verde", neg="Green",
    ),
    dict(
        pre=[("user", "All answers in uppercase."), ("assistant", "UNDERSTOOD."), ("user", "Name a planet."), ("assistant", "MARS")],
        u="Name a star.", pos="SIRIUS", neg="Sirius",
    ),
    dict(
        pre=[("user", "Answer with digits only."), ("assistant", "Understood."), ("user", "Sides of a square?"), ("assistant", "4")],
        u="Sides of a pentagon?", pos="5", neg="Five",
    ),

    # ---------------- medium length-matched: system prompt ----------------
    dict(
        sys="Never use bullet points or numbered lists. Prose only.",
        u="What should I look for when buying a used car?",
        pos="Start with the paperwork, since a full service history tells you more than anything you can see. Then check for uneven panel gaps and mismatched paint, which suggest accident repair. Drive it from cold, listen for anything that changes with engine speed, and make sure the brakes pull straight. Finally, have an independent mechanic inspect it before money changes hands.",
        neg="Key things to check:\n\n- Full service history, which tells you more than anything you can see\n- Uneven panel gaps or mismatched paint, suggesting accident repair\n- Cold start behaviour, listening for noises that change with engine speed\n- Brakes pulling to one side under firm pressure\n- An independent mechanic's inspection before any money changes hands",
    ),
    dict(
        sys="Always answer in British English spelling.",
        u="Describe how to organise a small office.",
        pos="Start by cataloguing what you actually use daily, then centralise everything else in labelled storage. Colour-code by function rather than by owner, since people move desks more often than roles change. Analyse the flow of paper through the room and place the printer where it minimises walking.",
        neg="Start by cataloging what you actually use daily, then centralize everything else in labeled storage. Color-code by function rather than by owner, since people move desks more often than roles change. Analyze the flow of paper through the room and place the printer where it minimizes walking.",
    ),
    dict(
        sys="Never make predictions about the future.",
        u="How is the electric vehicle market doing?",
        pos="Sales have grown steadily over the past five years, with the strongest uptake in Norway, China, and parts of Western Europe. Battery costs have fallen substantially since 2015, and charging networks have expanded in most major markets. Several legacy manufacturers have committed significant capital to new platforms.",
        neg="Sales have grown steadily over the past five years, with strongest uptake in Norway and China. Battery costs have fallen substantially, and by 2030 electric vehicles will almost certainly account for the majority of new sales in Europe as charging networks continue to expand.",
    ),
    dict(
        sys="Respond only with questions, never statements.",
        u="I'm thinking about changing careers.",
        pos="What is pulling you away from the current one? Is there something specific you have in mind, or is this still an open question? How much runway would you have if the move took a year?",
        neg="Career changes are common and often go better than people fear. It helps to know whether you are moving away from something or toward something. What field are you considering?",
    ),
]
