import SwiftUI

struct StepByStepContent: View {
    let procedure: Procedure

    var body: some View {
        VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
            if !procedure.sections.positioning.isEmpty {
                SectionCard(title: "Positioning", systemImage: "person.crop.rectangle") {
                    BulletListView(items: procedure.sections.positioning)
                }
            }

            if !procedure.sections.steps.isEmpty {
                SectionCard(title: "Steps", systemImage: "list.number") {
                    NumberedListView(items: procedure.sections.steps)
                }
            }

            if !procedure.sections.confirmation.isEmpty {
                SectionCard(title: "Confirmation", systemImage: "checkmark.seal") {
                    BulletListView(items: procedure.sections.confirmation)
                }
            }
        }
    }
}
