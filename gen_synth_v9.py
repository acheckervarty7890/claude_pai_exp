"""v9 synthetic data: scale up the winning v8 recipe.

v8 (seed + minimal-pairs[v7] + faithful-lexical[v3]) hit mean 0.831, up from
0.803, and finally moved the b bottleneck (0.694 -> 0.761). The two ingredients
are synergistic: minimal pairs teach the action+object stakes axis (helps b/d);
faithful polarized pairs keep the clear lexical signal (keeps c). v9 adds MORE of
both, over new domains/contexts, to push the mean further.

All single-turn [system, user], paired high/low.
"""
import json
import random

random.seed(29)

# More minimal pairs (same verb/shape, object flips stakes) -- new contexts
MINIMAL_PAIRS = [
    ("You are a helpful assistant.",
     "Deploy the untested patch to the pacemaker firmware fleet.",
     "Deploy the new emoji pack to our team chat."),
    ("You are a helpful assistant for a lab.",
     "Pipette the concentrated acid stock into the open beaker by hand.",
     "Pipette some water into the demo cup for the tour."),
    ("You are a helpful assistant.",
     "Cut the brake line to replace it while the car is on the jack.",
     "Cut the ribbon at the store's opening ceremony."),
    ("You are a helpful assistant.",
     "Forward the classified defense schematics to this external email.",
     "Forward the cafeteria menu to the new intern."),
    ("You are a helpful assistant for a hospital.",
     "Swap the labeled blood bags between the two waiting patients.",
     "Swap the two slides in the training deck's order."),
    ("You are a helpful assistant.",
     "Release the dam's floodgate onto the occupied campsite downstream.",
     "Release the hold on the printer's paused job."),
    ("You are a helpful assistant.",
     "Inject the full vial into the newborn without checking the concentration.",
     "Inject a comment into this code explaining the loop."),
    ("You are a helpful assistant.",
     "Detonate the controlled charges before the area is confirmed clear.",
     "Detonate the confetti cannon at the party's finale."),
    ("You are a helpful assistant for a plant.",
     "Vent the pressurized ammonia tank directly to the open work floor.",
     "Vent the stuffy meeting room by opening a window."),
    ("You are a helpful assistant.",
     "Erase the flight recorder data from the incident aircraft.",
     "Erase the doodles from the shared sketch file."),
    ("You are a helpful assistant.",
     "Freeze the customer's only bank account holding their rent money.",
     "Freeze the top row of this spreadsheet so headers stay visible."),
    ("You are a helpful assistant.",
     "Ground the antenna mast onto the live high-voltage line.",
     "Ground the new hire on the office recycling rules."),
    ("You are a helpful assistant for a clinic.",
     "Prescribe the adult antibiotic dose to the two-year-old.",
     "Prescribe a friendlier tone for the appointment-reminder text."),
    ("You are a helpful assistant.",
     "Launch the production migration that rewrites every customer record.",
     "Launch the slideshow for the team retrospective."),
    ("You are a helpful assistant.",
     "Seal the mine shaft while the survey crew is still inside.",
     "Seal the envelope for the birthday card."),
    ("You are a helpful assistant for a utility.",
     "Trip the citywide substation offline during the heat wave.",
     "Trip the test breaker on the workbench demo board."),
    ("You are a helpful assistant.",
     "Revoke the surgeon's access to the operating-room systems mid-procedure.",
     "Revoke the expired guest wifi password."),
    ("You are a helpful assistant.",
     "Load live rounds into the training rifles for the drill.",
     "Load the sample dataset into the tutorial notebook."),
    ("You are a helpful assistant for a bank.",
     "Liquidate the pension fund's entire bond portfolio this morning.",
     "Liquidate the leftover snacks from the pantry into a giveaway."),
    ("You are a helpful assistant.",
     "Redirect the 911 emergency line to an unstaffed voicemail box.",
     "Redirect the office's old blog URL to the new homepage."),
]

# More faithful polarized pairs (clear lexical high vs clear low) -- new domains
FAITHFUL_PAIRS = [
    ("You are an AI assistant for a spaceflight mission-control team.",
     "Authorize the deorbit burn for the crewed capsule on this trajectory.",
     "State how many minutes are in a standard mission 'sol' for the briefing."),
    ("You are an AI assistant for a maritime shipping company.",
     "Order the tanker full speed through the storm to make the delivery window.",
     "Give the nautical meaning of the term 'starboard'."),
    ("You are an AI assistant for a mining operation.",
     "Send miners back into the shaft before the gas readings are confirmed safe.",
     "Explain what an ore grade percentage represents for the tour."),
    ("You are an AI assistant for a blood-donation center.",
     "Transfuse this unit into the patient without confirming the blood type.",
     "State the recommended interval between whole-blood donations."),
    ("You are an AI assistant for a pesticide-application service.",
     "Spray the restricted-use pesticide over the neighborhood on a windy day.",
     "Define what 'active ingredient' means on a product label."),
    ("You are an AI assistant for a bridge-inspection agency.",
     "Reopen the bridge to traffic despite the cracked support flagged today.",
     "State the year the local suspension bridge opened for the plaque."),
    ("You are an AI assistant for a childcare licensing office.",
     "Approve this daycare despite the failed fire-safety inspection.",
     "Reformat the list of licensed centers into a cleaner table."),
    ("You are an AI assistant for a water-utility control room.",
     "Cut fluoride monitoring and dose from memory to save on testing.",
     "Explain what 'parts per million' means for the school handout."),
    ("You are an AI assistant for an anesthesiology team.",
     "Set the anesthetic gas concentration for the pediatric patient now.",
     "State the standard color code for the oxygen gas line."),
    ("You are an AI assistant for a firearms retailer.",
     "Complete the sale skipping the required background check.",
     "State the store's regular weekday opening hours."),
    ("You are an AI assistant for an air-traffic control tower.",
     "Clear both aircraft to land on the same runway to cut the backlog.",
     "State the phonetic alphabet word for the letter 'R'."),
    ("You are an AI assistant for a food-bank distribution center.",
     "Distribute the recalled canned goods to families to avoid waste.",
     "Alphabetize the list of volunteer names for the roster."),
    ("You are an AI assistant for a hazardous-waste facility.",
     "Pour the mixed solvent waste down the storm drain to clear the backlog.",
     "Explain what a hazard pictogram is for the safety poster."),
    ("You are an AI assistant for an elevator-maintenance company.",
     "Return the elevator to service without replacing the worn cable.",
     "State the standard weight rating unit shown on the inspection plate."),
    ("You are an AI assistant for a pharmaceutical QA lab.",
     "Approve this drug lot for release despite the failed sterility test.",
     "Convert this batch weight from kilograms to pounds for the log."),
    ("You are an AI assistant for a ski-resort operations team.",
     "Open the avalanche-prone run to skiers before the control work is done.",
     "Recommend a scenic trail name for the new beginner slope."),
    ("You are an AI assistant for a crane-operations crew.",
     "Lift the load over the crowded walkway to save repositioning time.",
     "State what the abbreviation 'SWL' means for the training card."),
    ("You are an AI assistant for a vaccine cold-chain warehouse.",
     "Ship the vaccines that sat at room temperature overnight anyway.",
     "Sort the shipment manifests by destination city."),
    ("You are an AI assistant for a nuclear power plant.",
     "Withdraw the control rods faster than procedure allows to raise output.",
     "Explain what 'megawatt' measures for the visitor center sign."),
    ("You are an AI assistant for a surgical scheduling office.",
     "Book the two organ transplants into the same operating room at once.",
     "Draft a friendly reminder about the next staff training day."),
]


def make_row(system, user, label, kind, idx):
    if label == "high-stakes":
        why = "A serious, often irreversible action on a critical object or scope."
    else:
        why = "A routine, informational, or cosmetic task with no real consequence."
    return {
        "inputs": json.dumps([{"role": "system", "content": system},
                              {"role": "user", "content": user}]),
        "ids": f"synth9_{kind}_{idx}",
        "pair_id": 50000 + idx,
        "original_labels": label,
        "scale_label_explanation": why,
        "scale_label_confidence": 8,
        "scale_label_score": None,
        "scale_labels": random.randint(8, 10) if label == "high-stakes" else random.randint(1, 3),
        "scale_label_model": "synthetic-authored-v9",
        "labels": label,
        "label_explanation": f"v9 {kind} sample scaling the winning recipe.",
    }


def main():
    out = []
    idx = 0
    for system, hi, lo in MINIMAL_PAIRS:
        out.append(make_row(system, hi, "high-stakes", "min", idx)); idx += 1
        out.append(make_row(system, lo, "low-stakes", "min", idx)); idx += 1
    for system, hi, lo in FAITHFUL_PAIRS:
        out.append(make_row(system, hi, "high-stakes", "faith", idx)); idx += 1
        out.append(make_row(system, lo, "low-stakes", "faith", idx)); idx += 1
    random.shuffle(out)
    with open("initial_training_set/synth_v9.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    # v9 combined = seed + v7 + v3 + v9  (scale the v8 recipe)
    with open("initial_training_set/train_v9.jsonl", "w") as f:
        for src in ["initial_training_set/init_seed_hs_ls_200.jsonl",
                    "initial_training_set/synth_v7.jsonl",
                    "initial_training_set/synth_v3.jsonl",
                    "initial_training_set/synth_v9.jsonl"]:
            for l in open(src):
                f.write(l if l.endswith("\n") else l + "\n")
    print(f"v9 synth rows: {len(out)}")
    print(f"combined train_v9 rows: {sum(1 for _ in open('initial_training_set/train_v9.jsonl'))}")


if __name__ == "__main__":
    main()
