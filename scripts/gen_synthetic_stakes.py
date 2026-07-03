"""
Generate synthetic high-stakes / low-stakes training data for the probe.

Design principles (why this should help mean AUROC without contaminating eval):
  * The signal we want the probe to learn is STAKES, not TOPIC. So every domain
    below appears in BOTH classes (e.g. a medical emergency vs. a trivial health
    question). This discourages the probe from latching onto topic words.
  * Coverage is deliberately broad, including tool-use / agentic transcripts,
    because the `toolace` eval axis is the current weakest (AUROC 0.737).
  * These conversations are authored from scratch from the *concept* of stakes.
    Nothing here is copied from, sampled from, or tuned against eval_datasets/
    or the existing initial_training_set contents.

Output schema (matches tuberlens LabelledDataset.from_pandas):
  one JSON object per line: {"inputs": [{"role","content"}...], "labels": "<label>"}
"""
import argparse
import json
import random

HIGH = "high-stakes"
LOW = "low-stakes"

# ----------------------------------------------------------------------------
# Base scenarios. Each entry is a full user/assistant (and sometimes tool/system)
# dialogue. Domains are shared across classes on purpose.
# ----------------------------------------------------------------------------

HIGH_SCENARIOS = [
    # --- Medical emergencies / serious health decisions ---
    [("user", "I've had crushing chest pain radiating down my left arm for 20 minutes and I'm sweating and nauseous. What should I do?"),
     ("assistant", "This can be a heart attack. Call emergency services (911) right now and chew an aspirin if you're not allergic. Do not drive yourself.")],
    [("user", "My 3-month-old has a fever of 104F and is limp and not responding normally."),
     ("assistant", "A limp, unresponsive infant with a fever that high is a medical emergency. Call emergency services or go to the ER immediately.")],
    [("user", "I think I took too many of my blood pressure pills by accident, maybe double. My heart is racing and I feel faint."),
     ("assistant", "Please contact poison control and emergency services now. An overdose of blood pressure medication can be dangerous; get help immediately rather than waiting.")],
    [("user", "My father collapsed and isn't breathing. What do I do?"),
     ("assistant", "Call 911 immediately and begin CPR: push hard and fast in the center of the chest, about 100-120 compressions per minute. Put me on speaker if you need me to count with you.")],
    [("user", "The doctor says I need to decide today whether to start chemotherapy or a clinical trial for my stage 3 cancer. Which is safer?"),
     ("assistant", "This is a serious decision that will affect your life expectancy and quality of life. I can help you think through questions to ask your oncologist, but please make the final call with your medical team given the stakes.")],

    # --- Finance: large, irreversible money decisions ---
    [("user", "Should I withdraw my entire $180k retirement account to put it all into one crypto coin a friend recommended?"),
     ("assistant", "Liquidating your whole retirement into a single speculative coin risks catastrophic, irreversible loss and large tax penalties. This is an extremely high-stakes move; please talk to a fiduciary advisor before doing anything.")],
    [("user", "I'm about to wire my life savings, $95,000, to a seller for a house I found online but haven't visited. They want it in the next hour."),
     ("assistant", "High-pressure, wire-now demands for a property you haven't verified are a classic fraud pattern. Do not send the money yet; verify the title, the escrow company, and the seller independently first.")],
    [("user", "I want to co-sign a $60,000 loan for my brother-in-law's business tomorrow. What should I know?"),
     ("assistant", "Co-signing makes you fully liable if he defaults, which could ruin your credit and finances. Given the amount, treat this as a high-stakes commitment and get the terms reviewed before signing.")],
    [("user", "My company wants me to sign off on the quarterly financials today but I found a $2M discrepancy I can't explain."),
     ("assistant", "Signing off on financials you believe are materially misstated can carry serious legal and professional consequences. Do not certify them until the discrepancy is resolved; escalate it in writing.")],

    # --- Legal ---
    [("user", "The police want to question me about a felony without a lawyer present and I'm scared. Should I just answer?"),
     ("assistant", "This is a high-stakes legal situation. You have the right to remain silent and to an attorney; it's generally wise to say you want a lawyer before answering questions.")],
    [("user", "I have to sign a settlement agreement waiving all future claims from my accident by end of day. The number seems low."),
     ("assistant", "Signing a full release is irreversible and could bar you from future compensation for injuries that worsen. Given the stakes, have an attorney review it before you sign, even if it means asking for more time.")],
    [("user", "I'm representing myself in a custody hearing tomorrow. What's the one thing I must not mess up?"),
     ("assistant", "Custody outcomes are hard to undo and deeply affect your children, so this is high-stakes. Focus on demonstrating the child's best interests calmly; if at all possible, get even brief legal advice tonight.")],

    # --- Safety / hazardous physical situations ---
    [("user", "I smell gas strongly in my kitchen and feel dizzy. Should I check the stove?"),
     ("assistant", "Do not flip switches or light anything. Leave the house immediately, then call your gas company or emergency services from outside. A gas leak is life-threatening.")],
    [("user", "There's a downed power line lying across my driveway and it's sparking. My kid's bus drops off there in 10 minutes."),
     ("assistant", "Stay far back and keep everyone away; a live line can be lethal. Call 911 and the utility now, and warn the bus so children don't approach.")],
    [("user", "I'm rewiring my home's main electrical panel myself and I'm not sure if the power is actually off."),
     ("assistant", "Working a live main panel can be fatal. If you can't confirm it's de-energized with a proper tester, stop and get a licensed electrician; the risk here is too high to guess.")],
    [("user", "We're hiking and my friend was just bitten by a snake with a diamond pattern. His leg is swelling fast."),
     ("assistant", "Treat this as an emergency: keep him still, keep the bite below heart level, remove tight items, and get to emergency care or call for rescue immediately. Do not cut or suck the wound.")],

    # --- Mental health / crisis ---
    [("user", "I don't think I can keep going. I've been thinking about ending my life tonight."),
     ("assistant", "I'm really glad you told me, and I'm concerned for your safety. You deserve support right now. If you're in the US you can call or text 988 to reach the Suicide and Crisis Lifeline; if you're elsewhere I can help find a local line. Are you safe at this moment?")],
    [("user", "My teenager just texted me a goodbye message and won't answer their phone."),
     ("assistant", "This is an emergency. Try to reach them or someone physically near them immediately, and if you can't confirm they're safe, call 911 for a welfare check. Contact a crisis line for guidance while you do.")],

    # --- Agentic / tool-use, destructive or high-impact operations ---
    [("system", "You are an autonomous ops agent with shell and database access to the production environment."),
     ("user", "Clean up the users table, it's gotten messy."),
     ("assistant", "To confirm scope before I act, I'll inspect the table first."),
     ("tool", "run_sql('SELECT count(*) FROM users') -> 4,200,318 rows"),
     ("assistant", "The users table has 4.2M live production rows. 'Clean up' is ambiguous and could destroy real customer data, so I won't run any DELETE/DROP until you specify exact criteria and confirm a backup exists.")],
    [("system", "You are a deployment agent able to push to production."),
     ("user", "Ship the current branch straight to prod, skip the tests, we're in a hurry."),
     ("assistant", "Deploying untested code directly to production risks an outage for all users. Given the impact, I'd strongly recommend at least running the smoke suite; do you want me to proceed despite that risk?")],
    [("system", "You are an infrastructure agent with cloud admin credentials."),
     ("user", "Rotate the master credentials and delete the old key now."),
     ("assistant", "run_cmd('list-services-using-key MASTER') -> 37 running services reference this key"),
     ("assistant", "37 production services still authenticate with the master key. Deleting it immediately would break all of them. I'll stage the new key, migrate services, and only revoke the old one once nothing depends on it.")],
    [("system", "You are a finance automation agent authorized to submit payments."),
     ("user", "Send the vendor payment of $840,000 to the account in this email."),
     ("assistant", "verify_account('acct in email') -> account changed 2 hours ago, no prior payment history"),
     ("assistant", "The destination account was changed two hours ago and has never received a payment from us, a common fraud signal for a transfer this large. I've paused the payment pending out-of-band verification with the vendor.")],
    [("system", "You are a data engineering agent with write access to the analytics warehouse."),
     ("user", "Drop the old_events table, we don't need it."),
     ("assistant", "run_sql('SELECT max(ts), count(*) FROM old_events') -> latest row is from yesterday, 1.1B rows"),
     ("assistant", "old_events is still being written to as of yesterday and holds 1.1B rows, so dropping it is likely destructive and irreversible. Can you confirm it's truly deprecated and that we have a backup before I drop it?")],
    [("system", "You are an email agent that can send on the user's behalf."),
     ("user", "Reply-all to the whole company announcing the layoffs I pasted below."),
     ("assistant", "This message would notify the entire company about layoffs, an irreversible and highly sensitive communication. Before I send to all-staff, can you confirm HR and leadership have approved this exact wording and timing?")],

    # --- Aviation / driving / transport ---
    [("user", "My car's brakes just went soft and barely respond, I'm doing 60 on the highway."),
     ("assistant", "Downshift to slow the engine, pump the brakes, gently apply the parking brake, and steer to the shoulder. This is an emergency; put your hazards on and call for help once stopped.")],
    [("user", "The pilot is incapacitated and I'm the only one in the cockpit of a small plane. What do I do?"),
     ("assistant", "Immediately declare an emergency on the radio (say 'Mayday' on the current frequency or 121.5) so air traffic control can talk you through it. Keep the wings level and don't touch anything abruptly while help is coming on the radio.")],

    # --- Childcare / poisoning ---
    [("user", "My toddler just swallowed a button battery. He seems okay right now."),
     ("assistant", "A swallowed button battery can cause severe internal burns within hours even if he looks fine. Go to the ER now and call poison control on the way; do not wait for symptoms.")],
    [("user", "The daycare gave my child another kid's medication by mistake. What now?"),
     ("assistant", "Find out exactly what drug and dose was given and call poison control immediately with that information; they'll tell you if it's an emergency. This needs prompt attention, not waiting.")],
]

LOW_SCENARIOS = [
    # --- Medical: trivial / informational ---
    [("user", "What foods are high in vitamin C?"),
     ("assistant", "Citrus fruits, bell peppers, strawberries, kiwi, broccoli, and tomatoes are all good sources of vitamin C.")],
    [("user", "Is it normal for my muscles to feel sore two days after a workout?"),
     ("assistant", "Yes, that's delayed onset muscle soreness (DOMS) and is completely normal after new or intense exercise. Gentle movement and hydration help.")],
    [("user", "How much water should I drink in a day, roughly?"),
     ("assistant", "A common rule of thumb is around 2 liters (about 8 cups), but it varies with your size, activity, and climate. Thirst and pale-yellow urine are decent everyday guides.")],
    [("user", "What's a good multivitamin brand for general health?"),
     ("assistant", "Any reputable brand that's third-party tested is usually fine for general use. If you eat a varied diet you may not need one at all.")],
    [("user", "My throat is a little scratchy today. Any home remedies?"),
     ("assistant", "Warm tea with honey, salt-water gargles, and staying hydrated can soothe a mild scratchy throat. Rest helps too.")],

    # --- Finance: trivial / everyday ---
    [("user", "How do I split a $86 dinner bill evenly between 4 people including a 20% tip?"),
     ("assistant", "The total with 20% tip is $103.20, so each person pays about $25.80.")],
    [("user", "Is it worth using a coupon app to save a couple dollars on groceries?"),
     ("assistant", "If it's low effort, sure, small savings add up over time. Just don't let it push you to buy things you wouldn't otherwise.")],
    [("user", "What's the difference between a debit card and a credit card, simply?"),
     ("assistant", "A debit card spends money you already have in your account; a credit card borrows money you pay back later, often with interest if you carry a balance.")],
    [("user", "Should I round up my savings transfers to the nearest $5 to save a little more?"),
     ("assistant", "That's a harmless, nice little habit, automatic round-ups can quietly build a small cushion over time.")],

    # --- Legal: trivial / informational ---
    [("user", "Do I legally need to write my name in cursive on a form or is print okay?"),
     ("assistant", "In most everyday cases a signature can be printed or stylized; there's usually no legal requirement that it be cursive.")],
    [("user", "What's the difference between a law and a regulation, in plain terms?"),
     ("assistant", "A law is passed by a legislature; a regulation is a more detailed rule made by an agency to implement a law. Both are enforceable.")],
    [("user", "Can I use a nickname on a casual club membership form?"),
     ("assistant", "For an informal club membership a nickname is generally fine; it only matters when a form requires your legal name.")],

    # --- Safety: trivial / everyday ---
    [("user", "What's a safe way to reach a mug on a high shelf?"),
     ("assistant", "Use a small step stool with a wide base rather than a chair, and keep three points of contact. Or just grab something to gently nudge it forward.")],
    [("user", "How often should I replace my smoke detector batteries as routine maintenance?"),
     ("assistant", "A common habit is once a year, and many people tie it to a date like a clock change so it's easy to remember.")],
    [("user", "Is it okay to leave a phone charger plugged in when nothing's connected?"),
     ("assistant", "A modern charger left plugged in with nothing attached draws a tiny amount of power and is generally fine, though unplugging saves a little.")],
    [("user", "What household plant is hard to kill for a beginner?"),
     ("assistant", "Snake plants, pothos, and ZZ plants are famously low-maintenance and tolerate irregular watering well.")],

    # --- Casual chit-chat / hobbies ---
    [("user", "Tell me a fun fact about octopuses."),
     ("assistant", "Octopuses have three hearts and blue, copper-based blood. Two hearts pump to the gills and one to the rest of the body.")],
    [("user", "What's a good movie for a relaxed Friday night?"),
     ("assistant", "If you want something easy and feel-good, comedies or animated films tend to fit a relaxed night. Any genre you're in the mood for?")],

    # --- Agentic / tool-use, low-impact operations ---
    [("system", "You are a helpful assistant with tools for formatting and simple lookups."),
     ("user", "Turn this list of three fruits into a markdown table for me."),
     ("assistant", "format_table(['apple','banana','cherry']) -> rendered a 1-column table"),
     ("assistant", "Here's your markdown table:\n\n| Fruit |\n|-------|\n| apple |\n| banana |\n| cherry |")],
    [("system", "You are an assistant with a read-only weather tool."),
     ("user", "What's the weather looking like for my picnic Saturday?"),
     ("assistant", "get_weather('Saturday') -> sunny, 74F, light breeze"),
     ("assistant", "Saturday looks great for a picnic: sunny, about 74F with a light breeze.")],
    [("system", "You are a coding helper with a scratch sandbox."),
     ("user", "Rename the variable `x` to `count` in this snippet I'm pasting."),
     ("assistant", "Sure, here's the snippet with `x` renamed to `count`. It's a cosmetic change and behaves identically.")],
    [("system", "You are an assistant with a calendar tool."),
     ("user", "Add a reminder to water my plants on Sunday morning."),
     ("assistant", "add_reminder('water plants', 'Sunday 9am') -> created"),
     ("assistant", "Done, I've set a reminder to water your plants Sunday at 9am.")],
    [("system", "You are an assistant that can search a recipe database."),
     ("user", "Find me an easy pasta recipe for tonight."),
     ("assistant", "search_recipes('easy pasta') -> aglio e olio (15 min)"),
     ("assistant", "Aglio e olio is a great quick option, spaghetti, garlic, olive oil, chili flakes, and parsley, ready in about 15 minutes.")],
    [("system", "You are an assistant with a units-conversion tool."),
     ("user", "How many cups is 250 grams of flour?"),
     ("assistant", "convert('250g flour','cups') -> about 2 cups"),
     ("assistant", "Roughly 2 cups of all-purpose flour, though it varies a little with how it's packed.")],

    # --- Transport: trivial ---
    [("user", "What tire pressure is typical for a normal sedan, just curious?"),
     ("assistant", "Most sedans run around 32-35 psi; the exact number is on a sticker inside the driver's door jamb.")],
    [("user", "Is premium gas necessary if my car only calls for regular?"),
     ("assistant", "If the manufacturer specifies regular, premium generally offers no benefit, so you can save the money.")],

    # --- Childcare: trivial ---
    [("user", "What's a fun rainy-day activity for a 4-year-old?"),
     ("assistant", "Building a pillow fort, finger painting, or a simple indoor scavenger hunt are all crowd-pleasers for that age.")],
    [("user", "How do I get my toddler to eat more vegetables without a fight?"),
     ("assistant", "Offering small portions, letting them dip veggies in something they like, and involving them in prep tend to help. Keep it low-pressure.")],

    # --- Cooking / education trivia ---
    [("user", "What temperature do I bake chocolate chip cookies at?"),
     ("assistant", "350F (175C) for about 10-12 minutes is a reliable default for classic chocolate chip cookies.")],
    [("user", "Who painted the Mona Lisa?"),
     ("assistant", "Leonardo da Vinci painted the Mona Lisa in the early 1500s.")],
]

# Wrappers to add lexical / structural variety without changing the stakes.
SYSTEM_PREFIXES = [
    None, None, None,  # often no system prompt
    "You are a helpful, honest assistant.",
    "You are a concise assistant. Answer directly.",
    "You are an assistant. Be careful and accurate.",
]

HIGH_FOLLOWUPS = [
    ("user", "Please, quickly, what's the very first step?"),
    ("user", "Okay I'm panicking a bit, tell me what matters most."),
    ("user", "This feels serious. Am I overreacting?"),
]
LOW_FOLLOWUPS = [
    ("user", "Cool, thanks. Anything else worth knowing?"),
    ("user", "Nice, that's helpful."),
    ("user", "Got it, no rush at all."),
]
HIGH_FOLLOWUP_REPLIES = [
    ("assistant", "The single most important thing is to get to safety and get help now; everything else can wait."),
    ("assistant", "You're not overreacting, this warrants prompt action. Prioritize safety first."),
]
LOW_FOLLOWUP_REPLIES = [
    ("assistant", "That's about it, it's a pretty low-stakes thing, so no worries either way."),
    ("assistant", "Nope, you're all set. Enjoy!"),
]


def to_messages(pairs):
    return [{"role": r, "content": c} for r, c in pairs]


def augment(base, label, rng):
    """Return a possibly-varied copy of a base dialogue as a messages list."""
    pairs = list(base)
    # Optionally prepend a system message (only if not already present).
    if pairs[0][0] != "system":
        sysp = rng.choice(SYSTEM_PREFIXES)
        if sysp is not None:
            pairs = [("system", sysp)] + pairs
    # Optionally append a short follow-up turn.
    if rng.random() < 0.45:
        if label == HIGH:
            pairs = pairs + [rng.choice(HIGH_FOLLOWUPS), rng.choice(HIGH_FOLLOWUP_REPLIES)]
        else:
            pairs = pairs + [rng.choice(LOW_FOLLOWUPS), rng.choice(LOW_FOLLOWUP_REPLIES)]
    return to_messages(pairs)


def build(n_per_class, seed):
    rng = random.Random(seed)
    rows = []
    for label, scenarios in ((HIGH, HIGH_SCENARIOS), (LOW, LOW_SCENARIOS)):
        made = 0
        # Cycle through base scenarios, augmenting, until we hit the target count.
        order = list(range(len(scenarios)))
        while made < n_per_class:
            rng.shuffle(order)
            for i in order:
                if made >= n_per_class:
                    break
                msgs = augment(scenarios[i], label, rng)
                rows.append({"inputs": msgs, "labels": label})
                made += 1
    rng.shuffle(rows)
    # Assign stable ids
    for j, r in enumerate(rows):
        r["ids"] = f"syn-{j}"
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_per_class", type=int, default=250)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="initial_training_set/synthetic_stakes.jsonl")
    args = ap.parse_args()

    rows = build(args.n_per_class, args.seed)
    with open(args.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n_high = sum(1 for r in rows if r["labels"] == HIGH)
    print(f"Wrote {len(rows)} rows to {args.out} ({n_high} high / {len(rows)-n_high} low)")
    print(f"Distinct high base scenarios: {len(HIGH_SCENARIOS)}, low base: {len(LOW_SCENARIOS)}")


if __name__ == "__main__":
    main()
