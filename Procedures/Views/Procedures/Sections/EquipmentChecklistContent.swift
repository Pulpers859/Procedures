import SwiftUI

struct EquipmentChecklistContent: View {
    @EnvironmentObject private var userData: UserDataStore
    let procedure: Procedure
    @State private var showingResetConfirmation = false

    var body: some View {
        SectionCard(title: "Room + Equipment Checklist", systemImage: "checklist") {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Tap items as they are physically in the room.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                    Spacer()
                    Button("Reset") {
                        showingResetConfirmation = true
                    }
                    .font(.footnote.weight(.semibold))
                    .confirmationDialog("Reset all equipment items?", isPresented: $showingResetConfirmation, titleVisibility: .visible) {
                        Button("Reset Checklist", role: .destructive) {
                            userData.resetEquipment(for: procedure)
                        }
                    }
                }

                ForEach(procedure.sections.equipment, id: \.self) { item in
                    ChecklistRow(
                        text: item,
                        isChecked: userData.isEquipmentChecked(item, for: procedure),
                        action: { userData.toggleEquipment(item, for: procedure) }
                    )
                }
            }
        }
    }
}
