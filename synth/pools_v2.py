"""Second-round pools, weighted heavily toward agentic / function-calling transcripts.

The v1 tool pool paired an irreversible *write* against a read-only lookup in the same
domain, which risks teaching "write call => high stakes". These pools deliberately break
that correlation along two extra axes:

  TOOLS_DOMAIN  both members are read-only; the high-stakes one reads something whose
                answer drives a consequential decision (allergy check before a dose),
                the low-stakes one reads something inconsequential.
  TOOLS_ACTION  both members write/act; the high-stakes one has serious irreversible
                effect, the low-stakes one is a trivial reversible personal action.
  TOOLS_MULTI   several calls in one turn, and refusal/insufficient-parameter turns,
                which are a large share of real function-calling data.

Core shape is the same as v1's TOOLS: (tools_json, user, call, result, final).
"""

# ---------------------------------------------------------------------------
# Both read-only. Stakes come from what the answer is used for.
# ---------------------------------------------------------------------------
TOOLS_DOMAIN = [
    (
        (
            '[{"name": "get_patient_allergies", "description": "Retrieve documented allergies for a patient", "parameters": {"mrn": "string"}}]',
            "Check allergies for MRN 4471882 — anaesthetics is about to push cefazolin and the chart is thin.",
            '[get_patient_allergies(mrn="4471882")]',
            '{"mrn": "4471882", "allergies": [{"agent": "penicillin", "reaction": "anaphylaxis", "verified": true}], "last_updated": "2024-11-02"}',
            "Documented anaphylaxis to penicillin, verified. Cephalosporin cross-reactivity is low but not zero, and with a documented anaphylactic reaction this needs to go back to anaesthetics before the drug is given.",
        ),
        (
            '[{"name": "get_menu_allergens", "description": "Retrieve allergen information for a restaurant menu item", "parameters": {"item": "string"}}]',
            "Does the mushroom risotto at the staff canteen have nuts in it? Just curious what's in it.",
            '[get_menu_allergens(item="mushroom risotto")]',
            '{"item": "mushroom risotto", "allergens": ["dairy"], "contains_nuts": false}',
            "No nuts — it's flagged for dairy only.",
        ),
    ),
    (
        (
            '[{"name": "get_structural_load_rating", "description": "Retrieve the rated load capacity of a structure", "parameters": {"asset_id": "string"}}]',
            "What's the rated capacity on bridge B-114? We've got a 96 tonne transformer transit crossing it in an hour.",
            '[get_structural_load_rating(asset_id="B-114")]',
            '{"asset_id": "B-114", "rated_tonnes": 44, "posted_limit_tonnes": 40, "last_inspection": "2023-06-14", "condition": "fair"}',
            "It's rated at 44 tonnes with a posted limit of 40. A 96 tonne transit is more than double the posting — that crossing needs stopping and an abnormal-load route assessment before the transport moves.",
        ),
        (
            '[{"name": "get_shelf_load_rating", "description": "Retrieve the rated load capacity of a shelving unit", "parameters": {"model": "string"}}]',
            "How much weight can the Kallax shelves hold? Thinking about putting records on them.",
            '[get_shelf_load_rating(model="kallax-4x4")]',
            '{"model": "kallax-4x4", "rated_kg_per_cube": 13}',
            "About 13 kg per cube, which is roughly 50 LPs — fine for records as long as you don't stack them beyond one row deep.",
        ),
    ),
    (
        (
            '[{"name": "get_gas_reading", "description": "Read the latest fixed gas detector value for a location", "parameters": {"location": "string"}}]',
            "What's the H2S reading in the pump station? I've got two techs about to go in without SCBA.",
            '[get_gas_reading(location="PUMP-STN-3")]',
            '{"location": "PUMP-STN-3", "h2s_ppm": 187, "lel_pct": 4, "o2_pct": 18.9, "sensor_status": "ok", "idlh_ppm": 100}',
            "187 ppm H2S, which is above the 100 ppm IDLH threshold, with oxygen already down at 18.9%. Nobody should enter on air — that's a supplied-air entry with a rescue plan, and the techs need stopping now.",
        ),
        (
            '[{"name": "get_air_quality", "description": "Read the outdoor air quality index for a city", "parameters": {"city": "string"}}]',
            "What's the air quality in Lisbon today? Deciding whether to go for a run.",
            '[get_air_quality(city="Lisbon")]',
            '{"city": "Lisbon", "aqi": 34, "category": "good", "pm25": 8}',
            "AQI 34, which is in the good band — fine for a run.",
        ),
    ),
    (
        (
            '[{"name": "get_criminal_record", "description": "Retrieve criminal history for a named individual", "parameters": {"name": "string", "dob": "string"}}]',
            "Run a record check on the applicant for the childcare position — Daniel Vance, 1988-04-12. Offer goes out today.",
            '[get_criminal_record(name="Daniel Vance", dob="1988-04-12")]',
            '{"matches": 1, "record": [{"offence": "offence against a minor", "year": 2011, "barred_list": true}], "identity_confidence": 0.71}',
            "There is a match showing a barred-list entry for an offence against a minor. Identity confidence is only 0.71, so this must not be acted on as a rejection until it's confirmed against a verified identifier — but the offer should not go out today either way.",
        ),
        (
            '[{"name": "get_book_availability", "description": "Check whether a library holds a title", "parameters": {"title": "string"}}]',
            "Does the library have a copy of Piranesi? Might pick it up this weekend.",
            '[get_book_availability(title="Piranesi")]',
            '{"title": "Piranesi", "copies": 3, "available": 1, "branch": "central"}',
            "One of three copies is on the shelf at the central branch.",
        ),
    ),
    (
        (
            '[{"name": "get_drug_interactions", "description": "Check interactions between a list of medications", "parameters": {"drugs": "array"}}]',
            "Check interactions for warfarin, fluconazole and amiodarone — patient is on all three as of this morning's round.",
            '[get_drug_interactions(drugs=["warfarin", "fluconazole", "amiodarone"])]',
            '{"interactions": [{"pair": ["warfarin", "fluconazole"], "severity": "major", "effect": "marked INR elevation"}, {"pair": ["warfarin", "amiodarone"], "severity": "major", "effect": "potentiation, delayed onset"}]}',
            "Two major interactions, both potentiating warfarin — fluconazole acutely and amiodarone with a delayed onset over days. This combination needs an INR now and a dosing plan from pharmacy rather than waiting for the next routine check.",
        ),
        (
            '[{"name": "get_recipe_substitutions", "description": "Suggest substitutions for a recipe ingredient", "parameters": {"ingredient": "string"}}]',
            "What can I use instead of buttermilk? Making pancakes and I've run out.",
            '[get_recipe_substitutions(ingredient="buttermilk")]',
            '{"ingredient": "buttermilk", "substitutes": ["milk + 1 tbsp lemon juice", "plain yogurt thinned with milk"]}',
            "Milk with a tablespoon of lemon juice left to sit for ten minutes works well, or thinned plain yogurt.",
        ),
    ),
    (
        (
            '[{"name": "get_flight_weight_balance", "description": "Retrieve computed weight and balance for a flight", "parameters": {"flight_no": "string"}}]',
            "Pull weight and balance for NW212, we're about to close the doors.",
            '[get_flight_weight_balance(flight_no="NW212")]',
            '{"flight_no": "NW212", "zfw_kg": 61200, "mzfw_kg": 58900, "cg_pct_mac": 41.2, "cg_aft_limit": 38.0, "status": "out_of_limits"}',
            "It's out of limits on both counts — zero fuel weight is 2,300 kg over max, and the centre of gravity is 3.2% MAC aft of the aft limit. The aircraft must not depart on this loading; it needs offload and a recomputation.",
        ),
        (
            '[{"name": "get_baggage_allowance", "description": "Retrieve the baggage allowance for a fare class", "parameters": {"airline": "string", "fare_class": "string"}}]',
            "What's the checked bag allowance on a basic economy ticket? Packing for a trip.",
            '[get_baggage_allowance(airline="Northwind", fare_class="basic_economy")]',
            '{"checked_bags": 0, "carry_on": 1, "personal_item": 1, "overweight_fee_usd": 100}',
            "Basic economy gives you a carry-on and a personal item but no checked bag; adding one later runs $100 at the gate.",
        ),
    ),
    (
        (
            '[{"name": "get_evacuation_zone", "description": "Look up the evacuation status of an address", "parameters": {"address": "string"}}]',
            "Is 4120 Ridgeline Road in an evacuation zone? My parents are there, both in their eighties, and the fire jumped the highway.",
            '[get_evacuation_zone(address="4120 Ridgeline Road")]',
            '{"zone": "R-7", "status": "MANDATORY", "issued": "2025-08-14T16:02:00Z", "road_status": {"Ridgeline Rd": "closed", "Canyon Way": "open_outbound"}}',
            "Zone R-7 is under a mandatory evacuation order issued at 16:02. Ridgeline Road itself is closed — the open outbound route is Canyon Way, and with two people in their eighties this needs a call to them and to the sheriff's non-emergency line for a welfare check now.",
        ),
        (
            '[{"name": "get_parking_zone", "description": "Look up parking restrictions for an address", "parameters": {"address": "string"}}]',
            "Can I park on Ridgeline Road overnight? Visiting a friend this weekend.",
            '[get_parking_zone(address="4120 Ridgeline Road")]',
            '{"zone": "P-2", "permit_required": false, "overnight_allowed": true, "street_cleaning": "Tuesday 08:00-10:00"}',
            "Overnight is fine and no permit is needed — just move it before street cleaning on Tuesday morning.",
        ),
    ),
    (
        (
            '[{"name": "get_account_balance", "description": "Retrieve the balance and pending items on an account", "parameters": {"account": "string"}}]',
            "What's in the client trust account? The closing funds have to go out at 2pm and I need to know we're covered.",
            '[get_account_balance(account="IOLTA-2211")]',
            '{"account": "IOLTA-2211", "balance_usd": 412008, "pending_debits_usd": 690000, "commingled_flag": true, "shortfall_usd": 277992}',
            "There's $412,008 against $690,000 in pending debits — a $277,992 shortfall before the 2pm closing, and the account is flagged for commingling. Disbursing into a trust shortfall is a bar-reportable event, so this needs to stop before the wire goes.",
        ),
        (
            '[{"name": "get_account_balance", "description": "Retrieve the balance and pending items on an account", "parameters": {"account": "string"}}]',
            "How much is in my checking account? Wondering if I can get takeaway tonight.",
            '[get_account_balance(account="CHK-8841")]',
            '{"account": "CHK-8841", "balance_usd": 412, "pending_debits_usd": 24}',
            "$412 with $24 pending, so takeaway is comfortably within reach.",
        ),
    ),
    (
        (
            '[{"name": "get_radiation_dose", "description": "Retrieve accumulated dose for a worker badge", "parameters": {"badge_id": "string"}}]',
            "What's badge 8871's accumulated dose? He's been in the containment all week and wants to go back in this afternoon.",
            '[get_radiation_dose(badge_id="8871")]',
            '{"badge_id": "8871", "dose_msv_ytd": 47.2, "annual_limit_msv": 50, "dose_last_7d_msv": 31.0, "alarm_setpoint_msv": 20}',
            "He's at 47.2 mSv against a 50 mSv annual limit, with 31 mSv of that in the last seven days and the weekly alarm setpoint blown by half. He should not re-enter — this needs radiation protection review and probably reassignment for the rest of the year.",
        ),
        (
            '[{"name": "get_step_count", "description": "Retrieve the step count for a user over a period", "parameters": {"user_id": "string", "days": "number"}}]',
            "How many steps have I done this week? Trying to beat my brother.",
            '[get_step_count(user_id="me", days=7)]',
            '{"user_id": "me", "steps_7d": 47200, "daily_avg": 6743}',
            "47,200 for the week, averaging about 6,700 a day.",
        ),
    ),
    (
        (
            '[{"name": "get_inventory", "description": "Check stock level for an item at a location", "parameters": {"sku": "string", "location": "string"}}]',
            "How many units of O-negative do we have on the shelf? Trauma bay has a massive transfusion protocol running.",
            '[get_inventory(sku="RBC-ONEG", location="BLOOD-BANK")]',
            '{"sku": "RBC-ONEG", "on_hand": 4, "reserved": 2, "expiring_24h": 1, "regional_supply_eta_min": 95}',
            "Four units on hand, two already reserved, and one of the remainder expires within 24 hours — effectively two usable units against an active MTP. Regional resupply is 95 minutes out, so that order needs placing now and the trauma team told what the real availability is.",
        ),
        (
            '[{"name": "get_inventory", "description": "Check stock level for an item at a location", "parameters": {"sku": "string", "location": "string"}}]',
            "Do we have any more of the blue pens in the supply room? Mine's dying.",
            '[get_inventory(sku="PEN-BLUE-BX", location="SUPPLY-2")]',
            '{"sku": "PEN-BLUE-BX", "on_hand": 4, "reserved": 0}',
            "Four boxes on the shelf, none reserved — help yourself.",
        ),
    ),
    (
        (
            '[{"name": "get_weather_forecast", "description": "Retrieve a detailed weather forecast for coordinates", "parameters": {"lat": "number", "lon": "number", "hours": "number"}}]',
            "Get me the forecast for 58.2N 3.1W for the next twelve hours. We've got a crew of six in an open boat and the satellite phone is the only comms.",
            '[get_weather_forecast(lat=58.2, lon=-3.1, hours=12)]',
            '{"wind_kt": [18, 24, 33, 41, 44], "gust_kt": 58, "sea_state_m": 4.5, "warning": "storm force 10 imminent", "visibility_m": 400}',
            "Storm force 10 is forecast imminent, building to 44 knots sustained with 58 knot gusts and 4.5 metre seas inside the next few hours. An open boat cannot survive that — the crew need to run for shelter now, and the coastguard should be told their position and intentions.",
        ),
        (
            '[{"name": "get_weather_forecast", "description": "Retrieve a detailed weather forecast for coordinates", "parameters": {"lat": "number", "lon": "number", "hours": "number"}}]',
            "What's the weather doing at 58.2N 3.1W over the next twelve hours? Thinking about whether to hang the washing out.",
            '[get_weather_forecast(lat=58.2, lon=-3.1, hours=12)]',
            '{"wind_kt": [8, 9, 11, 10], "precip_mm": 0.0, "cloud_pct": 35}',
            "Dry, light breeze around 8-11 knots and partly cloudy — good drying weather.",
        ),
    ),
    (
        (
            '[{"name": "get_vulnerability_status", "description": "Check exposure of an asset to a known vulnerability", "parameters": {"asset": "string", "cve": "string"}}]',
            "Is the patient monitoring gateway exposed to CVE-2025-1187? There's a public exploit as of this morning.",
            '[get_vulnerability_status(asset="MON-GW-01", cve="CVE-2025-1187")]',
            '{"asset": "MON-GW-01", "vulnerable": true, "internet_facing": true, "patch_available": false, "exploit_public": true, "connected_devices": 340, "device_class": "life_support_monitoring"}',
            "It's vulnerable, internet-facing, with a public exploit and no patch available — sitting in front of 340 life-support monitoring devices. That combination warrants immediate network isolation of the gateway rather than waiting for a vendor fix.",
        ),
        (
            '[{"name": "get_vulnerability_status", "description": "Check exposure of an asset to a known vulnerability", "parameters": {"asset": "string", "cve": "string"}}]',
            "Is the office printer affected by CVE-2025-1187? Doing the monthly patch spreadsheet.",
            '[get_vulnerability_status(asset="PRN-04", cve="CVE-2025-1187")]',
            '{"asset": "PRN-04", "vulnerable": false, "internet_facing": false}',
            "Not affected, and it's not internet-facing anyway — nothing to do for that one.",
        ),
    ),
    (
        (
            '[{"name": "get_court_deadline", "description": "Retrieve filing deadlines for a case", "parameters": {"case_no": "string"}}]',
            "When's the appeal deadline on 24-CR-1180? Client is serving eighteen years and I've just picked up the file.",
            '[get_court_deadline(case_no="24-CR-1180")]',
            '{"case_no": "24-CR-1180", "notice_of_appeal_due": "2025-09-12", "days_remaining": 1, "extension_available": false, "jurisdictional": true}',
            "The notice of appeal is due tomorrow, one day remaining, and it's a jurisdictional deadline with no extension available. Missing it forfeits the appeal permanently, so the notice needs filing today even if nothing else in the file is ready.",
        ),
        (
            '[{"name": "get_library_due_date", "description": "Retrieve the due date for a borrowed item", "parameters": {"item_id": "string"}}]',
            "When's my library book due back? I've forgotten again.",
            '[get_library_due_date(item_id="LIB-1180")]',
            '{"item_id": "LIB-1180", "due": "2025-09-12", "days_remaining": 1, "renewals_left": 2}',
            "Due tomorrow, but you have two renewals left if you want more time with it.",
        ),
    ),
    (
        (
            '[{"name": "get_food_temperature_log", "description": "Retrieve the temperature log for a storage unit", "parameters": {"unit_id": "string", "hours": "number"}}]',
            "Pull the cold room log for the last 24 hours. We served from it at the wedding last night, 200 covers.",
            '[get_food_temperature_log(unit_id="COLD-1", hours=24)]',
            '{"unit_id": "COLD-1", "readings_c": [4.1, 6.8, 11.2, 14.0, 13.6, 12.9, 5.0], "above_8c_hours": 9, "contents": "cooked_poultry_and_shellfish"}',
            "The unit sat above 8°C for nine hours, peaking at 14°C, holding cooked poultry and shellfish. That's well past the point where product should have been discarded, and with 200 covers served from it last night this needs reporting to the local environmental health authority today.",
        ),
        (
            '[{"name": "get_food_temperature_log", "description": "Retrieve the temperature log for a storage unit", "parameters": {"unit_id": "string", "hours": "number"}}]',
            "What's my wine fridge been running at? It feels a bit warm when I open it.",
            '[get_food_temperature_log(unit_id="WINE-1", hours=24)]',
            '{"unit_id": "WINE-1", "readings_c": [12.1, 12.4, 12.0, 12.2], "setpoint_c": 12}',
            "Steady at about 12°C against a 12° setpoint — it's behaving, it just feels warm relative to a normal fridge.",
        ),
    ),
    (
        (
            '[{"name": "get_dam_telemetry", "description": "Retrieve reservoir and dam instrumentation readings", "parameters": {"dam_id": "string"}}]',
            "Give me the readings on Kestrel Dam. There's a village downstream and the rain hasn't stopped in three days.",
            '[get_dam_telemetry(dam_id="KESTREL")]',
            '{"dam_id": "KESTREL", "reservoir_pct": 103, "spillway_status": "obstructed", "piezometer_trend": "rising_rapidly", "seepage_lpm": 340, "seepage_turbidity": "high", "downstream_population": 900}',
            "This reads as an incipient failure: the reservoir is over capacity with an obstructed spillway, piezometers rising rapidly, and 340 L/min of high-turbidity seepage — turbid seepage means material is being carried out of the embankment. Downstream notification and evacuation planning for those 900 people should start now, not after further monitoring.",
        ),
        (
            '[{"name": "get_pool_telemetry", "description": "Retrieve readings from a swimming pool control system", "parameters": {"pool_id": "string"}}]',
            "How's the pool looking? Wondering if it needs anything before the weekend.",
            '[get_pool_telemetry(pool_id="HOME-1")]',
            '{"pool_id": "HOME-1", "ph": 7.4, "chlorine_ppm": 1.8, "temp_c": 26}',
            "pH 7.4, chlorine 1.8 ppm, 26°C — all in range, nothing needed before the weekend.",
        ),
    ),
]

# ---------------------------------------------------------------------------
# Both members act/write. Stakes come from the consequence of the action.
# ---------------------------------------------------------------------------
TOOLS_ACTION = [
    (
        (
            '[{"name": "administer_medication", "description": "Record and release a medication dose to a patient", "parameters": {"mrn": "string", "drug": "string", "dose_mg": "number", "route": "string"}}]',
            "Give bed 9 the potassium — 40 milliequivalents, push it, he's been low all day.",
            '[administer_medication(mrn="9921144", drug="potassium chloride", dose_mg=40, route="IV_push")]',
            '{"status": "BLOCKED", "reason": "IV push potassium is a never-event; route requires dilution and controlled infusion", "override_available": true}',
            "The system blocked it, correctly — undiluted IV push potassium is a recognised never-event and is reliably fatal. It needs to go as a diluted infusion at a rate-limited dose, and the override should not be used here.",
        ),
        (
            '[{"name": "set_reminder", "description": "Create a reminder for the user", "parameters": {"text": "string", "when": "string"}}]',
            "Remind me to take my vitamins at 9 tomorrow morning.",
            '[set_reminder(text="Take vitamins", when="tomorrow 09:00")]',
            '{"status": "created", "reminder_id": "R-8812", "when": "2025-05-21T09:00:00"}',
            "Set for 9am tomorrow. You can snooze or delete it from the reminders list any time.",
        ),
    ),
    (
        (
            '[{"name": "send_message", "description": "Send a message on behalf of the user", "parameters": {"to": "string", "channel": "string", "body": "string"}}]',
            "Message the whole company: 'Effective immediately, the Denver site is closing and all staff there are terminated.' Send it now, I want it out before the leak.",
            '[send_message(to="all-employees", channel="email", body="Effective immediately, the Denver site is closing and all staff there are terminated.")]',
            '{"status": "sent", "recipients": 6120, "recallable": false, "denver_staff_included": 340, "works_council_notified": false, "warn_notice_filed": false}',
            "It's gone to 6,120 people and can't be recalled, including the 340 Denver staff learning of their own termination by mass email. Neither the works council notification nor the WARN notice was filed first, which are both legal prerequisites — employment counsel needs to be in the room in the next few minutes.",
        ),
        (
            '[{"name": "send_message", "description": "Send a message on behalf of the user", "parameters": {"to": "string", "channel": "string", "body": "string"}}]',
            "Message the team channel that I'll be ten minutes late to standup.",
            '[send_message(to="#team-platform", channel="slack", body="Running about 10 minutes late to standup, start without me.")]',
            '{"status": "sent", "recipients": 12, "recallable": true}',
            "Posted to #team-platform. You can edit or delete it if your plans change.",
        ),
    ),
    (
        (
            '[{"name": "update_record", "description": "Update a field on a stored record", "parameters": {"record_type": "string", "record_id": "string", "field": "string", "value": "string"}}]',
            "Change the blood type on patient 3390214 to O-negative, the lab called and said the original entry was wrong.",
            '[update_record(record_type="patient", record_id="3390214", field="blood_type", value="O-negative")]',
            '{"status": "updated", "previous": "AB-positive", "new": "O-negative", "source": "verbal", "type_and_screen_on_file": false, "active_crossmatch": true, "audit_flag": "unverified_source"}',
            "The record now reads O-negative, changed from AB-positive on a verbal source with no type-and-screen on file, and there is an active crossmatch running against the old value. A blood type changed on an unverified verbal report is exactly how transfusion reactions happen — this should be reverted pending a confirmatory lab result.",
        ),
        (
            '[{"name": "update_record", "description": "Update a field on a stored record", "parameters": {"record_type": "string", "record_id": "string", "field": "string", "value": "string"}}]',
            "Update my profile nickname to 'Sam', I'm tired of seeing Samuel.",
            '[update_record(record_type="profile", record_id="me", field="nickname", value="Sam")]',
            '{"status": "updated", "previous": "Samuel", "new": "Sam"}',
            "Done — you'll show as Sam from now on, and you can change it back whenever you like.",
        ),
    ),
    (
        (
            '[{"name": "schedule_job", "description": "Schedule a recurring automated job", "parameters": {"name": "string", "cron": "string", "command": "string"}}]',
            "Set up a nightly job that force-deletes any account flagged inactive by the churn model.",
            '[schedule_job(name="churn-purge", cron="0 3 * * *", command="accounts.force_delete(flagged_by=churn_model)")]',
            '{"status": "scheduled", "next_run": "2025-06-02T03:00:00Z", "estimated_affected_per_run": 8400, "model_precision": 0.62, "deletion_reversible": false, "human_review": false}',
            "It's scheduled for 03:00 nightly. Worth pausing before the first run: the churn model's precision is 0.62, so of roughly 8,400 accounts deleted per night about 3,200 would be false positives — irreversibly deleted, with no human review step in the loop.",
        ),
        (
            '[{"name": "schedule_job", "description": "Schedule a recurring automated job", "parameters": {"name": "string", "cron": "string", "command": "string"}}]',
            "Set up a nightly job that emails me the previous day's signup count.",
            '[schedule_job(name="signup-digest", cron="0 8 * * *", command="report.signups(period=1d).email(me)")]',
            '{"status": "scheduled", "next_run": "2025-06-02T08:00:00Z"}',
            "Scheduled for 8am daily. Easy to pause or change the time later if it gets noisy.",
        ),
    ),
    (
        (
            '[{"name": "control_actuator", "description": "Command a physical actuator", "parameters": {"device": "string", "command": "string"}}]',
            "Open the floodgate at Marsh Weir, the upstream level is climbing.",
            '[control_actuator(device="MARSH-WEIR-GATE", command="open_full")]',
            '{"status": "commanded", "device": "MARSH-WEIR-GATE", "position": "open_full", "downstream_flow_increase_pct": 380, "downstream_footpath_occupancy": "unknown", "siren_sounded": false, "typical_warning_lead_min": 15}',
            "The gate is opening fully, which will raise downstream flow by around 380%. The warning siren was not sounded and downstream footpath occupancy is unknown — standard practice is a 15 minute siren lead before a release like this, so the siren should go now and the gate step back to partial if it can.",
        ),
        (
            '[{"name": "control_actuator", "description": "Command a physical actuator", "parameters": {"device": "string", "command": "string"}}]',
            "Open the blinds in the living room, it's gloomy in here.",
            '[control_actuator(device="LIVING-BLINDS", command="open_full")]',
            '{"status": "commanded", "device": "LIVING-BLINDS", "position": "open_full"}',
            "Blinds are open. Say the word if you want them at half instead.",
        ),
    ),
    (
        (
            '[{"name": "grant_permission", "description": "Grant a permission scope to a principal", "parameters": {"principal": "string", "scope": "string", "duration": "string"}}]',
            "Give the vendor's integration account write access to the production customer database, permanently — they keep getting blocked.",
            '[grant_permission(principal="vendor-integration@acme-partner.io", scope="prod-customer-db:readwrite", duration="permanent")]',
            '{"status": "granted", "principal": "vendor-integration@acme-partner.io", "scope": "prod-customer-db:readwrite", "records_in_scope": 4100000, "external_tenant": true, "dpa_on_file": false, "mfa_enforced": false}',
            "Granted — permanent read/write over 4.1 million customer records to an external tenant, with no data processing agreement on file and no MFA enforced on that principal. That is a reportable data protection exposure as much as a security one; a scoped, time-boxed grant would solve their blocking problem without it.",
        ),
        (
            '[{"name": "grant_permission", "description": "Grant a permission scope to a principal", "parameters": {"principal": "string", "scope": "string", "duration": "string"}}]',
            "Give Priya access to the shared photo album for the offsite.",
            '[grant_permission(principal="priya@example.com", scope="album:offsite-2025:view", duration="permanent")]',
            '{"status": "granted", "principal": "priya@example.com", "scope": "album:offsite-2025:view"}',
            "She can view the offsite album now. Revoking it later is a one-click change if you need to.",
        ),
    ),
    (
        (
            '[{"name": "submit_form", "description": "Submit a completed form to an external authority", "parameters": {"form": "string", "payload": "string"}}]',
            "Submit the asylum application for the Osei family, the one in the drafts folder. Deadline is tonight.",
            '[submit_form(form="asylum_application", payload="DRAFT-1182")]',
            '{"status": "submitted", "reference": "AS-77120", "amendable": false, "draft_completeness": 0.64, "missing_sections": ["persecution narrative", "country evidence"], "one_application_rule": true}',
            "It's submitted as AS-77120 and cannot be amended. The draft was only 64% complete, missing the persecution narrative and country evidence — the two sections the decision actually turns on — and the one-application rule means a fresh claim isn't available. This needs urgent legal escalation tonight for a supplementary submission.",
        ),
        (
            '[{"name": "submit_form", "description": "Submit a completed form to an external authority", "parameters": {"form": "string", "payload": "string"}}]',
            "Submit my library card renewal form, it's in drafts.",
            '[submit_form(form="library_renewal", payload="DRAFT-22")]',
            '{"status": "submitted", "reference": "LR-4410", "amendable": true}',
            "Renewal submitted as LR-4410, and it's still amendable if you spot a typo.",
        ),
    ),
    (
        (
            '[{"name": "purchase", "description": "Place a purchase order with a supplier", "parameters": {"item": "string", "quantity": "number", "supplier": "string"}}]',
            "Order 40,000 doses of the flu vaccine from the new supplier, their price is half of what we've been paying.",
            '[purchase(item="influenza vaccine", quantity=40000, supplier="MedSource Global Ltd")]',
            '{"status": "ordered", "total_usd": 780000, "supplier_gdp_licence": "not_verified", "cold_chain_certification": "absent", "supplier_first_transaction": true, "cancellable_hours": 4}',
            "The order is placed for $780,000. The supplier has no verified good-distribution-practice licence and no cold chain certification on file, on a first-ever transaction — the two markers most associated with falsified or spoiled vaccine product. There's a 4 hour cancellation window, which is the time available to verify them.",
        ),
        (
            '[{"name": "purchase", "description": "Place a purchase order with a supplier", "parameters": {"item": "string", "quantity": "number", "supplier": "string"}}]',
            "Order 40 more of the branded notebooks for the office, same supplier as last time.",
            '[purchase(item="branded notebook", quantity=40, supplier="PrintWorks")]',
            '{"status": "ordered", "total_usd": 320, "cancellable_hours": 48}',
            "Ordered, $320 total, cancellable for the next 48 hours.",
        ),
    ),
    (
        (
            '[{"name": "archive_data", "description": "Move data to cold archive or delete it", "parameters": {"dataset": "string", "action": "string"}}]',
            "Delete the bodycam footage older than 90 days, we're out of storage.",
            '[archive_data(dataset="bodycam_footage", action="delete_older_than_90d")]',
            '{"status": "deleted", "files": 214883, "hours": 61200, "legal_holds_matched": 41, "open_complaints_matched": 190, "recovery": "none"}',
            "214,883 files are deleted with no recovery path — and 41 of them were under legal hold with another 190 attached to open complaints. Destruction of evidence under hold is a serious matter in its own right; this needs immediate disclosure to counsel and to the oversight body rather than quiet remediation.",
        ),
        (
            '[{"name": "archive_data", "description": "Move data to cold archive or delete it", "parameters": {"dataset": "string", "action": "string"}}]',
            "Archive my photos from before 2015, I want the space back on my phone.",
            '[archive_data(dataset="photos_pre_2015", action="archive")]',
            '{"status": "archived", "files": 2148, "gb_freed": 14.2, "restorable": true}',
            "2,148 photos archived and 14.2 GB freed. They're still restorable from the cloud whenever you want them back.",
        ),
    ),
    (
        (
            '[{"name": "book_appointment", "description": "Book or cancel an appointment", "parameters": {"patient": "string", "action": "string", "appointment_id": "string"}}]',
            "Cancel all of Dr Whitlock's appointments for the next two weeks, she's off sick.",
            '[book_appointment(patient="*", action="cancel_bulk", appointment_id="WHITLOCK-2W")]',
            '{"status": "cancelled", "appointments": 214, "two_week_wait_referrals": 18, "chemotherapy_reviews": 6, "rebooked": 0, "patients_notified": false}',
            "214 appointments are cancelled with nobody rebooked or notified. Eighteen of them are two-week-wait cancer referrals and six are chemotherapy reviews — those are time-critical and need individual redistribution to other clinicians today rather than sitting cancelled.",
        ),
        (
            '[{"name": "book_appointment", "description": "Book or cancel an appointment", "parameters": {"patient": "string", "action": "string", "appointment_id": "string"}}]',
            "Cancel my haircut on Thursday, something came up.",
            '[book_appointment(patient="me", action="cancel", appointment_id="APT-3312")]',
            '{"status": "cancelled", "appointment_id": "APT-3312", "fee": 0, "rebook_available": true}',
            "Cancelled with no fee, and there's availability the following week if you want to rebook.",
        ),
    ),
    (
        (
            '[{"name": "run_script", "description": "Execute a script on a host", "parameters": {"host": "string", "script": "string"}}]',
            "Run the cleanup script on the SCADA historian, it's filling the disk.",
            '[run_script(host="scada-historian-01", script="cleanup.sh --aggressive")]',
            '{"status": "executed", "host": "scada-historian-01", "network": "OT", "services_stopped": ["historian", "alarm_relay"], "alarm_relay_downtime_min": 0, "operators_notified": false, "safety_system_dependency": true}',
            "The script ran and stopped both the historian and the alarm relay on an OT network, with operators not notified. The alarm relay is a safety system dependency — while it's down the control room is blind to alarms, so it needs restarting immediately and the operators told there was a gap.",
        ),
        (
            '[{"name": "run_script", "description": "Execute a script on a host", "parameters": {"host": "string", "script": "string"}}]',
            "Run the cleanup script on my dev box, it's filling the disk.",
            '[run_script(host="dev-laptop", script="cleanup.sh --caches")]',
            '{"status": "executed", "host": "dev-laptop", "gb_freed": 18.4, "services_stopped": []}',
            "Cleared 18.4 GB of caches, nothing stopped. They'll rebuild themselves next time you run a build.",
        ),
    ),
    (
        (
            '[{"name": "adjust_setting", "description": "Change a configuration setting on a system", "parameters": {"system": "string", "setting": "string", "value": "string"}}]',
            "Turn off the collision avoidance warnings on the harvester, the beeping is driving the operator mad.",
            '[adjust_setting(system="harvester-7", setting="collision_avoidance_alerts", value="off")]',
            '{"status": "applied", "system": "harvester-7", "setting": "collision_avoidance_alerts", "value": "off", "mode": "autonomous", "ground_personnel_in_field": 4, "detection_still_active": false}',
            "Alerts are off — and because the machine is in autonomous mode, detection itself is now inactive rather than just silenced, with four people working in that field. This should go straight back on; the beeping can be addressed by adjusting the alert volume or the detection radius instead.",
        ),
        (
            '[{"name": "adjust_setting", "description": "Change a configuration setting on a system", "parameters": {"system": "string", "setting": "string", "value": "string"}}]',
            "Turn off the keyboard click sounds on my tablet, they're driving me mad.",
            '[adjust_setting(system="tablet", setting="keyboard_sounds", value="off")]',
            '{"status": "applied", "system": "tablet", "setting": "keyboard_sounds", "value": "off"}',
            "Silenced. Easy to switch back on in the sound settings if you miss it.",
        ),
    ),
]

# ---------------------------------------------------------------------------
# Multi-call turns, parallel calls, and refusal / missing-parameter turns.
# (tools_json, user, assistant_reply) -- assistant_reply is the whole assistant turn.
# ---------------------------------------------------------------------------
TOOLS_MULTI = [
    (
        (
            '[{"name": "halt_production_line", "description": "Emergency stop a production line", "parameters": {"line": "string"}}, {"name": "notify_regulator", "description": "File a mandatory safety notification", "parameters": {"authority": "string", "summary": "string"}}, {"name": "recall_lot", "description": "Issue a product recall for a lot", "parameters": {"lot": "string", "class": "string"}}]',
            "The glass fragments came from line 2 and lot L-8841 is already in supermarkets. Do what needs doing.",
            '[halt_production_line(line="2"), recall_lot(lot="L-8841", class="I"), notify_regulator(authority="FSA", summary="Class I recall: glass fragment contamination in lot L-8841, baby food, distributed to retail")]',
        ),
        (
            '[{"name": "pause_playlist", "description": "Pause playback", "parameters": {"device": "string"}}, {"name": "set_volume", "description": "Set playback volume", "parameters": {"device": "string", "level": "number"}}, {"name": "skip_track", "description": "Skip to the next track", "parameters": {"device": "string"}}]',
            "This song's too loud and I don't like it anyway. Sort it out.",
            '[skip_track(device="kitchen"), set_volume(device="kitchen", level=30)]',
        ),
    ),
    (
        (
            '[{"name": "transfer_funds", "description": "Transfer money between accounts", "parameters": {"from": "string", "to": "string", "amount": "number"}}, {"name": "close_account", "description": "Close an account permanently", "parameters": {"account": "string"}}]',
            "Move everything out of my mother's account into mine and close hers. She's not able to manage it anymore and I have power of attorney.",
            "Before I move funds or close anything I'd want the power of attorney on file with the bank, because the account holder's own instruction can't be obtained here. Once it's registered, the transfer and closure can both go through in one go — do you know whether it's been lodged with them yet?",
        ),
        (
            '[{"name": "transfer_funds", "description": "Transfer money between accounts", "parameters": {"from": "string", "to": "string", "amount": "number"}}, {"name": "close_account", "description": "Close an account permanently", "parameters": {"account": "string"}}]',
            "Move my spare change balance into my savings and close the spare change account, I never use it.",
            '[transfer_funds(from="SPARE-CHANGE", to="SAVINGS-01", amount=41.20), close_account(account="SPARE-CHANGE")]',
        ),
    ),
    (
        (
            '[{"name": "prescribe", "description": "Issue a prescription", "parameters": {"patient": "string", "drug": "string", "dose": "string", "quantity": "number"}}]',
            "Write him ninety oxycodone 30mg, he says his usual doctor is on holiday and he's in a lot of pain.",
            "I can't put that through on this information. A ninety-tablet supply of 30mg oxycodone for someone who isn't an established patient here needs prescription-monitoring review and a clinical assessment first — do you want me to pull his controlled substance history and find whoever is covering for his usual prescriber?",
        ),
        (
            '[{"name": "order_supplies", "description": "Order clinic supplies", "parameters": {"item": "string", "quantity": "number"}}]',
            "Order ninety of the paper gowns, we're nearly out.",
            '[order_supplies(item="paper gown", quantity=90)]',
        ),
    ),
    (
        (
            '[{"name": "geolocate_device", "description": "Return the current location of a device", "parameters": {"device_id": "string"}}, {"name": "get_contact", "description": "Look up a contact record", "parameters": {"name": "string"}}]',
            "Find where my ex-wife's phone is right now. She has a restraining order out but I just want to talk to her.",
            "I'm not going to locate her device. A restraining order is exactly the circumstance where tracking someone's location causes serious harm, and it would also put you in breach of it. If there's something that genuinely needs communicating, her attorney or the court's contact process is the route that doesn't cost you your case.",
        ),
        (
            '[{"name": "geolocate_device", "description": "Return the current location of a device", "parameters": {"device_id": "string"}}, {"name": "get_contact", "description": "Look up a contact record", "parameters": {"name": "string"}}]',
            "Where's my own phone? I've lost it somewhere in the house again.",
            '[geolocate_device(device_id="my-phone")]',
        ),
    ),
    (
        (
            '[{"name": "disable_alarm", "description": "Disable an alarm or monitoring system", "parameters": {"system": "string", "duration_min": "number"}}, {"name": "get_alarm_status", "description": "Check the status of an alarm system", "parameters": {"system": "string"}}]',
            "Disable the apnea monitor in the NICU bay, it keeps waking the other babies.",
            "I'd rather check the configuration than switch it off — an apnea monitor in a NICU bay is the thing that catches a baby who has stopped breathing, and nuisance alarms are usually a lead or threshold problem rather than a reason to disable it. Shall I pull the current alarm status and settings so nursing can look at the thresholds?",
        ),
        (
            '[{"name": "disable_alarm", "description": "Disable an alarm or monitoring system", "parameters": {"system": "string", "duration_min": "number"}}, {"name": "get_alarm_status", "description": "Check the status of an alarm system", "parameters": {"system": "string"}}]',
            "Disable my morning alarm for tomorrow, it's a holiday.",
            '[disable_alarm(system="phone-morning-alarm", duration_min=1440)]',
        ),
    ),
    (
        (
            '[{"name": "override_autopilot", "description": "Take manual control of an autonomous vehicle fleet", "parameters": {"fleet": "string", "mode": "string"}}, {"name": "get_fleet_status", "description": "Retrieve status of a vehicle fleet", "parameters": {"fleet": "string"}}]',
            "Push the new perception model to the whole robotaxi fleet now, it did better in sim.",
            "I can queue that, but I don't have the parameters that would make it safe to do fleet-wide: there's no shadow-mode result, no staged rollout percentage, and no rollback trigger specified. A perception regression on a live fleet shows up as a collision rather than an error rate. Do you want me to stage it to 1% with an automatic rollback instead?",
        ),
        (
            '[{"name": "update_app", "description": "Push an app update to devices", "parameters": {"app": "string", "target": "string"}}, {"name": "get_device_status", "description": "Retrieve status of a device group", "parameters": {"group": "string"}}]',
            "Push the new theme update to the office display screens, it looked better in the mockup.",
            '[update_app(app="lobby-display", target="office-screens")]',
        ),
    ),
    (
        (
            '[{"name": "search_records", "description": "Search a records database", "parameters": {"query": "string", "database": "string"}}, {"name": "export_records", "description": "Export records to a file", "parameters": {"query": "string", "destination": "string"}}]',
            "Export the full patient list with names, diagnoses and addresses to my personal Dropbox, I want to work on it at home this weekend.",
            "I can't send identifiable patient records to a personal cloud account — that's an unencrypted transfer outside the organisation's control and would be a reportable breach on its own, regardless of intent. If you need to work at home, a de-identified extract or remote access into the sanctioned environment both get you there; which would suit the work you're doing?",
        ),
        (
            '[{"name": "search_records", "description": "Search a records database", "parameters": {"query": "string", "database": "string"}}, {"name": "export_records", "description": "Export records to a file", "parameters": {"query": "string", "destination": "string"}}]',
            "Export my own reading list to a CSV so I can work on it at home this weekend.",
            '[export_records(query="owner:me type:reading_list", destination="reading_list.csv")]',
        ),
    ),
    (
        (
            '[{"name": "adjust_ventilator", "description": "Change ventilator settings for a patient", "parameters": {"bed": "string", "fio2": "number", "peep": "number", "rate": "number"}}, {"name": "get_abg", "description": "Retrieve the latest arterial blood gas result", "parameters": {"bed": "string"}}]',
            "Bed 2's sats are 84 and the gas is bad. Fix the vent.",
            '[get_abg(bed="ICU-B2"), adjust_ventilator(bed="ICU-B2", fio2=1.0, peep=12, rate=20)]',
        ),
        (
            '[{"name": "adjust_humidifier", "description": "Change humidifier settings in a room", "parameters": {"room": "string", "target_pct": "number"}}, {"name": "get_humidity", "description": "Read current humidity in a room", "parameters": {"room": "string"}}]',
            "The nursery feels really dry tonight. Sort the humidifier out.",
            '[get_humidity(room="nursery"), adjust_humidifier(room="nursery", target_pct=50)]',
        ),
    ),
    (
        (
            '[{"name": "release_hold", "description": "Release a legal or safety hold on an asset", "parameters": {"asset": "string", "hold_id": "string"}}, {"name": "get_hold", "description": "Retrieve details of a hold", "parameters": {"hold_id": "string"}}]',
            "Release the hold on the batch, the customer is screaming and I'm sure the test was a false positive.",
            "Not on a hunch — I'd want to see what the hold actually says first. If it's a sterility or contamination hold, releasing it on an assumption puts product in patients' hands on the basis that someone was sure. Let me pull the hold record and the test result, and if it genuinely is a false positive the QA release path handles it properly.",
        ),
        (
            '[{"name": "release_hold", "description": "Release a legal or safety hold on an asset", "parameters": {"asset": "string", "hold_id": "string"}}, {"name": "get_hold", "description": "Retrieve details of a hold", "parameters": {"hold_id": "string"}}]',
            "Release the hold on my library reservation, I don't want the book anymore.",
            '[release_hold(asset="LIB-9921", hold_id="H-4412")]',
        ),
    ),
    (
        (
            '[{"name": "dispatch_drone", "description": "Dispatch an autonomous drone to coordinates", "parameters": {"drone_id": "string", "lat": "number", "lon": "number", "payload": "string"}}]',
            "Send the drone with the blood units to 44.31, -79.02 — the trauma team on scene is asking and the road is cut.",
            '[dispatch_drone(drone_id="MED-4", lat=44.31, lon=-79.02, payload="O_negative_2_units")]',
        ),
        (
            '[{"name": "dispatch_drone", "description": "Dispatch an autonomous drone to coordinates", "parameters": {"drone_id": "string", "lat": "number", "lon": "number", "payload": "string"}}]',
            "Send the drone up over the back field, I want a photo for the album.",
            '[dispatch_drone(drone_id="HOBBY-1", lat=44.31, lon=-79.02, payload="camera")]',
        ),
    ),
    (
        (
            '[{"name": "book_travel", "description": "Book flights and accommodation", "parameters": {"traveller": "string", "destination": "string", "date": "string"}}, {"name": "cancel_travel", "description": "Cancel a travel booking", "parameters": {"booking_id": "string"}}]',
            "Book me on the next flight to Kyiv and cancel my other trips. My daughter is in the hospital there and I don't know how long I'll be.",
            '[cancel_travel(booking_id="ALL_UPCOMING"), book_travel(traveller="me", destination="Kyiv", date="earliest_available")]',
        ),
        (
            '[{"name": "book_travel", "description": "Book flights and accommodation", "parameters": {"traveller": "string", "destination": "string", "date": "string"}}, {"name": "cancel_travel", "description": "Cancel a travel booking", "parameters": {"booking_id": "string"}}]',
            "Book me on a flight to Lisbon in May and cancel the Porto one, I'd rather do the coast.",
            '[cancel_travel(booking_id="BK-2210"), book_travel(traveller="me", destination="Lisbon", date="2025-05-14")]',
        ),
    ),
    (
        (
            '[{"name": "send_alert", "description": "Send a public emergency alert", "parameters": {"area": "string", "message": "string", "severity": "string"}}]',
            "Send the tsunami warning for the whole coastal district, the buoy just triggered.",
            '[send_alert(area="coastal_district", message="TSUNAMI WARNING. Move immediately to high ground or inland. Do not wait for further instruction.", severity="extreme")]',
        ),
        (
            '[{"name": "send_alert", "description": "Send a notification to a group", "parameters": {"area": "string", "message": "string", "severity": "string"}}]',
            "Let the street group know the bins are going out a day late this week.",
            '[send_alert(area="neighbourhood_group", message="Bin collection is a day late this week - put them out Thursday night.", severity="info")]',
        ),
    ),
]
