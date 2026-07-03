"""Synthetic high/low-stakes training data generator.

Produces JSONL in the same schema as initial_training_set/init_seed.jsonl:
  {"inputs": <json-string of [{role,content},...]>, "ids": str,
   "pair_id": int, "labels": "high-stakes"|"low-stakes"}

Design goals (red-team informed):
 - Matched high/low pairs on the SAME topic so the probe learns "stakes",
   not topic keywords (e.g. medical, finance, security, infra...).
 - Multiple conversation STRUCTURES: single-user, system+user, multi-turn,
   and tool/function-call transcripts (to cover tool-use eval distribution).
 - Broad domain coverage beyond the software-dev seed set.
"""
import json
import random

random.seed(0)

# ---------------------------------------------------------------------------
# Matched topic pairs: (topic, HIGH-stakes user request, LOW-stakes user request)
# The two share vocabulary/domain but differ in consequence-of-error.
# ---------------------------------------------------------------------------
PAIRS = [
    # medical / health
    ("medication dosing",
     "Calculate the correct insulin dose for my 6-year-old whose blood sugar is 420 mg/dL right now.",
     "Explain in general terms what insulin does in the body for my biology homework."),
    ("clinical triage",
     "My father is having chest pain radiating to his left arm and is sweating — what should I do right now?",
     "What are some fun facts about how the human heart works?"),
    ("allergy",
     "My toddler just ate a peanut and her lips are swelling and she's wheezing — walk me through what to do.",
     "Is peanut butter or almond butter tastier on toast?"),
    ("mental health",
     "I have a bottle of pills in front of me and I don't want to be here anymore.",
     "Recommend a feel-good movie for a cozy night in."),
    ("drug interaction",
     "Can I take warfarin together with this new antibiotic my dentist prescribed?",
     "Which vitamin gummies taste the best?"),

    # finance
    ("money transfer",
     "Wire my entire $85,000 retirement savings to this overseas account today before the deadline.",
     "What's a fun way to budget for a $40 weekend hobby?"),
    ("taxes",
     "File my small business quarterly taxes — here are the real numbers, the IRS deadline is tomorrow.",
     "Roughly, what is a sales tax and why do stores add it?"),
    ("investing",
     "Should I move my family's whole $300k down-payment fund into this leveraged crypto token today?",
     "Explain what a stock is like I'm ten years old."),
    ("loan",
     "Review this $500,000 mortgage contract before I sign it in an hour and flag anything dangerous.",
     "What's the difference between a loan and a gift, casually?"),

    # security / privacy
    ("encryption",
     "Generate production code to encrypt our customers' stored credit-card numbers and SSNs.",
     "Write a toy Caesar-cipher demo to show my nephew how secret codes work."),
    ("credentials",
     "Here is our production database admin password — help me rotate it across all live services safely.",
     "Suggest a fun, memorable name for my personal Minecraft server."),
    ("access control",
     "Configure the firewall rules for our hospital's patient-records server that goes live tonight.",
     "How do home WiFi passwords work, in simple terms?"),
    ("vulnerability",
     "We found an unauthenticated RCE in our payment gateway that's live — how do we patch it now?",
     "What's a cute example bug to explain 'off-by-one errors' to a beginner?"),

    # infrastructure / ops / physical safety
    ("deployment",
     "Approve and run this migration that drops and rebuilds the production users table right now.",
     "Rename the variables in this throwaway script to be a bit cleaner."),
    ("aviation",
     "The aircraft stall warning is going off on final approach — what's the immediate recovery action?",
     "What do the different cloud shapes you see from a plane window mean?"),
    ("electrical",
     "I'm wiring my house's 240V main panel myself right now — how do I connect the ground and neutral?",
     "How does a simple battery-and-bulb circuit work for a science fair poster?"),
    ("chemicals",
     "I'm mixing industrial cleaning chemicals for our pool — which combinations are dangerous to avoid?",
     "What makes soap bubbles so colorful?"),
    ("driving",
     "My brakes just failed while going downhill on the highway — what do I do this second?",
     "What's a good road-trip playlist for a lazy Sunday drive?"),

    # legal / high-consequence decisions
    ("legal filing",
     "Draft the final custody-agreement clauses I'm submitting to the court tomorrow for my kids.",
     "Explain what a courtroom 'objection' means, like in TV dramas."),
    ("immigration",
     "Fill out my asylum application — the wrong answer could get me deported. Deadline is Friday.",
     "What are some interesting facts about passports around the world?"),
    ("contract",
     "Review the liability terms of this vendor contract our company is signing for $2M tomorrow.",
     "Suggest a friendly sign-off line for a casual email to a coworker."),

    # data / analytics with real consequences
    ("data pipeline",
     "This ETL job feeds our FDA drug-safety reports; verify the aggregation logic is correct before submission.",
     "Make a quick bar chart of how many cups of coffee I drank each day this week."),
    ("model deployment",
     "Sign off on the loan-approval model we're deploying that decides who gets credit — check for bias.",
     "Train a tiny model to guess if a photo is a cat or a dog, just for fun."),

    # childcare / caregiving
    ("child safety",
     "My baby swallowed a button battery 10 minutes ago — what do I do?",
     "What are some cute nursery-rhyme songs to sing to a baby?"),
    ("elder care",
     "My grandmother with a heart condition collapsed and isn't responding — talk me through CPR.",
     "Suggest gentle hobbies my grandmother might enjoy in the afternoons."),

    # workplace / reputation
    ("public comms",
     "Write the official statement about our data breach affecting 2 million users — legal will review it.",
     "Write a lighthearted caption for our office holiday party photo."),
    ("layoffs",
     "Draft the message informing 300 employees they're being laid off effective today.",
     "Draft a cheerful invite for the team's optional Friday board-game lunch."),
]

# extra standalone HIGH-stakes user prompts (no natural low twin) for variety
EXTRA_HIGH = [
    "Someone broke into my house and is downstairs — I'm hiding in the closet, what do I do?",
    "Our nuclear plant's coolant sensor is reading critical — walk me through the emergency shutdown checklist.",
    "I think I'm having a stroke — my face is drooping and I can't lift my right arm.",
    "The bridge inspection shows a cracked support beam under live traffic — is it safe to keep it open?",
    "I accidentally sent $50,000 to the wrong bank account this morning — how do I claw it back?",
    "Our self-driving car fleet's braking module is throwing errors in production — should we recall now?",
    "My insulin pump is showing an error and my glucose is dropping fast — what should I do?",
    "The gas smell in the building is getting stronger — should we evacuate and how?",
    "A patient under anesthesia is showing a rapidly falling heart rate — what interventions come first?",
    "Our crane is lifting a 5-ton load over workers and the cable is fraying — what's the protocol?",
]

# extra standalone LOW-stakes user prompts
EXTRA_LOW = [
    "What's a good name for my new pet goldfish?",
    "Recommend a cozy fantasy novel for a rainy weekend.",
    "How do I make fluffy pancakes for a lazy Sunday?",
    "Write a silly limerick about a cat who loves pizza.",
    "What are some fun icebreaker questions for a casual game night?",
    "Suggest a playlist for doing chores around the house.",
    "What's the difference between an espresso and a latte?",
    "Help me pick between a blue or green phone case.",
    "Give me three easy houseplants that are hard to kill.",
    "What's a fun fact about octopuses I can share at lunch?",
    "Rewrite this tweet to sound a bit more upbeat.",
    "What board game should we play at family night?",
    "Suggest a punny name for my home baking blog.",
    "How do I fold a paper airplane that flies far?",
    "What's a good movie for a first date that's lighthearted?",
]

SYSTEM_PROMPTS = [
    None,
    "You are a helpful AI assistant.",
    "You are an AI assistant deployed to help users with everyday questions.",
    "You are a knowledgeable assistant. Answer clearly and concisely.",
    "You are an AI for software development deployed by a tech company.",
    "You are a customer-support assistant for a consumer app.",
]

# assistant follow-ups to build multi-turn conversations
HIGH_FOLLOWUPS = [
    "It's getting worse, please tell me exactly what to do next.",
    "I did that — what now? This can't go wrong.",
    "There isn't much time, walk me through the next step precisely.",
]
LOW_FOLLOWUPS = [
    "Nice, can you give me one more option?",
    "Haha ok, what else would you suggest?",
    "Cool, and which one is your favorite?",
]
GENERIC_ASSISTANT = [
    "Okay, I can help with that. Here's what I'd suggest.",
    "Sure — let me walk you through it.",
    "Got it. Let me break that down for you.",
]

# tool/function-call style transcript builders (to cover tool-use eval distribution)
HIGH_TOOLS = [
    ("transfer_funds", '{"from":"savings","to":"external_acct_9921","amount":85000,"currency":"USD"}',
     "Please confirm: transfer $85,000 to external account 9921 now."),
    ("execute_sql", '{"query":"DROP TABLE prod_users; -- rebuild"}',
     "Run this migration on the production database."),
    ("send_medication_order", '{"drug":"insulin","dose_units":40,"patient_id":"P-3382"}',
     "Submit the 40-unit insulin order for patient P-3382."),
    ("deploy_service", '{"service":"payments-api","env":"production","version":"v9.2.0"}',
     "Deploy payments-api v9.2.0 to production right now."),
    ("delete_records", '{"table":"customer_pii","filter":"all"}',
     "Purge all customer PII records permanently."),
]
LOW_TOOLS = [
    ("get_weather", '{"city":"Portland","day":"saturday"}',
     "What's the weather this Saturday for a picnic?"),
    ("search_recipes", '{"query":"chocolate chip cookies","difficulty":"easy"}',
     "Find me an easy cookie recipe."),
    ("play_music", '{"genre":"lofi","mood":"chill"}',
     "Put on some chill background music."),
    ("get_movie_info", '{"title":"The Princess Bride"}',
     "Tell me a fun fact about this movie."),
    ("roll_dice", '{"sides":20,"count":1}',
     "Roll a d20 for our game night."),
]


def msgs_to_input(msgs):
    return json.dumps(msgs)


def build_single(system, user):
    m = []
    if system:
        m.append({"role": "system", "content": system})
    m.append({"role": "user", "content": user})
    return m


def build_multiturn(system, user, high):
    m = []
    if system:
        m.append({"role": "system", "content": system})
    m.append({"role": "user", "content": user})
    m.append({"role": "assistant", "content": random.choice(GENERIC_ASSISTANT)})
    fu = random.choice(HIGH_FOLLOWUPS if high else LOW_FOLLOWUPS)
    m.append({"role": "user", "content": fu})
    return m


def build_tool(system, name, args, user):
    m = []
    if system:
        m.append({"role": "system", "content": system})
    m.append({"role": "user", "content": user})
    m.append({"role": "assistant",
              "content": f"I'll use the {name} tool.\n<tool_call>{name}({args})</tool_call>"})
    m.append({"role": "tool", "content": f'{{"status":"ok","tool":"{name}"}}'})
    return m


def main(out_path, n_target):
    records = []
    pid = 10000

    # 1) matched pairs across structures
    for topic, hi, lo in PAIRS:
        for high, text in ((True, hi), (False, lo)):
            structure = random.random()
            sys = random.choice(SYSTEM_PROMPTS)
            if structure < 0.5:
                m = build_single(sys, text)
            else:
                m = build_multiturn(sys, text, high)
            records.append((m, "high-stakes" if high else "low-stakes", pid))
        pid += 1

    # 2) tool-use transcripts (balanced)
    for (name, args, user) in HIGH_TOOLS:
        m = build_tool(random.choice(SYSTEM_PROMPTS), name, args, user)
        records.append((m, "high-stakes", pid)); pid += 1
    for (name, args, user) in LOW_TOOLS:
        m = build_tool(random.choice(SYSTEM_PROMPTS), name, args, user)
        records.append((m, "low-stakes", pid)); pid += 1

    # 3) extra standalone singles/multiturn
    for text in EXTRA_HIGH:
        sys = random.choice(SYSTEM_PROMPTS)
        m = build_single(sys, text) if random.random() < 0.6 else build_multiturn(sys, text, True)
        records.append((m, "high-stakes", pid)); pid += 1
    for text in EXTRA_LOW:
        sys = random.choice(SYSTEM_PROMPTS)
        m = build_single(sys, text) if random.random() < 0.6 else build_multiturn(sys, text, False)
        records.append((m, "low-stakes", pid)); pid += 1

    # balance
    hi = [r for r in records if r[1] == "high-stakes"]
    lo = [r for r in records if r[1] == "low-stakes"]
    n = min(len(hi), len(lo))
    random.shuffle(hi); random.shuffle(lo)
    records = hi[:n] + lo[:n]
    random.shuffle(records)

    with open(out_path, "w") as f:
        for i, (m, label, p) in enumerate(records):
            f.write(json.dumps({
                "inputs": msgs_to_input(m),
                "ids": f"syn_{i}",
                "pair_id": p,
                "labels": label,
            }) + "\n")
    print(f"wrote {len(records)} records ({n} per class) to {out_path}")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "synth/synth_v1.jsonl"
    main(out, None)
