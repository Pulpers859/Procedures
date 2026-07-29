import SwiftUI

struct ProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @ObservedObject private var deepLinkRouter = DeepLinkRouter.shared
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var searchText = ""
    @State private var navigationPath = NavigationPath()
    @State private var highRiskOnly = false

    private var filteredProcedures: [Procedure] {
        let matches = repository.search(searchText)
        // The filter control is only shown while browsing. Letting it keep
        // applying during a search would silently drop matches with nothing
        // on screen explaining why.
        guard highRiskOnly, searchText.isEmpty else { return matches }
        return matches.filter { $0.difficulty == .advanced || $0.difficulty == .rareCrash }
    }

    private var highRiskCount: Int {
        repository.procedures.filter { $0.difficulty == .advanced || $0.difficulty == .rareCrash }.count
    }

    private var populatedCategories: [ProcedureCategory] {
        ProcedureCategory.allCases.filter { !repository.procedures(in: $0).isEmpty }
    }

    var body: some View {
        NavigationStack(path: $navigationPath) {
            Group {
                if let error = repository.loadError {
                    EmptyStateView(title: "Content failed to load", message: error, systemImage: "exclamationmark.triangle")
                } else if filteredProcedures.isEmpty {
                    EmptyStateView(title: "No procedures found", message: "Try a procedure name, abbreviation, or category.", systemImage: "magnifyingglass")
                } else {
                    List {
                        if searchText.isEmpty {
                            if let loadWarning = repository.loadWarning {
                                Section {
                                    Label(loadWarning, systemImage: "exclamationmark.triangle.fill")
                                        .font(.footnote.weight(.semibold))
                                        .foregroundStyle(AppSemanticColor.warningText)
                                }
                            }
                            unreviewedCorpusNotice
                            quickAccessSection
                            riskFilterSection
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
            .settingsToolbar()
            .searchable(text: $searchText, prompt: "Search ETT, CVC, IJ, finger block…")
            .scrollDismissesKeyboard(.immediately)
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .onChange(of: deepLinkRouter.destination) { _, destination in
                consumeDeepLink(destination)
            }
            .onAppear {
                consumeDeepLink(deepLinkRouter.destination)
            }
        }
    }

    /// Finishes a Spotlight route by pushing the requested procedure. An id
    /// that no longer resolves leaves the list showing.
    private func consumeDeepLink(_ destination: DeepLinkRouter.Destination?) {
        guard case .procedure(let id) = destination else { return }
        deepLinkRouter.destination = nil
        if let procedure = repository.procedure(withID: id) {
            navigationPath = NavigationPath([procedure])
        }
    }

    /// Said once, here, instead of as an orange badge on every row.
    ///
    /// While nothing in the library has been reviewed the per-row badge marks
    /// 100% of rows and distinguishes nothing, so it is suppressed and the state
    /// is disclosed in one place. Detail pages still carry their own banner, so
    /// no procedure can be opened without the reader being told.
    ///
    /// Counts local sign-offs, not just what shipped. Asking the bundled content
    /// alone meant this went on insisting nothing had been reviewed to a reader
    /// looking at procedures they had reviewed. Once even one is reviewed it
    /// disappears and the per-row badge takes over, marking the reviewed minority.
    @ViewBuilder
    private var unreviewedCorpusNotice: some View {
        if !repository.procedures.isEmpty,
           userData.effectiveReviewedCount(procedures: repository.procedures) == 0 {
            Section {
                Label(
                    "Nothing in this library has been reviewed yet. Verify against a trusted source before bedside use.",
                    systemImage: "exclamationmark.shield"
                )
                .font(.footnote.weight(.semibold))
                .foregroundStyle(AppSemanticColor.warningText)
                .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    /// The home screen used to render all 37 advanced and rare-crash
    /// procedures as its fourth section - two thirds of the library, unbounded,
    /// on the screen you land on. It is a filter of this tab, so it belongs
    /// here, where filtering is what the screen is for.
    private var riskFilterSection: some View {
        Section {
            Picker("Show", selection: $highRiskOnly) {
                Text("All (\(repository.procedures.count))").tag(false)
                Text("High-risk (\(highRiskCount))").tag(true)
            }
            .pickerStyle(.segmented)
            .accessibilityLabel("Filter procedures")
            .accessibilityHint("High-risk shows advanced and rare-crash procedures only")
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
                                Text("\(repository.procedures(in: category).count)")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(.secondary)
                            }
                            .padding(12)
                            // Fixed 144pt clipped category names like "Cardiac /
                            // Resuscitation" at accessibility sizes.
                            .frame(width: dynamicTypeSize.isAccessibilitySize ? nil : 144, alignment: .leading)
                            .frame(minHeight: 92, alignment: .leading)
                            .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
                            .overlay(RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
                        }
                        .buttonStyle(.plain)
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("\(category.rawValue), \(repository.procedures(in: category).count) procedures")
                        .accessibilityAddTraits(.isButton)
                    }
                }
                .padding(.vertical, 4)
            }
            .listRowBackground(Color.clear)
            .listRowInsets(EdgeInsets(top: 6, leading: 16, bottom: 6, trailing: 16))
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
            // Category drill-down is already pushed from the Procedures root, so
            // keep the procedure destination explicit here.
            NavigationLink {
                ProcedureDetailView(procedure: procedure)
            } label: {
                ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
            }
        }
        .navigationTitle(category.rawValue)
    }
}
