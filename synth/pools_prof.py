"""Register-matched batch, following the training seed's own convention.

The seed labels calm professional work high-stakes when an error would be
consequential ("calculate the load-bearing capacity", "review the terms and
conditions"), and labels routine admin low-stakes even inside a serious domain
("reschedule my doctor's appointment", "remind me to take my medication"). The
rest of the synthetic set leans emergency-shaped on one side and leisure-shaped on
the other; this batch fills the calm professional / routine office middle, which is
where most real rows sit.
"""

HIGH = [
 [("user","I'm sizing the steel beam for a 6.4 metre clear span carrying a floor at 2.5 kN/m2 plus partitions. Can you check my working?"),
  ("assistant","Happy to check it, with the caveat that this needs a chartered engineer's sign-off before it's built. Walk me through the load takedown first: what tributary width are you using, and have you included the partition allowance as a line load or smeared over the area? Those two choices usually account for most of the difference between a section that works and one that deflects visibly.")],
 [("user","We're revising our anticoagulation protocol for the whole trust. Can you help me structure the bridging section?"),
  ("assistant","Structure it around procedural bleed risk and thrombotic risk as two independent axes, because most protocol errors come from treating them as one. Define the procedures where interruption isn't needed at all, then the low and high thrombotic risk groups with explicit CHA2DS2-VASc or mechanical valve criteria. Every branch should end in a named timing instruction rather than a range, since ranges are where the ward-level variation creeps in.")],
 [("user","I need to work out the ventilation rate for a laboratory handling volatile solvents. 40 square metres, 3 metre ceiling."),
  ("assistant","For a solvent-handling lab you'd normally design to 8 to 12 air changes an hour, which on 120 cubic metres is 960 to 1,440 cubic metres per hour. But the general rate is the secondary control - the fume hood face velocity is the primary one, and the room supply has to be sized so the hoods still achieve 0.5 metres per second with the door closed. What hoods are specified, and how many run simultaneously?")],
 [("user","Can you review our data retention schedule against GDPR before we roll it out?"),
  ("assistant","Send it over. The three things I'd look at first: whether each retention period has a stated lawful basis and justification rather than a round number, whether deletion is actually implemented in backups and not only in the primary store, and whether there's a documented exception process for litigation hold. Schedules usually fail on the second one - the policy says 24 months and the backups keep everything for seven years.")],
 [("user","I'm the estate's compliance lead and I need to design the audit sampling plan for our supplier due diligence."),
  ("assistant","Sample risk-weighted rather than randomly: stratify suppliers by spend, jurisdiction risk and whether they touch personal data or safety-critical components, then sample proportionally more from the high strata. Document the stratification logic itself, because that's what an auditor examines - a defensible plan with a small sample beats a large random sample with no rationale.")],
 [("user","We're modelling the flood risk for a proposed housing development on a river floodplain. What return period should we design to?"),
  ("assistant","For residential development you'd normally assess against the 1 in 100 year fluvial event with a climate change allowance, and check the 1 in 1000 for the residual risk case. The allowance is the part that gets argued about - use the current central and upper-end percentiles for the river basin district, and present both, because a scheme that only works on the central estimate will not survive planning.")],
 [("user","I need to calculate the safe working load for a lifting eye welded to a 12mm plate."),
  ("assistant","The eye itself is rarely the governing case - it's usually the weld and the plate behind it. You need the weld throat area against the resolved load at the actual sling angle, plus a check on plate tear-out and bearing. And a welded lifting point needs proof testing and certification before use regardless of the calculation; an uncertified padeye is not a lifting point.")],
 [("user","Our pension scheme's actuarial valuation came back with a deficit. Can you help me understand the recovery plan options?"),
  ("assistant","There are three levers and they trade against each other: the length of the recovery period, the contribution amount, and the investment return assumption. Lengthening the period lowers contributions but increases the risk the covenant weakens before it closes. The regulator will want to see the employer covenant assessed independently, and a plan that leans on optimistic returns rather than contributions is the one that draws scrutiny.")],
 [("user","I'm writing the validation protocol for a new sterilisation autoclave cycle."),
  ("assistant","You'll need installation, operational and performance qualification as separate documents with separate acceptance criteria. For PQ, biological indicators with a defined D-value at the worst-case load configuration, thermocouples at the cold spots you've identified rather than the convenient ones, and three consecutive successful runs. The worst-case load definition is what an inspector will challenge, so justify it in writing.")],
 [("user","Can you help me analyse whether this merger raises competition concerns before we notify?"),
  ("assistant","Start with market definition, since everything follows from it - product scope, geographic scope, and whether the parties compete in the same one. Then combined share and the increment, plus the HHI delta. Contemporaneous internal documents matter more than people expect: if your own strategy deck names the target as the main competitive constraint, that's the document the authority will lead with.")],
 [("user","I need to specify the fall arrest system for a 40 metre communications mast."),
  ("assistant","Specify the whole system rather than the harness: anchor points rated for the arrest force and certified on the structure, a rigid rail or cable system for climbing rather than lanyards, and calculated fall clearance including deceleration distance and harness stretch. Then the part people forget - a written rescue plan with equipment on site, because suspension trauma is measured in minutes and calling the fire service is not a plan.")],
 [("user","We're setting the credit limits for a new commercial lending product. Can you review the affordability model?"),
  ("assistant","Send it through. The two areas I'd focus on are the stress assumptions and the treatment of existing commitments. A model that only tests the current rate environment will pass borrowers who fail at a plausible rate rise, and undercounting existing commitments is the most common source of systematic over-lending. Also check what happens at the boundaries - many models behave oddly for the smallest and largest cases.")],
 [("user","I'm drafting the informed consent document for a first-in-human trial."),
  ("assistant","The specific things an IRB will look at: that the experimental nature is stated plainly and early, that the absence of expected therapeutic benefit is explicit for a phase 1, that the reasonably foreseeable risks include those seen in the animal data, and that withdrawal is described as free of penalty. Reading level matters as much as content - aim for around grade 8, and have someone outside the study read it back to you.")],
 [("user","Can you help me plan the cutover for migrating our patient records system?"),
  ("assistant","Plan around the read-only window and the fallback, not the migration itself. You need a defined point where the legacy system goes read-only, a reconciliation count that must match before go-live, downtime procedures printed on paper at every ward, and a rollback decision point with a named person and a deadline. Clinical system cutovers fail on the fallback plan far more often than on the data.")],
 [("user","I need to determine whether our new product falls under the medical device regulations."),
  ("assistant","It turns on intended purpose as you state it, not on the technology. If you claim diagnosis, prevention, monitoring, prediction, prognosis or treatment of disease, you're in scope, and marketing copy counts as a claim. Software that only stores or displays data is generally excluded; software that interprets it generally is not. Get this determination in writing early - reclassifying after launch is far more expensive than designing to the class.")],
]

LOW = [
 [("user","Can you set up a shared calendar for the team's annual leave?"),
  ("assistant","Create a secondary calendar and share it with the team at 'see all event details' rather than 'make changes', then have people submit leave through the existing form so the calendar stays a view rather than a second source of truth. Colour-code by team if you've more than about eight people.")],
 [("user","I need to reformat the monthly report so the tables fit the page properly."),
  ("assistant","Set the table to autofit to window, then turn off 'allow row to break across pages' - that's usually what makes them look broken. If they're still overflowing, landscape orientation for just those pages via a section break is cleaner than shrinking the font.")],
 [("user","Can you help me write the meeting invite for the quarterly planning session?"),
  ("assistant","Something like: 'Q3 planning - please bring your team's top three priorities and anything you need from another team. Agenda attached; we'll finish on time.' Put the agenda in the body rather than only as an attachment, since half the room reads it on a phone.")],
 [("user","I want to set up an out of office that only replies to external senders."),
  ("assistant","In Outlook, the automatic replies dialogue has separate tabs for inside and outside the organisation - leave the internal one blank and fill in the external. There's also a checkbox for 'my contacts only' if you'd rather not reply to mailing lists.")],
 [("user","Can you suggest a naming convention for our shared drive folders?"),
  ("assistant","Date first in ISO form so they sort correctly, then project, then document type: 2025-03_northgate_proposal_v2. Avoid spaces if anything syncs to a command line, keep version numbers in the filename rather than the folder, and pick one and write it on a page somewhere - consistency matters more than the scheme.")],
 [("user","I need to book a meeting room with a video setup for eight people next Tuesday."),
  ("assistant","Filter the room list by capacity 8 and the video conferencing attribute, then book from the room's own calendar rather than adding it as an attendee - that way you see the actual availability. Worth booking fifteen minutes either side if the room's popular.")],
 [("user","Can you help me choose a font pairing for our new internal newsletter?"),
  ("assistant","A serif for headings and a sans for body reads well and is hard to get wrong - something like Source Serif with Source Sans, which are designed to sit together. Keep it to two families, and set the body at 16px with generous line height; that does more for readability than the choice of font.")],
 [("user","I want to archive last year's project folders without losing the links in old documents."),
  ("assistant","Move rather than copy, so the file IDs stay the same and existing links keep resolving. If you're on SharePoint or Drive, links follow the file. What breaks links is copy-then-delete, which creates a new ID for the copy.")],
 [("user","Can you set up a recurring reminder for the team to submit timesheets?"),
  ("assistant","A recurring Thursday afternoon message in the team channel works better than a calendar reminder, because people action it where they already are. Set it for 3pm rather than 5, so there's time to actually do it before people leave.")],
 [("user","I need to compare a few options for the office coffee subscription."),
  ("assistant","Compare on cost per cup rather than per bag, since bag sizes differ, and check whether the machine is included or leased separately - that's usually where the difference is. Also ask about the minimum term; the cheap per-cup rates tend to come with a two year commitment.")],
 [("user","Can you help me add conditional formatting to the budget tracker so overspend shows in red?"),
  ("assistant","Select the variance column, then conditional formatting, new rule, format only cells that contain, cell value less than 0, and set the fill. If the variance is a formula, use 'use a formula to determine which cells to format' with something like =$F2<0 and apply it to the whole row so the context comes with it.")],
 [("user","I want to standardise the email signature across the department."),
  ("assistant","Keep it to name, role, team and one contact method - signatures get quoted in every reply and long ones make threads unreadable. If your mail admin supports server-side signatures, set it there rather than asking forty people to paste something correctly.")],
 [("user","Can you recommend how to organise the team's onboarding documents?"),
  ("assistant","One page that links to everything else, ordered by when a new starter needs it: day one, first week, first month. New joiners fail to find things because documents are organised by who owns them rather than by when they're needed.")],
 [("user","I need to update the office floor plan to show the new desk layout."),
  ("assistant","If the original is a CAD file, ask facilities for the DWG rather than redrawing over the PDF - they usually have it. For a quick version, the shapes and layers in any diagramming tool are fine, but keep desk numbering consistent with the booking system or you'll create two conflicting maps.")],
 [("user","Can you help me set up a poll for the team lunch venue?"),
  ("assistant","Three options maximum, with the dietary constraints named against each - polls with eight options produce a four-way tie and another poll. Set a closing time in the message itself, and say what happens if it ties so nobody has to have that conversation.")],
]
