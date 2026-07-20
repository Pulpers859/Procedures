# AI Procedure Verification Audit Protocol

## Scope Fingerprint

- Repository commit: `81919a1a9cf16e3f70dcebe32b5900028441f527`
- Procedures SHA-256: `3b642c17b79839d111a20e21f158765ba820d3a3a4889d2d49aaa37bf28edde1`
- Rescue cards SHA-256: `4f8e47d0e93dcc95476f4e4bf8af0bcbfa866d6e5dca4fd63e54dd48fba2fc14`
- Kits SHA-256: `c4c40950e457eabb3b8830f838140cd43ff1c610a6c84e8abd9358951d39e520`
- Corpus: 55 procedures, 10 rescue cards, 8 kits.
- Audit date: 2026-07-18.

The procedures and rescue-card fingerprints include uncommitted clinical-content
work present in the source-of-truth working tree at audit start. Findings are
invalidated if either fingerprint changes.

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

