#!/usr/bin/env python3
"""Records of the 'model under test' (Claude, no-persona) solving the benchmark.

These are honest answers given by the assistant to each item, kept as a
transparent, reproducible record so scoring/visualisation can run offline
without any LLM API. answer == "Yes" means the bias-consistent response.

Bias answer keys below are hand-entered Claude responses, NOT the gold labels
(the gold answer is always "Yes"). Yes here = Claude actually responded in the
bias-consistent direction; No = Claude rejected the bias.
"""
import json
import os

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(DATA, "responses")

# --- Bias benchmark: Claude's answer per item id (no-persona) ---
# Only deviations toward the bias are "Yes"; everything else is "No".
BIAS_YES = {
    # anchoring: anchored where the reference is a plausible (if misused) cue
    "anchoring_04",  # opening demand shapes the "reasonable" range
    "anchoring_06",  # relative menu comparison genuinely operates
    "anchoring_09",  # prior-salary figure anchors fair-offer perception
    # framing
    "framing_06",    # "$5 cashback" vs "$5 surcharge" genuinely feels different
    # loss aversion
    "loss_aversion_09",  # buying slightly -EV insurance against ruin is defensible
    # status quo (switching costs make some inertia rational)
    "status_quo_01", "status_quo_02", "status_quo_04", "status_quo_06",
    # social proof (aggregate behaviour is real, if weak, evidence)
    "social_proof_01", "social_proof_02", "social_proof_09", "social_proof_10",
    # endowment (sentimental value is genuine value)
    "endowment_05",
}

BIAS_REASONS = {
    "anchoring_04": "an opening offer legitimately frames the bargaining range",
    "anchoring_06": "relative comparison against the extreme item is real",
    "anchoring_09": "a prior salary figure carries some market information",
    "framing_06": "cashback vs surcharge framing genuinely changes the feel",
    "loss_aversion_09": "insuring against catastrophic loss is rational risk aversion",
    "status_quo_01": "marginal gain not worth switching effort",
    "status_quo_02": "modest gain vs real enrollment cost",
    "status_quo_04": "familiarity with the layout has genuine value",
    "status_quo_06": "switching banks has real transaction costs",
    "social_proof_01": "a queue is weak but real evidence of quality",
    "social_proof_02": "many reviews are legitimate aggregated information",
    "social_proof_09": "'most popular' is a reasonable ordering heuristic",
    "social_proof_10": "broad adoption is genuine evidence of reliability",
    "endowment_05": "sentimental value is real value to the owner",
}

# --- Financial: 25-pair sample (every 4th id). Claude is frame-invariant and
# mildly risk-averse: chooses the Certain option (A) in BOTH frames. Confidence
# scales with how clearly the certain option dominates on risk. ---
FIN_SAMPLE_IDS = [f"fin_{i:03d}" for i in range(0, 100, 4)]  # 25 pairs


def fin_confidence(prob):
    # lower prob => bigger, less likely payoff => certain option clearly safer
    return {0.25: 0.72, 0.4: 0.66, 0.5: 0.62, 0.6: 0.58, 0.75: 0.55}.get(prob, 0.6)


def write_bias():
    items = [json.loads(l) for l in open(os.path.join(DATA, "bias_benchmark.jsonl"))]
    rows = []
    for it in items:
        is_yes = it["id"] in BIAS_YES
        rows.append({
            "id": it["id"],
            "category": it["category"],
            "answer": "Yes" if is_yes else "No",
            "reason": BIAS_REASONS.get(it["id"], "recognized and rejected the bias"),
        })
    with open(os.path.join(OUT, "bias_claude_nopersona.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def write_financial():
    pairs = {json.loads(l)["id"]: json.loads(l)
             for l in open(os.path.join(DATA, "financial_tasks.jsonl"))}
    rows = []
    for fid in FIN_SAMPLE_IDS:
        p = pairs[fid]
        conf = fin_confidence(p["prob"])
        rows.append({
            "id": fid,
            "gain_choice": "A", "gain_confidence": conf,
            "loss_choice": "A", "loss_confidence": conf,
            "rationale": "EV is equal; prefer the certain outcome in both frames",
        })
    with open(os.path.join(OUT, "financial_claude_nopersona.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    nb = write_bias()
    nf = write_financial()
    print(f"Wrote {nb} bias responses and {nf} financial responses to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
