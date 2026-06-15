import SwiftUI

struct ContentHealthView: View {
    @EnvironmentObject private var repository: ProcedureRepository

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
                MetadataRow(icon: "exclamationmark.octagon", title: "Blockers", value: "\(count(.blocker))")
                MetadataRow(icon: "exclamationmark.triangle", title: "Warnings", value: "\(count(.warning))")
                MetadataRow(icon: "sparkles", title: "Polish", value: "\(count(.polish))")
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
                }
            }
        }
        .navigationTitle("Content Health")
    }

    private func count(_ severity: ContentValidationIssue.Severity) -> Int {
        repository.contentIssues.filter { $0.severity == severity }.count
    }
}

private extension ContentValidationIssue.Severity {
    static let displayOrder: [ContentValidationIssue.Severity] = [.blocker, .warning, .polish]
}
