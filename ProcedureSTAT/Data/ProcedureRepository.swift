import Foundation

@MainActor
final class ProcedureRepository: ObservableObject {
    @Published private(set) var procedures: [Procedure] = []
    @Published private(set) var loadError: String?
    @Published private(set) var contentIssues: [ContentValidationIssue] = []
    var contentWarnings: [String] { contentIssues.map(\.displayMessage) }

    init() {
        loadProcedures()
    }

    func loadProcedures() {
        guard let url = Bundle.main.url(forResource: "procedures", withExtension: "json") else {
            loadError = "Could not find procedures.json in the app bundle. Confirm it is included in the target Resources build phase."
            return
        }

        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            let decodedProcedures = try decoder.decode([Procedure].self, from: data)
            procedures = decodedProcedures.sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
            contentIssues = ContentValidator.validate(decodedProcedures)
            loadError = nil
        } catch {
            loadError = "Failed to load procedures.json: \(error.localizedDescription)"
            procedures = []
            contentIssues = []
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

    private func normalizedSearchTerms(from query: String) -> [String] {
        let lowercased = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !lowercased.isEmpty else { return [] }

        var terms = lowercased
            .split { $0.isWhitespace || $0 == "," || $0 == ";" || $0 == "/" }
            .map(String.init)

        let synonyms: [String: [String]] = [
            "ett": ["endotracheal", "intubation", "airway", "tube"],
            "tube": ["endotracheal", "intubation", "chest", "thoracostomy"],
            "rsi": ["rapid", "sequence", "intubation", "airway"],
            "line": ["central", "catheter", "vascular", "access"],
            "cvc": ["central", "venous", "catheter"],
            "ij": ["internal", "jugular", "central"],
            "cordis": ["introducer", "mac", "central"],
            "vascath": ["dialysis", "catheter", "vas", "cath"],
            "vas": ["dialysis", "catheter"],
            "pacer": ["transvenous", "pacemaker", "capture"],
            "block": ["nerve", "anesthesia", "digital"],
            "finger": ["digital", "nerve", "block"],
            "lac": ["laceration", "suture", "repair"],
            "cric": ["cricothyrotomy", "surgical", "airway", "front", "neck"],
            "chesttube": ["chest", "tube", "thoracostomy", "pneumothorax"],
            "pigtail": ["catheter", "thoracic", "pleural", "pneumothorax", "effusion"],
            "needle": ["decompression", "tension", "pneumothorax"],
            "pericardial": ["pericardiocentesis", "tamponade", "cardiac"],
            "sedation": ["procedural", "ketamine", "propofol", "apnea"],
            "lp": ["lumbar", "puncture", "csf", "meningitis"]
        ]

        for term in terms {
            if let matches = synonyms[term] {
                terms.append(contentsOf: matches)
            }
        }

        return Array(Set(terms.filter { !$0.isEmpty }))
    }

    private func score(for procedure: Procedure, matching terms: [String]) -> Int {
        let searchableFields: [(text: String, weight: Int)] = [
            (procedure.title, 12),
            (procedure.category.rawValue, 7),
            (procedure.difficulty.rawValue, 4),
            (procedure.reviewTime, 2),
            (procedure.tags.joined(separator: " "), 10),
            (procedure.sections.shiftMode.joined(separator: " "), 8),
            (procedure.sections.equipment.joined(separator: " "), 6),
            (procedure.sections.steps.joined(separator: " "), 5),
            (procedure.sections.complications.joined(separator: " "), 5),
            (procedure.sections.troubleshooting.joined(separator: " "), 5),
            (procedure.sections.documentation.joined(separator: " "), 3),
            (procedure.sections.seniorPearls.joined(separator: " "), 4)
        ].map { ($0.text.lowercased(), $0.weight) }

        var total = 0
        for term in terms {
            for field in searchableFields where field.text.contains(term) {
                total += field.weight
            }
        }
        return total
    }

}
