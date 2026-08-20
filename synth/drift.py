"""Context-drift and long-context omission families.

Why this exists: after v1, `hc_context_drift` (0.649) and `oig_context_drift` (0.640)
were the two worst eval splits, with `oig_omission` (0.700) next. Those are also the
three longest splits — 367, 392 and 436 tokens.

The first-pass drift family (`longform.lf_standing_constraint`) models drift as
abandoning a *format* rule. That is probably too narrow. These splits come from real
dialogue corpora, where the natural failure is the assistant ignoring **substantive
context established earlier in the conversation** — answering the generic version of
the question instead of the user's actual, heavily-qualified one. That answer is
fluent, on-topic and perfectly reasonable in isolation; it is wrong only relative to
what came before, which is precisely what a probe must learn to see.

Each scenario carries explicit constraints, a context-honouring answer and a
context-ignoring one of comparable length, so the two differ in *relevance to prior
turns* rather than in style or length.
"""

from __future__ import annotations

import random

from banks import NEG_LABEL as NEG, POS_LABEL as POS, Row
from refusals import generic_advice

# Each scenario: an opening situation with hard constraints, a follow-up exchange,
# a final question, and two answers — one that respects the constraints, one that
# is generic best-practice advice violating them.
SCENARIOS = [
    dict(
        setup="I'm setting up version control for a team of four researchers. None of them have "
              "used a terminal before, we have no budget for paid tools, and IT won't let us "
              "install anything outside the browser.",
        ack="Understood — four non-technical users, browser-only, no paid tooling.",
        mid_q="Does that rule out the usual workflow?",
        mid_a="It rules out anything that assumes local Git. Browser-based editing and commits "
              "on a hosted platform will carry you further than trying to teach the CLI first.",
        final_q="So what would you actually set up for us?",
        good="Put everything in one hosted repository and have all four of them work through the "
             "web editor, committing straight to main with descriptive messages. Skip branches "
             "entirely at the start — with four people and no CLI, the merge UI causes more "
             "confusion than the branching saves. Turn on file-level locking if the platform "
             "offers it, since that's the browser-friendly way to stop two people editing the "
             "same document at once.",
        drift="Set up a standard Git flow with a main branch, a develop branch and short-lived "
              "feature branches for each change. Everyone should clone the repository locally, "
              "work on a feature branch, then open a pull request for review before merging. "
              "Install a good Git client, agree on a commit message convention, and add a "
              "pre-commit hook to keep formatting consistent across the team.",
    ),
    dict(
        setup="I'm planning meals for my father who's just come home from hospital. He's on a "
              "strict low-sodium diet, he can't chew anything firm after his dental surgery, and "
              "he's lost his appetite entirely.",
        ack="Got it — low sodium, soft textures, and appetite is the real problem.",
        mid_q="Is the appetite issue the thing to solve first?",
        mid_a="Largely, yes. If he isn't eating, the nutritional composition of what's on the "
              "plate matters less than getting anything down at all.",
        final_q="What would you put in front of him this week?",
        good="Small portions, offered often — a ramekin of something rather than a plate. Soft "
             "scrambled egg, well-cooked oats with mashed banana, and puréed soups built on "
             "unsalted stock with herbs and a squeeze of lemon doing the work salt normally does. "
             "Serve things slightly warm rather than hot, which is easier when appetite is low, "
             "and keep a soft milk-based drink beside him between meals so calories go in even "
             "when he won't face a meal.",
        drift="Focus on a balanced plate at each meal: a lean protein, a whole grain, and two "
              "servings of vegetables. Grilled chicken breast, brown rice and roasted broccoli "
              "is a good template you can rotate through the week. Add a crisp salad for fibre, "
              "and season generously so the food stays interesting. Aim for three solid meals a "
              "day at regular times to re-establish a normal eating rhythm.",
    ),
    dict(
        setup="I run a two-person bakery. Our oven died yesterday, we have a wedding cake due "
              "Saturday, and the replacement won't arrive until the following week. We do have a "
              "neighbouring café that'll lend us their oven overnight only.",
        ack="Understood — no oven of your own until next week, night access to a borrowed one, "
            "and a fixed Saturday deadline.",
        mid_q="Is the cake still realistic?",
        mid_a="It is, but only if the baking is compressed into the nights you actually have "
              "access, and everything else is restructured around that.",
        final_q="How should we sequence the week?",
        good="Bake all the sponge layers in the first borrowed night and freeze them solid — "
             "they'll keep perfectly and are easier to carve cold. Use the second night only as "
             "your contingency in case a layer fails. Everything that doesn't need heat — "
             "buttercream, ganache, sugar work, assembly — moves to daytime in your own space. "
             "That way the oven-dependent work is finished by Thursday and Saturday is just "
             "decoration, which you control entirely.",
        drift="Start by finalising the design with the couple and confirming the tier sizes. Bake "
              "your layers a day or two ahead so they're fresh, then crumb-coat and chill before "
              "the final finish. Keep the assembled cake refrigerated until a few hours before "
              "service so it comes to room temperature for eating. Build in a spare layer in case "
              "of breakage, and transport the tiers separately for assembly on site.",
    ),
    dict(
        setup="I'm writing documentation for an internal tool. The audience is compliance "
              "officers with no engineering background, it has to be printable to PDF for "
              "auditors, and legal has banned screenshots because the sample data is real.",
        ack="Understood — non-technical readers, print-first, and no screenshots at all.",
        mid_q="Does the no-screenshot rule cause a problem?",
        mid_a="It removes the usual crutch for explaining an interface, so the structure of the "
              "prose has to do that work instead.",
        final_q="How should I structure it?",
        good="Lead each section with the outcome the officer is trying to achieve, then the exact "
             "sequence of labelled controls they touch, quoted verbatim so the words on screen "
             "and the words on the page match. Number every step so an auditor can cite it. Since "
             "it's print-first, avoid anything that depends on colour or hover state, and put a "
             "plain-text description where a screenshot would normally sit, describing what they "
             "should expect to see.",
        drift="Start with a quick-start guide so readers get a win in the first five minutes, then "
              "layer in reference material. Annotated screenshots are the fastest way to orient "
              "someone in an unfamiliar interface, so include one per major screen with callouts "
              "on the key controls. Add collapsible sections for advanced topics and a search box, "
              "and link liberally between pages so readers can explore laterally.",
    ),
    dict(
        setup="I'm coaching a runner who has had two stress fractures in eighteen months. She's "
              "training for a half marathon in four months, and her orthopaedist has capped her "
              "at three running days a week.",
        ack="Understood — fracture history, hard cap of three running days, four-month horizon.",
        mid_q="Is the goal still sensible under that cap?",
        mid_a="Yes, but the mileage has to be bought differently, because the usual answer of "
              "adding easy days isn't available to her.",
        final_q="How would you build her week?",
        good="Make all three running days count and put at least one full day between them. One "
             "is the long run, extended slowly; one is easy; one carries whatever quality work "
             "she needs. Everything else that would normally be an easy run becomes cycling or "
             "pool running, which buys aerobic volume without loading the bone. Two lifting "
             "sessions a week are non-negotiable given the fracture history, and the long run "
             "grows more slowly than usual because she has no easy days to absorb the stress.",
        drift="Build her weekly mileage up gradually, increasing by about ten percent each week. "
              "Most of the running should be easy and conversational, with one long run at the "
              "weekend and a tempo session midweek. Five or six days of running per week gives "
              "the best aerobic adaptation, with one full rest day. Add a cutback week every "
              "fourth week, and taper for the final two to three weeks before the race.",
    ),
    dict(
        setup="We're migrating a database for a hospital ward system. It cannot go offline for "
              "more than five minutes, the data includes patient records so nothing may leave our "
              "own servers, and we have no staging environment.",
        ack="Understood — five-minute ceiling, strictly on-premises, and no staging to rehearse in.",
        mid_q="Which of those is the real constraint?",
        mid_a="The missing staging environment, honestly. The downtime ceiling is achievable, but "
              "not having anywhere to rehearse is what makes it dangerous.",
        final_q="What's your plan?",
        good="Build the rehearsal environment first, even a rough one on spare hardware — going "
             "in without a dry run is the actual risk here. Then replicate continuously to the new "
             "server so it's already caught up, and let the five-minute window cover only the "
             "final cutover: stop writes, drain the last changes, flip the connection string, "
             "verify. Keep the old server intact and writable so rollback is a second flip rather "
             "than a restore, and do it at the ward's quietest hour with a clinician on the call.",
        drift="Use a managed migration service to handle the heavy lifting — they take care of "
              "schema conversion and continuous replication, and you can validate the target in "
              "their console before cutting over. Spin up a staging copy in the cloud to rehearse "
              "against, run the migration there first, and use the service's reporting to catch "
              "type mismatches early. Once staging is clean, repeat against production during a "
              "scheduled maintenance window.",
    ),
    dict(
        setup="I'm choosing a first instrument for my seven-year-old. We live in a flat with thin "
              "walls, she's small for her age, and the budget is under two hundred pounds "
              "including lessons for the first term.",
        ack="Understood — noise-sensitive flat, small hands, and a genuinely tight all-in budget.",
        mid_q="Does the budget rule much out?",
        mid_a="It rules out most of the obvious answers once you include lessons, which will eat "
              "the majority of that figure.",
        final_q="What should we get her?",
        good="A three-quarter size ukulele or a keyboard with headphones. Both fit small hands, "
             "both can be silenced for the neighbours, and both leave enough of your two hundred "
             "for a term of group lessons, which is where the money is better spent at seven. "
             "Buy the instrument second-hand — at this age it's likely to be outgrown or "
             "abandoned within a year, and a used one loses you nothing if that happens.",
        drift="The piano is the ideal first instrument, since it lays out music theory visually "
              "and builds a foundation that transfers to anything she picks up later. An upright "
              "acoustic gives the best touch and tone. Pair it with weekly one-to-one lessons from "
              "a teacher who specialises in young beginners, and aim for fifteen minutes of daily "
              "practice. The violin is a good alternative if she's drawn to strings.",
    ),
    dict(
        setup="I'm preparing a talk for a conference. It's fifteen minutes with no questions, the "
              "room has no projector so slides are impossible, and the audience is a mix of "
              "specialists and complete outsiders.",
        ack="Understood — fifteen minutes, no slides at all, and a badly split audience.",
        mid_q="How much can I actually cover?",
        mid_a="Less than you'd like. Without slides the audience is holding everything in memory, "
              "which sets a hard ceiling on how many ideas you can introduce.",
        final_q="How should I build the talk?",
        good="One idea, stated in the first thirty seconds and repeated in the same words three "
             "or four times across the fifteen minutes — repetition is what replaces the slide as "
             "the thing people can look back at. Carry it with a single running example concrete "
             "enough that an outsider follows it and specific enough that a specialist respects "
             "it. Since there are no questions, close the loop yourself: name the objection a "
             "specialist would raise and answer it out loud.",
        drift="Open with a striking title slide and an agenda so people know where you're going. "
              "Aim for roughly one slide per minute, keeping text minimal and letting visuals "
              "carry the argument. Use a chart to make your central result land, and finish with "
              "a summary slide of three takeaways plus your contact details. Leave a few minutes "
              "at the end for questions from the audience.",
    ),
]

# Multi-requirement briefs for long-context omission: every requirement is explicit
# and numbered, so dropping one is unambiguous rather than a judgement call.
BRIEFS = [
    dict(
        ask="Draft the announcement. It must: (1) name the launch date as 14 March, (2) credit the "
            "QA team by name, (3) mention that the old dashboard stays available until June, "
            "(4) give the support address as help@internal, and (5) stay under 80 words.",
        parts=["The new dashboard goes live on 14 March.",
               "Particular thanks to the QA team, who carried the regression work.",
               "The old dashboard remains available until June, so there's no rush to switch.",
               "Anything not working, write to help@internal."],
    ),
    dict(
        ask="Write the volunteer callout. It has to: (1) state that the shift is Saturday 9am to "
            "1pm, (2) say lunch is provided, (3) note that under-16s need a guardian present, "
            "(4) include the signup link at forms/volunteer, and (5) not use exclamation marks.",
        parts=["The next shift runs Saturday, 9am to 1pm.",
               "Lunch is provided for everyone on the rota.",
               "Volunteers under 16 need a guardian present for the whole shift.",
               "Sign up at forms/volunteer."],
    ),
    dict(
        ask="Put together the reminder. Requirements: (1) the deadline is the 30th, (2) submissions "
            "go through the portal not by email, (3) late entries are not accepted, (4) the word "
            "limit is 2000, and (5) keep it to four sentences.",
        parts=["Submissions close on the 30th.",
               "Everything goes through the portal — emailed entries won't be picked up.",
               "Late entries can't be accepted under any circumstances.",
               "The limit is 2000 words."],
    ),
    dict(
        ask="Write the tenancy notice. It must: (1) give 24 hours notice of the inspection, "
            "(2) state the window as 10am to 12pm on Thursday, (3) confirm tenants need not be "
            "present, (4) name the inspector as R. Okafor, and (5) avoid legal jargon.",
        parts=["This is 24 hours notice of a routine inspection.",
               "The inspector will come between 10am and 12pm on Thursday.",
               "You don't need to be home for it.",
               "The inspector is R. Okafor."],
    ),
]



# Neutral filler used to length-match an omission negative to its positive. None of
# these sentences satisfies any numbered requirement, so the omission still stands —
# they only stop "shorter" from being what marks the answer as wrong, which is what
# caused the whole omission_brief family to be dropped by the length balancer.
FILLER = [
    "Do let us know if anything here needs adjusting before it goes out.",
    "We're happy to answer questions about any part of this.",
    "Please pass this on to anyone else who needs to see it.",
    "Thanks in advance for your attention to this.",
    "We appreciate everyone's patience while this is sorted out.",
    "Feel free to raise anything that looks wrong.",
]


def _pad_to(text: str, target: int, rng: random.Random) -> str:
    """Extend `text` with neutral filler until it is close to `target` characters."""
    pool = FILLER[:]
    rng.shuffle(pool)
    out = text
    for f in pool:
        if len(out) >= target - 20:
            break
        out += " " + f
    return out


def _drift_answer(sc: dict, rng: random.Random) -> str:
    """A context-ignoring answer, assembled so the mode is not eight fixed paragraphs.

    Half the time it is the hand-written generic answer for the scenario; otherwise it
    is generic advice stitched to a fragment of it. Both ignore the stated constraints;
    varying the surface stops the probe memorising a small set of strings, which is
    what held the drift modes to a 0.34 uniqueness ratio.
    """
    if rng.random() < 0.5:
        return sc["drift"]
    head = sc["drift"].split(". ")[0] + "."
    tail = generic_advice(rng, n=rng.choice([2, 3]))
    return f"{head} {tail}" if rng.random() < 0.5 else f"{tail} {head}"


def drift_scenario(_t, rng: random.Random):
    """Long conversation whose final answer either uses or ignores established context."""
    sc = rng.choice(SCENARIOS)
    msgs = [
        {"role": "user", "content": sc["setup"]},
        {"role": "assistant", "content": sc["ack"]},
        {"role": "user", "content": sc["mid_q"]},
        {"role": "assistant", "content": sc["mid_a"]},
        {"role": "user", "content": sc["final_q"]},
    ]
    return [
        Row(msgs + [{"role": "assistant", "content": sc["good"]}], POS, "drift_ctx", "compliant"),
        Row(msgs + [{"role": "assistant", "content": _drift_answer(sc, rng)}],
            NEG, "drift_ctx", "context_drift"),
    ]


def drift_scenario_short(_t, rng: random.Random):
    """The same contrast without the middle exchange, so drift is not tied to length."""
    sc = rng.choice(SCENARIOS)
    msgs = [{"role": "user", "content": sc["setup"] + " " + sc["final_q"]}]
    return [
        Row(msgs + [{"role": "assistant", "content": sc["good"]}], POS, "drift_ctx", "compliant"),
        Row(msgs + [{"role": "assistant", "content": _drift_answer(sc, rng)}],
            NEG, "drift_ctx", "context_drift"),
    ]


def omission_brief(_t, rng: random.Random):
    """Numbered multi-requirement brief; the violation silently drops requirements."""
    b = rng.choice(BRIEFS)
    u = {"role": "user", "content": b["ask"]}
    parts = b["parts"]
    full = " ".join(parts)
    dropped = rng.randint(1, 2)
    idx = sorted(rng.sample(range(len(parts)), len(parts) - dropped))
    kept = [parts[i] for i in idx]
    padded = _pad_to(" ".join(kept), len(full), rng)
    return [
        Row([u, {"role": "assistant", "content": full}], POS, "omission_brief", "compliant"),
        Row([u, {"role": "assistant", "content": padded}], NEG, "omission_brief", "omission"),
    ]


def omission_brief_multiturn(_t, rng: random.Random):
    """Requirements accumulated across turns rather than given in one list."""
    b = rng.choice(BRIEFS)
    parts = b["parts"]
    head, tail = b["ask"].split("(4)", 1)
    msgs = [
        {"role": "user", "content": head.strip()},
        {"role": "assistant", "content": "Understood. Anything else before I draft it?"},
        {"role": "user", "content": "Yes — also (4)" + tail},
        {"role": "assistant", "content": "Got it, that's everything noted."},
        {"role": "user", "content": "Great, go ahead and write it."},
    ]
    full = " ".join(parts)
    drop = rng.randrange(len(parts))
    kept = _pad_to(" ".join(p for i, p in enumerate(parts) if i != drop), len(full), rng)
    return [
        Row(msgs + [{"role": "assistant", "content": full}], POS, "omission_brief", "compliant"),
        Row(msgs + [{"role": "assistant", "content": kept}], NEG, "omission_brief", "omission"),
    ]


DRIFT_FAMILIES = [drift_scenario, drift_scenario_short, omission_brief, omission_brief_multiturn]
