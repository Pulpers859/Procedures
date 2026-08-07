#!/usr/bin/env python3
"""Query the bundled clinical content without loading all of it.

`procedures.json` is ~146k tokens. A single record is ~2k. Across this repo's
session transcripts, 688 throwaway python one-liners were run through Bash and
65% of them were doing nothing but opening that file and filtering it - roughly
744 KB of disposable code re-solving the same problem. That is what this
replaces.

The interface is deliberately guessable, because a tool nobody finds is a tool
that does not exist. `scripts/session_brief.py` names it in the SessionStart
banner so every session is told it is here.

    pq ls                                    every id, title, status
    pq ls --unreviewed --category Airway     filtered
    pq show cricothyrotomy                   one whole record, sections only
    pq show cricothyrotomy steps equipment   only those sections
    pq sections cricothyrotomy               section names and line counts
    pq grep "bougie"                         matching lines, with id and section
    pq grep "20-30" --section equipment
    pq fp cricothyrotomy                     material fingerprint + what feeds it
    pq diff cricothyrotomy origin/main       what changed in this record since
    pq stats                                 corpus counts

    --kind rescue|kit                        the other two content files

Read-only by design. Writing content is `apply_local_edits.py`, which produces
a reviewable diff and reports the retrieval cost; nothing here should tempt a
session into hand-editing the JSON.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"
KINDS = {
    "procedure": "procedures.json",
    "rescue": "rescue_cards.json",
    "kit": "kits.json",
}
# Rescue cards and kits keep their content in top-level list fields rather than
# a `sections` dict; normalising here lets one set of verbs serve all three.
FLAT_SECTIONS = {
    "rescue": ["immediateMoves", "trigger", "avoid", "reassess"],
    "kit": ["inKit", "outsideKit", "commonlyForgotten", "patientSetup", "sterileSetup"],
}


def load(kind, rev=None):
    name = KINDS[kind]
    if rev:
        try:
            raw = subprocess.check_output(
                ["git", "show", f"{rev}:Procedures/Resources/{name}"],
                cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            sys.exit(f"error: {name} not found at revision {rev!r}")
    else:
        raw = (RESOURCES / name).read_text(encoding="utf-8")
    return json.loads(raw)


def sections_of(item, kind):
    if kind == "procedure":
        return {k: v for k, v in (item.get("sections") or {}).items() if isinstance(v, list)}
    return {f: list(item.get(f) or []) for f in FLAT_SECTIONS[kind] if item.get(f)}


def find(items, item_id, kind):
    for item in items:
        if item.get("id") == item_id:
            return item
    near = [i.get("id", "") for i in items if item_id.lower() in i.get("id", "").lower()]
    hint = f" Did you mean: {', '.join(near[:5])}?" if near else ""
    sys.exit(f"error: no {kind} with id {item_id!r}.{hint}")


def cmd_ls(args, items, kind):
    for item in items:
        if args.category and (item.get("category") or "").lower() != args.category.lower():
            continue
        if args.status and (item.get("reviewerStatus") or "") != args.status:
            continue
        if args.tag and args.tag.lower() not in [t.lower() for t in item.get("tags") or []]:
            continue
        reviewed = (item.get("reviewerStatus") or "Needs Clinical Review")
        if args.unreviewed and reviewed not in (
                "Needs Clinical Review", "Draft", None):
            continue
        print(f"{item.get('id'):42s} {reviewed:22s} {item.get('title')}")


def cmd_show(args, items, kind):
    item = find(items, args.id, kind)
    secs = sections_of(item, kind)
    wanted = args.sections or list(secs)
    unknown = [s for s in wanted if s not in secs]
    if unknown:
        print(f"# no such section(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"# available: {', '.join(secs)}", file=sys.stderr)
    for name in wanted:
        if name not in secs:
            continue
        print(f"\n## {name}")
        for line in secs[name]:
            print(f"- {line}")


def cmd_sections(args, items, kind):
    item = find(items, args.id, kind)
    material = material_fields(kind)
    for name, lines in sections_of(item, kind).items():
        mark = " *material" if name in material else ""
        print(f"{name:20s} {len(lines):3d} line(s){mark}")
    print("\n* material sections feed the review fingerprint; editing one revokes a sign-off.")


def cmd_grep(args, items, kind):
    pattern = re.compile(args.pattern, 0 if args.case else re.IGNORECASE)
    hits = 0
    for item in items:
        for name, lines in sections_of(item, kind).items():
            if args.section and name != args.section:
                continue
            for line in lines:
                if pattern.search(line):
                    hits += 1
                    print(f"{item.get('id')}:{name}: {line}")
    print(f"\n{hits} match(es).", file=sys.stderr)


def material_fields(kind):
    sys.path.insert(0, str(ROOT / "scripts"))
    import apply_local_reviews as review
    if kind == "procedure":
        return list(review.PROCEDURE_MATERIAL_SECTIONS)
    return list(review.KINDS[kind][1] or [])


def cmd_fp(args, items, kind):
    sys.path.insert(0, str(ROOT / "scripts"))
    import apply_local_reviews as review
    item = find(items, args.id, kind)
    print(f"fingerprint      {review.current_fingerprint(kind, item)}")
    print(f"version          v{review.FINGERPRINT_VERSION}")
    print(f"reviewerStatus   {item.get('reviewerStatus')}")
    print(f"contentSource    {item.get('contentSource')}")
    print(f"material         {', '.join(material_fields(kind))}")
    if kind == "procedure":
        extra = [f for f in ("majorBlockMonitoring", "dosing", "medicationDosing") if item.get(f)]
        if extra:
            print(f"also hashed      {', '.join(extra)} (not editable in the app)")


def cmd_diff(args, items, kind):
    old = {i.get("id"): i for i in load(kind, args.rev)}
    item = find(items, args.id, kind)
    before = sections_of(old.get(args.id, {}), kind)
    after = sections_of(item, kind)
    changed = False
    for name in sorted(set(before) | set(after)):
        b, a = before.get(name, []), after.get(name, [])
        if b == a:
            continue
        changed = True
        print(f"\n## {name}")
        for line in b:
            if line not in a:
                print(f"- {line}")
        for line in a:
            if line not in b:
                print(f"+ {line}")
    if not changed:
        print(f"{args.id} is unchanged since {args.rev}.")


def cmd_stats(args, items, kind):
    from collections import Counter
    status = Counter((i.get("reviewerStatus") or "Needs Clinical Review") for i in items)
    print(f"{len(items)} {kind}(s)")
    for name, count in status.most_common():
        print(f"  {count:3d}  {name}")
    if kind == "procedure":
        cats = Counter(i.get("category") for i in items)
        print("categories: " + ", ".join(f"{c}={n}" for c, n in cats.most_common()))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pq", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kind", choices=sorted(KINDS), default="procedure")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ls", help="ids, statuses and titles")
    p.add_argument("--category")
    p.add_argument("--status")
    p.add_argument("--tag")
    p.add_argument("--unreviewed", action="store_true")
    p.set_defaults(fn=cmd_ls)

    p = sub.add_parser("show", help="one record's sections")
    p.add_argument("id")
    p.add_argument("sections", nargs="*")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("sections", help="section names, sizes, and which are material")
    p.add_argument("id")
    p.set_defaults(fn=cmd_sections)

    p = sub.add_parser("grep", help="search every line of every record")
    p.add_argument("pattern")
    p.add_argument("--section")
    p.add_argument("--case", action="store_true", help="case-sensitive")
    p.set_defaults(fn=cmd_grep)

    p = sub.add_parser("fp", help="material fingerprint and what feeds it")
    p.add_argument("id")
    p.set_defaults(fn=cmd_fp)

    p = sub.add_parser("diff", help="what changed in one record since a git revision")
    p.add_argument("id")
    p.add_argument("rev")
    p.set_defaults(fn=cmd_diff)

    p = sub.add_parser("stats", help="corpus counts")
    p.set_defaults(fn=cmd_stats)

    args = parser.parse_args(argv)
    args.fn(args, load(args.kind), args.kind)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
