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

    func matches(_ query: String) -> Bool {
        let normalized = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return true }

        let expandedTerms = Self.normalizedSearchTerms(from: normalized)
        let haystack = searchFields()
            .joined(separator: " ")
            .lowercased()

        return expandedTerms.allSatisfy { haystack.contains($0) }
    }

    private func searchFields() -> [RescueCardSearchField] {
        var fields: [RescueCardSearchField] = []
        fields.reserveCapacity(4 + relatedProcedureIDs.count + trigger.count + immediateMoves.count + reassess.count + avoid.count + tags.count + references.count)
        fields.append(title)
        fields.append(acuity.rawValue)
        fields.append(lastReviewed)
        fields.append(version)
        fields.append(contentsOf: relatedProcedureIDs)
        fields.append(contentsOf: trigger)
        fields.append(contentsOf: immediateMoves)
        fields.append(contentsOf: reassess)
        fields.append(contentsOf: avoid)
        fields.append(contentsOf: tags)
        fields.append(contentsOf: references)
        return fields
    }

    private static func normalizedSearchTerms(from query: String) -> [String] {
        var terms = query
            .split { $0.isWhitespace || $0 == "," || $0 == ";" || $0 == "/" }
            .map(String.init)

        let synonyms: [String: [String]] = [
            "ett": ["endotracheal", "intubation", "airway", "tube"],
            "rsi": ["rapid", "sequence", "intubation", "airway"],
            "cvc": ["central", "venous", "catheter", "arterial"],
            "ij": ["internal", "jugular", "neck", "arterial"],
            "wire": ["guidewire", "seldinger", "lost"],
            "pacer": ["transvenous", "pacemaker", "capture", "bradycardia"],
            "tvp": ["transvenous", "pacemaker", "capture"],
            "hypotension": ["shock", "pressor", "blood", "pressure"],
            "apnea": ["sedation", "hypoxia", "ventilation", "bvm"],
            "cric": ["failed", "airway", "front", "neck"],
            "last": ["local", "anesthetic", "toxicity", "lipid"],
            "chest": ["thoracic", "tube", "pneumothorax"],
            "tube": ["endotracheal", "intubation", "thoracostomy", "chest"]
        ]

        for term in terms {
            if let matches = synonyms[term] {
                terms.append(contentsOf: matches)
            }
        }

        return Array(Set(terms.filter { !$0.isEmpty }))
    }
}

enum ComplicationRescueCardStore {
    static func loadFromBundle() throws -> [ComplicationRescueCard] {
        guard let url = Bundle.main.url(forResource: "rescue_cards", withExtension: "json") else {
            throw RescueCardLoadingError.missingBundleResource
        }

        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        return try decoder.decode([ComplicationRescueCard].self, from: data)
            .sorted { lhs, rhs in
                if lhs.acuity.sortOrder != rhs.acuity.sortOrder {
                    return lhs.acuity.sortOrder < rhs.acuity.sortOrder
                }
                return lhs.title.localizedCaseInsensitiveCompare(rhs.title) == .orderedAscending
            }
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

private extension ComplicationRescueCard.Acuity {
    var sortOrder: Int {
        switch self {
        case .crash: return 0
        case .urgent: return 1
        case .watch: return 2
        }
    }
}
