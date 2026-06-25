#!/usr/bin/env python3
"""Generate 100 matched gain/loss financial framing pairs (Section 3.3).

Each pair shares numeric parameters and flips only the wording between a gain
and a loss frame. Decision skeleton is fixed: A = Certain, B = Risky.
Amounts/probabilities come from bounded grids and are filtered so the risky and
certain options have comparable expected value (within a small tolerance),
avoiding trivial dominance.

  EV(certain) = X
  EV(risky)   = p * Y     (Y paid with prob p, else 0)
  keep pair iff |p*Y - X| / X <= TOL

Deterministic: a fixed seed selects 100 pairs from the filtered candidate set.
"""
import argparse
import json
import os
import random

# Bounded grids
WEALTH_GRID = [10000, 20000, 50000, 100000]
CERTAIN_GRID = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000]  # X
PROB_GRID = [0.25, 0.4, 0.5, 0.6, 0.75]                                # p
SNAP = 100        # risky payoff Y snapped to nearest $100
TOL = 0.03        # max relative EV gap between certain and risky
SEED = 20260620
N_PAIRS = 100


def render_gain(w, x, y, p):
    pct = int(round(p * 100))
    return (
        f"Now, you have ${w:,}. The market is uncertain. "
        f"Choose one of the following two options:\n"
        f"Option A (Certain): You will gain ${x:,}.\n"
        f"Option B (Risky): {pct}% chance to gain ${y:,}, "
        f"{100 - pct}% chance to gain nothing."
    )


def render_loss(w, x, y, p):
    pct = int(round(p * 100))
    return (
        f"Now, you have ${w:,}. The market is uncertain. "
        f"Choose one of the following two options:\n"
        f"Option A (Certain): You will lose ${x:,}.\n"
        f"Option B (Risky): {pct}% chance to lose ${y:,}, "
        f"{100 - pct}% chance to lose nothing."
    )


def build_candidates():
    cands = []
    seen = set()
    for w in WEALTH_GRID:
        for x in CERTAIN_GRID:
            for p in PROB_GRID:
                y = int(round((x / p) / SNAP) * SNAP)   # Y so that p*Y ~= X
                if y <= x:
                    continue                            # risky upside must exceed certain
                if y > w:
                    continue                            # keep amounts within endowment
                ev_risky = p * y
                if abs(ev_risky - x) / x > TOL:
                    continue
                key = (w, x, y, p)
                if key in seen:
                    continue
                seen.add(key)
                cands.append({"wealth": w, "certain": x, "risky": y, "prob": p,
                              "ev_certain": float(x), "ev_risky": round(ev_risky, 2)})
    return cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data", "financial_tasks.jsonl"))
    args = ap.parse_args()

    cands = build_candidates()
    if len(cands) < N_PAIRS:
        raise SystemExit(f"only {len(cands)} EV-matched candidates; widen the grids")

    rng = random.Random(SEED)
    rng.shuffle(cands)
    chosen = sorted(cands[:N_PAIRS], key=lambda c: (c["wealth"], c["prob"], c["certain"]))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        for i, c in enumerate(chosen):
            rec = {
                "id": f"fin_{i:03d}",
                "wealth": c["wealth"],
                "prob": c["prob"],
                "certain_amount": c["certain"],
                "risky_amount": c["risky"],
                "ev_certain": c["ev_certain"],
                "ev_risky": c["ev_risky"],
                "decision_skeleton": {"A": "Certain", "B": "Risky"},
                "gain_frame": render_gain(c["wealth"], c["certain"], c["risky"], c["prob"]),
                "loss_frame": render_loss(c["wealth"], c["certain"], c["risky"], c["prob"]),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    max_gap = max(abs(c["ev_risky"] - c["ev_certain"]) / c["ev_certain"] for c in chosen)
    print(f"Candidates: {len(cands)}; wrote {len(chosen)} pairs to {os.path.normpath(args.out)}")
    print(f"Max relative EV gap among chosen pairs: {max_gap:.3%} (tol={TOL:.0%})")


if __name__ == "__main__":
    main()
