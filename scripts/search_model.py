"""The app's search pipeline, ported to Python.

Mirrors ClinicalSynonyms + ProcedureRepository scoring in
ProcedureRepository.swift: tokenizer, synonym expansion, single-edit typo
recovery, and weighted contains-scoring. The port must stay behaviorally
identical to the Swift implementation; change both together.

This lives in scripts/ rather than scripts/tests/ because two things need it
now - the bedside regression suite and the ranking ratchet - and a second copy
of the scoring model would drift from the first the way the regional safety
spine did.

The index is a class rather than module state so a caller can score a
hypothetical corpus (content with an edit applied) against the shipped one.
Typo recovery depends on the whole corpus, so an edited snapshot has to build
its own index rather than borrow the default one.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Procedures" / "Resources"

PROCEDURES = json.loads((RESOURCES / "procedures.json").read_text(encoding="utf-8"))
RESCUE_CARDS = json.loads((RESOURCES / "rescue_cards.json").read_text(encoding="utf-8"))
SYNONYMS = json.loads((RESOURCES / "synonyms.json").read_text(encoding="utf-8"))

VOCABULARY = set(SYNONYMS)
for _terms in SYNONYMS.values():
    VOCABULARY.update(_terms)

STOP_WORDS = {
    "the", "and", "for", "with", "has", "have", "had", "was", "were", "are",
    "this", "that", "then", "than", "from", "into", "onto", "after", "before",
    "during", "while", "when", "why", "how", "what", "who", "his", "her",
    "their", "our", "your", "its", "patient", "pt", "still", "just", "very",
    "really", "some", "any", "all", "not", "but", "out", "off", "over",
    "under", "about", "also", "been", "being", "does", "did", "get", "got",
    "now", "new", "can", "cant", "wont", "doesnt",
    # Two-letter connectives; see the note in ProcedureRepository.stopWords.
    # "or" (operating room) and "no" (nitric oxide) are deliberately absent.
    "do", "is", "in", "of", "to", "on", "at", "an", "as", "be", "by",
    "so", "up", "it", "my", "me", "we", "us", "am",
}

ACUITY_ORDER = {"Crash": 0, "Urgent": 1, "Watch": 2}


def tokens(query):
    result = []
    for chunk in re.split(r"[\s,;/]+", query.strip().lower()):
        parts = [part for part in chunk.split("-") if part]
        if len(parts) > 1:
            result.append("".join(parts))
        result.extend(parts)
    return [token for token in result if len(token) > 1]


def content_tokens(query):
    raw = tokens(query)
    filtered = [token for token in raw if token not in STOP_WORDS]
    return filtered or raw


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


def card_haystack(card):
    # lastReviewed/version are deliberately excluded: editorial metadata is not
    # clinical search text. Mirrors ComplicationRescueCard.searchFields().
    return " ".join(
        [card["title"], card["acuity"]]
        + card.get("relatedProcedureIDs", []) + card.get("trigger", [])
        + card.get("immediateMoves", []) + card.get("reassess", [])
        + card.get("avoid", []) + card.get("tags", []) + card.get("references", [])
    ).lower()


class SearchIndex:
    """Scores queries against one snapshot of the content."""

    def __init__(self, procedures=None, rescue_cards=None):
        self.procedures = PROCEDURES if procedures is None else procedures
        self.rescue_cards = RESCUE_CARDS if rescue_cards is None else rescue_cards
        self._corpus_words = None

    def corpus_words(self):
        """Every word the shipped content actually uses.

        Mirrors ClinicalSynonyms.corpusWords. Typo recovery is for words that
        are not there: "lost" is one edit from "last" and was being rewritten
        into the LAST group, so a query about a lost airway answered with local
        anaesthetic systemic toxicity.
        """
        if self._corpus_words is None:
            words = set()
            for procedure in self.procedures:
                for text, _ in searchable_fields(procedure):
                    words.update(re.findall(r"[a-z0-9]+", text))
            for card in self.rescue_cards:
                words.update(re.findall(r"[a-z0-9]+", card_haystack(card)))
            self._corpus_words = words
        return self._corpus_words

    def fuzzy_match(self, token):
        if len(token) < 4 or token in VOCABULARY:
            return None
        if token in self.corpus_words():
            return None
        candidates = [word for word in VOCABULARY if within_one_edit(token, word)]
        return min(candidates) if candidates else None

    def group(self, token):
        if token in SYNONYMS:
            return [token] + SYNONYMS[token]
        corrected = self.fuzzy_match(token)
        if corrected:
            return [token, corrected] + SYNONYMS.get(corrected, [])
        return [token]

    def terms_for(self, query):
        terms = set()
        for token in content_tokens(query):
            terms.update(self.group(token))
        return terms

    def scored(self, query):
        """(id, score) for every procedure that matches, best first."""
        terms = self.terms_for(query)
        results = []
        for procedure in self.procedures:
            total = 0
            for term in terms:
                for text, weight in searchable_fields(procedure):
                    if term in text:
                        total += weight
            if total > 0:
                results.append((procedure, total))
        results.sort(key=lambda pair: (-pair[1], pair[0]["title"].lower()))
        return [(procedure["id"], score) for procedure, score in results]

    def search(self, query):
        return [pid for pid, _ in self.scored(query)]

    def rank_of(self, query, procedure_id):
        """1-based rank, or None when the query does not reach the record."""
        ids = self.search(query)
        return ids.index(procedure_id) + 1 if procedure_id in ids else None

    def rescue_matches(self, query):
        """Best-tier rescue ranking. Mirrors
        ProcedureRepository.searchRescueCards: keep every card satisfying the
        most query tokens, ordered by title relevance then acuity. Strict AND
        used to empty the crash screen whenever a single typed word was absent
        from a card."""
        query_tokens = content_tokens(query)
        if not query_tokens:
            return [card["id"] for card in self.rescue_cards]

        scored = []
        for card in self.rescue_cards:
            haystack = card_haystack(card)
            title = card["title"].lower()
            matched = exact_title = title_hits = 0
            for token in query_tokens:
                expansion = self.group(token)
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


DEFAULT_INDEX = SearchIndex()


def corpus_words():
    return DEFAULT_INDEX.corpus_words()


def fuzzy_match(token):
    return DEFAULT_INDEX.fuzzy_match(token)


def group(token):
    return DEFAULT_INDEX.group(token)


def search(query):
    return DEFAULT_INDEX.search(query)


def rescue_matches(query):
    return DEFAULT_INDEX.rescue_matches(query)


def self_retrieval_probes(procedure):
    """The queries a record should answer for: its own title and each of its
    own tags. Derived from the record, so a new procedure is covered the moment
    it is added and no hand-written expectation can go stale."""
    probes = [procedure["title"]]
    probes.extend(procedure.get("tags", []))
    seen, unique = set(), []
    for probe in probes:
        key = probe.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(probe)
    return unique
