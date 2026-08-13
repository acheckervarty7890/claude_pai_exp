"""Thirteenth batch: crossed pairs -- same response, opposite label.

Every module up to here holds the instruction fixed and varies the response.
That leaves the response itself partially predictive: `pos` and `neg` are
different texts, so any surface regularity separating them (length, hedging,
directness) is a cue the probe can take instead of compliance. pairs_v8/v10/v11
each fought one such cue by length-matching, which controls length but not the
rest.

This batch removes the cue class outright by inverting the contrast. Each group
below is two instructions and two responses, crossed:

    u1 + r1 -> follows        u2 + r2 -> follows
    u1 + r2 -> does not       u2 + r1 -> does not

So r1 appears once labelled `follows` and once labelled `does not`, and so does
r2. Within a group the two labels are backed by *identical* response text; the
only thing that separates them is which instruction the response is answering.
No property of the response alone can beat chance, and the probe has to encode
the instruction-response relation.

Both instructions in a group are about the same topic, so topic is held fixed
too, and the crossing neutralizes length automatically -- when a short and a
long response each carry both labels, response length is uninformative even for
the groups whose constraint is explicitly about length.
"""

# Each group: two same-topic instructions with incompatible requirements, and
# the two responses that satisfy exactly one apiece.
CROSS = [
    {
        "u1": "How does a heat pump work? Answer in exactly one sentence.",
        "u2": "How does a heat pump work? Answer in exactly three sentences.",
        "r1": "A heat pump moves heat from one place to another by evaporating "
        "and compressing a refrigerant, rather than generating heat directly.",
        "r2": "A heat pump moves heat rather than creating it. A refrigerant "
        "evaporates outdoors and absorbs warmth, then a compressor raises its "
        "pressure and temperature. Indoors it condenses and releases that heat.",
    },
    {
        "u1": "Name three uses for baking soda. Give them as bullet points.",
        "u2": "Name three uses for baking soda. Write it as one paragraph with "
        "no lists or bullets.",
        "r1": "- Deodorizing a fridge\n- Scrubbing a sink\n- Leavening in baking",
        "r2": "Baking soda deodorizes a fridge, works as a mild abrasive for "
        "scrubbing a sink, and acts as a leavening agent in baking.",
    },
    {
        "u1": "What is the capital of Peru? Reply only in lowercase.",
        "u2": "What is the capital of Peru? Reply in ALL CAPS.",
        "r1": "lima is the capital of peru.",
        "r2": "LIMA IS THE CAPITAL OF PERU.",
    },
    {
        "u1": "Describe the taste of ginger without using the word 'spicy'.",
        "u2": "Describe the taste of ginger and be sure to use the word 'spicy'.",
        "r1": "Ginger is sharp and warming, with a bright citrus edge and a "
        "lingering heat at the back of the throat.",
        "r2": "Ginger is spicy and warming, with a bright citrus edge and a "
        "lingering heat at the back of the throat.",
    },
    {
        "u1": "What is 17 times 4? Give the answer with no explanation.",
        "u2": "What is 17 times 4? Show your reasoning before the answer.",
        "r1": "68",
        "r2": "17 times 4 is 17 doubled twice: 17 becomes 34, and 34 becomes 68. "
        "The answer is 68.",
    },
    {
        "u1": "Give me the height and year of the Eiffel Tower as valid JSON.",
        "u2": "Give me the height and year of the Eiffel Tower in plain prose, "
        "with no JSON or code formatting.",
        "r1": '{"height_m": 330, "year_completed": 1889}',
        "r2": "The Eiffel Tower stands 330 metres tall and was completed in 1889.",
    },
    {
        "u1": "Why do leaves change colour? Keep it under ten words.",
        "u2": "Why do leaves change colour? Write at least forty words.",
        "r1": "Chlorophyll breaks down, revealing yellow and orange pigments.",
        "r2": "As daylight shortens and temperatures drop, trees stop producing "
        "chlorophyll, the green pigment that dominates a leaf all summer. Once it "
        "breaks down, the carotenoids and anthocyanins that were present all "
        "along become visible, which is why leaves turn yellow, orange and red "
        "before they finally fall.",
    },
    {
        "u1": "Recommend a beginner houseplant. Start your reply with 'Sure'.",
        "u2": "Recommend a beginner houseplant. Do not begin your reply with "
        "'Sure'.",
        "r1": "Sure -- a pothos is nearly unkillable and tolerates low light.",
        "r2": "A pothos is nearly unkillable and tolerates low light.",
    },
    {
        "u1": "List two safety checks before a long drive, as a numbered list.",
        "u2": "List two safety checks before a long drive, as a single sentence "
        "with no numbering.",
        "r1": "1. Check tyre pressure and tread\n2. Check oil and coolant levels",
        "r2": "Check the tyre pressure and tread, then check the oil and coolant "
        "levels.",
    },
    {
        "u1": "Is Venus hotter than Mercury? Answer yes or no only.",
        "u2": "Is Venus hotter than Mercury? Don't just say yes or no -- explain.",
        "r1": "Yes.",
        "r2": "Yes -- Venus is hotter despite being further out, because its thick "
        "carbon dioxide atmosphere traps heat that Mercury has no atmosphere to "
        "hold.",
    },
    {
        "u1": "Explain what a semicolon does. Write it in the second person.",
        "u2": "Explain what a semicolon does. Write it in the third person, never "
        "addressing the reader.",
        "r1": "You use a semicolon to join two clauses that could each stand "
        "alone, when you want them held closer than a full stop would allow.",
        "r2": "A semicolon joins two clauses that could each stand alone, holding "
        "them closer together than a full stop would allow.",
    },
    {
        "u1": "Suggest a weeknight dinner. End your reply with a question.",
        "u2": "Suggest a weeknight dinner. Do not ask me any questions.",
        "r1": "Sheet-pan sausages with peppers takes about half an hour. Do you "
        "have a preference on spice level?",
        "r2": "Sheet-pan sausages with peppers takes about half an hour and needs "
        "only one tray.",
    },
    {
        "u1": "Give me these animals sorted alphabetically: zebra, ant, moose.",
        "u2": "Give me these animals in the order I listed them, unsorted: zebra, "
        "ant, moose.",
        "r1": "ant, moose, zebra",
        "r2": "zebra, ant, moose",
    },
    {
        "u1": "A shirt costs 23.4567 dollars. Round it to the nearest whole "
        "number.",
        "u2": "A shirt costs 23.4567 dollars. Give it to two decimal places.",
        "r1": "23 dollars.",
        "r2": "23.46 dollars.",
    },
    {
        "u1": "Describe yesterday's storm in the past tense.",
        "u2": "Describe yesterday's storm in the present tense, as if it is "
        "happening now.",
        "r1": "The wind picked up after dark and rain hammered the windows until "
        "the power finally cut out.",
        "r2": "The wind picks up after dark and rain hammers the windows until "
        "the power finally cuts out.",
    },
    {
        "u1": "Summarize the plot of Cinderella in exactly one word.",
        "u2": "Summarize the plot of Cinderella in a full sentence.",
        "r1": "Transformation.",
        "r2": "A mistreated young woman is helped to a royal ball, and is found "
        "again afterwards by the slipper she leaves behind.",
    },
    {
        "u1": "How far is a marathon? Use metric units.",
        "u2": "How far is a marathon? Use imperial units.",
        "r1": "A marathon is 42.2 kilometres.",
        "r2": "A marathon is 26.2 miles.",
    },
    {
        "u1": "Write a greeting for a colleague. Use no punctuation at all.",
        "u2": "Write a greeting for a colleague. Use full, correct punctuation.",
        "r1": "morning hope the week is treating you well",
        "r2": "Morning! Hope the week is treating you well.",
    },
    {
        "u1": "Explain gravity to me. Give exactly two examples.",
        "u2": "Explain gravity to me. Do not give any examples.",
        "r1": "Gravity is the attraction between masses. It is why a dropped "
        "apple falls to the ground, and why the Moon stays in orbit around Earth.",
        "r2": "Gravity is the mutual attraction between masses, growing stronger "
        "with mass and weaker with the square of the distance between them.",
    },
    {
        "u1": "What should I pack for a rainy hike? Answer in French.",
        "u2": "What should I pack for a rainy hike? Answer in English.",
        "r1": "Emportez une veste impermeable, des chaussettes de rechange et un "
        "sac etanche pour votre telephone.",
        "r2": "Bring a waterproof jacket, spare socks, and a dry bag for your "
        "phone.",
    },
    {
        "u1": "Describe the ocean at dawn as a haiku.",
        "u2": "Describe the ocean at dawn as a single flowing sentence, not a "
        "poem.",
        "r1": "Grey water breathing\nthe first light finds every wave\ngulls call "
        "and scatter",
        "r2": "The grey water breathes slowly as the first light finds every wave "
        "and the gulls call and scatter above it.",
    },
    {
        "u1": "Tell me about sourdough starter. Use no more than two sentences.",
        "u2": "Tell me about sourdough starter. Use at least five sentences.",
        "r1": "A sourdough starter is a live culture of wild yeast and bacteria "
        "kept in flour and water. Feeding it regularly keeps it active enough to "
        "raise bread.",
        "r2": "A sourdough starter is a live culture. It holds wild yeast "
        "alongside lactic acid bacteria. The yeast produces the gas that lifts a "
        "loaf. The bacteria produce the acids that give it a sour note. Feeding "
        "it with fresh flour and water keeps the balance stable.",
    },
    {
        "u1": "Give me a title for an essay on urban foxes. Put it in quotes.",
        "u2": "Give me a title for an essay on urban foxes. Do not use quotation "
        "marks.",
        "r1": '"The City After Dark"',
        "r2": "The City After Dark",
    },
    {
        "u1": "Explain a firewall using an analogy.",
        "u2": "Explain a firewall literally, without using any analogy or "
        "metaphor.",
        "r1": "A firewall is like a doorman with a guest list: traffic that isn't "
        "on the list doesn't get through the door.",
        "r2": "A firewall inspects network traffic against a set of rules and "
        "blocks any packets that those rules do not permit.",
    },
    {
        "u1": "What time zone is Tokyo in? Answer with the offset only.",
        "u2": "What time zone is Tokyo in? Give the name of the zone, not the "
        "offset.",
        "r1": "UTC+9",
        "r2": "Japan Standard Time",
    },
    {
        "u1": "Name a good first programming language and justify it in one line.",
        "u2": "Name a good first programming language with no justification at "
        "all.",
        "r1": "Python -- the syntax stays out of the way while you learn to think "
        "in code.",
        "r2": "Python.",
    },
    {
        "u1": "Rewrite this more formally: 'we gotta move the meeting'.",
        "u2": "Rewrite this more casually: 'we gotta move the meeting'.",
        "r1": "We will need to reschedule the meeting.",
        "r2": "We've gotta shift the meeting, sorry!",
    },
    {
        "u1": "How do I descale a kettle? Answer as a two-step recipe.",
        "u2": "How do I descale a kettle? Answer without giving any steps -- just "
        "say what it involves.",
        "r1": "1. Fill the kettle with equal parts white vinegar and water and "
        "boil it.\n2. Let it sit an hour, then rinse thoroughly.",
        "r2": "It involves soaking the element in a mild acid such as white "
        "vinegar until the limescale dissolves, followed by a thorough rinse.",
    },
    {
        "u1": "Give me a fact about octopuses. Write it as a question and answer.",
        "u2": "Give me a fact about octopuses. Write it as a plain statement, not "
        "a question.",
        "r1": "How many hearts does an octopus have? Three -- two pump blood to "
        "the gills and one to the rest of the body.",
        "r2": "An octopus has three hearts: two pump blood to the gills and one "
        "to the rest of the body.",
    },
    {
        "u1": "Describe a lemon using only its colour and shape.",
        "u2": "Describe a lemon using only its taste and smell.",
        "r1": "It is bright yellow and oval, tapering to a small point at each "
        "end.",
        "r2": "It is sharply sour with a clean, bright scent that catches in the "
        "nose.",
    },
    {
        "u1": "List the first three prime numbers, separated by commas.",
        "u2": "List the first three prime numbers, one per line.",
        "r1": "2, 3, 5",
        "r2": "2\n3\n5",
    },
    {
        "u1": "Explain why the sky is blue to a five-year-old.",
        "u2": "Explain why the sky is blue to a physics graduate.",
        "r1": "Sunlight is made of lots of colours mixed together, and the air "
        "bounces the blue ones around the most, so blue is what you see "
        "everywhere you look.",
        "r2": "Rayleigh scattering goes as the inverse fourth power of "
        "wavelength, so shorter wavelengths scatter far more strongly, and the "
        "diffuse sky radiance is correspondingly weighted toward the blue.",
    },
    {
        "u1": "Give me a packing list for a beach day. Exactly four items.",
        "u2": "Give me a packing list for a beach day. Exactly two items.",
        "r1": "Sunscreen, a towel, water, and a hat.",
        "r2": "Sunscreen and a towel.",
    },
    {
        "u1": "Answer in a single word: what gas do plants absorb?",
        "u2": "Answer in a complete sentence: what gas do plants absorb?",
        "r1": "Carbon dioxide.",
        "r2": "Plants absorb carbon dioxide from the air during photosynthesis.",
    },
    {
        "u1": "Describe the rules of chess without naming any specific piece.",
        "u2": "Describe the rules of chess and name at least three pieces.",
        "r1": "Two players alternate moves on a chequered board, each type of "
        "unit moving in its own fixed pattern, until one player's most important "
        "unit is trapped with no legal escape.",
        "r2": "Two players alternate moves; the rook moves in straight lines, the "
        "bishop diagonally, and the knight in an L-shape, and the game ends when "
        "the king is trapped.",
    },
    {
        "u1": "What's a good gift for a gardener? Reply in under five words.",
        "u2": "What's a good gift for a gardener? Reply in roughly thirty words.",
        "r1": "A sturdy pair of secateurs.",
        "r2": "A sturdy pair of secateurs is hard to beat, since cheap ones crush "
        "stems instead of cutting them cleanly, and a good pair will last for "
        "decades with occasional sharpening.",
    },
    {
        "u1": "Tell me about the Nile. Mention its length.",
        "u2": "Tell me about the Nile. Do not mention any numbers or measurements.",
        "r1": "The Nile runs about 6,650 kilometres northward through eastern "
        "Africa before emptying into the Mediterranean.",
        "r2": "The Nile runs northward through eastern Africa for an enormous "
        "distance before emptying into the Mediterranean.",
    },
    {
        "u1": "Write a one-line apology for a late reply, signed 'Alex'.",
        "u2": "Write a one-line apology for a late reply with no signature or "
        "name.",
        "r1": "Sorry for the slow reply -- this week got away from me.\nAlex",
        "r2": "Sorry for the slow reply -- this week got away from me.",
    },
    {
        "u1": "Compare cats and dogs in a table.",
        "u2": "Compare cats and dogs in prose, without using a table.",
        "r1": "| trait | cat | dog |\n|---|---|---|\n| exercise | low | high |\n"
        "| alone time | tolerates | struggles |",
        "r2": "Cats need less exercise than dogs and tolerate being alone for "
        "longer, while dogs generally struggle with both.",
    },
    {
        "u1": "State one benefit of cycling to work, hedged as an opinion.",
        "u2": "State one benefit of cycling to work as a flat fact, with no "
        "hedging.",
        "r1": "I'd say the biggest benefit is probably that your commute doubles "
        "as exercise.",
        "r2": "Cycling to work turns the commute into exercise.",
    },
]

PAIRS = []
for _group in CROSS:
    # Each response is used once as the compliant answer and once as the
    # non-compliant one, so the two labels are backed by identical text.
    PAIRS.append({"u": _group["u1"], "pos": _group["r1"], "neg": _group["r2"]})
    PAIRS.append({"u": _group["u2"], "pos": _group["r2"], "neg": _group["r1"]})
