#!/usr/bin/env python3
"""Ratchet on bedside retrieval: no edit may quietly cost a record its place.

The hand-written queries in test_search_regression.py only cover what someone
thought to write down. "the patient needs a central line" was in that list, so
when a review trimmed the central-line shiftMode and took the last high-weight
occurrence of "catheter" with it, the dialysis catheter started ranking first
and the suite caught it. Nothing would have caught the same edit to any record
outside those few sentences - and in the same review, an edit did exactly that
to ultrasound-guided PIV without a single test noticing.

So the probes here are derived from the content instead of written by hand:
every procedure is queried by its own title and each of its own tags. A new
procedure is covered the moment it is added, and no expectation can go stale.

Ranks are compared against a committed baseline rather than asserted absolute,
because 8 records do not currently rank first for their own title (search them
with --report to see them). Those are real retrieval defects, but they predate
this check and fixing them is a separate piece of work with its own blast
radius. A ratchet does not need them fixed to be useful: it only has to refuse
to let things get worse. Improvements are reported and the baseline is
regenerated with --update.

Usage:
    python3 scripts/check_search_ranking.py            # verify against baseline
    python3 scripts/check_search_ranking.py --report   # full current ranking
    python3 scripts/check_search_ranking.py --update   # accept current as baseline
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomic_write import atomic_write_text
import search_model

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "scripts" / "search_ranking_baseline.json"

# A rank worse than this is treated as "not found" for reporting purposes: past
# the first screen at the bedside, the difference between 12th and 30th does
# not matter.
UNRANKED = 999


def current_ranks(procedures=None, rescue_cards=None):
    """{ "<procedure id>|<probe>": rank } for every record's own title/tags."""
    index = search_model.SearchIndex(procedures, rescue_cards)
    ranks = {}
    for procedure in index.procedures:
        for probe in search_model.self_retrieval_probes(procedure):
            rank = index.rank_of(probe, procedure["id"])
            ranks[f"{procedure['id']}|{probe}"] = rank if rank is not None else UNRANKED
    return ranks


def load_baseline():
    if not BASELINE.exists():
        sys.exit(
            f"error: no baseline at {BASELINE.relative_to(ROOT)}.\n"
            "Create it with: python3 scripts/check_search_ranking.py --update"
        )
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def write_baseline(ranks):
    atomic_write_text(BASELINE, json.dumps(ranks, indent=2, sort_keys=True) + "\n")


def compare(baseline, ranks):
    """(worse, better, added, removed) - each a list of printable lines."""
    worse, better, added, removed = [], [], [], []
    for key in sorted(set(baseline) | set(ranks)):
        was, now = baseline.get(key), ranks.get(key)
        if was is None:
            added.append(f"{key}  (new, #{now})")
        elif now is None:
            removed.append(f"{key}  (gone, was #{was})")
        elif now > was:
            worse.append(f"{key}  #{was} -> #{now}")
        elif now < was:
            better.append(f"{key}  #{was} -> #{now}")
    return worse, better, added, removed


def report(ranks):
    by_procedure = {}
    for key, rank in ranks.items():
        pid, _, probe = key.partition("|")
        by_procedure.setdefault(pid, []).append((probe, rank))
    for pid in sorted(by_procedure):
        rows = sorted(by_procedure[pid], key=lambda r: (r[1], r[0]))
        flag = "" if rows[0][1] == 1 else "   <- does not rank first for any of its own probes"
        print(f"\n{pid}{flag}")
        for probe, rank in rows:
            mark = " " if rank == 1 else "!"
            print(f"  {mark} #{'-' if rank == UNRANKED else rank:<4} {probe}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--update", action="store_true", help="Write the current ranking as the new baseline.")
    parser.add_argument("--report", action="store_true", help="Print every probe and its rank.")
    args = parser.parse_args(argv)

    ranks = current_ranks()

    if args.report:
        report(ranks)
        return 0

    if args.update:
        write_baseline(ranks)
        print(f"Baseline written: {len(ranks)} probes across {len({k.split('|')[0] for k in ranks})} procedures.")
        return 0

    worse, better, added, removed = compare(load_baseline(), ranks)

    for line in removed:
        print(f"gone     {line}")
    for line in added:
        print(f"new      {line}")
    for line in better:
        print(f"better   {line}")
    for line in worse:
        print(f"WORSE    {line}")

    if worse:
        print(
            f"\n{len(worse)} probe(s) lost ground. A procedure got harder to find by its own "
            "title or tag.\nRestore the wording, add a tag to carry the term (tags are outside "
            "the material\nfingerprint, so they do not disturb a sign-off), or accept it with "
            "--update."
        )
        return 1

    if better or added or removed:
        print("\nNo regressions. Run --update to fold these changes into the baseline.")
        return 0

    print(f"Bedside retrieval unchanged: {len(ranks)} probes, none worse.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
