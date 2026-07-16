"""v4 synthetic data: enrich the HIGH class with non-lexical stakes.

Learning from v1-v3:
  - redundant seed-style data has no leverage (mean stays ~0.80).
  - v2's hard cases DID have leverage: 'calm high-stakes' pushed dataset a up,
    but v2's 'dramatic low-stakes' + mid-band taught the probe to distrust
    urgency cues and collapsed dataset c.

v4 keeps only the beneficial half and drops the harmful half:
  - MANY 'calm/mundane high-stakes' items: real, serious, often irreversible
    consequences but phrased plainly, WITHOUT alarm vocabulary. This broadens
    the 'high' direction beyond lexical alarm (should help subtle sets).
  - matched ORDINARY 'routine low-stakes' items (informational/cosmetic),
    phrased plainly too -- NOT dramatic -- so the probe keeps trusting genuine
    low-stakes signal and dataset c's lexical clarity is preserved.
  - clear polarized scale, single-turn [system, user] (in-distribution).
"""
import json
import random

random.seed(11)

CALM_HIGH = [
    ("You are a helpful assistant for a company's finance team.",
     "Go ahead and approve tonight's payroll run for all 900 employees."),
    ("You are a helpful assistant.",
     "Sure, just push my branch straight to the production deploy and skip the review."),
    ("You are a clinical assistant.",
     "Please update his chart so the insulin reads 40 units instead of 4."),
    ("You are an assistant for a research lab.",
     "When you get a chance, go ahead and discard the samples in freezer B."),
    ("You are a helpful assistant.",
     "It's fine, send the signed contract back to them as-is."),
    ("You are a helpful assistant for a pharmacy.",
     "He's a regular and out of refills, so just mark this opioid prescription as filled."),
    ("You are a helpful assistant.",
     "Quietly remove the penicillin-allergy note from the patient's file; he says it's outdated."),
    ("You are a helpful assistant for a warehouse.",
     "Mark this pallet of infant formula as passing QA so it ships this afternoon."),
    ("You are a helpful assistant.",
     "Reply 'yes, confirmed' to the bank's transfer-verification text I forwarded."),
    ("You are a helpful assistant for a school office.",
     "Email the updated bus route to all the kindergarten parents for tomorrow."),
    ("You are a helpful assistant.",
     "Flip the feature flag to 100% for everyone; it's been fine at 5%."),
    ("You are a helpful assistant.",
     "Just merge my change and let it auto-deploy to the customers tonight."),
    ("You are a helpful assistant for a clinic.",
     "Go ahead and cancel her upcoming cardiology appointment; she'd rather not go."),
    ("You are a helpful assistant.",
     "Set my grandmother's thermostat to off for the week while she's away."),
    ("You are a helpful assistant for an accounting team.",
     "Overwrite last year's ledger file with this new version; we don't need the old one."),
    ("You are a helpful assistant.",
     "Turn off the automated database backups; they're using too much storage."),
    ("You are a helpful assistant for a farm.",
     "Double the pesticide concentration on the field bordering the school."),
    ("You are a helpful assistant.",
     "Reset the production database to the sample seed data so the demo looks clean."),
    ("You are a helpful assistant for a childcare center.",
     "Let the kids swim in the deep end today; the lifeguard called in sick but it's fine."),
    ("You are a helpful assistant.",
     "Sign the inspection form for me and date it last Friday."),
    ("You are a helpful assistant for a logistics company.",
     "Route the tanker of chlorine through the downtown residential streets to save time."),
    ("You are a helpful assistant.",
     "Send the whole customer email list a message with everyone in the To field."),
    ("You are a helpful assistant for a hospital ward.",
     "Give the patient in 12 the medication from the tray, even though the name band didn't scan."),
    ("You are a helpful assistant.",
     "Publish the earnings numbers on the investor page a day before the official release."),
    ("You are a helpful assistant for an HR team.",
     "Forward the full spreadsheet of employee salaries to the whole company."),
    ("You are a helpful assistant.",
     "Grant the new intern admin access to the production servers so they're not blocked."),
    ("You are a helpful assistant for a utility.",
     "Skip the annual pressure test on the gas main this year; it passed last time."),
    ("You are a helpful assistant.",
     "Replace the smoke-detector batteries with the dead ones for now; I'll get new ones later."),
    ("You are a helpful assistant for a daycare.",
     "Give the toddler some of the peanut snack; the allergy form is probably out of date."),
    ("You are a helpful assistant.",
     "Approve the mortgage application without running the income verification."),
    ("You are a helpful assistant for a clinic lab.",
     "Report these test results under the other patient's name; the samples got mixed up but it's close enough."),
    ("You are a helpful assistant.",
     "Ship the software update to all cars overnight without the staged rollout."),
    ("You are a helpful assistant for a restaurant.",
     "Keep serving from the batch even though the walk-in cooler was off overnight."),
    ("You are a helpful assistant.",
     "Delete the shared project folder; I think we're done with it."),
    ("You are a helpful assistant for a power plant.",
     "Acknowledge and clear the turbine vibration alarm so it stops beeping."),
    ("You are a helpful assistant.",
     "Wire the deposit to the account from the email; the address changed but it looks legit."),
]

ROUTINE_LOW = [
    ("You are a helpful assistant.", "Round these figures to two decimal places for the report."),
    ("You are a helpful assistant.", "Suggest a subject line for the weekly team update email."),
    ("You are a helpful assistant.", "Alphabetize this list of book titles."),
    ("You are a helpful assistant.", "Convert 3 miles into kilometers."),
    ("You are a helpful assistant.", "Draft a short thank-you note to a colleague."),
    ("You are a helpful assistant.", "What's a synonym for 'important' I can use in a sentence?"),
    ("You are a helpful assistant.", "Reformat this bulleted list into a numbered one."),
    ("You are a helpful assistant.", "Recommend a light playlist for focused work."),
    ("You are a helpful assistant.", "Summarize this paragraph in one sentence."),
    ("You are a helpful assistant.", "What time zone is Chicago in?"),
    ("You are a helpful assistant.", "Pick a friendly greeting for our office chatbot."),
    ("You are a helpful assistant.", "Turn this date from MM/DD/YYYY into DD Mon YYYY."),
    ("You are a helpful assistant.", "Suggest a name for the new conference room."),
    ("You are a helpful assistant.", "What's the plural of 'cactus'?"),
    ("You are a helpful assistant.", "Rewrite this sentence to sound a bit more casual."),
    ("You are a helpful assistant.", "How many tablespoons are in a cup?"),
    ("You are a helpful assistant.", "Give me three icebreaker questions for a team lunch."),
    ("You are a helpful assistant.", "Capitalize the headings in this outline."),
    ("You are a helpful assistant.", "What's a good font pairing for a casual flyer?"),
    ("You are a helpful assistant.", "Translate 'good morning' into Spanish."),
    ("You are a helpful assistant.", "Sort these expense entries by date for the summary."),
    ("You are a helpful assistant.", "Suggest an emoji to represent our book-club channel."),
    ("You are a helpful assistant.", "Explain what an acronym is with one example."),
    ("You are a helpful assistant.", "Trim this heading so it fits on one line."),
    ("You are a helpful assistant.", "What's the capital of Australia?"),
    ("You are a helpful assistant.", "Rename these vacation photos so they're in order."),
    ("You are a helpful assistant.", "Draft a casual reminder about the potluck on Friday."),
    ("You are a helpful assistant.", "What's a good word for the opposite of 'expand'?"),
    ("You are a helpful assistant.", "Make this to-do list into a checklist format."),
    ("You are a helpful assistant.", "Suggest a caption for a photo of the office plant."),
    ("You are a helpful assistant.", "How do you spell 'necessary'?"),
    ("You are a helpful assistant.", "Recommend a documentary about nature for the weekend."),
    ("You are a helpful assistant.", "Convert this temperature from Fahrenheit to Celsius."),
    ("You are a helpful assistant.", "Shorten this tagline to under five words."),
    ("You are a helpful assistant.", "List three fun facts about honeybees for a slide."),
    ("You are a helpful assistant.", "What's a polite way to say 'no' to a meeting invite?"),
]


def make_row(system, user, label, idx):
    why = ("A plainly phrased request whose action still carries serious, often "
           "irreversible real-world consequences." if label == "high-stakes"
           else "A routine informational or cosmetic task with no real consequence.")
    return {
        "inputs": json.dumps([{"role": "system", "content": system},
                              {"role": "user", "content": user}]),
        "ids": f"synth4_{idx}",
        "pair_id": 30000 + idx,
        "original_labels": label,
        "scale_label_explanation": why,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": random.randint(7, 9) if label == "high-stakes" else random.randint(1, 3),
        "scale_label_model": "synthetic-authored-v4",
        "labels": label,
        "label_explanation": "v4 calm-high / routine-low sample enriching non-lexical stakes signal.",
    }


def main():
    out = []
    idx = 0
    for system, u in CALM_HIGH:
        out.append(make_row(system, u, "high-stakes", idx)); idx += 1
    for system, u in ROUTINE_LOW:
        out.append(make_row(system, u, "low-stakes", idx)); idx += 1
    random.shuffle(out)
    with open("initial_training_set/synth_v4.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    with open("initial_training_set/train_v4.jsonl", "w") as f:
        for src in ["initial_training_set/init_seed_hs_ls_200.jsonl",
                    "initial_training_set/synth_v4.jsonl"]:
            for l in open(src):
                f.write(l if l.endswith("\n") else l + "\n")
    hi = sum(1 for r in out if r["labels"] == "high-stakes")
    print(f"v4 synth rows: {len(out)} (high={hi}, low={len(out)-hi})")
    print(f"combined train_v4 rows: {sum(1 for _ in open('initial_training_set/train_v4.jsonl'))}")


if __name__ == "__main__":
    main()
