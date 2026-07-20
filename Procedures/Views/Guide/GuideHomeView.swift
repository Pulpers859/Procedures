import SwiftUI

struct GuideHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var searchText = ""
    @State private var showingSettings = false
    @State private var selectedPathway: ClinicalPathway?

    private var filteredProcedures: [Procedure] {
        repository.search(searchText)
    }

    private var filteredRescueCards: [ComplicationRescueCard] {
        repository.searchRescueCards(searchText)
    }

    private var filteredKits: [Kit] {
        repository.searchKits(searchText)
    }

    private var recentProcedures: [Procedure] {
        userData.recentIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var crashProcedures: [Procedure] {
        repository.procedures
            .filter { $0.difficulty == .rareCrash || $0.difficulty == .advanced }
            .sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    var body: some View {
        NavigationStack {
            List {
                if searchText.isEmpty {
                    // Crash content stays above the fold: rescue always renders
                    // first, before recents, so the crash path never scrolls away.
                    rescuePreviewSection

                    if !recentProcedures.isEmpty {
                        procedureSection(title: "Recently Viewed", procedures: recentProcedures)
                    }

                    clinicalPathwaysSection

                    if !crashProcedures.isEmpty {
                        procedureSection(title: "Advanced / Rare-Crash", procedures: crashProcedures)
                    }
                } else {
                    searchResults
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("Guide")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingSettings = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                    .accessibilityLabel("Settings")
                }
            }
            .searchable(text: $searchText, prompt: "Search procedure, problem, or kit…")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
            }
            .navigationDestination(item: $selectedPathway) { pathway in
                PathwayProcedureListView(pathway: pathway)
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
        }
    }

    @ViewBuilder
    private var searchResults: some View {
        if filteredRescueCards.isEmpty && filteredProcedures.isEmpty && filteredKits.isEmpty {
            Section {
                EmptyStateView(
                    title: "No results",
                    message: "Try a procedure, clinical problem, abbreviation, or kit name.",
                    systemImage: "magnifyingglass"
                )
            }
        } else if !filteredRescueCards.isEmpty {
            Section("Rescue Cards") {
                ForEach(filteredRescueCards) { card in
                    NavigationLink(value: card) {
                        RescueCardRow(card: card)
                    }
                }
            }
        }

        if !filteredProcedures.isEmpty {
            Section("Procedures") {
                ForEach(filteredProcedures) { procedure in
                    NavigationLink(value: procedure) {
                        ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                    }
                }
            }
        }

        if !filteredKits.isEmpty {
            Section("Kits") {
                ForEach(filteredKits) { kit in
                    NavigationLink(value: kit) {
                        VStack(alignment: .leading, spacing: 3) {
                            Text(kit.title)
                                .font(.headline)
                            Text(kit.subtitle)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                    }
                }
            }
        }
    }

    private var clinicalPathwaysSection: some View {
        Section("Clinical Pathways") {
            LazyVGrid(columns: pathwayColumns, spacing: 8) {
                ForEach(ClinicalPathway.defaultPathways) { pathway in
                    Button {
                        selectedPathway = pathway
                    } label: {
                        PathwayTile(pathway: pathway, count: pathwayCount(pathway))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.vertical, 2)
            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            .listRowBackground(Color.clear)
        }
    }

    private var pathwayColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize {
            return [GridItem(.flexible())]
        }
        return [GridItem(.flexible(), spacing: 8), GridItem(.flexible(), spacing: 8)]
    }

    private var rescuePreviewSection: some View {
        Section("Immediate Rescue") {
            if let error = repository.rescueLoadError {
                Label(error, systemImage: "exclamationmark.triangle.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.red)
            } else if repository.rescueCards.isEmpty {
                Text("Rescue cards are unavailable.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                ForEach(repository.rescueCards.prefix(3)) { card in
                    NavigationLink(value: card) {
                        RescueCardRow(card: card)
                    }
                }

                NavigationLink {
                    AllRescueCardsListView()
                } label: {
                    Label("All rescue cards", systemImage: "lifepreserver")
                }
            }
        }
    }

    private func procedureSection(title: String, procedures: [Procedure]) -> some View {
        Section(title) {
            ForEach(procedures) { procedure in
                NavigationLink(value: procedure) {
                    ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                }
            }
        }
    }

    private func pathwayCount(_ pathway: ClinicalPathway) -> Int {
        repository.procedures.filter { pathway.categories.contains($0.category) }.count
    }
}

struct PathwayTile: View {
    let pathway: ClinicalPathway
    let count: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: pathway.systemImage)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(pathway.tint)
                    .frame(width: 32, height: 32)
                    .background(pathway.tint.opacity(0.14), in: RoundedRectangle(cornerRadius: 6, style: .continuous))
                Spacer()
                Text("\(count)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Color(.tertiarySystemFill), in: Capsule())
            }

            Text(pathway.title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, minHeight: 84, alignment: .topLeading)
        .padding(12)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
    }
}

struct ClinicalPathway: Identifiable, Hashable {
    let id: String
    let title: String
    let subtitle: String
    let systemImage: String
    let tint: Color
    let categories: [ProcedureCategory]

    static func == (lhs: ClinicalPathway, rhs: ClinicalPathway) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }

    static let defaultPathways: [ClinicalPathway] = [
        ClinicalPathway(id: "airway", title: "Airway", subtitle: "ETT, RSI, cric, failed airway", systemImage: "lungs.fill", tint: .cyan, categories: [.airway]),
        ClinicalPathway(id: "lines", title: "Lines", subtitle: "CVC, IJ, access, dialysis", systemImage: "drop.fill", tint: .blue, categories: [.vascularAccess, .ultrasoundGuided]),
        ClinicalPathway(id: "thoracic", title: "Thoracic", subtitle: "Chest tube, pigtail, needle", systemImage: "stethoscope", tint: .indigo, categories: [.thoracic]),
        ClinicalPathway(id: "resus", title: "Resus", subtitle: "Pacer, pericardiocentesis, crash", systemImage: "heart.fill", tint: .red, categories: [.cardiacResuscitation]),
        ClinicalPathway(id: "blocks", title: "Blocks", subtitle: "Digital and regional anesthesia", systemImage: "syringe", tint: .purple, categories: [.regionalAnesthesia]),
        ClinicalPathway(id: "neuro", title: "Neuro", subtitle: "LP, CSF, meningitis workup", systemImage: "brain.head.profile", tint: .orange, categories: [.neuro]),
        ClinicalPathway(id: "sedation", title: "Sedation", subtitle: "Procedural sedation and analgesia", systemImage: "moon.zzz.fill", tint: .teal, categories: [.sedationAnalgesia]),
        ClinicalPathway(id: "wound", title: "Wound & Soft Tissue", subtitle: "Abscess I&D, lacerations, wound care", systemImage: "bandage.fill", tint: .brown, categories: [.woundSoftTissue])
    ]
}

struct PathwayProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let pathway: ClinicalPathway

    private var procedures: [Procedure] {
        repository.procedures
            .filter { pathway.categories.contains($0.category) }
            .sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    var body: some View {
        List {
            Section {
                HStack(spacing: 12) {
                    Image(systemName: pathway.systemImage)
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(pathway.tint)
                        .frame(width: 44, height: 44)
                        .background(pathway.tint.opacity(0.14), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
                    VStack(alignment: .leading, spacing: 3) {
                        Text(pathway.title)
                            .font(.title3.weight(.bold))
                        Text(pathway.subtitle)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.vertical, 4)
            }

            Section("Procedures") {
                if procedures.isEmpty {
                    Text("No procedures in this pathway yet. Content is added before release rather than showing empty categories.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                } else {
                    // This list already lives inside a pushed destination. Keep the
                    // next drill-down explicit so taps cannot be misrouted back to
                    // the pathway screen by stack-level route resolution.
                    ForEach(procedures) { procedure in
                        NavigationLink {
                            ProcedureDetailView(procedure: procedure)
                        } label: {
                            ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                        }
                    }
                }
            }
        }
        .navigationTitle(pathway.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct AllRescueCardsListView: View {
    @EnvironmentObject private var repository: ProcedureRepository

    var body: some View {
        List {
            Section {
                Text("Problem-first cards for the moment a procedure starts going sideways.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Section("Immediate Rescue") {
                // Same rule as the pathway list above: this view is already one
                // level deep, so the next hop stays explicit.
                ForEach(repository.rescueCards) { card in
                    NavigationLink {
                        RescueCardDetailView(card: card)
                    } label: {
                        RescueCardRow(card: card)
                    }
                }
            }
        }
        .navigationTitle("Rescue Cards")
    }
}
