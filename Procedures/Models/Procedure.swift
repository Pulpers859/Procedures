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

    /// Structured medication dosing for procedures that give systemic drugs
    /// (currently RSI). Separate from `dosing`, which is a local-anaesthetic
    /// *ceiling* model: its `maxDoseMgPerKg` means "never exceed", while an
    /// induction or paralytic dose is a target to hit. Rendering one as the
    /// other would put a target dose under a "Max Dose" heading.
    let medicationDosing: ProcedureMedicationDosing?

    /// Editorial review state. Optional in the wire format for decode
    /// resilience; absent content is treated as the conservative default.
    /// Declared before `sections` so the memberwise initializer reads with the
    /// rest of the metadata.
    let reviewerStatus: ReviewerStatus?

    /// Content provenance. Optional in the wire format; absent provenance is
    /// treated as an AI draft, never as trusted human work.
    let contentSource: ContentSource?

    /// `var` so locally authored edits can be overlaid onto a copy. The
    /// bundled JSON is still never mutated — ProcedureEditStore merges into a
    /// value copy at load time.
    var sections: ProcedureSections

    /// Never-nil review state for UI and validation: an undeclared status is
    /// reported as needing clinical review rather than silently trusted.
    var reviewer: ReviewerStatus { reviewerStatus ?? .unreviewedDefault }

    /// Never-nil provenance: undeclared content reads as an AI draft.
    var source: ContentSource { contentSource ?? .undeclaredDefault }

    var primaryVisualAsset: ProcedureVisualAsset? { visualAssets?.first }

    /// Fingerprint of the parts a clinician is actually vouching for when they
    /// sign this off. Deliberately excludes tags, references, documentation,
    /// and visual metadata: those change for editorial reasons and must not
    /// disturb an existing review.
    /// Sections the reader is clinically vouching for. `shiftMode` is the
    /// default landing section and the condensed crash-path text — the
    /// highest-traffic clinical content in the app — and it was not covered,
    /// so a bundled rewrite of it left every sign-off reading "Reviewed".
    /// `equipment`, `confirmation` and `troubleshooting` are material for the
    /// same reason: the wrong kit, an unverified placement, or a missing
    /// bailout all change what the reader endorsed.
    ///
    /// Still excluded, deliberately: anatomy, indications, positioning,
    /// ultrasound, aftercare, documentation, seniorPearls, references, tags
    /// and visual metadata. Those move for editorial reasons, and a notice
    /// that fires on every update is a notice nobody reads.
    static let materialSectionNames = [
        "shiftMode", "contraindications", "equipment",
        "steps", "confirmation", "troubleshooting", "complications"
    ]

    var materialFingerprint: String {
        var grouped: [(name: String, lines: [String])] = [
            ("shiftMode", sections.shiftMode),
            ("contraindications", sections.contraindications),
            ("equipment", sections.equipment),
            ("steps", sections.steps),
            ("confirmation", sections.confirmation),
            ("troubleshooting", sections.troubleshooting),
            ("complications", sections.complications)
        ]
        if let dosing {
            var doseParts: [String] = []
            for agent in dosing.agents {
                let ceiling = agent.absoluteMaxMg.map(Self.doseString) ?? "-"
                // Strengths are hashed because the calculator divides by them:
                // a percentage edited alone changes every millilitre the card
                // prints while the milligram ceiling stays put.
                let strengths = agent.concentrationsPercent.map(Self.doseString).joined(separator: ",")
                // Spelled out rather than interpolating the Bool, whose Swift
                // and Python spellings differ ("true" vs "True") and would
                // silently desynchronise the two implementations.
                let epinephrine = agent.withEpinephrine ? "epi" : "plain"
                doseParts.append(
                    "\(agent.agent)|\(epinephrine)|\(Self.doseString(agent.maxDoseMgPerKg))"
                    + "|\(ceiling)|\(strengths)|\(agent.note ?? "-")"
                )
            }
            doseParts.append(dosing.cumulativeWarning)
            doseParts.append(contentsOf: dosing.caveats ?? [])
            grouped.append(("dosing", doseParts))
        }
        if let medicationDosing {
            // A drug dose is the most material content in the app. Omitting it
            // here would let a rocuronium dose change while every sign-off
            // still read "Reviewed" — the same blind spot that let references
            // move unnoticed under the audit fingerprint.
            var medParts: [String] = [medicationDosing.indication]
            for med in medicationDosing.medications {
                let high = med.doseHighPerKg.map(Self.doseString) ?? "-"
                medParts.append(
                    "\(med.medication)|\(med.role)|\(Self.doseString(med.doseLowPerKg))"
                    + "|\(high)|\(med.unit)|\(med.caution ?? "-")"
                )
            }
            medParts.append(contentsOf: medicationDosing.selectionGuidance ?? [])
            medParts.append(medicationDosing.inductionRequirement)
            grouped.append(("medicationDosing", medParts))
        }
        return ContentFingerprint.make(sections: grouped)
    }

    /// Fixed-precision, locale-independent dose formatting.
    ///
    /// Interpolating a `Double` directly would let a formatting difference read
    /// as a dose change and flag a review that nothing clinically relevant
    /// touched. `String.init` is also too overloaded to resolve against an
    /// optional `Double` here, which is what broke the build.
    private static func doseString(_ value: Double) -> String {
        String(format: "%.4f", value)
    }
}

/// Machine-checkable dosing limits for procedures that inject local
/// anesthetic. This is first-class data — not prose — so the validator can
/// refuse content that names a volume without a weight-based ceiling, and the
/// UI can compute the ceiling before the operator draws up.
struct ProcedureDosing: Codable, Hashable {
    struct Agent: Codable, Hashable, Identifiable {
        /// Plain and with-epinephrine are separate entries for the same drug,
        /// so the drug name alone is not unique.
        var id: String { displayName }
        /// Drug name only — no strength, no epinephrine qualifier. Both are
        /// held as data below so the calculator can compute with them.
        let agent: String
        /// Epinephrine raises the ceiling by slowing systemic absorption, so
        /// it selects a different `maxDoseMgPerKg`. A flag rather than a
        /// suffix on the name: the arithmetic depends on it.
        let withEpinephrine: Bool
        /// Conventional weight-based maximum in mg/kg.
        let maxDoseMgPerKg: Double
        /// Conventional absolute ceiling in mg regardless of weight.
        let absoluteMaxMg: Double?
        /// Stocked strengths, strongest-selling first — element 0 is what the
        /// calculator preselects. Held as percentages rather than mg/mL
        /// because the vial is labelled in percent and the conversion is
        /// exact, so deriving it removes a number that could disagree.
        let concentrationsPercent: [Double]
        /// Optional caveat shown beside the ceiling. Carries the reason an
        /// entry is missing as much as anything else: without it, a reader
        /// hunting for ropivacaine with epinephrine finds no row and no
        /// explanation, and cannot tell an omission from an oversight.
        let note: String?

        var displayName: String {
            withEpinephrine ? "\(agent) with epinephrine" : agent
        }

        /// Exact by definition: 1% is 1 g per 100 mL, which is 10 mg/mL.
        static func mgPerML(percent: Double) -> Double { percent * 10 }

        /// Ceiling in mg for a given body weight, already capped.
        func maxMilligrams(forWeightKg weight: Double) -> Double {
            let weightBased = maxDoseMgPerKg * weight
            guard let absoluteMaxMg else { return weightBased }
            return min(weightBased, absoluteMaxMg)
        }

        /// True when the absolute ceiling — not the patient's weight — is what
        /// limits the dose. The UI marks this, because a reader who does not
        /// notice will scale the number up for a bigger patient.
        func isCapped(atWeightKg weight: Double) -> Bool {
            guard let absoluteMaxMg else { return false }
            return maxDoseMgPerKg * weight > absoluteMaxMg
        }
    }

    let agents: [Agent]
    /// Cumulative-dose rule covering bilateral blocks, prior infiltration,
    /// and repeat dosing in the same encounter.
    let cumulativeWarning: String
    /// Qualifiers on the computed number — lean body weight, reduction at the
    /// extremes of age, dead space in the giving set.
    ///
    /// Data rather than text in the view because they are not universal. "Reduce
    /// by about 25% at the extremes of age" is right for an infiltration ceiling
    /// and wrong for the fixed 0.5 mg/kg intraosseous analgesic dose, so a card
    /// shared by both cannot state either from inside the view.
    let caveats: [String]?
    /// Non-negotiable monitoring and preparation actions (lipid location,
    /// incremental injection, monitoring window).
    let monitoring: [String]
    /// Rescue card the operator escalates to, typically LAST.
    let rescueCardID: String?
}

/// Systemic medication doses given as part of a procedure, as first-class data
/// rather than prose so the validator can check them and the UI can show a
/// range as a range.
///
/// Doses here are *targets*, not ceilings — the opposite of `ProcedureDosing`.
/// A dose may be a single value (`doseHighPerKg == nil`) or a range, and the UI
/// labels a range as such so it cannot be misread as a maximum.
struct ProcedureMedicationDosing: Codable, Hashable {
    struct Medication: Codable, Hashable, Identifiable {
        var id: String { medication }
        let medication: String
        /// Where the drug sits in the sequence, e.g. "Pretreatment",
        /// "Induction", "Neuromuscular blocker".
        let role: String
        let doseLowPerKg: Double
        /// nil for a single-value dose; set for a range.
        let doseHighPerKg: Double?
        /// "mg/kg" or "mcg/kg". Held as data because RSI mixes both and a
        /// hardcoded unit is how a microgram dose becomes a milligram dose.
        let unit: String
        let onset: String?
        let durationNote: String?
        let caution: String?

        var isRange: Bool {
            guard let doseHighPerKg else { return false }
            return doseHighPerKg > doseLowPerKg
        }
    }

    let indication: String
    let medications: [Medication]
    /// Which agent to reach for in a given physiology, e.g.
    /// "Haemodynamic instability or distributive shock: etomidate, ketamine".
    /// Optional: a block may carry doses without a selection table.
    let selectionGuidance: [String]?
    /// Guards the hazard this block would otherwise create: a card that names a
    /// paralytic dose and says nothing about induction invites paralysis
    /// without anaesthesia. Non-optional for that reason.
    let inductionRequirement: String
    let sourceNote: String
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

/// Properties are `var` so a locally edited section can replace one field on a
/// value copy. Decoding is unaffected.
struct ProcedureSections: Codable, Hashable {
    var shiftMode: [String]
    var indications: [String]
    var contraindications: [String]
    var anatomy: [String]
    var equipment: [String]
    var positioning: [String]
    var steps: [String]
    var ultrasound: [String]
    var confirmation: [String]
    var troubleshooting: [String]
    var complications: [String]
    var aftercare: [String]
    var documentation: [String]
    var seniorPearls: [String]
    var references: [String]
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
