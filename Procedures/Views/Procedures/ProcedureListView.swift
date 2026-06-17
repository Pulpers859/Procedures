import SwiftUI

struct ProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @State private var searchText = ""

    private var filteredProcedures: [Procedure] {
        repository.search(searchText)
    }

    private var populatedCategories: [ProcedureCategory] {
        ProcedureCategory.allCases.filter { !repository.procedures(in: $0).isEmpty }
    }

    var body: some View {
        NavigationStack {
            Group {
                if let error = repository.loadError {
                    EmptyStateView(title: "Content failed to load", message: error, systemImage: "exclamationmark.triangle")
                } else if filteredProcedures.isEmpty {
                    EmptyStateView(title: "No procedures found", message: "Try a synonym, abbreviation, or category. Search understands terms like ETT, CVC, cordis, US IV, a-line, tap, abscess, suture, shoulder, fascia iliaca, pacer, LP, and thoracotomy.", systemImage: "magnifyingglass")
                } else {
                    List {
                        if searchText.isEmpty {
                            if let loadWarning = repository.loadWarning {
                                Section {
                                    Label(loadWarning, systemImage: "exclamationmark.triangle.fill")
                                        .font(.footnote.weight(.semibold))
                                        .foregroundStyle(.orange)
                                }
                            }
                            quickAccessSection
                        }

                        Section(searchText.isEmpty ? "All Procedures" : "Search Results") {
                            ForEach(filteredProcedures) { procedure in
                                NavigationLink(value: procedure) {
                                    ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                                }
                            }
                        }
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .navigationTitle("Procedures")
            .searchable(text: $searchText, prompt: "Search ETT, CVC, IJ, finger block…")
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
        }
    }

    private var quickAccessSection: some View {
        Section("Quick Access") {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(populatedCategories) { category in
                        NavigationLink {
                            CategoryProcedureListView(category: category)
                        } label: {
                            VStack(alignment: .leading, spacing: 8) {
                                Image(systemName: icon(for: category))
                                    .font(.title3)
                                    .foregroundStyle(.blue)
                                Text(category.rawValue)
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(.primary)
                                Text("\(repository.procedures(in: category).count) procedures")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            .padding()
                            .frame(width: 172, alignment: .leading)
                            .frame(minHeight: 110)
                            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.vertical, 4)
            }
        }
    }

    private func icon(for category: ProcedureCategory) -> String {
        switch category {
        case .airway: return "lungs.fill"
        case .vascularAccess: return "drop.fill"
        case .thoracic: return "stethoscope"
        case .cardiacResuscitation: return "heart.fill"
        case .neuro: return "brain.head.profile"
        case .regionalAnesthesia: return "syringe"
        case .woundSoftTissue: return "bandage.fill"
        case .ultrasoundGuided: return "waveform.path.ecg.rectangle"
        case .sedationAnalgesia: return "moon.zzz.fill"
        case .other: return "square.grid.2x2"
        }
    }
}

struct CategoryProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let category: ProcedureCategory

    private var procedures: [Procedure] {
        repository.procedures(in: category)
    }

    var body: some View {
        List(procedures) { procedure in
            NavigationLink(value: procedure) {
                ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
            }
        }
        .navigationTitle(category.rawValue)
        // Procedure destination is registered at the Procedures stack root; re-declaring
        // it here would duplicate the destination and misroute procedure taps.
    }
}
