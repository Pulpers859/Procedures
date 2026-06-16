import Foundation

struct Kit: Identifiable, Codable, Hashable {
    enum KitCategory: String, Codable, Hashable, CaseIterable, Identifiable {
        case airway = "Airway"
        case vascularAccess = "Vascular Access"
        case thoracic = "Thoracic"
        case cardiacResuscitation = "Cardiac / Resuscitation"
        case neuro = "Neuro"
        case regionalAnesthesia = "Regional Anesthesia"
        case woundSoftTissue = "Wound / Soft Tissue"
        case sedationAnalgesia = "Sedation & Analgesia"
        case ultrasoundGuided = "Ultrasound-Guided"
        case other = "Other"

        var id: String { rawValue }
    }

    let id: String
    let title: String
    let subtitle: String
    let category: KitCategory
    let relatedProcedureIDs: [String]
    let tags: [String]
    let lastReviewed: String
    let version: String
    let reviewerStatus: ReviewerStatus?

    let inKit: [String]
    let outsideKit: [String]
    let commonlyForgotten: [String]
    let patientSetup: [String]
    let sterileSetup: [String]
    let backupEquipment: [String]
    let references: [String]

    var reviewer: ReviewerStatus { reviewerStatus ?? .unreviewedDefault }

    /// Items eligible for the interactive room-setup checklist.
    var allChecklistItems: [String] { inKit + outsideKit }

    func matches(_ query: String) -> Bool {
        let tokens = ClinicalSynonyms.tokens(in: query)
        guard !tokens.isEmpty else { return true }
        let haystack = searchFields().joined(separator: " ").lowercased()
        return tokens.allSatisfy { token in
            ClinicalSynonyms.group(for: token).contains { haystack.contains($0) }
        }
    }

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
