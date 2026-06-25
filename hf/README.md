---
license: cc-by-4.0
language:
- en
pretty_name: Persona-Aware Cognitive-Bias Benchmark
size_categories:
- n<1K
task_categories:
- text-classification
- question-answering
tags:
- cognitive-bias
- llm-evaluation
- persona
- framing
- behavioral-economics
- decision-making
configs:
- config_name: bias_benchmark
  default: true
  data_files:
  - split: test
    path: bias_benchmark.jsonl
- config_name: personas
  data_files:
  - split: test
    path: personas.jsonl
- config_name: financial_tasks
  data_files:
  - split: test
    path: financial_tasks.jsonl
---

# Persona-Aware Cognitive-Bias Benchmark

Data resources from the LREC 2026 paper **"Persona-Aware Evaluation of Cognitive
Bias in LLMs: From Benchmark to Applied Decision-Making"** (Yoshikawa, Takayama,
Yamazaki). The suite couples a 12-category cognitive-bias benchmark with a
factorial persona space and an applied financial-framing task, to study how
persona conditioning modulates bias-consistent responding in LLMs.

> **Reconstruction notice.** The original construction data was lost. The 120
> bias items here were **re-authored to the paper's specification** (same
> construct, format, invariant, and controls) and are **not** the identical
> strings used in the paper's experiments. Absolute Yes-rates a model produces
> may therefore differ from the paper's tables. The persona space and financial
> tasks are regenerated deterministically and match the paper exactly.

## Subsets

### `bias_benchmark` (120 items)
12 cognitive-bias categories × 10 items. Each item is a short vignette ending in
a Yes/No question. **Invariant: the bias-consistent answer is always `"Yes"`.**

| field | type | description |
|---|---|---|
| `id` | string | e.g. `availability_01` |
| `category` | string | one of 12 categories |
| `scenario` | string | vignette + Yes/No question |
| `answer` | string | gold label, always `"Yes"` (bias-consistent) |
| `surface_form` | string | `positive` / `negative` wording variant |
| `bias_consistent_reason` | string | why Yes is the bias-consistent response |

Categories: anchoring, framing, confirmation, availability, loss_aversion,
status_quo, sunk_cost, social_proof, hindsight, representativeness,
overconfidence, endowment.

### `personas` (162 personas)
Factorial Gender(2) × Age(3) × Politics(3) × Income(3) × Education(3) = 162, each
with a marginal-product weight `w(p)` for weighted aggregation.

| field | type | description |
|---|---|---|
| `id` | string | `persona_000` … `persona_161` |
| `gender` / `age` / `politics` / `income` / `education` | — | attribute values |
| `weight` | float | `P(g)P(a)P(pol)P(inc)P(edu)`; the 162 weights sum to 1 |
| `persona_text` | string | natural-language preface ("a 40-year-old male with …") |

Country (8) and Occupation (8) are **uniform, non-stratified** randomization
fields (not part of the 162-key); their value lists ship in the repo's
`persona_fields.json`.

### `financial_tasks` (100 matched pairs)
Matched gain/loss framing pairs. Fixed decision skeleton A=Certain, B=Risky; each
pair shares numeric parameters and flips only the wording. Amounts/probabilities
are filtered so EV(certain) ≈ EV(risky) (≤3% relative gap).

| field | type | description |
|---|---|---|
| `id` | string | `fin_000` … `fin_099` |
| `wealth` / `prob` / `certain_amount` / `risky_amount` | num | parameters |
| `ev_certain` / `ev_risky` | float | expected values (matched) |
| `gain_frame` / `loss_frame` | string | rendered prompts |

## Usage

```python
from datasets import load_dataset

bias = load_dataset("katsumasay/cog-bias-bench", "bias_benchmark", split="test")
personas = load_dataset("katsumasay/cog-bias-bench", "personas", split="test")
fin = load_dataset("katsumasay/cog-bias-bench", "financial_tasks", split="test")
```

**Metrics (from the paper):** Yes-rate (bias-consistent rate; weighted by `w(p)`
under persona aggregation), reversal rate, and confidence mean. Persona weights
are applied at **aggregation** time only; all 162 personas are sampled uniformly
when running a model. Output schemas: bias `{"answer":"Yes/No","reason":"..."}`;
financial `{"choice":"A/B","confidence":0.0-1.0,"rationale":"..."}`.

## Intended use & limitations

- **Intended use:** evaluating cognitive-bias susceptibility and persona
  sensitivity of LLMs. Research only.
- **Not** a measure of human bias, nor a fairness/social-bias dataset (cf. BBQ,
  StereoSet) — it targets behavioral–cognitive biases.
- Items are English and necessarily stylized; absolute scores are model- and
  prompt-dependent. Treat small per-category samples (n=10) as indicative.

## Ethical considerations

Personas include sensitive attributes (political orientation, income, education).
They are coarse, synthetic constructs for controlled evaluation and must not be
used to profile, stereotype, or make decisions about real individuals.

## License & citation

Data: **CC BY 4.0**. (Repository code: Apache-2.0.)

```bibtex
@inproceedings{yoshikawa2026persona,
  title     = {Persona-Aware Evaluation of Cognitive Bias in {LLM}s: From Benchmark to Applied Decision-Making},
  author    = {Yoshikawa, Katsumasa and Takayama, Junya and Yamazaki, Takato},
  booktitle = {Proceedings of the 2026 Conference on Language Resources and Evaluation (LREC 2026)},
  year      = {2026}
}
```

Code & reproduction scripts: https://github.com/Wildkatze/cog_bias_bench
