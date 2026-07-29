#!/usr/bin/env python3
"""The fingerprint that answers "is this the record the audit screened?".

This is deliberately NOT Procedure.materialFingerprint. That one answers a
different question — "does the reader's sign-off still apply to the text they
would act on at the bedside?" — and so it hashes only the seven bedside
sections plus dosing. Reusing it here looked economical and was wrong: it is
blind to `references`, and 27 of the 55 procedures had their references
replaced after the audit. The lane reports grade "reference unable to support
the text" as a MAJOR finding, so a reference swap invalidates audit evidence
even though it changes nothing a clinician does with their hands. Measured
against the audited bytes, the material fingerprint saw 2 drifted records out
of the 27 that had really drifted: a false green on 25.

Two fingerprints, two questions, two versions. Keeping them separate also stops
an app-side fingerprint change from silently invalidating the audit baseline.

The scope rule is a denylist, and that polarity is the whole point. An allowlist
of audited fields is how the material fingerprint became blind to references:
a field nobody remembered to add simply stopped counting, silently. Here, every
field counts unless it is named below, so a field added to the schema next year
defaults to "this is content" and trips the gate. Being asked an unnecessary
question is recoverable; a false green on a clinical record is not.
"""

import hashlib
import json


# Bumped when the scope rule or serialization changes. A digest written under an
# older version answers a different question and must not be compared.
AUDIT_FINGERPRINT_VERSION = 1

# Bookkeeping about a record, not the record. Each is excluded for a stated
# reason, and nothing is excluded merely because it is noisy.
#
#   contentSource   provenance label; adding it corpus-wide is what destroyed
#                   the previous gate, and it asserts nothing clinical
#   reviewerStatus  review workflow state, which the audit is forbidden to move
#   lastReviewed    a date stamp on that workflow state
#   version         changes *because* content changed, so the content change
#                   already trips this; counting it would double-report
BOOKKEEPING_FIELDS = frozenset({
    "contentSource",
    "reviewerStatus",
    "lastReviewed",
    "version",
})


def audited_scope(item: dict) -> dict:
    """The part of a record the audit screened."""
    return {key: value for key, value in item.items() if key not in BOOKKEEPING_FIELDS}


def audit_fingerprint(item: dict) -> str:
    """SHA-256 over a canonical serialization of everything but bookkeeping.

    sort_keys makes key order irrelevant, so reserializing the file cannot
    manufacture drift. Value order is preserved, because step order is
    clinical content: the same steps in a different sequence is a different
    procedure and must register as changed.
    """
    canonical = json.dumps(
        audited_scope(item),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
