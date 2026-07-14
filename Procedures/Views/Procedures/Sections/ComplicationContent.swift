import SwiftUI

struct ComplicationContent: View {
    @EnvironmentObject private var repository: ProcedureRepository
    let procedure: Procedure

    private var relatedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { $0.relatedProcedureIDs.contains(procedure.id) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            CriticalWarningCard(title: "Complications to anticipate", items: procedure.sections.complications)

            if !relatedRescueCards.isEmpty {
                SectionCard(title: "Rescue Cards", systemImage: "lifepreserver.fill") {
                    VStack(alignment: .leading, spacing: 10) {
                        // Procedure detail can be opened from multiple tab stacks.
                        // Use an explicit destination so rescue links work the same
                        // regardless of which stack presented this screen.
                        ForEach(relatedRescueCards) { card in
                            NavigationLink {
                                RescueCardDetailView(card: card)
                            } label: {
                                HStack {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(card.title)
                                            .font(.subheadline.weight(.semibold))
                                        Text(card.trigger.first ?? "")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                            .lineLimit(1)
                                    }
                                    Spacer()
                                    Text(card.acuity.rawValue.uppercased())
                                        .font(.caption2.weight(.heavy))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .foregroundStyle(card.acuity.tintColor)
                                        .background(card.acuity.tintColor.opacity(0.14), in: Capsule())
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

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "Immediate Rescue Moves", systemImage: "lifepreserver") {
                    BulletListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.aftercare.isEmpty {
                SectionCard(title: "Aftercare", systemImage: "cross.case") {
                    BulletListView(items: procedure.sections.aftercare)
                }
            }
        }
    }
}
