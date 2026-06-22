import SwiftUI

struct ContentHealthView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore

    private var groupedIssues: [(ContentValidationIssue.Severity, [ContentValidationIssue])] {
        ContentValidationIssue.Severity.displayOrder.map { severity in
            (severity, repository.contentIssues.filter { $0.severity == severity })
        }.filter { !$0.1.isEmpty }
    }

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Content Validation")
                        .font(.title3.weight(.bold))
                    Text("This is a built-in editorial safety net. It does not prove clinical correctness, but it catches missing sections, weak metadata, duplicate IDs, and thin high-risk content before release.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }

            Section("Summary") {
                MetadataRow(icon: "list.bullet.rectangle", title: "Procedures", value: "\(repository.procedures.count)")
                MetadataRow(icon: "lifepreserver", title: "Rescue Cards", value: "\(repository.rescueCards.count)")
                MetadataRow(icon: "shippingbox", title: "Kits", value: "\(repository.kits.count)")
                MetadataRow(icon: "exclamationmark.octagon", title: "Blockers", value: "\(count(.blocker))")
                MetadataRow(icon: "exclamationmark.triangle", title: "Warnings", value: "\(count(.warning))")
                MetadataRow(icon: "sparkles", title: "Polish", value: "\(count(.polish))")
            }

            Section("My Reviews") {
                MetadataRow(icon: "checkmark.seal", title: "Reviewed by Me", value: "\(localReviewCount)")
                MetadataRow(icon: "circle.dashed", title: "Awaiting My Review", value: "\(max(totalContentItems - localReviewCount, 0))")
                if totalContentItems > 0 {
                    ProgressView(value: Double(localReviewCount), total: Double(totalContentItems))
                }
                Text("These review marks are local to this device. They do not modify the bundled clinical content.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            if !unreviewedProcedures.isEmpty {
                Section("Procedures To Review") {
                    ForEach(unreviewedProcedures) { procedure in
                        NavigationLink {
                            ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
                        } label: {
                            reviewQueueRow(title: procedure.title, subtitle: procedure.category.rawValue)
                        }
                    }
                }
            }

            if !unreviewedRescueCards.isEmpty {
                Section("Rescue Cards To Review") {
                    ForEach(unreviewedRescueCards) { card in
                        NavigationLink {
                            RescueCardDetailView(card: card)
                        } label: {
                            reviewQueueRow(title: card.title, subtitle: card.acuity.rawValue)
                        }
                    }
                }
            }

            if !unreviewedKits.isEmpty {
                Section("Kits To Review") {
                    ForEach(unreviewedKits) { kit in
                        NavigationLink {
                            KitDetailView(kit: kit)
                        } label: {
                            reviewQueueRow(title: kit.title, subtitle: kit.category.rawValue)
                        }
                    }
                }
            }

            if let loadError = repository.loadError {
                Section("Procedure Load Error") {
                    Text(loadError)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.red)
                }
            }

            if let rescueLoadError = repository.rescueLoadError {
                Section("Rescue Load Error") {
                    Text(rescueLoadError)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.red)
                }
            }

            if let loadWarning = repository.loadWarning {
                Section("Partial Procedure Load") {
                    Label(loadWarning, systemImage: "exclamationmark.triangle.fill")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.orange)
                }
            }

            if let rescueLoadWarning = repository.rescueLoadWarning {
                Section("Partial Rescue Load") {
                    Label(rescueLoadWarning, systemImage: "exclamationmark.triangle.fill")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.orange)
                }
            }

            if groupedIssues.isEmpty {
                Section {
                    Label("No content validation issues detected", systemImage: "checkmark.seal.fill")
                        .foregroundStyle(.green)
                }
            } else {
                ForEach(groupedIssues, id: \.0) { severity, issues in
                    Section(severity.rawValue) {
                        ForEach(issues) { issue in
                            linkedIssueRow(issue, severity: severity)
                        }
                    }
                }
            }
        }
        .navigationTitle("Content Health")
    }

    private var totalContentItems: Int {
        repository.procedures.count + repository.rescueCards.count + repository.kits.count
    }

    private var localReviewCount: Int {
        userData.localReviewCount(
            procedures: repository.procedures,
            rescueCards: repository.rescueCards,
            kits: repository.kits
        )
    }

    private var unreviewedProcedures: [Procedure] {
        repository.procedures.filter { userData.localReviewDate(for: $0) == nil }
    }

    private var unreviewedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { userData.localReviewDate(for: $0) == nil }
    }

    private var unreviewedKits: [Kit] {
        repository.kits.filter { userData.localReviewDate(for: $0) == nil }
    }

    private func count(_ severity: ContentValidationIssue.Severity) -> Int {
        repository.contentIssues.filter { $0.severity == severity }.count
    }

    private func reviewQueueRow(title: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title)
                .font(.subheadline.weight(.semibold))
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 3)
    }

    @ViewBuilder
    private func linkedIssueRow(_ issue: ContentValidationIssue, severity: ContentValidationIssue.Severity) -> some View {
        if let procedureID = issue.procedureID,
           let procedure = repository.procedure(withID: procedureID) {
            NavigationLink {
                ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
            } label: {
                issueRow(issue, severity: severity)
            }
        } else {
            issueRow(issue, severity: severity)
        }
    }

    private func issueRow(_ issue: ContentValidationIssue, severity: ContentValidationIssue.Severity) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(issue.displayMessage)
                .font(.subheadline.weight(severity == .blocker ? .semibold : .regular))
            if let procedureID = issue.procedureID {
                Text(procedureID)
                    .font(.caption.monospaced())
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 4)
    }
}

private extension ContentValidationIssue.Severity {
    static let displayOrder: [ContentValidationIssue.Severity] = [.blocker, .warning, .polish]
}
