#!/usr/bin/env python3
"""Persona-conditioned scoring + visualisation.

Compares bias Yes-rate and applied framing behaviour across persona conditions
(all Sonnet, one attribute swapped from a common centre) plus no-persona
baselines. Renders four figures into results/.
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
RESP = os.path.join(DATA, "responses")
RESULTS = os.path.join(ROOT, "results")

CAT_ORDER = [
    "anchoring", "framing", "confirmation", "availability", "loss_aversion",
    "status_quo", "sunk_cost", "social_proof", "hindsight",
    "representativeness", "overconfidence", "endowment",
]

# display order + labels for persona conditions
CONDITIONS = [
    ("none_sonnet",      "no-persona\n(Sonnet)"),
    ("center",           "centre\n(mod/mid/univ)"),
    ("pol_liberal",      "politics:\nliberal"),
    ("pol_conservative", "politics:\nconservative"),
    ("inc_low",          "income:\nlow"),
    ("inc_high",         "income:\nhigh"),
    ("edu_highschool",   "education:\nhigh school"),
    ("edu_graduate",     "education:\ngraduate"),
]

ITEM_CAT = {json.loads(l)["id"]: json.loads(l)["category"]
            for l in open(os.path.join(DATA, "bias_benchmark.jsonl"))}


def load_condition(pid):
    d = json.load(open(os.path.join(RESP, f"persona_{pid}.json")))
    return d["bias"], d["financial"]


def bias_rates(bias):
    per_cat = {c: [] for c in CAT_ORDER}
    for b in bias:
        per_cat[ITEM_CAT[b["id"]]].append(1 if b["answer"] == "Yes" else 0)
    rates = {c: (sum(v) / len(v) if v else 0.0) for c, v in per_cat.items()}
    overall = sum(sum(v) for v in per_cat.values()) / sum(len(v) for v in per_cat.values())
    return rates, overall


def framing_coords(fin):
    # x = rate of choosing A (safe) in gain frame; y = rate of choosing B (risky) in loss frame
    x = np.mean([1 if r["gain_choice"] == "A" else 0 for r in fin])
    y = np.mean([1 if r["loss_choice"] == "B" else 0 for r in fin])
    rev = np.mean([1 if r["gain_choice"] != r["loss_choice"] else 0 for r in fin])
    conf = np.mean([r["gain_confidence"] for r in fin] + [r["loss_confidence"] for r in fin])
    return x, y, rev, conf


def opus_baseline():
    bias = [{"id": r["id"], "answer": r["answer"]}
            for r in (json.loads(l) for l in open(os.path.join(RESP, "bias_claude_nopersona.jsonl")))]
    fin = [json.loads(l) for l in open(os.path.join(RESP, "financial_claude_nopersona.jsonl"))]
    return bias, fin


def main():
    os.makedirs(RESULTS, exist_ok=True)
    data = {}
    for pid, _ in CONDITIONS:
        bias, fin = load_condition(pid)
        rates, overall = bias_rates(bias)
        x, y, rev, conf = framing_coords(fin)
        data[pid] = dict(rates=rates, overall=overall, x=x, y=y, rev=rev, conf=conf)
    ob, of = opus_baseline()
    opus_rates, opus_overall = bias_rates(ob)
    ox, oy, orev, oconf = framing_coords([
        {"gain_choice": r["gain_choice"], "loss_choice": r["loss_choice"],
         "gain_confidence": r["gain_confidence"], "loss_confidence": r["loss_confidence"]} for r in of])

    labels = [lab for _, lab in CONDITIONS]
    pids = [pid for pid, _ in CONDITIONS]

    # ---- Figure 1: overall Yes-rate by condition ----
    fig, ax = plt.subplots(figsize=(11, 5))
    vals = [data[p]["overall"] for p in pids]
    colors = ["#9D9D9D", "#4C78A8", "#72B7B2", "#1F6F8B", "#F2A93B", "#B8860B", "#88C580", "#3E7A2E"]
    bars = ax.bar(range(len(pids)), vals, color=colors, edgecolor="black", linewidth=0.5)
    ax.axhline(opus_overall, color="#E45756", linestyle="--", linewidth=1.5,
               label=f"no-persona (Opus, ref) = {opus_overall:.3f}")
    ax.set_xticks(range(len(pids)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Bias-consistent Yes-rate")
    ax.set_ylim(0, 1.0)
    ax.set_title("Persona conditioning shifts bias-consistent responding\n(Yes = bias-consistent; one attribute swapped from the centre persona)")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.legend(loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "persona_yesrate_overall.png"), dpi=130); plt.close(fig)

    # ---- Figure 2: category x persona heatmap ----
    mat = np.array([[data[p]["rates"][c] for p in pids] for c in CAT_ORDER])
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(len(pids))); ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks(range(len(CAT_ORDER))); ax.set_yticklabels(CAT_ORDER, fontsize=9)
    for i in range(len(CAT_ORDER)):
        for j in range(len(pids)):
            ax.text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center", fontsize=7,
                    color="black" if mat[i, j] < 0.6 else "white")
    ax.set_title("Per-category Yes-rate by persona condition")
    fig.colorbar(im, ax=ax, label="Yes-rate", shrink=0.8)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "persona_category_heatmap.png"), dpi=130); plt.close(fig)

    # ---- Figure 3: framing map (small jitter so coincident points are visible) ----
    fig, ax = plt.subplots(figsize=(8, 7))
    jit = [(-0.012, 0.012), (0.012, 0.012), (-0.012, -0.012), (0.012, -0.012),
           (-0.024, 0.0), (0.024, 0.0), (0.0, 0.024), (0.0, -0.024)]
    for (pid, lab), (dx, dy), col in zip(CONDITIONS, jit, colors):
        ax.scatter(data[pid]["x"] + dx, data[pid]["y"] + dy, s=140, color=col,
                   edgecolor="black", zorder=3, label=lab.replace("\n", " "))
    ax.scatter(ox, oy, s=200, marker="*", color="#E45756", edgecolor="black", zorder=4, label="no-persona (Opus)")
    ax.set_xlim(0.4, 1.08); ax.set_ylim(-0.08, 1.08)
    ax.set_xlabel("P(choose A = safe | gain frame)")
    ax.set_ylabel("P(choose B = risky | loss frame)")
    ax.set_title("Framing map (per condition)\ntop-right = classic framing (high reversal); bottom-right = frame-invariant")
    ax.axhline(0.5, color="gray", lw=0.5); ax.axvline(0.5, color="gray", lw=0.5)
    ax.legend(loc="center left", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "persona_framing_map.png"), dpi=130); plt.close(fig)

    # ---- Figure 4: attribute contrasts (mirror Table 5) ----
    axes_def = [
        ("Politics", ["pol_liberal", "center", "pol_conservative"], ["liberal", "moderate", "conservative"]),
        ("Income",   ["inc_low", "center", "inc_high"],             ["low", "middle", "high"]),
        ("Education", ["edu_highschool", "center", "edu_graduate"], ["high school", "university", "graduate"]),
    ]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, (name, ids, ticks) in zip(axs, axes_def):
        vals = [data[i]["overall"] for i in ids]
        ax.bar(range(3), vals, color="#4C78A8", edgecolor="black", linewidth=0.5)
        ax.set_xticks(range(3)); ax.set_xticklabels(ticks, fontsize=9)
        ax.set_title(name)
        for k, v in enumerate(vals):
            ax.text(k, v + 0.01, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    axs[0].set_ylabel("Bias-consistent Yes-rate")
    axs[0].set_ylim(0, 1.0)
    fig.suptitle("Attribute-level contrasts (each swaps one attribute from the centre persona)")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "persona_attribute_contrasts.png"), dpi=130); plt.close(fig)

    # ---- console summary ----
    print("Condition           Yes-rate  Reversal  Confidence")
    print(f"{'no-persona (Opus)':<19} {opus_overall:>7.3f}  {orev:>7.1%}  {oconf:>9.1%}")
    for pid, lab in CONDITIONS:
        d = data[pid]
        print(f"{pid:<19} {d['overall']:>7.3f}  {d['rev']:>7.1%}  {d['conf']:>9.1%}")
    print(f"\nFigures written to {os.path.normpath(RESULTS)}/")


if __name__ == "__main__":
    main()
