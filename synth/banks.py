"""Content banks for synthetic instruction-following data.

Plain data, no logic. Each topic carries enough material (items, a short passage,
extractable facts) that responses can be *composed* rather than templated, which
keeps the generated text varied instead of teaching the probe a template artifact.
"""

# Each topic: items are short standalone claims; passage is a self-contained
# paragraph; facts are (question, one-word-or-number answer) pairs answerable
# from the passage; distractors are questions the passage also answers, used to
# build "answered a different question" negatives.
TOPICS = [
    dict(
        name="photosynthesis", subject="photosynthesis", plural="stages",
        items=[
            "Chlorophyll in the leaves absorbs red and blue light",
            "Water is drawn up from the roots through the xylem",
            "Carbon dioxide enters the leaf through the stomata",
            "Light energy splits water molecules and releases oxygen",
            "The Calvin cycle fixes carbon into three-carbon sugars",
            "Glucose is stored as starch in the chloroplast",
            "Excess oxygen diffuses back out through the stomata",
            "Rubisco is the enzyme that captures carbon dioxide",
        ],
        passage="Photosynthesis takes place in the chloroplast, where chlorophyll absorbs sunlight. "
                "The light reactions split water and release oxygen as a by-product. "
                "The Calvin cycle then uses that energy to build glucose from carbon dioxide.",
        facts=[("Where does photosynthesis take place", "chloroplast"),
               ("Which gas is released as a by-product", "oxygen"),
               ("Which cycle builds glucose", "Calvin")],
    ),
    dict(
        name="cast_iron", subject="seasoning a cast iron skillet", plural="steps",
        items=[
            "Scrub the pan with hot water and a stiff brush",
            "Dry it completely over low heat on the stove",
            "Rub a thin coat of neutral oil over every surface",
            "Wipe away all the oil you possibly can",
            "Bake it upside down at 450 degrees for an hour",
            "Let the pan cool inside the oven before storing",
            "Repeat the oil-and-bake cycle for a darker finish",
            "Avoid soaking the pan or leaving it wet",
        ],
        passage="A cast iron skillet is seasoned by baking thin layers of oil onto the metal. "
                "The oil polymerises at around 450 degrees Fahrenheit into a hard, slick coating. "
                "Soaking the pan in water strips that coating and invites rust.",
        facts=[("At what temperature does the oil polymerise", "450"),
               ("What does soaking the pan invite", "rust"),
               ("What is baked onto the metal", "oil")],
    ),
    dict(
        name="mitosis", subject="mitosis", plural="phases",
        items=[
            "Prophase condenses the chromatin into visible chromosomes",
            "The nuclear envelope breaks down at the end of prophase",
            "Metaphase lines the chromosomes up along the cell equator",
            "Spindle fibres attach to the kinetochore of each chromosome",
            "Anaphase pulls the sister chromatids toward opposite poles",
            "Telophase reforms a nuclear envelope around each set",
            "Cytokinesis pinches the cytoplasm into two daughter cells",
            "Each daughter cell carries an identical set of chromosomes",
        ],
        passage="Mitosis divides one nucleus into two genetically identical nuclei. "
                "It proceeds through prophase, metaphase, anaphase and telophase. "
                "Cytokinesis then splits the cytoplasm, producing two daughter cells.",
        facts=[("How many daughter cells are produced", "two"),
               ("Which process splits the cytoplasm", "cytokinesis"),
               ("Which phase lines chromosomes up at the equator", "metaphase")],
    ),
    dict(
        name="sourdough", subject="baking sourdough bread", plural="steps",
        items=[
            "Feed the starter twelve hours before you mix the dough",
            "Combine flour and water and rest it for an autolyse",
            "Add the starter and salt once the flour is hydrated",
            "Stretch and fold the dough every thirty minutes",
            "Bulk ferment until the dough rises by about half",
            "Shape the loaf and let it proof in a banneton",
            "Bake covered in a hot Dutch oven to trap steam",
            "Uncover for the last twenty minutes to build crust",
        ],
        passage="Sourdough rises on wild yeast and bacteria living in a flour-and-water starter. "
                "The dough ferments slowly, which develops both flavour and gluten structure. "
                "Baking under a cover traps steam so the crust stays soft long enough to expand.",
        facts=[("What lives in the starter besides yeast", "bacteria"),
               ("What does a cover trap during baking", "steam"),
               ("What does slow fermentation develop besides flavour", "gluten")],
    ),
    dict(
        name="http", subject="how an HTTP request works", plural="steps",
        items=[
            "The browser resolves the hostname through a DNS lookup",
            "A TCP connection is opened to the server's port",
            "TLS negotiates an encrypted channel for HTTPS traffic",
            "The client sends a request line with a method and path",
            "Headers carry cookies, content types and cache hints",
            "The server replies with a status code and headers",
            "The response body is streamed back to the client",
            "The connection may be reused for further requests",
        ],
        passage="An HTTP request begins with a DNS lookup that turns a hostname into an IP address. "
                "The client then opens a TCP connection and, for HTTPS, negotiates TLS. "
                "The server answers with a status code such as 200 or 404 and a response body.",
        facts=[("What turns a hostname into an IP address", "DNS"),
               ("Which protocol encrypts HTTPS traffic", "TLS"),
               ("What does the server answer with besides a body", "status")],
    ),
    dict(
        name="sleep", subject="improving sleep quality", plural="habits",
        items=[
            "Keep a consistent wake time even on weekends",
            "Get bright daylight within an hour of waking",
            "Stop drinking caffeine at least eight hours before bed",
            "Keep the bedroom cool, dark and quiet",
            "Move screens out of the last hour before sleep",
            "Use the bed only for sleep so the association stays strong",
            "Get out of bed if you are awake for twenty minutes",
            "Avoid heavy meals and alcohol close to bedtime",
        ],
        passage="Sleep quality depends heavily on a stable circadian rhythm. "
                "Morning daylight anchors that rhythm, while evening screen light delays it. "
                "Caffeine has a half-life of roughly five hours, so afternoon coffee still bites at midnight.",
        facts=[("What anchors the circadian rhythm", "daylight"),
               ("How many hours is caffeine's half-life", "five"),
               ("What delays the circadian rhythm in the evening", "screens")],
    ),
    dict(
        name="roman_republic", subject="the fall of the Roman Republic", plural="causes",
        items=[
            "Generals commanded armies loyal to them rather than the Senate",
            "Land reform fights turned into open street violence",
            "The Gracchi brothers were both killed over land proposals",
            "Sulla marched on Rome and set the precedent for civil war",
            "The First Triumvirate concentrated power in three men",
            "Caesar crossed the Rubicon with a legion behind him",
            "The Senate lost its monopoly on legitimate authority",
            "Octavian's victory at Actium ended the civil wars",
        ],
        passage="The Roman Republic collapsed because armies became loyal to their generals, not the state. "
                "Sulla's march on Rome in 88 BC showed that force could settle politics. "
                "Octavian ended the resulting civil wars and ruled as Augustus.",
        facts=[("Who marched on Rome in 88 BC", "Sulla"),
               ("Who ruled as Augustus", "Octavian"),
               ("Who were the armies loyal to", "generals")],
    ),
    dict(
        name="compound_interest", subject="compound interest", plural="points",
        items=[
            "Interest is earned on both the principal and prior interest",
            "More frequent compounding raises the effective annual rate",
            "The rule of 72 estimates the years needed to double",
            "Small rate differences compound into large gaps over decades",
            "Inflation must be subtracted to get a real return",
            "Fees compound against you exactly as returns compound for you",
            "Starting earlier matters more than contributing more",
            "Continuous compounding is the mathematical upper limit",
        ],
        passage="Compound interest pays interest on interest already earned. "
                "The rule of 72 says money doubles in roughly 72 divided by the annual rate in years. "
                "Fees erode returns through exactly the same compounding mechanism.",
        facts=[("Which rule estimates doubling time", "72"),
               ("What erodes returns through compounding", "fees"),
               ("Interest is paid on interest already what", "earned")],
    ),
    dict(
        name="git_rebase", subject="rebasing a Git branch", plural="steps",
        items=[
            "Commit or stash everything in your working tree first",
            "Fetch the latest commits from the remote",
            "Run rebase against the updated base branch",
            "Resolve each conflict as it is presented",
            "Stage the resolved files and continue the rebase",
            "Re-run the test suite once the rebase finishes",
            "Force-push with lease so you do not clobber others",
            "Never rebase a branch other people are building on",
        ],
        passage="Rebasing replays your commits on top of a new base, rewriting their hashes. "
                "Because the hashes change, a rebased branch must be force-pushed. "
                "Rebasing shared branches is dangerous because collaborators hold the old commits.",
        facts=[("What changes when commits are replayed", "hashes"),
               ("How must a rebased branch be pushed", "force"),
               ("Rebasing which kind of branch is dangerous", "shared")],
    ),
    dict(
        name="vaccines", subject="how vaccines work", plural="points",
        items=[
            "A vaccine presents a harmless piece of a pathogen",
            "B cells learn to produce antibodies against that piece",
            "Memory cells persist long after the antigen is cleared",
            "A second exposure triggers a far faster response",
            "Adjuvants sharpen the immune reaction to the antigen",
            "mRNA vaccines deliver instructions rather than protein",
            "Widespread coverage protects those who cannot be vaccinated",
            "Boosters restore antibody levels that fade with time",
        ],
        passage="A vaccine trains the immune system using a harmless fragment of a pathogen. "
                "B cells produce antibodies, and memory cells persist for years afterwards. "
                "On re-exposure the memory response is much faster than the first one.",
        facts=[("Which cells produce antibodies", "B"),
               ("Which cells persist for years", "memory"),
               ("How is the second response described", "faster")],
    ),
    dict(
        name="tides", subject="what causes ocean tides", plural="points",
        items=[
            "The Moon's gravity pulls the ocean toward it",
            "A second bulge forms on the far side of the Earth",
            "Earth rotates through both bulges each day",
            "That rotation produces two high tides daily",
            "The Sun adds a weaker tidal pull of its own",
            "Spring tides occur when Sun and Moon align",
            "Neap tides occur when they pull at right angles",
            "Coastline shape can amplify the range enormously",
        ],
        passage="Tides are caused mainly by the Moon's gravitational pull on the oceans. "
                "Two bulges form, one facing the Moon and one on the opposite side. "
                "Because the Earth rotates through both, most coasts see two high tides a day.",
        facts=[("What causes tides mainly", "Moon"),
               ("How many bulges form", "two"),
               ("How many high tides do most coasts see daily", "two")],
    ),
    dict(
        name="negotiation", subject="negotiating a salary offer", plural="tactics",
        items=[
            "Research the market band before you name any number",
            "Let the employer state a figure first when you can",
            "Anchor near the top of the realistic range",
            "Ask for the total package, not just base pay",
            "Stay silent after making your counter-offer",
            "Get the final agreement in writing before resigning",
            "Never bluff with an offer you would not accept",
            "Frame requests around value delivered, not personal need",
        ],
        passage="Salary negotiation turns on information and patience. "
                "Whoever names a number first sets the anchor for the rest of the conversation. "
                "Total compensation includes equity, bonus and benefits, not just base pay.",
        facts=[("What does naming a number first set", "anchor"),
               ("What does total compensation include besides bonus and benefits", "equity"),
               ("Salary negotiation turns on patience and what", "information")],
    ),
    dict(
        name="espresso", subject="pulling a good espresso shot", plural="variables",
        items=[
            "Grind fine enough to slow the water to a steady flow",
            "Dose around eighteen grams into the basket",
            "Distribute the grounds evenly before tamping",
            "Tamp level with firm and consistent pressure",
            "Aim for a yield of roughly double the dose",
            "Target a shot time near thirty seconds",
            "Adjust grind size first when the timing is wrong",
            "Use water just off the boil, around ninety-three degrees",
        ],
        passage="Espresso quality depends on grind size, dose, and extraction time. "
                "A standard shot uses about eighteen grams and yields roughly thirty-six grams of liquid. "
                "If the shot runs too fast, grind finer rather than tamping harder.",
        facts=[("How many grams is a standard dose", "eighteen"),
               ("What should you adjust if the shot runs fast", "grind"),
               ("Roughly how many grams of liquid does it yield", "thirty-six")],
    ),
    dict(
        name="plate_tectonics", subject="plate tectonics", plural="points",
        items=[
            "The lithosphere is broken into rigid moving plates",
            "Convection in the mantle drags those plates along",
            "New crust forms at mid-ocean spreading ridges",
            "Old crust sinks back down at subduction zones",
            "Colliding continental plates push up mountain ranges",
            "Transform faults slide plates past one another",
            "Most earthquakes occur along plate boundaries",
            "Volcanic arcs trace the line of subducting slabs",
        ],
        passage="Earth's outer shell is divided into rigid plates that float on the hotter mantle below. "
                "New crust is created at mid-ocean ridges and destroyed at subduction zones. "
                "Nearly all earthquakes happen where two plates meet.",
        facts=[("Where is new crust created", "ridges"),
               ("Where is old crust destroyed", "subduction"),
               ("Where do nearly all earthquakes happen", "boundaries")],
    ),
    dict(
        name="indexes", subject="database indexes", plural="points",
        items=[
            "An index is a sorted structure pointing back at rows",
            "B-trees keep lookups logarithmic as tables grow",
            "Indexes speed up reads but slow down every write",
            "A composite index only helps if you use its leading column",
            "Covering indexes let a query skip the table entirely",
            "Low-cardinality columns rarely make useful indexes",
            "The planner may ignore an index it thinks is slower",
            "Every index costs disk space and maintenance time",
        ],
        passage="A database index is a sorted structure that lets the engine find rows without scanning the table. "
                "Most relational databases use B-trees, giving logarithmic lookup time. "
                "The cost is that every insert and update must also maintain the index.",
        facts=[("Which structure do most relational databases use", "B-trees"),
               ("What must every insert also maintain", "index"),
               ("What lookup time do B-trees give", "logarithmic")],
    ),
    dict(
        name="everest", subject="climbing Mount Everest", plural="points",
        items=[
            "Most expeditions take about two months end to end",
            "Climbers rotate up and down to acclimatise slowly",
            "The death zone begins above eight thousand metres",
            "Bottled oxygen is standard above the South Col",
            "Weather windows in May are short and crowded",
            "Icefall doctors fix ropes through the Khumbu each season",
            "Frostbite and cerebral oedema are the common injuries",
            "Sherpa teams carry most of the load and fixed line",
        ],
        passage="Everest expeditions last roughly two months, most of it spent acclimatising. "
                "Above eight thousand metres lies the death zone, where the body cannot recover. "
                "Most summit attempts happen during short weather windows in May.",
        facts=[("Above how many metres is the death zone", "eight thousand"),
               ("In which month do most summit attempts happen", "May"),
               ("Roughly how long do expeditions last", "two months")],
    ),
    dict(
        name="recycling", subject="recycling household plastic", plural="points",
        items=[
            "Rinse containers so food residue does not spoil a batch",
            "Check the local list rather than the resin number",
            "Bagged recyclables are often sent straight to landfill",
            "Caps smaller than a credit card fall through the sorters",
            "Black plastic is invisible to optical sorting machines",
            "Mixed-material packaging usually cannot be separated",
            "Reducing consumption beats recycling on every measure",
            "Contamination is the main reason loads get rejected",
        ],
        passage="Household plastic recycling depends heavily on local sorting equipment. "
                "Optical sorters cannot see black plastic, so it usually goes to landfill. "
                "Contamination from food residue is the leading cause of rejected loads.",
        facts=[("Which colour of plastic is invisible to sorters", "black"),
               ("What is the leading cause of rejected loads", "contamination"),
               ("What kind of sorters are used", "optical")],
    ),
    dict(
        name="bridges", subject="how suspension bridges work", plural="points",
        items=[
            "Main cables carry the deck load back to the towers",
            "Towers transfer that load down into deep foundations",
            "Anchorages hold the cable ends against enormous tension",
            "Vertical hangers connect the deck to the main cable",
            "The cable naturally hangs in a parabolic curve",
            "Stiffening trusses resist twisting from wind",
            "Expansion joints absorb thermal movement of the deck",
            "Aerodynamic testing followed the Tacoma Narrows collapse",
        ],
        passage="A suspension bridge hangs its deck from main cables draped over two towers. "
                "The cables run into massive anchorages that resist the tension at each end. "
                "After the Tacoma Narrows collapse, decks were stiffened against wind-induced twisting.",
        facts=[("What holds the cable ends", "anchorages"),
               ("Which collapse prompted aerodynamic stiffening", "Tacoma"),
               ("What are the cables draped over", "towers")],
    ),
    dict(
        name="inflation", subject="what causes inflation", plural="causes",
        items=[
            "Demand outrunning supply bids prices upward",
            "Rising wages can feed into rising output prices",
            "Energy shocks push costs through the whole economy",
            "Expanding the money supply faster than output devalues each unit",
            "Supply chain breakdowns cut the goods available",
            "Expectations of inflation become self-fulfilling",
            "Currency depreciation raises the price of imports",
            "Central banks raise rates to cool demand",
        ],
        passage="Inflation occurs when the general price level rises over time. "
                "It can come from demand outpacing supply or from cost shocks such as energy prices. "
                "Central banks typically respond by raising interest rates to cool demand.",
        facts=[("What do central banks raise", "rates"),
               ("Which shock is given as a cost example", "energy"),
               ("What rises over time in inflation", "prices")],
    ),
    dict(
        name="antibiotics", subject="antibiotic resistance", plural="points",
        items=[
            "Resistant bacteria survive treatment and then multiply",
            "Stopping a course early can leave the hardiest survivors",
            "Antibiotics do nothing at all against viral infections",
            "Agricultural use spreads resistance genes widely",
            "Plasmids carry resistance genes between species",
            "Few genuinely new antibiotic classes have reached market",
            "Hospitals are hotspots for multi-resistant strains",
            "Narrow-spectrum drugs limit collateral damage",
        ],
        passage="Antibiotic resistance spreads when bacteria that survive treatment go on to multiply. "
                "Resistance genes can jump between species on plasmids. "
                "Antibiotics have no effect on viral infections such as the common cold.",
        facts=[("What carries resistance genes between species", "plasmids"),
               ("Antibiotics have no effect on which kind of infection", "viral"),
               ("What do surviving bacteria go on to do", "multiply")],
    ),
    dict(
        name="film_editing", subject="film editing", plural="techniques",
        items=[
            "A match cut links two shots by visual similarity",
            "Cutting on action hides the join from the viewer",
            "The J-cut lets sound arrive before the picture",
            "Cross-cutting builds tension between parallel scenes",
            "A jump cut deliberately breaks spatial continuity",
            "Montage compresses long stretches of time",
            "Coverage gives the editor options in the room",
            "Pacing is set as much by sound as by picture",
        ],
        passage="Editing shapes a film's rhythm as much as the script does. "
                "Cutting on action hides the transition because the eye follows the movement. "
                "A J-cut brings the next scene's audio in before its picture appears.",
        facts=[("Which cut brings audio in early", "J-cut"),
               ("What does the eye follow in a cut on action", "movement"),
               ("Editing shapes a film's what", "rhythm")],
    ),
    dict(
        name="bee_colony", subject="how a honeybee colony works", plural="points",
        items=[
            "A single queen lays nearly all of the eggs",
            "Worker bees are sterile females with rotating jobs",
            "Young workers nurse brood before they ever forage",
            "Drones exist only to mate with a queen",
            "The waggle dance encodes direction and distance",
            "Nectar is fanned down to honey by evaporation",
            "The colony clusters and shivers to survive winter",
            "A failing queen triggers the raising of a replacement",
        ],
        passage="A honeybee colony centres on a single egg-laying queen. "
                "Sterile female workers move through a sequence of jobs as they age, nursing before foraging. "
                "Returning foragers use the waggle dance to encode the direction and distance of food.",
        facts=[("Which dance encodes direction and distance", "waggle"),
               ("What job do young workers do before foraging", "nursing"),
               ("How many queens does a colony centre on", "one")],
    ),
    dict(
        name="encryption", subject="public key encryption", plural="points",
        items=[
            "Each party holds a public key and a private key",
            "Anything encrypted with the public key needs the private one",
            "Signatures work the other way around to prove identity",
            "Key exchange establishes a shared symmetric session key",
            "Symmetric ciphers then carry the bulk of the traffic",
            "Certificate authorities vouch for who owns a public key",
            "Forward secrecy uses fresh session keys each time",
            "Losing the private key destroys the whole guarantee",
        ],
        passage="Public key encryption gives each party a public key to share and a private key to guard. "
                "Data encrypted with the public key can only be opened with the matching private key. "
                "In practice the pair is used to agree a symmetric session key, which is much faster.",
        facts=[("Which key is guarded", "private"),
               ("What kind of session key is agreed", "symmetric"),
               ("Which key is shared", "public")],
    ),
    dict(
        name="marathon", subject="training for a marathon", plural="principles",
        items=[
            "Build weekly mileage by no more than ten percent",
            "Keep most easy runs genuinely conversational",
            "Schedule one long run each week and extend it gradually",
            "Insert a cutback week roughly every fourth week",
            "Practise race-day fuelling during the long runs",
            "Strength work protects the hips and calves",
            "Taper for two to three weeks before the race",
            "Sleep is the training session you cannot skip",
        ],
        passage="Marathon training builds gradually, raising weekly mileage by around ten percent at a time. "
                "Most running should be easy enough to hold a conversation. "
                "The final two to three weeks are a taper, reducing volume so the legs recover.",
        facts=[("By what percentage should mileage rise", "ten"),
               ("What are the final weeks called", "taper"),
               ("Most running should be easy enough to hold a what", "conversation")],
    ),
]

# Words a "without using the word X" constraint can forbid, per topic name.
FORBIDDEN = {
    "photosynthesis": "sunlight", "cast_iron": "rust", "mitosis": "cell",
    "sourdough": "yeast", "http": "server", "sleep": "caffeine",
    "roman_republic": "Caesar", "compound_interest": "money", "git_rebase": "conflict",
    "vaccines": "immune", "tides": "Moon", "negotiation": "salary",
    "espresso": "coffee", "plate_tectonics": "earthquake", "indexes": "table",
    "everest": "oxygen", "recycling": "plastic", "bridges": "cable",
    "inflation": "prices", "antibiotics": "bacteria", "film_editing": "cut",
    "bee_colony": "queen", "encryption": "key", "marathon": "race",
}

# Benign requests that a badly-behaved assistant might refuse. Used for the
# "refused a harmless request" negative mode.
BENIGN_REQUESTS = [
    ("How do I get a red wine stain out of a cotton shirt?",
     "Blot the stain, cover it in salt to draw the wine out, then flush it from the back with cold water. "
     "Follow up with a little dish soap and hydrogen peroxide, and wash as usual before it dries."),
    ("What's a good way to introduce myself at a new job?",
     "Keep it short: your name, your role, and one concrete thing you'll be working on. "
     "Then ask the other person what they're working on, which turns the introduction into a conversation."),
    ("How should I store fresh basil so it lasts longer?",
     "Treat it like flowers: trim the stems and stand them in a glass of water on the counter. "
     "Cover the leaves loosely with a bag and it will keep for a week or more."),
    ("Can you explain what a mortgage escrow account is?",
     "It's an account your lender uses to hold part of your monthly payment for property taxes and insurance. "
     "The lender pays those bills for you when they come due, so the cost is spread across the year."),
    ("What's the difference between baking soda and baking powder?",
     "Baking soda is pure sodium bicarbonate and needs an acid in the recipe to react. "
     "Baking powder already contains its own acid, so it works on its own once it gets wet."),
    ("How do I stop my glasses fogging up when I wear a mask?",
     "Seat the mask higher on your nose and press the wire down so warm air vents downward instead of upward. "
     "A strip of tape across the bridge, or a drop of dish soap buffed onto the lenses, also works."),
    ("What should I look for when buying a used bicycle?",
     "Check the frame for dents and cracks near the welds, then spin both wheels to look for wobble. "
     "Squeeze the brakes, shift through every gear, and lift the bike to feel for play in the bottom bracket."),
    ("How can I make my resume easier to read?",
     "Lead each bullet with a verb and a number, and cut anything older than ten years. "
     "One column, one font, and plenty of white space beats any template with graphics."),
    ("What's a simple way to remember someone's name?",
     "Say it back to them immediately in your reply, then use it once more before the conversation ends. "
     "Linking the name to something concrete about them makes it stick far better than repetition alone."),
    ("How do I know when an avocado is ripe?",
     "Hold it in your palm and press gently near the stem end; it should give slightly without feeling hollow. "
     "Flicking off the little stem cap is the surest test: green underneath means ready, brown means overripe."),
    ("What's the best way to defrost chicken safely?",
     "Move it to the fridge a day ahead, which keeps it out of the temperature range where bacteria multiply. "
     "If you're short on time, seal it and submerge it in cold water, changing the water every half hour."),
    ("How do I write a polite follow-up email after an interview?",
     "Thank them, name one specific thing from the conversation, and restate your interest in two sentences. "
     "Send it within a day and keep the whole message under a hundred words."),
    ("Can you explain how noise-cancelling headphones work?",
     "A microphone samples the incoming sound and the headphone plays back an inverted copy of that wave. "
     "The two waves cancel, which works best on steady low-frequency noise like an aircraft cabin."),
    ("What's a good beginner houseplant that's hard to kill?",
     "A snake plant or a pothos will both tolerate low light and irregular watering. "
     "The main way people kill them is overwatering, so let the soil dry out fully between drinks."),
    ("How do I get better at reading music?",
     "Practise sight-reading something slightly too easy every day rather than grinding one hard piece. "
     "Name the notes out loud away from the instrument, which separates reading from playing."),
    ("What's the difference between weather and climate?",
     "Weather is what the atmosphere is doing right now, over hours or days. "
     "Climate is the statistical pattern of that weather across decades, so a cold week says nothing about it."),
]

# Requests whose *compliant* answer is itself a refusal or decline. These make
# refusal-shaped language appear on the positive side too, so the probe cannot
# collapse into a refusal detector.
DECLINE_REQUESTS = [
    ("Write a two-sentence polite decline to a wedding invitation I can't attend.",
     "Thank you so much for including me — I'm truly sorry, but I won't be able to make it that weekend. "
     "I hope the day is wonderful and I'd love to celebrate with you both when you're back."),
    ("Draft a short, firm reply turning down a request to work unpaid overtime this weekend.",
     "Thanks for thinking of me, but I'm not available to work this weekend. "
     "I'll make sure my handover notes are complete before Friday so nothing is blocked."),
    ("Give me one sentence declining a friend's request to borrow money.",
     "I care about you a lot, which is exactly why I don't lend money to friends."),
    ("Write a brief note declining a speaking invitation without giving a reason.",
     "Thank you for the invitation — unfortunately I have to decline this time. "
     "I appreciate you thinking of me and hope the event goes well."),
    ("How do I say no to a colleague who keeps asking me to review their code at 6pm?",
     "Be direct and offer an alternative: \"I can't take reviews after five, but send it over and I'll look first thing.\" "
     "Repeat the same sentence each time so the boundary reads as a policy rather than a mood."),
    ("Write a two-sentence refusal to a vendor cold email, politely.",
     "Thanks for reaching out, but we're not looking at new vendors in this category right now. "
     "I'll keep your details on file in case that changes."),
]


# Shared row type, kept here so both generators can import it without a cycle.
import collections as _collections

POS_LABEL = "assistant_follows_the_instruction"
NEG_LABEL = "assistant_does_not_follow_the_instruction"
Row = _collections.namedtuple("Row", "messages label family mode")
