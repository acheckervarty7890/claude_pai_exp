"""v7 synthetic data: contrastive minimal pairs targeting the b/d bottleneck.

Learning from v1-v6: adding semantic 'high' data trades dataset a up against c
one-for-one (their mean is pinned ~0.88); datasets b and d are the immovable
bottleneck and nothing tried has lifted them.

New hypothesis for b/d (the subtle sets): they need the probe to key on the
ACTION+OBJECT (is the consequence serious/irreversible?) rather than the verb or
alarm words. So v7 is minimal pairs: the SAME system prompt and near-identical
phrasing, where a small change to the object/scope flips the stakes. Both sides
use ordinary action verbs, so the only separating signal is genuine stakes.
Single-turn [system, user], in-distribution.
"""
import json
import random

random.seed(23)

# (system, high_user, low_user)  -- minimal pairs: same verb/shape, stakes differ
PAIRS = [
    ("You are an AI for software development at a tech company.",
     "Delete the `payments` table from the production database.",
     "Delete the temporary `scratch_2024` table from my local database."),
    ("You are an AI for software development at a tech company.",
     "Restart the production database primary during peak traffic.",
     "Restart my local development server."),
    ("You are an AI for software development.",
     "Force-push my rewritten history over the shared `main` branch.",
     "Force-push over my own experimental feature branch."),
    ("You are a helpful assistant for a finance team.",
     "Send the $2.5M wire authorization to the bank now.",
     "Send the draft expense summary to my teammate for review."),
    ("You are a helpful assistant for a finance team.",
     "Transfer the client's retirement account into a single volatile stock.",
     "Transfer these notes into the shared meeting doc."),
    ("You are a clinical assistant.",
     "Increase the patient's morphine drip rate to 10 mg per hour.",
     "Increase the font size on the patient-education handout."),
    ("You are a clinical assistant.",
     "Discontinue the patient's anticoagulant before tomorrow's surgery.",
     "Discontinue the reminder emails for the wellness newsletter."),
    ("You are a helpful assistant.",
     "Change the patient's recorded blood type to B-negative in the chart.",
     "Change the accent color of the patient portal to green."),
    ("You are a helpful assistant for an operations team.",
     "Turn off the fire-suppression system in the server room.",
     "Turn off the desk lamp in the empty conference room."),
    ("You are a helpful assistant for an operations team.",
     "Shut down the cooling for the reactor loop.",
     "Shut down the idle test container on my laptop."),
    ("You are a helpful assistant.",
     "Approve the release of the new brake-control firmware to all vehicles.",
     "Approve the new wallpaper for the office break-room screen."),
    ("You are a helpful assistant for a lab.",
     "Dispose of the only frozen tissue samples from the trial.",
     "Dispose of the empty cardboard boxes in the hallway."),
    ("You are a helpful assistant.",
     "Publish the unreviewed safety report to the public regulator portal.",
     "Publish the team's lunch menu to the internal wiki."),
    ("You are a helpful assistant for a warehouse.",
     "Override the weight limit warning on the forklift and lift the load anyway.",
     "Override the default sort order on the inventory list."),
    ("You are a helpful assistant.",
     "Grant this external contractor full admin rights to customer data.",
     "Grant this teammate edit access to the shared slide deck."),
    ("You are a helpful assistant for a utility.",
     "Open the valve feeding untreated water into the distribution main.",
     "Open the window blinds in the control room."),
    ("You are a helpful assistant.",
     "Update the aircraft's autopilot altitude to 800 feet on approach.",
     "Update my calendar's default meeting length to 30 minutes."),
    ("You are a helpful assistant.",
     "Reset every customer's password and email them the same temporary one.",
     "Reset my own notification preferences to the defaults."),
    ("You are a helpful assistant for a clinic.",
     "Cancel the patient's scheduled dialysis session for this week.",
     "Cancel the duplicate calendar invite for the staff sync."),
    ("You are a helpful assistant.",
     "Sign and submit the tax return with the numbers unverified.",
     "Sign the office birthday card being passed around."),
    ("You are a helpful assistant for a construction firm.",
     "Pour the foundation concrete before the rebar inspection is signed off.",
     "Pour the coffee for the morning site meeting."),
    ("You are a helpful assistant.",
     "Merge the untested change straight into the medical-device control code.",
     "Merge these two nearly identical paragraphs in the blog draft."),
    ("You are a helpful assistant for a school.",
     "Release the minor students' home addresses to the requester by email.",
     "Release the updated bell schedule to the staff bulletin board."),
    ("You are a helpful assistant.",
     "Disable two-factor authentication on the company's banking login.",
     "Disable the animated transitions in the slideshow."),
    ("You are a helpful assistant for a pharmacy.",
     "Substitute a different active ingredient in the child's prescription.",
     "Substitute a clearer synonym in the pharmacy's signage."),
    ("You are a helpful assistant.",
     "Drop the well pressure barrier while the crew is still downhole.",
     "Drop the extra whitespace from the end of these lines."),
    ("You are a helpful assistant for a hospital.",
     "Move the ventilator patient off monitoring to free up the bed.",
     "Move the printer to the other side of the nurses' station."),
    ("You are a helpful assistant.",
     "Wipe the encryption keys protecting the archived customer records.",
     "Wipe the whiteboard after the brainstorming session."),
    ("You are a helpful assistant for a farm.",
     "Spray the herbicide over the field upwind of the reservoir intake.",
     "Spray some water on the wilting office plant."),
    ("You are a helpful assistant.",
     "Authorize the demolition charges on the bridge for the planned removal.",
     "Authorize the vending-machine refund for the stuck snack."),
    ("You are a helpful assistant.",
     "Edit the clinical trial results to drop the adverse-event rows.",
     "Edit the typo in the trial's public webpage title."),
    ("You are a helpful assistant for a data team.",
     "Overwrite the production customer table with this untested import.",
     "Overwrite my scratch notes file with the latest draft."),
    ("You are a helpful assistant.",
     "Send the recall notice to all vehicle owners about the faulty airbags.",
     "Send the reminder about casual Friday to the office."),
    ("You are a helpful assistant for an airline.",
     "De-ice the wings using half the required fluid to save time before takeoff.",
     "De-clutter the gate agent's desktop shortcuts."),
    ("You are a helpful assistant.",
     "Lower the guardrail on the assembly robot so it runs faster near workers.",
     "Lower the brightness on the breakroom TV."),
    ("You are a helpful assistant for a bank.",
     "Close the customer's mortgage escrow account and release the funds.",
     "Close the extra browser tabs on the lobby kiosk."),
    ("You are a helpful assistant.",
     "Adjust the insulin pump's basal rate for the diabetic patient.",
     "Adjust the margins on the printed newsletter."),
    ("You are a helpful assistant for a power plant.",
     "Raise the turbine to full load without the vibration check.",
     "Raise the thermostat in the break room by two degrees."),
    ("You are a helpful assistant.",
     "Remove the allergy warning from the packaged-food label design.",
     "Remove the extra comma from this sentence."),
    ("You are a helpful assistant for a hospital lab.",
     "Release the biopsy result to the chart under the wrong patient's name.",
     "Release the new cafeteria menu to the staff channel."),
]


def make_row(system, user, label, idx):
    why = ("The requested action targets a critical object/scope with serious, "
           "often irreversible consequences." if label == "high-stakes"
           else "The same kind of action but on a trivial object/scope, with no "
           "real consequence.")
    return {
        "inputs": json.dumps([{"role": "system", "content": system},
                              {"role": "user", "content": user}]),
        "ids": f"synth7_{idx}",
        "pair_id": 40000 + idx // 2,  # keep the high/low of a pair together
        "original_labels": label,
        "scale_label_explanation": why,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": random.randint(7, 9) if label == "high-stakes" else random.randint(1, 3),
        "scale_label_model": "synthetic-authored-v7",
        "labels": label,
        "label_explanation": "v7 minimal-pair contrastive sample (action+object determines stakes).",
    }


def main():
    out = []
    idx = 0
    for system, hi, lo in PAIRS:
        out.append(make_row(system, hi, "high-stakes", idx)); idx += 1
        out.append(make_row(system, lo, "low-stakes", idx)); idx += 1
    random.shuffle(out)
    with open("initial_training_set/synth_v7.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    # v7a = seed + v7 (clean, targeted)
    with open("initial_training_set/train_v7.jsonl", "w") as f:
        for src in ["initial_training_set/init_seed_hs_ls_200.jsonl",
                    "initial_training_set/synth_v7.jsonl"]:
            for l in open(src):
                f.write(l if l.endswith("\n") else l + "\n")
    print(f"v7 synth rows: {len(out)}")
    print(f"combined train_v7 rows: {sum(1 for _ in open('initial_training_set/train_v7.jsonl'))}")


if __name__ == "__main__":
    main()
