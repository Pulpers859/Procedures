# Safety and Review Policy

Procedures is an educational review tool for trained clinicians.

It does not replace:

- Clinical judgment
- Formal training
- Supervision
- Credentialing
- Local institutional policy

## Required content metadata

Every procedure should include:

- Last reviewed date
- Version number
- References
- Cautions
- Complications
- Troubleshooting
- Documentation considerations

Every procedure, rescue card, and kit must include `reviewerStatus`. Draft and
Needs Clinical Review content may exist in authoring builds but cannot pass the
strict release gate. A reviewed status records workflow state only; qualified
clinical sign-off for the exact content version remains required.

Visual assets are an optional enhancement, not release-gating content. A
declared asset with no artwork yet (`assetName: null`) falls back to an SF
Symbol and the card still reads correctly, so a placeholder is a warning, not a
stop-ship. This was changed on 2026-07-30 by owner decision: artwork is a
feature in progress and was blocking release of text that is otherwise ready.

Artwork that *is* declared must exist. An `assetName` naming a file that is not
in the bundle stays a release blocker, because that renders as a broken image
rather than a graceful fallback — a build defect, not a pending feature. Any
artwork that does ship still needs clinical review of what it depicts; the
cricothyrotomy danger-zone image already has an open anatomy concern.

## Review interval suggestion

- High-risk procedures: every 6 months
- Medication-heavy content: every 3–6 months
- Common procedures: every 12 months
- Rare-crash procedures: every 6 months
