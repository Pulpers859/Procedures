import SwiftUI

enum ReviewCenterTab: String, CaseIterable, Identifiable {
    case queue = "Queue"
    case fix = "Fix"
    case track = "Track"

    var id: String { rawValue }
}

struct ReviewCenterView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var selectedTab: ReviewCenterTab = .queue
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    var body: some View {
        List {
            heroSection

            Section {
                Picker("Review Center Section", selection: $selectedTab) {
                    ForEach(ReviewCenterTab.allCases) { tab in
                        Text(tab.rawValue).tag(tab)
                    }
                }
                .pickerStyle(.segmented)
                .accessibilityLabel("Review Center section")
            }

            switch selectedTab {
            case .queue:
                queueContent
            case .fix:
                fixContent
            case .track:
                trackContent
            }
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Review Center")
        .onAppear {
            reviewModeEnabled = true
        }
    }

    private var heroSection: some View {
        Section {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: "checkmark.seal")
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(.blue)
                        .frame(width: 44, height: 44)
                        .background(.blue.opacity(0.12), in: RoundedRectangle(cornerRadius: 12, style: .continuous))

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Review Workspace")
                            .font(.title3.weight(.bold))
                        Text("Separate from bedside use. Review content, capture fixes, and track what you have personally signed off on this device.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }

                HStack(spacing: 8) {
                    ReviewMetricPill(value: "\(reviewedCount)", label: "reviewed", tint: .green)
                    ReviewMetricPill(value: "\(needsEditCount)", label: "needs edits", tint: .orange)
                    ReviewMetricPill(value: "\(issueCount(.warning))", label: "warnings", tint: .red)
                }
            }
            .padding(.vertical, 4)
        }
    }

    @ViewBuilder
    private var queueContent: some View {
        if unstartedProcedures.isEmpty && unstartedRescueCards.isEmpty && unstartedKits.isEmpty && needsEditItemsCount == 0 && deferredItemsCount == 0 {
            Section {
                Label("No local review work is queued.", systemImage: "checkmark.seal.fill")
                    .foregroundStyle(.green)
            }
        }

        if needsEditItemsCount > 0 {
            Section("Needs Edits") {
                reviewRows(disposition: .needsEdits)
            }
        }

        if !unstartedProcedures.isEmpty {
            Section("Procedures To Review") {
                ForEach(unstartedProcedures) { procedure in
                    NavigationLink {
                        ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
                    } label: {
                        ProcedureReviewRow(
                            title: procedure.title,
                            subtitle: procedure.category.rawValue,
                            detail: issueSummary(for: procedure),
                            record: userData.localReviewRecord(for: procedure)
                        )
                    }
                }
            }
        }

        if !unstartedRescueCards.isEmpty {
            Section("Rescue Cards To Review") {
                ForEach(unstartedRescueCards) { card in
                    NavigationLink {
                        RescueCardDetailView(card: card)
                    } label: {
                        ProcedureReviewRow(
                            title: card.title,
                            subtitle: card.acuity.rawValue,
                            detail: "Problem-first rescue card",
                            record: userData.localReviewRecord(for: card)
                        )
                    }
                }
            }
        }

        if !unstartedKits.isEmpty {
            Section("Kits To Review") {
                ForEach(unstartedKits) { kit in
                    NavigationLink {
                        KitDetailView(kit: kit)
                    } label: {
                        ProcedureReviewRow(
                            title: kit.title,
                            subtitle: kit.category.rawValue,
                            detail: "Room setup checklist",
                            record: userData.localReviewRecord(for: kit)
                        )
                    }
                }
            }
        }

        if deferredItemsCount > 0 {
            Section("Deferred") {
                reviewRows(disposition: .deferred)
            }
        }
    }

    @ViewBuilder
    private var fixContent: some View {
        if let loadError = repository.loadError {
            issueMessageSection(title: "Procedure Load Error", message: loadError, tint: .red)
        }
        if let rescueLoadError = repository.rescueLoadError {
            issueMessageSection(title: "Rescue Load Error", message: rescueLoadError, tint: .red)
        }
        if let kitLoadError = repository.kitLoadError {
            issueMessageSection(title: "Kit Load Error", message: kitLoadError, tint: .red)
        }
        if let loadWarning = repository.loadWarning {
            issueMessageSection(title: "Partial Procedure Load", message: loadWarning, tint: .orange)
        }
        if let rescueLoadWarning = repository.rescueLoadWarning {
            issueMessageSection(title: "Partial Rescue Load", message: rescueLoadWarning, tint: .orange)
        }
        if let kitLoadWarning = repository.kitLoadWarning {
            issueMessageSection(title: "Partial Kit Load", message: kitLoadWarning, tint: .orange)
        }

        if groupedIssues.isEmpty {
            Section {
                Label("No content validation issues detected.", systemImage: "checkmark.seal.fill")
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

    private var trackContent: some View {
        Group {
            Section("Progress") {
                MetadataRow(icon: "list.bullet.rectangle", title: "Procedures", value: "\(repository.procedures.count)")
                MetadataRow(icon: "lifepreserver", title: "Rescue Cards", value: "\(repository.rescueCards.count)")
                MetadataRow(icon: "shippingbox", title: "Kits", value: "\(repository.kits.count)")
                MetadataRow(icon: "checkmark.seal", title: "Reviewed", value: "\(reviewedCount)")
                MetadataRow(icon: "square.and.pencil", title: "Needs Edits", value: "\(needsEditCount)")
                MetadataRow(icon: "clock", title: "Deferred", value: "\(deferredCount)")
                if totalContentItems > 0 {
                    ProgressView(value: Double(reviewedCount), total: Double(totalContentItems))
                }
            }

            Section("Validation") {
                MetadataRow(icon: "exclamationmark.octagon", title: "Blockers", value: "\(issueCount(.blocker))")
                MetadataRow(icon: "exclamationmark.triangle", title: "Warnings", value: "\(issueCount(.warning))")
                MetadataRow(icon: "sparkles", title: "Polish", value: "\(issueCount(.polish))")
            }

            if !reviewedProcedures.isEmpty {
                Section("Reviewed Procedures") {
                    ForEach(reviewedProcedures) { procedure in
                        NavigationLink {
                            ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
                        } label: {
                            ProcedureReviewRow(
                                title: procedure.title,
                                subtitle: procedure.category.rawValue,
                                detail: issueSummary(for: procedure),
                                record: userData.localReviewRecord(for: procedure)
                            )
                        }
                    }
                }
            }

            if !reviewedRescueCards.isEmpty {
                Section("Reviewed Rescue Cards") {
                    ForEach(reviewedRescueCards) { card in
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

            if !reviewedKits.isEmpty {
                Section("Reviewed Kits") {
                    ForEach(reviewedKits) { kit in
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
    }

    private var groupedIssues: [(ContentValidationIssue.Severity, [ContentValidationIssue])] {
        ContentValidationIssue.Severity.displayOrder.map { severity in
            (severity, repository.contentIssues.filter { $0.severity == severity })
        }.filter { !$0.1.isEmpty }
    }

    private var totalContentItems: Int {
        repository.procedures.count + repository.rescueCards.count + repository.kits.count
    }

    private var reviewedCount: Int {
        userData.localReviewCount(
            procedures: repository.procedures,
            rescueCards: repository.rescueCards,
            kits: repository.kits
        )
    }

    private var needsEditCount: Int {
        userData.localReviewCount(disposition: .needsEdits, procedures: repository.procedures, rescueCards: repository.rescueCards, kits: repository.kits)
    }

    private var deferredCount: Int {
        userData.localReviewCount(disposition: .deferred, procedures: repository.procedures, rescueCards: repository.rescueCards, kits: repository.kits)
    }

    private var unstartedProcedures: [Procedure] {
        repository.procedures.filter { userData.localReviewRecord(for: $0) == nil }
    }

    private var unstartedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { userData.localReviewRecord(for: $0) == nil }
    }

    private var unstartedKits: [Kit] {
        repository.kits.filter { userData.localReviewRecord(for: $0) == nil }
    }

    private var reviewedProcedures: [Procedure] {
        repository.procedures.filter { userData.localReviewRecord(for: $0)?.disposition == .reviewed }
    }

    private var reviewedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { userData.localReviewRecord(for: $0)?.disposition == .reviewed }
    }

    private var reviewedKits: [Kit] {
        repository.kits.filter { userData.localReviewRecord(for: $0)?.disposition == .reviewed }
    }

    private var needsEditItemsCount: Int { needsEditCount }
    private var deferredItemsCount: Int { deferredCount }

    private func issueCount(_ severity: ContentValidationIssue.Severity) -> Int {
        repository.contentIssues.filter { $0.severity == severity }.count
    }

    private func issueSummary(for procedure: Procedure) -> String {
        let issues = repository.contentIssues.filter { $0.procedureID == procedure.id }
        if issues.isEmpty { return "No item-specific validator issues" }
        let warningCount = issues.filter { $0.severity == .warning }.count
        let polishCount = issues.filter { $0.severity == .polish }.count
        let blockerCount = issues.filter { $0.severity == .blocker }.count
        return [
            blockerCount > 0 ? "\(blockerCount) blocker" : nil,
            warningCount > 0 ? "\(warningCount) warning" : nil,
            polishCount > 0 ? "\(polishCount) polish" : nil
        ]
        .compactMap { $0 }
        .joined(separator: ", ")
    }

    @ViewBuilder
    private func reviewRows(disposition: LocalReviewDisposition) -> some View {
        ForEach(repository.procedures.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }) { procedure in
            NavigationLink {
                ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
            } label: {
                ProcedureReviewRow(
                    title: procedure.title,
                    subtitle: procedure.category.rawValue,
                    detail: issueSummary(for: procedure),
                    record: userData.localReviewRecord(for: procedure)
                )
            }
        }

        ForEach(repository.rescueCards.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }) { card in
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

        ForEach(repository.kits.filter { userData.localReviewRecord(for: $0)?.disposition == disposition }) { kit in
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

    private func issueMessageSection(title: String, message: String, tint: Color) -> some View {
        Section(title) {
            Label(message, systemImage: "exclamationmark.triangle.fill")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(tint)
        }
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

struct ProcedureReviewRow: View {
    let title: String
    let subtitle: String
    let detail: String
    let record: LocalReviewRecord?

    private var tint: Color {
        switch record?.disposition {
        case .reviewed: return .green
        case .needsEdits: return .orange
        case .deferred: return .secondary
        case nil: return .blue
        }
    }

    private var statusText: String {
        record?.disposition.rawValue ?? "Needs Review"
    }

    private var statusIcon: String {
        record?.disposition.systemImage ?? "circle"
    }

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: statusIcon)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(tint)
                .frame(width: 28, height: 28)
                .background(tint.opacity(0.12), in: RoundedRectangle(cornerRadius: 8, style: .continuous))

            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                if !detail.isEmpty {
                    Text(detail)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }

            Spacer(minLength: 8)

            Text(statusText)
                .font(.caption2.weight(.bold))
                .foregroundStyle(tint)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(tint.opacity(0.12), in: Capsule())
        }
        .padding(.vertical, 4)
    }
}

struct ReviewMetricPill: View {
    let value: String
    let label: String
    let tint: Color

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.subheadline.weight(.bold))
                .foregroundStyle(tint)
            Text(label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(tint.opacity(0.10), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}

private extension ContentValidationIssue.Severity {
    static let displayOrder: [ContentValidationIssue.Severity] = [.blocker, .warning, .polish]
}
