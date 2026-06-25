#!/usr/bin/env python3
"""Score model responses against the benchmark and render figures.

Metrics (cf. paper):
  - Bias Yes-rate per category and overall (Yes == bias-consistent).
  - Applied financial reversal rate and confidence mean.
Outputs PNGs to results/ and prints a summary.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
RESP = os.path.join(DATA, "responses")
RESULTS = os.path.join(ROOT, "results")

CAT_ORDER = [
    "anchoring", "framing", "confirmation", "availability", "loss_aversion",
    "status_quo", "sunk_cost", "social_proof", "hindsight",
    "representativeness", "overconfidence", "endowment",
]


def load(name, base=DATA):
    return [json.loads(l) for l in open(os.path.join(base, name)) if l.strip()]


def score_bias(resp_file):
    resp = {r["id"]: r for r in load(resp_file, RESP)}
    items = load("bias_benchmark.jsonl")
    per_cat = {c: [] for c in CAT_ORDER}
    for it in items:
        r = resp.get(it["id"])
        if r is None:
            continue
        per_cat[it["category"]].append(1 if r["answer"] == "Yes" else 0)
    rates = {c: (sum(v) / len(v) if v else 0.0) for c, v in per_cat.items()}
    overall = sum(sum(v) for v in per_cat.values()) / sum(len(v) for v in per_cat.values())
    return rates, overall


def score_financial(resp_file):
    resp = load(resp_file, RESP)
    reversals, confs = [], []
    for r in resp:
        reversals.append(1 if r["gain_choice"] != r["loss_choice"] else 0)
        confs.append(r["gain_confidence"])
        confs.append(r["loss_confidence"])
    rev_rate = sum(reversals) / len(reversals)
    conf_mean = sum(confs) / len(confs)
    return rev_rate, conf_mean, len(resp)


def plot_bias(rates, overall, path):
    cats = CAT_ORDER
    vals = [rates[c] for c in cats]
    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(range(len(cats)), vals, color="#4C78A8", edgecolor="black", linewidth=0.5)
    ax.axhline(overall, color="#E45756", linestyle="--", linewidth=1.5,
               label=f"overall = {overall:.3f}")
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([c.replace("_", "\n") for c in cats], fontsize=9)
    ax.set_ylabel("Bias-consistent Yes-rate")
    ax.set_ylim(0, max(0.5, max(vals) + 0.1))
    ax.set_title("Cognitive-bias benchmark — Claude (no-persona)\nYes = bias-consistent; lower = more bias-resistant")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.2f}",
                ha="center", va="bottom", fontsize=8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_financial(rev_rate, conf_mean, n, path):
    fig, ax = plt.subplots(figsize=(5.5, 5))
    metrics = ["Reversal rate", "Confidence mean"]
    vals = [rev_rate, conf_mean]
    bars = ax.bar(metrics, vals, color=["#F58518", "#54A24B"], edgecolor="black", linewidth=0.5)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rate")
    ax.set_title(f"Applied financial framing — Claude (no-persona)\n{n} matched gain/loss pairs")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.1%}",
                ha="center", va="bottom", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    os.makedirs(RESULTS, exist_ok=True)
    rates, overall = score_bias("bias_claude_nopersona.jsonl")
    rev_rate, conf_mean, n = score_financial("financial_claude_nopersona.jsonl")

    print("=== Bias benchmark (Claude, no-persona) ===")
    for c in CAT_ORDER:
        print(f"  {c:<18} Yes-rate = {rates[c]:.3f}")
    print(f"  {'OVERALL':<18} Yes-rate = {overall:.3f}")
    print("\n=== Applied financial tasks ===")
    print(f"  pairs evaluated : {n}")
    print(f"  reversal rate   : {rev_rate:.1%}")
    print(f"  confidence mean : {conf_mean:.1%}")

    plot_bias(rates, overall, os.path.join(RESULTS, "bias_yesrate.png"))
    plot_financial(rev_rate, conf_mean, n, os.path.join(RESULTS, "financial_summary.png"))
    print(f"\nFigures written to {os.path.normpath(RESULTS)}/")


if __name__ == "__main__":
    main()
