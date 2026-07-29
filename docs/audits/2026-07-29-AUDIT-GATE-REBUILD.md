# Rebuilding the audit corpus fingerprint check

2026-07-29. Two solutions were built. The first is described because measuring
why it failed is what produced the second.

## What was actually wrong

`scripts/verify_procedure_audit.py` pinned three whole-file SHA-256 constants
and failed the release gate if the shipping files did not match. Three findings,
in order of how badly they undermine the gate:

**1. The check was born red and could never go green.** The commit that wired
it in (`9a41ed0`, "Fail closed on complete audit corpus drift") already failed
on all three files at the moment it landed. It never passed, once.

**2. Two of the three constants named bytes that no longer existed anywhere.**
`AUDIT_PROTOCOL.md` says the audit fingerprinted "uncommitted clinical-content
work present in the source-of-truth working tree". Hashing every object in the
repository — 669 blobs, reachable and unreachable — found the audited
procedures.json (blob `9d176792`) and kits.json (blob `0976cd8c`), and did not
find the audited rescue_cards.json in any object at all. The audited
rescue-card bytes are permanently lost, so that constant identified a state the
repository could not reach even by reverting everything.

**3. The gate could not tell a metadata edit from a dose change.** Of the 55
procedures, **53 differed from the audited snapshot by exactly one thing**: the
addition of `"contentSource": "ai-draft"`. The field that made the corpus more
honest about being unreviewed is what invalidated all 55 audits. The
whole-file digest has no notion of *which* record moved, so the only path to
green was rewriting the fingerprint in 13 files — which re-stamps all 55
records' evidence as current, including the 53 nobody looked at. **The cheapest
route to green was a global rubber stamp**, which is precisely what
`AUDIT_PROTOCOL.md` forbids.

Two further facts, found while fixing it:

**4. The gate had never executed.** It runs only on `push: tags: v*`. This
repository has no tags. A guard built to catch content drift caught nothing for
its entire existence, and reported nothing, because the moment it fires had
never happened.

**5. The gate had no closure semantics.** With fingerprints satisfied, it would
have printed *"Verified nine fingerprinted audit reports…"* over a corpus where
all 55 procedures carry an unresolved `STOP-SHIP` or `MAJOR` disposition. That
is the most dangerous output the script could produce: a clean bill of health
for exactly the records the audit objected to.

## Solution 1: per-record baselines using the existing material fingerprint

Replace three whole-file hashes with a checked-in ledger of per-record
fingerprints, reusing `Procedure.materialFingerprint` (already mirrored in
Python in `apply_local_reviews.py`). Fail only on records that drifted, and
name them.

Built, working, and **wrong**. Measured against the recovered audited bytes it
reported **2 drifted records**. The true number within audit scope is **27**.

The material fingerprint answers *"does the reader's bedside sign-off still
apply?"* — so it deliberately hashes only seven bedside sections plus dosing.
It does not cover `references`. And 25 procedures had placeholder references
("Standard emergency medicine regional anesthesia literature.") replaced with
real citations after the audit. The lane reports grade "reference unable to
support the text" as a `MAJOR` finding, so a reference swap invalidates audit
evidence even though it changes nothing a clinician does with their hands.

Solution 1 was a **false green on 25 clinical records**. Reusing a digest built
for a different question silently imported that question's narrower scope.

## Solution 2: an audit-scoped fingerprint, shipped

Same ledger and amendment machinery, different digest — `scripts/audit_fingerprint.py`.

**Denylist, not allowlist.** Every field counts as content unless explicitly
named bookkeeping (`contentSource`, `reviewerStatus`, `lastReviewed`,
`version`). This is the load-bearing decision. An allowlist is *how* the
material fingerprint went blind to references: a field nobody remembered to add
simply stopped counting, silently. Under a denylist, a field added to the schema
next year defaults to "this is content" and trips the gate. Being asked an
unnecessary question is recoverable; a false green on a clinical record is not.

Kept separate from the app's material fingerprint, with its own version, so
neither drifts to serve the other and an app-side change cannot invalidate the
audit baseline.

### What else changed

- **Baselines are derived, not typed.** `generate_audit_ledger.py` reads the
  audited bytes out of the pinned git blobs and verifies each blob against the
  fingerprint `AUDIT_PROTOCOL.md` records before computing anything. There is no
  code path from today's `procedures.json` to a baseline entry — you cannot mint
  an "audited" baseline for content that was never audited. `--check` fails if a
  baseline was edited by hand, and it runs in CI.
- **The lost rescue-card baseline is recorded, not laundered.** It is marked
  `post-audit`, `auditedBaselineUnrecoverable: true`, `screening: none`, and
  carries a note saying why. Seeding it from today's content and calling it
  audited would have been the easy lie.
- **Honest scope.** No kit and 9 of 10 rescue cards appear in any lane report.
  Their drift blocks nothing, because there is no per-record evidence to
  invalidate — it is reported as a notice instead. The reviewed-status stop-ship
  in `RELEASE_CONSTITUTION.md` is what actually holds that content back, and it
  is far stricter.
- **Drift has an exit that is not a rubber stamp.** `amend_audit_ledger.py`
  records a re-screen carrying the five fields the constitution already requires
  of a waiver — owner, rationale, commit, expiry, follow-up. Amendments expire,
  so one cannot quietly become permanent, and an amendment is void the moment
  the record changes again. It refuses empty rationales, past expiries, and
  records that never drifted.
- **Open findings block.** The verifier will not report success while any
  procedure carries an unresolved `STOP-SHIP` or `MAJOR`. Nothing here closes a
  finding — closure is a clinical judgement — it only refuses to let silence be
  mistaken for resolution.
- **It runs where drift happens.** Advisory on every push and PR
  (`validate-content.yml`), blocking in `release-readiness.yml`. Both now
  checkout with `fetch-depth: 0`, since the baselines need the audited blobs.
- **The integrity hold is computed.** It used to be a hand-written blockquote in
  `AUDIT_INDEX.md` that the generator did not emit — the first regeneration
  would have silently deleted the warning. It is now derived from the ledger and
  names the drifted records.
- **One disposition parser.** The generator carried a second, looser regex for
  the same line and would crash on input the verifier would reject.
- **The index generator is no longer deadlocked.** It refused to run while any
  issue existed, including the drift it was meant to describe.

## Honest limits

- **This is not a release unblock, and was never going to be.**
  `validate_procedures.py --release` reports 127 blockers and 0/73 clinically
  reviewed; the clinical owner is unassigned. Fixing this gate moves the failure
  from step 4 to step 5.
- **The gate is still red — for 27 true reasons instead of one false one**, each
  naming a record with a documented remedy. That is the intended state.
- **No in-repo check can stop the repository owner from rubber-stamping.** What
  it buys: rubber-stamping must be typed out per record, with a name, a reason,
  and an end date, in a diff. That stops an *agent* doing it quietly, which is
  the threat this repository already documents in
  `EXTERNAL_AGENT_RECONCILIATION.md`.
- **Not addressed:** the gate hashes the bundled content, while the app renders
  bundle ⊕ local overrides (`ProcedureRepository.swift`). Three per-procedure
  evidence checks are satisfiable by the report template rather than by
  analysis. The approval-claim check is a phrase blocklist that "cleared for
  release" would pass. A renamed record is an invisible delete plus a caught add.
  Section boundaries in lane reports leak past non-procedure `##` headings.
