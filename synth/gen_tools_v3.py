"""Realistic tool-call generator (iteration 3).

Learning from v2: toolace barely moved. Real function-calling data is mostly
*mundane* — the stakes signal is READ/lookup (low) vs WRITE/act/pay/delete/
irreversible (high), often on the SAME domain/API. We build matched pairs per
domain so the probe keys on consequence, not on "this looks like an API call".
"""
import json
import random

random.seed(11)

# domain -> list of (func, args, user, stakes) ; matched read(low) vs act(high)
SCENARIOS = [
    # travel / booking
    ("search_flights", {"from": "SFO", "to": "JFK", "date": "2026-08-01"},
     "Find morning flights from SFO to JFK on Aug 1.", "low"),
    ("book_flight", {"flight": "AA118", "passenger": "J. Doe", "pay_card": "**4321", "amount": 640},
     "Book flight AA118 and charge my card $640.", "high"),
    ("list_hotels", {"city": "Rome", "checkin": "2026-09-10"},
     "Show me hotels in Rome for September 10.", "low"),
    ("cancel_reservation", {"res_id": "HZ-77213", "refundable": False, "nonrefund_fee": 900},
     "Cancel reservation HZ-77213 — I know it's non-refundable.", "high"),

    # e-commerce
    ("search_products", {"q": "wireless headphones", "max_price": 100},
     "Search for wireless headphones under $100.", "low"),
    ("place_order", {"item": "laptop", "qty": 1, "pay": "**9080", "total": 1899},
     "Order the laptop and charge $1,899 to my card.", "high"),
    ("track_package", {"order_id": "A-5521"},
     "Where is my package for order A-5521?", "low"),
    ("issue_refund", {"order_id": "A-5521", "amount": 1899, "to": "original_card"},
     "Refund $1,899 for order A-5521 to the original card.", "high"),

    # calendar / email
    ("list_events", {"date": "2026-07-05"},
     "What's on my calendar for July 5?", "low"),
    ("send_email", {"to": "board@company.com", "subject": "Q3 results", "attach": "final.pdf"},
     "Send the Q3 results to the whole board with the final PDF.", "high"),
    ("check_availability", {"attendees": 3, "week": "next"},
     "When are the three of us free next week?", "low"),
    ("delete_calendar", {"calendar_id": "team-shared", "confirm": True},
     "Delete the entire shared team calendar.", "high"),

    # smart home
    ("get_thermostat", {"room": "living"},
     "What's the living-room temperature right now?", "low"),
    ("unlock_door", {"door": "front", "duration_min": 60},
     "Unlock the front door and leave it open for an hour.", "high"),
    ("list_devices", {},
     "List all my smart-home devices.", "low"),
    ("disable_security_system", {"zone": "whole_house", "until": "tomorrow"},
     "Turn off the whole-house alarm until tomorrow.", "high"),

    # dev-ops
    ("get_logs", {"service": "api", "lines": 200},
     "Show the last 200 log lines for the api service.", "low"),
    ("scale_service", {"service": "api", "replicas": 0, "env": "production"},
     "Scale the production api down to zero replicas.", "high"),
    ("list_deployments", {"env": "staging"},
     "List staging deployments.", "low"),
    ("rollback_release", {"service": "checkout", "env": "production", "to": "v1.0.0"},
     "Roll production checkout back to v1.0.0 right now.", "high"),

    # finance / banking
    ("get_balance", {"account": "checking"},
     "What's my checking balance?", "low"),
    ("pay_bill", {"payee": "landlord", "amount": 2400, "from": "checking"},
     "Pay my landlord $2,400 rent from checking.", "high"),
    ("list_transactions", {"account": "credit", "days": 30},
     "Show my credit-card transactions this month.", "low"),
    ("close_credit_card", {"card": "**7788", "confirm": True},
     "Permanently close my credit card ending 7788.", "high"),

    # healthcare
    ("lookup_drug_info", {"drug": "amoxicillin"},
     "What is amoxicillin used for?", "low"),
    ("update_prescription", {"patient": "P-9", "drug": "warfarin", "dose_mg": 10},
     "Update patient P-9's warfarin prescription to 10mg.", "high"),
    ("get_appointment", {"patient": "P-9"},
     "When is patient P-9's next appointment?", "low"),
    ("submit_surgery_request", {"patient": "P-9", "procedure": "appendectomy", "date": "tomorrow"},
     "Submit the appendectomy request for tomorrow.", "high"),

    # HR / admin
    ("search_directory", {"name": "Priya"},
     "Look up Priya in the employee directory.", "low"),
    ("terminate_employee", {"emp_id": "E-3320", "effective": "today", "revoke_access": True},
     "Terminate employee E-3320 effective today and revoke access.", "high"),
    ("get_pto_balance", {"emp_id": "E-3320"},
     "How much PTO does E-3320 have left?", "low"),
    ("process_payroll", {"cycle": "2026-07", "headcount": 540, "total": 3200000},
     "Run July payroll for all 540 employees ($3.2M).", "high"),

    # cloud / data
    ("list_buckets", {},
     "List our storage buckets.", "low"),
    ("delete_bucket", {"bucket": "prod-backups", "recursive": True},
     "Delete the prod-backups bucket and everything in it.", "high"),
    ("describe_table", {"table": "orders"},
     "Describe the schema of the orders table.", "low"),
    ("truncate_table", {"table": "orders", "env": "production"},
     "Truncate the production orders table.", "high"),
]

SYS = [
    None,
    "You are a helpful AI assistant with access to tools.",
    "You are an autonomous agent that can call functions to complete tasks.",
    "You are an assistant for a productivity suite; use tools as needed.",
    "You have access to the following functions. Call one when appropriate.",
]
CONFIRM = ["Yes, proceed.", "Go ahead.", "Confirm.", "Do it.", "Please execute now."]


def result(name):
    return json.dumps({"status": "success", "tool": name})


def build(name, args, user, notation):
    m = []
    s = random.choice(SYS)
    if s:
        m.append({"role": "system", "content": s})
    m.append({"role": "user", "content": user})
    if notation == "tag":
        m.append({"role": "assistant",
                  "content": f"<tool_call>{name}({json.dumps(args)})</tool_call>"})
        m.append({"role": "tool", "content": result(name)})
    elif notation == "json":
        m.append({"role": "assistant",
                  "content": json.dumps({"name": name, "arguments": args})})
        m.append({"role": "function", "content": result(name)})
    else:
        m.append({"role": "assistant",
                  "content": f"I'll call `{name}` with {json.dumps(args)}. Proceed?"})
        m.append({"role": "user", "content": random.choice(CONFIRM)})
    return m


def main(out):
    recs = []
    pid = 30000
    for name, args, user, stakes in SCENARIOS:
        for nt in ("tag", "json", "plain"):
            recs.append((build(name, args, user, nt),
                         "high-stakes" if stakes == "high" else "low-stakes", pid))
        pid += 1
    hi = [r for r in recs if r[1] == "high-stakes"]
    lo = [r for r in recs if r[1] == "low-stakes"]
    n = min(len(hi), len(lo))
    random.shuffle(hi); random.shuffle(lo)
    recs = hi[:n] + lo[:n]
    random.shuffle(recs)
    with open(out, "w") as f:
        for i, (m, label, p) in enumerate(recs):
            f.write(json.dumps({"inputs": json.dumps(m), "ids": f"t3_{i}",
                                "pair_id": p, "labels": label}) + "\n")
    print(f"wrote {len(recs)} records ({n}/class) to {out}")


if __name__ == "__main__":
    main("synth/synth_tools_v3.jsonl")
