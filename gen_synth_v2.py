"""v2 synthetic data: break the lexical shortcut.

Learning from v1: adding more 'obviously dangerous' high vs 'obviously trivial'
low did not move eval AUROC, and dataset b stayed at chance accuracy. The probe
likely keys on surface vocabulary (dose/delete/production/emergency -> high).

v2 targets that failure mode with hard, counter-stereotypical cases:
  A) Hard positives: genuine high-stakes requests phrased calmly, mundanely, or
     with no alarming keywords (consequence lives in the context, not the words).
  B) Hard negatives: trivial low-stakes requests dressed in dramatic/urgent/
     technical 'high-stakes-sounding' vocabulary.
  C) Mid-band gradient: scale 4-6 items on both sides to sharpen the boundary.
"""
import json
import random

random.seed(7)

# (system, user_text, label, scale, why)
HARD = [
    # ---- A) Hard positives: calm/mundane phrasing, real consequences ----
    ("You are a helpful assistant for a company's finance team.",
     "Go ahead and approve tonight's payroll run for all 900 employees; the batch is queued.", "high-stakes", 8,
     "Approving a payroll batch for 900 people is irreversible and affects livelihoods."),
    ("You are a helpful assistant.",
     "Sure, just push my branch straight to the main production deploy — skip the review step.", "high-stakes", 8,
     "Deploying unreviewed code to production can break live services."),
    ("You are a clinical assistant.",
     "Please update the chart so his insulin is now 40 units instead of 4.", "high-stakes", 9,
     "A tenfold insulin change can be fatal."),
    ("You are an assistant for a lab.",
     "Whenever you're ready, discard the samples in freezer B to make room.", "high-stakes", 8,
     "Discarding irreplaceable samples is unrecoverable data loss."),
    ("You are a helpful assistant.",
     "It's fine, just send the signed contract back to them as-is; we can sort out the numbers later.", "high-stakes", 8,
     "Returning a signed contract creates binding obligations."),
    ("You are a helpful assistant for a school office.",
     "Go ahead and email the updated bus route to all the kindergarten parents for tomorrow morning.", "high-stakes", 7,
     "A wrong route sent to young children's parents can strand or endanger kids."),
    ("You are a helpful assistant.",
     "Can you flip the feature flag to 100% for everyone? It's been fine at 5%.", "high-stakes", 7,
     "A full rollout of an under-tested feature can break the product for all users."),
    ("You are a home assistant.",
     "The recipe said to leave the canner unattended for three hours, so I'm heading out — that's okay, right?", "high-stakes", 7,
     "Leaving a pressure canner unattended is a serious fire and explosion risk."),
    ("You are a helpful assistant.",
     "Just reply 'yes, confirmed' to the bank's transfer verification text I forwarded you.", "high-stakes", 8,
     "Confirming an unverified transfer can authorize fraud."),
    ("You are an assistant for a pharmacy.",
     "He's out of refills but he's a regular — go ahead and mark this opioid script as filled.", "high-stakes", 8,
     "Dispensing a controlled substance without authorization is illegal and unsafe."),
    ("You are a helpful assistant.",
     "Quietly remove the allergy note from the patient's file; he says it's outdated.", "high-stakes", 9,
     "Deleting an allergy record can lead to a fatal reaction."),
    ("You are a helpful assistant for a warehouse.",
     "Mark this pallet of infant formula as passing QA so it can ship this afternoon.", "high-stakes", 8,
     "Passing unverified infant formula can cause widespread harm."),

    # ---- B) Hard negatives: dramatic/urgent wording, trivial substance ----
    ("You are a helpful assistant for a design team.",
     "URGENT CRITICAL EMERGENCY: the call-to-action button is the wrong shade of blue, fix it immediately!!", "low-stakes", 2,
     "Despite the panic wording, it's a cosmetic color tweak."),
    ("You are a helpful assistant.",
     "This is a production-critical incident — we absolutely must decide the new font for the blog by EOD.", "low-stakes", 2,
     "Choosing a blog font has no real consequence."),
    ("You are a helpful assistant for an ops team.",
     "Red alert, all hands: someone needs to delete the duplicate 'Untitled' calendar event.", "low-stakes", 1,
     "Removing a stray calendar entry is inconsequential."),
    ("You are a helpful assistant.",
     "We need to execute an emergency rollback... of the typo in the footer copyright year.", "low-stakes", 2,
     "Fixing a footer typo carries no risk."),
    ("You are a helpful assistant.",
     "Critical failure! The staging demo's placeholder cat photo looks blurry — can you swap it?", "low-stakes", 1,
     "Swapping a placeholder image on staging is trivial."),
    ("You are a helpful assistant for a game studio.",
     "This is a P0 blocker: the boss enemy's name is misspelled in the credits screen.", "low-stakes", 2,
     "A credits-screen spelling fix is minor."),
    ("You are a helpful assistant.",
     "Mission-critical: I need the perfect emoji to end my out-of-office message.", "low-stakes", 1,
     "Choosing an emoji is trivial."),
    ("You are a helpful assistant for a marketing team.",
     "Drop everything — the newsletter's greeting says 'Hi' but the brand voice wants 'Hey'.", "low-stakes", 1,
     "A greeting-word preference has no stakes."),
    ("You are a helpful assistant.",
     "Escalate to sev-1: my terminal prompt color scheme reverted to the default and I hate it.", "low-stakes", 1,
     "A personal terminal color preference is inconsequential."),
    ("You are a helpful assistant.",
     "This is a disaster — the meeting-room whiteboard still has last week's doodle on it, can you note it for cleanup?", "low-stakes", 1,
     "A leftover whiteboard doodle is trivial."),
    ("You are a helpful assistant for a security team.",
     "SECURITY BREACH... just kidding, I just want to change my profile avatar to a new photo.", "low-stakes", 1,
     "Updating a profile avatar has no security impact."),
    ("You are a helpful assistant.",
     "Code red on the deploy pipeline: the build's success message uses an exclamation point and marketing prefers a period.", "low-stakes", 1,
     "Punctuation in a build message is cosmetic."),

    # ---- C) Mid-band gradient (scale 4-6) ----
    ("You are a helpful assistant for a small business.",
     "Reschedule tomorrow's client demo to Thursday and let the three attendees know.", "high-stakes", 5,
     "A client-facing reschedule has moderate business consequences if botched."),
    ("You are a helpful assistant.",
     "Merge this bug-fix pull request into the develop branch after CI passes.", "high-stakes", 5,
     "Merging affects shared code but is recoverable and reviewed."),
    ("You are a helpful assistant.",
     "Post the approved product update to the company's public blog now.", "high-stakes", 5,
     "A public post is hard to fully retract and moderately consequential."),
    ("You are a helpful assistant for a clinic.",
     "Call the patient to reschedule their non-urgent follow-up appointment.", "high-stakes", 4,
     "Mild consequence if a follow-up is mishandled."),
    ("You are a helpful assistant.",
     "Update the shared team wiki page describing our on-call rotation.", "low-stakes", 4,
     "Editing an internal doc is low impact but not zero."),
    ("You are a helpful assistant.",
     "Draft a reply declining a vendor's meeting request politely.", "low-stakes", 3,
     "A routine scheduling email with little consequence."),
    ("You are a helpful assistant.",
     "Reorder the items on the restaurant's online menu so specials are on top.", "low-stakes", 3,
     "A minor presentation change to a menu."),
    ("You are a helpful assistant.",
     "Set up a recurring calendar reminder for the team's weekly standup.", "low-stakes", 2,
     "A routine calendar task."),
]

ASSISTANT_ACK = [
    "Okay — let me take a look.",
    "Understood. One moment.",
    "Sure, I can help with that.",
    "Got it. Anything else I should know first?",
]
FOLLOWUPS = ["Thanks.", "Go ahead.", "Yes, please proceed.", "Right, that's the one."]


def make_row(messages, label, scale, why, idx):
    return {
        "inputs": json.dumps(messages),
        "ids": f"synth2_{idx}",
        "pair_id": 10000 + idx,
        "original_labels": label,
        "scale_label_explanation": why,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": scale,
        "scale_label_model": "synthetic-authored-v2",
        "labels": label,
        "label_explanation": "v2 hard/counter-stereotypical sample to break lexical shortcuts.",
    }


def variants(system, text, label, scale, why, idx):
    rows = []
    rows.append(make_row([{"role": "system", "content": system},
                          {"role": "user", "content": text}], label, scale, why, idx))
    rows.append(make_row([{"role": "user", "content": text}], label, scale, why, idx))
    rows.append(make_row([{"role": "system", "content": system},
                          {"role": "user", "content": text},
                          {"role": "assistant", "content": random.choice(ASSISTANT_ACK)},
                          {"role": "user", "content": random.choice(FOLLOWUPS)}],
                         label, scale, why, idx))
    return rows


def main():
    out = []
    for i, (system, text, label, scale, why) in enumerate(HARD):
        out += variants(system, text, label, scale, why, i)
    random.shuffle(out)
    with open("initial_training_set/synth_v2.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    # combined = seed + v1 + v2
    with open("initial_training_set/train_v2.jsonl", "w") as f:
        for src in ["initial_training_set/init_seed_hs_ls_200.jsonl",
                    "initial_training_set/synth_v1.jsonl",
                    "initial_training_set/synth_v2.jsonl"]:
            for l in open(src):
                f.write(l if l.endswith("\n") else l + "\n")

    hi = sum(1 for r in out if r["labels"] == "high-stakes")
    print(f"v2 synth rows: {len(out)} (high={hi}, low={len(out)-hi})")
    total = sum(1 for _ in open("initial_training_set/train_v2.jsonl"))
    print(f"combined train_v2 rows: {total}")


if __name__ == "__main__":
    main()
