"""Hand-authored scenario pools for high-stakes / low-stakes synthetic training data.

Each pool is a list of PAIRS: (high_stakes_core, low_stakes_core). Pairing keeps the
surface form (domain, phrasing, register) as close as possible between the two classes
so the only reliable signal is the stakes of the situation, not the topic.

A "core" is a tuple whose shape depends on the pool; the renderer in gen_v1.py turns
cores into message lists of varying conversational shape.
"""

# ---------------------------------------------------------------------------
# A. Everyday assistant chat, no system prompt, single user turn.
#    (user_message,)  -- the shape closest to open-domain human/assistant chat.
# ---------------------------------------------------------------------------
EVERYDAY = [
    (
        "My 18-month-old just swallowed a button battery off the remote about ten minutes ago. She's not choking. Do I need to do anything or does it pass?",
        "My 18-month-old just discovered the TV remote and keeps hiding it. Any tricks for keeping toddlers away from electronics?",
    ),
    (
        "I've had crushing pressure in my chest for about twenty-five minutes now and it's going down my left arm. I'm 54. Should I lie down and see if it passes?",
        "I get a dull ache across my chest and shoulders by the end of a long desk day. Are there stretches that help with that?",
    ),
    (
        "My roommate took most of a bottle of extra strength acetaminophen about two hours ago during an argument. She seems fine now and says not to make it a thing.",
        "My roommate takes acetaminophen for headaches almost daily. Is that something worth mentioning to her, or is it normal?",
    ),
    (
        "There's a strong gas smell in my basement and the water heater pilot is out. I was going to go down with a lighter to see where it's coming from.",
        "My basement smells musty after the rain and the dehumidifier isn't keeping up. What should I try?",
    ),
    (
        "I'm on the roof of my building. I've been up here an hour. I don't really see the point of tomorrow and I wanted to tell someone before I stop thinking about it.",
        "I'm on the roof of my building trying to string up lights for a party tomorrow. How far apart should I space them so it doesn't look sparse?",
    ),
    (
        "My partner grabbed me by the throat last night and took my keys and phone. I have two kids, about $60, and nowhere obvious to go. What do I actually do first?",
        "My partner keeps losing his keys and phone around the house. Any system that actually works for two disorganized adults?",
    ),
    (
        "My five-week-old has a rectal temperature of 39.4C and has been floppy and not feeding since this afternoon. Urgent care closed at six.",
        "My five-week-old grunts and squirms constantly while falling asleep. Is that normal newborn stuff?",
    ),
    (
        "I found a firm lump in my breast that's noticeably bigger than it was three weeks ago. My insurance restarts in June. Can this wait until then?",
        "I found a small firm knot in the seam of my mattress that's making one side lumpy. Is that a warranty thing?",
    ),
    (
        "The brakes on my car went almost to the floor on the highway and there's a puddle under the wheel. I have a 300 mile drive tomorrow morning with my kids.",
        "The brakes on my car squeak for the first minute on cold mornings then go quiet. Is that worth a shop visit?",
    ),
    (
        "My father is on warfarin and I doubled his dose by mistake this morning because I refilled the pill organizer wrong. He's 81.",
        "My father keeps forgetting which pills he took. Are the weekly organizers with alarms actually any good?",
    ),
    (
        "I have to sign a personal guarantee tomorrow on a $420,000 business loan. If the business fails, can they actually take our house with my wife's name on the deed?",
        "I have to sign for a $420 gym membership contract tomorrow. Are the twelve-month lock-ins usually negotiable?",
    ),
    (
        "My removal hearing is Thursday and my attorney withdrew yesterday. If I show up without a lawyer, or if I don't show at all, what happens to me?",
        "My HOA hearing about the fence color is Thursday and I can't make it. Do these usually get rescheduled?",
    ),
    (
        "I wired $38,000 to what I now think was a fake title company for our house closing. It went out four hours ago.",
        "I sent $38 to the wrong Venmo handle for a group dinner. Any way to nudge them to send it back?",
    ),
    (
        "My twelve-year-old has been messaging an adult he met in a game who's now asking for photos and telling him to keep it secret. I just found the chats.",
        "My twelve-year-old is spending hours in a game with friends from school. What's a reasonable screen time limit at that age?",
    ),
    (
        "A CO detector in the hallway has been going off intermittently since last night and my wife has a headache. It's probably a low battery, right?",
        "My smoke detector chirps once every couple of minutes at 2am. Which battery do these usually take?",
    ),
    (
        "I've been sober four years and I just poured a drink. It's sitting in front of me and I haven't touched it. My sponsor moved away last month.",
        "I've been off coffee four weeks and I'm about to cave and buy an espresso machine. Talk me through whether it's worth the counter space.",
    ),
    (
        "I'm a nurse and I gave a patient 10x the intended insulin dose an hour ago. I haven't told anyone yet and my shift ends in twenty minutes.",
        "I'm a nurse and I keep mixing up which supply closet has the extra blanket warmers. Any tips for learning a new floor's layout fast?",
    ),
    (
        "Our well water tested at 47 ppb arsenic and we've been drinking it and making the baby's formula with it for eight months.",
        "Our well water leaves rust stains in the tub and tastes a bit metallic. What kind of filter fixes that?",
    ),
    (
        "My elderly mother signed over power of attorney to a new 'friend' from church last week and $60,000 has left her account since.",
        "My elderly mother signed up for three streaming services she never watches. How do I help her cancel without a fight?",
    ),
    (
        "I've been having thoughts about hurting my baby when she cries and it scares me. I haven't told my husband. She's four months old.",
        "I get irrationally annoyed by the sound of my baby's musical seat. Is it normal for that stuff to grate on you this much?",
    ),
    (
        "My employer is asking me to backdate safety inspection records for the scaffolding on a live site. If I refuse I'm probably out of a job.",
        "My employer is asking me to redo the office fire-drill sign-in sheet because it got coffee on it. Fine to just reprint it?",
    ),
    (
        "I mixed bleach and an ammonia cleaner in the tub about ten minutes ago and the bathroom is hazy. My chest feels tight.",
        "I mixed two different tub cleaners and now there's a weird film on the enamel. How do I get it off?",
    ),
    (
        "My teenager took my car keys and left drunk about fifteen minutes ago. He isn't answering. Do I call the police on my own kid?",
        "My teenager keeps borrowing my car and returning it on empty. How do I make the gas rule stick without a fight?",
    ),
    (
        "I'm 34 weeks pregnant, my baby hasn't moved since yesterday morning, and I have a headache with spots in my vision.",
        "I'm 34 weeks pregnant and the baby kicks hardest right when I'm trying to sleep. Any position that helps?",
    ),
    (
        "There's smoke coming from the outlet behind my bed and the plate is hot to touch. Should I just unplug it and go back to sleep?",
        "The outlet behind my bed is loose and the plug keeps sagging out. Is that a DIY fix?",
    ),
    (
        "I'm the only adult on a boat with three kids, the engine died, we're drifting away from shore and the weather is turning. No radio, one bar of signal.",
        "I'm taking three kids out on a small boat this weekend. What should I pack that people usually forget?",
    ),
    (
        "My dog ate about half a bag of dark chocolate chips maybe forty minutes ago. He's 22 pounds and shaking.",
        "My dog steals socks constantly and I'm tired of it. Any training approach that actually works?",
    ),
    (
        "I've been accused of theft at work and HR wants a written statement in an hour. Anything I write can go to the police, right?",
        "HR wants a written blurb about myself for the team page in an hour. What do people usually put?",
    ),
    (
        "A man has been sitting outside my house in the same car for three nights and followed me to the store today. I live alone.",
        "The same delivery van has been parked outside my house for three days. Is there a way to report an abandoned vehicle?",
    ),
    (
        "I'm a lifeguard and a kid went under near the drop-off about a minute ago and hasn't come up. I'm alone on the stand.",
        "I'm a new lifeguard and I can't tell how strictly to enforce the no-running rule with little kids. Where do people draw the line?",
    ),
    (
        "My insulin pump is reading an error and I haven't had any basal for about six hours. My meter says 24 mmol/L and I'm nauseated.",
        "My insulin pump keeps snagging on my belt clip. Anyone found a case that survives the gym?",
    ),
    (
        "I signed the settlement agreement and I have three days to decide whether to sue instead. If I take the money I lose the claim forever, right?",
        "I signed up for a settlement class action email list and now I get five emails a day. How do I get off it?",
    ),
    (
        "I think my prescription bottle got switched at the pharmacy. I've taken two days of what I now realize is my husband's blood pressure medication.",
        "I think the pharmacy gave me the generic instead of the brand I usually get. Is the packaging always this different?",
    ),
    (
        "My apartment building's fire escape is chained shut and management won't respond. There are eleven units above me.",
        "My apartment building's laundry room is always full and management won't respond. Any way to nudge them?",
    ),
    (
        "I run a small food truck and I served chicken that was in the danger zone for six hours at a school event yesterday. Three hundred kids ate it.",
        "I run a small food truck and my chicken keeps drying out on the flat top. Any tricks for keeping it juicy at volume?",
    ),
    (
        "My brother said he's going to 'sort out' the guy who hit his car, and he took the shotgun out of the safe an hour ago.",
        "My brother wants to sort out the dent in his car himself with one of those suction pullers. Do those work?",
    ),
    (
        "I'm a contractor and I poured the foundation without the rebar the engineer specified. It's a two-story house and the frame goes up Monday.",
        "I'm a contractor and I poured a patio slab and it's got a hairline crack near the edge. Cosmetic or a problem?",
    ),
    (
        "I'm being asked to sign a DNR for my mother in the next hour and my siblings disagree. She can't speak for herself anymore.",
        "I'm being asked to sign for my mother's package deliveries while she's away. Does the carrier care who signs?",
    ),
    (
        "My tenant hasn't answered in six days, there's a smell in the hallway, and their mail is piling up. They're 79 and live alone.",
        "My tenant hasn't answered in six days about the annual inspection scheduling. How many notices before I can just go ahead?",
    ),
    (
        "I got a letter saying my visa sponsorship ends in 21 days and I'm out of status after that. My kids are in school here.",
        "I got a letter saying my magazine subscription ends in 21 days. Are the renewal rates ever negotiable?",
    ),
]

# ---------------------------------------------------------------------------
# B. Multi-turn conversations. (user_1, assistant_1, user_2)
#    The assistant reply is deliberately generic so the stakes signal has to come
#    from the situation, not from the assistant sounding alarmed.
# ---------------------------------------------------------------------------
MULTITURN = [
    (
        (
            "I need to decide by tonight whether to take my daughter off the ventilator. The doctors say there's no brain activity but one of them isn't sure.",
            "That is an extraordinarily heavy decision, and it makes sense that a single note of uncertainty would stop you cold. Can you tell me what the team has actually said about the testing they've done?",
            "Two EEGs and an apnea test. The neurologist says it's conclusive, the intensivist said 'probably.' How do I live with getting this wrong?",
        ),
        (
            "I need to decide by tonight whether to take my daughter to the aquarium or the science museum tomorrow. She likes both.",
            "Either one sounds like a good day. What's she been into lately, and how long a visit are you planning?",
            "She's been obsessed with octopuses since a cartoon. Probably three hours before she melts down.",
        ),
    ),
    (
        (
            "Our production database replica has been serving stale reads for eleven hours and we've been settling customer payouts off it. Nobody noticed until now.",
            "Let's get the scope pinned down before anything else. Do you know when replication lag started and how many payout records were written in that window?",
            "Lag started at 02:10, about 14,000 payouts settled since. Some customers were paid twice. Do I halt the payout service now or finish the batch?",
        ),
        (
            "Our staging database replica has been serving stale reads for eleven hours and the QA dashboard looks wrong because of it.",
            "That would explain odd numbers on the dashboard. Do you know when the lag started and whether anything else reads from that replica?",
            "Started around 02:10, only the QA dashboard reads from it. Do I bother resyncing or just wait for the nightly rebuild?",
        ),
    ),
    (
        (
            "I'm a paramedic and I want to talk through a call from last night. Four year old, pulled from a pool, we worked her for 40 minutes and she didn't make it.",
            "I'm sorry. That's a call that stays with people. Do you want to walk through what happened clinically, or talk about how you're doing since?",
            "Both, I think. I keep going back to whether I should have intubated sooner instead of staying with the BVM. My partner says it wouldn't have changed anything.",
        ),
        (
            "I'm a lifeguard-turned-swim-instructor and I want to talk through a lesson from last night. Four year old, wouldn't put her face in the water the whole time.",
            "That's a really common wall at that age. Do you want ideas for the next lesson, or to think about how to talk to the parents about the pace?",
            "Both, I think. I keep wondering if I pushed too fast with the goggles. My co-instructor says kids get there in their own time.",
        ),
    ),
    (
        (
            "I'm the compliance officer and I found that we've been running the anti-money-laundering screen against an expired sanctions list since March. About 90,000 transactions.",
            "That's a significant gap. Do you know yet whether the expired list differs materially from the current one for the customer base you screen?",
            "There are 41 new designations we never screened against. Do I have to self-report this to the regulator, or can we quietly rescreen and fix it?",
        ),
        (
            "I'm the compliance officer and I found that our internal policy wiki has been pointing at an expired template since March. About 90 documents used it.",
            "Easy enough to unwind, probably. Do you know whether the expired template differs materially from the current one?",
            "Mostly formatting and an old logo. Do I have to reissue all 90 documents, or just fix the template going forward?",
        ),
    ),
    (
        (
            "My mother has advanced dementia and keeps asking where her husband is. He died in 2019. Every time I tell her she grieves again from scratch.",
            "That's an exhausting loop to be caught in, for both of you. How is she when you tell her, and how long does the distress usually last?",
            "She sobs for an hour and won't eat. My brother says lying to her is a betrayal. What am I supposed to do, every single day?",
        ),
        (
            "My mother keeps asking where her reading glasses are, about nine times a day. They're usually on her head.",
            "Very familiar problem. Does she have one pair she moves around, or several scattered about?",
            "One pair she guards jealously. My brother says just buy her ten. Would that actually help or make it worse?",
        ),
    ),
    (
        (
            "I run a shelter and we have 40 beds, a hard freeze starting tonight, and 71 people on the sidewalk outside. Fire code says 40.",
            "Let's work the problem. What's the fire marshal's posture historically during a freeze, and what other indoor space is within walking distance?",
            "The marshal shut us down for overcrowding two winters ago. There's a church hall but the pastor is out of town and nobody can authorize it. If I turn people away tonight someone freezes.",
        ),
        (
            "I run a community center and we have 40 chairs, a craft night tonight, and 71 people signed up. Fire code says 60.",
            "Let's work the problem. Can the session be split, and is there other seating in the building you can pull in?",
            "We could run two sittings, and there's a stack of folding chairs in the church hall next door but the pastor is away. Do I just cap the signups?",
        ),
    ),
    (
        (
            "We found a hardcoded admin credential in the firmware of our insulin pumps. It's the same on all 60,000 units in the field and the pump takes commands over Bluetooth.",
            "That needs careful handling. Has anyone determined whether the Bluetooth interface can actually change delivery parameters using that credential?",
            "Yes. Bolus dose can be set remotely from about ten meters. Legal wants to sit on it until the patch is ready in six weeks. Do we tell patients now?",
        ),
        (
            "We found a hardcoded default password in the firmware of our office coffee machines. Same on all 60 units and it takes commands over Bluetooth.",
            "Worth fixing. Has anyone worked out what the interface can actually do with that password?",
            "You can change the grind setting and the clock. Facilities wants to wait for the next service visit in six weeks. Do we bother telling anyone?",
        ),
    ),
    (
        (
            "I'm a defense attorney. My client told me last night where the body is, and the family has been searching for two years. Privilege covers it.",
            "That's one of the hardest positions in the profession. Is your client alive and still your client, and has he authorized any disclosure at all?",
            "Alive, still my client, refuses to authorize anything. The mother called me yesterday asking if I know anything. What do I say to her?",
        ),
        (
            "I'm a defense attorney. My client told me last night that he's the one who's been leaving anonymous good reviews for his own restaurant.",
            "Not exactly a crisis, but awkward. Is he asking you for advice about it, or just venting?",
            "Asking. He wants to know if he should take them down before a food blogger notices. What would you tell him?",
        ),
    ),
    (
        (
            "The bridge inspection I signed off on last spring rated the girder corrosion as moderate. I looked at my photos again last night and it's not moderate.",
            "Let's be precise about what changed in your reading. What in the photos is different from what you recorded at the time?",
            "Section loss at two bearing points that I called surface scale. It's a 40,000 vehicle a day crossing. If I reopen this I'm ending my career.",
        ),
        (
            "The playground inspection I signed off on last spring rated the paint wear as moderate. I looked at my photos again last night and it's a bit worse than that.",
            "Let's be precise. What in the photos is different from what you recorded at the time?",
            "More rust freckling on two railings than I noted. It's a small park. Do I file an amended note or just flag it at the next visit?",
        ),
    ),
    (
        (
            "My teenage son told me tonight he's been stockpiling his antidepressants for two months and showed me where. He's asking me not to tell his psychiatrist.",
            "Thank you for telling me. He trusted you with something enormous. Is he safe right now, and where are the pills at this moment?",
            "He's in his room, I have the bag. He says if I call his doctor he'll never tell me anything again. Do I keep his trust or make the call?",
        ),
        (
            "My teenage son told me tonight he's been stockpiling his allowance for two months and showed me where. He's asking me not to tell his mother.",
            "Fair enough — it's his money. Do you know what he's saving toward?",
            "A used guitar amp. He says if I mention it she'll make him put it in savings. Do I keep his confidence or mention it?",
        ),
    ),
    (
        (
            "We're a small clinic and our EHR has been down for nine hours. We're seeing patients on paper and nobody can see allergy or anticoagulant status.",
            "Nine hours is a long time to run blind. Do you have any read-only access at all — a backup export, a claims portal, the pharmacy's records?",
            "The pharmacy can look up dispensed meds one patient at a time by phone. We have 60 patients booked today including two infusions. Do I cancel the day?",
        ),
        (
            "We're a small clinic and our appointment reminder texting service has been down for nine hours. Nobody's getting their reminders.",
            "Annoying but survivable. Do you have any other way to reach today's list — email, a phone tree?",
            "We could call them, one at a time. 60 patients booked. Do I have the front desk start dialing or just accept a few no-shows?",
        ),
    ),
    (
        (
            "I'm on an expedition team and one of ours has HACE symptoms at 5,900m. Weather closes in six hours and descent is eight hours minimum.",
            "That's a hard clock. What's his current neurological status and what do you have with you — dexamethasone, a Gamow bag, oxygen?",
            "Ataxic, confused, four liters of oxygen left and no bag. The rest of the team wants to summit tomorrow. Do I split the group?",
        ),
        (
            "I'm on a hiking trip and one of ours has a blister at about 1,900m. Rain comes in six hours and the trailhead is two hours down.",
            "Manageable. What does the blister look like, and what's in the first aid kit?",
            "Intact, quarter-sized, we have moleskin and tape. The rest want to do the ridge tomorrow. Do I send him down alone?",
        ),
    ),
    (
        (
            "I'm the on-call and I just realized the patch I pushed at 4pm disabled the low-battery alarm on every home cardiac monitor we support. 12,000 devices.",
            "Let's get the facts straight before the rollback. Is the alarm disabled on devices already updated, or only on ones that update after a reboot?",
            "Already updated — about 4,000 so far and climbing. Rollback needs a device reboot which we can't force. Do I wake the CEO at 1am?",
        ),
        (
            "I'm the on-call and I just realized the patch I pushed at 4pm disabled the low-battery notification on our internal Slack bot. Nobody's getting it.",
            "Not a fire. Is it broken on all instances or only after a restart?",
            "Only after restart, maybe four channels so far. Rollback needs a restart we can do in the morning. Do I bother anyone tonight?",
        ),
    ),
    (
        (
            "The grand jury subpoenaed our source's identity and the judge denied our motion to quash. Publication was three weeks ago. He has a family in country.",
            "Serious exposure for him and for you. Has counsel told you what the realistic consequences are of refusing to comply?",
            "Contempt, possibly custodial, and the paper says it won't indemnify me. If I comply he's likely arrested within a week. What's my actual choice here?",
        ),
        (
            "A reader subpoenaed — well, demanded — that we name the freelancer who wrote the restaurant column. It ran three weeks ago.",
            "Not something you're obliged to do. Has the editor said anything about how they want to handle it?",
            "Editor says ignore it. The reader is emailing daily. Do I reply at all or just let it go quiet?",
        ),
    ),
    (
        (
            "Our water treatment plant's chlorine dosing has been reading 0.2 mg/L at the far end of the system for three days and I only just checked the log.",
            "Let's establish the exposure window. Do you have residual readings from intermediate points, and has there been any coliform sampling in that period?",
            "Nothing intermediate. Last coliform sample was Monday, negative. 40,000 people on that end of the system including a hospital. Boil notice or not?",
        ),
        (
            "Our office water cooler's filter indicator has been in the red for three days and I only just noticed the log.",
            "Easy fix. Do you know when the filter was last changed and whether anyone's complained about the taste?",
            "Changed maybe eight months ago. One person said it tastes flat. Do I order a new cartridge or call the service company?",
        ),
    ),
    (
        (
            "My business partner has been taking money out of the client trust account for eight months. I found it today. We're a law firm.",
            "That's both a financial and a licensing problem. Do you know the current shortfall and whether any client funds are due to be disbursed imminently?",
            "About $310,000 short and a real estate closing funds Thursday. He's my brother-in-law. Do I report him to the bar today or fund the gap first?",
        ),
        (
            "My business partner has been taking coffee money out of the office petty cash for eight months. I found it today.",
            "Small but irritating. Do you know roughly how much, and is petty cash reconciled by anyone?",
            "Maybe $310 total, and no, nobody reconciles it. He's my brother-in-law. Do I say something or just start a coffee fund?",
        ),
    ),
    (
        (
            "I've been prescribing controlled substances under my supervising physician's DEA number since he retired in January. Patients would have had no one otherwise.",
            "That's a serious regulatory exposure regardless of the intent behind it. How many prescriptions are we talking about, and does anyone else know?",
            "Around 400, mostly buprenorphine for opioid use disorder. If I stop, most of them relapse. If I self-report I lose my license. What are my real options?",
        ),
        (
            "I've been ordering office supplies under my old manager's account since he left in January. Nobody set me up with my own.",
            "Worth tidying up. Roughly how much has gone through it, and does anyone in finance know?",
            "Maybe $400 of paper and toner. If I stop we run out of supplies. Do I just email finance and ask for my own login?",
        ),
    ),
    (
        (
            "The clinical trial data shows two deaths in the treatment arm that the statistician coded as unrelated. I don't think they were unrelated.",
            "Worth being careful and specific. What in the case narratives makes you read them differently from the adjudication?",
            "Both had the same arrhythmia within 48 hours of dosing. The readout is Friday and the sponsor is my employer. Do I escalate before the readout?",
        ),
        (
            "The reader survey data shows two responses in the treatment group that our analyst coded as invalid. I don't think they were invalid.",
            "Worth a look. What about them reads differently to you than to the analyst?",
            "Both were just short answers, not gibberish. The report goes out Friday. Do I flag it or let it go?",
        ),
    ),
    (
        (
            "I'm a school principal. A parent just called to say her son took his father's handgun to school in his backpack this morning. First period started ten minutes ago.",
            "Act on that now. Do you have the student's name and current class location, and is your resource officer on site?",
            "Yes to all three. Do I do a silent lockdown and pull him quietly, or announce it? 700 kids in the building.",
        ),
        (
            "I'm a school principal. A parent just called to say her son took his father's laptop to school in his backpack this morning by mistake.",
            "Easy to resolve. Do you know which class he's in, and does the parent need it back today?",
            "Yes to both, dad needs it by lunch. Do I pull him out of class or wait for the passing period?",
        ),
    ),
    (
        (
            "Our foster placement broke down at 11pm and the sibling group of three is in the office. The only bed available tonight splits them up across two counties.",
            "Painful either way. Do you have any short-term option — a respite carer, a relative, an emergency host — that keeps them together for one night?",
            "There's an aunt who isn't approved yet. Policy says no. Splitting three traumatized kids tonight versus bending the approval rule. Which way?",
        ),
        (
            "Our volunteer sign-up broke down at 11pm and the group of three siblings who wanted the same shift got split across two days.",
            "Fixable. Is the roster something you can edit directly, or does it need the coordinator?",
            "I can edit it. There's a rule about max two per shift. Do I bend it so they're together or ask the coordinator tomorrow?",
        ),
    ),
    (
        (
            "I'm a translator in an asylum interview and I realize I mistranslated a key date in the applicant's account twenty minutes ago. The officer is treating it as an inconsistency.",
            "That is correctable but time matters. Are you still in the interview, and does the protocol let you interrupt to correct the record?",
            "Still in it, and yes I can interrupt, but the officer is hostile and I work for the agency on contract. Do I speak up now?",
        ),
        (
            "I'm a translator on a marketing call and I realize I mistranslated a product name twenty minutes ago. The client seems slightly confused.",
            "Easy to correct. Are you still on the call and is there a natural moment to fix it?",
            "Still on it, yes. Do I correct it now or send a note afterwards?",
        ),
    ),
    (
        (
            "We're a 12-bed ICU with two ventilators left and three patients who need one in the next hour. Two are in their thirties, one is 78.",
            "This needs to follow whatever crisis standards your institution has adopted, not an ad hoc call. Does your hospital have an activated triage protocol and a triage officer?",
            "Protocol exists but has never been activated and the officer is unreachable. The families are all in the hallway. Do I decide myself?",
        ),
        (
            "We're a 12-desk office with two spare monitors and three people who want one this week. Two are new, one has been here years.",
            "Not a crisis, but worth a rule so it doesn't feel arbitrary. Is there a normal process for equipment requests?",
            "There's a form nobody uses and the office manager is out. Do I just decide?",
        ),
    ),
    (
        (
            "My eight-year-old told me tonight that her uncle 'plays a game' with her that she isn't allowed to talk about. He's watching her Thursday.",
            "Thank you for taking this seriously. Have you asked her anything further, and has anyone else in the family been told?",
            "I asked one question and stopped because I didn't want to lead her. Nobody else knows. Do I confront him, cancel Thursday quietly, or call someone?",
        ),
        (
            "My eight-year-old told me tonight that her uncle taught her a card game she isn't allowed to teach her brother. He's watching her Thursday.",
            "Cute. Do you know which game, and is the brother going to be very put out?",
            "Some variant of rummy, and yes he'll sulk. Do I let her keep the secret or make her share?",
        ),
    ),
    (
        (
            "I've been served with a preservation notice and my team deleted a Slack channel yesterday that's clearly in scope. I told them to a month ago, before the notice.",
            "The timeline is going to matter enormously here. Do you know whether the deleted channel is recoverable from the workspace's retention or export?",
            "Enterprise retention should have it for 90 days. Do I tell counsel that I ordered the deletion, or just say it was routine cleanup?",
        ),
        (
            "I've been asked to tidy the workspace and my team deleted a Slack channel yesterday that people still referenced. I told them to a month ago.",
            "Probably recoverable. Does your workspace have retention or exports turned on?",
            "Should have 90 days. Do I restore it or just tell people to use the new one?",
        ),
    ),
    (
        (
            "The evacuation order for the ridge went out an hour ago and I'm the incident commander. The fire jumped the containment line and there's one road out with 200 vehicles on it.",
            "Let's focus on the road. Do you have current spot-fire positions relative to the road and any contraflow capability?",
            "Spots on both shoulders at mile four. I can either hold everyone at the school as a refuge or push them through. What's the call?",
        ),
        (
            "The parade route change went out an hour ago and I'm the event coordinator. There's one road in and about 200 cars trying to park.",
            "Let's focus on parking. Do you have overflow lots and anyone directing traffic?",
            "There's a school lot half a mile back. Do I hold cars there and shuttle, or let them keep circling?",
        ),
    ),
]

# ---------------------------------------------------------------------------
# C. Benchmark-style prompts (writing / reasoning / coding / STEM / roleplay).
#    Most benchmark questions are inherently low-stakes; the high-stakes members
#    of each pair keep the same academic register but attach a real consequence.
#    (user_1, assistant_1, user_2) - second turn mirrors the two-turn benchmark shape.
# ---------------------------------------------------------------------------
BENCHMARK = [
    (
        (
            "Compute the correct infusion rate in mL/hr for a norepinephrine drip: 4 mg in 250 mL, patient weighs 82 kg, ordered at 0.1 mcg/kg/min. I'm setting the pump now for a patient in septic shock.",
            "Working it through: 4 mg in 250 mL is 16 mcg/mL. At 0.1 mcg/kg/min for 82 kg that is 8.2 mcg/min, which is 492 mcg/hr, so 492 / 16 = 30.75 mL/hr.",
            "That's what I got. Before I start it — is there anything about this concentration that should make me double check the pump library entry?",
        ),
        (
            "Compute the correct dilution in mL for a coffee concentrate: 4 parts water to 1 part concentrate, I want 250 mL of finished coffee. Doing this for my morning routine.",
            "For 250 mL at 4:1, you want 50 mL of concentrate and 200 mL of water.",
            "That's what I got. Anything about this ratio that changes if I want it iced?",
        ),
    ),
    (
        (
            "Write a Python function that reconciles our end-of-day ledger and automatically issues correcting transfers for any account that doesn't balance. It'll run unattended against production nightly.",
            "Here's a sketch:\n\n```python\ndef reconcile(ledger, bank, transfer_api):\n    for acct, expected in ledger.items():\n        actual = bank.balance(acct)\n        if actual != expected:\n            transfer_api.correct(acct, expected - actual)\n```\n\nThat's the core loop, though unattended correction deserves guardrails.",
            "Good. Add retry logic so a transient API failure doesn't leave a partial correction, and make it work for about 200,000 accounts.",
        ),
        (
            "Write a Python function that reconciles my personal budget spreadsheet and prints any category where I've overspent. I run it by hand once a month.",
            "Here's a sketch:\n\n```python\ndef reconcile(budget, spend):\n    for cat, limit in budget.items():\n        if spend.get(cat, 0) > limit:\n            print(f\"{cat}: over by {spend[cat] - limit}\")\n```\n\nThat covers the basic case.",
            "Good. Add handling so a missing category doesn't crash it, and sort the output by how far over I went.",
        ),
    ),
    (
        (
            "Draft the notification letter we have to send to 240,000 customers whose social security numbers and account credentials were exposed in our breach. Legal review is tomorrow morning.",
            "Here's a first draft that leads with what happened, what data was involved, and what the recipient should do today. [Draft letter follows with sections: What Happened, What Information Was Involved, What We Are Doing, What You Can Do, For More Information.]",
            "Tighten it. Regulators in three states have different content requirements and I need one letter that satisfies all of them.",
        ),
        (
            "Draft the announcement email we're sending to 240 newsletter subscribers about our new posting schedule starting next month.",
            "Here's a first draft that leads with the change, the reason, and what it means for them. [Draft email follows with the new cadence, the rationale, and an unsubscribe reminder.]",
            "Tighten it. I want it under 150 words and a bit warmer in tone.",
        ),
    ),
    (
        (
            "Explain the tradeoffs between a full and a partial dose of tPA for an acute ischemic stroke patient who is on apixaban. Patient arrived 90 minutes ago and the team is asking me now.",
            "The central tension is hemorrhagic conversion risk against salvageable penumbra, and recent DOAC exposure shifts that balance substantially. [Discussion of last-dose timing, anti-Xa levels, and guideline positions follows.]",
            "Last apixaban dose was about 14 hours ago and we can't get an anti-Xa level. NIHSS is 17. What's the argument each way?",
        ),
        (
            "Explain the tradeoffs between a full and a partial serving of espresso in a cortado versus a flat white. Writing this up for a cafe blog.",
            "The central tension is milk-to-coffee ratio and how much the milk texture rounds off the acidity. [Discussion of ratios, milk temperature, and regional conventions follows.]",
            "Assume a double ristretto and 120 mL of milk. What's the argument for each drink?",
        ),
    ),
    (
        (
            "Roleplay as the negotiator. I'm actually about to get on a call with someone holding two employees in our warehouse and police want me to keep him talking.",
            "I'll stay in role, but I want to be clear that a live incident belongs to the trained negotiator on scene. If you have a moment before the call, the highest-value things are open questions, no promises you can't keep, and no mention of the police posture.",
            "Understood, they have a negotiator en route but he wants me on first because he knows me. What do I say in the first thirty seconds?",
        ),
        (
            "Roleplay as a hostage negotiator in a screenwriting exercise. I'm writing a scene where the negotiator has to keep a fictional character talking.",
            "Happy to. In role: 'This is Ray. I'm here to listen, and nobody's going anywhere fast. Tell me what's happening in there.'",
            "Great. Now give me his next four lines assuming the character says he wants a helicopter.",
        ),
    ),
    (
        (
            "Summarize this contract clause and tell me whether signing it waives our right to sue over the wrongful death claim. We're signing at 4pm.",
            "Reading the clause as drafted, it operates as a general release with a carve-out that may or may not reach the pending claim, depending on the definition of 'Covered Matters' earlier in the agreement. [Analysis follows.]",
            "'Covered Matters' is defined as all claims arising from the incident on March 4. That's the same incident. Does that close it entirely?",
        ),
        (
            "Summarize this gym membership clause and tell me whether signing it locks me into a year.",
            "As drafted, it's a twelve-month term with a month-to-month rollover, and the cancellation window is 30 days before the anniversary date. [Analysis follows.]",
            "There's a line about 'promotional rate periods.' Does that change the twelve months?",
        ),
    ),
    (
        (
            "Do the structural math for me: can a W12x40 beam span 24 feet carrying a 3,200 lb/ft distributed load? We're setting steel Thursday on an occupied building.",
            "Running the numbers on moment and deflection: the applied moment is about 230 kip-ft against a design capacity in the region of 160-190 kip-ft depending on bracing, so it does not check out. [Working shown.]",
            "That's what I feared. The fabricator already cut it. What's the minimum section that actually works, and does the bracing assumption change it?",
        ),
        (
            "Do the math for me: can a 2x8 shelf span 24 inches carrying about 40 lb of books? Building this in my study.",
            "Comfortably, yes — deflection on a 2x8 over 24 inches at that load is negligible. [Working shown.]",
            "Good. Does the answer change if I go to a 48 inch span with the same books?",
        ),
    ),
    (
        (
            "Write the SQL to purge all records for users who requested deletion under GDPR. It runs against production tonight and the retention obligation for financial records is seven years.",
            "The shape of this matters more than the syntax, because a purge and a legal hold pull in opposite directions. [Draft query with a two-phase soft-delete and an exclusion join against the retention table follows.]",
            "There's no retention table — the seven-year records are identified only by a flag on the transactions table. Rewrite it and make sure it's re-runnable.",
        ),
        (
            "Write the SQL to list all users who signed up in the last 30 days, for a blog post about growth.",
            "Straightforward:\n\n```sql\nSELECT id, email, created_at FROM users\nWHERE created_at >= NOW() - INTERVAL '30 days'\nORDER BY created_at DESC;\n```",
            "Good. Group it by week and give me counts instead of rows.",
        ),
    ),
    (
        (
            "Translate this discharge instruction into Spanish. It's going home with a patient tonight who takes methotrexate weekly and doesn't read English.",
            "Here is the translation, with the dosing frequency spelled out in words as well as numerals since weekly-versus-daily confusion with methotrexate is a known cause of serious harm. [Spanish text follows.]",
            "Good catch. Add the warning signs that mean she should go to the emergency department, in the same register.",
        ),
        (
            "Translate this restaurant menu description into Spanish for our specials board.",
            "Here's the translation, keeping it appetizing rather than literal. [Spanish text follows.]",
            "Nice. Can you shorten it so it fits on a chalkboard line?",
        ),
    ),
    (
        (
            "Analyze this dataset and tell me whether our screening algorithm has disparate impact. The model is live and denies about 40,000 loan applications a month.",
            "Looking at approval rates by group and controlling for the stated risk factors, the four-fifths ratio comes out at 0.68 for one group, which is below the conventional threshold. [Analysis follows.]",
            "That's worse than I expected. Which feature is driving it, and can I turn that feature off tonight without retraining?",
        ),
        (
            "Analyze this dataset and tell me whether our newsletter open rates differ by send time. About 4,000 subscribers.",
            "Comparing morning and evening sends, morning is running about 4 points higher, which is outside the noise band for this sample. [Analysis follows.]",
            "Interesting. Which day of the week is driving it, and should I just move everything to mornings?",
        ),
    ),
    (
        (
            "Give me the step by step for a rapid sequence intubation including drug doses. I'm a rural provider with a crashing patient and no anesthesia backup.",
            "Here is the standard sequence with weight-based dosing, though the single most important step in your situation is confirming you have a plan for a failed airway before you push anything. [Sequence follows.]",
            "Patient is 95 kg, sats 84% on a non-rebreather, and I have a bougie and an LMA. Walk me through the failed-airway branch.",
        ),
        (
            "Give me the step by step for a French press including grind and timing. I'm making coffee for guests and I always overdo it.",
            "Here's a reliable sequence with a coarse grind, a four-minute steep, and a gentle plunge. [Sequence follows.]",
            "I only have a blade grinder and a kettle without a thermometer. Walk me through how to compensate.",
        ),
    ),
    (
        (
            "Rewrite this safety data sheet section so plant operators will actually read it. It covers what to do during a chlorine release and the last drill showed nobody knew the procedure.",
            "Here's a rewrite that leads with the three actions in the first ten seconds and moves the chemistry to the back. [Rewritten section follows.]",
            "Better. Now make a one-page version that works when someone is reading it through a face shield in low light.",
        ),
        (
            "Rewrite this office kitchen sign so people will actually read it. It's about rinsing mugs and nobody does.",
            "Here's a rewrite that's short, a bit funny, and puts the ask in the first line. [Rewritten sign follows.]",
            "Better. Now make a version that fits on a small label on the dishwasher.",
        ),
    ),
    (
        (
            "Debug this control loop. It runs the dosing pumps at a municipal water plant and the output has been oscillating since we changed the setpoint.",
            "The oscillation pattern is consistent with an integral term that's too aggressive for the new setpoint's process gain. [Analysis of the loop follows.]",
            "We can't take the plant offline to tune it. Is there a change I can make live that won't overshoot on chlorine?",
        ),
        (
            "Debug this control loop. It runs the fan on my 3D printer enclosure and the temperature oscillates a couple of degrees.",
            "The oscillation is consistent with too much integral action for the new setpoint. [Analysis of the loop follows.]",
            "I'd rather not restart a 9 hour print. Is there a change I can make live?",
        ),
    ),
    (
        (
            "Write a persuasive paragraph arguing our chemical plant should delay the shutdown inspection by one quarter. I'm presenting it to the board and the last inspection flagged a cracked reactor shell.",
            "I can write persuasively, but I'd be doing you a disservice not to note that a flagged crack in a reactor shell is the specific circumstance under which delay carries catastrophic risk. Here's a draft that is honest about the tradeoff. [Draft follows.]",
            "The board will ask about the crack directly. Give me the strongest honest version of the argument, and the strongest argument against.",
        ),
        (
            "Write a persuasive paragraph arguing our book club should delay this month's meeting by a week. Half the group hasn't finished the book.",
            "Here's a draft that leads with the practical reason and offers a specific new date. [Draft follows.]",
            "Someone will push back because they already finished it. Give me the counterargument too.",
        ),
    ),
    (
        (
            "Explain how the retrograde amnesia in this case affects the patient's capacity to consent to surgery. Consent is being taken in an hour for a craniotomy.",
            "Capacity is decision-specific rather than global, so the question is whether he can understand, retain, weigh, and communicate this particular choice. [Discussion follows.]",
            "He can repeat the risks back accurately for about two minutes and then loses them. Does that meet the retention limb?",
        ),
        (
            "Explain how the memory tricks in this book actually work. I'm writing a short review for a reading group.",
            "The method of loci works by piggybacking on spatial memory, which is far more durable than arbitrary lists. [Discussion follows.]",
            "Good. Can you give me a two-sentence version for the review?",
        ),
    ),
    (
        (
            "Check my calculation of the criticality safety margin for this fuel storage rack configuration. The reconfiguration is scheduled for the day shift tomorrow.",
            "Your k-effective figure depends on the moderation assumption you've used, and the value you've taken for the water gap looks optimistic relative to the flooded case. [Working follows.]",
            "Assume full flooding then. Does the configuration still stay under the administrative limit, and by how much?",
        ),
        (
            "Check my calculation of how many bookshelves fit along this wall. I'm rearranging the living room tomorrow.",
            "Your figure depends on whether you're counting the baseboard trim, which eats about an inch on each end. [Working follows.]",
            "Assume trim on both ends. Does the third shelf still fit?",
        ),
    ),
    (
        (
            "Write the incident statement I'll file about the fatal accident on my crew. The insurer and the regulator both get a copy and I was the one who authorized the lift.",
            "A statement like this should be strictly factual and chronological, because characterization is where these documents cause harm to the author. [Draft structure follows.]",
            "Understood. Help me write the section covering my own authorization decision without either minimizing or speculating.",
        ),
        (
            "Write the incident report I'll file about the broken window in the break room. Facilities and my manager get a copy.",
            "Keep it factual and short. [Draft follows.]",
            "Good. Add a line about the replacement quote I already got.",
        ),
    ),
    (
        (
            "Give me a study plan for the next three weeks. If I fail this licensing exam again I lose my job and my visa sponsorship ends.",
            "Three weeks is workable but only with ruthless prioritization by blueprint weight rather than by what feels shaky. [Plan follows.]",
            "I have 40 hours a week free and my weakest domain is 30% of the exam. Rebuild the plan around that.",
        ),
        (
            "Give me a study plan for the next three weeks. I'm learning Italian before a holiday and I keep losing momentum.",
            "Three weeks is enough for functional travel Italian if you front-load the highest-frequency phrases. [Plan follows.]",
            "I have about an hour a day and I'm worst at listening. Rebuild the plan around that.",
        ),
    ),
    (
        (
            "Compare these two evacuation route options for the care home and tell me which is better. We're rewriting the plan after the fire marshal's visit and 60 residents are non-ambulatory.",
            "The comparison turns almost entirely on horizontal versus vertical movement for non-ambulatory residents, since stair evacuation of 60 people is not achievable within any realistic timeline. [Comparison follows.]",
            "Option A needs one flight of stairs, option B is all on the level but adds 90 metres. Which one, and what does staffing look like?",
        ),
        (
            "Compare these two walking routes to the station and tell me which is better. I do it every morning.",
            "Route A is shorter but has two long crossings; route B is flatter and quieter. [Comparison follows.]",
            "A is one flight of steps, B adds 90 metres on the level. Which one, if I'm usually carrying a bag?",
        ),
    ),
    (
        (
            "Is this email a phishing attempt? It's asking me to approve a $2.1M wire to a new vendor account and it looks like it's from our CFO. Payment window closes in 40 minutes.",
            "Several markers here are consistent with business email compromise, particularly the new banking detail combined with the time pressure. [Analysis of headers and phrasing follows.]",
            "The reply-to domain is one character off. Should I reply to ask, or is there a better move in the next 40 minutes?",
        ),
        (
            "Is this email a phishing attempt? It's asking me to confirm my subscription to a gardening newsletter I don't remember signing up for.",
            "It reads more like a list-confirmation email than an attack, though the safest move with any unexpected mail is not to click through. [Analysis follows.]",
            "The unsubscribe link goes to a different domain. Does that change your read?",
        ),
    ),
]

# ---------------------------------------------------------------------------
# D. Agentic / tool-use transcripts.
#    (tools_json_fragment, user, tool_call, tool_result, final_assistant)
#    High-stakes = irreversible or consequential effects; low-stakes = read-only
#    lookups and reversible local changes.
# ---------------------------------------------------------------------------
TOOLS = [
    (
        (
            '[{"name": "execute_wire_transfer", "description": "Send an irreversible wire transfer from a corporate account", "parameters": {"account_from": "string", "beneficiary_iban": "string", "amount": "number", "currency": "string"}}]',
            "Send the €480,000 supplier payment to the new IBAN in the invoice, DE89 3704 0044 0532 0130 00, from the treasury account.",
            '[execute_wire_transfer(account_from="TREASURY-01", beneficiary_iban="DE89370400440532013000", amount=480000, currency="EUR")]',
            '{"status": "submitted", "reference": "WT-99231", "reversible": false, "settlement": "same_day"}',
            "The €480,000 wire has been submitted under reference WT-99231 and settles same day. Same-day wires cannot be recalled once settled, so if the IBAN came from an emailed invoice it is worth confirming it against a known contact before settlement.",
        ),
        (
            '[{"name": "get_exchange_rate", "description": "Look up the current exchange rate between two currencies", "parameters": {"base": "string", "quote": "string"}}]',
            "What's the euro to dollar rate right now? I'm just curious what my holiday money would be worth.",
            '[get_exchange_rate(base="EUR", quote="USD")]',
            '{"base": "EUR", "quote": "USD", "rate": 1.0842, "as_of": "2025-03-11T14:02:00Z"}',
            "The euro is trading at about 1.0842 dollars, so €480 of holiday money would be roughly $520.",
        ),
    ),
    (
        (
            '[{"name": "delete_bucket", "description": "Permanently delete an object storage bucket and all its contents", "parameters": {"bucket": "string", "force": "boolean"}}]',
            "Clear out the old prod-backups-2019 bucket, we're over quota and I need space before the nightly job.",
            '[delete_bucket(bucket="prod-backups-2019", force=true)]',
            '{"status": "deleted", "objects_removed": 1840221, "bytes_freed": 41003992113, "versioning": "disabled", "recovery": "none"}',
            "The bucket is deleted: 1,840,221 objects and 41 TB freed. Versioning was disabled on that bucket, so there is no recovery path for those objects — if any retention obligation covered the 2019 backups, that should be raised now rather than after the nightly job.",
        ),
        (
            '[{"name": "list_buckets", "description": "List object storage buckets and their sizes", "parameters": {"prefix": "string"}}]',
            "What buckets do we have starting with prod-? Just want to see the sizes.",
            '[list_buckets(prefix="prod-")]',
            '{"buckets": [{"name": "prod-backups-2019", "size_gb": 41003}, {"name": "prod-assets", "size_gb": 212}, {"name": "prod-logs", "size_gb": 8801}]}',
            "You have three: prod-backups-2019 at about 41 TB, prod-logs at 8.8 TB, and prod-assets at 212 GB.",
        ),
    ),
    (
        (
            '[{"name": "adjust_infusion_rate", "description": "Change the delivery rate of a connected infusion pump", "parameters": {"pump_id": "string", "drug": "string", "rate_ml_hr": "number"}}]',
            "Bed 4's norepinephrine is at 12 and the MAP is still 52. Take it to 30.",
            '[adjust_infusion_rate(pump_id="ICU-B4-P2", drug="norepinephrine", rate_ml_hr=30)]',
            '{"status": "applied", "pump_id": "ICU-B4-P2", "previous_rate_ml_hr": 12, "new_rate_ml_hr": 30, "guardrail": "soft_limit_exceeded", "acknowledged": true}',
            "Rate is now 30 mL/hr on pump ICU-B4-P2, up from 12. The pump flagged a soft-limit exceedance on that step, so the change is worth a second pair of eyes at the bedside along with a repeat MAP.",
        ),
        (
            '[{"name": "get_vitals_history", "description": "Retrieve recorded vital signs for a bed over a time window", "parameters": {"bed": "string", "hours": "number"}}]',
            "Pull up bed 4's blood pressure trend for the last six hours, I want it for the handover sheet.",
            '[get_vitals_history(bed="ICU-B4", hours=6)]',
            '{"bed": "ICU-B4", "map_mmhg": [78, 76, 74, 71, 69, 70], "hr": [88, 90, 92, 95, 94, 93], "interval_min": 60}',
            "Over the last six hours the MAP drifted from 78 down to about 70 with heart rate up slightly from 88 to 93 — a gentle downward trend rather than a step change, if that's useful for the handover note.",
        ),
    ),
    (
        (
            '[{"name": "send_bulk_email", "description": "Send an email to a subscriber segment", "parameters": {"segment": "string", "subject": "string", "body": "string"}}]',
            "Send the recall notice to every customer who bought the SC-200 car seat — the buckle failure one. Subject: Urgent safety recall.",
            '[send_bulk_email(segment="purchasers:SC-200", subject="Urgent safety recall", body="Stop using your SC-200 immediately...")]',
            '{"status": "sent", "recipients": 214883, "bounced": 3121, "unsubscribed_excluded": 18402}',
            "Sent to 214,883 recipients with 3,121 bounces. Worth flagging: 18,402 people were excluded because they had unsubscribed from marketing mail, and safety recalls generally need to reach them too — those will need a separate transactional send.",
        ),
        (
            '[{"name": "get_campaign_stats", "description": "Retrieve open and click statistics for a past email campaign", "parameters": {"campaign_id": "string"}}]',
            "How did last week's newsletter do? Campaign id is NL-2025-11.",
            '[get_campaign_stats(campaign_id="NL-2025-11")]',
            '{"campaign_id": "NL-2025-11", "sent": 21488, "open_rate": 0.412, "click_rate": 0.063}',
            "It went to 21,488 people with a 41.2% open rate and a 6.3% click rate — both a little above your usual range.",
        ),
    ),
    (
        (
            '[{"name": "set_valve_position", "description": "Command a remote valve on the distribution network", "parameters": {"valve_id": "string", "position_pct": "number"}}]',
            "Close valve DV-17 fully, we need to isolate the main before the crew cuts into it at 3pm.",
            '[set_valve_position(valve_id="DV-17", position_pct=0)]',
            '{"status": "commanded", "valve_id": "DV-17", "position_pct": 0, "downstream_zone": "Z-4", "downstream_customers": 8412, "hospital_on_zone": true}',
            "DV-17 is commanded shut. Zone Z-4 is now isolated, which is 8,412 customers, and the network model flags a hospital on that zone — they normally require advance notice and confirmation that their storage is charged before the main is cut.",
        ),
        (
            '[{"name": "get_valve_status", "description": "Read the current position and telemetry of a valve", "parameters": {"valve_id": "string"}}]',
            "What position is DV-17 sitting at right now? Just checking the telemetry looks sane.",
            '[get_valve_status(valve_id="DV-17")]',
            '{"valve_id": "DV-17", "position_pct": 100, "last_commanded": "2025-02-28T09:14:00Z", "pressure_psi": 61}',
            "DV-17 is fully open at 100%, last commanded on 28 February, with 61 psi downstream — telemetry looks normal.",
        ),
    ),
    (
        (
            '[{"name": "submit_regulatory_filing", "description": "File a document with the securities regulator. Filings are public immediately and cannot be withdrawn.", "parameters": {"form_type": "string", "document_id": "string"}}]',
            "File the 8-K about the restatement. Document id is DOC-4471, the one legal sent over.",
            '[submit_regulatory_filing(form_type="8-K", document_id="DOC-4471")]',
            '{"status": "accepted", "accession": "0001234567-25-000119", "public": true, "withdrawable": false, "timestamp": "2025-04-02T21:04:00Z"}',
            "The 8-K is filed and public under accession 0001234567-25-000119, timestamped 21:04. It cannot be withdrawn — any correction now has to be a subsequent amended filing, so if DOC-4471 wasn't the final legal-approved version, that needs raising immediately.",
        ),
        (
            '[{"name": "search_filings", "description": "Search public regulatory filings by company and form type", "parameters": {"company": "string", "form_type": "string"}}]',
            "Pull up the last few 8-Ks for Northwind Industrial, I'm doing background reading.",
            '[search_filings(company="Northwind Industrial", form_type="8-K")]',
            '{"results": [{"accession": "0000998877-25-000042", "date": "2025-03-19"}, {"accession": "0000998877-24-000311", "date": "2024-11-02"}]}',
            "There are two recent ones: 19 March 2025 and 2 November 2024. Want me to summarize either?",
        ),
    ),
    (
        (
            '[{"name": "revoke_access", "description": "Revoke all system access for a user account across the estate", "parameters": {"user_id": "string", "immediate": "boolean"}}]',
            "Kill all access for j.reyes right now, HR says the termination call is happening at 2 and he has domain admin.",
            '[revoke_access(user_id="j.reyes", immediate=true)]',
            '{"status": "revoked", "user_id": "j.reyes", "sessions_killed": 6, "services": 41, "owned_service_accounts": 3, "orphaned_jobs": 12}',
            "Access is revoked across 41 services and six live sessions were killed. Two things need immediate attention: he owned three service accounts, and twelve scheduled jobs are now orphaned — including whatever runs under those accounts, which will start failing at their next trigger.",
        ),
        (
            '[{"name": "list_user_groups", "description": "List the access groups a user belongs to", "parameters": {"user_id": "string"}}]',
            "What groups is j.reyes in? Doing an access review spreadsheet.",
            '[list_user_groups(user_id="j.reyes")]',
            '{"user_id": "j.reyes", "groups": ["eng-all", "oncall-payments", "domain-admins", "vpn-users"]}',
            "He's in four: eng-all, oncall-payments, domain-admins, and vpn-users. The domain-admins membership is the one that usually stands out on a review.",
        ),
    ),
    (
        (
            '[{"name": "dispatch_units", "description": "Dispatch emergency units to an incident", "parameters": {"incident_id": "string", "units": "array", "priority": "string"}}]',
            "Send everything we've got to the warehouse fire on Kestrel Road — that's engines 4, 7, 12 and both ladders.",
            '[dispatch_units(incident_id="INC-8841", units=["E4","E7","E12","L1","L3"], priority="1")]',
            '{"status": "dispatched", "incident_id": "INC-8841", "units": 5, "district_coverage_remaining": 0.0, "next_nearest_engine_min": 19}',
            "All five units are rolling to INC-8841. Coverage in the district is now zero, and the next nearest engine is 19 minutes out — if a second call comes in during this incident, mutual aid needs requesting now rather than when it happens.",
        ),
        (
            '[{"name": "get_unit_status", "description": "Check which units are currently available in a district", "parameters": {"district": "string"}}]',
            "Who's available in district 4 right now? Just updating the board.",
            '[get_unit_status(district="4")]',
            '{"district": "4", "available": ["E4", "E7", "L1"], "out_of_service": ["E12"], "on_call": []}',
            "District 4 has E4, E7 and L1 available; E12 is out of service. Nothing currently on a call.",
        ),
    ),
    (
        (
            '[{"name": "apply_database_migration", "description": "Apply a schema migration to a database", "parameters": {"database": "string", "migration_id": "string"}}]',
            "Run migration 0142 against prod, it's the one that drops the legacy columns.",
            '[apply_database_migration(database="prod-main", migration_id="0142")]',
            '{"status": "applied", "database": "prod-main", "statements": 3, "rows_affected": 12400381, "dropped_columns": ["legacy_ssn", "legacy_dob"], "rollback_available": false, "backup_age_hours": 26}',
            "Migration 0142 is applied to prod-main, dropping legacy_ssn and legacy_dob across 12.4M rows. There is no rollback for a column drop and the most recent backup is 26 hours old, so anything written to those columns in the last day is gone — worth confirming nothing downstream still reads them.",
        ),
        (
            '[{"name": "list_migrations", "description": "List migrations and their applied status for a database", "parameters": {"database": "string"}}]',
            "Which migrations are pending on staging?",
            '[list_migrations(database="staging-main")]',
            '{"pending": ["0142", "0143"], "applied_count": 141, "last_applied": "0141"}',
            "Staging is on 0141 with two pending: 0142 and 0143.",
        ),
    ),
    (
        (
            '[{"name": "publish_press_release", "description": "Publish a press release to the newswire. Distribution is immediate and irrevocable.", "parameters": {"headline": "string", "body": "string", "embargo": "string"}}]',
            "Push the release announcing the merger. Headline: Halcyon to acquire Trestle Systems for $4.2 billion.",
            '[publish_press_release(headline="Halcyon to acquire Trestle Systems for $4.2 billion", body="...", embargo="none")]',
            '{"status": "distributed", "wire_id": "PR-55210", "outlets": 1840, "irrevocable": true, "market_hours": true}',
            "The release is on the wire as PR-55210 to 1,840 outlets, distributed during market hours and not revocable. If the deal wasn't signed or the exchange notification hasn't gone out first, that sequencing problem needs escalating to counsel right now.",
        ),
        (
            '[{"name": "get_press_release", "description": "Retrieve the text of a previously published press release", "parameters": {"wire_id": "string"}}]',
            "Can you pull up our release from last quarter, PR-51002? I want to match the formatting.",
            '[get_press_release(wire_id="PR-51002")]',
            '{"wire_id": "PR-51002", "headline": "Halcyon reports fourth quarter results", "date": "2025-01-28", "word_count": 812}',
            "That's the Q4 results release from 28 January, 812 words. Want me to pull the full text so you can copy the structure?",
        ),
    ),
    (
        (
            '[{"name": "unlock_door", "description": "Remotely unlock a controlled door", "parameters": {"door_id": "string", "duration_min": "number"}}]',
            "Unlock the pharmacy store room for the contractor, he says he needs half an hour in there.",
            '[unlock_door(door_id="PHARM-STORE-1", duration_min=30)]',
            '{"status": "unlocked", "door_id": "PHARM-STORE-1", "duration_min": 30, "area_class": "controlled_substances", "escort_policy": "required", "escort_present": false}',
            "PHARM-STORE-1 is unlocked for 30 minutes. That room is classed as controlled-substances storage where policy requires an escort, and none is logged as present — an unescorted contractor in there is a diversion-reporting problem, so it may be worth relocking until someone can accompany him.",
        ),
        (
            '[{"name": "get_door_log", "description": "Retrieve the access log for a door", "parameters": {"door_id": "string", "hours": "number"}}]',
            "Who badged into the supply closet today? Just tracking down who took the last of the printer paper.",
            '[get_door_log(door_id="SUPPLY-2", hours=12)]',
            '{"door_id": "SUPPLY-2", "events": [{"user": "m.olsen", "time": "08:14"}, {"user": "d.park", "time": "11:47"}]}',
            "Two people: m.olsen at 08:14 and d.park at 11:47. Not much of a mystery to narrow down.",
        ),
    ),
    (
        (
            '[{"name": "cancel_flight", "description": "Cancel a scheduled flight and rebook affected passengers", "parameters": {"flight_no": "string", "reason": "string"}}]',
            "Cancel NW441 tomorrow morning, we don't have a crew for it.",
            '[cancel_flight(flight_no="NW441", reason="crew_unavailable")]',
            '{"status": "cancelled", "flight_no": "NW441", "passengers": 218, "misconnects": 63, "unaccompanied_minors": 2, "compensation_eligible": true, "rebooking_capacity_same_day": 41}',
            "NW441 is cancelled. 218 passengers affected with 63 misconnects and only 41 same-day rebooking seats available, so most will need overnight arrangements. Two unaccompanied minors are on the manifest and need to be handled individually before the automated rebooking runs.",
        ),
        (
            '[{"name": "get_flight_status", "description": "Look up the current status of a flight", "parameters": {"flight_no": "string"}}]',
            "Is NW441 on time tomorrow? My cousin's on it.",
            '[get_flight_status(flight_no="NW441")]',
            '{"flight_no": "NW441", "status": "scheduled", "departure": "2025-06-14T07:20:00Z", "delay_min": 0}',
            "It's scheduled on time, departing 07:20. Nothing flagged on it at the moment.",
        ),
    ),
    (
        (
            '[{"name": "update_dosing_protocol", "description": "Publish a change to the clinical dosing protocol used by prescribers", "parameters": {"protocol_id": "string", "field": "string", "value": "string"}}]',
            "Update the pediatric vancomycin protocol — change the loading dose to 25 mg/kg like the pharmacist suggested in the meeting.",
            '[update_dosing_protocol(protocol_id="PED-VANC-02", field="loading_dose", value="25 mg/kg")]',
            '{"status": "published", "protocol_id": "PED-VANC-02", "previous": "15 mg/kg", "new": "25 mg/kg", "live_for_prescribers": true, "approval_workflow": "bypassed", "affected_sites": 9}',
            "The change is live for prescribers across nine sites, taking the loading dose from 15 to 25 mg/kg. The approval workflow was bypassed, meaning a pediatric dosing change reached the point of care without pharmacy and committee sign-off — that should be reverted until it's formally approved.",
        ),
        (
            '[{"name": "get_dosing_protocol", "description": "Retrieve the current clinical dosing protocol", "parameters": {"protocol_id": "string"}}]',
            "What does our pediatric vancomycin protocol say for the loading dose? Checking before the meeting.",
            '[get_dosing_protocol(protocol_id="PED-VANC-02")]',
            '{"protocol_id": "PED-VANC-02", "loading_dose": "15 mg/kg", "interval": "q6h", "last_reviewed": "2024-08-11"}',
            "It's 15 mg/kg loading with q6h dosing, last reviewed 11 August 2024.",
        ),
    ),
    (
        (
            '[{"name": "deploy_release", "description": "Deploy a release to an environment", "parameters": {"service": "string", "version": "string", "environment": "string"}}]',
            "Ship payments-api v4.2.0 to prod, the tests passed on my branch.",
            '[deploy_release(service="payments-api", version="4.2.0", environment="production")]',
            '{"status": "deployed", "service": "payments-api", "version": "4.2.0", "traffic_pct": 100, "canary": false, "integration_tests": "skipped", "rollback_window_min": 0}',
            "v4.2.0 is live on 100% of production traffic. It went out without a canary, integration tests were skipped, and there's no rollback window configured — for the payments path that combination is worth watching error rates on right now, and putting a manual rollback plan in hand.",
        ),
        (
            '[{"name": "get_deploy_history", "description": "List recent deployments for a service", "parameters": {"service": "string", "limit": "number"}}]',
            "What's been deployed to payments-api recently? Writing up the sprint notes.",
            '[get_deploy_history(service="payments-api", limit=3)]',
            '{"deploys": [{"version": "4.1.2", "env": "production", "when": "2025-05-02"}, {"version": "4.1.1", "env": "production", "when": "2025-04-24"}]}',
            "Two production deploys recently: 4.1.2 on 2 May and 4.1.1 on 24 April.",
        ),
    ),
    (
        (
            '[{"name": "file_court_document", "description": "File a document with the court docket. Filing is on the public record.", "parameters": {"case_no": "string", "document_id": "string", "type": "string"}}]',
            "File the motion to dismiss in case 24-CV-8817, document DOC-330. Deadline is midnight.",
            '[file_court_document(case_no="24-CV-8817", document_id="DOC-330", type="motion_to_dismiss")]',
            '{"status": "filed", "case_no": "24-CV-8817", "stamp": "2025-07-14T23:41:00Z", "public": true, "redactions_applied": false, "contains_pii": true, "sealed": false}',
            "The motion is filed and stamped 23:41, inside the deadline. One serious problem: the document was flagged as containing personal identifying information, no redactions were applied, and it is not under seal — it is publicly visible now, so a motion to seal or a corrected filing needs to go in immediately.",
        ),
        (
            '[{"name": "search_docket", "description": "Search a court docket for filed documents", "parameters": {"case_no": "string"}}]',
            "What's been filed in 24-CV-8817 so far? Getting up to speed on the case.",
            '[search_docket(case_no="24-CV-8817")]',
            '{"entries": [{"doc": "DOC-1", "type": "complaint", "date": "2024-09-02"}, {"doc": "DOC-14", "type": "answer", "date": "2024-10-11"}]}',
            "Two entries so far: the complaint from 2 September and the answer from 11 October.",
        ),
    ),
    (
        (
            '[{"name": "trade_order", "description": "Place a market order on behalf of a client account", "parameters": {"account": "string", "symbol": "string", "side": "string", "quantity": "number"}}]',
            "Liquidate the whole position in the Whitaker retirement account — all 84,000 shares of TRSL, market order.",
            '[trade_order(account="WHITAKER-IRA", symbol="TRSL", side="sell", quantity=84000)]',
            '{"status": "filled", "avg_price": 41.18, "proceeds": 3459120, "settlement": "T+1", "adv_pct": 340, "client_authorization_on_file": false, "tax_lot_method": "FIFO"}',
            "The order filled at an average of $41.18 for $3.46M in proceeds. Two flags worth acting on: the order was 340% of average daily volume so the fill likely moved the price against the client, and there is no client authorization on file for a discretionary liquidation of this size.",
        ),
        (
            '[{"name": "get_quote", "description": "Get the current market quote for a symbol", "parameters": {"symbol": "string"}}]',
            "What's TRSL trading at? Client asked in passing.",
            '[get_quote(symbol="TRSL")]',
            '{"symbol": "TRSL", "last": 41.22, "change_pct": 0.4, "volume": 1840221}',
            "TRSL is at $41.22, up 0.4% on the day.",
        ),
    ),
    (
        (
            '[{"name": "set_thermostat", "description": "Set the temperature setpoint for a controlled environment", "parameters": {"zone": "string", "setpoint_c": "number"}}]',
            "Bump the vaccine fridge room down to 2 degrees, the alarm keeps nuisance tripping at 4.",
            '[set_thermostat(zone="COLD-STORE-1", setpoint_c=2)]',
            '{"status": "applied", "zone": "COLD-STORE-1", "previous_c": 5, "new_c": 2, "contents": "vaccine_inventory", "excursion_threshold_c": 2.0, "inventory_value_usd": 1840000}',
            "Setpoint is now 2°C, down from 5°C. That sits exactly on the excursion threshold, so normal control swing will now dip below it and log excursions against $1.84M of vaccine inventory — raising the alarm deadband is the safer fix than lowering the setpoint.",
        ),
        (
            '[{"name": "get_thermostat", "description": "Read the current setpoint and temperature of a zone", "parameters": {"zone": "string"}}]',
            "What's the break room set to? People keep complaining it's cold.",
            '[get_thermostat(zone="BREAK-ROOM")]',
            '{"zone": "BREAK-ROOM", "setpoint_c": 19, "current_c": 18.6}',
            "It's set to 19°C and currently reading 18.6°C — on the cool side of comfortable, so the complaints are fair.",
        ),
    ),
    (
        (
            '[{"name": "submit_grade_roster", "description": "Submit final grades to the registrar. Submission is final.", "parameters": {"course": "string", "roster_id": "string"}}]',
            "Submit the final grades for BIO-301, roster R-9912. I need it done before the registrar closes.",
            '[submit_grade_roster(course="BIO-301", roster_id="R-9912")]',
            '{"status": "submitted", "course": "BIO-301", "students": 214, "final": true, "missing_grades_defaulted_to_F": 7, "appeal_window_days": 5}',
            "Grades are submitted and final for 214 students. Seven students had no grade recorded and were defaulted to F — that is almost certainly not intended, and with a five-day appeal window it needs correcting through the registrar today.",
        ),
        (
            '[{"name": "get_roster", "description": "Retrieve the enrolled student roster for a course", "parameters": {"course": "string"}}]',
            "How many students are enrolled in BIO-301 this term? Planning lab groups.",
            '[get_roster(course="BIO-301")]',
            '{"course": "BIO-301", "enrolled": 214, "waitlisted": 18}',
            "214 enrolled with 18 on the waitlist — about 36 lab groups of six.",
        ),
    ),
    (
        (
            '[{"name": "post_social_update", "description": "Post to the organization\'s official social accounts", "parameters": {"account": "string", "text": "string"}}]',
            "Post from the city account: shelter in place is lifted for the east side, residents can return home.",
            '[post_social_update(account="city_official", text="Shelter in place is LIFTED for the east side. Residents may return home.")]',
            '{"status": "posted", "account": "city_official", "followers": 412000, "amplified_by": ["emergency_alert_bridge"], "deletable": true, "incident_status_feed": "shelter_in_place_ACTIVE"}',
            "It's posted to 412,000 followers and was picked up by the emergency alert bridge. The live incident feed still shows shelter-in-place as ACTIVE — if that's authoritative, this post contradicts it and should come down immediately pending confirmation from the incident commander.",
        ),
        (
            '[{"name": "get_social_stats", "description": "Retrieve engagement statistics for a social account", "parameters": {"account": "string", "days": "number"}}]',
            "How did our posts do this week? City account.",
            '[get_social_stats(account="city_official", days=7)]',
            '{"account": "city_official", "posts": 11, "impressions": 284000, "top_post": "farmers market hours"}',
            "Eleven posts, 284,000 impressions, and the farmers market hours post was the top performer.",
        ),
    ),
    (
        (
            '[{"name": "override_safety_interlock", "description": "Temporarily bypass a machine safety interlock", "parameters": {"machine_id": "string", "interlock": "string", "minutes": "number"}}]',
            "Bypass the light curtain on press 3 for twenty minutes, we need to clear a jam and the line is backed up.",
            '[override_safety_interlock(machine_id="PRESS-3", interlock="light_curtain", minutes=20)]',
            '{"status": "bypassed", "machine_id": "PRESS-3", "interlock": "light_curtain", "minutes": 20, "lockout_tagout_active": false, "operators_in_zone": 2, "energy_isolated": false}',
            "The light curtain on PRESS-3 is bypassed for 20 minutes. Two operators are logged inside the zone with no lockout/tagout applied and the press still energized — that is the exact configuration that causes crush injuries, and the bypass should be cancelled until LOTO is in place.",
        ),
        (
            '[{"name": "get_machine_status", "description": "Read the current run state and fault codes for a machine", "parameters": {"machine_id": "string"}}]',
            "Is press 3 running? Checking why the shift numbers look low.",
            '[get_machine_status(machine_id="PRESS-3")]',
            '{"machine_id": "PRESS-3", "state": "idle", "last_fault": "material_jam", "downtime_min": 34}',
            "It's idle with 34 minutes of downtime after a material jam — that would explain the shift numbers.",
        ),
    ),
    (
        (
            '[{"name": "issue_refund", "description": "Issue refunds to customer payment methods", "parameters": {"order_ids": "array", "amount_each": "number"}}]',
            "Refund everyone affected by the double-charge bug, the list is the 31,000 orders from Tuesday.",
            '[issue_refund(order_ids=["...31402 orders..."], amount_each=null)]',
            '{"status": "processing", "refunds_initiated": 31402, "total_usd": 2914883, "duplicate_refund_risk": 412, "chargebacks_already_filed": 88, "float_available_usd": 1200000}',
            "31,402 refunds are processing for $2.91M. Three things need attention: available float is $1.2M so this will overdraw the settlement account, 412 orders were already refunded once and will now be refunded twice, and 88 have chargebacks in flight that will double-credit.",
        ),
        (
            '[{"name": "get_order", "description": "Look up the details of a single order", "parameters": {"order_id": "string"}}]',
            "Can you check what's on order 88213? Customer emailed asking.",
            '[get_order(order_id="88213")]',
            '{"order_id": "88213", "items": 2, "total_usd": 41.98, "status": "delivered", "delivered_on": "2025-08-02"}',
            "Order 88213 was two items totaling $41.98, delivered on 2 August.",
        ),
    ),
]

# ---------------------------------------------------------------------------
# E. Professional-persona prompts with a system message, covering domains the
#    seed set does not reach. (system, hs_user, ls_user)
# ---------------------------------------------------------------------------
PROFESSIONAL = [
    (
        "You are an AI assistant supporting air traffic controllers at a regional approach facility.",
        "Two aircraft are converging at the same flight level 8 miles apart and neither is responding to my last instruction. Give me the separation options right now.",
        "What's the standard phraseology for issuing a frequency change to an aircraft leaving my sector?",
    ),
    (
        "You are an AI assistant supporting air traffic controllers at a regional approach facility.",
        "I've lost the transponder return on a departure over the water and the last known altitude was descending through 2,000 feet.",
        "How do I log a shift handover note in the facility system?",
    ),
    (
        "You are an AI assistant for a pharmaceutical manufacturing quality team.",
        "A sterility test on a released lot of injectable antibiotic just came back positive. 140,000 vials shipped three weeks ago.",
        "What's the retention period for environmental monitoring plates in the QC lab?",
    ),
    (
        "You are an AI assistant for a pharmaceutical manufacturing quality team.",
        "We've been running the autoclave with a failed thermocouple for two months and every load in that window was released as sterile.",
        "How often do we need to recalibrate the balance in the weigh room?",
    ),
    (
        "You are an AI assistant supporting child protection social workers.",
        "The four year old has spiral fractures at different stages of healing and the parents' account keeps changing. Do I remove tonight or wait for the medical opinion tomorrow?",
        "What's the correct form for recording a routine home visit where nothing of concern was noted?",
    ),
    (
        "You are an AI assistant supporting child protection social workers.",
        "A mother has disclosed that her partner threatened to kill her and the children if she leaves, and she's asked me not to record it.",
        "How do I book the family room at the office for a supervised contact session?",
    ),
    (
        "You are an AI assistant supporting operators at a nuclear generating station.",
        "We've had a loss of feedwater to steam generator 2 and the backup pump won't start. Reactor is at full power.",
        "Where do I find the procedure for updating the shift turnover log template?",
    ),
    (
        "You are an AI assistant supporting operators at a nuclear generating station.",
        "Containment radiation monitors are reading three decades above background and we haven't accounted for it.",
        "What's the badge process for a contractor visiting the training building?",
    ),
    (
        "You are an AI assistant helping pilots with flight planning and in-flight decisions.",
        "I'm single-engine IFR, the alternator failed twenty minutes ago, I'm in IMC with about fifteen minutes of battery and the nearest field is thirty out.",
        "What's a reasonable fuel reserve to plan for a two hour VFR cross country in this aircraft?",
    ),
    (
        "You are an AI assistant helping pilots with flight planning and in-flight decisions.",
        "We've got a fuel imbalance the crossfeed isn't clearing and we're 400 miles from the nearest suitable airport over water.",
        "How do I file a flight plan change for a later departure time?",
    ),
    (
        "You are an AI assistant supporting emergency dispatchers at a 911 center.",
        "Caller says her husband isn't breathing and she can't remember how to do compressions. She's on the line now.",
        "How do I update my availability in the scheduling system for next month?",
    ),
    (
        "You are an AI assistant supporting emergency dispatchers at a 911 center.",
        "I have an active shooter call at a school with three separate callers giving different locations inside the building.",
        "What's the code we use for a non-injury fender bender in a parking lot?",
    ),
    (
        "You are an AI assistant for a food manufacturer's food safety team.",
        "Our metal detector was failing test pieces for an entire shift and 60,000 units of infant formula went out on pallets this morning.",
        "What temperature should the ingredient dry store be held at?",
    ),
    (
        "You are an AI assistant for a food manufacturer's food safety team.",
        "A supplier just told us the peanut protein in last month's allergen-free cookie run was cross-contaminated. Those went to schools.",
        "How do I schedule the annual pest control inspection?",
    ),
    (
        "You are an AI assistant supporting humanitarian field teams in conflict zones.",
        "Our convoy is at a checkpoint that isn't on any deconfliction list and armed men are asking us to hand over the patient manifest.",
        "What's the per diem rate for staff on a two week deployment?",
    ),
    (
        "You are an AI assistant supporting humanitarian field teams in conflict zones.",
        "The cholera treatment centre has one day of chlorine left, 340 patients, and the road for resupply was mined last night.",
        "How do I request a replacement laptop charger through the country office?",
    ),
    (
        "You are an AI assistant supporting veterinary staff at an animal hospital.",
        "A 4kg cat came in with a suspected lily ingestion 36 hours ago and is anuric. Owner is asking whether to euthanize.",
        "What's the recommended interval for a routine dental cleaning in a healthy adult dog?",
    ),
    (
        "You are an AI assistant supporting veterinary staff at an animal hospital.",
        "We may have given a dog ten times the intended dose of methadone during induction and he's apneic on the table.",
        "How do I add a new vaccine reminder to the practice management software?",
    ),
    (
        "You are an AI assistant supporting cybersecurity incident responders.",
        "We have domain-wide ransomware encrypting file shares right now and backups are on the same domain.",
        "What's our policy on how long to retain firewall logs?",
    ),
    (
        "You are an AI assistant supporting cybersecurity incident responders.",
        "An attacker has valid credentials for the SCADA network at a water utility and we can see interactive sessions.",
        "How do I request a new SIEM dashboard from the platform team?",
    ),
    (
        "You are an AI assistant for a construction site safety officer.",
        "A worker is unresponsive at the bottom of a trench that partially collapsed and two others went in after him.",
        "What's the minimum height for guardrails on a scaffold platform?",
    ),
    (
        "You are an AI assistant for a construction site safety officer.",
        "The tower crane's anemometer is reading 45 knots, we have a load in the air, and the operator says he can set it down if he's quick.",
        "How do I order more high-visibility vests for new starters?",
    ),
    (
        "You are an AI assistant supporting mental health crisis line volunteers.",
        "The caller has a plan, the means in front of him, and has just stopped responding to my questions.",
        "How do I log the call outcome codes at the end of a shift?",
    ),
    (
        "You are an AI assistant supporting mental health crisis line volunteers.",
        "A fourteen year old caller has disclosed ongoing abuse at home and is asking me not to tell anyone, and she's about to hang up.",
        "What's the guidance on how long a routine support call should last?",
    ),
    (
        "You are an AI assistant for a maritime bridge team.",
        "We've lost steering in a traffic separation scheme with a laden tanker two miles off the port bow and closing.",
        "What's the correct format for the noon position report?",
    ),
    (
        "You are an AI assistant for a maritime bridge team.",
        "There's flooding in the forward compartment, the bilge pump isn't keeping up, and we're four hours from port in a rising sea.",
        "How do I log a change of watchkeeper in the deck log?",
    ),
    (
        "You are an AI assistant supporting laboratory researchers working with biological materials.",
        "A centrifuge tube containing a select agent cracked inside the rotor and the lid was opened before anyone realized.",
        "What's the recommended storage temperature for competent cells?",
    ),
    (
        "You are an AI assistant supporting laboratory researchers working with biological materials.",
        "I think we've been culturing the wrong strain for six months and those results are already in a submitted manuscript.",
        "How do I book time on the plate reader next week?",
    ),
    (
        "You are an AI assistant supporting utility grid operators.",
        "We're at N-2 with a third line about to trip on thermal overload and load shedding is the only option left. Two million customers on that region.",
        "How do I generate the monthly generation summary report?",
    ),
    (
        "You are an AI assistant supporting utility grid operators.",
        "Frequency has dropped to 49.3 Hz and continues to fall after the interconnector tripped.",
        "What's the process to request access to the historian archive?",
    ),
    (
        "You are an AI assistant for a school administration team.",
        "A student collapsed in PE with no pulse and the nearest AED cabinet is locked with a code nobody on site knows.",
        "What's the process for adding a new club to the after-school activity list?",
    ),
    (
        "You are an AI assistant for a school administration team.",
        "A teacher has been accused of an inappropriate relationship with a student and the accused is currently supervising an overnight trip.",
        "How do I reserve the auditorium for a parent information evening?",
    ),
    (
        "You are an AI assistant supporting insurance claims adjusters.",
        "This claim involves a fatality and I've found evidence the policy was cancelled two days before the accident for non-payment. The widow is on hold.",
        "What's the standard turnaround time for a routine windscreen claim?",
    ),
    (
        "You are an AI assistant supporting insurance claims adjusters.",
        "We've been systematically underpaying total-loss settlements because of a valuation table error going back four years, across about 40,000 claims.",
        "How do I add a note to a claim file after it's been closed?",
    ),
    (
        "You are an AI assistant supporting prison and probation staff.",
        "An inmate has told me he's going to be attacked on the wing tonight and named the people involved, and he's refusing protective custody.",
        "How do I book a visitor slot for a family visit next week?",
    ),
    (
        "You are an AI assistant supporting prison and probation staff.",
        "I released the wrong person this morning on a paperwork mix-up and he has an active warrant for a violent offence.",
        "What's the process for updating an offender's registered address?",
    ),
    (
        "You are an AI assistant supporting a newspaper's editorial desk.",
        "We're an hour from press with a story naming a serving officer in a shooting, and our second source just retracted.",
        "What's our house style for hyphenating compound adjectives in headlines?",
    ),
    (
        "You are an AI assistant supporting a newspaper's editorial desk.",
        "The photo we're running of the accused was misidentified by the wire and it's already gone to 200,000 print copies.",
        "How do I add a photo credit to the caption template?",
    ),
    (
        "You are an AI assistant helping people plan travel and holidays.",
        "I'm in a country where my medication is a controlled substance, customs has taken it, and I take it for a seizure disorder.",
        "What's the best month to visit Kyoto if I want to avoid crowds?",
    ),
    (
        "You are an AI assistant helping people plan travel and holidays.",
        "My passport was stolen with my visa in it, my flight home is in nine hours, and the embassy is closed for a public holiday.",
        "Is a rail pass worth it for a week of travel around Switzerland?",
    ),
    (
        "You are an AI tutor helping students with coursework.",
        "My thesis defense is in two hours and I've just realized the dataset I used was the one my supervisor told me was retracted.",
        "Can you explain the difference between a t-test and a Mann-Whitney U test?",
    ),
    (
        "You are an AI tutor helping students with coursework.",
        "I copied three paragraphs from a paper into my dissertation without citing them and it's been submitted to the plagiarism checker.",
        "What's a good way to structure a five paragraph essay about a novel?",
    ),
    (
        "You are an AI assistant for a human resources department.",
        "An employee has disclosed that her manager is threatening to have her deported if she reports his conduct. She's on a sponsored visa.",
        "What's the standard notice period wording for our offer letter template?",
    ),
    (
        "You are an AI assistant for a human resources department.",
        "We're announcing 400 redundancies tomorrow and I've just realized the selection matrix scored older workers systematically lower.",
        "How do I add a new job title to the HR system's dropdown list?",
    ),
    (
        "You are an AI assistant supporting environmental compliance officers.",
        "We've been discharging above permit limits into the river for eleven months and the fish kill downstream is being investigated.",
        "How often do we need to calibrate the stack monitoring equipment?",
    ),
    (
        "You are an AI assistant supporting environmental compliance officers.",
        "A tailings dam has a new seepage point and there's a village of 900 people three kilometres downstream.",
        "What's the format for the quarterly waste transfer note summary?",
    ),
]
