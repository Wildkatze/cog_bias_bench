#!/usr/bin/env python3
"""Generate the factorial persona space (162 personas) described in the paper.

Persona key = Gender(2) x Age(3) x Politics(3) x Income(3) x Education(3) = 162.
Each persona carries a marginal-product weight w(p) (Eq. 2) used for weighted
aggregation. Country and Occupation are NON-stratified randomization fields:
they are NOT part of the 162 key and are sampled uniformly per prompt instance.

This script is fully deterministic and reproduces the persona space exactly.
"""
import argparse
import itertools
import json
import os

# --- Factorial attributes with marginal weights (Table 2) ---
ATTRIBUTES = {
    "gender": {"male": 0.5, "female": 0.5},
    "age": {"25": 0.3, "40": 0.4, "60": 0.3},
    "politics": {"liberal": 0.3, "moderate": 0.3, "conservative": 0.4},
    "income": {"low": 0.3, "middle": 0.5, "high": 0.2},
    "education": {"high school": 0.5, "university": 0.4, "graduate": 0.1},
}

# --- Non-stratified randomization fields (uniform, not part of the key) ---
COUNTRIES = ["USA", "Germany", "India", "Brazil", "Kenya", "France", "China", "Japan"]
OCCUPATIONS = ["student", "engineer", "teacher", "doctor", "artist", "farmer", "manager", "freelancer"]

# Display order for attribute values (keeps output stable/readable)
ORDER = {attr: list(vals.keys()) for attr, vals in ATTRIBUTES.items()}


def persona_text(g, a, pol, inc, edu):
    """Natural-language persona string prepended to the prompt as 'You are {persona}.'"""
    edu_phrase = {
        "high school": "a high-school education",
        "university": "a university education",
        "graduate": "a graduate-school education",
    }[edu]
    return (
        f"a {a}-year-old {g} with {pol} political views, "
        f"{inc} income, and {edu_phrase}"
    )


def build_personas():
    personas = []
    combos = itertools.product(
        ORDER["gender"], ORDER["age"], ORDER["politics"],
        ORDER["income"], ORDER["education"],
    )
    for idx, (g, a, pol, inc, edu) in enumerate(combos):
        w = (
            ATTRIBUTES["gender"][g]
            * ATTRIBUTES["age"][a]
            * ATTRIBUTES["politics"][pol]
            * ATTRIBUTES["income"][inc]
            * ATTRIBUTES["education"][edu]
        )
        personas.append({
            "id": f"persona_{idx:03d}",
            "gender": g,
            "age": int(a),
            "politics": pol,
            "income": inc,
            "education": edu,
            "weight": round(w, 6),
            "persona_text": persona_text(g, a, pol, inc, edu),
        })
    return personas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data", "personas.jsonl"))
    ap.add_argument("--meta-out", default=os.path.join(os.path.dirname(__file__), "..", "data", "persona_fields.json"))
    args = ap.parse_args()

    personas = build_personas()
    assert len(personas) == 162, f"expected 162 personas, got {len(personas)}"
    total_w = sum(p["weight"] for p in personas)
    assert abs(total_w - 1.0) < 1e-6, f"persona weights must sum to 1, got {total_w}"

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        for p in personas:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with open(args.meta_out, "w") as f:
        json.dump({
            "countries": COUNTRIES,
            "occupations": OCCUPATIONS,
            "attributes": ATTRIBUTES,
            "note": "country/occupation are uniform, non-stratified randomization fields; not part of the 162-persona key.",
        }, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(personas)} personas to {os.path.normpath(args.out)} (weights sum={total_w:.6f})")
    print(f"Wrote randomization fields to {os.path.normpath(args.meta_out)}")


if __name__ == "__main__":
    main()
