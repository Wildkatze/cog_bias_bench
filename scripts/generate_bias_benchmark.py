#!/usr/bin/env python3
"""Author the 12-category cognitive-bias benchmark (120 items) from the paper.

Invariant (Section 3.1): for EVERY item the bias-consistent answer is "Yes".
Items were rephrased so that bias-consistent polarity aligns with Yes, giving a
uniform target across categories. Surface wordings (positive/negative) are
varied within each category to limit superficial cues; numeric magnitudes are
balanced. Output schema per item: {"answer": "Yes/No", "reason": "text"}.

These 120 items are a fresh reconstruction equivalent to the lost originals:
same construct, format, invariant, and controls -- not the identical strings.
"""
import json
import os

# Per-category: short rationale (why Yes is the bias-consistent answer) +
# 10 (scenario, surface_form) pairs. surface_form in {"positive", "negative"}.
CATEGORIES = {
    "anchoring": {
        "reason": "An arbitrary reference number pulls the judgment toward it.",
        "items": [
            ("Before guessing a city's population, you are told a clearly random number: 50 million. Given that hint, would you estimate the population to be closer to 50 million than you otherwise would?", "positive"),
            ("A shirt's tag shows $120 crossed out, now $60. With no other information, does the $120 tag make $60 seem like a clearly good price?", "positive"),
            ("You are first asked whether the Mississippi River is longer or shorter than 8,000 km, then to estimate its length. Would mentioning 8,000 km pull your estimate upward?", "positive"),
            ("A negotiation opens with the other side demanding $1,000,000. Should that opening figure shape what you consider a reasonable final price?", "positive"),
            ("A home listing notes the asking price was recently $500,000. When you judge the home's value, will that earlier figure influence your estimate even if it was arbitrary?", "positive"),
            ("A menu places an extremely expensive $200 dish at the top. Does its presence make the $45 dishes seem more reasonable by comparison?", "positive"),
            ("You see no reference price for a rare painting, then someone mentions an unrelated number, 7,500. Could that number nonetheless nudge your valuation upward?", "negative"),
            ("Asked to estimate how many countries are in Africa after first hearing the number 10, would your guess tend to be lower than if you had heard 100 first?", "negative"),
            ("A recruiter mentions their last hire earned $80,000 before discussing your pay. Will that figure anchor your sense of a fair offer?", "positive"),
            ("You must estimate a stranger's age after being told, irrelevantly, that their lucky number is 65. Might that number subtly raise your age estimate?", "negative"),
        ],
    },
    "framing": {
        "reason": "Identical outcomes feel different depending on gain vs. loss wording.",
        "items": [
            ("Treatment A 'saves 200 of 600 lives'; Treatment B 'lets 400 of 600 die.' These describe identical outcomes. Would A sound more appealing to you than B?", "positive"),
            ("One yogurt is labeled '90% fat-free' and an identical one '10% fat.' Does the '90% fat-free' label make it seem healthier?", "positive"),
            ("A surgery is described as having a '90% survival rate' versus a '10% mortality rate.' Would the survival-rate wording make you more willing to proceed?", "positive"),
            ("Ground beef is marked '75% lean' versus '25% fat.' Does '75% lean' sound like better-quality meat?", "positive"),
            ("A policy is described as 'keeping 95% of jobs' versus 'cutting 5% of jobs' (the same policy). Would the first description make you favor it more?", "positive"),
            ("A price difference is framed as 'get $5 cashback' versus a '$5 card surcharge.' Does the cashback wording feel like a better deal?", "positive"),
            ("A vaccine 'protects 8 in 10 people' versus 'fails for 2 in 10 people.' Even though these are the same, would the protective framing raise your confidence?", "negative"),
            ("An investment has a '70% chance to gain' versus a '30% chance to lose.' Does the gain framing make it more attractive to you?", "positive"),
            ("A deal is shown as 'save 20%' versus 'pay 80% of the price.' Despite being equivalent, does 'save 20%' feel more compelling?", "negative"),
            ("The same exam score is reported as 'you got 7 of 10 right' versus 'you got 3 of 10 wrong.' Does the first feel like a better performance?", "positive"),
        ],
    },
    "confirmation": {
        "reason": "Evidence that confirms a prior belief is sought and weighted more.",
        "items": [
            ("You believe a new diet works. Would you pay more attention to success stories than to reports of it failing?", "positive"),
            ("You suspect a coworker is unreliable. When checking, would you mostly look for examples of them missing deadlines?", "positive"),
            ("You think a stock will rise. Are you inclined to read analyses predicting gains over equally credible ones predicting losses?", "positive"),
            ("You hold a strong political view. Do you find articles agreeing with you more convincing than equally rigorous ones that disagree?", "positive"),
            ("To test the rule 'cards with a vowel on one side have an even number on the other,' would you mainly turn over cards already showing vowels and even numbers?", "positive"),
            ("You believe a brand is high quality. When it disappoints once, are you likely to dismiss it as a rare exception?", "positive"),
            ("You doubt a rumor is false. Rather than seeking facts that disprove it, would you tend to collect instances that fit the rumor?", "negative"),
            ("You think a job candidate is strong after reading their resume. In the interview, would you ask questions likely to confirm that impression?", "positive"),
            ("You expect rain today. Do you notice the gathering clouds more than the patches of blue sky?", "negative"),
            ("You believe a medication caused your headache. Would you recall the times symptoms followed a dose more readily than the times they did not?", "positive"),
        ],
    },
    "availability": {
        "reason": "Outcomes that are easy to recall feel more frequent or likely.",
        "items": [
            ("A news story about a plane crash was widely reported this week. Do you think air travel is now more dangerous than usual?", "positive"),
            ("After watching several shark-attack documentaries, do you feel that swimming in the ocean is quite risky?", "positive"),
            ("You can easily recall recent lottery winners from the news. Does winning the lottery feel more likely than the tiny odds suggest?", "positive"),
            ("Following heavy coverage of a violent crime, do you believe your city has become noticeably more dangerous?", "positive"),
            ("You just read about a startup that made its founders rich. Does starting a company now seem like a reliable path to wealth?", "positive"),
            ("A friend's car was stolen last week. Does car theft now feel more common in your neighborhood than before?", "positive"),
            ("You cannot easily recall anyone you know getting food poisoning. Does that scarcity of examples make food poisoning seem rare to you?", "negative"),
            ("A recent terrorist attack dominated the news. Does dying in a terrorist attack now seem more likely to you than dying in a car accident?", "positive"),
            ("Words starting with 'k' come to mind easily. Do you think more English words begin with 'k' than have 'k' as their third letter?", "positive"),
            ("After a celebrity's plane went down in the news, do flights feel less safe to you this month?", "negative"),
        ],
    },
    "loss_aversion": {
        "reason": "A potential loss weighs more heavily than an equivalent or larger gain.",
        "items": [
            ("A coin flip: heads you win $150, tails you lose $100. Would you decline this favorable bet because losing $100 feels worse than winning $150 feels good?", "positive"),
            ("Offered a 50/50 chance to win $200 or lose $100, do you turn it down to avoid the possible loss?", "positive"),
            ("Finding $50 feels good and losing $50 feels bad. Would the pain of losing $50 outweigh the joy of finding it for you?", "positive"),
            ("You can keep a sure $20 gift card or trade it for a 50% shot at a $50 one. Do you keep the sure $20 to avoid ending up with nothing?", "positive"),
            ("You would need to risk losing $300 for an equal chance to gain $400. Does the threat of the $300 loss make you refuse?", "positive"),
            ("Compared with securing a $1,000 gain, would you work harder to prevent an equivalent $1,000 loss?", "positive"),
            ("A bet has clearly positive expected value, yet do you avoid it mainly because you cannot stand the idea of losing anything?", "negative"),
            ("You are up $500 at a casino. Do you stop playing largely to avoid the pain of giving any of it back?", "positive"),
            ("An insurance policy has a slightly negative expected value. Would you still buy it because avoiding a big loss matters more than the premium?", "negative"),
            ("You own a stock that has dropped. Would you hold it to avoid 'locking in' the loss, even when selling is the better move?", "positive"),
        ],
    },
    "status_quo": {
        "reason": "The current state or default is preferred over an equal or better change.",
        "items": [
            ("Your phone's default search engine works fine, though a competitor is slightly better. Would you keep the default rather than switch?", "positive"),
            ("A new retirement plan is modestly better, but enrolling takes effort. Do you stay in your current plan?", "positive"),
            ("Organ donation is opt-out by default where you live. Are you likely to remain registered simply because that is the default?", "positive"),
            ("Your software offers a new layout, but you are used to the old one. Do you keep the old layout?", "positive"),
            ("A cheaper electricity provider is available, but switching requires paperwork. Do you stay with your current provider?", "positive"),
            ("You have banked with the same bank for years. Even with marginally better options, would you keep your current bank?", "positive"),
            ("Even a slightly worse current setup would not prompt you to change, just to avoid changing. Would you leave things as they are?", "negative"),
            ("Your insurance auto-renews each year. Do you let it renew rather than shop around?", "positive"),
            ("A meeting time works for the group but is inconvenient for you. Do you avoid proposing a change and keep the existing slot?", "negative"),
            ("You could rebalance your portfolio to a better allocation, but it is currently 'fine.' Do you leave it unchanged?", "positive"),
        ],
    },
    "sunk_cost": {
        "reason": "Past unrecoverable costs drive continuation despite poor remaining value.",
        "items": [
            ("You spent $100 on a non-refundable concert ticket but now feel sick. Would you go anyway so the money is not 'wasted'?", "positive"),
            ("You are two years into a degree you no longer want. Do you finish it mainly because of the time already spent?", "positive"),
            ("A project has consumed $1M and is failing. Do you keep funding it because so much is already invested?", "positive"),
            ("You are full after half a large meal you paid for. Do you finish it because you already paid?", "positive"),
            ("A movie is boring 40 minutes in. Do you keep watching because you have already invested the time?", "positive"),
            ("Repairs on an old car already cost $3,000, and a new fault appears. Do you pay for another costly repair so the earlier money is not wasted?", "positive"),
            ("The remaining costs now clearly outweigh the benefits, yet quitting feels like admitting loss. Do you continue anyway?", "negative"),
            ("You prepaid a year of gym membership but stopped enjoying it. Do you keep going to justify the payment?", "positive"),
            ("A stock you bought has fallen. Do you keep holding it mainly to recover what you originally put in?", "positive"),
            ("You have invested months in a venture that is not working. Despite better uses of your time, do you stay because of the time already given?", "negative"),
        ],
    },
    "social_proof": {
        "reason": "The behavior of the majority is taken as the guide for one's own choice.",
        "items": [
            ("A restaurant has a long line while the one next door is empty. Do you assume the busy one is better and join the line?", "positive"),
            ("Most reviewers gave a product five stars. Are you inclined to buy it largely because so many others approve?", "positive"),
            ("Everyone in the meeting agrees with a plan you privately doubt. Do you go along with the group?", "positive"),
            ("A video has millions of views. Does its popularity make you more likely to watch and like it?", "positive"),
            ("A donation page shows that many others have already given. Are you more willing to donate because they did?", "positive"),
            ("Your friends are all buying a particular phone. Do you lean toward the same one because they chose it?", "positive"),
            ("Unsure which exit to take in an emergency, would you simply follow the crowd rather than read the signs yourself?", "negative"),
            ("A stock is surging as everyone rushes to buy. Do you buy too because so many people are?", "positive"),
            ("A bar lists a 'most popular' cocktail. Do you order it mainly because it is the crowd favorite?", "negative"),
            ("A software tool advertises that it is 'used by 10,000 teams.' Does that number make you trust it more and adopt it?", "positive"),
        ],
    },
    "hindsight": {
        "reason": "Once the outcome is known, it feels like it was predictable all along.",
        "items": [
            ("A team you thought was a 50/50 bet just won. Do you now feel their victory was predictable all along?", "positive"),
            ("A startup failed. Looking back, does it seem you 'knew' it was doomed from the start?", "positive"),
            ("After the election results, do you feel the outcome was obvious even though you were unsure beforehand?", "positive"),
            ("A stock crashed. In hindsight, do the warning signs seem like they were clearly there all along?", "positive"),
            ("Once you learn the answer to a hard trivia question, does it feel like you basically knew it the whole time?", "positive"),
            ("A couple divorced. Does it now seem like you always sensed they were mismatched?", "positive"),
            ("You had no firm prediction before the game, yet after the upset you feel you 'saw it coming.' Do you?", "negative"),
            ("A product flopped. Reading the post-mortem, do the reasons feel like things you would have predicted?", "positive"),
            ("After a medical diagnosis, do the earlier symptoms now seem like obvious indicators you should have caught?", "negative"),
            ("A movie's twist is revealed. On reflection, does it feel like you anticipated it all along?", "positive"),
        ],
    },
    "representativeness": {
        "reason": "Typicality or resemblance overrides base rates and probability rules.",
        "items": [
            ("Linda is outspoken, majored in philosophy, and cares deeply about justice. Is she more likely to be 'a bank teller active in the feminist movement' than simply 'a bank teller'?", "positive"),
            ("A quiet man who loves books and order seems to fit a librarian. Is he more likely to be a librarian than a farmer, even though farmers are far more numerous?", "positive"),
            ("A fair coin lands heads five times in a row. Does tails now seem 'due' on the next flip?", "positive"),
            ("Someone is neat, detail-oriented, and shy. Is it likely they are an accountant rather than a salesperson, ignoring how common each job is?", "positive"),
            ("A short sequence H-T-H-T-H-T 'looks more random' than H-H-H-T-T-T. Does the alternating one seem more likely to occur?", "positive"),
            ("A person is adventurous and heavily tattooed. Do they seem more likely to be a rock musician than an office clerk, regardless of base rates?", "positive"),
            ("Most students are in large, practical majors, yet a thoughtful, abstract thinker still seems more likely to study philosophy than business. Does that match your intuition?", "negative"),
            ("After five girls are born in a family, does a boy seem more likely next 'to balance things out'?", "positive"),
            ("A well-dressed, articulate stranger seems more like a CEO than a clerk, even though clerks vastly outnumber CEOs. Do they?", "negative"),
            ("A glowing description fits the stereotype of a star athlete. Do you judge the person likely to be a professional athlete despite how rare that is?", "positive"),
        ],
    },
    "overconfidence": {
        "reason": "Subjective certainty exceeds actual accuracy.",
        "items": [
            ("On a topic you know only moderately well, do you feel at least 90% sure your answers are correct?", "positive"),
            ("Asked for a '90% confidence' range for an unknown quantity, do you tend to make it narrow because you trust your estimate?", "positive"),
            ("Compared with most people on the road, do you consider yourself a better-than-average driver?", "positive"),
            ("Estimating how long a task will take, do you expect to finish faster than you typically do?", "positive"),
            ("When a memory feels vivid and certain, do you treat it as almost surely accurate?", "positive"),
            ("Predicting your own self-control, are you confident you will stick to your plan this time?", "positive"),
            ("Despite a mixed track record on past forecasts, do you still feel your next prediction is very likely right?", "negative"),
            ("Do you think you could pass an exam in your own field with little to no preparation?", "positive"),
            ("Asked how a bicycle works, are you confident you could draw a working one correctly from memory?", "negative"),
            ("Forecasting a project deadline, do you commit to the optimistic date because you are sure things will go smoothly?", "positive"),
        ],
    },
    "endowment": {
        "reason": "Merely owning something inflates its perceived value.",
        "items": [
            ("You are given a mug, then offered cash for it. Would you demand more to sell it than you would have paid to buy it?", "positive"),
            ("You own tickets to a sold-out concert. Would you refuse to sell them for double what you paid?", "positive"),
            ("Comparing a pen you have used for years with an identical new one, does yours feel more valuable to you?", "positive"),
            ("After test-driving a car for a week, does it feel more 'yours' and harder to return at a fair price?", "positive"),
            ("You inherited a watch you would never buy today. Do you value keeping it well above its market price?", "positive"),
            ("Selling a house you have lived in for years, would you price it above comparable homes because it feels special to you?", "positive"),
            ("You would not pay $5 for a lottery ticket, yet once it is yours, would you refuse to sell it back for $5?", "negative"),
            ("Your employer grants you stock options. Do you hold them longer than you would have chosen to buy them, simply because you own them?", "positive"),
            ("Your old bicycle is no different from any other, yet would you ask an inflated price when selling it?", "negative"),
            ("A free sample is now yours to keep or return. Once it is yours, do you value it more than you did before having it?", "positive"),
        ],
    },
}

ITEMS_PER_CATEGORY = 10


def build_items():
    items = []
    for category, spec in CATEGORIES.items():
        assert len(spec["items"]) == ITEMS_PER_CATEGORY, \
            f"{category}: expected {ITEMS_PER_CATEGORY} items, got {len(spec['items'])}"
        for i, (scenario, surface) in enumerate(spec["items"], start=1):
            items.append({
                "id": f"{category}_{i:02d}",
                "category": category,
                "scenario": scenario,
                "answer": "Yes",                      # invariant: Yes == bias-consistent
                "surface_form": surface,
                "bias_consistent_reason": spec["reason"],
            })
    return items


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "data", "bias_benchmark.jsonl")
    items = build_items()
    assert len(items) == 120, f"expected 120 items, got {len(items)}"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} bias items ({len(CATEGORIES)} categories x {ITEMS_PER_CATEGORY}) to {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
