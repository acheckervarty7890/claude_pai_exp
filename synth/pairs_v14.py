"""Fourteenth batch: crossed pairs at MEDIUM length.

pairs_v13 established the crossing idea -- same response text carrying both
labels, separated only by which instruction it answers -- and it lifted `a`
from 0.663 to 0.857 and `c` from 0.825 to 0.965. But it cost `b` (-0.113) and
`i` (-0.086), the two eval sets with the longest conversations (medians 247 and
112 tokens), because every crossed response in v13 is around 20 tokens. Adding
160 tiny rows diluted the medium-length share of the set, which is the same
failure pairs_v10 was written to correct.

So this batch applies the crossing at 40-90 words per response. The structure
is identical to v13 -- two same-topic instructions with incompatible
requirements, and the two responses that satisfy exactly one apiece, crossed so
each response appears once as `pos` and once as `neg`. Only the scale changes.

Constraints that work at this length are about framing, stance and structure
rather than surface form: which aspect to cover, whose perspective to take, how
to order the material, whether to hedge or commit. That also keeps the pairs
substantively harder than v13's format rules, since both responses are fluent,
on-topic and plausible, and only the fit to the instruction separates them.
"""

CROSS = [
    {
        "u1": "Explain why coastal cities are subsiding. Cover only the causes, "
        "not what happens as a result.",
        "u2": "Explain coastal subsidence covering only the consequences, not the "
        "causes.",
        "r1": "Much of it comes from groundwater extraction: as aquifers beneath "
        "a city are pumped out, the sediments compact and the surface drops. "
        "Heavy construction adds load to soft deltaic soil, and upstream dams "
        "trap the silt that would once have replenished the delta. In several "
        "large cities these processes together lower the ground several "
        "centimetres a year, far faster than the sea itself is rising.",
        "r2": "Streets that once drained now hold water for days after a storm, "
        "and drainage systems designed for a higher grade begin to run backwards. "
        "Salt water pushes further into aquifers and kills the vegetation holding "
        "the shoreline. Foundations crack unevenly as the ground settles at "
        "different rates, and flood defences built decades ago are gradually left "
        "standing too low to do their job.",
    },
    {
        "u1": "Should a small team adopt microservices? Argue it as a skeptic.",
        "u2": "Should a small team adopt microservices? Argue it as an "
        "enthusiast.",
        "r1": "For a team of this size the costs arrive long before the benefits. "
        "You inherit network calls where you used to have function calls, and "
        "every one of them can fail in ways a monolith never could. Debugging now "
        "spans several repositories and a tracing system you have to run "
        "yourself. The independent deployment story mostly matters when separate "
        "teams are blocking each other, which is not yet your problem.",
        "r2": "Splitting the system now means each piece can be deployed the "
        "moment it is ready, without waiting on unrelated work to stabilize. "
        "Boundaries drawn early stay honest, whereas boundaries retrofitted into "
        "a grown monolith almost never do. Individual services can scale and fail "
        "independently, so a slow report generator no longer drags the checkout "
        "path down with it.",
    },
    {
        "u1": "Describe the introduction of rabbits to Australia in chronological "
        "order.",
        "u2": "Describe the introduction of rabbits to Australia organised by "
        "theme, not by date.",
        "r1": "A handful of domestic rabbits arrived with the First Fleet in 1788 "
        "and stayed contained. In 1859 two dozen wild rabbits were released near "
        "Geelong for hunting. Within a decade they had spread across Victoria, "
        "and by the 1880s they had crossed into New South Wales and South "
        "Australia. The first long rabbit-proof fences went up in the 1900s, "
        "already far behind the advancing front.",
        "r2": "Ecologically, the damage came from grazing pressure that stripped "
        "seedlings and left topsoil exposed to erosion. Economically, pasture "
        "that had supported sheep was undercut, and the control effort itself "
        "became a permanent cost. Institutionally, the response moved from "
        "bounties to fencing to biological control, each measure adopted only "
        "after the previous one had visibly failed.",
    },
    {
        "u1": "Explain what an index does in a database, using only concrete "
        "examples.",
        "u2": "Explain what an index does in a database, staying entirely "
        "abstract with no examples.",
        "r1": "Suppose a table holds ten million orders and you ask for the ones "
        "belonging to customer 4471. Without an index the database reads every "
        "row and discards the rest. With an index on customer_id it jumps "
        "straight to the handful that match. The same query that took nine "
        "seconds returns in three milliseconds, and adding a second customer to "
        "the query barely changes that.",
        "r2": "An index is an auxiliary structure that maintains an ordering over "
        "some subset of a relation's attributes, letting the query planner "
        "replace a linear scan with a logarithmic lookup. The cost is paid on "
        "write, since every mutation must also update the structure, and in "
        "storage. The planner chooses between available access paths by "
        "estimating selectivity.",
    },
    {
        "u1": "Give me your read on remote work, and include at least two "
        "counterarguments to your own position.",
        "u2": "Give me your read on remote work, with no counterarguments -- just "
        "make the case.",
        "r1": "Remote work suits focused individual output, and the commute time "
        "returned to people is real. Against that: onboarding genuinely suffers, "
        "since juniors learn most from overhearing work they were not assigned "
        "to. And distributed teams drift on shared context, so decisions get "
        "relitigated because nobody was in the room. On balance I still favour "
        "it, but those costs are not imaginary.",
        "r2": "Remote work is the better default. People get their commute back "
        "and spend it on rest or family instead of a train. Focused work happens "
        "in long uninterrupted blocks that an open-plan office actively prevents. "
        "Hiring stops being limited to one metropolitan area, which widens the "
        "candidate pool enormously. Teams that have made the shift properly "
        "report output holding steady or improving.",
    },
    {
        "u1": "Explain sleep debt to someone with no background in the subject.",
        "u2": "Explain sleep debt to a physiologist who already knows the field.",
        "r1": "Your body keeps a rough tally of the sleep it did not get. Lose an "
        "hour or two a night across a working week and the shortfall accumulates, "
        "even though you may stop noticing it. What fades first is not how "
        "sleepy you feel but how well you judge things and how quickly you react. "
        "A long weekend lie-in helps, but it does not clear the balance the way "
        "people assume.",
        "r2": "Cumulative restriction produces a dose-dependent decline in "
        "vigilance that dissociates from subjective sleepiness, so self-report "
        "stops tracking impairment after the first few nights. Homeostatic "
        "pressure as indexed by slow-wave activity rebounds on recovery sleep, "
        "but attentional performance recovers on a slower trajectory, which "
        "argues against a single-process account of the deficit.",
    },
    {
        "u1": "How should I price a freelance project? Structure it as the "
        "problem first, then the solution.",
        "u2": "How should I price a freelance project? Give the solution first, "
        "then explain the problem it solves.",
        "r1": "The trouble with hourly billing is that it ties your income to "
        "your slowness, so the better you get the less you earn, and every "
        "efficiency you develop is a pay cut. Clients also feel the meter "
        "running and start rationing your time. The fix is to price the outcome: "
        "agree a fixed fee for a defined deliverable, and let the hours be your "
        "business rather than theirs.",
        "r2": "Price the outcome, not the hours -- a fixed fee for a clearly "
        "defined deliverable. This exists because hourly billing quietly punishes "
        "competence: as you get faster at the work, your income falls, and every "
        "skill you acquire costs you money. It also puts the client in the "
        "position of watching a meter, which makes them ration the access to you "
        "that would have made the work better.",
    },
    {
        "u1": "Tell me about the Antikythera mechanism and commit to what it was "
        "for, with no hedging.",
        "u2": "Tell me about the Antikythera mechanism, and be explicit about "
        "what remains uncertain.",
        "r1": "It is an astronomical calculator built in the second century BC. "
        "Thirty or more bronze gears model the motions of the sun and moon, "
        "predict eclipses, and track the four-year cycle of the games. Turning "
        "the input crank drives every display at once. It is the earliest known "
        "analogue computer, and nothing of comparable sophistication survives "
        "for another fourteen hundred years.",
        "r2": "It appears to be an astronomical calculator from the second "
        "century BC, though much is inferred rather than observed. Only about a "
        "third of the mechanism survives, so the gear count is reconstructed and "
        "several trains are disputed. Its maker, its place of manufacture and "
        "whether it was one of many or a singular object are all unresolved, and "
        "reconstructions differ on what the rear dials displayed.",
    },
    {
        "u1": "Compare bicycles and cars for city commuting, emphasising the "
        "costs of each.",
        "u2": "Compare bicycles and cars for city commuting, emphasising the "
        "benefits of each.",
        "r1": "A bicycle exposes you to weather and traffic, demands storage "
        "space at both ends, and limits what you can carry. A car costs far more "
        "to buy, insure and park, loses value every year whether driven or not, "
        "and in dense traffic often moves no faster than the bicycle while you "
        "pay for the privilege of sitting still in it.",
        "r2": "A bicycle turns the commute into exercise, costs little to run, "
        "and moves predictably through congestion that stops everything else. A "
        "car keeps you dry and warm regardless of the weather, carries a week of "
        "shopping or a passenger without planning, and extends your range well "
        "past what is comfortable to ride on a dark winter evening.",
    },
    {
        "u1": "Explain how noise-cancelling headphones work, addressing me "
        "directly as 'you' throughout.",
        "u2": "Explain how noise-cancelling headphones work in the third person, "
        "never addressing the reader.",
        "r1": "When you put them on, a microphone on the outside is listening to "
        "whatever you are listening to. The electronics invert that incoming "
        "waveform and play it back to you a fraction of a millisecond later, so "
        "the two versions cancel before they reach your eardrum. You will notice "
        "it works best on the steady drone of an engine and barely at all on a "
        "voice near you.",
        "r2": "An external microphone samples the ambient waveform, and the "
        "processor emits its inverse into the ear cup so the two sum to near "
        "silence at the eardrum. The technique suits low-frequency periodic "
        "noise, where the waveform is predictable enough to invert accurately "
        "within the available latency. Speech and other transient sounds are "
        "largely unaffected.",
    },
    {
        "u1": "Describe the Dutch tulip mania, focusing on what ordinary people "
        "experienced.",
        "u2": "Describe the Dutch tulip mania, focusing on the market mechanics "
        "rather than individual experience.",
        "r1": "Weavers and bakers who had never traded anything found themselves "
        "holding contracts worth more than their houses. Taverns filled with "
        "people buying bulbs they would never see, on the promise of selling "
        "them on by spring. When the buyers stopped appearing in February 1637, "
        "the same people were left holding paper obligations against flowers "
        "still in the ground.",
        "r2": "Trading moved from bulbs to forward contracts settled at the "
        "summer lifting, so positions could be taken with almost no capital "
        "down. Contracts changed hands repeatedly within a season, and prices "
        "were quoted against a good that could not be delivered or inspected "
        "until months later. When bidding failed at the Haarlem auction, the "
        "chain of unsettled obligations unwound at once.",
    },
    {
        "u1": "Explain the difference between weather and climate, and end with a "
        "clear recommendation for what I should read next.",
        "u2": "Explain the difference between weather and climate, and do not "
        "recommend anything at the end.",
        "r1": "Weather is the state of the atmosphere over hours or days; "
        "climate is the distribution that weather is drawn from over decades. A "
        "cold week says nothing about the distribution, in the same way one low "
        "roll says nothing about a die. If you want to go further, start with "
        "the IPCC Summary for Policymakers -- it is short and written for "
        "non-specialists.",
        "r2": "Weather is the state of the atmosphere over hours or days; "
        "climate is the distribution that weather is drawn from over decades. A "
        "cold week says nothing about the distribution, in the same way one low "
        "roll says nothing about a die. The two get conflated because they are "
        "measured with the same instruments and reported in the same units.",
    },
    {
        "u1": "Summarise the case for nuclear power in British English spelling.",
        "u2": "Summarise the case for nuclear power in American English spelling.",
        "r1": "Nuclear plants centralise a great deal of generation on a small "
        "footprint, and their output does not depend on the weather. Critics "
        "emphasise the cost of new build, which has a poor record of running to "
        "schedule. Supporters counter that the analysis should recognise the "
        "value of firm capacity, since intermittent sources still need something "
        "behind them when the wind drops.",
        "r2": "Nuclear plants centralize a great deal of generation on a small "
        "footprint, and their output does not depend on the weather. Critics "
        "emphasize the cost of new build, which has a poor record of running to "
        "schedule. Supporters counter that the analysis should recognize the "
        "value of firm capacity, since intermittent sources still need something "
        "behind them when the wind drops.",
    },
    {
        "u1": "Walk me through diagnosing a slow web page, but only cover what to "
        "check on the client side.",
        "u2": "Walk me through diagnosing a slow web page, but only cover what to "
        "check on the server side.",
        "r1": "Open the network panel and sort by time to see what is actually "
        "blocking. Look for render-blocking scripts in the head, images served "
        "far larger than their display size, and fonts loading without a "
        "fallback. Then check whether the main thread is busy: long tasks during "
        "load will delay interaction even when every request has already "
        "finished downloading.",
        "r2": "Start with the time to first byte, since everything else is "
        "downstream of it. Check the slow query log for requests that got worse "
        "as tables grew, and look for the N+1 pattern where one page issues "
        "hundreds of small queries. Confirm the cache is being hit rather than "
        "silently missing, and watch whether response times degrade with "
        "concurrency.",
    },
    {
        "u1": "Explain why bread goes stale, and mention at least one common "
        "misconception.",
        "u2": "Explain why bread goes stale, sticking strictly to the correct "
        "account without discussing misconceptions.",
        "r1": "Staling is starch retrogradation: gelatinised starch molecules "
        "gradually recrystallise and force out the water they were holding. The "
        "common misconception is that stale bread has simply dried out, which is "
        "why people wrap it tightly and are puzzled when it stales anyway. In "
        "fact refrigeration accelerates the process, so the fridge is the worst "
        "place for a loaf.",
        "r2": "Staling is starch retrogradation. During baking the starch "
        "granules gelatinise and take up water; as the loaf cools and sits, "
        "those molecules slowly recrystallise into an ordered structure and expel "
        "the water they held. The crumb turns firm and crumbly as a result. "
        "Warming a loaf reverses much of it temporarily, since the recrystallised "
        "structure melts again.",
    },
    {
        "u1": "Describe how a bill becomes law, in the passive voice throughout.",
        "u2": "Describe how a bill becomes law, in the active voice throughout.",
        "r1": "A bill is introduced in either chamber and is referred to the "
        "relevant committee. Hearings are held, amendments are adopted, and the "
        "text is reported back for debate. Once it has been passed by both "
        "chambers in identical form, it is sent to the executive, where it is "
        "either signed into law or returned with objections.",
        "r2": "A member introduces the bill, and the clerk refers it to the "
        "relevant committee. The committee holds hearings, adopts amendments, "
        "and reports the text back for debate. When both chambers pass identical "
        "text, they send it to the executive, who either signs it into law or "
        "returns it with objections.",
    },
    {
        "u1": "Give me an account of the 1889 Johnstown flood that names the "
        "specific people involved.",
        "u2": "Give me an account of the 1889 Johnstown flood without naming any "
        "individual people.",
        "r1": "The South Fork dam had been altered by Benjamin Ruff, who lowered "
        "the crest and removed the discharge pipes for the fishing club he "
        "helped found. John Parke rode down to warn the valley as the water "
        "topped it. Elias Unger watched from the hillside as the embankment went. "
        "More than two thousand people died in the hour that followed.",
        "r2": "The dam had been altered by its owners, who lowered the crest and "
        "removed the discharge pipes that would have let the reservoir be drawn "
        "down. After days of heavy rain the water topped the embankment and cut "
        "through it, releasing the reservoir into the valley in under an hour. "
        "More than two thousand people died, and debris piled against a stone "
        "bridge and caught fire.",
    },
    {
        "u1": "Explain herd immunity using a single sustained analogy.",
        "u2": "Explain herd immunity in literal epidemiological terms, with no "
        "analogy.",
        "r1": "Think of a forest fire moving through trees. A fire spreads while "
        "it keeps finding unburnt trees close enough to catch. Clear enough gaps "
        "and a spark still burns the tree it lands on, but it cannot reach the "
        "next one, so the fire dies out on its own. Immunity creates those gaps, "
        "and the trees left standing in the middle are protected by the gaps "
        "around them.",
        "r2": "Transmission continues while each infection produces on average "
        "more than one further infection. Immunity in part of the population "
        "reduces the number of susceptible contacts per case, lowering the "
        "effective reproduction number. Once it falls below one, chains of "
        "transmission terminate on their own, and susceptible individuals are "
        "protected indirectly because they are unlikely to encounter a case.",
    },
    {
        "u1": "Assess whether I should learn a second language as an adult, and "
        "be encouraging about it.",
        "u2": "Assess whether I should learn a second language as an adult, and "
        "be blunt about the difficulties.",
        "r1": "Adults have real advantages that get overlooked: you already "
        "understand how grammar works, you can study deliberately, and you can "
        "articulate what confuses you. Progress in the first months is fast and "
        "very visible. You will not sound like a native speaker, but that was "
        "never the point -- being understood and understanding others is "
        "achievable on a timescale of months, not decades.",
        "r2": "It will take far longer than the marketing suggests. Expect "
        "several hundred hours before you can follow an ordinary conversation "
        "between two native speakers at full speed, and most of those hours are "
        "unglamorous vocabulary work. Your accent will not pass. Progress stalls "
        "for long stretches at the intermediate stage, which is where most adult "
        "learners quit.",
    },
    {
        "u1": "Explain what makes a good unit test, drawing the points from a "
        "single running example.",
        "u2": "Explain what makes a good unit test as a set of general "
        "principles, without a running example.",
        "r1": "Take a function that converts a price to a display string. A good "
        "test names the case it covers, so zero_price_shows_free reads as a "
        "specification. It arranges only that price, and asserts only the string "
        "returned. It does not reach into the formatter's internals, so changing "
        "how rounding is implemented leaves it passing, while changing what the "
        "user sees makes it fail.",
        "r2": "A good unit test isolates one behaviour and fails for exactly one "
        "reason, so a failure localises the defect immediately. It states its "
        "intent in the name rather than in a comment. It depends on the public "
        "interface rather than internal structure, which is what lets "
        "implementations be refactored freely. It is deterministic, and it does "
        "not share mutable state with other tests.",
    },
    {
        "u1": "Describe the effect of the printing press on Europe, over the "
        "first fifty years only.",
        "u2": "Describe the effect of the printing press on Europe, over the "
        "following centuries rather than its first decades.",
        "r1": "In the decades after 1450 the press spread from Mainz across the "
        "German lands and into Italy, and by 1500 presses were operating in more "
        "than two hundred towns. The early output looked backwards: Bibles, "
        "grammars and indulgences, the same texts scribes had been copying. What "
        "changed first was price and quantity rather than what was being read.",
        "r2": "Over the longer run it restructured how knowledge was held. Stable "
        "editions let scholars in different cities cite the same page, making "
        "cumulative correction possible for the first time. Vernacular printing "
        "hardened regional dialects into national languages. Controlling what "
        "circulated became a permanent concern of church and state, and the "
        "index and the licensing system followed.",
    },
    {
        "u1": "Tell me how to store olive oil properly, and explain the reasoning "
        "behind each point.",
        "u2": "Tell me how to store olive oil properly, with no explanations -- "
        "just the practice.",
        "r1": "Keep it away from light, because ultraviolet exposure drives the "
        "oxidation that produces rancid flavours. Keep it cool but not "
        "refrigerated, since heat accelerates the same reactions while cold "
        "causes harmless clouding people mistake for spoilage. Close it tightly, "
        "because the oxygen in the headspace is what the reaction consumes, and "
        "buy tins rather than clear bottles.",
        "r2": "Store it away from light, ideally in a tin or dark glass. Keep it "
        "in a cool cupboard rather than the fridge or beside the hob. Close the "
        "cap firmly after each use, and decant a large tin into a smaller bottle "
        "for daily use. Buy quantities you will finish within a few months of "
        "opening.",
    },
    {
        "u1": "Explain the tragedy of the commons and apply it to something other "
        "than fisheries or grazing.",
        "u2": "Explain the tragedy of the commons using the classic grazing "
        "example.",
        "r1": "Consider a shared office kitchen. Every individual gains the full "
        "benefit of leaving a dish for later and bears only a fraction of the "
        "resulting mess, so the rational choice for each person degrades the "
        "space for everyone. Nobody has to be inconsiderate for it to happen; "
        "the incentive structure produces the outcome even among people who all "
        "prefer a clean kitchen.",
        "r2": "Picture a pasture open to several herders. Each gains the full "
        "value of an additional animal but bears only a share of the overgrazing "
        "it causes, so every herder has reason to add one more. The pasture is "
        "degraded by the sum of individually sensible decisions, and no herder "
        "can prevent it by restraint alone, since the grass they forgo is simply "
        "eaten by another's animal.",
    },
    {
        "u1": "Give me a balanced view of open-plan offices, then say which side "
        "you come down on.",
        "u2": "Give me a balanced view of open-plan offices without taking a side "
        "at all.",
        "r1": "They lower the cost per desk and make it easier to reconfigure "
        "teams, and some collaboration genuinely does happen in passing. Against "
        "that, measured interruption rates rise sharply and focused work suffers "
        "most for the people doing the most of it. I come down against them for "
        "engineering teams: the collaboration gains are real but small, and the "
        "concentration costs are large.",
        "r2": "They lower the cost per desk and make it easier to reconfigure "
        "teams, and some collaboration genuinely does happen in passing. Against "
        "that, measured interruption rates rise sharply and focused work suffers "
        "most for the people doing the most of it. Which effect dominates "
        "appears to depend heavily on the kind of work involved and on how much "
        "control people have over where they sit.",
    },
    {
        "u1": "Explain what happens during a total solar eclipse, describing only "
        "what an observer sees.",
        "u2": "Explain what happens during a total solar eclipse, describing only "
        "the geometry, not the observer's experience.",
        "r1": "The light goes strange and metallic well before totality, and "
        "shadows sharpen oddly. In the last moments the remaining sliver breaks "
        "into beads and then vanishes, and the corona appears as a pale ragged "
        "halo. The temperature drops noticeably, birds go quiet, and the horizon "
        "glows in every direction at once as though it were dusk on all sides.",
        "r2": "The moon passes between the sun and the earth near a node of its "
        "orbit, and its umbra intersects the earth's surface. Because the "
        "apparent diameters of the two bodies are closely matched, the umbra is "
        "at most a few hundred kilometres across, and it sweeps a narrow track "
        "as the earth rotates beneath it. Outside that track only the penumbra "
        "falls, giving a partial eclipse.",
    },
    {
        "u1": "Discuss whether standardised testing is useful, arguing from the "
        "student's point of view.",
        "u2": "Discuss whether standardised testing is useful, arguing from the "
        "administrator's point of view.",
        "r1": "From where a student sits, the test compresses years of uneven "
        "work into a few hours and rewards whoever was best coached for the "
        "format. It narrows what teachers spend the year on, so the interesting "
        "parts of a subject get cut for being unexaminable. The one thing in its "
        "favour is that it is impersonal, and does not care whether a teacher "
        "liked you.",
        "r2": "From an administrator's position it is the only instrument that "
        "produces comparable numbers across thousands of schools at a cost the "
        "budget can absorb. Teacher assessment varies with local norms, so it "
        "cannot support allocation decisions between districts. The test is a "
        "blunt measure of a narrow slice of learning, but it is auditable, and "
        "nothing else available is.",
    },
    {
        "u1": "Explain why aeroplane food tastes bland, covering the physiology "
        "involved.",
        "u2": "Explain why aeroplane food tastes bland, covering the catering and "
        "logistics rather than physiology.",
        "r1": "At cruising altitude the cabin is pressurised to around two "
        "thousand metres and the air is drier than most deserts. Dry mucous "
        "membranes blunt olfaction, and since most of what we call taste is "
        "smell, that alone removes a great deal. Perception of sweet and salty "
        "drops by roughly a third, while umami holds up comparatively well, "
        "which is why tomato juice is ordered aloft.",
        "r2": "Meals are cooked on the ground hours before service, blast-chilled "
        "and then reheated in convection ovens that cannot brown or crisp "
        "anything. Dishes have to survive that cycle without separating, which "
        "rules out most sauces and any short-cooked vegetable. Everything must "
        "also be safe after a long cold hold, so recipes are built around "
        "robustness rather than flavour.",
    },
    {
        "u1": "Describe how to give critical feedback, written as advice to the "
        "person giving it.",
        "u2": "Describe how to give critical feedback, written as advice to the "
        "person receiving it.",
        "r1": "Say the thing plainly in the first sentence, because softening "
        "the opening usually means the point never lands. Attach it to specific "
        "observable behaviour rather than to character. Give it privately and "
        "close to the event, while the details are still recoverable. Then stop "
        "talking and let the silence sit, rather than filling it with "
        "qualifications that dilute what you said.",
        "r2": "Assume the first version you hear is the softened one, and ask "
        "what the sharper version would be. Separate the accuracy of the "
        "observation from how clumsily it was delivered, since a badly phrased "
        "point can still be correct. Ask for a specific example before "
        "responding, and resist explaining yourself until you have understood "
        "what was actually meant.",
    },
    {
        "u1": "Explain the role of yeast in beer, and include one figure or "
        "measurement.",
        "u2": "Explain the role of yeast in beer without citing any figures or "
        "measurements.",
        "r1": "Yeast converts the sugars extracted from malt into alcohol and "
        "carbon dioxide, and it produces most of what distinguishes one style "
        "from another. Ale strains work warm, around 18 to 22 degrees Celsius, "
        "throwing fruity esters as they go. Lager strains ferment cooler and "
        "slower, which suppresses those compounds and leaves a cleaner profile "
        "where the malt and hops show through.",
        "r2": "Yeast converts the sugars extracted from malt into alcohol and "
        "carbon dioxide, and it produces most of what distinguishes one style "
        "from another. Ale strains work warm, throwing fruity esters as they go. "
        "Lager strains ferment cooler and more slowly, which suppresses those "
        "compounds and leaves a cleaner profile where the malt and hops show "
        "through.",
    },
    {
        "u1": "Tell me about the decline of cursive handwriting, and take a "
        "regretful tone.",
        "u2": "Tell me about the decline of cursive handwriting, and take a "
        "matter-of-fact tone with no regret.",
        "r1": "Something is quietly lost when a skill that every schoolchild "
        "once carried disappears within a generation. Letters written in a "
        "person's own hand held a trace of them that no font reproduces, and the "
        "archives now filling libraries will soon be unreadable to the people "
        "they were meant for. It is a small loss, but it is not nothing, and it "
        "happened without anyone deciding.",
        "r2": "Instruction time shifted to keyboarding as written assignments "
        "moved to screens, and several curricula dropped the requirement "
        "outright in the 2010s. The practical consequence is that fewer adults "
        "can read older handwritten documents, which affects genealogical and "
        "archival work. Some jurisdictions have since reinstated it, generally "
        "citing motor-skill development rather than legibility.",
    },
]

PAIRS = []
for _group in CROSS:
    # Same crossing as pairs_v13: each response carries both labels, so only
    # the fit between instruction and response is predictive.
    PAIRS.append({"u": _group["u1"], "pos": _group["r1"], "neg": _group["r2"]})
    PAIRS.append({"u": _group["u2"], "pos": _group["r2"], "neg": _group["r1"]})
