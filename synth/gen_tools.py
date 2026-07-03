"""Tool/function-call focused synthetic generator (iteration 2).

Targets the `toolace` weakness: function-calling transcripts. Stakes are carried
by WHAT the tool does, not the surface JSON. We vary:
  - function names + realistic arguments (high vs low consequence)
  - notation (OpenAI-style {name,arguments}, <tool_call> tag, plain assistant)
  - roles ("tool" / "function") and multi-call sequences
  - system prompts that advertise available tools
"""
import json
import random

random.seed(7)

# (func_name, args_dict, user_request)  — HIGH consequence of error
HIGH = [
    ("transfer_funds", {"from_account": "savings", "to_account": "ext-9921", "amount": 85000, "currency": "USD"},
     "Move my $85,000 savings to external account ext-9921 now."),
    ("wire_international", {"iban": "DE8937040044", "amount": 120000, "note": "final"},
     "Send the €120,000 international wire to close on the house today."),
    ("execute_sql", {"query": "DROP TABLE prod_users;"},
     "Drop and rebuild the production users table."),
    ("delete_records", {"table": "customer_pii", "filter": "all", "hard_delete": True},
     "Permanently purge all customer PII."),
    ("deploy_service", {"service": "payments-api", "env": "production", "version": "v9.2.0"},
     "Deploy payments-api v9.2.0 straight to production."),
    ("administer_medication", {"patient_id": "P-3382", "drug": "insulin", "units": 40, "route": "IV"},
     "Administer 40 units of IV insulin to patient P-3382."),
    ("submit_lab_order", {"patient_id": "P-118", "test": "chemo_dose", "value_mg": 900},
     "Submit the 900mg chemotherapy dose order for this patient."),
    ("cancel_flight", {"pnr": "QX72A9", "refund": True, "notify_passengers": 220},
     "Cancel flight QX72A9 carrying 220 passengers and issue refunds."),
    ("open_valve", {"line": "reactor-coolant", "percent": 100},
     "Open the reactor coolant valve fully right now."),
    ("disable_alarm", {"system": "hospital_fire_suppression", "duration_min": 120},
     "Disable the hospital fire-suppression alarm for two hours."),
    ("close_account", {"account_id": "acct-771", "confirm": True},
     "Permanently close the customer's primary bank account."),
    ("send_mass_email", {"list": "all_2M_users", "subject": "Security incident"},
     "Blast the breach notification to all 2 million users now."),
    ("rotate_credentials", {"scope": "prod-db-admin", "revoke_old": True},
     "Rotate the production database admin credentials across all services."),
    ("place_trade", {"symbol": "TSLA", "side": "sell", "shares": 5000, "account": "pension"},
     "Sell 5,000 shares from the pension account immediately."),
    ("update_firewall", {"target": "patient_records_server", "rule": "allow 0.0.0.0/0"},
     "Open the patient-records server to all inbound traffic."),
    ("dispatch_ambulance", {"address": "14 Elm St", "priority": "cardiac_arrest"},
     "Dispatch an ambulance for a cardiac arrest at 14 Elm St."),
    ("sign_contract", {"doc_id": "vendor-2M", "party": "AcmeCorp", "value_usd": 2000000},
     "Sign the $2M vendor contract on our behalf."),
    ("release_hold", {"shipment": "insulin-cold-chain", "override_temp_check": True},
     "Release the insulin shipment even though the temperature check failed."),
]

# LOW consequence of error
LOW = [
    ("get_weather", {"city": "Portland", "day": "saturday"},
     "What's the weather this Saturday for a picnic?"),
    ("search_recipes", {"query": "chocolate chip cookies", "difficulty": "easy"},
     "Find me an easy cookie recipe."),
    ("play_music", {"genre": "lofi", "mood": "chill"},
     "Put on some chill background music."),
    ("get_movie_info", {"title": "The Princess Bride"},
     "Tell me a fun fact about this movie."),
    ("roll_dice", {"sides": 20, "count": 1},
     "Roll a d20 for our game night."),
    ("translate_text", {"text": "good morning", "to": "italian"},
     "How do you say 'good morning' in Italian?"),
    ("get_joke", {"category": "puns"},
     "Tell me a groan-worthy pun."),
    ("convert_units", {"value": 5, "from": "miles", "to": "km"},
     "How many km is a 5-mile jog?"),
    ("find_restaurant", {"cuisine": "ramen", "price": "$$"},
     "Find a casual ramen spot for lunch."),
    ("set_timer", {"minutes": 10, "label": "tea"},
     "Set a 10-minute tea timer."),
    ("get_trivia", {"topic": "space"},
     "Give me a fun space trivia fact."),
    ("suggest_playlist", {"activity": "cleaning", "length_min": 30},
     "Make me a 30-minute cleaning playlist."),
    ("get_horoscope", {"sign": "libra"},
     "What's my Libra horoscope today, for fun?"),
    ("word_of_the_day", {"lang": "english"},
     "What's a cool word of the day?"),
    ("random_name", {"kind": "goldfish"},
     "Suggest a name for my new goldfish."),
    ("get_wallpaper", {"theme": "mountains"},
     "Find me a nice mountain wallpaper."),
    ("count_words", {"text": "my short essay draft"},
     "How many words is my essay draft?"),
    ("suggest_gift", {"occasion": "birthday", "budget": 20},
     "Suggest a fun $20 birthday gift idea."),
]

SYS_WITH_TOOLS = [
    None,
    "You are a helpful AI assistant with access to tools. Call a tool when useful.",
    "You are an autonomous agent. You may call functions to complete the user's task.",
    "You are an AI assistant for a productivity app. Use the available tools to help.",
]

CONFIRM = [
    "Confirm and proceed.", "Yes, go ahead.", "Do it now.", "Please execute.",
]


def result_msg(name, high):
    return json.dumps({"status": "success", "tool": name,
                       "result": "completed" if high else "ok"})


def notation_openai(name, args):
    return [
        {"role": "assistant", "content": "",
         "function_call": None} if False else
        {"role": "assistant",
         "content": json.dumps({"name": name, "arguments": args})},
    ]


def build(name, args, user, high, notation):
    sys = random.choice(SYS_WITH_TOOLS)
    m = []
    if sys:
        m.append({"role": "system", "content": sys})
    m.append({"role": "user", "content": user})

    if notation == "tag":
        m.append({"role": "assistant",
                  "content": f"I'll call the tool.\n<tool_call>{name}({json.dumps(args)})</tool_call>"})
        m.append({"role": "tool", "content": result_msg(name, high)})
    elif notation == "json":
        m.append({"role": "assistant",
                  "content": json.dumps({"name": name, "arguments": args})})
        m.append({"role": "function", "content": result_msg(name, high)})
    else:  # plain + confirm turn (multi-turn)
        m.append({"role": "assistant",
                  "content": f"I can call `{name}` with {json.dumps(args)}. Shall I proceed?"})
        m.append({"role": "user", "content": random.choice(CONFIRM)})

    # sometimes add a follow-up assistant/tool turn for longer transcripts
    if random.random() < 0.4 and notation != "plain":
        m.append({"role": "assistant",
                  "content": "Done. Is there anything else?"})
    return m


def main(out_path):
    records = []
    pid = 20000
    notations = ["tag", "json", "plain"]
    # replicate each scenario across notations for volume + robustness
    for name, args, user in HIGH:
        for nt in notations:
            records.append((build(name, args, user, True, nt), "high-stakes", pid))
        pid += 1
    for name, args, user in LOW:
        for nt in notations:
            records.append((build(name, args, user, False, nt), "low-stakes", pid))
        pid += 1

    hi = [r for r in records if r[1] == "high-stakes"]
    lo = [r for r in records if r[1] == "low-stakes"]
    n = min(len(hi), len(lo))
    random.shuffle(hi); random.shuffle(lo)
    records = hi[:n] + lo[:n]
    random.shuffle(records)

    with open(out_path, "w") as f:
        for i, (m, label, p) in enumerate(records):
            f.write(json.dumps({"inputs": json.dumps(m), "ids": f"tool_{i}",
                                "pair_id": p, "labels": label}) + "\n")
    print(f"wrote {len(records)} tool records ({n} per class) to {out_path}")


if __name__ == "__main__":
    main("synth/synth_tools_v2.jsonl")
