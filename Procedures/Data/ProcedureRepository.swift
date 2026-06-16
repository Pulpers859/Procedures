import Foundation

private typealias SearchableField = (text: String, weight: Int)

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
        "cordis": ["introducer", "mac", "central", "sheath", "resuscitation"],
        "vascath": ["dialysis", "catheter", "vas", "cath"],
        "vas": ["dialysis", "catheter"],
        "dialysis": ["vascath", "catheter", "crrt", "hemodialysis", "renal"],
        "piv": ["peripheral", "iv", "ultrasound", "access", "difficult"],
        "usgiv": ["ultrasound", "peripheral", "iv", "difficult", "access"],
        "canthotomy": ["cantholysis", "orbital", "retrobulbar", "eye", "compartment"],
        "orbital": ["canthotomy", "cantholysis", "retrobulbar", "eye", "compartment"],
        "wire": ["guidewire", "seldinger", "lost"],
        "pacer": ["transvenous", "pacemaker", "capture", "bradycardia"],
        "tvp": ["transvenous", "pacemaker", "capture"],
        "block": ["nerve", "anesthesia", "digital", "fascia", "iliaca"],
        "finger": ["digital", "nerve", "block"],
        "lac": ["laceration", "suture", "repair"],
        "suture": ["laceration", "repair", "wound", "closure"],
        "wound": ["laceration", "suture", "repair", "abscess"],
        "shoulder": ["dislocation", "reduction", "glenohumeral", "anterior"],
        "dislocation": ["shoulder", "reduction", "glenohumeral"],
        "fascia": ["iliaca", "ficb", "femoral", "hip", "block"],
        "iliaca": ["fascia", "ficb", "femoral", "hip", "block"],
        "hip": ["fascia", "iliaca", "femoral", "fracture", "block"],
        "thoracotomy": ["edt", "clamshell", "trauma", "pericardiotomy", "resuscitative"],
        "edt": ["thoracotomy", "clamshell", "trauma", "resuscitative"],
        "clamshell": ["thoracotomy", "edt", "trauma", "resuscitative"],
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
        "chest": ["thoracic", "tube", "pneumothorax"],
        "aline": ["arterial", "line", "radial", "hemodynamic", "monitoring", "abg"],
        "radial": ["arterial", "line", "wrist", "access"],
        "abg": ["arterial", "blood", "gas", "radial", "line"],
        "tap": ["thoracentesis", "paracentesis", "pleural", "ascites", "fluid"],
        "thoracentesis": ["pleural", "effusion", "thoracic", "tap", "drainage"],
        "pleural": ["thoracentesis", "effusion", "thoracic", "fluid"],
        "para": ["paracentesis", "ascites", "cirrhosis", "tap", "fluid"],
        "paracentesis": ["ascites", "cirrhosis", "sbp", "tap", "fluid"],
        "ascites": ["paracentesis", "cirrhosis", "sbp", "tap", "abdominal"],
        "sbp": ["spontaneous", "bacterial", "peritonitis", "paracentesis", "cirrhosis"],
        "abscess": ["incision", "drainage", "pus", "soft", "tissue", "mrsa"],
        "i&d": ["abscess", "incision", "drainage", "pus"],
        "laryngospasm": ["airway", "sedation", "stridor", "succinylcholine", "crash"]
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
    @Published private(set) var loadWarning: String?
    @Published private(set) var rescueLoadWarning: String?
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
