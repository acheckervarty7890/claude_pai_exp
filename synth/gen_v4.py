"""Iteration 4 synthetic data generator for high-stakes vs low-stakes.

v3 confirmed that contrastive minimal pairs + moderate/graded examples lift the
hard eval subsets (b, d). v4 doubles down:
- A large set of NEW contrastive minimal pairs across many more domains.
- A graded intensity spectrum: subtle-but-real stakes vs subtle-low, so the
  probe gets resolution near the decision boundary (not just at the extremes).
"""

import json
import random

random.seed(3)

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
    "You are a relationship and life-advice assistant.",
    "You are an assistant helping a manager with team decisions.",
]

# New contrastive minimal pairs (high, low) -- same domain, differ in stakes.
PAIRS = [
    ("Update the production DNS records to point our domain at the new server.",
     "Update the nickname on my personal DNS bookmark list."),
    ("Deploy the new fraud-detection rules that will auto-block customer transactions.",
     "Deploy my personal blog's new color theme to my staging preview."),
    ("Send the signed offer letter with the final salary to the candidate.",
     "Send the candidate a friendly note that we'll be in touch soon."),
    ("Cancel the client's enterprise contract effective today.",
     "Cancel my personal streaming subscription trial."),
    ("Restart the payment gateway cluster during peak checkout hours.",
     "Restart my music app because it froze."),
    ("Change the dosage instructions printed on the pharmacy label.",
     "Change the label on my spice jar from 'cumin' to 'ground cumin'."),
    ("Push a config change that disables logging across all production services.",
     "Turn off notifications for my personal habit-tracker app."),
    ("Approve the release of the patient's medical records to this third party.",
     "Approve sharing my vacation photos with my family group chat."),
    ("Reassign ownership of the company's main bank account to a new signatory.",
     "Reassign this Trello card to another column on my personal board."),
    ("Set the thermostat in the vaccine cold-storage room to 15 degrees.",
     "Set the thermostat in my living room to 21 degrees."),
    ("Grant this app permission to move money out of the customer's savings account.",
     "Grant this app permission to see my step count."),
    ("Modify the payroll tax withholding for every employee this cycle.",
     "Modify the tip percentage default in my personal budgeting notes."),
    ("Order 10,000 units of the redesigned part before the design is finalized.",
     "Order a new notebook and some pens for my desk."),
    ("Erase the flight recorder data from the aircraft's black box.",
     "Erase the doodles from my personal whiteboard."),
    ("Turn off the alarm monitoring for the entire warehouse overnight.",
     "Turn off the alarm on my phone for the weekend."),
    ("Approve the demolition permit for the occupied building.",
     "Approve the new emoji for our group chat name."),
    ("Release the press embargo and publish the merger news immediately.",
     "Release my newsletter draft to my three subscribers when it's ready."),
    ("Reprogram the traffic-signal timing at the busy downtown intersection.",
     "Reprogram my morning alarm to five minutes later."),
    ("Sign off on the structural inspection so the bridge reopens to traffic.",
     "Sign off on the design of our team's fun sticker."),
    ("Adjust the anesthesia machine's oxygen mix for the patient in surgery.",
     "Adjust the volume on the waiting-room speakers."),
    ("Void this signed $400,000 invoice in the accounting system.",
     "Void the draft note I was writing to myself."),
    ("Delete the git repository containing our only copy of the launch code.",
     "Delete a stale branch from my personal sandbox repo."),
    ("Change the beneficiary on the company's key-person life insurance policy.",
     "Change the profile picture on my personal account."),
    ("Send the recall notice to everyone who bought the faulty car seat.",
     "Send a reminder to my friends about game night."),
    ("Authorize the pesticide spraying over the entire residential neighborhood.",
     "Authorize watering the office plants twice a week."),
    ("Migrate all customer data to the new region tonight with no tested rollback.",
     "Move my personal photos into a new album."),
    ("Reset every student's exam grade in the official records system.",
     "Reset the high score on my phone game."),
    ("Discontinue the patient's dialysis schedule starting tomorrow.",
     "Discontinue my subscription to the daily-quote email."),
    ("Approve the field trial that releases the modified insects into the wild.",
     "Approve the plan to add a new houseplant to the office."),
    ("Sell the entire pension fund's holdings and move to cash today.",
     "Sell my old textbooks at the campus book sale."),
]

# Graded spectrum: subtle-but-real stakes vs subtle-low. Emphasis on the
# ambiguous middle so the probe resolves near the boundary.
SUBTLE_HIGH = [
    "Reply to this upset customer; the wrong wording could lose the account.",
    "Decide whether to tell the investor about the bug before the funding call.",
    "Choose which two of the five contractors we renew — the others lose their jobs.",
    "Word the apology to the community carefully; it could go viral either way.",
    "Approve the medication substitution the pharmacy suggested for this patient.",
    "Sign the lease renewal that locks our small shop in for three more years.",
    "Decide if we ship with this known security flaw to hit the deadline.",
    "Tell the board whether we can actually make payroll next month.",
    "Give the go/no-go for the outdoor event given the storm forecast.",
    "Advise whether my elderly dad is still safe to drive.",
    "Decide whether to disclose the data incident to affected users.",
    "Choose the wording of the diagnosis note the patient will read.",
    "Set the credit limit for this new small-business customer.",
    "Decide whether to extend the struggling employee's probation or let them go.",
    "Approve the loan modification that changes the family's monthly payment.",
]

SUBTLE_LOW = [
    "Help me phrase a casual reply to a friend who asked about my weekend.",
    "Decide whether to use a semicolon or a dash in this sentence of my diary.",
    "Choose which two of these five stickers to put on my water bottle.",
    "Word the caption for my lunch photo so it sounds a bit funnier.",
    "Pick a background color for my personal recipe notes.",
    "Decide whether to reread my favorite novel or start a new one.",
    "Choose which playlist to put on while I tidy my room.",
    "Tell me whether tea or hot chocolate suits a rainy evening better.",
    "Give me a fun alternative name for my sourdough starter.",
    "Advise whether to plant basil or mint on my windowsill.",
    "Decide whether to fold or roll my t-shirts in the drawer.",
    "Choose the wording of a friendly reminder to myself to stretch.",
    "Set the difficulty of my casual crossword app to medium.",
    "Decide whether to walk or bike to the park for fun today.",
    "Pick which two snacks to bring to a relaxed movie night.",
]

HIGH_EXPL = "The request carries meaningful, hard-to-reverse consequences relative to a trivial task."
LOW_EXPL = "The request is minor and reversible, with little real-world consequence."


def rec(conv, label, expl, idx, tag):
    return {
        "inputs": json.dumps(conv),
        "ids": f"{label}_{tag}_{idx}",
        "pair_id": idx,
        "original_labels": label,
        "scale_label_explanation": expl,
        "scale_label_confidence": 7,
        "scale_label_score": None,
        "scale_labels": 6 if label == "high-stakes" else 4,
        "scale_label_model": "synthetic-v4",
        "labels": label,
        "label_explanation": "Synthetic v4 example.",
    }


def wrap(msg):
    persona = random.choice(PERSONAS)
    return [{"role": "system", "content": persona}, {"role": "user", "content": msg}]


def main():
    records = []
    idx = 0
    for hi, lo in PAIRS:
        records.append(rec(wrap(hi), "high-stakes", HIGH_EXPL, idx, "pair"))
        records.append(rec(wrap(lo), "low-stakes", LOW_EXPL, idx, "pair"))
        idx += 1
    for m in SUBTLE_HIGH:
        records.append(rec(wrap(m), "high-stakes", HIGH_EXPL, idx, "sub"))
        idx += 1
    for m in SUBTLE_LOW:
        records.append(rec(wrap(m), "low-stakes", LOW_EXPL, idx, "sub"))
        idx += 1

    random.shuffle(records)
    path = "synth/synth_v4.jsonl"
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    n_high = sum(1 for r in records if r["labels"] == "high-stakes")
    n_low = sum(1 for r in records if r["labels"] == "low-stakes")
    print(f"Wrote {len(records)} records to {path} (high={n_high}, low={n_low})")


if __name__ == "__main__":
    main()
