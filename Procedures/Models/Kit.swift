import Foundation

struct Kit: Identifiable, Codable, Hashable {

    let id: String
    let title: String
    let subtitle: String
    let category: ProcedureCategory
    let relatedProcedureIDs: [String]
    let tags: [String]
    let lastReviewed: String
    let version: String
    let reviewerStatus: ReviewerStatus?

    /// Content provenance; optional in the wire format. Undeclared provenance
    /// reads as an AI draft, never as trusted human work.
    let contentSource: ContentSource?

    let inKit: [String]
    let outsideKit: [String]
    let commonlyForgotten: [String]
    let patientSetup: [String]
    let sterileSetup: [String]
    let backupEquipment: [String]
    let references: [String]

    var reviewer: ReviewerStatus { reviewerStatus ?? .unreviewedDefault }

    /// Never-nil provenance: undeclared content reads as an AI draft.
    var source: ContentSource { contentSource ?? .undeclaredDefault }

    /// Items eligible for the interactive room-setup checklist.
    var allChecklistItems: [String] { inKit + outsideKit }

    /// What a clinician vouches for on a kit: the physical contents and the
    /// patient setup. Subtitle, tags, and references are excluded.
    ///
    /// `commonlyForgotten` is included because it is the highest-value list on
    /// a room-setup card — the whole point of one — and it was invisible to
    /// reviews. The named boundaries matter more here than anywhere else:
    /// moving an item from `inKit` to `outsideKit` is a real correction that
    /// left a flat concatenation byte-identical.
    var materialFingerprint: String {
        ContentFingerprint.make(sections: [
            ("inKit", inKit),
            ("outsideKit", outsideKit),
            ("commonlyForgotten", commonlyForgotten),
            ("patientSetup", patientSetup),
            ("sterileSetup", sterileSetup)
        ])
    }

    struct KitRelevance: Hashable {
        let matchedTokens: Int
        /// Query tokens appearing literally in the title.
        let exactTitleHits: Int
        /// Query tokens appearing in the title directly or through a synonym.
        let titleHits: Int

        var isMatch: Bool { matchedTokens > 0 }
    }

    /// Scores the kit against already-normalized query tokens.
    ///
    /// Matching used to be a strict AND across every typed word, so one word
    /// the kit happened not to contain collapsed the result to zero. Counting
    /// matched tokens alone is not the fix either: with synonym expansion and
    /// substring matching, a generic word buried in some other kit's checklist
    /// scores that kit higher than the kit the reader named. "chest tube
    /// setup" is the case — "setup" appears in the RSI, cric, and CVC kits but
    /// not in the chest tube kit's own text, so ranking on token count alone
    /// puts three wrong kits above the right one.
    ///
    /// Title hits break that: what the reader typed as the *name* of the thing
    /// outranks a word that merely appears somewhere in a checklist.
    func relevance(forTokens tokens: [String]) -> KitRelevance {
        guard !tokens.isEmpty else {
            return KitRelevance(matchedTokens: 0, exactTitleHits: 0, titleHits: 0)
        }
        let haystack = searchFields().joined(separator: " ").lowercased()
        let titleText = title.lowercased()

        var matched = 0
        var exactTitleMatches = 0
        var titleMatches = 0
        for token in tokens {
            let group = ClinicalSynonyms.group(for: token)
            if group.contains(where: { haystack.contains($0) }) { matched += 1 }
            if group.contains(where: { titleText.contains($0) }) { titleMatches += 1 }
            if titleText.contains(token) { exactTitleMatches += 1 }
        }
        return KitRelevance(
            matchedTokens: matched,
            exactTitleHits: exactTitleMatches,
            titleHits: titleMatches
        )
    }

    /// Flattened searchable text, for the corpus vocabulary that stops typo
    /// recovery rewriting a word the content actually uses.
    var searchCorpusText: String { searchFields().joined(separator: " ") }

    private func searchFields() -> [String] {
        var fields: [String] = []
        fields.reserveCapacity(6 + tags.count + inKit.count + outsideKit.count + commonlyForgotten.count + patientSetup.count)
        fields.append(title)
        fields.append(subtitle)
        fields.append(category.rawValue)
        fields.append(contentsOf: tags)
        fields.append(contentsOf: inKit)
        fields.append(contentsOf: outsideKit)
        fields.append(contentsOf: commonlyForgotten)
        fields.append(contentsOf: patientSetup)
        fields.append(contentsOf: sterileSetup)
        fields.append(contentsOf: backupEquipment)
        return fields
    }
}

enum KitStore {
    struct Load {
        let kits: [Kit]
        let total: Int
        var dropped: Int { total - kits.count }
    }

    static func loadFromBundle() throws -> Load {
        guard let url = Bundle.main.url(forResource: "kits", withExtension: "json") else {
            throw KitLoadingError.missingBundleResource
        }
        let data = try Data(contentsOf: url)
        let wrapped = try JSONDecoder().decode([FailableDecodable<Kit>].self, from: data)
        let kits = wrapped.compactMap(\.value)
            .sorted { lhs, rhs in
                if lhs.category.rawValue != rhs.category.rawValue {
                    return lhs.category.rawValue.localizedCaseInsensitiveCompare(rhs.category.rawValue) == .orderedAscending
                }
                return lhs.title.localizedCaseInsensitiveCompare(rhs.title) == .orderedAscending
            }
        return Load(kits: kits, total: wrapped.count)
    }
}

enum KitLoadingError: LocalizedError {
    case missingBundleResource

    var errorDescription: String? {
        "Could not find kits.json in the app bundle. Confirm it is included in the target Resources build phase."
    }
}
