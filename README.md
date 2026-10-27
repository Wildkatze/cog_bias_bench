# Persona-Aware Cognitive-Bias Benchmark

[![Code: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-green.svg)](data/LICENSE)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-dataset-yellow.svg)](https://huggingface.co/datasets/katsumasay/cog-bias-bench)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20845756.svg)](https://doi.org/10.5281/zenodo.20845756)

Data resources from the LREC 2026 paper
*"Persona-Aware Evaluation of Cognitive Bias in LLMs: From Benchmark to Applied
Decision-Making"* (Yoshikawa, Takayama, Yamazaki) — a 12-category cognitive-bias
benchmark, a 162-persona factorial space, and 100 matched gain/loss financial
framing tasks, plus the tooling to build, validate, score, and visualise them.

> **Reconstruction notice.** The original construction data was lost. The 120
> bias items here were **re-authored to the paper's specification** (same
> construct, format, invariant, and controls) and are **not** the identical
> strings used in the paper's experiments. The persona space and financial tasks
> are regenerated deterministically and match the paper exactly. No large-scale
> LLM experiments are run here.

- 📄 Paper: LREC 2026 — ACL Anthology: https://aclanthology.org/2026.lrec-1.332/
  (DOI: [10.63317/2dvjjaywrket](https://doi.org/10.63317/2dvjjaywrket))
- 🤗 Dataset: https://huggingface.co/datasets/katsumasay/cog-bias-bench

## Install

```bash
pip install -r requirements.txt
```

## What is reconstructed

| Resource | File | Size | Reproduction fidelity |
|---|---|---|---|
| Cognitive-bias benchmark | `data/bias_benchmark.jsonl` | 12 categories × 10 = **120 items** | Fresh authoring (same construct, format, invariant, controls). Original strings are not recoverable. |
| Persona space | `data/personas.jsonl` (+ `persona_fields.json`) | **162 personas** + weights | **Exact** — fully deterministic from Table 2. |
| Applied financial tasks | `data/financial_tasks.jsonl` | **100 matched gain/loss pairs** | Equivalent — deterministic sampling under the paper's EV-match constraint. |

## Key invariants (from §3 of the paper)

- **Bias benchmark:** `answer` is **always `"Yes"`** — Yes is the bias-consistent
  label for every item. Items use a unified Yes/No schema
  `{"answer": "Yes/No", "reason": "text"}`. Surface wordings (positive/negative)
  are varied within each category to limit superficial cues.
- **Personas:** factorial Gender(2) × Age(3) × Politics(3) × Income(3) ×
  Education(3) = 162. Weight `w(p) = P(g)P(a)P(pol)P(inc)P(edu)` (marginals in
  Table 2; weights sum to 1). Country (8) and Occupation (8) are **uniform,
  non-stratified** randomization fields and are *not* part of the 162-key.
- **Financial tasks:** fixed decision skeleton A=Certain, B=Risky. Each pair
  shares numeric parameters and flips only gain/loss wording. Amounts/probabilities
  are filtered so EV(certain) ≈ EV(risky) (≤3% relative gap), avoiding trivial
  dominance. Schema `{"choice": "A/B", "confidence": 0.0-1.0, "rationale": "text"}`.

## Rebuild & validate

```bash
python3 scripts/build_all.py        # regenerate all data + run validation
python3 scripts/validate.py         # validation only
```

Individual generators:

```bash
python3 scripts/generate_personas.py
python3 scripts/generate_financial_tasks.py
python3 scripts/generate_bias_benchmark.py
```

All generators are deterministic (the financial sampler uses a fixed seed), so
repeated runs produce byte-identical output.

## Layout

```
data/                       generated datasets (JSONL + JSON)
  bias_benchmark.jsonl
  personas.jsonl
  persona_fields.json       country/occupation lists + attribute marginals
  financial_tasks.jsonl
prompts/                    prompt templates matching the paper
  bias_prompt.txt           (cf. Figure 1)
  financial_prompt.txt
scripts/                    generators + validator + build orchestrator
results/                    demo figures (see below)
hf/                         HuggingFace dataset card (staging for upload)
```

The paper itself is not redistributed here (LREC/ELRA copyright); cite it via
[ACL Anthology](https://aclanthology.org/2026.lrec-1.332/).

## Prompt assembly

Prepend the persona preface (or omit it for the no-persona condition), append
the randomized `Country`/`Occupation` context, and fill the scenario/frame into
the templates in `prompts/`. Persona weights are applied only at **aggregation**
time, not during sampling (all 162 personas are sampled uniformly when running a
model).

## Demo: solving the benchmark & visualising persona effects

A small offline smoke test (not in the paper) exercises the data end-to-end with
Claude as the model under test. Responses are stored as transparent records under
`data/responses/`; no LLM API is called by the scoring code.

```bash
python3 scripts/_claude_responses.py   # Opus no-persona answers (hand-recorded)
python3 scripts/score.py               # single-condition metrics + 2 figures
python3 scripts/score_personas.py      # persona comparison + 4 figures
```

Persona runs were produced by 8 Sonnet sub-agents (7 persona conditions, each
swapping one attribute from a common centre persona, + a no-persona baseline),
each reading the data and writing `data/responses/persona_*.json`.

Figures in `results/`:
- `bias_yesrate.png`, `financial_summary.png` — single-condition (Opus, no-persona).
- `persona_yesrate_overall.png` — overall Yes-rate by persona condition.
- `persona_category_heatmap.png` — 12 categories × 8 conditions.
- `persona_framing_map.png` — safe-in-gain vs risky-in-loss scatter (cf. Fig. 3).
- `persona_attribute_contrasts.png` — politics / income / education slices (cf. Table 5).

**Observed (illustrative only):** the persona effect appears as the spread *among*
the Sonnet conditions — Yes-rate ranges ~0.66 (high income) to ~0.97 (high-school
education); education shows the cleanest gradient (high school > university >
graduate) and conservative > liberal, echoing the paper's qualitative findings.
Persona conditioning also pushes financial choices from frame-invariant
(no-persona, reversal 0%) toward classic framing (reversal 77–100%). The large
gap between the Opus no-persona reference (0.117) and the Sonnet conditions is a
**model-tier** effect (Opus debiases hard, Sonnet responds human-like), not a
persona effect — keep the two separated when interpreting.

## Notes / deviations from the lost originals

- The 120 bias items are newly written. They satisfy the same normalization
  constraints but are not the identical sentences from the original run, so
  absolute Yes-rates produced by a model may differ from the paper's tables.
- Minor inconsistency observed in the paper itself (not data-affecting): §4 lists
  some models (e.g. Qwen3-8B/32B) that differ from the models in Tables 4–6
  (e.g. Qwen3-235B-A22B). The released model set should follow the tables.
- Provenance: the 120 bias items were authored by Claude (Opus 4.8); the paper's
  originals were drafted with GPT-4o and manually reviewed.

## Ethical considerations

Personas encode sensitive attributes (political orientation, income, education).
They are coarse, synthetic constructs for controlled LLM evaluation only and must
not be used to profile, stereotype, or make decisions about real individuals.
This is **not** a fairness/social-bias dataset (cf. BBQ, StereoSet) — it targets
behavioral–cognitive biases.

## License

- Code (`scripts/`): **Apache-2.0** — see [LICENSE](LICENSE).
- Data (`data/`): **CC BY 4.0** — see [data/LICENSE](data/LICENSE).

## Citation

```bibtex
@inproceedings{yoshikawa-etal-2026-persona,
    title = "Persona-Aware Evaluation of Cognitive Bias in {LLM}s: From Benchmark to Applied Decision-Making",
    author = "Yoshikawa, Katsumasa  and
      Takayama, Junya  and
      Yamazaki, Takato",
    editor = "Piperidis, Stelios  and
      Bel, N{\'u}ria  and
      van den Heuvel, Henk  and
      Ide, Nancy  and
      Krek, Simon  and
      Toral, Antonio",
    booktitle = "Proceedings of the Fifteenth Language Resources and Evaluation Conference",
    month = may,
    year = "2026",
    address = "Palma de Mallorca, Spain",
    publisher = "ELRA Language Resource Association",
    url = "https://aclanthology.org/2026.lrec-1.332/",
    doi = "10.63317/2dvjjaywrket",
    pages = "4213--4225"
}
```

To cite this dataset/code release specifically, use the Zenodo DOI
(concept DOI, always resolves to the latest version):
**[10.5281/zenodo.20845756](https://doi.org/10.5281/zenodo.20845756)**.
