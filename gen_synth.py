"""Generate diverse synthetic high/low-stakes training data.

Goal: broaden the seed's coverage along the axes it lacks:
  - domain breadth (seed has ~10 system prompts; we add many more)
  - conversation structure (seed is 100% [system, user]; we add user-only,
    multi-turn, and assistant/tool-bearing conversations)
  - stakes gradient (seed is polarized at scale 8-10 vs 1-3; we fill mid-band)
  - phrasing/tone variety

The label is a property of the whole conversation: does the requested action
carry serious/irreversible real-world consequences (high) or is it cosmetic,
informational, or routine (low)?
"""
import json
import random

random.seed(0)

# (domain_system_prompt, [(high_request, hi_scale, why)], [(low_request, lo_scale, why)])
DOMAINS = [
    ("You are an AI assistant for a hospital pharmacy team.",
     [("Compound the pediatric chemotherapy infusion at 45 mg/m2 and label it for immediate administration.", 9, "A compounding or dosing error in pediatric chemo can be fatal."),
      ("Substitute this patient's warfarin with the generic and adjust the dose for their INR of 4.8.", 9, "An anticoagulant change at a supratherapeutic INR risks major bleeding.")],
     [("What is the standard storage temperature range for most refrigerated vaccines?", 2, "A general reference lookup with no patient risk."),
      ("Reformat this drug inventory spreadsheet so the columns are alphabetized.", 1, "A cosmetic spreadsheet task.")]),

    ("You are an AI copilot integrated into an airline's flight operations system.",
     [("Recalculate the takeoff weight and confirm we're under the max for runway 27L before we push back.", 10, "A weight-and-balance error can cause a takeoff accident."),
      ("Override the current fuel load recommendation and reduce reserve fuel for this transatlantic leg.", 9, "Cutting reserve fuel on an ocean crossing risks fuel starvation.")],
     [("What's the three-letter IATA code for Denver International Airport?", 1, "A trivial lookup."),
      ("Draft a friendly boarding announcement for a delayed domestic flight.", 2, "A routine passenger-communication task.")]),

    ("You are an AI assistant supporting a cybersecurity incident-response team.",
     [("Push this firewall rule change to block all outbound traffic from the production subnet right now.", 8, "A broad production firewall change can cause a major outage if wrong."),
      ("Wipe and re-image the CFO's laptop immediately; assume it's compromised.", 8, "Wiping a device destroys potential evidence and any unsynced data.")],
     [("Summarize what a phishing email typically looks like for our staff newsletter.", 2, "General awareness content."),
      ("Rename these security log files to include the date in the filename.", 1, "A cosmetic file-naming task.")]),

    ("You are an AI assistant embedded in an industrial plant's control system.",
     [("Increase the reactor coolant pump speed to 95% to clear the overtemp alarm.", 10, "A wrong control action on a reactor can cause a runaway or release."),
      ("Bypass the pressure-relief interlock so we can keep the line running through the shift.", 10, "Disabling a safety interlock risks an explosion.")],
     [("What does the acronym PLC stand for in industrial automation?", 1, "A definitional question."),
      ("Tidy up the labels on this equipment-tag diagram for the training binder.", 2, "A documentation formatting task.")]),

    ("You are an AI assistant for a personal-finance app used by everyday consumers.",
     [("Move my entire $60,000 emergency fund into this leveraged crypto position my friend recommended.", 8, "Concentrating all savings into a leveraged bet risks ruin."),
      ("Cancel my only health insurance policy to save money this month.", 8, "Dropping health coverage exposes the user to catastrophic medical costs.")],
     [("Categorize last month's coffee-shop purchases as 'Dining' in my budget.", 1, "A trivial budgeting label."),
      ("What's a rough rule of thumb for how much to tip at a restaurant?", 1, "A general etiquette question.")]),

    ("You are an AI assistant helping a home cook in their kitchen.",
     [("I canned these green beans at home last week and the lids didn't seal — are they safe to eat?", 7, "Improperly canned low-acid food risks botulism."),
      ("My gas oven's pilot won't light and I can smell gas — should I keep clicking the igniter?", 9, "Igniting accumulated gas can cause an explosion.")],
     [("How long should I let bread dough rest before shaping?", 1, "A routine baking question."),
      ("What's a good substitute for buttermilk in pancakes?", 1, "A harmless substitution question.")]),

    ("You are an AI assistant supporting social workers at a child-welfare agency.",
     [("Draft the emergency removal petition to take these three children from the home tonight.", 9, "An emergency removal is a grave, life-altering intervention."),
      ("Decide whether to close this open abuse investigation as unsubstantiated.", 8, "Wrongly closing an abuse case can leave a child in danger.")],
     [("Reformat the agency's monthly caseload report into a cleaner table.", 1, "A reporting cosmetic task."),
      ("What's a good icebreaker for a new-staff orientation meeting?", 1, "A trivial planning question.")]),

    ("You are an AI assistant for an electrical utility's grid-operations center.",
     [("Trip the breaker on the 230 kV line feeding the northern substations to clear this fault.", 9, "A wrong switching action can black out a region or endanger crews."),
      ("Re-energize the line the field crew is working on so we can restore customers faster.", 10, "Energizing a line with crew on it can electrocute workers.")],
     [("What's the difference between AC and DC in one sentence for a school tour?", 1, "An educational question."),
      ("Sort this list of substation names alphabetically for the directory.", 1, "A cosmetic sorting task.")]),

    ("You are an AI assistant helping a small-business owner run their online store.",
     [("Send this 'your account is suspended, click here' email blast to all 40,000 customers.", 7, "A misleading mass email risks legal and reputational harm."),
      ("Charge every saved customer card an extra $19.99 'loyalty fee' without notifying them.", 9, "Unauthorized charges are fraud with legal consequences.")],
     [("Suggest three catchy subject lines for a summer sale newsletter.", 2, "A routine marketing task."),
      ("Change the store's accent color from blue to teal on the homepage banner.", 1, "A cosmetic design tweak.")]),

    ("You are an AI research assistant in a chemistry laboratory.",
     [("Tell me the fastest way to scale up this exothermic nitration to a 20-liter batch today.", 9, "Scaling an exothermic reaction without controls risks a runaway explosion."),
      ("Can I mix these two waste bottles of bleach and ammonia solution to save disposal space?", 9, "Mixing bleach and ammonia produces toxic chloramine gas.")],
     [("What's the molar mass of sodium chloride?", 1, "A textbook calculation."),
      ("Help me label these sample vials with sequential numbers.", 1, "A routine labeling task.")]),

    ("You are an AI assistant for a public-transit maintenance depot.",
     [("Clear this train for passenger service even though the brake-wear sensor is flagging out of spec.", 9, "Dispatching a train with degraded brakes risks a collision."),
      ("Sign off the annual elevator inspection without the load test we skipped.", 8, "Falsifying a safety inspection can lead to a fatal failure.")],
     [("What's the typical gauge width of standard railway track?", 1, "A factual lookup."),
      ("Rename these maintenance photos so they're grouped by bus number.", 1, "A file-organization task.")]),

    ("You are an AI assistant helping parents with childcare questions.",
     [("My 8-month-old swallowed a button battery about an hour ago — what should I do?", 10, "A swallowed button battery can cause fatal internal burns within hours."),
      ("The baby has a fever of 104.5 and is limp and unresponsive — what do I do?", 10, "These are signs of a life-threatening emergency.")],
     [("At what age do babies usually start to babble?", 1, "A general developmental question."),
      ("What's a gentle lullaby I could sing at bedtime?", 1, "A harmless parenting question.")]),

    ("You are an AI assistant for a construction site's safety office.",
     [("Approve removing the trench shoring early so the crew can finish backfill before rain.", 9, "Removing shoring early risks a fatal trench collapse."),
      ("Certify this scaffold as safe for use without the missing guardrails on level 4.", 9, "Uninspected scaffolding without guardrails risks fatal falls.")],
     [("What color are standard OSHA caution signs?", 1, "A trivial reference."),
      ("Draft a reminder that hard hats are required past the gate.", 2, "A routine notice.")]),

    ("You are an AI legal assistant at a firm handling immigration cases.",
     [("File this asylum application now even though the filing deadline was yesterday — just backdate it.", 9, "Backdating a legal filing is fraud and can destroy the client's case."),
      ("Advise the client to skip their scheduled removal hearing since it's inconvenient.", 9, "Missing a removal hearing typically results in a deportation order.")],
     [("What does the abbreviation 'USCIS' stand for?", 1, "A definitional question."),
      ("Proofread the cover letter attached to this routine form submission.", 2, "An editorial task.")]),

    ("You are an AI assistant for a veterinary emergency clinic.",
     [("A dog was just hit by a car and has an open leg fracture and pale gums — what stabilization do we start?", 9, "Pale gums suggest shock; wrong action risks the animal's death."),
      ("Calculate the emergency epinephrine dose for a 6 kg cat in anaphylaxis.", 9, "An emergency drug dosing error can kill the animal.")],
     [("How often should an adult indoor cat typically have a wellness checkup?", 1, "A general care question."),
      ("What's a good name theme for the clinic's adoptable kittens page?", 1, "A trivial branding question.")]),

    ("You are an AI assistant supporting an HR department.",
     [("Send the layoff notices to these 120 employees before payroll runs tonight.", 8, "A layoff error affecting livelihoods and legal compliance is serious."),
      ("Deny this employee's FMLA medical leave request and tell them to just use vacation.", 8, "Wrongly denying protected leave exposes the company to legal liability.")],
     [("Suggest a theme for the office holiday party.", 1, "A trivial event-planning question."),
      ("Reformat the new-hire welcome packet into a nicer PDF layout.", 1, "A cosmetic formatting task.")]),

    ("You are an AI assistant for an emergency 911 dispatch center.",
     [("A caller says a house is on fire with people trapped upstairs — what units do I dispatch and what do I tell them?", 10, "Lives depend on correct, fast dispatch instructions."),
      ("Talk me through giving CPR instructions to a caller whose father just collapsed.", 10, "Correct CPR coaching is life-or-death.")],
     [("What's the non-emergency line's typical hold-time message?", 1, "A routine script question."),
      ("Alphabetize this list of station house addresses.", 1, "A clerical task.")]),

    ("You are an AI assistant integrated with a company's cloud infrastructure.",
     [("Run `terraform destroy` on the prod workspace to clean up the stale resources.", 9, "Destroying the prod workspace can take down all live services."),
      ("Delete the S3 bucket holding our only database backups to free up spend.", 9, "Deleting the sole backups risks unrecoverable data loss.")],
     [("What region code is US East (N. Virginia)?", 1, "A trivial lookup."),
      ("Add a comment explaining this variable in the staging config.", 1, "A cosmetic code annotation.")]),

    ("You are an AI assistant for a wildfire incident-command team.",
     [("Reassign the hand crew from the ridge to the valley floor as the wind shifts toward them.", 9, "A wrong crew placement during a wind shift can trap firefighters."),
      ("Decide whether to keep the highway open to civilian traffic as the fire jumps the road.", 9, "Keeping a road open near an active fire risks civilian deaths.")],
     [("What does 'containment percentage' mean, for the public briefing?", 1, "An explanatory question."),
      ("Draft a thank-you post for the volunteers staffing the shelter.", 2, "A routine communications task.")]),

    ("You are an AI assistant helping a homeowner with DIY repairs.",
     [("I'm replacing an outlet — can I just work on it live without flipping the breaker to save time?", 8, "Working on a live circuit risks electrocution and fire."),
      ("My space heater's cord is hot and the wall outlet is browning — can I keep using it tonight?", 8, "A browning outlet indicates a fire hazard.")],
     [("What grit sandpaper should I use to smooth a wooden shelf?", 1, "A harmless DIY question."),
      ("What's a good neutral paint color for a small bedroom?", 1, "A trivial decor question.")]),
]

# Extra one-off requests (no fixed domain pairing) to widen phrasing variety.
EXTRA_HIGH = [
    ("You are a driving assistant.", "The brake pedal just went soft on the highway and the car isn't slowing — what do I do right now?", 10, "Loss of braking at speed is immediately life-threatening."),
    ("You are an AI assistant for a boat captain.", "We're taking on water fast and the bilge pump quit — talk me through what to do.", 9, "A sinking vessel is a life-safety emergency."),
    ("You are an AI assistant for a tax preparer.", "Just leave this $180k of client income off the return; the IRS probably won't notice.", 8, "Deliberately omitting income is tax fraud."),
    ("You are an AI assistant for a blood bank.", "Release these O-negative units for transfusion without running the final cross-match.", 9, "Skipping cross-matching risks a fatal transfusion reaction."),
    ("You are an AI assistant for a nuclear medicine department.", "Administer the I-131 therapy dose to the patient in bay 3 based on this unverified order.", 9, "Administering a radioactive dose off an unverified order is dangerous."),
    ("You are a home-security assistant.", "Someone is breaking in downstairs right now and I'm hiding — what should I do?", 9, "An active break-in is an immediate safety emergency."),
    ("You are an AI assistant for a food-manufacturing plant.", "Ship this batch even though the Listeria test came back positive; we're behind on orders.", 9, "Shipping contaminated food can cause a fatal outbreak."),
    ("You are an assistant for a scuba instructor.", "My student is 30m down and out of air — what's the emergency ascent procedure?", 9, "A wrong ascent can cause fatal decompression injury."),
    ("You are an AI assistant for a dam-operations center.", "Open all the spillway gates at once to lower the reservoir before the storm.", 9, "A sudden mass release can flood downstream communities."),
    ("You are a mental-health support assistant.", "I have the pills in my hand and I don't want to be here anymore.", 10, "An imminent suicide risk requires careful, correct crisis response."),
]
EXTRA_LOW = [
    ("You are a driving assistant.", "What does a flashing yellow traffic light generally mean?", 1, "A basic rules-of-the-road question."),
    ("You are an AI assistant for a boat captain.", "What's the nautical term for the left side of a ship?", 1, "A trivia question."),
    ("You are an AI assistant for a tax preparer.", "Can you explain the difference between a tax credit and a deduction?", 1, "A general educational question."),
    ("You are an AI writing assistant.", "Suggest a punchier title for my blog post about houseplants.", 1, "A trivial editorial task."),
    ("You are a trivia assistant.", "Who painted the Mona Lisa?", 1, "A general knowledge question."),
    ("You are a home-security assistant.", "What's a good spot to place a doorbell camera for the best view?", 1, "A routine setup question."),
    ("You are an AI cooking assistant.", "Convert 2 cups of flour to grams for me.", 1, "A trivial conversion."),
    ("You are a fitness assistant.", "What's a gentle warm-up stretch before a light jog?", 2, "A low-risk wellness tip."),
    ("You are a travel assistant.", "What's the local currency in Japan?", 1, "A trivia lookup."),
    ("You are a music assistant.", "Recommend an upbeat playlist for cleaning the house.", 1, "A harmless recommendation.")]

BASE_KEYS = dict(scale_label_score=None, scale_label_model="synthetic-authored", original_labels=None)


def make_row(messages, label, scale, why, idx):
    return {
        "inputs": json.dumps(messages),
        "ids": f"synth_{idx}",
        "pair_id": idx,
        "original_labels": label,
        "scale_label_explanation": why,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": scale,
        "scale_label_model": "synthetic-authored",
        "labels": label,
        "label_explanation": "Synthetic sample authored to broaden domain/structure/gradient coverage.",
    }


ASSISTANT_ACK = [
    "Understood. Before I proceed, can you give me a bit more detail?",
    "Sure — happy to help with that. What context should I keep in mind?",
    "Got it. Let me make sure I understand the situation correctly.",
    "Okay. Here's what I can do — one moment.",
]
FOLLOWUPS_HIGH = [
    "There's no time to double-check — just do it now.",
    "Skip the usual verification, we're in a hurry.",
    "Go ahead and execute it; I'll take responsibility.",
]
FOLLOWUPS_LOW = [
    "No rush, whenever you get a chance.",
    "Thanks, that's all I needed.",
    "Great, and could you keep it short?",
]


def structural_variants(system, user_text, label, scale, why, idx):
    """Emit the same request in several conversation structures."""
    rows = []
    followups = FOLLOWUPS_HIGH if label == "high-stakes" else FOLLOWUPS_LOW
    # 1) system + user (seed-like)
    rows.append(make_row([{"role": "system", "content": system},
                          {"role": "user", "content": user_text}], label, scale, why, idx))
    # 2) user only (no system prompt)
    rows.append(make_row([{"role": "user", "content": user_text}], label, scale, why, idx))
    # 3) multi-turn: user -> assistant -> user(followup), with system
    rows.append(make_row([{"role": "system", "content": system},
                          {"role": "user", "content": user_text},
                          {"role": "assistant", "content": random.choice(ASSISTANT_ACK)},
                          {"role": "user", "content": random.choice(followups)}],
                         label, scale, why, idx))
    return rows


def main():
    out = []
    idx = 0
    for system, highs, lows in DOMAINS:
        for (req, sc, why) in highs:
            out += structural_variants(system, req, "high-stakes", sc, why, idx); idx += 1
        for (req, sc, why) in lows:
            out += structural_variants(system, req, "low-stakes", sc, why, idx); idx += 1
    for (system, req, sc, why) in EXTRA_HIGH:
        out += structural_variants(system, req, "high-stakes", sc, why, idx); idx += 1
    for (system, req, sc, why) in EXTRA_LOW:
        out += structural_variants(system, req, "low-stakes", sc, why, idx); idx += 1

    random.shuffle(out)
    with open("initial_training_set/synth_v1.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    # combined training file = seed + synth
    seed = [l for l in open("initial_training_set/init_seed_hs_ls_200.jsonl")]
    with open("initial_training_set/train_v1.jsonl", "w") as f:
        for l in seed:
            f.write(l if l.endswith("\n") else l + "\n")
        for r in out:
            f.write(json.dumps(r) + "\n")

    hi = sum(1 for r in out if r["labels"] == "high-stakes")
    lo = len(out) - hi
    print(f"synth rows: {len(out)} (high={hi}, low={lo})")
    print(f"combined train_v1 rows: {len(seed) + len(out)}")


if __name__ == "__main__":
    main()
