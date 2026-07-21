import Foundation

enum CriticalCaseTemplate: String, Codable, CaseIterable, Identifiable {
    case freeform = "Freeform"
    case resuscitation = "Resuscitation"
    case sepsisShock = "Sepsis / Shock"
    case airway = "Airway"
    case cardiac = "Cardiac"
    case neuro = "Neuro"
    case trauma = "Trauma"
    case toxicology = "Toxicology"
    case pediatrics = "Pediatrics"
    case ob = "OB"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .freeform: return "square.and.pencil"
        case .resuscitation: return "bolt.heart"
        case .sepsisShock: return "drop.triangle"
        case .airway: return "lungs"
        case .cardiac: return "heart"
        case .neuro: return "brain.head.profile"
        case .trauma: return "cross.case"
        case .toxicology: return "pills"
        case .pediatrics: return "figure.and.child.holdinghands"
        case .ob: return "person.2"
        }
    }
}

enum MentorReviewDepth: String, Codable, CaseIterable, Identifiable {
    case quick = "Quick"
    case standard = "Standard"
    case brutal = "Brutal"

    var id: String { rawValue }

    var promptDirection: String {
        switch self {
        case .quick:
            return "Be concise. Identify the top three learning points and the one highest-risk miss."
        case .standard:
            return "Give a balanced attending-level debrief with specific reasoning feedback and alternate management paths."
        case .brutal:
            return "Be direct and unsparing about weak reasoning, delayed escalation, missed reassessments, and dangerous assumptions. Keep the tone professional and constructive."
        }
    }
}

enum MentorReviewLens: String, Codable, CaseIterable, Identifiable {
    case diagnosticReasoning = "Diagnostic Reasoning"
    case resuscitation = "Resuscitation"
    case disposition = "Disposition"
    case communication = "Communication"
    case systems = "Systems"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .diagnosticReasoning: return "stethoscope"
        case .resuscitation: return "bolt.fill"
        case .disposition: return "arrow.triangle.branch"
        case .communication: return "bubble.left.and.bubble.right"
        case .systems: return "gearshape.2"
        }
    }
}

struct CasePrivacyFinding: Codable, Hashable, Identifiable {
    enum Kind: String, Codable {
        case exactDate = "Exact date"
        case timestamp = "Timestamp"
        case ageOver89 = "Age over 89"
        case medicalRecordNumber = "MRN-like value"
        case contact = "Contact detail"
    }

    let id: UUID
    let kind: Kind
    let excerpt: String
    let suggestion: String

    init(kind: Kind, excerpt: String, suggestion: String) {
        self.id = UUID()
        self.kind = kind
        self.excerpt = excerpt
        self.suggestion = suggestion
    }
}

struct CaseMentorFeedback: Codable, Hashable, Identifiable {
    let id: UUID
    let createdAt: Date
    let model: String
    let content: String
    let privacyFindings: [CasePrivacyFinding]

    init(
        id: UUID = UUID(),
        createdAt: Date = Date(),
        model: String,
        content: String,
        privacyFindings: [CasePrivacyFinding]
    ) {
        self.id = id
        self.createdAt = createdAt
        self.model = model
        self.content = content
        self.privacyFindings = privacyFindings
    }
}

struct CriticalCaseReview: Codable, Hashable, Identifiable {
    let id: UUID
    var title: String
    var template: CriticalCaseTemplate
    var lens: MentorReviewLens
    var depth: MentorReviewDepth
    var caseText: String
    var createdAt: Date
    var updatedAt: Date
    var mentorFeedback: CaseMentorFeedback?

    init(
        id: UUID = UUID(),
        title: String,
        template: CriticalCaseTemplate,
        lens: MentorReviewLens,
        depth: MentorReviewDepth,
        caseText: String,
        createdAt: Date = Date(),
        updatedAt: Date = Date(),
        mentorFeedback: CaseMentorFeedback? = nil
    ) {
        self.id = id
        self.title = title
        self.template = template
        self.lens = lens
        self.depth = depth
        self.caseText = caseText
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.mentorFeedback = mentorFeedback
    }

    var displayTitle: String {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? "\(template.rawValue) case" : trimmed
    }
}
