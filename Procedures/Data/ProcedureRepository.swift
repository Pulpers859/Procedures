import Foundation

private typealias SearchableField = (text: String, weight: Int)

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

    /// Nearest vocabulary word within one edit, or nil. Only engages for
    /// tokens of 4+ characters, so short clinical shorthand ("ij", "lp",
    /// "abg") is never rewritten into something else.
    static func fuzzyMatch(for token: String) -> String? {
        guard token.count >= 4, !vocabulary.contains(token) else { return nil }
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

    init() {
        loadContent()
    }

    func loadContent() {
        loadProcedures()
        loadRescueCards()
        loadKits()
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
            procedures = decoded.sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
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
            rescueCards = load.cards
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

    func searchKits(_ query: String) -> [Kit] {
        guard !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return kits }
        return kits.filter { $0.matches(query) }
    }

    func search(_ query: String) -> [Procedure] {
        let terms = normalizedSearchTerms(from: query)
        guard !terms.isEmpty else { return procedures }

        return procedures
            .map { procedure in (procedure, score(for: procedure, matching: terms)) }
            .filter { $0.1 > 0 }
            .sorted {
                if $0.1 == $1.1 {
                    return $0.0.title.localizedCaseInsensitiveCompare($1.0.title) == .orderedAscending
                }
                return $0.1 > $1.1
            }
            .map(\.0)
    }

    func searchRescueCards(_ query: String) -> [ComplicationRescueCard] {
        rescueCards.filter { $0.matches(query) }
    }

    private func normalizedSearchTerms(from query: String) -> [String] {
        let tokens = ClinicalSynonyms.tokens(in: query)
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

    private func score(for procedure: Procedure, matching terms: [String]) -> Int {
        let fields = searchIndex[procedure.id] ?? Self.searchableFields(for: procedure)

        var total = 0
        for term in terms {
            for field in fields where field.text.contains(term) {
                total += field.weight
            }
        }
        return total
    }

    private func rebuildSearchIndex() {
        // `uniquingKeysWith` (not `uniqueKeysWithValues`) so duplicate IDs in the
        // shipped JSON degrade gracefully instead of trapping. Duplicates are a
        // validator blocker, but the runtime must never crash on bad content.
        searchIndex = Dictionary(
            procedures.map { ($0.id, Self.searchableFields(for: $0)) },
            uniquingKeysWith: { first, _ in first }
        )
    }

    /// Builds the lowercased, weighted fields a query is scored against. Field
    /// set and weights must match the scorer's expectations exactly; changing
    /// them changes ranking.
    private static func searchableFields(for procedure: Procedure) -> [SearchableField] {
        let sections = procedure.sections
        var fields: [SearchableField] = []
        fields.reserveCapacity(13)
        fields.append((procedure.title.lowercased(), 12))
        fields.append((procedure.category.rawValue.lowercased(), 7))
        fields.append((procedure.difficulty.rawValue.lowercased(), 4))
        fields.append((procedure.reviewTime.lowercased(), 2))
        fields.append((procedure.tags.joined(separator: " ").lowercased(), 10))
        fields.append((procedure.visualAssetsText.lowercased(), 7))
        fields.append((sections.shiftMode.joined(separator: " ").lowercased(), 8))
        fields.append((sections.equipment.joined(separator: " ").lowercased(), 6))
        fields.append((sections.steps.joined(separator: " ").lowercased(), 5))
        fields.append((sections.complications.joined(separator: " ").lowercased(), 5))
        fields.append((sections.troubleshooting.joined(separator: " ").lowercased(), 5))
        fields.append((sections.documentation.joined(separator: " ").lowercased(), 3))
        fields.append((sections.seniorPearls.joined(separator: " ").lowercased(), 4))
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
