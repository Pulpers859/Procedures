# AI Procedure Verification Audit Protocol

## Scope Fingerprint

- Repository commit: `81919a1a9cf16e3f70dcebe32b5900028441f527`
- Procedures SHA-256: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Rescue cards SHA-256: `4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14`
- Kits SHA-256: `c4c40950e457eabb3b8830f838140cd43ff1c610a6c84e8abd9358951d39e520`
- Corpus: 55 procedures, 10 rescue cards, 8 kits.
- Audit date: 2026-07-18.

The procedures and rescue-card fingerprints include uncommitted clinical-content
work present in the source-of-truth working tree at audit start.

## Where The Audited Bytes Are

That uncommitted working tree has consequences, and they are not symmetrical:

- **procedures.json** — recoverable. Git blob
  `9d17679217cece51047c9d762c5602766aca25b2` hashes to the fingerprint above.
- **kits.json** — recoverable. Git blob
  `0976cd8c5caab57435e2ae03cafb296695093688`.
- **rescue_cards.json** — **unrecoverable.** Every object in this repository was
  hashed, reachable and unreachable; nothing matches
  `4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14`. Those
  bytes were never committed and are gone. No rescue-card baseline can be
  reconstructed, and none is faked: `AUDIT_LEDGER.json` records the rescue-card
  baseline as `post-audit`, established after the fact, attesting to nothing
  about the audit.

The commit named above (`81919a1a…`) is where the audit ran, not a commit whose
files match these fingerprints — at `81919a1a` procedures.json hashed
`c3211fb9…` and rescue_cards.json `ab0f239c…`. Only the kits fingerprint
matches its commit. This is recorded because it is the reason a whole-file gate
built on these three constants could never pass.

## Current Integrity Status

Drift is now measured **per record**, against per-record baselines derived from
the audited blobs above, over every field except provenance bookkeeping
(`contentSource`, `reviewerStatus`, `lastReviewed`, `version`). This replaced a
whole-file comparison that could not tell a metadata edit from a dose change:
adding `contentSource` to all 55 records invalidated the entire packet, while
exactly 27 records had actually changed within audit scope.

Run `python scripts/verify_procedure_audit.py` for the current per-record list.
As of 2026-07-29 it names 27 drifted procedures — 25 whose `references` were
replaced post-audit, plus `anterior_nasal_packing` (topical TXA added) and
`block_raptir` (dose ceiling corrected). The other 28 procedures still match the
bytes that were screened, and their findings remain live evidence.

Findings themselves remain unresolved: all 55 procedures carry a `STOP-SHIP` or
`MAJOR` disposition, and the verifier refuses to report success while any is
open. Satisfying fingerprints alone is not clearance.

The original audited fingerprints remain unchanged in this protocol and must not
be rewritten merely to silence the verifier. Baselines in `AUDIT_LEDGER.json`
are derived from the immutable blobs above, and
`scripts/generate_audit_ledger.py --check` fails if one is edited by hand.

## Amending A Drifted Record

Editing content is *expected* to turn the gate red. The remedy is to re-screen
the record and record an amendment — never to move a baseline:

```text
python3 scripts/amend_audit_ledger.py --record <id> \
    --owner "<who adjudicated>" --rationale "<what changed, what you checked>" \
    --commit <sha> --expires <YYYY-MM-DD> --follow-up "<where it is tracked>"
```

These are the five fields `RELEASE_CONSTITUTION.md` already requires of a
waiver. Amendments expire, so one cannot quietly become permanent, and an
amendment stops applying the moment the record changes again.

## Clinical Boundary

This is an AI-assisted evidence and discrepancy screen. It is not medical
approval, credentialing, an institutional protocol, or a substitute for review
by a qualified clinician. Agents must not change `reviewerStatus` or describe a
procedure as clinically verified. A finding of no material discrepancy means
only that the agent did not identify one against the sources reviewed.

## Required Review For Every Procedure

1. Check indications, contraindications, anatomy, positioning, preparation,
   equipment and instruments, ordered steps, ultrasound guidance, confirmation,
   troubleshooting, complications and rescue actions, aftercare, documentation,
   senior pearls, dosing when applicable, and references.
2. Compare against current primary or authoritative sources: specialty-society
   guidelines, government guidance, consensus statements, manufacturer IFUs,
   and original peer-reviewed standards. Secondary summaries may orient the
   search but cannot be the sole support for a substantive finding.
3. Identify pediatric, pregnancy, anticoagulation, infection-control, sedation,
   monitoring, local-anesthetic, and institutional-policy dependencies when
   material.
4. Check that named instruments are standard, correctly sized or qualified where
   size matters, used in the correct sequence, and accompanied by reasonable
   rescue or backup equipment.
5. Do not invent replacement instructions. State the discrepancy, evidence, and
   exact clinician decision required.

## Finding Levels

- `STOP-SHIP`: plausible risk of serious harm, wrong-site/wrong-route action,
  materially unsafe dose, missing immediate rescue action, or contradiction of a
  strong current standard.
- `MAJOR`: clinically important omission, ambiguous step, incomplete instrument
  setup, weak confirmation/failure plan, or reference unable to support the text.
- `MINOR`: useful clarification, discoverability, documentation, or workflow
  improvement without an identified immediate safety consequence.
- `NO MATERIAL DISCREPANCY IDENTIFIED`: no substantive conflict found in the
  sources reviewed; still requires human approval.
- `INSUFFICIENT EVIDENCE`: standards are variable, local-policy dependent, or the
  agent could not obtain authoritative support.

## Per-Procedure Output

Each lane report must include:

- procedure ID, title, and screening disposition;
- concise source-standard summary;
- findings tied to the exact JSON section and quoted only briefly;
- equipment and instrument assessment;
- dosing and monitoring assessment when applicable;
- source links with publisher, guideline title, and publication/update year;
- explicit questions and proposed disposition for the clinical reviewer;
- a statement that `reviewerStatus` remains unchanged.
