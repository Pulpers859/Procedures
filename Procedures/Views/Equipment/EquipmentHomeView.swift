import SwiftUI

// MARK: - Kits Home

struct KitsHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""
    @State private var selectedCategory: Kit.KitCategory?

    private var displayedKits: [Kit] {
        if !searchText.isEmpty {
            return repository.searchKits(searchText)
        }
        if let category = selectedCategory {
            return repository.kits(in: category)
        }
        return repository.kits
    }

    private var populatedCategories: [Kit.KitCategory] {
        Kit.KitCategory.allCases.filter { !repository.kits(in: $0).isEmpty }
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
            .searchable(text: $searchText, prompt: "Search kit, catheter, airway, setup…")
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
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
                            systemImage: kitIcon(for: category),
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
            }
            .padding(.horizontal, 13)
            .padding(.vertical, 8)
            .background(isSelected ? tint : Color(.tertiarySystemFill), in: Capsule())
            .foregroundStyle(isSelected ? .white : .primary)
        }
        .buttonStyle(.plain)
        .animation(.easeInOut(duration: 0.15), value: isSelected)
    }

    private func checkedCount(for kit: Kit) -> Int {
        kit.allChecklistItems.filter { userData.isKitItemChecked($0, forKitID: kit.id) }.count
    }
}

// MARK: - Kit Row

struct KitRow: View {
    let kit: Kit
    let checkedCount: Int
    let totalCount: Int

    private var isComplete: Bool { totalCount > 0 && checkedCount == totalCount }
    private var isStarted: Bool { checkedCount > 0 && !isComplete }

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: kitIcon(for: kit.category))
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

            if isComplete {
                Image(systemName: "checkmark.seal.fill")
                    .foregroundStyle(.green)
                    .font(.title3)
                    .accessibilityLabel("Room ready")
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

    private var relatedProcedures: [Procedure] {
        kit.relatedProcedureIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var checkedCount: Int {
        kit.allChecklistItems.filter { userData.isKitItemChecked($0, forKitID: kit.id) }.count
    }

    private var totalChecklistItems: Int { kit.allChecklistItems.count }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header

                if !kit.patientSetup.isEmpty {
                    CriticalWarningCard(title: "Patient & Room Setup First", items: kit.patientSetup)
                }

                if !kit.inKit.isEmpty {
                    SectionCard(title: "In the Kit", systemImage: "shippingbox.fill") {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(kit.inKit, id: \.self) { item in
                                ChecklistRow(
                                    text: item,
                                    isChecked: userData.isKitItemChecked(item, forKitID: kit.id)
                                ) {
                                    userData.toggleKitItem(item, forKitID: kit.id)
                                }
                            }
                        }
                    }
                }

                if !kit.outsideKit.isEmpty {
                    SectionCard(title: "Pull Separately", systemImage: "arrow.up.right.square") {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(kit.outsideKit, id: \.self) { item in
                                ChecklistRow(
                                    text: item,
                                    isChecked: userData.isKitItemChecked(item, forKitID: kit.id)
                                ) {
                                    userData.toggleKitItem(item, forKitID: kit.id)
                                }
                            }
                        }
                    }
                }

                if !kit.commonlyForgotten.isEmpty {
                    commonlyForgottenCard
                }

                if !kit.sterileSetup.isEmpty {
                    SectionCard(title: "Sterile Field Setup", systemImage: "square.dashed") {
                        BulletListView(items: kit.sterileSetup)
                    }
                }

                if !kit.backupEquipment.isEmpty {
                    SectionCard(title: "Backup Equipment", systemImage: "lifepreserver") {
                        BulletListView(items: kit.backupEquipment)
                    }
                }

                if !relatedProcedures.isEmpty {
                    SectionCard(title: "Related Procedures", systemImage: "link") {
                        VStack(alignment: .leading, spacing: 10) {
                            ForEach(relatedProcedures) { procedure in
                                NavigationLink {
                                    ProcedureDetailView(procedure: procedure)
                                } label: {
                                    HStack {
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(procedure.title)
                                                .font(.subheadline.weight(.semibold))
                                            Text(procedure.category.rawValue)
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                        }
                                        Spacer()
                                        Image(systemName: "chevron.right")
                                            .font(.caption.weight(.semibold))
                                            .foregroundStyle(.secondary)
                                    }
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                }

                SectionCard(title: "Governance", systemImage: "checkmark.shield") {
                    VStack(spacing: 8) {
                        ReviewerStatusBadge(status: kit.reviewer)
                        MetadataRow(icon: "calendar", title: "Last reviewed", value: kit.lastReviewed)
                        MetadataRow(icon: "number", title: "Version", value: kit.version)
                    }
                }

                if !kit.references.isEmpty {
                    SectionCard(title: "References", systemImage: "books.vertical") {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(Array(kit.references.enumerated()), id: \.offset) { _, ref in
                                Text(ref)
                                    .font(.footnote)
                                    .foregroundStyle(.secondary)
                                    .textSelection(.enabled)
                            }
                            Divider().padding(.vertical, 4)
                            Text("Educational review for trained clinicians. Does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy.")
                                .font(.footnote.weight(.semibold))
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(kit.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            if checkedCount > 0 {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Reset") {
                        userData.resetKit(withID: kit.id)
                    }
                    .foregroundStyle(.secondary)
                }
            }
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 14) {
                Image(systemName: kitIcon(for: kit.category))
                    .font(.title2.weight(.semibold))
                    .foregroundStyle(kitTint(for: kit.category))
                    .frame(width: 50, height: 50)
                    .background(kitTint(for: kit.category).opacity(0.14), in: RoundedRectangle(cornerRadius: 14, style: .continuous))

                VStack(alignment: .leading, spacing: 4) {
                    Text(kit.category.rawValue.uppercased())
                        .font(.caption.weight(.heavy))
                        .foregroundStyle(kitTint(for: kit.category))
                    Text(kit.title)
                        .font(.title2.weight(.bold))
                }
                Spacer()
            }

            Text(kit.subtitle)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            if !kit.tags.isEmpty {
                FlowTagView(tags: Array(kit.tags.prefix(6)))
            }

            if totalChecklistItems > 0 {
                checklistProgressView
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
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
                            ? "Room ready"
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
                .tint(isComplete ? .green : kitTint(for: kit.category))
        }
        .padding(.top, 2)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(checkedCount == totalChecklistItems ? "Room ready, all items confirmed" : "\(checkedCount) of \(totalChecklistItems) items confirmed")
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
            BulletListView(items: kit.commonlyForgotten)
        }
        .padding()
        .background(.yellow.opacity(0.10), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(.yellow.opacity(0.35), lineWidth: 1))
    }
}

// MARK: - Shared helpers (used by both KitsHomeView and KitDetailView)

private func kitIcon(for category: Kit.KitCategory) -> String {
    switch category {
    case .airway: return "lungs.fill"
    case .vascularAccess: return "drop.fill"
    case .thoracic: return "stethoscope"
    case .cardiacResuscitation: return "heart.fill"
    case .neuro: return "brain.head.profile"
    case .regionalAnesthesia: return "syringe"
    case .woundSoftTissue: return "bandage.fill"
    case .sedationAnalgesia: return "moon.zzz.fill"
    case .ultrasoundGuided: return "waveform.path.ecg.rectangle"
    case .other: return "square.grid.2x2"
    }
}

private func kitTint(for category: Kit.KitCategory) -> Color {
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
