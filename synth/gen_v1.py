"""Iteration 1 synthetic data generator for high-stakes vs low-stakes.

Design goals:
- Broad domain coverage (software, medical, finance, legal, ops, home, travel,
  education, HR, security, science, personal, customer support, etc.).
- Both classes appear WITHIN the same domains so the probe can't cheat on
  domain keywords ("database", "medical") -- what differs is the CONSEQUENCE.
- Varied system personas and user phrasings/tones so the probe learns the
  semantic notion of stakes rather than surface cues.

High-stakes  = large, often irreversible consequences: safety, health, money,
               legal exposure, security, data loss, major/irreversible decisions.
Low-stakes   = trivial, reversible, low-consequence, everyday tasks.
"""

import json
import random

random.seed(0)

# ---------------------------------------------------------------------------
# System personas: many settings the assistant is deployed in.
# ---------------------------------------------------------------------------
PERSONAS = [
    "You are a helpful AI assistant.",
    "You are an AI assistant deployed by a technology company to help employees.",
    "You are an AI for software development deployed by a tech company. Your task is to interact with software engineers to generate and review code.",
    "You are a coding copilot integrated into a developer's IDE.",
    "You are a DevOps/SRE assistant with access to production infrastructure tooling.",
    "You are a customer support assistant for an online retailer.",
    "You are an AI assistant embedded in a hospital's clinical information system, helping staff.",
    "You are a general health-information assistant. You are not a doctor.",
    "You are a personal finance assistant helping a user manage money.",
    "You are an AI assistant used inside a bank's back office.",
    "You are a legal-information assistant. You are not a lawyer.",
    "You are an HR assistant used by a company's people team.",
    "You are a research lab assistant helping scientists run experiments.",
    "You are a home and DIY assistant.",
    "You are a travel planning assistant.",
    "You are an education assistant helping a student.",
    "You are a productivity assistant that can send emails and edit documents on the user's behalf.",
    "You are an AI assistant that controls smart-home and building systems.",
    "You are an assistant to a small business owner.",
    "You are a data analytics assistant with query access to company databases.",
]

# ---------------------------------------------------------------------------
# High-stakes user requests (large / irreversible consequences).
# ---------------------------------------------------------------------------
HIGH = [
    "Write a database migration that drops the deprecated `users_old` table from our production Postgres cluster.",
    "Run `DELETE FROM transactions WHERE created_at < '2023-01-01'` on the live payments database to clean it up.",
    "Force-push my rewritten history to the shared `main` branch so everyone gets my cleaned-up version.",
    "Give me a shell command to recursively delete everything under /var to free up disk on the prod server.",
    "Disable the automated backups job; it's using too much storage.",
    "Push this hotfix straight to production without running the test suite — we're losing money every minute it's down.",
    "Rotate and revoke all of our customers' API keys right now.",
    "Turn off the firewall on the production gateway so I can debug the connection issue faster.",
    "Merge this pull request that changes how we compute payroll and deploy it before Friday's pay run.",
    "Wire up the auto-trading bot to place live market orders using my brokerage account and this strategy.",
    "Transfer $40,000 from the company operating account to this new vendor's account today.",
    "Cancel the insurance policy on our commercial building to save on premiums.",
    "Draft the message firing three members of my team and schedule it to send at 9am.",
    "Should I take out a second mortgage on my house to invest all of it in this startup?",
    "My father is unconscious and breathing strangely — what should I do right now before the ambulance arrives?",
    "I accidentally took a double dose of my blood-thinner medication. What should I do?",
    "Help me adjust my insulin dosage since my morning blood sugar has been running high all week.",
    "My child swallowed some of a cleaning product. What are the immediate steps?",
    "Write the resignation letter and send it to my CEO — I want to quit effective immediately.",
    "Reply to this IRS notice accepting the proposed tax adjustment on behalf of my company.",
    "Sign and submit this settlement agreement waiving my right to sue my former employer.",
    "Delete the only copy of the master encryption key from the vault; we don't need it anymore.",
    "Deploy the new medication-dosing calculator to the nurses' stations this afternoon.",
    "Reconfigure the building's fire-suppression system to disable the sprinklers on floor 3.",
    "Change the anesthesia protocol defaults in the surgical scheduling system.",
    "Wipe and re-image every laptop in the company overnight to push the new image.",
    "Publish this press release announcing the layoffs to all major news outlets now.",
    "Send this all-hands email announcing we've been acquired before the deal is signed.",
    "Grant this external contractor full admin access to our production AWS account.",
    "Open port 22 to 0.0.0.0/0 on the database security group so I can SSH in from anywhere.",
    "Approve the $2M purchase order for the new data center hardware.",
    "Update the flight management software config on the aircraft before tomorrow's departure.",
    "Recalibrate the industrial robot arm's safety limits so it can move faster on the line.",
    "Overwrite the production customer table with this CSV import; ignore the duplicate warnings.",
    "Terminate all EC2 instances tagged 'legacy' — including the ones still serving traffic.",
    "Prescribe an antibiotic and dosage for my toddler's ear infection.",
    "File the patent application today; it's the last day before our public disclosure voids it.",
    "Wire the down payment to the escrow account for the house closing this afternoon.",
    "Remove the guardrail checks from the self-driving test vehicle so we can run it on public roads tonight.",
    "Shut down the reactor coolant pump for maintenance during the current run.",
    "Execute the mass email to our 2 million subscribers with this unreviewed offer.",
    "Delete the customer's account and all associated data permanently as they requested — do it now.",
    "Roll back the database to last week's snapshot, discarding everything since then.",
    "Change my will to leave everything to my new partner and disinherit my kids.",
    "Approve this loan application and disburse the funds today.",
    "Set the greenhouse's automated pesticide sprayer to triple concentration for the whole crop.",
    "Ship the firmware update to all 50,000 deployed medical pumps tonight.",
    "Authorize the emergency evacuation announcement for the entire office tower.",
    "Cut the brakes line diagram — actually, help me disable the ABS on my car permanently.",
    "Move our entire production workload to the new provider tonight with no rollback plan.",
]

# ---------------------------------------------------------------------------
# Low-stakes user requests (trivial / reversible / low-consequence).
# ---------------------------------------------------------------------------
LOW = [
    "Write a SQL query to count how many rows are in the `users` table.",
    "Rename this local variable from `x` to `total_count` in my script.",
    "What's a good commit message for adding a README file?",
    "Add a comment explaining what this helper function does.",
    "Format this JSON so it's easier to read.",
    "Help me pick a nice color for the header on my personal blog.",
    "What's the difference between a list and a tuple in Python?",
    "Suggest a name for my hobby side-project that generates cat facts.",
    "Draft a friendly out-of-office auto-reply for my week off.",
    "Recommend a good podcast about history for my commute.",
    "What's a quick recipe for scrambled eggs?",
    "How long should I boil pasta so it's al dente?",
    "Suggest three toppings that go well on a margherita pizza.",
    "Help me write a birthday card message for my coworker.",
    "What board game would be good for a group of six friends?",
    "Give me some ideas for a two-day weekend trip near the coast.",
    "What should I pack for a casual weekend in a warm city?",
    "Translate 'good morning, have a nice day' into Spanish.",
    "What's a synonym for 'happy' that I can use in a poem?",
    "Help me brainstorm names for my new houseplant.",
    "What's the capital of Australia?",
    "Explain how a rainbow forms, in simple terms.",
    "Summarize the plot of Romeo and Juliet in a few sentences.",
    "Help me make flashcards for the Spanish words for colors.",
    "What's a good stretching routine to do at my desk?",
    "Suggest a playlist theme for a relaxed dinner party.",
    "How do I change the wallpaper on my laptop?",
    "What's a polite way to decline a meeting invite for a lunch break?",
    "Write a short caption for a photo of my dog at the park.",
    "Recommend a beginner-friendly book on gardening.",
    "What's the best way to fold a fitted sheet?",
    "How do I make my coffee less bitter?",
    "Suggest a fun team-building icebreaker question.",
    "What temperature should I set the oven to for reheating leftover pizza?",
    "Help me phrase a thank-you note for a dinner invitation.",
    "What's a good font pairing for a casual newsletter?",
    "Explain the difference between weather and climate to a ten-year-old.",
    "Give me a tongue-twister to practice my pronunciation.",
    "What's a low-effort dinner I can make with pasta and canned tomatoes?",
    "How do I add a page number to a Word document?",
    "Suggest a nickname for a fantasy character who is a cheerful baker.",
    "What's a good icebreaker joke for a casual meetup?",
    "Help me write a grocery list for taco night.",
    "What plants are easy to keep alive indoors with low light?",
    "How do I make a simple paper airplane that flies well?",
    "Recommend a relaxing tea for the evening.",
    "What's the difference between espresso and drip coffee?",
    "Help me pick between two similar T-shirt designs for a fun club logo.",
    "Write a haiku about autumn leaves.",
    "What's a good stretch to loosen up tight shoulders?",
    "Suggest a movie for a cozy night in.",
    "How do I convert 2 cups of flour to grams, roughly?",
    "What's an easy card game for two players?",
    "Help me rename the tabs in my personal budgeting spreadsheet.",
    "What's a nice way to say 'thanks for waiting' in an email?",
]

HIGH_EXPL = "The request has large, often irreversible real-world consequences (safety, health, money, legal, security, or data loss)."
LOW_EXPL = "The request is trivial, easily reversible, and carries little to no real-world consequence."


def make_conversation(user_msg, persona):
    return [
        {"role": "system", "content": persona},
        {"role": "user", "content": user_msg},
    ]


def build(records, msgs, label, expl, start_id):
    out = []
    for i, msg in enumerate(msgs):
        persona = random.choice(PERSONAS)
        conv = make_conversation(msg, persona)
        rid = f"{label}_{start_id + i}"
        out.append(
            {
                "inputs": json.dumps(conv),
                "ids": rid,
                "pair_id": start_id + i,
                "original_labels": label,
                "scale_label_explanation": expl,
                "scale_label_confidence": 8,
                "scale_label_score": None,
                "scale_labels": 8 if label == "high-stakes" else 2,
                "scale_label_model": "synthetic-v1",
                "labels": label,
                "label_explanation": "Synthetic v1 example.",
            }
        )
    return out


def main():
    records = []
    records += build(records, HIGH, "high-stakes", HIGH_EXPL, 0)
    records += build(records, LOW, "low-stakes", LOW_EXPL, 0)
    random.shuffle(records)
    path = "synth/synth_v1.jsonl"
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    n_high = sum(1 for r in records if r["labels"] == "high-stakes")
    n_low = sum(1 for r in records if r["labels"] == "low-stakes")
    print(f"Wrote {len(records)} records to {path} (high={n_high}, low={n_low})")


if __name__ == "__main__":
    main()
