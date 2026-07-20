import Foundation

struct Procedure: Identifiable, Codable, Hashable {
    let id: String
    let title: String
    let category: ProcedureCategory
    let difficulty: ProcedureDifficulty
    let reviewTime: String
    let setting: [ProcedureSetting]
    let lastReviewed: String
    let version: String
    let tags: [String]
    let visualAssets: [ProcedureVisualAsset]?

    /// Structured local-anesthetic safety limits. Required content for
    /// Regional Anesthesia procedures (enforced by the validators); nil for
    /// categories where a max-dose block does not apply.
    let dosing: ProcedureDosing?

    /// Editorial review state. Optional in the wire format for decode
    /// resilience; absent content is treated as the conservative default.
    /// Declared before `sections` so the memberwise initializer reads with the
    /// rest of the metadata.
    let reviewerStatus: ReviewerStatus?

    /// Content provenance. Optional in the wire format; absent provenance is
    /// treated as an AI draft, never as trusted human work.
    let contentSource: ContentSource?

    let sections: ProcedureSections

    /// Never-nil review state for UI and validation: an undeclared status is
    /// reported as needing clinical review rather than silently trusted.
    var reviewer: ReviewerStatus { reviewerStatus ?? .unreviewedDefault }

    /// Never-nil provenance: undeclared content reads as an AI draft.
    var source: ContentSource { contentSource ?? .undeclaredDefault }

    var primaryVisualAsset: ProcedureVisualAsset? { visualAssets?.first }
}

/// Machine-checkable dosing limits for procedures that inject local
/// anesthetic. This is first-class data — not prose — so the validator can
/// refuse content that names a volume without a weight-based ceiling, and the
/// UI can render the ceiling before the operator draws up.
struct ProcedureDosing: Codable, Hashable {
    struct Agent: Codable, Hashable, Identifiable {
        var id: String { agent }
        /// Agent name including plain/with-epinephrine qualifier.
        let agent: String
        /// Concentration-to-mg conversion the operator needs at the bedside,
        /// e.g. "0.25% = 2.5 mg/mL".
        let concentrationNote: String
        /// Conventional weight-based maximum in mg/kg.
        let maxDoseMgPerKg: Double
        /// Conventional absolute ceiling in mg regardless of weight.
        let absoluteMaxMg: Double?
    }

    let agents: [Agent]
    /// A worked mg/mL calculation at this block's typical volume.
    let workedExample: String
    /// Cumulative-dose rule covering bilateral blocks, prior infiltration,
    /// and repeat dosing in the same encounter.
    let cumulativeWarning: String
    /// Non-negotiable monitoring and preparation actions (lipid location,
    /// incremental injection, monitoring window).
    let monitoring: [String]
    /// Rescue card the operator escalates to, typically LAST.
    let rescueCardID: String?
}

struct ProcedureVisualAsset: Identifiable, Codable, Hashable {
    enum Kind: String, Codable, Hashable, CaseIterable {
        case landmark = "Landmark"
        case probePosition = "Probe Position"
        case dangerZone = "Danger Zone"
        case confirmation = "Confirmation"
        case setup = "Setup"
    }

    let id: String
    let kind: Kind
    let title: String
    let subtitle: String
    let assetName: String?
    let systemImage: String?
    let caption: String
    let clinicalWarning: String?
}

struct ProcedureSections: Codable, Hashable {
    let shiftMode: [String]
    let indications: [String]
    let contraindications: [String]
    let anatomy: [String]
    let equipment: [String]
    let positioning: [String]
    let steps: [String]
    let ultrasound: [String]
    let confirmation: [String]
    let troubleshooting: [String]
    let complications: [String]
    let aftercare: [String]
    let documentation: [String]
    let seniorPearls: [String]
    let references: [String]
}

enum ProcedureCategory: String, Codable, CaseIterable, Identifiable {
    case airway = "Airway"
    case vascularAccess = "Vascular Access"
    case thoracic = "Thoracic"
    case cardiacResuscitation = "Cardiac / Resuscitation"
    case neuro = "Neuro"
    case regionalAnesthesia = "Regional Anesthesia"
    case woundSoftTissue = "Wound / Soft Tissue"
    case ultrasoundGuided = "Ultrasound-Guided"
    case sedationAnalgesia = "Sedation & Analgesia"
    case other = "Other"

    var id: String { rawValue }
}

enum ProcedureDifficulty: String, Codable {
    case basic = "Basic"
    case intermediate = "Intermediate"
    case advanced = "Advanced"
    case rareCrash = "Rare-Crash"
}

enum ProcedureSetting: String, Codable, Hashable {
    case ed = "ED"
    case icu = "ICU"
    case trauma = "Trauma"
    case peds = "Peds"
}

enum ProcedureDetailSection: String, CaseIterable, Identifiable {
    case shiftMode = "Shift Mode"
    case visuals = "Visuals"
    case equipment = "Equipment"
    case steps = "Steps"
    case complications = "Complications"
    case documentation = "Documentation"
    case deepReview = "Deep Review"

    var id: String { rawValue }
}
