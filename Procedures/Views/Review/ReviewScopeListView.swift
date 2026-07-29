import SwiftUI

/// A slice of the review workspace, reachable by tapping any count in the
/// Review Center.
///
/// Every number on that screen was previously a dead end: the reader could see
/// "Warnings 156" or "Procedures edited locally 1" and had no way to reach the
/// things being counted. A count that cannot be opened is a claim the reader
/// has to take on faith.
enum ReviewScope: Hashable {
    case allProcedures
    case allRescueCards
    case allKits
    case disposition(LocalReviewDisposition)
    case changedSinceReview
    case issues(ContentValidationIssue.Severity)
    case locallyEdited

    var title: String {
        switch self {
        case .allProcedures: return "All Procedures"
        case .allRescueCards: return "All Rescue Cards"
        case .allKits: return "All Kits"
        case .disposition(let disposition): return disposition.rawValue
        case .changedSinceReview: return "Changed Since Review"
        case .issues(let severity): return "\(severity.rawValue)s"
        case .locallyEdited: return "Locally Edited"
        }
    }

    /// One line saying what the reader is looking at and what to do with it.
    var explanation: String {
        switch self {
        case .allProcedures:
            return "Every procedure in the library with its current review state."
        case .allRescueCards:
            return "Every rescue card in the library with its current review state."
        case .allKits:
            return "Every kit in the library with its current review state."
        case .disposition(let disposition):
            switch disposition {
            case .reviewed:
                return "Items you have signed off on this device. Export them from the Review Center to promote them in the repo."
            case .needsEdits:
                return "Items you flagged as needing changes. Open one to edit the text inline."
            case .deferred:
                return "Items you set aside. Deferring is not a review, so these still read as unreviewed everywhere else."
            }
        case .changedSinceReview:
            return "Still reviewed, and still counted as done. Listed only because the steps, doses, contraindications, or complications moved after you signed off."
        case .issues(let severity):
            switch severity {
            case .blocker:
                return "Structural problems that must be fixed before release."
            case .warning:
                return "Content the validator flagged as likely wrong or incomplete. Structural only — it says nothing about clinical correctness."
            case .polish:
                return "Non-blocking consistency and style findings."
            }
        case .locallyEdited:
            return "Procedures whose text you changed on this device. The originals are untouched in the repo until you export."
        }
    }
}

struct ReviewScopeListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @EnvironmentObject private var editStore: ProcedureEditStore
    let scope: ReviewScope

    var body: some View {
        List {
            Section {
                Text(scope.explanation)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            if isEmpty {
                Section {
                    // Reachable in normal use: clear a review while standing on
                    // the Reviewed list and it empties underneath you. A blank
                    // screen would read as a bug.
                    Label("Nothing here right now.", systemImage: "checkmark.seal")
                        .foregroundStyle(.secondary)
                }
            }

            if case .issues(let severity) = scope {
                issueSection(severity: severity)
            } else {
                contentSections
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle(scope.title)
        .navigationBarTitleDisplayMode(.inline)
    }

    // MARK: - Content

    @ViewBuilder
    private var contentSections: some View {
        if !procedures.isEmpty {
            Section("Procedures") {
                ForEach(procedures) { procedure in
                    NavigationLink {
                        ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
                    } label: {
                        ProcedureReviewRow(
                            title: procedure.title,
                            subtitle: procedure.category.rawValue,
                            detail: detail(for: procedure),
                            record: userData.localReviewRecord(for: procedure)
                        )
                    }
                }
            }
        }

        if !rescueCards.isEmpty {
            Section("Rescue Cards") {
                ForEach(rescueCards) { card in
                    NavigationLink {
                        RescueCardDetailView(card: card)
                    } label: {
                        ProcedureReviewRow(
                            title: card.title,
                            subtitle: "Rescue Card",
                            detail: card.acuity.rawValue,
                            record: userData.localReviewRecord(for: card)
                        )
                    }
                }
            }
        }

        if !kits.isEmpty {
            Section("Kits") {
                ForEach(kits) { kit in
                    NavigationLink {
                        KitDetailView(kit: kit)
                    } label: {
                        ProcedureReviewRow(
                            title: kit.title,
                            subtitle: "Kit",
                            detail: kit.category.rawValue,
                            record: userData.localReviewRecord(for: kit)
                        )
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func issueSection(severity: ContentValidationIssue.Severity) -> some View {
        // Grouped by procedure so a single item with nine findings reads as one
        // problem to open, not nine rows to scroll past. Issues with no owning
        // procedure (corpus-level findings) go in their own section.
        ForEach(issueGroups, id: \.0) { procedureID, issues in
            Section(repository.procedure(withID: procedureID)?.title ?? procedureID) {
                if let procedure = repository.procedure(withID: procedureID) {
                    NavigationLink {
                        ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
                    } label: {
                        Label("Open \(procedure.title)", systemImage: "arrow.forward.circle")
                            .font(.subheadline.weight(.semibold))
                    }
                }
                ForEach(issues) { issue in
                    Text(issue.displayMessage)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }

        if !unownedIssues.isEmpty {
            Section("Library-wide") {
                ForEach(unownedIssues) { issue in
                    Text(issue.displayMessage)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    // MARK: - Resolution
    //
    // Every list below is recomputed from the published stores on each render
    // rather than captured when the row was tapped, so clearing a review or
    // editing a procedure updates this screen while the reader is standing on it.

    private var procedures: [Procedure] {
        switch scope {
        case .allProcedures:
            return repository.procedures
        case .disposition(let disposition):
            return repository.procedures.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }
        case .changedSinceReview:
            return repository.procedures.filter {
                userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
            }
        case .locallyEdited:
            return repository.procedures.filter { editStore.hasEdits(for: $0.id) }
        case .allRescueCards, .allKits, .issues:
            return []
        }
    }

    private var rescueCards: [ComplicationRescueCard] {
        switch scope {
        case .allRescueCards:
            return repository.rescueCards
        case .disposition(let disposition):
            return repository.rescueCards.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }
        case .changedSinceReview:
            return repository.rescueCards.filter {
                userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
            }
        case .allProcedures, .allKits, .issues, .locallyEdited:
            return []
        }
    }

    private var kits: [Kit] {
        switch scope {
        case .allKits:
            return repository.kits
        case .disposition(let disposition):
            return repository.kits.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }
        case .changedSinceReview:
            return repository.kits.filter {
                userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
            }
        case .allProcedures, .allRescueCards, .issues, .locallyEdited:
            return []
        }
    }

    private var scopedIssues: [ContentValidationIssue] {
        guard case .issues(let severity) = scope else { return [] }
        return repository.contentIssues.filter { $0.severity == severity }
    }

    private var issueGroups: [(String, [ContentValidationIssue])] {
        let owned = scopedIssues.compactMap { issue -> (String, ContentValidationIssue)? in
            guard let procedureID = issue.procedureID else { return nil }
            return (procedureID, issue)
        }
        return Dictionary(grouping: owned, by: \.0)
            .map { ($0.key, $0.value.map(\.1)) }
            .sorted { lhs, rhs in
                let lhsTitle = repository.procedure(withID: lhs.0)?.title ?? lhs.0
                let rhsTitle = repository.procedure(withID: rhs.0)?.title ?? rhs.0
                return lhsTitle.localizedCaseInsensitiveCompare(rhsTitle) == .orderedAscending
            }
    }

    private var unownedIssues: [ContentValidationIssue] {
        scopedIssues.filter { $0.procedureID == nil }
    }

    private var isEmpty: Bool {
        if case .issues = scope { return scopedIssues.isEmpty }
        return procedures.isEmpty && rescueCards.isEmpty && kits.isEmpty
    }

    private func detail(for procedure: Procedure) -> String {
        if case .locallyEdited = scope {
            let sections = editStore.editedSections(for: procedure.id)
            guard !sections.isEmpty else { return "Edited on this device" }
            return sections.map(\.displayName).joined(separator: ", ")
        }
        let issues = repository.contentIssues.filter { $0.procedureID == procedure.id }
        guard !issues.isEmpty else { return "No item-specific validator issues" }
        let blockers = issues.filter { $0.severity == .blocker }.count
        let warnings = issues.filter { $0.severity == .warning }.count
        let polish = issues.filter { $0.severity == .polish }.count
        return [
            blockers > 0 ? "\(blockers) blocker" : nil,
            warnings > 0 ? "\(warnings) warning" : nil,
            polish > 0 ? "\(polish) polish" : nil
        ]
        .compactMap { $0 }
        .joined(separator: ", ")
    }
}
