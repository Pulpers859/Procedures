import Foundation

/// `words` alongside `text` so a term can be matched at a word boundary.
/// Scoring on raw substrings meant "ear" matched the "ear" in *linear
/// transducer* — shipped in the equipment list of every ultrasound-guided
/// record — so "ear block" answered with the median nerve.
private typealias SearchableField = (text: String, words: Set<String>, weight: Int)

enum ContentLoadAuthority {
    static func authoritativeIDs(
        _ ids: Set<String>,
        loadError: String?,
        loadWarning: String?
    ) -> Set<String>? {
        guard !ids.isEmpty, loadError == nil, loadWarning == nil else { return nil }
        return ids
    }
}

/// Decodes one element of a JSON array without throwing: a malformed record
/// becomes `nil` instead of aborting the decode of the entire file. This keeps
/// a single bad procedure or rescue card from emptying the whole library while
/// still letting callers count and surface what was skipped.
struct FailableDecodable<Wrapped: Decodable>: Decodable {
    let value: Wrapped?

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        value = try? container.decode(Wrapped.self)
    }
}

/// Single source of truth for clinical shorthand expansion. Both the procedure
/// scorer and the rescue-card matcher read from this map so the two search
/// surfaces can never drift apart. The map itself ships as validated content
/// (`Resources/synonyms.json`, checked by scripts/validate_procedures.py)
/// rather than Swift source, so shorthand can be extended and reviewed like
/// any other content. Keys are lowercased shorthand; values are related terms.
enum ClinicalSynonyms {
    /// Loaded once from the bundle. An unreadable or missing file degrades
    /// search to exact matching; `ProcedureRepository` surfaces that as a
    /// content warning instead of failing silently.
    static let expansions: [String: [String]] = loadBundledExpansions() ?? [:]

    /// True when the bundled synonym map could not be loaded.
    static var loadFailed: Bool { expansions.isEmpty }

    private static func loadBundledExpansions() -> [String: [String]]? {
        guard let url = Bundle.main.url(forResource: "synonyms", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([String: [String]].self, from: data),
              !decoded.isEmpty
        else { return nil }
        return decoded
    }

    /// Every shorthand key and expansion term — the vocabulary single-edit
    /// typo recovery corrects toward.
    private static let vocabulary: Set<String> = {
        var words = Set(expansions.keys)
        for terms in expansions.values { words.formUnion(terms) }
        return words
    }()

    /// Splits a raw query into normalized, lowercased tokens. A hyphenated
    /// chunk contributes its parts AND their concatenation, so "a-line"
    /// searches as "aline" + "line" rather than dying on the hyphen.
    /// Single-character tokens are dropped: they substring-match nearly every
    /// field and only add ranking noise.
    static func tokens(in query: String) -> [String] {
        let chunks = query
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .split { $0.isWhitespace || $0 == "," || $0 == ";" || $0 == "/" }
        var result: [String] = []
        for chunk in chunks {
            let parts = chunk.split(separator: "-").map(String.init)
            if parts.count > 1 {
                result.append(parts.joined())
            }
            result.append(contentsOf: parts)
        }
        return result.filter { $0.count > 1 }
    }

    /// Filler words that carry no clinical meaning. A stressed clinician types
    /// sentences ("the patient is hypotensive after intubation"), and every one
    /// of these words used to count as a required term on the rescue path.
    /// Dropped before matching so phrasing does not change the answer.
    static let stopWords: Set<String> = [
        "the", "and", "for", "with", "has", "have", "had", "was", "were", "are",
        "this", "that", "then", "than", "from", "into", "onto", "after", "before",
        "during", "while", "when", "why", "how", "what", "who", "his", "her",
        "their", "our", "your", "its", "patient", "pt", "still", "just", "very",
        "really", "some", "any", "all", "not", "but", "out", "off", "over",
        "under", "about", "also", "been", "being", "does", "did", "get", "got",
        "now", "new", "can", "cant", "wont", "doesnt",
        // Verbs of intent and modals. A clinician types "the patient needs a
        // central line"; "needs" discriminates nothing but scored 14 points
        // and decided that query against the central line. "patient" and
        // "get" were already here for the same reason — this finishes the set.
        "need", "needs", "needed", "want", "wants", "wanted", "give", "gives",
        "given", "put", "puts", "take", "takes", "make", "makes", "use", "uses",
        "using", "require", "requires", "required", "going", "goes", "went",
        "let", "lets", "try", "trying", "help", "please", "should", "would",
        "could", "will", "shall", "must", "may", "might", "him", "them", "they",
        "she", "there", "here",
        // Two-letter connectives. The tokenizer keeps anything longer than one
        // character, so these survived and matched as substrings: "do" inside
        // *ab-do-minal*, "is" inside *ep-is-taxis*. That is enough to outscore
        // the procedure the sentence actually described.
        //
        // Deliberately absent: "or" and "no". The clinical vocabulary's own
        // two-letter terms are ij, io, iv, and lp, none of which are here —
        // but in an anaesthesia app "OR" reads as operating room and "NO" as
        // nitric oxide, and dropping a word the reader meant is worse than
        // keeping one they didn't.
        "do", "is", "in", "of", "to", "on", "at", "an", "as", "be", "by",
        "so", "up", "it", "my", "me", "we", "us", "am"
    ]

    /// Query tokens with filler removed. If a query is *only* filler the raw
    /// tokens are kept, so a literal search for such a word still does
    /// something rather than silently matching everything.
    static func contentTokens(in query: String) -> [String] {
        let raw = tokens(in: query)
        let filtered = raw.filter { !stopWords.contains($0) }
        return filtered.isEmpty ? raw : filtered
    }

    /// A token together with its synonyms — the OR-group that satisfies that
    /// token. Matching any one member counts the token as present. A token
    /// with no exact expansion falls back to single-edit typo recovery, so
    /// "crich" resolves through "cric" to the cricothyrotomy group.
    static func group(for token: String) -> [String] {
        if let expansion = expansions[token] { return [token] + expansion }
        if let corrected = fuzzyMatch(for: token) {
            return [token, corrected] + (expansions[corrected] ?? [])
        }
        return [token]
    }

    /// Every word that literally appears in the shipped content, populated at
    /// index build. Typo recovery is for words that are *not there*; a word the
    /// library actually uses is not a misspelling of a different one.
    ///
    /// Without this, "lost" was one edit from "last" and got rewritten into the
    /// LAST group — so "what do I do when the airway is lost" answered with
    /// local anaesthetic systemic toxicity and ranked nerve blocks above
    /// intubation. "pacing" → "packing" was the same bug, previously patched by
    /// narrowing one synonym; this removes the whole class.
    static private(set) var corpusWords: Set<String> = []

    static func registerCorpusWords(_ words: Set<String>) {
        corpusWords = words
    }

    /// Splits indexed text into the bare words used for the guard above.
    static func words(in text: String) -> [String] {
        text.lowercased().split { !$0.isLetter && !$0.isNumber }.map(String.init)
    }

    /// Nearest vocabulary word within one edit, or nil. Only engages for
    /// tokens of 4+ characters, so short clinical shorthand ("ij", "lp",
    /// "abg") is never rewritten into something else.
    static func fuzzyMatch(for token: String) -> String? {
        guard token.count >= 4, !vocabulary.contains(token) else { return nil }
        // A word the content actually contains is a real word, not a typo.
        guard !corpusWords.contains(token) else { return nil }
        return vocabulary.filter { isWithinOneEdit(token, $0) }.min()
    }

    /// True when the strings are equal or differ by one insertion, deletion,
    /// or substitution.
    static func isWithinOneEdit(_ first: String, _ second: String) -> Bool {
        if first == second { return true }
        let a = Array(first), b = Array(second)
        guard abs(a.count - b.count) <= 1 else { return false }
        var i = 0, j = 0, edits = 0
        while i < a.count && j < b.count {
            if a[i] == b[j] { i += 1; j += 1; continue }
            edits += 1
            if edits > 1 { return false }
            if a.count == b.count { i += 1; j += 1 }
            else if a.count > b.count { i += 1 }
            else { j += 1 }
        }
        return edits + (a.count - i) + (b.count - j) <= 1
    }
}

@MainActor
final class ProcedureRepository: ObservableObject {
    @Published private(set) var procedures: [Procedure] = [] {
        didSet { rebuildSearchIndex() }
    }

    /// Per-procedure lowercased, weighted search fields, computed once when
    /// `procedures` changes instead of on every keystroke and re-render. Keyed by
    /// procedure ID.
    private var searchIndex: [String: [SearchableField]] = [:]

    /// Memoized term rarity. Document frequency is a property of the whole
    /// corpus, so this is cleared whenever the index rebuilds — a stale entry
    /// would score a term against a library that no longer exists.
    private var rarityCache: [String: Int] = [:]
    @Published private(set) var rescueCards: [ComplicationRescueCard] = []
    @Published private(set) var kits: [Kit] = []
    @Published private(set) var loadError: String?
    @Published private(set) var rescueLoadError: String?
    @Published private(set) var kitLoadError: String?
    @Published private(set) var loadWarning: String?
    @Published private(set) var rescueLoadWarning: String?
    @Published private(set) var kitLoadWarning: String?
    @Published private(set) var contentIssues: [ContentValidationIssue] = []
    var contentWarnings: [String] { contentIssues.map(\.displayMessage) }

    /// Locally authored corrections, overlaid onto bundled content at load.
    /// Held weakly by reference so the repository can re-merge when edits
    /// change without owning the store's lifetime.
    private weak var editStore: ProcedureEditStore?

    init() {
        loadContent()
    }

    /// Connects the local edit layer and immediately re-merges. Called once at
    /// app start; edits made later call `reapplyEdits()`.
    func attachEditStore(_ store: ProcedureEditStore) {
        editStore = store
        reapplyEdits()
    }

    /// Re-reads bundled content and re-overlays local edits. Used after an edit
    /// so every surface — search index, detail views, validator — sees the same
    /// merged text.
    func reapplyEdits() {
        loadProcedures()
        revalidate()
    }

    private func revalidate() {
        contentIssues = ContentValidator.validate(procedures, rescueCards: rescueCards, kits: kits)
        if ClinicalSynonyms.loadFailed {
            contentIssues.append(.init(
                severity: .warning,
                procedureID: nil,
                procedureTitle: nil,
                message: "synonyms.json failed to load from the bundle; shorthand search is degraded to exact matching."
            ))
        }
    }

    // Badge informativeness used to be answered here, from the bundled
    // reviewer status alone. That made it structurally blind to the reader's
    // own sign-offs: reviewing a procedure changed nothing anywhere outside the
    // Review Center. The question now belongs to UserDataStore.badgePolicy(for:),
    // which can see both records. Nothing in the UI should ask the repository
    // about review state again.

    func loadContent() {
        loadProcedures()
        loadRescueCards()
        loadKits()
        registerCorpusVocabulary()
        contentIssues = ContentValidator.validate(procedures, rescueCards: rescueCards, kits: kits)
        if ClinicalSynonyms.loadFailed {
            contentIssues.append(.init(
                severity: .warning,
                procedureID: nil,
                procedureTitle: nil,
                message: "synonyms.json failed to load from the bundle; shorthand search is degraded to exact matching."
            ))
        }
    }

    func loadProcedures() {
        guard let url = Bundle.main.url(forResource: "procedures", withExtension: "json") else {
            loadError = "Could not find procedures.json in the app bundle. Confirm it is included in the target Resources build phase."
            procedures = []
            return
        }

        do {
            let data = try Data(contentsOf: url)
            let wrapped = try JSONDecoder().decode([FailableDecodable<Procedure>].self, from: data)
            let decoded = wrapped.compactMap(\.value)
            // Local corrections are overlaid before anything else sees the
            // content, so the search index, the validator, and every view all
            // read the same merged text.
            let merged = editStore?.applyEdits(to: decoded) ?? decoded
            procedures = merged.sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
            let dropped = wrapped.count - decoded.count
            if decoded.isEmpty {
                loadError = "procedures.json was read but no procedures could be decoded. Confirm the structure matches the current schema."
                loadWarning = nil
            } else {
                loadError = nil
                loadWarning = dropped > 0
                    ? "\(dropped) of \(wrapped.count) procedures could not be read and were skipped. The others are available; fix procedures.json to restore them."
                    : nil
            }
        } catch {
            loadError = "Failed to load procedures.json: \(error.localizedDescription)"
            procedures = []
            loadWarning = nil
        }
    }

    func loadRescueCards() {
        do {
            let load = try ComplicationRescueCardStore.loadFromBundle()
            // Acuity order, not file order. Browsing was showing raw JSON
            // sequence, which put an Urgent card above four Crash cards —
            // while the App Intent told Siri and Action-button users the list
            // was "Crash-acuity problems first". The sort key already existed
            // and was only ever applied to the search path.
            rescueCards = load.cards.sorted { lhs, rhs in
                if lhs.acuity.sortOrder != rhs.acuity.sortOrder {
                    return lhs.acuity.sortOrder < rhs.acuity.sortOrder
                }
                return lhs.title.localizedCaseInsensitiveCompare(rhs.title) == .orderedAscending
            }
            if load.cards.isEmpty {
                rescueLoadError = "rescue_cards.json was read but no rescue cards could be decoded. Confirm the structure matches the current schema."
                rescueLoadWarning = nil
            } else {
                rescueLoadError = nil
                rescueLoadWarning = load.dropped > 0
                    ? "\(load.dropped) of \(load.total) rescue cards could not be read and were skipped. The others are available; fix rescue_cards.json to restore them."
                    : nil
            }
        } catch {
            rescueLoadError = "Failed to load rescue_cards.json: \(error.localizedDescription)"
            rescueCards = []
            rescueLoadWarning = nil
        }
    }

    func loadKits() {
        do {
            let load = try KitStore.loadFromBundle()
            kits = load.kits
            if load.kits.isEmpty {
                kitLoadError = "kits.json was read but no kits could be decoded. Confirm the structure matches the current schema."
                kitLoadWarning = nil
            } else {
                kitLoadError = nil
                kitLoadWarning = load.dropped > 0
                    ? "\(load.dropped) of \(load.total) kits could not be read and were skipped. Fix kits.json to restore them."
                    : nil
            }
        } catch {
            kitLoadError = "Failed to load kits.json: \(error.localizedDescription)"
            kits = []
            kitLoadWarning = nil
        }
    }

    func procedure(withID id: String) -> Procedure? {
        procedures.first { $0.id == id }
    }

    func procedures(in category: ProcedureCategory) -> [Procedure] {
        procedures.filter { $0.category == category }
    }

    func kit(withID id: String) -> Kit? {
        kits.first { $0.id == id }
    }

    func kits(in category: ProcedureCategory) -> [Kit] {
        kits.filter { $0.category == category }
    }

    /// Ranked kit lookup.
    ///
    /// Deliberately *not* filtered to a best-matching tier. Kit text is short
    /// and heavily shared — every kit lists gloves, a drape, and a syringe —
    /// so a tier filter lets one incidental word decide the whole result: for
    /// "chest tube setup", "setup" appears in three other kits' checklists and
    /// not in the chest tube kit's own text, so tiering drops the one kit the
    /// reader named and returns three confident wrong answers. An empty result
    /// is recoverable at the bedside; a wrong one that looks right is not.
    ///
    /// Every match is kept and ordered by how well it matches, title first.
    /// With eight kits the list is short enough that ranking beats hiding.
    func searchKits(_ query: String) -> [Kit] {
        struct ScoredKit {
            let kit: Kit
            let relevance: Kit.KitRelevance
        }

        let tokens = ClinicalSynonyms.contentTokens(in: query)
        guard !tokens.isEmpty else { return kits }

        return kits
            .map { ScoredKit(kit: $0, relevance: $0.relevance(forTokens: tokens)) }
            .filter { $0.relevance.isMatch }
            .sorted { lhs, rhs in
                if lhs.relevance.exactTitleHits != rhs.relevance.exactTitleHits {
                    return lhs.relevance.exactTitleHits > rhs.relevance.exactTitleHits
                }
                if lhs.relevance.titleHits != rhs.relevance.titleHits {
                    return lhs.relevance.titleHits > rhs.relevance.titleHits
                }
                if lhs.relevance.matchedTokens != rhs.relevance.matchedTokens {
                    return lhs.relevance.matchedTokens > rhs.relevance.matchedTokens
                }
                return lhs.kit.title.localizedCaseInsensitiveCompare(rhs.kit.title) == .orderedAscending
            }
            .map(\.kit)
    }

    func search(_ query: String) -> [Procedure] {
        let terms = normalizedSearchTerms(from: query)
        guard !terms.isEmpty else { return procedures }
        let typed = Set(ClinicalSynonyms.contentTokens(in: query))

        return procedures
            .map { procedure in (procedure, score(for: procedure, matching: terms, typed: typed)) }
            .filter { $0.1 > 0 }
            .sorted {
                if $0.1 == $1.1 {
                    return $0.0.title.localizedCaseInsensitiveCompare($1.0.title) == .orderedAscending
                }
                return $0.1 > $1.1
            }
            .map(\.0)
    }

    /// Ranked rescue lookup. Returns the best-matching tier — every card that
    /// satisfies the most query tokens — rather than requiring all of them.
    /// Strict AND made one unmatched word empty the crash screen; keeping the
    /// top tier preserves that precision when the words do all match while
    /// degrading to the nearest cards when they do not.
    func searchRescueCards(_ query: String) -> [ComplicationRescueCard] {
        struct ScoredCard {
            let card: ComplicationRescueCard
            let relevance: ComplicationRescueCard.RescueRelevance
        }

        let tokens = ClinicalSynonyms.contentTokens(in: query)
        guard !tokens.isEmpty else { return rescueCards }

        let scored = rescueCards
            .map { ScoredCard(card: $0, relevance: $0.relevance(forTokens: tokens)) }
            .filter { $0.relevance.isMatch }
        guard let bestTier = scored.map({ $0.relevance.matchedTokens }).max() else { return [] }

        return scored
            .filter { $0.relevance.matchedTokens == bestTier }
            .sorted { lhs, rhs in
                if lhs.relevance.exactTitleHits != rhs.relevance.exactTitleHits {
                    return lhs.relevance.exactTitleHits > rhs.relevance.exactTitleHits
                }
                if lhs.relevance.titleHits != rhs.relevance.titleHits {
                    return lhs.relevance.titleHits > rhs.relevance.titleHits
                }
                if lhs.card.acuity.sortOrder != rhs.card.acuity.sortOrder {
                    return lhs.card.acuity.sortOrder < rhs.card.acuity.sortOrder
                }
                return lhs.card.title.localizedCaseInsensitiveCompare(rhs.card.title) == .orderedAscending
            }
            .map { $0.card }
    }

    private func normalizedSearchTerms(from query: String) -> [String] {
        // `contentTokens`, not `tokens`: the same filler-word filter the rescue
        // path uses. Scoring is substring-based, so a kept "the" matches
        // *ca-the-ter* and "are" matches *prep-are*, which is enough to score
        // every procedure in the library and bury the one the clinician
        // described. Typing a sentence is the normal way to use this under
        // pressure. The filter was written for that and only ever wired to one
        // of the two search paths.
        let tokens = ClinicalSynonyms.contentTokens(in: query)
        guard !tokens.isEmpty else { return [] }

        // Scoring is OR-based: every token, its synonyms, and any typo-
        // corrected group contribute, so a flat expanded set is exactly what
        // the scorer needs.
        var terms: [String] = []
        for token in tokens {
            terms.append(contentsOf: ClinicalSynonyms.group(for: token))
        }
        return Array(Set(terms))
    }

    /// How much a term discriminates, from how many records contain it.
    ///
    /// "block", "nerve", "regional" and "anesthesia" each appear in 31-38 of
    /// the 55 procedures; "carpal" appears in one. Weighting them equally is
    /// what let the generic half of a two-word query outvote the half that
    /// identified the procedure — "ear block" answered with the median nerve,
    /// "abdomen block" with the popliteal sciatic. Buckets rather than a log
    /// so this and its Python mirror cannot drift on floating point.
    private func rarity(of term: String) -> Int {
        if let cached = rarityCache[term] { return cached }
        var frequency = 0
        for procedure in procedures {
            let fields = searchIndex[procedure.id] ?? Self.searchableFields(for: procedure)
            if fields.contains(where: { Self.field($0, matches: term) }) { frequency += 1 }
        }
        let value: Int
        switch max(1, frequency) {
        case ...2: value = 4
        case ...15: value = 2
        default: value = 1
        }
        rarityCache[term] = value
        return value
    }

    /// Word-prefix match, so "block" still finds blocks/blocked/blocking but
    /// "ear" no longer finds *linear*.
    private static func field(_ field: SearchableField, matches term: String) -> Bool {
        field.words.contains { $0.hasPrefix(term) }
    }

    /// Each term scores its *best* field once, not every field it appears in.
    /// Summing across fields rewarded a record for repeating a word rather
    /// than for being the answer: a generic term sitting in nine fields
    /// outscored the rare term that actually named the procedure.
    ///
    /// A term the clinician typed outranks one the synonym map added. "tube"
    /// expands to endotracheal/intubation, which are rare and so score high —
    /// enough that "chest tube" answered with the intubation card.
    private func score(for procedure: Procedure, matching terms: [String], typed: Set<String>) -> Int {
        let fields = searchIndex[procedure.id] ?? Self.searchableFields(for: procedure)

        var total = 0
        for term in terms {
            var best = 0
            var sum = 0
            for field in fields where Self.field(field, matches: term) {
                best = max(best, field.weight)
                sum += field.weight
            }
            guard best > 0 else { continue }
            // Best field, plus a damped contribution from the others. Pure max
            // discards the signal that a record discusses the term throughout —
            // which is how "fib" stopped reaching the cardioversion card ahead
            // of the fascia iliaca block.
            let base = best + (sum - best) / 4
            let rarity = rarity(of: term)
            total += base * (typed.contains(term) ? rarity : max(1, rarity / 4))
        }
        return total
    }

    /// Feeds every word in the shipped content to the typo-recovery guard, so
    /// a real word is never rewritten into a different clinical term. Covers
    /// all three corpora because all three share one tokenizer.
    private func registerCorpusVocabulary() {
        var words: Set<String> = []
        for procedure in procedures {
            for field in searchIndex[procedure.id] ?? Self.searchableFields(for: procedure) {
                words.formUnion(ClinicalSynonyms.words(in: field.text))
            }
        }
        for card in rescueCards {
            words.formUnion(ClinicalSynonyms.words(in: card.searchCorpusText))
        }
        for kit in kits {
            words.formUnion(ClinicalSynonyms.words(in: kit.searchCorpusText))
        }
        ClinicalSynonyms.registerCorpusWords(words)
    }

    private func rebuildSearchIndex() {
        // `uniquingKeysWith` (not `uniqueKeysWithValues`) so duplicate IDs in the
        // shipped JSON degrade gracefully instead of trapping. Duplicates are a
        // validator blocker, but the runtime must never crash on bad content.
        searchIndex = Dictionary(
            procedures.map { ($0.id, Self.searchableFields(for: $0)) },
            uniquingKeysWith: { first, _ in first }
        )
        rarityCache.removeAll(keepingCapacity: true)
    }

    /// Builds the lowercased, weighted fields a query is scored against. Field
    /// set and weights must match the scorer's expectations exactly; changing
    /// them changes ranking.
    private static func searchableFields(for procedure: Procedure) -> [SearchableField] {
        let sections = procedure.sections
        var fields: [SearchableField] = []
        fields.reserveCapacity(13)
        func add(_ text: String, _ weight: Int) {
            let lowered = text.lowercased()
            fields.append((lowered, Set(ClinicalSynonyms.words(in: lowered)), weight))
        }
        add(procedure.title, 12)
        add(procedure.category.rawValue, 7)
        add(procedure.difficulty.rawValue, 4)
        add(procedure.reviewTime, 2)
        add(procedure.tags.joined(separator: " "), 10)
        add(procedure.visualAssetsText, 7)
        add(sections.shiftMode.joined(separator: " "), 8)
        add(sections.equipment.joined(separator: " "), 6)
        add(sections.steps.joined(separator: " "), 5)
        add(sections.complications.joined(separator: " "), 5)
        add(sections.troubleshooting.joined(separator: " "), 5)
        add(sections.documentation.joined(separator: " "), 3)
        add(sections.seniorPearls.joined(separator: " "), 4)
        return fields
    }

}

private extension Procedure {
    var visualAssetsText: String {
        (visualAssets ?? []).map { asset in
            [
                asset.title,
                asset.subtitle,
                asset.kind.rawValue,
                asset.caption,
                asset.clinicalWarning ?? ""
            ].joined(separator: " ")
        }
        .joined(separator: " ")
    }
}
