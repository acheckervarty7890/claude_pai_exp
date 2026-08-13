"""Eleventh batch: more ultra-short length-matched pairs, to rebalance.

v9 added medium-length matched pairs and set new bests on b, d, f and i, but
`a` fell from 0.804 to 0.663. `a` is the shortest eval set by far -- median 39
tokens for the *entire* conversation, minimum 20 -- so it is carried by
training examples of the same tiny scale, and v9's 52 medium pairs diluted
their share of the set.

Everything here is deliberately tiny: a terse question and a handful of words
back, total conversation length in the 20-50 token range that `a` occupies.
Both responses in a pair are the same length, so the only difference is
compliance. This is the pairs_v8 recipe, extended with violation types and
domains it did not reach.
"""

PAIRS = [
    # ---------------- one-word / single-token discipline ----------------
    dict(u="One word. Capital of Poland?", pos="Warsaw", neg="It's Warsaw"),
    dict(u="One word only. Largest continent?", pos="Asia", neg="Asia is largest"),
    dict(u="Single word. Colour of snow?", pos="White", neg="Usually white"),
    dict(u="One word answer. Hottest planet?", pos="Venus", neg="Venus, surprisingly"),
    dict(u="Just one word. Fastest land animal?", pos="Cheetah", neg="The cheetah"),
    dict(u="One word. Smallest prime number?", pos="Two", neg="Two, obviously"),
    dict(u="A single word. What do cows drink?", pos="Water", neg="They drink water"),
    dict(u="One word. Capital of Norway?", pos="Oslo", neg="Oslo, Norway"),
    dict(u="Single word only. Deepest ocean?", pos="Pacific", neg="The Pacific"),
    dict(u="One word. Study of stars?", pos="Astronomy", neg="That's astronomy"),

    # ---------------- yes/no discipline ----------------
    dict(u="Yes or no. Is ice less dense than water?", pos="Yes", neg="Correct"),
    dict(u="Yes or no only. Do sharks have bones?", pos="No", neg="Cartilage, not bone"),
    dict(u="Answer yes or no. Is Mars larger than Earth?", pos="No", neg="Smaller"),
    dict(u="Yes or no. Can sound travel in a vacuum?", pos="No", neg="It cannot"),
    dict(u="Just yes or no. Is gold magnetic?", pos="No", neg="Not magnetic"),
    dict(u="Yes or no. Is a whale a mammal?", pos="Yes", neg="Indeed it is"),
    dict(u="Answer only yes or no. Is Everest the tallest peak?", pos="Yes", neg="By elevation, yes"),

    # ---------------- numeric format discipline ----------------
    dict(u="Digits only. How many hours in two days?", pos="48", neg="Forty-eight"),
    dict(u="Digits only. Legs on three spiders?", pos="24", neg="Twenty-four"),
    dict(u="Words, not digits. How many continents?", pos="Seven", neg="7"),
    dict(u="Words, not digits. Sides of an octagon?", pos="Eight", neg="8"),
    dict(u="Number only, no units. How many metres in a kilometre?", pos="1000", neg="1000 m"),
    dict(u="Include the unit. How long is a marathon?", pos="42 km", neg="42"),
    dict(u="Round to the nearest whole number. What is 7.6?", pos="8", neg="7.6"),
    dict(u="Give it to one decimal place. What is 3.14159?", pos="3.1", neg="3.14"),
    dict(u="No decimals. What is half of 9?", pos="4", neg="4.5"),
    dict(u="Give the exact value. What is half of 9?", pos="4.5", neg="About 4"),

    # ---------------- casing, both terse ----------------
    dict(u="All caps. Name a fruit.", pos="MANGO", neg="Mango"),
    dict(u="Lowercase only. Name a country.", pos="brazil", neg="Brazil"),
    dict(u="All caps. What is the opposite of stop?", pos="GO", neg="Go"),
    dict(u="Lowercase. Name a musical instrument.", pos="violin", neg="Violin"),
    dict(u="Title case. Name a famous mountain.", pos="Mount Fuji", neg="mount fuji"),
    dict(u="All caps. Name a colour.", pos="AMBER", neg="Amber"),

    # ---------------- language, both terse ----------------
    dict(u="In French. Say 'please'.", pos="S'il vous plaît", neg="Por favor"),
    dict(u="In Spanish. Say 'good night'.", pos="Buenas noches", neg="Boa noite"),
    dict(u="In German. What is 'house'?", pos="Haus", neg="Maison"),
    dict(u="In Italian. Say 'thank you'.", pos="Grazie", neg="Merci"),
    dict(u="In French, one word. What is 'bread'?", pos="Pain", neg="Pan"),
    dict(u="In Spanish. What is 'book'?", pos="Libro", neg="Livre"),
    dict(u="Answer in Dutch. Say 'yes'.", pos="Ja", neg="Oui"),
    dict(u="In Portuguese. What is 'milk'?", pos="Leite", neg="Leche"),

    # ---------------- exact count, both terse ----------------
    dict(u="Exactly two words.", pos="Bright morning", neg="Very bright morning"),
    dict(u="Exactly three words.", pos="Rain falls softly", neg="Rain falls very softly"),
    dict(u="Name exactly two metals.", pos="Iron, tin", neg="Iron, tin, zinc"),
    dict(u="Exactly one example.", pos="Sparrow", neg="Sparrow, robin"),
    dict(u="Give exactly three letters.", pos="X, Y, Z", neg="X, Y"),
    dict(u="Name exactly two oceans.", pos="Pacific, Arctic", neg="Pacific"),
    dict(u="Exactly four words.", pos="The sun rose slowly", neg="The sun rose"),

    # ---------------- ordering, both terse ----------------
    dict(u="Alphabetical: pear, date, fig.", pos="date, fig, pear", neg="pear, date, fig"),
    dict(u="Descending: 3, 9, 6.", pos="9, 6, 3", neg="3, 6, 9"),
    dict(u="Ascending: 20, 4, 11.", pos="4, 11, 20", neg="20, 11, 4"),
    dict(u="Reverse: red, green, blue.", pos="blue, green, red", neg="red, green, blue"),
    dict(u="Alphabetical: Nile, Amazon.", pos="Amazon, Nile", neg="Nile, Amazon"),
    dict(u="Shortest word first: elephant, ant, cat.", pos="ant, cat, elephant", neg="elephant, cat, ant"),

    # ---------------- prohibition ignored, both terse ----------------
    dict(u="Name a bird that isn't a penguin.", pos="Heron", neg="Penguin"),
    dict(u="Describe fire without saying 'hot'.", pos="Burning and bright", neg="Hot and bright"),
    dict(u="Name a sport, not football.", pos="Rowing", neg="Football"),
    dict(u="Answer without the word 'no'.", pos="Incorrect", neg="No"),
    dict(u="Name a drink without caffeine.", pos="Chamomile tea", neg="Black coffee"),
    dict(u="A number that isn't even.", pos="Seven", neg="Eight"),
    dict(u="Name a month, not January.", pos="August", neg="January"),
    dict(u="Describe night without 'dark'.", pos="Starlit and quiet", neg="Dark and quiet"),

    # ---------------- adjacent answer, both terse ----------------
    dict(u="Capital of Morocco?", pos="Rabat", neg="Casablanca"),
    dict(u="Capital of Switzerland?", pos="Bern", neg="Zurich"),
    dict(u="Capital of New Zealand?", pos="Wellington", neg="Auckland"),
    dict(u="Capital of the USA?", pos="Washington", neg="New York"),
    dict(u="Capital of India?", pos="New Delhi", neg="Mumbai"),
    dict(u="Largest US state by area?", pos="Alaska", neg="Texas"),
    dict(u="What is the plural of 'child'?", pos="Children", neg="Childs"),
    dict(u="Past tense of 'swim'?", pos="Swam", neg="Swum"),
    dict(u="Opposite of 'ancient'?", pos="Modern", neg="Elderly"),
    dict(u="What is 6 divided by 2?", pos="3", neg="12"),
    dict(u="What is 5 percent of 200?", pos="10", neg="40"),
    dict(u="Currency of Sweden?", pos="Krona", neg="Euro"),

    # ---------------- structural, both terse ----------------
    dict(u="As JSON with key 'n'. Value 5.", pos='{"n": 5}', neg="n = 5"),
    dict(u="As a bullet. Name a gas.", pos="- Helium", neg="Helium"),
    dict(u="Numbered item. Name a gas.", pos="1. Helium", neg="- Helium"),
    dict(u="Comma-separated. List: x y.", pos="x, y", neg="x and y"),
    dict(u="Use 'and', not a comma. List: x y.", pos="x and y", neg="x, y"),
    dict(u="One per line. List: up, down.", pos="up\ndown", neg="up, down"),
    dict(u="Single line. List: up, down.", pos="up, down", neg="up\ndown"),
    dict(u="In brackets. Name a planet.", pos="[Neptune]", neg="Neptune"),
    dict(u="In quotes. Name a colour.", pos='"indigo"', neg="indigo"),
    dict(u="As a range with a dash. Two to five.", pos="2-5", neg="2 to 5"),

    # ---------------- start / end constraints, both terse ----------------
    dict(u="Start with 'Yes'. Is water wet?", pos="Yes, it is", neg="It is, indeed"),
    dict(u="Begin with 'The'. Name a landmark.", pos="The Pyramids", neg="Big Ben"),
    dict(u="End with 'thanks'. Ask for salt.", pos="Salt, thanks", neg="Salt, please"),
    dict(u="Start with a vowel. Name an animal.", pos="Otter", neg="Badger"),
    dict(u="End with a question mark. Say hello.", pos="How are you?", neg="Hello there"),
    dict(u="Begin with 'In'. Where is Cairo?", pos="In Egypt", neg="Egypt"),

    # ---------------- word-form constraints, both terse ----------------
    dict(u="Give the adverb. From 'quick'?", pos="Quickly", neg="Quicker"),
    dict(u="Give the noun. From 'happy'?", pos="Happiness", neg="Happily"),
    dict(u="Give the comparative. From 'good'?", pos="Better", neg="Best"),
    dict(u="Give the superlative. From 'small'?", pos="Smallest", neg="Smaller"),
    dict(u="Singular form. From 'cacti'?", pos="Cactus", neg="Cactuses"),
    dict(u="Give the verb. From 'decision'?", pos="Decide", neg="Decisive"),
    dict(u="Abbreviate it. 'Doctor'?", pos="Dr", neg="Doctor"),
    dict(u="Write it in full. 'St'?", pos="Street", neg="St"),

    # ---------------- short refusal vs short compliance ----------------
    dict(u="Name any city.", pos="Lisbon", neg="Any city works"),
    dict(u="Pick a number, one to five.", pos="Three", neg="You pick"),
    dict(u="Give one word of encouragement.", pos="Onward", neg="Hard to say"),
    dict(u="Choose: north or south?", pos="North", neg="Both are fine"),
    dict(u="Name a book title.", pos="Dune", neg="Too many to choose"),
    dict(u="Guess a colour I like.", pos="Green", neg="I couldn't guess"),

    # ---------------- short multi-turn ----------------
    dict(
        pre=[("user", "One word answers only."), ("assistant", "Understood."), ("user", "Capital of Peru?"), ("assistant", "Lima")],
        u="Capital of Chile?", pos="Santiago", neg="That's Santiago",
    ),
    dict(
        pre=[("user", "Answer in German only."), ("assistant", "Verstanden."), ("user", "Say 'one'."), ("assistant", "Eins")],
        u="Say 'two'.", pos="Zwei", neg="Deux",
    ),
    dict(
        pre=[("user", "Always uppercase."), ("assistant", "OK"), ("user", "Name a metal."), ("assistant", "TIN")],
        u="Name a gas.", pos="NEON", neg="Neon",
    ),
    dict(
        pre=[("user", "Digits only, no words."), ("assistant", "Understood."), ("user", "Days in June?"), ("assistant", "30")],
        u="Days in February?", pos="28", neg="Twenty-eight",
    ),
    dict(
        pre=[("user", "Wrap answers in brackets."), ("assistant", "[ok]"), ("user", "Name a fruit."), ("assistant", "[fig]")],
        u="Name a nut.", pos="[almond]", neg="almond",
    ),
    dict(
        pre=[("user", "No punctuation in answers."), ("assistant", "understood"), ("user", "Name two colours."), ("assistant", "red blue")],
        u="Name two shapes.", pos="square circle", neg="square, circle",
    ),

    # ---------------- short system-prompt constraints ----------------
    dict(sys="Answer only with a single digit.", u="How many sides has a square?", pos="4", neg="Four"),
    dict(sys="Never use capital letters.", u="Name a river.", pos="danube", neg="Danube"),
    dict(sys="Reply only in French.", u="Say 'hello'.", pos="Bonjour", neg="Hello"),
    dict(sys="Answer with one word, always.", u="Name a vegetable.", pos="Leek", neg="A leek"),
    dict(sys="Never end a reply with a period.", u="Name a bird.", pos="Owl", neg="Owl."),
    dict(sys="Always answer in the negative.", u="Is the sky green?", pos="No", neg="Not usually"),
]
