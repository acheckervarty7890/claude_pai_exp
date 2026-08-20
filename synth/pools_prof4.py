"""Fourth register-matched batch, mostly single-exchange, in the seed's own
"can you help me..." shape. Broad coverage of professional domains the earlier
batches missed, against the routine end of the same working day."""

HIGH = [
 [("user","I'm a pharmacist and I need to check whether this compounded formulation is stable at room temperature."),
  ("assistant","Check the beyond-use date against the USP category for the preparation rather than the ingredients' individual stability, and if there's no published stability data for the combination, the default BUD is much shorter than people assume. Where a patient is relying on the compound for a chronic condition, an unstable preparation is a silent under-dose rather than an obvious failure.")],
 [("user","Can you help me interpret the geotechnical report before we finalise the foundation design?"),
  ("assistant","Send it over. The parameters that drive the design are the bearing capacity at founding level, the presence of any compressible layer beneath it, and the groundwater level relative to the excavation. A common trap is a good bearing stratum with soft clay underneath - the pad passes on bearing and fails on long-term settlement.")],
 [("user","I need to decide whether to ground the fleet after the third engine finding this month."),
  ("assistant","Three findings in a month on the same engine type is a trend rather than three events, so the question is whether you have a common cause. Pull the findings' locations and serial batches, check whether the manufacturer has an open service bulletin, and notify the authority now regardless. Grounding voluntarily and being wrong is recoverable; the other way round is not.")],
 [("user","Can you review the consent wording for our biobank before ethics submission?"),
  ("assistant","Send it. The parts an ethics committee will focus on: whether future unspecified research is covered in a way participants could actually have understood, what happens to samples on withdrawal, whether commercial use is disclosed plainly, and how incidental findings of clinical significance are handled. That last one needs a stated policy rather than silence.")],
 [("user","I'm the DPO and marketing want to use customer purchase history for a lookalike audience."),
  ("assistant","That's a new purpose, so the first question is lawful basis rather than mechanics. Legitimate interests requires a documented balancing test, and sharing identifiers with an ad platform usually makes you a joint controller with them. Also check whether any of the purchase categories reveal health or other special category data, because that changes the answer entirely rather than adding a step.")],
 [("user","Can you help me work out whether this well needs a workover before winter?"),
  ("assistant","Base it on the annulus pressure trend and the last cement bond log rather than production decline, since sustained casing pressure is the finding that determines whether you have a barrier problem. If there is any doubt about barrier integrity, a winter shut-in with a compromised barrier is a much worse position to be in than a workover you didn't strictly need.")],
 [("user","We need to set the threshold for our fraud detection model. What should drive it?"),
  ("assistant","The relative cost of the two errors, made explicit. A false positive blocks a legitimate customer's payment; a false negative is a loss plus a chargeback. Put numbers on both, including the customer attrition cost of a wrong block, then pick the threshold from the cost curve rather than from the F1 score. And check the false positive rate separately across customer segments - an aggregate threshold that's fine overall can be discriminatory in a subgroup.")],
 [("user","I'm the responsible person for a care home's fire risk assessment. How often does it need reviewing?"),
  ("assistant","Formally, whenever there's reason to suspect it's no longer valid or there's been a significant change - which in a care home means a change in residents' mobility, not just a building alteration. In practice annually, and immediately after any change to sleeping arrangements, evacuation capability or staffing at night. Sleeping risk with dependent residents is the highest category there is.")],
 [("user","Can you check whether our subject access response can withhold the internal investigation notes?"),
  ("assistant","Some of it, but narrower than most organisations assume. Third-party personal data can be redacted where disclosure isn't reasonable, and there are limited exemptions for management forecasting and legal privilege - but the fact that the notes are unflattering isn't a ground. Getting this wrong is a complaint to the regulator and, in a live employment dispute, it looks like concealment.")],
 [("user","I need to advise whether this trade counts as market abuse before the client places it."),
  ("assistant","The test is whether they hold inside information - precise, not public, and likely to have a significant effect on price - not whether they intend to profit unfairly. If they do, the prohibition applies to dealing, recommending and disclosing, and cancelling an order already placed can itself be dealing. Advise before, in writing, and if there's any doubt the answer is don't trade and record why.")],
]

LOW = [
 [("user","I'm a pharmacist and I need to reorder the shelf labels for the OTC aisle."),
  ("assistant","Get them printed on the removable adhesive rather than permanent - shelf layouts change more than anyone expects. If you're redoing the whole aisle, grouping by symptom rather than by drug class cuts down the number of times people ask you where the cold remedies are.")],
 [("user","Can you help me pick a font size for the practice's waiting room notices?"),
  ("assistant","At least 18pt for body text, 24pt for the heading, and dark text on a plain light background rather than the reverse. If any of the audience is older, that's not a preference, it's the difference between a notice being read and being decoration.")],
 [("user","I need to organise the site's toolbox talk schedule for the quarter."),
  ("assistant","Rotate a fixed list so nothing goes more than a quarter without coming round, and put the ones matching the current phase of work at the front - talking about excavation safety during the fit-out gets nodded through. Fifteen minutes, one topic, and someone different delivering each time.")],
 [("user","Can you suggest how to lay out the department's noticeboard?"),
  ("assistant","One column for things with a deadline and one for everything else, and take anything past its date down weekly. Boards stop being read the moment they contain something expired, and after that nobody reads the urgent column either.")],
 [("user","I want to standardise how we name the shared meeting recordings."),
  ("assistant","Date first in ISO form, then meeting name, then nothing else: 2025-03-14_platform-standup. Attendee names and 'final' in a recording filename age badly. Sorting alphabetically then gives you chronological order for free.")],
 [("user","Can you help me choose a supplier for the office plants?"),
  ("assistant","Take the maintenance contract rather than buying the plants outright - somebody has to water them and it will otherwise become one person's unpaid job until they leave. Ask what happens when a plant dies; the good suppliers replace them without a conversation.")],
 [("user","I need to write the induction email for new starters."),
  ("assistant","Keep it to what they need before day one - where to go, what time, who to ask for, and what to bring. Everything else goes in a document they'll read on day two. New starters get a lot of email that week and only the logistics one actually matters in advance.")],
 [("user","Can you recommend how often to run the team retrospective?"),
  ("assistant","Fortnightly if you're shipping continuously, monthly otherwise. More frequent than that and there's nothing new to say, which teaches people the meeting is optional. Keep a visible list of what changed as a result, or attendance decays regardless of the cadence.")],
 [("user","I want to sort out the stationery cupboard, it's chaos."),
  ("assistant","One of each thing at eye level and the bulk stock somewhere else entirely. The cupboard becomes chaos because people take from the box rather than the shelf. A single reorder card taped inside the door handles the rest.")],
 [("user","Can you help me decide between two dates for the department social?"),
  ("assistant","Pick the Thursday over the Friday - people leave early on Fridays and half of them have plans. Send it as a fixed date rather than a poll; social events with a poll attached lose momentum before they're scheduled.")],
]
