import Foundation

private typealias SearchableField = (text: String, weight: Int)

/// Single source of truth for clinical shorthand expansion. Both the procedure
/// scorer and the rescue-card matcher read from this map so the two search
/// surfaces can never drift apart (they previously kept separate, divergent
/// copies). Keys are lowercased shorthand; values are related terms.
enum ClinicalSynonyms {
    static let expansions: [String: [String]] = [
        "ett": ["endotracheal", "intubation", "airway", "tube"],
        "tube": ["endotracheal", "intubation", "chest", "thoracostomy"],
        "rsi": ["rapid", "sequence", "intubation", "airway"],
        "line": ["central", "catheter", "vascular", "access"],
        "cvc": ["central", "venous", "catheter", "arterial"],
        "ij": ["internal", "jugular", "central", "neck", "arterial"],
        "cordis": ["introducer", "mac", "central"],
        "vascath": ["dialysis", "catheter", "vas", "cath"],
        "vas": ["dialysis", "catheter"],
        "wire": ["guidewire", "seldinger", "lost"],
        "pacer": ["transvenous", "pacemaker", "capture", "bradycardia"],
        "tvp": ["transvenous", "pacemaker", "capture"],
        "block": ["nerve", "anesthesia", "digital"],
        "finger": ["digital", "nerve", "block"],
        "lac": ["laceration", "suture", "repair"],
        "cric": ["cricothyrotomy", "surgical", "airway", "front", "neck", "failed"],
        "chesttube": ["chest", "tube", "thoracostomy", "pneumothorax"],
        "pigtail": ["catheter", "thoracic", "pleural", "pneumothorax", "effusion"],
        "needle": ["decompression", "tension", "pneumothorax"],
        "ptx": ["pneumothorax", "tension", "chest", "thoracostomy"],
        "pericardial": ["pericardiocentesis", "tamponade", "cardiac"],
        "tamponade": ["pericardiocentesis", "pericardial", "cardiac", "effusion"],
        "sedation": ["procedural", "ketamine", "propofol", "apnea"],
        "lp": ["lumbar", "puncture", "csf", "meningitis"],
        "visual": ["landmark", "probe", "danger", "confirmation"],
        "probe": ["ultrasound", "landmark", "visual"],
        "hypotension": ["shock", "pressor", "blood", "pressure"],
        "apnea": ["sedation", "hypoxia", "ventilation", "bvm"],
        "last": ["local", "anesthetic", "toxicity", "lipid"],
        "chest": ["thoracic", "tube", "pneumothorax"]
    ]

    /// Splits a raw query into normalized, lowercased tokens.
    static func tokens(in query: String) -> [String] {
        query
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .split { $0.isWhitespace || $0 == "," || $0 == ";" || $0 == "/" }
            .map(String.init)
            .filter { !$0.isEmpty }
    }

    /// A token together with its synonyms — the OR-group that satisfies that
    /// token. Matching any one member counts the token as present.
    static func group(for token: String) -> [String] {
        [token] + (expansions[token] ?? [])
    }
}

@MainActor
final class ProcedureRepository: ObservableObject {
    @Published private(set) var procedures: [Procedure] = []
    @Published private(set) var rescueCards: [ComplicationRescueCard] = []
    @Published private(set) var loadError: String?
    @Published private(set) var rescueLoadError: String?
    @Published private(set) var contentIssues: [ContentValidationIssue] = []
    var contentWarnings: [String] { contentIssues.map(\.displayMessage) }

    init() {
        loadContent()
    }

    func loadContent() {
        loadProcedures()
        loadRescueCards()
        contentIssues = ContentValidator.validate(procedures, rescueCards: rescueCards)
    }

    func loadProcedures() {
        guard let url = Bundle.main.url(forResource: "procedures", withExtension: "json") else {
            loadError = "Could not find procedures.json in the app bundle. Confirm it is included in the target Resources build phase."
            procedures = []
            return
        }

        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            let decodedProcedures = try decoder.decode([Procedure].self, from: data)
            procedures = decodedProcedures.sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
            loadError = nil
        } catch {
            loadError = "Failed to load procedures.json: \(error.localizedDescription)"
            procedures = []
        }
    }

    func loadRescueCards() {
        do {
            rescueCards = try ComplicationRescueCardStore.loadFromBundle()
            rescueLoadError = nil
        } catch {
            rescueLoadError = "Failed to load rescue_cards.json: \(error.localizedDescription)"
            rescueCards = []
        }
    }

    func procedure(withID id: String) -> Procedure? {
        procedures.first { $0.id == id }
    }

    func procedures(in category: ProcedureCategory) -> [Procedure] {
        procedures.filter { $0.category == category }
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

        // Scoring is OR-based: every token and its synonyms contribute, so a
        // flat expanded set is exactly what the scorer needs.
        var terms = tokens
        for token in tokens {
            terms.append(contentsOf: ClinicalSynonyms.expansions[token] ?? [])
        }
        return Array(Set(terms))
    }

    private func score(for procedure: Procedure, matching terms: [String]) -> Int {
        let visualText = procedure.visualAssetsText
        let sections = procedure.sections

        var searchableFields: [SearchableField] = []
        searchableFields.reserveCapacity(13)
        searchableFields.append((procedure.title.lowercased(), 12))
        searchableFields.append((procedure.category.rawValue.lowercased(), 7))
        searchableFields.append((procedure.difficulty.rawValue.lowercased(), 4))
        searchableFields.append((procedure.reviewTime.lowercased(), 2))
        searchableFields.append((procedure.tags.joined(separator: " ").lowercased(), 10))
        searchableFields.append((visualText.lowercased(), 7))
        searchableFields.append((sections.shiftMode.joined(separator: " ").lowercased(), 8))
        searchableFields.append((sections.equipment.joined(separator: " ").lowercased(), 6))
        searchableFields.append((sections.steps.joined(separator: " ").lowercased(), 5))
        searchableFields.append((sections.complications.joined(separator: " ").lowercased(), 5))
        searchableFields.append((sections.troubleshooting.joined(separator: " ").lowercased(), 5))
        searchableFields.append((sections.documentation.joined(separator: " ").lowercased(), 3))
        searchableFields.append((sections.seniorPearls.joined(separator: " ").lowercased(), 4))

        var total = 0
        for term in terms {
            for field in searchableFields where field.text.contains(term) {
                total += field.weight
            }
        }
        return total
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
