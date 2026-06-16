import SwiftUI

struct ComplicationsHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @State private var searchText = ""

    private var rescueCards: [ComplicationRescueCard] {
        repository.searchRescueCards(searchText)
    }

    private var procedures: [Procedure] {
        repository.search(searchText).filter { !$0.sections.complications.isEmpty }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Rescue Cards")
                            .font(.title3.weight(.bold))
                        Text("Problem-first rescue cards for the moment a procedure starts going sideways. This is the action layer, not a passive complication list.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)
                }

                if !rescueCards.isEmpty {
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
                                        .padding()
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
        }
    }
}

struct RescueCardRow: View {
    let card: ComplicationRescueCard

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 3) {
                    Text(card.title)
                        .font(.headline)
                    Text(card.trigger.first ?? "")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer()
                Text(card.acuity.rawValue.uppercased())
                    .font(.caption2.weight(.heavy))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 5)
                    .foregroundStyle(card.acuity.tintColor)
                    .background(card.acuity.tintColor.opacity(0.14), in: Capsule())
            }

            FlowTagView(tags: card.tags.prefix(3).map { String($0) })
        }
        .padding(.vertical, 6)
    }
}

struct RescueCardDetailView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    let card: ComplicationRescueCard

    private var relatedProcedures: [Procedure] {
        card.relatedProcedureIDs.compactMap { repository.procedure(withID: $0) }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header

                CriticalWarningCard(title: "Trigger", items: card.trigger)
                CriticalWarningCard(title: "Immediate Moves", items: card.immediateMoves)

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

                SectionCard(title: "Governance", systemImage: "checkmark.shield") {
                    VStack(spacing: 8) {
                        ReviewerStatusBadge(status: card.reviewer)
                        MetadataRow(icon: "calendar", title: "Last reviewed", value: card.lastReviewed)
                        MetadataRow(icon: "number", title: "Version", value: card.version)
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
                            Divider().padding(.vertical, 4)
                            Text(AppConstants.shortDisclaimer)
                                .font(.footnote.weight(.semibold))
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
            .padding()
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle(card.title)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Rescue Card")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)
            Text(card.title)
                .font(.title2.weight(.bold))
            FlowTagView(tags: [card.acuity.rawValue] + card.tags.prefix(4).map { String($0) })
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}
