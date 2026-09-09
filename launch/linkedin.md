# LinkedIn article (Serhii; tag state CIOs of VA, MD, CA, OH, TX and NASCIO)

Title: What AI agents cost your state when they read instead of retrieve

Federal prime contracts naming AI performed in Virginia total $128 million this fiscal year, in Maryland $71.6 million, in California $33.6 million, in Ohio $22.1 million, in Texas $15.8 million (USAspending.gov, labelled contracts only, a floor). Those are public numbers. What is not public is how much of the AI work inside them is an agent reading whole files to find one passage.

I measured that habit on a production codebase: 16 to 47 times more bytes read than used, for the same answers. A local index that answers "where is it" before the agent reads removes most of it. The software is open source, runs inside the state's own environment, and a pilot fits on one laptop with no procurement.

The AI Burn Clock publishes a dated release for every state, datelined at the capital, with the sources, the method and a one-page memo on request: aiburnclock.org/state/. State CIOs and agency IT leads: reply with your state and I will send the memo with your figures.
