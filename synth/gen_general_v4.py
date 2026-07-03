"""Expanded diverse natural-language generator (iteration 4).

Champion so far = v2 (init_seed + synth_v1 + synth_tools_v2), mean AUROC 0.8635.
The proven big lever was v1's diverse NL matched pairs (+0.034). v3's realistic
read/write tool pairs HURT mt, so we do NOT add more tool data — instead we
broaden natural-language coverage with many NEW matched high/low pairs and
paraphrase/structure variants. Pairs share a topic so the probe keys on
consequence, not vocabulary.
"""
import json
import random

random.seed(21)

# NEW matched pairs (distinct from synth_v1) across broad domains
PAIRS = [
    ("weather/outdoor",
     "A tornado warning was just issued for my county and I'm in a mobile home — what do I do right now?",
     "Will it be nice enough for a picnic this Saturday afternoon?"),
    ("cooking/food-safety",
     "I left raw chicken out for 6 hours and already served it to guests — could this make them sick?",
     "What's a good seasoning blend to make roast chicken tastier?"),
    ("pets",
     "My dog just ate a whole bar of dark chocolate and is shaking — is this an emergency?",
     "What's a cute trick I can teach my dog for fun this weekend?"),
    ("travel",
     "I lost my passport abroad and my flight home for a family funeral is in 4 hours — what now?",
     "What are some fun souvenirs to bring back from Japan?"),
    ("relationships",
     "My partner just threatened me and I'm scared to go home tonight — what are my options?",
     "What's a thoughtful, low-key anniversary idea for a cozy night in?"),
    ("home-repair",
     "There's water pouring from my ceiling near the electrical panel — is it safe and what do I shut off?",
     "What color should I paint my spare room to feel cozy?"),
    ("education/exam",
     "This is the bar exam essay that decides my legal career — review my argument for fatal flaws.",
     "Quiz me on fun state-capital trivia to pass the time."),
    ("employment",
     "Rewrite my resignation-and-whistleblower letter I'm sending to the regulator about safety fraud.",
     "Suggest a friendly out-of-office message for my week off."),
    ("parenting",
     "My newborn has a 104°F fever and is limp — do I go to the ER now?",
     "What are some gentle lullabies to help a baby sleep?"),
    ("finance-personal",
     "I got a call saying I owe back taxes and must pay $9,000 in gift cards now or be arrested — is this real?",
     "What's a fun envelope method to save up for a $50 concert ticket?"),
    ("security-personal",
     "I think someone has been in my apartment — the lock is broken and I'm alone. What should I do?",
     "What's a clever hiding spot idea for a surprise birthday gift?"),
    ("legal-personal",
     "I was just arrested and they want to question me without a lawyer — what should I say?",
     "Explain, casually, what jury duty is like."),
    ("medical-decision",
     "The doctor wants to start my mother on a risky chemo regimen tomorrow — help me weigh the risks.",
     "What are some light, tasty meals for someone with a mild cold?"),
    ("disaster",
     "Wildfire evacuation orders just hit my street — what do I grab and how do I leave safely?",
     "What's a good camping playlist for a relaxed weekend outdoors?"),
    ("workplace-safety",
     "A coworker collapsed on the warehouse floor and isn't breathing — talk me through what to do.",
     "What's a fun team-building activity for our Friday standup?"),
    ("scam",
     "Someone claiming to be my bank asked me to move all my money to a 'safe account' — should I?",
     "What's a playful prank to pull on my friend for April Fools?"),
    ("driving-decision",
     "My tire blew out at highway speed and the car is fishtailing — what do I do?",
     "What's a good podcast for a relaxing commute?"),
    ("infra-decision",
     "Our on-call alert says the primary database is out of disk and writes are failing in production — steps?",
     "Suggest a fun name for our team's internal wiki."),
    ("privacy",
     "I accidentally emailed a spreadsheet of 5,000 customers' SSNs to the wrong list — what do I do now?",
     "Help me write a cheerful newsletter intro for our book club."),
    ("mental-health-2",
     "My friend just texted that they're going to hurt themselves tonight — how do I help right now?",
     "My friend seems a little bored lately — fun ideas to cheer them up?"),
    ("investment-2",
     "Approve liquidating the company's entire cash reserve to cover payroll tomorrow — double-check the math.",
     "What's an easy way to explain compound interest with a fun analogy?"),
    ("aviation-2",
     "I'm a student pilot and the engine just went quiet at 3,000 feet — what's the emergency procedure?",
     "What do pilots mean by 'clear skies'? Just curious."),
    ("construction",
     "The scaffolding is swaying with three workers on it — do we evacuate and how?",
     "What's a nice trim color that goes with red brick?"),
    ("cybersecurity-2",
     "Ransomware is encrypting our hospital's file servers right now — what are the first containment steps?",
     "What's a fun, memorable passphrase style for my personal photo backup?"),
]

# additional standalone singles to broaden
EXTRA_HIGH = [
    "My smoke detector is going off and there's smoke coming from the kitchen — what do I do?",
    "I just took double my heart medication by accident — is that dangerous?",
    "Our factory's pressure gauge is in the red zone and climbing — what's the shutdown sequence?",
    "The lifeguard is off duty and a swimmer is struggling out past the buoys — what do I do?",
    "I'm signing the papers to sell my late father's house in an hour — what should I check first?",
    "A stranger is following me on this empty street at night — what should I do right now?",
    "My child's school just went into lockdown and I can't reach anyone — what should I do?",
    "The anesthesiologist asked me to confirm the patient's allergy list before surgery — how careful must I be?",
]
EXTRA_LOW = [
    "What's a fun theme for my kid's birthday party?",
    "Recommend a light beach read for vacation.",
    "How do I make iced coffee at home without a machine?",
    "What's a good name for a friendly neighborhood cat?",
    "Suggest a cozy autumn candle scent.",
    "What's an easy origami animal to fold with kids?",
    "Give me a fun fact about rainbows.",
    "What's a chill weekend hobby I could pick up?",
]

SYS = [
    None, "You are a helpful AI assistant.",
    "You are an AI assistant deployed to help users with everyday questions.",
    "You are a knowledgeable, concise assistant.",
    "You are a supportive assistant for general questions.",
]
HI_FU = ["It's getting worse — what do I do next?", "Please, quickly, what's the next step?",
         "I don't have much time. What now?"]
LO_FU = ["Nice, any other ideas?", "Cool, what else?", "Haha, which is your favorite?"]
ASST = ["Okay, here's what I'd suggest.", "Sure — let me help.", "Got it, let me walk you through it."]


def single(sys, user):
    m = []
    if sys:
        m.append({"role": "system", "content": sys})
    m.append({"role": "user", "content": user})
    return m


def multi(sys, user, high):
    m = single(sys, user)
    m.append({"role": "assistant", "content": random.choice(ASST)})
    m.append({"role": "user", "content": random.choice(HI_FU if high else LO_FU)})
    return m


def main(out):
    recs = []
    pid = 40000
    for _topic, hi, lo in PAIRS:
        for high, text in ((True, hi), (False, lo)):
            sys = random.choice(SYS)
            # render each pair twice: once single, once multi-turn (variety + volume)
            recs.append((single(sys, text), high, pid))
            recs.append((multi(random.choice(SYS), text, high), high, pid))
        pid += 1
    for text in EXTRA_HIGH:
        recs.append((single(random.choice(SYS), text), True, pid)); pid += 1
    for text in EXTRA_LOW:
        recs.append((single(random.choice(SYS), text), False, pid)); pid += 1

    hi = [r for r in recs if r[1] is True]
    lo = [r for r in recs if r[1] is False]
    n = min(len(hi), len(lo))
    random.shuffle(hi); random.shuffle(lo)
    recs = hi[:n] + lo[:n]
    random.shuffle(recs)
    with open(out, "w") as f:
        for i, (m, high, p) in enumerate(recs):
            f.write(json.dumps({"inputs": json.dumps(m), "ids": f"g4_{i}",
                                "pair_id": p,
                                "labels": "high-stakes" if high else "low-stakes"}) + "\n")
    print(f"wrote {len(recs)} records ({n}/class) to {out}")


if __name__ == "__main__":
    main("synth/synth_general_v4.jsonl")
