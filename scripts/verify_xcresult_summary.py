#!/usr/bin/env python3
"""Fail closed unless an xcresult summary reports the exact expected test count."""

import argparse
import json
from pathlib import Path
import sys


def verify_test_count(summary: dict, expected: int) -> int:
    actual = summary.get("totalTestCount")
    if not isinstance(actual, int):
        raise ValueError("xcresult summary has no top-level integer totalTestCount")
    if actual != expected:
        raise ValueError(f"expected {expected} executed tests, xcresult reported {actual}")
    return actual


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--expected", type=int, required=True)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
        actual = verify_test_count(summary, args.expected)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"XCTest evidence verification failed: {error}", file=sys.stderr)
        return 1

    print(f"Verified {actual} executed XCTest cases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
