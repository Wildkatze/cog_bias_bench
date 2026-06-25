#!/usr/bin/env python3
"""Validate all rebuilt datasets against the paper's specification.

Checks the normalization constraints and structural invariants so the rebuild
can be trusted as a drop-in replacement for the lost originals.
Exit code 0 = all checks pass; 1 = at least one failure.
"""
import json
import os
import sys

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
EXPECTED_CATEGORIES = {
    "anchoring", "framing", "confirmation", "availability", "loss_aversion",
    "status_quo", "sunk_cost", "social_proof", "hindsight",
    "representativeness", "overconfidence", "endowment",
}

errors = []
checks = []


def ok(cond, msg):
    checks.append((bool(cond), msg))
    if not cond:
        errors.append(msg)


def load_jsonl(name):
    with open(os.path.join(DATA, name)) as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------- Bias benchmark ----------------
def check_bias():
    items = load_jsonl("bias_benchmark.jsonl")
    ok(len(items) == 120, f"bias: 120 items (got {len(items)})")
    cats = {}
    ids, scenarios = set(), set()
    for it in items:
        cats.setdefault(it["category"], []).append(it)
        ids.add(it["id"])
        scenarios.add(it["scenario"].strip().lower())
        ok(it["answer"] == "Yes", f"bias: {it['id']} answer must be 'Yes' (invariant)")
        ok(it["surface_form"] in {"positive", "negative"}, f"bias: {it['id']} surface_form valid")
        ok(it["scenario"].strip().endswith("?"), f"bias: {it['id']} scenario ends with a Yes/No question")
    ok(set(cats) == EXPECTED_CATEGORIES, "bias: exactly the 12 expected categories present")
    for c, lst in cats.items():
        ok(len(lst) == 10, f"bias: category '{c}' has 10 items (got {len(lst)})")
        forms = {x["surface_form"] for x in lst}
        ok("positive" in forms and "negative" in forms,
           f"bias: category '{c}' varies surface wording (has both positive & negative)")
    ok(len(ids) == 120, f"bias: ids unique (got {len(ids)})")
    ok(len(scenarios) == 120, f"bias: scenarios unique (got {len(scenarios)})")


# ---------------- Personas ----------------
def check_personas():
    p = load_jsonl("personas.jsonl")
    ok(len(p) == 162, f"persona: 162 personas (got {len(p)})")
    keys = {(x["gender"], x["age"], x["politics"], x["income"], x["education"]) for x in p}
    ok(len(keys) == 162, f"persona: 162 unique factorial keys (got {len(keys)})")
    total_w = sum(x["weight"] for x in p)
    ok(abs(total_w - 1.0) < 1e-6, f"persona: weights sum to 1.0 (got {total_w:.6f})")
    for x in p:
        ok(x["weight"] > 0, f"persona: {x['id']} weight positive")
        ok(x["persona_text"].startswith("a "), f"persona: {x['id']} has natural-language text")
    meta = json.load(open(os.path.join(DATA, "persona_fields.json")))
    ok(len(meta["countries"]) == 8, "persona: 8 country values")
    ok(len(meta["occupations"]) == 8, "persona: 8 occupation values")


# ---------------- Financial tasks ----------------
def check_financial():
    f = load_jsonl("financial_tasks.jsonl")
    ok(len(f) == 100, f"financial: 100 matched pairs (got {len(f)})")
    ids = set()
    for r in f:
        ids.add(r["id"])
        gap = abs(r["ev_risky"] - r["ev_certain"]) / r["ev_certain"]
        ok(gap <= 0.03 + 1e-9, f"financial: {r['id']} EV gap <= 3% (got {gap:.3%})")
        ok(r["risky_amount"] > r["certain_amount"], f"financial: {r['id']} risky upside exceeds certain (no trivial dominance)")
        ok(r["decision_skeleton"] == {"A": "Certain", "B": "Risky"}, f"financial: {r['id']} fixed A/B skeleton")
        g, l = r["gain_frame"].lower(), r["loss_frame"].lower()
        ok("gain" in g and "lose" not in g, f"financial: {r['id']} gain frame uses gain wording")
        ok("lose" in l and "gain" not in l, f"financial: {r['id']} loss frame uses loss wording")
        # frames must share identical numeric parameters
        for amt in (f"${r['certain_amount']:,}", f"${r['risky_amount']:,}", f"${r['wealth']:,}"):
            ok(amt in r["gain_frame"] and amt in r["loss_frame"],
               f"financial: {r['id']} gain/loss share parameter {amt}")
    ok(len(ids) == 100, f"financial: ids unique (got {len(ids)})")


def main():
    check_bias()
    check_personas()
    check_financial()
    passed = sum(1 for c, _ in checks if c)
    print(f"Checks passed: {passed}/{len(checks)}")
    if errors:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All datasets conform to the paper specification.")


if __name__ == "__main__":
    main()
