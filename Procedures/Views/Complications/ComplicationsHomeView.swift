import SwiftUI

struct ComplicationsHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @ObservedObject private var deepLinkRouter = DeepLinkRouter.shared
    @State private var searchText = ""
    @State private var navigationPath: [ComplicationRescueCard] = []

    private var rescueCards: [ComplicationRescueCard] {
        repository.searchRescueCards(searchText)
    }

    // Procedure-specific complication reviews surface only when the clinician is
    // actively searching. The default Rescue screen stays focused on the
    // problem-first rescue cards rather than dumping every procedure.
    private var procedures: [Procedure] {
        guard !searchText.isEmpty else { return [] }
        return repository.search(searchText).filter { !$0.sections.complications.isEmpty }
    }

    var body: some View {
        NavigationStack(path: $navigationPath) {
            List {
                if let error = repository.rescueLoadError {
                    Section {
                        Label(error, systemImage: "exclamationmark.triangle.fill")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.red)
                    }
                } else if let warning = repository.rescueLoadWarning, searchText.isEmpty {
                    Section {
                        Label(warning, systemImage: "exclamationmark.triangle.fill")
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(.orange)
                    }
                }

                if rescueCards.isEmpty {
                    Section("Immediate Rescue") {
                        Text(searchText.isEmpty ? "Rescue cards are unavailable." : "No rescue cards match \"\(searchText)\".")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                } else {
                    Section("Immediate Rescue") {
                        ForEach(rescueCards) { card in
                            NavigationLink(value: card) {
                                RescueCardRow(card: card)
                            }
                        }
                    }
                }

                if !procedures.isEmpty {
                    Section("Procedure-Specific Reviews") {
                        ForEach(procedures) { procedure in
                            NavigationLink {
                                ScrollView {
                                    ComplicationContent(procedure: procedure)
                                        .detailContentColumn()
                                        .padding(16)
                                }
                                .background(Color(.systemGroupedBackground))
                                .navigationTitle(procedure.title)
                                .navigationBarTitleDisplayMode(.inline)
                            } label: {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(procedure.title)
                                        .font(.headline)
                                    Text(procedure.sections.complications.prefix(2).joined(separator: " • "))
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Rescue")
            .searchable(text: $searchText, prompt: "Search hypotension, apnea, capture…")
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

    /// Finishes a Spotlight route by pushing the requested card. An id that no
    /// longer resolves leaves the crash-sorted list showing, which is the
    /// safest place to land.
    private func consumeDeepLink(_ destination: DeepLinkRouter.Destination?) {
        guard case .rescueCard(let id) = destination else { return }
        deepLinkRouter.destination = nil
        if let card = repository.rescueCards.first(where: { $0.id == id }) {
            navigationPath = [card]
        }
    }
}

struct RescueCardRow: View {
    let card: ComplicationRescueCard

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            ViewThatFits(in: .horizontal) {
                HStack(alignment: .top) {
                    titleBlock
                    Spacer(minLength: 8)
                    badges
                }
                VStack(alignment: .leading, spacing: 6) {
                    titleBlock
                    badges
                }
            }

            FlowTagView(tags: card.tags.prefix(3).map { String($0) })
        }
        .padding(.vertical, 6)
    }

    private var titleBlock: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(card.title)
                .font(.headline)
            Text(card.trigger.first ?? "")
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(2)
        }
    }

    private var badges: some View {
        HStack(spacing: 8) {
            if !card.reviewer.isClinicallyReviewed {
                Image(systemName: "exclamationmark.shield")
                    .foregroundStyle(.orange)
                    .accessibilityLabel("Needs clinical review")
            }
            AcuityBadge(acuity: card.acuity)
        }
    }
}

struct RescueCardDetailView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let card: ComplicationRescueCard
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    private var relatedProcedures: [Procedure] {
        card.relatedProcedureIDs.compactMap { repository.procedure(withID: $0) }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
                CriticalWarningCard(title: "Act Now", items: card.immediateMoves, ordered: true)

                statusStrip

                SectionCard(title: "Recognize", systemImage: "waveform.path.ecg") {
                    BulletListView(items: card.trigger)
                }

                SectionCard(title: "Reassess", systemImage: "waveform.path.ecg") {
                    BulletListView(items: card.reassess)
                }

                SectionCard(title: "Avoid", systemImage: "hand.raised") {
                    BulletListView(items: card.avoid)
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

                if reviewModeEnabled {
                    SectionCard(title: "My Review", systemImage: "checkmark.shield") {
                        LocalReviewPanel(
                            sourceStatus: card.reviewer,
                            sourceOrigin: card.source,
                            sourceLastReviewed: card.lastReviewed,
                            sourceVersion: card.version,
                            localReviewRecord: userData.localReviewRecord(for: card),
                            markReviewed: { userData.markReviewed(card) },
                            markNeedsEdits: { userData.setReviewDisposition(.needsEdits, for: card) },
                            deferReview: { userData.setReviewDisposition(.deferred, for: card) },
                            clearReview: { userData.clearReview(for: card) }
                        )
                    }
                }

                if !card.references.isEmpty {
                    SectionCard(title: "References", systemImage: "books.vertical") {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(Array(card.references.enumerated()), id: \.offset) { _, reference in
                                Text(reference)
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
        .navigationTitle(card.title)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var showGovernanceCopy: Bool {
        reviewModeEnabled || !hideGovernanceCopy
    }

    private var statusStrip: some View {
        HStack(spacing: 10) {
            AcuityBadge(acuity: card.acuity)
            if !card.reviewer.isClinicallyReviewed {
                Label("Needs clinical review", systemImage: "exclamationmark.shield")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.orange)
            }
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, minHeight: AppLayout.controlMinHeight, alignment: .leading)
    }
}
