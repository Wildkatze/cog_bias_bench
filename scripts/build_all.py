#!/usr/bin/env python3
"""Rebuild every dataset from scratch and validate the result."""
import runpy
import os
import sys

HERE = os.path.dirname(__file__)


def run(name):
    print(f"\n=== {name} ===")
    runpy.run_path(os.path.join(HERE, name), run_name="__main__")


def main():
    for s in ("generate_personas.py", "generate_financial_tasks.py", "generate_bias_benchmark.py"):
        run(s)
    print("\n=== validate.py ===")
    try:
        runpy.run_path(os.path.join(HERE, "validate.py"), run_name="__main__")
    except SystemExit as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
