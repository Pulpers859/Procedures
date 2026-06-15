import Foundation

struct ContentValidationIssue: Identifiable, Hashable {
    enum Severity: String, Hashable {
        case blocker = "Blocker"
        case warning = "Warning"
        case polish = "Polish"
    }

    let id = UUID()
    let severity: Severity
    let procedureID: String?
    let procedureTitle: String?
    let message: String

    var displayMessage: String {
        if let procedureTitle {
            return "\(procedureTitle): \(message)"
        }
        return message
    }
}

enum ContentValidator {
    static func validate(_ procedures: [Procedure]) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        let ids = procedures.map(\.id)
        let duplicateIDs = Dictionary(grouping: ids, by: { $0 }).filter { $0.value.count > 1 }.keys.sorted()
        if !duplicateIDs.isEmpty {
            issues.append(.init(severity: .blocker, procedureID: nil, procedureTitle: nil, message: "Duplicate procedure IDs: \(duplicateIDs.joined(separator: ", "))."))
        }

        for procedure in procedures {
            issues.append(contentsOf: validate(procedure))
        }

        return issues.sorted { lhs, rhs in
            if lhs.severity.sortOrder != rhs.severity.sortOrder {
                return lhs.severity.sortOrder < rhs.severity.sortOrder
            }
            return lhs.displayMessage.localizedCaseInsensitiveCompare(rhs.displayMessage) == .orderedAscending
        }
    }

    private static func validate(_ procedure: Procedure) -> [ContentValidationIssue] {
        var issues: [ContentValidationIssue] = []

        func add(_ severity: ContentValidationIssue.Severity, _ message: String) {
            issues.append(.init(severity: severity, procedureID: procedure.id, procedureTitle: procedure.title, message: message))
        }

        if procedure.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, "missing title.") }
        if procedure.lastReviewed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, "missing last-reviewed metadata.") }
        if procedure.version.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { add(.blocker, "missing version metadata.") }
        if procedure.tags.isEmpty { add(.warning, "missing search tags/synonyms.") }

        let required: [(String, [String], Int, ContentValidationIssue.Severity)] = [
            ("Shift Mode", procedure.sections.shiftMode, 6, .blocker),
            ("Equipment", procedure.sections.equipment, 5, .blocker),
            ("Steps", procedure.sections.steps, 5, .blocker),
            ("Complications", procedure.sections.complications, 4, .blocker),
            ("Troubleshooting", procedure.sections.troubleshooting, 3, .warning),
            ("Documentation", procedure.sections.documentation, 4, .warning),
            ("Senior Pearls", procedure.sections.seniorPearls, 2, .polish),
            ("References", procedure.sections.references, 1, .blocker)
        ]

        for (name, items, minimumCount, severity) in required {
            if items.isEmpty {
                add(severity, "missing \(name) content.")
            } else if items.count < minimumCount {
                add(severity == .blocker ? .warning : severity, "\(name) may be too thin for release-quality content; found \(items.count), target at least \(minimumCount).")
            }
        }

        let allContent = [
            procedure.sections.shiftMode,
            procedure.sections.equipment,
            procedure.sections.steps,
            procedure.sections.complications,
            procedure.sections.troubleshooting,
            procedure.sections.documentation,
            procedure.sections.seniorPearls
        ].flatMap { $0 }

        if allContent.contains(where: { $0.localizedCaseInsensitiveContains("monitor closely") }) {
            add(.polish, "contains vague phrase 'monitor closely'; replace with concrete reassessment actions.")
        }

        if procedure.difficulty == .advanced || procedure.difficulty == .rareCrash {
            let hasRescueLanguage = procedure.sections.troubleshooting.joined(separator: " ").localizedCaseInsensitiveContains("rescue") ||
                procedure.sections.shiftMode.joined(separator: " ").localizedCaseInsensitiveContains("backup") ||
                procedure.sections.troubleshooting.count >= 4
            if !hasRescueLanguage {
                add(.warning, "high-risk procedure needs an explicit rescue/failure plan.")
            }
        }

        return issues
    }
}

private extension ContentValidationIssue.Severity {
    var sortOrder: Int {
        switch self {
        case .blocker: return 0
        case .warning: return 1
        case .polish: return 2
        }
    }
}
