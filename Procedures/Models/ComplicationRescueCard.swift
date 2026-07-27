import Foundation

private typealias RescueCardSearchField = String

struct ComplicationRescueCard: Identifiable, Codable, Hashable {
    enum Acuity: String, Codable, Hashable, CaseIterable {
        case crash = "Crash"
        case urgent = "Urgent"
        case watch = "Watch"
    }

    let id: String
    let title: String
    let acuity: Acuity
    let relatedProcedureIDs: [String]
    let trigger: [String]
    let immediateMoves: [String]
    let reassess: [String]
    let avoid: [String]
    let tags: [String]
    let lastReviewed: String
    let version: String
    let references: [String]

    /// Editorial review state; optional in the wire format for decode
    /// resilience. See `reviewer` for the never-nil value used by the app.
    let reviewerStatus: ReviewerStatus?

    /// Content provenance; optional in the wire format. Undeclared provenance
    /// reads as an AI draft, never as trusted human work.
    let contentSource: ContentSource?

    /// Never-nil review state: undeclared content is treated as needing review.
    var reviewer: ReviewerStatus { reviewerStatus ?? .unreviewedDefault }

    /// Never-nil provenance: undeclared content reads as an AI draft.
    var source: ContentSource { contentSource ?? .undeclaredDefault }

    /// Relevance of this card to a query, used to rank the rescue list.
    /// `matchedTokens` drives the match tier; the title counters break ties so
    /// the card actually named by the query leads.
    struct RescueRelevance: Hashable {
        let matchedTokens: Int
        let exactTitleHits: Int
        let titleHits: Int

        var isMatch: Bool { matchedTokens > 0 }
    }

    /// Scores the card against already-normalized query tokens.
    ///
    /// Matching used to be a strict AND across every typed word, which meant
    /// one word the card happened not to contain collapsed the crash path to
    /// zero results — "the patient has hypotension" returned nothing while
    /// "hypotension" returned five cards. Scoring instead lets the caller keep
    /// the best-matching tier, so a query degrades gracefully rather than
    /// falling off a cliff mid-resuscitation.
    func relevance(forTokens tokens: [String]) -> RescueRelevance {
        guard !tokens.isEmpty else {
            return RescueRelevance(matchedTokens: 0, exactTitleHits: 0, titleHits: 0)
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
        return RescueRelevance(
            matchedTokens: matched,
            exactTitleHits: exactTitleMatches,
            titleHits: titleMatches
        )
    }

    private func searchFields() -> [RescueCardSearchField] {
        var fields: [RescueCardSearchField] = []
        fields.reserveCapacity(2 + relatedProcedureIDs.count + trigger.count + immediateMoves.count + reassess.count + avoid.count + tags.count + references.count)
        fields.append(title)
        fields.append(acuity.rawValue)
        // `lastReviewed` and `version` are deliberately excluded: editorial
        // metadata is not clinical search text, and including it let a query
        // like "0.2.0" match every card.
        fields.append(contentsOf: relatedProcedureIDs)
        fields.append(contentsOf: trigger)
        fields.append(contentsOf: immediateMoves)
        fields.append(contentsOf: reassess)
        fields.append(contentsOf: avoid)
        fields.append(contentsOf: tags)
        fields.append(contentsOf: references)
        return fields
    }
}

enum ComplicationRescueCardStore {
    /// Result of a tolerant load: the cards that decoded plus how many records
    /// were present in the file, so callers can surface skipped entries.
    struct Load {
        let cards: [ComplicationRescueCard]
        let total: Int
        var dropped: Int { total - cards.count }
    }

    static func loadFromBundle() throws -> Load {
        guard let url = Bundle.main.url(forResource: "rescue_cards", withExtension: "json") else {
            throw RescueCardLoadingError.missingBundleResource
        }

        let data = try Data(contentsOf: url)
        let wrapped = try JSONDecoder().decode([FailableDecodable<ComplicationRescueCard>].self, from: data)
        let cards = wrapped.compactMap(\.value)
            .sorted { lhs, rhs in
                if lhs.acuity.sortOrder != rhs.acuity.sortOrder {
                    return lhs.acuity.sortOrder < rhs.acuity.sortOrder
                }
                return lhs.title.localizedCaseInsensitiveCompare(rhs.title) == .orderedAscending
            }
        return Load(cards: cards, total: wrapped.count)
    }
}

enum RescueCardLoadingError: LocalizedError {
    case missingBundleResource

    var errorDescription: String? {
        switch self {
        case .missingBundleResource:
            return "Could not find rescue_cards.json in the app bundle. Confirm it is included in the target Resources build phase."
        }
    }
}

extension ComplicationRescueCard.Acuity {
    var sortOrder: Int {
        switch self {
        case .crash: return 0
        case .urgent: return 1
        case .watch: return 2
        }
    }
}
