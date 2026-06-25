#!/usr/bin/env python3
"""Publish the benchmark to the HuggingFace Hub (data only, 3 subsets).

Prereqs:
    pip install huggingface_hub
    export HF_TOKEN=hf_...           # a token with write access
    # or run: huggingface-cli login

Usage:
    python3 scripts/upload_hf.py --repo-id <namespace>/cog-bias-bench
    python3 scripts/upload_hf.py --repo-id <namespace>/cog-bias-bench --private

Uploads the dataset card (hf/README.md) plus the three data files and
persona_fields.json to the dataset repo root, matching the card's `configs`.
"""
import argparse
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

# (local path, path in the HF repo)
FILES = [
    (os.path.join(ROOT, "hf", "README.md"), "README.md"),
    (os.path.join(DATA, "bias_benchmark.jsonl"), "bias_benchmark.jsonl"),
    (os.path.join(DATA, "personas.jsonl"), "personas.jsonl"),
    (os.path.join(DATA, "financial_tasks.jsonl"), "financial_tasks.jsonl"),
    (os.path.join(DATA, "persona_fields.json"), "persona_fields.json"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-id", required=True, help="e.g. yourname/cog-bias-bench")
    ap.add_argument("--private", action="store_true", help="create the repo as private")
    ap.add_argument("--token", default=os.environ.get("HF_TOKEN"))
    args = ap.parse_args()

    from huggingface_hub import HfApi
    api = HfApi(token=args.token)

    api.create_repo(args.repo_id, repo_type="dataset", private=args.private, exist_ok=True)
    for local, remote in FILES:
        if not os.path.exists(local):
            raise SystemExit(f"missing file: {local}")
        api.upload_file(path_or_fileobj=local, path_in_repo=remote,
                        repo_id=args.repo_id, repo_type="dataset")
        print(f"uploaded {remote}")
    print(f"\nDone: https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()
