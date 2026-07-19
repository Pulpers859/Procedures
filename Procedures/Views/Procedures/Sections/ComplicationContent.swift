import SwiftUI

struct ComplicationContent: View {
    @EnvironmentObject private var repository: ProcedureRepository
    let procedure: Procedure

    private var relatedRescueCards: [ComplicationRescueCard] {
        repository.rescueCards.filter { $0.relatedProcedureIDs.contains(procedure.id) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            if !relatedRescueCards.isEmpty {
                SectionCard(title: "Open Rescue", systemImage: "lifepreserver.fill") {
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
                                    AcuityBadge(acuity: card.acuity)
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

            CriticalWarningCard(title: "Watch For", items: procedure.sections.complications)

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "If It Fails", systemImage: "wrench.and.screwdriver") {
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
