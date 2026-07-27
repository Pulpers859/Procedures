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


STOP_WORDS = {
    "the", "and", "for", "with", "has", "have", "had", "was", "were", "are",
    "this", "that", "then", "than", "from", "into", "onto", "after", "before",
    "during", "while", "when", "why", "how", "what", "who", "his", "her",
    "their", "our", "your", "its", "patient", "pt", "still", "just", "very",
    "really", "some", "any", "all", "not", "but", "out", "off", "over",
    "under", "about", "also", "been", "being", "does", "did", "get", "got",
    "now", "new", "can", "cant", "wont", "doesnt",
}

ACUITY_ORDER = {"Crash": 0, "Urgent": 1, "Watch": 2}


def content_tokens(query):
    raw = tokens(query)
    filtered = [token for token in raw if token not in STOP_WORDS]
    return filtered or raw


def card_haystack(card):
    # lastReviewed/version are deliberately excluded: editorial metadata is not
    # clinical search text. Mirrors ComplicationRescueCard.searchFields().
    return " ".join(
        [card["title"], card["acuity"]]
        + card.get("relatedProcedureIDs", []) + card.get("trigger", [])
        + card.get("immediateMoves", []) + card.get("reassess", [])
        + card.get("avoid", []) + card.get("tags", []) + card.get("references", [])
    ).lower()


def rescue_matches(query):
    """Best-tier rescue ranking. Mirrors ProcedureRepository.searchRescueCards:
    keep every card satisfying the most query tokens, ordered by title
    relevance then acuity. Strict AND used to empty the crash screen whenever a
    single typed word was absent from a card."""
    query_tokens = content_tokens(query)
    if not query_tokens:
        return [card["id"] for card in RESCUE_CARDS]

    scored = []
    for card in RESCUE_CARDS:
        haystack = card_haystack(card)
        title = card["title"].lower()
        matched = exact_title = title_hits = 0
        for token in query_tokens:
            expansion = group(token)
            if any(term in haystack for term in expansion):
                matched += 1
            if any(term in title for term in expansion):
                title_hits += 1
            if token in title:
                exact_title += 1
        if matched:
            scored.append((matched, exact_title, title_hits, card))

    if not scored:
        return []

    best = max(entry[0] for entry in scored)
    top = [entry for entry in scored if entry[0] == best]
    top.sort(key=lambda e: (-e[1], -e[2], ACUITY_ORDER[e[3]["acuity"]], e[3]["title"].lower()))
    return [entry[3]["id"] for entry in top]


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
    # Named regional blocks must beat the generic "block" vocabulary. Before
    # the "block" synonym was narrowed these ranked 9th and 10th.
    ("tap block", "block_tap", 3),
    ("esp block", "block_thoracic_esp", 3),
    ("transversus abdominis", "block_tap", 3),
    # "tap" is overloaded: drainage taps and the TAP block share the word, and
    # both must still resolve.
    ("ascites tap", "paracentesis", 3),
    ("spinal tap", "lumbar_puncture", 3),
    ("knee tap", "knee_arthrocentesis", 3),
    # Bare clinical abbreviations clinicians actually type.
    ("io", "intraosseous_access", 3),
    ("cico", "cricothyrotomy", 3),
    ("surgical airway", "cricothyrotomy", 3),
    # "pacing" previously typo-corrected into "packing" and surfaced epistaxis.
    ("pacing", "transvenous_pacemaker", 3),
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

    def test_natural_phrasing_does_not_collapse_to_zero_results(self):
        # Strict AND across typed words used to empty the crash screen: one
        # word a card happened not to contain returned nothing at all.
        for query in (
            "the patient has hypotension",
            "patient is hypotensive after intubation",
            "loss of capture",
            "my patient is crashing",
        ):
            with self.subTest(query=query):
                self.assertNotEqual(rescue_matches(query), [], f"{query!r} emptied the rescue list")

    def test_query_names_the_card_that_leads(self):
        leading = {
            "hypotension": "post_intubation_hypotension",
            "the patient has hypotension": "post_intubation_hypotension",
            "patient is hypotensive after intubation": "post_intubation_hypotension",
            "laryngospasm": "laryngospasm",
            "last": "local_anesthetic_systemic_toxicity",
            "loss of capture": "failed_transvenous_capture",
            "cant ventilate": "failed_airway",
        }
        for query, expected_id in leading.items():
            with self.subTest(query=query):
                self.assertEqual(rescue_matches(query)[0], expected_id)

    def test_precise_multiword_queries_stay_precise(self):
        # Graceful degradation must not cost precision when every word matches.
        self.assertEqual(rescue_matches("lost wire"), ["lost_wire"])
        self.assertEqual(rescue_matches("capture"), ["failed_transvenous_capture"])
        self.assertEqual(rescue_matches("lipid"), ["local_anesthetic_systemic_toxicity"])

    def test_nonsense_stays_empty_and_blank_returns_everything(self):
        self.assertEqual(rescue_matches("zzzznotaclinicalterm"), [])
        self.assertEqual(len(rescue_matches("   ")), len(RESCUE_CARDS))

    def test_editorial_metadata_is_not_searchable(self):
        # Version/date strings are not clinical search text.
        self.assertEqual(rescue_matches("0.2.0"), [])


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
