import SwiftUI

struct ShiftModeProcedureContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            CriticalWarningCard(title: "Before You Start", items: procedure.sections.shiftMode)

            if !procedure.sections.troubleshooting.isEmpty {
                SectionCard(title: "If It Fails", systemImage: "wrench.and.screwdriver") {
                    BulletListView(items: procedure.sections.troubleshooting)
                }
            }

            if !procedure.sections.seniorPearls.isEmpty {
                SectionCard(title: "Technique Notes", systemImage: "quote.bubble") {
                    BulletListView(items: procedure.sections.seniorPearls)
                }
            }
        }
    }
}
