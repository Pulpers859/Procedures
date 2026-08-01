import SwiftUI
import UniformTypeIdentifiers

enum ReviewCenterTab: String, CaseIterable, Identifiable {
    case queue = "Queue"
    case fix = "Fix"
    case track = "Track"

    var id: String { rawValue }
}

struct ReviewCenterView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @EnvironmentObject private var editStore: ProcedureEditStore
    @EnvironmentObject private var recoveryStore: ClinicalRecoveryStore
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var exportURL: URL?
    @State private var reviewExportURL: URL?
    @State private var recoveryExportURL: URL?
    @State private var showingRecoveryImporter = false
    @State private var showingRecoveryExportWarning = false
    @State private var recoveryPreview: ClinicalRecoveryPreview?
    @State private var recoveryError: String?
    @State private var selectedTab: ReviewCenterTab = .queue
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    // Presented by pushing onto the Settings navigation stack. It must not
    // declare its own NavigationStack: a stack nested inside a stack shadows
    // the parent's navigation destinations and double-stacks the nav bar.
    var body: some View {
        List {
            heroSection

            if !reviewModeEnabled {
                reviewToolsDisabledSection
            }

            Section {
                // Segmented pickers neither reflow nor scroll, so at
                // accessibility sizes Queue/Fix/Track truncate to stubs.
                // Same branch as SavedView and the Procedures risk filter.
                if dynamicTypeSize.isAccessibilitySize {
                    sectionPicker.pickerStyle(.menu)
                } else {
                    sectionPicker.pickerStyle(.segmented)
                }
            }

            switch selectedTab {
            case .queue:
                queueContent
            case .fix:
                fixContent
            case .track:
                trackContent
            }

            myEditsSection
            myReviewsSection
            recoverySection
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Review Center")
        .onAppear { refreshExport() }
        .onChange(of: editStore.editsByProcedureID) { _, _ in refreshExport() }
        .onChange(of: userData.locallyReviewedContent) { _, _ in refreshExport() }
        .fileImporter(
            isPresented: $showingRecoveryImporter,
            allowedContentTypes: [.json],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                presentRecoveryPreview(from: url)
            case .failure(let error):
                recoveryError = "Could not open recovery package: \(error.localizedDescription)"
            }
        }
        .confirmationDialog(
            "Restore recovery package?",
            isPresented: Binding(get: { recoveryPreview != nil }, set: { if !$0 { recoveryPreview = nil } }),
            titleVisibility: .visible,
            presenting: recoveryPreview
        ) { preview in
            Button("Restore Safe Items") {
                restore(preview, replacingConflicts: false)
            }
            if !preview.conflicts.isEmpty || !preview.staleProcedureIDs.isEmpty {
                Button("Replace Conflicting Local Items", role: .destructive) {
                    restore(preview, replacingConflicts: true)
                }
            }
            Button("Cancel", role: .cancel) { recoveryPreview = nil }
        } message: { preview in
            Text(recoveryMessage(for: preview))
        }
        .alert("Recovery Backup", isPresented: Binding(get: { recoveryError != nil }, set: { if !$0 { recoveryError = nil } })) {
            Button("OK", role: .cancel) { recoveryError = nil }
        } message: {
            Text(recoveryError ?? "")
        }
    }

    /// Without review tools the "Review" panel is hidden on every content
    /// page, so each queue row would dead-end on a screen with no way to record
    /// a disposition. Say that here and offer the switch inline.
    private var sectionPicker: some View {
        Picker("Review Center Section", selection: $selectedTab) {
            ForEach(ReviewCenterTab.allCases) { tab in
                Text(tab.rawValue).tag(tab)
            }
        }
        .accessibilityLabel("Review Center section")
    }

    private var reviewToolsDisabledSection: some View {
        Section {
            VStack(alignment: .leading, spacing: 10) {
                Label("Review tools are turned off", systemImage: "exclamationmark.triangle.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(AppSemanticColor.warningText)
                Text("Opening an item below will show the content but no review controls. Turn review tools on to record Reviewed, Needs Edits, or Defer.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
                Button {
                    reviewModeEnabled = true
                } label: {
                    Label("Turn On Review Tools", systemImage: "checkmark.shield")
                        .frame(minHeight: AppLayout.controlMinHeight - 12)
                }
                .buttonStyle(.borderedProminent)
            }
            .padding(.vertical, 4)
        }
    }

    /// Corrections made in the app are only useful if they can get back to the
    /// repo. Without this the edits would live and die on one device.
    @ViewBuilder
    private var myEditsSection: some View {
        if editStore.editedProcedureCount > 0 {
            Section {
                scopeRow(
                    icon: "square.and.pencil",
                    title: "Procedures edited locally",
                    count: editStore.editedProcedureCount,
                    scope: .locallyEdited
                )
                if let exportURL {
                    ShareLink(item: exportURL) {
                        Label("Export Edits", systemImage: "square.and.arrow.up")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                }
            } header: {
                Text("Edits")
            } footer: {
                Text("Exports a JSON file of every local correction. Apply it to the repo with scripts/apply_local_edits.py to turn local edits into a reviewable diff.")
            }
        }
    }

    /// Your sign-offs are worth nothing to the content until they can leave the
    /// device. Without this a clinician could review all 73 items and every
    /// page would still read "AI draft - not clinically reviewed".
    @ViewBuilder
    private var myReviewsSection: some View {
        if !userData.locallyReviewedContent.isEmpty {
            Section {
                scopeRow(
                    icon: "checkmark.seal",
                    title: "Signed off",
                    count: reviewedCount,
                    scope: .disposition(.reviewed)
                )
                if let reviewExportURL {
                    ShareLink(item: reviewExportURL) {
                        Label("Export Reviews", systemImage: "square.and.arrow.up")
                            .frame(minHeight: AppLayout.controlMinHeight)
                    }
                }
            } header: {
                Text("Reviews")
            } footer: {
                Text("Apply it to the repo with scripts/apply_local_reviews.py to promote these items out of \"AI draft\". Sign-offs recorded against content that has since changed are refused rather than promoted.")
            }
        }
    }

    private func refreshExport() {
        exportURL = editStore.editedProcedureCount > 0 ? editStore.writeExportFile() : nil
        reviewExportURL = userData.locallyReviewedContent.isEmpty ? nil : userData.writeReviewExportFile()
    }

    @ViewBuilder
    private var recoverySection: some View {
        Section {
            if let date = recoveryStore.lastAutomaticBackupDate {
                Label("Automatic backup: \(date)", systemImage: "checkmark.icloud")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                Label("Automatic backup starts after your first local change.", systemImage: "externaldrive.badge.exclamationmark")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            if userData.hasUnreadableData || editStore.hasUnreadableEdits {
                Label("Some local data could not be read. Restore a recovery package before making more edits.", systemImage: "exclamationmark.triangle.fill")
                    .foregroundStyle(AppSemanticColor.warningText)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Button {
                showingRecoveryExportWarning = true
            } label: {
                Label("Prepare Recovery Package", systemImage: "archivebox")
                    .frame(minHeight: AppLayout.controlMinHeight)
            }
            .confirmationDialog(
                "Never enter patient identifiers",
                isPresented: $showingRecoveryExportWarning,
                titleVisibility: .visible
            ) {
                Button("Prepare Package") {
                    recoveryExportURL = recoveryStore.writePortableExport(userData: userData, editStore: editStore)
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("This package includes your local notes. Check them before sharing to Files, iCloud Drive, or your Mac.")
            }

            if let recoveryExportURL {
                ShareLink(item: recoveryExportURL) {
                    Label("Save Recovery Package to Files", systemImage: "square.and.arrow.up")
                        .frame(minHeight: AppLayout.controlMinHeight)
                }
            }

            Button {
                showingRecoveryImporter = true
            } label: {
                Label("Restore Recovery Package", systemImage: "arrow.clockwise.icloud")
                    .frame(minHeight: AppLayout.controlMinHeight)
            }

            ForEach(recoveryStore.snapshots) { snapshot in
                Button {
                    presentRecoveryPreview(from: snapshot.url)
                } label: {
                    Label("Review automatic backup from \(snapshot.date)", systemImage: "clock.arrow.circlepath")
                        .font(.subheadline)
                }
            }
        } header: {
            Text("Recovery Backup")
        } footer: {
            Text("Automatic copies protect this app on this device. Save a recovery package to Files, iCloud Drive, or your Mac to survive an app deletion, phone replacement, or reset. It includes local notes; use approved storage and never enter patient identifiers. Restoring never changes bundled GitHub content.")
        }
    }

    private func presentRecoveryPreview(from url: URL) {
        do {
            recoveryPreview = try recoveryStore.previewImport(
                from: url,
                editStore: editStore,
                procedures: repository.procedures
            )
        } catch {
            recoveryError = error.localizedDescription
        }
    }

    private func restore(_ preview: ClinicalRecoveryPreview, replacingConflicts: Bool) {
        recoveryStore.restore(
            preview,
            replacingConflicts: replacingConflicts,
            userData: userData,
            editStore: editStore,
            repository: repository
        )
        recoveryPreview = nil
    }

    private func recoveryMessage(for preview: ClinicalRecoveryPreview) -> String {
        var lines = ["This package contains \(preview.package.edits.count) local procedure correction(s)."]
        if !preview.conflicts.isEmpty { lines.append("\(preview.conflicts.count) correction(s) conflict with current local edits.") }
        if !preview.staleProcedureIDs.isEmpty { lines.append("\(preview.staleProcedureIDs.count) correction(s) need comparison with the current bundled clinical text.") }
        if !preview.unknownProcedureIDs.isEmpty { lines.append("\(preview.unknownProcedureIDs.count) correction(s) refer to procedures no longer in this build and will be skipped.") }
        lines.append("Restore Safe Items keeps current or stale corrections unchanged. Replace Conflicting Local Items is deliberate and replaces only matching local records.")
        return lines.joined(separator: " ")
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
                        Text("Separate from bedside use. Review content, capture fixes, and track what has been signed off on this device.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }

                // The pills are the first thing read on this screen and were the
                // one place a number could not be opened. Nested links inside a
                // row keep the pill's own appearance rather than taking on a
                // disclosure chevron.
                HStack(spacing: 8) {
                    metricPillLink(value: reviewedCount, label: "reviewed", tint: .green, scope: .disposition(.reviewed))
                    if changedSinceReviewCount > 0 {
                        metricPillLink(value: changedSinceReviewCount, label: "changed", tint: .orange, scope: .changedSinceReview)
                    }
                    metricPillLink(value: needsEditCount, label: "needs edits", tint: .orange, scope: .disposition(.needsEdits))
                    metricPillLink(value: issueCount(.warning), label: "warnings", tint: .red, scope: .issues(.warning))
                }
            }
            .padding(.vertical, 4)
        }
    }

    @ViewBuilder
    private var queueContent: some View {
        if unstartedProcedures.isEmpty && unstartedRescueCards.isEmpty && unstartedKits.isEmpty
            && needsEditItemsCount == 0 && deferredItemsCount == 0 {
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
                scopeRow(icon: "list.bullet.rectangle", title: "Procedures", count: repository.procedures.count, scope: .allProcedures)
                scopeRow(icon: "lifepreserver", title: "Rescue Cards", count: repository.rescueCards.count, scope: .allRescueCards)
                scopeRow(icon: "shippingbox", title: "Kits", count: repository.kits.count, scope: .allKits)
                // Counts local sign-offs only, and the list it opens filters the
                // same way, so the number and its destination cannot disagree.
                scopeRow(icon: "checkmark.seal", title: "Reviewed", count: reviewedCount, scope: .disposition(.reviewed))
                if changedSinceReviewCount > 0 {
                    scopeRow(icon: "arrow.triangle.2.circlepath", title: "Changed since review", count: changedSinceReviewCount, scope: .changedSinceReview)
                }
                scopeRow(icon: "square.and.pencil", title: "Needs Edits", count: needsEditCount, scope: .disposition(.needsEdits))
                scopeRow(icon: "clock", title: "Deferred", count: deferredCount, scope: .disposition(.deferred))
                if totalContentItems > 0 {
                    // Every review counts, permanently. A content update must
                    // never move a clinician's completed work backwards.
                    ProgressView(value: Double(reviewedCount), total: Double(totalContentItems))
                }
            }

            Section("Validation") {
                scopeRow(icon: "exclamationmark.octagon", title: "Blockers", count: issueCount(.blocker), scope: .issues(.blocker))
                scopeRow(icon: "exclamationmark.triangle", title: "Warnings", count: issueCount(.warning), scope: .issues(.warning))
                scopeRow(icon: "sparkles", title: "Polish", count: issueCount(.polish), scope: .issues(.polish))
            }

            if changedSinceReviewCount > 0 {
                Section {
                    changedSinceReviewRows
                } header: {
                    Text("Changed Since Review")
                } footer: {
                    Text("These stay reviewed and still count as done. Listed only because the clinically material text moved — open one to re-confirm.")
                }
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

    /// Reviewed items whose material content moved since sign-off. They stay
    /// reviewed and keep their progress credit; this only powers an optional
    /// "worth a second look" list.
    private var changedSinceReviewCount: Int {
        userData.changedSinceReviewCount(
            procedures: repository.procedures,
            rescueCards: repository.rescueCards,
            kits: repository.kits
        )
    }

    private var changedProcedures: [Procedure] {
        repository.procedures.filter {
            userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
        }
    }

    private var changedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter {
            userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
        }
    }

    private var changedKits: [Kit] {
        repository.kits.filter {
            userData.hasMaterialChange(userData.localReviewRecord(for: $0), fingerprint: $0.materialFingerprint)
        }
    }

    @ViewBuilder
    private var changedSinceReviewRows: some View {
        ForEach(changedProcedures) { procedure in
            NavigationLink {
                ProcedureDetailView(procedure: procedure, initialSection: .deepReview)
            } label: {
                ProcedureReviewRow(
                    title: procedure.title,
                    subtitle: procedure.category.rawValue,
                    detail: "Steps or doses changed since review",
                    record: userData.localReviewRecord(for: procedure)
                )
            }
        }

        ForEach(changedRescueCards) { card in
            NavigationLink {
                RescueCardDetailView(card: card)
            } label: {
                ProcedureReviewRow(
                    title: card.title,
                    subtitle: "Rescue Card",
                    detail: "Immediate moves changed since review",
                    record: userData.localReviewRecord(for: card)
                )
            }
        }

        ForEach(changedKits) { kit in
            NavigationLink {
                KitDetailView(kit: kit)
            } label: {
                ProcedureReviewRow(
                    title: kit.title,
                    subtitle: "Kit",
                    detail: "Contents or setup changed since review",
                    record: userData.localReviewRecord(for: kit)
                )
            }
        }
    }

    @ViewBuilder
    private func metricPillLink(value: Int, label: String, tint: Color, scope: ReviewScope) -> some View {
        if value > 0 {
            NavigationLink {
                ReviewScopeListView(scope: scope)
            } label: {
                ReviewMetricPill(value: "\(value)", label: label, tint: tint)
            }
            .buttonStyle(.plain)
            .accessibilityHint("Opens the \(label) list")
        } else {
            ReviewMetricPill(value: "\(value)", label: label, tint: tint)
        }
    }

    /// A count the reader can open.
    ///
    /// Tapping is offered only when there is something behind the number: a
    /// zero that pushes an empty screen teaches the reader that these rows are
    /// not worth tapping, which costs more than it gains. A zero row therefore
    /// renders as plain text, with no chevron promising a destination.
    @ViewBuilder
    private func scopeRow(icon: String, title: String, count: Int, scope: ReviewScope) -> some View {
        if count > 0 {
            NavigationLink {
                ReviewScopeListView(scope: scope)
            } label: {
                MetadataRow(icon: icon, title: title, value: "\(count)")
            }
        } else {
            MetadataRow(icon: icon, title: title, value: "\(count)")
        }
    }

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
