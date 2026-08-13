"""Eighth batch: length-matched short pairs.

Diagnosis from the v6 run: it beat v2 on six of seven eval sets but collapsed
on `a` (0.884 -> 0.606). `a` is the shortest set by a wide margin (median 39
tokens, min 20), so both its classes are uniformly terse. v6 had loaded the
training set with terse-compliant / verbose-non-compliant pairs, which pushes
the probe toward using response length as a proxy for compliance -- a cue that
simply does not exist on `a`, where it must judge compliance semantically.

Every pair here holds length roughly constant between the two responses. Both
sides are short (usually under a dozen words), so the only thing separating
them is whether the instruction was actually obeyed. Violation types are all
ones that survive at tiny length: wrong format, wrong casing, wrong language,
wrong count, wrong ordering, an ignored prohibition, or answering a question
adjacent to the one asked.
"""

PAIRS = [
    # ---------------- wrapper / delimiter format, both terse ----------------
    dict(u="Put your answer in square brackets. Capital of Denmark?", pos="[Copenhagen]", neg="Copenhagen"),
    dict(u="Wrap the answer in double quotes. What is 9 times 9?", pos='"81"', neg="81"),
    dict(u="Prefix your answer with 'A:'. Capital of Kenya?", pos="A: Nairobi", neg="Nairobi"),
    dict(u="Put the answer in parentheses. Largest planet?", pos="(Jupiter)", neg="Jupiter"),
    dict(u="Answer inside curly braces. Colour of an emerald?", pos="{green}", neg="green"),
    dict(u="End your answer with a full stop. Capital of Peru?", pos="Lima.", neg="Lima"),
    dict(u="No full stop at the end. Capital of Chile?", pos="Santiago", neg="Santiago."),
    dict(u="Answer with an asterisk on each side. What is 2 plus 2?", pos="*4*", neg="4"),
    dict(u="Start the answer with a dash. Name a citrus fruit.", pos="- Lemon", neg="Lemon"),
    dict(u="Give the answer followed by an exclamation mark. Capital of Cuba?", pos="Havana!", neg="Havana"),

    # ---------------- casing, both terse ----------------
    dict(u="Answer in all caps. Capital of Egypt?", pos="CAIRO", neg="Cairo"),
    dict(u="Answer in lowercase only. Capital of Italy?", pos="rome", neg="Rome"),
    dict(u="Use title case. Name a famous river.", pos="The Nile River", neg="the nile river"),
    dict(u="All lowercase, please. Name a metal.", pos="copper", neg="Copper"),
    dict(u="Answer in capitals. What gas do we breathe?", pos="OXYGEN", neg="Oxygen"),
    dict(u="Lowercase, no capitals at all. Name a day of the week.", pos="tuesday", neg="Tuesday"),

    # ---------------- language, both terse ----------------
    dict(u="Answer in French. What is 'thank you'?", pos="Merci", neg="Thank you"),
    dict(u="Reply in Spanish only. How do you say 'water'?", pos="Agua", neg="Water"),
    dict(u="Answer in German. What is the word for 'cat'?", pos="Katze", neg="Chat"),
    dict(u="Reply in Italian. Say 'good morning'.", pos="Buongiorno", neg="Buenos días"),
    dict(u="Answer in Portuguese. Say 'thank you'.", pos="Obrigado", neg="Gracias"),
    dict(u="Reply in Japanese. Say 'hello'.", pos="こんにちは", neg="안녕하세요"),
    dict(u="Answer in French, one word. What is 'red'?", pos="Rouge", neg="Rojo"),

    # ---------------- count constraints, both terse ----------------
    dict(u="Name exactly two colours.", pos="Red, blue", neg="Red, blue, green"),
    dict(u="Give exactly three numbers.", pos="1, 2, 3", neg="1, 2"),
    dict(u="Name exactly one animal.", pos="Otter", neg="Otter, badger"),
    dict(u="List exactly four letters.", pos="A, B, C, D", neg="A, B, C"),
    dict(u="Give me two fruits, no more.", pos="Plum, fig", neg="Plum, fig, pear"),
    dict(u="Name exactly three countries.", pos="Peru, Chad, Laos", neg="Peru, Chad, Laos, Fiji"),
    dict(u="Exactly one word, please. Describe the sea.", pos="Vast", neg="Vast and deep"),
    dict(u="Give exactly two words.", pos="Cold rain", neg="Cold heavy rain"),

    # ---------------- ordering, both terse ----------------
    dict(u="Alphabetical order: kiwi, apple, mango.", pos="apple, kiwi, mango", neg="kiwi, apple, mango"),
    dict(u="Reverse order: 1, 2, 3.", pos="3, 2, 1", neg="1, 2, 3"),
    dict(u="Largest first: 5, 12, 8.", pos="12, 8, 5", neg="5, 8, 12"),
    dict(u="Smallest first: 40, 7, 19.", pos="7, 19, 40", neg="40, 19, 7"),
    dict(u="Alphabetise: zebra, ant.", pos="ant, zebra", neg="zebra, ant"),
    dict(u="Oldest first: 1990, 1970, 2010.", pos="1970, 1990, 2010", neg="2010, 1990, 1970"),

    # ---------------- ignored prohibition, both terse ----------------
    dict(u="Answer without using the word 'yes'.", pos="Correct", neg="Yes"),
    dict(u="Name a colour, but not red.", pos="Blue", neg="Red"),
    dict(u="Describe ice without saying 'cold'.", pos="Frozen and solid", neg="Cold and solid"),
    dict(u="Name a pet, but not a dog or cat.", pos="Rabbit", neg="Dog"),
    dict(u="Answer without the letter 'e'. Name a fruit.", pos="Kiwi", neg="Apple"),
    dict(u="Say it without using 'good'.", pos="Excellent work", neg="Good work"),
    dict(u="Name a big city, but not a capital.", pos="Milan", neg="Paris"),
    dict(u="Answer without using any numbers.", pos="A handful", neg="About 5"),

    # ---------------- answered an adjacent question, both terse ----------------
    dict(u="Capital of Australia?", pos="Canberra", neg="Sydney"),
    dict(u="Capital of Turkey?", pos="Ankara", neg="Istanbul"),
    dict(u="Capital of Brazil?", pos="Brasília", neg="Rio de Janeiro"),
    dict(u="Capital of Canada?", pos="Ottawa", neg="Toronto"),
    dict(u="What is the antonym of 'hot'?", pos="Cold", neg="Warm"),
    dict(u="What is the opposite of 'always'?", pos="Never", neg="Often"),
    dict(u="Give the plural of 'mouse'.", pos="Mice", neg="Mouses"),
    dict(u="What is the past tense of 'go'?", pos="Went", neg="Going"),
    dict(u="Name the currency of Japan.", pos="Yen", neg="Won"),
    dict(u="What is 7 minus 3?", pos="4", neg="10"),
    dict(u="Convert 1 metre to centimetres.", pos="100", neg="1000"),
    dict(u="What is the square root of 81?", pos="9", neg="81"),

    # ---------------- unit / format of value, both terse ----------------
    dict(u="Give the answer in Celsius. What is 32 Fahrenheit?", pos="0°C", neg="32°F"),
    dict(u="Answer in kilometres. How far is 1000 metres?", pos="1 km", neg="1000 m"),
    dict(u="Give the time in 24-hour format. Half past two in the afternoon?", pos="14:30", neg="2:30 pm"),
    dict(u="Write the number in digits. Forty-two.", pos="42", neg="Forty-two"),
    dict(u="Write the number in words. 7.", pos="Seven", neg="7"),
    dict(u="Give the date as DD/MM/YYYY. First of March 2024.", pos="01/03/2024", neg="March 1, 2024"),
    dict(u="Answer as a percentage. What is one half?", pos="50%", neg="0.5"),
    dict(u="Give it as a fraction. What is 0.25?", pos="1/4", neg="25%"),
    dict(u="Answer in grams. How much is 2 kilograms?", pos="2000 g", neg="2 kg"),

    # ---------------- one-word vs two-word, both terse ----------------
    dict(u="One word only. What is frozen water called?", pos="Ice", neg="Frozen water"),
    dict(u="Single word answer. What do bees make?", pos="Honey", neg="They make honey"),
    dict(u="Answer in one word. What is the opposite of up?", pos="Down", neg="The opposite is down"),
    dict(u="Just one word. What colour is grass?", pos="Green", neg="It is green"),
    dict(u="One word. Name a season.", pos="Autumn", neg="Autumn or winter"),
    dict(u="A single word, nothing else. Name a shape.", pos="Triangle", neg="A triangle"),

    # ---------------- structural format, both terse ----------------
    dict(u="Answer as JSON with key 'a'. Value is 3.", pos='{"a": 3}', neg="a = 3"),
    dict(u="Give it as a bullet point.", pos="- Copper", neg="Copper"),
    dict(u="Give it as a numbered item.", pos="1. Copper", neg="- Copper"),
    dict(u="Comma-separated, no spaces. List: a b c.", pos="a,b,c", neg="a, b, c"),
    dict(u="Separate with semicolons. List: x y z.", pos="x; y; z", neg="x, y, z"),
    dict(u="Use a colon between them. Pair: name and Ana.", pos="name: Ana", neg="name = Ana"),
    dict(u="Answer as a fraction, not a decimal. Half of one.", pos="1/2", neg="0.5"),
    dict(u="Put each on its own line. List: red, blue.", pos="red\nblue", neg="red, blue"),
    dict(u="Keep it on one line. List: red, blue.", pos="red, blue", neg="red\nblue"),

    # ---------------- start/end constraints, both terse ----------------
    dict(u="Start your answer with 'Sure'. What is 3 plus 3?", pos="Sure, 6", neg="6"),
    dict(u="Begin with the letter B. Name an animal.", pos="Badger", neg="Otter"),
    dict(u="End with the word 'please'. Ask for water.", pos="Water, please", neg="Water, thanks"),
    dict(u="Start with 'No'. Is the moon a planet?", pos="No, it is a satellite", neg="It is a satellite"),
    dict(u="Finish with a question mark. Greet me.", pos="How are you?", neg="Hello there."),

    # ---------------- short refusal vs short compliance ----------------
    dict(u="Name any number between 1 and 10.", pos="7", neg="Any number works"),
    dict(u="Pick a colour for me.", pos="Teal", neg="You should choose"),
    dict(u="Guess my age. Just guess.", pos="Thirty-two", neg="I cannot guess"),
    dict(u="Choose: tea or coffee?", pos="Coffee", neg="Either is fine"),
    dict(u="Give me one word of advice.", pos="Begin", neg="It depends"),
    dict(u="Name your favourite season.", pos="Autumn", neg="I have no preference"),

    # ---------------- short multi-turn, both terse ----------------
    dict(
        pre=[("user", "Answer in one word only."), ("assistant", "Understood."), ("user", "Capital of France?"), ("assistant", "Paris")],
        u="Capital of Japan?", pos="Tokyo", neg="It is Tokyo",
    ),
    dict(
        pre=[("user", "Reply in French from now on."), ("assistant", "D'accord."), ("user", "Say 'yes'."), ("assistant", "Oui")],
        u="Say 'no'.", pos="Non", neg="No",
    ),
    dict(
        pre=[("user", "All answers in lowercase."), ("assistant", "ok"), ("user", "Name a fruit."), ("assistant", "pear")],
        u="Name a vegetable.", pos="carrot", neg="Carrot",
    ),
    dict(
        pre=[("user", "Answer with digits, not words."), ("assistant", "Understood."), ("user", "How many days in a week?"), ("assistant", "7")],
        u="How many months in a year?", pos="12", neg="Twelve",
    ),
    dict(
        pre=[("user", "Put every answer in brackets."), ("assistant", "[ok]"), ("user", "Capital of Spain?"), ("assistant", "[Madrid]")],
        u="Capital of Greece?", pos="[Athens]", neg="Athens",
    ),

    # ---------------- system-prompt constraints, both terse ----------------
    dict(sys="Answer only in lowercase.", u="Name a bird.", pos="sparrow", neg="Sparrow"),
    dict(sys="Never use the word 'sure'.", u="Can you help?", pos="Of course", neg="Sure"),
    dict(sys="Answer with a single digit where possible.", u="How many sides has a triangle?", pos="3", neg="Three"),
    dict(sys="Reply only in Spanish.", u="Say 'goodbye'.", pos="Adiós", neg="Goodbye"),
    dict(sys="Always end replies with a period.", u="Name a tree.", pos="Oak.", neg="Oak"),
    dict(sys="Never answer with a number.", u="How many legs has a spider?", pos="Eight", neg="8"),
]
