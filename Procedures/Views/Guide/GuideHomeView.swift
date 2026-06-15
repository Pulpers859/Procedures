import SwiftUI

struct GuideHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""
    @State private var showingSettings = false

    private var filteredProcedures: [Procedure] {
        repository.search(searchText)
    }

    private var filteredRescueCards: [ComplicationRescueCard] {
        repository.searchRescueCards(searchText)
    }

    private var recentProcedures: [Procedure] {
        userData.recentIDs.compactMap { repository.procedure(withID: $0) }
    }

    private var favoriteProcedures: [Procedure] {
        repository.procedures.filter { userData.favoriteIDs.contains($0.id) }
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
                    heroSection
                    clinicalPathwaysSection

                    if !recentProcedures.isEmpty {
                        procedureSection(title: "Recently Viewed", procedures: recentProcedures)
                    }

                    if !crashProcedures.isEmpty {
                        procedureSection(title: "Crash / High-Risk", procedures: crashProcedures)
                    }

                    rescuePreviewSection

                    if !favoriteProcedures.isEmpty {
                        procedureSection(title: "Saved", procedures: favoriteProcedures)
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
            .searchable(text: $searchText, prompt: "Search problem or procedure…")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: ClinicalPathway.self) { pathway in
                PathwayProcedureListView(pathway: pathway)
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
        }
    }

    @ViewBuilder
    private var searchResults: some View {
        if !filteredRescueCards.isEmpty {
            Section("Rescue Cards") {
                ForEach(filteredRescueCards) { card in
                    NavigationLink(value: card) {
                        RescueCardRow(card: card)
                    }
                }
            }
        }

        Section("Procedure Results") {
            if filteredProcedures.isEmpty {
                Text("No procedures found. Try clinical shorthand like ETT, CVC, IJ, pigtail, pacer, LP, or finger block.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            } else {
                ForEach(filteredProcedures) { procedure in
                    NavigationLink(value: procedure) {
                        ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                    }
                }
            }
        }
    }

    private var heroSection: some View {
        Section {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("Bedside Command Center")
                            .font(.title3.weight(.bold))
                        Text("Start with the problem, the procedure, or the complication. Built to get you to the right card fast.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Spacer(minLength: 12)
                    Image(systemName: "cross.case.fill")
                        .font(.title2)
                        .foregroundStyle(.blue)
                        .padding(10)
                        .background(.blue.opacity(0.12), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                }

                HStack(spacing: 10) {
                    QuickStatPill(value: "\(repository.procedures.count)", label: "procedures")
                    QuickStatPill(value: "\(repository.rescueCards.count)", label: "rescue")
                    QuickStatPill(value: "Offline", label: "ready")
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var clinicalPathwaysSection: some View {
        Section("Clinical Pathways") {
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
                ForEach(ClinicalPathway.defaultPathways) { pathway in
                    NavigationLink(value: pathway) {
                        PathwayTile(pathway: pathway, count: pathwayCount(pathway))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.vertical, 4)
            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
        }
    }

    private var rescuePreviewSection: some View {
        Section("Immediate Rescue") {
            ForEach(repository.rescueCards.prefix(3)) { card in
                NavigationLink(value: card) {
                    RescueCardRow(card: card)
                }
            }

            NavigationLink {
                AllRescueCardsListView()
            } label: {
                Label("View all Rescue Cards", systemImage: "lifepreserver")
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

struct QuickStatPill: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.subheadline.weight(.bold))
                .lineLimit(1)
            Text(label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .lineLimit(1)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(.thinMaterial, in: Capsule())
    }
}

struct PathwayTile: View {
    let pathway: ClinicalPathway
    let count: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: pathway.systemImage)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(pathway.tint)
                    .frame(width: 34, height: 34)
                    .background(pathway.tint.opacity(0.14), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                Spacer()
                Text("\(count)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 3)
                    .background(Color(.tertiarySystemFill), in: Capsule())
            }

            VStack(alignment: .leading, spacing: 3) {
                Text(pathway.title)
                    .font(.headline)
                    .foregroundStyle(.primary)
                Text(pathway.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, minHeight: 120, alignment: .topLeading)
        .padding(14)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
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
        ClinicalPathway(id: "sedation", title: "Sedation", subtitle: "Procedural sedation and analgesia", systemImage: "moon.zzz.fill", tint: .teal, categories: [.sedationAnalgesia])
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
                    ForEach(procedures) { procedure in
                        NavigationLink(value: procedure) {
                            ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                        }
                    }
                }
            }
        }
        .navigationTitle(pathway.title)
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(for: Procedure.self) { procedure in
            ProcedureDetailView(procedure: procedure)
        }
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
                ForEach(repository.rescueCards) { card in
                    NavigationLink(value: card) {
                        RescueCardRow(card: card)
                    }
                }
            }
        }
        .navigationTitle("Rescue Cards")
        .navigationDestination(for: ComplicationRescueCard.self) { card in
            RescueCardDetailView(card: card)
        }
    }
}
