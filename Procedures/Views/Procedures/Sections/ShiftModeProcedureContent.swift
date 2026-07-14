import SwiftUI

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            CriticalWarningCard(title: "Need-to-know before you walk in", items: procedure.sections.shiftMode)

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "Failure Plan", systemImage: "wrench.and.screwdriver") {
                    BulletListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.seniorPearls.isEmpty {
                SectionCard(title: "Senior Pearls", systemImage: "quote.bubble") {
                    BulletListView(items: procedure.sections.seniorPearls)
                }
            }
        }
    }
}
