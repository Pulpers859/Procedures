import SwiftUI

// MARK: - Kits Home

struct KitsHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""
    @State private var selectedCategory: ProcedureCategory?

    private var displayedKits: [Kit] {
        if !searchText.isEmpty {
            return repository.searchKits(searchText)
        }
        if let category = selectedCategory {
            return repository.kits(in: category)
        }
        return repository.kits
    }

    private var populatedCategories: [ProcedureCategory] {
        ProcedureCategory.allCases.filter { !repository.kits(in: $0).isEmpty }
    }

    var body: some View {
        NavigationStack {
            Group {
                if let error = repository.kitLoadError {
                    EmptyStateView(
                        title: "Kits failed to load",
                        message: error,
                        systemImage: "exclamationmark.triangle"
                    )
                } else if repository.kits.isEmpty {
                    // A load that succeeds and yields nothing is not the same
                    // as a filter matching nothing. Without this the reader
                    // saw "No kits in this category" and blamed the category
                    // filter for a library that is not there at all.
                    EmptyStateView(
                        title: "No kits available",
                        message: "The kit library is empty. Reinstall the app or restore a recovery package.",
                        systemImage: "shippingbox"
                    )
                } else {
                    List {
                        if searchText.isEmpty && !repository.kits.isEmpty {
                            categoryFilterSection
                        }

                        Section(sectionHeader) {
                            if displayedKits.isEmpty {
                                Text(searchText.isEmpty ? "No kits in this category." : "No kits matched your search.")
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            } else {
                                ForEach(displayedKits) { kit in
                                    NavigationLink(value: kit) {
                                        KitRow(
                                            kit: kit,
                                            checkedCount: checkedCount(for: kit),
                                            totalCount: kit.allChecklistItems.count
                                        )
                                    }
                                }
                            }
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .navigationTitle("Kits")
            .settingsToolbar()
            .searchable(text: $searchText, prompt: "Search kit, catheter, airway, setup…")
            .scrollDismissesKeyboard(.immediately)
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
            }
            // KitDetailView opens ProcedureDetailView, which surfaces rescue-card
            // links, so this stack must resolve them at the root.
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
        }
    }

    private var sectionHeader: String {
        if !searchText.isEmpty { return "Search Results" }
        return selectedCategory?.rawValue ?? "All Kits"
    }

    private var categoryFilterSection: some View {
        Section {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    categoryChip(
                        label: "All",
                        systemImage: "checklist",
                        isSelected: selectedCategory == nil,
                        tint: .blue
                    ) {
                        selectedCategory = nil
                    }
                    ForEach(populatedCategories) { category in
                        categoryChip(
                            label: category.rawValue,
                            systemImage: category.systemImageName,
                            isSelected: selectedCategory == category,
                            tint: kitTint(for: category)
                        ) {
                            selectedCategory = selectedCategory == category ? nil : category
                        }
                    }
                }
                .padding(.vertical, 4)
            }
        }
        .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 4, trailing: 16))
        .listRowBackground(Color.clear)
        .listRowSeparator(.hidden)
    }

    private func categoryChip(
        label: String,
        systemImage: String,
        isSelected: Bool,
        tint: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 5) {
                Image(systemName: systemImage)
                    .font(.caption.weight(.semibold))
                Text(label)
                    .font(.subheadline.weight(.semibold))
                    .lineLimit(1)
                if isSelected {
                    Image(systemName: "checkmark")
                        .font(.caption.weight(.bold))
                }
            }
            .padding(.horizontal, 13)
            .frame(minHeight: AppLayout.controlMinHeight)
            .background(isSelected ? tint : Color(.tertiarySystemFill), in: Capsule())
            .foregroundStyle(isSelected ? .white : .primary)
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }

    private func checkedCount(for kit: Kit) -> Int {
        kit.allChecklistItems.filter { userData.isKitItemChecked($0, forKitID: kit.id) }.count
    }
}

// MARK: - Kit Row

struct KitRow: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let kit: Kit
    let checkedCount: Int
    let totalCount: Int

    private var isComplete: Bool { totalCount > 0 && checkedCount == totalCount }
    private var isStarted: Bool { checkedCount > 0 && !isComplete }

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: kit.category.systemImageName)
                .font(.title3.weight(.semibold))
                .foregroundStyle(kitTint(for: kit.category))
                .frame(width: 42, height: 42)
                .background(kitTint(for: kit.category).opacity(0.14), in: RoundedRectangle(cornerRadius: 12, style: .continuous))

            VStack(alignment: .leading, spacing: 3) {
                Text(kit.title)
                    .font(.headline)
                Text(kit.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer(minLength: 8)

            ReviewStateBadge(
                state: userData.reviewState(for: kit),
                policy: userData.badgePolicy(forKits: repository.kits)
            )

            if isComplete {
                Image(systemName: "checkmark.seal.fill")
                    .foregroundStyle(.green)
                    .font(.title3)
                    .accessibilityLabel("Saved checklist complete")
            } else if isStarted {
                Text("\(checkedCount)/\(totalCount)")
                    .font(.caption2.weight(.heavy))
                    .foregroundStyle(.blue)
                    .padding(.horizontal, 7)
                    .padding(.vertical, 4)
                    .background(.blue.opacity(0.12), in: Capsule())
                    .accessibilityLabel("\(checkedCount) of \(totalCount) items confirmed")
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Kit Detail

struct KitDetailView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let kit: Kit
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false
    @State private var showingResetConfirmation = false

    /// The merged kit, so a local edit shows here the moment it is saved.
    private var currentKit: Kit {
        repository.kits.first(where: { $0.id == kit.id }) ?? kit
    }

    private var relatedProcedures: [Procedure] {
        currentKit.relatedProcedureIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var checkedCount: Int {
        currentKit.allChecklistItems.filter { userData.isKitItemChecked($0, forKitID: currentKit.id) }.count
    }

    private var totalChecklistItems: Int { currentKit.allChecklistItems.count }

    private var requiresSessionDecision: Bool {
        userData.requiresKitSessionDecision(forKitID: currentKit.id)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
                header

                if requiresSessionDecision {
                    savedChecklistDecisionCard
                }

                if !currentKit.patientSetup.isEmpty {
                    CriticalWarningCard(title: "Patient & Room Setup First", items: currentKit.patientSetup)
                }

                if !requiresSessionDecision, !currentKit.inKit.isEmpty {
                    SectionCard(title: "In the Kit", systemImage: "shippingbox.fill") {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(currentKit.inKit, id: \.self) { item in
                                ChecklistRow(
                                    text: item,
                                    isChecked: userData.isKitItemChecked(item, forKitID: currentKit.id)
                                ) {
                                    userData.toggleKitItem(item, forKitID: currentKit.id)
                                }
                            }
                        }
                    }
                }

                if !requiresSessionDecision, !currentKit.outsideKit.isEmpty {
                    SectionCard(title: "Pull Separately", systemImage: "arrow.up.right.square") {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(currentKit.outsideKit, id: \.self) { item in
                                ChecklistRow(
                                    text: item,
                                    isChecked: userData.isKitItemChecked(item, forKitID: currentKit.id)
                                ) {
                                    userData.toggleKitItem(item, forKitID: currentKit.id)
                                }
                            }
                        }
                    }
                }

                if !currentKit.commonlyForgotten.isEmpty {
                    commonlyForgottenCard
                }

                if !currentKit.sterileSetup.isEmpty {
                    SectionCard(title: "Sterile Field Setup", systemImage: "square.dashed") {
                        BulletListView(items: currentKit.sterileSetup)
                    }
                }

                if !currentKit.backupEquipment.isEmpty {
                    SectionCard(title: "Backup Equipment", systemImage: "lifepreserver") {
                        BulletListView(items: currentKit.backupEquipment)
                    }
                }

                RelatedProceduresCard(procedures: relatedProcedures)

                if reviewModeEnabled {
                    SectionCard(title: "Review", systemImage: "checkmark.shield") {
                        LocalReviewPanel(
                            sourceStatus: currentKit.reviewer,
                            sourceOrigin: currentKit.source,
                            sourceLastReviewed: currentKit.lastReviewed,
                            sourceVersion: currentKit.version,
                            localReviewRecord: userData.localReviewRecord(for: currentKit),
                            materialState: userData.reviewContentState(for: currentKit),
                            markReviewed: { userData.markReviewed(currentKit) },
                            markNeedsEdits: { userData.setReviewDisposition(.needsEdits, for: currentKit) },
                            deferReview: { userData.setReviewDisposition(.deferred, for: currentKit) },
                            clearReview: { userData.clearReview(for: currentKit) }
                        )
                    }
                }

                if !currentKit.references.isEmpty {
                    DisclosureSectionCard(title: "References", systemImage: "books.vertical") {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(Array(currentKit.references.enumerated()), id: \.offset) { _, ref in
                                Text(ref)
                                    .font(.footnote)
                                    .foregroundStyle(.secondary)
                                    .textSelection(.enabled)
                            }
                            if showGovernanceCopy {
                                Divider().padding(.vertical, 4)
                                Text(AppConstants.shortDisclaimer)
                                    .font(.footnote.weight(.semibold))
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }
                }
            }
            .detailContentColumn()
            .padding(16)
        }
        .background(Color(.systemGroupedBackground))
        // Full title already renders in `header` below - see the matching
        // note on ProcedureDetailView.
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if reviewModeEnabled {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink {
                        CardEditorView(kind: .kit, id: kit.id, title: currentKit.title)
                    } label: {
                        Image(systemName: "square.and.pencil")
                    }
                    .accessibilityLabel("Edit this kit's content")
                }
            }
            if checkedCount > 0, !requiresSessionDecision {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Reset") {
                        showingResetConfirmation = true
                    }
                }
            }
        }
        .alert("Reset all kit checklist items?", isPresented: $showingResetConfirmation) {
            Button("Reset Checklist", role: .destructive) {
                userData.resetKit(withID: currentKit.id)
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This clears the current room-setup checks for this currentKit.")
        }
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 14) {
                Image(systemName: currentKit.category.systemImageName)
                    .font(.title2.weight(.semibold))
                    .foregroundStyle(kitTint(for: currentKit.category))
                    .frame(width: 50, height: 50)
                    .background(kitTint(for: currentKit.category).opacity(0.14), in: RoundedRectangle(cornerRadius: 14, style: .continuous))

                VStack(alignment: .leading, spacing: 4) {
                    Text(currentKit.category.rawValue.uppercased())
                        .font(.caption.weight(.heavy))
                        .foregroundStyle(kitTint(for: currentKit.category))
                    Text(currentKit.title)
                        .font(.title2.weight(.bold))
                }
                Spacer()
            }

            Text(currentKit.subtitle)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            // Kits were the one detail page that disclosed nothing about review
            // state, so a kit signed off on this device looked identical to one
            // nobody had ever opened.
            ReviewStateChip(
                state: userData.reviewState(for: currentKit),
                source: currentKit.source,
                alignment: .leading
            )

            if !currentKit.tags.isEmpty {
                FlowTagView(tags: Array(currentKit.tags.prefix(6)))
            }

            if totalChecklistItems > 0 {
                if requiresSessionDecision {
                    Label("Saved checklist needs confirmation", systemImage: "clock.arrow.circlepath")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(AppSemanticColor.warningText)
                } else {
                    checklistProgressView
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(AppLayout.cardPadding)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
    }

    private var checklistProgressView: some View {
        let progress = totalChecklistItems > 0 ? Double(checkedCount) / Double(totalChecklistItems) : 0.0
        let isComplete = checkedCount == totalChecklistItems
        return VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(
                    checkedCount == 0
                        ? "\(totalChecklistItems) items to confirm"
                        : isComplete
                            ? "Checklist complete"
                            : "\(checkedCount) of \(totalChecklistItems) confirmed"
                )
                .font(.caption.weight(.semibold))
                .foregroundStyle(isComplete ? .green : .secondary)
                Spacer()
                if checkedCount > 0 {
                    Image(systemName: isComplete ? "checkmark.seal.fill" : "circle.dashed")
                        .foregroundStyle(isComplete ? .green : .secondary)
                        .font(.caption)
                }
            }
            ProgressView(value: progress)
                .tint(isComplete ? .green : kitTint(for: currentKit.category))
        }
        .padding(.top, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(checkedCount == totalChecklistItems ? "Checklist complete, all items confirmed" : "\(checkedCount) of \(totalChecklistItems) items confirmed")
    }

    private var commonlyForgottenCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "lightbulb.fill")
                    .foregroundStyle(.yellow)
                Text("Commonly Forgotten")
                    .font(.headline)
                Spacer()
            }
            BulletListView(items: currentKit.commonlyForgotten)
        }
        .padding(AppLayout.cardPadding)
        .background(.yellow.opacity(0.10), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous).stroke(.yellow.opacity(0.35), lineWidth: 1))
    }

    private var savedChecklistDecisionCard: some View {
        SectionCard(title: "Saved Checklist", systemImage: "clock.arrow.circlepath") {
            VStack(alignment: .leading, spacing: 12) {
                Text("Saved checks may be from a prior patient or room. Choose before using this checklist.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)

                ViewThatFits(in: .horizontal) {
                    HStack(spacing: 10) { savedChecklistButtons }
                    VStack(spacing: 8) { savedChecklistButtons }
                }
            }
        }
    }

    @ViewBuilder
    private var savedChecklistButtons: some View {
        Button("Resume Saved") {
            userData.resumeKitSession(withID: currentKit.id)
        }
        .buttonStyle(.borderedProminent)
        .frame(minHeight: AppLayout.controlMinHeight)

        Button("Start New", role: .destructive) {
            userData.resetKit(withID: currentKit.id)
        }
        .buttonStyle(.bordered)
        .frame(minHeight: AppLayout.controlMinHeight)
    }
}

// MARK: - Shared helpers (used by both KitsHomeView and KitDetailView)

private func kitTint(for category: ProcedureCategory) -> Color {
    switch category {
    case .airway: return .cyan
    case .vascularAccess: return .blue
    case .thoracic: return .indigo
    case .cardiacResuscitation: return .red
    case .neuro: return .orange
    case .regionalAnesthesia: return .purple
    case .woundSoftTissue: return .brown
    case .sedationAnalgesia: return .teal
    case .ultrasoundGuided: return .green
    case .other: return Color(.secondaryLabel)
    }
}
