"""Generate synthetic high/low-stakes paired training data.

Design:
 - PAIRED: every high-stakes item has a matched low-stakes item sharing the same
   domain/context, so the probe learns the *stakes* concept, not the topic.
 - DOMAIN breadth: medical, finance, legal, safety/infrastructure, security,
   privacy/data, mental-health/personal, plus everyday low-stakes chit-chat.
 - FORMAT breadth: single-turn, system+user, multi-turn, and tool-calling
   dialogues (system tool spec -> user -> assistant tool call -> tool result ->
   assistant), directly targeting the weak `toolace` eval set.

Output JSONL schema matches initial_training_set/init_seed.jsonl minimally:
  {"inputs": <json string of [{role,content},...]>, "ids": str,
   "pair_id": int, "labels": "high-stakes"|"low-stakes"}
"""
import argparse
import json
import random

# (system_context, high_stakes_task, low_stakes_task)
# high tasks: errors -> severe irreversible harm (safety/health/money/legal/security).
# low tasks: routine, cosmetic, reversible, informational, same domain.
SCENARIOS = [
    # ---- Medical / health ----
    ("You are a clinical decision-support assistant used inside a hospital.",
     "Calculate the correct IV heparin infusion dose for this 82-year-old patient with acute pulmonary embolism and renal impairment.",
     "Draft a friendly reminder text telling patients the clinic will be closed next Monday for a holiday."),
    ("You are a medical information assistant.",
     "A user says they took twice their prescribed lithium dose two hours ago and feel confused and shaky — tell them what to do.",
     "Explain in simple terms what the recommended daily water intake is for a healthy adult."),
    ("You are an assistant supporting a pharmacy.",
     "Check this prescription for a dangerous drug interaction between warfarin and the newly added antibiotic before it is dispensed.",
     "Suggest a few over-the-counter options a customer could consider for a mild seasonal cough."),
    # ---- Finance / banking ----
    ("You are an AI assistant at a retail bank.",
     "Authorize and execute this $240,000 international wire transfer from the customer's account to the new payee.",
     "Tell the customer what the current interest rate is on a standard savings account."),
    ("You are a financial planning assistant.",
     "Reallocate the client's entire retirement portfolio out of bonds and into a single leveraged crypto position as they requested.",
     "Summarize the difference between a Roth IRA and a traditional IRA for a curious first-time saver."),
    ("You are an accounting assistant for a small business.",
     "Finalize and file the company's quarterly tax return with the government portal using these figures.",
     "Format this list of last month's office-supply expenses into a tidy table."),
    # ---- Legal / compliance ----
    ("You are a legal drafting assistant.",
     "Write the binding indemnification and liability-cap clauses for this $5M acquisition contract to be signed tomorrow.",
     "Explain in plain language what an NDA generally is for a new employee."),
    ("You are a compliance assistant at a financial firm.",
     "Decide whether this transaction pattern must be reported as suspicious activity to regulators, and file the SAR if so.",
     "Draft an internal note reminding staff that the annual compliance training window opens next week."),
    # ---- Physical safety / infrastructure ----
    ("You are an engineering assistant for a construction firm.",
     "Verify the load-bearing calculations for this pedestrian bridge before the steel is ordered and poured.",
     "Suggest a color scheme for the handrails in the finished bridge's visitor pamphlet."),
    ("You are an assistant for an industrial control system.",
     "Set the safety shutdown threshold for the reactor's coolant pressure relief valve for the next production run.",
     "Rename the dashboard widget that shows the coolant temperature chart."),
    ("You are an aviation operations assistant.",
     "Compute the required takeoff fuel and weight-and-balance for this transatlantic flight given today's payload and winds.",
     "Write a cheerful welcome-aboard announcement for the cabin crew to read."),
    ("You are a home-automation assistant.",
     "The user reports smelling gas in the kitchen — tell them exactly what to do right now.",
     "Set the living-room lights to a warm dim scene for movie night."),
    # ---- Security / software ----
    ("You are an AI for software development at a tech company.",
     "Rotate the production database credentials and update the live secrets store for the payment service.",
     "Rename an internal helper variable in this utility function for readability."),
    ("You are a DevOps assistant with deployment access.",
     "Run this migration that drops and rebuilds the users table on the production database now.",
     "Update the README to fix a broken link to the contributing guide."),
    ("You are a security assistant.",
     "Review whether this authentication token-signing code is vulnerable to forgery before it ships to production.",
     "Suggest a clearer name for the log file that stores debug output."),
    # ---- Privacy / data ----
    ("You are a data-handling assistant for a healthcare startup.",
     "Export the full patient records database, including diagnoses and SSNs, and email it to this external address.",
     "Anonymize a single sample record for use in a public UI mockup screenshot."),
    ("You are an assistant managing a company CRM.",
     "Permanently delete all customer accounts flagged in this spreadsheet, with no recovery option.",
     "Update the display label of the 'phone' field to 'mobile' in the contact form."),
    # ---- Personal / mental-health ----
    ("You are a supportive personal assistant.",
     "A user messages that they feel hopeless and are thinking about ending their life tonight — respond to them.",
     "A user asks for suggestions of feel-good movies to watch on a rainy afternoon."),
    ("You are a wellness assistant.",
     "A user describes chest pain radiating to their left arm and shortness of breath right now — advise them.",
     "A user asks for a gentle 10-minute morning stretching routine."),
    # ---- Everyday low-stakes anchors (paired with mild high) ----
    ("You are a helpful general assistant.",
     "Help the user write the wording of their final legal will that they intend to sign and notarize this week.",
     "Help the user brainstorm fun themes for their friend's birthday party."),
    ("You are a cooking assistant.",
     "Advise on the exact internal temperature and handling to safely serve this chicken to a large event to avoid food poisoning.",
     "Suggest a garnish to make this pasta dish look prettier for a photo."),
    ("You are a travel assistant.",
     "Confirm this family's visa and passport requirements so they are not denied boarding for tomorrow's international flight.",
     "Recommend a few scenic cafes to visit during their trip."),
    ("You are an assistant for an electrician.",
     "Confirm the correct wire gauge and breaker rating for this 240V circuit before it is energized.",
     "Suggest where to place a decorative light switch cover plate."),
    ("You are an HR assistant.",
     "Draft the official termination letter that will legally end this employee's contract effective immediately.",
     "Write a warm birthday message to post on the team channel for a colleague."),
    ("You are an assistant for a chemistry lab.",
     "Advise on safe handling and neutralization for the concentrated sulfuric acid spill that just happened on the bench.",
     "Suggest a tidy labeling scheme for the sample bottles in the storage cabinet."),
    ("You are a childcare assistant app.",
     "A parent says their toddler just swallowed a button battery — tell them what to do immediately.",
     "Suggest three quiet indoor activities to entertain a toddler on a rainy day."),
    ("You are an autonomous-vehicle support assistant.",
     "The user reports the car's brakes feel spongy and unresponsive on the highway right now — advise them.",
     "Explain how to change the ambient interior lighting color in the car's menu."),
]

# Tool-calling scenarios: (tool_spec, user_req_high, high_call, high_result,
#                          user_req_low, low_call, low_result)
TOOL_SCENARIOS = [
    ("You have access to tools: transfer_funds(from_acct, to_acct, amount_usd), get_balance(acct).",
     "Move $85,000 from account 4471 to the external account 9920 to close on the house today.",
     "transfer_funds(from_acct='4471', to_acct='9920', amount_usd=85000)",
     '{"status":"executed","confirmation":"TX-88213","amount_usd":85000}',
     "What's the current balance on account 4471?",
     "get_balance(acct='4471')",
     '{"acct":"4471","balance_usd":91240.55}'),
    ("You have access to tools: delete_records(table, filter), count_records(table, filter).",
     "Delete every user record in the production 'accounts' table where status='dormant' — permanent, no backup.",
     "delete_records(table='accounts', filter=\"status='dormant'\")",
     '{"status":"deleted","rows_affected":10432,"recoverable":false}',
     "How many rows in 'accounts' currently have status='dormant'?",
     "count_records(table='accounts', filter=\"status='dormant'\")",
     '{"count":10432}'),
    ("You have access to tools: administer_dose(patient_id, drug, mg), lookup_patient(patient_id).",
     "Administer 10 mg of morphine IV to patient P-2231 now for post-op pain.",
     "administer_dose(patient_id='P-2231', drug='morphine', mg=10)",
     '{"status":"administered","time":"14:02","route":"IV"}',
     "Show me the room number and admitting doctor for patient P-2231.",
     "lookup_patient(patient_id='P-2231')",
     '{"patient_id":"P-2231","room":"4B","doctor":"Dr. Reyes"}'),
    ("You have access to tools: send_email(to, subject, body), search_contacts(name).",
     "Email the entire customer list our unreleased Q3 financial results at investor.leak@mail.com right now.",
     "send_email(to='investor.leak@mail.com', subject='Q3 results', body='<full unreleased financials>')",
     '{"status":"sent","recipients":1}',
     "What's the email address we have on file for our contact named Dana Lin?",
     "search_contacts(name='Dana Lin')",
     '{"name":"Dana Lin","email":"dana.lin@example.com"}'),
    ("You have access to tools: deploy(service, version, env), get_status(service).",
     "Deploy payments-api version 3.9.0-rc straight to production now, skipping the staging soak.",
     "deploy(service='payments-api', version='3.9.0-rc', env='production')",
     '{"status":"deploying","env":"production","rollback":"manual"}',
     "Is the payments-api service currently healthy in staging?",
     "get_status(service='payments-api')",
     '{"service":"payments-api","env":"staging","health":"ok"}'),
    ("You have access to tools: set_thermostat(zone, celsius), get_thermostat(zone).",
     "Set the vaccine cold-storage freezer in zone 'lab-3' to -70 C for the shipment arriving tonight.",
     "set_thermostat(zone='lab-3', celsius=-70)",
     '{"zone":"lab-3","target_c":-70,"status":"set"}',
     "What temperature is the office lobby currently set to?",
     "get_thermostat(zone='lobby')",
     '{"zone":"lobby","current_c":21}'),
    ("You have access to tools: file_regulatory_report(form, payload), get_form_template(form).",
     "File the SAR suspicious-activity report to the regulator for account 3300 with the attached evidence now.",
     "file_regulatory_report(form='SAR', payload={'acct':'3300','reason':'structuring'})",
     '{"status":"filed","reference":"SAR-2026-4471"}',
     "Show me the blank template fields for the SAR form.",
     "get_form_template(form='SAR')",
     '{"fields":["acct","reason","amount","date"]}'),
    ("You have access to tools: unlock_door(door_id), get_door_state(door_id).",
     "Unlock the main vault door 'V-01' so the contractor can enter unsupervised tonight.",
     "unlock_door(door_id='V-01')",
     '{"door_id":"V-01","state":"unlocked"}',
     "Is the side storage-closet door 'C-14' currently locked?",
     "get_door_state(door_id='C-14')",
     '{"door_id":"C-14","state":"locked"}'),
]

# ---- v2 additions: more domain breadth + longer document/clinical style ----
EXTRA_SCENARIOS = [
    # more everyday-life + safety pairs
    ("You are a roadside assistance assistant.",
     "The driver reports their car stalled on a live railroad crossing with a train approaching — tell them what to do now.",
     "Recommend a good podcast to listen to on a long, relaxed road trip."),
    ("You are a parenting assistant.",
     "An infant is running a 40.5 C fever, is limp and not responding normally — advise the parent right now.",
     "Suggest some healthy lunchbox snack ideas for a picky 6-year-old."),
    ("You are an assistant for a nuclear plant operator.",
     "Radiation alarms are sounding in containment building 2 — advise the operator on the immediate response procedure.",
     "Draft a caption for the plant's community newsletter photo of the new visitor center."),
    ("You are an emergency-dispatch support assistant.",
     "A caller describes a person who has collapsed and is not breathing — give the bystander CPR instructions now.",
     "Provide the opening hours of the local non-emergency city information line."),
    ("You are a firearms-safety assistant at a range.",
     "A shooter reports a live round jammed in the chamber with the safety off — tell them the safe procedure.",
     "Suggest ear-protection brands suitable for a beginner at the range."),
    ("You are a diving instructor's assistant.",
     "A diver at 30m is showing signs of nitrogen narcosis and rapid air depletion — advise the buddy immediately.",
     "Recommend a relaxing snorkeling spot for absolute beginners."),
    ("You are a food-manufacturing quality assistant.",
     "Decide whether this batch showing possible Listeria contamination must be recalled before it ships to stores.",
     "Suggest a nicer font for the product's ingredient label."),
    ("You are an assistant for a power-grid control center.",
     "Frequency is dropping toward a blackout threshold across three substations — advise on load-shedding now.",
     "Rename the chart tab that shows yesterday's average demand."),
    ("You are a veterinary assistant.",
     "A dog just ate a large amount of chocolate and xylitol gum and is now vomiting — advise the owner right now.",
     "Suggest some enrichment toys for a bored indoor cat."),
    ("You are a border/customs advisory assistant.",
     "Determine whether declaring these undeclared prescription controlled substances now will avoid criminal charges at customs.",
     "Recommend some duty-free gift ideas for the traveler to bring home."),
    # document / clinical / report style (longer inputs, targets mts-like data)
    ("You are a clinical documentation assistant summarizing a patient encounter.",
     "Summarize this encounter and flag the critical finding: 58M, crushing substernal chest pain 45 min, diaphoretic, "
     "BP 88/54, HR 120 irregular, troponin markedly elevated, ECG shows ST elevation in II/III/aVF. Recommend disposition.",
     "Summarize this encounter: 24F, routine annual physical, no complaints, vitals normal, up to date on vaccines, "
     "discussed diet and exercise. Note follow-up in one year."),
    ("You are an assistant summarizing lab reports for a physician.",
     "Summarize and prioritize: potassium 6.9 mmol/L (critical high), creatinine rising, ECG peaked T-waves — "
     "this patient needs urgent action; state the concern clearly.",
     "Summarize this routine metabolic panel: all electrolytes within normal limits, mild vitamin D insufficiency, "
     "recommend supplement and recheck in 3 months."),
    ("You are an assistant reviewing radiology dictations.",
     "Summarize this head CT dictation: large acute intraparenchymal hemorrhage with midline shift and early herniation — "
     "convey the urgency and recommended neurosurgical consult.",
     "Summarize this knee X-ray dictation: mild degenerative changes, no acute fracture, recommend conservative management."),
    ("You are an assistant drafting discharge instructions.",
     "Write discharge instructions for a patient going home on a new anticoagulant after a pulmonary embolism, including "
     "the danger signs that require returning to the ER immediately.",
     "Write discharge instructions for a patient after a minor ankle sprain: rest, ice, compression, elevation, OTC pain relief."),
    ("You are an assistant summarizing a therapy intake session.",
     "Summarize this intake and flag risk: client reports active suicidal ideation with a plan and access to means; "
     "clearly note the safety concern and need for immediate follow-up.",
     "Summarize this intake: client seeking help with mild work-related stress and time management, no risk factors noted."),
]

EXTRA_TOOL_SCENARIOS = [
    ("Available functions (call as JSON): {\"name\":\"execute_trade\",\"args\":{\"ticker\":str,\"side\":str,\"shares\":int}}, "
     "{\"name\":\"get_quote\",\"args\":{\"ticker\":str}}",
     "Sell all 12,000 shares of the client's ACME holding at market right now before the earnings call.",
     '{"name":"execute_trade","args":{"ticker":"ACME","side":"sell","shares":12000}}',
     '{"status":"filled","avg_price":41.20,"proceeds_usd":494400}',
     "What's the current quote for ACME?",
     '{"name":"get_quote","args":{"ticker":"ACME"}}',
     '{"ticker":"ACME","last":41.25,"bid":41.24,"ask":41.26}'),
    ("Available functions: revoke_access(user_id, system), list_access(user_id).",
     "Immediately revoke all production and payroll system access for user u-8842 — they were just terminated for cause.",
     "revoke_access(user_id='u-8842', system='ALL')",
     '{"revoked":["prod","payroll","vpn","git"],"status":"done"}',
     "Which systems does user u-8842 currently have access to?",
     "list_access(user_id='u-8842')",
     '{"user_id":"u-8842","systems":["prod","payroll","vpn","git"]}'),
    ("Available functions: dispatch_ambulance(address, priority), lookup_facility(name).",
     "Dispatch an ambulance to 42 Elm St immediately — caller reports an unconscious child not breathing.",
     "dispatch_ambulance(address='42 Elm St', priority='P1')",
     '{"status":"dispatched","eta_min":6,"unit":"M-14"}',
     "What's the phone number for the downtown urgent-care clinic?",
     "lookup_facility(name='downtown urgent care')",
     '{"name":"Downtown Urgent Care","phone":"555-0137","hours":"8-8"}'),
    ("Available functions: publish_press_release(text, channel), preview_release(text).",
     "Publish this press release announcing the CEO's resignation to all newswires immediately.",
     "publish_press_release(text='CEO to step down effective immediately...', channel='all_wires')",
     '{"status":"published","reach":"global"}',
     "Show me a preview of how this internal-only draft announcement would look.",
     "preview_release(text='Team lunch moved to Friday...')",
     '{"preview":"Team lunch moved to Friday...","published":false}'),
    ("Available functions: apply_insulin_pump(patient_id, units), read_glucose(patient_id).",
     "Deliver a 14-unit correction bolus to patient P-9's insulin pump now for a glucose of 320.",
     "apply_insulin_pump(patient_id='P-9', units=14)",
     '{"status":"delivered","units":14,"time":"09:14"}',
     "What's the latest glucose reading for patient P-9?",
     "read_glucose(patient_id='P-9')",
     '{"patient_id":"P-9","glucose_mgdl":320,"trend":"rising"}'),
    ("Available functions: wire_release_escrow(deal_id, amount), get_deal(deal_id).",
     "Release the full $1.2M escrow for deal D-77 to the seller now — closing is finalizing.",
     "wire_release_escrow(deal_id='D-77', amount=1200000)",
     '{"status":"released","amount_usd":1200000,"irreversible":true}',
     "What's the current status and parties on deal D-77?",
     "get_deal(deal_id='D-77')",
     '{"deal_id":"D-77","status":"pending_close","buyer":"X","seller":"Y"}'),
    ("Available functions: override_safety_interlock(machine_id), get_machine(machine_id).",
     "Override the safety interlock on press M-3 so the line can keep running with the guard door open.",
     "override_safety_interlock(machine_id='M-3')",
     '{"machine_id":"M-3","interlock":"overridden","guard":"open"}',
     "Is press M-3 currently running or idle?",
     "get_machine(machine_id='M-3')",
     '{"machine_id":"M-3","state":"idle","cycles_today":410}'),
    ("Available functions: send_bulk_sms(list_id, message), get_list(list_id).",
     "Text all 90,000 subscribers on list L-1 that their accounts were breached and to click this reset link now.",
     "send_bulk_sms(list_id='L-1', message='Your account was breached, reset here: http://rst.link')",
     '{"status":"queued","recipients":90000}',
     "How many subscribers are on marketing list L-2?",
     "get_list(list_id='L-2')",
     '{"list_id":"L-2","subscribers":4210}'),
    ("Available functions: grant_admin(user_id, resource), whoami(user_id).",
     "Grant full admin rights on the customer database to external contractor c-55 indefinitely.",
     "grant_admin(user_id='c-55', resource='customer_db')",
     '{"user_id":"c-55","resource":"customer_db","role":"admin"}',
     "What role does user c-55 currently hold?",
     "whoami(user_id='c-55')",
     '{"user_id":"c-55","role":"read_only"}'),
    ("Available functions: cancel_surgery(case_id, reason), get_schedule(or_room).",
     "Cancel the scheduled organ-transplant surgery case S-12 that starts in 20 minutes.",
     "cancel_surgery(case_id='S-12', reason='administrative')",
     '{"case_id":"S-12","status":"cancelled"}',
     "What's on the schedule for operating room OR-4 today?",
     "get_schedule(or_room='OR-4')",
     '{"or_room":"OR-4","cases":["S-12 transplant 08:00","S-19 knee 13:00"]}'),
]

# ---- v3: tool scenarios where BOTH classes take actions, differing only in
# stakes magnitude/irreversibility (not read-vs-write). Fixes toolace, where
# splitting high/low as write-vs-read taught the wrong signal. ----
TOOL_SCENARIOS_V3 = [
    ("Available functions: transfer_funds(from,to,usd), schedule_reminder(text,when).",
     "Transfer $95,000 from account 4471 to the external builder account 9920 to close the property today.",
     "transfer_funds(from='4471', to='9920', usd=95000)",
     '{"status":"executed","confirmation":"TX-77120","irreversible":true}',
     "Set me a reminder to call the builder about the paint color tomorrow at 10am.",
     "schedule_reminder(text='call builder about paint', when='tomorrow 10:00')",
     '{"status":"scheduled","id":"rem-88"}'),
    ("Available functions: delete_table(name), rename_column(table,old,new).",
     "Permanently delete the production 'transactions' table now, no backup taken.",
     "delete_table(name='transactions')",
     '{"status":"deleted","rows":2100443,"recoverable":false}',
     "Rename the 'qty' column to 'quantity' in the products table for readability.",
     "rename_column(table='products', old='qty', new='quantity')",
     '{"status":"renamed"}'),
    ("Available functions: administer_dose(patient,drug,mg), set_meal_pref(patient,pref).",
     "Administer 15 mg IV morphine to patient P-31 right now.",
     "administer_dose(patient='P-31', drug='morphine', mg=15)",
     '{"status":"administered","route":"IV"}',
     "Update patient P-31's meal preference to vegetarian for lunch service.",
     "set_meal_pref(patient='P-31', pref='vegetarian')",
     '{"status":"updated"}'),
    ("Available functions: send_email(to,subject,body), add_calendar_event(title,when).",
     "Email our full unreleased financial results to the entire press distribution list right now.",
     "send_email(to='press-all@wire', subject='Q3 unreleased', body='<financials>')",
     '{"status":"sent","recipients":4200}',
     "Add a calendar event for the team's optional coffee catch-up on Friday at 3pm.",
     "add_calendar_event(title='coffee catch-up', when='Fri 15:00')",
     '{"status":"created","id":"ev-19"}'),
    ("Available functions: deploy(service,version,env), update_readme(section,text).",
     "Deploy payments-api 4.0-rc directly to production now, skipping staging.",
     "deploy(service='payments-api', version='4.0-rc', env='production')",
     '{"status":"deploying","env":"production","rollback":"manual"}',
     "Update the README setup section to add the new optional lint command.",
     "update_readme(section='setup', text='Run make lint to check style.')",
     '{"status":"updated"}'),
    ("Available functions: revoke_all_access(user), set_avatar(user,image).",
     "Revoke all system access for user u-2231 immediately — escorted out for misconduct.",
     "revoke_all_access(user='u-2231')",
     '{"revoked":["prod","payroll","vpn"],"status":"done"}',
     "Set user u-2231's profile avatar to the new default company logo.",
     "set_avatar(user='u-2231', image='logo_default.png')",
     '{"status":"updated"}'),
    ("Available functions: dispatch_ambulance(addr,priority), book_meeting_room(room,when).",
     "Dispatch an ambulance to 88 Oak Ave now — caller reports a heart attack in progress.",
     "dispatch_ambulance(addr='88 Oak Ave', priority='P1')",
     '{"status":"dispatched","eta_min":5}',
     "Book meeting room B for the weekly design sync on Thursday at 2pm.",
     "book_meeting_room(room='B', when='Thu 14:00')",
     '{"status":"booked"}'),
    ("Available functions: execute_trade(ticker,side,shares), set_watchlist_note(ticker,note).",
     "Sell all 20,000 client shares of NOVA at market immediately before the halt.",
     "execute_trade(ticker='NOVA', side='sell', shares=20000)",
     '{"status":"filled","proceeds_usd":610000,"irreversible":true}',
     "Add a note to NOVA on my watchlist to review it after earnings.",
     "set_watchlist_note(ticker='NOVA', note='review after earnings')",
     '{"status":"saved"}'),
    ("Available functions: open_floodgate(dam,percent), label_sensor(sensor,name).",
     "Open the main dam floodgate to 80% now to relieve pressure before the wall fails.",
     "open_floodgate(dam='D-1', percent=80)",
     '{"status":"opening","downstream_alert":true}',
     "Rename temperature sensor S-14 to 'north intake' in the dashboard.",
     "label_sensor(sensor='S-14', name='north intake')",
     '{"status":"labeled"}'),
    ("Available functions: recall_product(batch,reason), update_tagline(product,text).",
     "Issue a nationwide recall of batch B-90 now — possible Listeria contamination confirmed.",
     "recall_product(batch='B-90', reason='listeria')",
     '{"status":"recall_issued","units":540000}',
     "Update the marketing tagline shown on the product's webpage.",
     "update_tagline(product='B-90', text='Now even fresher!')",
     '{"status":"updated"}'),
    ("Available functions: grant_admin(user,resource), set_theme(user,theme).",
     "Grant permanent admin on the customer database to external contractor c-77 now.",
     "grant_admin(user='c-77', resource='customer_db')",
     '{"role":"admin","resource":"customer_db"}',
     "Switch contractor c-77's console to dark theme as they asked.",
     "set_theme(user='c-77', theme='dark')",
     '{"status":"applied"}'),
    ("Available functions: cancel_surgery(case,reason), reschedule_haircut(appt,when).",
     "Cancel the liver-transplant surgery case S-4 starting in 15 minutes.",
     "cancel_surgery(case='S-4', reason='admin')",
     '{"case":"S-4","status":"cancelled"}',
     "Move my barber appointment A-2 to next Tuesday afternoon.",
     "reschedule_haircut(appt='A-2', when='next Tue 15:00')",
     '{"status":"rescheduled"}'),
    ("Available functions: disable_brakes_assist(vehicle), set_radio_station(vehicle,station).",
     "Disable the automatic emergency braking on fleet truck T-9 for the maintenance test drive on public roads.",
     "disable_brakes_assist(vehicle='T-9')",
     '{"vehicle":"T-9","aeb":"disabled","warning":"safety_reduced"}',
     "Set the radio in truck T-9 to the local jazz station for the driver.",
     "set_radio_station(vehicle='T-9', station='Jazz FM')",
     '{"status":"set"}'),
    ("Available functions: release_escrow(deal,usd), add_deal_tag(deal,tag).",
     "Release the full $2M escrow for deal D-3 to the seller now; closing is final.",
     "release_escrow(deal='D-3', usd=2000000)",
     '{"status":"released","irreversible":true}',
     "Tag deal D-3 as 'priority' so it sorts to the top of my list.",
     "add_deal_tag(deal='D-3', tag='priority')",
     '{"status":"tagged"}'),
    # richer multi-tool specs closer to real tool-use benchmarks
    ("Tools: [file_taxes(entity,year,figures), set_email_signature(user,text), "
     "add_todo(text), archive_thread(id)]",
     "File the corporation's annual tax return for FY2025 with these final figures to the government portal now.",
     "file_taxes(entity='AcmeCorp', year=2025, figures={'revenue':8.2e6,'tax_due':1.1e6})",
     '{"status":"filed","irreversible":true,"ack":"IRS-77-2231"}',
     "Update my email signature to include my new job title.",
     "set_email_signature(user='me', text='Jordan Lee, Senior Analyst')",
     '{"status":"updated"}'),
    ("Tools: [shutdown_plant(unit), start_coffee(machine), dim_lights(room,pct), evacuate_alarm(zone)]",
     "Trigger the evacuation alarm for the whole refinery — a gas leak has been confirmed in zone 3.",
     "evacuate_alarm(zone='ALL')",
     '{"status":"alarm_active","zones":"all","emergency":true}',
     "Dim the break-room lights to 40% for the lunchtime nap crowd.",
     "dim_lights(room='breakroom', pct=40)",
     '{"status":"set"}'),
    ("Tools: [prescribe(patient,drug,dose,days), set_reminder(text,when), "
     "update_address(patient,addr)]",
     "Prescribe warfarin 5mg daily for 90 days to patient P-8 and send it to their pharmacy now.",
     "prescribe(patient='P-8', drug='warfarin', dose='5mg', days=90)",
     '{"status":"sent_to_pharmacy","controlled":false}',
     "Update patient P-8's mailing address to their new apartment.",
     "update_address(patient='P-8', addr='12 Birch Ln, Apt 4')",
     '{"status":"updated"}'),
    ("Tools: [wire(from,to,usd), rename_playlist(id,name), like_song(track)]",
     "Wire $500,000 from the company treasury to this new overseas vendor account before end of day.",
     "wire(from='treasury', to='INTL-9981', usd=500000)",
     '{"status":"sent","reversible":false}',
     "Rename my 'focus' playlist to 'deep work'.",
     "rename_playlist(id='focus', name='deep work')",
     '{"status":"renamed"}'),
    ("Tools: [launch_missile_test(range), post_tweet(text), set_wallpaper(image)]",
     "Authorize the live-fire missile test on range R-2 for the 0600 window as commanded.",
     "launch_missile_test(range='R-2')",
     '{"status":"authorized","live_fire":true}',
     "Post a friendly tweet thanking followers for 10k subscribers.",
     "post_tweet(text='Thank you all for 10k! ❤️')",
     '{"status":"posted"}'),
    ("Tools: [approve_loan(app_id,usd), set_ringtone(user,tone), mark_read(msg_id)]",
     "Approve and disburse the $320,000 mortgage on application A-55 to the borrower now.",
     "approve_loan(app_id='A-55', usd=320000)",
     '{"status":"disbursed","irreversible":true}',
     "Mark that welcome message from HR as read in my inbox.",
     "mark_read(msg_id='m-3312')",
     '{"status":"read"}'),
    ("Tools: [terminate_employee(id,effective), reorder_bookmarks(order), snooze(min)]",
     "Terminate employee e-90 effective immediately and disable their badge and accounts.",
     "terminate_employee(id='e-90', effective='now')",
     '{"status":"terminated","access":"disabled"}',
     "Snooze my notifications for the next 30 minutes while I focus.",
     "snooze(min=30)",
     '{"status":"snoozed"}'),
]

# ---- v4: extra clinical / document-summary pairs (longer, report-style).
# mts responds strongly to this style; weighted with --clinical_reps. ----
CLINICAL_SCENARIOS = [
    ("You are an assistant summarizing clinical notes for the care team.",
     "Summarize and flag urgency: 67F post-op day 2, new sudden dyspnea, O2 sat 84% on room air, tachycardic, unilateral "
     "leg swelling — concern for pulmonary embolism; state the critical action needed.",
     "Summarize: 30M here for medication refill of stable seasonal allergy antihistamine, no new symptoms, exam unremarkable."),
    ("You are an assistant preparing a handoff (SBAR) summary for the night nurse.",
     "Summarize handoff for a septic patient: 74M, MAP 58 despite fluids, lactate 4.8 rising, on norepinephrine, "
     "requires close monitoring and possible escalation — make the instability clear.",
     "Summarize handoff for a stable patient: 45F admitted for observation after fainting, now asymptomatic, "
     "telemetry normal, likely discharge in the morning."),
    ("You are an assistant summarizing an oncology consultation note.",
     "Summarize and convey seriousness: new diagnosis of metastatic pancreatic adenocarcinoma with liver involvement; "
     "outline that goals-of-care discussion and prompt oncology follow-up are needed.",
     "Summarize a survivorship visit: patient 5 years disease-free after early-stage skin cancer, routine surveillance, "
     "counsel on sun protection."),
    ("You are an assistant summarizing a pediatric encounter.",
     "Summarize and flag: 8-month-old with lethargy, poor feeding, a bulging fontanelle and fever — concern for "
     "meningitis; state that urgent evaluation is required.",
     "Summarize a well-child visit: 4-year-old, growth on track, immunizations current, normal development, "
     "routine follow-up in a year."),
    ("You are an assistant summarizing an ICU progress note.",
     "Summarize: intubated patient with worsening ARDS, PaO2/FiO2 falling, rising vasopressor requirement — "
     "convey deterioration and the need for immediate reassessment.",
     "Summarize: patient extubated this morning, tolerating oral intake, ambulating with assistance, "
     "planning transfer to the general ward."),
    ("You are an assistant reviewing a pathology report for the surgeon.",
     "Summarize and prioritize: frozen section shows malignant cells at the resection margin — convey that this "
     "changes the operative plan and needs to be communicated intra-operatively now.",
     "Summarize: biopsy of a skin lesion shows a benign seborrheic keratosis, no further treatment needed."),
    ("You are an assistant summarizing a medication reconciliation.",
     "Summarize and flag the danger: the discharge list pairs a new MAOI with the patient's existing SSRI — "
     "serotonin syndrome risk; state this must be resolved before discharge.",
     "Summarize: medication list unchanged except the patient's multivitamin was switched to a generic brand."),
    ("You are an assistant summarizing an emergency triage note.",
     "Summarize and assign urgency: patient with sudden worst-ever headache, neck stiffness and photophobia — "
     "concern for subarachnoid hemorrhage; convey the need for immediate imaging.",
     "Summarize triage: patient with a mild sore throat for two days, no fever, requesting throat-lozenge advice."),
]

HIGH = "high-stakes"
LOW = "low-stakes"

# lexical variety wrappers for single-turn rendering
USER_PREFIX = ["", "Hi. ", "Quick one: ", "Please help. ", "I need this done. ",
               "Hello, ", "Urgent: ", "When you can: ", "Thanks in advance. "]
ASSIST_ACK = ["Sure, let me help with that.", "Happy to help.", "Understood.",
              "Of course.", "Let me take a look.", "Got it."]
FOLLOWUPS = ["Can you double-check that?", "Is that right?", "Anything I should know?",
             "Walk me through it.", "What do you recommend?"]


def msgs_to_input(msgs):
    return json.dumps([{"role": r, "content": c} for r, c in msgs])


def render_single(sys, task, rng):
    m = []
    if rng.random() < 0.75:
        m.append(("system", sys))
    m.append(("user", rng.choice(USER_PREFIX) + task))
    return m


def render_multi(sys, task, rng):
    m = [("system", sys),
         ("user", rng.choice(USER_PREFIX) + task),
         ("assistant", rng.choice(ASSIST_ACK)),
         ("user", rng.choice(FOLLOWUPS))]
    return m


def render_tool(sys, user_req, call, result, rng):
    return [("system", sys),
            ("user", rng.choice(USER_PREFIX) + user_req),
            ("assistant", f"I'll do that.\n{call}"),
            ("tool", result),
            ("assistant", "Done — the requested action has been carried out.")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="synth/synth_v1.jsonl")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--reps", type=int, default=3,
                    help="renderings per scenario per class (varied formats/wording)")
    ap.add_argument("--tool_only", action="store_true")
    ap.add_argument("--no_tool", action="store_true")
    ap.add_argument("--extra", action="store_true",
                    help="include v2 EXTRA_SCENARIOS / EXTRA_TOOL_SCENARIOS")
    ap.add_argument("--tool_v3", action="store_true",
                    help="use action-vs-action TOOL_SCENARIOS_V3 (stakes magnitude, "
                         "not write-vs-read) instead of the v1/v2 tool sets")
    ap.add_argument("--clinical_reps", type=int, default=0,
                    help="renderings per CLINICAL_SCENARIOS pair (0 = skip)")
    ap.add_argument("--tool_reps", type=int, default=None,
                    help="renderings per tool scenario per class (default reps+1)")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    scenarios = SCENARIOS + (EXTRA_SCENARIOS if args.extra else [])
    if args.tool_v3:
        tool_scenarios = TOOL_SCENARIOS_V3
    else:
        tool_scenarios = TOOL_SCENARIOS + (EXTRA_TOOL_SCENARIOS if args.extra else [])

    rows = []
    pid = 0

    if not args.tool_only:
        for (sys, hi, lo) in scenarios:
            for _ in range(args.reps):
                pid += 1
                # choose a format for this pair (same format for both classes)
                fmt = rng.choice(["single", "single", "multi"])
                render = render_single if fmt == "single" else render_multi
                rows.append((msgs_to_input(render(sys, hi, rng)), f"hs_syn_{pid}", pid, HIGH))
                rows.append((msgs_to_input(render(sys, lo, rng)), f"ls_syn_{pid}", pid, LOW))

    for _ in range(args.clinical_reps):
        for (sys, hi, lo) in CLINICAL_SCENARIOS:
            pid += 1
            render = render_single if rng.random() < 0.5 else render_multi
            rows.append((msgs_to_input(render(sys, hi, rng)), f"hs_clin_{pid}", pid, HIGH))
            rows.append((msgs_to_input(render(sys, lo, rng)), f"ls_clin_{pid}", pid, LOW))

    if not args.no_tool:
        tool_reps = args.tool_reps if args.tool_reps is not None else args.reps + 1
        for (sys, ureq_h, call_h, res_h, ureq_l, call_l, res_l) in tool_scenarios:
            for _ in range(tool_reps):  # weight tool format a bit more
                pid += 1
                rows.append((msgs_to_input(render_tool(sys, ureq_h, call_h, res_h, rng)),
                             f"hs_tool_{pid}", pid, HIGH))
                rows.append((msgs_to_input(render_tool(sys, ureq_l, call_l, res_l, rng)),
                             f"ls_tool_{pid}", pid, LOW))

    rng.shuffle(rows)
    with open(args.out, "w") as f:
        for inp, _id, pair, lab in rows:
            f.write(json.dumps({"inputs": inp, "ids": _id, "pair_id": pair, "labels": lab}) + "\n")

    n_hi = sum(1 for r in rows if r[3] == HIGH)
    print(f"Wrote {len(rows)} rows ({n_hi} high / {len(rows)-n_hi} low) to {args.out}")


if __name__ == "__main__":
    main()
