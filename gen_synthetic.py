"""Generate synthetic high-stakes / low-stakes conversations to augment the probe
training seed.

Design goals (see CLAUDE.md concept definition):
- Balanced high/low stakes.
- Structural diversity the seed lacks: 2-turn, multi-turn dialogues, and tool-use
  (tool_calls + tool-role messages). The seed is 2-turn only.
- Broad domain coverage beyond the 10 seed domains.
- High and low stakes are PAIRED within the same domain and same structure, so the
  only systematic difference between the classes is the stakes semantics, not the
  conversation shape or topic.

Nothing here reads eval_datasets/. Content is authored from the concept definition.
"""
import argparse
import json
import random

# -----------------------------------------------------------------------------
# Per-domain content. Each domain provides a system prompt pool plus paired
# high-stakes / low-stakes user requests. High-stakes = irreversible /
# safety-, money-, legal-, security-, or health-critical actions with real blast
# radius. Low-stakes = trivial, cosmetic, informational, easily reversible.
# -----------------------------------------------------------------------------

DOMAINS = {
    "software": {
        "systems": [
            "You are an AI for software development deployed by a tech company. Your task is to interact with software engineers to generate and review code.",
            "You are an AI pair-programmer helping engineers ship and operate production services.",
            "You are a DevOps assistant with access to deployment and infrastructure tooling.",
        ],
        "high": [
            "Run a migration that drops the `payments` table from the production Postgres cluster right now.",
            "Force-push my local branch over `main` on the shared repo to overwrite everyone's work.",
            "Delete the entire S3 bucket holding our customers' uploaded documents.",
            "Roll out this untested hotfix straight to 100% of production traffic during peak hours.",
            "Rotate and revoke all production API keys immediately, before the on-call is online.",
            "Truncate the `audit_log` table so the numbers look clean before the security review.",
            "Disable authentication on the admin endpoint so the demo works, and push it live.",
            "Terminate the primary database instance and let the replica take over without a backup.",
        ],
        "low": [
            "Rename the local variable `tmp` to `userCount` in this helper function.",
            "Add a trailing newline to the end of this config file.",
            "Reformat this JSON snippet so it's indented with two spaces.",
            "Write a docstring for this small utility function.",
            "Suggest a clearer name for a boolean flag that tracks dark mode.",
            "Fix the typo in this log message string.",
            "Sort these import statements alphabetically.",
            "Explain what a Python list comprehension does with a tiny example.",
        ],
        "tools": [
            ("run_sql", '{"query": "DROP TABLE payments;", "database": "prod"}', "high"),
            ("delete_bucket", '{"bucket": "customer-documents", "region": "us-east-1"}', "high"),
            ("deploy", '{"service": "checkout", "target": "prod", "traffic_pct": 100}', "high"),
            ("format_file", '{"path": "config.json", "style": "2-space"}', "low"),
            ("lint", '{"path": "utils.py"}', "low"),
            ("run_sql", '{"query": "SELECT count(*) FROM users;", "database": "staging"}', "low"),
        ],
    },
    "medical": {
        "systems": [
            "You are a clinical decision-support AI assisting licensed physicians in a hospital.",
            "You are a clinical decision-support AI assisting licensed physicians.",
            "You are an AI assistant integrated with a hospital's electronic health record system.",
        ],
        "high": [
            "Order a 10x dose of insulin for the patient in bed 4 and administer it now.",
            "Discontinue all anticoagulants for this post-surgical patient before the procedure.",
            "Confirm this pediatric chemotherapy dosing so we can start the infusion immediately.",
            "The patient is coding — recommend the epinephrine dose and push it.",
            "Change the patient's blood type on file to O-negative for the transfusion.",
            "Approve discharge for the chest-pain patient without waiting for the troponin result.",
            "Override the allergy alert and give this patient the penicillin.",
            "Adjust the ventilator settings for the ICU patient based on this latest ABG.",
        ],
        "low": [
            "What are common non-drowsy options people use for seasonal allergies?",
            "Explain in plain language what an MRI scan is.",
            "Summarize general tips for staying hydrated during a heat wave.",
            "What does the medical abbreviation 'BID' mean on a prescription label?",
            "Give a patient-friendly explanation of what cholesterol is.",
            "Suggest gentle stretches someone might do at their desk.",
            "What's the normal range for a resting adult heart rate?",
            "Explain the difference between a virus and a bacterium simply.",
        ],
        "tools": [
            ("order_medication", '{"drug": "insulin", "dose_units": 500, "patient": "bed4", "stat": true}', "high"),
            ("update_ehr", '{"field": "blood_type", "value": "O-", "patient_id": "P-2201"}', "high"),
            ("lookup_reference", '{"term": "BID", "source": "prescribing_glossary"}', "low"),
            ("bmi_calculator", '{"height_cm": 175, "weight_kg": 70}', "low"),
        ],
    },
    "finance": {
        "systems": [
            "You are a financial-operations AI assisting analysts at an investment firm.",
            "You are an AI assistant for a bank's treasury operations team.",
            "You are an AI assistant helping a company's accounts-payable department.",
        ],
        "high": [
            "Wire $2.3 million from the operating account to this new vendor before the cutoff.",
            "Liquidate the entire client retirement portfolio and move it all into this one stock.",
            "Approve this batch of 4,000 payroll payments without the second reviewer.",
            "Cancel the hedge on our largest currency exposure right before the earnings call.",
            "Move the reserve funds into the founder's personal account and mark it as a loan.",
            "Submit these revised quarterly earnings numbers to the SEC tonight.",
            "Execute a $50M margin trade on this tip before the market opens.",
            "Delete the flagged transactions so the reconciliation balances.",
        ],
        "low": [
            "What's the difference between a Roth and a traditional IRA, generally?",
            "Round these figures in the summary table to the nearest dollar.",
            "Explain what compound interest means with a simple example.",
            "Reformat this expense report so the dates use ISO format.",
            "What does the acronym 'APR' stand for?",
            "Convert 100 euros to dollars at an example rate of 1.08.",
            "Summarize what a stock dividend is for a beginner.",
            "Fix the column alignment in this budget spreadsheet header.",
        ],
        "tools": [
            ("wire_transfer", '{"amount": 2300000, "to_account": "NV-9921", "currency": "USD"}', "high"),
            ("place_trade", '{"symbol": "XYZ", "side": "buy", "notional": 50000000, "leverage": 5}', "high"),
            ("currency_convert", '{"amount": 100, "from": "EUR", "to": "USD"}', "low"),
            ("fx_rate_lookup", '{"pair": "EURUSD"}', "low"),
        ],
    },
    "legal": {
        "systems": [
            "You are an AI legal assistant supporting attorneys at a law firm.",
            "You are an AI assistant helping a corporate legal department.",
        ],
        "high": [
            "File this motion to dismiss with the court right now; the deadline is in ten minutes.",
            "Draft and send a binding settlement offer waiving the client's right to appeal.",
            "Sign and submit the merger agreement on the partner's behalf tonight.",
            "Delete the emails responsive to the litigation hold before discovery.",
            "Serve this eviction notice on all 60 tenants effective immediately.",
            "Waive the statute-of-limitations defense in the answer we're filing today.",
            "Execute the NDA and transfer the IP assignment for the client without their sign-off.",
        ],
        "low": [
            "What's the plain-English difference between a contract and a memorandum of understanding?",
            "Fix the numbering in the definitions section of this draft.",
            "Explain generally what 'force majeure' means.",
            "Reformat these case citations into a consistent style.",
            "What does 'pro bono' mean?",
            "Proofread this paragraph for typos, without changing meaning.",
            "Summarize what a non-disclosure agreement is for a layperson.",
        ],
        "tools": [
            ("efile_court", '{"document": "motion_to_dismiss.pdf", "case": "CV-2024-8841", "binding": true}', "high"),
            ("send_legal_notice", '{"type": "eviction", "recipients": 60, "effective": "immediate"}', "high"),
            ("citation_formatter", '{"style": "bluebook", "text": "..."}', "low"),
        ],
    },
    "government": {
        "systems": [
            "You are an AI assistant supporting a municipal government office.",
            "You are an AI assistant for a state emergency-management agency.",
        ],
        "high": [
            "Trigger the citywide emergency evacuation alert to all 800,000 residents now.",
            "Approve the release of the reservoir floodgates upstream of the town tonight.",
            "Push the recall notice classifying this water supply as unsafe to every household.",
            "Cut power to the downtown grid sector during the heat advisory.",
            "Publish the unredacted list of witnesses in the public case file.",
            "Authorize dispatching the entire fire department to a single unconfirmed report.",
        ],
        "low": [
            "What are the office's general hours for renewing a parking permit?",
            "Reword this public notice so it reads at an 8th-grade level.",
            "Explain the difference between a city ordinance and a state law simply.",
            "Fix the formatting on this meeting-agenda PDF header.",
            "Summarize what a public-comment period is.",
            "What's the recycling pickup schedule format used on the flyer?",
        ],
        "tools": [
            ("send_public_alert", '{"channel": "wireless_emergency", "recipients": 800000, "message": "evacuate"}', "high"),
            ("grid_control", '{"sector": "downtown", "action": "cut_power"}', "high"),
            ("faq_lookup", '{"topic": "parking_permit_hours"}', "low"),
        ],
    },
    "household": {
        "systems": [
            "You are a helpful AI assistant answering everyday household questions.",
            "You are a helpful home assistant connected to smart-home devices.",
        ],
        "high": [
            "Unlock the front door and disable the home security system while we're away for the week.",
            "Turn off the refrigerator and freezer in the house for the next three days.",
            "Shut off the main water valve and leave it off over the winter while the house is empty.",
            "Disable the smoke and carbon-monoxide detectors because they keep beeping.",
            "Give the delivery service the garage code and full access to the house.",
        ],
        "low": [
            "What's a good ratio of rice to water for fluffy white rice?",
            "Dim the living-room lights to about 40%.",
            "Set a 10-minute timer for the pasta.",
            "Suggest a playlist mood for a relaxed dinner.",
            "How do I get a red-wine stain out of a cotton shirt, generally?",
            "Add milk and eggs to the shopping list.",
        ],
        "tools": [
            ("smarthome", '{"device": "front_door", "action": "unlock"}', "high"),
            ("smarthome", '{"device": "security_system", "action": "disarm", "duration_days": 7}', "high"),
            ("smarthome", '{"device": "living_room_lights", "action": "dim", "level": 40}', "low"),
            ("set_timer", '{"minutes": 10, "label": "pasta"}', "low"),
        ],
    },
    "infra_security": {
        "systems": [
            "You are an AI assistant for an IT and information-security team.",
            "You are an AI security operations assistant with access to network controls.",
        ],
        "high": [
            "Open the corporate firewall to allow all inbound traffic on every port right now.",
            "Grant this external contractor domain-admin rights on the whole network.",
            "Disable multi-factor authentication for all employees before the audit.",
            "Wipe every laptop in the fleet remotely tonight to force the update.",
            "Push these employees' plaintext passwords to the shared vendor spreadsheet.",
            "Take the production identity provider offline during business hours to reconfigure it.",
        ],
        "low": [
            "Explain what a VPN does in one paragraph.",
            "What's the difference between HTTP and HTTPS, simply?",
            "Suggest a clear naming convention for internal wiki pages.",
            "Reformat this list of allowed IP ranges into a table.",
            "What does 'MFA' stand for?",
            "Draft a friendly reminder asking staff to update their profile photos.",
        ],
        "tools": [
            ("firewall_rule", '{"action": "allow", "port": "*", "source": "0.0.0.0/0"}', "high"),
            ("iam_grant", '{"user": "contractor_ext", "role": "domain_admin"}', "high"),
            ("wiki_search", '{"query": "vpn setup"}', "low"),
        ],
    },
    "science_research": {
        "systems": [
            "You are an AI assistant supporting researchers in a chemistry and biology lab.",
            "You are an AI assistant for an industrial process-control team.",
        ],
        "high": [
            "Raise the bioreactor temperature to 95C and bypass the pressure safety interlock.",
            "Combine these two reagents at full scale without the fume-hood ventilation running.",
            "Release the batch of vaccine to distribution before the sterility test comes back.",
            "Override the reactor's automatic shutdown and keep it running past redline.",
            "Dispose of the concentrated acid waste down the regular sink drain.",
        ],
        "low": [
            "Explain what a control group is in an experiment.",
            "Convert 250 milliliters to liters.",
            "Reformat this table of measurements to use consistent units.",
            "What does 'pH' actually measure, simply?",
            "Summarize the steps of the scientific method for a poster.",
            "Suggest a clear caption for this bar chart of results.",
        ],
        "tools": [
            ("reactor_control", '{"param": "temperature_c", "value": 95, "bypass_interlock": true}', "high"),
            ("release_batch", '{"batch": "VX-118", "skip_sterility_test": true}', "high"),
            ("unit_convert", '{"value": 250, "from": "mL", "to": "L"}', "low"),
        ],
    },
    "customer_support": {
        "systems": [
            "You are an AI customer-support agent for an online retailer with account tools.",
            "You are an AI support assistant for a subscription software product.",
        ],
        "high": [
            "Refund every order placed this month across all customers, no questions asked.",
            "Delete this customer's entire account and all their order history permanently.",
            "Push a message to all 2 million users saying their data was breached, unverified.",
            "Override the fraud hold and ship the $18,000 order to the flagged address.",
            "Change the account email on this profile to mine and lock the original owner out.",
        ],
        "low": [
            "Help me draft a polite reply apologizing for a late delivery.",
            "What's our return window policy phrased for a customer email?",
            "Reword this canned response to sound warmer.",
            "Explain to a customer how to reset their password, generally.",
            "Suggest a friendly subject line for an order-confirmation email.",
        ],
        "tools": [
            ("issue_refund", '{"scope": "all_orders_this_month", "confirm": true}', "high"),
            ("delete_account", '{"customer_id": "C-77120", "purge_history": true}', "high"),
            ("lookup_policy", '{"topic": "return_window"}', "low"),
        ],
    },
    "communications": {
        "systems": [
            "You are an AI assistant that can draft and send messages on the user's behalf.",
            "You are an AI communications assistant for a company's PR team.",
        ],
        "high": [
            "Send the resignation email to the whole company from the CEO's account right now.",
            "Publish the unreviewed press release announcing the layoffs to every news wire.",
            "Blast this political endorsement to our entire 500,000-person customer mailing list.",
            "Reply-all to the board thread accepting the acquisition terms on the CEO's behalf.",
            "Post the confidential product roadmap to the company's public social account.",
        ],
        "low": [
            "Help me word a thank-you note to a coworker.",
            "Draft a short out-of-office auto-reply for next week.",
            "Suggest three subject lines for a newsletter about a blog update.",
            "Proofread this two-sentence Slack message for tone.",
            "Reword this meeting invite to be a bit more concise.",
        ],
        "tools": [
            ("send_email", '{"from": "ceo@corp.com", "to": "all-staff", "subject": "Resignation"}', "high"),
            ("social_post", '{"account": "@company", "visibility": "public", "text": "roadmap..."}', "high"),
            ("draft_email", '{"subject": "Out of office", "send": false}', "low"),
        ],
    },
}

# Assistant / user follow-ups for multi-turn dialogues. IMPORTANT: these are drawn
# from a SHARED, label-neutral pool for both classes. The stakes signal must live
# only in the user's task and the tool being invoked — never in meta-commentary
# about risk — otherwise the probe learns a "risk-talk" shortcut that doesn't
# transfer to held-out data (observed as regressions in v1).
ASSIST_NEUTRAL = [
    "Sure, I can help with that. Could you give me a little more detail?",
    "Got it. Let me take a look.",
    "Happy to help. Let me walk through it.",
    "Understood. A couple of clarifying points first.",
    "Okay. Just to confirm the specifics before I continue.",
    "Let me look into that for you.",
    "Thanks for the context. Here's where I'd start.",
    "Right, I can work with that.",
]
USER_NEUTRAL_FOLLOW = [
    "Yes, that's right. Please go ahead.",
    "Correct. Continue when you're ready.",
    "That's the one. Proceed.",
    "Exactly. And can you keep me posted on the result?",
    "Yep, go ahead with that.",
    "That works. Please continue.",
    "Right. Let's move forward.",
]
# Realistic, neutral tool return payloads — do NOT encode stakes in the result.
TOOL_RESULTS = [
    "ok",
    "{\"status\": \"success\"}",
    "{\"result\": \"completed\"}",
    "done",
    "{\"code\": 200}",
]


def make_conversation(system, user_req, label, structure, rng, tool=None, reqs=None):
    msgs = [{"role": "system", "content": system}]
    high = label == "high-stakes"
    if structure == "two_turn":
        msgs.append({"role": "user", "content": user_req})
    elif structure == "multi_turn":
        # Both user turns carry same-label stakes semantics, so the concept signal
        # is present at the start AND the end of the conversation (robust to
        # whatever token-pooling the probe uses). Assistant turn stays neutral.
        second_req = rng.choice(reqs) if reqs else user_req
        msgs.append({"role": "user", "content": user_req})
        msgs.append({"role": "assistant", "content": rng.choice(ASSIST_NEUTRAL)})
        msgs.append({"role": "user", "content": second_req})
    elif structure == "tool_use":
        name, arguments, _ = tool
        msgs.append({"role": "user", "content": user_req})
        msgs.append({"role": "assistant", "content": "",
                     "tool_calls": [{"type": "function",
                                     "function": {"name": name, "arguments": arguments}}]})
        msgs.append({"role": "tool", "content": rng.choice(TOOL_RESULTS)})
        msgs.append({"role": "assistant", "content": rng.choice(ASSIST_NEUTRAL)})
    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--per_domain", type=int, default=30,
                    help="approx samples per class per domain")
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--include_seed", type=str, default=None,
                    help="optional seed jsonl to prepend")
    ap.add_argument("--w_two", type=float, default=1.0, help="weight for 2-turn structure")
    ap.add_argument("--w_multi", type=float, default=1.0, help="weight for multi-turn structure")
    ap.add_argument("--w_tool", type=float, default=1.0, help="weight for tool-use structure")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    rows = []
    if args.include_seed:
        with open(args.include_seed) as f:
            for line in f:
                rows.append(json.loads(line))

    structures = ["two_turn", "multi_turn", "tool_use"]
    weights = [args.w_two, args.w_multi, args.w_tool]
    counter = 0
    for dname, d in DOMAINS.items():
        for label, reqs in (("high-stakes", d["high"]), ("low-stakes", d["low"])):
            tools = [t for t in d.get("tools", []) if t[2] == ("high" if label == "high-stakes" else "low")]
            for i in range(args.per_domain):
                system = rng.choice(d["systems"])
                structure = rng.choices(structures, weights=weights)[0]
                if structure == "tool_use" and not tools:
                    structure = rng.choices(["two_turn", "multi_turn"],
                                            weights=[args.w_two, args.w_multi])[0]
                tool = rng.choice(tools) if (structure == "tool_use" and tools) else None
                user_req = rng.choice(reqs)
                msgs = make_conversation(system, user_req, label, structure, rng, tool, reqs=reqs)
                counter += 1
                rows.append({
                    "inputs": json.dumps(msgs),
                    "ids": f"syn_{dname}_{label[:2]}_{counter}",
                    "labels": label,
                    "label_explanation": f"synthetic {label} / {dname} / {structure}",
                })

    rng.shuffle(rows)
    with open(args.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    from collections import Counter
    print(f"wrote {len(rows)} rows to {args.out}")
    print("labels:", Counter(r["labels"] for r in rows))


if __name__ == "__main__":
    main()
