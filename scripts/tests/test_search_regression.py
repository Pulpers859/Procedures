"""Bedside search regression suite.

Ports the app's search pipeline (ClinicalSynonyms + ProcedureRepository
scoring in ProcedureRepository.swift — tokenizer, synonym expansion,
single-edit typo recovery, weighted contains-scoring) to Python and runs
real clinician queries against the real shipped content. If a query a
clinician would type at the bedside stops resolving, this fails in CI.

The port must stay behaviorally identical to the Swift implementation;
change both together.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "Procedures" / "Resources"

PROCEDURES = json.loads((RESOURCES / "procedures.json").read_text(encoding="utf-8"))
RESCUE_CARDS = json.loads((RESOURCES / "rescue_cards.json").read_text(encoding="utf-8"))
SYNONYMS = json.loads((RESOURCES / "synonyms.json").read_text(encoding="utf-8"))

VOCABULARY = set(SYNONYMS)
for _terms in SYNONYMS.values():
    VOCABULARY.update(_terms)


def tokens(query):
    result = []
    for chunk in re.split(r"[\s,;/]+", query.strip().lower()):
        parts = [part for part in chunk.split("-") if part]
        if len(parts) > 1:
            result.append("".join(parts))
        result.extend(parts)
    return [token for token in result if len(token) > 1]


def within_one_edit(first, second):
    if first == second:
        return True
    if abs(len(first) - len(second)) > 1:
        return False
    i = j = edits = 0
    while i < len(first) and j < len(second):
        if first[i] == second[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(first) == len(second):
            i += 1
            j += 1
        elif len(first) > len(second):
            i += 1
        else:
            j += 1
    return edits + (len(first) - i) + (len(second) - j) <= 1


def fuzzy_match(token):
    if len(token) < 4 or token in VOCABULARY:
        return None
    candidates = [word for word in VOCABULARY if within_one_edit(token, word)]
    return min(candidates) if candidates else None


def group(token):
    if token in SYNONYMS:
        return [token] + SYNONYMS[token]
    corrected = fuzzy_match(token)
    if corrected:
        return [token, corrected] + SYNONYMS.get(corrected, [])
    return [token]


def searchable_fields(procedure):
    sections = procedure["sections"]
    visuals = " ".join(
        " ".join(
            [v.get("title", ""), v.get("subtitle", ""), v.get("kind", ""),
             v.get("caption", ""), v.get("clinicalWarning") or ""]
        )
        for v in procedure.get("visualAssets") or []
    )
    return [
        (procedure["title"].lower(), 12),
        (procedure["category"].lower(), 7),
        (procedure["difficulty"].lower(), 4),
        (procedure.get("reviewTime", "").lower(), 2),
        (" ".join(procedure.get("tags", [])).lower(), 10),
        (visuals.lower(), 7),
        (" ".join(sections["shiftMode"]).lower(), 8),
        (" ".join(sections["equipment"]).lower(), 6),
        (" ".join(sections["steps"]).lower(), 5),
        (" ".join(sections["complications"]).lower(), 5),
        (" ".join(sections["troubleshooting"]).lower(), 5),
        (" ".join(sections["documentation"]).lower(), 3),
        (" ".join(sections["seniorPearls"]).lower(), 4),
    ]


def search(query):
    query_tokens = tokens(query)
    terms = set()
    for token in query_tokens:
        terms.update(group(token))
    scored = []
    for procedure in PROCEDURES:
        total = 0
        for term in terms:
            for text, weight in searchable_fields(procedure):
                if term in text:
                    total += weight
        if total > 0:
            scored.append((procedure, total))
    scored.sort(key=lambda pair: (-pair[1], pair[0]["title"].lower()))
    return [procedure["id"] for procedure, _ in scored]


def rescue_matches(query):
    query_tokens = tokens(query)
    matched = []
    for card in RESCUE_CARDS:
        haystack = " ".join(
            [card["title"], card["acuity"], card.get("lastReviewed", ""), card.get("version", "")]
            + card.get("relatedProcedureIDs", []) + card.get("trigger", [])
            + card.get("immediateMoves", []) + card.get("reassess", [])
            + card.get("avoid", []) + card.get("tags", []) + card.get("references", [])
        ).lower()
        if all(any(term in haystack for term in group(token)) for token in query_tokens):
            matched.append(card["id"])
    return matched


# (query, expected procedure id, max acceptable rank). Rank 3 means "in the
# first three results" — the bedside bar is that the target is immediately
# visible, not merely present.
PROCEDURE_QUERIES = [
    ("cric", "cricothyrotomy", 3),
    ("crich", "cricothyrotomy", 3),          # edit-distance-1 typo
    ("cricothyrotomy", "cricothyrotomy", 1),
    ("a-line", "arterial_line", 3),          # hyphen tokenization
    ("aline", "arterial_line", 3),
    ("abg", "arterial_line", 3),
    ("txa", "anterior_nasal_packing", 3),
    ("nosebleed", "anterior_nasal_packing", 3),
    ("epistaxis", "anterior_nasal_packing", 3),
    ("chest tube", "thoracostomy_chest_tube", 3),
    ("rsi", "endotracheal_intubation", 3),
    ("ett", "endotracheal_intubation", 3),
    ("cvc", "central_venous_catheter", 3),
    ("lp", "lumbar_puncture", 3),
    ("tamponade", "pericardiocentesis", 3),
    ("edt", "resuscitative_thoracotomy", 3),
    ("clamshell", "resuscitative_thoracotomy", 3),
    ("pigtail", "pigtail_catheter", 3),
    ("tension ptx", "needle_decompression", 3),
    ("thoracentesis", "thoracentesis", 3),
    ("thoracentsis", "thoracentesis", 3),    # edit-distance-1 typo
    ("paracentesis", "paracentesis", 3),
    ("ascites tap", "paracentesis", 3),
    ("pacer", "transvenous_pacemaker", 3),
    ("tvp", "transvenous_pacemaker", 3),
    ("usgiv", "ultrasound_guided_piv", 3),
    ("canthotomy", "lateral_canthotomy", 3),
    ("shoulder reduction", "shoulder_reduction", 3),
    ("fascia iliaca", "fascia_iliaca_block", 3),
    ("digital block", "digital_nerve_block", 3),
    ("interscalene", "block_interscalene", 3),
    ("peng", "block_peng", 3),
    ("sedation", "procedural_sedation", 3),
]

RESCUE_QUERIES = [
    ("last", "local_anesthetic_systemic_toxicity"),
    ("lipid", "local_anesthetic_systemic_toxicity"),
    ("laryngospasm", "sedation_apnea"),
    ("capture", "failed_transvenous_capture"),
]


class ProcedureSearchRegressionTests(unittest.TestCase):
    def test_bedside_queries_surface_the_expected_procedure(self):
        for query, expected_id, max_rank in PROCEDURE_QUERIES:
            with self.subTest(query=query):
                results = search(query)
                self.assertIn(expected_id, results, f"{query!r} found nothing relevant")
                rank = results.index(expected_id) + 1
                self.assertLessEqual(
                    rank, max_rank,
                    f"{query!r} ranks {expected_id} at {rank}, above the bedside bar of {max_rank}; "
                    f"top results: {results[:5]}",
                )

    def test_zero_result_queries_stay_zero(self):
        # A nonsense query must not fuzzy-correct into noise.
        self.assertEqual(search("zzzzqqqq"), [])


class RescueSearchRegressionTests(unittest.TestCase):
    def test_bedside_queries_match_the_expected_rescue_card(self):
        for query, expected_id in RESCUE_QUERIES:
            with self.subTest(query=query):
                self.assertIn(expected_id, rescue_matches(query), f"{query!r} misses {expected_id}")


class FuzzyMatcherTests(unittest.TestCase):
    def test_short_shorthand_is_never_rewritten(self):
        for token in ("ij", "lp", "abg", "ptx"):
            self.assertIsNone(fuzzy_match(token))

    def test_single_edit_definitions(self):
        self.assertTrue(within_one_edit("crich", "cric"))
        self.assertTrue(within_one_edit("cric", "crik"))
        self.assertFalse(within_one_edit("cric", "crikh"))
        self.assertFalse(within_one_edit("chest", "tube"))


if __name__ == "__main__":
    unittest.main()
