import SwiftUI

struct GuideHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""

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
        repository.procedures.filter { $0.difficulty == .rareCrash || $0.difficulty == .advanced }
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
                        procedureSection(title: "Favorites", procedures: favoriteProcedures)
                    }
                } else {
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
            }
            .navigationTitle("Guide")
            .searchable(text: $searchText, prompt: "Search problem or procedure…")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
        }
    }

    private var heroSection: some View {
        Section {
            VStack(alignment: .leading, spacing: 12) {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 5) {
                        Text("Bedside Command Center")
                            .font(.title2.weight(.bold))
                        Text("Start with the clinical problem, the procedure, or the complication. Built to get you to the right card fast.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Image(systemName: "cross.case.fill")
                        .font(.title2)
                        .foregroundStyle(.blue)
                        .padding(10)
                        .background(.blue.opacity(0.12), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                }

                HStack(spacing: 10) {
                    QuickStatPill(value: "\(repository.procedures.count)", label: "procedures")
                    QuickStatPill(value: "\(repository.rescueCards.count)", label: "rescue")
                    QuickStatPill(value: "offline", label: "ready")
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var clinicalPathwaysSection: some View {
        Section("Clinical Pathways") {
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(ClinicalPathway.defaultPathways) { pathway in
                    NavigationLink {
                        PathwayProcedureListView(pathway: pathway)
                    } label: {
                        VStack(alignment: .leading, spacing: 10) {
                            Image(systemName: pathway.systemImage)
                                .font(.title3.weight(.semibold))
                                .foregroundStyle(pathway.tint)
                            Text(pathway.title)
                                .font(.headline)
                                .foregroundStyle(.primary)
                            Text(pathway.subtitle)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                        .frame(maxWidth: .infinity, minHeight: 112, alignment: .topLeading)
                        .padding()
                        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.vertical, 4)
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

struct ClinicalPathway: Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let systemImage: String
    let tint: Color
    let categories: [ProcedureCategory]
    let searchTerms: [String]

    static let defaultPathways: [ClinicalPathway] = [
        ClinicalPathway(id: "airway", title: "Airway", subtitle: "ETT, RSI, cric, failed airway", systemImage: "lungs.fill", tint: .cyan, categories: [.airway], searchTerms: ["airway", "intubation", "cric", "rsi"]),
        ClinicalPathway(id: "lines", title: "Lines", subtitle: "CVC, IJ, access, dialysis", systemImage: "drop.fill", tint: .blue, categories: [.vascularAccess, .ultrasoundGuided], searchTerms: ["line", "cvc", "access", "catheter"]),
        ClinicalPathway(id: "thoracic", title: "Thoracic", subtitle: "Chest tube, pigtail, needle", systemImage: "stethoscope", tint: .indigo, categories: [.thoracic], searchTerms: ["thoracic", "chest", "pigtail", "needle"]),
        ClinicalPathway(id: "resus", title: "Resus", subtitle: "Pacer, pericardiocentesis, crash", systemImage: "heart.fill", tint: .red, categories: [.cardiacResuscitation], searchTerms: ["resuscitation", "pacer", "pericardial", "tamponade"]),
        ClinicalPathway(id: "blocks", title: "Blocks", subtitle: "Digital and regional anesthesia", systemImage: "syringe", tint: .purple, categories: [.regionalAnesthesia], searchTerms: ["block", "nerve", "anesthesia"]),
        ClinicalPathway(id: "neuro", title: "Neuro", subtitle: "LP, CSF, meningitis workup", systemImage: "brain.head.profile", tint: .orange, categories: [.neuro], searchTerms: ["lp", "lumbar", "csf", "neuro"])
    ]
}

struct PathwayProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let pathway: ClinicalPathway

    private var procedures: [Procedure] {
        let byCategory = repository.procedures.filter { pathway.categories.contains($0.category) }
        let bySearch = pathway.searchTerms.flatMap { repository.search($0) }
        return Array(Set(byCategory + bySearch)).sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Label(pathway.title, systemImage: pathway.systemImage)
                        .font(.title3.weight(.bold))
                        .foregroundStyle(pathway.tint)
                    Text(pathway.subtitle)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }

            Section("Procedures") {
                if procedures.isEmpty {
                    Text("No procedures in this pathway yet. Add content before release rather than showing empty categories.")
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
