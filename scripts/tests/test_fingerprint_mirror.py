"""Locks the Swift and Python material-fingerprint implementations together.

`apply_local_reviews.py` refuses to promote a sign-off whose recorded
fingerprint no longer matches the shipping content. That refusal is the only
thing standing between a stale review and content marked clinically reviewed,
and it is computed by a *reimplementation* of the Swift fingerprint. The two
have to agree byte for byte.

Before this file they could drift without anything failing. `ContentEditingTests`
asserted hardcoded digests, but Swift never runs the Python; and the Python
suite built its expected fingerprints by calling the very function under test,
which is a tautology that passes no matter what that function computes.

The failure mode was quiet and total: a clinician works through all 73 items,
exports, and every single sign-off comes back "content changed since this
review; re-review it in the app" — about content that never changed. Nothing
crashes and nothing logs. The reviewer would reasonably conclude the app had
lost their work.

So the digests are read back out of the Swift test file and compared against
what this implementation actually computes. Either side moving alone fails
here, and this suite runs on Linux and in CI, where the Swift one may not.
Changing a fingerprint is still allowed — it just has to be done on both sides
in the same commit, which is the point.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import apply_local_reviews as promote  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SWIFT_TESTS = REPO_ROOT / "ProceduresTests" / "ContentEditingTests.swift"

# Fixtures mirroring the ones in ContentEditingTests.swift. Kept deliberately
# literal rather than loaded from anywhere: two independent statements of the
# same content are what makes the comparison meaningful.
PROCEDURE = {
    "sections": {
        "shiftMode": ["a", "b", "c", "d", "e", "f"],
        "contraindications": ["a"],
        "equipment": ["a", "b", "c", "d", "e"],
        "steps": ["a", "b", "c", "d", "e"],
        "confirmation": ["a"],
        "troubleshooting": ["a", "b", "c"],
        "complications": ["a", "b", "c", "d"],
    }
}

PROCEDURE_WITH_DOSING = {
    **PROCEDURE,
    "dosing": {
        # The two entries differ in every field the digest reads, including the
        # epinephrine flag and the absent absolute ceiling, so a mirror that
        # drops one of them fails here rather than at a clinician's export.
        "agents": [
            {
                "agent": "Lidocaine",
                "withEpinephrine": False,
                "maxDoseMgPerKg": 4.5,
                "absoluteMaxMg": 300,
                "concentrationsPercent": [1.0, 2.0],
            },
            {
                "agent": "Lidocaine",
                "withEpinephrine": True,
                "maxDoseMgPerKg": 7.0,
                "absoluteMaxMg": None,
                "concentrationsPercent": [1.0],
            },
        ],
        "cumulativeWarning": "Count every source.",
    },
}

RESCUE_CARD = {
    "immediateMoves": ["im1", "im2"],
    "trigger": ["tr1"],
    "avoid": ["av1"],
    "reassess": ["re1"],
}

KIT = {
    "inKit": ["ik1", "ik2"],
    "outsideKit": ["ok1"],
    "commonlyForgotten": ["cf1"],
    "patientSetup": ["ps1"],
    "sterileSetup": ["ss1"],
}

# Swift test function -> the fingerprint this implementation should produce.
MIRRORED = {
    "testMaterialFingerprintMatchesThePythonMirror":
        lambda: promote.procedure_fingerprint(PROCEDURE),
    "testDosingFingerprintMatchesThePythonMirror":
        lambda: promote.procedure_fingerprint(PROCEDURE_WITH_DOSING),
    "testRescueCardFingerprintMatchesThePythonMirror":
        lambda: promote.current_fingerprint("rescue", RESCUE_CARD),
    "testKitFingerprintMatchesThePythonMirror":
        lambda: promote.current_fingerprint("kit", KIT),
}

DIGEST = re.compile(r'"([0-9a-f]{64})"')


def swift_expected_digests():
    """Pulls the digest asserted inside each named Swift test function."""
    source = SWIFT_TESTS.read_text(encoding="utf-8")
    found = {}
    for name in MIRRORED:
        start = source.find(f"func {name}(")
        if start == -1:
            continue
        match = DIGEST.search(source, start)
        if match:
            found[name] = match.group(1)
    return found


class FingerprintMirrorTests(unittest.TestCase):
    def setUp(self):
        self.swift = swift_expected_digests()

    def test_every_mirrored_swift_test_still_exists(self):
        """A deleted Swift test must not silently retire the lock."""
        self.assertEqual(
            sorted(self.swift), sorted(MIRRORED),
            "ContentEditingTests.swift no longer asserts every mirrored digest; "
            "the Swift and Python fingerprints can now drift undetected",
        )

    def test_python_agrees_with_every_swift_digest(self):
        for name, compute in MIRRORED.items():
            with self.subTest(name):
                self.assertIn(name, self.swift)
                self.assertEqual(
                    compute(), self.swift[name],
                    f"{name}: the Python mirror and Swift disagree. Every exported "
                    f"sign-off would be refused as stale. Fix both sides together.",
                )

    def test_field_order_is_part_of_the_contract(self):
        """Reordering the concatenated fields must change the fingerprint.

        Guards the assumption the fixtures rest on: that these tests would
        actually notice a mirror that used the right fields in the wrong order.
        """
        straight = promote.fingerprint(["im1", "im2", "tr1", "av1", "re1"])
        swapped = promote.fingerprint(["tr1", "im1", "im2", "av1", "re1"])
        self.assertNotEqual(straight, swapped)

    def test_the_separator_prevents_boundary_collisions(self):
        """["ab", "c"] and ["a", "bc"] must not fingerprint alike."""
        self.assertNotEqual(
            promote.fingerprint(["ab", "c"]),
            promote.fingerprint(["a", "bc"]),
        )


if __name__ == "__main__":
    unittest.main()
