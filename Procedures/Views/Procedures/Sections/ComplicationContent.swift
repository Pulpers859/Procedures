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
                                // At accessibility sizes the growing badge used
                                // to squeeze the rescue title down to a few
                                // characters. Reflow instead, matching
                                // RescueCardRow.
                                ViewThatFits(in: .horizontal) {
                                    HStack {
                                        rescueLinkTitle(card)
                                        Spacer()
                                        AcuityBadge(acuity: card.acuity)
                                        Image(systemName: "chevron.right")
                                            .font(.caption.weight(.semibold))
                                            .foregroundStyle(.secondary)
                                    }
                                    VStack(alignment: .leading, spacing: 6) {
                                        rescueLinkTitle(card)
                                        AcuityBadge(acuity: card.acuity)
                                    }
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
                    TroubleshootingListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.aftercare.isEmpty {
                SectionCard(title: "Aftercare", systemImage: "cross.case") {
                    BulletListView(items: procedure.sections.aftercare)
                }
            }
        }
    }

    private func rescueLinkTitle(_ card: ComplicationRescueCard) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(card.title)
                .font(.subheadline.weight(.semibold))
                .fixedSize(horizontal: false, vertical: true)
            Text(card.trigger.first ?? "")
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(2)
        }
    }
}
